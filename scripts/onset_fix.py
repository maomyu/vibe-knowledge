"""onset_fix.apply(S, fix_json, max_shift=1.5, min_shift=.1): shift t0 of text elements whose text contains a measured
OCR line by (ref - remake) onset delta; t1 kept. Use as last post-pass in build_script.py; iterate render->ocr10->align."""
import json,os,re
def norm(s): return re.sub(r'[\s，。、,.!?！？“”"\'：:；;—\-·()（）]','',s or '')
def apply(S,path,max_shift=1.5,min_shift=.1):
    if not os.path.exists(path): return 0
    fix=json.load(open(path)); n=0
    for coll in [S.get('overlays',[])]+[sc['elements'] for sc in S['scenes']]:
        for e in coll:
            tx=norm(e.get('text','') if isinstance(e.get('text'),str) else '')
            if len(tx)<2 or e.get('_shifted'): continue
            ds=[d for s,d in fix.items() if s and (s in tx or tx in s)]
            if not ds: continue
            d=sorted(ds,key=abs)[0]
            if min_shift<=abs(d)<=max_shift and 't0' in e:
                e['t0']=round(e['t0']+d,3); e['_shifted']=1; n+=1
    return n
