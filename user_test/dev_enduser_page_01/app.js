/* END-USER-LISTENING-PAGE-PROTOTYPE-01 DEV試作(静的・外部ライブラリなし)。
   データ: data/<article>.json (docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/tools/build_data_01.py が公開済み/候補ページから生成)。
   音声: 既存mp3を相対パスで参照(コピー・再生成なし)。
   文単位ハイライトのフック: 各文は <span class="sent" data-sid="...">、同期データ(sentences:[{sid,start,end}], 全編内の秒)を
   data/sync_index.json 経由(または ?sync=dummy の確認用ダミー)で読み込む。 */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var A = $('aud'), Q = new URLSearchParams(location.search);
  var art = null, lv = null, L = null, parts = [];
  var mode = 'full', curIdx = null;               // 'full'(通し) / 'part'(segment)
  var sync = [], syncKind = 'none', sentEls = {}, activeSid = null;
  var raf = 0, lastUserScroll = 0, syncIndex = null;
  var LEVEL_NAME = { std: 'Standard', adv: 'Advanced' };
  var JA = /[ぁ-んァ-ヶ一-龠]/;

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]; }); }
  function fmt(t) { t = Math.max(0, t || 0); var m = Math.floor(t / 60), s = Math.floor(t % 60); return m + ':' + (s < 10 ? '0' : '') + s; }
  function audioUrl(p) { return new URL(art.audio_base + p, location.href).href; }
  function fetchJson(u) { return fetch(u).then(function (r) { if (!r.ok) throw new Error(u + ' (' + r.status + ')'); return r.json(); }); }

  /* ---------- 描画 ---------- */
  function sentHtml(p) {
    return (p.paragraphs || []).map(function (para) {
      var ja = JA.test(para.map(function (s) { return s.text; }).join(''));
      var inner = para.map(function (s) { return '<span class="sent" data-sid="' + s.sid + '">' + s.html + '</span>'; }).join(ja ? '' : ' ');
      return '<p class="script' + (ja ? '' : '') + '" lang="' + (ja ? 'ja' : 'en') + '">' + inner + '</p>';
    }).join('');
  }
  function btns(p) {
    return '<span class="btns"><button type="button" class="seek part" data-act="part" data-i="' + p.idx + '" aria-label="' + esc(p.label) + ' を再生">▶ このパート</button>' +
           '<button type="button" class="seek" data-act="full" data-i="' + p.idx + '" aria-label="通しでここから再生">通しで ▶</button></span>';
  }
  function card(title, body, opts) {
    opts = opts || {};
    return '<section class="card"' + (opts.part != null ? ' data-part="' + opts.part + '"' : '') + (opts.id ? ' id="' + opts.id + '"' : '') + '>' +
      (opts.label ? '<span class="label">' + esc(opts.label) + '</span>' : '') +
      '<div class="sectionhead"><h2>' + esc(title) + '</h2>' + (opts.btn || '') + '</div>' + body + '</section>';
  }
  function render() {
    var by = function (k) { return parts.filter(function (p) { return p.kind === k; }); };
    var out = '';
    var intro = by('topic').concat(by('jtitle'));
    if (intro.length) {
      out += card('Intro', intro.map(function (p) {
        var ja = p.kind === 'jtitle';
        return '<div class="subblk" data-part="' + p.idx + '"><div class="sectionhead"><span class="note">' + (ja ? '日本語タイトル' : 'Topic') + '</span>' + btns(p) + '</div>' +
               (ja ? '<div class="jp">' + sentHtml(p) + '</div>' : sentHtml(p)) + '</div>';
      }).join(''), { label: 'INTRO' });
    }
    by('preview').forEach(function (p) {
      var ja = JA.test(p.paragraphs.map(function (x) { return x.map(function (s) { return s.text; }).join(''); }).join(''));
      out += card('Preview', ja ? '<div class="jp">' + sentHtml(p) + '</div>' : sentHtml(p), { part: p.idx, btn: btns(p) });
    });
    var kps = by('kp');
    if (kps.length) {
      var hdr = kps[0].kp_header || ['英語', '意味'];
      var body = '<div class="kp">' + kps.map(function (p) {
        return p.kp.map(function (k) {
          return '<div class="kpitem" data-part="' + p.idx + '"><div><span class="th">' + esc(hdr[0]) + '</span><b>' + esc(k.en) + '</b></div>' +
                 '<div class="def"><span class="th">' + esc(hdr[1] || '') + '</span>' + esc(k.text) + '</div>' +
                 '<button type="button" class="seek part" data-act="part" data-i="' + p.idx + '" aria-label="' + esc(k.en) + ' の音声を再生">▶ 音声</button></div>';
        }).join('');
      }).join('') + '</div><p class="note" style="margin-top:10px">Full Storyの本文中では、下線付きで表示されます。</p>';
      out += card('Key Phrases', body, { label: 'KEY PHRASES' });
    }
    var full = parts.filter(function (p) { return p.kind === 'comment' || p.kind === 'story'; });
    if (full.length) {
      var hasLk = full.some(function (p) { return (p.meanings && p.meanings.length) || /class="lk\d"/.test(JSON.stringify(p.paragraphs)); });
      var b = hasLk ? '<p class="legend">本文の下線: <strong class="lk1">太字+二重下線</strong> = 重要表現 / <strong class="lk2">太字+下線</strong> = 追加の解説つき表現 / <span class="lk3">下線のみ</span> = 意味を下の一覧で確認</p>' : '';
      b += full.map(function (p) {
        if (p.kind === 'comment') {
          var ja = JA.test(p.paragraphs.map(function (x) { return x.map(function (s) { return s.text; }).join(''); }).join(''));
          return '<div class="comment" data-part="' + p.idx + '"><div class="ch"><strong>' + esc(p.label) + '</strong>' + btns(p) + '</div>' + sentHtml(p) + '</div>';
        }
        var m = (p.meanings || []).length ? '<ul class="meanings">' + p.meanings.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' : '';
        return '<div class="partblock" data-part="' + p.idx + '"><div class="ph"><b>' + esc(p.label) + '</b>' + btns(p) + '</div>' + sentHtml(p) + m + '</div>';
      }).join('');
      out += card('Full Story', b, { label: 'FULL STORY', id: 'fullstory' });
    }
    by('oneline').forEach(function (p) { out += card('In One Line', sentHtml(p), { part: p.idx, btn: btns(p), label: 'IN ONE LINE' }); });
    if (L.vocab && L.vocab.length) {
      var wide = window.matchMedia('(min-width: 700px)').matches;
      out += card('Vocabulary & Expressions', L.vocab.map(function (it) {
        var mean = (it.fields.filter(function (f) { return f.label === '本文中の意味'; })[0] || {}).html || '';
        return '<details class="vi"' + (wide ? ' open' : '') + '><summary>' + esc(it.heading) + '<span>' + mean + '</span></summary><dl>' +
          it.fields.map(function (f) { return '<dt>' + esc(f.label) + '</dt><dd>' + f.html + '</dd>'; }).join('') + '</dl></details>';
      }).join(''), { label: 'WORDS', id: 'vocab' });
    }
    if (L.grammar && L.grammar.length) {   // 採用0件ならコーナーごと非表示
      out += card('Grammar & Sentence Structure', L.grammar.map(function (it) {
        return '<div class="gr"><dl style="margin:0">' + it.fields.map(function (f) { return '<dt style="font-size:12px;font-weight:700;color:var(--accent);margin-top:10px">' + esc(f.label) + '</dt><dd style="margin:2px 0 0">' + f.html + '</dd>'; }).join('') + '</dl></div>';
      }).join(''), { label: 'GRAMMAR', id: 'grammar' });
    }
    $('content').innerHTML = out;
    sentEls = {};
    Array.prototype.forEach.call(document.querySelectorAll('[data-sid]'), function (e) { sentEls[e.dataset.sid] = e; });
  }

  /* ---------- 再生 ---------- */
  function ensureSrc(url) { if (A.src !== url) { A.src = url; A.load(); } }
  function withMeta(fn) { if (A.readyState >= 1) fn(); else A.addEventListener('loadedmetadata', function h() { A.removeEventListener('loadedmetadata', h); fn(); }); }
  function playNow() { var pr = A.play(); if (pr && pr.catch) pr.catch(function (e) { if (e.name !== 'AbortError') console.warn('play()', e.name); }); }
  function playFull(at) { mode = 'full'; curIdx = null; ensureSrc(audioUrl(L.main)); withMeta(function () { if (at != null) A.currentTime = at; playNow(); }); labels(); }
  function playPart(i) { mode = 'part'; curIdx = i; ensureSrc(audioUrl(parts[i].seg)); withMeta(function () { A.currentTime = 0; playNow(); }); labels(); }
  function dur() {
    var d = mode === 'part' && curIdx != null ? parts[curIdx].dur : L.total_sec;
    return (isFinite(A.duration) && A.duration > 0 && A.readyState >= 1) ? A.duration : d;
  }
  function gt() { return (mode === 'part' && curIdx != null ? parts[curIdx].start : 0) + (A.currentTime || 0); }
  function labels() {
    var pi = currentPartIdx();
    $('nowLabel').textContent = (mode === 'part' && curIdx != null) ? ('パート再生: ' + parts[curIdx].label) : ('全体' + (pi != null && A.currentTime > 0 && parts[pi].kind !== 'sfx' && parts[pi].kind !== 'fixed' ? ' · ' + parts[pi].label : ''));
  }
  function currentPartIdx() {
    if (mode === 'part') return curIdx;
    var g = gt(), r = null;
    for (var i = 0; i < parts.length; i++) { if (g >= parts[i].start - 0.001) r = i; else break; }
    return r;
  }
  function highlight(sid) {
    if (sid === activeSid) return;
    if (activeSid && sentEls[activeSid]) sentEls[activeSid].classList.remove('on');
    activeSid = sid;
    if (sid && sentEls[sid]) {
      var el = sentEls[sid]; el.classList.add('on');
      if (!A.paused && Date.now() - lastUserScroll > 3500) {
        var r = el.getBoundingClientRect(), barTop = $('bar').getBoundingClientRect().top;
        if (r.top < 70 || r.bottom > barTop - 16) el.scrollIntoView({ block: 'center', behavior: 'smooth' });
      }
    }
  }
  function findActive(g) {
    var lo = 0, hi = sync.length - 1, k = -1;
    while (lo <= hi) { var m = (lo + hi) >> 1; if (sync[m].start <= g) { k = m; lo = m + 1; } else hi = m - 1; }
    if (k >= 0 && g < sync[k].end) return sync[k].sid;
    return null;                                  // 文と文の間・長い無音・終了後は強調なし
  }
  function tick() {
    var d = dur(), c = A.currentTime || 0;
    $('seek').value = d ? Math.min(1000, Math.round(c / d * 1000)) : 0; $('tCur').textContent = fmt(c);
    $('tTot').textContent = fmt(d);
    $('pp').textContent = A.paused ? '▶' : '⏸'; $('pp').setAttribute('aria-label', A.paused ? '再生' : '一時停止');
    labels();
    var pi = currentPartIdx();
    Array.prototype.forEach.call(document.querySelectorAll('[data-part].now'), function (e) { if (Number(e.dataset.part) !== pi || (A.paused && A.currentTime === 0)) e.classList.remove('now'); });
    if (pi != null && !(A.paused && A.currentTime === 0)) Array.prototype.forEach.call(document.querySelectorAll('[data-part="' + pi + '"]'), function (e) { e.classList.add('now'); });
    if (sync.length) highlight(findActive(gt()));
    window.__EUP = { mode: mode, curIdx: curIdx, gt: gt(), active: activeSid, paused: A.paused, level: lv, article: art && art.id, syncKind: syncKind, src: A.src };
  }
  function loop() { tick(); raf = A.paused ? 0 : requestAnimationFrame(loop); }
  function kick() { if (!raf) raf = requestAnimationFrame(loop); }

  /* ---------- 同期データ(文単位ハイライトのフック) ---------- */
  function norm(j) {
    var a = Array.isArray(j) ? j : (j.sentences || []);
    return a.map(function (s) { return { sid: s.sid, start: Number(s.start != null ? s.start : s.start_sec), end: Number(s.end != null ? s.end : s.end_sec) }; })
            .filter(function (s) { return s.sid && isFinite(s.start) && isFinite(s.end); }).sort(function (x, y) { return x.start - y.start; });
  }
  function loadSync() {
    sync = []; syncKind = 'none'; highlight(null);
    var m = Q.get('sync'), url = null, kind = 'none';
    var done = function () {
      $('syncState').textContent = { none: 'ハイライト: 同期データなし(委任_02で統合)', dummy: 'ハイライト: ダミー同期(確認用・精度未検証)', real: 'ハイライト: 同期データ使用' }[syncKind];
      tick();
    };
    if (m === 'dummy') { url = 'data/sync_dummy_' + art.id + '_' + lv + '.json'; kind = 'dummy'; }
    else if (m !== 'off') {
      var p = syncIndex ? Promise.resolve(syncIndex) : fetchJson('data/sync_index.json').then(function (j) { syncIndex = j; return j; }).catch(function () { syncIndex = {}; return {}; });
      return p.then(function (idx) {
        var f = idx[art.id] && idx[art.id][lv];
        if (!f) { done(); return; }
        return fetchJson('data/' + f).then(function (j) { sync = norm(j); syncKind = 'real'; done(); }).catch(function (e) { console.warn(e); done(); });
      });
    }
    if (!url) { done(); return Promise.resolve(); }
    return fetchJson(url).then(function (j) { sync = norm(j); syncKind = kind; done(); }).catch(function (e) { console.warn(e); done(); });
  }

  /* ---------- レベル切替・初期化 ---------- */
  function setLevel(next) {
    lv = next; L = art.levels[lv]; parts = L.parts;
    A.pause(); mode = 'full'; curIdx = null; activeSid = null;
    ensureSrc(audioUrl(L.main));
    $('eyebrow').textContent = 'English Your Way · ' + LEVEL_NAME[lv];
    $('playAll').textContent = '▶ 全体を再生(' + fmt(L.total_sec) + ')';
    Array.prototype.forEach.call($('tabs').children, function (b) { b.setAttribute('aria-selected', b.dataset.lv === lv ? 'true' : 'false'); });
    document.title = '【DEV試作】' + art.title_ja + '｜' + LEVEL_NAME[lv];
    var u = new URL(location.href); u.searchParams.set('a', art.id); u.searchParams.set('lv', lv); history.replaceState(null, '', u);
    render(); labels(); loadSync();
  }
  function init(aid) {
    fetchJson('data/' + aid + '.json').then(function (j) {
      art = j;
      $('devArticle').value = aid;
      $('jaTitle').textContent = art.title_ja; $('enTitle').textContent = art.topic_en;
      $('tabs').innerHTML = Object.keys(art.levels).map(function (k) { return '<button type="button" role="tab" data-lv="' + k + '">' + LEVEL_NAME[k] + '</button>'; }).join('');
      var want = Q.get('lv'); setLevel(art.levels[want] ? want : Object.keys(art.levels)[0]);
    }).catch(function (e) { $('content').innerHTML = '<div class="error"><strong>表示エラー</strong><br>' + esc(e.message) + '</div>'; });
  }

  /* ---------- イベント ---------- */
  $('content').addEventListener('click', function (e) {
    var b = e.target.closest('button[data-act]'); if (!b) return;
    var i = Number(b.dataset.i);
    if (b.dataset.act === 'part') playPart(i); else playFull(parts[i].start);
  });
  $('tabs').addEventListener('click', function (e) { var b = e.target.closest('button[data-lv]'); if (b && b.dataset.lv !== lv) setLevel(b.dataset.lv); });
  $('playAll').addEventListener('click', function () { playFull(0); window.scrollTo({ top: 0, behavior: 'smooth' }); });
  $('devArticle').addEventListener('change', function () { var u = new URL(location.href); u.searchParams.set('a', this.value); u.searchParams.delete('lv'); location.href = u.href; });
  $('pp').addEventListener('click', function () { if (A.paused) { if (!A.src) playFull(0); else playNow(); } else A.pause(); });
  $('back10').addEventListener('click', function () { A.currentTime = Math.max(0, A.currentTime - 10); tick(); });
  $('fwd10').addEventListener('click', function () { A.currentTime = Math.min(dur() - 0.05, A.currentTime + 10); tick(); });
  $('seek').addEventListener('input', function () { A.currentTime = Math.min(dur() - 0.05, this.value / 1000 * dur()); tick(); });
  ['play', 'playing'].forEach(function (ev) { A.addEventListener(ev, kick); });
  ['pause', 'seeked', 'timeupdate', 'loadedmetadata', 'durationchange'].forEach(function (ev) { A.addEventListener(ev, tick); });
  A.addEventListener('ended', function () { tick(); });
  A.addEventListener('error', function () { console.warn('audio error', A.error && A.error.code, A.src); });
  ['wheel', 'touchmove'].forEach(function (ev) { window.addEventListener(ev, function () { lastUserScroll = Date.now(); }, { passive: true }); });

  init(Q.get('a') === 'moon' ? 'moon' : 'ai_island');
})();
