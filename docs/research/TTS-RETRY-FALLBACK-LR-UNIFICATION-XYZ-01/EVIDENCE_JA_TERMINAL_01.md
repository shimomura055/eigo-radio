# EVIDENCE_JA_TERMINAL_01 (委任_05: JA部位の終端NG→HRQ・Lock・STOPPED の実経路確認)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 / 実行: 2026-10-27 / 到達上限: EVIDENCE_COLLECTED

## 1. 条件
- case `JA_01`(X Std a2 `japanese_title`、X-Std-7と同部位・leaf L7・policy JA_STD)。run dir `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_tru_ev_ja_01`(不追跡)。
- 注入方式(委任_03のX-Std-7=判定戻り値の注入、との差分): driverが **Primary ASR(`routing.transcribe`[ja-JP])と Secondary(Azure、`er007._azure_stt_strict`)の転写の最長の漢字/カタカナ連続1語を別語へ置換**(「コーヒー豆」→「天気予報」)。JA判定器(`evaluate_attempt_ja_with_cascade`)自身が3回ともTRUE_CONTENT_MISMATCHを出した(judge戻り値は無改変)。Production無改変、driver monkeypatchのみ(終了時復元)。
- `TTS_EXECUTION_MODE=STANDARD`(環境変数+CLI)、`--budget-jpy 3`、`stop_scope_check`事前実行 rc=0(`stop_check_ja_01.json`)。使用: TTS=gemini-3.1-flash-tts-preview(speech_metadata_flash_lite)、ASR=OpenAI(Primary)+Azure(Secondary)。モデルは正式経路のまま(評価用の最新モデル原則の対象外=本番経路そのもの)。
- 起動コマンド: `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/tools/tru_ev_ja_01.py --tts-execution-mode STANDARD --budget-jpy 3`(1回目はsystem python[google.genai無]でAPI呼出前に失敗=費用0、空のrun dirを削除して.venvで1回のみ実行)。
- 証跡: `evidence_runs/JA_01.json`(`driver_observation`に置換・HRQ書込経路の記録)。

## 2. 観測
| 項目 | 結果 |
|---|---|
| TTS attempt | 3(標準①②+minimal③。実API 3) |
| 待機 | 1回、実180.0秒(②NG後・③前)。STOP確認=cooldown 36+attempt 3 |
| LR | 0回(JA_STDはLR対象外) |
| 判定 | slot1〜3すべて判定器自身がTRUE_CONTENT_MISMATCH(Primary置換+Secondary置換の両方でNG)。slot3=is_last_slot |
| 最終status | STOPPED(標準2+fallback 1、合計3回で不合格) |
| Lock | `japanese_title`: HUMAN_REVIEW_REQUIRED(cumulative_tts_attempts=3) |
| 共有Gate | `m3_assembly_gate` status=BLOCK(X-Std-7と同じ観測) |
| 例外 | なし |
| **HRQ行** | **2行**(重複1件) |

### HRQ 2行の内訳(`driver_observation.log_human_review`)
1. JA判定器(er007 `evaluate_attempt_ja_with_cascade`、最終slotの`human_review_required`)→ `_log_human_review`(er007版)→ **`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`**(本runでは隔離先 `human_review_queue_ja.jsonl`)。final_status=TRUE_CONTENT_MISMATCH。
2. 委任_04で追加した `er127.register_ja_terminal_hr` → `er127.register_terminal_hr` → `er006_secondary_asr_01._log_human_review` → **`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`**(本runでは `human_review_queue.jsonl`)。final_status=TERMINAL_NG。

`register_ja_terminal_hr`は呼ばれ(returned=True、blk_depth=0、last_attempt status=OK/verified=False)、重複抑止(`is_duplicate_queue_entry`)は**書込先ファイルごと**に判定するため、JA判定器の書いたJA queueの行は検出されず、EN queueへ2行目が作られた。

## 3. 判定
- 「終端NG→Lock=HUMAN_REVIEW_REQUIRED・STOPPED・TTS3・待機180秒1回・LR0」: 実経路で観測(PASS)。
- 「終端NG1件=HRQ1行」: **未達(2行、JA queue + EN queue)**。委任_04の`register_ja_terminal_hr`の書込先がJA判定器と別queue。単体testは両queueを同一path扱いにしたため検出できなかった(委任_04の負の対照は『fix無効化でHRQ行が出ない』のみ)。
- したがってOPEN-540のJA部位HRQの限定解除は、このevidenceでは**解除不可**(新規OPEN候補: 分類=**修正へ進む**、Production軽微)。
- 修正案(次委任、Production編集): (A) `register_ja_terminal_hr`が書込先をJA queue(`ja_secondary._log_human_review`)にする(`register_terminal_hr`へ`log_fn`/queue選択引数を追加)。他: (B) EN queueへ一本化=JA判定器の書込と分裂するため非推奨。推奨=(A)。修正後に本driver(`tru_ev_ja_01.py`)を再実行して`hrq_rows==1`を確認(費用約¥0.6)。

## 4. 費用
実費 ¥0.56(raw_usage_log: openai 0.07 + gemini 0.16 + openai_asr 0.04 + azure 0.29)。上限¥3以内。
