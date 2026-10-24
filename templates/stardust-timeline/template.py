"""#1 星尘时间轴 (stardust-timeline) — reference 7690337875291950345 《信息论 惊奇之学》.
Near-black blue night (#010205) with faint star dust & grid, light-weight wide-tracked serif (#e8eceb), gold accents (#ddc79a),
cyan glow (#5ad0e8), crimson signal (#e0405a); glowing horizontal axes with comet dots, typed lines with a glowing
"blank" slot, bilingual subtitles (CN serif + EN italic Garamond), chapter kicker top-left (01 猜 THE GUESS ...)."""
import os, math, random, numpy as np, skia
from engine.core import *
from engine.layers import draw_elements, U, el_text, glyph_points
from engine import richness as RICH

WHITE='#e8eceb'; GOLD='#ddc79a'; CYAN='#5ad0e8'; CRIM='#e0405a'; DIM='#7a8088'
def prepare(S):
    for sc in S['scenes']:
        if sc.get('plate'): sc['_plate']=os.path.join(S['_dir'],sc['plate'])

@lru_cache(2)
def star_tex(W,H):
    rng=np.random.default_rng(2); img=np.zeros((H,W,3),float)
    yy,xx=np.mgrid[0:H,0:W]; img+=np.array([1,2,5])[None,None,:]
    img+=(np.exp(-(((xx-W*.5)/(W*.6))**2+((yy-H*.45)/(H*.6))**2))*6)[:,:,None]*np.array([.6,.8,1.2])
    n=rng.random((H,W)); m=n>.9985; img[m]+=rng.uniform(40,140,(m.sum(),1))
    img+=rng.normal(0,1.2,(H,W,1))
    # faint grid (very subtle)
    s=int(W/64); img[::s,:,:]+=1.2; img[:,::s,:]+=1.2
    return skia.Image.fromarray(np.dstack([img.clip(0,255).astype(np.uint8),np.full((H,W),255,np.uint8)]),colorType=skia.kRGBA_8888_ColorType)

def mountains(ctx,t,a=1.,y0=120,color='#7a9ab0',tower=(800,128)):
    """night ridges (frame-study of ref 75-90s): 5 long-wavelength transparent wire ridges that cross each other,
    soft glow on each stroke, faint navy haze under the top ridge; 烽火台 trestle snapped onto the top ridge"""
    c=ctx.c; u=U(ctx); xs=list(range(-10,1045,6))
    def ridge(k,x):
        rng=random.Random(k*7+3); ph=[rng.uniform(0,6.28) for _ in range(3)]
        amp=[rng.uniform(30,55),rng.uniform(18,30),rng.uniform(5,9)]; wl=[rng.uniform(700,1000),rng.uniform(300,420),rng.uniform(110,160)]
        return sum(amp[i]*math.sin(x/wl[i]*6.283+ph[i]+t*.006*(k+1)) for i in range(3))
    L=[(y0+88+i*60,.50-.06*i,1.25-.1*i) for i in range(5)]
    for k,(base,al,sw) in enumerate(L):
        pts=[(x*u,(base-ridge(k,x))*u) for x in xs]
        path=skia.Path(); path.moveTo(*pts[0]); [path.lineTo(*p) for p in pts[1:]]
        if k<2:
            fill=skia.Path(path); fill.lineTo(1045*u,ctx.H); fill.lineTo(-10*u,ctx.H); fill.close(); top=min(p[1] for p in pts)
            sh=skia.GradientShader.MakeLinear([(0,top),(0,top+170*u)],[hexc('#1a2c3c',a*.30),hexc('#0a121a',0)]); q=skia.Paint(AntiAlias=True); q.setShader(sh); c.drawPath(fill,q)
        c.drawPath(path,paint(color,a*al*.35,stroke=sw*4*u,blur=3.5*u))
        c.drawPath(path,paint(color,a*al,stroke=sw*u))
    if tower:
        x=tower[0]; yb=L[0][0]-ridge(0,x)+3; p=paint('#8ab0c4',a*.8,stroke=1.2*u); h=56; w0,w1=19,13
        segs=[(-w0,0,-w1,-h+12),(w0,0,w1,-h+12),(-w1,-h+12,w1,-h+12),(-w0*.85,-h*.28,w0*.85,-h*.28),(-w0*.85,-h*.28,w1*.9,-h*.62),(w0*.85,-h*.28,-w1*.9,-h*.62),
              (-w1,-h+12,-w1,-h),(w1,-h+12,w1,-h),(-w1,-h,w1,-h)]
        for (x0,y0_,x1,y1) in segs: c.drawLine((x+x0)*u,(yb+y0_)*u,(x+x1)*u,(yb+y1)*u,p)
        TOWER_TOP[:]=[x,yb-h-6]
