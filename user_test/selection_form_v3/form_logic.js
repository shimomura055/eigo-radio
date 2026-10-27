/* 学習項目選定フォームv3 の純ロジック(DOMなし)。参照HTML(docs/pm/Phrase_Form/eigo_radio_selection_form_reference.html)の
 * counts / allowed / payload を関数化したもの。ブラウザ(window.FormLogic)とnode(module.exports)の両方で使える。 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(); else root.FormLogic = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  var LIMITS = [3, 5, 12];          // 累積上限: ①<=3, ①+②<=5, ①+②+③<=12
  var GRAMMAR_MAX = 1;              // 新仕様(2026-10-27ユーザー正式決定): 文法は原則1件(0件可・2件同時選択禁止)
  var GRAMMAR_TOP_N = 2;            // ユーザーへ提示する文法はAI評価Top 1・Top 2の最大2件のみ
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
  // ---- 文法(新仕様): 提示=Top1/Top2のみ(rank順)、選択=ラジオ(1件)または「適切な候補なし(0件)」、2件同時は不可 ----
  function grammarPresented(d) {
    var gs = ((d && d.grammar) || []).map(function (g, i) { return { g: g, i: i }; });
    gs.sort(function (a, b) { var ra = a.g.rank == null ? 1e9 : a.g.rank, rb = b.g.rank == null ? 1e9 : b.g.rank; return ra - rb || a.i - b.i; });
    return gs.slice(0, GRAMMAR_TOP_N).map(function (x, k) { return Object.assign({}, x.g, { display_rank: k + 1 }); });
  }
  function grammarIds(d) { return grammarPresented(d).map(function (g) { return g.id; }); }
  function grammarChosen(grammarSel, gids) { return gids.filter(function (id) { return !!(grammarSel || {})[id]; }); }
  function grammarCanToggle(grammarSel, gids, id) {
    var on = !!(grammarSel || {})[id];
    return on || grammarChosen(grammarSel, gids).length < GRAMMAR_MAX;
  }
  // 古い保存状態(旧仕様で最大2件選択)が新仕様に反する場合は選択を破棄して未決定に戻す(黙って1件に丸めない)
  function normalizeGrammar(st, gids) {
    if (grammarChosen(st.grammar, gids).length > GRAMMAR_MAX) { st.grammar = {}; st.grammar_zero = false; return true; }
    return false;
  }
  // 状態: 'selected'(1件) | 'none'(「適切な候補なし」を明示選択) | 'undecided'(未決定) | 'n/a'(提示候補0件)
  function grammarDecision(d, st) {
    var gids = grammarIds(d);
    if (!gids.length) return 'n/a';
    var n = grammarChosen(st.grammar, gids).length;
    if (n === 1) return 'selected';
    if (n === 0 && st.grammar_zero === true) return 'none';
    return 'undecided';
  }
  function hasGrammarSpec(d) { return !!(d && d.grammar_spec); }
  // 新仕様データ(grammar_spec有り)で提示候補があるのに未決定なら、送信/コピーを止める(0件は「適切な候補なし」の明示選択が必要。旧フォームの0件は引き継がない)
  function grammarBlocked(d, st) { return hasGrammarSpec(d) && grammarDecision(d, st) === 'undecided'; }
  function chooseGrammar(st, gids, id) {            // ラジオ操作: 他を外して1件にする
    if (gids.indexOf(id) < 0) return false;
    gids.forEach(function (x) { st.grammar[x] = (x === id); }); st.grammar_zero = false; return true;
  }
  function chooseGrammarNone(st, gids) { gids.forEach(function (x) { st.grammar[x] = false; }); st.grammar_zero = true; return true; }
  // 状態の変更(不許可なら変更しない)。戻り値=変更したか
  function setChoice(st, termList, term, cat, checked) {
    if (checked && !allowed(st.choices, termList, term, cat)) return false;
    st.choices[term] = checked ? cat : 0; return true;
  }
  function setGrammar(st, gids, id, checked) {      // チェック方式API。既に1件選択済みなら2件目は拒否する(置換はchooseGrammar)
    if (checked && !grammarCanToggle(st.grammar, gids, id)) return false;
    st.grammar[id] = !!checked; if (checked) st.grammar_zero = false; return true;
  }
  function newState() { return { choices: {}, grammar: {}, grammar_zero: false, comment: '' }; }
  // ユーザー確定済みKP/KW(kp_confirmed)がある記事は、保存状態(choices)ではなく確定内容を常に採用する(再選定不可)
  function choicesOf(d, st) {
    if (d && d.kp_confirmed) { var m = {}; (d.kp_confirmed.selection || []).forEach(function (r) { m[r.term] = r.category; }); return m; }
    return (st && st.choices) || {};
  }
  function stateKey(entry) { return entry.slug + '__' + entry.level; }

  function summary(d, st) {
    var tl = terms(d), ch = choicesOf(d, st), c = counts(ch, tl);
    var groups = [1, 2, 3].map(function (cat) { return tl.filter(function (t) { return ch[t] === cat; }); });
    var gids = grammarIds(d);
    var gsel = grammarPresented(d).filter(function (g) { return (st.grammar || {})[g.id]; });
    return { counts: c, groups: groups, grammar: gsel, gids: gids };
  }
  // ---- 日本語訳・AI選定理由(委任_02 ①③) ----
  // 日本語訳=候補doc既存の japanese_gloss(ページ表示・P8-KP音声の元と同一項目)。AI再生成はしない。status: official|provisional|missing
  var GLOSS_LABEL = { official: '正式訳', provisional: '仮訳・未確定', missing: '日本語訳未生成' };
  var CAT_LABEL = { 1: '①Key Phrase', 2: '②追加解説', 3: '③本文意味表示' };
  function glossOf(it) {
    var text = (it.ja_gloss !== undefined ? it.ja_gloss : it.meaning_ja) || '';
    var st = it.ja_gloss_status || (text ? 'provisional' : 'missing');   // status無しの旧データは正式扱いしない
    if (!text) st = 'missing';
    return { text: text, status: st, label: GLOSS_LABEL[st] || st };
  }
  function reasonOf(it) {
    var r = (it.reason_ja || '').trim();
    // 理由が実際に存在する候補だけ has=true。存在しない候補は理由欄を描画せず、送信にも含めない(2026-10-27ユーザー決定§4。理由欠落を示す文言は出さない)
    if (r) return { text: r, source: it.reason_source || 'ai_unknown', has: true };
    return { text: '', source: '', has: false };
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
    var r = { id: g.id, title: g.title, explanation_full: full, explanation_status: full ? 'provided' : 'missing', example: g.example || '' };
    // 事前生成の契約項目(SCHEMA_CONTRACT_01 §5)がデータにある場合のみ併記(後工程の照合用。無い旧データでは従来どおり)
    if (g.candidate_id) r.candidate_id = g.candidate_id;
    if (g.explanation_sha256) r.explanation_sha256 = g.explanation_sha256;
    if (g.level) r.level = g.level;
    if (g.display_rank || g.rank) { r.rank = g.display_rank || g.rank; r.rank_label = 'Top ' + r.rank; }
    return r;
  }

  // 参照HTMLのpayload()と同じ書式(人間可読テキスト)の先頭5ブロック+委任_02の確定内容詳細・AI理由(確認用)
  function buildText(d, st) {
    var s = summary(d, st), c = s.counts, tot = c[0] + c[1] + c[2];
    var lvl = d.level_label || d.level || '';
    var t = '記事: ' + d.name + ' ' + lvl + '\n' +
      '① Key Phrase (' + c[0] + '/3): ' + (s.groups[0].join(' / ') || 'なし') + '\n' +
      '② 追加解説 (①＋②=' + (c[0] + c[1]) + '/5): ' + (s.groups[1].join(' / ') || 'なし') + '\n' +
      '③ 本文意味表示 (累計=' + tot + '/12): ' + (s.groups[2].join(' / ') || 'なし') + '\n' +
      '文法 (' + s.grammar.length + '/' + GRAMMAR_MAX + '｜AI評価Top 1・Top 2から1件、または適切な候補なしで0件): ' + (s.grammar.map(function (g) { return (g.display_rank ? 'Top ' + g.display_rank + ' ' : '') + g.title; }).join(' / ') || (grammarDecision(d, st) === 'undecided' ? '未決定' : 'なし')) + '\n' +
      '自由コメント: ' + (st.comment || 'なし');
    var si = shaInfo(d);
    var lines = [];
    if (d.kp_confirmed) lines.push('', '【Key Phrase／Key Word 10件はユーザー確定済み(' + d.kp_confirmed.status + '、' + (d.kp_confirmed.confirmed_at || '') + ')。再選定不可。この送信では文法だけを選定しました】');
    lines = lines.concat(['', '【ユーザー確定内容の詳細(英語表現・日本語訳・区分。後続工程で変更しない)】',
      '候補集合sha256: ' + (si.sha || 'なし(取得不可: ' + si.src + ')')]);
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
      lines.push('・' + (r.rank_label ? r.rank_label + '｜' : '') + r.title + (r.explanation_status === 'provided' ? '\n' + r.explanation_full + (r.example ? '\n例: ' + r.example : '') : '\n【解説本文: 未生成】'));
    });
    if (unconfirmed) lines.push('※【仮訳・未確定】【日本語訳未生成】は正式な日本語訳ではありません。確認と修正案の提示を求めます(黙って確定・変更しないこと)。');
    lines.push('', '【AI選定理由(確認用情報。ユーザーが確定した英語・日本語訳・解説本文とは別。確定内容ではありません)】');
    var nr = 0;
    s.groups.forEach(function (grp) { grp.forEach(function (term) {
      nr++; var it0 = findItem(d, term), ro = reasonOf(it0);
      if (ro.has) lines.push('・' + term + '(' + (candIdOf(it0) || 'candidate_idなし') + '): ' + ro.text);   // 理由が無い候補の行は出さない
    }); });
    if (!nr) lines.push('(選択なし)');
    t += lines.join('\n');
    if (d.is_ui_check_dummy) t += '\n※これはUI確認用ダミー記事の操作結果です。正式記事ではない。';
    else t += '\n※未選択候補は不採用。';
    return t;
  }
  // opts.all_candidates=true のとき、未選択を含む全候補(英語・日本語訳・状態・AI理由)も出力(コピー用。URL送信では長さ上限のため省略)
  // 文法の状態表示: 新仕様(grammar_spec)は選定状態、旧形式は従来の3値
  function grammarStatus(d, st) {
    if (hasGrammarSpec(d)) {
      var ds = grammarDecision(d, st);
      return ds === 'selected' ? 'user_selected_one' : ds === 'none' ? 'user_selected_none' : ds === 'n/a' ? 'no_candidates_found' : 'pending_reselection';
    }
    return grammarPresented(d).length ? 'candidates_available' : (d.grammar_status === 'no_candidates_found' ? 'no_candidates_found' : 'no_candidates_ungenerated');
  }
  function buildStructured(d, st, now, opts) {
    var s = summary(d, st);
    var sel = [1, 2, 3].map(function (cat) { return s.groups[cat - 1].map(function (t) { return itemRecord(findItem(d, t), cat); }); });
    // ユーザー確定済みKP/KWは確定レコードを逐語でそのまま送る(再選定・再構成しない)
    if (d.kp_confirmed) sel = [1, 2, 3].map(function (cat) { return (d.kp_confirmed.selection || []).filter(function (r) { return r.category === cat; }).map(function (r) { return JSON.parse(JSON.stringify(r)); }); });
    var refs = []; s.groups.forEach(function (grp) { grp.forEach(function (t) { var ro = reasonOf(findItem(d, t)); if (ro.has) refs.push({ candidate_id: candIdOf(findItem(d, t)), term: t, reason_ja: ro.text, reason_source: ro.source }); }); });   // 理由がある候補のみ(空文字・「なし」文言は送らない)
    var o = {
      schema: SCHEMA, schema_version: 2, schema_minor: 1, generated_at: now || new Date().toISOString(),
      article: { slug: d.slug, level: d.level, level_label: d.level_label || '', name: d.name, text_sha256: (d.source || {}).text_sha256 || null,
        candidates_sha256: shaInfo(d).sha, candidates_sha256_source: shaInfo(d).src, source_kp_candidates_path: shaInfo(d).path },
      candidate_source: (d.source || {}).kind || null,
      limits: { key_phrase: LIMITS[0], key_phrase_plus_extra: LIMITS[1], total_highlight: LIMITS[2], grammar: GRAMMAR_MAX, grammar_presented_max: GRAMMAR_TOP_N },
      user_confirmed_note_ja: 'selection・comment はユーザーが確定した内容(英語表現・日本語訳・区分・文法解説全文)。後続工程で変更しない。ja_gloss_status が official 以外の日本語訳は未確定で、変更が必要なら修正案を提示して再確認を求めること。',
      selection: { key_phrase: sel[0], extra_explanation: sel[1], meaning_display: sel[2], grammar: s.grammar.map(grammarRecord) },
      grammar_status: grammarStatus(d, st),
      comment: st.comment || '',
      ai_reference: { for_reference_only: true, note_ja: 'AIの選定理由は確認用情報です。ユーザーが確定した英語・日本語訳・解説本文ではありません。', items: refs },
      counts: { key_phrase: s.counts[0], key_phrase_plus_extra: s.counts[0] + s.counts[1], total_highlight: s.counts[0] + s.counts[1] + s.counts[2], grammar: s.grammar.length },
      production_connected: false
    };
    if (d.kp_confirmed) o.kp_confirmed = { status: d.kp_confirmed.status, locked: true, confirmed_at: d.kp_confirmed.confirmed_at || null, user_ref: d.kp_confirmed.user_ref || null, note_ja: 'Key Phrase／Key Word 10件はユーザー確定済み。この送信で再選定していない(selectionは確定内容の逐語)。' };
    if (hasGrammarSpec(d)) {
      var pres = grammarPresented(d);
      o.grammar_decision = { state: grammarDecision(d, st), spec: 'top2_select1_v1', max_select: GRAMMAR_MAX, presented: pres.map(function (g) { return { rank: g.display_rank, candidate_id: g.candidate_id || g.id, title: g.title }; }),
        selected_candidate_id: s.grammar.length ? (s.grammar[0].candidate_id || s.grammar[0].id) : null };
    }
    if (opts && opts.all_candidates) {
      o.candidates_all = allItems(d).map(function (it) {
        var g = glossOf(it), ro = reasonOf(it), cat = choicesOf(d, st)[it.term] || 0;
        var rec = { candidate_id: candIdOf(it), kind: kindOf(it), term: it.term, category: cat, ja_gloss: g.text, ja_gloss_status: g.status };
        if (ro.has) { rec.reason_ja = ro.text; rec.reason_source = ro.source; rec.reason_for_reference_only = true; }
        return rec;
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
      if (d.grammar_spec) {   // 新仕様データ: 提示=Top1/Top2のみ(3位以降をデータに残さない)・rank 1,2・presented_idsと一致
        var gp = d.grammar || [];
        if (gp.length > GRAMMAR_TOP_N) e.push('grammar_spec: 提示候補が' + GRAMMAR_TOP_N + '件を超えています(' + gp.length + ')');
        gp.forEach(function (g, i) { if (g.rank !== i + 1) e.push('grammar_spec: rank不一致 ' + g.id); });
        if (JSON.stringify((d.grammar_spec.presented_ids || [])) !== JSON.stringify(gp.map(function (g) { return g.candidate_id || g.id; }))) e.push('grammar_spec: presented_ids不一致');
        if (d.grammar_spec.max_select !== GRAMMAR_MAX) e.push('grammar_spec: max_select');
      }
      if (d.kp_confirmed) {   // ユーザー確定済みKP/KW: 候補データと逐語照合(不一致=fail-closed)
        var kc = d.kp_confirmed, byId = {};
        allItems(d).forEach(function (x) { byId[candIdOf(x)] = x; });
        if (kc.status !== 'USER_CONFIRMED') e.push('kp_confirmed.status');
        var cnt = [0, 0, 0];
        (kc.selection || []).forEach(function (r) {
          var it = byId[r.candidate_id];
          if (!it) { e.push('kp_confirmed: 候補に無いcandidate_id ' + r.candidate_id); return; }
          if (it.term !== r.term) e.push('kp_confirmed: term不一致 ' + r.candidate_id);
          if (glossOf(it).text !== r.ja_gloss || r.ja_gloss_status !== 'official') e.push('kp_confirmed: ja_gloss不一致 ' + r.candidate_id);
          if (r.category >= 1 && r.category <= 3) cnt[r.category - 1]++; else e.push('kp_confirmed: category ' + r.candidate_id);
        });
        if (cnt.join() !== '3,2,5' || (kc.selection || []).length !== allItems(d).length) e.push('kp_confirmed: 件数 ' + cnt.join('/'));
        if (!shaInfo(d).sha || kc.candidates_sha256 !== shaInfo(d).sha) e.push('kp_confirmed: candidates_sha256不一致');
        if (kc.text_sha256 !== (d.source || {}).text_sha256) e.push('kp_confirmed: text_sha256不一致');
      }
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
  return { LIMITS: LIMITS, GRAMMAR_MAX: GRAMMAR_MAX, GRAMMAR_TOP_N: GRAMMAR_TOP_N, grammarPresented: grammarPresented, grammarIds: grammarIds, normalizeGrammar: normalizeGrammar, grammarDecision: grammarDecision, grammarBlocked: grammarBlocked, hasGrammarSpec: hasGrammarSpec, chooseGrammar: chooseGrammar, chooseGrammarNone: chooseGrammarNone, choicesOf: choicesOf, grammarStatus: grammarStatus, SCHEMA: SCHEMA, terms: terms, counts: counts, allowed: allowed, grammarChosen: grammarChosen,
    grammarCanToggle: grammarCanToggle, setChoice: setChoice, setGrammar: setGrammar, newState: newState, stateKey: stateKey, summary: summary,
    buildText: buildText, buildStructured: buildStructured, buildChatGptUrl: buildChatGptUrl, buildCopyText: buildCopyText, glossOf: glossOf, reasonOf: reasonOf, itemRecord: itemRecord, candIdOf: candIdOf, kindOf: kindOf, shaInfo: shaInfo, grammarRecord: grammarRecord, GLOSS_LABEL: GLOSS_LABEL,
    validateArticle: validateArticle, validateIndex: validateIndex };
});
