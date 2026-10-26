/* 学習項目選定フォームv3 の純ロジック(DOMなし)。参照HTML(docs/pm/Phrase_Form/eigo_radio_selection_form_reference.html)の
 * counts / allowed / payload を関数化したもの。ブラウザ(window.FormLogic)とnode(module.exports)の両方で使える。 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(); else root.FormLogic = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  var LIMITS = [3, 5, 12];          // 累積上限: ①<=3, ①+②<=5, ①+②+③<=12
  var GRAMMAR_MAX = 2;
  var SCHEMA = 'eigo_radio_selection_result_v2';

  function terms(d) { return (d.phrases || []).concat(d.words || []).map(function (x) { return x.term; }); }
  // 現在の候補に存在する語の選択だけを数える(候補データ更新後の古い選択でカウントが狂わないようにするため)
  function counts(choices, termList) {
    var c = [0, 0, 0];
    termList.forEach(function (t) { var v = (choices || {})[t] || 0; if (v >= 1 && v <= 3) c[v - 1]++; });
    return c;
  }
  function allowed(choices, termList, term, cat) {
    var c = counts(choices, termList), old = (choices || {})[term] || 0;
    if (old === cat) return true;
    var n = c.map(function (v, i) { return v + (cat === i + 1 ? 1 : 0) - (old === i + 1 ? 1 : 0); });
    return n[0] <= LIMITS[0] && n[0] + n[1] <= LIMITS[1] && n[0] + n[1] + n[2] <= LIMITS[2];
  }
  function grammarChosen(grammarSel, gids) { return gids.filter(function (id) { return !!(grammarSel || {})[id]; }); }
  function grammarCanToggle(grammarSel, gids, id) {
    var on = !!(grammarSel || {})[id];
    return on || grammarChosen(grammarSel, gids).length < GRAMMAR_MAX;
  }
  // 状態の変更(不許可なら変更しない)。戻り値=変更したか
  function setChoice(st, termList, term, cat, checked) {
    if (checked && !allowed(st.choices, termList, term, cat)) return false;
    st.choices[term] = checked ? cat : 0; return true;
  }
  function setGrammar(st, gids, id, checked) {
    if (checked && !grammarCanToggle(st.grammar, gids, id)) return false;
    st.grammar[id] = !!checked; return true;
  }
  function newState() { return { choices: {}, grammar: {}, comment: '' }; }
  function stateKey(entry) { return entry.slug + '__' + entry.level; }

  function summary(d, st) {
    var tl = terms(d), c = counts(st.choices, tl);
    var groups = [1, 2, 3].map(function (cat) { return tl.filter(function (t) { return (st.choices || {})[t] === cat; }); });
    var gids = (d.grammar || []).map(function (g) { return g.id; });
    var gsel = (d.grammar || []).filter(function (g) { return (st.grammar || {})[g.id]; });
    return { counts: c, groups: groups, grammar: gsel, gids: gids };
  }
  // ---- 日本語訳・AI選定理由(委任_02 ①③) ----
  // 日本語訳=候補doc既存の japanese_gloss(ページ表示・P8-KP音声の元と同一項目)。AI再生成はしない。status: official|provisional|missing
  var GLOSS_LABEL = { official: '正式訳', provisional: '仮訳・未確定', missing: '日本語訳未生成' };
  var CAT_LABEL = { 1: '①Key Phrase', 2: '②追加解説', 3: '③本文意味表示' };
  var REASON_NONE = {
    none_call1_has_no_reason: 'AI理由なし(最初の候補生成は選定理由を出さない仕様)',
    none_placeholder_not_real: 'AI理由なし(試験用の仮文言のため非表示)',
    none_not_generated: 'AI理由は未生成'
  };
  function glossOf(it) {
    var text = (it.ja_gloss !== undefined ? it.ja_gloss : it.meaning_ja) || '';
    var st = it.ja_gloss_status || (text ? 'provisional' : 'missing');   // status無しの旧データは正式扱いしない
    if (!text) st = 'missing';
    return { text: text, status: st, label: GLOSS_LABEL[st] || st };
  }
  function reasonOf(it) {
    var r = (it.reason_ja || '').trim();
    var src = it.reason_source || (r ? 'ai_unknown' : 'none_not_generated');
    if (r) return { text: r, source: src, has: true, note: '' };
    return { text: '', source: src, has: false, note: REASON_NONE[src] || 'AI理由は未生成' };
  }
  function allItems(d) { return (d.phrases || []).concat(d.words || []); }
  function findItem(d, term) { return allItems(d).filter(function (x) { return x.term === term; })[0] || { term: term }; }
  // 候補の識別(委任_03): candidate_id=候補docの逐語(termは同一表示が複数候補にあり得るため対応付けの正にしない)。旧データはidを流用、無ければnull(捏造しない)
  function candIdOf(it) { return it.candidate_id || it.id || null; }
  function kindOf(it) { return it.kind === 'phrase' || it.kind === 'word' ? it.kind : null; }
  function shaInfo(d) {
    var sha = d.candidates_sha256 || null;
    return { sha: sha, src: d.candidates_sha256_source || (sha ? 'candidate_doc_field' : 'unavailable'), path: d.source_kp_candidates_path || null };
  }
  function itemRecord(it, cat) {
    var g = glossOf(it), o = { term: it.term, category: cat, category_label: CAT_LABEL[cat], ja_gloss: g.text, ja_gloss_status: g.status, candidate_id: candIdOf(it), kind: kindOf(it) };
    if (it.selection_phrase && it.selection_phrase !== it.term) o.selection_phrase = it.selection_phrase;
    return o;
  }
  function grammarRecord(g) {
    var full = g.body || '';
    return { id: g.id, title: g.title, explanation_full: full, explanation_status: full ? 'provided' : 'missing', example: g.example || '' };
  }

  // 参照HTMLのpayload()と同じ書式(人間可読テキスト)の先頭5ブロック+委任_02の確定内容詳細・AI理由(確認用)
  function buildText(d, st) {
    var s = summary(d, st), c = s.counts, tot = c[0] + c[1] + c[2];
    var lvl = d.level_label || d.level || '';
    var t = '記事: ' + d.name + ' ' + lvl + '\n' +
      '① Key Phrase (' + c[0] + '/3): ' + (s.groups[0].join(' / ') || 'なし') + '\n' +
      '② 追加解説 (①＋②=' + (c[0] + c[1]) + '/5): ' + (s.groups[1].join(' / ') || 'なし') + '\n' +
      '③ 本文意味表示 (累計=' + tot + '/12): ' + (s.groups[2].join(' / ') || 'なし') + '\n' +
      '文法 (' + s.grammar.length + '/2): ' + (s.grammar.map(function (g) { return g.title; }).join(' / ') || 'なし') + '\n' +
      '自由コメント: ' + (st.comment || 'なし');
    var si = shaInfo(d);
    var lines = ['', '【ユーザー確定内容の詳細(英語表現・日本語訳・区分。後続工程で変更しない)】',
      '候補集合sha256: ' + (si.sha || 'なし(取得不可: ' + si.src + ')')];
    var anyItem = false, unconfirmed = false;
    s.groups.forEach(function (grp, i) {
      grp.forEach(function (term) {
        var r = itemRecord(findItem(d, term), i + 1); anyItem = true; if (r.ja_gloss_status !== 'official') unconfirmed = true;
        lines.push(r.category_label + '｜' + r.term + '｜日本語訳: ' + (r.ja_gloss || '(未生成)') + '【' + GLOSS_LABEL[r.ja_gloss_status] + '】' +
          '｜candidate_id: ' + (r.candidate_id || 'なし') + '｜種類: ' + (r.kind || 'なし'));
      });
    });
    if (!anyItem) lines.push('(選択なし)');
    lines.push('【文法解説(選択分の解説全文)】');
    if (!s.grammar.length) lines.push('(選択なし)');
    s.grammar.forEach(function (g) {
      var r = grammarRecord(g);
      lines.push('・' + r.title + (r.explanation_status === 'provided' ? '\n' + r.explanation_full + (r.example ? '\n例: ' + r.example : '') : '\n【解説本文: 未生成】'));
    });
    if (unconfirmed) lines.push('※【仮訳・未確定】【日本語訳未生成】は正式な日本語訳ではありません。確認と修正案の提示を求めます(黙って確定・変更しないこと)。');
    lines.push('', '【AI選定理由(確認用情報。ユーザーが確定した英語・日本語訳・解説本文とは別。確定内容ではありません)】');
    var nr = 0;
    s.groups.forEach(function (grp) { grp.forEach(function (term) {
      var ro = reasonOf(findItem(d, term)); nr++; var it0 = findItem(d, term); lines.push('・' + term + '(' + (candIdOf(it0) || 'candidate_idなし') + '): ' + (ro.has ? ro.text : '(' + ro.note + ')'));
    }); });
    if (!nr) lines.push('(選択なし)');
    t += lines.join('\n');
    if (d.is_ui_check_dummy) t += '\n※これはUI確認用ダミー記事の操作結果です。正式記事ではない。';
    else t += '\n※未選択候補は不採用。';
    return t;
  }
  // opts.all_candidates=true のとき、未選択を含む全候補(英語・日本語訳・状態・AI理由)も出力(コピー用。URL送信では長さ上限のため省略)
  function buildStructured(d, st, now, opts) {
    var s = summary(d, st);
    var sel = [1, 2, 3].map(function (cat) { return s.groups[cat - 1].map(function (t) { return itemRecord(findItem(d, t), cat); }); });
    var refs = []; s.groups.forEach(function (grp) { grp.forEach(function (t) { var ro = reasonOf(findItem(d, t)); refs.push({ candidate_id: candIdOf(findItem(d, t)), term: t, reason_ja: ro.text, reason_source: ro.source }); }); });
    var o = {
      schema: SCHEMA, schema_version: 2, schema_minor: 1, generated_at: now || new Date().toISOString(),
      article: { slug: d.slug, level: d.level, level_label: d.level_label || '', name: d.name, text_sha256: (d.source || {}).text_sha256 || null,
        candidates_sha256: shaInfo(d).sha, candidates_sha256_source: shaInfo(d).src, source_kp_candidates_path: shaInfo(d).path },
      candidate_source: (d.source || {}).kind || null,
      limits: { key_phrase: LIMITS[0], key_phrase_plus_extra: LIMITS[1], total_highlight: LIMITS[2], grammar: GRAMMAR_MAX },
      user_confirmed_note_ja: 'selection・comment はユーザーが確定した内容(英語表現・日本語訳・区分・文法解説全文)。後続工程で変更しない。ja_gloss_status が official 以外の日本語訳は未確定で、変更が必要なら修正案を提示して再確認を求めること。',
      selection: { key_phrase: sel[0], extra_explanation: sel[1], meaning_display: sel[2], grammar: s.grammar.map(grammarRecord) },
      grammar_status: (d.grammar || []).length ? 'candidates_available' : 'no_candidates_ungenerated',
      comment: st.comment || '',
      ai_reference: { for_reference_only: true, note_ja: 'AIの選定理由は確認用情報です。ユーザーが確定した英語・日本語訳・解説本文ではありません。', items: refs },
      counts: { key_phrase: s.counts[0], key_phrase_plus_extra: s.counts[0] + s.counts[1], total_highlight: s.counts[0] + s.counts[1] + s.counts[2], grammar: s.grammar.length },
      production_connected: false
    };
    if (opts && opts.all_candidates) {
      o.candidates_all = allItems(d).map(function (it) {
        var g = glossOf(it), ro = reasonOf(it), cat = (st.choices || {})[it.term] || 0;
        return { candidate_id: candIdOf(it), kind: kindOf(it), term: it.term, category: cat, ja_gloss: g.text, ja_gloss_status: g.status, reason_ja: ro.text, reason_source: ro.source, reason_for_reference_only: true };
      });
    }
    return o;
  }
  var PREFACE = '以下の選定内容を整理し、必要な修正指示と実装範囲を確認してください。Claude Code向け指示案を作成してください。正式Productionへの未承認変更は禁止します。\n\n';
  var URL_MAX = 6000;
  // ChatGPT送信URL。長すぎる場合はJSONを外し、それでも長ければ url=null(=コピー誘導)
  function buildChatGptUrl(d, st, now) {
    var text = PREFACE + buildText(d, st);
    var withJson = text + '\n\n```json\n' + JSON.stringify(buildStructured(d, st, now)) + '\n```';
    var base = 'https://chatgpt.com/?q=';
    var u1 = base + encodeURIComponent(withJson);
    if (u1.length <= URL_MAX) return { url: u1, with_json: true };
    var u2 = base + encodeURIComponent(text);
    if (u2.length <= URL_MAX) return { url: u2, with_json: false };
    return { url: null, with_json: false };
  }
  function buildCopyText(d, st, now) {
    return buildText(d, st) + '\n\n```json\n' + JSON.stringify(buildStructured(d, st, now, { all_candidates: true }), null, 1) + '\n```';
  }

  // ---- データ検証(testとブラウザの双方で使う) ----
  function validateArticle(d) {
    var e = [];
    if (!d || d.schema !== 'eigo_radio_selection_article_v1') e.push('schema');
    ['slug', 'level', 'name'].forEach(function (k) { if (!d || !d[k]) e.push('missing:' + k); });
    if (d) {
      if (!Array.isArray(d.phrases) || d.phrases.length > 7) e.push('phrases>7');
      if (!Array.isArray(d.words) || d.words.length > 5) e.push('words>5');
      if (!Array.isArray(d.grammar)) e.push('grammar');
      var seen = {};
      terms(d).forEach(function (t) { if (!t) e.push('empty term'); if (seen[t]) e.push('dup:' + t); seen[t] = 1; });
      var seenId = {};
      allItems(d).forEach(function (x) { var id = candIdOf(x); if (id) { if (seenId[id]) e.push('dup_candidate_id:' + id); seenId[id] = 1; } });
      (d.grammar || []).forEach(function (g) { ['id', 'title', 'body'].forEach(function (k) { if (!g[k]) e.push('grammar.' + k); }); });
    }
    return e;
  }
  function validateIndex(idx) {
    var e = [], seen = {};
    if (!idx || idx.schema !== 'eigo_radio_selection_index_v1' || !Array.isArray(idx.articles)) return ['schema'];
    idx.articles.forEach(function (a) {
      ['slug', 'level', 'name'].forEach(function (k) { if (a[k] === undefined) e.push('missing:' + k); });
      var k = stateKey(a); if (seen[k]) e.push('dup:' + k); seen[k] = 1;
    });
    return e;
  }
  return { LIMITS: LIMITS, GRAMMAR_MAX: GRAMMAR_MAX, SCHEMA: SCHEMA, terms: terms, counts: counts, allowed: allowed, grammarChosen: grammarChosen,
    grammarCanToggle: grammarCanToggle, setChoice: setChoice, setGrammar: setGrammar, newState: newState, stateKey: stateKey, summary: summary,
    buildText: buildText, buildStructured: buildStructured, buildChatGptUrl: buildChatGptUrl, buildCopyText: buildCopyText, glossOf: glossOf, reasonOf: reasonOf, itemRecord: itemRecord, candIdOf: candIdOf, kindOf: kindOf, shaInfo: shaInfo, grammarRecord: grammarRecord, GLOSS_LABEL: GLOSS_LABEL,
    validateArticle: validateArticle, validateIndex: validateIndex };
});
