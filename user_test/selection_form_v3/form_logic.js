/* 学習項目選定フォームv3 の純ロジック(DOMなし)。参照HTML(docs/pm/Phrase_Form/eigo_radio_selection_form_reference.html)の
 * counts / allowed / payload を関数化したもの。ブラウザ(window.FormLogic)とnode(module.exports)の両方で使える。 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(); else root.FormLogic = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  var LIMITS = [3, 5, 12];          // 累積上限: ①<=3, ①+②<=5, ①+②+③<=12
  var GRAMMAR_MAX = 2;
  var SCHEMA = 'eigo_radio_selection_result_v1';

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
  // 参照HTMLのpayload()と同じ書式(人間可読テキスト)
  function buildText(d, st) {
    var s = summary(d, st), c = s.counts, tot = c[0] + c[1] + c[2];
    var lvl = d.level_label || d.level || '';
    var t = '記事: ' + d.name + ' ' + lvl + '\n' +
      '① Key Phrase (' + c[0] + '/3): ' + (s.groups[0].join(' / ') || 'なし') + '\n' +
      '② 追加解説 (①＋②=' + (c[0] + c[1]) + '/5): ' + (s.groups[1].join(' / ') || 'なし') + '\n' +
      '③ 本文意味表示 (累計=' + tot + '/12): ' + (s.groups[2].join(' / ') || 'なし') + '\n' +
      '文法 (' + s.grammar.length + '/2): ' + (s.grammar.map(function (g) { return g.title; }).join(' / ') || 'なし') + '\n' +
      '自由コメント: ' + (st.comment || 'なし');
    if (d.is_ui_check_dummy) t += '\n※これはUI確認用ダミー記事の操作結果です。正式記事ではない。';
    else t += '\n※未選択候補は不採用。';
    return t;
  }
  function buildStructured(d, st, now) {
    var s = summary(d, st);
    return {
      schema: SCHEMA, schema_version: 1, generated_at: now || new Date().toISOString(),
      article: { slug: d.slug, level: d.level, level_label: d.level_label || '', name: d.name, text_sha256: (d.source || {}).text_sha256 || null },
      candidate_source: (d.source || {}).kind || null,
      limits: { key_phrase: LIMITS[0], key_phrase_plus_extra: LIMITS[1], total_highlight: LIMITS[2], grammar: GRAMMAR_MAX },
      selection: {
        key_phrase: s.groups[0], extra_explanation: s.groups[1], meaning_display: s.groups[2],
        grammar: s.grammar.map(function (g) { return { id: g.id, title: g.title }; })
      },
      counts: { key_phrase: s.counts[0], key_phrase_plus_extra: s.counts[0] + s.counts[1], total_highlight: s.counts[0] + s.counts[1] + s.counts[2], grammar: s.grammar.length },
      comment: st.comment || '',
      production_connected: false
    };
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
    return buildText(d, st) + '\n\n```json\n' + JSON.stringify(buildStructured(d, st, now), null, 1) + '\n```';
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
    buildText: buildText, buildStructured: buildStructured, buildChatGptUrl: buildChatGptUrl, buildCopyText: buildCopyText,
    validateArticle: validateArticle, validateIndex: validateIndex };
});
