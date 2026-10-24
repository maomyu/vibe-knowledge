"""#5 鎏金年代档案 (gold-archive-history) — ref 7690344836800913785《运气的形状》1024x576. Topic-agnostic.
Warm-black archive look: radial amber glow, drifting dust motes, grain. Persistent chrome: big gold year stamp top-left (+ place·person),
book card top-right (Latin italic title, 《中文书名》 gold, author line, red seal), brand bottom-right, bold serif caption bottom with
left→right blur sweep. Scene props are generic: 3D die, bones, wheel, scoreboard, coin(+pie split), die net, fraction, dice-combo
columns, comparison panels, real-geodata country map with places + linking arc, quote, probability tree, text block, parchment ledger,
tally bars, urn + convergence chart, binomial histogram, Buffon needles, Galton board, axioms list, title card, references.
Design space 1024x576 (U=W/1024).
v3 RICHNESS: tin, denser motes, kb, wipe/iris. See RICHNESS_STANDARD.md.
"""
import math, json, os, random, numpy as np, skia
from functools import lru_cache
from engine.core import *
from engine.layers import draw_elements, U, wrap_markup
from engine import richness as RICH

WHITE='#efe6d6'; GOLD='#e2bf7c'; GOLD2='#c9a062'; GREY='#8a8070'; DIM='#5a5246'; RED='#d8463a'; IVORY='#ece4d0'; INK='#2a2016'
def prepare(S): pass
def env(e,t,fi=.5,fo=.5): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def F(n,s,w=None): return font(n,s,w)
def SER(s,w=700): return font('serif-vf',s,w)
def runs_of(ln):
    out=[]; mode=None; buf=''
    for ch in ln:
        if ch in '[{': out.append((buf,mode)); buf=''; mode=ch
        elif ch in ']}': out.append((buf,mode)); buf=''; mode=None
        else: buf+=ch
    out.append((buf,mode)); return [r for r in out if r[0]]
def rich_line(c,ln,x,y,f,a,align='center',col=WHITE,kcol=GOLD,tcol=RED,reveal=None,glow=0,u=1):
    """markup line; reveal(i,n)->alpha per char (sweep)"""
    rs=runs_of(ln); tw=sum(f.measureText(s) for s,_ in rs)
    x=x-tw/2 if align=='center' else x-tw if align=='right' else x
    n=sum(len(s) for s,_ in rs); i=0
    for s,m in rs:
        cl=kcol if m=='[' else tcol if m=='{' else col
        if reveal is None:
            if glow: c.drawString(s,x,y,f,paint(cl,a*.35,blur=glow))
            c.drawString(s,x,y,f,paint(cl,a)); x+=f.measureText(s); i+=len(s); continue
        for ch in s:
            k=reveal(i,n); i+=1
            if k>0:
                c.drawString(ch,x,y,f,paint(cl,a*k,blur=(1-k)*4*u))
            x+=f.measureText(ch)
    return tw

# ---------------- chrome ----------------
def caption(ctx,e,t,frame):
    """bottom bold serif caption; [gold] {red}; left→right blur sweep over 'sweep' s; autowrap max_w"""
    a=env(e,t,.01,.35)
    if a<=0: return
    c=ctx.c; u=U(ctx); f=SER(e.get('size',28)*u,e.get('weight',800))
    lines=wrap_markup(e['text'],f,e.get('max_w',900)*u); sw=e.get('sweep',.9); lh=e.get('lh',38)
    y0=e.get('y',500)-(len(lines)-1)*lh*(0 if e.get('grow','up')=='down' else 1)
    tot=sum(len(l) for l in lines); done=0
    for j,ln in enumerate(lines):
        n0=done
        def rv(i,n,n0=n0): return clamp((t-e['t0']-(n0+i)/max(1,tot)*sw)/.25)
        rich_line(c,ln,e.get('x',512)*u,(y0+j*lh)*u,f,a,e.get('align','center'),e.get('color',WHITE),reveal=rv,u=u,
                  kcol=e.get('kcolor',GOLD),tcol=e.get('tint',RED)); done+=len(runs_of(ln) and ''.join(s for s,_ in runs_of(ln)))
def yearstamp(ctx,e,t,frame):
    """big gold year top-left + rule + sub line (place · person). 'from' rolls digits to 'year' over roll s"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',58),e.get('y',62)
    if 'years' in e:   # persistent stamp: years=[[t,year,sub],...] rolls digits at each change, sub crossfades
        ys=e['years']; i=max([j for j,y_ in enumerate(ys) if t>=y_[0]] or [0]); yr=ys[i][1]; sub=ys[i][2] if len(ys[i])>2 else ''
        if i>0 and str(yr).isdigit() and str(ys[i-1][1]).isdigit():
            k=ease_in_out_cubic(prog(t,ys[i][0],e.get('roll',.9))); yr=str(int(round(lerp(float(ys[i-1][1]),float(yr),k))))
        e=dict(e,year=yr,sub=sub)
    yr=e['year']
    if 'from' in e:
        k=ease_in_out_cubic(prog(t,e['t0'],e.get('roll',.8))); yr=str(int(round(lerp(float(e['from']),float(yr),k)))) if str(yr).isdigit() else yr
    draw_text(c,str(yr),x*u,y*u,F('garamond',e.get('size',48)*u,600),GOLD,a,'left',glow=3*u,glow_color='#6a4a20')
    c.drawRect(skia.Rect.MakeXYWH(x*u,(y+16)*u,e.get('rule',180)*u,.8*u),paint(GOLD2,a*.45))
    if e.get('sub'): draw_text(c,e['sub'],x*u,(y+42)*u,SER(13*u,500),'#d8cfbf',a,'left')
def bookcard(ctx,e,t,frame):
    """top-right source card: latin (italic), 《title》 gold, author line, rule, red seal"""
    a=env(e,t,.5,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x=e.get('x',952); y=e.get('y',42)
    if e.get('latin'):
        ls=e.get('lsize',15); mw=e.get('max_w',380)
        while ls>8 and F('garamond-italic',ls*u,450).measureText(e['latin'])>mw*u: ls-=.5   # auto-shrink long titles
        draw_text(c,e['latin'],x*u,y*u,F('garamond-italic',ls*u,450),'#d8cfbf',a,'right')
    draw_text(c,'《%s》'%e['title'] if not e['title'].startswith('《') else e['title'],(x+6)*u,(y+25)*u,SER(16*u,700),GOLD,a,'right')
    if e.get('author'): draw_text(c,e['author'],x*u,(y+50)*u,SER(10.5*u,500),GREY,a,'right',spacing=.6*u)
    c.drawRect(skia.Rect.MakeXYWH((x-170)*u,(y+58)*u,170*u,.7*u),paint(GOLD2,a*.35))
    if e.get('seal','文献'):
        sx,sy=x+12,y-16; rrect(c,sx*u,sy*u,26*u,26*u,2*u,fill='#a83226',a=a*.9)
        s=e.get('seal','文献'); fs=F('serif-vf',9.5*u,700)
        for i,ch in enumerate(s[:2]): draw_text(c,ch,(sx+13)*u,(sy+11+i*10)*u,fs,'#f4d8c8',a)
def brand(ctx,e,t,frame):
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',944),e.get('y',552)
    rrect(c,(x-14)*u,(y-10)*u,11*u,11*u,2.5*u,stroke='#c04a3a',a=a*.8,sw=1*u); c.drawCircle((x-8.5)*u,(y-4.5)*u,2*u,paint('#c04a3a',a))
    draw_text(c,e.get('text','Iwanau'),x*u,y*u,F('garamond',12*u,500),'#d8cfbf',a*.85,'left')
def label(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    u=U(ctx); f=F(e.get('font','serif-vf'),e.get('size',13)*u,e.get('weight',600))
    rich_line(ctx.c,e['text'],e.get('x',512)*u,e.get('y',300)*u,f,a,e.get('align','center'),e.get('color','#d8cfbf'),kcol=e.get('kcolor',GOLD),tcol=e.get('tint',RED))
def textblock(ctx,e,t,frame):
    """left/right aligned rich lines: lines=[[text,size,dy,(color)],...] each may have its own at (relative)"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x=e.get('x',60); y=e.get('y',150)
    for i,l in enumerate(e['lines']):
        txt,sz=l[0],l[1]; y+=l[2] if len(l)>2 else sz*1.6
        at=e.get('at',[0]*len(e['lines'])); k=ease_out_cubic(prog(t,e['t0']+at[min(i,len(at)-1)],.5))
        rich_line(c,txt,x*u,y*u,F(e.get('font','serif-vf'),sz*u,700 if sz>=16 else 500),a*k,e.get('align','left'),l[3] if len(l)>3 else '#d8cfbf',kcol=GOLD,tcol=RED)
