"""Tiny code-only 3D layer on skia: pinhole camera, flat-shaded meshes (cubes/boxes/extruded glyph slabs),
spheres (analytic shading + texture), cylinders (bamboo), depth sort + exponential fog. Deterministic, no GPU.
Coordinates: world Y up, camera looks along -Z by default. Units arbitrary (we use ~1 = 1 glyph)."""
import math, numpy as np, skia
from .core import hexc, paint, font, draw_text

def _norm(v): v=np.asarray(v,float); n=np.linalg.norm(v); return v/n if n else v
class Camera:
    def __init__(s,pos=(0,0,10),target=(0,0,0),fov=40,W=1024,H=576,up=(0,1,0)):
        s.pos=np.array(pos,float); s.target=np.array(target,float); s.fov=fov; s.W=W; s.H=H
        f=_norm(s.target-s.pos); r=_norm(np.cross(f,up)); u=np.cross(r,f); s.R=np.stack([r,u,-f]); s.f=H/2/math.tan(math.radians(fov)/2)
    def view(s,P): return (np.asarray(P,float)-s.pos)@s.R.T          # camera space, visible z<0
    def proj(s,P):
        V=s.view(P); z=-V[...,2]; z=np.where(z<1e-3,1e-3,z)
        return np.stack([s.W/2+s.f*V[...,0]/z, s.H/2-s.f*V[...,1]/z],-1), z
def mix(a,b,k):
    A=np.array([int(a[i:i+2],16) for i in (1,3,5)],float); B=np.array([int(b[i:i+2],16) for i in (1,3,5)],float)
    C=A+(B-A)*min(1,max(0,k)); return '#%02x%02x%02x'%tuple(C.astype(int))
def shade(col,n,light=(-.4,.7,.6),amb=.45):
    l=_norm(light); k=amb+(1-amb)*max(0,float(np.dot(_norm(n),l))); return mix('#000000',col,k)
def fogk(z,fog): return 0 if not fog else 1-math.exp(-max(0,z-fog.get('near',0))*fog.get('density',.05))

CUBE_F=[((0,1,2,3),(0,0,-1)),((4,5,6,7),(0,0,1)),((0,1,5,4),(0,-1,0)),((3,2,6,7),(0,1,0)),((0,3,7,4),(-1,0,0)),((1,2,6,5),(1,0,0))]
def rot(rx=0,ry=0,rz=0):
    cx,sx,cy,sy,cz,sz=math.cos(rx),math.sin(rx),math.cos(ry),math.sin(ry),math.cos(rz),math.sin(rz)
    Rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]); Ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]); Rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    return Rz@Ry@Rx
def box_faces(center,size,R=None,col='#e8582f',face_text=None,text_col='#fff8ee',light=(-.4,.7,.6),fog=None,fog_col='#000000',a=1.,cam=None,bevel=.06):
    """returns list of draw ops (depth, fn) for a box; the +Z face carries a glyph (seal tile / glyph cube)"""
    sx,sy,sz=(size,size,size) if np.isscalar(size) else size
    V=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],float)*[sx/2,sy/2,sz/2]
    R=np.eye(3) if R is None else R; Wv=V@R.T+np.asarray(center,float)
    P,z=cam.proj(Wv); ops=[]
    for idx,n in CUBE_F:
        nw=R@np.array(n,float); cen=Wv[list(idx)].mean(0)
        if np.dot(nw,cam.pos-cen)<=0: continue           # back-face cull
        d=float(z[list(idx)].mean()); fk=fogk(d,fog)
        c=mix(shade(col if n!=(0,0,1) else col,nw,light),fog_col,fk)
        pts=[skia.Point(*P[i]) for i in idx]
        def fn(canvas,pts=pts,c=c,n=n,idx=idx,fk=fk):
            path=skia.Path(); path.addPoly(pts,True); canvas.drawPath(path,paint(c,a))
            if n==(0,0,1) and face_text:                   # glyph on front face via homography
                src=[skia.Point(0,0),skia.Point(100,0),skia.Point(100,100),skia.Point(0,100)]
                dst=[pts[3],pts[2],pts[1],pts[0]] if False else [skia.Point(*P[7]),skia.Point(*P[6]),skia.Point(*P[5]),skia.Point(*P[4])]
                m=skia.Matrix(); 
                if m.setPolyToPoly(src,dst):
                    canvas.save(); canvas.concat(m); draw_text(canvas,face_text,50,78,font('serif-vf',76,900),mix(text_col,fog_col,fk),a); canvas.restore()
        ops.append((d,fn))
    return ops
