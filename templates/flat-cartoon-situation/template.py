"""#12 扁平卡通情景剧 (flat-cartoon-situation) — ref 7696886159099661604《为什么对最亲近的人发脾气》1920x1080 149.5s. Topic-agnostic.
Flat vector sitcom: preset backdrops (night city, warm dining room, cream paper, pale blue, red stage curtain, dark room,
orange/blue diagonal split, purple bokeh, night|warm split). Bold rounded sans headline top-centre with [orange-red] / {blue}
/ <green> keywords, chapter pill tag ("原因 ①"), bottom subtitle bar. Cartoon people (kid/adult/elder; moods smile/angry/
sad/neutral/mask), dinner table w/ steam, patience battery (big/small), labelled chips, speech bubble, red jagged shout
burst, thermometer tubes, rope, dot-grid of days, ✓/✗ icons, heart, wall clock, window+moon, countdown digits.
Design space 1024x576."""
import math, random, numpy as np, skia
from engine.core import *
from engine.layers import draw_elements, U, wrap_markup

RED='#e8453a'; ORA='#f39a3a'; BLUE='#3a7ad0'; GRN='#3ab060'; INK='#2a2a35'; WHITE='#ffffff'
def ease_in_cubic(x): return x*x*x
def prepare(S): pass
def env(e,t,fi=.25,fo=.25): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def SB(s): return font('sans-bold',s)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def rich(c,ln,x,y,f,a,col,align='center',shadow=False):
    M={'[':RED,'{':BLUE,'<':GRN,'(':ORA}; rs=[];b='';m=None
    for ch in ln:
        if ch in '[{<(' : rs.append((b,m)); b=''; m=M[ch]
        elif ch in ']}>)': rs.append((b,m)); b=''; m=None
        else: b+=ch
    rs.append((b,m)); tw=sum(f.measureText(s) for s,_ in rs); x=x-tw/2 if align=='center' else x
    for s,m in rs:
        if shadow: c.drawString(s,x+1.5,y+2,f,paint('#000000',a*.35))
        c.drawString(s,x,y,f,paint(m or col,a)); x+=f.measureText(s)
def rr(c,x,y,w,h,r,p): c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x,y,w,h),r,r),p)

