"""#6 剪影舞台·信纸 (silhouette-stage-paper) — reference 7692022955122937098 《知识诅咒》.
Music-only explainer: dark bokeh night (#0e0f16) with warm/blue blurred orbs, a wooden stage floor, glowing cream
silhouettes (#fbefd8), gold UI (#b08a4f / #ffe6a0), letter-paper documents, red stamps (#c8402a), bold-serif
subtitles (#f7e9cc) with gold (#f4e695) / red (#e8553a) keyword highlights, top-left info card, top-right citation."""
import os, math, random, numpy as np, skia
from engine.core import *
from engine.layers import draw_elements, U, el_text

CREAM='#fbefd8'; GOLD='#c9a465'; GOLD_L='#ffe6a0'; RED='#d24a35'; SUB='#f7e9cc'; HL='#f4e08a'; HLR='#ee5b3f'
def prepare(S): pass

# ---------------- backgrounds ----------------
def orbs(ctx,t,seed=1,n=78,warm=.6,a=1.):
    u=U(ctx); rng=random.Random(seed); c=ctx.c
    def fn():
        for i in range(n):
            x=rng.random()*1100-40; y=rng.random()*620-20; r=rng.uniform(14,56)
            dx=math.sin(t*.12+i)*22; dy=math.cos(t*.09+i*1.7)*12
            col= rng.choice(['#8a6a44','#9a7a52','#6a5640','#a8875e']) if rng.random()<warm else rng.choice(['#3a4660','#46526a','#5a5e66'])
            al=rng.uniform(.05,.14)*a*(.75+.25*math.sin(t*.5+i))
            c.drawCircle((x+dx)*u,(y+dy)*u,r*u,paint(col,al)); c.drawCircle((x+dx)*u,(y+dy)*u,r*.94*u,paint(col,al*.7,stroke=1.6*u))  # lens-bokeh rim
    blurred_layer(c,fn,3.5*u)
    for i in range(70):  # fine dust specks
        x=rng.random()*1024; y=rng.random()*576; c.drawCircle((x+t*3*rng.uniform(-1,1))*u%ctx.W,y*u,rng.uniform(.4,1.1)*u,paint('#d8c8a8',a*rng.uniform(.06,.25)))

def base_dark(ctx,col='#0f0f15'):
    c=ctx.c; W,H=ctx.W,ctx.H; c.clear(hexc(col))
    sh=skia.GradientShader.MakeLinear([(0,0),(0,H)],[hexc('#0e0d12'),hexc('#08080b')]); p=skia.Paint(); p.setShader(sh); c.drawRect(skia.Rect.MakeWH(W,H),p)

def floor(ctx,y=398,a=1.):
    c=ctx.c; u=U(ctx); W,H=ctx.W,ctx.H; Y=y*u
    sh=skia.GradientShader.MakeLinear([(0,Y),(0,H)],[hexc('#3a2c1e',a),hexc('#130d09',a)]); p=skia.Paint(); p.setShader(sh)
    c.drawRect(skia.Rect.MakeLTRB(0,Y,W,H),p)
    sh2=skia.GradientShader.MakeRadial((W/2,Y),W*.45,[hexc('#6a4e2e',.35*a),hexc('#6a4e2e',0)]); p2=skia.Paint(); p2.setShader(sh2)
    c.drawRect(skia.Rect.MakeLTRB(0,Y,W,H),p2)
    line(c,0,Y,W,Y,'#8a7050',.35*a,1*u,cap=False)

def spot(ctx,x=512,a=.5):
    c=ctx.c; u=U(ctx)
    sh=skia.GradientShader.MakeRadial((x*u,0),360*u,[hexc('#fff2d8',.16*a),hexc('#fff2d8',0)]); p=skia.Paint(); p.setShader(sh)
    c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),p)

def rays(ctx,t,a=1.,cx=512,cy=250):
    c=ctx.c; u=U(ctx)
    for i in range(36):
        ang=i/36*2*math.pi+t*.02
        x1=cx+math.cos(ang)*900; y1=cy+math.sin(ang)*900
        line(c,cx*u,cy*u,x1*u,y1*u,'#c8a870',a*.06,1.2*u,cap=False)

def seat_tex(cell=96,n=12,seed=3):
    """tile texture: n x n cells, each with gold dotted border + clustered blue 'audience' dots"""
    rng=np.random.default_rng(seed); S=cell*n
    img=np.zeros((S,S,4),np.uint8)
    for gy in range(n):
        for gx in range(n):
            y0,x0=gy*cell,gx*cell
            sp=4
            for yy in range(y0+5,y0+cell-3,sp):
                for xx in range(x0+5,x0+cell-3,sp):
                    if rng.random()<.5:
                        v=rng.uniform(.2,.9); col=np.array([90,110,165])*v
                        img[yy:yy+2,xx:xx+2,:3]=col.astype(np.uint8); img[yy:yy+2,xx:xx+2,3]=255
            for xx in range(x0,x0+cell,3): img[y0:y0+2,xx:xx+2]=[214,172,100,235]
            for yy in range(y0,y0+cell,3): img[yy:yy+2,x0:x0+2]=[214,172,100,235]
    return skia.Image.fromarray(img,colorType=skia.kRGBA_8888_ColorType)
