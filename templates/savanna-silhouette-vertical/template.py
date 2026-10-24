"""#21 草原剪影·竖屏 (savanna-silhouette-vertical) — ref 7698690169096782538《给不会来的狮子站岗》720x1280 99s (Nico). Topic-agnostic.
Two alternating worlds: (1) night bedroom — navy gloom, window (dark / lit warm), bedside lamp, bed + hunched or lying
person silhouette, red LED alarm clock; (2) savanna sunset — orange gradient sky, sun disc, acacia trees, horizon hills,
striped zebra, lion silhouette. Overlays: floating worry phrases (white/grey, drifting), dense dim text wall, red smoke
blob (imagined lion), red ECG strip with label, red dot-matrix counter, top serif white text with [红] highlight + big red
number. Design space 1024 wide (height = 1024*H/W ≈ 1820)."""
import math, random, skia
from engine.core import *
from engine.layers import draw_elements, U

RED='#e8453a'
def prepare(S): pass
def env(e,t,fi=.4,fo=.4): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def HH(ctx): return ctx.H/U(ctx)
def room(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx);h=HH(ctx);a=e.get('a',1)
    c.drawRect(skia.Rect.MakeWH(W,H),skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0,0),skia.Point(0,H)],[hexc('#2a3446'),hexc('#1a2030'),hexc('#0e1016')],[0,.55,1])))
    wx,wy,ww,wh=e.get('win',[60,380,330,380]);lit=kfi(e.get('lit',0),t)
    c.drawRect(skia.Rect.MakeXYWH(wx*u,wy*u,ww*u,wh*u),paint('#2a3448' if not lit else '#c8a060',1))
    if lit: c.drawRect(skia.Rect.MakeXYWH(wx*u,wy*u,ww*u,wh*u),paint('#f0c880',lit*.8))
    for k in (1,2): line(c,(wx+ww*k/3)*u,wy*u,(wx+ww*k/3)*u,(wy+wh)*u,'#10141c',1,w=8*u)
    line(c,wx*u,(wy+wh/2)*u,(wx+ww)*u,(wy+wh/2)*u,'#10141c',1,w=8*u)
    if lit:
        p=skia.Path();p.moveTo(wx*u,(wy+wh)*u);p.lineTo((wx+ww)*u,(wy+wh)*u);p.lineTo((wx+ww+420)*u,(h*.78)*u);p.lineTo((wx+120)*u,(h*.78)*u);p.close();c.drawPath(p,paint('#e0b070',lit*.22,blur=20*u))
    if e.get('lamp',True):
        lx,ly=e.get('lampxy',[830,1000]);on=kfi(e.get('lampon',1),t)
        c.drawCircle(lx*u,ly*u,170*u,paint('#f0b060',.22*on,blur=70*u))
        p=skia.Path();p.moveTo((lx-55)*u,(ly-40)*u);p.lineTo((lx+55)*u,(ly-40)*u);p.lineTo((lx+75)*u,(ly+30)*u);p.lineTo((lx-75)*u,(ly+30)*u);p.close()
        c.drawPath(p,paint('#f8d090' if on>.5 else '#3a3020',1));line(c,lx*u,(ly+30)*u,lx*u,(ly+150)*u,'#1a1410',1,w=6*u)
        c.drawRect(skia.Rect.MakeXYWH((lx-120)*u,(ly+150)*u,240*u,260*u),paint('#120e0c'))
    if e.get('clock'):
        cx,cy=e.get('clockxy',[860,1120]);rrect(c,(cx-75)*u,(cy-35)*u,150*u,70*u,8*u,fill='#1a0c0c',stroke='#3a1a1a',sw=2*u)
        tx=e['clock'] if isinstance(e['clock'],str) else '%02d:%02d'%divmod(int(kfi(e['clock'],t)),60)
        draw_text(c,tx,cx*u,(cy+15)*u,font('mono-bold',40*u),RED,1,glow=10*u)
    by=e.get('bed',1180)
    p=skia.Path();p.moveTo(0,by*u);p.cubicTo(200*u,(by-40)*u,500*u,(by-30)*u,1024*u,(by-10)*u);p.lineTo(1024*u,h*u);p.lineTo(0,h*u);p.close();c.drawPath(p,skia.Paint(AntiAlias=True,Shader=skia.GradientShader.MakeLinear([skia.Point(0,by*u),skia.Point(0,h*u)],[hexc('#2a3040'),hexc('#0c0e14')])))
    line(c,0,by*u,1024*u,(by-10)*u,'#2a3040',.7,w=3*u)
    pose=e.get('pose','sit')
    if pose:
        px,py=e.get('person',[360,by-20]);s=e.get('ps',1);col='#050608'
        if pose=='sit':
            c.drawCircle((px+40*s)*u,(py-290*s)*u,62*s*u,paint(col))
            p=skia.Path();p.moveTo((px-120*s)*u,py*u);p.cubicTo((px-140*s)*u,(py-200*s)*u,(px-40*s)*u,(py-300*s)*u,(px+60*s)*u,(py-240*s)*u)
            p.cubicTo((px+150*s)*u,(py-180*s)*u,(px+170*s)*u,(py-60*s)*u,(px+150*s)*u,py*u);p.close();c.drawPath(p,paint(col))
        elif pose=='lie':
            c.drawCircle(px*u,(py-60*s)*u,58*s*u,paint(col));c.drawOval(skia.Rect.MakeLTRB((px+20*s)*u,(py-80*s)*u,(px+420*s)*u,(py+10*s)*u),paint(col))
    vignette(c,W,H,.55)