# ---------- backdrops ----------
def backdrop(ctx,e,t,frame):
    a=env(e,t,.2,.2)
    if a<=0: return
    c=ctx.c; u=U(ctx); W,H=ctx.W,ctx.H; k=e.get('kind','cream')
    def grad(c0,c1,y0=0,y1=576):
        g=skia.GradientShader.MakeLinear([(0,y0*u),(0,y1*u)],[hexc(c0,a),hexc(c1,a)]); q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeWH(W,H),q)
    if k=='night':
        grad('#1a2350','#2a3a6a'); r=random.Random(3)
        for i in range(40): c.drawCircle(r.uniform(0,1024)*u,r.uniform(0,250)*u,r.uniform(.5,1.4)*u,paint('#ffffff',a*r.uniform(.3,.8)))
        c.drawCircle(860*u,60*u,18*u,paint('#f4f0e0',a)); c.drawCircle(860*u,60*u,34*u,paint('#f4f0e0',a*.25,blur=10*u))
        for i in range(16):
            bw=r.uniform(50,90); bh=r.uniform(120,300); bx=i*68-20
            c.drawRect(skia.Rect.MakeXYWH(bx*u,(470-bh)*u,bw*u,bh*u),paint(r.choice(['#2a3360','#323c6e','#252d58']),a))
            for wy in range(int(470-bh+12),460,22):
                for wx in range(int(bx+8),int(bx+bw-8),16):
                    if r.random()<.35: c.drawRect(skia.Rect.MakeXYWH(wx*u,wy*u,7*u,10*u),paint('#f4c860',a*.85))
        c.drawRect(skia.Rect.MakeXYWH(0,470*u,W,106*u),paint('#1c2244',a))
    elif k=='room':
        grad('#f0a070','#e88a5a',0,470); c.drawRect(skia.Rect.MakeXYWH(0,470*u,W,106*u),paint('#b86a48',a))
        c.drawLine(512*u,0,512*u,150*u,paint('#3a2a2a',a,stroke=1.5*u)); pa=skia.Path(); pa.addPoly([skia.Point(490*u,150*u),skia.Point(534*u,150*u),skia.Point(548*u,170*u),skia.Point(476*u,170*u)],True); c.drawPath(pa,paint('#e05040',a))
        c.drawCircle(512*u,240*u,200*u,paint('#ffd8a0',a*.35,blur=60*u))
    elif k=='dark':
        grad('#2a2632','#1a1820',0,470); c.drawRect(skia.Rect.MakeXYWH(0,470*u,W,106*u),paint('#24202a',a))
    elif k=='cream': grad('#f6f0e4','#ece4d4')
    elif k=='blue': grad('#eef4fa','#dce8f4')
    elif k=='green': grad('#eef6ee','#dcecdc')
    elif k=='stage':
        grad('#1a1430','#2a2048'); c.drawRect(skia.Rect.MakeXYWH(0,470*u,W,106*u),paint('#141026',a))
        for side in (0,1):
            for i in range(6):
                x=(i*22 if side==0 else 1024-140+i*22); c.drawRect(skia.Rect.MakeXYWH(x*u,0,24*u,H),paint('#b02a30' if i%2 else '#8a1e24',a))
        c.drawRect(skia.Rect.MakeXYWH(0,0,W,40*u),paint('#8a1e24',a))
    elif k=='split':
        c.drawRect(skia.Rect.MakeWH(W,H),paint('#2a5aa8',a)); pa=skia.Path(); pa.addPoly([skia.Point(0,0),skia.Point(W,0),skia.Point(W,200*u),skia.Point(0,300*u)],True)
        g=skia.GradientShader.MakeLinear([(0,0),(W,0)],[hexc('#f07038',a),hexc('#f09040',a)]); q=skia.Paint(AntiAlias=True); q.setShader(g); c.drawPath(pa,q)
        r=random.Random(5)
        for i in range(14): draw_text(c,'☺',r.uniform(600,1000)*u,r.uniform(320,560)*u,font('sans',r.uniform(14,26)*u),'#ffffff',a*.3)
    elif k=='bokeh':
        grad('#2a1a3a','#3a2040'); r=random.Random(8)
        for i in range(40): c.drawCircle(r.uniform(0,1024)*u,r.uniform(0,576)*u,r.uniform(10,50)*u,paint(r.choice(['#e070a0','#f0a060','#a070e0']),a*r.uniform(.05,.18),blur=12*u))
    elif k=='nightwarm':
        c.save(); c.clipRect(skia.Rect.MakeXYWH(0,0,512*u,H)); backdrop(ctx,dict(e,kind='night'),t,frame); c.restore()
        c.save(); c.clipRect(skia.Rect.MakeXYWH(512*u,0,512*u,H)); backdrop(ctx,dict(e,kind='room'),t,frame); c.restore()
        c.drawRect(skia.Rect.MakeXYWH(500*u,0,24*u,H),paint('#ffe8b0',a*.6,blur=10*u))
    elif k=='black': c.drawRect(skia.Rect.MakeWH(W,H),paint('#0e0c12',a))
