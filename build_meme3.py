#!/usr/bin/env python3
"""Meme v3 — LEONIDA MUTUAL INSURANCE: CLAIM FOR DAMAGES.
Flat vector insurance-claim document, PIL only. No photo, no AI faces.
Official make.fun ghost reused from ghost.png (v1 press-kit extraction).
"""
import math, random
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
DIR = "/home/hatch/workspace/makefun/gta6-meme-x-01"
FONT = "/usr/share/fonts/truetype/liberation/"

PAPER   = (245, 239, 224)   # warm cream
NAVY    = (28, 43, 74)
MAGENTA = (230, 0, 126)     # make.fun magenta
STAMP   = (214, 0, 90)      # stamp red-magenta
INK     = (38, 38, 38)
FAINT   = (150, 143, 125)

def font(name, size):
    return ImageFont.truetype(FONT + name, size)

def fit(draw, text, name, size, max_w):
    """Shrink font until text fits max_w; returns (font, width)."""
    while size > 8:
        f = font(name, size)
        w = draw.textlength(text, font=f)
        if w <= max_w:
            return f, w
        size -= 1
    return font(name, 8), draw.textlength(text, font=font(name, 8))

def centered(draw, y, text, f, fill, x_center=W // 2):
    w = draw.textlength(text, font=f)
    draw.text((x_center - w / 2, y), text, font=f, fill=fill)
    return w

def letterspaced(draw, y, text, f, fill, tracking, x_center=W // 2):
    """Draw text with extra tracking, centered."""
    widths = [draw.textlength(ch, font=f) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = x_center - total / 2
    for ch, cw in zip(text, widths):
        draw.text((x, y), ch, font=f, fill=fill)
        x += cw + tracking
    return total

# ---------------------------------------------------------------- canvas
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# subtle paper vignette: faint darker edge
for i in range(24):
    d.rectangle([i, i, W - 1 - i, H - 1 - i], outline=(240 - i, 233 - i, 216 - i))

# double navy border
d.rectangle([26, 26, W - 27, H - 27], outline=NAVY, width=6)
d.rectangle([40, 40, W - 41, H - 41], outline=NAVY, width=2)

INNER_L, INNER_R = 78, W - 78   # text column
CW = INNER_R - INNER_L          # 868

# ---------------------------------------------------------------- seal (ghost on magenta disc)
SEAL_CX, SEAL_CY, SEAL_R = W // 2, 108, 46
d.ellipse([SEAL_CX - SEAL_R - 5, SEAL_CY - SEAL_R - 5,
           SEAL_CX + SEAL_R + 5, SEAL_CY + SEAL_R + 5], outline=NAVY, width=2)
d.ellipse([SEAL_CX - SEAL_R, SEAL_CY - SEAL_R,
           SEAL_CX + SEAL_R, SEAL_CY + SEAL_R], fill=MAGENTA)
d.ellipse([SEAL_CX - SEAL_R, SEAL_CY - SEAL_R,
           SEAL_CX + SEAL_R, SEAL_CY + SEAL_R], outline=(255, 255, 255), width=3)
ghost = Image.open(f"{DIR}/ghost.png").convert("RGBA")
gw = 70
gh = int(gw * ghost.height / ghost.width)
ghost = ghost.resize((gw, gh), Image.LANCZOS)
img.paste(ghost, (SEAL_CX - gw // 2, SEAL_CY - gh // 2 + 2), ghost)
d = ImageDraw.Draw(img)

# ---------------------------------------------------------------- header
y = 164
f, _ = fit(d, "LEONIDA MUTUAL INSURANCE CO.", "LiberationSerif-Bold.ttf", 44, CW)
centered(d, y, "LEONIDA MUTUAL INSURANCE CO.", f, NAVY)
y += 50
letterspaced(d, y, "EST. 2013  ·  WE COVER THE WAIT",
             font("LiberationSans-Bold.ttf", 20), MAGENTA, tracking=3)
y += 30
# small rule with diamond
d.line([INNER_L + 120, y + 8, W // 2 - 16, y + 8], fill=NAVY, width=2)
d.line([W // 2 + 16, y + 8, INNER_R - 120, y + 8], fill=NAVY, width=2)
d.polygon([(W // 2, y), (W // 2 + 8, y + 8), (W // 2, y + 16), (W // 2 - 8, y + 8)],
          fill=MAGENTA)
y += 26

# ---------------------------------------------------------------- meta block (mono)
meta = [
    "CLAIM NO. VI-2013      CLAIMANT: ONE PATIENT GAMER",
    "POLICY NO. GTA-V-2013  FILED: 19 NOV 2026",
]
for line in meta:
    f, _ = fit(d, line, "LiberationMono-Bold.ttf", 20, CW)
    centered(d, y, line, f, NAVY)
    y += 26
f, _ = fit(d, "INCIDENT: THE 13-YEAR WAIT", "LiberationMono-Bold.ttf", 22, CW)
centered(d, y, "INCIDENT: THE 13-YEAR WAIT", f, MAGENTA)
y += 30
d.line([INNER_L, y, INNER_R, y], fill=NAVY, width=3)
y += 12

# ---------------------------------------------------------------- schedule of losses
letterspaced(d, y, "SCHEDULE OF LOSSES",
             font("LiberationSans-Bold.ttf", 26), NAVY, tracking=6)
y += 34

ROWS = [
    ("DELAY NO. 1 — ", "ANNOUNCED THE WEEK MY HOLIDAY WAS BOOKED"),
    ("DELAY NO. 2 — ", "CONTROLLER THROWN, WALL DENTED"),
    ("EVERY LEAK — ", "READ AT 3 AM, BELIEVED, DEBUNKED BY NOON"),
    ("NAPKIN MAP OF LEONIDA — ", "REDRAWN 41 TIMES FROM MEMORY"),
    ("CONSOLE ON STANDBY — ", "NEVER SWITCHED OFF SINCE 2013"),
    ("DAY-ONE PATCH: 68 GB — ", "BIGGER THAN ALL OF GTA V"),
    ("MY TWENTIES — ", "SPENT EXPLAINING THE DELAYS TO MY MUM"),
]
ROW_H = 30
for lead, rest in ROWS:
    f_lead = font("LiberationSans-Bold.ttf", 22)
    f_rest = font("LiberationSans-Regular.ttf", 22)
    # auto-shrink if too wide
    size = 22
    while (d.textlength(lead, font=f_lead) + d.textlength(rest, font=f_rest) > CW
           and size > 14):
        size -= 1
        f_lead = font("LiberationSans-Bold.ttf", size)
        f_rest = font("LiberationSans-Regular.ttf", size)
    d.text((INNER_L, y), lead, font=f_lead, fill=NAVY)
    d.text((INNER_L + d.textlength(lead, font=f_lead), y), rest,
           font=f_rest, fill=INK)
    # faint dotted rule under the row
    yy = y + size + 7
    for xx in range(INNER_L, INNER_R, 9):
        d.line([xx, yy, xx + 4, yy], fill=FAINT, width=1)
    y += ROW_H

# kicker
f_lead = font("LiberationSans-Bold.ttf", 22)
f_rest = font("LiberationSans-Bold.ttf", 22)
d.text((INNER_L, y), "REFUNDS REQUESTED: 0 — ", font=f_lead, fill=MAGENTA)
d.text((INNER_L + d.textlength("REFUNDS REQUESTED: 0 — ", font=f_lead), y),
       "I NEVER GAVE UP", font=f_rest, fill=MAGENTA)
y += ROW_H + 2
d.line([INNER_L, y, INNER_R, y], fill=NAVY, width=3)
y += 10

# ---------------------------------------------------------------- total damages
f, _ = fit(d, "TOTAL DAMAGES:  13 YEARS", "LiberationSans-Bold.ttf", 32, CW)
centered(d, y, "TOTAL DAMAGES:  13 YEARS", f, NAVY)
y_total_end = y + 40

# ---------------------------------------------------------------- stamp (own layer, rotated)
stamp_w, stamp_h = 660, 120
layer = Image.new("RGBA", (stamp_w + 40, stamp_h + 40), (0, 0, 0, 0))
sd = ImageDraw.Draw(layer)
ox, oy = 20, 20
sd.rectangle([ox, oy, ox + stamp_w, oy + stamp_h], outline=STAMP, width=6)
sd.rectangle([ox + 9, oy + 9, ox + stamp_w - 9, oy + stamp_h - 9],
             outline=STAMP, width=2)
sy = oy + 10
f1, _ = fit(sd, "CLAIM APPROVED", "LiberationSans-Bold.ttf", 42, stamp_w - 36)
w1 = sd.textlength("CLAIM APPROVED", font=f1)
sd.text((ox + (stamp_w - w1) / 2, sy), "CLAIM APPROVED", font=f1, fill=STAMP)
sy += 46
f2, _ = fit(sd, "SETTLEMENT $250.00 PAID IN FULL BY MY AI AGENT",
            "LiberationSans-Bold.ttf", 23, stamp_w - 36)
w2 = sd.textlength("SETTLEMENT $250.00 PAID IN FULL BY MY AI AGENT", font=f2)
sd.text((ox + (stamp_w - w2) / 2, sy),
        "SETTLEMENT $250.00 PAID IN FULL BY MY AI AGENT", font=f2, fill=STAMP)
sy += 28
f3, _ = fit(sd, "EARNED ON MAKE.FUN WHILE I WAITED",
            "LiberationSans-Bold.ttf", 23, stamp_w - 36)
w3 = sd.textlength("EARNED ON MAKE.FUN WHILE I WAITED", font=f3)
sd.text((ox + (stamp_w - w3) / 2, sy),
        "EARNED ON MAKE.FUN WHILE I WAITED", font=f3, fill=STAMP)
# light distress speckles so the stamp reads as stamped ink
random.seed(2013)
px = layer.load()
for _ in range(2200):
    x = random.randint(ox, ox + stamp_w)
    x2 = random.randint(oy, oy + stamp_h)
    if px[x, x2][3] > 0 and random.random() < 0.5:
        layer.putpixel((x, x2), (0, 0, 0, 0))
layer = layer.rotate(-4, resample=Image.BICUBIC, expand=True)
# dynamic placement: stamp must end before the footer zone
FOOTER_H = 30
stamp_y = y_total_end + 4
max_stamp_bottom = H - 40 - FOOTER_H - 4
if stamp_y + layer.height > max_stamp_bottom:
    stamp_y = max_stamp_bottom - layer.height
assert stamp_y >= y_total_end - 6, f"stamp overlaps total-damages line: {stamp_y}"
img.paste(layer, (W // 2 - layer.width // 2, stamp_y), layer)
d = ImageDraw.Draw(img)

# ---------------------------------------------------------------- footer
fy = stamp_y + layer.height + 10
f, _ = fit(d, "NEXT CLAIM: GTA VII — PLEASE FILE IN 2039.",
           "LiberationMono-Bold.ttf", 20, CW)
centered(d, fy, "NEXT CLAIM: GTA VII — PLEASE FILE IN 2039.", f, NAVY)
f, _ = fit(d, "FORM VI-2013 · REV. 19 NOV 2026 · KEEP THIS CLAIM FOREVER",
           "LiberationMono-Regular.ttf", 14, CW)
centered(d, fy + 27, "FORM VI-2013 · REV. 19 NOV 2026 · KEEP THIS CLAIM FOREVER",
         f, FAINT)

img.save(f"{DIR}/meme3.png")
img.resize((480, 480), Image.LANCZOS).save(f"{DIR}/meme3_480.png")
print("saved meme3.png + meme3_480.png")
print("stamp top y:", stamp_y, "stamp height:", layer.height,
      "-> stamp bottom:", stamp_y + layer.height, "footer y:", fy)
