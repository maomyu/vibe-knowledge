"""#13 星空配对图谱 (starry-matchmaking-graph) — ref 7690785624487590054《月老的算法》1280x720 143.3s. Topic-agnostic.
Purple-blue night sky (#121430) with twinkling stars, faint milky way, misty mountain silhouettes and a moon; flat
hanfu-style bust avatars; left/right columns of people with name tiles + ranked preference chips; red (dashed=tentative)
curved threads with a 「暂」 tag; gold brush big titles; bottom serif subtitles with {gold} keywords; pill header with
round dots; info panels; gold medal; heart outline; moon-elder silhouette on cloud. Design space 1024x576.

v3 RICHNESS: tin transitions (fade/zoom/wipe/iris/flash/slide), scene.kb Ken Burns,
motes/spark ambient layers, pulse rings, continuous overlays. See RICHNESS_STANDARD.md."""
import math, random, skia
from engine.core import *
from engine.layers import draw_elements, U
from engine import richness as RICH

GOLD='#e8c37a'; RED='#e0453c'; WHITE='#f4efe6'; PANEL='#1a1c3c'
def prepare(S): pass
def env(e,t,fi=.35,fo=.35): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def rich(c,s,x,y,f,a,col=WHITE,hi=GOLD,align='center',glow=0):
    rs=[];b='';m=False
    for ch in s:
        if ch in '{}': rs.append((b,m)); b=''; m=(ch=='{')
        else: b+=ch
    rs.append((b,m)); tw=sum(f.measureText(r) for r,_ in rs); x=x-tw/2 if align=='center' else x
    for r,mm in rs:
        if r: draw_text(c,r,x,y,f,hi if mm else col,a,align='left',glow=glow,glow_color='#000000'); x+=f.measureText(r)

_ST=None
def sky(ctx,e,t,frame):
    global _ST
    c=ctx.c; u=U(ctx); W,H=ctx.W,ctx.H; a=env(e,t,0,0)
    linear_grad(c,skia.Rect.MakeWH(W,H),(0,0),(0,H),[hexc(e.get('top','#0c0d22')),hexc(e.get('mid','#1a1b40')),hexc('#141530')],[0,.6,1])
    if e.get('milky',True):
        p=paint('#6a6aa8',.13*a,blur=60*u); path=skia.Path(); path.moveTo(560*u,-20*u); path.quadTo(470*u,300*u,560*u,600*u); c.drawPath(path,paint('#7a78b8',.10*a,stroke=160*u,blur=70*u))
    if _ST is None:
        R=random.Random(7); _ST=[(R.random(),R.random(),R.random()**3,R.random()*6) for _ in range(260)]
    for x,y,s,ph in _ST:
        k=.5+.5*math.sin(t*1.3+ph*3); c.drawCircle(x*W,y*H*.85,(.5+s*1.6)*u,paint('#ffffff',(.25+.6*k*s+.15)*a))
        if s>.6: c.drawCircle(x*W,y*H*.85,4*u,paint('#c8a0ff',.15*k*a,blur=3*u))
    if e.get('mountains',True):
        for i,(yb,col,al) in enumerate([(470,'#2a2a52',.55),(505,'#1c1d3e',.8)]):
            pth=skia.Path(); pth.moveTo(0,H)
            for xx in range(0,1030,16): pth.lineTo(xx*u,(yb-28*math.sin(xx/97+i*2)-18*math.sin(xx/41+i))*u)
            pth.lineTo(W,H); pth.close(); c.drawPath(pth,paint(col,al*a,blur=2*u))
    m=e.get('moon',[820,62,20])
    if m: moon(c,u,m[0],m[1],m[2],a)
def moon(c,u,x,y,r,a):
    c.drawCircle(x*u,y*u,r*2.2*u,paint('#fff3d0',.10*a,blur=r*u)); c.drawCircle(x*u,y*u,r*u,paint('#e9e1c8',a))
    for dx,dy,rr_ in [(-.3,-.2,.18),(.25,.15,.22),(-.05,.45,.12),(.4,-.35,.1)]: c.drawCircle((x+dx*r)*u,(y+dy*r)*u,rr_*r*u,paint('#cfc5a8',.6*a))
