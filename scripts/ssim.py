#!/usr/bin/env python3
"""ssim.py ref.mp4 rem.mp4 out.json [--fps 2] : per-frame SSIM/PSNR on aligned timeline (gray, 256w), plot png, worst segments"""
import sys,json,subprocess,numpy as np,cv2,argparse
def frames(p,fps,w=256,h=144,ss=0):
    cmd=['ffmpeg','-v','error','-ss',str(ss),'-i',p,'-vf',f'fps={fps},scale={w}:{h}','-f','rawvideo','-pix_fmt','gray','-']
    b=subprocess.run(cmd,capture_output=True).stdout; return np.frombuffer(b,np.uint8).reshape(-1,h,w)
def ssim(a,b):
    a=a.astype(np.float64);b=b.astype(np.float64);C1,C2=6.5025,58.5225
    g=lambda x:cv2.GaussianBlur(x,(11,11),1.5)
    ma,mb=g(a),g(b);va=g(a*a)-ma*ma;vb=g(b*b)-mb*mb;cab=g(a*b)-ma*mb
    return float((((2*ma*mb+C1)*(2*cab+C2))/((ma*ma+mb*mb+C1)*(va+vb+C2))).mean())
ap=argparse.ArgumentParser();ap.add_argument('ref');ap.add_argument('rem');ap.add_argument('out');ap.add_argument('--fps',type=float,default=2)
a=ap.parse_args();A=frames(a.ref,a.fps);B=frames(a.rem,a.fps);n=min(len(A),len(B))
S=[ssim(A[i],B[i]) for i in range(n)]
C=frames(a.ref,a.fps,ss=0.1); nc=min(n,len(C))
CEIL=[ssim(A[i],C[i]) for i in range(nc)]   # ref vs itself +0.1s (3 frames): stochastic-texture ceiling
NORM=[min(1.0,S[i]/max(.05,CEIL[i])) for i in range(nc)]
P=[float(10*np.log10(255**2/max(1e-9,((A[i].astype(float)-B[i])**2).mean()))) for i in range(n)]
t=[i/a.fps for i in range(n)]
# worst 5s windows
w=int(5*a.fps);win=sorted([(float(np.mean(NORM[i:i+w])),i/a.fps) for i in range(0,nc-w+1,w)])[:8]
R=dict(mean_ssim=float(np.mean(S)),mean_ceiling=float(np.mean(CEIL)),mean_norm=float(np.mean(NORM)),norm=NORM,ceiling=CEIL,mean_psnr=float(np.mean(P)),worst_windows=[dict(t0=t0,ssim=s) for s,t0 in win],t=t,ssim=S,psnr=P)
json.dump(R,open(a.out,'w'))
try:
    import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
    f,ax=plt.subplots(figsize=(14,3));ax.plot(t,S,label='ssim');ax.plot(t[:nc],CEIL,label='ref self +0.1s',alpha=.6);ax.legend();ax.set_ylim(0,1);ax.set_title(f'SSIM mean {R["mean_ssim"]:.3f}');ax.grid(1);f.savefig(a.out.replace('.json','.png'),dpi=80,bbox_inches='tight')
except Exception as e: print('noplot',e)
print(json.dumps({k:R[k] for k in['mean_ssim','mean_ceiling','mean_norm','mean_psnr','worst_windows']}))
