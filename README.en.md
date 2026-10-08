# Trans Pride Flag · High Contrast Edition

![license](assets/badge-license.svg) ![palette](assets/badge-palette.svg) ![formats](assets/badge-formats.svg)

A derivative redesign of the Transgender Pride Flag designed by **Monica Helms in 1999**.
The five equal stripes stay. What changed is the light–dark structure and the colour intensity:
the centre stripe flips from the **lightest** band in the flag to the **darkest**, pink and blue swap
places, blue is deepened, and pink is pushed to H300°.

In the original, pink and blue have a contrast ratio of just **1.04 : 1** — effectively none.
The flag is legible only because of the white stripe in the middle. Here every adjacent boundary
is pulled apart, so the structure survives being scaled down, placed on dark backgrounds,
or embroidered.

> **Get it** ｜ [SVG](flag/trans-flag-hc.svg) ｜ [1500×900](flag/trans-flag-hc-1500x900.png) ｜ [3000×1800](flag/trans-flag-hc-3000x1800.png) ｜ [avatar](assets/avatar-1080.png) ｜ [wallpaper](assets/wallpaper-1200x1800.png) ｜ [dark-UI variant](flag/trans-flag-hc-dark-ui-1500x900.png) ｜ [colouriser](https://sakamonya.github.io/trans-flag-hc/)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="preview/01-hero.png">
  <img alt="Trans pride flag, high contrast edition" src="preview/01-hero-light.png">
</picture>

---

<a id="toc"></a>

## Contents

| Design | Usage | More |
|---|---|---|
| [vs. the 1999 original](#compare) | [On dark backgrounds](#dark-bg) | [Files](#files) |
| [Small-size legibility](#legibility) | [Cloth render](#cloth) | [Colouriser](#colorizer) |
| [Colour specification](#palette) | [Usage notes](#usage) | [Rebuild](#rebuild) · [Licence](#license) |

---

<a id="compare"></a>

## How it differs from the 1999 original

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="preview/02-compare.png">
  <img alt="Comparison with the 1999 original" src="preview/02-compare-light.png">
</picture>

| | Classic 1999 | This version |
|---|---|---|
| Centre stripe | `#FFFFFF` white — brightest band | `#383838` charcoal — darkest band |
| Outer stripes | blue outside | **pink outside** |
| pink / axis | 1.87 : 1 | **6.78 : 1** |
| blue / axis | 1.80 : 1 | **3.59 : 1** |
| pink / blue | **1.04 : 1** | **1.89 : 1** |

Three decisions:

1. **The centre stripe goes from highlight to anchor.** The original white stands for transition,
   neutrality, possibility — an open blank. Darkening it moves the meaning from "open space" to
   "weight in the dark": still undefined, opposite in temperament. The flag stops floating and
   starts sitting; the eye is pulled to the dark centre while the pink and blue radiate outward.
2. **Pink and blue swap.** The outer stripes set the first impression. The original leads with cold
   colour, held in. This version leads with bright pink, pushed out and forward. Symmetry is intact,
   so Monica's line — "the flag is always right side up" — still holds.
3. **Pink is pushed to H300°.** `#F5A9B8` (H348°) → `#FFA6FF` (H300°), from a warm fleshy pink to
   a magenta. In the original, blue and pink encode the boy/girl binary; at 300° that reading is
   weakened — it is neither blue nor red.

---

<a id="legibility"></a>

## Small-size legibility

![Legibility test](preview/03-legibility.png)

Below 48 px the classic pink and blue merge into one band. This version still reads as five
stripes from 24 px upward.

---

<a id="palette"></a>

## Colour specification

![Colour specification](preview/04-color-spec.png)

There is exactly **one canonical specification** in this repository. The flag files, every preview
image, and the colouriser's defaults all use it:

| Stripe | Hex | RGB | HSL |
|---|---|---|---|
| Pink (1st, 5th) | `#FFA6FF` | 255, 166, 255 | H300° S100% L83% |
| Blue (2nd, 4th) | `#0090FF` | 0, 144, 255 | H206° S100% L50% |
| Axis (3rd) | `#383838` | 56, 56, 56 | H0° S0% L22% |

```css
:root{
  --flag-pink: #FFA6FF;
  --flag-blue: #0090FF;
  --flag-axis: #383838;
}
```

---

<a id="dark-bg"></a>

## On dark backgrounds

![The axis problem on dark backgrounds](preview/07-dark-bg.png)

On GitHub's dark background `#0D1117`, the axis `#383838` has a contrast ratio of only **1.61 : 1**.
It gets swallowed, and five stripes read as four. **Adding a white outline does not fix this** —
an outline only wraps the outer edge and cannot rescue the middle stripe.

So there is a separate **light-axis variant**: the axis becomes `#525252`, raising the axis-to-background
contrast from 1.61 to **2.42** (even the weakest of the three adjacent boundaries — against blue —
reaches 2.39). That value is not a guess — it is solved by scanning every grey on `#0D1117` and
maximising the weakest of the three adjacent boundaries (see `solve_dark_axis()` in `tools/flagkit.py`).

The light-axis variant is for **dark backgrounds only**. Do not treat it as the default.

![Dark UI scene](preview/05-scene-dark-ui.png)

---

<a id="cloth"></a>

## Cloth render

![Cloth render](preview/06-cloth.png)

The same colours rendered as folded cloth (procedural, not a photograph): folds take away
luminance, not structure.

---

<a id="files"></a>

## Files

| File | Size | Use |
|---|---|---|
| `flag/trans-flag-hc.svg` | vector | print, embroidery, heat transfer, any scale |
| `flag/trans-flag-hc-1500x900.png` | 1500×900 | screen |
| `flag/trans-flag-hc-3000x1800.png` | 3000×1800 | hi-dpi |
| `flag/trans-flag-hc-outline-white-1548x948.png`, `flag/trans-flag-hc-outline-white.svg` | 1548×948 / vector | 24 px white outline, drops onto dark backgrounds |
| `flag/trans-flag-hc-dark-ui-1500x900.png`, `flag/trans-flag-hc-dark-ui.svg` | 1500×900 / vector | light-axis variant, dark UI only |
| `flag/trans-flag-hc-onecolor-white-1500x900.png`, `flag/trans-flag-hc-onecolor-white.svg` | 1500×900 / vector | one-colour white, embroidery (transparent) |
| `flag/trans-flag-hc-onecolor-pink-1500x900.png`, `flag/trans-flag-hc-onecolor-pink.svg` | 1500×900 / vector | one-colour pink, stickers (transparent) |
| `assets/avatar-*.png` | square | avatars |
| `assets/avatar-round-1080.png`, `assets/avatar-round-512.png`, `assets/badge-ring-*.png` | round | avatars, stickers, badges |
| `assets/wallpaper-*.png` | portrait | phone wallpapers |
| `assets/social-card-1200x630.png` | 1200×630 | social card (drop straight into GitHub Social preview) |
| `preview/` | — | all preview images |
| `docs/index.html` | — | single-file colouriser (GitHub Pages entry) |

### Every variant at a glance

![Variants](preview/08-variants.png)

---

<a id="colorizer"></a>

## Colouriser

**Live version: <https://sakamonya.github.io/trans-flag-hc/>**

`docs/index.html` is a **single file** with no dependencies: you can also download it and open it directly.

- Independent pink / blue / axis controls, lightness sliders
- Axis width 0.4×–2.2×, one-click swap of pink and blue
- Outline toggle and weight, preview background: dark / light / checkerboard
- Three contrast ratios computed live with the same WCAG formula as the Python side
- Export PNG 1500×900, export ratio-based SVG, copy CSS variables

---

<a id="rebuild"></a>

## Fork and rebuild

Every asset in this repository is **generated by script**. Changing the colours means changing one
place:

```bash
# 1. edit PALETTE at the top of tools/flagkit.py
# 2. regenerate
python tools/build_assets.py
python tools/build_previews.py
# 3. verify (opens every image and compares pixels)
python tools/verify.py
```

`verify.py` samples pixels from every generated image, asserts they match `PALETTE`, and checks that
the SVGs, the web page defaults and the READMEs are in sync. If you fork this to try another palette,
run it once and you will know whether anything was missed.

Requirements: Python 3 + Pillow. Chinese glyphs use the system face "DengXian" and Latin uses
Segoe UI; on non-Windows systems replace the font paths in `tools/flagkit.py`.

---

<a id="usage"></a>

## Usage notes

- Dark-mode banners, dark UI → **light-axis variant** or the outlined version
- Print, embroidery, heat transfer → **SVG** or the one-colour versions
- Avatars, stickers → **round badge**
- Transparent background → export from the SVG
- Below 24 px wide → use three stripes only, or a one-colour outlined mark

---

<a id="license"></a>

## Licence

Everything in this repository is released under **CC0 1.0** (all rights waived, public domain),
see [LICENSE](LICENSE).

| | |
|---|---|
| **Original design** | **Monica Helms**, 1999. She publicly dedicated the Transgender Pride Flag to the trans community |
| **Derivative design** | **Sakamonya**. Keeps the original five-stripe structure and symmetry, rewrites the light–dark structure and colour intensity |
| **Implementation** | **蓝色大肥鱼** (Blue Big Fat Fish), an AI assistant — preview images, build scripts, documentation and repository setup |

CC0 means you may use anything here commercially, adapt it, or **omit credit** — including the flag
itself. Attribution is not a condition of use; it is a sentence you may say if you wish to:

> Original design by Monica Helms (1999), high-contrast derivative by Sakamonya
> https://github.com/Sakamonya/trans-flag-hc

**First published: 2026-10-08.** The commit, tag (`v1.0.0`) and Release timestamps in this
repository are publicly verifiable and can be used to establish the earliest provenance of this flag.

**Canonical source**: <https://github.com/Sakamonya/trans-flag-hc>

**On accounts using this name** — there are exactly **two** genuine identities:

| Identity | Note |
|---|---|
| GitHub [@Sakamonya](https://github.com/Sakamonya) | the account hosting this repository |
| QQ (with **QID `Sakamonya`**) | a QQ QID is network-wide unique — one QQ number can bind exactly one QID. Search `Sakamonya` inside QQ and you will find that single account |

**Any other account named Sakamonya (in any capitalisation) on any platform is not this author** and
has no connection to this design. If someone contacts you, offers commissions, asks for payment or
requests licensing under the name "Sakamonya", **verify through this repository's Issues or GitHub
direct messages first**.

The full record of the design decisions — who proposed what, which options were rejected, and the
measured numbers — is in [`docs/design-notes.md`](docs/design-notes.md) (Chinese).

> "The flag is always right side up — no matter where you are in your life, no matter which way
> you are going, you can find your own correct."
> — Monica Helms

[Back to contents](#toc) ｜ [中文 README](README.md)