def title(ctx,e,t,frame):
    """title card: spaced latin small caps, huge gold title, bell-curve hairline, subtitle, credit"""
    a=env(e,t,.8,.8)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',512),e.get('y',250); k=ease_out_cubic(prog(t,e['t0'],1.4))
    if e.get('latin'): draw_text(c,e['latin'],x*u,(y-62)*u,F('garamond',13*u,500),'#bfae8c',a*k,spacing=4*u)
    draw_text(c,e['text'],x*u,y*u,SER(e.get('size',80)*u,900),'#f0d08a',a*k,glow=10*u,glow_color='#8a5a18',spacing=e.get('spacing',6)*u)
    w=e.get('curve_w',300); p=skia.Path(); N=60
    for i in range(N+1):
        xx=x-w/2+w*i/N; yy=y+44-34*math.exp(-((i/N-.5)/.16)**2)
        (p.moveTo if i==0 else p.lineTo)(xx*u,yy*u)
    c.save(); c.clipRect(skia.Rect.MakeLTRB((x-w/2)*u,0,(x-w/2+w*k)*u,ctx.H)); c.drawPath(p,paint(GOLD,a*.8,stroke=1.1*u)); c.drawLine((x-w/2-40)*u,(y+44)*u,(x+w/2+40)*u,(y+44)*u,paint(GOLD2,a*.4,stroke=.7*u)); c.restore()
    if e.get('sub'): draw_text(c,e['sub'],x*u,(y+76)*u,SER(17*u,500),'#e6dccb',a*prog(t,e['t0']+.6,.8),spacing=2*u)
    if e.get('credit'): draw_text(c,'——  %s  ——'%e['credit'],x*u,(y+102)*u,F('garamond',12*u,600),'#bfae8c',a*prog(t,e['t0']+.9,.8),spacing=2*u)
def refs(ctx,e,t,frame):
    a=env(e,t,.6,.6)
    if a<=0: return
    c=ctx.c; u=U(ctx); y=e.get('y',470); f=SER(7.5*u,500)
    draw_text(c,e.get('head','文献线索'),512*u,y*u,SER(8.5*u,700),'#bfae8c',a,spacing=2*u)
    for j,l in enumerate(wrap_markup(e['text'],f,640*u)): draw_text(c,l,512*u,(y+16+j*12)*u,f,'#8a8070',a)
def bigword(ctx,e,t,frame):
    """huge faint spaced latin words across the frame, slow drift"""
    a=env(e,t,.8,.8)
    if a<=0: return
    u=U(ctx); dx=(t-e['t0'])*e.get('drift',-6)
    draw_text(ctx.c,e['text'],(e.get('x',512)+dx)*u,e.get('y',120)*u,F('garamond',e.get('size',58)*u,600),e.get('color','#3a3128'),a*e.get('alpha',.8),spacing=e.get('spacing',10)*u)

# ---------------- dice ----------------
PIPS={1:[(0,0)],2:[(-1,-1),(1,1)],3:[(-1,-1),(0,0),(1,1)],4:[(-1,-1),(1,-1),(-1,1),(1,1)],5:[(-1,-1),(1,-1),(0,0),(-1,1),(1,1)],6:[(-1,-1),(1,-1),(-1,0),(1,0),(-1,1),(1,1)]}
FACES=[((0,0,1),1),((0,0,-1),6),((1,0,0),3),((-1,0,0),4),((0,1,0),2),((0,-1,0),5)]
def _basis(n):
    n=np.array(n,float); a=np.array([0,1,0.]) if abs(n[1])<.9 else np.array([1,0,0.])
    t1=np.cross(a,n); t1/=np.linalg.norm(t1); t2=np.cross(n,t1); return t1,t2
def die3d(c,x,y,s,R,a=1.,col=IVORY,pip='#1a1612',light=(-.5,.7,.6)):
    """s = edge px; R rotation; mild perspective; flat-shaded faces + projected pips (red 1)"""
    fz=s*6
    def P(v): v=R@v; z=fz/(fz-v[2]*s); return x+v[0]*s*z, y-v[1]*s*z, v[2]
    L=np.array(light); L/=np.linalg.norm(L); faces=[]
    for n,val in FACES:
        nw=R@np.array(n,float)
        if nw[2]<=0.02: continue
        t1,t2=_basis(n); cen=np.array(n,float)*.5
        corn=[cen+(sx*t1+sy*t2)*.5 for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
        faces.append((nw[2],n,val,nw,t1,t2,cen,corn))
    faces.sort(key=lambda f:f[0])
    c.drawCircle(x+s*.15,y+s*.62,s*.55,paint('#000000',a*.35,blur=s*.25))
    for _,n,val,nw,t1,t2,cen,corn in faces:
        k=.5+.5*max(0,float(nw@L)); pts=[P(v) for v in corn]
        p=skia.Path(); p.addPoly([skia.Point(px,py) for px,py,_ in pts],True)
        base=np.array([int(col[i:i+2],16) for i in (1,3,5)])*k
        c.drawPath(p,paint('#%02x%02x%02x'%tuple(np.clip(base,0,255).astype(int)),a))
        c.drawPath(p,paint('#00000',a*.18,stroke=max(.6,s*.012)) if False else paint('#000000',a*.15,stroke=max(.6,s*.012)))
        pr=.095 if val!=1 else .15; pc='#b0281e' if val==1 else pip
        for qx,qy in PIPS[val]:
            q=skia.Path(); 
            for i in range(14):
                ang=i/14*2*math.pi; v=cen+t1*(qx*.27+pr*math.cos(ang))+t2*(qy*.27+pr*math.sin(ang)); px,py,_=P(v)
                (q.moveTo if i==0 else q.lineTo)(px,py)
            q.close(); c.drawPath(q,paint(pc,a*min(1,nw[2]*3)))
def _rotm(r): 
    from engine.three import rot; return rot(*r)
def die(ctx,e,t,frame):
    """3D die. rest=[rx,ry,rz] final orientation (rad), spin=[wx,wy,wz] rad/s decaying over settle s; drop from y0 with bounce; ghosts"""
    a=env(e,t,.4,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); D=e.get('settle',1.2); s=e.get('size',90)
    def pose(tt):
        k=prog(tt,e['t0'],D); off=(1-k)**2*D/2
        r=[e.get('rest',[.5,.6,0])[i]+e.get('spin',[0,0,0])[i]*off+e.get('turn',[0,0,0])[i]*(tt-e['t0']) for i in range(3)]
        b=1-abs(math.cos(k*math.pi*1.5))*(1-k) if e.get('y0') is not None else 1
        y=lerp(e.get('y0',e.get('y',260)),e.get('y',260),min(1,ease_out_cubic(k)*1.0)) - (abs(math.sin(k*math.pi*2.5))*(1-k)*30 if e.get('y0') is not None else 0)
        xx=lerp(e.get('x0',e.get('x',512)),e.get('x',512),ease_out_cubic(k))
        return xx,y,r
    for g in range(e.get('ghosts',0),0,-1):
        xx,yy,r=pose(t-g*.05); die3d(c,xx*u,yy*u,s*u,_rotm(r),a*.18*(1-g/(e['ghosts']+1)))
    xx,yy,r=pose(t); die3d(c,xx*u,yy*u,s*u,_rotm(r),a)
    for i,l in enumerate(e.get('labels',[])):   # ring of labels around die (e.g. 1/6)
        ang=-math.pi/2+i*2*math.pi/len(e['labels'])+ (t-e['t0'])*.15
        draw_text(c,l,(xx+math.cos(ang)*s*1.35)*u,(yy+math.sin(ang)*s*1.15+4)*u,F('garamond',11*u),GREY,a*prog(t,e.get('labels_at',e['t0']+.3)+i*.1,.5))
def die2d(c,x,y,s,v,a=1.,col=IVORY):
    rrect(c,x-s/2,y-s/2,s,s,s*.18,fill=col,a=a)
    for qx,qy in PIPS[v]: c.drawCircle(x+qx*s*.27,y+qy*s*.27,s*(.1 if v!=1 else .13),paint('#b0281e' if v==1 else '#1a1612',a))
def bones(ctx,e,t,frame):
    """row of astragalus knuckle-bones (ivory), staggered drop"""
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); n=e.get('n',4); y=e.get('y',345); s=e.get('size',46)
    for i in range(n):
        k=ease_out_back(prog(t,e['t0']+i*.15,.6)); x=e.get('x',512)+(i-(n-1)/2)*s*1.9; yy=y-(1-k)*40; rr=(-.3+.25*i)*(1-k)+(.12 if i%2 else -.1)
        c.save(); c.translate(x*u,yy*u); c.rotate(math.degrees(rr))
        c.drawOval(skia.Rect.MakeXYWH(-s*.9*u,(s*.2)*u,s*1.8*u,s*.25*u),paint('#000000',a*.4,blur=4*u))
        g=skia.GradientShader.MakeLinear([(0,-s*.3*u),(0,s*.3*u)],[hexc('#f4ecd8',a),hexc('#b8a888',a)])
        p=skia.Path(); p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-s*.6*u,-s*.2*u,s*1.2*u,s*.4*u),s*.2*u,s*.2*u))
        for sx in (-1,1):
            for sy in (-1,1): p.addCircle(sx*s*.55*u,sy*s*.14*u,s*.17*u)
        p.setFillType(skia.PathFillType.kWinding); q=skia.Paint(AntiAlias=True); q.setShader(g); c.drawPath(p,q); c.restore()
    if e.get('label'): draw_text(c,e['label'],e.get('x',512)*u,(y-50)*u,SER(9*u,500),GREY,a*prog(t,e['t0']+.6,.6),spacing=2*u)
