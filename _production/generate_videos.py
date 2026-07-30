#!/usr/bin/env python3
"""Generate Parade Panic clips with the formal 2026-06-29 video API."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

SUBMIT = "https://u545921-b746-8a491f44.westc.seetacloud.com:8443/video"
POLL = "https://u545921-b746-8a491f44.westc.seetacloud.com:8443/video_task"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "videos"
IMAGE_MANIFEST = ROOT / "_production" / "generated-urls.json"
VIDEO_MANIFEST = ROOT / "_production" / "generated-video-urls.json"

TASKS = [
    ("clip_01_melon.mp4", "end_melon", "The pink rabbit notices the watermelon confetti cannon and points without touching it. The camera itself glides past the wooden cannon barrel; no hand, arm, paw or limb enters the foreground. The rabbit fully leaves frame before MelonMick is revealed already holding the crank. MelonMick pulls it once; a harmless red, green and cream confetti arc bursts upward, then MelonMick settles into the exact final pose. Preserve identities, no morphing, one action, stable face, empty unmarked street, absolutely no human, no disembodied hand, no text, no logo."),
    ("clip_02_lemon.mp4", "end_lemon", "The pink rabbit notices the icy yellow bubble valve. The camera playfully pans to the valve after the rabbit fully leaves frame, revealing LemonShark with exact black X eyes and white triangular teeth. LemonShark turns the valve once, one giant soap bubble forms, and LemonShark slides gently inside it into the exact final pose. Preserve identities, no morphing, no people, no text, no logo."),
    ("clip_03_guac.mp4", "end_guac", "The pink rabbit gestures toward the green banner crank. The camera follows the fabric line until the rabbit leaves frame, revealing GuacPiggy. GuacPiggy turns once; one soft pennant sash loops around the body, then GuacPiggy gives a slow confused look and settles into the exact final pose. Preserve identities, no morphing, no people, no text, no logo."),
    ("clip_04_mango.mp4", "end_mango", "The pink rabbit taps toward the mango-yellow beat pedal. The camera whip-pans to the pedal after the rabbit leaves frame, revealing MangoChick. MangoChick stomps once, five blank flags spring upward, and the chick bounces backward into the exact final pose. Preserve identities, one safe gag, no people, no text, no logo."),
    ("clip_05_pearl.mp4", "end_pearl", "The dark pearl-shaped balloon clasp floats past the pink rabbit. The camera follows it upward and the rabbit leaves frame, revealing BubblePearl. BubblePearl catches it; pearl-shaped balloons gently lift the mascot one body-height before settling into the exact final pose. Preserve cat ears, white eyes, yellow halo and white wings. No people, no text, no logo."),
    ("clip_06_climax.mp4", "end_climax", "Preserve the exact pink rabbit and sunny float. The rabbit looks up, grips one giant plain cream drinking straw with both paws and presses it into the round float socket. Colorful pearl bulbs light in a quick sequence, the float gives one tiny joyful bounce and confetti catches the sunlight, ending in the exact triumphant final pose. Face unobstructed, no other character, no people, no text, no logo."),
]


def post(url: str, body: dict) -> dict:
    request = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST", headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.loads(response.read())


def submit_task(filename: str, start_url: str, end_url: str, prompt: str) -> tuple[str, str]:
    result = post(SUBMIT, {"query": "", "params": {"image_url": start_url, "end_image_url": end_url, "prompt": prompt, "env": "prod", "target_image_ratio": "9x16"}})
    task_id = result.get("task_id") or result.get("data", {}).get("task_id")
    if not task_id:
        raise RuntimeError(result)
    print(f"{filename}\tsubmitted\t{task_id}", flush=True)
    return filename, task_id


def poll_and_download(filename: str, task_id: str) -> tuple[str, str, str]:
    destination = OUT / filename
    deadline = time.time() + 1800
    while time.time() < deadline:
        time.sleep(15)
        try:
            result = post(POLL, {"query": "", "params": {"task_id": task_id}})
        except urllib.error.HTTPError as error:
            if error.code == 429:
                print(f"{filename}\tpoll-429", flush=True)
                continue
            raise
        status = result.get("status") or result.get("data", {}).get("status")
        print(f"{filename}\t{status}", flush=True)
        if status == "success":
            url = result.get("url") or result.get("data", {}).get("url")
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=600) as response:
                data = response.read()
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            return filename, url, hashlib.sha256(data).hexdigest()
        if status == "failed":
            raise RuntimeError(result)
    raise TimeoutError(task_id)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slice", action="store_true")
    args = parser.parse_args()
    images = json.loads(IMAGE_MANIFEST.read_text())
    start_url = images["hero"]
    tasks = TASKS[:1] if args.slice else TASKS
    pending = [task for task in tasks if not (OUT / task[0]).exists()]
    recorded = json.loads(VIDEO_MANIFEST.read_text()) if VIDEO_MANIFEST.exists() else {}
    for offset in range(0, len(pending), 2):
        pair = pending[offset:offset + 2]
        submitted = []
        for index, (filename, end_key, prompt) in enumerate(pair):
            if index:
                time.sleep(20)
            submitted.append(submit_task(filename, start_url, images[end_key], prompt))
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            for filename, url, digest in executor.map(lambda item: poll_and_download(*item), submitted):
                recorded[filename] = {"url": url, "sha256": digest}
                VIDEO_MANIFEST.write_text(json.dumps(recorded, ensure_ascii=False, indent=2) + "\n")
                print(f"{filename}\t{url}\t{digest}", flush=True)
    hashes = [entry["sha256"] for entry in recorded.values()]
    if len(hashes) != len(set(hashes)):
        raise RuntimeError("duplicate video hashes detected")


if __name__ == "__main__":
    main()
