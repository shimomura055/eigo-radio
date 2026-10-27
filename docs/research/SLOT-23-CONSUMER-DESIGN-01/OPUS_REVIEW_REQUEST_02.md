# OPUS_REVIEW_REQUEST_02 条件A(新しい構造・処理フローの設計)独立レビュー依頼
正本の条件=`docs/pm/PM_GOVERNANCE.md` 11-3(条件A)。OPUS_REVIEW_REQUEST_01(Std②案選定向け)は**失効**(ユーザー正式決定で案Cが確定したため)。本依頼は`DESIGN_02.md`に対するもの。コード編集0・API 0。

## 依頼対象(読む順)
1. `docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md`(ユーザー原文。これが正)
2. `docs/research/SLOT-23-CONSUMER-DESIGN-01/DESIGN_02.md`(+`SPEC_CONFLICT_02.md`、`IMPL_PLAN_02.md`、`COST_02.md`)
3. 参照コード: `er003_kp_general_explanation_01.py`、`er105_kp_fulltext_selector_01.py:157-200,248-282`(`_phrase_pattern`/`locate_phrase`/`selection_resolution_method`)、`er128_kp_confirmed_content_01.py`(`_item_from_cand`:238/`build_items`:252/`verify_outputs`:764/`cmd_from_form`:1317/`load_verified_items`:1258)、`er119_kp_human_review_01.py`(:524-530,:564-580,:1020-1060,:1135)、`er_user_listening_page_common_01.py`(`script_block`/`check_page`)、`er120_part2_wiring_01.py:497-531`、Family別page builder(`er063…:2528,2557-2610`、`er121_family_y_audio_01.py:1467`、`er019_family_x_audio_production_runner_01.py:3017-3150`、`tools/build_aif3_listening_page_01.py`)

## レビュー論点(各論点にPASS/修正要/設計変更要を付けて返してください)
1. **照合の正確性**(DESIGN_02 §B-3): `source_sentence_id`→`build_sentence_units`→`_phrase_pattern(source_span)`の最初の一致、という手順は、`carry over→carried over`等の活用形・大小・引用符・apostrophe・複数出現(AI島Std`Strategy`S2・3回、Adv`technique`S25・3回の`first_of_N`)で、候補生成が選んだ出現と常に同一か。表示本文(X`parts.json`/Y`segments`/Zクリップ連結)への写像の落とし穴(Local Rewrite後、正規化差、クリップ境界を跨ぐ文)。
2. **多重出現・fail-closed境界**: 「特定した1出現のみ装飾」(他の出現は装飾しない)は学習目的に適切か(全出現装飾との比較)。fail-closedの原因コード(`HL_*`)が過剰/不足でないか。USER.md:130-138の「複数出現=不合格としない」「過剰制約で制作を止めない」と、ISSUEでSTOPする範囲(`HL_SENTENCE_NOT_IN_DISPLAY`等)が整合しているか。
3. **重なり**(§B-4): 完全包含=低優先を装飾せずNOTICE(停止しない)、部分交差のみISSUE、という扱いは、既存Redundancy QA(`er119:531-551`)・KCP Gateと整合するか。③同士・隣接の扱い。
4. **Std Part 1のlevel化がAdv品質を変えないこと**(§A-2): `PROMPT_HEADS`分割・`phrases_signature(level=)`(a2のときだけpayloadへlevel追加)で、既存Adv成果物のsignature・Prompt sha・出力が本当にバイト同一か。Std Headの差分(学習者像1文+難易度指示1項目)は「Prompt難易度調整のみ」(USER.md:95)の範囲内か、独自品質基準を足していないか。T1訳Promptを共通のまま使う判断の妥当性。
5. **「英語解説」の解釈**(DESIGN_02 §0 判断候補#1): 既存Part 1と同型(日本語の解説文・Std向け難易度)で、USER.md:15,:89,:95,:97に最も忠実か。解説本文を英語にする読みの妥当性とリスク。
6. **旧経路撤去漏れ**(`SPEC_CONFLICT_02.md` S1-S27/T1-T5): 列挙漏れ(他のFamilyのPart 1ガード、`level=="b1b"`の暗黙前提、Validator、stage名`_b1b`固定、`_assert_study_ready`系)がないか。`std_part1`/`display_spec`マークによる「遡及なし」区分が、実質的に旧経路を残す抜け穴(新規記事が旧経路を使える)になっていないか。
7. **KCP整合**(§D/§F): ②がStdでitemsに入ることでG0〜G4・`record_sha256`・hash chain・`PROTECTED_ITEM_FIELDS`・`reconsume`(migration)が既存の確定内容保護と矛盾しないか。`display_spec`をハッシュ対象外にする判断、`unconsumed[]`の`CATEGORY3_HIGHLIGHT`化(読取互換)、候補doc`candidates_sha256`との結合の安全性。
8. **X/Y/Z差異**(§C): Xが二系統(`player`段/公開page script)でProduction正式入口が曖昧な点を、`er019_family_x_listening_page_01.py`(新)へ昇格・旧scriptはマーク検出でSTOPとする案は妥当か(遡及なしとの整合)。Zのクリップ分割(Chunk)と複数`div.script`での片分割描画。Yの`audience="dev"`。
9. **既存ページ回帰**: `highlights=None`でのバイト同一、`check_page`(`div.script`のall_text)・`⏸`検査・標準適合check、既存公開ページ再ビルドなしの担保。
10. **表示**: 二重下線のCSS(longhand+`-webkit-`)・スマホ可読性(thickness/offset)・凡例1行・③訳リスト(JS不要)・コピー/読み上げ非汚染の設計は十分か。
11. **費用・単価**(`COST_02.md`): Std Part 1 ≒ ¥0.16/記事セット(+0.23%)・評価¥2〜10見込みの妥当性、削減余地。
12. **並列分割**(`IMPL_PLAN_02.md`): 所有ファイルの分離(特に`er128`をB専任とし、Aは新規`er128_kp_highlight_01.py`)、依存、競合リスク。

## 返してほしい形式
各論点 `PASS | 修正要(内容) | 設計変更要(内容)` と、致命(実装前に必須)/任意の別。逐語は`docs/pm/OPUS_FINDINGS_LEDGER.md`の運用に従いFableが転記する(本依頼側では台帳更新しない)。