TOWER_TOP=[800,150]

def bg(ctx,sc,t,frame):
    c=ctx.c; c.drawImage(star_tex(ctx.W,ctx.H),0,0)
    kind=sc.get('bg','stars')
    if kind=='mountains': mountains(ctx,t,sc.get('mt_a',1.),sc.get('mt_y',300),tower=sc.get('tower'))
    if kind=='city':
        # grey overcast city night (ref 91-104s): lighter sky, layered grey blocks, lit windows, TV tower spire
        rng=random.Random(5); u=U(ctx); gy=480
        sh=skia.GradientShader.MakeLinear([(0,0),(0,ctx.H)],[hexc('#1e1f23'),hexc('#2c2d31'),hexc('#141518')],[0,.7,1]); q=skia.Paint(); q.setShader(sh); c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),q)
        for layer,(col,hmin,hmax,wa) in enumerate([('#16171b',60,150,.6),('#0e0f12',40,190,1.0)]):
            x=-10
            while x<1034:
                w=rng.uniform(18,52); h=rng.uniform(hmin,hmax); c.drawRect(skia.Rect.MakeXYWH(x*u,(gy-h)*u,w*u,(h+120)*u),paint(col,1))
                for wy in range(int(gy-h+5),gy,8):
                    for wx in range(int(x+3),int(x+w-3),6):
                        if rng.random()<.11*wa: c.drawRect(skia.Rect.MakeXYWH(wx*u,wy*u,1.6*u,1.6*u),paint('#e8dcb0',.55*wa))
                x+=w+rng.uniform(0,8)
        tx=708; c.drawRect(skia.Rect.MakeXYWH((tx-6)*u,(gy-250)*u,12*u,250*u),paint('#0e0f12',1)); c.drawRect(skia.Rect.MakeXYWH((tx-1.2)*u,(gy-320)*u,2.4*u,72*u),paint('#0e0f12',1))
        c.drawCircle(tx*u,(gy-322)*u,1.6*u,paint('#e84030',.8))
        c.drawRect(skia.Rect.MakeXYWH(0,gy*u,ctx.W,ctx.H-gy*u),paint('#111215',1))
        c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint('#020304',.9 if t<sc.get('lit_at',-1) else .68))   # ref: city stays near-black until the 97.67 'snow' flash
    if kind=='paper':  # warm sepia flash (24s)
        c.clear(hexc('#3a3226')); vignette(c,ctx.W,ctx.H,.6)
    if sc.get('_plate'): draw_image_cover(c,sc['_plate'],ctx.W,ctx.H,sc.get('plate_a',1))
    vignette(c,ctx.W,ctx.H,.45)

def env(e,t,fi=.6,fo=.6): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1.)

def sub2(ctx,e,t,frame):
    """bilingual subtitle: CN serif (light) + EN italic garamond, fade in/out"""
    a=env(e,t,.35,.35)
    if a<=0: return
    u=U(ctx); c=ctx.c
    f=font('serif-vf',e.get('size',19.5)*u,e.get('weight',400)); runs=[]
    tx=e['text']; hl=e.get('hl',[])
    cols=[WHITE]*len(tx)
    for i0,i1,col in hl:
        for i in range(i0,min(i1,len(tx))): cols[i]=col
    tot=f.measureText(tx)+1.2*u*(len(tx)-1); x=512*u-tot/2
    for ch,col in zip(tx,cols): draw_text(c,ch,x,e.get('y',508)*u,f,col if col!=WHITE else '#dcdcd6',a,'left'); x+=f.measureText(ch)+1.2*u
    if e.get('en'): draw_text(c,e['en'],512*u,(e.get('y',508)+19)*u,font('garamond-italic',11.5*u,400),'#9aa0a8',a*.95)

def kicker(ctx,e,t,frame):
    """chapter label top-left: '01  猜  THE GUESS' with thin line"""
    a=env(e,t,.6,.6)
    if a<=0: return
    u=U(ctx); c=ctx.c
    draw_text(c,e['num'],60*u,51*u,font('garamond',12*u,500),GOLD,a,'left')
    line(c,76*u,48*u,92*u,48*u,GOLD,a*.6,.8*u,cap=False)
    draw_text(c,e['zh'],97*u,53*u,font('serif-vf',13*u,500),WHITE,a,'left')
    draw_text(c,e['en'],(97+len(e['zh'])*14+6)*u,52*u,font('garamond',9*u,500),DIM,a,'left',spacing=2*u)

