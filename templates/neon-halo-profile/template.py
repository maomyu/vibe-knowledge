"""#24 霓虹光环侧影 (neon-halo-profile) — ref 7699336324809067817《七美德》1920x1080 50.2s (San). Topic-agnostic.
Near-black purple stage with letterbox bars; right side: line-art human head profile (faces left) with neon glow stroke,
optional fill tint, circular halo (soft ring + radial rays), gold halo ellipse, veil lines, small glowing prop icon
(cup, hourglass, heart, sun, flower, coin, bread); left side: chapter kicker, huge serif title with RGB chromatic
split + glow (or gold gradient), spaced italic latin, thin rule, two "label value latin" rows; centred quotes
(“…”) and caption lines; scattered gold tags; intro title over a halo ring. Design space 1024 x 576."""
import math, random, skia
from engine.core import *
from engine.layers import draw_elements, U

def prepare(S):
    for sc in S['scenes']:
        for e in sc['elements']: e.setdefault('t0',sc['t0']); e.setdefault('t1',sc['t1'])
    # dots.n defaults to the number of distinct chapter titles (left-aligned ctext) in the script
    n=len({e['text'] for sc in S['scenes'] for e in sc['elements'] if e.get('type')=='ctext' and e.get('align','left')=='left' and e.get('size',90)>=100})
    for sc in S['scenes']:
        for e in sc['elements']:
            if e.get('type')=='dots' and 'n' not in e and n: e['n']=n
def env(e,t,fi=.4,fo=.4): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def bg(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx)
    c.drawRect(skia.Rect.MakeWH(W,H),paint(e.get('col','#0e0c13')))
    if e.get('tint'): c.drawCircle(e.get('tx',800)*u,300*u,600*u,paint(e['tint'],e.get('ta',.18),blur=200*u))
    R=random.Random(5)
    for i in range(50): c.drawCircle(R.uniform(0,1024)*u,R.uniform(40,540)*u,R.uniform(.5,1.2)*u,paint('#ffffff',R.uniform(.1,.4)*(.6+.4*math.sin(t*2+i))))
    vignette(c,W,H,.6)
    if e.get('bars',True):
        b=e.get('barh',34);c.drawRect(skia.Rect.MakeLTRB(0,0,W,b*u),paint('#000000'));c.drawRect(skia.Rect.MakeLTRB(0,(576-b)*u,W,H),paint('#000000'))
HEAD=[('m',1040,500),('c',980,500,915,480,905,420),('c',900,390,935,380,935,330),('c',935,200,880,128,820,126),('c',760,124,735,165,738,215),('c',740,240,730,262,712,290),
      ('c',704,302,712,308,722,310),('c',720,320,726,326,722,334),('c',718,342,728,350,732,358),('c',738,376,750,388,790,392),('c',800,420,800,450,792,480),('c',760,500,700,520,640,560)]
def head_path(x,y,s,u):
    p=skia.Path()
    for op,*v in HEAD:
        pts=[((v[i]-820)*s+x)*u for i in range(0,len(v),2)];ys=[((v[i]-330)*s+y)*u for i in range(1,len(v),2)]
        if op=='m': p.moveTo(pts[0],ys[0])
        else: p.cubicTo(pts[0],ys[0],pts[1],ys[1],pts[2],ys[2])
    return p
