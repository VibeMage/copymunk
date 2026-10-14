English | [简体中文](README.md)

# Copymunk final artwork: 04 Delight

The maintainer selected round-three 04. This package prepares a complete asset set for integration. **The selected macOS face, geometry, gradients, blush, shadows, and warm background remain unchanged**: `sources/macos.svg` is byte-identical to the selected `04-delight/source.svg`. Separate 16/32px optical drawings, three iOS appearances, and menu-bar templates complete the set.

Start with the [overview](overview.png), [native-size contact sheet](contact-sheet.png), and [small-size comparison](previews/optical-review.png). Drawing specifications are in [copymunk-icon-spec.md](copymunk-icon-spec.md), in Chinese.

## Changes

- **Original background retained.** A test moved `#FFD7A5 → #F2AE78` to `#FFD3AF → #EFA888`. Separation improved slightly at large size, but not clearly at 64/32px, so the test was rejected. The [original](comparisons/before-1024.png), [color trial](comparisons/after-1024.png), and [comparison](comparisons/background-comparison.png) are included. Integrate from `appiconset/`, not the rejected trial.
- **Independent hand-drawn 16/32px optics.** Eyes, highlights, and nose/mouth spacing use target-size coordinates. At 16px, fine teeth, secondary highlights, and side stripes are removed; bright round eyes, cream cheeks, and a cheerful open mouth remain. At 32px, a small tooth remains. Both 32px slots share identical PNG bytes. Antialiasing renders each target SVG without passing through the 1024 master.
- **64px retains a master reduction.** Native and enlarged checks preserved eyes, highlights, nose, mouth, and cheeks, so no separate 64px drawing was needed. Larger sizes retain the selected master.
- **All iOS appearances share face geometry.** Light keeps the original palette. Dark uses a warm deep-brown background and gently dimmed fur and cheeks. Tinted deliberately separates head, cheeks, facial features, and highlights with manual grayscale on transparency.
- **Menu-bar templates simplify the round ears and stuffed cheeks.** The 18/36px drawings use integer black/transparent pixels. Template inversion supplies the light appearance. See [pixel rules](sources/menubar-notes.md) and the [simulation](previews/menubar-simulation.png).

## Xcode mapping

`appiconset/` maps to `Copyo/Assets.xcassets/AppIcon.appiconset/`:

| Delivered file | Xcode size / scale | Pixels | Source |
| --- | --- | --- | --- |
| `icon_16x16.png` | 16×16 / 1x | 16 | Independent 16px optics |
| `icon_16x16@2x.png` | 16×16 / 2x | 32 | Independent 32px optics |
| `icon_32x32.png` | 32×32 / 1x | 32 | Same bytes as previous row |
| `icon_32x32@2x.png` | 32×32 / 2x | 64 | Master reduction |
| `icon_128x128.png` | 128×128 / 1x | 128 | Master reduction |
| `icon_128x128@2x.png` | 128×128 / 2x | 256 | Master reduction |
| `icon_256x256.png` | 256×256 / 1x | 256 | Master reduction |
| `icon_256x256@2x.png` | 256×256 / 2x | 512 | Master reduction |
| `icon_512x512.png` | 512×512 / 1x | 512 | Master reduction |
| `icon_512x512@2x.png` | 512×512 / 2x | 1024 | Selected master |

All are RGBA with a transparent exterior. At 1024, the tile starts at x/y=100.352, measures 823.296 square, and has radius 229.0688. Optical drawings preserve those tile proportions while redrawing facial geometry.

`ios-appiconset/` maps to `CopyoIOS/Assets.xcassets/AppIcon.appiconset/`:

| Delivered file | Appearance | Format |
| --- | --- | --- |
| `AppIcon.png` | Default / Light | 1024 RGB, opaque, full bleed, no alpha or baked corners |
| `AppIcon-Dark.png` | luminosity / dark | 1024 RGB, opaque, full bleed, no alpha or baked corners |
| `AppIcon-Tinted.png` | luminosity / tinted | 1024 RGBA, transparent background, manual grayscale with R=G=B everywhere |