_SEAT={}
def gridfloor(ctx,t,a=1.,hz=-120,near=290,speed=.12,yaw=0):
    """true perspective audience plane (homography), horizon above frame, slow dolly forward"""
    c=ctx.c; u=U(ctx); W,H=ctx.W,ctx.H
    if 'seat' not in _SEAT: _SEAT['seat']=seat_tex()
    img=_SEAT['seat']; cell=96
    hzp=hz*u; f=W*.9; z0=1.0; hc=(H-hzp)/f; g=near*u/f; A=40.0; Z1=60.0
    def P(X,Z): return skia.Point(W/2+f*X/Z, hzp+f*hc/Z)
    toT=lambda v: v/g*cell
    sc_=-t*speed*g*cell/ g/cell*g  # world units
    src=[skia.Point(toT(-A),toT(-Z1+sc_)),skia.Point(toT(A),toT(-Z1+sc_)),skia.Point(toT(A),toT(-z0+sc_)),skia.Point(toT(-A),toT(-z0+sc_))]
    dst=[P(-A,Z1),P(A,Z1),P(A,z0),P(-A,z0)]
    m=skia.Matrix(); m.setPolyToPoly(dst,src); inv=skia.Matrix(); m.invert(inv)
    sh=img.makeShader(skia.TileMode.kRepeat,skia.TileMode.kRepeat,skia.SamplingOptions(skia.FilterMode.kLinear,skia.MipmapMode.kLinear),skia.Matrix.RotateDeg(yaw))
    p=skia.Paint(AntiAlias=True); p.setShader(sh); p.setAlphaf(a*.85)
    c.save(); c.concat(inv); c.drawRect(skia.Rect.MakeLTRB(toT(-A),toT(-Z1+sc_),toT(A),toT(-z0+sc_)),p); c.restore()
    g2=skia.GradientShader.MakeLinear([(0,0),(0,H*.45)],[hexc('#05060a',.85),hexc('#05060a',0)]); q=skia.Paint(); q.setShader(g2); c.drawRect(skia.Rect.MakeWH(W,H),q)
    spot(ctx,512,1.0)

def night(ctx,t):
    c=ctx.c; W,H=ctx.W,ctx.H; u=U(ctx)
    sh=skia.GradientShader.MakeLinear([(0,0),(0,H)],[hexc('#070b16'),hexc('#0d172d'),hexc('#05080f')],[0,.62,1]); p=skia.Paint(); p.setShader(sh); c.drawRect(skia.Rect.MakeWH(W,H),p)
    rng=random.Random(4)
    for i in range(160): c.drawCircle(rng.random()*W,rng.random()*H*.8,rng.uniform(.4,1.2)*u,paint('#cfd8ff',rng.uniform(.15,.6)))
    for k in range(3):  # soft waves
        path=skia.Path(); y0=(470+k*30)*u; path.moveTo(0,H)
        for x in range(0,1030,20): path.lineTo(x*u,y0+math.sin(x/90+t*.3+k)*12*u)
        path.lineTo(W,H); path.close(); c.drawPath(path,paint('#0e1a33',.55))

def bg(ctx,sc,t,frame):
    kind=sc.get('bg','bokeh'); base_dark(ctx)
    if kind=='night': night(ctx,t); return
    if kind=='grid': gridfloor(ctx,t); return
    orbs(ctx,t,seed=sc.get('seed',1),a=sc.get('orb_a',1.))
    if kind=='stage': floor(ctx,sc.get('floor_y',398)); spot(ctx,sc.get('spot_x',512),sc.get('spot_a',.8))
    if kind=='title': rays(ctx,t)
    vignette(ctx.c,ctx.W,ctx.H,.55)

# ---------------- elements ----------------
def env(e,t,fi=.35,fo=.3): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1.)

def subtitle(ctx,e,t,frame):
    """bottom subtitle: bold serif cream, typewriter reveal, keyword highlight via [[i0,i1,color]]"""
    a=env(e,t,.15,.15)
    if a<=0: return
    ee=dict(type='text',text=e['text'],t0=e['t0'],t1=e['t1'],x=512,y=e.get('y',528),size=e.get('size',25.5),font='serif-vf',weight=700,
            color=SUB,hl=e.get('hl',[]),anim_in='type',cps=e.get('cps',32),char_fade=.12,fi=.01,fo=.15,glow=0)
    ctx.c.save(); el_text(ctx,ee,t,frame); ctx.c.restore()

def infocard(ctx,e,t,frame):
    """top-left info card: big serif number (gold or red) + small label"""
    u=U(ctx); c=ctx.c; a=env(e,t)
    if a<=0: return
    rrect(c,8*u,10*u,104*u,40*u,3*u,fill='#15151d',stroke='#2c2c36',a=a*.85,sw=1*u)
    val=e['value']
    if 'count' in e:  # mm:ss count-up timer
        k=prog(t,e.get('count_at',e['t0']),e['count'][2]); sec=lerp(e['count'][0],e['count'][1],ease_in_out_cubic(k)); val=f"{int(sec//60):02d}:{int(sec%60):02d}"
    draw_text(c,val,18*u,38*u,font('garamond',24*u,500),e.get('color','#c9a465'),a,'left')
    draw_text(c,e.get('label',''),18*u,49*u,font('serif',6.5*u),'#8a8378',a,'left')

def cite(ctx,e,t,frame):
    u=U(ctx); c=ctx.c; a=env(e,t)
    if a<=0: return
    draw_text(c,e['ref'],960*u,34*u,font('garamond',7.5*u,400),'#77705f',a,'right')
    draw_text(c,e['title'],960*u,49*u,font('serif-vf',8.5*u,600),'#c9a465',a,'right')
    rrect(c,968*u,26*u,22*u,22*u,1.5*u,fill='#9a3a2a',a=a); draw_text(c,'证',979*u,42*u,font('serif-vf',11*u,700),'#f0d8c0',a)