def wheel(ctx,e,t,frame):
    a=env(e,t,.8,.8)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,r=e.get('x',512),e.get('y',260),e.get('r',190); rot_=(t-e['t0'])*e.get('speed',.15)
    col=e.get('color','#6a5a44'); al=a*e.get('alpha',.6)
    for rr,w in ((r,5),(r*.93,1.5),(r*.25,4),(r*.12,2)): c.drawCircle(x*u,y*u,rr*u,paint(col,al,stroke=w*u))
    for i in range(12):
        an=rot_+i*math.pi/6; c.drawLine((x+math.cos(an)*r*.25)*u,(y+math.sin(an)*r*.25)*u,(x+math.cos(an)*r*.93)*u,(y+math.sin(an)*r*.93)*u,paint(col,al,stroke=3*u))
        c.drawCircle((x+math.cos(an)*r*1.04)*u,(y+math.sin(an)*r*1.04)*u,6*u,paint(col,al))

# ---------------- coins / scoreboard ----------------
def coin_draw(c,x,y,r,a=1.,pie=None,u=1):
    """gold coin with 8-point star; pie=(frac,'#col') removes a wedge to show a share"""
    g=skia.GradientShader.MakeRadial((x-r*.3,y-r*.35),r*1.5,[hexc('#f6dc98',a),hexc('#c99a4a',a),hexc('#7a5420',a)],[0,.55,1])
    q=skia.Paint(AntiAlias=True); q.setShader(g)
    c.drawCircle(x,y+r*.12,r,paint('#000000',a*.4,blur=r*.2))
    if pie is None: c.drawCircle(x,y,r,q)
    else:
        fr=pie[0]; p=skia.Path(); p.moveTo(x,y); p.arcTo(skia.Rect.MakeXYWH(x-r,y-r,2*r,2*r),-90+360*(1-fr)/2*0+ (360*(1-fr))/2*0+0, 360*fr,False); p.close()
        c.save(); c.rotate(-90+ (1-fr)*180 ,x,y); 
        p=skia.Path(); p.moveTo(x,y); p.arcTo(skia.Rect.MakeXYWH(x-r,y-r,2*r,2*r),(1-fr)*180-(1-fr)*180, 360*fr,False); p.close(); c.drawPath(p,q); c.restore()
    c.drawCircle(x,y,r*.86,paint('#7a5420',a*.5,stroke=r*.025))
    for i in range(24): an=i/24*2*math.pi; c.drawCircle(x+math.cos(an)*r*.78,y+math.sin(an)*r*.78,r*.02,paint('#8a6028',a*.6))
    st=skia.Path()
    for i in range(16):
        an=-math.pi/2+i*math.pi/8; rr=r*(.3 if i%2==0 else .1); (st.moveTo if i==0 else st.lineTo)(x+math.cos(an)*rr,y+math.sin(an)*rr)
    st.close(); c.drawPath(st,paint('#6a4818',a*.75))
