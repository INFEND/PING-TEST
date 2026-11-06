package com.xarkon.pingtest;

import android.graphics.Color;

/** Calibrated, continuous green -> yellow -> red signal quality palette. */
public final class QualityColors {
    private QualityColors(){}
    public static final int GREEN=0xFF4BE6A0;
    public static final int YELLOW=0xFFFFD35B;
    public static final int RED=0xFFFF667A;
    public static final int UNKNOWN=0xFF778592;

    public static int blend(int a,int b,float fraction){
        float t=Float.isNaN(fraction)?0f:Math.max(0f,Math.min(1f,fraction));
        return Color.argb(255,
            (int)(Color.red(a)+(Color.red(b)-Color.red(a))*t),
            (int)(Color.green(a)+(Color.green(b)-Color.green(a))*t),
            (int)(Color.blue(a)+(Color.blue(b)-Color.blue(a))*t));
    }
    private static int map(double v,double good,double middle,double bad){
        if(v<0||Double.isNaN(v)||Double.isInfinite(v))return UNKNOWN;
        if(v<=good)return GREEN;
        if(v<=middle)return blend(GREEN,YELLOW,(float)((v-good)/(middle-good)));
        return blend(YELLOW,RED,(float)Math.min(1,(v-middle)/(bad-middle)));
    }
    public static int rtt(double ms){return map(ms,45,110,240);}
    public static int loss(double percent){return map(percent,0.1,4,18);}
    public static int jitter(double ms){return map(ms,4,15,50);}
    public static int success(int received,int sent){
        if(sent<=0||received<0||received>sent)return UNKNOWN;
        return loss(100.0*(sent-received)/sent);
    }
}
