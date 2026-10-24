"""#17 生物显微 3D (bio-3d-microscope) — ref 7693232955136675072《2026诺奖：光遗传学》1024x576 210.5s (宇宙常数). Topic-agnostic.
Deep blue-black (#020306) with soft vignette; procedural glowing neurons (soma + branching dendrites + long axon, colour
families blue/violet/cyan/gold) with travelling spikes; neuron fields; green algae cells with eyespot + flagellum;
lipid bilayer (spheres + tails, perspective rows) with blue channel barrels and ions; big cell sphere; spike-trace
panels; stylised white lab mouse with fibre; glass box; circular lens inset; brain outline with lit circuits and
icon tags; gold glowing title. HUD: top-left breadcrumb, top-right logo; left-aligned bottom subtitle with dash +
small grey citation line. Design space 1024x576."""
import math, random, numpy as np, skia
from engine.core import *
from engine.layers import draw_elements, U

FAM={'blue':['#3a6af0','#8ab0ff'],'violet':['#a050f0','#e0a0ff'],'cyan':['#30d0e0','#a0f8ff'],'gold':['#f0b040','#fff0b0'],'white':['#a0b8ff','#ffffff'],'green':['#40e070','#c0ffc0']}
def prepare(S): pass
def env(e,t,fi=.4,fo=.4): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def bg(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx)
    if not e.get('only_glow'): c.drawRect(skia.Rect.MakeWH(W,H),paint(e.get('col','#03050a')))
    if e.get('glow'): x,y,r,col=e['glow']; c.drawCircle(x*u,y*u,r*u,paint(col,.25,blur=r*.6*u))
    if e.get('floor'): c.drawRect(skia.Rect.MakeLTRB(0,e['floor']*u,W,H),skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0,e['floor']*u),skia.Point(0,H)],[hexc('#1a2030'),hexc('#2a3040')])))
    if not e.get('only_glow'): vignette(c,W,H,.6)
def hud(ctx,e,t,frame):
    a=env(e,t,0,0)
    if a<=0: return
    c=ctx.c;u=U(ctx)
    if e.get('crumb'): draw_text(c,e['crumb'],22*u,24*u,font('sans',9*u),'#8a90a0',a,align='left')
    if e.get('logo'): c.drawCircle(940*u,20*u,4*u,paint('#c0c8d8',a,stroke=1.2*u)); draw_text(c,e['logo'],950*u,23*u,font('sans',9*u),'#c0c8d8',a,align='left')
    if e.get('tag'):
        f=font('sans',6.5*u);w=f.measureText(e['tag'])/u+14; rrect(c,22*u,40*u,w*u,13*u,6.5*u,stroke=hexc('#6a7080',a),sw=.8*u); draw_text(c,e['tag'],(22+w/2)*u,49*u,f,'#b0b8c8',a)
def sub(ctx,e,t,frame):
    a=env(e,t,.2,.2)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e.get('x',22),e.get('y',512);f=font('sans',e.get('size',16)*u)
    c.drawLine(x*u,(y-4)*u,(x+8)*u,(y-4)*u,paint('#d0d8e8',a,stroke=1*u))
    for i,ln in enumerate(e['text'].split('\n')):
        xx=(x+14)*u; runs=[];b='';h=False
        for ch in ln:
            if ch in '[]': runs.append((b,h)); b=''; h=(ch=='[')
            else: b+=ch
        runs.append((b,h))
        for r,h in runs:
            if r: draw_text(c,r,xx,(y+i*30)*u,f,'#8ab0ff' if h else '#e8ecf4',a,align='left'); xx+=f.measureText(r)
    if e.get('cite'): draw_text(c,e['cite'],(x+14)*u,(y+e['text'].count('\n')*30+22)*u,font('sans',8.5*u),'#7a8090',a,align='left',spacing=.5*u)
