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
    public static int bg(Context c){return AppPrefs.light(c)?0xfff5f7fb:AppPrefs.amoled(c)?0xff000000:0xff0a111b;}
    public static int surface(Context c){return AppPrefs.light(c)?0xffffffff:AppPrefs.amoled(c)?0xff0b0b0d:0xff121e2a;}
    public static int surface2(Context c){return AppPrefs.light(c)?0xffe8eef5:AppPrefs.amoled(c)?0xff191b20:0xff203140;}
    private static int text=0xfff5f7f9,secondary=0xff9ba8b1,stroke=0xff27282e;
    public static void applyPalette(Context c){String mode=AppPrefs.mode(c);
        if("light".equals(mode)){text=0xff152536;secondary=0xff607587;stroke=0xffdce5ed;}
        else if("amoled".equals(mode)){text=0xfff5f7f9;secondary=0xff9ba8b1;stroke=0xff27282e;}
        else{text=0xfff1f6fb;secondary=0xff9caebd;stroke=0xff283947;}
    }
    public static int fg(){return text;}
    public static int muted(){return secondary;}
    public static int border(){return stroke;}
    public static int soft(Context c){return AppPrefs.light(c)?0xffedf2f7:AppPrefs.amoled(c)?0xff101315:0xff101924;}
    public static int onAccent(Context c){int a=AppPrefs.accent(c);
        double r=android.graphics.Color.red(a)/255.0,g=android.graphics.Color.green(a)/255.0,b=android.graphics.Color.blue(a)/255.0;
        r=r<=.04045?r/12.92:Math.pow((r+.055)/1.055,2.4);
        g=g<=.04045?g/12.92:Math.pow((g+.055)/1.055,2.4);
        b=b<=.04045?b/12.92:Math.pow((b+.055)/1.055,2.4);
        return .2126*r+.7152*g+.0722*b>.24?0xff071219:0xffffffff;
    }
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
        l.setBackground(shape(surface(c),dp(22),border()));return l;
    }
    public static LinearLayout.LayoutParams margins(int w,int h,int t,int b){
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(w<0?w:dp(w),h<0?h:dp(h));
        p.topMargin=dp(t);p.bottomMargin=dp(b);return p;
    }
    public static TextView button(Context c,String text,boolean filled){
        TextView b=text(c,text,15,filled?onAccent(c):fg(),true);
        b.setGravity(Gravity.CENTER);b.setPadding(dp(14),dp(10),dp(14),dp(10));
        b.setBackground(shape(filled?AppPrefs.accent(c):surface2(c),dp(12),filled?0:border()));
        b.setClickable(true);b.setFocusable(true);motion(c,b);return b;
    }
    public static TextView chip(Context c,String value,boolean selected){
        TextView t=text(c,value,13,selected?onAccent(c):muted(),selected);
        t.setGravity(Gravity.CENTER);t.setPadding(dp(10),dp(7),dp(10),dp(7));
        t.setBackground(shape(selected?AppPrefs.accent(c):surface2(c),dp(10),selected?0:border()));
        t.setClickable(true);motion(c,t);return t;
    }
    public static void motion(Context c, View view){
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
