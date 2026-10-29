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
  var mode = 'full', curIdx = null, kpEnd = null;   // 'full'(全体音声) / 'kp'(Key Phrase英語区間のみ)
  var sync = [], syncKind = 'none', sentEls = {}, activeSid = null;
  var raf = 0, lastUserScroll = 0, syncIndex = null;
  var LEVEL_NAME = { std: 'Standard', adv: 'Advanced' };
  var JA = /[ぁ-んァ-ヶ一-龠]/;

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]; }); }
  function fmt(t) { t = Math.max(0, t || 0); var m = Math.floor(t / 60), s = Math.floor(t % 60); return m + ':' + (s < 10 ? '0' : '') + s; }
  function audioUrl(p) { return new URL(art.audio_base + p, location.href).href; }
  var BUILD = (document.querySelector('meta[name=build-id]') || {}).content || '';
  function fetchJson(u) { return fetch(u + (u.indexOf('?') < 0 ? '?v=' + BUILD : '')).then(function (r) { if (!r.ok) throw new Error(u + ' (' + r.status + ')'); return r.json(); }); }

  /* ---------- 描画 ---------- */
  function sentHtml(p) {
    return (p.paragraphs || []).map(function (para) {
      var ja = JA.test(para.map(function (s) { return s.text; }).join(''));
      var inner = para.map(function (s) { return '<span class="sent" data-sid="' + s.sid + '">' + s.html + '</span>'; }).join(ja ? '' : ' ');
      return '<p class="script' + (ja ? '' : '') + '" lang="' + (ja ? 'ja' : 'en') + '">' + inner + '</p>';
    }).join('');
  }
  function btns(p) {
    return '<span class="btns"><button type="button" class="seek from" data-act="full" data-i="' + p.idx + '" aria-label="' + esc(p.label) + ' から再生">▶ ここから再生</button><button type="button" class="seek stop" data-act="stop" data-i="' + p.idx + '" aria-label="再生を停止">■ 停止</button></span>';
  }
  function trHtml(p) {   // 英語本文の直後に日本語訳(承認済み日本語原稿の対応段落 / DEV訳(未承認))
    if (!p.ja || !p.ja.length) return '';
    var dev = p.ja_source === 'dev_translation_unapproved';
    return '<div class="tr" lang="ja" data-src="' + esc(p.ja_source) + '"><span class="trtag">日本語訳' + (dev ? '<em>(DEV訳・未承認)</em>' : '') + '</span>' +
      p.ja.map(function (t) { return '<p>' + esc(t) + '</p>'; }).join('') + '</div>';
  }
  function glossHtml(p) {   // 本文直下の意味一覧(下線対象 + Key Phrase/Word + Vocabulary。簡潔な日本語の意味のみ)
    if (!p.glossary || !p.glossary.length) return '';
    return '<div class="gloss" data-gloss="' + p.idx + '"><div class="gh">覚えておきたい表現</div><ul>' + p.glossary.map(function (g) {
      return '<li><span class="ge">' + esc(g.en) + '</span><span class="gj">' + esc(g.ja) + '</span>' +
        (g.vi != null ? '<a class="glink" href="#vi-' + lv + '-' + g.vi + '" data-vi="' + g.vi + '">解説</a>' : '') + '</li>';
    }).join('') + '</ul></div>';
  }
  function card(title, body, opts) {
    opts = opts || {};
    return '<section class="card' + (opts.cls ? ' ' + opts.cls : '') + '"' + (opts.part != null ? ' data-part="' + opts.part + '"' : '') + (opts.id ? ' id="' + opts.id + '"' : '') + '>' +
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
                 '<button type="button" class="seek part" data-act="kp" data-i="' + p.idx + '" aria-label="' + esc(k.en) + ' の英語音声を再生">▶ 英語音声</button></div>';
        }).join('');
      }).join('') + '</div><p class="note" style="margin-top:10px">Full Storyの本文中では、下線付きで表示されます。</p>';
      out += card('Key Phrases', body, { label: 'KEY PHRASES' });
    }
    var full = parts.filter(function (p) { return p.kind === 'comment' || p.kind === 'story'; });
    if (full.length) {
      // Full Story と In One Line は1つの連続したまとまり(同一カード内。Comment 4 の直後に In One Line)
      var b = full.map(function (p) {
        if (p.kind === 'comment') {
          return '<div class="comment" data-part="' + p.idx + '"><div class="ch"><strong>' + esc(p.label) + '</strong>' + btns(p) + '</div>' + sentHtml(p) + trHtml(p) + '</div>';
        }
        return '<div class="partblock" data-part="' + p.idx + '"><div class="ph"><b>' + esc(p.label) + '</b>' + btns(p) + '</div>' + sentHtml(p) + glossHtml(p) + trHtml(p) + '</div>';
      }).join('');
      by('oneline').forEach(function (p) {
        b += '<div class="partblock oneline" data-part="' + p.idx + '"><div class="ph"><h3>In One Line</h3>' + btns(p) + '</div>' + sentHtml(p) + glossHtml(p) + trHtml(p) + '</div>';
      });
      out += card('Full Story', b, { label: 'FULL STORY', id: 'fullstory' });
    }
    if (L.vocab && L.vocab.length) {
      var wide = window.matchMedia('(min-width: 700px)').matches;
      out += card('Vocabulary & Expressions', L.vocab.map(function (it, vi) {
        var mean = (it.fields.filter(function (f) { return f.label === '本文中の意味'; })[0] || {}).html || '';
        return '<details class="vi" id="vi-' + lv + '-' + vi + '"' + (wide ? ' open' : '') + '><summary><b class="vh">' + esc(it.heading) + '</b><span class="vm">' + mean + '</span></summary><dl>' +
          it.fields.map(function (f) { return '<dt>' + esc(f.label) + '</dt><dd>' + f.html + '</dd>'; }).join('') + '</dl></details>';
      }).join(''), { label: 'WORDS', id: 'vocab', cls: 'blk-vocab' });
    }
    if (L.grammar && L.grammar.length) {   // 採用0件ならコーナーごと非表示
      var ph = L.grammar_source === 'placeholder_for_layout_check';   // rev01-c: 表示確認用の仮データ(DEVページのみ・本文と内容は無関係)
      out += card('Grammar & Sentence Structure', (ph ? '<div class="phnote" data-grammar-source="placeholder_for_layout_check">【仮データ・表示確認用】他記事(月のしわ Advanced)の文法解説を流用しています。記事本文とは内容が対応しません。レイアウト・文字サイズ確認専用で、正式な文法解説ではありません。</div>' : '') + L.grammar.map(function (it) {
        return '<div class="gr"><dl>' + it.fields.map(function (f) { return '<dt>' + esc(f.label) + '</dt><dd>' + f.html + '</dd>'; }).join('') + '</dl></div>';
      }).join(''), { label: ph ? 'GRAMMAR(仮)' : 'GRAMMAR', id: 'grammar', cls: 'blk-grammar' });
    }
    if (L.nuance && L.nuance.length) {   // rev01-d: ニュアンス解説(DEV仮表示。採用0件ならコーナーごと非表示)
      var nph = L.nuance_source === 'placeholder_for_layout_check';
      out += card('ニュアンス解説', (nph ? '<div class="phnote" data-nuance-source="placeholder_for_layout_check">【仮データ・表示確認用】他記事のニュアンス解説を流用。記事本文とは内容が対応しません。</div>' : '') + L.nuance.map(function (it) {
        return '<div class="gr"><h4 class="nh">' + esc(it.heading) + '</h4><dl>' + it.fields.map(function (f) { return '<dt>' + esc(f.label) + '</dt><dd>' + f.html + '</dd>'; }).join('') + '</dl></div>';
      }).join(''), { label: nph ? 'NUANCE(仮)' : 'NUANCE', id: 'nuance', cls: 'blk-nuance' });
    }
    $('content').innerHTML = out;
    sentEls = {};
    Array.prototype.forEach.call(document.querySelectorAll('[data-sid]'), function (e) { sentEls[e.dataset.sid] = e; });
  }

  /* ---------- 再生 ---------- */
  function ensureSrc(url) { if (A.src !== url) { A.src = url; A.load(); } }
  function withMeta(fn) { if (A.readyState >= 1) fn(); else A.addEventListener('loadedmetadata', function h() { A.removeEventListener('loadedmetadata', h); fn(); }); }
  function playNow() { var pr = A.play(); if (pr && pr.catch) pr.catch(function (e) { if (e.name !== 'AbortError') console.warn('play()', e.name); }); }
  function playFull(at) { mode = 'full'; curIdx = null; kpEnd = null; ensureSrc(audioUrl(L.main)); withMeta(function () { if (at != null) A.currentTime = at; playNow(); }); labels(); }
  /* Key Phrase の発音: 既存KP区間mp3(番号→英語→日本語の意味(Advは英語解説)→英語再掲)のうち、最初の英語発話の区間だけを再生し、終端で停止(音声ファイルは不変) */
  function playKp(i, k) {
    var kk = parts[i].kp[k || 0], ea = kk && kk.en_audio; if (!ea) return;
    mode = 'kp'; curIdx = i; kpEnd = ea.end; ensureSrc(audioUrl(parts[i].seg));
    withMeta(function () { A.currentTime = ea.start; playNow(); }); labels();
  }
  function endKp() {   // 英語区間の終端: 停止して通し再生の状態へ戻す(意味・再掲は再生されない)
    var i = curIdx; A.pause(); mode = 'full'; kpEnd = null; curIdx = null;
    ensureSrc(audioUrl(L.main)); withMeta(function () { A.currentTime = parts[i].start; tick(); });
  }
  function dur() {
    var d = mode === 'kp' && curIdx != null ? parts[curIdx].dur : L.total_sec;
    return (isFinite(A.duration) && A.duration > 0 && A.readyState >= 1) ? A.duration : d;
  }
  function gt() { return (mode === 'kp' && curIdx != null ? parts[curIdx].start : 0) + (A.currentTime || 0); }
  function labels() {
    var pi = currentPartIdx();
    $('nowLabel').textContent = (mode === 'kp' && curIdx != null) ? ('英語音声: ' + parts[curIdx].label) : ('全体' + (pi != null && A.currentTime > 0 && parts[pi].kind !== 'sfx' && parts[pi].kind !== 'fixed' ? ' · ' + parts[pi].label : ''));
  }
  function currentPartIdx() {
    if (mode === 'kp') return curIdx;
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
    if (mode === 'kp' && kpEnd != null && !A.paused && (A.currentTime || 0) >= kpEnd) { endKp(); return; }
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
  function seekSentence(sid) {   // 文クリック: その文の先頭から全体音声を再生
    var r = sync.filter(function (x) { return x.sid === sid; })[0]; if (!r) return;
    playFull(r.start);
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
      $('syncState').textContent = { none: 'ハイライト: OFF(同期データなし/?sync=off)', dummy: 'ハイライト: ダミー同期(確認用・精度未検証)', real: 'ハイライト: 実同期(ASR+無音スナップ・聴感未確認)' }[syncKind];
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
    A.pause(); mode = 'full'; curIdx = null; kpEnd = null; activeSid = null;
    ensureSrc(audioUrl(L.main));
    $('eyebrow').textContent = 'English Your Way · ' + LEVEL_NAME[lv];
    $('playAll').textContent = '▶ 全体を再生(' + fmt(L.total_sec) + ')';
    Array.prototype.forEach.call($('tabs').children, function (b) { b.setAttribute('aria-selected', b.dataset.lv === lv ? 'true' : 'false'); });
    document.title = '[DEV] ' + art.title_ja + '｜' + LEVEL_NAME[lv];
    var u = new URL(location.href); u.searchParams.set('a', art.id); u.searchParams.set('lv', lv); history.replaceState(null, '', u);
    render(); labels(); loadSync();
  }
  function init(aid) {
    fetchJson('data/' + aid + '.json').then(function (j) {
      art = j;
      $('jaTitle').textContent = art.title_ja; $('enTitle').textContent = art.topic_en;
      $('tabs').innerHTML = Object.keys(art.levels).map(function (k) { return '<button type="button" role="tab" data-lv="' + k + '">' + LEVEL_NAME[k] + '</button>'; }).join('');
      var want = Q.get('lv'); setLevel(art.levels[want] ? want : Object.keys(art.levels)[0]);
    }).catch(function (e) { $('content').innerHTML = '<div class="error"><strong>表示エラー</strong><br>' + esc(e.message) + '</div>'; });
  }

  /* ---------- イベント ---------- */
  $('content').addEventListener('click', function (e) {
    var se = e.target.closest('.sent');
    if (se && !e.target.closest('button') && syncKind !== 'none') { seekSentence(se.dataset.sid); return; }
    var gl = e.target.closest('a.glink');
    if (gl) {   // 意味一覧の「解説」: 該当表現の解説(Vocabulary項目)へ直接移動し、開く
      e.preventDefault();
      var t = $('vi-' + lv + '-' + gl.dataset.vi);
      if (t) { t.open = true; t.scrollIntoView({ block: 'start', behavior: 'smooth' }); t.classList.add('flash'); setTimeout(function () { t.classList.remove('flash'); }, 2200); }
      return;
    }
    var b = e.target.closest('button[data-act]'); if (!b) return;
    if (b.dataset.act === 'stop') { A.pause(); tick(); return; }   // rev01-c: 停止(連続再生中も)。位置は保持し、固定バー/ここから再生で再開
    var i = Number(b.dataset.i);
    if (b.dataset.act === 'kp') playKp(i, 0); else playFull(parts[i].start);
  });
  $('tabs').addEventListener('click', function (e) { var b = e.target.closest('button[data-lv]'); if (b && b.dataset.lv !== lv) setLevel(b.dataset.lv); });
  $('playAll').addEventListener('click', function () { playFull(0); window.scrollTo({ top: 0, behavior: 'smooth' }); });
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