def logo(ctx,e,t,frame):
    c=ctx.c;u=U(ctx);a=env(e,t,0,0)
    rrect(c,25*u,21*u,16*u,16*u,3*u,fill=hexc('#c8343a',a)); draw_text(c,'❖',33*u,34*u,font('sans-bold',10*u),'#ffffff',a)
    draw_text(c,e.get('text','Iwanau'),50*u,34*u,font('serif-bold',15*u),'#ffffff',a,align='left',spacing=1.5*u)
    if e.get('note'):
        f=font('sans',9*u); w=f.measureText(e['note'])/u+16; rrect(c,(998-w)*u,22*u,w*u,18*u,3*u,stroke=hexc('#8888aa',.6*a),fill=hexc('#000000',.2*a),sw=1*u)
        draw_text(c,e['note'],(998-w/2)*u,34.5*u,f,'#d0d0e0',a)
def header(ctx,e,t,frame):
    c=ctx.c;u=U(ctx);a=env(e,t);x,y=e.get('x',512),e.get('y',37);f=font('serif-bold',17*u)
    w=f.measureText(e['text'].replace('{','').replace('}',''))/u+50
    rrect(c,(x-w/2)*u,(y-18)*u,w*u,36*u,18*u,fill=hexc('#0c0d22',.75*a),stroke=hexc(GOLD,.85*a),sw=1.4*u)
    rich(c,e['text'],x*u,(y+6)*u,f,a,WHITE,GOLD)
    if e.get('sub'):
        fs=font('serif-bold',12*u); n=e.get('dots',0); k=int(kfi(e.get('k',0),t)); ws=fs.measureText(e['sub'])/u+(n*9+14 if n else 24)
        rrect(c,(x-ws/2)*u,(y+24)*u,ws*u,22*u,11*u,fill=hexc('#3a1a2c',.85*a),stroke=hexc('#8a3a48',.8*a),sw=1*u)
        draw_text(c,e['sub'],(x-ws/2+12)*u,(y+39)*u,fs,WHITE,a,align='left')
        for i in range(n): c.drawCircle((x+ws/2-14-(n-1-i)*9)*u,(y+35)*u,2.6*u,paint(RED if i<k else '#777788',a))
def person(c,u,x,y,s,g,col,a,mood='smile',hair=0,face='#fbe5d6'):
    S=s*u; X,Y=x*u,y*u
    body=skia.Path(); body.moveTo(X-27*S,Y+38*S); body.quadTo(X-26*S,Y+6*S,X,Y+4*S); body.quadTo(X+26*S,Y+6*S,X+27*S,Y+38*S); body.close()
    c.drawPath(body,paint(col,a)); v=skia.Path(); v.moveTo(X-9*S,Y+5*S); v.lineTo(X,Y+20*S); v.lineTo(X+9*S,Y+5*S); c.drawPath(v,paint('#ffffff',.85*a,stroke=3*S))
    c.drawCircle(X,Y-14*S,20*S,paint(face,a)); hc='#1d1d2e'
    if g=='m':
        p=skia.Path(); p.addArc(skia.Rect.MakeXYWH(X-21*S,Y-36*S,42*S,40*S),180,180); c.drawPath(p,paint(hc,a))
        c.drawRect(skia.Rect.MakeXYWH(X-21*S,Y-17*S,4*S,10*S),paint(hc,a)); c.drawRect(skia.Rect.MakeXYWH(X+17*S,Y-17*S,4*S,10*S),paint(hc,a))
        if hair==1: c.drawCircle(X,Y-37*S,6*S,paint(hc,a))
        if hair==2: c.drawRect(skia.Rect.MakeXYWH(X-21*S,Y-27*S,42*S,5*S),paint('#7aa8d8',a))
    else:
        p=skia.Path(); p.addArc(skia.Rect.MakeXYWH(X-22*S,Y-37*S,44*S,44*S),170,200); c.drawPath(p,paint(hc,a))
        c.drawCircle(X-(16 if hair!=1 else 0)*S,Y-36*S,7*S,paint(hc,a)); c.drawCircle(X+16*S,Y-36*S,7*S,paint(hc,a)) if hair!=1 else None
        c.drawRect(skia.Rect.MakeXYWH(X-22*S,Y-17*S,5*S,18*S),paint(hc,a)); c.drawRect(skia.Rect.MakeXYWH(X+17*S,Y-17*S,5*S,18*S),paint(hc,a))
    st=paint('#2a2a35',a,stroke=1.6*S)
    for sx in (-1,1):
        p=skia.Path()
        if mood=='smile': p.addArc(skia.Rect.MakeXYWH(X+sx*8*S-4*S,Y-14*S,8*S,6*S),200,140)
        else: p.addOval(skia.Rect.MakeXYWH(X+sx*8*S-2*S,Y-14*S,4*S,4*S))
        c.drawPath(p,st if mood=='smile' else paint('#2a2a35',a))
        c.drawCircle(X+sx*13*S,Y-5*S,3.5*S,paint('#f0a0a0',.6*a))
    m=skia.Path()
    if mood=='sad': m.addArc(skia.Rect.MakeXYWH(X-4*S,Y-3*S,8*S,5*S),200,140)
    else: m.addArc(skia.Rect.MakeXYWH(X-4*S,Y-6*S,8*S,6*S),20,140)
    c.drawPath(m,st)
