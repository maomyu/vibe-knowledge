"""#23 进化剪影横屏 (evolution-silhouette) — ref 7696111289969560872《从海里爬上岸的那条鱼》1280x720 93.6s (码点小人). Topic-agnostic.
Full-width side-scroller of flat silhouette layers: per-era gradient sky (+ sun/moon disc, god-rays, haze band), parallax
hills / tree rows (fern, palm, round, acacia, spruce) / city skyline / ruins scrolling at layer speed, optional sea band
(water gradient + weeds), a walking silhouette (fish, lizard, ape, man, spear, rifle, staff, adult+child) with walk
cycle and x keyframes, beasts (mammoth, dino), mushroom cloud, fire wall, curtain bars, poison smog, smoke plumes,
bottom bilingual small subtitles (EN line + 中文 line), centred black-card title. Design space 1024 x 576."""
import math, random, skia
from engine.core import *
from engine.layers import draw_elements, U
import engine.richness as RICH

def prepare(S):
    for sc in S['scenes']:
        for e in sc['elements']: e.setdefault('t0',sc['t0']); e.setdefault('t1',sc['t1'])
def env(e,t,fi=.4,fo=.4): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*((t-a)/(b-a))
    return keys[-1][1]
def lg(c,y0,y1,cols,W,x0=0):
    st=[i/(len(cols)-1) for i in range(len(cols))]
    c.drawRect(skia.Rect.MakeLTRB(x0,y0,W,y1),skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0,y0),skia.Point(0,y1)],[hexc(k) for k in cols],st)))
def sky(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx);a=e.get('a',1)
    c.saveLayerAlpha(None,int(255*a)) if a<1 else c.save()
    lg(c,0,H,e.get('cols',['#6a5a8a','#c88a9a','#f0c0a0']),W)
    if e.get('sun'):
        sx,sy,r=e['sun'];c.drawCircle(sx*u,sy*u,r*3*u,paint(e.get('suncol','#fff0d0'),.3,blur=r*1.5*u));c.drawCircle(sx*u,sy*u,r*u,paint(e.get('suncol','#fff0d0'),.95))
    if e.get('rays'):
        sx,sy=e.get('rayxy',[512,300]);R=random.Random(4)
        for i in range(14):
            an=math.pi*(1+i/13);w=R.uniform(.03,.07);p=skia.Path();p.moveTo(sx*u,sy*u)
            for s in(-w,w): p.lineTo((sx+1400*math.cos(an+s))*u,(sy+1400*math.sin(an+s))*u)
            p.close();c.drawPath(p,paint('#ffffff',e['rays']*R.uniform(.3,1),blur=12*u))
    if e.get('stars'):
        R=random.Random(9)
        for i in range(60): c.drawCircle(R.uniform(0,1024)*u,R.uniform(0,250)*u,1.2*u,paint('#ffffff',e['stars']*R.uniform(.3,1)))
    if e.get('haze'):
        hy,hc,ha=e['haze'];c.drawRect(skia.Rect.MakeLTRB(0,(hy-60)*u,W,(hy+50)*u),paint(hc,ha,blur=30*u))
    c.restore()
def _scroll(e,t): return kfi(e.get('scroll',0),t) if isinstance(e.get('scroll',0),list) else e.get('scroll',0)*t
def hills(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx);a=e.get('a',1);y=e.get('y',420);amp=e.get('amp',30);fr=e.get('freq',.006);off=_scroll(e,t);sd=e.get('seed',1)
    p=skia.Path();p.moveTo(0,H)
    for x in range(0,1040,8):
        X=x+off;yy=y-amp*(math.sin(X*fr+sd)*.6+math.sin(X*fr*2.7+sd*2)*.3+math.sin(X*fr*6.1)*.1)
        p.lineTo(x*u,yy*u)
    p.lineTo(W,H);p.close();c.drawPath(p,paint(e.get('col','#2a2038'),a))
    if e.get('volcano'):
        vx,vh=e['volcano'];vx-=off;q=skia.Path();q.moveTo((vx-180)*u,y*u);q.lineTo((vx-30)*u,(y-vh)*u);q.lineTo((vx+30)*u,(y-vh)*u);q.lineTo((vx+200)*u,y*u);q.close();c.drawPath(q,paint(e.get('col','#2a2038'),a))
        for i in range(5): c.drawCircle((vx+i*14+math.sin(t+i)*6)*u,(y-vh-25-i*30)*u,(16+i*8)*u,paint('#c0a0b0',a*.25,blur=8*u))
