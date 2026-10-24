"""#15 乐理可视化 (music-theory-visualizer) — ref 7697671776544804138《宫商角徵羽》1920x1080 104.3s. Topic-agnostic.
Deep blue-black (#0c0e13) with faint grid + vignette; mono-spaced corner HUD (EN caps label · 中文, big mono counters);
five-colour note glyphs (宫 gold / 商 pale-gold / 角 coral / 徵 cyan / 羽 violet) in bold serif with glow; glowing
strings with end caps and length counters; pitch bars with ellipse rings; sine waves + sum; Lissajous; piano keyboard
with lit keys; pentagram; five vertical plucked strings; guitar fretboard; petal flower; skewed cards with diagonal
light sweep; jianpu digit sequence; numbered conclusion list. Serif-bold white subtitles. Design space 1024x576."""
import math, random, numpy as np, skia
from engine.core import *
from engine.layers import draw_elements, U

COL={'宫':'#f2b450','商':'#f0d28a','角':'#f07850','徵':'#4cc8d8','羽':'#8c84f2'}
DEG={'1':'#f2b450','2':'#f0d28a','3':'#f07850','5':'#4cc8d8','6':'#8c84f2'}
def prepare(S): pass
def env(e,t,fi=.3,fo=.3): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def M(s,b=True): return font('mono-bold' if b else 'mono',s)
def SR(s): return font('serif-bold',s)
def gl(c,ch,x,y,f,col,a,glow=14,align='center'): draw_text(c,ch,x,y,f,col,a,align=align,glow=glow,glow_color=col,glow_a=.55)
def bg(ctx,e,t,frame):
    c=ctx.c;u=U(ctx);W,H=ctx.W,ctx.H; c.drawRect(skia.Rect.MakeWH(W,H),paint(e.get('col','#0c0e13')))
    p=paint('#ffffff',.035,stroke=1)
    for x in range(0,1025,32): c.drawLine(x*u,0,x*u,H,p)
    for y in range(0,577,32): c.drawLine(0,y*u,W,y*u,p)
    if e.get('tint'): c.drawRect(skia.Rect.MakeWH(W,H),paint(e['tint'],e.get('tint_a',.3)))
    vignette(c,W,H,.55)
def hud(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx)
    for key,x,al in (('tl',37,'left'),('tr',987,'right')):
        if e.get(key):
            en,zh=e[key][:2]; draw_text(c,en,x*u,37*u,M(9*u,False),'#8a8a90',a,align=al,spacing=2.2*u)
            if zh: draw_text(c,zh,x*u,52*u,font('sans',9*u),'#6a6a70',a,align=al)
    for key,x,al in (('big_tl',37,'left'),('big_tr',987,'right')):
        if e.get(key) is not None:
            v=e[key]; v=('%02d'%int(kfi(v,t))) if isinstance(v,list) else str(v); draw_text(c,v,x*u,80*u,M(32*u),'#f0ece0',a,align=al)
    if e.get('bl'): draw_text(c,e['bl'],37*u,553*u,font('sans',9*u),'#7a7a80',a,align='left',spacing=1*u)
def sub(ctx,e,t,frame):
    a=env(e,t,.2,.2)
    if a<=0: return
    u=U(ctx);f=SR(e.get('size',22)*u);txt=e['text'];x=e.get('x',512)*u;y=e.get('y',527)*u
    runs=[];b='';cc=None
    for ch in txt:
        if ch=='[': runs.append((b,None)); b=''; cc=e.get('hi','#f07850')
        elif ch==']': runs.append((b,cc)); b=''; cc=None
        else: b+=ch
    runs.append((b,cc)); tw=sum(f.measureText(r) for r,_ in runs); x-=tw/2 if e.get('align','center')=='center' else 0
    for r,cc in runs:
        if r: draw_text(ctx.c,r,x,y,f,cc or e.get('col','#f2eee6'),a,align='left'); x+=f.measureText(r)
def glyph(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);ch=e['text'];col=e.get('col',COL.get(ch,'#f2b450'));sz=e.get('size',90);k=ease_out_back(clamp((t-e['t0'])/.45))
    c.save(); c.translate(e['x']*u,e['y']*u); c.scale(k,k); gl(c,ch,0,sz*.36*u,SR(sz*u),col,a,e.get('glow',18)*u); c.restore()
    if e.get('pinyin'): draw_text(c,e['pinyin'],(e['x']+sz*.62)*u,(e['y']+sz*.3)*u,font('garamond-italic',sz*.28*u),'#8a8a90',a,align='left')
