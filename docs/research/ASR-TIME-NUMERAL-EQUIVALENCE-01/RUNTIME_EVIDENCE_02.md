# RUNTIME_EVIDENCE_02(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_04、OPEN-489、API 0・新規TTS 0・費用0円)

実行器 `runtime_evidence_03.py`(委任_02の`runtime_evidence_02.py`に OPEN-489 variantとscope外[A/B/C同等]ブロックを追加)。生データ `runtime_base_03.json`(修正前=`--modules base_HEAD03`)/`runtime_after_03.json`(修正後)/`runtime03_compare.txt`。X/Zの既存保存entry(`tts_generation_results.json`)を **再利用・引継ぎの正式経路 `er078_reuse_value_guard_01.guard_entry`(内部で `er019_family_x_validation_inheritance_01.rejudge_with_current_judge` → 統一judge)** で再判定。環境注記: 本環境に`google.genai`/`pykakasi`が無いため、importを通すだけのstub(MagicMock)を実行器内で入れた(API呼出なし・判定ロジックは実module)。

## 結果(53 record)
- **保存entry(variant=stored)の判定変化 = 0件**(退行なし)。変化した3件は全てOPEN-489合成variantの NG→PASS。
| scope | variant | 修正前 | 修正後 |
|---|---|---|---|
| Z(run_scope) | canon `between 9 and 11` / ASR `between nine and eleven`(c8 entryへ1文追加の合成) | BLOCKED NG_PROTECTED/p1_value_diff | **ok PASS/primary_pass** |
| X(run_scope) | 同(coffee_prices a2 full_story_part1へ1文追加の合成) | BLOCKED NG_PROTECTED/p1_value_diff | **ok PASS/primary_pass** |
| A/B/C同等(scope外) | 同 | BLOCKED NG_PROTECTED/p1_value_diff | **ok PASS/primary_pass** |
| Z/X/ABC | canon `between nine and eleven` / ASR `between 9 and 12`(NG側) | BLOCKED p1_value_diff | **BLOCKED p1_value_diff(維持)** |
| X/ABC | `Seven and eight people came.` / ASR `7 and 8 people came.` | ok PASS | ok PASS(維持) |
| X/ABC | `It cost one hundred and ten dollars.` / ASR `110 dollars` | BLOCKED p1_value_diff | BLOCKED p1_value_diff(**修正前後同じ**。TTS入力の数字化が`one hundred and 10`にする別の既存不具合=OPEN-491候補、本修正の範囲外) |
- 共通moduleのため X/Z/A/B/C に区別なく作用する(er109のrun_scopeは同音救済のscopeで、atom化・正規化には効かない)。retry/fallback/regeneration/resume・最終ANDゲート・Human Review Lockは無変更。
- 実作品への影響: 完成済み作品への影響なし(再生成・再処理なし)。今後のrunで`X and Y`型の数詞語が語形で書き起こされたとき、誤NGによる不要な再生成/HR Lockが起きなくなる。