def el_person(ctx,e,t,frame):
    a=env(e,t);
    if a<=0: return
    k=ease_out_back(clamp((t-e['t0'])/.45)); u=U(ctx)
    person(ctx.c,u,e['x'],e['y']+(1-k)*12,e.get('s',1),e.get('g','m'),e.get('col','#6a7ac8'),a,e.get('mood','smile'),e.get('hair',0))
def tile(c,u,x,y,ch,col,a,s=1):
    rrect(c,(x-12*s)*u,(y-15*s)*u,24*s*u,30*s*u,4*u,fill=hexc(col,a)); draw_text(c,ch,x*u,(y+6*s)*u,font('serif-bold',15*s*u),'#1a1a2a',a)
def chip(c,u,x,y,ch,col,a,r=13):
    c.drawCircle(x*u,y*u,r*u,paint(col,a)); draw_text(c,ch,x*u,(y+5)*u,font('serif-bold',13*u),'#1a1a2a',a)
def thread(c,u,p0,p1,bend,k,a,dashed,col=RED,w=2.2):
    pth=skia.Path(); pth.moveTo(p0[0]*u,p0[1]*u); mx,my=(p0[0]+p1[0])/2,(p0[1]+p1[1])/2+bend; pth.quadTo(mx*u,my*u,p1[0]*u,p1[1]*u)
    me=skia.PathMeasure(pth,False); L=me.getLength(); seg=skia.Path(); me.getSegment(0,L*k,seg,True)
    pg=paint(col,.35*a,stroke=w*3*u,blur=4*u); c.drawPath(seg,pg); p=paint(col,a,stroke=w*u)
    if dashed: p.setPathEffect(skia.DashPathEffect.Make([7*u,5*u],0))
    c.drawPath(seg,p); return me
def link(ctx,e,t,frame):
    a=env(e,t,.2,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx); k=ease_in_out_cubic(clamp((t-e['t0'])/e.get('dur',.8)))
    me=thread(c,u,e['p0'],e['p1'],e.get('bend',0),k,a,e.get('dashed',False),e.get('col',RED),e.get('w',2.2))
    if e.get('tag') and k>.95:
        L=me.getLength(); pt,_=me.getPosTan(L*e.get('tag_at',.85)); rrect(c,pt.x()-9*u,pt.y()-9*u,18*u,18*u,3*u,fill=hexc('#3a1410',a),stroke=hexc('#d08050',a),sw=1*u)
        draw_text(c,e['tag'],pt.x(),pt.y()+4.5*u,font('serif-bold',11*u),'#f0d0a0',a)
    if e.get('knot') and k>.95: knot(c,u,e['p1'][0],e['p1'][1],a)
