# 委任_07: C1仕上げ・main commit/push・feature branch作成(RISK-FLAGGER-PRODUCTION-WIRING-01、2026-10-10)

課金API 0件。Production runner本体(er012_e / entertainment runner / jaw / audio runner)変更なし。

## Fable承認事項(委任_06要対応への回答)
1. 既存test 2件を最小更新(許可範囲の明示のみ、assertion緩和ではない):
   - `er006_model_routing_gpt6_wiring_test_01.py::test_process_map_openai_models_all_gpt6_luna`: FAMILY_X_FACTLOCK_REVISE=gpt-6-astra / FAMILY_X_RF_GEMINI=gemini-3.5-flash-lite を許可リスト化(ユーザー決定2026-10-10)。他のgpt-系はluna固定を維持。
   - `er006_model_routing_pricing_coverage_test_01.py::test_gpt6_astra_prices_registered_standard_only`: 末尾を「astraはFAMILY_X_FACTLOCK_REVISEのみ」へ更新。
2. 契約検証V5/V6/V10の解釈追加(Storyline重複行の除外1行/印の出現ベース整合/Storylineは数値印除去後に完全一致)は実装是正として承認。**Open Item候補**: Lane B(自動注記)出力形式との擦り合わせが必要(OPEN-247として起票)。
3. F8許容差(import行・`fl.`接頭辞除去)承認。chain_method="W-1"+chain_method_detail承認。unlocated_flags部分採用は未実装のまま(新仕様判断、報告のみ)。
4. er015 test収集時RuntimeError: `er015_standard_a2_6000_generation_first_trial_01.py:205` のガードが参照する `std_gen.STANDARD_A2_PROMPT_V5` の定義元は `er003_v1_n3_01_standard_a2_generate.py`。同ファイルとer015の両ファイルは `git status --porcelain` に出ず(未変更)、`git log -1 --format=%H -- <er015 test/本体>` = 9dcd0e59…。C1変更ファイルに含まれず、C1と無関係(既存FAIL)と静的確認。stash/checkout未使用。

## テスト(.venv/Scripts/python.exe -m pytest。システムpythonはscipy無しで不可)
er053_*_test_01 7本 + er006_model_routing*test* = **170 passed / 0 failed**。er015 testは上記の既知収集エラーのため除外。秘密情報grep(sk-/AIza/api_key)はer053_*・er053_output・review_queueで実キー0件(`OpenAI(api_key=_key("OPENAI_API_KEY"))`の変数参照1行のみ)。

## ブランチ運用メモ(feature/factlock-rf-wiring-01)
- 作成元: main のC1 commit群先頭。C2/C3はこのブランチで実装。
- merge方式: `git merge --no-ff`(main側)。rebase禁止。mainの更新は `git merge main` でブランチへ取り込む。
- rollback tag: merge直前のmain HEADへ付与(例 `pre-factlock-rf-wiring-merge`)。
- ブランチ存続中の凍結対象(mainで編集しない): `er012_e_*`(Production runner本体)、entertainment runner、audio runner(jawはC2/C3対象のため同様に注意)。具体3ファイルはC2着手前にFableが確定する。
- Production採用(merge)は人間ユーザー承認後のみ。
