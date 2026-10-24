"""#4 暗室微光 (dim-room-candle) — ref 7691737108725140762《看懂了熵增》1280x720. Topic-agnostic.
Near-black (#08090b) frames lit by one warm source; serif white captions with warm-gold [..] / tinted {..} keywords;
particle/dot graphics: perspective room with window beam + dust, skyline (lit windows) + overgrowth, glowing pair with thread,
giant particle glyph, coin/dot grid with counter bar, ticker number, falling-particle histogram, formula arch, dot-silhouette
figure + mono readout, chat bubbles, perspective road, dotted sphere, glow dot. Design space 1024x576; fades to black between scenes."""
import math, random, numpy as np, skia
from functools import lru_cache
from engine.core import *
from engine.layers import draw_elements, U, wrap_markup, glyph_points
import engine.richness as RICH

WHITE='#f2ede4'; GOLD='#f0c860'; GREY='#8c857a'; WARM='#ffcf7a'
def prepare(S): pass
def env(e,t,fi=.5,fo=.5): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def F(n,s,w=None): return font(n,s,w)
def R(seed): return random.Random(seed)

def caption(ctx,e,t,frame):
    """centered serif caption, auto-wrap; [gold] {tint}; per-line blur-in (at=[...] relative)"""
    a=env(e,t,.5,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); f=F(e.get('font','serif-vf'),e.get('size',22)*u,e.get('weight',800))
    lines=wrap_markup(e['text'],f,e.get('max_w',820)*u); at=e.get('at'); st=e.get('stagger',.6)
    for i,ln in enumerate(lines):
        tl=e['t0']+(at[min(i,len(at)-1)]+max(0,i-len(at)+1)*st if at else i*st); k=ease_out_cubic(prog(t,tl,.6))
        if k<=0: continue
        runs=[]; mode=None; buf=''
        for ch in ln:
            if ch in '[{': runs.append((buf,mode)); buf=''; mode=ch
            elif ch in ']}': runs.append((buf,mode)); buf=''; mode=None
            else: buf+=ch
        runs.append((buf,mode)); runs=[r for r in runs if r[0]]
        tw=sum(f.measureText(s) for s,_ in runs); al=e.get('align','center')
        x=(e.get('x',512)*u-tw/2) if al=='center' else e.get('x',512)*u; y=(e.get('y',486)+i*e.get('lh',34))*u
        if e.get('check'):   # ✓ bullet drawn left of the line (checklist rows)
            sz=e.get('size',22)*u; cx0=x-sz*1.25; cy0=y-sz*.35; pk=skia.Path(); pk.moveTo(cx0-sz*.35,cy0); pk.lineTo(cx0-sz*.1,cy0+sz*.28); pk.lineTo(cx0+sz*.4,cy0-sz*.32)
            for bl,al_ in ((4*u,.5),(0,1)): c.drawPath(pk,paint(e.get('check_color',GOLD),a*k*al_,stroke=sz*.07,blur=bl))
        for s,m in runs:
            col=e.get('kcolor',GOLD) if m=='[' else e.get('tint','#8fd0e8') if m=='{' else e.get('color',WHITE)
            p=paint(col,a*k,blur=(1-k)*5*u); 
            if e.get('glow',1): c.drawString(s,x,y,f,paint(col,a*k*.35,blur=6*u))
            c.drawString(s,x,y,f,p); x+=f.measureText(s)
