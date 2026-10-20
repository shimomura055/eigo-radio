# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 委任_02a(Phase B準備: 設計書§2-Bの42 wav生成[TTS、Aoede通常/6%減速・Charon]+各wavのPrimary(OpenAI)転写+eval拡張[他語perturbation指標]+wav manifest固定+SSOT初回記録。**Azure Phase B/C呼出は本委任では実行しない**[Opus_J任意レビューの結果をFableが反映した後の委任_02bで実行])。2026-10-20。
並行タスク衝突確認: 並行でopus-consultant(Opus_J、read-only、`TRIAL_DESIGN_01.md`/`design_matrix_01.json`/`PHASE_A_RESULT_01.md`/`_judge.py`/`_eval.py`を読む)が走る。本委任は**`TRIAL_DESIGN_01.md`・`design_matrix_01.json`・`PHASE_A_RESULT_01.md`・`_judge.py`を編集しない**(読取のみ)。`_eval.py`の拡張は**新ファイル`er084_azure_phraselist_weight_trial_01_eval_ext.py`**として追加する(既存evalは触らない)。SSOT編集権: あり(`OPEN_ITEMS.md`新規行、`DECISION_LOG.md`末尾、`docs/pm/USER_DECISION_REGISTER_01.md`新規番号、`docs/pm/REPORT_LEDGER.md`。Grep→該当行のみ)。

## 性質/到達上限Status/禁止事項
- 性質: Trial準備(Trial専用経路)。Production module・Prompt・判定・設定は変更しない(`er006_secondary_asr_01.py:288`の古いコメントも触らない)。
- 到達上限Status: `PLW_PHASE_B_ASSETS_READY_PENDING_OPUS_J_AND_FABLE`。
- 禁止: (1)Azure STT呼出(Phase B/C)。(2)A案/A'案/P1/P2の実装。(3)設計書・design_matrixの改変(改訂が必要と判断した点は文案としてRESULT_PACKETへ。改訂は委任_02bで§9履歴付きで実施)。(4)`git add -A/-u/-f`・amend・rebase・force push・stash。(5)wavのcommit(`er084_output/`配下のwavは未追跡のまま。manifest jsonにsha256を記録)。
- 修正範囲の線引き(11-8): 不具合修正なし。
- Opus独立技術レビューGate(11-3): 本委任=非該当(Opus_Jは任意レビュー、並行中)。
- 費用/日次: 当日既使用JPY45.72(出典: RESULT_PACKET_PLW1.md `daily_dev_cost_01` adopted)/残JPY954.28/本委任見積JPY≤15(根拠: TTS gemini-3.8-flash-lite-tts 28 take×約JPY0.3≈8.4[設計書§4]、OpenAI gpt-4o-mini-transcribe 42 wav×約JPY0.1≈4.2、予備2)/改善見込み高/承認区分C(ユーザー承認済みTrial・案件合算[probe+A 16.93+本委任≤15+02b見込み約49+C予備≤60≈141]300円以下・日次内)。
- T-3: 上限¥15(Guardrail、本委任分)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 時間見込み: 全体1.5〜2.5h(T-0 5分/TTS 28 take生成+減速版4 30分/Primary転写42 15分/manifest 10分/eval_ext+test 30分/SSOT 20分/報告10分)。並列化: TTS生成とeval_ext実装は独立(先にTTSをbackgroundで流す)。Primary転写はwav完成後に並列可。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。**本委任文は本メッセージ全文を一字一句そのまま保存する(要旨版・節の省略はFAIL)。**
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい。T-2追記(7-5)4点: (1)差分生成=設計書§2-Bの28 take(新規文のため既存音声なし。P1の4take/voiceは設計どおり)、(2)既存音声再利用: run_e2e_05/04に同一文は無い(新規文)。録音2は既存を再利用済み、(3)TTS scriptに`--budget-jpy 15`相当のguard(呼出数上限28+減速4=生成32ファイル、超過時停止)を実装、(4)全再生成ではない(新規Trial音声)。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 定型文は上記「性質」欄に記載済み。

## ユーザー指示(原文、該当部抜粋。全文=`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_USER.md`、sha256 7d7b9e16…)
> 3. 意図的に複数の文脈を作り、重み付けの有効性と副作用を評価する。 4. 必要に応じて新規TTS音声を生成してよい。 6. **Production設定・発音判定仕様は変更しない。** 7. A案・A'案は引き続きREJECTED。今回のTrialで暗黙に再採用しない。
> 重要なのは、**認識してほしい固有名詞を含む正例だけでなく、本来Melosと認識してはいけない負例も設けること。**
> **試行回数・対象文脈・比較方法を実行前に設計・記録し、結果を見て都合のよい条件だけ採用することを防ぐ。**
> - API費用を抑えるため、既存音声・キャッシュ・既存研究成果を優先利用する。 - 独立した比較や分析は並列化する。

