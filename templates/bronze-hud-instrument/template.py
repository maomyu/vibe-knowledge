"""#8 暗金仪表盘 (bronze-hud-instrument) — ref 7696889509102816550《专注力训练》1920x1080 370s. Topic-agnostic.
Warm-black stage with a soft amber spotlight (#2f2417 → #090604), faint dust; thin gold-line UI. Persistent header top-left: progress
dashes (chapter i of n) + 'series · section' small text. Bottom caption: serif white with [gold] keywords. Interactive-test widgets:
emblem badge (target / numbered chapter seal), timer box (count up/down), number grid (Schulte), colour-word grid (Stroop) with
progressive reveal, flying digits (memory / interference), card row with ? / glyph reveal, line icons, big word with size keyframes,
character carousel, node diagram (icons + labels + links), framed panels, gauge dial, formula strip. Design space 1024x576."""
import math, random, numpy as np, skia
from engine.core import *
from engine.layers import draw_elements, U, wrap_markup
from engine import richness as RICH

WHITE='#f0ebe2'; GOLD='#e0bd6a'; GOLD2='#a88a4c'; LINE='#8a7046'; GREY='#8a8274'; DIM='#4a4236'
CMAP={'白':'#3a50ff','红':'#ffe14a','绿':'#ff2a2a','黄':'#30ff40','蓝':'#ffffff'}
NAMED={'white':'#f0ebe2','yellow':'#f0e040','green':'#30d070','gold':GOLD,'red':'#e03a30','blue':'#3a50ff','grey':GREY}
def col(c): return NAMED.get(c,c) if isinstance(c,str) else c
def prepare(S): pass
def env(e,t,fi=.4,fo=.4): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def SER(s,w=700): return font('serif-vf',s,w)
def kf(keys,t):
    if not keys: return None
    if not isinstance(keys,list): return keys
    v=keys[0][1]
    for k in keys:
        if t>=k[0]: v=k[1]
    return v
def kfi(keys,t):
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def runs(ln):
    out=[];m=None;b=''
    for ch in ln:
        if ch in '[{': out.append((b,m)); b=''; m=ch
        elif ch in ']}': out.append((b,m)); b=''; m=None
        else: b+=ch
    out.append((b,m)); return [r for r in out if r[0]]
def rich(c,ln,x,y,f,a,align='center',color=WHITE,kcol=GOLD,tcol='#e03a30',glow=0):
    rs=runs(ln); tw=sum(f.measureText(s) for s,_ in rs); x=x-tw/2 if align=='center' else x-tw if align=='right' else x
    for s,m in rs:
        cl=kcol if m=='[' else tcol if m=='{' else color
        if glow: c.drawString(s,x,y,f,paint(cl,a*.4,blur=glow))
        c.drawString(s,x,y,f,paint(cl,a)); x+=f.measureText(s)

