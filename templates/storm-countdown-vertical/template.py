"""#7 雷暴倒计时·竖屏 (storm-countdown-vertical) — ref 7694898938109505713《闪电从地面往上打》576x1024. Topic-agnostic.
Night-storm look: blue-violet sky gradient, drifting cloud texture, rain streaks, city skyline with lit windows + TV tower (red beacon).
Slow-motion "high-speed camera" HUD: corner brackets, 真实时间 + huge thin timer (keyframed) + unit, a status line (keyframed), ● 高速摄影 / 帧 counter,
altitude ticks. Big bold serif title + 1–2 small sub lines low on screen. Procedural lightning (stepped leader growing to a tip,
upward streamers, return stroke with flash/flicker), ice-crystal cloud interior, charge signs, big number, thunder rings, rows (3 秒 ≈ 1 公里),
night-side globe with city lights + live counter, inset head with standing hair. Design space 1024 x 1820 (U=W/1024)."""
import math, random, numpy as np, skia
from functools import lru_cache
from engine.core import *
from engine.layers import draw_elements, U, wrap_markup
from engine.proc import precip, clouds, fbm, to_img

WHITE='#f2f2fa'; SOFT='#c8cbe6'; DIMC='#8a8eb0'; VIOLET='#b8a8ff'; HOT='#f4f0ff'
def prepare(S): pass
def env(e,t,fi=.4,fo=.4): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def kf(keys,t,ease=True):
    """piecewise interpolation over [[t,v],...]; numbers or strings (strings step)"""
    if not keys: return None
    if t<=keys[0][0]: return keys[0][1]
    for (t0,v0),(t1,v1) in zip(keys,keys[1:]):
        if t<t1:
            if isinstance(v0,str): return v0
            k=(t-t0)/(t1-t0); k=ease_in_out_cubic(k) if ease else k; return v0+(v1-v0)*k
    return keys[-1][1]
def SER(s,w=900): return font('serif-vf',s,w)
def SANS(s): return font('sans',s)

# ---------------- lightning geometry (deterministic) ----------------
@lru_cache(32)
def bolt(seed,x0,y0,x1,y1,rough=.22,depth=7,branches=7):
    """main channel + branches as polylines in design px: [(pts ndarray, width_scale, is_main)]"""
    r=np.random.default_rng(seed)
    def mid(p,q,d,amp):
        if d==0: return [p]
        m=((p[0]+q[0])/2+r.normal(0,amp),(p[1]+q[1])/2+r.normal(0,amp*.25))
        return mid(p,m,d-1,amp/1.9)+mid(m,q,d-1,amp/1.9)
    L=math.hypot(x1-x0,y1-y0); main=np.array(mid((x0,y0),(x1,y1),depth,L*rough)+[(x1,y1)])
    out=[(main,1.,True)]
    for b in range(branches):
        i=int(r.uniform(.08,.8)*len(main)); p=main[i]; ang=r.choice([-1,1])*r.uniform(.35,1.1); ln=r.uniform(.12,.35)*L
        q=(p[0]+math.sin(ang)*ln,p[1]+math.cos(ang)*ln*.8)
        br=np.array(mid(tuple(p),q,5,ln*.25)+[q]); out.append((br,.45,False))
    return out
def draw_poly(c,pts,u,col,a,w,blur=0,upto=None,frm=None):
    P=pts
    if upto is not None: P=P[P[:,1]<=upto]
    if frm is not None: P=P[P[:,1]>=frm]
    if len(P)<2: return None
    p=skia.Path(); p.moveTo(P[0][0]*u,P[0][1]*u)
    for x,y in P[1:]: p.lineTo(x*u,y*u)
    c.drawPath(p,paint(col,a,stroke=w*u,blur=blur*u)); return P[-1] if upto is not None else P[0]
def draw_bolt(c,u,B,a,core=3.,glow=1.,upto=None,frm=None,col=VIOLET):
    tip=None
    for pts,ws,main in B:
        if upto is not None and pts[0][1]>upto: continue
        for w,bl,al,cl in ((core*9*ws,22,.3*glow,col),(core*3*ws,5,.7*glow,col),(core*ws,0,1,HOT)):
            r_=draw_poly(c,pts,u,cl,a*al,w,bl,upto=upto,frm=frm)
            if main and r_ is not None: tip=r_
    return tip

