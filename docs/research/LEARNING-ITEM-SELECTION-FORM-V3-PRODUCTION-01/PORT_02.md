# PORT_02 実装差分(委任_02、2026-10-27)
承認済みUI仕様(①②③累積上限3/5/12、同一候補1区分、文法独立枠最大2、自由コメント、9記事枠、localStorage保持)は**不変**。`counts/allowed/setChoice/setGrammar`は無改変(node fuzz 20000の参照HTML等価性testが引き続きPASS)。

| ファイル | 変更 |
|---|---|
| `user_test/selection_form_v3/index.html` | 各候補行に(1)日本語訳(ラベル: 正式訳=緑/仮訳・未確定=黄/日本語訳未生成=赤)、(2)折りたたみ「AI理由・確認用」(理由なしの場合は理由なしの種別を明示)を追加。ヒント文追加。再描画で開閉状態を保持。送信: URL不可時に黙って切り詰めず全項目入りコピー+誘導(`doCopy`)。 |
| `user_test/selection_form_v3/form_logic.js` | `glossOf/reasonOf/itemRecord/grammarRecord`追加。`buildText`は先頭5ブロックの書式を維持し確定内容詳細・文法解説全文・AI理由(確認用)節を追加。`buildStructured`をschema v2へ(DATA_MODEL_02)。`buildCopyText`は全候補入り。 |
| `user_test/selection_form_v3/data/*.json`(7件) | 再生成(AI 0): `ja_gloss/ja_gloss_status/ja_gloss_source/reason_source`追加、replay placeholder理由の除去、Trial-02に`reason_ja`再利用。 |
| `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py` | `gloss_status()/reason_info()`追加、`entry()`が新項目を出力(既存項目は不変。日本語訳・理由の出力項目追加のみ)。 |
| `docs/research/.../build_data_01.py` | Trial-02データに同項目を追加(上記関数を共有)。 |
| test | `selection_form_logic_test_01.js`(node 25→36件)、`browser_check_02.mjs`(新規19件)、`form1_selection_form_v3_test_01.py`(6→11件)。 |
