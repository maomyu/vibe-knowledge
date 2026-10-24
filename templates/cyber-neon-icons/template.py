"""#18 赛博霓虹图标 (cyber-neon-icons) — ref 7697578828587126025《像反派一样思考》1920x1080 341s (人心有局). Topic-agnostic.
Dark navy/purple/crimson radial-gradient grounds with bokeh, perspective grid floor or flowing purple wave lines.
Flat glowing icons: blue bust person, glowing figure silhouettes, line-art sedan, phone + chat, clock, chapter card
(01 + label), HUD bars, neon line with dot head, ECG wave, glowing orb with rays, magenta network with avatar nodes,
radar rings, neon frame being drawn, pink people group, round table, dot ring, light split, horizon line + target.
Subtitle: centred bold white with cyan glow + underline bar, [关键词] in blue/magenta; big headline at top.
Design space 1024x576."""
import math, random, skia
from engine.core import *
from engine.layers import draw_elements, U
from engine import richness as RICH

def prepare(S): pass
def env(e,t,fi=.35,fo=.35): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def pop(e,t,d=.35):
    x=clamp((t-e['t0'])/d); return ease_out_back(x) if x<1 else 1
B='sans-bold'

def bg(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx)
    c1,c2=e.get('c1','#1a2a50'),e.get('c2','#060814')
    cx,cy=e.get('cx',512),e.get('cy',260)
    c.drawRect(skia.Rect.MakeWH(W,H),skia.Paint(Shader=skia.GradientShader.MakeRadial(skia.Point(cx*u,cy*u),e.get('r',620)*u,[hexc(c1),hexc(c2)])))
    if e.get('c3'): x,y,r=e.get('p3',[200,450,300]); c.drawCircle(x*u,y*u,r*u,paint(e['c3'],.35,blur=r*.5*u))
    R=random.Random(e.get('seed',3))
    for i in range(e.get('bokeh',0)):
        x=R.uniform(0,1024)+math.sin(t*.2+i)*8;y=R.uniform(0,576);r=R.uniform(10,40)
        c.drawCircle(x*u,y*u,r*u,paint(R.choice(['#6080ff','#ff60a0','#60e0ff']),.06,blur=r*.4*u))
    if e.get('grid'):
        gy=e.get('grid');col=e.get('gcol','#3050a0')
        for i in range(-20,21):
            line(c,(512+i*40)*u,gy*u,(512+i*160)*u,576*u,col,.25,w=.7*u)
        for j in range(8):
            yy=gy+(576-gy)*(j/8)**1.8; line(c,0,yy*u,W,yy*u,col,.25,w=.7*u)
    if e.get('waves'):
        col=e.get('wcol','#8040c0')
        for k in range(e.get('waves')):
            p=skia.Path()
            for i in range(0,1030,8):
                y=e.get('wy',470)+k*7+math.sin(i*.008+t*.5+k*.4)*30+math.sin(i*.02-t*.3)*10
                (p.moveTo if i==0 else p.lineTo)(i*u,y*u)
            c.drawPath(p,paint(col,.35,stroke=1*u))
    vignette(c,W,H,.55)

def sub(ctx,e,t,frame):
    a=env(e,t,.12,.12)
    if a<=0: return
    c=ctx.c;u=U(ctx);f=font(B,e.get('size',19)*u);hl=e.get('hl','#5ab0ff')
    lines=e['text'].split('\n');y0=e.get('y',490)-(len(lines)-1)*e.get('size',19)*1.35
    for i,ln in enumerate(lines):
        runs=[];b='';h=False
        for ch in ln:
            if ch in '[]': runs.append((b,hl if h else e.get('col','#ffffff'))); b=''; h=(ch=='[')
            else: b+=ch
        runs.append((b,hl if h else e.get('col','#ffffff')))
        runs=[r for r in runs if r[0]]
        draw_rich(c,runs,e.get('x',512)*u,(y0+i*e.get('size',19)*1.35)*u,f,a=a,glow=e.get('glow',6)*u)
    if e.get('bar',True):
        w=text_width(lines[-1].replace('[','').replace(']',''),f)/u+30
        yb=y0+(len(lines)-1)*e.get('size',19)*1.35+e.get('size',19)*.55
        line(c,(512-w/2)*u,yb*u,(512+w/2)*u,yb*u,e.get('barcol','#4a6aa0'),a*.8,w=1.5*u)
