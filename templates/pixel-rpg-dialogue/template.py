"""#22 像素RPG对话 (pixel-rpg-dialogue) — ref 7697181453029738171《非暴力沟通》1280x720 134s (致愛麗絲). Topic-agnostic.
16-bit RPG dining-room battle: warm pixel kitchen (window cityscape, wood table + dishes, wall clock/calendar/photos),
mom sprite (apron) + son back-of-head; dual HP bars (player green / mom BOSS red); navy dialogue box with typewriter
text + speaker name; right-side command menu; floating damage numbers; GAME OVER / READY cards; blue NVC flowchart
(观察/感受/需要/请求 nodes + edges); inspect status window; optional photo plate insert; book cover end card.
Design space 1024x576. Pixel look via nearest-neighbour scaled offscreen buffer."""
import math, random, skia
from engine.core import *
from engine.layers import draw_elements, U

NAVY='#1a2850';NAVY2='#243868';GOLD='#e8c060';GREEN='#40c060';RED='#e04040'
def prepare(S): pass
def env(e,t,fi=.25,fo=.25): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*((t-a)/(b-a))
    return keys[-1][1]
def px(c,x,y,w,h,col,a=1): c.drawRect(skia.Rect.MakeXYWH(x,y,w,h),paint(col,a))
def rectb(c,x,y,w,h,fill,border='#0a0a14',bw=2,a=1):
    px(c,x,y,w,h,border,a);px(c,x+bw,y+bw,w-2*bw,h-2*bw,fill,a)
def pfont(size): return font('sans-bold',size)  # closest to pixel without dedicated bitmap font

def room(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx)
    # night sky through window
    c.drawRect(skia.Rect.MakeWH(W,H),paint('#1a1420'))
    # wall
    c.drawRect(skia.Rect.MakeLTRB(0,0,W,H*.58),paint('#4a322c'))
    # window
    wx,wy,ww,wh=80*u,30*u,520*u,260*u
    rectb(c,wx,wy,ww,wh,'#1a2040',bw=4*u)
    c.drawRect(skia.Rect.MakeXYWH(wx+4*u,wy+4*u,ww-8*u,wh-8*u),skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0,wy),skia.Point(0,wy+wh)],[hexc('#2a1840'),hexc('#6a3060'),hexc('#c07050')],[0,.55,1])))
    R=random.Random(3)
    for i in range(18):
        bx=wx+20*u+R.uniform(0,ww-60*u);bh=R.uniform(40,120)*u;by=wy+wh-bh-8*u
        px(c,bx,by,18*u,bh,'#1a1428'); [px(c,bx+4*u,by+j*10*u,4*u,4*u,'#e8c060',.6) for j in range(int(bh/(12*u)))]
    # muntins
    px(c,wx+ww/2-2*u,wy,4*u,wh,'#2a1a18');px(c,wx,wy+wh/2-2*u,ww,4*u,'#2a1a18')
    # wall decor
    for (dx,dy) in ((640,50),(720,40),(800,55)):
        rectb(c,dx*u,dy*u,70*u,70*u,'#d8c8a0',bw=3*u);px(c,(dx+10)*u,(dy+15)*u,50*u,40*u,'#8a6a50')
    rectb(c,900*u,40*u,80*u,100*u,'#f0e8d8',bw=3*u)  # calendar
    draw_text(c,'日',940*u,80*u,pfont(18*u),'#c04040',1)
    # clock
    c.drawCircle(960*u,180*u,28*u,paint('#e8d8b0'));c.drawCircle(960*u,180*u,28*u,paint('#2a1a10',1,stroke=3*u))
    # floor
    c.drawRect(skia.Rect.MakeLTRB(0,H*.58,W,H),paint('#2a1a14'))
    for i in range(0,int(W),int(40*u)): px(c,i,H*.58,2*u,H*.42,'#1a100c',.5)
    # table
    ty=340*u;tw=700*u;tx=160*u
    px(c,tx,ty,tw,40*u,'#6a3a22');px(c,tx,ty+40*u,tw,16*u,'#4a2818')
    px(c,tx+40*u,ty+56*u,20*u,120*u,'#3a1e10');px(c,tx+tw-60*u,ty+56*u,20*u,120*u,'#3a1e10')
    # dishes
    for (dx,dy,dw,col) in ((220,310,90,'#f0e8d0'),(340,305,110,'#e8d8b0'),(480,310,80,'#f0e8d0'),(580,308,100,'#e0d0b0'),(700,312,70,'#f0e8d0')):
        c.drawOval(skia.Rect.MakeXYWH(dx*u,dy*u,dw*u,28*u),paint(col));c.drawOval(skia.Rect.MakeXYWH((dx+8)*u,(dy+4)*u,(dw-16)*u,14*u),paint('#c04030' if dw>95 else '#e8a040'))
    # mom
    if e.get('mom',True):
        mx,my=e.get('momxy',[560,160]);su=e.get('ms',1.25)
        px(c,(mx-22)*u,(my+10)*u,44*u*su,36*u*su,'#e8b090')  # face
        px(c,(mx-28)*u,(my-8)*u,56*u*su,28*u*su,'#2a1810')  # hair top
        px(c,(mx-32)*u,(my+10)*u,12*u*su,40*u*su,'#2a1810');px(c,(mx+20)*u,(my+10)*u,12*u*su,40*u*su,'#2a1810')
        px(c,(mx-8)*u,(my+22)*u,5*u*su,5*u*su,'#1a1010');px(c,(mx+8)*u,(my+22)*u,5*u*su,5*u*su,'#1a1010')  # eyes
        px(c,(mx-6)*u,(my+34)*u,12*u*su,3*u*su,'#c06050')  # mouth
        # body / apron
        px(c,(mx-40)*u,(my+48)*u,80*u*su,100*u*su,'#8a3040')  # sweater
        px(c,(mx-36)*u,(my+55)*u,72*u*su,90*u*su,'#c04040')  # apron
        for i in range(5): px(c,(mx-20+i*10)*u,(my+70)*u,6*u*su,6*u*su,'#e8a0a0')  # pattern
        px(c,(mx-50)*u,(my+55)*u,16*u*su,50*u*su,'#e8b090');px(c,(mx+34)*u,(my+55)*u,16*u*su,50*u*su,'#e8b090')  # arms
    # son back (foreground)
    if e.get('son',True):
        sx,sy=e.get('sonxy',[480,400]);su=e.get('ss',1.15)
        px(c,(sx-36)*u,(sy-28)*u,72*u*su,48*u*su,'#2a2a30')  # hair
        px(c,(sx-22)*u,(sy-8)*u,44*u*su,28*u*su,'#3a3a42')
        px(c,(sx-48)*u,sy*u,96*u*su,110*u*su,'#5a5a68')  # hoodie
        px(c,(sx-28)*u,(sy+16)*u,56*u*su,40*u*su,'#4a4a52')
        # chair back
        px(c,(sx-55)*u,(sy+80)*u,14*u*su,70*u*su,'#4a3020');px(c,(sx+50)*u,(sy+80)*u,14*u*su,70*u*su,'#4a3020')

