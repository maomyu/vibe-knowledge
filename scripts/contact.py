#!/usr/bin/env python3
"""contact.py video out_prefix [step=2] [cols=6] : contact sheets (timestamped thumbnails every `step` s), 36 per sheet"""
import sys,subprocess,os
from PIL import Image,ImageDraw
v,out=sys.argv[1],sys.argv[2]; step=float(sys.argv[3]) if len(sys.argv)>3 else 2; cols=int(sys.argv[4]) if len(sys.argv)>4 else 6
dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',v],capture_output=True,text=True).stdout)
w,h=map(int,subprocess.run(['ffprobe','-v','error','-select_streams','v','-show_entries','stream=width,height','-of','csv=p=0',v],capture_output=True,text=True).stdout.split(','))
tw=300 if w>=h else 170; th=int(tw*h/w)
raw=subprocess.run(['ffmpeg','-v','error','-i',v,'-vf',f'fps=1/{step},scale={tw}:{th}','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
n=len(raw)//(tw*th*3); per=cols*6
for s in range(0,n,per):
    W=Image.new('RGB',(cols*tw,((min(per,n-s)+cols-1)//cols)*th))
    for i in range(s,min(n,s+per)):
        im=Image.frombytes('RGB',(tw,th),raw[i*tw*th*3:(i+1)*tw*th*3]); d=ImageDraw.Draw(im); d.text((3,2),f'{i*step:.0f}s',fill=(255,255,0))
        W.paste(im,(((i-s)%cols)*tw,((i-s)//cols)*th))
    W.save(f'{out}_{s//per:02d}.jpg',quality=85); print(f'{out}_{s//per:02d}.jpg')
