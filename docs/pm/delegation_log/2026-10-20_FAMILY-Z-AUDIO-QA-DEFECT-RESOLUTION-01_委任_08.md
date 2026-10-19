# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_08(Fable受入照合の補助: (A)run_e2e_05 Std part3_c1 attempt2の`NUMERIC_EQUIVALENCE_MATCH`ラベルの11-8照合、(B)③の正式経路統合test[外側ループ経由・API 0]の既存有無確認と不足時の追加、(C)OPUS_FINDINGS_LEDGER新規行`OF-FZAQ-G-01`の書式確認)。2026-10-20。JPY0。
並行タスク衝突確認: 並行委任なし(委任_07完了、commit 65ab771b8/118c09356/5789f8a18)。SSOT編集権: `docs/pm/OPUS_FINDINGS_LEDGER.md`と`OPEN_ITEMS.md`(OPEN-283/OPEN-422行のみ)に限りあり。`CURRENT_SPEC.md`/`DECISION_LOG.md`/REGISTERは編集しない(文案のみ)。

## 性質/到達上限Status/禁止事項
- 性質: 照合(read-only)+test追加(コード変更はtestファイルのみ。Production module・Prompt・閾値・Gate変更禁止)。
- 到達上限Status: `FABLE_ACCEPTANCE_CHECKS_DONE_PENDING_FABLE`。
- 禁止: 有料API(TTS/ASR/LLM)0。run_e2e_04/05の成果物変更禁止(読取のみ)。HR Lock・承認記録変更禁止。`git add -A/-u/-f`・amend・rebase・force push・stash禁止。
- 修正範囲の線引き(11-8): (A)でラベル付与が承認済み仕様文(CURRENT_SPEC L2136付近のclassify分類・値等価正規化の定義)と矛盾する実装であれば「不具合(範囲内)」として原因箇所(関数:行)・最小修正案・影響範囲をRESULT_PACKETへ記す(**修正は本委任では行わない**。Fableが判断)。ラベルは正しく、名称が紛らわしいだけなら「仕様どおり(名称の注記候補)」と記す。
- Opus独立技術レビューGate(11-3): 非該当。
- 費用/日次: JPY0(当日既使用JPY28.79、出典RESULT_PACKET_FZAQ7.md)。
- 時間見込み: 60〜90分((A)25分/(B)30〜45分/(C)5分/報告10分)。並列化なし(小規模)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。本委任文は本メッセージ全文を逐語保存すること(要旨版はFAIL)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示する(本委任はTTSを伴わない)。
T-3: 本委任は費用上限を伴わない(JPY0)。

## ユーザー指示(原文、該当部抜粋。全文=`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_ROOT-CAUSE-WIRING-CLOSEOUT_USER.md`)
> **必要なruntime evidenceの充足状況を整理し、追加の確認が必要なら最小限の検証で取得すること。** 自然発生の誤発音やRewriteを待つために、不必要な有料TTSを繰り返さない。正式経路の発火証拠が不足する場合は、未確認事項を明示し、証拠なしにPRODUCTION_WIREDと判定しない。
> FableはClaudeの「完了」報告をそのまま採用せず、実装・正式経路・runtime evidence・SSOT・Gitを独立照合すること。

## 作業
(A) `er026_output/family_z_production_e2e_01/melos/run_e2e_05/a2/audit/tts_generation_results.json`の`segments.full_story_part3_c1`(attempts配列/`asr_judgement`/`audio_classification`/`primary`/`secondary`)と`er011_output/attempt_history.jsonl`のtheme_id=run_e2e_05・part3_c1行を読み、attempt2の判定経路を関数:行で再構成する: Primary転写`Mellos drank`→`classify_asr_match`(`er006_preprod_hardening_01_validation.py:1200-`)で何が返ったか(`NUMERIC_EQUIVALENCE_MATCH`はどの関数がどの条件で付与するか=Grep `NUMERIC_EQUIVALENCE_MATCH` in `*.py`)→Secondary転写と`SECONDARY_ASR_CORROBORATED_MATCH`の付与箇所(`er006_secondary_asr_01.py`/`er078_asr_unified_judge_01.py`)。問い: (a-1)文中に数値表現があるか(原稿を引用)。(a-2)`NUMERIC_EQUIVALENCE_MATCH`が「値等価正規化後に一致」の意味で、`Mellos`≠`Melos`の文に付くのは仕様文(CURRENT_SPEC Grep `NUMERIC_EQUIVALENCE|値等価`)上あり得るか。(a-3)実際の受理根拠(Secondaryが`Melos drank`を返した等)は何か。結論を「仕様どおり/不具合(範囲内)/不明」で1行、根拠を関数:行で。
(B) ③の統合test有無: `er020_lr_post_rewrite_expected_text_fzaq2_test_01.py`と`er020_lr_post_rewrite_m1_anchor_fzaq3_test_01.py`の各test名を列挙し、「LR採用→再TTS→`apply_a2_slowdown_postprocess`→減速後再検証が**書換え後文**で判定される」流れを、Production関数(`generate_with_a2_slowdown_outer_loop`または同等の外側ループ、`er003_v1_n3_01_tts_generate.py`)を**実際に呼んで**stub TTS/ASR(API 0)で通すtestが存在するか判定する。存在しなければ、`er003_v1_n3_01_tts_generate.py`の外側ループを対象に、TTS/ASR/ffmpegをmonkeypatchで差し替え、3 attempt NG→LR採用(`Melos drank`→`He drank`型のfixture、記事非依存)→減速後再検証で`post_slowdown_expected_text_source=="local_rewrite_text"`かつ比較対象が書換え後文であることを検証するtest `er003_lr_post_rewrite_outer_loop_fzaq8_test_01.py`を追加する(Production moduleは変更しない。既存のtest fixtureの流儀[fzaq2/fzaq3のmonkeypatch手法]に合わせる。LR経路の呼出しが外側ループから到達できない構造なら、その事実と到達経路[crosslevel `_retts_fn` L415等]を記し、到達可能な最小の統合点でtestを書く)。実行: `.venv\Scripts\python.exe -m pytest er003_lr_post_rewrite_outer_loop_fzaq8_test_01.py er020_lr_post_rewrite_expected_text_fzaq2_test_01.py er020_lr_post_rewrite_m1_anchor_fzaq3_test_01.py -q`。
(C) `docs/pm/OPUS_FINDINGS_LEDGER.md`のOF-FZAQ-G-01行が台帳の列構成(ID/出典/指摘/状態遷移)に合っているか確認し、合っていなければ同行のみ整形(内容不変)。

