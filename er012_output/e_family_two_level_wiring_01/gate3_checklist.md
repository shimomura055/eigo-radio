# gate3_checklist.md — NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01

Gate 3(Production Wiring Checklist)。前タスク(`NEWS-STANDARD-A2-VOCAB-6000-
CUTOFF-PRODUCTION-WIRING-01`)の14項目 + Advanced項目 + E2E項目。

| # | 項目 | 判定 | 根拠 |
|---|---|---|---|
| 1 | Production正式初回経路へ実装・接続(runnerから呼ばれる位置に配線) | **○** | `er012_e_family_entertainment_two_level_runner_01.py`(新規Production runner)が、日本語完成記事→Advanced→Standard→downstreamを実際に呼び出す。`er003_v1_n3_01_advanced_adaptation_generate.py`・`er003_v1_n3_01_standard_a2_generate.py`はこのrunnerからimportされ、CLI経由で実行された(Meta b1b: 完走)。 |
| 2 | retry・fallback・regenerationとの整合 | **○** | 両段とも`vfl01.run_writer_with_technical_retry()`(構造Gate付きretry、既存primitive、後方互換`developer`引数を追加)を使用。fallbackモデル未定義(既存方針と一致、observed-onlyの`fallback_detected`)。`--regenerate-stage advanced|standard`を実装・単体テストで検証。 |
| 3 | DEV・Trial-onlyではないこと | **○** | Production module(er003/er012 family命名)。Trial import 0件(Dangling Reference Check §19参照)。 |
| 4 | Advanced→Standardの正式経路との整合 | **○** | Advancedが書いた`{out_dir}/b1b/article.md`をStandardがそのまま入力として消費する(同一runner内、同一theme dict)。Sewer/Meta実行で実際にこの経路を通過(Sewerはdeviation STOPまで到達、Metaは完走)。 |
| 5 | Key Words/Phrasesとの役割分担に矛盾なし | **○** | 既存`sc.run_key_phrases`/`run_key_phrase_selection`を無改変で再利用。Meta b1b/a2両方で実際にKey Phrase選定・正規化・redundancy QAが走り、CANONICALIZATION_PASSで完了(a2はredundancy retry 1回で解消、既存仕様どおり)。新Key Phrase仕様は追加していない。 |
| 6 | Production runtimeでの実発火 | **○** | CLI(`er012_e_family_entertainment_two_level_runner_01.py --stage ...`)から実API呼び出し(OpenAI Responses/TTS/ASR)が実際に発火(cost/usage/response_id記録済み)。 |
| 7 | 必要testのPASS | **○** | 新規unit test 40件PASS(Advanced 13、Standard 15[更新後]、runner 12)。全体regression`unittest discover -s . -p "*_test_01.py"`: **1033 tests, OK**。 |
| 8 | runtime evidence | **○** | `er012_output/e_family_two_level_wiring_01/{sewer,meta}/`配下に`entry_point.json`・`writer_run_summary.json`・`{b1b,a2}/audit/deviation_check.json`・`{b1b,a2}/run_summary_tts.json`・`{b1b,a2}/run_summary_assemble.json`を保存。 |
| 9 | 実際のmodel_id・routing確認 | **○** | Advanced/Standardとも`model_id_actual=gpt-5.6-luna`、`routing.require_model("NATURAL_ENGLISH_ADAPTATION"/"STANDARD_A2_ADAPTATION", ...)`使用確認。 |
| 10 | コスト影響評価 | **○** | 合計¥34.97(Sewer ¥17.01[Ledger新規構築¥9.93含む]、Meta ¥17.96[TTS/ASR含む])。予算¥300の約11.7%。 |
| 11 | `CURRENT_SPEC.md` | **○** | L829(Advanced)・L830(Standard)のStatus・Production module記述を実態に合わせ更新(本コミット)。 |
| 12 | `DECISION_LOG.md` | **○** | 本管理IDで新規エントリ追加(本コミット)。 |
| 13 | `OPEN_ITEMS.md` | **○** | OPEN-177の該当サブ項目を更新(本コミット)。 |
| 14 | 必要なGit反映 | **○**(本レポート後にcommit) | 新規module・test・evidence・SSOT更新・REPORT・delegation_logをcommit。 |
| 15 | Advanced Prompt逐語性(sha256 assert+Trial一致) | **○** | `ADVANCED_UNCHANGED_PORTION_SHA256`をimport時fail-closed assert。テストでTrial(`er015_news_ja_to_en_adaptation_trial_01.py`)のDEVELOPER/ARM3_BLOCKと逐語一致、COMMON_BLOCKのPREFIX/SUFFIXも一致を確認(6件のMeta固有bulletのみ意図的に一般形へ置換、diffはREPORT §2に逐語記載)。 |
| 16 | Production contract付与(2つの`### `+`## In one line`)がAdvanced/Standard両方で機能 | **○** | Sewer/Meta全4出力(Sewer b1b/a2は生成のみ、Meta b1b/a2)とも、`sc.split_article_text()`(`### `ちょうど2つ+`## In one line`要求)がエラーなく通過。構造Gate(`vfl01.run_writer_with_technical_retry`内`validate_point_structure`)は全呼び出しでSTRUCTURE_PASS(1回で通過、リトライなし)。 |
| 17 | Meta「一部の通話」scope確定(delegation D6) | **○** | `er012_output/e_family_two_level_wiring_01/meta/fact/meta_fact_scope.md`。Reuters一次情報(`r.jina.ai`経由でmarketscreener.com republish全文取得)で「一部の通話(call単位)」と確定。既存Ledger(MUSE-006)は修正不要と確認。Advanced/Standard生成後、Meta deviation checkはLEDGER_COMPLIANT(scope不整合の指摘なし)。 |
| 18 | E2E完走(4製品: Sewer B1/A2、Meta B1/A2、記事生成→scaffold→Key Phrase→TTS→Assembly→Audio Validation→player) | **×** | Sewer B1/A2: **0/2完走**。Advanced writer stageで`vfl01.run_deviation_check`がLEDGER_DEVIATION(MAJOR severity 2件、記事の中核claim「既存の老朽化した公共下水道を浄化槽へ切り替える」がLedgerの実際のscope[未整備区域の計画変更等]を超える一般化と判定)。delegation D5の既存retry(1回)を実施したが再度LEDGER_DEVIATION→STOP(本文を手で直さず、Ledger topicの調整もせず)。downstream(scaffold/TTS/Assembly)は未実行。Meta B1(Advanced): **完走**(writer→scaffold→TTS[全segment OK]→Assembly[OK, duration 275.6s, clipping無し]→player.html)。Meta A2(Standard): writer完走(deviation 1回retryでLEDGER_COMPLIANT)・scaffold完走・TTSはcomment_1/2/3が既存`ER-009-JA-FOREIGN-TOKEN-GATE-01`により未知の外来語("Meta")検出でSTOPPED(Human Review待ち、TTS自体呼び出さず)・Assemblyは既存Audio Validation Gateにより`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`(comment_1/2/3=STOPPED)。4製品中、完全なaudio artifactまで到達したのはMeta B1のみ。 |
| 19 | Audio Validation Gate/Human Review Lockの尊重(上書き禁止) | **○** | Meta A2でGate実際にblock(`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`)。`run_assemble_stage()`は例外を捕捉し`GATE_BLOCKED`として記録するのみで、Gate側のロジック(`verify_episode_audio_validation_gate`/`foreign_token_gate_requires_stop`)は無改変。Human Review Lock相当の承認も本タスクでは付与していない。 |
| 20 | Fact/Ledger deviation checkの実施(Advanced/Standard両方、全出力) | **○** | Sewer b1b(2回、いずれもLEDGER_DEVIATION)・Meta b1b(1回、LEDGER_COMPLIANT)・Meta a2(2回、1回目LEDGER_DEVIATION→2回目LEDGER_COMPLIANT)。全deviation_check.jsonを`audit/`配下に保存。 |
| (別項目) approved specとProduction挙動の一致 | **○** | Advanced/Standardとも実際の生成テキストがEditorial structure/angle/metaphor/ending保持・6,000語超語の自然な平易化(例: Sewer "combined septic tank"はそのまま、A2側で"replacing"等の平易表現へ調整)という承認済み仕様どおり(REPORT §6全文参照)。 |
| (delegation) Dangling Reference Check | **○** | `Grep "er015_" glob="er003_*.py,er012_e_family*.py"`一致はコメント内の由来引用のみ(`import er015`文は新規Advancedモジュールのテストファイル1箇所のみ、Production module自体は0件)。 |

## 最終判定
×1件(18、E2E 4製品完走)が残るため、**`PRODUCTION_WIRED`にはしない**。
配線自体(項目1〜17、19〜20)は実質的に完了・実証済み(Meta B1で実際にE2E
完走、Meta A2/Sewerでは既存Fact Safety Gate・Audio Validation Gate・Human
Review Lockが正しく機能してblockしたことを確認)。
最終Status: `APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`
(Advanced/Standardとも。配線自体は完了、Gate 3の全項目○には未到達)。