def hpbar(ctx,e,t,frame):
    a=env(e,t,0,0)
    if a<=0: return
    c=ctx.c;u=U(ctx)
    # player
    bx,by=e.get('px',30),e.get('py',18)
    draw_text(c,e.get('plabel','你'),(bx+20)*u,(by+14)*u,pfont(15*u),'#ffffff',a,align='left')
    rectb(c,(bx+50)*u,by*u,180*u,18*u,'#1a1a20',bw=2*u,a=a)
    pv=kfi(e.get('php',1),t);px(c,(bx+52)*u,(by+2)*u,max(0,176*pv)*u,14*u,e.get('pcol',GREEN),a)
    # mom
    mx,my=e.get('mx',620),e.get('my',18)
    if e.get('boss',True):
        rectb(c,(mx-50)*u,(my-2)*u,48*u,16*u,RED,bw=1*u,a=a);draw_text(c,'BOSS',(mx-26)*u,(my+11)*u,pfont(10*u),'#ffffff',a)
    draw_text(c,e.get('mlabel','妈妈'),(mx+10)*u,(my+14)*u,pfont(15*u),'#ffffff',a,align='left')
    rectb(c,(mx+70)*u,my*u,220*u,18*u,'#1a1a20',bw=2*u,a=a)
    mv=kfi(e.get('mhp',1),t);px(c,(mx+72)*u,(my+2)*u,216*mv*u,14*u,e.get('mcol',RED),a)