## 作業
W1. **TTS生成**(`er084_azure_phraselist_weight_trial_01_tts.py` 新規): `design_matrix_01.json`の正例P1〜P7・負例N1〜N4の最終文を読み、Production Zと同じTTS呼出(Grep `gemini-3.8-flash-lite-tts|def generate_narrator|real_generators` in `er063_family_z_audio_01.py`・`er003_v1_n3_01_tts_generate.py`で、Std narratorのvoice/style/promptの実値をrun_e2e_05の`a2/audit/tts_generation_results.json`から取り、**同じ関数**をTrial用out_dirで呼ぶ。Production run dirには書かない)で生成: Aoede(P1 4take、P2〜P7・N1〜N4 各1take)+Charon(同配分)=28 take。Aoede P1 4takeに対し**Production Std経路と同じ6%減速後処理**(`apply_a2_slowdown_postprocess`またはそのffmpeg部分の既存関数を呼ぶ。ASR再検証部分は呼ばない)で減速版4本=計32 wav(設計書§2-Bの42は「P1 8take+減速4+P2〜P7 18+負例12=42」。wav数の内訳を再計算し、設計書と差があれば**設計書は編集せず**RESULT_PACKETに差分と正しい内訳を記す)。出力=`er084_output/azure_phraselist_weight_trial_01/wav/<id>_<voice>_take<n>[_slow6].wav`。`TTS_EXECUTION_MODE=STANDARD`。費用は`er005_cost_logger` THEME_TAG `PLW_TRIAL_01`(委任_01の方式)。生成後、各wavの長さ(秒)・sha256・voice・style・model・take・元文・減速有無をmanifest `wav/manifest_01.json`へ固定(以後不変。Phase B/Cはこのmanifestのみ参照)。負例の判定用canonical(confusable語→`Melos`置換文)もmanifestに固定(設計書§2-B)。
W2. **Primary転写**: 各wav 1回、Productionと同じOpenAI Primary ASR関数(`er006_secondary_asr_01.py`または呼出元のPrimary経路をGrep `gpt-4o-mini-transcribe|def transcribe_primary|openai`)をTrial用に呼び(Productionファイルへの書込み無し)、`raw/primary_calls.jsonl`へ保存(wav id・転写・所要・費用)。42呼出(wav数に合わせる)、並列可(rate limit配慮)。
W3. **eval拡張**(`er084_azure_phraselist_weight_trial_01_eval_ext.py` 新規+`_eval_ext_test_01.py`): 既存evalの集計に加え、(a)**他語perturbation指標**=各(wav,条件)で、Azure転写とwav原稿の語単位差分のうち、ターゲット語(`Melos`とそのvariant)以外の差分語数と差分内容(例`onto→unto`)、保護語(数値・否定、`protected_check`相当の語集合はProduction関数を呼ぶ)への影響有無、(b)条件別の非ターゲット差分の合計と、ベースライン(`pl_unspecified`)との増減、(c)負例の誤`Melos`件数と、負例canonical注入のProduction判定(PASS系なら「誤PASS」)の集計、(d)設計書§3の判定基準①〜⑤を機械的に評価して候補Status(VALIDATED候補/REJECTED/判断候補/INCONCLUSIVE)を出す関数(閾値は`design_matrix_01.json`または設計書から読み、ハードコードしない)。testはPhase Aのraw 15行+合成行で検証(API 0、10件程度)。
W4. **SSOT初回記録**: (a)`OPEN_ITEMS.md`新規行 OPEN-424(末尾、既存行の書式に合わせる): 「OPEN-424 Azure PhraseList重み比較Trial(FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01、POST_USER_VALIDATION、ユーザー2026-10-20承認、原文sha256 7d7b9e16…、4,096文字)。Production非変更・到達上限VALIDATED・A/A' REJECTED維持。Phase A(録音2×5条件×3回、実費JPY16.93): 決定論的、未指定≡1.0(送信JSON `dgi.bias`で実証)、w1.5で`Mellows`→`Melos`(判定PASS_WITH_WARNING)、w2.0は`onto→unto`副作用。Status=PHASE_B_ASSETS_READY(Opus_J任意レビュー中)。付記: `er006_secondary_asr_01.py:288`のコメント『SDKは重みAPI非公開』は事実誤認(SDK 1.50.0に`setWeight`あり、範囲0〜2)=Production採用判断時に是正対象」(b)`DECISION_LOG.md`末尾: 2026-10-20 ユーザー承認7項目(原文パス・sha・文字数)+Fable決定(Phase A実走・Opus_J任意レビュー・Phase B準備)。(c)`docs/pm/USER_DECISION_REGISTER_01.md`: 末尾番号を確認し次番号で「判断済み(2026-10-20) Azure PhraseList重み比較Trial実施承認(1.0/1.5/2.0、複数回・複数文脈・新規TTS可・Production設定/判定仕様不変・A/A' REJECTED維持)。Production採用は別判断。OPEN-424」。(d)`docs/pm/REPORT_LEDGER.md`: 本管理IDの行追加(初回報告未)。
W5. `docs/pm/ACTIVE_TASK.md`先頭に本委任ヘッダ5行以内。

