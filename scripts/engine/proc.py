"""Procedural illustration library (all code-drawn): bamboo forest (3D, fog), straw-hat walker with walk cycle,
water planes, mist, fbm clouds, moon+sea, lychee sphere rain (3D), ink mountains (山水), ink bird (brush strokes),
city skyline, rain/snow statistics-driven precipitation. Deterministic in (t, seed)."""
import math, random, numpy as np, skia, cv2
from functools import lru_cache
from .core import hexc, paint, blurred_layer, lerp, prog, ease_in_out_cubic
from . import three as T

# ---------- noise ----------
def fbm(h,w,seed=0,octaves=(64,32,16,8,4),gain=.55):
    rng=np.random.default_rng(seed); n=np.zeros((h,w))
    for i,s in enumerate(octaves):
        g=rng.normal(0,1,(h//s+3,w//s+3)); n+=cv2.resize(g,(w+ (w//s+3)*0,h),interpolation=cv2.INTER_CUBIC)[:h,:w]*gain**i if False else cv2.resize(g,(w,h),interpolation=cv2.INTER_CUBIC)*gain**i
    n=(n-n.min())/(n.max()-n.min()+1e-9); return n
def to_img(rgba): return skia.Image.fromarray(np.ascontiguousarray(rgba.astype(np.uint8)),colorType=skia.kRGBA_8888_ColorType)
@lru_cache(16)
def noise_tex(w,h,seed,lo,hi,alpha=False,streak=1):
    n=fbm(h*streak,w,seed)[::streak] if streak>1 else fbm(h,w,seed)
    if alpha: n=np.clip((n-.3)*1.8,0,1)**1.1
    lo=np.array(lo,float); hi=np.array(hi,float); rgb=lo+(hi-lo)*n[...,None]
    a=(n*255) if alpha else np.full((h,w),255.)
    return to_img(np.dstack([rgb,a]))

def vgrad(c,W,H,stops,y0=0,y1=None):
    y1=H if y1 is None else y1; cols=[hexc(s[1],s[2] if len(s)>2 else 1) for s in stops]; pos=[s[0] for s in stops]
    sh=skia.GradientShader.MakeLinear([(0,y0),(0,y1)],cols,pos); p=skia.Paint(); p.setShader(sh); c.drawRect(skia.Rect.MakeLTRB(0,y0,W,y1),p)

# ---------- walker (straw hat traveler, 竹杖芒鞋) ----------
def walker(c,x,y,h,t,col='#111111',a=1.,speed=1.6,staff=True,walking=True):
    """x,y = feet center; h = figure height px. 2-beat walk cycle; hat (斗笠) cone, cloak trapezoid, staff."""
    ph=t*speed*2*math.pi if walking else 0; sw=math.sin(ph)*h*.07; bob=abs(math.cos(ph))*h*.012
    p=paint(col,a); top=y-h-bob
    hat=skia.Path(); hat.moveTo(x-h*.21,top+h*.17); hat.lineTo(x,top); hat.lineTo(x+h*.21,top+h*.17); hat.close(); c.drawPath(hat,p)
    c.drawCircle(x,top+h*.2,h*.055,p)
    body=skia.Path(); body.moveTo(x-h*.07,top+h*.22); body.lineTo(x+h*.07,top+h*.22); body.lineTo(x+h*.13,top+h*.72); body.lineTo(x-h*.13,top+h*.72); body.close(); c.drawPath(body,p)
    lw=max(1,h*.035)
    c.drawLine(x-h*.04,top+h*.7,x-h*.04+sw,y,paint(col,a,stroke=lw)); c.drawLine(x+h*.04,top+h*.7,x+h*.04-sw,y,paint(col,a,stroke=lw))
    if staff: c.drawLine(x+h*.16,top+h*.35,x+h*.2+sw*.3,y+h*.01,paint(col,a,stroke=max(.8,h*.018)))

# ---------- bamboo forest (3D) ----------
def _leaf(c,x,y,L,ang,col,a):
    ca,sa=math.cos(ang),math.sin(ang); w=L*.18
    p=skia.Path(); p.moveTo(x,y); p.quadTo(x+ca*L*.5-sa*w,y+sa*L*.5+ca*w,x+ca*L,y+sa*L); p.quadTo(x+ca*L*.5+sa*w,y+sa*L*.5-ca*w,x,y); c.drawPath(p,paint(col,a))
def bamboo_forest(c,W,H,t,mode='rain',seed=3,a=1.,cam_z=0.,walker_at=None,leaves=True,n=330,tex=None):
    """mode: 'rain' (dark, grey fog), 'snow' (very dark), 'mist' (bright paper fog). Camera dolly via cam_z."""
    sky={'rain':[(0,'#2b2b2b'),(.55,'#5a5a5a'),(.75,'#3a3a3a'),(1,'#0c0c0c')],
         'snow':[(0,'#161616'),(.55,'#3a3a3a'),(.72,'#202020'),(1,'#050505')],
         'mist':[(0,'#f2f2f0'),(.6,'#e8e8e6'),(1,'#d6d6d4')]}[mode]
    vgrad(c,W,H,sky)
    if tex: tex_layer(c,load_tex(tex,W,H,contrast=1.2),W,H,t,.9 if mode=='mist' else .25,'kMultiply' if mode=='mist' else 'kScreen',drift=.5*W/1024,zoom=(1.,1.05),dur=4)
    fogc={'rain':'#6a6a6a','snow':'#3c3c3c','mist':'#ecebe8'}[mode]; stalk={'rain':'#0e0e0e','snow':'#0a0a0a','mist':'#151515'}[mode]
    cam=T.Camera(pos=(0,1.6,-cam_z),target=(0,1.9,-cam_z-10),fov=55,W=W,H=H); fog=dict(near=2.5,density=.09 if mode!='mist' else .14)
    rng=random.Random(seed); ops=[]
    for i in range(n):
        X=rng.uniform(-14,14); Z=-rng.uniform(1.2,30)
        if abs(X)<.9 and Z>-6: X+=2.2*(1 if X>=0 else -1)          # keep a path open in the middle
        lean=rng.uniform(-.05,.05); r=rng.uniform(.04,.08)
        ops.append(T.cylinder_op((X,-.2,Z),(X+lean*12,12,Z),r,cam,col=stalk,fog=fog,fog_col=fogc,a=a,nodes=7))
        if leaves and rng.random()<.85:
            for k in range(rng.randint(3,6)):
                hy=rng.uniform(3.5,9); P,z=cam.proj(np.array([[X+lean*hy,hy,Z]]))
                d=float(z[0]); fk=T.fogk(d,fog); col=T.mix(stalk,fogc,fk); L=cam.f*.55/d
                px,py=P[0]; sd=rng.random()
                def lf(cv,px=px,py=py,L=L,col=col,sd=sd):
                    r2=random.Random(int(sd*1e6))
                    for j in range(r2.randint(5,9)):
                        _leaf(cv,px,py,L*r2.uniform(.6,1.1),math.radians(r2.uniform(20,160)),col,a*.95)
                ops.append((d-.01,lf))
    T.render_ops(c,ops)
    # ground haze band
    vgrad(c,W,H,[(0,fogc,0),(.5,fogc,.55 if mode!='mist' else .4),(1,fogc,0)],H*.5,H*.8)
    if mode!='mist': vgrad(c,W,H,[(0,'#000000',0),(1,'#000000',.85)],H*.72,H)
    if walker_at: walker(c,walker_at[0]*W/1024,walker_at[1]*W/1024,walker_at[2]*W/1024,t,col='#0b0b0b' if mode!='mist' else '#141414',a=a)

# ---------- precipitation with explicit statistics ----------
def precip(c,W,H,t,kind='rain',density=170,speed=900,length=26,width=1.1,bright=.55,seed=1,wind=.12,size=(1,3)):
    """rain: streaks (density per frame, px/s speed, streak length px) ; snow: dots drifting. Stats tunable to match reference."""
    rng=random.Random(seed); u=W/1024
    for i in range(density):
        x0=rng.random()*W*1.2-W*.1; ph=rng.random(); sp=speed*rng.uniform(.7,1.3)*u
        if kind=='rain':
            y=((ph*H*1.3+t*sp)%(H*1.3))-H*.15; x=x0+(y)*wind; L=length*rng.uniform(.6,1.4)*u
            c.drawLine(x,y,x-L*wind,y-L,paint('#ffffff',bright*rng.uniform(.35,1),stroke=width*u*rng.uniform(.7,1.3)))
        else:
            y=((ph*H*1.2+t*sp*.08)%(H*1.2))-H*.1; x=x0+math.sin(t*.8+i)*8*u
            c.drawCircle(x,y,rng.uniform(*size)*u*.5,paint('#ffffff',bright*rng.uniform(.4,1)))

# ---------- water / mist / sea ----------
def water(c,W,H,hz,t,top='#9a9a98',bot='#5a5a58',lines=90,line_col='#ffffff',line_a=.12,seed=2,speed=.4):
    vgrad(c,W,H,[(0,top),(1,bot)],hz,H); rng=random.Random(seed)
    for i in range(lines):
        z=(i+1)/lines; y=hz+(H-hz)*z**2.2; seg=rng.uniform(20,140)*z*W/1024
        for k in range(int(6+z*10)):
            x=(rng.random()*W*1.4-W*.2+math.sin(t*speed+i*.7+k)*20*z)
            c.drawLine(x,y,x+seg,y,paint(line_col if rng.random()<.6 else '#000000',line_a*rng.uniform(.4,1),stroke=max(.6,1.6*z)*W/1024))
def mist(c,W,H,y,h,col='#f4f4f2',a=.8,t=0,drift=6):
    def fn():
        for k in range(6):
            yy=y+(k-2.5)*h*.25+math.sin(t*.2+k)*drift; c.drawOval(skia.Rect.MakeXYWH(-W*.2+math.sin(t*.1+k*1.3)*40,yy-h*.3,W*1.4,h*.6),paint(col,a*.35))
    blurred_layer(c,fn,h*.35)
def clouds(c,W,H,t,y0,y1,seed=5,col_lo=(20,20,20),col_hi=(170,170,170),drift=4,a=1.):
    h=int(y1-y0); img=noise_tex(int(W*1.5),max(8,h),seed,col_lo,col_hi,True,4)
    p=skia.Paint(); p.setAlphaf(a); c.save(); c.clipRect(skia.Rect.MakeLTRB(0,y0,W,y1))
    off=-(t*drift)%(img.width())
    for k in (-1,0,1): c.drawImage(img,off+k*img.width(),y0,skia.SamplingOptions(skia.FilterMode.kLinear),p)
    c.restore()
def moon(c,x,y,r,a=1.,halo=2.2,col='#f6f6f2'):
    sh=skia.GradientShader.MakeRadial((x,y),r*halo,[hexc('#ffffff',.45*a),hexc('#ffffff',0)]); p=skia.Paint(); p.setShader(sh); c.drawCircle(x,y,r*halo,p)
    sh2=skia.GradientShader.MakeRadial((x-r*.25,y-r*.25),r*1.2,[hexc('#ffffff',a),hexc(col,a),hexc('#c8c8c0',a)],[0,.6,1]); q=skia.Paint(AntiAlias=True); q.setShader(sh2); c.drawCircle(x,y,r,q)
_CLUMP={}
def cloud_clumps(W,H,hz,mx,my,tex=None,seed=11):
    """broken cumulus bank (ref 38-46s): thresholded fbm clumps, flattened toward horizon, detail from AI texture if present,
    rim-lit near the moon. returns RGBA skia image (1.3W wide for drift)"""
    key=(W,H,int(hz),int(mx),int(my),tex)
    if key in _CLUMP: return _CLUMP[key]
    w,h=int(W*1.3),int(hz)
    n=fbm(h*2,w,seed,octaves=(96,48,24,12,6,3),gain=.6)[::2]
    yy=np.linspace(0,1,h)[:,None]; n=n*(.75+.35*yy)                        # denser toward horizon
    m=cv2.GaussianBlur(np.clip((n-.46)/.22,0,1)**1.1,(0,0),2.2)
    det=fbm(h,w,seed+3,octaves=(8,4,2),gain=.7)
    if tex:
        tg=load_tex(tex,w,h,contrast=1.6,gamma=.85,crop=(0,.02,1,.55))
        if tg is not None:
            arr=tg.toarray()[:,:,0].astype(float)/255.; det=.5*det+.5*cv2.GaussianBlur(arr,(0,0),1.0)/max(arr.max(),1e-3)
    xx=np.arange(w)[None,:]; d=np.hypot((xx-(mx+W*.15))/W,(np.arange(h)[:,None]-my)/H)
    rim=np.exp(-d*4.5); edge=np.clip(m*(1-m)*4,0,1)
    v=14+60*det+160*rim*(.35+edge)+45*edge*det
    al=np.clip(m*.95,0,1)*255
    img=to_img(np.dstack([v,v,v*1.02,al]).clip(0,255)); _CLUMP[key]=img; return img
def moon_sea(c,W,H,t,mx,my,mr,hz=None,a=1.,tex=None):
    hz=hz or H*.56
    vgrad(c,W,H,[(0,'#050505'),(.7,'#151515'),(1,'#262626')],0,hz)
    moon(c,mx,my,mr,a,halo=2.6)
    img=cloud_clumps(W,H,hz,mx,my,tex)
    off=-(W*.15)+((t*2.5*W/1024)%(W*.15)); p=skia.Paint(); p.setAlphaf(a)
    c.drawImage(img,off,0,skia.SamplingOptions(skia.FilterMode.kLinear),p)
    water(c,W,H,hz,t,top='#1c1c1c',bot='#080808',lines=80,line_a=.14)
    def ref():
        c.drawRect(skia.Rect.MakeXYWH(mx-mr*.22,hz,mr*.44,H-hz),paint('#ffffff',.85))
    blurred_layer(c,ref,mr*.1)

# ---------- optional AI base textures (code-transformed) ----------
_TEX={}
def load_tex(path,W,H,gray=True,denoise=True,contrast=1.,gamma=1.,crop=None):
    """load an AI texture, upscale (cubic) + edge-preserving denoise, grayscale/contrast in code. None if missing."""
    import os
    key=(path,W,H,gray,denoise,contrast,gamma,crop)
    if key in _TEX: return _TEX[key]
    im=None
    if path and os.path.exists(path):
        a=cv2.cvtColor(cv2.imread(path),cv2.COLOR_BGR2RGB).astype(np.float32)
        if crop: h0,w0=a.shape[:2]; a=a[int(crop[1]*h0):int(crop[3]*h0),int(crop[0]*w0):int(crop[2]*w0)]
        a=cv2.resize(a,(W,H),interpolation=cv2.INTER_CUBIC)
        if denoise: a=cv2.bilateralFilter(a,7,18,7)
        if gray: g=a.mean(2,keepdims=True); a=np.repeat(g,3,2)
        a=((a/255.)**gamma-.5)*contrast+.5
        a=(a*255).clip(0,255)
        im=to_img(np.dstack([a,np.full(a.shape[:2],255.)]))
    _TEX[key]=im; return im
def tex_layer(c,img,W,H,t=0,a=1.,blend=None,drift=0.,zoom=(1.,1.),dur=1.,y0=0,y1=None):
    if img is None: return False
    y1=H if y1 is None else y1; k=min(1,t/max(dur,1e-3)); z=lerp(zoom[0],zoom[1],k)
    p=skia.Paint(); p.setAlphaf(a)
    if blend: p.setBlendMode(getattr(skia.BlendMode,blend))
    c.save(); c.clipRect(skia.Rect.MakeLTRB(0,y0,W,y1)); c.translate(W/2-t*drift,H/2); c.scale(z*1.04,z*1.04); c.translate(-W/2,-H/2)
    c.drawImage(img,0,0,skia.SamplingOptions(skia.FilterMode.kLinear),p); c.restore(); return True

# ---------- 3D lychee field ----------
@lru_cache(2)
def lychee_tex(seed=4):
    n=fbm(256,256,seed,octaves=(4,2)); bumps=.62+.38*n
    rgb=np.dstack([bumps*255,bumps*235,bumps*225]); return to_img(np.dstack([rgb,np.full((256,256),255.)]))
def lychee_rain(c,W,H,t,t0=0,bg='#f2dccb',n=30,seed=9,fall=.35):
    vgrad(c,W,H,[(0,'#f6e6da'),(1,bg)]); cam=T.Camera(pos=(0,0,8),target=(0,0,0),fov=45,W=W,H=H)
    rng=random.Random(seed); ops=[]
    for i in range(n):
        X,Y,Z=rng.uniform(-4.8,4.8),rng.uniform(-2.5,4.5),rng.uniform(-3,2.5); r=rng.uniform(.95,1.5)
        Y-= (t-t0)*fall*rng.uniform(.6,1.4)
        ops.append(T.sphere_op((X,Y,Z),r,cam,col='#d8402a',tex=lychee_tex()))
    T.render_ops(c,ops)

# ---------- ink mountains (山水) ----------
def ridge(x,seed,oct=5):
    rng=np.random.default_rng(seed); y=np.zeros_like(x)
    for k in range(oct):
        f=2**k; y+=np.sin(x*f*rng.uniform(.8,1.2)*2*math.pi+rng.uniform(0,6.28))/f**1.1
    return y
def ink_mountains(c,W,H,layers=4,base=.62,amp=.18,seed=1,ink='#1d1b19',paper='#f4f0e8',t=0,a=1.):
    xs=np.linspace(0,1,240)
    for i in range(layers):
        k=i/(max(1,layers-1)); col=T.mix(paper,ink,.25+.7*k); yb=(base+.08*k)*H
        ys=yb-(ridge(xs+t*.002*(1+k),seed+i)*.5+.5)*amp*H*(1.2-.3*k)
        p=skia.Path(); p.moveTo(0,H)
        for x,y in zip(xs*W,ys): p.lineTo(x,y)
        p.lineTo(W,H); p.close()
        sh=skia.GradientShader.MakeLinear([(0,float(ys.min())),(0,yb+H*.2)],[hexc(col,a),hexc(paper,0)]); q=skia.Paint(AntiAlias=True); q.setShader(sh); c.drawPath(p,q)
def wire_mountains(c,W,H,t,y0=330,amp=60,rows=7,col='#5a8aa0',a=.5,seed=3):
    """info-style line mountains (thin cyan ridge lines)"""
    xs=np.linspace(0,1,200); u=W/1024
    for r in range(rows):
        ys=(y0+r*14-(ridge(xs+r*.07+t*.003,seed+r)*.5+.5)*amp*(1-r*.08))*u
        p=skia.Path(); p.moveTo(0,ys[0])
        for x,y in zip(xs*W,ys): p.lineTo(x,y)
        c.drawPath(p,paint(col,a*(1-r*.1),stroke=.8*u))

# ---------- ink bird (brush strokes) ----------
def brush(c,pts,w0,w1,col,a=1.):
    pts=np.asarray(pts,float); n=len(pts)
    for i in range(n-1):
        w=lerp(w0,w1,i/(n-1)); c.drawLine(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],paint(col,a,stroke=max(.5,w)))
def ink_bird(c,x,y,s,t,col='#1d1b19',a=1.,flap=2.2):
    ph=math.sin(t*flap*2*math.pi); up=ph*.6
    for side in (-1,1):
        P=[(x,y)]+[(x+side*s*k/6,y-s*(math.sin(k/6*math.pi)*.25+up*.55*k/6)) for k in range(1,7)]
        brush(c,P,s*.16,s*.02,col,a)
    brush(c,[(x-s*.25,y+s*.02),(x,y),(x+s*.3,y-s*.06)],s*.12,s*.05,col,a)

# ---------- city skyline ----------
def skyline(c,W,H,y,seed=4,col='#06080b',win='#d8c89a',win_a=.25,n=60,t=0):
    rng=random.Random(seed); u=W/1024; x=-10
    while x<1034:
        w=rng.uniform(14,46); h=rng.uniform(30,150)
        c.drawRect(skia.Rect.MakeXYWH(x*u,(y-h)*u,w*u,(h+300)*u),paint(col,.97))
        for wy in range(int(y-h+6),int(y),7):
            for wx in range(int(x+3),int(x+w-3),6):
                if rng.random()<.12: c.drawRect(skia.Rect.MakeXYWH(wx*u,wy*u,2*u,2.5*u),paint(win,win_a*(.6+.4*math.sin(t*.7+wx))))
        x+=w+rng.uniform(1,6)

# ---------- composed scenes used by templates ----------
def boat(c,x,y,s,col='#2a2a2a',a=1.):
    """long low wupeng boat: hull + arched mat cabin; s = half-length"""
    p=skia.Path(); p.moveTo(x-s,y-s*.04); p.quadTo(x,y+s*.12,x+s,y-s*.07); p.lineTo(x+s*.85,y+s*.04); p.quadTo(x,y+s*.14,x-s*.9,y+s*.03); p.close(); c.drawPath(p,paint(col,a))
    q=skia.Path(); q.moveTo(x-s*.35,y); q.quadTo(x-s*.05,y-s*.2,x+s*.3,y-s*.01); q.close(); c.drawPath(q,paint(col,a))
def river_snow(c,W,H,t,a=1.,tex=None):
    vgrad(c,W,H,[(0,'#9c9c9a'),(.35,'#d8d8d6'),(.55,'#e6e6e4'),(1,'#bdbdbb')])
    if tex_layer(c,load_tex(tex,W,H,contrast=1.1),W,H,t,.85,None,drift=.8*W/1024,zoom=(1.,1.04),dur=6): 
        mist(c,W,H,H*.5,H*.14,'#ffffff',.45,t); water(c,W,H,H*.62,t,top='#c8c8c6',bot='#7a7a78',lines=60,line_col='#ffffff',line_a=.10); return
    def cliff():
        p=skia.Path(); p.moveTo(W*.45,0); p.lineTo(W*.47,H*.28); p.lineTo(W*.5,H*.34); p.lineTo(W*.53,H*.24); p.lineTo(W*.56,0); p.close(); c.drawPath(p,paint('#6a6a68',.8))
    blurred_layer(c,cliff,6*W/1024)
    mist(c,W,H,H*.35,H*.4,'#f4f4f2',.9,t)
    water(c,W,H,H*.55,t,top='#c8c8c6',bot='#7a7a78',lines=110,line_col='#ffffff',line_a=.22)
    mist(c,W,H,H*.52,H*.12,'#ffffff',.8,t)
def lake_boat(c,W,H,t,a=1.):
    vgrad(c,W,H,[(0,'#f2f2f0'),(.45,'#e4e4e2'),(.6,'#d6d6d4'),(1,'#b4b4b2')])
    water(c,W,H,H*.6,t,top='#d4d4d2',bot='#a8a8a6',lines=70,line_col='#ffffff',line_a=.18,speed=.2)
    mist(c,W,H,H*.58,H*.1,'#f4f4f2',.7,t)
    bx=W*(.64+.003*t); boat(c,bx,H*.675,W*.085,'#3a3a3a'); walker(c,bx-W*.06,H*.668,W*.035,t,col='#1a1a1a',walking=False,staff=False)
