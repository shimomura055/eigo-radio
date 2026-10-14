# CHECKLIST_05 (Production Wiring Checklist 1-12、2026-10-14 委任_04)

判定: **Family X(Coffee) = Coffee Std/Adv 完成版は生成・正式assemble・試聴ページ・Playwright実再生まで完了。ただし`PRODUCTION_WIRED`は付与しない**(#11未充足: gloss再整合工程は新しい処理フロー1段で、ユーザー承認・Opus条件A独立レビュー・Fable判定が未実施。#10はSSOT commit後に確定)。Family Zは対象外(変更なし)。

| # | 項目 | 結果 | 証跡 |
|---|---|---|---|
| 1 | 正式初回経路 | 充足: gloss再整合は`run_key_phrase_canonicalization`(Production)内。Std TTS/assembleはrunner正式`--stage tts/assemble`(Audio Validation Gate/M3通過) | `er003_v1_n3_01_scaffold_generate.py`、`a2/run_summary_assemble.json`、`a2/audit/style_profile_gate.json`(PASS) |
| 2 | retry/fallback/regen整合 | 充足: 初回/Redundancy retry/Strategy L fallback/regenerationは全て同関数経由。gloss再整合の失敗は上限2回→自動でKPを候補へ戻す(Human Reviewへ送らない)。canonicalization retry・Rule7・A'・Gateは無変更 | `er003_test_key_words_gloss_alignment.py` 22件(統合3件) |
| 3 | Trial専用実装に依存しない | 充足(限界あり): 新moduleは標準ライブラリ+既存Production module。**限界**: Std/Advの固定Master phrase(welcome=A5/preview_intro=B5ほか)はsha256 provenance付きseed(再生成なし)で、`tts_generation_results.json`に載らずAudio Validation Gateの走査対象外 | `audit/seed_provenance_04_std_assemble.json`、`seed_provenance_03_assemble.json` |
| 4 | Regression/Validator/integration test | 充足: er003_test_key_words* **354**(新規22込み)/er003_v1_n3_01 **55**/er019 **421**/er030 **108** 全PASS、失敗0 | `regression/*_final.log`(untracked、件数のみ本書に記載) |
| 5 | 正式経路でのruntime発火 | 充足: Std Part2 N01(attempt4、fallbackなし、6%減速適用、減速後ASR NORMALIZED_MATCH)・japanese_title・KP10 segment すべてstatus=OK/ASR検証済み、Std正式assemble成功(314.865秒)、gloss再整合は`sc.run_key_phrase_canonicalization`実LLM in-lineで再現(独立再実行でも同KP・同gloss) | `a2/audit/tts_generation_results.json`、`inline_runtime_04/` |
| 6 | actual model_id/routing | 充足: Std TTS `gemini-3.8-flash-lite-tts`(各entry)、KP canonicalization/gloss再整合 `gpt-6-luna`(routing A2_SUPPORT=SUPPORT_MODEL、応答model一致検査あり)。いずれも最新世代最上位系(開発・評価原則適合) | `gloss_alignment_runtime_metadata.json`、`canonicalization_runtime_metadata.json` |
| 7 | CURRENT_SPEC更新 | 充足(今回追記) | CURRENT_SPEC |
| 8 | DECISION_LOG更新 | 充足(今回追記) | DECISION_LOG |
| 9 | OPEN_ITEMS更新・整理 | 充足(OPEN-310/349/350/352/353更新、OPEN-356新規) | OPEN_ITEMS |
| 10 | commit/push/merge | commit1=3b64e5632(実装+test+Std完成+試聴ページ)push済み。SSOT commitは本書作成後に実施(secret_scan hits=0確認) | git log |
| 11 | 承認内容とProduction挙動の一致 | **未充足**: (a)gloss再整合工程は新Production処理フロー(承認済みPrompt本文は無変更だが課題指示文は新規)=ユーザー承認・Opus条件A・Fable判定が未実施。(b)Std Preview/Comment=R2・Std KP=既存・Adv=E1/P3/N01は承認内容と一致。(c)E0は既存承認済みと一致(`E0_RECONCILIATION_04.md`、OPEN-350のClose可否はFable判断) | `GLOSS_ROOT_CAUSE_AND_FIX_04.md` |
| 12 | Dangling Referenceなし | 充足(下記) | 下記 |

## 聴感判断(deferred item、タイミング合意済み2026-10-14)
UDR #49: 完成版試聴ページ `user_test/coffee_m2p0_n01_final_03/` 提示時に判断。Std 6%減速後WPM **157.7**(参考157±6の範囲内)、Adv WPM **178.2**(参考167±6の外、v5承認Advと同値)、文末ポーズ平均 Std **629ms**(参考ref<=498msの外)/Adv **572ms**(参考ref<=593ms内)、800ms以上の無音 Std 5/Adv 0。参考値はTrial値でProductionの合否基準ではない(新Gateは作っていない)。

## 未充足一覧
1. #11: gloss再整合工程のProduction採用位置づけ(新処理フロー1段、承認済みPrompt本文は無変更・課題指示文は新規)= ユーザー承認/Opus条件A独立レビュー/Fable判定が必要。これが残るため`PRODUCTION_WIRED`未付与。
2. UDR #49(聴感)= deferred(試聴ページ提示時)。
3. 固定Master phrase seedがAudio Validation Gate走査対象外(限界、Adv委任_03と同じ)。
4. OPEN-350(Adv Comment Style正本)のClose可否=Fable判断(事実は`E0_RECONCILIATION_04.md`)。

## Dangling Reference Check
- 新規ファイル: `er003_key_words_gloss_alignment.py`/`er003_test_key_words_gloss_alignment.py`/`er071_completion_04_*.py`/`er071_coffee_assemble_seed_04_std.py`/`er071_coffee_m2p0_n01_page_04.py`/`er071_coffee_m2p0_n01_play_verify_04.py` 実在。Production経路が参照する新規moduleは`er003_key_words_gloss_alignment`のみ(scaffoldからimport、実在・test済み)。`er071_*`はoffline/証跡script(Production経路からimportされない)。
- 試聴ページ(`user_test/coffee_m2p0_n01_final_03/`)のaudio参照51件は全て実在(Playwright 51/51再生OK、HTTP>=400 0件)。旧ページ`coffee_m2p0_n01_01/`は途中段階の注記を追記しfinal_03へリンク。
- SSOT内の参照(`completion_04/*.md|json`)は実在ファイルのみ。
