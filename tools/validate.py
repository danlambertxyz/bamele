#!/usr/bin/env python3
"""Check BaMeLe content: glossary coverage, exercise refs, audio files.

Usage: python tools/validate.py [--no-audio]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN = re.compile(r"[a-zA-Z][a-zA-Z'\-]*")


def tokens(text):
    return [t.lower().strip("-'") for t in TOKEN.findall(text)]


def slug(key):
    return re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")


def main():
    check_audio = "--no-audio" not in sys.argv
    glossary = json.loads((ROOT / "content/glossary.json").read_text())
    course = json.loads((ROOT / "content/course.json").read_text())
    problems, missing_words, missing_audio = [], {}, []

    def need_words(text, where):
        for t in tokens(text):
            if t not in glossary:
                missing_words.setdefault(t, where)

    def need_audio(path):
        if check_audio and not (ROOT / path).exists():
            missing_audio.append(path)

    for mod in course["modules"]:
        if not mod.get("ready"):
            continue
        mdir = ROOT / "content" / mod["dir"]
        module = json.loads((mdir / "module.json").read_text())
        for entry in module["lessons"]:
            lesson = json.loads((mdir / entry["file"]).read_text())
            lid = lesson["id"]
            adir = f"audio/{mod['id']}/{entry['id']}"
            for pid, p in lesson["phrases"].items():
                need_words(p["ms"], f"{lid} {pid}")
                for sp in ("normal", "slow"):
                    need_audio(f"{adir}/{pid}-{sp}.mp3")
            for a, b in lesson["match"]:
                if a not in glossary:
                    missing_words.setdefault(a, f"{lid} match")
            for level in ("easy", "medium", "hard"):
                lv = lesson["levels"][level]
                ids = {}
                for line in lv["dialogue"]:
                    ids[line["id"]] = line
                    if line["s"] not in ("staff", "you"):
                        problems.append(f"{lid} {line['id']}: bad speaker")
                    need_words(line["ms"], f"{lid} {line['id']}")
                    for sp in ("normal", "slow"):
                        need_audio(f"{adir}/{line['id']}-{sp}.mp3")
                for pid in lv["phrases"]:
                    if pid not in lesson["phrases"]:
                        problems.append(f"{lid} {level}: unknown phrase {pid}")
                g = lv["gist"]
                if not 0 <= g["answer"] < len(g["options"]):
                    problems.append(f"{lid} {level}: gist answer out of range")
                for i, ex in enumerate(lv["exercises"]):
                    tag = f"{lid} {level} ex{i} ({ex['type']})"
                    if "ref" in ex and ex["ref"] not in ids:
                        problems.append(f"{tag}: unknown ref {ex['ref']}")
                        continue
                    if ex["type"] == "gap" and ex["word"] not in tokens(ids[ex["ref"]]["ms"]):
                        problems.append(f"{tag}: word '{ex['word']}' not in line")
                    if ex["type"] in ("choose", "reply") and not 0 <= ex["answer"] < len(ex["options"]):
                        problems.append(f"{tag}: answer out of range")
                    if ex["type"] == "reply":
                        need_words(ex["prompt"], tag)
                        for o in ex["options"]:
                            need_words(o, tag)

    for key in glossary:
        need_audio(f"audio/words/{slug(key)}.mp3")

    for p in problems:
        print("PROBLEM", p)
    for w, where in sorted(missing_words.items()):
        print(f"NO GLOSS  {w:16} ({where})")
    if missing_audio:
        print(f"MISSING AUDIO: {len(missing_audio)} files, e.g. {missing_audio[:3]}")
    ok = not (problems or missing_words or missing_audio)
    print("OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
