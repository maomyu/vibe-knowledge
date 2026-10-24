"""#11 宇宙粒子大片 (cosmic-particle-epic) — ref 7693526422271690406《2026诺奖·中微子》1024x576 137.9s. Topic-agnostic.
Deep-space blue-black (#07090e) with stars; gilded serif titles (year kicker + big gold title + sub with keyword colours),
bottom bold serif captions with [blue] / {red} / <gold> keywords. Set pieces drawn in code: particle rain / horizontal speed
lines / warp, fingertip close-up, Earth globe (Natural Earth land), dot-assembled title, glowing star with flare + nebula
cloud + travelling beam, sonar ring with depth ticks and counter, rotating wireframe cube with sensor strings, falling red
streaks + counter, spectral neon columns, spiral galaxy, aurora night horizon with silhouette, ice-blue depth plane with
hanging string + glow + big year. Design space 1024x576.
v3 RICHNESS: tin (flash/zoom/wipe/iris), denser particle rain, camera drift, chapter. See RICHNESS_STANDARD.md."""
import math, random, os, importlib.util, numpy as np, skia
from engine.core import *
from engine.layers import draw_elements, U, wrap_markup
from engine import richness as RICH
from engine.proc import fbm, to_img

GOLD='#f0c060'; BLUE='#6ec0ff'; RED='#ff5a4a'; WHITE='#eef2f6'; GREY='#8a96a2'
def ease_in_cubic(x): return x*x*x
def prepare(S): pass
def env(e,t,fi=.5,fo=.5): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def SR(s,w=800): return font('serif-vf',s,w)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def rich(c,ln,x,y,f,a,align='center',col=WHITE):
    rs=[];b='';m=None; M={'[':BLUE,'{':RED,'<':GOLD}
    for ch in ln:
        if ch in '[{<': rs.append((b,m)); b=''; m=M[ch]
        elif ch in ']}>': rs.append((b,m)); b=''; m=None
        else: b+=ch
    rs.append((b,m)); tw=sum(f.measureText(s) for s,_ in rs); x=x-tw/2 if align=='center' else x
    for s,m in rs:
        if m: c.drawString(s,x,y,f,paint(m,a*.5,blur=4))
        c.drawString(s,x,y,f,paint(m or col,a)); x+=f.measureText(s)
_ST={}
def _storm():
    if 'm' not in _ST:
        p=os.path.join(os.path.dirname(__file__),'..','storm-countdown-vertical','template.py'); sp=importlib.util.spec_from_file_location('_stormtpl',p); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); _ST['m']=m; _ST['tex']=m._earth_tex()
    return _ST['tex']

def caption(ctx,e,t,frame):
    a=env(e,t,.25,.25)
    if a<=0: return
    c=ctx.c; u=U(ctx); f=SR(e.get('size',21)*u,800); lines=wrap_markup(e['text'],f,e.get('max_w',860)*u); lh=e.get('lh',30); y=e.get('y',522)-(len(lines)-1)*lh
    for j,l in enumerate(lines): rich(c,l,e.get('x',512)*u,(y+j*lh)*u,f,a,e.get('align','center'))