# ---------------- chrome ----------------
def header(ctx,e,t,frame):
    """top-left progress dashes (n segments, i lit) + small 'series · section' text"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',14),e.get('y',14); n=e.get('n',6); i=e.get('i',0)
    for j in range(n): c.drawRect(skia.Rect.MakeXYWH((x+j*15)*u,y*u,12*u,1.2*u),paint(GOLD if j<=i else DIM,a*(1 if j<=i else .7)))
    draw_text(c,e.get('text',''),x*u,(y+11)*u,SER(5.5*u,500),GREY,a,'left',spacing=.4*u)
def caption(ctx,e,t,frame):
    """bottom serif caption with [gold]; fades/blur-in; autowrap"""
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c; u=U(ctx); f=SER(e.get('size',24)*u,700); k=ease_out_cubic(prog(t,e['t0'],.4))
    lines=wrap_markup(e['text'],f,e.get('max_w',760)*u); lh=e.get('lh',34); y=e.get('y',528)-(len(lines)-1)*lh
    for j,l in enumerate(lines): rich(c,l,e.get('x',512)*u,(y+j*lh)*u,f,a*k,e.get('align','center'),e.get('color',WHITE),glow=2*u)
def label(ctx,e,t,frame):
    a=env(e,t,.35,.35)
    if a<=0: return
    u=U(ctx); rich(ctx.c,e['text'],e.get('x',512)*u,e.get('y',100)*u,font(e.get('font','serif-vf'),e.get('size',12)*u,e.get('weight',600)),a,e.get('align','center'),col(e.get('color',WHITE)),glow=e.get('glow',0)*u)

# ---------------- widgets ----------------
def emblem(ctx,e,t,frame):
    """gold medallion: kind 'target' (rings+crosshair) | 'number' (seal with text) ; label below, sub; slow rotation of tick ring"""
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,r=e.get('x',512),e.get('y',230),e.get('r',55); k=ease_out_back(prog(t,e['t0'],.7))
    g=skia.GradientShader.MakeRadial((x*u,(y-r*.3)*u),r*1.4*u,[hexc('#6a5028',a),hexc('#2a1e10',a)]); q=skia.Paint(AntiAlias=True); q.setShader(g)
    c.drawCircle(x*u,y*u,r*k*u,paint(GOLD,a*.25,blur=14*u)); c.drawCircle(x*u,y*u,r*k*u,q); c.drawCircle(x*u,y*u,r*k*u,paint(GOLD,a,stroke=1.3*u))
    for i in range(60):
        an=i/60*2*math.pi+(t-e['t0'])*.2; L=(3 if i%5 else 5)
        c.drawLine((x+math.cos(an)*(r*1.12))*u,(y+math.sin(an)*(r*1.12))*u,(x+math.cos(an)*(r*1.12+L))*u,(y+math.sin(an)*(r*1.12+L))*u,paint(GOLD2,a*k*.7,stroke=.6*u))
    if e.get('kind','target')=='target':
        for rr in (.72,.5,.28): c.drawCircle(x*u,y*u,r*rr*k*u,paint(GOLD,a,stroke=.9*u))
        c.drawLine((x-r*.85)*u,y*u,(x+r*.85)*u,y*u,paint(GOLD,a*.6,stroke=.6*u)); c.drawLine(x*u,(y-r*.85)*u,x*u,(y+r*.85)*u,paint(GOLD,a*.6,stroke=.6*u)); c.drawCircle(x*u,y*u,2.5*u,paint(GOLD,a))
    else:
        c.drawCircle(x*u,y*u,r*.78*k*u,paint(GOLD,a*.8,stroke=.8*u)); draw_text(c,str(e.get('text','1')),x*u,(y+r*.3)*u,font('garamond',r*.8*u,600),GOLD,a*k)
    if e.get('label'): draw_text(c,e['label'],x*u,(y+r+e.get('label_dy',30))*u,SER(e.get('label_size',17)*u,700),GOLD,a*prog(t,e['t0']+.3,.5),spacing=2*u,glow=3*u,glow_color='#6a4a10')
    if e.get('sub'): draw_text(c,e['sub'],x*u,(y+r+e.get('label_dy',30)+26)*u,SER(12*u,500),GREY,a*prog(t,e['t0']+.5,.5),spacing=1*u)
def timerbox(ctx,e,t,frame):
    """framed timer: title, value counting from→to over dur (start), unit, progress bar"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,w,h=e.get('x',272),e.get('y',96),112,96; sc_=e.get('s',1.)
    c.save(); c.translate(x*u,y*u); c.scale(sc_,sc_); c.translate(-x*u,-y*u)
    rrect(c,x*u,y*u,w*u,h*u,3*u,fill='#120d07',a=a*.9); rrect(c,x*u,y*u,w*u,h*u,3*u,stroke=LINE,a=a,sw=1*u); rrect(c,(x+3)*u,(y+3)*u,(w-6)*u,(h-6)*u,2*u,stroke='#3a2c18',a=a,sw=.6*u)
    draw_text(c,e.get('title','计时 30 秒'),(x+w/2)*u,(y+20)*u,SER(9*u,600),'#e8dcc0',a)
    c.drawLine((x+12)*u,(y+28)*u,(x+w-12)*u,(y+28)*u,paint(DIM,a,stroke=.6*u))
    st=e.get('start',e['t0']); k=clamp((t-st)/e.get('dur',30)); v=lerp(e.get('from',0),e.get('to',30),k) if t>=st else e.get('from',0)
    draw_text(c,e.get('fmt','{:05.2f}').format(v),(x+w/2-6)*u,(y+62)*u,font('garamond',24*u,500),'#f0dca8',a,glow=3*u,glow_color='#6a4a10')
    draw_text(c,e.get('unit','秒'),(x+w-16)*u,(y+60)*u,SER(7*u),GOLD2,a)
    c.drawRect(skia.Rect.MakeXYWH((x+12)*u,(y+78)*u,(w-24)*u,1.5*u),paint(DIM,a)); c.drawRect(skia.Rect.MakeXYWH((x+12)*u,(y+78)*u,(w-24)*k*u,1.5*u),paint(GOLD,a)); c.restore()
