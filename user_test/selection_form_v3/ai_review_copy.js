/* AIレビュー用一括コピーの純ロジック(DOMなし)。SELECTION-FORM-AI-REVIEW-COPY-PRODUCTION-WIRING-01(正式配線)。
 * ブラウザ(window.AIReviewCopy)とnode(module.exports)の両方で使える。
 * 方針: 承認済み定型文(ai_review_template_01.md)は逐語。レベルに応じて差し替えるのは、Standardのときの下記2行(行単位の完全一致・各1回のみ)だけ。
 *   (1)「対象レベルはAdvanced（上級学習者）です。」 (2)④「上級学習者にとっての新規学習価値」行(Fable解釈=ユーザー原文§1-2/§3の『評価指示がAdvancedのまま』防止)。
 * TODAYS-EXPRESSION-CROSS-FAMILY-PRODUCTION-01: Today's Expressionのデータ(別sidecar `_todays_expression.json`)があるセットのコピーにだけ、テンプレート本体を変えず条件付き行挿入で
 *   冒頭1段落・①に4行・③に修正コメント形式1行・④にランク外1行を追加し、評価対象の末尾へTE 4点(英語表現・日本語の意味・英語例文・例文の日本語訳)を足す。各行はちょうど1回。②⑤は不変。TEデータが無いセットの出力は従来とバイト同一。
 * Advancedの出力は定型文と完全に同一(差分0行)。元の英文は画面に出さず、コピー文字列にのみ入れる。候補の自動修正・自動採用は行わない。 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(); else root.AIReviewCopy = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  // M-5: 承認済み定型文(LF正規化)のsha256。公開ページが取得した定型文がこれと違えばコピーを拒否する(古いキャッシュ・誤編集対策)
  var TEMPLATE_SHA256 = 'bd9e1fb2e054f27ae723b91bf5ce57e7770b239bd5990cb1628a2b8226a355d1';
  var SCHEMA = 'eigo_radio_ai_review_data_v2';
  var LEVEL_JA = { a2: 'Standard（中級学習者）', b1b: 'Advanced（上級学習者）' };
  var PLACEHOLDER_HEAD = '# 評価対象\n';
  // 行単位の完全一致で置換する対象行(定型文の原文行)と、Standard用の置換後の行
  var L57 = '対象レベルはAdvanced（上級学習者）です。';
  var L61 = '1. **上級学習者にとっての新規学習価値**：すでに知っている可能性が高い基本表現より、学ぶことで英語表現の幅が広がるものを評価する。';
  var LEVEL_SUBS = {
    b1b: [],
    a2: [[L57, '対象レベルはStandard（中級学習者）です。'],
         [L61, '1. **中級学習者にとっての新規学習価値**：Standard（中級）学習者がまだ知らない・使いこなせていない可能性が高く、学ぶことで実際に使える表現が増えるものを評価する。難しさや珍しさそのものは評価しない。']]
  };

  // ---- Today's Expression(TE)用の条件付き挿入。承認済み定型文(TEMPLATE_SHA256)は無変更。ここが「TEが入った実効Promptの追加行」の唯一の定義(ev/ai_review_copy_*.txtが実効Prompt全文)。
  var TE_SCHEMA = 'eigo_radio_ai_review_te_v1';
  var A_INTRO = '厳格な校閲ではありません。明らかな問題だけを指摘し、回答は簡潔にしてください。';
  var A_PH = '- Phraseの切り出し方に問題がないか。';
  var A_RANK = '- 元のPhrase／Wordを全件、重複・欠落なく掲載する。';
  var A_FIX = '日本語訳だけの問題なら、英語表現は変更しないでください。';
  var TE_INTRO = ['', '評価対象に「Today\'s Expression（本日の表現）」が含まれる場合は、その自然さと正確さの確認だけを行ってください。Today\'s Expressionは学習有益度ランキングの対象外（ランク外）です。'];
  var TE_CHECK = ['- Today\'s Expressionがある場合：英語表現が自然か。', '- Today\'s Expressionがある場合：日本語の意味が正確か。',
                  '- Today\'s Expressionがある場合：英語例文の自然さ・意味・文脈が正確か。', '- Today\'s Expressionがある場合：例文の日本語訳が正確か。'];
  var TE_FIX = ['', 'Today\'s Expressionに明らかな問題がある場合も、既存と同じ形式で修正コメントを示してください。'];
  var TE_RANK = ['- Today\'s Expressionはランキングに含めない（ランク外）。'];
  var TE_FIELDS = ['expression', 'meaning_ja', 'example_en', 'example_ja'];

  function levelWord(level) { return LEVEL_JA[level] || null; }
  function normLF(s) { return String(s).replace(/\r\n/g, '\n'); }

  /* 定型文のレベル別差し替え。未知level・対象行が(完全一致で)ちょうど1回でない場合は例外(誤レベルのコピーを作らない) */
  function applyLevel(template, level) {
    if (!Object.prototype.hasOwnProperty.call(LEVEL_SUBS, level)) throw new Error('未知のレベル: ' + level);
    var subs = LEVEL_SUBS[level];
    var lines = normLF(template).split('\n');
    // 定型文自体の健全性: 差し替え元の2行は(Standard/Advancedどちらでも)ちょうど1回ずつ存在するはず
    [L57, L61].forEach(function (o) {
      var n = lines.filter(function (x) { return x === o; }).length;
      if (n !== 1) throw new Error('定型文の対象行が行単位の完全一致で1箇所ではありません(' + n + '): ' + o.slice(0, 20));
    });
    subs.forEach(function (p) {
      var idx = -1;
      lines.forEach(function (x, i) { if (x === p[0]) idx = i; });
      lines[idx] = p[1];
    });
    return lines.join('\n');
  }

  function itemBlock(kindLabel, i, it, rv) {
    var L = ['### ' + kindLabel + ' ' + (i + 1)];
    L.push('- 英語表現：' + it.term);
    if (it.selection_phrase && it.selection_phrase !== it.term) L.push('- 本文中の形：' + it.selection_phrase);
    var gloss = (it.ja_gloss !== undefined ? it.ja_gloss : it.meaning_ja) || '';
    L.push('- 日本語訳：' + (gloss || '（未生成）'));
    var st = it.ja_gloss_status;
    if (gloss && st && st !== 'official') L.push('- 訳の状態：仮訳・未確定');
    L.push('- 元の英文（該当文）：' + rv.sentence);
    if (rv.prev) L.push('- 前の文：' + rv.prev);
    if (rv.next) L.push('- 後の文：' + rv.next);
    return L.join('\n');
  }

  function candId(it) { return it.candidate_id || it.id || null; }
  function presented(d) { return (d.phrases || []).concat(d.words || []); }

  /* 評価対象ブロック(記事名・Family・レベル・全Phrase/Word)。rvDoc=ai_reviewデータ(items[candidate_id])。guard通過後にだけ呼ぶ */
  function buildTargetBlock(d, rvDoc) {
    var items = rvDoc.items;
    var L = ['- 記事名：' + d.name, '- Family：' + d.family, '- レベル：' + (d.level_label || String(levelWord(d.level) || d.level).split('（')[0]) + '（' + d.level + '）', ''];
    [['phrases', 'Phrase'], ['words', 'Word']].forEach(function (p) {
      var arr = d[p[0]] || [];
      L.push('## ' + p[1] + '候補（' + arr.length + '件）', '');
      arr.forEach(function (it, i) { L.push(itemBlock(p[1], i, it, items[candId(it)]), ''); });
    });
    return L.join('\n').replace(/\n+$/, '\n');
  }

  /* 完全一致行(ちょうど1回)の直後へ挿入。0回/複数回は例外(テンプレートが変わったのにTE挿入が黙って抜ける/重複するのを防ぐ) */
  function insertAfterLine(lines, anchor, add) {
    var idx = [];
    lines.forEach(function (x, i) { if (x === anchor) idx.push(i); });
    if (idx.length !== 1) throw new Error('定型文のTE挿入位置が行単位の完全一致で1箇所ではありません(' + idx.length + '): ' + anchor.slice(0, 24));
    lines.splice.apply(lines, [idx[0] + 1, 0].concat(add));
  }
  function applyTe(template) {
    var lines = normLF(template).split('\n');
    insertAfterLine(lines, A_INTRO, TE_INTRO);
    insertAfterLine(lines, A_PH, TE_CHECK);
    insertAfterLine(lines, A_FIX, TE_FIX);
    insertAfterLine(lines, A_RANK, TE_RANK);
    return lines.join('\n');
  }

  /* TE sidecarの整合ガード(fail-closed)。戻り値=エラー文字列の配列(空=OK)。teDocが無い(=404)場合は呼ばない。 */
  function teGuard(te, d, entryStem) {
    var e = [];
    if (!te || typeof te !== 'object') return ['Today\'s Expressionのデータが不正です'];
    if (te.schema !== TE_SCHEMA) e.push('Today\'s Expressionデータの形式が違います');
    if (te.stem !== entryStem) e.push('Today\'s Expressionデータの対象セット(stem)が違います: ' + te.stem + ' != ' + entryStem);
    if (te.level !== d.level) e.push('Today\'s Expressionデータのレベルが違います: ' + te.level + ' != ' + d.level);
    if (!Array.isArray(te.items)) { e.push('Today\'s Expressionのitemsがありません'); return e; }
    if (te.n_items !== te.items.length) e.push('Today\'s Expressionの件数が一致しません(n_items=' + te.n_items + ' / ' + te.items.length + ')');
    if (te.items.length > 2) e.push('Today\'s Expressionが3件以上あります');
    te.items.forEach(function (it, i) {
      TE_FIELDS.forEach(function (k) { if (!it || typeof it[k] !== 'string' || !it[k].trim()) e.push('Today\'s Expression ' + (i + 1) + 'の' + k + 'が空です'); });
    });
    return e;
  }

  function teBlock(te) {
    var L = ['## Today\'s Expression（本日の表現。ランキング対象外）', ''];
    te.items.forEach(function (it, i) {
      L.push('### Today\'s Expression ' + (i + 1), '- 英語表現：' + it.expression, '- 日本語の意味：' + it.meaning_ja, '- 英語例文：' + it.example_en, '- 例文の日本語訳：' + it.example_ja, '');
    });
    return L.join('\n').replace(/\n+$/, '\n');
  }

  /* コピー前の整合ガード。戻り値=エラー文字列の配列(空=OK)。entryStem=記事枠のstem、d=ロード済みdata(d.__file_sha256=fetch生バイトのLF正規化sha)。
   * M-1: candidates_sha256はdata側と同値でなければ拒否(生成側が候補docから再計算して一致を保証済み。ここはsidecar取り違え検出)
   * M-4: data側の一意ID数 == phrases+words件数 == sidecar.n_items == itemsのキー数(JSONの重複キーはパース時に潰れるため件数で検出) */
  function guard(d, rvDoc, entryStem) {
    var e = [];
    if (!d) return ['このセットの候補データがありません'];
    if (!rvDoc || typeof rvDoc !== 'object') return ['AIレビュー用データがありません'];
    if (rvDoc.schema !== SCHEMA) e.push('AIレビュー用データの形式が違います');
    if (rvDoc.stem !== entryStem) e.push('AIレビュー用データの対象セット(stem)が違います: ' + rvDoc.stem + ' != ' + entryStem);
    if (levelWord(d.level) === null) e.push('未知のレベル: ' + d.level);
    if (rvDoc.level !== d.level) e.push('AIレビュー用データのレベルが違います: ' + rvDoc.level + ' != ' + d.level);
    if (!d.__file_sha256 || rvDoc.data_file_sha256 !== d.__file_sha256) e.push('候補データが更新されています(AIレビュー用データのdata shaが不一致)。再生成が必要です');
    var dcs = d.candidates_sha256 === undefined ? null : d.candidates_sha256;
    var rcs = rvDoc.candidates_sha256 === undefined ? null : rvDoc.candidates_sha256;
    if (rcs !== dcs) e.push('候補docのshaが不一致です');
    var list = presented(d), ids = list.map(candId), uniq = {};
    ids.forEach(function (x) { if (!x) e.push('candidate_idのない候補があります'); uniq[x] = 1; });
    var nUniq = Object.keys(uniq).length;
    var items = (rvDoc.items && typeof rvDoc.items === 'object') ? rvDoc.items : null;
    if (!items) { e.push('AIレビュー用データのitemsがありません'); return e; }
    var nKeys = Object.keys(items).length;
    if (nUniq !== list.length) e.push('候補IDが重複しています(一意' + nUniq + '/' + list.length + '件)');
    if (rvDoc.n_items !== list.length) e.push('AIレビュー用データの件数が一致しません(n_items=' + rvDoc.n_items + ' / 候補' + list.length + ')');
    if (nKeys !== list.length) e.push('AIレビュー用データのitems件数が一致しません(' + nKeys + ' / 候補' + list.length + ')');
    list.forEach(function (it) {
      var r = items[candId(it)];
      if (!r) { e.push('元の英文がない候補: ' + it.term); return; }
      if (r.term !== it.term) e.push('候補の表現が一致しません: ' + it.term + ' != ' + r.term);
      if (r.kind !== (it.kind || (d.phrases.indexOf(it) >= 0 ? 'phrase' : 'word'))) e.push('候補の種別が一致しません: ' + it.term);
      if (!r.sentence || !String(r.sentence).trim()) e.push('元の英文が空です: ' + it.term);
    });
    Object.keys(items).forEach(function (k) { if (!uniq[k]) e.push('余剰のitem: ' + k); });
    return e;
  }

  /* M-5: 取得した定型文(LF正規化)のshaが承認済みの固定値と一致するか。shaFn=文字列->sha256 hex。一致=null、不一致=エラー文字列 */
  function checkTemplate(text, shaFn) {
    var got = shaFn(normLF(text));
    return got === TEMPLATE_SHA256 ? null : '承認済み定型文と一致しません(sha ' + String(got).slice(0, 8) + '… != ' + TEMPLATE_SHA256.slice(0, 8) + '…)。ページを再読込してください';
  }

  /* teDoc: 省略/null=TEデータなし(出力は従来とバイト同一)。n_items=0のTE docも「TE追記なし」と同じ扱い(Todays Expressionが0件の記事のPromptに存在しないTEを言及しない)。 */
  function buildCopyText(template, d, rvDoc, entryStem, teDoc) {
    var tpl = normLF(template);
    if (tpl.slice(-PLACEHOLDER_HEAD.length) !== PLACEHOLDER_HEAD) throw new Error('定型文の末尾が「# 評価対象」ではありません');
    var errs = guard(d, rvDoc, entryStem);
    if (errs.length) throw new Error(errs.slice(0, 3).join(' / '));
    var useTe = !!teDoc;
    if (useTe) {
      var te = teGuard(teDoc, d, entryStem);
      if (te.length) throw new Error(te.slice(0, 3).join(' / '));
      useTe = teDoc.items.length > 0;
    }
    var head = applyLevel(tpl, d.level);
    if (!useTe) return head + '\n' + buildTargetBlock(d, rvDoc);
    return applyTe(head) + '\n' + buildTargetBlock(d, rvDoc) + '\n' + teBlock(teDoc);
  }

  return { TEMPLATE_SHA256: TEMPLATE_SHA256, SCHEMA: SCHEMA, LEVEL_SUBS: LEVEL_SUBS, L57: L57, L61: L61, levelWord: levelWord, applyLevel: applyLevel,
    buildTargetBlock: buildTargetBlock, buildCopyText: buildCopyText, checkTemplate: checkTemplate, guard: guard, teGuard: teGuard, applyTe: applyTe, teBlock: teBlock, TE_SCHEMA: TE_SCHEMA, candId: candId, presented: presented };
});
