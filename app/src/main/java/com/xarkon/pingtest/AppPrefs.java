package com.xarkon.pingtest;
import android.content.Context;
import android.content.SharedPreferences;
public final class AppPrefs {
 private AppPrefs(){}
 public static SharedPreferences of(Context c){return c.getSharedPreferences("settings",Context.MODE_PRIVATE);}
 public static boolean bool(Context c,String k,boolean def){return of(c).getBoolean(k,def);}
 public static int number(Context c,String k,int def){return of(c).getInt(k,def);}
 public static String string(Context c,String k,String def){return of(c).getString(k,def);}
 public static void put(Context c,String k,boolean v){of(c).edit().putBoolean(k,v).apply();}
 public static void put(Context c,String k,int v){of(c).edit().putInt(k,v).apply();}
 public static void put(Context c,String k,String v){of(c).edit().putString(k,v).apply();}
 public static int accent(Context c){return number(c,"accent",0xff55dfcb);}
 public static String mode(Context c){
  String mode=string(c,"theme_mode","");
  if("amoled".equals(mode)||"dark".equals(mode)||"light".equals(mode))return mode;
  return bool(c,"amoled",true)?"amoled":"dark";
 }
 public static boolean amoled(Context c){return "amoled".equals(mode(c));}
 public static boolean light(Context c){return "light".equals(mode(c));}
 public static void setMode(Context c,String mode){
  if(!"amoled".equals(mode)&&!"light".equals(mode)&&!"dark".equals(mode))return;
  of(c).edit().putString("theme_mode",mode).putBoolean("amoled","amoled".equals(mode)).apply();
 }
}
