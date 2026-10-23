# WIRING_EVIDENCE_01(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_02)

結論: 修正は **共通module `er021_en_asr_semantic_equivalence_production_01.py` の `_tier1_atoms` 1箇所** であり、Tier1(`classify_asr_match`)・最終ANDゲート(`value_guard`)・再判定/再利用/引継ぎのすべてが同じ `_tier1_atoms` を通る。flagは追加していない(不具合修正・既定ON、新規flag読取関数なし。X/Z/A/B/C共通)。

## 1. 変更点(1関数追加+1呼出)
- `er021_en_asr_semantic_equivalence_production_01.py:130` 分の範囲定数 `_CLOCK_MINUTE_MIN, _CLOCK_MINUTE_MAX = 10, 59`
- `:370` `_try_clock_pair(words, i)`(新規。時1〜12+分10〜59の隣接2語を時刻形atomへ)
- `:503` `_tier1_atoms` のループ内の呼出1行(`_NUMSTR_RE.fullmatch(w)`直前)

## 2. `_tier1_atoms` を通る経路(呼出元の実コード)
| 層 | 関数・行 | 備考 |
|---|---|---|
| 一次分類 Tier1 | `er006_preprod_hardening_01_validation.py:1376` `semantic_equivalence.tier1_numeric_equivalence` → `er021:724-725` `_tier1_atoms(canonical/asr)` | 5 role(FULL_STORY/COMMENT/PREVIEW/TOPIC_INTRO/IN_ONE_LINE)で有効 |
| 最終ANDゲート | `er078_asr_value_guard_01.py:353` `_en_sequence` → `_tier1._tier1_atoms` ; `er078_asr_unified_judge_01.py:355-357` `_protected` → `vg.value_guard`(Primary l.509 / Secondary l.642) | 非Tier1 role(KEY_PHRASE等)もこの層で作用 |
| 生成時(初回) | `er003_v1_n3_01_tts_generate.py:237-242` `_post_slowdown_unified_judge` → 統一judge EN adapter `er006_secondary_asr_01.py`(`val.classify_asr_match` l.1090/1193) | retry/fallback/regeneration/再試行slotも同じadapter |
| 再利用・引継ぎ(retry/resume/再利用/Master Store) | `er078_reuse_value_guard_01.guard_entry` → `er019_family_x_validation_inheritance_01.rejudge_with_current_judge`(l.256)。呼出点: X runner `er019_family_x_audio_production_runner_01.py:654`、Z `er063_family_z_audio_01.py:762`、C `er013_family_c_production_runner_01.py:444`、Master Store `er006_master_audio_store_01.py:130`、引継ぎ `er019_family_x_validation_inheritance_01.py:207,501` | 保存転写をAPI 0で現行judgeにかけ直す=修正が保存entryにも効く |
| resume | `er008_n8_a2_resume_01.py:41`/`er008_n8_b1_resume_01.py:47` `classify_asr_match` | 同じ分類器 |
| 日本語 | `_guard_ja` は `_tier1_atoms` を使わない(影響なし。Opus所見8) | |

## 3. X/Z/A/B/Cへの作用
- 共通moduleのため区別なく作用(Opus所見7: er109の`run_scope`は同音救済のscopeであり、atom化の適用範囲は制限しない)。A/B/C Legacy(§27-3)は判定変化がないことをreplayのFamily別内訳(REPLAY_02.md)で確認。
- 既存のretry/fallback/regeneration・Gate(最終ANDゲート・Human Review Lock・Secondary 1回)は無変更。上限回数・安全装置の迂回なし。
- Default OFFの未承認機能の追加はない(新flagなし)。