def coin(ctx,e,t,frame):
    """gold coin; split_at → wedge pie showing 'share' (0..1) with a red counter-wedge flying out"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,r=e.get('x',512)*u,e.get('y',340)*u,e.get('r',46)*u
    k=ease_out_cubic(prog(t,e.get('split_at',1e9),.7))
    if k<=0: coin_draw(c,x,y,r,a)
    else:
        sh=e.get('share',5/7)
        c.save(); p=skia.Path(); p.moveTo(x,y); p.arcTo(skia.Rect.MakeLTRB(x-r*1.1,y-r*1.1,x+r*1.1,y+r*1.1),90-180*(1-sh)*0-0+ (1-sh)*180-180*(1-sh)+  -180*0, 0,False)
        c.restore()
        # main share: wedge from angle a0 sweep 360*sh
        a0=-90+360*(1-sh)/2+ 90
        c.save(); clip=skia.Path(); clip.moveTo(x,y); clip.arcTo(skia.Rect.MakeLTRB(x-r*1.2,y-r*1.2,x+r*1.2,y+r*1.2),a0,360*sh,False); clip.close(); c.clipPath(clip,doAntiAlias=True)
        coin_draw(c,x-r*.12*k,y,r,a); c.restore()
        c.save(); clip=skia.Path(); clip.moveTo(x,y); clip.arcTo(skia.Rect.MakeLTRB(x-r*1.2,y-r*1.2,x+r*1.2,y+r*1.2),a0+360*sh,360*(1-sh),False); clip.close()
        c.translate(r*.9*k,0); c.clipPath(clip,doAntiAlias=True); c.drawCircle(x,y,r,paint('#b8483a',a)); c.drawCircle(x,y,r*.86,paint('#7a2a20',a*.5,stroke=r*.03)); c.restore()
    if e.get('label'): draw_text(c,e['label'],x,y+r+22*u,SER(11*u,500),'#bfb3a0',a,spacing=1*u)
def scoreboard(ctx,e,t,frame):
    """two-sided score: sides=[{badge,score,filled,total,color}], head text, axis labels; stamp (rotated red seal) at stamp_at; ratio text at ratio_at"""
    a=env(e,t,.5,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); y=e.get('y',230)
    if e.get('head'): rich_line(c,e['head'],512*u,(y-112)*u,SER(17*u,500),a,'center','#d8cfbf',kcol=GOLD)
    for i,sd in enumerate(e['sides']):
        x=sd.get('x',295 if i==0 else 728); col=sd.get('color',GOLD if i==0 else RED)
        c.drawCircle(x*u,(y-72)*u,23*u,paint('#1a1612',a)); c.drawCircle(x*u,(y-72)*u,23*u,paint(col,a,stroke=1.4*u))
        draw_text(c,sd['badge'],x*u,(y-64)*u,SER(20*u,800),col,a)
        draw_text(c,str(sd['score']),x*u,(y+24)*u,F('garamond',64*u,600),'#d8cfbf',a)
        tot=sd.get('total',6); fl=sd.get('filled',0); sw=34; gx=x-tot*(sw+5)/2
        for j in range(tot):
            on=j<fl; c.drawRect(skia.Rect.MakeXYWH((gx+j*(sw+5))*u,(y+40)*u,sw*u,7*u),paint(col if on else '#2a2620',a*(1 if on else .8)))
            if not on: c.drawRect(skia.Rect.MakeXYWH((gx+j*(sw+5))*u,(y+40)*u,sw*u,7*u),paint('#4a4236',a,stroke=.6*u))
        draw_text(c,'0',gx*u,(y+62)*u,SER(9*u),GREY,a,'left'); draw_text(c,sd.get('goal','60分·胜'),(gx+tot*(sw+5)-5)*u,(y+62)*u,SER(9*u),GREY,a,'right')
    if t>=e.get('stamp_at',1e9) and t<e.get('stamp_off',1e9):
        k=ease_out_back(prog(t,e['stamp_at'],.35)); s=88*(2-k)/1.0
        c.save(); c.translate(512*u,(y+8)*u); c.rotate(-8); c.scale(1/(2-k)*1.0+0*k,1/(2-k)); 
        rrect(c,-44*u,-44*u,88*u,88*u,4*u,fill='#b8362a',a=a*k); rrect(c,-38*u,-38*u,76*u,76*u,3*u,stroke='#f0d0c0',a=a*k*.8,sw=1.6*u)
        st=e.get('stamp','中断'); 
        for i_,ch in enumerate(st[:2]): draw_text(c,ch,0,(-6+i_*30)*u,SER(26*u,900),'#f8e8dc',a*k)
        c.restore()
    if t>=e.get('ratio_at',1e9):
        k=ease_out_cubic(prog(t,e['ratio_at'],.5)); rich_line(c,e.get('ratio','5 : 2{?}'),512*u,(y+34)*u,F('garamond',34*u,600),a*k,'center','#f0e4cc',tcol=RED)

# ---------------- probability props ----------------
def dienet(ctx,e,t,frame):
    """unfolded die (cross) with a label per face (e.g. 1/6), side note; faces pop in"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y,s=e.get('x',512),e.get('y',150),e.get('size',42); lab=e.get('labels',['1/6']*6)
    cells=[(0,0),(-1,1),(0,1),(1,1),(0,2),(0,3)]
    for i,(cx,cy) in enumerate(cells):
        k=ease_out_back(prog(t,e['t0']+i*.12,.45)); X=x+cx*(s+4); Y=y+cy*(s+4)
        rrect(c,(X-s/2*k)*u,(Y-s/2*k)*u,s*k*u,s*k*u,5*u,fill='#e8dfc8',a=a)
        draw_text(c,lab[i],X*u,(Y+4)*u,F('garamond',13*u*k+1e-3,600),'#3a3024',a)
    for j,l in enumerate(e.get('note',[])): draw_text(c,l,(x+2*s+18)*u,(y+s+8+j*16)*u,SER(11*u,500),'#bfb3a0',a*prog(t,e['t0']+.8,.5),'left')
def fraction(ctx,e,t,frame):
    """label = numerator / denominator (gold lead word, rule)"""
    a=env(e,t,.5,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); x,y=e.get('x',560),e.get('y',420)
    draw_text(c,e.get('label','概率'),(x-16)*u,(y+6)*u,SER(19*u,800),GOLD,a,'right'); draw_text(c,'=',(x)*u,(y+6)*u,SER(16*u),'#d8cfbf',a)
    w=max(SER(14*u).measureText(e['num']),SER(14*u).measureText(e['den']))/u+20
    c.drawRect(skia.Rect.MakeXYWH((x+16)*u,(y)*u,w*u,.9*u),paint('#d8cfbf',a))
    draw_text(c,e['num'],(x+16+w/2)*u,(y-8)*u,SER(14*u,600),GOLD,a); draw_text(c,e['den'],(x+16+w/2)*u,(y+20)*u,SER(14*u,600),'#d8cfbf',a)