# ---------------- background ----------------
@lru_cache(8)
def _cloud_tex(w,h,seed,b):
    """clumped storm cumulus: thresholded fbm (cauliflower lumps), violet ramp, lit undersides"""
    n=fbm(h,w,seed,octaves=(48,24,12,6,3),gain=.6); n2=fbm(h,w,seed+7,octaves=(96,48),gain=.5)
    d=np.clip((n*.75+n2*.25-.38)*2.0,0,1); lit=np.clip(np.roll(d,-3,0)-d+.5,0,1)
    lo=np.array([52,46,100.]); hi=np.array([196,178,250.])*b; rgb=lo+(hi-lo)*(d*.6+lit*.4)[...,None]
    return to_img(np.dstack([np.clip(rgb,0,255),np.clip(d*1.1,0,1)*185]))
def flash(ctx,e,t,frame):
    """global light flashes at=[[t,amp,dur]] (white-violet screen) — used to land hard cuts"""
    a=0
    for f in e['at']:
        if f[0]<=t<f[0]+f[2]: a=max(a,f[1]*(1-(t-f[0])/f[2])**1.5)
    if a>0: ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('color','#d8d0ff'),min(1,a)))
def sky(ctx,e,t,frame):
    """storm sky: gradient (top,mid,bottom), clouds band, rain, flash (keys [[t,amount]]), optional brightness b"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; W,H=ctx.W,ctx.H; u=U(ctx); b=e.get('b',1.)
    g=skia.GradientShader.MakeLinear([(0,0),(0,H)],[hexc(e.get('top','#0b0c1a'),a),hexc(e.get('mid','#2a2c48'),a),hexc(e.get('bot','#0a0b14'),a)],[0,.55,1])
    q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeWH(W,H),q)
    if e.get('clouds',1):
        ch=int(H*e.get('cloud_h',.55)); img=_cloud_tex(int(W*1.4)//2,ch//2,e.get('seed',5),b)
        p_=skia.Paint(); p_.setAlphaf(a*e.get('clouds',1)); off=-((t*8*U(ctx))%(W*.4))
        c.saveLayer(skia.Rect.MakeWH(W,ch))
        c.drawImageRect(img,skia.Rect.MakeXYWH(off,0,W*1.4,ch),skia.SamplingOptions(skia.FilterMode.kLinear),p_)
        m=skia.Paint(); m.setBlendMode(skia.BlendMode.kDstIn); m.setShader(skia.GradientShader.MakeLinear([(0,0),(0,ch)],[0xffffffff,0xffffffff,0x00ffffff],[0,.6,1])); c.drawRect(skia.Rect.MakeWH(W,ch),m)
        c.restore()
    fl=kf(e.get('flash',[]),t,False) or 0
    for fx in e.get('flicker',[]):     # [t, amp, dur]
        if fx[0]<=t<fx[0]+fx[2]: fl=max(fl,fx[1]*(1-(t-fx[0])/fx[2]))
    if fl>0: c.drawRect(skia.Rect.MakeWH(W,H),paint('#b8b0ff',a*fl*.55,blend=skia.BlendMode.kScreen))
    if e.get('rain',1): precip(c,W,H,t,'rain',density=int(e.get('rain',1)*160),speed=1600,length=40,width=1.3,bright=.28,wind=.08,seed=3)
def city(ctx,e,t,frame):
    """skyline at ground y with lit windows, TV tower at tower_x (red beacon), ground fog"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); y=e.get('y',1560); r=random.Random(e.get('seed',4)); x=-10; lit=e.get('lit',.18)
    while x<1040:
        w=r.uniform(36,90); h=r.uniform(40,230)*e.get('hs',1.)
        c.drawRect(skia.Rect.MakeXYWH(x*u,(y-h)*u,w*u,(h+400)*u),paint('#07080f',a))
        for wy in range(int(y-h+10),int(y),16):
            for wx in range(int(x+6),int(x+w-6),12):
                if r.random()<lit: c.drawRect(skia.Rect.MakeXYWH(wx*u,wy*u,4.5*u,6*u),paint('#e8c878',a*r.uniform(.4,.9)))
        x+=w+r.uniform(2,10)
    tx=e.get('tower_x',560); th=e.get('tower_h',420)
    if tx is not None:
        p=skia.Path(); p.moveTo((tx-16)*u,y*u); p.lineTo((tx-3)*u,(y-th)*u); p.lineTo((tx+3)*u,(y-th)*u); p.lineTo((tx+16)*u,y*u); p.close(); c.drawPath(p,paint('#090a12',a))
        c.drawOval(skia.Rect.MakeXYWH((tx-18)*u,(y-th*.62)*u,36*u,14*u),paint('#0d0e18',a))
        c.drawLine(tx*u,(y-th)*u,tx*u,(y-th-60)*u,paint('#0d0e18',a,stroke=3*u))
        bl=.5+.5*math.sin(t*3); glow_dot(c,tx*u,(y-th-60)*u,4*u,'#ff4a3a',a*(.4+.6*bl),4)
    c.drawRect(skia.Rect.MakeXYWH(0,y*u,ctx.W,ctx.H-y*u),paint('#05060b',a))
    g=skia.GradientShader.MakeLinear([(0,(y-120)*u),(0,y*u)],[hexc('#3a3c60',0),hexc('#3a3c60',a*.35)]); q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeXYWH(0,(y-120)*u,ctx.W,120*u),q)

