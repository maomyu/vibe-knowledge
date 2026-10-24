"""#20 琥珀散景文明史 (amber-bokeh-history) — ref 7692188183110356266《所有文明都酿酒》1280x720 161s (比特新语). Topic-agnostic.
Amber/umber grounds: procedural flowing amber marble (fbm noise), engraved stone, forest-trunk dusk, wheat-field hill,
near-black. Rising yeast-cell rings, multicolour bokeh, gold dust; real world map (Natural Earth) with glowing places;
stone relief stick figures; twin cell dials; vessels with glowing liquid (jar / goblet / tripod / cup / whiskey glass)
under spot beams; toasting glasses; top timeline ruler; three-panel icons (sprout / mold burst / dots).
Text: Songti/serif white, [金色] keywords; bottom subtitle; small top-left HUD captions. Design space 1024x576.
v3 RICHNESS: tin transitions, denser dust/bokeh, pour/spark/chapter. See RICHNESS_STANDARD.md.
"""
import math, os, random, numpy as np, skia
from functools import lru_cache
from engine.core import *
from engine.layers import draw_elements, U
from engine import richness as RICH

GOLD='#f2c25a';AMB='#c8842e'
def prepare(S): pass
def env(e,t,fi=.5,fo=.5): return fade_env(t,e['t0'],e['t1'],e.get('fi',fi),e.get('fo',fo))*e.get('a',1)
def kfi(keys,t):
    if not isinstance(keys,list) or not keys or not isinstance(keys[0],list): return keys
    if t<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if t<b: return va+(vb-va)*ease_in_out_cubic((t-a)/(b-a))
    return keys[-1][1]