def ground(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx);y=e.get('y',500)
    lg(c,y*u,H,[e.get('col','#100c14'),e.get('col2',e.get('col','#100c14'))],W)
    if e.get('grass'):
        R=random.Random(3);off=_scroll(e,t)
        for i in range(260):
            x=(R.uniform(0,1200)-off)%1100-40;g=R.uniform(4,e['grass']);line(c,x*u,y*u,(x+R.uniform(-3,3))*u,(y-g)*u,e.get('col','#100c14'),1,w=1.4*u)
def sea(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx);y=kfi(e.get('y',260),t);x1=kfi(e.get('x1',1024),t)
    c.save();c.clipRect(skia.Rect.MakeLTRB(0,y*u,x1*u,H))
    lg(c,y*u,H,e.get('cols',['#3a8a8a','#1a5a6a','#0a2a3a']),W)
    for i in range(3): c.drawRect(skia.Rect.MakeLTRB(0,(y-2+i*1.5)*u,W,(y+1+i*1.5)*u),paint('#a0e0e0',.3))
    R=random.Random(5);off=_scroll(e,t)
    for i in range(e.get('weeds',14)):
        x=(R.uniform(0,1100)-off)%1100-40;b=H/u-R.uniform(0,60);hh=R.uniform(40,120)
        p=skia.Path();p.moveTo(x*u,b*u)
        for k in range(1,9): p.lineTo((x+math.sin(t*1.2+k*.7+i)*6*k/8)*u,(b-hh*k/8)*u)
        c.drawPath(p,paint('#0a2a30',.9,stroke=3*u))
    c.restore()
def _tree(c,u,x,y,s,kind,col):
    P=lambda: paint(col)
    if kind=='fern':
        line(c,x*u,y*u,x*u,(y-110*s)*u,col,1,w=4*s*u)
        for k in range(10):
            an=math.pi*(1.05+k*.09);L=60*s;p=skia.Path();p.moveTo(x*u,(y-110*s)*u);p.quadTo((x+L*.5*math.cos(an))*u,(y-110*s+L*.5*math.sin(an)-15*s)*u,(x+L*math.cos(an))*u,(y-110*s+L*math.sin(an)+12*s)*u);c.drawPath(p,paint(col,1,stroke=2.2*s*u))
    elif kind=='palm':
        p=skia.Path();p.moveTo(x*u,y*u);p.quadTo((x+15*s)*u,(y-70*s)*u,(x+5*s)*u,(y-140*s)*u);c.drawPath(p,paint(col,1,stroke=5*s*u))
        for k in range(7):
            an=math.pi*(1+k/6);q=skia.Path();q.moveTo((x+5*s)*u,(y-140*s)*u);q.quadTo((x+5*s+40*s*math.cos(an))*u,(y-160*s+30*s*math.sin(an))*u,(x+5*s+70*s*math.cos(an))*u,(y-120*s+20*s*abs(math.sin(an)))*u);c.drawPath(q,paint(col,1,stroke=4*s*u))
    elif kind=='round':
        line(c,x*u,y*u,x*u,(y-70*s)*u,col,1,w=6*s*u)
        for dx,dy,r in((0,-110,50),(-35,-85,35),(38,-88,38),(0,-140,32)): c.drawCircle((x+dx*s)*u,(y+dy*s)*u,r*s*u,P())
    elif kind=='acacia':
        line(c,x*u,y*u,x*u,(y-70*s)*u,col,1,w=6*s*u);c.drawOval(skia.Rect.MakeLTRB((x-80*s)*u,(y-100*s)*u,(x+80*s)*u,(y-65*s)*u),P())
    elif kind=='spruce':
        p=skia.Path();p.moveTo(x*u,(y-150*s)*u);p.lineTo((x+35*s)*u,y*u);p.lineTo((x-35*s)*u,y*u);p.close();c.drawPath(p,P())
    elif kind=='pole':
        line(c,x*u,y*u,x*u,(y-150*s)*u,col,1,w=3*s*u);line(c,x*u,(y-150*s)*u,(x+25*s)*u,(y-150*s)*u,col,1,w=3*s*u)
