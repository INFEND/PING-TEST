package com.xarkon.pingtest;

import android.app.Activity;
import android.content.SharedPreferences;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.TextView;

/** In-app QR LINK-style OTA preferences, independent of PING measurement settings. */
public final class OtaOptions {
    private OtaOptions(){}
    public static void attach(Activity activity,LinearLayout parent,Runnable refresh){
        SharedPreferences prefs=activity.getSharedPreferences("settings",0);
        TextView launch=Ui.chip(activity,"",false);
        launch.setTextColor(Ui.fg());
        Runnable updateLaunch=()->launch.setText("При запуске: "+(prefs.getBoolean(OtaUpdateSchedule.PREF_ON_LAUNCH,false)?"ВКЛ":"ВЫКЛ"));
        updateLaunch.run();
        launch.setOnClickListener(v->{
            boolean enabled=!prefs.getBoolean(OtaUpdateSchedule.PREF_ON_LAUNCH,false);
            prefs.edit().putBoolean(OtaUpdateSchedule.PREF_ON_LAUNCH,enabled).apply();
            updateLaunch.run();
        });
        parent.addView(launch,Ui.margins(-1,-2,0,7));
        TextView background=Ui.chip(activity,"",false);
        background.setTextColor(Ui.fg());
        Runnable updateBg=()->background.setText("Проверять в фоне: "+(prefs.getBoolean(OtaUpdateSchedule.PREF_BACKGROUND,false)?"ВКЛ":"ВЫКЛ"));
        updateBg.run();
        background.setOnClickListener(v->{
            boolean enabled=!prefs.getBoolean(OtaUpdateSchedule.PREF_BACKGROUND,false);
            prefs.edit().putBoolean(OtaUpdateSchedule.PREF_BACKGROUND,enabled).apply();
            OtaUpdateSchedule.configure(activity);
            updateBg.run();
        });
        parent.addView(background,Ui.margins(-1,-2,0,12));
        parent.addView(Ui.text(activity,"ИНТЕРВАЛ ФОНОВОЙ ПРОВЕРКИ",11,Ui.muted(),true));
        HorizontalScrollView scroll=new HorizontalScrollView(activity);
        scroll.setHorizontalScrollBarEnabled(false);
        LinearLayout strip=Ui.horizontal(activity);
        long selected=prefs.getLong(OtaUpdateSchedule.PREF_FREQUENCY,24L);
        for(int i=0;i<OtaUpdateSchedule.INTERVAL_HOURS.length;i++){
            final long hours=OtaUpdateSchedule.INTERVAL_HOURS[i];
            TextView chip=Ui.chip(activity,OtaUpdateSchedule.INTERVAL_NAMES[i],selected==hours);
            strip.addView(chip,Ui.margins(-2,-2,0,0));
            chip.setOnClickListener(v->{
                prefs.edit().putLong(OtaUpdateSchedule.PREF_FREQUENCY,hours).apply();
                OtaUpdateSchedule.configure(activity);
                refresh.run();
            });
        }
        scroll.addView(strip);
        parent.addView(scroll,Ui.margins(-1,-2,0,9));
        String status=prefs.getString("ota_background_result","");
        if(!status.isEmpty())parent.addView(Ui.text(activity,status,11,Ui.muted(),false));
        parent.addView(Ui.text(activity,"Фоновая проверка зависит от энергосбережения Android. Уведомление появляется только при новой версии.",11,Ui.muted(),false));
    }
}
