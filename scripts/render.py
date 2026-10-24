#!/usr/bin/env python3
"""render.py script.json -o out.mp4 [--workers 8] [--start s --end s] [--fps N]
Loads templates/<style>/template.py (function draw(ctx, t, frame, S)) and renders in parallel chunks."""
import skia, argparse, json, os, sys, subprocess, importlib.util, time, multiprocessing as mp
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sys.path.insert(0,HERE)

def load_template(style):
    p=os.path.join(ROOT,'templates',style,'template.py')
    spec=importlib.util.spec_from_file_location('tpl_'+style.replace('-','_'),p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def worker(args):
    script_path,f0,f1,out=args
    from engine.core import Ctx
    S=json.load(open(script_path)); S['_dir']=os.path.dirname(os.path.abspath(script_path))
    tpl=load_template(S['style']); W,H=S['size']; fps=S.get('fps',30)
    if hasattr(tpl,'prepare'): tpl.prepare(S)
    ff=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgba','-s',f'{W}x{H}','-r',str(fps),'-i','-',
        '-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    ctx=Ctx(W,H,fps)
    for f in range(f0,f1):
        ctx.c.clear(0xff000000); ctx.c.save()
        tpl.draw(ctx,f/fps,f,S)
        ctx.c.restore()
        ff.stdin.write(ctx.rgba())
    ff.stdin.close(); ff.wait(); return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('script'); ap.add_argument('-o','--out',required=True)
    ap.add_argument('--workers',type=int,default=os.cpu_count()); ap.add_argument('--start',type=float,default=0); ap.add_argument('--end',type=float,default=None)
    ap.add_argument('--audio',default=None,help='mixed audio file (from audio.py); default: S["audio_mix"] if exists')
    ap.add_argument('--still',type=float,default=None,help='render single frame at time to PNG (out path)')
    a=ap.parse_args(); S=json.load(open(a.script)); fps=S.get('fps',30)
    if a.still is not None:
        from engine.core import Ctx
        S['_dir']=os.path.dirname(os.path.abspath(a.script)); tpl=load_template(S['style']); W,H=S['size']
        if hasattr(tpl,'prepare'): tpl.prepare(S)
        ctx=Ctx(W,H,fps); ctx.c.clear(0xff000000); tpl.draw(ctx,a.still,int(a.still*fps),S); ctx.image().save(a.out); return
    end=a.end or S['duration']; F0,F1=int(a.start*fps),int(end*fps)
    tmp=a.out+'.parts'; os.makedirs(tmp,exist_ok=True)
    n=a.workers; step=(F1-F0+n-1)//n
    jobs=[(a.script,F0+i*step,min(F1,F0+(i+1)*step),f'{tmp}/p{i:03d}.mp4') for i in range(n) if F0+i*step<F1]
    t0=time.time()
    with mp.get_context('spawn').Pool(len(jobs)) as pool: parts=pool.map(worker,jobs)
    lst=f'{tmp}/list.txt'; open(lst,'w').write(''.join(f"file '{os.path.abspath(p)}'\n" for p in parts))
    audio=a.audio or (os.path.join(os.path.dirname(os.path.abspath(a.script)),S['audio_mix']) if S.get('audio_mix') else None)
    cmd=['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',lst]
    if audio and os.path.exists(audio):
        cmd+=['-ss',str(a.start),'-t',str(end-a.start),'-i',audio,'-map','0:v','-map','1:a','-c:a','aac','-b:a','192k','-shortest']
    cmd+=['-c:v','copy','-movflags','+faststart',a.out]
    subprocess.run(cmd,check=True)
    subprocess.run(['rm','-rf',tmp])
    print(json.dumps({'out':a.out,'frames':F1-F0,'render_s':round(time.time()-t0,1)}))
if __name__=='__main__': main()