# ---------------- HUD ----------------
def hud(ctx,e,t,frame):
    """slow-mo HUD: label, timer keys [[t,ms]], unit, status keys [[t,'text']], left tag, frame counter, corner brackets"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); y=e.get('y',380)
    if e.get('brackets',True):
        bx0,by0,bx1,by1=e.get('box',[70,180,954,1590]); L=50
        for (x,yy,dx,dy) in ((bx0,by0,1,1),(bx1,by0,-1,1),(bx0,by1,1,-1),(bx1,by1,-1,-1)):
            c.drawLine(x*u,yy*u,(x+dx*L)*u,yy*u,paint(SOFT,a*.6,stroke=2*u)); c.drawLine(x*u,yy*u,x*u,(yy+dy*L)*u,paint(SOFT,a*.6,stroke=2*u))
    draw_text(c,e.get('label','真 实 时 间'),512*u,(y-150)*u,SANS(24*u),SOFT,a,spacing=4*u)
    v=kf(e['timer'],t,e.get('ease',False)); s=e.get('fmt','{:.2f}').format(v) if not isinstance(v,str) else v
    f=font('sans',e.get('size',128)*u); tw=f.measureText(s)
    draw_text(c,s,512*u-tw/2-20*u+tw/2,y*u,f,WHITE,a,glow=6*u,glow_color='#6a6aff')
    draw_text(c,e.get('unit','毫秒'),(512+tw/u/2-4)*u,(y-6)*u,SANS(38*u),WHITE,a,'left')
    st=kf(e.get('status',[]),t)
    if st: draw_text(c,st,512*u,(y+62)*u,SANS(27*u),SOFT,a)
    ty=y+160
    if e.get('tag','高速摄影'):
        glow_dot(c,108*u,(ty-9)*u,4*u,'#ff5050',a*(.5+.5*(math.sin(t*6)>0)),2)
        draw_text(c,e.get('tag','高速摄影'),125*u,ty*u,SANS(23*u),SOFT,a,'left')
    if e.get('frames',True):
        fr=int(e.get('frame0',786633)+(t-e['t0'])*e.get('fps_cam',24000))%1000000
        draw_text(c,'帧 %06d'%fr,916*u,ty*u,SANS(23*u),SOFT,a,'right')
def altitude(ctx,e,t,frame):
    """right-edge altitude ticks: marks=[[y_design,'1500 米',t_on,t_off]]"""
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c; u=U(ctx)
    for m in e['marks']:
        if not (m[2]<=t<m[3]): continue
        k=fade_env(t,m[2],m[3],.3,.3)
        for xx in range(720,960,16): c.drawLine(xx*u,m[0]*u,(xx+8)*u,m[0]*u,paint(DIMC,a*k*.6,stroke=1.2*u))
        draw_text(c,m[1],940*u,(m[0]-10)*u,SANS(22*u),DIMC,a*k,'right')
def title(ctx,e,t,frame):
    """big bold serif title + sub lines (subs=[[text,at_rel]]), centred; autowrap; y=title baseline"""
    a=env(e,t,.35,.35)
    if a<=0: return
    c=ctx.c; u=U(ctx); y=e.get('y',1350); k=ease_out_cubic(prog(t,e['t0'],.45))
    f=SER(e.get('size',84)*u,900); lines=wrap_markup(e['text'],f,e.get('max_w',900)*u) if e.get('text') else []
    for j,l in enumerate(lines):
        yy=y-(len(lines)-1-j)*e.get('size',84)*1.2
        draw_text(c,l,512*u,(yy+(1-k)*20)*u,f,WHITE,a*k,glow=8*u,glow_color='#4040a0')
    for j,s in enumerate(e.get('subs',[])):
        txt,at=(s,j*.6) if isinstance(s,str) else s; kk=prog(t,e['t0']+at,.4)
        draw_text(c,txt,512*u,(y+e.get('sub_dy',72)+j*e.get('sub_lh',48))*u,SANS(e.get('sub_size',32)*u),e.get('sub_color',SOFT) if j else WHITE,a*kk)
def text(ctx,e,t,frame):
    """free text: lines=[[text,size,dy,(color),(font)]] at x/align; staggered 'at'"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); y=e.get('y',300); at=e.get('at',[0])
    for i,l in enumerate(e['lines']):
        y+=l[2] if len(l)>2 else l[1]*1.4; k=prog(t,e['t0']+at[min(i,len(at)-1)],.4)
        fn=l[4] if len(l)>4 else ('serif' if l[1]>=48 else 'sans')
        f=SER(l[1]*u) if fn=='serif' else font(fn,l[1]*u)
        draw_text(c,l[0],e.get('x',512)*u,y*u,f,l[3] if len(l)>3 else WHITE,a*k,e.get('align','center'),glow=(4*u if l[1]>=48 else 0),glow_color='#4040a0')

