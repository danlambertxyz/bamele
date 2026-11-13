#!/usr/bin/env python3
"""Rewrite the Tatoeba attribution list in credits.html from content/*/sources.json."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
items = {}
for f in sorted(ROOT.glob("content/*/sources.json")):
    for it in json.loads(f.read_text()):
        items[it["id"]] = it
rows = "\n".join(
    f'      <li lang="ms">{html.escape(it["ms"])} — <a href="https://tatoeba.org/en/sentences/show/{i}">#{i}</a>, {html.escape(it["by"]) if it["by"] != chr(92) + "N" else "unknown contributor"}</li>'
    for i, it in sorted(items.items()))
p = ROOT / "credits.html"
s = p.read_text()
a, b = s.index("<!--tatoeba-start-->"), s.index("<!--tatoeba-end-->")
s = s[:a] + "<!--tatoeba-start-->\n    <ul class=\"sources\">\n" + rows + "\n    </ul>\n    " + s[b:]
p.write_text(s)
print(len(items), "sentences listed")