def ltext(ctx,e,t,frame):
    """light-weight wide-tracked serif line (typed) with optional glowing blank slot cycling characters"""
    a=env(e,t,.4,.6)
    if a<=0: return
    u=U(ctx); c=ctx.c; size=e.get('size',28); f=font('serif-vf',size*u,e.get('weight',300)); sp=e.get('spacing',.18)*size*u
    tx=e['text']; n=len(tx); cps=e.get('cps',5); shown=tx if e.get('instant') else tx[:int(clamp((t-e['t0'])*cps,0,n))]
    tot=f.measureText(tx)+sp*(n-1)+(size*1.2*u if e.get('slot') else 0)
    x=e.get('x',512)*u-(tot/2 if e.get('align','center')=='center' else 0); y=e['y']*u
    for i,ch in enumerate(shown):
        ca=a*ease_out_cubic(prog(t,e['t0']+i/cps,.35)) if not e.get('instant') else a
        draw_text(c,ch,x,y,f,e.get('color',WHITE),ca,'left',glow=e.get('glow',0)*u); x+=f.measureText(ch)+sp
    if e.get('slot') and len(shown)==n:
        sx=x+size*.1*u; sl=e['slot']; ks=prog(t,sl['t0'],1)
        if t>=sl['t0']:
            if sl.get('cycle'):  # vertical cycling candidate characters
                ch_list=sl['cycle']; idx=(t-sl['t0'])*sl.get('rate',2.2)
                for j in range(-1,2):
                    k=int(idx)+j; fr=idx-int(idx)
                    ch=ch_list[k%len(ch_list)]; yy=y+(j-fr)*size*1.05*u
                    al=a*(1-abs(j-fr)*.75)
                    draw_text(c,ch,sx+size*.55*u,yy,f,GOLD,max(0,al),'center',glow=10*u,glow_a=.8)
            else:
                draw_text(c,sl.get('char','_'),sx+size*.55*u,y,f,GOLD,a,'center',glow=10*u)
        c.drawCircle(sx+size*.55*u,y-size*.35*u,size*1.1*u,paint('#e0a050',a*.25*(.6+.4*math.sin(t*3)),blur=18*u))
        line(c,sx,y+5*u,sx+size*1.1*u,y+5*u,GOLD if t>=sl.get('t0',1e9) else WHITE,a*.8,1.2*u,cap=False)

def meter(ctx,e,t,frame):
    """small surprise meter: '惊奇 SURPRISE' label, thin track, glowing dot sliding to value, value text"""
    a=env(e,t,.5,.5)
    if a<=0: return
    u=U(ctx); c=ctx.c; x0,x1,y=e.get('x0',372)*u,e.get('x1',652)*u,e.get('y',336)*u
    line(c,x0,y,x1,y,'#3a4a58',a,1*u,cap=False)
    k=ease_in_out_cubic(prog(t,e.get('move_t',e['t0']),e.get('move_dur',1.2))); v=lerp(e.get('v0',0),e.get('v1',0),k)
    col=e.get('color',CYAN); xd=lerp(x0,x1,v)
    if v>0.02: line(c,x0,y,xd,y,col,a,1.6*u,glow=4*u)
    glow_dot(c,xd,y,3*u,col,a,5)
    mixed(c,e.get('tag','惊奇  SURPRISE'),x0+40*u,y-9*u,'garamond',8*u,500,DIM,a,'center')
    draw_text(c,e.get('label','≈ 0 bit'),x1,y-9*u,font('garamond-italic',11*u,400),col,a,'right')

