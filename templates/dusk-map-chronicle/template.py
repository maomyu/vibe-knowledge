"""#3 暮色地图史话 (dusk-map-chronicle) — ref 7693231930334855918《唐朝烽火 平安火》1024x576.
Backgrounds: real-DEM shaded relief map (engine.terrain, AWS terrain tiles) with Yellow River (Natural Earth), night beacon
landscape, tower-row stage, dusk city gate, fog, desert dig site, dark paper/book desk.
Overlays: top-left bold serif narration ([gold underline] {red underline}), right-top gold counters, glowing bead routes with fire
head, palace icons, procedural flames, parchment cards/book, dashed radius rings, moon badge, bottom citation.
Design space 1024x576."""
import math, random, json, os, numpy as np, skia
from functools import lru_cache
from engine.core import *
from engine.layers import draw_elements, U, wrap_markup
from engine import lines as LN
from engine.geo import Proj
from engine import terrain as TR

GOLD='#f2c766'; RED='#e0584a'; WHITE='#f4efe6'; GREY='#a99f90'; PAPER='#d9c7a0'
CITY={'凉州':(102.64,37.93),'长安':(108.94,34.27),'潼关':(110.25,34.55),'秦州':(105.72,34.58),'尉犁':(86.26,41.34),
      '边境':(98.5,39.75),'京城':(108.94,34.27),'兰州':(103.83,36.06),'甘州':(100.45,38.93),'肃州':(98.5,39.75),'原州':(106.28,36.0)}
def prepare(S):
    """script may add/override places: S['places']={name:[lon,lat]}; S['map']={'palette':{base,lift,dark},'rivers':[names] or 'all'}"""
    CITY.update({k:tuple(v) for k,v in S.get('places',{}).items()}); MAPCFG.update(S.get('map',{}))
MAPCFG={'rivers':['Huang'],'contrast':1.35,'base':[30,24,17],'lift':[80,68,52],'dark':[8,6,5]}
def _relief(q,W,H,ppd):
    kw=dict(contrast=MAPCFG['contrast'],base=tuple(MAPCFG['base']),lift=tuple(MAPCFG['lift']),dark=tuple(MAPCFG['dark']))
    return TR.relief_auto(q,W,H,ppd,**kw)
def env(e,t,fi=.4,fo=.4): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def F(n,s,w=None): return font(n,s,w)

# ---------------- camera / map ----------------
def cam_proj(cam):
    """cam=[lon_c,lat_c,ppd] (pixels per degree latitude) -> Proj on 1024x576"""
    lc,bc,ppd=cam; k=math.cos(math.radians(bc)); hw=512/(ppd*k); hh=288/ppd
    return Proj((lc-hw,bc-hh,lc+hw,bc+hh),0,0,1024,576)
def fit_cam(spec):
    """{'fit':[places or [lon,lat]], 'box':[x0,y0,x1,y1] design px (default keeps the top-left caption area free)} -> [lon,lat,ppd]"""
    pts=[CITY[q] if isinstance(q,str) else q for q in spec['fit']]; lo=[p[0] for p in pts]; la=[p[1] for p in pts]
    x0,y0,x1,y1=spec.get('box',[120,200,960,540]); bc=(min(la)+max(la))/2; k=math.cos(math.radians(bc))
    ppd=min((x1-x0)/max((max(lo)-min(lo))*k,.05),(y1-y0)/max(max(la)-min(la),.05))
    lc=(min(lo)+max(lo))/2-((x0+x1)/2-512)/(ppd*k); bcc=bc+((y0+y1)/2-288)/ppd
    return [lc,bcc,ppd]
def cam_at(sc,t):
    for kk in ('cam','cam1'):
        if isinstance(sc.get(kk),dict): sc[kk]=fit_cam(sc[kk])
    c0=sc['cam']; c1=sc.get('cam1',c0); d=sc.get('cam_dur',sc['t1']-sc['t0']); k=ease_in_out_cubic(prog(t,sc.get('cam_at',sc['t0']),d))
    # log-interp zoom
    return [lerp(c0[0],c1[0],k),lerp(c0[1],c1[1],k),math.exp(lerp(math.log(c0[2]),math.log(c1[2]),k))]
@lru_cache(64)
def _relief_img(key,W,H):
    lc,bc,ppd=key; p=cam_proj((lc,bc,ppd)); s=W/1024
    q=Proj((p.l0,p.b0,p.l1,p.b1),0,0,W,H)
    rgb=_relief(q,W,H,ppd)
    return skia.Image.fromarray(np.dstack([rgb,np.full(rgb.shape[:2],255,np.uint8)]),colorType=skia.kRGBA_8888_ColorType)
@lru_cache(8)
def _master(c0,c1,W):
    s=W/1024; ppd=max(c0[2],c1[2])*s*1.0
    bbs=[]
    for c in (c0,c1):
        q=cam_proj(c); bbs.append((q.l0,q.b0,q.l1,q.b1))
    l0=min(b[0] for b in bbs); b0=min(b[1] for b in bbs); l1=max(b[2] for b in bbs); b1=max(b[3] for b in bbs)
    k=math.cos(math.radians((b0+b1)/2)); iw=int((l1-l0)*k*ppd)+2; ih=int((b1-b0)*ppd)+2
    if iw*ih>9e6: f=math.sqrt(9e6/(iw*ih)); iw,ih=int(iw*f),int(ih*f)
    q=Proj((l0,b0,l1,b1),0,0,iw,ih); 
    # Proj keeps aspect: recompute exact bbox it maps to image rect
    L0=q.ml-(iw/2)/(q.k*q.s); L1=q.ml+(iw/2)/(q.k*q.s); B1=q.mb+(ih/2)/q.s; B0=q.mb-(ih/2)/q.s
    ppd_eff=q.s/s
    rgb=_relief(q,iw,ih,ppd_eff)
    return skia.Image.fromarray(np.dstack([rgb,np.full(rgb.shape[:2],255,np.uint8)]),colorType=skia.kRGBA_8888_ColorType),(L0,B0,L1,B1)
@lru_cache(4)
def rivers():
    d=json.load(open(os.path.join(TR.GEOD,'rivers_50m.geojson'))); out=[]
    for f in d['features']:
        rv=MAPCFG.get('rivers',[])
        nm=f['properties'].get('name') or ''
        if (rv=='all' and f['properties'].get('scalerank',9)<=6) or (rv!='all' and nm in rv):
            g=f['geometry']; cs=g['coordinates'] if g['type']=='MultiLineString' else [g['coordinates']]
            out+= [np.array(c) for c in cs]
    if MAPCFG.get('wrap'):   # Pacific-centred maps: lon>180 also drawn (terrain tiles already wrap)
        out+= [r+np.array([360.,0]) for r in out if r[:,0].min()<0]
    return out
def map_bg(ctx,sc,t):
    cam=cam_at(sc,t); W,H=ctx.W,ctx.H
    # quantise camera to limit cache misses while keeping motion smooth (moving cams re-render)
    p=cam_proj(cam); u=U(ctx)
    if 'cam1' not in sc:
        key=(round(cam[0],3),round(cam[1],3),round(cam[2],2)); ctx.c.drawImageRect(_relief_img(key,W,H),skia.Rect.MakeWH(W,H))
    else:
        img,mb=_master(tuple(sc['cam']),tuple(sc['cam1']),W)   # mb = (l0,b0,l1,b1) of master image
        # affine: lon/lat -> screen via p; master pixel (0,0)=(l0,b1), (iw,ih)=(l1,b0)
        x0,y0=p(mb[0],mb[3]); x1,y1=p(mb[2],mb[1])
        ctx.c.drawImageRect(img,skia.Rect.MakeLTRB(float(x0)*u,float(y0)*u,float(x1)*u,float(y1)*u),skia.SamplingOptions(skia.FilterMode.kLinear))
    for r in rivers():
        X,Y=p(r[:,0],r[:,1]); path=skia.Path(); path.addPoly([skia.Point(float(x)*u,float(y)*u) for x,y in zip(X,Y)],False)
        ctx.c.drawPath(path,paint('#c8a560',.38*sc.get('river_a',1),stroke=1.1*u))
    ctx.proj=p
    # top darkening for caption legibility
    linear_grad(ctx.c,skia.Rect.MakeWH(W,H*.45),(0,0),(0,H*.45),[hexc('#0b0907',.55),hexc('#0b0907',0)])

def P(ctx,ll):
    if isinstance(ll,str): ll=CITY[ll]
    x,y=ctx.proj(*ll); return float(x),float(y)

# ---------------- night / stage backgrounds ----------------
@lru_cache(4)
def stars(seed=1,n=180):
    r=random.Random(seed); return [(r.uniform(0,1024),r.uniform(0,330),r.uniform(.3,1.2),r.uniform(.15,.7),r.uniform(0,6.3)) for _ in range(n)]
def sky(ctx,top='#0b0b10',mid='#17121a',hz='#2a1c14',hy=400,t=0,star_a=1.):
    c=ctx.c; u=U(ctx); W,H=ctx.W,ctx.H
    linear_grad(c,skia.Rect.MakeWH(W,H),(0,0),(0,hy*u),[hexc(top),hexc(mid),hexc(hz)],[0,.6,1])
    for x,y,r,a,ph in stars():
        if y<hy-40: c.drawCircle(x*u,y*u,r*u,paint('#f4ecdc',star_a*a*(.75+.25*math.sin(t*1.3+ph))))
def ridge_line(c,u,y0,amp,seed,col,a=1.,n=60):
    r=random.Random(seed); p=skia.Path(); p.moveTo(0,576*u); ys=[]
    v=0
    for i in range(n+1):
        v=v*.7+r.uniform(-1,1); ys.append(y0-amp*(.5+.5*math.sin(i*.37+seed)+.35*v))
    for i,y in enumerate(ys): p.lineTo(i*1024/n*u,y*u)
    p.lineTo(1024*u,576*u); p.close(); c.drawPath(p,paint(col,a))
def ground(ctx,y=420,col='#1d140d',glow=None,ga=.5):
    c=ctx.c; u=U(ctx)
    c.drawRect(skia.Rect.MakeLTRB(0,y*u,ctx.W,ctx.H),paint(col))
    if glow: c.drawOval(skia.Rect.MakeXYWH((glow[0]-glow[2])*u,(y-glow[2]*.35)*u,glow[2]*2*u,glow[2]*.9*u),paint('#e08a30',ga*.35,blur=60*u))

# ---------------- props ----------------
def flame(c,x,y,s,t,u,a=1.,seed=0):
    """procedural layered flame; (x,y)=base centre, s=height (design units)"""
    if a<=0 or s<=0: return
    r=random.Random(seed)
    c.drawCircle(x*u,(y-s*.45)*u,s*2.6*u,paint('#ff8a20',a*.16,blur=s*1.2*u)); c.drawCircle(x*u,(y-s*.4)*u,s*1.1*u,paint('#ffb040',a*.35,blur=s*.5*u))
    for L,(col,w,ha) in enumerate([('#d8461c',.72,1.0),('#ff8a22',.64,.9),('#ffc54a',.52,.74),('#fff6d8',.38,.52)]):
        fl=1+.12*math.sin(t*11+seed+L*1.7)+.07*math.sin(t*17.3+seed*2+L)
        h=s*ha*fl; ww=s*w; sway=math.sin(t*6.3+seed+L)*s*.06
        p=skia.Path(); p.moveTo((x-ww/2)*u,y*u)
        p.cubicTo((x-ww*.7)*u,(y-h*.45)*u,(x-ww*.15+sway)*u,(y-h*.75)*u,(x+sway*1.6)*u,(y-h)*u)
        p.cubicTo((x+ww*.15+sway)*u,(y-h*.7)*u,(x+ww*.7)*u,(y-h*.45)*u,(x+ww/2)*u,y*u); p.close()
        c.drawPath(p,paint(col,a*(.9 if L else .8),blur=(1.4 if L<3 else 2.2)*u))
    for i in range(6):   # sparks
        ph=(t*.9+r.random())%1; sx=x+r.uniform(-s*.3,s*.3)+math.sin(t*3+i)*4; sy=y-s*(.8+ph*1.4)
        c.drawCircle(sx*u,sy*u,1.1*u,paint('#ffb050',a*(1-ph)*.9))