def label(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a>0:
        u=U(ctx); draw_text(ctx.c,e['text'],e.get('x',512)*u,e.get('y',300)*u,F(e.get('font','serif-vf'),e.get('size',12)*u,e.get('weight',600)),e.get('color',GREY),a,e.get('align','center'),spacing=e.get('spacing',0)*u)
def ticker(ctx,e,t,frame):
    """mono number that counts / scrambles; 'value' string or from/to; e.g. day counter, big combinatorics number"""
    a=env(e,t,.3,.4)
    if a<=0: return
    u=U(ctx); 
    if 'from' in e:
        k=ease_out_cubic(prog(t,e.get('count_at',e['t0']),e.get('dur',1.5))); v=lerp(e['from'],e['to'],k); s=(e.get('fmt','{:.0f}')).format(v)
    elif e.get('scramble'):
        r=R(int(t*12)); s=''.join(r.choice('0123456789') if ch.isdigit() and t<e.get('settle_at',e['t0']+1) else ch for ch in e['value'])
    else: s=e['value']
    draw_text(ctx.c,e.get('prefix','')+s+e.get('suffix',''),e.get('x',512)*u,e.get('y',300)*u,F(e.get('font','sans-bold'),e.get('size',20)*u),e.get('color',GOLD),a,e.get('align','center'),glow=e.get('glow',4)*u,glow_color='#7a5010')
def dust(c,u,box,t,n=160,seed=1,a=1.,col='#e8d8b0'):
    x0,y0,x1,y1=box; r=R(seed)
    for i in range(n):
        bx,by=r.uniform(x0,x1),r.uniform(y0,y1); ph=r.uniform(0,6.3); sp=r.uniform(.2,.8)
        x=bx+math.sin(t*sp+ph)*6; y=y0+(by-y0+t*sp*4)%(y1-y0)
        c.drawCircle(x*u,y*u,r.uniform(.4,1.1)*u,paint(col,a*(.25+.35*math.sin(t*2+ph)**2)))
def room(ctx,e,t,frame):
    """one-point perspective room: back wall, window (light on/off), light beam, dust, desk + lamp, corner frame; dim → dirty"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); cx,cy=e.get('cx',512),e.get('cy',200); bw,bh=e.get('bw',260),e.get('bh',230)
    L,T,Rr,B=cx-bw/2,cy-bh/2,cx+bw/2,cy+bh/2
    def poly(pts,col,al=1.):
        p=skia.Path(); p.addPoly([skia.Point(x*u,y*u) for x,y in pts],True); c.drawPath(p,paint(col,a*al))
    poly([(0,0),(1024,0),(Rr,T),(L,T)],'#141312'); poly([(0,576),(1024,576),(Rr,B),(L,B)],'#1c1a17')
    poly([(0,0),(L,T),(L,B),(0,576)],'#100f0e'); poly([(1024,0),(Rr,T),(Rr,B),(1024,576)],'#121110')
    c.drawRect(skia.Rect.MakeLTRB(L*u,T*u,Rr*u,B*u),paint('#24221f',a))
    lit=e.get('light',1.)
    wx,wy,ww=cx-38,T+30,76
    c.drawRect(skia.Rect.MakeXYWH(wx*u,wy*u,ww*u,ww*u),paint('#f6dc9a' if lit>.5 else '#4a463e',a))
    for d in (0,): c.drawLine((wx+ww/2)*u,wy*u,(wx+ww/2)*u,(wy+ww)*u,paint('#2a2620',a,stroke=3*u)); c.drawLine(wx*u,(wy+ww/2)*u,(wx+ww)*u,(wy+ww/2)*u,paint('#2a2620',a,stroke=3*u))
    if lit>0:
        c.drawRect(skia.Rect.MakeXYWH((wx-20)*u,(wy-20)*u,(ww+40)*u,(ww+40)*u),paint('#ffd890',a*lit*.35,blur=20*u))
        p=skia.Path(); p.moveTo(wx*u,(wy+ww)*u); p.lineTo((wx+ww)*u,(wy+ww)*u); p.lineTo((cx+150)*u,576*u); p.lineTo((cx-150)*u,576*u); p.close()
        c.drawPath(p,paint('#f0d090',a*lit*.10,blur=14*u))
    if e.get('frame',True): c.drawRect(skia.Rect.MakeXYWH((Rr-55)*u,(T+40)*u,26*u,20*u),paint('#6a6250',a*.8,stroke=1.2*u))
    if e.get('desk',True):
        c.drawRect(skia.Rect.MakeXYWH((cx-70)*u,(B-30)*u,140*u,5*u),paint('#3a3530',a))
        for x in (cx-64,cx+60): c.drawRect(skia.Rect.MakeXYWH(x*u,(B-25)*u,4*u,26*u),paint('#3a3530',a))
        c.drawLine(cx*u,(B-30)*u,(cx+2)*u,(B-52)*u,paint('#6a5a48',a,stroke=1.2*u)); c.drawCircle((cx+2)*u,(B-54)*u,3.5*u,paint('#ff8060',a))
    dust(c,u,(L-60,T,Rr+60,576),t,e.get('dust',150),3,a*e.get('dust_a',1))
    if e.get('dirt',0)>0:   # accumulated grime as speckle on surfaces
        r=R(9)
        for i in range(int(900*e['dirt'])): c.drawCircle(r.uniform(0,1024)*u,r.uniform(B,576)*u,.7*u,paint('#8a8070',a*.35))
def city(ctx,e,t,frame):
    """skyline with lit-window grid; lit fraction; overgrowth (green dot vines) 0..1"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); r=R(e.get('seed',4)); base=e.get('base',470); lit=e.get('lit',1.); og=e.get('grow',0.)
    linear_grad(c,skia.Rect.MakeWH(ctx.W,ctx.H),(0,0),(0,ctx.H),[hexc(e.get('sky','#0c0f14')),hexc('#07080a')])
    x=0
    while x<1024:
        w=r.uniform(40,80); h=r.uniform(90,300); col='#15171b'
        c.drawRect(skia.Rect.MakeXYWH(x*u,(base-h)*u,(w-6)*u,h*u),paint(col,a))
        for wy in np.arange(base-h+10,base-8,13):
            for wx in np.arange(x+6,x+w-12,10):
                v=r.random()
                if v<lit*e.get('density',.55): c.drawRect(skia.Rect.MakeXYWH(wx*u,wy*u,5*u,7*u),paint('#f2c870',a*(.6+.4*r.random())))
        x+=w
    c.drawRect(skia.Rect.MakeLTRB(0,base*u,ctx.W,ctx.H),paint('#07080a',a))
    if og>0:
        for i in range(int(90*og)):
            vx=r.uniform(0,1024); vh=r.uniform(60,260)*og; ph=r.uniform(0,6.3)
            for j in range(int(vh/7)):
                y=base+10-j*7; xx=vx+math.sin(j*.45+ph+t*.6)*6
                c.drawCircle(xx*u,y*u,1.7*u,paint('#5fbf5a',a*.75))
        for i in range(int(24*og)):
            bx=r.uniform(0,1024); br=r.uniform(30,60)*og
            c.drawArc(skia.Rect.MakeXYWH((bx-br)*u,(base-br*.7)*u,2*br*u,1.4*br*u),180,180,False,paint('#4aa04a',a*.6,stroke=1.4*u))
def pair(ctx,e,t,frame):
    """two glowing dots (warm / pink) joined by a sagging thread; sep 0..1 drifts apart, thread fades by 'fray'"""
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); k=ease_in_out_cubic(prog(t,e.get('sep_at',e['t0']),e.get('sep_dur',4.)))
    sep=lerp(e.get('d0',90),e.get('d1',360),k); cx,cy=e.get('x',512),e.get('y',180); x1,x2=cx-sep/2,cx+sep/2
    fray=lerp(1,0,prog(t,e.get('fray_at',1e9),2.))
    if fray>0:
        r=R(2)
        for i in range(60):
            s=i/59; x=lerp(x1,x2,s); y=cy+math.sin(s*math.pi)*e.get('sag',20)
            if r.random()<fray: c.drawCircle(x*u,y*u,.9*u,paint('#e8d0b0',a*.7))
    for x,col in ((x1,e.get('c1','#ffd080')),(x2,e.get('c2','#ff9ab0'))):
        c.drawCircle(x*u,cy*u,16*u,paint(col,a*.35,blur=10*u)); c.drawCircle(x*u,cy*u,3*u,paint('#fff6e8',a))