def head(ctx,e,t,frame):
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('size',30);f=font(B,s*u)
    for i,ln in enumerate(e['text'].split('\n')):
        draw_text(c,ln,e.get('x',512)*u,(e.get('y',130)+i*s*1.3)*u,f,e.get('col','#e8f0ff'),a,glow=12*u,glow_color=e.get('gcol','#4080ff'),glow_a=.8,align=e.get('align','center'))
def person(ctx,e,t,frame):
    a=env(e,t);
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('s',1)*pop(e,t)*u;x,y=e['x']*u,e['y']*u;col=e.get('col','#5a8ae0')
    c.drawCircle(x,y-10*s,60*s,paint(col,.25*a,blur=30*s))
    p=skia.Path();p.moveTo(x-40*s,y+30*s);p.cubicTo(x-40*s,y-5*s,x-20*s,y-12*s,x,y-12*s);p.cubicTo(x+20*s,y-12*s,x+40*s,y-5*s,x+40*s,y+30*s);p.close()
    c.drawPath(p,skia.Paint(AntiAlias=True,Shader=skia.GradientShader.MakeLinear([skia.Point(x,y-12*s),skia.Point(x,y+30*s)],[hexc(col,a),hexc('#2a4aa0',a)])))
    c.drawCircle(x,y-32*s,19*s,paint('#dde8ff',a));c.drawCircle(x,y-32*s,19*s,paint(col,a,stroke=2*s))
    if e.get('horns'):
        for sg in (-1,1):
            p=skia.Path();p.moveTo(x+sg*10*s,y-48*s);p.lineTo(x+sg*20*s,y-64*s);p.lineTo(x+sg*17*s,y-44*s);p.close();c.drawPath(p,paint(col,a))
    if e.get('neon'):
        c.drawCircle(x,y-32*s,19*s,paint('#1a0612',a));c.drawCircle(x,y-32*s,19*s,paint(col,a,stroke=2.5*s))
        c.drawPath(p,paint('#1a0612',a));c.drawPath(p,paint(col,a,stroke=2.5*s))
        for dx in (-7,7): line(c,x+(dx-4)*s,y-35*s,x+(dx+4)*s,y-33*s if dx<0 else y-37*s,col,a,w=2*s)
        return
    mood=e.get('mood','sad')
    for dx in (-6,6): c.drawCircle(x+dx*s,y-34*s,2*s,paint('#203060',a))
    p=skia.Path();p.moveTo(x-6*s,y-24*s);p.quadTo(x,y-(28 if mood=='sad' else 20)*s,x+6*s,y-24*s);c.drawPath(p,paint('#203060',a,stroke=1.5*s))
    if e.get('scribble'):
        R=random.Random(5);p=skia.Path();p.moveTo(x+10*s,y-50*s)
        for i in range(30): p.lineTo(x+R.uniform(-50,50)*s,y+R.uniform(-90,-10)*s)
        c.drawPath(p,paint('#6a8ad0',a*.6,stroke=1*s))
