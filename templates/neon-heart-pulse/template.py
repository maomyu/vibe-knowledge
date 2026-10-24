"""#14 霓虹心跳 (neon-heart-pulse) — ref 7697026270730718514《焦虑的本质是活得太用力》1920x1080 80.9s. Topic-agnostic.
Near-black navy night (#0a0b13) with dust motes + vignette; huge heavy rounded glyph (『心』coral-pink / 『嗯』cream) with
glow, hand-drawn red ring + red handwritten annotation; ECG line sweeping through the glyph; taut "string" between two
pins inside a faint ellipse (tension → snap); tension gauge; RGB-split glitch alarm clock; dark chat app with keyboard
typing / deleting; dim scattered thought words; glowing cupped hands holding / leaking light sand; light iMessage chat
on cream paper; ending cream card. Subtitles bold white with [pink] keywords, optional RGB glitch. Design space 1024x576."""
import math, random, numpy as np, skia
from engine.core import *
from engine.layers import draw_elements, U
import engine.richness as RICH

PINK='#ff5a7a'; CORAL='#ff7a72'; CREAM='#f6eee4'; INK='#0a0b13'; BLUE='#2f86ee'
def prepare(S): pass
def env(e,t,fi=.3,fo=.3): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def SB(s): return font('sans-bold',s)
def rich(c,s,x,y,f,a,col='#ffffff',hi=PINK,align='center',glitch=0):
    rs=[];b='';m=False
    for ch in s:
        if ch in '[]': rs.append((b,m)); b=''; m=(ch=='[')
        else: b+=ch
    rs.append((b,m)); tw=sum(f.measureText(r) for r,_ in rs); x=x-tw/2 if align=='center' else x
    for r,mm in rs:
        if not r: continue
        if glitch:
            draw_text(c,r,x-glitch,y,f,'#ff2040',a*.7,align='left'); draw_text(c,r,x+glitch,y,f,'#20c0ff',a*.7,align='left')
        draw_text(c,r,x,y,f,hi if mm else col,a,align='left'); x+=f.measureText(r)

_D=None
def bg(ctx,e,t,frame):
    global _D
    c=ctx.c;u=U(ctx);W,H=ctx.W,ctx.H;a=env(e,t,0,0);k=e.get('kind','dark')
    if k=='cream':
        c.drawRect(skia.Rect.MakeWH(W,H),paint(e.get('col','#efe6da'),a)); c.drawCircle(W*.5,H*.45,W*.45,paint('#ffffff',.55*a,blur=120*u))
    else:
        c.drawRect(skia.Rect.MakeWH(W,H),paint(e.get('col','#0b0b14'),a))
        if e.get('glow'): gx,gy,gr,gc=e['glow']; c.drawCircle(gx*u,gy*u,gr*u,paint(gc,.35*a,blur=gr*.7*u))
        if _D is None: R=random.Random(3); _D=[(R.random(),R.random(),R.random(),R.random()*6) for _ in range(70)]
        for x,y,s,ph in _D:
            yy=(y-t*.004*(1+s))%1; c.drawCircle(x*W,yy*H,(.6+s*1.4)*u,paint('#c8a8b0',(.10+.25*s)*a*(.6+.4*math.sin(t+ph))))
    if e.get('vignette',True): vignette(c,W,H,.6 if k!='cream' else .25)
