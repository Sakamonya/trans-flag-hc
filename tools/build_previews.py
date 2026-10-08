"""
build_previews.py — 生成全部效果图（README 用）。

    python tools/build_previews.py            # 全部
    python tools/build_previews.py hero       # 只出某几张
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
import flagkit as fk  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PRE = ROOT / "preview"
ASSETS = ROOT / "assets"

PINK, BLUE, AXIS = fk.PALETTE["pink"], fk.PALETTE["blue"], fk.PALETTE["axis"]
DARK_AXIS, _ = fk.solve_dark_axis()
DARKC = {"pink": PINK, "blue": BLUE, "axis": DARK_AXIS}

BG = "#0D1117"
BG2 = "#010409"
PANEL = "#161B22"
PANEL2 = "#1C232C"
BORDER = "#262D38"
TXT = "#E6EDF3"
TXT2 = "#9AA4B2"
TXT3 = "#6E7681"
L_BG = "#FFFFFF"
L_BG2 = "#F6F8FA"
L_PANEL = "#FFFFFF"
L_BORDER = "#D0D7DE"
L_TXT = "#1F2328"
L_TXT2 = "#59636E"

# --------------------------------------------------------------- 主题 ----
# 深色版：给「深色底演示」类图（可读性 / 色卡 / 深色场景 / 布面 / 变体）
# 浅色版：给 hero 与对比图 —— GitHub 默认浅色主题下的首屏
THEMES = {
    "dark": dict(bg=BG, panel=PANEL, panel2=PANEL2, border=BORDER,
                 txt=TXT, txt2=TXT2, txt3=TXT3, grid="#262D38", accent=PINK,
                 shadow_alpha=110, glow=40, chart_classic="#4A5361"),
    "light": dict(bg="#FFFFFF", panel="#F6F8FA", panel2="#EAEEF2", border="#D0D7DE",
                  txt="#1F2328", txt2="#59636E", txt3="#6E7781", grid="#D8DEE4",
                  accent="#C026D3",
                  shadow_alpha=46, glow=20, chart_classic="#8C959F"),
}
SUFFIX = {"dark": "", "light": "-light"}

#: 溯源水印：出现在 hero 与社交分享卡上
CREDIT_LINE = "Sakamonya · github.com/Sakamonya/trans-flag-hc · CC0"

SERIES = {"classic": "#6E7681", "hc": PINK}


# ------------------------------------------------------------- 画布 ----

def canvas(w: int, h: int, bg: str = BG) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (w, h), bg)
    return img, ImageDraw.Draw(img)


def vgrad(w: int, h: int, top: str, bottom: str) -> Image.Image:
    t = np.array(fk.hex_to_rgb(top), dtype=np.float32)
    b = np.array(fk.hex_to_rgb(bottom), dtype=np.float32)
    ramp = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    arr = (t[None, None, :] * (1 - ramp) + b[None, None, :] * ramp)
    arr = np.repeat(arr, w, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def glow(img: Image.Image, box, color: str, alpha=70, blur=90) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    r, g, b = fk.hex_to_rgb(color)
    ImageDraw.Draw(layer).ellipse(box, fill=(r, g, b, alpha))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def panel(img, box, radius=16, fill=PANEL, border=BORDER, width=1) -> None:
    ImageDraw.Draw(img).rounded_rectangle(box, radius=radius, fill=fill,
                                          outline=border if border else None, width=width)


def paste_flag(img: Image.Image, box, colors=None, radius=10, shadow=True, bands=None,
               shadow_alpha=110) -> None:
    x, y, w, h = box
    fl = fk.flag_exact(w, h, colors, bands, radius=radius)
    if shadow:
        fk.shadow(img, (x, y, x + w, y + h), radius, offset=(0, 16), blur=30, alpha=shadow_alpha)
    img.alpha_composite(fl, (x, y))


def T(d, x, y, s, size, color, weight="regular", align="l", valign="t", tracking=0.0):
    fk.draw_text(d, (x, y), s, size, color, weight, align=align, valign=valign, tracking=tracking)


def chip(img, d, x, y, color: str, name: str, size=200, gap=28) -> int:
    """色卡：方块 + 名称 + hex。返回占宽。"""
    d.rounded_rectangle((x, y, x + size, y + size), radius=size * 0.14, fill=color)
    T(d, x, y + size + 20, name, 24, TXT, "semibold")
    T(d, x, y + size + 54, color, 22, TXT2, "regular", tracking=0.6)
    return size + gap


def chip_inline(d, x, y, color: str, name: str, gap=230,
                txt=None, txt3=None) -> int:
    """横排小色卡：方块 + 右侧两行说明。返回占宽。"""
    txt = txt or TXT
    txt3 = txt3 or TXT3
    d.rounded_rectangle((x, y, x + 48, y + 48), radius=11, fill=color)
    T(d, x + 66, y - 6, name, 22, txt, "semibold")
    T(d, x + 66, y + 26, color, 20, txt3, "mono")
    return gap


# --------------------------------------------------------- 01 hero ----

def fig_hero(theme: str = "dark") -> None:
    th = THEMES[theme]
    W, H = 1600, 1000
    img, d = canvas(W, H, th["bg"])
    glow(img, (-260, 260, 1000, 1120), BLUE, alpha=th["glow"], blur=150)
    glow(img, (660, 260, 1900, 1120), PINK, alpha=th["glow"], blur=150)
    d = ImageDraw.Draw(img)

    T(d, W // 2, 62, "BASED ON MONICA HELMS · 1999", 24, th["txt3"], "regular",
      align="c", tracking=3.4)
    T(d, W // 2, 102, "跨性别骄傲旗", 66, th["txt"], "bold", align="c")
    T(d, W // 2, 190, "高对比版本  ·  High Contrast Edition", 30, th["accent"], "light",
      align="c", tracking=1.2)

    fw = 980
    fh = round(fw * 3 / 5)
    paste_flag(img, ((W - fw) // 2, 258, fw, fh), radius=14, shadow=True,
               shadow_alpha=th["shadow_alpha"])
    d = ImageDraw.Draw(img)

    x = (W - 3 * 230) // 2
    for name, col in (("粉 Pink", PINK), ("蓝 Blue", BLUE), ("中轴 Axis", AXIS)):
        x += chip_inline(d, x, 900, col, name, txt=th["txt"], txt3=th["txt3"])
    # 溯源水印：图常被单独转走（不带仓库），这一行让人找得回来
    T(d, W // 2, 958, CREDIT_LINE, 20, th["txt3"], "regular", align="c", tracking=0.6)
    out = f"01-hero{SUFFIX[theme]}.png"
    img.convert("RGB").save(PRE / out, optimize=True)
    print(f"  {out}")


# ------------------------------------------------------ 02 social ----

def fig_social() -> None:
    W, H = 1200, 630
    img, d = canvas(W, H, BG)
    glow(img, (-200, 120, 700, 900), BLUE, alpha=46, blur=120)
    d.rectangle((0, 0, W, 6), fill=PINK)

    fw = 560
    fh = round(fw * 3 / 5)
    paste_flag(img, (76, (H - fh) // 2 + 8, fw, fh), radius=12, shadow=True)

    x = 700
    T(d, x, 150, "HIGH CONTRAST EDITION", 22, PINK, "semibold", tracking=2.6)
    T(d, x, 192, "Trans Pride Flag", 54, TXT, "bold")
    T(d, x, 262, "跨性别骄傲旗 · 高对比版", 34, TXT, "light")
    d.line((x, 322, x + 420, 322), fill=BORDER, width=2)
    T(d, x, 348, "粉—蓝—灰—蓝—粉", 24, TXT2)
    T(d, x, 388, "五条等宽 · 中轴翻暗 · 粉蓝对调", 24, TXT2)
    T(d, x, 428, "每个相邻边界都有对比", 24, TXT2)
    cx = x
    for col in (PINK, BLUE, AXIS):
        d.rounded_rectangle((cx, 496, cx + 26, 522), radius=6, fill=col)
        T(d, cx + 36, 496, col, 22, TXT3, "mono")
        cx += 150
    T(d, x, 572, CREDIT_LINE, 20, TXT3, "regular", tracking=0.4)
    img.convert("RGB").save(ASSETS / "social-card-1200x630.png", optimize=True)
    print("  assets/social-card-1200x630.png")


# ----------------------------------------------------- 03 compare ----

def bar_chart(img, d, box, groups, series, max_v, bg, fg, fg2, border) -> None:
    x, y, w, h = box
    ticks = 4
    for i in range(ticks + 1):
        v = max_v * i / ticks
        yy = y + h - h * i / ticks
        d.line((x, yy, x + w, yy), fill=border, width=1)
        T(d, x - 16, yy, f"{v:.0f}", 20, fg2, "regular", align="r", valign="m")
    gw = w / len(groups)
    bw = gw * 0.24
    for gi, (label, vals) in enumerate(groups):
        cx = x + gw * gi + gw / 2
        for si, key in enumerate(series):
            v = vals[key]
            bx = cx - bw * 1.18 + si * bw * 1.36
            bh = h * v / max_v
            col = series[key]["color"]
            d.rounded_rectangle((bx, y + h - bh, bx + bw, y + h), radius=6, fill=col)
            T(d, bx + bw / 2, y + h - bh - 14, f"{v:.2f}", 22, fg, "semibold",
              align="c", valign="b")
        T(d, cx, y + h + 26, label, 24, fg2, "regular", align="c")


def fig_compare(theme: str = "dark") -> None:
    th = THEMES[theme]
    W, H = 1600, 1340
    img, d = canvas(W, H, th["bg"])
    T(d, 96, 66, "1999 原版  vs  高对比版", 50, th["txt"], "bold")
    T(d, 96, 132, "同一套五条结构，只改明暗关系与色彩强度。下面的数字都是 WCAG 2.1 对比度。",
      24, th["txt2"])

    cols = [(140, "经典版 · 1999", fk.CLASSIC), (860, "高对比版 · 本仓库", fk.PALETTE)]
    fw, fh = 600, round(600 * 3 / 5)
    for x, title, colors in cols:
        T(d, x, 210, title, 30, th["txt"], "semibold")
        panel(img, (x - 20, 262, x + fw + 20, 262 + fh + 40), radius=18, fill=th["panel"],
              border=th["border"])
        paste_flag(img, (x, 282, fw, fh), colors, radius=8, shadow=False)
        d = ImageDraw.Draw(img)
        rows = [("粉 / 中轴", fk.contrast(colors["pink"], colors["axis"])),
                ("蓝 / 中轴", fk.contrast(colors["blue"], colors["axis"])),
                ("粉 / 蓝", fk.contrast(colors["pink"], colors["blue"]))]
        yy = 282 + fh + 42
        for name, v in rows:
            T(d, x, yy, name, 24, th["txt2"])
            T(d, x + fw, yy, f"{v:.2f} : 1", 24,
              th["txt"] if v > 4 else th["txt2"], "semibold", align="r")
            yy += 42

    gy = 900
    T(d, 96, gy - 52, "相邻边界对比度", 30, th["txt"], "semibold")
    groups = [
        ("粉 / 中轴", {"classic": fk.contrast(fk.CLASSIC["pink"], fk.CLASSIC["axis"]),
                       "hc": fk.contrast(PINK, AXIS)}),
        ("蓝 / 中轴", {"classic": fk.contrast(fk.CLASSIC["blue"], fk.CLASSIC["axis"]),
                       "hc": fk.contrast(BLUE, AXIS)}),
        ("粉 / 蓝", {"classic": fk.contrast(fk.CLASSIC["pink"], fk.CLASSIC["blue"]),
                     "hc": fk.contrast(PINK, BLUE)}),
    ]
    series = {"classic": {"color": th["chart_classic"], "name": "经典版 1999"},
              "hc": {"color": PINK, "name": "高对比版"}}
    bar_chart(img, d, (180, gy, 1120, 300), groups, series, 8, th["bg"],
              th["txt"], th["txt2"], th["grid"])
    lx = 1360
    for i, k in enumerate(("classic", "hc")):
        d.rounded_rectangle((lx, gy + 16 + i * 44, lx + 26, gy + 38 + i * 44), radius=6,
                            fill=series[k]["color"])
        T(d, lx + 42, gy + 27 + i * 44, series[k]["name"], 24, th["txt2"], valign="m")

    T(d, 96, 1282, "原版粉与蓝的相对亮度几乎持平（1.04），整面旗靠中间那条白撑住辨识度；"
                   "本版每个相邻边界都拉开，缩小后仍能读出五条。", 24, th["txt2"])
    out = f"02-compare{SUFFIX[theme]}.png"
    img.convert("RGB").save(PRE / out, optimize=True)
    print(f"  {out}")


# -------------------------------------------------- 04 legibility ----

def legibility_strip(img, row_h, d, x, y, sizes, light: bool, label_w=230) -> None:
    """左标签列 + 两行（经典版 / 高对比版），各尺寸按底边对齐。"""
    fg2 = L_TXT2 if light else TXT2
    gap = 40
    cx = x + label_w
    y2 = y + row_h + 24
    T(d, x + label_w - 24, y + row_h - 22, "经典版 1999", 22, fg2, "regular", align="r")
    T(d, x + label_w - 24, y2 + row_h - 22, "高对比版", 22, PINK, "semibold", align="r")
    for s in sizes:
        ww = round(s * 5 / 3)
        T(d, cx + ww / 2, y - 34, f"{s}px", 20, fg2, "regular", align="c")
        img.alpha_composite(fk.flag_exact(ww, s, fk.CLASSIC), (cx, y + row_h - s))
        img.alpha_composite(fk.flag_exact(ww, s, fk.PALETTE), (cx, y2 + row_h - s))
        cx += ww + gap


def fig_legibility() -> None:
    W, H = 1600, 1280
    img, d = canvas(W, H, BG)
    T(d, 96, 62, "小尺寸可读性实测", 50, TXT, "bold")
    T(d, 96, 128, "同一组尺寸，分别放在浅色底与深色底上，按底边对齐。数字为该旗的宽度（px）。",
      24, TXT2)

    sizes = [160, 96, 64, 48, 32, 24, 16]
    row_h = 160
    for light, top in ((True, 210), (False, 740)):
        bg = L_BG2 if light else "#08090C"
        fg2 = L_TXT2 if light else TXT2
        panel(img, (76, top, W - 76, top + 490), radius=20, fill=bg,
              border=L_BORDER if light else BORDER)
        T(d, 108, top + 28, "浅色底 · 白纸 / 浅色 UI" if light else "深色底 · GitHub Dark #0D1117",
          24, fg2, "semibold")
        legibility_strip(img, row_h, d, 108, top + 110, sizes, light)

    T(d, W // 2, 1276, "24px 起高对比版的五条仍分得清；原版在 48px 以下粉与蓝已并成一条。",
      24, TXT2, "regular", align="c")
    img.convert("RGB").save(PRE / "03-legibility.png", optimize=True)
    print("  03-legibility.png")


# --------------------------------------------------- 05 color spec ----

def fig_spec() -> None:
    W, H = 1600, 1340
    img, d = canvas(W, H, BG)
    T(d, 96, 62, "色彩规格", 50, TXT, "bold")
    T(d, 96, 128, "取色、复用、二次创作都照这张表。改色请改 tools/flagkit.py 后重跑构建脚本。",
      24, TXT2)

    cards = [("粉 Pink", PINK, "第 1、5 条 · 外圈"), ("蓝 Blue", BLUE, "第 2、4 条"),
             ("中轴 Axis", AXIS, "第 3 条 · 整面旗最暗")]
    for i, (name, col, role) in enumerate(cards):
        x = 96 + i * 456
        panel(img, (x, 200, x + 416, 620), radius=18, fill=PANEL, border=BORDER)
        d.rounded_rectangle((x + 28, 228, x + 388, 372), radius=12, fill=col,
                            outline=BORDER, width=1)
        T(d, x + 28, 398, name, 30, TXT, "semibold")
        T(d, x + 28, 438, role, 22, TXT3)
        h_, s_, l_ = fk.rgb_to_hsl(col)
        r, g, b = fk.hex_to_rgb(col)
        T(d, x + 28, 492, col, 30, TXT, "mono")
        T(d, x + 28, 548, f"RGB {r}, {g}, {b}", 21, TXT3, "mono")
        T(d, x + 28, 580, f"H{h_:.0f}° S{s_*100:.0f}% L{l_*100:.0f}%", 21, TXT3, "mono")

    T(d, 96, 676, "结构", 30, TXT, "semibold")
    fw = 760
    fh = round(fw * 3 / 5)
    paste_flag(img, (96, 726, fw, fh), radius=8, shadow=False)
    d = ImageDraw.Draw(img)
    for i, key in enumerate(fk.BANDS):
        y = 726 + fh * (i + 0.5) / 5
        T(d, 96 + fw + 24, y, f"{i+1}", 22, TXT3, "mono", align="r", valign="m")
    T(d, 96, 726 + fh + 22, "五条等宽 · 粉—蓝—灰—蓝—粉 · 上下对称", 22, TXT3)

    x0 = 1000
    T(d, x0, 640, "相对亮度", 30, TXT, "semibold")
    base = 1000
    for i, (nm, col) in enumerate((("粉", PINK), ("蓝", BLUE), ("轴", AXIS))):
        y = fk.relative_luminance(col)
        bh = fh * y
        x = x0 + i * 160
        d.rounded_rectangle((x, base - bh, x + 100, base), radius=8, fill=col)
        T(d, x + 50, base - bh - 16, f"{y*100:.0f}%", 22, TXT2, "semibold", align="c", valign="b")
        T(d, x + 50, base + 20, nm, 24, TXT2, align="c")
    d.line((x0, base + 1, x0 + 460, base + 1), fill=BORDER, width=2)
    T(d, x0, base + 80, "亮度差就是边界强度——", 22, TXT3)
    T(d, x0, base + 114, "粉比中轴亮 14 倍，蓝比中轴亮 6.9 倍；", 22, TXT3)
    T(d, x0, base + 148, "原版的粉与蓝只差 1.04 倍，全靠白条撑住。", 22, TXT3)

    d.line((96, 1220, W - 96, 1220), fill=BORDER, width=2)
    T(d, 96, 1250, "本仓库唯一正式规格即上表三色（定稿版）。成品文件、预览图、调色器网页三处默认值已对齐。",
      24, TXT2)
    T(d, 96, 1290, "深色 UI 另有亮轴变体（中轴 #525252），只用于深色底，不替代正式规格。", 24, TXT2)
    img.convert("RGB").save(PRE / "04-color-spec.png", optimize=True)
    print("  04-color-spec.png")


# ------------------------------------------------- 06 dark UI 场景 ----

def fig_scene() -> None:
    W, H = 1600, 1120
    img, d = canvas(W, H, BG2)
    glow(img, (-100, -200, 900, 600), BLUE, alpha=40, blur=140)
    T(d, 96, 58, "深色场景应用", 50, TXT, "bold")
    T(d, 96, 124, "GitHub 深色 / 暗色 Banner / 头像 / 通知卡。深色底上建议用亮轴变体或描边版。",
      24, TXT2)

    # 浏览器窗口
    win = (110, 200, 1490, 940)
    fk.shadow(img, win, 20, offset=(0, 24), blur=44, alpha=130)
    panel(img, win, radius=20, fill=PANEL, border=BORDER)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((110, 200, 1490, 254), radius=20, fill=PANEL2)
    d.rectangle((110, 234, 1490, 254), fill=PANEL2)
    for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        d.ellipse((140 + i * 26, 218, 154 + i * 26, 232), fill=c)
    d.rounded_rectangle((236, 212, 900, 242), radius=15, fill="#0D1117")
    T(d, 258, 227, "github.com/your-name/trans-flag-hc", 20, TXT3, "mono", valign="m")

    # banner（深色底 → 用亮轴变体）
    fl = fk.flag_exact(1380, 306, DARKC)
    img.alpha_composite(fl, (110, 254))
    d = ImageDraw.Draw(img)

    # 头像（压住 banner 下沿）
    av = 168
    ax, ay = 168, 560 - av // 2 - 10
    d.ellipse((ax - 7, ay - 7, ax + av + 7, ay + av + 7), fill=PANEL)
    badge = fk.flag_image(av, av).convert("RGBA")
    mask = Image.new("L", (av, av), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, av - 1, av - 1), fill=255)
    badge.putalpha(mask)
    img.alpha_composite(badge, (ax, ay))
    d = ImageDraw.Draw(img)

    T(d, ax, ay + av + 26, "Your Name", 32, TXT, "bold")
    T(d, ax, ay + av + 68, "@your-name", 24, TXT3, "mono")
    T(d, ax, ay + av + 112, "把跨性别骄傲旗换成高对比版本：五条等宽、粉蓝对调、中轴翻暗。",
      24, TXT2)

    bx = 1180
    d.rounded_rectangle((bx, ay + 6, bx + 220, ay + 58), radius=26, fill="#238636")
    T(d, bx + 110, ay + 32, "Follow", 24, "#FFFFFF", "semibold", align="c", valign="m")

    # 通知卡
    card = (168, 800, 1432, 900)
    d.rounded_rectangle(card, radius=14, fill=PANEL2, outline=BORDER, width=1)
    mini = fk.flag_exact(96, 58, radius=6)
    img.alpha_composite(mini, (196, 821))
    d = ImageDraw.Draw(img)
    T(d, 316, 828, "trans-flag-hc 有新提交  ·  README.md  +214  −38", 24, TXT)
    T(d, 316, 862, "每个相邻边界都有对比  —  2 分钟前", 21, TXT3)

    T(d, 96, 1000, "深色底上的关键一条：中轴 #383838 与 #0D1117 的对比度只有 1.61:1，"
                   "中轴会被背景吃掉。", 24, TXT2)
    T(d, 96, 1040, "上图的 banner 用的是亮轴变体（中轴 "
                   f"{DARK_AXIS}，边界对比度 2.42:1），五条结构在深色底上完整保留。", 24, PINK)
    img.convert("RGB").save(PRE / "05-scene-dark-ui.png", optimize=True)
    print("  05-scene-dark-ui.png")


# ------------------------------------------------ 07 布面实物渲染 ----

def cloth(flag: Image.Image, amp=20.0, wavelength=235.0, phase=0.4, depth=0.26) -> Image.Image:
    """按布面折皱做横向位移 + 逐列明暗调制（双线性取样，避免锯齿）。"""
    w, h = flag.size
    arr = np.asarray(flag.convert("RGB"), dtype=np.float32)
    xs = np.arange(w, dtype=np.float32)[None, :]
    ys = np.arange(h)[:, None]
    ph = 2 * np.pi * xs / wavelength + phase
    fold = np.sin(ph) * 0.70 + np.sin(ph * 2.7 + 1.1) * 0.30
    src = np.clip(xs + amp * fold, 0, w - 1)
    x0 = np.floor(src).astype(np.int32)
    x1 = np.minimum(x0 + 1, w - 1)
    t = (src - x0).astype(np.float32)
    out = arr[ys, x0] * (1 - t)[..., None] + arr[ys, x1] * t[..., None]

    light = 0.78 + depth * (fold + 1) / 2 * 1.30
    edge = np.clip(np.minimum(ys, h - 1 - ys) / (h * 0.06), 0, 1)
    light = light * (0.90 + 0.10 * edge)
    out = np.clip(out * light[..., None], 0, 255).astype(np.uint8)

    rgb = Image.fromarray(out, "RGB").convert("RGBA")
    valid = ((xs + amp * fold) >= 0) & ((xs + amp * fold) <= w - 1)
    a = np.repeat(valid.astype(np.float32), h, axis=0) * 255
    rgb.putalpha(Image.fromarray(a.astype(np.uint8), "L"))
    return rgb


def fig_cloth() -> None:
    W, H = 1600, 1120
    img = vgrad(W, H, "#20242B", "#0F1216")
    glow(img, (400, 300, 1300, 940), "#FFFFFF", alpha=16, blur=170)
    d = ImageDraw.Draw(img)
    T(d, 96, 58, "实物感预览", 50, TXT, "bold")
    T(d, 96, 124, "同一组色值按布面折叠渲染——检验它在真实光照下是否还成立。", 24, TXT2)

    fw, fh = 1000, round(1000 * 3 / 5)
    x, y = (W - fw) // 2, 200
    fk.shadow(img, (x + 10, y + 18, x + fw - 10, y + fh + 24), 6, offset=(0, 26), blur=42, alpha=150)
    img.alpha_composite(cloth(fk.flag_image(fw, fh)), (x, y))
    d = ImageDraw.Draw(img)

    d.rounded_rectangle((x - 80, y - 32, x + fw + 80, y - 14), radius=8, fill="#2E333B")
    d.rounded_rectangle((x - 80, y - 32, x + fw + 80, y - 25), radius=4, fill="#3C424B")
    for cx in (x + 50, x + fw - 50):
        d.rounded_rectangle((cx - 16, y - 36, cx + 16, y + 28), radius=8, fill="#454B54")
        d.rounded_rectangle((cx - 16, y - 36, cx + 16, y - 25), radius=6, fill="#565D68")

    kx, ky, kw = 96, 850, 320
    kh = round(kw * 3 / 5)
    d.rounded_rectangle((kx - 20, ky - 20, kx + kw + 20, ky + kh + 74), radius=16,
                        fill="#161A20", outline=BORDER, width=1)
    img.alpha_composite(fk.flag_exact(kw, kh, radius=6), (kx, ky))
    d = ImageDraw.Draw(img)
    T(d, kx, ky + kh + 22, "同一色值的扁平版", 22, TXT3)

    tx = kx + kw + 90
    T(d, tx, ky - 6, "褶皱吃掉的只是明度，吃不掉结构。", 30, TXT, "semibold")
    T(d, tx, ky + 52, "粉条的暗面仍比中轴的亮面亮，蓝条在任何一个褶皱相位上都不会与中轴合并——",
      24, TXT2)
    T(d, tx, ky + 88, "这是「每个相邻边界都有对比」在实物上的收益。", 24, TXT2)
    img.convert("RGB").save(PRE / "06-cloth.png", optimize=True)
    print("  06-cloth.png")


# --------------------------------------------- 08 深底问题与解法 ----

def fig_darkbg() -> None:
    W, H = 1400, 800
    img, d = canvas(W, H, BG)
    T(d, 80, 54, "深色底上的中轴问题", 46, TXT, "bold")
    T(d, 80, 116, "同一面旗放进 GitHub 深色底，中轴与背景的对比度决定了五条结构还在不在。",
      24, TXT2)

    cols = [
        ("经典版 1999", fk.CLASSIC, "中轴是白的，边界 1.87:1", "#FFFFFF"),
        ("高对比版 · 定稿", fk.PALETTE, "中轴 #383838  边界 1.61:1  ← 会被吃掉", "#FF7B72"),
        ("亮轴变体 · 深色 UI 专用", DARKC, f"中轴 {DARK_AXIS}  边界 2.42:1", "#3FB950"),
    ]
    cw, ch = round(1200 * 3 / 5), 0
    for i, (title, colors, note, tone) in enumerate(cols):
        x = 80 + i * 424
        w = 360
        h = round(w * 3 / 5)
        panel(img, (x, 210, x + w, 210 + h + 150), radius=16, fill=fk.DARK_BG, border=BORDER)
        paste_flag(img, (x, 210, w, h), colors, radius=0, shadow=False, bands=fk.BANDS)
        d = ImageDraw.Draw(img)
        T(d, x + 20, 210 + h + 24, title, 24, TXT, "semibold")
        T(d, x + 20, 210 + h + 62, note, 21, tone)
        # 中轴取样线
        d.line((x - 14, 210 + h // 2, x + w + 14, 210 + h // 2), fill=tone, width=2)

    T(d, 80, 590, "为什么不是简单加一圈白描边：描边只包住旗子外沿，救不了中间那条。中轴要么压到比背景深、", 24, TXT2)
    T(d, 80, 626, "要么抬到比背景亮。亮轴变体由脚本求解：在 #0D1117 上扫描全部灰度，取「与背景 / 蓝 / 粉", 24, TXT2)
    T(d, 80, 662, f"三条边界里最弱的那条」最大的解，得到 {DARK_AXIS}。", 24, TXT2)
    T(d, 80, 726, "浅色底上请用正式规格；亮轴变体只用于深色 UI，不要拿它当默认色值。", 24, PINK)
    img.convert("RGB").save(PRE / "07-dark-bg.png", optimize=True)
    print("  07-dark-bg.png")


# ---------------------------------------------------- 09 variants ----

def fig_variants() -> None:
    W, H = 1600, 1060
    img, d = canvas(W, H, BG)
    T(d, 96, 58, "变体清单", 50, TXT, "bold")
    T(d, 96, 124, "每种变体对应一种真实用途，全部由 tools/build_assets.py 产出。", 24, TXT2)

    cw, chh = 440, 360
    fw = 360
    fh = round(fw * 3 / 5)

    row1 = [
        ("标准版", "屏幕、印刷、默认", fk.PALETTE, "flag/trans-flag-hc.svg"),
        ("白描边版", "深色底直贴，边缘不糊", fk.PALETTE, "flag/…-outline-white.svg"),
        ("亮轴变体", "深色 UI 专用", DARKC, "flag/trans-flag-hc-dark-ui.svg"),
    ]
    for i, (name, use, colors, path) in enumerate(row1):
        x, y = 80 + i * 480, 190
        panel(img, (x, y, x + cw, y + chh), radius=16, fill=fk.DARK_BG, border=BORDER)
        if "描边" in name:
            d.rectangle((x + 40, y + 50, x + 40 + fw, y + 50 + fh), fill="#FFFFFF")
            img.paste(fk.flag_image(fw - 16, fh - 16), (x + 48, y + 58))
        else:
            paste_flag(img, (x + 40, y + 50, fw, fh), colors, radius=6, shadow=False)
        d = ImageDraw.Draw(img)
        T(d, x + 40, y + 50 + fh + 26, name, 26, TXT, "semibold")
        T(d, x + 40, y + 50 + fh + 64, use, 21, TXT3)

    row2 = [("单色 · 白", "刺绣、烫印、暗底", "#FFFFFF"),
            ("单色 · 粉", "亮底印刷、贴纸", PINK),
            ("圆形徽章", "头像挂件、贴纸", None)]
    for i, (name, use, col) in enumerate(row2):
        x, y = 80 + i * 480, 580
        panel(img, (x, y, x + cw, y + chh), radius=16, fill="#11151B", border=BORDER)
        if col is None:
            s = 180
            badge = fk.flag_image(s, s).convert("RGBA")
            mask = Image.new("L", (s, s), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, s - 1, s - 1), fill=255)
            badge.putalpha(mask)
            img.alpha_composite(badge, (x + (cw - s) // 2, y + 84))
        else:
            mw, mh = 300, 180
            gap = 3
            for k in range(5):
                bh = mh / 5
                yy = y + 84 + bh * k
                d.rounded_rectangle((x + (cw - mw) // 2, yy, x + (cw + mw) // 2, yy + bh - gap),
                                    radius=3, fill=col)
        d = ImageDraw.Draw(img)
        T(d, x + 40, y + 300, name, 26, TXT, "semibold")
        T(d, x + 40, y + 338, use, 21, TXT3)

    T(d, 96, 990, "改色 / 改比例 fork 即可：全部产物由 tools/ 下三个脚本按 flagkit.PALETTE 推导，"
                  "改两行重跑，图与文档一起更新。", 24, TXT2)
    img.convert("RGB").save(PRE / "08-variants.png", optimize=True)
    print("  08-variants.png")


FIGS = {
    "hero": fig_hero, "social": fig_social, "compare": fig_compare,
    "legibility": fig_legibility, "spec": fig_spec, "scene": fig_scene,
    "cloth": fig_cloth, "darkbg": fig_darkbg, "variants": fig_variants,
}


def main(argv: list[str]) -> None:
    PRE.mkdir(exist_ok=True)
    names = argv or list(FIGS)
    print(f"palette pink={PINK} blue={BLUE} axis={AXIS}  dark-axis={DARK_AXIS}")
    for n in names:
        if n in ("hero", "compare"):
            FIGS[n]("dark")
            FIGS[n]("light")
        else:
            FIGS[n]()


if __name__ == "__main__":
    main(sys.argv[1:])
