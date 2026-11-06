package com.xarkon.pingtest;

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;

/**
 * Checks the DEFAULT route available to this app's UID.
 * A VPN visible elsewhere on the device does not imply our ICMP packets use it:
 * Android's per-app VPN exclusions can route this UID over Wi-Fi/cellular instead.
 *
 * This is a routing indicator, not a packet-level proof of the public egress IP.
 */
public final class VpnGuard {
    public enum Route { VPN, DIRECT, UNKNOWN }

    private VpnGuard(){}

    public static Route route(Context context){
        try{
            ConnectivityManager cm=(ConnectivityManager)context.getSystemService(
                Context.CONNECTIVITY_SERVICE);
            if(cm==null)return Route.UNKNOWN;
            Network network=cm.getActiveNetwork();
            if(network==null)return Route.UNKNOWN;
            NetworkCapabilities caps=cm.getNetworkCapabilities(network);
            if(caps==null)return Route.UNKNOWN;
            if(caps.hasTransport(NetworkCapabilities.TRANSPORT_VPN))
                return Route.VPN;
            // A physical/non-VPN default network means that PING TEST does NOT
            // use the VPN, even if other applications still do.
            if(caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_NOT_VPN)
                ||caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)
                ||caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR)
                ||caps.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET)
                ||caps.hasTransport(NetworkCapabilities.TRANSPORT_BLUETOOTH))
                return Route.DIRECT;
        }catch(RuntimeException ignored){
            // Fail to an honest unknown, not to a fabricated VPN warning.
        }
        return Route.UNKNOWN;
    }

    public static boolean active(Context context){
        return route(context)==Route.VPN;
    }

    public static String statusText(Context context){
        switch(route(context)){
            case VPN: return "● VPN · сеть по умолчанию для приложения";
            case DIRECT: return "● Без VPN · сеть по умолчанию для приложения";
            default: return "● Не удалось определить сеть по умолчанию";
        }
    }
}