def numgrid(ctx,e,t,frame):
    """number grid (Schulte etc): cells=[[val,color],...] row-major, cols; cell px; hl=[[t,index]] highlights (gold box)"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); n=e.get('cols',5); cells=e['cells']; d=e.get('cell',45); rows_=math.ceil(len(cells)/n)
    x0=e.get('x',512)-n*d/2; y0=e.get('y',288)-rows_*d/2
    c.drawRect(skia.Rect.MakeXYWH(x0*u,y0*u,n*d*u,rows_*d*u),paint('#050403',a*.85))
    for i in range(n+1): c.drawLine((x0+i*d)*u,y0*u,(x0+i*d)*u,(y0+rows_*d)*u,paint('#d8d0c0',a*.85,stroke=.8*u))
    for j in range(rows_+1): c.drawLine(x0*u,(y0+j*d)*u,(x0+n*d)*u,(y0+j*d)*u,paint('#d8d0c0',a*.85,stroke=.8*u))
    f=font('garamond',d*.46*u,500)
    for i,cl in enumerate(cells):
        v,cc=(cl if isinstance(cl,list) else (cl,'white')); x=x0+(i%n+.5)*d; y=y0+(i//n+.5)*d
        k=prog(t,e['t0']+e.get('pop_dt',0)*i,.3)
        draw_text(c,str(v),x*u,(y+d*.16)*u,f,col(cc),a*k)
    for h in e.get('hl',[]):
        if t>=h[0]:
            i=h[1]; x=x0+(i%n)*d; y=y0+(i//n)*d; kk=prog(t,h[0],.25); c.drawRect(skia.Rect.MakeXYWH((x+2)*u,(y+2)*u,(d-4)*u,(d-4)*u),paint(GOLD,a*kk*(.9),stroke=1.6*u))
def wordgrid(ctx,e,t,frame):
    """colour-word grid (Stroop): words row-major, cols; colors per word (ink); reveal keys [[t,count]] → first N words in ink, rest dim grey"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); n=e.get('cols',5); W_=e['words']; dx,dy=e.get('dx',100),e.get('dy',62); x0=e.get('x',512)-(n-1)*dx/2; y0=e.get('y',190)
    N=kf(e.get('reveal',[[e['t0'],0]]),t); inks=e.get('inks',[CMAP.get(w,'#ffffff') for w in W_]); f=SER(e.get('size',42)*u,500)
    for i,w in enumerate(W_):
        x=x0+(i%n)*dx; y=y0+(i//n)*dy; on=i<N
        draw_text(c,w,x*u,y*u,f,col(inks[i]) if on else '#5a5650',a*(1 if on else .75),glow=(3*u if on else 0),glow_color=col(inks[i]))
    if e.get('head'): draw_text(c,e['head'],512*u,(y0-70)*u,SER(16*u,600),'#e8e0d0',a)
    if e.get('counter'): draw_text(c,e['counter'].format(n=N,total=len(W_)),512*u,(y0-50)*u,font('garamond',10*u),GREY,a)
def digits(ctx,e,t,frame):
    """flying digits/chars: items=[[text,x,y,size,t_on,t_off,(color)]]; pop with scale"""
    a=env(e,t,.2,.3)
    if a<=0: return
    c=ctx.c; u=U(ctx)
    for it in e['items']:
        s,x,y,sz,t0,t1=it[:6]; cl=it[6] if len(it)>6 else WHITE
        if not (t0<=t<t1): continue
        k=ease_out_back(prog(t,t0,.25)); kk=fade_env(t,t0,t1,.08,.2)
        draw_text(c,str(s),x*u,(y+sz*.35)*u,font(e.get('font','sans-bold'),sz*k*u+1e-3),col(cl),a*kk)
def cards(ctx,e,t,frame):
    """row of framed cards: items=[[text|'?', reveal_t, (color)]]; flips to text at reveal_t"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); it=e['items']; w,h,gap=e.get('w',90),e.get('h',112),e.get('gap',16); x0=e.get('x',512)-(len(it)*w+(len(it)-1)*gap)/2; y=e.get('y',250)
    for i,ci in enumerate(it):
        x=x0+i*(w+gap); kin=ease_out_cubic(prog(t,e['t0']+i*e.get('dt',.1),.4))
        rrect(c,x*u,(y+(1-kin)*10)*u,w*u,h*u,4*u,fill='#120d07',a=a*kin); rrect(c,x*u,(y+(1-kin)*10)*u,w*u,h*u,4*u,stroke=LINE,a=a*kin,sw=1*u)
        rv=len(ci)>1 and ci[1] is not None and t>=ci[1]; txt=ci[0] if rv or len(ci)<2 or ci[1] is None else '?'
        if len(ci)>1 and ci[1] is None: txt=ci[0]
        fl=1-abs(math.cos(min(1,prog(t,ci[1],.3))*math.pi)) if rv else 0
        draw_text(c,txt,(x+w/2)*u,(y+h/2+9)*u,SER(e.get('size',36)*u,600) if len(txt)<=2 else SER(17*u,600),col(ci[2]) if len(ci)>2 else ('#e8dcc0' if txt!='?' else GOLD2),a*kin)
def icon(ctx,e,t,frame):
    """gold line icon: shape in circle|triangle|diamond|square|eye|shield|book|pen|star; x,y,s; label below"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,s=e.get('x',512),e.get('y',250),e.get('s',30); sh=e.get('shape','circle'); p=paint(col(e.get('color',GOLD)),a,stroke=e.get('w',1.4)*u)
    k=ease_out_cubic(prog(t,e['t0'],.5)); s*=k
    if sh=='circle': c.drawCircle(x*u,y*u,s*u,p)
    elif sh=='square': c.drawRect(skia.Rect.MakeXYWH((x-s)*u,(y-s)*u,2*s*u,2*s*u),p)
    elif sh in('triangle','diamond','star'):
        pts=[(0,-1),(.87,.5),(-.87,.5)] if sh=='triangle' else [(0,-1),(1,0),(0,1),(-1,0)] if sh=='diamond' else [(math.cos(-math.pi/2+i*math.pi/5)*(1 if i%2==0 else .45),math.sin(-math.pi/2+i*math.pi/5)*(1 if i%2==0 else .45)) for i in range(10)]
        q=skia.Path(); q.addPoly([skia.Point((x+px*s)*u,(y+py*s)*u) for px,py in pts],True); c.drawPath(q,p)
    elif sh=='eye':
        q=skia.Path(); q.moveTo((x-s)*u,y*u); q.quadTo(x*u,(y-s*.9)*u,(x+s)*u,y*u); q.quadTo(x*u,(y+s*.9)*u,(x-s)*u,y*u); c.drawPath(q,p); c.drawCircle(x*u,y*u,s*.3*u,p); c.drawCircle(x*u,y*u,s*.1*u,paint(GOLD,a))
    elif sh=='shield':
        q=skia.Path(); q.moveTo(x*u,(y-s)*u); q.lineTo((x+s*.8)*u,(y-s*.65)*u); q.lineTo((x+s*.7)*u,(y+s*.2)*u); q.quadTo((x+s*.4)*u,(y+s*.8)*u,x*u,(y+s)*u); q.quadTo((x-s*.4)*u,(y+s*.8)*u,(x-s*.7)*u,(y+s*.2)*u); q.lineTo((x-s*.8)*u,(y-s*.65)*u); q.close(); c.drawPath(q,p)
    elif sh=='book':
        for sg in (-1,1):
            q=skia.Path(); q.moveTo(x*u,(y-s*.6)*u); q.quadTo((x+sg*s*.5)*u,(y-s*.8)*u,(x+sg*s)*u,(y-s*.6)*u); q.lineTo((x+sg*s)*u,(y+s*.6)*u); q.quadTo((x+sg*s*.5)*u,(y+s*.4)*u,x*u,(y+s*.6)*u); q.close(); c.drawPath(q,p)
            for j in range(4): c.drawLine((x+sg*s*.15)*u,(y-s*.35+j*s*.22)*u,(x+sg*s*.8)*u,(y-s*.4+j*s*.22)*u,paint(GOLD2,a,stroke=.6*u))
    elif sh=='pen':
        c.save(); c.translate(x*u,y*u); c.rotate(-35); g=skia.GradientShader.MakeLinear([(0,-s*.12*u),(0,s*.12*u)],[hexc('#f0d080',a),hexc('#7a5420',a)]); q=skia.Paint(AntiAlias=True); q.setShader(g)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-s*u,-s*.11*u,s*1.6*u,s*.22*u),s*.1*u,s*.1*u),q); pth=skia.Path(); pth.moveTo(s*.6*u,-s*.11*u); pth.lineTo(s*1.0*u,0); pth.lineTo(s*.6*u,s*.11*u); pth.close(); c.drawPath(pth,q); c.restore()
    if e.get('box'): c.drawCircle(x*u,y*u,s*1.6*u,paint(LINE,a,stroke=.8*u))
    if e.get('label'): draw_text(c,e['label'],x*u,(y+s*(1.6 if e.get('box') else 1)+26)*u,SER(e.get('label_size',14)*u,600),col(e.get('label_color','#d8d0c0')),a)
