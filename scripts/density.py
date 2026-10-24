"""density.py video.mp4 [label] -> per-second frame-diff stats (motion/visual-change density); compare to reference"""
import sys,subprocess,numpy as np
v=sys.argv[1]; W,H=320,180
raw=subprocess.run(['ffmpeg','-v','error','-i',v,'-vf',f'fps=1,scale={W}:{H},format=gray','-f','rawvideo','-'],capture_output=True).stdout
f=np.frombuffer(raw,np.uint8).reshape(-1,H,W).astype(float); d=np.abs(np.diff(f,axis=0)).mean((1,2))
run=mx=0
for x in d: run=run+1 if x<.6 else 0; mx=max(mx,run)
print(f"{sys.argv[-1]}: n={len(d)} median={np.median(d):.2f} p90={np.percentile(d,90):.2f} big(>8)/10s={(d>8).sum()/len(d)*10:.2f} mid(>4)/10s={(d>4).sum()/len(d)*10:.2f} longest_static={mx}s mean_luma={f.mean():.1f}")