def combos(ctx,e,t,frame):
    """dice-combination columns: cols=[{title, sub, rows:[[d1,d2,d3,'×6'],...], foot, x, color}] ; rows pop sequentially"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); y0=e.get('y',140); s=e.get('die',15)
    for ci,col in enumerate(e['cols']):
        x=col.get('x',300 if ci==0 else 724); cl=col.get('color',WHITE)
        draw_text(c,col['title'],x*u,y0*u,F('garamond',34*u,600),cl,a); 
        if col.get('unit'): draw_text(c,col['unit'],(x+28)*u,y0*u,SER(12*u),cl,a,'left')
        for ri,row in enumerate(col['rows']):
            k=prog(t,e['t0']+col.get('delay',0)+ri*e.get('row_dt',.12),.3)
            if k<=0: continue
            ry=y0+30+ri*(s+7); dv=[v for v in row if isinstance(v,int)]
            for di,v in enumerate(dv): die2d(c,(x-(len(dv)-1)*(s+3)/2+di*(s+3))*u,ry*u,s*u,v,a*k)
            tag=[v for v in row if isinstance(v,str)]
            if tag: draw_text(c,tag[0],(x+len(dv)*(s+3)/2+12)*u,(ry+4)*u,F('garamond',11*u),GREY,a*k,'left')
        if col.get('foot'): rich_line(c,col['foot'],x*u,(y0+48+len(col['rows'])*(s+7))*u,SER(11*u,500),a*prog(t,e['t0']+col.get('foot_at',1),.5),'center','#bfb3a0',kcol=GOLD)
    if e.get('vs'): draw_text(c,e['vs'],512*u,(y0+130)*u,F('garamond-italic',12*u),DIM,a)
def panels(ctx,e,t,frame):
    """comparison cards: cards=[{title, dice:[v..] | pairs:n, mult, lines:[..], pct, pct_at, bar_label, color}]"""
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c; u=U(ctx); y=e.get('y',120); h=e.get('h',190); w=e.get('w',255)
    for i,cd in enumerate(e['cards']):
        x=cd.get('x',512-w-e.get('gap',50)/2 if i==0 else 512+e.get('gap',50)/2); k=ease_out_cubic(prog(t,e['t0']+i*e.get('dt',.4),.5)); al=a*k; col=cd.get('color',GOLD if i==0 else RED)
        rrect(c,x*u,y*u,w*u,h*u,5*u,fill='#16130f',a=al*.9); rrect(c,x*u,y*u,w*u,h*u,5*u,stroke=cd.get('border','#4a4030'),a=al,sw=1*u)
        draw_text(c,cd['title'],(x+14)*u,(y+22)*u,SER(13*u,700),col,al,'left')
        if cd.get('dice'):
            ds=cd.get('die',28)
            for j,v in enumerate(cd['dice']): die2d(c,(x+30+j*ds*1.45)*u,(y+62)*u,ds*u,v,al)
        if cd.get('pairs'):
            n=cd['pairs']; pc=min(cd.get('per_row',12),n)
            for j in range(n):
                xx=x+22+(j%pc)*19; yy=y+48+(j//pc)*16; die2d(c,xx*u,yy*u,8*u,6,al); die2d(c,(xx+8.6)*u,yy*u,8*u,6,al)
        if cd.get('mult'): draw_text(c,cd['mult'],(x+w-40)*u,(y+66)*u,F('garamond',13*u),'#d8cfbf',al,'left')
        for j,l in enumerate(cd.get('lines',[])): draw_text(c,l,(x+14)*u,(y+112+j*16)*u,SER(11*u,500),'#bfb3a0',al,'left')
        by=y+h-30; c.drawRect(skia.Rect.MakeXYWH((x+14)*u,by*u,(w-28)*u,2*u),paint('#3a3328',al))
        if 'pct' in cd:
            kk=ease_in_out_cubic(prog(t,cd.get('pct_at',e['t0']+1),1.2)); v=cd['pct']*kk
            c.drawRect(skia.Rect.MakeXYWH((x+14)*u,by*u,(w-28)*v*u,2*u),paint(col,al))
            c.drawLine((x+14+(w-28)*.5)*u,(by-5)*u,(x+14+(w-28)*.5)*u,(by+7)*u,paint(GREY,al,stroke=.8*u)); draw_text(c,'50%',(x+14+(w-28)*.5)*u,(by+18)*u,F('garamond',8*u),GREY,al)
            if kk>0: draw_text(c,cd.get('pct_text','%.1f%%'%(v*100)),(x+w-14)*u,(by-8)*u,F('garamond',16*u,600),col,al*kk,'right')

# ---------------- map ----------------
WORLD=os.path.join(os.path.dirname(__file__),'..','..','assets','geo','countries_50m.geojson')
@lru_cache(8)
def _country(names,bbox):
    d=json.load(open(WORLD)); out=[]
    for f in d['features']:
        P=f['properties']
        if not any(n in (P.get('NAME'),P.get('NAME_EN'),P.get('NAME_ZH'),P.get('ADMIN')) for n in names): continue
        g=f['geometry']; cs=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
        for poly in cs:
            r=np.array(poly[0],float)
            if bbox and not (bbox[0]<=r[:,0].mean()<=bbox[2] and bbox[1]<=r[:,1].mean()<=bbox[3]): continue
            out.append(r)
    return out
def countrymap(ctx,e,t,frame):
    """real outline (Natural Earth 50m): countries=[name..], bbox=[lon0,lat0,lon1,lat1], box=[x,y,w,h]; places=[[label,lon,lat,sub]]; link=[i,j,at,dur]"""
    a=env(e,t,.6,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); from engine.geo import Proj
    bb=e['bbox']; bx=e.get('box',[40,40,420,380]); pr=Proj(bb,*[v*u for v in bx])
    k=ease_in_out_cubic(prog(t,e['t0'],e.get('draw',1.5)))
    for r in _country(tuple(e['countries']),tuple(bb)):
        X,Y=pr(r[:,0],r[:,1]); p=skia.Path(); p.addPoly([skia.Point(float(x),float(y)) for x,y in zip(X,Y)],True)
        c.drawPath(p,paint('#14110d',a*.9)); c.drawPath(p,paint(GOLD2,a*.25*k,stroke=6*u,blur=4*u)); c.drawPath(p,paint('#d8b878',a*k,stroke=1*u))
    pts=[]
    for i,pl in enumerate(e.get('places',[])):
        x,y=pr(pl[1],pl[2]); pts.append((float(x),float(y))); kk=prog(t,e['t0']+.8+i*.2,.4)
        glow_dot(c,float(x),float(y),3.2*u,'#fff0c8',a*kk,3)
        draw_text(c,pl[0],float(x)+8*u,float(y)+5*u,SER(13*u,700),'#f0e4cc',a*kk,'left')
        if len(pl)>3: draw_text(c,pl[3],float(x)+8*u+SER(13*u,700).measureText(pl[0])+4*u,float(y)+5*u,SER(8*u,500),GOLD,a*kk,'left')
    if e.get('link') and len(pts)>1:
        i,j,at,dur=e['link']; (x0,y0),(x1,y1)=pts[i],pts[j]; kk=ease_in_out_cubic(prog(t,at,dur)); mx,my=(x0+x1)/2+60*u,(y0+y1)/2
        p=skia.Path(); N=30; q=[]
        for s_ in range(N+1):
            s=s_/N*kk; px=(1-s)**2*x0+2*(1-s)*s*mx+s*s*x1; py=(1-s)**2*y0+2*(1-s)*s*my+s*s*y1; q.append((px,py))
        p.moveTo(*q[0]); [p.lineTo(*qq) for qq in q[1:]]; c.drawPath(p,paint(GOLD,a*.6,stroke=1*u))
        if 0<kk<1 or e.get('keep_icon'):
            hx,hy=q[-1]; c.save(); c.translate(hx,hy); c.rotate(-15); rrect(c,-10*u,-7*u,20*u,14*u,1.5*u,fill='#e8dcc0',a=a); c.drawCircle(0,0,3*u,paint('#a83226',a)); c.restore()

# ---------------- quote / tree / docs ----------------
def quote(ctx,e,t,frame):
    """foreign italic line (small), main zh quote (bold, [gold]), attribution; x/align"""
    a=env(e,t,.6,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); x=e.get('x',512); y=e.get('y',150); al=e.get('align','center')
    if e.get('foreign'):
        for j,l in enumerate(wrap_markup(e['foreign'],F('garamond-italic',e.get('fsize',13)*u),e.get('fmax',440)*u)): draw_text(c,l,x*u,(y+j*18)*u,F('garamond-italic',e.get('fsize',13)*u),'#bfb3a0',a*prog(t,e['t0'],.8),al)
        y+=18*len(wrap_markup(e['foreign'],F('garamond-italic',e.get('fsize',13)*u),e.get('fmax',440)*u))+24
    f=SER(e.get('size',20)*u,800); lines=wrap_markup(e['text'],f,e.get('max_w',420)*u)
    for j,l in enumerate(lines): rich_line(c,l,x*u,(y+j*e.get('size',20)*1.55)*u,f,a*ease_out_cubic(prog(t,e['t0']+.4+j*.25,.6)),al,'#f0e4cc',kcol=GOLD,glow=3*u)
    y+=len(lines)*e.get('size',20)*1.55
    for j,l in enumerate(e.get('more',[])): rich_line(c,l,x*u,(y+6+j*e.get('size',20)*1.4)*u,SER(e.get('size',20)*.85*u,500),a*prog(t,e['t0']+e.get('more_at',1.2)+j*.3,.6),al,'#d8cfbf',kcol=GOLD)
    if e.get('attr'): draw_text(c,'— '+e['attr'],x*u,(y+12)*u,SER(10*u,500),GREY,a*prog(t,e['t0']+1,.6),al)
def tree(ctx,e,t,frame):
    """binary outcome tree: depth, root x0,y; leaves column x1, span [ytop,ybot]; grows level by level from grow_at (lvl_dur);
    upper edges col_up, lower col_dn; hl = list of leaf indices whose path glows; leaves=[label per leaf] or rule; groups=[[i0,i1,text,col]]"""
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); D=e.get('depth',4); x0,x1=e.get('x0',350),e.get('x1',840); yt,yb=e.get('span',[130,445]); y0=e.get('y',(yt+yb)/2)
    n=2**D; ly=[yt+(yb-yt)*i/(n-1) for i in range(n)]; g0=e.get('grow_at',e['t0']); ld=e.get('lvl_dur',.5)
    hl=set(e.get('hl',[n-1])); hk=prog(t,e.get('hl_at',1e9),1.)
    def node(d,i): # depth d index i (0..2^d-1)
        span=n//2**d; ys=ly[i*span:(i+1)*span]; return x0+(x1-60-x0)*d/D, (sum(ys)/len(ys) if d else y0)
    c.drawLine((x0-75)*u,y0*u,x0*u,y0*u,paint(GREY,a*.6,stroke=.8*u,blur=0)) if True else None
    for d in range(D):
        kk=ease_in_out_cubic(prog(t,g0+d*ld,ld))
        if kk<=0: break
        for i in range(2**d):
            xa,ya=node(d,i)
            for ch in (0,1):
                xb,yb_=node(d+1,2*i+ch) if d+1<D else (x1-30,ly[(2*i+ch)*(n//2**(d+1))])
                if d+1==D: xb,yb_=x1-30,ly[2*i+ch]
                p=skia.Path(); p.moveTo(xa*u,ya*u); mx=(xa+xb)/2; p.cubicTo(mx*u,ya*u,mx*u,yb_*u,xb*u,yb_*u)
                leaves_under=range((2*i+ch)*(n//2**(d+1)),(2*i+ch+1)*(n//2**(d+1)))
                on=any(l in hl for l in leaves_under)
                col=e.get('col_up','#9a8458') if ch==0 else e.get('col_dn','#9a3a2a')
                pm=skia.PathMeasure(p,False); L=pm.getLength(); seg=skia.Path(); pm.getSegment(0,L*kk,seg,True)
                c.drawPath(seg,paint(col,a*.9,stroke=1*u))
                if on and hk>0: c.drawPath(seg,paint('#e05a40',a*hk*.6,stroke=5*u,blur=4*u)); c.drawPath(seg,paint('#f07050',a*hk,stroke=2*u))
            glow_dot(c,xa*u,ya*u,2.8*u,'#fff0c8',a,2.5)
    if t>=g0+D*ld-.2:
        kk=prog(t,g0+D*ld-.2,.5); labs=e.get('leaves',['甲']*(n-1)+['乙'])
        for i in range(n):
            col=e.get('leaf_cols',{}).get(labs[i],GOLD if labs[i]==labs[0] else RED)
            c.drawCircle((x1-20)*u,ly[i]*u,8.5*u,paint('#1a1612',a*kk)); c.drawCircle((x1-20)*u,ly[i]*u,8.5*u,paint(col,a*kk,stroke=1*u))
            draw_text(c,labs[i],(x1-20)*u,(ly[i]+4)*u,SER(10*u,800),col,a*kk)
        for g in e.get('groups',[]):
            i0,i1,txt=g[:3]; col=g[3] if len(g)>3 else GOLD; gk=prog(t,g[4] if len(g)>4 else g0+D*ld,.5)
            if i1>i0: c.drawLine((x1)*u,ly[i0]*u,(x1+6)*u,ly[i0]*u,paint(GREY,a*gk)); c.drawLine((x1+6)*u,ly[i0]*u,(x1+6)*u,ly[i1]*u,paint(GREY,a*gk)); c.drawLine((x1)*u,ly[i1]*u,(x1+6)*u,ly[i1]*u,paint(GREY,a*gk))
            rich_line(c,txt,(x1+18)*u,((ly[i0]+ly[i1])/2+6)*u,SER(15*u,700),a*gk,'left',col,kcol=GOLD)
def ledger(ctx,e,t,frame):
    """parchment document (rotated): head, sub, rows=[[left,right]], foot; slides in"""
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); k=ease_out_cubic(prog(t,e['t0'],.9)); x,y,w,h=e.get('x',512),e.get('y',290),e.get('w',150),e.get('h',210)
    c.save(); c.translate(x*u,(y+(1-k)*30)*u); c.rotate(e.get('rot',-6)); c.scale(e.get('scale',1.),e.get('scale',1.))
    c.drawRect(skia.Rect.MakeXYWH((-w/2+6)*u,(-h/2+8)*u,w*u,h*u),paint('#000000',a*.5,blur=10*u))
    g=skia.GradientShader.MakeRadial((0,-h*.2*u),h*u,[hexc('#efe2c2',a),hexc('#d2bf98',a),hexc('#a89068',a)],[0,.6,1]); q=skia.Paint(AntiAlias=True); q.setShader(g)
    c.drawRect(skia.Rect.MakeXYWH(-w/2*u,-h/2*u,w*u,h*u),q)
    draw_text(c,e.get('head','LONDON'),0,(-h/2+22)*u,F('garamond',14*u,600),INK,a,spacing=2*u)
    if e.get('sub'): draw_text(c,e['sub'],0,(-h/2+32)*u,F('garamond-italic',5.5*u),INK,a)
    c.drawLine((-w/2+12)*u,(-h/2+48)*u,(w/2-12)*u,(-h/2+48)*u,paint(INK,a*.6,stroke=.5*u))
    rows=e.get('rows',[]); rh=(h-80)/max(1,len(rows))
    for i,r in enumerate(rows):
        yy=-h/2+60+i*rh; draw_text(c,r[0],(-w/2+12)*u,yy*u,F('garamond-italic',6*u),INK,a,'left')
        if len(r)>1: draw_text(c,r[1],(w/2-12)*u,yy*u,F('garamond',6*u),INK,a,'right')
    if e.get('foot'): draw_text(c,e['foot'],(-w/2+12)*u,(h/2-12)*u,F('garamond-italic',6.5*u),INK,a,'left')
    c.restore()
def tally(ctx,e,t,frame):
    """two (or more) dense hatched bars growing: bars=[{label,value,frac,color}], baseline y, height H"""
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); yb=e.get('y',405); H=e.get('h',150); w=e.get('w',50)
    for i,b in enumerate(e['bars']):
        x=b.get('x',300+i*80); k=ease_out_cubic(prog(t,e['t0']+i*.2,e.get('grow',1.5))); hh=H*b.get('frac',1)*k; col=b.get('color',GOLD if i==0 else '#d8d0c0')
        c.drawRect(skia.Rect.MakeLTRB(x*u,(yb-hh)*u,(x+w)*u,yb*u),paint(col,a*.35))
        for j in range(int(w/3)): c.drawLine((x+j*3+1)*u,yb*u,(x+j*3+1)*u,(yb-hh)*u,paint(col,a*.9,stroke=1.1*u))
        for j in range(0,int(hh),4): c.drawLine(x*u,(yb-j)*u,(x+w)*u,(yb-j)*u,paint('#0c0a08',a*.35,stroke=.6*u))
        draw_text(c,'%s %s'%(b['label'],'{:,}'.format(int(b['value']*k))),(x+w/2)*u,(yb+18)*u,SER(8*u,500),GREY,a)
    if e.get('ratio'): draw_text(c,e['ratio'],e.get('rx',512)*u,e.get('ry',270)*u,F('garamond',20*u,600),GOLD,a*prog(t,e.get('ratio_at',e['t0']+1.5),.5))

# ---------------- simulations (deterministic) ----------------
@lru_cache(8)
def _walk(p,n,seed):
    r=np.random.default_rng(seed); x=(r.random(n)<p).astype(float); return np.cumsum(x)/np.arange(1,n+1)
def urnchart(ctx,e,t,frame):
    """urn with white/black stones + convergence chart (log-x) of running proportion → p; counter label; draws over [draw_at, dur]"""
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); ux,uy=e.get('ux',220),e.get('uy',330); p_=e.get('p',.6); N=e.get('n',25550)
    # urn (amphora outline) + stones
    pth=skia.Path(); s=e.get('us',1.)
    pts=[(-30,-110),(-28,-95),(-50,-80),(-70,-40),(-72,10),(-60,60),(-35,95),(-30,108),(30,108),(35,95),(60,60),(72,10),(70,-40),(50,-80),(28,-95),(30,-110)]
    pth.moveTo((ux+pts[0][0]*s)*u,(uy+pts[0][1]*s)*u)
    for i in range(1,len(pts)): pth.lineTo((ux+pts[i][0]*s)*u,(uy+pts[i][1]*s)*u)
    pth.close(); c.drawPath(pth,paint('#2a2018',a)); c.drawPath(pth,paint(GOLD2,a*.8,stroke=1.4*u))
    r=random.Random(3)
    for i in range(e.get('stones',130)):
        xx=ux+r.uniform(-55,55)*s; yy=uy+r.uniform(-60,85)*s; c.drawCircle(xx*u,yy*u,3.3*s*u,paint('#efe8da' if r.random()<p_ else '#3a332a',a))
    # chart
    cx0,cx1,cy0,cy1=e.get('chart',[400,880,150,400]); c.drawLine(cx0*u,cy1*u,cx1*u,cy1*u,paint(GREY,a*.6,stroke=.7*u)); c.drawLine(cx0*u,cy0*u,cx0*u,cy1*u,paint(GREY,a*.6,stroke=.7*u))
    def X(i): return cx0+(cx1-cx0)*math.log10(i)/math.log10(N)
    def Y(v): return cy1-(cy1-cy0)*v
    for v in (0,.5,1): draw_text(c,'%.1f'%v,(cx0-8)*u,(Y(v)+3)*u,F('garamond',8*u),GREY,a,'right')
    for tk in e.get('xticks',[1,10,100,1000,10000]): draw_text(c,'{:,}'.format(tk),X(max(tk,1))*u,(cy1+14)*u,F('garamond',8*u),GREY,a)
    yy=Y(p_); 
    for xx in range(int(cx0),int(cx1),8): c.drawLine(xx*u,yy*u,(xx+4)*u,yy*u,paint(GOLD,a*.5,stroke=.8*u))
    draw_text(c,e.get('true_label','真实比例 %.1f'%p_),(cx1-4)*u,(yy-6)*u,SER(8*u),GOLD,a,'right')
    k=prog(t,e.get('draw_at',e['t0']+.5),e.get('dur',5.)); m=max(2,int(N**k)); W=_walk(p_,N,e.get('seed',7))
    idx=np.unique(np.geomspace(1,m,min(400,m)).astype(int))
    pp=skia.Path(); pp.moveTo(X(1)*u,Y(W[0])*u)
    for i in idx: pp.lineTo(X(i)*u,Y(W[i-1])*u)
    c.drawPath(pp,paint('#e8dcc0',a,stroke=1.2*u))
    glow_dot(c,X(m)*u,Y(W[m-1])*u,2.5*u,'#fff0c8',a,3)
    rich_line(c,e.get('counter','第 [{n:,}] 次 · 白石占 {v:.3f}').format(n=m,v=W[m-1]).replace('{','').replace('}',''),cx1*u,(cy0-20)*u,SER(12*u,600),a,'right','#d8cfbf',kcol=GOLD)
    if e.get('caption_small'): draw_text(c,e['caption_small'],ux*u,(uy+130*s)*u,SER(8*u),GREY,a)
def binom(ctx,e,t,frame):
    """binomial histogram for n coins (n may step over time: steps=[[t,n],..]); head text with n; normal curve option"""
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); n=e.get('n',32)
    for st in e.get('steps',[]):
        if t>=st[0]: n=st[1]
    x0,x1,yb,H=e.get('x0',160),e.get('x1',864),e.get('y',440),e.get('h',260)
    mu=n/2; sd=math.sqrt(n)/2; lo=max(0,int(math.floor(mu-e.get('span_sd',3.2)*sd))); hi=min(n,int(math.ceil(mu+e.get('span_sd',3.2)*sd)))
    pk=[math.comb(n,k)/2**n for k in range(n+1)]; m=max(pk); bw=(x1-x0)/(hi-lo+1); kk=ease_out_cubic(prog(t,e['t0'],.8))
    for k_ in range(lo,hi+1):
        v=pk[k_]; h=H*v/m*kk; k_=k_-lo; g=skia.GradientShader.MakeLinear([(0,(yb-h)*u),(0,yb*u)],[hexc('#d8b878',a),hexc('#5a4628',a)])
        q=skia.Paint(AntiAlias=True); q.setShader(g); c.drawRect(skia.Rect.MakeXYWH((x0+k_*bw+bw*.06)*u,(yb-h)*u,bw*.88*u,h*u),q)
    c.drawLine((x0-20)*u,yb*u,(x1+20)*u,yb*u,paint(GREY,a*.6,stroke=.7*u))
    if e.get('head'): rich_line(c,e['head'].format(n=n),512*u,(yb-H-30)*u,SER(13*u,500),a,'center','#d8cfbf',kcol=GOLD)
    if t>=e.get('curve_at',1e9):
        ck=prog(t,e['curve_at'],1.); p=skia.Path()
        for i in range(201):
            xx=x0+(x1-x0)*i/200; kx=(xx-x0)/bw-.5+lo; yy=yb-H*math.exp(-((kx-mu)/sd)**2/2)
            (p.moveTo if i==0 else p.lineTo)(xx*u,yy*u)
        c.save(); c.clipRect(skia.Rect.MakeLTRB(0,0,(x0+(x1-x0)*ck)*u,ctx.H)); c.drawPath(p,paint('#fff0c8',a,stroke=1.5*u)); c.restore()
        if e.get('curve_label'): draw_text(c,e['curve_label'],(x1-60)*u,(yb-H*.5)*u,SER(11*u,600),GOLD,a*ck,'left')
@lru_cache(4)
def _needles(n,seed,spacing,box):
    r=np.random.default_rng(seed); x0,y0,x1,y1=box; L=spacing*.8
    X=r.uniform(x0,x1,n); Y=r.uniform(y0,y1,n); A=r.uniform(0,math.pi,n)
    ya=Y-np.sin(A)*L/2; yb=Y+np.sin(A)*L/2; cross=np.floor((ya-y0)/spacing)!=np.floor((yb-y0)/spacing)
    return X,Y,A,cross,L
def needles(ctx,e,t,frame):
    """Buffon's needle: wooden floor planks (horizontal lines), needles rain over [t0+.3, dur]; panel counts 投针/压线/π estimate"""
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); box=tuple(e.get('box',[150,110,880,470])); sp=e.get('spacing',60); n=e.get('n',520)
    x0,y0,x1,y1=box; g=skia.GradientShader.MakeLinear([(0,y0*u),(0,y1*u)],[hexc('#3a2c1c',a),hexc('#2a2014',a)]); q=skia.Paint(); q.setShader(g)
    c.drawRect(skia.Rect.MakeLTRB(x0*u,y0*u,x1*u,y1*u),q)
    yy=y0
    while yy<=y1: c.drawLine(x0*u,yy*u,x1*u,yy*u,paint('#140e08',a,stroke=1.4*u)); yy+=sp
    X,Y,A,cr,L=_needles(n,e.get('seed',5),sp,box); k=prog(t,e['t0']+.3,e.get('dur',6.)); m=int(n*k**1.6)
    for i in range(m):
        dx,dy=math.cos(A[i])*L/2,math.sin(A[i])*L/2; col='#f0d090' if cr[i] else '#c8b68a'
        c.drawLine((X[i]-dx)*u,(Y[i]-dy)*u,(X[i]+dx)*u,(Y[i]+dy)*u,paint(col,a*(.95 if cr[i] else .7),stroke=1.3*u))
    hits=int(cr[:m].sum()); px,py=e.get('panel',[770,395])
    rrect(c,(px-10)*u,(py-12)*u,128*u,74*u,4*u,fill='#0e0c0a',a=a*.85); rrect(c,(px-10)*u,(py-12)*u,128*u,74*u,4*u,stroke='#4a4030',a=a,sw=.8*u)
    f=SER(9*u,500); fn=F('garamond',13*u,600)
    for j,(lab,v) in enumerate([(e.get('l1','投针'),str(m)),(e.get('l2','压线'),str(hits))]):
        draw_text(c,lab,px*u,(py+4+j*18)*u,f,GREY,a,'left'); draw_text(c,v,(px+110)*u,(py+4+j*18)*u,fn,'#e8dcc0',a,'right')
    est=(2*m*.8/hits) if hits else 0
    draw_text(c,'π ≈ 2NL/Kd',px*u,(py+46)*u,F('garamond-italic',9*u),GREY,a,'left'); draw_text(c,'%.3f'%est if hits else '—',(px+110)*u,(py+48)*u,F('garamond',16*u,600),GOLD,a,'right')