def bigchar(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e.get('x',512),e.get('y',290);sz=e.get('size',200)*kfi(e.get('scale',1),t)
    pulse=1+.04*max(0,math.sin((t-e['t0'])*math.pi*2*e.get('bpm',0)/60))**8 if e.get('bpm') else 1
    f=font('sans-bold',sz*pulse*u); col=e.get('col',CORAL); k=ease_out_back(clamp((t-e['t0'])/.5)) if e.get('pop',True) else 1
    c.save(); c.translate(x*u,y*u); c.scale(k,k); c.rotate(e.get('rot',0))
    if e.get('glow',True): draw_text(c,e['text'],0,sz*.36*u,f,col,a*.6,glow=30*u,glow_color=col,glow_a=.7)
    draw_text(c,e['text'],0,sz*.36*u,f,col,a); c.restore()
    if e.get('ring'):
        rk=clamp((t-e.get('ring_t',e['t0']+.3))/.7); r=sz*.92
        if rk>0:
            p=skia.Path()
            for i in range(int(90*rk)+1):
                th=-2.2+i/90*2*math.pi*1.08; rr_=r*(1+.05*math.sin(th*3)); p.lineTo((x+rr_*math.cos(th))*u,(y+rr_*.95*math.sin(th))*u) if i else p.moveTo((x+rr_*math.cos(th))*u,(y+rr_*.95*math.sin(th))*u)
            c.drawPath(p,paint(PINK,.45*a,stroke=7*u,blur=5*u)); c.drawPath(p,paint(PINK,a,stroke=2.5*u))
    an=e.get('annot')
    if an and t>=an.get('t',e['t0']):
        ak=clamp((t-an.get('t',e['t0']))/.4); draw_text(c,an['text'],an['x']*u,an['y']*u,font('brush',an.get('size',22)*u),PINK,a*ak,align='center')
        if an.get('to'): c.drawLine((an['x']+40)*u,(an['y']+8)*u,an['to'][0]*u,an['to'][1]*u,paint(PINK,a*ak,stroke=1.5*u))
def ecg(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);y=e.get('y',270);x0,x1=e.get('x0',0),e.get('x1',1024);amp=e.get('amp',60);bx=e.get('beats',[860]);col=e.get('col',PINK)
    rev=clamp((t-e['t0'])/e.get('draw',.01)); xe=x0+(x1-x0)*rev; p=skia.Path(); p.moveTo(x0*u,y*u)
    gap=e.get('gap',[])
    for xx in np.arange(x0,xe,1.5):
        v=0
        for b in bx:
            d=xx-b; v+= -amp*math.exp(-(d/4)**2)+amp*.45*math.exp(-((d-9)/4)**2)-amp*.15*math.exp(-((d+40)/12)**2)-amp*.18*math.exp(-((d-50)/16)**2)
        if any(g0<=xx<=g1 for g0,g1 in gap): p.moveTo(xx*u,y*u); continue
        p.lineTo(xx*u,(y+v)*u)
    c.drawPath(p,paint(col,.5*a,stroke=5*u,blur=5*u)); c.drawPath(p,paint(col,a,stroke=1.6*u))
    if rev<1: c.drawCircle(xe*u,y*u,5*u,paint('#ffffff',a,blur=3*u))
def string(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);y=e.get('y',290);x0,x1=e.get('x0',80),e.get('x1',944);ten=kfi(e.get('tension',.3),t)
    if e.get('ellipse',True): c.drawOval(skia.Rect.MakeLTRB((x0-30)*u,(y-115)*u,(x1+30)*u,(y+115)*u),paint('#ffffff',.12*a,stroke=1*u))
    col=PINK; snap=e.get('snap')
    if snap is not None and t>=snap:
        k=ease_out_cubic(clamp((t-snap)/.8)); R=random.Random(9)
        for i in range(60):
            ang=R.uniform(0,6.28); sp=R.uniform(20,90)*clamp((t-snap)/1.2); c.drawCircle((512+math.cos(ang)*sp)*u,(y+math.sin(ang)*sp+20*clamp(t-snap))*u,1.8*u,paint('#ffb0a0',a*(1-clamp((t-snap)/2))))
        for side in (-1,1):
            px=x0 if side<0 else x1; p=skia.Path(); p.moveTo(px*u,y*u); p.quadTo((px-side*10)*u,(y+80*k)*u,(px-side*(-30+20*k))*u,(y+170*k)*u); c.drawPath(p,paint(col,.4*a,stroke=5*u,blur=4*u)); c.drawPath(p,paint(col,a,stroke=1.8*u))
    else:
        jit=ten*1.5*math.sin(t*60); g=e.get('glitch',0)
        for dx,cc,al in ([(-g,'#ff2040',.6),(g,'#20c0ff',.6)] if g else [])+[(0,col,1)]:
            c.drawLine(x0*u,(y+dx+jit)*u,x1*u,(y+dx-jit)*u,paint(cc,al*a,stroke=(1+ten*2.5)*u))
        c.drawLine(x0*u,y*u,x1*u,y*u,paint(col,.4*a*ten,stroke=8*u,blur=6*u))
    for px in (x0,x1): c.drawCircle(px*u,y*u,10*u,paint('#ffffff',a,stroke=1.5*u)); c.drawCircle(px*u,y*u,4*u,paint(col,a)); c.drawLine((px-2)*u,(y-12)*u,(px+2)*u,(y+12)*u,paint('#ffffff',a,stroke=1.5*u))
def gauge(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e.get('x',512),e.get('y',95),e.get('r',38);v=kfi(e.get('v',.3),t)
    for i in range(40):
        th=math.pi*(1+i/40); col=['#40c060','#f0c040','#ff4040'][min(2,int(i/14))]; c.drawArc(skia.Rect.MakeXYWH((x-r)*u,(y-r)*u,2*r*u,2*r*u),180+i*4.5,4.6,False,paint(col,a,stroke=4*u))
    th=math.pi*(1+v); c.drawLine(x*u,y*u,(x+r*.85*math.cos(th))*u,(y+r*.85*math.sin(th))*u,paint('#ffffff',a,stroke=2.5*u)); c.drawCircle(x*u,y*u,4*u,paint('#ffffff',a))
    if e.get('label'): draw_text(c,e['label'],x*u,(y+18)*u,font('sans',8*u),'#888888',a)
def clock(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e.get('x',512),e.get('y',180),e.get('r',48);g=e.get('glitch',2)
    for dx,cc,al in [(-g,'#ff2040',.7),(g,'#20c0ff',.7),(0,'#ffffff',1)]:
        X=(x+dx)*u; c.drawCircle(X,y*u,r*u,paint(cc,al*a,stroke=3*u))
        for i in range(12): th=i/12*2*math.pi; c.drawLine(X+r*.8*math.cos(th)*u,y*u+r*.8*math.sin(th)*u,X+r*.92*math.cos(th)*u,y*u+r*.92*math.sin(th)*u,paint(cc,al*a,stroke=2*u))
        h=t*e.get('spin',2); c.drawLine(X,y*u,X+r*.7*math.cos(h)*u,y*u+r*.7*math.sin(h)*u,paint(cc,al*a,stroke=2.5*u)); c.drawLine(X,y*u,X+r*.5*math.cos(h/12-1)*u,y*u+r*.5*math.sin(h/12-1)*u,paint(cc,al*a,stroke=3*u))
    c.drawArc(skia.Rect.MakeXYWH((x-r*1.25)*u,(y-r*1.25)*u,r*2.5*u,r*2.5*u),200+t*90,140,False,paint(PINK,a,stroke=3*u)); c.drawArc(skia.Rect.MakeXYWH((x-r*1.25)*u,(y-r*1.25)*u,r*2.5*u,r*2.5*u),20+t*90,140,False,paint(PINK,a,stroke=3*u))
def bubble(c,u,x,y,text,side,a,dark,size=14,col=None):
    f=font('sans-bold' if dark else 'sans',size*u); w=f.measureText(text)/u+26; h=size+18
    bx=x-w if side=='r' else x; fill=col or ((BLUE if not dark else '#1e5fb0') if side=='r' else ('#e6e6ea' if not dark else '#c8c8cc'))
    rrect(c,bx*u,y*u,w*u,h*u,h/2*u,fill=hexc(fill,a)); tc='#ffffff' if side=='r' else '#111111'
    draw_text(c,text,(bx+w/2)*u,(y+h/2+size*.36)*u,f,tc,a); return h
def chat(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);dark=e.get('dark',False);x0,x1=e.get('x0',300),e.get('x1',724);y=e.get('y',60);sz=e.get('size',14)
    if e.get('panel'):
        px,py,pw,ph=e['panel']; rrect(c,px*u,py*u,pw*u,ph*u,22*u,fill=hexc('#0e0f1a',.95*a),stroke=hexc('#4a4c66',a),sw=2*u)
        c.drawCircle((px+38)*u,(py+30)*u,14*u,paint('#505470',a)); draw_text(c,e.get('name','TA'),(px+70)*u,(py+30)*u,SB(13*u),'#ffffff',a,align='left'); draw_text(c,'在线',(px+70)*u,(py+44)*u,font('sans',8*u),'#40c070',a,align='left')
        c.drawLine((px+12)*u,(py+60)*u,(px+pw-12)*u,(py+60)*u,paint('#4a4c66',a,stroke=1*u))
    if e.get('head'): draw_text(c,e['head'],512*u,(y-25)*u,font('sans',8*u),'#999999',a)
    vis=[m for m in e['msgs'] if t>=m[0] and (len(m)<5 or t<m[4])]; vis=vis[-e.get('max',99):]
    for m in vis:
        k=ease_out_back(clamp((t-m[0])/.35)); side=m[1]; xx=x1 if side=='r' else x0
        c.save(); c.translate(xx*u,(y+10)*u); c.scale(k,k); c.translate(-xx*u,-(y+10)*u)
        h=bubble(c,u,xx,y,m[2],side,a*clamp(k),dark,m[3] if len(m)>3 and m[3] else sz); c.restore(); y+=h+e.get('gap',12)
def keyboard(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w=e.get('x',225),e.get('y',255),e.get('w',575)
    rrect(c,x*u,y*u,w*u,64*u,32*u,fill=hexc('#1a1c30',a),stroke=hexc('#5a5c80',a),sw=2*u); c.drawCircle((x+w-34)*u,(y+32)*u,21*u,paint('#5a5c78',a)); draw_text(c,'↑',(x+w-34)*u,(y+40)*u,SB(20*u),'#ffffff',a)
    txt=''
    for k_ in e.get('typed',[]):
        t0,s=k_[0],k_[1]; mode=k_[2] if len(k_)>2 else 'type'
        if t>=t0:
            n=int(clamp((t-t0)/max(.1,len(s)*.12))*len(s)); txt=s[:n] if mode=='type' else s[:len(s)-n]
    f=font('sans',17*u); draw_text(c,txt,(x+26)*u,(y+38)*u,f,'#ffffff',a,align='left')
    if int(t*2)%2==0: cx=x+28+f.measureText(txt)/u; c.drawLine(cx*u,(y+18)*u,cx*u,(y+46)*u,paint('#ffffff',a,stroke=2*u))
    rows=['qwertyuiop','asdfghjkl','zxcvbnm']; ky=y+88; kw=52
    for ri,row in enumerate(rows):
        off=x+(w-len(row)*(kw+5))/2+(0 if ri<2 else 0)
        for i,ch in enumerate(row): rrect(c,(off+i*(kw+5))*u,ky*u,kw*u,42*u,7*u,fill=hexc('#3a3d58',a)); draw_text(c,ch,(off+i*(kw+5)+kw/2)*u,(ky+27)*u,font('sans',15*u),'#e0e0f0',a)
        ky+=48
    for lab,bx,bw in [('123',x,75),('空格',x+84,340),('发送',x+432,143)]: rrect(c,bx*u,ky*u,bw*u,42*u,7*u,fill=hexc('#2e3048',a)); draw_text(c,lab,(bx+bw/2)*u,(ky+27)*u,font('sans',13*u),'#e0e0f0',a)
def corner(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    u=U(ctx);txt=e['text']
    if e.get('count'): txt=txt.replace('#',str(int(kfi(e['count'],t))))
    draw_text(ctx.c,txt,e.get('x',940)*u,e.get('y',48)*u,font(e.get('font','sans'),e.get('size',22)*u),e.get('col','#7a7a90'),a,align=e.get('align','center'))
    if e.get('sub'): draw_text(ctx.c,e['sub'],e.get('x',940)*u,(e.get('y',48)+16)*u,font('sans',8*u),e.get('col','#7a7a90'),a)
def words(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    R=random.Random(e.get('seed',5));c=ctx.c;u=U(ctx)
    for i in range(e.get('n',40)):
        w=e['items'][i%len(e['items'])]; x=R.uniform(40,980); y=R.uniform(40,540); s=R.uniform(10,18); t0=e['t0']+R.uniform(0,e.get('spread',2))
        k=clamp((t-t0)/.5); draw_text(c,w,x*u,(y-t*2)*u,font('sans',s*u),'#8a8aa0',a*k*R.uniform(.3,.7))
_HP=None
def hands(ctx,e,t,frame):
    """glowing cupped hand holding light sand. fill:[[t,0..1]] level, pour:[t0,t1], leak:[t0,t1], open:[[t,0..1]] spread fingers"""
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,s=e.get('x',512),e.get('y',330),e.get('s',1);op=kfi(e.get('open',0),t);lv=kfi(e.get('fill',.7),t);sq=kfi(e.get('squeeze',0),t)
    c.drawCircle(x*u,(y-20)*u,180*s*u,paint('#ff9a50',.25*a*(.4+lv),blur=90*u))
    G='#f0a868'
    def limb(x0,y0,x1,y1,w=26):
        X0,Y0,X1,Y1=x0*u,y0*u,x1*u,y1*u
        for pp in (paint(G,.55*a,stroke=(w+10)*s*u,blur=9*u),paint(G,.95*a,stroke=(w+3)*s*u),paint('#3a2622',a,stroke=w*s*u)):
            pp.setStrokeCap(skia.Paint.kRound_Cap); c.drawLine(X0,Y0,X1,Y1,pp)
    # forearm + palm
    pal=skia.Path(); pal.moveTo((x-115*s)*u,(y+80*s)*u); pal.quadTo(x*u,(y+120*s)*u,(x+120*s)*u,(y+60*s)*u); pal.lineTo((x+520)*u,(y+80)*u); pal.lineTo((x+520)*u,(y+260)*u); pal.lineTo((x-60*s)*u,(y+200*s)*u); pal.close()
    c.drawPath(pal,paint('#1e1616',a)); c.drawPath(pal,paint(G,.7*a,stroke=2*u)); c.drawPath(pal,paint(G,.3*a,stroke=8*u,blur=8*u))
    spread=60*op-40*sq
    limb(x-115*s,y+80*s,x-150*s-spread,y-60*s,30); limb(x-150*s-spread,y-60*s,x-70*s-spread*.4,y-150*s+spread*.5,26)
    limb(x+120*s,y+60*s,x+150*s+spread,y-50*s,30); limb(x+150*s+spread,y-50*s,x+140*s+spread*.8,y-110*s+spread*.3,26)
    # sand bowl
    R=random.Random(1); n=int(600*lv); bw=(120-30*sq)*s
    for i in range(n):
        xx=R.uniform(-1,1); yy=R.random()
        if yy> (1-xx*xx)*.9+.1: continue
        px=x+xx*bw; py=y+60*s-yy*120*s*lv
        c.drawCircle(px*u,py*u,3.2*s*u,paint('#fff0c8',.85*a))
    c.drawCircle(x*u,(y+10*s)*u,bw*.8*u,paint('#fff3d0',.35*a*lv,blur=30*u))
    for key,dirn in (('pour',-1),('leak',1)):
        if e.get(key) and e[key][0]<=t<e[key][1]:
            for i in range(80):
                ph=(i/80+t*.8)%1; jx=R.uniform(-6,6)
                if dirn<0: px,py=x+jx,(y-260*s)+ph*230*s
                else: px,py=x+(bw-10)+jx*1.5+ph*30,(y+30*s)+ph*220*s
                c.drawCircle(px*u,py*u,2.2*u,paint('#fff0c8',.8*a*(1-ph*.5)))
def sub(ctx,e,t,frame):
    a=env(e,t,.2,.2)
    if a<=0: return
    u=U(ctx); y=e.get('y',525)
    for i,ln in enumerate(e['text'].split('\n')):
        k=clamp((t-e['t0']-i*e.get('stag',.4))/.3)
        rich(ctx.c,ln,e.get('x',512)*u,(y+i*e.get('lh',34))*u,font(e.get('font','sans-bold'),e.get('size',22)*u),a*k,e.get('col','#ffffff'),e.get('hi',PINK),glitch=e.get('glitch',0)*u)
def flash(ctx,e,t,frame):
    d=e.get('dur',.4); k=1-clamp((t-e['t0'])/d) if d>0 else clamp((t-e['t0'])/-d)*.7
    if k>0: ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#ffffff'),k*e.get('a',1)))
def ring(ctx,e,t,frame):
    a=env(e,t)
    if a>0: u=U(ctx); ctx.c.drawCircle(e.get('x',512)*u,e.get('y',290)*u,e.get('r',230)*u,paint('#ffffff',.12*a,stroke=1.2*u))



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

EXTRA=dict(spark=spark,bg=bg,bigchar=bigchar,ecg=ecg,string=string,gauge=gauge,clock=clock,chat=chat,keyboard=keyboard,corner=corner,words=words,hands=hands,sub=sub,flash=flash,ring=ring)

def _render_sc(ctx,sc,t,frame):
    draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)

def draw(ctx,t,frame,S):
    ctx.beats=S.get('beats',[])
    c=ctx.c; c.clear(hexc(INK))
    RICH.compose_scenes(ctx,S,t,frame,_render_sc,overlays_extra=EXTRA,clear=None,
                        vignette_s=.4,grain_a=.03,band_color='#ff5a7a',design_size=(1024,576))
    if S.get('beat_punch',False) and getattr(ctx,'beats',None):
        RICH.beat_punch(ctx.c,ctx.W,ctx.H,t,ctx.beats,a=min(S.get('punch_a',.05),.05),color=S.get('punch_col','#ff5a7a'),window=.06)
