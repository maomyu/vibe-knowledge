#!/usr/bin/env python3
"""extract_plate.py video t out.png [--ocr]  -> grab a frame and inpaint any OCR-detected text (stand-in for AI image assets
when re-making a reference; for new topics use GenerateImage / your image model with the prompt in the scene JSON)."""
import sys,cv2,numpy as np
v,t,out=sys.argv[1],float(sys.argv[2]),sys.argv[3]
cap=cv2.VideoCapture(v); cap.set(cv2.CAP_PROP_POS_MSEC,t*1000); ok,fr=cap.read()
from rapidocr_onnxruntime import RapidOCR
r,_=RapidOCR()(fr); m=np.zeros(fr.shape[:2],np.uint8)
for b,txt,c in (r or []):
    pts=np.array(b,np.int32); x,y,w,h=cv2.boundingRect(pts); cv2.rectangle(m,(x-6,y-6),(x+w+6,y+h+6),255,-1)
if m.any(): fr=cv2.inpaint(fr,m,9,cv2.INPAINT_TELEA)
cv2.imwrite(out,fr); print(out,len(r or []),'text boxes removed')