def savanna(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx);h=HH(ctx);hy=e.get('horizon',1060);night=kfi(e.get('night',0),t)
    pa=env(e,t,.5,.5) if e.get('panel') else 1
    if pa<=0: return
    c.save()
    if e.get('panel'): y0,y1=e['panel'];c.clipRect(skia.Rect.MakeLTRB(0,y0*u,W,y1*u));c.saveLayerAlpha(None,int(255*pa))
    else: c.saveLayer(None)
    c.drawRect(skia.Rect.MakeWH(W,H),paint('#0a0807'))
    top=e.get('top',560)
    c.drawRect(skia.Rect.MakeLTRB(0,top*u,W,hy*u),skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0,top*u),skia.Point(0,hy*u)],[hexc('#2a1610'),hexc('#8a4428'),hexc('#e09858')],[0,.55,1])))
    sx,sy=e.get('sun',[760,hy-30]);sy=kfi(sy,t) if isinstance(sy,list) else sy
    c.save();c.clipRect(skia.Rect.MakeLTRB(0,top*u,W,hy*u))
    c.drawCircle(sx*u,sy*u,140*u,paint('#ffd090',.35,blur=60*u));c.drawCircle(sx*u,sy*u,46*u,paint('#ffe8b0',.95))
    c.restore()
    p=skia.Path();p.moveTo(0,hy*u)
    for x in range(0,1030,20): p.lineTo(x*u,(hy-14*math.sin(x*.004+1)-6*math.sin(x*.013))*u)
    p.lineTo(W,(hy+40)*u);p.lineTo(0,(hy+40)*u);p.close();c.drawPath(p,paint('#1e100a'))
    c.drawRect(skia.Rect.MakeLTRB(0,(hy+10)*u,W,(hy+260)*u),skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0,hy*u),skia.Point(0,(hy+260)*u)],[hexc('#3a2016'),hexc('#0a0807')])))
    for (tx,ts) in e.get('trees',[[420,1.0],[160,.6],[900,.7]]):
        ty=hy-6;line(c,tx*u,ty*u,tx*u,(ty-90*ts)*u,'#140a06',1,w=7*ts*u)
        for dx in(-1,1): line(c,tx*u,(ty-60*ts)*u,(tx+dx*45*ts)*u,(ty-115*ts)*u,'#140a06',1,w=4*ts*u)
        c.drawOval(skia.Rect.MakeLTRB((tx-110*ts)*u,(ty-150*ts)*u,(tx+110*ts)*u,(ty-105*ts)*u),paint('#140a06'))
    R=random.Random(2)
    for i in range(160):
        x=R.uniform(0,1024);g=R.uniform(8,30);sw=math.sin(t*1.5+x*.02)*3;line(c,x*u,(hy+4)*u,(x+sw)*u,(hy+4-g)*u,'#1a0d08',.9,w=1.2*u)
    if night: c.drawRect(skia.Rect.MakeWH(W,H),paint('#05070c',night*.75))
    if not e.get('panel'): vignette(c,W,H,.55)
    c.restore();c.restore()
