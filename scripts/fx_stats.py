#!/usr/bin/env python3
"""fx_stats.py video t0 t1 [--roi x0,y0,x1,y1 (0-1)] : statistics of random particle effects (rain/snow/bokeh/sparks)
-> count per frame, mean area px (at 1024w), mean brightness above local bg, dominant motion (dx,dy px/s) via phase correlation of the
high-pass layer. Compare reference vs remake windows: match feel, not pixels."""
import sys,subprocess,numpy as np,cv2,json,argparse
ap=argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('t0',type=float); ap.add_argument('t1',type=float)
ap.add_argument('--roi',default='0,0,1,1'); ap.add_argument('--thr',type=float,default=18); ap.add_argument('--fps',type=float,default=15)
a=ap.parse_args(); W,H=1024,576
b=subprocess.run(['ffmpeg','-v','error','-ss',str(a.t0),'-t',str(a.t1-a.t0),'-i',a.video,'-vf',f'fps={a.fps},scale={W}:{H}','-f','rawvideo','-pix_fmt','gray','-'],capture_output=True).stdout
F=np.frombuffer(b,np.uint8).reshape(-1,H,W).astype(np.float32)
x0,y0,x1,y1=[float(v) for v in a.roi.split(',')]; F=F[:,int(y0*H):int(y1*H),int(x0*W):int(x1*W)]
cnt=[];area=[];br=[];mot=[];prev=None
BG=np.median(F,axis=0)  # static layer (trees, text) removed: only moving particles remain
for f in F:
    hp=f-BG; m=(hp>a.thr).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(m,8); st=st[1:]; st=st[st[:,4]>=2]
    cnt.append(len(st)); area.append(float(st[:,4].mean()) if len(st) else 0); br.append(float(hp[m>0].mean()) if m.any() else 0)
    if prev is not None:
        (dx,dy),r=cv2.phaseCorrelate(prev,np.clip(hp,0,None)); mot.append((dx*a.fps,dy*a.fps,r))
    prev=np.clip(hp,0,None)
mv=np.array([m for m in mot if m[2]>.05]) if mot else np.zeros((0,3))
R=dict(count=float(np.mean(cnt)),area=float(np.mean(area)),bright=float(np.mean(br)),
       speed_px_s=(float(np.median(mv[:,0])),float(np.median(mv[:,1]))) if len(mv) else None,frames=len(F))
print(json.dumps(R))