This follows the reviewed `scripts/make-icon.sh --ios` channel conventions. Tinted uses neither automatic grayscale conversion nor an opaque gray tile. iOS assets have no baked mask; presentation previews add an approximate continuous-corner mask.

`menubar/` maps to `Copyo/Assets.xcassets/MenuBarIcon.imageset/`:

| Delivered file | Xcode scale | Format |
| --- | --- | --- |
| `menubar-template-18.png` | 1x | 18×18 RGBA, black RGB, alpha only 0/255 |
| `menubar-template-36.png` | 2x | 36×36 RGBA, black RGB, alpha only 0/255 |

Each of these three directories includes the existing matching `Contents.json` slot declarations. The menu set declares `template-rendering-intent: template`. No assets were installed and no loading code was changed.

## Sources and reproduction

- `sources/macos.svg`: final master; `macos-original.svg` preserves the selected input.
- `sources/macos-optical-16.svg` and `macos-optical-32.svg`: editable target-size vectors.
- `sources/ios-light.svg`, `ios-dark.svg`, `ios-tinted.svg`: editable iOS artwork.
- `sources/menubar.py`: integer pixel source, producing template SVGs, PNGs, and menu simulation.
- `sources/sRGB.icc`: fixed sRGB profile for stable regeneration.
- `render.py`: writes only within this delivery directory; it does not invoke the existing icon script or install assets.

Requires Python 3.9+, Pillow 11.3.0, and resvg-py 0.3.2. Preview text uses macOS `/System/Library/Fonts/Supplemental/Arial Unicode.ttf`; icons themselves have no font dependency.

```bash
cd art/app-icon-exploration/2026-10-15-copymunk-final
python3 -m pip install --user Pillow==11.3.0 resvg-py==0.3.2
python3 render.py
```

The default rebuilds PNGs, comparisons, simulations, validation, and manifest from the delivered SVGs and menu pixel source. The master uses 4× supersampling and BOX reduction. Optical SVGs render at 8× their target grid and reduce with BOX. Sizes 64 and larger reduce from the master with LANCZOS. Menu templates use no supersampling or image resizing.

After intentionally changing the macOS master, `python3 render.py --only sources` can regenerate the three iOS SVGs using the `DARK`/`TINTED` palette maps. This overwrites iOS SVGs; avoid it after independent iOS source edits. Also available: `--only render`, `--only sheets`, `--only audit`, `--only manifest`. Do not overwrite the 16/32px optics with the old `make-icon.sh`.

## Previews and validation

- [contact-sheet.png](contact-sheet.png): all ten macOS slots at native size, each on light and dark surroundings; iOS appearances at 320px with a presentation mask; menu templates at native 18/36px. Inspect at 100% zoom.
- [Dock simulation](previews/dock-simulation.png) and [App Store search simulation](previews/app-store-search-simulation.png): light/dark layout and scale checks, not runtime or store screenshots.
- [Optical review](previews/optical-review.png): native 16/32/64px and nearest-neighbor enlargement, beside direct reductions.
- `qa-report.json`: format checks for 15 integration PNGs, identical 32px slots, 20 native macOS contact samples, selected-source identity, and 187 protected input hashes.
- `manifest.json`: delivery SHA-256 hashes.
- `reproducibility-report.json`: all 15 integration PNGs were regenerated for this delivery, with identical SHA-256 hashes across both runs.

Native 16/32/64px, menu templates, and platform previews were visually checked on light and dark backgrounds. At 16px, fine teeth and full species markings cannot survive; eyes, cheeks, and cheerful expression take priority. Background and fur remain related warm colors, preserving the chosen style.

**Integration status: integrated (2026-10-15).** `scripts/make-icon.sh` copies the 15 PNGs into `Copyo/Assets.xcassets/AppIcon.appiconset`, `CopyoIOS/Assets.xcassets/AppIcon.appiconset` and `Copyo/Assets.xcassets/MenuBarIcon.imageset` (`--check` only compares); macOS and the iOS simulator both build. The iOS mask and Tinted background are still presentation approximations; the dark / tinted appearances and the 18px menu bar icon still need a check on a real device.
