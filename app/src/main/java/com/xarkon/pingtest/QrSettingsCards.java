package com.xarkon.pingtest;

import android.Manifest;
import android.animation.*;
import android.app.Activity;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.os.Build;
import android.view.*;
import android.view.animation.DecelerateInterpolator;
import android.widget.*;
import java.util.Set;
import java.util.function.Consumer;

/** QR LINK settings component port: animated sections, themes, 24 named accents, and OTA scheduler. */
public final class QrSettingsCards {
    private QrSettingsCards(){}
    private static final int[] ACCENTS={
        0xff55dfcb,0xff43baf5,0xff658aff,0xffac8dff,0xffdb91ff,0xffff77ce,
        0xffff7085,0xffff936d,0xffffba63,0xffffd45a,0xffd0e46d,0xff90df79,
        0xff57cda3,0xff4ad5de,0xff35a6de,0xff8773e4,0xffba6ef6,0xffed77a3,
        0xffe75f5f,0xffd39c78,0xffa3bbc8,0xffe8edf5,0xff76a4ab,0xff9a86ab
    };
    private static final String[] NAMES={
        "Мята","Лазурь","Сапфир","Лаванда","Сирень","Фуксия",
        "Коралл","Персик","Янтарь","Лимон","Лайм","Весна",
        "Изумруд","Бирюза","Океан","Ирис","Аметист","Пион",
        "Рубин","Бронза","Сталь","Лёд","Шалфей","Слива"
    };
    private static LinearLayout.LayoutParams margin(int bottom){
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.bottomMargin=Ui.dp(bottom);return lp;
    }
    private static TextView text(Activity a,String value,int size,int color,boolean bold){
        return Ui.text(a,value,size,color,bold);
    }
    private static UiIcon symbol(Activity a,String id,int size,int color){
        UiIcon glyph=new UiIcon(a,id,color);glyph.setContentDescription(id);
        return glyph;
    }
    private static void spacer(LinearLayout p,int dp){p.addView(new View(p.getContext()),new LinearLayout.LayoutParams(1,Ui.dp(dp)));}
    private static void feedback(Activity a,View v){
        if(AppPrefs.bool(a,"haptics",true))v.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);
    }
    private static android.graphics.drawable.Drawable ripple(Activity a,int background,int line,int radius){
        return new android.graphics.drawable.RippleDrawable(
          ColorStateList.valueOf((AppPrefs.accent(a)&0x00ffffff)|0x32000000),
          Ui.shape(background,Ui.dp(radius),line),Ui.shape(0xffffffff,Ui.dp(radius),0));
    }
    /** Animate the entire section body, exactly as in QR LINK's collapsible settings. */
    public static void section(Activity a,LinearLayout parent,Set<String> expanded,
          String key,String title,String detail,String glyph,Consumer<LinearLayout> builder){
        LinearLayout shell=Ui.vertical(a);shell.setBackground(Ui.shape(Ui.surface(a),Ui.dp(22),Ui.border()));
        shell.setClipChildren(true);shell.setClipToPadding(true);
        LinearLayout.LayoutParams card=margin(13);parent.addView(shell,card);
        LinearLayout head=Ui.horizontal(a);head.setMinimumHeight(Ui.dp(82));
        head.setPadding(Ui.dp(16),Ui.dp(15),Ui.dp(15),Ui.dp(15));
        head.addView(symbol(a,glyph,29,AppPrefs.accent(a)),new LinearLayout.LayoutParams(Ui.dp(29),Ui.dp(29)));
        LinearLayout titles=Ui.vertical(a);titles.setPadding(Ui.dp(13),0,Ui.dp(8),0);
        titles.addView(text(a,title,17,Ui.fg(),true));spacer(titles,5);
        titles.addView(text(a,detail,12,Ui.muted(),false));
        head.addView(titles,new LinearLayout.LayoutParams(0,-2,1));
        UiIcon chevron=symbol(a,"chevron",22,Ui.muted());
        head.addView(chevron,new LinearLayout.LayoutParams(Ui.dp(22),Ui.dp(22)));
        head.setBackground(ripple(a,0x00000000,0,22));head.setClickable(true);
        shell.addView(head);
        View divider=new View(a);divider.setBackgroundColor(Ui.border());
        LinearLayout.LayoutParams line=new LinearLayout.LayoutParams(-1,Ui.dp(1));
        line.setMargins(Ui.dp(16),0,Ui.dp(16),0);
        shell.addView(divider,line);
        LinearLayout body=Ui.vertical(a);body.setPadding(Ui.dp(16),Ui.dp(17),Ui.dp(16),Ui.dp(9));
        body.setClipChildren(true);body.setClipToPadding(true);shell.addView(body);
        final boolean[] opened={expanded.contains(key)};
        final boolean[] filled={false};
        if(opened[0]){builder.accept(body);filled[0]=true;}
        body.setVisibility(opened[0]?View.VISIBLE:View.GONE);
        divider.setVisibility(opened[0]?View.VISIBLE:View.GONE);
        chevron.setRotation(opened[0]?180:0);
        final int[] revision={0};
        final ValueAnimator[] animation={null};
        head.setContentDescription(title+". "+(opened[0]?"Свернуть":"Развернуть"));
        head.setOnClickListener(v->{
            feedback(a,v);
            boolean opening=!opened[0];opened[0]=opening;
            if(opening)expanded.add(key);else expanded.remove(key);
            head.setContentDescription(title+". "+(opening?"Свернуть":"Развернуть"));
            if(opening&&!filled[0]){builder.accept(body);filled[0]=true;}
            final int id=++revision[0];
            if(animation[0]!=null){animation[0].cancel();animation[0]=null;}
            chevron.animate().cancel();
            if(!AppPrefs.bool(a,"motion",true)){
                LinearLayout.LayoutParams lp=(LinearLayout.LayoutParams)body.getLayoutParams();
                lp.height=ViewGroup.LayoutParams.WRAP_CONTENT;body.setLayoutParams(lp);
                body.setVisibility(opening?View.VISIBLE:View.GONE);
                divider.setVisibility(opening?View.VISIBLE:View.GONE);
                body.setAlpha(1f);chevron.setRotation(opening?180f:0f);return;
            }
            int initial=Math.max(0,body.getHeight()),goal=0;
            if(opening){
                LinearLayout.LayoutParams lp=(LinearLayout.LayoutParams)body.getLayoutParams();
                lp.height=ViewGroup.LayoutParams.WRAP_CONTENT;body.setLayoutParams(lp);
                body.setVisibility(View.VISIBLE);
                int available=Math.max(1,shell.getWidth()-shell.getPaddingLeft()-shell.getPaddingRight());
                body.measure(View.MeasureSpec.makeMeasureSpec(available,View.MeasureSpec.EXACTLY),
                    View.MeasureSpec.makeMeasureSpec(0,View.MeasureSpec.UNSPECIFIED));
                goal=Math.max(1,body.getMeasuredHeight());divider.setVisibility(View.VISIBLE);
            }
            ValueAnimator animator=ValueAnimator.ofInt(initial,goal);animation[0]=animator;
            animator.setDuration(opening?245:210);
            animator.setInterpolator(new DecelerateInterpolator(1.4f));
            animator.addUpdateListener(t->{
                if(id!=revision[0])return;
                LinearLayout.LayoutParams lp=(LinearLayout.LayoutParams)body.getLayoutParams();
                lp.height=(Integer)t.getAnimatedValue();body.setLayoutParams(lp);
                float fraction=t.getAnimatedFraction();body.setAlpha(opening?fraction:1f-fraction);
            });
            animator.addListener(new AnimatorListenerAdapter(){
                @Override public void onAnimationEnd(Animator t){
                    if(id!=revision[0])return;
                    animation[0]=null;
                    LinearLayout.LayoutParams lp=(LinearLayout.LayoutParams)body.getLayoutParams();
                    lp.height=ViewGroup.LayoutParams.WRAP_CONTENT;body.setLayoutParams(lp);
                    body.setAlpha(1f);body.setVisibility(opening?View.VISIBLE:View.GONE);
                    divider.setVisibility(opening?View.VISIBLE:View.GONE);
                }
            });
            chevron.animate().rotation(opening?180f:0f).setDuration(opening?220:190)
                .setInterpolator(new DecelerateInterpolator()).start();
            animator.start();
        });
    }
    private static void toggle(Activity a,LinearLayout body,String icon,String title,String detail,
           boolean current,Consumer<Boolean> action){
        LinearLayout line=Ui.horizontal(a);line.setPadding(Ui.dp(7),Ui.dp(10),Ui.dp(5),Ui.dp(10));
        line.addView(symbol(a,icon,24,AppPrefs.accent(a)),new LinearLayout.LayoutParams(Ui.dp(24),Ui.dp(24)));
        LinearLayout labels=Ui.vertical(a);labels.setPadding(Ui.dp(12),0,Ui.dp(8),0);
        labels.addView(text(a,title,14,Ui.fg(),true));spacer(labels,5);
        labels.addView(text(a,detail,12,Ui.muted(),false));
        line.addView(labels,new LinearLayout.LayoutParams(0,-2,1));
        Switch sw=new Switch(a);sw.setChecked(current);
        sw.setThumbTintList(new ColorStateList(
            new int[][]{new int[]{android.R.attr.state_checked},new int[]{}},
            new int[]{AppPrefs.accent(a),Ui.muted()}));
        line.addView(sw);body.addView(line,margin(5));
        sw.setOnCheckedChangeListener((b,on)->action.accept(on));
        line.setOnClickListener(v->{feedback(a,v);sw.setChecked(!sw.isChecked());});
    }
    public static void appearance(Activity a,LinearLayout p,Runnable refresh){
        p.addView(text(a,"ТЕМА ИНТЕРФЕЙСА",11,Ui.muted(),true),margin(13));
        LinearLayout themes=Ui.horizontal(a);p.addView(themes,margin(19));
        String[] ids={"dark","amoled","light"};
        String[] names={"Тёмная","AMOLED","Светлая"};
        String[] icons={"moon","amoled","sun"};
        for(int i=0;i<3;i++){
            final String id=ids[i];boolean selected=id.equals(AppPrefs.mode(a));
            LinearLayout tile=Ui.vertical(a);tile.setGravity(Gravity.CENTER);
            tile.setPadding(Ui.dp(5),Ui.dp(13),Ui.dp(5),Ui.dp(12));
            tile.setMinimumHeight(Ui.dp(87));
            tile.setBackground(ripple(a,selected?Ui.soft(a):Ui.surface2(a),selected?AppPrefs.accent(a):Ui.border(),16));
            tile.addView(symbol(a,icons[i],28,selected?AppPrefs.accent(a):Ui.muted()),new LinearLayout.LayoutParams(Ui.dp(28),Ui.dp(28)));
            spacer(tile,8);
            TextView name=text(a,names[i],12,selected?AppPrefs.accent(a):Ui.fg(),selected);name.setGravity(Gravity.CENTER);tile.addView(name);
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-2,1);
            lp.setMargins(Ui.dp(3),0,Ui.dp(3),0);themes.addView(tile,lp);
            tile.setContentDescription("Тема: "+names[i]+(selected?", выбрана":""));
            tile.setOnClickListener(v->{feedback(a,v);
                if(!id.equals(AppPrefs.mode(a))){AppPrefs.setMode(a,id);refresh.run();}
            });Ui.motion(a,tile);
        }
        p.addView(text(a,"АКЦЕНТНЫЙ ЦВЕТ",11,Ui.muted(),true),margin(12));
        LinearLayout indicator=Ui.horizontal(a);indicator.setPadding(Ui.dp(9),Ui.dp(9),Ui.dp(10),Ui.dp(9));
        indicator.setBackground(Ui.shape(Ui.soft(a),Ui.dp(13),Ui.border()));p.addView(indicator,margin(14));
        View dot=new View(a);dot.setBackground(Ui.shape(AppPrefs.accent(a),Ui.dp(10),0));
        indicator.addView(dot,new LinearLayout.LayoutParams(Ui.dp(21),Ui.dp(21)));
        int index=0;for(int i=0;i<ACCENTS.length;i++)if(AppPrefs.accent(a)==ACCENTS[i])index=i;
        indicator.addView(text(a,"   Выбран: ",12,Ui.fg(),true));
        indicator.addView(text(a,NAMES[index],13,AppPrefs.accent(a),true));
        for(int start=0;start<ACCENTS.length;start+=4){
            LinearLayout line=Ui.horizontal(a);p.addView(line,margin(9));
            for(int n=start;n<start+4;n++){
                int at=n;boolean selected=AppPrefs.accent(a)==ACCENTS[n];
                LinearLayout tile=Ui.vertical(a);tile.setGravity(Gravity.CENTER);
                tile.setPadding(Ui.dp(3),Ui.dp(11),Ui.dp(3),Ui.dp(9));
                tile.setBackground(ripple(a,selected?Ui.soft(a):Ui.surface(a),selected?AppPrefs.accent(a):Ui.border(),13));
                FrameLayout swatch=new FrameLayout(a);
                swatch.setBackground(Ui.shape(ACCENTS[n],Ui.dp(25),0));
                if(selected){
                    UiIcon check=symbol(a,"check",21,Ui.onAccent(a));
                    swatch.addView(check,new FrameLayout.LayoutParams(Ui.dp(26),Ui.dp(26),Gravity.CENTER));
                }
                LinearLayout.LayoutParams sw=new LinearLayout.LayoutParams(Ui.dp(29),Ui.dp(29));sw.gravity=Gravity.CENTER;
                tile.addView(swatch,sw);spacer(tile,8);
                TextView caption=text(a,NAMES[n],11,Ui.fg(),selected);caption.setGravity(Gravity.CENTER);
                caption.setSingleLine(true);caption.setEllipsize(android.text.TextUtils.TruncateAt.END);
                tile.addView(caption,new LinearLayout.LayoutParams(-1,-2));
                LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,Ui.dp(79),1);
                lp.setMargins(Ui.dp(3),0,Ui.dp(3),0);line.addView(tile,lp);
                tile.setContentDescription("Акцент: "+NAMES[n]+(selected?", выбран":""));
                tile.setOnClickListener(v->{feedback(a,v);if(AppPrefs.accent(a)!=ACCENTS[at]){
                    AppPrefs.put(a,"accent",ACCENTS[at]);refresh.run();
                }});Ui.motion(a,tile);
            }
        }
        toggle(a,p,"sparkles","Плавные анимации",
            "Быстрые переходы и мягкое обновление чисел",
            AppPrefs.bool(a,"motion",true),on->AppPrefs.put(a,"motion",on));
        toggle(a,p,"flash","Тактильный отклик",
            "Короткая вибрация при нажатии",
            AppPrefs.bool(a,"haptics",true),on->AppPrefs.put(a,"haptics",on));
    }
    private static void enableTree(View view,boolean enabled){
        view.setEnabled(enabled);
        if(view instanceof ViewGroup){
            ViewGroup v=(ViewGroup)view;
            for(int i=0;i<v.getChildCount();i++)enableTree(v.getChildAt(i),enabled);
        }
    }
    public static void updates(Activity a,LinearLayout p,Runnable check){
        LinearLayout button=Ui.horizontal(a);button.setGravity(Gravity.CENTER);
        button.setPadding(Ui.dp(17),Ui.dp(15),Ui.dp(17),Ui.dp(15));
        int accent=AppPrefs.accent(a);button.setBackground(ripple(a,Ui.surface2(a),Ui.border(),16));
        button.addView(symbol(a,"check",24,accent),new LinearLayout.LayoutParams(Ui.dp(24),Ui.dp(24)));
        TextView title=text(a,"  ПРОВЕРИТЬ ОБНОВЛЕНИЕ",14,Ui.fg(),true);button.addView(title);
        p.addView(button,margin(12));button.setOnClickListener(v->{feedback(a,v);check.run();});Ui.motion(a,button);
        SharedPreferences prefs=AppPrefs.of(a);
        toggle(a,p,"check","Проверка обновлений при запуске","При открытии PING TEST",
            prefs.getBoolean(OtaUpdateSchedule.PREF_ON_LAUNCH,true),
            value->prefs.edit().putBoolean(OtaUpdateSchedule.PREF_ON_LAUNCH,value).apply());
        LinearLayout frequency=Ui.vertical(a);
        toggle(a,p,"history","Проверка обновлений в фоне","Когда приложение не открыто",
            prefs.getBoolean(OtaUpdateSchedule.PREF_BACKGROUND,false),enabled->{
                prefs.edit().putBoolean(OtaUpdateSchedule.PREF_BACKGROUND,enabled).apply();
                OtaUpdateSchedule.configure(a);
                frequency.animate().cancel();
                frequency.animate().alpha(enabled?1f:.45f).setDuration(175).start();
                enableTree(frequency,enabled);
                if(enabled&&Build.VERSION.SDK_INT>=33&&a.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                   !=PackageManager.PERMISSION_GRANTED)
                    a.requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},1007);
            });
        spacer(p,7);p.addView(frequency,margin(8));
        frequency.addView(text(a,"ЧАСТОТА ПРОВЕРКИ",11,Ui.muted(),true),margin(12));
        LinearLayout sliderCard=Ui.vertical(a);
        sliderCard.setPadding(Ui.dp(9),Ui.dp(15),Ui.dp(9),Ui.dp(12));
        sliderCard.setBackground(Ui.shape(Ui.soft(a),Ui.dp(15),Ui.border()));
        frequency.addView(sliderCard,margin(7));
        long[] hours=OtaUpdateSchedule.INTERVAL_HOURS;
        String[] names=OtaUpdateSchedule.INTERVAL_NAMES;
        int selected=4;
        long stored=prefs.getLong(OtaUpdateSchedule.PREF_FREQUENCY,24L);
        for(int i=0;i<hours.length;i++)if(hours[i]==stored)selected=i;
        final SeekBar slider=new SeekBar(a);slider.setMax(hours.length-1);slider.setProgress(selected);
        slider.setProgressTintList(ColorStateList.valueOf(accent));
        slider.setProgressBackgroundTintList(ColorStateList.valueOf(Ui.border()));
        slider.setThumbTintList(ColorStateList.valueOf(accent));slider.setSplitTrack(false);
        TextView interval=text(a,names[selected],15,accent,true);interval.setGravity(Gravity.CENTER);
        sliderCard.addView(interval,margin(6));
        sliderCard.addView(slider,new LinearLayout.LayoutParams(-1,Ui.dp(46)));
        slider.setContentDescription("Частота проверки обновлений");
        slider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
            int last=slider.getProgress();
            @Override public void onProgressChanged(SeekBar bar,int pos,boolean fromUser){
                if(pos==last)return;
                last=pos;interval.animate().cancel();interval.setText(names[pos]);
                interval.setAlpha(.72f);interval.setScaleX(.98f);interval.setScaleY(.98f);
                interval.animate().alpha(1).scaleX(1).scaleY(1).setDuration(145)
                    .setInterpolator(new DecelerateInterpolator()).start();
                if(fromUser&&AppPrefs.bool(a,"haptics",true))bar.performHapticFeedback(HapticFeedbackConstants.CLOCK_TICK);
            }
            @Override public void onStartTrackingTouch(SeekBar bar){}
            @Override public void onStopTrackingTouch(SeekBar bar){
                prefs.edit().putLong(OtaUpdateSchedule.PREF_FREQUENCY,hours[bar.getProgress()]).apply();
                OtaUpdateSchedule.configure(a);
            }
        });
        boolean enabled=prefs.getBoolean(OtaUpdateSchedule.PREF_BACKGROUND,false);
        frequency.setAlpha(enabled?1f:.45f);enableTree(frequency,enabled);
    }
    public static void about(Activity a,LinearLayout p){
        String version=BuildConfig.VERSION_NAME;
        android.text.SpannableStringBuilder styled=new android.text.SpannableStringBuilder("PING TEST v"+version);
        styled.setSpan(new android.text.style.ForegroundColorSpan(AppPrefs.accent(a)),10,styled.length(),0);
        TextView heading=text(a,styled.toString(),16,Ui.fg(),true);heading.setText(styled);
        p.addView(heading,margin(14));
        info(a,p,"history","Сетевой монитор для Android",
             "ICMP-проверка, график задержки, игровые и пользовательские узлы, история сеансов.",false);
        info(a,p,"info","VPN и реальные результаты",
             "При активном VPN измеряется маршрут через туннель. Некоторые игровые службы не отвечают на ICMP.",true);
        info(a,p,"check","Официальные обновления",
             "Подписанный APK, проверка сертификата и SHA-256; установка внутри приложения.",true);
    }
    private static void info(Activity a,LinearLayout p,String glyph,String title,String detail,boolean small){
        LinearLayout row=Ui.horizontal(a);row.setGravity(Gravity.CENTER_VERTICAL);
        row.addView(symbol(a,glyph,25,AppPrefs.accent(a)),new LinearLayout.LayoutParams(Ui.dp(26),Ui.dp(26)));
        LinearLayout labels=Ui.vertical(a);labels.setPadding(Ui.dp(12),0,0,0);
        labels.addView(text(a,title,small?12:13,Ui.fg(),true));spacer(labels,4);
        labels.addView(text(a,detail,12,Ui.muted(),false));
        row.addView(labels,new LinearLayout.LayoutParams(0,-2,1));p.addView(row,margin(15));
    }
}
