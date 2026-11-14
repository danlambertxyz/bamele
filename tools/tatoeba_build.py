"""Shared helpers for modules assembled from Tatoeba sentences.

A line is built from parts: a Tatoeba id (int) pulls the Malay text verbatim
from the corpus export; a string is text written for the app. Fully verbatim
items get `real: true`; every id used is recorded for the credits page.

The TSVs are Tatoeba's per-language "sentences_detailed" exports (CC BY 2.0 FR):
https://downloads.tatoeba.org/exports/per_language/{zlm,zsm}/{lang}_sentences_detailed.tsv.bz2
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if len(sys.argv) < 2:
    sys.exit("usage: python tools/build_mNN.py <dir with zlm.tsv and zsm.tsv>")
SRC = Path(sys.argv[1])
T = {}
for name in ("zlm.tsv", "zsm.tsv"):
    for row in (SRC / name).read_text(encoding="utf-8").splitlines():
        p = row.split("\t")
        if len(p) >= 4:
            T[int(p[0])] = (p[2].strip(), p[3])
USED = {}
S, Y = "staff", "you"


def text(parts):
    parts = parts if isinstance(parts, (list, tuple)) else [parts]
    out, ids = [], []
    for part in parts:
        if isinstance(part, int):
            t = T[part][0]
            if t[-1] not in ".!?…":
                t += "."
            USED[part] = T[part]
            ids.append(part)
            out.append(t)
        else:
            out.append(part)
    ms = " ".join(out)
    extra = {}
    if ids:
        extra["src"] = [f"t{i}" for i in ids]
        if all(isinstance(p, int) for p in parts):
            extra["real"] = True
    return ms, extra


def ln(s, parts, en):
    ms, extra = text(parts)
    return {"s": s, "ms": ms, "en": en, **extra}


def c(s, parts, en, *wrong): return {"type": "choose", **ln(s, parts, en), "wrong": list(wrong)}
def g(s, parts, en, word): return {"type": "gap", **ln(s, parts, en), "word": word}
def d(s, parts, en): return {"type": "dictation", **ln(s, parts, en)}
def l(s, parts, en): return {"type": "ladder", **ln(s, parts, en)}
def o(s, parts, en): return {"type": "order", **ln(s, parts, en)}


def r(prompt, right, wrong, why):
    return {"type": "reply", "prompt": text(prompt)[0], "right": text(right)[0], "wrong": [text(w)[0] for w in wrong], "why": why}


M = {"type": "match"}


def ph(parts, en, note=None, v=None):
    ms, extra = text(parts)
    out = {"ms": ms, "en": en, **extra}
    if note:
        out["note"] = note
    if v:
        out["v"] = v
    return out


def gist(q, right, *wrong, why=""):
    return {"q": q, "options": [right, *wrong], "answer": 0, "why": why}


PRE = {"easy": "e", "medium": "m", "hard": "h"}


def write_module(mid, dirname, title, lessons, vocab, tr):
    """vocab: {lesson id: {level: [keys]}}; tr: {lesson id: {malay: english}} for reply options."""
    mdir = ROOT / "content" / dirname
    mdir.mkdir(exist_ok=True)
    entries = []
    for L in lessons:
        lesson = {"id": f"{mid}-{L['id']}", "title": L["title"], "blurb": L["blurb"], "staff": L["staff"], "you": L["you"],
                  "notes": L["notes"], "phrases": L.get("phrases", {}), "match": L["match"], "tr": tr.get(L["id"], {}), "clips": [], "levels": {}}
        for level, lv in L["levels"].items():
            dialogue = [{"id": f"{PRE[level]}{i + 1}", **line} for i, line in enumerate(lv["dialogue"])]
            n, drills = 0, {}
            for kind in ("listen", "read"):
                drills[kind] = []
                for ex in lv[kind]:
                    ex = dict(ex)
                    if "ms" in ex:
                        n += 1
                        ex = {"type": ex["type"], "id": f"{PRE[level]}v{n}", **{k: v for k, v in ex.items() if k != "type"}}
                    drills[kind].append(ex)
            lesson["levels"][level] = {"dialogue": dialogue, "gist": lv["gist"], "vocab": vocab[L["id"]][level],
                                       "phrases": lv.get("phrases", []), "drills": drills}
        (mdir / f"{L['id']}.json").write_text(json.dumps(lesson, ensure_ascii=False, indent=1) + "\n")
        entries.append({"id": L["id"], "file": f"{L['id']}.json", "title": L["title"], "blurb": L["blurb"]})
    num = int(mid[1:])
    module = {"id": mid, "title": title, "lessons": entries,
              "finale": {"title": f"Module {num} test", "blurb": "Twelve questions drawn from all five lessons.", "testSize": 12}, "clips": []}
    (mdir / "module.json").write_text(json.dumps(module, ensure_ascii=False, indent=1) + "\n")
    # attribution list for the credits page (CC BY 2.0 FR needs author + source)
    credits = [{"id": i, "by": u, "ms": t} for i, (t, u) in sorted(USED.items())]
    (mdir / "sources.json").write_text(json.dumps(credits, ensure_ascii=False, indent=1) + "\n")
    print(f"{mid}: wrote {len(lessons)} lessons; {len(USED)} Tatoeba sentences used")
