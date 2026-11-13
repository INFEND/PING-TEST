package com.xarkon.pingtest;

import android.animation.ValueAnimator;
import android.content.Context;
import android.graphics.*;
import android.view.View;
import android.view.animation.DecelerateInterpolator;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

/** Realtime RTT chart, quality-colored samples, error markers and animated latest sample. */
public final class GraphView extends View {
    private float[] points=new float[0];
    // UI-thread-only scratch storage for the interpolated last RTT sample.
    // Never mutate points: it is the immutable snapshot used by setData().
    private float[] animatedPoints=new float[0];
    private float progress=1f, previous=-1;
    private float displayMax=Float.NaN,scaleStart=Float.NaN,scaleTarget=Float.NaN;
    private int accent=0xff55dfcb,bg=0xff0b0b0d;
    private ValueAnimator animator;
    private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Path fillPath=new Path();
    public GraphView(Context c){super(c);}
    public void setData(List<Float> values,int color,int background){
        float[] fresh=new float[values.size()];for(int i=0;i<fresh.length;i++)fresh[i]=values.get(i);
        if(Arrays.equals(points,fresh)&&accent==color&&bg==background)return;
        // A full rolling window can shift even when consecutive RTT values match.
        // Compare the entire visible window so repeated RTTs still animate as new samples.
        boolean newSample=points.length>0&&fresh.length>0&&!Arrays.equals(points,fresh);
        previous=points.length>0?points[points.length-1]:-1;
        // Keep the Y axis stable across incoming packets. A sudden high RTT
        // must still fit, while downward rescaling waits for a meaningful drop.
        float required=axisMaximum(fresh);
        if(Float.isNaN(displayMax)){
            displayMax=required;scaleStart=required;scaleTarget=required;
        }else{
            scaleStart=displayMax;
            scaleTarget=required>displayMax?required:
                required<displayMax*.70f?required:displayMax;
            // Expand immediately so the new spike fits from the first frame.
            if(required>displayMax){
                displayMax=required;
                scaleStart=required;
            }
        }
        points=fresh;
        // Resize only when the sample window length changes, not on each frame.
        if(animatedPoints.length!=fresh.length) animatedPoints=new float[fresh.length];
        accent=color;bg=background;
        if(animator!=null)animator.cancel();
        boolean animate=AppPrefs.bool(getContext(),"motion",true)&&fresh.length>0
            &&(newSample||Math.abs(scaleTarget-scaleStart)>0.01f);
        if(animate){
            progress=0f;animator=ValueAnimator.ofFloat(0f,1f);animator.setDuration(220);
            animator.setInterpolator(new DecelerateInterpolator(1.2f));
            animator.addUpdateListener(v->{
                progress=(Float)v.getAnimatedValue();
                displayMax=scaleStart+(scaleTarget-scaleStart)*progress;
                invalidate();
            });
            animator.start();
        }else{
            progress=1f;displayMax=scaleTarget;
        }
        invalidate();
    }
    @Override protected void onDraw(Canvas canvas){super.onDraw(canvas);
        float[] animated=points;
        if(points.length>0&&progress<1f&&Float.isFinite(previous)&&previous>=0&&Float.isFinite(points[points.length-1])&&points[points.length-1]>=0){
            System.arraycopy(points,0,animatedPoints,0,points.length);
            animated=animatedPoints;
            animated[points.length-1]=previous+(points[points.length-1]-previous)*progress;
        }
        renderWithScale(canvas,getWidth(),getHeight(),animated,accent,bg,displayMax,paint,fillPath);
    }
    /** Fixed autoscale for exports and screenshots, independent of live animations. */
    public static void render(Canvas c,int w,int h,float[] v,int accent,int background){
        renderWithScale(c,w,h,v,accent,background,axisMaximum(v));
    }
    private static float axisMaximum(float[] v){
        float highest=30f;
        for(float r:v)if(Float.isFinite(r)&&r>highest)highest=r;
        double power=Math.pow(10,Math.floor(Math.log10(highest/3.0)));
        float step=(float)(Math.ceil((highest*1.14/3.0)/power)*power);
        return Math.max(3f,step*3f);
    }
    private static void renderWithScale(Canvas c,int w,int h,float[] v,int accent,int background,float scale){
        renderWithScale(c,w,h,v,accent,background,scale,new Paint(Paint.ANTI_ALIAS_FLAG),new Path());
    }
    private static void renderWithScale(Canvas c,int w,int h,float[] v,int accent,int background,float scale,Paint p,Path area){
        if(w<=0||h<=0)return;
        // Live drawing reuses scratch objects; reset state left by the previous frame.
        p.reset();p.setAntiAlias(true);
        area.rewind();
        c.drawColor(background);
        float density=h/145f;
        float left=38*density,right=w-13*density,top=15*density,bottom=h-23*density;
        if(right<=left+5||bottom<=top+5)return;
        float max=Float.isFinite(scale)&&scale>0?scale:axisMaximum(v);
        p.setStrokeWidth(Math.max(1f,.65f*density));
        for(int k=0;k<=3;k++){
            float y=top+(bottom-top)*k/3f;
            p.setColor(0xff28303a);c.drawLine(left,y,right,y,p);
            p.setColor(0xff8b98a5);p.setTextSize(10*density);
            c.drawText(String.format(Locale.US,"%.0f",max*(3-k)/3),4*density,y+3*density,p);
        }
        if(v.length==0){p.setColor(0xff9ba8b1);p.setTextSize(12*density);
            c.drawText("Ожидание измерений",left+10*density,h/2f,p);return;}
        float spacing=v.length>1?(right-left)/(v.length-1):0;
        // Reuse the fill path across up to 500 samples instead of allocating
        // hundreds of short-lived Path objects on every animation frame.
        for(int i=0;i<v.length;i++){
            float x=v.length==1?left:left+i*spacing;
            if(!Float.isFinite(v[i])){
                // Malformed telemetry is unknown, never fabricate a loss or draw NaN coordinates.
                continue;
            }
            if(v[i]==-2f){
                // A real reply bounded by "<1 ms", not a loss and not
                // an invented 0 or 1 ms measurement. Hollow marker, no line.
                p.setStyle(Paint.Style.STROKE);
                p.setColor(QualityColors.GREEN);
                p.setStrokeWidth(Math.max(1.5f,1.7f*density));
                c.drawCircle(x,bottom-4*density,2.7f*density,p);
                p.setStyle(Paint.Style.FILL);
                continue;
            }
            if(v[i]<0){
                // Only the explicit loss sentinel represents a confirmed timeout.
                // Unknown negative values must not become red loss markers.
                if(v[i]!=-1f)continue;
                p.setColor(QualityColors.RED);p.setStrokeWidth(1.6f*density);
                c.drawLine(x-3*density,bottom-5*density,x+3*density,bottom+1*density,p);
                c.drawLine(x+3*density,bottom-5*density,x-3*density,bottom+1*density,p);
                continue;
            }
            float y=bottom-(bottom-top)*Math.min(1f,Math.max(0,v[i]/max));
            int color=QualityColors.rtt(v[i]);
            // A measured reply between gaps has no connecting segment.
            // Keep it visible even after a newer sample arrives.
            boolean connectedBefore=i>0&&Float.isFinite(v[i-1])&&v[i-1]>=0;
            boolean connectedAfter=i+1<v.length&&Float.isFinite(v[i+1])&&v[i+1]>=0;
            if(i<v.length-1&&!connectedBefore&&!connectedAfter){
                p.setStyle(Paint.Style.FILL);p.setColor(color);
                c.drawCircle(x,y,Math.max(1.5f,2.2f*density),p);
            }
            if(i>0&&Float.isFinite(v[i-1])&&v[i-1]>=0){
                float px=left+(i-1)*spacing;
                float py=bottom-(bottom-top)*Math.min(1f,Math.max(0,v[i-1]/max));
                area.rewind();area.moveTo(px,bottom);area.lineTo(px,py);area.lineTo(x,y);area.lineTo(x,bottom);area.close();
                p.setStyle(Paint.Style.FILL);p.setColor((color&0x00ffffff)|0x1D000000);
                c.drawPath(area,p);
                p.setStrokeCap(Paint.Cap.ROUND);
                p.setStrokeWidth(Math.max(4f,4.4f*density));p.setColor((color&0x00ffffff)|0x26000000);
                c.drawLine(px,py,x,y,p);
                p.setStrokeWidth(Math.max(1.7f,2f*density));p.setColor(QualityColors.blend(QualityColors.rtt(v[i-1]),color,.5f));
                c.drawLine(px,py,x,y,p);
            }
        }
        // Highlight only the actual latest sample. Searching backward for the
        // last successful reply incorrectly makes an older point look current
        // after a timeout or an unclassified ICMP error.
        int latest=v.length-1;
        if(Float.isFinite(v[latest])&&(v[latest]>=0||v[latest]==-2f)){
            int i=latest;
            float x=v.length==1?left:left+i*spacing;
            if(v[i]==-2f){
                // Emphasize the most recent bounded success without using
                // a fictitious point on the RTT scale.
                p.setColor(QualityColors.GREEN);
                p.setStyle(Paint.Style.STROKE);
                p.setStrokeWidth(Math.max(1.5f,1.7f*density));
                c.drawCircle(x,bottom-4*density,5.5f*density,p);
                p.setStyle(Paint.Style.FILL);
            }else{
                float y=bottom-(bottom-top)*Math.min(1f,Math.max(0,v[i]/max));
                int col=QualityColors.rtt(v[i]);
                p.setColor((col&0x00ffffff)|0x35000000);c.drawCircle(x,y,6*density,p);
                p.setColor(col);c.drawCircle(x,y,3*density,p);
            }
        }
        p.setColor(0xff8b98a5);p.setTextSize(10*density);
        c.drawText("0",left,h-5*density,p);
        String label=v.length+" пак.";c.drawText(label,right-p.measureText(label),h-5*density,p);
    }
}
