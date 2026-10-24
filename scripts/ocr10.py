#!/usr/bin/env python3
"""ocr10.py video out.json [fps=10] : RapidOCR at N fps (downscaled to 1024 wide) -> {frames:[{t,items:[{box,text,conf}]}]}"""
import sys,json,cv2
from rapidocr_onnxruntime import RapidOCR
v,out=sys.argv[1],sys.argv[2]; fps=float(sys.argv[3]) if len(sys.argv)>3 else 10
eng=RapidOCR(); cap=cv2.VideoCapture(v); vf=cap.get(cv2.CAP_PROP_FPS); step=max(1,int(round(vf/fps))); R=[]; i=0
while True:
    ok,fr=cap.read()
    if not ok: break
    if i%step==0:
        s=1024/fr.shape[1]; fr=cv2.resize(fr,None,fx=s,fy=s) if s!=1 else fr
        r,_=eng(fr); R.append({"t":round(i/vf,3),"items":[{"box":[[float(a) for a in p] for p in b],"text":t,"conf":float(c)} for b,t,c in (r or []) if float(c)>.6]})
    i+=1
json.dump({"fps":fps,"frames":R},open(out,'w'),ensure_ascii=False); print(out,len(R))
