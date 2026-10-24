"""#28 宣纸水墨字效 (ink-paper-typography) — reference 7690248321424074417 《定风波》.
Music-only kinetic typography: alternating rice-paper (#f4efe6) and ink-black (#0d0d0d) grounds, heavy display serif,
red seal tiles (#e8582f), particle/ink assemble & disperse, top-right location HUD, AI image plates (hooks)."""
import os, math, random, numpy as np, skia
from engine.core import *
from engine.layers import draw_elements, U, el_text
from engine import proc as PROC, three as T3
from engine import richness as RICH

PAPER='#f4f0e8'; INK='#0d0d0d'; RED='#e8582f'; RED_D='#b53a1c'

def prepare(S):
    for sc in S['scenes']:
        for e in sc.get('elements',[]):
            if e['type']=='image' or e.get('src'):
                e['_abs']=os.path.join(S['_dir'],e['src'])
        if sc.get('plate'): sc['_plate']=os.path.join(S['_dir'],sc['plate'])

# ---------- backgrounds ----------
@lru_cache(4)
def paper_tex(W,H,warm=False):
    rng=np.random.default_rng(5)
    base=np.array([0xe6,0xd5,0xbe] if warm else [0xf5,0xf1,0xea],float)
    lo=rng.normal(0,1,(H//32+2,W//32+2)); 
    import cv2
    lo=cv2.resize(lo,(W,H),interpolation=cv2.INTER_CUBIC)*0.9
    fine=rng.normal(0,1.3,(H,W))
    yy,xx=np.mgrid[0:H,0:W]; r=np.hypot((xx-W/2)/(W/2),(yy-H/2)/(H/2))
    vig=-np.clip(r-0.35,0,1)**1.4*(22 if warm else 5)
    img=base[None,None,:]+(lo+fine+vig)[:,:,None]*np.array([1,1.0,1.1])
    arr=np.dstack([img.clip(0,255).astype(np.uint8),np.full((H,W),255,np.uint8)])
    return skia.Image.fromarray(arr,colorType=skia.kRGBA_8888_ColorType)

@lru_cache(4)
def dark_tex(W,H):
    rng=np.random.default_rng(9)
    yy,xx=np.mgrid[0:H,0:W]; r=np.hypot((xx-W/2)/(W/2),(yy-H*.45)/(H/2))
    v=14-np.clip(r,0,1.4)*9+rng.normal(0,2.0,(H,W))
    img=np.dstack([v,v,v]).clip(0,255).astype(np.uint8)
    return skia.Image.fromarray(np.dstack([img,np.full((H,W),255,np.uint8)]),colorType=skia.kRGBA_8888_ColorType)

POEM=("大江东去浪淘尽千古风流人物故垒西边人道是三国周郎赤壁乱石穿空惊涛拍岸卷起千堆雪江山如画一时多少豪杰"
      "莫听穿林打叶声何妨吟啸且徐行竹杖芒鞋轻胜马谁怕一蓑烟雨任平生料峭春风吹酒醒微冷山头斜照却相迎回首向来萧瑟处归去也无风雨也无晴"
      "明月几时有把酒问青天不知天上宫阙今夕是何年我欲乘风归去又恐琼楼玉宇高处不胜寒起舞弄清影何似在人间横看成岭侧成峰远近高低各不同")

def bg(ctx,sc,t,frame):
    c=ctx.c; W,H=ctx.W,ctx.H; kind=sc.get('bg','paper')
    if kind=='paper': c.drawImage(paper_tex(W,H),0,0)
    elif kind=='paper_warm': c.drawImage(paper_tex(W,H,True),0,0)
    elif kind=='dark': c.drawImage(dark_tex(W,H),0,0)
    elif kind=='black': c.clear(hexc('#050401'))
    elif kind=='orange':
        c.clear(hexc('#ea5a2c')); vignette(c,W,H,.25,(120,30,10))
    elif kind=='plate':
        c.clear(hexc('#101010'))
        k=prog(t,sc['t0'],sc['t1']-sc['t0']); z0,z1=sc.get('kenburns',[1.0,1.06])
        draw_image_cover(c,sc['_plate'],W,H,1.,lerp(z0,z1,k),.5,.5,sc.get('gray',False))
    elif kind=='proc':           # code-drawn illustration backgrounds (replace AI plates)
        P=sc['proc']; k=P['kind']; tt=t-sc['t0']
        if k=='bamboo':
            PROC.bamboo_forest(c,W,H,tt,P.get('mode','rain'),seed=P.get('seed',3),cam_z=P.get('dolly',0)*tt,walker_at=P.get('walker'),tex=P.get('tex'))
        elif k=='river': PROC.river_snow(c,W,H,tt,tex=P.get('tex'))
        elif k=='lake': PROC.lake_boat(c,W,H,tt)
        elif k=='lychee': PROC.lychee_rain(c,W,H,tt,fall=P.get('fall',.35))
        elif k=='moonsea':
            mk=P.get('moon',[520,135,42]); g=P.get('grow'); 
            r=mk[2] if not g else lerp(mk[2],g[1],ease_in_out_cubic(prog(t,g[0],g[2])))
            PROC.moon_sea(c,W,H,tt,mk[0]*W/1024,mk[1]*W/1024,r*W/1024,tex=P.get('tex'))
        for pr in P.get('precip',[]): PROC.precip(c,W,H,tt,**pr)
    elif kind=='redglow':
        c.clear(hexc('#0a0605'))
        sh=skia.GradientShader.MakeRadial((W/2,H*.62),W*.5,[hexc('#5a1408',.9),hexc('#0a0605',0)]); p=skia.Paint(); p.setShader(sh)
        c.save(); c.scale(1,.35); c.translate(0,H*1.15); c.drawCircle(W/2,H*.62,W*.5,p); c.restore()

# ---------- special elements ----------
def tile(ctx,e,t,frame):
    """red seal tile(s): text chars each in a red rounded block. anim: drop with bounce / fall-away"""
    u=U(ctx); c=ctx.c; t0,t1=e['t0'],e['t1']
    if t<t0 or t>t1: return
    size=e.get('size',40)*u; gap=e.get('gap',4)*u; chars=e['text']; n=len(chars)
    f=font('serif-vf',size*.78,900)
    x=e['x']*u; y=e['y']*u; tw=n*size+(n-1)*gap; x0=x-tw/2
    for i,ch in enumerate(chars):
        ct=t0+i*e.get('stagger',.06)
        k=ease_out_back(prog(t,ct,e.get('fi',.45)),1.4)
        if k<=0: continue
        a=min(1,prog(t,ct,.15)*1.5)*(1-prog(t,t1-e.get('fo',.3),e.get('fo',.3)))
        dy=-(1-k)*e.get('drop',90)*u
        fall=prog(t,e.get('fall_at',1e9),.8)
        rot=0
        if fall>0: dy+=fall*fall*500*u; rot=(i%2*2-1)*fall*40; a*=1-fall*.5
        cx=x0+i*(size+gap)+size/2; cy=y+dy
        c.save(); c.translate(cx,cy); c.rotate(rot+e.get('rot',0)*(1-k))
        # extruded side (3D-ish block)
        gray=e.get('gray') and ch not in e.get('keep','')
        rrect(c,-size/2+size*.06,-size/2+size*.08,size,size,size*.08,fill=('#1e1e1e' if gray else RED_D),a=a)
        sh=skia.GradientShader.MakeLinear([(0,-size/2),(0,size/2)],[hexc('#262626' if gray else '#f26a3c',a),hexc('#202020' if gray else '#dc4f26',a)])
        p=skia.Paint(AntiAlias=True); p.setShader(sh)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-size/2,-size/2,size,size),size*.08,size*.08),p)
        draw_text(c,ch,0,size*.28,f,('#5a5752' if gray else '#fff8ee'),a)
        c.restore()
