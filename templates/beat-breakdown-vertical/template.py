"""#25 节拍拆解·竖屏 (beat-breakdown-vertical) — ref 7697546640952970532《最火的那首BGM》576x1024 160s (freedomkey). Topic-agnostic.
Warm-black stage with gold glow. Elements: bg (radial glow, blur-dim option), tag (circled section no. + small gold title),
head (big serif 1–3 lines, [gold] highlight, optional RGB chroma), bignum (huge number + unit, chroma), walker (gold
walking figure + footstep marks), slider (axis, ticks, labels, marker), dial (loop ring: segment labels, progress arc,
needle, sunburst ticks, centre counter), chords (row of chord boxes, highlighted index, scroll), piano (keys with
highlighted labelled keys), bassline (stepped glowing pitch line with cursor + dot, level labels), stats (big-number rows
with label + note), cards (tilted nested frame outlines), rays (burst), count (full-screen white card with big number),
text, flash. Design space 1024 wide (height ≈ 1820)."""
import math, random, skia
from engine.core import *
from engine.layers import draw_elements, U
GOLD='#f0b050';CREAM='#f4ead8';DIM='#6a5a48'
def prepare(S):
    for sc in S['scenes']:
        for e in sc['elements']: e.setdefault('t0',sc['t0']); e.setdefault('t1',sc['t1'])
def env(e,t,fi=.3,fo=.3): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def bg(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx)
    c.drawRect(skia.Rect.MakeWH(W,H),paint(e.get('col','#0c0a09')))
    gx,gy=e.get('glow',[512,900]);c.drawCircle(gx*u,gy*u,e.get('gr',700)*u,paint(e.get('gcol','#3a2814'),e.get('ga',.6),blur=250*u))
    R=random.Random(3)
    for i in range(40): c.drawCircle(R.uniform(0,1024)*u,R.uniform(0,1820)*u,1*u,paint(GOLD,R.uniform(.05,.25)))
    vignette(c,W,H,.6)
def tag(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);y=e.get('y',100);tx=f"{e.get('no','①')}  {e.get('text','')}"
    draw_text(c,'  '.join(tx) if e.get('spaced',True) else tx,512*u,y*u,font('serif',e.get('size',27)*u),GOLD,a*.85)
def _rich(c,ln,x,y,f,col,hl,a,al='center',dx=0,colover=None):
    runs=[];b='';h=False
    for ch in ln:
        if ch in '[]': runs.append((b,hl if h else col)); b=''; h=(ch=='[')
        else: b+=ch
    runs.append((b,hl if h else col))
    if colover: runs=[(r,colover) for r,_ in runs]
    draw_rich(c,[r for r in runs if r[0]],x+dx,y,f,align=al,a=a)
def head(ctx,e,t,frame):
    a=env(e,t,e.get('fi',.25),e.get('fo',.25))
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('size',74);f=font(e.get('font','serif-bold'),s*u);x=e.get('x',512);y=e.get('y',230);ch=e.get('chroma',0)
    sl=1
    if e.get('slam'): k=clamp((t-e['t0'])/.12);sl=1+(1-k)*.25
    for i,ln in enumerate(e['text'].split('\n')):
        yy=(y+i*s*1.22)*u
        if sl!=1: c.save();c.translate(x*u,yy-s*.35*u);c.scale(sl,sl);c.translate(-x*u,-(yy-s*.35*u))
        if ch:
            _rich(c,ln,x*u,yy,f,CREAM,GOLD,a*.8,e.get('align','center'),-ch*u,'#ff3058');_rich(c,ln,x*u,yy,f,CREAM,GOLD,a*.8,e.get('align','center'),ch*u,'#30d8ff')
        _rich(c,ln,x*u,yy,f,e.get('col',CREAM),e.get('hl',GOLD),a,e.get('align','center'))
        if sl!=1: c.restore()
