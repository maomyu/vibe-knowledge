"""#27 黑板教室数据 (chalkboard-classroom) — ref 7698565783005220137《小时候总被说慢》1280x720 160.6s (硅基物语). Topic-agnostic.
Ink-green chalkboard (smudged eraser strokes, wooden frame + ledge) above a dark classroom floor with a row of yellow-hat
audience heads; navy kid silhouettes with yellow helmets (row, single kid at desk with open book); glowing vertical
divider line (lime / ice blue) that moves; chalk charts: hatched bars with value labels, scatter + trend line, month
axis, progress bars, sparkline, chalk boxes with text, stick figures, calendar grid, paper notes; night nursery opener
(window + moon, clock, cribs, date cards). Text: top question line, big serif title with [lime] keyword, top-left data
header, bottom caption with [lime]. Design space 1024 x 576."""
import math, random, skia
from engine.core import *
from engine.layers import draw_elements, U
from engine import richness as RICH
LIME='#c8f040';ICE='#8ad0f0';CHALK='#ecece4';NAVY='#1e2a4a';HAT='#e8c040'
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
def board(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx);x0,y0,x1,y1=e.get('box',[-10,-10,1034,480])
    c.drawRect(skia.Rect.MakeWH(W,H),paint('#06080a'))
    c.drawRect(skia.Rect.MakeLTRB(x0*u,y0*u,x1*u,y1*u),paint('#1a2c24'))
    R=random.Random(4)
    for i in range(40):
        y=R.uniform(y0,y1);x=R.uniform(x0,x1-200);c.drawRoundRect(skia.Rect.MakeXYWH(x*u,y*u,R.uniform(120,360)*u,R.uniform(6,16)*u),8*u,8*u,paint('#3a5248',R.uniform(.12,.3),blur=5*u))
    c.drawRect(skia.Rect.MakeLTRB(x0*u,y0*u,x1*u,y1*u),paint('#000000',.25,stroke=40*u,blur=30*u))
    if e.get('frame',True): c.drawRect(skia.Rect.MakeLTRB(x0*u,y0*u,x1*u,y1*u),paint('#5a3a20',1,stroke=7*u))
    c.drawRect(skia.Rect.MakeLTRB((x0-10)*u,y1*u,(x1+10)*u,(y1+8)*u),paint('#6a4a2a'))
    lg=skia.GradientShader.MakeLinear([skia.Point(0,(y1+8)*u),skia.Point(0,H)],[hexc('#1a1410'),hexc('#06060a')])
    c.drawRect(skia.Rect.MakeLTRB(0,(y1+8)*u,W,H),skia.Paint(Shader=lg))
    if e.get('heads',True):
        for i in range(9): c.drawCircle((40+i*120)*u,(H/u+12)*u,30*u,paint('#a08020',.7))
def night(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx)
    c.drawRect(skia.Rect.MakeWH(W,H),skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0,0),skia.Point(0,H)],[hexc('#0c1230'),hexc('#05070e')])))
    rrect(c,40*u,140*u,110*u,130*u,8*u,fill='#141c40',stroke='#4a5a9a',sw=2*u);c.drawCircle(115*u,180*u,16*u,paint('#e8e8f0',.95));c.drawRect(skia.Rect.MakeXYWH(30*u,140*u,18*u,140*u),paint('#2a2a6a'))
    cx,cy=820,140;c.drawCircle(cx*u,cy*u,30*u,paint(CHALK,.9,stroke=2*u));an=t*.5
    line(c,cx*u,cy*u,(cx+18*math.sin(an))*u,(cy-18*math.cos(an))*u,CHALK,.9,w=2*u);line(c,cx*u,cy*u,(cx+12)*u,cy*u,CHALK,.9,w=2*u)