H_=576

def hud(ctx,e,t,frame):
    """top-right place·year + km, small serif, ink or white"""
    u=U(ctx); a=fade_env(t,e['t0'],e['t1'],.3,.3)
    if a<=0: return
    col=e.get('color','#222222'); f=font('serif',9.5*u); f2=font('garamond',9*u,500)
    draw_text(ctx.c,e['text'],1000*u,38*u,f,col,a*.85,'right',spacing=.6*u)
    km=e.get('km')
    if isinstance(km,list):  # animate between values
        k=ease_out_cubic(prog(t,e.get('km_t',e['t0']),1.0)); v=lerp(km[0],km[1],k); kms=f"{v:,.0f} km"
    else: kms=f"{km:,} km" if isinstance(km,(int,float)) else str(km)
    if km is not None: draw_text(ctx.c,kms,1000*u,56*u,f2,col,a*.7,'right')

def ink_burst(ctx,e,t,frame):
    """radial ink-dot spokes exploding from center (opening), or a soft ink cloud"""
    u=U(ctx); c=ctx.c; a=fade_env(t,e['t0'],e['t1'],.15,e.get('fo',.5))
    if a<=0: return
    rng=random.Random(e.get('seed',2)); k=ease_out_expo(prog(t,e['t0'],e.get('dur',1.2)))
    cx,cy=e.get('x',512)*u,e.get('y',288)*u; col=e.get('color','#1a1a1a'); R=e.get('r',260)*u
    pts=[]
    for i in range(e.get('n',2400)):
        if e.get('mode','spokes')=='spokes':
            ang=(i%48)/48*2*math.pi+rng.gauss(0,.03); d=R*(rng.random()**.7)*k
        elif e['mode']=='cloud':
            ang=rng.random()*2*math.pi; d=abs(rng.gauss(0,.45))*R*(.6+.4*k)
        elif e['mode']=='mountain':
            hgt=R*k; yy=rng.random()**.8; half=yy*R*.55
            x=cx+rng.uniform(-half,half); y=cy-hgt+yy*hgt*1.0
            pts.append(skia.Point(x,y)); continue
        else:  # streak
            ang=0; d=0
        x=cx+math.cos(ang)*d*e.get('sx',1); y=cy+math.sin(ang)*d*e.get('sy',1)
        if e.get('mode')=='streak':
            x=cx+rng.gauss(0,R*.5)*(.3+k); y=cy+rng.gauss(0,R*.06)
        pts.append(skia.Point(x,y))
    c.drawPoints(skia.Canvas.kPoints_PointMode,pts,paint(col,a*.75,stroke=1.4*u))

