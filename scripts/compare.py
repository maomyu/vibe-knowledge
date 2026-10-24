#!/usr/bin/env python3
"""compare.py ref.mp4 remake.mp4 outdir [--times 1,2,3] [--excerpt s0,s1]
 -> compare.mp4 (full, ref|remake hstack, ref audio L / remake audio? we keep remake audio), compare_excerpt.mp4, compare.jpg contact sheet (rows: ref over remake)."""
import sys,subprocess,os,argparse
from PIL import Image,ImageDraw
ap=argparse.ArgumentParser(); ap.add_argument('ref'); ap.add_argument('rem'); ap.add_argument('out')
ap.add_argument('--times',default=None); ap.add_argument('--excerpt',default=None); ap.add_argument('--h',type=int,default=540); ap.add_argument('--no-video',action='store_true')
a=ap.parse_args(); os.makedirs(a.out,exist_ok=True)
def dur(p): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p]))
D=min(dur(a.ref),dur(a.rem)); h=a.h
vf=f"[0:v]scale=-2:{h},setsar=1,drawtext=text='ORIGINAL':x=10:y=10:fontcolor=lime:fontsize=18[a];[1:v]scale=-2:{h},setsar=1,drawtext=text='REMAKE':x=10:y=10:fontcolor=yellow:fontsize=18[b];[a][b]hstack=inputs=2[v]"
def make(out,ss=0,t=None):
    cmd=['ffmpeg','-loglevel','error','-y','-ss',str(ss)]+(['-t',str(t)] if t else [])+['-i',a.ref,'-ss',str(ss)]+(['-t',str(t)] if t else [])+['-i',a.rem,
        '-filter_complex',vf+';[1:a]volume=1[ar]','-map','[v]','-map','[ar]','-c:v','libx264','-preset','veryfast','-crf','22','-c:a','aac','-shortest',out]
    subprocess.run(cmd,check=True)
if not a.no_video:
    make(os.path.join(a.out,'compare.mp4'),0,None)
    if a.excerpt:
        s0,s1=map(float,a.excerpt.split(',')); make(os.path.join(a.out,'compare_excerpt.mp4'),s0,s1-s0)
times=[float(x) for x in a.times.split(',')] if a.times else [D*(i+.5)/12 for i in range(12)]
tiles=[]
for t in times:
    pair=[]
    for src in (a.ref,a.rem):
        p=f'/tmp/_cmp_{os.getpid()}.png'
        subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(t),'-i',src,'-frames:v','1','-vf','scale=480:-2',p],check=True)
        pair.append(Image.open(p).convert('RGB').copy())
    tiles.append((t,pair))
w,hh=tiles[0][1][0].size; cols=4; rows=(len(tiles)+cols-1)//cols
g=Image.new('RGB',(cols*w,rows*hh*2+rows*4),(40,40,40))
for i,(t,(r,m)) in enumerate(tiles):
    x=(i%cols)*w; y=(i//cols)*(hh*2+4)
    g.paste(r,(x,y)); g.paste(m.resize((w,hh)),(x,y+hh))
    d=ImageDraw.Draw(g); d.text((x+4,y+3),f'REF {t:.1f}s',fill=(0,255,0)); d.text((x+4,y+hh+3),'REMAKE',fill=(255,255,0))
g.save(os.path.join(a.out,'compare.jpg'),quality=85)
# review pages: 6 pairs per page, larger
for pi in range(0,len(tiles),6):
    sub=tiles[pi:pi+6]; pg=Image.new('RGB',(3*w,2*(hh*2+4)),(40,40,40))
    for i,(t,(r,m)) in enumerate(sub):
        x=(i%3)*w; y=(i//3)*(hh*2+4); pg.paste(r,(x,y)); pg.paste(m.resize((w,hh)),(x,y+hh))
        d=ImageDraw.Draw(pg); d.text((x+4,y+3),f'REF {t:.1f}s',fill=(0,255,0)); d.text((x+4,y+hh+3),'REMAKE',fill=(255,255,0))
    pg.save(os.path.join(a.out,f'review_{pi//6:02d}.jpg'),quality=85)
print('ok',a.out)