def tower(c,x,y,h,u,a=1.,col='#3a2e24',lit=0.):
    """brick beacon tower (trapezoid), base centre (x,y), height h"""
    w0,w1=h*.78,h*.54; p=skia.Path(); p.moveTo((x-w0/2)*u,y*u); p.lineTo((x-w1/2)*u,(y-h)*u); p.lineTo((x+w1/2)*u,(y-h)*u); p.lineTo((x+w0/2)*u,y*u); p.close()
    c.drawPath(p,paint(col,a))
    c.save(); c.clipPath(p,doAntiAlias=True)
    for i in range(1,int(h/9)):
        yy=y-i*9; c.drawLine((x-w0)*u,yy*u,(x+w0)*u,yy*u,paint('#000000',a*.18,stroke=.8*u))
    if lit: c.drawRect(skia.Rect.MakeLTRB((x-w0)*u,(y-h)*u,(x+w0)*u,y*u),paint('#ff9a40',a*lit*.35,blend=skia.BlendMode.kScreen))
    c.restore()
    # crenels
    for i in range(5):
        cx=x-w1/2+w1*(i+.5)/5; c.drawRect(skia.Rect.MakeXYWH((cx-w1*.06)*u,(y-h-h*.06)*u,w1*.12*u,h*.06*u),paint(col,a))
    # door
    dw=h*.11; c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((x-dw/2)*u,(y-dw*1.6)*u,dw*u,dw*1.6*u),dw/2*u,dw/2*u),paint('#0e0a08',a))
def tower_stage(c,x,y,h,u,a=1.,col='#3e3127'):
    """big left tower with hut + ladder (tower-row scene)"""
    tower(c,x,y,h,u,a,col)
    hw=h*.16; c.drawRect(skia.Rect.MakeXYWH((x-hw/2)*u,(y-h-h*.2)*u,hw*u,h*.15*u),paint(col,a))
    p=skia.Path(); p.moveTo((x-hw*.75)*u,(y-h-h*.19)*u); p.lineTo(x*u,(y-h-h*.28)*u); p.lineTo((x+hw*.75)*u,(y-h-h*.19)*u); p.close(); c.drawPath(p,paint(col,a))
    lx=x-h*.25
    for s in (0,1): c.drawLine((lx+s*8)*u,y*u,(lx+s*8+h*.07)*u,(y-h)*u,paint('#6a5848',a*.8,stroke=1.1*u))
    for i in range(1,14): yy=y-i*h/14; f=i/14; c.drawLine((lx+f*h*.07)*u,yy*u,(lx+8+f*h*.07)*u,yy*u,paint('#6a5848',a*.7,stroke=.9*u))
def stand(c,x,y,u,a=1.,lit=1.,t=0,seed=0,fs=66):
    """fire stand: stepped base + pole + basket + flame"""
    c.drawPath(_trap(x,y,64,46,22,u),paint('#5c4a38',a)); c.drawRect(skia.Rect.MakeXYWH((x-2.5)*u,(y-22-50)*u,5*u,50*u),paint('#6b553d',a))
    c.drawRect(skia.Rect.MakeXYWH((x-9)*u,(y-72-32)*u,18*u,32*u),paint('#8a6a42',a))
    for i in range(4): c.drawLine((x-9)*u,(y-76-i*7)*u,(x+9)*u,(y-76-i*7)*u,paint('#3a2a1a',a,stroke=.9*u))
    if lit>0: flame(c,x,y-102,fs*lit,t,u,a,seed)
def chimney(c,x,y,u,a=1.,h=118,col='#2c241d'):
    p=skia.Path(); p.moveTo((x-17)*u,y*u); p.lineTo((x-11)*u,(y-h)*u); p.lineTo((x+11)*u,(y-h)*u); p.lineTo((x+17)*u,y*u); p.close()
    c.drawPath(p,paint(col,a)); c.drawRect(skia.Rect.MakeXYWH((x-12)*u,(y-h-4)*u,24*u,5*u),paint('#3a3028',a))
    c.drawRect(skia.Rect.MakeXYWH((x-5)*u,(y-16)*u,10*u,10*u),paint('#0a0806',a))
def _trap(x,y,w0,w1,h,u):
    p=skia.Path(); p.moveTo((x-w0/2)*u,y*u); p.lineTo((x-w1/2)*u,(y-h)*u); p.lineTo((x+w1/2)*u,(y-h)*u); p.lineTo((x+w0/2)*u,y*u); p.close(); return p
def palace(c,x,y,s,u,a=1.):
    """small gold palace icon (city marker), base centre"""
    c.drawRect(skia.Rect.MakeXYWH((x-s*.55)*u,(y-s*.32)*u,s*1.1*u,s*.32*u),paint('#6a4a26',a))
    c.drawRect(skia.Rect.MakeXYWH((x-s*.42)*u,(y-s*.6)*u,s*.84*u,s*.28*u),paint('#a01e18',a))
    for i in range(4): c.drawRect(skia.Rect.MakeXYWH((x-s*.36+i*s*.22)*u,(y-s*.56)*u,s*.07*u,s*.2*u),paint('#f0c060',a))
    p=skia.Path(); p.moveTo((x-s*.75)*u,(y-s*.58)*u); p.quadTo(x*u,(y-s*.72)*u,(x+s*.75)*u,(y-s*.58)*u); p.lineTo((x+s*.45)*u,(y-s*.9)*u); p.lineTo((x-s*.45)*u,(y-s*.9)*u); p.close()
    c.drawPath(p,paint('#e0a840',a)); c.drawCircle(x*u,(y-s*.5)*u,s*1.1*u,paint('#f0b050',a*.18,blur=s*.6*u))

# ---------------- elements ----------------
def caption(ctx,e,t,frame):
    """top-left narration; per-line blur-in reveal; [gold] {red} keyword runs with underline"""
    if t<e['t0']: return
    a=env(e,t,.35,.35)
    if a<=0: return
    c=ctx.c; u=U(ctx); f=F('serif-vf',e.get('size',37)*u,900); x0=e.get('x',62)*u
    lines=wrap_markup(e['text'],f,e.get('max_w',660)*u); st=e.get('stagger',.45)
    for i,ln in enumerate(lines):
        at_=e.get('at'); tl=e['t0']+(at_[min(i,len(at_)-1)]+(i-len(at_)+1)*st*(i>=len(at_)) if isinstance(at_,list) else i*st)
        k=ease_out_cubic(prog(t,tl,.55))
        if k<=0: continue
        y=(e.get('y',91)+i*e.get('lh',60))*u
        runs=[]; mode=None; buf=''
        for ch in ln:
            if ch in '[{':
                if buf: runs.append((buf,mode)); buf=''
                mode='g' if ch=='[' else 'r'
            elif ch in ']}':
                runs.append((buf,mode)); buf=''; mode=None
            else: buf+=ch
        if buf: runs.append((buf,mode))
        x=x0 if e.get('align','left')=='left' else e.get('x',512)*u-sum(f.measureText(s) for s,_ in runs)/2
        for s,m in runs:
            col=GOLD if m=='g' else RED if m=='r' else e.get('color',WHITE); w=f.measureText(s)
            blur=(1-k)*6*u
            draw_text(c,s,x+2*u,y+2*u,f,'#000000',a*k*.55,'left')
            p=paint(col,a*k,blur=blur) ; c.drawString(s,x,y,f,p)
            if m: c.drawRect(skia.Rect.MakeXYWH(x,y+7*u,w*ease_out_cubic(prog(t,tl+.3,.5)),2.2*u),paint(col,a*k*.9))
            x+=w