def _fbm(w,h,seed,oct=5):
    R=np.random.default_rng(seed);out=np.zeros((h,w))
    for o in range(oct):
        s=2**o;g=R.random((h//(32//min(s,16))+2,w//(32//min(s,16))+2))
        import cv2
        out+=cv2.resize(g,(w,h),interpolation=cv2.INTER_CUBIC)/s
    out=(out-out.min())/(out.max()-out.min());return out
@lru_cache(16)
def tex(kind,seed=1):
    import cv2
    w,h=512,288
    if kind=='amber':
        n=_fbm(w,h,seed,5);n2=_fbm(w,h,seed+3,3);vein=np.exp(-np.abs(np.sin(n*4.5+n2*2))*9)*np.clip(n2*1.4-.2,0,1);glow=np.clip(n2-.45,0,1)*1.6
        base=.12+.25*n;r=np.clip(255*(base*.55+vein*.85+glow*.6),0,255);g=np.clip(255*(base*.3+vein*.5+glow*.4),0,255);b=np.clip(255*(base*.12+vein*.12+glow*.12),0,255)
        img=cv2.GaussianBlur(np.dstack([r,g,b]),(0,0),1.2)
    elif kind=='stone':
        n=_fbm(w,h,seed,6);n2=_fbm(w,h,seed+9,3);v=.55+.45*n
        img=np.dstack([70*v+20*n2,58*v+14*n2,46*v+8*n2])
        R=np.random.default_rng(seed);sp=R.random((h,w))>.985;img[sp]*=.55
    else:
        n=_fbm(w,h,seed);img=np.dstack([20+20*n,12+12*n,6+6*n])
    img=np.clip(img,0,255).astype(np.uint8);rgba=np.dstack([img,np.full((h,w),255,np.uint8)])
    return skia.Image.fromarray(np.ascontiguousarray(rgba),colorType=skia.kRGBA_8888_ColorType)
def bg(ctx,e,t,frame):
    c=ctx.c;W,H=ctx.W,ctx.H;u=U(ctx);k=e.get('kind','dark');a=e.get('a',1)
    c.drawRect(skia.Rect.MakeWH(W,H),paint('#0d0705'))
    if k in('amber','stone','dark2'):
        img=tex(k if k!='dark2' else 'dark',e.get('seed',1));dr=math.sin(t*.06)*e.get('drift',6)*6;sc=e.get('zoom',1.15)+.01*t*e.get('push',0)
        p=skia.Paint();p.setAlphaf(e.get('ta',1))
        c.drawImageRect(img,skia.Rect.MakeXYWH(-W*(sc-1)/2-dr*u*.3,-H*(sc-1)/2,W*sc,H*sc),skia.SamplingOptions(skia.FilterMode.kLinear),p)
    if k=='forest':
        c.drawRect(skia.Rect.MakeWH(W,H),skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0,0),skia.Point(0,H)],[hexc('#1a0c04'),hexc('#7a3a10'),hexc('#2a1206')],[0,.65,1])))
        R=random.Random(4)
        for i in range(14):
            x=R.uniform(0,1024);w=R.uniform(8,22);c.drawRect(skia.Rect.MakeXYWH((x-w/2)*u,0,w*u,430*u),paint('#120804'))
        c.drawRect(skia.Rect.MakeLTRB(0,0,W,90*u),paint('#140a04'))
        for i in range(40): c.drawCircle(R.uniform(0,1024)*u,R.uniform(0,100)*u,R.uniform(20,50)*u,paint('#1a0e06'))
        c.drawRect(skia.Rect.MakeLTRB(0,430*u,W,H),paint('#1a0a04'))
        for i in range(10):
            x=R.uniform(40,980);c.drawCircle(x*u,(415+R.uniform(0,10))*u,(3+R.random()*2)*u,paint('#ffb040',.9));c.drawCircle(x*u,415*u,14*u,paint('#ff9020',.35,blur=8*u))
    if k=='wheat':
        c.drawRect(skia.Rect.MakeWH(W,H),skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0,0),skia.Point(0,H)],[hexc('#3a1a08'),hexc('#c06a20'),hexc('#5a2a0a')],[0,.6,1])))
        R=random.Random(2);hy=lambda x:430+18*math.sin(x*.006+1)+10*math.sin(x*.017)
        for i in range(380):
            x=R.uniform(0,1024);h=R.uniform(40,130);sw=math.sin(t*1.2+x*.01)*5;y0=hy(x)
            line(c,x*u,y0*u,(x+sw)*u,(y0-h)*u,'#2a1306',.9,w=1*u)
            c.drawOval(skia.Rect.MakeXYWH((x+sw-2)*u,(y0-h-12)*u,4*u,14*u),paint('#3a1a08',.9))
        p=skia.Path();p.moveTo(0,H)
        for x in range(0,1030,10): p.lineTo(x*u,hy(x)*u)
        p.lineTo(W,H);p.close();c.drawPath(p,paint('#1a0a04'))
    if e.get('glow'): x,y,r=e['glow'];c.drawCircle(x*u,y*u,r*u,paint(e.get('gcol',AMB),.3,blur=r*.6*u))
    if e.get('band'): y=e['band'];c.drawRect(skia.Rect.MakeLTRB(0,(y-30)*u,W,(y+40)*u),paint('#f0a030',.55,blur=25*u));c.drawRect(skia.Rect.MakeLTRB(0,(y-3)*u,W,(y+3)*u),paint('#fff0c0',.9,blur=3*u))
    vignette(c,W,H,e.get('vig',.6))
def bubbles(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);R=random.Random(e.get('seed',3));col=e.get('col','#e8b040')
    for i in range(e.get('n',40)):
        x=R.uniform(0,1024);r=R.uniform(*e.get('rr',[6,26]));sp=R.uniform(8,25)*e.get('speed',1)
        y=(R.uniform(0,700)-t*sp)%700-60;x+=math.sin(t*.5+i)*6
        c.drawCircle(x*u,y*u,r*1.6*u,paint(col,a*.15,blur=r*.6*u))
        c.drawCircle(x*u,y*u,r*u,paint(col,a*.85,stroke=max(1.5,r*.18)*u))
        if R.random()<.4: c.drawCircle((x+r*.8)*u,(y+r*.6)*u,r*.45*u,paint(col,a*.8,stroke=1.2*u))