def bigword(ctx,e,t,frame):
    """single big word/char, size keyframes [[t,size]] (smooth), optional x keys; glow"""
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c; u=U(ctx); sz=kfi(e['size'],t) if isinstance(e.get('size'),list) else e.get('size',60); x=kfi(e['x'],t) if isinstance(e.get('x'),list) else e.get('x',512)
    txt=kf(e['text'],t) if isinstance(e['text'],list) else e['text']; rot=kfi(e['rot'],t) if isinstance(e.get('rot'),list) else e.get('rot',0)
    y=e.get('y',300); c.save(); c.rotate(rot,x*u,y*u)
    draw_text(c,txt,x*u,(y+sz*.35)*u,SER(sz*u,e.get('weight',800)),col(e.get('color',WHITE)),a,glow=4*u,glow_color='#6a5020'); c.restore()
    if e.get('sub'): draw_text(c,e['sub'],x*u,(e.get('y',300)+sz*.35+26)*u,SER(8*u,500),GREY,a)
def carousel(ctx,e,t,frame):
    """characters sliding left at speed px/s, spacing; big serif"""
    a=env(e,t,.3,.3)
    if a<=0: return
    c=ctx.c; u=U(ctx); sp=e.get('spacing',170); off=(t-e['t0'])*e.get('speed',120); f=SER(e.get('size',90)*u,800)
    for i,ch in enumerate(e['chars']):
        x=e.get('x0',1100)+i*sp-off
        if -100<x<1124: draw_text(c,ch,x*u,(e.get('y',300)+e.get('size',90)*.35)*u,f,WHITE,a)
