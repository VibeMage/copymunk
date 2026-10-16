# Copymunk

[English](README.en.md)

Copymunk 是一款开源的剪贴板管理工具，支持 Mac、iPhone 和 iPad。Mac 上菜单栏常驻，`⇧⌘V` 唤出悬浮卡片面板，历史即输即搜；
iPhone 和 iPad 上通过你自己的 iCloud 查看、搜索 Mac 上复制过的内容，也能随手存下新的。官网：[copymunk.com](https://copymunk.com)

Mac 版数据默认只保存在本机（`~/Library/Application Support/Copyo/`），同步默认关闭；不含任何第三方 SDK、统计或崩溃上报，适合不允许安装第三方闭源工具的办公环境。

## 功能

### Mac

- **剪贴板历史**：后台自动记录复制过的内容——纯文本、富文本、链接、颜色（`#RRGGBB`）、图片、文件
- **悬浮面板**：按 `⇧⌘V` 在屏幕底部、Dock 上方浮出一块玻璃面板，横向卡片流展示历史；卡片整卡淡染来源应用的颜色
- **即输即搜**：面板打开后直接键入即可过滤历史，支持按内容、文件名、来源应用搜索
- **键盘优先**：`← →` 导航、`⇥` 切换筛选、`↩` 复制并回到之前的应用、`⇧↩` 以纯文本复制、`⌘1–9` 直接复制第 N 张、`空格` 预览、`⌘P` 固定、`⌘⌫` 删除、`Esc` 关闭
- **筛选与 Pinboard**：按 全部 / 文本 / 链接 / 图片 / 颜色 / 文件 筛选；把常用内容固定到自定义分组，不受历史上限清理影响
- **来源应用标识**：卡片带类型角标、来源应用图标与「来源 · 时间」；颜色条目用内容本身的颜色
- **拖拽**：卡片可直接拖出到任何应用
- **隐私保护**：自动跳过密码管理器等标记为 Concealed/Transient 的内容；可在设置里选出不记录的应用
- **同步（可选，三选一）**：关闭 / 文件夹 / iCloud。文件夹方式把历史与 Pinboard 写成快照放进 iCloud Drive
  或任意多设备都能读写的目录（公司 NAS、网盘同步目录等），**不传播删除**——一台 Mac 上删掉的条目在其他 Mac
  上依然保留；iCloud 方式经你自己的 iCloud 私有数据库同步，增删改全量生效，**删除会在所有设备上同时消失**。
  两种方式的数据都只经过你自己的存储，默认关闭（公司环境可保持完全离线）
- **自定义快捷键**：默认 `⇧⌘V`，可在设置中录制任意组合键
- **历史上限**：100/300/500/1000/无限制，超限自动清理最旧的未固定记录
- **开机自启**、隐藏菜单栏图标、暂停记录、纯文本模式等设置
- **多语言界面**：跟随系统语言，共 18 种（简体中文 / 繁體中文 / English / Français / Deutsch / Español / Italiano / Português (Brasil) / Nederlands / Polski / Русский / Türkçe / 日本語 / 한국어 / ไทย / Tiếng Việt / Bahasa Indonesia / العربية，阿拉伯语按从右到左排版），基于 String Catalog

### iPhone 与 iPad

iOS 不允许 App 在后台读取剪贴板，所以 iPhone 和 iPad 版在你选定的时机保存：

- **与 Mac 同步**：iCloud 同步默认开启，Mac 上选「iCloud」同步后，复制的内容会自己出现在手机上
- **打开时保存**：每次打开或回到 Copymunk 都会读取剪贴板并保存新内容（可关闭，改用系统「粘贴」按钮手动保存）
- **分享面板**：在任意 App 里选中文本、链接或图片，分享到 Copymunk，可顺手固定到 Pinboard
- **一键保存**：按住操作按钮、点控制中心或锁屏上的控件，或者用「轻点背面」
- **小组件与快捷指令**：主屏幕「最近的内容」小组件，快捷指令和 Siri 里的「保存剪贴板」
- **卡片操作**：轻点复制，右滑固定，左滑删除，长按更多
- **iPad**：侧栏加卡片网格，可把卡片拖到其他 App，支持硬件键盘快捷键

## 安装

- **Mac、iPhone、iPad**：[App Store](https://apps.apple.com/app/id6813955206)，免费，三端通用（同一条 App Store 记录）。Mac 需 macOS 14+，iPhone 和 iPad 需 iOS / iPadOS 18+
- **Mac 直接下载版**：[下载 DMG](https://github.com/VibeMage/copymunk/releases/latest/download/Copymunk.dmg)（各版本见 [Releases](https://github.com/VibeMage/copymunk/releases)），打开后把 Copymunk
拖进 Applications 即可。官方发布均已使用 Developer ID 签名并通过 Apple 公证——双击即可打开，
仅首次有一次「从互联网下载的 App」标准确认弹窗。

## 从源码构建

需要 Xcode 16+、macOS 14+。

```bash
git clone https://github.com/VibeMage/copymunk.git && cd copymunk
xcodebuild -project Copyo.xcodeproj -scheme Copyo -configuration Release -derivedDataPath build build
open build/Build/Products/Release/Copymunk.app   # 或拷贝到 /Applications
```

也可以直接用 Xcode 打开 `Copyo.xcodeproj` 运行（⌘R）。

### 本机日常用最新版（维护者）

```bash
./scripts/install-local.sh   # 编 Release → 替换 /Applications/Copyo.app → 重启
```

装的是直分发版（非沙盒），读 `~/Library/Application Support/Copyo/` 那份日常历史；用 Apple Development
证书签名，iCloud 同步可用（需要 Xcode 里已登录团队账号）。旧版备份在 `build.noindex/install/previous/`。
`/Applications` 里是商店版时脚本会先停下，删掉商店版再跑。它只退出 `/Applications` 那一份 Copymunk，
Debug 构建等其他实例不碰，只提示它们还在跑（会和新装的抢 ⇧⌘V）。
本机只留 `/Applications` 这一份：构建目录放在 `build.noindex/`（Spotlight 不索引），装完把构建产物从
LaunchServices 注销，「打开方式」里不会冒出一排开发版。商店包要验证时走 TestFlight。

iOS / iPadOS 版在同一个工程里（scheme `Copyo iOS`，iOS 18+，与 Mac 版共用 `CopyoCore` 与 iCloud 数据），模拟器构建：

```bash
xcodebuild -project Copyo.xcodeproj -scheme "Copyo iOS" -configuration Debug \
  -destination 'generic/platform=iOS Simulator' -derivedDataPath build CODE_SIGNING_ALLOWED=NO build
```

工程使用 Xcode 的自动签名，Team 填的是维护者的。贡献者请在 Xcode 的 Signing & Capabilities
里把 Team 换成自己的，或者构建时传入：

```bash
xcodebuild -project Copyo.xcodeproj -scheme Copyo -configuration Release \
  -derivedDataPath build DEVELOPMENT_TEAM=<你的 Team ID> build
```

只想编译看看、不打算安装到别的机器，也可以加 `CODE_SIGNING_ALLOWED=NO` 直接跳过签名。
注意 iCloud 同步依赖 App ID 上的 iCloud 容器与推送能力，换成自己的 Team 构建时这一项不可用
（需要在自己的开发者账号里建一个 iCloud 容器并改掉 `CopyoStore.cloudKitContainerIdentifier`），
其余功能不受影响。

## 打包分发（维护者）

```bash
EXPORT_PROFILE="Copymunk Developer ID" NOTARIZE=1 ./scripts/build-release.sh
# 归档 → 用本机的 Developer ID 证书和描述文件导出
# → Apple 公证 → staple → 产出 dist/Copymunk-<版本>.dmg + .zip
```

登录和公证都用 App Store Connect API 密钥（与 `scripts/asc.rb` 共用，放在 `~/.appstoreconnect/`，不进仓库），
不需要在 Xcode 里登录 Apple ID，也不需要 App 专用密码；用法和描述文件的说明见脚本开头的注释。
上传到 Releases 时，除了带版本号的 DMG / ZIP 和 `SHA256SUMS.txt`，再传一份同内容的 `Copymunk.dmg`：
官网的下载按钮固定指向 `releases/latest/download/Copymunk.dmg`。

- 脚本需要一份 Developer ID 证书与对应的描述文件（含 iCloud 容器与推送能力）。
  **没有开发者证书时**（比如自行从源码构建）：直接用上一节的 `CODE_SIGNING_ALLOWED=NO`
  构建即可，产物只适合本机使用；拿到其他机器会提示「已损坏，无法打开」（Gatekeeper 对
  无开发者身份应用的固定提示），需执行一次 `xattr -cr /Applications/Copymunk.app`。
- 企业环境若有 MDM（Jamf 等），也可以白名单分发。

### 自动构建（GitHub Actions）

每个 PR 和推送到 main（纯文档改动除外）都会跑 `.github/workflows/ci.yml`：无签名编译
macOS Debug、macOS Release-AppStore、iOS 模拟器三条，外加 `swift test --package-path CopyoCore`。
不需要任何证书，fork 出去的 PR 也能跑绿。

推送 `v<版本>` 形式的 tag 触发 `.github/workflows/release.yml`：校验 tag 与工程里的
`MARKETING_VERSION` 一致 → 归档 → 以 Developer ID 手动签名导出 → Apple 公证 → staple
→ 产出 DMG / ZIP，并自动创建 Release 附上产物。

```bash
# 先把 project.pbxproj 里的 MARKETING_VERSION 改成要发的版本并提交，再打 tag
git tag v1.0.1 && git push origin v1.0.1
```

CI 跑的不是上面那条 `build-release.sh`，而是 `scripts/ci-release.sh`：无人值守的 runner
既没有 Xcode 里登录的 Apple ID，也没有已注册的 Mac，自动签名那条路在它上面走不通，
所以 CI 改走手动签名 + 预装的 Developer ID 描述文件。两边产出的 .app 与 DMG 完全一致，
CI 只额外多附一份 `SHA256SUMS.txt`。

在 Actions 页面手动触发（Run workflow）是演练：缺哪一环就降级到哪一步，没配任何 secret
时也能跑完，产物只作为 workflow artifact 提供、不会挂到 Release 上。推 tag 则是在要一次
正式发布，签名或公证凑不齐就当场失败——这保证了 Release 页面上的 DMG 永远是签过名并
公证过的。

**目前签名仍在本机做**：2026-09-21 决定不把 Developer ID 私钥放进 GitHub Secrets，
正式包用 `scripts/build-release.sh` 在本地签名公证后手动上传，因此不推 `v*` tag。
CI 只做编译校验与手动演练。理由与改回条件见 [`docs/ci.md`](docs/ci.md) 第二节。

### 更新

官方发布签名身份固定：新版 DMG 覆盖安装（拖进 Applications 替换）即可，历史数据在
`~/Library/Application Support/Copyo/`，不受影响。

## 图标

图标的源头在 `art/app-icon-exploration/2026-10-15-copymunk-final/`，规格见其中的
`copymunk-icon-spec.md`。macOS 10 个规格（16 / 32 是手工光学稿）、iOS 浅色 / 深色 / 着色三张、
菜单栏模板两张，都由同一个脚本从各自的 SVG 直接出图，再同步进资产目录：

```bash
python3 art/app-icon-exploration/2026-10-15-copymunk-final/render.py   # 从 sources/ 里的 SVG 重新出图
./scripts/make-icon.sh            # 把 15 张 PNG 复制进三个资产目录
./scripts/make-icon.sh --check    # 只比对资产目录和源头是否一致
```

`render.py` 需要 Pillow 和 resvg-py（`python3 -m pip install --user Pillow resvg-py`）；
`make-icon.sh` 只做复制，不缩放，所以小尺寸和 iOS 变体不会被按比例缩糊。

再重新构建即可生效。

## 快捷键

| 操作 | 快捷键 |
| --- | --- |
| 打开 / 关闭面板 | `⇧⌘V`（全局，可在设置中自定义） |
| 在卡片间导航 | `←` `→` |
| 复制选中内容并回到之前的应用 | `↩` 或双击卡片 |
| 以纯文本复制 | `⇧↩`（1.1 及以前的 `⌥↩` 在 1.2 仍可用，下个版本移除） |
| 直接复制第 N 张卡片 | `⌘1`–`⌘9` |
| 在筛选间循环 | `⇥` / `⇧⇥` |
| 预览选中内容 | `空格`（搜索框为空时；输入中则键入空格）或 `⌘Y` |
| 固定到 Pinboard / 取消固定 | `⌘P` |
| 搜索 | 直接输入（`⌘F` 回到搜索框并全选） |
| 删除选中内容 | `⌘⌫` |
| 关闭预览 / 清除搜索 / 关闭面板 | `Esc` |

## 架构

工程里的几个 target：`Copyo/` 是 Mac 应用，`CopyoIOS/` 是 iPhone / iPad 应用，`CopyoShareExtension/` 是分享扩展，
`CopyoWidgets/` 是小组件和控制中心控件，`CopyoShared/` 是 iOS 各 target 共用的代码，`CopyoCore/` 是两端共用的
Swift Package（数据模型与存储）。下面是 Mac 应用的结构：

```
Copyo/
├── App/        应用入口、菜单栏常驻（NSStatusItem）
├── Models/     SwiftData 模型：ClipItem、Pinboard
├── Services/   剪贴板轮询监听、写回剪贴板并把焦点还给之前的应用、全局快捷键、iCloud 同步、图标取色、缩略图缓存
├── Panel/      悬浮面板（NSPanel + SwiftUI）：卡片流、搜索、筛选，预览子窗口与「已复制」轻提示
└── Settings/   设置窗口（通用 / 同步 / 快捷键 / 历史 / 关于）
```

技术要点：

- macOS 没有剪贴板变化通知 API，`ClipboardMonitor` 以 0.3s 间隔轮询 `NSPasteboard.changeCount`（所有剪贴板工具的通用做法）
- 文本优先于图片抓取：Excel/Numbers 等复制文本时会同时放一份图像渲染，必须按文本记录
- 全局快捷键使用 Carbon `RegisterEventHotKey`，零第三方依赖；应用不使用辅助功能权限
- 存储使用 SwiftData（SQLite），图片走 `externalStorage` + SHA-256 去重 + 缩略图缓存
- 同步有两条互斥的通道：文件夹方式是快照合并（iCloud Drive 或任意共享目录皆可，
  无需付费开发者账号，但不传播删除）；iCloud 方式由 SwiftData 直接镜像到 CloudKit
  私有数据库，增删改全量同步。两者共用同一份 `Copyo.store`，同一时刻只有一种生效

## License

[GPL-3.0](LICENSE)
