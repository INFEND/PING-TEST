package com.xarkon.pingtest;

import android.content.Context;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.Locale;

/** Readable labels are separate from endpoints. Game websites are NOT match servers. */
public final class TargetStore {
    private TargetStore(){}
    public static final class Target {
        public final String id,name,host,category,note;
        public final boolean custom;
        Target(String id,String name,String host,String category,String note,boolean custom){
            this.id=id;this.name=name;this.host=host;this.category=category;this.note=note;this.custom=custom;
        }
    }
    private static final String[][] BUILT_INS={
        {"yandex","Яндекс","ya.ru","Сайты","Общий доступ к интернету"},
        {"google","Google","google.com","Сайты","Поисковый сервис"},
        {"cloudflare","Cloudflare","1.1.1.1","Сайты","Общедоступный DNS"},
        {"google_dns","Google DNS","8.8.8.8","Сайты","Общедоступный DNS"},
        {"quad9","Quad9","9.9.9.9","Сайты","Общедоступный DNS"},
        {"fort_de","Fortnite","ping-de.ds.on.epicgames.com","Игры","Epic Games · диагностический узел (Германия)"},
        {"pubgm","PUBG Mobile","pubgmobile.com","Игры","Сайт игры, не сервер матча"},
        {"codm","Call of Duty: Mobile","callofduty.com","Игры","Сайт франшизы, не сервер матча"},
        {"mlbb","Mobile Legends: Bang Bang","mobilelegends.com","Игры","Сайт игры, не сервер матча"},
        {"freefire","Free Fire","freefiremobile.com","Игры","Сайт игры, не сервер матча"},
        {"brawl","Brawl Stars","brawlstars.com","Игры","Сайт игры, не сервер матча"},
        {"clash","Clash Royale","clashroyale.com","Игры","Сайт игры, не сервер матча"},
        {"roblox","Roblox","roblox.com","Игры","Платформа, не сервер игрового опыта"},
        {"genshin","Genshin Impact","genshin.hoyoverse.com","Игры","Сайт игры, не игровой сервер"}
    };
    public static ArrayList<Target> all(Context c){
        ArrayList<Target> out=new ArrayList<>();
        for(String[] item:BUILT_INS)out.add(new Target(item[0],item[1],item[2],item[3],item[4],false));
        try{JSONArray a=new JSONArray(AppPrefs.string(c,"custom_targets","[]"));
            for(int i=0;i<a.length();i++){JSONObject x=a.optJSONObject(i);if(x==null)continue;
                String id=x.optString("id"),name=x.optString("name"),host=x.optString("host");
                if(!id.isEmpty()&&!name.isEmpty()&&!host.isEmpty())out.add(new Target(id,name,host,"Мои узлы","Пользовательский адрес",true));
            }
        }catch(Exception ignored){}
        return out;
    }
    public static Target selected(Context c){
        String id=AppPrefs.string(c,"target_id","yandex");
        for(Target t:all(c))if(t.id.equals(id))return t;
        // Old 1.3.x installations stored one of several Fortnite region IDs.
        // Migrate those selections to the sole retained Fortnite entry.
        if(id.startsWith("fort_")){
            for(Target t:all(c))if(t.id.equals("fort_de")){
                AppPrefs.put(c,"target_id","fort_de");return t;
            }
        }
        return all(c).get(0);
    }
    public static void select(Context c,Target t){AppPrefs.put(c,"target_id",t.id);}
    public static String friendly(Context c,String host){
        for(Target t:all(c))if(t.host.equalsIgnoreCase(host))return t.name;
        return host;
    }
    public static boolean validHost(String s){
        if(s==null||s.length()<1||s.length()>253||s.contains("/")||s.contains("@")||s.contains(" ")||s.contains("://"))return false;
        if(s.startsWith("[")&&s.endsWith("]"))return s.length()>2;
        return s.matches("(?i)[a-z0-9._:-]+") && !s.startsWith("-") && !s.endsWith("-");
    }
    public static void save(Context c,Target previous,String name,String host){
        try{JSONArray current=new JSONArray(AppPrefs.string(c,"custom_targets","[]"));JSONArray next=new JSONArray();
            for(int i=0;i<current.length();i++){JSONObject x=current.optJSONObject(i);if(x==null)continue;
                if(previous==null||!x.optString("id").equals(previous.id))next.put(x);
            }
            String id=previous!=null?previous.id:"custom_"+System.currentTimeMillis();
            JSONObject value=new JSONObject();value.put("id",id);value.put("name",name);value.put("host",host);next.put(value);
            AppPrefs.put(c,"custom_targets",next.toString());AppPrefs.put(c,"target_id",id);
        }catch(Exception ignored){}
    }
    public static void remove(Context c,Target target){if(!target.custom)return;
        try{JSONArray current=new JSONArray(AppPrefs.string(c,"custom_targets","[]"));JSONArray next=new JSONArray();
            for(int i=0;i<current.length();i++){JSONObject x=current.optJSONObject(i);if(x!=null&&!x.optString("id").equals(target.id))next.put(x);}
            boolean wasSelected=AppPrefs.string(c,"target_id","yandex").equals(target.id);
            AppPrefs.put(c,"custom_targets",next.toString());
            if(wasSelected)AppPrefs.put(c,"target_id","yandex");
        }catch(Exception ignored){AppPrefs.put(c,"target_id","yandex");}
    }
}