def cite(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a>0: u=U(ctx); draw_text(ctx.c,e['text'],e.get('x',512)*u,e.get('y',566)*u,F('sans',8.2*u),'#b8ad9c',a*.85)
def label(ctx,e,t,frame):
    a=env(e,t,.3,.3)
    if a<=0: return
    u=U(ctx); x,y=(P(ctx,e['at']) if 'at' in e else (e['x'],e['y']))
    x+=e.get('dx',0); y+=e.get('dy',0)
    draw_text(ctx.c,e['text'],x*u,y*u,F(e.get('font','serif-vf'),e.get('size',15)*u,e.get('weight',700)),e.get('color',WHITE),a,e.get('align','center'),glow=e.get('glow',0)*u,glow_color=e.get('glow_color'))
def counter(ctx,e,t,frame):
    """right-top gold counter: small head label, big number (+unit), sub lines"""
    a=env(e,t,.3,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x=e.get('x',900)*u; y=e.get('y',62)*u
    if e.get('head'): draw_text(c,e['head'],x,y-e.get('size',34)*1.25*u,F('sans',e.get('hsize',11)*u),'#d8cdb8',a)
    if 'vals' in e:   # stepped values [[t,val],...]
        v=e['vals'][0][1]; prev=0; un_=None
        for row in e['vals']:
            tt,vv=row[0],row[1]
            if t>=tt and len(row)>2: un_=row[2]
            if t>=tt:
                kk=ease_out_cubic(prog(t,tt,e.get('step_dur',1.4)))
                v=str(round(lerp(float(prev),float(vv),kk))) if str(vv).isdigit() else vv
            prev=vv if t>=tt else prev
    else:
        k=ease_out_cubic(prog(t,e.get('count_at',e['t0']),e.get('dur',1.5))); v=round(lerp(e['from'],e['to'],k))
    s=f"{v}" if not isinstance(v,str) else v
    fn=F('serif-vf',e.get('size',34)*u,900); fu=F('serif-vf',e.get('usize',22)*u,800); un=e.get('unit','') if 'vals' not in e or un_ is None else un_
    tw=fn.measureText(s)+fu.measureText(un)+(6*u if un else 0); xx=x-tw/2
    draw_text(c,s,xx,y,fn,e.get('color',GOLD),a,'left',glow=4*u,glow_color='#a07020'); draw_text(c,un,xx+fn.measureText(s)+6*u,y,fu,e.get('color',GOLD),a,'left')
    for i,(sub,col) in enumerate(e.get('subs',[])): draw_text(c,sub,x,y+(22+i*24)*u,F('serif-vf',(12 if i==0 else 18)*u,800),col,a)
def chain(ctx,e,t,frame):
    """beacon chain: beads along lon/lat route lighting up sequentially; glowing fire head; optional trail glow line"""
    a=env(e,t,.3,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); pts=np.array([P(ctx,q) for q in e['route']],float)
    if e.get('smooth',True) and len(pts)>2:
        from scipy.interpolate import splprep,splev
        try:
            tck,_=splprep(pts.T,s=0,k=min(3,len(pts)-1)); pts=np.array(splev(np.linspace(0,1,300),tck)).T
        except Exception: pass
    seg=np.hypot(*np.diff(pts,axis=0).T); cum=np.concatenate([[0],np.cumsum(seg)]); L=cum[-1]
    k=(ease_out_cubic if e.get('ease')=='out' else ease_in_out_cubic)(prog(t,e.get('draw_at',e['t0']),e.get('dur',2.0)))
    p,_=LN.path_from(pts,u,k)
    if e.get('line',False): LN.glow_path(c,p,u,'#ffb43c',a,e.get('w',1.6),8,core='#fff0b8')
    elif p is not None: c.drawPath(p,paint('#ff9a30',a*.35,stroke=6*u,blur=5*u))
    sp=e.get('spacing',9); n=int(L/sp)
    for i in range(n+1):
        d=i*sp
        if d>L*k: break
        x=np.interp(d,cum,pts[:,0]); y=np.interp(d,cum,pts[:,1]); age=(L*k-d)/max(L,1)
        b=.55+.45*math.sin(t*5+i*.9)
        c.drawCircle(x*u,y*u,e.get('r',2.3)*u,paint('#ffd070',a*(.7+.3*b)))
        c.drawCircle(x*u,y*u,6*u,paint('#ff9a30',a*.3*b,blur=3*u))
    if 0<k and e.get('head',True):
        d=L*k; x=np.interp(d,cum,pts[:,0]); y=np.interp(d,cum,pts[:,1])
        if k<1 or e.get('head_hold',True):
            c.drawCircle(x*u,y*u,34*u,paint('#ff9a30',a*.35,blur=16*u)); c.drawCircle(x*u,y*u,12*u,paint('#ffd080',a*.8,blur=5*u)); c.drawCircle(x*u,y*u,5*u,paint('#fff6d8',a,blur=1.2*u))
def faintroute(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    u=U(ctx); pts=[P(ctx,q) for q in e['route']]; p,_=LN.path_from(pts,u,ease_in_out_cubic(prog(t,e['t0'],e.get('dur',1.)))); 
    if p: ctx.c.drawPath(p,paint(e.get('color','#d8c8a0'),a*.5,stroke=e.get('w',.9)*u))
def city(ctx,e,t,frame):
    a=env(e,t,.3,.4)
    if a<=0: return
    u=U(ctx); x,y=P(ctx,e['at']) if 'at' in e else (e['x'],e['y']); k=ease_out_back(prog(t,e['t0'],.4))
    s=e.get('s',16)*max(k,.01)
    if e.get('halo',True): ctx.c.drawOval(skia.Rect.MakeXYWH((x-s*2.2)*u,(y-s*.5)*u,s*4.4*u,s*1.0*u),paint('#f0b050',a*.35,blur=s*.5*u))
    palace(ctx.c,x,y,s,u,a)
    if e.get('label',True): draw_text(ctx.c,e.get('name',e.get('at')),(x+e.get('ldx',0))*u,(y+e.get('ldy',20))*u,F('serif-vf',e.get('size',15)*u,900),e.get('lcolor',GOLD),a,glow=3*u,glow_color='#000000')
def fire(ctx,e,t,frame):
    a=env(e,t,.3,.4)
    if a<=0: return
    u=U(ctx); x,y=P(ctx,e['at']) if 'at' in e else (e['x'],e['y'])
    flame(ctx.c,x,y,e.get('s',14)*ease_out_cubic(prog(t,e['t0'],.5)),t,u,a,e.get('seed',0))
def ring(ctx,e,t,frame):
    """dashed radius ring with optional radius line + label"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=P(ctx,e['at']) if 'at' in e else (e['x'],e['y']); r=e.get('r',60)
    k=ease_in_out_cubic(prog(t,e['t0'],e.get('dur',.9)))
    p=skia.Path(); p.addArc(skia.Rect.MakeLTRB((x-r)*u,(y-r)*u,(x+r)*u,(y+r)*u),-90,360*k)
    pt=paint(e.get('color','#e8dcc4'),a*.8,stroke=1.2*u); pt.setPathEffect(skia.DashPathEffect.Make([5*u,4*u],0)); c.drawPath(p,pt)
    if e.get('radius'): 
        ang=math.radians(e.get('ang',-150)); c.drawLine(x*u,y*u,(x+math.cos(ang)*r*k)*u,(y+math.sin(ang)*r*k)*u,paint('#e8dcc4',a*.8,stroke=1*u))
    if e.get('text'): draw_text(c,e['text'],(x+e.get('tdx',0))*u,(y+e.get('tdy',-r-8))*u,F('serif-vf',e.get('size',15)*u,900),e.get('tcolor',RED),a)
def slash(ctx,e,t,frame):
    a=env(e,t,.2,.3)
    if a<=0: return
    u=U(ctx); x,y=P(ctx,e['at']) if 'at' in e else (e['x'],e['y']); k=ease_out_cubic(prog(t,e['t0'],.35)); L=e.get('L',22)
    for s in ((1,1),(-1,1)) if e.get('cross') else ((1,1),):
        ctx.c.drawLine((x-L*s[0])*u,(y-L*.6)*u,(x-L*s[0]+2*L*s[0]*k)*u,(y-L*.6+1.2*L*k)*u,paint(RED,a,stroke=2.6*u))
def badge(ctx,e,t,frame):
    """round moon badge (每天入夜)"""
    a=env(e,t,.3,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,r=e.get('x',920),e.get('y',60),e.get('r',18)
    c.drawCircle(x*u,y*u,r*u,paint('#14161c',a)); c.drawCircle(x*u,y*u,r*u,paint('#8a8478',a*.8,stroke=1*u))
    c.drawCircle((x-3)*u,(y+2)*u,5*u,paint('#f4ecd8',a)); c.drawCircle((x-1)*u,(y)*u,4.6*u,paint('#14161c',a))
    if e.get('text'): draw_text(c,e['text'],x*u,(y+r+16)*u,F('sans',11*u),'#d8cdb8',a)
    if e.get('top'): draw_text(c,e['top'],x*u,(y-r*.35)*u,F('sans',8*u),'#d8cdb8',a)
def bigword(ctx,e,t,frame):
    """big glowing word (没来 / 我还在 / 公元756年): blur-in, optional red/gold"""
    a=env(e,t,.4,.4)
    if a<=0: return
    u=U(ctx); k=ease_out_cubic(prog(t,e['t0'],.6)); f=F('serif-vf',e.get('size',40)*u,900)
    p=paint(e.get('color',GOLD),a*k,blur=(1-k)*8*u)
    draw_text(ctx.c,e['text'],e['x']*u,e['y']*u,f,e.get('color',GOLD),a*k*.6,e.get('align','center'),glow=6*u,glow_color=e.get('glow_color','#7a4a10'))
    tw=f.measureText(e['text']); xx=e['x']*u-(tw/2 if e.get('align','center')=='center' else 0)
    ctx.c.drawString(e['text'],xx,e['y']*u,f,p)
def card(ctx,e,t,frame):
    """parchment card with title + vertical text columns + optional red seals"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,w,h=e['box']; k=ease_out_cubic(prog(t,e['t0'],.6)); y+= (1-k)*14
    c.drawRect(skia.Rect.MakeXYWH((x+4)*u,(y+5)*u,w*u,h*u),paint('#000000',a*.45,blur=6*u))
    c.drawRect(skia.Rect.MakeXYWH(x*u,y*u,w*u,h*u),paint(e.get('paper',PAPER),a))
    c.drawRect(skia.Rect.MakeXYWH((x+4)*u,(y+4)*u,(w-8)*u,(h-8)*u),paint('#8a6a40',a*.6,stroke=.8*u))
    if e.get('title'): draw_text(c,e['title'],(x+w/2)*u,(y+22)*u,F('serif-vf',11*u,900),'#3a2a18',a)
    if e.get('lines'):
        for i,ln in enumerate(e['lines']):
            draw_text(c,ln,(x+12)*u,(y+44+i*15)*u,F('serif-vf',8.6*u,600),'#3a2a18',a*.9,'left')
    for sx,sy,txt in e.get('seals',[]):
        ks=prog(t,e.get('seal_at',e['t0']+.6),.25)
        if ks>0:
            rrect(c,(x+sx)*u,(y+sy)*u,38*u,18*u,2*u,stroke='#c0302a',a=a*ks,sw=1.4*u); draw_text(c,txt,(x+sx+19)*u,(y+sy+13)*u,F('serif-vf',9*u,900),'#c0302a',a*ks)
def book(ctx,e,t,frame):
    """open book: two parchment pages, vertical columns of text (right-to-left), red heading"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,w,h=e['box']; k=ease_out_cubic(prog(t,e['t0'],.6))
    c.drawRect(skia.Rect.MakeXYWH((x-6)*u,(y-6)*u,(w+12)*u,(h+12)*u),paint('#5a3c22',a)); c.drawRect(skia.Rect.MakeXYWH((x+3)*u,(y+8)*u,w*u,h*u),paint('#000000',a*.4,blur=8*u))
    for side in (0,1):
        c.drawRect(skia.Rect.MakeXYWH((x+side*w/2)*u,y*u,(w/2-1)*u,h*u),paint('#e2d2ae',a))
        for i in range(1,9): c.drawLine((x+side*w/2+i*w/18)*u,(y+12)*u,(x+side*w/2+i*w/18)*u,(y+h-12)*u,paint('#a08a60',a*.35,stroke=.6*u))
    c.drawLine((x+w/2)*u,y*u,(x+w/2)*u,(y+h)*u,paint('#6a5030',a,stroke=1.5*u))
    if e.get('head'): draw_text(c,e['head'],(x+w/2)*u,(y-14)*u,F('serif-vf',13*u,900),'#f0e4c8',a)
    cols=e.get('cols',[])  # list of (text,color) right to left
    for i,(txt,col) in enumerate(cols):
        cx=x+w-14-i*w/18; kk=prog(t,e['t0']+.4+i*.08,.3)
        for j,ch in enumerate(txt): draw_text(c,ch,cx*u,(y+26+j*15)*u,F('serif-vf',11*u,800),col,a*kk)
def slips(ctx,e,t,frame):
    """wooden bamboo slips (木简) standing"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx)
    for i,(x,y,h,ang) in enumerate(e['items']):
        k=ease_out_cubic(prog(t,e['t0']+i*.15,.5)); c.save(); c.translate(x*u,y*u); c.rotate(ang)
        c.drawRect(skia.Rect.MakeXYWH(-8*u,-h*k*u,16*u,h*k*u),paint('#b48a50',a)); c.drawRect(skia.Rect.MakeXYWH(-8*u,-h*k*u,16*u,h*k*u),paint('#6a4a28',a,stroke=1*u))
        for j in range(int(h/22)):
            if (j+i)%3!=2: c.drawRect(skia.Rect.MakeXYWH(-3*u,(-h*k+10+j*20)*u,6*u,8*u),paint('#2a1a10',a*.85*k))
        c.restore()
def bubble(ctx,e,t,frame):
    a=env(e,t,.25,.3)
    if a<=0: return
    c=ctx.c; u=U(ctx); f=F('serif-vf',e.get('size',13)*u,900); w=f.measureText(e['text'])+20*u; x,y=e['x']*u,e['y']*u
    rrect(c,x-w/2,y-14*u,w,26*u,13*u,fill='#16110c',a=a*.9); rrect(c,x-w/2,y-14*u,w,26*u,13*u,stroke=GOLD,a=a,sw=1*u)
    draw_text(c,e['text'],x,y+4.5*u,f,e.get('color',GOLD),a)
def dashline(ctx,e,t,frame):
    a=env(e,t,.3,.3)
    if a<=0: return
    u=U(ctx); k=ease_in_out_cubic(prog(t,e['t0'],e.get('dur',1.))); x0,y0,x1,y1=e['xy']
    pt=paint(e.get('color','#d8ccb0'),a*.8,stroke=1.1*u); pt.setPathEffect(skia.DashPathEffect.Make([4*u,4*u],0))
    ctx.c.drawLine(x0*u,y0*u,lerp(x0,x1,k)*u,lerp(y0,y1,k)*u,pt)
def rider(ctx,e,t,frame):
    """courier on horse silhouette moving along a route (lon/lat), with dust"""
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c; u=U(ctx); pts=np.array([P(ctx,q) for q in e['route']]); seg=np.hypot(*np.diff(pts,axis=0).T); cum=np.concatenate([[0],np.cumsum(seg)])
    d=cum[-1]*ease_in_out_cubic(prog(t,e.get('go_at',e['t0']),e.get('dur',3))); x=np.interp(d,cum,pts[:,0]); y=np.interp(d,cum,pts[:,1])
    s=e.get('s',10); b=math.sin(t*14)*1.2
    p=skia.Path(); p.addOval(skia.Rect.MakeXYWH((x-s)*u,(y-s*.9+b)*u,s*2*u,s*.8*u)); c.drawPath(p,paint('#f0c060',a))
    c.drawCircle((x+s*1.1)*u,(y-s*1.1+b)*u,s*.35*u,paint('#f0c060',a)); c.drawCircle(x*u,(y-s*1.5+b)*u,s*.3*u,paint('#f0c060',a))
    for i in range(4): c.drawLine((x-s*.7+i*s*.45)*u,(y-s*.2)*u,(x-s*.7+i*s*.45+math.sin(t*14+i*1.5)*3)*u,(y+s*.5)*u,paint('#f0c060',a,stroke=1.2*u))
    c.drawCircle(x*u,y*u,s*2.2*u,paint('#f0b050',a*.25,blur=s*u))

def stage(ctx,sc,t):
    """night tower-row stage: starry sky, distant ridge, ground, big tower left, stands/chimneys row"""
    c=ctx.c; u=U(ctx); sky(ctx,'#07080c','#120f13','#2b1d14',hy=400,t=t)
    ridge_line(c,u,402,26,3,'#17120f'); ground(ctx,y=420,col='#1e150e',glow=(690,420,330),ga=sc.get('gl',.7))
    tower_stage(c,sc.get('tx',210),436,180,u,1.,'#4e4034')
    for i,item in enumerate(sc.get('row',[])):
        x=item['x']
        if item['k']=='c': chimney(c,x,436,u)
        else:
            lit=item.get('lit',[]); on=any(a0<=t<a1 for a0,a1 in lit); ko=max([prog(t,a0,.35)*(1-prog(t,a1-.3,.3)) for a0,a1 in lit] or [0])
            stand(c,x,436,u,1.,ko,t,i)
def night(ctx,sc,t):
    c=ctx.c; u=U(ctx); sky(ctx,'#06070b','#12101a','#3a2618',hy=430,t=t)
    ridge_line(c,u,410,40,7,'#151116'); ridge_line(c,u,440,22,9,'#100c0a')
    for i in range(40):
        r=random.Random(i); x=r.uniform(40,500); y=r.uniform(418,445); c.drawCircle(x*u,y*u,1.3*u,paint('#ffa040',.6+.4*math.sin(t*3+i)))
    p=skia.Path(); p.moveTo(0,576*u); p.quadTo(512*u,415*u,1024*u,470*u); p.lineTo(1024*u,576*u); p.close(); c.drawPath(p,paint('#20160e'))
    c.drawOval(skia.Rect.MakeXYWH(300*u,390*u,500*u,220*u),paint('#d08030',.32,blur=50*u))
    moon_x,moon_y=sc.get('moon',(710,245)); c.drawCircle(moon_x*u,moon_y*u,7*u,paint('#f4ecd8')); c.drawCircle((moon_x+3)*u,(moon_y-1.5)*u,6.3*u,paint('#0c0b10'))
def citygate(ctx,sc,t):
    c=ctx.c; u=U(ctx); sky(ctx,'#0c0a0e','#2a1812','#7a3a1c',hy=340,t=t,star_a=.6)
    c.drawRect(skia.Rect.MakeLTRB(0,330*u,ctx.W,ctx.H),paint('#0e0b09'))
    ridge_line(c,u,330,22,4,'#1a1210')
    # wall
    c.drawRect(skia.Rect.MakeXYWH(0,260*u,500*u,72*u),paint('#3a2e26'))
    for i in range(30): c.drawRect(skia.Rect.MakeXYWH(i*17*u,252*u,9*u,9*u),paint('#3a2e26'))
    c.drawRect(skia.Rect.MakeXYWH(196*u,236*u,152*u,96*u),paint('#4a3a2e')); c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(250*u,272*u,40*u,60*u),20*u,20*u),paint('#0a0806'))
    c.drawRect(skia.Rect.MakeXYWH(220*u,196*u,104*u,42*u),paint('#7a1a14'))
    for i in range(6): c.drawRect(skia.Rect.MakeXYWH((228+i*16)*u,204*u,7*u,22*u),paint('#e0b050',.9))
    p=skia.Path(); p.moveTo(190*u,198*u); p.quadTo(272*u,186*u,354*u,198*u); p.lineTo(330*u,176*u); p.lineTo(214*u,176*u); p.close(); c.drawPath(p,paint('#c89a40'))
    for i,x in enumerate([600,660,720,790,850]): tower(c,x,334,48-i*4,u,1.,'#2a221c')
def fog(ctx,sc,t):
    c=ctx.c; u=U(ctx); sky(ctx,'#07080c','#100e14','#1f1812',hy=440,t=t)
    ridge_line(c,u,440,30,5,'#141012')
    p=skia.Path(); p.moveTo(0,576*u); p.lineTo(0,520*u); p.quadTo(200*u,470*u,420*u,520*u); p.quadTo(700*u,540*u,1024*u,510*u); p.lineTo(1024*u,576*u); p.close(); c.drawPath(p,paint('#3a2616'))
    c.drawOval(skia.Rect.MakeXYWH(0,380*u,420*u,240*u),paint('#e08030',.3,blur=50*u))
    tower(c,115,528,95,u,1.,'#4a3a2c',lit=.4); flame(c,115,438,48,t,u,1.,3)
    tower(c,395,505,56,u,.45,'#2e2620')
    for i in range(5):   # drifting mist bands
        ph=(t*.01+i*.19)%1; c.drawOval(skia.Rect.MakeXYWH((380+ph*300+i*40)*u,(300+i*35)*u,420*u,160*u),paint('#c8c2b8',.42*sc.get('fog',1),blur=50*u))
def dig(ctx,sc,t):
    c=ctx.c; u=U(ctx)
    linear_grad(c,skia.Rect.MakeWH(ctx.W,ctx.H),(0,0),(0,430*u),[hexc('#2a2a2c'),hexc('#5a5246'),hexc('#7a6a52')],[0,.7,1])
    ridge_line(c,u,465,18,11,'#5a5040'); c.drawRect(skia.Rect.MakeLTRB(0,470*u,ctx.W,ctx.H),paint('#8a7454'))
    for i in range(7): c.drawRect(skia.Rect.MakeXYWH((466+i*12)*u,(458-i*17-17)*u,(212-i*24)*u,17*u),paint(['#c8a878','#bfa070'][i%2]))
    for x,y in [(690,515),(720,522),(895,518),(925,527)]: c.drawOval(skia.Rect.MakeXYWH((x-16)*u,(y-6)*u,32*u,12*u),paint('#3a4a3a',.8))
    pt=paint('#e8dcc4',.4,stroke=.8*u)
    for i in range(5): c.drawLine((680+i*40)*u,535*u,(700+i*40)*u,576*u,pt)
    c.drawLine(670*u,545*u,900*u,545*u,pt)
def desk(ctx,sc,t):
    c=ctx.c; u=U(ctx)
    c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint('#17120d'))
    c.drawOval(skia.Rect.MakeXYWH(250*u,120*u,700*u,480*u),paint('#5a4028',.35,blur=80*u))

