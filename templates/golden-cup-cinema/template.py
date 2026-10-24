"""#16 金杯剧场 (golden-cup-cinema) — ref 7693418695520196836《何为享乐主义》1920x1080 168.8s (叁号暗房 Logos). Topic-agnostic.
Dark warm-brown stage (#080707) lit by spotlights / god-rays; polished gold goblets (gradient, liquid fill, pour stream,
drips), copper mug, plates (grapes/bread/meat), candles, labelled pedestals; flat black silhouettes (kneel / stand /
arms-up / sit) with floor shadows; cracked desert at sunset with pale sun; portal ring with moon; garden wall + arched gate
+ Latin plaque + trees; long table; radial light burst with confetti; ghost year numbers; top-left chapter tag; top-centre
serif subtitles (white + [gold] keywords). Design space 1024x576."""
import math, random, numpy as np, skia
from engine.core import *
from engine.layers import draw_elements, U

GOLD='#e5b97a'; WHITE='#f2ede4'
def prepare(S): pass
def env(e,t,fi=.5,fo=.5): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def lg(x0,y0,x1,y1,cols,pos=None): return skia.GradientShader.MakeLinear([skia.Point(x0,y0),skia.Point(x1,y1)],[hexc(c) for c in cols],pos)
def pg(shader,a=1.):
    p=skia.Paint(AntiAlias=True); p.setShader(shader); p.setAlphaf(a); return p
def stage(ctx,e,t,frame):
    c=ctx.c;u=U(ctx);W,H=ctx.W,ctx.H;k=e.get('kind','dark');a=env(e,t,0,0);fy=e.get('floor',400)*u
    SK={'dark':('#0a0908','#15110e','#0c0a09','#16120f'),'desert':('#6a4a30','#e8b880','#c88a58','#8a5a38'),'dusk':('#1a1820','#c89060','#2a2420','#3a3028'),
        'night':('#05060a','#0c0e16','#0a0a0c','#121214'),'warm':('#1a120c','#5a3a20','#2a1c12','#3a2818'),'stone':('#2a2620','#4a4238','#5a5248','#3a342c')}[k]
    c.drawRect(skia.Rect.MakeWH(W,fy),pg(lg(0,0,0,fy,[SK[0],SK[1]]),a)); c.drawRect(skia.Rect.MakeLTRB(0,fy,W,H),pg(lg(0,fy,0,H,[SK[2],SK[3]]),a))
    if e.get('sun'): x,y,r=e['sun']; c.drawCircle(x*u,y*u,r*3*u,paint('#fff0d0',.35*a,blur=r*2*u)); c.drawCircle(x*u,y*u,r*u,paint('#f8f0e0',.95*a))
    if e.get('cracks'):
        R=random.Random(4); p=paint('#2a160c',.8*a,stroke=1.6*u)
        for i in range(260):
            x=R.uniform(-100,1124); yy=R.uniform(0,1)**1.6; y=fy/u+yy*(576-fy/u); L=10+yy*60
            pth=skia.Path(); pth.moveTo(x*u,y*u)
            for j in range(3): x+=R.uniform(-1,1)*L; y+=R.uniform(-.3,.3)*L*.4; pth.lineTo(x*u,y*u)
            c.drawPath(pth,p)
    if e.get('stars'):
        R=random.Random(2)
        for i in range(e['stars']): c.drawCircle(R.uniform(0,W),R.uniform(0,fy),R.uniform(.4,1.4)*u,paint('#ffffff',R.uniform(.2,.8)*a))
    vignette(c,W,H,e.get('vig',.6))
