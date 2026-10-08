"""
flagkit — 共享内核：色值数学、排版、绘图原语。

供 build_assets.py / build_previews.py 共用。所有颜色以 sRGB hex 表示。
"""
from __future__ import annotations

import math
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------- 色值 ----

#: 正式规格（定稿版）。改这里即可整体换色。
PALETTE = {
    "pink": "#FFA6FF",
    "blue": "#0090FF",
    "axis": "#383838",
}

#: 深底亮轴变体：只改中轴，留给深色 UI 用。
DARK_VARIANT_AXIS = None  # 由 solve_dark_axis() 求值

#: 五条结构，上到下。对称。
BANDS = ["pink", "blue", "axis", "blue", "pink"]

#: 深色 / 浅色基准背景
DARK_BG = "#0D1117"      # GitHub dark
DARKER_BG = "#08090C"
LIGHT_BG = "#FFFFFF"
PAPER_BG = "#F6F8FA"

CLASSIC = {"pink": "#F5A9B8", "blue": "#5BCEFA", "axis": "#FFFFFF"}


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def rgb_to_hex(rgb) -> str:
    return "#%02X%02X%02X" % tuple(int(round(c)) for c in rgb[:3])


def blend(a: str, b: str, t: float) -> str:
    """线性插值两个 hex（sRGB 空间直接插）。"""
    ra, ga, ba = hex_to_rgb(a)
    rb, gb, bb = hex_to_rgb(b)
    return rgb_to_hex((ra + (rb - ra) * t, ga + (gb - ga) * t, ba + (bb - ba) * t))


# ------------------------------------------------------------ 色彩科学 ----

def _lin(c: float) -> float:
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(h: str) -> float:
    r, g, b = hex_to_rgb(h)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a: str, b: str) -> float:
    """WCAG 2.1 对比度。"""
    la, lb = relative_luminance(a), relative_luminance(b)
    if la < lb:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


def rgb_to_hsl(h: str) -> tuple[float, float, float]:
    r, g, b = (c / 255 for c in hex_to_rgb(h))
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        return 0.0, 0.0, l
    d = mx - mn
    s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
    if mx == r:
        hh = ((g - b) / d) % 6
    elif mx == g:
        hh = (b - r) / d + 2
    else:
        hh = (r - g) / d + 4
    return hh * 60, s, l


def hsl_to_hex(h: float, s: float, l: float) -> str:
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    seg = int(h // 60) % 6
    rgb = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][seg]
    return rgb_to_hex([(v + m) * 255 for v in rgb])


def _srgb_to_lab(h: str) -> tuple[float, float, float]:
    r, g, b = hex_to_rgb(h)
    rl, gl, bl = _lin(r), _lin(g), _lin(b)
    x = (0.4124 * rl + 0.3576 * gl + 0.1805 * bl) / 0.95047
    y = (0.2126 * rl + 0.7152 * gl + 0.0722 * bl) / 1.00000
    z = (0.0193 * rl + 0.1192 * gl + 0.9505 * bl) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a: str, b: str) -> float:
    """CIEDE2000 色差。ΔE<2 肉眼几乎不可辨，>5 明显。"""
    l1, a1, b1 = _srgb_to_lab(a)
    l2, a2, b2 = _srgb_to_lab(b)
    c1, c2 = math.hypot(a1, b1), math.hypot(a2, b2)
    cb = (c1 + c2) / 2
    g = 0.5 * (1 - math.sqrt(cb ** 7 / (cb ** 7 + 25 ** 7))) if cb else 0.5
    ap1, ap2 = (1 + g) * a1, (1 + g) * a2
    cp1, cp2 = math.hypot(ap1, b1), math.hypot(ap2, b2)

    def hue(ap, bp):
        if ap == 0 and bp == 0:
            return 0.0
        return math.degrees(math.atan2(bp, ap)) % 360

    h1, h2 = hue(ap1, b1), hue(ap2, b2)
    dl, dc = l2 - l1, cp2 - cp1
    if cp1 * cp2 == 0:
        dh_ang = 0.0
    else:
        dh_ang = h2 - h1
        if dh_ang > 180:
            dh_ang -= 360
        elif dh_ang < -180:
            dh_ang += 360
    dh = 2 * math.sqrt(cp1 * cp2) * math.sin(math.radians(dh_ang) / 2)
    lb = (l1 + l2) / 2
    cpb = (cp1 + cp2) / 2
    if cp1 * cp2 == 0:
        hb = h1 + h2
    elif abs(h1 - h2) <= 180:
        hb = (h1 + h2) / 2
    elif h1 + h2 < 360:
        hb = (h1 + h2 + 360) / 2
    else:
        hb = (h1 + h2 - 360) / 2
    t = (1 - 0.17 * math.cos(math.radians(hb - 30))
         + 0.24 * math.cos(math.radians(2 * hb))
         + 0.32 * math.cos(math.radians(3 * hb + 6))
         - 0.20 * math.cos(math.radians(4 * hb - 63)))
    sl = 1 + 0.015 * (lb - 50) ** 2 / math.sqrt(20 + (lb - 50) ** 2)
    sc = 1 + 0.045 * cpb
    sh = 1 + 0.015 * cpb * t
    rt = -2 * math.sqrt(cpb ** 7 / (cpb ** 7 + 25 ** 7)) * math.sin(
        math.radians(2 * (30 * math.exp(-(((hb - 275) / 25) ** 2)))))
    return math.sqrt((dl / sl) ** 2 + (dc / sc) ** 2 + (dh / sh) ** 2 + rt * (dc / sc) * (dh / sh))


