/* review.js — 復習帳ビュー(DOM生成+イベント)。DEV/Trial専用・Production未承認。window.WURReview / node: module.exports
   app.js・index.html・style.css は編集しない。接続(viewReviewの差替え・script/link追加)は後続S5で行う。
   依存(注入): SRS(srs.js)・store(SRS.createStore)・記事取得(loadArticle/hasArticle)・解答描画(PWCard.renderPWCard, variant:'review')。
   PWCard未存在時はstubで動作(02a pwcard.js 到着後は自動的にそちらを使う)。 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(); else root.WURReview = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  var LVNAME = { std: 'Standard', adv: 'Advanced' };
  var GLABEL = { again: '忘れた', hard: '難しい', good: '普通', easy: '簡単' };
  var JA_RE = /[぀-ヿ一-鿿]/;

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]; }); }
  function normEn(s) { return String(s || '').toLowerCase().normalize('NFKC').replace(/[^a-z0-9 ]+/g, ' ').replace(/\s+/g, ' ').trim(); }

  /* ---------- 02a pwcard.js 未到着時のstub(解答は表示用の最小形。本番は renderPWCard(item,{variant:'review'})) ---------- */
  function stubLookup(art, level, en) {
    var L = art && art.levels && art.levels[level], k = normEn(en), hit = null; if (!L) return null;
    (L.parts || []).forEach(function (p) { if (p.kind === 'kp') (p.kp || []).forEach(function (x) { if (!hit && normEn(x.en) === k) hit = { en: x.en, ja: JA_RE.test(x.text || '') ? x.text : '', jaHtml: false, det: [], audio: null }; }); });
    (L.vocab || []).forEach(function (v) {
      if (normEn(v.heading) !== k) return;
      var m = (v.fields || []).filter(function (f) { return f.label === '本文中の意味'; })[0];
      if (!hit) hit = { en: v.heading, ja: m ? m.html : '', jaHtml: true, det: [], audio: null };
      (v.fields || []).forEach(function (f) { if (f.label !== '本文中の意味') hit.det.push({ label: f.label, html: f.html }); });
    });
    return hit;
  }
  function stubRender(item) {
    var ja = item.ja ? '<div class="srs-ja">' + (item.jaHtml ? item.ja : esc(item.ja)) + '</div>' : '<div class="srs-ja srs-pending">日本語訳: 準備中</div>';
    return '<div class="pwcard pwcard-review" data-stub="1">' + ja + (item.det || []).map(function (d) { return '<div class="srs-det"><b>' + esc(d.label) + '</b> ' + d.html + '</div>'; }).join('') + '</div>';
  }
  function pw() { return (typeof window !== 'undefined' && window.PWCard) || null; }
  function defaultLookup(art, level, en, bases) { var p = pw(); return p && p.buildPWItem ? (p.buildPWItem(art && art.levels && art.levels[level], en, bases) || null) : stubLookup(art, level, en); }
  function defaultRender(item) { var p = pw(); return p && p.renderPWCard ? p.renderPWCard(item, { variant: 'review' }) : stubRender(item); }

  /* ---------- HTML生成(純関数・data-属性はPlaywright E2E用) ---------- */
  function homeHtml(m) {
    var h = '<section class="srs-home" data-srs-view="home">';
    h += '<h2 class="srs-h">復習帳<span class="kari">仮動作</span></h2>';
    if (m.storeStatus === 'failed') h += '<div class="srs-warn" data-srs-warn="failed">保存データを読み込めませんでした。壊れたデータは退避済みで、勝手に作り直しません。<button type="button" class="srs-link" data-srs-reset>初期化して続ける</button></div>';
    if (m.storeStatus === 'unavailable') h += '<div class="srs-warn" data-srs-warn="unavailable">この環境では保存できません(プライベートモード等)。</div>';
    var total = m.counts.remaining;
    h += '<div class="srs-today" data-srs-today="' + total + '"><b>今日の復習 ' + total + '件</b><span class="srs-sub">(新規 ' + m.counts.newShown + ' / 復習 ' + (total - m.counts.newShown) + ')</span>' +
      (m.counts.newDeferred ? '<span class="srs-sub" data-srs-deferred="' + m.counts.newDeferred + '">新規はあと' + m.counts.newDeferred + '件(明日以降)</span>' : '') + '</div>';
    if (total) h += '<button type="button" class="bigbtn srs-start" data-srs-start>始める</button>';
    else h += '<div class="empty" data-srs-empty>' + (m.items.length ? '今日の復習は完了です' + (m.nextDue ? '(次回 ' + esc(m.nextDue) + ')' : '') : '保存した表現はまだありません。記事の「学ぶ」から保存できます。') + '</div>';
    if (m.netfail) h += '<div class="srs-warn" data-srs-warn="netfail" data-srs-netfail="' + m.netfail + '">通信できなかった項目が' + m.netfail + '件あります。今回は飛ばしました(予定は変わりません)。<button type="button" class="srs-link" data-srs-retry>再読込</button></div>';
    if (m.orphans.length) h += '<div class="srs-warn" data-srs-warn="orphan" data-srs-orphan-count="' + m.orphans.length + '">元データが見つかりません: ' + m.orphans.length + '件(出題・評価の対象外)<button type="button" class="srs-link" data-srs-remove-orphans>まとめて解除</button></div>';
    h += '<h3 class="srs-h3">保存した表現 ' + m.items.length + '件</h3>';
    m.items.forEach(function (it) {
      var orph = m.orphanKeys[it.key];
      h += '<div class="kpi srs-row' + (orph ? ' srs-orph' : '') + '" data-srs-row="' + esc(it.key) + '"><b class="srs-rowen">' + esc(it.en) + '</b>' +
        '<button type="button" class="save on" data-srs-unsave="' + esc(it.key) + '">' + (orph ? '解除' : '保存済(解除)') + '</button>' +
        '<span class="m">' + esc(LVNAME[it.level] || it.level) + (orph ? ' / 元データが見つかりません' : ' / 次回 ' + (it.state === 'new' ? '未学習' : esc(it.due))) + '</span></div>';
    });
    return h + '</section>';
  }
  function sessionHeader(s) { return '<div class="srs-prog" data-srs-progress="' + s.remaining + '">今日の残り <b>' + s.remaining + '</b>件<button type="button" class="srs-link" data-srs-end>ここで終了</button></div>'; }
  var SPK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9v6h4l5 4V5L7 9z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M18 6a8.5 8.5 0 0 1 0 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
  /* WUI4 改善②: スピーカー再生ボタン。音声の有無は resolved 項目(保存key=slug|level|表現 → 同レベルの article.json 項目 → audio)で決まる。無ければ無効表示(別音声で代替しない) */
  function spkHtml(en, has) {
    return has ? '<button type="button" class="srs-spk" data-srs-play aria-label="' + esc(en) + ' の英語音声を再生">' + SPK + '</button>'
      : '<button type="button" class="srs-spk" disabled aria-disabled="true" data-srs-noaudio aria-label="音声なし" title="この表現の音声はありません">' + SPK + '</button>';
  }
  function enRow(it, has) { return '<div class="srs-enrow"><div class="srs-en len-' + enLen(it.en) + '" data-srs-en>' + esc(it.en) + '</div>' + spkHtml(it.en, has) + '</div>'; }
  function enLen(en) { var n = String(en || '').length; return n <= 12 ? 's' : n <= 28 ? 'm' : 'l'; }   // WUG2: 表示サイズ階層のみ(出題内容・保存・スケジュールとは無関係)
  function askHtml(s, it, notice, has) {
    return '<section class="srs-sess" data-srs-view="ask" data-srs-key="' + esc(it.key) + '">' + sessionHeader(s) + (notice ? '<div class="srs-note" data-srs-notice>' + esc(notice) + '</div>' : '') +
      '<div class="srs-body"><div class="srs-q">' +
      enRow(it, has) + '</div></div>' +   // WUG A-6: 記事タイトル/出典は出題画面に表示しない(it.title は内部データとして保存・参照関係は不変)
      '<div class="srs-bar srs-askbar"><button type="button" class="bigbtn srs-show" data-srs-show>答えを見る</button></div></section>';   // WUG2 改善③: 「答えを見る」は下部固定(mini/nav直上)。出題語は上部で目立たせ、下に考える余白
  }
  function answerHtml(s, it, cardHtml, pv, has) {
    var btns = ['again', 'hard', 'good', 'easy'].map(function (g) {
      return '<button type="button" class="srs-g srs-g-' + g + '" data-srs-grade="' + g + '"><span class="srs-gl">' + GLABEL[g] + '</span><span class="srs-gs">' + esc(pv[g].label) + '</span></button>';
    }).join('');
    return '<section class="srs-sess" data-srs-view="answer" data-srs-key="' + esc(it.key) + '">' + sessionHeader(s) +
      '<div class="srs-body"><div class="srs-q">' + enRow(it, has) + '</div>' +
      '<div class="srs-card" data-srs-card>' + cardHtml + '</div></div><div class="srs-bar srs-grades" data-srs-grades>' + btns + '</div></section>';
  }
  function doneHtml(sum, notice) {
    return '<section class="srs-done" data-srs-view="done"><h2 class="srs-h">おつかれさまでした</h2>' + (notice ? '<div class="srs-note" data-srs-notice>' + esc(notice) + '</div>' : '') + '<div class="srs-today" data-srs-done-count="' + sum.n + '"><b>' + sum.n + '回 評価しました</b></div>' +
      '<div class="srs-sub">' + ['again', 'hard', 'good', 'easy'].map(function (g) { return GLABEL[g] + ' ' + sum.by[g]; }).join(' / ') + '</div>' +
      '<button type="button" class="bigbtn" data-srs-home>復習帳に戻る</button></section>';
  }

  /* ---------- コントローラ ---------- */
  /* deps: { SRS, store, hasArticle(slug)->bool, loadArticle(slug)->Promise<art>, bases(slug)->{baseV,baseK}, lookup?, render?, now?, rng?, onChange?, saved? } */
  function create(deps) {
    var SRS = deps.SRS, store = deps.store, nowFn = deps.now || Date.now, el = null, off = null;
    var lookup = deps.lookup || defaultLookup, render = deps.render || defaultRender;
    var V = { phase: 'home', status: {}, resolved: {}, sess: null, sum: null, notice: '', busy: false };

    function today() { return SRS.todayJST(nowFn()); }
    function setHtml(h) { if (el) el.innerHTML = h; }

    /* キュー構築前に対象記事のarticle.jsonをまとめて読込(M6) */
    function prepare() {
      var st = store.load(), items = st.status === 'ok' ? st.state.items : [], slugs = {};
      items.forEach(function (i) { slugs[i.slug] = 1; });
      V.status = {}; V.resolved = {};
      var arts = {}, jobs = Object.keys(slugs).map(function (slug) {
        if (deps.hasArticle && !deps.hasArticle(slug)) { arts[slug] = { orphan: true }; return Promise.resolve(); }
        return Promise.resolve().then(function () { return deps.loadArticle(slug); }).then(function (a) { arts[slug] = { art: a }; }, function () { arts[slug] = { net: true }; });
      });
      return Promise.all(jobs).then(function () {
        items.forEach(function (i) {
          var a = arts[i.slug];
          if (a.net) { V.status[i.key] = 'netfail'; return; }
          if (a.orphan) { V.status[i.key] = 'orphan'; return; }
          var pwi = lookup(a.art, i.level, i.en, deps.bases ? deps.bases(i.slug) : undefined);   // 保存レベルのみ。別レベル代用禁止
          if (!pwi) { V.status[i.key] = 'orphan'; return; }
          V.status[i.key] = 'ok'; V.resolved[i.key] = pwi;
        });
        return { st: st, items: items };
      });
    }
    function homeModel(p) {
      var items = p.items, t = today(), bq = SRS.buildQueue(items, t, { rng: deps.rng, newPerDay: p.st.status === 'ok' ? p.st.state.settings.newPerDay : undefined });
      var part = SRS.partitionByStatus(bq.queue, function (i) { return V.status[i.key]; });
      var orphanKeys = {}, netfail = 0; items.forEach(function (i) { if (V.status[i.key] === 'orphan') orphanKeys[i.key] = 1; if (V.status[i.key] === 'netfail') netfail++; });
      var future = items.filter(function (i) { return i.state !== 'new' && i.due > t && V.status[i.key] !== 'orphan'; }).map(function (i) { return i.due; }).sort()[0];
      var newShown = part.queue.filter(function (i) { return i.state === 'new'; }).length;
      return { storeStatus: p.st.status, items: items, queue: part.queue, orphans: items.filter(function (i) { return orphanKeys[i.key]; }), orphanKeys: orphanKeys, netfail: netfail, nextDue: future,
        counts: { remaining: part.queue.length, newShown: newShown, newDeferred: bq.counts.newDeferred } };
    }
    function showHome() {
      V.phase = 'home'; stopAudio();
      return prepare().then(function (p) { V.model = homeModel(p); setHtml(homeHtml(V.model)); if (deps.onChange) deps.onChange('home'); });
    }
    function startSession() {
      V.sess = { queue: V.model.queue.slice(), total: V.model.queue.length, remaining: V.model.queue.length }; V.sum = { n: 0, by: { again: 0, hard: 0, good: 0, easy: 0 } }; V.notice = '';
      showAsk();
    }
    function hasAudio(it) { var x = it && V.resolved[it.key]; return !!(x && x.audio && x.audio.url); }
    function stopAudio() { if (deps.stopAudio) deps.stopAudio(); }
    function cur() { return V.sess && V.sess.queue[0]; }
    function showAsk() {
      if (!cur()) { V.phase = 'done'; setHtml(doneHtml(V.sum, V.notice)); V.notice = ''; if (deps.onChange) deps.onChange('done'); return; }
      V.phase = 'ask'; V.sess.remaining = V.sess.queue.length; setHtml(askHtml(V.sess, cur(), V.notice, hasAudio(cur()))); V.notice = '';
      if (deps.onChange) deps.onChange('ask');
    }
    function showAnswer() {
      var it = cur(); if (!it) return; V.phase = 'answer';
      setHtml(answerHtml(V.sess, it, render(V.resolved[it.key]), SRS.preview(it, today()), hasAudio(it))); if (deps.onChange) deps.onChange('answer');
    }
    function grade(g) {
      var it = cur(); if (!it || V.phase !== 'answer') return;
      stopAudio();
      var r = store.grade(it.key, g, it.history.length);   // 評価直前に再読込(R5)
      V.sess.queue.shift();
      if (!r.ok) { V.notice = r.reason === 'conflict' ? '別のタブで評価済みのため、この項目は飛ばしました' : r.reason === 'missing' ? '別のタブで解除されたため、この項目は飛ばしました' : '保存に失敗しました(この項目は評価されていません)'; return showAsk(); }
      V.sum.n++; V.sum.by[g]++;
      var n = r.item;
      if (n.due <= today() && (n.state === 'learning' || n.state === 'relearning')) V.sess.queue.splice(SRS.reinsertIndex(V.sess.queue.length), 0, n);   // Againは約10件後に同日再出題
      showAsk();
    }
    function onClick(e) {
      var t = e.target, b;
      if (!t || !t.closest) return;
      if ((b = t.closest('[data-srs-start]'))) return startSession();
      if ((b = t.closest('[data-srs-play]'))) { var pi = cur(), px = pi && V.resolved[pi.key]; if (px && px.audio && px.audio.url && deps.playAudio) deps.playAudio(px.audio); return; }   // 評価・答え表示・スケジュールには触れない(再生のみ)
      if ((b = t.closest('[data-srs-noaudio]'))) return;
      if ((b = t.closest('[data-srs-show]'))) return showAnswer();
      if ((b = t.closest('[data-srs-grade]'))) return grade(b.getAttribute('data-srs-grade'));
      if ((b = t.closest('[data-srs-unsave]'))) { store.remove(b.getAttribute('data-srs-unsave')); if (deps.saved && deps.saved.onRemoved) deps.saved.onRemoved(); return showHome(); }
      if ((b = t.closest('[data-srs-remove-orphans]'))) { store.removeMany(V.model.orphans.map(function (i) { return i.key; })); return showHome(); }
      if ((b = t.closest('[data-srs-end]')) || (b = t.closest('[data-srs-home]')) || (b = t.closest('[data-srs-retry]'))) return showHome();
      if ((b = t.closest('[data-srs-reset]'))) { store.resetAfterFailure(); return showHome(); }
    }
    return {
      mount: function (container) {
        el = container; el.addEventListener('click', onClick);
        if (deps.win && store.attachStorage) off = store.attachStorage(deps.win, function () { if (V.phase === 'home') showHome(); });   // 他タブ変更: ホームは再描画、出題中は評価直前の再読込で吸収
        return showHome();
      },
      destroy: function () { if (el) el.removeEventListener('click', onClick); if (off) off(); el = null; },
      refresh: showHome, _state: V
    };
  }
  return { create: create, homeHtml: homeHtml, askHtml: askHtml, answerHtml: answerHtml, doneHtml: doneHtml, stubLookup: stubLookup, stubRender: stubRender, esc: esc };
});