BG=dict(map=map_bg,stage=stage,night=night,citygate=citygate,fog=fog,dig=dig,desk=desk)
EXTRA=dict(caption=caption,cite=cite,label=label,counter=counter,chain=chain,faintroute=faintroute,city=city,fire=fire,ring=ring,slash=slash,
           badge=badge,bigword=bigword,card=card,book=book,slips=slips,bubble=bubble,dashline=dashline,rider=rider)

def draw(ctx,t,frame,S):
    c=ctx.c; act=[sc for sc in S['scenes'] if sc['t0']-1e-6<=t<sc['t1']+sc.get('xfade',0)]
    for j,sc in enumerate(act[:2]):
        if j==1 or len(act)==1 or True:
            pass
    sc=act[0] if act else None
    def render(sc,alpha):
        if alpha<=0: return
        if alpha<1: c.saveLayerAlpha(None,int(alpha*255))
        else: c.save()
        BG[sc.get('bg','map')](ctx,sc,t); draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)
        c.restore()
    if not act: c.clear(skia.Color(0,0,0)); return
    c.clear(skia.Color(0,0,0))
    render(act[0],1.)
    if len(act)>1:
        nx=act[1]; xf=act[0].get('xfade',0) or .01
        render(nx,prog(t,nx['t0'],nx.get('xin',xf)))
    draw_elements(ctx,S.get('overlays',[]),t,frame,EXTRA)
    vignette(c,ctx.W,ctx.H,.45); grain(c,ctx.W,ctx.H,frame,.035,10)

def towers(ctx,e,t,frame):
    """mini beacon towers (screen or lon/lat) lighting in sequence: items [[x,y,h]] ; light_at, step"""
    a=env(e,t,.3,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx)
    for i,it in enumerate(e['items']):
        x,y=(P(ctx,it[0]) if isinstance(it[0],(str,list,tuple)) else (it[0],it[1])); h=it[-1]
        tower(c,x,y,h,u,a,'#8a7a66')
        la=e.get('light_at',1e9)+i*e.get('step',.2)
        if t>=la: flame(c,x,y-h-1,h*.9*ease_out_cubic(prog(t,la,.3)),t,u,a,i)
def tokens(ctx,e,t,frame):
    """row of round item tokens with labels (柴/艾蒿/芦苇/狼粪)"""
    a=env(e,t,.3,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx)
    for i,(txt,col) in enumerate(e['items']):
        k=ease_out_back(prog(t,e['t0']+i*e.get('step',.4),.4)); x=e['x']+i*e.get('dx',110); y=e['y']; r=e.get('r',30)*max(k,.01)
        c.drawCircle(x*u,y*u,r*u,paint('#2a2016',a)); c.drawCircle(x*u,y*u,r*u,paint(col,a,stroke=1.6*u))
        for j in range(5): c.drawLine((x-r*.4+j*r*.2)*u,(y+r*.4)*u,(x-r*.27+j*r*.17)*u,(y-r*.47)*u,paint(col,a*.8,stroke=1.8*u))
        draw_text(c,txt,x*u,(y+e.get('r',30)+26)*u,F('serif-vf',20*u,900),col,a*prog(t,e['t0']+i*e.get('step',.4)+.2,.3))
def ripple(ctx,e,t,frame):
    a=env(e,t,.4,.5)
    if a<=0: return
    u=U(ctx); x,y=P(ctx,e['at']) if 'at' in e else (e['x'],e['y'])
    for i in range(4):
        ph=((t-e['t0'])*.45+i/4)%1; r=12+ph*e.get('r',90)
        ctx.c.drawOval(skia.Rect.MakeXYWH((x-r)*u,(y-r*.45)*u,2*r*u,.9*r*u),paint('#f0c060',a*(1-ph)*.6,stroke=1.4*u))
EXTRA.update(towers=towers,tokens=tokens,ripple=ripple)

# =====================================================================================================
# v3 RICH-SHOT EXTENSIONS (topic-agnostic). See TEMPLATE_GUIDE §7 dusk-map-chronicle "v3".
#   backgrounds: globe (orthographic, real NE land) | flat (equirect<->Mercator morph) | sky (altitude profile)
#                | dusk (generic dusk horizon for icon scenes); map gains cams keyframes + map.drift Ken Burns
#   elements:    plane, windflow, arrow, kmring, zone, tissot, panel, tag, motes, cloudshade, chapter,
#                storm, volcano, airport, topshade, borders, grat
#   transitions: scene.tin={type:fade|zoom|wipe|iris|flash|slide, dur, at:[x,y]}; scenes overlap by dur
# =====================================================================================================
LAND='#8a6e48'; LAND_HI='#c09040'; OCEAN0='#22323e'; OCEAN1='#0c1218'

@lru_cache(2)
def land_polys(step=2):
    d=json.load(open(os.path.join(TR.GEOD,'countries_50m.geojson'))); out=[]
    for f in d['features']:
        g=f['geometry']; pr=f['properties']
        if not g: continue
        cs=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
        for poly in cs:
            r=np.array(poly[0],float)
            if len(r)>60: r=r[::step]
            if len(r)>=3: out.append((pr.get('NAME',''),pr.get('NAME_ZH',''),r))
    return out
def _hl(nm,zh,hl): return bool(hl) and (nm in hl or zh in hl)

# ---------- generic projected path with break on wrap / hidden ----------
def _poly_path(X,Y,u,close=True,maxjump=None,vis=None):
    p=skia.Path(); pen=False
    for i in range(len(X)):
        ok=vis is None or vis[i]
        if not ok: pen=False; continue
        if pen and maxjump and abs(X[i]-X[i-1])>maxjump: pen=False
        if not pen: p.moveTo(float(X[i])*u,float(Y[i])*u); pen=True
        else: p.lineTo(float(X[i])*u,float(Y[i])*u)
    if close: p.close()
    return p

