#!/usr/bin/env python3
"""meme10c: inpaint the meme10b checklist panel so it looks printed on the
original poster, then rewrite the checklist + circle + star.

Input : meme10b.png (1024x1024) - read-only, never modified.
Output: meme10c.png (1024x1024).

Method
------
1. Erase the flat panel (and the old circle/star) with paper repainted from a
   2D linear gradient fitted to CLEAN poster-paper samples (header band +
   right margin, 85th percentile per channel so dark letters don't pollute
   the fit), plus fixed-seed Gaussian grain matched to the photo's grain.
   The erase mask is feathered everywhere EXCEPT at the sticky note
   (kept pixel-identical) and the header ink (kept pixel-identical).
2. Rewrite the 7 checklist rows in DejaVu Sans Mono Bold 18 (no handwriting
   font exists on this system), each row on its own tile with a tiny fixed
   rotation jitter so it doesn't look machine-typed.
3. Redraw the green circle around the 2026 row with real clearance and the
   gold star at the row's right end. The sticky note is restored on top
   afterwards, exactly as in meme10b, so the layering matches.

Deterministic: fixed numpy seed for the grain; all coordinates fixed.
"""
import hashlib
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC = "/home/hatch/workspace/makefun/gta6-meme-x-01/meme10b.png"
DST = "/home/hatch/workspace/makefun/gta6-meme-x-01/meme10c.png"

MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT_SIZE = 18

INK = (32, 28, 26)        # dark marker ink
RED = (198, 32, 32)       # red X marks
GREEN = (34, 139, 34)     # green checks + circle
GOLD = (212, 160, 20)     # star
GOLD_DARK = (150, 110, 8)

# ---- measured geometry (1024x1024 canvas, from pixel measurement) ----
PANEL = (193, 240, 492, 518)          # erase rect (x0, y0, x1, y1), excl.
NOTE = (450, 376, 536, 490)           # sticky note rect, kept identical
TEXT_X0 = 208                         # checklist text left edge
MARK_X = 432                          # check/cross column
ROWS = [  # (text, mark, baseline_y, jitter_deg) — baselines measured
    # from meme10b's ink bands (header blue ink ends ~y264; row 1 top ~270)
    ("2013 \u2014 ANNOUNCED", "\u2713", 284, -0.4),
    ("2015 \u2014 STILL WAITING", "\u2717", 316, +0.3),
    ("2018 \u2014 STILL WAITING", "\u2717", 348, -0.2),
    ("2021 \u2014 STILL WAITING", "\u2717", 378, +0.5),
    ("2023 \u2014 STILL WAITING", "\u2717", 408, -0.5),
    ("2025 \u2014 STILL WAITING", "\u2717", 440, +0.2),
    ("2026 \u2014 RELEASED!!!", "\u2713", 468, -0.3),
    ("19 NOV 2026", None, 502, +0.4),
]
# Circle sized from the text block (x 208-445, y 454-505): the poster's
# left edge slants (x~155 at this height), so rx=152 stays on the paper.
CIRCLE = (326, 480, 152, 40)          # (cx, cy, rx, ry)
STAR_C = (427, 496)                   # gold star centre
STAR_R = 11

GRAIN_SIGMA = 4.0
GRAIN_SEED = 20261120


def percentile_patch(img, x0, x1, y0, y1, pct=85):
    """Robust paper colour of a patch: high percentile dodges dark letters."""
    arr = np.asarray(img.crop((x0, y0, x1, y1))).astype(np.float64)
    return np.percentile(arr.reshape(-1, 3), pct, axis=0)


def fit_paper_plane(img):
    """Paper colour as bilinear interpolation of four directly measured
    anchor points (least-squares on percentile samples proved unstable:
    one bright tape patch flipped the slope). Anchors were measured from
    clean poster paper: header band (~167,149,128), right margin
    (~162,144,130), bottom strip (~161,144,126).
    Returns (x0, y0, x1, y1, colours[2][2][3])."""
    anchors = {
        (200, 250): (168.0, 149.0, 130.0),
        (480, 250): (164.0, 146.0, 130.0),
        (200, 500): (162.0, 144.0, 127.0),
        (480, 500): (160.0, 143.0, 126.0),
    }
    return anchors


def paper_base(anchors, w, h):
    """Bilinear interpolation of the anchor colours over the canvas
    (constant extension outside the anchor rectangle)."""
    (x0, y0), (x1, y1) = (200, 250), (480, 500)
    c00 = np.array(anchors[(200, 250)])
    c10 = np.array(anchors[(480, 250)])
    c01 = np.array(anchors[(200, 500)])
    c11 = np.array(anchors[(480, 500)])
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float64)
    tx = np.clip((xs - x0) / (x1 - x0), 0.0, 1.0)
    ty = np.clip((ys - y0) / (y1 - y0), 0.0, 1.0)
    top = c00[None, None, :] * (1 - tx[:, :, None]) + c10[None, None, :] * tx[:, :, None]
    bot = c01[None, None, :] * (1 - tx[:, :, None]) + c11[None, None, :] * tx[:, :, None]
    return top * (1 - ty[:, :, None]) + bot * ty[:, :, None]