def dust(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);R=random.Random(e.get('seed',5))
    for i in range(e.get('n',80)):
        x=(R.uniform(0,1024)+t*R.uniform(-4,4))%1024;y=(R.uniform(0,576)-t*R.uniform(2,8))%576
        c.drawCircle(x*u,y*u,R.uniform(.6,1.8)*u,paint(e.get('col','#ffd080'),a*R.uniform(.2,.8)))
def bokeh(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);R=random.Random(e.get('seed',8));cols=e.get('cols',['#c04060','#e08030','#4060a0','#a03080','#d0a040','#40a080'])
    y0,y1=e.get('band',[0,576])
    for i in range(e.get('n',70)):
        x=R.uniform(-20,1044)+math.sin(t*.2+i)*5;y=R.uniform(y0,y1);r=R.uniform(10,38)
        c.drawCircle(x*u,y*u,r*u,paint(R.choice(cols),a*R.uniform(.12,.32)*e.get('k',1),blur=r*.15*u))
def worldmap(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx)
    from engine.geo import Proj,draw_map
    bx=e.get('box',[0,60,1024,470]);pr=Proj(e.get('bbox',[-170,-48,190,78]),*[v*u for v in bx])
    from engine.geo import load
    for name,ring in load(os.path.join(os.path.dirname(__file__),'..','..','assets','geo','countries_50m.geojson')):
        if ring[:,1].mean()<-58: continue
        X,Y=pr(ring[:,0],ring[:,1]);p=skia.Path();p.addPoly([skia.Point(float(x),float(y)) for x,y in zip(X,Y)],True)
        c.drawPath(p,paint(e.get('fill','#5a3a1e'),a*e.get('ma',.6)));c.drawPath(p,paint(e.get('stroke','#a0703a'),a*e.get('ma',.6),stroke=.7*u))
    for i,pl in enumerate(e.get('places',[])):
        lab,lon,lat=pl[:3];kk=a*clamp((t-e['t0']-.4-i*e.get('step',.4))/.4)
        if kk<=0: continue
        x,y=pr(lon,lat);x,y=float(x),float(y)
        glow_dot(c,x,y,2.5*u,GOLD,kk,halo=7)
        draw_text(c,lab,x+8*u,y-4*u,font('serif-bold',10*u),'#f4e8d0',kk,align='left')
        if len(pl)>3: draw_text(c,pl[3],x+8*u,y+9*u,font('sans',7*u),'#a89070',kk,align='left')
def craters(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx)
    for (x,y,rx,ry) in e.get('list',[[440,270,55,24],[560,285,48,20]]):
        R=skia.Rect.MakeLTRB((x-rx)*u,(y-ry)*u,(x+rx)*u,(y+ry)*u)
        c.drawOval(R,paint('#1a120c',a*.7));c.drawOval(R.makeOffset(0,2*u),paint('#8a7a68',a*.6,stroke=3*u,blur=1.5*u))
        c.drawOval(R,paint('#2a2018',a*.9,stroke=4*u))
        if e.get('glow'): c.drawOval(R,paint(GOLD,a*e['glow'],blur=10*u))
