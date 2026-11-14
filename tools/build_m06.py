#!/usr/bin/env python3
"""Build Module 6 (Pasar & shops).

Usage: python tools/build_m06.py <dir with zlm.tsv and zsm.tsv>
See tools/tatoeba_build.py for how lines are assembled. Price, money and
looking-for-things sentences come from the corpus; stall talk (weights,
haggling numbers, QR payment) is written.
"""
import json

from tatoeba_build import *  # noqa: F401,F403

LESSONS = []

# ---------------------------------------------------------------- lesson 1
LESSONS.append(dict(
    id="l01", title="Berapa harga ni?", blurb="Asking prices at a fruit stall, and tasting before you buy.",
    staff={"label": "Kak", "name": "Stallholder", "voice": "f"}, you={"voice": "m"},
    notes=[
        {"title": "Berapa?", "body": "<b>Berapa</b> asks how much or how many. <i>Berapa harga ni?</i> — how much is this? At a stall, pointing and saying <i>Berapa?</i> is enough."},
        {"title": "sekilo, sebiji", "body": "<b>se-</b> means “one”: <b>sekilo</b> = one kilo, <b>sebiji</b> = one (piece of fruit). Prices are usually per kilo: <i>dua belas ringgit sekilo</i>."},
        {"title": "Cuba rasa dulu", "body": "“Try a taste first.” Fruit sellers will often offer; <b>manis tak?</b> (is it sweet?) is the question that gets you a sample."},
    ],
    match=[["ni", "ini"], ["tu", "itu"], ["tak", "tidak"], ["je", "sahaja"], ["ambik", "ambil"], ["tak payah", "tidak perlu"], ["dua-dua", "kedua-duanya"]],
    levels={
        "easy": dict(
            dialogue=[
                ln(Y, 6938144, "How much is this?"),
                ln(S, "Lima ringgit.", "Five ringgit."),
                ln(Y, "Yang ni?", "And this one?"),
                ln(S, [924021, "Tiga ringgit je."], "This one isn't expensive. Only three ringgit."),
                ln(Y, 961001, "I must buy one."),
                ln(S, "Okay. Terima kasih.", "Okay. Thank you."),
            ],
            gist=gist("How much is the cheaper one?", "Three ringgit", "Five ringgit", "Eight ringgit", why="Yang ini tak mahal. Tiga ringgit je."),
            listen=[
                c(S, 3936297, "How much is it?", "How many are there?", "Where is it?"),
                g(Y, 5239320, "This price is expensive.", "mahal"),
                c(S, 2915790, "This plastic chair is very cheap.", "This plastic chair is very expensive.", "This plastic chair is broken."),
                d(Y, 7850527, "Just a little."),
                l(S, 1230096, "How much is this?"),
            ],
            read=[
                r("Mahal tak?", "Tak mahal. Lima ringgit je.", ["Saya mesti beli satu.", "Yang ni?"], "Mahal tak? — tak mahal, and the price."),
                o(Y, 4839717, "This book is very expensive."),
                r("Nak beli berapa?", "Satu je.", ["Lima ringgit.", "Terima kasih."], "Berapa here asks how many: satu je — just one."),
                o(S, 9419770, "How many apples?"),
                M,
            ]),
        "medium": dict(
            dialogue=[
                ln(S, 10583556, "What are you looking for?"),
                ln(Y, ["Tengok-tengok je.", 11158001], "Just looking. How much are the grapes?"),
                ln(S, "Anggur dua belas ringgit sekilo.", "Grapes are twelve ringgit a kilo."),
                ln(Y, 3936333, "That's expensive."),
                ln(S, [924021, "Lapan ringgit je."], "This one isn't expensive. Only eight ringgit."),
                ln(Y, "Manis tak?", "Is it sweet?"),
                ln(S, "Manis. Cuba rasa dulu.", "It's sweet. Try a taste first."),
                ln(Y, ["Okay, sedap.", 961001], "Okay, it's good. I must buy one."),
            ],
            gist=gist("Why does he buy the second kind?", "It's cheaper, and it tastes good", "The first kind was sold out", "It's bigger", "She gives it to him free", why="Yang ini tak mahal … Okay, sedap."),
            listen=[
                c(S, 13949661, "This meat is too expensive.", "This meat is very cheap.", "This meat isn't fresh."),
                g(Y, 10682997, "The price of rice has come down.", "turun"),
                c(S, 10677728, "And how much is that thing?", "How many of those do you have?", "Why is that thing so expensive?"),
                d(Y, 3936297, "How much is it?"),
                l(S, 960687, "How much is this red hat?"),
            ],
            read=[
                r(9695830, "Nak beli anggur sikit.", ["Harganya mahal.", "Cuba rasa dulu."], "Apa kau nak beli? — what do you want to buy: name it."),
                o(Y, 5200280, "Food prices at this shop are very expensive."),
                r("Anggur ni manis tak?", "Manis sangat. Rasa lah.", ["Lapan ringgit je.", "Tengok-tengok je."], "Manis tak? — manis, and an invitation to taste."),
                o(S, 720237, "That apple is very red."),
                M,
            ]),
        "hard": dict(
            dialogue=[
                ln(S, 10583556, "What are you looking for?"),
                ln(Y, ["Tengok-tengok je, kak.", 11158001], "Just looking. How much are the grapes?"),
                ln(S, "Anggur hijau dua belas, yang merah lima belas sekilo.", "Green grapes are twelve, the red ones fifteen a kilo."),
                ln(Y, 11395878, "Things just keep getting more expensive."),
                ln(S, ["Tu la.", 11376504], "I know. The price of everything is going up."),
                ln(Y, "Yang hijau tu manis tak?", "Are the green ones sweet?"),
                ln(S, "Manis. Cuba rasa dulu, tak payah bayar.", "They're sweet. Try one first, no need to pay."),
                ln(Y, "Hmm, masam sikit.", "Hmm, a bit sour."),
                ln(S, "Yang tu belum masak lagi. Ambik yang ni.", "That one isn't ripe yet. Take this one."),
                ln(Y, "Ha, yang ni sedap. Tapi yang merah pun nampak sedap.", "Ah, this one's good. But the red ones look good too."),
                ln(S, 11220443, "How about you buy both?"),
                ln(Y, ["Okay lah.", 11365012], "Okay then. It'd be a loss not to buy."),
            ],
            gist=gist("What does he end up buying?", "Both the green and the red grapes", "Only the green grapes", "Only the red grapes", "Nothing — too expensive", why="Apa kata kau beli dua-dua? … Okay lah."),
            listen=[
                c(S, 11518677, "Not like now, when everything is expensive.", "Just like now, everything was cheap.", "Now everything is cheaper than before.", "Nothing is expensive these days."),
                g(Y, 11187905, "This book is expensive wherever you buy it.", "mana-mana"),
                c(S, 11516632, "I thought it was finished, but it turns out there's more.", "I thought there was more, but it's finished.", "It's finished and there won't be more.", "I knew there was plenty left."),
                d(Y, 10682997, "The price of rice has come down."),
                l(S, 10876355, "Oranges are sweeter than limes."),
            ],
            read=[
                r("Yang hijau dua belas, yang merah lima belas. Nak yang mana?", "Yang hijau lah. Murah sikit.", ["Rugi la kalau tak beli.", "Masam sikit."], "Yang mana? — which one: choose, and say why."),
                o(Y, 10681166, "That banana isn't ripe yet."),
                r("Tak nak beli ke? Murah ni.", "Mahal lah, kak. Lain kali lah.", ["Cuba rasa dulu.", "Yang ni sedap."], "A polite way out: lain kali lah — next time."),
                o(S, 11884127, "Green apples are smaller than red ones."),
                M,
            ]),
    }))

