#!/usr/bin/env python3
"""Generate UMe Parade Panic frames through Aigram transit, strictly serial."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://chat.aiwaves.tech/aigram/api/gen-image"
ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
FRAMES = PUBLIC / "frames"
MANIFEST = ROOT / "_production" / "generated-urls.json"

REFS = {
    "pink": "https://images.aiwaves.tech/uploads/1784396382160-k04sji1k7zd.jpg",
    "melon": "https://images.aiwaves.tech/uploads/1784396383830-tt0k1opksjm.jpg",
    "lemon": "https://images.aiwaves.tech/uploads/1784396385389-bqpu7v81dgf.jpg",
    "guac": "https://images.aiwaves.tech/uploads/1784396386784-7c4axgzm258.jpg",
    "mango": "https://images.aiwaves.tech/uploads/1784396388766-q3paajpmh7.jpg",
    "pearl": "https://images.aiwaves.tech/uploads/1784396390133-s2sj1jce6br.jpg",
}

WORLD = (
    "Polished 9:16 portrait frame for a joyful family-friendly premium 3D animated game. "
    "The same sunny UMe summer parade street: a whimsical bubble-tea parade float built from rounded painted wood and soft molded plastic, "
    "an empty closed parade street with completely blank cream building facades, little fabric pennants, blue sky, warm sunlight from upper left "
    "and soft sky-blue fill from front right. Every storefront is an unmarked solid surface: no signboards, no shop names, no glyph-like marks. "
    "Unified three-quarter camera, coherent perspective, contact shadows, tactile animated-film materials, subtle depth of field. "
    "Keep the supplied mascot's exact identity and silhouette, fully integrated into the world, never pasted on. "
    "Exactly one mascot, clear unobstructed face, safe slapstick, absolutely no people or human silhouettes anywhere, no other mascot, no logo, "
    "no letters, no pseudo-letters, no readable text, "
    "no label, no watermark, no collage. "
)

SCENES: dict[str, tuple[str | None, str, Path]] = {
    "hero": (
        "pink",
        WORLD
        + "Opening frame. The only character is the exact pink UMe rabbit: one long upright ear, one shorter rounded bent ear, blue bow, glossy "
        "black eyes with tiny lashes, rosy cheeks, short limbs. The rabbit stands naturally at the float control deck with an eager funny smile, "
        "full face unobstructed and both eyes visible. Place all five environmental clues apart from the face and apart from each other: a striped "
        "watermelon-red confetti cannon at lower left, an icy yellow bubble valve at mid left, a thick green banner crank at upper right, a mango-yellow "
        "beat pedal at lower right, and one dark pearl-shaped balloon clasp near the float canopy. A completely plain amber bubble-tea cup sits below "
        "waist level. No other character."
        ,
        PUBLIC / "hero.png",
    ),
    "end_melon": (
        "melon",
        WORLD
        + "MelonMick only, preserving red round ears, white muzzle, watermelon rind body band with black seeds and short limbs. MelonMick hangs from "
        "the striped confetti-cannon crank with a mischievous surprised grin while a harmless arc of watermelon-red, green and cream paper confetti "
        "bursts above the float. The cannon remains attached, the character settles safely with both feet near the deck."
        ,
        FRAMES / "end_melon.png",
    ),
    "end_lemon": (
        "lemon",
        WORLD
        + "LemonShark only. Preserve the bright whole-lemon shark body, pointed lemon tip, side fins, short feet, giant open red mouth with clean white "
        "triangular teeth, and both official eyes as bold black X marks, never pupils. LemonShark has turned the yellow bubble valve too far and slides "
        "sideways inside one enormous translucent soap bubble, fins spread, delighted, ending safely beside the float."
        ,
        FRAMES / "end_lemon.png",
    ),
    "end_guac": (
        "guac",
        WORLD
        + "GuacPiggy only, preserving deep green avocado-pig body, pale avocado face frame, brown pig nose, ears and dark green knit cap without readable "
        "letters. GuacPiggy calmly turns the green crank once, but one completely plain cream fabric ribbon wraps around the body like an oversized parade sash. "
        "There is no separate banner, no hanging flag, no green panel and no printed mark anywhere. Face fully visible, mildly confused, standing safely."
        ,
        FRAMES / "end_guac.png",
    ),
    "end_mango": (
        "mango",
        WORLD
        + "MangoChick only, preserving round yellow-orange body, green leaf crown, orange beak and feet. MangoChick stomps the mango-yellow beat pedal "
        "once; five tiny blank parade flags spring upward like a fan and the chick bounces backward into a proud pose. Flags have no writing."
        ,
        FRAMES / "end_mango.png",
    ),
    "end_pearl": (
        "pearl",
        WORLD
        + "BubblePearl only, preserving dark brown round body, cat ears, white oval eyes, yellow halo and two white wings. BubblePearl catches the dark "
        "balloon clasp, but a cluster of pearl-shaped pastel balloons gently lifts the mascot one body-height above the float. Wings open, halo straight, "
        "dreamy surprised expression, harmless and stable."
        ,
        FRAMES / "end_pearl.png",
    ),
    "end_climax": (
        "pink",
        WORLD
        + "Triumphant climax with the exact pink rabbit only. The rabbit keeps the full face clear and presses one giant plain cream drinking straw back "
        "into the float's round top socket using both paws. A chain of colorful pearl-shaped bulbs lights up along the float, paper confetti catches the "
        "sunlight, and the rabbit smiles proudly. Any cup remains plain and below chin level."
        ,
        FRAMES / "end_climax.png",
    ),
    "result_parade": (
        "pink",
        "Polished 9:16 portrait final frame in the same sunny premium 3D animated parade world. An extreme macro camera looks straight down inside one transparent "
        "bubble-tea cup, so the exterior wall and any label area are completely outside the frame. Glossy dark tapioca pearls tumble gently through swirling amber tea; "
        "sunlight and tiny pink, green and gold confetti reflections sparkle on the liquid surface. The upper edge of the plain clear cup forms a soft circular frame, "
        "with the sunny parade street reduced to abstract colorful bokeh beyond it. No character, no person, no hands, no face, no mascot, no second cup, no logo, "
        "no letters, no label, no badge, no symbol, no watermark."
        ,
        FRAMES / "result_parade.png",
    ),
    "poster_art": (
        None,
        "Square 1:1 premium raster key art for a joyful family-friendly animated game poster. A lovable pink rabbit with one long upright ear, one shorter "
        "rounded bent ear and a blue bow braces both paws against a giant cream drinking straw atop a whimsical bubble-tea parade float. The float rolls "
        "through a sunny cream storefront street as colorful paper confetti bursts behind it. Strong central silhouette, expressive unobstructed face, "
        "warm sunlight, UMe pink, green, gold and sky blue, tactile 3D animated-film materials, cinematic depth. Leave the top 25 percent as clean bright "
        "sky for a title and keep the bottom 20 percent free of faces and essential objects. One character only. No words, no logo, no letters, no watermark."
        ,
        PUBLIC / "poster-art.png",
    ),
    "poster_v2": (
        "pink",
        "Square 1:1 premium raster key art for a joyful family-friendly animated game poster. Preserve the supplied pink UMe rabbit exactly: "
        "one long upright ear, one shorter rounded bent ear, blue bow, glossy black eyes with tiny lashes, rosy cheeks and short limbs. "
        "Show the rabbit in a dynamic three-quarter pose on the lower-right half, leaning with both paws against a giant cream drinking straw as "
        "a whimsical bubble-tea parade float starts moving. Pearl-shaped bulbs sweep in a strong arc from lower left to the rabbit, and a controlled "
        "burst of red, green, gold and blue paper confetti creates motion behind the character. Sunny cream storefront street, bright blue sky, warm "
        "upper-left sunlight, tactile soft molded-plastic character and painted-wood float, cinematic animated-film depth. Reserve the upper-left "
        "quadrant as uncluttered pale sky with a soft cloud edge for release typography; do not place the rabbit's face, ears or essential props there. "
        "The rabbit's face is large, unobstructed and delighted, with both eyes visible. Exactly one mascot, no people, no extra character, no words, "
        "no logo, no letters, no pseudo-letters, no label, no watermark, no collage.",
        PUBLIC / "poster-art-v2.png",
    ),
}


def load_manifest() -> dict[str, str]:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return {}


def save_manifest(data: dict[str, str]) -> None:
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def request_image(prompt: str, ref_url: str | None) -> str:
    payload = {"prompt": prompt}
    if ref_url:
        payload["ref_url"] = ref_url
    body = json.dumps(payload).encode()
    for attempt, delay in enumerate((3, 8, 15), start=1):
        request = urllib.request.Request(
            API,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json", "Origin": "https://aigram.app", "User-Agent": "Mozilla/5.0"},
        )
        try:
            with urllib.request.urlopen(request, timeout=900) as response:
                result = json.loads(response.read())
            url = result.get("url")
            if not url:
                raise RuntimeError(result)
            return url
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise
            print(f"retry {attempt} HTTP {error.code}; wait {delay}s", flush=True)
            time.sleep(delay)
    raise RuntimeError("unreachable")


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=300) as response:
        destination.write_bytes(response.read())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slice", action="store_true", help="generate hero and first branch only")
    parser.add_argument("--only", nargs="+", choices=SCENES.keys(), help="generate selected named frames")
    args = parser.parse_args()
    names = args.only if args.only else ["hero", "end_melon"] if args.slice else list(SCENES)
    manifest = load_manifest()
    for index, name in enumerate(names):
        ref_key, prompt, destination = SCENES[name]
        if destination.exists() and destination.stat().st_size > 100_000 and name in manifest:
            print(f"{name}\tskip\t{manifest[name]}", flush=True)
            continue
        if index:
            time.sleep(3)
        url = request_image(prompt, REFS.get(ref_key) if ref_key else None)
        download(url, destination)
        manifest[name] = url
        save_manifest(manifest)
        print(f"{name}\t{url}", flush=True)


if __name__ == "__main__":
    main()
