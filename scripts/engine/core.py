"""Vibe knowledge video engine core: skia-python 2D renderer -> raw frames -> ffmpeg.
Every template is a pure function draw(ctx, t) so frames render independently (parallel-safe)."""
import skia, math, os, random, numpy as np
from functools import lru_cache
HERE=os.path.dirname(os.path.abspath(__file__))
FONTDIR=os.path.normpath(os.path.join(HERE,'..','..','assets','fonts'))
SYS={'serif':'/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc','serif-bold':'/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc',
     'sans':'/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','sans-bold':'/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
     'mono':'/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf','mono-bold':'/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'}
VF={'serif-vf':'NotoSerifSC-VF.ttf','garamond':'EBGaramond-VF.ttf','garamond-italic':'EBGaramond-Italic-VF.ttf',
    'brush':'MaShanZheng-Regular.ttf','brush2':'ZhiMangXing-Regular.ttf','grass':'LiuJianMaoCao-Regular.ttf'}

@lru_cache(None)
def typeface(name='serif', weight=None):
    if name in SYS:
        tf=skia.Typeface.MakeFromFile(SYS[name], 2)  # ttc index 2 = SC
    else:
        tf=skia.Typeface.MakeFromFile(os.path.join(FONTDIR,VF[name]))
        if weight is not None:
            tag=skia.FourByteTag.Make('w','g','h','t') if hasattr(skia,'FourByteTag') else 0x77676874
            coord=skia.FontArguments.VariationPosition.Coordinate(0x77676874, float(weight))
            arr=skia.FontArguments.VariationPosition.Coordinates([coord])
            pos=skia.FontArguments.VariationPosition(arr)
            args=skia.FontArguments(); args.setVariationDesignPosition(pos)
            tf=tf.makeClone(args)
    return tf

@lru_cache(4096)
def font(name='serif', size=40, weight=None):
    f=skia.Font(typeface(name,weight), size); f.setSubpixel(True); f.setEdging(skia.Font.Edging.kAntiAlias); return f

def hexc(h, a=1.0):
    h=h.lstrip('#'); r,g,b=int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    return skia.Color(r,g,b,int(max(0,min(1,a))*255))

# ---------- easing ----------
def clamp(x,a=0.,b=1.): return a if x<a else b if x>b else x
def prog(t,t0,dur): return clamp((t-t0)/dur) if dur>0 else float(t>=t0)
def ease_out_cubic(x): return 1-(1-x)**3
def ease_in_out_cubic(x): return 4*x*x*x if x<.5 else 1-(-2*x+2)**3/2
def ease_out_back(x,s=1.70158): x-=1; return 1+(s+1)*x**3+s*x**2
def ease_out_expo(x): return 1 if x>=1 else 1-2**(-10*x)
EASE={'linear':lambda x:x,'out':ease_out_cubic,'inout':ease_in_out_cubic,'back':ease_out_back,'expo':ease_out_expo}
def fade_env(t,t0,t1,fi=.4,fo=.4):
    """alpha envelope for an element visible [t0,t1]"""
    if t<t0 or t>t1: return 0.
    a=1.
    if fi>0: a=min(a,ease_out_cubic(prog(t,t0,fi)))
    if fo>0: a=min(a,1-prog(t,t1-fo,fo))
    return a
def lerp(a,b,x): return a+(b-a)*x

class Ctx:
    def __init__(self,W,H,fps):
        self.W,self.H,self.fps=W,H,fps
        self.surface=skia.Surface(W,H); self.c=self.surface.getCanvas()
        self.cache={}
    def image(self):
        return self.surface.makeImageSnapshot()
    def rgba(self):
        return self.surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes()

# ---------- primitives ----------
def paint(color, a=1., stroke=None, blur=0, aa=True, blend=None, shader=None):
    p=skia.Paint(AntiAlias=aa)
    if isinstance(color,str): color=hexc(color,a)
    p.setColor(color)
    if stroke: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend: p.setBlendMode(blend)
    if shader: p.setShader(shader)
    return p

def text_width(s,f):
    return f.measureText(s)

def draw_text(c,s,x,y,f,color='#ffffff',a=1.,align='center',glow=0,glow_color=None,glow_a=.6,stroke=None,spacing=0):
    """x,y: anchor; y is the baseline. align: left/center/right. spacing = extra px between chars"""
    if a<=0.003 or not s: return 0
    w=text_width(s,f)+spacing*max(0,len(s)-1)
    x0= x-w/2 if align=='center' else x-w if align=='right' else x
    def emit(p):
        if spacing==0:
            c.drawString(s,x0,y,f,p)
        else:
            xx=x0
            for ch in s:
                c.drawString(ch,xx,y,f,p); xx+=f.measureText(ch)+spacing
    if glow:
        emit(paint(glow_color or color,a*glow_a,blur=glow))
    if stroke: emit(paint(stroke[0],a,stroke=stroke[1]))
    emit(paint(color,a))
    return w