# ---------- globe ----------
class Ortho:
    def __init__(s,lon0,lat0,cx,cy,R):
        s.l0=math.radians(lon0); s.p0=math.radians(lat0); s.cx,s.cy,s.R=cx,cy,R; s.sp,s.cp=math.sin(s.p0),math.cos(s.p0)
    def xyz(s,lon,lat):
        lon=np.radians(np.asarray(lon,float)); lat=np.radians(np.asarray(lat,float)); cl=np.cos(lat); dl=lon-s.l0
        return cl*np.sin(dl), s.cp*np.sin(lat)-s.sp*cl*np.cos(dl), s.sp*np.sin(lat)+s.cp*cl*np.cos(dl)
    def __call__(s,lon,lat):
        x,y,z=s.xyz(lon,lat); n=np.hypot(x,y)+1e-9; b=z<0
        x=np.where(b,x/n,x); y=np.where(b,y/n,y); return s.cx+s.R*x, s.cy-s.R*y
    def visible(s,lon,lat): return s.xyz(lon,lat)[2]>=0
def globe_state(sc,t):
    g=sc.get('globe',{}); k=ease_in_out_cubic(prog(t,sc['t0']+g.get('at',0),g.get('dur',sc['t1']-sc['t0'])))
    r0=g.get('rot',[120,30]); r1=g.get('rot1',r0); spin=g.get('spin',0)*(t-sc['t0'])
    R=lerp(g.get('r',230),g.get('r1',g.get('r',230)),k); c0=g.get('c',[512,330]); c1=g.get('c1',c0)
    return Ortho(lerp(r0[0],r1[0],k)+spin,lerp(r0[1],r1[1],k),lerp(c0[0],c1[0],k),lerp(c0[1],c1[1],k),R)
def globe_bg(ctx,sc,t):
    c=ctx.c; u=U(ctx); W,H=ctx.W,ctx.H; g=sc.get('globe',{})
    linear_grad(c,skia.Rect.MakeWH(W,H),(0,0),(0,H),[hexc('#07080c'),hexc('#120f14'),hexc('#24180f')],[0,.6,1])
    for x,y,r,a,ph in stars(3,260): c.drawCircle(x*u,y*1.6*u,r*u,paint('#f4ecdc',a*(.7+.3*math.sin(t*1.3+ph))))
    o=globe_state(sc,t); cx,cy,R=o.cx*u,o.cy*u,o.R*u
    c.drawCircle(cx,cy,R*1.08,paint('#e0a050',.22,blur=R*.12))            # dusk atmosphere
    sh=skia.GradientShader.MakeRadial((cx-R*.3,cy-R*.35),R*1.4,[hexc(OCEAN0),hexc(OCEAN1)],[0,1])
    c.drawCircle(cx,cy,R,paint('#000000',1,shader=sh))
    c.save(); c.clipPath(skia.Path().addCircle(cx,cy,R),doAntiAlias=True)
    gs=g.get('grat',15)
    for la in range(-90+gs,90,gs):                                        # graticule
        lo=np.linspace(-180,180,181); X,Y=o(lo,np.full_like(lo,la)); v=o.visible(lo,np.full_like(lo,la))
        c.drawPath(_poly_path(X,Y,u,False,vis=v),paint('#c8a560',.22,stroke=.7*u))
    for lo0 in range(-180,180,gs):
        la=np.linspace(-89,89,90); X,Y=o(np.full_like(la,lo0),la); v=o.visible(np.full_like(la,lo0),la)
        c.drawPath(_poly_path(X,Y,u,False,vis=v),paint('#c8a560',.22,stroke=.7*u))
    hl=g.get('hl',[])
    for nm,zh,r in land_polys():
        x,y,z=o.xyz(r[:,0],r[:,1])
        if (z<0).all(): continue
        X,Y=o(r[:,0],r[:,1]); p=_poly_path(X,Y,u)
        c.drawPath(p,paint(LAND_HI if _hl(nm,zh,hl) else LAND,.95)); c.drawPath(p,paint('#d8b46a',.35,stroke=.6*u))
    # 3D shading + terminator + rim
    sh=skia.GradientShader.MakeRadial((cx-R*.35,cy-R*.4),R*1.55,[skia.Color(255,220,160,50),skia.Color(0,0,0,0),skia.Color(0,0,0,150)],[0,.55,1])
    c.drawRect(skia.Rect.MakeWH(W,H),paint('#000000',1,shader=sh)); c.restore()
    c.drawCircle(cx,cy,R,paint('#f0c070',.55,stroke=1.4*u,blur=1.2*u))
    ctx.proj=o; ctx.ppd=o.R*math.pi/180
    linear_grad(c,skia.Rect.MakeWH(W,H*.42),(0,0),(0,H*.42),[hexc('#0b0907',.6),hexc('#0b0907',0)])

# ---------- flat world, equirect <-> Mercator morph ----------
def merc_deg(lat): lat=np.clip(np.asarray(lat,float),-85,85); return np.degrees(np.log(np.tan(np.pi/4+np.radians(lat)/2)))
class Flat:
    def __init__(s,m,lc,cyl,sx,cx=512,cy=330): s.m,s.lc,s.cyl,s.sx,s.cx,s.cy=m,lc,cyl,sx,cx,cy
    def _y(s,lat): return lerp(np.asarray(lat,float),merc_deg(lat),s.m)
    def __call__(s,lon,lat):
        dl=(np.asarray(lon,float)-s.lc+180)%360-180
        return s.cx+dl*s.sx, s.cy-(s._y(lat)-s._y(s.cyl))*s.sx
def flat_state(sc,t):
    f=sc.get('flat',{}); k=ease_in_out_cubic(prog(t,sc['t0']+f.get('merc_at',0),f.get('merc_dur',2.5)))
    m=lerp(f.get('merc',0),f.get('merc1',f.get('merc',0)),k)
    kz=ease_in_out_cubic(prog(t,sc['t0']+f.get('zoom_at',0),f.get('zoom_dur',sc['t1']-sc['t0'])))
    sx=lerp(f.get('sx',2.7),f.get('sx1',f.get('sx',2.7)),kz)
    return Flat(m,f.get('lon',0),f.get('cy_lat',15),sx,f.get('cx',512),f.get('cy',330))
def flat_bg(ctx,sc,t):
    c=ctx.c; u=U(ctx); W,H=ctx.W,ctx.H; f=sc.get('flat',{}); o=flat_state(sc,t)
    linear_grad(c,skia.Rect.MakeWH(W,H),(0,0),(0,H),[hexc('#0c1014'),hexc('#141518'),hexc('#1b150f')],[0,.6,1])
    gs=f.get('grat',15)
    for la in range(-75,90,gs):
        _,y=o(0,la); c.drawLine(0,float(y)*u,W,float(y)*u,paint('#c8a560',.22 if la else .4,stroke=(.8 if la else 1.2)*u))
        if f.get('lat_labels',True) and la>=0 and la%30==0: draw_text(c,f'{la}°',14*u,(float(y)-4)*u,F('sans',10*u),'#c8a560',.7,'left')
    for lo in range(-180,180,gs):
        x,_=o(lo,0); c.drawLine(float(x)*u,0,float(x)*u,H,paint('#c8a560',.12,stroke=.7*u))
    hl=f.get('hl',[])
    for nm,zh,r in land_polys():
        lat=np.clip(r[:,1],-84,84); X,Y=o(r[:,0],lat); p=_poly_path(X,Y,u,maxjump=180*o.sx)
        c.drawPath(p,paint(LAND_HI if _hl(nm,zh,hl) else LAND,.95)); c.drawPath(p,paint('#d8b46a',.35,stroke=.6*u))
    ctx.proj=o; ctx.ppd=o.sx; ctx.flat=o
    linear_grad(c,skia.Rect.MakeWH(W,H*.42),(0,0),(0,H*.42),[hexc('#0b0907',.7),hexc('#0b0907',0)])

# ---------- sky altitude profile ----------
def sky_bg(ctx,sc,t):
    c=ctx.c; u=U(ctx); W,H=ctx.W,ctx.H; s=sc.get('sky',{})
    linear_grad(c,skia.Rect.MakeWH(W,H),(0,0),(0,H),[hexc('#070a12'),hexc('#1a1626'),hexc('#5a3220'),hexc('#c07a3a')],[0,.45,.82,1])
    for x,y,r,a,ph in stars(5,120):
        if y<200: c.drawCircle(x*u,y*u,r*u,paint('#f4ecdc',a*.7))
    ground=s.get('ground',520); amax=s.get('alt_max',15000); top=s.get('top',120)
    ctx.alt=lambda a: ground-(ground-top)*a/amax
    # earth limb
    p=skia.Path(); p.moveTo(0,H); p.lineTo(0,(ground+10)*u); p.quadTo(W/2,(ground-30)*u,W,(ground+10)*u); p.lineTo(W,H); p.close()
    c.drawPath(p,paint('#120d0a')); c.drawPath(p,paint('#ffb060',.5,stroke=2*u,blur=3*u))
    # cloud deck (drifting)
    r=random.Random(7)
    for i in range(26):
        x=(r.uniform(-100,1124)-t*s.get('cloud_v',6)*(1+i%3))%1224-100; y=ctx.alt(r.uniform(1500,4500)); w=r.uniform(90,220)
        c.drawOval(skia.Rect.MakeXYWH((x-w/2)*u,(y-w*.13)*u,w*u,w*.26*u),paint('#d8a878',.18,blur=10*u))
    # ruler
    for a in s.get('ticks',[0,5000,10000,15000]):
        y=ctx.alt(a); c.drawLine(58*u,y*u,74*u,y*u,paint('#e8dcc4',.8,stroke=1*u))
        draw_text(c,f'{a:,} m'.replace(',',' ') if a else '海平面',80*u,(y+4)*u,F('sans',11*u),'#e8dcc4',.85,'left')
    c.drawLine(66*u,ctx.alt(0)*u,66*u,ctx.alt(amax)*u,paint('#e8dcc4',.5,stroke=1*u))
    if s.get('band'):
        a0,a1,lab=s['band']; y0,y1=ctx.alt(a1),ctx.alt(a0); k=ease_out_cubic(prog(t,sc['t0']+s.get('band_at',0),1))
        c.drawRect(skia.Rect.MakeLTRB(120*u,y0*u,(120+(W/u-140)*k)*u,y1*u),paint('#7fc4e8',.10))
        c.drawLine(120*u,y0*u,(120+(W/u-140)*k)*u,y0*u,paint('#9ed4f0',.5,stroke=1*u)); c.drawLine(120*u,y1*u,(120+(W/u-140)*k)*u,y1*u,paint('#9ed4f0',.5,stroke=1*u))
        draw_text(c,lab,(W/u-30)*u,(y0-8)*u,F('serif-vf',14*u,800),'#9ed4f0',k,'right')
    ctx.proj=None

# ---------- generic dusk horizon (for icon scenes) ----------
def dusk_bg(ctx,sc,t):
    c=ctx.c; u=U(ctx); d=sc.get('dusk',{}); hy=d.get('hy',420)
    sky(ctx,d.get('top','#0a0b12'),d.get('mid','#22161a'),d.get('hz','#5a2e18'),hy=hy,t=t)
    ridge_line(c,u,hy,d.get('ridge',24),d.get('seed',4),'#140f0d'); ground(ctx,y=hy+12,col=d.get('ground','#120d0a'),glow=d.get('glow'),ga=.6)
    ctx.proj=None

