package com.xarkon.pingtest;

import android.app.Activity;
import android.graphics.Insets;
import android.os.Build;
import android.view.View;
import android.view.WindowInsets;

/** Keeps the header and bottom navigation clear of system bars and display cutouts. */
@SuppressWarnings("deprecation")
public final class UiInsets {
    private UiInsets() {}

    public static void apply(Activity activity, View root) {
        final int baseLeft=root.getPaddingLeft(),baseTop=root.getPaddingTop();
        final int baseRight=root.getPaddingRight(),baseBottom=root.getPaddingBottom();

        // Android 15–17 can draw a frame before the first inset callback.
        // Reserve status-bar space immediately to avoid flashing under the clock.
        int statusHeight=0;
        int id=activity.getResources().getIdentifier("status_bar_height","dimen","android");
        if(id!=0) {
            try { statusHeight=activity.getResources().getDimensionPixelSize(id); }
            catch(android.content.res.Resources.NotFoundException ignored) {}
        }
        final int fallbackTop=statusHeight;
        root.setPadding(baseLeft,baseTop+fallbackTop,baseRight,baseBottom);
        root.setOnApplyWindowInsetsListener((view,insets)->{
            int left,top,right,bottom;
            if(Build.VERSION.SDK_INT>=30) {
                // Include hidden navigation bars as well as side cutouts in landscape.
                int bars=WindowInsets.Type.statusBars()|WindowInsets.Type.navigationBars();
                Insets safe=insets.getInsetsIgnoringVisibility(bars);
                Insets cutout=insets.getInsets(WindowInsets.Type.displayCutout());
                left=Math.max(safe.left,cutout.left);
                top=Math.max(fallbackTop,Math.max(safe.top,cutout.top));
                right=Math.max(safe.right,cutout.right);
                bottom=Math.max(safe.bottom,cutout.bottom);
            } else {
                left=insets.getSystemWindowInsetLeft();
                top=Math.max(fallbackTop,insets.getSystemWindowInsetTop());
                right=insets.getSystemWindowInsetRight();
                bottom=insets.getSystemWindowInsetBottom();
            }
            // Use immutable base paddings: insets never accumulate after tab/theme changes.
            int l=baseLeft+left,t=baseTop+top,r=baseRight+right,b=baseBottom+bottom;
            if(view.getPaddingLeft()!=l||view.getPaddingTop()!=t
                    ||view.getPaddingRight()!=r||view.getPaddingBottom()!=b)
                view.setPadding(l,t,r,b);
            return insets;
        });
    }
}
