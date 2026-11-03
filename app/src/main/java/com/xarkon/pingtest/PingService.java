package com.xarkon.pingtest;

import android.app.*;
import android.content.*;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.net.wifi.WifiManager;
import android.net.*;
import android.os.*;
import android.content.pm.ServiceInfo;
import android.graphics.Color;
import android.util.Log;
import org.json.JSONObject;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.concurrent.*;
import java.util.regex.*;

public final class PingService extends Service {
    public static final String ACTION_START = "com.xarkon.pingtest.START";
    public static final String ACTION_STOP = "com.xarkon.pingtest.STOP";
    public static final String ACTION_UPDATE = "com.xarkon.pingtest.UPDATE";
    private static final String CHANNEL = "ping_monitor_v1";
    private static final int ONGOING = 117, GRAPH = 118;
    private static final Object LOCK = new Object();
    private static final Pattern TIME = Pattern.compile("time[=<]\\s*([0-9]+(?:[.,][0-9]+)?)", Pattern.CASE_INSENSITIVE);
    private static final Pattern TTL = Pattern.compile("ttl[= ]([0-9]+)", Pattern.CASE_INSENSITIVE);
    private static Snapshot live = new Snapshot();

    /** Immutable per-request journal row; payloadBytes is ICMP data size selected by the user. */
    public static final class ProbeEvent {
        public final int number, payloadBytes;
        public final double latencyMs;
        public final String message;
        public ProbeEvent(int number,double latencyMs,int payloadBytes,String message){
            this.number=number;this.latencyMs=latencyMs;this.payloadBytes=payloadBytes;
            this.message=message==null?"":message;
        }
    }
    public static final class Snapshot {
        public boolean active=false;
        public long id=0;
        public String host="ya.ru", label="Яндекс", ip="", error="", method="ICMP", route="", vpnInfo="", warning="";
        public int port=443;
        public long version=0;
        public int planned, sent, done, ok, lost, skipped, ttl=-1, limit=0, intervalMs=200, chartLimit=150;
        public double last=-1, min=Double.MAX_VALUE, max=0, total, jitterTotal, previous=-1;
        public int jitterCount;
        public long started;
        public final ArrayList<Float> chart = new ArrayList<>();
        public final ArrayList<String> log = new ArrayList<>();
        public final ArrayList<ProbeEvent> events = new ArrayList<>();
        public double avg(){return ok==0?-1:total/ok;}
        /** Loss is measured only among completed ICMP outcomes (reply or timeout).
         * Pending probes, skipped dispatches and fatal local execution errors are
         * not evidence of packet loss. */
        public double lossPct(){int classified=ok+lost;return classified==0?0:100.0*lost/classified;}
        public double jitter(){return jitterCount==0?0:jitterTotal/jitterCount;}
        public Snapshot copy(){
            Snapshot s=new Snapshot();
            s.active=active;s.id=id;s.host=host;s.label=label;s.ip=ip;s.error=error;s.method=method;s.route=route;s.vpnInfo=vpnInfo;s.warning=warning;s.port=port;s.version=version;s.planned=planned;
            s.sent=sent;s.done=done;s.ok=ok;s.lost=lost;s.skipped=skipped;s.ttl=ttl;
            s.limit=limit;s.intervalMs=intervalMs;s.chartLimit=chartLimit;s.last=last;s.min=min;s.max=max;
            s.total=total;s.previous=previous;s.jitterTotal=jitterTotal;s.jitterCount=jitterCount;
            s.started=started;s.chart.addAll(chart);s.log.addAll(log);s.events.addAll(events);return s;
        }
    }
    public static Snapshot snapshot() { synchronized(LOCK){return live.copy();} }

    private ScheduledExecutorService clock;
    private ThreadPoolExecutor workers;
    private PowerManager.WakeLock wakeLock;
    private WifiManager.WifiLock wifiLock;
    private NotificationManager notify;
    private String address="";
    private int bytes=64, ttl=64, timeout=4, chartLimit=150;
    private volatile VpnGuard.Route sessionRoute=VpnGuard.Route.UNKNOWN;
    private volatile long runId=0;
    private volatile boolean stopping=false;
    private long lastNotify=0, lastGraph=0;

