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

    public static final class Snapshot {
        public boolean active=false;
        public long id=0;
        public String host="ya.ru", label="Яндекс", ip="", error="", method="ICMP", route="", vpnInfo="", warning="";
        public int port=443;
        public long version=0;
        public int planned, sent, done, ok, lost, skipped, ttl=-1, limit=0, intervalMs=200;
        public double last=-1, min=Double.MAX_VALUE, max=0, total, jitterTotal, previous=-1;
        public int jitterCount;
        public long started;
        public final ArrayList<Float> chart = new ArrayList<>();
        public final ArrayList<String> log = new ArrayList<>();
        public double avg(){return ok==0?-1:total/ok;}
        public double lossPct(){return sent==0?0:100.0*lost/sent;}
        public double jitter(){return jitterCount==0?0:jitterTotal/jitterCount;}
        public Snapshot copy(){
            Snapshot s=new Snapshot();
            s.active=active;s.id=id;s.host=host;s.label=label;s.ip=ip;s.error=error;s.method=method;s.route=route;s.vpnInfo=vpnInfo;s.warning=warning;s.port=port;s.version=version;s.planned=planned;
            s.sent=sent;s.done=done;s.ok=ok;s.lost=lost;s.skipped=skipped;s.ttl=ttl;
            s.limit=limit;s.intervalMs=intervalMs;s.last=last;s.min=min;s.max=max;
            s.total=total;s.previous=previous;s.jitterTotal=jitterTotal;s.jitterCount=jitterCount;
            s.started=started;s.chart.addAll(chart);s.log.addAll(log);return s;
        }
    }
    public static Snapshot snapshot() { synchronized(LOCK){return live.copy();} }

    private ScheduledExecutorService clock;
    private ThreadPoolExecutor workers;
    private PowerManager.WakeLock wakeLock;
    private WifiManager.WifiLock wifiLock;
    private NotificationManager notify;
    private String address="";
    private int bytes=64, ttl=64, timeout=4;
    private volatile boolean sessionVpn=false;
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
        boolean vpn=VpnGuard.active(this);
        sessionVpn=vpn;
        synchronized(LOCK){
            live=new Snapshot();live.active=true;live.id=System.currentTimeMillis();live.host=chosen;
            live.label=intent.getStringExtra("label")==null?chosen:intent.getStringExtra("label");
            live.started=System.currentTimeMillis();live.limit=limit;live.intervalMs=interval;
            live.method="ICMP";
            live.vpnInfo=vpn?"VPN включён":"VPN не обнаружен";
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
                String route=vpn?"Через VPN":"Без VPN";
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
        if(VpnGuard.active(this)!=sessionVpn){finish("VPN изменился. Начните новый тест для корректного маршрута.");return;}
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
                live.sent--;live.skipped++;addLog("#"+seq+" • пропуск: очередь заполнена");live.version++;}
            signalUpdate();checkFinished();
        }
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
                Matcher m=TIME.matcher(output);Matcher t=TTL.matcher(output);
                if(m.find())try{rtt=Double.parseDouble(m.group(1).replace(',','.'));}catch(NumberFormatException ignored){}
                if(t.find())try{replyTtl=Integer.parseInt(t.group(1));}catch(NumberFormatException ignored){}
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
                addLog(String.format(Locale.US,"#%d  •  %.2f мс%s",seq,rtt,replyTtl<0?"":"  •  TTL "+replyTtl));
            }else if(fatal){live.error=error;addLog("#"+seq+" • "+error);}
            else{live.lost++;addLog("#"+seq+"  •  "+error);}
            if(!fatal){live.chart.add(rtt<0?-1f:(float)rtt);if(live.chart.size()>120)live.chart.remove(0);}
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
        if(live.log.size()>180)live.log.remove(0);live.log.add(msg);
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
        if(s.ok==0&&s.sent>0)content=s.ok+" / "+s.sent+" • ответов нет";
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
            j.put("sent",s.sent);j.put("ok",s.ok);j.put("lost",s.lost);j.put("skipped",s.skipped);
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