def figure(ctx,e,t,frame):
    """glowing cream silhouette (head + dome body), optional pointing arm, dim / small variants, labels below"""
    u=U(ctx); c=ctx.c; a=env(e,t,.5,.4)
    if a<=0: return
    x=e['x']*u; base=e.get('y',412)*u; s=e.get('s',1.)*u; col=e.get('color',CREAM); dim=e.get('dim',0)
    if dim: col='#8a8278'
    glow=e.get('glow',1)*(0 if dim else 1)
    k=ease_out_back(prog(t,e['t0'],.5),1.2)
    c.save(); c.translate(x,base); c.scale(1,max(.01,k)); 
    hr=17*s; bw=48*s; bh=78*s
    body=skia.Path(); body.moveTo(-bw,0); body.cubicTo(-bw,-bh*.95,bw,-bh*.95,bw,0); body.close()
    if glow:
        c.drawPath(body,paint('#ffe8b8',a*.35,blur=16*s)); c.drawCircle(0,-bh-hr*.9,hr*1.6,paint('#ffe8b8',a*.3,blur=12*s))
    c.drawPath(body,paint(col,a)); c.drawCircle(0,-bh-hr*.75,hr,paint(col,a))
    if e.get('arm'):
        ang=math.radians(e.get('arm_angle',-12)+math.sin(t*e.get('tap',0)*6.28)*6*bool(e.get('tap')))
        sx,sy=bw*.55*e.get('side',1),-bh*.6; L=62*s
        ex,ey=sx+math.cos(ang)*L*e.get('side',1),sy+math.sin(ang)*L
        line(c,sx,sy,ex,ey,col,a,10*s); c.drawCircle(ex,ey,5.5*s,paint(col,a))
    c.restore()
    if e.get('label'):
        draw_text(c,e['label'],x,base+48*u,font('serif-vf',9.5*u,600),e.get('label_color','#a88e64'),a)
    if e.get('ring'):
        p=paint('#c9a465',a*.5,stroke=1*u); c.drawOval(skia.Rect.MakeXYWH(x-60*s,base-4*u,120*s,16*u),p)

def icon_person(c,x,y,s,col,a):
    c.drawCircle(x,y-s*.55,s*.28,paint(col,a))
    p=skia.Path(); p.moveTo(x-s*.5,y+s*.35); p.cubicTo(x-s*.5,y-s*.3,x+s*.5,y-s*.3,x+s*.5,y+s*.35); p.close(); c.drawPath(p,paint(col,a))

def crowd(ctx,e,t,frame):
    """grid of small person icons; reveal row-by-row; 'hits' highlighted with ring, rest dimmed after dim_at"""
    u=U(ctx); c=ctx.c; a=env(e,t)
    if a<=0: return
    cols,rows=e.get('cols',12),e.get('rows',10); x0,y0=e['x0'],e['y0']; dx,dy=e.get('dx',21),e.get('dy',23)
    n=e.get('n',cols*rows); k=prog(t,e['t0'],e.get('reveal',1.5)); dimk=prog(t,e.get('dim_at',1e9),.5)
    hits=set(map(tuple,e.get('hits',[])))
    for i in range(n):
        r,cc=divmod(i,cols)
        if i/n>k: break
        x=(x0+cc*dx)*u; y=(y0+r*dy)*u
        if (r,cc) in hits and dimk>0:
            c.drawCircle(x,y-2*u,15*u,paint('#fbefd8',a*dimk)); c.drawCircle(x,y-2*u,15*u,paint('#c9a465',a*dimk,stroke=1.5*u))
            icon_person(c,x,y,17*u,'#3a2c1e',a); continue
        col=lerp_col('#d8b070','#5a554e',dimk)
        icon_person(c,x,y,12*u,col,a*(1-.4*dimk))

def lerp_col(c1,c2,k):
    a=[int(c1[i:i+2],16) for i in (1,3,5)]; b=[int(c2[i:i+2],16) for i in (1,3,5)]
    return '#%02x%02x%02x'%tuple(int(lerp(x,y,k)) for x,y in zip(a,b))

def bubble(ctx,e,t,frame):
    """dark rounded box with gold/red border + pointer; content: text | wave | dots"""
    u=U(ctx); c=ctx.c; a=env(e,t,.3,.25)
    if a<=0: return
    k=ease_out_back(prog(t,e['t0'],.35),1.3)
    x,y,w,h=e['x']*u,e['y']*u,e['w']*u,e['h']*u
    c.save(); c.translate(x,y); c.scale(k,k)
    border=e.get('border','#c9a465'); fill=e.get('fill','#17161c')
    rrect(c,-w/2,-h/2,w,h,4*u,fill=fill,stroke=border,a=a,sw=1.2*u)
    if e.get('pointer',True):
        pp=skia.Path(); px=e.get('px',0)*u; py=h/2 if e.get('pdir','down')=='down' else -h/2; d=1 if e.get('pdir','down')=='down' else -1
        pp.moveTo(px-6*u,py); pp.lineTo(px,py+9*u*d); pp.lineTo(px+6*u,py); pp.close(); c.drawPath(pp,paint(e.get('pcolor',border),a))
    kind=e.get('kind','text')
    if kind=='text':
        f=font('serif-vf',e.get('size',11)*u,e.get('weight',600))
        lines=e['text'].split('\n')
        for i,l in enumerate(lines):
            draw_text(c,l,0,(i-(len(lines)-1)/2)*e.get('size',11)*1.5*u+e.get('size',11)*.36*u,f,e.get('color','#e8dcc4'),a)
    elif kind=='wave':
        path=skia.Path(); n=60
        for i in range(n+1):
            xx=-w*.42+w*.84*i/n; yy=math.sin(i*.35+t*3)*h*.18*math.sin(i/n*math.pi)+math.sin(i*.9+t*5)*h*.06
            path.moveTo(xx,yy) if i==0 else path.lineTo(xx,yy)
        c.drawPath(path,paint(GOLD_L,a,stroke=1.6*u))
    elif kind=='dots':
        for i in range(3):
            on=(t*2.2-i*.35)%1.4<.9
            c.drawCircle((i-1)*12*u,0,(4 if i!=2 else 3)*u,paint('#e8e0d0',a*(1 if on else .35)))
    c.restore()
    if e.get('caption'):
        draw_text(c,e['caption'],x,y-h/2-8*u,font('serif',8*u),'#d8ccb4',a)