def header_ink_mask(img):
    """Header ink pixels to protect from erasing: dark blue-ish pixels
    (B clearly above R) in the header band, dilated 2px so the letters'
    soft antialiased edges survive too. Paper (B-R ~ -38), the green
    circle (B-R 0) and red marks (B-R << 0) are never caught."""
    a = np.asarray(img).astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    m = (b - r >= 4) & ((r + g + b) < 500)
    m[:225, :] = False
    m[272:, :] = False
    m[:, :190] = False
    m[:, 500:] = False
    # dilate 2px via max filter
    pm = Image.fromarray((m * 255).astype(np.uint8)).filter(
        ImageFilter.MaxFilter(5))
    return np.asarray(pm) > 0


def main():
    img = Image.open(SRC).convert("RGB")
    w, h = img.size
    assert (w, h) == (1024, 1024)
    orig = np.asarray(img).astype(np.float64)

    # ---- 1. erase mask ----
    mask = np.zeros((h, w), dtype=np.float64)
    x0, y0, x1, y1 = PANEL
    mask[y0:y1, x0:x1] = 1.0
    # keep the sticky note exactly
    nx0, ny0, nx1, ny1 = NOTE
    mask[ny0:ny1, nx0:nx1] = 0.0
    # feather (blur), then re-apply hard exclusions crisply
    m_img = Image.fromarray((mask * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(3))
    mask = np.asarray(m_img).astype(np.float64) / 255.0
    mask[ny0:ny1, nx0:nx1] = 0.0
    mask[header_ink_mask(img)] = 0.0

    # ---- 2. repaint paper: fitted plane + fixed-seed grain ----
    anchors = fit_paper_plane(img)
    print("paper anchors:", anchors)
    base = paper_base(anchors, w, h)
    rng = np.random.RandomState(GRAIN_SEED)
    grain = rng.normal(0.0, GRAIN_SIGMA, (h, w, 3))
    repaint = np.clip(base + grain, 0, 255)
    comp = orig * (1.0 - mask[:, :, None]) + repaint * mask[:, :, None]
    out = Image.fromarray(np.clip(comp, 0, 255).astype(np.uint8))

    # ---- 3. rewrite the checklist ----
    font = ImageFont.truetype(MONO_BOLD, FONT_SIZE)
    for text, mark, baseline, jitter in ROWS:
        tile = Image.new("RGBA", (280, 40), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        td.text((2, 8), text, font=font, fill=INK + (255,))
        if mark:
            mc = GREEN if mark == "\u2713" else RED
            td.text((MARK_X - TEXT_X0 + 2, 8), mark, font=font, fill=mc + (255,))
        tile = tile.rotate(jitter, resample=Image.BICUBIC, expand=False,
                           center=(140, 20))
        out.paste(tile, (TEXT_X0 - 2, baseline - 24), tile)

    # ---- 4. green circle (hand-drawn-style irregular ellipse) ----
    cx, cy, rx, ry = CIRCLE
    pts = []
    for deg in range(0, 360):
        th = math.radians(deg)
        f = 1.0 + 0.02 * math.sin(3 * th) + 0.015 * math.sin(5 * th + 1.3)
        pts.append((cx + rx * f * math.cos(th), cy + ry * f * math.sin(th)))
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.line(pts + [pts[0]], fill=GREEN + (255,), width=4, joint="curve")
    out.paste(ov, (0, 0), ov)

    # ---- 5. gold star ----
    sx, sy, sr = STAR_C[0], STAR_C[1], STAR_R
    sp = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        r = sr if i % 2 == 0 else sr * 0.45
        sp.append((sx + r * math.cos(ang), sy + r * math.sin(ang)))
    ov2 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od2 = ImageDraw.Draw(ov2)
    od2.polygon(sp, fill=GOLD + (255,), outline=GOLD_DARK + (255,))
    out.paste(ov2, (0, 0), ov2)

    # ---- 6. restore the sticky note pixels exactly (circle passes under it) ----
    orig_img = Image.open(SRC).convert("RGB")
    note = orig_img.crop((nx0, ny0, nx1, ny1))
    out.paste(note, (nx0, ny0))

    out.save(DST)
    data = open(DST, "rb").read()
    print("wrote", DST, len(data), "bytes")
    print("sha256", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
