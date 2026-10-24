# NOTICE / 第三方与素材说明

## BGM（重要）

本仓库**不包含**任何背景音乐文件。

参考风格分析中提到的 Douyin /「We Never (Remix)」/「开智小曲」等曲目**仅作研究备注，不予分发**。  
渲染前请自行准备已获授权的音频，例如：

```json
"bgm": { "src": "audio/your-licensed-bgm.wav", "fade_out": 1.5 }
```

将文件放到工程内任意相对路径，并在 `script.json` 的 `bgm.src` 中指向它。`scripts/audio.py` 会按成片时长裁剪或 acrossfade 拼接。

## 参考视频

原 Douyin「vibe知识大赏」类参考片**未收录**于本仓库（无 `videos/`、`frames/`、`tests/` 大体积复刻产物）。`styles/STYLES.md` 中的链接仅供风格对照。

## 字体（随仓库分发）

`assets/fonts/` 均为 Google Fonts，**SIL Open Font License 1.1 (OFL)**：

| 文件 | 字体 | 许可 |
|---|---|---|
| NotoSerifSC-VF.ttf | Noto Serif SC | OFL-1.1 |
| EBGaramond-VF.ttf / EBGaramond-Italic-VF.ttf | EB Garamond | OFL-1.1 |
| MaShanZheng-Regular.ttf | 马善政 | OFL-1.1 |
| ZhiMangXing-Regular.ttf | 志莽行 | OFL-1.1 |
| LiuJianMaoCao-Regular.ttf | 刘建毛草 | OFL-1.1 |

完整 OFL 文本见：https://openfontlicense.org/  
系统回退字体（可选）：`fonts-noto-cjk`（Debian/Ubuntu 包），不随本仓库分发。

## 地理数据

| 路径 | 来源 | 说明 |
|---|---|---|
| `assets/geo/countries_50m.geojson` | Natural Earth 50m admin_0 | 公有领域 |
| `assets/geo/rivers_50m.geojson` | Natural Earth 50m rivers | 公有领域 |
| `assets/geo/china_provinces.json` | 阿里云 DataV.GeoAtlas（省级） | **商用前请自行核实授权**；国界/南海相关正式发布须遵守当地地图法规 |
| `assets/geo/tiles/*.png` | AWS Terrain Tiles（Terrarium 编码高程） | 开源地形镶嵌缓存，用于 dusk-map 等 DEM 阴影；使用时保留 AWS / 源数据归因 |

`scripts/engine/terrain.py` 可在缺瓦片时从 `elevation-tiles-prod` 自动补拉。

## 纹理

`assets/tex/paper_fiber.png`：程序/生成用纸纤维贴图，随模板 procedural 回退使用。

## 本软件许可

代码与模板：见根目录 `LICENSE`（MIT © 2026 maomyu）。