def relief(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);y=e.get('y',380)
    def fig(x,s,bend=0):
        cc='#2a2016';hl='#9a8a74'
        for col,off in((hl,1.5),(cc,0)):
            c.drawCircle((x+bend*6)*u,(y-95*s+off)*u,9*s*u,paint(col,a))
            line(c,(x+bend*6)*u,(y-85*s+off)*u,x*u,(y-40*s+off)*u,col,a,w=7*s*u)
            line(c,x*u,(y-40*s+off)*u,(x-10*s)*u,(y+off)*u,col,a,w=6*s*u);line(c,x*u,(y-40*s+off)*u,(x+10*s)*u,(y+off)*u,col,a,w=6*s*u)
            line(c,(x+bend*4)*u,(y-75*s+off)*u,(x+25*s)*u,(y-60*s+off)*u,col,a,w=5*s*u)
    for (x,s,b) in e.get('figs',[[230,1,1],[420,1,1]]): fig(x,s,b)
    for (x,w,h) in e.get('jars',[[330,40,50]]):
        c.drawOval(skia.Rect.MakeXYWH((x-w/2)*u,(y-h)*u,w*u,h*u),paint('#2a2016',a));c.drawOval(skia.Rect.MakeXYWH((x-w/2)*u,(y-h)*u,w*u,h*u),paint('#9a8a74',a,stroke=1.5*u))
    if e.get('pillar'): x=e['pillar'];c.drawRect(skia.Rect.MakeXYWH(x*u,(y-150)*u,22*u,170*u),paint('#5a4a3a',a));c.drawRect(skia.Rect.MakeXYWH(x*u,(y-150)*u,6*u,170*u),paint('#8a7a64',a))
