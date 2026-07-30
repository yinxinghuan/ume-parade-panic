#!/usr/bin/env python3
"""Crop Aigram climax key art and add exact release typography."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public" / "frames" / "end_climax.png"
DEST = ROOT / "public" / "poster.png"
THUMB = ROOT / "_qa" / "ui" / "poster-160.png"
FONT = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"

source = Image.open(SOURCE).convert("RGB")
image = source.crop((0, 70, 768, 838)).resize((1024, 1024), Image.Resampling.LANCZOS)

shade = Image.new("RGBA", image.size, (0, 0, 0, 0))
shade_draw = ImageDraw.Draw(shade)
for y in range(290):
    alpha = int(218 * (1 - y / 290) ** 1.35)
    shade_draw.line((0, y, 1024, y), fill=(255, 247, 231, alpha), width=1)
shade = shade.filter(ImageFilter.GaussianBlur(8))
canvas = Image.alpha_composite(image.convert("RGBA"), shade)

layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
draw = ImageDraw.Draw(layer)
eyebrow = ImageFont.truetype(FONT, 28)
line_one = ImageFont.truetype(FONT, 72)
line_two = ImageFont.truetype(FONT, 110)
draw.rounded_rectangle((388, 18, 636, 61), radius=21, fill=(18, 107, 69, 244), outline=(53, 35, 30, 255), width=3)
draw.text((512, 39), "UMe FAMILY", font=eyebrow, anchor="mm", fill=(255, 247, 231, 255))
draw.text((512, 77), "PARADE", font=line_one, anchor="ma", fill=(53, 35, 30, 255), stroke_width=2, stroke_fill=(255, 247, 231, 230))
draw.text((512, 133), "PANIC", font=line_two, anchor="ma", fill=(239, 74, 66, 255), stroke_width=3, stroke_fill=(53, 35, 30, 230))

finished = Image.alpha_composite(canvas, layer).convert("RGB")
DEST.parent.mkdir(parents=True, exist_ok=True)
finished.save(DEST, "PNG", optimize=True)
THUMB.parent.mkdir(parents=True, exist_ok=True)
finished.resize((160, 160), Image.Resampling.LANCZOS).save(THUMB, "PNG", optimize=True)
print(DEST)
print(THUMB)
