[English](README.en.md) | 简体中文

# Copymunk 定稿：04 鼓腮小开心

维护者选择第三轮的 04，本轮将它整理为供接入的完整图标资产。**选中的 macOS 主图形状、五官、渐变、腮红、阴影和暖底全部保留**；`sources/macos.svg` 与第三轮 `04-delight/source.svg` 字节一致。另行完成 16／32px 光学稿、iOS 三种外观和菜单栏模板。

先看 [定稿总览](overview.png)、[原生尺寸 contact sheet](contact-sheet.png)、[小尺寸对比](previews/optical-review.png)。完整绘制规范见 [copymunk-icon-spec.md](copymunk-icon-spec.md)。

## 改了什么

- **底色保留原样。** 尝试把 `#FFD7A5 → #F2AE78` 微调为 `#FFD3AF → #EFA888`，大图分离略好，64／32px 改善不明显，按简报不采用。保留 [原稿](comparisons/before-1024.png)、[改色试稿](comparisons/after-1024.png) 和 [并排比较](comparisons/background-comparison.png)。后者是未采用的试验，接入请用 `appiconset/`。
- **16px、32px 独立手工光学稿。** 在目标坐标系重排眼睛、高光及鼻嘴间距；16px 去掉细牙、副高光与侧纹，保留圆亮眼、奶油鼓腮和开心开口。32px 保留小门牙，两个 32px 槽共用同一份 PNG。抗锯齿从各自目标 SVG 渲染，未经过 1024 母版。
- **64px 保留母版缩图。** 原尺寸与放大检查中，圆眼、高光、鼻口与鼓腮可辨，没有另作光学稿；128px 及以上继续使用选中主图。
- **iOS 三种外观保持同一脸部几何。** 浅色沿用原色；深色使用暖深棕背景并温和压暗毛色、奶油腮；着色稿以手工灰阶分离脸、腮、眼口和高光，背景透明。
- **菜单栏提炼为小圆耳与鼓腮剪影。** 18／36px 使用黑色与透明的整像素稿，浅深环境由模板反色展示。详见 [像素规则](sources/menubar-notes.md) 和 [菜单栏模拟](previews/menubar-simulation.png)。

## Xcode 槽位对应

`appiconset/` 对应 `Copyo/Assets.xcassets/AppIcon.appiconset/`：

| 交付文件 | Xcode size / scale | 实际像素 | 来源 |
| --- | --- | --- | --- |
| `icon_16x16.png` | 16×16 / 1x | 16 | 独立 16 光学稿 |
| `icon_16x16@2x.png` | 16×16 / 2x | 32 | 独立 32 光学稿 |
| `icon_32x32.png` | 32×32 / 1x | 32 | 与上一张字节一致 |
| `icon_32x32@2x.png` | 32×32 / 2x | 64 | 母版缩图 |
| `icon_128x128.png` | 128×128 / 1x | 128 | 母版缩图 |
| `icon_128x128@2x.png` | 128×128 / 2x | 256 | 母版缩图 |
| `icon_256x256.png` | 256×256 / 1x | 256 | 母版缩图 |
| `icon_256x256@2x.png` | 256×256 / 2x | 512 | 母版缩图 |
| `icon_512x512.png` | 512×512 / 1x | 512 | 母版缩图 |
| `icon_512x512@2x.png` | 512×512 / 2x | 1024 | 选中母版 |

全部为 RGBA，透明外底。1024 方块 x/y=100.352、宽高=823.296、圆角=229.0688，遵循原规范。16／32 的外框比例相同，脸部按目标像素重新绘制。

`ios-appiconset/` 对应 `CopyoIOS/Assets.xcassets/AppIcon.appiconset/`：

| 交付文件 | 外观槽位 | 格式 |
| --- | --- | --- |
| `AppIcon.png` | 默认 / Light | 1024×1024 RGB，不透明、满幅、无 alpha、无预制圆角 |
| `AppIcon-Dark.png` | luminosity / dark | 1024×1024 RGB，不透明、满幅、无 alpha、无预制圆角 |
| `AppIcon-Tinted.png` | luminosity / tinted | 1024×1024 RGBA，透明底、手工灰度，所有像素 R=G=B |

这遵循已读取的 `scripts/make-icon.sh --ios` 通道约定；Tinted 是刻意设计的灰阶稿，未使用自动灰化或自带不透明灰底。SVG 中不烘焙 iOS 圆角，展示图才添加近似系统连续圆角蒙版。