@lru_cache(4)
def _galton(nb,rows,seed):
    r=np.random.default_rng(seed); steps=(r.random((nb,rows))<.5).astype(int)*2-1; return np.cumsum(steps,1)
def galton(ctx,e,t,frame):
    """Galton board in a gold frame: peg triangle, balls released over [t0+.3, dur] at rate, fall row by row, stack in bins; curve_at overlays normal curve"""
    a=env(e,t,.5,.5)*(prog(t,e['show_at'],.6) if 'show_at' in e else 1)
    if a<=0: return
    c=ctx.c; u=U(ctx); cx=e.get('x',512); top=e.get('y',30); rows=e.get('rows',14); dx=e.get('dx',13); dy=e.get('dy',14); nb=e.get('n',600)
    W_=dx*(rows+3); fx0,fx1=cx-W_/2-8,cx+W_/2+8; fy0=top; fy1=top+rows*dy+40+e.get('bin_h',110)
    rrect(c,fx0*u,fy0*u,(fx1-fx0)*u,(fy1-fy0)*u,4*u,fill='#0e0c09',a=a*.9); rrect(c,fx0*u,fy0*u,(fx1-fx0)*u,(fy1-fy0)*u,4*u,stroke=GOLD2,a=a*.8,sw=1*u)
    c.drawLine((cx-40)*u,(top+8)*u,(cx-4)*u,(top+20)*u,paint(GOLD2,a,stroke=1*u)); c.drawLine((cx+40)*u,(top+8)*u,(cx+4)*u,(top+20)*u,paint(GOLD2,a,stroke=1*u))
    py0=top+30
    for rI in range(rows):
        for j in range(rI+1): c.drawCircle((cx+(j-rI/2)*dx)*u,(py0+rI*dy)*u,1.3*u,paint('#c8a868',a*.8))
    byt=py0+rows*dy+6; byb=fy1-6
    for j in range(rows+2): xx=cx+(j-(rows+1)/2)*dx; c.drawLine(xx*u,byt*u,xx*u,byb*u,paint('#6a5434',a*.7,stroke=.6*u))
    P=_galton(nb,rows,e.get('seed',3)); T0=e['t0']+.3; dur=e.get('dur',6.); fall=e.get('fall',1.2)
    rel=T0+np.arange(nb)/nb*dur; counts=np.zeros(rows+3,int); br=e.get('ball',2.1)
    for i in range(nb):
        tt=t-rel[i]
        if tt<0: break
        if tt<fall:
            s=tt/fall*rows; rI=int(s); fr=s-rI; xa=P[i,rI-1] if rI>0 else 0; xb=P[i,min(rI,rows-1)]
            xx=cx+lerp(xa,xb,fr)*dx/2; yy=py0+s*dy-4*math.sin(fr*math.pi)
            c.drawCircle(xx*u,yy*u,br*u,paint('#f0d48c',a)); c.drawCircle(xx*u,yy*u,br*2*u,paint('#f0c060',a*.25,blur=2*u))
        else:
            b=(P[i,-1]+rows)//2; counts[b]+=1; h=counts[b]-1; per=max(1,int(dx/(2.05*br))); col_=h%per; row_=h//per
            xx=cx+(b-rows/2)*dx+(col_-(per-1)/2)*br*2.05; c.drawCircle(xx*u,(byb-br-row_*br*1.8)*u,br*u,paint('#e0c078',a*.95))
    if t>=e.get('curve_at',1e9):
        ck=prog(t,e['curve_at'],1.); p=skia.Path(); mx=counts.max() or 1; sd=math.sqrt(rows)/2
        for i in range(101):
            b=-1+(rows+2)*i/100; xx=cx+(b-rows/2)*dx; yy=byb-mx/max(1,int(dx/(2.05*br)))*br*1.8*math.exp(-((b-rows/2)/sd)**2/2)
            (p.moveTo if i==0 else p.lineTo)(xx*u,yy*u)
        c.save(); c.clipRect(skia.Rect.MakeLTRB(0,0,(fx0+(fx1-fx0)*ck)*u,ctx.H)); c.drawPath(p,paint('#fff4d8',a,stroke=1.4*u)); c.restore()