def title(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e.get('x',512),e.get('y',110);k=ease_out_cubic(clamp((t-e['t0'])/.8));sz=e.get('size',56)
    f=font('sans-bold',sz*u); draw_text(c,e['text'],x*u,y*u,f,e.get('col','#f8c060'),a*k,glow=18*u,glow_color='#e08020',glow_a=.8,spacing=e.get('spacing',4)*u)
    if e.get('sub'):
        fs=font('sans',sz*.22*u); w=fs.measureText(e['sub'])/u; draw_text(c,e['sub'],x*u,(y+sz*.62)*u,fs,'#a0b8e8',a*k,spacing=2*u)
        for sx in (-1,1): c.drawLine((x+sx*(w/2+12))*u,(y+sz*.55)*u,(x+sx*(w/2+60))*u,(y+sz*.55)*u,paint('#6a88d0',a*k,stroke=1*u))
_NEU={}
def neuron_geom(seed,n_dend=7,axon=(300,0),scale=1.):
    if (seed,n_dend,axon,scale) in _NEU: return _NEU[(seed,n_dend,axon,scale)]
    R=random.Random(seed); segs=[]
    def branch(x,y,ang,L,depth,w):
        if depth==0 or L<4: return
        x2=x+math.cos(ang)*L; y2=y+math.sin(ang)*L; mx=x+math.cos(ang+R.uniform(-.4,.4))*L*.5; my=y+math.sin(ang+R.uniform(-.4,.4))*L*.5
        segs.append((x,y,mx,my,x2,y2,w))
        for _ in range(R.choice([1,2,2,3])): branch(x2,y2,ang+R.uniform(-.8,.8),L*R.uniform(.55,.8),depth-1,w*.65)
    for i in range(n_dend): branch(0,0,i*2*math.pi/n_dend+R.uniform(-.3,.3),R.uniform(20,40)*scale,4,2.2*scale)
    ax=[]
    if axon[0]>0:
        L,ang=axon; x=y=0; pts=[(0,0)]
        for i in range(12): ang+=R.uniform(-.15,.15); x+=math.cos(ang)*L/12; y+=math.sin(ang)*L/12; pts.append((x,y))
        ax=pts
        for _ in range(4): branch(x,y,ang+R.uniform(-1,1),12*scale,3,1.2*scale)
    _NEU[(seed,n_dend,axon,scale)]=(segs,ax); return segs,ax
def draw_neuron(c,u,x,y,seed,fam,a,s=1,axon=(0,0),grow=1,fire=None,t=0,n=7,glow=1):
    segs,ax=neuron_geom(seed,n,tuple(axon),1); col,hi=FAM.get(fam,FAM['blue'])
    c.save(); c.translate(x*u,y*u); c.scale(s,s)
    pth=skia.Path()
    for (x0,y0,mx,my,x2,y2,w) in segs[:max(1,int(len(segs)*grow))]: pth.moveTo(x0*u,y0*u); pth.quadTo(mx*u,my*u,x2*u,y2*u)
    if ax:
        pa=skia.Path(); pa.moveTo(0,0)
        for px,py in ax[1:max(2,int(len(ax)*grow))]: pa.lineTo(px*u,py*u)
        c.drawPath(pa,paint(col,.45*a*glow,stroke=5*u,blur=4*u)); c.drawPath(pa,paint(hi,.9*a,stroke=1.4*u))
    c.drawPath(pth,paint(col,.4*a*glow,stroke=4*u,blur=3*u)); c.drawPath(pth,paint(hi,.85*a,stroke=1.1*u))
    fk=0
    if fire is not None:
        for ft in (fire if isinstance(fire,list) else [fire]):
            if 0<=t-ft<.6: fk=max(fk,1-(t-ft)/.6)
    c.drawCircle(0,0,(7+5*fk)*u,paint(hi,a*(.4+.6*fk),blur=(6+14*fk)*u)); c.drawCircle(0,0,5*u,paint(hi,a))
    if fk>0 and ax:
        q=1-fk; i=min(len(ax)-1,int(q*(len(ax)-1))); px,py=ax[i]; c.drawCircle(px*u,py*u,4*u,paint('#ffffff',a,blur=3*u))
    c.restore()
def neuron(ctx,e,t,frame):
    a=env(e,t)
    if a>0: draw_neuron(ctx.c,U(ctx),e['x'],e['y'],e.get('seed',1),e.get('fam','blue'),a,e.get('s',1),e.get('axon',(0,0)),clamp((t-e['t0'])/e.get('grow',.01)),e.get('fire'),t,e.get('n',7),e.get('glow',1))
def field(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    R=random.Random(e.get('seed',3)); fams=e.get('fams',['blue','violet','cyan']); u=U(ctx)
    for i in range(e.get('n',18)):
        x=R.uniform(0,1024);y=R.uniform(0,576);s=R.uniform(.5,1.4)*e.get('s',1);fam=R.choice(fams);dr=e.get('drift',4)
        fire=[R.uniform(0,5)+k*R.uniform(2,5) for k in range(40)]
        draw_neuron(ctx.c,u,x+math.sin(t*.2+i)*dr,y+math.cos(t*.17+i)*dr,i+e.get('seed',3)*50,fam,a*R.uniform(.5,1),s,(R.uniform(60,160),R.uniform(0,6.28)),1,[e['t0']+f for f in fire],t,6,1)
def cell(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e['x'],e['y'],e.get('r',50);rot=e.get('rot',-20)+math.sin(t)*3
    c.save();c.translate(x*u,y*u);c.rotate(rot)
    rr=skia.Rect.MakeLTRB(-r*u,-r*.75*u,r*u,r*.75*u)
    c.drawOval(rr,paint('#40ff60',.35*a,blur=14*u)); c.drawOval(rr,skia.Paint(AntiAlias=True,Shader=skia.GradientShader.MakeRadial(skia.Point(-r*.2*u,-r*.2*u),r*1.2*u,[hexc('#c0ffb0',a),hexc('#40d050',a),hexc('#108020',a)])))
    c.drawOval(rr,paint('#d0ffd0',.8*a,stroke=1.5*u)); c.drawCircle(r*.3*u,-r*.25*u,r*.12*u,paint('#ff6020',a)); 
    fl=skia.Path(); fl.moveTo(r*u,0)
    for i in range(1,30): fl.lineTo((r+i*5)*u,(math.sin(i*.4-t*6)*6+i*.8)*u)
    c.drawPath(fl,paint('#d0ffd0',.7*a,stroke=1*u)); c.restore()
def membrane(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);y=e.get('y',330);rows=e.get('rows',4);ch=e.get('channels',[])
    for r_ in range(rows):
        sc=.7+r_*.15; yy=y-(rows-1-r_)*26*sc; sp=17*sc; R=random.Random(r_)
        for side in (-1,1):
            for i in range(int(1100/sp)):
                x=-40+i*sp+(r_%2)*sp/2; top=yy+side*(-12*sc) if side<0 else yy+30*sc
                c.drawLine(x*u,(yy-4*sc+ (0 if side<0 else 18*sc))*u,x*u,(yy+(14 if side<0 else 6)*sc)*u,paint('#5a6a9a',a*.8,stroke=1.6*sc*u))
                c.drawCircle(x*u,(yy-6*sc if side<0 else yy+26*sc)*u,9*sc*u,skia.Paint(AntiAlias=True,Shader=skia.GradientShader.MakeRadial(skia.Point((x-2*sc)*u,(yy-8*sc if side<0 else yy+24*sc)*u),10*sc*u,[hexc('#e0e4f0',a),hexc('#7a84a8',a)])))
        for cx in ch:
            if r_==rows-1:
                op=kfi(cx[1] if len(cx)>1 else 0,t); col=cx[2] if len(cx)>2 else '#3a80f0'
                for k in range(4): rrect(c,(cx[0]-26+k*14)*u,(yy-40)*u,12*u,95*u,5*u,fill=hexc(col,a))
                if op>0: c.drawRect(skia.Rect.MakeXYWH((cx[0]-4)*u,(yy-40)*u,8*u,95*u),paint('#b0e0ff',.7*a*op,blur=3*u))
    if e.get('ions'):
        R=random.Random(9)
        for i in range(e['ions']):
            x=R.uniform(0,1024); y0=R.uniform(y+50,576); flow=kfi(e.get('flow',0),t); yy=y0-((t*40*flow)%200 if flow>0 else 0)
            c.drawCircle(x*u,yy*u,5*u,skia.Paint(AntiAlias=True,Shader=skia.GradientShader.MakeRadial(skia.Point((x-1.5)*u,(yy-1.5)*u),6*u,[hexc('#f0b090',a),hexc('#a04030',a)])))
def sphere(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e['x'],e['y'],e.get('r',120);col=e.get('col',['#e8c8a0','#6a4a30'])
    c.drawCircle(x*u,y*u,r*u,skia.Paint(AntiAlias=True,Shader=skia.GradientShader.MakeRadial(skia.Point((x-r*.35)*u,(y-r*.35)*u),r*1.4*u,[hexc(col[0],a),hexc(col[1],a),hexc('#0a0806',a)])))
    c.drawCircle(x*u,y*u,r*1.02*u,paint('#c0d0ff',.25*a,stroke=3*u,blur=3*u))
def trace(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e.get('x',250),e.get('y',100),e.get('w',230),e.get('h',190)
    rrect(c,x*u,y*u,w*u,h*u,6*u,fill=hexc('#0a1020',.85*a),stroke=hexc('#3a4a70',a),sw=1*u)
    draw_text(c,e.get('l1','光'),(x+10)*u,(y+22)*u,font('sans-bold',11*u),'#e0e8f8',a,align='left'); draw_text(c,e.get('l2','神经元'),(x+10)*u,(y+70)*u,font('sans-bold',11*u),'#e0e8f8',a,align='left')
    spikes=e.get('spikes',[]); p=skia.Path(); base=y+h-20; p.moveTo((x+10)*u,base*u); q=skia.Path(); q.moveTo((x+10)*u,(y+35)*u)
    win=e.get('win',4.0)
    for i in range(201):
        tt=t-win+win*i/200; xx=x+10+(w-20)*i/200; v=0; l=0
        for sp in spikes:
            d=tt-sp
            if 0<=d<.03: v=max(v,1)
            if 0<=d<.15: l=1
        p.lineTo(xx*u,(base-v*(h-80))*u); q.lineTo(xx*u,(y+35-l*14)*u)
    c.drawPath(q,paint('#4a8aff',a,stroke=1.5*u)); c.drawPath(p,paint('#f0e0a0',.4*a,stroke=3*u,blur=2*u)); c.drawPath(p,paint('#f8e8b0',a,stroke=1.2*u))
def mouse(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,s=e['x'],e['y'],e.get('s',1);S=s*u;X,Y=x*u,y*u;fl=e.get('flip',1)
    c.save();c.translate(X,Y);c.scale(fl,1)
    c.drawOval(skia.Rect.MakeLTRB(-90*S,40*S,90*S,60*S),paint('#000000',.4*a,blur=8*S))
    tail=skia.Path(); tail.moveTo(-70*S,30*S); tail.cubicTo(-130*S,40*S,-170*S,10*S,-210*S,25*S); c.drawPath(tail,paint('#e8a0a8',a,stroke=3*S))
    body=skia.Path(); body.addOval(skia.Rect.MakeLTRB(-80*S,-35*S,60*S,45*S)); 
    sh=skia.GradientShader.MakeRadial(skia.Point(-10*S,-20*S),90*S,[hexc('#ffffff',a),hexc('#e8e8f0',a),hexc('#9aa0b8',a)])
    c.drawPath(body,skia.Paint(AntiAlias=True,Shader=sh)); c.drawOval(skia.Rect.MakeLTRB(30*S,-30*S,105*S,25*S),skia.Paint(AntiAlias=True,Shader=sh))
    c.drawOval(skia.Rect.MakeLTRB(48*S,-58*S,78*S,-22*S),paint('#f0f0f4',a)); c.drawOval(skia.Rect.MakeLTRB(53*S,-52*S,73*S,-28*S),paint('#f0b0c0',a))
    c.drawCircle(85*S,-8*S,4*S,paint('#e02040',a)); c.drawCircle(104*S,2*S,3*S,paint('#f0a0b0',a))
    for wx in (-1,1): c.drawLine(100*S,2*S,128*S,(2+wx*8)*S,paint('#ffffff',.6*a,stroke=.6*S))
    for fx in (-40,-10,25,50): c.drawOval(skia.Rect.MakeLTRB((fx-8)*S,36*S,(fx+8)*S,48*S),paint('#f0b0c0',a))
    c.restore()
    if e.get('fiber'): c.drawLine((x+60*s*fl)*u,(y-30*s)*u,(x+60*s*fl)*u,0,paint('#4060c0',.8*a,stroke=1.2*u)); c.drawCircle((x+60*s*fl)*u,(y-30*s)*u,4*u,paint('#80a0ff',a*(.6+.4*math.sin(t*8)),blur=3*u))
    if e.get('glow'): c.drawCircle(x*u,y*u,140*s*u,paint('#ffffff',.08*a,blur=60*u))
def glassbox(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h,d=e.get('x',70),e.get('y',330),e.get('w',370),e.get('h',120),e.get('d',90)
    P=[(x,y),(x+w,y),(x+w+d,y-d*.6),(x+d,y-d*.6)]; fl=skia.Path(); fl.moveTo(P[0][0]*u,(P[0][1]+h)*u)
    for px,py in [(P[1][0],P[1][1]+h),(P[2][0],P[2][1]+h),(P[3][0],P[3][1]+h)]: fl.lineTo(px*u,py*u)
    fl.close(); c.drawPath(fl,paint('#c0c8e0',.6*a))
    pp=paint('#c0d0f0',.55*a,stroke=1*u)
    for (ax,ay),(bx,by) in zip(P,P[1:]+P[:1]): c.drawLine(ax*u,ay*u,bx*u,by*u,pp); c.drawLine(ax*u,(ay+h)*u,bx*u,(by+h)*u,pp)
    for px,py in P: c.drawLine(px*u,py*u,px*u,(py+h)*u,pp)
def lens(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e['x'],e['y'],e.get('r',45);k=ease_out_back(clamp((t-e['t0'])/.5))
    c.save(); p=skia.Path(); p.addCircle(x*u,y*u,r*k*u); c.clipPath(p,doAntiAlias=True); c.drawCircle(x*u,y*u,r*u,paint('#04060c',a))
    R=random.Random(e.get('seed',2))
    for i in range(e.get('n',6)): draw_neuron(c,u,x+R.uniform(-r*.6,r*.6),y+R.uniform(-r*.6,r*.6),i+30,e.get('fam','white'),a,.35,(0,0),1,[e['t0']+R.uniform(0,2)+j*1.7 for j in range(30)],t,6)
    c.restore(); c.drawCircle(x*u,y*u,r*k*u,paint('#6a8ad0',a,stroke=2.5*u)); c.drawCircle(x*u,y*u,(r+4)*k*u,paint('#4a6ab0',.5*a,stroke=4*u,blur=4*u))
    if e.get('label'): draw_text(c,e['label'],x*u,(y+r+14)*u,font('sans',7*u),'#c0c8d8',a)
def label(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e['x'],e['y'];tx,ty=e.get('to',[x,y]);col=e.get('col','#f0a040')
    if e.get('to'): c.drawLine(x*u,y*u,tx*u,ty*u,paint('#c0c8d8',.7*a,stroke=.8*u)); c.drawCircle(tx*u,ty*u,2*u,paint('#ffffff',a))
    draw_text(c,e['text'],x*u,(y-3)*u,font('sans-bold',e.get('size',10)*u),col,a,align=e.get('align','center'))
    if e.get('sub'): draw_text(c,e['sub'],x*u,(y+9)*u,font('sans',6.5*u),'#a0a8b8',a,align=e.get('align','center'))
def bignum(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e.get('x',60),e.get('y',70);v=kfi(e.get('value',0),t)
    draw_text(c,e.get('pre','约'),x*u,y*u,font('sans',10*u),'#c0c8d8',a,align='left'); draw_text(c,e.get('fmt','%d')%v,(x+18)*u,(y+12)*u,font('sans',54*u),'#e8ecf8',a,align='left',glow=8*u,glow_color='#6080ff')
    draw_text(c,e.get('unit','亿'),(x+18+font('sans',54*u).measureText(e.get('fmt','%d')%v)/u+4)*u,y*u,font('sans',14*u),'#e8ecf8',a,align='left')
    for i,(lab,col) in enumerate(e.get('legend',[])): c.drawCircle((x+4+i*48)*u,(y+30)*u,2.5*u,paint(col,a)); draw_text(c,lab,(x+10+i*48)*u,(y+33)*u,font('sans',6.5*u),'#c0c8d8',a,align='left')
def brain(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e.get('x',512),e.get('y',300),e.get('w',560),e.get('h',260)
    o=skia.Path(); o.addOval(skia.Rect.MakeXYWH((x-w/2)*u,(y-h/2)*u,w*u,h*u)); c.drawPath(o,paint('#2a3a80',.25*a)); c.drawPath(o,paint('#6a80d0',.8*a,stroke=1.5*u))
    c.drawOval(skia.Rect.MakeXYWH((x+w*.3)*u,(y-h*.15)*u,w*.25*u,h*.45*u),paint('#6a80d0',.8*a,stroke=1.2*u))
    R=random.Random(5)
    for i in range(60): c.drawCircle((x+R.uniform(-.45,.45)*w)*u,(y+R.uniform(-.4,.4)*h)*u,R.uniform(.5,1.5)*u,paint('#c0d0ff',R.uniform(.2,.7)*a))
    for path in e.get('circuits',[]):
        t0=path[0]; pts=path[1]; k=clamp((t-t0)/1.2); p=skia.Path(); p.moveTo(pts[0][0]*u,pts[0][1]*u)
        for (px,py) in pts[1:]: p.lineTo(px*u,py*u)
        me=skia.PathMeasure(p,False); seg=skia.Path(); me.getSegment(0,me.getLength()*k,seg,True)
        c.drawPath(seg,paint('#f0b040',.5*a,stroke=6*u,blur=4*u)); c.drawPath(seg,paint('#ffd070',a,stroke=2*u))
    for ic in e.get('icons',[]):
        ix,iy,txt,ti=ic; k=clamp((t-ti)/.4)
        if k>0: c.drawCircle(ix*u,iy*u,11*u,paint('#0a1020',a*k)); c.drawCircle(ix*u,iy*u,11*u,paint('#c0c8e0',a*k,stroke=1.2*u)); draw_text(c,txt,ix*u,(iy+24)*u,font('sans-bold',9*u),'#e8ecf8',a*k)
def flash(ctx,e,t,frame):
    if e['t0']<=t<e['t0']+e.get('dur',.034): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#ffffff'),e.get('a',.85)))
def stars(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    R=random.Random(1);u=U(ctx)
    for i in range(e.get('n',150)): ctx.c.drawCircle(R.uniform(0,ctx.W),R.uniform(0,ctx.H),R.uniform(.3,1.2)*u,paint('#c0d0ff',R.uniform(.2,.7)*a))
def card(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e['x'],e['y'],e.get('w',170),e.get('h',80)
    rrect(c,x*u,y*u,w*u,h*u,6*u,fill=hexc('#0a1020',.85*a),stroke=hexc('#3a4a70',a),sw=1*u)
    for i,ln in enumerate(e.get('lines',[])): draw_text(c,ln,(x+w/2)*u,(y+h/2+5+(i-(len(e['lines'])-1)/2)*14)*u,font('sans',8*u),'#d0d8e8',a)
EXTRA={'bg':bg,'hud':hud,'sub':sub,'title':title,'neuron':neuron,'field':field,'cell':cell,'membrane':membrane,'sphere':sphere,'trace':trace,'mouse':mouse,'glassbox':glassbox,'lens':lens,'label':label,'bignum':bignum,'brain':brain,'flash':flash,'stars':stars,'card':card}
def draw(ctx,t,frame,S):
    c=ctx.c; c.clear(hexc('#020306')); draw_elements(ctx,S.get('under',[]),t,frame,EXTRA)
    for sc in S['scenes']:
        if sc['t0']-1e-6<=t<sc['t1']:
            k=fade_env(t,sc['t0'],sc['t1'],sc.get('fade_in',.5),sc.get('fade_out',.5))
            if k<=0: continue
            c.saveLayerAlpha(None,int(255*k)); draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)
            if sc.get('flash') and sc['t0']<=t<sc['t0']+.034: c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint('#ffffff',.85))
            c.restore()
    draw_elements(ctx,S.get('overlays',[]),t,frame,EXTRA)