    @Override public void onCreate() {
        super.onCreate();
        notify=(NotificationManager)getSystemService(NOTIFICATION_SERVICE);
        if(Build.VERSION.SDK_INT>=26)notify.createNotificationChannel(new NotificationChannel(CHANNEL,"PING TEST · проверка сети",NotificationManager.IMPORTANCE_LOW));
    }
    @Override public int onStartCommand(Intent intent,int flags,int startId) {
        String action=intent==null?"":intent.getAction();
        if(ACTION_STOP.equals(action)){finish("Остановлено пользователем");return START_NOT_STICKY;}
        if(!ACTION_START.equals(action))return START_NOT_STICKY;
        synchronized(LOCK){ if(live.active) return START_NOT_STICKY; }
        String host=intent.getStringExtra("host");
        if(host==null||host.trim().isEmpty())host="ya.ru";
        final String chosen=host;
        bytes=Math.max(0,Math.min(65000,intent.getIntExtra("size",64)));
        ttl=Math.max(1,Math.min(255,intent.getIntExtra("ttl",64)));
        timeout=Math.max(1,Math.min(10,intent.getIntExtra("timeout",4)));
        int interval=Math.max(100,Math.min(10000,intent.getIntExtra("interval",200)));
        int limit=Math.max(0,Math.min(50000,intent.getIntExtra("count",0)));
        chartLimit=Math.max(50,Math.min(500,intent.getIntExtra("graph_points",150)));
        VpnGuard.Route selectedRoute=VpnGuard.route(this);
        boolean vpn=selectedRoute==VpnGuard.Route.VPN;
        sessionRoute=selectedRoute;
        synchronized(LOCK){
            live=new Snapshot();live.active=true;live.id=System.currentTimeMillis();live.host=chosen;
            live.label=intent.getStringExtra("label")==null?chosen:intent.getStringExtra("label");
            live.started=System.currentTimeMillis();live.limit=limit;live.intervalMs=interval;live.chartLimit=chartLimit;
            live.method="ICMP";
            live.vpnInfo=vpn?"VPN включён":selectedRoute==VpnGuard.Route.DIRECT?
                "Прямой маршрут PING TEST":"Маршрут не определён";
            addLog("PING TEST • " + live.label + " | "+interval+" мс"+(vpn?" | VPN":""));
        }
        stopping=false; address="";
        final long expectedRun=live.id;runId=expectedRun;
        startForeground(ONGOING,makeNotification(snapshot()));
        acquireLocks();
        workers=new ThreadPoolExecutor(20,20,0L,TimeUnit.MILLISECONDS,new SynchronousQueue<Runnable>(), r->{Thread t=new Thread(r,"PingProbe");t.setDaemon(true);return t;});
        clock=Executors.newSingleThreadScheduledExecutor(r->{Thread t=new Thread(r,"PingClock");t.setDaemon(true);return t;});
        new Thread(()->{
            try{
                String route=vpn?"Через VPN":selectedRoute==VpnGuard.Route.DIRECT?
                    "Прямой маршрут (PING TEST вне VPN)":"Не определён";
                InetAddress[] resolved=InetAddress.getAllByName(chosen);
                if(resolved.length==0)throw new UnknownHostException(chosen);
                address=preferV4(resolved).getHostAddress();
                synchronized(LOCK){if(!live.active || runId!=expectedRun)return;
                    live.ip=address;live.route=route;live.method="ICMP";
                    addLog("Маршрут: "+route);live.version++;}
                signalUpdate();
                ScheduledExecutorService c=clock;
                if(c!=null&&!c.isShutdown()&&!stopping)c.scheduleAtFixedRate(this::tick,0,interval,TimeUnit.MILLISECONDS);
                refreshNotification(true);
            }catch(Exception e){
                synchronized(LOCK){if(runId!=expectedRun)return;
                    live.error="Подключение: "+safeMessage(e);addLog("ОШИБКА: "+safeMessage(e));live.version++;}
                finish("Проверка недоступна: "+safeMessage(e));
            }
        },"PingDNS").start();
        return START_NOT_STICKY;
    }
    private InetAddress preferV4(InetAddress[] list){
        for(InetAddress a:list)if(a instanceof Inet4Address)return a;
        return list[0];
    }
    private String safeMessage(Throwable t){
        String msg=t.getMessage();return msg==null?t.getClass().getSimpleName():msg;
    }
    private void tick(){
        if(stopping)return;
        VpnGuard.Route currentRoute=VpnGuard.route(this);
        if(currentRoute!=VpnGuard.Route.UNKNOWN&&sessionRoute!=VpnGuard.Route.UNKNOWN
            &&currentRoute!=sessionRoute){
            finish("Маршрут VPN изменился. Начните новую проверку.");return;
        }
        final int seq;final long capturedRun=runId;
        synchronized(LOCK){
            if(!live.active || (live.limit>0 && live.planned>=live.limit))return;
            seq=++live.planned;live.sent++;live.version++;
        }
        try{
            workers.execute(()->probe(seq,capturedRun));
            signalUpdate();
        }catch(RejectedExecutionException ex){
            synchronized(LOCK){if(capturedRun!=runId || !live.active)return;
                live.sent--;live.skipped++;addProbeEvent(seq,-1,bytes,"Пропуск: очередь заполнена");live.version++;}
            signalUpdate();checkFinished();
        }
    }
    /**
     * Android toybox ping prints "N bytes from ADDRESS: ... time=...".
     * Require a full reply line from the selected address, not arbitrary
     * stderr/stdout text that happens to contain a time token.
     */
    /**
     * Parse latency and TTL from the SAME reply line for the selected IP.
     * Summary lines and unrelated diagnostic text must never supply an RTT.
     */
    private static double[] parseIcmpReply(String output,String expectedAddress){
        if(expectedAddress==null||expectedAddress.isEmpty())return null;
        String quoted=Pattern.quote(expectedAddress);
        Pattern reply=Pattern.compile("(?m)^\\d+ bytes from "+quoted+
            "(?:%[\\w.:-]+)?(?::|\\s)[^\\r\\n]*$",Pattern.CASE_INSENSITIVE);
        Matcher lines=reply.matcher(output);
        while(lines.find()){
            String line=lines.group();
            Matcher time=TIME.matcher(line);
            if(!time.find())continue;
            try{
                double latency=Double.parseDouble(time.group(1).replace(',','.'));
                if(!Double.isFinite(latency)||latency<0)continue;
                Matcher ttl=TTL.matcher(line);
                int replyTtl=-1;
                if(ttl.find())try{replyTtl=Integer.parseInt(ttl.group(1));}
                    catch(NumberFormatException ignored){}
                return new double[]{latency,replyTtl};
            }catch(NumberFormatException ignored){}
        }
        return null;
    }