def tag(ctx,e,t,frame):
    """small outlined pill/label (song titles, side labels)"""
    u=U(ctx); c=ctx.c; a=env(e,t,.25,.25)
    if a<=0: return
    f=font('serif-vf',e.get('size',9)*u,e.get('weight',500)); tw=f.measureText(e['text']); pad=e.get('pad',8)*u; h=e.get('h',16)*u
    x,y=e['x']*u,e['y']*u
    if e.get('box',True): rrect(c,x-tw/2-pad,y-h/2,tw+2*pad,h,e.get('r',h/2/u)*u,fill=e.get('fill','#17161c'),stroke=e.get('border','#a88e64'),a=a,sw=1*u)
    draw_text(c,e['text'],x,y+e.get('size',9)*.36*u,f,e.get('color','#e0d4bc'),a)

_FIB=[]
def fiber(c,rect,a=1.):
    """AI paper-fiber texture (skill/assets/tex/paper_fiber.png) as multiply detail layer; fallback: none"""
    if not _FIB:
        pth=os.path.join(os.path.dirname(__file__),'..','..','assets','tex','paper_fiber.png'); im=None
        if os.path.exists(pth):
            import cv2; g=cv2.imread(pth,cv2.IMREAD_GRAYSCALE).astype(np.float32); g=cv2.resize(g,(1024,1024),interpolation=cv2.INTER_CUBIC)
            g=cv2.bilateralFilter(g,5,12,5); g=255-(g.mean()-g)*2.2  # high-pass detail around white
            g=g.clip(0,255).astype(np.uint8); im=skia.Image.fromarray(np.dstack([g,g,g,np.full_like(g,255)]),colorType=skia.kRGBA_8888_ColorType)
        _FIB.append(im)
    im=_FIB[0]
    if im is None: return
    p=skia.Paint(); p.setShader(im.makeShader(skia.TileMode.kRepeat,skia.TileMode.kRepeat,skia.SamplingOptions(skia.FilterMode.kLinear))); p.setBlendMode(skia.BlendMode.kMultiply); p.setAlphaf(min(1,a)*.9)
    c.drawRect(rect,p)

def paper(ctx,e,t,frame):
    """letter paper / document card on stage: title, rows, ruled lines, optional red top bar; tilt; slide-in"""
    u=U(ctx); c=ctx.c; a=env(e,t,.5,.35)
    if a<=0: return
    k=ease_out_cubic(prog(t,e['t0'],.7)); mv=e.get('move')
    x,y,w,h=e['x'],e['y'],e['w'],e['h']
    if mv:  # [t, x, y, scale]
        mk=ease_in_out_cubic(prog(t,mv[0],.8)); x=lerp(x,mv[1],mk); y=lerp(y,mv[2],mk); sc=lerp(1,mv[3],mk); w*=sc; h*=sc
    x,y,w,h=x*u,(y+(1-k)*30)*u,w*u,h*u; s=w/(e['w']*u)
    c.save(); c.translate(x,y); c.rotate(e.get('rot',3))
    rrect(c,-w/2+6*u,-h/2+10*u,w,h,2*u,fill='#000000',a=a*.5,blur=10*u)
    sh=skia.GradientShader.MakeLinear([(-w/2,-h/2),(w/2,h/2)],[hexc('#f6ecd6',a),hexc('#e6d6b6',a)]); p=skia.Paint(AntiAlias=True); p.setShader(sh)
    c.drawRect(skia.Rect.MakeXYWH(-w/2,-h/2,w,h),p); fiber(c,skia.Rect.MakeXYWH(-w/2,-h/2,w,h),a)
    if e.get('topbar'): c.drawRect(skia.Rect.MakeXYWH(-w/2,-h/2,w,3*u*s),paint('#c8402a',a))
    for it in e.get('items',[]):
        f=font(it.get('font','serif-vf'),it.get('size',9)*u*s,it.get('weight',500))
        draw_text(c,it['text'],it.get('x',0)*u*s,it['y']*u*s,f,it.get('color','#3a2e22'),a*it.get('a',1),it.get('align','center'))
    for ln in e.get('lines',[]):  # ruled text lines
        y0,x0,x1,n,gap=ln; 
        for i in range(n): line(c,x0*u*s,(y0+i*gap)*u*s,(x1-(i%3)*8)*u*s,(y0+i*gap)*u*s,'#8a7a62',a*.6,1.6*u*s,cap=False)
    c.restore()

def stamp(ctx,e,t,frame):
    """red rotated stamp box with text; slams in (scale 1.6->1)"""
    u=U(ctx); c=ctx.c; a=env(e,t,.12,.3)
    if a<=0: return
    k=ease_out_back(prog(t,e['t0'],.25),1.5); s=lerp(1.7,1,k)
    f=font(e.get('font','serif-vf'),e.get('size',22)*u,e.get('weight',800)); tw=f.measureText(e['text']); pad=e.get('pad',8)*u; h=e.get('size',22)*1.5*u
    c.save(); c.translate(e['x']*u,e['y']*u); c.rotate(e.get('rot',-10)); c.scale(s,s)
    rrect(c,-tw/2-pad,-h/2,tw+2*pad,h,2*u,fill=e.get('fill'),stroke=e.get('color','#d24a35'),a=a*.95,sw=2*u)
    draw_text(c,e['text'],0,e.get('size',22)*.36*u,f,e.get('color','#d24a35') if not e.get('fill') else '#f8e8d8',a)
    c.restore()