def axis(ctx,e,t,frame):
    """glowing number axis with ticks/labels, optional moving cursor & red eliminated range"""
    a=env(e,t,.6,.6)
    if a<=0: return
    u=U(ctx); c=ctx.c; y=e.get('y',308)*u; X0,X1=e.get('x0',20),e.get('x1',1004)
    lo,hi=e['range'] if 'range' in e else (1,1024)
    if 'zoom' in e:  # [[t,lo,hi],...]
        zs=e['zoom']
        for (ta,la,ha),(tb,lb,hb) in zip(zs,zs[1:]):
            if ta<=t<tb: k=ease_in_out_cubic(prog(t,ta,min(.8,tb-ta))); lo,hi=lerp(la,lb,k),lerp(ha,hb,k); break
        else:
            if t>=zs[-1][0]: lo,hi=zs[-1][1],zs[-1][2]
            else: lo,hi=zs[0][1],zs[0][2]
    def X(v): return (X0+(v-lo)/(hi-lo)*(X1-X0))*u
    kd=ease_in_out_cubic(prog(t,e['t0'],e.get('draw',1.2)))
    col=e.get('color','#e8d8a8')
    line(c,X0*u,y,lerp(X0,X1,kd)*u,y,col,a,1.6*u,glow=5*u)
    step=e.get('step',None) or (10**math.floor(math.log10(max(1e-9,(hi-lo)/5))))
    if (hi-lo)/step>12: step*=2
    v=math.ceil(lo/step)*step
    while v<=hi:
        if X(v)<=lerp(X0,X1,kd)*u: 
            line(c,X(v),y-3*u,X(v),y+3*u,'#a8b0b8',a*.7,.8*u,cap=False)
            draw_text(c,f"{v:.0f}",X(v),y+17*u,font('garamond',10*u,400),'#8a929a',a)
        v+=step
    if 'cut' in e:  # red eliminated half: list of [t, value, side]
        cur=[q for q in e['cut'] if t>=q[0]]
        if cur:
            q=cur[-1]; kk=prog(t,q[0],.5); xv=X(q[1])
            fade=a*.6*(1-prog(t,q[0]+.4,.3))*kk
            if q[2]=='right': c.drawRect(skia.Rect.MakeLTRB(xv,y-14*u,X1*u,y+14*u),paint('#8a2030',fade))
            else: c.drawRect(skia.Rect.MakeLTRB(X0*u,y-14*u,xv,y+14*u),paint('#8a2030',fade))
            line(c,xv,y-18*u,xv,y+18*u,'#e8e0d0',a*kk,1*u)
    if 'dot' in e:
        dv=e['dot']; 
        if isinstance(dv,list):
            for (ta,va),(tb,vb) in zip(dv,dv[1:]):
                if ta<=t<tb: val=lerp(va,vb,ease_in_out_cubic(prog(t,ta,min(.8,tb-ta)))); break
            else: val=dv[-1][1] if t>=dv[-1][0] else dv[0][1]
        else: val=dv
        glow_dot(c,X(val),y,3.2*u,'#ffd890',a,6)

def bigtext(ctx,e,t,frame):
    """big centered value/title in light serif with glow; anim 'particles' for title"""
    ee=dict(type='text',font=e.get('font','serif-vf'),weight=e.get('weight',300),color=e.get('color',WHITE),glow=e.get('glow',0),**{k:v for k,v in e.items() if k not in('type','font','weight','color','glow')})
    el_text(ctx,ee,t,frame)

def comet(ctx,e,t,frame):
    """light dots flying along a horizontal line with trails (title / channel)"""
    a=env(e,t,.4,.6)
    if a<=0: return
    u=U(ctx); c=ctx.c; y=e.get('y',290)*u
    line(c,0,y,ctx.W,y,e.get('line_color','#3a7a9a'),a*e.get('line_a',.5),.8*u,cap=False,glow=2*u)
    for i,(x0,v) in enumerate(e.get('dots',[[0,120]])):
        x=((x0+v*(t-e['t0']))%1100-40)*u; L=e.get('trail',60)*u
        sh=skia.GradientShader.MakeLinear([(x-L,y),(x,y)],[hexc('#9ae0ff',0),hexc('#d8f4ff',a)]); p=skia.Paint(AntiAlias=True); p.setShader(sh); p.setStrokeWidth(2*u); p.setStyle(skia.Paint.kStroke_Style)
        c.drawLine(x-L,y,x,y,p); glow_dot(c,x,y,2.6*u,'#bfeeff',a,5)
    if e.get('bits'):  # floating binary digits above/below
        rng=random.Random(3)
        for i in range(e.get('nbits',96)):
            xx=(rng.random()*1100+t*rng.uniform(6,18))%1100-40; yy=y/u+rng.choice(e.get('rows',[-34,-15,18]))+rng.uniform(-1.5,1.5)
            draw_text(c,rng.choice('01'),xx*u,yy*u,font('garamond',e.get('bit_size',10)*u,500),rng.choice([GOLD,'#e8eceb','#e8eceb']),a*.85)

def binrow(ctx,e,t,frame):
    a=env(e,t,.3,.5)
    if a<=0: return
    u=U(ctx); bits=e['bits']; n=len(bits); k=int(clamp((t-e['t0'])*e.get('cps',3),0,n))
    x0=512-(n-1)*12/2*1.0
    for i in range(e.get('slots',n)):
        x=(512-(e.get('slots',n)-1)*16/2+i*16)*u
        if i<k: draw_text(ctx.c,bits[i],x,e.get('y',368)*u,font('garamond',18*u,500),WHITE,a)
        else: ctx.c.drawCircle(x,(e.get('y',368)-4)*u,1*u,paint('#5a6068',a))

