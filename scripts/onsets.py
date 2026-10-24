#!/usr/bin/env python3
"""onsets.py video y0 y1 [thr] : 10fps bright-pixel count in a horizontal band (normalized coords) -> text onset/offset events"""
import sys,subprocess,numpy as np,json
v=sys.argv[1]; y0,y1=float(sys.argv[2]),float(sys.argv[3]); thr=int(sys.argv[4]) if len(sys.argv)>4 else 200
w,h=320,180
b=subprocess.run(['ffmpeg','-v','error','-i',v,'-vf',f'fps=10,scale={w}:{h}','-f','rawvideo','-pix_fmt','gray','-'],capture_output=True).stdout
A=np.frombuffer(b,np.uint8).reshape(-1,h,w)[:,int(y0*h):int(y1*h),int(.15*w):int(.85*w)]
c=(A>thr).sum((1,2)).astype(float)
ev=[];on=False
for i,x in enumerate(c):
    if not on and x>8: on=True; st=i
    elif on and x<=3: on=False; ev.append((st/10,i/10))
# also: big drops (new sentence replaces old) — detect sharp decrease then rise
print(json.dumps(ev))
