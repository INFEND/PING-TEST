package com.xarkon.pingtest;

import android.content.Context;
import android.content.SharedPreferences;

public final class AppPrefs {
    private AppPrefs() {}
    public static SharedPreferences of(Context c) { return c.getSharedPreferences("settings", Context.MODE_PRIVATE); }
    public static boolean bool(Context c, String key, boolean fallback) { return of(c).getBoolean(key, fallback); }
    public static int number(Context c, String key, int fallback) { return of(c).getInt(key, fallback); }
    public static String string(Context c, String key, String fallback) { return of(c).getString(key, fallback); }
    public static void put(Context c, String key, boolean v) { of(c).edit().putBoolean(key, v).apply(); }
    public static void put(Context c, String key, int v) { of(c).edit().putInt(key, v).apply(); }
    public static void put(Context c, String key, String v) { of(c).edit().putString(key, v).apply(); }
    public static int accent(Context c) { return number(c, "accent", 0xff55dfcb); }
    public static boolean amoled(Context c) { return bool(c, "amoled", true); }
}