def diagram(ctx,e,t,frame):
    """nodes=[{x,y,shape,s,label,at,box}] (icons) and links=[[i,j,at,(style)]] gold hairlines drawn on; optional centre glow"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); N=e['nodes']
    for l in e.get('links',[]):
        i,j,at=l[:3]; k=ease_in_out_cubic(prog(t,at,.6)); x0,y0,x1,y1=N[i]['x'],N[i]['y'],N[j]['x'],N[j]['y']
        if k>0: c.drawLine(x0*u,y0*u,lerp(x0,x1,k)*u,lerp(y0,y1,k)*u,paint(LINE,a,stroke=.8*u))
        if len(l)>3 and l[3]=='arrow' and k>=1:
            an=math.atan2(y1-y0,x1-x0); 
            for sg in (-1,1): c.drawLine(x1*u,y1*u,(x1-8*math.cos(an+sg*.4))*u,(y1-8*math.sin(an+sg*.4))*u,paint(LINE,a,stroke=.8*u))
    for n in N:
        ee=dict(n,type='icon',t0=n.get('at',e['t0']),t1=e['t1'],fi=.4,fo=e.get('fo',.4)); icon(ctx,ee,t,frame)
    if e.get('glow'):
        gx,gy,gr=e['glow']; c.drawCircle(gx*u,gy*u,gr*u,paint('#d0a050',a*.35*(.8+.2*math.sin(t*2)),blur=gr*.5*u))
def panel(ctx,e,t,frame):
    """framed rectangle(s) with title/body: boxes=[{x,y,w,h,title,body,at}]"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx)
    for b in e['boxes']:
        k=ease_out_cubic(prog(t,b.get('at',e['t0']),.5))
        rrect(c,b['x']*u,b['y']*u,b['w']*u,b['h']*u,3*u,fill='#0e0a06',a=a*k*.8); rrect(c,b['x']*u,b['y']*u,b['w']*u,b['h']*u,3*u,stroke=LINE,a=a*k,sw=1*u)
        if b.get('title'): draw_text(c,b['title'],(b['x']+b['w']/2)*u,(b['y']+20)*u,SER(13*u,600),'#e8dcc0',a*k)
        for j,l in enumerate(wrap_markup(b.get('body',''),SER(9*u),(b['w']-16)*u) if b.get('body') else []): rich(c,l,(b['x']+b['w']/2)*u,(b['y']+b['h']/2+j*14+4)*u,SER(b.get('size',9)*u,600),a*k,'center','#d8d0c0')
