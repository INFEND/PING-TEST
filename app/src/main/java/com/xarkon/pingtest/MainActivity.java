package com.xarkon.pingtest;

import android.Manifest;
import android.animation.ValueAnimator;
import android.app.*;
import android.content.*;
import android.content.pm.PackageManager;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.text.SpannableStringBuilder;
import android.text.style.ForegroundColorSpan;
import android.text.Spanned;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import android.graphics.Typeface;
import android.graphics.drawable.ColorDrawable;
import android.net.*;
import android.provider.Settings;
import android.os.*;
import android.text.*;
import android.view.*;
import android.view.animation.DecelerateInterpolator;
import android.view.inputmethod.InputMethodManager;
import android.widget.*;
import org.json.*;
import java.net.*;
import java.text.*;
import java.util.*;

/** PING TEST 1.5.0 • QR LINK design language • Android framework only. */
public final class MainActivity extends Activity {
    private int tab=0;
    private final Handler handler=new Handler(Looper.getMainLooper());
    private final Runnable periodic=new Runnable(){@Override public void run(){
        if(tab==0)refreshPing();
        long now=SystemClock.elapsedRealtime();
        if(now-lastVpnUiCheck>1100){lastVpnUiCheck=now;showVpnOnEntry();}
        handler.postDelayed(this,180);
    }};
    private final Runnable immediate=()->{if(tab==0)refreshPing();};
    private final BroadcastReceiver updates=new BroadcastReceiver(){@Override public void onReceive(Context c,Intent i){
        handler.removeCallbacks(immediate);handler.postDelayed(immediate,16);
    }};
    private boolean registered=false;
    private long renderedVersion=-1,seenSession=-1;
    private boolean activeBefore=false;
    private LinearLayout root,page,nav;
    private TextView host;
    private boolean vpnConsent=false,vpnDialogVisible=false;
    private long lastVpnUiCheck=0;
    private ScrollView scroller;
    private TextView status,go,ip,info,logText,sendText,bestText,maxText,jitterText,unit,qualityState;
    private Metric last,avg,failed;
    private GraphView graph;
    private boolean noEntrance=false;
    private final HashSet<String> openSections=new HashSet<>();
    private ValueAnimator replyColorAnimator;
    private Dialog journalDialog;
    private TextView journalBody;
    private ScrollView journalScroll;
    private String journalLast="";
    private final Runnable journalTick=new Runnable(){@Override public void run(){
        if(journalDialog==null||!journalDialog.isShowing())return;
        refreshJournal();handler.postDelayed(this,140);
    }};
    private static final int OK=0xFF65DDBB, BAD=0xFFFFA875;

