"""Shared visual-richness helpers for vibe templates (transitions, ambient motion, Ken Burns).
See skill/RICHNESS_STANDARD.md and dusk-map-chronicle v3.
"""
import math, random, skia
from engine.core import *

def motes(c, W, H, t, n=60, color='#f2c766', a=.4, seed=11, speed=1., blur_k=.6, design_w=1024., design_h=576.):
    """Floating dust / sparkles in design space mapped to canvas W×H."""
    u=W/design_w; r=random.Random(seed)
    for i in range(n):
        x=(r.uniform(0,design_w)+t*r.uniform(-6,10)*speed)%design_w
        y=(r.uniform(0,design_h)-t*r.uniform(3,12)*speed)%design_h
        s=r.uniform(.6,2.0)
        c.drawCircle(x*u,y*(H/design_h),s*u,paint(color,a*r.uniform(.15,.55)*(.6+.4*math.sin(t*2+i)),blur=s*blur_k*u))

def apply_ken_burns(c, W, H, t, t0, t1, zoom=1.04, pan=(0.,0.), at=None):
    """Slow push + optional pan. Call inside c.save()/restore(). Returns scale factor used."""
    dur=max(t1-t0,1e-3); k=ease_in_out_cubic(clamp((t-t0)/dur))
    z=1+(zoom-1)*k; cx,cy=(at or (W/2,H/2)); dx,dy=pan[0]*W*k, pan[1]*H*k
    c.translate(cx+dx,cy+dy); c.scale(z,z); c.translate(-cx,-cy)
    return z

def _tin_spec(nx):
    if not nx: return None
    tin=nx.get('tin') or ({'type':'fade','dur':nx.get('xin',nx.get('xfade',.8))} if (nx.get('xin') or nx.get('xfade')) else {'type':'fade','dur':.8})
    if isinstance(tin,str): tin={'type':tin}
    tin.setdefault('dur',.8); return tin

