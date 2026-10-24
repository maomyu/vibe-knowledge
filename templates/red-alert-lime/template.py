"""#19 红色警报·荧光绿 (red-alert-lime) — ref 7692657855442214321《自律》1920x1080 110s (Ember余烬). Topic-agnostic.
Near-black ground with soft radial tint that shifts from alarm red to lime green; serif-bold centred big text
(red/lime highlight words, strike-through, glow); small grey sans helper lines; HUD (top-left caps label, top-right
label, bottom progress line, centre chapter tag '● 03 名'); red outlined pills; checkbox lists; loop ring with labelled
nodes and centre counter; twin glowing dots (red/lime); full red alarm panel with stripes; countdown ring; play
triangle; hand-drawn ellipse around words; dashed spinning ring; chevrons. Design space 1024x576."""
import math, random, skia
from engine.core import *
from engine.layers import draw_elements, U

def prepare(S): pass
def env(e,t,fi=.3,fo=.3): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
RED='#e8333a';LIME='#c8f03c'
def bg(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx)
    c.drawRect(skia.Rect.MakeWH(W,H),paint(e.get('base','#0d0b0e')))
    tint=e.get('tint','#3a1414');x,y=e.get('cx',512),e.get('cy',260)
    c.drawCircle(x*u,y*u,e.get('r',520)*u,skia.Paint(AntiAlias=True,Shader=skia.GradientShader.MakeRadial(skia.Point(x*u,y*u),e.get('r',520)*u,[hexc(tint,e.get('ta',.8)),hexc(tint,0)])))
    vignette(c,W,H,.5)
def hud(ctx,e,t,frame):
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);f=font('sans',8*u)
    if e.get('tl'): draw_text(c,e['tl'],22*u,20*u,f,'#8a8580',a,align='left',spacing=2*u)
    if e.get('tr'): draw_text(c,e['tr'],1000*u,20*u,f,'#8a8580',a,align='right')
    y=556*u;line(c,22*u,y,1002*u,y,'#3a3634',a,w=1*u)
    p=kfi(e.get('prog',[[e['t0'],0],[e['t1'],1]]),t);line(c,22*u,y,(22+980*p)*u,y,e.get('col',RED),a,w=1.2*u)
def tag(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);col=e.get('col',RED);y=e.get('y',22)
    c.drawCircle((e.get('x',512)-40)*u,(y-2.5)*u,2.2*u,paint(col,a))
    draw_text(c,e.get('num',''),(e.get('x',512)-30)*u,y*u,font('sans',8.5*u),col,a,align='left')
    draw_text(c,e.get('text',''),(e.get('x',512)-14)*u,y*u,font('sans',8.5*u),'#b0aaa5',a,align='left')
def text(ctx,e,t,frame):
    a=env(e,t,e.get('fi',.25),e.get('fo',.25))
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('size',30);f=font(e.get('font','serif-bold'),s*u);x,y=e.get('x',512),e.get('y',300)
    runs=[];b='';h=False;col=e.get('col','#f4f0ea');hl=e.get('hl',RED)
    for ch in e['text']:
        if ch in '[]': runs.append((b,hl if h else col)); b=''; h=(ch=='[')
        else: b+=ch
    runs.append((b,hl if h else col));runs=[r for r in runs if r[0]]
    g=e.get('glow',0)
    if g:
        for r,cc in runs: pass
    w=draw_rich(c,runs,x*u,y*u,f,align=e.get('align','center'),a=a,glow=g*u)
    if e.get('strike') is not None:
        p=clamp((t-e['strike'])/.4);x0=(x-w/u/2 if e.get('align','center')=='center' else x)
        if p>0: line(c,(x0-4)*u,(y-s*.32)*u,(x0-4+(w/u+8)*p)*u,(y-s*.32)*u,e.get('scol',RED),a,w=max(1.5,s*.07)*u)
def pill(ctx,e,t,frame):
    a=env(e,t,.2,.2)
    if a<=0: return
    c=ctx.c;u=U(ctx);f=font('sans-bold',e.get('size',7)*u);col=e.get('col',RED);w=text_width(e['text'],f)/u+14;h=e.get('size',7)*2
    x=e['x']-w/2;y=e['y']-h/2
    rrect(c,x*u,y*u,w*u,h*u,h/2*u,fill=e.get('fill','#2a0e10') if e.get('fill',True) else None,stroke=col,a=a,sw=1*u)
    draw_text(c,e['text'],e['x']*u,(e['y']+e.get('size',7)*.35)*u,f,e.get('tcol',col),a)