# ---------------------------------------------------------------- lesson 2
LESSONS.append(dict(
    id="l02", title="Kurang sikit boleh?", blurb="Gentle bargaining: too expensive, a bit less, last price.",
    staff={"label": "Abg", "name": "Stallholder", "voice": "m"}, you={"voice": "f"},
    notes=[
        {"title": "Kurang sikit boleh?", "body": "“Can it be a bit less?” — the standard opening move. Smile when you say it; this is a game both sides know."},
        {"title": "… lah", "body": "<b>lah</b> softens a counter-offer: <i>dua puluh lima lah</i> — come on, twenty-five. Sellers answer in kind: <i>okay lah</i>."},
        {"title": "mampu and rugi", "body": "<b>Tak mampu</b> = can't afford it. <b>Rugi</b> = a loss: the seller says <i>rugi saya</i> (I'd lose money); friends say <i>rugi kalau tak beli</i> (you'd lose out not buying)."},
    ],
    match=[["takde", "tiada"], ["sikit", "sedikit"], ["je", "sahaja"], ["ni", "ini"], ["jugak", "juga"], ["kecik", "kecil"], ["tau", "tahu"]],
    levels={
        "easy": dict(
            dialogue=[
                ln(Y, 3936297, "How much is it?"),
                ln(S, "Dua puluh ringgit.", "Twenty ringgit."),
                ln(Y, 5239320, "This price is expensive."),
                ln(S, "Okay, lapan belas.", "Okay, eighteen."),
                ln(Y, "Lima belas boleh?", "Can you do fifteen?"),
                ln(S, "Boleh lah.", "Okay then."),
            ],
            gist=gist("What price do they agree on?", "Fifteen ringgit", "Eighteen ringgit", "Twenty ringgit", why="Lima belas boleh? … Boleh lah."),
            listen=[
                c(S, 924021, "This one isn't expensive.", "This one is very expensive.", "This one isn't for sale."),
                g(Y, 3276538, "I have a little money.", "sedikit"),
                c(S, 3936400, "I don't have any money.", "I have a lot of money.", "I found some money."),
                d(Y, 3936334, "That price is expensive."),
                l(S, 9294870, "Can the price be discounted?"),
            ],
            read=[
                r("Dua puluh ringgit. Okay?", "Mahal lah. Lima belas boleh?", ["Dua puluh ringgit.", "Berapa harganya?"], "Too much? Say mahal lah, then name your price."),
                o(Y, 974240, "I forgot my money."),
                r("Kurang sikit boleh?", "Boleh. Lapan belas.", ["Harga ini mahal.", "Saya terlupa duit saya."], "Asked for a discount: boleh, and the new price."),
                o(S, 8658129, "I need money."),
                M,
            ]),
        "medium": dict(
            dialogue=[
                ln(Y, ["Bang.", 1230096], "Excuse me. How much is this?"),
                ln(S, "Tiga puluh ringgit.", "Thirty ringgit."),
                ln(Y, 10761188, "These shoes are seriously expensive."),
                ln(S, "Kualiti bagus ni. Tak rugi.", "This is good quality. You won't lose out."),
                ln(Y, "Kurang sikit boleh?", "Can it be a bit less?"),
                ln(S, "Dua puluh lapan.", "Twenty-eight."),
                ln(Y, ["Dua puluh lima.", 10684039], "Twenty-five. This is all the money I have."),
                ln(S, "Okay lah, dua puluh lima. Untuk awak je.", "Okay then, twenty-five. Just for you."),
            ],
            gist=gist("How much does she pay for the shoes?", "Twenty-five ringgit", "Twenty-eight ringgit", "Thirty ringgit", "She walks away", why="Okay lah, dua puluh lima."),
            listen=[
                c(S, 10761179, "These shoes are too expensive.", "These shoes are too small.", "These shoes are very cheap."),
                g(Y, 10690011, "He doesn't have very much money.", "banyak"),
                c(S, 5900277, "How much money do you have left?", "How much money did you spend?", "How much do you want to pay?"),
                d(Y, 974240, "I forgot my money."),
                l(S, 11518825, "I thought he wanted to borrow money."),
            ],
            read=[
                r("Tiga puluh. Kualiti bagus ni.", "Mahal lah. Kurang sikit boleh?", ["Untuk awak je.", "Tak rugi."], "He's defending the price; you still ask for less."),
                o(Y, 5200284, "May I borrow your money?"),
                r("Dua puluh lapan. Nak tak?", "Dua puluh lima lah. Ini je yang saya ada.", ["Tiga puluh ringgit.", "Kualiti bagus ni."], "Counter with a number and a reason."),
                o(S, 3936400, "I don't have any money."),
                M,
            ]),
        "hard": dict(
            dialogue=[
                ln(Y, "Bang, kasut ni berapa?", "How much are these shoes?"),
                ln(S, "Lapan puluh. Original ni.", "Eighty. These are original."),
                ln(Y, [10761188, "Kedai sebelah jual enam puluh je."], "These shoes are seriously expensive. The shop next door sells them for just sixty."),
                ln(S, "Itu lain. Yang ni kualiti bagus.", "Those are different. These are good quality."),
                ln(Y, "Kurang sikit lah, bang. Enam puluh boleh?", "A bit less, come on. Can you do sixty?"),
                ln(S, "Tak boleh lah, rugi saya. Tujuh puluh lima.", "I can't, I'd lose money. Seventy-five."),
                ln(Y, 11380307, "I've wanted to buy these for ages but can't afford them."),
                ln(S, "Okay, okay. Tujuh puluh. Last price.", "Okay, okay. Seventy. Last price."),
                ln(Y, ["Enam puluh lima.", 10684039], "Sixty-five. This is all the money I have."),
                ln(S, [6387846, "Haha. Okay lah, enam puluh lima."], "Do you have money or not? Haha. Okay then, sixty-five."),
                ln(Y, "Terima kasih, bang!", "Thank you!"),
            ],
            gist=gist("What is the final price?", "Sixty-five ringgit", "Sixty ringgit", "Seventy ringgit", "Seventy-five ringgit", why="Okay lah, enam puluh lima."),
            listen=[
                c(S, 11521599, "Buy what? I don't even have any money.", "I'll buy anything, I have money.", "What did you buy with the money?", "I bought it, so the money's gone."),
                g(Y, 11521603, "Knows there's no money, and still wants to buy.", "jugak"),
                c(S, 11540126, "I thought they only sold the small size.", "I thought they only sold the big size.", "I knew they had every size.", "They told me the small size was sold out."),
                d(Y, 10690011, "He doesn't have very much money."),
                l(S, 11395878, "Things just keep getting more expensive."),
            ],
            read=[
                r("Lapan puluh ringgit. Barang original.", "Mahal sangat. Kedai sebelah jual enam puluh.", ["Last price.", "Terima kasih, bang!"], "Compare with the shop next door — a classic bargaining move."),
                o(Y, 5900277, "How much money do you have left?"),
                r("Tujuh puluh. Last price.", "Enam puluh lima lah. Tak mampu.", ["Original ni.", "Itu lain."], "Even at “last price” you can try once more: tak mampu — can't afford it."),
                o(S, 11518825, "I thought he wanted to borrow money."),
                M,
            ]),
    }))