## 事前指定Read一覧
- `er026_output/family_z_production_e2e_01/melos/run_e2e_05/a2/audit/tts_generation_results.json`: Grep `full_story_part3_c1`→該当segmentの範囲のみ
- `er026_output/family_z_production_e2e_01/melos/run_e2e_05/audit/clip_evidence_summary_07.json`: Grep `part3_c1`
- `er006_preprod_hardening_01_validation.py`: Grep `NUMERIC_EQUIVALENCE_MATCH|SECONDARY_ASR_CORROBORATED_MATCH`→該当関数範囲
- `er006_secondary_asr_01.py`・`er078_asr_unified_judge_01.py`: Grep `SECONDARY_ASR_CORROBORATED_MATCH|NUMERIC_EQUIVALENCE`
- `er003_v1_n3_01_tts_generate.py`: Grep `def generate_with_a2_slowdown_outer_loop|def apply_a2_slowdown_postprocess|post_slowdown_expected_text_source|_retts|local_rewrite`→該当範囲
- `er003_v1_crosslevel_audio_02_common.py`:250-310, 405-425
- `er020_lr_post_rewrite_expected_text_fzaq2_test_01.py`・`er020_lr_post_rewrite_m1_anchor_fzaq3_test_01.py`: 全体(testファイルのため可)
- `docs/pm/OPUS_FINDINGS_LEDGER.md`: 1-15(列構成)+Grep `OF-FZAQ-G-01`

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep `NUMERIC_EQUIVALENCE_MATCH` in `*.py`(`-n`、`*_output`除外)→付与条件の特定。
- Grep `NUMERIC_EQUIVALENCE|値等価` in `CURRENT_SPEC.md`(`-n`、全文Read禁止)→仕様文の逐語。
- `OPEN_ITEMS.md`: Grep `^- OPEN-283`→(B)でtestを追加した場合のみ行末に「2026-10-20 委任_08: 外側ループ統合test(API 0)追加=<test名・件数>。live自然発火は未観測のまま」を追記。
- `docs/pm/ACTIVE_TASK.md`先頭に本委任ヘッダ3行を追記。

## 実行コマンド全文
- T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_08.md --json-out docs\pm\delegation_log\2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_08.md_check.json`
- test: `.venv\Scripts\python.exe -m pytest er003_lr_post_rewrite_outer_loop_fzaq8_test_01.py er020_lr_post_rewrite_expected_text_fzaq2_test_01.py er020_lr_post_rewrite_m1_anchor_fzaq3_test_01.py -q`
- secret scan: `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`
- Git: `git status --porcelain`→`git add docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_08.md docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_08.md_check.json`(+追加testファイル、+OPUS_FINDINGS_LEDGER.md/OPEN_ITEMS.mdを編集した場合のみ)→commit→push(直近commit 5789f8a18と同じ手順、`git log --oneline -3 origin/main`で到達確認)

## SSOT追記文
上記Grep一覧のOPEN-283追記文のみ。その他は文案としてRESULT_PACKETへ。

## Git(明示add対象・コミットメッセージ・trailer)
- commit: `FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_08: part3_c1判定ラベル11-8照合+③外側ループ統合test(<件数>、API 0)+OPUS台帳行整形`
- trailer: `Delegation: FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/委任_08`

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_FZAQ8.md`: (1)T-0 (2)(A)判定経路の再構成表(attempt1〜2、関数:行)と結論1行(仕様どおり/不具合/不明)+不具合なら最小修正案 (3)(B)既存test一覧と判定、追加testの名称・件数・結果、到達経路の事実 (4)(C)結果 (5)費用JPY0 (6)Git (7)判断候補(あれば、ラベルなし) (8)一覧外Read理由。判定整合行1行。