def splatter(ctx,e,t,frame):
    """ink splatter under text (final '干就完了！'): random blobs scaled in fast"""
    u=U(ctx); c=ctx.c; a=fade_env(t,e['t0'],e['t1'],.05,.3)
    if a<=0: return
    rng=random.Random(e.get('seed',4)); k=ease_out_expo(prog(t,e['t0'],.35))
    cx,cy=e['x']*u,e['y']*u
    for i in range(e.get('n',420)):
        ang=rng.random()*2*math.pi; d=abs(rng.gauss(0,1))*e.get('r',70)*u*k
        r=max(.5,rng.expovariate(1)*1.4)*u
        c.drawCircle(cx+math.cos(ang)*d*1.6,cy+math.sin(ang)*d*.55,r,paint('#151210',a*rng.uniform(.5,1)))

def charwall(ctx,e,t,frame):
    """wall of tiny poem characters (ink on paper or white on dark), optional perspective floor & reveal"""
    u=U(ctx); c=ctx.c; a=fade_env(t,e['t0'],e['t1'],e.get('fi',.3),e.get('fo',.3))
    if a<=0: return
    size=e.get('size',11)*u; f=font('serif',size); col=e.get('color','#3a3632')
    cols=int(ctx.W/size)+2; rows=int(ctx.H/(size*1.25))+2
    k=prog(t,e['t0'],e['t1']-e['t0'])
    c.save()
    if e.get('floor') and e.get('persp',True):
        floor3d(ctx,e,t,a,k); c.restore(); return
    if e.get('floor'):  # perspective: draw rows with scale increasing toward bottom
        hz=e.get('horizon',230)*u
        for r in range(40):
            z=(r+ (k*e.get('speed',3))%1)/40.
            yy=hz+(ctx.H-hz)*(z**2.2); s=.15+e.get('near',4.5)*z**2.2
            ff=font('serif-vf',round(size*s,1),700)
            line_s=''.join(POEM[(r*37+j)%len(POEM)] for j in range(int(ctx.W/(size*s)*1.6)+4))
            draw_text(c,line_s,ctx.W/2,yy,ff,col,a*min(1,z*3),'center',spacing=size*s*.3)
    else:
        rng=random.Random(7)
        for r in range(rows):
            s=''.join(POEM[(r*cols+j+int(e.get('scroll',0)*t))%len(POEM)] for j in range(cols))
            draw_text(c,s,0,(r+1)*size*1.25,f,col,a*e.get('density',1),'left')
    c.restore()