# ---------------- lightning elements ----------------
def leader(ctx,e,t,frame):
    """stepped leader: bolt from (x0,y0) to (x1,y1); tip keys [[t,frac 0..1]] reveal down to tip; tip glow; stepping flicker"""
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c; u=U(ctx); x0,y0,x1,y1=e.get('from',[420,-40])+e.get('to',[560,1140])
    B=bolt(e.get('seed',11),x0,y0,x1,y1,e.get('rough',.22),7,e.get('branches',7))
    fr=kf(e['tip'],t,False); ty=y0+(y1-y0)*fr; step=.6+.4*(math.sin(t*40)>0)
    tip=draw_bolt(c,u,B,a*e.get('alpha',.75)*step,core=e.get('w',2.2),glow=.8,upto=ty)
    if tip is not None:
        glow_dot(c,tip[0]*u,tip[1]*u,6*u,HOT,a*step,7); c.drawCircle(tip[0]*u,tip[1]*u,70*u,paint(VIOLET,a*.18*step,blur=30*u))
def streamers(ctx,e,t,frame):
    """short upward sparks from points=[[x,y,len]] flickering"""
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c; u=U(ctx)
    for i,(x,y,L) in enumerate(e['points']):
        k=ease_out_cubic(prog(t,e['t0']+i*.25,1.2)); B=bolt(100+i,x,y,x+random.Random(i).uniform(-15,15),y-L*k+1,.3,4,2)
        fl=.5+.5*math.sin(t*25+i*2); draw_bolt(c,u,B,a*(.5+.5*fl),core=1.3,glow=.7)