def knot(c,u,x,y,a):
    p=skia.Path(); p.moveTo(x*u,(y-6)*u); p.lineTo((x+6)*u,y*u); p.lineTo(x*u,(y+6)*u); p.lineTo((x-6)*u,y*u); p.close()
    c.drawPath(p,paint(RED,a)); c.drawLine(x*u,(y+6)*u,x*u,(y+16)*u,paint(RED,a,stroke=2*u)); c.drawCircle(x*u,y*u,10*u,paint(RED,.3*a,blur=5*u))
def board(ctx,e,t,frame):
    """rows of people: left/right lists [{name,col,g,hair,prefs:[[ch,col]..],mood}], links [[t0,t1,i,j,'temp'|'ok']], ring/cross/heart [[t0,t1,side,i,k]]"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx); y0,dy=e.get('y0',152),e.get('dy',94); xs=e.get('xs',[165,277,330,692,745,857]); s=e.get('s',1); showp=e.get('prefs',True)
    def anchor(side,i): return (xs[2]+28*s,y0+i*dy-8) if side==0 else (xs[3]-28*s,y0+i*dy-8)
    for L in e.get('links',[]):
        t0,t1,i,j=L[:4]; kind=L[4] if len(L)>4 else 'ok'
        if t0<=t<t1:
            la=a*fade_env(t,t0,t1,.15,.3); k=ease_in_out_cubic(clamp((t-t0)/.8)); p0,p1=anchor(0,i),anchor(1,j)
            me=thread(c,u,p0,p1,(L[5] if len(L)>5 else 20),k,la,kind=='temp',L[6] if len(L)>6 else RED)
            if kind=='temp' and k>.95:
                pt,_=me.getPosTan(me.getLength()*.86); rrect(c,pt.x()-9*u,pt.y()-9*u,18*u,18*u,3*u,fill=hexc('#3a1410',la),stroke=hexc('#d08050',la),sw=1*u); draw_text(c,'暂',pt.x(),pt.y()+4.5*u,font('serif-bold',11*u),'#f0d0a0',la)
    for side,lst in ((0,e.get('left',[])),(1,e.get('right',[]))):
        for i,p in enumerate(lst):
            y=y0+i*dy; px=xs[2] if side==0 else xs[3]; tx=xs[1] if side==0 else xs[4]; bx=xs[0] if side==0 else xs[5]
            dim=1-.55*any(d[0]<=t<d[1] and d[2]==side and d[3]==i for d in e.get('dim',[]))
            person(c,u,px,y-10,s,p.get('g','m' if side==0 else 'f'),p.get('col','#6a8ac8'),a*dim,p.get('mood','smile'),p.get('hair',i%3))
            tile(c,u,tx,y-12,p['name'],p.get('tcol','#7ad0b0'),a*dim)
            if showp and p.get('prefs'):
                n=len(p['prefs']); w=n*34+16; rrect(c,(bx-w/2)*u,(y-38)*u,w*u,52*u,6*u,fill=hexc('#0c0d22',.55*a),stroke=hexc('#5a5a80',.7*a),sw=1*u)
                for k,(ch,cc) in enumerate(p['prefs']):
                    cx=bx-w/2+25+k*34; draw_text(c,str(k+1),cx*u,(y-27)*u,font('sans',7*u),'#aaaacc',a); chip(c,u,cx,y-10,ch,cc,a*dim)
                    for d in e.get('ring',[]):
                        if d[0]<=t<d[1] and d[2]==side and d[3]==i and d[4]==k: c.drawCircle(cx*u,(y-10)*u,16*u,paint(d[5] if len(d)>5 else RED,a,stroke=2*u))
                    for d in e.get('cross',[]):
                        if d[0]<=t<d[1] and d[2]==side and d[3]==i and d[4]==k: c.drawCircle(cx*u,(y-10)*u,13*u,paint('#000000',.45*a)); c.drawLine((cx-10)*u,(y-20)*u,(cx+10)*u,y*u,paint(RED,a,stroke=2*u))
            for d in e.get('heart',[]):
                if d[0]<=t<d[1] and d[2]==side and d[3]==i:
                    hx,hy=px+22,y-44; c.drawCircle(hx*u,hy*u,11*u,paint('#ffffff',a)); heart(c,u,hx,hy+1,.35,a,fill=True)
def heart(c,u,x,y,s,a,fill=False,k=1,col=RED,w=2.5):
    p=skia.Path(); S=s*u; X,Y=x*u,y*u
    p.moveTo(X,Y+22*S); p.cubicTo(X-40*S,Y-5*S,X-22*S,Y-38*S,X,Y-18*S); p.cubicTo(X+22*S,Y-38*S,X+40*S,Y-5*S,X,Y+22*S)
    if fill: c.drawPath(p,paint(col,a)); return
    me=skia.PathMeasure(p,False); seg=skia.Path(); me.getSegment(0,me.getLength()*k,seg,True)
    c.drawPath(seg,paint(col,.4*a,stroke=w*3*u,blur=5*u)); c.drawPath(seg,paint(col,a,stroke=w*u))
def el_heart(ctx,e,t,frame):
    a=env(e,t);
    if a>0: heart(ctx.c,U(ctx),e['x'],e['y'],e.get('s',3),a,e.get('fill',False),ease_in_out_cubic(clamp((t-e['t0'])/e.get('dur',1.5))))
def bigtitle(ctx,e,t,frame):
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c;u=U(ctx); s=e['text']; f=font(e.get('font','brush'),e.get('size',56)*u); n=len(s); tw=f.measureText(s); x=e.get('x',512)*u-tw/2; y=e.get('y',300)*u
    for i,ch in enumerate(s):
        k=clamp((t-e['t0']-i*e.get('stagger',.12))/.5)
        if k>0: draw_text(c,ch,x+f.measureText(s[:i]),y+(1-k)*6*u,f,e.get('col',GOLD),a*k,align='left',glow=10*u,glow_color='#b08030',glow_a=.5)
def sub(ctx,e,t,frame):
    a=env(e,t,.2,.2)
    if a<=0: return
    u=U(ctx); rich(ctx.c,e['text'],e.get('x',512)*u,e.get('y',497)*u,font(e.get('font','serif-bold'),e.get('size',27)*u),a,e.get('col',WHITE),GOLD,glow=4*u)
def note(ctx,e,t,frame):
    a=env(e,t)
    if a>0: u=U(ctx); draw_text(ctx.c,e['text'],e.get('x',512)*u,e.get('y',554)*u,font('serif',e.get('size',10)*u),e.get('col','#b0b0c8'),a,align=e.get('align','center'))
def panel(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e['x'],e['y'],e['w'],e['h']
    rrect(c,x*u,y*u,w*u,h*u,8*u,fill=hexc(e.get('bg',PANEL),.85*a if 'bg' not in e else a),stroke=hexc('#5a5a88',.7*a),sw=1*u)
    if e.get('title'): draw_text(c,e['title'],(x+w/2 if e.get('center',True) else x+16)*u,(y+24)*u,font('serif-bold',e.get('tsize',15)*u),e.get('tcol',GOLD),a,align='center' if e.get('center',True) else 'left')
    for i,L in enumerate(e.get('lines',[])):
        L=L if isinstance(L,list) else [L]; txt=L[0]; col=(L[1] if len(L)>1 and L[1] else WHITE); tk=L[2] if len(L)>2 else e['t0']
        k=clamp((t-tk)/.4)
        if k>0: rich(c,txt,(x+16)*u,(y+e.get('ly',52)+i*e.get('lh',26))*u,font('serif-bold',e.get('size',14)*u),a*k,col,GOLD,align='left')
def medal(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e.get('x',512),e.get('y',230),e.get('r',38); k=ease_out_back(clamp((t-e['t0'])/.6)); R=r*k
    c.drawCircle(x*u,y*u,R*1.8*u,paint('#f0c060',.18*a,blur=R*u))
    c.drawCircle(x*u,y*u,R*u,paint('#c99a3a',a)); c.drawCircle(x*u,y*u,R*.86*u,paint('#e6bc5c',a)); c.drawCircle(x*u,y*u,R*.86*u,paint('#a07020',a,stroke=1.2*u))
    if e.get('year'): draw_text(c,e['year'],x*u,(y+6)*u,font('serif-bold',R*.42*u),'#5a3a10',a)
    for i,(txt,sz,col) in enumerate(e.get('lines',[])): draw_text(c,txt,x*u,(y+r+30+i*20)*u,font('serif-bold',sz*u),col,a)
def elder(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e.get('x',745),e.get('y',165),e.get('r',88); moon(c,u,x,y,r,a)
    ink='#1c1d3e'; p=skia.Path(); p.moveTo((x-55)*u,(y+70)*u); p.quadTo((x-40)*u,(y+5)*u,(x-25)*u,(y-5)*u); p.quadTo((x+5)*u,(y-10)*u,(x+25)*u,(y+60)*u); p.close(); c.drawPath(p,paint(ink,a))
    c.drawCircle((x-28)*u,(y-22)*u,15*u,paint(ink,a)); c.drawCircle((x-28)*u,(y-40)*u,6*u,paint(ink,a)); c.drawLine((x+30)*u,(y-80)*u,(x+22)*u,(y+60)*u,paint(ink,a,stroke=4*u)); c.drawCircle((x+30)*u,(y-82)*u,6*u,paint(ink,a))
    for cx,cy,cr in [(x-80,y+78,26),(x-40,y+70,34),(x+10,y+75,30),(x+60,y+80,26),(x+95,y+86,18)]: c.drawCircle(cx*u,cy*u,cr*u,paint('#222448',a))
    for cx,cy,cr in [(x+10,y-60,18),(x+40,y-66,22),(x+75,y-60,16)]: c.drawCircle(cx*u,cy*u,cr*u,paint('#3a3c66',.9*a))
def avatar(ctx,e,t,frame): return el_person(ctx,e,t,frame)
def el_knot(ctx,e,t,frame):
    a=env(e,t)
    if a>0: knot(ctx.c,U(ctx),e['x'],e['y'],a)
def el_tile(ctx,e,t,frame):
    a=env(e,t)
    if a>0: tile(ctx.c,U(ctx),e['x'],e['y'],e['text'],e.get('col','#7ad0b0'),a,e.get('s',1))
def arrow(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y0,y1=e['x'],e['y0'],e['y1']; c.drawLine(x*u,y0*u,x*u,y1*u,paint(e.get('col','#a0b8e0'),a,stroke=2*u)); d=1 if y1>y0 else -1
    p=skia.Path(); p.moveTo((x-6)*u,(y1-d*9)*u); p.lineTo(x*u,y1*u); p.lineTo((x+6)*u,(y1-d*9)*u); c.drawPath(p,paint(e.get('col','#a0b8e0'),a,stroke=2*u))
def motes(ctx,e,t,frame):
    a=env(e,t,.5,.5)
    if a<=0: return
    RICH.motes(ctx.c,ctx.W,ctx.H,t,n=e.get('n',70),color=e.get('color','#c8a0ff'),a=a*e.get('a',.45),seed=e.get('seed',11),speed=e.get('speed',1.2))
def pulse(ctx,e,t,frame):
    """expanding ring pulse at x,y — visual event beat"""
    a=env(e,t,.15,.4)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e['x'],e['y']; ph=((t-e['t0'])*e.get('rate',.7))%1
    r=e.get('r0',8)+ph*e.get('r1',40); c.drawCircle(x*u,y*u,r*u,paint(e.get('col',GOLD),a*(1-ph)*.8,stroke=2*u)); c.drawCircle(x*u,y*u,(r+6)*u,paint(e.get('col',GOLD),a*(1-ph)*.25,blur=4*u))
def counter(ctx,e,t,frame):
    a=env(e,t); 
    if a<=0: return
    c=ctx.c;u=U(ctx); k=ease_out_cubic(prog(t,e.get('count_at',e['t0']),e.get('dur',1.2)))
    v=int(round(lerp(e.get('from',0),e.get('to',0),k))); txt=e.get('prefix','')+f"{v:,}".replace(',','')+e.get('suffix','')
    draw_text(c,txt,e.get('x',900)*u,e.get('y',80)*u,font('serif-bold',e.get('size',28)*u),e.get('col',GOLD),a,align=e.get('align','right'),glow=6*u,glow_color='#805020')
def chapter(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c;u=U(ctx);k=ease_out_cubic(prog(t,e['t0'],.6));x=e.get('x',990)
    draw_text(c,e.get('no',''),x*u,48*u,font('serif-bold',18*u),GOLD,a*k,'right')
    draw_text(c,e.get('text',''),x*u,68*u,font('serif',11*u),'#d0d0e0',a*k,'right')
def sparkline(ctx,e,t,frame):
    """particles travel along a link path for constant motion"""
    a=env(e,t,.2,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);p0,p1=e['p0'],e['p1']; bend=e.get('bend',20)
    pth=skia.Path(); pth.moveTo(p0[0]*u,p0[1]*u); pth.quadTo(((p0[0]+p1[0])/2)*u,((p0[1]+p1[1])/2+bend)*u,p1[0]*u,p1[1]*u)
    me=skia.PathMeasure(pth,False); L=me.getLength()
    for i in range(e.get('n',5)):
        ph=(t*e.get('speed',.35)+i/e.get('n',5))%1; pt,_=me.getPosTan(L*ph)
        c.drawCircle(pt.x(),pt.y(),2.2*u,paint(e.get('col',GOLD),a*(.4+.6*(1-abs(2*ph-1)))))


def beatflash(ctx,e,t,frame):
    """full-frame punch on listed beat times (or S beats near t)"""
    beats=e.get('beats') or getattr(ctx,'beats',[])
    if not beats: return
    a=e.get('a',.4); col=e.get('col','#c8a0ff'); win=e.get('window',.08)
    b=min(beats,key=lambda x:abs(x-t)); d=abs(t-b)
    if d>win: return
    k=(1-d/win)**1.6
    ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(col,a*k))
def beatrings(ctx,e,t,frame):
    a=env(e,t,.2,.2)
    if a<=0: return
    beats=e.get('beats') or getattr(ctx,'beats',[])
    u=U(ctx)
    for pt in e.get('pts',[[512,288]]):
        RICH.accent_ring(ctx.c,pt[0],pt[1],u,t,beats,e.get('col',GOLD),e.get('r0',10),e.get('span',36),e.get('window',.1))
def driftstars(ctx,e,t,frame):
    """extra drifting star field for density"""
    a=env(e,t,0,0)
    if a<=0: return
    c=ctx.c;u=U(ctx); r=random.Random(e.get('seed',21)); n=e.get('n',120)
    for i in range(n):
        x=(r.uniform(0,1024)+t*r.uniform(-15,25))%1024; y=(r.uniform(0,500)+math.sin(t*.7+i)*.8)%500
        k=.4+.6*math.sin(t*2.5+i); c.drawCircle(x*u,y*u,r.uniform(.4,1.8)*u,paint('#ffffff',a*k*r.uniform(.3,.8)))

EXTRA={'sky':sky,'logo':logo,'header':header,'person':el_person,'link':link,'board':board,'heart':el_heart,'bigtitle':bigtitle,'sub':sub,'note':note,'panel':panel,'medal':medal,'elder':elder,'knot':el_knot,'tile':el_tile,'arrow':arrow,
       'motes':motes,'pulse':pulse,'counter':counter,'chapter':chapter,'sparkline':sparkline,'beatflash':beatflash,'beatrings':beatrings,'driftstars':driftstars}
def _render_sc(ctx,sc,t,frame):
    draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)
def draw(ctx,t,frame,S):
    c=ctx.c; c.clear(hexc('#121430')); ctx.beats=S.get('beats',[])
    draw_elements(ctx,S.get('under',[]),t,frame,EXTRA)
    RICH.compose_scenes(ctx,S,t,frame,_render_sc,overlays_extra=EXTRA,clear=None,
                        vignette_s=.35,grain_a=.03,band_color='#c8a0ff',design_size=(1024,576))
    # NOTE: full-frame RICH.beat_punch + type=beatflash cause eye-pain strobe at ~112 BPM.
# Default beat_punch OFF; if enabled keep punch_a <= 0.05. Prefer local pulses (beatrings/motes/pulse).
    if S.get('beat_punch',False) and ctx.beats:
        RICH.beat_punch(c,ctx.W,ctx.H,t,ctx.beats,a=S.get('punch_a',.05),color=S.get('punch_col','#d8c0ff'),window=.06)
