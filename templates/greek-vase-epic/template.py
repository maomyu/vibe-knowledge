"""#29 希腊陶绘史诗 (greek-vase-epic) — ref 7699046111025057050《奥德赛 两难的抉择》768x576 147.5s (烬序). Topic-agnostic.
Black-figure vase painting look: terracotta field with grain + bottom black subtitle band framed by meander/key-pattern
borders; black silhouettes: sea band with wave scrolls, jagged cliffs, galley (hull eye, mast, sail, oars, rowers, rocking),
figures (warrior with crest/spear/shield, robed woman, red tunic accents, side-step walk), many-necked sea monster with
dog heads, whirlpool spiral (rotating), balance scale (tilting), circular medallion inset, island with palm, sun halo,
flat white clouds, tag label (Greek caps + zh), ship's-log black card, big outlined title. Design space 1024 x 768."""
import math, random, skia
from engine.core import *
from engine.layers import draw_elements, U
CLAY='#c67948';INK='#19130c';CREAM='#efe2c8';ORG='#e0884a'
def prepare(S):
    for sc in S['scenes']:
        for e in sc['elements']: e.setdefault('t0',sc['t0']); e.setdefault('t1',sc['t1'])
def env(e,t,fi=.4,fo=.4): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def rich(c,s,x,y,f,col,hl,a,al='center'):
    runs=[];b='';h=False
    for ch in s:
        if ch in '[]': runs.append((b,hl if h else col)); b=''; h=(ch=='[')
        else: b+=ch
    runs.append((b,hl if h else col));draw_rich(c,[r for r in runs if r[0]],x,y,f,align=al,a=a)
def meander(c,u,y,h,W):
    c.drawRect(skia.Rect.MakeLTRB(0,y*u,W,(y+h)*u),paint(INK));s=h*.7;y0=y+h*.15
    for i in range(int(1024/s)+2):
        x=i*s;p=skia.Path();p.moveTo(x*u,(y0+s)*u);p.lineTo(x*u,y0*u);p.lineTo((x+s*.75)*u,y0*u);p.lineTo((x+s*.75)*u,(y0+s*.6)*u);p.lineTo((x+s*.35)*u,(y0+s*.6)*u);p.lineTo((x+s*.35)*u,(y0+s*.35)*u)
        c.drawPath(p,paint(CLAY,1,stroke=max(1,h*.1)*u))
def vase(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx);top=e.get('band',640);col=e.get('col',CLAY)
    c.drawRect(skia.Rect.MakeWH(W,H),skia.Paint(Shader=skia.GradientShader.MakeRadial(skia.Point(W*.5,H*.35),W*.7,[hexc('#d88a58'),hexc(col),hexc('#8a4a28')],[0,.6,1])))
    R=random.Random(1)
    for i in range(500): c.drawCircle(R.uniform(0,W),R.uniform(0,top*u),R.uniform(.5,1.6)*u,paint('#5a3018',R.uniform(.05,.18)))
    if e.get('dark'): c.drawRect(skia.Rect.MakeWH(W,H),paint(INK,e['dark']))
def band(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx);top=e.get('y',640)
    meander(c,u,top-26,22,W);c.drawRect(skia.Rect.MakeLTRB(0,(top-4)*u,W,H),paint(INK));line(c,0,(top-2)*u,W,(top-2)*u,CLAY,.8,w=1.5*u)
    if e.get('topband'): meander(c,u,0,18,W)
def sea(ctx,e,t,frame):
    c=ctx.c;W=ctx.W;u=U(ctx);y=e.get('y',560);bot=e.get('bot',614);off=(t*e.get('speed',20))%60
    c.drawRect(skia.Rect.MakeLTRB(0,y*u,W,bot*u),paint(INK))
    for row in range(2):
        yy=y+14+row*20;p=skia.Path()
        for i in range(-1,20):
            x=i*60-off+row*30;p.moveTo(x*u,yy*u);p.cubicTo((x+15)*u,(yy-12)*u,(x+35)*u,(yy-12)*u,(x+40)*u,(yy-2)*u);p.cubicTo((x+42)*u,(yy+4)*u,(x+34)*u,(yy+6)*u,(x+32)*u,yy*u)
        c.drawPath(p,paint(CLAY,.8,stroke=1.6*u))
