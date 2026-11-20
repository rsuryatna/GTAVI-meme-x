#!/usr/bin/env python3
"""Build meme7.png — GTA VI download stuck at 99% (fake system status).

Flat-vector system dialog, drawn from scratch with PIL only. Deterministic:
fixed values, no randomness, no clock, no network.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "meme7.png"
GHOST = HERE / "ghost.png"

W, H = 1024, 1024

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

# Palette
BG = (11, 18, 32)          # deep navy page
CARD = (20, 28, 46)        # window panel
CARD_EDGE = (42, 54, 72)
DIVIDER = (34, 48, 74)
TRACK = (35, 47, 69)
MAGENTA = (230, 0, 126)    # make.fun magenta
WHITE = (255, 255, 255)
LABEL = (147, 161, 184)    # muted blue-grey
GREEN_BG = (12, 43, 26)
GREEN_EDGE = (34, 197, 94)
GREEN = (74, 222, 128)
DOT_R = (255, 95, 87)
DOT_Y = (254, 188, 46)
DOT_G = (40, 200, 64)


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(path, text, max_w, start):
    """Largest font size <= start whose rendered width fits max_w."""
    size = start
    while size > 10:
        f = font(path, size)
        if f.getlength(text) <= max_w:
            return f
        size -= 1
    return font(path, 10)


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # --- window card ---------------------------------------------------
    d.rounded_rectangle([48, 48, 976, 976], radius=24, fill=CARD,
                        outline=CARD_EDGE, width=3)

    # --- title bar: traffic lights + title -----------------------------
    for cx, col in ((84, DOT_R), (120, DOT_Y), (156, DOT_G)):
        d.ellipse([cx - 10, 78, cx + 10, 98], fill=col)
    title = font(BOLD, 38)
    d.text((512, 88), "GTA VI \u2014 DOWNLOAD", font=title, fill=WHITE,
           anchor="mm")
    d.line([72, 132, 952, 132], fill=DIVIDER, width=2)

    # --- big 99% --------------------------------------------------------
    pct = font(BOLD, 170)
    d.text((512, 228), "99%", font=pct, fill=WHITE, anchor="mm")

    # --- progress bar ----------------------------------------------------
    bx0, bx1, by0, by1 = 110, 914, 356, 410
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=14, fill=TRACK)
    fill_w = int((bx1 - bx0) * 0.99)
    d.rounded_rectangle([bx0, by0, bx0 + fill_w, by1], radius=14,
                        fill=MAGENTA)
    # square off the fill's right edge so the 1% gap reads as a gap
    d.rectangle([bx0 + fill_w - 14, by0, bx0 + fill_w, by1], fill=MAGENTA)
    left = font(REG, 24)
    d.text((bx0, 336), "DOWNLOADING: GRAND THEFT AUTO VI", font=left,
           fill=LABEL, anchor="lb")
    right = font(BOLD, 24)
    d.text((bx1, 336), "1% TO GO", font=right, fill=MAGENTA, anchor="rb")

    # --- status rows ------------------------------------------------------
    rows = [
        ("ELAPSED", "13 YEARS"),
        ("SPEED", "1 TRAILER / 3 YEARS"),
        ("ESTIMATED REMAINING", "UNKNOWN"),
        ("LAST UPDATE", "TRAILER 2 \u2014 MAY 2025"),
    ]
    y = 452
    for i, (label, value) in enumerate(rows):
        lf = font(BOLD, 28)
        vf = font(MONO_B, 30)
        d.text((110, y), label, font=lf, fill=LABEL, anchor="lm")
        d.text((914, y), value, font=vf, fill=WHITE, anchor="rm")
        if i < len(rows) - 1:
            d.line([110, y + 29, 914, y + 29], fill=DIVIDER, width=2)
        y += 58
    d.line([72, 700, 952, 700], fill=DIVIDER, width=2)

    # --- punchline box ----------------------------------------------------
    d.rounded_rectangle([80, 740, 944, 944], radius=18, fill=GREEN_BG,
                        outline=GREEN_EDGE, width=3)

    # ghost avatar: rounded tile, 132x111, vertically centred in the box
    ghost = Image.open(GHOST).convert("RGBA").resize((132, 111),
                                                    Image.LANCZOS)
    mask = Image.new("L", (132, 111), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, 131, 110], radius=14,
                                           fill=255)
    img.paste(ghost, (104, 787), mask)

    line1 = "MEANWHILE, MY AGENT DOWNLOADED $250"
    line2 = "FROM MAKE.FUN \u2014 DOWNLOAD COMPLETE \u2713"
    f1 = fit(BOLD, line1, 944 - 264 - 16, 32)
    f2 = fit(BOLD, line2, 944 - 264 - 16, 32)
    d.text((264, 806), line1, font=f1, fill=WHITE, anchor="lm")
    d.text((264, 862), line2, font=f2, fill=GREEN, anchor="lm")

    img.save(OUT)
    print(f"saved {OUT} {W}x{H}")


if __name__ == "__main__":
    main()