def strike(ctx,e,t,frame):
    """return stroke: full channel lights up from ground upward (rise s) then glows; flick=[[t,amp]] re-strikes; ring halo at top (halo_y)"""
    a=env(e,t,.05,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); x0,y0,x1,y1=e.get('from',[420,-40])+e.get('to',[560,1140])
    B=bolt(e.get('seed',11),x0,y0,x1,y1,e.get('rough',.22),7,e.get('branches',7))
    kr=ease_out_cubic(prog(t,e['t0'],e.get('rise',.6))); frm=y1-(y1-y0+60)*kr
    amp=e.get('glow',1.); 
    for f_ in e.get('flick',[]):
        if f_[0]<=t<f_[0]+.35: amp=max(amp,f_[1]*(1-(t-f_[0])/.35)+.4)
    if e.get('dim_after') and t>e['dim_after']: amp*=.55
    jit=.85+.15*math.sin(t*30)
    draw_bolt(c,u,B,a*jit,core=e.get('w',3.2)*min(1.6,amp),glow=amp,frm=frm)
    if e.get('halo_y') and kr>.2:
        hx=np.interp(e['halo_y'],B[0][0][:,1],B[0][0][:,0]); hy=e['halo_y']
        c.drawOval(skia.Rect.MakeXYWH((hx-110)*u,(hy-14)*u,220*u,28*u),paint(HOT,a*.7,stroke=2.5*u))
        glow_dot(c,hx*u,hy*u,26*u,HOT,a*min(1,amp),5)
    if e.get('flash_top',True): c.drawCircle(x1*u,y1*u,90*u,paint(VIOLET,a*.25*amp,blur=40*u))
def ice(ctx,e,t,frame):
    """cloud interior: violet glow, tumbling snowflakes (crystals rise) + graupel lumps (fall), collision sparks"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; W,H=ctx.W,ctx.H; u=U(ctx)
    g=skia.GradientShader.MakeRadial((W*.45,H*.6),H*.75,[hexc('#d8d0ff',a),hexc('#6a66b8',a),hexc('#232442',a)],[0,.35,1]); q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeWH(W,H),q)
    r=random.Random(7)
    for i in range(e.get('n',70)):
        x=r.uniform(0,1024); sp=r.uniform(30,90); kind=r.random()<.55; s=r.uniform(10,26)
        y=(r.uniform(0,1900)+(-1 if kind else 1)*sp*(t-e['t0']))%1900-40; x+=math.sin(t*.6+i)*12
        if kind:   # crystal: 6 arms
            rot_=t*r.uniform(-.8,.8)+i
            for k in range(6):
                an=rot_+k*math.pi/3; c.drawLine(x*u,y*u,(x+math.cos(an)*s)*u,(y+math.sin(an)*s)*u,paint('#f0f0ff',a*.8,stroke=1.6*u))
                for bb in (.5,.75):
                    bx,by=x+math.cos(an)*s*bb,y+math.sin(an)*s*bb
                    for sg in (-1,1): c.drawLine(bx*u,by*u,(bx+math.cos(an+sg*.8)*s*.25)*u,(by+math.sin(an+sg*.8)*s*.25)*u,paint('#f0f0ff',a*.6,stroke=1.1*u))
        else:
            c.drawCircle(x*u,y*u,s*.9*u,paint('#e8e8f8',a*.55,blur=3*u)); c.drawCircle(x*u,y*u,s*.6*u,paint('#ffffff',a*.6))
    for i in range(3):
        ph=(t*1.3+i*.37)%1
        if ph<.12: x=random.Random(int(t*1.3)*7+i).uniform(250,800); y=random.Random(int(t*1.3)*11+i).uniform(600,1300); glow_dot(c,x*u,y*u,10*u,'#ffffff',a*(1-ph/.12),8)
def charges(ctx,e,t,frame):
    """charge signs: rows=[[y,'-'|'+',n,color]] scattered, shimmering"""
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); f=SANS(34*u)
    for ri,(y,sg,n,col) in enumerate(e['rows']):
        r=random.Random(ri*13+5)
        for i in range(n):
            k=prog(t,e['t0']+r.uniform(0,1.2),.5); x=r.uniform(60,964); yy=y+r.uniform(-50,50)+math.sin(t*2+i)*4
            draw_text(c,sg,x*u,yy*u,f,col,a*k*(.6+.4*math.sin(t*3+i)),glow=4*u,glow_color=col)
def bignum(ctx,e,t,frame):
    """big number with head/foot text: value string or from/to count over dur"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); y=e.get('y',760)
    if 'rate' in e: v=e.get('fmt','{:.0f}').format(max(0,(t-e.get('start',e['t0']))*e['rate']))
    elif 'value' in e: v=e['value']
    else: v='{:,}'.format(int(lerp(e['from'],e['to'],ease_out_cubic(prog(t,e['t0'],e.get('dur',1.2))))))
    if e.get('head'): draw_text(c,e['head'],512*u,(y-e.get('size',110)-30)*u,SANS(28*u),SOFT,a)
    draw_text(c,v,512*u,y*u,font('sans',e.get('size',110)*u),WHITE,a,glow=8*u,glow_color='#6a6aff',spacing=e.get('spacing',2)*u)
    if e.get('foot'): draw_text(c,e['foot'],512*u,(y+56)*u,SANS(28*u),SOFT,a)
