package com.xarkon.pingtest;

/** Contrast calculations for the monitor's primary action; no Android dependencies. */
final class AccentContrast {
    private AccentContrast(){}
    private static final int WHITE=0xffffffff, BLACK=0xff000000, INK=0xff071219;

    private static double linear(int channel){
        double s=channel/255.0;
        return s<=.04045?s/12.92:Math.pow((s+.055)/1.055,2.4);
    }

    static double luminance(int rgb){
        return .2126*linear((rgb>>>16)&255)+.7152*linear((rgb>>>8)&255)+.0722*linear(rgb&255);
    }

    static double contrast(int a,int b){
        double x=luminance(a),y=luminance(b);
        return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);
    }

    static int readableText(int fill){
        // Black or white always gives at least 4.5:1 on an opaque sRGB fill.
        if(contrast(fill,WHITE)>=contrast(fill,BLACK))return WHITE;
        // Preserve the QR LINK-style dark ink when it meets the same threshold.
        return contrast(fill,INK)>=4.5?INK:BLACK;
    }
}
