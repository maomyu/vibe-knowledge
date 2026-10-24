# 画面丰富度标准（所有 vibe知识 风格强制）

依据：dusk-map-chronicle 模板 v3 与实测密度基线。
测量：`python scripts/density.py <video.mp4> <label>`（1fps 灰度帧差）。

## 1. 量化门槛（交付前自检）

| 指标 | 目标 | 说明 |
|---|---|---|
| 逐秒帧差中位数 | **接近该风格参考中位数**（通常 ≥3；dusk 参考 5.35） | 低于参考 50% 视为不合格 |
| 大变化（帧差>8）/10s | ≥ 参考的 ~60% | 不能只靠偶尔硬切凑数 |
| 最长静止段（连续帧差<0.6） | **≤2–3 秒** | 0 秒最佳；>3s 必须修 |
| 硬切 | 按风格参考；多数用叠化/推拉 | 白闪仅用于段落切换 |

> 不是“多切几刀”，而是**同一镜头内每 1–2 秒长出新东西或在动**。

## 2. 每镜 ~7 层（自下而上，缺层要补）

1. **底** — 可轮换的背景（纹理/地图/天空/舞台…），同底少连续超过 2 场  
2. **数据/路线层** — 生长线、点亮链、计数、图表  
3. **道具/图标** — 程序化物件、人物剪影、徽章  
4. **叠加 UI** — 章节号、面板、时间轴、HUD  
5. **字幕** — 旁白/金句；**字幕区从不空**（overlays 跨镜衔接）  
6. **光效** — 辉光、暗角、颗粒、闪烁、尘点  
7. **相机** — Ken Burns / 推拉 / 平移；默认慢推，可用 `static:true` 关  

## 3. 节奏

- 新视觉事件（元素出现、计数跳变、点亮、机位到位、换底）约 **每 1–2 秒一次**，3 秒内必有一次。  
- 旁白一句 ≈ 一个视觉事件；关键词出现时画面同步出现对应物。  
- 常驻运动层（微尘、星闪、云影、粒子流、火焰）全程开着，防止“静帧感”。

## 4. 转场（`scene.tin`）

场景时间可重叠 `dur` 秒；重叠段即转场。

| type | 用途 |
|---|---|
| `fade` | 默认叠化 |
| `zoom` | 旧镜放大穿越，新镜从 0.6 放大进入（`at:[x,y]`） |
| `wipe` | 斜向光带擦除（`skew`、色随风格） |
| `iris` | 从 `at` 圆形展开 |
| `flash` | 白/暖闪硬换（段落） |
| `slide` | 横向滑入 |

实现：优先用 `engine.richness.compose_scenes`（或各模板等价逻辑）。旧字段 `xin`/`xfade` 仍可当 fade。

## 5. BGM

- 请自备完整授权 BGM（建议 ≥ 成片时长，如 ~190s）；短轨会被 `audio.py` 用 acrossfade 拼接并发 WARNING。  
- `audio.py`：够长则 trim；太短则 `acrossfade`（`bgm.xfade` 默认 3s）并 WARNING。  
- 禁止听感上的硬循环接缝；全片连续 BGM + 片尾 fade_out。

## 6. 模板约束

- **纯代码渲染**（skia + ffmpeg），不录网页、不用 img2video。  
- **题材无关**：文字/数字/地名/坐标全部来自 `script.json`。  
- 升级模板时备份旧版为 `template_vN_backup.py`（可选），在 `TEMPLATE_GUIDE.md` §7 写 vN 扩展说明。

## 7. 交付清单（每个风格 / 每条成片）

- [ ] `density.py` 对成片跑过，中位数接近参考、静止 ≤3s  
- [ ] 抽 4–6 张静帧：无空字幕、无长时间静底、无文字溢出  
- [ ] 转场不全是硬切；至少用到 2 种 `tin`（或风格参考允许的集合）  
- [ ] 每镜可见 ≥5 层（底+数据/道具+字幕+光效+相机/运动）  
- [ ] BGM 来自完整轨或 crossfade，无 30s 卡点  
- [ ] 自留 density 数字 / contact sheet 作为验收证明

## 8. 工具

```bash
# 密度
.venv/bin/python scripts/density.py out.mp4 label
# 对照条带
.venv/bin/python scripts/compare.py ref.mp4 remake.mp4 outdir --excerpt a,b
# 共享转场/尘点
from engine.richness import compose_scenes, motes, apply_ken_burns
```

软降优先级（3D/插画重，仍须满足清单备注）：`bio-3d-microscope`、`pixel-rpg-dialogue`、`greek-vase-epic`。

## 9. 卡点与 Anti-strobe（强制）

全屏闪 = 观感失败。batch-1 v2 因 `beat_punch`（punch_a 0.28–0.42）+ 全程 `beatflash` overlay，在 ~112 BPM 下整屏刷色，用户反馈「一闪一闪」。

- [ ] 默认 `beat_punch: false`；若开，`punch_a ≤ 0.05` 且不要再叠 beatflash
- [ ] script 里**不要**放覆盖全片的 `type: beatflash`
- [ ] 卡点用局部：字幕/场景 snap 到 `beats.json`、pulse、sparkline、counter、beatrings、motes 起伏
- [ ] 交付前抽检：短窗帧差不应出现每拍一次的全屏尖峰
- [ ] density 略低于参考时，加层/加事件补，**禁止**用全屏闪灌水抬数字

## 10. 音乐结构锁定（强制）

高潮 / drop / 停顿 / 旋律转折处，画面必须有对应变化（切镜、相机 push、粒子或数据爆发、字幕换段、转场加重）。字幕与场景边界尽量 snap 到拍。仍禁止用全屏 beat_punch/beatflash 假装卡点。

## 11. 文案可视化（最高标准）

屏上文字提到的物品、地点、角色、数据、过程，同一拍内要有对应图形/道具/地图/示意图。写 script 时做 caption→elements 映射；禁止长时间「只有字在空底上」。静音看片仍应大致读懂内容。

## 12. 一文一动与抬档密度（batch-3+）

文案目标约 520–580 字/约 2 分钟。每一句字幕必须伴随可见动作（生长、弹出、位移、变形、计数、相机），禁止静态图标搪塞。整体要比 batch-1/2 更密、更吸睛、更丝滑。

## 13. 零静止与主字幕唯一

全程逐帧变化：常驻运动 + Ken Burns + 微动；`density.py` 最长静止目标 0s。同一画面只保留一条主字幕（大、清楚）；次要文案删除或降到角落，禁止叠字抢位。