def spot(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y1,w=e['x'],e.get('y1',470),e.get('w',150);top=e.get('top',w*.3); I=kfi(e.get('i',1),t)
    p=skia.Path(); p.moveTo((x-top/2)*u,0); p.lineTo((x+top/2)*u,0); p.lineTo((x+w/2)*u,y1*u); p.lineTo((x-w/2)*u,y1*u); p.close()
    c.drawPath(p,pg(lg(0,0,0,y1*u,['#fff0d8','#fff0d800']),.13*a*I)); c.drawOval(skia.Rect.MakeXYWH((x-w*.55)*u,(y1-14)*u,w*1.1*u,28*u),paint('#fff0d8',.22*a*I,blur=10*u))
def goblet(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,s=e['x'],e['y'],e.get('s',1)*u;kind=e.get('col','gold');fl=kfi(e.get('fill',.8),t)
    G={'gold':['#5a3a14','#e8c078','#fff0c0','#b07a30','#4a2a10'],'black':['#050505','#3a3a3a','#6a6a6a','#202020','#050505'],'copper':['#4a2010','#c07040','#f0b080','#8a4020','#3a1808']}[kind]
    X,Y=x*u,y*u; rw,bh=70*s,80*s   # rim half width, bowl height. (x,y)=rim centre
    if e.get('glow',True): c.drawCircle(X,Y+40*s,120*s,paint('#e8b060',.18*a,blur=60*s))
    bowl=skia.Path(); bowl.moveTo(X-rw,Y); bowl.cubicTo(X-rw,Y+bh*.8,X-rw*.35,Y+bh,X-8*s,Y+bh*1.05); bowl.lineTo(X+8*s,Y+bh*1.05); bowl.cubicTo(X+rw*.35,Y+bh,X+rw,Y+bh*.8,X+rw,Y); bowl.close()
    c.drawPath(bowl,pg(lg(X-rw,0,X+rw,0,G,[0,.3,.45,.75,1]),a))
    stem=skia.Path(); stem.addRect(skia.Rect.MakeLTRB(X-5*s,Y+bh*1.05,X+5*s,Y+bh*1.9)); c.drawPath(stem,pg(lg(X-5*s,0,X+5*s,0,G[1:4]),a))
    c.drawOval(skia.Rect.MakeLTRB(X-12*s,Y+bh*1.42,X+12*s,Y+bh*1.5),pg(lg(X-12*s,0,X+12*s,0,G[1:4]),a))
    base=skia.Path(); base.moveTo(X-8*s,Y+bh*1.85); base.quadTo(X-40*s,Y+bh*1.95,X-45*s,Y+bh*2.05); base.lineTo(X+45*s,Y+bh*2.05); base.quadTo(X+40*s,Y+bh*1.95,X+8*s,Y+bh*1.85); base.close()
    c.drawPath(base,pg(lg(X-45*s,0,X+45*s,0,G,[0,.3,.45,.75,1]),a))
    c.drawOval(skia.Rect.MakeLTRB(X-rw,Y-9*s,X+rw,Y+9*s),paint(G[4],a)); c.drawOval(skia.Rect.MakeLTRB(X-rw,Y-9*s,X+rw,Y+9*s),paint(G[2],a,stroke=2*s))
    if fl>0:
        lq=e.get('liquid','#e8b868'); c.drawOval(skia.Rect.MakeLTRB(X-rw*.93,Y-7*s+(1-fl)*10*s,X+rw*.93,Y+7*s+(1-fl)*10*s),paint(lq,a*min(1,fl*2)))
    if e.get('drips'):
        for i,dx in enumerate((-.6,-.2,.35,.7)):
            L=(8+12*((i*7)%3))*s*(1+.2*math.sin(t+i)); c.drawLine(X+dx*rw,Y+5*s,X+dx*rw,Y+5*s+L,paint(G[2],a,stroke=3*s))
    st=e.get('stream')
    if st and st[0]<=t<st[1]:
        c.drawLine(X,0,X,Y,paint('#f0c880',.9*a,stroke=4*s)); c.drawLine(X,0,X,Y,paint('#f0c880',.4*a,stroke=14*s,blur=6*s))
def mug(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('s',1)*u;X,Y=e['x']*u,e['y']*u
    p=skia.Path(); p.moveTo(X-24*s,Y); p.lineTo(X+24*s,Y); p.lineTo(X+19*s,Y+45*s); p.lineTo(X-19*s,Y+45*s); p.close()
    c.drawPath(p,pg(lg(X-24*s,0,X+24*s,0,['#4a2010','#c07040','#f0a070','#8a4020','#3a1808'],[0,.3,.45,.75,1]),a))
    c.drawOval(skia.Rect.MakeLTRB(X-24*s,Y-5*s,X+24*s,Y+5*s),paint('#2a1408',a)); c.drawOval(skia.Rect.MakeLTRB(X-24*s,Y-5*s,X+24*s,Y+5*s),paint('#e09060',a,stroke=1.5*s))
    if e.get('steam'):
        for i in range(3):
            pth=skia.Path(); x0=X+(i-1)*9*s; pth.moveTo(x0,Y-8*s)
            for j in range(1,12): pth.lineTo(x0+5*s*math.sin(j*.8+t*2+i),Y-8*s-j*4*s)
            c.drawPath(pth,paint('#ffffff',.25*a,stroke=1.5*s,blur=1*s))
def plate(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('s',1)*u;X,Y=e['x']*u,e['y']*u;w=e.get('w',60)*s
    c.drawOval(skia.Rect.MakeLTRB(X-w,Y-w*.25,X+w,Y+w*.25),paint('#b88a40',a)); c.drawOval(skia.Rect.MakeLTRB(X-w*.8,Y-w*.18,X+w*.8,Y+w*.18),paint('#6a4a20',a))
    k=e.get('kind','grapes'); R=random.Random(int(e['x']))
    if k=='grapes':
        for i in range(22): c.drawCircle(X+R.uniform(-.5,.5)*w,Y-R.uniform(0,.35)*w,5*s,paint(R.choice(['#6a4aa0','#8a6ac8','#4a3080']),a))
    elif k=='bread': c.drawOval(skia.Rect.MakeLTRB(X-w*.6,Y-w*.35,X+w*.5,Y+w*.05),pg(lg(0,Y-w*.35,0,Y,['#e8c890','#8a6038']),a))
    elif k=='meat': c.drawOval(skia.Rect.MakeLTRB(X-w*.6,Y-w*.3,X+w*.6,Y+w*.05),paint('#6a2a1a',a))
    elif k=='bowl':
        c.drawOval(skia.Rect.MakeLTRB(X-w*.7,Y-w*.15,X+w*.7,Y+w*.15),paint('#f0eee8',a))
def candle(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);X,Y,h=e['x']*u,e['y']*u,e.get('h',120)*u
    c.drawLine(X,Y,X,Y-h,paint('#a07a40',a,stroke=3*u)); c.drawRect(skia.Rect.MakeLTRB(X-5*u,Y-h-30*u,X+5*u,Y-h),paint('#f0ece0',a))
    fl=1+.1*math.sin(t*13+X); c.drawOval(skia.Rect.MakeLTRB(X-3*u,Y-h-44*u*fl,X+3*u,Y-h-30*u),paint('#ffe0a0',a)); c.drawCircle(X,Y-h-38*u,18*u,paint('#ffc070',.25*a,blur=10*u))
def pedestal(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e['x'],e.get('y',450),e.get('w',105),e.get('h',125);lit=kfi(e.get('lit',.5),t)
    c.drawRect(skia.Rect.MakeLTRB((x-w/2)*u,(y-h)*u,(x+w/2)*u,y*u),pg(lg((x-w/2)*u,0,(x+w/2)*u,0,['#0e0e10','#2a2a2e','#141416']),a))
    c.drawOval(skia.Rect.MakeLTRB((x-w/2)*u,(y-h-10)*u,(x+w/2)*u,(y-h+10)*u),paint('#3a3a40',a*(.6+.4*lit)))
    if e.get('label'): draw_text(c,e['label'],x*u,(y-h/2+5)*u,font('serif',10*u),'#c8c0b0',a*(.5+.5*lit))
def person(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('s',1)*u;X,Y=e['x']*u,e['y']*u;pose=e.get('pose','stand');ink=e.get('col','#050403');P=paint(ink,a);L=lambda w:(lambda p:(p.setStrokeCap(skia.Paint.kRound_Cap),p)[1])(paint(ink,a,stroke=w*s))
    c.drawOval(skia.Rect.MakeLTRB(X-60*s,Y-8*s,X+60*s,Y+8*s),paint('#000000',.4*a,blur=8*s))
    if pose=='kneel':
        c.drawCircle(X-5*s,Y-118*s,13*s,P); c.drawLine(X-8*s,Y-100*s,X-15*s,Y-45*s,L(26)); c.drawLine(X-15*s,Y-35*s,X+20*s,Y-8*s,L(16)); c.drawLine(X-15*s,Y-35*s,X-45*s,Y-4*s,L(16)); c.drawLine(X-45*s,Y-4*s,X-80*s,Y-2*s,L(12))
        c.drawLine(X-2*s,Y-90*s,X+25*s,Y-70*s,L(10)); c.drawLine(X+25*s,Y-70*s,X+40*s,Y-78*s,L(9))
    elif pose=='arms':
        c.drawCircle(X,Y-150*s,12*s,P); c.drawLine(X,Y-130*s,X,Y-60*s,L(26)); c.drawLine(X-6*s,Y-60*s,X-8*s,Y,L(12)); c.drawLine(X+6*s,Y-60*s,X+8*s,Y,L(12))
        for sx in (-1,1): c.drawLine(X+sx*10*s,Y-125*s,X+sx*30*s,Y-170*s,L(8)); c.drawLine(X+sx*30*s,Y-170*s,X+sx*24*s,Y-210*s,L(7))
    elif pose=='sit':
        c.drawCircle(X,Y-95*s,11*s,P); c.drawLine(X,Y-80*s,X,Y-30*s,L(28)); c.drawLine(X-14*s,Y-75*s,X+14*s,Y-75*s,L(14))
    else:
        c.drawCircle(X,Y-140*s,12*s,P); c.drawLine(X,Y-122*s,X,Y-60*s,L(26)); c.drawLine(X-6*s,Y-60*s,X-8*s,Y,L(11)); c.drawLine(X+6*s,Y-60*s,X+10*s,Y,L(11))
        c.drawLine(X-12*s,Y-115*s,X-16*s,Y-65*s,L(8)); c.drawLine(X+12*s,Y-115*s,X+18*s,Y-70*s,L(8))
def rays(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);X,Y=e.get('x',512)*u,e.get('y',300)*u;n=e.get('n',26);rot=t*e.get('spin',.03)
    c.drawCircle(X,Y,90*u,paint('#fff0c8',.5*a,blur=40*u))
    for i in range(n):
        th=rot+i*2*math.pi/n; w=.035+.02*math.sin(i*3.1); p=skia.Path(); p.moveTo(X,Y)
        p.lineTo(X+1400*u*math.cos(th-w),Y+1400*u*math.sin(th-w)); p.lineTo(X+1400*u*math.cos(th+w),Y+1400*u*math.sin(th+w)); p.close()
        c.drawPath(p,skia.Paint(AntiAlias=True,Shader=skia.GradientShader.MakeRadial(skia.Point(X,Y),900*u,[hexc('#f8e0b0',.22*a),hexc('#f8e0b0',0)])))
    if e.get('confetti'):
        R=random.Random(6)
        for i in range(160):
            ang=R.uniform(0,6.28); sp=R.uniform(.2,1); d=((t*60*sp+R.uniform(0,600))%600)*u
            c.drawRect(skia.Rect.MakeXYWH(X+math.cos(ang)*d,Y+math.sin(ang)*d+d*.15,2.5*u,1.4*u),paint(R.choice(['#f0c060','#e06060','#60a0e0','#f0f0f0']),.8*a))
def portal(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);X,Y,r=e.get('x',512)*u,e.get('y',290)*u,e.get('r',100)*u*kfi(e.get('scale',1),t)
    c.drawCircle(X,Y,r,paint('#0a1020',a)); c.drawCircle(X,Y,r*1.06,paint('#6a4030',a,stroke=r*.1)); c.drawCircle(X,Y,r*1.12,paint('#c09060',.6*a,stroke=1.5*u))
    if e.get('moon'): mx,my=e['moon']; c.drawCircle(X+mx*r,Y+my*r,r*.1,paint('#f0f0f0',a,blur=1*u)); c.drawCircle(X+mx*r,Y+my*r,r*.25,paint('#ffffff',.2*a,blur=8*u))
    if e.get('text'): draw_text(c,e['text'],X,Y+r*.15,font('serif-bold',r*.38),'#f2ede4',a,spacing=r*.1)
def wall(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);y=e.get('y',370)*u;W=ctx.W;H=ctx.H
    c.drawRect(skia.Rect.MakeLTRB(0,y,W,H),pg(lg(0,y,0,H,['#5a5040','#2a241c']),a))
    for r_ in range(12):
        yy=y+r_*22*u; c.drawLine(0,yy,W,yy,paint('#1a160f',.6*a,stroke=1*u))
        for k in range(0,30): xx=(k*60+(r_%2)*30)*u; c.drawLine(xx,yy,xx,yy+22*u,paint('#1a160f',.5*a,stroke=1*u))
    gx=e.get('gate',512)*u; gw=56*u; p=skia.Path(); p.moveTo(gx-gw,H); p.lineTo(gx-gw,y+60*u); p.arcTo(skia.Rect.MakeLTRB(gx-gw,y+10*u,gx+gw,y+110*u),180,180,False); p.lineTo(gx+gw,H); p.close()
    c.drawPath(p,paint('#e8c890',.35*a*kfi(e.get('glow',1),t),blur=10*u)); c.drawPath(p,paint('#d8c8a0',.7*a,stroke=1.5*u))
    if e.get('plaque'):
        rrect(c,gx-115*u,y-28*u,230*u,45*u,2*u,fill=hexc('#5a5448',a),stroke=hexc('#8a8270',a),sw=1*u)
        for i,ln in enumerate(e['plaque']): draw_text(c,ln,gx,y+(-10+i*15)*u,font('garamond',9*u),'#e8e0d0',a)
    for tx,sx in e.get('trees',[[150,1],[870,-1]]): tree(c,u,tx,y/u+20,a,sx)
def tree(c,u,x,y,a,sx=1):
    ink=paint('#0a0806',a); p=skia.Path(); p.moveTo((x-6)*u,y*u); p.quadTo((x+4*sx)*u,(y-80)*u,(x-10*sx)*u,(y-150)*u); p.lineTo((x-4*sx)*u,(y-150)*u); p.quadTo((x+14*sx)*u,(y-80)*u,(x+6)*u,y*u); p.close(); c.drawPath(p,ink)
    R=random.Random(int(x))
    for i in range(60): c.drawCircle((x+R.gauss(0,60))*u,(y-165+R.gauss(0,25))*u,R.uniform(6,14)*u,paint('#14180e',.9*a))
    for i in range(6): th=R.uniform(-2.6,-.5); c.drawLine((x-4*sx)*u,(y-140)*u,(x+math.cos(th)*80)*u,(y-150+math.sin(th)*40)*u,paint('#0a0806',a,stroke=3*u))
def table(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w=e.get('x',512),e.get('y',405),e.get('w',360)
    p=skia.Path(); p.moveTo((x-w/2)*u,y*u); p.lineTo((x+w/2)*u,y*u); p.lineTo((x+w/2+20)*u,(y+12)*u); p.lineTo((x-w/2-20)*u,(y+12)*u); p.close(); c.drawPath(p,paint('#7a4a28',a))
    c.drawRect(skia.Rect.MakeLTRB((x-w/2-20)*u,(y+12)*u,(x+w/2+20)*u,(y+20)*u),paint('#3a2010',a))
    for lx in (x-w/2,x+w/2-8): c.drawRect(skia.Rect.MakeLTRB(lx*u,(y+20)*u,(lx+8)*u,(y+90)*u),paint('#2a1608',a))
def ticket(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);c.save();c.translate(e.get('x',260)*u,e.get('y',150)*u);c.rotate(e.get('rot',-8))
    rrect(c,-50*u,-28*u,100*u,56*u,3*u,fill=hexc('#e8c050',a)); draw_text(c,e.get('text','LOTTERY'),0,4*u,font('mono-bold',9*u),'#4a3010',a); c.restore()
def halo(ctx,e,t,frame):
    a=env(e,t)
    if a>0: u=U(ctx); ctx.c.drawOval(skia.Rect.MakeXYWH((e['x']-e.get('w',80)/2)*u,(e['y']-e.get('h',40)/2)*u,e.get('w',80)*u,e.get('h',40)*u),paint(e.get('col','#e8b868'),.45*a,blur=14*u))
def flash(ctx,e,t,frame):
    if e['t0']<=t<e['t0']+e.get('dur',.034): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#ffffff'),e.get('a',.9)))
def ghost(ctx,e,t,frame):
    a=env(e,t)
    if a>0: u=U(ctx); draw_text(ctx.c,e['text'],e.get('x',512)*u,e.get('y',380)*u,font('garamond',e.get('size',120)*u),'#ffffff',.06*a)
def vortex(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);X,Y=e.get('x',512)*u,e.get('y',300)*u
    for i in range(6): r=(60+i*70)*u; c.drawOval(skia.Rect.MakeLTRB(X-r*1.6,Y-r*.5,X+r*1.6,Y+r*.5),paint('#c09050',(.35-i*.04)*a,stroke=(2+i)*u))
    R=random.Random(3)
    for i in range(30): th=R.uniform(0,6.28)+t*R.uniform(.3,1); r=R.uniform(20,90)*u; c.drawCircle(X+math.cos(th)*r,Y+math.sin(th)*r*.6,R.uniform(2,6)*u,paint('#d8a868',.7*a,stroke=1.5*u))
def tag(ctx,e,t,frame):
    a=env(e,t,0,0)
    if a<=0: return
    u=U(ctx); draw_text(ctx.c,e.get('text','享乐主义'),27*u,26*u,font('serif-bold',15*u),'#f2ede4',a,align='left'); draw_text(ctx.c,e.get('en','Hedonism'),27*u,38*u,font('garamond-italic',8*u),'#a09888',a,align='left')
def sub(ctx,e,t,frame):
    a=env(e,t,.35,.35)
    if a<=0: return
    c=ctx.c;u=U(ctx);y=e.get('y',40);sz=e.get('size',15);f=font('serif-bold',sz*u)
    for i,ln in enumerate(e['text'].split('\n')):
        runs=[];b='';g=False
        for ch in ln:
            if ch in '[]': runs.append((b,g)); b=''; g=(ch=='[')
            else: b+=ch
        runs.append((b,g)); tw=sum(f.measureText(r) for r,_ in runs); x=e.get('x',512)*u-tw/2
        for r,g in runs:
            if r: draw_text(c,r,x,(y+i*e.get('lh',sz*1.65))*u,f,GOLD if g else e.get('col',WHITE),a,align='left',glow=6*u if g else 0,glow_color='#a07030'); x+=f.measureText(r)
def big(ctx,e,t,frame):
    a=env(e,t)
    if a>0: u=U(ctx); draw_text(ctx.c,e['text'],e.get('x',512)*u,e.get('y',300)*u,font(e.get('font','serif-bold'),e.get('size',30)*u),e.get('col',WHITE),a,glow=e.get('glow',0)*u,glow_color=GOLD)
def pool(ctx,e,t,frame):
    """giant gold liquid surface (close-up of goblet rim) with ripples + pouring column"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);W=ctx.W;cy=e.get('y',380)*u
    c.drawRect(skia.Rect.MakeLTRB(0,cy,W,ctx.H),pg(lg(0,cy,0,ctx.H,['#c89040','#6a4416']),a))
    c.drawOval(skia.Rect.MakeLTRB(-60*u,cy-120*u,W+60*u,cy+90*u),pg(lg(0,cy-120*u,0,cy+90*u,['#f0c070','#a06a28']),a))
    R=random.Random(8)
    for i in range(70):
        x=R.uniform(0,1024);y=R.uniform(-90,70);ph=t*1.5+i
        c.drawOval(skia.Rect.MakeXYWH((x-18)*u,(cy/u+y-3)*u,(36+8*math.sin(ph))*u,6*u),paint('#fff0c0',.35*a,stroke=1.2*u))
    c.drawOval(skia.Rect.MakeLTRB(-60*u,cy-120*u,W+60*u,cy+90*u),paint('#f8e0a8',.8*a,stroke=3*u))
    if e.get('stream',True):
        x=e.get('sx',580)*u; c.drawRect(skia.Rect.MakeLTRB(x-40*u,0,x+40*u,cy-20*u),pg(lg(x-40*u,0,x+40*u,0,['#8a5a20','#f8d890','#c08a40']),a))
        for i in range(25): c.drawCircle(x+R.uniform(-90,90)*u,cy-R.uniform(0,90)*u-((t*80+i*30)%90)*u,R.uniform(2,5)*u,paint('#fff0c0',.7*a))
EXTRA={'flash':flash,'halo':halo,'stage':stage,'spot':spot,'goblet':goblet,'mug':mug,'plate':plate,'candle':candle,'pedestal':pedestal,'person':person,'rays':rays,'portal':portal,'wall':wall,'table':table,'ticket':ticket,'ghost':ghost,'vortex':vortex,'tag':tag,'sub':sub,'big':big,'pool':pool}
def draw(ctx,t,frame,S):
    c=ctx.c; c.clear(hexc('#080707'))
    for sc in S['scenes']:
        if sc['t0']-1e-6<=t<sc['t1']:
            k=fade_env(t,sc['t0'],sc['t1'],sc.get('fade_in',.6),sc.get('fade_out',.6))
            if k<=0: continue
            c.saveLayerAlpha(None,int(255*k)); draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA); c.restore()
    draw_elements(ctx,S.get('overlays',[]),t,frame,EXTRA)
