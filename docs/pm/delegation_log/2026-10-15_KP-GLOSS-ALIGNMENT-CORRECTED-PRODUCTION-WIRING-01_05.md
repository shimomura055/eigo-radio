# 委任文(逐語) KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 委任_05

## 管理ID

`KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01`(KGCPW)委任_05(Fable判定のSSOT記録のみ。コード・Production・run dir無変更、有料API 0)。前提: 委任_03(`e46821295`)・委任_04(`ccc774f14`)commit済み。文案は`docs/pm/RESULT_PACKET_KGCPW4.md`(7)を基にし、**下記Fable判定を正**とする。git `index.lock`衝突時は30秒待ち最大3回再試行。他の並行委任なし。

## Fable判定(これを記録する)

- **PRODUCTION_WIREDは宣言しない。Status=`APPROVED_FOR_PRODUCTION`(Production正式runnerへ配線済み・既定ON・legacy撤去済み、PRODUCTION_WIRED判定は保留)。**理由: ユーザー指示「一つでも未確認なら`APPROVED_FOR_PRODUCTION`のまま管理し、未完了項目と理由を報告する」。
- 10条件: Family X=10条件すべて確認済み(委任_03、E1〜E10)。Family Z=条件1は注入で確認(自然発火は未観測)、条件4はZ正式CLIのHR停止確認済み・Z E2E完成(gate〜page_verify)未確認、条件6はa2再開確認済み・b1bのgloss HR未実施。条件2/3/5/7/8/9/10は確認済み。
- Z E2E未完の原因: gloss整合とは無関係の既存音声Human Review Lock(`er011_human_review_lock_01`、kp1_en=ASR TRUE_CONTENT_MISMATCH / kp3_en=TTS_FAILURE×2 / full_story_part1_c5=ASR_VALIDATION_UNCERTAIN「Melos said.」→「Nello said.」)で`tts_b1b`がrc=2停止。`approve_regenerate`は人間承認が必要な既存安全装置のためFableは承認せず→**USER_DECISION_REQUIRED(非ブロッキング: 承認すれば再生成約JPY5〜10+gate〜page_verifyでZ E2E完成evidenceを取得。承認しなければZ E2E完成は未確認のままAPPROVED_FOR_PRODUCTION維持)**。
- 費用: 委任_03 JPY8.35+委任_04 JPY38.74=KGCPW合計約JPY47.09(+委任_01/02は0)。量産単価影響 +JPY0.056/記事セット(委任_03実測、70円の約0.08%)。当日累計約JPY60/1,000。
- 既知の軽微逸脱(事実のみ): 委任_04で最初の2起動が12秒差(RESTART_STORM閾値未満・発動なし)/初回`--approved-budget-jpy 3`で見積guard停止→25で再実行(費用0)。

## 性質/到達上限Status/禁止事項

- 性質: SSOT追記のみ。到達上限: `KGCPW_SSOT_RECORDED`。
- 禁止: コード・test・run dir・evidence・`CURRENT_SPEC.md`の規定本文の変更(事実行の追記のみ可)。既存エントリの書換え(追記のみ)。git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f。有料API 0。
- 時間見込み: 約0.5h。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`check_delegation_prompt.py`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する。保存先: `docs/pm/delegation_log/2026-10-15_KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01_05.md`(全文逐語保存。要旨化禁止)。
T-2: 本委任はTTSなし。T-3: 費用0のためGuardrail文不要。

## ユーザー指示(原文)

委任_01保存ファイル(`docs/pm/delegation_log/2026-10-15_KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01_01.md`)に全文。本委任に効く逐語: 「一つでも未確認なら`APPROVED_FOR_PRODUCTION`のまま管理し、未完了項目と理由を報告する」「OPEN-359が未解決のまま、Family Xで不整合KPが完成版に流出しうる場合、PRODUCTION_WIREDを宣言しない」。

## KPI provenance欄 / Opus台帳更新

provenance: 該当なし。Opus台帳: `docs/pm/OPUS_FINDINGS_LEDGER.md`のOF-KGDC-01/02/03・OF-KGCPW-08/09にZ側evidence(E11b/c/d、注入・正式CLI)を追記(RESULT_PACKET_KGCPW4 (7)の文案)。既存行は書き換えず、各行末尾へ追記または直下に追記行。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_KGCPW4.md` (7)SSOT文案・(4)10条件表
2. `er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/VALIDATION_WIRING_04.md` §2(10条件表)・§3(費用)
3. `OPEN_ITEMS.md`: Grep `OPEN-356|OPEN-359|OPEN-360|OPEN-361|OPEN-362` → 現行文(OPEN-356を更新。他は変更不要なら触れない)。最大番号確認(現在367)。
4. `CURRENT_SPEC.md`: Grep `KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01|ER-003-KP-GLOSS-ALIGN-02` → 委任_02/03段落の位置(末尾に委任_04/05の事実段落を追記)
5. `DECISION_LOG.md`: Grep `KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01` → 既存エントリと索引形式
6. `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#6[0-9]|#70` → 最新番号(現在#69)、#60/#61の現行文
7. `docs/pm/REPORT_LEDGER.md` 末尾10行、`docs/pm/ACTIVE_TASK.md`:1-12

