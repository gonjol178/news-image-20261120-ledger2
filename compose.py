#!/usr/bin/env python3
"""The World Ledger — broadsheet compositor.

Builds the entry image (1024x1024) for make.fun news-image-20261120:
a one-page newspaper front page dated Friday, 20 November 2026, with
three generated photo panels and six verified stories of the day.

Run:  python3 compose.py            (writes assets/entry.png)
Requires Pillow locally; the graded entrypoint (main.py) only copies
the finished PNG, so it needs no third-party library.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

W, H = 1024, 1024
PAPER = (246, 241, 227)   # warm newsprint
INK = (28, 26, 23)
ACCENT = (143, 29, 29)    # deep broadsheet red
GRAY = (111, 106, 94)
RULE = (60, 55, 48)

FONT_DIR = "/usr/share/fonts/truetype"
FONTS = {
    "masthead": ("noto/NotoSerifDisplay-Black.ttf", 74),
    "headline": ("noto/NotoSerif-Bold.ttf", 40),
    "headline_sm": ("noto/NotoSerif-Bold.ttf", 27),
    "headline_xs": ("noto/NotoSerif-Bold.ttf", 23),
    "deck": ("noto/NotoSerif-Italic.ttf", 16),
    "body": ("noto/NotoSerif-Regular.ttf", 14),
    "body_sm": ("noto/NotoSerif-Regular.ttf", 13),
    "caption": ("noto/NotoSerif-Italic.ttf", 11),
    "kicker": ("noto/NotoSans-Bold.ttf", 13),
    "kicker_sm": ("noto/NotoSans-Bold.ttf", 12),
    "dateline": ("noto/NotoSerif-Bold.ttf", 17),
    "dateline_sm": ("noto/NotoSans-Bold.ttf", 11),
    "brief": ("noto/NotoSerif-Regular.ttf", 13),
    "brief_bold": ("noto/NotoSerif-Bold.ttf", 13),
    "footer": ("noto/NotoSerif-Regular.ttf", 10),
    "brief_title": ("noto/NotoSans-Bold.ttf", 14),
}


def font(name):
    path, size = FONTS[name]
    return ImageFont.truetype(os.path.join(FONT_DIR, path), size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap measured with the real font; returns line list."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill=INK, leading=None):
    """Draw wrapped lines; returns the y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.28)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def kicker(draw, x, y, text, size="kicker"):
    fnt = font(size)
    draw.text((x, y), text, font=fnt, fill=ACCENT)
    return y + fnt.size + 8