def dotglyph(ctx,e,t,frame):
    """giant character/word made of particles; assemble from scatter (assemble dur) or scatter away (scatter_at)"""
    a=env(e,t,.5,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); sz=e.get('size',220)
    pts,w,h=glyph_points(e['text'],e.get('font','serif-bold'),int(sz),None,False,e.get('n',2600),1)
    if not len(pts): return
    r=np.random.default_rng(5); sc0=r.uniform([-600,-400],[600,400],(len(pts),2))
    k=ease_out_cubic(prog(t,e['t0'],e.get('assemble',1.6))); ks=ease_in_out_cubic(prog(t,e.get('scatter_at',1e9),2.5))
    P=pts-np.array([w/2-sz/2,0])  # centre
    X=e.get('x',512)-w/2+sz/2+P[:,0]; Y=e.get('y',60)+P[:,1]
    X=X*k+(e.get('x',512)+sc0[:,0])*(1-k); Y=Y*k+(e.get('y',160)+sc0[:,1])*(1-k)
    X+= sc0[:,0]*ks*.8; Y+=sc0[:,1]*ks*.8
    tw=np.sin(t*2+np.arange(len(X))*.7)
    col=hexc(e.get('color','#d8c8a0'),1)
    for i in range(0,len(X)):
        c.drawCircle(float(X[i])*u,float(Y[i])*u,e.get('r',1.1)*u,paint(e.get('color','#d8c8a0'),a*(.55+.35*tw[i])))
