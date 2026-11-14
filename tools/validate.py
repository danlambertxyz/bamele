#!/usr/bin/env python3
"""Check BaMeLe content: glossary coverage, drill structure, audio files.

Usage: python tools/validate.py [--no-audio]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN = re.compile(r"[a-zA-Z][a-zA-Z'\-]*")
LISTEN = {"choose", "gap", "dictation", "ladder"}
READ = {"reply", "order", "match"}


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
            for a, _ in lesson["match"]:
                if a not in glossary:
                    missing_words.setdefault(a, f"{lid} match")
            # English known for a Malay sentence anywhere in this lesson (reply options are looked up here)
            english = dict(lesson.get("tr", {}))
            for p in lesson["phrases"].values():
                english[p["ms"]] = p["en"]
            for lv in lesson["levels"].values():
                for x in lv["dialogue"] + lv["drills"]["listen"] + lv["drills"]["read"]:
                    if "ms" in x:
                        english[x["ms"]] = x["en"]
            for level in ("easy", "medium", "hard"):
                lv = lesson["levels"][level]
                seen_ids, seen_ms = set(), set()
                for line in lv["dialogue"]:
                    seen_ids.add(line["id"])
                    seen_ms.add(line["ms"].lower())
                    if line["s"] not in ("staff", "you"):
                        problems.append(f"{lid} {line['id']}: bad speaker")
                    need_words(line["ms"], f"{lid} {line['id']}")
                    for sp in ("normal", "slow"):
                        need_audio(f"{adir}/{line['id']}-{sp}.mp3")
                for pid in lv["phrases"]:
                    if pid not in lesson["phrases"]:
                        problems.append(f"{lid} {level}: unknown phrase {pid}")
                vocab = [w[0] if isinstance(w, list) else w for w in lv.get("vocab", [])]
                if len(vocab) < 5:
                    problems.append(f"{lid} {level}: needs at least 5 vocab words")
                for w in vocab:
                    if w not in glossary:
                        problems.append(f"{lid} {level}: vocab word '{w}' is not a glossary key")
                if len(set(vocab)) != len(vocab):
                    problems.append(f"{lid} {level}: repeated vocab word")
                g = lv["gist"]
                if not 0 <= g["answer"] < len(g["options"]):
                    problems.append(f"{lid} {level}: gist answer out of range")
                for kind, allowed in (("listen", LISTEN), ("read", READ)):
                    for i, ex in enumerate(lv["drills"][kind]):
                        tag = f"{lid} {level} {kind}{i} ({ex['type']})"
                        if ex["type"] not in allowed:
                            problems.append(f"{tag}: type not allowed in {kind} drills")
                        if "ms" in ex:
                            # drills must vary the dialogue, never repeat a sentence
                            if ex["ms"].lower() in seen_ms:
                                problems.append(f"{tag}: sentence repeats one already used")
                            seen_ms.add(ex["ms"].lower())
                            if ex.get("id") in seen_ids or "id" not in ex:
                                problems.append(f"{tag}: missing or duplicate id")
                            seen_ids.add(ex.get("id"))
                            if ex.get("s") not in ("staff", "you"):
                                problems.append(f"{tag}: bad speaker")
                            need_words(ex["ms"], tag)
                            for sp in ("normal", "slow"):
                                need_audio(f"{adir}/{ex['id']}-{sp}.mp3")
                        if ex["type"] == "gap" and tokens(ex["ms"]).count(ex["word"]) != 1:
                            problems.append(f"{tag}: word '{ex['word']}' must appear exactly once")
                        if ex["type"] == "choose" and len(ex["wrong"]) < 2:
                            problems.append(f"{tag}: needs at least two wrong options")
                        if ex["type"] == "reply":
                            if ex["prompt"].lower() in seen_ms:
                                problems.append(f"{tag}: prompt repeats a sentence already used")
                            seen_ms.add(ex["prompt"].lower())
                            for text in [ex["prompt"], ex["right"], *ex["wrong"]]:
                                need_words(text, tag)
                                if text not in english:
                                    problems.append(f"{tag}: no English for reply text '{text}' (add it to the lesson's tr)")

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
