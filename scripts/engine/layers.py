"""Generic, JSON-driven element library shared by all style templates.
Coordinates are in design units of a 1024-wide canvas (scaled by ctx.W/1024). Times are absolute seconds.
Element common keys: type, t0, t1, x, y, fi (fade in s), fo (fade out s), anim_in, anim_out, color, a."""
import skia, math, numpy as np, random
from functools import lru_cache
from .core import *

def U(ctx): return ctx.W/1024.

# ---------------- glyph point sampling for particle text ----------------
@lru_cache(256)
def glyph_points(text,fontname,size,weight,vertical,n,seed=0):
    f=font(fontname,size,weight)
    if vertical:
        w=int(size*1.3); h=int(size*1.05*len(text)+size*.5)
    else:
        w=int(f.measureText(text)+size); h=int(size*1.6)
    s=skia.Surface(max(w,4),max(h,4)); c=s.getCanvas(); c.clear(0)
    p=paint('#ffffff')
    if vertical:
        for i,ch in enumerate(text):
            c.drawString(ch,w/2-f.measureText(ch)/2,size*(i+1)*1.05,f,p)
    else:
        c.drawString(text,size/2,size*1.15,f,p)
    a=np.asarray(s.makeImageSnapshot().toarray())[:,:,3]
    ys,xs=np.nonzero(a>128)
    if len(xs)==0: return np.zeros((0,2)),w,h
    rng=np.random.default_rng(seed); idx=rng.choice(len(xs),min(n,len(xs)),replace=False)
    pts=np.stack([xs[idx]-(size/2 if not vertical else w/2),ys[idx]],1).astype(float)
    return pts,w,h

def _text_block(ctx,e,t,a):
    """draw text element. supports horizontal/vertical, runs (rich), spacing."""
    c=ctx.c; u=U(ctx)
    size=e.get('size',40)*u; fn=e.get('font','serif'); wt=e.get('weight')
    f=font(fn,round(size,1),wt)
    text=e['text']; col=e.get('color','#ffffff'); x=e.get('x',512)*u; y=e.get('y',288)*u
    vertical=e.get('vertical',False); spacing=e.get('spacing',0)*u; align=e.get('align','center')
    glow=e.get('glow',0)*u; lh=e.get('line_height',1.08)
    ain=e.get('anim_in','fade'); t0=e['t0']; dur_in=e.get('fi',.5)
    # per-character reveal count
    nchar=len(text); reveal=nchar
    if ain=='type':
        rate=e.get('cps',8.); reveal=int(clamp((t-t0)*rate,0,nchar)); char_fade=e.get('char_fade',.25)
    hl=e.get('highlight',{})  # {"char_index_range": color} via list [[i0,i1,color]]
    def color_at(i):
        for r in e.get('hl',[]):
            if r[0]<=i<r[1]: return r[2]
        return col
    def char_alpha(i):
        if ain!='type': return a
        ct=t0+i/e.get('cps',8.)
        return a*ease_out_cubic(prog(t,ct,e.get('char_fade',.25)))
    if vertical:
        yy=y
        for i,ch in enumerate(text):
            ca=char_alpha(i)
            if ca>0: draw_text(c,ch,x,yy+size,f,color_at(i),ca,'center',glow=glow,stroke=e.get('stroke'))
            yy+=size*lh
    else:
        if e.get('hl') or ain=='type':
            tot=f.measureText(text)+spacing*(nchar-1)
            xx= x-tot/2 if align=='center' else x-tot if align=='right' else x
            for i,ch in enumerate(text):
                ca=char_alpha(i)
                if ca>0: draw_text(c,ch,xx,y,f,color_at(i),ca,'left',glow=glow,stroke=e.get('stroke'))
                xx+=f.measureText(ch)+spacing
        else:
            draw_text(c,text,x,y,f,col,a,align,glow=glow,spacing=spacing,stroke=e.get('stroke'),glow_color=e.get('glow_color'))

