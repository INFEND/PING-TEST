package com.xarkon.pingtest;

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;

public final class VpnGuard {
    private VpnGuard(){}
    public static boolean active(Context context){
        try{
            ConnectivityManager cm=(ConnectivityManager)context.getSystemService(Context.CONNECTIVITY_SERVICE);
            if(cm==null)return false;
            Network current=cm.getActiveNetwork();
            if(current!=null){NetworkCapabilities caps=cm.getNetworkCapabilities(current);
                if(caps!=null&&caps.hasTransport(NetworkCapabilities.TRANSPORT_VPN))return true;
            }
            for(Network net:cm.getAllNetworks()){
                NetworkCapabilities caps=cm.getNetworkCapabilities(net);
                if(caps!=null&&caps.hasTransport(NetworkCapabilities.TRANSPORT_VPN))return true;
            }
        }catch(Exception ignored){}
        return false;
    }
}
