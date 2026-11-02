package com.xarkon.pingtest;

import android.content.Context;
import android.content.SharedPreferences;
import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONException;

public final class HistoryStore {
    private static final String KEY = "sessions";
    private HistoryStore() {}
    public static synchronized JSONArray all(Context c) {
        String raw = c.getSharedPreferences("history", Context.MODE_PRIVATE).getString(KEY, "[]");
        try { return new JSONArray(raw); } catch (JSONException ignored) { return new JSONArray(); }
    }
    public static synchronized void upsert(Context c, JSONObject entry) {
        JSONArray old = all(c), updated = new JSONArray();
        long id = entry.optLong("id", -1);
        updated.put(entry);
        for (int i = 0; i < old.length() && updated.length() < 200; i++) {
            JSONObject x = old.optJSONObject(i);
            if (x != null && x.optLong("id", -2) != id) updated.put(x);
        }
        save(c, updated);
    }
    public static synchronized void remove(Context c, long id) {
        JSONArray old = all(c), result = new JSONArray();
        for (int i = 0; i < old.length(); i++) {
            JSONObject x = old.optJSONObject(i);
            if (x != null && x.optLong("id", -2) != id) result.put(x);
        }
        save(c, result);
    }
    public static synchronized void clear(Context c) { save(c, new JSONArray()); }
    private static void save(Context c, JSONArray a) {
        c.getSharedPreferences("history", Context.MODE_PRIVATE).edit().putString(KEY, a.toString()).apply();
    }
}
