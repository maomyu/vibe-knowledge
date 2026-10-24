"""#9 白线涂鸦寓言 (white-line-doodle) — ref 7692319542446873700《虚无主义？然后呢》1920x1080 165.7s. Topic-agnostic.
Near-black stage (#030406) with faint dust stars; everything drawn as 'constellation line art': thin white strokes with bright
dots strung along them (twinkling). Persistent corner tags (top-left topic, top-right boxed channel). Bottom serif caption, [bold]
keywords brighter. Props: ground line, stick figures (stand/sit/walk/fall, crowd rows), dotted glyph titles (assemble from scatter),
ferris/mandala wheel with rays + ladder towers, floating shard constellations, prop library (camel, book, bowl, sign, box, tree,
house, bag), word-chain snake, spotlight cone, waves, rising sun (warm), photo-ish grey crowd intro. Scene `invert` gives the
white-paper flashback look. Design space 1024x576."""
import math, random, numpy as np, skia
from engine.core import *
from engine.layers import draw_elements, U, wrap_markup, glyph_points
import engine.richness as RICH

WHITE='#e4e4df'; DIM='#7b7a7a'; WARM='#ab8d63'
def ease_in_cubic(x): return x*x*x
def prepare(S): pass
def env(e,t,fi=.5,fo=.5): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def SER(s,w=500): return font('serif-vf',s,w)
def kfi(keys,t):
    if not isinstance(keys,list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]

# ---------- constellation stroke primitive ----------
def dotpath(c,pts,u,a,t,seed=0,col=WHITE,lw=.8,gap=5,dot=1.05,closed=False,k=1.0,line_a=.65):
    """polyline in design coords drawn as faint line + dots every `gap`; k = draw-on fraction"""
    if len(pts)<2 or a<=0: return
    P=[tuple(p) for p in pts]+([tuple(pts[0])] if closed else [])
    seg=[math.dist(P[i],P[i+1]) for i in range(len(P)-1)]; L=sum(seg); lim=L*k
    pa=skia.Path(); pa.moveTo(P[0][0]*u,P[0][1]*u); acc=0; r=random.Random(seed); dots=[]; nxt=0
    for i,s in enumerate(seg):
        if acc>=lim: break
        x0,y0=P[i]; x1,y1=P[i+1]; f=min(1,(lim-acc)/s) if s else 1
        pa.lineTo((x0+(x1-x0)*f)*u,(y0+(y1-y0)*f)*u)
        while nxt<=acc+s*f:
            q=(nxt-acc)/s if s else 0; dots.append((x0+(x1-x0)*q,y0+(y1-y0)*q)); nxt+=gap*r.uniform(.7,1.4)
        acc+=s
    c.drawPath(pa,paint(col,a*line_a,stroke=lw*u))
    for j,(x,y) in enumerate(dots):
        tw=.55+.45*math.sin(t*r.uniform(1,3)+j*1.7); rr=dot*r.uniform(.6,1.4)
        c.drawCircle(x*u,y*u,rr*u,paint(col,a*tw))
        if r.random()<.12: c.drawCircle(x*u,y*u,rr*3*u,paint(col,a*.25*tw,blur=2*u))
def circ(cx,cy,r,n=28,a0=0,a1=2*math.pi): return [(cx+r*math.cos(a0+(a1-a0)*i/n),cy+r*math.sin(a0+(a1-a0)*i/n)) for i in range(n+1)]
def ell(cx,cy,rx,ry,n=30): return [(cx+rx*math.cos(2*math.pi*i/n),cy+ry*math.sin(2*math.pi*i/n)) for i in range(n+1)]