# ---------------------------------------------------------------- 排版 ----

LATIN = "C:/Windows/Fonts/segoeui.ttf"
LATIN_SB = "C:/Windows/Fonts/seguisb.ttf"
LATIN_BD = "C:/Windows/Fonts/segoeuib.ttf"
LATIN_LT = "C:/Windows/Fonts/segoeuil.ttf"
CJK = "C:/Windows/Fonts/Deng.ttf"        # 等线
CJK_LT = "C:/Windows/Fonts/Dengl.ttf"    # 等线 Light
CJK_BD = "C:/Windows/Fonts/Dengb.ttf"    # 等线 Bold
MONO = "C:/Windows/Fonts/consola.ttf"
MONO_BD = "C:/Windows/Fonts/consolab.ttf"

_LIGHT_W = {"light": CJK_LT, "regular": CJK, "semibold": CJK_BD, "bold": CJK_BD, "mono": MONO}
_LATIN_W = {"light": LATIN_LT, "regular": LATIN, "semibold": LATIN_SB, "bold": LATIN_BD,
            "mono": MONO, "mono_bold": MONO_BD}


@lru_cache(maxsize=256)
def font(size: int, weight: str = "regular", script: str = "latin") -> ImageFont.FreeTypeFont:
    if weight in ("mono", "mono_bold"):
        return ImageFont.truetype(MONO_BD if weight == "mono_bold" else MONO, size)
    path = _LATIN_W[weight] if script == "latin" else _LIGHT_W[weight]
    return ImageFont.truetype(path, size)


def _is_cjk(ch: str) -> bool:
    o = ord(ch)
    return (0x2E80 <= o <= 0x9FFF) or (0x3000 <= o <= 0x303F) or (0xFF00 <= o <= 0xFFEF) or (0xFE30 <= o <= 0xFE4F)


def _runs(text: str):
    out, buf, cur = [], "", None
    for ch in text:
        c = _is_cjk(ch)
        if cur is None or c == cur:
            buf += ch
        else:
            out.append((buf, cur))
            buf = ch
        cur = c
    if buf:
        out.append((buf, cur))
    return out


def measure(draw: ImageDraw.ImageDraw, text: str, size: int, weight: str = "regular",
            tracking: float = 0.0) -> float:
    w = 0.0
    for chunk, cjk in _runs(text):
        f = font(size, weight, "cjk" if cjk else "latin")
        w += draw.textlength(chunk, font=f)
        if tracking:
            w += tracking * len(chunk)
    return w


def line_height(size: int, weight: str = "regular") -> int:
    a, d = font(size, weight).getmetrics()
    return a + d


def draw_text(draw: ImageDraw.ImageDraw, xy, text: str, size: int, color: str,
              weight: str = "regular", align: str = "l", valign: str = "t",
              tracking: float = 0.0) -> tuple[float, float]:
    """
    混排绘制：中文走等线，拉丁/数字走 Segoe UI，按基线对齐。
    align: l/c/r（水平）  valign: t/c/s（s = 以 y 为基线）
    返回 (x, y) 左上角。
    """
    x, y = xy
    total = measure(draw, text, size, weight, tracking)
    asc, desc = font(size, weight).getmetrics()
    if align == "c":
        x -= total / 2
    elif align == "r":
        x -= total
    if valign == "c":
        y -= (asc + desc) / 2
    elif valign == "m":          # 视觉居中（大写高度中点）
        y -= asc * 0.72
    elif valign == "b":
        y -= (asc + desc)
    elif valign == "s":
        y -= asc

    cursor = x
    for chunk, cjk in _runs(text):
        f = font(size, weight, "cjk" if cjk else "latin")
        draw.text((cursor, y + asc), chunk, font=f, fill=color, anchor="ls")
        cursor += draw.textlength(chunk, font=f)
        if tracking:
            cursor += tracking * len(chunk)
    return x, y


def wrap(draw: ImageDraw.ImageDraw, text: str, size: int, max_w: float,
         weight: str = "regular") -> list[str]:
    """按宽度折行；中文逐字断，拉丁按词断。"""
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur)
            cur = ""
            continue
        trial = cur + ch
        if measure(draw, trial, size, weight) > max_w and cur:
            if not _is_cjk(ch) and " " in cur.rstrip() and not _is_cjk(cur[-1]):
                head, _, tail = cur.rstrip().rpartition(" ")
                lines.append(head)
                cur = tail + ch
            else:
                lines.append(cur)
                cur = ch
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def draw_para(draw, xy, text, size, color, weight="regular", max_w=1000, leading=1.55,
              align="l") -> float:
    x, y = xy
    step = int(size * leading)
    for ln in wrap(draw, text, size, max_w, weight):
        draw_text(draw, (x, y), ln, size, color, weight, align=align, valign="t")
        y += step
    return y