# ---------------------------------------------------------------- lesson 3
LESSONS.append(dict(
    id="l03", title="Nak berapa kilo?", blurb="Quantities at the wet market: kilos, pieces, half a tray of eggs.",
    staff={"label": "Kak", "name": "Stallholder", "voice": "f"}, you={"voice": "m"},
    notes=[
        {"title": "biji, kilo, papan", "body": "Fruit and eggs are counted in <b>biji</b>: <i>lima biji epal</i>. Most other things go by <b>kilo</b>. A tray of thirty eggs is <b>sepapan</b>; half a tray is <i>setengah papan</i>."},
        {"title": "setengah", "body": "<b>Setengah</b> = half: <i>setengah kilo</i>. <b>Sekilo setengah</b> = a kilo and a half."},
        {"title": "Lagi?", "body": "The stallholder's “anything else?” Answer with the next item, or <b>itu je</b> — that's all."},
    ],
    match=[["nak", "hendak"], ["je", "sahaja"], ["bijik", "biji"], ["sikit", "sedikit"], ["tak payah", "tidak perlu"], ["dah", "sudah"], ["tu", "itu"]],
    levels={
        "easy": dict(
            dialogue=[
                ln(Y, "Kak, nak epal.", "I'd like some apples."),
                ln(S, 9419770, "How many apples?"),
                ln(Y, "Lima biji.", "Five."),
                ln(S, "Lagi?", "Anything else?"),
                ln(Y, "Itu je.", "That's all."),
                ln(S, "Lima ringgit.", "Five ringgit."),
            ],
            gist=gist("How many apples does he buy?", "Five", "One", "A kilo", why="Lima biji."),
            listen=[
                c(S, 3936573, "I ate an apple.", "I bought an apple.", "I ate five apples."),
                g(Y, 1230484, "This box contains apples.", "kotak"),
                c(S, 4839615, "Is there any sugar?", "Is it sweet?", "Do you want sugar?"),
                d(Y, 720237, "That apple is very red."),
                l(S, 10732649, "Have you bought the eggs?"),
            ],
            read=[
                r("Nak berapa biji?", "Tiga biji je.", ["Lima ringgit.", "Nak epal."], "Berapa biji? — how many: a number + biji."),
                o(Y, 10512580, "Bananas are yellow."),
                r("Nak apa-apa lagi?", "Tak. Itu je.", ["Lima biji.", "Berapa biji epal?"], "Anything else? No — itu je."),
                o(S, 3936410, "I don't like eggs."),
                M,
            ]),
        "medium": dict(
            dialogue=[
                ln(S, "Ya, nak apa?", "Yes, what would you like?"),
                ln(Y, "Bawang sekilo. Dengan cili setengah kilo.", "A kilo of onions. And half a kilo of chillies."),
                ln(S, "Bawang besar ke bawang kecil?", "Big onions or small onions?"),
                ln(Y, "Bawang besar.", "Big onions."),
                ln(S, "Lagi?", "Anything else?"),
                ln(Y, 4839615, "Is there any sugar?"),
                ln(S, [11516632, "Nak berapa?"], "I thought it was finished, but it turns out there's more. How much do you want?"),
                ln(Y, "Sekilo je.", "Just a kilo."),
            ],
            gist=gist("What happened with the sugar?", "She thought it had run out, but there was some left", "It was sold out", "It was too expensive", "He decided he didn't need it", why="Ingatkan dah habis, rupanya ada lagi."),
            listen=[
                c(S, 10732639, "Did you buy the eggs?", "Did you eat the eggs?", "Do you sell eggs?"),
                g(Y, 10655082, "There's a little milk in that bottle.", "botol"),
                c(S, 9695726, "I have two pears.", "I ate two pears.", "I want two pears."),
                d(Y, 9500969, "I want to buy a bit of food."),
                l(S, 10724976, "How much honey should I buy?"),
            ],
            read=[
                r("Cili nak berapa?", "Setengah kilo je.", ["Bawang besar.", "Ada gula?"], "Nak berapa? — how much: an amount."),
                o(Y, 10732649, "Have you bought the eggs?"),
                r("Gula ada lagi tak?", "Ada lagi. Nak berapa kilo?", ["Sekilo je.", "Bawang sekilo."], "Ada lagi tak? — is there still some: ada lagi."),
                o(S, 3936573, "I ate an apple."),
                M,
            ]),
        "hard": dict(
            dialogue=[
                ln(S, "Ya dik, nak apa hari ni?", "Yes, what would you like today?"),
                ln(Y, "Nak ikan. Ikan apa yang segar hari ni?", "I want fish. Which fish is fresh today?"),
                ln(S, "Semua segar. Kembung baru sampai pagi tadi.", "All of it is fresh. The mackerel only came in this morning."),
                ln(Y, "Kembung sekilo berapa?", "How much is mackerel a kilo?"),
                ln(S, "Lima belas.", "Fifteen."),
                ln(Y, "Okay, bagi setengah kilo. Tolong siang sekali.", "Okay, give me half a kilo. Please clean them too."),
                ln(S, "Boleh. Lagi?", "Sure. Anything else?"),
                ln(Y, "Telur ada?", "Do you have eggs?"),
                ln(S, "Ada. Sepapan ke setengah?", "Yes. A tray or half?"),
                ln(Y, "Setengah papan je.", "Just half a tray."),
                ln(S, [10542208, "Nak plastik lagi satu?"], "The bag's full. Want another plastic bag?"),
                ln(Y, "Tak payah, saya ada beg.", "No need, I have a bag."),
            ],
            gist=gist("What does he ask her to do with the fish?", "Clean them for him", "Cut them in half", "Keep them for later", "Weigh them again", why="Tolong siang sekali."),
            listen=[
                c(S, 5900202, "This box is quite heavy, isn't it!", "This box is quite light, isn't it!", "This box is empty, isn't it!", "This box is too big, isn't it!"),
                g(Y, 10681166, "That banana isn't ripe yet.", "masak"),
                c(S, 11518687, "Just a little more and it's finished.", "It finished a long time ago.", "There's still plenty left.", "It will never be finished."),
                d(Y, 10732639, "Did you buy the eggs?"),
                l(S, 10903250, "You sell some apples at the market."),
            ],
            read=[
                r("Kembung sekilo lima belas. Nak berapa?", "Setengah kilo je. Tolong siang sekali.", ["Semua segar.", "Saya ada beg."], "How much do you want? An amount — and ask her to clean them."),
                o(Y, 9881562, "We got a lot of stuff."),
                r("Nak plastik?", "Tak payah. Saya ada beg.", ["Setengah papan je.", "Baru sampai pagi tadi."], "Turning down a plastic bag: tak payah."),
                o(S, 10655082, "There's a little milk in that bottle."),
                M,
            ]),
    }))