# ---------- map with keyframed camera + optional drift ----------
def cam_at(sc,t):
    for kk in ('cam','cam1'):
        if isinstance(sc.get(kk),dict): sc[kk]=fit_cam(sc[kk])
    if 'cams' in sc:
        ks=sc['cams']
        for row in ks:
            if isinstance(row[1],dict): row[1]=fit_cam(row[1])
        if t<=sc['t0']+ks[0][0]: return list(ks[0][1])
        for (ta,ca),(tb,cb) in zip(ks,ks[1:]):
            if t<sc['t0']+tb:
                k=ease_in_out_cubic(prog(t,sc['t0']+ta,tb-ta)); return [lerp(ca[0],cb[0],k),lerp(ca[1],cb[1],k),math.exp(lerp(math.log(ca[2]),math.log(cb[2]),k))]
        return list(ks[-1][1])
    if 'cam1' not in sc and MAPCFG.get('drift') and not sc.get('static'):
        c0=sc['cam']; dr=MAPCFG['drift']; sc['cam1']=[c0[0]+sc.get('pan',[0,0])[0],c0[1]+sc.get('pan',[0,0])[1],c0[2]*dr]
    c0=sc['cam']; c1=sc.get('cam1',c0); d=sc.get('cam_dur',sc['t1']-sc['t0']); k=ease_in_out_cubic(prog(t,sc['t0']+sc.get('cam_at',0) if sc.get('cam_rel') else sc.get('cam_at',sc['t0']),d))
    return [lerp(c0[0],c1[0],k),lerp(c0[1],c1[1],k),math.exp(lerp(math.log(c0[2]),math.log(c1[2]),k))]
@lru_cache(16)
def _master_n(cams,W):
    s=W/1024; ppd=max(c[2] for c in cams)*s; bbs=[cam_proj(c) for c in cams]
    l0=min(b.l0 for b in bbs); b0=max(-84,min(b.b0 for b in bbs)); l1=max(b.l1 for b in bbs); b1=min(84,max(b.b1 for b in bbs))
    k=math.cos(math.radians((b0+b1)/2)); iw=int((l1-l0)*k*ppd)+2; ih=int((b1-b0)*ppd)+2
    if iw*ih>1.6e7: f=math.sqrt(1.6e7/(iw*ih)); iw,ih=int(iw*f),int(ih*f)
    q=Proj((l0,b0,l1,b1),0,0,iw,ih)
    L0=q.ml-(iw/2)/(q.k*q.s); L1=q.ml+(iw/2)/(q.k*q.s); B1=q.mb+(ih/2)/q.s; B0=q.mb-(ih/2)/q.s
    rgb=_relief(q,iw,ih,q.s/s)
    return skia.Image.fromarray(np.dstack([rgb,np.full(rgb.shape[:2],255,np.uint8)]),colorType=skia.kRGBA_8888_ColorType),(L0,B0,L1,B1)
def map_bg(ctx,sc,t):
    cam=cam_at(sc,t); W,H=ctx.W,ctx.H; p=cam_proj(cam); u=U(ctx)
    keys=[tuple(r[1]) for r in sc['cams']] if 'cams' in sc else ([tuple(sc['cam']),tuple(sc['cam1'])] if 'cam1' in sc else None)
    if not keys:
        key=(round(cam[0],3),round(cam[1],3),round(cam[2],2)); ctx.c.drawImageRect(_relief_img(key,W,H),skia.Rect.MakeWH(W,H))
    else:
        img,mb=_master_n(tuple(keys),W); x0,y0=p(mb[0],mb[3]); x1,y1=p(mb[2],mb[1])
        ctx.c.drawImageRect(img,skia.Rect.MakeLTRB(float(x0)*u,float(y0)*u,float(x1)*u,float(y1)*u),skia.SamplingOptions(skia.FilterMode.kLinear))
    for r in rivers():
        X,Y=p(r[:,0],r[:,1]); path=skia.Path(); path.addPoly([skia.Point(float(x)*u,float(y)*u) for x,y in zip(X,Y)],False)
        ctx.c.drawPath(path,paint('#c8a560',.38*sc.get('river_a',1),stroke=1.1*u))
    ctx.proj=p; ctx.ppd=p.s
    linear_grad(ctx.c,skia.Rect.MakeWH(W,H*.45),(0,0),(0,H*.45),[hexc('#0b0907',.6),hexc('#0b0907',0)])

# ---------- helpers ----------
def _pts(ctx,e,key='route'):
    """route of place names / [lon,lat] (needs ctx.proj) or 'xy' screen points"""
    if 'xy' in e and key=='route': return np.array(e['xy'],float)
    return np.array([P(ctx,q) for q in e[key]],float)
def _resample(pts,n=200):
    seg=np.hypot(*np.diff(pts,axis=0).T); cum=np.concatenate([[0],np.cumsum(seg)])
    if cum[-1]<=0: return pts,cum
    s=np.linspace(0,cum[-1],n); return np.c_[np.interp(s,cum,pts[:,0]),np.interp(s,cum,pts[:,1])],s
def geodesic(a,b,n=90):
    def v(p): lo,la=map(math.radians,p); return np.array([math.cos(la)*math.cos(lo),math.cos(la)*math.sin(lo),math.sin(la)])
    A,B=v(a),v(b); w=math.acos(max(-1,min(1,float(np.dot(A,B))))); out=[]
    for i in range(n+1):
        f=i/n; Pp=(math.sin((1-f)*w)*A+math.sin(f*w)*B)/math.sin(w) if w>1e-9 else A
        lo=math.degrees(math.atan2(Pp[1],Pp[0])); 
        if a[0]>180 or b[0]>180 or (out and abs(lo-out[-1][0])>180): lo=lo%360
        out.append([lo,math.degrees(math.asin(Pp[2]))])
    return out
def circle_ll(lon,lat,rkm,n=72):
    d=rkm/6371.; la1=math.radians(lat); lo1=math.radians(lon); out=[]
    for i in range(n+1):
        b=2*math.pi*i/n; la=math.asin(math.sin(la1)*math.cos(d)+math.cos(la1)*math.sin(d)*math.cos(b))
        lo=lo1+math.atan2(math.sin(b)*math.sin(d)*math.cos(la1),math.cos(d)-math.sin(la1)*math.sin(la))
        out.append([math.degrees(lo),math.degrees(la)])
    return out

PLANE_TOP=[(1,0),(.9,.07),(.2,.09),(-.22,.95),(-.36,.95),(-.18,.09),(-.72,.07),(-.9,.36),(-1,.36),(-.94,0)]
def draw_plane(c,x,y,ang,s,u,a=1.,col='#f6efe2',side=False):
    c.save(); c.translate(x*u,y*u); c.rotate(math.degrees(ang)); c.scale(s*u,s*u)
    if side:
        p=skia.Path(); p.moveTo(1,-.02); p.cubicTo(1,-.14,.8,-.16,.6,-.16); p.lineTo(-.7,-.14); p.lineTo(-1,-.62); p.lineTo(-1.08,-.62); p.lineTo(-.98,-.06); p.lineTo(-.9,.05); p.lineTo(.7,.08); p.cubicTo(.9,.08,1,.05,1,-.02); p.close()
        c.drawPath(p,paint(col,a)); c.drawOval(skia.Rect.MakeLTRB(-.3,-.02,.25,.1),paint('#b8ac98',a))
        c.drawOval(skia.Rect.MakeLTRB(-.05,.06,.25,.16),paint('#d8ccb8',a))
        for i in range(8): c.drawCircle(.55-i*.14,-.07,.022,paint('#3a2a1a',a*.8))
    else:
        pts=PLANE_TOP+[(x_,-y_) for x_,y_ in reversed(PLANE_TOP[1:])]
        p=skia.Path(); p.addPoly([skia.Point(*q) for q in pts],True)
        c.drawPath(p,paint('#000000',a*.45,blur=.12)); c.drawPath(p,paint(col,a))
        for sgn in (1,-1): c.drawRoundRect(skia.Rect.MakeLTRB(-.02,sgn*.36-.05,.22,sgn*.36+.05),.04,.04,paint('#b8ac98',a))
    c.restore()

def plane(ctx,e,t,frame):
    """plane icon flying along route/xy: go_at, dur, ease(io|lin|out), s, trail (0-1 of path), side(view), col"""
    a=env(e,t,.3,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); pts=_pts(ctx,e)
    if len(pts)<2: return
    pts,cum=_resample(pts,400); L=cum[-1]; fe={'io':ease_in_out_cubic,'lin':lambda x:x,'out':ease_out_cubic}[e.get('ease','io')]
    k=fe(prog(t,e.get('go_at',e['t0']),e.get('dur',3.))); d=L*k
    i=int(np.clip(np.searchsorted(cum,d),1,len(cum)-1)); x=np.interp(d,cum,pts[:,0]); y=np.interp(d,cum,pts[:,1])
    dx,dy=pts[i]-pts[i-1]; ang=math.atan2(dy,dx)
    tr=e.get('trail',.35)
    if tr>0 and d>0:   # fading contrail
        d0=max(0,d-L*tr); m=(cum>=d0)&(cum<=d); q=np.r_[pts[m],[[x,y]]]
        for j in range(1,len(q)):
            f=j/len(q); c.drawLine(q[j-1][0]*u,q[j-1][1]*u,q[j][0]*u,q[j][1]*u,paint(e.get('trail_col','#fff3d8'),a*f*.85,stroke=(.6+1.6*f)*u))
        c.drawPath(LN.path_from(q,u,1)[0],paint('#ffb850',a*.25,stroke=6*u,blur=4*u)) if len(q)>1 else None
    c.drawCircle(x*u,y*u,min(e.get('s',14)*1.6,30)*u,paint('#ffb850',a*.22,blur=8*u))
    draw_plane(c,x,y,ang if not e.get('side') else e.get('tilt',0),e.get('s',14),u,a,e.get('col','#f6efe2'),e.get('side',False))
    if e.get('label'): draw_text(c,e['label'],x*u,(y-e.get('s',14)-10)*u,F('serif-vf',13*u,900),GOLD,a,glow=3*u,glow_color='#000000')