def bars(ctx,e,t,frame):
    """vertical bars from a baseline (pred vs actual etc.)"""
    u=U(ctx); c=ctx.c; a=env(e,t)
    if a<=0: return
    base=e['base']*u
    for i,b in enumerate(e['bars']):
        k=ease_out_cubic(prog(t,e['t0']+b.get('delay',i*.25),.7))
        x,w,hh=b['x']*u,b['w']*u,b['h']*u*k
        sh=skia.GradientShader.MakeLinear([(0,base-hh),(0,base)],[hexc(b.get('c1','#d8b878'),a),hexc(b.get('c2','#8a6a3a'),a)]); p=skia.Paint(); p.setShader(sh)
        c.drawRect(skia.Rect.MakeXYWH(x-w/2,base-hh,w,hh),p)
        if b.get('value'): draw_text(c,b['value'],x,base-hh-8*u,font('serif-vf',b.get('vsize',15)*u,700),b.get('vcolor','#f4e0b8'),a*k)
        if b.get('label'): draw_text(c,b['label'],x,base+14*u,font('serif',7.5*u),b.get('lcolor','#a89880'),a)
    if e.get('axis',True): line(c,e.get('ax0',340)*u,base,e.get('ax1',680)*u,base,'#6a5a48',a,1*u,cap=False)

def phone(ctx,e,t,frame):
    """phone chat: outline phone, header, gold voice/text bubbles appearing over time, gray reply; glitch option"""
    u=U(ctx); c=ctx.c; a=env(e,t,.4,.3)
    if a<=0: return
    x,y,w,h=e.get('x',512)*u,e.get('y',278)*u,e.get('w',114)*u,e.get('h',216)*u
    gl=prog(t,e.get('glitch_at',1e9),.6)
    c.save()
    if gl>0: c.translate(math.sin(t*90)*4*u*gl,0)
    rrect(c,x-w/2,y-h/2,w,h,14*u,fill='#121218',stroke='#6a6a72',a=a,sw=1.4*u)
    rrect(c,x-17*u,y-h/2+6*u,34*u,7*u,3.5*u,fill='#050507',a=a)
    draw_text(c,e.get('clock','22:47'),x-w/2+12*u,y-h/2+14*u,font('garamond',6*u),'#b0aaa0',a,'left')
    draw_text(c,'对方',x,y-h/2+30*u,font('serif-vf',7.5*u,600),'#e0d8c8',a); line(c,x-w/2+4*u,y-h/2+37*u,x+w/2-4*u,y-h/2+37*u,'#3a3a40',a,.8*u)
    # messages: list of {t, text, voice(bool), me(bool)}; newest at bottom, scroll up
    msgs=[m for m in e['msgs'] if t>=m['t']]
    yb=y+h/2-62*u; gap=20*u
    for i,m in enumerate(reversed(msgs[-e.get('max',6):])):
        my=yb-i*gap; k=ease_out_back(prog(t,m['t'],.3),1.4)
        f=font('serif',6.6*u); txt=m['text']; bw=max(28*u,f.measureText(txt)+14*u)
        if m.get('reply'):
            bx=x-w/2+8*u; rrect(c,bx,my-4*u,40*u,22*u,4*u,fill='#3a3a44',a=a*k); draw_text(c,txt,bx+20*u,my+11*u,font('serif-vf',11*u,700),'#f0ece4',a*k); continue
        bx=x+w/2-8*u-bw
        rrect(c,bx,my-8*u,bw,15*u,3*u,fill='#c9a060',a=a*k)
        if txt.startswith('▮'):   # voice message: code-drawn waveform bars + duration
            rest=txt.lstrip('▮ '); hs=[3,6,9,5,7]
            for j,hh in enumerate(hs): c.drawRect(skia.Rect.MakeXYWH(bx+7*u+j*3.2*u,my-.5*u-hh*.5*u,1.6*u,hh*u),paint('#2a2014',a*k))
            draw_text(c,rest,bx+bw-7*u,my+2.2*u,f,'#2a2014',a*k,'right')
        else: draw_text(c,txt,bx+bw/2,my+2.2*u,f,'#2a2014',a*k)
    rrect(c,x-w/2+8*u,y+h/2-20*u,w-16*u,11*u,5.5*u,stroke='#4a4a52',a=a,sw=1*u)
    c.restore()
    if gl>0:
        rng=random.Random(int(t*20))
        for i in range(10):
            yy=y+rng.uniform(-h/2,h/2); c.drawRect(skia.Rect.MakeXYWH(x-w/2,yy,w,rng.uniform(1,4)*u),paint(rng.choice(['#c8402a','#e0d0c0']),a*gl*.8))

def linkline(ctx,e,t,frame):
    """horizontal knowledge line: left node (gray) -> right node (gold), dashed arc back crossed with X"""
    u=U(ctx); c=ctx.c; a=env(e,t)
    if a<=0: return
    x0,x1,y=e['x0']*u,e['x1']*u,e['y']*u; k=ease_in_out_cubic(prog(t,e['t0'],.8))
    line(c,x0,y,lerp(x0,x1,k),y,'#c9a465',a,2*u)
    c.drawCircle(x0,y,5*u,paint('#8a8580',a)); 
    if k>.95: glow_dot(c,x1,y,6*u,'#ffd88a',a,3)
    draw_text(c,e.get('l0','不知道'),x0,y-14*u,font('serif-vf',10*u,600),'#a8a298',a); draw_text(c,e.get('l1','知道'),x1,y-14*u,font('serif-vf',10*u,600),'#ffe6a0',a)
    if t>e.get('back_at',1e9):
        kb=prog(t,e['back_at'],.8); path=skia.Path(); path.moveTo(x1,y+8*u); path.quadTo((x0+x1)/2,y+60*u,lerp(x1,x0,1),y+8*u)
        p=paint('#c8402a',a*.8,stroke=1.4*u); p.setPathEffect(skia.DashPathEffect.Make([5*u,4*u],0)); 
        meas=skia.PathMeasure(path,False); seg=skia.Path(); meas.getSegment(0,meas.getLength()*kb,seg,True); c.drawPath(seg,p)
        if kb>.6: xm=(x0+x1)/2; ym=y+34*u; s=7*u; line(c,xm-s,ym-s,xm+s,ym+s,'#e0503a',a,2*u); line(c,xm-s,ym+s,xm+s,ym-s,'#e0503a',a,2*u)