def dial(ctx,e,t,frame):
    """gauge: arc from a0..a1 deg, needle value keys [[t,0..1]], ticks, centre label, sub"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,r=e.get('x',512),e.get('y',260),e.get('r',120); a0,a1=e.get('a0',150),e.get('a1',390)
    c.drawCircle(x*u,y*u,r*u,paint('#1a120a',a*.8)); c.drawCircle(x*u,y*u,r*u,paint(LINE,a,stroke=1*u)); c.drawCircle(x*u,y*u,r*1.08*u,paint(DIM,a,stroke=.6*u))
    for i in range(41):
        an=math.radians(a0+(a1-a0)*i/40); L=8 if i%5==0 else 4
        c.drawLine((x+math.cos(an)*(r-3))*u,(y+math.sin(an)*(r-3))*u,(x+math.cos(an)*(r-3-L))*u,(y+math.sin(an)*(r-3-L))*u,paint(GOLD2,a,stroke=.7*u))
    v=kfi(e.get('value',[[e['t0'],0],[e['t1'],1]]),t); an=math.radians(a0+(a1-a0)*v)
    c.drawLine(x*u,y*u,(x+math.cos(an)*r*.8)*u,(y+math.sin(an)*r*.8)*u,paint('#e05a40',a,stroke=1.6*u)); c.drawCircle(x*u,y*u,4*u,paint(GOLD,a))
    if e.get('text'): rich(c,e['text'],x*u,(y+r*.45)*u,SER(e.get('size',17)*u,700),a,'center','#e8dcc0')
    if e.get('sub'): draw_text(c,e['sub'],x*u,(y+r+30)*u,SER(13*u,600),GREY,a)
def strip(ctx,e,t,frame):
    """formula strip: items=[[text,at,(color),(size)]] laid out centred with gap; e.g. ['A','+','B','=','C']"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); y=e.get('y',260); gap=e.get('gap',18); its=e['items']
    fs=[SER((it[3] if len(it)>3 else e.get('size',22))*u,700) for it in its]; ws=[f.measureText(it[0])/u for f,it in zip(fs,its)]
    x=e.get('x',512)-(sum(ws)+gap*(len(its)-1))/2
    for f,w,it in zip(fs,ws,its):
        k=prog(t,it[1] if len(it)>1 and it[1] is not None else e['t0'],.4); rich(c,it[0],x*u,y*u,f,a*k,'left',col(it[2]) if len(it)>2 and it[2] else WHITE); x+=w+gap
