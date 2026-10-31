/* 学習項目選定フォームv3 の純ロジック(DOMなし)。参照HTML(docs/pm/Phrase_Form/eigo_radio_selection_form_reference.html)の
 * counts / allowed / payload を関数化したもの。ブラウザ(window.FormLogic)とnode(module.exports)の両方で使える。 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(); else root.FormLogic = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  var KP_EXACT = 3;                 // 2026-10-30(SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01): 区分①はちょうど3件(Done/一括コピーの条件)。②は0〜2件任意、③は累積12まで不変
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
  function newState() { return { choices: {}, grammar: {}, grammar_zero: false, comment: '', comment_phrase: '', comment_word: '', done: null }; }
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
  // KP-DIFFICULTY-4LEVEL-DISPLAY-01: 難易度は表示専用の参考情報(Gateではない)。選択/LIMITS/Done署名/照合コード(AIF1/BATCH1)には一切含めない。
  // difficulty無し(旧data)・source=not_graded(旧docの再export)は表示なし(has=false)。判定不能(unknown等)は「未判定」。
  var DIFF_LABEL = { easy: '易', medium: '中', hard: '難', rare: '激難(レア)', unknown: '未判定' };
  function difficultyOf(it) {
    var d = it && it.difficulty;
    if (!d || typeof d !== 'object' || Array.isArray(d) || d.source === 'not_graded') return { has: false, level: '', label: '' };
    var lv = Object.prototype.hasOwnProperty.call(DIFF_LABEL, d.level) ? d.level : 'unknown';
    return { has: true, level: lv, label: DIFF_LABEL[lv] };
  }
  // ---- SELECTION-UI-OCCURRENCE-COUNT-01 (occ-v1, 委任_02): 出現回数は表示専用の参考情報(Gateではない) ----
  // 選択/LIMITS/Done署名/照合コード(AIF1/BATCH1)/Claude受領形式には一切含めない(難易度と同じ扱い)。UIは数えない: exporterが焼き込んだ entry.occurrence を読むだけ。
  // 表示: `出現 6回｜本文4・Comment1・In One Line1`(0の区分は省略) / タイトルのみ=`出現 本文等0回・タイトルのみ1回` / 数えられない=`出現回数を確認できません`(0回と表示しない, Opus M5)
  //       保留=`＋似た形N（未計上）` / 区分未取得=`※Comment・Preview未集計` / 数えた形=`（put it away含む）`(スマホでも見える行内表示)。
  var OCC_ORDER = ['story', 'comment', 'preview', 'oneline'];
  var OCC_LABEL = { story: '本文', comment: 'Comment', preview: 'Preview', oneline: 'In One Line' };
  function occNum(v) { return (typeof v === 'number' && isFinite(v) && v >= 0) ? Math.floor(v) : 0; }
  function occObj(o) { return !!o && typeof o === 'object' && !Array.isArray(o); }
  function hasOccurrence(it) { var o = it && it.occurrence; return occObj(o) && occObj(o.counts); }
  function occNorm(s) { return String(s || '').toLowerCase().replace(/[’‘]/g, "'").replace(/\s+/g, ' ').trim(); }
  function occFormList(f, skip) {
    if (!occObj(f)) return [];
    return Object.keys(f).filter(function (k) { return occNum(f[k]) > 0 && skip.indexOf(occNorm(k)) < 0; }).sort(function (a, b) { return occNum(f[b]) - occNum(f[a]) || (a < b ? -1 : 1); });
  }
  // pageHas: そのページ(記事x水準)の他候補に occurrence があるか。ある=この候補だけ欠落→「確認できません」。無い=ページ単位の案内(occurrencePage)に任せ、候補行には何も出さない。
  function occurrenceOf(it, pageHas) {
    var base = { has: false, state: 'missing', text: '', total: 0, parts: [], title: 0, unc: 0, uncText: '', unavail: [], unavailText: '', note: '', tip: '' };
    if (!hasOccurrence(it)) {
      if (pageHas) { base.has = true; base.state = 'unconfirmable'; base.text = '出現回数を確認できません'; }
      return base;
    }
    var o = it.occurrence, c = o.counts, parts = [], sum = 0;
    OCC_ORDER.forEach(function (k) { var n = occNum(c[k]); sum += n; if (n > 0) parts.push({ key: k, label: OCC_LABEL[k], n: n }); });
    var title = occNum(c.title), unc = 0;
    if (occObj(o.uncertain)) Object.keys(o.uncertain).forEach(function (k) { unc += occNum(o.uncertain[k]); });
    var unavail = Array.isArray(o.unavailable) ? o.unavailable.filter(function (k) { return OCC_ORDER.indexOf(k) >= 0; }) : [];
    var state = 'ok';
    if (sum === 0) state = (title > 0 && !unavail.length) ? 'title_only' : 'unconfirmable';      // 候補なのに本文等0回=数え損ね。0回と断定しない
    var text;
    if (state === 'ok') text = '出現 ' + sum + '回｜' + parts.map(function (p) { return p.label + p.n; }).join('・') + (title > 0 ? '（ほかにタイトルに' + title + '回）' : '');
    else if (state === 'title_only') text = '出現 本文等0回・タイトルのみ' + title + '回';
    else text = '出現回数を確認できません';
    var skip = [occNorm(it.term), occNorm(it.selection_phrase)];
    var forms = occFormList(o.forms, skip), note = '';
    if (state !== 'unconfirmable' && forms.length) note = '（' + forms.slice(0, 3).join('、') + (forms.length > 3 ? '、ほか' + (forms.length - 3) + '形' : '') + '含む）';
    var uforms = occFormList(o.uncertain_forms, []);
    var tip = '同じ綴り・活用形・分離形（例 put it away）の出現を数えています。意味の違いまでは判別していません。';
    if (occObj(o.forms) && Object.keys(o.forms).length) tip += '数えた形: ' + Object.keys(o.forms).map(function (k) { return k + '×' + occNum(o.forms[k]); }).join(', ') + '。';
    if (uforms.length) tip += '未計上の似た形: ' + uforms.map(function (k) { return k + '×' + occNum(o.uncertain_forms[k]); }).join(', ') + '。';
    return { has: true, state: state, text: text, total: sum, parts: parts, title: title, unc: unc, uncText: unc ? '＋似た形' + unc + '（未計上）' : '',
      unavail: unavail, unavailText: unavail.length ? '※' + unavail.map(function (k) { return OCC_LABEL[k]; }).join('・') + '未集計' : '', note: note, tip: tip };
  }
  // ページ単位(Opus M6): 表示対象の候補に1件も occurrence が無い=集計されていないページ。
  function occurrencePage(d) {
    var items = allItems(d || {}), withOcc = items.filter(hasOccurrence).length;
    var missingAll = items.length > 0 && withOcc === 0;
    // OCC-03(残課題②): occurrence_meta が無い=出現回数表示の導入前に作られた旧データ(正常。legacy=案内表示)。meta があるのに回数が1件も無い=今回の集計が失敗(failed=警告)
    var hasMeta = !!(d && d.occurrence_meta && typeof d.occurrence_meta === 'object');
    return { n: items.length, withOcc: withOcc, anyHas: withOcc > 0, missingAll: missingAll, legacy: missingAll && !hasMeta, failed: missingAll && hasMeta };
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
      comment: normalizeComment(st.comment),
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
  // ======== 送信・コピー v3(委任_07、2026-10-27ユーザー正式決定USER_03 §B、設計=HANDOFF_DESIGN_01/COPY_FORMAT_01) ========
  // 人間可読の選定結果+照合コード1行を送る。JSON・candidate_id一覧・SHA全文はコピーに出さない(照合コード+公開データJSONから復元できる)。
  // 旧仕様(JSON同梱・buildText)は技術情報付きコピー(buildCopyText)と buildText に残置(既定非表示の補助)。
  var PREFACE = '以下はeigo-radioの学習項目選定結果です。内容(英語・日本語訳・区分・文法解説・自由コメント・照合コード)を一切変更・要約・翻訳せず、' +
    '下の「選定結果」をそのままコードブロックで返してください。修正してほしい点があればコードブロックの外に書いてください。\n\n▼選定結果\n';
  var URL_MAX = 6000;
  var MARK_BEGIN = '【解説全文】', MARK_END = '【解説ここまで】', BODY_TERM = '\n=====';
  var CAT_HEAD = { 1: '① Key Phrase', 2: '② 追加解説', 3: '③ 本文意味表示' };

  // 純JS SHA-256(同期。外部ライブラリなし。照合コードの算出用。Python hashlib.sha256 とバイト一致)
  var K256 = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2];
  function utf8Bytes(str) {
    if (typeof TextEncoder !== 'undefined') return new TextEncoder().encode(str);
    var u = unescape(encodeURIComponent(str)), a = new Uint8Array(u.length); for (var i = 0; i < u.length; i++) a[i] = u.charCodeAt(i); return a;
  }
  function sha256Hex(input) {
    var m = typeof input === 'string' ? utf8Bytes(input) : input, l = m.length;
    var nb = ((l + 9 + 63) >> 6) << 6, b = new Uint8Array(nb); b.set(m); b[l] = 0x80;
    var hi = Math.floor(l / 0x20000000), lo = (l << 3) >>> 0;
    b[nb - 8] = hi >>> 24; b[nb - 7] = (hi >>> 16) & 255; b[nb - 6] = (hi >>> 8) & 255; b[nb - 5] = hi & 255;
    b[nb - 4] = lo >>> 24; b[nb - 3] = (lo >>> 16) & 255; b[nb - 2] = (lo >>> 8) & 255; b[nb - 1] = lo & 255;
    var h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19], w = new Array(64);
    function rr(x, n) { return (x >>> n) | (x << (32 - n)); }
    for (var o = 0; o < nb; o += 64) {
      for (var t = 0; t < 16; t++) w[t] = (b[o + 4 * t] << 24) | (b[o + 4 * t + 1] << 16) | (b[o + 4 * t + 2] << 8) | b[o + 4 * t + 3];
      for (t = 16; t < 64; t++) { var s0 = rr(w[t - 15], 7) ^ rr(w[t - 15], 18) ^ (w[t - 15] >>> 3), s1 = rr(w[t - 2], 17) ^ rr(w[t - 2], 19) ^ (w[t - 2] >>> 10); w[t] = (w[t - 16] + s0 + w[t - 7] + s1) | 0; }
      var a = h[0], bb = h[1], c = h[2], dd = h[3], e = h[4], f = h[5], g = h[6], hh = h[7];
      for (t = 0; t < 64; t++) {
        var S1 = rr(e, 6) ^ rr(e, 11) ^ rr(e, 25), ch = (e & f) ^ (~e & g), t1 = (hh + S1 + ch + K256[t] + w[t]) | 0;
        var S0 = rr(a, 2) ^ rr(a, 13) ^ rr(a, 22), mj = (a & bb) ^ (a & c) ^ (bb & c), t2 = (S0 + mj) | 0;
        hh = g; g = f; f = e; e = (dd + t1) | 0; dd = c; c = bb; bb = a; a = (t1 + t2) | 0;
      }
      h[0] = (h[0] + a) | 0; h[1] = (h[1] + bb) | 0; h[2] = (h[2] + c) | 0; h[3] = (h[3] + dd) | 0; h[4] = (h[4] + e) | 0; h[5] = (h[5] + f) | 0; h[6] = (h[6] + g) | 0; h[7] = (h[7] + hh) | 0;
    }
    return h.map(function (x) { return ('00000000' + (x >>> 0).toString(16)).slice(-8); }).join('');
  }
  // 表示用: 解説全文の末尾の内部終端記号「=====」だけ外す(内容は一字も変えない)
  // 委任_08: 末尾の `\s*=+\s*$`(直前に改行が無い `。=====` も含む)を除去。本文中の=====は触らない(COPY_FORMAT_01 §6)
  var BODY_TERM_RE = /\s*=+\s*$/;
  function bodyView(body) {
    var b = String(body || '').replace(/\r\n/g, '\n');
    return BODY_TERM_RE.test(b) ? b.replace(BODY_TERM_RE, '') : b.replace(/\n+$/, '');
  }
  // 委任_08: 自由コメントの正規化(COPY_FORMAT_01 §6)。trim後が空、または既定語(NFKC+小文字で比較)のみなら「コメントなし」=''。Python側 normalize_comment と同一定数
  var COMMENT_NONE_WORDS = ['なし', '特になし', '無し', '特に無し', 'ありません', '特にありません', '-', 'ー', '―', '—', 'n/a', 'none'];
  function normalizeComment(c) {
    var t = String(c == null ? '' : c).trim();
    return (t === '' || COMMENT_NONE_WORDS.indexOf(t.normalize('NFKC').toLowerCase()) >= 0) ? '' : t;
  }
  function glossMark(status) { return status === 'official' ? '' : status === 'provisional' ? '（仮訳・未確定）' : '（日本語訳未生成）'; }
  // 照合コード AIF1-<stem>-<d6>-<c8>-<t8>-<s10>-<g10|0>-<m8|0>-<k4>(COPY_FORMAT_01 §3 / RESTORE_TOOL_SPEC_01)
  //   (旧AIF2=ニュアンス欄つきは廃止[2026-10-30]。Python側[er128_form_readable_restore]が明示拒否)
  function makeCode(stem, d6, d, selIds, gram, comment) {
    var c8 = (d.candidates_sha256 || '00000000').slice(0, 8), t8 = ((d.source || {}).text_sha256 || '00000000').slice(0, 8);
    var s10 = sha256Hex('v1\n' + selIds.map(function (x) { return x[0] + ':' + x[1]; }).join('\n')).slice(0, 10);
    var g10 = gram.length ? sha256Hex('v1\n' + gram.map(function (x) { return x[0] + ':' + x[1]; }).join('\n')).slice(0, 10) : '0';
    var m8 = comment ? sha256Hex(comment).slice(0, 8) : '0';
    var body = 'AIF1-' + stem + '-' + d6 + '-' + c8 + '-' + t8 + '-' + s10 + '-' + g10 + '-' + m8;
    return body + '-' + sha256Hex(body).slice(0, 4);
  }
  // opts.stem(データJSONのファイル名、拡張子なし) / opts.file_sha256(fetchした生バイト列のsha256 hex)。無ければ d.__stem / d.__file_sha256
  function buildReadable(d, st, opts) {
    opts = opts || {};
    var stem = opts.stem || d.__stem, fsha = opts.file_sha256 || d.__file_sha256;
    if (!stem) throw new Error('buildReadable: stem(データファイル名)が不明です');
    var d6 = fsha ? String(fsha).slice(0, 6) : '000000';
    var ch = choicesOf(d, st), its = allItems(d), L = ['記事：' + d.name + '｜' + (d.level_label || d.level || ''), ''], selIds = [];
    [1, 2, 3].forEach(function (cat) {
      L.push(CAT_HEAD[cat]);
      var got = its.filter(function (it) { return ch[it.term] === cat; });
      got.forEach(function (it) {
        var g = glossOf(it);
        L.push('- ' + it.term + '：' + (g.text || '(未生成)') + glossMark(g.status)); selIds.push([cat, candIdOf(it)]);
      });
      if (!got.length) L.push('（選択なし）');
      L.push('');
    });
    var gs = summary(d, st).grammar;
    if (!gs.length) L.push('文法：選定なし');
    gs.forEach(function (g) { L.push('文法：' + g.title, MARK_BEGIN, bodyView(g.body), MARK_END); });
    L.push('');
    var com = normalizeComment(opts.comment !== undefined ? opts.comment : st.comment);   // 一括画面は合成コメント(opts.comment)を渡す。未指定=従来どおりst.comment
    L.push('自由コメント：' + (com || 'なし'));
    L.push('', '照合コード(変更しないでください)：' + makeCode(stem, d6, d, selIds, gs.map(function (g) { return [g.candidate_id || g.id, g.explanation_sha256 || '']; }), com));
    return L.join('\n');
  }
  // 「ChatGPTへ送信」: 送信文(PREFACE+人間可読)は常にクリップボードへ。URL(?q=)が閾値内なら本文入りURL、超過なら url=null(=chatgpt.comを開いて貼付案内。エラー扱いにしない)
  function buildChatGptUrl(d, st, now, opts) {
    var text = PREFACE + buildReadable(d, st, opts), url = 'https://chatgpt.com/?q=' + encodeURIComponent(text);
    return { text: text, url: url.length <= URL_MAX ? url : null, url_length: url.length, mode: url.length <= URL_MAX ? 'url' : 'paste' };
  }
  // 技術情報付きコピー(補助・既定非表示): 従来の人間可読要約+JSON(candidates_all付き)。er128 confirm --from-form へ直接渡せる逃げ道
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
      if (d.nuance_spec || d.nuance || d.nuance_note_ja) e.push('nuance: 旧形式データです(ニュアンス解説コーナーは2026-10-30に廃止。フォームデータを再出力してください)');
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
  // ======== 一括選定画面(SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 委任_02A、設計=DESIGN_01.md + Opus条件Aレビュー反映M1-M5) ========
  var SIG_VER = 'sig1';
  // 保存状態の正規化(下位互換: 旧state[choices/grammar/grammar_zero/comment]を読み、未知フィールドは保持。旧commentは「追加指示(全体)」として保持)
  function normalizeState(raw) {
    var o = (raw && typeof raw === 'object' && !Array.isArray(raw)) ? Object.assign({}, raw) : {};
    o.choices = (o.choices && typeof o.choices === 'object' && !Array.isArray(o.choices)) ? o.choices : {};
    o.grammar = (o.grammar && typeof o.grammar === 'object' && !Array.isArray(o.grammar)) ? o.grammar : {};
    o.grammar_zero = o.grammar_zero === true;
    ['comment', 'comment_phrase', 'comment_word'].forEach(function (k) { if (typeof o[k] !== 'string') o[k] = ''; });
    o.done = (o.done && typeof o.done === 'object' && typeof o.done.sig === 'string') ? { sig: o.done.sig, at: String(o.done.at || '') } : null;
    return o;
  }
  // M4 区切り注入対策: コメントが照合コード行・一括区切り・AIF1/BATCH1コードを偽装できないよう置換する(内容の他部分は不変)
  function sanitizeComment(text) {
    var t = String(text == null ? '' : text).replace(/\r\n?/g, '\n');
    t = t.replace(/═{2,}/g, '──').replace(/照合コード/g, '照合 コード').replace(/AIF1-/g, 'AIF1_').replace(/BATCH1-/g, 'BATCH1_');
    return t.split('\n').map(function (l) { return l.replace(/\s+$/, ''); }).join('\n');
  }
  function commentPart(raw) { return sanitizeComment(normalizeComment(raw)).trim(); }
  // 3欄→単一合成文字列(AIF1のm8互換のため単一文字列)。空欄は行ごと省略。全空=''(=従来の「なし」と同一)
  function composeComment(st) {
    var L = [], p = commentPart(st.comment_phrase), w = commentPart(st.comment_word), g = commentPart(st.comment);
    if (p) L.push('【フレーズ】' + p);
    if (w) L.push('【単語】' + w);
    if (g) L.push('【追加指示(全体)】' + g);
    return L.join('\n');
  }
  // 単体コピー(従来形式維持): フレーズ/単語コメントが無ければ従来どおり自由コメントそのまま(ラベル無し)
  function singleComment(st) {
    return (commentPart(st.comment_phrase) || commentPart(st.comment_word)) ? composeComment(st) : normalizeComment(st.comment);
  }
  // M1 Done署名: stem/d6/正規化choices(term順)/文法/3コメント欄/SIG_VER。内容が1つでも変わればsigが変わりDoneが自動解除される
  function doneSig(d, st) {
    var tl = terms(d), ch = choicesOf(d, st);
    var gids = grammarIds(d), gsel = grammarChosen(st.grammar, gids);
    var arr = [SIG_VER, d.__stem || '', d.__file_sha256 ? String(d.__file_sha256).slice(0, 6) : '000000',
      tl.map(function (t) { return t + ':' + (ch[t] || 0); }), gsel, st.grammar_zero === true && !gsel.length,
      commentPart(st.comment_phrase), commentPart(st.comment_word), commentPart(st.comment)];
    return sha256Hex(JSON.stringify(arr));
  }
  // Done条件(具体的エラー配列。コメントは任意): ①ちょうど3件(kp_confirmedは確定3件で自動充足)/文法決定済み/validateArticle/提示候補>=3
  function doneErrors(d, st) {
    if (!d) return ['この記事枠にはデータがありません。'];
    var e = [], ve = validateArticle(d);
    if (ve.length) e.push('候補データの形式エラー: ' + ve.join(', '));
    var tl = terms(d);
    if (tl.length < KP_EXACT) e.push('候補不足(' + tl.length + '件)のためKey Phraseを' + KP_EXACT + '件選べません。品質基準を下げず停止します。候補の補充が必要です。');
    var c = counts(choicesOf(d, st), tl);
    if (c[0] !== KP_EXACT) e.push('① Key Phraseはちょうど' + KP_EXACT + '件必要です(現在' + c[0] + '件)。');
    if (grammarBlocked(d, st)) e.push('文法が未決定です。Top 1・Top 2のどちらかを1件選ぶか「適切な候補なし(0件)」を選んでください。');
    return e;
  }
  // 'done'(署名一致+エラー無し) | 'stale'(Done済みだった内容が変わった=要再確認) | 'todo'
  function doneStatus(d, st) {
    if (!d) return 'todo';
    var ok = !!(st.done && st.done.sig && st.done.sig === doneSig(d, st));
    if (ok) return doneErrors(d, st).length ? 'todo' : 'done';
    return st.done && st.done.sig ? 'stale' : 'todo';
  }
  // 「残りをすべて選択」(純関数。stは変更しない): 未選択の提示候補を表示順に③へ。allowed()を必ず通す。
  // 無効条件: kp_confirmed / データ不正 / 候補なし / ①が3件未満 / 未選択0。戻り値 { ok, reason, choices(新), added[], blocked[] }
  function selectRemaining(d, st, tl) {
    var termList = tl || (d ? terms(d) : []);
    var fail = function (r) { return { ok: false, reason: r, choices: Object.assign({}, (st && st.choices) || {}), added: [], blocked: [] }; };
    if (!d || validateArticle(d).length) return fail('invalid_data');
    if (d.kp_confirmed) return fail('kp_confirmed');
    if (!termList.length) return fail('no_candidates');
    var work = { choices: Object.assign({}, (st && st.choices) || {}) };
    if (counts(work.choices, termList)[0] < KP_EXACT) return fail('kp_lt3');
    var rest = termList.filter(function (t) { return !(work.choices[t] >= 1 && work.choices[t] <= 3); });
    if (!rest.length) return fail('nothing_left');
    var added = [], blocked = [];
    rest.forEach(function (t) { if (allowed(work.choices, termList, t, 3)) { work.choices[t] = 3; added.push(t); } else blocked.push(t); });
    return { ok: added.length > 0, reason: added.length ? '' : 'blocked', choices: work.choices, added: added, blocked: blocked };
  }
  // ---- 対象バッチ ----
  // articles.json の任意キー batch:{id,date,members:[...]}。members要素=データファイルstem(例 moon_shrinking__b1b__prod。02Bのexport/restore_batchの契約)。slug / "slug__level" も許容。無ければ null(=一括コピー不可・M3 fail-closed。全35枠フォールバックはしない)
  function batchSets(idx) {
    var b = idx && idx.batch;
    if (!b || !Array.isArray(b.members) || !b.members.length) return null;
    var m = {}; b.members.forEach(function (x) { m[String(x)] = 1; });
    var stemOf = function (a) { return String(a.data || '').replace(/^.*\//, '').replace(/\.json$/, ''); };
    var sets = (idx.articles || []).filter(function (a) { return a.data && (m[stemOf(a)] || m[a.slug] || m[stateKey(a)]); });   // members=データファイル名stem(02B export/restore_batchと同一)。slug / slug__level も許容
    return sets.length ? { id: String(b.id || ''), date: b.date || '', members: sets } : null;
  }
  // items=[{entry,d,st}]。未完了セット(データ無し/署名不一致/エラー)を列挙
  function batchCopyErrors(items) {
    var out = [];
    (items || []).forEach(function (it) {
      var name = it.entry.name, lv = it.entry.level_label || it.entry.level, key = stateKey(it.entry);
      if (!it.d) { out.push({ key: key, name: name, level: lv, errors: ['データを読み込めていません。'] }); return; }
      var errs = doneErrors(it.d, it.st);
      if (!errs.length && doneStatus(it.d, it.st) !== 'done') errs = ['Doneになっていません(内容変更後は再度Doneを押してください)。'];
      if (errs.length) out.push({ key: key, name: name, level: lv, errors: errs });
    });
    return out;
  }
  var BATCH_PREFACE = PREFACE.replace('選定結果です', '選定結果(一括)です');
  function extractCode(readable) {
    var m = /照合コード\(変更しないでください\)：(AIF1-\S+)/.exec(readable);
    return m ? m[1] : null;
  }
  // BATCH1-<N>-<全照合コード(SET順)を区切り無しで連結したsha256の先頭10桁>
  function batchCode(codes) { return 'BATCH1-' + codes.length + '-' + sha256Hex(codes.join('')).slice(0, 10); }
  // DESIGN_01 §2 のコピー形式。各SETは buildReadable をそのまま(コメントのみ合成文字列)。fail-closed: 1件でも未完了なら例外
  function buildBatchReadable(items, batch, now) {
    if (!batch || batch.id === undefined || !items || !items.length) throw new Error('buildBatchReadable: batchが無いため一括コピーを作りません');
    var bad = batchCopyErrors(items);
    if (bad.length) throw new Error('buildBatchReadable: 未完了セットがあります: ' + bad.map(function (b) { return b.name + '｜' + b.level; }).join(', '));
    var N = items.length, L = [BATCH_PREFACE.replace(/\n+$/, ''), '一括ヘッダ:', '件数=' + N + ' / 生成=' + (now || new Date().toISOString()) + ' / バッチ=' + batch.id, ''], codes = [];
    items.forEach(function (it, i) {
      var r = buildReadable(it.d, it.st, { comment: composeComment(it.st) });
      var c = extractCode(r); if (!c) throw new Error('buildBatchReadable: 照合コードを抽出できません ' + stateKey(it.entry));
      codes.push(c);
      L.push('════ SET ' + (i + 1) + '/' + N + ' ｜ ' + (it.d.__stem || stateKey(it.entry)) + ' ════', r, '');   // 区切り名=データファイルstem(=照合コードのstem。02B restore_batchが一致を検査)
    });
    L.push('════ END 合計' + N + '件 / ' + batchCode(codes) + ' ════');
    return L.join('\n');
  }

  // ======== 報告単位batch(SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 委任_04、DESIGN_03 + Opus M1-M14) ========
  // M13: UI資産の版。live smokeがローカルHEADと一致を確認する(index.htmlもこの値を表示)
  var ASSET_VERSION = 'sel-v3-rev06-b';
  // M6: batch id。UI・publish tool・er128の3箇所で同一の正規表現(パストラバーサル対策)
  var BATCH_ID_RE = /^[a-z0-9][a-z0-9_-]{2,63}$/;
  function validBatchId(id) { return typeof id === 'string' && BATCH_ID_RE.test(id); }
  function stemOfEntry(a) { return String((a && a.data) || '').replace(/^.*\//, '').replace(/\.json$/, ''); }
  // 状態の名前空間(報告単位)。dev=true は ?dev=all 専用(報告状態と混ざらない)
  function storeKey(batchId, dev) { return dev ? 'eigo-kp-form-v3:dev' : 'eigo-kp-form-v3:b:' + batchId; }
  // M1: batch解決=stem完全一致のみ(slug一致・slug__level緩和なし)。1件でも未解決/重複ならok:false(部分表示しない)
  function resolveBatch(idx, doc) {
    if (!doc || typeof doc !== 'object' || doc.schema !== 'eigo_radio_batch_v1') return { ok: false, code: 'bad_doc', missing: [], dup: [] };
    if (!validBatchId(doc.id)) return { ok: false, code: 'bad_id', missing: [], dup: [] };
    if (!Array.isArray(doc.members) || !doc.members.length) return { ok: false, code: 'no_members', missing: [], dup: [] };
    var byStem = Object.create(null); ((idx && idx.articles) || []).forEach(function (a) { if (a.data) byStem[stemOfEntry(a)] = a; });
    var seen = Object.create(null), sets = [], missing = [], dup = [], keys = Object.create(null), kdup = [];
    doc.members.forEach(function (m) {
      var s = String(m);
      if (seen[s]) { dup.push(s); return; } seen[s] = 1;
      var a = byStem[s] || null;
      if (!a) { missing.push(s); return; }
      var k = stateKey(a); if (keys[k]) kdup.push(s); keys[k] = 1; sets.push(a);
    });
    if (missing.length) return { ok: false, code: 'member_unresolved', missing: missing, dup: dup };
    if (dup.length) return { ok: false, code: 'member_dup', missing: [], dup: dup };
    if (kdup.length) return { ok: false, code: 'state_key_dup', missing: [], dup: kdup };
    return { ok: true, batch: { id: doc.id, date: doc.date || '', report_ref: doc.report_ref || '', test: !!doc.test, members: sets, shas: (doc.member_sha256 && typeof doc.member_sha256 === 'object') ? doc.member_sha256 : {} } };
  }
  // M2/M5: URL→画面の決定(純関数)。p={batch,a,dev}、bidx=data/batches/index.json(無ければnull)
  function resolveRoute(p, bidx) {
    p = p || {};
    var latest = (bidx && validBatchId(bidx.latest)) ? bidx.latest : null;
    if (p.dev === 'all') return { mode: 'dev', latest: latest };
    if (p.batch !== undefined && p.batch !== null && p.batch !== '') {
      if (!validBatchId(p.batch)) return { mode: 'error', code: 'bad_batch_id', latest: latest };
      return { mode: 'batch', id: p.batch, latest: latest, notLatest: (latest && latest !== p.batch) ? latest : null, aParam: p.a || null, fromLatest: false };
    }
    if (p.a) return { mode: 'legacy_a', latest: latest, aParam: p.a };
    if (latest) return { mode: 'batch', id: latest, latest: latest, notLatest: null, aParam: null, fromLatest: true };
    return { mode: 'none', latest: null };
  }
  // M4: 一覧=test:trueを除外
  function listBatches(bidx) { return ((bidx && Array.isArray(bidx.batches)) ? bidx.batches : []).filter(function (b) { return b && validBatchId(b.id) && !b.test; }); }
  // M10: 公開時に記録したdata sha256とUIが読んだsha256の不一致stem
  function shaMismatches(batch, loadedByStem) {
    var out = [];
    Object.keys(batch.shas || {}).forEach(function (s) { if (loadedByStem[s] && loadedByStem[s] !== batch.shas[s]) out.push(s); });
    return out;
  }
  // 一括コピーに入る各SETのstemが、batch members(stem)と順序・件数まで完全一致するか(欠落・重複・余剰の検査)
  function batchCopyStems(text) {
    var out = [], re = /════ SET (\d+)\/(\d+) ｜ (\S+) ════/g, m;
    while ((m = re.exec(text))) out.push({ i: Number(m[1]), n: Number(m[2]), stem: m[3] });
    return out;
  }

  return {
    LIMITS: LIMITS, GRAMMAR_MAX: GRAMMAR_MAX, GRAMMAR_TOP_N: GRAMMAR_TOP_N, grammarPresented: grammarPresented, grammarIds: grammarIds, normalizeGrammar: normalizeGrammar, grammarDecision: grammarDecision, grammarBlocked: grammarBlocked, hasGrammarSpec: hasGrammarSpec, chooseGrammar: chooseGrammar, chooseGrammarNone: chooseGrammarNone, choicesOf: choicesOf, grammarStatus: grammarStatus, SCHEMA: SCHEMA, terms: terms, counts: counts, allowed: allowed, grammarChosen: grammarChosen,
    grammarCanToggle: grammarCanToggle, setChoice: setChoice, setGrammar: setGrammar, newState: newState, stateKey: stateKey, summary: summary,
    buildText: buildText, buildStructured: buildStructured, buildChatGptUrl: buildChatGptUrl, buildCopyText: buildCopyText, buildReadable: buildReadable, normalizeComment: normalizeComment, COMMENT_NONE_WORDS: COMMENT_NONE_WORDS, sha256Hex: sha256Hex, makeCode: makeCode, PREFACE: PREFACE, URL_MAX: URL_MAX, bodyView: bodyView, glossOf: glossOf, reasonOf: reasonOf, difficultyOf: difficultyOf, DIFF_LABEL: DIFF_LABEL, occurrenceOf: occurrenceOf, occurrencePage: occurrencePage, hasOccurrence: hasOccurrence, OCC_LABEL: OCC_LABEL, itemRecord: itemRecord, candIdOf: candIdOf, kindOf: kindOf, shaInfo: shaInfo, grammarRecord: grammarRecord, GLOSS_LABEL: GLOSS_LABEL,
    validateArticle: validateArticle, validateIndex: validateIndex,
    KP_EXACT: KP_EXACT, SIG_VER: SIG_VER, normalizeState: normalizeState, doneSig: doneSig, doneStatus: doneStatus, doneErrors: doneErrors, selectRemaining: selectRemaining,
    sanitizeComment: sanitizeComment, composeComment: composeComment, singleComment: singleComment, batchSets: batchSets, batchCopyErrors: batchCopyErrors, buildBatchReadable: buildBatchReadable, batchCode: batchCode, extractCode: extractCode, BATCH_PREFACE: BATCH_PREFACE,
    ASSET_VERSION: ASSET_VERSION, BATCH_ID_RE: BATCH_ID_RE, validBatchId: validBatchId, stemOfEntry: stemOfEntry, storeKey: storeKey, resolveBatch: resolveBatch, resolveRoute: resolveRoute, listBatches: listBatches, shaMismatches: shaMismatches, batchCopyStems: batchCopyStems };
});
