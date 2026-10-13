# EVIDENCE_PLAN_01 (委任_02のruntime evidence計画。保存先は既存`er0XX_output/`構造=委任_02の指示で`er071_output/m2p0_n01_production_wiring_01/`配下。新しい証跡置き場は作らない)

KPI provenance: すべて`production_formal_path`/`fresh`(Production正式runner経由の新規生成)。Trial結果・過去生成物の流用はevidenceにしない。

## 1. 共通の事前確認(各有料run開始前)

1. `docs/pm/delegation_log/*STOP_NOTICE*`・`<run>/STOP`・`er026_output/family_z_production_e2e_01/STOP_ALL`の存在確認(あれば新規API呼出なし)。
2. `TTS_EXECUTION_MODE=STANDARD`を明示(T-2)。`--tts-backend speech_metadata_flash_lite`、`--budget-jpy 80`(費用上限提案、COST_ESTIMATE参照)。
3. 起動はforegroundの単発またはbackground単発(監督ループ・`timeout`ラッパ・自動再試行ラッパなし)。外部停止または原因不明のrc≠0が2回続いたら再起動せずSTOP。有料run再起動は委任文が明示許可した回数のみ。
4. out_dirは新規(例: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_v6_n01_01`、命名は委任_02で確定)。再利用segment(IN_ONE_LINE/Preview/Comment1-4/shell)は明示コピー+sha一致確認(V5委任の手順)。

## 2. Family X(Coffee)の取得項目

### 2-1 KP(M2P0)

| 取得項目 | 取得方法 | 合格条件 |
|---|---|---|
| `kp_backend_used` / `kp_supply` | `er030_output/kp_backend_telemetry_01/telemetry.jsonl`+`key_phrases/*/runtime_metadata.json`(`kp_backend_model_id`等) | `db_hybrid` かつ `m2`。`strategy_l_fallback`はM2不発火=不合格(`PRODUCTION_WIRED`根拠にしない、原因を報告) |
| actual model_id・routing | 選定/canonicalization/Redundancy QAの応答`model`(`kp_backend_model_id`、`cost_log`)、`routing.require_model(process,…)` | `gpt-6-luna`(`SUPPORT_MODEL`)。契約違反はSTOP |
| 候補数・予約枠 | `db_hybrid_stage1_debug.json`+M2メタ(shortlist総数、reserved件数/canonical、overflow、tier_h_dropped、dropped_non_contiguous) | 予約枠<=3、cap15の外側、`match:`なし |
| Wiktionary照会 | `stage1.wiktionary_multiword_lookup`(api_calls/elapsed_sec/candidates_checked) | 実測秒を記録(Trial約43秒/記事との差を報告)。429で失敗した場合はfallbackとして記録 |
| P0無変更 | 実送信prompt(`keywords_selector_prompt.txt`/db_hybrid側保存)のstatic部/guidance部sha | `b8af4d50…`/`026aa730…`と一致 |
| gate結果 | selection status、`canonicalization_status`、`redundancy_status`、retry到達(`strategy_l_attempts`/`redundancy_retry_attempts`) | 既存上限内。INVALID/NGは既存経路で処理・報告(人為修正禁止) |
| 最終KP5件 | `key_phrases`の最終items(display_phrase・role) | 報告(M2由来の予約枠候補が選ばれたか) |
| 費用 | `cost_log`/`kp_backend_cost_jpy` | `KP_ARTICLE_COST_CAP_JPY=15`以内 |

### 2-2 KP音声・Full Story(N01)

| 取得項目 | 取得方法 | 合格条件 |
|---|---|---|
| N01 style sha | segment結果`style_profile`(`expected_base_sha256`/`style_base_sha256`)+`audit/style_profile.json`+`attempts_log`の送信style record | Full Story part1-3(Std/Adv)の全attemptで`d1956c91…`、Stdに減速instruction連結なし。M3 assembly gate PASS |
| model / voice / backend | `tts_generation_results.json`の`model_version`/voice/`tts_backend`、cost_log | `gemini-3.8-flash-lite-tts`(実`model_version`を記録)、Aoede、`speech_metadata_flash_lite` |
| ASR Gate | 各segmentの`classify_asr_match`結果(verified/classification)、attempts数 | 既存Gate・閾値・retry上限のまま合格。fallback takeで合格した場合は`instruction_type=minimal_fallback`(N01ではない)として別掲 |
| Std減速後再検証 | `slowdown_info`(6%)、`post_slowdown_asr_text`/`post_slowdown_classification`、cascade rescue有無 | 全Std Full Story partで再検証PASS(STOPPEDなし) |
| 品質指標 | WPM(Full Story部)・文末無音・segment gap・総尺(`er057_coffee_final_v5_wpm_01.py`/pause測定の既存手順) | 数値を報告のみ(新基準を作らない。既存の速度・ポーズ基準を維持) |
| 異音・Audio Validation | `er057_coffee_final_v5_anomaly_01.py`/`audio_validation`系の既存スクリプト手順 | 欠落0、medium/high異音の有無を報告 |
| 費用 | runner cost表示+cost_log | COST_ESTIMATE内。超過見込みで停止 |

### 2-3 試聴ページ・再生

- 組立(`stage_assemble_family_x_a2/b1b`)→QA→GitHub Pages `user_test/`へ公開(既存手順、`er057_coffee_final_v5_page_01.py`系)→Playwright実再生evidence(`er057_coffee_final_v5_play_verify_01.py`系: 実際に再生して進行を確認、URL・再生時刻・総尺)。
- 試聴URLはユーザー報告にそのまま添える。評価はユーザーが行う(自動合否にしない)。

## 3. Family Z(STOP維持。課金・生成・記事再生成なし)

| 項目 | 方法 | 結果の扱い |
|---|---|---|
| N01 style到達 | mock test(`style_text_for(spec)`、`assert_style_table_integrity`)、dry-run plan(音声生成なし) | 配線到達の**静的/mock確認**として記録。Production runtime発火ではない |
| M2 | 構造上Z KPは`strategy_l`(Z-1) | 実施なし |
| Checklist 5(Production runtime発火)/6(actual model_id・routing) | STOP条件に抵触するため取得しない | **「未確認」として残す。推測・Trial結果で代替しない。`PRODUCTION_WIRED`と判定しない** |
| STOP確認 | 各作業前にSTOP/STOP_ALL/STOP_NOTICE確認、Melos run_e2e_02等へ書込なし | 報告に記載 |

## 4. 報告に必ず入れる項目(Production Wiring Checklist 11項目との対応)

| Checklist | Family X | Family Z |
|---|---|---|
| 1 正式初回経路 | selector挿入+runner profile(コード+テスト) | N01定数差替(コード)。M2=Z-1未決 |
| 2 retry/fallback/regen整合 | `PATH_MAP_01.md`+回帰test | 同左(共有module) |
| 3 Trial専用でない | Dangling test | 同左 |
| 4 test PASS | `TEST_PLAN_01.md`の全件 | 同左 |
| 5 runtime発火 | 2-1/2-2 | **未確認** |
| 6 actual model_id・routing | 2-1/2-2 | **未確認** |
| 7-9 SSOT | 配線完了後に更新 | 未確認項目を明記して更新 |
| 10 Git | commit/push(明示add、secret scan) | 同左 |
| 11 承認と実挙動の一致 | N-1/N-3の解釈確定後、承認内容との照合表 | Z-1/N-2未決のため未確定 |
