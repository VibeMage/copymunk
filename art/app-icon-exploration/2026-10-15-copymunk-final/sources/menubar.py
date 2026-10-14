#!/usr/bin/env python3
"""Native integer-pixel Copymunk menu glyphs. Importing performs no writes."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def make_mask(size: int) -> Image.Image:
    """Draw each target grid directly; no antialiasing or supersampling."""
    mask = Image.new("1", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    if size == 18:
        # Small round ears, a high forehead, and two wider cheek pockets.
        draw.ellipse((3, 2, 6, 5), fill=1)
        draw.ellipse((11, 2, 14, 5), fill=1)
        draw.ellipse((3, 3, 14, 14), fill=1)
        draw.ellipse((1, 8, 8, 15), fill=1)
        draw.ellipse((9, 8, 16, 15), fill=1)
        draw.rectangle((6, 12, 11, 15), fill=1)
        # An open forehead with two friendly positive eyes. No eye-mask bar.
        draw.ellipse((5, 4, 12, 10), fill=0)
        draw.rectangle((8, 4, 9, 5), fill=1)
        draw.rectangle((6, 7, 7, 8), fill=1)
        draw.rectangle((10, 7, 11, 8), fill=1)
        # Native one-pixel ear hollows; only the central crown mark survives.
        draw.point((4, 3), fill=0)
        draw.point((13, 3), fill=0)
        # The two cream cheeks become separate rounded negative pockets.
        draw.ellipse((3, 10, 6, 13), fill=0)
        draw.ellipse((11, 10, 14, 13), fill=0)
        draw.rectangle((8, 10, 9, 12), fill=0)
        draw.point((8, 10), fill=1)
        draw.point((9, 10), fill=1)
        # Remove two one-pixel islands left by overlapping native ellipses.
        draw.point((6, 10), fill=0)
        draw.point((11, 10), fill=0)
    elif size == 36:
        # Independently placed native 36px curves, not a resized 18px mask.
        draw.ellipse((7, 4, 14, 12), fill=1)
        draw.ellipse((21, 4, 28, 12), fill=1)
        draw.ellipse((7, 7, 28, 29), fill=1)
        draw.ellipse((2, 17, 17, 32), fill=1)
        draw.ellipse((18, 17, 33, 32), fill=1)
        draw.rectangle((12, 28, 23, 32), fill=1)
        draw.ellipse((9, 6, 12, 9), fill=0)
        draw.ellipse((23, 6, 26, 9), fill=0)
        draw.ellipse((9, 9, 26, 22), fill=0)
        draw.rectangle((17, 9, 18, 13), fill=1)
        draw.ellipse((12, 15, 15, 19), fill=1)
        draw.ellipse((20, 15, 23, 19), fill=1)
        draw.rectangle((17, 22, 18, 23), fill=1)
        draw.ellipse((5, 21, 14, 28), fill=0)
        draw.ellipse((21, 21, 30, 28), fill=0)
        draw.line([(16, 25), (16, 26), (17, 27), (18, 27), (19, 26), (19, 25)], fill=0, width=1)
        for point in ((12, 21), (14, 22), (23, 21), (21, 22)):
            draw.point(point, fill=0)
    else:
        raise ValueError("Only independently drawn 18px and 36px grids exist")
    return mask.convert("L")


def write_svg(mask: Image.Image, destination: Path) -> None:
    size = mask.width
    rows = []
    for y in range(size):
        x = 0
        while x < size:
            if not mask.getpixel((x, y)):
                x += 1
                continue
            start = x
            while x < size and mask.getpixel((x, y)):
                x += 1
            rows.append(f'    <rect x="{start}" y="{y}" width="{x-start}" height="1"/>')
    destination.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">\n'
        '  <title>Copymunk menu bar template</title>\n'
        '  <desc>Native integer-pixel cheek silhouette, open forehead, positive eyes, and transparent pockets.</desc>\n'
        '  <g fill="#000000" shape-rendering="crispEdges">\n'
        + "\n".join(rows) + '\n  </g>\n</svg>\n', encoding="utf-8"
    )


def font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def simulation(masks: dict[int, Image.Image], destination: Path) -> None:
    canvas = Image.new("RGB", (1180, 620), "#F0EEE8")
    draw = ImageDraw.Draw(canvas)
    draw.text((40, 22), "菜单栏模板 / 原尺寸与整数像素检查", font=font(28), fill="#293532")
    draw.text((40, 64), "18px 与 36px 各自直接绘制；右侧 4× 最近邻放大。系统负责反色。", font=font(18), fill="#68716D")
    for top, background, foreground, label in (
        (116, "#E0E4E1", "#101715", "浅色菜单栏"),
        (366, "#252D30", "#F7F9F7", "深色菜单栏"),
    ):
        draw.rounded_rectangle((24, top, 1156, top + 226), radius=22, fill=background)
        draw.text((44, top + 18), label, font=font(19), fill=foreground)
        draw.text((986, top + 18), "周四 10:24", font=font(17), fill=foreground)
        for size, x in ((18, 75), (36, 590)):
            draw.text((x, top + 62), f"{size}px 原尺寸", font=font(16), fill=foreground)
            mask = masks[size]
            canvas.paste(foreground, (x + 38, top + 107), mask)
            zoom = mask.resize((size * 4, size * 4), Image.Resampling.NEAREST)
            canvas.paste(foreground, (x + 145, top + 62), zoom)
            draw.text((x + 345, top + 116), f"{size} × {size}\nalpha 0 / 255", font=font(15), fill=foreground)
    # 4x is deliberate: both complete native grids fit without crop.
    draw.text((40, 597), "右侧实际为 4× 像素放大；未做平滑、灰边或超采样。", font=font(14), fill="#68716D")
    canvas.save(destination)


def render() -> dict[str, object]:
    masks: dict[int, Image.Image] = {}
    result: dict[str, object] = {}
    for size in (18, 36):
        mask = make_mask(size)
        masks[size] = mask
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        image.putalpha(mask)
        png_path = ROOT / "menubar" / f"menubar-template-{size}.png"
        svg_path = ROOT / "sources" / f"menubar-{size}.svg"
        png_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(png_path)
        write_svg(mask, svg_path)
        assert set(mask.getdata()) == {0, 255}
        assert all(pixel[:3] == (0, 0, 0) for pixel in image.getdata())
        result[str(size)] = {"png": str(png_path), "svg": str(svg_path), "bbox": mask.getbbox(), "opaque_pixels": sum(v == 255 for v in mask.getdata())}
    preview_path = ROOT / "previews" / "menubar-simulation.png"
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    simulation(masks, preview_path)
    result["preview"] = str(preview_path)
    return result


def main() -> None:
    print(json.dumps(render(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