def dialog(ctx,e,t,frame):
    a=env(e,t,.15,.15)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e.get('x',40),e.get('y',430),e.get('w',700),e.get('h',120)
    rectb(c,x*u,y*u,w*u,h*u,NAVY,bw=3*u,a=a);px(c,(x+3)*u,(y+3)*u,(w-6)*u,3*u,NAVY2,a)
    if e.get('name'):
        nw=text_width(e['name'],pfont(14*u))/u+16
        rectb(c,(x+16)*u,(y-14)*u,nw*u,22*u,NAVY2,bw=2*u,a=a);draw_text(c,e['name'],(x+16+nw/2)*u,(y+2)*u,pfont(14*u),GOLD,a)
    txt=e.get('text','');cps=e.get('cps',28);n=min(len(txt),int(max(0,t-e['t0']-e.get('delay',.15))*cps)) if e.get('typewriter',True) else len(txt)
    shown=txt[:n];f=pfont(e.get('size',18)*u);maxw=(w-40)*u
    # wrap
    lines=[];cur=''
    for ch in shown:
        if ch=='\n' or text_width(cur+ch,f)>maxw: lines.append(cur);cur='' if ch=='\n' else ch
        else: cur+=ch
    if cur: lines.append(cur)
    for i,ln in enumerate(lines[:4]):
        col=GOLD if e.get('gold') else '#f0f0f8'
        draw_text(c,ln,(x+20)*u,(y+28+i*22)*u,f,col,a,align='left')
    if e.get('arrow',True) and (int(t*4)%2==0):
        px(c,(x+w-28)*u,(y+h-22)*u,10*u,10*u,'#f0f0f8',a)

def menu(ctx,e,t,frame):
    a=env(e,t,.2,.2)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e.get('x',780),e.get('y',200);items=e.get('items',[]);sel=e.get('sel',0);w=e.get('w',200);h=18+len(items)*32
    rectb(c,x*u,y*u,w*u,h*u,NAVY,bw=3*u,a=a)
    for i,it in enumerate(items):
        yy=y+12+i*32;active=(i==sel)
        if active: px(c,(x+6)*u,(yy-6)*u,(w-12)*u,26*u,'#2a4880',a);draw_text(c,'▶',(x+18)*u,(yy+10)*u,pfont(12*u),GOLD,a)
        col=GOLD if active else '#d0d0e0'
        draw_text(c,it,(x+36)*u,(yy+10)*u,pfont(15*u),col,a,align='left')

def dmg(ctx,e,t,frame):
    a=env(e,t,.05,.4)
    if a<=0: return
    c=ctx.c;u=U(ctx);dt=t-e['t0'];y=e['y']-dt*40
    draw_text(c,e.get('text','-25'),e['x']*u,y*u,pfont(e.get('size',28)*u),e.get('col',RED),a,glow=6*u)

def gameover(ctx,e,t,frame):
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx)
    c.drawRect(skia.Rect.MakeWH(W,H),paint('#0a0610',a*.75))
    draw_text(c,e.get('title','GAME OVER'),W/2,(H*.42)*u,pfont(48*u),RED,a,glow=12*u)
    if e.get('sub'): draw_text(c,e['sub'],W/2,(H*.55)*u,pfont(18*u),'#d0d0e0',a)
    if e.get('hint'): draw_text(c,e['hint'],W/2,(H*.68)*u,pfont(15*u),GOLD,a)

def ready(ctx,e,t,frame):
    a=env(e,t,.2,.2)
    if a<=0: return
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx)
    c.drawRect(skia.Rect.MakeWH(W,H),paint('#0a0610',a))
    draw_text(c,e.get('text','READY'),W/2,H*.45,pfont(e.get('size',42)*u),GOLD,a,glow=10*u)
    if e.get('sub'): draw_text(c,e['sub'],W/2,H*.55,pfont(18*u),'#d0d0e0',a)

def flowchart(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx)
    c.drawRect(skia.Rect.MakeWH(W,H),paint('#141e3a',a))
    # grid
    for i in range(0,int(W),int(32*u)): px(c,i,0,1*u,H,'#1a2850',a*.5)
    for j in range(0,int(H),int(32*u)): px(c,0,j,W,1*u,'#1a2850',a*.5)
    nodes=e.get('nodes',[])  # [x,y,w,h,label,col]
    for i,(x,y,w,h,lab,col) in enumerate(nodes):
        aa=a*clamp((t-e['t0']-i*e.get('step',.35))/.3)
        if aa<=0: continue
        rectb(c,x*u,y*u,w*u,h*u,col,bw=2*u,a=aa)
        draw_text(c,lab,(x+w/2)*u,(y+h/2+5)*u,pfont(14*u),'#ffffff',aa)
    for (i,j) in e.get('edges',[]):
        if i>=len(nodes) or j>=len(nodes): continue
        a0,b0=nodes[i],nodes[j]
        x0,y0=a0[0]+a0[2]/2,a0[1]+a0[3];x1,y1=b0[0]+b0[2]/2,b0[1]
        aa=a*clamp((t-e['t0']-max(i,j)*e.get('step',.35))/.3)
        if aa<=0: continue
        line(c,x0*u,y0*u,x1*u,y1*u,'#80a0e0',aa,w=2*u)
    if e.get('title'): draw_text(c,e['title'],W/2,36*u,pfont(20*u),GOLD,a)