@lru_cache(8)
def glyph_tex(col,dark,cell=48,n=40,seed=3):
    """square texture of bold poem glyphs (cell px), transparent bg -> tiled on 3D floor"""
    S=cell*n; surf=skia.Surface(S,S); c=surf.getCanvas(); c.clear(skia.Color4f(0,0,0,0))
    rng=random.Random(seed); f=font('serif-vf',cell*.82,800)
    for gy in range(n):
        if gy%2: continue
        for gx in range(n):
            ch=POEM[rng.randrange(len(POEM))]
            draw_text(c,ch,gx*cell+cell/2,gy*cell+cell*1.3,f,col,1,'center')
    return surf.makeImageSnapshot()
def floor3d(ctx,e,t,a,k):
    """true perspective ground plane: glyph texture projected with a homography; scroll toward camera"""
    c=ctx.c; W,H=ctx.W,ctx.H; u=U(ctx); hz=e.get('horizon',60)
    if isinstance(hz,list): hz=float(np.interp(t,[q[0] for q in hz],[q[1] for q in hz]))
    hz*=u
    img=glyph_tex(e.get('color','#2c2824'),False,int(e.get('cell',48)))
    cell=img.width()/40; f=W*.8; z0=1.0; hc=(H-hz)/f
    g=(float(np.interp(t,[q[0] for q in e['glyph']],[q[1] for q in e['glyph']])) if isinstance(e.get('glyph'),list) else e.get('glyph',58))*u/f          # world size of a glyph (near row ≈ glyph px)
    A=60.0; Z1=120.0
    def P(X,Z): return skia.Point(W/2+f*X/Z, hz+f*hc/Z)
    toT=lambda v: v/g*cell
    scroll=-(t-e['t0'])*e.get('speed',1.0)*g*2.2
    src=[skia.Point(toT(-A),toT(-Z1+scroll)),skia.Point(toT(A),toT(-Z1+scroll)),skia.Point(toT(A),toT(-z0+scroll)),skia.Point(toT(-A),toT(-z0+scroll))]
    dst=[P(-A,Z1),P(A,Z1),P(A,z0),P(-A,z0)]
    m=skia.Matrix(); m.setPolyToPoly(dst,src)   # screen->texture
    inv=skia.Matrix(); m.invert(inv)
    sh=img.makeShader(skia.TileMode.kRepeat,skia.TileMode.kRepeat,skia.SamplingOptions(skia.FilterMode.kLinear,skia.MipmapMode.kLinear),skia.Matrix())
    p=skia.Paint(AntiAlias=True); p.setShader(sh); p.setAlphaf(a)
    pts=[skia.Point(0,0)]*0
    c.save(); c.clipRect(skia.Rect.MakeLTRB(0,hz,W,H)); c.concat(inv)
    c.drawRect(skia.Rect.MakeLTRB(toT(-A),toT(-Z1+scroll),toT(A),toT(-z0+scroll)),p); c.restore()
    if e.get('road'):
        rp=skia.Path(); rp.moveTo(W/2-2*u,hz); rp.lineTo(W/2+2*u,hz); rp.lineTo(W/2+e['road']*W/2,H); rp.lineTo(W/2-e['road']*W/2,H); rp.close()
        c.drawPath(rp,paint(e.get('road_col','#fbf9f4'),a*.95,blur=3*u))
    # atmospheric haze toward horizon
    hcol=e.get('haze','#f2eee6')
    g=skia.GradientShader.MakeLinear([(0,hz),(0,hz+(H-hz)*.45)],[hexc(hcol,1*a),hexc(hcol,0)]); q=skia.Paint(); q.setShader(g)
    c.drawRect(skia.Rect.MakeLTRB(0,hz-2,W,H),q)
    if e.get('sky',True): c.drawRect(skia.Rect.MakeLTRB(0,0,W,hz),paint(hcol,a))

