#!/usr/bin/env python3
"""从商店截图抠出机身和面板，生成首页用的透明底图（docs/assets/）。

- 手机：art/store-ios/ 的 iPhone 截图，只留机身（圆角深色边框 + 屏幕）
- Mac 面板：art/store/01-panel-*.png，只留面板（圆角浅灰描边以内）

商店截图是整张暖白底板，机身和面板外还烘焙了一圈投影。早先首页直接裁成 JPG，
底板颜色和网页背景差一点、再叠上网页自己的 drop-shadow，四周会露出一个方框。
这里外面全透明，投影交给网页的 CSS。

    python3 scripts/make-site-shots.py

机身位置靠找深色边框定位，圆角半径来自 make-store-shots-ios.py 的 phone 配置
（corner 150 + bezel 22，按商店图原尺寸）。
"""
from pathlib import Path
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "art" / "store-ios"
OUT = REPO / "docs" / "assets"

SHOTS = {"phone-history": "phone-01-history", "phone-share": "phone-04-share"}
BEZEL = (22, 22, 26)
BEZEL_WIDTH = 22
OUTER_RADIUS = 150 + BEZEL_WIDTH
WIDTH = 560          # 网页上最宽约 260px，按 2 倍图出
MAC_WIDTH = 2000     # 网页上最宽约 1080px


def is_bezel(px):
    return all(abs(a - b) <= 6 for a, b in zip(px[:3], BEZEL))


def bezel_box(im):
    """机身外框。左右边：机身下部一行里最左、最右的深色像素（机身外是底板）。
    下边：中间一列从底往上第一个深色像素。上边不直接找——标题文字和边框同色，
    改用屏幕比例反推：屏幕是 1320×2868 的模拟器截图等比缩放，四周各一圈 BEZEL_WIDTH 边框。"""
    w, h = im.size
    row = h * 3 // 4
    xs = [x for x in range(w) if is_bezel(im.getpixel((x, row)))]
    left, right = xs[0], xs[-1] + 1
    bottom = next(y for y in range(h - 1, 0, -1) if is_bezel(im.getpixel((w // 2, y)))) + 1
    screen_w = right - left - 2 * BEZEL_WIDTH
    top = bottom - (round(2868 * screen_w / 1320) + 2 * BEZEL_WIDTH)
    return left, top, right, bottom


def cut(name, source, lang):
    im = Image.open(SRC / f"{source}-{lang}.png").convert("RGB")
    box = bezel_box(im)
    phone = im.crop(box).convert("RGBA")
    w, h = phone.size
    # 4 倍尺寸画遮罩再缩小，边缘才不发毛；内缩 1px，避开边框外沿和底板混色的那一圈
    s = 4
    mask = Image.new("L", (w * s, h * s), 0)
    ImageDraw.Draw(mask).rounded_rectangle((s, s, w * s - 1 - s, h * s - 1 - s),
                                           radius=(OUTER_RADIUS - 1) * s, fill=255)
    phone.putalpha(mask.resize((w, h), Image.LANCZOS))
    out = phone.resize((WIDTH, round(h * WIDTH / w)), Image.LANCZOS)
    path = OUT / f"{name}-{lang}.webp"
    out.save(path, "WEBP", quality=86, method=6)
    print(f"{path.relative_to(REPO)}  {out.size[0]}×{out.size[1]}  {path.stat().st_size // 1024} KB  机身 {box}")


def lum(im, x, y):
    r, g, b = im.getpixel((x, y))[:3]
    return (r * 299 + g * 587 + b * 114) // 1000


def cut_mac(lang):
    """面板外沿是一圈约 2px 的灰色描边（亮度 180 上下），底板和烘焙投影都在 205 以上。
    上边从副标题下方开始往下找，避开标题文字。圆角半径从上沿那一行描边的起点量出来。"""
    im = Image.open(REPO / "art" / "store" / f"01-panel-{lang}.png").convert("RGB")
    w, h = im.size
    edge = lambda v: v < 205
    row = h * 68 // 100
    left = next(x for x in range(w) if edge(lum(im, x, row)))
    right = next(x for x in range(w - 1, 0, -1) if edge(lum(im, x, row))) + 1
    top = next(y for y in range(h * 40 // 100, h) if edge(lum(im, w // 2, y)))
    bottom = next(y for y in range(h - 1, 0, -1) if edge(lum(im, w // 2, y))) + 1
    radius = next(x for x in range(left, w) if edge(lum(im, x, top))) - left
    panel = im.crop((left, top, right, bottom)).convert("RGBA")
    pw, ph = panel.size
    s = 4
    mask = Image.new("L", (pw * s, ph * s), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw * s - 1, ph * s - 1), radius=radius * s, fill=255)
    panel.putalpha(mask.resize((pw, ph), Image.LANCZOS))
    out = panel.resize((MAC_WIDTH, round(ph * MAC_WIDTH / pw)), Image.LANCZOS)
    path = OUT / f"mac-panel-{lang}.webp"
    out.save(path, "WEBP", quality=86, method=6)
    print(f"{path.relative_to(REPO)}  {out.size[0]}×{out.size[1]}  {path.stat().st_size // 1024} KB  "
          f"面板 {(left, top, right, bottom)} 圆角 {radius}")


def main():
    for name, source in SHOTS.items():
        for lang in ("en", "zh"):
            cut(name, source, lang)
    for lang in ("en", "zh"):
        cut_mac(lang)


if __name__ == "__main__":
    main()