## 追記位置・更新位置の手順

- CURRENT_SPEC: 委任_02/03段落の直後に「委任_04/05(2026-10-15)」事実段落: Z正式CLI evidence(E11a〜e要点、run `run_kgcpw_z_e2e_01`)、10条件の充足状況(X全確認/Z部分)、**Status=APPROVED_FOR_PRODUCTION(配線済み・既定ON、PRODUCTION_WIRED未宣言。Z E2E完成evidenceは音声HR承認待ち)**。規定本文は変更しない。
- OPEN_ITEMS: OPEN-356を更新(見出し角括弧内Statusを「APPROVED_FOR_PRODUCTION・配線済み・PRODUCTION_WIRED判定保留[Z E2E完成evidence=音声HR承認待ち]」へ。本文に委任_04の事実・残る未確認4点・USER_DECISION[音声HR 3 clipの再生成承認]・費用合計を追記)。新規起票は不要(音声HR LockはOPEN-356内のサブ項目とする)。
- DECISION_LOG(追記、索引1行+本体): 「KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 委任_04/05 Fable判定(2026-10-15)」= 上記Fable判定の全文(10条件表のX/Z状況、PRODUCTION_WIRED未宣言の理由、費用、UDR)。
- REGISTER: 新規#70「KGCPW Z E2E完成のための音声HR Lock 3 clip再生成承認(`approve_regenerate`、約JPY5〜10)」UDR非ブロッキング、推奨=承認(理由: Z E2E完成evidenceが唯一の残件で、費用小・gloss配線とは独立の既存安全装置)。#60/#61に「委任_04で配線済み・PRODUCTION_WIRED判定保留」を注記(追記)。集計表を更新。
- REPORT_LEDGER: 2行(委任_04、委任_05)。
- Opus台帳: 上記。
- ACTIVE_TASK.md固定ヘッダ(L1-12を上書き、旧は「前タスク群(保持)」へ退避): KGCPW=`APPROVED_FOR_PRODUCTION(配線済み・PRODUCTION_WIRED判定保留)`・UDR-deferred に「#70 音声HR 3 clip再生成承認」を追加、QDC行の当日費用を「約JPY60/1,000」へ更新、ROLLOUT=盲検リプレイ実施方法ユーザー判断待ち、SKJT-02=STOP(試聴待ち)、CFSA=STOP。
- `docs/pm/RESULT_PACKET_KGCPW5.md`: 反映一覧(ファイル:行)。

## 実行コマンド全文

- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-15_KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01_05.md --json-out docs/pm/delegation_log/2026-10-15_KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01_05_check.json`
- secret scan: `.venv\Scripts\python.exe tools/secret_scan_01.py --staged`(hits=0)
- git: `git status --porcelain -- CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/USER_DECISION_REGISTER_01.md docs/pm/REPORT_LEDGER.md docs/pm/OPUS_FINDINGS_LEDGER.md docs/pm/delegation_log`、`git log --oneline -3`

## SSOT追記文

上記「追記位置」のとおり。ユーザー原文は逐語、事実はcommit hash付き(`e46821295`/`ccc774f14`)。

## Git(明示add対象・コミットメッセージ・trailer)

SSOT編集権: あり(上記6本)。明示add: SSOT6本+`docs/pm/delegation_log/..._05.md`(+`_check.json`)。`ACTIVE_TASK.md`はgitignore対象なら更新のみ。
コミットメッセージ: 「KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 委任_05: Fable判定のSSOT記録(X=10条件充足、Z=条件1注入確認/4 CLI停止確認・E2E未完/6 a2再開確認。Status APPROVED_FOR_PRODUCTION・配線済み・PRODUCTION_WIRED判定保留。Z E2E完成は音声HR Lock 3 clip再生成承認待ち=REGISTER #70。KGCPW費用合計約JPY47.09)。コード/Production無変更、JPY0」。push to origin/main。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_KGCPW5.md`へ: (1)T-0 (2)SSOT差分(ファイル:行・要旨) (3)REGISTER #70の文面と集計 (4)ACTIVE_TASK新ヘッダ全文 (5)commit hash・push・raw URL(CURRENT_SPEC・OPEN_ITEMS・DECISION_LOG) (6)確認できなかった事項・逸脱。

Fableは(2)(4)を照合する(受領≠受入)。