def bignum(ctx,e,t,frame):
    a=env(e,t,.2,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('size',200);x,y=e.get('x',480),e.get('y',260);v=e['text'] if 'text' in e else (e['fmt']%kfi(e['value'],t) if e.get('fmt') else str(int(round(kfi(e['value'],t)))))
    f=font(e.get('font','serif-vf'),s*u,900);ch=e.get('chroma',5)
    draw_text(c,v,x*u,y*u,f,GOLD,a*.35,glow=30*u)
    if ch: draw_text(c,v,(x-ch)*u,y*u,f,'#ff3058',a*.8);draw_text(c,v,(x+ch)*u,y*u,f,'#30d8ff',a*.8)
    draw_text(c,v,x*u,y*u,f,e.get('col','#fff8ee'),a)
    if e.get('unit'): w=text_width(v,f)/u;draw_text(c,e['unit'],(x+w/2+10)*u,(y-4)*u,font('sans-bold',s*.17*u),GOLD,a,align='left')
def walker(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,s=e.get('x',512),e.get('y',1000),e.get('s',1);bpm=e.get('bpm',113);ph=(t-e['t0'])*bpm/60*math.pi;sw=math.sin(ph)
    col=GOLD;hip=(x,y-170*s);P=lambda w: dict(w=w*s*u)
    c.drawCircle(x*u,(y-330*s)*u,30*s*u,paint(col,a))
    line(c,x*u,(y-295*s)*u,hip[0]*u,hip[1]*u,col,a,w=44*s*u)
    for k,al in((1,1),(-1,.7)):
        kx=hip[0]+sw*k*45*s;ky=y-85*s;fx=hip[0]+sw*k*95*s;line(c,hip[0]*u,hip[1]*u,kx*u,ky*u,col,a*al,w=26*s*u);line(c,kx*u,ky*u,fx*u,y*u,col,a*al,w=22*s*u)
        ax=x-sw*k*40*s;line(c,x*u,(y-270*s)*u,ax*u,(y-170*s)*u,col,a*al*.9,w=18*s*u)
    gy=y+20*s
    for i in range(-10,11):
        line(c,(x+i*48)*u,gy*u,(x+i*48+24)*u,gy*u,DIM,a*.6,w=2*u)
    beat=int((t-e['t0'])*bpm/60)
    for i in range(6):
        k=beat-i;xx=x+(-i)*70*s;c.drawOval(skia.Rect.MakeXYWH((xx-25)*u,(gy+15+(k%2)*25)*u,50*u,14*u),paint(col,a*(1-i/6)*.7))
    if e.get('labels'):
        for lb,dx in zip(e['labels'],(-90,90)): draw_text(c,lb,(x+dx*s)*u,(gy+95)*u,font('sans',22*u),'#a89070',a)
def slider(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);y=e.get('y',560);x0,x1=e.get('x0',90),e.get('x1',930);v0,v1=e.get('range',[60,140]);X=lambda v:x0+(x1-x0)*(v-v0)/(v1-v0)
    line(c,x0*u,y*u,x1*u,y*u,DIM,a,w=2*u)
    if e.get('band'): b0,b1=e['band'];line(c,X(b0)*u,y*u,X(b1)*u,y*u,GOLD,a,w=5*u);draw_text(c,e.get('bandlabel',''),X((b0+b1)/2)*u,(y-22)*u,font('sans',19*u),'#c8a878',a)
    for v,lb in e.get('ticks',[]): c.drawCircle(X(v)*u,y*u,7*u,paint('#8a7a68',a));draw_text(c,lb,X(v)*u,(y+38)*u,font('sans',19*u),'#8a7a68',a)
    mv=kfi(e.get('value',113),t);c.drawCircle(X(mv)*u,y*u,14*u,paint(GOLD,a,blur=2*u))
    if e.get('label'): draw_text(c,e['label'],X(mv)*u,(y+42)*u,font('sans-bold',22*u),GOLD,a)
def dial(ctx,e,t,frame):
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e.get('x',512),e.get('y',900),e.get('r',260);per=e.get('period',8.5);t0=e.get('start',e['t0'])
    pr=((t-t0)/per)%1 if t>=t0 else 0;cnt=e.get('count0',1)+int(max(0,t-t0)//per)
    if e.get('rays',1):
        for i in range(120):
            an=i/120*math.tau;L=(18+14*(i%5==0))*(1+.3*math.sin(t*3+i));line(c,(x+(r+40)*math.cos(an))*u,(y+(r+40)*math.sin(an))*u,(x+(r+40+L)*math.cos(an))*u,(y+(r+40+L)*math.sin(an))*u,GOLD,a*.5,w=2*u)
    c.drawCircle(x*u,y*u,(r+18)*u,paint('#3a3028',a,stroke=26*u))
    p=skia.Path();p.addArc(skia.Rect.MakeLTRB((x-r-18)*u,(y-r-18)*u,(x+r+18)*u,(y+r+18)*u),-90,360*pr)
    c.drawPath(p,paint(GOLD,a*.6,stroke=30*u,blur=10*u));c.drawPath(p,paint('#ffc870',a,stroke=24*u))
    c.drawCircle(x*u,y*u,r*.42*u,paint('#14100c',a));c.drawCircle(x*u,y*u,r*.42*u,paint('#5a4a38',a,stroke=3*u))
    labs=e.get('labels',['F','Fm','Fm','E♭'])
    for i,lb in enumerate(labs):
        an=-math.pi/2+(i+.5)/len(labs)*math.tau;on=int(pr*len(labs))==i
        draw_text(c,lb,(x+r*.72*math.cos(an))*u,(y+r*.72*math.sin(an)+14)*u,font('serif-bold',40*u),GOLD if on else '#8a7a68',a)
        an2=-math.pi/2+i/len(labs)*math.tau;line(c,(x+r*.45*math.cos(an2))*u,(y+r*.45*math.sin(an2))*u,(x+r*math.cos(an2))*u,(y+r*math.sin(an2))*u,'#3a3028',a,w=2*u)
    an=-math.pi/2+pr*math.tau;line(c,x*u,y*u,(x+(r+10)*math.cos(an))*u,(y+(r+10)*math.sin(an))*u,'#fff0d8',a,w=4*u)
    draw_text(c,str(cnt),x*u,(y+30)*u,font('serif-vf',r*.36*u,900),'#fff0d8',a)
    draw_text(c,e.get('unit','圈'),x*u,(y+r*.3)*u,font('sans',18*u),'#a89070',a)
    if e.get('caption'): draw_text(c,e['caption'],x*u,(y+r+110)*u,font('sans',22*u),'#a89070',a)
def chords(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);y=e.get('y',420);items=e.get('items',['E♭','F','Fm','Fm','E♭','F']);w=e.get('w',150);off=kfi(e.get('scroll',0),t);sel=e.get('sel_rate')
    hi=int((t-e['t0'])*sel)%len(items) if sel else e.get('sel',-1)
    if e.get('label'): draw_text(c,e['label'],40*u,(y-30)*u,font('sans',18*u),'#a89070',a,align='left')
    for i,lb in enumerate(items):
        x=20+i*(w+10)-off
        if x<-w or x>1030: continue
        on=i==hi;rrect(c,x*u,y*u,w*u,64*u,6*u,fill=GOLD if on else '#1a1612',stroke='#6a5a48',sw=2*u)
        draw_text(c,lb,(x+w/2)*u,(y+44)*u,font('serif-bold',32*u),'#140e08' if on else CREAM,a*(1 if on else .8))
def piano(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);y=e.get('y',800);h=e.get('h',260);n=e.get('n',14);kw=1024/n;hi=e.get('hi',{})
    names='CDEFGAB'
    for i in range(n):
        nm=names[i%7];on=str(i) in hi
        c.drawRect(skia.Rect.MakeXYWH((i*kw+2)*u,y*u,(kw-4)*u,h*u),paint(GOLD if on else '#ece4d6',a))
        if on: draw_text(c,hi[str(i)],(i*kw+kw/2)*u,(y+h-20)*u,font('sans-bold',24*u),'#2a1a08',a);c.drawRect(skia.Rect.MakeXYWH((i*kw+2)*u,y*u,(kw-4)*u,h*u),paint(GOLD,a*.4,blur=12*u))
        if nm not in 'EB': c.drawRect(skia.Rect.MakeXYWH((i*kw+kw*.65)*u,y*u,kw*.7*u,h*.6*u),paint('#100c0a',a))
    for lb,x in e.get('under',[]): draw_text(c,lb,x*u,(y+h+34)*u,font('sans',20*u),'#a89070',a)
def bassline(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);y0=e.get('y',560);sp=e.get('sp',100);steps=e.get('steps',[[0,0],[1024,0]]);cx=e.get('cursor',780);spd=e.get('speed',0)
    off=spd*(t-e['t0']);p=skia.Path()
    for i,(x,l) in enumerate(steps):
        X=(x-off)*u;Y=(y0-l*sp)*u
        if i==0: p.moveTo(X,Y)
        else: p.lineTo(X,(y0-steps[i-1][1]*sp)*u);p.lineTo(X,Y)
    c.save();c.clipRect(skia.Rect.MakeLTRB(0,0,cx*u,ctx.H))
    c.drawPath(p,paint(GOLD,a*.6,stroke=12*u,blur=10*u));c.drawPath(p,paint('#ffd890',a,stroke=4*u));c.restore()
    c.drawPath(p,paint('#5a4a38',a*.6,stroke=2*u))
    line(c,cx*u,(y0-e.get('top',2.6)*sp)*u,cx*u,(y0+e.get('bot',1.8)*sp)*u,'#c8b8a0',a*.8,w=2*u)
    lv=0
    for x,l in steps:
        if x-off<=cx: lv=l
    c.drawCircle(cx*u,(y0-lv*sp)*u,13*u,paint('#ffe0a0',a,blur=3*u))
    for lb,l in e.get('levels',[]): draw_text(c,lb,990*u,(y0-l*sp+10)*u,font('serif-bold',30*u),'#c8b8a0',a,align='right');line(c,(cx+20)*u,(y0-l*sp)*u,960*u,(y0-l*sp)*u,'#4a3e30',a,w=1.5*u)
    if e.get('label'): draw_text(c,e['label'],40*u,(y0-e.get('top',2.6)*sp+10)*u,font('sans',18*u),'#a89070',a,align='left')
def stats(ctx,e,t,frame):
    c=ctx.c;u=U(ctx);y=e.get('y',650);gap=e.get('gap',170)
    for i,r in enumerate(e['rows']):
        t0=e['t0']+i*e.get('stagger',.6);a=fade_env(t,t0,e['t1'],.3,.3)
        if a<=0: continue
        yy=y+i*gap;draw_text(c,r[0],70*u,yy*u,font('serif-vf',70*u,800),GOLD,a,align='left',glow=6*u)
        draw_text(c,r[1],270*u,(yy-22)*u,font('serif-bold',36*u),CREAM,a,align='left')
        if len(r)>2: draw_text(c,r[2],270*u,(yy+16)*u,font('sans',19*u),'#8a7a68',a,align='left')
        line(c,60*u,(yy+60)*u,964*u,(yy+60)*u,'#2a2218',a,w=1.5*u)
def cards(ctx,e,t,frame):
    a=env(e,t,.4,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e.get('x',512),e.get('y',960);w,h=e.get('w',760),e.get('h',1300);rot=kfi(e.get('rot',-5),t);n=e.get('n',3)
    c.save();c.translate(x*u,y*u);c.rotate(rot)
    for i in range(n):
        k=1-i*.09;rrect(c,-w/2*k*u,-h/2*k*u,w*k*u,h*k*u,24*u,fill=None,stroke=GOLD,sw=(3 if i==0 else 1.5)*u)
    c.drawRect(skia.Rect.MakeXYWH(-w/2*u,-h/2*u,w*u,h*u),paint(GOLD,a*.06))
    c.restore()
def rays(ctx,e,t,frame):
    a=env(e,t,.2,.6)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e.get('x',512),e.get('y',900);R=random.Random(1);g=.6+.4*clamp((t-e['t0'])/.5)
    for i in range(e.get('n',90)):
        an=R.uniform(0,math.tau);L=R.uniform(300,1100)*g;line(c,(x+60*math.cos(an))*u,(y+60*math.sin(an))*u,(x+L*math.cos(an))*u,(y+L*math.sin(an))*u,GOLD,a*R.uniform(.1,.45),w=R.uniform(1,3)*u)
    c.drawCircle(x*u,y*u,220*u,paint(GOLD,a*.25,blur=90*u))
def count(ctx,e,t,frame):
    a=env(e,t,0,0)
    if a<=0: return
    c=ctx.c;u=U(ctx);c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('bgcol','#f4f0ea'),a))
    draw_text(c,e['text'],512*u,(e.get('y',1060))*u,font('serif-vf',e.get('size',520)*u,700),e.get('col','#0c0a09'),a)
def blurbg(ctx,e,t,frame):
    a=env(e,t,0,0)
    if a<=0: return
    c=ctx.c;u=U(ctx);c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#4a3a2a'),a*.5,blur=0))
    for i,(x,y,w,h) in enumerate(e.get('boxes',[[60,420,904,90],[60,700,904,380]])): c.drawRect(skia.Rect.MakeXYWH(x*u,y*u,w*u,h*u),paint('#8a7a68',a*.35,blur=30*u))
def text(ctx,e,t,frame):
    a=env(e,t,e.get('fi',.25),e.get('fo',.25))
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('size',24)
    for i,ln in enumerate(e['text'].split('\n')): _rich(c,ln,e.get('x',512)*u,(e.get('y',300)+i*s*1.35)*u,font(e.get('font','sans'),s*u),e.get('col','#a89070'),e.get('hl',GOLD),a,e.get('align','center'))
def flash(ctx,e,t,frame):
    if e['t0']<=t<e['t0']+e.get('dur',.034): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#ffffff'),e.get('a',1)))
EXTRA=dict(bg=bg,tag=tag,head=head,bignum=bignum,walker=walker,slider=slider,dial=dial,chords=chords,piano=piano,bassline=bassline,stats=stats,cards=cards,rays=rays,count=count,blurbg=blurbg,text=text,flash=flash)
def draw(ctx,t,frame,S):
    c=ctx.c;c.clear(skia.ColorBLACK)
    draw_elements(ctx,S.get('under',[]),t,frame,EXTRA)
    for s in S['scenes']:
        if s['t0']<=t<s['t1']:
            fi=s.get('fade_in',.3);a=clamp((t-s['t0'])/fi) if fi>0 else 1
            if a<1:
                for p in S['scenes']:
                    if abs(p['t1']-s['t0'])<.05: draw_elements(ctx,p['elements'],min(t,p['t1']-.04),frame,EXTRA)
                c.saveLayerAlpha(None,int(255*a))
            draw_elements(ctx,s['elements'],t,frame,EXTRA)
            if a<1: c.restore()
            if s.get('flash') and t<s['t0']+.034: c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint('#ffffff',1))
    draw_elements(ctx,S.get('overlays',[]),t,frame,EXTRA)
