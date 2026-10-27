# 模板编写指南：从参考视频 vibe-code 一个新风格

原则：纯代码渲染（skia-python → ffmpeg）。不录网页、不用 img2video。3D 用 engine/three.py 软件渲染；人物/山水/插画用 engine/proc.py 程序化；地图用真实地理数据（engine/geo.py）。AI 图只作可选底纹，登记到 ai_image_requests.json。随机特效只需"统计上像"。

## 1. 拆解参考
1. 抽帧与字幕：`scripts/analyze.py <ref>` → analysis/<id>/（场景切点、OCR 字幕、主色、节拍）。
2. 切点：`scripts/cuts.py ref` 得硬切时间；脚本里场景边界对齐到这些时间（目标 ±1 帧）。
3. 字幕出现：`scripts/onsets.py` 获取字幕带起始帧。
4. 看帧！每个场景至少看 1 帧，列元素清单：背景类型 / 文字排版（字号以 1024 宽为单位 U）/ 3D 物体 / 粒子 / 镜头运动。

## 2. 模板结构（templates/<slug>/template.py）
- `BG` 字典：背景生成器（纸、夜空、proc 程序化场景、geomap…）。
- `EL`/`EXTRA` 字典：元素渲染器（text、cubes3d、text3d、route、charbars…），签名 `fn(ctx, el, t_local)`。
- 每个元素支持 t_in/t_out/kf 关键帧 `[[t, y, size, x], ...]`，由引擎插值；坐标用设计单位。
- 新元素务必注册进 EXTRA 字面量字典（否则静默丢失）。

## 3. 工具箱
- engine/three.py：Camera.proj、box_faces（字块立方体，正面贴字形）、sphere_op、cylinder_op、fog、render_ops（画家排序）。地面透视用 setPolyToPoly 单应。
- engine/proc.py：fbm/noise_tex、bamboo_forest(rain/snow/mist)、walker（走路循环）、precip（density/speed/length/width/size 统计参数）、water/mist/clouds/moon/moon_sea、ink_mountains/wire_mountains、boat/river_snow/lake_boat、lychee_rain、ink_bird。
- engine/geo.py：draw_map（省份高亮）、route（动画路线+城市名）。数据 assets/geo/china_provinces.json（DataV GeoAtlas，商用前核实许可）。

## 4. 随机特效的验收（统计而非逐像素）
`scripts/fx_stats.py <video> t0 t1` → count/area/bright（已去中值背景）。对 ref 与 remake 同一时间段比较，把 precip/orbs 参数调到 count、area、bright 各自 ±30% 内。motion 估计目前不可靠，靠肉眼。

## 5. 迭代循环
build_script.py → script.json → `render.py script.json -o remake_rN.mp4` → `/tmp/strip.py` 式对照条带肉眼检查 → `ssim.py`（看归一化分，结构类场景才有意义）→ `compare.py ref rem out --excerpt a,b`。
没看过帧不宣称还原度。

---
## 6. 通用化约定（所有风格必须满足）
- 模板只含"视觉语法"，**不含任何题材内容**：文字、数字、标签、地名/坐标、时间轴全部来自 script.json。
- 场景 = `{t0,t1,bg|kind, elements:[...], 可选 cam/xin/xfade/fade_in/fade_out}`；元素 = `{type,t0,t1,fi,fo,...}`，时间为绝对秒。
- 文本布局自适应：caption 类元素按 `max_w`（设计单位）自动折行（`engine.layers.wrap_markup`，保留 `[金/红]` 标记跨行），显式 `\n` 仍有效；`at:[...]` 为逐行出现时刻（相对 t0），行数多于 at 时按 stagger 递推。
- 标记：`[文字]` = 主强调色（金/红，依风格），`{文字}` = 次强调色（dusk 为红）。
- pipeline：`pipeline.py prompt --style <slug> --topic <题目>` 产出 LLM 提示（含本节 schema + 该风格 tests/<slug>/script.json 作为示例）；`pipeline.py build scene.json -o out.mp4 [--tts]`。

## 7. 风格 schema

### golden-fractal-vertical（金线分形·竖屏，1080x1920，设计 1024×1820）
顶层：`size:[1080,1920]`, `scenes[]`（每场 `elements`, 可选 `fade_in/fade_out`(默认.4), `zoom:[s0,s1]`, `zc:[x,y]`），`overlays[]`。
| type | 关键参数 | 用途 |
|---|---|---|
| caption | text, y=345, size=56, lh=90, max_w=940, x=512, color, glow | 顶部旁白，`[红字]` |
| glowtext | 同 caption（默认 glow） | 居中金句 |
| cite | text, y=1690, size=13 | 底部出处 |
| gline | pts[[x,y]…] 或 curve=[a,b,bend], draw=[t,dur], w, color, spark | 生长金线 |
| node | x,y, age(左灰), label(右白), r, side | 节点 |
| tree | x,y, branches=[[dx,dy,label,bend,children]], grow_at, stagger, dur, size | 分叉树/放射树 |
| crack | seed, box, n, depth, grow_at, dur, net_a, w | 裂纹网（程序生成） |
| arcweb | seed, n, nhub, hub, nv | 稀疏长弧网 + 红珠竖线 |
| ring | x,y,r, ticks=[[deg,label]], title, count=[c0,c1,dur], count_at, unit, csize, sub, sub1 | 环形时钟 + 大数字 |
| vbundle | xs, y0, y1, bends{idx:dx}, bend_at, rings, ring_y | 竖线束/转向 |
| matrix | x0,y0,dx,dy, rows, cols, red(比例), red_at, white_at, recover | 点阵统计 |
| ucurve | box=[x,y,w,h], ylabel, xlabels=[[0..1,label]], mark, draw_at, dur | U 形曲线图 |
| ropeline | p0, p1, draw, amp, turns | 麻花绳 |
| redcluster | x,y,r,n,seed | 红色粒子团 |
| hflash | t0, a, tau, color | 硬切闪光 |

