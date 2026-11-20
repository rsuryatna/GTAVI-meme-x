#!/usr/bin/env python3
"""meme10b — overlay fixes on the user's own photo (do NOT redraw the scene).

Source: user's photo of an old man who waited since 2013 finally playing GTA VI.
Fixes overlaid on the original photo (all coordinates fixed, deterministic):
  1. Letterbox bars top/bottom (photo is 3:2 landscape; output must be square).
  2. Ghost portrait + "MY AGENT" in the top bar (competition requires the ghost).
  3. Red "PAID BY MY AI AGENT — $250 FROM MAKE.FUN" banner in the bottom bar.
  4. Checklist block on the wall poster covered with a clean cream panel and
     redrawn with correct dates (2013 announced ... 2026 RELEASED 19 NOV 2026).
  5. Yellow/pink sticky note covered with a fresh note reading "after 13 years".

Deterministic: fixed coordinates, fixed colors, no randomness, no timestamps.
"""
import math
from PIL import Image, ImageDraw, ImageFont

SRC = "/home/hatch/workspace/user/media_library/image/ae/aec909d049c85b49b52066e905e724c0df3eb944b3d1a4b4aed0745a91a9e18a.jpg"
GHOST = "/home/hatch/workspace/makefun/gta6-meme-x-01/ghost.png"
OUT = "/home/hatch/workspace/makefun/gta6-meme-x-01/meme10b.png"

W = 1024
BAR = (40, 33, 25)          # dark warm brown sampled from photo corners
MAGENTA = (214, 0, 110)     # make.fun ghost panel
RED = (200, 16, 46)         # banner red
GREEN = (34, 139, 34)
REDX = (200, 30, 30)
GOLD = (212, 160, 20)
INK = (35, 30, 28)          # near-black marker ink
NOTE_FILL = (192, 169, 104) # muted yellow, sampled from the original sticky note
NOTE_INK = (64, 48, 40)
TAPE = (226, 210, 175)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
F_BOLD = FONT_DIR + "DejaVuSans-Bold.ttf"
F_MONO = FONT_DIR + "DejaVuSansMono-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, start, max_w):
    """Largest font size (<= start) whose rendered width fits max_w."""
    size = start
    while size > 8:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return font(path, 8)


def star_points(cx, cy, r_outer, r_inner, rot=-90):
    pts = []
    for i in range(10):
        r = r_outer if i % 2 == 0 else r_inner
        a = math.radians(rot + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def heart_points(cx, cy, s):
    """Small heart polygon centred near (cx, cy), size s."""
    pts = []
    for deg in range(0, 361, 6):
        t = math.radians(deg)
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * s / 16.0, cy - y * s / 16.0))
    return pts


