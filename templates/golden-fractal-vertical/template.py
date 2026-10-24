"""#2 金线分形·竖屏 (golden-fractal-vertical) — ref 7697240924837748134《人生的容错率》 1080x1920.
Warm black (#0b0908) + central warm haze + vignette; one glowing gold life-line that grows, forks into a tree, shatters into a
crack network; nodes = glowing dots with age (grey) + event (white serif); clock ring; vertical bundle; dot matrix (red/white);
twisted rope; U-curve chart; top-centre serif captions with red keywords; tiny grey citations at the bottom.
Design space: 1024 wide × 1820 tall (U=W/1024)."""
import math, random, numpy as np, skia
from engine.core import *
from engine.layers import draw_elements, U, el_text, wrap_markup
from engine import lines as LN

GOLD='#f0d9a8'; WHITE='#f2ece2'; GREY='#8a8178'; RED='#d0403e'; CORE='#fff6e0'
def prepare(S): pass

@lru_cache(2)
def bg_tex(W,H):
    rng=np.random.default_rng(3); yy,xx=np.mgrid[0:H,0:W]
    r=np.hypot((xx-W*.5)/(W*.55),(yy-H*.5)/(H*.5))
    v=np.clip(1-r,0,1)**1.6
    img=np.dstack([11+26*v,9+20*v,8+14*v])+rng.normal(0,1.0,(H,W,1))
    return skia.Image.fromarray(np.dstack([img.clip(0,255).astype(np.uint8),np.full((H,W),255,np.uint8)]),colorType=skia.kRGBA_8888_ColorType)

def env(e,t,fi=.5,fo=.5): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1.)
def F(name,size,u,w=None): return font(name,size*u,w)

def caption(ctx,e,t,frame):
    """top caption lines; runs '[...]' are red keywords; anim: fade+slight rise, optional blur-in"""
    a=env(e,t,.35,.35)
    if a<=0: return
    u=U(ctx); c=ctx.c; k=ease_out_cubic(prog(t,e['t0'],.5))
    f=F(e.get('font','serif-vf'),e.get('size',56),u,e.get('weight',700))
    for i,ln in enumerate(wrap_markup(e['text'],f,e.get('max_w',940)*u)):
        y=(e.get('y',345)+i*e.get('lh',90))*u+(1-k)*10*u
        parts=[]; red=False
        for seg in ln.replace(']','[').split('['):
            if seg: parts.append((seg,RED if red else e.get('color',WHITE)))
            red=not red
        tw=sum(f.measureText(s) for s,_ in parts); x=e.get('x',512)*u-tw/2
        for s,col in parts:
            g=e.get('glow',0)*u+(8*u if col==RED else 0)
            draw_text(c,s,x,y,f,col,a,'left',glow=g,glow_color=col if col==RED else None); x+=f.measureText(s)
            if col==RED:
                # soft red halo disc behind keyword
                cx=x-f.measureText(s)/2; c.drawCircle(cx,y-f.getSize()*.35,f.measureText(s)*.7,paint(RED,a*.12,blur=10*u))