def rings(ctx,e,t,frame):
    """thunder: concentric arcs expanding from (x,y) at speed px/s, every period s"""
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',560),e.get('y',1200)
    for i in range(e.get('n',4)):
        R=((t-e['t0'])*e.get('speed',260)+i*e.get('gap',40))
        if R<=0: continue
        al=a*max(0,1-R/e.get('max_r',1400))
        c.drawCircle(x*u,y*u,R*u,paint(SOFT,al*.6,stroke=2*u))
def rows(ctx,e,t,frame):
    """equation rows: rows=[[big,small,at]] e.g. ['3 秒','≈ 1 公里']"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); y=e.get('y',700)
    for i,r in enumerate(e['rows']):
        k=prog(t,r[2] if len(r)>2 else e['t0']+i*.5,.4); yy=y+i*e.get('dy',100)
        draw_text(c,r[0],(e.get('x',512)-20)*u,yy*u,font('sans',e.get('size',72)*u),WHITE,a*k,'right')
        draw_text(c,r[1],(e.get('x',512)+10)*u,yy*u,SANS(e.get('size',72)*.55*u),SOFT,a*k,'left')
@lru_cache(2)
def _earth_tex(seed=3,w=1440,h=720):
    """land mask rasterised from Natural Earth 50m countries (real geodata); city lights sampled inside land, denser where fbm high"""
    import cv2, json, os
    p=os.path.join(os.path.dirname(__file__),'..','..','assets','geo','countries_50m.geojson'); m=np.zeros((h,w),np.uint8)
    for f in json.load(open(p))['features']:
        g=f['geometry']; cs=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
        for poly in cs:
            r=np.array(poly[0],float); pts=np.stack([(r[:,0]+180)/360*(w-1),(90-r[:,1])/180*(h-1)],1).astype(np.int32)
            cv2.fillPoly(m,[pts],1)
    land=m.astype(bool); lat=np.linspace(90,-90,h)[:,None]
    r=np.random.default_rng(seed); dens=fbm(h,w,seed+1)**3*np.exp(-((np.abs(lat)-35)/22)**2)
    lights=land&(r.random((h,w))<.5*dens)
    return land,lights
def earth(ctx,e,t,frame):
    """night-side globe: procedural continents + city lights, blue rim, rotates (spin deg/s); lit from 'sun' side"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); cx,cy,R=e.get('x',512),e.get('y',860),e.get('r',300); land,lights=_earth_tex()
    N=int(2*R*u); N=max(64,min(N,700)); ys,xs=np.mgrid[-1:1:N*1j,-1:1:N*1j]; m=xs**2+ys**2<=1; z=np.sqrt(np.clip(1-xs**2-ys**2,0,1))
    tilt=math.radians(15); yy=ys*math.cos(tilt)-z*math.sin(tilt); zz=ys*math.sin(tilt)+z*math.cos(tilt)
    lat=np.degrees(np.arcsin(np.clip(-yy,-1,1))); lon=(np.degrees(np.arctan2(xs,zz))+180+(t-e['t0'])*e.get('spin',6)+e.get('lon0',0))%360
    iy=((90-lat)/180*(land.shape[0]-1)).astype(int); ix=(lon/360*(land.shape[1]-1)).astype(int)
    L=land[iy,ix]; Li=lights[iy,ix]; sun=np.clip(-.6*xs-.2*ys+.3*z,0,1)
    img=np.zeros((N,N,4)); ocean=np.array([10,24,60]); grd=np.array([22,30,30])
    img[...,:3]=np.where(L[...,None],grd,ocean)*(.35+1.6*sun[...,None])
    img[...,:3]+=np.where(Li[...,None],np.array([255,200,110])*(1-sun[...,None]*1.2).clip(0,1),0)
    rim=np.clip((1-z)**3,0,1); img[...,:3]+=np.array([60,110,220])*rim[...,None]*.9
    img[...,3]=m*255; img[...,:3]=np.clip(img[...,:3],0,255)
    c.drawCircle(cx*u,cy*u,R*1.06*u,paint('#3a6ad0',a*.35,blur=30*u))
    p=skia.Paint(); p.setAlphaf(a); c.drawImageRect(to_img(img),skia.Rect.MakeXYWH((cx-R)*u,(cy-R)*u,2*R*u,2*R*u),skia.SamplingOptions(skia.FilterMode.kLinear),p)
    r=random.Random(int(t*3))
    for i in range(e.get('sparks',3)):
        an=r.uniform(0,2*math.pi); rr=r.uniform(0,.85)*R; glow_dot(c,(cx+math.cos(an)*rr)*u,(cy+math.sin(an)*rr)*u,4*u,'#e8e8ff',a*r.uniform(.4,1),5)
