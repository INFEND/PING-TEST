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
    private static final Pattern TIME = Pattern.compile("\\btime[=<]\\s*([0-9]+(?:[.,][0-9]+)?)(?![0-9.,eE+\\-\\w])", Pattern.CASE_INSENSITIVE);
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
        public int jitterCount, timed;
        public long started;
        public final ArrayList<Float> chart = new ArrayList<>();
        public final ArrayList<String> log = new ArrayList<>();
        public final ArrayList<ProbeEvent> events = new ArrayList<>();
        public double avg(){return timed==0?-1:total/timed;}
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
            s.total=total;s.previous=previous;s.jitterTotal=jitterTotal;s.jitterCount=jitterCount;s.timed=timed;
            s.started=started;s.chart.addAll(chart);s.log.addAll(log);s.events.addAll(events);return s;
        }
    }
    public static Snapshot snapshot() { synchronized(LOCK){return live.copy();} }

    private ScheduledExecutorService clock;
    private ThreadPoolExecutor workers;
    // Track active native ping processes so STOP can terminate them immediately.
    private final Set<java.lang.Process> activePings=Collections.newSetFromMap(new ConcurrentHashMap<java.lang.Process,Boolean>());
    private PowerManager.WakeLock wakeLock;
    private WifiManager.WifiLock wifiLock;
    private NotificationManager notify;
    private String address="";
    private int bytes=64, ttl=64, timeout=4, chartLimit=150;
    private volatile VpnGuard.Route sessionRoute=VpnGuard.Route.UNKNOWN;
    // Network identity is stronger than the VPN/direct label: Wi-Fi to cellular
    // can change the actual ICMP path while both routes remain DIRECT.
    private volatile Network sessionNetwork;
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
            live=new Snapshot();live.active=true;
            // Millisecond timestamps can repeat across rapid STOP/START cycles.
            // Keep history keys and stale-callback guards strictly increasing.
            live.id=Math.max(System.currentTimeMillis(),runId+1);live.host=chosen;
            live.label=intent.getStringExtra("label")==null?chosen:intent.getStringExtra("label");
            live.started=System.currentTimeMillis();live.limit=limit;live.intervalMs=interval;live.chartLimit=chartLimit;
            live.method="ICMP";
            live.vpnInfo=vpn?"VPN включён":selectedRoute==VpnGuard.Route.DIRECT?
                "Сеть приложения без VPN":"Сеть по умолчанию не определена";
            addLog("PING TEST • " + live.label + " | "+interval+" мс"+(vpn?" | VPN":""));
        }
        stopping=false; address="";sessionNetwork=null;
        final long expectedRun=live.id;runId=expectedRun;
        startForeground(ONGOING,makeNotification(snapshot()));
        acquireLocks();
        workers=new ThreadPoolExecutor(20,20,0L,TimeUnit.MILLISECONDS,new SynchronousQueue<Runnable>(), r->{Thread t=new Thread(r,"PingProbe");t.setDaemon(true);return t;});
        clock=Executors.newSingleThreadScheduledExecutor(r->{Thread t=new Thread(r,"PingClock");t.setDaemon(true);return t;});
        new Thread(()->{
            try{
                String route=vpn?"Сеть по умолчанию: VPN":selectedRoute==VpnGuard.Route.DIRECT?
                    "Сеть по умолчанию: без VPN":"Не определён";
                ConnectivityManager connectivity=(ConnectivityManager)getSystemService(CONNECTIVITY_SERVICE);
                Network activeNetwork=connectivity==null?null:connectivity.getActiveNetwork();
                // Resolve on this UID's active network, including split-tunnel VPN exclusions.
                // DNS must use only the active network selected for this application's UID.
                if(activeNetwork==null)throw new UnknownHostException("Сеть приложения не определена");
                InetAddress[] resolved=activeNetwork.getAllByName(chosen);
                if(resolved.length==0)throw new UnknownHostException(chosen);
                // Reject DNS results from a network that disappeared during resolution.
                // Otherwise the first ICMP packets may be attributed to a stale route.
                if(!activeNetwork.equals(connectivity.getActiveNetwork()))
                    throw new UnknownHostException("Сеть приложения изменилась во время DNS");
                final String resolvedAddress=preferV4(resolved).getHostAddress();
                // Publish the network atomically for the active session only.
                synchronized(LOCK){if(!live.active || runId!=expectedRun || stopping)return;
                    sessionNetwork=activeNetwork;
                    live.ip=resolvedAddress;live.route=route;live.method="ICMP";
                    addLog("Сеть приложения: "+route);live.version++;}
                signalUpdate();
                synchronized(LOCK){if(!live.active || runId!=expectedRun || stopping)return;
                    ScheduledExecutorService c=clock;
                    if(c!=null&&!c.isShutdown())
                        c.scheduleAtFixedRate(()->tick(expectedRun),0,interval,TimeUnit.MILLISECONDS);
                }
                if(runId==expectedRun&&!stopping)refreshNotification(true);
            }catch(Exception e){
                // DNS may complete after the user stopped this run. Never let an
                // old resolver terminate a newer session or overwrite its error.
                synchronized(LOCK){if(runId!=expectedRun || !live.active || stopping)return;
                    live.error="Подключение: "+safeMessage(e);addLog("ОШИБКА: "+safeMessage(e));live.version++;}
                finishRun(expectedRun,"Проверка недоступна: "+safeMessage(e));
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
    private void tick(long scheduledRun){
        if(stopping || scheduledRun!=runId)return;
        ConnectivityManager cm=(ConnectivityManager)getSystemService(CONNECTIVITY_SERVICE);
        Network currentNetwork=cm==null?null:cm.getActiveNetwork();
        Network initialNetwork=sessionNetwork;
        if(initialNetwork==null || !initialNetwork.equals(currentNetwork)){
            finishRun(scheduledRun,"Сеть приложения изменилась. Начните новую проверку.");return;
        }
        VpnGuard.Route currentRoute=VpnGuard.route(this);
        if(currentRoute!=VpnGuard.Route.UNKNOWN&&sessionRoute!=VpnGuard.Route.UNKNOWN
            &&currentRoute!=sessionRoute){
            finishRun(scheduledRun,"Сеть по умолчанию изменилась. Начните новую проверку.");return;
        }
        final int seq;final long capturedRun=scheduledRun;
        final String probeAddress;
        final int probeBytes,probeTtl,probeTimeout;
        synchronized(LOCK){
            // An old scheduler may fire after STOP and a new START.
            // Never let it dispatch probes or increment the new session's counters.
            if(stopping || runId!=capturedRun || !live.active ||
                (live.limit>0 && live.planned>=live.limit))return;
            probeAddress=live.ip;
            if(probeAddress==null || probeAddress.isEmpty())return;
            probeBytes=bytes;probeTtl=ttl;probeTimeout=timeout;
            seq=++live.planned;live.sent++;live.version++;
        }
        try{
            workers.execute(()->probe(seq,capturedRun,probeAddress,probeBytes,probeTtl,probeTimeout));
            signalUpdate();
        }catch(RejectedExecutionException ex){
            synchronized(LOCK){if(capturedRun!=runId || !live.active)return;
                live.sent--;live.skipped++;addProbeEvent(seq,-1,probeBytes,"Пропуск: очередь заполнена");live.version++;}
            signalUpdate();checkFinished(capturedRun);
        }
    }
    /**
     * Android toybox ping prints "N bytes from ADDRESS: ... time=...".
     * Require ICMP sequence 1 (each native process sends exactly one request) on the selected address, not arbitrary
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
            "(?:%[\\w.:-]+)?(?::|\\s)(?=[^\\r\\n]*\\bicmp_seq[= ]1\\b)[^\\r\\n]*$",Pattern.CASE_INSENSITIVE);
        Matcher lines=reply.matcher(output);
        while(lines.find()){
            String line=lines.group();
            Matcher time=TIME.matcher(line);
            if(!time.find())continue;
            try{
                double latency=Double.parseDouble(time.group(1).replace(',','.'));
                // A bounded RTT is not an exact numeric measurement.
                if(line.charAt(time.start()+4)=='<')latency=-2;
                if(!Double.isFinite(latency)||(latency<0&&latency!=-2))continue;
                Matcher ttl=TTL.matcher(line);
                int replyTtl=-1;
                if(ttl.find())try{replyTtl=Integer.parseInt(ttl.group(1));}
                    catch(NumberFormatException ignored){}
                return new double[]{latency,replyTtl};
            }catch(NumberFormatException ignored){}
        }
        return null;
    }

    /** Native ping diagnostics vary in capitalization across Android vendors.
     * These local failures must not be counted as ICMP packet loss. */
    private static boolean isDnsFailure(String output){
        String text=output.toLowerCase(Locale.ROOT);
        return text.contains("unknown host")||text.contains("bad address")||
            text.contains("name or service not known")||
            text.contains("temporary failure in name resolution")||
            text.contains("nodename nor servname provided")||
            text.contains("name resolution failed");
    }
    private static boolean isNetworkFailure(String output){
        String text=output.toLowerCase(Locale.ROOT);
        return text.contains("network is unreachable")||
            text.contains("network unreachable")||
            text.contains("no route to host")||
            text.contains("host is unreachable")||
            text.contains("host unreachable")||
            text.contains("destination host unreachable")||
            text.contains("destination net unreachable")||
            text.contains("destination network unreachable")||
            text.contains("destination unreachable")||
            text.contains("network is down")||
            text.contains("connect: invalid argument")||
            text.contains("address family not supported by protocol")||
            text.contains("protocol not supported")||
            text.contains("socket: permission denied")||
            text.contains("cannot assign requested address")||
            text.contains("no buffer space available")||
            text.contains("message too long")||
            text.contains("network interface is down");
    }

    /** Exit code 1 alone is not proof of ICMP loss: vendor ping builds may
     * also return 1 for unsupported flags, malformed output or local errors.
     * Only an explicit no-reply outcome can increment the loss counter. */
    private static boolean isConfirmedNoReply(String output){
        if(output==null||output.isEmpty())return false;
        String text=output.toLowerCase(Locale.ROOT);
        // A local socket/route failure can accompany a zero-received summary.
        // Such an attempt is not proof that an ICMP echo actually left the UID.
        if(isNetworkFailure(output)||isDnsFailure(output)||
            text.contains("permission denied")||text.contains("operation not permitted")||
            text.contains("sendto:")||text.contains("sendmsg:")||
            text.contains("socket:")||text.contains("invalid argument")||
            text.contains("network is down"))return false;
        // A vendor may print "Request timeout" even when its own summary
        // reports that no echo was transmitted. Explicit zero transmission
        // must override timeout wording: no packet left this process.
        Pattern zeroTransmitted=Pattern.compile(
            "(?m)^\\s*0\\s+packets? transmitted\\b",Pattern.CASE_INSENSITIVE);
        if(zeroTransmitted.matcher(output).find())return false;
        // A summary reporting a received echo contradicts an earlier timeout
        // line. Never manufacture a lost packet from mixed vendor diagnostics.
        Pattern positiveReceived=Pattern.compile(
            "(?m)^\\s*[1-9]\\d*\\s+packets? transmitted,\\s*[1-9]\\d*\\s+(?:packets? )?received\\b",
            Pattern.CASE_INSENSITIVE);
        if(positiveReceived.matcher(output).find())return false;
        if(text.contains("request timeout")||text.contains("timed out waiting for reply"))
            return true;
        // Require at least ONE transmitted packet. "0 transmitted, 0 received"
        // is a local failure, never a confirmed lost echo.
        Pattern zeroReceived=Pattern.compile(
            "(?m)^\\s*[1-9]\\d*\\s+packets? transmitted,\\s*0\\s+(?:packets? )?received\\b",
            Pattern.CASE_INSENSITIVE);
        return zeroReceived.matcher(output).find();
    }

    private void probe(int seq,long capturedRun,String probeAddress,int probeBytes,int probeTtl,int probeTimeout){
        double rtt=-1;int replyTtl=-1;String error="";
        java.lang.Process process=null;
        try{
            String binary=new File("/system/bin/ping").exists()?"/system/bin/ping":"ping";
            String[] cmd={binary,"-n","-c","1","-W",Integer.toString(probeTimeout),"-s",Integer.toString(probeBytes),"-t",Integer.toString(probeTtl),probeAddress};
            process=new ProcessBuilder(cmd).redirectErrorStream(true).start();
            activePings.add(process);
            // STOP may race with process startup: never leave a newly spawned ping alive.
            if(stopping || capturedRun!=runId)process.destroyForcibly();
            // Drain stdout concurrently: waiting before reading can deadlock if
            // a vendor ping fills the OS pipe while the parent waits for exit.
            // Keep at most 8 KiB of diagnostics but continue draining the pipe.
            final ByteArrayOutputStream buffer=new ByteArrayOutputStream();
            final java.util.concurrent.atomic.AtomicBoolean outputTruncated=new java.util.concurrent.atomic.AtomicBoolean(false);
            final java.util.concurrent.atomic.AtomicBoolean outputReadFailed=new java.util.concurrent.atomic.AtomicBoolean(false);
            final InputStream input=process.getInputStream();
            Thread reader=new Thread(()->{
                byte[] temp=new byte[2048];int read;
                try{
                    while((read=input.read(temp))!=-1){
                        synchronized(buffer){
                            int remaining=8192-buffer.size();
                            if(read>remaining)outputTruncated.set(true);
                            if(remaining>0)buffer.write(temp,0,Math.min(read,remaining));
                        }
                    }
                }catch(IOException ignored){
                    // Incomplete diagnostics cannot prove an ICMP timeout.
                    outputReadFailed.set(true);
                }
            },"PingOutput");
            reader.setDaemon(true);
            reader.start();
            boolean finished=process.waitFor(probeTimeout+3,TimeUnit.SECONDS);
            if(!finished){
                process.destroyForcibly();
                // A timed-out process may leave its pipe reader blocked. Close the
                // stream and join briefly so repeated probes do not leak readers.
                try{input.close();}catch(IOException ignored){}
                reader.join(200);
                error="Локальный тайм-аут процесса ping";
            }
            else{
                // Process has exited; wait briefly for the reader to consume
                // remaining pipe bytes before parsing the reply.
                reader.join(1000);
                if(reader.isAlive()){
                    // The child has already exited. Some Android vendors throw
                    // IOException when closing an exhausted process pipe.
                    // Cleanup must not turn a valid ICMP reply into a local error.
                    try{input.close();}catch(IOException ignored){}
                    reader.join(200);
                }
                // An unfinished reader means diagnostics may be incomplete.
                // Do not infer packet loss from an unfinished read.
                if(reader.isAlive())outputReadFailed.set(true);
                String output;
                synchronized(buffer){output=new String(buffer.toByteArray(),StandardCharsets.UTF_8);}

                // A time= token in diagnostic text is not proof of an ICMP reply.
                // Only accept an actual successful ping process and a reply line
                // naming the probed address. Prevents false-positive latency.
                int exitCode=process.exitValue();
                double[] parsed=exitCode==0?parseIcmpReply(output,probeAddress):null;
                if(parsed!=null){rtt=parsed[0];replyTtl=(int)parsed[1];}
                if(rtt<0&&rtt!=-2){
                    // A vendor may emit more than the bounded 8 KiB capture.
                    // Missing reply text in truncated diagnostics is not evidence of packet loss.
                    if(outputTruncated.get())error="Вывод ping превышает 8 КиБ";
                    else if(outputReadFailed.get())error="Не удалось полностью прочитать вывод ping";
                    else if(output.toLowerCase(Locale.ROOT).contains("operation not permitted")||
                            output.toLowerCase(Locale.ROOT).contains("permission denied"))
                        error="Пинг запрещён системой";
                    else if(output.toLowerCase(Locale.ROOT).contains("unknown option")||
                            output.toLowerCase(Locale.ROOT).contains("invalid option")||
                            output.toLowerCase(Locale.ROOT).contains("usage:"))
                        error="Параметры ping не поддерживаются прошивкой";
                    else if(isDnsFailure(output))error="Не удалось разрешить адрес узла";
                    else if(isNetworkFailure(output))error="Сеть недоступна";
                    // Only exit 1 means no ICMP reply. Any other nonzero code,
                    // including negative vendor-specific codes, is a local failure.
                    else if(exitCode==1&&isConfirmedNoReply(output))error="Нет ответа";
                    else if(exitCode==1)error="Неоднозначный результат ping (код 1)";
                    else if(exitCode==0)error="Ответ ping не распознан";
                    else error="Локальная ошибка ping (код "+exitCode+")";
                }
            }
        }catch(InterruptedException e){Thread.currentThread().interrupt();error="Прервано";}
        catch(Exception e){error="Ошибка запуска ping: "+e.getMessage();}
        finally{if(process!=null){activePings.remove(process);try{if(process.isAlive())process.destroyForcibly();else process.destroy();}catch(Exception ignored){}}}
        // A route may change while the native ping process is running, after
        // tick() checked the UID network. Never classify that result as a reply
        // or packet loss from the original network.
        ConnectivityManager resultConnectivity=(ConnectivityManager)getSystemService(CONNECTIVITY_SERVICE);
        Network resultNetwork=resultConnectivity==null?null:resultConnectivity.getActiveNetwork();
        Network expectedNetwork=sessionNetwork;
        if(expectedNetwork==null || !expectedNetwork.equals(resultNetwork)){
            finishRun(capturedRun,"Сеть приложения изменилась во время ICMP. Начните новую проверку.");
            return;
        }
        // The Network handle can remain stable while its capabilities change
        // (for example during VPN handover). Do not attribute an in-flight
        // result to the route captured at the start of this session.
        VpnGuard.Route resultRoute=VpnGuard.route(this);
        if(sessionRoute!=VpnGuard.Route.UNKNOWN && resultRoute!=sessionRoute){
            finishRun(capturedRun,"Маршрут приложения изменился во время ICMP. Начните новую проверку.");
            return;
        }
        // Local routing/permission/command failures are not ICMP packet loss.
        // Only an attempted probe with no reply contributes to loss statistics.
        boolean fatal=error.startsWith("Пинг запрещён")||
                error.startsWith("Параметры ping")||
                error.startsWith("Ошибка запуска ping")||
                error.startsWith("Сеть недоступна")||
                 error.startsWith("Не удалось разрешить адрес узла")||
                error.startsWith("Локальная ошибка ping")||
                error.startsWith("Локальный тайм-аут процесса ping")||
                error.startsWith("Вывод ping превышает 8 КиБ")||
                error.startsWith("Не удалось полностью прочитать вывод ping")||
                error.startsWith("Ответ ping не распознан")||
                error.startsWith("Неоднозначный результат ping")||
                error.equals("Прервано");
        synchronized(LOCK){
            if(!live.active||runId!=capturedRun)return;
            live.done++;
            if(rtt>=0||rtt==-2){
                live.ok++;
                if(rtt>=0){live.timed++;live.last=rtt;live.total+=rtt;live.min=Math.min(live.min,rtt);live.max=Math.max(live.max,rtt);
                if(live.previous>=0){live.jitterTotal+=Math.abs(rtt-live.previous);live.jitterCount++;}
                live.previous=rtt;}else{live.last=-1;live.previous=-1;}
                if(replyTtl>=0)live.ttl=replyTtl;
                addProbeEvent(seq,rtt,probeBytes,"");
            }else if(fatal){live.error=error;addProbeEvent(seq,-1,probeBytes,error);}
            else{live.lost++;addProbeEvent(seq,-1,probeBytes,error);}
            // Keep the bounded '<1 ms' successful outcome separate from an
            // actual lost packet. Neither is a precise numeric RTT.
            if(!fatal){live.chart.add(rtt==-2?-2f:rtt<0?-1f:(float)rtt);
                while(live.chart.size()>live.chartLimit)live.chart.remove(0);}
            live.version++;
        }
        signalUpdate();
        if(fatal){finishRun(capturedRun,error);return;}
        if(capturedRun!=runId)return;
        refreshNotification(false);
        if(seq%10==0)persist(false);
        checkFinished(capturedRun);
    }
    private static void addLog(String msg){
        if(live.log.size()>=600)live.log.remove(0);
        live.log.add(msg);
        addEvent(new ProbeEvent(0,-1,0,msg));
    }
    private static void addProbeEvent(int seq,double rtt,int payloadBytes,String error){
        String line=String.format(Locale.US,"#%d  |  %s  |  %d",seq,
            rtt==-2?"<1 мс":rtt>=0?String.format(Locale.US,"%.1f мс",rtt):error,payloadBytes);
        if(live.log.size()>=600)live.log.remove(0);
        live.log.add(line);
        addEvent(new ProbeEvent(seq,rtt,payloadBytes,error));
    }
    private static void addEvent(ProbeEvent event){
        if(live.events.size()>=600)live.events.remove(0);
        live.events.add(event);
    }
    private void checkFinished(long expectedRun){
        synchronized(LOCK){
            if(stopping || runId!=expectedRun || !live.active || live.limit<=0 ||
                live.planned<live.limit || live.done+live.skipped<live.planned)return;
        }
        finishRun(expectedRun,"Завершено");
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
        int classified=s.ok+s.lost;
        String routeLabel=s.vpnInfo.contains("включён")?"С VPN":
                s.vpnInfo.contains("не определена")?"Сеть неизвестна":"Без VPN";
        String content=s.sent==0?"Подключение к узлу…":
                String.format(Locale.US,"%s · %d/%d завершено · %s · потери %.1f%%",
                    routeLabel,s.ok,classified,s.timed>0?String.format(Locale.US,"%.0f мс",s.avg()):s.ok>0?"<1 мс":"ожидание",s.lossPct());
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
            if(s.timed>0)sb.append(String.format(Locale.US,"\nmin / avg / max: %.1f / %.1f / %.1f мс",s.min,s.avg(),s.max));
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
            j.put("min",s.timed>0?s.min:-1);j.put("avg",s.avg());j.put("max",s.timed>0?s.max:-1);j.put("timed",s.timed);
            j.put("jitter",s.jitter());j.put("ttl",s.ttl);j.put("finished",finished);
            // Preserve measured events verbatim; legacy text logs remain readable.
            org.json.JSONArray recorded=new org.json.JSONArray();
            for(ProbeEvent e:s.events){
                org.json.JSONObject item=new org.json.JSONObject();
                item.put("number",e.number);
                item.put("latencyMs",e.latencyMs);
                item.put("payloadBytes",e.payloadBytes);
                item.put("message",e.message);
                recorded.put(item);
            }
            j.put("events",recorded);
            j.put("log",String.join("\n",s.log));
            HistoryStore.upsert(this,j);
        }catch(Exception e){Log.e("PING TEST","History save",e);}
    }
    /** Terminate only the session that produced the callback.
     * A late probe/DNS callback must never stop a subsequent session. */
    private synchronized void finishRun(long expectedRun,String reason){
        synchronized(LOCK){if(runId!=expectedRun || !live.active)return;}
        finish(reason);
    }
    private void terminateActivePings(){
        for(java.lang.Process process:activePings){try{process.destroyForcibly();}catch(Exception ignored){}}
    }
    private synchronized void finish(String reason){
        if(stopping)return;stopping=true;
        synchronized(LOCK){if(!live.active){stopSelf();return;}live.active=false;addLog("● "+reason);live.version++;if(!reason.equals("Завершено")&&!reason.equals("Остановлено пользователем"))live.error=reason;}
        if(clock!=null)clock.shutdownNow();
        if(workers!=null)workers.shutdownNow();
        terminateActivePings();
        signalUpdate();persist(true);releaseLocks();notify.cancel(GRAPH);
        if(Build.VERSION.SDK_INT>=24)stopForeground(STOP_FOREGROUND_REMOVE);else stopForeground(true);
        stopSelf();
    }
    @Override public void onDestroy(){
        if(!stopping){synchronized(LOCK){live.active=false;addLog("● Служба остановлена системой");}persist(true);}
        if(clock!=null)clock.shutdownNow();if(workers!=null)workers.shutdownNow();
        terminateActivePings();
        releaseLocks();notify.cancel(GRAPH);super.onDestroy();
    }
    private void signalUpdate(){
        try{sendBroadcast(new Intent(ACTION_UPDATE).setPackage(getPackageName()));}
        catch(RuntimeException ignored){}
    }
    @Override public IBinder onBind(Intent i){return null;}
}
