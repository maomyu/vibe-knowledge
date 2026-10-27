# vibe-knowledge · vibe知识大赏（开源渲染器）

中文 | [English](#english)

用 **纯代码**（skia-python 逐帧 + ffmpeg）生成「vibe知识大赏」风格的知识短视频：  
**一个知识主题 + 30 种风格之一 + 你自己的 BGM** → 约 2 分钟竖屏/横屏成片（字幕、动效、节拍对齐）。

> **BGM 不随仓库提供。** 请使用你拥有授权的音轨。参考 Douyin 原片与「We Never Remix / 开智小曲」等曲目**不予分发**。详见 [`NOTICE.md`](NOTICE.md)。

许可证：[MIT](LICENSE) © 2026 [maomyu](https://github.com/maomyu)

---

## 快速开始

### 1. 依赖

```bash
# 系统
sudo apt-get install -y ffmpeg fonts-noto-cjk   # macOS: brew install ffmpeg

# Python 3.10+
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

### 2. 准备 BGM

将授权音轨放到例如 `audio/your-licensed-bgm.wav`（需自行创建 `audio/` 目录）。

### 3. 渲染一条示例风格

```bash
# 编辑 examples/entropy_stardust.json 里的 bgm.src 指向你的音轨后：
python scripts/pipeline.py build examples/entropy_stardust.json -o /tmp/entropy.mp4
```

或分步：

```bash
python scripts/audio.py examples/entropy_stardust.json
python scripts/render.py examples/entropy_stardust.json -o /tmp/entropy.mp4
python scripts/density.py /tmp/entropy.mp4 demo
```

生成 LLM 写稿提示词：

```bash
python scripts/pipeline.py prompt --style stardust-timeline --topic "熵"
```

### 4. 文档

| 文档 | 内容 |
|---|---|
| [`SKILL.md`](SKILL.md) | 制作约定：零静止、主字幕唯一、anti-strobe、验收口诀 |
| [`TEMPLATE_GUIDE.md`](TEMPLATE_GUIDE.md) | 各风格 `script.json` 字段与元素类型 |
| [`RICHNESS_STANDARD.md`](RICHNESS_STANDARD.md) | 画面丰富度、转场、音乐锁、密度门槛 |
| [`styles/STYLES.md`](styles/STYLES.md) | 30 风格视觉说明（含研究用参考链接，不含原片） |
| [`NOTICE.md`](NOTICE.md) | BGM / 字体 / 地理数据许可 |

风格元数据：[`styles/styles.json`](styles/styles.json)（根目录有同步副本供 `pipeline.py` 读取）。

---

## 30 种风格

| # | 中文名 | English | slug |
|---|---|---|---|
| 1 | 星尘时间轴 | Stardust Timeline | `stardust-timeline` |
| 2 | 金线分形·竖屏 | Golden Fractal Vertical | `golden-fractal-vertical` |
| 3 | 暮色地图史话 | Dusk Map Chronicle | `dusk-map-chronicle` |
| 4 | 暗室微光 | Dim Room Candlelight | `dim-room-candle` |
| 5 | 鎏金年代档案 | Gilded Era Archive | `gold-archive-history` |
| 6 | 剪影舞台·信纸 | Silhouette Stage & Paper | `silhouette-stage-paper` |
| 7 | 雷暴倒计时·竖屏 | Storm Countdown Vertical | `storm-countdown-vertical` |
| 8 | 暗金仪表盘 | Bronze HUD Instruments | `bronze-hud-instrument` |
| 9 | 白线涂鸦寓言 | White Line Doodle Fable | `white-line-doodle` |
| 10 | 俯瞰夜城·青蓝 | Top-down Teal Night City | `teal-night-city-topdown` |
| 11 | 宇宙粒子大片 | Cosmic Particle Epic | `cosmic-particle-epic` |
| 12 | 扁平卡通情景剧 | Flat Cartoon Sitcom | `flat-cartoon-situation` |
| 13 | 星空配对图谱 | Starry Matching Graph | `starry-matchmaking-graph` |
| 14 | 心电霓虹 | Neon Heart Pulse | `neon-heart-pulse` |
| 15 | 乐理可视化仪表 | Music Theory Visualizer | `music-theory-visualizer` |
| 16 | 金杯光影剧场 | Golden Chalice Cinema | `golden-cup-cinema` |
| 17 | 3D生物显微 | 3D Bio Microscope | `bio-3d-microscope` |
| 18 | 赛博霓虹图标 | Cyber Neon Icons | `cyber-neon-icons` |
| 19 | 红色警报·荧光绿 | Red Alert to Lime | `red-alert-lime` |
| 20 | 琥珀散景文明史 | Amber Bokeh Civilization | `amber-bokeh-history` |
| 21 | 草原剪影·竖屏 | Savanna Silhouette Vertical | `savanna-silhouette-vertical` |
| 22 | 像素RPG对话 | Pixel RPG Dialogue | `pixel-rpg-dialogue` |
| 23 | 剪影演化史 | Evolution Silhouette Saga | `evolution-silhouette` |
| 24 | 霓虹光环侧影 | Neon Halo Profile | `neon-halo-profile` |
| 25 | 节拍拆解·竖屏 | Beat Breakdown Vertical | `beat-breakdown-vertical` |
| 26 | 器官信息卡 | Organ Infographic Cards | `organ-infocard-dark` |
| 27 | 黑板教室数据 | Chalkboard Classroom Data | `chalkboard-classroom` |
| 28 | 宣纸水墨字效 | Ink Paper Typography | `ink-paper-typography` |
| 29 | 希腊陶绘史诗 | Greek Vase Epic | `greek-vase-epic` |
| 30 | 灰阶终端数据 | Terminal Grayscale Data | `terminal-gray-data` |

预览图：`styles/<slug>.jpg`。

---

## 目录结构

```
templates/<slug>/template.py   # 30 个风格渲染模板
scripts/                       # render / audio / pipeline / density / engine/
styles/                        # styles.json + STYLES.md + 预览图
assets/fonts|geo|tex           # OFL 字体、Natural Earth / DEM 缓存、纹理
examples/*.json                # 小体积示例脚本（无成片、无 BGM）
```

---

## 设计硬约束（摘要）

- **零静止**：每帧有运动；`density.py` 最长静止目标 0s。
- **主字幕唯一**：同一画面只留一条高对比主字幕。
- **一文一动**：每句字幕对应可见动作；7+ 层；1–2s 一事件。
- **Anti-strobe**：默认 `beat_punch:false`；禁止全片 beatflash。
- **音乐锁**：高潮/转折处必须有切镜、相机、粒子或字幕换段。

---

<a id="english"></a>
## English

**vibe-knowledge** is an open-source, code-only renderer for short knowledge videos in 30 curated visual styles (inspired by the Douyin “vibe知识大赏” aesthetic).

Give it a topic, pick a style slug, supply **your own licensed BGM**, and render ~2 minutes of skia→ffmpeg video with captions and motion locked to structure—not a browser capture, not an img2video pipeline.

### Install

```bash
sudo apt-get install -y ffmpeg fonts-noto-cjk
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

### Render

1. Point `bgm.src` in an example JSON (or your script) at a licensed track under e.g. `audio/your-licensed-bgm.wav`.
2. `python scripts/pipeline.py build examples/entropy_stardust.json -o /tmp/out.mp4`

### Docs

- [`TEMPLATE_GUIDE.md`](TEMPLATE_GUIDE.md) — script schema per style  
- [`RICHNESS_STANDARD.md`](RICHNESS_STANDARD.md) — density / anti-strobe / music-lock QA  
- [`SKILL.md`](SKILL.md) — production rules  
- [`NOTICE.md`](NOTICE.md) — **BGM not included**; font & geo attributions  

#
## Demo clips（开源宣传案例）

短片在 [`examples/x-promo/`](examples/x-promo/)（约 20–30 秒，可直接挂 X Articles）：

| 文件 | 说明 |
|------|------|
| `montage_vibe30styles_28s.mp4` | 30 风格混剪总览 · ~28s |
| `clip_flat-cartoon-situation_spotlight.mp4` | 聚光灯效应 |
| `clip_golden-cup-cinema_commitment.mp4` | 承诺升级 |
| `clip_golden-fractal-vertical_generational.mp4` | 代际循环 |
| `clip_neon-halo-profile_halo.mp4` | 光环效应 |
| `clip_storm-countdown-vertical_scarcity.mp4` | 稀缺效应 |

完整约 2 分钟成片不进仓（体积）。**完整 BGM 母带不随仓分发**（见 `audio/README.md`）。

宣传长文草稿：[`docs/X_PROMO_ARTICLE_CN.md`](docs/X_PROMO_ARTICLE_CN.md) / [`docs/X_PROMO_ARTICLE_EN.md`](docs/X_PROMO_ARTICLE_EN.md)。

## License

MIT © 2026 [maomyu](https://github.com/maomyu). Third-party fonts (OFL), Natural Earth (public domain), DataV provinces & AWS Terrarium tiles: see `NOTICE.md`. Reference Douyin videos/audio are **not** redistributed.