def trees(ctx,e,t,frame):
    c=ctx.c;u=U(ctx);off=_scroll(e,t);col=e.get('col','#1a1420');a=e.get('a',1)
    if a<1: c.saveLayerAlpha(None,int(255*a))
    for it in e.get('items',[]):
        x,s,k=it[0],it[1],it[2] if len(it)>2 else e.get('kind','fern');span=e.get('wrap',0)
        X=x-off
        if span: X=(X+100)%span-100
        _tree(c,u,X,e.get('y',500),s,k,col)
    if a<1: c.restore()
def city(ctx,e,t,frame):
    c=ctx.c;u=U(ctx);a=e.get('a',1);y=e.get('y',480);off=_scroll(e,t);R=random.Random(e.get('seed',7));x=-off%60-60;col=e.get('col','#2a2a34');ruin=e.get('ruin',0)
    while x<1060:
        w=R.uniform(25,70);h=R.uniform(30,e.get('hmax',160))
        if ruin and R.random()<ruin: h*=.4
        c.drawRect(skia.Rect.MakeXYWH(x*u,(y-h)*u,w*u,h*u),paint(col,a))
        if e.get('lights'):
            for k in range(int(h/14)):
                if R.random()<.35: c.drawRect(skia.Rect.MakeXYWH((x+4+R.uniform(0,w-10))*u,(y-h+6+k*14)*u,4*u,5*u),paint(e['lights'],a*.8))
        x+=w+R.uniform(0,10)