def titlecard(ctx,e,t,frame):
    """big gold title with small spaced english kicker, optional box"""
    u=U(ctx); c=ctx.c; a=env(e,t,.6,.5)
    if a<=0: return
    x,y=e.get('x',512)*u,e.get('y',255)*u; sz=e.get('size',58)
    if e.get('box'):
        bx,by,bw,bh=[v*u for v in e['box']]; rrect(c,bx,by,bw,bh,2*u,fill='#16151c',stroke='#5a4a36',a=a*.92,sw=1.2*u)
    k=ease_out_cubic(prog(t,e['t0'],.9))
    f=font('serif-vf',sz*u,800)
    draw_text(c,e['title'],x,y+sz*.36*u,f,GOLD_L,a*k,glow=10*u,glow_a=.45,glow_color='#e0a850',spacing=sz*.12*u)
    if e.get('kicker'): draw_text(c,e['kicker'],x,y-sz*.75*u,font('garamond',6.5*u,500),'#8a7a60',a,spacing=3*u)
    for i,s in enumerate(e.get('subs',[])):
        draw_text(c,s['text'],x,y+(sz*.9+14+i*15)*u,font('serif',s.get('size',11.5)*u),s.get('color','#b8b0a2'),a*fade_env(t,s.get('t0',e['t0']),e['t1'],.4,.3))
    if e.get('dot',True): c.drawCircle(x,y+sz*.62*u,1.6*u,paint('#e0c080',a))

def textbox(ctx,e,t,frame):
    u=U(ctx); c=ctx.c; a=env(e,t,.4,.3)
    if a<=0: return
    bx,by,bw,bh=[v*u for v in e['box']]; rrect(c,bx,by,bw,bh,3*u,fill='#14141a',stroke='#5a4a36',a=a*.92,sw=1.2*u)
    if e.get('kicker'): draw_text(c,e['kicker'],bx+bw/2,by+16*u,font('garamond',5.5*u,500),'#7a6a50',a,spacing=2.5*u)
    for i,l in enumerate(e['lines']):
        ee=dict(type='text',text=l['text'],t0=l.get('t0',e['t0']),t1=e['t1'],x=(bx+bw/2)/u,y=l['y'],size=l.get('size',17),font='serif-vf',weight=700,color=l.get('color',GOLD_L),anim_in='type',cps=14,fi=.01,fo=0)
        el_text(ctx,ee,t,frame)

def quotecard(ctx,e,t,frame):
    """small dark card with gold role pill + person icon + quote + red rebuttal strip"""
    u=U(ctx); c=ctx.c; a=env(e,t,.4,.3)
    if a<=0: return
    x,y=e['x']*u,e['y']*u; w,h=92*u,58*u; k=ease_out_cubic(prog(t,e['t0'],.4))
    c.save(); c.translate(0,(1-k)*12*u)
    rrect(c,x-w/2,y-h/2,w,h,2*u,fill='#16151c',stroke='#6a5a40',a=a,sw=1*u)
    rrect(c,x-9*u,y-h/2-4*u,18*u,8*u,1*u,fill='#c9a465',a=a); draw_text(c,e['role'],x,y-h/2+2.2*u,font('serif',4.8*u),'#2a2014',a)
    icon_person(c,x,y-12*u,13*u,'#e8b860',a)
    draw_text(c,e['quote'],x,y+14*u,font('serif-vf',8.2*u,600),'#efe6d2',a)
    if t>=e.get('rebut_at',1e9):
        kr=prog(t,e['rebut_at'],.3); rrect(c,x-w/2,y+h/2+3*u,w,13*u,1*u,fill='#5a1e16',stroke='#a03a2a',a=a*kr,sw=.8*u)
        draw_text(c,e['rebut'],x,y+h/2+12*u,font('serif',6*u),'#f0c0b0',a*kr)
    c.restore()

