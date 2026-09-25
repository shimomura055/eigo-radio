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
| 18 | E2E完走(4製品: Sewer B1/A2、Meta B1/A2、記事生成→scaffold→Key Phrase→TTS→Assembly→Audio Validation→player) | **Fable確認済み**(2026-09-25、下記「Fable最終判定」参照) | Sewer B1/A2: 本更新時点で未着手(**0/2完走**、記述は上記時点のまま、本タスクではSewerに触れていない)。Meta B1(Advanced): 従来通り完走。Meta A2(Standard): `NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-01` Phase Bで`er003_audio_tts_asr_safety.py`の`DEFAULT_JA_READING_DICTIONARY`へ`"meta": "メタ"`追加後、`--stage tts`実行(想定は差分再生成のみだったが実際はb1b/a2両方の全segmentが無条件で再生成され、実測¥54.66の予算逸脱が発生。詳細は`meta/audit/phase_b_budget_deviation.md`)。結果、comment_1/2/3の`foreign_token_findings`はMeta→READING_DICTIONARY(HUMAN_REVIEW解消)。ASR結果はcomment_1/2が「メタ」で正しく認識されstatus=OK、**comment_3のみASRが「メタン」と誤認識**したがpass-through設計のためstatus=OKのまま通過(発音保証はされない実例)。Human Review Lockが解消された状態で`--stage assemble`(API非課金と確認済み、追加費用¥0)を実行した結果、b1b/a2とも`run_summary_assemble.json`の`status`が**OK**(GATE_BLOCKED解消)。`--stage player`でplayer.html(b1b/a2共通)を生成。4製品中、完全なaudio artifactまで到達したのはMeta B1・Meta A2の2製品(Sewerは引き続き0/2)。 |
| 19 | Audio Validation Gate/Human Review Lockの尊重(上書き禁止) | **Fable確認済み**(2026-09-25、下記「Fable最終判定」参照) | 過去記述: Meta A2でGate実際にblock(`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`)。`run_assemble_stage()`は例外を捕捉し`GATE_BLOCKED`として記録するのみで、Gate側のロジック(`verify_episode_audio_validation_gate`/`foreign_token_gate_requires_stop`)は無改変。追記(2026-09-25): Phase Bでreading dictionary追加→TTS全segment再生成(予算逸脱、`phase_b_budget_deviation.md`参照)によりHuman Review Lockの条件(`ER-009-JA-FOREIGN-TOKEN-GATE-01`)がRESOLVED状態となり、Gate自体は上書きせず正規の再生成結果としてOKへ遷移した。ただしこのTTS再生成は予算上限¥10を超過した状態で発生しており、その事実の是非はFable/ユーザー判断待ち。 |
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

## 追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-01` Phase B後)
項目18・19の判定を「Fable確認待ち」へ変更した(上記参照)。Meta A2の
Assembly/player生成自体はstatus=OKまで到達したが、その前段のTTS再生成が
Phase B委任時の予算上限¥10を超えて実測¥54.66を消費した経緯があるため、
本チェックリスト全体の最終判定(`PRODUCTION_WIRED`可否を含む)はFableの
確認を経てから更新する。本追記時点ではPRODUCTION_WIREDへの変更は行って
いない。

## Fable最終判定(2026-09-25、Management-ID: NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02)
Fable判定(2026-09-25): Meta E2E経路は両レベルassemble OK・GATE_BLOCKED
解消。ただし現行Point構造は変更予定(Family X Trial待ち)のため現行Meta
を完成品化せず、E2E経路全体のStatusは `APPROVED_FOR_PRODUCTION /
WIRING INCOMPLETE` を維持。読み検証(expected reading→ASR照合)は
CLOSEOUT-02 で PRODUCTION_WIRED(commit f2f94d2a)。