def cite(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a>0: u=U(ctx); draw_text(ctx.c,e['text'],e.get('x',512)*u,e.get('y',1690)*u,F('serif',e.get('size',13),u),GREY,a*.8)

def gline(ctx,e,t,frame):
    """growing glowing polyline/curve. pts or curve=[a,b,bend]; draw=[t,dur]; optional tip spark"""
    a=env(e,t,.3,.5)
    if a<=0: return
    u=U(ctx); pts=e.get('pts') or LN.curve_to(*e['curve'][:2],e['curve'][2] if len(e['curve'])>2 else .2)
    d=e.get('draw',[e['t0'],1.0]); k=ease_in_out_cubic(prog(t,d[0],d[1])) if d[1]>0 else 1
    p,tip=LN.path_from(pts,u,k); LN.glow_path(ctx.c,p,u,e.get('color',GOLD),a,e.get('w',2.),e.get('glow',10))
    if e.get('spark',True) and 0<k<1 and tip is not None: LN.glow_node(ctx.c,tip[0],tip[1],u,4,a,halo=7)

def node(ctx,e,t,frame):
    """glowing dot + labels: age left (grey), event right (white bold); pop-in"""
    a=env(e,t,.25,.4)
    if a<=0: return
    u=U(ctx); c=ctx.c; k=ease_out_back(prog(t,e['t0'],.35)); x,y=e['x'],e['y']
    LN.glow_node(c,x,y,u,e.get('r',5)*max(.01,k),a,e.get('color','#ffe6b0'))
    if e.get('age'): draw_text(c,e['age'],(x-18)*u,(y+9)*u,F('serif-vf',e.get('size',32),u,400),GREY,a,'right')
    if e.get('label'): draw_text(c,e['label'],(x+(18 if e.get('side','r')=='r' else -18))*u,(y+9)*u,F('serif-vf',e.get('size',32),u,700),e.get('lcolor',WHITE),a,'left' if e.get('side','r')=='r' else 'right')

def tree(ctx,e,t,frame):
    """radial/upward branching tree of labelled curved branches grown from root; branches=[[dx,dy,label,bend,(children)]]"""
    a=env(e,t,.4,.6)
    if a<=0: return
    u=U(ctx); c=ctx.c; x0,y0=e['x'],e['y']; st=e.get('stagger',.12); dur=e.get('dur',.9)
    def grow(px,py,brs,t0,depth):
        for i,b in enumerate(brs):
            dx,dy,lab=b[0],b[1],b[2]; bend=b[3] if len(b)>3 else .15; kids=b[4] if len(b)>4 else []
            tb=t0+i*st; k=ease_in_out_cubic(prog(t,tb,dur))
            if k<=0: continue
            pts=LN.curve_to((px,py),(px+dx,py+dy),bend)
            p,tip=LN.path_from(pts,u,k); LN.glow_path(c,p,u,GOLD,a*(1-.18*depth),max(.6,1.8-.45*depth),8-2*depth)
            if k>=1:
                LN.glow_node(c,px+dx,py+dy,u,max(2,4-depth),a*(1-.2*depth),halo=4)
                if lab:
                    ka=prog(t,tb+dur,.3); sz=e.get('size',32)*(1-.15*depth)
                    al='left' if dx>=0 else 'right'; off=12 if dx>=0 else -12
                    draw_text(c,lab,(px+dx+off)*u,(py+dy+8)*u,F('serif-vf',sz,u,700 if depth==0 else 500),WHITE if depth==0 else '#cfc6b8',a*ka,al)
                grow(px+dx,py+dy,kids,tb+dur*.7,depth+1)
    grow(x0,y0,e['branches'],e.get('grow_at',e['t0']),0)
    LN.glow_node(c,x0,y0,u,6,a,halo=6)

def crack(ctx,e,t,frame):
    """procedural crack network spreading over the frame (shatter); seeds/depth control density"""
    a=env(e,t,.4,.8)
    if a<=0: return
    u=U(ctx); net=_net(e.get('seed',1),tuple(e.get('box',[-40,-40,1064,1860])),e.get('n',14),e.get('depth',10))
    k=ease_out_cubic(prog(t,e.get('grow_at',e['t0']),e.get('dur',2.0)))*e.get('kmax',1)
    LN.draw_net(ctx.c,net,u,k,e.get('color','#cdb88e'),a*e.get('net_a',.85),e.get('w',1.15))
@lru_cache(16)
def _net(seed,box,n,depth): return LN.crack_net(seed,box,n,depth)

def ring(ctx,e,t,frame):
    """social-clock ring: arc + ticks; optional title (above), big count/center, sub (below)"""
    a=env(e,t,.4,.5)
    if a<=0: return
    u=U(ctx); c=ctx.c; x,y,r=e['x']*u,e['y']*u,e.get('r',210)*u
    kd=e.get('draw',1.2); k=ease_in_out_cubic(prog(t,e['t0'],kd)) if kd else 1.0
    p=skia.Path(); p.addArc(skia.Rect.MakeLTRB(x-r,y-r,x+r,y+r),-90,360*k); LN.glow_path(c,p,1,GOLD,a,2.2*u,10*u)
    for tk in e.get('ticks',[]):
        ang=math.radians(tk[0]-90); kk=prog(t,e['t0']+.3+tk[0]/360*max(kd,.01),.3)
        px,py=e['x']+math.cos(ang)*e.get('r',210),e['y']+math.sin(ang)*e.get('r',210); LN.glow_node(c,px,py,u,4,a*kk)
        if len(tk)>1: draw_text(c,tk[1],(px+math.cos(ang)*28)*u,(py+math.sin(ang)*28+8)*u,F('serif-vf',22,u,500),'#d8d0c4',a*kk,'left' if math.cos(ang)>.2 else 'right' if math.cos(ang)<-.2 else 'center')
    cs=e.get('csize',72)
    if e.get('title'):
        draw_text(c,e['title'],x,y-cs*.55*u,F('serif-vf',e.get('tsize',28),u,500),e.get('tcolor','#d8d0c4'),a)
    if e.get('count') or e.get('center'):
        if e.get('count'):
            c0,c1,cd=e['count']; v=f"{lerp(c0,c1,ease_out_cubic(prog(t,e.get('count_at',e['t0']),cd))):.2f}"
            unit=e.get('unit',''); yy=y+cs*.38*u; col=e.get('ccolor',WHITE); aa=a*e.get('ca',1)
            fn=F('garamond',cs,u,600); fu=F('serif-vf',cs*.55,u,500) if unit else None
            tw=fn.measureText(v)+(fu.measureText(' '+unit) if fu else 0)
            draw_text(c,v,x-tw/2,yy,fn,col,aa,'left',glow=5*u)
            if fu: draw_text(c,' '+unit,x-tw/2+fn.measureText(v),yy,fu,col,aa,'left',glow=3*u)
        else:
            draw_text(c,e['center'],x,y+cs*.38*u,F('serif-vf',cs,u,600),e.get('ccolor',WHITE),a*e.get('ca',1),glow=4*u)
    sub=e.get('sub')
    if e.get('sub1') and e.get('count'):
        c0,c1,cd=e['count']; kk=ease_out_cubic(prog(t,e.get('count_at',e['t0']),cd))
        sub=e['sub1'] if kk>.55 else e.get('sub')
    if sub:
        draw_text(c,sub,x,y+cs*.95*u,F('serif-vf',e.get('ssize',18),u,500),GREY,a)

def vbundle(ctx,e,t,frame):
    """N vertical lines rising from a baseline with top dots; some lines bend sideways into arcs (career change)"""
    a=env(e,t,.4,.5)
    if a<=0: return
    u=U(ctx); c=ctx.c; xs=e['xs']; yb,yt=e['y0'],e['y1']; bends=e.get('bends',{})
    for i,x in enumerate(xs):
        k=ease_in_out_cubic(prog(t,e['t0']+i*e.get('stagger',.08),e.get('dur',1.2)))
        if str(i) in bends:
            bx=bends[str(i)]; kb=ease_in_out_cubic(prog(t,e.get('bend_at',e['t0']+1.5)+i*.05,1.0))
            pts=np.array([[x,yb],[x,lerp(yt,yt+120,kb)],[lerp(x,x+bx,kb),lerp(yt,yt-120,kb)]])
            pts=LN.bezier(pts[0],pts[1],pts[2],50)
        else: pts=[(x,yb),(x,yt)]
        p,tip=LN.path_from(pts,u,k); LN.glow_path(c,p,u,GOLD,a*.85,1.3,6)
        if k>=1: LN.glow_node(c,tip[0],tip[1],u,3.5,a,halo=4)
    for i,x in enumerate(e.get('rings',[])): c.drawCircle(x*u,e.get('ring_y',yt-150)*u,7*u,paint('#8a8178',a*.7,stroke=1.2*u))

def matrix(ctx,e,t,frame):
    """dot matrix (rows×cols); fraction `red` of dots turn red (deterministic shuffle) at red_at; reveal row by row"""
    a=env(e,t,.3,.5)
    if a<=0: return
    u=U(ctx); c=ctx.c; R,C=e.get('rows',10),e.get('cols',10); x0,y0,dx,dy=e['x0'],e['y0'],e.get('dx',44),e.get('dy',44)
    rng=random.Random(e.get('seed',2)); idx=list(range(R*C)); rng.shuffle(idx); nred=int(R*C*e.get('red',.7)); reds=set(idx[:nred])
    kr=prog(t,e.get('red_at',1e9),e.get('red_dur',1.0)); kw=prog(t,e.get('white_at',1e9),1.0)
    for i in range(R*C):
        r_,c_=divmod(i,C); kk=prog(t,e['t0']+r_*.05,.3)
        if kk<=0: continue
        x,y=(x0+c_*dx)*u,(y0+r_*dy)*u; isred=i in reds and idx.index(i)<nred*kr
        col=RED if isred else '#d8cfc2'; rad=5.5*u
        if isred and kw>0 and idx.index(i)<nred*kw*e.get('recover',.0): col='#f2e6c8'
        c.drawCircle(x,y,rad,paint(col,a*kk*(1. if isred else .6)))
        if isred and col==RED: c.drawCircle(x,y,rad*2.6,paint('#ff5a4a',a*kk*.15,blur=3*u))

def ucurve(ctx,e,t,frame):
    """chart: axes + U-shaped glowing curve (high at ends = more suffering); mark at trough"""
    a=env(e,t,.4,.5)
    if a<=0: return
    u=U(ctx); c=ctx.c; x0,y0,w,h=e['box']
    line(c,x0*u,y0*u,x0*u,(y0+h)*u,'#8a8178',a*.7,1.2*u); line(c,x0*u,(y0+h)*u,(x0+w)*u,(y0+h)*u,'#8a8178',a*.7,1.2*u)
    draw_text(c,e.get('ylabel',''),(x0-8)*u,(y0-20)*u,F('serif-vf',22,u,500),'#cfc6b8',a,'left')
    for xl,lab in e.get('xlabels',[]):
        al='left' if xl<.1 else 'right' if xl>.9 else 'center'
        draw_text(c,lab,(x0+xl*w)*u,(y0+h+36)*u,F('serif-vf',20,u,600),'#cfc6b8',a,al)
    # U shape in screen space: high (near y0) at ends, low (near y0+h) at middle
    xs=np.linspace(0,1,100); depth=e.get('depth',.78)
    ys=depth*(2*xs-1)**2   # 0 at center, depth at ends  → screen y = y0 + h*(pad + (1-pad-top)*ys_inv)
    # map: value_high → small screen-y. value = 1 - (2x-1)^2 for inverted-U of "happiness"; suffering U = (2x-1)^2
    # screen: y = y0 + h*(0.12 + 0.78*(1 - suffering_norm)) with suffering_norm = (2x-1)^2
    # → high suffering at ends → near top. Wait ref shows U with ends HIGH on chart (top) and middle LOW (bottom).
    # suffering high at ends: screen_y_ends small, screen_y_mid large
    # screen_y = y0 + h*(0.10 + 0.80*(1 - (2xs-1)**2))  NO that's inverted U on screen (∩)
    # U on screen: screen_y = y0 + h*(0.10 + 0.80*(2xs-1)**2)
    pts=np.column_stack([x0+w*(.04+.92*xs), y0+h*(.10+.80*(1-(2*xs-1)**2))])  # U: high at ends
    k=ease_in_out_cubic(prog(t,e.get('draw_at',e['t0']),e.get('dur',1.2))); p,tip=LN.path_from(pts,u,k); LN.glow_path(c,p,u,GOLD,a,2.4,12)
    if e.get('mark') is not None and k>=.95:
        m=e['mark']; j=int(np.clip(m,0,1)*99); LN.glow_node(c,pts[j][0],pts[j][1],u,6,a*prog(t,e.get('draw_at',e['t0'])+e.get('dur',1.2)*.9,.35))

def ropeline(ctx,e,t,frame):
    """diagonal twisted rope (life thread); labels pop along it in red"""
    a=env(e,t,.4,.5)
    if a<=0: return
    u=U(ctx); k=ease_in_out_cubic(prog(t,e['t0'],e.get('draw',1.0)))
    LN.rope(ctx.c,e['p0'],e['p1'],u,t,k,a=a,amp=e.get('amp',7),turns=e.get('turns',36))

def glowtext(ctx,e,t,frame):
    """centre statement with red keyword runs, blur-in"""
    caption(ctx,dict(e,glow=e.get('glow',6)),t,frame)

def redcluster(ctx,e,t,frame):
    """red glowing particle cluster (ref 53.3s): soft red ellipse + jittering sparks"""
    a=env(e,t,.15,.5)
    if a<=0: return
    u=U(ctx); c=ctx.c; x,y=e['x'],e['y']; R=e.get('r',90)
    c.drawOval(skia.Rect.MakeXYWH((x-R*1.3)*u,(y-R*.8)*u,R*2.6*u,R*1.6*u),paint('#c8302c',a*.22,blur=R*.4*u))
    rng=random.Random(e.get('seed',1))
    for i in range(e.get('n',60)):
        ang=rng.uniform(0,6.283); rr=R*rng.random()**.6; ph=rng.uniform(0,6.283)
        px=x+math.cos(ang)*rr*1.3+math.sin(t*2+ph)*3; py=y+math.sin(ang)*rr*.8+math.cos(t*1.7+ph)*3
        fl=.5+.5*math.sin(t*6+ph); col='#ff6a50' if i%3 else '#fff0e0'
        c.drawCircle(px*u,py*u,rng.uniform(1,2.6)*u,paint(col,a*(.4+.6*fl)))

def arcweb(ctx,e,t,frame):
    """sparse web of long smooth arcs (ref 51-56s) + thin verticals with red beads"""
    a=env(e,t,.3,.5)
    if a<=0: return
    u=U(ctx); c=ctx.c; rng=random.Random(e.get('seed',1)); k=ease_out_cubic(prog(t,e['t0'],e.get('dur',.01)))
    hub=e.get('hub',(512,1150))
    for i in range(e.get('n',22)):
        if i<e.get('nhub',8): a0=hub
        else: a0=(rng.uniform(-100,1124),rng.uniform(200,1900))
        b0=(rng.uniform(-200,1224),rng.uniform(150,1950))
        pts=LN.curve_to(a0,b0,rng.uniform(-.35,.35)); pp,_=LN.path_from(pts,u,k)
        LN.glow_path(c,pp,u,'#e8d6b0',a*rng.uniform(.5,1),rng.uniform(.6,1.3),5)
    for i in range(e.get('nv',4)):
        x=hub[0]+rng.uniform(-120,180); y0=hub[1]+rng.uniform(-40,60); L=rng.uniform(150,350)
        line(c,x*u,y0*u,x*u,(y0+L)*u,'#f2ece2',a*.8,1.2*u); c.drawCircle(x*u,(y0+L*rng.uniform(.3,.9))*u,3*u,paint(RED,a))
    LN.glow_node(c,hub[0],hub[1],u,5,a,halo=8)

def hflash(ctx,e,t,frame):
    """instant peak flash at t0 for hard-cut emphasis"""
    if not (e['t0']<=t<e.get('t1',e['t0']+2.5)): return
    a=e.get('a',.35)*math.exp(-(t-e['t0'])/e.get('tau',.18))
    p=paint(e.get('color','#f2e6c8'),a); p.setBlendMode(skia.BlendMode.kScreen); ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),p)