def cliff(ctx,e,t,frame):
    a=env(e,t,.4,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);side=e.get('side','left');w=e.get('w',120);R=random.Random(e.get('seed',2));H=e.get('h',620);p=skia.Path()
    xe=0 if side=='left' else 1024;sg=1 if side=='left' else -1;p.moveTo(xe*u,0)
    for i in range(14): y=i*H/13;p.lineTo((xe+sg*(w+R.uniform(-30,30)))*u,y*u)
    p.lineTo(xe*u,H*u);p.close();c.drawPath(p,paint(INK,a))
    for i in range(6): y=R.uniform(40,H-40);x=xe+sg*R.uniform(20,w-30);line(c,x*u,y*u,(x+sg*R.uniform(10,30))*u,(y+R.uniform(10,30))*u,CLAY,a*.4,w=1.2*u)
def ship(ctx,e,t,frame):
    a=env(e,t,.4,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x=kfi(e.get('x',400),t);y=e.get('y',560);s=e.get('s',1);rk=math.sin(t*1.3)*e.get('rock',2)
    c.save();c.translate(x*u,y*u);c.rotate(rk);c.scale(s,s);S=lambda v:v*u
    p=skia.Path();p.moveTo(S(-260),S(-40));p.cubicTo(S(-200),S(10),S(180),S(10),S(230),S(-30));p.lineTo(S(260),S(-70));p.cubicTo(S(250),S(-40),S(240),S(-45),S(220),S(-48));p.lineTo(S(-230),S(-48));p.cubicTo(S(-250),S(-70),S(-280),S(-80),S(-290),S(-110));p.cubicTo(S(-270),S(-70),S(-265),S(-55),S(-260),S(-40));p.close()
    c.drawPath(p,paint(INK,a));c.drawCircle(S(200),S(-30),S(6),paint(CLAY,a));c.drawCircle(S(200),S(-30),S(2.5),paint(INK,a))
    for i in range(14):
        ox=-200+i*30;ph=math.sin(t*3+i*.3)*8;line(c,S(ox),S(-30),S(ox-20+ph),S(25),INK,a,w=S(2.5))
    if e.get('rowers',True):
        for i in range(7): c.drawCircle(S(-150+i*50),S(-66),S(9),paint(INK,a));c.drawRect(skia.Rect.MakeXYWH(S(-158+i*50),S(-58),S(16),S(12)),paint(INK,a))
    if e.get('mast',True):
        line(c,0,S(-48),0,S(-330),INK,a,w=S(6));line(c,S(-130),S(-300),S(130),S(-300),INK,a,w=S(5))
        if e.get('sail',True):
            q=skia.Path();q.moveTo(S(-125),S(-298));q.lineTo(S(125),S(-298));q.lineTo(S(115),S(-150));q.cubicTo(S(40),S(-140),S(-40),S(-140),S(-115),S(-150));q.close();c.drawPath(q,paint(e.get('sailcol',INK),a*.95))
            for k in range(1,6): line(c,S(-125+k*42),S(-298),S(-115+k*38),S(-148),CLAY,a*.35,w=S(1))
        line(c,0,S(-330),S(250),S(-60),INK,a,w=S(1.5));line(c,0,S(-330),S(-260),S(-48),INK,a,w=S(1.5))
    c.restore()
def figure(ctx,e,t,frame):
    a=env(e,t,.4,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x=kfi(e.get('x',500),t);y=e.get('y',560);s=e.get('s',1);k=e.get('kind','warrior');face=e.get('face',1);ph=math.sin(t*e.get('speed',0)*math.pi*2)
    c.save();c.translate(x*u,y*u);c.scale(face*s,s);S=lambda v:v*u;P=paint(INK,a);red=e.get('red','#a83a28')
    if k=='woman':
        p=skia.Path();p.moveTo(S(-10),S(-150));p.lineTo(S(14),S(-150));p.lineTo(S(36),S(0));p.lineTo(S(-34),S(0));p.close();c.drawPath(p,paint(red,a))
        for i in range(5): line(c,S(-28+i*3),S(-30-i*25),S(30-i*3),S(-30-i*25),INK,a*.8,w=S(2.5))
        c.drawRect(skia.Rect.MakeXYWH(S(-12),S(-200),S(26),S(55)),P);c.drawCircle(S(2),S(-218),S(15),P);line(c,S(10),S(-185),S(60),S(-160),INK,a,w=S(6));line(c,S(5),S(-185),S(55),S(-170),INK,a,w=S(5))
        c.drawCircle(S(-6),S(-228),S(9),P)
    else:
        for d in(1,-1): line(c,0,S(-90),S(d*22*(1+.6*ph*d)),S(-45),INK,a,w=S(11));line(c,S(d*22*(1+.6*ph*d)),S(-45),S(d*18+ph*10*d),0,INK,a,w=S(9))
        c.drawRect(skia.Rect.MakeXYWH(S(-24),S(-110),S(48),S(28)),paint(red,a))
        for i in range(5): line(c,S(-22+i*11),S(-110),S(-22+i*11),S(-82),INK,a*.7,w=S(1.5))
        p=skia.Path();p.moveTo(S(-20),S(-112));p.lineTo(S(-26),S(-180));p.lineTo(S(26),S(-180));p.lineTo(S(20),S(-112));p.close();c.drawPath(p,P)
        c.drawCircle(S(4),S(-198),S(17),P)
        if e.get('helmet',True): p=skia.Path();p.addArc(skia.Rect.MakeLTRB(S(-14),S(-218),S(22),S(-190)),180,180);c.drawPath(p,paint(CREAM,a));c.drawRect(skia.Rect.MakeXYWH(S(-12),S(-224),S(30),S(6)),paint(CREAM,a*.8))
        arm=e.get('arm','spear')
        if arm=='spear': line(c,S(10),S(-170),S(50),S(-130),INK,a,w=S(8));line(c,S(-10),S(-320),S(70),S(40),INK,a,w=S(3.5))
        elif arm=='point': line(c,S(10),S(-170),S(80),S(-165),INK,a,w=S(8))
        elif arm=='shield': c.drawCircle(S(30),S(-140),S(36),P);c.drawCircle(S(30),S(-140),S(26),paint(CLAY,a,stroke=S(2)))
        elif arm=='bound': line(c,S(-20),S(-170),S(-20),S(-110),INK,a,w=S(8));line(c,S(-40),S(-400),S(-40),S(0),INK,a,w=S(10))
    if e.get('halo'):
        for i in range(24): an=i/24*math.tau;line(c,S(4+30*math.cos(an)),S(-198+30*math.sin(an)),S(4+50*math.cos(an)),S(-198+50*math.sin(an)),CREAM,a*.9,w=S(2.5))
    c.restore()
def monster(ctx,e,t,frame):
    a=env(e,t,.4,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);ox,oy=e.get('x',80),e.get('y',200);n=e.get('n',6);L=kfi(e.get('reach',1),t)*e.get('len',520);R=random.Random(3)
    for i in range(n):
        an=-.55+i*(1.0/max(1,n-1))+math.sin(t*1.2+i)*.05;ex=ox+L*math.cos(an)*R.uniform(.75,1);ey=oy+L*math.sin(an)*.8+120*i/n
        p=skia.Path();p.moveTo(ox*u,(oy+i*10)*u);p.cubicTo((ox+L*.3)*u,(oy-40+i*30)*u,(ex-L*.3)*u,(ey+40)*u,ex*u,ey*u);c.drawPath(p,paint(INK,a,stroke=(16-i)*u))
        hd=skia.Path();hd.moveTo((ex-10)*u,(ey-12)*u);hd.lineTo((ex+46)*u,(ey-4)*u);hd.lineTo((ex+36)*u,(ey+6)*u);hd.lineTo((ex+48)*u,(ey+14)*u);hd.lineTo((ex-8)*u,(ey+12)*u);hd.close();c.drawPath(hd,paint(INK,a))
        c.drawCircle((ex+10)*u,(ey-4)*u,2.5*u,paint('#e84030',a))
    if e.get('maw'):
        mx,my,ms=e['maw'];op=.5+.5*math.sin(t*3);c.save();c.translate(mx*u,my*u);c.scale(ms,ms)
        p=skia.Path();p.moveTo(-300*u,-60*u);p.lineTo(250*u,(-40-op*40)*u);p.lineTo(280*u,0);p.lineTo(250*u,(40+op*40)*u);p.lineTo(-300*u,60*u);p.close();c.drawPath(p,paint(INK,a))
        q=skia.Path();q.moveTo(-60*u,0);q.lineTo(250*u,(-30-op*35)*u);q.lineTo(250*u,(30+op*35)*u);q.close();c.drawPath(q,paint('#8a2018',a))
        for i in range(9): xx=-40+i*32;tri=skia.Path();tri.moveTo(xx*u,(-6-i*4*op)*u);tri.lineTo((xx+12)*u,(-6-i*4*op)*u);tri.lineTo((xx+6)*u,(10-i*3*op)*u);tri.close();c.drawPath(tri,paint(CREAM,a))
        c.drawCircle(60*u,-50*u,14*u,paint('#e84030',a));c.restore()
def whirl(ctx,e,t,frame):
    a=env(e,t,.5,.4)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e.get('x',512),e.get('y',380),e.get('r',260);sp=t*e.get('spin',.8)
    c.drawOval(skia.Rect.MakeLTRB((x-r)*u,(y-r*.45)*u,(x+r)*u,(y+r*.45)*u),paint(INK,a))
    for k in range(3):
        p=skia.Path()
        for i in range(400):
            th=i/400*6*math.pi+sp+k*2.09;rr=r*(1-i/400)*.95;(p.moveTo if i==0 else p.lineTo)((x+rr*math.cos(th))*u,(y+rr*.45*math.sin(th))*u)
        c.drawPath(p,paint(CLAY,a*.8,stroke=1.6*u))
    c.drawOval(skia.Rect.MakeLTRB((x-r*.18)*u,(y-r*.08)*u,(x+r*.18)*u,(y+r*.08)*u),paint('#000000',a))
def scale(ctx,e,t,frame):
    a=env(e,t,.4,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w=e.get('x',660),e.get('y',260),e.get('w',360);tl=kfi(e.get('tilt',0),t)+math.sin(t*1.5)*1.5
    line(c,x*u,y*u,x*u,(y+300)*u,INK,a,w=5*u);c.drawRect(skia.Rect.MakeXYWH((x-60)*u,(y+300)*u,120*u,10*u),paint(INK,a))
    c.drawCircle(x*u,(y-14)*u,12*u,paint(INK,a))
    th=math.radians(tl);dx=w/2*math.cos(th);dy=w/2*math.sin(th)
    line(c,(x-dx)*u,(y-dy)*u,(x+dx)*u,(y+dy)*u,INK,a,w=5*u)
    for sg,lb in ((-1,e.get('left')),(1,e.get('right'))):
        px,py=x+sg*dx,y+sg*dy;line(c,px*u,py*u,(px-40)*u,(py+120)*u,INK,a,w=1.5*u);line(c,px*u,py*u,(px+40)*u,(py+120)*u,INK,a,w=1.5*u)
        p=skia.Path();p.moveTo((px-50)*u,(py+120)*u);p.lineTo((px+50)*u,(py+120)*u);p.quadTo(px*u,(py+150)*u,(px-50)*u,(py+120)*u);c.drawPath(p,paint(INK,a))
        if lb: draw_text(c,lb,px*u,(py+108)*u,font('serif-bold',18*u),INK,a)
def medal(ctx,e,t,frame):
    a=env(e,t,.4,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e['x'],e['y'],e.get('r',90);k=ease_out_cubic(clamp((t-e['t0'])/.5));r*=k
    c.drawCircle(x*u,y*u,(r+8)*u,paint(INK,a));c.drawCircle(x*u,y*u,r*u,paint('#d88a58',a));c.drawCircle(x*u,y*u,(r+3)*u,paint(CLAY,a,stroke=1.5*u))
    if e.get('inner') and k>.6:
        c.save();p=skia.Path();p.addCircle(x*u,y*u,r*u);c.clipPath(p,doAntiAlias=True);sub=dict(e['inner'],t0=e['t0'],t1=e['t1']);EXTRA[sub['type']](ctx,sub,t,frame);c.restore()
    if e.get('from'): fx,fy=e['from'];line(c,fx*u,fy*u,(x-r*.7)*u,(y+r*.7)*u,INK,a,w=2*u)
def island(ctx,e,t,frame):
    a=env(e,t,.4,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e.get('x',700),e.get('y',560),e.get('w',360),e.get('h',130)
    p=skia.Path();p.moveTo((x-w/2)*u,y*u);p.cubicTo((x-w*.3)*u,(y-h)*u,(x+w*.3)*u,(y-h)*u,(x+w/2)*u,y*u);p.close();c.drawPath(p,paint(INK,a))
    if e.get('palm',True):
        px,py=x+w*.15,y-h*.72;line(c,px*u,py*u,(px+8)*u,(py-90)*u,INK,a,w=5*u)
        for i in range(7): an=math.pi*(1.05+i*.15);q=skia.Path();q.moveTo((px+8)*u,(py-90)*u);q.quadTo((px+8+40*math.cos(an))*u,(py-110+20*math.sin(an))*u,(px+8+65*math.cos(an))*u,(py-80+15*abs(math.sin(an)))*u);c.drawPath(q,paint(INK,a,stroke=4*u))
def clouds(ctx,e,t,frame):
    a=env(e,t,.5,.4)
    if a<=0: return
    c=ctx.c;u=U(ctx);off=t*e.get('speed',6)
    for (x,y,s) in e.get('items',[[300,120,1],[750,90,1.2]]):
        xx=(x+off)%1200-80
        for dx,dy,r in((0,0,40),(45,-15,48),(95,0,38),(50,15,40)): c.drawCircle((xx+dx*s)*u,(y+dy*s)*u,r*s*u,paint(CREAM,a*.95))
        for k in range(3): line(c,(xx-30*s)*u,(y+30*s+k*8)*u,(xx+130*s)*u,(y+30*s+k*8)*u,CREAM,a*.6,w=1.5*u)
def sun(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e.get('x',512),e.get('y',150),e.get('r',40)
    c.drawCircle(x*u,y*u,r*u,paint(CREAM,a))
    for i in range(16): an=i/16*math.tau+t*.2;line(c,(x+(r+8)*math.cos(an))*u,(y+(r+8)*math.sin(an))*u,(x+(r+26)*math.cos(an))*u,(y+(r+26)*math.sin(an))*u,CREAM,a,w=3*u)
def tag(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e['x'],e['y']
    c.drawRect(skia.Rect.MakeXYWH((x-40)*u,(y-20)*u,80*u,40*u),paint(INK,a*.9));c.drawRect(skia.Rect.MakeXYWH((x-37)*u,(y-17)*u,74*u,34*u),paint(CLAY,a*.6,stroke=1*u))
    draw_text(c,e.get('gr',''),x*u,(y-3)*u,font('serif',9*u),CLAY,a);draw_text(c,e.get('zh',''),x*u,(y+12)*u,font('serif-bold',11*u),CREAM,a)
def logcard(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e.get('x',300),e.get('y',120),e.get('w',424),e.get('h',200)
    c.drawRect(skia.Rect.MakeXYWH(x*u,y*u,w*u,h*u),paint(INK,a*.95));c.drawRect(skia.Rect.MakeXYWH((x+6)*u,(y+6)*u,(w-12)*u,(h-12)*u),paint(CLAY,a*.6,stroke=1.2*u))
    draw_text(c,e.get('title','航海日志'),(x+w/2)*u,(y+42)*u,font('serif-bold',26*u),CREAM,a)
    for i,ln in enumerate(e.get('lines',[])):
        k=clamp((t-e['t0']-.4-i*.4)/.3);rich(c,ln,(x+w/2)*u,(y+82+i*32)*u,font('serif-bold',20*u),CREAM,ORG,a*k)
    if e.get('note'): draw_text(c,e['note'],(x+w/2)*u,(y+h-14)*u,font('serif',10*u),'#a89070',a)
def title(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('size',40);f=font(e.get('font','serif-bold'),s*u)
    for i,ln in enumerate(e['text'].split('\n')):
        x,y=e.get('x',512)*u,(e.get('y',100)+i*s*1.15)*u
        for dx,dy in ((-2,0),(2,0),(0,-2),(0,2),(2,2),(-2,2)): rich(c,ln,x+dx*u,y+dy*u,f,INK,INK,a,e.get('align','center'))
        rich(c,ln,x,y,f,e.get('col',CREAM),e.get('hl',ORG),a,e.get('align','center'))
def sub(ctx,e,t,frame):
    a=env(e,t,.2,.2)
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('size',22);y=e.get('y',680)
    for i,ln in enumerate(e['text'].split('\n')): rich(c,ln,512*u,(y+i*s*1.4)*u,font('serif-vf',s*u,900),CREAM,ORG,a)
def tint(ctx,e,t,frame): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#000000'),env(e,t,e.get('fi',.3),e.get('fo',.3))))
def flash(ctx,e,t,frame):
    if e['t0']<=t<e['t0']+e.get('dur',.034): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#ffffff'),e.get('a',1)))
EXTRA=dict(vase=vase,band=band,sea=sea,cliff=cliff,ship=ship,figure=figure,monster=monster,whirl=whirl,scale=scale,medal=medal,island=island,clouds=clouds,sun=sun,tag=tag,logcard=logcard,title=title,sub=sub,tint=tint,flash=flash)
def draw(ctx,t,frame,S):
    c=ctx.c;c.clear(skia.ColorBLACK)
    draw_elements(ctx,S.get('under',[]),t,frame,EXTRA)
    for s in S['scenes']:
        if s['t0']<=t<s['t1']:
            fi=s.get('fade_in',.4);a=clamp((t-s['t0'])/fi) if fi>0 else 1
            if a<1:
                for p in S['scenes']:
                    if abs(p['t1']-s['t0'])<.05: draw_elements(ctx,p['elements'],min(t,p['t1']-.04),frame,EXTRA)
                c.saveLayerAlpha(None,int(255*a))
            draw_elements(ctx,s['elements'],t,frame,EXTRA)
            if a<1: c.restore()
            if s.get('flash') and t<s['t0']+.034: c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint('#ffffff',1))
    draw_elements(ctx,S.get('overlays',[]),t,frame,EXTRA)
