# IMPLEMENTATION_05B (委任_05B, 2026-10-27, API 0)

## 変更
- `er120_part2_wiring_01.py`
  - `pregen_stage(all_candidates=)` 引数と分岐を撤去(新仕様: 事前生成はTop1/Top2=PREGEN_MAX=2のみ)。docstringの「PREGEN_MAX=8」→2。
  - 新規 `_ex_excluding_frozen(ex, frozen, review)`: 凍結(ユーザー確定)がある場合、凍結候補と確定後に使われない非選択候補(Top2等)の事前生成物itemを、explain_signature(model依存)検査から除外。`explanations_sha256`(書換え検知)は先に全itemで検証し、除外後集合で再計算。凍結が無ければexをそのまま返す(保護OFF対照・挙動不変)。
  - `require_final`(v2経路)と`finalize_stage`のvalidate_explanations呼出に適用。
- `form_grammar_bundle`: `doc["candidates"][:g.PREGEN_MAX]` で<=2を確認(変更なし)。
- test: integration 2件(旧2件採用)→「2件指定はPart2ReviewErrorで拒否+Top2の1件採用が1ブロックで節単位検査PASS」(X/Z Adv, Std player)。
- test: `er128_kp_confirmed_content_02b_test_01.py` の `test_KNOWN_DEFECT_...` を通常test `test_frozen_part2_survives_model_change_with_pregen_explanations` へ(expectedFailure解除。所有外だが解除対象の実体がここ)。

## GPG4不具合の根拠
model変更後 `require_final`が `validate_explanations(ex, ...)` で事前生成物の全itemの `_expl_item_ok`(explain_signature一致)を検査 -> 凍結済み候補(1回目)、さらに非選択Top2(2回目)でPart2Stale。M6「確定した文法はmodel変更で失効しない」に反する。凍結の正は `frozen:<sha>`(require_fresh_part2/build_result_v2側で検査済み)。

## ページbuilder/Validator
`er120_part2_grammar_production_01.py:1438` は`result_items`をitemごとに描画(<=1が新規確定、旧2件結果の読取互換で残置)。`GRAMMAR_MAX=1`(:49)。ブロック数1検査(part2_blocks==1)は1件採用testでPASS。