## 事前指定Read一覧
- `docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01/TRIAL_DESIGN_01.md`:30-64(§2〜§3)、`design_matrix_01.json`(全体、小ファイル)
- `docs/pm/RESULT_PACKET_PLW1.md`: Grep `voice|Aoede|Charon|style|費用|cost`→該当範囲
- `er026_output/family_z_production_e2e_01/melos/run_e2e_05/a2/audit/tts_generation_results.json`: Grep `"voice"|"style"|"model"|speaking|instruction`→narrator entry 1件分の範囲
- `er063_family_z_audio_01.py`: Grep `real_generators|def _gen_narrator|generate_a2_segment_with_slowdown|voice=`→該当範囲
- `er003_v1_n3_01_tts_generate.py`: Grep `def generate_a2_segment_with_slowdown|def apply_a2_slowdown_postprocess|ffmpeg|atempo`→該当範囲
- `er006_secondary_asr_01.py`: Grep `gpt-4o-mini-transcribe|def .*primary|openai`→Primary転写関数の範囲
- `er084_azure_phraselist_weight_trial_01_lib.py`・`_run.py`・`_eval.py`: 全体(Trialファイル、小)
- `er005_cost_logger.py`:30-70
- `er084_output/azure_phraselist_weight_trial_01/raw/azure_calls.jsonl`: 先頭3行(行形式)
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `^- #12[0-9]`→末尾番号
- `OPEN_ITEMS.md`: Grep `^- OPEN-42[0-9]`→末尾番号・書式(全文Read禁止)

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep `protected_check|def _protected|NEGATION|NUMERIC` in `er006_preprod_hardening_01_validation.py`→保護語判定関数の再利用箇所(W3(a))。
- Grep `THEME_TAG` in `er084_azure_phraselist_weight_trial_01_lib.py`→費用記録の方式を踏襲。
- `OPEN_ITEMS.md`: Grep `^- OPEN-423`→その直後(または台帳末尾の規約位置)にOPEN-424を追加。
- `DECISION_LOG.md`: Grep `^## 2026-10-20`→最後のエントリの後に追加。索引リストがあれば1行追加。
- `docs/pm/REPORT_LEDGER.md`: Grep `FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01`→同書式で新行。

## 実行コマンド全文
- T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_委任_02a.md --json-out docs\pm\delegation_log\2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_委任_02a.md_check.json`
- TTS: `$env:TTS_EXECUTION_MODE='STANDARD'; .venv\Scripts\python.exe er084_azure_phraselist_weight_trial_01_tts.py --design docs\research\FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01\design_matrix_01.json --out er084_output\azure_phraselist_weight_trial_01\wav --budget-jpy 15 --tts-execution-mode STANDARD`(先に`--dry-run`で生成数・見積を出力)
- Primary転写: `.venv\Scripts\python.exe er084_azure_phraselist_weight_trial_01_run.py --manifest er084_output\azure_phraselist_weight_trial_01\wav\manifest_01.json --phase PRIMARY --out er084_output\azure_phraselist_weight_trial_01 --budget-jpy 6`(`--phase PRIMARY`を`_run.py`に追加実装。Azure phaseは呼ばれない構造にしtestで固定)
- test: `.venv\Scripts\python.exe -m pytest er084_azure_phraselist_weight_trial_01_test_01.py er084_azure_phraselist_weight_trial_01_eval_ext_test_01.py -q`
- 当日費用: `.venv\Scripts\python.exe docs\pm\tools\daily_dev_cost_01.py --date 2026-10-20`
- secret scan: `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`
- Git: `git status --porcelain`→明示add→commit→push(直近commit 8112dc2e8と同じ手順、`git log --oneline -3 origin/main`で到達確認)

## SSOT追記文
上記W4の文案を実値で埋めて使用(REGISTER番号・OPEN行位置は実確認後)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1: `docs/pm/delegation_log/2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_委任_02a.md`(+check)、`er084_azure_phraselist_weight_trial_01_tts.py`、`_run.py`(PRIMARY phase追加)、`_eval_ext.py`、`_eval_ext_test_01.py`、`er084_output/azure_phraselist_weight_trial_01/wav/manifest_01.json`、`raw/primary_calls.jsonl`、cost log(wav除外)。msg: `FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 委任_02a: Phase B音声<n>wav生成(Aoede/Charon/6%減速、manifest固定)+Primary転写<n>+eval拡張(他語perturbation・負例誤PASS・判定基準自動評価)、実費JPY<v>`
- commit 2: SSOT 4ファイル。msg: `FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 委任_02a: SSOT初回記録(OPEN-424/DECISION_LOG/REGISTER #<n>/REPORT_LEDGER)`
- trailer: `Delegation: FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01/委任_02a`

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_PLW2a.md`: (1)T-0 (2)生成wav一覧(id/voice/take/減速/秒/sha先頭8)と設計書§2-Bとの件数差分 (3)Primary転写の要約(正例でのMelos認識数、負例での出方) (4)eval_extの指標定義とtest結果 (5)SSOT差分(ファイル:行、REGISTER番号) (6)費用(TTS/OpenAI別、当日累計) (7)Git (8)設計書の改訂提案(あれば文案のみ) (9)判断候補(あれば、ラベル無し) (10)一覧外Read理由。判定整合行1行。