### dusk-map-chronicle（暮色地图史话，1024x576）
顶层：`places:{名:[lon,lat]}`（任意地区地名；内置少量唐代地名可被覆盖），`map:{rivers:[NaturalEarth名]|'all', contrast, base, lift, dark}`。
地形：任意 bbox 自动下载 AWS Terrain Tiles（terrarium，按 ppd 选 z3–z9，缓存 assets/geo/tiles/）→ 自算 hillshade；河流来自 Natural Earth 50m。
场景 `bg`：`map`（需 `cam:[lon,lat,ppd]`，可选 `cam1`、`cam_at`、`cam_dur` 推拉/平移）| `stage`（烽台+`row:[{k:'s'|'c',x,lit:[[t0,t1]]}]`）| `night` | `citygate` | `fog` | `dig` | `desk`。`xin` = 与上一场叠化时长。
位置参数 `at` 可为地名或 `[lon,lat]`（地图场景），否则用 `x,y`（设计像素）。
| type | 关键参数 | 用途 |
|---|---|---|
| caption | text, at=[行时刻], size=37, lh=60, x=62, y=91, max_w=900, align | 左上叙述（`[金下划线]` `{红下划线}`） |
| cite / label | text, x,y 或 at, dx, dy, size, color, font, weight | 出处/标注 |
| counter | from,to,count_at,dur 或 vals=[[t,val,unit]], unit, head, x,y,size,usize,color | 跳动数字 |
| chain | route=[地名/坐标…], draw_at, dur, ease('out'), line, spacing, r, head, head_hold | 光点烽线/路线 |
| faintroute | route, color, w, dur | 淡色路线 |
| city | at, name, s, size, ldx, ldy, label, halo | 宫殿城市图标 |
| fire | at 或 x,y, s | 程序火焰 |
| towers | items=[[x,y,h]] 或 [[地名,h]], light_at, step | 小烽台链 |
| ring / ripple / slash | at, r, text, radius, ang / r / L | 虚线半径圈、涟漪、红斜杠 |
| badge | x,y,r,text,top | 月相徽章 |
| bigword | text,x,y,size,color,align | 大字（没来/我还在） |
| card / book / slips / tokens | box, title, lines, seals / cols=[(text,color)], head / items / items=[(label,color)],x,y,dx,r | 文献卡片、古书、木简、物件圆标 |
| bubble / dashline / rider | text,x,y / xy / route, go_at, dur, s | 对话框、虚线、驿马 |
- dusk `cam` 也可写 `{"fit":[地名…],"box":[x0,y0,x1,y1]}` 自动取景（默认 box [120,200,960,540]，给左上旁白留位）；示例 examples/dusk_grand_canal.json（京杭大运河，任意地区地形自动下载）。

