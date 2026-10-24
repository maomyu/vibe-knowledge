"""#30 灰阶终端数据 (terminal-gray-data) — ref 7694277028904806730《新鲜感的魔咒》1280x720 115.6s. Topic-agnostic.
Near-black (#07080a) data-terminal look, hard cut to paper-white (#dee0e2) inverted scenes. Light serif for big lines,
small grey sans for labels/meta, [blue] keywords (#8eafec on dark, #475083-ish on white). Widgets: big clock/counter with tiny
sub-label, chat bubbles stacking with timestamps, left text block (kicker + big lines), dot-matrix rows of tiny glyph cells
(counts), noisy vertical spike bar, pill-grid with highlighted share + big percentage, twin water tanks with rising levels,
wave surface and labels, pipe; danmaku coloured floating phrases; teal ocean surface with particle sediment; centred title.
Design space 1024x576."""
import math, random, numpy as np, skia
from engine.core import *
from engine.layers import draw_elements, U, wrap_markup
import engine.richness as RICH

DARK='#07080a'; PAPER='#dee0e2'; INK='#e8e9ea'; GREY='#7d7f83'; DIM='#36393d'; BLUE='#8eafec'; BLUE_W='#4a62c8'
def prepare(S): pass
def env(e,t,fi=.3,fo=.3): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def SR(s,w=300): return font('serif-vf',s,w)
def SN(s,bold=False): return font('sans-bold' if bold else 'sans',s)
def kfi(keys,t):
    if not isinstance(keys,list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def fg(ctx): return '#15171a' if ctx.inv else INK
def bl(ctx): return BLUE_W if ctx.inv else BLUE
def rich(c,ln,x,y,f,a,ctx,col=None,align='left'):
    rs=[];b='';m=0
    for ch in ln:
        if ch=='[': rs.append((b,0)); b=''
        elif ch==']': rs.append((b,1)); b=''
        else: b+=ch
    rs.append((b,0)); tw=sum(f.measureText(s) for s,_ in rs); x=x-tw/2 if align=='center' else x
    for s,m in rs: c.drawString(s,x,y,f,paint(bl(ctx) if m else (col or fg(ctx)),a)); x+=f.measureText(s)
def typed(text,t,t0,cps):
    if not cps: return text
    n=int((t-t0)*cps); out='';k=0
    for ch in text:
        if ch in '[]': out+=ch; continue
        if k>=n: break
        out+=ch; k+=1
    return out

def textblock(ctx,e,t,frame):
    """left block: kicker (small grey) + big serif lines (list; each line may have its own reveal time [text,t])"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',60),e.get('y',200); sz=e.get('size',30); lh=e.get('lh',sz*1.4)
    if e.get('kicker'): draw_text(c,e['kicker'],x*u,(y-sz*1.3)*u,SN(10*u),GREY,a,'left')
    f=SR(sz*u,e.get('weight',350)); yy=y
    for ln in e['lines']:
        txt,t_=(ln if isinstance(ln,list) else [ln,e['t0']])
        k=prog(t,t_,.35)
        if k>0:
            for w in wrap_markup(txt,f,e.get('max_w',420)*u):
                rich(c,typed(w,t,t_,e.get('cps')),x*u,(yy+(1-ease_out_cubic(k))*6)*u,f,a*k,ctx,align=e.get('align','left') if e.get('align')!='center' else 'center'); yy+=lh
        else: yy+=lh
    if e.get('note'): 
        for j,n in enumerate(e['note'] if isinstance(e['note'],list) else [e['note']]): draw_text(c,n,x*u,(yy+6+j*15)*u,SN(9*u),GREY,a*prog(t,e['t0']+.6,.4),'left')
def caption(ctx,e,t,frame):
    """small grey meta caption/subtitle (bottom-left or centred)"""
    a=env(e,t,.2,.2)
    if a<=0: return
    c=ctx.c; u=U(ctx); f=SN(e.get('size',11)*u)
    for j,ln in enumerate(e['text'].split('\n')): rich(c,ln,e.get('x',512)*u,(e.get('y',540)+j*16)*u,f,a,ctx,e.get('color',GREY),e.get('align','center'))
def title(ctx,e,t,frame):
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); f=SR(e.get('size',34)*u,e.get('weight',350)); rich(c,e['text'],e.get('x',512)*u,e.get('y',300)*u,f,a,ctx,align='center')
    if e.get('sub'): draw_text(c,e['sub'],e.get('x',512)*u,(e.get('y',300)+22)*u,SN(8*u),GREY,a)
def clock(ctx,e,t,frame):
    """big number/clock top-left; values=[[t,'23:14']] steps or count {from,to,dur}; sub small text"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',20),e.get('y',70)
    if 'count' in e:
        q=e['count']; v=lerp(q['from'],q['to'],ease_out_cubic(prog(t,e['t0'],q.get('dur',2)))); s=q.get('fmt','{:.0f}').format(v)
    else:
        s=e['values'][0][1]
        for tt,v in e['values']:
            if t>=tt: s=v
    f=SR(e.get('size',30)*u,300); c.drawString(s,x*u,y*u,f,paint(fg(ctx),a))
    if e.get('unit'): c.drawString(e['unit'],x*u+f.measureText(s)+3*u,y*u,SN(9*u),paint(GREY,a))
    if e.get('sub'): draw_text(c,e['sub'],x*u,(y+16)*u,SN(8*u),GREY,a,'left')
def chat(ctx,e,t,frame):
    """chat log: msgs=[[t,text,side('l'|'r'),stamp]] stacked from y; scrolls up when exceeding max_h"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x=e.get('x',512); y0=e.get('y',60); f=SN(e.get('size',12.5)*u); vis=[m for m in e['msgs'] if t>=m[0]]
    step=e.get('step',30); tot=sum(step+(12 if len(m)>3 and m[3] else 0) for m in vis); sh=max(0,tot-e.get('max_h',460))
    yy=y0-sh
    for m in vis:
        k=ease_out_cubic(prog(t,m[0],.25))
        if len(m)>3 and m[3]: draw_text(c,m[3],x*u,(yy+6)*u,SN(6*u),GREY,a*k); yy+=12
        w=f.measureText(m[1])/u+18; side=m[2] if len(m)>2 else 'c'; bx=x-w/2 if side=='c' else (x+e.get('dx',120)-w if side=='r' else x-e.get('dx',120))
        bx+= (1-k)*(10 if side=='r' else -10)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(bx*u,yy*u,w*u,22*u),5*u,5*u),paint(('#d8dadc' if side=='r' else '#3a3d42') if not ctx.inv else '#c8cacc',a*k))
        c.drawString(m[1],(bx+9)*u,(yy+15.5)*u,f,paint('#15171a' if side=='r' else fg(ctx),a*k)); yy+=step
def dotmatrix(ctx,e,t,frame):
    """rows of tiny glyph cells: groups=[[label,count,y]] fills left->right over `fill` s; cols per row"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x0=e.get('x',160); cols=e.get('cols',110); cw=e.get('cw',2.3); ch=e.get('ch',3.6)
    for g in e['groups']:
        lab,n,y=g[0],g[1],g[2]; t_=g[3] if len(g)>3 else e['t0']; k=prog(t,t_,e.get('fill',1.5)); m=int(n*k)
        draw_text(c,lab,x0*u,(y-6)*u,SN(7*u),fg(ctx),a*min(1,k*4),'left')
        pa=skia.Path()
        for i in range(m): r,cc=divmod(i,cols); pa.addRect(skia.Rect.MakeXYWH((x0+cc*cw)*u,(y+r*ch)*u,cw*.7*u,ch*.6*u))
        c.drawPath(pa,paint(GREY,a*.8))
def spike(ctx,e,t,frame):
    """noisy vertical glowing bar (signal column) growing from y1 to y0"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x=e.get('x',512); y0,y1=e.get('y0',4),e.get('y1',230); k=ease_out_cubic(prog(t,e['t0'],e.get('grow',1.2))); r=np.random.RandomState(int(t*8))
    top=y1-(y1-y0)*k
    for yy in np.arange(top,y1,1.5):
        w=1.5+abs(r.randn())*e.get('w',3.5); c.drawRect(skia.Rect.MakeXYWH((x-w/2)*u,yy*u,w*u,1.3*u),paint('#f3e6cf',a*.85))
    c.drawRect(skia.Rect.MakeXYWH((x-6)*u,top*u,12*u,(y1-top)*u),paint('#f3e6cf',a*.15,blur=5*u))
def pillgrid(ctx,e,t,frame):
    """grid of pill dots, `hi` share highlighted (blue dot beside), big percentage counting up, labels"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',60),e.get('y',260); cols,rows=e.get('cols',10),e.get('rows',8); pw,ph,gx,gy=e.get('pw',15),e.get('ph',6.5),e.get('gx',20),e.get('gy',13)
    r=random.Random(e.get('seed',3)); n=cols*rows; hi=set(r.sample(range(n),int(n*e.get('hi',.3)))); k=prog(t,e['t0']+.2,e.get('fill',1.0))
    if e.get('label'): draw_text(c,e['label'],x*u,(y-10)*u,SN(7*u),fg(ctx),a,'left')
    for i in range(int(n*k)):
        rr,cc=divmod(i,cols); px,py=x+cc*gx,y+rr*gy
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(px*u,py*u,pw*u,ph*u),ph/2*u,ph/2*u),paint(fg(ctx),a*.9))
        if i in hi and t>e.get('hi_t',e['t0']+1): c.drawCircle((px+pw+1.5)*u,(py+ph/2)*u,1.2*u,paint(bl(ctx),a))
    if 'pct' in e and t>=e.get('hi_t',e['t0']+1):
        v=e['pct']*ease_out_cubic(prog(t,e.get('hi_t',e['t0']+1),1.0)); s='%d%%'%round(v)
        draw_text(c,s,(x+cols*gx+12)*u,(y+rows*gy*.7)*u,SR(e.get('pct_size',34)*u,300),bl(ctx) if e.get('pct_blue') else fg(ctx),a,'left')
        if e.get('pct_sub'): draw_text(c,e['pct_sub'],(x+cols*gx+12)*u,(y+rows*gy*.7+12)*u,SN(6*u),GREY,a,'left')
