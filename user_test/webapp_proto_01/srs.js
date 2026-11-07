/* srs.js — 復習帳 簡易Spaced Repetition (algo "sm2s-1")。DEV/Trial専用・Production未承認。
   DOM・localStorage・時計に依存しない純関数 + 注入式ストア。UMD(ブラウザ: window.SRS / node: module.exports)。
   規則の正本: docs/research/WEBAPP-UI-REVIEW-SRS-AND-VIEWPORT-01/SRS_DESIGN_01.md + SRS_DESIGN_02.md */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(); else root.SRS = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  var P = {
    algo: 'sm2s-1', schema: 1,
    initEase: 2.5, minEase: 1.3, maxEase: 3.0, maxInterval: 180,
    newGood: 1, newEasy: 4, hardMul: 1.2, easyMul: 1.3, relearnMul: 0.4, relearnHardMul: 0.8, relearnEasyMul: 1.3,
    dEaseAgain: -0.20, dEaseHard: -0.15, dEaseEasy: 0.15,
    againCap: 3,            // 同日Againがこの回数を超えたら翌日へ
    newPerDay: 20, reinsertOffset: 10, historyMax: 100,
    storeKey: 'wut01.review.v1', failKey: 'wut01.review.v1.fail', bakPrefix: 'wut01.review.bak.'
  };
  var GRADES = ['again', 'hard', 'good', 'easy'];
  var STATES = ['new', 'learning', 'review', 'relearning'];

  /* ---------- 日付(JST暦日・0時切替) ---------- */
  function todayJST(nowMs) { return new Date(nowMs + 9 * 3600 * 1000).toISOString().slice(0, 10); }
  function addDays(d, n) { var p = d.split('-'); return new Date(Date.UTC(+p[0], +p[1] - 1, +p[2] + n)).toISOString().slice(0, 10); }
  function daysBetween(a, b) { var f = function (d) { var p = d.split('-'); return Date.UTC(+p[0], +p[1] - 1, +p[2]); }; return Math.round((f(b) - f(a)) / 86400000); }

  /* ---------- キー(M5): slug|level|normEn(en) ---------- */
  function normEn(s) { return String(s || '').toLowerCase().normalize('NFKC').replace(/[^a-z0-9 ]+/g, ' ').replace(/\s+/g, ' ').trim(); }
  function keyOf(slug, level, en) { return slug + '|' + level + '|' + normEn(en); }

  /* ---------- 項目 ---------- */
  function newItem(e, today, nowMs) {   // 控えはidentity用 title/en/level のみ(M6)。新規保存はその日がdue(R4)
    return { key: keyOf(e.slug, e.level, e.en), slug: e.slug, level: e.level, en: e.en, title: e.title || '', savedAt: nowMs || 0,
      state: 'new', due: today, interval: 0, ease: P.initEase, reps: 0, lapses: 0, base: 0, history: [] };
  }
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function clampEase(x) { return Math.round(Math.min(P.maxEase, Math.max(P.minEase, x)) * 100) / 100; }
  function capI(i) { return Math.min(P.maxInterval, Math.max(1, i)); }
  function againsOn(item, day) { var n = 0; item.history.forEach(function (h) { if (h.t === day && h.g === 'again') n++; }); return n; }

  /* 規則表(SRS_DESIGN_02 §2)の生計算。item を変更せず新しい item を返す。単調化guardは schedule 側(SRS_DESIGN_02 §2)。 */
  function scheduleRaw(item, grade, today) {
    if (GRADES.indexOf(grade) < 0) throw new Error('bad grade ' + grade);
    var it = clone(item), s0 = it.state, i0 = it.interval, I = it.interval, n;
    if (s0 === 'new') {
      if (grade === 'again') { it.state = 'learning'; it.interval = 0; it.base = P.newGood; it.due = today; }
      else { it.state = 'review'; it.interval = grade === 'easy' ? P.newEasy : P.newGood; it.due = addDays(today, it.interval); it.reps++; }
      /* 新規はeaseを変えない(R3)。Hard=1日(Good=2日は単調化guard、schedule側) */
    } else if (s0 === 'learning') {
      if (grade === 'again') { it.interval = 0; n = againsOn(it, today) + 1; it.due = n > P.againCap ? addDays(today, 1) : today; }
      else { it.state = 'review'; it.interval = grade === 'easy' ? P.newEasy : (it.base || P.newGood); it.due = addDays(today, it.interval); it.reps++; }
    } else if (s0 === 'relearning') {
      var b = it.base || 1;
      if (grade === 'again') { n = againsOn(it, today) + 1; it.due = n > P.againCap ? addDays(today, 1) : today; it.interval = b; }   // 翌日に回っても base を保持
      else {
        it.interval = capI(grade === 'hard' ? Math.round(b * P.relearnHardMul) : grade === 'easy' ? Math.max(b + 1, Math.round(b * P.relearnEasyMul)) : b);
        it.state = 'review'; it.due = addDays(today, it.interval); it.reps++;
      }
      /* 再学習中もeaseは変えない(R3) */
    } else {   // review
      if (grade === 'again') {
        it.lapses++; it.ease = clampEase(it.ease + P.dEaseAgain); it.base = Math.max(1, Math.round(I * P.relearnMul));
        it.state = 'relearning'; it.interval = it.base; n = againsOn(it, today) + 1; it.due = n > P.againCap ? addDays(today, 1) : today;
      } else {
        if (grade === 'hard') { it.interval = capI(Math.max(1, Math.round(I * P.hardMul))); it.ease = clampEase(it.ease + P.dEaseHard); }
        else if (grade === 'good') { it.interval = capI(Math.max(I + 1, Math.round(I * it.ease))); }
        else { it.interval = capI(Math.max(I + 2, Math.round(I * it.ease * P.easyMul))); it.ease = clampEase(it.ease + P.dEaseEasy); }
        it.due = addDays(today, it.interval); it.reps++;
      }
    }
    it.history.push({ t: today, g: grade, s0: s0, s1: it.state, i0: i0, i1: it.interval });
    if (it.history.length > P.historyMax) it.history = it.history.slice(-P.historyMax);
    return it;
  }
  /* 単調化guard(SRS_DESIGN_02 §2。承認済み原文§4-2「4段階評価に応じて復習タイミングが変わる」): 同一状態・同一入力で計算した候補に対し
     Hard>=1、Good=max(Good,Hard+1)、Easy=max(Easy,Good+1)、Again=同日(従来どおり)。上限maxInterval(180日)に達した場合のみ同値を許容(従来のcap挙動を維持)。
     状態遷移・ease規則・lapses・新規上限は変えない(変えるのは review へ進む評価の interval/due のみ)。決定論。 */
  var RANK = { hard: 0, good: 1, easy: 2 };
  function schedule(item, grade, today) {
    var r = scheduleRaw(item, grade, today);
    if (!(grade in RANK) || r.state !== 'review') return r;
    var iv = 0, k, g, c;
    for (k = 0; k <= RANK[grade]; k++) {
      g = GRADES[k + 1]; c = k === RANK[grade] ? r : scheduleRaw(item, g, today);
      var raw = c.interval, lo = k === 0 ? 1 : iv + 1, hi = P.maxInterval;
      iv = Math.min(hi, Math.max(raw, lo));
    }
    if (iv !== r.interval) { r.interval = iv; r.due = addDays(today, iv); r.history[r.history.length - 1].i1 = iv; }
    return r;
  }
  function preview(item, today) {   // 4ボタンの次回目安
    var o = {};
    GRADES.forEach(function (g) {
      var r = schedule(item, g, today), d = daysBetween(today, r.due);
      o[g] = { due: r.due, days: d, label: d <= 0 ? '今日' : d + '日後' };
    });
    return o;
  }

  /* ---------- 出題キュー(R4) ---------- */
  function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; var t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  function shuffle(arr, rng) { var a = arr.slice(), i, j, t; rng = rng || Math.random; for (i = a.length - 1; i > 0; i--) { j = Math.floor(rng() * (i + 1)); t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function isSameDayAgain(it, today) {
    var h = it.history[it.history.length - 1];
    return (it.state === 'learning' || it.state === 'relearning') && it.due <= today && !!h && h.t === today && h.g === 'again';
  }
  function newStartedToday(items, today) {   // 今日始めた新規件数はhistoryから数える(R4)
    return items.filter(function (it) { return it.history.length && it.history[0].s0 === 'new' && it.history[0].t === today; }).length;
  }
  function buildQueue(items, today, opts) {
    opts = opts || {}; var cap = opts.newPerDay == null ? P.newPerDay : opts.newPerDay, rng = opts.rng || Math.random;
    var again = [], due = [], fresh = [];
    items.forEach(function (it) {
      if (it.state === 'new') { if (it.due <= today) fresh.push(it); }
      else if (it.due <= today) (isSameDayAgain(it, today) ? again : due).push(it);
    });
    due.sort(function (a, b) { return a.due < b.due ? -1 : a.due > b.due ? 1 : 0; });
    var out = [], i = 0, j;
    while (i < due.length) { j = i; while (j < due.length && due[j].due === due[i].due) j++; out = out.concat(shuffle(due.slice(i, j), rng)); i = j; }
    fresh.sort(function (a, b) { return a.savedAt - b.savedAt; });
    var started = newStartedToday(items, today), room = Math.max(0, cap - started), newPick = fresh.slice(0, room);
    return { queue: shuffle(again, rng).concat(out, newPick), counts: { again: again.length, due: due.length, newShown: newPick.length, newDeferred: fresh.length - newPick.length, newStartedToday: started } };
  }
  function reinsertIndex(remainingLen) { return Math.min(P.reinsertOffset, remainingLen); }   // Again後は約10件後(少なければ末尾)

  /* ---------- 孤児・通信失敗(M6) ---------- */
  /* statusOf(item) -> 'ok' | 'orphan'(記事がカタログに無い/保存レベルに項目が無い。別レベル代用禁止) | 'netfail'(通信失敗: このセッションだけ飛ばす) */
  function partitionByStatus(queue, statusOf) {
    var r = { queue: [], orphans: [], skipped: [] };
    queue.forEach(function (it) { var s = statusOf(it); (s === 'ok' ? r.queue : s === 'orphan' ? r.orphans : r.skipped).push(it); });
    return r;
  }

  /* ---------- 旧 wut01.saved 移行(M5) ---------- */
  /* levelsOf(slug, en) -> その表現があるレベル配列(['std','adv']の部分集合)。データで決める。両方ならStd、どちらにも無ければ孤児(Std仮置き。出題時に孤児判定される) */
  function migrateFromSaved(saved, today, levelsOf) {
    var seen = {}, items = [], orphans = 0, dups = 0;
    (saved || []).slice().sort(function (a, b) { return (a && a.at || 0) - (b && b.at || 0); }).forEach(function (x) {
      if (!x || !x.slug || !x.en) return;
      var lv = levelsOf(x.slug, x.en) || [], level = lv.indexOf('std') >= 0 ? 'std' : lv.indexOf('adv') >= 0 ? 'adv' : 'std';
      if (!lv.length) orphans++;
      var it = newItem({ slug: x.slug, level: level, en: x.en, title: x.title }, today, x.at || 0);
      if (seen[it.key]) { dups++; return; }   // 古い方(先に処理した方)を採用
      seen[it.key] = 1; items.push(it);
    });
    return { items: items, orphans: orphans, dups: dups };
  }

  /* ---------- serialize / parse(R5) ---------- */
  function emptyState() { return { schema: P.schema, algo: P.algo, migrated: false, settings: { newPerDay: P.newPerDay }, items: [] }; }
  function serialize(state) { return JSON.stringify(state); }
  function validItem(it) {
    return it && typeof it.key === 'string' && STATES.indexOf(it.state) >= 0 && /^\d{4}-\d{2}-\d{2}$/.test(it.due) && typeof it.interval === 'number' &&
      typeof it.ease === 'number' && Array.isArray(it.history) && it.slug && (it.level === 'std' || it.level === 'adv');
  }
  function parse(raw) {
    var s; try { s = JSON.parse(raw); } catch (e) { return { ok: false, reason: 'json' }; }
    if (!s || typeof s !== 'object' || Array.isArray(s)) return { ok: false, reason: 'shape' };
    if (s.schema !== P.schema) return { ok: false, reason: 'schema' };
    if (s.algo !== P.algo) return { ok: false, reason: 'algo' };
    if (!Array.isArray(s.items) || !s.items.every(validItem)) return { ok: false, reason: 'shape' };
    s.settings = s.settings || { newPerDay: P.newPerDay };
    return { ok: true, state: s };
  }

  /* ---------- ストア(ls は getItem/setItem/removeItem を持つ注入物) ---------- */
  function createStore(ls, opts) {
    opts = opts || {}; var nowFn = opts.now || Date.now;
    function load() {
      var raw = null; try { raw = ls.getItem(P.storeKey); } catch (e) { return { status: 'unavailable' }; }
      var marker = null; try { marker = ls.getItem(P.failKey); } catch (e) { }
      if (raw == null) return marker ? { status: 'failed', marker: marker } : { status: 'absent' };
      var p = parse(raw);
      if (p.ok) return { status: 'ok', state: p.state };
      var bak = P.bakPrefix + nowFn();   // 退避して再移行しない
      try { ls.setItem(bak, raw); ls.setItem(P.failKey, JSON.stringify({ t: nowFn(), reason: p.reason, bak: bak })); ls.removeItem(P.storeKey); } catch (e) { }
      return { status: 'failed', reason: p.reason, bak: bak };
    }
    function write(state) { try { ls.setItem(P.storeKey, serialize(state)); return { ok: true, state: state }; } catch (e) { return { ok: false, reason: 'write' }; } }
    function update(fn) {   // 評価直前に必ず再読込(複数タブ)。書込みは1回のsetItem
      var l = load(); if (l.status === 'failed' || l.status === 'unavailable') return { ok: false, reason: l.status };
      var st = l.status === 'ok' ? clone(l.state) : emptyState(), r = fn(st);
      if (r && r.abort) return { ok: false, reason: r.abort, item: r.item };
      return write(st);
    }
    function state() { var l = load(); return l.status === 'ok' ? l.state : emptyState(); }
    function migrateOnce(saved, today, levelsOf) {
      var l = load(); if (l.status === 'failed' || l.status === 'unavailable') return { ok: false, reason: l.status };
      if (l.status === 'ok' && l.state.migrated) return { ok: true, noop: true };
      var m = migrateFromSaved(saved, today, levelsOf), r = update(function (st) {
        var have = {}; st.items.forEach(function (i) { have[i.key] = 1; });
        m.items.forEach(function (i) { if (!have[i.key]) st.items.push(i); });
        st.migrated = true;
      });
      r.migrated = m; return r;
    }
    function isSaved(slug, level, en) { var k = keyOf(slug, level, en), l = load(); return l.status === 'ok' && l.state.items.some(function (i) { return i.key === k; }); }
    function toggle(slug, level, en, title) {
      var k = keyOf(slug, level, en), now = nowFn(), res = { saved: false };
      var r = update(function (st) {
        var ix = -1; st.items.forEach(function (i, n) { if (i.key === k) ix = n; });
        if (ix >= 0) { st.items.splice(ix, 1); res.saved = false; } else { st.items.push(newItem({ slug: slug, level: level, en: en, title: title }, todayJST(now), now)); res.saved = true; }
      });
      res.ok = r.ok; return res;
    }
    function remove(key) { return update(function (st) { st.items = st.items.filter(function (i) { return i.key !== key; }); }); }
    function removeMany(keys) { var m = {}; keys.forEach(function (k) { m[k] = 1; }); return update(function (st) { st.items = st.items.filter(function (i) { return !m[i.key]; }); }); }
    function clearAll() { var st = emptyState(); st.migrated = true; return write(st); }   // 空stateを書く(keyを消すと旧wut01.savedから再移行されるため)
    function resetAfterFailure() { try { ls.removeItem(P.failKey); } catch (e) { } var st = emptyState(); st.migrated = true; return write(st); }   // 明示操作のみ
    function grade(key, g, expectHistLen) {   // 評価直前に再読込し、他タブで既に評価済みなら conflict
      var now = nowFn(), today = todayJST(now), out = null;
      var r = update(function (st) {
        var it = st.items.filter(function (i) { return i.key === key; })[0];
        if (!it) return { abort: 'missing' };
        if (expectHistLen != null && it.history.length !== expectHistLen) return { abort: 'conflict', item: it };
        var n = schedule(it, g, today); st.items[st.items.indexOf(it)] = n; out = n;
      });
      if (r.ok) r.item = out; return r;
    }
    function attachStorage(win, cb) {   // 他タブの変更通知
      var h = function (e) { if (!e || e.key === P.storeKey || e.key === null) cb(e); };
      win.addEventListener('storage', h); return function () { win.removeEventListener('storage', h); };
    }
    return { load: load, state: state, update: update, migrateOnce: migrateOnce, isSaved: isSaved, toggle: toggle, remove: remove, removeMany: removeMany,
      clearAll: clearAll, resetAfterFailure: resetAfterFailure, grade: grade, attachStorage: attachStorage };
  }

  return { P: P, GRADES: GRADES, STATES: STATES, todayJST: todayJST, addDays: addDays, daysBetween: daysBetween, normEn: normEn, keyOf: keyOf,
    newItem: newItem, schedule: schedule, scheduleRaw: scheduleRaw, preview: preview, againsOn: againsOn, isSameDayAgain: isSameDayAgain, newStartedToday: newStartedToday,
    buildQueue: buildQueue, reinsertIndex: reinsertIndex, partitionByStatus: partitionByStatus, migrateFromSaved: migrateFromSaved,
    emptyState: emptyState, serialize: serialize, parse: parse, createStore: createStore, mulberry32: mulberry32, shuffle: shuffle };
});
