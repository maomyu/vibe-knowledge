---
name: vibe-knowledge
description: 用户给一个知识主题、选 vibe知识大赏 30 种风格之一，要纯代码渲染一条带统一 BGM 的知识短视频时使用。
---

# vibe知识 / vibe-knowledge

纯代码（skia-python + ffmpeg）渲染知识短视频：选题 + 30 种风格之一 + 用户自备 BGM → 约 2 分钟成片。

## 路径（相对本仓库根目录）

| 内容 | 路径 |
|---|---|
| 风格模板 | `templates/<slug>/template.py` |
| 风格元数据 | `styles/styles.json`（`pipeline.py` 亦读取根目录 `styles.json` 副本） |
| Schema / 字段 | `TEMPLATE_GUIDE.md` |
| 丰富度与验收 | `RICHNESS_STANDARD.md` |
| 示例脚本 | `examples/*.json` |
| 渲染入口 | `scripts/pipeline.py` / `scripts/render.py` / `scripts/audio.py` |
| 密度自检 | `scripts/density.py` |

## 硬性约定

- 新选题；先审文案后渲染；成片约 **115–130s**；屏上约 **520–580** 字；无品牌水印；默认无口播（可选用 edge-tts）。
- **BGM 须由用户自行提供授权曲目**（本仓库不附带任何音乐文件）。见 `NOTICE.md`。

## 零静止（极重要）

**每一帧都要在变**：常驻运动层（motes/粒子/尘/星/车流）、Ken Burns、数据/指针微动、背景呼吸。禁止「只有字停在静底上」。`density.py` 最长静止目标 **0s**（绝对上限 ≤0.5s）。

## 字幕层级（极重要）

同一拍/同一画面：**只留一条主字幕**（大、高对比、可读）。次要信息删除，或降为角落小标签/低透明度，绝不与主句抢位、叠字。写 script 时每段指定 `primary` caption；多余 overlay 文案砍掉。

## 一文一动 + 丰富丝滑

每句主字幕对应可见动作；7+ 层；1–2s 一事件；`tin`≥2；continuous build-up。详见 `RICHNESS_STANDARD.md`。

## 音乐锁 + Anti-strobe

高潮/转折 = 切镜/相机/粒子/字幕换段。默认 `beat_punch: false`；禁全程 beatflash / `punch_a>0.05`。

## 推荐步骤

1. 选题文案先过用户确认。
2. 读 `TEMPLATE_GUIDE.md` + `examples/` + `RICHNESS_STANDARD.md`；标 accents。
3. 写 `script.json`：一文一动、主字幕唯一、零静止、高潮对齐拍点。
4. 放入自备 BGM，设置 `bgm.src`。
5. 纯代码渲染：`python scripts/pipeline.py build script.json -o out.mp4`
6. 自检：`density.py` 静止≈0、字幕清晰、无闪屏、音乐结构锁定。

软降（3D/插画重，仍须满足清单）：`bio-3d-microscope`、`pixel-rpg-dialogue`、`greek-vase-epic`。

## 验收口诀

零静止 · 主字幕唯一清楚 · 一文一动 · 密而丝滑 · 高潮锁画面 · 不闪屏 · ~2min/520–580字 · 无品牌 · density · 自备完整 BGM。