def windflow(ctx,e,t,frame):
    """particle streaks flowing along a centreline (route lon/lat or xy): width(px), n, speed(px/s), trail(px), color, taper"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); pts=_pts(ctx,e)
    pts,cum=_resample(pts,300); L=cum[-1]
    if L<=0: return
    tg=np.gradient(pts,axis=0); nrm=np.c_[-tg[:,1],tg[:,0]]; nrm/=np.linalg.norm(nrm,axis=1)[:,None]+1e-9
    r=random.Random(e.get('seed',1)); w=e.get('width',40); sp=e.get('speed',120)*(-1 if e.get('reverse') else 1); tl=e.get('trail',40)
    col=e.get('color','#9ed4f0'); grow=ease_out_cubic(prog(t,e['t0'],e.get('grow',1.2)))
    for i in range(e.get('n',90)):
        off=r.uniform(-1,1); off=math.copysign(abs(off)**1.4,off)*w/2; v=sp*r.uniform(.6,1.25)*(1-.45*abs(off)/(w/2+1e-6))
        s=(r.uniform(0,L)+t*v)%L; s0=s-tl*abs(v)/abs(sp)*(1 if v>0 else -1)
        ss=np.linspace(s0,s,7)
        if (ss<0).any() or (ss>L).any(): continue
        X=np.interp(ss,cum,pts[:,0])+np.interp(ss,cum,nrm[:,0])*off; Y=np.interp(ss,cum,pts[:,1])+np.interp(ss,cum,nrm[:,1])*off
        fade=min(1,s/(L*.12),(L-s)/(L*.12))*grow
        for j in range(1,7):
            c.drawLine(X[j-1]*u,Y[j-1]*u,X[j]*u,Y[j]*u,paint(col,a*fade*j/6*e.get('alpha',.8),stroke=e.get('lw',1.3)*u))
    if e.get('label'):
        mid=len(pts)//2; draw_text(c,e['label'],pts[mid][0]*u,(pts[mid][1]-w/2-10)*u,F('serif-vf',15*u,900),col,a*grow,glow=3*u,glow_color='#000000')

def arrow(ctx,e,t,frame):
    """animated arrow along route/xy (draw_at,dur), color, w, head, dashed"""
    a=env(e,t,.3,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); pts=_pts(ctx,e)
    if len(pts)>2:
        try:
            from scipy.interpolate import splprep,splev
            tck,_=splprep(pts.T,s=0,k=min(3,len(pts)-1)); pts=np.array(splev(np.linspace(0,1,120),tck)).T
        except Exception: pass
    k=ease_in_out_cubic(prog(t,e.get('draw_at',e['t0']),e.get('dur',1.)))
    p,head=LN.path_from(pts,u,k)
    if p is None: return
    pt=paint(e.get('color',RED),a,stroke=e.get('w',2.2)*u); pt.setStrokeCap(skia.Paint.kRound_Cap)
    if e.get('dashed'): pt.setPathEffect(skia.DashPathEffect.Make([7*u,5*u],0))
    c.drawPath(p,paint(e.get('color',RED),a*.35,stroke=e.get('w',2.2)*3*u,blur=3*u)); c.drawPath(p,pt)
    if e.get('head',True) and k>.05:
        pp,cum=_resample(pts,200); d=cum[-1]*k; i=int(np.clip(np.searchsorted(cum,d),1,len(cum)-1))
        x=np.interp(d,cum,pp[:,0]); y=np.interp(d,cum,pp[:,1]); ang=math.atan2(*(pp[i]-pp[i-1])[::-1]); h=e.get('hs',11)
        hp=skia.Path(); hp.moveTo((x+math.cos(ang)*h*.4)*u,(y+math.sin(ang)*h*.4)*u)
        for da in (2.6,-2.6): hp.lineTo((x+math.cos(ang+da)*h)*u,(y+math.sin(ang+da)*h)*u)
        hp.close(); c.drawPath(hp,paint(e.get('color',RED),a))
    if e.get('text'):
        x,y=pts[len(pts)//2]; draw_text(c,e['text'],(x+e.get('dx',0))*u,(y+e.get('dy',-12))*u,F('serif-vf',e.get('size',14)*u,900),e.get('color',RED),a*prog(t,e.get('draw_at',e['t0'])+.3,.4),glow=3*u,glow_color='#000000')

def kmring(ctx,e,t,frame):
    """true geodesic circle of radius rkm around 'at' on any projection; grows in; fill, dashed edge, label"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); lon,lat=CITY[e['at']] if isinstance(e['at'],str) else e['at']
    k=ease_out_cubic(prog(t,e.get('grow_at',e['t0']),e.get('dur',1.)))
    ring_=np.array(circle_ll(lon,lat,max(1,e['rkm']*k)),float); X,Y=ctx.proj(ring_[:,0],ring_[:,1])
    p=_poly_path(X,Y,u,maxjump=400)
    col=e.get('color','#7fe0b0'); c.drawPath(p,paint(col,a*e.get('fill',.10)))
    st=paint(col,a*.85,stroke=1.3*u); st.setPathEffect(skia.DashPathEffect.Make([6*u,4*u],t*20*u)); c.drawPath(p,st)
    x,y=P(ctx,e['at']); c.drawCircle(x*u,y*u,3*u,paint(col,a))
    if e.get('text'): draw_text(c,e['text'],(x+e.get('dx',0))*u,(y+e.get('dy',18))*u,F('serif-vf',e.get('size',13)*u,900),col,a,glow=3*u,glow_color='#000000')

def zone(ctx,e,t,frame):
    """restricted zone: poly=[[lon,lat]..] or at+rkm; red hatch, pulsing edge, label"""
    a=env(e,t,.3,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx)
    ring_=np.array(e['poly'] if 'poly' in e else circle_ll(*(CITY[e['at']] if isinstance(e['at'],str) else e['at']),e['rkm']),float)
    X,Y=ctx.proj(ring_[:,0],ring_[:,1]); p=_poly_path(X,Y,u); k=ease_out_cubic(prog(t,e['t0'],.6)); col=e.get('color',RED)
    c.save(); c.clipPath(p,doAntiAlias=True); b=p.getBounds()
    c.drawRect(b,paint(col,a*.14*k))
    for i in range(-40,80):
        x0=b.left()+i*7*u; c.drawLine(x0,b.bottom(),x0+(b.height()),b.top(),paint(col,a*.35*k,stroke=1*u))
    c.restore(); c.drawPath(p,paint(col,a*(.6+.4*math.sin(t*5)),stroke=1.6*u))
    if e.get('text'):
        cx,cy=float(np.mean(X)),float(np.mean(Y)); draw_text(c,e['text'],(cx+e.get('dx',0))*u,(cy+5+e.get('dy',0))*u,F('serif-vf',e.get('size',15)*u,900),col,a*k,glow=3*u,glow_color='#000000')

def tissot(ctx,e,t,frame):
    """equal-size ground circles (radius r deg) at points; on flat bg they inflate with Mercator morph"""
    a=env(e,t,.3,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); o=getattr(ctx,'flat',None)
    for i,(lon,lat) in enumerate(e['at']):
        k=ease_out_back(prog(t,e['t0']+i*e.get('step',.12),.5))
        if k<=0: continue
        x,y=ctx.proj(lon,lat); r=e.get('r',5)
        cl=math.cos(math.radians(lat)); m=o.m if o else 0; sx=(o.sx if o else ctx.ppd)
        rx=r/cl*sx*k; ry=r*lerp(1,1/cl,m)*sx*k
        rect=skia.Rect.MakeLTRB((float(x)-rx)*u,(float(y)-ry)*u,(float(x)+rx)*u,(float(y)+ry)*u)
        col=e.get('color','#ff8a50'); c.drawOval(rect,paint(col,a*.28)); c.drawOval(rect,paint(col,a*.9,stroke=1.2*u))

def panel(ctx,e,t,frame):
    """data panel/inset card: x,y,w,h, title, rows=[{label,value,frac,color}], note, slide(from right/left/up)"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); k=ease_out_cubic(prog(t,e['t0'],.6)); x,y,w,h=e['x'],e['y'],e['w'],e['h']
    sl=e.get('slide','right'); off=(1-k)*40; x+= off if sl=='right' else -off if sl=='left' else 0; y+= off if sl=='up' else 0
    rrect(c,(x+4)*u,(y+6)*u,w*u,h*u,8*u,fill='#000000',a=a*.5*k,blur=8*u)
    rrect(c,x*u,y*u,w*u,h*u,8*u,fill='#15110d',a=a*.86*k); rrect(c,x*u,y*u,w*u,h*u,8*u,stroke='#c8a560',a=a*.7*k,sw=1*u)
    c.drawRect(skia.Rect.MakeXYWH((x+14)*u,(y+32)*u,(w-28)*u,.8*u),paint('#c8a560',a*.5*k))
    if e.get('title'): draw_text(c,e['title'],(x+14)*u,(y+23)*u,F('serif-vf',14*u,900),GOLD,a*k,'left')
    for i,row in enumerate(e.get('rows',[])):
        tr=e['t0']+.35+i*e.get('step',.35); kr=ease_out_cubic(prog(t,tr,.6))
        if kr<=0: continue
        yy=y+56+i*e.get('dy',40); col=row.get('color',WHITE)
        draw_text(c,row.get('label',''),(x+14)*u,yy*u,F('serif-vf',13*u,800),'#d8cdb8',a*kr,'left')
        if 'value' in row: draw_text(c,str(row['value']),(x+w-14)*u,yy*u,F('serif-vf',15*u,900),col,a*kr,'right')
        if 'frac' in row:
            bw=(w-28)*row['frac']*kr; c.drawRect(skia.Rect.MakeXYWH((x+14)*u,(yy+7)*u,(w-28)*u,5*u),paint('#ffffff',a*.08))
            c.drawRect(skia.Rect.MakeXYWH((x+14)*u,(yy+7)*u,bw*u,5*u),paint(col,a*.9)); c.drawCircle((x+14+bw)*u,(yy+9.5)*u,4*u,paint(col,a*.6,blur=3*u))
    if e.get('note'): draw_text(c,e['note'],(x+14)*u,(y+h-12)*u,F('sans',9.5*u),'#a99f90',a*k,'left')

def tag(ctx,e,t,frame):
    """callout: dot at 'at' + leader line + boxed label at offset (dx,dy)"""
    a=env(e,t,.3,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=P(ctx,e['at']) if 'at' in e else (e['x'],e['y']); dx,dy=e.get('dx',60),e.get('dy',-40)
    k=ease_out_cubic(prog(t,e['t0'],.5)); col=e.get('color',GOLD)
    c.drawCircle(x*u,y*u,3.2*u,paint(col,a)); c.drawCircle(x*u,y*u,(6+4*math.sin(t*4))*u,paint(col,a*.5,stroke=1*u))
    ex,ey=x+dx*k,y+dy*k; c.drawLine(x*u,y*u,ex*u,ey*u,paint(col,a*.8,stroke=1*u))
    f=F('serif-vf',e.get('size',13)*u,900); tw=f.measureText(e['text'])/u; bx=ex if dx>=0 else ex-tw-16
    rrect(c,bx*u,(ey-11)*u,(tw+16)*u,22*u,3*u,fill='#0e0b08',a=a*.8*k); rrect(c,bx*u,(ey-11)*u,(tw+16)*u,22*u,3*u,stroke=col,a=a*.8*k,sw=.8*u)
    draw_text(c,e['text'],(bx+8)*u,(ey+5)*u,f,e.get('tcolor',WHITE),a*k,'left')
    if e.get('sub'): draw_text(c,e['sub'],(bx+8)*u,(ey+24)*u,F('sans',10*u),'#d8cdb8',a*k,'left')

def motes(ctx,e,t,frame):
    """ambient floating gold dust (constant motion layer)"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); r=random.Random(e.get('seed',11))
    for i in range(e.get('n',60)):
        x=(r.uniform(0,1024)+t*r.uniform(-6,10))%1024; y=(r.uniform(0,576)-t*r.uniform(3,12))%576; s=r.uniform(.6,2.0)
        c.drawCircle(x*u,y*u,s*u,paint(e.get('color','#f2c766'),a*r.uniform(.15,.55)*(.6+.4*math.sin(t*2+i)),blur=s*.6*u))

def cloudshade(ctx,e,t,frame):
    """drifting soft cloud shadows/highlights over a map"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); r=random.Random(e.get('seed',3))
    for i in range(e.get('n',9)):
        x=(r.uniform(-200,1224)+t*e.get('v',8))%1424-200; y=r.uniform(150,560); w=r.uniform(160,340)
        c.drawOval(skia.Rect.MakeXYWH((x-w/2)*u,(y-w*.22)*u,w*u,w*.44*u),paint(e.get('color','#e8d8c0'),a*e.get('alpha',.06),blur=30*u))

def chapter(ctx,e,t,frame):
    """top-right chapter kicker: no + title + thin progress line"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); k=ease_out_cubic(prog(t,e['t0'],.8)); x=e.get('x',990)
    draw_text(c,e.get('no',''),x*u,40*u,F('serif-vf',22*u,900),GOLD,a*k,'right',glow=4*u,glow_color='#7a4a10')
    draw_text(c,e['text'],x*u,60*u,F('serif-vf',12*u,800),'#e8dcc4',a*k,'right',spacing=1.5*u)
    c.drawRect(skia.Rect.MakeXYWH((x-120*k)*u,67*u,120*k*u,1*u),paint(GOLD,a*.7))

def topshade(ctx,e,t,frame):
    linear_grad(ctx.c,skia.Rect.MakeWH(ctx.W,ctx.H*.4),(0,0),(0,ctx.H*.4),[hexc('#0b0907',e.get('a',.45)),hexc('#0b0907',0)])

def borders(ctx,e,t,frame):
    """real country borders (Natural Earth) drawn over map, names list highlighted (NAME or NAME_ZH), staggered reveal"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); hl=e.get('hl',[]); i=0
    for nm,zh,r in land_polys():
        h=_hl(nm,zh,hl)
        if e.get('only_hl') and not h: continue
        X,Y=ctx.proj(r[:,0],r[:,1])
        if np.max(X)<-50 or np.min(X)>1074 or np.max(Y)<-50 or np.min(Y)>626: continue
        p=_poly_path(X,Y,u,maxjump=500)
        if h:
            k=ease_out_cubic(prog(t,e['t0']+hl.index(nm if nm in hl else zh)*e.get('step',.25),.6))
            c.drawPath(p,paint(e.get('fill',GOLD),a*k*e.get('fill_a',.16))); c.drawPath(p,paint(e.get('color',GOLD),a*k*.9,stroke=1.4*u))
        else: c.drawPath(p,paint('#e8dcc4',a*e.get('base_a',.28),stroke=.7*u))

def grat(ctx,e,t,frame):
    """graticule over current projection (map/globe/flat): every 'step' deg"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); s=e.get('step',10)
    for la in range(-80,90,s):
        lo=np.linspace(-180,540,361); X,Y=ctx.proj(lo,np.full_like(lo,la)); c.drawPath(_poly_path(X,Y,u,False,maxjump=300),paint('#c8a560',a*.18,stroke=.7*u))
    for lo0 in range(-180,540,s):
        la=np.linspace(-85,85,60); X,Y=ctx.proj(np.full_like(la,lo0),la); c.drawPath(_poly_path(X,Y,u,False),paint('#c8a560',a*.12,stroke=.7*u))

