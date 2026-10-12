# 2026-10-12 FAMILY-Z-MELOS-PROPER-NOUN-ASR-ROOT-CAUSE-01 委任_01

## 管理ID
FAMILY-Z-MELOS-PROPER-NOUN-ASR-ROOT-CAUSE-01(委任_01)

## 性質
調査主体+既承認仕様の配線漏れ是正(分類A)。TTS再生成0、有料は既存wavへのASR再評価のみ(約JPY11、上限JPY20)。run_e2e_02のstate/checkpoint/queueは未編集。HR Lock迂回・`record_human_approval`呼出なし。runner/TTS未起動。

## 事前指定Read一覧
run_e2e_02の`{b1b,a2}/audit/tts_generation_results.json`・`review_lock_state.json`、`er011_output/attempt_history.jsonl`(theme_id=run_e2e_02のみ抽出)、`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`(L73-75)、`er021_output/.../telemetry.jsonl`(Melos行のみ)、`er006_output/pronunciation_ledger_01/ledger.json`、コード: `er063_family_z_audio_01.py` L526-635/694-760、`er003_v1_n3_01_tts_generate.py`、`er003_v1_sing01_news_tail_fix.py`、`er006_secondary_asr_01.py`、`er006_preprod_hardening_01_validation.py`、`er021_en_asr_semantic_equivalence_production_01.py`、`er008_asr_variant_hardening_15_homophone_en.py`、`er007_ja_asr_validator_01.py`

## 事前指定Grep一覧+追記位置・更新位置の手順
CURRENT_SPEC.md: entity_only/cascade_unresolved/Phrase List/SECONDARY_ASR_CORROBORATED/Tier3(L1964-2019, L2183-2295のみ読込)。追記位置: OPEN_ITEMS.md OPEN-308/OPEN-270本体行末尾追記+OPEN-318〜320をOPEN-317直後に新規行、DECISION_LOG.md末尾、CURRENT_SPEC.md L2019セル内の「既知Gapなし」直後に是正注記1文。

## 実行コマンド全文
- 調査: python -c / heredoc(読取のみ)。再評価: `.venv/Scripts/python.exe er026_output/family_z_production_e2e_01/melos/asr_root_cause_01/reeval_post_slowdown_01.py`(単発、計3回実行、初回2回は`cl.install`未呼出で例外fail-closedの無効試走)。
- test: `python -m unittest er026_post_slowdown_cascade_rescue_01_test_01 er063_family_z_audio_01_test_01 er058_asr_tts_prodfix_01_test_01 er008_n8_a2_slowdown_sha256_refresh_22_test_01 er021_en_asr_semantic_equivalence_production_wiring_01_test_01 er026_family_z_fiction_production_runner_01_test er026_family_z_e2e_integration_test_01 er026_family_z_stop_sentinel_test_01 er025_pronunciation_resolution_phase3_b1b_en_wiring_01_test_01`

## 変更ファイル
`er003_v1_n3_01_tts_generate.py`、`er026_post_slowdown_cascade_rescue_01_test_01.py`(新規)、`er026_output/family_z_production_e2e_01/melos/asr_root_cause_01/`(ROOT_CAUSE_01.md、clip_transcripts_01.md、reeval_post_slowdown_01.py/.json、reeval_cost_log.jsonl)、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`CURRENT_SPEC.md`(是正注記1文のみ)

## 注意・開示
- STOP_NOTICE(`2026-10-12_..._STOP_NOTICE.md`)は存在するが、run_e2e_01の旧runner暴走の記録として本委任と別scopeと解釈し、既存wavへのASR再評価のみ実施(Fable確認事項)。`STOP`/`STOP_ALL`は有料呼出直前に不在を確認。
- 調査用の分類呼出(`classify_asr_match`)の副作用で、`er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl`に調査プローブ由来の行が数行追記された(tracked、並行agentの追記と混在、編集禁止判断のため削除せず、本commitに含めない)。
- stop sentinel/integration testの失敗は環境起因(共有ファイル競合、実ディレクトリへのSTOP_ALL一時生成)。再実行は危険なため見送り。

## SSOT追記文
DECISION_LOG.md「FAMILY-Z-MELOS-PROPER-NOUN-ASR-ROOT-CAUSE-01 委任_01」節、OPEN-308/270追記、OPEN-318/319/320新規、CURRENT_SPEC L2019是正注記。

## Git
対象ファイルのみ明示add、secret_scan --staged PASS後にcommit/push。

## 報告
`docs/pm/RESULT_PACKET_MELOS_ASR_01.md`(要約)、詳細は`er026_output/family_z_production_e2e_01/melos/asr_root_cause_01/ROOT_CAUSE_01.md`。