def coingrid(ctx,e,t,frame):
    """rows×cols gold coins; heads fraction animates (heads list [[t,frac]]); flipped coins dim"""
    a=env(e,t,.4,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); R_,C_=e.get('rows',10),e.get('cols',10); x0,y0,d=e.get('x0',300),e.get('y0',110),e.get('d',22)
    fr=1.
    for tt,v in e.get('heads',[[0,1.]]):
        if t>=tt: fr=v
    rng=R(e.get('seed',3)); order=list(range(R_*C_)); rng.shuffle(order); nh=int(round(fr*R_*C_)); heads=set(order[:nh])
    for i in range(R_*C_):
        r_,c_=divmod(i,C_); x,y=(x0+c_*d)*u,(y0+r_*d)*u; on=i in heads
        if on: c.drawCircle(x,y,d*.62*u,paint('#ffc040',a*.25,blur=4*u))
        c.drawCircle(x,y,d*.42*u,paint('#f4c45a' if on else '#3a3020',a))
        if on: c.drawCircle(x-d*.1*u,y-d*.1*u,d*.18*u,paint('#fff0b0',a*.6))
    if e.get('bar',True):
        bx=x0+C_*d+30; by=y0+R_*d-10; draw_text(c,e.get('bar_label','正面'),bx*u,by*u,F('serif-vf',9*u,600),GREY,a,'left')
        draw_text(c,f"{nh} / {R_*C_}",(bx+40)*u,by*u,F('sans-bold',12*u),GOLD,a,'left'); c.drawRect(skia.Rect.MakeXYWH(bx*u,(by+8)*u,180*u,1.2*u),paint('#6a5a40',a))
        c.drawRect(skia.Rect.MakeXYWH(bx*u,(by+7.5)*u,180*fr*u,2.2*u),paint(GOLD,a))