def title(ctx,e,t,frame):
    """kicker(year, spaced) + big title (gold|silver) + sub; align center/left"""
    a=env(e,t,.6,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',512),e.get('y',90); al=e.get('align','center'); k=ease_out_cubic(prog(t,e['t0'],.9))
    col=GOLD if e.get('style','gold')=='gold' else '#c8d4e0'; f=SR(e.get('size',46)*u,900)
    if e.get('kicker'): draw_text(c,e['kicker'],x*u,(y-e.get('size',46)*.95)*u,SR(12*u,700),col,a*k,al,spacing=6*u)
    w=f.measureText(e['text']); xx=x*u-(w/2 if al=='center' else 0)
    c.drawString(e['text'],xx,y*u,f,paint(col,a*.55*k,blur=10*u))
    g=skia.GradientShader.MakeLinear([(0,(y-e.get('size',46))*u),(0,y*u)],[hexc('#fff2c0' if col==GOLD else '#ffffff',a*k),hexc(col,a*k),hexc('#b07a20' if col==GOLD else '#7a8a9a',a*k)],[0,.5,1])
    q=skia.Paint(AntiAlias=True); q.setShader(g); c.drawString(e['text'],xx,(y+(1-k)*8)*u,f,q)
    if e.get('sub'):
        fs=SR(e.get('sub_size',15)*u,700)
        for j,s in enumerate(e['sub'].split('\n')): rich(c,s,(x if al=='center' else x)*u,(y+max(30,e.get('size',46)*.55)+j*e.get('sub_size',15)*1.5)*u,fs,a*prog(t,e['t0']+.5,.5),al)
    if e.get('foot'): draw_text(c,e['foot'],x*u,(y+max(30,e.get('size',46)*.55)+e.get('sub_size',15)*1.5*len(e.get('sub','').split('\n'))+6)*u,SR(8*u,500),GREY,a,al,spacing=2*u)
def stars(ctx,e,t,frame):
    """starfield + mode: rain (diagonal particle streaks) | hlines (horizontal speed lines) | warp (radial)"""
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); r=random.Random(e.get('seed',1)); m=e.get('mode')
    for i in range(e.get('n',220)): c.drawCircle(r.uniform(0,1024)*u,r.uniform(0,576)*u,r.uniform(.3,1.1)*u,paint('#ffffff',a*r.uniform(.15,.7)*(.7+.3*math.sin(t*2+i))))
    if m=='rain':
        for i in range(e.get('streaks',60)):
            sp=r.uniform(300,600); ph=r.uniform(0,1); L=r.uniform(20,60); p=((t*sp/700+ph)%1.2)
            x=r.uniform(-200,1024)+p*300; y=-60+p*700
            c.drawLine(x*u,y*u,(x-L*.45)*u,(y-L)*u,paint('#cfe0ff',a*.5,stroke=.8*u))
    elif m=='hlines':
        for i in range(e.get('streaks',80)):
            y=r.uniform(0,576); x=(r.uniform(0,1300)-t*r.uniform(200,500))%1300-150; L=r.uniform(40,200)
            c.drawLine(x*u,y*u,(x+L)*u,y*u,paint('#9ab0d0',a*r.uniform(.1,.4),stroke=.7*u))
    elif m=='warp':
        for i in range(e.get('streaks',120)):
            an=r.uniform(0,6.28); d=((t*r.uniform(.2,.5)+r.random())%1); d0=40+d**2*700; L=10+d*80
            c.drawLine((512+math.cos(an)*d0)*u,(288+math.sin(an)*d0)*u,(512+math.cos(an)*(d0+L))*u,(288+math.sin(an)*(d0+L))*u,paint('#d0e0ff',a*d,stroke=.8*u))
def finger(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',512),e.get('y',60); w,h=e.get('w',200),e.get('h',560)
    g=skia.GradientShader.MakeLinear([((x-w/2)*u,0),((x+w/2)*u,0)],[hexc('#4a2a1e',a),hexc('#9a6a52',a),hexc('#5a3424',a)],[0,.45,1]); q=skia.Paint(AntiAlias=True); q.setShader(g)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((x-w/2)*u,y*u,w*u,h*u),w/2*u,w/2*u),q)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((x-w*.32)*u,(y+30)*u,w*.64*u,h*.35*u),w*.25*u,w*.25*u),paint('#c8a8a0',a*.55))
    s=e.get('box',70); bx,by=x-s/2,y+70
    for i in range(0,int(s*4),8):
        q_=i/s; px,py=(bx+min(i,s),by) if i<s else (bx+s,by+i-s) if i<2*s else (bx+s-(i-2*s),by+s) if i<3*s else (bx,by+s-(i-3*s))
        c.drawRect(skia.Rect.MakeXYWH(px*u,py*u,3*u,1.2*u),paint('#ffffff',a*.8))
    if e.get('label'): draw_text(c,e['label'],(bx+s+8)*u,(by+6)*u,SR(9*u,600),WHITE,a,'left')
