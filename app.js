/* BaMaLe — vanilla JS, no build step. Content lives in /content/*.json. */
'use strict';

/* ---------- helpers ---------- */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const shuffle = (a) => { a = [...a]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const slug = (k) => k.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

const app = $('#app');
const nav = $('#nav');
const LEVELS = ['easy', 'medium', 'hard'];
const SHORT = { easy: 'Easy', medium: 'Med', hard: 'Hard' };
const FULL = { easy: 'Easy', medium: 'Medium', hard: 'Hard' };
const STEPS = ['Listen', 'Read along', 'Phrases', 'Drills', 'Real clip', 'Wrap-up'];
const DAY = 864e5;
const BOXES = [1, 3, 7, 14, 30]; // days

const ICON = {
  pause: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="4" width="4.5" height="16" rx="1"/><rect x="13.5" y="4" width="4.5" height="16" rx="1"/></svg>',
  x: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  star: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l2.7 5.6 6.1.8-4.5 4.3 1.1 6.1L12 16.9 6.6 19.8l1.1-6.1L3.2 9.4l6.1-.8z"/></svg>',
  play: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" aria-hidden="true"><path d="M7 4l13 8-13 8z"/></svg>',
  flag: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 21V4h11l-2 4 2 4H5"/></svg>',
  tick: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5 9-10"/></svg>',
  slow: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
};

/* ---------- progress (localStorage, single key) ---------- */
const KEY = 'bamale.progress';
const S = Object.assign({ v: 1, levels: {}, done: {}, tests: {}, review: {}, flags: {}, clipEdits: {}, days: [], last: null }, (() => {
  try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; }
})());
function save() {
  try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { /* storage full or blocked: carry on in memory */ }
  renderNavCount();
}
const levelOf = (mid) => S.levels[mid] || 'medium';
const dueItems = () => Object.entries(S.review).filter(([, r]) => r.due <= Date.now()).sort((a, b) => a[1].due - b[1].due);

function addReview(item, dueNow) {
  const old = S.review[item.id];
  if (old && !dueNow) return false;
  S.review[item.id] = { ms: item.ms, en: item.en, audio: item.audio, box: 0, due: Date.now() + (dueNow ? 0 : DAY) };
  save();
  return true;
}

/* ---------- content ---------- */
const cache = {};
const getJSON = (p) => (cache[p] = cache[p] || fetch(p).then((r) => { if (!r.ok) throw new Error('Could not load ' + p); return r.json(); }));
let COURSE, GLOSS;
const modMeta = (mid) => COURSE.modules.find((m) => m.id === mid);
const getModule = (mid) => getJSON(`content/${modMeta(mid).dir}/module.json`);
async function getLesson(mid, lid) {
  const mod = await getModule(mid);
  const entry = mod.lessons.find((l) => l.id === lid);
  if (!entry) throw new Error('No such lesson');
  return getJSON(`content/${modMeta(mid).dir}/${entry.file}`);
}
const clipOf = (c) => Object.assign({}, c, S.clipEdits[c.id] || {});

/* ---------- audio ---------- */
const audio = new Audio();
let seq = 0;
let endOne = null; // settles the clip that is playing now
let NOW = null; // the running sequence: { items, i, onEach, tag, paused }
function syncPlayAll() {
  const b = $('.play-all');
  if (!b) return;
  const on = NOW && NOW.tag === 'all';
  b.innerHTML = on ? (NOW.paused ? `${ICON.play} Resume` : `${ICON.pause} Pause`) : `${ICON.play} ${b.dataset.label}`;
  b.classList.toggle('playing', !!on && !NOW.paused);
}
function halt() {
  seq++;
  audio.pause();
  NOW = null;
  if (endOne) endOne(false);
  $$('.playing').forEach((e) => e.classList.remove('playing'));
  syncPlayAll();
}
function playOne(src, el, frac) {
  audio.pause();
  return new Promise((res) => {
    if (el) el.classList.add('playing');
    const fin = (ok) => {
      if (endOne !== fin) return;
      endOne = null;
      audio.onended = audio.onerror = audio.onloadedmetadata = null;
      if (el) el.classList.remove('playing');
      res(ok);
    };
    endOne = fin;
    audio.onended = () => fin(true);
    audio.onerror = () => fin(false);
    audio.onloadedmetadata = frac ? () => { audio.currentTime = frac * audio.duration; } : null;
    audio.src = src;
    audio.play().catch(() => fin(false));
  });
}
/**
 * Play [src, element] pairs in order; a new call or halt() cancels.
 * `src` may be a function, so a speed change mid-play can re-resolve it.
 * `frac` starts the first item part-way through; `tag` 'all' marks a pausable run.
 */
async function play(items, onEach, frac, tag) {
  halt();
  const mine = seq, st = (NOW = { items, i: 0, onEach, tag, paused: false });
  syncPlayAll();
  for (; st.i < items.length; st.i++) {
    const [src, el] = items[st.i];
    const ok = await playOne(typeof src === 'function' ? src() : src, el, st.i === 0 ? frac : 0);
    if (mine !== seq) return;
    if (el && onEach) onEach(el);
    if (!ok) break;
    if (st.i < items.length - 1) {
      await wait(350);
      while (st.paused && mine === seq) await wait(120);
      if (mine !== seq) return;
    }
  }
  if (NOW === st) { NOW = null; syncPlayAll(); }
}
/** The whole-dialogue button: start, then pause / resume while it runs. */
function playAll(makeItems, onEach) {
  if (NOW && NOW.tag === 'all') {
    NOW.paused = !NOW.paused;
    if (NOW.paused) audio.pause();
    else if (endOne) audio.play().catch(() => {});
    syncPlayAll();
    return;
  }
  play(makeItems(), onEach, 0, 'all');
}
/** Speed changed: restart the current line at the new speed, at the same point. */
function respeed() {
  const st = NOW;
  if (!st || !st.items[st.i] || typeof st.items[st.i][0] !== 'function') return;
  const frac = audio.duration ? audio.currentTime / audio.duration : 0;
  play(st.items.slice(st.i), st.onEach, frac, st.tag);
}