def el_text(ctx,e,t,frame):
    t0,t1=e['t0'],e['t1']
    if t<t0-1e-6 or t>t1+e.get('linger',0): return
    c=ctx.c; u=U(ctx)
    ain=e.get('anim_in','fade'); aout=e.get('anim_out','fade')
    fi=e.get('fi',.5); fo=e.get('fo',.4)
    pin=prog(t,t0,fi); pout=prog(t,t1-fo,fo) if fo>0 else 0.
    a=e.get('a',1.)
    # ---- particle assembly / dispersal ----
    if ain=='particles' and pin<1 or aout=='disperse' and pout>0:
        size=e.get('size',40); vertical=e.get('vertical',False)
        n=e.get('n',1600)
        pts,w,h=glyph_points(e['text'],e.get('font','serif'),round(size*u,1),e.get('weight'),vertical,n,e.get('seed',1))
        if len(pts)==0: return
        rng=np.random.default_rng(e.get('seed',1)+7)
        x=e.get('x',512)*u; y=e.get('y',288)*u
        if vertical: ox,oy=x,y
        else:
            f=font(e.get('font','serif'),round(size*u,1),e.get('weight')); tw=f.measureText(e['text'])
            al=e.get('align','center'); ox=x-(tw/2 if al=='center' else tw if al=='right' else 0); oy=y-size*u*1.15
        target=pts+[ox,oy]
        spread=e.get('spread',260)*u
        if ain=='particles' and pin<1:
            k=ease_in_out_cubic(pin); src=target+rng.normal(0,spread,target.shape)*np.array(e.get('spread_xy',[1,1]))
            P=src+(target-src)*k; alpha=a*(0.35+0.65*k); dot=max(1.,size*u/38)
            if pin>.85:  # crossfade into crisp text
                ee=dict(e); ee['anim_in']='none'; _text_block(ctx,ee,t,a*(pin-.85)/.15)
        else:
            k=ease_in_out_cubic(pout); wind=np.array(e.get('wind',[1.0,-0.3]))*spread*1.6
            jitter=rng.normal(0,spread*.5,target.shape)
            P=target+(wind+jitter)*k*(0.4+rng.random((len(target),1))); alpha=a*(1-k); dot=max(1.,size*u/38)
            if pout<.15:
                ee=dict(e); ee['anim_in']='none'; _text_block(ctx,ee,t,a*(1-pout/.15))
        col=hexc(e.get('pcolor',e.get('color','#ffffff')),alpha)
        p=skia.Paint(AntiAlias=True,Color=col)
        c.drawPoints(skia.Canvas.kPoints_PointMode,[skia.Point(float(px),float(py)) for px,py in P],paint(e.get('pcolor',e.get('color','#ffffff')),alpha,stroke=dot*1.6))
        return
    # ---- regular envelope ----
    alpha=a
    if ain in ('fade','blur','rise','scale','drop','type','none','particles'):
        if ain!='type' and ain!='none': alpha*=ease_out_cubic(pin)
    if aout in ('fade','blur','disperse') and fo>0: alpha*=1-pout
    if alpha<=0.003: return
    c.save()
    x=e.get('x',512)*u; y=e.get('y',288)*u
    if ain=='rise': c.translate(0,(1-ease_out_cubic(pin))*e.get('rise',18)*u)
    if ain=='scale':
        s=lerp(e.get('scale_from',1.25),1,ease_out_expo(pin)); c.translate(x,y); c.scale(s,s); c.translate(-x,-y)
    if ain=='drop':
        k=ease_out_back(pin,1.2); c.translate(0,-(1-k)*e.get('drop',120)*u)
    if 'zoom' in e:  # slow push over life [s0,s1]
        z0,z1=e['zoom']; s=lerp(z0,z1,prog(t,t0,t1-t0)**e.get('zoom_pow',1)); zx,zy=[v*u for v in e.get('zoom_c',[x/u,y/u])]; c.translate(zx,zy); c.scale(s,s); c.translate(-zx,-zy)
        if 0: c.translate(x,y); c.scale(s,s); c.translate(-x,-y)
    blur=0
    if ain=='blur' and pin<1: blur=(1-pin)*e.get('blur',10)*u
    if aout=='blur' and pout>0: blur=max(blur,pout*e.get('blur',10)*u)
    if blur>0.3:
        p=skia.Paint(); p.setImageFilter(skia.ImageFilters.Blur(blur,blur)); c.saveLayer(None,p)
    _text_block(ctx,e,t,alpha)
    if blur>0.3: c.restore()
    c.restore()

def el_rect(ctx,e,t,frame):
    a=fade_env(t,e['t0'],e['t1'],e.get('fi',.3),e.get('fo',.3))*e.get('a',1)
    if a<=0: return
    u=U(ctx); x,y,w,h=[v*u for v in e['rect']]
    if e.get('grow'):  # grow along axis
        k=ease_out_cubic(prog(t,e['t0'],e.get('grow_dur',.6)))
        if e['grow']=='x': w*=k
        else: h*=k
    rrect(ctx.c,x,y,w,h,e.get('r',0)*u,fill=e.get('fill'),stroke=e.get('stroke'),a=a,sw=e.get('sw',1.5)*u,blur=e.get('blur',0)*u)

def el_line(ctx,e,t,frame):
    a=fade_env(t,e['t0'],e['t1'],e.get('fi',.3),e.get('fo',.3))*e.get('a',1)
    if a<=0: return
    u=U(ctx); x0,y0,x1,y1=[v*u for v in e['pts']]
    k=ease_in_out_cubic(prog(t,e['t0'],e.get('draw',.8))) if e.get('draw') else 1
    line(ctx.c,x0,y0,lerp(x0,x1,k),lerp(y0,y1,k),e.get('color','#ffffff'),a,e.get('w',2)*u,glow=e.get('glow',0)*u)