def head(ctx,e,t,frame):
    a=env(e,t,e.get('fi',.6),e.get('fo',.4))
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,s=e.get('x',820),e.get('y',330),e.get('s',1);col=e.get('col','#e0a070');pulse=.85+.15*math.sin(t*2.2)
    hr=e.get('halo',190);RY=kfi(e.get('rays',1),t)
    if hr:
        hx,hy=x+e.get('hdx',-15)*s,y+e.get('hdy',-75)*s
        if RY:
            for i in range(72):
                an=i/72*math.tau;r0=(hr+8)*s;r1=(hr+60+40*(i%3==0))*s*1.6
                line(c,(hx+r0*math.cos(an))*u,(hy+r0*math.sin(an))*u,(hx+r1*math.cos(an))*u,(hy+r1*math.sin(an))*u,col,a*.18*RY,w=1*u)
        c.drawCircle(hx*u,hy*u,hr*s*u,paint(col,a*.5*pulse,stroke=26*s*u,blur=22*u))
        c.drawCircle(hx*u,hy*u,(hr-10)*s*u,paint('#06050a',a*.85))
        c.drawCircle(hx*u,hy*u,hr*s*u,paint(col,a*.35,stroke=2*u))
    p=head_path(x,y,s,u);rev=clamp((t-e['t0'])/e.get('draw',.0001)) if e.get('draw') else 1
    fill=kfi(e.get('fill',0),t)
    c.drawPath(p,paint('#050407',a))
    if fill: c.drawPath(p,paint(col,a*fill))
    if rev<1:
        m=skia.PathMeasure(p,False);L=m.getLength();q=skia.Path();m.getSegment(0,L*rev,q,True);p=q
    c.drawPath(p,paint(col,a*.6*pulse,stroke=8*u,blur=8*u));c.drawPath(p,paint('#fff4e8',a,stroke=2*u))
    if rev>=1:
        X=lambda v:((v-820)*s+x)*u;Y=lambda v:((v-330)*s+y)*u
        line(c,X(748),Y(242),X(770),Y(240),'#fff4e8',a,w=1.6*u)
        if e.get('eye_glow'): c.drawOval(skia.Rect.MakeLTRB(X(746),Y(236),X(772),Y(248)),paint(col,a*.8))
        q=skia.Path();q.moveTo(X(725),Y(332));q.quadTo(X(735),Y(340),X(752),Y(330));c.drawPath(q,paint('#fff4e8',a,stroke=1.6*u))
        q=skia.Path();q.moveTo(X(858),Y(245));q.cubicTo(X(880),Y(240),X(885),Y(285),X(862),Y(290));c.drawPath(q,paint('#fff4e8',a,stroke=1.6*u))
        q=skia.Path();q.moveTo(X(762),Y(280));q.quadTo(X(775),Y(300),X(770),Y(330));c.drawPath(q,paint('#fff4e8',a*.6,stroke=1.2*u))
        if e.get('veil'):
            q=skia.Path();q.moveTo(X(780),Y(130));q.cubicTo(X(900),Y(90),X(960),Y(250),X(1000),Y(560));c.drawPath(q,paint('#d8e0f0',a*.7,stroke=1.4*u))
            q=skia.Path();q.moveTo(X(760),Y(150));q.cubicTo(X(860),Y(140),X(900),Y(300),X(940),Y(560));c.drawPath(q,paint('#d8e0f0',a*.4,stroke=1*u))
        if e.get('ring'):
            c.drawOval(skia.Rect.MakeLTRB(X(705),Y(80),X(900),Y(118)),paint('#f0c060',a*.6,stroke=5*u,blur=5*u));c.drawOval(skia.Rect.MakeLTRB(X(705),Y(80),X(900),Y(118)),paint('#ffe0a0',a,stroke=1.6*u))
def prop(ctx,e,t,frame):
    a=env(e,t,.4,.3)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,s=e.get('x',650),e.get('y',380),e.get('s',1);col=e.get('col','#f0b080');k=e.get('kind','sun');bob=math.sin(t*2)*3
    y+=bob;G=lambda: paint(col,a*.5,stroke=6*u,blur=6*u);L=lambda w=1.8: paint('#fff4e8',a,stroke=w*u)
    def both(p): c.drawPath(p,G());c.drawPath(p,L())
    if k=='sun':
        c.drawCircle(x*u,y*u,16*s*u,paint(col,a,blur=3*u))
        for i in range(5): an=math.pi*(1.1+i*.2);line(c,(x+24*s*math.cos(an))*u,(y+24*s*math.sin(an))*u,(x+34*s*math.cos(an))*u,(y+34*s*math.sin(an))*u,col,a,w=1.5*u)
    elif k=='cup':
        p=skia.Path();p.moveTo((x-18*s)*u,(y-14*s)*u);p.lineTo((x+18*s)*u,(y-14*s)*u);p.lineTo((x+12*s)*u,(y+16*s)*u);p.lineTo((x-12*s)*u,(y+16*s)*u);p.close();both(p)
        p=skia.Path();p.addArc(skia.Rect.MakeLTRB((x+12*s)*u,(y-8*s)*u,(x+28*s)*u,(y+8*s)*u),-90,180);both(p)
    elif k=='hourglass':
        p=skia.Path();p.moveTo((x-16*s)*u,(y-26*s)*u);p.lineTo((x+16*s)*u,(y-26*s)*u);p.lineTo((x-16*s)*u,(y+26*s)*u);p.lineTo((x+16*s)*u,(y+26*s)*u);p.close();both(p)
        fl=(t*.3)%1;c.drawRect(skia.Rect.MakeLTRB((x-8*s*(1-fl))*u,(y+26*s-14*s*fl)*u,(x+8*s*(1-fl))*u,(y+26*s)*u),paint(col,a*.8))
    elif k=='heart':
        for i in range(e.get('n',3)):
            yy=y+i*30*s-(t*15)%30;hx=x+math.sin(t+i)*6;p=skia.Path();r=7*s
            p.moveTo(hx*u,(yy+r)*u);p.cubicTo((hx-2*r)*u,(yy-r*.4)*u,(hx-r*.6)*u,(yy-1.6*r)*u,hx*u,(yy-r*.5)*u);p.cubicTo((hx+r*.6)*u,(yy-1.6*r)*u,(hx+2*r)*u,(yy-r*.4)*u,hx*u,(yy+r)*u)
            c.drawPath(p,paint(col,a*(1-i*.25)))
    elif k=='flower':
        for j,(dx,dy) in enumerate(e.get('pos',[[0,0]])):
            for i in range(5): an=i/5*math.tau+t*.3;c.drawCircle((x+dx+8*s*math.cos(an))*u,(y+dy+8*s*math.sin(an))*u,6*s*u,paint(col,a*.9))
            c.drawCircle((x+dx)*u,(y+dy)*u,3*s*u,paint('#fff4e8',a))
    elif k=='coin':
        c.drawCircle(x*u,y*u,14*s*u,paint(col,a*.9));c.drawCircle(x*u,y*u,10*s*u,paint('#fff4e8',a*.6,stroke=1.4*u))
    elif k=='bread':
        c.drawOval(skia.Rect.MakeLTRB((x-28*s)*u,(y-10*s)*u,(x+28*s)*u,(y+12*s)*u),paint('#100c0c',a));c.drawOval(skia.Rect.MakeLTRB((x-28*s)*u,(y-10*s)*u,(x+28*s)*u,(y+12*s)*u),L())