def dial(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,r=e['x'],e['y'],e.get('r',30);col=e.get('col','#40c0a0')
    c.drawCircle(x*u,y*u,r*u,paint(col,a*.7,stroke=1.2*u))
    for i in range(36): an=i*math.pi/18+t*.3;line(c,(x+math.cos(an)*r)*u,(y+math.sin(an)*r)*u,(x+math.cos(an)*(r+4))*u,(y+math.sin(an)*(r+4))*u,col,a*.6,w=1*u)
    glow_dot(c,x*u,y*u,4*u,GOLD,a,halo=8)
def link(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x0,y0,x1,y1=e['pts'];p=ease_in_out_cubic(clamp((t-e['t0'])/e.get('dur',1)))
    line(c,x0*u,y0*u,(x0+(x1-x0)*p)*u,(y0+(y1-y0)*p)*u,GOLD,a,w=1.2*u,glow=4*u)
def vessel(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,s=e.get('x',512),e.get('y',330),e.get('s',1);k=e.get('kind','jar');fill=kfi(e.get('fill',.7),t)
    if e.get('beams',True):
        for dx in (-1,1):
            p=skia.Path();p.moveTo((x+dx*30*s)*u,0);p.lineTo((x+dx*130*s)*u,(y+70*s)*u);p.lineTo((x+dx*60*s)*u,(y+70*s)*u);p.close();c.drawPath(p,paint('#f0c070',a*.07,blur=10*u))
            line(c,(x+dx*120*s)*u,(y-200*s)*u,(x+dx*20*s)*u,(y-60*s)*u,'#f8e0a0',a*.7,w=1.2*u,glow=3*u)
    c.drawOval(skia.Rect.MakeLTRB((x-120*s)*u,(y+60*s)*u,(x+120*s)*u,(y+80*s)*u),paint('#f0b050',a*.25,blur=12*u))
    def liquid(path,top):
        c.save();c.clipPath(path,doAntiAlias=True)
        c.drawRect(skia.Rect.MakeLTRB(0,top*u,ctx.W,ctx.H),skia.Paint(AntiAlias=True,Shader=skia.GradientShader.MakeLinear([skia.Point(0,top*u),skia.Point(0,(y+70*s)*u)],[hexc('#fff0b0',a),hexc('#e8a030',a),hexc('#a05010',a)])))
        R=random.Random(1)
        for i in range(14): bx=x+R.uniform(-60,60)*s;by=(top+R.uniform(0,120)*s-t*15*s)%((y+70*s)-top)+top;c.drawCircle(bx*u,by*u,R.uniform(1,3)*s*u,paint('#fff8d0',a*.7))
        c.restore()
    p=skia.Path()
    if k=='jar':
        p.moveTo((x-40*s)*u,(y-80*s)*u);p.lineTo((x+40*s)*u,(y-80*s)*u);p.cubicTo((x+40*s)*u,(y-50*s)*u,(x+90*s)*u,(y-30*s)*u,(x+80*s)*u,(y+20*s)*u)
        p.cubicTo((x+70*s)*u,(y+70*s)*u,(x-70*s)*u,(y+70*s)*u,(x-80*s)*u,(y+20*s)*u);p.cubicTo((x-90*s)*u,(y-30*s)*u,(x-40*s)*u,(y-50*s)*u,(x-40*s)*u,(y-80*s)*u);p.close()
        liquid(p,y-80*s+150*s*(1-fill))
    elif k=='goblet':
        p.moveTo((x-55*s)*u,(y-110*s)*u);p.lineTo((x+55*s)*u,(y-110*s)*u);p.cubicTo((x+55*s)*u,(y-30*s)*u,(x+20*s)*u,(y-10*s)*u,(x+5*s)*u,(y-5*s)*u);p.lineTo((x-5*s)*u,(y-5*s)*u);p.cubicTo((x-20*s)*u,(y-10*s)*u,(x-55*s)*u,(y-30*s)*u,(x-55*s)*u,(y-110*s)*u);p.close()
        liquid(p,y-110*s+100*s*(1-fill))
        line(c,x*u,(y-5*s)*u,x*u,(y+60*s)*u,'#d8c8a0',a,w=2.5*s*u);c.drawOval(skia.Rect.MakeLTRB((x-35*s)*u,(y+56*s)*u,(x+35*s)*u,(y+66*s)*u),paint('#d8c8a0',a,stroke=1.5*u))
    elif k=='cup':
        p.moveTo((x-65*s)*u,(y-40*s)*u);p.lineTo((x+65*s)*u,(y-40*s)*u);p.lineTo((x+45*s)*u,(y+10*s)*u);p.lineTo((x-45*s)*u,(y+10*s)*u);p.close()
        liquid(p,y-40*s+50*s*(1-fill));line(c,x*u,(y+10*s)*u,x*u,(y+50*s)*u,'#8a5a30',a,w=8*s*u);c.drawOval(skia.Rect.MakeLTRB((x-45*s)*u,(y+45*s)*u,(x+45*s)*u,(y+60*s)*u),paint('#8a5a30',a))
    elif k=='tripod':
        p.moveTo((x-45*s)*u,(y-90*s)*u);p.lineTo((x+45*s)*u,(y-90*s)*u);p.lineTo((x+35*s)*u,(y-10*s)*u);p.lineTo((x-35*s)*u,(y-10*s)*u);p.close()
        liquid(p,y-90*s+80*s*(1-fill))
        for dx in (-30,0,30): line(c,(x+dx*s)*u,(y-10*s)*u,(x+dx*1.4*s)*u,(y+60*s)*u,'#c8a060',a,w=3*s*u)
        for dx in (-25,25): line(c,(x+dx*s)*u,(y-90*s)*u,(x+dx*s)*u,(y-115*s)*u,'#c8a060',a,w=2*s*u)
    elif k=='glass':
        p.addRect(skia.Rect.MakeLTRB((x-40*s)*u,(y-40*s)*u,(x+40*s)*u,(y+50*s)*u));liquid(p,y-40*s+90*s*(1-fill))
    c.drawPath(p,paint('#f8e8c0',a*.8,stroke=1.6*u))
    if k=='glass': c.drawPath(p,paint('#ffffff',a*.12))
def toast(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e.get('x',512),e.get('y',190);p=ease_out_cubic(clamp((t-e['t0'])/e.get('dur',.8)))
    for sg in (-1,1):
        c.save();c.translate((x+sg*(130-60*p)*e.get('s',1))*u,y*u);c.rotate(sg*12*p)
        vessel(ctx,dict(kind='goblet',x=0,y=0,s=.55*e.get('s',1)*1.8,fill=.6,beams=False,t0=e['t0'],t1=e['t1']),t,frame);c.restore()
    if p>=1: c.drawCircle(x*u,(y-50)*u,30*u,paint('#fff0c0',a*.4*max(0,1-(t-e['t0']-e.get('dur',.8))*2),blur=12*u))
def ruler(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);y=e.get('y',22);line(c,30*u,y*u,994*u,y*u,'#6a5a48',a,w=.8*u)
    labs=e.get('labels',[]);n=len(labs)
    for i,l in enumerate(labs):
        x=30+964*i/max(n-1,1);line(c,x*u,(y-3)*u,x*u,(y+3)*u,'#8a7a64',a,w=.8*u);draw_text(c,l,x*u,(y+13)*u,font('sans',6*u),'#8a7a64',a)
    if e.get('at') is not None: x=30+964*kfi(e['at'],t);glow_dot(c,x*u,y*u,2.5*u,GOLD,a,halo=5)
def icon3(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y=e['x'],e['y'];k=e.get('kind','sprout');aa=a*clamp((t-e['t0'])/.5)
    c.save();c.translate(x*u,y*u);c.scale(e.get('s',1),e.get('s',1));c.translate(-x*u,-y*u)
    if k=='sprout':
        line(c,x*u,(y+30)*u,x*u,(y-10)*u,'#c8a050',aa,w=2*u);p=skia.Path();p.moveTo(x*u,(y-10)*u);p.quadTo((x-25)*u,(y-30)*u,(x-30)*u,(y-10)*u);p.quadTo((x-15)*u,(y-5)*u,x*u,(y-10)*u);c.drawPath(p,paint('#e0b050',aa))
        c.drawOval(skia.Rect.MakeXYWH((x-8)*u,(y+26)*u,16*u,10*u),paint('#a07030',aa))
    elif k=='burst':
        R=random.Random(3)
        for i in range(40): an=R.uniform(0,6.28);d=R.uniform(10,45)*clamp((t-e['t0'])/1);line(c,x*u,y*u,(x+math.cos(an)*d)*u,(y+math.sin(an)*d)*u,'#f0e0b0',aa*.7,w=.8*u);c.drawCircle((x+math.cos(an)*d)*u,(y+math.sin(an)*d)*u,1.4*u,paint('#fff0c0',aa))
        for dx in (-8,0,8): c.drawOval(skia.Rect.MakeXYWH((x+dx-5)*u,(y+15)*u,10*u,7*u),paint('#e0c080',aa))
    elif k=='dots':
        for i in range(5): c.drawCircle((x-20+i*10)*u,y*u,2*u,paint('#e0c080',aa*(.5+.5*math.sin(t*3+i))))
    c.restore()
def table(ctx,e,t,frame):
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);W=ctx.W;y=e.get('y',470)
    c.drawRect(skia.Rect.MakeLTRB(0,y*u,W,ctx.H),skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0,y*u),skia.Point(0,ctx.H)],[hexc('#3a2210',a),hexc('#120a04',a)])))
    line(c,0,y*u,W,y*u,'#a06a30',a*.8,w=1*u)
    for x in range(0,1030,170): line(c,x*u,0,x*u,y*u*.6,'#0a0604',a*.8,w=6*u)
    line(c,0,y*.3*u,W,y*.3*u,'#0a0604',a*.8,w=6*u)