def zebra(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('s',1)*(-1 if e.get('flip') else 1);x=e['x']+kfi(e.get('dx',0),t);y=e['y'];run=e.get('run',0)
    sa=abs(s);bob=math.sin(t*12)*6*run
    c.save();c.translate(x*u,(y+bob)*u);c.scale(s*u,sa*u)
    body=skia.Rect.MakeLTRB(-110,-150,90,-70)
    c.drawRoundRect(body,40,40,paint('#f4f0e8',a))
    c.save();c.clipRRect(skia.RRect.MakeRectXY(body,40,40))
    for i in range(-110,100,22): p=skia.Path();p.moveTo(i,-150);p.lineTo(i+14,-150);p.lineTo(i+4,-70);p.lineTo(i-10,-70);p.close();c.drawPath(p,paint('#121010',a))
    c.restore()
    p=skia.Path();p.moveTo(60,-130);p.lineTo(110,-220);p.lineTo(150,-200);p.lineTo(160,-170);p.lineTo(120,-160);p.lineTo(90,-100);p.close();c.drawPath(p,paint('#f4f0e8',a))
    for k in range(4): line(c,70+k*12,-140-k*20,95+k*12,-130-k*18,'#121010',a,w=6)
    for i in range(10): line(c,70+i*7,-150-i*8,62+i*7,-160-i*8,'#121010',a,w=5)
    ph=t*14*run
    for j,lx in enumerate((-90,-60,40,70)):
        sw=math.sin(ph+j*1.6)*25*run
        line(c,lx,-80,lx+sw,0,'#f4f0e8',a,w=13);line(c,lx+sw-2,-40,lx+sw+2,-30,'#121010',a,w=13);line(c,lx+sw,-8,lx+sw,0,'#121010',a,w=13)
    line(c,-110,-130,-135,-80,'#121010',a,w=5)
    c.restore()
def lion(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('s',1)*(-1 if e.get('flip') else 1);x=e['x']+kfi(e.get('dx',0),t);y=e['y'];run=e.get('run',0);col=e.get('col','#0a0605')
    c.save();c.translate(x*u,(y+math.sin(t*10)*5*run)*u);c.scale(s*u,abs(s)*u)
    c.drawOval(skia.Rect.MakeLTRB(-130,-140,100,-60),paint(col,a));c.drawCircle(110,-140,62,paint(col,a));c.drawOval(skia.Rect.MakeLTRB(130,-150,190,-110),paint(col,a))
    p=skia.Path();p.moveTo(-130,-110);p.quadTo(-200,-120,-210,-170);c.drawPath(p,paint(col,a,stroke=8))
    ph=t*12*run
    for j,lx in enumerate((-100,-70,50,80)): sw=math.sin(ph+j*1.7)*35*run;line(c,lx,-80,lx+sw,0,col,a,w=20)
    c.restore()
def worries(ctx,e,t,frame):
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c;u=U(ctx);R=random.Random(e.get('seed',4));lst=e.get('list',[]);y0,y1=e.get('band',[400,1500])
    for i in range(e.get('n',14)):
        tx=lst[i%len(lst)] if lst else '';x=R.uniform(80,940);y=R.uniform(y0,y1)-t*R.uniform(4,12)*e.get('rise',1);sz=R.uniform(*e.get('sizes',[24,40]))
        y=y0+(y-y0)%(y1-y0);al=a*R.uniform(.35,.95)*clamp((t-e['t0']-i*e.get('step',.25))/.5)
        draw_text(c,tx,x*u,y*u,font('serif-bold' if sz>30 else 'serif',sz*u),'#f4eee8' if R.random()<.6 else '#b0a8a0',al,glow=3*u if sz>30 else 0)
def wall(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);R=random.Random(e.get('seed',9));lst=e.get('list',['怎么办'])
    for r in range(e.get('rows',46)):
        y=r*40+20+(t*6)%40;x=-R.uniform(0,200)
        while x<1024:
            tx=R.choice(lst);sz=R.uniform(20,30);draw_text(c,tx,x*u,y*u,font('serif',sz*u),'#e8e0d8',a*R.uniform(.08,.3),align='left');x+=text_width(tx,font('serif',sz*u))/u+R.uniform(20,60)
def smoke(ctx,e,t,frame):
    a=env(e,t,.8,.6)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,s=e['x'],e['y'],e.get('s',1)*(.7+.3*clamp((t-e['t0'])/2));R=random.Random(e.get('seed',2))
    for i in range(46):
        dx=R.uniform(-1,1)*200*s;dy=R.uniform(-1,.6)*120*s;r=R.uniform(30,70)*s
        dx+=math.sin(t*.8+i)*10;c.drawCircle((x+dx)*u,(y+dy)*u,r*u,paint(e.get('col','#d84a3a'),a*.45,blur=r*.25*u))
    c.drawCircle(x*u,y*u,260*s*u,paint(e.get('col','#d84a3a'),a*.15,blur=80*u))
def ecg(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);y=e.get('y',1540);x0,x1=e.get('x0',60),e.get('x1',960);rate=kfi(e.get('rate',1),t);amp=kfi(e.get('amp',40),t);col=e.get('col',RED)
    p=skia.Path();N=180;off=t*rate*1.2
    for i in range(N+1):
        x=x0+(x1-x0)*i/N;ph=(i/N*6+off)%1;v=0
        if .40<ph<.43: v=-1
        elif .43<ph<.47: v=1.6
        elif .47<ph<.5: v=-.5
        yy=y-v*amp;(p.moveTo if i==0 else p.lineTo)(x*u,yy*u)
    c.drawPath(p,paint(col,a*.5,stroke=5*u,blur=4*u));c.drawPath(p,paint(col,a,stroke=2.2*u))
    if e.get('label'): draw_text(c,e['label'],x0*u,(y+55)*u,font('serif',22*u),col,a*.85,align='left')
def matrix(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x0,y0=e.get('x',90),e.get('y',780);cols=e.get('cols',30);n=int(kfi(e.get('n',178),t));sp=e.get('sp',28)
    for i in range(n):
        x=x0+(i%cols)*sp;y=y0+(i//cols)*sp*.8
        c.drawOval(skia.Rect.MakeXYWH(x*u,y*u,sp*.75*u,sp*.4*u),paint(e.get('col',RED),a*.9));c.drawCircle((x+sp*.75)*u,(y+2)*u,sp*.18*u,paint(e.get('col',RED),a*.9))
def text(ctx,e,t,frame):
    a=env(e,t,e.get('fi',.35),e.get('fo',.35))
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('size',40);f=font(e.get('font','serif-bold'),s*u);col=e.get('col','#f4eee8');hl=e.get('hl',RED)
    for li,ln in enumerate(e['text'].split('\n')):
        runs=[];b='';h=False
        for ch in ln:
            if ch in '[]': runs.append((b,hl if h else col)); b=''; h=(ch=='[')
            else: b+=ch
        runs.append((b,hl if h else col))
        draw_rich(c,[r for r in runs if r[0]],e.get('x',512)*u,(e.get('y',300)+li*s*1.4)*u,f,align=e.get('align','center'),a=a,glow=e.get('glow',0)*u)
def flash(ctx,e,t,frame):
    if e['t0']<=t<e['t0']+e.get('dur',.034): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#ffffff'),e.get('a',1)))
def black(ctx,e,t,frame): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#0a0807'),env(e,t)))
EXTRA=dict(room=room,savanna=savanna,zebra=zebra,lion=lion,worries=worries,wall=wall,smoke=smoke,ecg=ecg,matrix=matrix,text=text,flash=flash,black=black)
def draw(ctx,t,frame,S):
    c=ctx.c;c.clear(skia.ColorBLACK)
    draw_elements(ctx,S.get('under',[]),t,frame,EXTRA)
    for s in S['scenes']:
        if s['t0']<=t<s['t1']:
            fi=s.get('fade_in',.5);a=clamp((t-s['t0'])/fi) if fi>0 else 1
            if a<1:
                for p in S['scenes']:
                    if abs(p['t1']-s['t0'])<.05: draw_elements(ctx,p['elements'],min(t,p['t1']-.04),frame,EXTRA)
                c.saveLayerAlpha(None,int(255*a))
            draw_elements(ctx,s['elements'],t,frame,EXTRA)
            if a<1: c.restore()
            if s.get('flash') and t<s['t0']+.034: c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint('#ffffff',1))
    draw_elements(ctx,S.get('overlays',[]),t,frame,EXTRA)