def axioms(ctx,e,t,frame):
    """numbered formula rows: rows=[[num, formula, desc, at]] — garamond italic formula, grey desc right, roman numeral left"""
    a=env(e,t,.5,.5)
    if a<=0: return
    c=ctx.c; u=U(ctx); x=e.get('x',150); y=e.get('y',180); dy=e.get('dy',58)
    c.drawLine((x-10)*u,(y-30)*u,(x-10)*u,(y+dy*(len(e['rows'])-1)+20)*u,paint(GOLD2,a*.4,stroke=.8*u))
    for i,r in enumerate(e['rows']):
        k=ease_out_cubic(prog(t,r[3] if len(r)>3 else e['t0']+i*.8,.7)); yy=y+i*dy
        if k<=0: continue
        draw_text(c,r[0],(x-25)*u,yy*u,F('garamond',10*u),GREY,a*k,'center')
        draw_text(c,r[1],(x+30+(1-k)*-10)*u,yy*u,F('garamond-italic',e.get('size',22)*u,500),'#e8dcc0',a*k,'left')
        draw_text(c,r[2],(x+e.get('desc_dx',640))*u,yy*u,SER(10*u,500),'#bfb3a0',a*k,'left')

# ---------------- background ----------------
def _bg(ctx,S,t,frame):
    c=ctx.c; W,H=ctx.W,ctx.H; b=S.get('bg',{})
    gx,gy=b.get('glow',[.5,.35]); g=skia.GradientShader.MakeRadial((gx*W,gy*H),max(W,H)*.75,[hexc(b.get('c1','#2a221a')),hexc(b.get('c2','#141210')),hexc(b.get('c3','#08080a'))],[0,.45,1])
    q=skia.Paint(); q.setShader(g); c.drawRect(skia.Rect.MakeWH(W,H),q)
    r=random.Random(11); u=U(ctx)
    for i in range(b.get('motes',90)):
        x=(r.random()*1100+t*r.uniform(-4,4)*3)%1100-40; y=(r.random()*620-t*r.uniform(2,8))%620-20; s=r.uniform(.6,2.4)
        al=.08+.25*(.5+.5*math.sin(t*r.uniform(.3,1.)+i))
        c.drawCircle(x*u,y*u,s*u*(2 if s>2 else 1),paint('#f0c880',al*(.5 if s>2 else 1),blur=(2.5 if s>2 else .4)*u))