# ---------------------------------------------------------------- lesson 4
LESSONS.append(dict(
    id="l04", title="Cari apa?", blurb="In a shop: what you're looking for, size, colour and “maybe next time”.",
    staff={"label": "Abg", "name": "Shop assistant", "voice": "m"}, you={"voice": "f"},
    notes=[
        {"title": "cari", "body": "<b>Cari</b> = look for. <i>Apa yang awak cari?</i> — what are you looking for? <i>Saya cari kasut</i> — I'm looking for shoes."},
        {"title": "muat", "body": "<b>Muat tak?</b> — does it fit? Answers: <i>muat</i>, <i>besar sikit</i> (a bit big), <i>kecik sikit</i> (a bit small)."},
        {"title": "lain kali", "body": "<b>Mungkin lain kali</b> — maybe next time — is the easy, polite way to leave without buying."},
    ],
    match=[["kecik", "kecil"], ["takde", "tiada"], ["sikit", "sedikit"], ["kot", "agaknya"], ["macam ni", "begini"], ["takyah", "tidak payah"], ["je", "sahaja"]],
    levels={
        "easy": dict(
            dialogue=[
                ln(S, 10583556, "What are you looking for?"),
                ln(Y, "Saya cari baju.", "I'm looking for a top."),
                ln(S, 10542284, "What colour do you like?"),
                ln(Y, "Saya suka biru.", "I like blue."),
                ln(S, "Saiz apa?", "What size?"),
                ln(Y, "Saiz M.", "Size M."),
            ],
            gist=gist("What is she shopping for?", "A blue top, size M", "Black shoes, size 7", "A white bag", why="Saya cari baju … biru … saiz M."),
            listen=[
                c(S, 6469504, "Whose bag is this?", "Where is this bag from?", "How much is this bag?"),
                g(Y, 342112, "The sky is blue.", "biru"),
                c(S, 3942271, "This pencil is white.", "This pencil is black.", "This pencil is new."),
                d(Y, 3276540, "That table is green."),
                l(S, 9621016, "The shirt is white and black."),
            ],
            read=[
                r("Nak warna apa?", "Warna hitam.", ["Saiz M.", "Saya cari baju."], "Warna apa? — which colour."),
                o(Y, 9621007, "The shirt is white and red."),
                r("Awak pakai saiz apa?", "Saiz S.", ["Warna biru.", "Saya suka biru."], "Saiz apa? — which size."),
                o(S, 634156, "That book is small."),
                M,
            ]),
        "medium": dict(
            dialogue=[
                ln(S, 10583556, "What are you looking for?"),
                ln(Y, "Saya cari kasut.", "I'm looking for shoes."),
                ln(S, 10583707, "What size are you looking for?"),
                ln(Y, "Saiz tujuh. Warna hitam ada?", "Size seven. Do you have black?"),
                ln(S, "Hitam habis. Putih ada.", "Black is sold out. We have white."),
                ln(Y, "Boleh cuba yang putih?", "Can I try the white ones?"),
                ln(S, "Boleh. Muat tak?", "Sure. Do they fit?"),
                ln(Y, "Besar sikit. Saiz enam ada?", "A bit big. Do you have size six?"),
                ln(S, 3936700, "I'll try to find it."),
            ],
            gist=gist("What's wrong with the white shoes?", "They're a bit big", "They're too expensive", "They're the wrong colour", "They're sold out", why="Besar sikit. Saiz enam ada?"),
            listen=[
                c(S, 5311481, "Where did you buy that shirt?", "When did you buy that shirt?", "Why did you buy that shirt?"),
                g(Y, 5491975, "Because it's too big.", "besar"),
                c(S, 10583778, "What kind of shoes are you looking for?", "What size shoes do you wear?", "Where did you find those shoes?"),
                d(Y, 9621016, "The shirt is white and black."),
                l(S, 11540126, "I thought they only sold the small size."),
            ],
            read=[
                r("Muat tak?", "Kecik sikit. Ada saiz besar?", ["Warna hitam ada?", "Saya cari kasut."], "Does it fit? A bit small — ask for a bigger size."),
                o(Y, 12752310, "I'm looking for a wallet."),
                r("Hitam habis. Nak warna lain?", "Boleh. Putih ada?", ["Saiz tujuh.", "Besar sikit."], "Offered another colour: boleh, and ask what there is."),
                o(S, 9621007, "The shirt is white and red."),
                M,
            ]),
        "hard": dict(
            dialogue=[
                ln(S, 10583556, "What are you looking for?"),
                ln(Y, "Saya cari kasut. Yang macam ni, tapi warna hitam.", "I'm looking for shoes. Like these, but in black."),
                ln(S, 10583707, "What size are you looking for?"),
                ln(Y, "Saiz tujuh.", "Size seven."),
                ln(S, "Hitam saiz tujuh habis lah. Tinggal saiz kecik je.", "Black in size seven is sold out. Only small sizes are left."),
                ln(Y, "Alamak. Bila stok baru sampai?", "Oh no. When does new stock arrive?"),
                ln(S, ["Minggu depan kot. Kejap.", 3936700], "Next week, I think. Hang on. I'll try to find it."),
                ln(Y, "Okay, terima kasih.", "Okay, thank you."),
                ln(S, "Jumpa! Tapi warna biru. Nak cuba?", "Found some! But in blue. Want to try them?"),
                ln(Y, "Boleh lah. Hmm, muat. Tapi biru…", "Okay then. Hmm, they fit. But blue…"),
                ln(S, "Cantik tu. Sesuai dengan awak.", "They're nice. They suit you."),
                ln(Y, [10723468, "Saya fikir dulu."], "Maybe next time. I'll think about it first."),
            ],
            gist=gist("Why doesn't she buy the shoes?", "They only have her size in blue, not black", "They don't fit", "They cost too much", "The shop is closing", why="Jumpa! Tapi warna biru … Mungkin lain kali."),
            listen=[
                c(S, 11395918, "There's still time to go shopping for Raya.", "It's too late to shop for Raya.", "Shopping for Raya is finished.", "I never shop for Raya."),
                g(Y, 11365041, "No need for the headache of looking for clothes.", "cari"),
                c(S, 10723478, "Another time, I guess.", "Right now, I guess.", "Never again, I guess.", "Every time, I guess."),
                d(Y, 5491975, "Because it's too big."),
                l(S, 11376577, "Arrange things neatly so they're easy to find later."),
            ],
            read=[
                r("Stok baru sampai minggu depan. Nak tunggu?", "Takpe lah. Mungkin lain kali.", ["Saiz tujuh.", "Jumpa!"], "Not waiting: takpe lah, mungkin lain kali."),
                o(Y, 12752310, "I'm looking for a wallet."),
                r("Biru je ada. Nak cuba?", "Boleh lah, cuba dulu.", ["Minggu depan kot.", "Sesuai dengan awak."], "Only blue — sure, try first: cuba dulu."),
                o(S, 10583778, "What kind of shoes are you looking for?"),
                M,
            ]),
    }))

