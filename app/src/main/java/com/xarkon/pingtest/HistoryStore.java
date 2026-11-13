package com.xarkon.pingtest;

import android.content.Context;
import android.content.SharedPreferences;
import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONException;

public final class HistoryStore {
    private static final String KEY = "sessions";
    private HistoryStore() {}
    public static int limit(Context c) {
        int saved=c.getSharedPreferences("history",Context.MODE_PRIVATE).getInt("session_limit",200);
        return Math.max(50,Math.min(1000,50*Math.round(saved/50f)));
    }
    public static synchronized void setLimit(Context c,int value) {
        int safe=Math.max(50,Math.min(1000,50*Math.round(value/50f)));
        c.getSharedPreferences("history",Context.MODE_PRIVATE).edit().putInt("session_limit",safe).apply();
        JSONArray old=all(c), trimmed=new JSONArray();
        for(int i=0;i<old.length()&&trimmed.length()<safe;i++)trimmed.put(old.opt(i));
        if(trimmed.length()<old.length())save(c,trimmed);
    }
    public static synchronized JSONArray all(Context c) {
        String raw = c.getSharedPreferences("history", Context.MODE_PRIVATE).getString(KEY, "[]");
        try { return new JSONArray(raw); } catch (JSONException ignored) { return new JSONArray(); }
    }
    public static synchronized void upsert(Context c, JSONObject entry) {
        JSONArray old = all(c), updated = new JSONArray();
        long id = entry.optLong("id", -1);
        // Parallel probe callbacks may persist snapshots out of order.
        // Never replace a newer or final snapshot with an older checkpoint.
        if(id>=0)for(int i=0;i<old.length();i++){
            JSONObject previous=old.optJSONObject(i);
            if(previous!=null && previous.optLong("id",-2)==id &&
                    isStaleCheckpoint(previous,entry))return;
        }
        updated.put(entry);
        for (int i = 0; i < old.length() && updated.length() < limit(c); i++) {
            JSONObject x = old.optJSONObject(i);
            if (x != null && (id < 0 || !x.has("id") || x.optLong("id", -2) != id)) updated.put(x);
        }
        save(c, updated);
    }
    static boolean isStaleCheckpoint(JSONObject previous,JSONObject incoming) {
        if(previous.optBoolean("finished",false) && !incoming.optBoolean("finished",false))return true;
        return previous.has("revision") && incoming.has("revision") &&
                previous.optLong("revision",-1)>incoming.optLong("revision",-1);
    }
    public static synchronized void remove(Context c, long id) {
        JSONArray old = all(c), result = new JSONArray();
        for (int i = 0; i < old.length(); i++) {
            JSONObject x = old.optJSONObject(i);
            if (x != null && (id < 0 || !x.has("id") || x.optLong("id", -2) != id)) result.put(x);
        }
        save(c, result);
    }
    /** Delete one selected session, including legacy records with no ID.
     *  Verify the selected row against current storage before changing anything.
     *  A concurrently appended session shifts indices; never delete a different row.
     */
    public static synchronized boolean removeEntry(Context c,int index,JSONObject expected) {
        if(expected==null || index<0)return false;
        JSONArray old=all(c);
        JSONObject current=old.optJSONObject(index);
        if(current==null || !current.toString().equals(expected.toString()))return false;
        JSONArray updated=new JSONArray();
        for(int i=0;i<old.length();i++)if(i!=index)updated.put(old.opt(i));
        save(c,updated);
        return true;
    }
    public static synchronized void clear(Context c) { save(c, new JSONArray()); }
    private static void save(Context c, JSONArray a) {
        c.getSharedPreferences("history", Context.MODE_PRIVATE).edit().putString(KEY, a.toString()).apply();
    }
}
