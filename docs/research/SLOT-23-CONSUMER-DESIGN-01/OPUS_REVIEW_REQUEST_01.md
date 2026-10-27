# OPUS_REVIEW_REQUEST_01 (条件A: 新しい処理フロー設計。Q1〜Q3のユーザー回答後に依頼)
対象: DESIGN_01.md / CURRENT_CONSUMERS_01.md / COST_01.md。観点:
1. ハイライトの本文一致: `source_span`+`source_sentence_id`による一意特定の十分性。多重一致(同一文内2回/他文に同語)、活用形(原形used_formは本文に無い)、大文字(タイトル由来「Strategy」)、句読点・引用符・ハイフン・正規化(`_norm_match`との関係)、台本表のScript分割(X段落/Y/Z clip境界、⏸マーカー併用)で文が複数行に跨る場合。
2. 確定保護G3拡張: BLOCK条件と修正案提示の十分性。`load_verified_items(which=…)`追加がrecord_sha/content_sha互換を壊さないか。`unconsumed[]`から消費可能へ移す方式(理由コード更新 vs 別フィールド)。LR後の再突合。
3. X/Y/Z共通化: `script_block`に`highlights`を追加する共通builder案と、Xの記事別script分散(呼出側修正が必要)の妥当性。`highlights=None`でバイト同一の担保範囲。
4. 既存ページ回帰: `check_page`/lint(`_RAW_ID_RE`、table/h2判定)、標準適合check、Z `page_verify`、既存公開記事の再ビルド副作用。
5. 費用: B/Aは0円、C=約0.16円/Std記事(COST_01)。Std Part 1拡張(C)を選ぶ場合の承認仕様(CURRENT_SPEC.md:2086)との整合。
6. 区分②Std: Q1の回答に応じたSchema/validate_selection(`er119…:524`の`a2 and vocab`)変更の要否と影響。