def geomap(ctx,e,t,frame):
    """real-geodata map (engine.geo): {bbox:[lon0,lat0,lon1,lat1], rect:[x,y,w,h], highlight:[...], route:[names], route_t0, route_dur}"""
    from engine import geo
    a=fade_env(t,e['t0'],e['t1'],e.get('fi',.4),e.get('fo',.4))
    if a<=0: return
    u=U(ctx); x,y,w,h=[v*u for v in e.get('rect',[60,30,900,520])]; P=geo.Proj(tuple(e.get('bbox',(100,17,123,37))),x,y,w,h)
    geo.draw_map(ctx.c,P,a,e.get('fill','#e9e2d4'),e.get('stroke','#8a8070'),.8*u,e.get('highlight'))
    if e.get('route'): geo.route(ctx.c,P,e['route'],t,e.get('route_t0',e['t0']),e.get('route_dur',3),w=2*u,a=a,size=14*u)

def cubes3d(ctx,e,t,frame):
    """real 3D glyph cubes (seal tiles): placed from 2D layout (px,py,size px) at camera distance D, drop-in with back-ease,
    gravity fall + tumble at fall_at, per-cube yaw/pitch; flat-shaded, back-face culled, depth sorted (engine.three)."""
    if t<e['t0'] or t>e['t1']: return
    W,H=ctx.W,ctx.H; u=U(ctx); D=e.get('D',9.0)
    cam=T3.Camera(pos=(0,0,D),target=(0,0,0),fov=e.get('fov',40),W=W,H=H); f=cam.f
    ops=[]
    for g in e['groups']:
        gx,gy,gs=g['x'],g['y'],g['size']
        if g.get('kf'):
            T_=[q[0] for q in g['kf']]; gy=float(np.interp(t,T_,[q[1] for q in g['kf']])); gs=float(np.interp(t,T_,[q[2] for q in g['kf']])); gx=float(np.interp(t,T_,[q[3] for q in g['kf']]))
        n=len(g['text']); sz=gs*u; gap=g.get('gap',4)*u*gs/g['size']; x0=gx*u-(n*sz+(n-1)*gap)/2+sz/2
        for i,ch in enumerate(g['text']):
            ct=g.get('t_in',e['t0'])+i*g.get('stagger',.06); k=ease_out_back(prog(t,ct,g.get('fi',.45)),1.3)
            if k<=0: continue
            px=x0+i*(sz+gap); py=gy*u
            X=(px-W/2)*D/f; Y=(H/2-py)*D/f+(1-k)*g.get('drop',2.0); S=sz*D/f*.92
            fa=g.get('fall_at',1e9); fk=max(0,t-fa); Y-=4.9*fk*fk*1.4; Z=-fk*1.5
            R=T3.rot(g.get('rx',.28)+fk*(1.5+i*.4)*(1 if i%2 else -1),g.get('ry',-.22)+fk*.9,g.get('rz',0)+fk*(i%3-1)*.8)
            col='#2a2826' if (g.get('gray') and ch not in g.get('keep','')) else g.get('color','#e8582f')
            ops+=T3.box_faces((X,Y,Z),(S,S,S*g.get('depth',.85)),R,col=col,face_text=ch,text_col=g.get('text_col','#fff8ee'),cam=cam,
                               light=tuple(e.get('light',(-.35,.8,.55))),fog=e.get('fog'),fog_col=e.get('fog_col','#000000'))
    T3.render_ops(ctx.c,ops)