def text(ctx,e,t,frame):
    a=env(e,t,e.get('fi',.35),e.get('fo',.35))
    if a<=0: return
    c=ctx.c;u=U(ctx);s=e.get('size',16);f=font(e.get('font','serif-bold'),s*u);col=e.get('col','#f4ece0');hl=e.get('hl',GOLD)
    for li,ln in enumerate(e['text'].split('\n')):
        runs=[];b='';h=False
        for ch in ln:
            if ch in '[]': runs.append((b,hl if h else col)); b=''; h=(ch=='[')
            else: b+=ch
        runs.append((b,hl if h else col))
        draw_rich(c,[r for r in runs if r[0]],e.get('x',512)*u,(e.get('y',520)+li*s*1.35)*u,f,align=e.get('align','center'),a=a,glow=e.get('glow',0)*u)
def flash(ctx,e,t,frame):
    if e['t0']<=t<e['t0']+e.get('dur',.034): ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(e.get('col','#ffffff'),e.get('a',1)))
def beatflash(ctx,e,t,frame):
    beats=e.get('beats') or getattr(ctx,'beats',[])
    if not beats: return
    a=e.get('a',.35); col=e.get('col','#fff4dc'); win=e.get('window',.07)
    b=min(beats,key=lambda x:abs(x-t)); d=abs(t-b)
    if d>win: return
    k=(1-d/win)**1.5; ctx.c.drawRect(skia.Rect.MakeWH(ctx.W,ctx.H),paint(col,a*k))

