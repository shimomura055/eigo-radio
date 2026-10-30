/* English Your Way 記事視聴ページ(End User向け。静的・外部ライブラリなし)。
   データ: data/article.json と data/sync_<level>.json(er135_enduser_page_01.pyが公開dirの最終dev index.htmlから生成)。
   音声: 既存mp3を相対パス(../)で参照(コピー・再生成なし)。
   文単位ハイライト: 各文は <span class="sent" data-sid="...">、同期データ(sentences:[{sid,start,end}], 全編内の秒)で点灯する。 */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var A = $('aud'), Q = new URLSearchParams(location.search);
  var art = null, lv = null, L = null, parts = [];
  var mode = 'full', curIdx = null, kpEnd = null, vocabI = null, resumeAt = null;   // 'full'(全体音声) / 'kp'(Key Phrase英語区間のみ) / 'vocab'(Vocabulary項目の単体音声)
  var sync = [], syncKind = 'none', sentEls = {}, activeSid = null;
  var raf = 0, lastUserScroll = 0;
  var LEVEL_NAME = { std: 'Standard', adv: 'Advanced' };
  var selectedSid = null, selTime = 0;   // rev01-h: 英文クリックの選択(停止中・一時停止中のみ保持。再生が始まる/位置操作[seek・±10秒等]で解除)
  var jgEls = {}, sidToG = {}, activeG = null, jaHold = null;   // rev01-f: 英語文と日本語訳の連動(ja_align)
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
  function trHtml(p) {   // 英語本文の直後に日本語訳(承認済み日本語原稿の対応段落のみ。無いブロックは出さない)
    if (!p.ja || !p.ja.length) return '';
    return '<div class="tr" lang="ja" data-src="' + esc(p.ja_source) + '"><span class="trtag">日本語訳</span>' +
      p.ja.map(function (t, k) { return '<p>' + jaHtml(p, k, t) + '</p>'; }).join('') + '</div>';
  }
  /* rev01-f: 英語文と日本語訳の連動。ja_align=[{g,sids,ja:[段落,開始,終了]|null}]。オフセットはJSのsubstringと同じUTF-16 code unit(正規化しない)。
     訳本文は書き換えず、群の範囲を<span class="jhl" data-jg>で包むだけ。ja_align無し/不正(範囲外・重なり)は従来どおりの素のテキスト。 */
  function jaHtml(p, k, t) {
    var al = p.ja_align;
    if (!al || !al.length) return esc(t);
    var gs = al.filter(function (g) { return g.ja && g.ja[0] === k && g.ja[1] >= 0 && g.ja[1] < g.ja[2] && g.ja[2] <= t.length; })
      .sort(function (x, y) { return x.ja[1] - y.ja[1]; });
    var out = '', pos = 0;
    for (var i = 0; i < gs.length; i++) {
      var a = gs[i].ja[1], b = gs[i].ja[2];
      if (a < pos) return esc(t);
      out += esc(t.substring(pos, a)) + '<span class="jhl" data-jg="' + p.idx + ':' + gs[i].g + '">' + esc(t.substring(a, b)) + '</span>';
      pos = b;
    }
    return out + esc(t.substring(pos));
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
      out += card('Preview', (ja ? '<div class="jp">' + sentHtml(p) + '</div>' : sentHtml(p)) + trHtml(p), { part: p.idx, btn: btns(p) });
    });
    var kps = by('kp');
    if (kps.length) {
      var hdr = kps[0].kp_header || ['英語', '意味'];
      var body = '<div class="kp">' + kps.map(function (p) {
        return p.kp.map(function (k) {
          return '<div class="kpitem" data-part="' + p.idx + '"><div><span class="th">' + esc(hdr[0]) + '</span><b>' + esc(k.en) + '</b></div>' +
                 '<div class="def"><span class="th">' + esc(hdr[1] || '') + '</span>' + esc(k.text) + (k.text2 ? '<span class="th th2">' + esc(hdr[2] || '') + '</span>' + esc(k.text2) : '') + '</div>' +
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
        return '<details class="vi" id="vi-' + lv + '-' + vi + '"' + (wide ? ' open' : '') + '><summary><b class="vh">' + esc(it.heading) + '</b><span class="vm">' + mean + '</span>' + (it.audio ? '<button type="button" class="seek part vplay" data-act="vocab" data-i="' + vi + '" aria-label="' + esc(it.heading) + ' の英語音声を再生">▶ 英語音声</button>' : '') + '</summary><dl>' +
          it.fields.map(function (f) { return '<dt>' + esc(f.label) + '</dt><dd>' + f.html + '</dd>'; }).join('') + '</dl></details>';
      }).join(''), { label: 'WORDS', id: 'vocab', cls: 'blk-vocab' });
    }
    if (L.grammar && L.grammar.length) {   // 採用0件ならコーナーごと非表示
      out += card('Grammar & Sentence Structure', L.grammar.map(function (it) {
        return '<div class="gr"><dl>' + it.fields.map(function (f) { return '<dt>' + esc(f.label) + '</dt><dd>' + f.html + '</dd>'; }).join('') + '</dl></div>';
      }).join(''), { label: 'GRAMMAR', id: 'grammar', cls: 'blk-grammar' });
    }
    if (L.nuance && L.nuance.length) {   // ニュアンス解説(採用0件ならコーナーごと非表示)
      out += card('ニュアンス解説', L.nuance.map(function (it) {
        return '<div class="gr"><h4 class="nh">' + esc(it.heading) + '</h4><dl>' + it.fields.map(function (f) { return '<dt>' + esc(f.label) + '</dt><dd>' + f.html + '</dd>'; }).join('') + '</dl></div>';
      }).join(''), { label: 'NUANCE', id: 'nuance', cls: 'blk-nuance' });
    }
    $('content').innerHTML = out;
    emphasize();
    sentEls = {};
    Array.prototype.forEach.call(document.querySelectorAll('[data-sid]'), function (e) { sentEls[e.dataset.sid] = e; });
    jgEls = {}; sidToG = {}; activeG = null; jaHold = null; selectedSid = null;
    Array.prototype.forEach.call(document.querySelectorAll('.jhl'), function (e) { (jgEls[e.dataset.jg] = jgEls[e.dataset.jg] || []).push(e); });
    parts.forEach(function (p) { (p.ja_align || []).forEach(function (g) { if (g.ja && jgEls[p.idx + ':' + g.g]) g.sids.forEach(function (s) { sidToG[s] = p.idx + ':' + g.g; }); }); });
  }

  /* ---------- rev01-e: 学習ブロック引用英文内の解説対象語句を太字化(表示時のみ。データの英文は不変・記事非依存) ---------- */
  var IRR = (function () {
    var g = 'get got gotten|give gave given|hold held|go went gone|take took taken|make made|come came|do did done|have has had|be is are was were been am|say said|see saw seen|know knew known|think thought|feel felt|leave left|keep kept|find found|tell told|bring brought|buy bought|run ran|write wrote written|speak spoke spoken|break broke broken|choose chose chosen|fall fell fallen|grow grew grown|let|put|cut|set|read|lose lost|mean meant|meet met|pay paid|sell sold|send sent|sit sat|stand stood|win won|begin began begun|catch caught|teach taught|forget forgot forgotten|arise arose arisen|awake awoke awoken|bear bore borne|beat beat beaten|bend bent|bet|bind bound|bite bit bitten|bleed bled|blow blew blown|breed bred|build built|burn burnt|burst|cast|cling clung|creep crept|deal dealt|dig dug|draw drew drawn|dream dreamt|drink drank drunk|drive drove driven|eat ate eaten|feed fed|fight fought|flee fled|fling flung|fly flew flown|forbid forbade forbidden|forgive forgave forgiven|freeze froze frozen|hang hung|hear heard|hide hid hidden|hit|hurt|kneel knelt|lay laid|lead led|lean leant|leap leapt|lend lent|lie lay lain|light lit|ride rode ridden|ring rang rung|rise rose risen|seek sought|shake shook shaken|shine shone|shoot shot|show showed shown|shrink shrank shrunk|shut|sing sang sung|sink sank sunk sunken|sleep slept|slide slid|speed sped|spend spent|spin spun|spit spat|split|spread|spring sprang sprung|steal stole stolen|stick stuck|sting stung|strike struck stricken|swear swore sworn|sweep swept|swim swam swum|swing swung|tear tore torn|throw threw thrown|understand understood|wake woke woken|wear wore worn|weave wove woven|weep wept|wind wound|withdraw withdrew withdrawn|undergo underwent undergone|overcome overcame|become became|forecast|rebuild rebuilt|retell retold|rewrite rewrote rewritten|upset|bid|broadcast|shed|sew sewed sewn|swell swelled swollen|thrust|tread trod trodden|stride strode stridden|mistake mistook mistaken|overtake overtook overtaken|undertake undertook undertaken|outgrow outgrew outgrown|withhold withheld|uphold upheld|lead led'.split('|'), m = {};
    g.forEach(function (x) { var w = x.split(' '); w.forEach(function (a) { m[a] = m[a] ? m[a].concat(w) : w; }); });
    return m;
  })();
  var PH = { "one's": 1, "someone's": 1, "sb's": 1, "somebody's": 1, one: 1, someone: 1, somebody: 1, something: 1, sth: 1, sb: 1, oneself: 1, etc: 1 };
  function toks(s) { var r = [], re = /[A-Za-z0-9]+(?:['’][A-Za-z]+)?/g, m; while ((m = re.exec(s))) r.push({ w: m[0].toLowerCase().replace(/’/g, "'"), s: m.index, e: m.index + m[0].length }); return r; }
  function forms(w) {
    if (IRR[w]) {   // 不規則動詞: 原形・過去形・過去分詞に加え、3単現(-s/-es)・-ing形(語尾e脱落・子音重ね)も候補にする
      var ex = IRR[w].slice();
      IRR[w].forEach(function (x) {
        ex.push(x + 's', x + 'es', x + 'ing');
        if (/e$/.test(x)) ex.push(x.slice(0, -1) + 'ing');
        if (!/[aeiou]$/.test(x) && x.length < 6) ex.push(x + x.slice(-1) + 'ing');
      });
      return ex;
    }
    var f = [w]; if (w.length < 3) return f;
    var last = w.charAt(w.length - 1), pre = w.slice(0, -1), cons = !/[aeiou]/.test(last);
    f.push(w + 's', w + 'es', w + 'ed', w + 'd', w + 'ing', w + 'er', w + 'est');
    if (last === 'e') f.push(pre + 'ing');
    if (last === 'y' && !/[aeiou]/.test(w.charAt(w.length - 2))) f.push(pre + 'ies', pre + 'ied', pre + 'ier', pre + 'iest');
    if (cons && /[aeiou]/.test(w.charAt(w.length - 2)) && w.length < 7) f.push(w + last + 'ed', w + last + 'ing', w + last + 'er');
    return f;
  }
  /* heading → 本文tokens上の一意な一致範囲(wildcard=プレースホルダ。空配列=特定不可)。{ranges:[[s,e]..], n:一致数} */
  function matchPhrase(heading, text, allowWild) {
    var ht = toks(heading).map(function (t) { return { w: t.w, ph: allowWild && !!PH[t.w], f: null }; });
    if (!ht.length || ht.every(function (t) { return t.ph; })) return { n: 0, ranges: [] };
    ht.forEach(function (t) { if (!t.ph) t.f = forms(t.w); });
    var qt = toks(text), hits = [];
    function rec(hi, qi, acc) {
      if (hi === ht.length) { hits.push(acc); return; }
      var h = ht[hi];
      if (h.ph) { for (var n = 1; n <= 3; n++) if (qi + n <= qt.length) rec(hi + 1, qi + n, acc); return; }
      if (qi < qt.length && h.f.indexOf(qt[qi].w.replace(/'s$/, '')) >= 0) rec(hi + 1, qi + 1, acc.concat([[qt[qi].s, qt[qi].e]]));
    }
    for (var i = 0; i < qt.length; i++) rec(0, i, []);
    var seen = {}, uniq = hits.filter(function (h) { var k = h.map(function (r) { return r[0]; }).join(','); if (seen[k]) return false; seen[k] = 1; return true; });
    if (uniq.length !== 1) return { n: uniq.length, ranges: [] };
    var out = [], cur = null, prevEnd = -1;   // 隣接トークン(間が空白のみ)は1つの太字にまとめる
    uniq[0].forEach(function (r) { if (cur && /^\s*$/.test(text.slice(prevEnd, r[0]))) cur[1] = r[1]; else { cur = [r[0], r[1]]; out.push(cur); } prevEnd = r[1]; });
    return { n: 1, ranges: out };
  }
  function wrapRanges(dd, ranges) {
    var nodes = [], w = document.createTreeWalker(dd, NodeFilter.SHOW_TEXT, null), n, off = 0;
    while ((n = w.nextNode())) { nodes.push({ n: n, s: off, e: off + n.nodeValue.length }); off += n.nodeValue.length; }
    ranges.slice().reverse().forEach(function (r) {
      nodes.slice().reverse().forEach(function (x) {
        var a = Math.max(r[0], x.s), b = Math.min(r[1], x.e); if (a >= b) return;
        var t = x.n, mid = (a > x.s) ? t.splitText(a - x.s) : t; if (b < x.e) mid.splitText(b - a);
        var st = document.createElement('strong'); st.className = 'target-term'; mid.parentNode.insertBefore(st, mid); st.appendChild(mid);
      });
    });
  }
  function ddOf(box, label) { var dts = box.querySelectorAll('dt'); for (var i = 0; i < dts.length; i++) if (dts[i].textContent === label) return dts[i].nextElementSibling; return null; }
  function emphasize() {
    var stats = { vocab: [], nuance: [], grammar: [] };
    function item(kind, box, heading, qLabel) {
      var dd = ddOf(box, qLabel), text = dd ? dd.textContent : '', r = matchPhrase(heading, text, true);
      if (dd && r.ranges.length) wrapRanges(dd, r.ranges);
      stats[kind].push({ heading: heading, bold: r.ranges.length ? dd.querySelectorAll('strong.target-term').length : 0, matches: r.n, reason: r.ranges.length ? null : (r.n ? 'multiple_candidates' : 'no_match') });
    }
    Array.prototype.forEach.call(document.querySelectorAll('#vocab details.vi'), function (b) { item('vocab', b, b.querySelector('.vh').textContent, '本文の英文'); });
    Array.prototype.forEach.call(document.querySelectorAll('#nuance .gr'), function (b) { item('nuance', b, b.querySelector('.nh').textContent, '本文の英文'); });
    Array.prototype.forEach.call(document.querySelectorAll('#grammar .gr'), function (b) {   // 文法: 解説本文の「…」内の英語2語以上の語句のうち、引用英文に一意に一致する最初のもの
      var dd = ddOf(b, '対象となる本文英文'), ex = ddOf(b, '文法・構文の仕組み'), text = dd ? dd.textContent : '', res = null, reason = 'no_english_phrase_in_explanation', heads = [], re = /「([^」]+)」/g, m;
      while (ex && (m = re.exec(ex.textContent))) { var c = m[1].trim(); if (/^[A-Za-z][A-Za-z0-9'’,\- ]*$/.test(c) && toks(c).length >= 2) heads.push(c); }
      if (heads.length) reason = 'no_unique_match';
      for (var i = 0; i < heads.length && !res; i++) { var r = matchPhrase(heads[i], text, false); if (r.ranges.length) res = { h: heads[i], r: r }; else if (r.n > 1) reason = 'multiple_candidates'; }
      if (res) wrapRanges(dd, res.r.ranges);
      stats.grammar.push({ heading: res ? res.h : null, bold: res ? 1 : 0, reason: res ? null : reason });
    });
    window.__EMPH = stats; window.__matchPhrase = matchPhrase;   // 検証用の読取専用フック
  }

  /* ---------- 再生 ---------- */
  function ensureSrc(url) { if (A.src !== url) { A.src = url; A.load(); } }
  function withMeta(fn) { if (A.readyState >= 1) fn(); else A.addEventListener('loadedmetadata', function h() { A.removeEventListener('loadedmetadata', h); fn(); }); }
  function playNow() { var pr = A.play(); if (pr && pr.catch) pr.catch(function (e) { if (e.name !== 'AbortError') console.warn('play()', e.name); }); }
  function playFull(at) { selectedSid = null; mode = 'full'; curIdx = null; kpEnd = null; ensureSrc(audioUrl(L.main)); withMeta(function () { if (at != null) A.currentTime = at; playNow(); }); labels(); }
  /* Key Phrase の発音: 既存KP区間mp3(番号→英語→日本語の意味(Advは英語解説)→英語再掲)のうち、最初の英語発話の区間だけを再生し、終端で停止(音声ファイルは不変) */
  function playKp(i, k) {
    var kk = parts[i].kp[k || 0], ea = kk && kk.en_audio; if (!ea) return;
    selectedSid = null; mode = 'kp'; curIdx = i; kpEnd = ea.end; ensureSrc(audioUrl(parts[i].seg));
    withMeta(function () { A.currentTime = ea.start; playNow(); }); labels();
  }
  function playVocab(vi) {   // rev01-g: Vocabulary項目の英語音声(KPと同じ契約の単体mp3。区間指定なし)
    var it = L.vocab && L.vocab[vi], au = it && it.audio; if (!au) return;
    if (mode !== 'vocab') resumeAt = mode === 'full' ? (A.currentTime || 0) : (mode === 'kp' && curIdx != null ? parts[curIdx].start : null);
    selectedSid = null; mode = 'vocab'; vocabI = vi; curIdx = null; kpEnd = null;
    ensureSrc(new URL(au.file, location.href).href);
    withMeta(function () { A.currentTime = 0; playNow(); }); labels();
  }
  function endVocab() {   // 単体音声の終端: 停止して通し再生の状態へ戻す(自動再生しない)
    var at = resumeAt; A.pause(); mode = 'full'; vocabI = null; resumeAt = null;
    ensureSrc(audioUrl(L.main)); withMeta(function () { A.currentTime = at || 0; tick(); });
  }
  function endKp() {   // 英語区間の終端: 停止して通し再生の状態へ戻す(意味・再掲は再生されない)
    var i = curIdx; A.pause(); mode = 'full'; kpEnd = null; curIdx = null;
    ensureSrc(audioUrl(L.main)); withMeta(function () { A.currentTime = parts[i].start; tick(); });
  }
  function dur() {
    var d = mode === 'vocab' && vocabI != null ? L.vocab[vocabI].audio.dur : (mode === 'kp' && curIdx != null ? parts[curIdx].dur : L.total_sec);
    return (isFinite(A.duration) && A.duration > 0 && A.readyState >= 1) ? A.duration : d;
  }
  function gt() { return (mode === 'kp' && curIdx != null ? parts[curIdx].start : 0) + (A.currentTime || 0); }
  function labels() {
    var pi = currentPartIdx();
    $('nowLabel').textContent = (mode === 'vocab' && vocabI != null) ? ('英語音声: ' + L.vocab[vocabI].heading) : (mode === 'kp' && curIdx != null) ? ('英語音声: ' + parts[curIdx].label) : ('全体' + (pi != null && A.currentTime > 0 && parts[pi].kind !== 'sfx' && parts[pi].kind !== 'fixed' ? ' · ' + parts[pi].label : ''));
  }
  function currentPartIdx() {
    if (mode === 'vocab') return null;
    if (mode === 'kp') return curIdx;
    var g = gt(), r = null;
    for (var i = 0; i < parts.length; i++) { if (g >= parts[i].start - 0.001) r = i; else break; }
    return r;
  }
  function jaLight(sid) {   // rev01-f: 英語文のon/offに連動して、対応する日本語群だけを点灯する
    var g = sid ? (sidToG[sid] || null) : jaHold;   // 文と文の間: 同一群の前後の文に挟まれている間(jaHold)は消さない
    if (g === activeG) return;
    if (activeG && jgEls[activeG]) jgEls[activeG].forEach(function (e) { e.classList.remove('on'); });
    activeG = g;
    if (g && jgEls[g]) jgEls[g].forEach(function (e) { e.classList.add('on'); });
  }
  function gapGroup(g) {   // 文と文の間(2秒未満)で前後の文が同じ群なら、その群を返す
    var lo = 0, hi = sync.length - 1, k = -1;
    while (lo <= hi) { var m = (lo + hi) >> 1; if (sync[m].start <= g) { k = m; lo = m + 1; } else hi = m - 1; }
    if (k < 0 || k + 1 >= sync.length) return null;
    var a = sidToG[sync[k].sid], b = sidToG[sync[k + 1].sid];
    return (a && a === b && sync[k + 1].start - sync[k].end < 2.0) ? a : null;
  }
  function highlight(sid) {
    jaLight(sid);
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
    if (!A.paused || (selectedSid && Math.abs((A.currentTime || 0) - selTime) > 0.3)) selectedSid = null;   // rev01-h: 再生中は自動ハイライト優先(クリック選択は次のtickで自動ハイライトへ戻る)。選択後に再生位置が動いた場合(シーク等)も解除
    if (selectedSid) { jaHold = null; highlight(selectedSid); }   // rev01-h: 停止中・一時停止中は選択を維持(日本語はsidToGのみ=未確定は点灯しない)
    else if (sync.length) { var ga = mode === 'vocab' ? null : findActive(gt()); jaHold = (ga || mode === 'vocab') ? null : gapGroup(gt()); highlight(ga); }
    window.__EUP = { mode: mode, curIdx: curIdx, gt: gt(), active: activeSid, paused: A.paused, level: lv, article: art && art.id, syncKind: syncKind, src: A.src, jg: activeG, vi: vocabI, sel: selectedSid };
  }
  function selectSentence(sid) {   // rev01-h: 文クリック=その文と対応する日本語を点灯するのみ。再生開始・シーク・一時停止は一切しない
    if (!sid || !sentEls[sid]) return;
    if (A.paused) { selectedSid = sid; selTime = A.currentTime || 0; tick(); return; }   // 停止中・一時停止中=選択を維持 / 再生中=一瞬描くだけで次のtickが自動ハイライトへ戻す(保存しない)
    highlight(sid);
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
    var done = function () { tick(); };
    return fetchJson('data/sync_' + lv + '.json').then(function (j) { sync = norm(j); syncKind = 'real'; done(); }).catch(function (e) { console.warn(e); done(); });
  }

  /* ---------- レベル切替・初期化 ---------- */
  function setLevel(next) {
    lv = next; L = art.levels[lv]; parts = L.parts;
    A.pause(); selectedSid = null; mode = 'full'; curIdx = null; kpEnd = null; activeSid = null;
    ensureSrc(audioUrl(L.main));
    $('eyebrow').textContent = 'English Your Way · ' + LEVEL_NAME[lv];
    $('playAll').textContent = '▶ 全体を再生(' + fmt(L.total_sec) + ')';
    Array.prototype.forEach.call($('tabs').children, function (b) { b.setAttribute('aria-selected', b.dataset.lv === lv ? 'true' : 'false'); });
    document.title = art.title_ja + '｜' + LEVEL_NAME[lv];
    var u = new URL(location.href); u.searchParams.set('lv', lv); history.replaceState(null, '', u);
    render(); labels(); loadSync();
  }
  function init() {
    fetchJson('data/article.json').then(function (j) {
      art = j;
      $('jaTitle').textContent = art.title_ja; $('enTitle').textContent = art.topic_en;
      if (art.notice) { $('notice').textContent = art.notice; $('notice').hidden = false; }
      $('tabs').innerHTML = Object.keys(art.levels).map(function (k) { return '<button type="button" role="tab" data-lv="' + k + '">' + LEVEL_NAME[k] + '</button>'; }).join('');
      var want = Q.get('lv'); setLevel(art.levels[want] ? want : Object.keys(art.levels)[0]);
    }).catch(function (e) { $('content').innerHTML = '<div class="error"><strong>表示エラー</strong><br>' + esc(e.message) + '</div>'; });
  }

  /* ---------- イベント ---------- */
  $('content').addEventListener('click', function (e) {
    var se = e.target.closest('.sent');
    if (se && !e.target.closest('button')) { selectSentence(se.dataset.sid); return; }
    var gl = e.target.closest('a.glink');
    if (gl) {   // 意味一覧の「解説」: 該当表現の解説(Vocabulary項目)へ直接移動し、開く
      e.preventDefault();
      var t = $('vi-' + lv + '-' + gl.dataset.vi);
      if (t) { t.open = true; t.scrollIntoView({ block: 'start', behavior: 'smooth' }); t.classList.add('flash'); setTimeout(function () { t.classList.remove('flash'); }, 2200); }
      return;
    }
    var b = e.target.closest('button[data-act]'); if (!b) return;
    if (b.dataset.act === 'vocab') { e.preventDefault(); playVocab(Number(b.dataset.i)); return; }
    if (b.dataset.act === 'stop') { A.pause(); tick(); return; }   // rev01-c: 停止(連続再生中も)。位置は保持し、固定バー/ここから再生で再開
    var i = Number(b.dataset.i);
    if (b.dataset.act === 'kp') playKp(i, 0); else playFull(parts[i].start);
  });
  $('tabs').addEventListener('click', function (e) { var b = e.target.closest('button[data-lv]'); if (b && b.dataset.lv !== lv) setLevel(b.dataset.lv); });
  $('playAll').addEventListener('click', function () { playFull(0); window.scrollTo({ top: 0, behavior: 'smooth' }); });
  $('pp').addEventListener('click', function () { if (A.paused) { if (!A.src) playFull(0); else playNow(); } else A.pause(); });
  $('back10').addEventListener('click', function () { selectedSid = null; A.currentTime = Math.max(0, A.currentTime - 10); tick(); });
  $('fwd10').addEventListener('click', function () { selectedSid = null; A.currentTime = Math.min(dur() - 0.05, A.currentTime + 10); tick(); });
  $('seek').addEventListener('input', function () { selectedSid = null; A.currentTime = Math.min(dur() - 0.05, this.value / 1000 * dur()); tick(); });
  ['play', 'playing'].forEach(function (ev) { A.addEventListener(ev, kick); });
  ['pause', 'seeked', 'timeupdate', 'loadedmetadata', 'durationchange'].forEach(function (ev) { A.addEventListener(ev, tick); });
  A.addEventListener('ended', function () { if (mode === 'vocab') endVocab(); else tick(); });
  A.addEventListener('error', function () { console.warn('audio error', A.error && A.error.code, A.src); });
  ['wheel', 'touchmove'].forEach(function (ev) { window.addEventListener(ev, function () { lastUserScroll = Date.now(); }, { passive: true }); });

  init();
})();