# ------------------------------------------------------------ 绘图原语 ----

def rounded(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def shadow(img: Image.Image, box, radius, offset=(0, 14), blur=28, alpha=90) -> None:
    """在 img 上原地叠加一层柔和投影。"""
    x0, y0, x1, y1 = box
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((x0 + offset[0], y0 + offset[1], x1 + offset[0], y1 + offset[1]),
                        radius=radius, fill=(0, 0, 0, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(layer)


# ---------------------------------------------------------------- 旗帜 ----

def flag_image(width: int, height: int, colors: dict | None = None,
               bands: list[str] | None = None) -> Image.Image:
    """把旗子铺满给定画布（条纹等分整幅高度）。"""
    c = colors or PALETTE
    b = bands or BANDS
    img = Image.new("RGB", (width, height), c[b[0]])
    d = ImageDraw.Draw(img)
    y = 0.0
    for i, key in enumerate(b):
        y2 = round(height * (i + 1) / len(b))
        d.rectangle((0, round(y), width, y2), fill=c[key])
        y = y2
    return img


def flag_exact(width: int, height: int, colors: dict | None = None,
               bands: list[str] | None = None, radius: float = 0.0) -> Image.Image:
    """等分条纹，带可选圆角，返回 RGBA。"""
    img = flag_image(width, height, colors, bands).convert("RGBA")
    if radius:
        mask = Image.new("L", (width, height), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=255)
        img.putalpha(mask)
    return img


def fit_flag(box_w: int, box_h: int, colors: dict | None = None, bands=None,
             ratio: float = 5 / 3) -> Image.Image:
    """按 3:5 旗比例适配到框内。"""
    w = box_w
    h = round(w / ratio)
    if h > box_h:
        h = box_h
        w = round(h * ratio)
    return flag_exact(w, h, colors, bands)


def flag_svg(colors: dict | None = None, bands: list[str] | None = None,
             ratio: float = 5 / 3, unit: int = 1000, outline: str | None = None,
             outline_w: float = 0.0) -> str:
    """比例化 SVG：无论缩放都不损失精度（条纹按百分比定位）。"""
    c = colors or PALETTE
    b = bands or BANDS
    h = unit / ratio
    n = len(b)
    pad = outline_w
    W = unit + 2 * pad
    H = h + 2 * pad
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {H:g}" '
        f'width="{W:g}" height="{H:g}" role="img" aria-label="Trans pride flag, high contrast edition">',
        "  <title>Trans Flag · High Contrast Edition</title>",
    ]
    if outline:
        lines.append(f'  <rect x="0" y="0" width="{W:g}" height="{H:g}" fill="{outline}"/>')
    for i, key in enumerate(b):
        y = pad + h * i / n
        lines.append(f'  <rect x="{pad:g}" y="{y:.4f}" width="{unit:g}" height="{h / n:.4f}" fill="{c[key]}"/>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def mono_svg(color: str, ratio: float = 5 / 3, unit: int = 1000, gap: float = 6.0) -> str:
    """单色版：五条同色，条间留缝，底色透出。"""
    h = unit / ratio
    n = 5
    bh = h / n
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {unit:g} {h:g}" '
        f'width="{unit:g}" height="{h:g}" role="img" aria-label="Trans pride flag, one-color edition">',
        "  <title>Trans Flag · One-color Edition</title>",
    ]
    for i in range(n):
        y = bh * i + gap / 2
        lines.append(f'  <rect x="0" y="{y:.4f}" width="{unit:g}" height="{bh - gap:.4f}" fill="{color}"/>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def solve_dark_axis(bg: str = DARK_BG, pink: str | None = None, blue: str | None = None,
                    lo: int = 20, hi: int = 140) -> tuple[str, float]:
    """
    深底亮轴求解：在给定深色背景上，让中轴与「背景 / 粉 / 蓝」三个相邻边界
    里最弱的那一条最大化。返回 (hex, 最弱对比度)。
    """
    pink = pink or PALETTE["pink"]
    blue = blue or PALETTE["blue"]
    best, best_v = PALETTE["axis"], -1.0
    for v in range(lo, hi + 1):
        cand = rgb_to_hex((v, v, v))
        v_min = min(contrast(cand, bg), contrast(cand, pink), contrast(cand, blue))
        if v_min > best_v:
            best, best_v = cand, v_min
    return best, best_v


def tone(img: Image.Image, factor: float) -> Image.Image:
    """整体提亮/压暗（RGB 乘法）。"""
    from PIL import ImageEnhance
    return ImageEnhance.Brightness(img).enhance(factor)