def figure(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('s',1)*u;x,y=e['x']*u,e['y']*u;col=e.get('col','#a0f0ff')
    c.drawCircle(x,y-20*s,50*s,paint(col,.2*a,blur=25*s))
    rrect(c,x-14*s,y-30*s,28*s,62*s,12*s,fill=col,a=a);c.drawCircle(x,y-44*s,11*s,paint(col,a))
    c.drawCircle(x,y-44*s,14*s,paint('#ffffff',.3*a,blur=6*s))
def car(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('s',1)*u;x,y=(e['x']+kfi(e.get('dx',0),t))*u,e['y']*u;col=e.get('col','#c02040')
    p=skia.Path();pts=[(-110,0),(-110,-18),(-90,-24),(-50,-28),(-25,-48),(35,-48),(65,-28),(105,-22),(112,-8),(110,0)]
    p.moveTo((pts[0][0])*s+x,pts[0][1]*s+y)
    for px,py in pts[1:]: p.lineTo(px*s+x,py*s+y)
    p.close()
    c.drawPath(p,skia.Paint(AntiAlias=True,Shader=skia.GradientShader.MakeLinear([skia.Point(x,y-48*s),skia.Point(x,y)],[hexc(col,a),hexc('#400818',a)])))
    c.drawPath(p,paint(e.get('ncol','#ff5070'),a,stroke=1.8*s)); c.drawPath(p,paint(e.get('ncol','#ff5070'),a*.5,stroke=4*s,blur=4*s))
    q=skia.Path();q.moveTo(x-20*s,y-44*s);q.lineTo(x+30*s,y-44*s);q.lineTo(x+52*s,y-28*s);q.lineTo(x-42*s,y-28*s);q.close();c.drawPath(q,paint('#ffc0d0',.25*a))
    for wx in (-65,65): c.drawCircle(x+wx*s,y,14*s,paint('#100008',a));c.drawCircle(x+wx*s,y,14*s,paint('#ff5070',a,stroke=1.5*s))
    c.drawOval(skia.Rect.MakeLTRB(x-130*s,y+10*s,x+130*s,y+22*s),paint(col,.35*a,blur=8*s))
    if e.get('scratch'): line(c,x-10*s,y-20*s,x+40*s,y-14*s,'#ffffff',a*clamp((t-e['scratch'])/.4),w=1.5*s,glow=3*s)
def phone(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('s',1)*u;x,y=e['x']*u,e['y']*u
    rrect(c,x-45*s,y-85*s,90*s,170*s,14*s,fill='#0c0a20',stroke='#a070ff',a=a,sw=2*s);rrect(c,x-45*s,y-85*s,90*s,170*s,14*s,stroke='#a070ff',a=a*.5,sw=6*s,blur=5*s)
    for i,m in enumerate(e.get('msgs',[])):
        tt=m.get('t',e['t0']+i*.6)
        if t<tt: continue
        me=m.get('me',i%2==1);f=font('sans',7*s);w=min(70,text_width(m['text'],f)/s+10)
        bx=x+(35-w)*s if me else x-37*s;by=y-70*s+i*20*s
        rrect(c,bx,by,w*s,14*s,4*s,fill='#e0a030' if me else '#3a3a60',a=a);draw_text(c,m['text'],bx+5*s,by+10*s,f,'#101010' if me else '#ffffff',a,align='left')
def clock(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);r=e.get('r',30)*u;x,y=e['x']*u,e['y']*u;col=e.get('col','#ff5a8a')
    c.drawCircle(x,y,r,paint(col,a,stroke=2*u));c.drawCircle(x,y,r,paint(col,a*.5,stroke=5*u,blur=4*u))
    for i in range(12): an=i*math.pi/6; line(c,x+math.cos(an)*r*.82,y+math.sin(an)*r*.82,x+math.cos(an)*r*.92,y+math.sin(an)*r*.92,col,a,w=1*u)
    an=t*e.get('speed',2);line(c,x,y,x+math.sin(an)*r*.75,y-math.cos(an)*r*.75,'#ffffff',a,w=1.5*u);line(c,x,y,x+math.sin(an/12)*r*.5,y-math.cos(an/12)*r*.5,'#ffffff',a,w=2*u)
def chapter(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e.get('x',60),e.get('y',60);w,h=e.get('w',130),e.get('h',110)
    rrect(c,x*u,y*u,w*u,h*u,8*u,fill='#101830',stroke='#5a70b0',a=a*.85,sw=1.2*u)
    draw_text(c,e.get('num','01'),(x+12)*u,(y+30)*u,font('sans',18*u),'#a0b8ff',a,align='left')
    draw_text(c,e.get('label',''),(x+w/2)*u,(y+h/2+12)*u,font(B,13*u),'#ffffff',a)
def hbars(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e['x'],e['y'];R=random.Random(e.get('seed',2))
    for i in range(e.get('n',5)):
        w=e.get('w',90)*R.uniform(.5,1)*clamp((t-e['t0']-i*.08)/.5)
        rrect(c,x*u,(y+i*14)*u,e.get('w',90)*u,4*u,2*u,fill='#2a3a60',a=a);rrect(c,x*u,(y+i*14)*u,w*u,4*u,2*u,fill=e.get('col','#5a90ff'),a=a)
def gline(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);p=clamp((t-e['t0'])/e.get('dur',.8)) if e.get('draw',True) else 1;p=ease_out_cubic(p)
    x0,y0,x1,y1=e['pts'];xe,ye=x0+(x1-x0)*p,y0+(y1-y0)*p;col=e.get('col','#ff4060')
    if e.get('dash'):
        n=int(math.hypot(xe-x0,ye-y0)/8)
        for i in range(n): xx=x0+(xe-x0)*i/max(n,1);yy=y0+(ye-y0)*i/max(n,1);c.drawCircle(xx*u,yy*u,1.2*u,paint(col,a))
    else: line(c,x0*u,y0*u,xe*u,ye*u,col,a,w=e.get('w',2)*u,glow=5*u)
    glow_dot(c,xe*u,ye*u,3*u,col,a,halo=4)
    if e.get('nodes'):
        for (nx,ny,lab) in e['nodes']:
            c.drawCircle(nx*u,ny*u,24*u,paint('#2a1020',a));c.drawCircle(nx*u,ny*u,24*u,paint(e.get('ncol','#f0c040'),a,stroke=2.5*u));c.drawCircle(nx*u,ny*u,30*u,paint(e.get('ncol','#f0c040'),a*.4,blur=10*u))
            draw_text(c,lab,nx*u,(ny+7)*u,font(B,20*u),e.get('ncol','#f0c040'),a)
def ecg(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);y=e.get('y',260);col=e.get('col','#ff3050');R=random.Random(e.get('seed',4))
    pts=[(x,y+(R.uniform(-1,1)*e.get('amp',70)*(abs(math.sin(x*.02)))) if x%12==0 else y) for x in range(e.get('x0',120),e.get('x1',900),6)]
    n=int(len(pts)*clamp((t-e['t0'])/e.get('dur',1.2)))
    p=skia.Path()
    for i,(x,yy) in enumerate(pts[:max(n,2)]): (p.moveTo if i==0 else p.lineTo)(x*u,yy*u)
    c.drawPath(p,paint(col,a*.6,stroke=4*u,blur=4*u));c.drawPath(p,paint(col,a,stroke=1.6*u))
    glow_dot(c,pts[max(n,2)-1][0]*u,pts[max(n,2)-1][1]*u,3*u,col,a)
def orb(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e['x']*u,e['y']*u,e.get('r',50)*u*pop(e,t,.5);col=e.get('col','#40e0d0')
    c.drawCircle(x,y,r*1.6,paint(col,.25*a,blur=r*.6));c.drawCircle(x,y,r*1.3,paint(col,a,stroke=1.2*u))
    c.drawCircle(x,y,r,skia.Paint(AntiAlias=True,Shader=skia.GradientShader.MakeRadial(skia.Point(x-r*.3,y-r*.3),r*1.2,[hexc('#ffe8a0',a),hexc('#806020',a)])))
    R=random.Random(1)
    for i in range(14):
        an=R.uniform(0,6.28)+t*.1;d=r*(1.8+R.uniform(0,.8))
        line(c,x+math.cos(an)*d,y+math.sin(an)*d,x+math.cos(an)*(d+10*u),y+math.sin(an)*(d+10*u),e.get('rcol','#ff4070'),a,w=2*u)
def web(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);R=random.Random(e.get('seed',7));col=e.get('col','#e030a0')
    for i in range(e.get('n',60)):
        x0,y0=R.uniform(-100,1124),R.uniform(-50,626);x1,y1=x0+R.uniform(-600,600),y0+R.uniform(-300,300)
        p=skia.Path();p.moveTo(x0*u,y0*u);p.quadTo((x0+x1)/2*u+math.sin(t+i)*30*u,(y0+y1)/2*u,x1*u,y1*u)
        c.drawPath(p,paint(col,a*.45,stroke=.8*u))
    for (nx,ny) in e.get('nodes',[]):
        c.drawCircle(nx*u,ny*u,13*u,paint('#300820',a));c.drawCircle(nx*u,ny*u,13*u,paint('#ff70c0',a,stroke=1.5*u))
        c.drawCircle(nx*u,(ny-3)*u,4*u,paint('#ffd0e8',a));c.drawCircle(nx*u,(ny+8)*u,7*u,paint('#ffd0e8',a))
    if e.get('slash'):
        p=skia.Path();x=e['slash'];p.moveTo((x+60)*u,0);p.lineTo((x+70)*u,0);p.lineTo((x-60)*u,576*u);p.lineTo((x-70)*u,576*u);p.close();c.drawPath(p,paint('#ffffff',a))
def radar(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e.get('x',512)*u,e.get('y',290)*u;col=e.get('col','#5ac0c0')
    for i in range(e.get('n',4)): rr=(e.get('r',80)+i*e.get('step',70)+(t*20)%e.get('step',70))*u; c.drawCircle(x,y,rr,paint(col,a*.35,stroke=1*u))
def frame_(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e['x'],e['y'],e['w'],e['h'];col=e.get('col','#a070ff')
    P=[(x,y+h),(x+w,y+h),(x+w,y),(x,y),(x,y+h*.0)];per=2*(w+h);L=per*ease_in_out_cubic(clamp((t-e['t0'])/e.get('dur',1.5)))
    p=skia.Path();p.moveTo(x*u,(y+h)*u);acc=0;last=(x,y+h)
    for (ax,ay),(bx,by) in zip(P,P[1:]):
        sl=math.hypot(bx-ax,by-ay)
        if acc+sl>=L: f=(L-acc)/sl if sl else 0; last=(ax+(bx-ax)*f,ay+(by-ay)*f); p.lineTo(last[0]*u,last[1]*u); break
        p.lineTo(bx*u,by*u);acc+=sl;last=(bx,by)
    c.drawPath(p,paint(col,a*.5,stroke=5*u,blur=4*u));c.drawPath(p,paint(col,a,stroke=1.5*u));glow_dot(c,last[0]*u,last[1]*u,2.5*u,'#ffffff',a)
def people(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx)
    for (x,y,s,col) in e['list']:
        s*=u*pop(e,t);x*=u;y*=u
        c.drawCircle(x,y-22*s,9*s,paint(col,a));rrect(c,x-15*s,y-10*s,30*s,22*s,10*s,fill=col,a=a)
        c.drawCircle(x,y-10*s,30*s,paint(col,.15*a,blur=14*s))
def table(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e.get('x',512)*u,e.get('y',300)*u;r=e.get('r',120)*u
    c.drawOval(skia.Rect.MakeLTRB(x-r,y-r*.45,x+r,y+r*.45),paint('#5a2030',a));c.drawOval(skia.Rect.MakeLTRB(x-r,y-r*.45,x+r,y+r*.45),paint('#c05070',a,stroke=2*u))
    R=random.Random(2)
    for i in range(6): an=i*1.05+.3;c.drawOval(skia.Rect.MakeXYWH(x+math.cos(an)*r*.55-12*u,y+math.sin(an)*r*.25-6*u,24*u,12*u),paint(R.choice(['#f0e0c0','#80c060','#e08040']),a))
    for i in range(e.get('n',6)):
        an=i*2*math.pi/e.get('n',6)-math.pi/2;px,py=x+math.cos(an)*r*1.25,y+math.sin(an)*r*.75
        c.drawCircle(px,py,13*u,paint('#f0d0b0',a));c.drawCircle(px,py-4*u,13*u,paint('#a03060',a*.9,stroke=3*u))
def dots(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e.get('x',512)*u,e.get('y',270)*u;rx,ry=e.get('rx',110)*u,e.get('ry',70)*u;col=e.get('col','#40d0ff')
    c.drawOval(skia.Rect.MakeLTRB(x-rx*.45,y-ry*.4,x+rx*.45,y+ry*.4),paint(col,a,stroke=1.5*u))
    n=e.get('n',8)
    for i in range(n): an=i*2*math.pi/n+t*.2; c.drawCircle(x+math.cos(an)*rx,y+math.sin(an)*ry,9*u,paint(col,a));c.drawCircle(x+math.cos(an)*rx,y+math.sin(an)*ry,16*u,paint(col,a*.4,blur=8*u))
def split(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);W,H=ctx.W,ctx.H;x=e.get('x',512)*u
    c.drawRect(skia.Rect.MakeLTRB(0,0,x,H),paint(e.get('cl','#301840'),a*.6));c.drawRect(skia.Rect.MakeLTRB(x,0,W,H),paint(e.get('cr','#103838'),a*.6))
    c.drawRect(skia.Rect.MakeLTRB(x-2*u,0,x+2*u,H),paint('#ffffff',a));c.drawRect(skia.Rect.MakeLTRB(x-12*u,0,x+12*u,H),paint('#a0ffff',a*.5,blur=10*u))
def horizon(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);W=ctx.W;y=e.get('y',440)*u;col=e.get('col','#30c0ff')
    c.drawRect(skia.Rect.MakeLTRB(0,y-1*u,W,y+1*u),paint(col,a));c.drawRect(skia.Rect.MakeLTRB(0,y-8*u,W,y+8*u),paint(col,a*.35,blur=8*u))
    if e.get('target'):
        tx=e['target']*u
        for r in (6,12,18): c.drawCircle(tx,y,r*u,paint('#ffffff',a,stroke=1.2*u))
    R=random.Random(9)
    for i in range(e.get('tiles',0)):
        x=R.uniform(0,1024);yy=R.uniform(300,560);s=R.uniform(5,12);c.save();c.translate(x*u,yy*u);c.rotate(R.uniform(0,90)+t*5);c.drawRect(skia.Rect.MakeXYWH(-s*u,-s*u,2*s*u,2*s*u),paint('#8090c0',a*.3));c.restore()
def face(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e.get('x',512)*u,e.get('y',250)*u;s=e.get('s',1)*u
    c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint('#8a9090',a*.6))
    c.drawOval(skia.Rect.MakeLTRB(x-85*s,y-120*s,x+85*s,y+120*s),paint('#c0c4c4',a));c.drawOval(skia.Rect.MakeLTRB(x-85*s,y-120*s,x+85*s,y+120*s),paint('#ffffff',a*.6,stroke=2*s,blur=3*s))
    for dx in (-35,35): c.drawOval(skia.Rect.MakeLTRB(x+(dx-18)*s,y-8*s,x+(dx+18)*s,y+4*s),paint('#404848',a)); c.drawCircle(x+dx*s,y-2*s,4*s,paint('#ffffff',a))
def target(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e['x']*u,e['y']*u;col=e.get('col','#ff4070')
    for r in (12,24,36,48): c.drawCircle(x,y,r*u,paint(col,a*(1-r/70),stroke=2*u))
    c.drawCircle(x,y,50*u,paint(col,a*.3,stroke=6*u,blur=6*u))
    if e.get('check') and t>e['check']:
        cx,cy=x+40*u,y-50*u;c.drawCircle(cx,cy,14*u,paint('#30c060',a));p=skia.Path();p.moveTo(cx-6*u,cy);p.lineTo(cx-1*u,cy+5*u);p.lineTo(cx+7*u,cy-5*u);c.drawPath(p,paint('#ffffff',a,stroke=2.5*u))
def gauge(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e['x']*u,e['y']*u,e.get('r',60)*u;col=e.get('col','#ff4060')
    c.drawArc(skia.Rect.MakeLTRB(x-r,y-r,x+r,y+r),180,180,False,paint('#402040',a,stroke=6*u))
    v=kfi(e.get('v',.7),t);c.drawArc(skia.Rect.MakeLTRB(x-r,y-r,x+r,y+r),180,180*v,False,paint(col,a,stroke=6*u));c.drawArc(skia.Rect.MakeLTRB(x-r,y-r,x+r,y+r),180,180*v,False,paint(col,a*.5,stroke=12*u,blur=6*u))
    an=math.pi*(1+v);line(c,x,y,x+math.cos(an)*r*.8,y+math.sin(an)*r*.8,'#ffffff',a,w=2*u);c.drawCircle(x,y,4*u,paint('#ffffff',a))
    line(c,x-r*1.4,y+8*u,x+r*1.4,y+8*u,col,a,w=1.5*u,glow=4*u)
def tiles(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);col=e.get('col','#5ac0c0')
    for i,(x,y,kind) in enumerate(e['list']):
        aa=a*clamp((t-e['t0']-i*.25)/.3)
        if aa<=0: continue
        c.save();c.translate(x*u,y*u);c.scale(e.get('s',1),e.get('s',1));c.translate(-x*u,-y*u)
        rrect(c,(x-32)*u,(y-32)*u,64*u,64*u,8*u,fill='#0c2028',stroke=col,a=aa,sw=1.5*u)
        if kind=='eye': c.drawOval(skia.Rect.MakeLTRB((x-16)*u,(y-8)*u,(x+16)*u,(y+8)*u),paint(col,aa,stroke=2*u));c.drawCircle(x*u,y*u,4*u,paint(col,aa))
        elif kind=='text':
            for k in range(3): line(c,(x-14)*u,(y-8+k*8)*u,(x+14-k*6)*u,(y-8+k*8)*u,col,aa,w=2*u)
        elif kind=='chat': rrect(c,(x-16)*u,(y-10)*u,32*u,20*u,5*u,stroke=col,a=aa,sw=2*u); [c.drawCircle((x+k*7)*u,y*u,1.8*u,paint(col,aa)) for k in (-1,0,1)]
        elif kind=='card':
            for k in range(2): line(c,(x-18)*u,(y-6+k*10)*u,(x+18)*u,(y-6+k*10)*u,col,aa,w=2*u)
        elif kind=='key': c.drawCircle((x-10)*u,y*u,8*u,paint(col,aa,stroke=2*u));line(c,(x-2)*u,y*u,(x+18)*u,y*u,col,aa,w=2*u);line(c,(x+12)*u,y*u,(x+12)*u,(y+7)*u,col,aa,w=2*u)
        elif kind=='check': p=skia.Path();p.moveTo((x-12)*u,y*u);p.lineTo((x-3)*u,(y+9)*u);p.lineTo((x+14)*u,(y-10)*u);c.drawPath(p,paint(col,aa,stroke=3*u))
        elif kind=='smile': c.drawCircle(x*u,y*u,16*u,paint(col,aa,stroke=2*u));p=skia.Path();p.moveTo((x-7)*u,(y+4)*u);p.quadTo(x*u,(y+11)*u,(x+7)*u,(y+4)*u);c.drawPath(p,paint(col,aa,stroke=2*u))
        elif kind=='flat': c.drawCircle(x*u,y*u,16*u,paint(col,aa,stroke=2*u));line(c,(x-7)*u,(y+6)*u,(x+7)*u,(y+6)*u,col,aa,w=2*u)
        if kind in('smile','flat'): [c.drawCircle((x+k)*u,(y-4)*u,1.8*u,paint(col,aa)) for k in (-6,6)]
        c.restore()
def flash(ctx,e,t,frame):
    if e['t0']<=t<e['t0']+e.get('dur',.034): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#ffffff'),e.get('a',1)))


def spark(ctx,e,t,frame):
    a=env(e,t,.3,.3)
    if a<=0: return
    RICH.motes(ctx.c,ctx.W,ctx.H,t,n=e.get('n',50),color=e.get('color','#5ac0c0'),a=a*.4,seed=e.get('seed',11),speed=e.get('speed',1.3))

EXTRA=dict(spark=spark,bg=bg,sub=sub,head=head,person=person,figure=figure,car=car,phone=phone,clock=clock,chapter=chapter,hbars=hbars,gline=gline,ecg=ecg,orb=orb,web=web,radar=radar,frame=frame_,people=people,table=table,dots=dots,split=split,horizon=horizon,face=face,target=target,gauge=gauge,tiles=tiles,flash=flash)
def _render_sc(ctx,sc,t,frame):
    draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)

def draw(ctx,t,frame,S):
    ctx.beats=S.get('beats',[])
    c=ctx.c; c.clear(skia.ColorBLACK)
    draw_elements(ctx,S.get('under',[]),t,frame,EXTRA)
    RICH.compose_scenes(ctx,S,t,frame,_render_sc,overlays_extra=EXTRA,clear=None,
                        vignette_s=.4,grain_a=.03,band_color='#5ac0c0',design_size=(1024,576))
    if S.get('beat_punch',False) and getattr(ctx,'beats',None):
        RICH.beat_punch(ctx.c,ctx.W,ctx.H,t,ctx.beats,a=min(S.get('punch_a',.05),.05),color=S.get('punch_col','#5ac0c0'),window=.06)