# ---------- chrome ----------
def corner(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx)
    # dark chip behind left tag so it stays readable on inverted (light) scenes
    left=e.get('left','')
    if left:
        fl=SER(10*u,700); lw=fl.measureText(left)
        rrect(c,10*u,12*u,lw+16*u,18*u,4*u,fill='#050508',a=a*.55)
        draw_text(c,left,18*u,26*u,fl,WHITE,a*.85,'left')
    if e.get('right'):
        f=SER(6.5*u,500); w=f.measureText(e['right'])/u+10
        # filled near-black chip + stroke so invert doesn't wash it out
        rrect(c,(1006-w)*u,15*u,w*u,13*u,3*u,fill='#050508',stroke=DIM,a=a*.7,sw=.6*u)
        draw_text(c,e['right'],(1001)*u,24.5*u,f,WHITE,a*.75,'right')
    if e.get('sub'): draw_text(c,e['sub'],1006*u,40*u,SER(6*u,500),DIM,a*.6,'right')
def caption(ctx,e,t,frame):
    """bottom serif caption; [word] = bold bright.
    Always draws a near-black rounded pill behind text so captions stay readable
    on both dark stage and scene `invert` (light paper) — overlays sit outside
    the invert saveLayer, so white-on-light would otherwise vanish.
    """
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c; u=U(ctx); f=SER(e.get('size',17)*u,600); fb=SER(e.get('size',17)*u,900)
    # force light text; contrast comes from the dark pill (works under invert too)
    col=e.get('color',WHITE); lines=wrap_markup(e['text'],f,e.get('max_w',800)*u); lh=e.get('lh',24); y=e.get('y',522)-(len(lines)-1)*lh
    parsed=[]; maxw=0.0
    for j,ln in enumerate(lines):
        rs=[];b='';m=0
        for ch in ln:
            if ch=='[': rs.append((b,0)); b=''
            elif ch==']': rs.append((b,1)); b=''
            else: b+=ch
        rs.append((b,0)); tw=sum((fb if m else f).measureText(s) for s,m in rs)
        parsed.append((rs,tw)); maxw=max(maxw,tw)
    if maxw<=0: return
    pad_x,pad_y=16*u,8*u
    cx=e.get('x',512)*u
    # baseline of first line → pill top slightly above glyph top
    top=(y*u)-f.getSize()*0.82-pad_y*0.35
    h=len(lines)*lh*u + pad_y*1.15
    rrect(c,cx-maxw/2-pad_x,top,maxw+2*pad_x,h,9*u,fill='#050508',a=a*0.78)
    # soft outer halo (not a flash) for edge separation on light frames
    rrect(c,cx-maxw/2-pad_x,top,maxw+2*pad_x,h,9*u,stroke='#000000',a=a*0.45,sw=1.4*u,blur=2.5*u)
    for j,(rs,tw) in enumerate(parsed):
        x=cx-tw/2
        for s,m in rs:
            ff=fb if m else f; c.drawString(s,x,(y+j*lh)*u,ff,paint(col,a)); x+=ff.measureText(s)
def title(ctx,e,t,frame):
    """solid big title (brush-ish serif) with optional glow/blur-in"""
    a=env(e,t,.4,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); k=ease_out_cubic(prog(t,e['t0'],.6)); f=SER(e.get('size',48)*u,e.get('weight',800))
    col=e.get('color',WHITE); bl=(1-k)*8*u
    w=f.measureText(e['text']); c.drawString(e['text'],e.get('x',512)*u-w/2,e.get('y',120)*u,f,paint(col,a*.35,blur=6*u))
    p=paint(col,a*k*e.get('title_a',0.72),blur=bl if bl>.3 else 0); c.drawString(e['text'],e.get('x',512)*u-w/2,e.get('y',120)*u,f,p)
