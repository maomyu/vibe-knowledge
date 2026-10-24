"""Code-drawn maps from real geodata (GeoJSON; default: assets/geo/china_provinces.json, DataV.GeoAtlas, 阿里云 public
boundary data — check its terms before commercial use). Equirectangular w/ cos(lat0) correction; ink/paper or dark/neon styles; animated route
(draw-on polyline with moving head), city dots + labels, province highlight."""
import json, math, os, skia, numpy as np
from functools import lru_cache
from .core import paint, font, draw_text, hexc, prog, ease_in_out_cubic
GEO=os.path.join(os.path.dirname(__file__),'..','..','assets','geo','china_provinces.json')
CITIES={'汴京':(114.31,34.80),'黄州':(114.87,30.45),'惠州':(114.42,23.11),'儋州':(109.58,19.52),'眉山':(103.85,30.08),'杭州':(120.16,30.27),'密州':(119.41,35.99),'徐州':(117.28,34.20),'常州':(119.97,31.81)}
@lru_cache(4)
def load(path=GEO):
    d=json.load(open(path)); polys=[]
    for f in d['features']:
        g=f['geometry']; name=f['properties'].get('name','')
        if not g: continue
        cs=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
        for poly in cs:
            for ring in poly[:1]: polys.append((name,np.array(ring,float)))
    return polys
class Proj:
    def __init__(s,bbox,x,y,w,h):   # bbox lon0,lat0,lon1,lat1 -> screen rect (keeps aspect)
        s.l0,s.b0,s.l1,s.b1=bbox; k=math.cos(math.radians((s.b0+s.b1)/2))
        sx=w/((s.l1-s.l0)*k); sy=h/(s.b1-s.b0); s.s=min(sx,sy); s.k=k
        s.cx=x+w/2; s.cy=y+h/2; s.ml=(s.l0+s.l1)/2; s.mb=(s.b0+s.b1)/2
    def __call__(s,lon,lat): return s.cx+(np.asarray(lon)-s.ml)*s.k*s.s, s.cy-(np.asarray(lat)-s.mb)*s.s
def draw_map(c,proj,a=1.,fill='#e9e2d4',stroke='#8a8070',sw=.8,highlight=None,hl_fill='#e8582f',path=GEO):
    for name,ring in load(path):
        X,Y=proj(ring[:,0],ring[:,1]); p=skia.Path(); p.addPoly([skia.Point(float(x),float(y)) for x,y in zip(X,Y)],True)
        f=hl_fill if highlight and name.startswith(tuple(highlight)) else fill
        c.drawPath(p,paint(f,a)); c.drawPath(p,paint(stroke,a,stroke=sw))
def route(c,proj,names,t,t0,dur,col='#e8582f',w=2.,a=1.,label_font='serif-vf',size=14,label_col='#2a2622'):
    pts=np.array([proj(*CITIES[n]) for n in names],float); seg=np.hypot(*np.diff(pts,axis=0).T); L=seg.sum(); k=ease_in_out_cubic(prog(t,t0,dur))*L
    acc=0; p=skia.Path(); p.moveTo(*pts[0]); head=pts[0]
    for i,s in enumerate(seg):
        if acc+s<=k: p.lineTo(*pts[i+1]); head=pts[i+1]
        else: r=(k-acc)/s if s else 0; head=pts[i]+(pts[i+1]-pts[i])*r; p.lineTo(*head); break
        acc+=s
    c.drawPath(p,paint(col,a,stroke=w)); c.drawCircle(*head,w*2.2,paint(col,a))
    acc=0
    for i,n in enumerate(names):
        if i and sum(seg[:i])>k+1e-6: break
        x,y=pts[i]; c.drawCircle(x,y,w*1.6,paint('#ffffff',a)); c.drawCircle(x,y,w*1.6,paint(col,a,stroke=w*.8))
        draw_text(c,n,x+size*.8,y+size*.35,font(label_font,size,700),label_col,a,'left')
