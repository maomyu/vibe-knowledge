#!/usr/bin/env python3
"""onset_align.py script.json ref.ocr10.json rem.ocr10.json [fix.json] [--win 2]
For every text element in the script, find the first 10fps OCR frame (in a ±win window around its scripted t0) whose detected
lines contain the element's first 2 chars (typing reveals left->right), in ref and in remake. delta = ref - rem.
Prints table + share within ±0.1s (1 OCR frame); writes {text: delta} consumed by onset_fix.apply()."""
import sys,json,re
def norm(s): return re.sub(r'[\s，。、,.!?！？“”"\'：:；;—\-·()（）《》]','',s or '')
def frames(p): return [(f['t'],[norm(i['text']) for i in f['items']]) for f in json.load(open(p))['frames']]
def first(F,key,t0,win):
    hit=[t for t,L in F if t0-win<=t<=t0+win and any(key in l for l in L)]
    # need 2 consecutive hits to reject flukes
    for a,b in zip(hit,hit[1:]):
        if b-a<.15: return a
    return None
def texts(S):
    out=[]
    for coll in [S.get('overlays',[])]+[sc['elements'] for sc in S['scenes']]:
        for e in coll:
            tx=e.get('text')
            if isinstance(tx,str) and len(norm(tx))>=2 and e.get('type') not in ('charwall',): out.append((e.get('t0',0),norm(tx)))
    return sorted(set(out))
if __name__=='__main__':
    a=[x for x in sys.argv[1:] if not x.startswith('--')]; win=2.0
    S=json.load(open(a[0])); R,M=frames(a[1]),frames(a[2]); fix={}; rows=[]
    for t0,tx in texts(S):
        key=tx[:2]; r=first(R,key,t0,win); m=first(M,key,t0,win)
        if r is None or m is None: continue
        d=round(r-m,2); rows.append((t0,tx,r,m,d)); fix[tx]=d
    ok=sum(abs(x[4])<=.1+1e-6 for x in rows)
    for t0,tx,r,m,d in rows: print(f'{t0:7.2f} ref {r:6.2f} rem {m:6.2f} {d:+.2f} {tx[:20]}')
    print(f'matched {len(rows)}  within ±0.1s: {ok}/{len(rows)}')
    if len(a)>3: json.dump(fix,open(a[3],'w'),ensure_ascii=False,indent=0)