def text(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    u=U(ctx);x=e.get('x',512);y=e.get('y',300);f=(M if e.get('mono') else (SR if e.get('serif',True) else (lambda s:font('sans',s))))(e.get('size',16)*u)
    runs=e['runs'] if 'runs' in e else [[e['text'],e.get('col','#f2eee6')]]; tw=sum(f.measureText(r[0]) for r in runs)
    xx=x*u-(tw/2 if e.get('align','center')=='center' else (tw if e.get('align')=='right' else 0))
    for r in runs:
        k=clamp((t-(r[2] if len(r)>2 else e['t0']))/.3); draw_text(ctx.c,r[0],xx,y*u,f,r[1],a*k,align='left',glow=e.get('glow',0)*u,glow_color=r[1]); xx+=f.measureText(r[0])
def counter(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e['x'],e['y']; v=kfi(e['value'],t); s=e.get('fmt','%d')%v
    if e.get('label'): draw_text(c,e['label'],x*u,(y-44)*u,M(8*u,False),'#8a8a90',a,align=e.get('align','left'),spacing=2*u)
    gl(c,s,x*u,y*u,M(e.get('size',40)*u),e.get('col','#f2c060'),a,8*u,align=e.get('align','left'))
def string(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x0=e.get('x0',80);L=kfi(e.get('len',390),t);y=e.get('y',300);col=e.get('col','#f2c060');x1=x0+L
    amp=0
    for pt in e.get('pluck',[]):
        if t>=pt: amp=max(amp,6*math.exp(-(t-pt)*2.5))
    p=skia.Path(); p.moveTo(x0*u,y*u)
    for i in range(1,41): xx=x0+L*i/40; p.lineTo(xx*u,(y+amp*math.sin(math.pi*i/40)*math.sin(t*50))*u)
    c.drawPath(p,paint(col,.5*a,stroke=6*u,blur=5*u)); c.drawPath(p,paint(col,a,stroke=2.2*u))
    for xx in (x0,x1): rrect(c,(xx-3)*u,(y-11)*u,6*u,22*u,2*u,fill=hexc('#d8d4cc',a))
    if e.get('label'): draw_text(c,e['label'],x0*u,(y-20)*u,M(10*u,False),col,a,align='left',spacing=1*u)
    if e.get('ring'): c.drawCircle((x0+L/2)*u,y*u,e['ring']*u,paint('#c0a070',.5*a,stroke=1*u))
def bars(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);its=e['items'];x0=e.get('x0',283);w=e.get('w',75);gap=e.get('gap',22);yb=e.get('y',435)
    for i,it in enumerate(its):
        x=x0+i*(w+gap);col=it.get('col',DEG.get(str(it.get('num','1')),'#f2b450'));h=kfi(it.get('h',0),t);on=kfi(it.get('on',.3),t)
        if h>0: c.drawRect(skia.Rect.MakeXYWH(x*u,(yb-h)*u,w*u,h*u),paint(col,.25*a*(.4+on)))
        rrect(c,x*u,(yb-4)*u,w*u,9*u,4*u,fill=hexc(col,a*(.35+.65*on)))
        if on>.5: c.drawCircle((x+w/2)*u,yb*u,40*u,paint(col,.25*a*on,blur=20*u))
        if it.get('ring'): c.drawOval(skia.Rect.MakeXYWH((x-28)*u,(yb-18)*u,(w+56)*u,40*u),paint(col,.6*a*on,stroke=1.2*u))
        if it.get('num') and h>20: draw_text(c,str(it['num']),(x+w-12)*u,(yb-h*.08-30)*u,M(14*u),col,a*.7)
    if e.get('ghost'): draw_text(c,str(kfi(e['ghost'],t)) if not isinstance(e['ghost'],str) else e['ghost'],512*u,360*u,M(300*u),'#ffffff',.07*a)
def wave(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e.get('x',70),e.get('y',300),e.get('w',885),e.get('h',180)
    rrect(c,x*u,y*u,w*u,h*u,8*u,fill=hexc('#14161c',.7*a),stroke=hexc('#2a2c34',a),sw=1*u)
    k=clamp((t-e['t0'])/e.get('draw',1.5)); ws=e['waves']
    for wi,wv in enumerate(ws):
        cy=y+wv.get('cy',(wi+1)*h/(len(ws)+1)); p=skia.Path(); n=200
        for i in range(int(n*k)+1):
            xx=x+10+(w-20)*i/n; ph=i/n*2*math.pi
            if wv.get('sum'): v=sum(math.sin(ph*q['f']+q.get('ph',0)-t*q.get('sp',0)) for q in ws if not q.get('sum'))/2
            else: v=math.sin(ph*wv['f']+wv.get('ph',0)-t*wv.get('sp',0))
            yy=cy-v*wv.get('amp',20); p.lineTo(xx*u,yy*u) if i else p.moveTo(xx*u,yy*u)
        col=wv.get('col','#ffffff'); c.drawPath(p,paint(col,.4*a,stroke=5*u,blur=4*u)); c.drawPath(p,paint(col,a,stroke=1.8*u))
        if wv.get('label'): draw_text(c,wv['label'],(x+10+wi*160)*u,(y+16)*u,M(9*u,False),col,a,align='left',spacing=1*u)
    for m in e.get('marks',[]): c.drawLine((x+10+(w-20)*m)*u,y*u,(x+10+(w-20)*m)*u,(y+h)*u,paint('#d0d0d0',.8*a,stroke=1.2*u))
def lissa(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e['x'],e['y'],e.get('r',90);A,B=e.get('ratio',[3,2]);k=clamp((t-e['t0'])/e.get('draw',2.5))
    c.drawCircle(x*u,y*u,r*1.15*u,paint('#ffffff',.06*a,stroke=1*u)); p=skia.Path(); n=600; ph=e.get('ph',.6)+t*e.get('spin',0)
    for i in range(int(n*k)+1):
        s=i/n*2*math.pi; xx=x+r*math.sin(A*s+ph); yy=y+r*math.sin(B*s); p.lineTo(xx*u,yy*u) if i else p.moveTo(xx*u,yy*u)
    col=e.get('col','#ffffff'); c.drawPath(p,paint(col,.4*a,stroke=6*u,blur=5*u)); c.drawPath(p,paint(col,a,stroke=2*u))
def piano(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e.get('x',300),e.get('y',320),e.get('w',420),e.get('h',140);n=e.get('white',14);kw=w/n
    lit={}
    for L in e.get('lit',[]):
        if L[0]<=t<L[1]: lit[L[2]]=L[3]
    for i in range(n):
        col=lit.get('w%d'%i); rrect(c,(x+i*kw+1)*u,y*u,(kw-2)*u,h*u,3*u,fill=hexc('#e8e4dc',a))
        if col: rrect(c,(x+i*kw+1)*u,y*u,(kw-2)*u,h*u,3*u,fill=hexc(col,.75*a)); c.drawRect(skia.Rect.MakeXYWH((x+i*kw)*u,(y-30)*u,kw*u,30*u),paint(col,.25*a,blur=12*u))
        if e.get('labels') and 'w%d'%i in e['labels']: draw_text(c,e['labels']['w%d'%i],(x+i*kw+kw/2)*u,(y+h-12)*u,SR(10*u),'#3a3a3a',a)
    for i in range(n-1):
        if i%7 in (2,6): continue
        col=lit.get('b%d'%i); bx=x+(i+1)*kw-kw*.3; c.drawRect(skia.Rect.MakeXYWH(bx*u,y*u,kw*.6*u,h*.6*u),paint(col or '#16161a',a*(.85 if col else 1)))
def penta(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e.get('x',512),e.get('y',245),e.get('r',165);names=e.get('names',['宫','商','角','徵','羽'])
    P=[(x+r*math.sin(i*2*math.pi/5),y-r*math.cos(i*2*math.pi/5)) for i in range(5)]
    c.drawCircle(x*u,y*u,r*u,paint('#ffffff',.08*a,stroke=1*u)); order=e.get('order',[0,3,1,4,2,0]); k=clamp((t-e.get('draw_t',e['t0']))/e.get('draw',2))*(len(order)-1)
    p=skia.Path(); p.moveTo(P[order[0]][0]*u,P[order[0]][1]*u)
    for j in range(1,len(order)):
        f=clamp(k-(j-1))
        if f<=0: break
        A,B=P[order[j-1]],P[order[j]]; p.lineTo((A[0]+(B[0]-A[0])*f)*u,(A[1]+(B[1]-A[1])*f)*u)
    if k>=len(order)-1: c.drawPath(p,paint('#f2c060',.10*a))
    c.drawPath(p,paint('#f2c060',.4*a,stroke=6*u,blur=5*u)); c.drawPath(p,paint('#f2d080',a,stroke=2.2*u))
    for i,(px,py) in enumerate(P):
        col=COL.get(names[i],'#f2b450'); c.drawCircle(px*u,py*u,27*u,paint(col,.4*a,blur=10*u)); c.drawCircle(px*u,py*u,25*u,paint('#0c0e13',a)); c.drawCircle(px*u,py*u,25*u,paint(col,a,stroke=2*u))
        draw_text(c,names[i],px*u,(py+8)*u,SR(21*u),col,a)
def strings5(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);xs=e.get('xs',[155,268,382,495,608]);y0,y1=e.get('y0',90),e.get('y1',420);names=e.get('names',['宫','商','角','徵','羽'])
    for i,x in enumerate(xs):
        col=COL.get(names[i],'#f2b450'); amp=0; lit=0
        for pt in e.get('pluck',[]):
            if pt[1]==i and t>=pt[0]: amp=max(amp,5*math.exp(-(t-pt[0])*3)); lit=max(lit,math.exp(-(t-pt[0])*1.5))
        p=skia.Path(); p.moveTo(x*u,y0*u)
        for j in range(1,31): yy=y0+(y1-y0)*j/30; p.lineTo((x+amp*math.sin(math.pi*j/30)*math.sin(t*60))*u,yy*u)
        c.drawPath(p,paint(col,(.2+.5*lit)*a,stroke=5*u,blur=4*u)); c.drawPath(p,paint(col,(.5+.5*lit)*a,stroke=1.6*u))
        draw_text(c,names[i],x*u,(y1+30)*u,SR(15*u),col,a)
        if lit>.3: c.drawCircle(x*u,((y0+y1)/2)*u,10*u,paint(col,lit*a,blur=4*u))
def fret(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e.get('x',270),e.get('y',150),e.get('w',470),e.get('h',190);nf=e.get('frets',12)
    rrect(c,x*u,y*u,w*u,h*u,3*u,fill=hexc('#2a1e16',a))
    for i in range(nf+1): c.drawLine((x+w*i/nf)*u,y*u,(x+w*i/nf)*u,(y+h)*u,paint('#a09080',.7*a,stroke=1.5*u))
    for s in range(6): c.drawLine(x*u,(y+h*(s+.5)/6)*u,(x+w)*u,(y+h*(s+.5)/6)*u,paint('#d8d0c0',.8*a,stroke=(1+s*.3)*u))
    for d in e.get('dots',[]):
        f,s,ch=d[:3]; td=d[3] if len(d)>3 else e['t0']; k=ease_out_back(clamp((t-td)/.35))
        if k<=0: continue
        px=x+w*(f-.5)/nf; py=y+h*(s+.5)/6; col=COL.get(ch,DEG.get(ch,'#f2b450'))
        c.drawCircle(px*u,py*u,9*k*u,paint(col,.5*a,blur=5*u)); c.drawCircle(px*u,py*u,8*k*u,paint('#1a1410',a)); c.drawCircle(px*u,py*u,8*k*u,paint(col,a,stroke=2*u))
def flower(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e.get('x',512),e.get('y',260);rings=e.get('rings',[[5,60,16,'#f2c060'],[5,115,22,'#4cc8d8'],[5,175,26,'#f07850']]);rot=t*e.get('spin',.15)
    for ri,(n,R,s,col) in enumerate(rings):
        k=clamp((t-e['t0']-ri*.25)/.6); off=(ri%2)*math.pi/n
        for i in range(n):
            th=rot*(1 if ri%2 else -1)+off+i*2*math.pi/n; px=x+R*k*math.cos(th); py=y+R*k*math.sin(th)
            c.save(); c.translate(px*u,py*u); c.rotate(math.degrees(th)+90); r=skia.Rect.MakeXYWH(-s*.55*u,-s*1.3*u,s*1.1*u,s*2.6*u)
            c.drawOval(r,paint(col,.35*a*k,blur=6*u)); c.drawOval(r,paint(col,.25*a*k)); c.drawOval(r,paint(col,a*k,stroke=2*u)); c.restore()
    if e.get('center'): gl(c,e['center'],x*u,(y+22)*u,SR(64*u),COL.get(e['center'],'#f07850'),a,12*u)
def cards(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);its=e['items'];x0,y,w,h,gap=e.get('x0',60),e.get('y',105),e.get('w',165),e.get('h',350),e.get('gap',30);sk=e.get('skew',.06)
    for i,it in enumerate(its):
        ch=it[0];col=COL.get(ch,'#f2b450');k=clamp((t-e['t0']-i*.12)/.4);x=x0+i*(w+gap)
        c.save(); c.translate((x+w/2)*u,(y+h/2+(1-k)*20)*u); c.skew(-sk,0)
        rrect(c,-w/2*u,-h/2*u,w*u,h*u,6*u,fill=hexc(col,.1*a*k),stroke=hexc(col,a*k),sw=1.5*u)
        gl(c,ch,0,(-10+40)*u,SR(110*u),col,a*k,10*u); draw_text(c,it[1],0,(h/2-55)*u,M(34*u),'#f2eee6',a*k); c.restore()
    sw=e.get('sweep')
    if sw and sw[0]<=t<sw[1]:
        q=(t-sw[0])/(sw[1]-sw[0]); cx=-200+q*1400
        for dx,wd,al,col in ((0,240,.85,'#5cd0e0'),(-60,20,.6,'#d0d0d0')):
            p=skia.Path(); p.moveTo((cx+dx)*u,600*u); p.lineTo((cx+dx+wd)*u,600*u); p.lineTo((cx+dx+wd+220)*u,-20*u); p.lineTo((cx+dx+220)*u,-20*u); p.close(); c.drawPath(p,paint(col,al*a))
def seq(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e['text'];x=e.get('x',512);y=e.get('y',82);sz=e.get('size',20);sp=sz*1.0;n=len(s);x0=x-(n-1)*sp/2;hi=e.get('hi')
    for i,ch in enumerate(s):
        k=clamp((t-e['t0']-i*e.get('stag',0))/.2)
        if k<=0: continue
        col=DEG.get(ch,'#aaaaaa'); al=a*k*(1 if hi is None or int(kfi(hi,t))==i else .55); cx=(x0+i*sp)*u
        draw_text(c,ch,cx,y*u,M(sz*u),col,al)
        if e.get('dots') and e['dots'][i]: c.drawCircle(cx,(y-sz*.95)*u,1.6*u,paint(col,al))
def items(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e.get('x',512),e.get('y',190);lh=e.get('lh',34)
    if e.get('title'): draw_text(c,e['title'],x*u,(y-34)*u,font('sans',8*u),'#7a7a80',a)
    for i,it in enumerate(e['items']):
        num,txt,col=it[:3]; ti=it[3] if len(it)>3 else e['t0']; k=clamp((t-ti)/.4)
        if k<=0: continue
        f=SR(e.get('size',17)*u); tw=f.measureText(txt)+M(16*u).measureText(num+' '); xx=x*u-tw/2
        draw_text(c,num+' ',xx,(y+i*lh)*u,M(16*u),col,a*k,align='left'); draw_text(c,txt,xx+M(16*u).measureText(num+' '),(y+i*lh)*u,f,'#f2eee6',a*k,align='left')
def chips(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e['x'],e['y'];sz=e.get('size',40);gap=e.get('gap',10)
    for i,it in enumerate(e['items']):
        ch=it[0];ti=it[2] if len(it)>2 else e['t0'];k=ease_out_back(clamp((t-ti)/.35))
        if k<=0: continue
        col=COL.get(ch,'#f2b450');xx=x+i*(sz+gap);act=it[3] if len(it)>3 else False
        rrect(c,xx*u,y*u,sz*u,sz*u,4*u,fill=hexc(col if act else '#0c0e13',.25 if act else a),stroke=hexc(col,a*k),sw=1.5*u)
        draw_text(c,ch,(xx+sz/2)*u,(y+sz*.68)*u,SR(sz*.55*u),col,a*k)
        if it[1]: draw_text(c,str(it[1]),(xx+sz/2)*u,(y+sz+13)*u,M(8*u,False),'#8a8a90',a*k)
def flash(ctx,e,t,frame):
    k=1-clamp((t-e['t0'])/e.get('dur',.034))
    if k>0: ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#ffffff'),k*e.get('a',.8)))
EXTRA={'bg':bg,'hud':hud,'sub':sub,'glyph':glyph,'text':text,'counter':counter,'string':string,'bars':bars,'wave':wave,'lissa':lissa,'piano':piano,'penta':penta,'strings5':strings5,'fret':fret,'flower':flower,'cards':cards,'seq':seq,'items':items,'chips':chips,'flash':flash}
def draw(ctx,t,frame,S):
    c=ctx.c; c.clear(hexc('#0c0e13')); draw_elements(ctx,S.get('under',[]),t,frame,EXTRA)
    for sc in S['scenes']:
        if sc['t0']-1e-6<=t<sc['t1']:
            k=fade_env(t,sc['t0'],sc['t1'],sc.get('fade_in',.3),sc.get('fade_out',.3))
            if k<=0: continue
            c.saveLayerAlpha(None,int(255*k)); draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)
            if sc.get('flash') and sc['t0']<=t<sc['t0']+.034: c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint('#ffffff',.85))
            c.restore()
    draw_elements(ctx,S.get('overlays',[]),t,frame,EXTRA)
