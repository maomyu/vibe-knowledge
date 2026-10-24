"""#26 器官信息卡 (organ-infocard-dark) — ref 7698983598958841097《养胃误区》1920x1080 135.8s (我是风流帅). Topic-agnostic.
Dark tinted HUD stage (wine / teal / navy, faint grid, FILE / MYTH corner labels). Left: glossy vector illustration
(organ = stomach blob with glow, glass of ice water, chili, rice bowl + steam, thermometer); microscope circle cutaway
(green mucus with bubbles over pink villi); right/centre: rounded data panels (title + rows), tissue strip with
receptor pins, mini bars, bell-curve pair, temperature path with labelled dots; red tilted "误区" stamp, struck-through
myth title, three tilted food cards, habit card grid (icon + title + sub + No.), action cards around a central organ,
pill bubble, caption line. Design space 1024 x 576."""
import math, random, skia
from engine.core import *
from engine.layers import draw_elements, U
RED='#e8505a';GRN='#4ad08a';GOLD='#f0c050';CREAM='#f2ece4';MUTE='#a8a098'
BGS={'wine':('#24141a','#160c10'),'teal':('#10261f','#0a1612'),'navy':('#10202c','#0a121a'),'dark':('#1a1816','#0e0d0c')}
def prepare(S):
    for sc in S['scenes']:
        for e in sc['elements']: e.setdefault('t0',sc['t0']); e.setdefault('t1',sc['t1'])
def env(e,t,fi=.35,fo=.3): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def slide(e,t,d=24):
    k=clamp((t-e['t0'])/.45);return (1-ease_out_cubic(k))*d
def rich(c,s,x,y,f,col,hl,a,al='center'):
    runs=[];b='';h=False
    for ch in s:
        if ch in '[]': runs.append((b,hl if h else col)); b=''; h=(ch=='[')
        else: b+=ch
    runs.append((b,hl if h else col));draw_rich(c,[r for r in runs if r[0]],x,y,f,align=al,a=a)
def bg(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx);a,b=BGS.get(e.get('kind','wine'),BGS['wine'])
    c.drawRect(skia.Rect.MakeWH(W,H),skia.Paint(Shader=skia.GradientShader.MakeRadial(skia.Point(W/2,H*.45),W*.75,[hexc(a),hexc(b)])))
    for x in range(0,1025,32): line(c,x*u,0,x*u,H,'#ffffff',.025,w=1*u)
    for y in range(0,577,32): line(c,0,y*u,W,y*u,'#ffffff',.025,w=1*u)
    if e.get('glow'): gx,gy,gc=e['glow'];c.drawCircle(gx*u,gy*u,260*u,paint(gc,.18,blur=120*u))
    if e.get('hud'):
        l,r=e['hud'] if isinstance(e['hud'],list) else (e['hud'],'')
        c.drawCircle(30*u,38*u,3*u,paint(RED,.9));draw_text(c,l,40*u,41*u,font('sans',9*u),MUTE,.7,align='left')
        if r: draw_text(c,r,994*u,41*u,font('mono',9*u),MUTE,.6,align='right')
    vignette(c,W,H,.45)
def title(ctx,e,t,frame):
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('size',30);f=font(e.get('font','sans-bold'),s*u);x,y=e.get('x',512),e.get('y',70);al=e.get('align','center')
    rich(c,e['text'],x*u,y*u,f,e.get('col',CREAM),e.get('hl',RED),a,al)
    if e.get('strike'):
        w=text_width(e['text'].replace('[','').replace(']',''),f)/u;x0=x-(w/2 if al=='center' else 0);k=clamp((t-e.get('strike_t',e['t0']+.4))/.35)
        if k>0:
            sc=e.get('strike_col','#ff1a2a');yy=(y-s*.32)*u
            line(c,(x0-4)*u,yy,(x0-4+(w+8)*k)*u,yy,'#120608',a*.8,w=s*.16*u);line(c,(x0-4)*u,yy,(x0-4+(w+8)*k)*u,yy,sc,a,w=s*.09*u)