import re as _re
def mixed(c,text,x,y,fname,size,weight,color,a,align='center',spacing=0,glow=0):
    """latin font with CJK fallback to serif-vf (Garamond has no CJK glyphs)"""
    fl=font(fname,size,weight); fc=font('serif-vf',size*.92,max(300,weight or 400) if fname!='serif-vf' else weight)
    if fname.startswith('serif') or not _re.search(r'[\u3000-\u9fff\uff00-\uffef]',text):
        return draw_text(c,text,x,y,fl,color,a,align,spacing=spacing,glow=glow)
    parts=[(ch,fc if _re.match(r'[\u3000-\u9fff\uff00-\uffef]',ch) else fl) for ch in text]
    tot=sum(f.measureText(ch)+spacing for ch,f in parts)-spacing
    xx=x-tot/2 if align=='center' else x-tot if align=='right' else x
    for ch,f in parts: draw_text(c,ch,xx,y,f,color,a,'left',glow=glow); xx+=f.measureText(ch)+spacing
def label(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    u=U(ctx)
    mixed(ctx.c,e['text'],e['x']*u,e['y']*u,e.get('font','serif-vf'),e.get('size',9)*u,e.get('weight',400),e.get('color',WHITE),a,e.get('align','center'),e.get('spacing',0)*u,e.get('glow',0)*u)

def charbars(ctx,e,t,frame):
    """per-character surprise bars under a sentence (cyan small, white tall for unexpected chars)"""
    a=env(e,t,.4,.4)
    if a<=0: return
    u=U(ctx); c=ctx.c; n=e['n']; x0,x1,y=e['x0']*u,e['x1']*u,e['y']*u; tall=set(e.get('tall',[]))
    for i in range(n):
        k=ease_out_cubic(prog(t,e['t0']+i*.06,.4)); x=lerp(x0,x1,i/(n-1)); h=(52 if i in tall else 4+(i*7%4))*u*k
        col='#fff4d8' if i in tall else '#4ab0d0'
        c.drawRect(skia.Rect.MakeXYWH(x-3.5*u,y-h,7*u,h),paint(col,a,blur=(1.5*u if i in tall else 0)))
    line(c,x0-10*u,y+1*u,x1+10*u,y+1*u,'#3a6a80',a*.6,.8*u,cap=False)

def wave(ctx,e,t,frame):
    """signal waveform: 'clean' smooth sine, 'noise' crimson jagged"""
    a=env(e,t,.4,.4)
    if a<=0: return
    u=U(ctx); c=ctx.c; x0,x1,y,amp=e.get('x0',240)*u,e.get('x1',784)*u,e['y']*u,e.get('amp',10)*u
    path=skia.Path(); rng=np.random.default_rng(int(t*12)); n=220
    mix=e.get('noise',0.)
    if 'noise_t' in e: mix=lerp(e['noise_t'][1],e['noise_t'][2],prog(t,e['noise_t'][0],1.5))
    for i in range(n+1):
        x=lerp(x0,x1,i/n); v=math.sin(i*.25+t*2)*(1-mix)+rng.normal(0,1)*mix
        yy=y+v*amp; path.moveTo(x,yy) if i==0 else path.lineTo(x,yy)
    col=e.get('color',CRIM if mix>.3 else '#7ab8d8')
    c.drawPath(path,paint(col,a,stroke=1.1*u)); c.drawPath(path,paint(col,a*.4,stroke=3*u,blur=3*u))

def orbit(ctx,e,t,frame):
    a=env(e,t,.5,.5)
    if a<=0: return
    u=U(ctx); c=ctx.c; x,y,rx,ry=e['x']*u,e['y']*u,e['rx']*u,e['ry']*u
    c.drawOval(skia.Rect.MakeLTRB(x-rx,y-ry,x+rx,y+ry),paint(CYAN,a*.8,stroke=1.2*u)); c.drawOval(skia.Rect.MakeLTRB(x-rx,y-ry,x+rx,y+ry),paint(CYAN,a*.3,stroke=4*u,blur=4*u))
    ang=t*1.3; glow_dot(c,x+math.cos(ang)*rx,y+math.sin(ang)*ry,2.4*u,'#c8f4ff',a,5)

def maskline(ctx,e,t,frame):
    """boxed announcement line where some chars are masked by crimson blocks (noise)"""
    a=env(e,t,.4,.4)
    if a<=0: return
    u=U(ctx); c=ctx.c; tx=e['text']; size=e.get('size',17); f=font('serif-vf',size*u,400); sp=size*.12*u
    tot=f.measureText(tx)+sp*(len(tx)-1); x=512*u-tot/2; y=e['y']*u
    if e.get('box'): rrect(c,x-22*u,y-size*1.15*u,tot+44*u,size*1.9*u,2*u,fill='#12233a',stroke='#3a5a7a',a=a*.9,sw=1*u)
    mask=set(e.get('mask',[])); mk=prog(t,e.get('mask_t',1e9),.3)
    for i,ch in enumerate(tx):
        w=f.measureText(ch)
        if i in mask and mk>0: c.drawRect(skia.Rect.MakeXYWH(x,y-size*.85*u,w,size*1.05*u),paint(CRIM,a*mk*.95))
        else: draw_text(c,ch,x,y,f,WHITE,a,'left')
        x+=w+sp

def scramble(ctx,e,t,frame):
    """typed line where some characters swap (汉字序顺) highlighting kept chars gold"""
    a=env(e,t,.4,.4)
    if a<=0: return
    u=U(ctx); c=ctx.c; tx=e['text']; size=e.get('size',20); f=font('serif-vf',size*u,300); sp=size*.12*u
    if 'alt' in e and t>=e.get('alt_t',1e9): tx=e['alt']
    tot=f.measureText(tx)+sp*(len(tx)-1); x=512*u-tot/2
    keep=set(e.get('keep',[])); dk=prog(t,e.get('dim_t',1e9),.6)
    for i,ch in enumerate(tx):
        col=GOLD if (i in keep and dk>0) else WHITE; al=a*(1-.75*dk if i not in keep else 1)
        draw_text(c,ch,x,e['y']*u,f,col,al,'left'); x+=f.measureText(ch)+sp

def cmb(ctx,e,t,frame):
    """cosmic-microwave-background ellipse (procedural stand-in for a photo/AI asset)"""
    a=env(e,t,.6,.5)
    if a<=0: return
    u=U(ctx); key=('cmb',ctx.W)
    if key not in ctx.cache:
        import cv2
        rng=np.random.default_rng(7); w,h=int(960*u),int(480*u)
        n=sum(cv2.resize(rng.normal(0,1,(h//s+2,w//s+2)),(w,h),interpolation=cv2.INTER_CUBIC)/(i+1)**.55 for i,s in enumerate([60,30,14,7,3]))
        n=(n-n.min())/(n.max()-n.min())
        cmap=np.array([[30,40,160],[80,140,230],[230,230,200],[240,150,60],[200,40,30]],float)
        idx=np.clip(n*4,0,3.999); lo=idx.astype(int); fr=(idx-lo)[:,:,None]; rgb=cmap[lo]*(1-fr)+cmap[lo+1]*fr
        yy,xx=np.mgrid[0:h,0:w]; m=(((xx-w/2)/(w/2))**2+((yy-h/2)/(h/2))**2)<=1
        img=np.dstack([rgb,m*255.]).astype(np.uint8); ctx.cache[key]=skia.Image.fromarray(img,colorType=skia.kRGBA_8888_ColorType)
    img=ctx.cache[key]; p=skia.Paint(); p.setAlphaf(a)
    kf=e.get('kf',[[e['t0'],160,80,e['y']]]); T=[q[0] for q in kf]
    ek=lambda i: float(np.interp(t,T,[q[i] for q in kf]))
    rx,ry,cy=ek(1)*u,ek(2)*u,ek(3)*u
    ctx.c.drawImageRect(img,skia.Rect.MakeLTRB(e['x']*u-rx,cy-ry,e['x']*u+rx,cy+ry),skia.SamplingOptions(skia.FilterMode.kLinear),p)

def noisefield(ctx,e,t,frame):
    a=env(e,t,.3,.4)
    if a<=0: return
    rng=np.random.default_rng(int(t*24)); W,H=ctx.W//4,ctx.H//4
    n=rng.random((H,W))**e.get('pow',6)*e.get('amp',90)+e.get('base',0)
    if e.get('band'):
        yy=np.arange(H)[:,None]/H; n=n*np.exp(-((yy-e['band'][0]/576)/(e['band'][1]/576))**2)
    n=n.clip(0,255).astype(np.uint8); tint=e.get('tint',[1,1,1.1]); img=np.dstack([(n*tint[0]).clip(0,255).astype(np.uint8),(n*tint[1]).clip(0,255).astype(np.uint8),(n*tint[2]).clip(0,255).astype(np.uint8),np.full((H,W),255,np.uint8)])
    p=skia.Paint(); p.setAlphaf(a); p.setBlendMode(skia.BlendMode.kScreen)
    ctx.c.drawImageRect(skia.Image.fromarray(img,colorType=skia.kRGBA_8888_ColorType),skia.Rect.MakeWH(ctx.W,ctx.H),skia.SamplingOptions(),p)

def horn(ctx,e,t,frame):
    """Holmdel horn antenna line drawing + noise scope box"""
    a=env(e,t,.5,.5)
    if a<=0: return
    u=U(ctx); c=ctx.c; x,y=e['x']*u,e['y']*u
    k=e.get('s',1.0); c.save(); c.translate(x,y); c.scale(k,k); c.translate(-x,-y); _horn_body(ctx,e,a,u,c,x,y); c.restore()
def _horn_body(ctx,e,a,u,c,x,y):
    pts=[(-30,60),(-55,-60),(5,-70),(25,55)]; p=skia.Path(); p.moveTo(x+pts[0][0]*u,y+pts[0][1]*u)
    for px,py in pts[1:]: p.lineTo(x+px*u,y+py*u)
    p.close(); c.drawPath(p,paint('#a8d8f0',a,stroke=1.2*u)); c.drawPath(p,paint('#a8d8f0',a*.3,stroke=4*u,blur=3*u))
    for i in range(1,6):
        k=i/6; line(c,x+lerp(-30,-55,k)*u,y+lerp(60,-60,k)*u,x+lerp(25,5,k)*u,y+lerp(55,-70,k)*u,'#a8d8f0',a*.5,.8*u)
    c.drawRect(skia.Rect.MakeXYWH(x-42*u,y+58*u,70*u,8*u),paint('#a8d8f0',a,stroke=1*u))
    line(c,0,y+66*u,ctx.W,y+66*u,'#3a5a70',a*.6,.8*u,cap=False)

def scope(ctx,e,t,frame):
    a=env(e,t,.5,.5)
    if a<=0: return
    u=U(ctx); c=ctx.c; x,y,w,h=[v*u for v in e['box']]
    rrect(c,x,y,w,h,1*u,stroke='#5a8aa0',a=a*.8,sw=1*u)
    wave(ctx,dict(e,type='wave',x0=e['box'][0]+8,x1=e['box'][0]+e['box'][2]-8,y=e['box'][1]+e['box'][3]/2,amp=e['box'][3]*e.get('amp',.22),noise=1,color=CRIM),t,frame)
    if e.get('title'): draw_text(c,e['title'],x+w/2,y-8*u,font('serif',8*u),CRIM,a)

def cards(ctx,e,t,frame):
    """feed cards stack (recommendation stream) + vertical surprise gauge"""
    a=env(e,t,.4,.4)
    if a<=0: return
    u=U(ctx); c=ctx.c
    for i in range(e.get('n',4)):
        k=ease_out_cubic(prog(t,e['t0']+i*.25,.4)); y=(e['y']+i*42)*u
        rrect(c,e['x']*u,y,108*u,34*u,1*u,fill='#16120c',stroke='#8a6a3a',a=a*k,sw=1*u)
        rrect(c,(e['x']+5)*u,y+5*u,24*u,24*u,1*u,fill='#a88050',a=a*k)
        for j in range(3): line(c,(e['x']+36)*u,y+(10+j*7)*u,(e['x']+(96-j*14))*u,y+(10+j*7)*u,'#a8b0c0',a*k*.7,1*u,cap=False)
    gx=e['x']*u+178*u; gy=e['y']*u; gh=160*u; lvl=lerp(1,.03,prog(t,e['t0']+.5,4))
    rrect(c,gx,gy,8*u,gh,1*u,stroke='#5a6068',a=a,sw=1*u); c.drawRect(skia.Rect.MakeXYWH(gx+1*u,gy+gh*(1-lvl),6*u,gh*lvl),paint('#e8c070',a))
    draw_text(c,'惊奇',gx+14*u,gy+gh-14*u,font('serif',8*u),WHITE,a,'left'); draw_text(c,f"{lvl*2.6:.2f} bits",gx+14*u,gy+gh-3*u,font('garamond-italic',8*u),GOLD,a,'left')

def arc(ctx,e,t,frame):
    """semicircle 'map of not-knowing' with lights at towers"""
    a=env(e,t,.6,.6)
    if a<=0: return
    u=U(ctx); c=ctx.c; x,y,r=e['x']*u,e['y']*u,e['r']*u; k=ease_in_out_cubic(prog(t,e['t0'],1.5))
    path=skia.Path(); path.addArc(skia.Rect.MakeLTRB(x-r,y-r,x+r,y+r),180,180*k); c.drawPath(path,paint(CYAN,a*.8,stroke=1.4*u)); c.drawPath(path,paint(CYAN,a*.3,stroke=5*u,blur=4*u))
    ang=math.pi*(1-prog(t,e['t0'],e.get('travel',3))); 
    if ang>0: glow_dot(c,x+math.cos(ang)*r*(-1)*-1,y-math.sin(ang)*r,4*u,'#ffd890',a,6)
    for L in e.get('lights',[]):
        if t>=L['t']: glow_dot(c,L['x']*u,L['y']*u,L.get('r',4)*u,'#ffd890',a*prog(t,L['t'],.5),6)
        if L.get('label') and t>=L['t']: draw_text(c,L['label'],L['x']*u,(L['y']-12)*u,font('serif',7*u),'#c8ccd0',a)

def probe(ctx,e,t,frame):
    a=env(e,t,.5,.5)
    if a<=0: return
    u=U(ctx); c=ctx.c; x,y=e['x']*u,e['y']*u
    c.drawOval(skia.Rect.MakeXYWH(x-6*u,y-14*u,10*u,28*u),paint('#d8e0e8',a,stroke=1.2*u))
    line(c,x+2*u,y,x+40*u,y-14*u,'#d8e0e8',a,1*u); line(c,x+2*u,y,x+40*u,y+12*u,'#d8e0e8',a,1*u)
    c.drawRect(skia.Rect.MakeXYWH(x+40*u,y+10*u,6*u,6*u),paint(GOLD,a,stroke=1*u))

def planet(ctx,e,t,frame):
    a=env(e,t,.5,.5)
    if a>0: glow_dot(ctx.c,e['x']*U(ctx),e['y']*U(ctx),e.get('r',6)*U(ctx),e.get('color','#7ad8ff'),a,5)

def flare(ctx,e,t,frame):
    a=env(e,t,.5,.8)
    if a>0:
        u=U(ctx); c=ctx.c; r=e.get('r',40); x,y=(TOWER_TOP if e.get('at_tower') else (e['x'],e['y']))
        fl=1+.08*math.sin(t*17)+.05*math.sin(t*29) if e.get('fire',True) else 1
        c.drawCircle(x*u,y*u,r*2.4*u*fl,paint('#d88a3a',a*.22,blur=r*1.2*u))
        c.drawCircle(x*u,y*u,r*1.0*u*fl,paint('#ffb455',a*.65,blur=r*.45*u))
        c.drawCircle(x*u,y*u,r*.38*u*fl,paint('#fff4dc',a*.95,blur=r*.12*u))
        c.drawRect(skia.Rect.MakeXYWH((x-r*1.6)*u,(y-.6)*u,r*3.2*u,1.2*u),paint('#ffe0a8',a*.35,blur=1.5*u))
        if e.get('bar'): ctx.c.drawRect(skia.Rect.MakeXYWH((e['x']-1)*u,(e['y']-18)*u,2*u,36*u),paint('#ffe0a0',a*.8,blur=1*u))

def headline(ctx,e,t,frame):
    a=env(e,t,.3,.4)
    if a<=0: return
    u=U(ctx); x,y,w,h=[v*u for v in e['box']]; rrect(ctx.c,x,y,w,h,1*u,fill='#c8304a',a=a*.85)
    draw_text(ctx.c,e['text'],x+w/2,y+h*.68,font('serif-vf',10*u,500),'#ffe8ec',a,spacing=2*u)

def hflash(ctx,e,t,frame):
    """hard-cut light flash (ref 24.03/64.13/86.03/97.67/166.83): instant peak at t0, exponential decay tau"""
    if not (e['t0']<=t<e.get('t1',e['t0']+3)): return
    a=e.get('a',.3)*math.exp(-(t-e['t0'])/e.get('tau',.22))
    p=paint(e.get('color','#ffffff'),a); p.setBlendMode(skia.BlendMode.kScreen); ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),p)


def spark(ctx,e,t,frame):
    a=env(e,t,.3,.3)
    if a<=0: return
    RICH.motes(ctx.c,ctx.W,ctx.H,t,n=e.get('n',55),color=e.get('color','#e8d8a8'),a=a*.45,seed=e.get('seed',7),speed=e.get('speed',1.2))

EXTRA=dict(spark=spark,hflash=hflash,charbars=charbars,sub2=sub2,kicker=kicker,ltext=ltext,meter=meter,axis=axis,bigtext=bigtext,comet=comet,binrow=binrow,label=label,wave=wave,orbit=orbit,
           maskline=maskline,scramble=scramble,cmb=cmb,noisefield=noisefield,horn=horn,scope=scope,cards=cards,arc=arc,probe=probe,planet=planet,flare=flare,headline=headline)

def _render_sc(ctx,sc,t,frame):
    bg(ctx,sc,t,frame)
    draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)

def draw(ctx,t,frame,S):
    ctx.beats=S.get('beats',[])
    c=ctx.c; c.clear(skia.ColorBLACK)
    RICH.compose_scenes(ctx,S,t,frame,_render_sc,overlays_extra=EXTRA,clear=None,
                        vignette_s=.35,grain_a=.035,band_color='#c8a860',design_size=(1024,576))
    for sb in S.get('subtitles',[]):
        if sb['t0']<=t<=sb['t1']: sub2(ctx,sb,t,frame)
    if S.get('beat_punch',False) and getattr(ctx,'beats',None):
        RICH.beat_punch(ctx.c,ctx.W,ctx.H,t,ctx.beats,a=min(S.get('punch_a',.05),.05),color=S.get('punch_col','#e8d8a8'),window=.06)