def crib(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w=e['x'],e.get('y',330),e.get('w',190)
    rrect(c,(x-w/2+30)*u,(y-95)*u,(w-60)*u,46*u,6*u,fill='#f0ece0',a=a,sw=0)
    for i,ln in enumerate(e.get('label',['',''])): rich(c,ln,x*u,(y-78+i*18)*u,font('sans-bold',13*u),'#1a1a20','#2a8a20',a)
    line(c,(x-w/2)*u,(y-20)*u,(x+w/2)*u,(y-20)*u,CHALK,a,w=2*u);line(c,(x-w/2)*u,(y+60)*u,(x+w/2)*u,(y+60)*u,CHALK,a,w=2*u)
    for i in range(11): xx=x-w/2+i*w/10;line(c,xx*u,(y-20)*u,xx*u,(y+75)*u,CHALK,a*.8,w=1.5*u)
    c.drawOval(skia.Rect.MakeLTRB((x-60)*u,(y+5)*u,(x+60)*u,(y+40)*u),paint('#3a4a7a',a*.8));c.drawCircle((x-55)*u,(y+22)*u,14*u,paint('#3a4a7a',a,stroke=1.5*u))
def kid(c,u,x,y,s,a,hat=HAT):
    p=skia.Path();p.moveTo((x-18*s)*u,y*u);p.lineTo((x-16*s)*u,(y-50*s)*u);p.quadTo(x*u,(y-62*s)*u,(x+16*s)*u,(y-50*s)*u);p.lineTo((x+18*s)*u,y*u);p.close();c.drawPath(p,paint(NAVY,a))
    c.drawCircle(x*u,(y-72*s)*u,15*s*u,paint(NAVY,a));p=skia.Path();p.addArc(skia.Rect.MakeLTRB((x-16*s)*u,(y-90*s)*u,(x+16*s)*u,(y-60*s)*u),180,180);c.drawPath(p,paint(hat,a))
def kids(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x0,x1,y=e.get('x0',480),e.get('x1',870),e.get('y',190);n=e.get('n',14);S=e.get('sizes')
    for i in range(n):
        s=S[i] if S else e.get('s',1)*(1+.12*math.sin(i*2.3));x=x0+(x1-x0)*i/max(1,n-1);bob=math.sin(t*2+i)*1.2
        kid(c,u,x,y+bob,s,a*(e.get('dimfar',1)))
def desk(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,s=e.get('x',512),e.get('y',420),e.get('s',1.3)
    kid(c,u,x,y-20*s,s,a);c.drawRect(skia.Rect.MakeXYWH((x-120*s)*u,(y-20*s)*u,240*s*u,20*s*u),paint('#3a2a20',a));c.drawRect(skia.Rect.MakeXYWH((x-110*s)*u,y*u,220*s*u,60*s*u),paint('#1e1610',a))
    if e.get('book',True):
        rrect(c,(x+30*s)*u,(y-75*s)*u,90*s*u,55*s*u,3*u,fill='#f0ece0',a=a,sw=0);line(c,(x+75*s)*u,(y-75*s)*u,(x+75*s)*u,(y-20*s)*u,'#a09888',a,w=1*u)
        if e.get('booktext'): draw_text(c,e['booktext'],(x+97*s)*u,(y-45*s)*u,font('sans-bold',8*s*u),'#c83030',a)
    for dx in e.get('side',[]): kid(c,u,x+dx,y-10,1.1,a);c.drawRect(skia.Rect.MakeXYWH((x+dx-90)*u,(y-10)*u,180*u,60*u),paint('#1a120c',a))
def vline(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c;u=U(ctx);x=kfi(e.get('x',512),t);y0,y1=e.get('y0',30),e.get('y1',470);col=e.get('col',LIME);fl=.85+.15*math.sin(t*5)
    c.drawRect(skia.Rect.MakeLTRB((x-8)*u,y0*u,(x+8)*u,y1*u),paint(col,a*.3*fl,blur=8*u));line(c,x*u,y0*u,x*u,y1*u,col,a,w=2.5*u)
    if e.get('dot'): c.drawCircle(x*u,e['dot']*u,6*u,paint('#ffffff',a,blur=2*u))
    if e.get('label'): draw_text(c,e['label'],x*u,(y0-6)*u,font('sans',10*u),CHALK,a)
def hatch(c,u,x,y,w,h,col,a,sp=6):
    c.save();c.clipRect(skia.Rect.MakeXYWH(x*u,y*u,w*u,h*u));c.drawRect(skia.Rect.MakeXYWH(x*u,y*u,w*u,h*u),paint(col,a*.35))
    for k in range(int(-h),int(w),sp): line(c,(x+k)*u,(y+h)*u,(x+k+h)*u,y*u,col,a*.8,w=1.4*u)
    c.restore();c.drawRect(skia.Rect.MakeXYWH(x*u,y*u,w*u,h*u),paint(col,a,stroke=1.5*u))
def bar(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,base,w,h=e['x'],e.get('base',420),e.get('w',70),e['h'];k=ease_out_cubic(clamp((t-e['t0'])/e.get('grow',.8)));col=e.get('col',LIME)
    hatch(c,u,x,base-h*k,w,h*k,col,a)
    if e.get('top'): draw_text(c,e['top'],(x+w/2)*u,(base-h*k-10)*u,font('sans-bold',e.get('ts',20)*u),e.get('tcol',col),a*k)
    if e.get('bottom'): draw_text(c,e['bottom'],(x+w/2)*u,(base+18)*u,font('sans-bold',11*u),CHALK,a)
def scatter(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x0,y0,x1,y1=e.get('box',[100,90,940,440]);g=clamp((t-e['t0'])/e.get('grow',2));R=random.Random(e.get('seed',3));n=e.get('n',90);sl=e.get('slope',.5)
    line(c,x0*u,y0*u,x0*u,y1*u,CHALK,a*.8,w=1.5*u);line(c,x0*u,y1*u,x1*u,y1*u,CHALK,a*.8,w=1.5*u)
    for i in range(int(n*g)):
        fx=R.random();fy=clamp(sl*fx+R.gauss(.25,.2)*(1-sl*.5),0,1);c.drawCircle((x0+10+fx*(x1-x0-20))*u,(y1-10-fy*(y1-y0-20))*u,2*u,paint(CHALK,a*.85))
    if e.get('trend'):
        k=clamp((t-e['t0']-e.get('trend_t',2))/1);line(c,x0*u,(y1-30)*u,(x0+(x1-x0)*k)*u,(y1-30-(y1-y0-80)*sl*k)*u,LIME,a,w=3*u)
    for lb,xx,yy in e.get('labels',[]): draw_text(c,lb,xx*u,yy*u,font('sans-bold',11*u),CHALK,a,align='left')
def months(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x0,x1,y=e.get('x0',130),e.get('x1',690),e.get('y',70)
    line(c,x0*u,y*u,x1*u,y*u,CHALK,a,w=1.5*u)
    for i in range(12): x=x0+(x1-x0)*i/11;line(c,x*u,(y-6)*u,x*u,(y+2)*u,CHALK,a,w=1.5*u);draw_text(c,f'{i+1}月',x*u,(y+18)*u,font('sans',9*u),CHALK,a)
def hbar(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w=e['x'],e['y'],e.get('w',300);fr=kfi(e.get('frac',.6),t);k=clamp((t-e['t0'])/.8)
    c.drawRect(skia.Rect.MakeXYWH(x*u,y*u,w*u,12*u),paint(CHALK,a*.5,stroke=1.2*u));hatch(c,u,x,y,w*fr*k,12,e.get('col',LIME),a,4)
    if e.get('label'): draw_text(c,e['label'],x*u,(y-8)*u,font('sans',11*u),CHALK,a,align='left')
def box(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e['x'],e['y'],e['w'],e['h']
    c.drawRect(skia.Rect.MakeXYWH(x*u,y*u,w*u,h*u),paint(CHALK,a*.7,stroke=1.4*u))
    for i,ln in enumerate(e.get('lines',[])): rich(c,ln,(x+w/2 if e.get('center',True) else x+14)*u,(y+22+i*18)*u,font('sans',11*u),CHALK,LIME,a,'center' if e.get('center',True) else 'left')
def stick(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,s=e['x'],e.get('y',420),e.get('s',1);col=e.get('col',CHALK)
    c.drawCircle(x*u,(y-62*s)*u,9*s*u,paint(col,a,stroke=1.6*u));line(c,x*u,(y-53*s)*u,x*u,(y-22*s)*u,col,a,w=1.6*u)
    for d in(-1,1): line(c,x*u,(y-22*s)*u,(x+d*9*s)*u,y*u,col,a,w=1.6*u);line(c,x*u,(y-45*s)*u,(x+d*11*s)*u,(y-30*s)*u,col,a,w=1.6*u)
def calendar(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e.get('x',360),e.get('y',120),e.get('w',300),e.get('h',200)
    rrect(c,x*u,y*u,w*u,h*u,6*u,fill='#e8e0d0',a=a,sw=0);c.drawRect(skia.Rect.MakeXYWH(x*u,y*u,w*u,34*u),paint('#c84a3a',a))
    for r in range(4):
        for k in range(7): c.drawRect(skia.Rect.MakeXYWH((x+10+k*(w-20)/7)*u,(y+44+r*(h-54)/4)*u,((w-20)/7-4)*u,((h-54)/4-4)*u),paint('#b8b0a0',a*.6))
def paper(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e['x'],e['y'],e.get('w',160),e.get('h',60)
    c.save();c.translate(x*u,y*u);c.rotate(e.get('rot',0));rrect(c,-w/2*u,-h/2*u,w*u,h*u,3*u,fill='#f0ece0',a=a,sw=0)
    for i,ln in enumerate(e.get('lines',[])): rich(c,ln,0,(-h/2+20+i*16)*u,font('sans-bold',11*u),'#1a1a20','#c83030',a)
    c.restore()
def spark(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);pts=e['pts'];k=clamp((t-e['t0'])/1);p=skia.Path()
    for i,(x,y) in enumerate(pts[:max(2,int(len(pts)*k))]): (p.moveTo if i==0 else p.lineTo)(x*u,y*u);c.drawCircle(x*u,y*u,2.5*u,paint(CHALK,a))
    c.drawPath(p,paint(CHALK,a,stroke=1.5*u))
def window(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e.get('x',0),e.get('y',100),e.get('w',70),e.get('h',260)
    c.drawRect(skia.Rect.MakeXYWH(x*u,y*u,w*u,h*u),skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0,y*u),skia.Point(0,(y+h)*u)],[hexc('#7a8aa0',a),hexc('#e8a060',a)])))
    line(c,(x+w/2)*u,y*u,(x+w/2)*u,(y+h)*u,'#3a2a1a',a,w=3*u);line(c,x*u,(y+h/2)*u,(x+w)*u,(y+h/2)*u,'#3a2a1a',a,w=3*u)
    c.drawRect(skia.Rect.MakeXYWH(x*u,y*u,(w+200)*u,(h+100)*u),paint('#e8a060',a*.08,blur=60*u))
def text(ctx,e,t,frame):
    a=env(e,t,e.get('fi',.3),e.get('fo',.3))
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('size',16)
    for i,ln in enumerate(e['text'].split('\n')): rich(c,ln,e.get('x',512)*u,(e.get('y',300)+i*s*1.3)*u,font(e.get('font','serif-bold'),s*u),e.get('col',CHALK),e.get('hl',LIME),a,e.get('align','center'))
def tint(ctx,e,t,frame): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#000000'),env(e,t,e.get('fi',.3),e.get('fo',.3))))
def flash(ctx,e,t,frame):
    if e['t0']<=t<e['t0']+e.get('dur',.034): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#ffffff'),e.get('a',1)))

def motes(ctx,e,t,frame):
    a=env(e,t,.3,.3)
    if a<=0: return
    RICH.motes(ctx.c,ctx.W,ctx.H,t,n=e.get('n',35),color=e.get('color','#c8c0a8'),a=a*.35,seed=e.get('seed',9),speed=e.get('speed',.8))

EXTRA=dict(motes=motes,board=board,night=night,crib=crib,kids=kids,desk=desk,vline=vline,bar=bar,scatter=scatter,months=months,hbar=hbar,box=box,stick=stick,calendar=calendar,paper=paper,spark=spark,window=window,text=text,tint=tint,flash=flash)
def _render_sc(ctx,sc,t,frame):
    draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)

def draw(ctx,t,frame,S):
    ctx.beats=S.get('beats',[])
    c=ctx.c; c.clear(skia.ColorBLACK)
    draw_elements(ctx,S.get('under',[]),t,frame,EXTRA)
    RICH.compose_scenes(ctx,S,t,frame,_render_sc,overlays_extra=EXTRA,clear=None,
                        vignette_s=.35,grain_a=.04,band_color='#b8d080',design_size=(1024,576))
    if S.get('beat_punch',False) and getattr(ctx,'beats',None):
        RICH.beat_punch(ctx.c,ctx.W,ctx.H,t,ctx.beats,a=min(S.get('punch_a',.05),.05),color=S.get('punch_col','#b8d080'),window=.06)
