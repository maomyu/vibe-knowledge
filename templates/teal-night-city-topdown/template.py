"""#10 俯瞰夜城·青蓝 (teal-night-city-topdown) — ref 7694210498786768485《缘分》1280x720 130.4s. Topic-agnostic.
Deep blue-grey night (#0c0e17), top-down 'diorama' views drawn in code: subway carriage from above (teal seats, dark
heads, two highlighted people = orange & teal rings, distance callout), zebra crossing crowd, street-lamp pool of light,
city block map (lit windows, parks, river band) with orange/teal route polylines drawing on + labels + year, twin curves
(title / weave / wiggle chart with years, merge to one gold line), particle clusters, teal search bar/chat pill.
Bottom-left white small caption with grey tail. Warm (#806045) light-ray grade for the ending. Design space 1024x576.
v3 RICHNESS: tin transitions, blinking windows, car motes, continuous route growth, kb. See RICHNESS_STANDARD.md."""
import math, random, numpy as np, skia
from engine.core import *
from engine.layers import draw_elements, U, wrap_markup
from engine import richness as RICH

BG='#0c0e17'; ORA='#e0a060'; TEAL='#5fc7c3'; WHITE='#e8e6e0'; GREY='#8a8a88'; WARM='#806045'
def prepare(S): pass
def env(e,t,fi=.5,fo=.5): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def SR(s,w=500): return font('serif-vf',s,w)
def SN(s): return font('sans',s)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def glow(c,x,y,r,col,a,u):
    c.drawCircle(x*u,y*u,r*3*u,paint(col,a*.25,blur=r*2*u)); c.drawCircle(x*u,y*u,r*u,paint(col,a))
def cam(ctx,e,t):
    """camera: pan [[t,dx,dy]] / zoom keys applied to scene content"""
    c=ctx.c; u=U(ctx); z=kfi(e.get('zoom',1),t); dx=kfi(e.get('dx',0),t); dy=kfi(e.get('dy',0),t)
    c.save(); c.translate(512*u,288*u); c.scale(z,z); c.translate((-512+dx)*u,(-288+dy)*u)

def caption(ctx,e,t,frame):
    """bottom-left caption: 'main|grey tail'"""
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c; u=U(ctx); f=SN(e.get('size',21)*u); x=e.get('x',36)*u; y=e.get('y',530)*u
    main,_,tail=e['text'].partition('|'); c.drawString(main,x,y,f,paint(WHITE,a)); c.drawString(tail,x+f.measureText(main),y,f,paint(GREY,a*.8))
def title(ctx,e,t,frame):
    a=env(e,t,.8,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); k=ease_out_cubic(prog(t,e['t0'],1.2)); f=SR(e.get('size',44)*u,e.get('weight',600)); x,y=e.get('x',512),e.get('y',290)
    al=e.get('align','center'); w=f.measureText(e['text']); xx=x*u-(w/2 if al=='center' else 0)
    c.drawString(e['text'],xx,y*u,f,paint(WHITE,a*.3,blur=6*u)); c.drawString(e['text'],xx,(y+(1-k)*6)*u,f,paint(WHITE,a*k))
    if e.get('sub'): draw_text(c,e['sub'],(x if al=='center' else x)*u,(y+26)*u,SN(9*u),GREY,a*prog(t,e['t0']+.8,.6),al if al!='center' else 'center')