# ---------------------------------------------------------------- lesson 5
LESSONS.append(dict(
    id="l05", title="Bayar macam mana?", blurb="Paying up: cash, card or QR, and what to do when you're three ringgit short.",
    staff={"label": "Kak", "name": "Shopkeeper", "voice": "f"}, you={"voice": "m"},
    notes=[
        {"title": "cash, kad, QR", "body": "Small shops and stalls take <b>cash</b> or <b>QR</b> (DuitNow / e-wallet); many don't take <b>kad</b>. <i>Scan sini</i> — scan here."},
        {"title": "baki and duit kecik", "body": "<b>Baki</b> = change (what's left). <b>Duit kecik</b> or <b>duit pecah</b> = small change. <i>Takde duit kecik</i> — no small notes."},
        {"title": "Semua sekali", "body": "<b>Semua sekali</b> = all together: <i>Semua sekali berapa?</i> — how much for everything?"},
    ],
    match=[["takde", "tiada"], ["kecik", "kecil"], ["tak boleh", "tidak boleh"], ["jugak", "juga"], ["je", "sahaja"], ["dah", "sudah"], ["takpe", "tidak apa"]],
    levels={
        "easy": dict(
            dialogue=[
                ln(S, 12623531, "Please pay here."),
                ln(Y, "Berapa semua?", "How much is everything?"),
                ln(S, "Dua puluh ringgit.", "Twenty ringgit."),
                ln(Y, "Bayar cash boleh?", "Can I pay cash?"),
                ln(S, "Boleh.", "Yes."),
                ln(Y, "Nah. Terima kasih.", "Here you go. Thank you."),
            ],
            gist=gist("How does he pay?", "In cash", "By card", "By QR code", why="Bayar cash boleh? … Boleh."),
            listen=[
                c(S, 9186372, "We can pay in cash.", "We can't pay in cash.", "We already paid in cash."),
                g(Y, 3936400, "I don't have any money.", "duit"),
                c(S, 924047, "This shop closes at 9.", "This shop opens at 9.", "This shop is closed today."),
                d(Y, 8658129, "I need money."),
                l(S, 10500837, "Do you sell mineral water?"),
            ],
            read=[
                r("Cash ke kad?", "Cash. Nah, dua puluh.", ["Berapa semua?", "Sila bayar di sini."], "Cash or card? Choose one, and hand it over: nah."),
                o(Y, 3276538, "I have a little money."),
                r("Semua sekali berapa?", "Dua puluh ringgit je.", ["Bayar cash boleh?", "Terima kasih."], "How much altogether? The total."),
                o(S, 5137389, "This shop isn't open today."),
                M,
            ]),
        "medium": dict(
            dialogue=[
                ln(S, "Semua sekali tiga puluh dua ringgit.", "Thirty-two ringgit altogether."),
                ln(Y, 3936621, "Can I pay by credit card?"),
                ln(S, "Kad tak boleh. Cash ke QR je.", "No cards. Cash or QR only."),
                ln(Y, "Okay, cash lah. Lima puluh, ada baki?", "Okay, cash then. A fifty — do you have change?"),
                ln(S, 5900274, "I don't have any small change."),
                ln(Y, "Kalau macam tu, saya scan QR.", "In that case, I'll scan the QR."),
                ln(S, "Okay, scan sini. Dah masuk?", "Okay, scan here. Has it gone through?"),
                ln(Y, "Dah. Terima kasih, kak.", "Yes. Thank you."),
            ],
            gist=gist("Why does he end up paying by QR?", "She has no change for his fifty", "He has no cash", "QR is cheaper", "The card machine worked", why="Saya tiada duit pecah … saya scan QR."),
            listen=[
                c(S, 10163695, "My money got stolen.", "I found some money.", "I spent all my money."),
                g(Y, 10158826, "Give me back my money.", "balik"),
                c(S, 8653173, "They sell everything here.", "They sell nothing here.", "They buy everything here."),
                d(Y, 9186372, "We can pay in cash."),
                l(S, 5200284, "May I borrow your money?"),
            ],
            read=[
                r("Lima puluh. Ada baki?", "Takde duit kecik lah.", ["Dah masuk?", "Scan sini."], "Asked for change: takde duit kecik — no small notes."),
                o(Y, 6387846, "Do you have money or not?"),
                r("Dah masuk?", "Dah. Tiga puluh dua ringgit.", ["Kad tak boleh.", "Ada baki?"], "Has the payment gone through? Dah, and the amount."),
                o(S, 10778241, "Please give me back my money."),
                M,
            ]),
        "hard": dict(
            dialogue=[
                ln(S, "Semua sekali empat puluh tiga ringgit.", "Forty-three ringgit altogether."),
                ln(Y, 3936621, "Can I pay by credit card?"),
                ln(S, "Kad tak boleh lah. Mesin rosak. Cash ke QR je.", "No cards, sorry. The machine's broken. Cash or QR only."),
                ln(Y, [974240, "QR lah."], "I forgot my money. QR, then."),
                ln(S, "Okay, scan sini.", "Okay, scan here."),
                ln(Y, "Eh, internet slow. Tak boleh scan.", "Oh, the internet's slow. I can't scan."),
                ln(S, "Cuba lagi sekali.", "Try once more."),
                ln(Y, ["Tak boleh jugak. Kejap, saya cari cash.", 10684039], "Still can't. Hang on, I'll look for cash. This is all the money I have."),
                ln(S, "Empat puluh je? Kurang tiga ringgit.", "Only forty? You're three ringgit short."),
                ln(Y, "Alamak. Boleh saya tinggal satu barang?", "Oh no. Can I leave one item behind?"),
                ln(S, "Takpe lah, tiga ringgit je. Lain kali bayar.", "Never mind, it's only three ringgit. Pay next time."),
                ln(Y, "Betul ke? Terima kasih banyak, kak!", "Really? Thank you so much!"),
            ],
            gist=gist("How is the missing three ringgit settled?", "She lets him pay it next time", "He leaves one item behind", "He pays by card after all", "He borrows it from a friend", why="Takpe lah, tiga ringgit je. Lain kali bayar."),
            listen=[
                c(S, 11521603, "Knows there's no money, and still wants to buy.", "Has plenty of money but won't buy.", "Bought it because it was cheap.", "Didn't know the price before buying."),
                g(Y, 924047, "This shop closes at 9.", "tutup"),
                c(S, 10690011, "He doesn't have very much money.", "He has far too much money.", "He never carries money.", "He lost all his money."),
                d(Y, 10163695, "My money got stolen."),
                l(S, 11518677, "Not like now, when everything is expensive."),
            ],
            read=[
                r("Kurang tiga ringgit. Macam mana?", "Boleh saya tinggal satu barang?", ["Scan sini.", "Mesin rosak."], "Short of money: offer to leave one item."),
                o(Y, 10158826, "Give me back my money."),
                r("Mesin kad rosak. Cash ada?", "Tak cukup. QR boleh?", ["Lain kali bayar.", "Cuba lagi sekali."], "Not enough cash: tak cukup — and ask about QR."),
                o(S, 8653173, "They sell everything here."),
                M,
            ]),
    }))