def window(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,w,h=e.get('x',140),e.get('y',100),e.get('w',150),e.get('h',140)
    rr(c,x*u,y*u,w*u,h*u,4*u,paint('#3a2c2a',a)); c.drawRect(skia.Rect.MakeXYWH((x+6)*u,(y+6)*u,(w-12)*u,(h-12)*u),paint('#1a2450',a))
    c.drawCircle((x+w*.6)*u,(y+h*.35)*u,10*u,paint('#f4f0e0',a)); c.drawLine((x+w/2)*u,y*u,(x+w/2)*u,(y+h)*u,paint('#3a2c2a',a,stroke=5*u)); c.drawLine(x*u,(y+h/2)*u,(x+w)*u,(y+h/2)*u,paint('#3a2c2a',a,stroke=5*u))
def frame_pic(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',780),e.get('y',90)
    c.drawRect(skia.Rect.MakeXYWH(x*u,y*u,90*u,64*u),paint('#6a4a3a',a)); c.drawRect(skia.Rect.MakeXYWH((x+6)*u,(y+6)*u,78*u,52*u),paint('#f4e8d0',a))
    for i,cc in enumerate(['#e88a5a','#5a8ad0','#e8b050']): c.drawCircle((x+24+i*20)*u,(y+38)*u,7*u,paint(cc,a))
def clock(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,r=e.get('x',700),e.get('y',200),e.get('r',26)
    c.drawCircle(x*u,y*u,r*u,paint('#ffffff',a)); c.drawCircle(x*u,y*u,r*u,paint('#3a3a3a',a,stroke=3*u))
    an=t*e.get('speed',1.5); c.drawLine(x*u,y*u,(x+math.cos(an)*r*.75)*u,(y+math.sin(an)*r*.75)*u,paint('#3a3a3a',a,stroke=2*u)); c.drawLine(x*u,y*u,(x+math.cos(an/12)*r*.5)*u,(y+math.sin(an/12)*r*.5)*u,paint('#3a3a3a',a,stroke=3*u))
def curtain_spot(ctx,e,t,frame):
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); x=e.get('x',512)
    pa=skia.Path(); pa.addPoly([skia.Point((x-40)*u,0),skia.Point((x+40)*u,0),skia.Point((x+150)*u,480*u),skia.Point((x-150)*u,480*u)],True); c.drawPath(pa,paint('#fff4d0',a*.18,blur=8*u))
    c.drawOval(skia.Rect.MakeXYWH((x-150)*u,462*u,300*u,36*u),paint('#fff4d0',a*.3,blur=4*u))

# ---------- text / UI ----------
def headline(ctx,e,t,frame):
    """bold headline lines; pop-in; keywords coloured; optional 'typed' cps"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); sz=e.get('size',34); f=SB(sz*u); y=e.get('y',90); lh=e.get('lh',sz*1.35); k=ease_out_back(prog(t,e['t0'],.35))
    col=e.get('color',INK)
    for j,ln in enumerate(e['text'].split('\n')):
        lt=e.get('line_t',[e['t0']]*9)[j] if e.get('line_t') else e['t0']
        if t<lt: continue
        kk=ease_out_back(prog(t,lt,.35)); c.save(); cx,cy=e.get('x',512)*u,(y+j*lh)*u; c.translate(cx,cy); s_=.7+.3*kk; c.scale(s_,s_); c.translate(-cx,-cy)
        rich(c,ln,cx,cy,f,a*min(1,kk),col,'center',e.get('shadow',False)); c.restore()
def subtitle(ctx,e,t,frame):
    a=env(e,t,.15,.15)
    if a<=0: return
    c=ctx.c; u=U(ctx); f=SB(e.get('size',13)*u); y=e.get('y',560)
    w=f.measureText(e['text'].replace('[','').replace(']',''))/u+30
    if e.get('bar',True): rr(c,(512-w/2)*u,(y-16)*u,w*u,22*u,4*u,paint('#000000',a*.45))
    rich(c,e['text'],512*u,y*u,f,a,WHITE)
def tag(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); f=SB(15*u); x,y=e.get('x',512),e.get('y',40); w=f.measureText(e['text'])/u+32
    rr(c,(x-w/2)*u,(y-15)*u,w*u,30*u,15*u,paint(e.get('bg','#2a3a5a'),a)); draw_text(c,e['text'],x*u,(y+5.5)*u,f,e.get('color','#ffffff'),a)
def battery(ctx,e,t,frame):
    """battery: pct keys; big (with % text centre) or small hud (label above); colour by level"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,w,h=e.get('x',140),e.get('y',290),e.get('w',360),e.get('h',70); p=kfi(e.get('pct',100),t)
    col='#4ab04a' if p>50 else '#f0a030' if p>20 else '#e04030'
    rr(c,x*u,y*u,w*u,h*u,h*.18*u,paint('#2a2830',a)); rr(c,x*u,y*u,w*u,h*u,h*.18*u,paint('#f4f4f4',a,stroke=max(2,h*.06)*u))
    c.drawRect(skia.Rect.MakeXYWH((x+w)*u,(y+h*.3)*u,h*.12*u,h*.4*u),paint('#f4f4f4',a))
    pad=h*.12; c.drawRect(skia.Rect.MakeXYWH((x+pad)*u,(y+pad)*u,(w-2*pad)*max(0,p)/100*u,(h-2*pad)*u),paint(col,a))
    if e.get('show_pct',True): draw_text(c,'%d%%'%round(p),(x+w/2)*u,(y+h*.68)*u,SB(h*.42*u),WHITE,a)
    if e.get('label'): draw_text(c,e['label'],x*u,(y-5)*u,SB(8*u),e.get('label_col','#ffffff'),a*.8,'left')
    if e.get('delta'):
        for d in e['delta']:
            if d[0]<=t<d[0]+1.2: draw_text(c,d[1],(x+w+20)*u,(y+h*.7-(t-d[0])*12)*u,SB(12*u),RED,a*(1-(t-d[0])/1.2),'left')
def chips(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); y=e.get('y',380); its=e['items']; f=SB(14*u); w=e.get('w',190); gap=e.get('gap',22); x0=512-(len(its)*w+(len(its)-1)*gap)/2
    for i,it in enumerate(its):
        lab,sub,cc=it[0],it[1],it[2] if len(it)>2 else '#e86a6a'; tt=it[3] if len(it)>3 else e['t0']; k=ease_out_back(prog(t,tt,.3))
        if k<=0: continue
        x=x0+i*(w+gap); rr(c,x*u,(y+(1-k)*20)*u,w*u,62*u,10*u,paint(cc,a*min(1,k))); draw_text(c,lab,(x+w/2)*u,(y+26+(1-k)*20)*u,f,WHITE,a*min(1,k)); draw_text(c,sub,(x+w/2)*u,(y+50+(1-k)*20)*u,SB(12*u),'#fff0e0',a*min(1,k))
def bubble(ctx,e,t,frame):
    a=env(e,t,.15,.15)
    if a<=0: return
    c=ctx.c; u=U(ctx); f=SB(e.get('size',16)*u); x,y=e.get('x',512),e.get('y',100); w=f.measureText(e['text'])/u+24; h=e.get('size',16)+18; k=ease_out_back(prog(t,e['t0'],.3))
    c.save(); c.translate(x*u,y*u); c.scale(k,k); rr(c,-w/2*u,-h/2*u,w*u,h*u,h/2*u,paint('#ffffff',a)); rr(c,-w/2*u,-h/2*u,w*u,h*u,h/2*u,paint(INK,a,stroke=1.5*u))
    pa=skia.Path(); tx=e.get('tail',-10); pa.addPoly([skia.Point((tx-6)*u,(h/2-1)*u),skia.Point((tx+6)*u,(h/2-1)*u),skia.Point((tx-4)*u,(h/2+10)*u)],True); c.drawPath(pa,paint('#ffffff',a))
    draw_text(c,e['text'],0,(e.get('size',16)*.36)*u,f,INK,a); c.restore()
def burst(ctx,e,t,frame):
    """red jagged shout burst with white bold text, shakes"""
    a=env(e,t,.1,.2)
    if a<=0: return
    c=ctx.c; u=U(ctx); f=SB(e.get('size',22)*u); x,y=e.get('x',512),e.get('y',80); w=f.measureText(e['text'])/u+60; h=e.get('size',22)*2.4
    k=ease_out_back(prog(t,e['t0'],.25)); sh=math.sin(t*50)*1.5 if t-e['t0']<.6 else 0
    c.save(); c.translate((x+sh)*u,y*u); c.scale(k,k); c.rotate(e.get('rot',-3))
    pa=skia.Path(); n=22
    for i in range(n*2):
        an=i*math.pi/n; rx=w/2*(1 if i%2 else .82); ry=h/2*(1 if i%2 else .7); px,py=math.cos(an)*rx,math.sin(an)*ry
        (pa.moveTo if i==0 else pa.lineTo)(px*u,py*u)
    pa.close(); c.drawPath(pa,paint('#e83a3a',a)); c.drawPath(pa,paint('#ffffff',a,stroke=2*u))
    draw_text(c,e['text'],0,(e.get('size',22)*.36)*u,f,WHITE,a); c.restore()
def tube(ctx,e,t,frame):
    """thermometer tube: level keys 0..100, colour, label below, value badge, dashed threshold"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,w,h=e.get('x',330),e.get('y',150),e.get('w',44),e.get('h',200); v=kfi(e.get('level',50),t)
    rr(c,x*u,y*u,w*u,h*u,w/2*u,paint('#ffffff',a)); rr(c,x*u,y*u,w*u,h*u,w/2*u,paint('#3a3a44',a,stroke=2*u))
    fh=h*v/100; rr(c,(x+5)*u,(y+h-fh)*u,(w-10)*u,(fh-5)*u,(w/2-5)*u,paint(e.get('col',GRN),a))
    if e.get('show_val',True): draw_text(c,'%d'%round(v),(x+w/2)*u,(y+h-fh+18)*u,SB(16*u),WHITE,a)
    if e.get('label'): draw_text(c,e['label'],(x+w/2)*u,(y+h+24)*u,SB(16*u),INK,a)
    for th in e.get('thresholds',[]):
        ty=y+h-h*th[0]/100
        for xx in range(int(x-60),int(x+w+10),8): c.drawLine(xx*u,ty*u,(xx+4)*u,ty*u,paint(INK,a*.7,stroke=1*u))
        draw_text(c,th[1],(x-62)*u,(ty-4)*u,SB(12*u),INK,a,'left')
def rope(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); (x0,y0),(x1,y1)=e['p0'],e['p1']; sag=kfi(e.get('sag',20),t); tension=e.get('shake',0)
    pa=skia.Path(); pa.moveTo(x0*u,y0*u); pa.quadTo((x0+x1)/2*u,(max(y0,y1)+sag+math.sin(t*30)*tension)*u,x1*u,y1*u); c.drawPath(pa,paint(e.get('col','#f06a3a'),a,stroke=6*u))
def dotgrid(ctx,e,t,frame):
    """grid of days: n dots, lit (first `lit`) colour vs dim; fills over `fill` s"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); n=e.get('n',210); cols=e.get('cols',42); x0,y0=e.get('x',90),e.get('y',260); dx=e.get('dx',20); k=prog(t,e['t0'],e.get('fill',2))
    for i in range(int(n*k)):
        r_,c_=divmod(i,cols); col=e.get('col','#f0c040') if i<e.get('lit',n) else '#5a5060'
        if e.get('red_from') and t>=e['red_from'][0] and i>=e['red_from'][1]: col=RED
        c.drawCircle((x0+c_*dx)*u,(y0+r_*dx)*u,dx*.3*u,paint(col,a))
def icon(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,r=e.get('x',100),e.get('y',300),e.get('r',16); k=ease_out_back(prog(t,e['t0'],.3)); kind=e.get('kind','check')
    c.save(); c.translate(x*u,y*u); c.scale(k,k)
    if kind in ('check','cross'):
        c.drawCircle(0,0,r*u,paint(GRN if kind=='check' else '#e04040',a))
        if kind=='check': pa=skia.Path(); pa.moveTo(-r*.45*u,0); pa.lineTo(-r*.1*u,r*.35*u); pa.lineTo(r*.5*u,-r*.35*u); c.drawPath(pa,paint(WHITE,a,stroke=r*.22*u))
        else: c.drawLine(-r*.4*u,-r*.4*u,r*.4*u,r*.4*u,paint(WHITE,a,stroke=r*.22*u)); c.drawLine(r*.4*u,-r*.4*u,-r*.4*u,r*.4*u,paint(WHITE,a,stroke=r*.22*u))
    elif kind=='heart':
        s=r*(1+.08*math.sin(t*6)); pa=skia.Path(); pa.moveTo(0,s*.9*u); pa.cubicTo(-s*1.6*u,-s*.2*u,-s*.6*u,-s*1.3*u,0,-s*.4*u); pa.cubicTo(s*.6*u,-s*1.3*u,s*1.6*u,-s*.2*u,0,s*.9*u)
        c.drawPath(pa,paint('#f05a6a',a)); c.drawCircle(0,0,s*1.6*u,paint('#f05a6a',a*.25,blur=s*.8*u))
    elif kind=='house':
        pa=skia.Path(); pa.addPoly([skia.Point(-r*u,0),skia.Point(0,-r*u),skia.Point(r*u,0)],True); c.drawPath(pa,paint('#e04040',a)); c.drawRect(skia.Rect.MakeXYWH(-r*.7*u,0,r*1.4*u,r*u),paint('#e04040',a))
    elif kind=='num':
        c.drawCircle(0,0,r*u,paint(e.get('bg',ORA),a)); draw_text(c,e.get('text','1'),0,r*.38*u,SB(r*1.1*u),WHITE,a)
    c.restore()
def bignum(ctx,e,t,frame):
    a=env(e,t,.1,.1)
    if a<=0: return
    c=ctx.c; u=U(ctx); vals=e['values']; s=None
    for tt,v in vals:
        if t>=tt: s=v; t0=tt
    if s is None: return
    k=ease_out_back(prog(t,t0,.3)); f=SB(e.get('size',40)*u*(.6+.4*k)); draw_text(c,s,e.get('x',60)*u,e.get('y',390)*u,f,e.get('color',WHITE),a,e.get('align','center'))

# ---------- people / props ----------
SKIN='#f7d2b0'
PRESET={'man':dict(body='#f0a030',hair='#2a2228',pants='#3a3a5a',h=150),'mom':dict(body='#e86a5a',hair='#9a9aa4',pants='#5a4a5a',h=135,bun=True,apron=True),
        'kid':dict(body='#f0a030',hair='#2a2228',pants='#3a3a5a',h=110),'blue':dict(body='#4aa0d0',hair='#2a2228',pants='#3a3a5a',h=150),'green':dict(body='#5ab070',hair='#4a3028',pants='#3a3a5a',h=148),
        'pink':dict(body='#e88aa0',hair='#3a2228',pants='#4a3a5a',h=145,long=True),'grey':dict(body='#8a8a9a',hair='#2a2228',pants='#3a3a4a',h=150)}
def _face(c,u,x,y,r,mood,t,a):
    ey=y-r*.05
    if mood=='mask':
        c.drawCircle(x*u,y*u,r*.95*u,paint('#ffffff',a)); c.drawCircle(x*u,y*u,r*.95*u,paint('#3a3a3a',a,stroke=1*u))
        for s in (-1,1): c.drawArc(skia.Rect.MakeXYWH((x+s*r*.38-r*.15)*u,(ey-r*.15)*u,r*.3*u,r*.25*u),200,140,False,paint('#3a3a3a',a,stroke=1.4*u))
        c.drawArc(skia.Rect.MakeXYWH((x-r*.4)*u,(y)*u,r*.8*u,r*.55*u),20,140,False,paint('#3a3a3a',a,stroke=1.6*u)); return
    for s in (-1,1):
        if mood=='angry': c.drawLine((x+s*r*.55)*u,(ey-r*.32)*u,(x+s*r*.15)*u,(ey-r*.18)*u,paint('#2a2228',a,stroke=1.8*u))
        if mood=='sad': c.drawLine((x+s*r*.55)*u,(ey-r*.18)*u,(x+s*r*.15)*u,(ey-r*.32)*u,paint('#2a2228',a,stroke=1.4*u))
        c.drawCircle((x+s*r*.35)*u,ey*u,r*.09*u,paint('#2a2228',a))
    if mood=='smile': c.drawArc(skia.Rect.MakeXYWH((x-r*.3)*u,(y+r*.05)*u,r*.6*u,r*.4*u),10,160,False,paint('#c04a3a',a,stroke=1.6*u))
    elif mood=='angry': c.drawOval(skia.Rect.MakeXYWH((x-r*.2)*u,(y+r*.25)*u,r*.4*u,r*.25*u),paint('#a03028',a))
    elif mood=='sad': c.drawArc(skia.Rect.MakeXYWH((x-r*.25)*u,(y+r*.3)*u,r*.5*u,r*.3*u),200,140,False,paint('#7a3a3a',a,stroke=1.6*u))
    else: c.drawLine((x-r*.18)*u,(y+r*.38)*u,(x+r*.18)*u,(y+r*.38)*u,paint('#7a3a3a',a,stroke=1.4*u))
    c.drawCircle((x-r*.55)*u,(y+r*.2)*u,r*.12*u,paint('#f4a0a0',a*.6)); c.drawCircle((x+r*.55)*u,(y+r*.2)*u,r*.12*u,paint('#f4a0a0',a*.6))
def person(ctx,e,t,frame):
    """flat cartoon person: who preset, x (keys), y=feet, s scale, mood (keys [[t,m]]), walk bool, flip, shake"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); P=dict(PRESET.get(e.get('who','man'),PRESET['man'])); P.update(e.get('style',{})); s=e.get('s',1); H_=P['h']*s*1.5
    x=kfi(e.get('x',512),t); y=e.get('y',470); mood=e.get('mood','neutral')
    if isinstance(mood,list):
        m_=mood[0][1]
        for tt,mm in mood:
            if t>=tt: m_=mm
        mood=m_
    if e.get('shake') and mood=='angry': x+=math.sin(t*40)*1.5
    walk=e.get('walk',False); ph=t*8
    hr=H_*.2; hy=y-H_+hr; by0=hy+hr*.9; by1=y-H_*.28; bw=H_*.26
    c.drawOval(skia.Rect.MakeXYWH((x-bw*.8)*u,(y-4)*u,bw*1.6*u,8*u),paint('#000000',a*.15))
    for side in (-1,1):
        sw=math.sin(ph+(0 if side<0 else math.pi))*H_*.06 if walk else 0
        c.drawLine((x+side*bw*.22)*u,by1*u,(x+side*bw*.22+sw)*u,(y-3)*u,paint(P['pants'],a,stroke=bw*.28*u))
        c.drawOval(skia.Rect.MakeXYWH((x+side*bw*.22+sw-bw*.2)*u,(y-6)*u,bw*.4*u,6*u),paint('#2a2228',a))
    rr(c,(x-bw/2)*u,by0*u,bw*u,(by1-by0+bw*.1)*u,bw*.45*u,paint(P['body'],a))
    if P.get('apron'): rr(c,(x-bw*.3)*u,(by0+bw*.4)*u,bw*.6*u,(by1-by0)*.75*u,bw*.12*u,paint('#ffffff',a*.95))
    for side in (-1,1):
        sw=math.sin(ph+(math.pi if side<0 else 0))*H_*.05 if walk else 0
        c.drawLine((x+side*bw*.45)*u,(by0+bw*.25)*u,(x+side*bw*.55+sw)*u,(by1-bw*.1)*u,paint(P['body'],a,stroke=bw*.22*u))
        c.drawCircle((x+side*bw*.55+sw)*u,(by1-bw*.05)*u,bw*.12*u,paint(SKIN,a))
    c.drawCircle(x*u,hy*u,hr*u,paint(SKIN,a))
    if P.get('bun'): c.drawCircle(x*u,(hy-hr*.95)*u,hr*.4*u,paint(P['hair'],a)); c.drawArc(skia.Rect.MakeXYWH((x-hr*1.02)*u,(hy-hr*1.02)*u,hr*2.04*u,hr*1.6*u),180,180,True,paint(P['hair'],a))
    elif P.get('long'): c.drawArc(skia.Rect.MakeXYWH((x-hr*1.1)*u,(hy-hr*1.05)*u,hr*2.2*u,hr*2.4*u),160,220,True,paint(P['hair'],a)); c.drawCircle(x*u,(hy+hr*.1)*u,hr*.85*u,paint(SKIN,a))
    else: c.drawArc(skia.Rect.MakeXYWH((x-hr*1.02)*u,(hy-hr*1.05)*u,hr*2.04*u,hr*1.3*u),180,180,True,paint(P['hair'],a))
    _face(c,u,x,hy+hr*.1,hr,mood,t,a)
    if e.get('steam') and mood=='angry':
        for j in range(3): c.drawCircle((x+hr*1.2+j*4)*u,(hy-hr-j*6-(t*20)%10)*u,(3+j)*u,paint('#ffffff',a*.6))
def table(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,w=e.get('x',512),e.get('y',380),e.get('w',260)
    c.drawRect(skia.Rect.MakeXYWH((x-w/2)*u,y*u,w*u,12*u),paint('#f4f0ea',a)); c.drawRect(skia.Rect.MakeXYWH((x-w/2)*u,(y+12)*u,w*u,6*u),paint('#d84a3a',a))
    for s in (-1,1): c.drawRect(skia.Rect.MakeXYWH((x+s*(w/2-14)-4)*u,(y+18)*u,8*u,(470-y-18)*u),paint('#6a4038',a))
    if e.get('food',True):
        for i,cc in enumerate(['#ffffff','#f0a040','#ffffff']):
            fx=x-w*.3+i*w*.3; c.drawOval(skia.Rect.MakeXYWH((fx-22)*u,(y-10)*u,44*u,14*u),paint(cc,a)); c.drawOval(skia.Rect.MakeXYWH((fx-16)*u,(y-16)*u,32*u,10*u),paint('#e88a3a' if i==1 else '#e8d8c0',a))
            for j in range(2):
                pa=skia.Path(); sx=fx-6+j*12; pa.moveTo(sx*u,(y-20)*u)
                for q in range(1,6): pa.lineTo((sx+4*math.sin(q+t*3+j))*u,(y-20-q*6)*u)
                c.drawPath(pa,paint('#ffffff',a*.5,stroke=1.4*u))
def phone(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',800),e.get('y',260)
    rr(c,(x-45)*u,(y-80)*u,90*u,160*u,12*u,paint('#2a2a30',a)); rr(c,(x-40)*u,(y-72)*u,80*u,144*u,8*u,paint('#f4f6f8',a))
    for i,(txt,side) in enumerate(e.get('msgs',[])):
        tt=e['t0']+i*.5
        if t>=tt: rr(c,(x-34+(20 if side=='r' else 0))*u,(y-60+i*22)*u,48*u,16*u,6*u,paint('#5ac85a' if side=='r' else '#ffffff',a)); draw_text(c,txt,(x-10+(20 if side=='r' else 0))*u,(y-49+i*22)*u,SB(6*u),INK,a)
EXTRA=dict(backdrop=backdrop,window=window,picture=frame_pic,clock=clock,spot=curtain_spot,headline=headline,subtitle=subtitle,tag=tag,battery=battery,chips=chips,bubble=bubble,
           burst=burst,tube=tube,rope=rope,dotgrid=dotgrid,icon=icon,bignum=bignum,person=person,table=table,phone=phone)
def draw(ctx,t,frame,S):
    c=ctx.c; c.clear(hexc('#f4efe4')); SC=S['scenes']
    for i,sc in enumerate(SC):
        if sc['t0']-1e-6<=t<sc['t1']:
            fi=sc.get('fade_in',.25)
            if fi>0 and t<sc['t0']+fi and i>0:   # crossfade: previous scene underneath
                draw_elements(ctx,SC[i-1].get('elements',[]),SC[i-1]['t1']-.04,frame,EXTRA)
                c.saveLayerAlpha(None,int(255*min(1,(t-sc['t0'])/fi))); draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA); c.restore()
            else: draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)
            fl=([sc['t0']] if sc.get('flash') else [])+sc.get('flash_at',[])
            for f0 in fl:
                if f0<=t<f0+.034: c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint('#ffffff',.8))
    draw_elements(ctx,S.get('overlays',[]),t,frame,EXTRA)
