#!/bin/bash
# 把定稿的 Copymunk 图标同步进 Xcode 资产目录。
#
#   ./scripts/make-icon.sh           复制 15 张 PNG 进三个资产目录
#   ./scripts/make-icon.sh --check   只比对，不复制；有差异时退出码 1
#
# 图标源头在 $SRC（规格见其中的 copymunk-icon-spec.md）。改图标的流程是：
# 改 $SRC/sources 里的 SVG → `python3 $SRC/render.py` 重新出图 → 跑本脚本同步。
# render.py 需要 Pillow 和 resvg-py（python3 -m pip install --user Pillow resvg-py）。
#
# 本脚本只复制、不缩放，原因有三个：
# - macOS 的 16 / 32（icon_16x16、icon_16x16@2x、icon_32x32）是手工光学稿。按比例缩出来的
#   小尺寸会糊成一团，鼓腮和眼睛都认不出来。
# - iOS 不能复用 macOS 那张主图：macOS 是透明底、内缩 9.8% 的圆角方块，iOS 要满幅、
#   不带 alpha（否则上传时会触发 ITMS-90717）。深色和着色两张也是单独画的。
# - 菜单栏模板在 18 / 36px 上是逐像素画的。
# 所以三类都由 render.py 从各自的 SVG 直接出图，这里不再做任何派生。
#
# 资产目录里的 Contents.json 不动：文件名与源头一一对应；iOS 的 appearances 结构、
# 菜单栏的 template-rendering-intent 都保留现状。
set -euo pipefail
cd "$(dirname "$0")/.."

SRC="art/app-icon-exploration/2026-10-15-copymunk-final"

# 源子目录:资产目录:文件名…
SETS=(
  "appiconset:Copyo/Assets.xcassets/AppIcon.appiconset:icon_16x16.png icon_16x16@2x.png icon_32x32.png icon_32x32@2x.png icon_128x128.png icon_128x128@2x.png icon_256x256.png icon_256x256@2x.png icon_512x512.png icon_512x512@2x.png"
  "ios-appiconset:CopyoIOS/Assets.xcassets/AppIcon.appiconset:AppIcon.png AppIcon-Dark.png AppIcon-Tinted.png"
  "menubar:Copyo/Assets.xcassets/MenuBarIcon.imageset:menubar-template-18.png menubar-template-36.png"
)

CHECK=0
[[ "${1:-}" == "--check" ]] && CHECK=1

diffs=0
for set in "${SETS[@]}"; do
  IFS=: read -r sub dest files <<<"$set"
  for f in $files; do
    src="$SRC/$sub/$f"
    if [[ ! -f "$src" ]]; then
      echo "找不到源文件: $src（先跑 python3 $SRC/render.py）" >&2
      exit 1
    fi
    if cmp -s "$src" "$dest/$f"; then
      continue
    fi
    diffs=$((diffs + 1))
    if [[ $CHECK -eq 1 ]]; then
      echo "不一致: $dest/$f"
    else
      cp "$src" "$dest/$f"
      echo "已更新: $dest/$f"
    fi
  done
done

if [[ $CHECK -eq 1 ]]; then
  [[ $diffs -eq 0 ]] && echo "图标与 $SRC 一致" || { echo "$diffs 个文件与源头不一致，跑 ./scripts/make-icon.sh 同步" >&2; exit 1; }
else
  echo "同步完成，更新了 $diffs 个文件（重新构建后生效）"
fi