def text3d(ctx,e,t,frame):
    """extruded display glyphs: N back-layers along (dx,dy) shaded dark->mid, then lit face; optional slow yaw via skew"""
    n=e.get('depth',18); dx,dy=e.get('dir',[-1.0,1.2]); u=U(ctx)
    side0,side1=e.get('side',['#3a3836','#9a9690'])
    c=ctx.c; c.save()
    if e.get('skew'): 
        cx,cy=e['x']*u,e['y']*u; c.translate(cx,cy); c.skew(e['skew'],0); c.translate(-cx,-cy)
    for i in range(n,0,-1):
        k=i/n; col=lerp_hex(side1,side0,k)
        el_text(ctx,dict(e,type='text',x=e['x']+dx*i*e.get('step',1.0),y=e['y']+dy*i*e.get('step',1.0),color=col,glow=0),t,frame)
    el_text(ctx,dict(e,type='text'),t,frame); c.restore()
def lerp_hex(a,b,k):
    A=[int(a[i:i+2],16) for i in (1,3,5)]; B=[int(b[i:i+2],16) for i in (1,3,5)]
    return '#%02x%02x%02x'%tuple(int(A[j]+(B[j]-A[j])*k) for j in range(3))

def tilegrid(ctx,e,t,frame):
    """black extruded glyph cubes popping in, density grows (03.2-04.8s)"""
    u=U(ctx); c=ctx.c; a=fade_env(t,e['t0'],e['t1'],.01,.05)
    if a<=0: return
    rng=random.Random(11); s=e.get('cell',26)*u; W,H=ctx.W,ctx.H
    k=prog(t,e['t0'],e['t1']-e['t0']); cells=[]
    for gy in range(int(H/s)+1):
        for gx in range(int(W/s)+1):
            on_t=rng.random(); big=rng.random(); ch=POEM[(gx*7+gy*13)%len(POEM)]
            cells.append((on_t,big,gx,gy,ch))
    for on_t,big,gx,gy,ch in sorted(cells,key=lambda q:q[1]):
        th=lerp(.06,.97,k**1.5)
        if on_t>th: continue
        pop=ease_out_cubic(min(1,(th-on_t)*8))
        sz=s*(2.2 if big>.97 else 1.5 if big>.9 else .9)*lerp(.6,1,pop)
        x=gx*s+s/2; y=gy*s+s/2
        dx=(x-W/2)/W*sz*.35; dy=(y-H/2)/H*sz*.35; d=sz*.22   # extrusion away from vanishing pt
        p=skia.Path(); p.moveTo(x-sz/2,y-sz/2); p.lineTo(x+sz/2,y-sz/2); p.lineTo(x+sz/2+dx,y-sz/2+dy+d); p.lineTo(x+sz/2+dx,y+sz/2+dy+d); p.lineTo(x-sz/2+dx,y+sz/2+dy+d); p.lineTo(x-sz/2+dx,y-sz/2+dy+d); p.close()
        c.drawPath(p,paint('#000000',a*.9))
        rrect(c,x-sz/2,y-sz/2,sz,sz,1.2*u,fill='#151413',a=a)
        draw_text(c,ch,x,y+sz*.22,font('serif-vf',sz*.62,700),'#f4f0e8',a)

def cards(ctx,e,t,frame):
    """poker-like cards: dark backs flipping to white fronts with vertical poem lines + red seal"""
    u=U(ctx); c=ctx.c
    a=fade_env(t,e['t0'],e['t1'],.3,.3)
    if a<=0: return
    items=e['items']; n=len(items); w,h=e.get('w',62)*u,e.get('h',92)*u; gap=e.get('gap',16)*u
    x0=e['x']*u-(n*w+(n-1)*gap)/2; y=e['y']*u
    for i,it in enumerate(items):
        ft=e.get('flip_at',[1e9]*n)[i]; fk=prog(t,ft,.35)
        sx=abs(math.cos(fk*math.pi)); front=fk>.5
        cx=x0+i*(w+gap)+w/2; rot=it.get('rot',0)
        c.save(); c.translate(cx,y); c.rotate(rot); c.scale(max(.02,sx),1)
        rrect(c,-w/2+3*u,-h/2+5*u,w,h,4*u,fill='#000000',a=a*.25,blur=5*u)
        if not front:
            rrect(c,-w/2,-h/2,w,h,4*u,fill='#1b1716',a=a); rrect(c,-w/2+3*u,-h/2+3*u,w-6*u,h-6*u,3*u,stroke='#5a2a20',a=a,sw=1*u)
            bk=it.get('back','黄州'); fs=min(24,(h/u*.62)/max(2,len(bk)))*u; ff=font('serif-vf',fs,900)
            for j,ch in enumerate(bk): draw_text(c,ch,0,-(len(bk)-1)*fs*.55+j*fs*1.1+fs*.36,ff,'#e8462a',a)
        else:
            rrect(c,-w/2,-h/2,w,h,4*u,fill='#fbf8f2',a=a); rrect(c,w/2-11*u,-h/2+5*u,6*u,6*u,1*u,fill=RED,a=a)
            ff=font('serif',8.5*u); lines=it['front']
            for li,ln in enumerate(lines):
                xx=(len(lines)-1)/2*11*u-li*11*u
                for j,ch in enumerate(ln): draw_text(c,ch,xx,-h*.32+j*10*u,ff,'#2a2622',a)
        c.restore()