def histo(ctx,e,t,frame):
    """particles drop from a source and stack into a bell-shaped histogram over an axis; labels"""
    a=env(e,t,.4,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); x0,x1,yb=e.get('x0',60),e.get('x1',960),e.get('yb',430); n=e.get('n',900); r=np.random.default_rng(1)
    bins=e.get('bins',101); mu=e.get('mu',.5); sd=e.get('sd',.06)
    v=np.clip(r.normal(mu,sd,n),0,1); b=(v*(bins-1)).round().astype(int); order=np.arange(n)
    rate=n/e.get('dur',6.); emitted=int(min(n,(t-e['t0'])*rate)); cnt=np.zeros(bins,int)
    c.drawLine(x0*u,yb*u,x1*u,yb*u,paint('#6a6458',a,stroke=1*u))
    for lab,xx in e.get('xticks',[]): draw_text(c,lab,lerp(x0,x1,xx)*u,(yb+14)*u,F('sans',8*u),GREY,a)
    bw=(x1-x0)/bins; sx=e.get('src_x',(x0+x1)/2)
    for i in range(emitted):
        bi=b[i]; cnt[bi]+=1; age=(t-e['t0'])-i/rate; fall=min(1,age/.9)
        tx=x0+bi*bw+bw/2; ty=yb-cnt[bi]*2.4
        x=lerp(sx,tx,fall); y=lerp(e.get('src_y',80),ty,fall**2)
        c.drawCircle(x*u,y*u,1.1*u,paint('#f4c860',a*(.6 if fall<1 else .9)))
    c.drawCircle(sx*u,yb*u,60*u,paint('#ffc050',a*.12,blur=30*u))
    if e.get('peak'): draw_text(c,e['peak'],(sx)*u,(yb-60)*u,F('serif-vf',10*u,800),GOLD,a*prog(t,e['t0']+2,.5))
def formula(ctx,e,t,frame):
    """big italic formula under a thin arch (tombstone), with legend lines and footnote"""
    a=env(e,t,.6,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); cx,cy=e.get('x',512),e.get('y',260)
    if e.get('arch',True):
        k=ease_in_out_cubic(prog(t,e['t0'],1.2)); p=skia.Path(); r=130
        p.moveTo((cx-r)*u,(cy+140)*u); p.lineTo((cx-r)*u,(cy-20)*u); p.arcTo(skia.Rect.MakeXYWH((cx-r)*u,(cy-150)*u,2*r*u,2*r*u),180,180,False); p.lineTo((cx+r)*u,(cy+140)*u)
        m=skia.PathMeasure(p,False); seg=skia.Path(); m.getSegment(0,m.getLength()*k,seg,True); c.drawPath(seg,paint('#6a6458',a,stroke=1*u))
        c.drawLine((cx-r-60)*u,(cy+140)*u,(cx+r+60)*u,(cy+140)*u,paint('#4a463e',a,stroke=1*u))
    draw_text(c,e['text'],cx*u,cy*u,F('garamond-italic',e.get('size',44)*u,500),WHITE,a,glow=8*u,glow_color='#a08040')
    for i,(s,col) in enumerate(e.get('legend',[])): draw_text(c,s,(cx-60)*u,(cy+38+i*16)*u,F('serif-vf',9*u,600),col,a*prog(t,e['t0']+1+i*.4,.5),'left')
    if e.get('foot'): draw_text(c,e['foot'],cx*u,(cy+160)*u,F('serif-vf',8.5*u,500),GREY,a)