def globe(ctx,e,t,frame):
    """day-blue Earth from Natural Earth land mask; blue rim; optional marker [lon,lat,label]"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); cx,cy,R=e.get('x',512),e.get('y',288),kfi(e.get('r',120),t); land,_=_storm()
    N=max(64,min(int(2*R*u),640)); ys,xs=np.mgrid[-1:1:N*1j,-1:1:N*1j]; m=xs**2+ys**2<=1; z=np.sqrt(np.clip(1-xs**2-ys**2,0,1))
    tilt=math.radians(e.get('tilt',20)); yy=ys*math.cos(tilt)-z*math.sin(tilt); zz=ys*math.sin(tilt)+z*math.cos(tilt)
    lat=np.degrees(np.arcsin(np.clip(-yy,-1,1))); lon=(np.degrees(np.arctan2(xs,zz))+180+(t-e['t0'])*e.get('spin',4)+e.get('lon0',0))%360
    L=land[((90-lat)/180*(land.shape[0]-1)).astype(int),(lon/360*(land.shape[1]-1)).astype(int)]
    sh=np.clip(.35+.75*(-.4*xs-.3*ys+.6*z),0,1.2)[...,None]
    img=np.zeros((N,N,4)); img[...,:3]=np.where(L[...,None],np.array([70,100,120]),np.array([16,40,80]))*sh
    rim=np.clip((1-z)**2.5,0,1); img[...,:3]+=np.array([90,150,240])*rim[...,None]; img[...,3]=m*255; img[...,:3]=np.clip(img[...,:3],0,255)
    c.drawCircle(cx*u,cy*u,R*1.08*u,paint('#3a7ae0',a*.4,blur=18*u))
    p=skia.Paint(); p.setAlphaf(a); c.drawImageRect(to_img(img),skia.Rect.MakeXYWH((cx-R)*u,(cy-R)*u,2*R*u,2*R*u),skia.SamplingOptions(skia.FilterMode.kLinear),p)
    c.drawCircle(cx*u,cy*u,R*u,paint('#a0d0ff',a*.8,stroke=1.2*u))
    if e.get('marker'):
        mx,my,lab=e['marker']; c.drawCircle(mx*u,my*u,4*u,paint(GOLD,a,blur=1*u)); c.drawCircle(mx*u,my*u,12*u,paint(GOLD,a*.3,blur=6*u))
        if lab: draw_text(c,lab,(mx+16)*u,(my+5)*u,SR(11*u,700),WHITE,a,'left')
def dottext(ctx,e,t,frame):
    a=env(e,t,.4,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); key=(e['text'],e.get('size',110))
    if key not in _ST: P,_,_=glyph_points(e['text'],'serif-vf',e.get('size',110)*3,900,False,e.get('n',1600)); P=np.array(P)/3; P-=P.mean(0); _ST[key]=P
    P=_ST[key]; r=np.random.RandomState(3); S0=r.uniform(-1,1,P.shape)*[600,400]; k=ease_in_out_cubic(prog(t,e['t0'],e.get('build',1.5))); kd=ease_in_cubic(prog(t,e['t1']-e.get('disperse',.4),e.get('disperse',.4)))
    Q=S0*(1-k)+P*k+S0*kd*.5; x,y=e.get('x',512),e.get('y',288)
    for i,(qx,qy) in enumerate(Q): c.drawCircle((x+qx)*u,(y+qy)*u,(.9+.6*(i%4==0))*u,paint('#e8f0ff',a*(1-kd)*(.6+.4*math.sin(t*3+i))))
def star(ctx,e,t,frame):
    """glowing star: orange halo, dark lensing ring, vertical+horizontal flare"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,R=e.get('x',140),e.get('y',260),e.get('r',40); col=e.get('col','#ff9a40'); pul=1+.05*math.sin(t*3)
    c.drawCircle(x*u,y*u,R*3*pul*u,paint(col,a*.35,blur=R*1.5*u)); c.drawCircle(x*u,y*u,R*u,paint(col,a*.8,blur=R*.4*u))
    c.drawCircle(x*u,y*u,R*.45*u,paint('#000000',a*.85)); c.drawCircle(x*u,y*u,R*.5*u,paint('#ffe0b0',a,stroke=1.5*u))
    c.drawRect(skia.Rect.MakeXYWH((x-1.2)*u,(y-R*3)*u,2.4*u,R*6*u),paint('#fff0d8',a*.7,blur=2*u)); c.drawRect(skia.Rect.MakeXYWH((x-R*1.6)*u,(y-1)*u,R*3.2*u,2*u),paint('#fff0d8',a*.6,blur=2*u))