_GP={}
def dottext(ctx,e,t,frame):
    """title made of star dots + short links; assembles from scatter over `build` s, optional disperse at t1"""
    a=env(e,t,.3,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); sz=e.get('size',60); key=(e['text'],sz,e.get('vertical',False))
    if key not in _GP:
        pts,w,h=None,0,0
        g=glyph_points(e['text'],'serif-vf',sz*4,500,e.get('vertical',False),e.get('n',260))
        pts=np.array(g[0] if isinstance(g,tuple) else g,dtype=float); pts=pts/4.0; pts-=pts.mean(0); _GP[key]=pts
    P=_GP[key]; r=np.random.RandomState(len(e['text'])); S0=r.uniform(-1,1,P.shape)*[500,300]
    k=ease_in_out_cubic(prog(t,e['t0'],e.get('build',1.6))); kd=ease_in_cubic(prog(t,e['t1']-e.get('disperse',0),e.get('disperse',0)+1e-6)) if e.get('disperse') else 0
    Q=S0*(1-k)+P*k; Q=Q+S0*kd*.6; x,y=e.get('x',512),e.get('y',120); col=e.get('color',WHITE)
    if k>.5:
        pa=skia.Path()
        for i in range(0,len(P)-1):
            if np.linalg.norm(P[i]-P[i+1])<sz*.12: pa.moveTo((x+Q[i,0])*u,(y+Q[i,1])*u); pa.lineTo((x+Q[i+1,0])*u,(y+Q[i+1,1])*u)
        c.drawPath(pa,paint(col,a*.35*(k-.5)*2*(1-kd),stroke=.5*u))
    for i,(qx,qy) in enumerate(Q):
        tw=.6+.4*math.sin(t*2+i); c.drawCircle((x+qx)*u,(y+qy)*u,(.8+.5*(i%3==0))*u,paint(col,a*tw*(1-kd*.7)))

# ---------- scenery ----------
def ground(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); y=e.get('y',420); k=ease_in_out_cubic(prog(t,e['t0'],e.get('draw',1.0))); x0,x1=e.get('x0',0),e.get('x1',1024); xm=(x0+x1)/2
    c.drawLine((xm-(xm-x0)*k)*u,y*u,(xm+(x1-xm)*k)*u,y*u,paint(WHITE,a*.8,stroke=1.4*u))
    c.drawLine((xm-(xm-x0)*k)*u,y*u,(xm+(x1-xm)*k)*u,y*u,paint(WHITE,a*.3,stroke=3*u,blur=3*u))
    if e.get('sparkle'):
        r=random.Random(3)
        for i in range(int(e['sparkle'])):
            xx=r.uniform(x0,x1); c.drawCircle(xx*u,(y+r.uniform(-4,14))*u,r.uniform(.4,1.1)*u,paint(WHITE,a*(.3+.3*math.sin(t*2+i))))
def _fig(c,u,x,y,h,pose,t,a,seed,col,filled=False):
    hr=h*.12; s=h/60
    if pose=='sit':
        body=ell(x,y-h*.28,h*.17,h*.24); head=circ(x,y-h*.62,hr*1.3)
    else:
        sw=math.sin(t*6+seed)*(1 if pose=='walk' else 0)
        head=circ(x,y-h+hr,hr)
        body=[(x-h*.09,y-h+hr*2.3),(x+h*.09,y-h+hr*2.3),(x+h*.1,y-h*.45),(x+h*.06+sw*h*.08,y),(x-h*.06-sw*h*.08,y),(x-h*.1,y-h*.45),(x-h*.09,y-h+hr*2.3)]
        if pose=='fall':
            cx,cy=x,y-h*.1; body=[(cx+(py-cy),cy-(px-cx)*.4) for px,py in body]; head=[(cx+(py-cy),cy-(px-cx)*.4) for px,py in head]
    if filled:
        for poly in (body,head):
            pa=skia.Path(); pa.addPoly([skia.Point(px*u,py*u) for px,py in poly],True); c.drawPath(pa,paint(col,a))
        return
    dotpath(c,head,u,a,t,seed,col,gap=3.5); dotpath(c,body,u,a,t,seed+1,col,gap=3.5)
def figure(ctx,e,t,frame):
    """stick figure: x(keys ok),y=ground,h,pose stand|walk|sit|fall, filled bool"""
    a=env(e,t,.4,.4)
    if a<=0: return
    _fig(ctx.c,U(ctx),kfi(e.get('x',512),t),e.get('y',420),e.get('h',60),e.get('pose','stand'),t,a,e.get('seed',1),e.get('color',WHITE),e.get('filled',False))