def figure(ctx,e,t,frame):
    """dot-silhouette bust (head+shoulders), warm; warmth 0..1 (cool → grey & dissolving); dissolve 0..1 scatters dots"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); cx,cy,s=e.get('x',512),e.get('y',300),e.get('s',1.)
    pts=_bust(); r=np.random.default_rng(3); off=r.normal(0,1,(len(pts),2))
    ds=ease_in_out_cubic(prog(t,e.get('dissolve_at',1e9),e.get('dissolve_dur',3.)))
    wm=e.get('warmth',1.)
    if 'cool_at' in e: wm=lerp(1,0,prog(t,e['cool_at'],e.get('cool_dur',3.)))
    col='#e8b060' if wm>.5 else '#b8b0a4'
    c.drawCircle(cx*u,(cy+40*s)*u,150*s*u,paint('#ff9a40',a*.10*wm,blur=50*u))
    for i,(px,py) in enumerate(pts):
        x=cx+px*s+off[i,0]*ds*160+math.sin(t+i)*ds*4; y=cy+py*s+off[i,1]*ds*90-ds*20
        c.drawCircle(x*u,y*u,1.0*u,paint(col,a*(.55+.3*math.sin(t*1.5+i))*(1-ds*.4)))
@lru_cache(1)
def _bust():
    out=[]
    for y in np.arange(-150,160,4.2):
        for x in np.arange(-150,150,4.2):
            hd=(x/42)**2+((y+95)/52)**2<1; neck=abs(x)<20 and -50<y<-20
            sh=y>-20 and abs(x)<150*min(1,(y+40)/60)**.4
            if hd or neck or sh: out.append((x,y))
    return out
def readout(ctx,e,t,frame):
    """mono instrument readout (e.g. 体温 37.0°C) bottom-left with underline; value tween from/to"""
    a=env(e,t,.4,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',40),e.get('y',530)
    v=e.get('value')
    if 'from' in e: v=e.get('fmt','{:.1f}').format(lerp(e['from'],e['to'],ease_in_out_cubic(prog(t,e.get('at',e['t0']),e.get('dur',3)))))
    draw_text(c,e.get('head',''),x*u,(y-28)*u,F('sans',8*u),GREY,a,'left')
    draw_text(c,str(v)+e.get('unit',''),x*u,y*u,F('sans-bold',e.get('size',22)*u),e.get('color',GOLD),a,'left',glow=4*u,glow_color='#7a5010')
    c.drawRect(skia.Rect.MakeXYWH(x*u,(y+8)*u,120*u,1*u),paint('#6a5a40',a))
def chat(ctx,e,t,frame):
    """phone chat log: msgs [[t,side('l'|'r'),text,stamp]]; warm bubbles right, grey left; scrolls up as new arrive"""
    a=env(e,t,.4,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); x0,x1=e.get('x0',80),e.get('x1',500); y=e.get('y',40); f=F('serif-vf',e.get('fs',9.5)*u,600)
    shown=[m for m in e['msgs'] if t>=m[0]]; yy=y
    tops=[]
    for m in shown:
        fs=e.get('fs',9.5); lh=fs*1.5; lines=wrap_markup(m[2],f,e.get('bubble_w',240)*u); h=lh*len(lines)+fs
        if len(m)>3 and m[3]: tops.append(('s',m[3],yy)); yy+=16
        tops.append(('m',m,yy,lines,h)); yy+=h+10
    shift=max(0,yy-e.get('max_y',540))
    for it in tops:
        if it[0]=='s': draw_text(c,it[1],(x0+x1)/2*u,(it[2]-shift+8)*u,F('sans',max(7,fs*.65)*u),'#5a564e',a); continue
        _,m,yy0,lines,h=it; k=ease_out_cubic(prog(t,m[0],.35)); yy0-=shift
        w=max(f.measureText(l) for l in lines)/u+18; xl=x0 if m[1]=='l' else x1-w
        fill='#2a2724' if m[1]=='l' else '#a07a3a'; fade=e.get('fade_old',0)
        rrect(c,xl*u,yy0*u,w*u,h*u,6*u,fill=fill,a=a*k)
        for j,l in enumerate(lines): draw_text(c,l,(xl+9)*u,(yy0+fs*.5+lh*.8+j*lh)*u,f,'#e8e2d8' if m[1]=='l' else '#fff4dc',a*k,'left')
def word(ctx,e,t,frame):
    """big glowing statement word with twinkling stars either side"""
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); k=ease_out_cubic(prog(t,e['t0'],.8)); f=F('serif-vf',e.get('size',48)*u,900)
    draw_text(c,e['text'],e.get('x',512)*u,e.get('y',300)*u,f,e.get('color','#cfe8f0'),a*k,glow=10*u,glow_color=e.get('glow_color','#4a7a90'))
    for sx in e.get('stars',[]): 
        tw=.6+.4*math.sin(t*3+sx)
        for ang in range(0,180,45):
            dx,dy=math.cos(math.radians(ang))*9,math.sin(math.radians(ang))*9
            c.drawLine((sx-dx)*u,(e.get('y',300)-14-dy)*u,(sx+dx)*u,(e.get('y',300)-14+dy)*u,paint('#a8c8e0',a*tw*.8,stroke=.8*u))
def road(ctx,e,t,frame):
    """perspective ground plane with grid/speckle, a glowing edge line drawing toward the horizon, lit window at vanishing point"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); hz=e.get('hz',250); vx=e.get('vx',512)
    c.drawRect(skia.Rect.MakeLTRB(0,hz*u,ctx.W,ctx.H),paint(e.get('ground','#1d1913'),a))
    if e.get('road_fill',True):
        p_=skia.Path(); p_.moveTo(0,ctx.H); p_.lineTo((vx-2)*u,hz*u); p_.lineTo((vx+3)*u,hz*u); p_.lineTo(640*u,ctx.H); p_.close(); c.drawPath(p_,paint(e.get('road_color','#211b14'),a))
    if e.get('grid',False):
        for i in range(-20,21): c.drawLine(vx*u,hz*u,(vx+i*90)*u,576*u,paint('#3a3428',a*.5,stroke=.6*u))
        for j in range(1,18): y=hz+(576-hz)*(j/18)**2; c.drawLine(0,y*u,ctx.W,y*u,paint('#3a3428',a*.5,stroke=.6*u))
    r=R(7)
    for i in range(e.get('speck',1400)):
        s=r.random()**1.6; y=hz+s*(576-hz); x=vx+(r.random()-.5)*2*(60+s*900)
        c.drawCircle(x*u,y*u,(.3+s*.9)*u,paint('#8a7c64',a*.5))
    k=ease_in_out_cubic(prog(t,e.get('draw_at',e['t0']),e.get('dur',2.)))
    x0,y0=e.get('edge',[640,576]); x1,y1=lerp(x0,vx+3,k),lerp(y0,hz+2,k)
    c.drawLine(x0*u,y0*u,x1*u,y1*u,paint('#ffd890',a*.4,stroke=6*u,blur=4*u)); c.drawLine(x0*u,y0*u,x1*u,y1*u,paint('#fff0c8',a,stroke=1.4*u))
    if e.get('window',True):
        lit=prog(t,e.get('light_at',1e9),.5); ww=e.get('ww',56)
        c.drawRect(skia.Rect.MakeXYWH((vx-ww/2)*u,(hz-ww*.8-20)*u,ww*u,ww*.8*u),paint('#f6dc9a' if lit else '#4a463e',a))
        if lit: c.drawRect(skia.Rect.MakeXYWH((vx-ww)*u,(hz-ww*1.5-20)*u,2*ww*u,2*ww*u),paint('#ffd890',a*.4*lit,blur=14*u))
        c.drawLine(vx*u,(hz-ww-20)*u,vx*u,(hz-20)*u,paint('#2a2620',a,stroke=2*u)); c.drawLine((vx-ww/2)*u,(hz-ww/2-20)*u,(vx+ww/2)*u,(hz-ww/2-20)*u,paint('#2a2620',a,stroke=2*u))
