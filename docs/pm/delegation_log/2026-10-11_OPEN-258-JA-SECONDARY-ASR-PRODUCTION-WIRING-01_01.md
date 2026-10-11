# OPEN-258-JA-SECONDARY-ASR-PRODUCTION-WIRING-01 委任_01 (2026-10-11、Sonnet実行層)

範囲: 実装+無課金testまで(課金0)。runtime確認・merge・SSOT編集は未実施(後続、Opusレビュー後)。branch `feature/scg-ja-secondary-01`(mainから、worktree `../eigo-radio-scg`で隔離。他agentのstage残骸・並行agentの作業ツリーには触れていない)。
ユーザー正式決定(2026-10-11、Fable経由): V1方式=SCG(Secondary Confirm Gate)を`APPROVED_FOR_PRODUCTION`、Phase 0=VALIDATED、到達目標PRODUCTION_WIRED。

## 実装
- `er007_ja_secondary_asr_01.py` `evaluate_attempt_ja_with_cascade_detail`の早期return直前にSCGブロック。Primary=TRUE_CONTENT_MISMATCH かつ 数字/否定差なし かつ 類似度>=0.4 のときだけ、既存関数`p4.get_full_text_via_azure_stt_continuous`(Phrase Listなし)を1回呼ぶ。Secondary転写を既存`classify_ja_asr_match`で原稿照合し、EXACT/NORMALIZEDのみPASS(新final_status `SECONDARY_CONFIRMED_PRIMARY_FALSE_NG`)。PHONETIC_MATCH・不一致・空/None/例外=従来(TRUE_CONTENT_MISMATCH=再生成/fallback/STOP)。
- 既定ON(`FEATURE_FLAG_JA_SCG_ENABLED=True`)。緊急停止: 環境変数`JA_SCG_ENABLED=0`。`cascade_enabled=False`ではSCG不実行。
- 証跡: result["scg_applied"/"scg_result"/"scg_info"]。scg_infoにsecondary_transcript(全文)・judgement_reason・secondary_classification・service/azure_region/speech_sdk_version/language/phrase_list=False・audio_seconds・est_cost_jpy・wall_seconds・error・primary_text・timestamp。既存キー不変。呼び出し元3ファイル(repro01/n3/sing01_voice01)は`scg_info`をattempts_log・attempt音声metadataへ追記のみ(判定ロジック無変更)。
- 採用しなかったもの(安全条件): PHONETIC_MATCH自動PASS/助詞差・漢数字の追加除外/Whisper 2-of-3/Phrase List/新規Human Review投入。attempt上限3・fallback・Human Review Lock・英語ASR無変更。

## 検証(課金0、Azure/OpenAI/TTSはmock、Reading Resolver LLM OFF)
- 新規 `er007_ja_scg_test_01.py` 31件PASS((a)〜(h)・各呼び出し経路・flag/kill switch・Human Review不変・英語非干渉)。
- 新規 `er007_ja_scg_phase0_regression_test_01.py` 9件PASS(Phase 0保存Azure転写25行fixture `er007_ja_scg_phase0_fixture_01.jsonl`: 要試聴6音声PASS/META 3/3/救済7群8音声PASS/C群5音声NG/PHONETIC 3群NG/g7不実行/全24実行行がPhase 0判定と一致、PASS計14)。
- 全suite(255ファイル): baseline(main)と branch で失敗集合が**完全同一**(各125=117 failed+8 errors、worktreeには未追跡fixtureが無いため参照36件より多いが同一)。新規failure 0。詳細`er053_output/open258_scg_production_wiring_01/`。
- 呼出経路全数調査: `CALLPATH_01.md`。runtime確認計画: `RUNTIME_PLAN_01.md`(未実行)。