def main():
    photo = Image.open(SRC).convert("RGB")
    s = W / photo.width                      # 1024 / 1599
    ph = int(round(photo.height * s))        # 683
    y0 = (W - ph) // 2                       # 170

    canvas = Image.new("RGB", (W, W), BAR)
    canvas.paste(photo.resize((W, ph), Image.LANCZOS), (0, y0))
    d = ImageDraw.Draw(canvas)

    # ---------- top bar: ghost portrait + MY AGENT ----------
    panel = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([48, 15, 188, 155], radius=18, fill=MAGENTA + (255,))
    ghost = Image.open(GHOST).convert("RGBA")
    gw, gh = 116, 98
    gscale = min(gw / ghost.width, gh / ghost.height)
    ghost = ghost.resize((int(ghost.width * gscale), int(ghost.height * gscale)), Image.LANCZOS)
    panel.alpha_composite(ghost, (118 - ghost.width // 2, 85 - ghost.height // 2))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), panel).convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.text((212, 62), "MY AGENT", font=font(F_BOLD, 46), fill=(255, 255, 255), anchor="lm")
    d.text((212, 112), "HE PAID. I PLAY.", font=font(F_BOLD, 26), fill=(255, 205, 220), anchor="lm")

    # ---------- bottom bar: red banner ----------
    d.rounded_rectangle([36, 893, 988, 993], radius=14, fill=RED)
    banner = "PAID BY MY AI AGENT — $250 FROM MAKE.FUN"
    bf = fit_font(d, banner, F_BOLD, 40, 920)
    d.text((512, 943), banner, font=bf, fill=(255, 255, 255), anchor="mm")

    # ---------- checklist panel on the poster ----------
    # photo rect (308,150)-(758,544) -> final coords. Top edge sits just
    # below the "— SINCE 2013" header line (ends ~photo y 145); left edge
    # covers the stray × marks at the poster's left edge.
    px0, py0 = int(308 * s), y0 + int(150 * s)
    px1, py1 = int(758 * s), y0 + int(544 * s)
    pw, ph2 = px1 - px0, py1 - py0
    # soft drop shadow
    sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([px0 + 4, py0 + 5, px1 + 4, py1 + 5], fill=(0, 0, 0, 70))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), sh).convert("RGB")
    # cream panel with a very subtle top-left -> bottom-right darkening
    base = (176, 157, 138)
    grad = Image.new("RGB", (pw, ph2))
    pxdata = []
    for yy in range(ph2):
        for xx in range(pw):
            f = 1.0 - 0.10 * ((xx / pw + yy / ph2) / 2.0)
            pxdata.append((int(base[0] * f), int(base[1] * f), int(base[2] * f)))
    grad.putdata(pxdata)
    canvas.paste(grad, (px0, py0))
    d = ImageDraw.Draw(canvas)

    rows = [
        ("2013 — ANNOUNCED", "✓", GREEN),
        ("2015 — STILL WAITING", "✗", REDX),
        ("2018 — STILL WAITING", "✗", REDX),
        ("2021 — STILL WAITING", "✗", REDX),
        ("2023 — STILL WAITING", "✗", REDX),
        ("2025 — STILL WAITING", "✗", REDX),
        ("2026 — RELEASED!!!", "✓", GREEN),
        ("19 NOV 2026", "★", GOLD),
    ]
    mf = font(F_MONO, 18)
    y = py0 + 8
    for text, mark, color in rows:
        d.text((px0 + 9, y + 10), text, font=mf, fill=INK, anchor="lm")
        if mark == "★":
            d.polygon(star_points(px1 - 57, y + 10, 12, 5), fill=color)
        else:
            d.text((px1 - 45, y + 10), mark, font=mf, fill=color, anchor="rm")
        y += 31
    # green circle around the 2026 rows (last two lines)
    d.ellipse([px0 + 3, py0 + 8 + 6 * 31 - 4, px1 - 3, py1 - 4], outline=GREEN, width=4)

    # ---------- sticky note: fresh note, "after 13 years" ----------
    # True note footprint is photo (701,330)-(815,495); the patch is nudged
    # slightly right into plain wall so it clears the checklist marks
    # (which end at final x 440). It sits well clear of the man's
    # face/glasses (which start ~photo x 950).
    nx0, ny0, nx1, ny1 = 452, 378, 534, 488
    sh2 = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(sh2).rectangle([nx0 + 3, ny0 + 3, nx1 + 3, ny1 + 3], fill=(0, 0, 0, 60))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), sh2).convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.rectangle([nx0, ny0, nx1, ny1], fill=NOTE_FILL)
    nf = font(F_BOLD, 14)
    ncx = (nx0 + nx1) // 2
    d.text((ncx, ny0 + 14), "Finally...", font=nf, fill=NOTE_INK, anchor="ma")
    d.text((ncx, ny0 + 38), "after 13", font=nf, fill=NOTE_INK, anchor="ma")
    yw = d.textlength("years", font=nf)
    d.text((ncx - 8, ny0 + 62), "years", font=nf, fill=NOTE_INK, anchor="ma")
    d.polygon(heart_points(ncx + int(yw / 2) + 8, ny0 + 70, 6), fill=(200, 40, 60))

    canvas.save(OUT, "PNG")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