def timeline(ctx,e,t,frame):
    """thin red horizontal track with nodes + labels (50-55s)"""
    u=U(ctx); c=ctx.c; a=fade_env(t,e['t0'],e['t1'],.4,.4)
    if a<=0: return
    y=e.get('y',400)*u; k=ease_in_out_cubic(prog(t,e['t0'],1.2))
    line(c,0,y,ctx.W*k,y,'#e07a5a',a*.7,1.0*u)
    f=font('serif',8*u); f2=font('garamond',7.5*u)
    for nd in e['nodes']:
        if nd['x']*u>ctx.W*k: continue
        x=nd['x']*u; glow_dot(c,x,y,2.2*u,'#e8582f',a,3)
        draw_text(c,nd['label'],x,y-9*u,f,'#3a3530',a,'center')
        if nd.get('km'): draw_text(c,nd['km'],x,y+16*u,f2,'#6a625a',a,'center')

def ring(ctx,e,t,frame):
    u=U(ctx); c=ctx.c; a=fade_env(t,e['t0'],e['t1'],.2,.3)
    if a<=0: return
    k=ease_in_out_cubic(prog(t,e['t0'],e.get('draw',.6)))
    p=paint(e.get('color','#cc3322'),a,stroke=e.get('w',4)*u); p.setStrokeCap(skia.Paint.kRound_Cap)
    rx,ry=e['rx']*u,e['ry']*u; x,y=e['x']*u,e['y']*u
    path=skia.Path(); path.addArc(skia.Rect.MakeLTRB(x-rx,y-ry,x+rx,y+ry),e.get('start',200),370*k)
    c.save(); c.rotate(e.get('rot',-4),x,y); c.drawPath(path,p); c.restore()

def bird(ctx,e,t,frame):
    """ink swallow/goose silhouette flying across (飞鸿)"""
    u=U(ctx); c=ctx.c; a=fade_env(t,e['t0'],e['t1'],.2,.3)
    if a<=0: return
    k=prog(t,e['t0'],e['t1']-e['t0']); x=lerp(e['x0'],e['x1'],k)*u; y=(lerp(e['y0'],e['y1'],k)+math.sin(k*9)*4)*u
    flap=math.sin(t*14)*.6; s=e.get('s',14)*u
    path=skia.Path(); path.moveTo(x-s*1.4,y-s*flap); path.quadTo(x-s*.5,y-s*.2,x,y); path.quadTo(x+s*.5,y-s*.2,x+s*1.4,y-s*flap*.8)
    path.quadTo(x+s*.4,y+s*.25,x,y+s*.3); path.quadTo(x-s*.4,y+s*.25,x-s*1.4,y-s*flap)
    c.drawPath(path,paint('#141210',a))

def flash(ctx,e,t,frame):
    a=fade_env(t,e['t0'],e['t1'],e.get('fi',.15),e.get('fo',.4))*e.get('a',1)
    if a>0: ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('color','#ffffff'),a))

