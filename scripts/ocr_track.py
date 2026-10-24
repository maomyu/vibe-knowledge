#!/usr/bin/env python3
"""ocr_track.py ocr10.json W H y0 y1 [min_len=2] : text events inside a horizontal band (fractions of H).
Merges per-frame band text (lines sorted top->bottom joined by '\\n') into events {t0,t1,text,y,h} using fuzzy continuity;
text = most complete (longest) reading. Prints JSON list. Used to build timeline.json / captions for new styles."""
import sys,json,difflib
p,W,H,y0,y1=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]),float(sys.argv[5]); ml=int(sys.argv[6]) if len(sys.argv)>6 else 2
F=json.load(open(p))['frames']; s=1024/W   # ocr10 frames were downscaled to 1024 wide
ev=[]; cur=None
for f in F:
    its=[i for i in f['items'] if y0*H*s<=sum(q[1] for q in i['box'])/4<=y1*H*s and len(i['text'])>=ml]
    its.sort(key=lambda i:i['box'][0][1]); txt='\n'.join(i['text'] for i in its)
    ys=[sum(q[1] for q in i['box'])/4/s for i in its]; hs=[abs(i['box'][2][1]-i['box'][0][1])/s for i in its]
    if txt and cur and difflib.SequenceMatcher(None,txt,cur['text']).ratio()>.5:
        cur['t1']=f['t']; cur['_n']+=1
        if len(txt)>len(cur['text']): cur.update(text=txt,y=round(min(ys)),h=round(max(hs)))
    else:
        if cur and cur['_n']>=2: ev.append(cur)
        cur=dict(t0=f['t'],t1=f['t'],text=txt,y=round(min(ys)) if ys else 0,h=round(max(hs)) if hs else 0,_n=1) if txt else None
if cur and cur['_n']>=2: ev.append(cur)
for e in ev: e.pop('_n'); e['t1']=round(e['t1']+.1,2)
print(json.dumps(ev,ensure_ascii=False,indent=0))