def curves(ctx,e,t,frame):
    """two sweeping arcs (orange from top, teal from bottom) or weave (eye shape) or wave (low sine pair)"""
    a=env(e,t,.8,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); m=e.get('mode','arcs'); k=ease_in_out_cubic(prog(t,e['t0'],e.get('draw',2)))
    def line(P,col,w=1.2):
        n=max(2,int(len(P)*k)); pa=skia.Path.Polygon([skia.Point(x*u,y*u) for x,y in P[:n]],False)
        c.drawPath(pa,paint(col,a*.35,stroke=w*3*u,blur=3*u)); c.drawPath(pa,paint(col,a,stroke=w*u)); return P[n-1]
    xs=np.linspace(0,1024,200)
    if m=='arcs':
        line([(x,40+((x-560)/560)**2*-140+180) for x in xs][::-1] if False else [(x,-20+180*(1-((x-600)/600)**2)*.9) for x in xs],ORA)
        line([(x,576+20-210*(1-((x-600)/600)**2)*.9) for x in xs],TEAL)
    elif m=='weave':
        cx,cy,w,h=e.get('x',512),e.get('y',300),e.get('w',300),e.get('h',90); ph=t*.6
        for j in range(e.get('lines',10)):
            col=ORA if j%2==0 else TEAL; s=(1 if j%2 else -1)*(1-.09*(j//2))
            P=[(cx-w+2*w*q,cy+s*h*math.sin(math.pi*q)*(1+.08*math.sin(ph+j))) for q in np.linspace(0,1,120)]; end=line(P,col,.9)
        glow(c,cx+w,cy,3,'#ffffff',a*k,u); glow(c,cx-w,cy,2.5,ORA,a,u)
    elif m=='wave':
        y=e.get('y',540)
        for j,col in enumerate([ORA,TEAL]): line([(x,y+6*math.sin(x/40+t*1.2+j*2)) for x in xs],col,.9)
def wiggle(ctx,e,t,frame):
    """two wiggly life-lines orange/teal over time axis (years); merge -> converge to one gold line at merge t"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); k=ease_in_out_cubic(prog(t,e['t0'],e.get('draw',4))); mg=ease_in_out_cubic(prog(t,e.get('merge',1e9),2.5))
    x0,x1,y=e.get('x0',40),e.get('x1',800),e.get('y',330); amp=e.get('amp',70)
    for j,(col,ph) in enumerate([(ORA,0),(TEAL,2.1)]):
        P=[]
        for q in np.linspace(0,k,int(160*k)+2):
            x=x0+(x1-x0)*q; yy=y+amp*(1-mg)*(math.sin(q*9+ph)*.6+math.sin(q*4.3+ph*1.7)*.4)*(1 if q<.95 else 1)
            P.append((x,yy))
        cc=ORA if mg>.5 and j==0 else col
        pa=skia.Path.Polygon([skia.Point(px*u,py*u) for px,py in P],False); c.drawPath(pa,paint(cc,a*.3,stroke=3*u,blur=3*u)); c.drawPath(pa,paint(cc,a*(1-mg*j),stroke=1.1*u))
        glow(c,P[-1][0],P[-1][1],2.5,cc,a*(1-mg*j),u)
    for i,yr in enumerate(e.get('years',[])):
        draw_text(c,str(yr),(x0+(x1-x0)*i/max(1,len(e['years'])-1))*u,556*u,SN(7*u),GREY,a*.6)
def citymap(ctx,e,t,frame):
    """navy block grid with lit windows, parks, diagonal river band; routes=[{pts,col,t0,dur,label}] ; year label"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); cam(ctx,e,t); r=random.Random(e.get('seed',2)); bs=e.get('block',38); gap=6
    c.drawRect(skia.Rect.MakeXYWH(-200*u,-200*u,1424*u,976*u),paint('#0a0f1c',a))
    for gx in range(-4,30):
        for gy in range(-4,18):
            x,y=gx*(bs+gap),gy*(bs+gap); park=r.random()<.06
            c.drawRect(skia.Rect.MakeXYWH(x*u,y*u,bs*u,bs*u),paint('#0f2418' if park else '#0e1630',a))
            if not park:
                for _ in range(5): c.drawRect(skia.Rect.MakeXYWH((x+r.uniform(2,bs-6))*u,(y+r.uniform(2,bs-6))*u,3*u,3*u),paint(r.choice(['#1c2850','#24305a','#3a4a7a']),a*.6))
    pa=skia.Path(); P=[(x,420-x*.32+30*math.sin(x/120)) for x in range(-200,1250,20)]
    pa.moveTo(P[0][0]*u,P[0][1]*u)
    for x,y in P: pa.lineTo(x*u,y*u)
    c.drawPath(pa,paint('#0c1a22',a*.95,stroke=44*u)); c.drawPath(pa,paint('#1a3440',a*.3,stroke=30*u,blur=6*u))
    for ro in e.get('routes',[]):
        k=ease_in_out_cubic(prog(t,ro.get('t0',e['t0']),ro.get('dur',2))); pts=ro['pts']; seg=[math.dist(pts[i],pts[i+1]) for i in range(len(pts)-1)]; L=sum(seg)*k
        q=skia.Path(); q.moveTo(pts[0][0]*u,pts[0][1]*u); acc=0; end=pts[0]
        for i,s in enumerate(seg):
            if acc+s<=L: q.lineTo(pts[i+1][0]*u,pts[i+1][1]*u); end=pts[i+1]; acc+=s
            else:
                f=(L-acc)/s; end=(pts[i][0]+(pts[i+1][0]-pts[i][0])*f,pts[i][1]+(pts[i+1][1]-pts[i][1])*f); q.lineTo(end[0]*u,end[1]*u); break
        col=ORA if ro.get('col','o')=='o' else TEAL
        c.drawPath(q,paint(col,a*.3,stroke=3*u,blur=2*u)); c.drawPath(q,paint(col,a*.9,stroke=1*u)); glow(c,end[0],end[1],2.2,col,a*(k>0),u)
        if ro.get('label') and k>=1: draw_text(c,ro['label'],(end[0]+8)*u,(end[1]-6)*u,SN(7*u),col,a*prog(t,ro.get('t0',e['t0'])+ro.get('dur',2),.4),'left')
    c.restore()
    for lb in e.get('labels',[]):
        if t>=lb[0]: draw_text(c,lb[1],lb[2]*u,lb[3]*u,SN(lb[4] if len(lb)>4 else 8*u),WHITE,a*prog(t,lb[0],.4),'left')
    if e.get('year'): draw_text(c,str(e['year']),990*u,32*u,SN(9*u),WHITE,a*.8,'right')
def _person(c,x,y,u,a,col='#15161a',hl=None,face=0,t=0,ring=1.0):
    c.drawOval(skia.Rect.MakeXYWH((x-15)*u,(y-10)*u,30*u,20*u),paint('#000000',a*.35,blur=4*u))
    c.drawOval(skia.Rect.MakeXYWH((x-13)*u,(y-8)*u,26*u,16*u),paint(col,a)); c.drawCircle(x*u,y*u,6.5*u,paint('#0b0b0e',a))
    if hl:
        cc=ORA if hl=='o' else TEAL; c.drawCircle(x*u,y*u,13*u,paint(cc,a*ring,stroke=1.6*u)); c.drawCircle(x*u,y*u,18*u,paint(cc,a*.25*ring,blur=5*u))
def subway(ctx,e,t,frame):
    """top-down carriage(s): rows of teal seats both walls, seated/standing heads, highlights [[idx,'o'|'t']], distance callout"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); cam(ctx,e,t); r=random.Random(e.get('seed',1)); warm=e.get('warm',False)
    for car,(y0) in enumerate(e.get('cars',[30,300])):
        floor=e.get('floor','#6e6f72') if not warm else '#c8a678'
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(10*u,y0*u,1004*u,220*u),30*u,30*u),paint(floor,a))
        g=skia.GradientShader.MakeLinear([(0,y0*u),(0,(y0+220)*u)],[hexc('#000000',.45*a),hexc('#000000',.05*a),hexc('#000000',.45*a)]); q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeXYWH(10*u,y0*u,1004*u,220*u),q)
        for row in (y0+22,y0+190):
            for i in range(14):
                x=40+i*70
                if i%4==3: continue
                c.drawRect(skia.Rect.MakeXYWH(x*u,(row-6)*u,52*u,14*u),paint('#2a9a98' if not warm else '#3a8a80',a*.9))
        for i in range(e.get('n',18)):
            x=r.uniform(40,980); y=y0+r.choice([22,190,r.uniform(60,160)])
            _person(c,x,y,u,a)
        if e.get('poles',True):
            for i in range(6): c.drawCircle((120+i*160)*u,(y0+110)*u,2.5*u,paint('#8a8a88',a))
        if warm:
            for i in range(5):
                pa=skia.Path(); x=200+i*120; pa.addPoly([skia.Point(x*u,y0*u),skia.Point((x+40)*u,y0*u),skia.Point((x+100)*u,(y0+220)*u),skia.Point((x+60)*u,(y0+220)*u)],True)
                c.drawPath(pa,paint('#fff0c8',a*.18,blur=4*u))
    for h in e.get('hl',[]):
        x,y,cc=h[0],h[1],h[2]; _person(c,x,y,u,a,hl=cc,ring=prog(t,h[3] if len(h)>3 else e['t0'],.5))
    if e.get('dist'):
        d=e['dist']; (x0,y0),(x1,y1)=d['a'],d['b']; k=prog(t,d.get('t0',e['t0']),.6)
        for s in np.arange(0,1,.04):
            if s<k: c.drawCircle(lerp(x0,x1,s)*u,lerp(y0,y1,s)*u,.8*u,paint('#ffffff',a))
        draw_text(c,d['text'],(lerp(x0,x1,.5)+18)*u,lerp(y0,y1,.5)*u,SN(11*u),WHITE if not warm else '#ffffff',a*k,'left')
    c.restore()
def zebra(ctx,e,t,frame):
    """zebra crossing from above + crowd heads crossing both directions; two highlighted walkers converge"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); cam(ctx,e,t); r=random.Random(3); tt=t-e['t0']
    c.drawRect(skia.Rect.MakeXYWH(-100*u,-100*u,1224*u,776*u),paint('#1a1c22',a))
    for yy in (70,500): c.drawRect(skia.Rect.MakeXYWH(-100*u,yy*u,1224*u,5*u),paint('#8a8a88',a*.6))
    for i in range(-2,26): c.drawRect(skia.Rect.MakeXYWH((i*46)*u,100*u,26*u,370*u),paint('#d0d0cc',a*.9))
    def umb(x,y,R,col,rib,al):
        c.drawCircle((x+3)*u,(y+4)*u,R*u,paint('#000000',al*.4,blur=4*u)); c.drawCircle(x*u,y*u,R*u,paint(col,al))
        for k in range(8): an=k*math.pi/4; c.drawLine(x*u,y*u,(x+math.cos(an)*R)*u,(y+math.sin(an)*R)*u,paint(rib,al*.7,stroke=.6*u))
    for i in range(e.get('n',40)):
        d=1 if i%2 else -1; x=(r.uniform(0,1024)+d*tt*r.uniform(6,12))%1100-40; y=r.uniform(90,480)
        umb(x,y,r.uniform(18,24),r.choice(['#22262c','#2a3036','#3a3040','#24303a']),'#4a5058',a)
    for h in e.get('hl',[]):
        x=kfi(h['x'],t); y=kfi(h['y'],t); cc=ORA if h['c']=='o' else TEAL
        c.drawCircle(x*u,y*u,34*u,paint(cc,a*.3,blur=12*u)); umb(x,y,22,'#c8884a' if h['c']=='o' else '#3a9a98',cc,a)
    c.restore()
def lamp(ctx,e,t,frame):
    """street lamp from above: lamp head bar + cone pool; walker dot(s) passing with glow"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',512),e.get('y',120)
    g=skia.GradientShader.MakeRadial((x*u,(y+80)*u),300*u,[hexc('#b8c4d0',.35*a),hexc('#40485a',.12*a),hexc('#000000',0)]); q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),q)
    c.drawRect(skia.Rect.MakeXYWH((x-180)*u,(y-14)*u,360*u,90*u),paint('#8a9098',a*.35,blur=8*u))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((x-170)*u,(y-18)*u,340*u,16*u),3*u,3*u),paint('#2a2e36',a)); c.drawRect(skia.Rect.MakeXYWH((x-166)*u,(y-6)*u,332*u,5*u),paint('#f4f6ff',a,blur=2*u))
    c.drawCircle(x*u,y*u,6*u,paint('#111111',a))
    for w in e.get('walkers',[]):
        wx,wy=kfi(w['x'],t),kfi(w['y'],t); col=ORA if w.get('c','o')=='o' else TEAL
        if w.get('umbrella'):
            R=w.get('r',24); c.drawCircle(wx*u,wy*u,R*u,paint('#c8884a',a*.9)); c.drawCircle(wx*u,wy*u,R*1.6*u,paint(col,a*.25,blur=10*u))
            for i in range(8): an=i*math.pi/4; c.drawLine(wx*u,wy*u,(wx+math.cos(an)*R)*u,(wy+math.sin(an)*R)*u,paint('#7a5028',a*.8,stroke=.7*u))
        else: c.drawCircle(wx*u,wy*u,18*u,paint(col,a*.35,blur=10*u)); c.drawCircle(wx*u,wy*u,9*u,paint(col,a*.75,blur=2*u))
def particles(ctx,e,t,frame):
    """drifting star-clusters = people; clusters=[{x,y,col,n,vx,vy}]"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); tt=t-e['t0']
    if e.get('link') and len(e['clusters'])>1:
        A,B=e['clusters'][0],e['clusters'][1]; ax,ay=A['x']+A.get('vx',0)*tt,A['y']+A.get('vy',0)*tt; bx,by=B['x']+B.get('vx',0)*tt,B['y']+B.get('vy',0)*tt
        pa=skia.Path(); pa.moveTo(ax*u,ay*u); pa.quadTo((ax+bx)/2*u,(min(ay,by)-120)*u,bx*u,by*u); c.drawPath(pa,paint(TEAL,a*.6,stroke=.8*u))
    for j,cl in enumerate(e['clusters']):
        r=random.Random(j); cx=cl['x']+cl.get('vx',0)*tt; cy=cl['y']+cl.get('vy',0)*tt; col=cl.get('col','#ffffff')
        glow(c,cx,cy,3.5,'#ffffff',a,u); c.drawCircle(cx*u,cy*u,30*u,paint(col,a*.25,blur=18*u))
        for i in range(cl.get('n',120)):
            rr=abs(r.gauss(0,cl.get('s',30))); an=r.uniform(0,6.28)+tt*.1
            c.drawCircle((cx+math.cos(an)*rr)*u,(cy+math.sin(an)*rr*.8)*u,r.uniform(.3,.9)*u,paint(r.choice([col,'#ffffff','#a0b0c8']),a*r.uniform(.2,.8)))
def pill(ctx,e,t,frame):
    """teal search/chat pill: text types in; dot on right; x,y,w"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,w=e.get('x',512),e.get('y',290),e.get('w',400); f=SN(14*u); fill=e.get('fill',False)
    rr=skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((x-w/2)*u,(y-18)*u,w*u,36*u),18*u,18*u)
    c.drawRRect(rr,paint(TEAL if fill else '#1a2a38',a*(.85 if fill else .7))); 
    if not fill: c.drawRRect(rr,paint('#3a5a6a',a,stroke=.7*u))
    n=int(max(0,t-e['t0']-.3)*e.get('cps',8)); s=e['text'][:n]
    c.drawString(s,(x-w/2+20)*u,(y+5)*u,f,paint('#0c1a20' if fill else WHITE,a))
    if not fill: glow(c,x+w/2-18,y,7,TEAL,a,u)
def vig_warm(ctx,e,t,frame):
    a=env(e,t,1,1)
    if a<=0: return
    c=ctx.c; g=skia.GradientShader.MakeRadial((ctx.W/2,ctx.H*.55),ctx.W*.6,[hexc('#6a4a30',.8*a),hexc('#2a1c12',.6*a),hexc('#000000',0)]); q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),q)
def cars(ctx,e,t,frame):
    """tiny top-down car motes drifting on streets for constant motion"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c;u=U(ctx); r=random.Random(e.get('seed',9))
    for i in range(e.get('n',18)):
        lane=r.choice(e.get('lanes',[[80,120,900,120],[80,280,900,280],[80,440,900,440],[200,60,200,520],[520,60,520,520],[800,60,800,520]]))
        x0,y0,x1,y1=lane; ph=(t*r.uniform(.08,.22)+r.random())%1
        x=lerp(x0,x1,ph); y=lerp(y0,y1,ph); col=r.choice([ORA,TEAL,'#c8c0a8','#6a8ab0'])
        c.drawRect(skia.Rect.MakeXYWH((x-3)*u,(y-1.5)*u,6*u,3*u),paint(col,a*.85))
def blinkwin(ctx,e,t,frame):
    """random window blinks over a city block grid — density heartbeat"""
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx); r=random.Random(e.get('seed',2)); x0,y0=e.get('x0',60),e.get('y0',80)
    for i in range(e.get('rows',8)):
        for j in range(e.get('cols',14)):
            on=((int(t*2.3)+i*3+j*7)%11)<e.get('lit',4)
            if on: c.drawRect(skia.Rect.MakeXYWH((x0+j*e.get('dx',28))*u,(y0+i*e.get('dy',22))*u,8*u,6*u),paint(e.get('col','#e8c878'),a*(.35+.4*((i+j+int(t))%3==0))))
def chapter(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c;u=U(ctx);k=ease_out_cubic(prog(t,e['t0'],.5))
    draw_text(c,e.get('no',''),e.get('x',990)*u,36*u,font('sans',14*u),TEAL,a*k,'right')
    draw_text(c,e.get('text',''),e.get('x',990)*u,54*u,font('sans',10*u),GREY,a*k,'right')
def motes(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    RICH.motes(ctx.c,ctx.W,ctx.H,t,n=e.get('n',40),color=e.get('color',TEAL),a=a*.35,seed=e.get('seed',5),speed=e.get('speed',.8))
def beatflash(ctx,e,t,frame):
    beats=e.get('beats') or getattr(ctx,'beats',[])
    if not beats: return
    a=e.get('a',.35); col=e.get('col','#fff4dc'); win=e.get('window',.07)
    b=min(beats,key=lambda x:abs(x-t)); d=abs(t-b)
    if d>win: return
    k=(1-d/win)**1.5; ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(col,a*k))

EXTRA=dict(beatflash=beatflash,caption=caption,title=title,curves=curves,wiggle=wiggle,citymap=citymap,subway=subway,zebra=zebra,lamp=lamp,particles=particles,pill=pill,warm=vig_warm,
           cars=cars,blinkwin=blinkwin,chapter=chapter,motes=motes)
def _render_sc(ctx,sc,t,frame):
    draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)
def draw(ctx,t,frame,S):
    ctx.beats=S.get('beats',[])
    c=ctx.c; c.clear(hexc(BG))
    g=skia.GradientShader.MakeRadial((ctx.W/2,ctx.H*.4),ctx.W*.6,[hexc('#141a2a'),hexc('#06070c')]); q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),q)
    RICH.compose_scenes(ctx,S,t,frame,_render_sc,overlays_extra=EXTRA,clear=None,
                        vignette_s=.55,grain_a=.03,band_color=TEAL,design_size=(1024,576))
    # NOTE: full-frame RICH.beat_punch + type=beatflash cause eye-pain strobe at ~112 BPM.
# Default beat_punch OFF; if enabled keep punch_a <= 0.05. Prefer local pulses (beatrings/motes/pulse).
    if S.get('beat_punch',False) and getattr(ctx,'beats',None): RICH.beat_punch(ctx.c,ctx.W,ctx.H,t,ctx.beats,a=S.get('punch_a',.05),color=S.get('punch_col','#5fc7c3'),window=.06)