EXTRA=dict(beatflash=beatflash,bg=bg,bubbles=bubbles,dust=dust,bokeh=bokeh,worldmap=worldmap,craters=craters,relief=relief,dial=dial,link=link,vessel=vessel,toast=toast,table=table,ruler=ruler,icon3=icon3,text=text,flash=flash)
def chapter(ctx,e,t,frame):
    a=env(e,t,.4,.4)
    if a<=0: return
    c=ctx.c;u=U(ctx);k=ease_out_cubic(prog(t,e['t0'],.5))
    draw_text(c,e.get('no',''),e.get('x',40)*u,40*u,font('serif-bold',16*u),GOLD,a*k,'left')
    draw_text(c,e.get('text',''),e.get('x',40)*u,58*u,font('serif',11*u),'#e8d8c0',a*k,'left')
def pour(ctx,e,t,frame):
    """liquid fill level animating 0→1 inside a vessel silhouette hint (ellipse)"""
    a=env(e,t)
    if a<=0: return
    c=ctx.c;u=U(ctx);x,y,w,h=e['x'],e['y'],e.get('w',40),e.get('h',60)
    k=ease_in_out_cubic(prog(t,e.get('fill_at',e['t0']),e.get('dur',1.5))); fill=lerp(e.get('from',0),e.get('to',1),k)
    c.drawOval(skia.Rect.MakeXYWH((x-w/2)*u,(y-h)*u,w*u,h*u),paint('#2a1a10',a*.5,stroke=1.5*u))
    c.save(); c.clipRect(skia.Rect.MakeXYWH((x-w/2)*u,(y-h*fill)*u,w*u,h*fill*u))
    c.drawOval(skia.Rect.MakeXYWH((x-w/2)*u,(y-h)*u,w*u,h*u),paint(e.get('col',GOLD),a*.75)); c.restore()
def spark(ctx,e,t,frame):
    a=env(e,t,.3,.3)
    if a<=0: return
    RICH.motes(ctx.c,ctx.W,ctx.H,t,n=e.get('n',50),color=e.get('color',GOLD),a=a*.5,seed=e.get('seed',3),speed=e.get('speed',1.4))
EXTRA.update(chapter=chapter,pour=pour,spark=spark)
def _render_sc(ctx,sc,t,frame):
    draw_elements(ctx,sc.get('elements',[]),t,frame,EXTRA)
def draw(ctx,t,frame,S):
    ctx.beats=S.get('beats',[])
    c=ctx.c; c.clear(skia.ColorBLACK)
    draw_elements(ctx,S.get('under',[]),t,frame,EXTRA)
    RICH.compose_scenes(ctx,S,t,frame,_render_sc,overlays_extra=EXTRA,clear=None,
                        vignette_s=.4,grain_a=.04,band_color='#ffb060',design_size=(1024,576))
    # NOTE: full-frame RICH.beat_punch + type=beatflash cause eye-pain strobe at ~112 BPM.
# Default beat_punch OFF; if enabled keep punch_a <= 0.05. Prefer local pulses (beatrings/motes/pulse).
    if S.get('beat_punch',False) and getattr(ctx,'beats',None): RICH.beat_punch(ctx.c,ctx.W,ctx.H,t,ctx.beats,a=S.get('punch_a',.05),color=S.get('punch_col','#ffb060'),window=.06)
