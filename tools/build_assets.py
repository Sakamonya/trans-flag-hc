"""
build_assets.py — 生成成品旗帜与尺寸套图。

运行：
    python tools/build_assets.py

全部产物确定性地由 flagkit.PALETTE / flagkit.BANDS 推导。
改色只需改 flagkit.py 顶部两行，然后重跑本脚本与 build_previews.py。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import flagkit as fk  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FLAG = ROOT / "flag"
ASSETS = ROOT / "assets"

PINK = fk.PALETTE["pink"]
BLUE = fk.PALETTE["blue"]
AXIS = fk.PALETTE["axis"]

DARK_AXIS, DARK_MIN = fk.solve_dark_axis()
DARK_COLORS = {"pink": PINK, "blue": BLUE, "axis": DARK_AXIS}


def save(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, optimize=True)
    print(f"  {path.relative_to(ROOT)}  {img.width}x{img.height}  {path.stat().st_size / 1024:.1f} KB")


def save_svg(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  {path.relative_to(ROOT)}  {path.stat().st_size} B")


def mono_png(w: int, h: int, color: str) -> Image.Image:
    gap = max(3, round(h * 0.010))
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bh = h / 5
    for i in range(5):
        y = bh * i + gap / 2
        d.rectangle((0, round(y), w, round(y + bh - gap)), fill=color)
    return img


def round_badge(size: int, ring: int = 0, ring_color: str = "#FFFFFF") -> Image.Image:
    ss = 4
    W = size * ss
    src = fk.flag_image(W, W).convert("RGBA")
    mask = Image.new("L", (W, W), 0)
    r = W // 2 - (ring * ss)
    ImageDraw.Draw(mask).ellipse((W // 2 - r, W // 2 - r, W // 2 + r, W // 2 + r), fill=255)
    src.putalpha(mask)
    if ring:
        d = ImageDraw.Draw(src)
        d.ellipse((W // 2 - r - ring * ss, W // 2 - r - ring * ss,
                   W // 2 + r + ring * ss, W // 2 + r + ring * ss),
                  outline=ring_color, width=ring * ss)
    return src.resize((size, size), Image.LANCZOS)


def main() -> None:
    print(f"palette  pink={PINK} blue={BLUE} axis={AXIS}")
    print(f"dark-UI axis solved  {AXIS} -> {DARK_AXIS}")
    print(f"  axis/bg contrast {fk.contrast(AXIS, fk.DARK_BG):.2f} -> {fk.contrast(DARK_AXIS, fk.DARK_BG):.2f}"
          f"   weakest of the three adjacent boundaries -> {DARK_MIN:.2f}\n")
    print("flag/")
    save_svg(fk.flag_svg(), FLAG / "trans-flag-hc.svg")
    save(fk.flag_image(1500, 900), FLAG / "trans-flag-hc-1500x900.png")
    save(fk.flag_image(3000, 1800), FLAG / "trans-flag-hc-3000x1800.png")

    # 白描边版：24px 边（以 1500 宽为基准）
    save_svg(fk.flag_svg(outline="#FFFFFF", outline_w=24), FLAG / "trans-flag-hc-outline-white.svg")
    canvas = Image.new("RGB", (1548, 948), "#FFFFFF")
    canvas.paste(fk.flag_image(1500, 900), (24, 24))
    save(canvas, FLAG / "trans-flag-hc-outline-white-1548x948.png")

    # 单色线稿（透明底）
    for name, col in (("white", "#FFFFFF"), ("pink", PINK)):
        save_svg(fk.mono_svg(col), FLAG / f"trans-flag-hc-onecolor-{name}.svg")
        save(mono_png(1500, 900, col), FLAG / f"trans-flag-hc-onecolor-{name}-1500x900.png")

    # 深底亮轴变体
    save_svg(fk.flag_svg(DARK_COLORS), FLAG / "trans-flag-hc-dark-ui.svg")
    save(fk.flag_image(1500, 900, DARK_COLORS), FLAG / "trans-flag-hc-dark-ui-1500x900.png")

    print("assets/")
    save(fk.flag_image(1080, 1080), ASSETS / "avatar-1080.png")
    save(fk.flag_image(512, 512), ASSETS / "avatar-512.png")
    save(round_badge(1080), ASSETS / "avatar-round-1080.png")
    save(round_badge(512), ASSETS / "avatar-round-512.png")
    save(round_badge(512, ring=14), ASSETS / "badge-ring-512.png")
    save(round_badge(1024, ring=28), ASSETS / "badge-ring-1024.png")
    save(fk.flag_image(1200, 1800), ASSETS / "wallpaper-1200x1800.png")
    save(fk.flag_image(1440, 3120), ASSETS / "wallpaper-1440x3120.png")

    # 一致性清单：供 README 与校验脚本引用
    spec = {
        "canonical": {"pink": PINK, "blue": BLUE, "axis": AXIS},
        "bands": fk.BANDS,
        "ratio": "3:5",
        "dark_ui_variant": {"pink": PINK, "blue": BLUE, "axis": DARK_AXIS},
        "contrast": {
            "pink_axis": round(fk.contrast(PINK, AXIS), 2),
            "blue_axis": round(fk.contrast(BLUE, AXIS), 2),
            "pink_blue": round(fk.contrast(PINK, BLUE), 2),
            "pink_axis_dark": round(fk.contrast(PINK, DARK_AXIS), 2),
            "blue_axis_dark": round(fk.contrast(BLUE, DARK_AXIS), 2),
            "axis_bg_dark": round(fk.contrast(AXIS, fk.DARK_BG), 2),
            "axis_dark_bg_dark": round(fk.contrast(DARK_AXIS, fk.DARK_BG), 2),
        },
        "classic_1999": {
            "pink": fk.CLASSIC["pink"],
            "blue": fk.CLASSIC["blue"],
            "axis": fk.CLASSIC["axis"],
            "contrast": {
                "pink_axis": round(fk.contrast(fk.CLASSIC["pink"], fk.CLASSIC["axis"]), 2),
                "blue_axis": round(fk.contrast(fk.CLASSIC["blue"], fk.CLASSIC["axis"]), 2),
                "pink_blue": round(fk.contrast(fk.CLASSIC["pink"], fk.CLASSIC["blue"]), 2),
            },
        },
    }
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "spec.json").write_text(
        json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("  docs/spec.json")
    print("\n" + json.dumps(spec["contrast"], indent=2))


if __name__ == "__main__":
    main()