def walker(ctx,e,t,frame):
    a=env(e,t,e.get('fi',.3),e.get('fo',.3))
    if a<=0: return
    c=ctx.c;u=U(ctx);x=kfi(e.get('x',400),t);y=kfi(e.get('y',500),t);s=e.get('s',1);kind=e.get('kind','man');col=e.get('col','#08060a');sp=e.get('speed',1.6)
    ph=t*sp*math.pi*2 if e.get('walk',True) else 0;P=paint(col,a)
    def stick(x0,y0,x1,y1,w): line(c,x0*u,y0*u,x1*u,y1*u,col,a,w=w*s*u)
    if kind=='fish':
        c.drawOval(skia.Rect.MakeLTRB((x-60*s)*u,(y-14*s)*u,(x+60*s)*u,(y+12*s)*u),P);tw=math.sin(ph)*8*s
        p=skia.Path();p.moveTo((x-55*s)*u,y*u);p.lineTo((x-85*s)*u,(y-16*s+tw)*u);p.lineTo((x-85*s)*u,(y+16*s+tw)*u);p.close();c.drawPath(p,P)
        for dx in(-10,20): stick(x+dx*s,y+8*s,x+(dx-8+math.sin(ph+dx)*6)*s,y+22*s,3)
    elif kind in('lizard','dino'):
        L=1.6 if kind=='dino' else 1
        c.drawOval(skia.Rect.MakeLTRB((x-50*s*L)*u,(y-30*s*L)*u,(x+45*s*L)*u,(y-8*s*L)*u),P);c.drawCircle((x+55*s*L)*u,(y-30*s*L)*u,11*s*L*u,P);stick(x+40*s*L,y-22*s*L,x+55*s*L,y-30*s*L,10*L)
        p=skia.Path();p.moveTo((x-45*s*L)*u,(y-25*s*L)*u);p.quadTo((x-90*s*L)*u,(y-20*s*L)*u,(x-120*s*L)*u,(y-8*s*L)*u);p.lineTo((x-45*s*L)*u,(y-12*s*L)*u);p.close();c.drawPath(p,P)
        for k,dx in enumerate((-30,25)):
            sw=math.sin(ph+k*math.pi)*10;stick(x+dx*s*L,y-14*s*L,x+(dx+sw)*s*L,y,5*L)
    elif kind=='mammoth':
        c.drawOval(skia.Rect.MakeLTRB((x-70*s)*u,(y-120*s)*u,(x+60*s)*u,(y-40*s)*u),P);c.drawCircle((x-55*s)*u,(y-100*s)*u,30*s*u,P)
        p=skia.Path();p.moveTo((x-80*s)*u,(y-100*s)*u);p.quadTo((x-100*s)*u,(y-40*s)*u,(x-85*s)*u,(y-25*s)*u);c.drawPath(p,paint(col,a,stroke=10*s*u))
        p=skia.Path();p.moveTo((x-75*s)*u,(y-80*s)*u);p.quadTo((x-130*s)*u,(y-60*s)*u,(x-120*s)*u,(y-110*s)*u);c.drawPath(p,paint('#f0ece0',a,stroke=4*s*u))
        for dx in(-50,-25,20,45): stick(x+dx*s,y-50*s,x+dx*s,y,14)
    else:
        sw=math.sin(ph);hy=y-150*s if kind!='child' else y-80*s;sc=1 if kind!='child' else .55
        hunch={'ape':30,'man':0}.get(kind,4)*sc
        hip=(x,y-75*s*sc);neck=(x+hunch*s,y-135*s*sc)
        for k in(1,-1): stick(hip[0],hip[1],hip[0]+sw*k*18*s*sc,y-35*s*sc,9*sc);stick(hip[0]+sw*k*18*s*sc,y-35*s*sc,hip[0]+sw*k*24*s*sc-4*s,y,8*sc)
        stick(hip[0],hip[1],neck[0],neck[1],16*sc);c.drawCircle((neck[0]+4*s*sc)*u,(neck[1]-16*s*sc)*u,13*s*sc*u,P)
        hx,hyy=neck[0]+10*s*sc,neck[1]+35*s*sc
        if kind=='spear':
            stick(neck[0],neck[1]+6*s,neck[0]+30*s,neck[1]+10*s,6);stick(x-60*s,neck[1]+20*s,x+130*s,neck[1]-10*s,3)
        elif kind=='rifle':
            stick(neck[0],neck[1]+6*s,neck[0]+30*s,neck[1]+15*s,6);stick(x-10*s,neck[1]+25*s,x+70*s,neck[1]+5*s,5)
        elif kind=='staff':
            stick(neck[0],neck[1]+6*s,hx+20*s,hyy,6);stick(hx+20*s,hyy-20*s,hx+55*s,y,3)
        else:
            for k in(1,-1): stick(neck[0],neck[1]+6*s*sc,neck[0]-sw*k*16*s*sc,hyy+10*s*sc,6*sc)
        if e.get('child'):
            walker(ctx,dict(e,kind='child',child=False,x=x+e['child']*s,t0=e['t0'],t1=e['t1']),t,frame)
def mushroom(ctx,e,t,frame):
    a=env(e,t,1,.5)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e['x'],e.get('y',480);g=e.get('s',1)*(.5+.5*clamp((t-e['t0'])/3));col=e.get('col','#c09888');R=random.Random(3)
    c.drawRect(skia.Rect.MakeLTRB((x-40*g)*u,(y-260*g)*u,(x+40*g)*u,y*u),paint(col,a*.8,blur=10*u))
    for i in range(40):
        an=R.uniform(0,6.28);r=R.uniform(0,1);c.drawCircle((x+math.cos(an)*r*170*g)*u,(y-290*g+math.sin(an)*r*80*g)*u,R.uniform(30,60)*g*u,paint(col,a*.5,blur=6*u))
    c.drawCircle(x*u,(y-280*g)*u,300*g*u,paint('#ffd0a0',a*.18,blur=90*u))
def fire(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);y=e.get('y',576);R=random.Random(8)
    for i in range(90):
        x=R.uniform(-20,1040);h=R.uniform(60,e.get('h',220))*(.8+.2*math.sin(t*6+i));w=R.uniform(15,40)
        p=skia.Path();p.moveTo((x-w)*u,y*u);p.quadTo((x-w*.3)*u,(y-h*.6)*u,(x+math.sin(t*3+i)*10)*u,(y-h)*u);p.quadTo((x+w*.3)*u,(y-h*.6)*u,(x+w)*u,y*u);p.close()
        c.drawPath(p,paint(R.choice(['#e05020','#f08030','#f0b050']),a*.8))