def draw_rich(c,runs,x,y,f,align='center',a=1.,spacing=0,glow=0):
    """runs: list of (text,color). returns width"""
    tot=sum(text_width(s,f) for s,_ in runs)+spacing*max(0,sum(len(s) for s,_ in runs)-1)
    xx= x-tot/2 if align=='center' else x-tot if align=='right' else x
    for s,col in runs:
        w=draw_text(c,s,xx,y,f,col,a,align='left',spacing=spacing,glow=glow); xx+=w+spacing
    return tot

def rrect(c,x,y,w,h,r,fill=None,stroke=None,a=1.,sw=1.5,blur=0):
    rr=skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x,y,w,h),r,r)
    if fill: c.drawRRect(rr,paint(fill,a,blur=blur))
    if stroke: c.drawRRect(rr,paint(stroke,a,stroke=sw))

def glow_dot(c,x,y,r,color,a=1.,halo=6.):
    c.drawCircle(x,y,r*halo,paint(color,a*.18,blur=r*halo*.6))
    c.drawCircle(x,y,r*2.2,paint(color,a*.5,blur=r*1.5))
    c.drawCircle(x,y,r,paint('#ffffff',a))

def line(c,x0,y0,x1,y1,color,a=1.,w=2,glow=0,cap=True):
    p=paint(color,a,stroke=w)
    if cap: p.setStrokeCap(skia.Paint.kRound_Cap)
    if glow:
        g=paint(color,a*.6,stroke=w*3,blur=glow); c.drawLine(x0,y0,x1,y1,g)
    c.drawLine(x0,y0,x1,y1,p)

def vignette(c,W,H,strength=.55,color=(0,0,0)):
    sh=skia.GradientShader.MakeRadial((W/2,H/2),max(W,H)*.72,[skia.Color(*color,0),skia.Color(*color,int(255*strength))],[0.45,1.0])
    p=skia.Paint(); p.setShader(sh); c.drawRect(skia.Rect.MakeWH(W,H),p)

def linear_grad(c,rect,p0,p1,colors,pos=None):
    sh=skia.GradientShader.MakeLinear([p0,p1],colors,pos); p=skia.Paint(); p.setShader(sh); c.drawRect(rect,p)

@lru_cache(64)
def grain_image(W,H,seed=0,amp=18):
    rng=np.random.default_rng(seed)
    n=rng.normal(0,amp,(H,W)).clip(-127,127).astype(np.int16)+128
    arr=np.dstack([n,n,n,np.full((H,W),255)]).astype(np.uint8)
    return skia.Image.fromarray(arr,colorType=skia.kRGBA_8888_ColorType)

def grain(c,W,H,frame,a=.06,amp=18):
    img=grain_image(W,H,frame%8,amp)
    p=skia.Paint(); p.setAlphaf(a); p.setBlendMode(skia.BlendMode.kOverlay)
    c.drawImage(img,0,0,skia.SamplingOptions(),p)

def blurred_layer(c,fn,sigma):
    """draw fn() into a layer that gets gaussian-blurred (for bokeh / soft glows)"""
    p=skia.Paint(); p.setImageFilter(skia.ImageFilters.Blur(sigma,sigma))
    c.saveLayer(None,p); fn(); c.restore()

@lru_cache(64)
def load_image(path):
    return skia.Image.open(path)

def draw_image_cover(c,path,W,H,a=1.,scale=1.,cx=.5,cy=.5,gray=False):
    img=load_image(path); iw,ih=img.width(),img.height()
    s=max(W/iw,H/ih)*scale; w,h=iw*s,ih*s
    p=skia.Paint(); p.setAlphaf(a)
    if gray:
        m=[.299,.587,.114,0,0]*3+[0,0,0,1,0]; p.setColorFilter(skia.ColorFilters.Matrix(m))
    c.drawImageRect(img,skia.Rect.MakeXYWH(W*cx-w/2,H*cy-h/2,w,h),skia.SamplingOptions(skia.FilterMode.kLinear),p)

def rng_for(*key):
    return random.Random(hash(key)&0xffffffff)
