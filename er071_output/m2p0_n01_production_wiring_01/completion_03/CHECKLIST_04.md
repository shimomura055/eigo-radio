# CHECKLIST_04 (Production Wiring Checklist 1-12、2026-10-13 委任_03)

判定: **Family X(Coffee) = 配線済み・未完了(`PRODUCTION_WIRED`は付与しない)**。Std側がG運用STOP(KP『based on interviews』のja_gloss不整合、`gloss_check_03.md`)。Adv(b1b)は完成(正式assemble成功)。Family Zは対象外(変更なし)。

| # | 項目 | Family X Coffee | 証跡 |
|---|---|---|---|
| 1 | 正式初回経路 | 充足: 案A'・gloss監査フラグ・E1 profile・記録移行CLI・Preview M4記録・sha256記録是正・clobber復元CLIはいずれも正式経路(canonicalization入力/runner/profile機構)に実装 | 各py、`completion_03/` |
| 2 | retry/fallback/regen整合 | 充足: canonicalization retry上限(2)・Rule7検証・左端ガード・Gate・M3は無変更(retryへの失敗理由追記なし)。移行は上位集合+sha一致のみ | `er003_test_..._dangling_span.py`(32)、`er019_family_x_style_profile_migration_01_test_01.py`(15) |
| 3 | Trial専用実装に依存しない | 充足: 新moduleは標準ライブラリ+既存Production module。`er071_*`はoffline証跡script | grep確認 |
| 4 | Regression/Validator/integration test PASS | 充足: er019 421/er030 108/er003_v1_n3_01 55/er003_test_key_words* 332 全PASS、失敗0 | `completion_03/regression/*_final.log` |
| 5 | 正式経路でのruntime発火 | **部分**: Std KP canonicalization PASS(A'窓で『based on interviews』)・Adv preview(E1)+comment_1〜4 TTS・Adv正式assemble(Gate/M3 PASS、315.43秒)は実発火。**Std Part 2 N01再生成・Std KP音声・Std japanese_title・Std assembleは未実行(G STOP)** | `scaffold_kp_std_d05_stdout.log`、`tts_adv_d03_stdout.log`、`assemble_adv_d04_stdout.log`、`F1_M1_RUNTIME_EVIDENCE_03.md` |
| 6 | actual model_id/routing | 部分: Adv TTS `gemini-3.8-flash-lite-tts`(各entry `tts_model_id`)、KP LLM actual記録済み。Std TTSは未実行 | `b1b/audit/tts_generation_results.json` |
| 7 | CURRENT_SPEC更新 | 充足(今回追記) | CURRENT_SPEC |
| 8 | DECISION_LOG更新 | 充足(今回追記) | DECISION_LOG |
| 9 | OPEN_ITEMS更新・整理 | 充足(OPEN-346/349/350更新、OPEN-352[G]/353[C]/354[sha・clobber]新規) | OPEN_ITEMS |
| 10 | commit/push/merge | 充足見込み(明示add・secret scan・Managed-ID trailer) | git log |
| 11 | 承認内容とProduction挙動の一致 | **部分**: Adv Preview=E1(sha 8862317ff766...)・Full Story=N01(Adv part1〜3は引継ぎ維持)・Adv KP解説=P3は一致確認。Std側(N01再生成・6%減速後再検証・F1後ASR判定)の完成版での動作は未確認。Adv Comment Style正本(OPEN-350)は未決のまま | `F1_M1_RUNTIME_EVIDENCE_03.md` |
| 12 | Dangling Referenceなし | 充足(下記) | 下記 |

## PRODUCTION_WIREDにならない理由
1. **G運用STOP**: Std KP #4 `based on interviews`(候補`based on`をA'窓内で補語まで伸ばした)のja_gloss `～をもとにした`(TTS「なになにをもとにした」)が英語KPの具体語`interviews`を反映しない。独自にglossを書き換えず停止(UDR G1〜G3のユーザー判断待ち)。
2. Std完成版(Part 2 N01再生成・KP音声・japanese_title・assemble)・試聴ページ(Std/Adv完成版)・Playwright実再生・WPM/ポーズ測定は未作成。

## Dangling Reference Check
- 新規ファイル: `er019_family_x_clobber_restore_03.py` / `er019_family_x_clobber_restore_03_test_01.py` / `er019_family_x_style_profile_migration_01_test_01.py` / `er071_completion_03_*.py` / `er071_expansion_census_03.py` — すべて実在、Production経路(runner/Gate/er006/er011)からimportされない(clobber復元CLIは明示CLI、runnerは`_with_recorded_sha256`のみ追加)。
- runnerの新規参照: `style_profile_mod.ROLE_PREVIEW`/`migrate_record`/`validation_inheritance.sha256_file`(実在、test済み)。
- SSOT内の参照(`completion_03/*.md|json`)は実在ファイルのみ。
