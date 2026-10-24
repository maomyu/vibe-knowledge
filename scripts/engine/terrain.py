"""Real-DEM shaded relief for map styles (dusk-map-chronicle, ...).
Data: AWS Terrain Tiles (terrarium, z7) mosaic assets/geo/dem_*.npy — open data (SRTM/GMTED/ETOPO1; attribution required).
relief(bbox,W,H) returns an RGB uint8 array in the same equirectangular(cos lat0) projection as engine.geo.Proj."""
import numpy as np, json, math, os
from functools import lru_cache
GEOD=os.path.join(os.path.dirname(__file__),'..','..','assets','geo')
@lru_cache(2)
def _mosaic(name='dem_nw_china_z7'):
    M=np.load(os.path.join(GEOD,name+'.npy')).astype(np.float32); meta=json.load(open(os.path.join(GEOD,name+'.json')))
    M=np.maximum(M,0)
    # hillshade (light from NW, 45deg); pixel ~ 1.0 km at z7/36N
    gy,gx=np.gradient(M,156543.*0.81/2**meta["z"])
    ex=2.2; slope=np.arctan(ex*np.hypot(gx,gy)); asp=np.arctan2(-gx,gy)
    az,alt=math.radians(315),math.radians(40)
    hs=np.sin(alt)*np.cos(slope)+np.cos(alt)*np.sin(slope)*np.cos(az-asp-math.pi/2)
    hs=np.clip(hs,0,1)
    return M,hs.astype(np.float32),meta
def lonlat_to_px(lon,lat,meta):
    n=2**meta['z']*256; x=(np.asarray(lon)+180)/360*n-meta['x0']*256
    r=np.radians(np.asarray(lat)); y=(1-np.log(np.tan(r)+1/np.cos(r))/math.pi)/2*n-meta['y0']*256
    return x,y
def relief(proj,W,H,name='dem_nw_china_z7',base=(30,24,17),lift=(74,64,50),dark=(10,8,6),contrast=1.0,step=1):
    M,hs,meta=_mosaic(name)
    xs=np.arange(0,W,step)+.5; ys=np.arange(0,H,step)+.5
    lon=proj.ml+(xs-proj.cx)/(proj.k*proj.s); lat=proj.mb-(ys-proj.cy)/proj.s
    px,_=lonlat_to_px(lon,np.full_like(lon,proj.mb),meta); _,py=lonlat_to_px(np.full_like(lat,proj.ml),lat,meta)
    PX,PY=np.meshgrid(px,py)
    from scipy.ndimage import map_coordinates
    s=map_coordinates(hs,[PY,PX],order=1,mode='nearest'); e=map_coordinates(M,[PY,PX],order=1,mode='nearest')
    s=np.clip((s-.55)*contrast+.55,0,1)
    k=(s-.55)/.45   # -1.2..1
    b=np.array(base,np.float32); L=np.array(lift,np.float32); D=np.array(dark,np.float32)
    rgb=np.where(k[...,None]>0, b+(L-b)*k[...,None], b+(b-D)*k[...,None])
    rgb*= (0.85+0.15*np.clip(e/3000,0,1))[...,None]   # high plateau slightly brighter
    if step>1: rgb=np.repeat(np.repeat(rgb,step,0),step,1)[:H,:W]
    return np.clip(rgb,0,255).astype(np.uint8)

