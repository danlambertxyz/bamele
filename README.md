# BaMeLe

A small personal web app for learning everyday spoken Malaysian Malay, weighted towards listening. Plain HTML, CSS and JavaScript — no backend, no build step, no tracking.

**Use it online: https://danlambertxyz.github.io/bamele/**

## Run it locally

```bash
python3 -m http.server 8765
```

Then open http://localhost:8765. Progress is kept in the browser's localStorage only.

## Content

Lessons are JSON files under `content/`; audio is pre-generated MP3 under `audio/`.

```bash
python3 tools/validate.py              # check glossary coverage, references, audio
.venv/bin/python tools/gen_audio.py    # generate missing audio (needs: pip install edge-tts)
```

See [credits.html](credits.html) for sources and licences. Dialogues are written for this app; real-speech clips are YouTube embeds and are never rehosted.
