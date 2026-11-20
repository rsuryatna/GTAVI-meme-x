#!/usr/bin/env python3
"""meme10d: fix ONLY the green ellipse in meme10c.png.

- Erase the old green ellipse (largest green component in the poster
  area) with local-median inpainting + text-stroke restoration, keeping
  the two green checkmarks untouched.
- Draw ONE new flattened hand-drawn ellipse (superellipse, n=18) that
  encloses only the two 2026 lines, stays on the poster paper, clears
  every letter, encloses the gold star, and never touches the sticky
  note. Everything else is copied pixel-identical from meme10c.png.

Geometry (all measured from meme10c.png, 1024x1024):
  2025 row text: x 209-423, y 428-440
  2026 line 1:   x 209-398, y 455-468 ; checkmark x 434-440, y 460-467
  19 NOV 2026:   x 210-325, y 490-503
  gold star:      x ~415-438, y ~484-505
  sticky note:    left edge x ~460, bottom y ~475
  poster paper:   left x 195, right x ~470, bottom y 515-517
  New ellipse: superellipse n=18, centre (327, 478.5), a=126, b=31
    -> spans x 201-453, y 447.5-509.5; 3px stroke, green (34,139,34)
  Measured clearances: top arc 6px from 2025 row at centre, ~5.3px
  from the "2" at x=209; bottom arc ~4.5px below "19 NOV 2026" and
  ~4-6px above the paper bottom edge; left end 6px inside paper left
  edge; right end ~13px right of the checkmark, ~15px right of the
  star, ~7px left of the note. (A literal 6px on every side is
  geometrically impossible: the gaps are 14px (top) and 12px (bottom)
  for a 3px stroke, which needs 15px; this is the closest a closed
  loop can get without touching a letter.)
Deterministic: fixed seed (7) for the inpaint grain.
"""
import numpy as np
from PIL import Image, ImageDraw

SRC = '/home/hatch/workspace/makefun/gta6-meme-x-01/meme10c.png'
DST = '/home/hatch/workspace/makefun/gta6-meme-x-01/meme10d.png'

GREEN = (34, 139, 34)
ELLIPSE = dict(cx=327, cy=478.5, a=126, b=31, n=18, width=3)

im = Image.open(SRC).convert('RGB')
arr = np.array(im).astype(int)
H, W, _ = arr.shape
R, G, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

# ---- 1. find the old ellipse: ALL green pixels in the poster area ----
# (the old arc is broken into several components where it crosses the
# dark TV frame, and its blended edge pixels are darker than the strict
# mask, so take every greenish pixel, not just the largest component).
# A loose mask is safe here: paper, wall, TV frame, red X marks, gold
# star, sticky note and calendar are all far from green in G-R.
# The only green things in this region are the old ellipse and the two
# checkmarks, which are protected by the exclusion boxes below.
loose = (G > 75) & ((G - R) > 20) & ((G - B) > 10)
region = np.zeros_like(loose)
region[400:540, 150:500] = True
target = loose & region
# protect the two green checkmarks (measured boxes)
target[273:287, 430:444] = False   # 2013 checkmark
target[457:471, 430:444] = False   # 2026 checkmark
target[464:473, 447:455] = False   # 2026 checkmark tip
print('erase target pixels:', int(target.sum()))

# ---- 2. inpaint the erased pixels ----
out = arr.copy()
dark = (R < 100) & (G < 100) & (B < 100)
rng = np.random.default_rng(7)
tys, txs = np.where(target)
for y, x in zip(tys, txs):
    # (a) letter bottoms: dark text directly above within 3px, text band only
    if y <= 441:
        above = dark[max(0, y - 3):y, max(0, x - 2):x + 3]
        if above.any():
            ys2, xs2 = np.where(above)
            cols = arr[max(0, y - 3) + ys2, max(0, x - 2) + xs2]
            out[y, x] = np.median(cols, axis=0)
            continue
    # (b) vertical stroke continuity (e.g. TV frame edge). Neighbours
    #     must be DARK and NOT green / NOT themselves being erased, or
    #     the median inherits the arc's green tint.
    def _dark_clean(ys_, xs_):
        return [arr[yy, xx] for yy, xx in zip(ys_, xs_)
                if dark[yy, xx] and not loose[yy, xx] and not target[yy, xx]]
    up_cols = _dark_clean(range(max(0, y - 4), y), [x] * 4)
    dn_cols = _dark_clean(range(y + 1, min(H, y + 5)), [x] * 4)
    if up_cols and dn_cols:
        out[y, x] = np.median(np.array(up_cols + dn_cols), axis=0)
        continue
    # (c) horizontal stroke continuity (same green-exclusion)
    lf_cols = _dark_clean([y] * 4, range(max(0, x - 4), x))
    rt_cols = _dark_clean([y] * 4, range(x + 1, min(W, x + 5)))
    if lf_cols and rt_cols:
        out[y, x] = np.median(np.array(lf_cols + rt_cols), axis=0)
        continue
    # (d) local background: median of non-green, non-target neighbours
    #     in an 11x11 window. Dark pixels are INCLUDED: the median is
    #     robust to a minority of dark text strokes, and excluding them
    #     biased the fill toward the light tail, leaving a pale scar
    #     where the old arc ran over the dark wall / TV frame.
    y0, y1 = max(0, y - 5), min(H, y + 6)
    x0, x1 = max(0, x - 5), min(W, x + 6)
    win_green = loose[y0:y1, x0:x1]
    win_tgt = target[y0:y1, x0:x1]
    keep = ~(win_green | win_tgt)
    cols = arr[y0:y1, x0:x1][keep]
    if len(cols):
        base = np.median(cols, axis=0)
    else:
        base = np.array([160.0, 143.0, 127.0])
    out[y, x] = np.clip(base + rng.normal(0, 3, 3), 0, 255)

# ---- 3. draw the new flattened ellipse (superellipse) ----
img = Image.fromarray(out.astype(np.uint8))
dr = ImageDraw.Draw(img)
cx, cy, a, b, n = ELLIPSE['cx'], ELLIPSE['cy'], ELLIPSE['a'], ELLIPSE['b'], ELLIPSE['n']
pts = []
for k in range(720):
    t = 2 * np.pi * k / 720
    c, s = np.cos(t), np.sin(t)
    px = cx + a * np.sign(c) * abs(c) ** (2 / n)
    py = cy + b * np.sign(s) * abs(s) ** (2 / n)
    pts.append((px, py))
pts.append(pts[0])
dr.line(pts, fill=GREEN, width=ELLIPSE['width'], joint='curve')

img.save(DST)
print('wrote', DST)