_NEB={}
def nebula(ctx,e,t,frame):
    a=env(e,t,.8,.8)
    if a<=0: return
    c=ctx.c; u=U(ctx); w,h=e.get('w',260),e.get('h',140); key=(w,h,e.get('seed',4))
    if key not in _NEB:
        n=fbm(128,224,e.get('seed',4)); yy,xx=np.mgrid[-1:1:128j,-1:1:224j]; m=np.clip(1-(xx**2+yy**2),0,1); d=np.clip((n*m*1.8-.25),0,1)
        col=np.array(tuple(int(e.get('col','#c0583a')[i:i+2],16) for i in (1,3,5)))
        img=np.zeros((128,224,4)); img[...,:3]=col*(.6+.6*d[...,None]); img[...,3]=d*220; _NEB[key]=to_img(img)
    p=skia.Paint(); p.setAlphaf(a); x,y=e.get('x',300),e.get('y',100); c.drawImageRect(_NEB[key],skia.Rect.MakeXYWH((x-w/2)*u,(y-h/2)*u,w*u,h*u),skia.SamplingOptions(skia.FilterMode.kLinear),p)
def beam(ctx,e,t,frame):
    """line from a to b drawing on, with travelling bright particle(s)"""
    a=env(e,t,.3,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); (x0,y0),(x1,y1)=e['p0'],e['p1']; k=ease_in_out_cubic(prog(t,e['t0'],e.get('draw',1.5))); col=e.get('col','#d0e4ff')
    c.drawLine(x0*u,y0*u,lerp(x0,x1,k)*u,lerp(y0,y1,k)*u,paint(col,a*.6,stroke=.8*u))
    for j in range(e.get('n',1)):
        q=((t-e['t0'])*e.get('speed',.5)+j/max(1,e.get('n',1)))%1
        if q<k: c.drawCircle(lerp(x0,x1,q)*u,lerp(y0,y1,q)*u,2.5*u,paint('#ffffff',a,blur=1.5*u))
def sonar(ctx,e,t,frame):
    """ring + vertical light column + core glow; depth ticks on left; counter bottom-right"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,R=e.get('x',512),e.get('y',250),e.get('r',150)
    g=skia.GradientShader.MakeLinear([(0,0),(0,ctx.H)],[hexc('#163a6a',a),hexc('#0a1830',a)]); q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),q)
    c.drawCircle(x*u,y*u,R*u,paint('#c0dcff',a*.8,stroke=1*u))
    c.drawRect(skia.Rect.MakeXYWH((x-5)*u,0,10*u,(y+R*.5)*u),paint('#d0e8ff',a*.5,blur=4*u)); c.drawRect(skia.Rect.MakeXYWH((x-1.5)*u,0,3*u,(y+R*.5)*u),paint('#ffffff',a*.8))
    c.drawCircle(x*u,y*u,10*u,paint('#ffffff',a,blur=5*u))
    for i,lab in enumerate(e.get('ticks',['1000 m','1500 m','2000 m','2500 m'])):
        yy=60+i*120; c.drawLine(20*u,yy*u,60*u,yy*u,paint(GREY,a*.6,stroke=.6*u)); draw_text(c,lab,20*u,(yy-4)*u,SR(6*u,500),GREY,a*.7,'left')
    if e.get('count'):
        q_=e['count']; v=lerp(q_['from'],q_['to'],prog(t,e['t0'],q_.get('dur',4)))
        draw_text(c,q_.get('label',''),980*u,(500)*u,SR(7*u,500),GREY,a,'right'); draw_text(c,'{:,.0f}'.format(v)+q_.get('unit',''),980*u,520*u,SR(20*u,700),WHITE,a,'right')
        c.drawLine(880*u,526*u,980*u,526*u,paint(GREY,a,stroke=.6*u))
def cube(ctx,e,t,frame):
    """rotating wireframe cube with vertical sensor strings (dots) inside; optional glow event inside"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,s=e.get('x',400),e.get('y',300),e.get('s',150); ry=e.get('ry',.6)+(t-e['t0'])*e.get('spin',.08); rx=e.get('rx',-.35)
    def P(px,py,pz):
        X=px*math.cos(ry)+pz*math.sin(ry); Z=-px*math.sin(ry)+pz*math.cos(ry); Y=py*math.cos(rx)-Z*math.sin(rx); Z2=py*math.sin(rx)+Z*math.cos(rx); f=600/(600+Z2*s)
        return (x+X*s*f)*u,(y+Y*s*f)*u
    V=[(i,j,k) for i in (-1,1) for j in (-1,1) for k in (-1,1)]
    for a_ in V:
        for b_ in V:
            if sum(p!=q for p,q in zip(a_,b_))==1 and a_<b_:
                p0,p1=P(*a_),P(*b_); c.drawLine(*p0,*p1,paint('#c8dcff',a*.4,stroke=3*u,blur=3*u)); c.drawLine(*p0,*p1,paint('#e0ecff',a*.9,stroke=1*u))
    n=e.get('strings',8)
    for i in range(n):
        for j in range(n):
            px,pz=-1+2*(i+.5)/n,-1+2*(j+.5)/n; k=prog(t,e['t0']+(i+j)*.03,.6)
            for q in np.linspace(-1,-1+2*k,10): X,Y=P(px,q,pz); c.drawCircle(X,Y,.7*u,paint('#d8e8ff',a*.55))
    if e.get('event_t') and t>e['event_t']:
        X,Y=P(0,0,0); kk=prog(t,e['event_t'],.4); c.drawCircle(X,Y,30*kk*u,paint('#ffe8a0',a*.6,blur=12*u))
