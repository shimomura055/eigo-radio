/* eigo-radio WebApp UI 試作(WUR 委任_02c S2): Word/Phrase吹き出しの純関数モジュール(DOM保存・音声は持たない)。
   1) glScore: 本番側 er135_enduser_page_01._gl_score と同じ対応度(文字列比と語幹列比の大きい方。difflib.SequenceMatcher.ratio相当)
   2) checkLevel: 本文の下線span(lk1/lk2/lk3, data-hl)と part.glossary[] の対応付け+内容照合(M3)
      手順=本番側 build_glossary と同じ(レベル全体で同一data-hlの重複を除外・初出順)。不一致パートは ok=false(語クリックを文クリックへ降格)
   3) layout: 吹き出しの配置計算(上/下/代替表示)。pwcard.js は読み取りのみ(編集しない) */
(function (root) {
  'use strict';
  /* ---- difflib.SequenceMatcher.ratio 相当(autojunkなし: 対象は短い文字列/語列) ---- */
  function longest(a, b, alo, ahi, blo, bhi) {   // 最長一致(同長なら a側が最小i、次に b側が最小j) = difflib.find_longest_match
    var bi = alo, bj = blo, bs = 0, j2len = {}, i, j, k, nj;
    var b2j = {};
    for (j = blo; j < bhi; j++) { (b2j[b[j]] = b2j[b[j]] || []).push(j); }
    for (i = alo; i < ahi; i++) {
      nj = {};
      var js = b2j[a[i]] || [];
      for (var q = 0; q < js.length; q++) {
        j = js[q];
        k = (j2len[j - 1] || 0) + 1; nj[j] = k;
        if (k > bs) { bi = i - k + 1; bj = j - k + 1; bs = k; }
      }
      j2len = nj;
    }
    return [bi, bj, bs];
  }
  function matchTotal(a, b) {
    var stack = [[0, a.length, 0, b.length]], tot = 0;
    while (stack.length) {
      var t = stack.pop(), m = longest(a, b, t[0], t[1], t[2], t[3]), i = m[0], j = m[1], k = m[2];
      if (k) {
        tot += k;
        if (t[0] < i && t[2] < j) stack.push([t[0], i, t[2], j]);
        if (i + k < t[1] && j + k < t[3]) stack.push([i + k, t[1], j + k, t[3]]);
      }
    }
    return tot;
  }
  function ratio(a, b) { var n = a.length + b.length; return n ? 2 * matchTotal(a, b) / n : 1; }
  function normEn(s) { return String(s || '').toLowerCase().trim().replace(/^(the|a|an)\s+/, ''); }
  var POSS = { 'my': 1, 'your': 1, 'his': 1, 'her': 1, 'our': 1, 'their': 1, 'its': 1, "one's": 1, 'one’s': 1, "someone's": 1, 'someone’s': 1, "somebody's": 1, 'somebody’s': 1 };
  function stem(t) { if (POSS[t]) return '<p>'; return t.length > 3 ? t.replace(/(ing|ed|es|s|e)$/, '') : t; }
  function toks(s) { return (normEn(s).match(/[\p{L}\p{N}_'’]+/gu) || []).map(stem); }
  function glScore(a, b) {
    var ch = ratio(Array.from(normEn(a)), Array.from(normEn(b))), ta = toks(a), tb = toks(b);
    var tk = ta.length && tb.length ? ratio(ta, tb) : 0;
    return Math.max(ch, tk);
  }
  /* ECUI 委任_05(M3是正): er135 _gl_score の部分列救済(FYAI 委任_04・FX3R 委任_05・FZLT 委任_02)と同じ規則の移植。ビルド側が対応とみなす下線<->見出しをM3ガードも一致とみなす
     (見出し語が下線の連続部分列/途中の不定代名詞<r>を除いた連続部分列/<r>区切り断片が先頭から順に出現[間1〜4語]。2語以上のみ。1語見出しは救済しない。閾値0.8の式・count/ja/vi検査は不変)。
     語形吸収表(_IRREG/_POSS/_REF)は er135_enduser_page_01.py から機械生成(手書き転記なし)。 */
  var G_IRREG = {"spoke":"speak","spoken":"speak","went":"go","gone":"go","came":"come","took":"take","taken":"take","gave":"give","given":"give","got":"get","gotten":"get","made":"make","saw":"see","seen":"see","knew":"know","known":"know","thought":"think","told":"tell","found":"find","felt":"feel","kept":"keep","left":"leave","held":"hold","brought":"bring","began":"begin","begun":"begin","ran":"run","wrote":"write","written":"write","chose":"choose","chosen":"choose","drew":"draw","drawn":"draw","fell":"fall","fallen":"fall","led":"lead","met":"meet","paid":"pay","put":"put","read":"read","said":"say","sold":"sell","sent":"send","set":"set","sat":"sit","stood":"stand","understood":"understand","wore":"wear","worn":"wear","won":"win","lost":"lose","built":"build","bought":"buy","caught":"catch","taught":"teach","heard":"hear","meant":"mean","spent":"spend","lent":"lend","broke":"break","broken":"break","forgot":"forget","forgotten":"forget","rose":"rise","risen":"rise","threw":"throw","thrown":"throw","grew":"grow","grown":"grow","showed":"show","shown":"show","hid":"hide","hidden":"hide","fed":"feed","ate":"eat","eaten":"eat","drank":"drink","drunk":"drink","swam":"swim","sang":"sing","sung":"sing","flew":"fly","flown":"fly","slept":"sleep","dealt":"deal","stuck":"stick","struck":"strike","shot":"shoot","hung":"hang","dug":"dig","bent":"bend","lit":"light","woke":"wake","woken":"wake","getting":"get","putting":"put","setting":"set","letting":"let","running":"run","sitting":"sit","stopping":"stop","cutting":"cut","hitting":"hit","beginning":"begin","forgetting":"forget","shutting":"shut","swimming":"swim","winning":"win","planning":"plan"}, G_POSS = ["her", "herself", "himself", "his", "its", "itself", "my", "myself", "one's", "oneself", "one’s", "our", "ourselves", "somebody's", "somebody’s", "someone's", "someone’s", "their", "themselves", "your", "yourself", "yourselves"], G_REF = ["anybody", "anyone", "anything", "everybody", "everyone", "everything", "him", "it", "me", "one", "somebody", "someone", "something", "them", "us", "you"];
  function gstem(t) {
    t = Object.prototype.hasOwnProperty.call(G_IRREG, t) ? G_IRREG[t] : t;
    if (G_POSS.indexOf(t) >= 0) return '<p>';
    if (G_REF.indexOf(t) >= 0) return '<r>';
    return t.length > 3 ? t.replace(/(ing|ed|es|s|e)$/, '') : t;
  }
  function gtoks(s) { return (normEn(s).match(/[\p{L}\p{N}_'’]+/gu) || []).map(gstem); }
  function eqSeq(x, y) { if (x.length !== y.length) return false; for (var i = 0; i < x.length; i++) if (x[i] !== y[i]) return false; return true; }
  function hasSub(long_, short) {
    for (var i = 0; i + short.length <= long_.length; i++) { var k = 0; while (k < short.length && long_[i + k] === short[k]) k++; if (k === short.length) return true; }
    return false;
  }
  function glRescue(a, b) {
    var ta = gtoks(a), tb = gtoks(b), short = ta.length <= tb.length ? ta : tb, long_ = ta.length <= tb.length ? tb : ta;
    if (short.length >= 2 && hasSub(long_, short)) return true;
    if (tb.slice(1, -1).indexOf('<r>') >= 0) {
      var sa = ta.filter(function (t) { return t !== '<r>'; }), sb = tb.filter(function (t) { return t !== '<r>'; });
      if (sb.length >= 2 && hasSub(sa, sb)) return true;
      var segs = [], cur = [];
      tb.forEach(function (t) { if (t === '<r>') { if (cur.length) segs.push(cur); cur = []; } else cur.push(t); });
      if (cur.length) segs.push(cur);
      var tot = segs.reduce(function (n, frag) { return n + frag.length; }, 0);
      if (segs.length >= 2 && tot >= 2 && eqSeq(ta.slice(0, segs[0].length), segs[0])) {
        var pos = segs[0].length, ok = true;
        for (var s = 1; s < segs.length && ok; s++) {
          var frag = segs[s], hit = -1, hi = Math.min(ta.length - frag.length, pos + 4);
          for (var i = pos + 1; i <= hi; i++) { if (eqSeq(ta.slice(i, i + frag.length), frag)) { hit = i; break; } }
          if (hit < 0) ok = false; else pos = hit + frag.length;
        }
        if (ok) return true;
      }
    }
    return false;
  }
  var LKSEL = 'span.lk1,span.lk2,span.lk3,strong.lk1,strong.lk2,strong.lk3';
  function lkOf(el) { return el.classList.contains('lk1') ? 'lk1' : el.classList.contains('lk2') ? 'lk2' : 'lk3'; }
  function plain(html) { var d = document.createElement('div'); d.innerHTML = html || ''; return d.textContent; }
  /* L = article.json の levels[lv]。戻り値 {byKey:{data-hl: entry}, parts:[{pi,ok,reasons,n,entries}], okParts, ngParts}
     entry={key,lk,form,gl:{en,ja,vi},vi,ok,pi,idx} */
  function checkLevel(L) {
    var vocab = L.vocab || [], quotes = vocab.map(function (v) {
      var f = (v.fields || []).filter(function (x) { return x.label === '本文の英文'; })[0];
      return plain(f ? f.html : '').toLowerCase();
    });
    var seen = {}, byKey = {}, parts = [];
    (L.parts || []).forEach(function (p, pi) {
      var cand = [];
      (p.paragraphs || []).forEach(function (para) {
        para.forEach(function (s) {
          var d = document.createElement('div'); d.innerHTML = s.html || '';
          Array.prototype.forEach.call(d.querySelectorAll(LKSEL), function (el) {
            var key = el.getAttribute('data-hl') || '';
            if (seen[key]) return;
            seen[key] = 1; cand.push({ key: key, lk: lkOf(el), form: el.textContent.trim() });
          });
        });
      });
      var gl = p.glossary || [];
      if (!cand.length && !gl.length) return;
      var reasons = [];
      if (cand.length !== gl.length) reasons.push('count ' + cand.length + '!=' + gl.length);
      else cand.forEach(function (c, i) {
        var g = gl[i], vi = g.vi;
        if (!g.ja) reasons.push(c.form + ': ja empty');
        if (c.lk === 'lk1' || c.lk === 'lk2') {
          if (vi == null || vi < 0 || vi >= vocab.length) reasons.push(c.form + ': vi missing');
          else if (quotes[vi].indexOf(c.form.toLowerCase()) < 0) reasons.push(c.form + ': not in vocab[' + vi + '] quote');
        } else {
          if (vi != null) reasons.push(c.form + ': lk3 has vi');
          else if (glScore(c.form, g.en || '') < 0.8 && !glRescue(c.form, g.en || '')) reasons.push(c.form + ': lk3 score<0.8');
        }
      });
      var ok = !reasons.length, entries = cand.map(function (c, i) {
        var e = { key: c.key, lk: c.lk, form: c.form, gl: gl[i] || null, vi: gl[i] ? gl[i].vi : null, ok: ok, pi: pi, idx: i };
        byKey[c.key] = e; return e;
      });
      parts.push({ pi: pi, key: p.key, ok: ok, reasons: reasons, n: cand.length, entries: entries });
    });
    return { byKey: byKey, parts: parts, okParts: parts.filter(function (x) { return x.ok; }).length, ngParts: parts.filter(function (x) { return !x.ok; }).length };
  }
  /* 吹き出し配置。rects=語のclientRects(1行ごと)[{left,top,right,bottom}], band={top,bottom}(自由帯域), vw=表示幅, bw/bh=吹き出しの希望寸法
     戻り値 {mode:'above'|'below'|'alt', left, top, width, maxH, arrowX}。帯域高<MINBAND、または上下とも MINFIT 未満なら 'alt'(キャプチャ枠へ意味行を代替表示) */
  var MINBAND = 100, MINFIT = 90, GAP = 8, EDGE = 8;
  function layout(rects, band, vw, bw, bh) {
    var bandH = band.bottom - band.top;
    if (bandH < MINBAND || !rects.length) return { mode: 'alt' };
    var first = rects[0], last = rects[rects.length - 1];
    var above = first.top - band.top - GAP, below = band.bottom - last.bottom - GAP;
    var w = Math.min(bw, vw - 2 * EDGE), cx = (first.left + first.right) / 2;
    if (rects.length > 1) cx = (rects[0].left + rects[0].right) / 2;
    var left = Math.max(EDGE, Math.min(cx - w / 2, vw - EDGE - w)), arrowX = Math.max(14, Math.min(w - 14, cx - left));
    var mode, maxH;
    if (bh <= above) { mode = 'above'; maxH = bh; }
    else if (bh <= below) { mode = 'below'; maxH = bh; }
    else if (Math.max(above, below) >= MINFIT) { mode = above >= below ? 'above' : 'below'; maxH = Math.max(above, below); }
    else return { mode: 'alt' };
    var h = Math.min(bh, maxH), top = mode === 'above' ? first.top - GAP - h : last.bottom + GAP;
    return { mode: mode, left: left, top: top, width: w, maxH: maxH, arrowX: arrowX };
  }
  root.WURBubble = { glScore: glScore, glRescue: glRescue, checkLevel: checkLevel, layout: layout, MINBAND: MINBAND };
})(window);
