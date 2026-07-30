#!/usr/bin/env python3
"""Compose the release poster from Aigram key art with an authored parade title badge."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public" / "poster-art-v2.png"
LOGO = ROOT / "public" / "brand" / "ume-logo.png"
DEST = ROOT / "public" / "poster.png"
THUMB = ROOT / "_qa" / "ui" / "poster-160.png"
TITLE_FONT = "/Library/Fonts/SF-Pro-Rounded-Black.otf"

COCOA = (53, 35, 30, 255)
CREAM = (255, 247, 231, 255)
GREEN = (18, 107, 69, 255)
RED = (239, 74, 66, 255)
PINK = (245, 142, 183, 255)
GOLD = (255, 212, 85, 255)
BLUE = (101, 200, 239, 255)


def fit_font(text: str, maximum: int, width: int) -> ImageFont.FreeTypeFont:
    size = maximum
    while size > 20:
        font = ImageFont.truetype(TITLE_FONT, size)
        if font.getlength(text) <= width:
            return font
        size -= 2
    return ImageFont.truetype(TITLE_FONT, size)


source = Image.open(SOURCE).convert("RGB")
art = source.crop((0, 260, 768, 1028)).resize((1024, 1024), Image.Resampling.LANCZOS).convert("RGBA")

# A warm left-side veil connects the physical title badge to the sunlight.
veil = Image.new("RGBA", art.size, (0, 0, 0, 0))
veil_draw = ImageDraw.Draw(veil)
for x in range(650):
    alpha = int(90 * (1 - x / 650) ** 1.7)
    veil_draw.line((x, 0, x, 590), fill=(255, 247, 231, alpha), width=1)
veil = veil.filter(ImageFilter.GaussianBlur(18))
canvas = Image.alpha_composite(art, veil)

# Official logo sits on a small parade ticket instead of a generic eyebrow pill.
logo_layer = Image.new("RGBA", (330, 132), (0, 0, 0, 0))
ld = ImageDraw.Draw(logo_layer)
ld.rounded_rectangle((14, 18, 316, 116), radius=31, fill=GREEN)
ld.rounded_rectangle((2, 6, 304, 104), radius=31, fill=CREAM, outline=COCOA, width=5)
logo = Image.open(LOGO).convert("RGBA")
logo.thumbnail((236, 72), Image.Resampling.LANCZOS)
logo_layer.alpha_composite(logo, ((304 - logo.width) // 2, 19 + (72 - logo.height) // 2))
canvas.alpha_composite(logo_layer, (44, 34))

# The title is a chunky parade placard, slightly tilted and decorated like the float.
badge = Image.new("RGBA", (684, 364), (0, 0, 0, 0))
bd = ImageDraw.Draw(badge)
bd.rounded_rectangle((22, 24, 670, 350), radius=60, fill=PINK)
bd.rounded_rectangle((6, 8, 654, 334), radius=60, fill=CREAM, outline=COCOA, width=7)

parade_font = fit_font("PARADE", 70, 500)
panic_font = fit_font("PANIC!", 130, 590)
bd.text((330, 58), "PARADE", font=parade_font, anchor="ma", fill=GREEN)
bd.text((334, 128), "PANIC!", font=panic_font, anchor="ma", fill=RED, stroke_width=5, stroke_fill=COCOA)

# Pearl bulbs replace a generic subtitle rule and visually tie the title to the float.
for i, color in enumerate((BLUE, GOLD, RED, GREEN, PINK, BLUE, GOLD)):
    cx = 174 + i * 54
    bd.ellipse((cx - 15, 286, cx + 15, 316), fill=color, outline=COCOA, width=3)
bd.line((155, 301, 518, 301), fill=COCOA, width=4)

badge = badge.rotate(2.3, resample=Image.Resampling.BICUBIC, expand=True)
badge = badge.resize((int(badge.width * 0.88), int(badge.height * 0.88)), Image.Resampling.LANCZOS)
canvas.alpha_composite(badge, (26, 154))

finished = canvas.convert("RGB")
DEST.parent.mkdir(parents=True, exist_ok=True)
finished.save(DEST, "PNG", optimize=True)
THUMB.parent.mkdir(parents=True, exist_ok=True)
finished.resize((160, 160), Image.Resampling.LANCZOS).save(THUMB, "PNG", optimize=True)
print(DEST)
print(THUMB)