def badge(ctx,e,t,frame):
    a=env(e,t,.15,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e['x'],e['y'];k=clamp((t-e['t0'])/.2);sc=1+(1-k)*.6
    c.save();c.translate(x*u,y*u);c.rotate(e.get('rot',-6));c.scale(sc,sc)
    tx=e.get('text','误区');f=font('sans-bold',e.get('size',22)*u);w=text_width(tx,f)/u+24
    rrect(c,-w/2*u,-18*u,w*u,36*u,4*u,fill='#5a1820',stroke=e.get('col',RED),a=a,sw=2*u);draw_text(c,tx,0,8*u,f,e.get('col','#ff6a70'),a)
    c.restore()
def stomach(ctx,e,t,frame):
    a=env(e,t,.5,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,s=e.get('x',512),e.get('y',300),e.get('s',1)*(1+.02*math.sin(t*2));col=e.get('col','#f06a70')
    P=lambda px,py:((x+px*s)*u,(y+py*s)*u)
    p=skia.Path();p.moveTo(*P(-10,-80));p.cubicTo(*P(-5,-40),*P(-40,-30),*P(-50,10));p.cubicTo(*P(-60,60),*P(-10,85),*P(30,70))
    p.cubicTo(*P(70,55),*P(80,40),*P(85,60));p.cubicTo(*P(95,40),*P(75,10),*P(55,20));p.cubicTo(*P(30,30),*P(15,20),*P(25,-20));p.cubicTo(*P(30,-50),*P(15,-80),*P(10,-80));p.close()
    c.drawPath(p,paint(col,a*.5,blur=25*s*u))
    c.drawPath(p,skia.Paint(AntiAlias=True,Shader=skia.GradientShader.MakeLinear([skia.Point(*P(-50,-60)),skia.Point(*P(60,70))],[hexc('#ffb0a8',a),hexc(col,a),hexc('#a03040',a)])))
    c.drawOval(skia.Rect.MakeLTRB(*P(-35,-10),*P(-15,30)),paint('#ffffff',a*.35,blur=4*u))
def glass(ctx,e,t,frame):
    a=env(e,t,.4,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,s=e.get('x',90),e.get('y',340),e.get('s',1)
    p=skia.Path();p.moveTo((x-30*s)*u,(y-60*s)*u);p.lineTo((x+30*s)*u,(y-60*s)*u);p.lineTo((x+25*s)*u,(y+50*s)*u);p.lineTo((x-25*s)*u,(y+50*s)*u);p.close()
    c.save();c.clipPath(p,doAntiAlias=True);c.drawRect(skia.Rect.MakeLTRB((x-40*s)*u,(y-20*s)*u,(x+40*s)*u,(y+60*s)*u),paint('#5aa0d8',a*.75))
    for i,(dx,dy) in enumerate([(-12,-22),(8,-26),(-2,-8),(14,-6)]): c.save();c.translate((x+dx*s)*u,(y+dy*s)*u);c.rotate(15*i);c.drawRect(skia.Rect.MakeXYWH(-9*s*u,-9*s*u,18*s*u,18*s*u),paint('#e8f4ff',a*.85));c.restore()
    c.restore();c.drawPath(p,paint('#d8ecff',a*.9,stroke=2*u))
def chili(ctx,e,t,frame):
    a=env(e,t,.4,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,s=e.get('x',80),e.get('y',300),e.get('s',1);sw=math.sin(t*1.5)*3
    c.save();c.translate(x*u,y*u);c.rotate(e.get('rot',0)+sw)
    p=skia.Path();p.moveTo(-10*s*u,-50*s*u);p.cubicTo(20*s*u,-40*s*u,30*s*u,20*s*u,-20*s*u,70*s*u);p.cubicTo(0,30*s*u,-25*s*u,-10*s*u,-22*s*u,-40*s*u);p.close()
    c.drawPath(p,paint('#e83030',a*.5,blur=14*u));c.drawPath(p,skia.Paint(AntiAlias=True,Shader=skia.GradientShader.MakeLinear([skia.Point(-20*s*u,-40*s*u),skia.Point(20*s*u,40*s*u)],[hexc('#ff7060',a),hexc('#c81818',a)])))
    line(c,-15*s*u,-48*s*u,-22*s*u,-66*s*u,'#3a9a40',a,w=5*s*u);c.restore()
def bowl(ctx,e,t,frame):
    a=env(e,t,.4,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,s=e.get('x',110),e.get('y',340),e.get('s',1)
    c.drawOval(skia.Rect.MakeLTRB((x-70*s)*u,(y-14*s)*u,(x+70*s)*u,(y+12*s)*u),paint('#f4f0e8',a))
    p=skia.Path();p.moveTo((x-72*s)*u,y*u);p.cubicTo((x-70*s)*u,(y+60*s)*u,(x+70*s)*u,(y+60*s)*u,(x+72*s)*u,y*u);p.close();c.drawPath(p,paint('#e8e4dc',a))
    line(c,(x-60*s)*u,(y+22*s)*u,(x+60*s)*u,(y+22*s)*u,'#4aa0a0',a*.7,w=2*u)
    if e.get('steam',1):
        for k in(-20,0,20):
            q=skia.Path();q.moveTo((x+k*s)*u,(y-20*s)*u)
            for i in range(1,6): q.lineTo((x+k*s+math.sin(t*2+i+k)*5)*u,(y-20*s-i*10*s)*u)
            c.drawPath(q,paint('#ffffff',a*.35,stroke=2*u))
def thermo(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,h=e.get('x',830),e.get('y',150),e.get('h',260);lv=kfi(e.get('level',.6),t)
    rrect(c,(x-8)*u,y*u,16*u,h*u,8*u,fill='#20181a',stroke='#6a5a58',a=a,sw=1.5*u);c.drawCircle(x*u,(y+h+8)*u,14*u,paint(RED,a))
    c.drawRect(skia.Rect.MakeLTRB((x-4)*u,(y+h*(1-lv))*u,(x+4)*u,(y+h+4)*u),paint(RED,a))
    for i in range(6): line(c,(x+10)*u,(y+i*h/5)*u,(x+16)*u,(y+i*h/5)*u,MUTE,a*.6,w=1*u);draw_text(c,str(40-i*8),(x+20)*u,(y+i*h/5+3)*u,font('mono',7*u),MUTE,a*.6,align='left')
def scope(ctx,e,t,frame):
    a=env(e,t,.5,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e.get('x',300),e.get('y',290),e.get('r',150)
    c.save();p=skia.Path();p.addCircle(x*u,y*u,r*u);c.clipPath(p,doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB((x-r)*u,(y-r)*u,(x+r)*u,(y+r)*u),paint(e.get('acid','#4a6a1a'),a))
    R=random.Random(2)
    for i in range(24): bx=x+R.uniform(-r,r);by=y-r+((R.uniform(0,r*1.3)-t*12)%(r*1.3));c.drawCircle(bx*u,by*u,R.uniform(3,8)*u,paint('#c8e070',a*.5,stroke=1.2*u))
    my=y+r*.18;c.drawRect(skia.Rect.MakeLTRB((x-r)*u,my*u,(x+r)*u,(my+r*.14)*u),paint('#5ad0a0',a*.85))
    vy=my+r*.14
    c.drawRect(skia.Rect.MakeLTRB((x-r)*u,vy*u,(x+r)*u,(y+r)*u),paint('#c83c50',a))
    for i in range(12):
        vx=x-r+i*r/5.5;rrect(c,(vx+2)*u,vy*u,(r/5.5-4)*u,r*.3*u,8*u,fill='#ffb8c0',stroke='#d05060',a=a,sw=1*u)
    for k in range(3): line(c,(x-r)*u,(vy+r*.42+k*10)*u,(x+r)*u,(vy+r*.42+k*10)*u,'#e06070',a*.6,w=2*u)
    c.restore();c.drawCircle(x*u,y*u,r*u,paint('#1a1a1a',a,stroke=8*u));c.drawCircle(x*u,y*u,(r+4)*u,paint('#c8d0c8',a*.3,stroke=1.5*u))
    for lb,ly in e.get('labels',[]): line(c,(x+r+6)*u,ly*u,(x+r+28)*u,ly*u,GRN,a*.7,w=1*u);draw_text(c,lb,(x+r+32)*u,(ly+3)*u,font('sans',8*u),GRN,a*.8,align='left')
def tempath(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);pts=e.get('pts',[[120,260],[220,250],[300,290],[380,270]]);g=clamp((t-e['t0'])/e.get('draw',1.2))
    p=skia.Path();p.moveTo(pts[0][0]*u,pts[0][1]*u)
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]): mx=(x0+x1)/2;p.cubicTo(mx*u,y0*u,mx*u,y1*u,x1*u,y1*u)
    m=skia.PathMeasure(p,False);q=skia.Path();m.getSegment(0,m.getLength()*g,q,True)
    c.drawPath(q,skia.Paint(AntiAlias=True,Style=skia.Paint.kStroke_Style,StrokeWidth=3*u,Shader=skia.GradientShader.MakeLinear([skia.Point(pts[0][0]*u,0),skia.Point(pts[-1][0]*u,0)],[hexc('#8ac8f0',a),hexc('#f08080',a)])))
    R=random.Random(1)
    for i in range(14): k=R.random()*g;pos=m.getPosTan(m.getLength()*k);c.drawCircle(pos[0].x(),pos[0].y()-R.uniform(-8,8)*u,2*u,paint('#ffffff',a*.5))
    for (lx,ly,l1,l2,cl) in e.get('dots',[]):
        c.drawCircle(lx*u,ly*u,5*u,paint(cl,a));draw_text(c,l1,lx*u,(ly+20)*u,font('sans-bold',10*u),CREAM,a);draw_text(c,l2,lx*u,(ly+32)*u,font('sans',8*u),MUTE,a)
def panel(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e['x'],e['y']+slide(e,t,e.get('slide',16)),e['w'],e['h'];col=e.get('col','#2a2426');bd=e.get('border','#4a4244')
    rrect(c,x*u,y*u,w*u,h*u,e.get('r',8)*u,fill=col,stroke=bd,a=a,sw=1.2*u)
    if e.get('hl'): rrect(c,x*u,y*u,w*u,h*u,e.get('r',8)*u,fill=None,stroke=e['hl'],a=a,sw=2*u);c.drawRect(skia.Rect.MakeXYWH(x*u,y*u,w*u,h*u),paint(e['hl'],a*.06))
    yy=y+e.get('pad',20)
    if e.get('title'): rich(c,e['title'],(x+14)*u,(yy+4)*u,font('sans-bold',e.get('ts',16)*u),CREAM,e.get('thl',GOLD),a,'left');yy+=e.get('ts',16)*1.6
    for ln in e.get('lines',[]): rich(c,ln,(x+14)*u,(yy+4)*u,font('sans',e.get('ls',13)*u),MUTE,e.get('lhl',GOLD),a,'left');yy+=e.get('ls',13)*1.6
def tissue(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e['x'],e['y'],e['w'],e.get('h',60)
    c.drawRect(skia.Rect.MakeXYWH(x*u,(y+14)*u,w*u,h*u),paint('#e86a78',a))
    for i in range(int(w/24)): rrect(c,(x+i*24+2)*u,(y+14)*u,20*u,h*.7*u,8*u,fill='#ffb0b8',stroke='#d05060',a=a,sw=1*u)
    c.drawRect(skia.Rect.MakeXYWH(x*u,y*u,w*u,14*u),paint('#3a9a78',a))
    if e.get('label'): draw_text(c,e['label'],(x+w/2)*u,(y+10)*u,font('sans',8*u),CREAM,a)
    for i,px in enumerate(e.get('pins',[])):
        k=clamp((t-e['t0']-.3-i*.15)/.3)
        line(c,px*u,y*u,px*u,(y-30*k)*u,'#e0d070',a,w=1.5*u);c.drawCircle(px*u,(y-34*k)*u,4*u,paint(RED,a*k,blur=1*u))
        if e.get('fire'): c.drawCircle(px*u,(y-34)*u,9*u,paint(RED,a*k*(.3+.3*math.sin(t*6+i)),blur=6*u))
def bars(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e['x'],e['y']
    for i,(lb,fr,val,cl) in enumerate(e['rows']):
        yy=y+i*e.get('gap',18);k=clamp((t-e['t0']-.2-i*.2)/.6)
        draw_text(c,lb,x*u,(yy+3)*u,font('sans',11*u),MUTE,a,align='left');rrect(c,(x+70)*u,(yy-4)*u,fr*k*e.get('w',140)*u,8*u,4*u,fill=cl,a=a)
        draw_text(c,val,(x+78+fr*e.get('w',140))*u,(yy+3)*u,font('sans',11*u),cl,a*k,align='left')
def bell(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e['x'],e['y'],e.get('w',120),e.get('h',50);g=clamp((t-e['t0'])/1)
    for mu,sg,amp,cl,dash in [(.35,.12,1,RED,False),(.6,.2,.6,GRN,True)]:
        p=skia.Path()
        for i in range(int(61*g)):
            xx=i/60;yy=amp*math.exp(-((xx-mu)/sg)**2/2);(p.moveTo if i==0 else p.lineTo)((x+xx*w)*u,(y+h-yy*h)*u)
        pt=paint(cl,a,stroke=2*u)
        if dash: pt.setPathEffect(skia.DashPathEffect.Make([4*u,3*u],0))
        c.drawPath(p,pt)
    line(c,x*u,(y+h)*u,(x+w)*u,(y+h)*u,MUTE,a*.5,w=1*u)
ICONS='clock moon bowl bed cup cig cloud run chop sleep plate fire'
def icon(c,k,x,y,s,col,a,u):
    S=lambda v: v*s*u;st=paint(col,a,stroke=1.6*u)
    if k=='clock': c.drawCircle(x*u,y*u,S(9),st);line(c,x*u,y*u,x*u,(y-6*s)*u,col,a,w=1.6*u);line(c,x*u,y*u,(x+4*s)*u,y*u,col,a,w=1.6*u)
    elif k=='moon': p=skia.Path();p.addCircle(x*u,y*u,S(9));q=skia.Path();q.addCircle((x+5*s)*u,(y-3*s)*u,S(8));p=skia.Op(p,q,skia.PathOp.kDifference_PathOp);c.drawPath(p,st)
    elif k in('bowl','plate'): p=skia.Path();p.moveTo((x-10*s)*u,y*u);p.cubicTo((x-10*s)*u,(y+10*s)*u,(x+10*s)*u,(y+10*s)*u,(x+10*s)*u,y*u);p.close();c.drawPath(p,st);line(c,(x-4*s)*u,(y-3*s)*u,(x+6*s)*u,(y-12*s)*u,col,a,w=1.6*u)
    elif k=='bed': c.drawRect(skia.Rect.MakeXYWH((x-11*s)*u,(y-2*s)*u,S(22),S(7)),st);c.drawCircle((x-6*s)*u,(y-6*s)*u,S(3),st)
    elif k=='cup': c.drawRect(skia.Rect.MakeXYWH((x-7*s)*u,(y-5*s)*u,S(14),S(14)),st);[line(c,(x+d*s)*u,(y-8*s)*u,(x+d*s)*u,(y-14*s)*u,col,a,w=1.4*u) for d in(-3,0,3)]
    elif k=='cig': line(c,(x-11*s)*u,(y+4*s)*u,(x+9*s)*u,(y-6*s)*u,col,a,w=3*u)
    elif k=='cloud': c.drawCircle((x-4*s)*u,y*u,S(6),st);c.drawCircle((x+5*s)*u,(y-2*s)*u,S(7),st)
    elif k=='run': c.drawCircle(x*u,(y-9*s)*u,S(3),st);line(c,x*u,(y-5*s)*u,x*u,(y+3*s)*u,col,a,w=1.6*u);line(c,x*u,(y+3*s)*u,(x-5*s)*u,(y+10*s)*u,col,a,w=1.6*u);line(c,x*u,(y+3*s)*u,(x+5*s)*u,(y+10*s)*u,col,a,w=1.6*u)
    elif k=='chop': line(c,(x-6*s)*u,(y+9*s)*u,(x+2*s)*u,(y-9*s)*u,col,a,w=1.6*u);line(c,(x-1*s)*u,(y+9*s)*u,(x+7*s)*u,(y-9*s)*u,col,a,w=1.6*u)
    elif k=='sleep': draw_text(c,'z',x*u,(y+4*s)*u,font('sans-bold',S(14)),col,a)
    elif k=='fire': p=skia.Path();p.moveTo(x*u,(y-10*s)*u);p.cubicTo((x+10*s)*u,y*u,(x+6*s)*u,(y+10*s)*u,x*u,(y+10*s)*u);p.cubicTo((x-6*s)*u,(y+10*s)*u,(x-10*s)*u,y*u,x*u,(y-10*s)*u);c.drawPath(p,st)
def habit(ctx,e,t,frame):
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e['x'],e['y']+slide(e,t,14),e.get('w',150),e.get('h',78);col=e.get('col',RED);dim=kfi(e.get('dim',0),t)
    aa=a*(1-dim*.75)
    rrect(c,x*u,y*u,w*u,h*u,8*u,fill='#2a1a1e' if col==RED else '#14302a',stroke=e.get('hl') or ('#5a3036' if col==RED else '#2a5a4a'),a=a,sw=(2 if e.get('hl') else 1.2)*u)
    ic=e.get('icon','clock');ix=x+(w-20 if e.get('iconright') else 22);icon(c,ic,ix,y+26,e.get('is',1.4),col,aa,u)
    tx=x+(14 if e.get('iconright') else 14)
    draw_text(c,e.get('title',''),tx*u,(y+h-30)*u,font('sans-bold',e.get('ts',12)*u),CREAM,aa,align='left')
    if e.get('sub'): rich(c,e['sub'],tx*u,(y+h-14)*u,font('sans',e.get('ss',11)*u),MUTE,GOLD,aa,'left')
    if e.get('no'): draw_text(c,e['no'],(x+w-10)*u,(y+16)*u,font('mono',7*u),MUTE,aa*.7,align='right')
def foodcard(ctx,e,t,frame):
    a=env(e,t,.35,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e['x'],e['y']+slide(e,t,30);w,h=e.get('w',200),e.get('h',230)
    c.save();c.translate(x*u,y*u);c.rotate(e.get('rot',0))
    rrect(c,-w/2*u,-h/2*u,w*u,h*u,10*u,fill='#3a2a2e',stroke='#6a5a5c',a=a,sw=1.2*u);c.restore()
    k=e.get('kind','glass');sub=dict(e,t0=e['t0'],t1=e['t1'])
    if k=='glass': glass(ctx,dict(sub,x=x,y=y-40,s=.85),t,frame)
    elif k=='chili': chili(ctx,dict(sub,x=x,y=y-45,s=.9,rot=30),t,frame)
    elif k=='bowl': bowl(ctx,dict(sub,x=x,y=y-45,s=.8),t,frame)
    draw_text(c,e.get('label',''),x*u,(y+50)*u,font('sans-bold',16*u),CREAM,a)
    draw_text(c,e.get('verdict',''),x*u,(y+84)*u,font('sans-bold',22*u),e.get('vcol','#6ac0ff'),a,glow=4*u)
def pill(ctx,e,t,frame):
    a=env(e,t,.25,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);f=font('sans-bold',e.get('size',10)*u);w=text_width(e['text'],f)/u+20;x,y=e['x'],e['y']
    rrect(c,(x-w/2)*u,(y-10)*u,w*u,20*u,10*u,fill=e.get('fill','#1a4a3a'),stroke=e.get('col',GRN),a=a,sw=1.2*u);draw_text(c,e['text'],x*u,(y+4)*u,f,e.get('col',GRN),a)
def text(ctx,e,t,frame):
    a=env(e,t,e.get('fi',.3),e.get('fo',.3))
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('size',13)
    for i,ln in enumerate(e['text'].split('\n')): rich(c,ln,e.get('x',512)*u,(e.get('y',500)+i*s*1.4)*u,font(e.get('font','sans'),s*u),e.get('col',CREAM),e.get('hl',GOLD),a,e.get('align','center'))
def tint(ctx,e,t,frame): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#000000'),env(e,t,e.get('fi',.3),e.get('fo',.3))))
def flash(ctx,e,t,frame):
    if e['t0']<=t<e['t0']+e.get('dur',.034): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#ffffff'),e.get('a',1)))
EXTRA=dict(bg=bg,title=title,badge=badge,stomach=stomach,glass=glass,chili=chili,bowl=bowl,thermo=thermo,scope=scope,tempath=tempath,panel=panel,tissue=tissue,bars=bars,bell=bell,habit=habit,foodcard=foodcard,pill=pill,text=text,tint=tint,flash=flash)
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