def spark(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    RICH.motes(ctx.c,ctx.W,ctx.H,t,n=e.get('n',70),color=e.get('color','#f0c880'),a=a*e.get('a',.5),seed=e.get('seed',13),speed=e.get('speed',1.3))
def chapter(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c;u=U(ctx);k=ease_out_cubic(prog(t,e['t0'],.5))
    draw_text(c,e.get('no',''),e.get('x',990)*u,40*u,font('garamond',18*u),GOLD,a*k,'right')
    draw_text(c,e.get('text',''),e.get('x',990)*u,58*u,font('serif',11*u),'#d8cfbf',a*k,'right')
def beatflash(ctx,e,t,frame):
    beats=e.get('beats') or getattr(ctx,'beats',[])
    if not beats: return
    a=e.get('a',.35); col=e.get('col','#fff4dc'); win=e.get('window',.07)
    b=min(beats,key=lambda x:abs(x-t)); d=abs(t-b)
    if d>win: return
    k=(1-d/win)**1.5; ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(col,a*k))

EXTRA=dict(beatflash=beatflash,caption=caption,yearstamp=yearstamp,bookcard=bookcard,brand=brand,label=label,textblock=textblock,title=title,refs=refs,bigword=bigword,
           die=die,bones=bones,wheel=wheel,coin=coin,scoreboard=scoreboard,dienet=dienet,fraction=fraction,combos=combos,panels=panels,
           countrymap=countrymap,quote=quote,tree=tree,ledger=ledger,tally=tally,urnchart=urnchart,binom=binom,needles=needles,galton=galton,axioms=axioms,
           spark=spark,chapter=chapter)
def _render_sc(ctx,sc,t,frame):
    draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)
def draw(ctx,t,frame,S):
    ctx.beats=S.get('beats',[])
    c=ctx.c; _bg(ctx,S,t,frame)
    # boost default motes via bg.motes if set low
    RICH.compose_scenes(ctx,S,t,frame,_render_sc,overlays_extra=EXTRA,clear=None,
                        vignette_s=.5,grain_a=.035,band_color='#e2bf7c',design_size=(1024,576))
    # NOTE: full-frame RICH.beat_punch + type=beatflash cause eye-pain strobe at ~112 BPM.
# Default beat_punch OFF; if enabled keep punch_a <= 0.05. Prefer local pulses (beatrings/motes/pulse).
    if S.get('beat_punch',False) and getattr(ctx,'beats',None): RICH.beat_punch(ctx.c,ctx.W,ctx.H,t,ctx.beats,a=S.get('punch_a',.05),color=S.get('punch_col','#e2bf7c'),window=.06)