def el_circle(ctx,e,t,frame):
    a=fade_env(t,e['t0'],e['t1'],e.get('fi',.3),e.get('fo',.3))*e.get('a',1)
    if a<=0: return
    u=U(ctx); c=ctx.c; x,y,r=e['x']*u,e['y']*u,e['r']*u
    if e.get('draw'):
        k=ease_in_out_cubic(prog(t,e['t0'],e['draw']))
        p=paint(e.get('color','#ffffff'),a,stroke=e.get('w',2)*u); p.setStrokeCap(skia.Paint.kRound_Cap)
        path=skia.Path(); path.addArc(skia.Rect.MakeLTRB(x-r*e.get('sx',1),y-r,x+r*e.get('sx',1),y+r),e.get('start',-90),360*k); c.drawPath(path,p)
    elif e.get('glowdot'):
        glow_dot(c,x,y,r,e.get('color','#ffffff'),a,e.get('halo',6))
    else:
        c.drawCircle(x,y,r,paint(e.get('color','#ffffff'),a,stroke=(e.get('w')*u if e.get('w') else None),blur=e.get('blur',0)*u))

def el_image(ctx,e,t,frame):
    """image plate (AI-image hook). keys: src (path rel. to script dir), kenburns [s0,s1], gray"""
    a=fade_env(t,e['t0'],e['t1'],e.get('fi',.5),e.get('fo',.5))*e.get('a',1)
    if a<=0: return
    k=prog(t,e['t0'],e['t1']-e['t0']); z0,z1=e.get('kenburns',[1,1])
    draw_image_cover(ctx.c,e['_abs'],ctx.W,ctx.H,a,lerp(z0,z1,k),e.get('cx',.5),e.get('cy',.5),e.get('gray',False))

def el_counter(ctx,e,t,frame):
    a=fade_env(t,e['t0'],e['t1'],e.get('fi',.2),e.get('fo',.3))*e.get('a',1)
    if a<=0: return
    k=ease_out_cubic(prog(t,e['t0'],e.get('count_dur',1.2))); v=lerp(e['from'],e['to'],k)
    s=e.get('fmt','{:.0f}').format(v)
    ee=dict(e,text=s,anim_in='none',anim_out='none'); _text_block(ctx,ee,t,a)

def el_precip(ctx,e,t,frame):
    """rain / snow / dust overlay"""
    a=fade_env(t,e['t0'],e['t1'],e.get('fi',.5),e.get('fo',.5))*e.get('a',1)
    if a<=0: return
    u=U(ctx); c=ctx.c; rng=random.Random(e.get('seed',3)); kind=e.get('kind','rain')
    n=e.get('n',160); W,H=ctx.W,ctx.H
    for i in range(n):
        x0=rng.random()*W*1.2; sp=rng.uniform(.6,1.4); ph=rng.random()
        if kind=='rain':
            L=rng.uniform(14,38)*u; v=H*1.6*sp; y=((ph*H*1.3+v*t)%(H*1.3))-H*.15; x=x0-y*.12
            line(c,x,y,x-L*.12,y+L,'#ffffff',a*rng.uniform(.15,.55),rng.uniform(.6,1.6)*u,cap=False)
        else:
            v=H*.12*sp; y=(ph*H*1.1+v*t)%(H*1.1); x=x0+math.sin(t*.8+i)*12*u
            c.drawCircle(x,y,rng.uniform(.6,2.2)*u,paint(e.get('color','#ffffff'),a*rng.uniform(.3,.9)))

REGISTRY={'text':el_text,'rect':el_rect,'line':el_line,'circle':el_circle,'image':el_image,'counter':el_counter,'precip':el_precip}

def draw_elements(ctx,elements,t,frame,extra=None):
    reg=dict(REGISTRY); reg.update(extra or {})
    for e in elements:
        if t<e.get('t0',0)-0.001 or t>e.get('t1',1e9)+e.get('linger',0)+0.001: continue
        fn=reg.get(e['type'])
        if fn: fn(ctx,e,t,frame)

def wrap_markup(text,f,maxw,marks='[]{}'):
    """greedy CJK-friendly wrap of each '\\n' line to maxw px, ignoring markup chars ([..] {..}) for width
    and re-opening an unclosed run on the next line. Keeps explicit line breaks."""
    opens=marks[0::2]; closes=marks[1::2]; out=[]
    for ln in text.split('\n'):
        cur=''; w=0; mode=None
        for ch in ln:
            if ch in opens: mode=ch; cur+=ch; continue
            if ch in closes: mode=None; cur+=ch; continue
            cw=f.measureText(ch)
            if w+cw>maxw and cur and ch not in '，。、；：？！,.;:?!”）》':
                if mode: cur+=closes[opens.index(mode)]
                out.append(cur); cur=(mode or ''); w=0
            cur+=ch; w+=cw
        out.append(cur)
    return out