def streaks(ctx,e,t,frame):
    """falling red/orange streaks (cosmic-ray muons) + optional counter"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); r=random.Random(e.get('seed',2))
    for i in range(e.get('n',40)):
        x=r.uniform(e.get('x0',380),e.get('x1',660)); sp=r.uniform(250,500); ph=r.random(); L=r.uniform(30,90); yy=((t*sp/576+ph)%1.3)*700-100; tilt=r.uniform(-.15,.15)
        col=r.choice(['#ff6a4a','#ff8a60','#ffc0a0']); c.drawLine(x*u,yy*u,(x+L*tilt)*u,(yy+L)*u,paint(col,a*.6,stroke=6*u,blur=5*u)); c.drawLine(x*u,yy*u,(x+L*tilt)*u,(yy+L)*u,paint(col,a,stroke=1*u))
    for i in range(e.get('lines',18)):
        x=e.get('x0',380)+i*(e.get('x1',660)-e.get('x0',380))/18; c.drawLine(x*u,0,x*u,ctx.H,paint('#a0b0c0',a*.12,stroke=.5*u))
    if e.get('count'):
        q=e['count']; v=lerp(q['from'],q['to'],prog(t,e['t0'],q.get('dur',4)))
        draw_text(c,q.get('label',''),60*u,(440)*u,SR(6*u,500),GREY,a,'left'); draw_text(c,'{:,.0f}+'.format(v),60*u,462*u,SR(16*u,800),RED,a,'left'); c.drawLine(60*u,468*u,180*u,468*u,paint(RED,a,stroke=.8*u))
def neon(ctx,e,t,frame):
    """spectral neon columns blob (event display): rainbow vertical bars around x,y, flicker"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); r=random.Random(e.get('seed',5)); x,y,w,h=e.get('x',512),e.get('y',280),e.get('w',120),e.get('h',260); k=ease_out_cubic(prog(t,e['t0'],.8))
    cols=['#ff3a5a','#ff9a3a','#ffe04a','#5aff7a','#3ad0ff','#6a7aff','#c05aff']
    for i in range(e.get('n',40)):
        bx=x+r.gauss(0,w*.35); bh=h*r.uniform(.2,1)*k; by=y+r.gauss(0,h*.15)-bh/2; col=cols[int((bx-x+w)/(2*w)*len(cols))%len(cols)]
        fl=.6+.4*math.sin(t*r.uniform(3,9)+i); bw=r.uniform(3,10)
        c.drawRect(skia.Rect.MakeXYWH(bx*u,by*u,bw*u,bh*u),paint(col,a*.5*fl,blur=9*u)); c.drawRect(skia.Rect.MakeXYWH((bx+bw/3)*u,by*u,bw/3*u,bh*u),paint(col,a*fl))
    c.drawCircle(x*u,y*u,w*.9*u,paint('#a0d0ff',a*.35*k,blur=w*.6*u)); c.drawCircle(x*u,y*u,w*.4*u,paint('#ffffff',a*.45*k,blur=w*.3*u))
