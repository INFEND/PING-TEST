package com.xarkon.pingtest;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import android.net.Uri;
import android.os.Build;
import android.provider.Settings;
import android.widget.ProgressBar;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import org.json.JSONObject;
import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.IOException;
import java.net.URL;
import java.net.HttpURLConnection;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Locale;

/** Pin official GitHub channel and signing certificate. All network I/O stays off main thread. */
public final class UpdateManager {
    private UpdateManager(){}
    public static final String MANIFEST_URL="https://github.com/INFEND/PING-TEST/releases/latest/download/update.json";
    private static final String RELEASE_PREFIX="https://github.com/INFEND/PING-TEST/releases/download/";
    private static final String PACKAGE="com.xarkon.pingtest";
    private static final String CERT="C17E87ED0E0EB7E9D96CE71F91804AE8A0F8BCAD5065C464342E2FA5F4026802";
    private static final long LIMIT=250L*1024*1024;
    private static final String FILENAME="PING-TEST.apk";
    private static class Release {
        final int code;
        final String version,url,sha,notes;
        final long bytes;
        Release(JSONObject j)throws Exception {
            if(j.optInt("schema",0)!=1 || !PACKAGE.equals(j.optString("packageName")))throw new IOException("Некорректный OTA-манифест");
            code=j.getInt("versionCode");version=j.getString("versionName");
            sha=j.getString("sha256").toLowerCase(Locale.US);url=j.getString("apkUrl");
            bytes=j.getLong("sizeBytes");notes=j.optString("notes","");
            if(code<=0||!version.matches("[0-9]+\\.[0-9]+\\.[0-9]+")||!sha.matches("[a-f0-9]{64}")||bytes<1||bytes>LIMIT||notes.length()>5000)
                throw new IOException("Некорректные параметры обновления");
            if(!url.equals(RELEASE_PREFIX+"v"+version+"/"+FILENAME))throw new IOException("Неофициальный адрес APK");
        }
    }
    public static File apkFile(Context c){return new File(new File(c.getFilesDir(),"ota"),FILENAME);}
    private static HttpURLConnection open(String url)throws Exception {
        URL u=new URL(url);
        if(!"https".equalsIgnoreCase(u.getProtocol())||!"github.com".equalsIgnoreCase(u.getHost()))throw new IOException("Недоверенный сервер");
        HttpURLConnection c=(HttpURLConnection)u.openConnection();
        c.setConnectTimeout(15000);c.setReadTimeout(25000);c.setRequestProperty("User-Agent","PING-TEST-OTA/1.0");
        if(c.getResponseCode()!=200){int status=c.getResponseCode();c.disconnect();throw new IOException("GitHub: HTTP "+status);}
        return c;
    }
    private static Release latest()throws Exception {
        HttpURLConnection c=open(MANIFEST_URL);
        try(InputStream in=c.getInputStream();ByteArrayOutputStream out=new ByteArrayOutputStream()) {
            byte[] b=new byte[8192];int n;
            while((n=in.read(b))!=-1){if(out.size()+n>65536)throw new IOException("Слишком большой OTA-манифест");out.write(b,0,n);}
            return new Release(new JSONObject(out.toString("UTF-8")));
        }finally{c.disconnect();}
    }
    private static void ui(Activity a,Runnable callback){a.runOnUiThread(()->{if(!a.isFinishing()&&!a.isDestroyed())callback.run();});}
    private static void error(Activity a,Exception e){ui(a,()->new AlertDialog.Builder(a).setTitle("Не удалось обновить").setMessage(
        e.getMessage()==null?"Проверьте интернет и повторите попытку.":e.getMessage()).setPositiveButton("Закрыть",null).show());}
    public static void check(Activity activity){
        Toast.makeText(activity,"Проверка обновлений…",Toast.LENGTH_SHORT).show();
        new Thread(()->{
            try{
                Release r=latest();
                int current=currentVersion(activity);
                ui(activity,()->{
                    if(r.code<=current){new AlertDialog.Builder(activity).setTitle("PING TEST обновлён")
                        .setMessage("Установлена актуальная версия.\nВерсия: "+BuildConfig.VERSION_NAME)
                        .setPositiveButton("Готово",null).show();return;}
                    new AlertDialog.Builder(activity).setTitle("Доступна версия "+r.version)
                        .setMessage("Обновление PING TEST\n\n"+r.notes+"\n\nРазмер: "+(r.bytes/1024/1024)+" МБ")
                        .setNegativeButton("Позже",null).setPositiveButton("Загрузить",(d,w)->download(activity,r)).show();
                });
            }catch(Exception e){error(activity,e);}
        },"ping-ota-check").start();
    }
    private static int currentVersion(Context c)throws Exception{return c.getPackageManager().getPackageInfo(c.getPackageName(),0).versionCode;}
    private static void download(Activity a,Release release){
        LinearLayout panel=new LinearLayout(a);panel.setPadding(42,30,42,10);panel.setOrientation(LinearLayout.VERTICAL);
        TextView label=new TextView(a);label.setText("Загрузка защищённого обновления…");panel.addView(label);
        ProgressBar bar=new ProgressBar(a,null,android.R.attr.progressBarStyleHorizontal);bar.setMax(100);panel.addView(bar);
        AlertDialog dlg=new AlertDialog.Builder(a).setTitle("PING TEST · OTA").setView(panel).setCancelable(false).create();dlg.show();
        new Thread(()->{
            File apk=apkFile(a), temp=new File(apk.getParentFile(),FILENAME+".part");
            HttpURLConnection c=null;
            try{
                if(!apk.getParentFile().isDirectory()&&!apk.getParentFile().mkdirs())throw new IOException("Невозможно подготовить память");
                if(apk.getParentFile().getUsableSpace()<release.bytes+5*1024*1024)throw new IOException("Недостаточно памяти");
                c=open(release.url);long total=c.getContentLengthLong();
                if(total>LIMIT || (total>0&&total!=release.bytes))throw new IOException("Размер APK не совпадает");
                long received=0,shown=0;MessageDigest digest=MessageDigest.getInstance("SHA-256");
                try(InputStream input=new BufferedInputStream(c.getInputStream());FileOutputStream output=new FileOutputStream(temp)){
                    byte[] b=new byte[32768];int n;
                    while((n=input.read(b))!=-1){received+=n;if(received>release.bytes)throw new IOException("APK превышает заявленный размер");
                        output.write(b,0,n);digest.update(b,0,n);
                        long completed=received;
                        if(received-shown>release.bytes/100||received==release.bytes){shown=received;
                            ui(a,()->{bar.setProgress((int)(100L*completed/release.bytes));label.setText("Загружено: "+(100L*completed/release.bytes)+"%");});}
                    }
                    output.getFD().sync();
                }
                if(received!=release.bytes)throw new IOException("Файл загружен не полностью");
                if(!hex(digest.digest()).equalsIgnoreCase(release.sha))throw new IOException("SHA-256 APK не совпадает");
                if(apk.exists()&&!apk.delete())throw new IOException("Невозможно заменить предыдущий файл");
                if(!temp.renameTo(apk))throw new IOException("Не удалось сохранить APK");
                verify(a,apk,release.code);
                ui(a,()->{dlg.dismiss();new AlertDialog.Builder(a).setTitle("Подпись проверена")
                    .setMessage("Обновление загружено и проверено. Android запросит подтверждение установки.")
                    .setPositiveButton("Установить",(d,w)->install(a,apk,release.code)).setNegativeButton("Позже",null).show();});
            }catch(Exception e){temp.delete();apk.delete();ui(a,dlg::dismiss);error(a,e);}
            finally{if(c!=null)c.disconnect();}
        },"ping-ota-download").start();
    }
    private static String hex(byte[] data){StringBuilder sb=new StringBuilder();for(byte b:data)sb.append(String.format(Locale.US,"%02x",b&255));return sb.toString();}
    @SuppressWarnings("deprecation") private static Signature[] signatures(PackageInfo info){
        if(Build.VERSION.SDK_INT>=28&&info.signingInfo!=null)return info.signingInfo.getApkContentsSigners();
        return info.signatures;
    }
    private static void verify(Context c,File apk,int expected)throws Exception{
        PackageManager pm=c.getPackageManager();
        int flag=Build.VERSION.SDK_INT>=28?PackageManager.GET_SIGNING_CERTIFICATES:PackageManager.GET_SIGNATURES;
        PackageInfo file=pm.getPackageArchiveInfo(apk.getAbsolutePath(),flag);
        PackageInfo installed=pm.getPackageInfo(c.getPackageName(),flag);
        if(file==null||!PACKAGE.equals(file.packageName)||file.versionCode!=expected||expected<=installed.versionCode)
            throw new IOException("Неверный пакет или версия APK");
        Signature[] s=signatures(file),current=signatures(installed);
        if(s==null||current==null||s.length!=1||current.length!=1)throw new IOException("Непроверенная подпись");
        String candidate=hex(MessageDigest.getInstance("SHA-256").digest(s[0].toByteArray()));
        String existing=hex(MessageDigest.getInstance("SHA-256").digest(current[0].toByteArray()));
        if(!CERT.equalsIgnoreCase(candidate)||!CERT.equalsIgnoreCase(existing)||!Arrays.equals(s[0].toByteArray(),current[0].toByteArray()))
            throw new IOException("Подпись APK не соответствует официальной подписи PING TEST");
    }
    private static void install(Activity a,File apk,int code){
        try{
            verify(a,apk,code);
            if(Build.VERSION.SDK_INT>=26&&!a.getPackageManager().canRequestPackageInstalls()){
                a.startActivity(new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,Uri.parse("package:"+a.getPackageName())));
                Toast.makeText(a,"Разрешите установку APK и повторите обновление",Toast.LENGTH_LONG).show();return;
            }
            Uri uri=Uri.parse("content://"+a.getPackageName()+".ota/apk");
            Intent intent=new Intent(Intent.ACTION_VIEW).setDataAndType(uri,"application/vnd.android.package-archive");
            intent.setClipData(ClipData.newRawUri("PING TEST OTA",uri));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_GRANT_READ_URI_PERMISSION);
            a.getApplicationContext().startActivity(intent);
        }catch(Exception e){error(a,e);}
    }
}