def checks(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);f=font('sans',e.get('size',7.5)*u);x,y=e['x'],e['y'];lh=e.get('lh',16)
    for i,it in enumerate(e['items']):
        ti=e['t0']+i*e.get('step',.6)
        if isinstance(it,list): it,ti=it
        aa=a*clamp((t-ti)/.2)
        if aa<=0: continue
        yy=y+i*lh;bs=8
        bs=e.get('size',7.5)*.95;rrect(c,x*u,(yy-bs)*u,bs*u,bs*u,1*u,stroke=e.get('bcol','#d0ccc8'),a=aa,sw=1*u)
        if e.get('checked',True): p=skia.Path();p.moveTo((x+bs*.2)*u,(yy-bs*.5)*u);p.lineTo((x+bs*.45)*u,(yy-bs*.2)*u);p.lineTo((x+bs*.85)*u,(yy-bs*.85)*u);c.drawPath(p,paint('#ffffff',aa,stroke=1.3*u))
        draw_text(c,it,(x+bs+8)*u,yy*u,f,e.get('col','#d8d4cf'),aa,align='left')
def boxes(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);f=font('sans',10*u)
    for i,(x,y,w,tx) in enumerate(e['list']):
        aa=a*clamp((t-e['t0']-i*e.get('step',.4))/.25)
        if aa<=0: continue
        rrect(c,x*u,y*u,w*u,28*u,3*u,fill='#1a1214',stroke=e.get('col','#5a2a2a'),a=aa,sw=1*u)
        rrect(c,(x+9)*u,(y+9)*u,10*u,10*u,1*u,stroke='#c0bab5',a=aa,sw=1*u)
        draw_text(c,tx,(x+26)*u,(y+18)*u,f,'#e0dcd8',aa,align='left')