def crowd(ctx,e,t,frame):
    """row of figures between x0..x1 (skip gap [g0,g1]); hs height jitter; pop-in stagger"""
    a=env(e,t,.4,.4)
    if a<=0: return
    r=random.Random(e.get('seed',2)); n=e.get('n',12); x0,x1=e.get('x0',60),e.get('x1',964); g=e.get('gap')
    for i in range(n):
        x=x0+(x1-x0)*(i+.5)/n
        if g and g[0]<x<g[1]: continue
        k=prog(t,e['t0']+i*e.get('stagger',.05),.4); h=e.get('h',40)*r.uniform(.85,1.1)
        _fig(ctx.c,U(ctx),x,e.get('y',420)+e.get('dy',0)*r.uniform(-1,1),h,e.get('pose','stand'),t,a*k,i,e.get('color',WHITE),e.get('filled',False))
def wheel(ctx,e,t,frame):
    """glowing mandala wheel with petals, rotating; rays down; ladder towers; orbit ring optional"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,R=e.get('x',512),e.get('y',150),e.get('r',110); rot=t*e.get('spin',.15); k=ease_out_cubic(prog(t,e['t0'],1.5))
    g=skia.GradientShader.MakeRadial((x*u,y*u),R*.9*u,[skia.Color4f(1,1,1,.9*a).toColor(),skia.Color4f(1,1,1,.15*a).toColor(),skia.Color4f(1,1,1,0).toColor()],[0,.25,1])
    q=skia.Paint(); q.setShader(g); c.drawCircle(x*u,y*u,R*u,q)
    if e.get('rays',True):
        for i in range(-3,4):
            pa=skia.Path(); ang=math.pi/2+i*.28; pa.moveTo(x*u,y*u); pa.lineTo((x+math.cos(ang-.05)*R*3)*u,(y+math.sin(ang-.05)*R*3)*u); pa.lineTo((x+math.cos(ang+.05)*R*3)*u,(y+math.sin(ang+.05)*R*3)*u)
            c.drawPath(pa,paint(WHITE,a*.06,blur=4*u))
    dotpath(c,circ(x,y,R,64),u,a,t,1,k=k,gap=4); dotpath(c,circ(x,y,R*.62,48),u,a*.8,t,2,k=k,gap=4)
    for i in range(12):
        an=rot+i*math.pi/6; cx,cy=x+math.cos(an)*R*.62,y+math.sin(an)*R*.62
        dotpath(c,circ(cx,cy,R*.38,24),u,a*.55,t,10+i,k=k,gap=5,line_a=.3); c.drawCircle((x+math.cos(an)*R)*u,(y+math.sin(an)*R)*u,2*u,paint(WHITE,a*k))
    if e.get('towers',True):
        gy=e.get('ground',420)
        for tx in (x-R*1.0,x+R*1.0):
            for j in (-10,10): dotpath(c,[(tx+j,y),(tx+j,gy)],u,a,t,int(tx)+j,gap=4)
            for yy in np.arange(y+10,gy,20): c.drawLine((tx-10)*u,yy*u,(tx+10)*u,yy*u,paint(WHITE,a*.6,stroke=.7*u))
        dotpath(c,circ(x,y,R*1.0+0,40,math.pi,2*math.pi),u,a*.8,t,7,gap=4)
    if e.get('orbit'):
        dotpath(c,ell(x,y,R*2.3,R*.45,60),u,a*.6,t,9,gap=6,line_a=.3)
def shards(ctx,e,t,frame):
    """floating constellation fragments (tri/rect/arc) drifting outward from centre"""
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); r=random.Random(e.get('seed',4)); x0,y0=e.get('x',512),e.get('y',280); tt=t-e['t0']
    for i in range(e.get('n',26)):
        an=r.uniform(0,6.28); d0=r.uniform(40,420)+tt*e.get('speed',8); cx,cy=x0+math.cos(an)*d0*1.3,y0+math.sin(an)*d0*.8; s=r.uniform(14,34); ro=r.uniform(0,6)+tt*r.uniform(-.3,.3)
        kind=r.choice(['tri','rect','arc','line'])
        if kind=='tri': P=[(cx+s*math.cos(ro+j*2.09),cy+s*math.sin(ro+j*2.09)) for j in range(3)]; cl=True
        elif kind=='rect': P=[(cx+s*math.cos(ro+j*1.57+.6)*(1.3 if j%2 else 1),cy+s*math.sin(ro+j*1.57+.6)) for j in range(4)]; cl=True
        elif kind=='arc': P=circ(cx,cy,s,10,ro,ro+2); cl=False
        else: P=[(cx,cy),(cx+s*1.5*math.cos(ro),cy+s*1.5*math.sin(ro))]; cl=False
        dotpath(c,P,u,a,t,i,closed=cl,gap=4)
PROPS={
 'camel':[[(-72,-38),(-60,-55),(-35,-72),(-10,-70),(10,-55),(28,-42),(45,-50),(52,-80),(62,-94),(78,-92),(84,-85),(70,-82),(64,-60),(60,-36),(50,-20),(42,-18),(44,0),(36,0),(30,-18),(-40,-18),(-38,0),(-46,0),(-52,-20),(-66,-26),(-72,-38)],[(-74,-36),(-80,-20)],[(74,-89),(75,-88)]],
 'book':[[(-40,-30),(0,-25),(40,-30),(40,20),(0,25),(-40,20),(-40,-30)],[(0,-25),(0,25)],[(-32,-15),(-8,-12)],[(-32,-5),(-8,-2)],[(8,-12),(32,-15)],[(8,-2),(32,-5)]],
 'tablet':[[(-22,-30),(22,-30),(22,30),(-22,30),(-22,-30)],[(-14,-20),(14,-20),(14,-8),(-14,-8),(-14,-20)],[(-14,0),(14,0)],[(-14,8),(14,8)],[(-14,16),(6,16)]],
 'bowl':[[(-30,-8),(30,-8),(20,12),(-20,12),(-30,-8)],[(-10,-14),(-6,-26),(-10,-38)],[(2,-14),(6,-28),(2,-40)],[(20,-6),(44,-30)]],
 'sign':[[(0,0),(0,-50)],[(-20,-50),(20,-50),(20,-75),(-20,-75),(-20,-50)]],
 'box':[[(-20,0),(20,0),(20,-34),(-20,-34),(-20,0)],[(-20,-34),(-10,-42),(30,-42),(20,-34)],[(20,0),(30,-8),(30,-42)]],
 'tree':[[(0,0),(0,-30)]]+[circ(0,-48,20,20)],
 'house':[[(-25,0),(-25,-30),(0,-50),(25,-30),(25,0),(-25,0)],[(-6,0),(-6,-16),(6,-16),(6,0)]],
 'bag':[[(-18,0),(18,0),(14,-28),(-14,-28),(-18,0)],[(-7,-28),(-7,-36),(7,-36),(7,-28)]],
 'kite':[[(0,-20),(14,0),(0,26),(-14,0),(0,-20)],[(0,26),(6,44),(-4,60)]],
 'bench':[[(-30,-14),(30,-14)],[(-26,-14),(-26,0)],[(26,-14),(26,0)],[(-30,-24),(30,-24)]],
}
def prop(ctx,e,t,frame):
    """library prop or custom `paths`; x,y = baseline anchor, s scale, flip, draw-on, drift [vx,vy], bob"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); s=e.get('s',1); fl=-1 if e.get('flip') else 1; tt=t-e['t0']
    x=kfi(e.get('x',512),t)+e.get('drift',[0,0])[0]*tt; y=kfi(e.get('y',420),t)+e.get('drift',[0,0])[1]*tt+math.sin(t*1.5)*e.get('bob',0)
    k=ease_in_out_cubic(prog(t,e['t0'],e.get('draw',1.0))); ro=e.get('rot',0)+e.get('spin',0)*tt
    cs,sn=math.cos(ro),math.sin(ro)
    for j,P in enumerate(e.get('paths') or PROPS[e.get('kind','box')]):
        Q=[(x+(px*fl*cs-py*sn)*s,y+(px*fl*sn+py*cs)*s) for px,py in P]; dotpath(c,Q,u,a,t,j+e.get('seed',0),e.get('color',WHITE),k=k,gap=e.get('gap',3.5))
