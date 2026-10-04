## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_67)。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: rep25(委任_66)で発生した**Safety-critical B3の見逃し**(Stage 1がMAJORで検出した因果`so`のclaimを、Stage 2[V7b、1 call]がACCEPTABLEへ降格→Rewriteされず合格)の原因診断(有料・限定)と、対策の設計(実装しない)、費用見積り、Opus条件A向けpacket作成。ユーザーのSafety KPI=重大Fact見逃し0件に反する事象であり、「原因特定→対策→限定再確認」の原則に従う。L6(完結文復元)は関与していない(Stage 2は照合より前段)。
- 到達上限Status: 診断結果+対策設計+packet。実装・rep25再開・29件再確認は次委任以降。次Trial(10本)は開始しない。
- 禁止事項:
  - コード変更禁止(診断スクリプトの新規作成のみ可: `er052_open233_stage2_b3_misdowngrade_diag_01.py`)。Production path変更禁止。Checker Prompt・Schema変更禁止。
  - V7b・V7の原則文を変更しない(診断で両者を比較するだけ)。「既存より厳しくする変更」を勝手に実装しない(設計として提示)。
  - 不要な再測定・惰性的retryをしない。測定のnは下記のとおり固定。
  - `git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。
- 費用上限: 上限¥15(Guardrail。内訳の目安: 診断(a)¥3、(c)¥6、合計¥9前後)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計¥573.9699、上限¥900。
- Opus独立技術レビューGate: 対策がStage 2の判定構造(Safety処理)の変更にあたるため条件A該当。本委任でpacketを作り、Opusへの依頼はFableが行う。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。記録用)。
T-2: TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示する。(本委任はTTSを伴わない。)
T-3: 費用上限[Cap]は暴走防止のGuardrailであり、Cap到達=自動STOPではない。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_67.md`。委任文は全文そのまま保存(要旨化不可)。一時ファイルはリポジトリ外(`%TEMP%`配下)。報告用`.md`をWriteツールが拒否する場合は、Pythonスクリプトからファイル出力する。全体回帰を回す場合は`PYTHONIOENCODING`を設定しないシェルで実行する(委任_66の注意8)。

## ユーザー指示(原文、該当部分)

````
必ず以下のKPIを同時に満たす前提で設計・検証してください。
- Primary:USER_DECISION_REQUIRED / Human Review 0件
- Safety:重大Fact見逃し 0件
- Cost:平均 +¥2/記事以内
````
(2026-10-02)「単に1回TrialがFAILした…という理由だけでは戻さず…原因特定→対策→限定再確認まで進めてください。」
(2026-10-03)「数値・主体・否定・比較・時期などの機械的な安全装置については、今回の採用内容だけを理由に勝手に緩めないでください。」

## 作業1: 事実の確定(¥0)