def galaxy(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,R=e.get('x',512),e.get('y',260),e.get('r',120); r=random.Random(7); rot=t*.05
    for i in range(e.get('n',1600)):
        arm=i%2; d=r.random()**.7; an=arm*math.pi+d*4.2+rot+r.gauss(0,.25); px=x+math.cos(an)*d*R; py=y+math.sin(an)*d*R*.5
        c.drawCircle(px*u,py*u,r.uniform(.5,1.4)*u,paint('#cfe0ff' if d>.25 else '#ffd8a0',a*r.uniform(.4,1)))
    c.drawCircle(x*u,y*u,14*u,paint('#ffb060',a,blur=8*u)); c.drawCircle(x*u,y*u,4*u,paint('#ffffff',a))
def aurora(ctx,e,t,frame):
    """aurora night: green curtains above mountain silhouette, icy ground, optional person + bench, milky way band"""
    a=env(e,t,.8,.8)
    if a<=0: return
    c=ctx.c; u=U(ctx); hz=e.get('hz',420)
    for j in range(3):
        for x in range(0,1030,4):
            yy=hz-60-40*math.sin(x/140+j*2+t*.3)-20*math.sin(x/53+t*.5); hh=60+30*math.sin(x/90+j+t*.4)
            c.drawRect(skia.Rect.MakeXYWH(x*u,(yy-hh)*u,4*u,hh*u),paint('#30d08a',a*.06*(1+j*.3),blur=3*u))
    if e.get('milky'):
        r=random.Random(2)
        for i in range(900): q=r.random(); c.drawCircle((60+q*900+r.gauss(0,20))*u,(70+q*170+r.gauss(0,18))*u,r.uniform(.3,.9)*u,paint('#e0e8ff',a*r.uniform(.2,.7)))
    pa=skia.Path(); pa.moveTo(0,hz*u)
    for x in range(0,1040,20): pa.lineTo(x*u,(hz-20-18*abs(math.sin(x/130))-10*math.sin(x/37))*u)
    pa.lineTo(ctx.W,hz*u); pa.close(); c.drawPath(pa,paint('#0a1420',a))
    g=skia.GradientShader.MakeLinear([(0,hz*u),(0,ctx.H)],[hexc('#5a7a98',a),hexc('#1a2a3a',a)]); q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeLTRB(0,hz*u,ctx.W,ctx.H),q)
    if e.get('person'):
        px=e['person']; c.drawRect(skia.Rect.MakeXYWH((px-4)*u,(hz-34)*u,8*u,34*u),paint('#05080c',a)); c.drawCircle(px*u,(hz-38)*u,5*u,paint('#05080c',a))
    if e.get('bench'):
        bx=e['bench']; c.drawRect(skia.Rect.MakeXYWH((bx-25)*u,(hz-10)*u,50*u,4*u),paint('#05080c',a)); c.drawRect(skia.Rect.MakeXYWH((bx-22)*u,(hz-10)*u,3*u,10*u),paint('#05080c',a)); c.drawRect(skia.Rect.MakeXYWH((bx+19)*u,(hz-10)*u,3*u,10*u),paint('#05080c',a))
def depth(ctx,e,t,frame):
    """ice-blue depth plane: gradient, hanging dotted string from top, glow ball at y (keys), big year right, depth ticks"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x=e.get('x',512); by=kfi(e.get('ball_y',280),t)
    g=skia.GradientShader.MakeLinear([(0,0),(0,ctx.H)],[hexc('#3a5a7a',a),hexc('#7a9ab8',a),hexc('#2a3a50',a)],[0,.55,1]); q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),q)
    for yy in np.arange(0,by,8): c.drawCircle(x*u,yy*u,.9*u,paint('#ffffff',a*.8))
    c.drawCircle(x*u,by*u,30*u,paint('#e8f0ff',a*.6,blur=14*u)); c.drawCircle(x*u,by*u,14*u,paint('#ffffff',a*.6,blur=4*u))
    for i,lab in enumerate(e.get('ticks',[])): c.drawLine(40*u,(80+i*120)*u,70*u,(80+i*120)*u,paint('#c0d0e0',a*.5,stroke=.6*u)); draw_text(c,lab,40*u,(76+i*120)*u,SR(6*u,500),'#c0d0e0',a*.7,'left')
    if e.get('year'):
        ys=e['year'] if isinstance(e['year'],str) else str(e['year']); draw_text(c,ys,900*u,240*u,SR(34*u,800),GOLD,a,'right')
        if e.get('year_sub'): draw_text(c,e['year_sub'],900*u,256*u,SR(7*u,500),WHITE,a*.8,'right',spacing=1*u)
def beams3d(ctx,e,t,frame):
    """perspective light beams converging (in-ice detectors): many blue streaks toward vanishing point"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); r=random.Random(4); vx,vy=e.get('vx',512),e.get('vy',-200)
    for i in range(e.get('n',70)):
        x0=r.uniform(100,920); y0=r.uniform(200,560); k=((t*.4+r.random())%1)
        x1=lerp(x0,vx,.25*k+.1); y1=lerp(y0,vy,.25*k+.1)
        c.drawLine(x0*u,y0*u,x1*u,y1*u,paint('#80c8ff',a*.7*(1-k*.5),stroke=1.2*u))
