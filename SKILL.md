---
name: vibe知识视频
description: 用户给一个知识主题、选 vibe知识大赏 30 种风格之一，要纯代码渲染一条带统一 BGM 的知识短视频时使用。
---
项目在 `/workspace/vibe-knowledge/`。模板 `skill/templates/<slug>/template.py`，风格 `styles/styles.json`，schema 见 `skill/TEMPLATE_GUIDE.md`，丰富度见 `skill/RICHNESS_STANDARD.md`（含 §14 底部字幕节奏）。

## 硬性约定

- 新选题；先审后渲；~115–130s；屏上约 **520–580** 字；无品牌；无口播。
- 交付：文件 + Drive `1sSejhnWDSuokZQ2hFJeimViPc_cLCF96`。

## 零静止（极重要）

**每一帧都要在变**：常驻运动层（motes/粒子/尘/星/车流）、Ken Burns、数据/指针微动、背景呼吸。禁止「只有字停在静底上」。`density.py` 最长静止目标 **0s**（绝对上限 ≤0.5s）。

## 字幕层级（极重要）

同一拍/同一画面：**只留一条主字幕**（大、高对比、可读）。次要信息删除，或降为角落小标签/低透明度，绝不与主句抢位、叠字。写 script 时每段指定 `primary` caption；多余 overlay 文案砍掉。

## 底部字幕节奏（极重要）

对照原片（一句接一句循序读完，非贴拍碎切）与 `white-line-doodle` caption fix。

- 底栏 **primary 唯一流**；与画面大字/卡片**错峰或呼应**，同一句不要底栏+大字双堆。
- 每条 primary **≥2.0s**，目标 med **2.5–3.5s**；约 **4–5 汉字/秒**；句间软间隙 0.1–0.3s。
- **可读优先于贴拍**；禁止 0.3s 碎片；宁少句、句更长。
- 自检 min/med/<2s 计数与 CJK≈520–580。详见 `RICHNESS_STANDARD.md` §14。

## 一文一动 + 丰富丝滑

每句主字幕对应可见动作；7+ 层；事件跟字幕节奏走（勿为密而碎切字幕）；`tin`≥2；continuous build-up。

## 音乐锁 + Anti-strobe

高潮/转折=切镜/相机/粒子/字幕换段。默认 `beat_punch:false`；禁全程 beatflash / punch_a>0.05。完整 BGM `audio/7693296008339442986.wav`。

## 步骤

1. 选题文案先过用户。 2. 读 guide+examples+RICHNESS（含 §14）；标 accents。 3. script：一文一动、主字幕唯一、底栏可读节奏、零静止、高潮对齐。 4. 纯代码渲。 5. 自检 density/静止=0、字幕 min≥2s、无闪、音乐锁。 6. 交付。

软降：`bio-3d-microscope`、`pixel-rpg-dialogue`、`greek-vase-epic`。

## 验收口诀

零静止 · 主字幕唯一清楚 · 底栏≥2s循序可读 · 一文一动 · 密而丝滑 · 高潮锁画面 · 不闪屏 · ~2min/520–580字 · 无品牌 · density · 完整BGM · 文件+Drive。