- rep25 `bgroup_B3` s1のinstance JSON(`er052_output/open233_self_recovery_flow_runner_01_rep25/`)から、Stage 1の出力(claim・severity・issue・related_fact_id・`dev`フラグ)、Stage 2の入力(本文・rubric版・batch構成)・出力(materiality・basis/explanation逐語)、floor適用の有無(`FLOOR_FLAGS`該当なし=floor対象外か)、`apply_stage2_two_of_two`の適用条件と本件で適用されなかった理由(Grep `apply_stage2_two_of_two`、`two_of_two`、`disclosure_gap`で該当範囲を読む)、hook-aware Stage 2の関与、`SAFETY_CRITICAL_CLAIM_DEFS`のB3定義とrep25の`residual_at_pass`記録、を設計書`docs/pm/design_open233_stage2_safety_downgrade_01.md` §1に逐語で整理。
- 既存ログ全体(iter1〜7、rep7〜25)で、Safety-critical 5件(B3、B4-a、A2A3-0、A4-0、A5-0)のclaimがStage 2で非BLOCKINGになった件数・rubric版別(R3'''/V4〜V7/V7b)・最終結果(Rewrite有無・合格/STAGE4)を集計(§2)。委任_66報告の「B3同claim 39件: BLOCKING 31/QUALITY 6/ACCEPTABLE 2」を出発点に、Rewrite前本文に対する判定だけを抜き出す(Rewrite後本文への判定は除外)。
- rep25 B3 s1のStage 1入力(Stage 1がfresh/reuse/`substitute_baseline_on_stage1_miss`のどれか)と、rep24 B3 s1との差(本文・claim文言・batch内の他claim)を比較(§1)。

## 作業2: 診断測定(有料、固定n)

診断スクリプト`er052_open233_stage2_b3_misdowngrade_diag_01.py`(既存`er052_open233_element_trial_safety_control_06.py`のStage 2呼び出しを再利用)。出力`er052_output/open233_stage2_b3_misdowngrade_diag_01/`(生応答・`results_01.json`・`results_01.md`)。
- (a) rep25 B3 s1と**同一入力**(同じ本文・同じclaim・同じbatch構成)で、V7b n=10、V7 n=10。各回のmaterialityとbasisを記録。非BLOCKING率を版別に出す。V7bのみで出るならV7bの文言(「方向・時期のニュアンスの差で事実関係の核心が保たれているものは、この限りではない」)が因果claimへ波及している仮説を、basis逐語で確認。
- (b) 同じclaimを**単独**(batchに他claimを含めない)でV7b n=5。batch構成の影響を見る。
- (c) Safety-critical残り4件(B4-a、A2A3-0、A4-0、A5-0)+K16+K20を、委任_61再較正と同じ入力でV7b n=5ずつ(委任_61はn=2のみ)。非BLOCKING率を出す。
- 単価はrep24実測¥0.14/call。(a)20+(b)5+(c)30=55 call≈¥7.7。最初に1 callで単価を確認し、見込みが¥12を超えるなら(c)のnを3へ落として報告。

## 作業3: 対策の設計(実装しない、§4)

- 前提: Stage 2は「Checkerが重大(MAJOR)と検出した指摘を、軽微/問題なしへ降格する」権限を持つ単独LLM判定で、非決定性により一定率で重大を取りこぼす。KPI(重大見逃し0)に対し、単独判定での降格は構造的に不十分。
- 案S1「降格の2-of-2」: Checker severity=MAJORの指摘について、Stage 2の1回目が非BLOCKINGのときだけ、独立した2回目のStage 2呼び出し(同rubric、同入力、temperature既定)を行い、**2回とも非BLOCKINGの場合のみ降格**。1回でもBLOCKINGなら BLOCKING。API失敗はBLOCKING。既存の`apply_stage2_two_of_two`の仕組みを拡張できるか、別関数かを明記。ユーザーが判断D/選択肢3で採用した「追加確認2回とも重大でない場合だけ軽微へ戻す」原則と同型。
- 案S2「Safety-critical相当の決定論ガード」: 因果接続(`so`/`because`/`therefore`/`as a result`/`led to`等)でLedgerに因果が無い場合をfloor(`changed_causality`)として追加。→ 新しい機械的安全装置の追加=ユーザー判断事項、かつ過剰Majorを増やす恐れ。参考案として記載し推奨しない理由を書く。
- 案S3「V7b文言の限定」: 「この限りではない」の適用範囲を比較・時期の語に明示限定。→ 診断(a)でV7b起因が確認された場合のみ併用候補。
- 各案について: 重大見逃しへの効果(診断データで試算: 1回判定の見逃し率pなら2-of-2はp²)、過剰Major・不要Rewrite・Human Reviewへの影響(増えない根拠: 2-of-2は降格を減らすだけで、Rewriteは既存のラダー)、費用(rep24ログで「Checker MAJOR→Stage 2非BLOCKING」の件数/runを数え、2回目call¥0.14×件数で平均+¥/記事を試算。+¥2/記事以内か)、cycleごとの再評価・Recheck由来への適用・floor_verify/2-of-2(既存)との相互作用、Production配線時の対応箇所。
- 推奨案と理由(KPI 3つ同時)。既存より厳しくなる点(降格が減る)は、Safety KPI 0件のための対策であり、ユーザー承認を要する旨を明記(USER_DECISION候補)。

## 作業4: Opus向けcontext packet

`docs/pm/opus_packet_open233_stage2_safety_downgrade_01.md`(雛形(a)〜(g)。(g)の独立レビューブロックは逐語貼付、条件A、既存Opus#8[floor整合、F5の2回確認]との関係を記載)。(a)論点: 1.単独LLM判定による降格は重大見逃し0と両立するか 2.案S1の2-of-2は十分か(p²の仮定の妥当性、同一prompt再呼び出しの独立性) 3.より単純な構造(例: MAJORは降格不可、QUALITY/MINORのみStage 2対象)はないか 4.過剰Major・不要Rewrite・Human Reviewを増やさないか 5.費用 6.cycle/Recheck/floor_verify/既存2-of-2との整合 7.Production配線時の矛盾。(b)診断データ・既存ログ集計・費用試算・B3 claimと本文の逐語。(c)runner行範囲(Grep確認列)。

## 作業5: 記録

- REPORT §49「B3見逃し(rep25)の原因診断と対策設計(委任_67)」。`OPEN_ITEMS.md` OPEN-233行Status「rep25でSafety-critical B3見逃し1件(Stage 2単独判定の降格)→原因診断【結果】・対策設計(S1推奨案)・Opus条件A待ち(委任_67)。KPI: Human Review未実証、重大見逃し1件(是正中)」(旧Statusは「旧Status参考(委任_66)」で残す)、次Action末尾「(委任_67)Opus#10→Fable照合→ユーザー確認(降格2-of-2=既存より厳しくする変更)→実装→rep25再開→29件再確認」。`docs/pm/REPORT_LEDGER.md`。`docs/pm/ACTIVE_TASK.md` Status=「IN_PROGRESS(B3見逃しの診断・対策設計、Opus待ち)」(addしない)。`CURRENT_SPEC.md`・`DECISION_LOG.md`は編集しない。

## 事前指定Read一覧

- rep25 B3 s1 instance JSON(該当フィールドをGrep/Pythonで抽出)。rep24 B3 s1(比較)。
- runner: Grep `apply_stage2_two_of_two`、`two_of_two`、`run_stage2`、`llm_materiality`、`hook`(Stage 2 hook-aware)、`SAFETY_CRITICAL_CLAIM_DEFS`、`detect_safety_critical_misdowngrades`、`residual_at_pass` → 該当範囲(全文Read禁止)。
- `er052_open233_self_recovery_stage2_calibration_01.py`: Grep `V7B`、`V7`、`run_stage2_batch_variant` → 該当範囲。`er052_open233_element_trial_safety_control_06.py`: 全文(再利用)。
- 既存ログ集計: `er052_output/open233_self_recovery_flow_runner_01_*/`のinstance JSON(Pythonで走査。手Readしない)。
- `docs/pm/design_open233_floor_alignment_01.md`: §2-4(F5)のみ。`docs/pm/opus_l2_review_open233_self_recovery_08.md`: Grep `2回|two|p²|独立` → 該当行。
- テンプレート: `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`、`docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md`。
- `OPEN_ITEMS.md`/REPORT/REPORT_LEDGER: Grep `委任_66` → 更新位置のみ。

## 事前指定Grep一覧+追記位置

- 上記のとおり。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_67.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_67.md_check.json

診断(有料):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_stage2_b3_misdowngrade_diag_01.py --stage probe
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_stage2_b3_misdowngrade_diag_01.py --stage main --n-a 10 --n-b 5 --n-c 5 --budget-jpy 12
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_stage2_b3_misdowngrade_diag_01.py --stage agg
(引数名は実装に合わせてよい。)

テスト: runner未変更のため回帰不要。`git status --porcelain`で混入なしを確認。

順序: T-0 → 作業1 → 2 → 3 → 4 → 5 → commit/push → 報告。

## Git(明示add対象・コミットメッセージ)

- SSOT編集権: `OPEN_ITEMS.md`の1行、`REPORT_LEDGER.md`の1行、REPORT。`CURRENT_SPEC.md`/`DECISION_LOG.md`/`PM_GOVERNANCE.md`は編集しない。
- add対象: 診断スクリプトと出力、設計書、packet、REPORT、`OPEN_ITEMS.md`、`REPORT_LEDGER.md`、委任ログ`_67.md`・`_check.json`。
- メッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: rep25のSafety-critical B3見逃し(Stage 2単独判定の降格)を診断【V7b非BLOCKING率X%/V7 Y%】、降格2-of-2等の対策を設計しOpus条件A向けpacketを作成(未実装、Production未変更)(委任_67)`
- commit前に`git status --porcelain`で混入なしを確認。

## 報告(RESULT_PACKET項目)

(1)結論10行以内(原因は何か: 非決定性/V7b文言/batch構成/入力差)、(2)事実の確定(§1要約、2-of-2が適用されなかった理由)、(3)既存ログ集計表、(4)診断測定の結果表(版別・単独/batch別・Safety-critical別の非BLOCKING率、basis代表逐語)、費用、(5)対策案S1〜S3の比較表と推奨案・費用試算(+¥/記事)、(6)USER_DECISION候補、(7)packet文字数、(8)SSOT更新箇所、(9)T-0・commit・push・raw URL、一覧外Read、確認できたことと推測の区別。
