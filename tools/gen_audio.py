#!/usr/bin/env python3
"""Generate BaMeLe audio with Microsoft ms-MY neural voices via edge-tts.

Writes, skipping files that already exist:
  audio/<module>/<lesson>/<id>-normal.mp3 and <id>-slow.mp3  (lines, phrases)
  audio/words/<slug>.mp3                                      (glossary entries)

Usage: .venv/bin/python tools/gen_audio.py [--force]
Setup: python3 -m venv .venv && .venv/bin/pip install edge-tts
"""
import asyncio
import json
import re
import sys
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent.parent
VOICES = {"m": "ms-MY-OsmanNeural", "f": "ms-MY-YasminNeural"}
RATES = {"normal": "+0%", "slow": "-25%"}
FORCE = "--force" in sys.argv

# Hook for respelling words a voice reads badly (speech only). Empty until a
# problem is actually heard: e.g. {"takpe": "tak pe"}.
SAY = {}


def spoken(text):
    return re.sub(r"[A-Za-z']+", lambda m: SAY.get(m.group(0).lower(), m.group(0)), text)


def slug(key):
    return re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")


def jobs():
    course = json.loads((ROOT / "content/course.json").read_text())
    for mod in course["modules"]:
        if not mod.get("ready"):
            continue
        mdir = ROOT / "content" / mod["dir"]
        module = json.loads((mdir / "module.json").read_text())
        for entry in module["lessons"]:
            lesson = json.loads((mdir / entry["file"]).read_text())
            out = ROOT / "audio" / mod["id"] / entry["id"]
            voice = {"staff": lesson["staff"]["voice"], "you": lesson["you"]["voice"]}
            for pid, p in lesson["phrases"].items():
                v = p.get("v", voice["you"])
                for sp, rate in RATES.items():
                    yield out / f"{pid}-{sp}.mp3", p["ms"], VOICES[v], rate
            for lv in lesson["levels"].values():
                for line in lv["dialogue"]:
                    for sp, rate in RATES.items():
                        yield out / f"{line['id']}-{sp}.mp3", line["ms"], VOICES[voice[line["s"]]], rate
                for kind in ("listen", "read"):
                    for ex in lv["drills"][kind]:
                        if "ms" in ex:
                            for sp, rate in RATES.items():
                                yield out / f"{ex['id']}-{sp}.mp3", ex["ms"], VOICES[voice[ex["s"]]], rate
    glossary = json.loads((ROOT / "content/glossary.json").read_text())
    for key in glossary:
        yield ROOT / "audio/words" / f"{slug(key)}.mp3", key, VOICES["f"], "-10%"


async def make(sem, path, text, voice, rate):
    if path.exists() and path.stat().st_size > 0 and not FORCE:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    async with sem:
        for attempt in range(4):
            try:
                await edge_tts.Communicate(spoken(text), voice, rate=rate).save(str(path))
                return 1
            except Exception as e:  # network hiccups: retry
                if attempt == 3:
                    print("FAILED", path, e)
                    path.unlink(missing_ok=True)
                    return 0
                await asyncio.sleep(1.5 * (attempt + 1))


async def main():
    sem = asyncio.Semaphore(6)
    done = await asyncio.gather(*(make(sem, *j) for j in jobs()))
    print(f"generated {sum(done)} files, {len(done) - sum(done)} skipped/failed")


if __name__ == "__main__":
    asyncio.run(main())
