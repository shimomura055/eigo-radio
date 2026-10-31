# FABLE_ACCEPTANCE_01 (SELECTION-UI-TWO-TIER-01、2026-10-31、Fable独立受入。記録はSonnet代筆)

## 1. 当初目的(ユーザー原文 docs/pm/delegation_log/2026-10-31_SELECTION-UI-TWO-TIER-01_USER.md から逐語)
- :11 「これを次の**2階層構成**に変更してください。」(トップ=一覧・進捗・入口/個別=1記事x1レベルのフォーム)
- :35 「**重要：トップページには個別の選定フォームを表示しないこと。**」
- :55 「**個別ページの最上部と最下部に「Topへ戻る」ボタンを設置してください。**」
- :78 「**ページを移動しても、入力内容とDone状態が消えないことが必須です。**」
- :82 全セットDone後の一括コピーはトップから「1回の操作で全記事・全レベルの選定結果とコメントをまとめてコピー」
- :97 「無効なURLや存在しないセットについては、安全な案内表示とする。」
- :109 「実際の公開URLでの操作確認を必須」(受入条件1〜12=:111-124)
- :145 目標「PRODUCTION_WIRED（選定UIの正式利用経路への反映・公開実操作確認まで）」

## 2. 最終成果物
- 成功経路: 公開(github.io)の `user_test/selection_form_v3/index.html`(共通テンプレート)。トップ`?batch=<id>`=一覧・Done n/N・進捗バー・Std/Advリンク・一括コピー。個別`?batch=<id>&set=<slug>__<level>`=フォーム+上下「Topへ戻る」。UI版`sel-v3-rev05-a`。
- 失敗経路: 無効URL/存在しないset/別batchのsetは案内画面(Topへ戻るリンク付き)。未完了(例17/18)の一括コピーは拒否+未完了一覧(shots/T6_copy_refused_pc.png)。
- 残置: 実報告batchは未発行(次回報告時にstage1→smoke→promote→issue_batch_urlで発行)。test batchはtest:true・latest=null。

## 3. 証拠
- 実装commit: 9e8350076 / f5cca3ec0 / 61b1f3947 / 445ce77bc / 377fce501。
- 公開URL実操作: docs/research/SELECTION-UI-TWO-TIER-01/live_result_pc.json・live_result_mobile.json(base=github.io)、PC/スマホ12項目66件PASS(各33)。EVIDENCE_01.md。
- Fable自身のスクショ確認: shots/T1_top_mobile.png(トップに一覧のみ・Done 0/18・進捗バー)、shots/T3_set_bottom_mobile.png(最下部「Topへ戻る」・UI版sel-v3-rev05-a)、shots/T6_copy_refused_pc.png(17/18で拒否+未完了一覧)。
- 無変更確認: user_test/selection_form_v3/form_logic.js:492 版文字列のみ変更、:498 保存キー(eigo-kp-form-v3:b:<id>)不変。
- 受領側: er128 confirm-batch n=18受領。

## 4. 一致・不一致(項目別)
| 原文要求 | 結果 |
|---|---|
| 2階層構成(:11) | 一致 |
| トップにフォーム非表示(:35) | 一致(T1) |
| 上下「Topへ戻る」(:55) | 一致(T3、上下とも実操作PASS) |
| 入力・Done保持(:78) | 一致(戻る/再読込後も保持、保存キー不変) |
| 一括コピー1回(:82)/未完了拒否 | 一致(18/18で1回、17/18で拒否=T6) |
| 無効URL案内(:97) | 一致 |
| 公開URL実操作(:109-124) | 一致(66件PASS、Fable自身もスクショ確認) |
| 既存機能維持(:61-) | 一致(Regression PASS、form_logicロジック無変更) |
| Status目標(:145) | 一致(PRODUCTION_WIRED) |
不一致: なし。

## 5. 最終判定
**ACCEPTED、Status=PRODUCTION_WIRED(2026-10-31)**。
判定整合: 重大NG=なし
