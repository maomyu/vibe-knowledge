#!/usr/bin/env python3
"""topic -> (LLM) scene JSON -> audio.py -> render.py
用法:
  pipeline.py prompt --style stardust-timeline --topic "熵"      # 输出给 LLM 的提示词
  pipeline.py build  scene.json -o out.mp4 [--tts]               # 混音+渲染
"""
import argparse,json,os,subprocess,sys
H=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(H)
def prompt(a):
    st=next(s for s in json.load(open(f'{ROOT}/styles.json')) if s['slug']==a.style)
    if not os.path.exists(f'{ROOT}/templates/{a.style}/template.py'): sys.exit(f'style {a.style}: no template yet')
    tpl=open(f'{ROOT}/prompts/script_writer.md').read()
    exs=[f'{ROOT}/examples/entropy_stardust.json'] if a.style=='stardust-timeline' else []
    exs.append(f'{os.path.dirname(ROOT)}/tests/{a.style}/script.json')
    ex=next((open(e).read() for e in exs if os.path.exists(e)),'(no example)')
    guide=open(f'{ROOT}/TEMPLATE_GUIDE.md').read(); sch=guide[guide.find('## 6.'):]
    sec=sch[sch.find(f'### {a.style}'):]; sec=sec[:sec.find('\n### ',4)] if '\n### ' in sec[4:] else sec
    print(tpl.replace('{{TOPIC}}',a.topic).replace('{{STYLE}}',json.dumps(st,ensure_ascii=False)+'\n\n'+sch[:sch.find('## 7.')]+sec).replace('{{EXAMPLE}}',ex))
def build(a):
    py=sys.executable
    subprocess.check_call([py,f'{H}/audio.py',a.scene])
    subprocess.check_call([py,f'{H}/render.py',a.scene,'-o',a.out])
ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd',required=True)
p=sp.add_parser('prompt'); p.add_argument('--style',required=True); p.add_argument('--topic',required=True)
b=sp.add_parser('build'); b.add_argument('scene'); b.add_argument('-o','--out',required=True)
a=ap.parse_args(); {'prompt':prompt,'build':build}[a.cmd](a)