    private void probe(int seq,long capturedRun){
        double rtt=-1;int replyTtl=-1;String error="";
        java.lang.Process process=null;
        try{
            String binary=new File("/system/bin/ping").exists()?"/system/bin/ping":"ping";
            String[] cmd={binary,"-n","-c","1","-W",Integer.toString(timeout),"-s",Integer.toString(bytes),"-t",Integer.toString(ttl),address};
            process=new ProcessBuilder(cmd).redirectErrorStream(true).start();
            boolean finished=process.waitFor(timeout+3,TimeUnit.SECONDS);
            if(!finished){process.destroyForcibly();error="Истекло время ожидания";}
            else{
                ByteArrayOutputStream buffer=new ByteArrayOutputStream();
                byte[] temp=new byte[2048];int read;
                InputStream input=process.getInputStream();
                while(buffer.size()<8192&&(read=input.read(temp,0,Math.min(temp.length,8192-buffer.size())))!=-1)buffer.write(temp,0,read);
                String output=new String(buffer.toByteArray(),StandardCharsets.UTF_8);
                // A time= token in diagnostic text is not proof of an ICMP reply.
                // Only accept an actual successful ping process and a reply line
                // naming the probed address. Prevents false-positive latency.
                double[] parsed=process.exitValue()==0?parseIcmpReply(output,address):null;
                if(parsed!=null){rtt=parsed[0];replyTtl=(int)parsed[1];}
                if(rtt<0){
                    if(output.contains("Operation not permitted")||output.contains("Permission denied"))error="Пинг запрещён системой";
                    else if(output.contains("unknown option")||output.contains("invalid option")||output.contains("usage:"))error="Параметры ping не поддерживаются прошивкой";
                    else if(output.contains("Network is unreachable"))error="Сеть недоступна";
                    else error="Нет ответа";
                }
            }
        }catch(InterruptedException e){Thread.currentThread().interrupt();error="Прервано";}
        catch(Exception e){error="Ошибка запуска ping: "+e.getMessage();}
        finally{if(process!=null){try{process.destroy();}catch(Exception ignored){}}}
        boolean fatal=error.startsWith("Пинг запрещён")||error.startsWith("Параметры ping")||error.startsWith("Ошибка запуска ping");
        synchronized(LOCK){
            if(!live.active||runId!=capturedRun)return;
            live.done++;
            if(rtt>=0){
                live.ok++;live.last=rtt;live.total+=rtt;live.min=Math.min(live.min,rtt);live.max=Math.max(live.max,rtt);
                if(live.previous>=0){live.jitterTotal+=Math.abs(rtt-live.previous);live.jitterCount++;}
                live.previous=rtt;if(replyTtl>=0)live.ttl=replyTtl;
                addProbeEvent(seq,rtt,bytes,"");
            }else if(fatal){live.error=error;addProbeEvent(seq,-1,bytes,error);}
            else{live.lost++;addProbeEvent(seq,-1,bytes,error);}
            if(!fatal){live.chart.add(rtt<0?-1f:(float)rtt);while(live.chart.size()>live.chartLimit)live.chart.remove(0);}
            live.version++;
        }
        signalUpdate();
        if(fatal){if(capturedRun==runId)finish(error);return;}
        if(capturedRun!=runId)return;
        refreshNotification(false);
        if(seq%10==0)persist(false);
        checkFinished();
    }
    private static void addLog(String msg){
        if(live.log.size()>=600)live.log.remove(0);
        live.log.add(msg);
        addEvent(new ProbeEvent(0,-1,0,msg));
    }
    private static void addProbeEvent(int seq,double rtt,int payloadBytes,String error){
        String line=String.format(Locale.US,"#%d  |  %s  |  %d",seq,
            rtt>=0?String.format(Locale.US,"%.1f мс",rtt):error,payloadBytes);
        if(live.log.size()>=600)live.log.remove(0);
        live.log.add(line);
        addEvent(new ProbeEvent(seq,rtt,payloadBytes,error));
    }
    private static void addEvent(ProbeEvent event){
        if(live.events.size()>=600)live.events.remove(0);
        live.events.add(event);
    }
    private void checkFinished(){
        synchronized(LOCK){if(!live.active || live.limit<=0 || live.planned<live.limit || live.done + live.skipped < live.planned)return;}
        finish("Завершено");
    }
    private void acquireLocks(){
        try{PowerManager pm=(PowerManager)getSystemService(POWER_SERVICE);wakeLock=pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"pingtest:monitor");wakeLock.acquire();}catch(Exception e){Log.w("PING TEST","WakeLock",e);}
        try{WifiManager wm=(WifiManager)getApplicationContext().getSystemService(WIFI_SERVICE);if(wm!=null){wifiLock=wm.createWifiLock(WifiManager.WIFI_MODE_FULL_HIGH_PERF,"pingtest:wifi");wifiLock.acquire();}}catch(Exception e){Log.w("PING TEST","WifiLock",e);}
    }
    private void releaseLocks(){
        try{if(wakeLock!=null&&wakeLock.isHeld())wakeLock.release();}catch(Exception ignored){}
        try{if(wifiLock!=null&&wifiLock.isHeld())wifiLock.release();}catch(Exception ignored){}
    }
    private Notification makeNotification(Snapshot s){
        Intent open=new Intent(this,MainActivity.class);open.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP|Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent p=PendingIntent.getActivity(this,0,open,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        Intent stop=new Intent(this,PingService.class).setAction(ACTION_STOP);
        PendingIntent stopP=PendingIntent.getService(this,1,stop,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        String content=s.sent==0?"Подключение к узлу…":String.format(Locale.US,"%s · %d/%d · %.0f мс · %s %.1f%%",(s.vpnInfo.contains("включён")?"С VPN":"Без VPN"),s.ok,s.sent,s.avg(),"потери",s.lossPct());
        if(!s.error.isEmpty())content=s.error;
        else if(!s.warning.isEmpty())content=s.warning;
        if(s.ok==0&&s.lost>0&&s.error.isEmpty())content="0 / "+(s.ok+s.lost)+" • ответов нет";
        if(!AppPrefs.bool(this,"notifications",true)) content="Активная проверка сети · нажмите для просмотра";
        Notification.Builder b=Build.VERSION.SDK_INT>=26?new Notification.Builder(this,CHANNEL):new Notification.Builder(this);
        b.setSmallIcon(android.R.drawable.stat_notify_sync).setContentTitle("PING TEST • "+s.label)
                .setContentText(content).setContentIntent(p).setOngoing(true)
                .setOnlyAlertOnce(true).setCategory(Notification.CATEGORY_SERVICE)
                .setColor(AppPrefs.accent(this)).addAction(new Notification.Action.Builder(
                        android.R.drawable.ic_media_pause,"Остановить",stopP).build());
        if(AppPrefs.bool(this,"notifications",true) && AppPrefs.bool(this,"notify_progress",true)) {
            if(s.limit>0)b.setProgress(s.limit,Math.min(s.limit,s.done+s.skipped),false);
            else b.setProgress(0,0,true);
        }
        if(AppPrefs.bool(this,"notifications",true)&&AppPrefs.bool(this,"notify_details",true)){
            StringBuilder sb=new StringBuilder(content);
            if(!s.log.isEmpty())sb.append("\n").append(s.log.get(s.log.size()-1));
            if(s.ok>0)sb.append(String.format(Locale.US,"\nmin / avg / max: %.1f / %.1f / %.1f мс",s.min,s.avg(),s.max));
            b.setStyle(new Notification.BigTextStyle().bigText(sb.toString()));
        }
        return b.build();
    }
    private void refreshNotification(boolean force){
        Snapshot s=snapshot();long now=SystemClock.elapsedRealtime();
        if(!s.active || !AppPrefs.bool(this,"notifications",true)){
            // A foreground service must still keep its mandatory ongoing notification.
            if(force||now-lastNotify>=3000){notify.notify(ONGOING,makeNotification(s));lastNotify=now;}
            notify.cancel(GRAPH);return;
        }
        if(force||now-lastNotify>=1100){notify.notify(ONGOING,makeNotification(s));lastNotify=now;}
        if(AppPrefs.bool(this,"notify_chart",false)&&s.chart.size()>1&&now-lastGraph>5000){
            try{
                float[] data=new float[s.chart.size()];for(int i=0;i<data.length;i++)data[i]=s.chart.get(i);
                Bitmap bmp=Bitmap.createBitmap(700,260,Bitmap.Config.ARGB_8888);
                GraphView.render(new Canvas(bmp),700,260,data,AppPrefs.accent(this),0xFF121B27);
                Notification.Builder b=Build.VERSION.SDK_INT>=26?new Notification.Builder(this,CHANNEL):new Notification.Builder(this);
                b.setSmallIcon(android.R.drawable.stat_notify_sync).setContentTitle("PING TEST • график задержки")
                 .setContentText(s.label+" · "+s.ok+" ответов")
                 .setColor(AppPrefs.accent(this)).setOngoing(true).setOnlyAlertOnce(true)
                 .setStyle(new Notification.BigPictureStyle().bigPicture(bmp));
                notify.notify(GRAPH,b.build());lastGraph=now;
            }catch(Exception e){Log.w("PING TEST","Chart notification",e);}
        }else if(!AppPrefs.bool(this,"notify_chart",false))notify.cancel(GRAPH);
    }
    private void persist(boolean finished){
        if(!AppPrefs.bool(this,"history",true))return;
        Snapshot s=snapshot();if(s.id==0)return;
        try{
            JSONObject j=new JSONObject();
            j.put("id",s.id);j.put("host",s.host);j.put("ip",s.ip);j.put("time",s.started);
            j.put("method",s.method);j.put("label",s.label);j.put("vpnInfo",s.vpnInfo);j.put("route",s.route);j.put("port",s.port);j.put("warning",s.warning);j.put("error",s.error);
            j.put("sent",s.sent);j.put("done",s.done);j.put("ok",s.ok);j.put("lost",s.lost);j.put("skipped",s.skipped);
            j.put("min",s.ok>0?s.min:-1);j.put("avg",s.avg());j.put("max",s.ok>0?s.max:-1);
            j.put("jitter",s.jitter());j.put("ttl",s.ttl);j.put("finished",finished);
            j.put("log",String.join("\n",s.log));
            HistoryStore.upsert(this,j);
        }catch(Exception e){Log.e("PING TEST","History save",e);}
    }
    private synchronized void finish(String reason){
        if(stopping)return;stopping=true;
        synchronized(LOCK){if(!live.active){stopSelf();return;}live.active=false;addLog("● "+reason);live.version++;if(!reason.equals("Завершено")&&!reason.equals("Остановлено пользователем"))live.error=reason;}
        if(clock!=null)clock.shutdownNow();
        if(workers!=null)workers.shutdownNow();
        signalUpdate();persist(true);releaseLocks();notify.cancel(GRAPH);
        if(Build.VERSION.SDK_INT>=24)stopForeground(STOP_FOREGROUND_REMOVE);else stopForeground(true);
        stopSelf();
    }
    @Override public void onDestroy(){
        if(!stopping){synchronized(LOCK){live.active=false;addLog("● Служба остановлена системой");}persist(true);}
        if(clock!=null)clock.shutdownNow();if(workers!=null)workers.shutdownNow();
        releaseLocks();notify.cancel(GRAPH);super.onDestroy();
    }
    private void signalUpdate(){
        try{sendBroadcast(new Intent(ACTION_UPDATE).setPackage(getPackageName()));}
        catch(RuntimeException ignored){}
    }
    @Override public IBinder onBind(Intent i){return null;}
}