def tank(ctx,e,t,frame):
    """water tank: x,y(top),w,h; level keys [[t,frac]]; wave bool; label below; tags=[[t,text]] inside; particles"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,w,h=e.get('x',300),e.get('y',190),e.get('w',90),e.get('h',150); lv=kfi(e.get('level',.2),t)
    p=paint(GREY,a*.8,stroke=.8*u); c.drawLine(x*u,y*u,x*u,(y+h)*u,p); c.drawLine((x+w)*u,y*u,(x+w)*u,(y+h)*u,p); c.drawLine(x*u,(y+h)*u,(x+w)*u,(y+h)*u,p)
    top=y+h-h*lv; pa=skia.Path(); pa.moveTo(x*u,(y+h)*u)
    for i in range(0,int(w)+1,2):
        wy=top+(math.sin(i/9+t*3)*2.2 if e.get('wave') else 0); pa.lineTo((x+i)*u,wy*u)
    pa.lineTo((x+w)*u,(y+h)*u); pa.close()
    g=skia.GradientShader.MakeLinear([(0,top*u),(0,(y+h)*u)],[hexc('#5a5d62',a*.9),hexc('#1c1e21',a*.9)]); q=skia.Paint(AntiAlias=True); q.setShader(g); c.drawPath(pa,q)
    c.drawLine(x*u,top*u,(x+w)*u,top*u,paint('#d8dadc',a*.9,stroke=.9*u))
    for j,(tt,tx) in enumerate(e.get('tags',[])):
        if t>=tt: draw_text(c,tx,(x+w/2)*u,(top+12+j*10)*u,SN(6*u),'#c8cacc',a*prog(t,tt,.3))
    if e.get('particles'):
        r=random.Random(1)
        for i in range(60): c.drawCircle((x+r.uniform(0,w))*u,(top-r.uniform(0,10)+math.sin(t+i))*u,.5*u,paint('#e0e0e0',a*.6))
    if e.get('label'): draw_text(c,e['label'],(x+w/2)*u,(y+h+14)*u,SN(7*u),fg(ctx),a)
    if e.get('head'): draw_text(c,e['head'],x*u,(y-6)*u,SN(6*u),GREY,a,'left')
    if e.get('head_r'): draw_text(c,e['head_r'],(x+w)*u,(y-6)*u,SN(6*u),fg(ctx),a,'right')
def pipe(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x0,x1,y=e['x0'],e['x1'],e['y']; k=prog(t,e['t0'],.6)
    for d in (0,5): c.drawLine(x0*u,(y+d)*u,lerp(x0,x1,k)*u,(y+d)*u,paint(GREY,a,stroke=.7*u))
PAL=['#e2536e','#e8c95a','#7ec7a0','#9f8cf0','#6fb0e8','#d88a5a','#c070c0','#a0d060']
def danmaku(ctx,e,t,frame):
    """coloured floating phrases drifting left, random sizes, pop/fade"""
    a=env(e,t,.4,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); r=random.Random(e.get('seed',5)); W_=e['words']
    for i in range(e.get('n',30)):
        w=W_[i%len(W_)]; st=e['t0']+r.uniform(0,max(.1,(e['t1']-e['t0'])*.6)); x=r.uniform(-50,900)-(t-st)*r.uniform(8,25); y=r.uniform(40,460); sz=r.choice([10,11,13,15,19,24])
        k=prog(t,st,.4)
        if k>0: draw_text(c,w,x*u,y*u,SN(sz*u),r.choice(PAL),a*k*r.uniform(.55,1),'left')
def ocean(ctx,e,t,frame):
    """teal water from surface y down, sparse coloured sediment particles, dim surface line, optional object"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); y=kfi(e.get('y',140),t)
    g=skia.GradientShader.MakeLinear([(0,y*u),(0,ctx.H)],[hexc('#2c4a52',a),hexc('#10242a',a),hexc('#061015',a)],[0,.4,1]); q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeLTRB(0,y*u,ctx.W,ctx.H),q)
    c.drawLine(0,y*u,ctx.W,y*u,paint('#a8c8d0',a*.6,stroke=.8*u)); r=random.Random(7); cx=e.get('cx',512)
    for i in range(e.get('n',1500)):
        px=cx+r.gauss(0,e.get('spread',150)); py=y+abs(r.gauss(0,1))*e.get('depth',260)+math.sin(t*.5+i)*1.5
        c.drawCircle(px*u,py*u,r.uniform(.3,.9)*u,paint(r.choice(PAL),a*r.uniform(.3,.8)))
    if e.get('buoy'): c.drawRect(skia.Rect.MakeXYWH((cx-6)*u,(y-10)*u,12*u,14*u),paint('#c8cacc',a*.8))
    for j,(tt,tx,lx,ly) in enumerate(e.get('labels',[])):
        if t>=tt: draw_text(c,tx,lx*u,ly*u,SN(8*u),INK,a*prog(t,tt,.4),'left')