def hline(draw, x0, x1, y, width=1, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def vline(draw, x, y0, y1, width=1, fill=RULE):
    draw.line([(x, y0), (x, y1)], fill=fill, width=width)


def photo(draw, path, x, y, w, h):
    """Center-crop a panel to the target box and paste it with a border."""
    im = Image.open(path).convert("RGB")
    tw, th = im.size
    target = w / h
    if tw / th > target:  # too wide: crop sides
        nw = int(th * target)
        off = (tw - nw) // 2
        im = im.crop((off, 0, off + nw, th))
    else:  # too tall: crop top/bottom (keep the upper part)
        nh = int(tw / target)
        off = max(0, (th - nh) // 6)
        im = im.crop((0, off, tw, off + nh))
    im = im.resize((w, h), Image.LANCZOS)
    page.paste(im, (x, y))
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=1)


page = Image.new("RGB", (W, H), PAPER)
draw = ImageDraw.Draw(page)

# ---- frame ---------------------------------------------------------------
draw.rectangle([10, 10, W - 11, H - 11], outline=INK, width=2)
draw.rectangle([16, 16, W - 17, H - 17], outline=RULE, width=1)

# ---- masthead ------------------------------------------------------------
f_top = font("dateline_sm")
top_line = "ONE DAY  ·  ONE PAGE  ·  THE WHOLE WORLD"
draw.text(((W - draw.textlength(top_line, font=f_top)) / 2, 30),
          top_line, font=f_top, fill=GRAY)

f_mast = font("masthead")
mast = "THE WORLD LEDGER"
draw.text(((W - draw.textlength(mast, font=f_mast)) / 2, 46),
          mast, font=f_mast, fill=INK)

f_date = font("dateline")
date = "FRIDAY,  20 NOVEMBER 2026"
draw.text((30, 128), date, font=f_date, fill=INK)
f_dright = font("dateline_sm")
right = "FIVE STORIES  ·  FOUR IN BRIEF"
draw.text((W - 30 - draw.textlength(right, font=f_dright), 133),
          right, font=f_dright, fill=GRAY)

hline(draw, 30, W - 30, 154, width=3, fill=INK)
hline(draw, 30, W - 30, 159, width=1)

# ---- row 1: lead (left) + Kyiv (right) ------------------------------------
LX, LW = 30, 634          # lead column
RX, RW = 684, 310         # Kyiv column
ROW1_Y = 174

y = kicker(draw, LX, ROW1_Y, "WASHINGTON — THE LEAD")
y = text_block(draw, LX, y,
               wrap(draw, "Trump puts the Iran decision off until the new year",
                    font("headline"), LW),
               font("headline"), leading=48)
y = text_block(draw, LX, y + 6,
               wrap(draw, "The Senate blocks the war measure, 51–48, in a "
                           "late-night vote — and the White House waits.",
                    font("deck"), LW),
               font("deck"), leading=21)
photo(draw, os.path.join(ASSETS, "panel-senate.webp"), LX, 348, LW, 192)
draw.text((LX, 546), "The U.S. Senate chamber in Washington.",
          font=font("caption"), fill=GRAY)

vline(draw, 674, ROW1_Y, 560)

y = kicker(draw, RX, ROW1_Y, "KYIV")
y = text_block(draw, RX, y,
               wrap(draw, "Strikes on the capital's bridges kill eight",
                    font("headline_sm"), RW),
               font("headline_sm"), leading=33)
y = text_block(draw, RX, y + 4,
               wrap(draw, "Russian attacks hit Kyiv at dawn; 28 people are "
                           "injured across nine regions.",
                    font("body"), RW),
               font("body"), leading=19)
photo(draw, os.path.join(ASSETS, "panel-kyiv.webp"), RX, 366, RW, 168)
draw.text((RX, 540), "Dawn over the Dnipro in Kyiv.",
          font=font("caption"), fill=GRAY)

# ---- divider --------------------------------------------------------------
hline(draw, 30, W - 30, 574, width=2, fill=INK)
hline(draw, 30, W - 30, 578, width=1)

# ---- row 2: Shenzhen + Pacific -------------------------------------------
ROW2_Y = 592
CX = 512  # centre rule

y = kicker(draw, 30, ROW2_Y, "SHENZHEN")
y = text_block(draw, 30, y,
               wrap(draw, "\u201cA nuclear war cannot be won and must never "
                           "be fought\u201d",
                    font("headline_xs"), 470),
               font("headline_xs"), leading=28)
text_block(draw, 30, y + 4,
           wrap(draw, "Trump, Putin and Xi issue the joint statement — but "
                       "there is no breakthrough on Ukraine.",
                font("body_sm"), 470),
           font("body_sm"), leading=18)

vline(draw, CX, ROW2_Y, 736)

y = kicker(draw, 524, ROW2_Y, "THE PACIFIC")
y = text_block(draw, 524, y,
               wrap(draw, "U.S. leases 31.5M acres of seabed for $6M",
                    font("headline_xs"), 470),
               font("headline_xs"), leading=28)
text_block(draw, 524, y + 4,
           wrap(draw, "Wetstone U.S. Ventures wins the first deep-sea "
                       "mining sale of its kind.",
                font("body_sm"), 470),
           font("body_sm"), leading=18)

# ---- divider --------------------------------------------------------------
hline(draw, 30, W - 30, 750, width=2, fill=INK)
hline(draw, 30, W - 30, 754, width=1)

# ---- row 3: Nairobi + In Brief -------------------------------------------
ROW3_Y = 768
photo(draw, os.path.join(ASSETS, "panel-nairobi.webp"), 30, ROW3_Y, 296, 164)
draw.text((30, 936), "Outside a hospital in Nairobi.",
          font=font("caption"), fill=GRAY)

NX = 342
y = kicker(draw, NX, ROW3_Y, "NAIROBI")
y = text_block(draw, NX, y,
               wrap(draw, "Kenya discharges its last Ebola patient",
                    font("headline_xs"), 278),
               font("headline_xs"), leading=28)
text_block(draw, NX, y + 4,
           wrap(draw, "Thirty-seven days after the first case, the "
                       "outbreak's final patient walks out of hospital.",
                font("body_sm"), 278),
           font("body_sm"), leading=18)

# In Brief box
BX, BW = 644, 350
draw.rectangle([BX, ROW3_Y, BX + BW - 1, 950], outline=INK, width=2)
f_bt = font("brief_title")
title = "IN BRIEF"
draw.text((BX + (BW - draw.textlength(title, font=f_bt)) / 2, ROW3_Y + 10),
          title, font=f_bt, fill=INK)
hline(draw, BX + 14, BX + BW - 14, ROW3_Y + 36, width=1)

briefs = [
    ("WARSAW", "Russian missiles and a drone enter Polish airspace."),
    ("ROME", "Italy fines Meta \u20ac805M."),
    ("NEW YORK", "GTA VI tops $2.3B at launch."),
    ("TALLINN", "Estonia closes its Russian border."),
]
by = ROW3_Y + 48
for city, item in briefs:
    f_b, f_bb = font("brief"), font("brief_bold")
    lead = city + " — "
    lines = wrap(draw, lead + item, f_b, BW - 28)
    # bold the city lead on the first line
    draw.text((BX + 14, by), lead, font=f_bb, fill=INK)
    rest = lines[0][len(lead):]
    draw.text((BX + 14 + draw.textlength(lead, font=f_bb), by), rest,
              font=f_b, fill=INK)
    by += int(f_b.size * 1.28)
    for extra in lines[1:]:
        draw.text((BX + 14, by), extra, font=f_b, fill=INK)
        by += int(f_b.size * 1.28)
    by += 7

# ---- footer ---------------------------------------------------------------
hline(draw, 30, W - 30, 966, width=1)
f_foot = font("footer")
sources = ("Sources: Just Security Early Edition, 20 Nov 2026  ·  "
           "One Turn News day report, 20 Nov 2026  ·  Bangladesh Chronicle "
           "morning briefing, Fri 20 Nov 2026  ·  Morning Briefing #222")
while draw.textlength(sources, font=f_foot) > W - 60 and f_foot.size > 8:
    f_foot = ImageFont.truetype(
        os.path.join(FONT_DIR, "noto/NotoSerif-Regular.ttf"), f_foot.size - 1)
draw.text(((W - draw.textlength(sources, font=f_foot)) / 2, 974),
          sources, font=f_foot, fill=GRAY)

out = os.path.join(ASSETS, "entry.png")
page.save(out, "PNG", optimize=True)
size = os.path.getsize(out)
print(f"wrote {out}  {W}x{H}  {size} bytes")
if size > 1048576:
    # Photos make PNG too big: fall back to JPEG bytes in the same name,
    # which the competition rules explicitly allow.
    page.save(out, "JPEG", quality=88, optimize=True)
    size = os.path.getsize(out)
    print(f"PNG over 1 MiB; rewrote as JPEG bytes: {size} bytes")
assert size <= 1048576, "entry.png still over 1 MiB"