EXTRA=dict(caption=caption,cite=cite,gline=gline,node=node,tree=tree,crack=crack,ring=ring,vbundle=vbundle,matrix=matrix,ucurve=ucurve,ropeline=ropeline,glowtext=glowtext,hflash=hflash,redcluster=redcluster,arcweb=arcweb)

def draw(ctx,t,frame,S):
    c=ctx.c; c.drawImage(bg_tex(ctx.W,ctx.H),0,0)
    for sc in S['scenes']:
        if sc['t0']-1e-6<=t<sc['t1']:
            c.save()
            z=sc.get('zoom')
            if z: k=prog(t,sc['t0'],sc['t1']-sc['t0']); s=lerp(z[0],z[1],ease_in_out_cubic(k)); cx,cy=sc.get('zc',[512,910]); u=U(ctx); c.translate(cx*u,cy*u); c.scale(s,s); c.translate(-cx*u,-cy*u)
            draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA); c.restore()
            fi,fo=sc.get('fade_in',.4),sc.get('fade_out',.4)
            dk=max(1-prog(t,sc['t0'],fi) if fi else 0, prog(t,sc['t1']-fo,fo) if fo else 0)
            if dk>0: c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint('#0b0908',dk))
    draw_elements(ctx,S.get('overlays',[]),t,frame,EXTRA)
    vignette(c,ctx.W,ctx.H,.5); grain(c,ctx.W,ctx.H,frame,.03,10)