def ctext(ctx,e,t,frame):
    """big title with chroma split; gold=True gives gold gradient fill; reveal=chars/s letter reveal."""
    a=env(e,t,e.get('fi',.3),e.get('fo',.3))
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('size',90);f=font(e.get('font','serif-vf'),s*u,e.get('weight',900) if e.get('font','serif-vf')=='serif-vf' else None);x,y=e.get('x',90),e.get('y',290);al=e.get('align','left');tx=e['text']
    if e.get('reveal'): tx=tx[:max(0,int((t-e['t0'])*e['reveal'])+1)]
    col=e.get('col','#f4ece0');ch=e.get('chroma',2.5)
    jit=e.get('jitter',1)*(1.5 if (frame//3)%7==0 else 0)
    if e.get('glow',1): draw_text(c,tx,x*u,y*u,f,e.get('gcol',col),a*.5,align=al,glow=14*u)
    if ch:
        draw_text(c,tx,(x-ch-jit)*u,y*u,f,'#ff3050',a*.7,align=al);draw_text(c,tx,(x+ch+jit)*u,y*u,f,'#30e0ff',a*.7,align=al)
    if e.get('gold'):
        g=skia.Paint(AntiAlias=True,Shader=skia.GradientShader.MakeLinear([skia.Point(0,(y-s)*u),skia.Point(0,y*u)],[hexc('#fff0c0'),hexc('#d8a850'),hexc('#8a6020')]))
        g.setAlphaf(a);w=text_width(tx,f);X=x*u-(w/2 if al=='center' else w if al=='right' else 0);c.drawString(tx,X,y*u,f,g)
    else: draw_text(c,tx,x*u,y*u,f,col,a,align=al)
def text(ctx,e,t,frame):
    a=env(e,t,e.get('fi',.3),e.get('fo',.3))
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('size',16);f=font(e.get('font','serif'),s*u);sp=e.get('spacing',0);tx=e['text']
    if sp: tx=(' '*sp).join(tx)
    draw_text(c,tx,e.get('x',90)*u,e.get('y',200)*u,f,e.get('col','#d8ccc0'),a,align=e.get('align','left'),glow=e.get('glow',0)*u)
def rule(ctx,e,t,frame):
    a=env(e,t);
    if a<=0: return
    u=U(ctx);x0,x1,y=e.get('x0',90),e.get('x1',360),e.get('y',382);g=clamp((t-e['t0'])/.5)
    line(ctx.c,x0*u,y*u,(x0+(x1-x0)*g)*u,y*u,e.get('col','#8a7a6a'),a*.7,w=1*u)
def ring(ctx,e,t,frame):
    a=env(e,t,.5,.4)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e.get('x',512),e.get('y',288),e.get('r',80);col=e.get('col','#e0b060');g=clamp((t-e['t0'])/e.get('grow',.6))
    p=skia.Path();p.addArc(skia.Rect.MakeLTRB((x-r)*u,(y-r)*u,(x+r)*u,(y+r)*u),-90,360*g)
    c.drawPath(p,paint(col,a*.6,stroke=6*u,blur=8*u));c.drawPath(p,paint('#ffe8c0',a,stroke=1.6*u))
def dots(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    u=U(ctx);x,y=e.get('x',512),e.get('y',340);cols=e.get('cols',['#e0e0f0','#40c0c0','#e0a070','#e0c050','#60c090','#e090b0','#90a0e0','#c080e0','#e07060','#80d0f0']);n=e.get('n',len(cols));cols=[cols[i%len(cols)] for i in range(n)]
    for i,cl in enumerate(cols): ctx.c.drawCircle((x+(i-(len(cols)-1)/2)*12)*u,y*u,2.4*u,paint(cl,a))
def tint(ctx,e,t,frame): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#000000'),env(e,t,e.get('fi',.3),e.get('fo',.3))))
def flash(ctx,e,t,frame):
    if e['t0']<=t<e['t0']+e.get('dur',.034): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#ffffff'),e.get('a',1)))
EXTRA=dict(bg=bg,head=head,prop=prop,ctext=ctext,text=text,rule=rule,ring=ring,dots=dots,tint=tint,flash=flash)
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