    @Override public void onCreate(Bundle state){super.onCreate(state);
        getWindow().setStatusBarColor(0xFF000000);getWindow().setNavigationBarColor(0xFF000000);
        getWindow().getDecorView().setSystemUiVisibility(0);
        if(Build.VERSION.SDK_INT>=30)getWindow().setDecorFitsSystemWindows(false);
        else getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LAYOUT_STABLE|View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN|View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
        if(Build.VERSION.SDK_INT>=29)getWindow().setNavigationBarContrastEnforced(false);
        showTab(0);
        OtaUpdateSchedule.configure(this);
        if(getSharedPreferences("settings",0).getBoolean(OtaUpdateSchedule.PREF_ON_LAUNCH,false))handler.postDelayed(()->UpdateManager.check(this),1900L);
        if(Build.VERSION.SDK_INT>=33&&checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},101);
    }
    @Override protected void onResume(){super.onResume();handler.removeCallbacks(periodic);handler.post(periodic);
        if(!registered){try{IntentFilter f=new IntentFilter(PingService.ACTION_UPDATE);
            if(Build.VERSION.SDK_INT>=33)registerReceiver(updates,f,Context.RECEIVER_NOT_EXPORTED);else registerReceiver(updates,f);
            registered=true;}catch(Exception ignored){}}
        handler.post(immediate);handler.postDelayed(this::checkClipboard,350);
        if(journalDialog!=null&&journalDialog.isShowing()){handler.removeCallbacks(journalTick);handler.post(journalTick);}
        handler.postDelayed(this::showVpnOnEntry,180);
    }
    @Override protected void onPause(){handler.removeCallbacks(periodic);handler.removeCallbacks(immediate);
        handler.removeCallbacks(journalTick);
        if(registered){try{unregisterReceiver(updates);}catch(Exception ignored){}registered=false;}super.onPause();}
    @Override protected void onDestroy(){handler.removeCallbacks(periodic);handler.removeCallbacks(immediate);
        handler.removeCallbacks(journalTick);super.onDestroy();}
    @Override public void onBackPressed(){if(tab==0)super.onBackPressed();else showTab(0);}

    private void showTab(int next){
        if(replyColorAnimator!=null){replyColorAnimator.cancel();replyColorAnimator=null;}
        tab=next;host=null;go=null;last=null;avg=null;failed=null;graph=null;qualityState=null;
        root=Ui.vertical(this);root.setBackgroundColor(Ui.bg(this));
        root.setOnApplyWindowInsetsListener((v,insets)->{
            int top,bottom;if(Build.VERSION.SDK_INT>=30){android.graphics.Insets st=insets.getInsets(WindowInsets.Type.systemBars()|WindowInsets.Type.displayCutout());top=st.top;bottom=st.bottom;}
            else{top=insets.getSystemWindowInsetTop();bottom=insets.getSystemWindowInsetBottom();}
            if(v.getPaddingTop()!=top||v.getPaddingBottom()!=bottom)v.setPadding(0,top,0,bottom);
            return insets;
        });
        setContentView(root);root.requestApplyInsets();
        header();
        scroller=new ScrollView(this);scroller.setClipToPadding(false);scroller.setFillViewport(false);
        scroller.setVerticalScrollBarEnabled(false);
        page=Ui.vertical(this);page.setPadding(Ui.dp(15),Ui.dp(11),Ui.dp(15),Ui.dp(22));
        scroller.addView(page,new ScrollView.LayoutParams(-1,-2));
        root.addView(scroller,new LinearLayout.LayoutParams(-1,0,1));
        if(tab==0)pingPage();else if(tab==1)historyPage();else settingsPage();
        navigation();
        if(!noEntrance&&AppPrefs.bool(this,"motion",true)){
            page.setAlpha(.45f);page.setTranslationY(Ui.dp(7));page.animate().alpha(1).translationY(0).setDuration(190)
                .setInterpolator(new DecelerateInterpolator(1.35f)).start();
        }
    }
    private void header(){
        LinearLayout l=Ui.horizontal(this);l.setPadding(Ui.dp(20),Ui.dp(10),Ui.dp(20),Ui.dp(10));
        ImageView mark=new ImageView(this);mark.setImageResource(R.drawable.ic_pulse);
        mark.setImageTintList(ColorStateList.valueOf(AppPrefs.accent(this)));
        mark.setPadding(Ui.dp(5),Ui.dp(5),Ui.dp(5),Ui.dp(5));
        mark.setBackground(Ui.shape(Ui.surface2(this),Ui.dp(12),0));
        l.addView(mark,new LinearLayout.LayoutParams(Ui.dp(35),Ui.dp(35)));
        LinearLayout title=Ui.vertical(this);title.setPadding(Ui.dp(8),0,0,0);
        TextView a=Ui.text(this,"PING TEST",19,Ui.fg(),true);a.setLetterSpacing(.045f);title.addView(a);
        TextView b=Ui.text(this,"СЕТЕВОЙ МОНИТОР",10,Ui.muted(),false);b.setLetterSpacing(.13f);title.addView(b);
        l.addView(title,new LinearLayout.LayoutParams(0,-2,1));
        status=Ui.chip(this,"● ГОТОВ",false);status.setTextSize(10);status.setClickable(false);l.addView(status);
        root.addView(l);root.addView(Ui.divider(this),Ui.margins(-1,1,0,0));
        refreshStatus();
    }
    private void refreshStatus(){refreshStatus(PingService.snapshot());}
    private void refreshStatus(PingService.Snapshot s){if(status==null)return;
        boolean running=s.active;
        status.setText(running?"● LIVE":!s.error.isEmpty()?"● ERROR":"● ГОТОВ");
        status.setTextColor(running?OK:!s.error.isEmpty()?BAD:Ui.muted());
    }
    private void navigation(){
        nav=Ui.horizontal(this);nav.setPadding(Ui.dp(14),Ui.dp(5),Ui.dp(14),Ui.dp(6));
        nav.setBackgroundColor(Ui.surface(this));
        String[] names={"Монитор","История","Настройки"};int[] icons={R.drawable.ic_pulse,R.drawable.ic_history,R.drawable.ic_settings};
        for(int i=0;i<3;i++){final int index=i;boolean selected=i==tab;
            LinearLayout cell=Ui.vertical(this);cell.setGravity(Gravity.CENTER);cell.setPadding(0,Ui.dp(3),0,Ui.dp(4));
            ImageView glyph=new ImageView(this);glyph.setImageResource(icons[i]);
            glyph.setPadding(Ui.dp(4),Ui.dp(4),Ui.dp(4),Ui.dp(4));
            glyph.setImageTintList(ColorStateList.valueOf(selected?AppPrefs.accent(this):Ui.muted()));
            cell.addView(glyph,new LinearLayout.LayoutParams(Ui.dp(29),Ui.dp(29)));
            TextView label=Ui.text(this,names[i],11,selected?Ui.fg():Ui.muted(),selected);
            label.setGravity(Gravity.CENTER);cell.addView(label);
            if(selected)cell.setBackground(Ui.shape(Ui.surface2(this),Ui.dp(13),0));
            nav.addView(cell,new LinearLayout.LayoutParams(0,Ui.dp(51),1));
            cell.setOnClickListener(v->{if(index!=tab)showTab(index);});
        }
        root.addView(nav);
    }
    private TextView label(String text){TextView t=Ui.text(this,text,10,Ui.muted(),true);t.setLetterSpacing(.1f);return t;}
    private void addSpace(LinearLayout l,int h){l.addView(new View(this),new LinearLayout.LayoutParams(1,Ui.dp(h)));}
    private void pingPage(){
        LinearLayout target=Ui.panel(this);target.setPadding(Ui.dp(15),Ui.dp(12),Ui.dp(15),Ui.dp(13));
        target.addView(label("ЦЕЛЕВОЙ УЗЕЛ"));
        LinearLayout row=Ui.horizontal(this);row.setGravity(Gravity.CENTER_VERTICAL);
        host=Ui.text(this,TargetStore.selected(this).name,22,Ui.fg(),true);
        host.setSingleLine(true);host.setEllipsize(TextUtils.TruncateAt.END);
        host.setPadding(0,Ui.dp(11),0,Ui.dp(11));
        row.addView(host,new LinearLayout.LayoutParams(0,-2,1));
        TextView pick=Ui.chip(this,"ИЗМЕНИТЬ  ⌄",false);pick.setTextSize(11);row.addView(pick);
        row.setOnClickListener(v->chooseHost());pick.setOnClickListener(v->chooseHost());
        target.setOnClickListener(v->chooseHost());target.addView(row);
        ip=Ui.text(this,"Готов к проверке",11,Ui.muted(),false);
        ip.setSingleLine(true);ip.setEllipsize(TextUtils.TruncateAt.END);
        target.addView(ip,Ui.margins(-1,-2,0,9));
        go=Ui.button(this,"НАЧАТЬ ПРОВЕРКУ  ›",true);go.setTextSize(13);
        go.setPadding(Ui.dp(8),Ui.dp(11),Ui.dp(8),Ui.dp(11));target.addView(go);
        go.setOnClickListener(v->toggle());
        page.addView(target,Ui.margins(-1,-2,0,11));
        // A single large, legible live panel, with fractional metrics animated.
        LinearLayout display=Ui.panel(this);display.setPadding(Ui.dp(15),Ui.dp(13),Ui.dp(15),Ui.dp(12));
        LinearLayout heading=Ui.horizontal(this);heading.addView(label("ТЕКУЩАЯ ЗАДЕРЖКА"),new LinearLayout.LayoutParams(0,-2,1));
        qualityState=Ui.text(this,"ОЖИДАНИЕ",10,QualityColors.UNKNOWN,true);
        qualityState.setLetterSpacing(.08f);heading.addView(qualityState);display.addView(heading);
        LinearLayout big=Ui.horizontal(this);
        last=new Metric("—",44,QualityColors.UNKNOWN,0);big.addView(last,new LinearLayout.LayoutParams(0,Ui.dp(64),1));
        unit=Ui.text(this,"мс",13,Ui.muted(),false);big.addView(unit);
        display.addView(big);
        View rule=Ui.divider(this);display.addView(rule,Ui.margins(-1,1,0,10));
        LinearLayout metrics=Ui.horizontal(this);
        avg=new Metric("—",20,QualityColors.UNKNOWN,0);miniMetric(metrics,"СРЕДНИЙ",avg,0);
        failed=new Metric("—",20,QualityColors.UNKNOWN,1);miniMetric(metrics,"ПОТЕРИ",failed,1);
        sendText=Ui.text(this,"0 / 0",20,Ui.fg(),true);sendText.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));
        miniMetric(metrics,"ОТВЕТЫ / ВСЕГО",sendText,2);
        display.addView(metrics);
        addSpace(display,11);
        LinearLayout detail=Ui.horizontal(this);
        bestText=Ui.text(this,"MIN —",11,Ui.muted(),false);detail.addView(bestText,new LinearLayout.LayoutParams(0,-2,1));
        maxText=Ui.text(this,"MAX —",11,Ui.muted(),false);detail.addView(maxText,new LinearLayout.LayoutParams(0,-2,1));
        jitterText=Ui.text(this,"JITTER —",11,Ui.muted(),false);detail.addView(jitterText);
        display.addView(detail);
        page.addView(display,Ui.margins(-1,-2,0,11));
        LinearLayout chartCard=Ui.panel(this);chartCard.setPadding(Ui.dp(13),Ui.dp(11),Ui.dp(13),Ui.dp(11));
        LinearLayout graphHead=Ui.horizontal(this);graphHead.addView(label("ГРАФИК ЗАДЕРЖКИ"),new LinearLayout.LayoutParams(0,-2,1));
        graphHead.addView(Ui.text(this,"120 ОТСЧЁТОВ",10,Ui.muted(),false));chartCard.addView(graphHead);
        TextView legend=Ui.text(this,"● Отлично       ● Норма       ● Плохо",10,Ui.muted(),false);
        SpannableStringBuilder legendSpan=new SpannableStringBuilder(legend.getText());
        legendSpan.setSpan(new ForegroundColorSpan(QualityColors.GREEN),0,1,Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
        // Use the actual positions instead of fixed character offsets for localization safety.
        int second=legendSpan.toString().indexOf('●',1),third=legendSpan.toString().indexOf('●',second+1);
        if(second>=0)legendSpan.setSpan(new ForegroundColorSpan(QualityColors.YELLOW),second,second+1,Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
        if(third>=0)legendSpan.setSpan(new ForegroundColorSpan(QualityColors.RED),third,third+1,Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
        legend.setText(legendSpan);chartCard.addView(legend,Ui.margins(-1,-2,0,3));
        graph=new GraphView(this);chartCard.addView(graph,Ui.margins(-1,142,0,7));
        page.addView(chartCard,Ui.margins(-1,-2,0,11));
        LinearLayout events=Ui.panel(this);events.setPadding(Ui.dp(14),Ui.dp(12),Ui.dp(14),Ui.dp(12));
        LinearLayout titleRow=Ui.horizontal(this);titleRow.addView(label("СОБЫТИЯ"),new LinearLayout.LayoutParams(0,-2,1));
        TextView all=Ui.chip(this,"Журнал  ↗",false);all.setTextSize(11);titleRow.addView(all);all.setOnClickListener(v->fullLogDialog());
        events.addView(titleRow);logText=Ui.mono(this,"Готов к запуску",12,Ui.muted());
        logText.setLineSpacing(Ui.dp(3),1f);logText.setPadding(Ui.dp(3),Ui.dp(11),Ui.dp(3),Ui.dp(3));
        events.addView(logText);page.addView(events);
        info=Ui.text(this,"",11,Ui.muted(),false);info.setPadding(Ui.dp(2),Ui.dp(9),Ui.dp(2),Ui.dp(1));
        page.addView(info);
        renderedVersion=-1;activeBefore=false;refreshPing();
    }
    private void miniMetric(LinearLayout parent,String name,TextView value,int index){
        LinearLayout col=Ui.vertical(this);col.setPadding(index==0?0:Ui.dp(9),0,0,0);
        col.addView(label(name));col.addView(value,Ui.margins(-1,29,0,0));
        parent.addView(col,new LinearLayout.LayoutParams(0,-2,index==2?1.35f:1f));
    }
    private void refreshPing(){if(tab!=0||go==null)return;
        PingService.Snapshot s=PingService.snapshot();refreshStatus(s);
        if(!s.active && !s.host.equals(TargetStore.selected(this).host)){
            ip.setText(VpnGuard.active(this)?"● VPN активен  ·  результат через VPN":"● Без VPN  ·  прямое измерение");
            last.update(-1,false,false);avg.update(-1,false,false);failed.update(-1,false,false);
            if(qualityState!=null){qualityState.setText("ОЖИДАНИЕ");qualityState.setTextColor(QualityColors.UNKNOWN);}
            sendText.setText("0 / 0");sendText.setTextColor(QualityColors.UNKNOWN);bestText.setText("MIN  —");maxText.setText("MAX  —");jitterText.setText("JITTER  —");
            bestText.setTextColor(QualityColors.UNKNOWN);maxText.setTextColor(QualityColors.UNKNOWN);
            jitterText.setTextColor(QualityColors.UNKNOWN);
            graph.setData(new ArrayList<Float>(),AppPrefs.accent(this),Ui.surface(this));
            logText.setText(coloredLog("Выбран другой узел. Начните проверку."));
            info.setText("");renderedVersion=-1;seenSession=-1;
            return;
        }
        if(s.active!=activeBefore||renderedVersion<0){activeBefore=s.active;
            go.setText(s.active?"■  ОСТАНОВИТЬ":"НАЧАТЬ ПРОВЕРКУ  ›");
            go.setBackground(Ui.shape(s.active?Ui.surface2(this):AppPrefs.accent(this),Ui.dp(12),s.active?Ui.border():0));
            go.setTextColor(s.active?Ui.fg():0xFF061216);
        }
        if(s.version==renderedVersion&&s.id==seenSession)return;
        boolean sameSession=s.id==seenSession;renderedVersion=s.version;seenSession=s.id;
        boolean vpn=VpnGuard.active(this);
        ip.setText(s.active||s.done>0?(s.vpnInfo.contains("включён")?"● С VPN  ·  маршрут через туннель":"● Без VPN  ·  прямой маршрут"):
            vpn?"● VPN активен  ·  результат через VPN":"● Без VPN  ·  прямое измерение");
        last.update(s.last,false,sameSession);avg.update(s.avg(),false,sameSession);
        boolean unusable=s.ok==0&&s.lost==0&&!s.error.isEmpty();
        failed.update(s.sent==0||unusable?-1:s.lossPct(),true,sameSession);
        if(qualityState!=null){
            double ms=s.last>=0?s.last:s.avg();
            qualityState.setText(ms<0?(s.sent>0?"НЕТ ОТВЕТА":"ОЖИДАНИЕ"):
                ms<=45?"ОТЛИЧНО":ms<=110?"СТАБИЛЬНО":ms<=240?"ПОВЫШЕННАЯ":"ВЫСОКАЯ");
            qualityState.setTextColor(ms<0?(s.sent>0?QualityColors.RED:QualityColors.UNKNOWN):QualityColors.rtt(ms));
        }
        String next=s.ok+" / "+s.sent;
        if(!next.contentEquals(sendText.getText())){
            if(sameSession&&AppPrefs.bool(this,"motion",true)){
                sendText.animate().cancel();sendText.setTranslationY(Ui.dp(3));sendText.setAlpha(.6f);
                sendText.animate().translationY(0).alpha(1).setDuration(130).start();
            }
            int targetColor=unusable?QualityColors.UNKNOWN:QualityColors.success(s.ok,s.sent);
            int currentColor=sendText.getCurrentTextColor();
            if(replyColorAnimator!=null)replyColorAnimator.cancel();
            if(sameSession&&AppPrefs.bool(this,"motion",true)){
                replyColorAnimator=ValueAnimator.ofArgb(currentColor,targetColor);
                replyColorAnimator.setDuration(185);
                replyColorAnimator.addUpdateListener(a->sendText.setTextColor((Integer)a.getAnimatedValue()));
                replyColorAnimator.start();
            }else sendText.setTextColor(targetColor);
            sendText.setText(next);
        }
        bestText.setText("MIN  "+(s.ok==0?"—":fmt(s.min)));
        bestText.setTextColor(s.ok==0?QualityColors.UNKNOWN:QualityColors.rtt(s.min));
        maxText.setText("MAX  "+(s.ok==0?"—":fmt(s.max)));
        maxText.setTextColor(s.ok==0?QualityColors.UNKNOWN:QualityColors.rtt(s.max));
        jitterText.setText("JITTER  "+(s.ok<2?"—":fmt(s.jitter())));
        jitterText.setTextColor(s.ok<2?QualityColors.UNKNOWN:QualityColors.jitter(s.jitter()));
        graph.setData(s.chart,AppPrefs.accent(this),Ui.surface(this));
        StringBuilder text=new StringBuilder();int from=Math.max(0,s.log.size()-3);
        for(int i=from;i<s.log.size();i++)text.append(s.log.get(i)).append(i<s.log.size()-1?"\n":"");
        logText.setText(coloredLog(text.length()==0?"Готов к запуску":text.toString()));
        if(!s.error.isEmpty()){info.setText("ВНИМАНИЕ  •  "+s.error+"  ›");info.setTextColor(BAD);}
        else if(!s.warning.isEmpty()){info.setText("МАРШРУТ  •  "+s.warning+"  ›");info.setTextColor(BAD);}
        else if(!s.route.isEmpty()){info.setText((s.vpnInfo.contains("включён")?"VPN АКТИВЕН  •  ":"СЕТЬ  •  ")+s.route+
            (s.skipped>0?"  ·  пропусков "+s.skipped:""));info.setTextColor(s.vpnInfo.contains("включён")?BAD:Ui.muted());}
        else{info.setText("Ответ может зависеть от ограничений ICMP на сервере.");info.setTextColor(Ui.muted());}
    }
    private String fmt(double value){return String.format(Locale.US,"%.1f",value);}
    private void toggle(){PingService.Snapshot s=PingService.snapshot();
        if(s.active){startService(new Intent(this,PingService.class).setAction(PingService.ACTION_STOP));return;}
        if(VpnGuard.active(this)){if(vpnConsent)beginPing();else vpnWarning(true);return;}
        vpnConsent=false;beginPing();
    }
    private void beginPing(){
        TargetStore.Target target=TargetStore.selected(this);
        String address=target.host;
        if(!TargetStore.validHost(address)){message("Ошибка адреса","Измени целевой узел");return;}
        AppPrefs.put(this,"host",address);
        Intent i=new Intent(this,PingService.class).setAction(PingService.ACTION_START);
        i.putExtra("host",address).putExtra("label",target.name).putExtra("size",AppPrefs.number(this,"size",64))
         .putExtra("ttl",AppPrefs.number(this,"ttl",64)).putExtra("timeout",AppPrefs.number(this,"timeout",3))
         .putExtra("interval",AppPrefs.number(this,"interval",200)).putExtra("count",AppPrefs.number(this,"count",0));
        try{if(Build.VERSION.SDK_INT>=26)startForegroundService(i);else startService(i);}
        catch(Exception e){message("Запуск не выполнен",String.valueOf(e.getMessage()));}
    }
    private String normal(String s){s=s.trim();
        if(s.startsWith("https://")||s.startsWith("http://")){try{URI uri=new URI(s);return uri.getHost()==null?"":uri.getHost();}catch(Exception e){return "";}}
        int slash=s.indexOf('/');if(slash>=0)s=s.substring(0,slash);
        if(s.startsWith("[")&&s.endsWith("]"))s=s.substring(1,s.length()-1);return s;
    }
    private void chooseHost(){
        Dialog dialog=new Dialog(this);
        LinearLayout body=Ui.vertical(this);
        body.setPadding(Ui.dp(16),Ui.dp(16),Ui.dp(16),Ui.dp(14));
        body.setBackground(Ui.shape(Ui.surface(this),Ui.dp(21),Ui.border()));
        LinearLayout heading=Ui.horizontal(this);
        ImageView icon=icon(R.drawable.ic_server,AppPrefs.accent(this),Ui.dp(27));
        heading.addView(icon,Ui.margins(29,29,0,0));
        LinearLayout titles=Ui.vertical(this);titles.setPadding(Ui.dp(10),0,0,0);
        titles.addView(Ui.text(this,"Выбор узла",20,Ui.fg(),true));
        titles.addView(Ui.text(this,"Нажми для переключения",11,Ui.muted(),false));
        heading.addView(titles,new LinearLayout.LayoutParams(0,-2,1));
        TextView add=Ui.chip(this,"＋  Свой",true);add.setTextSize(12);heading.addView(add);
        add.setOnClickListener(v->{dialog.dismiss();editTarget(null);});body.addView(heading,Ui.margins(-1,-2,0,11));
        String previous="";
        TargetStore.Target selected=TargetStore.selected(this);
        for(TargetStore.Target target:TargetStore.all(this)){
            if(!previous.equals(target.category)){
                previous=target.category;
                LinearLayout group=Ui.horizontal(this);
                int categoryIcon=previous.equals("Игры")?R.drawable.ic_gamepad:previous.equals("Сайты")?R.drawable.ic_globe:R.drawable.ic_server;
                group.addView(icon(categoryIcon,AppPrefs.accent(this),Ui.dp(18)),Ui.margins(19,19,0,0));
                TextView name=label(previous.toUpperCase(Locale.ROOT));name.setPadding(Ui.dp(9),0,0,0);
                group.addView(name);group.setPadding(Ui.dp(2),Ui.dp(15),0,Ui.dp(9));
                body.addView(group);
            }
            LinearLayout row=Ui.horizontal(this);row.setGravity(Gravity.CENTER_VERTICAL);
            row.setPadding(Ui.dp(12),Ui.dp(11),Ui.dp(10),Ui.dp(11));
            boolean chosen=target.id.equals(selected.id);
            row.setBackground(Ui.shape(chosen?Ui.surface2(this):Ui.surface(this),Ui.dp(13),chosen?AppPrefs.accent(this):Ui.border()));
            ImageView glyph=icon(target.category.equals("Игры")?R.drawable.ic_gamepad:
                    target.category.equals("Сайты")?R.drawable.ic_globe:R.drawable.ic_server,
                    chosen?AppPrefs.accent(this):Ui.muted(),Ui.dp(22));
            row.addView(glyph,Ui.margins(24,24,0,0));
            LinearLayout labels=Ui.vertical(this);labels.setPadding(Ui.dp(11),0,Ui.dp(4),0);
            labels.addView(Ui.text(this,target.name,14,Ui.fg(),true));
            TextView sub=Ui.text(this,target.note,10,Ui.muted(),false);sub.setMaxLines(2);
            labels.addView(sub,Ui.margins(-1,-2,0,0));
            row.addView(labels,new LinearLayout.LayoutParams(0,-2,1));
            if(chosen)row.addView(icon(R.drawable.ic_check,QualityColors.GREEN,Ui.dp(19)),Ui.margins(21,21,0,0));
            if(target.custom){TextView edit=Ui.chip(this,"✎",false);row.addView(edit);
                edit.setOnClickListener(v->{dialog.dismiss();editTarget(target);});}
            body.addView(row,Ui.margins(-1,-2,0,6));
            row.setOnClickListener(v->{dialog.dismiss();selectTarget(target);});
        }
        TextView note=Ui.text(this,"Игровые сайты не измеряют пинг сервера матча. Fortnite использует диагностический узел Epic Games.",11,Ui.muted(),false);
        note.setPadding(0,Ui.dp(10),0,Ui.dp(11));body.addView(note);
        TextView close=Ui.button(this,"ЗАКРЫТЬ",false);body.addView(close);
        close.setOnClickListener(v->dialog.dismiss());
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(false);scroll.addView(body);
        dialog.setContentView(scroll);dialog.show();Window window=dialog.getWindow();
        if(window!=null){window.setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
            window.setLayout(getResources().getDisplayMetrics().widthPixels-Ui.dp(24),
                (int)(getResources().getDisplayMetrics().heightPixels*.83f));}
    }
    private ImageView icon(int resource,int tint,int paddingSize){
        ImageView image=new ImageView(this);image.setImageResource(resource);
        image.setImageTintList(ColorStateList.valueOf(tint));
        image.setPadding(Ui.dp(2),Ui.dp(2),Ui.dp(2),Ui.dp(2));return image;
    }
    private void selectTarget(TargetStore.Target target){selectTarget(target,false);}
    private void selectTarget(TargetStore.Target target,boolean force){
        boolean running=PingService.snapshot().active;
        if(running&&!force&&target.id.equals(TargetStore.selected(this).id))return;
        TargetStore.select(this,target);
        if(host!=null)host.setText(target.name);
        if(tab==0)refreshPing();
        if(!running){toast("Выбрано: "+target.name);return;}
        startService(new Intent(this,PingService.class).setAction(PingService.ACTION_STOP));
        // Async service teardown must finish before a fresh foreground service starts.
        // Never mix the old host's statistics into the next session.
        handler.postDelayed(new Runnable(){int attempts=0;
            @Override public void run(){
                if(!target.id.equals(TargetStore.selected(MainActivity.this).id))return;
                if(PingService.snapshot().active){
                    if(++attempts<=18)handler.postDelayed(this,130);
                    else toast("Сеанс останавливается. Запусти проверку ещё раз.");
                }else{if(VpnGuard.active(MainActivity.this)&&!vpnConsent)vpnWarning(true);
                      else beginPing();}
            }
        },250);
    }
    private void editTarget(TargetStore.Target current){
        LinearLayout frame=Ui.vertical(this);frame.setPadding(Ui.dp(22),Ui.dp(13),Ui.dp(22),Ui.dp(4));
        EditText name=new EditText(this),address=new EditText(this);
        name.setSingleLine(true);name.setTextColor(Ui.fg());name.setHint("Например: Мой сервер");
        address.setSingleLine(true);address.setTextColor(Ui.fg());address.setHint("Домен или IP");
        address.setInputType(android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_VARIATION_URI);
        if(current!=null){name.setText(current.name);address.setText(current.host);}
        frame.addView(Ui.text(this,"НАЗВАНИЕ",11,Ui.muted(),true));frame.addView(name);
        frame.addView(Ui.text(this,"АДРЕС УЗЛА",11,Ui.muted(),true));frame.addView(address);
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle(current==null?"Добавить узел":"Изменить узел")
            .setView(frame).setNegativeButton("ОТМЕНА",null)
            .setPositiveButton("СОХРАНИТЬ",null).create();
        if(current!=null)dialog.setButton(AlertDialog.BUTTON_NEUTRAL,"УДАЛИТЬ",(d,w)->{
            TargetStore.remove(this,current);if(host!=null)host.setText(TargetStore.selected(this).name);
            if(PingService.snapshot().active)selectTarget(TargetStore.selected(this),true);
            else if(tab==0)refreshPing();
        });
        dialog.setOnShowListener(d->{dialog.getWindow().setBackgroundDrawable(Ui.shape(Ui.surface(this),Ui.dp(17),Ui.border()));
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
                String label=name.getText().toString().trim();String ip=normal(address.getText().toString());
                if(label.length()<1||label.length()>48){name.setError("Введите название до 48 символов");return;}
                if(!TargetStore.validHost(ip)){address.setError("Введите домен или IP без порта и пути");return;}
                boolean running=PingService.snapshot().active;
                TargetStore.save(this,current,label,ip);if(host!=null)host.setText(label);
                // Saved target immediately becomes the selected target.
                if(running)selectTarget(TargetStore.selected(this),true);
                else if(tab==0)refreshPing();dialog.dismiss();
            });
        });dialog.show();
    }
    private void showVpnOnEntry(){
        if(!VpnGuard.active(this)){vpnConsent=false;return;}
        if(isFinishing()||vpnDialogVisible||vpnConsent||PingService.snapshot().active)return;
        if(VpnGuard.active(this))vpnWarning(false);
    }
    private void vpnWarning(boolean startAfter){
        if(vpnDialogVisible)return;
        if(!VpnGuard.active(this)){vpnConsent=false;if(startAfter)beginPing();return;}
        vpnDialogVisible=true;
        Dialog dialog=new Dialog(this);
        dialog.setCancelable(false);dialog.setCanceledOnTouchOutside(false);
        LinearLayout frame=Ui.vertical(this);
        frame.setPadding(Ui.dp(22),Ui.dp(21),Ui.dp(22),Ui.dp(20));
        frame.setBackground(Ui.shape(Ui.surface(this),Ui.dp(22),0xFF4A3940));
        LinearLayout top=Ui.horizontal(this);
        ImageView shield=icon(R.drawable.ic_shield,QualityColors.YELLOW,Ui.dp(40));
        shield.setPadding(Ui.dp(10),Ui.dp(10),Ui.dp(10),Ui.dp(10));
        shield.setBackground(Ui.shape(0xFF302A20,Ui.dp(12),0xFF5C4930));
        top.addView(shield,Ui.margins(43,43,0,0));
        LinearLayout headline=Ui.vertical(this);headline.setPadding(Ui.dp(12),0,0,0);
        headline.addView(Ui.text(this,"Обнаружен VPN",19,Ui.fg(),true));
        headline.addView(Ui.text(this,"ПРОВЕРКА МАРШРУТА",10,QualityColors.YELLOW,true));
        top.addView(headline,new LinearLayout.LayoutParams(0,-2,1));frame.addView(top);
        addSpace(frame,18);
        frame.addView(Ui.text(this,"Для проверки настоящей задержки подключения отключи VPN перед запуском.",15,Ui.fg(),true));
        addSpace(frame,11);
        TextView details=Ui.text(this,"Если продолжить, измерения будут выполняться при активном VPN. Они не показывают задержку обычного маршрута без туннеля.",12,Ui.muted(),false);
        details.setLineSpacing(Ui.dp(4),1f);frame.addView(details);
        addSpace(frame,18);
        LinearLayout tip=Ui.horizontal(this);tip.setPadding(Ui.dp(12),Ui.dp(11),Ui.dp(12),Ui.dp(11));
        tip.setBackground(Ui.shape(Ui.surface2(this),Ui.dp(12),0));
        tip.addView(icon(R.drawable.ic_wifi,QualityColors.YELLOW,Ui.dp(22)),Ui.margins(24,24,0,0));
        TextView explanation=Ui.text(this,"Рекомендуется отключить VPN",12,QualityColors.YELLOW,true);
        explanation.setPadding(Ui.dp(9),0,0,0);tip.addView(explanation);
        frame.addView(tip);addSpace(frame,17);
        TextView settings=Ui.button(this,"ОТКРЫТЬ НАСТРОЙКИ VPN  ›",true);frame.addView(settings);
        addSpace(frame,9);
        TextView continueVpn=Ui.button(this,"ПРОДОЛЖИТЬ С VPN",false);frame.addView(continueVpn);
        settings.setOnClickListener(v->{vpnConsent=false;dialog.dismiss();
            try{startActivity(new Intent("android.settings.VPN_SETTINGS"));}
            catch(Exception e){toast("Открой настройки VPN на телефоне");}});
        continueVpn.setOnClickListener(v->{vpnConsent=true;dialog.dismiss();
            if(startAfter)beginPing();else refreshPing();});
        dialog.setOnDismissListener(d->vpnDialogVisible=false);
        dialog.setContentView(frame);dialog.show();
        Window w=dialog.getWindow();if(w!=null){
            w.setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
            w.addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);
            WindowManager.LayoutParams attr=w.getAttributes();attr.dimAmount=.68f;w.setAttributes(attr);
            w.setLayout(getResources().getDisplayMetrics().widthPixels-Ui.dp(35),-2);
        }
    }
    private void fullLogDialog(){
        if(journalDialog!=null&&journalDialog.isShowing())return;
        Dialog dialog=new Dialog(this);journalDialog=dialog;journalLast="";
        LinearLayout frame=Ui.vertical(this);
        frame.setPadding(Ui.dp(16),Ui.dp(15),Ui.dp(16),Ui.dp(14));
        frame.setBackground(Ui.shape(Ui.surface(this),Ui.dp(20),Ui.border()));
        LinearLayout top=Ui.horizontal(this);
        top.addView(icon(R.drawable.ic_log,AppPrefs.accent(this),Ui.dp(25)),Ui.margins(27,27,0,0));
        TextView heading=Ui.text(this,"Живой журнал",18,Ui.fg(),true);heading.setPadding(Ui.dp(10),0,0,0);
        top.addView(heading,new LinearLayout.LayoutParams(0,-2,1));
        TextView live=Ui.chip(this,"● LIVE",false);live.setTextColor(QualityColors.GREEN);top.addView(live);
        frame.addView(top,Ui.margins(-1,-2,0,13));
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);journalScroll=scroll;
        TextView text=Ui.mono(this,"",12,Ui.fg());text.setTextIsSelectable(true);
        text.setLineSpacing(Ui.dp(4),1f);text.setPadding(Ui.dp(8),Ui.dp(12),Ui.dp(8),Ui.dp(12));
        journalBody=text;scroll.addView(text);scroll.setBackground(Ui.shape(Ui.bg(this),Ui.dp(11),Ui.border()));
        frame.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        addSpace(frame,12);
        LinearLayout actions=Ui.horizontal(this);
        TextView copy=Ui.button(this,"КОПИРОВАТЬ",false);
        TextView close=Ui.button(this,"ЗАКРЫТЬ",true);
        actions.addView(copy,new LinearLayout.LayoutParams(0,Ui.dp(44),1));
        LinearLayout.LayoutParams after=new LinearLayout.LayoutParams(0,Ui.dp(44),1);after.leftMargin=Ui.dp(8);
        actions.addView(close,after);frame.addView(actions);
        copy.setOnClickListener(v->copy(String.join("\n",PingService.snapshot().log)));
        close.setOnClickListener(v->dialog.dismiss());
        dialog.setOnDismissListener(d->{handler.removeCallbacks(journalTick);
            journalDialog=null;journalBody=null;journalScroll=null;journalLast="";});
        dialog.setContentView(frame);dialog.show();
        Window w=dialog.getWindow();if(w!=null){w.setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
            w.setLayout(getResources().getDisplayMetrics().widthPixels-Ui.dp(24),
                (int)(getResources().getDisplayMetrics().heightPixels*.77f));}
        refreshJournal();handler.removeCallbacks(journalTick);handler.postDelayed(journalTick,140);
    }
    private void refreshJournal(){
        if(journalBody==null||journalScroll==null)return;
        String text=String.join("\n",PingService.snapshot().log);
        if(text.isEmpty())text="События появятся после запуска проверки";
        if(text.equals(journalLast))return;
        boolean pinned=journalScroll.getScrollY()+journalScroll.getHeight()>=journalBody.getHeight()-Ui.dp(36);
        journalLast=text;journalBody.setText(coloredLog(text));
        if(pinned)journalScroll.post(()->{if(journalScroll!=null)journalScroll.fullScroll(View.FOCUS_DOWN);});
    }
    private static final Pattern RTT_VALUE=Pattern.compile("([0-9]+(?:[.,][0-9]+)?)\\s*мс");
    private CharSequence coloredLog(String text){
        SpannableStringBuilder result=new SpannableStringBuilder(text);
        int cursor=0;
        for(String line:text.split("\n",-1)){
            int end=cursor+line.length();String lower=line.toLowerCase(Locale.ROOT);
            int color;
            if(lower.contains("нет ответа")||lower.contains("ошибка")||lower.contains("недоступ")||lower.contains("запрещ")||lower.contains("потер"))color=QualityColors.RED;
            else if(lower.contains("vpn")||lower.contains("пропуск")||lower.contains("тайм"))color=QualityColors.YELLOW;
            else if(line.startsWith("#")||lower.contains("завершено"))color=QualityColors.GREEN;
            else color=Ui.muted();
            if(end>cursor)result.setSpan(new ForegroundColorSpan(color),cursor,end,Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            Matcher matcher=RTT_VALUE.matcher(line);
            while(matcher.find())try{
                double ms=Double.parseDouble(matcher.group(1).replace(',','.'));
                result.setSpan(new ForegroundColorSpan(QualityColors.rtt(ms)),cursor+matcher.start(1),cursor+matcher.end(),Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            }catch(NumberFormatException ignored){}
            cursor=end+1;
        }
        return result;
    }
    // HISTORY
    private void historyPage(){
        LinearLayout row=Ui.horizontal(this);row.addView(Ui.text(this,"История проверок",21,Ui.fg(),true),new LinearLayout.LayoutParams(0,-2,1));
        TextView clear=Ui.chip(this,"Очистить",false);row.addView(clear);page.addView(row,Ui.margins(-1,-2,0,12));
        clear.setOnClickListener(v->new AlertDialog.Builder(this).setTitle("Очистить всю историю?")
            .setNegativeButton("Отмена",null).setPositiveButton("Очистить",(d,n)->{HistoryStore.clear(this);showTab(1);}).show());
        JSONArray data=HistoryStore.all(this);if(data.length()==0){LinearLayout empty=Ui.panel(this);empty.addView(Ui.text(this,"Нет сохранённых проверок",16,Ui.fg(),true));
            empty.addView(Ui.text(this,"Запустите мониторинг, и история появится здесь.",12,Ui.muted(),false));page.addView(empty);return;}
        for(int i=0;i<data.length();i++){JSONObject o=data.optJSONObject(i);if(o==null)continue;
            LinearLayout card=Ui.panel(this);LinearLayout r=Ui.horizontal(this);
            r.addView(Ui.text(this,o.optString("label",TargetStore.friendly(this,o.optString("host","—"))),17,Ui.fg(),true),new LinearLayout.LayoutParams(0,-2,1));
            boolean good=o.optInt("ok")>0;TextView m=Ui.text(this,good?fmt(o.optDouble("avg"))+" мс":"НЕТ ОТВЕТА",12,
                good?QualityColors.rtt(o.optDouble("avg")):QualityColors.RED,true);r.addView(m);
            card.addView(r);
            int sent=o.optInt("sent");int lost=o.optInt("lost");
            double percent=sent==0?0:100.0*lost/sent;
            TextView lossLabel=Ui.text(this,"Потери "+fmt(percent)+"%"+
                (o.optString("vpnInfo").contains("включён")?"  ·  с VPN":"  ·  без VPN"),11,
                sent==0?QualityColors.UNKNOWN:QualityColors.loss(percent),false);
            card.addView(lossLabel,Ui.margins(-1,-2,0,5));
            card.addView(Ui.text(this,date(o.optLong("time"))+"   ·   "+o.optInt("ok")+" / "+sent,11,Ui.muted(),false));
            card.setOnClickListener(v->historyDetails(o));card.setOnLongClickListener(v->{new AlertDialog.Builder(this).setTitle("Удалить сеанс?")
                .setNegativeButton("Отмена",null).setPositiveButton("Удалить",(d,w)->{HistoryStore.remove(this,o.optLong("id"));showTab(1);}).show();return true;});
            page.addView(card,Ui.margins(-1,-2,0,9));
        }
    }
    private void historyDetails(JSONObject obj){
        int sent=obj.optInt("sent"),bad=obj.optInt("lost");String method=obj.optString("method","ICMP");
        String out=obj.optString("label",TargetStore.friendly(this,obj.optString("host")))+"\n"+date(obj.optLong("time"))+"\n"+
          "Сеть: "+(obj.optString("vpnInfo").contains("включён")?"с VPN":"без VPN")+"\n"+
          "Отправлено: "+sent+"\nОтветов: "+obj.optInt("ok")+"\n"+
          (method.startsWith("TCP")?"Сбои: ":"Потери: ")+bad+" ("+fmt(sent==0?0:100.0*bad/sent)+"%)\n"+
          "Пропущено: "+obj.optInt("skipped")+"\nMIN / AVG / MAX: "+fmt(obj.optDouble("min"))+" / "+fmt(obj.optDouble("avg"))+" / "+fmt(obj.optDouble("max"))+" мс\n"+
          "Jitter: "+fmt(obj.optDouble("jitter"))+" мс\n"+obj.optString("warning")+"\n"+obj.optString("error")+"\n\n"+obj.optString("log");
        ScrollView view=new ScrollView(this);view.setPadding(Ui.dp(16),Ui.dp(15),Ui.dp(16),Ui.dp(8));
        TextView body=Ui.mono(this,out,12,Ui.fg());body.setTextIsSelectable(true);view.addView(body);
        new AlertDialog.Builder(this).setTitle("Отчёт • "+obj.optString("label",TargetStore.friendly(this,obj.optString("host"))))
            .setView(view).setNeutralButton("Копировать",(d,w)->copy(out))
            .setPositiveButton("Поделиться",(d,w)->share(out)).setNegativeButton("Закрыть",null).show();
    }
    private String date(long time){return new SimpleDateFormat("dd.MM.yyyy  HH:mm:ss",Locale.getDefault()).format(new Date(time));}
    // SETTINGS
    private void settingsPage(){page.addView(Ui.text(this,"Настройки",23,Ui.fg(),true),Ui.margins(-1,-2,0,15));
        group("ИЗМЕРЕНИЯ","Интервал, тайм-ауты и размер пакета",this::networkSettings);
        group("УВЕДОМЛЕНИЯ","Прогресс и график",this::notificationSettings);
        group("ИСТОРИЯ","Сохранение и буфер обмена",this::generalSettings);
        group("ВНЕШНИЙ ВИД","Темы, анимация и акцент",this::appearanceSettings);
        group("ОБНОВЛЕНИЯ","Официальный OTA-канал GitHub",this::otaSettings);
        group("О ПРИЛОЖЕНИИ","Версия, возможности и ограничения",this::about);
    }
    private interface Section{void fill(LinearLayout parent);}
    private void group(String title,String subtitle,Section factory){
        LinearLayout card=Ui.panel(this);card.setPadding(Ui.dp(14),Ui.dp(12),Ui.dp(14),Ui.dp(12));
        LinearLayout top=Ui.horizontal(this);LinearLayout txt=Ui.vertical(this);
        int glyph=title.equals("ИЗМЕРЕНИЯ")?R.drawable.ic_wifi:
            title.equals("УВЕДОМЛЕНИЯ")?R.drawable.ic_shield:
            title.equals("ИСТОРИЯ")?R.drawable.ic_history:
            title.equals("ВНЕШНИЙ ВИД")?R.drawable.ic_settings:R.drawable.ic_server;
        top.addView(icon(glyph,AppPrefs.accent(this),Ui.dp(23)),Ui.margins(25,25,0,0));
        txt.setPadding(Ui.dp(11),0,0,0);
        txt.addView(Ui.text(this,title,14,Ui.fg(),true));txt.addView(Ui.text(this,subtitle,11,Ui.muted(),false));
        top.addView(txt,new LinearLayout.LayoutParams(0,-2,1));TextView arrow=Ui.text(this,"⌄",20,AppPrefs.accent(this),true);top.addView(arrow);
        card.addView(top);LinearLayout extra=Ui.vertical(this);
        boolean expanded=openSections.contains(title);
        if(expanded){addSpace(extra,14);factory.fill(extra);extra.setVisibility(View.VISIBLE);arrow.setText("⌃");}
        else extra.setVisibility(View.GONE);
        card.addView(extra);
        top.setOnClickListener(v->{boolean open=extra.getVisibility()==View.GONE;
            if(open&&extra.getChildCount()==0){addSpace(extra,14);factory.fill(extra);}
            extra.setVisibility(open?View.VISIBLE:View.GONE);arrow.setText(open?"⌃":"⌄");
            if(open)openSections.add(title);else openSections.remove(title);
        });page.addView(card,Ui.margins(-1,-2,0,9));
    }
    private void networkSettings(LinearLayout root){
        selectRow(root,"Запросов","count",new int[]{0,10,30,100,500},new String[]{"∞","10","30","100","500"});
        selectRow(root,"Интервал","interval",new int[]{100,200,300,500,1000,2000},new String[]{"0.1","0.2","0.3","0.5","1","2"});
        selectRow(root,"Тайм-аут","timeout",new int[]{1,2,3,4,5,8},new String[]{"1","2","3","4","5","8"});
        number(root,"Размер пакета (байт)","size",64,0,65000);
        number(root,"TTL","ttl",64,1,255);
        TextView note=Ui.text(this,"При активном VPN приложение предупредит о проверке через туннель. Отказ от VPN необходим для измерения обычного маршрута.",12,Ui.muted(),false);
        root.addView(note,Ui.margins(-1,-2,0,12));
        TextView reset=Ui.button(this,"СБРОС ПАРАМЕТРОВ",false);root.addView(reset);reset.setOnClickListener(v->{
            AppPrefs.put(this,"count",0);AppPrefs.put(this,"interval",200);AppPrefs.put(this,"timeout",3);
            AppPrefs.put(this,"size",64);AppPrefs.put(this,"ttl",64);showTab(2);toast("Параметры восстановлены");});
    }
    private void notificationSettings(LinearLayout p){
        toggleRow(p,"Подробности","Показывать статистику в уведомлении","notify_details",true);
        toggleRow(p,"Прогресс","Индикатор для конечных проверок","notify_progress",true);
        toggleRow(p,"Отдельный график","Обновление раз в 5 секунд","notify_chart",false);
        toggleRow(p,"Краткое уведомление","Скрыть дополнительные сведения","notifications",true);
        p.addView(Ui.text(this,"Служебное уведомление Android обязательно, пока мониторинг работает в фоне.",11,Ui.muted(),false));
    }
    private void generalSettings(LinearLayout p){
        toggleRow(p,"Хранить историю","До 200 сеансов, включая события","history",true);
        
        TextView clear=Ui.button(this,"ОЧИСТИТЬ ИСТОРИЮ",false);p.addView(clear);
        clear.setOnClickListener(v->new AlertDialog.Builder(this).setTitle("Удалить историю?")
           .setPositiveButton("Удалить",(d,w)->{HistoryStore.clear(this);toast("История очищена");}).setNegativeButton("Отмена",null).show());
    }
    private void appearanceSettings(LinearLayout p){
        toggleRow(p,"AMOLED","Абсолютно чёрный фон","amoled",true);
        toggleRow(p,"Плавное движение","Анимация значений, графика и нажатий","motion",true);
        p.addView(label("ЦВЕТ АКЦЕНТА"),Ui.margins(-1,-2,0,8));
        int[] colors={0xff55dfcb,0xff43baf5,0xff658aff,0xffac8dff,0xffdb91ff,0xffff77ce,
            0xffff7085,0xffff936d,0xffffba63,0xffffd45a,0xffd0e46d,0xff90df79,
            0xff57cda3,0xff4ad5de,0xff35a6de,0xff8773e4,0xffba6ef6,0xffed77a3,
            0xffe75f5f,0xffd39c78,0xffa3bbc8,0xffe8edf5,0xff76a4ab,0xff9a86ab};
        String[] names={"Мята","Лазурь","Сапфир","Лаванда","Сирень","Фуксия","Коралл","Персик","Янтарь","Лимон","Лайм","Весна","Изумруд","Бирюза","Океан","Ирис","Аметист","Пион","Рубин","Бронза","Сталь","Лёд","Шалфей","Слива"};
        for(int r=0;r<6;r++){LinearLayout line=Ui.horizontal(this);
            for(int c=0;c<4;c++){int i=r*4+c,color=colors[i];boolean chosen=AppPrefs.accent(this)==color;
                LinearLayout col=Ui.vertical(this);col.setGravity(Gravity.CENTER);col.setPadding(Ui.dp(2),Ui.dp(8),Ui.dp(2),Ui.dp(8));
                TextView dot=Ui.text(this,chosen?"◉":"●",22,color,true);dot.setGravity(Gravity.CENTER);col.addView(dot);
                TextView name=Ui.text(this,names[i],9,chosen?Ui.fg():Ui.muted(),chosen);name.setGravity(Gravity.CENTER);col.addView(name);
                if(chosen)col.setBackground(Ui.shape(Ui.surface2(this),Ui.dp(11),color));
                line.addView(col,new LinearLayout.LayoutParams(0,-2,1));col.setOnClickListener(v->{AppPrefs.put(this,"accent",color);redrawSettings();});
            }p.addView(line,Ui.margins(-1,-2,0,3));}
    }
    private void otaSettings(LinearLayout p){
        p.addView(Ui.text(this,"PING TEST проверяет обновления только в официальном репозитории INFEND/PING-TEST.",12,Ui.muted(),false));
        TextView check=Ui.button(this,"ПРОВЕРИТЬ ОБНОВЛЕНИЯ",true);p.addView(check,Ui.margins(-1,-2,0,10));
        check.setOnClickListener(v->UpdateManager.check(this));
        OtaOptions.attach(this,p,this::redrawSettings);
    }
    private void about(LinearLayout p){
        p.addView(Ui.text(this,"PING TEST · 1.5.1",17,Ui.fg(),true));
        p.addView(Ui.text(this,"Java 17 · Code on the Go · Android "+Build.VERSION.RELEASE,12,Ui.muted(),false));
        p.addView(Ui.text(this,"Проверка измеряет ответы выбранного узла. При активном VPN результаты относятся к маршруту через VPN. Некоторые сайты и серверы не отвечают на ping: отсутствие ICMP-ответа не означает, что игра или сайт недоступны.",12,Ui.muted(),false),Ui.margins(-1,-2,9,0));
    }
    private void redrawSettings(){int scroll=scroller==null?0:scroller.getScrollY();
        noEntrance=true;try{showTab(2);}finally{noEntrance=false;}
        if(scroller!=null)scroller.post(()->scroller.scrollTo(0,scroll));
    }
    private void selectRow(LinearLayout p,String title,String key,String[] names){int[] values=new int[names.length];for(int i=0;i<values.length;i++)values[i]=i;selectRow(p,title,key,values,names);}
    private void selectRow(LinearLayout p,String title,String key,int[] values,String[] names){
        p.addView(Ui.text(this,title,13,Ui.fg(),true),Ui.margins(-1,-2,0,6));
        HorizontalScrollView sv=new HorizontalScrollView(this);sv.setHorizontalScrollBarEnabled(false);
        LinearLayout row=Ui.horizontal(this);int selected=AppPrefs.number(this,key,values[0]);
        for(int i=0;i<values.length;i++){final int n=i;TextView chip=Ui.chip(this,names[i],selected==values[i]);chip.setTextSize(11);
            LinearLayout.LayoutParams mp=Ui.margins(-2,-2,0,0);mp.rightMargin=Ui.dp(6);row.addView(chip,mp);
            chip.setOnClickListener(v->{AppPrefs.put(this,key,values[n]);
                for(int z=0;z<row.getChildCount();z++){TextView t=(TextView)row.getChildAt(z);boolean checked=z==n;
                    t.setBackground(Ui.shape(checked?AppPrefs.accent(this):Ui.surface2(this),Ui.dp(10),checked?0:Ui.border()));
                    t.setTextColor(checked?0xFF061216:Ui.muted());}
            });
        }sv.addView(row);p.addView(sv,Ui.margins(-1,-2,0,15));
    }
    private void number(LinearLayout p,String title,String key,int def,int min,int max){
        LinearLayout row=Ui.horizontal(this);TextView label=Ui.text(this,title,13,Ui.fg(),false);
        row.addView(label,new LinearLayout.LayoutParams(0,-2,1));
        EditText value=new EditText(this);value.setSingleLine(true);value.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
        value.setTextColor(Ui.fg());value.setTextSize(14);value.setGravity(Gravity.CENTER);value.setText(""+AppPrefs.number(this,key,def));
        value.setBackground(Ui.shape(Ui.surface2(this),Ui.dp(10),Ui.border()));value.setPadding(Ui.dp(6),Ui.dp(9),Ui.dp(6),Ui.dp(9));
        value.addTextChangedListener(new TextWatcher(){public void beforeTextChanged(CharSequence s,int start,int count,int after){}
            public void onTextChanged(CharSequence s,int start,int before,int count){try{int n=Integer.parseInt(s.toString());if(n>=min&&n<=max)AppPrefs.put(MainActivity.this,key,n);}catch(Exception ignored){}}
            public void afterTextChanged(Editable e){} });
        row.addView(value,Ui.margins(95,-2,0,0));p.addView(row,Ui.margins(-1,-2,0,13));
    }
    private void toggleRow(LinearLayout p,String title,String subtitle,String key,boolean def){
        LinearLayout row=Ui.horizontal(this);LinearLayout txt=Ui.vertical(this);
        txt.addView(Ui.text(this,title,13,Ui.fg(),true));txt.addView(Ui.text(this,subtitle,11,Ui.muted(),false));
        row.addView(txt,new LinearLayout.LayoutParams(0,-2,1));Switch sw=new Switch(this);sw.setChecked(AppPrefs.bool(this,key,def));
        sw.setThumbTintList(new ColorStateList(new int[][]{new int[]{android.R.attr.state_checked},new int[]{}},new int[]{AppPrefs.accent(this),0xFF9BA8B1}));
        sw.setTrackTintList(new ColorStateList(new int[][]{new int[]{android.R.attr.state_checked},new int[]{}},new int[]{0xFF3C746F,0xFF393D49}));
        row.addView(sw);sw.setOnCheckedChangeListener((v,checked)->{AppPrefs.put(this,key,checked);if(key.equals("amoled"))redrawSettings();});
        row.setOnClickListener(v->sw.setChecked(!sw.isChecked()));p.addView(row,Ui.margins(-1,-2,0,13));
    }
    // Smooth numeric *and color* interpolation, preserving green/yellow/red quality bands.
    private final class Metric extends TextView {
        private ValueAnimator motion;
        private double shown=Double.NaN,target=Double.NaN;
        private final int kind; // 0: RTT, 1: loss percentage.
        Metric(String value,int size,int color,int kind){super(MainActivity.this);this.kind=kind;
            setText(value);setTextColor(color);setTextSize(size);
            setIncludeFontPadding(false);setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));setSingleLine(true);}
        private int quality(double v){return kind==1?QualityColors.loss(v):QualityColors.rtt(v);}
        void update(double next,boolean percent,boolean animate){
            if(Double.compare(target,next)==0)return;
            if(motion!=null)motion.cancel();target=next;
            if(next<0||Double.isNaN(next)){shown=next;setText("—");setTextColor(QualityColors.UNKNOWN);return;}
            if(!animate||!AppPrefs.bool(MainActivity.this,"motion",true)||Double.isNaN(shown)||shown<0){
                shown=next;setText(fmt(next)+(percent?" %":""));setTextColor(quality(next));return;
            }
            double first=shown;ValueAnimator a=ValueAnimator.ofFloat(0f,1f);motion=a;a.setDuration(195);
            a.setInterpolator(new DecelerateInterpolator(1.2f));
            a.addUpdateListener(v->{shown=first+(next-first)*(Float)v.getAnimatedValue();
                setText(fmt(shown)+(percent?" %":""));setTextColor(quality(shown));});
            a.start();
        }
    }
    private void checkClipboard(){/* Узел выбирается только пользователем из каталога. */}
    private void hideKeyboard(){try{InputMethodManager mgr=(InputMethodManager)getSystemService(INPUT_METHOD_SERVICE);
        if(host!=null){mgr.hideSoftInputFromWindow(host.getWindowToken(),0);host.clearFocus();}}catch(Exception ignored){}}
    private void message(String title,String body){new AlertDialog.Builder(this).setTitle(title).setMessage(body).setPositiveButton("Закрыть",null).show();}
    private void copy(String text){android.content.ClipboardManager clip=(android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE);
        if(clip!=null)clip.setPrimaryClip(ClipData.newPlainText("PING TEST",text));toast("Скопировано");}
    private void share(String text){Intent i=new Intent(Intent.ACTION_SEND);i.setType("text/plain");i.putExtra(Intent.EXTRA_TEXT,text);
        startActivity(Intent.createChooser(i,"Поделиться отчётом"));}
    private void toast(String value){Toast.makeText(this,value,Toast.LENGTH_SHORT).show();}
}