def inspect(ctx,e,t,frame):
    a=env(e,t,.2,.2)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e.get('x',280),e.get('y',80),e.get('w',460),e.get('h',280)
    rectb(c,x*u,y*u,w*u,h*u,NAVY,bw=3*u,a=a)
    draw_text(c,e.get('title','查看：妈妈'),(x+20)*u,(y+28)*u,pfont(16*u),GOLD,a,align='left')
    for i,(k,v) in enumerate(e.get('rows',[])):
        draw_text(c,k,(x+24)*u,(y+60+i*36)*u,pfont(14*u),'#a0b0d0',a,align='left')
        draw_text(c,v,(x+w-24)*u,(y+60+i*36)*u,pfont(14*u),'#f0f0f8',a,align='right')

def photo(ctx,e,t,frame):
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx)
    c.drawRect(skia.Rect.MakeWH(W,H),paint('#1a1210',a))
    # procedural plate closeup
    c.drawOval(skia.Rect.MakeXYWH(200*u,80*u,620*u,400*u),paint('#e8e0d0',a))
    c.drawOval(skia.Rect.MakeXYWH(280*u,140*u,460*u,280*u),paint('#d8c8a8',a))
    # fish shape
    p=skia.Path();p.addOval(skia.Rect.MakeXYWH(340*u,200*u,340*u,140*u));c.drawPath(p,paint('#e8d8b0',a))
    c.drawPath(p,paint('#c8a070',a,stroke=2*u))
    for i in range(8): line(c,(380+i*35)*u,220*u,(380+i*35)*u,320*u,'#a07040',a*.6,w=1.5*u)
    # chopsticks
    line(c,600*u,160*u,780*u,340*u,'#2a1a10',a,w=6*u);line(c,620*u,150*u,800*u,330*u,'#2a1a10',a,w=6*u)
    if e.get('caption'): draw_text(c,e['caption'],W/2,520*u,pfont(16*u),'#f0e8d8',a)

def book(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx)
    c.drawRect(skia.Rect.MakeWH(W,H),paint('#1a1428',a))
    rectb(c,340*u,60*u,340*u,420*u,'#f4e8d0',bw=4*u,a=a)
    px(c,340*u,60*u,24*u,420*u,'#c04040',a)
    draw_text(c,e.get('title','非暴力沟通'),512*u,160*u,pfont(28*u),'#2a1a10',a)
    draw_text(c,e.get('author','马歇尔·卢森堡'),512*u,210*u,pfont(15*u),'#6a5a40',a)
    for i,s in enumerate(e.get('steps',['观察','感受','需要','请求'])):
        rectb(c,(400)*u,(260+i*50)*u,220*u,40*u,'#e8d8b0',bw=2*u,a=a)
        draw_text(c,f'{i+1}. {s}',512*u,(288+i*50)*u,pfont(16*u),'#2a1a10',a)

def bubble(ctx,e,t,frame):
    a=env(e,t,.15,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e['x'],e['y'];txt=e['text'];f=pfont(e.get('size',13)*u);w=text_width(txt,f)/u+20;h=28
    rectb(c,(x-w/2)*u,(y-h)*u,w*u,h*u,e.get('fill','#f0f0f8'),bw=2*u,a=a)
    # tail
    p=skia.Path();p.moveTo((x-6)*u,y*u);p.lineTo(x*u,(y+10)*u);p.lineTo((x+6)*u,y*u);c.drawPath(p,paint(e.get('fill','#f0f0f8'),a))
    draw_text(c,txt,x*u,(y-8)*u,f,e.get('col','#1a1a20'),a)

def flash(ctx,e,t,frame):
    if e['t0']<=t<e['t0']+e.get('dur',.034): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#ffffff'),e.get('a',1)))

def text(ctx,e,t,frame):
    a=env(e,t,e.get('fi',.3),e.get('fo',.3))
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('size',20);f=pfont(s*u) if e.get('pixel',True) else font(e.get('font','serif-bold'),s*u)
    draw_text(c,e['text'],e.get('x',512)*u,e.get('y',300)*u,f,e.get('col','#f0f0f8'),a,align=e.get('align','center'),glow=e.get('glow',0)*u)

EXTRA=dict(room=room,hpbar=hpbar,dialog=dialog,menu=menu,dmg=dmg,gameover=gameover,ready=ready,flowchart=flowchart,inspect=inspect,photo=photo,book=book,bubble=bubble,flash=flash,text=text)
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