def compose_scenes(ctx, S, t, frame, render_scene, overlays_extra=None, clear='#000000',
                   vignette_s=.45, grain_a=.035, band_color='#ffd890', design_size=(1024,576)):
    """Render active scenes with crafted transitions (fade|zoom|wipe|iris|flash|slide).
    render_scene(ctx, sc, t, frame) draws one scene's bg+elements (no overlays).
    overlays_extra: EXTRA dict for S['overlays']; if None, caller draws overlays after.
    Scenes overlapping in time: first is outgoing, second is incoming with tin.
    """
    c=ctx.c; W,H=ctx.W,ctx.H; u=W/design_size[0]
    if clear is not None: c.clear(hexc(clear) if isinstance(clear,str) else clear)
    act=[sc for sc in S['scenes'] if sc['t0']-1e-6<=t<sc['t1']]
    if not act: return
    base=act[0]; nx=act[1] if len(act)>1 else None
    tin=_tin_spec(nx); typ=tin['type'] if tin else None
    k=ease_in_out_cubic(prog(t,nx['t0'],tin.get('dur',.8))) if nx else 0
    at=(tin or {}).get('at',[design_size[0]/2,design_size[1]/2])
    ax,ay=at[0]*u,at[1]*(H/design_size[1])
    c.save()
    if typ=='zoom': z=1+k*1.2; c.translate(ax,ay); c.scale(z,z); c.translate(-ax,-ay)
    if typ=='slide': c.translate(-k*W,0)
    # optional per-scene Ken Burns when sc.kb = {zoom,pan,at} or sc.zoom number
    kb=base.get('kb') or ({'zoom':base['zoom']} if isinstance(base.get('zoom'),(int,float)) else None)
    if kb and typ!='zoom':
        apply_ken_burns(c,W,H,t,base['t0'],base['t1'],kb.get('zoom',1.04),tuple(kb.get('pan',(0,0))), 
                        (kb['at'][0]*u,kb['at'][1]*(H/design_size[1])) if kb.get('at') else None)
    render_scene(ctx,base,t,frame); c.restore()
    if nx:
        if typ in ('fade','zoom','flash',None):
            alpha=k if typ!='flash' else float(k>.5)
            c.saveLayerAlpha(None,int(255*alpha))
            if typ=='zoom': z=.6+.4*k; c.translate(ax,ay); c.scale(z,z); c.translate(-ax,-ay)
            render_scene(ctx,nx,t,frame); c.restore()
            if typ=='flash': c.drawRect(skia.Rect.MakeWH(W,H),paint(tin.get('color','#fff4dc'),(1-abs(2*k-1))**1.5*.95))
        elif typ=='wipe':
            ex=lerp(-.25,1.25,k)*W; sk=tin.get('skew',.25)*H
            p=skia.Path(); p.moveTo(-10,0); p.lineTo(ex+sk,0); p.lineTo(ex-sk,H); p.lineTo(-10,H); p.close()
            c.save(); c.clipPath(p,doAntiAlias=True); render_scene(ctx,nx,t,frame); c.restore()
            band=skia.Path(); band.moveTo(ex+sk,0); band.lineTo(ex-sk,H)
            col=tin.get('color',band_color)
            c.drawPath(band,paint(col,.9*(1-abs(2*k-1)),stroke=6*u,blur=8*u)); c.drawPath(band,paint('#fff6e0',.9*(1-abs(2*k-1)),stroke=1.5*u))
        elif typ=='iris':
            R=k*math.hypot(W,H); p=skia.Path(); p.addCircle(ax,ay,R)
            c.save(); c.clipPath(p,doAntiAlias=True); render_scene(ctx,nx,t,frame); c.restore()
            c.drawCircle(ax,ay,R,paint(tin.get('color','#ffc860'),.8*(1-k),stroke=5*u,blur=6*u))
        elif typ=='slide':
            c.save(); c.translate((1-k)*W,0); render_scene(ctx,nx,t,frame); c.restore()
    if overlays_extra is not None:
        from engine.layers import draw_elements
        draw_elements(ctx,S.get('overlays',[]),t,frame,overlays_extra)
    if vignette_s: vignette(c,W,H,vignette_s)
    if grain_a: grain(c,W,H,frame,grain_a,10)
    fo=S.get('fade_out',0)
    if fo and t>S['duration']-fo: c.drawRect(skia.Rect.MakeWH(W,H),paint('#000000',prog(t,S['duration']-fo,fo)))
    fi=S.get('fade_in',0)
    if fi and t<fi: c.drawRect(skia.Rect.MakeWH(W,H),paint('#000000',1-prog(t,0,fi)))

# ---------- beat sync ----------
def load_beats(path):
    import json
    return json.load(open(path))

def snap(t, beats, tol=.18):
    if not beats: return t
    b=min(beats, key=lambda x: abs(x-t))
    return b if abs(b-t)<=tol else t

def beats_in(beats, t0, t1):
    return [b for b in beats if t0-1e-6 <= b < t1]

def nearest_beats(beats, times, tol=.18):
    return [snap(t, beats, tol) for t in times]

def beat_punch(c, W, H, t, beats, a=.35, color='#fff4dc', window=.07):
    """brief full-frame punch if t is near a beat"""
    if not beats: return
    b=min(beats, key=lambda x: abs(x-t))
    d=abs(t-b)
    if d>window: return
    k=(1-d/window)**1.5
    c.drawRect(skia.Rect.MakeWH(W,H), paint(color, a*k*.55))

def accent_ring(c, x, y, u, t, beats, color='#f2c766', base_r=8, span=28, window=.12):
    if not beats: return
    b=min(beats, key=lambda x: abs(x-t))
    d=abs(t-b)
    if d>window: return
    k=1-d/window
    r=base_r+span*k
    c.drawCircle(x*u,y*u,r*u,paint(color,k*.7,stroke=2*u))
    c.drawCircle(x*u,y*u,(r+8)*u,paint(color,k*.25,blur=5*u))