def bars(ctx,e,t,frame):
    """tiny horizontal meter bars list (right side UI): items=[[label,frac]]"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',780),e.get('y',60)
    for i,(lab,fr) in enumerate(e['items']):
        k=prog(t,e['t0']+i*.08,.4); yy=y+i*12
        draw_text(c,lab,x*u,(yy+4)*u,SN(6*u),GREY,a*k,'left'); c.drawRect(skia.Rect.MakeXYWH((x+50)*u,yy*u,60*fr*k*u,4*u),paint(fg(ctx),a*.8))



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

EXTRA=dict(spark=spark,textblock=textblock,caption=caption,title=title,clock=clock,chat=chat,dotmatrix=dotmatrix,spike=spike,pillgrid=pillgrid,tank=tank,pipe=pipe,danmaku=danmaku,ocean=ocean,bars=bars)

def _render_sc(ctx,sc,t,frame):
    # paper invert bg when scene.invert
    if sc.get('invert'):
        g=skia.GradientShader.MakeRadial((ctx.W*.5,ctx.H*.4),ctx.W*.7,[hexc('#e6e8ea'),hexc('#c9cbcd')]); q=skia.Paint(); q.setShader(g)
        ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),q)
        ctx.inv=True
    else:
        ctx.inv=False
    draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)

def draw(ctx,t,frame,S):
    ctx.beats=S.get('beats',[]); ctx.inv=False
    c=ctx.c; c.clear(hexc(DARK))
    RICH.compose_scenes(ctx,S,t,frame,_render_sc,overlays_extra=EXTRA,clear=None,
                        vignette_s=.35,grain_a=.03,band_color='#8eafec',design_size=(1024,576))
    if S.get('beat_punch',False) and getattr(ctx,'beats',None):
        RICH.beat_punch(ctx.c,ctx.W,ctx.H,t,ctx.beats,a=min(S.get('punch_a',.05),.05),color=S.get('punch_col','#8eafec'),window=.06)