def sphere(ctx,e,t,frame):
    """dotted rotating sphere (lat/long dots), warm or cool"""
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,r=e.get('x',512),e.get('y',260),e.get('r',50)
    for la in np.linspace(-80,80,9):
        for lo in np.arange(0,360,12):
            l=math.radians(lo+t*e.get('spin',8)); p=math.radians(la); z=math.cos(p)*math.cos(l)
            px=x+r*math.cos(p)*math.sin(l); py=y-r*math.sin(p)
            c.drawCircle(px*u,py*u,.8*u,paint(e.get('color','#d8b878'),a*(.25+.5*(z+1)/2)))
    c.drawCircle(x*u,y*u,r*u,paint(e.get('color','#d8b878'),a*.5,stroke=.8*u))
def glowdot(ctx,e,t,frame):
    a=env(e,t,.6,.6)
    if a<=0: return
    u=U(ctx); x,y=e.get('x',512),e.get('y',500); pl=.8+.2*math.sin(t*2.2)
    ctx.c.drawCircle(x*u,y*u,e.get('r',22)*pl*u,paint(e.get('color','#ff9a50'),a*.35,blur=12*u)); ctx.c.drawCircle(x*u,y*u,2.5*u,paint('#fff0d0',a))
def stars(ctx,e,t,frame):
    a=env(e,t,.6,.6)
    if a<=0: return
    u=U(ctx); r=R(e.get('seed',2))
    for i in range(e.get('n',220)):
        x,y=r.uniform(0,1024),r.uniform(0,576); ph=r.uniform(0,6.3)
        ctx.c.drawCircle(x*u,y*u,r.uniform(.3,.9)*u,paint('#d8d0c0',a*(.2+.25*math.sin(t*1.2+ph)**2)))