def glass(ctx,e,t,frame):
    """code-drawn Feynman ice-water glass: tapered thick glass, water w/ meniscus, 3D-ish ice cubes, bubbles, O-ring that cools gold->blue"""
    u=U(ctx); c=ctx.c; a=env(e,t,e.get('fi',.25))
    if a<=0: return
    sc_=e.get('s',1.0); x,y=e['x']*u,e['y']*u; w,h=64*u*sc_,76*u*sc_; bw=w*.84
    top,bot=y-h/2,y+h/2
    def gp(inset=0):
        p=skia.Path(); p.moveTo(x-w/2+inset,top); p.lineTo(x-bw/2+inset,bot-inset); p.lineTo(x+bw/2-inset,bot-inset); p.lineTo(x+w/2-inset,top); return p
    rrect(c,x-bw/2,bot-4*u,bw,10*u,4*u,fill='#000000',a=a*.45,blur=8*u)          # contact shadow
    wl=top+h*.30; c.save(); c.clipPath(gp(3*u),doAntiAlias=True)
    sh=skia.GradientShader.MakeLinear([(0,wl),(0,bot)],[hexc('#5fa8c0',a*.55),hexc('#2a5a70',a*.75)]); q=skia.Paint(AntiAlias=True); q.setShader(sh)
    c.drawRect(skia.Rect.MakeLTRB(x-w,wl,x+w,bot),q)
    rng=random.Random(7)
    for i,(dx,dy,r,rot) in enumerate([(-.22,.06,.17,12),(.12,-.02,.18,-18),(.26,.22,.15,30),(-.06,.30,.16,-6),(-.26,.38,.13,40)]):
        cx,cy,cs=x+dx*w,wl+dy*h+math.sin(t*1.3+i)*1.2*u,r*w
        c.save(); c.translate(cx,cy); c.rotate(rot+math.sin(t*.7+i)*3)
        rrect(c,-cs/2,-cs/2,cs,cs,cs*.12,fill='#d8f0f8',a=a*.30); rrect(c,-cs/2,-cs/2,cs,cs,cs*.12,stroke='#e8f8ff',a=a*.85,sw=1.1*u)
        c.drawLine(-cs*.3,-cs*.32,cs*.15,-cs*.32,paint('#ffffff',a*.8,stroke=1.4*u)); c.restore()
    for k in range(10):                                                             # rising bubbles
        bx=x+(rng.random()-.5)*bw*.8; ph=(t*.35+rng.random())%1; by=lerp(bot-6*u,wl+4*u,ph)
        c.drawCircle(bx,by,(1+rng.random()*1.5)*u,paint('#e8f8ff',a*.6*(1-ph),stroke=.8*u))
    c.drawOval(skia.Rect.MakeLTRB(x-w*.47,wl-4*u,x+w*.47,wl+4*u),paint('#bfe6f2',a*.55))   # meniscus
    c.restore()
    c.drawPath(gp(),paint('#d6e6ee',a*.95,stroke=2.2*u)); c.drawPath(gp(5*u),paint('#9ab8c4',a*.35,stroke=1*u))
    c.drawOval(skia.Rect.MakeLTRB(x-w/2,top-4*u,x+w/2,top+4*u),paint('#e0eef4',a*.8,stroke=1.6*u))
    c.drawLine(x-w*.36,top+h*.12,x-bw*.36,bot-h*.14,paint('#ffffff',a*.35,stroke=4*u))          # specular streak
    c.drawRect(skia.Rect.MakeLTRB(x-bw/2+3*u,bot-8*u,x+bw/2-3*u,bot-2*u),paint('#c8dce4',a*.35))  # thick base
    ck=prog(t,e.get('cool_at',1e9),.8)
    ring=T3mix(e.get('ring','#e8c070'),'#7ad0e8',ck); ry=top-42*u*sc_+math.sin(t*2)*2*u; rw=50*u*sc_
    c.drawOval(skia.Rect.MakeXYWH(x-rw/2,ry-4*u,rw,8*u),paint(ring,a*.35,stroke=4*u)); c.drawOval(skia.Rect.MakeXYWH(x-rw/2,ry-4*u,rw,8*u),paint(ring,a,stroke=1.6*u))

def T3mix(a_,b_,k):
    A=[int(a_[i:i+2],16) for i in (1,3,5)]; B=[int(b_[i:i+2],16) for i in (1,3,5)]
    return '#%02x%02x%02x'%tuple(int(lerp(p,q,k)) for p,q in zip(A,B))

def formula(ctx,e,t,frame):
    u=U(ctx); c=ctx.c; a=env(e,t)
    if a<=0: return
    bx,by,bw,bh=[v*u for v in e['box']]; rrect(c,bx,by,bw,bh,2*u,stroke='#8a8070',a=a,sw=1*u)
    for i,l in enumerate(e['lines']): draw_text(c,l,bx+bw/2,by+(18+i*18)*u,font('garamond-italic',8.5*u,400),'#d8d0c0',a)
    if t>=e.get('cross_at',1e9):
        k=prog(t,e['cross_at'],.3); line(c,bx,by+bh,lerp(bx,bx+bw,k),lerp(by+bh,by,k),'#d04030',a,2*u)

def tower(ctx,e,t,frame):
    u=U(ctx); c=ctx.c; a=env(e,t)
    if a<=0: return
    x,y=e['x']*u,e['y']*u
    c.drawRect(skia.Rect.MakeXYWH(x-5*u,y-40*u,10*u,82*u),paint('#d8d0c0',a,stroke=1.2*u))
    p=skia.Path(); p.moveTo(x-16*u,y-42*u); p.lineTo(x+16*u,y-42*u); p.lineTo(x+12*u,y-52*u); p.lineTo(x-12*u,y-52*u); p.close(); c.drawPath(p,paint('#5a8a90',a))
    for i in range(2):
        r=(18+i*14)*u; path=skia.Path(); path.addArc(skia.Rect.MakeXYWH(x+10*u-r,y-48*u-r,2*r,2*r),-40,80); c.drawPath(path,paint('#a8a090',a*.7,stroke=1*u))
    draw_text(c,'塔台',x,y+52*u,font('serif',7*u),'#a89880',a)

def plane(ctx,e,t,frame):
    u=U(ctx); c=ctx.c; a=env(e,t)
    if a<=0: return
    x,y=(e['x']+math.sin(t*.8)*3)*u,(e['y']+math.sin(t*1.3)*2)*u; s=e.get('s',1)*u
    p=skia.Path(); p.moveTo(x-22*s,y); p.lineTo(x+20*s,y-2*s); p.lineTo(x+24*s,y+1*s); p.lineTo(x-22*s,y+3*s); p.close()
    w=skia.Path(); w.moveTo(x-2*s,y); w.lineTo(x+6*s,y-16*s); w.lineTo(x+10*s,y-16*s); w.lineTo(x+6*s,y+1*s); w.lineTo(x+10*s,y+18*s); w.lineTo(x+6*s,y+18*s); w.close()
    t_=skia.Path(); t_.moveTo(x-20*s,y); t_.lineTo(x-24*s,y-9*s); t_.lineTo(x-20*s,y-9*s); t_.lineTo(x-14*s,y); t_.close()
    for q in (p,w,t_): c.drawPath(q,paint('#f4ecdc',a))

