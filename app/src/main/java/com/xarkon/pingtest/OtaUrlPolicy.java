package com.xarkon.pingtest;
import java.net.URL;
public final class OtaUrlPolicy {
 public static final String CANONICAL_MANIFEST="https://github.com/INFEND/PING-TEST/releases/latest/download/update.json";
 public static final String LEGACY_MANIFEST=CANONICAL_MANIFEST;
 private OtaUrlPolicy(){}
 public static boolean trustedApk(String raw,String version){
  if(raw==null||version==null||!version.matches("[A-Za-z0-9._-]{1,40}"))return false;
  try{URL u=new URL(raw);
   return "https".equalsIgnoreCase(u.getProtocol())&&"github.com".equalsIgnoreCase(u.getHost())
    &&u.getPort()==-1&&u.getUserInfo()==null&&u.getQuery()==null&&u.getRef()==null
    &&u.getPath().equals("/INFEND/PING-TEST/releases/download/v"+version+"/PING-TEST.apk");
  }catch(Exception e){return false;}
 }
 public static String canonicalApkFallback(String raw,String version){return null;}
}