def rule(ctx,e,t,frame):
    """horizontal rule / timeline with bead dots: x0,x1,y; beads=[[x,label,at]]"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); k=ease_in_out_cubic(prog(t,e['t0'],e.get('draw',.8))); x0,x1,y=e.get('x0',200),e.get('x1',824),e.get('y',290)
    c.drawLine(x0*u,y*u,lerp(x0,x1,k)*u,y*u,paint(LINE,a,stroke=1*u))
    for b in e.get('beads',[]):
        kk=prog(t,b[2] if len(b)>2 else e['t0'],.3); glow_dot(c,b[0]*u,y*u,2.5*u,GOLD,a*kk,3)
        if b[1]: draw_text(c,b[1],b[0]*u,(y+18)*u,SER(12*u,600),'#d8d0c0',a*kk)

def _bg(ctx,S,t):
    c=ctx.c; W,H=ctx.W,ctx.H; b=S.get('bg',{}); u=U(ctx)
    gx,gy=b.get('glow',[.42,.42]); g=skia.GradientShader.MakeRadial((gx*W,gy*H),W*.55,[hexc(b.get('c1','#2c2012')),hexc(b.get('c2','#120c06')),hexc(b.get('c3','#070503'))],[0,.5,1])
    q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeWH(W,H),q)
    r=random.Random(5)
    for i in range(b.get('motes',30)):
        x=(r.random()*1024+t*r.uniform(-3,3))%1024; y=(r.random()*576+t*r.uniform(-3,1))%576
        c.drawCircle(x*u,y*u,r.uniform(.4,1.1)*u,paint('#d8b070',.08+.12*(.5+.5*math.sin(t*r.uniform(.3,1)+i))))

def spark(ctx,e,t,frame):
    a=env(e,t,.3,.3)
    if a<=0: return
    RICH.motes(ctx.c,ctx.W,ctx.H,t,n=e.get('n',40),color=e.get('color','#d8b070'),a=a*.4,seed=e.get('seed',5),speed=e.get('speed',1.1),design_w=1024.,design_h=576.)

EXTRA=dict(spark=spark,header=header,caption=caption,label=label,emblem=emblem,timerbox=timerbox,numgrid=numgrid,wordgrid=wordgrid,digits=digits,cards=cards,icon=icon,
           bigword=bigword,carousel=carousel,diagram=diagram,panel=panel,dial=dial,strip=strip,rule=rule)
def _render_sc(ctx,sc,t,frame):
    draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)

def draw(ctx,t,frame,S):
    ctx.beats=S.get('beats',[])
    _bg(ctx,S,t)
    RICH.compose_scenes(ctx,S,t,frame,_render_sc,overlays_extra=EXTRA,clear=None,
                        vignette_s=.5,grain_a=.03,band_color='#d8b070',design_size=(1024,576))
    if S.get('beat_punch',False) and getattr(ctx,'beats',None):
        RICH.beat_punch(ctx.c,ctx.W,ctx.H,t,ctx.beats,a=min(S.get('punch_a',.05),.05),color=S.get('punch_col','#d8b070'),window=.06)
