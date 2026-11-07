/* eigo-radio WebApp UI 試作(WUT 委任_02a、Trial専用・静的・依存なし)。
   データは ../<slug>/enduser/data/{article.json,sync_*.json} と 既存mp3 を「読取専用・相対参照」で使う(複製0)。
   正式採用前の試作。仮データ(ジャンル/概要/新着順/学習記録/復習帳)は画面に「仮」と表示する。 */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var A = $('aud');
  var LV = { std: 'Standard', adv: 'Advanced' };
  var CAPON = true;   // ECUI B(REF承継): 日本語字幕(dockの日本語キャプチャ)。既定ON。設定=端末保存(wut01.caption)、URL ?caption=0 はそのrouteの間だけ上書き
  var LV_HINT = { std: 'TOEIC 800点未満／英検2級程度を目安', adv: 'TOEIC 800点以上／英検準1級以上を目安' };   // 原文§4-4(ユーザー決定)
  var RATES = [0.5, 0.8, 0.9, 1, 1.1, 1.2];   // 原文§1-2: 6種(1.5倍以上は不要)
  function normRate(v) {   // 保存済みの旧値(0.75/1.25/1.5等)は最も近い許容値へ丸める(0.75→0.8, 1.25→1.2, 1.5→1.2)。数値でなければ1.0
    v = Number(v); if (!isFinite(v) || v <= 0) return 1;
    return RATES.reduce(function (b, r) { return Math.abs(r - v) < Math.abs(b - v) - 1e-9 ? r : b; }, RATES[0]);
  }
  var SKIP = 10;   // 既存End Userと同じ±10秒(H-4)
  var K_LEVEL = 'wut01.level', K_TUT = 'wut01.tutorial_done', K_SAVED = 'wut01.saved', K_STATS = 'wut01.stats', K_RATE = 'wut01.rate', K_CAP = 'wut01.caption';
  var QS = new URLSearchParams(location.search);
  /* WUR S5: 復習帳ストア(srs.js)。localStorageのみ(§7: 永続ストレージ/同期/本格SRSはユーザー判断事項)。 */
  var LSX = (function () { try { var l = window.localStorage; l.getItem('wut01.__probe'); return l; } catch (e) { return { getItem: function () { throw new Error('unavailable'); }, setItem: function () { throw new Error('unavailable'); }, removeItem: function () { throw new Error('unavailable'); } }; } })();
  var store = SRS.createStore(LSX);
  var reviewCtl = null;

  /* ---------- storage ---------- */
  function lsGet(k, d) { try { var v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } }
  function lsSet(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode等 */ } }

  var ST = { level: lsGet(K_LEVEL, 'std') === 'adv' ? 'adv' : 'std', mode: 'listen', rate: normRate(lsGet(K_RATE, 1)), sel: null, cat: null, warn: [] };
  var cur = null;          // 再生中: {slug, level, queue[], qi, label}
  var ART = {};            // slug -> {art, sha, sync:{std,adv}, jaBy:{std,adv}}
  var JG = {};             // 承継実装3: sid -> 訳本文の群キー(idx:g)。聴く画面の「日本語訳(全文)」の群単位点灯に使う(REF承継)
  var ARTP = {};
  var audioSid = null, manual = null, activePh = null, capSid = null, hlViol = 0, sentEls = {}, lastUserScroll = 0, tutOn = false;   // WUR 02c: 状態=audioSid(音声追従の文)+manual(手動選択{sid,wordEl,at})の2変数。描画は renderActive() のみ

  /* ---------- util ---------- */
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]; }); }
  function fmt(t) { t = Math.max(0, t || 0); var m = Math.floor(t / 60), s = Math.floor(t % 60); return m + ':' + (s < 10 ? '0' : '') + s; }
  function item(slug) { return ST.cat.items.filter(function (x) { return x.slug === slug; })[0]; }
  function fetchJson(u) { return fetch(u).then(function (r) { if (!r.ok) throw new Error(u + ' (' + r.status + ')'); return r.json(); }); }
  /* ECUI B(承継実装1): player系の真値(音声URL・総尺・同期)は article.json / sync_*.json。catalogは一覧表示用(カード分数・検索)のみ。
     例外: カード等のクリック内で同期的に src設定+play() する必要がある(iOS)ため、記事が未取得の瞬間だけ catalog の値で暫定再生し、取得完了後に reconcileAudio() が article の値へ差し替える。 */
  function lvInfo(slug, lv) {
    var d = ART[slug], L = d && d.art && d.art.levels && d.art.levels[lv];
    if (L && L.main) return { main: L.main, total: +L.total_sec || 0, src: 'article' };
    var it = item(slug), c = it && it.levels && it.levels[lv];
    return c ? { main: c.main, total: +c.total_sec || 0, src: 'catalog' } : null;
  }
  function lvTotal(slug, lv) { var i = lvInfo(slug, lv); return i ? i.total : 0; }
  function stripQ(u) { return String(u || '').split('#')[0].split('?')[0]; }
  function audioUrl(slug, lv) {
    var d = ART[slug], L = d && d.art && d.art.levels && d.art.levels[lv];
    if (L && L.main) {
      var eu = new URL('../' + slug + '/enduser/', location.href), u = new URL(L.main, new URL(d.art.audio_base || '../', eu));
      if (d.sha) u.search = '?v=' + d.sha;   // 承継実装5: CDN新旧混在防止(任意)
      return u.href;
    }
    var i = lvInfo(slug, lv); return new URL('../' + slug + '/' + (i ? i.main : ''), location.href).href;
  }
  function shuffle(a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  var IC = {
    play: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>',
    pause: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>',
    bars3: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="13" width="4" height="7" rx="1"/><rect x="10" y="9" width="4" height="11" rx="1"/><rect x="16" y="5" width="4" height="15" rx="1"/></svg>',
    bars4: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="14" width="3.5" height="6" rx="1"/><rect x="7.5" y="10" width="3.5" height="10" rx="1"/><rect x="13" y="7" width="3.5" height="13" rx="1"/><rect x="18.5" y="3" width="3.5" height="17" rx="1"/></svg>'
  };
  var LOGO = '<svg viewBox="0 0 32 32" aria-hidden="true"><g fill="#1d4fd8"><rect x="3" y="12" width="3" height="8" rx="1.5"/><rect x="9" y="7" width="3" height="18" rx="1.5"/><rect x="15" y="3" width="3" height="26" rx="1.5"/><rect x="21" y="8" width="3" height="16" rx="1.5"/><rect x="27" y="13" width="3" height="6" rx="1.5"/></g></svg>';
  function toast(msg, ms) { var t = $('toast'); t.textContent = msg; t.hidden = false; clearTimeout(toast._t); toast._t = setTimeout(function () { t.hidden = true; }, ms || 4200); }

  /* ---------- サムネ(画像が無い記事は代替グラデ) ---------- */
  function thumbUrl(it) {   // ECUI C-DEV2: サムネは catalog_auto の article.thumbnail(公開dir enduser/ の画像)。無ければ代替グラデ(プレースホルダ)
    var t = it && it.thumbnail; if (!t || !t.file) return '';
    return new URL('../' + it.slug + '/enduser/' + t.file + (t.sha256 ? '?v=' + String(t.sha256).slice(0, 12) : ''), location.href).href;
  }
  function thumbHtml(it, dur) {
    var h = 0; for (var i = 0; i < it.slug.length; i++) h = (h * 31 + it.slug.charCodeAt(i)) % 360;
    h = 205 + (h % 40);
    var u = thumbUrl(it);
    return '<div class="thumb" style="background:linear-gradient(135deg,hsl(' + h + ',72%,48%),hsl(' + (h + 14) + ',68%,20%))"><span class="fam">' + esc(it.family) + '</span><span class="k">仮</span>' +
      (u ? '<img src="' + u + '" alt="" loading="lazy" style="position:absolute;inset:0">' : '') +
      (dur ? '<span class="dur">' + Math.round(it.levels[ST.level].total_sec / 60) + '分</span>' : '') + '</div>';
  }
  document.addEventListener('error', function (e) { var t = e.target; if (t && t.tagName === 'IMG' && t.closest('.thumb')) t.remove(); }, true);

  /* ---------- 学習記録(仮集計: 再生秒を端末内へ加算) ---------- */
  function dayKey(d) { d = d || new Date(); return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate(); }
  var statAcc = 0, lastTickMs = 0;
  function statTick() {
    var n = Date.now();
    if (!A.paused && lastTickMs) { var dt = Math.min(1.2, (n - lastTickMs) / 1000); statAcc += dt; }
    lastTickMs = A.paused ? 0 : n;
    if (statAcc >= 5) statFlush();
  }
  function statFlush() {
    if (statAcc <= 0) return;
    var s = lsGet(K_STATS, { days: {} }); var k = dayKey(); s.days[k] = (s.days[k] || 0) + statAcc; statAcc = 0; lsSet(K_STATS, s);
  }
  function statsView() {
    statFlush();
    var s = lsGet(K_STATS, { days: {} }), d = s.days, now = new Date(), streak = 0, i, dt;
    for (i = 0; i < 400; i++) { dt = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i); if ((d[dayKey(dt)] || 0) > 0) streak++; else if (i > 0) break; }
    var dow = (now.getDay() + 6) % 7, week = 0, tot = 0, k;
    for (i = 0; i <= dow; i++) { dt = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i); week += d[dayKey(dt)] || 0; }
    for (k in d) tot += d[k];
    var tm = tot / 60;
    return { streak: streak, week: Math.round(week / 60), total: tm >= 60 ? { v: (tm / 60).toFixed(1), u: '時間' } : { v: Math.round(tm), u: '分' } };
  }

  /* ---------- 記事データ ---------- */
  function shaHex(buf) {   // 承継実装5: article.json の sha256(取得できない環境では空=?v=なし)
    if (!(window.crypto && crypto.subtle)) return Promise.resolve('');
    return crypto.subtle.digest('SHA-256', buf).then(function (h) { return Array.prototype.map.call(new Uint8Array(h), function (b) { return ('0' + b.toString(16)).slice(-2); }).join(''); }, function () { return ''; });
  }
  function ensureArt(slug) {   // 真値は article.json。sync_*.json は article の sha を ?v= に付けて取得(CDNの新旧混在防止)
    if (ARTP[slug]) return ARTP[slug];
    var base = '../' + slug + '/enduser/data/', it = item(slug);
    ARTP[slug] = fetch(base + 'article.json').then(function (r) { if (!r.ok) throw new Error('article.json ' + r.status); return r.arrayBuffer(); }).then(function (buf) {
      return shaHex(buf).then(function (hex) {
        var q = hex ? '?v=' + hex : '';
        return Promise.all([fetchJson(base + 'sync_std.json' + q), fetchJson(base + 'sync_adv.json' + q)]).then(function (sy) {
          var art = JSON.parse(new TextDecoder('utf-8').decode(buf));
          var d = { art: art, sha: hex, sync: { std: normSync(sy[0]), adv: normSync(sy[1]) }, jaBy: { std: jaIndex(art.levels.std), adv: jaIndex(art.levels.adv) } };
          ART[slug] = d;
          if (hex && it && it.article_sha256 && hex !== it.article_sha256) { ST.warn.push(slug); toast('元データが更新されています(' + slug + ')。同期のずれに注意'); }   // 既存: catalog取込時から更新されていないか(更新時は警告。表示・再生はarticle値で継続)
          return d;
        });
      });
    }).catch(function (e) { delete ARTP[slug]; throw e; });   // WUR 02e: 失敗を恒久キャッシュしない(中断された取得の後でも再試行できる)
    return ARTP[slug];
  }
  function normSync(j) { return (j.sentences || []).map(function (s) { return { sid: s.sid, start: +s.start, end: +s.end }; }).sort(function (a, b) { return a.start - b.start; }); }
  function jaIndex(L) {   // ja_align(既存)があるパートだけ、英文sid→対応する日本語を引けるようにする。無ければ英文のみ
    var by = {};
    L.parts.forEach(function (p) {
      (p.ja_align || []).forEach(function (g) {
        if (!g.ja || !p.ja || p.ja[g.ja[0]] == null) return;
        var txt = p.ja[g.ja[0]].substring(g.ja[1], g.ja[2]);
        (g.sids || []).forEach(function (s) { by[s] = txt; });
      });
    });
    return by;
  }

  /* ---------- 再生位置(A-8: レベル別に独立して端末内保存。他レベルへ転送しない=旧P1/P3写像は廃止) ---------- */
  var K_POS = 'wul01a.pos';
  var lastPosSave = 0, follow = true, units = [], activeUnit = null, PWI = [];
  function posKey(slug, lv) { return slug + '|' + lv; }
  function savedPos(slug, lv) {
    var t = Number((lsGet(K_POS, {}) || {})[posKey(slug, lv)]) || 0, tot = lvTotal(slug, lv);
    return (t > 1 && (!tot || t < tot - 3)) ? t : 0;
  }
  function savePos(slug, lv, t) { var m = lsGet(K_POS, {}) || {}; m[posKey(slug, lv)] = Math.max(0, Math.round(t * 10) / 10); lsSet(K_POS, m); }
  function persistPos(force) {   // 読込完了済みの現在音声だけ保存(src切替直後の0秒を誤って保存しない)
    if (!cur || !cur.loaded || A.seeking) return;
    var n = Date.now(); if (!force && n - lastPosSave < 1500) return; lastPosSave = n;
    savePos(cur.slug, cur.level, A.currentTime || 0);
  }

  /* ---------- 再生 ---------- */
  function playNow() { var p = A.play(); if (p && p.catch) p.catch(function (e) { if (e.name !== 'AbortError') console.warn('play()', e.name); }); }
  function onMeta(fn) { if (A.readyState >= 1) fn(); else A.addEventListener('loadedmetadata', function h() { A.removeEventListener('loadedmetadata', h); fn(); }); }
  function setRate() { A.defaultPlaybackRate = ST.rate; A.playbackRate = ST.rate; }
  A.addEventListener('loadedmetadata', function () { if (cur) cur.loaded = true; });
  function startPlay(slug, o) {   // クリックのイベント内で同期的に src設定+play(iOS対策)。再生レベルは常に選択中レベル
    o = o || {};
    var it = item(slug); if (!it) return;
    var lv = ST.level, url = audioUrl(slug, lv);
    if (cur && cur.loaded && (cur.slug !== slug || cur.level !== lv)) persistPos(true);   // 切替前に元の記事/レベルの位置を保存
    var same = stripQ(A.src) === stripQ(url);
    // 開始位置: 明示指定 > (同じ音声が読込済みならそのまま) > このレベル専用の保存位置(無ければ先頭)
    var at = o.at != null ? o.at : (same ? null : savedPos(slug, lv));
    cur = { slug: slug, level: lv, queue: o.queue || null, qi: o.qi || 0, loaded: same && A.readyState >= 1, startAt: at, playReq: true };
    activeUnit = null; follow = true; stopItemAudio(); clearManual('resume');
    if (!same) { A.src = url; A.load(); }
    setRate();
    if (at != null) onMeta(function () { A.currentTime = at; });
    playNow();
    ensureArt(slug).then(function () { reconcileAudio(slug); refresh(true); }, function () { /* 取得失敗(遷移で中断された等)は握りつぶさず、次回の ensureArt で再試行できる(下記 delete ARTP) */ });
    refresh(true);
  }
  function reconcileAudio(slug) {   // 記事取得後: 暫定(catalog)の音声が article の音声と違えば差し替える(位置・再生状態を引継ぐ)。?v=だけの差は再読込しない
    if (!cur || cur.slug !== slug || !A.src) return;
    var want = audioUrl(slug, cur.level);
    if (stripQ(want) === stripQ(A.src)) return;
    var wasPlaying = !A.paused || (!!A.error && cur.playReq), at = cur.loaded ? (A.currentTime || 0) : (cur.startAt != null ? cur.startAt : savedPos(slug, cur.level)), c = cur;
    c.loaded = false; A.src = want; A.load(); setRate();
    onMeta(function () { if (cur === c) { A.currentTime = at; c.loaded = true; } });
    if (wasPlaying) playNow();
  }
  function playFrom(slug, t) {   // 「ここから再生」: 選択位置(表示中レベルの正しい位置)から通常再生。以降も継続
    follow = true; lastUserScroll = 0; stopItemAudio(); clearManual('resume');
    if (isCur(slug) && cur.level === ST.level) { A.currentTime = t; playNow(); tick(); }
    else startPlay(slug, { at: t });
  }
  function playFromStart(slug) {   // 「始めから聞く」(WEBAPP-PLAY-FROM-START-BUTTON-01・DEV): 既存のplayFrom/startPlayと同じ再生制御で現在記事・現在レベルを0:00から。保存位置より優先・速度/字幕は不変
    follow = true; lastUserScroll = 0; solo = null; stopItemAudio(); clearManual('resume');
    if (isCur(slug) && cur.level === ST.level) {
      cur.startAt = 0; savePos(slug, cur.level, 0);
      if (A.readyState >= 1) A.currentTime = 0; else onMeta(function () { A.currentTime = 0; });
      playNow(); tick();
    } else startPlay(slug, { at: 0 });
  }
  function isCur(slug) { return !!(cur && cur.slug === slug && A.src); }
  function togglePlay() { solo = null; if (A.paused) { stopItemAudio(); clearManual('resume'); playNow(); } else A.pause(); }
  function nextInQueue() {
    if (!cur || !cur.queue) return false;
    var n = cur.qi + 1;
    if (n >= cur.queue.length) { return false; }
    var prev = cur.slug, wasHere = route.name === 'player' && route.arg === prev;
    startPlay(cur.queue[n], { queue: cur.queue, qi: n, at: 0 });
    if (wasHere) location.hash = '#/player/' + cur.queue[n];   // 視聴ページで聴いていた場合は次の記事の視聴ページへ追従
    toast('連続再生: 次は「' + item(cur.queue[n]).title_ja + '」(' + LV[ST.level] + ')');
    return true;
  }
  A.addEventListener('ended', function () { if (cur) savePos(cur.slug, cur.level, 0); if (!nextInQueue()) refresh(); });

  function setLevel(next) {   // A-8: StandardとAdvancedは独立した音声。位置を転送せず、切替で自動再生もしない
    if (next === ST.level) { if (ST.lvTemp) { ST.lvTemp = false; lsSet(K_LEVEL, next); } return Promise.resolve(); }   // 旧URL ?lv= の一時レベルと同じ値を利用者が明示選択した場合は、その選択を端末保存する
    ST.lvTemp = false;
    if (cur && cur.loaded) persistPos(true);   // 切替前のレベルの位置を、そのレベル用に保存
    ST.level = next; lsSet(K_LEVEL, next); clearManual('level');
    var p = Promise.resolve();
    if (cur && A.src && cur.level !== next) {   // 読込済みの音声がある場合: 一時停止し、相手レベルの「保存位置(無ければ先頭)」で待機
      var c = cur, at = savedPos(c.slug, next), was = !A.paused;
      A.pause(); c.level = next; c.loaded = false; activeUnit = null;
      A.src = audioUrl(c.slug, next); A.load(); setRate();
      p = new Promise(function (resolve) {
        onMeta(function () {
          if (cur === c) { A.currentTime = at; c.loaded = true; }
          toast(LV[next] + 'に切り替えました。' + (at > 1 ? '前回の続き(' + fmt(at) + ')から' : '先頭から') + '、再生ボタンで再生します' + (was ? '(再生を一時停止しました)' : ''));
          refresh(true); resolve();
        });
      });
    }
    rerender();
    return p;
  }

  /* ---------- 描画: 共通部品 ---------- */
  function lvSeg(id, small) {
    return '<div class="lvseg' + (small ? ' sm' : '') + '" id="' + id + '" role="group" aria-label="レベル選択">' +
      ['std', 'adv'].map(function (k) { return '<button type="button" data-lv="' + k + '" aria-pressed="' + (ST.level === k) + '">' + (k === 'std' ? IC.bars3 : IC.bars4) + LV[k] + '</button>'; }).join('') + '</div>';
  }
  function topBar(o) {
    o = o || {};
    return '<div class="top"><div class="side">' + (o.back ? '<button class="iconbtn backbtn" data-back aria-label="戻る"><span class="ba" aria-hidden="true">&#8249;</span><span class="bl">戻る</span></button>' : '') + '</div><div class="logo">' + LOGO + '<b>eigo-radio</b></div><div class="side"><button class="iconbtn q" id="helpbtn" aria-label="使い方(チュートリアル)を表示">?</button></div></div>';
  }
  function chips(it) {
    return '<div class="chips"><span class="chip">' + esc(it.genres[0]) + '</span><span class="chip lv' + (ST.level === 'adv' ? 'adv' : '') + '" data-lvchip>' + LV[ST.level] + '</span></div>';
  }
  function cardHtml(it, queueName) {   // A-2: 再生ボタンはカード上側(右上)。概要はその下でカード横幅いっぱい(行数は2行のまま)
    var on = isCur(it.slug) && !A.paused;
    return '<article class="card' + (isCur(it.slug) ? ' now' : '') + '" data-open="' + it.slug + '" data-q="' + (queueName || '') + '" tabindex="0">' +
      '<div class="ctop">' + thumbHtml(it, true) + '<div class="cmain"><h4>' + esc(it.title_ja) + '</h4>' + chips(it) + '</div>' +
      '<button type="button" class="cardplay' + (on ? ' on' : '') + '" data-play="' + it.slug + '" data-q="' + (queueName || '') + '" aria-label="' + esc(it.title_ja) + ' を' + LV[ST.level] + 'で' + (on ? '一時停止' : '再生') + '">' + (on ? IC.pause : IC.play) + '</button></div>' +
      '<p class="sum">' + esc(it.summary_ja) + '</p></article>';
  }
  function byNew() { return ST.cat.items.slice().sort(function (a, b) { return (b.added_ts - a.added_ts) || (a.slug < b.slug ? -1 : 1); }); }

  /* ---------- 画面: ホーム ---------- */
  function viewHome() {
    var s = statsView(), items = byNew();
    return topBar() + '<p class="tag">英語を、ラジオで楽しく学ぼう。<span class="kari">コピー仮</span></p>' +
      lvSeg('lvseg-home') + '<p class="lvnote">選んだレベルで、このアプリのすべての再生ボタンが再生されます(現在: <b data-lvname>' + LV[ST.level] + '</b>)</p>' +
      '<div class="stats" id="stats"><div class="stat"><small>連続学習</small><b>' + s.streak + '<i>日</i></b></div><div class="stat"><small>今週</small><b>' + s.week + '<i>分</i></b></div><div class="stat"><small>累計</small><b>' + s.total.v + '<i>' + s.total.u + '</i></b></div></div>' +
      '<div class="lvnote" style="margin:-6px 0 12px">学習記録は端末内の再生時間による<span class="kari">仮集計</span></div>' +
      '<section class="omakase" id="omakase"><span class="pill">おまかせラジオ</span><h2>今日も英語を楽しもう。</h2><p>新着記事からランダムに連続再生</p>' +
      '<button type="button" class="bigbtn" id="omakase-btn" data-omakase>' + IC.play + '<span><span data-lvname2>' + LV[ST.level] + '</span>で再生</span></button>' +
      '<div class="fine">仮設定: 新着' + items.length + '件すべてをランダム順・既聴も含む・1周で停止(Production採用しない)</div></section>' +
      '<div class="sh"><h3>新着エピソード<span class="kari">新着順・ジャンル・概要は仮</span></h3><a href="#/list?g=all">すべて見る &#8250;</a></div>' +
      '<div class="cards">' + items.map(function (it) { return cardHtml(it, 'home'); }).join('') + '</div>';
  }
  /* ---------- 画面: 記事を探す ---------- */
  function genreCount(g) { return ST.cat.items.filter(function (x) { return x.genres.indexOf(g) >= 0; }).length; }
  function viewSearch() {
    return topBar() + '<h2 style="margin:4px 0 10px;color:var(--navy)">記事を探す</h2>' +
      '<label class="search"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M16.5 16.5L21 21"/></svg><input id="q" type="search" placeholder="タイトル・概要・キーワードで検索" autocomplete="off" aria-label="キーワード検索"></label>' +
      '<div id="qres"></div><div id="browse"><div class="rows"><a class="row all" href="#/list?g=all">すべての記事<small>' + ST.cat.items.length + '件 &#8250;</small></a></div>' +
      '<div class="sh"><h3>ジャンル<span class="kari">仮割付</span></h3></div><div class="rows">' +
      ST.cat.genres.map(function (g, i) { var n = genreCount(g); return '<a class="row" href="#/list?g=' + i + '">' + esc(g) + '<small>' + (n ? n + '件' : '準備中') + ' &#8250;</small></a>'; }).join('') + '</div>' +
      '<p class="lvnote">ジャンル体系は既存記事の分布確認後に正式確定します(本画面は仮割付・主+副の多重所属)</p></div>';
  }
  function norm(s) { return String(s || '').toLowerCase().normalize('NFKC'); }
  function doSearch(q) {
    var terms = norm(q).split(/\s+/).filter(Boolean), res = $('qres'), br = $('browse');
    if (!terms.length) { res.innerHTML = ''; br.classList.remove('hide'); return; }
    var hit = byNew().filter(function (it) { var hay = norm([it.title_ja, it.title_en, it.summary_ja, it.keywords.join(' ')].join(' ')); return terms.every(function (t) { return hay.indexOf(t) >= 0; }); });
    br.classList.add('hide');
    res.innerHTML = '<div class="sh" style="margin-top:12px"><h3>検索結果 ' + hit.length + '件</h3></div>' + (hit.length ? '<div class="cards">' + hit.map(function (it) { return cardHtml(it, 'search'); }).join('') + '</div>' : '<div class="empty">該当する記事がありません</div>');
  }
  /* ---------- 画面: 一覧 ---------- */
  function listItems(g) { return byNew().filter(function (it) { return g === 'all' || it.genres.indexOf(ST.cat.genres[+g]) >= 0; }); }
  function viewList(g) {
    var items = listItems(g), title = g === 'all' ? 'すべての記事' : (ST.cat.genres[+g] || '');
    return topBar({ back: true }) + '<h2 style="margin:4px 0 4px;color:var(--navy)">' + esc(title) + '<small style="font-size:13px;color:var(--muted);margin-left:8px">' + items.length + '件' + (g === 'all' ? '' : '<span class="kari">仮割付</span>') + '</small></h2>' +
      '<div class="seqbtns"><button type="button" class="bigbtn" data-seq="new" data-g="' + g + '">' + IC.play + '新着順で連続再生</button><button type="button" class="bigbtn ghost" data-seq="rand" data-g="' + g + '">' + IC.play + 'ランダムで連続再生</button></div>' +
      '<p class="lvnote" style="margin-top:-6px">連続再生も選択中のレベル(<b data-lvname>' + LV[ST.level] + '</b>)で再生します</p>' +
      (items.length ? '<div class="cards">' + items.map(function (it) { return cardHtml(it, 'list:' + g); }).join('') + '</div>' : '<div class="empty">このジャンルの記事は準備中です(仮割付で該当0件)</div>');
  }
  /* ---------- 画面: 復習帳 / マイページ ---------- */
  function basesFor(slug) {
    var eu = new URL('../' + slug + '/enduser/', location.href), d = ART[slug];
    return { baseV: eu.href, baseK: new URL((d && d.art.audio_base) || '../', eu).href };
  }
  function reviewLookup(art, level, en, bases) {   // 保存レベルの項目のみ(別レベル代用禁止)。pwcard.js(buildPWItems)の出力から引く
    var L = art && art.levels && art.levels[level]; if (!L || !bases) return null;
    var k = PWCard.normEn(en), hit = PWCard.buildPWItems(L, bases.baseV, bases.baseK).filter(function (x) { return PWCard.normEn(x.en) === k; })[0];
    return hit || null;
  }
  function levelsOf(slug, en) {   // 旧wut01.savedの移行用: その表現があるレベル(データで決定)
    var d = ART[slug], k = PWCard.normEn(en), out = [];
    if (!d) return out;
    ['std', 'adv'].forEach(function (lv) { var L = d.art.levels[lv]; if (L && PWCard.buildPWItems(L, '', '').some(function (x) { return PWCard.normEn(x.en) === k; })) out.push(lv); });
    return out;
  }
  function migrateSaved() {   // 旧wut01.saved -> store(1回限り)。記事取得に失敗したら呼ばず次回に回す
    var sv = lsGet(K_SAVED, []); if (!Array.isArray(sv)) sv = [];
    var st = store.load(); if (st.status === 'failed' || st.status === 'unavailable') return Promise.resolve();
    if (st.status === 'ok' && st.state.migrated) return Promise.resolve();
    var slugs = {}; sv.forEach(function (x) { if (x && x.slug && item(x.slug)) slugs[x.slug] = 1; });
    return Promise.all(Object.keys(slugs).map(function (sl) { return ensureArt(sl).then(function () { return true; }, function () { return false; }); })).then(function (rs) {
      if (rs.indexOf(false) >= 0) return;
      store.migrateOnce(sv, SRS.todayJST(Date.now()), levelsOf);
    });
  }
  function viewReview() {
    return topBar() + '<div id="srsroot"></div>';
  }
  function mountReview() {
    if (reviewCtl) { reviewCtl.destroy(); reviewCtl = null; }
    var el = $('srsroot'); if (!el || route.name !== 'review') return;
    var ctl = reviewCtl = WURReview.create({
      SRS: SRS, store: store, win: window,
      hasArticle: function (slug) { return !!item(slug); },
      loadArticle: function (slug) { return ensureArt(slug).then(function (d) { return d.art; }); },
      bases: basesFor, lookup: reviewLookup,
      render: function (x) { return PWCard.renderPWCard(x, 0, { variant: 'review', playIcon: IC.play }); },
      playAudio: playReviewAudio, stopAudio: stopItemAudio   // WUI4: 復習の音声は保存項目の同レベルarticle項目のaudio(url[+start/end])のみ。再タップは先頭から
    });
    migrateSaved().then(function () { if (reviewCtl === ctl && $('srsroot') === el) ctl.mount(el); });
  }
  function viewMe() {
    return topBar() + '<h2 style="margin:4px 0 8px;color:var(--navy)">マイページ<span class="kari">ダミー</span></h2><div class="dummy">マイページはダミー画面です(正式仕様なし)。</div>' +
      '<div class="pl">レベル設定(共通)</div>' + lvSeg('lvseg-me', true) +
      '<div class="lvnote">Standard: ' + LV_HINT.std + ' / Advanced: ' + LV_HINT.adv + '。目安であり、どちらも自由に選べます。</div>' +
      '<button class="setrow" id="tutbtn">使い方(チュートリアル)を見る<span>&#8250;</span></button>' +
      '<button class="setrow" id="resetbtn">端末内の試作データを消す(レベル・保存・学習記録・チュートリアル)<span>&#8250;</span></button>' +
      '<div class="setrow"><span>試作版ビルド</span><small>rev12 / Trial・未承認 / 数値・ジャンル・概要の一部は仮データ</small></div>' +
      '<div class="setrow"><span>元データの更新検知</span><small>' + (ST.warn.length ? '更新あり: ' + ST.warn.length + '件' : '異常なし(再生時に検査)') + '</small></div>';
  }

  /* ---------- 画面: プレイヤー ---------- */
  var KIND_HEAD = { topic: 'Topic', jtitle: '日本語タイトル', preview: 'Preview', oneline: 'In One Line' };
  var JA_RE = /[ぁ-んァ-ヶ一-龠]/;
  function viewPlayer(slug) {
    var it = item(slug); if (!it) return topBar({ back: true }) + '<div class="empty">記事が見つかりません</div>';
    return topBar({ back: true }) +
      '<div class="ptitle">' + thumbHtml(it, false) + '<div><h1>' + esc(it.title_ja) + '</h1><p class="en">' + esc(it.title_en) + '</p><div class="chips"><span class="chip">' + esc(it.genres[0]) + '<span class="kari">仮</span></span><span class="chip lv' + (ST.level === 'adv' ? 'adv' : '') + '" data-lvchip>' + LV[ST.level] + '</span></div></div></div>' +
      '<div id="pnotice"></div>' + lvSeg('lvseg-player') + '<div class="nowlv" id="nowlv"></div>' +
      '<div class="modeseg" id="modeseg" role="group" aria-label="聴く/学ぶ"><button type="button" data-mode="listen" aria-pressed="' + (ST.mode === 'listen') + '">聴く</button><button type="button" data-mode="learn" aria-pressed="' + (ST.mode === 'learn') + '">学ぶ</button></div>' +
      '<div class="fsrow" id="fsrow"><button type="button" class="fsbtn" id="fsbtn" data-fromstart aria-label="この記事を始めから聞く">&#9654; 始めから聞く</button></div>' +
      '<div id="pcontent"><div class="empty">読み込み中…</div></div>' +
      '<a class="fullink" href="../' + slug + '/enduser/index.html?lv=' + ST.level + '" target="_blank" rel="noopener">既存の完全版ページを開く &#8250;</a>' +
      '<div class="backbottom"><button type="button" class="iconbtn backbtn big" data-back id="backbottom" aria-label="' + esc(backInfo().label) + '"><span class="ba" aria-hidden="true">&#8249;</span><span class="bl">' + esc(backInfo().label) + '</span></button></div>';
  }
  function sentHtml(p) {
    return (p.paragraphs || []).map(function (para) {
      var ja = JA_RE.test(para.map(function (s) { return s.text; }).join(''));
      return '<p lang="' + (ja ? 'ja' : 'en') + '">' + para.map(function (s) { return '<span class="sent" data-sid="' + s.sid + '">' + s.html + '</span>'; }).join(ja ? '' : ' ') + '</p>';
    }).join('');
  }
  /* A-3 聴く: 音声順に、読み上げられる全コンテンツ(Preview/Comment/Key Phrase/本文全Part/導入ナレーション)を表示。
     効果音(sfx)は読み上げではないので表示しない。全文日本語訳は全英語Partの後ろへ(A-6)。 */
  function jaHtml(p, k, t) {   // REF承継(従来enduser/app.js jaHtml と同アルゴリズム): ja_align の範囲を <span class="jhl" data-jg> で包むだけ(訳本文は書き換えない)。無し/不正(範囲外・重なり)は素のテキスト
    var al = p.ja_align;
    if (!al || !al.length) return esc(t);
    var gs = al.filter(function (g) { return g.ja && g.ja[0] === k && g.ja[1] >= 0 && g.ja[1] < g.ja[2] && g.ja[2] <= t.length; }).sort(function (x, y) { return x.ja[1] - y.ja[1]; });
    var out = '', pos = 0;
    for (var i = 0; i < gs.length; i++) {
      var a = gs[i].ja[1], b = gs[i].ja[2];
      if (a < pos) return esc(t);
      out += esc(t.substring(pos, a)) + '<span class="jhl" data-jg="' + p.idx + ':' + gs[i].g + '">' + esc(t.substring(a, b)) + '</span>';
      pos = b;
    }
    return out + esc(t.substring(pos));
  }
  function listenHtml(L) {
    var out = '', tr = '';
    JG = {};
    L.parts.forEach(function (p, i) {
      if (p.kind === 'sfx') return;
      var head = KIND_HEAD[p.kind] || p.label;
      var go = '<button type="button" class="from" data-from="' + p.start + '" aria-label="' + esc(head) + ' をここから再生">&#9654; ここから再生</button>';
      if (p.kind === 'fixed') { out += '<div class="fx" data-unit="p' + i + '"><span>' + esc(p.label) + '</span></div>'; return; }
      if (p.kind === 'kp') {
        out += '<section class="part kpb" data-unit="p' + i + '"><div class="phd"><span class="pl">' + esc(head) + '</span>' + go + '</div>' + (p.kp || []).map(function (k) {
          return '<div class="kpl"><div class="kp-en">' + esc(k.en) + '</div><div class="kp-tx" lang="' + (JA_RE.test(k.text || '') ? 'ja' : 'en') + '">' + esc(k.text || '') + (k.text2 ? '<br>' + esc(k.text2) : '') + '</div></div>';
        }).join('') + '</section>';
        return;
      }
      if (p.paragraphs && p.paragraphs.length) {
        out += '<section class="part" data-part="' + i + '"><div class="phd"><span class="pl">' + esc(head) + '</span>' + go + '</div>' + sentHtml(p) + '</section>';
        if (p.ja && p.ja.length) {
          (p.ja_align || []).forEach(function (g) { (g.sids || []).forEach(function (sd) { JG[sd] = p.idx + ':' + g.g; }); });
          tr += '<div class="pl">' + esc(head) + '</div><div class="tr" lang="ja">' + p.ja.map(function (t, k) { return '<p>' + jaHtml(p, k, t) + '</p>'; }).join('') + '</div>';
        }
      }
    });
    if (tr) out += '<section class="secbox" id="fulltr"><h3>日本語訳(全文)</h3>' + tr + '</section>';
    return '<div class="script">' + out + '</div>';
  }
  function buildPWI(slug, L, art) {   // 学ぶ画面と吹き出しが同じ項目生成(PWCard.buildPWItems)を使う(R2)
    var eu = new URL('../' + slug + '/enduser/', location.href);
    PWI = PWCard.buildPWItems(L, eu.href, new URL(art.audio_base || '../', eu).href);
  }
  /* A-9 学ぶ: Key Phraseとその他のPhrase/Wordを同一コーナーに統合(同じ表現は1項目に統合) */
  function learnHtml(slug, L, art) {
    var out = '';
    function isSaved(en) { return store.isSaved(slug, ST.level, en); }
    buildPWI(slug, L, art);
    if (PWI.length) {
      out += '<section class="secbox pw" id="pwbox"><h3>Phrase / Word<small>Key Phraseを含む</small></h3>' + PWI.map(function (x, i) {
        return PWCard.renderPWCard(x, i, { saved: isSaved(x.en), playIcon: IC.play });
      }).join('') + '</section>';
    }
    if (L.todays_expression && L.todays_expression.length) {   /* TDXP 委任_03: Today's Expression(学ぶの2番目=Phrase/Wordの次・文法の前。ユーザー判断 UDR #253。キー無し=非表示。折りたたみ・入力欄・採点・履歴・TTSなし。固定注記は見出し直下に1個) */
      out += '<section class="secbox tx-box" id="todaysbox"><h3>Today&#39;s Expression<small>本日の表現</small></h3><p class="lvnote tx-fixed">この記事に関連する、本文には登場しない英語表現を紹介します。</p>' + L.todays_expression.map(function (it) {
        var f = {}; it.fields.forEach(function (x) { f[x.label] = x.html; });
        return '<div class="tx"><p class="tx-expr">' + (f['表現'] || '') + '</p><p class="tx-mean">' + (f['意味'] || '') + '</p><dl>' +
          '<dt>どんな場面で使う？</dt><dd>' + (f['どんな場面で使う？'] || '') + '</dd>' +
          '<dt>自然な例文</dt><dd><p class="tx-en">' + (f['自然な例文'] || '') + '</p><p class="tx-ja">' + (f['例文の日本語訳'] || '') + '</p></dd>' +
          (f['似た表現との違い'] ? '<dt>似た表現との違い</dt><dd>' + f['似た表現との違い'] + '</dd>' : '') +
          '</dl></div>';   /* ECUI 委任_05(TELK): 「この記事とのつながり」(link)は描画しない(既存データに残っていても非表示) */
      }).join('') + '</section>';
    }
    if (L.grammar && L.grammar.length) {
      out += '<section class="secbox gram"><h3>文法・構文解説<small>Grammar &amp; Sentence Structure</small></h3>' + L.grammar.map(function (it) {
        return '<div class="gr"><dl>' + it.fields.map(function (f) { return '<dt>' + esc(f.label) + '</dt><dd>' + f.html + '</dd>'; }).join('') + '</dl></div>';
      }).join('') + '</section>';
    }
    if (L.think_express && L.think_express.length) {   /* TEX 委任_03: Think & Express(文法の次=3番目。キー無し=非表示。回答例は<details>初期閉・入力欄/採点/履歴/TTSなし) */
      out += '<section class="secbox te-box" id="thinkbox"><h3>Think &amp; Express<small>自分の考えを英語で</small></h3>' + L.think_express.map(function (it) {
        var f = {}; it.fields.forEach(function (x) { f[x.label] = x.html; });
        return '<div class="te"><div class="te-q"><p class="te-en">' + (f['質問'] || '') + '</p><p class="te-ja">' + (f['質問の日本語訳'] || '') + '</p></div>' +
          '<details class="te-ans"><summary>回答例を見る</summary><div class="te-a"><p class="te-en">' + (f['回答例'] || '') + '</p><p class="te-ja">' + (f['回答例の日本語訳'] || '') + '</p></div></details></div>';
      }).join('') + '</section>';
    }
    out += '<section class="secbox"><h3>保存・復習</h3><p class="lvnote" style="text-align:left;margin:0 0 8px">各項目の「保存」で、この端末内(仮動作)に保存できます。</p><a class="setrow" href="#/review" style="text-decoration:none">復習帳を開く<span>&#8250;</span></a></section>';
    return out;
  }
  function renderContent() {
    var el = $('pcontent'), slug = route.arg; if (!el) return;
    var d = ART[slug]; if (!d) return;
    var L = d.art.levels[ST.level];
    var n = $('pnotice'); if (n) n.innerHTML = d.art.notice ? '<div class="notice">' + esc(d.art.notice) + '</div>' : '';
    manual = null; ST.sel = null; closeBubble(true);
    if (ST.mode === 'listen') buildPWI(slug, L, d.art);
    el.classList.toggle('listenmode', ST.mode !== 'learn');
    el.innerHTML = ST.mode === 'learn' ? learnHtml(slug, L, d.art) : listenHtml(L);
    sentEls = {}; Array.prototype.forEach.call(el.querySelectorAll('[data-sid]'), function (e) { sentEls[e.dataset.sid] = e; });
    units = ST.mode === 'listen' ? buildUnits(slug, L) : [];
    activeUnit = null; audioSid = null; activePh = null;
    if (ST.mode === 'listen') markWords(el, glossFor(slug));
    placePanel(true); updateActive(true); updateCaption();
  }
  function hasJa(slug) { var d = ART[slug]; return !!(d && Object.keys(d.jaBy[ST.level]).length); }
  function buildUnits(slug, L) {   // A-4: 全音声区間(文/Key Phrase/導入ナレーション)の時間帯と表示要素の対応
    var u = [], by = {}, root = $('pcontent');
    syncOf(slug, ST.level).forEach(function (s) { by[s.sid] = s; });
    Object.keys(sentEls).forEach(function (sid) { var s = by[sid]; if (s) u.push({ kind: 'sent', key: sid, start: s.start, end: s.end, el: sentEls[sid] }); });
    L.parts.forEach(function (p, i) {
      if (p.kind !== 'fixed' && p.kind !== 'kp') return;
      var el = root.querySelector('[data-unit="p' + i + '"]'); if (!el) return;
      var ea = p.kind === 'kp' && p.kp && p.kp[0] && p.kp[0].en_audio;
      u.push({ kind: p.kind, key: 'p' + i, start: p.start, end: p.start + p.dur, el: el, enEnd: ea ? p.start + ea.end : null });
    });
    u.sort(function (a, b) { return a.start - b.start; });
    return u;
  }
  function syncOf(slug, lv) { return (ART[slug] && ART[slug].sync[lv]) || []; }
  function findUnit(t) {   // 現在位置の区間。隙間(~1.2秒)は直前の区間を保持してハイライトのちらつきを防ぐ
    var lo = 0, hi = units.length - 1, k = -1;
    while (lo <= hi) { var m = (lo + hi) >> 1; if (units[m].start <= t) { k = m; lo = m + 1; } else hi = m - 1; }
    return (k >= 0 && t < units[k].end + 1.2) ? units[k] : null;
  }
  function visBox(opt) {   // 本文を見られる領域: セーフエリア上端〜dock上端(視聴ページ)/ナビ・ミニの上端、visualViewport(Safariバー・ズーム)内
    var vv = window.visualViewport, t0 = vv ? vv.offsetTop : 0, h = vv ? vv.height : innerHeight;
    var top = t0 + safeInsets().t;
    var bottom = Math.min(t0 + h, $('nav').getBoundingClientRect().top);
    var dk = $('dock'); if (dk && !dk.hidden) bottom = Math.min(bottom, dk.getBoundingClientRect().top);
    var m = $('mini'); if (m && !m.hidden) bottom = Math.min(bottom, m.getBoundingClientRect().top);
    var fs = $('floatstack'); if (fs && !fs.hidden && !(opt && opt.nofloat)) Array.prototype.forEach.call(fs.children, function (c) { if (!c.hidden) bottom = Math.min(bottom, c.getBoundingClientRect().top - 8); });   // WUG2: 浮遊ボタンの上端より上を本文可視帯とする
    return { top: top, bottom: bottom };
  }
  function autoScroll(u) {   // A-5: 現在区間を画面中央付近へ滑らかに。大きなずれの時だけ動かす(過度なスクロール防止)
    if (!u || !follow || manual || ST.mode !== 'listen' || tutOn || route.name !== 'player') return;   // 手動選択中は追従スクロールしない
    var b = visBox(), H = b.bottom - b.top, r = u.el.getBoundingClientRect(), dy;
    if (H < 60) return;
    if (r.height > H * 0.8) dy = r.top - (b.top + H * 0.12);   // 入り切らない長い区間は先頭を優先
    else dy = (r.top + r.bottom) / 2 - (b.top + b.bottom) / 2;
    if (Math.abs(dy) < H * 0.1) return;
    window.scrollBy({ top: dy, behavior: Math.abs(dy) > innerHeight * 1.5 ? 'auto' : 'smooth' });   // 近い移動は滑らかに、シーク等の大きな移動は即時
  }
  function setFollow(on) { follow = on; var f = $('followbtn'); if (f) f.hidden = on || route.name !== 'player' || ST.mode !== 'listen' || !isCur(route.arg); if (on) autoScroll(activeUnit); }
  function updateActive(force) {
    if (route.name !== 'player') return;
    var slug = route.arg, u = null;
    if (ST.mode === 'listen' && isCur(slug) && cur.level === ST.level && (A.currentTime > 0 || !A.paused)) u = findUnit(A.currentTime || 0);
    var ph = u && u.kind === 'kp' ? ((u.enEnd != null && A.currentTime < u.enEnd) ? 'en' : 'tx') : null;   // Key Phrase: 英語表現/日本語訳の読み上げ中を行単位で(強調クラスは単一.hl+data-ph)
    if (u !== activeUnit || force || ph !== activePh) {
      var moved = u !== activeUnit || force;
      activeUnit = u; activePh = ph; audioSid = u && u.kind === 'sent' ? u.key : null;
      renderActive(); updateCaption();
      if (moved) { placePanel(false); autoScroll(u); }
    }
  }
  /* 強調の描画は renderActive() のみ。全要素から .hl/.man/data-ph を外し、表示対象1つにだけ付ける。
     手動選択中は音声側の強調(文・Key Phrase/導入区間・Key Phrase内の行)を全て外す(M2)。 */
  function renderActive() {
    Array.prototype.forEach.call(document.querySelectorAll('.hl,.man'), function (e) { e.classList.remove('hl', 'man'); });
    Array.prototype.forEach.call(document.querySelectorAll('[data-ph]'), function (e) { e.removeAttribute('data-ph'); });
    if (route.name === 'player' && ST.mode === 'listen') {
      if (manual && sentEls[manual.sid]) sentEls[manual.sid].classList.add('hl', 'man');
      else if (activeUnit) { activeUnit.el.classList.add('hl'); if (activeUnit.kind === 'kp' && activePh) activeUnit.el.setAttribute('data-ph', activePh); }
    }
    Array.prototype.forEach.call(document.querySelectorAll('.jhl.on'), function (e) { e.classList.remove('on'); });
    if (route.name === 'player' && ST.mode === 'listen') {   // 訳本文の群点灯: 英文の点灯文(手動選択優先)と同じ sid の群だけ。.hl とは別クラス(.hl 1個以下の不変条件に影響しない)
      var jsid = manual ? manual.sid : audioSid, jg = jsid && JG[jsid];
      if (jg) Array.prototype.forEach.call(document.querySelectorAll('.jhl[data-jg="' + jg + '"]'), function (e) { e.classList.add('on'); });
    }
    var cj = $('jacap'); if (cj) { if (manual) cj.setAttribute('data-man', ''); else cj.removeAttribute('data-man'); }
  }
  function syncView() { renderActive(); updateCaption(); }
  var CAP_PH = '文をタップすると日本語訳を表示します', CAP_NONE = 'この文の日本語補助訳はありません', CAP_NOART = 'この記事には日本語補助訳がありません';
  function sidAtTime(slug, t) { var r = null; syncOf(slug, ST.level).forEach(function (s) { if (t >= s.start && t < s.end) r = s.sid; }); return r; }
  function updateCaption() {   // 原文§1-1: 日本語キャプチャは画面下部dockの最上段(高さ予約でガタつき防止)。聴く/学ぶ両方で表示
    var el = $('jacap'); if (!el || route.name !== 'player') return;
    var d = ART[route.arg], sid = null;
    if (ST.mode === 'listen') sid = manual ? manual.sid : audioSid;   // 手動選択が優先(原文§2-1)
    else if (isCur(route.arg) && cur.level === ST.level && (A.currentTime > 0 || !A.paused)) sid = sidAtTime(route.arg, A.currentTime);   // 学ぶ: 再生位置の文
    var jp = sid && d ? d.jaBy[ST.level][sid] : '', txt = jp || (sid ? CAP_NONE : (d && !hasJa(route.arg) ? CAP_NOART : CAP_PH));
    capSid = sid || null;
    var cap = el.querySelector('.cap'); if (!cap) { cap = document.createElement('span'); cap.className = 'cap'; el.appendChild(cap); }
    if (cap.textContent !== txt) { cap.textContent = txt; el.scrollTop = 0; }
    el.classList.toggle('none', !jp);
    updateCapCue();
  }
  function updateCapCue() {   // WUG A-1: 続きがある時だけ右端インジケーター+下端グラデーションを出し、末尾到達でグラデーションを消す(説明文は追加しない)
    var el = $('jacap'), w = $('capwrap'); if (!el || !w) return;
    var sh = el.scrollHeight, ch = el.clientHeight, can = sh > ch + 1, atEnd = el.scrollTop + ch >= sh - 2;
    if (can) w.setAttribute('data-scroll', ''); else w.removeAttribute('data-scroll');
    if (can && !atEnd) w.setAttribute('data-more', ''); else w.removeAttribute('data-more');
    var b = w.querySelector('.capbar b'); if (!b || !can) return;
    var track = Math.max(10, w.clientHeight - 10), th = Math.max(14, Math.round(track * ch / sh)), max = sh - ch;
    b.style.height = th + 'px'; b.style.top = Math.round(max > 0 ? (track - th) * (el.scrollTop / max) : 0) + 'px';
  }
  /* ECUI B 承継実装2(REF承継): 日本語字幕ON/OFF。dock内トグル#capsw、既定ON、OFF時はキャプチャ領域(#capwrap)だけ畳む(キャプチャ→操作→ナビの順序は不変)。設定は端末保存(wut01.caption) */
  function savedCap() { return lsGet(K_CAP, 1) !== 0; }
  function capSet(on, persist) {
    CAPON = !!on; if (persist) lsSet(K_CAP, CAPON ? 1 : 0);
    var dk = $('dock'), b = $('capsw'); if (!dk) return;
    dk.classList.toggle('capoff', !CAPON);
    if (b) { b.setAttribute('aria-pressed', String(CAPON)); var st = b.querySelector('b'); if (st) st.textContent = CAPON ? 'ON' : 'OFF'; }
    layoutDock(); updateCapCue();
  }
  function capForce(on) { var dk = $('dock'); if (dk) dk.classList.toggle('capforce', !!on); }   // 字幕OFF中でも吹き出しの代替表示(キャプチャ枠内)が必要な時だけ一時的に枠を出す
  /* ECUI B 承継実装4: 旧URL互換 ?lv= / ?caption=0 (hash内、または location.search)。lvはそのrouteの間だけ(端末保存 wut01.level を上書きしない) */
  function applyRouteParams() {
    var q = route.qs, isP = route.name === 'player', lv = isP ? q.get('lv') : null, saved = lsGet(K_LEVEL, 'std') === 'adv' ? 'adv' : 'std';
    if (lv === 'std' || lv === 'adv') { ST.level = lv; ST.lvTemp = lv !== saved; }
    else if (ST.lvTemp) { ST.level = saved; ST.lvTemp = false; }
    capSet(isP && q.get('caption') === '0' ? false : savedCap(), false);
  }
  /* ---------- dock(画面下部固定): 上=日本語キャプチャ / 中=再生操作 / 下=既存#nav。実測値をCSS変数へ ---------- */
  function layoutDock() {
    var r = document.documentElement.style, nav = $('nav'), d = $('dock'), show = !!d && !d.hidden;
    r.setProperty('--nav-total', nav.offsetHeight + 'px');   // safe-area込みの実測(env()の二重加算を避ける)
    r.setProperty('--dock-h', (show ? d.offsetHeight : 0) + 'px');
    /* WUG2: 浮遊ボタン(#floatstack)の基準高さ。日本語訳の長さでdockが伸縮(キャプション52〜74px)しても文を選び直して2ボタンが上下に動かないよう、
       キャプションが上限まで伸びた時のdock高さで固定する。単語吹き出し表示中(.hasw=キャプションが大きく伸びる)は実高さに追従し、dockと重ならない。 */
    var j = $('jacap'), res = show ? d.offsetHeight : 0;
    if (show && j && !j.classList.contains('hasw') && j.offsetHeight > 0) {   // 字幕OFF(枠が畳まれている)時は予約しない
      var cs = getComputedStyle(j), mx = parseFloat(cs.maxHeight), ch = j.offsetHeight;
      if (isFinite(mx)) { if (cs.boxSizing !== 'border-box') mx += (parseFloat(cs.paddingTop) || 0) + (parseFloat(cs.paddingBottom) || 0) + (parseFloat(cs.borderTopWidth) || 0) + (parseFloat(cs.borderBottomWidth) || 0); if (mx > ch) res += mx - ch; }
    }
    r.setProperty('--dock-res', res + 'px');
  }
  function setRatePop(open) { var p = $('ratepop'), b = $('speedbtn'); if (!p || !b) return; p.hidden = !open; b.setAttribute('aria-expanded', String(open)); }
  function pickRate(v) { ST.rate = normRate(v); lsSet(K_RATE, ST.rate); setRate(); setRatePop(false); updatePlayerUI(); tick(); }
  /* WUG2 改善①: 文再生の2ボタンは本文へ挿入せず、固定の#floatstack内#sp(dock上端+12px基準)に常設。選択文が変わってもDOM・座標は不変(リフロー0)。 */
  function placePanel(force) {   // 選択した文の「この文だけ再生」「ここから再生」を#spに出す(文クリック自体は再生しない=REF)
    var tgt = ST.sel, sp = $('sp'); if (!sp) return;
    var show = !!tgt && !!sentEls[tgt] && ST.mode === 'listen' && route.name === 'player' && !tutOn;
    if (!show) { sp.hidden = true; sp.dataset.sid = ''; return; }
    if (!force && !sp.hidden && sp.dataset.sid === tgt) return;
    sp.dataset.sid = tgt;
    sp.innerHTML = '<button type="button" class="from" data-solosid="' + tgt + '">&#9654; この文だけ再生</button><button type="button" class="from" data-fromsid="' + tgt + '">&#9654; ここから再生</button>';
    sp.hidden = false;
    ensureSentVisible(sentEls[tgt]);
  }
  function ensureSentVisible(sentEl) {   // 選択文がフローティング操作の陰に入る場合だけ、文末が見える最小量スクロール(文が上端を超えない)。可視帯内ならスクロール0
    var b = visBox(), sr = sentEl.getBoundingClientRect(), dy = sr.bottom - (b.bottom - 4);
    if (dy <= 0) return;
    dy = Math.min(dy, sr.top - (b.top + 8));
    if (dy > 0) window.scrollBy(0, dy);
  }
  /* WUG A-2「この文だけ再生」: 選択した一文の開始位置から再生し、その文の終了位置で一時停止する(次の文へ進まない)。既存の同期データ(sync_*.json の start/end)を使用。
     未準備(読込直後でまだ開始位置へ移っていない)間は armed=false で終了判定をしない。ユーザーの停止/シーク/レベル切替/次の再生で解除。 */
  var solo = null;
  function playSolo(slug, sd) {
    solo = null; playFrom(slug, sd.start);
    solo = { slug: slug, level: ST.level, sid: sd.sid, start: sd.start, end: sd.end, armed: false, at: Date.now() };
  }
  function soloCheck() {
    if (!solo) return;
    if (!cur || cur.slug !== solo.slug || cur.level !== solo.level || !A.src) { solo = null; return; }
    var t = A.currentTime;
    if (!solo.armed) { if (!A.seeking && t >= solo.start - 0.3 && t < solo.end) solo.armed = true; return; }
    if (t >= solo.end - 0.02) { solo = null; A.pause(); }
  }
  /* Phrase/Word個別音声(既存音声がある項目のみ)。本編の音声とは別要素で再生し、再生中は本編を一時停止する */
  var PA = new Audio(), paNow = null;
  PA.addEventListener('timeupdate', function () { if (paNow && paNow.end != null && PA.currentTime >= paNow.end) stopItemAudio(); });
  PA.addEventListener('ended', function () { stopItemAudio(); });
  function stopItemAudio() { if (paNow == null) return; PA.pause(); paNow = null; Array.prototype.forEach.call(document.querySelectorAll('.pwplay.on'), function (b) { b.classList.remove('on'); b.innerHTML = IC.play; }); }
  function playItemAudio(i) {
    var x = PWI[i]; if (!x || !x.audio) return;
    var same = paNow && paNow.i === i; stopItemAudio(); if (same) return;
    A.pause();
    PA.src = x.audio.url + (x.audio.start != null ? '#t=' + x.audio.start + ',' + x.audio.end : ''); paNow = { i: i, end: x.audio.end != null ? x.audio.end : null };
    var p = PA.play(); if (p && p.catch) p.catch(function (e) { if (e.name !== 'AbortError') console.warn('item audio', e.name); });
    var b = document.querySelector('[data-pwplay="' + i + '"]'); if (b) { b.classList.add('on'); b.innerHTML = IC.pause; }
  }
  function playReviewAudio(au) {   // WUI4 改善②: 1タップで再生/再タップで先頭から。評価・スケジュール・答え表示には不干渉。本編は一時停止(既存item音声と同じ)
    if (!au || !au.url) return;
    stopItemAudio(); A.pause();
    PA.src = au.url + (au.start != null ? '#t=' + au.start + ',' + au.end : ''); paNow = { i: 'review', end: au.end != null ? au.end : null };
    var p = PA.play(); if (p && p.catch) p.catch(function (e) { if (e.name !== 'AbortError') console.warn('review audio', e.name); });
  }
  function updatePlayerUI() {
    if (route.name !== 'player') return;
    var slug = route.arg, it = item(slug); if (!it) return;
    var on = isCur(slug) && cur.level === ST.level, d = on ? (isFinite(A.duration) && A.duration > 0 ? A.duration : lvTotal(slug, ST.level)) : lvTotal(slug, ST.level);
    var playing = on && !A.paused;
    var sk = $('seek'); if (!sk) return;
    var sp = on ? 0 : savedPos(slug, ST.level);
    if (document.activeElement !== sk) sk.value = on && d ? Math.min(1000, Math.round(A.currentTime / d * 1000)) : (d ? Math.round(sp / d * 1000) : 0);
    sk.disabled = !on;
    $('tcur').textContent = fmt(on ? A.currentTime : sp); $('ttot').textContent = fmt(d);
    $('pp').innerHTML = playing ? IC.pause : IC.play; $('pp').setAttribute('aria-label', playing ? '一時停止' : '再生');
    $('back10').disabled = $('fwd10').disabled = !on;
    $('speedbtn').textContent = ST.rate.toFixed(1) + 'x';
    Array.prototype.forEach.call(document.querySelectorAll('#ratepop [data-rate]'), function (c) { var on = +c.dataset.rate === ST.rate; c.setAttribute('aria-checked', String(on)); c.classList.toggle('on', on); });
    var chip = '<span class="chip lv' + (ST.level === 'adv' ? 'adv' : '') + '">' + LV[ST.level] + '</span>';
    $('nowlv').innerHTML = on ? ('再生中のレベル: ' + chip) : (chip + (sp > 1 ? ' 前回の続き(' + fmt(sp) + ')から再生します <button type="button" class="linkbtn" data-restart="1">最初から</button>' : ' 先頭から再生します'));
  }
  function enterPlayer(slug) {
    ensureArt(slug).then(function () { if (route.name === 'player' && route.arg === slug) { renderContent(); updatePlayerUI(); } })
      .catch(function (e) { var c = $('pcontent'); if (c) c.innerHTML = '<div class="empty">読み込みエラー: ' + esc(e.message) + '</div>'; });
    if (ART[slug]) { renderContent(); }
    updatePlayerUI();
  }

  /* ---------- ミニプレイヤー(A-10: 再生中の記事のプレイヤー画面では非表示=固定プレイヤーと重複させない。ホーム/検索/一覧等では継続操作) ---------- */
  function renderMini() {
    var m = $('mini'), show = cur && A.src && route.name !== 'player' && !tutOn;   // 視聴ページ内はdock(再生操作)があるためミニ非表示(WUR D1)。ホーム/検索等では継続
    document.body.classList.toggle('nomini', !show);
    if (!show) { m.hidden = true; return; }
    var it = item(cur.slug);
    if (!m.firstChild || m.dataset.slug !== cur.slug) {
      m.dataset.slug = cur.slug;
      m.innerHTML = '<div class="miniin">' + thumbHtml(it, false) + '<div class="mt" data-open="' + cur.slug + '"><b>' + esc(it.title_ja) + '</b><span id="minilv"></span></div><button type="button" class="mpp" id="minipp" aria-label="再生/一時停止"></button><div class="bar" id="minibar"></div></div>';
    }
    m.hidden = false;
    var playing = !A.paused;
    $('minipp').innerHTML = playing ? IC.pause : IC.play;
    $('minilv').textContent = LV[cur.level] + ' · ' + fmt(A.currentTime) + (cur.queue ? ' · 連続再生 ' + (cur.qi + 1) + '/' + cur.queue.length : '');
    var d = isFinite(A.duration) && A.duration > 0 ? A.duration : 1; $('minibar').style.width = Math.min(100, A.currentTime / d * 100) + '%';
  }
  /* ---------- ルーティング ---------- */
  var route = { name: 'home', arg: null, qs: new URLSearchParams() };
  var fromHash = null, curHash = null;   // WUG A-3: アプリ内の遷移元(画面の種類が変わった時だけ更新。連続再生で記事→記事へ進んでも遷移元は保持)
  var BACK_LAB = { home: 'ホーム', list: '一覧', search: '検索', review: '復習帳', me: 'マイページ' };
  function backInfo() {
    var h = fromHash;
    if (!h || h === curHash || h.indexOf('#/player') === 0) h = route.name === 'list' ? '#/search' : '#/home';   // 遷移元が不明(直接アクセス等)のときの既定
    var nm = h.slice(2).split(/[\/?]/)[0];
    return { hash: h, label: (BACK_LAB[nm] || 'ホーム') + 'に戻る' };
  }
  function parseHashStr(hs) { var h = hs.slice(1) || '/home', q = h.indexOf('?'), seg = (q < 0 ? h : h.slice(0, q)).split('/').filter(Boolean); return { name: seg[0] || 'home' }; }
  function parseHash() {
    var h = location.hash.slice(1) || '/home', q = h.indexOf('?'), path = q < 0 ? h : h.slice(0, q);
    var seg = path.split('/').filter(Boolean);
    var qs = new URLSearchParams(q < 0 ? '' : h.slice(q + 1));
    ['lv', 'caption'].forEach(function (k) { if (!qs.has(k) && QS.has(k)) qs.set(k, QS.get(k)); });   // 旧URL互換: location.search の ?lv= / ?caption= も受入(hash優先)
    return { name: seg[0] || 'home', arg: seg[1] ? decodeURIComponent(seg[1]) : null, qs: qs };
  }
  function syncModeClass() { document.body.classList.toggle('modelearn', route.name === 'player' && ST.mode === 'learn'); }   // WUI4 改善④: 学ぶ画面のみ淡いブルー背景(復習帳・一覧等は不変)
  function rerender(keepScroll) {
    var y = window.scrollY, v = $('view');
    var html;
    switch (route.name) {
      case 'search': html = viewSearch(); break;
      case 'list': html = viewList(route.qs.get('g') || 'all'); break;
      case 'player': html = viewPlayer(route.arg); break;
      case 'review': html = viewReview(); break;
      case 'me': html = viewMe(); break;
      default: html = viewHome();
    }
    v.innerHTML = html; syncModeClass();
    if (route.name === 'review') mountReview(); else if (reviewCtl) { reviewCtl.destroy(); reviewCtl = null; }
    Array.prototype.forEach.call(document.querySelectorAll('#nav a'), function (a) {
      var t = a.dataset.tab, cur_ = route.name === t || (t === 'search' && route.name === 'list');
      if (cur_) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
    var dk = $('dock'); dk.hidden = route.name !== 'player'; document.body.classList.toggle('hasdock', route.name === 'player'); setRatePop(false);
    if (route.name === 'player') { enterPlayer(route.arg); }
    setFollow(follow);
    renderMini(); layoutDock();
    if (keepScroll !== false) window.scrollTo(0, y);
  }
  function onRoute() { var prevRoute = route, oldName = curHash ? parseHashStr(curHash).name : null, nh = location.hash || '#/home', nn = parseHashStr(nh).name; if (curHash && curHash !== nh && !(oldName === 'player' && nn === 'player') && oldName !== nn) fromHash = curHash; curHash = nh; route = parseHash(); if (route.name === 'player' && (prevRoute.name !== 'player' || prevRoute.arg !== route.arg)) ST.mode = 'listen'; applyRouteParams();   // WUI4 改善③: 一覧/ホーム/ミニ/戻る/別記事から記事を開く=聴く。同一記事内(?lv=等のhash変更)は維持
 manual = null; ST.sel = null; closeBubble(true); audioSid = null; activePh = null; activeUnit = null; units = []; sentEls = {}; follow = true; placePanel(true); stopItemAudio(); rerender(false); window.scrollTo(0, 0); }
  window.addEventListener('hashchange', onRoute);

  /* ---------- 一覧のうち「refresh」: 再生状態をDOMへ反映(再描画なし) ---------- */
  function refresh(structural) {
    if (structural && route.name !== 'player') {
      Array.prototype.forEach.call(document.querySelectorAll('.card'), function (c) { c.classList.toggle('now', !!cur && c.dataset.open === cur.slug); });
    }
    Array.prototype.forEach.call(document.querySelectorAll('.cardplay'), function (b) {
      var on = isCur(b.dataset.play) && !A.paused;
      b.classList.toggle('on', on); b.innerHTML = on ? IC.pause : IC.play;
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-lvchip]'), function (c) { c.textContent = LV[ST.level]; c.className = 'chip lv' + (ST.level === 'adv' ? 'adv' : ''); c.setAttribute('data-lvchip', ''); });
    Array.prototype.forEach.call(document.querySelectorAll('[data-lvname],[data-lvname2]'), function (c) { c.textContent = LV[ST.level]; });
    Array.prototype.forEach.call(document.querySelectorAll('.lvseg button'), function (b) { b.setAttribute('aria-pressed', String(b.dataset.lv === ST.level)); });
    updatePlayerUI(); renderMini();
  }

  /* ---------- tick ---------- */
  var raf = 0, touching = false, RESUME_MS = 8000;
  function tick() {
    statTick(); persistPos(false);
    soloCheck(); holdCheck();
    updatePlayerUI(); updateActive(false); if (ST.mode === 'learn') updateCaption(); renderMini();
    var st = snap();
    st.slug = cur && cur.slug; st.level = cur && cur.level; st.t = A.currentTime; st.active = activeUnit && activeUnit.key; st.src = A.src; st.rate = A.playbackRate;
    window.__WUL_STATE = st;
  }
  /* 手動選択の保持(D3/R1): 再生中の手動選択は RESUME_MS(8秒)保持→自動で追従へ復帰。手動スクロール後の追従復帰と同じ定数・同じtick内判定に一本化。
     時刻比較型(setTimeoutなし)。表示中記事の再生中のみ。吹き出し表示中は停止し、閉じた時点から再計測(closeBubbleがmanual.atを更新)。一時停止中は無期限保持。 */
  function holdCheck() {
    var now = Date.now();
    if (manual && !A.paused && route.name === 'player' && isCur(route.arg) && cur.level === ST.level && !bubbleOpen() && !touching && now - Math.max(manual.at, lastUserScroll) > RESUME_MS) { clearManual('hold'); return; }
    if (!follow && !touching && now - lastUserScroll > RESUME_MS) setFollow(true);   // 手動スクロールが止まって一定時間で自動追従へ復帰(手動選択は解除しない)
  }
  /* 不変条件: (1)全要素で .hl は1個以下 (2)キャプチャの文=強調の文(.sent.hl が無ければキャプチャも文なし)。違反はconsole.warn+data-hl-violations */
  function checkInvariant() {
    var hs = document.querySelectorAll('.hl'), sh = document.querySelector('.sent.hl'), hsid = sh ? sh.dataset.sid : null;
    if (route.name === 'player' && ST.mode === 'listen') {
      var bad = hs.length > 1 ? 'hl>1(' + hs.length + ')' : (capSid !== hsid ? 'cap(' + capSid + ')!=hl(' + hsid + ')' : (manual && hsid !== manual.sid ? 'manual!=hl' : ''));
      if (bad) { hlViol++; document.documentElement.setAttribute('data-hl-violations', String(hlViol)); if (hlViol <= 5) console.warn('WUR invariant violation:', bad); }
    }
    return { hlSid: hsid };
  }
  function snap() {   // 検査用の現在状態(DOMから直接算出)
    var inv = checkInvariant();
    return { paused: A.paused, follow: follow, hlCount: document.querySelectorAll('.hl').length, hlSid: inv.hlSid, capSid: capSid, audioSid: audioSid, manual: manual && manual.sid, bubble: bubbleOpen(), viol: hlViol };
  }
  function loop() { tick(); raf = A.paused ? 0 : requestAnimationFrame(loop); }
  ['play', 'playing'].forEach(function (ev) { A.addEventListener(ev, function () { if (!raf) raf = requestAnimationFrame(loop); refresh(); }); });
  ['pause', 'seeked', 'timeupdate', 'loadedmetadata', 'durationchange'].forEach(function (ev) { A.addEventListener(ev, function () { if (ev === 'pause') persistPos(true); tick(); if (ev === 'pause') refresh(); }); });
  A.addEventListener('play', function () { clearManual('resume'); });      // M1: 停止→再生はどの経路(ミニ▶/ロック画面/キーボード/ボタン)でも手動選択を解除
  A.addEventListener('seeking', function () { clearManual('seek'); if (solo && solo.armed) solo = null; });   // 開始位置への自分のシーク(読込が遅い回線では数秒後に起きる)は armed 前なので無視。armed後のシークは利用者操作
  A.addEventListener('pause', function () { if (solo && solo.armed) solo = null; });
  A.addEventListener('ended', function () { solo = null; });     // 位置操作(seek/±10/ここから再生)も解除
  A.addEventListener('error', function () { console.warn('audio error', A.error && A.error.code, A.src); });
  function onUserScroll(e) {   // 手動スクロール中は追従を止めて操作を妨げない(固定プレイヤー内の操作は除く)
    if (e && e.target && e.target.closest && e.target.closest('#ctl')) return;
    lastUserScroll = Date.now();
    if (follow && route.name === 'player' && ST.mode === 'listen' && isCur(route.arg)) setFollow(false);
  }
  ['wheel', 'touchmove'].forEach(function (ev) { window.addEventListener(ev, onUserScroll, { passive: true }); });
  window.addEventListener('touchstart', function () { touching = true; }, { passive: true });
  window.addEventListener('touchend', function () { touching = false; lastUserScroll = Date.now(); }, { passive: true });
  window.addEventListener('keydown', function (e) { if (['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End', ' '].indexOf(e.key) >= 0 && !(e.target && /INPUT|BUTTON/.test(e.target.tagName)) && !(e.key === ' ' && spaceEligible(e))) onUserScroll(); });
  /* ECUI B(PC): キーボード。Space=再生/一時停止(フォーカスが button/input(range含む)/select/textarea/summary/.wk に無く、吹き出し・チュートリアル・速度popが開いていない時のみ。既存の Space=スクロール->追従解除 と競合しない)、
     ←/→=±10秒(既存ボタン相当。range/select/textarea操作中は無効)、復習帳 1〜4=4段階評価(答え表示後のボタンが出ている時のみ)。Esc は既存。新しい学習仕様なし(既存操作の入力手段追加のみ) */
  var KB_BLOCK = 'button,input,select,textarea,summary,[contenteditable="true"],.wk';
  function kbOverlayOpen() { var rp = $('ratepop'); return tutOn || bubbleOpen() || !!(rp && !rp.hidden); }
  function spaceEligible(e) {
    return e.key === ' ' && !e.ctrlKey && !e.metaKey && !e.altKey && !e.shiftKey && !e.isComposing && route.name === 'player' && !kbOverlayOpen() && !(e.target && e.target.closest && e.target.closest(KB_BLOCK));
  }
  window.addEventListener('keydown', function (e) {
    if (e.defaultPrevented || e.ctrlKey || e.metaKey || e.altKey || e.isComposing) return;
    var tg = e.target, ed = tg && tg.closest && tg.closest('input,select,textarea,[contenteditable="true"]');
    if (route.name === 'player') {
      if (spaceEligible(e)) {
        e.preventDefault(); if (e.repeat) return;
        var sl = route.arg; clearManual('resume'); if (isCur(sl) && cur.level === ST.level) togglePlay(); else startPlay(sl, {}); setFollow(true); return;
      }
      if ((e.key === 'ArrowLeft' || e.key === 'ArrowRight') && !e.shiftKey && !ed && !kbOverlayOpen() && isCur(route.arg) && cur.level === ST.level) {
        e.preventDefault(); solo = null; clearManual('seek');
        A.currentTime = e.key === 'ArrowLeft' ? Math.max(0, A.currentTime - SKIP) : Math.min((A.duration || 1e9) - 0.05, A.currentTime + SKIP); tick(); return;
      }
    }
    if (route.name === 'review' && /^[1-4]$/.test(e.key) && !e.shiftKey && !e.repeat && !ed && !tutOn) {
      var gb = document.querySelectorAll('.srs-sess[data-srs-view=answer] [data-srs-grade]');
      if (gb.length === 4) { e.preventDefault(); gb[+e.key - 1].click(); }
    }
    if (e.key === 'Enter' && tg && tg.matches && tg.matches('.card[data-open]') && !tutOn) { e.preventDefault(); tg.click(); }
  });
  ['pointerover', 'focusin', 'touchstart'].forEach(function (ev) {   // 承継実装1: 再生前に article を先読みし、クリック時に真値(article)で再生できる可能性を上げる
    document.addEventListener(ev, function (e) { var b = e.target && e.target.closest && e.target.closest('[data-play]'); if (b && ST.cat && item(b.dataset.play)) ensureArt(b.dataset.play).catch(function () { }); }, { passive: true });
  });
  window.addEventListener('keydown', function (e) { if (e.key === 'Escape' && bubbleOpen()) { closeBubble(); return; } if ((e.key === 'Enter' || e.key === ' ') && e.target && e.target.classList && e.target.classList.contains('wk')) { e.preventDefault(); e.target.click(); } });
  window.addEventListener('keydown', function (e) { if (e.key === 'Escape') { var rp = $('ratepop'); if (rp && !rp.hidden) { setRatePop(false); var sb = $('speedbtn'); if (sb) sb.focus(); } } });
  window.addEventListener('pagehide', function () { persistPos(true); statFlush(); });
  document.addEventListener('visibilitychange', function () { if (document.hidden) persistPos(true); });

  function setMode(m) {
    ST.mode = m; clearManual('mode'); syncModeClass();
    Array.prototype.forEach.call(document.querySelectorAll('#modeseg button'), function (x) { x.setAttribute('aria-pressed', String(x.dataset.mode === ST.mode)); });
    renderContent(); setFollow(true);
  }
  /* ---------- 手動選択・吹き出し(WUR 委任_02c S2) ---------- */
  var GLOSS = {};
  /* WUG R2(b) 来歴ガード(実行時): 吹き出しに出す訳の出所が2つ(学習データ PWI と glossary.ja)あるとき、食い違う語は吹き出しを出さない(文クリックへ降格)。
     未検査の訳を表示しない。両者はどちらも確定gloss由来のはずなので、通常は不一致0(ビルド時検査 tools/verify_gloss_provenance_01.py と対)。 */
  function jaPlain(h) { var d = document.createElement('div'); d.innerHTML = String(h == null ? '' : h); return d.textContent.replace(/\s+/g, ' ').trim(); }
  function crossCheckGloss(gd, L, slug) {
    var items = PWCard.buildPWItems(L, '', ''), vocab = L.vocab || [];
    gd.provMismatch = [];
    Object.keys(gd.byKey).forEach(function (key) {
      var e = gd.byKey[key], g = e.gl || {};
      if (e.vi == null || !vocab[e.vi]) return;
      var nh = PWCard.normEn(vocab[e.vi].heading), x = null;
      for (var i = 0; i < items.length; i++) if (PWCard.normEn(items[i].en) === nh) { x = items[i]; break; }
      if (!x || !x.ja) return;   // PWIに訳が無い=glossary.ja単独(ビルド時検査の対象)
      var a = jaPlain(x.jaHtml ? x.ja : esc(x.ja)), b = jaPlain(esc(g.ja || ''));
      if (a !== b) { e.ok = false; e.provMismatch = true; gd.provMismatch.push({ key: key, form: e.form, pwi: a, glossary: b }); console.info('WUR gloss provenance mismatch (bubble hidden):', slug, ST.level, e.form, JSON.stringify(a), '!=', JSON.stringify(b)); }
    });
  }
  function glossFor(slug) {   // パート単位の内容照合(M3)。不一致パートは語クリックを文クリックへ降格(記事全体は止めない)
    var k = slug + '|' + ST.level, d = ART[slug];
    if (!d) return { byKey: {}, parts: [], okParts: 0, ngParts: 0 };
    if (!GLOSS[k]) {
      GLOSS[k] = WURBubble.checkLevel(d.art.levels[ST.level]);
      GLOSS[k].parts.forEach(function (p) { if (!p.ok) console.info('WUR glossary mismatch (word click disabled for this part):', slug, ST.level, p.key, p.reasons.join('; ')); });
      crossCheckGloss(GLOSS[k], d.art.levels[ST.level], slug);
    }
    return GLOSS[k];
  }
  function markWords(root, gd) {
    Array.prototype.forEach.call(root.querySelectorAll('[data-hl]'), function (w) {
      var e = gd.byKey[w.getAttribute('data-hl')];
      if (e && e.ok && w.closest('.sent')) { w.classList.add('wk'); w.setAttribute('role', 'button'); w.tabIndex = 0; w.setAttribute('aria-haspopup', 'dialog'); }
    });
  }
  var bubEntry = null, bubWord = null;
  function bubbleOpen() { var b = $('bubble'); return !!b && !b.hidden; }
  function markWordSel(w) {   // WUG A-5: 選択中のPhrase/Word(本文中)を淡いブルーで強調。常に1つだけ。吹き出しが閉じたら解除
    Array.prototype.forEach.call(document.querySelectorAll('.wsel'), function (e) { e.classList.remove('wsel'); });
    if (w && w.classList) w.classList.add('wsel');
  }
  function closeBubble(quiet) {
    var b = $('bubble'); if (!b) return;
    markWordSel(null);
    var was = !b.hidden;
    b.hidden = true; bubWord = null; bubEntry = null;
    if (b.parentNode !== document.body) document.body.appendChild(b);
    b.className = ''; b.removeAttribute('style');
    capForce(false);
    var cj = $('jacap'); if (cj) { cj.classList.remove('hasw'); layoutDock(); }
    if (was && manual) manual.at = Date.now();   // R1: 吹き出しを閉じてから8秒を再計測
  }
  function setManual(sid, wordEl) {
    manual = { sid: sid, wordEl: wordEl || null, at: Date.now() }; ST.sel = sid;
    placePanel(true); syncView();
  }
  function clearManual(reason) {   // reason: resume(再生開始/再開)/seek(位置操作)/hold(8秒経過)/toggle(同一文再クリック)/level/mode
    var had = !!manual || bubbleOpen();
    manual = null; ST.sel = null; closeBubble(true);
    if (!had) return;
    placePanel(true); syncView();
    if (reason === 'resume' || reason === 'hold') { follow = true; lastUserScroll = 0; setFollow(true); }   // 現在位置の文へ強調・キャプチャ・スクロールが復帰(原文§2-3)
  }
  function bubbleModel(entry) {
    var d = ART[route.arg], L = d.art.levels[ST.level], g = entry.gl || {}, x = null, idx = -1;
    if (entry.vi != null && L.vocab && L.vocab[entry.vi]) {   // R2: viがある項目はpwcard.js(buildPWItem)の出力から作る
      var nh = PWCard.normEn(L.vocab[entry.vi].heading);
      for (var i = 0; i < PWI.length; i++) if (PWCard.normEn(PWI[i].en) === nh) { idx = i; break; }
      if (idx >= 0) x = PWI[idx];
    }
    var ja = x && x.ja ? (x.jaHtml ? x.ja : esc(x.ja)) : esc(g.ja || '');
    return { en: x ? x.en : (g.en || entry.form), ja: ja, idx: idx, audio: !!(x && x.audio), more: idx >= 0 };
  }
  function openBubble(entry, wordEl) {
    var b = $('bubble'), m = bubbleModel(entry);
    bubEntry = entry; bubWord = wordEl; markWordSel(wordEl);
    b.innerHTML = '<div class="bub-hd"><span class="bub-lab">本文中の意味</span><button type="button" class="bub-x" id="bubclose" aria-label="吹き出しを閉じる">&times;</button></div>' +
      '<div class="bub-en" lang="en">' + esc(m.en) + '</div><div class="bub-ja" lang="ja">' + m.ja + '</div>' +
      ((m.audio || m.more) ? '<div class="bub-act">' + (m.audio ? '<button type="button" class="pwplay" data-pwplay="' + m.idx + '" aria-label="' + esc(m.en) + ' の音声を再生(本編は一時停止します)">' + IC.play + '</button>' : '') +
        (m.more ? (function () { var on = store.isSaved(route.arg, ST.level, m.en); return '<button type="button" class="save bub-save' + (on ? ' on' : '') + '" data-save="' + esc(m.en) + '" aria-pressed="' + on + '">' + (on ? '保存済' : '保存') + '</button>'; })() : '') +
        (m.more ? '<button type="button" class="bub-more" data-bubmore="' + m.idx + '">学ぶ画面で詳しく見る &#8250;</button>' : '') + '</div>' : '');
    b.hidden = false; b.setAttribute('data-lk', entry.lk);
    placeBubble();
  }
  function placeBubble() {
    var b = $('bubble'); if (!b || b.hidden || !bubWord) return;
    var bx = visBox(); if (bx.bottom - bx.top < 240) bx = visBox({ nofloat: true });   // WUG2: 浮遊ボタンを避けた帯域が狭い(横長等)時は従来の帯域(rev06と同一)で吹き出しを配置(吹き出しの出方を劣化させない)
    var band = { top: bx.top + 8, bottom: bx.bottom - 8 };
    var rects = Array.prototype.map.call(bubWord.getClientRects(), function (r) { return { left: r.left, top: r.top, right: r.right, bottom: r.bottom }; }).filter(function (r) { return r.right - r.left > 1; });
    if (rects.length && (rects[rects.length - 1].bottom < band.top || rects[0].top > band.bottom)) { closeBubble(); return; }   // 語が画面外へ出たら吹き出しだけ閉じる(文選択は維持)
    var cj = $('jacap');
    if (b.parentNode !== document.body) document.body.appendChild(b);
    b.className = ''; b.style.cssText = 'left:0;top:0;visibility:hidden;max-height:none';
    var bw = b.offsetWidth, bh = b.offsetHeight, vw = document.documentElement.clientWidth;
    var r = WURBubble.layout(rects, band, vw, bw, bh);
    if (r.mode === 'alt') {   // 吹き出しが難しい(帯域が狭い横向き等): キャプチャ枠の先頭へ意味行を代替表示(同じ要素を移動)
      b.style.cssText = ''; b.className = 'alt'; capForce(true); cj.insertBefore(b, cj.firstChild); cj.classList.add('hasw'); layoutDock();
      return;
    }
    capForce(false);
    if (cj) { cj.classList.remove('hasw'); layoutDock(); }
    b.className = r.mode; b.style.cssText = 'left:' + Math.round(r.left) + 'px;top:' + Math.round(r.top) + 'px;width:' + Math.round(r.width) + 'px;max-height:' + Math.floor(r.maxH) + 'px;--ax:' + Math.round(r.arrowX) + 'px';
  }
  function onWordClick(w) {
    var gd = glossFor(route.arg), e = gd.byKey[w.getAttribute('data-hl')], se = w.closest('.sent');
    if (!e || !e.ok || !se) return false;
    if (bubbleOpen() && bubWord === w) { closeBubble(); return true; }   // 同じ語の再クリック=吹き出しのみ閉じる(文選択は維持)
    setManual(se.dataset.sid, w);
    openBubble(e, w);
    return true;
  }
  window.addEventListener('scroll', function () { if (bubbleOpen()) requestAnimationFrame(placeBubble); }, { passive: true });
  window.addEventListener('resize', function () { if (bubbleOpen()) placeBubble(); });
  if (window.visualViewport) visualViewport.addEventListener('resize', function () { if (bubbleOpen()) placeBubble(); });

  /* ---------- 操作 ---------- */
  document.addEventListener('click', function (e) {
    var t = e.target, b;
    if (bubbleOpen() && !t.closest('#bubble') && !t.closest('.wk')) closeBubble();   // 外タップ: 吹き出しのみ閉じる(文選択は維持)
    if (t.closest('#bubclose')) { closeBubble(); return; }
    if ((b = t.closest('[data-bubmore]'))) {   // 学ぶ画面の同項目へ(詳細を開く)
      var bi = b.dataset.bubmore; clearManual('mode'); setMode('learn');
      var it = document.querySelector('[data-pw="' + bi + '"]'); if (it) { var tg = it.querySelector('.pwtog'); if (tg && tg.getAttribute('aria-expanded') === 'false') tg.click(); it.scrollIntoView({ block: 'center' }); }
      return;
    }
    var rp = $('ratepop'); if (rp && !rp.hidden && !t.closest('#ratepop,#speedbtn')) setRatePop(false);   // 外タップで閉じる
    var rb = t.closest('#ratepop [data-rate]'); if (rb) { pickRate(rb.dataset.rate); return; }
    if (tutOn && !t.closest('#tut')) return;
    if ((b = t.closest('[data-lv]'))) { setLevel(b.dataset.lv); return; }
    if ((b = t.closest('[data-play]'))) {   // 記事カードの再生: ワンタップ・選択中レベル・中間画面なし
      e.stopPropagation();
      var slug = b.dataset.play;
      if (route.name !== 'player') ST.mode = 'listen';   // WUI4 改善③: 一覧(ホーム/検索/ジャンル)の再生=リスニング目的
      if (isCur(slug) && cur.level === ST.level) { togglePlay(); return; }
      startPlay(slug, {});
      return;
    }
    if ((b = t.closest('[data-omakase]'))) { if (route.name !== 'player') ST.mode = 'listen'; var q2 = shuffle(byNew().map(function (x) { return x.slug; })); startPlay(q2[0], { queue: q2, qi: 0, at: 0 }); toast('おまかせラジオ(仮設定): ' + LV[ST.level] + ' · ランダム ' + q2.length + '件'); return; }
    if ((b = t.closest('[data-seq]'))) {
      if (route.name !== 'player') ST.mode = 'listen';
      var items = listItems(b.dataset.g).map(function (x) { return x.slug; });
      if (!items.length) { toast('このジャンルは準備中です'); return; }
      var qq = b.dataset.seq === 'rand' ? shuffle(items) : items;
      startPlay(qq[0], { queue: qq, qi: 0, at: 0 }); toast((b.dataset.seq === 'rand' ? 'ランダム' : '新着順') + 'で連続再生 · ' + LV[ST.level] + ' · ' + qq.length + '件'); return;
    }
    if ((b = t.closest('[data-open]'))) { if (route.name === 'player' && route.arg === b.dataset.open) { window.scrollTo({ top: 0, behavior: 'smooth' }); return; } location.hash = '#/player/' + b.dataset.open; return; }
    if (t.closest('[data-back]')) { location.hash = backInfo().hash; return; }   // 履歴を戻るのではなくアプリ内の遷移元へ。再生中の音声には触れない
    if (t.closest('#helpbtn') || t.closest('#tutbtn')) { startTutorial(); return; }
    if (t.closest('#resetbtn')) { [K_LEVEL, K_TUT, K_SAVED, K_STATS, K_RATE, K_POS, K_CAP].forEach(function (k) { try { localStorage.removeItem(k); } catch (er) { } }); if (store.load().status === 'failed') store.resetAfterFailure(); else store.clearAll(); toast('端末内の試作データを消しました'); ST.level = 'std'; ST.lvTemp = false; capSet(true, false); rerender(); return; }
    if ((b = t.closest('[data-save]'))) {   // 学ぶ画面・吹き出し共通: 同じstore.toggle(クリック毎のAI生成なし)
      var en = b.dataset.save, r = store.toggle(route.arg, ST.level, en, (item(route.arg) || {}).title_ja);
      if (!r.ok) { toast('保存できませんでした(この端末では保存データを使えません)'); return; }
      Array.prototype.forEach.call(document.querySelectorAll('[data-save]'), function (x) { if (x.dataset.save === en) { x.classList.toggle('on', r.saved); x.textContent = r.saved ? '保存済' : '保存'; x.setAttribute('aria-pressed', String(r.saved)); } });
      return;
    }
    if ((b = t.closest('[data-mode]'))) {   // 聴く/学ぶの切替では音声に触れない
      setMode(b.dataset.mode);
      var ms = $('modeseg'); if (ms) window.scrollTo(0, Math.max(0, ms.getBoundingClientRect().top + window.scrollY - 8));
      return;
    }
    if ((b = t.closest('[data-fromstart]'))) { playFromStart(route.arg); return; }   // 始めから聞く(聴く画面の共通ボタン)
    if ((b = t.closest('[data-from]'))) { playFrom(route.arg, +b.dataset.from); return; }   // Part先頭から
    if ((b = t.closest('[data-solosid]'))) {   // 選択した文だけ(文末で停止)
      var sd0 = syncOf(route.arg, ST.level).filter(function (x) { return x.sid === b.dataset.solosid; })[0];
      if (sd0) { clearManual('resume'); playSolo(route.arg, sd0); }
      return;
    }
    if ((b = t.closest('[data-fromsid]'))) {   // 選択した文から
      var sd = syncOf(route.arg, ST.level).filter(function (x) { return x.sid === b.dataset.fromsid; })[0];
      if (sd) { clearManual('resume'); playFrom(route.arg, sd.start); }
      return;
    }
    if ((b = t.closest('[data-pwtog]'))) {
      var dl = b.closest('.pwi').querySelector('.pwdet'), open = dl.hidden; dl.hidden = !open;
      b.setAttribute('aria-expanded', String(open)); b.querySelector('.t').textContent = open ? '閉じる' : '詳しい解説を見る'; return;
    }
    if ((b = t.closest('[data-pwplay]'))) { playItemAudio(+b.dataset.pwplay); return; }
    if (t.closest('[data-restart]')) { savePos(route.arg, ST.level, 0); updatePlayerUI(); return; }
    if (t.closest('#followbtn')) { clearManual('resume'); setFollow(true); return; }
    var wk = t.closest('.wk');   // R6: 語クリック判定は文クリックより前(最内側のdata-hl)でreturn
    if (wk && route.name === 'player' && ST.mode === 'listen' && !t.closest('button') && onWordClick(wk)) return;
    var se = t.closest('.sent');
    if (se && route.name === 'player' && !t.closest('button')) {   // 文タップ=選択のみ(REF不変。再生しない)。同時に選択は1文のみ
      var sid = se.dataset.sid;
      if (manual && manual.sid === sid) { if (!bubbleOpen()) clearManual('toggle'); return; }   // 同一文の再クリック=解除
      setManual(sid, null); return;
    }
    if (t.closest('#capsw')) { capSet(!CAPON, true); return; }
    if (t.closest('#pp')) { var sl = route.arg; clearManual('resume'); if (isCur(sl) && cur.level === ST.level) togglePlay(); else startPlay(sl, {}); setFollow(true); return; }
    if (t.closest('#minipp')) { togglePlay(); return; }
    if (t.closest('#back10')) { solo = null; clearManual('seek'); A.currentTime = Math.max(0, A.currentTime - SKIP); tick(); return; }
    if (t.closest('#fwd10')) { solo = null; clearManual('seek'); A.currentTime = Math.min((A.duration || 1e9) - 0.05, A.currentTime + SKIP); tick(); return; }
    if (t.closest('#speedbtn')) { setRatePop($('ratepop').hidden); return; }
  });
  document.addEventListener('input', function (e) {
    var t = e.target;
    if (t.id === 'q') doSearch(t.value);
    if (t.id === 'seek' && isCur(route.arg)) { solo = null; clearManual('seek'); var d = A.duration || 1; A.currentTime = Math.min(d - 0.05, t.value / 1000 * d); tick(); }
  });
  /* ---------- 初回チュートリアル: 実画面を背景にしたスポットライト(3ステップ)。A-1: 吹き出しは対象と重ならない空き領域へ自動配置 ----------
     WUG A-4(原因ベースの再設計。ROOT_CAUSE_TUTORIAL_01.md):
     (1) 座標系: 暗幕/リング/吹き出しは #tut(position:fixed)内の座標で描く。対象矩形は getBoundingClientRect() で得るため、#tut 自身の getBoundingClientRect()
         との「差」で座標を作る(innerWidth/innerHeight や layout/visual viewport の差・Safariバー変動・Safe Areaによる原点/寸法のずれが原理的に消える)。
     (2) 追従: 以前は 250ms ポーリング+resize のみ=スクロールや Safariバー伸縮の直後はずれたまま。今は requestAnimationFrame で毎フレーム実測し、
         変化(対象矩形/#tut矩形/visualViewport)があれば位置だけを更新する(DOMは作り直さない=「次へ」タップ中に消えない)。
     (3) 背景のスクロールを暗幕上で禁止(touchmove/wheel を止める)=実機で指が触れて背景だけ動き、枠が取り残される事態を防ぐ。
     (4) 枠のクランプ廃止(以前は y を2pxへ丸めて高さだけ残し枠が対象から外れた)。 */
  var TUT = null, probe = null, tutRaf = 0, tutLockBound = false;
  function tutSteps() {
    var first = byNew()[0].slug;
    return [
      { hash: '#/home', sel: ['#lvseg-home'], title: 'レベルを選ぶ', html: '<p>ここで切り替えます。</p><div class="lvs"><b>Standard</b>：TOEIC 800点未満／英検2級程度<br><b>Advanced</b>：TOEIC 800点以上／英検準1級以上</div><p class="fine2">あくまで目安で、利用制限ではありません。</p>' },
      { hash: '#/home', sel: ['#omakase-btn', '#nav a[data-tab=search]'], title: '聴き始める', html: '<p>「おまかせ再生」でランダムに連続再生。聴きたい記事は「記事を探す」から。</p>' },
      { hash: '#/player/' + first, sel: ['#lvseg-player', '#modeseg'], title: '視聴ページ', html: '<p>ここでもレベルを切り替えられます。「聴く／学ぶ」を切り替えても音声は止まりません。</p>' }
    ];
  }
  function stepEls() { return TUT ? TUT.steps[TUT.i].sel.map(function (q) { return document.querySelector(q); }).filter(Boolean) : []; }
  function startTutorial() {
    if (TUT) return;
    TUT = { i: 0, steps: tutSteps(), prevHash: location.hash || '#/home', els: null, sig: '', built: false };
    tutOn = true; $('tut').hidden = false; placePanel(true); (function () { var fs = $('floatstack'); if (fs) fs.hidden = true; })(); bindTutLock(); renderMini(); showStep();
    var loop = function () { if (!TUT) { tutRaf = 0; return; } tutSync(false); tutRaf = requestAnimationFrame(loop); };
    tutRaf = requestAnimationFrame(loop);   // 毎フレーム実測(スクロール/Safariバー伸縮/回転/読込後のレイアウト変化へ追従)
  }
  function bindTutLock() {   // 暗幕上では背景をスクロールさせない(吹き出し内の縦スクロールだけ許可)
    if (tutLockBound) return; tutLockBound = true;
    var t = $('tut');
    function stop(e) { if (!TUT) return; var tip = e.target && e.target.closest && e.target.closest('.tip'); if (tip && tip.scrollHeight > tip.clientHeight + 1) return; if (e.cancelable) e.preventDefault(); }
    t.addEventListener('touchmove', stop, { passive: false }); t.addEventListener('wheel', stop, { passive: false });
  }
  function sigOf(els) { return els.map(function (e) { var r = e.getBoundingClientRect(); return [r.left, r.top, r.width, r.height].map(function (v) { return Math.round(v * 10) / 10; }).join(','); }).join('|'); }
  function viewSig() {
    var o = $('tut').getBoundingClientRect(), vv = window.visualViewport;
    return [o.left, o.top, o.width, o.height, innerWidth, innerHeight, vv ? [vv.width, vv.height, vv.offsetLeft, vv.offsetTop, vv.scale].join(',') : '', dockTop()].map(function (v) { return typeof v === 'number' ? Math.round(v * 10) / 10 : v; }).join('|');
  }
  function waitFor(sels, cb, n) {
    n = n || 0;
    var els = sels.map(function (s) { return document.querySelector(s); });
    if (els.every(Boolean)) { cb(els); return; }
    if (n > 60) { cb(els.filter(Boolean)); return; }
    setTimeout(function () { waitFor(sels, cb, n + 1); }, 100);
  }
  function safeInsets() {   // セーフエリア(env(safe-area-inset-*))
    if (!probe) { probe = document.createElement('div'); probe.style.cssText = 'position:fixed;left:0;top:0;width:0;height:0;visibility:hidden;pointer-events:none;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)'; document.body.appendChild(probe); }
    var cs = getComputedStyle(probe); return { t: parseFloat(cs.paddingTop) || 0, b: parseFloat(cs.paddingBottom) || 0 };
  }
  function dockTop() { var d = $('dock'); return d && !d.hidden ? d.getBoundingClientRect().top : 1e9; }
  function vvBox() {   // 実際に見えている領域: visualViewport(Safariの上下バー・ズームを反映)からセーフエリアを除く(gBCRと同じ座標系)
    var vv = window.visualViewport, s = safeInsets(), t0 = vv ? vv.offsetTop : 0, h = vv ? vv.height : innerHeight;
    return { top: t0 + s.t, bottom: t0 + h - s.b, w: vv ? vv.width : innerWidth };
  }
  function showStep() {
    var st = TUT.steps[TUT.i], tut = $('tut');
    function go() {
      waitFor(st.sel, function (els) {
        if (!TUT) return;
        if (!els.length) { finishTutorial(false); return; }
        if (!els[0].closest('#nav')) {   // 対象を見える領域の上寄りへ(吹き出しを下の空き領域へ置くため)
          var r = els[0].getBoundingClientRect(); window.scrollBy(0, r.top - (vvBox().top + 72));
        }
        buildTut(); tutSync(true);   // 初回表示から実測位置で配置(同期)。以降は毎フレーム追従
      });
    }
    TUT.els = null; TUT.sig = ''; TUT.built = false; TUT.up = false;
    tut.innerHTML = '<div class="dim"></div>';
    if (location.hash !== st.hash) { location.hash = st.hash; setTimeout(go, 50); } else go();
  }
  function buildTut() {   // ステップごとに1回だけDOMを作る(位置更新では作り直さない)
    var st = TUT.steps[TUT.i], tut = $('tut'), last = TUT.i === TUT.steps.length - 1;
    tut.innerHTML = '<div class="dim"></div>' + st.sel.map(function (q, i) { return '<div class="ring" data-ring="' + i + '"></div>'; }).join('') +
      '<div class="tip" id="tip" role="dialog" aria-label="使い方 ' + (TUT.i + 1) + '/3" style="top:0;visibility:hidden"><h3>' + esc(st.title) + '</h3><div class="tbody">' + st.html + '</div><div class="foot"><div class="dots">' + TUT.steps.map(function (s, i) { return '<i class="' + (i === TUT.i ? 'on' : '') + '"></i>'; }).join('') + '<span>' + (TUT.i + 1) + '/3</span></div><div class="btns"><button type="button" data-tut="skip">スキップ</button><button type="button" class="pri" data-tut="' + (last ? 'done' : 'next') + '">' + (last ? '完了' : '次へ') + '</button></div></div></div>';
    TUT.built = true;
  }
  function tutSync(force) {   // 対象の実位置を測り、変化があれば位置だけ更新
    if (!TUT || !TUT.built) return;
    var els = stepEls(); if (els.length !== TUT.steps[TUT.i].sel.length) return;   // 対象が(再描画等で)一時的に無い間は更新しない
    var sig = sigOf(els) + '#' + viewSig();
    if (!force && sig === TUT.sig) return;
    TUT.els = els; TUT.sig = sig;
    var fit = placeTut(els);
    if (!fit && !TUT.up && !els[0].closest('#nav')) {   // 吹き出しが入らない(横長画面等): 対象を画面の上端近くへ寄せて下の空きを広げ、1回だけ再配置
      TUT.up = true; var r0 = els[0].getBoundingClientRect(); window.scrollBy(0, r0.top - (vvBox().top + 10));
      TUT.sig = sigOf(stepEls()) + '#' + viewSig(); placeTut(stepEls());
    }
  }
  function freeIntervals(rects, lo, hi, gap) {   // 対象矩形(+余白)を除いた縦方向の空き区間
    var busy = rects.map(function (r) { return [r.y - gap, r.y + r.h + gap]; }).sort(function (a, b) { return a[0] - b[0]; }), free = [], cur_ = lo;
    busy.forEach(function (b) { if (b[0] > cur_) free.push([cur_, Math.min(b[0], hi)]); cur_ = Math.max(cur_, b[1]); });
    if (hi > cur_) free.push([cur_, hi]);
    return free.filter(function (f) { return f[1] - f[0] > 0; });
  }
  function mergeOverlap(rs) {
    var out = rs.map(function (r) { return { x: r.x, y: r.y, w: r.w, h: r.h }; }), again = true;
    function hit(a, b) { return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y; }
    while (again) {
      again = false;
      for (var i = 0; i < out.length && !again; i++) for (var j = i + 1; j < out.length && !again; j++) if (hit(out[i], out[j])) {
        var x0 = Math.min(out[i].x, out[j].x), y0 = Math.min(out[i].y, out[j].y), x1 = Math.max(out[i].x + out[i].w, out[j].x + out[j].w), y1 = Math.max(out[i].y + out[i].h, out[j].y + out[j].h);
        out.splice(j, 1); out[i] = { x: x0, y: y0, w: x1 - x0, h: y1 - y0 }; again = true;
      }
    }
    return out;
  }
  function roundRectPath(r) {
    var q = Math.max(0, Math.min(18, r.w / 2, r.h / 2)), w2 = r.w - 2 * q, h2 = r.h - 2 * q;
    return 'M' + (r.x + q) + ' ' + r.y + 'h' + w2 + 'a' + q + ' ' + q + ' 0 0 1 ' + q + ' ' + q + 'v' + h2 + 'a' + q + ' ' + q + ' 0 0 1 -' + q + ' ' + q + 'h-' + w2 + 'a' + q + ' ' + q + ' 0 0 1 -' + q + ' -' + q + 'v-' + h2 + 'a' + q + ' ' + q + ' 0 0 1 ' + q + ' -' + q + 'z';
  }
  function placeTut(els) {
    var tut = $('tut'), tip = $('tip'), dim = tut.querySelector('.dim'), pad = 6;
    if (!tip || !dim) return;
    var o = tut.getBoundingClientRect(), W = o.width, H = o.height;   // #tut 自身の実矩形を原点・寸法にする(座標系の差を消す)
    var rects = els.map(function (e) { var r = e.getBoundingClientRect(); return { x: r.left - o.left - pad, y: r.top - o.top - pad, w: r.width + pad * 2, h: r.height + pad * 2 }; });
    var path = 'M0 0H' + W + 'V' + H + 'H0Z' + mergeOverlap(rects).map(roundRectPath).join('');   // 穴が重なる場合(固定ナビの裏に対象が来た等)は外接矩形へ統合(evenoddだと重なり部分が暗幕で塞がるため)
    dim.style.clipPath = 'path(evenodd,\'' + path + '\')';
    Array.prototype.forEach.call(tut.querySelectorAll('.ring'), function (rg, i) { var r = rects[i]; if (!r) return; rg.style.left = r.x + 'px'; rg.style.top = r.y + 'px'; rg.style.width = r.w + 'px'; rg.style.height = r.h + 'px'; });
    // ---- 吹き出し配置: 対象と重ならない空き領域(下→上→狭い画面は文字を詰める→横長画面は対象の左右の空き列) ----
    var box = vvBox(), gap = 12, lo = box.top - o.top + 8, hiFull = box.bottom - o.top - 8, hi = Math.min(hiFull, dockTop() - o.top - 8);
    tip.classList.remove('compact'); tip.style.cssText = 'top:0;visibility:hidden';
    var tw = Math.min(W * 0.92, 420); tip.style.width = tw + 'px';
    var fit = true, free = freeIntervals(rects, lo, hi, gap), th = tip.offsetHeight;
    function fits(f) { return f[1] - f[0] >= th; }
    var ok = free.filter(fits);
    if (!ok.length && hiFull > hi) { free = freeIntervals(rects, lo, hiFull, gap); ok = free.filter(fits); }   // 下部dockは対象ではないので、入らない時は吹き出しがdock上にかかってもよい
    if (!ok.length) { tip.classList.add('compact'); th = tip.offsetHeight; free = freeIntervals(rects, lo, hi, gap); ok = free.filter(fits); if (!ok.length && hiFull > hi) { free = freeIntervals(rects, lo, hiFull, gap); ok = free.filter(fits); } }   // 小さい画面: 文字を詰める
    if (ok.length) {
      var f = ok[ok.length - 1];   // 最も下側の空き区間(対象の下)を優先
      var firstBelow = f[0] >= Math.max.apply(null, rects.map(function (r) { return r.y; })) - 1;
      tip.style.top = Math.round(firstBelow ? f[0] : Math.max(f[0], f[1] - th)) + 'px';   // 対象の下側なら対象の直下、上側なら対象の直上
    } else {   // 縦に入らない(横長画面等): 対象の左右の空き列へ置く
      var ux0 = Math.min.apply(null, rects.map(function (r) { return r.x; })) - gap, ux1 = Math.max.apply(null, rects.map(function (r) { return r.x + r.w; })) + gap;
      var cols = [[8, ux0 - 8], [ux1 + 8, W - 8]].map(function (c) { return { x: c[0], w: c[1] - c[0] }; }).sort(function (a, b) { return b.w - a.w; }), col = cols[0];
      if (col && col.w >= 150) {
        tip.style.width = Math.min(col.w, 420) + 'px'; tip.style.left = col.x + 'px'; tip.style.transform = 'none'; tip.classList.add('compact'); th = tip.offsetHeight;
        var avail = hiFull - lo; if (th > avail) { tip.style.maxHeight = Math.max(80, avail) + 'px'; tip.style.overflowY = 'auto'; th = tip.offsetHeight; }
        tip.style.top = Math.round(Math.max(lo, Math.min(hiFull - th, rects[0].y))) + 'px';
      } else {   // 最後の手段: 最大の縦空き区間へ入れてスクロール可
        var f2 = free.slice().sort(function (a, b) { return (b[1] - b[0]) - (a[1] - a[0]); })[0] || [lo, hi];
        tip.style.maxHeight = Math.max(80, f2[1] - f2[0]) + 'px'; tip.style.overflowY = 'auto'; th = tip.offsetHeight; tip.style.top = Math.round(f2[0]) + 'px'; fit = false;
      }
    }
    tip.style.visibility = 'visible';
    return fit;
  }
  function tutCheck() {   // 検証用: 吹き出しと対象(リング/要素)の矩形交差
    if (!TUT || !TUT.els) return null;
    var tip = $('tip').getBoundingClientRect(), n = 0, list = [];
    function hit(a, b) { return a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top; }
    Array.prototype.slice.call(document.querySelectorAll('#tut .ring')).map(function (x) { return x.getBoundingClientRect(); }).concat(TUT.els.map(function (e) { return e.getBoundingClientRect(); })).forEach(function (r) { if (hit(tip, r)) n++; list.push([Math.round(r.top), Math.round(r.bottom)]); });
    var box = vvBox();
    return { overlap: n, tip: [Math.round(tip.top), Math.round(tip.bottom), Math.round(tip.left), Math.round(tip.right)], targets: list, visible: [Math.round(box.top), Math.round(box.bottom)], inside: tip.top >= box.top - 1 && tip.bottom <= box.bottom + 1 && tip.left >= 0 && tip.right <= innerWidth + 1 };
  }
  function finishTutorial(completed) {
    lsSet(K_TUT, true); tutOn = false; $('tut').hidden = true; (function () { var fs = $('floatstack'); if (fs) fs.hidden = false; })(); $('tut').innerHTML = '';
    if (tutRaf) { cancelAnimationFrame(tutRaf); tutRaf = 0; }
    TUT = null;
    if (location.hash !== '#/home') location.hash = '#/home'; else rerender();
    renderMini();
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-tut]'); if (!b || !TUT) return;
    var a = b.dataset.tut;
    if (a === 'skip' || a === 'done') { finishTutorial(a === 'done'); return; }
    TUT.i++; showStep();
  });
  function relayout() { if (TUT) TUT.up = false; tutSync(true); }
  window.addEventListener('resize', relayout);
  window.addEventListener('orientationchange', function () { setTimeout(relayout, 60); setTimeout(relayout, 400); });   // 回転直後は寸法が確定していない端末がある(再測定)
  window.addEventListener('scroll', function () { if (TUT) tutSync(false); }, { passive: true });
  if (window.visualViewport) { visualViewport.addEventListener('resize', relayout); visualViewport.addEventListener('scroll', relayout); }
  window.addEventListener('load', relayout);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(relayout);

  /* ---------- 起動 ---------- */
  if (window.ResizeObserver) { var ro = new ResizeObserver(layoutDock); ro.observe($('nav'), { box: 'border-box' }); ro.observe($('dock'), { box: 'border-box' }); }
  window.addEventListener('resize', layoutDock);
  (function () {   // キャプション手掛かりの更新契機: スクロール/本文の変化/寸法変化。resize系は寸法確定が遅れる端末(回線・WebKit)があるため、直後+遅延の2回再計算する
    var cj = $('jacap'); if (!cj) return;
    function later() { updateCapCue(); requestAnimationFrame(updateCapCue); setTimeout(updateCapCue, 250); }
    cj.addEventListener('scroll', updateCapCue, { passive: true });
    window.addEventListener('resize', later); window.addEventListener('orientationchange', later);
    if (window.visualViewport) visualViewport.addEventListener('resize', later);
    if (window.ResizeObserver) { var ro2 = new ResizeObserver(updateCapCue); ro2.observe(cj); ro2.observe($('capwrap')); }
    if (window.MutationObserver) new MutationObserver(updateCapCue).observe(cj, { childList: true, characterData: true, subtree: true });
  })();
  fetchJson('data/catalog_auto.json?v=rev12').then(function (r) {   // ECUI C-DEV2: データ源は自動catalogのみ。失敗時は旧データへ黙って戻らず、明示エラーを出す
    if (!r || r.schema !== 'ecui_catalog_auto_v1' || !Array.isArray(r.items)) throw new Error('catalog_auto.json の形式が想定外です');
    ST.cat = r;
    setRate(); onRoute(); migrateSaved();
    if (!lsGet(K_TUT, false) && !QS.get('notut')) setTimeout(startTutorial, 300);
    window.__WUL = { ST: ST, A: A, PA: PA, setLevel: setLevel, ensureArt: ensureArt, getCur: function () { return cur; }, ART: ART, startPlay: startPlay, item: item, tutCheck: tutCheck, visBox: visBox, normRate: normRate, RATES: RATES, layoutDock: layoutDock, getUnits: function () { return units; }, getFollow: function () { return follow; }, getManual: function () { return manual; }, snap: snap, glossFor: glossFor, resetGloss: function () { GLOSS = {}; }, getPWI: function () { return PWI; }, RESUME_MS: RESUME_MS, WUR02C: 1, WUR02E: 1, store: store, SRS: SRS, getReview: function () { return reviewCtl; }, migrateSaved: migrateSaved, savedPos: savedPos, resetForTest: function () { cur = null; A.pause(); A.removeAttribute('src'); A.load(); refresh(true); } };
  }).catch(function (e) { $('view').innerHTML = '<div class="empty" role="alert" data-load-error="1">一覧データ(catalog_auto.json)を読み込めませんでした: ' + esc(e.message) + '</div>'; });
})();