def sphere_op(center,r,cam,col='#d8402a',light=(-.5,.6,.6),tex=None,fog=None,fog_col='#000000',a=1.):
    P,z=cam.proj(np.asarray(center,float)[None]); d=float(z[0]); rr=cam.f*r/d; x,y=P[0]
    fk=fogk(d,fog)
    def fn(canvas):
        l=_norm(light); hx,hy=x-l[0]*rr*.45,y-l[1]*rr*.45
        sh=skia.GradientShader.MakeRadial((hx,hy),rr*1.5,[hexc(mix(mix(col,'#ffffff',.25),fog_col,fk),a),hexc(mix(col,fog_col,fk),a),hexc(mix(mix(col,'#000000',.55),fog_col,fk),a)],[0,.45,1])
        p=skia.Paint(AntiAlias=True); p.setShader(sh); canvas.drawCircle(x,y,rr,p)
        if tex is not None:                                  # bumpy skin: tiled noise texture clipped to disc, multiply
            canvas.save(); pth=skia.Path(); pth.addCircle(x,y,rr); canvas.clipPath(pth,doAntiAlias=True)
            q=skia.Paint(); q.setBlendMode(skia.BlendMode.kMultiply); q.setAlphaf(a*(1-fk))
            canvas.drawImageRect(tex,skia.Rect.MakeXYWH(x-rr,y-rr,2*rr,2*rr),skia.SamplingOptions(skia.FilterMode.kLinear),q); canvas.restore()
    return (d,fn)
def cylinder_op(p0,p1,r,cam,col='#1a1a1a',fog=None,fog_col='#888888',a=1.,nodes=0,node_col=None):
    """vertical-ish cylinder as a shaded quad (bamboo stalk) + node rings"""
    (A,B),z=cam.proj(np.array([p0,p1],float)); d=float(z.mean()); fk=fogk(d,fog)
    w0,w1=cam.f*r/z[0],cam.f*r/z[1]
    def fn(canvas):
        dx,dy=B-A; L=math.hypot(dx,dy) or 1; nx,ny=-dy/L,dx/L
        pts=[skia.Point(A[0]+nx*w0,A[1]+ny*w0),skia.Point(B[0]+nx*w1,B[1]+ny*w1),skia.Point(B[0]-nx*w1,B[1]-ny*w1),skia.Point(A[0]-nx*w0,A[1]-ny*w0)]
        c0=mix(col,fog_col,fk); c1=mix(mix(col,'#ffffff',.07),fog_col,fk)
        sh=skia.GradientShader.MakeLinear([(A[0]+nx*w0,A[1]+ny*w0),(A[0]-nx*w0,A[1]-ny*w0)],[hexc(c0,a),hexc(c1,a),hexc(c0,a)],[0,.35,1])
        p=skia.Paint(AntiAlias=True); p.setShader(sh); path=skia.Path(); path.addPoly(pts,True); canvas.drawPath(path,p)
        for k in range(1,nodes+1):
            u_=k/(nodes+1); X=A+(B-A)*u_; w=w0+(w1-w0)*u_
            canvas.drawLine(X[0]+nx*w*1.15,X[1]+ny*w*1.15,X[0]-nx*w*1.15,X[1]-ny*w*1.15,paint(mix(node_col or mix(col,'#000000',.4),fog_col,fk),a,stroke=max(.6,w*.35)))
    return (d,fn)
def render_ops(canvas,ops):
    for d,fn in sorted(ops,key=lambda o:-o[0]): fn(canvas)
