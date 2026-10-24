#!/usr/bin/env python3
"""audio.py script.json  -> writes <script_dir>/<audio_mix> (default mix.wav)
- BGM: S.bgm.src (+ offset, gain_db, loop to duration, fade out)
- Narration (optional): S.narration = {voice, rate, pitch, segments:[{t, text}]} -> edge-tts per segment, word boundaries
  saved to narration_words.json (for subtitle timing); BGM auto-ducked under voice via sidechaincompress.
- SFX (optional): S.sfx = [{t, src, gain_db}]
- Beat grid: writes beats.json (librosa) so scene cuts can be snapped: see snap_to_beats()."""
import json, os, sys, subprocess, asyncio
def sh(*a): subprocess.run(a,check=True)
def tts(text,voice,rate,pitch,out):
    import edge_tts
    async def go():
        c=edge_tts.Communicate(text,voice,rate=rate,pitch=pitch,boundary='WordBoundary'); words=[]
        with open(out,'wb') as f:
            async for ch in c.stream():
                if ch['type']=='audio': f.write(ch['data'])
                elif ch['type'] in('WordBoundary','SentenceBoundary'): words.append({'o':ch['offset']/1e7,'d':ch['duration']/1e7,'w':ch['text']})
        return words
    return asyncio.run(go())
def beats(path):
    import librosa
    y,sr=librosa.load(path,sr=22050,mono=True); tempo,b=librosa.beat.beat_track(y=y,sr=sr)
    return float(tempo if not hasattr(tempo,'__len__') else tempo[0]), [float(x) for x in librosa.frames_to_time(b,sr=sr)]
def snap_to_beats(t,beat_list,tol=.25):
    best=min(beat_list,key=lambda b:abs(b-t)) if beat_list else t
    return best if abs(best-t)<=tol else t
def main(p):
    S=json.load(open(p)); d=os.path.dirname(os.path.abspath(p)); D=S['duration']; out=os.path.join(d,S.get('audio_mix','mix.wav'))
    b=S['bgm']; src=os.path.normpath(os.path.join(d,b['src']))
    bgm=os.path.join(d,'_bgm.wav')
    # continuous BGM: never hard-loop (-stream_loop leaves an audible seam every loop = "一卡一卡").
    # If the track is long enough just trim; if shorter, chain copies with acrossfade (xfade seconds).
    off=float(b.get('offset',0)); fo=b.get('fade_out',1.5); xf=float(b.get('xfade',3))
    L=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',src],capture_output=True,text=True).stdout)-off
    n=1 if L>=D else int((D-xf)//(L-xf))+1
    if n>1: print(f'WARNING bgm {src} is {L:.1f}s < video {D}s: looping x{n} with {xf}s crossfades; prefer a full-length track')
    ins=[]
    for _ in range(n): ins+=['-ss',str(off),'-i',src]
    fc='[0:a]anull[a0]'
    for i in range(1,n): fc+=f';[a{i-1}][{i}:a]acrossfade=d={xf}:c1=tri:c2=tri[a{i}]'
    fc+=f";[a{n-1}]atrim=0:{D},asetpts=N/SR/TB,volume={b.get('gain_db',0)}dB,afade=t=out:st={max(0,D-fo)}:d={fo}[m]"
    sh('ffmpeg','-loglevel','error','-y',*ins,'-filter_complex',fc,'-map','[m]','-ar','48000','-ac','2',bgm)
    try: tempo,bl=beats(bgm)
    except ImportError: tempo,bl=0.,[]; print('librosa missing: beats.json skipped')
    json.dump({'tempo':tempo,'beats':bl},open(os.path.join(d,'beats.json'),'w'))
    N=S.get('narration')
    if not N or not N.get('segments'):
        sh('cp',bgm,out); print('bgm only',out,'tempo',round(tempo,1)); return
    inputs=[]; filt=[]; allw=[]
    for i,sg in enumerate(N['segments']):
        f=os.path.join(d,f'_n{i:03d}.mp3'); w=tts(sg['text'],N.get('voice','zh-CN-YunxiNeural'),N.get('rate','+0%'),N.get('pitch','+0Hz'),f)
        for x in w: x['o']+=sg['t']
        allw.append({'t':sg['t'],'text':sg['text'],'words':w}); inputs+=['-i',f]
        filt.append(f"[{i+1}:a]adelay={int(sg['t']*1000)}|{int(sg['t']*1000)},volume={N.get('gain_db',0)}dB[n{i}]")
    json.dump(allw,open(os.path.join(d,'narration_words.json'),'w'),ensure_ascii=False,indent=1)
    n=len(N['segments'])
    fc=';'.join(filt)+';'+''.join(f'[n{i}]' for i in range(n))+f'amix=inputs={n}:normalize=0[voice];[voice]asplit[v1][v2];'+\
       f"[0:a][v1]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[duck];[duck][v2]amix=inputs=2:normalize=0[m]"
    sh('ffmpeg','-loglevel','error','-y','-i',bgm,*inputs,'-filter_complex',fc,'-map','[m]','-t',str(D),'-ar','48000',out)
    print('mixed',out)
if __name__=='__main__': main(sys.argv[1])