# ---------------------------------------------------------------- vocab and reply translations
VOCAB = {
 "l01": {"easy": ["berapa", "harga", "mahal", "ringgit", "beli", "yang ni"],
         "medium": ["cari", "anggur", "sekilo", "mahal", "manis", ["rasa", "taste"]],
         "hard": ["masam", ["masak", "ripe"], "ambik", "dua-dua", "rugi", "makin"]},
 "l02": {"easy": ["harga", "mahal", "boleh", "lapan belas", "lima belas", "dua puluh"],
         "medium": ["kasut", "sumpah", "kualiti", "rugi", "kurang", "duit"],
         "hard": ["original", "kedai", ["jual", "sell"], "mampu", "last price", "sebelah"]},
 "l03": {"easy": ["epal", "biji", "berapa", "lagi", "itu je", "lima"],
         "medium": ["bawang", "sekilo", "setengah", "cili", "gula", "rupanya"],
         "hard": ["segar", "pagi tadi", "siang", "sepapan", "plastik", "beg"]},
 "l04": {"easy": ["cari", "baju", "warna", "biru", "saiz", "suka"],
         "medium": ["kasut", "hitam", "putih", "cuba", "muat", "habis"],
         "hard": ["stok", "kot", "jumpa", "cantik", "sesuai", "lain kali"]},
 "l05": {"easy": ["bayar", "semua", "cash", "nah", "berapa", "sila"],
         "medium": ["kad", "baki", "duit pecah", "scan", ["masuk", "go through; enter"], "semua sekali"],
         "hard": ["mesin", "rosak", "terlupa", "cuba", ["tinggal", "leave behind"], "lain kali"]},
}
REPLY_EN = json.loads(open(__file__.replace("build_m06.py", "m06_reply_en.json"), encoding="utf-8").read())
TR = {lid: REPLY_EN for lid in VOCAB}

write_module("m06", "m06-pasar", "Pasar & shops", LESSONS, VOCAB, TR)