def spark(ctx,e,t,frame):
    a=env(e,t,.1,.1)
    if a<=0: return
    import math, random
    col=e.get('color','#ffe0a0')
    RICH.motes(ctx.c,ctx.W,ctx.H,t,n=e.get('n',200),color=col,a=a*e.get('a_mul',1.0),seed=e.get('seed',3),speed=e.get('speed',5.5),blur_k=.4)
    u=ctx.W/1024.; c=ctx.c; H=ctx.H; R=random.Random(e.get('seed',3)+7)
    for i in range(e.get('orbs',30)):
        x=(R.uniform(0,1024)+t*R.uniform(80,200))%1024
        y=(R.uniform(0,576)-t*R.uniform(40,120))%576
        s=R.uniform(4.0,10.0)
        aa=a*R.uniform(.25,.6)*(.5+.5*math.sin(t*5+i))
        c.drawCircle(x*u,y*(H/576.),s*u,paint(col,aa,blur=s*.3*u))
    # large bright comets — dominate 1fps gray diff on dark frames
    for j,spd in enumerate((280,210,160)):
        x=(t*spd + j*200)%1200 - 80
        y=120 + j*140 + 40*math.sin(t*2.2+j)
        for k in range(8):
            c.drawCircle((x-k*10)*u,(y+k*2)*(H/576.), (9-k)*u, paint('#fff6d0', a*(.7-k*.07), blur=4*u))

EXTRA=dict(spark=spark,caption=caption,label=label,ticker=ticker,room=room,city=city,pair=pair,dotglyph=dotglyph,coingrid=coingrid,histo=histo,formula=formula,
           figure=figure,readout=readout,chat=chat,word=word,road=road,sphere=sphere,glowdot=glowdot,stars=stars)

def _render_sc(ctx,sc,t,frame):
    draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)
    # soft scene flash if requested (peak,tau[,col]) — brief, not full-duration beatflash
    if sc.get('flash') and abs(t-sc['t0'])<2.0:
        fl=sc['flash']; fa=fl[0]*math.exp(-(t-sc['t0'])/max(fl[1],.05))
        if fa>.004: ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(fl[2] if len(fl)>2 else '#fff2dc',fa))

def draw(ctx,t,frame,S):
    ctx.beats=S.get('beats',[])
    c=ctx.c; c.clear(hexc(S.get('bg','#08090b')))
    RICH.compose_scenes(ctx,S,t,frame,_render_sc,overlays_extra=EXTRA,clear=None,
                        vignette_s=.45,grain_a=.03,band_color='#f0c860',design_size=(1024,576))
    # permanent ambient comets — force every-frame change on near-black (static→0)
    import math
    u=ctx.W/1024.; H=ctx.H
    for j,spd in enumerate((320,250,190,140)):
        x=(t*spd + j*170)%1300 - 100
        y=90 + j*110 + 35*math.sin(t*2.4+j)
        for k in range(6):
            c.drawCircle((x-k*12)*u,(y+k*1.5)*(H/576.), (8-k)*u, paint('#fff3c8', .55-k*.07, blur=3.5*u))
    if S.get('beat_punch',False) and getattr(ctx,'beats',None):
        RICH.beat_punch(ctx.c,ctx.W,ctx.H,t,ctx.beats,a=min(S.get('punch_a',.05),.05),color=S.get('punch_col','#f0c860'),window=.06)