def snake(ctx,e,t,frame):
    """chain of small circled words winding along a sine path (e.g. 'you should' dragon)"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); W_=e.get('words',['应该']); n=e.get('n',22); k=prog(t,e['t0'],e.get('grow',2.0)); x0,y0=e.get('x',300),e.get('y',380); x1,y1=e.get('x1',700),e.get('y1',120)
    f=SER(6*u,600)
    for i in range(int(n*k)):
        q=i/n; x=x0+(x1-x0)*q+math.sin(q*8+t)*30; y=y0+(y1-y0)*q+math.cos(q*6+t*.7)*14; r_=10*(1-q*.5)
        dotpath(c,circ(x,y,r_,14),u,a,t,i,gap=3); draw_text(c,W_[i%len(W_)],x*u,(y+2)*u,f,WHITE,a*.8)
def spotlight(ctx,e,t,frame):
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); x=e.get('x',512); y=e.get('y',420); w0,w1=e.get('w0',20),e.get('w1',90)
    pa=skia.Path(); pa.moveTo((x-w0)*u,0); pa.lineTo((x+w0)*u,0); pa.lineTo((x+w1)*u,y*u); pa.lineTo((x-w1)*u,y*u); pa.close()
    g=skia.GradientShader.MakeLinear([(0,0),(0,y*u)],[hexc(e.get('color','#ffffff'),.05*a),hexc(e.get('color','#ffffff'),.3*a)])
    q=skia.Paint(); q.setShader(g); q.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle,6*u)); c.drawPath(pa,q)
    c.drawOval(skia.Rect.MakeXYWH((x-w1)*u,(y-6)*u,2*w1*u,12*u),paint(e.get('color','#ffffff'),a*.35,blur=4*u))
def waves(ctx,e,t,frame):
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx)
    for j in range(e.get('n',4)):
        y=e.get('y',300)+j*e.get('dy',35); P=[(x,y+math.sin(x/90+t*.6+j)*8) for x in range(0,1030,16)]
        c.drawPath(skia.Path.Polygon([skia.Point(px*u,py*u) for px,py in P],False),paint(WHITE,a*.25,stroke=.6*u))
def sun(ctx,e,t,frame):
    """warm glowing sun rising from horizon y over `rise` s"""
    a=env(e,t,1,.8)
    if a<=0: return
    c=ctx.c; u=U(ctx); x=e.get('x',512); gy=e.get('y',420); R=e.get('r',70); k=ease_out_cubic(prog(t,e['t0'],e.get('rise',4)))
    cy=gy+R*.8-(R*1.3)*k; c.save(); c.clipRect(skia.Rect.MakeLTRB(0,0,ctx.W,gy*u))
    g=skia.GradientShader.MakeRadial((x*u,cy*u),R*4*u,[hexc('#ffe9b8',a),hexc(WARM,.5*a),hexc('#3a2a14',.25*a),hexc('#000000',0)],[0,.2,.5,1])
    q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeLTRB(0,0,ctx.W,gy*u),q); c.drawCircle(x*u,cy*u,R*u,paint('#fff3d6',a))
    c.restore(); c.drawRect(skia.Rect.MakeLTRB(0,gy*u,ctx.W,(gy+40)*u),paint(WARM,a*.12*k,blur=12*u))
def photo(ctx,e,t,frame):
    """grey 'photographic' crowd intro: soft top light, filled grey figures rows (seated audience)"""
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c; u=U(ctx); W,H=ctx.W,ctx.H
    g=skia.GradientShader.MakeRadial((W/2,-H*.1),H*1.1,[hexc('#9a9a98',a),hexc('#3a3a3a',a),hexc('#0c0c0c',a)],[0,.5,1]); q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeWH(W,H),q)
    r=random.Random(e.get('seed',1)); dr=(t-e['t0'])*e.get('pan',6)
    for row in range(3):
        for i in range(9):
            x=(70+i*115+row*40-dr)%1100-40; h=90+row*45
            _fig(c,u,x,400+row*70,h,'stand',t,a*(.5+row*.2),i,['#bdbdbb','#9a9a98','#e0e0dc'][row],True)
    c.drawRect(skia.Rect.MakeWH(W,H),paint('#000000',a*.15))
def curtain(ctx,e,t,frame):
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c; u=U(ctx)
    for i in range(0,1024,7): c.drawLine(i*u,0,i*u,ctx.H,paint('#3a3a3c',a*(.3+.3*math.sin(i*.37)),stroke=3*u))



def spark(ctx,e,t,frame):
    """Dense motes + orbs + bright sweep so density longest_static → 0s."""
    a=env(e,t,.15,.15)
    if a<=0: return
    import math, random
    col=e.get('color','#e8d8a8')
    n=e.get('n',140)
    RICH.motes(ctx.c,ctx.W,ctx.H,t,n=n,color=col,a=a*e.get('a_mul',.85),seed=e.get('seed',11),speed=e.get('speed',3.5),blur_k=.45)
    u=ctx.W/1024.; c=ctx.c; R=random.Random(e.get('seed',11)+3); H=ctx.H
    for i in range(e.get('orbs',18)):
        x=(R.uniform(0,1024)+t*R.uniform(60,160)*e.get('speed',3.5))%1024
        y=(R.uniform(0,576)-t*R.uniform(30,100)*e.get('speed',3.5))%576
        s=R.uniform(3.0,8.0)
        aa=a*R.uniform(.18,.45)*(.5+.5*math.sin(t*4.2+i))
        c.drawCircle(x*u,y*(H/576.),s*u,paint(col,aa,blur=s*.35*u))
    # bright sweep bar — guarantees per-second frame change even on near-black frames
    if e.get('sweep', True):
        sx=(t*220 + e.get('seed',11)*37)%(1024+80)-40
        for k in range(5):
            xx=(sx+k*14)*u
            c.drawCircle(xx, (180+40*math.sin(t*2+k))*(H/576.), 5.5*u, paint(col, a*0.55*(1-k*.12), blur=3*u))
            c.drawCircle(xx, (400+30*math.cos(t*1.7+k))*(H/576.), 4.0*u, paint(col, a*0.4*(1-k*.1), blur=2.5*u))

EXTRA=dict(spark=spark,corner=corner,caption=caption,title=title,dottext=dottext,ground=ground,figure=figure,crowd=crowd,wheel=wheel,shards=shards,prop=prop,
           snake=snake,spotlight=spotlight,waves=waves,sun=sun,photo=photo,curtain=curtain)

INV=skia.ColorFilters.Matrix([-1,0,0,0,1, 0,-1,0,0,1, 0,0,-1,0,1, 0,0,0,1,0])

def _render_sc(ctx,sc,t,frame):
    # soft radial stage bg each scene
    c=ctx.c; u=U(ctx)
    g=skia.GradientShader.MakeRadial((ctx.W/2,ctx.H*.45),ctx.W*.5,[hexc('#111113'),hexc('#030406')]); q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),q)
    if sc.get('invert'):
        p=skia.Paint(); p.setColorFilter(INV); c.saveLayer(None,p); c.clear(hexc('#030406'))
        draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA); c.restore()
    else:
        draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)

def draw(ctx,t,frame,S):
    ctx.beats=S.get('beats',[])
    c=ctx.c; c.clear(hexc(S.get('bg','#030406')))
    RICH.compose_scenes(ctx,S,t,frame,_render_sc,overlays_extra=EXTRA,clear=None,
                        vignette_s=.55,grain_a=.035,band_color='#e4e4df',design_size=(1024,576))
    if S.get('beat_punch',False) and getattr(ctx,'beats',None):
        RICH.beat_punch(ctx.c,ctx.W,ctx.H,t,ctx.beats,a=min(S.get('punch_a',.05),.05),color=S.get('punch_col','#e4e4df'),window=.06)