# ---------- icon scenes (screen coords x,y = base centre, s = scale) ----------
def storm(ctx,e,t,frame):
    """cumulonimbus anvil + flickering lightning + rain"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=P(ctx,e['at']) if 'at' in e else (e['x'],e['y']); s=e.get('s',1.)*ease_out_cubic(prog(t,e['t0'],.8)); r=random.Random(e.get('seed',2))
    for i in range(24):  # rain
        rx=x+r.uniform(-70,70)*s; ph=(t*1.8+r.random())%1; c.drawLine(rx*u,(y-40*s+ph*60*s)*u,(rx-4*s)*u,(y-30*s+ph*60*s)*u,paint('#9ab0c8',a*.5,stroke=.8*u))
    blobs=[(0,-70,60),(-50,-60,42),(50,-62,44),(-25,-110,48),(25,-115,46),(0,-150,40),(-90,-175,30),(90,-178,32),(-50,-180,34),(50,-182,36),(0,-185,38)]
    flash=0
    for k_ in range(3):
        ft=(t*e.get('rate',.9)+k_*.37+e.get('seed',2)*.13)%1
        if ft<.06: flash=max(flash,1-ft/.06)
    for bx,by,br in blobs:
        cx,cy,rr=(x+bx*s+math.sin(t*.6+bx)*2*s),(y+by*s),br*s
        c.drawCircle(cx*u,cy*u,rr*u,paint('#2a2632',a*.95,blur=4*u)); c.drawCircle((cx-rr*.3)*u,(cy-rr*.35)*u,rr*.7*u,paint('#6a5a6a',a*.35,blur=rr*.4*u))
        if flash: c.drawCircle(cx*u,cy*u,rr*1.1*u,paint('#c8d8ff',a*flash*.35,blur=rr*.5*u,blend=skia.BlendMode.kScreen))
    if flash:
        rr=random.Random(int(t*1.7)); bxp=x+rr.uniform(-30,30)*s; byp=y-70*s; p=skia.Path(); p.moveTo(bxp*u,byp*u)
        for j in range(6): bxp+=rr.uniform(-14,14)*s; byp+=16*s; p.lineTo(bxp*u,byp*u)
        c.drawPath(p,paint('#e8f0ff',a*flash,stroke=2.2*u)); c.drawPath(p,paint('#9ab8ff',a*flash*.8,stroke=8*u,blur=6*u))
    if e.get('text'): draw_text(c,e['text'],x*u,(y+e.get('ty',36)*s)*u,F('serif-vf',e.get('size',16)*u,900),e.get('color',RED),a,glow=3*u,glow_color='#000000')

def volcano(ctx,e,t,frame):
    """cone + glowing crater + rising drifting ash plume particles"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=P(ctx,e['at']) if 'at' in e else (e['x'],e['y']); s=e.get('s',1.); r=random.Random(e.get('seed',5)); wind=e.get('wind',30)
    k=ease_out_cubic(prog(t,e['t0'],.8))
    for i in range(e.get('n',70)):   # plume
        ph=(t*.12*r.uniform(.7,1.3)+r.random())%1*k; px=x+(r.uniform(-8,8)+ph*wind*1.6+math.sin(ph*6+i)*6)*s; py=y-(72+ph*170)*s; rr=(6+ph*30)*s
        c.drawCircle(px*u,py*u,rr*u,paint('#4a4038' if i%3 else '#6a5a4c',a*(1-ph)*.55,blur=rr*.45*u))
    p=skia.Path(); p.moveTo((x-110*s)*u,y*u); p.cubicTo((x-60*s)*u,(y-30*s)*u,(x-22*s)*u,(y-70*s)*u,(x-12*s)*u,(y-74*s)*u)
    p.lineTo((x+12*s)*u,(y-74*s)*u); p.cubicTo((x+22*s)*u,(y-70*s)*u,(x+60*s)*u,(y-30*s)*u,(x+110*s)*u,y*u); p.close()
    c.drawPath(p,paint('#2a1e16',a)); c.drawPath(p,paint('#7a5232',a*.5,stroke=1*u))
    c.drawOval(skia.Rect.MakeXYWH((x-16*s)*u,(y-80*s)*u,32*s*u,12*s*u),paint('#ff7a20',a*(.7+.3*math.sin(t*7)),blur=5*u))
    for j in range(3):
        lp=skia.Path(); lp.moveTo((x-4*s+j*4*s)*u,(y-72*s)*u); lp.quadTo((x-10*s+j*14*s)*u,(y-40*s)*u,(x-30*s+j*30*s)*u,(y-8*s)*u)
        c.drawPath(lp,paint('#ff6a1a',a*.7,stroke=1.6*u,blur=1*u))
    if e.get('text'): draw_text(c,e['text'],x*u,(y+e.get('ty',26)*s)*u,F('serif-vf',e.get('size',16)*u,900),e.get('color',RED),a,glow=3*u,glow_color='#000000')

def airport(ctx,e,t,frame):
    """perspective runway with chasing lights, control tower, terminal glow (screen coords, base y=horizon)"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',512),e.get('y',420); s=e.get('s',1.)
    p=skia.Path(); p.moveTo((x-30*s)*u,y*u); p.lineTo((x+30*s)*u,y*u); p.lineTo((x+260*s)*u,576*u); p.lineTo((x-260*s)*u,576*u); p.close()
    c.drawPath(p,paint('#1c1814',a)); c.drawPath(p,paint('#5a4a38',a*.6,stroke=1*u))
    for i in range(14):   # centre dashes + edge lights (chasing)
        f=(i/14)**1.8; yy=y+(576-y)*f; ww=30*s+230*s*f
        c.drawLine(x*u,yy*u,x*u,(yy+6*f+1)*u,paint('#e8dcc4',a*.6,stroke=(1+2*f)*u))
        on=.35+.65*(((t*2.2-i*.18)%1)<.25)
        for sg in (-1,1): c.drawCircle((x+sg*ww)*u,yy*u,(1+2*f)*u,paint('#ffd070',a*on)); c.drawCircle((x+sg*ww)*u,yy*u,(4+6*f)*u,paint('#ffb040',a*on*.3,blur=4*u))
    tx=x+e.get('tower_dx',220)*s   # tower
    c.drawRect(skia.Rect.MakeXYWH((tx-5*s)*u,(y-80*s)*u,10*s*u,80*s*u),paint('#2a221c',a))
    c.drawRect(skia.Rect.MakeXYWH((tx-16*s)*u,(y-98*s)*u,32*s*u,18*s*u),paint('#3a3028',a))
    c.drawRect(skia.Rect.MakeXYWH((tx-13*s)*u,(y-95*s)*u,26*s*u,9*s*u),paint('#9ad0e0',a*.7))
    c.drawCircle(tx*u,(y-104*s)*u,2.5*u,paint('#ff4030',a*(.4+.6*(math.sin(t*5)>0))))
    c.drawRect(skia.Rect.MakeXYWH((x-330*s)*u,(y-26*s)*u,220*s*u,26*s*u),paint('#241c16',a))
    for i in range(18): c.drawRect(skia.Rect.MakeXYWH((x-322*s+i*12*s)*u,(y-18*s)*u,6*s*u,6*s*u),paint('#ffc060',a*.7))

# ---------- transitions ----------
def _render_scene(ctx,sc,t,frame):
    BG[sc.get('bg','map')](ctx,sc,t); draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)
def draw(ctx,t,frame,S):
    c=ctx.c; W,H=ctx.W,ctx.H; u=U(ctx); c.clear(skia.Color(0,0,0))
    act=[sc for sc in S['scenes'] if sc['t0']-1e-6<=t<sc['t1']]
    if not act: return
    base=act[0]; nx=act[1] if len(act)>1 else None
    tin=(nx.get('tin') or {'type':'fade','dur':nx.get('xin',.8)}) if nx else None
    if isinstance(tin,str): tin={'type':tin}
    typ=tin['type'] if tin else None; k=ease_in_out_cubic(prog(t,nx['t0'],tin.get('dur',.8))) if nx else 0
    at=(tin or {}).get('at',[512,288]) if nx else [512,288]
    # outgoing
    c.save()
    if typ=='zoom': z=1+k*1.2; c.translate(at[0]*u,at[1]*u); c.scale(z,z); c.translate(-at[0]*u,-at[1]*u)
    if typ=='slide': c.translate(-k*W,0)
    if base.get('fade_in') and base['t0']<1e-6: pass
    _render_scene(ctx,base,t,frame); c.restore()
    if nx:
        if typ in ('fade','zoom','flash',None):
            alpha=k if typ!='flash' else float(k>.5)
            c.saveLayerAlpha(None,int(255*alpha))
            if typ=='zoom': z=.6+.4*k; c.translate(at[0]*u,at[1]*u); c.scale(z,z); c.translate(-at[0]*u,-at[1]*u)
            _render_scene(ctx,nx,t,frame); c.restore()
            if typ=='flash': c.drawRect(skia.Rect.MakeWH(W,H),paint(tin.get('color','#fff4dc'),(1-abs(2*k-1))**1.5*.95))
        elif typ=='wipe':
            ex=lerp(-.25,1.25,k)*W; sk=tin.get('skew',.25)*H
            p=skia.Path(); p.moveTo(-10,0); p.lineTo(ex+sk,0); p.lineTo(ex-sk,H); p.lineTo(-10,H); p.close()
            c.save(); c.clipPath(p,doAntiAlias=True); _render_scene(ctx,nx,t,frame); c.restore()
            band=skia.Path(); band.moveTo(ex+sk,0); band.lineTo(ex-sk,H)
            c.drawPath(band,paint('#ffd890',.9*(1-abs(2*k-1)),stroke=6*u,blur=8*u)); c.drawPath(band,paint('#fff6e0',.9*(1-abs(2*k-1)),stroke=1.5*u))
        elif typ=='iris':
            R=k*math.hypot(W,H); p=skia.Path(); p.addCircle(at[0]*u,at[1]*u,R)
            c.save(); c.clipPath(p,doAntiAlias=True); _render_scene(ctx,nx,t,frame); c.restore()
            c.drawCircle(at[0]*u,at[1]*u,R,paint('#ffc860',.8*(1-k),stroke=5*u,blur=6*u))
        elif typ=='slide':
            c.save(); c.translate((1-k)*W,0); _render_scene(ctx,nx,t,frame); c.restore()
    draw_elements(ctx,S.get('overlays',[]),t,frame,EXTRA)
    vignette(c,W,H,.45); grain(c,W,H,frame,.035,10)
    fo=S.get('fade_out',0)
    if fo and t>S['duration']-fo: c.drawRect(skia.Rect.MakeWH(W,H),paint('#000000',prog(t,S['duration']-fo,fo)))
    fi=S.get('fade_in',0)
    if fi and t<fi: c.drawRect(skia.Rect.MakeWH(W,H),paint('#000000',1-prog(t,0,fi)))

BG.update(map=map_bg,globe=globe_bg,flat=flat_bg,sky=sky_bg,dusk=dusk_bg)
EXTRA.update(plane=plane,windflow=windflow,arrow=arrow,kmring=kmring,zone=zone,tissot=tissot,panel=panel,tag=tag,motes=motes,
             cloudshade=cloudshade,chapter=chapter,topshade=topshade,borders=borders,grat=grat,storm=storm,volcano=volcano,airport=airport)
