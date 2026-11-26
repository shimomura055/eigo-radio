/* eigo-radio WebApp UI 試作(WUR 委任_02a S0): Phrase/Word項目の「生成(buildPWItem)」と「描画(renderPWCard)」を切り出した共有モジュール。
   学ぶ画面・(後続の)吹き出し・復習帳が同じ関数を使えるようにするための挙動不変リファクタ。DOM・保存・音声は持たない(純関数)。 */
(function (root) {
  'use strict';
  var JA_RE = /[ぁ-んァ-ヶ一-龠]/;
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]; }); }
  function normEn(s) { return String(s || '').toLowerCase().normalize('NFKC').replace(/[^a-z0-9 ]+/g, ' ').replace(/\s+/g, ' ').trim(); }
  function fieldOf(v, label) { return (v && v.fields || []).filter(function (f) { return f.label === label; })[0]; }

  /* WUR 委任_02d S4: KP解説の「本文の英文」で該当Key Phraseを太字化。見出し文字列検索ではなく、一致した本文文の lk1 span(表層形)を使う。
     特定不能なら null(=従来表示に降格、エラーにしない)。lk2/lk3は対象外。 */
  var EX_LABEL = '本文の英文';   // 本文の英文
  function stripTags(h) { return String(h || '').replace(/<[^>]*>/g, ''); }
  function sentIndex(L) {
    var idx = [];
    (L.parts || []).forEach(function (p) { (p.paragraphs || []).forEach(function (para) { para.forEach(function (s) { if (s && s.html) idx.push({ n: normEn(s.text || stripTags(s.html)), html: s.html }); }); }); });
    return idx;
  }
  function lk1Of(html) {
    var out = [], re = /<(strong|span|b)\b[^>]*class="[^"]*\blk1\b[^"]*"[^>]*>([\s\S]*?)<\/\1>/g, m;
    while ((m = re.exec(html))) out.push(stripTags(m[2]));
    return out;
  }
  function pickLk1(cands, heading) {
    if (!cands.length) return null;
    var hn = normEn(heading), ex = cands.filter(function (c) { return normEn(c) === hn; });
    if (ex.length) return ex[0];
    if (cands.length === 1) return cands[0];
    var pre = function (w) { return w.length > 4 ? w.slice(0, 4) : w; }, ht = hn.split(' ').map(pre), best = null, bs = 0, tie = false;
    cands.forEach(function (c) { var sc = normEn(c).split(' ').filter(function (w) { return ht.indexOf(pre(w)) >= 0; }).length; if (sc > bs) { bs = sc; best = c; tie = false; } else if (sc === bs && sc > 0) tie = true; });
    return bs > 0 && !tie ? best : null;
  }
  function boldExample(html, heading, sents) {   // -> {html, how} | null
    if (!sents || html == null || /</.test(html)) return null;
    var plain = html.replace(/&amp;/g, '&').replace(/&#39;/g, "'"), n = normEn(plain), hit = null;
    for (var i = 0; i < sents.length; i++) if (sents[i].n === n) { hit = sents[i]; break; }
    if (!hit && n.length >= 12) for (var j = 0; j < sents.length; j++) if (sents[j].n.length >= 12 && (sents[j].n.indexOf(n) >= 0 || n.indexOf(sents[j].n) === 0) && (!hit || sents[j].n.length > hit.n.length)) hit = sents[j];   // 例文が文の途中で切れている場合
    if (!hit) return null;
    var surf = pickLk1(lk1Of(hit.html), heading); if (!surf) return null;
    var esc2 = surf.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/'/g, "(?:'|&#39;)"), re = new RegExp('(^|[^A-Za-z0-9])(' + esc2 + ')(?![A-Za-z0-9])', 'i');
    if (!re.test(html)) return null;
    return { html: html.replace(re, '$1<strong class="kpbold">$2</strong>'), how: normEn(surf) === normEn(heading) ? 'exact' : 'lk1' };
  }

  /* 1項目の生成。src={kind:'kp', k, hdr, v, seg, baseV, baseK} または {kind:'vocab', v, baseV} */
  function buildPWItem(src) {
    var v = src.v;
    if (src.kind === 'kp') {
      var k = src.k, hdr = src.hdr || [], ja = '', det = [], boldLog = [];
      if (JA_RE.test(k.text || '')) ja = k.text;                                   // Std等: 日本語の意味(承認済み)
      else {
        if (k.text) det.push({ label: hdr[1] || '英語での解説', html: esc(k.text) });   // Adv: 英英解説は詳細へ移動(削除しない)
        if (JA_RE.test(k.japanese_gloss || '')) ja = k.japanese_gloss;                // WUG R1: Adv Key Phraseの日本語訳は正式欄 kp[].japanese_gloss(internal-doc:3401)を参照(glossary.ja等の代替・「準備中」にしない)
      }
      if (k.text2) det.push({ label: hdr[2] || '英語での説明', html: esc(k.text2) });
      if (v) v.fields.forEach(function (f) {
        var h = f.html, b = (f.label === EX_LABEL && src.sents) ? boldExample(h, k.en, src.sents) : null;
        if (b) { h = b.html; boldLog.push(b.how); } else if (f.label === EX_LABEL) boldLog.push('none');
        det.push({ label: f.label, html: h });
      });
      var au = null;
      if (v && v.audio && v.audio.file) au = { url: src.baseV + v.audio.file };
      else if (k.en_audio) au = { url: src.baseK + src.seg, start: k.en_audio.start, end: k.en_audio.end };
      return { en: k.en, kp: true, ja: ja, jaPending: !ja, det: det, audio: au, bold: boldLog[0] || null };
    }
    var m = fieldOf(v, '本文中の意味'), det2 = v.fields.filter(function (f) { return f.label !== '本文中の意味'; }).map(function (f) { return { label: f.label, html: f.html }; });
    return { en: v.heading, kp: false, ja: m ? m.html : '', jaHtml: true, jaPending: !m, det: det2, audio: v.audio && v.audio.file ? { url: src.baseV + v.audio.file } : null };
  }
  /* 記事レベルL(article.json の levels[lv])から全項目: Key Phrase(+同名vocabの解説統合) → 残りのvocab */
  function buildPWItems(L, baseV, baseK) {   // baseV=Vocab単体mp3(enduser基準) baseK=Key Phrase区間音声(audio_base基準)
    var sents = sentIndex(L), items = [], vocab = L.vocab || [], vmap = {}, used = {};
    vocab.forEach(function (v, i) { if (vmap[normEn(v.heading)] == null) vmap[normEn(v.heading)] = i; });
    L.parts.forEach(function (p) {
      if (p.kind !== 'kp') return;
      (p.kp || []).forEach(function (k) {
        var vi = vmap[normEn(k.en)], v = vi != null ? vocab[vi] : null;
        if (v) used[vi] = 1;
        items.push(buildPWItem({ kind: 'kp', k: k, hdr: p.kp_header, v: v, seg: p.seg, baseV: baseV, baseK: baseK, sents: sents }));
      });
    });
    vocab.forEach(function (v, i) { if (!used[i]) items.push(buildPWItem({ kind: 'vocab', v: v, baseV: baseV })); });
    return items;
  }
  /* 1項目の描画(学ぶ画面の従来DOMと同一)。o={saved:boolean, playIcon:string} */
  function renderPWCard(x, i, o) {
    o = o || {};
    var rev = o.variant === 'review';   // WUR S5: 復習の答え側(保存ボタン・音声ボタンなし。他は学ぶ画面と同一部品)
    var ja = x.ja ? (x.jaHtml ? x.ja : esc(x.ja)) : '<span class="prep">日本語訳: 準備中</span>';
    return '<div class="pwi' + (x.kp ? ' iskp' : '') + '" data-pw="' + i + '"><div class="pwr"><div class="pwtxt">' + (x.kp ? '<span class="kpmark">Key Phrase</span>' : '') + '<b class="pwen">' + esc(x.en) + '</b><span class="pwja" lang="ja">' + ja + '</span></div>' +
      (rev ? '' : x.audio ? '<button type="button" class="pwplay" data-pwplay="' + i + '" aria-label="' + esc(x.en) + ' の音声を再生">' + o.playIcon + '</button>' : '<span class="noaud" aria-label="音声なし">音声なし</span>') + '</div>' +
      '<div class="pwact">' + (x.det.length ? '<button type="button" class="pwtog" data-pwtog="' + i + '" aria-expanded="false"><span class="t">詳しい解説を見る</span><i class="arr" aria-hidden="true"></i></button>' : '<span></span>') +
      (rev ? '' : '<button type="button" class="save' + (o.saved ? ' on' : '') + '" data-save="' + esc(x.en) + '" data-ja="' + esc(x.jaHtml ? '' : (x.ja || '')) + '">' + (o.saved ? '保存済' : '保存') + '</button>') + '</div>' +
      (x.det.length ? '<dl class="pwdet" hidden>' + x.det.map(function (f) { return '<dt>' + esc(f.label) + '</dt><dd>' + f.html + '</dd>'; }).join('') + '</dl>' : '') + '</div>';
  }
  root.PWCard = { buildPWItem: buildPWItem, buildPWItems: buildPWItems, renderPWCard: renderPWCard, boldExample: boldExample, sentIndex: sentIndex, normEn: normEn, fieldOf: fieldOf };
})(window);