def bars(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);R=random.Random(e.get('seed',2));off=_scroll(e,t)
    for i in range(e.get('n',18)):
        x=(R.uniform(0,1100)-off)%1100-40;w=R.uniform(6,26);c.drawRect(skia.Rect.MakeXYWH(x*u,0,w*u,ctx.H),paint(e.get('col','#3a2a24'),a*R.uniform(.5,1)))
    for b in e.get('banners',[]):
        bx,bw=b;c.drawRect(skia.Rect.MakeXYWH(bx*u,40*u,bw*u,260*u),paint('#a02020',a));c.drawCircle((bx+bw/2)*u,120*u,bw*.3*u,paint('#100808',a))
def smog(ctx,e,t,frame):
    a=env(e,t,1,1)
    if a<=0: return
    c=ctx.c;u=U(ctx);R=random.Random(4)
    for i in range(30): c.drawCircle((R.uniform(-50,600)+t*8)*u,R.uniform(300,560)*u,R.uniform(60,150)*u,paint(e.get('col','#90d040'),a*.25,blur=40*u))
def smoke(ctx,e,t,frame):
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c;u=U(ctx);off=_scroll(e,t)
    for (x,y,s) in e.get('items',[[300,400,1]]):
        for i in range(10): c.drawCircle((x-off+i*8*s+math.sin(t+i)*5)*u,(y-i*24*s-(t*15)%24)*u,(10+i*5)*s*u,paint(e.get('col','#3a3030'),a*.6,blur=6*u))
def sub(ctx,e,t,frame):
    a=env(e,t,.15,.15)
    if a<=0: return
    c=ctx.c;u=U(ctx);y=e.get('y',530);col=e.get('col','#f0ece8')
    sz=e.get('size',13);sh=e.get('shadow','#000000');sa=e.get('shadow_a',.75)
    L=[(e.get('en'),y,'sans-bold',.95),(e.get('zh'),y+sz*1.35,'sans',.9)]
    for tx,yy,fn,aa in L:
        if not tx: continue
        f=font(fn,sz*u)
        if sh:
            for dx,dy in((-1,0),(1,0),(0,-1),(0,1),(1,1),(-1,1),(1,-1),(-1,-1)): draw_text(c,tx,(512+dx*1.2)*u,(yy+dy*1.2)*u,f,sh,a*sa*.6)
            draw_text(c,tx,512*u,(yy+1.5)*u,f,sh,a*sa,glow=3*u)
        draw_text(c,tx,512*u,yy*u,f,col,a*aa)
def title(ctx,e,t,frame):
    a=env(e,t,.8,.8)
    if a<=0: return
    c=ctx.c;u=U(ctx)
    draw_text(c,e.get('zh',''),512*u,e.get('y',290)*u,font('serif',e.get('size',20)*u),'#c8c4c0',a)
    if e.get('en'): draw_text(c,e['en'],512*u,(e.get('y',290)+e.get('size',20)*1.1)*u,font('serif',e.get('size',20)*.55*u),'#8a8682',a)
def tint(ctx,e,t,frame): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#000000'),env(e,t,e.get('fi',.5),e.get('fo',.5))))
def flash(ctx,e,t,frame):
    if e['t0']<=t<e['t0']+e.get('dur',.034): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#ffffff'),e.get('a',1)))



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

EXTRA=dict(spark=spark,sky=sky,hills=hills,ground=ground,sea=sea,trees=trees,city=city,walker=walker,mushroom=mushroom,fire=fire,bars=bars,smog=smog,smoke=smoke,sub=sub,title=title,tint=tint,flash=flash)

def _render_sc(ctx,sc,t,frame):
    draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)

def draw(ctx,t,frame,S):
    ctx.beats=S.get('beats',[])
    c=ctx.c; c.clear(skia.ColorBLACK)
    RICH.compose_scenes(ctx,S,t,frame,_render_sc,overlays_extra=EXTRA,clear=None,
                        vignette_s=.35,grain_a=.03,band_color='#c8a860',design_size=(1024,576))
    if S.get('beat_punch',False) and getattr(ctx,'beats',None):
        RICH.beat_punch(ctx.c,ctx.W,ctx.H,t,ctx.beats,a=min(S.get('punch_a',.05),.05),color=S.get('punch_col','#c8a860'),window=.06)
