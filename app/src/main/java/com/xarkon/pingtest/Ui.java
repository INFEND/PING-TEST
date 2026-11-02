package com.xarkon.pingtest;

import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.widget.*;

public final class Ui {
    private Ui(){}
    public static int bg(Context c){return AppPrefs.amoled(c)?0xFF000000:0xFF0A111B;}
    public static int surface(Context c){return AppPrefs.amoled(c)?0xFF0C1015:0xFF121E2A;}
    public static int surface2(Context c){return AppPrefs.amoled(c)?0xFF19212A:0xFF203140;}
    public static int fg(){return 0xFFF5F7F9;}
    public static int muted(){return 0xFF9FAFBA;}
    public static int border(){return 0xFF25303A;}
    public static GradientDrawable shape(int color,int r,int line){
        GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(r);
        if(line!=0)d.setStroke(dp(1),line);return d;
    }
    public static int dp(float n){return (int)(android.content.res.Resources.getSystem().getDisplayMetrics().density*n+0.5f);}
    public static TextView text(Context c,String str,int sp,int color,boolean bold){
        TextView t=new TextView(c);t.setText(str);t.setTextColor(color);t.setTextSize(sp);
        t.setFontFeatureSettings("kern");t.setIncludeFontPadding(false);t.setGravity(Gravity.CENTER_VERTICAL);
        if(bold)t.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));
        return t;
    }
    public static TextView mono(Context c,String str,int sp,int color){
        TextView t=text(c,str,sp,color,false);t.setTypeface(Typeface.MONOSPACE);return t;
    }
    public static LinearLayout vertical(Context c){LinearLayout l=new LinearLayout(c);l.setOrientation(LinearLayout.VERTICAL);return l;}
    public static LinearLayout horizontal(Context c){LinearLayout l=new LinearLayout(c);l.setGravity(Gravity.CENTER_VERTICAL);l.setOrientation(LinearLayout.HORIZONTAL);return l;}
    public static LinearLayout panel(Context c){
        LinearLayout l=vertical(c);l.setPadding(dp(12),dp(10),dp(12),dp(10));
        l.setBackground(shape(surface(c),dp(18),border()));return l;
    }
    public static LinearLayout.LayoutParams margins(int w,int h,int t,int b){
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(w<0?w:dp(w),h<0?h:dp(h));
        p.topMargin=dp(t);p.bottomMargin=dp(b);return p;
    }
    public static TextView button(Context c,String text,boolean filled){
        TextView b=text(c,text,15,filled?0xFF0A1420:fg(),true);
        b.setGravity(Gravity.CENTER);b.setPadding(dp(14),dp(10),dp(14),dp(10));
        b.setBackground(shape(filled?AppPrefs.accent(c):surface2(c),dp(12),filled?0:border()));
        b.setClickable(true);b.setFocusable(true);motion(c,b);return b;
    }
    public static TextView chip(Context c,String value,boolean selected){
        TextView t=text(c,value,13,selected?0xFF07111F:muted(),selected);
        t.setGravity(Gravity.CENTER);t.setPadding(dp(10),dp(7),dp(10),dp(7));
        t.setBackground(shape(selected?AppPrefs.accent(c):surface2(c),dp(10),selected?0:border()));
        t.setClickable(true);motion(c,t);return t;
    }
    private static void motion(Context c, View view){
        view.setOnTouchListener((v,event)->{
            if(!AppPrefs.bool(c,"motion",true))return false;
            if(event.getAction()==android.view.MotionEvent.ACTION_DOWN){
                v.animate().cancel();v.animate().scaleX(.98f).scaleY(.98f).setDuration(65).start();
            }else if(event.getAction()==android.view.MotionEvent.ACTION_UP||event.getAction()==android.view.MotionEvent.ACTION_CANCEL){
                v.animate().scaleX(1f).scaleY(1f).setDuration(120).start();
            }
            return false;
        });
    }
    public static View divider(Context c){View v=new View(c);v.setBackgroundColor(border());return v;}
    public static void touch(View v,Runnable run){v.setOnClickListener(w->run.run());}
}