def head(ctx,e,t,frame):
    """inset circle with silhouette head whose hair stands up (k over rise s), purple ring"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,R=e.get('x',330),e.get('y',1150),e.get('r',190); k=ease_out_cubic(prog(t,e['t0']+.3,e.get('rise',1.5)))
    c.drawCircle(x*u,y*u,R*u,paint('#3a2c68',a*.95)); c.drawCircle(x*u,y*u,R*u,paint('#e0d0ff',a,stroke=4*u)); c.drawCircle(x*u,y*u,R*u,paint('#a080ff',a*.5,stroke=10*u,blur=8*u))
    c.save(); pth=skia.Path(); pth.addCircle(x*u,y*u,R*u); c.clipPath(pth,doAntiAlias=True)
    c.drawOval(skia.Rect.MakeXYWH((x-R*.75)*u,(y+R*.45)*u,R*1.5*u,R*1.2*u),paint('#0a0814',a)); c.drawCircle(x*u,(y+R*.12)*u,R*.42*u,paint('#0a0814',a))
    for i in range(40):
        an=math.pi*(1.05+.9*i/39); base=(x+math.cos(an)*R*.4,y+R*.12+math.sin(an)*R*.4)
        up=(-math.pi/2)*k+an*(1-k); L=R*(.18+.35*k)
        c.drawLine(base[0]*u,base[1]*u,(base[0]+math.cos(up)*L)*u,(base[1]+math.sin(up)*L)*u,paint('#0a0814',a,stroke=3*u))
        if k>.5: glow_dot(c,(base[0]+math.cos(up)*L)*u,(base[1]+math.sin(up)*L)*u,1.5*u,'#e0d0ff',a*(k-.5)*2*(.5+.5*math.sin(t*20+i)),2)
    c.restore()

EXTRA=dict(flash=flash,sky=sky,city=city,hud=hud,altitude=altitude,title=title,text=text,leader=leader,streamers=streamers,strike=strike,ice=ice,charges=charges,
           bignum=bignum,rings=rings,rows=rows,earth=earth,head=head)
def draw(ctx,t,frame,S):
    c=ctx.c; c.clear(hexc('#06070d'))
    for sc in S['scenes']:
        if sc['t0']-1e-6<=t<sc['t1']:
            fi,fo=sc.get('fade_in',.4),sc.get('fade_out',.4); k=fade_env(t,sc['t0'],sc['t1'],fi,fo) if (fi or fo) else 1
            if k<=0: continue
            if k<1: c.saveLayerAlpha(None,int(255*k))
            draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)
            if k<1: c.restore()
    draw_elements(ctx,S.get('overlays',[]),t,frame,EXTRA)
    vignette(c,ctx.W,ctx.H,.5); grain(c,ctx.W,ctx.H,frame,.03,10)