def glitch(ctx,e,t,frame):
    """1-3 frame transition glitch: optional bg fill + oversized text with RGB split (ref: 10.03 / 19.23 / 44.03)"""
    if not (e['t0']<=t<e['t1']): return
    c=ctx.c; u=U(ctx)
    if e.get('bg'): c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e['bg'],1))
    if e.get('tint'): p=paint(e['tint'],e.get('tint_a',.6)); p.setBlendMode(skia.BlendMode.kMultiply); c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),p)
    if e.get('text'):
        sp=e.get('split',10)
        base=dict(type='text',text=e['text'],t0=e['t0']-1,t1=e['t1']+1,x=e['x'],y=e['y'],size=e['size'],font=e.get('font','serif-vf'),weight=e.get('weight',900),fi=.001,fo=.001,anim_in='none')
        if sp:
            for dx,col in ((-sp,'#00e5ff'),(sp,'#ff2a3a')): el_text(ctx,dict(base,x=e['x']+dx,color=col),t,frame)
        el_text(ctx,dict(base,color=e.get('color','#ffffff')),t,frame)

def glitter(ctx,e,t,frame):
    """sparkle burst on water when a flying glyph passes the camera (ref 27.3/27.7/28.1/28.5)"""
    a=fade_env(t,e['t0'],e['t1'],.02,e.get('fo',.25))
    if a<=0: return
    c=ctx.c; u=U(ctx); rng=random.Random(e.get('seed',1)); y0,y1=e.get('band',[300,470]); k=prog(t,e['t0'],e['t1']-e['t0'])
    for i in range(e.get('n',900)):
        x=rng.uniform(0,1024); y=rng.uniform(y0,y1); ph=rng.random(); r=rng.uniform(.6,1.8)*(.6+.8*(y-y0)/(y1-y0))
        tw=.5+.5*math.sin(t*25+ph*6.28)
        if rng.random()<1-k*.7: c.drawCircle(x*u,y*u,r*u,paint('#ffffff',a*tw*rng.uniform(.4,1)))

def lightcross(ctx,e,t,frame):
    """bright cross / beam of light opening on the text wall (09-10s)"""
    u=U(ctx); c=ctx.c; a=fade_env(t,e['t0'],e['t1'],.2,.3)
    if a<=0: return
    k=ease_out_expo(prog(t,e['t0'],.6))
    c.drawRect(skia.Rect.MakeXYWH(ctx.W/2-8*u*k,0,16*u*k,ctx.H),paint('#ffffff',a,blur=6*u))
    c.drawRect(skia.Rect.MakeXYWH(0,ctx.H*.42-5*u*k,ctx.W,10*u*k),paint('#ffffff',a,blur=6*u))


def spark(ctx,e,t,frame):
    a=fade_env(t,e['t0'],e['t1'],.3,.3)*e.get('a',1)
    if a<=0: return
    RICH.motes(ctx.c,ctx.W,ctx.H,t,n=e.get('n',40),color=e.get('color','#2a2622'),a=a*.3,seed=e.get('seed',13),speed=e.get('speed',.7))

EXTRA={'spark':spark,'geomap':geomap,'cubes3d':cubes3d,'text3d':text3d,'tile':tile,'hud':hud,'ink_burst':ink_burst,'splatter':splatter,'charwall':charwall,'tilegrid':tilegrid,
       'cards':cards,'timeline':timeline,'ring':ring,'bird':bird,'flash':flash,'lightcross':lightcross,'glitch':glitch,'glitter':glitter}

def _render_sc(ctx,sc,t,frame):
    bg(ctx,sc,t,frame)
    draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)

def draw(ctx,t,frame,S):
    ctx.beats=S.get('beats',[])
    RICH.compose_scenes(ctx,S,t,frame,_render_sc,overlays_extra=EXTRA,clear=None,
                        vignette_s=.25,grain_a=.05,band_color='#c8362a',design_size=(1024,576))
    if S.get('beat_punch',False) and getattr(ctx,'beats',None):
        RICH.beat_punch(ctx.c,ctx.W,ctx.H,t,ctx.beats,a=min(S.get('punch_a',.05),.05),color=S.get('punch_col','#c8362a'),window=.06)
