# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 委任_02a(再開)。2026-10-20。前回の委任_02a agentはT-0(委任文全文の再出力による保存)で安全分類器に止められ、実装・API・SSOT・commitを一切行わずに中断した(費用JPY0)。本委任はその再開であり、**作業内容(W1〜W5)は前回の委任_02a委任文のとおり**。前回委任文の本文はFableが再送しない(再出力を避けるため)。代わりにsession transcriptから機械的に抽出して保存する(下記T-0手順)。
並行タスク衝突確認: opus-consultant(Opus_J、read-only)が`TRIAL_DESIGN_01.md`/`design_matrix_01.json`/`PHASE_A_RESULT_01.md`/`_judge.py`/`_eval.py`を読んでいる可能性がある。これらは編集しない。SSOT編集権: あり(前回委任文W4のとおり: `OPEN_ITEMS.md`新規行・`DECISION_LOG.md`末尾・`docs/pm/USER_DECISION_REGISTER_01.md`新規番号・`docs/pm/REPORT_LEDGER.md`)。

## 性質/到達上限Status/禁止事項
前回委任_02a委任文の「性質/到達上限Status/禁止事項」欄をそのまま適用(Trial準備、到達上限`PLW_PHASE_B_ASSETS_READY_PENDING_OPUS_J_AND_FABLE`、Azure Phase B/C呼出禁止、A/A'/P1/P2禁止、設計書・design_matrix改変禁止、wavはcommitしない、上限¥15 Guardrail[T-3定型文は前回委任文のとおり]、承認区分C、当日既使用JPY45.72)。Opus独立技術レビューGate(11-3): 非該当。時間見込み: 前回と同じ1.5〜2.5h(+T-0抽出10分)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。**本委任でのT-0の実施方法(逐語保存を自分で打ち直さない)**: (1)本メッセージ(再開委任文)は短いので`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_委任_02a_resume.md`へそのまま保存。(2)前回委任_02a委任文は`docs/pm/tools/extract_delegation_from_jsonl_01.py`でsession JSONLから抽出して保存する(委任_07で実績のある方法): `--jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index <N>`(Nを0から増やし、本文先頭が`# 委任文(Fable→sonnet-worker)`で管理ID行に`FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 委任_02a(Phase B準備`を含む**最初の**ものを採用。`--out`等の実引数名はhelpで確認)→既存の途中切れファイル`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_委任_02a.md`(4,300バイト)を**上書き**→文字数・sha256・check結果を記録。抽出ツールで取れない場合は、途中切れファイルの先頭に`<!-- 途中切れ(T-0未達、再出力は分類器により不可) -->`を付けて残し、理由をRESULT_PACKETへ記す(作業は継続)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batch不使用。T-2追記(7-5)4点は前回委任文のとおり。ただし呼出上限は前回agentの調査どおり**TTS 28 take+ffmpeg減速14=42 wav**に訂正する(前回委任文の「28+減速4=32」はFableの誤り)。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 上限¥15(Guardrail)。定型文は前回委任文のとおり。

## ユーザー指示(原文)
全文=`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_USER.md`(sha256 7d7b9e16…、4,096文字)。該当抜粋: 「3. 意図的に複数の文脈を作り、重み付けの有効性と副作用を評価する。」「4. 必要に応じて新規TTS音声を生成してよい。」「6. **Production設定・発音判定仕様は変更しない。**」「重要なのは、**認識してほしい固有名詞を含む正例だけでなく、本来Melosと認識してはいけない負例も設けること。**」「API費用を抑えるため、既存音声・キャッシュ・既存研究成果を優先利用する。」

## Fableの追加決定(前回agentの調査結果への回答)
1. wav数=42(TTS 28+減速14)で実施。manifestに固定。
2. **Charonはflash-lite+PD06(Aoedeと同じmodel/style)で生成**する(設計書§2-Bどおり。Trialの変数はVoiceであり、modelを揃える)。Production ZのCharonが対話経路(gemini-2.5-pro-preview-tts・Dialogue Style)である事実は**制約として設計書改訂提案とRESULT_PACKETに記録**(「Charon結果はナレーター経路のflash-liteでの結果であり、Production対話経路の再現ではない」)。
3. TTS低レベル再利用点は前回agentの調査どおり(`er033_tts_flash_lite_backend_wiring_01.resolve_tts_call_and_prompt`→`er002_common._call_tts_with_retry`→`er003_b1_p3u_audio.trim_english_keyword_silence`(0.35)→`write_wav_float`、入力は`n3_tts.tts_safe_news_en`、減速は`er008_a2_postprocess_slowdown_01.apply_a2_slowdown`のffmpeg部分のみ、Production量産関数[`generate_a2_segment_with_slowdown`等]はログ副作用があるため使わない)。Primary転写=`er006_asr_provider_routing_01.transcribe(wav,'en-US')`。保護語=`protected_check`/`tokenize`再利用。費用=`er005_cost_logger.install()`+THEME_TAG `PLW_TRIAL_01`。
4. 前回委任文のW1〜W5・事前指定Read/Grep・実行コマンド・SSOT追記文・Git・報告項目はそのまま有効(抽出保存した前回委任文を参照して実施)。commit messageの「<n>wav」は42、減速は14。RESULT_PACKETは`docs/pm/RESULT_PACKET_PLW2a.md`。

## 事前指定Read一覧
- 抽出保存後の`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_委任_02a.md`(前回委任文、全体)
- `docs/pm/tools/extract_delegation_from_jsonl_01.py`:1-60
- その他は前回委任文の「事前指定Read一覧」のとおり

## 事前指定Grep一覧+追記位置・更新位置の手順
前回委任文のとおり。追加: `docs/pm/ACTIVE_TASK.md`先頭ヘッダに「委任_02a 再開(T-0は転写抽出)」と記す。

## 実行コマンド全文
- 抽出: `.venv\Scripts\python.exe docs\pm\tools\extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 0 --out docs\pm\delegation_log\_extract_try_0.md`(indexを増やして照合、採用後に一時ファイル削除)
- T-0 check(2件): `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_委任_02a.md --json-out docs\pm\delegation_log\2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_委任_02a.md_check.json` / `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_委任_02a_resume.md --json-out docs\pm\delegation_log\2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_委任_02a_resume.md_check.json`
- TTS/Primary/test/費用/secret scan/Git: 前回委任文の「実行コマンド全文」のとおり(TTSは`$env:TTS_EXECUTION_MODE='STANDARD'`明示、`--budget-jpy 15`)。

## SSOT追記文
前回委任文W4のとおり。

## Git(明示add対象・コミットメッセージ・trailer)
前回委任文のとおり(add対象に`..._委任_02a_resume.md`+checkを追加)。trailer: `Delegation: FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01/委任_02a`

## 報告(RESULT_PACKET項目)
前回委任文のとおり+「T-0の実施方法(抽出成否・文字数・sha)」を(1)に含める。