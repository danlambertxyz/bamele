#!/usr/bin/env python3
"""Build Module 5 (Small talk) from Tatoeba sentences.

Lines and drills are assembled from sentence ids so the Malay text is copied
verbatim from the corpus export, never retyped. A part is either a Tatoeba id
(int) or a string written for the app. `real` = the whole line is verbatim.

Usage: python tools/build_m05.py <dir with zlm.tsv and zsm.tsv>
The TSVs are Tatoeba's per-language "sentences_detailed" exports (CC BY 2.0 FR).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
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


LESSONS = []

# ---------------------------------------------------------------- lesson 1
LESSONS.append(dict(
    id="l01", title="Lama tak jumpa", blurb="Catching up with a friend you haven't seen in ages.",
    staff={"label": "Adi", "name": "Adi, a friend", "voice": "m"}, you={"voice": "f"},
    notes=[
        {"title": "aku and kau", "body": "With friends it's <b>aku</b> (I) and <b>kau</b> (you). With people you don't know well, or at work, it's <b>saya</b> and <b>awak</b>. You'll hear both in this module."},
        {"title": "Dah makan?", "body": "“Have you eaten?” is as much a greeting as a question. <i>Dah</i> (already) or <i>belum</i> (not yet) are the two answers."},
        {"title": "Spoken spellings", "body": "People write the way they talk: <b>pegi</b> for pergi, <b>ambik</b> for ambil, <b>gak</b> for juga, <b>takde</b> for tiada."},
    ],
    phrases={
        "p1": ph(10656051, "It's been a long time since we met.", v="m"),
        "p2": ph(4563543, "Have you eaten?", "The everyday greeting between friends.", "m"),
        "p3": ph(9724812, "I'm always busy with work.", "asyik = keep on, always."),
        "p4": ph(10656062, "You work too hard.", "kuat = strong, hard."),
        "p5": ph(11368213, "When are we going for a drink together?", "sekali here = together."),
        "p6": ph(10772373, "Let's eat out tonight!", "jom = let's."),
        "p7": ph(11535538, "Sure, why not.", "A relaxed, slightly lukewarm yes."),
        "p8": ph(3351855, "How are you?", v="m"),
        "p9": ph(4560192, "We haven't met in a long time."),
        "p10": ph(11518810, "I miss hanging out with friends.", "lepak = hang out; member = friends."),
        "p11": ph(11368237, "You can't just work, right — once in a while you have to take a holiday.", "takkan = surely not; gak = juga.", "m"),
        "p12": ph(3936339, "See you again!"),
    },
    match=[["pegi", "pergi"], ["tak", "tidak"], ["nak", "hendak"], ["dah", "sudah"], ["ambik", "ambil"], ["gak", "juga"], ["takkan", "tidak akan"]],
    levels={
        "easy": dict(
            dialogue=[
                ln(S, 3351855, "How are you?"),
                ln(Y, ["Khabar baik.", 4560192], "I'm fine. We haven't met in a long time."),
                ln(S, 5900157, "Are you busy now?"),
                ln(Y, 3936366, "Busy right now."),
                ln(S, 4563543, "Have you eaten?"),
                ln(Y, "Belum. Jom makan!", "Not yet. Let's eat!"),
            ],
            gist=gist("What do they decide to do?", "Go and eat", "Go back to work", "Meet again next week", why="Dah makan? … Belum. Jom makan!"),
            phrases=["p8", "p9", "p2", "p12"],
            listen=[
                c(S, 10305802, "How are you two?", "Where are you two going?", "Have you two eaten?"),
                g(Y, 8346971, "I want to go home.", "balik"),
                c(S, 10304170, "What did you do yesterday?", "What are you doing tomorrow?", "Where were you yesterday?"),
                d(Y, 4573764, "I'm busy."),
                l(S, 4563544, "Have you had dinner?"),
            ],
            read=[
                r(3936306, "Tak buat apa-apa.", ["Khabar baik.", "Jumpa lagi!"], "He asks what you're doing; tak buat apa-apa = nothing much."),
                o(Y, 4551709, "I want to see you."),
                r(3936267, "Jom makan!", ["Khabar baik.", "Sekarang sibuk."], "Laparnya = so hungry. The friendly answer is to go and eat."),
                o(S, 10500846, "When did you get back?"),
                M,
            ]),
        "medium": dict(
            dialogue=[
                ln(S, 10656051, "It's been a long time since we met."),
                ln(Y, "Tu la. Kau buat apa sekarang?", "I know, right. What are you up to now?"),
                ln(S, 9724812, "I'm always busy with work."),
                ln(Y, 10656062, "You work too hard."),
                ln(S, ["Kau pulak?", 4563543], "And you? Have you eaten?"),
                ln(Y, ["Belum.", 11368213], "Not yet. When are we going for a drink together?"),
                ln(S, 10772373, "Let's eat out tonight!"),
                ln(Y, 11535538, "Sure, why not."),
            ],
            gist=gist("What is his life like at the moment?", "He's always busy with work", "He just lost his job", "He's on holiday", "He's about to move away", why="Aku ni asyik sibuk dengan kerja."),
            phrases=["p1", "p3", "p4", "p2", "p5", "p6", "p7"],
            listen=[
                c(S, 10729086, "What did you do last week?", "What are you doing next week?", "Where did you go last week?"),
                g(Y, 11518731, "It feels like I don't want to go back.", "macam"),
                c(S, 9688105, "Do you want to see me?", "Did you see me?", "Do you want me to go?"),
                d(Y, 10681083, "He went home yesterday."),
                l(S, 4563592, "When are we eating? I'm hungry!"),
            ],
            read=[
                r(9871547, ["Banyak kerja.", 11380330], ["Boleh la.", "Jom makan luar malam ni!"], "He asks why you didn't go home: too much work."),
                o(Y, 9708941, "We're heading home."),
                r("Bila nak jumpa?", 10727704, ["Kau ni kerja kuat sangat.", "Dah makan?"], "A when-question wants a time: esok mungkin…"),
                o(S, 9724813, "He feels kind of unwell."),
                M,
            ]),
        "hard": dict(
            dialogue=[
                ln(S, 11518699, "Oh, I thought you weren't coming back?"),
                ln(Y, [11376487, 11518810], "It's been ages since I came back to the kampung. I miss hanging out with friends."),
                ln(S, [10656051, "Kau apa cerita?"], "It's been a long time since we met. What's new with you?"),
                ln(Y, [9724812, 11380330], "I'm always busy with work. All I think about is going home."),
                ln(S, 11368237, "You can't just work, right — once in a while you have to take a holiday."),
                ln(Y, ["Tu la.", 11518733], "I know. Why on earth didn't I take leave that time."),
                ln(S, [10656062, 11368213], "You work too hard. When are we going for a drink together?"),
                ln(Y, 10772373, "Let's eat out tonight!"),
                ln(S, ["Malam ni tak boleh.", 10727704], "Tonight I can't. Maybe I'll see you tomorrow."),
                ln(Y, ["Okay.", 3936339], "Okay. See you!"),
            ],
            gist=gist("When will they probably meet up?", "Tomorrow", "Tonight", "Next Thursday", "Not at all", why="Malam ni tak boleh. Esok mungkin aku jumpa kau."),
            phrases=["p10", "p11", "p1", "p5", "p12", "p3"],
            listen=[
                c(S, 11540092, "An hour later, he called back.", "He called an hour ago and left.", "He'll call back in an hour.", "He called back every hour."),
                g(Y, 11518831, "Keeps going on about the same thing.", "pasal"),
                c(S, 11395984, "When I think back, it's really funny.", "When I get back, it'll be fun.", "I remember he was really funny.", "I can't remember what was funny."),
                d(Y, 10729086, "What did you do last week?"),
                l(S, 11518716, "It used to be hard to meet up even once a year."),
            ],
            read=[
                r("Kau apa cerita sekarang?", ["Asyik kerja.", 11380330], [11540092, "Jumpa lagi!"], "Kau apa cerita = what's new with you."),
                o(Y, 11518731, "It feels like I don't want to go back."),
                r("Cuti ni kau balik kampung tak?", ["Balik.", 11376487], ["Kau ni kerja kuat sangat.", "Malam ni tak boleh."], "A yes/no question with tak: answer with the verb, balik."),
                o(S, 9688105, "Do you want to see me?"),
                M,
            ]),
    }))

# ---------------------------------------------------------------- lesson 2
LESSONS.append(dict(
    id="l02", title="Kerja, kerja, kerja", blurb="Tired, busy and counting the days to the next holiday.",
    staff={"label": "Lin", "name": "Lin, a colleague", "voice": "f"}, you={"voice": "m"},
    notes=[
        {"title": "… ke?", "body": "Tack <b>ke</b> onto the end and a statement becomes a question: <i>Penat ke?</i> — tired, are you?"},
        {"title": "kena", "body": "<b>kena</b> + verb means “have to”: <i>kena rehat</i>, <i>kena masuk kerja</i>. Before a noun it means you got hit by it: <i>kena COVID</i>."},
        {"title": "sekali", "body": "At the start of a clause in a story, <b>sekali</b> means “and then, all of a sudden”: <i>Sekali bos panggil…</i>"},
    ],
    phrases={
        "p1": ph(4563523, "Are you tired?", v="f"),
        "p2": ph(11029399, "I'm pretty sleepy, actually.", "gak = juga; la softens it."),
        "p3": ph(10730628, "I've already done a lot of work.", "The doubled dah … dah stresses “already”."),
        "p4": ph(10678817, "This work has to be finished before tomorrow.", "besok = esok.", "f"),
        "p5": ph(11029302, "I think I need to rest for a moment.", "kena = have to."),
        "p6": ph(9714159, "Next Thursday is a holiday.", v="f"),
        "p7": ph(3936635, "Today is very busy."),
        "p8": ph(11029392, "I'm rather sleepy.", "agak = rather, quite."),
        "p9": ph(11518730, "And then the boss called and I had to go in to work.", "sekali = and then suddenly."),
        "p10": ph(11518847, "Still came to work even though sick.", "tetap = still, regardless; walaupun = even though.", "f"),
        "p11": ph(11518729, "The plan is to go on holiday.", "cadangnya = the plan is."),
        "p12": ph(961177, "I want to sleep.", "mahu is the standard word; nak is what you'll hear."),
    },
    match=[["gak", "juga"], ["besok", "esok"], ["sekejap", "sebentar"], ["jugak", "juga"], ["pegi", "pergi"], ["takyah", "tidak payah"], ["bagitau", "beritahu"]],
    levels={
        "easy": dict(
            dialogue=[
                ln(S, 4563523, "Are you tired?"),
                ln(Y, 11029392, "I'm rather sleepy."),
                ln(S, "Ada banyak kerja?", "Got a lot of work?"),
                ln(Y, 3936635, "Today is very busy."),
                ln(S, 10619687, "You go and sleep."),
                ln(Y, 961177, "I want to sleep."),
            ],
            gist=gist("How is he feeling?", "Sleepy after a very busy day", "Hungry and bored", "Excited about a holiday", why="Saya agak mengantuk … Hari ini sangat sibuk."),
            phrases=["p1", "p8", "p7", "p12"],
            listen=[
                c(S, 5900278, "Do you have work after this?", "Did you finish your work?", "Do you like your work?"),
                g(Y, 4587818, "He has a lot of work.", "banyak"),
                c(S, 6482949, "He's on leave today.", "He's working today.", "He's on leave tomorrow."),
                d(Y, 9620997, "I have a lot of work."),
                l(S, 10905545, "You look tired."),
            ],
            read=[
                r(5900157, "Sibuk. Banyak kerja.", ["Saya mahu tidur.", "Penat ke?"], "She asks if you're busy now: sibuk, lots of work."),
                o(S, 9152698, "Why isn't he sleeping?"),
                r("Awak okay?", "Okay. Penat sikit je.", ["Ada banyak kerja?", "Awak pergi tidur."], "Okay, just a bit tired: penat sikit je."),
                o(Y, 12752313, "My older sister has work."),
                M,
            ]),
        "medium": dict(
            dialogue=[
                ln(S, 4563523, "Are you tired?"),
                ln(Y, 11029399, "I'm pretty sleepy, actually."),
                ln(S, 3936635, "Today is very busy."),
                ln(Y, 10730628, "I've already done a lot of work."),
                ln(S, 10678817, "This work has to be finished before tomorrow."),
                ln(Y, 11029302, "I think I need to rest for a moment."),
                ln(S, 9714159, "Next Thursday is a holiday."),
                ln(Y, [5310568, "Aku nak tidur je."], "Great! I just want to sleep."),
            ],
            gist=gist("What's the good news?", "Next Thursday is a holiday", "The work is already finished", "The boss is away tomorrow", "He got a pay rise", why="Khamis minggu depan cuti."),
            phrases=["p1", "p2", "p3", "p4", "p5", "p6"],
            listen=[
                c(S, 9708981, "Nice work.", "Your job is boring.", "Do you have a good job?"),
                g(Y, 10652981, "Don't bother me. I'm busy.", "tengah"),
                c(S, 10726211, "We've finished the work for today.", "We haven't started today's work.", "We have more work today."),
                d(Y, 10229447, "I didn't take leave."),
                l(S, 9689235, "After a short rest, he went back to work."),
            ],
            read=[
                r(11518671, 13696566, ["Khamis minggu depan cuti.", "Bagus kerja kau."], "Lama dah…? asks how long; baru = I'm new to it."),
                o(S, 9700554, "He told me he was really tired."),
                r("Esok kau kerja tak?", "Kerja. Aku tak ambik cuti.", ["Penat ke?", "Bagus kerja kau."], "Answer a … tak? question by repeating the verb: kerja."),
                o(Y, 10729096, "Nobody works there anymore."),
                M,
            ]),
        "hard": dict(
            dialogue=[
                ln(S, [4563523, 10656062], "Tired? You work too hard."),
                ln(Y, [10730628, 11029399], "I've already done a lot of work. I'm pretty sleepy, actually."),
                ln(S, 10678817, "This work has to be finished before tomorrow."),
                ln(Y, ["Tu la. Semalam cuti.", 11518730], "I know. Yesterday was my day off. And then the boss called and I had to go in to work."),
                ln(S, 11518847, "And you still come to work even though you're sick."),
                ln(Y, 11029302, "I think I need to rest for a moment."),
                ln(S, 9714159, "Next Thursday is a holiday."),
                ln(Y, 11518729, "The plan is to go on holiday."),
                ln(S, "Bestnya. Aku pun teringin nak pegi bercuti.", "Nice. I'd love to go on holiday too."),
                ln(Y, "Jom la.", "Come along, then."),
            ],
            gist=gist("What happened on his day off?", "The boss called him in to work", "He slept all day", "He went on holiday", "He stayed home sick", why="Semalam cuti. Sekali bos panggil kena masuk kerja."),
            phrases=["p9", "p10", "p11", "p5", "p4", "p6"],
            listen=[
                c(S, 10657685, "Did you get fired?", "Did you quit your job?", "Have you found a job?", "Did you fire someone?"),
                g(Y, 11518733, "Why on earth didn't I take leave that time.", "cuti"),
                c(S, 11368180, "The pay never comes in, even though the work carries on.", "The pay came in before the work started.", "The pay is good but the work is hard.", "No work, so no pay."),
                d(Y, 10656055, "Those kids are getting more and more tired."),
                l(S, 11380339, "If you're not working, you don't get to make noise about it."),
            ],
            read=[
                r(11518670, ["Baru je.", 13696566], ["Cadangnya nak pegi bercuti.", "Khamis minggu depan cuti."], "Lama dah kerja kat sini? = been working here long?"),
                o(S, 11187964, "And then the whole office got COVID."),
                r("Kau sakit, kenapa datang kerja?", "Bos panggil. Kena masuk kerja jugak.", ["Khamis minggu depan cuti.", "Bagus kerja kau."], "Why come in sick? The boss called, so you had to."),
                o(Y, 10726242, "I've finished my homework."),
                M,
            ]),
    }))

# ---------------------------------------------------------------- lesson 3
LESSONS.append(dict(
    id="l03", title="Jom!", blurb="Making plans, turning them down, and making them again.",
    staff={"label": "Adi", "name": "Adi, a friend", "voice": "m"}, you={"voice": "f"},
    notes=[
        {"title": "jom", "body": "<b>Jom</b> is “let's”: <i>jom makan</i>, <i>jom pergi</i>. <b>Jomlah!</b> on its own is “come on, let's do it!”"},
        {"title": "mungkin", "body": "<b>Mungkin</b> (maybe) is the polite way to stay non-committal: <i>Esok mungkin aku jumpa kau.</i>"},
        {"title": "tak boleh", "body": "<b>Tak boleh</b> covers “can't”, “not allowed” and “doesn't work for me”. Add the day and you have a full excuse: <i>Isnin tak boleh.</i>"},
    ],
    phrases={
        "p1": ph(8875186, "Let's go and play football.", v="m"),
        "p2": ph(4611714, "I can't go."),
        "p3": ph(5900198, "It might rain tomorrow.", "mungkin = maybe."),
        "p4": ph(11518710, "If you don't like it, say so.", v="m"),
        "p5": ph(4609672, "Just kidding!", "bergurau = to joke."),
        "p6": ph(10727704, "Maybe I'll see you tomorrow."),
        "p7": ph(4563532, "Come on, let's go!", v="m"),
        "p8": ph(10772373, "Let's eat out tonight!", v="m"),
        "p9": ph(10789929, "Let's play tennis on Monday.", v="m"),
        "p10": ph(11518716, "It used to be hard to meet up even once a year.", "dulu = back then; payah = difficult."),
        "p11": ph(11395994, "If we only meet once a year, better not bother.", "takat = if it's only; baik = better.", "m"),
        "p12": ph(9714005, "My mum is coming over today."),
    },
    match=[["jom", "mari"], ["pegi", "pergi"], ["macam mana", "bagaimana"], ["je", "sahaja"], ["mak", "emak / ibu"], ["jap", "sekejap"], ["tak payah", "tidak perlu"]],
    levels={
        "easy": dict(
            dialogue=[
                ln(S, 8875186, "Let's go and play football."),
                ln(Y, 4611714, "I can't go."),
                ln(S, "Esok?", "Tomorrow?"),
                ln(Y, 5900198, "It might rain tomorrow."),
                ln(S, 10772373, "Let's eat out tonight!"),
                ln(Y, [11535538, 3936339], "Sure, why not. See you!"),
            ],
            gist=gist("What do they end up planning?", "Eating out tonight", "Football tomorrow", "Nothing at all", why="Jom makan luar malam ni! … Boleh la."),
            phrases=["p1", "p2", "p3", "p8"],
            listen=[
                c(S, 6569289, "Do you want to take a look?", "Do you want to go?", "Did you see it?"),
                g(Y, 3936286, "I'd like to go.", "pergi"),
                c(S, 3936283, "He's here!", "He's already left!", "He isn't coming!"),
                d(Y, 1403351, "See you on Sunday!"),
                l(S, 11056849, "You can't come tomorrow."),
            ],
            read=[
                r(9700640, "Tak nak. Aku tak boleh nyanyi.", ["Esok mungkin hujan.", "Dia dah datang!"], "He's inviting you to sing; you turn it down with tak nak."),
                o(Y, 11074689, "I want you to come."),
                r(1021697, "Nak. Jomlah!", ["Jumpa hari Ahad!", "Nak tengok?"], "Do you want to go? Nak — and jomlah gets things moving."),
                o(S, 10653396, "Today I'm going to the museum."),
                M,
            ]),
        "medium": dict(
            dialogue=[
                ln(S, 8875186, "Let's go and play football."),
                ln(Y, [4611714, 9714005], "I can't go. My mum is coming over today."),
                ln(S, "Esok macam mana?", "How about tomorrow?"),
                ln(Y, 5900198, "It might rain tomorrow."),
                ln(S, 11518710, "If you don't like it, say so."),
                ln(Y, [4609672, 10727704], "Just kidding! Maybe I'll see you tomorrow."),
                ln(S, ["Okay.", 4563532], "Okay. Let's do it!"),
            ],
            gist=gist("Why can't she go today?", "Her mum is coming over", "She has a test", "It's raining", "She's working late", why="Hari ni mak aku nak datang rumah."),
            phrases=["p1", "p2", "p12", "p3", "p4", "p5", "p6"],
            listen=[
                c(S, 10778270, "I think you have to come.", "I think you can't come.", "I think I have to go."),
                g(Y, 10677812, "Can I go first?", "dulu"),
                c(S, 10738298, "Apparently he wants to come here.", "Apparently he isn't coming.", "He said to come here quickly."),
                d(Y, 10674959, "You can't go."),
                l(S, 10730595, "I'm having a really great time tonight."),
            ],
            read=[
                r(10789929, "Isnin tak boleh. Selasa macam mana?", ["Bergurau je!", "Dia dah datang!"], "Turn down the day, then offer another."),
                o(Y, 10727829, "Maybe I'll go in a little while."),
                r("Kau datang tak malam ni?", "Datang. Jumpa lagi!", ["Esok mungkin hujan.", "Kalau tak suka, cakap."], "Answer a … tak? question with the verb: datang."),
                o(S, 10657647, "He only just left."),
                M,
            ]),
        "hard": dict(
            dialogue=[
                ln(S, 11368213, "When are we going for a drink together?"),
                ln(Y, [11518810, "Tapi minggu ni tak boleh."], "I miss hanging out with friends. But this week I can't."),
                ln(S, 10789929, "Let's play tennis on Monday."),
                ln(Y, "Isnin aku dah plan nak balik kampung.", "On Monday I've already planned to go back to my kampung."),
                ln(S, "Wah. Dah lama tak balik kampung?", "Wow. Been a long time since you went back?"),
                ln(Y, 11518716, "It used to be hard to meet up even once a year."),
                ln(S, 11395994, "If we only meet once a year, better not bother."),
                ln(Y, 11518710, "If you don't like it, say so."),
                ln(S, 4609672, "Just kidding!"),
                ln(Y, ["Okay la.", 10727704], "Okay then. Maybe I'll see you tomorrow."),
                ln(S, 4563532, "Come on, let's go!"),
            ],
            gist=gist("What is she doing on Monday?", "Going back to her kampung", "Playing tennis", "Working late", "Meeting him for a drink", why="Isnin aku dah plan nak balik kampung."),
            phrases=["p9", "p10", "p11", "p4", "p5", "p7"],
            listen=[
                c(S, 11540115, "It's due tomorrow, and only now the panic starts.", "It was sent yesterday, so relax.", "Send it tomorrow, there's no rush.", "Tomorrow we can panic together."),
                g(Y, 10684033, "Don't go so fast.", "cepat"),
                c(S, 10666257, "We have a test today.", "We had a test yesterday.", "There's no test today.", "We have a party today."),
                d(Y, 10653396, "Today I'm going to the museum."),
                l(S, 11368237, "You can't just work, right — once in a while you have to take a holiday."),
            ],
            read=[
                r(9688105, ["Nak la.", 10656051], ["Jangan pegi cepat sangat.", "Kita ada ujian hari ni."], "Do you want to see me? Of course — it's been ages."),
                o(S, 10738298, "Apparently he wants to come here."),
                r("Kenapa kau tak datang semalam?", "Sorry. Semalam mak aku datang rumah.", ["Jomlah!", "Takat jumpa setahun sekali, baik tak payah."], "A kenapa question wants a reason."),
                o(Y, 10778270, "I think you have to come."),
                M,
            ]),
    }))

# ---------------------------------------------------------------- lesson 4
LESSONS.append(dict(
    id="l04", title="Dah sampai mana?", blurb="Rain, jams and running late — the KL classics.",
    staff={"label": "Lin", "name": "Lin, a friend", "voice": "f"}, you={"voice": "m"},
    notes=[
        {"title": "Dah sampai mana?", "body": "Literally “arrived where already?” — the standard call or text to someone who is late."},
        {"title": "sempat", "body": "<b>Sempat</b> means there's enough time: <i>sempat</i> (we'll make it), <i>tak sempat</i> (we won't)."},
        {"title": "diorang, kitorang, korang", "body": "Spoken plurals: <b>diorang</b> (they), <b>kitorang</b> (we, not you), <b>korang</b> (you all). They come from <i>dia orang</i>, <i>kita orang</i>, <i>kau orang</i>."},
    ],
    phrases={
        "p1": ph(11518707, "Where have you got to?", "What you ask someone who's on the way.", "f"),
        "p2": ph(10657718, "I think I'm lost.", "sesat = lost."),
        "p3": ph(6457991, "Why are you so late?", v="f"),
        "p4": ph(10903311, "It's been raining since yesterday.", "sejak = since."),
        "p5": ph(10657673, "I don't think we'll make it in time.", "takkan = won't; sempat = make it in time.", "f"),
        "p6": ph(4555877, "Wait a moment."),
        "p7": ph(11518701, "I'm actually already here.", "dah … dah pun stresses that it's already done."),
        "p8": ph(1929801, "Wow, it's hot today, isn't it?", v="f"),
        "p9": ph(3936625, "I'm sorry for being late.", "Polite and fairly formal; with friends, just “sorry lambat”."),
        "p10": ph(11395899, "I've waited so long I've grown a beard, and you're still not here.", "A joke: berjanggut = bearded.", "f"),
        "p11": ph(10677732, "Right now I don't have a car.", "takde = tiada."),
        "p12": ph(11029373, "We have to wait for them.", "diorang = they / them.", "f"),
        "p13": ph(6469709, "So hot!", "-nya on an adjective = “so …!”"),
    },
    match=[["takde", "tiada"], ["diorang", "mereka"], ["lambat", "lewat"], ["sekejap", "sebentar"], ["takkan", "tidak akan"], ["kitorang", "kami"], ["bawak", "bawa"]],
    levels={
        "easy": dict(
            dialogue=[
                ln(S, 1929801, "Wow, it's hot today, isn't it?"),
                ln(Y, 6469709, "So hot!"),
                ln(S, 6457991, "Why are you so late?"),
                ln(Y, 3936625, "I'm sorry for being late."),
                ln(S, "Jalan jem ke?", "Was the traffic jammed?"),
                ln(Y, ["Ya.", 10723479], "Yes. We got lost getting here."),
            ],
            gist=gist("Why was he late?", "He got lost on the way", "His car broke down", "He overslept", why="Kami sesat nak sampai sini."),
            phrases=["p8", "p13", "p3", "p9"],
            listen=[
                c(S, 4731877, "The weather is cold today.", "The weather is hot today.", "It rained today."),
                g(Y, 2913001, "We must wait.", "tunggu"),
                c(S, 5900351, "He is very late.", "He is very early.", "He is very fast."),
                d(Y, 10682866, "Wait for me a moment."),
                l(S, 11129830, "I have to get up early."),
            ],
            read=[
                r(5900236, "Boleh. Saya tunggu.", ["Panasnya.", "Saya minta maaf kerana lewat."], "Can you wait a moment? Boleh — I'll wait."),
                o(Y, 4556556, "I don't have a car."),
                r("Hujan ke?", "Tak. Hari ini panas.", ["Kita mesti tunggu.", "Dia sangat lewat."], "Is it raining? No — it's hot today."),
                o(S, 9682981, "Let him wait."),
                M,
            ]),
        "medium": dict(
            dialogue=[
                ln(S, 11518707, "Where have you got to?"),
                ln(Y, 10657718, "I think I'm lost."),
                ln(S, 6457991, "Why are you so late?"),
                ln(Y, [10903311, "Jalan jem."], "It's been raining since yesterday. The roads are jammed."),
                ln(S, 10657673, "I don't think we'll make it in time."),
                ln(Y, ["Sempat.", 4555877], "We will. Wait a moment."),
                ln(S, ["Okay.", 12624134], "Okay. Be careful on the road!"),
                ln(Y, 11518701, "I'm actually already here."),
            ],
            gist=gist("What is slowing him down?", "Rain and traffic, and he's lost", "He left the house late", "His phone died", "He stopped to eat"),
            phrases=["p1", "p2", "p3", "p4", "p5", "p6", "p7"],
            listen=[
                c(S, 9714029, "I usually get up late.", "I usually get up early.", "I only got up late today."),
                g(Y, 11535547, "What are you still waiting for?", "lagi"),
                c(S, 10677732, "Right now I don't have a car.", "Right now I have a new car.", "My car is right here."),
                d(Y, 10727853, "I have to wash the car."),
                l(S, 11518726, "Before I knew it, I was home."),
            ],
            read=[
                r("Kau kat mana? Dah lambat ni.", "Sorry. Jalan jem teruk.", ["Aku kena cuci kereta.", "Berhati-hati di jalan raya!"], "Where are you, it's late: apologise and give the reason."),
                o(Y, 10778245, "I like driving."),
                r(9695851, "Ha'ah. Aircond ni sejuk gila.", ["Dah sampai dah pun.", "Aku rasa aku dah sesat."], "You're cold, right? Ha'ah — and say why."),
                o(S, 11029373, "We have to wait for them."),
                M,
            ]),
        "hard": dict(
            dialogue=[
                ln(S, 11518707, "Where have you got to?"),
                ln(Y, 10657718, "I think I'm lost."),
                ln(S, ["La.", 11395899], "Oh, come on. I've waited so long I've grown a beard, and you're still not here."),
                ln(Y, ["Sorry la.", 10903311, "Jalan jem teruk."], "Sorry. It's been raining since yesterday. The jam is terrible."),
                ln(S, 10657673, "I don't think we'll make it in time."),
                ln(Y, ["Sempat.", 10677732, "Aku naik Grab."], "We will. Right now I don't have a car. I'm taking a Grab."),
                ln(S, 11029373, "We have to wait for them."),
                ln(Y, "Diorang pun lambat?", "They're late too?"),
                ln(S, 11187973, "For all we know, they don't even have a driving licence."),
                ln(Y, ["Haha.", 4555877, 11518701], "Haha. Wait a moment. I'm actually already here."),
            ],
            gist=gist("How is he getting there?", "By Grab, because he has no car right now", "Driving his own car", "Walking in the rain", "Getting a lift from the others", why="Sekarang ni aku takde kereta. Aku naik Grab."),
            phrases=["p10", "p11", "p12", "p5", "p1", "p7"],
            listen=[
                c(S, 11187979, "The moment we arrived, we got told off.", "We arrived and everyone was happy.", "We got angry and left straight away.", "We arrived before anyone else."),
                g(Y, 10732600, "Everything happened so fast.", "jadi"),
                c(S, 11516633, "I wish this event would hurry up and end.", "This event ended too quickly.", "Hurry, the event is starting.", "The event finished early."),
                d(Y, 11187882, "Why did it get to that point?"),
                l(S, 10723479, "We got lost getting here."),
            ],
            read=[
                r("Diorang dah sampai?", "Belum. Diorang pun sesat.", ["Semua jadi cepat sangat.", "Aku kena cuci kereta."], "Have they arrived? Belum — they're lost too."),
                o(Y, 11518726, "Before I knew it, I was home."),
                r("Sempat tak ni?", "Tak sempat. Jalan jem teruk.", ["Rumah aku sejuk gila.", "Selalunya aku bangun lambat."], "Will we make it? Tak sempat, and the reason."),
                o(S, 9714029, "I usually get up late."),
                M,
            ]),
    }))

# ---------------------------------------------------------------- lesson 5
LESSONS.append(dict(
    id="l05", title="Kau rasa?", blurb="Saying what you think — and that you don't really mind.",
    staff={"label": "Adi", "name": "Adi, a friend", "voice": "m"}, you={"voice": "f"},
    notes=[
        {"title": "gila and betul", "body": "After an adjective, <b>gila</b> (crazy) and <b>betul</b> (really) are intensifiers: <i>best gila</i>, <i>bising betul</i>. Very common, very casual."},
        {"title": "tak kisah", "body": "<b>Aku tak kisah</b> — I don't mind, either way is fine. <b>Malas aku nak kisah</b> is stronger: I can't be bothered to care."},
        {"title": "camtu, camna", "body": "Squeezed forms of <i>macam itu</i> (like that) and <i>macam mana</i> (how): <b>camtu</b>, <b>camna</b>."},
    ],
    phrases={
        "p1": ph(10730605, "I like sitting here.", v="m"),
        "p2": ph(10729127, "This aircon is really noisy.", "betul after an adjective = really."),
        "p3": ph(9714147, "I don't mind.", v="m"),
        "p4": ph(11187984, "What do you think?", "Literally “you feel?”"),
        "p5": ph(11516638, "Both are amazing!", "best = great (from English); gila = crazy.", "m"),
        "p6": ph(9500986, "Is that true?"),
        "p7": ph(10727760, "I'm not always right.", "bukan selalu = not always.", "m"),
        "p8": ph(11535537, "It'll be okay after a while.", "lama-lama = eventually."),
        "p9": ph(10730593, "I've eaten here before.", "pernah = have (at some point).", "m"),
        "p10": ph(11376504, "The price of everything is going up.", "serba-serbi = all sorts of things.", "m"),
        "p11": ph(9689202, "No way, you can't do that.", "camtu = macam itu.", "m"),
        "p12": ph(11380293, "I can't be bothered to care."),
        "p13": ph(10690069, "I don't think there's any need."),
    },
    match=[["camtu", "macam itu"], ["kat", "di"], ["takyah", "tidak payah"], ["tau", "tahu"], ["camna", "macam mana"], ["tu", "itu"], ["korang", "kamu semua"]],
    levels={
        "easy": dict(
            dialogue=[
                ln(S, 10730605, "I like sitting here."),
                ln(Y, 10729127, "This aircon is really noisy."),
                ln(S, 9714147, "I don't mind."),
                ln(Y, [11187984, "Kopi ke teh?"], "What do you think? Coffee or tea?"),
                ln(S, 11516638, "Both are amazing!"),
                ln(Y, 9500986, "Is that true?"),
            ],
            gist=gist("What does he think of the coffee and the tea?", "Both are great", "Both are bad", "Only the tea is good", why="Dua-dua best gila!"),
            phrases=["p1", "p2", "p3", "p4", "p5"],
            listen=[
                c(S, 10677771, "I like his song.", "I don't like his song.", "I know his song."),
                g(Y, 10655093, "I don't like swimming.", "suka"),
                c(S, 3936260, "I don't know.", "I don't want to.", "I don't have it."),
                d(Y, 711822, "Everyone likes him."),
                l(S, 4587807, "He likes coffee without sugar."),
            ],
            read=[
                r(10542284, 10512583, ["Aircond ni bising betul.", "Dua-dua best gila!"], "What colour do you like? Name one."),
                o(Y, 9028641, "He doesn't like me."),
                r("Teh ke kopi? Kau rasa?", "Aku tak kisah. Dua-dua boleh.", ["Semua orang suka dia.", "Aku tak suka berenang."], "Either is fine: tak kisah, dua-dua boleh."),
                o(S, 10158849, "I don't remember his name."),
                M,
            ]),
        "medium": dict(
            dialogue=[
                ln(S, 10730593, "I've eaten here before."),
                ln(Y, [11187984, "Kopi ke teh?"], "What do you think? Coffee or tea?"),
                ln(S, 11516638, "Both are amazing!"),
                ln(Y, 9500986, "Is that true?"),
                ln(S, 10727760, "I'm not always right."),
                ln(Y, 10729127, "This aircon is really noisy."),
                ln(S, [9714147, 10730605], "I don't mind. I like sitting here."),
                ln(Y, 11535537, "It'll be okay after a while."),
            ],
            gist=gist("What bothers her about the place?", "The noisy aircon", "The slow service", "The prices", "The coffee", why="Aircond ni bising betul."),
            phrases=["p9", "p4", "p5", "p6", "p7", "p8"],
            listen=[
                c(S, 10653436, "I know you're nervous.", "I know you're angry.", "I don't know why you're nervous."),
                g(Y, 11029261, "He's crazy rich.", "kaya"),
                c(S, 9724798, "We all like him.", "None of us like him.", "They all like us."),
                d(Y, 10158849, "I don't remember his name."),
                l(S, 9714028, "I agree with your plan."),
            ],
            read=[
                r(4895684, 10666278, ["Aku bukan selalu betul.", "Aku tak ingat nama dia."], "Do I look okay? You look gorgeous."),
                o(Y, 10730631, "I think you're lying to me."),
                r(10730656, "OK je. Kitorang tak kisah.", ["Dia tu kaya gila.", "Betul ke itu?"], "How are you two doing? OK je — fine."),
                o(S, 11187923, "That's all I remember."),
                M,
            ]),
        "hard": dict(
            dialogue=[
                ln(S, 11365036, "I can't be bothered to eat at this mamak."),
                ln(Y, ["Kenapa?", 10730593, "Roti dengan teh tarik,", "dua-dua best gila!"], "Why? I've eaten here before. The roti and the teh tarik, both are amazing!"),
                ln(S, 11376504, "The price of everything is going up."),
                ln(Y, [11540127, "Tapi aku tak kisah."], "It's true what people say… But I don't mind."),
                ln(S, [11187984, "Nak makan kat sini ke?"], "What do you think? Shall we eat here?"),
                ln(Y, "Kalau kau malas, aku rasa tak payah pun.", "If you can't be bothered, I don't think there's any need."),
                ln(S, 9689202, "No way, you can't do that."),
                ln(Y, [11380293, "Kau nak pegi mana?"], "I can't be bothered to care. Where do you want to go?"),
                ln(S, "Takyah susah-susah. Makan kat sini je la.", "No need to make it hard. Let's just eat here."),
                ln(Y, 11535537, "It'll be okay after a while."),
                ln(S, 11535538, "Sure, why not."),
            ],
            gist=gist("Where do they end up eating?", "At the mamak after all", "At an expensive restaurant", "At home", "They skip the meal", why="Takyah susah-susah. Makan kat sini je la."),
            phrases=["p10", "p11", "p12", "p13", "p8", "p4"],
            listen=[
                c(S, 9724643, "This process is insanely complicated.", "This process is really simple.", "This process is too slow.", "This process is finished."),
                g(Y, 9688075, "You're so stubborn!", "degil"),
                c(S, 11380278, "He's like this, you know.", "He knows about this.", "He doesn't like this.", "He did it this way."),
                d(Y, 10784349, "You're crazy brave."),
                l(S, 11376530, "Almost all the shops there are expensive, especially the ones selling headscarves."),
            ],
            read=[
                r("Harga naik lagi. Kau rasa?", "Nak buat macam mana. Aku tak kisah.", ["Berani gila kau.", "Kau nampak lawa gila."], "Prices are up again — what can you do? Nak buat macam mana."),
                o(Y, 10727780, "My dog is crazy smart."),
                r(10730631, "Mana ada. Aku tak tipu kau.", ["Proses ni rumit gila.", "Lama-lama OK la tu."], "Accused of lying: mana ada = no way, that's not so."),
                o(S, 9724798, "We all like him."),
                M,
            ]),
    }))

# ---------------------------------------------------------------- write out
PRE = {"easy": "e", "medium": "m", "hard": "h"}
mdir = ROOT / "content/m05-smalltalk"
mdir.mkdir(exist_ok=True)
entries = []
for L in LESSONS:
    lesson = {"id": f"m05-{L['id']}", "title": L["title"], "blurb": L["blurb"], "staff": L["staff"], "you": L["you"],
              "notes": L["notes"], "phrases": L["phrases"], "match": L["match"], "clips": [], "levels": {}}
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
        lesson["levels"][level] = {"dialogue": dialogue, "gist": lv["gist"], "phrases": lv["phrases"], "drills": drills}
    (mdir / f"{L['id']}.json").write_text(json.dumps(lesson, ensure_ascii=False, indent=1) + "\n")
    entries.append({"id": L["id"], "file": f"{L['id']}.json", "title": L["title"], "blurb": L["blurb"]})

module = {"id": "m05", "title": "Small talk", "lessons": entries,
          "finale": {"title": "Module 5 test", "blurb": "Twelve questions drawn from all five lessons.", "testSize": 12}, "clips": []}
(mdir / "module.json").write_text(json.dumps(module, ensure_ascii=False, indent=1) + "\n")

# attribution list for the credits page (CC BY 2.0 FR needs author + source)
credits = [{"id": i, "by": u, "ms": t} for i, (t, u) in sorted(USED.items())]
(mdir / "sources.json").write_text(json.dumps(credits, ensure_ascii=False, indent=1) + "\n")
print(f"wrote {len(LESSONS)} lessons; {len(USED)} Tatoeba sentences used")