### dim-room-candle（暗室微光，1280x720，设计 1024×576）
示例：tests/dim-room-candle/script.json（熵增，24 场景）、examples/dimroom_habit.json（新题材）。
- 顶层：size、duration、audio_mix、bg(默认 #08090b)、scenes[]、overlays[]。
- scene：{t0,t1,elements[],fade_in=.5,fade_out=.5,flash?:[peak,tau,colour?]}。默认淡入淡出到黑；fade 设 0 就是硬切，贴着切点的元素会直接出现、不淡入。flash 是切点处的暖白闪光（参考值 [.95,.3]，弱一点用 [.2,.5]）。
- 每个元素都有 t0、t1，可选 fi/fo（淡入/淡出秒数）和 a（不透明度）。坐标都在 1024×576 设计空间。
  - caption：text 支持 `[金色强调]`、`{tint 色}`、`\n` 手动换行；超过 max_w(820) 会自动换行。可选 x、y(底部 430–500 / 中央 270 / 顶部 75–110)、size(22–33；验收脚本里乘了 1.5)、align、tint、at=[每行相对出现时间]。
  - label：小号灰字，可选 x、y、size、color、align、spacing。ticker：value 是固定字符串；或者给 from/to 加 count_at、dur 做计数；scramble+settle_at 做巨数滚动；另有 prefix、suffix。
  - room：dust、dust_a、dirt(0–1)、light、bw、bh、cx、cy。city：lit(亮窗比例)、grow(0–1 植被)、base(地平线 y)、sky、seed。pair：d0→d1 间距，sep_at/sep_dur 控制分离，fray_at 时连线断开，另有 y、c2。
  - dotglyph：text 单字或词，x、y、size、n、assemble(秒)、scatter_at。coingrid：rows、cols、x0、y0、d，heads=[[t,正面比例]]，bar 开关。
  - histo：n、dur、xticks=[[标签,0–1]]、peak 文案、src_y。formula：text、y、size、legend=[[文字,色]]、foot。
  - figure：x、y、s，cool_at/cool_dur 冷却变灰，dissolve_at/dissolve_dur 消散。readout：head、from/to、at、dur、unit、x、y、size。
  - chat：msgs=[[t,'l'|'r',文本,时间戳]]，x0、x1、y、fs(字号)、bubble_w、max_y（消息多了会自动上滚）。
  - word：text、y、size、stars=[x1,x2]。road：hz(地平线)、vx、ww(窗宽)、light_at(窗灯亮)、draw_at/dur(边线)、ground、road_color。
  - sphere：x、y、r、color。stars：n。glowdot：x、y。
- 写新题材的套路：生活类比用 room/city/pair，后面接抽象概念，再接统计或公式，最后回到类比。文字长短由自动换行处理；同一屏不要超过 2 行主字幕和 2 行辅助字。
- caption 的 check:true 会在行首画金色 ✓（清单行，建议 align:'left' 并固定 x）；coingrid 的 bar_label 默认是“正面”，可以改成别的。
- 已知限制：人像只有一种半身剪影。

### gold-archive-history（鎏金年代档案，1024x576）
示例：tests/gold-archive-history/script.json（概率史，18 场景）、examples/archive_vaccine.json（新题材：疫苗史，英国地图）。
- 顶层字段：size、duration、audio_mix、bg{glow:[x,y],c1,c2,c3,motes}、scenes[]、overlays[]（brand 一般放在这里）。
- scene 字段：{t0,t1,elements,fade_in=.5,fade_out=.5,linger}。场景整体用 alpha 淡变。相邻场景可以让 t0/t1 重叠，做交叉淡变。
- 常驻框架（每个时代场景都放，用 build 的 era() 辅助函数生成；验收脚本最后会把各场景的 yearstamp 合并成一个 overlay：yearstamp{years:[[t,年份,副标]]}，年份滚动换代，同时场景交叉淡变 0.7s，旧道具留到新场景淡入）：
  - yearstamp：year、sub（地点 · 人物）、from（上一年份，数字会滚动过渡）、roll、x、y、size。
  - bookcard：latin（过长会自动缩小）、title（会自动加《》）、author、seal（默认“文献”）、max_w。
  - brand：text。
  - caption：text 支持 `[金]` 和 `{红}`；可选 sweep（扫入秒数）、size（28）、y（500）、max_w（900，超出自动换行，向上增行）。
- 文字类元素：
  - label：通用小字。
  - textblock：lines=[[文本,字号,dy,色]]，at 控制每行出现时间。
  - quote：foreign 外文斜体、text 主引文（[金]）、more 续行、attr 出处、x/align/max_w。
  - title：latin、text、sub、credit，并画一条钟形细线。
  - refs：片尾文献小字。
  - bigword：巨大的淡色拉丁字。
- 道具类元素：
  - die：3D 骰子。x0/y0 → x/y 落下并弹跳；spin 衰减到 rest 朝向，turn 是持续旋转；ghosts 拖影；labels 环绕标签（labels_at 控制出现时间）。
  - bones：一排距骨（n、size、label）。wheel：命运之轮（r、speed、color、alpha）。
  - coin：金币；split_at 时按 share 切出扇形。
  - scoreboard：sides=[{badge,score,filled,total,color,goal}]、head、stamp/stamp_at/stamp_off（红色印章）、ratio/ratio_at。
  - dienet：骰子展开图（labels、note）。fraction：label = num / den。
  - combos：cols=[{title,unit,rows:[[d1,d2,d3,'×6']],delay,color}]，骰子组合列表。
  - panels：对比卡，cards=[{title, dice | pairs, mult, lines, pct, pct_at, pct_text, die}]；可选 w、h、gap。
  - countrymap：真实国界（Natural Earth 50m，按 NAME/NAME_ZH 匹配）。countries、bbox、box=[x,y,w,h]、places=[[名,lon,lat,副标]]、link=[i,j,at,dur]（弧线 + 信封）。
  - tree：二叉结局树。depth、x0、x1、span、grow_at、lvl_dur、hl（高亮的叶子序号）、hl_at、leaves（每片叶子的标签）、groups=[[i0,i1,文本,色]]。
  - ledger：羊皮纸账簿（head、sub、rows、rot、w、h）。
  - tally：密纹统计柱，bars=[{label,value,frac,x,color}]，可选 ratio。
  - urnchart：瓮 + 对数 x 轴收敛曲线。p、n、draw_at、dur、chart=[x0,x1,y0,y1]、xticks、counter 格式串、caption_small。
  - binom：二项直方图。steps=[[t,n]] 控制 n 的变化；显示范围是 μ±3.2σ，所以 n 越大柱子越细；head 可以用 {n}；curve_at 画正态曲线。
  - needles：布丰投针（n、dur、spacing、panel、标签 l1/l2）。
  - galton：高尔顿钉板。rows、dx、dy、n、dur、fall、ball、bin_h；show_at 让它晚出现；curve_at 叠正态曲线。
  - axioms：rows=[[编号,公式,说明,at]]，可选 size、desc_dx。
- 写新题材的套路：每个时代 = era() + 1 个道具 + 1–3 条字幕；开头钩子用 die，结尾回到 die，最后接 title 和 refs。模拟类道具都是确定性随机（seed），只保证统计上像。

### storm-countdown-vertical（雷暴倒计时·竖屏，576x1024，设计 1024×1820）
示例：tests/storm-countdown-vertical/script.json（闪电，11 场景）、examples/storm_rocket.json（新题材：火箭发射倒计时）。
- 顶层：size [576,1024]、duration、audio_mix、scenes[]、overlays[]。scene：{t0,t1,elements,fade_in,fade_out}（验收脚本默认 0 = 硬切；闪光用 sky.flicker 制造“切”）。
- 背景：sky{top,mid,bot,clouds(0–1, 团块状紫色积云),cloud_h,b(云亮度),rain(0–1),flash:[[t,amt]],flicker:[[t,amp,dur]]}；city{y(地面),hs(楼高倍率),lit,tower_x(None=无塔),tower_h}；ice{n}（云内冰晶）；earth{x,y,r,spin,lon0}（陆地取自 Natural Earth 50m 真实国界栅格化）；flash{at:[[t,amp,dur]]}（放 overlays，制造硬切亮度跳变）。
- HUD：hud{timer:[[t,数值]]（ease:false 线性）,fmt,unit,label,status:[[t,'文本']],tag,frames,frame0,fps_cam,box,brackets}；altitude{marks:[[y,'文本',t_on,t_off]]}。
- 文字：title{text,size(84),y(1350),subs:['…' | ['…',相对时间]],sub_size,sub_dy,max_w 自动换行}；text{lines:[[文本,字号,dy,色,字体]],x,align,y,at}；bignum{value | from/to+dur | rate+start+fmt, head, foot, y, size}；rows{rows:[[大字,小字,at]],y,dy,size}。
- 闪电：leader{from,to,seed,tip:[[t,0..1]],w,alpha,branches}（梯级先导下探）；strike{同 from/to/seed, rise(自下而上点亮秒数), glow, flick:[[t,amp]], dim_after, halo_y, w}；streamers{points:[[x,y,len]]}；charges{rows:[[y,'+'|'−',n,色]]}；rings{x,y,speed,n,gap,max_r}；head{x,y,r,rise}（头发竖起插图）。
- 同一 seed+from/to 的 leader 与 strike 共用同一条通道（先导→回击连贯）。
- 新题材套路：开头一句反常识（text 上部）→ “把这 X 秒放慢” → HUD 计时贯穿主体，每个物理阶段一个 title + 道具 → 数据面板 → 原速重放 → 结语。

### 7.x bronze-hud-instrument (1024x576)
scene: {t0,t1,zoom?,elements[]}; overlays: caption{lines,t0,t1,hl}, header{chapter,idx,total}.
elements: label{text,size,x,y} · emblem{kind:target|number,n,r,label,sub,label_size} · timerbox{s} · numgrid{n,cells} · wordgrid{rows:[[word,color]],head,counter,reveal_t} · digits{items:[[d,x,y,size,t]]} · cards{items,w,h,reveal} · icon{shape:circle|square|triangle|diamond|star|eye|shield|book|pen,s,label} · bigword{text,size|[[t,v]],x,rot,keys} · carousel{chars,speed,size,y} · diagram{nodes,edges} · panel{title,x,y,w,h} · dial{r,a0,a1,sub} · strip · rule.
文本长度自适应：caption 自动换行，label 超宽自动缩小。

### 7.x white-line-doodle (1024x576)
scene: {t0,t1,fade_in,fade_out,invert?(白底闪回)}; overlays: corner{left,right,sub}, caption{text "[粗体]"}.
elements: title{text,size,y,weight} · dottext{text,size,x,y,n,build,disperse} · ground{y,sparkle,draw} · figure{x|[[t,x]],y,h,pose:stand|walk|sit|fall,filled} · crowd{n,x0,x1,gap:[a,b],h,pose,stagger} ·
wheel{x,y,r,spin,rays,towers,orbit} · shards{n,speed,x,y} · prop{kind:camel|book|tablet|bowl|sign|box|tree|house|bag|kite|bench 或 paths,x,y,s,flip,draw,drift,spin,bob} ·
snake{words[],x,y,x1,y1,n,grow} · spotlight{x,y,w0,w1} · waves{y,n,dy} · sun{x,y,r,rise} · photo{pan} · curtain.

### 7.x terminal-gray-data (1024x576)
scene: {t0,t1,invert?(纸白),fade_in,fade_out}. 文本 [蓝色关键词]。
elements: textblock{x,y,lines:[str|[str,t]],size,lh,kicker,note,cps,max_w} · caption{text,x,y,size,align,color} · title{text,size,x,y,sub} · clock{values:[[t,str]]|count{from,to,dur,fmt},size,unit,sub} ·
chat{x,y,dx,msgs:[[t,text,l|r|c,stamp]],step,max_h} · dotmatrix{x,groups:[[label,count,y,t]],cols,fill} · spike{x,y0,y1,grow} · pillgrid{x,y,cols,rows,hi,hi_t,pct,pct_blue,pct_sub,label} ·
tank{x,y,w,h,level|[[t,v]],wave,tags:[[t,text]],particles,label,head} · pipe{x0,x1,y} · danmaku{words,n} · ocean{y|keys,n,spread,depth,buoy,labels:[[t,text,x,y]]} · bars{items:[[label,frac]]}.

### 7.x teal-night-city-topdown (1024x576)
scene: {t0,t1,fade_in,fade_out}; overlays: caption{text 'main|灰色尾巴',x,y,size}.
camera keys (zoom/dx/dy, [[t,v]]) on citymap/subway/zebra.
elements: title{text,size,x,y,align,sub} · curves{mode:arcs|weave|wave,lines,x,y,w,h,draw} · wiggle{years,merge,amp,draw} · citymap{routes:[{pts,col:o|t,t0,dur,label}],labels,year,seed} ·
subway{cars:[y],n,warm,floor,hl:[[x,y,o|t,t]],dist{a,b,text,t0}} · zebra{n,hl:[{x,y,c}]} · lamp{x,y,walkers:[{x,y,c,umbrella}]} · particles{clusters:[{x,y,col,n,s,vx,vy}],link} · pill{text,x,y,w,cps,fill} · warm.

### 7.x cosmic-particle-epic (1024x576)
scene: {t0,t1,fade_in,fade_out,flash(入场白闪)}; overlays: caption{text,[蓝]{红}<金>,x,y,size,align}.
elements: stars{mode:rain|hlines|warp} · title{text,style:gold|silver,kicker,sub,sub_size,foot,size,x,y,align} · counter{from,to,fmt,size,col} · finger{label} · globe{x,y,r,lon0,tilt,spin,marker:[x,y,label]}(Natural Earth 陆地) ·
dottext{text,size,build,disperse} · star{x,y,r,col} · nebula{x,y,w,h,col} · beam{p0,p1,draw,n,speed} · sonar{r,ticks,count{from,to,label,unit}} · cube{x,y,s,strings,event_t} · streaks{n,lines,x0,x1,count} ·
neon{x,y,w,h,seed} · galaxy{x,y,r} · aurora{hz,milky,person,bench} · depth{ball_y keys,ticks,year,year_sub} · beams3d.

### 7.x flat-cartoon-situation (1920x1080, 1024 设计坐标)
scene: {t0,t1,fade_in(>0=与上一场交叉淡化),flash(入场1帧白闪),flash_at:[t]}; overlays 同 elements.
场景: backdrop{kind:night|room|dark|cream|blue|green|stage|split|bokeh|nightwarm|black} · window{x,y,w,h} · picture · clock{x,y,speed} · spot.
文字/UI: headline{text,[红]{蓝}<绿>(橙),x,y,size,color,shadow} · subtitle · tag{text,x,y,bg} · battery{x,y,w,h,pct:[[t,%]..],delta,label} · chips{y,items:[[名,值,色,t]],w} · bubble{text,x,y} · burst{text,x,y,size} · tube{x,y,w,h,level:[[t,%]],col,label,thresholds:[[%,txt]]} · rope · dotgrid{red_from} · icon{kind:check|cross|heart|house|num,x,y,r,text,bg} · bignum.
角色/道具: person{who:man|mom|kid|blue|green|pink|grey,x,y,mood:smile|angry|sad|neutral|mask,s,walk,shake,steam} · table · phone{x,y,msgs:[[txt,l|r]]}.

### 7.x starry-matchmaking-graph (1280x720, 1024 设计坐标)
顶层: under[sky{moon:[x,y,r]|null,milky,mountains,top,mid}](全片底层) · overlays[logo{text,note}]. scene: {t0,t1,fade_in,fade_out}.
elements: header{text({金}),x,y,sub,dots,k(数或[[t,k]])} · board{left/right:[{name,tcol,col,g:m|f,hair:0-2,mood,prefs:[[字,色]]}],prefs(bool),y0,dy,xs[6],s,
links:[[t0,t1,i,j,'temp'|'ok',bend,col]],ring/cross:[[t0,t1,side,i,k(,col)]],heart/dim:[[t0,t1,side,i]]} · person{x,y,g,col,hair,mood,s} · link{p0,p1,bend,dur,dashed,tag,knot,col} ·
bigtitle{text,size,font(brush),y,stagger,col} · sub{text({金}),y,size} · note{text,x,y,size,col} · panel{x,y,w,h,title,tcol,center,lines:[[txt,col,t]],size,ly,lh} ·
medal{x,y,r,year,lines:[[txt,size,col]]} · heart{x,y,s,dur,fill} · elder{x,y,r}(月+云+月老剪影) · knot · tile{x,y,text,col} · arrow{x,y0,y1}.

### 7.x neon-heart-pulse (1920x1080, 1024 设计坐标)
scene: {t0,t1,fade_in,fade_out}; 硬切处加 flash{dur:.034,a:1}(1帧白闪，供切点检测)。
elements: bg{kind:dark|cream,col,glow:[x,y,r,col],vignette} · bigchar{text,x,y,size,col,glow,pop,scale keys,bpm,ring,ring_t,annot{text,x,y,size,t,to:[x,y]}} ·
ecg{y,x0,x1,beats:[x..],amp,gap:[[x0,x1]],draw,col} · string{y,x0,x1,tension keys,glitch,snap:t,ellipse} · gauge{x,y,r,v keys,label} · clock{x,y,r,spin,glitch} ·
chat{x0,x1,y,size,gap,dark,panel:[x,y,w,h],name,head,max,msgs:[[t,'l'|'r',text,size,t_end]]} · keyboard{x,y,w,typed:[[t,text,'type'|'del']]} ·
corner{text('#'=计数),count keys,x,y,size,col,font,sub} · words{items,n,spread,seed} · hands{x,y,s,fill keys,pour:[t0,t1],leak:[t0,t1],squeeze keys,open keys} ·
sub{text([粉]),x,y,size,col,hi,glitch,lh,stag; 多行用\n} · flash{col,dur(<0=渐暗)} · ring{x,y,r}.

### 7.x music-theory-visualizer (1920x1080, 1024 设计坐标)
顶层 under[bg{col,tint}]. scene: {t0,t1,fade_in,fade_out,flash(入场1帧白闪=硬切)}. 音名颜色 COL(宫商角徵羽)、简谱 DEG(1/2/3/5/6) 自动取色。
elements: hud{tl:[EN,中],tr,big_tl(数或keys→两位数),big_tr,bl} · sub{text([高亮]),hi,size,y} · glyph{text,x,y,size,col,pinyin,glow} · text{text|runs:[[txt,col,t]],x,y,size,mono,serif,align,glow} ·
counter{x,y,value keys,fmt,label,size,col} · string{x0,y,len keys,col,label,ring,pluck:[t]} · bars{x0,w,gap,y,items:[{num,col,h keys,on keys,ring}],ghost} ·
wave{x,y,w,h,draw,waves:[{f,col,amp,cy,label,sum}],marks} · lissa{x,y,r,ratio:[a,b],draw} · piano{x,y,w,h,white,lit:[[t0,t1,'w3'|'b2',col]],labels} ·
penta{x,y,r,names,order,draw_t,draw} · strings5{xs,y0,y1,names,pluck:[[t,i]]} · fret{x,y,w,h,frets,dots:[[fret,string,音名,t]]} · flower{x,y,center,rings:[[n,R,size,col]],spin} ·
cards{items:[[音名,数字]],x0,y,w,h,gap,skew,sweep:[t0,t1]} · seq{text(简谱),x,y,size,dots,stag,hi} · items{title,x,y,lh,items:[[num,txt,col,t]]} · chips{x,y,size,gap,items:[[音名,副标,t,active]]} · flash.

### 7.x golden-cup-cinema (1920x1080, 1024 设计坐标)
overlays: tag{text,en}. scene: {t0,t1,fade_in,fade_out}(默认 .6 淡变); 硬切处加 flash{t0}(自动排到最上层)。
elements: stage{kind:dark|desert|dusk|night|warm|stone,floor,sun:[x,y,r],cracks,stars,vig} · spot{x,w,top,y1,i keys} · halo{x,y,w,h,col} ·
goblet{x,y(杯口中心),s keys,col:gold|black|copper,fill keys,liquid,drips,stream:[t0,t1],glow} · mug{x,y,s,steam} · plate{x,y,w,kind:grapes|bread|meat|bowl} · candle{x,y,h} ·
pedestal{x,y,w,h,label,lit} · person{x,y(脚底),s,pose:stand|kneel|arms|sit,col} · rays{x,y,n,spin,confetti} · portal{x,y,r,scale keys,text,moon:[dx,dy]} ·
wall{y,gate,plaque:[行],trees:[[x,dir]],glow} · table{x,y,w} · ticket{x,y,text,rot} · ghost{text,x,y,size} · vortex{x,y} · pool{y,sx,stream}(金液特写) ·
sub{text([金]),x,y,size,lh} · big{text,x,y,size,font,col,glow} · flash.

### 7.x bio-3d-microscope (1024x576)
overlays: hud{logo|crumb|tag} · flash{t0,dur,a}(漏检硬切补 1 帧白闪)。scene 支持 flash 标志。
elements: bg{col,floor,glow:[x,y,r,col],only_glow} · sub{text([蓝]高亮,\n),x,y,size,cite} · title{text,x,y,size,sub,col,spacing} ·
neuron{x,y,seed,fam:blue|violet|cyan|gold,s,axon:(len,angle),fire:[t..],glow,grow} · field{n,fams,s,seed,drift}(背景神经元群) · cell{x,y,r,rot}(绿藻) ·
membrane{y,rows,channels:[[x,open|[[t,0/1]..]]],ions,flow:[[t,0/1]]} · sphere{x,y,r,col:[亮,暗]} · trace{x,y,w,h,l1,l2,spikes:[t..],win} ·
mouse{x,y,s,fiber,glow,flip} · glassbox{x,y,w,h,d} · lens{x,y,r,fam,n,seed,label} · label{text,x,y,size,col,align,sub,to} ·
bignum{x,y,value,unit,pre,fmt,legend:[[文字,色]]} · brain{x,y,w,h,circuits:[[t,[[x,y]..]]],icons} · stars{n} · card{x,y,w,h,lines}.

### 7.x cyber-neon-icons (1920x1080, 1024 设计坐标)
overlays: sub（字幕/金句都放 overlays，按 OCR 事件）· flash{t0,dur}。scene: fade_in(默认 .3) + flash 标志(硬切白闪)。
elements: bg{c1,c2,cx,cy,r,c3,p3:[x,y,r],bokeh,grid(地平 y),gcol,waves(条数),wcol,wy} ·
sub{text([关键词]=hl 色,\n),x,y(基线),size,col,hl,glow,bar(下划线),barcol} · head{text,x,y,size,col,gcol} ·
person{x,y,s,col,mood:sad|happy,scribble,neon,horns(反派)} · figure{x,y,s,col}(发光小人) · car{x,y,s,col,ncol,dx keys,scratch:t} ·
phone{x,y,s,msgs:[{text,t,me}]} · clock{x,y,r,col,speed} · chapter{x,y,w,h,num,label} · hbars{x,y,n,w,col,seed} ·
gline{pts:[x0,y0,x1,y1],col,w,dur,draw,dash,nodes:[[x,y,字]],ncol} · ecg{y,x0,x1,amp,col,dur} · orb{x,y,r,col,rcol} ·
web{n,col,seed,nodes:[[x,y]],slash:x} · radar{x,y,n,r,step,col} · frame{x,y,w,h,col,dur}(描画霓虹框) · people{list:[[x,y,s,col]]} ·
table{x,y,r,n} · dots{x,y,rx,ry,n,col} · split{x,cl,cr} · horizon{y,col,target:x,tiles} · face{x,y,s} · target{x,y,col,check:t} ·
gauge{x,y,r,v keys,col} · tiles{list:[[x,y,eye|text|chat|card|key|check|smile|flat]],col,s} · flash.

### 7.x red-alert-lime (1920x1080, 1024 设计坐标)
under: hud{tl,tr,prog keys,col}。overlays: text / tag{num,text,y,col} / flash。scene: fade_in(默认 .3)。前半用红底 bg，后半换绿底 bg 即完成"红→绿"叙事。
elements: bg{base,tint,ta,cx,cy,r} · text{text([关键]=hl),x,y(基线),size,font:serif-bold|sans|sans-bold,col,hl,glow,align,strike:t,scol,fi,fo} ·
pill{text,x,y,size,col,tcol,fill} · checks{x,y,lh,size,items:[[文字,t]],checked,bcol,col} · boxes{list:[[x,y,w,文字]],step,col} ·
loop{x,y,r,nodes:[[文字,角度]],hot(高亮节点下标),count keys,unit,draw,spin,ring} · dot{x,y,r,col,pulse} · alarm{blink,stripes:[y]} ·
countdown{x,y,r,p keys(0-1),secs keys,col} · play{x,y,s,col} · ellipse{x,y,rx,ry,draw,col}(圈词) · dashring{x,y,r,n,col} · chevron{x,y,col} ·
bar{x,y,w,p keys,col} · rule{x0,y0,x1,y1,col} · flash{t0,dur,col}。

### 7.x amber-bokeh-history (1280x720, 1024 设计坐标)
overlays: text（字幕 y≈538 size 19；标题/注释按位置）· flash。scene: fade_in(默认 .5 叠化，自动垫上一场景) + flash 标志。
elements: bg{kind:amber|stone|forest|wheat|dark2|dark,seed,drift,zoom,push,ta,glow:[x,y,r],gcol,band(y,亮金光带),vig} ·
bubbles{n,rr:[r0,r1],speed,col,seed}(酵母环) · dust{n,col} · bokeh{n,band:[y0,y1],cols,k(亮度)} ·
worldmap{bbox,box,ma,places:[[名,lon,lat,副]],step}(Natural Earth 真实轮廓) · craters{list:[[x,y,rx,ry]],glow} ·
relief{y,figs:[[x,s,朝向]],jars:[[x,w,h]],pillar:x} · dial{x,y,r,col} · link{pts,dur} ·
vessel{kind:jar|goblet|cup|tripod|glass,x,y,s,fill keys,beams} · toast{x,y,s,dur} · ruler{y,labels,at keys} ·
icon3{x,y,kind:sprout|burst|dots,s} · table{y} · text{text([金]),x,y,size,font,col,hl,align,glow}。

### 7.x savanna-silhouette-vertical (720x1280 竖屏, 设计宽 1024、高≈1820)
overlays: text / flash。scene: fade_in(默认 .5) + flash 标志。
elements: room{win:[x,y,w,h],lit keys(0-1 窗亮),lamp,lampxy,lampon keys,clock:'23:47'|分钟 keys,clockxy,bed(y),pose:sit|lie|None,person:[x,y],ps} ·
savanna{horizon,top,sun:[x,y],trees:[[x,s]],night keys,panel:[y0,y1](只画中间一条，用于上下分屏)} ·
zebra{x,y,s,flip,run(0/1 跑动),dx keys} · lion{x,y,s,flip,run,dx keys,col} · worries{list,n,band:[y0,y1],sizes,step,rise,seed}(漂浮担忧字) ·
wall{list,rows}(暗色文字墙) · smoke{x,y,s,col}(红色想象狮子) · ecg{y,x0,x1,rate keys,amp keys,label,col} · matrix{x,y,cols,sp,n keys,col}(红色小狮子点阵) ·
text{text([红]),x,y,size,font,col,hl,glow,align} · black{col} · flash。

### 7.x pixel-rpg-dialogue (1280x720, 1024 设计坐标)
overlays: text / flash。scene: fade_in(默认 .3) + flash 标志。
elements: room{mom,momxy,ms,son,sonxy,ss}(像素餐厅) · hpbar{px,py,php keys,pcol,plabel, mx,my,mhp keys,mcol,mlabel,boss} ·
dialog{name,text,x,y,w,h,size,cps,typewriter,delay,gold,arrow} · menu{items,sel,x,y,w} · dmg{text,x,y,size,col} ·
gameover{title,sub,hint} · ready{text,sub,size} · flowchart{nodes:[[x,y,w,h,label,col]],edges:[[i,j]],title,step} ·
inspect{title,rows:[[k,v]],x,y,w,h} · photo{caption} · book{title,author,steps} · bubble{text,x,y,size,fill,col} · text · flash。

### 7.x evolution-silhouette (1280x720, 1024x576 设计坐标)
scene: fade_in(默认 .6, 纪元交叉溶解 .8) + flash 标志；硬切用 fade_in=0。overlays: sub / title / walker / flash。
elements: sky{cols[上→下],sun[x,y,r],suncol,rays(强度),rayxy,stars,haze[y,col,a]} · hills{y,col,amp,freq,seed,scroll,volcano[x,h]} ·
ground{y,col,col2,grass(草高),scroll} · sea{y,x1(可 keys, 海岸线左移),cols,weeds,scroll} · trees{items[[x,s,kind]],kind:fern|palm|round|acacia|spruce|pole,y,col,scroll,wrap} ·
city{y,col,hmax,ruin(0-1 断楼比例),lights,seed,scroll} · walker{kind:fish|lizard|dino|mammoth|ape|man|spear|rifle|staff,x,y(可 keys),s,speed,walk,child(牵手小孩 dx)} ·
mushroom{x,y,s,col} · fire{y,h} · bars{n,col,scroll,banners[[x,w]]} · smog{col} · smoke{items[[x,y,s]],col} ·
sub{en,zh,shadow(描边色,默认黑,None 关),shadow_a,text(=zh,供 onset 对齐),y≈516,size 18-21} · title{zh,en,y,size} · tint{col} · flash。
scroll: 数字=px/s 匀速，或 keys [[t,px]]。视差：远层 scroll 小、近层大。浅色天(雪原)底部字幕需深色地面或改 col。

### 7.x neon-halo-profile (1920x1080, 1024x576 设计坐标)
scene: fade_in(默认 .3) + flash 标志；场景元素缺 t0/t1 自动继承场景。overlays: text / flash。
elements: bg{col,tint,tx,ta,bars,barh} · head{x=820,y=330,s,col,fill(可 keys),rays(可 keys),halo(半径,0 关),hdx,hdy,veil,ring(金色头顶光圈),eye_glow,draw(描线秒数)} ·
prop{kind:sun|cup|hourglass|heart|flower|coin|bread,x,y,s,col,n,pos} · ctext{text,x,y,size,align,font(默认 serif-vf 900),col,gcol,gold,chroma(RGB 偏移 px),jitter,glow,reveal(字/秒)} ·
text{text,x,y,size,font,col,align,spacing,glow} · rule{x0,x1,y} · ring{x,y,r,col,grow} · dots{x,y,cols,n(默认=脚本中章节大标题数)} · tint · flash。
惯例：情境 1.8s(灰 caption y236 + 引语 size38 y292，head fill .35) → 硬切 → 章节卡(kicker y178 / ctext size118 y305 / 拉丁 y+52 / rule y+77 / 两行 y+105,+132)。暗场景硬切需加白 flash 才可被检测。

### 7.x beat-breakdown-vertical (576x1024 / 1080x1920, 1024 宽设计坐标, H≈1820)
scene: fade_in(默认 .3, 本风格多用 0 硬切) + flash 标志；场景元素缺 t0/t1 自动继承。overlays: flash（暗底同色系切点必须加白闪才可检测）。
elements: bg{col,glow[x,y],gr,gcol,ga} · tag{no,text,y,size,spaced} · head{text 多行,[高亮],x,y,size,font,col,hl,chroma(px),slam} ·
bignum{text|value(keys),fmt('%.1f秒'),x,y,size,unit,chroma,col} · walker{x,y,s,bpm,labels} · slider{y,x0,x1,range,ticks[[v,lb]],band,bandlabel,value,label} ·
dial{x,y,r,period,start,count0,labels,unit,rays,caption} · chords{y,items,w,scroll(keys),sel|sel_rate,label} · piano{y,h,n,hi{键序号:标签},under[[lb,x]]} ·
bassline{y,sp,steps[[x,level]],levels[[lb,level]],cursor,speed,label,top,bot} · stats{y,gap,stagger,rows[[大数,标题,说明]]} · cards{x,y,w,h,rot(keys),n} ·
rays{x,y,n} · count{text,bgcol,col,size}(整屏倒数卡) · blurbg{col,boxes} · text{text,[高亮],x,y,size,font,col} · flash。
惯例：tag y≈100–230；标题 size 85–115 两行；dial 中心 y≈1000 r 280；章节 = 场景硬切。

### 7.x organ-infocard-dark (1920x1080, 1024x576 设计坐标)
scene: fade_in(默认 .5) + flash 标志；场景元素缺 t0/t1 自动继承。overlays: flash。
elements: bg{kind:wine|teal|navy|dark,hud[左标签,右标签],glow[x,y,col]} · title{text,[高亮],x,y,size,align,col,hl,strike,strike_t,strike_col(默认 #ff1a2a, 带暗边)} · badge{text='误区',x,y,rot,size,col} ·
stomach{x,y,s,col} · glass{x,y,s} · chili{x,y,s,rot} · bowl{x,y,s,steam} · thermo{x,y,h,level(keys)} · scope{x,y,r,acid,labels[[lb,y]]}(显微圆:黏液+绒毛) ·
tempath{pts,dots[[x,y,名,值,色]],draw} · panel{x,y,w,h,title,ts,lines,ls,col,border,hl,slide} · tissue{x,y,w,h,label,pins[x..],fire} · bars{x,y,rows[[lb,frac,val,col]],gap,w} ·
bell{x,y,w,h}(红实线+绿虚线) · habit{x,y,w,h,icon:clock|moon|bowl|bed|cup|cig|cloud|run|chop|sleep|plate|fire,is,title,ts,sub,ss,no,col(RED/GRN 决定底色),dim,hl,iconright} ·
foodcard{kind:glass|chili|bowl,x,y,w,h,rot,label,verdict,vcol} · pill{text,x,y,col,fill} · text{text,[高亮],x,y,size,font,col,hl,align} · tint · flash。
惯例：误区章节 = bg(hud) + 删除线标题(x30,y112,size46) + 误区章 + 左插画 + 右数据卡 + 底部 caption(y≈505,size19)；习惯网格 4x2 (x45+240i, y178/330, 218x140)。

### 7.x chalkboard-classroom (1280x720, 1024x576 设计坐标)
scene: fade_in(默认 .6, 本风格无硬切，全靠溶解) + flash；场景元素缺 t0/t1 自动继承；board/night 应放在元素列表最前。overlays: text(底部 caption y≈516 size 29, [荧光绿])。
elements: board{box[x0,y0,x1,y1](全屏 [-10,-10,1034,470] / 小黑板 [60,10,964,330]),frame,heads} · night{}(夜间婴儿房开场) · crib{x,y,w,label[2行]} ·
kids{x0,x1,y,n,s,sizes[]} · desk{x,y,s,book,booktext,side[dx..]} · vline{x(keys),y0,y1,col(LIME/ICE),dot,label} · bar{x,base,w,h,col,top,tcol,ts,bottom,grow} ·
scatter{box,n,slope,trend,trend_t,seed,labels[[lb,x,y]]} · months{x0,x1,y} · hbar{x,y,w,frac(keys),label,col} · box{x,y,w,h,lines,center} · stick{x,y,s,col} ·
calendar{x,y,w,h} · paper{x,y,w,h,rot,lines([红])} · spark{pts} · window{x,y,w,h} · text{text,[高亮],x,y,size,font,col,hl,align} · tint · flash。
惯例：左上数据来源 header size 20 (x30,y82)；顶部问句 size 17 y36；大标题 size 42–66。

### 7.x stardust-timeline (1024x576 设计坐标)
#1 星尘时间轴 (stardust-timeline) — reference 7690337875291950345 《信息论 惊奇之学》.
elements（由 template.py 自动整理的参数键，详见各函数）: hflash{a,tau,color} · charbars{n,x0,x1,y,tall} · sub2{size,weight,text,hl,y,en} · kicker{num,zh,en} · ltext{size,weight,spacing,text,cps,instant,slot,x,align,y,color,glow} · meter{x0,x1,y,move_t,move_dur,v0,v1,color,tag,label} · axis{y,x0,x1,range,zoom,draw,color,step,cut,dot} · bigtext{font,weight,color,glow} · comet{y,line_color,line_a,dots,trail,bits,nbits,rows,bit_size} · binrow{bits,cps,slots,y} · label{text,x,y,font,size,weight,color,align,spacing,glow} · wave{x0,x1,y,amp,noise,noise_t,color} · orbit{x,y,rx,ry} · maskline{text,size,y,box,mask,mask_t} · scramble{text,size,alt_t,alt,keep,dim_t,y} · cmb{kf,y,x} · noisefield{pow,amp,base,band,tint} · horn{x,y,s} · scope{box,amp,title} · cards{n,y,x} · arc{x,y,r,travel,lights} · probe{x,y} · planet{x,y,r,color} · flare{r,at_tower,x,y,fire,bar} · headline{box,text}

### 7.x silhouette-stage-paper (1024x576 设计坐标)
#6 剪影舞台·信纸 (silhouette-stage-paper) — reference 7692022955122937098 《知识诅咒》.
elements（由 template.py 自动整理的参数键，详见各函数）: subtitle{text,y,size,hl,cps} · infocard{value,count_at,count,color,label} · cite{ref,title} · figure{x,y,s,color,dim,glow,arm,arm_angle,tap,side,label,label_color,ring} · crowd{cols,rows,x0,y0,dx,dy,n,reveal,dim_at,hits} · bubble{x,y,w,h,border,fill,pointer,px,pdir,pcolor,kind,size,weight,text,color,caption} · tag{size,weight,text,pad,h,x,y,box,r,fill,border,color} · paper{move,x,y,w,h,rot,topbar,items,lines} · stamp{font,size,weight,text,pad,x,y,rot,fill,color} · bars{base,bars,axis,ax0,ax1} · phone{x,y,w,h,glitch_at,clock,msgs,max} · linkline{x0,x1,y,l0,l1,back_at} · titlecard{x,y,size,box,title,kicker,subs,dot} · textbox{box,kicker,lines} · quotecard{x,y,role,quote,rebut_at,rebut} · glass{fi,s,x,y,cool_at,ring} · formula{box,lines,cross_at} · tower{x,y} · plane{x,y,s} · book{x,y,w,h,rot,color,title,sub} · menu{header,items,current} · caption{text,x,y,size,color,spacing} · coins{n,x,y} · curve{draw,pts,color,w,dash}

### 7.x ink-paper-typography (1024x576 设计坐标)
#28 宣纸水墨字效 (ink-paper-typography) — reference 7690248321424074417 《定风波》.
elements（由 template.py 自动整理的参数键，详见各函数）: geomap{fi,fo,rect,bbox,fill,stroke,highlight,route,route_t0,route_dur} · cubes3d{D,fov,groups,light,fog,fog_col} · text3d{depth,dir,side,skew,x,y,step} · tile{size,gap,text,x,y,stagger,fi,fo,drop,fall_at,rot,gray,keep} · hud{color,text,km,km_t} · ink_burst{fo,seed,dur,x,y,color,r,n,mode,sx,sy} · splatter{seed,x,y,n,r} · charwall{fi,fo,size,color,floor,persp,horizon,speed,near,scroll,density} · tilegrid{cell} · cards{items,w,h,gap,x,y,flip_at} · timeline{y,nodes} · ring{draw,color,w,rx,ry,x,y,start,rot} · bird{x0,x1,y0,y1,s} · flash{fi,fo,a,color} · lightcross{} · glitch{bg,tint,tint_a,text,split,x,y,size,font,weight,color} · glitter{fo,seed,band,n}

### 7.x greek-vase-epic (768x576 → 设计 1024x768)
赤陶橙底黑绘剪影 + 回纹饰带 + 黑色字幕条。elements: vase(底) · band(回纹) · sea{y} · cliff{side,w,seed} · ship{x,y,s} · figure{x,y,s,kind=warrior|woman,arm=spear|point|shield|bound|none,halo,helmet,red,face} · monster{x,y,n,len,reach[[t,0..1]],maw[x,y,s]} · whirl{x,y,r} · scale{x,y,tilt,left,right} · medal{x,y,r,inner} · island{x,y} · clouds{items[[x,y,s]]} · sun{x,y} · tag{x,y,gr,zh} · logcard{title,lines,note} · title{text,x,y,size}(描边) · sub{text,y,size}（`[关键词]` 橙色；双行分两个 sub，下行晚 0.3–0.5s）· tint · flash{t0,a}（同色切换处加 a=.5 白闪）。示例 examples/greek_icarus.json。
- dusk 跨日界线：`map.wrap:true` 时河流复制一份 +360°；地名/路线经度可写 >180（如纽约 286.06），地形瓦片本来就按 x%2^z 取，自动跨太平洋取景。大圆航线等曲线可在 build 脚本里算好点列传给 chain/faintroute 的 route（示例 output/plane-route/build.py）。
- BGM（所有风格）：music/ 下的 mp3 只是约 30 秒的识曲片段，旧 audio.py 用 `-stream_loop` 硬循环，每 30 秒会有一个接缝，听起来“一卡一卡”。现在 audio.py 会先探测时长：够长就直接截取，太短就用 acrossfade（`bgm.xfade`，默认 3 秒）交叉淡化拼接，并打印 WARNING。优先用完整曲目，例如 audio/7693296008339442986.wav（约 190 秒，开智小曲完整版）。librosa 缺失时会跳过 beats.json，不再中断。

#### dusk-map-chronicle v3：密集镜头扩展（2026-10，题材无关）
画面丰富度的依据见 `analysis/dusk-map-chronicle/richness.md`：参考片逐秒帧差中位数为 5.35，帧差大于 8 的变化每 10 秒约 3 次，且从不静止。用 `python scripts/density.py out.mp4 label` 自测，目标是中位数 ≥3，且不出现超过 1.5 秒的静止。
- **转场**：scene 字段 `tin:{type, dur, at:[x,y]}`。type 可选 `fade | zoom`（旧镜头放大穿越，新镜头从 0.6 放大进入）`| wipe`（斜向金色光带擦除，可选 skew）`| iris`（从 at 点圆形展开）`| flash`（白闪硬换）`| slide`。新场景的 t0 要比上一场的 t1 早 dur 秒（重叠段就是转场）。顶层 `fade_in` / `fade_out` 控制片头和片尾黑场。
- **相机**：map 场景支持 `cams:[[相对秒, cam | {fit…}], …]` 关键帧飞行（ease-in-out，缩放用对数插值）。master 地形按全部关键帧一次性渲染，单次缩放比建议 ≤5。`map.drift:1.04` 给所有静态镜头加慢推，`static:true` 可关掉；`pan:[dlon,dlat]`。
- **新底**（每种都会设置 ctx.proj，地名、路线元素通用）：
  - `globe`：正射地球仪，用 Natural Earth 国界陆地，带经纬网、暮色大气、3D 明暗。参数 `globe:{rot:[lon,lat], rot1, r, r1, c:[x,y], c1, spin(°/s), at, dur, grat, hl:[国家 NAME/NAME_ZH]}`。
  - `flat`：平面世界图，可从等距圆柱逐渐变成墨卡托。参数 `flat:{merc:0, merc1:1, merc_at, merc_dur, sx, sx1(每度像素), lon(中心经度), cy_lat, hl, grat, lat_labels}`。
  - `sky`：高度剖面，带地平线弧、漂移云层和高度标尺。参数 `sky:{alt_max, ground, top, ticks, band:[a0,a1,文字], band_at, cloud_v}`，可通过 ctx.alt(m) 换算出 y。
  - `dusk`：通用暮色地平线，供图标场景使用。参数 `dusk:{hy, top, mid, hz, ridge, glow}`。
- **新元素**（`route` 用地名或 [lon,lat]，`xy` 用屏幕坐标）：
  - `plane`：飞机图标。参数 route/xy, go_at, dur, ease(io|lin|out), s, trail(0–1 尾迹), side(侧视), tilt, label。
  - `windflow`：沿中心线流动的粒子流线。参数 route/xy, width, n, speed, trail, color, alpha, reverse, label。
  - `arrow`：可以逐段画出的箭头。参数 route/xy, draw_at, dur, dashed, color, text。
  - `kmring`：真实大地圆（半径 rkm 公里，在任何投影上都正确）。
  - `zone`：红色斜纹限制区。参数 poly 或 at+rkm。
  - `tissot`：等面积圆，墨卡托下会膨胀。
  - `panel`：数据卡片，带滑入动画和条形图。参数 rows=[{label, value, frac, color}]。
  - `tag`：引线标注框。
  - `borders`：真实国界，hl 中的国家依次描金。
  - `grat`：经纬网。
  - 常驻运动层：`motes`（金色微尘）、`cloudshade`（云影漂移）。
  - `chapter`：右上角章节号。
  - `topshade`：全局顶部压暗，配合 overlays 里的字幕使用。
  - 图标场景元素：`storm`（积雨云 + 闪电 + 雨）、`volcano`（火山锥 + 火山灰粒子）、`airport`（透视跑道 + 追逐灯 + 塔台）。
- **字幕**：推荐全部放进 `overlays`，跨镜头连续。下一屏的 t0 等于上一屏的 t1，字幕区不留空。
- **工具**：`scripts/density.py`（帧差密度）。示例脚本见 `output/plane-route/build_v3.py`（19 个场景，含 6 种转场、4 种底和全部新元素）。旧版 template 备份在 template_v2_backup.py。


---
## 8. 画面丰富度标准（全风格，2026-10）

详见独立文档 `skill/RICHNESS_STANDARD.md`（量化门槛、7 层镜头、转场 `tin`、BGM、交付清单）。
共享实现：`scripts/engine/richness.py`（`compose_scenes` / `motes` / `apply_ken_burns`）。
dusk-map-chronicle 已是 v3 标杆；下列为首批升级（v3 richness）：

### starry-matchmaking-graph v3
- `tin` 转场；`scene.kb` Ken Burns；新元素 `motes` `pulse` `counter` `chapter` `sparkline`。
- 字幕放 overlays 连续；连线用 sparkline 保持帧差。

### amber-bokeh-history v3
- `tin`；新元素 `chapter` `pour` `spark`；under 层 dust/bokeh 加强。

### teal-night-city-topdown v3
- `tin`；新元素 `cars` `blinkwin` `chapter` `motes`（解决最长静止段）。

### cosmic-particle-epic v3
- `tin`（段落用 flash）；新元素 `rain` `chapter` `motes`。

### gold-archive-history v3
- `tin`；`spark`/`chapter`；默认 bg.motes 90。

软降优先级（仍须满足清单备注）：bio-3d-microscope、pixel-rpg-dialogue、greek-vase-epic。