def counter(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); v=lerp(e['from'],e['to'],ease_out_cubic(prog(t,e['t0'],e.get('dur',2)))); s=e.get('fmt','{:,.0f}').format(v)
    draw_text(c,s,e.get('x',512)*u,e.get('y',300)*u,SR(e.get('size',60)*u,900),e.get('col','#c8d4e0'),a,e.get('align','center'))
def rain(ctx,e,t,frame):
    """dense particle rain for constant frame change"""
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx); r=random.Random(e.get('seed',1))
    for i in range(e.get('n',120)):
        x=(r.uniform(0,1024)+t*r.uniform(-20,20))%1024; y=(r.uniform(0,576)+t*e.get('speed',180)*r.uniform(.5,1.4))%576
        c.drawCircle(x*u,y*u,r.uniform(.4,1.6)*u,paint(e.get('col','#a0c8ff'),a*r.uniform(.2,.7)))
def chapter(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c;u=U(ctx);k=ease_out_cubic(prog(t,e['t0'],.5))
    draw_text(c,e.get('no',''),e.get('x',40)*u,40*u,font('serif-vf',16*u,800),'#c8d4e0',a*k,'left')
    draw_text(c,e.get('text',''),e.get('x',40)*u,58*u,font('sans',10*u),'#8a98a8',a*k,'left')
def motes(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    RICH.motes(ctx.c,ctx.W,ctx.H,t,n=e.get('n',80),color=e.get('color','#c8a060'),a=a*.4,seed=e.get('seed',7),speed=e.get('speed',1.1))
def beatflash(ctx,e,t,frame):
    beats=e.get('beats') or getattr(ctx,'beats',[])
    if not beats: return
    a=e.get('a',.35); col=e.get('col','#fff4dc'); win=e.get('window',.07)
    b=min(beats,key=lambda x:abs(x-t)); d=abs(t-b)
    if d>win: return
    k=(1-d/win)**1.5; ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(col,a*k))

EXTRA=dict(beatflash=beatflash,caption=caption,title=title,stars=stars,finger=finger,globe=globe,dottext=dottext,star=star,nebula=nebula,beam=beam,sonar=sonar,cube=cube,streaks=streaks,
           neon=neon,galaxy=galaxy,aurora=aurora,depth=depth,beams3d=beams3d,counter=counter,rain=rain,chapter=chapter,motes=motes)
def _render_sc(ctx,sc,t,frame):
    draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)
def draw(ctx,t,frame,S):
    ctx.beats=S.get('beats',[])
    c=ctx.c; c.clear(hexc('#07090e'))
    g=skia.GradientShader.MakeRadial((ctx.W/2,ctx.H*.45),ctx.W*.6,[hexc('#111826'),hexc('#05070b')]); q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),q)
    RICH.compose_scenes(ctx,S,t,frame,_render_sc,overlays_extra=EXTRA,clear=None,
                        vignette_s=.45,grain_a=.03,band_color='#80c8ff',design_size=(1024,576))
    # NOTE: full-frame RICH.beat_punch + type=beatflash cause eye-pain strobe at ~112 BPM.
# Default beat_punch OFF; if enabled keep punch_a <= 0.05. Prefer local pulses (beatrings/motes/pulse).
    if S.get('beat_punch',False) and getattr(ctx,'beats',None): RICH.beat_punch(ctx.c,ctx.W,ctx.H,t,ctx.beats,a=S.get('punch_a',.05),color=S.get('punch_col','#80c8ff'),window=.06)