def book(ctx,e,t,frame):
    u=U(ctx); c=ctx.c; a=env(e,t,.5,.3)
    if a<=0: return
    x,y,w,h=e['x']*u,e['y']*u,e.get('w',82)*u,e.get('h',118)*u; k=ease_out_cubic(prog(t,e['t0'],.6))
    c.save(); c.translate(x,y+(1-k)*20*u); c.rotate(e.get('rot',4))
    rrect(c,-w/2+5*u,-h/2+8*u,w,h,2*u,fill='#000000',a=a*.5,blur=8*u)
    rrect(c,-w/2,-h/2,w,h,2*u,fill=e.get('color','#1e3468'),a=a); rrect(c,-w/2+5*u,-h/2+5*u,w-10*u,h-10*u,1*u,stroke='#c9a465',a=a*.6,sw=.8*u)
    draw_text(c,e['title'],0,-4*u,font('serif-vf',12*u,800),'#f4e8cc',a)
    if e.get('sub'): draw_text(c,e['sub'],0,10*u,font('garamond',4.5*u,500),'#c8b890',a)
    c.restore()

def menu(ctx,e,t,frame):
    """top-left checklist panel: header + items, current one highlighted, previous checked"""
    u=U(ctx); c=ctx.c; a=env(e,t)
    if a<=0: return
    rrect(c,8*u,10*u,108*u,58*u,3*u,fill='#14141a',stroke='#2c2c36',a=a*.85,sw=1*u)
    draw_text(c,e['header'],16*u,22*u,font('serif',6*u),'#8a8378',a,'left')
    for i,it in enumerate(e['items']):
        cur=e.get('current',0); col='#f0d890' if i==cur else ('#c8c0b0' if i<cur else '#6a655e')
        c.drawCircle(19*u,(32+i*11)*u,2.6*u,paint(col,a,stroke=.9*u))
        draw_text(c,it,26*u,(34.5+i*11)*u,font('serif-vf',6.8*u,600 if i==cur else 400),col,a,'left')

def caption(ctx,e,t,frame):
    u=U(ctx); a=env(e,t)
    if a>0: draw_text(ctx.c,e['text'],e.get('x',512)*u,e.get('y',38)*u,font('serif',e.get('size',8)*u),e.get('color','#8a8378'),a,spacing=e.get('spacing',1.5)*u)

def coins(ctx,e,t,frame):
    u=U(ctx); c=ctx.c; a=env(e,t)
    if a<=0: return
    for i in range(e.get('n',4)): c.drawOval(skia.Rect.MakeXYWH((e['x']-8)*u,(e['y']-i*4)*u,16*u,5*u),paint('#d8a850',a))

def curve(ctx,e,t,frame):
    u=U(ctx); c=ctx.c; a=env(e,t)
    if a<=0: return
    k=ease_in_out_cubic(prog(t,e['t0'],e.get('draw',1.0))); pts=e['pts']
    path=skia.Path(); path.moveTo(pts[0]*u,pts[1]*u); path.quadTo(pts[2]*u,pts[3]*u,pts[4]*u,pts[5]*u)
    meas=skia.PathMeasure(path,False); seg=skia.Path(); meas.getSegment(0,meas.getLength()*k,seg,True)
    p=paint(e.get('color','#c84a35'),a,stroke=e.get('w',1.6)*u)
    if e.get('dash'): p.setPathEffect(skia.DashPathEffect.Make([4*u,3*u],0))
    c.drawPath(seg,p)

# widget scale (measured: reference widgets vs. base drawing units); anchor = element (x,y) or a corner
KSCALE={'phone':1.9,'paper':2.0,'bubble':1.75,'tag':1.45,'stamp':1.6,'book':1.9,'glass':2.0,'tower':1.6,'plane':1.6,'quotecard':1.75,
        'formula':1.5,'infocard':1.85,'cite':1.5,'menu':1.6,'caption':1.3,'coins':1.6}
ANCHOR={'infocard':(8,10),'menu':(8,10),'cite':(1000,20)}
def scaled(fn,name):
    def w(ctx,e,t,frame):
        k=e.get('k',KSCALE.get(name,1.)); 
        if k==1: return fn(ctx,e,t,frame)
        u=U(ctx); ax,ay=ANCHOR.get(name,(e.get('x',512),e.get('y',288)))
        if name=='formula': ax,ay=e['box'][0]+e['box'][2]/2,e['box'][1]+e['box'][3]/2
        if e.get('move'):
            mv=e['move']; mk=ease_in_out_cubic(prog(t,mv[0],.8)); ax,ay=lerp(e['x'],mv[1],mk),lerp(e['y'],mv[2],mk)
        c=ctx.c; c.save(); c.translate(ax*u,ay*u); c.scale(k,k); c.translate(-ax*u,-ay*u); fn(ctx,e,t,frame); c.restore()
    return w
EXTRA=dict(subtitle=subtitle,infocard=infocard,cite=cite,figure=figure,crowd=crowd,bubble=bubble,tag=tag,paper=paper,stamp=stamp,bars=bars,
           phone=phone,linkline=linkline,titlecard=titlecard,textbox=textbox,quotecard=quotecard,glass=glass,formula=formula,tower=tower,
           plane=plane,book=book,menu=menu,caption=caption,coins=coins,curve=curve)
EXTRA={k:(scaled(v,k) if k in KSCALE else v) for k,v in EXTRA.items()}

def draw(ctx,t,frame,S):
    cur=None
    for sc in S['scenes']:
        if sc['t0']-1e-6<=t<sc['t1']: cur=sc; break
    if cur:
        bg(ctx,cur,t,frame); draw_elements(ctx,cur.get('elements',[]),t,frame,EXTRA)
        # scene cross-fade from/to black (the reference uses ~0.3s dips)
        fi,fo=cur.get('fade_in',.3),cur.get('fade_out',.3); dk=max(1-prog(t,cur['t0'],fi) if fi else 0,prog(t,cur['t1']-fo,fo) if fo else 0)
        if dk>0: ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint('#08080b',dk))
    draw_elements(ctx,[e for e in S.get('overlays',[])],t,frame,EXTRA)
    for sb in S.get('subtitles',[]):
        if sb['t0']<=t<=sb['t1']: subtitle(ctx,sb,t,frame)
    grain(ctx.c,ctx.W,ctx.H,frame,.04,12)
