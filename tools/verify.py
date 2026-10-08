"""
verify.py — 一致性校验。

逐一打开成品图，按像素确认它们用的就是 flagkit.PALETTE 里的色值；
再检查 SVG 与网页默认值是否同步。任何一处对不上就报错退出。

    python tools/verify.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import flagkit as fk  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DARK_AXIS, _ = fk.solve_dark_axis()

ok_count = 0
fails: list[str] = []


def check(cond: bool, msg: str) -> None:
    global ok_count
    if cond:
        ok_count += 1
    else:
        fails.append(msg)
        print(f"  FAIL  {msg}")


def sample_bands(path: Path, colors: dict) -> list[str]:
    """取图片中线上的五个色带色值。"""
    img = Image.open(path).convert("RGB")
    w, h = img.size
    out = []
    for i in range(5):
        y = int(h * (i + 0.5) / 5)
        out.append(fk.rgb_to_hex(img.getpixel((w // 2, y))))
    return out


def expect_bands(colors: dict) -> list[str]:
    return [colors[k] for k in fk.BANDS]


CANON, DARKV = fk.PALETTE, {"pink": fk.PALETTE["pink"], "blue": fk.PALETTE["blue"], "axis": DARK_AXIS}

RASTER = {
    "flag/trans-flag-hc-1500x900.png": CANON,
    "flag/trans-flag-hc-3000x1800.png": CANON,
    "flag/trans-flag-hc-dark-ui-1500x900.png": DARKV,
    "assets/avatar-1080.png": CANON,
    "assets/avatar-512.png": CANON,
    "assets/wallpaper-1200x1800.png": CANON,
    "assets/wallpaper-1440x3120.png": CANON,
}

# 描边版：中线仍应是正式规格，外圈是白
RASTER_ROUND = {
    "assets/avatar-round-512.png": CANON,
    "assets/badge-ring-512.png": CANON,
}

SVG = {
    "flag/trans-flag-hc.svg": CANON,
    "flag/trans-flag-hc-dark-ui.svg": DARKV,
    "flag/trans-flag-hc-outline-white.svg": CANON,
}

MONO = {
    "flag/trans-flag-hc-onecolor-white.svg": "#FFFFFF",
    "flag/trans-flag-hc-onecolor-pink.svg": fk.PALETTE["pink"],
}

PREVIEWS = [
    "preview/01-hero.png", "preview/01-hero-light.png",
    "preview/02-compare.png", "preview/02-compare-light.png",
    "preview/03-legibility.png",
    "preview/04-color-spec.png", "preview/05-scene-dark-ui.png", "preview/06-cloth.png",
    "preview/07-dark-bg.png", "preview/08-variants.png",
    "assets/social-card-1200x630.png",
]


def main() -> int:
    print(f"spec  pink={CANON['pink']} blue={CANON['blue']} axis={CANON['axis']} "
          f"dark-axis={DARK_AXIS}\n")

    print("成品位图（按像素抽样）")
    for rel, colors in RASTER.items():
        p = ROOT / rel
        if not p.exists():
            check(False, f"{rel} 不存在")
            continue
        got, want = sample_bands(p, colors), expect_bands(colors)
        check(got == want, f"{rel}\n        实得 {got}\n        期望 {want}")
        if got == want:
            print(f"  ok    {rel}  {' '.join(got)}")

    print("\n圆形裁切（圆心中线）")
    for rel, colors in RASTER_ROUND.items():
        p = ROOT / rel
        if not p.exists():
            check(False, f"{rel} 不存在")
            continue
        img = Image.open(p).convert("RGBA")
        w, h = img.size
        got = [fk.rgb_to_hex(img.getpixel((w // 2, int(h * (i + 0.5) / 5)))[:3]) for i in range(5)]
        check(got == expect_bands(colors), f"{rel}  实得 {got}")
        if got == expect_bands(colors):
            print(f"  ok    {rel}  {' '.join(got)}")

    print("\n矢量文件（色值字面量）")
    for rel, colors in SVG.items():
        p = ROOT / rel
        if not p.exists():
            check(False, f"{rel} 不存在")
            continue
        text = p.read_text(encoding="utf-8")
        missing = [v for v in colors.values() if v not in text]
        check(not missing, f"{rel} 缺少色值 {missing}")
        check("viewBox" in text, f"{rel} 缺少 viewBox")
        if not missing:
            print(f"  ok    {rel}")
    for rel, col in MONO.items():
        p = ROOT / rel
        if not p.exists():
            check(False, f"{rel} 不存在")
            continue
        check(col in p.read_text(encoding="utf-8"), f"{rel} 缺少 {col}")
        print(f"  ok    {rel}")

    print("\n效果图（存在性 + 体量）")
    for rel in PREVIEWS:
        p = ROOT / rel
        if not p.exists():
            check(False, f"{rel} 不存在")
            continue
        size = p.stat().st_size
        check(size > 20_000, f"{rel} 只有 {size} 字节，疑似空图")
        im = Image.open(p)
        check(min(im.size) >= 600, f"{rel} 尺寸过小 {im.size}")
        print(f"  ok    {rel}  {im.size[0]}x{im.size[1]}  {size/1024:.0f} KB")

    print("\n效果图用色（关键色必须出现）")
    # 深色 hero 走亮轴变体：中轴 #383838 贴深色背景只有 1.27–1.40:1，会被吃掉。
    # 浅色 hero 与规格图 / 对比图必须仍是正式规格——对比图里的数字要和 README 表格一致。
    PREVIEW_COLORS = {
        "preview/01-hero.png": DARKV,
        "preview/01-hero-light.png": CANON,
        "preview/02-compare.png": CANON,
        "preview/04-color-spec.png": CANON,
        # 社交卡只有一张、底色是 #0D1117，中轴 #383838 在上面只有 1.61:1，故用亮轴变体
        "assets/social-card-1200x630.png": DARKV,
    }
    for rel, want in PREVIEW_COLORS.items():
        im = Image.open(ROOT / rel).convert("RGB")
        got = {fk.rgb_to_hex(c) for _, c in im.getcolors(maxcolors=1 << 24)}
        for name, col in want.items():
            check(col in got, f"{rel} 中找不到 {name} {col}")
        if all(col in got for col in want.values()):
            print(f"  ok    {rel}  {' '.join(want.values())}")

    print("\n原版条纹顺序（对比图里 1999 版必须蓝在外圈）")
    for rel in ("preview/02-compare.png", "preview/02-compare-light.png"):
        im = Image.open(ROOT / rel).convert("RGB")
        x = 440                      # 左列＝原版那一栏的水平中心
        ys = {}
        for name in ("blue", "pink"):
            target = fk.CLASSIC[name]
            ys[name] = next((y for y in range(im.height)
                             if fk.rgb_to_hex(im.getpixel((x, y))) == target), None)
        check(ys["blue"] is not None, f"{rel} 里找不到原版的蓝 {fk.CLASSIC['blue']}")
        check(ys["pink"] is not None, f"{rel} 里找不到原版的粉 {fk.CLASSIC['pink']}")
        if ys["blue"] is not None and ys["pink"] is not None:
            check(ys["blue"] < ys["pink"],
                  f"{rel} 把 1999 原版画反了：外圈应为蓝，实得粉在上"
                  f"（blue y={ys['blue']} / pink y={ys['pink']}）")
            print(f"  ok    {rel}  蓝在粉之上（y {ys['blue']} < {ys['pink']}），顺序正确")

    print("\n调色器网页默认值")
    page = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    for name, col in CANON.items():
        check(col in page, f"docs/index.html 缺少 {name} {col}")
    check(str(DARK_AXIS) in page, f"docs/index.html 缺少亮轴变体 {DARK_AXIS}")
    print(f"  ok    docs/index.html  含 {CANON['pink']} / {CANON['blue']} / {CANON['axis']} / {DARK_AXIS}")

    print("\n文档")
    for rel in ("README.md", "README.en.md", "LICENSE", "docs/design-notes.md"):
        p = ROOT / rel
        check(p.exists() and p.stat().st_size > 200, f"{rel} 缺失或过小")
    for rel in ("README.md", "README.en.md", "docs/design-notes.md"):
        p = ROOT / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        for name, col in CANON.items():
            check(col in text, f"{rel} 缺少 {name} {col}")

    print("\n文档内的文件链接（markdown 链接 + <picture> 的 src/srcset，含图片与普通链接）")
    md_any = re.compile(r"\]\(([^)\s]+)\)")
    html_src = re.compile(r'(?:src|srcset)="([^"]+)"')
    for rel in ("README.md", "README.en.md", "docs/design-notes.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        links = [l.strip() for l in md_any.findall(text)]
        links += [l.strip() for l in html_src.findall(text)]
        files = sorted({l for l in links if not l.startswith(("http", "#", "mailto:"))})
        if rel.endswith(".md") and rel.startswith("README"):
            check(bool(files), f"{rel} 没有任何指向文件的链接")
        for l in files:
            if not (ROOT / l.split("#")[0]).exists():
                check(False, f"{rel} 引用了 {l}，但文件不存在")
        print(f"  ok    {rel}  {len(files)} 个文件链接全部存在")

    print("\nREADME 目录锚点（#链接必须有落点）")
    anchor = re.compile(r"\]\(#([^)]+)\)")
    for rel in ("README.md", "README.en.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        ids = set(re.findall(r'<a id="([^"]+)"', text))
        links = set(anchor.findall(text))
        check(bool(links), f"{rel} 没有任何目录锚点链接")
        for m in sorted(l for l in links if l not in ids):
            check(False, f"{rel} 的目录链接 #{m} 找不到对应的 <a id>")
        print(f"  ok    {rel}  {len(links)} 个锚点链接全部有落点")

    print("\n孤儿文件（在仓库里但没有任何文档提到）")
    text = "".join((ROOT / r).read_text(encoding="utf-8")
                   for r in ("README.md", "README.en.md", "docs/design-notes.md"))
    for folder in ("flag", "assets", "preview"):
        for f in sorted((ROOT / folder).iterdir()):
            if f.is_file():
                check(f.name in text, f"{folder}/{f.name} 未被任何文档提及")
    print("  ok    已扫描 flag/ assets/ preview/")

    print()
    if fails:
        print(f"[FAIL] {len(fails)} 项不一致，{ok_count} 项通过")
        return 1
    print(f"[OK] 全部 {ok_count} 项一致：{CANON['pink']} / {CANON['blue']} / {CANON['axis']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