`menubar/` 对应 `Copyo/Assets.xcassets/MenuBarIcon.imageset/`：

| 交付文件 | Xcode scale | 格式 |
| --- | --- | --- |
| `menubar-template-18.png` | 1x | 18×18 RGBA，RGB 全黑，alpha 仅 0／255 |
| `menubar-template-36.png` | 2x | 36×36 RGBA，RGB 全黑，alpha 仅 0／255 |

三个交付子目录都附有对应的 `Contents.json`，保留当前资产目录的槽位声明；菜单栏声明 `template-rendering-intent: template`。本次没有安装资产或改变代码中的加载方式。

## 源文件与重新生成

- `sources/macos.svg`：最终 macOS 母版；`macos-original.svg` 是选中原稿留档。
- `sources/macos-optical-16.svg`、`macos-optical-32.svg`：目标尺寸可编辑矢量稿。
- `sources/ios-light.svg`、`ios-dark.svg`、`ios-tinted.svg`：可编辑 iOS 源文件。
- `sources/menubar.py`：菜单栏整像素源；同时生成对应 SVG、PNG 和菜单栏模拟。
- `sources/sRGB.icc`：固定 sRGB 配置，供重复生成保持一致。
- `render.py`：只向本交付目录输出，不调用现有 `scripts/make-icon.sh`，不安装资产。

环境：Python 3.9+、Pillow 11.3.0、resvg-py 0.3.2。预览文字依赖 macOS `/System/Library/Fonts/Supplemental/Arial Unicode.ttf`，图标本身没有字体依赖。

```bash
cd art/app-icon-exploration/2026-10-15-copymunk-final
python3 -m pip install --user Pillow==11.3.0 resvg-py==0.3.2
python3 render.py
```

默认从已交付 SVG 和菜单栏像素源重建全部 PNG、对比图、模拟图、检查报告及清单。1024 母版使用 4 倍超采样加 BOX；16／32 使用目标坐标 SVG 的 8 倍抗锯齿加 BOX；64 及以上从母版 LANCZOS 降采样。菜单栏不做超采样或缩图。

若将来主动修改 macOS 主图并希望重新派生三份 iOS SVG，可先运行 `python3 render.py --only sources`。这会按脚本中的 `DARK`／`TINTED` 调色板覆盖 iOS SVG，独立编辑过 iOS 源时不要运行此选项。也支持 `--only render`、`--only sheets`、`--only audit`、`--only manifest`。不要用旧 `make-icon.sh` 覆盖本轮 16／32 光学稿。

## 预览与检查

- [contact-sheet.png](contact-sheet.png)：所有 10 个 macOS 槽位按原生像素嵌入，浅深各一行；iOS 三种外观按 320px 连续圆角示意，菜单栏为原生 18／36px。请以 100% 缩放检查小图。
- [Dock 模拟](previews/dock-simulation.png)、[App Store 搜索结果模拟](previews/app-store-search-simulation.png)：浅深两种环境的布局和比例检查，均非运行或商店截图。
- [optical-review.png](previews/optical-review.png)：16／32／64 原尺寸与最近邻放大，和直接缩图并排比较。
- `qa-report.json`：15 张接入 PNG 的尺寸、通道与 alpha，两个 32px 槽一致，20 个 macOS contact 样本像素一致，选中源文件一致，以及 187 个受保护输入文件的哈希检查。
- `manifest.json`：本交付文件的 SHA-256。
- `reproducibility-report.json`：本次定稿的 15 张接入 PNG 已重复生成，两次 SHA-256 全部一致。

本轮已在浅深背景检查 16／32／64px、菜单栏原尺寸和各平台预览。16px 无法保留细牙与完整物种条纹，优先保证圆眼、鼓腮和开心感；暖底与毛色仍是相近色，这是保留维护者所选风格的结果。

**接入状态：已接入（2026-10-15）。** 15 张 PNG 由 `scripts/make-icon.sh` 复制进 `Copyo/Assets.xcassets/AppIcon.appiconset`、`CopyoIOS/Assets.xcassets/AppIcon.appiconset` 与 `Copyo/Assets.xcassets/MenuBarIcon.imageset`（`--check` 只比对），macOS 与 iOS 模拟器均已编译通过。iOS 连续圆角和 Tinted 背景仍是预览近似，深色 / 着色外观与 18px 菜单栏图标还需在真机上确认。