# ---------------- generic (any region): auto-fetch + cache terrarium tiles ----------------
TILE_DIR=os.path.join(GEOD,'tiles')
def _tx(lon,z): return int((lon+180)/360*2**z)
def _ty(lat,z): r=math.radians(lat); return int((1-math.log(math.tan(r)+1/math.cos(r))/math.pi)/2*2**z)
def zoom_for(ppd): return int(min(9,max(3,round(math.log2(max(ppd,1)*360/256*1.2)))))
def ensure_tiles(bbox,z):
    """download (once) AWS Terrain Tiles covering bbox=(lon0,lat0,lon1,lat1) at zoom z; returns tile index range"""
    import subprocess
    os.makedirs(TILE_DIR,exist_ok=True)
    x0,x1=_tx(bbox[0],z),_tx(bbox[2],z); y0,y1=_ty(min(bbox[3],84),z),_ty(max(bbox[1],-84),z)
    for x in range(x0,x1+1):
        for y in range(y0,y1+1):
            f=os.path.join(TILE_DIR,f'{z}_{x}_{y}.png')
            if not os.path.exists(f):
                subprocess.run(['curl','-sS','-m','30','-o',f,f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x%(2**z)}/{y}.png'],check=False)
    return x0,x1,y0,y1
@lru_cache(6)
def _region(bbox,z):
    from PIL import Image
    x0,x1,y0,y1=ensure_tiles(bbox,z)
    M=np.zeros(((y1-y0+1)*256,(x1-x0+1)*256),np.float32)
    for x in range(x0,x1+1):
        for y in range(y0,y1+1):
            try: a=np.array(Image.open(os.path.join(TILE_DIR,f'{z}_{x}_{y}.png')).convert('RGB')).astype(np.float32)
            except Exception: continue
            M[(y-y0)*256:(y-y0+1)*256,(x-x0)*256:(x-x0+1)*256]=a[...,0]*256+a[...,1]+a[...,2]/256-32768
    M=np.maximum(M,0); lat=(bbox[1]+bbox[3])/2
    gy,gx=np.gradient(M,156543.*math.cos(math.radians(lat))/2**z)
    slope=np.arctan(2.2*np.hypot(gx,gy)); asp=np.arctan2(-gx,gy); az,alt=math.radians(315),math.radians(40)
    hs=np.clip(np.sin(alt)*np.cos(slope)+np.cos(alt)*np.sin(slope)*np.cos(az-asp-math.pi/2),0,1).astype(np.float32)
    return M,hs,dict(z=z,x0=x0,y0=y0)
def relief_auto(proj,W,H,ppd,**kw):
    """shaded relief for any proj (engine.geo.Proj); tiles auto-fetched for its bbox at a zoom matched to ppd"""
    z=zoom_for(ppd); pad=.5
    bbox=(round(proj.l0-pad,1),round(proj.b0-pad,1),round(proj.l1+pad,1),round(proj.b1+pad,1))
    M,hs,meta=_region(bbox,z)
    return _shade(proj,W,H,M,hs,meta,**kw)
def _shade(proj,W,H,M,hs,meta,base=(30,24,17),lift=(74,64,50),dark=(10,8,6),contrast=1.0,sea=(13,12,12)):
    from scipy.ndimage import map_coordinates
    xs=np.arange(W)+.5; ys=np.arange(H)+.5
    lon=proj.ml+(xs-proj.cx)/(proj.k*proj.s); lat=proj.mb-(ys-proj.cy)/proj.s
    px,_=lonlat_to_px(lon,np.full_like(lon,proj.mb),meta); _,py=lonlat_to_px(np.full_like(lat,proj.ml),lat,meta)
    PX,PY=np.meshgrid(px,py)
    s=map_coordinates(hs,[PY,PX],order=1,mode='nearest'); e=map_coordinates(M,[PY,PX],order=1,mode='nearest')
    s=np.clip((s-.55)*contrast+.55,0,1); k=(s-.55)/.45
    b=np.array(base,np.float32); L=np.array(lift,np.float32); D=np.array(dark,np.float32)
    rgb=np.where(k[...,None]>0,b+(L-b)*k[...,None],b+(b-D)*k[...,None])*(0.85+0.15*np.clip(e/3000,0,1))[...,None]
    rgb=np.where((e<=0.5)[...,None],np.array(sea,np.float32),rgb)
    return np.clip(rgb,0,255).astype(np.uint8)
