#!/usr/bin/env python3
"""cuts.py ref.mp4 rem.mp4 : detect hard cuts (30fps, gray 128px mean abs diff) in both and pair them"""
import sys,subprocess,numpy as np
def F(p):
    b=subprocess.run(['ffmpeg','-v','error','-i',p,'-vf','fps=30,scale=128:72','-f','rawvideo','-pix_fmt','gray','-'],capture_output=True).stdout
    return np.frombuffer(b,np.uint8).reshape(-1,72,128).astype(np.float32)
def cuts(A,th=28):
    d=np.abs(np.diff(A,axis=0)).mean((1,2)); return [i+1 for i in range(len(d)) if d[i]>th and d[i]>2.5*np.median(d[max(0,i-5):i+6])]
def merge(cs):
    o=[]
    for c in cs:
        if o and c-o[-1]<=2: continue
        o.append(c)
    return o
a,b=F(sys.argv[1]),F(sys.argv[2]); ca,cb=merge(cuts(a)),merge(cuts(b))
print('ref cuts',len(ca),'rem cuts',len(cb))
off=[]
for c in ca:
    m=min(cb,key=lambda x:abs(x-c)) if cb else None
    off.append((c,m,None if m is None else m-c))
    print(f'{c/30:7.2f}s f{c:5d}  rem f{m}  Δ{m-c:+d}f' if m is not None and abs(m-c)<30 else f'{c/30:7.2f}s f{c:5d}  MISSING')
ok=sum(1 for c,m,d in off if d is not None and abs(d)<=1); print(f'within ±1f: {ok}/{len(ca)}')