/* ---------- glossing ---------- */
const WORD = /[A-Za-z][A-Za-z'\-]*/g;
function glossHTML(text) {
  const parts = [];
  let last = 0, m;
  WORD.lastIndex = 0;
  while ((m = WORD.exec(text))) {
    if (m.index > last) parts.push({ sep: text.slice(last, m.index) });
    parts.push({ w: m[0] });
    last = m.index + m[0].length;
  }
  if (last < text.length) parts.push({ sep: text.slice(last) });
  let out = '', i = 0;
  while (i < parts.length) {
    const p = parts[i];
    if (p.sep !== undefined) { out += esc(p.sep); i++; continue; }
    let hit = false;
    for (let n = 4; n >= 1 && !hit; n--) { // longest multi-word unit first
      const span = parts.slice(i, i + 2 * n - 1);
      if (span.length < 2 * n - 1) continue;
      if (!span.every((q, j) => (j % 2 === 0 ? q.w !== undefined : q.sep === ' '))) continue;
      const key = span.filter((q) => q.w).map((q) => q.w.toLowerCase()).join(' ');
      if (GLOSS[key]) {
        out += `<button type="button" class="w" data-k="${esc(key)}">${esc(span.map((q) => q.w || q.sep).join(''))}</button>`;
        i += 2 * n - 1;
        hit = true;
      }
    }
    if (!hit) { out += esc(p.w); i++; }
  }
  return out;
}
const SES = { level: 'medium', hints: 0 }; // word taps count as hints on hard
document.addEventListener('click', (e) => {
  const playBtn = e.target.closest('.pop-play');
  if (playBtn) { play([[`audio/words/${slug(playBtn.dataset.k)}.mp3`, playBtn]]); return; }
  const w = e.target.closest('.w');
  if (!w) return;
  const host = w.closest('.ms');
  if (!host) return;
  const was = w.classList.contains('on');
  $$('.w.on').forEach((x) => x.classList.remove('on'));
  $$('.pop').forEach((x) => x.remove());
  if (was) return;
  const k = w.dataset.k, g = GLOSS[k];
  w.classList.add('on');
  if (SES.level === 'hard') SES.hints++;
  host.insertAdjacentHTML('afterend', `<div class="pop" role="dialog" aria-label="Word: ${esc(k)}">
    <div class="pop-head"><span class="pop-word">${esc(k)}</span>
      <button type="button" class="pop-play" data-k="${esc(k)}" aria-label="Play ${esc(k)}">${ICON.play}</button></div>
    <span class="pop-en">${esc(g.en)}</span>
    ${g.std ? `<span class="pop-std">Standard form: ${esc(g.std)}</span>` : ''}
    ${g.note ? `<span class="pop-note">${esc(g.note)}</span>` : ''}
  </div>`);
});

/* ---------- answer checking (tolerant of spelling variants) ---------- */
const VARIANT = {
  x: 'tak', tk: 'tak', tidak: 'tak', hendak: 'nak', nk: 'nak', sudah: 'dah', dh: 'dah', sahaja: 'je', saja: 'je', jer: 'je', ja: 'je',
  ok: 'okay', okey: 'okay', oke: 'okay', ya: 'ye', yer: 'ye', sedikit: 'sikit', skit: 'sikit', juga: 'jugak', ambil: 'ambik', bawa: 'bawak',
  dekat: 'kat', ini: 'ni', itu: 'tu', tahu: 'tau', sekejap: 'kejap', jap: 'kejap', selepas: 'lepas', mcm: 'macam', yg: 'yang', dgn: 'dengan',
  haah: 'haah', aah: 'haah', takpa: 'takpe', xpe: 'takpe', takpelah: 'takpe', mi: 'mee', mie: 'mee', paha: 'peha', dal: 'dhal', dhall: 'dhal',
  thanks: 'terima', tapi: 'tapi', tetapi: 'tapi', abang: 'bang', kakak: 'kak', beri: 'bagi', ais: 'ais', ice: 'ais',
};
function norm(text) {
  return text.toLowerCase().replace(/[’']/g, '').replace(/\b(tak|tidak) (pe|apa)\b/g, 'takpe').replace(/\bha ah\b/g, 'haah')
    .replace(/[^a-z0-9\s-]/g, ' ').split(/\s+/).filter(Boolean).map((w) => VARIANT[w] || w);
}
const plainWords = (text) => text.replace(/[^A-Za-z0-9'\-\s]/g, ' ').split(/\s+/).filter(Boolean);
/** Word-by-word grading via longest common subsequence. */
function gradeWords(target, typed) {
  const shown = plainWords(target), a = shown.map((w) => norm(w)[0] || w.toLowerCase()), b = norm(typed);
  const dp = Array.from({ length: a.length + 1 }, () => new Array(b.length + 1).fill(0));
  for (let i = a.length - 1; i >= 0; i--) for (let j = b.length - 1; j >= 0; j--) dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
  const marks = [];
  let i = 0, j = 0, right = 0;
  while (i < a.length) {
    if (j < b.length && a[i] === b[j]) { marks.push([shown[i], true]); right++; i++; j++; }
    else if (j < b.length && dp[i][j + 1] >= dp[i + 1][j]) j++;
    else { marks.push([shown[i], false]); i++; }
  }
  return { marks, right, total: a.length, extra: b.length - right };
}

/* ---------- feature switches, progress, shared bits ---------- */
const REAL = false; // real YouTube clips + clip review: built, switched off until the clips are vetted

const dayKey = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
function touchDay() {
  const t = dayKey(new Date());
  if (!S.days.includes(t)) S.days = S.days.concat(t).slice(-400);
}
function streak() {
  const days = new Set(S.days), d = new Date();
  if (!days.has(dayKey(d))) d.setDate(d.getDate() - 1);
  let n = 0;
  while (days.has(dayKey(d))) { n++; d.setDate(d.getDate() - 1); }
  return n;
}
/** { easy: [done, total], medium: …, hard: … } for one module. */
function levelCounts(mid, mod) {
  const o = {};
  LEVELS.forEach((l) => { o[l] = [mod.lessons.filter((x) => S.done[`${mid}-${x.id}:${l}`]).length, mod.lessons.length]; });
  return o;
}
const levelMeters = (counts) => `<div class="lvls" aria-label="Lessons finished at each difficulty">${LEVELS.map((l) => {
  const [n, t] = counts[l], full = n === t;
  return `<span class="lvl ${full ? 'full' : ''}">${full ? ICON.tick : ''}${FULL[l]} ${full ? 'done' : `${n}/${t}`}</span>`;
}).join('')}</div>`;
const lessonStars = (mid, lid) => `<span class="stars">${LEVELS.map((l) => {
  const on = !!S.done[`${mid}-${lid}:${l}`];
  return `<span class="star ${on ? 'on' : ''}" title="${FULL[l]}: ${on ? 'finished' : 'not yet'}">${ICON.star}<span class="sr">${FULL[l]} ${on ? 'finished' : 'not finished'}</span></span>`;
}).join('')}</span>`;
const crumbs = (parts) => `<nav class="crumbs" aria-label="Breadcrumb">${parts.map(([t, h]) => (h ? `<a href="${h}">${esc(t)}</a>` : `<span aria-current="page">${esc(t)}</span>`)).join('<span aria-hidden="true">›</span>')}</nav>`;
const flagBtn = (on) => `<button type="button" class="flagbtn flag" aria-pressed="${!!on}">${ICON.flag}<span>${on ? 'Flagged' : 'Feels off?'}</span></button>`;
function setFlagBtn(btn, on) { btn.setAttribute('aria-pressed', on); $('span', btn).textContent = on ? 'Flagged' : 'Feels off?'; }

/* ---------- small UI builders ---------- */
function levelSwitch(mid, disabled) {
  const cur = levelOf(mid);
  return `<div class="seg" role="group" aria-label="Difficulty">${LEVELS.map((l) =>
    `<button type="button" data-level="${l}" data-mid="${mid}" aria-pressed="${l === cur}" ${disabled ? 'disabled' : ''}>${SHORT[l]}</button>`).join('')}</div>`;
}
document.addEventListener('click', (e) => {
  const b = e.target.closest('[data-level]');
  if (!b || b.disabled) return;
  S.levels[b.dataset.mid] = b.dataset.level;
  save();
  route();
});
function feedback(el, ok, html) {
  el.insertAdjacentHTML('beforeend', `<div class="fb ${ok ? '' : 'bad'}" role="status"><b class="verdict">${ok ? 'Betul!' : 'Not quite.'}</b>${html || ''}</div>`);
}
/** Multiple choice. `q.options[q.answer]` is correct; options are shuffled on screen. */
function mcq(el, q, done) {
  const order = shuffle(q.options.map((_, i) => i));
  el.insertAdjacentHTML('beforeend', `<div class="opts">${order.map((i) => `<button type="button" class="opt" data-i="${i}">${esc(q.options[i])}</button>`).join('')}</div>`);
  const box = el.lastElementChild;
  box.addEventListener('click', (e) => {
    const b = e.target.closest('.opt');
    if (!b || e.target.closest('.w') || box.dataset.done) return;
    box.dataset.done = '1';
    const ok = +b.dataset.i === q.answer;
    $$('.opt', box).forEach((o) => { o.disabled = true; if (+o.dataset.i === q.answer) o.classList.add('right'); });
    if (!ok) b.classList.add('wrong');
    $$('.pop', box).forEach((x) => x.remove());
    done(ok);
  });
}
function selfCheck(el, q, done) {
  el.insertAdjacentHTML('beforeend', `<div class="row"><button type="button" class="btn" data-ok="1">Yes</button><button type="button" class="btn ghost" data-ok="0">Not yet</button></div>`);
  const box = el.lastElementChild;
  box.addEventListener('click', (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    box.innerHTML = `<span class="pill ${b.dataset.ok === '1' ? '' : 'red'}">${b.dataset.ok === '1' ? 'Got it' : 'Replay it a few times — it gets easier'}</span>`;
    done(b.dataset.ok === '1');
  });
}

/* ---------- nav ---------- */
function renderNavCount() {
  const c = $('#nav .count');
  if (c) { const n = dueItems().length; c.textContent = n; c.hidden = !n; }
}
function setNav(active, lesson) {
  if (lesson) {
    nav.className = 'steps';
    nav.setAttribute('aria-label', 'Lesson steps');
    nav.innerHTML = STEPS.map((s, i) => (i === 4 && !REAL
      ? `<span class="off" aria-disabled="true">${i + 1} ${s} <span class="soon-tag">soon</span></span>`
      : `<a href="#/l/${lesson.mid}/${lesson.lid}/${i}" class="${i === lesson.step ? 'on' : i < lesson.step ? 'done' : ''}" ${i === lesson.step ? 'aria-current="step"' : ''}>${i + 1} ${s}</a>`)).join('');
    return;
  }
  nav.className = '';
  nav.setAttribute('aria-label', 'Main');
  const item = (id, href, label) => `<a href="${href}" class="${active === id ? 'on' : ''}" ${active === id ? 'aria-current="page"' : ''}>${label}</a>`;
  nav.innerHTML = item('course', '#/', 'Home') + item('review', '#/review', 'Review <span class="count" hidden></span>')
    + (REAL ? item('clips', '#/clips', 'Clip review') : '<span class="off" aria-disabled="true">Clip review <span class="soon-tag">soon</span></span>')
    + item('flags', '#/flags', 'Feels off?');
  renderNavCount();
}

/* ---------- YouTube ---------- */
let ytReady;
let ytCleanup = [];
function loadYT() {
  return (ytReady = ytReady || new Promise((res) => {
    if (window.YT && window.YT.Player) return res(window.YT);
    window.onYouTubeIframeAPIReady = () => res(window.YT);
    const s = document.createElement('script');
    s.src = 'https://www.youtube.com/iframe_api';
    s.onerror = () => { ytReady = null; res(null); };
    document.head.appendChild(s);
  }));
}
function killYT() { ytCleanup.forEach((f) => f()); ytCleanup = []; }
/** Mount a cued YouTube segment into `box`. Returns a controller (or null if unavailable). */
async function mountClip(box, clip, sticky) {
  box.innerHTML = `<div class="yt"><div></div></div><p class="fb bad" hidden>Clip unavailable — the video may have been removed or blocked from embedding. The rest of the lesson still works.</p>`;
  const fail = () => { $('.yt', box).hidden = true; $('.fb', box).hidden = false; };
  const YT = await loadYT();
  if (!YT) { fail(); return null; }
  let timer;
  const ctl = {
    start: clip.start, end: clip.end, guard: !!sticky, player: null,
    playSegment() { ctl.guard = true; ctl.player.seekTo(ctl.start, true); ctl.player.playVideo(); },
    now() { return Math.round(ctl.player.getCurrentTime() * 10) / 10; },
  };
  await new Promise((ready) => {
    ctl.player = new YT.Player($('.yt div', box), {
      videoId: clip.yt,
      playerVars: { start: Math.floor(clip.start), rel: 0, playsinline: 1 },
      events: {
        onReady: ready,
        onError: () => { fail(); ready(); },
        onStateChange: (e) => {
          clearInterval(timer);
          if (e.data !== 1) return;
          timer = setInterval(() => {
            if (ctl.guard && ctl.player.getCurrentTime() >= ctl.end) { ctl.player.pauseVideo(); if (!sticky) ctl.guard = false; }
          }, 150);
        },
      },
    });
  });
  ytCleanup.push(() => { clearInterval(timer); try { ctl.player.destroy(); } catch (e) { /* already gone */ } });
  return ctl;
}
/** A confirmed clip with its level-specific questions. */
async function clipBlock(el, clip, level) {
  el.insertAdjacentHTML('beforeend', `<div class="card key"><span class="eyebrow">Real Malay</span><h2>${esc(clip.title || 'Real clip')}</h2>
    <div class="clipbox"></div>
    <div class="row"><button type="button" class="btn red seg-play">${ICON.play} Play the segment</button><span class="small muted">${fmt(clip.start)} – ${fmt(clip.end)}</span></div>
    <p><b>Listen for:</b> ${esc(clip.listenFor || '')}</p><div class="clipqs stack" style="gap:16px"></div></div>`);
  const card = el.lastElementChild;
  const ctl = await mountClip($('.clipbox', card), clip, true);
  $('.seg-play', card).addEventListener('click', () => ctl && ctl.playSegment());
  const qs = (clip.questions && clip.questions[level]) || [];
  for (const q of qs) {
    const wrap = document.createElement('div');
    wrap.className = 'stack';
    wrap.innerHTML = `<p class="q" style="font-size:18px">${esc(q.q)}</p>`;
    $('.clipqs', card).appendChild(wrap);
    if (q.self) selfCheck(wrap, q, () => {});
    else mcq(wrap, q, (ok) => feedback(wrap, ok, q.why ? `<span>${esc(q.why)}</span>` : ''));
  }
}
const fmt = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;

/* ---------- views: home (the course map) ---------- */
async function viewCourse() {
  setNav('course');
  let stars = 0, starTotal = 0;
  const cards = await Promise.all(COURSE.modules.map(async (m) => {
    let prog = 'Not written yet', counts = null;
    const lv = levelOf(m.id);
    if (m.ready) {
      counts = levelCounts(m.id, await getModule(m.id));
      LEVELS.forEach((l) => { stars += counts[l][0]; starTotal += counts[l][1]; });
      prog = `Playing at ${FULL[lv]}`;
    } else if (m.woven) prog = 'Woven through all';
    return `<article class="card mod ${m.ready ? '' : 'soon'}">
      <div class="mod-head"><span class="badge">${m.num}</span><div class="stack" style="gap:0"><span class="eyebrow quiet">Module ${m.num}</span>
        <h2>${m.ready ? `<a href="#/m/${m.id}">${esc(m.title)}</a>` : esc(m.title)}</h2></div></div>
      <p>${esc(m.blurb)}</p>
      ${counts ? levelMeters(counts) : ''}
      <div class="mod-foot"><span class="prog">${prog}</span>${levelSwitch(m.id, !m.ready)}</div>
    </article>`;
  }));
  let cont = S.last;
  if (!cont) {
    const first = COURSE.modules.find((m) => m.ready), mod = await getModule(first.id);
    cont = { href: `#/l/${first.id}/${mod.lessons[0].id}/0`, title: `Module ${first.num} · Lesson 1`, sub: mod.lessons[0].blurb, fresh: true };
  }
  const pct = starTotal ? Math.round((stars / starTotal) * 100) : 0, st = streak();
  app.innerHTML = `<section class="hero-row">
      <div class="stack"><h1 class="hero">Jom, sambung belajar.</h1>
        <p class="lede">Pick any module. Everything is open — set the difficulty per module and change it whenever.</p></div>
      <a class="card key continue" href="${cont.href}"><span class="eyebrow">${cont.fresh ? 'Start here' : 'Continue'}</span>
        <h2>${esc(cont.title)}</h2><span class="muted" style="font-size:15px">${esc(cont.sub)}</span>
        <span class="btn">${cont.fresh ? 'Start' : 'Resume'} →</span></a>
    </section>
    <section class="card progress" aria-label="Your progress">
      <div class="stack meter"><div class="row spread"><span class="eyebrow quiet">Course progress</span><b>${ICON.star} ${stars} of ${starTotal} stars</b></div>
        <div class="bar" role="progressbar" aria-label="Stars earned" aria-valuemin="0" aria-valuemax="${starTotal}" aria-valuenow="${stars}"><span style="width:${pct}%"></span></div>
        <span class="small muted">One star for every lesson you finish, at each difficulty. New modules add more stars.</span></div>
      <div class="stat"><b>${st}</b><span>day streak</span></div>
      <div class="stat"><b>${Object.keys(S.review).length}</b><span>phrases collected</span></div>
      <div class="stat"><b>${dueItems().length}</b><span>due for review</span></div>
    </section>
    <section class="stack"><h2>The course: ${COURSE.modules.length} modules</h2>
      <p class="muted">The <b>course</b> is everything here. A <b>module</b> is one real-life situation, like the mamak. Each module has a handful of short <b>lessons</b> — one dialogue each, worked through in steps — and ends with a <b>finale</b> test. Easy, Med and Hard are three versions of the same lessons.</p></section>
    <section class="grid" aria-label="Modules">${cards.join('')}</section>`;
}

/* ---------- views: module ---------- */
async function viewModule(mid) {
  setNav('course');
  const meta = modMeta(mid);
  if (!meta || !meta.ready) return viewCourse();
  const mod = await getModule(mid), lv = levelOf(mid);
  const test = S.tests[`${mid}:${lv}`];
  app.innerHTML = `<section class="stack">${crumbs([['Home', '#/'], [`Module ${meta.num}: ${meta.title}`]])}
      <span class="eyebrow">Module ${meta.num} of ${COURSE.modules.length}</span>
      <div class="row spread"><h1>${esc(meta.title)}</h1>${levelSwitch(mid)}</div>
      <p class="lede">${esc(meta.blurb)} ${mod.lessons.length} lessons and a finale, in any order.</p>
      ${levelMeters(levelCounts(mid, mod))}</section>
    <section class="lessons">${mod.lessons.map((l, i) => {
      const d = S.done[`${mid}-${l.id}:${lv}`];
      return `<article class="card lesson-row"><span class="badge ${d ? 'done' : ''}">${d ? ICON.tick : i + 1}</span>
        <div class="stack"><span class="eyebrow quiet">Lesson ${i + 1}</span><h2>${esc(l.title)}</h2><p>${esc(l.blurb)}</p></div>
        ${lessonStars(mid, l.id)}
        <a class="btn ${d ? 'ghost' : ''}" href="#/l/${mid}/${l.id}/0" aria-label="${d ? 'Repeat' : 'Start'} lesson ${i + 1}: ${esc(l.title)}">${d ? 'Again' : 'Start'} →</a></article>`;
    }).join('')}
      <article class="card key lesson-row"><span class="badge ${test ? 'done' : ''}">${test ? ICON.tick : ICON.star}</span>
        <div class="stack"><span class="eyebrow quiet">Finale</span><h2>${esc(mod.finale.title)}</h2><p>${esc(mod.finale.blurb)}${test ? ` Best at ${FULL[lv]}: ${test.best}/${test.total}.` : ''}</p></div>
        <a class="btn red" href="#/f/${mid}">Open finale →</a></article>
    </section>`;
}

/* ---------- views: lesson ---------- */
let LS = { key: null };
async function viewLesson(mid, lid, step) {
  const meta = modMeta(mid);
  if (!meta || !meta.ready) return viewCourse();
  const [mod, lesson] = await Promise.all([getModule(mid), getLesson(mid, lid)]);
  const level = levelOf(mid), lv = lesson.levels[level];
  const key = `${lesson.id}:${level}`;
  if (LS.key !== key) { LS = { key, speed: level === 'easy' ? 'slow' : 'normal', auto: false, drill: null, gist: null }; SES.hints = 0; }
  SES.level = level;
  step = Math.max(0, Math.min(STEPS.length - 1, step || 0));
  const num = mod.lessons.findIndex((l) => l.id === lid) + 1;
  S.last = { href: `#/l/${mid}/${lid}/${step}`, title: `Module ${meta.num} · Lesson ${num}`, sub: `${lesson.title} — ${STEPS[step]}` };
  save();
  setNav(null, { mid, lid, step });
  const c = { mid, lid, step, meta, mod, lesson, level, lv, num, key, adir: `audio/${mid}/${lid}` };
  c.src = (id, speed) => `${c.adir}/${id}-${speed || LS.speed}.mp3`;
  c.head = (sub) => `<div class="stack" style="gap:6px"><div class="row spread">${crumbs([['Home', '#/'], [`Module ${meta.num}: ${meta.title}`, `#/m/${mid}`], [`Lesson ${num}`]])}
    <a class="btn ghost exit" href="#/m/${mid}">${ICON.x} Exit lesson</a></div>
    <span class="eyebrow">Lesson ${num} of ${mod.lessons.length} · ${FULL[level]} · Step ${step + 1}: ${STEPS[step]}</span><h1>${esc(lesson.title)}</h1>${sub ? `<p class="muted" style="font-size:15px">${sub}</p>` : ''}</div>`;
  const nx = !REAL && step === 3 ? 5 : step + 1;
  c.next = (cls) => (step < STEPS.length - 1 ? `<a class="btn next ${cls || ''}" href="#/l/${mid}/${lid}/${nx}">Next: ${STEPS[nx]} →</a>` : '');
  [stepListen, stepRead, stepPhrases, stepDrills, stepClip, stepWrap][step](c);
}
const speakerLabel = (c, s) => (s === 'you' ? 'You' : c.lesson.staff.label);
function speedControl() {
  return `<div class="speed" role="group" aria-label="Speed"><button type="button" data-speed="slow" aria-pressed="${LS.speed === 'slow'}">Slow 0.75×</button><button type="button" data-speed="normal" aria-pressed="${LS.speed === 'normal'}">Normal</button></div>`;
}
function bindSpeed(root) {
  root.addEventListener('click', (e) => {
    const b = e.target.closest('[data-speed]');
    if (!b) return;
    LS.speed = b.dataset.speed;
    $$('[data-speed]', root).forEach((x) => x.setAttribute('aria-pressed', x === b));
    respeed();
  });
}

function stepListen(c) {
  const g = c.lv.gist;
  app.innerHTML = `<div class="lesson"><section>
      ${c.head('Listen first — the text stays hidden. Replay as often as you like, then answer.')}
      <div class="card key"><span class="eyebrow quiet">The dialogue · ${c.lv.dialogue.length} lines</span>
        <div class="chips">${c.lv.dialogue.map((l, i) => `<span class="chip ${l.s}" data-i="${i}">${esc(speakerLabel(c, l.s))}</span>`).join('')}</div>
        ${speedControl()}
        <button type="button" class="btn red block play-all" data-label="Play the dialogue">${ICON.play} Play the dialogue</button></div>
      <div class="card gist"><span class="eyebrow quiet">Gist check</span><p class="q">${esc(g.q)}</p></div>
    </section><aside>
      <div class="card note"><span class="eyebrow quiet">Why listen blind?</span><p>The goal is whole sentences at natural speed. Reading first trains your eyes; this trains your ears. Guessing is fine.</p></div>
      ${c.next()}</aside></div>`;
  bindSpeed(app);
  $('.play-all').addEventListener('click', () => playAll(() => {
    $$('.chip').forEach((x) => x.classList.remove('heard'));
    return c.lv.dialogue.map((l, i) => [() => c.src(l.id), $(`.chip[data-i="${i}"]`)]);
  }, (el) => el.classList.add('heard')));
  const box = $('.gist');
  mcq(box, g, (ok) => { LS.gist = ok; feedback(box, ok, `<span>${esc(g.why || '')}</span>`); box.insertAdjacentHTML('beforeend', c.next()); });
}

function stepRead(c) {
  const flagId = (l) => `${c.key}:${l.id}`;
  app.innerHTML = `<div class="lesson"><section>
      ${c.head('Tap any word for its meaning. Translations stay hidden until you ask. If a line sounds wrong in real life, press Feels off? to save it for correction.' + (c.level === 'hard' ? ' On Hard, word taps count as hints.' : ''))}
      <div class="dialogue">${c.lv.dialogue.map((l) => `<div class="line ${l.s}" data-id="${l.id}">
        <span class="avatar">${esc(speakerLabel(c, l.s))}</span>
        <div class="bubble"><p class="ms" lang="ms">${glossHTML(l.ms)}</p><p class="en" hidden>${esc(l.en)}</p>
          <div class="tools"><button type="button" class="iconbtn play-line" aria-label="Play line">${ICON.play}</button>
            <button type="button" class="link reveal" aria-expanded="false">Reveal sentence</button>
            ${flagBtn(S.flags[flagId(l)])}</div>
        </div></div>`).join('')}</div>
    </section><aside>
      <div class="card key"><span class="eyebrow quiet">Audio</span>
        <div class="seg wide" role="group" aria-label="Audio source"><button type="button" aria-pressed="true">Learning voice</button><button type="button" aria-pressed="false" disabled title="Coming soon">Real Malay · soon</button></div>
        ${speedControl()}
        <label class="check"><input type="checkbox" class="auto" ${LS.auto ? 'checked' : ''}> Auto-play next line</label>
        <button type="button" class="btn red block play-all" data-label="Play whole dialogue">${ICON.play} Play whole dialogue</button>
        <span class="small muted">Real Malay clips of real speakers are coming soon.</span></div>
      ${c.lesson.notes.map((n) => `<div class="card note"><span class="eyebrow quiet">Colloquial note · ${esc(n.title)}</span><p>${n.body}</p></div>`).join('')}
      ${c.next()}</aside></div>`;
  bindSpeed(app);
  const lines = c.lv.dialogue, rowOf = (l) => $(`.line[data-id="${l.id}"]`);
  const from = (i, all) => play((all ? lines.slice(i) : [lines[i]]).map((l) => [() => c.src(l.id), rowOf(l)]), null, 0, all ? 'all' : null);
  $('.auto').addEventListener('change', (e) => { LS.auto = e.target.checked; });
  $('.play-all').addEventListener('click', () => playAll(() => lines.map((l) => [() => c.src(l.id), rowOf(l)])));
  $('.dialogue').addEventListener('click', (e) => {
    const row = e.target.closest('.line');
    if (!row) return;
    const i = lines.findIndex((l) => l.id === row.dataset.id), l = lines[i];
    if (e.target.closest('.play-line')) from(i, LS.auto);
    const rv = e.target.closest('.reveal');
    if (rv) { const en = $('.en', row); en.hidden = !en.hidden; rv.textContent = en.hidden ? 'Reveal sentence' : 'Hide'; rv.setAttribute('aria-expanded', !en.hidden); }
    const fl = e.target.closest('.flag');
    if (fl) {
      const id = flagId(l);
      if (S.flags[id]) delete S.flags[id];
      else S.flags[id] = { ms: l.ms, en: l.en, where: `Module ${c.meta.num} · ${c.lesson.title} · ${FULL[c.level]} · line ${l.id}`, at: Date.now() };
      setFlagBtn(fl, !!S.flags[id]);
      save();
    }
  });
}

function stepPhrases(c) {
  app.innerHTML = `<section class="stack" style="gap:18px">${c.head('The phrases worth keeping from this dialogue. Say them out loud after the audio.')}
    <div class="phrases">${c.lv.phrases.map((pid) => { const p = c.lesson.phrases[pid]; return `<article class="card phrase" data-id="${pid}">
      <p class="ms" lang="ms">${glossHTML(p.ms)}</p>
      <div class="row"><button type="button" class="iconbtn" data-sp="normal" aria-label="Play">${ICON.play}</button>
        <button type="button" class="iconbtn" data-sp="slow" aria-label="Play slowly">${ICON.slow}</button>
        <button type="button" class="link show" aria-expanded="false">Show meaning</button>${flagBtn(S.flags[`${c.lesson.id}:${pid}`])}</div>
      <div class="stack more" hidden><p class="en">${esc(p.en)}</p>${p.note ? `<p class="small muted">${esc(p.note)}</p>` : ''}</div></article>`; }).join('')}</div>
    <div class="row" style="justify-content:flex-end">${c.next()}</div></section>`;
  $('.phrases').addEventListener('click', (e) => {
    const card = e.target.closest('.phrase');
    if (!card) return;
    const sp = e.target.closest('[data-sp]');
    if (sp) play([[c.src(card.dataset.id, sp.dataset.sp), sp]]);
    const fl = e.target.closest('.flag');
    if (fl) {
      const pid = card.dataset.id, p = c.lesson.phrases[pid], id = `${c.lesson.id}:${pid}`;
      if (S.flags[id]) delete S.flags[id];
      else S.flags[id] = { ms: p.ms, en: p.en, where: `Module ${c.meta.num} · ${c.lesson.title} · key phrase ${pid}`, at: Date.now() };
      setFlagBtn(fl, !!S.flags[id]);
      save();
    }
    const sh = e.target.closest('.show');
    if (sh) { const m = $('.more', card); m.hidden = !m.hidden; sh.textContent = m.hidden ? 'Show meaning' : 'Hide meaning'; sh.setAttribute('aria-expanded', !m.hidden); }
  });
}

/* ---------- exercises ---------- */
const EX_TITLE = { choose: 'Listen and choose', gap: 'Gap fill by ear', dictation: 'Dictation', ladder: 'Speed ladder', reply: 'What would you say?', order: 'Word order', match: 'Standard vs colloquial' };
/** item = { ex, line, src(speed), level, match, reviewId } ; done(ok) fires once. */
function renderExercise(el, item, done) {
  const { ex, line, level } = item, hard = level === 'hard';
  const listen = () => `<div class="row"><button type="button" class="btn red" data-play="normal">${ICON.play} Play</button>${hard ? '' : `<button type="button" class="btn ghost" data-play="slow">${ICON.slow} Slow</button>`}</div>`;
  const answerLine = () => `<p class="ms" lang="ms">${glossHTML(line.ms)}</p><span class="muted">${esc(line.en)}</span>`;
  el.innerHTML = `<span class="eyebrow quiet">${EX_TITLE[ex.type]}</span>`;
  el.addEventListener('click', (e) => { const b = e.target.closest('[data-play]'); if (b) play([[item.src(b.dataset.play), b]]); });
  const add = (html) => el.insertAdjacentHTML('beforeend', html);

  if (ex.type === 'choose') {
    add(`<p class="q">What does this mean?</p>${listen()}`);
    mcq(el, ex, (ok) => { feedback(el, ok, answerLine()); done(ok); });
  } else if (ex.type === 'reply') {
    add(`<p class="q">What would you say back?</p><div class="line staff"><span class="avatar">${esc(item.staff)}</span><div class="bubble"><p class="ms" lang="ms">${glossHTML(ex.prompt)}</p></div></div>`);
    mcq(el, Object.assign({ gloss: true }, ex), (ok) => { feedback(el, ok, `<span>${esc(ex.why || '')}</span>`); done(ok); });
  } else if (ex.type === 'gap') {
    const re = new RegExp(`\\b${ex.word}\\b`, 'i');
    const [before, after] = line.ms.split(re);
    const hint = hard ? '?' : `${ex.word[0]}${'·'.repeat(ex.word.length - 1)}`;
    add(`<p class="q">Type the missing word.</p>${listen()}<p class="gapline ms" lang="ms">${glossHTML(before)}<span class="blank">${esc(hint)}</span>${glossHTML(after || '')}</p>
      <form class="row"><input class="field" style="max-width:260px" aria-label="Missing word" autocomplete="off" autocapitalize="off" spellcheck="false"><button class="btn">Check</button></form>`);
    $('form', el).addEventListener('submit', (e) => {
      e.preventDefault();
      const v = $('input', el).value;
      if (!v.trim()) return;
      const ok = norm(v).join(' ') === norm(ex.word).join(' ');
      $('form', el).remove();
      feedback(el, ok, `<span>The word is <b>${esc(ex.word)}</b>.</span>${answerLine()}`);
      done(ok);
    });
  } else if (ex.type === 'dictation') {
    add(`<p class="q">Type what you hear.</p>${listen()}<form class="stack"><textarea class="field" aria-label="What you hear" autocomplete="off" autocapitalize="off" spellcheck="false" lang="ms"></textarea>
      <div class="row"><button class="btn">Check</button><span class="small muted">Short forms and their variants are all accepted (tak / x / tidak).</span></div></form>`);
    $('form', el).addEventListener('submit', (e) => {
      e.preventDefault();
      const v = $('textarea', el).value;
      if (!v.trim()) return;
      const g = gradeWords(line.ms, v), ok = g.right === g.total && g.extra <= 1;
      $('form', el).remove();
      feedback(el, ok, `<p class="diff" lang="ms">${g.marks.map(([w, r]) => `<span class="${r ? 'ok' : 'bad'}">${esc(w)}</span>`).join(' ')}</p>
        <span>${g.right} of ${g.total} words${g.extra > 1 ? `, ${g.extra} extra` : ''}. You typed: “${esc(v.trim())}”</span><span class="muted">${esc(line.en)}</span>`);
      done(ok);
    });
  } else if (ex.type === 'ladder') {
    add(`<p class="q">Climb the ladder: slow first, then normal speed.</p>
      <div class="rungs"><button type="button" class="btn ghost" data-play="slow">${ICON.slow} 1 · Slow</button><button type="button" class="btn red" data-play="normal">${ICON.play} 2 · Normal</button></div>
      <p class="muted">When did you understand the whole sentence?</p>
      <div class="row pick"><button type="button" class="btn" data-r="slow">At slow</button><button type="button" class="btn" data-r="normal">At normal speed</button><button type="button" class="btn ghost" data-r="no">Not yet</button></div>`);
    $('.pick', el).addEventListener('click', (e) => {
      const b = e.target.closest('[data-r]');
      if (!b) return;
      const ok = b.dataset.r !== 'no';
      $('.pick', el).remove();
      feedback(el, ok, answerLine() + (b.dataset.r === 'slow' ? '<span>Now replay it at normal speed and follow along.</span>' : ''));
      $('.fb .verdict', el).textContent = ok ? 'Bagus!' : 'It goes into your review queue.';
      done(ok);
    });
  } else if (ex.type === 'order') {
    const words = plainWords(line.ms);
    let pool = shuffle(words.map((w, i) => ({ w, i })));
    if (pool.map((t) => t.w).join(' ') === words.join(' ') && words.length > 1) pool.reverse();
    const picked = [];
    add(`<p class="q">Rebuild the sentence.</p><p class="muted">“${esc(line.en)}”</p>
      <div class="tiles answer" aria-label="Your sentence"></div><div class="tiles pool" aria-label="Word tiles"></div>
      <div class="row"><button type="button" class="btn check" disabled>Check</button></div>`);
    const draw = () => {
      $('.answer', el).innerHTML = picked.map((t) => `<button type="button" class="tile" data-i="${t.i}">${esc(t.w)}</button>`).join('') || '<span class="muted small">Tap the tiles in order</span>';
      $('.pool', el).innerHTML = pool.map((t) => `<button type="button" class="tile" data-i="${t.i}">${esc(t.w)}</button>`).join('');
      $('.check', el).disabled = pool.length > 0;
    };
    const move = (fromArr, toArr, i) => { const k = fromArr.findIndex((t) => t.i === i); if (k >= 0) toArr.push(fromArr.splice(k, 1)[0]); draw(); };
    $('.pool', el).addEventListener('click', (e) => { const b = e.target.closest('.tile'); if (b) move(pool, picked, +b.dataset.i); });
    $('.answer', el).addEventListener('click', (e) => { const b = e.target.closest('.tile'); if (b) move(picked, pool, +b.dataset.i); });
    $('.check', el).addEventListener('click', () => {
      const ok = picked.map((t) => t.w.toLowerCase()).join(' ') === words.map((w) => w.toLowerCase()).join(' ');
      $$('.tiles, .check', el).forEach((x) => x.remove());
      feedback(el, ok, answerLine());
      done(ok);
    });
    draw();
  } else if (ex.type === 'match') {
    const n = { easy: 4, medium: 5, hard: 7 }[level], pairs = item.match.slice(0, n);
    const right = shuffle(pairs.map((p, i) => i));
    let sel = null, slips = 0, left = pairs.length;
    add(`<p class="q">Match each casual form to its standard form.</p>
      <div class="matchgrid">${pairs.map((p, i) => `<button type="button" data-side="a" data-i="${i}" lang="ms">${esc(p[0])}</button><button type="button" data-side="b" data-i="${right[i]}" lang="ms">${esc(pairs[right[i]][1])}</button>`).join('')}</div>`);
    $('.matchgrid', el).addEventListener('click', (e) => {
      const b = e.target.closest('button');
      if (!b || b.classList.contains('locked')) return;
      if (!sel || sel.dataset.side === b.dataset.side) { if (sel) sel.classList.remove('sel'); sel = b; b.classList.add('sel'); return; }
      if (sel.dataset.i === b.dataset.i) {
        [sel, b].forEach((x) => { x.classList.remove('sel'); x.classList.add('locked'); x.disabled = true; });
        sel = null;
        if (--left === 0) { const ok = slips <= 1; feedback(el, ok, `<span>${slips ? `${slips} slip${slips > 1 ? 's' : ''} on the way.` : 'All matched first time.'}</span>`); done(ok); }
      } else {
        slips++;
        const a = sel; sel = null;
        [a, b].forEach((x) => { x.classList.remove('sel'); x.classList.add('shake'); });
        setTimeout(() => [a, b].forEach((x) => x.classList.remove('shake')), 500);
      }
    });
  }
}
/** Run a list of exercise items one at a time inside `host`; calls `finish(state)` at the end. */
function runDrills(host, items, state, finish) {
  const draw = () => {
    if (state.i >= items.length) return finish(state);
    const item = items[state.i];
    host.innerHTML = `<div class="row spread"><span class="eyebrow quiet">Drill ${state.i + 1} of ${items.length}</span>
      <div class="dots" aria-hidden="true">${items.map((_, k) => `<span class="${k < state.i ? (state.results[k] ? 'ok' : 'bad') : k === state.i ? 'cur' : ''}"></span>`).join('')}</div></div>
      <div class="card key ex"></div>`;
    renderExercise($('.ex', host), item, (ok) => {
      state.results[state.i] = ok;
      if (!ok && item.line) addReview({ id: item.reviewId, ms: item.line.ms, en: item.line.en, audio: item.src('normal') }, true);
      $('.ex', host).insertAdjacentHTML('beforeend', `<div class="row" style="justify-content:flex-end"><button type="button" class="btn go">${state.i + 1 < items.length ? 'Next drill' : 'Finish drills'} →</button></div>`);
      const go = $('.go', host);
      go.addEventListener('click', () => { halt(); state.i++; draw(); app.scrollIntoView(); });
      go.focus({ preventScroll: true });
    });
  };
  draw();
}
function drillItems(c, lesson, level, lid) {
  const lv = lesson.levels[level], adir = `audio/${c.mid}/${lid}`;
  return lv.exercises.map((ex) => {
    const line = ex.ref ? lv.dialogue.find((l) => l.id === ex.ref) : null;
    return { ex, line, level, match: lesson.match, staff: lesson.staff.label, reviewId: line ? `${lesson.id}:${level}:${line.id}` : null, src: (sp) => `${adir}/${ex.ref}-${sp}.mp3` };
  });
}
function stepDrills(c) {
  const items = drillItems(c, c.lesson, c.level, c.lid);
  if (!LS.drill) LS.drill = { i: 0, results: [] };
  app.innerHTML = `<section class="stack" style="gap:18px; max-width:760px; width:100%; align-self:center">${c.head()}<div class="stack host" style="gap:14px"></div></section>`;
  runDrills($('.host'), items, LS.drill, (st) => {
    const right = st.results.filter(Boolean).length;
    $('.host').innerHTML = `<div class="card key"><span class="eyebrow">Drills done</span><p class="score">${right}/${items.length}</p>
      <p class="muted">${right === items.length ? 'Clean sweep.' : 'Missed sentences are in your review queue.'}</p>
      <div class="row"><button type="button" class="btn ghost again">Do them again</button>${c.next()}</div></div>`;
    $('.again').addEventListener('click', () => { LS.drill = { i: 0, results: [] }; stepDrills(c); });
  });
}

async function stepClip(c) {
  if (!REAL) {
    app.innerHTML = `<section class="stack" style="gap:18px; max-width:760px; width:100%; align-self:center">${c.head()}
      <div class="card"><span class="eyebrow quiet">Real clip</span><h2>Coming soon</h2><p class="muted">Short clips of real people speaking will appear here in a later version.</p></div>
      <div class="row" style="justify-content:flex-end">${c.next()}</div></section>`;
    return;
  }
  const all = (c.mod.clips || []).map(clipOf).filter((k) => k.use === c.lid);
  const ok = all.filter((k) => k.status === 'confirmed'), waiting = all.filter((k) => k.status === 'candidate').length;
  app.innerHTML = `<section class="stack" style="gap:18px; max-width:860px; width:100%; align-self:center">${c.head('Real speech is faster and messier than the learning voice. Catching a few words is a win.')}
    <div class="stack clips" style="gap:18px"></div><div class="row" style="justify-content:flex-end">${c.next()}</div></section>`;
  const host = $('.clips');
  if (!ok.length) {
    host.innerHTML = `<div class="card"><span class="eyebrow quiet">Real clip</span><h2>No confirmed clip for this lesson yet</h2>
      <p class="muted">${waiting ? `${waiting} candidate clip${waiting > 1 ? 's are' : ' is'} waiting in <a href="#/clips">Clip review</a>. Confirm one there and it appears here.` : 'Nothing suitable has been found yet. The lesson works fine without it.'}</p></div>`;
    return;
  }
  for (const k of ok) await clipBlock(host, k, c.level);
}

function stepWrap(c) {
  const added = c.lv.phrases.filter((pid) => { const p = c.lesson.phrases[pid]; return addReview({ id: `${c.lesson.id}:${pid}`, ms: p.ms, en: p.en, audio: `${c.adir}/${pid}-normal.mp3` }); }).length;
  const d = LS.drill, right = d ? d.results.filter(Boolean).length : null;
  touchDay();
  const firstTime = !S.done[c.key];
  S.done[c.key] = { at: Date.now(), right, total: d ? d.results.length : null, hints: SES.hints };
  save();
  const nextL = c.mod.lessons[c.num];
  app.innerHTML = `<section class="stack" style="gap:18px; max-width:760px; width:100%; align-self:center">${c.head()}
    <div class="card key"><span class="eyebrow">Lesson done · ${FULL[c.level]}</span><h2>Siap! Bagus.</h2>${firstTime ? `<p class="starline">${ICON.star} Star earned for ${FULL[c.level]}</p>` : ''}
      <div class="row">${right !== null ? `<span class="pill">Drills ${right}/${d.results.length}</span>` : '<span class="pill yellow">Drills skipped</span>'}
        ${LS.gist !== null ? `<span class="pill ${LS.gist ? '' : 'red'}">Gist ${LS.gist ? 'right' : 'missed'}</span>` : ''}
        ${c.level === 'hard' ? `<span class="pill yellow">${SES.hints} word hint${SES.hints === 1 ? '' : 's'}</span>` : ''}</div>
      <p>${added ? `${added} phrase${added > 1 ? 's' : ''} joined your review queue; first review is due tomorrow.` : 'These phrases are already in your review queue.'}</p>
      <ul style="margin:0; padding-left:20px">${c.lv.phrases.map((pid) => `<li lang="ms">${esc(c.lesson.phrases[pid].ms)}</li>`).join('')}</ul>
      <div class="row">${nextL ? `<a class="btn" href="#/l/${c.mid}/${nextL.id}/0">Next lesson: ${esc(nextL.title)} →</a>` : `<a class="btn red" href="#/f/${c.mid}">Module finale →</a>`}
        <a class="btn ghost" href="#/m/${c.mid}">Module page</a><a class="btn ghost" href="#/review">Review</a></div></div></section>`;
}

/* ---------- views: finale ---------- */
async function viewFinale(mid) {
  setNav('course');
  const meta = modMeta(mid);
  if (!meta || !meta.ready) return viewCourse();
  const mod = await getModule(mid), level = levelOf(mid);
  SES.level = level;
  const clips = (mod.clips || []).map(clipOf).filter((k) => k.use === 'finale');
  const ok = clips.filter((k) => k.status === 'confirmed');
  const best = S.tests[`${mid}:${level}`];
  app.innerHTML = `<section class="stack" style="gap:18px; max-width:860px; width:100%; align-self:center">
    <div class="stack" style="gap:6px"><div class="row spread">${crumbs([['Home', '#/'], [`Module ${meta.num}: ${meta.title}`, `#/m/${mid}`], ['Finale']])}
      <a class="btn ghost exit" href="#/m/${mid}">${ICON.x} Exit finale</a></div>
      <span class="eyebrow">Module ${meta.num} · Finale · ${FULL[level]}</span><div class="row spread"><h1>${esc(mod.finale.title)}</h1>${levelSwitch(mid)}</div></div>
    <div class="stack clips" style="gap:18px"></div>
    <div class="stack test" style="gap:14px"><div class="card key"><span class="eyebrow">Module test</span><h2>${mod.finale.testSize} questions from all ${mod.lessons.length} lessons</h2>
      <p class="muted">Listening and reading, at ${FULL[level]}. Results are saved but nothing ever locks.${best ? ` Best so far: ${best.best}/${best.total}.` : ''}</p>
      <div class="row"><button type="button" class="btn red start">Start the test</button><a class="btn ghost" href="#/m/${mid}">Back to module</a></div></div></div></section>`;
  const host = $('.clips');
  if (!REAL) host.hidden = true;
  else if (!ok.length) host.innerHTML = `<div class="card"><span class="eyebrow quiet">Real conversation</span><h2>No confirmed finale clip yet</h2><p class="muted">${clips.length ? `A candidate is waiting in <a href="#/clips">Clip review</a>.` : 'None found yet.'} The test below works without it.</p></div>`;
  else for (const k of ok) await clipBlock(host, k, level);
  $('.start').addEventListener('click', async () => {
    const lessons = await Promise.all(mod.lessons.map((l) => getLesson(mid, l.id)));
    let pool = [];
    lessons.forEach((lesson, i) => { pool = pool.concat(drillItems({ mid }, lesson, level, mod.lessons[i].id).filter((it) => ['choose', 'gap', 'dictation', 'reply', 'order'].includes(it.ex.type))); });
    const items = shuffle(pool).slice(0, mod.finale.testSize);
    runDrills($('.test'), items, { i: 0, results: [] }, (st) => {
      const right = st.results.filter(Boolean).length, k = `${mid}:${level}`, old = S.tests[k];
      touchDay();
      S.tests[k] = { best: Math.max(right, old ? old.best : 0), total: items.length, at: Date.now() };
      save();
      $('.test').innerHTML = `<div class="card key"><span class="eyebrow">Test result · ${FULL[level]}</span><p class="score">${right}/${items.length}</p>
        <p class="muted">${right >= items.length * 0.8 ? 'Mantap. Try the next level up, or a new module.' : 'Missed sentences are in your review queue. Come back to it any time.'}</p>
        <div class="row"><a class="btn" href="#/m/${mid}">Module page</a><a class="btn ghost" href="#/review">Review</a></div></div>`;
    });
  });
}

/* ---------- views: review (spaced repetition) ---------- */
function viewReview(practiseAll) {
  setNav('review');
  const all = Object.entries(S.review);
  let queue = (practiseAll ? shuffle(all) : dueItems()).map(([id]) => id);
  const total = queue.length;
  let seen = 0;
  const head = `<section class="stack"><h1>Review</h1><p class="lede">Listen, recall the meaning, then check. Intervals grow 1 → 3 → 7 → 14 → 30 days; a miss starts again.</p></section>`;
  const draw = () => {
    halt();
    if (!queue.length) {
      const next = all.length ? Math.min(...Object.values(S.review).map((r) => r.due)) : null;
      const days = next ? Math.max(0, Math.ceil((next - Date.now()) / DAY)) : 0;
      app.innerHTML = `${head}<div class="card key empty reviewcard"><span class="eyebrow">${total ? 'Session done' : 'Nothing due'}</span>
        <h2>${all.length ? `${Object.keys(S.review).length} items in your queue` : 'Your queue is empty'}</h2>
        <p class="muted">${all.length ? (dueItems().length ? `${dueItems().length} still due.` : `Next one is due ${days <= 1 ? 'within a day' : `in ${days} days`}.`) : 'Finish a lesson and its key phrases land here. Sentences you miss in drills come here too.'}</p>
        <div class="row">${all.length ? '<button type="button" class="btn ghost all">Practise everything anyway</button>' : ''}<a class="btn" href="#/">Home</a></div></div>`;
      const b = $('.all');
      if (b) b.addEventListener('click', () => viewReview(true));
      return;
    }
    const id = queue[0], r = S.review[id];
    app.innerHTML = `${head}<div class="card key reviewcard"><div class="row spread"><span class="eyebrow quiet">${seen + 1} of ${Math.max(total, seen + queue.length)}</span><span class="pill">Interval: ${BOXES[r.box]} day${BOXES[r.box] > 1 ? 's' : ''}</span></div>
      <button type="button" class="iconbtn big-play" aria-label="Play">${ICON.play}</button>
      <p class="muted" style="text-align:center">What does it mean?</p>
      <div class="stack answer" hidden><p class="ms" lang="ms" style="text-align:center">${glossHTML(r.ms)}</p><p class="en" style="text-align:center">${esc(r.en)}</p></div>
      <div class="row" style="justify-content:center"><button type="button" class="btn show">Show answer</button>
        <button type="button" class="btn ghost miss" hidden>Missed it</button><button type="button" class="btn got" hidden>Got it</button></div></div>`;
    const sayIt = () => play([[r.audio, $('.big-play')]]);
    $('.big-play').addEventListener('click', sayIt);
    $('.show').addEventListener('click', () => { $('.answer').hidden = false; $('.show').hidden = true; $('.miss').hidden = $('.got').hidden = false; $('.got').focus(); });
    const grade = (ok) => {
      queue.shift(); seen++; touchDay();
      if (ok) { r.box = Math.min(r.box + 1, BOXES.length - 1); r.due = Date.now() + BOXES[r.box] * DAY; }
      else { r.box = 0; r.due = Date.now() + DAY; queue.push(id); }
      save();
      draw();
    };
    $('.got').addEventListener('click', () => grade(true));
    $('.miss').addEventListener('click', () => grade(false));
    sayIt();
  };
  draw();
}

/* ---------- views: Feels off? ---------- */
function viewFlags() {
  setNav('flags');
  const items = Object.entries(S.flags).sort((a, b) => b[1].at - a[1].at);
  const text = items.map(([id, f]) => `${id}\n  ms: ${f.ms}\n  en: ${f.en}\n  note: ${f.note || ''}`).join('\n\n');
  app.innerHTML = `<section class="stack"><h1>Feels off?</h1><p class="lede">Lines you flagged because they sounded wrong in real life. Add a note, then copy the list back to Claude for correction.</p></section>
    ${items.length ? `<section class="list">${items.map(([id, f]) => `<article class="card" data-id="${esc(id)}"><div class="stack"><p class="ms" lang="ms">${esc(f.ms)}</p><p class="muted">${esc(f.en)}</p><span class="small muted">${esc(f.where)}</span>
        <input class="field note" style="font-size:15px; margin-top:6px" placeholder="What did you hear instead? (optional)" aria-label="Note for this line" value="${esc(f.note || '')}"></div>
        <button type="button" class="btn ghost unflag">Remove flag</button></article>`).join('')}</section>
      <section class="card"><span class="eyebrow quiet">Copy for correction</span><textarea class="field out" readonly aria-label="Flagged lines">${esc(text)}</textarea>
        <div class="row"><button type="button" class="btn copy">Copy list</button></div></section>`
    : `<div class="card empty"><h2>Nothing flagged</h2><p class="muted">In any lesson's Read along step, tap the flag on a line that feels off. It will be listed here.</p></div>`}`;
  app.onchange = (e) => { const n = e.target.closest('.note'); if (n) { S.flags[n.closest('[data-id]').dataset.id].note = n.value; save(); viewFlags(); } };
  $$('.unflag').forEach((b) => b.addEventListener('click', () => { delete S.flags[b.closest('[data-id]').dataset.id]; save(); viewFlags(); }));
  const cp = $('.copy');
  if (cp) cp.addEventListener('click', () => copyOut(cp));
}
function copyOut(btn) {
  const ta = $('.out');
  ta.select();
  (navigator.clipboard ? navigator.clipboard.writeText(ta.value) : Promise.reject()).catch(() => document.execCommand('copy')).finally(() => { btn.textContent = 'Copied'; setTimeout(() => (btn.textContent = 'Copy list'), 1500); });
}

/* ---------- views: clip review ---------- */
async function viewClips() {
  setNav('clips');
  if (!REAL) {
    app.innerHTML = `<section class="stack"><h1>Clip review</h1></section><div class="card empty"><h2>Coming soon</h2><p class="muted">Real YouTube clips, and this page for checking them, are switched off for now.</p><a class="btn" href="#/">Home</a></div>`;
    return;
  }
  const mods = COURSE.modules.filter((m) => m.ready);
  const groups = await Promise.all(mods.map(async (m) => ({ m, clips: (await getModule(m.id)).clips || [] })));
  const flat = groups.flatMap((g) => g.clips.map((c) => ({ m: g.m, base: c })));
  const output = () => JSON.stringify(flat.map(({ base }) => { const k = clipOf(base); delete k.timesVerified; return k; }), null, 2);
  app.innerHTML = `<section class="stack"><h1>Clip review</h1><p class="lede">Candidate YouTube clips proposed for each module. Play each one, set the start and end of the useful segment, then confirm or reject. Confirmed clips show up in lessons in this browser straight away; paste the list below back to Claude to make it permanent.</p></section>
    <section class="cliplist">${flat.map(({ m, base }) => { const k = clipOf(base); return `<article class="card" data-id="${k.id}">
      <div class="row spread"><span class="eyebrow">Module ${m.num} · ${k.use === 'finale' ? 'Finale' : 'Lesson ' + k.use.replace(/\D+0?/, '')}</span><span class="pill st"></span></div>
      <h3>${esc(k.title)}</h3><p class="small muted"><b>Listen for:</b> ${esc(k.listenFor || '')}${base.timesVerified === false ? ' <b>Times are placeholders — set them here.</b>' : ''}</p>
      <div class="clipbox"><button type="button" class="btn ghost load">Load player</button></div>
      <div class="clipform"><label>Start (s)<input type="number" class="in-start" min="0" step="0.5" value="${k.start}"></label>
        <label>End (s)<input type="number" class="in-end" min="0" step="0.5" value="${k.end}"></label>
        <label>Status<select class="in-status">${['candidate', 'confirmed', 'rejected'].map((s) => `<option ${s === k.status ? 'selected' : ''}>${s}</option>`).join('')}</select></label></div>
      <div class="row"><button type="button" class="btn ghost set-start" disabled>Start = now</button><button type="button" class="btn ghost set-end" disabled>End = now</button><button type="button" class="btn red play-seg" disabled>${ICON.play} Play segment</button></div>
    </article>`; }).join('') || '<div class="card empty"><h2>No clips proposed yet</h2></div>'}</section>
    <section class="card"><span class="eyebrow quiet">Corrected clip list</span><p class="small muted">Updates as you edit. Paste it back to Claude to write into the content files.</p>
      <textarea class="field out" readonly aria-label="Corrected clip list"></textarea><div class="row"><button type="button" class="btn copy">Copy list</button><button type="button" class="btn ghost reset">Discard my edits</button></div></section>`;
  const ctls = {};
  const refresh = () => {
    $('.out').value = output();
    $$('.cliplist [data-id]').forEach((card) => { const k = clipOf(flat.find((f) => f.base.id === card.dataset.id).base), p = $('.st', card); p.textContent = k.status; p.className = `pill st ${k.status === 'rejected' ? 'red' : k.status === 'candidate' ? 'yellow' : ''}`; });
  };
  const edit = (card) => {
    const id = card.dataset.id, start = +$('.in-start', card).value || 0, end = Math.max(start + 1, +$('.in-end', card).value || 0);
    S.clipEdits[id] = { start, end, status: $('.in-status', card).value };
    if (ctls[id]) { ctls[id].start = start; ctls[id].end = end; }
    save();
    refresh();
  };
  $('.cliplist').addEventListener('change', (e) => { const card = e.target.closest('[data-id]'); if (card) edit(card); });
  $('.cliplist').addEventListener('click', async (e) => {
    const card = e.target.closest('[data-id]');
    if (!card) return;
    const id = card.dataset.id, ctl = ctls[id];
    if (e.target.closest('.load')) {
      ctls[id] = await mountClip($('.clipbox', card), clipOf(flat.find((f) => f.base.id === id).base), false);
      if (ctls[id]) $$('.set-start, .set-end, .play-seg', card).forEach((b) => (b.disabled = false));
    } else if (!ctl) return;
    else if (e.target.closest('.set-start')) { $('.in-start', card).value = ctl.now(); edit(card); }
    else if (e.target.closest('.set-end')) { $('.in-end', card).value = ctl.now(); edit(card); }
    else if (e.target.closest('.play-seg')) ctl.playSegment();
  });
  $('.copy').addEventListener('click', () => copyOut($('.copy')));
  $('.reset').addEventListener('click', () => { S.clipEdits = {}; save(); viewClips(); });
  refresh();
}

/* ---------- router ---------- */
async function route() {
  halt();
  killYT();
  app.onchange = null;
  const h = location.hash.replace(/^#\/?/, '').split('/');
  try {
    if (h[0] === 'm') await viewModule(h[1]);
    else if (h[0] === 'l') await viewLesson(h[1], h[2], +h[3]);
    else if (h[0] === 'f') await viewFinale(h[1]);
    else if (h[0] === 'review') viewReview();
    else if (h[0] === 'clips') await viewClips();
    else if (h[0] === 'flags') viewFlags();
    else await viewCourse();
  } catch (err) {
    console.error(err);
    app.innerHTML = `<div class="card empty"><h2>Something didn't load</h2><p class="muted">${esc(err.message)}. If you opened the file directly, serve the folder instead: <code>python3 -m http.server</code>.</p><a class="btn" href="#/">Course map</a></div>`;
  }
  window.scrollTo(0, 0);
}
window.addEventListener('hashchange', route);
(async () => {
  try {
    [COURSE, GLOSS] = await Promise.all([getJSON('content/course.json'), getJSON('content/glossary.json')]);
    route();
  } catch (err) {
    app.innerHTML = `<div class="card empty"><h2>Content didn't load</h2><p class="muted">${esc(err.message)}. Serve the folder with <code>python3 -m http.server</code> rather than opening the file directly.</p></div>`;
  }
})();
