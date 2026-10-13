# CHECKLIST_03 (Production Wiring Checklist 1-12、2026-10-13 委任_02)

判定: **Family X(Coffee) = 配線済み・未完了(`PRODUCTION_WIRED`は付与しない)**。Family Zは本委任の対象外(変更なし、CHECKLIST_02のまま)。

| # | 項目 | Family X Coffee | 証跡 |
|---|---|---|---|
| 1 | 正式初回経路 | 充足(CHECKLIST_02から変更なし)。是正①②③は正式経路(canonicalization入力/runner引継ぎ/明示無効化CLI)に実装 | `completion_02/` + 各py |
| 2 | retry/fallback/regen整合 | 充足: 既存retry上限・Gate・M3は無変更。引継ぎは`REUSED_VALIDATED`でGate判定不変、持ち越しはstatusを問わずGateが判定、無効化は`INVALIDATED_FOR_REGENERATION`=Gate fail-closed | `er019_test_family_x_completion_02_integration.py`(9件)、`fix2_gate_sim_02_step0.json` |
| 3 | Trial専用実装に依存しない | 充足: 新module(`er019_family_x_validation_inheritance_01.py`/`er019_family_x_segment_invalidate_01.py`)は標準ライブラリ+既存Production判定関数のみ。`er071_*`はoffline証跡script(Production経路から参照されない) | grep確認 |
| 4 | Regression/Validator/integration test PASS | 充足: er019 399+追加/er030 108/er003_v1_n3_01 55/er003_test_key_words* 320 全PASS、失敗0(最終回帰は`regression/`) | `completion_02/regression/` |
| 5 | 正式経路でのruntime発火 | **未充足**: 今回の有料runはStd KP canonicalization 1回(JPY1.01)のみ。**CANONICALIZATION_INVALID(別item: 候補C21『raw-bean』topic、LLMが『raw-bean prices』を返しRule7違反)=STOP**。Std Part 2 N01再生成・Std KP音声・Adv comment再生成・正式assembleは**未実行**(STOP条件) | `a2/key_phrases/canonicalization_runtime_metadata.json`、`scaffold_kp_std_d04_stdout.log` |
| 6 | actual model_id/routing | 部分: KP LLM `gpt-6-luna`(actual記録済み)。TTS(gemini-3.8-flash-lite-tts)は今回未実行のため新規runtime記録なし | 同上 |
| 7 | CURRENT_SPEC更新 | 充足(今回追記) | CURRENT_SPEC |
| 8 | DECISION_LOG更新 | 充足(今回追記) | DECISION_LOG |
| 9 | OPEN_ITEMS更新・整理 | 充足(OPEN-343/346更新、新規OPEN追記) | OPEN_ITEMS |
| 10 | commit/push/merge | 充足見込み(明示add・secret scan・Managed-ID trailer) | git log |
| 11 | 承認内容とProduction挙動の一致 | **未充足(確認できず)**: 完走していないため、M2P0/N01/6%減速/F1後判定が完成版Std/Advで動作していることを確認できていない。Adv Previewの承認Style(E1)は**未配線**(approved-but-unwired、OPEN-313) | `ADV_STYLE_FACTCHECK_02.md` |
| 12 | Dangling Referenceなし | 充足(下記)。新規参照は実在ファイルのみ | 下記 |

## PRODUCTION_WIRED にならない理由
1. **Std KP canonicalization INVALID再発(別item)**: 是正①は『based on』型(span末尾が機能語)を解消したが、今回の選定では topicスロットの候補C21『raw-bean』(修飾語のみの断片span、末尾が機能語でない)が選ばれ、LLMが『raw-bean prices』(原文には連続して存在するがsource_span外)を返してRule7違反。過去ログ(206ファイル)にも同種(span外の主要語復元)が18件ある(`bring in`→`bring in a human helper`等)。拡張ルールの一般化は「Rule7の許容範囲の変更」にあたる新しい仕様判断のため実装せずSTOP。
2. **Adv Preview(E1)が未配線**: e_tone_01(「warm, upbeat」)もmain runner `coffee_n01_r2_p3`(「calm, conversational」)も承認Style E1(「calm, composed news anchor; ...」)と不一致=Fable既定ルール(iii)。
3. 上記により正式`--stage assemble`(Std/Adv)・完成版・試聴ページは未作成。

## Dangling Reference Check
- 新規ファイル: `er019_family_x_segment_invalidate_01.py` / `er019_test_family_x_completion_02_integration.py` / `er071_expansion_census_02.py` / `er071_style_factcheck_02.py` / `er071_completion_02_gate_sim.py` — すべて実在、Production経路(runner/Gate/er006/er011)からimportされない。
- runnerの新規参照: `validation_inheritance.is_untouched_entry` / `try_inherit_from_cached`(実在、test済み)。
- SSOT内の参照(`completion_02/*.md|json`)は実在ファイルのみ。
