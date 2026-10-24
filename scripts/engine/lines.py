"""Glowing line-art primitives shared by line-based styles (golden-fractal, white-line-doodle, starry graph ...).
All coordinates in design units (1024-wide); caller passes u=W/1024."""
import math, random, numpy as np, skia
from .core import hexc, paint, lerp, prog, ease_in_out_cubic, ease_out_cubic, blurred_layer

def path_from(pts,u,k=1.0):
    """polyline -> skia.Path truncated to fraction k of its arc length"""
    P=np.asarray(pts,float)
    if len(P)<2 or k<=0: return None,None
    seg=np.hypot(*np.diff(P,axis=0).T); L=seg.sum(); target=L*min(1,k); acc=0
    p=skia.Path(); p.moveTo(P[0,0]*u,P[0,1]*u); tip=P[0]
    for i,s in enumerate(seg):
        if acc+s>=target:
            f=(target-acc)/max(s,1e-9); tip=P[i]+(P[i+1]-P[i])*f; p.lineTo(tip[0]*u,tip[1]*u); break
        p.lineTo(P[i+1,0]*u,P[i+1,1]*u); acc+=s; tip=P[i+1]
    return p,tip
def glow_path(c,path,u,col='#f0d9a8',a=1.,w=2.,glow=10.,core='#fff6e0'):
    if path is None or a<=0: return
    c.drawPath(path,paint(col,a*.35,stroke=w*4*u,blur=glow*u))
    c.drawPath(path,paint(col,a*.8,stroke=w*1.6*u,blur=1.2*u))
    c.drawPath(path,paint(core,a,stroke=w*.7*u))
def glow_node(c,x,y,u,r=5,a=1.,col='#ffe6b0',halo=5):
    if a<=0: return
    sh=skia.GradientShader.MakeRadial((x*u,y*u),r*halo*u,[hexc(col,.55*a),hexc(col,0)]); p=skia.Paint(AntiAlias=True); p.setShader(sh); c.drawCircle(x*u,y*u,r*halo*u,p)
    c.drawCircle(x*u,y*u,r*u,paint('#fffaf0',a))
def bezier(p0,p1,p2,n=40):
    t=np.linspace(0,1,n)[:,None]; p0,p1,p2=map(np.asarray,(p0,p1,p2))
    return (1-t)**2*p0+2*(1-t)*t*p1+t**2*p2
def curve_to(a,b,bend=.3,n=40):
    """quadratic curve from a to b bending sideways by `bend` × length"""
    a,b=np.asarray(a,float),np.asarray(b,float); m=(a+b)/2; d=b-a; nrm=np.array([-d[1],d[0]])
    return bezier(a,m+nrm*bend,b,n)
def crack_net(seed,box,n_seeds=6,depth=7,step=(55,110),branch=.45,wander=.3):
    """procedural crack / root network: angular walkers that fork; returns list of (polyline, birth_order 0..1)"""
    rng=random.Random(seed); x0,y0,x1,y1=box; out=[]; Q=[]
    for i in range(n_seeds): Q.append(((rng.uniform(x0,x1),rng.uniform(y0,y1)),rng.uniform(0,6.283),0))
    while Q and len(out)<1100:
        (x,y),ang,d=Q.pop(0); pts=[(x,y)]
        for k in range(rng.randint(2,5)):
            # snap-ish angular turns for geometric cracked-glass feel
            ang+=rng.choice([-1,1])*rng.uniform(.35,1.1)+rng.uniform(-wander,wander)
            L=rng.uniform(*step)*(1.15-.08*d)
            x+=math.cos(ang)*L; y+=math.sin(ang)*L; pts.append((x,y))
            if not (x0-100<x<x1+100 and y0-100<y<y1+100): break
        out.append((pts,d))
        if d<depth:
            Q.append(((x,y),ang+rng.uniform(-.2,.2),d+1))
            if rng.random()<branch: Q.append(((pts[len(pts)//2] if len(pts)>2 else (x,y)),ang+rng.choice([-1,1])*rng.uniform(.7,1.4),d+1))
            if d<2 and rng.random()<.4: Q.append(((x,y),ang+math.pi+rng.uniform(-.3,.3),d+1))
    md=max(1,max((d for _,d in out),default=1)); return [(p,d/md) for p,d in out]
def draw_net(c,net,u,k,col='#d8c49a',a=1.,w=1.,glow=4.):
    """grow network to fraction k; early-order paths drawn as thicker glowing spines"""
    if a<=0 or k<=0: return
    spines=skia.Path(); fine=skia.Path()
    for pts,o in net:
        if o>k: continue
        f=min(1,(k-o)*5+.0001); sub,_=path_from(pts,1,f)
        if not sub: continue
        (spines if o<.35 else fine).addPath(sub)
    m=skia.Matrix.Scale(u,u); spines.transform(m); fine.transform(m)
    if not fine.isEmpty():
        c.drawPath(fine,paint(col,a*.22,stroke=w*2.2*u,blur=glow*.8*u))
        c.drawPath(fine,paint(col,a*.7,stroke=w*.7*u))
    if not spines.isEmpty():
        c.drawPath(spines,paint(col,a*.4,stroke=w*6*u,blur=glow*2*u))
        c.drawPath(spines,paint(col,a*.85,stroke=w*2.2*u,blur=1.4*u))
        c.drawPath(spines,paint('#fff8e8',a,stroke=w*.9*u))
def rope(c,p0,p1,u,t,k=1.,col='#f0d9a8',a=1.,amp=6,turns=40,strands=3,w=1.4):
    """twisted multi-strand rope from p0 to p1 (ref: 88s 'life rope')"""
    p0,p1=np.asarray(p0,float),np.asarray(p1,float); d=p1-p0; L=np.hypot(*d); n=np.array([-d[1],d[0]])/L
    s=np.linspace(0,k,int(400*k)+2)[:,None]
    for j in range(strands):
        ph=j*2*math.pi/strands+t*1.5
        pts=p0+d*s+n*(amp*np.sin(s*turns*2*math.pi+ph))
        path,_=path_from(pts,u,1); glow_path(c,path,u,col,a*.8,w,6)