def loop(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e.get('x',300),e.get('y',290),e.get('r',90);col=e.get('col',RED)
    pr=clamp((t-e['t0'])/e.get('draw',1.5))
    c.drawArc(skia.Rect.MakeLTRB((x-r)*u,(y-r)*u,(x+r)*u,(y+r)*u),-90,360*pr,False,paint(col,a*kfi(e.get('ring',1),t),stroke=2*u))
    c.drawArc(skia.Rect.MakeLTRB((x-r)*u,(y-r)*u,(x+r)*u,(y+r)*u),-90,360*pr,False,paint(col,a*.4*kfi(e.get('ring',1),t),stroke=6*u,blur=5*u))
    sp=t*e.get('spin',1.2);c.drawCircle((x+math.cos(sp)*r)*u,(y+math.sin(sp)*r)*u,3*u,paint('#ffffff',a))
    for i,(lab,an) in enumerate(e.get('nodes',[])):
        aa=a*clamp((t-e['t0']-.3-i*.3)/.3)
        if aa<=0: continue
        rad=math.radians(an);nx,ny=x+math.cos(rad)*r,y+math.sin(rad)*r
        hot=e.get('hot') is not None and e['hot']==i
        pill(ctx,dict(text=lab,x=nx,y=ny,t0=-1,t1=1e9,col=RED if hot else '#e8e4e0',tcol='#ffffff' if hot else '#202020',fill='#d82a30' if hot else '#f0ece8',size=6.5),t,frame) if False else None
        f=font('sans-bold',9*u);w=text_width(lab,f)/u+16
        rrect(c,(nx-w/2)*u,(ny-10)*u,w*u,20*u,10*u,fill='#1a1214',stroke=RED if hot else '#e8e4e0',a=aa,sw=1*u)
        draw_text(c,lab,nx*u,(ny+3.2)*u,f,RED if hot else '#ffffff',aa)
    n=e.get('count')
    if n is not None:
        v=int(kfi(n,t));draw_text(c,str(v),x*u,(y+12)*u,font('serif-bold',48*u),'#ffffff',a,glow=6*u)
        if e.get('unit'): draw_text(c,e['unit'],x*u,(y+32)*u,font('sans',8*u),'#9a9590',a)
def dot(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e['x'],e['y'],e.get('r',13);col=e.get('col',RED)
    pl=1+.08*math.sin(t*e.get('pulse',4))
    c.drawCircle(x*u,y*u,r*3*pl*u,paint(col,a*.18,blur=r*1.5*u));c.drawCircle(x*u,y*u,r*1.9*u,paint(col,a*.35,stroke=1*u))
    c.drawCircle(x*u,y*u,r*pl*u,paint(col,a));c.drawCircle(x*u,y*u,r*pl*1.3*u,paint(col,a*.5,blur=r*.5*u))
def alarm(ctx,e,t,frame):
    a=env(e,t,.05,.2)
    if a<=0: return
    c=ctx.c;u=U(ctx);W,H=ctx.W,ctx.H;fl=.85+.15*math.sin(t*e.get('blink',14))
    c.drawRect(skia.Rect.MakeWH(W,H),paint('#a8262a',a*fl))
    for yy in e.get('stripes',[40,80,500]): c.drawRect(skia.Rect.MakeLTRB(0,yy*u,W,(yy+3)*u),paint('#5a0e10',a*.6))
    vignette(c,W,H,.6)
def countdown(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e.get('x',300),e.get('y',290),e.get('r',75);col=e.get('col',LIME)
    c.drawCircle(x*u,y*u,r*u,paint('#3a4030',a,stroke=3*u))
    p=kfi(e.get('p',[[e['t0'],1],[e['t1'],0]]),t)
    c.drawArc(skia.Rect.MakeLTRB((x-r)*u,(y-r)*u,(x+r)*u,(y+r)*u),-90,360*p,False,paint(col,a,stroke=3.5*u))
    c.drawArc(skia.Rect.MakeLTRB((x-r)*u,(y-r)*u,(x+r)*u,(y+r)*u),-90,360*p,False,paint(col,a*.4,stroke=8*u,blur=6*u))
    sec=int(kfi(e.get('secs',600),t));draw_text(c,'%02d:%02d'%(sec//60,sec%60),x*u,(y+9)*u,font('sans-bold',26*u),'#ffffff',a)
def play(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,s=e.get('x',512),e.get('y',200),e.get('s',28)*(1+.05*math.sin(t*3))
    p=skia.Path();p.moveTo((x-s*.6)*u,(y-s*.75)*u);p.lineTo((x+s*.8)*u,y*u);p.lineTo((x-s*.6)*u,(y+s*.75)*u);p.close()
    c.drawPath(p,paint(e.get('col',LIME),a*.5,blur=10*u));c.drawPath(p,paint(e.get('col',LIME),a))
def ellipse(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,rx,ry=e['x'],e['y'],e.get('rx',75),e.get('ry',24);pr=ease_in_out_cubic(clamp((t-e['t0'])/e.get('draw',.8)))
    rect=skia.Rect.MakeLTRB((x-rx)*u,(y-ry)*u,(x+rx)*u,(y+ry)*u)
    c.drawArc(rect,160,350*pr,False,paint(e.get('col',RED),a,stroke=2.4*u));c.drawArc(rect,160,350*pr,False,paint(e.get('col',RED),a*.5,stroke=5*u,blur=4*u))
    an=math.radians(160+350*pr);glow_dot(c,(x+math.cos(an)*rx)*u,(y+math.sin(an)*ry)*u,2*u,'#ffffff',a,halo=3)
def dashring(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e.get('x',512),e.get('y',260),e.get('r',40);n=e.get('n',18)
    for i in range(n):
        an=i*360/n+t*40;c.drawArc(skia.Rect.MakeLTRB((x-r)*u,(y-r)*u,(x+r)*u,(y+r)*u),an,360/n*.55,False,paint(e.get('col',RED),a,stroke=3*u))
def chevron(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e['x'],e['y']+2*math.sin(t*4);p=skia.Path();p.moveTo((x-5)*u,(y-3)*u);p.lineTo(x*u,(y+2)*u);p.lineTo((x+5)*u,(y-3)*u)
    c.drawPath(p,paint(e.get('col',LIME),a,stroke=1.4*u))
def bar(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w=e['x'],e['y'],e.get('w',100);line(c,x*u,y*u,(x+w)*u,y*u,'#3a3634',a,w=2*u)
    p=kfi(e.get('p',0),t);line(c,x*u,y*u,(x+w*p)*u,y*u,e.get('col',RED),a,w=2*u)
def rule(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);line(c,e['x0']*u,e['y0']*u,e['x1']*u,e['y1']*u,e.get('col','#3a3634'),a,w=1*u)
def flash(ctx,e,t,frame):
    if e['t0']<=t<e['t0']+e.get('dur',.034): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#ffffff'),e.get('a',1)))
EXTRA=dict(bg=bg,hud=hud,tag=tag,text=text,pill=pill,checks=checks,boxes=boxes,loop=loop,dot=dot,alarm=alarm,countdown=countdown,play=play,ellipse=ellipse,dashring=dashring,chevron=chevron,bar=bar,rule=rule,flash=flash)
def draw(ctx,t,frame,S):
    c=ctx.c;c.clear(skia.ColorBLACK)
    draw_elements(ctx,S.get('under',[]),t,frame,EXTRA)
    for s in S['scenes']:
        if s['t0']<=t<s['t1']:
            fi=s.get('fade_in',.3);a=clamp((t-s['t0'])/fi) if fi>0 else 1
            if a<1: c.saveLayerAlpha(None,int(255*a))
            draw_elements(ctx,s['elements'],t,frame,EXTRA)
            if a<1: c.restore()
    draw_elements(ctx,S.get('overlays',[]),t,frame,EXTRA)
