## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_63)。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー決定[5回目](2026-10-04、選択肢3)の手順5「少数flowが問題なければ、29件横断を1回だけ実施」を行う(有料、目安¥35〜70、ユーザー承認済み)。少数flow(委任_62、rep23)はFableが照合し、安全項目(JA変更0・解放0・Safety-critical残存0・例外0)PASS、不要Rewriteの形式FAILは「正常記事群=neg3の1 instanceのみ・BLOCKING claimがK16型(継続中の出来事の復活)でLLM・floor双方が重大判定」のため実質的な問題ではないと判断して29件横断へ進める。**本委任は29件横断1回と集計・記録まで。** そこでSTOPし、次Trial(5記事×Standard/Advanced=10本)は開始しない。Closeout確認(8項目)は次の委任_64。
- 到達上限Status: Trial評価(`VALIDATED`相当の記録)まで。Production採用判断・`PRODUCTION_WIRED`はしない。自己修復機構本体はProduction未接続。
- 禁止事項:
  - Production正式path(`er003*`〜`er019*`)の変更禁止。編集は`er052_open233_*`のみ。runner本体のロジック変更は禁止(不具合を見つけたら修正せず報告。集計スクリプトの追加・表示修正は可)。
  - 新しい仕様候補・新しい対策を勝手に追加しない(例: A2A3で観測された「Checker範囲が`2.6 percent`の途中から始まる切断」を許容する変更は、ユーザー判断事項であり実装しない)。新しいProduct判断が必要になったら`USER_DECISION_REQUIRED`としてSTOPし報告。
  - 29件横断は**1回だけ**。再実行・部分再実行・n増しをしない(失敗runの再実行も不可。失敗は失敗として記録)。
  - 日本語本文・日本語タイトルへの修正が発生したら即STOP。重大と思われる解放が1件でもあれば即STOP。Safety-critical 5件(B3、B4-a、A2A3-0、A4-0、A5-0)のいずれかが`residual_at_pass`に残ったら(=検出されず合格)即STOP。例外・クラッシュが2 instance以上で起きたら即STOP。
  - `git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。
- 費用上限: 上限¥70(Guardrail。ユーザー目安¥35〜70)。1 instance-runのrunner既存Guardrail¥7は変更しない。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計¥556.1277、上限¥900。
- Opus独立技術レビューGate: 新構造なし(確認のみ)。該当なし。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`check_delegation_prompt.py`を実行する。結果をRESULT_PACKETへ1行記録する(記録用)。
T-2: TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示(本委任はTTSを伴わない)。
T-3: 費用上限[Cap]は暴走防止のGuardrailであり、Cap到達=自動STOPではない。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_63.md`。委任文は全文そのまま保存。一時ファイルはリポジトリ外(`%TEMP%`配下)。報告用の`.md`をWriteツールが拒否する場合は、集計スクリプトからファイル出力する。

## ユーザー指示(原文、該当部分。全文は`DECISION_LOG.md`末尾の2026-10-04ユーザー決定[5回目])

5. 少数flowが問題なければ、29件横断を1回だけ実施。
   - 真の重大見逃し 0
   - 重大ケースの誤解放 0
   - 過剰Majorの状況
   - 不要Rewrite
   - Human Review増加有無
     を確認。
   - 費用目安 ¥35〜70。
6. そこでSTOPして報告。
   - 5記事 × Standard/Advanced = 10本の次Trialはまだ開始しない。
   - 次TrialはユーザーGO待ち。
今回の作業中に新しいProduct判断が必要になった場合は、追加Trialや仕様拡張へ進まず USER_DECISION_REQUIRED でSTOPしてください。

ユーザー決定[4回目](判断D)§6の確認項目も併せて集計: 説明文混入対策が誤範囲を選ばない / 句読点差対策が機能する / 英語だけ修正する方針が維持される / retry / recheckで仕様が崩れない。

## 作業1: 実行構成(rep24 全量)

- 実行スクリプト: `er052_open233_self_recovery_flow_runner_01_rep24_full_01.py`(委任_62の`..._rep23_limited_01.py`を複製し、instance集合を全量にする)。出力`er052_output/open233_self_recovery_flow_runner_01_rep24/`。
- スイッチ: rep23と同一(`HANDOFF_MODE=violation_span`、`VS_MATCH_EXT=True`、`VS_EXPLAIN_SPLIT=True`、`JA_MODE=english_only`、Stage 2 rubric=V7b[assert]、`FLOOR_VERIFY_MODE=time_only`、⑥OFF、`MAX_CYCLES=2`、`HARD_MAX_CYCLES=3`)。実測を`switches`で確認。
- instance集合とn: 直近の全量run=iteration 7(委任_22、29 instance・38 instance-run、¥39.5475)と同じinstance集合・同じn配分にする(比較可能性のため)。iteration 7の構成は`er052_output/`配下のiter7出力(Grep `iter7`/`iteration_7`)またはREPORT §(委任_22)から特定し、記録する。特定できない場合は29 instance × n=1。見込み費用(rep23実測の単価: Safety系¥0.5〜2.7、実記事¥0.05〜0.2、neg系¥1.0〜1.2)が¥70を超えるならn=1へ落として報告。
- 比較基準: (A)iteration 7(全量、旧構成)、(B)rep23(同構成、6 instance)。instance別に直近の記録も参照可。基準が旧rubric・旧スイッチである点は明記。

## 作業2: 実行(有料)

- 1回で全量を回す。instanceごとに完了後、即時STOP条件(JA変更/重大と思われる解放/Safety-critical残存/例外2 instance以上)を確認し、該当したら残りを止めて報告。
- 失敗runは再実行しない。

## 作業3: 集計(`summary_01.json` + `summary_01.md`、`release_log_01.md`、`blocking_claims_01.md`)

ユーザー確認項目:
1. 真の重大見逃し: Safety-critical 5件(B3、B4-a、A2A3-0、A4-0、A5-0)の検出状況(run別)、`residual_at_pass`の全件列挙と正式基準(重大=事実関係の重大な誤解/軽微/問題なし)による仮ラベル。
2. 重大ケースの誤解放: `floor_verify`の対象判定件数・CONFIRMED件数・確認call件数・解放件数・BLOCKING固定理由別件数・費用。解放全件(claim/Ledger逐語/`issue`/確認2回の`materiality`・`basis`・`ledger_citation`/最終値)に仮ラベル。
3. 過剰Majorの状況: Stage 2 BLOCKING件数、floor単独BLOCKING件数(フラグ別)、そのうち正式基準で軽微以下と思われる件数(仮ラベル、全件列挙)。iteration 7比・rep23比。
4. 不要Rewrite: 既存定義(正常記事群)の率と、全runでの「Rewrite実行件数/軽微以下と仮ラベルしたclaimのRewrite件数」の両方を示す(定義を1行で明記)。iteration 7比(iter7=21.43%[neg3 disputed除外で7%]、⑥使用7件、worst ¥8.95)。
5. Human Review増加有無: STAGE4_ESCALATION件数・理由別(`violation_span_unverified`/`unconfirmed_after_reverify`/`ladder_exhausted…`/`cycle_limit…`等)、instance別のiteration 7比。
判断D §6項目:
6. 説明文混入対策: `vs_explain_split`の試行件数・P採用件数・採用範囲全件(`claim_in_article`/断片/`dropped_remainders`/level)と誤範囲の有無(全件仮判定)。
7. 句読点差対策: L5/`label_only`の発火件数・成功件数、未確定(`mismatch`等)の理由別件数と代表例(委任_62のA2A3「`6 percent, …`」型の切断がほかにもあるか件数)。
8. 英語だけ修正: JA変更0/N、JA Rewrite 0、`en_title_rewritten`件数、`english_only_ja_source_requires_full_recheck`発火=全文Recheck実施の1対1。
9. retry/recheck整合: cycle 2・3到達run数、`severity_wobble`・`carry_forward_comparison`件数、Recheck由来claimが同じ経路(handoff/floor/floor_verify/2-of-2)を通ること、floor_verifyの解放がcycle間で引き継がれないこと(発火した場合)。
10. 費用: instance-run別・合計・worst・iteration 7比(¥39.5475)。
各項目に「PASS/注意/FAIL」の仮判定と根拠件数。FAIL定義は委任_62と同じ(1・2は1件でもFAIL、3・4は増えている、5は増えている、6は誤範囲1件、7は機能していない/誤解決、8はJA変更1件、9は仕様崩れ1件)。

## 作業4: SSOT・記録

- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §45「29件横断 rep24(委任_63)」(構成・結果表・仮判定・解放ログ要約・BLOCKING claim仮ラベル・費用・iteration 7比)。
- `OPEN_ITEMS.md` OPEN-233行Status: 「29件横断rep24実施(2026-10-04、委任_63、N instance-run、¥X): 項目別【PASS/注意/FAIL】。STOP(次TrialはユーザーGO待ち)。Closeout確認は委任_64。Production未接続」(旧Statusは「旧Status参考(委任_62)」で残す)。次Action欄末尾に「(委任_63)Fable照合→委任_64=Closeout確認(8項目)→ユーザーへSTOP報告(次TrialのGO判断待ち)」を追記。
- `docs/pm/REPORT_LEDGER.md` OPEN-233行の備考。`docs/pm/ACTIVE_TASK.md` Status=「IN_PROGRESS(rep24 29件横断完了、Fable照合待ち、次Trial禁止)」(addしない)。`CURRENT_SPEC.md`・`DECISION_LOG.md`は編集しない。

## 事前指定Read一覧

- `er052_open233_self_recovery_flow_runner_01_rep23_limited_01.py`、`er052_open233_self_recovery_flow_runner_01_rep23_agg_01.py`: 全文(複製元)。
- iteration 7の構成・結果: `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`をGrep `iteration 7`/`iter7`/`38 instance`/`委任_22` → 該当節のみ。iter7出力ディレクトリのsummary。
- rep23: `er052_output/open233_self_recovery_flow_runner_01_rep23/summary_01.json`、`release_log_01.md`。
- runner: Grep `switches`、`BODY_RUBRIC_DEFAULT`、`floor_verify_summarize`、`residual_at_pass`、`escalation_reason`、`SAFETY_CRITICAL_CLAIM_DEFS` → 該当範囲(全文Read禁止)。
- `OPEN_ITEMS.md`/`REPORT_LEDGER.md`/REPORT: Grep `委任_62` → 更新位置だけ。

## 事前指定Grep一覧+追記位置

- 上記のとおり。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`(0件を確認)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。PowerShellなら先に `$env:PYTHONIOENCODING="utf-8"`。

本実行(有料、1回のみ):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep24_full_01.py --stage main --budget-jpy 70

集計:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep24_full_01.py --stage agg
(引数名は複製元の実装に合わせてよい。)

テスト:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
(`budget_state_*.json`等の書き換えは`git checkout`で戻す。)

順序: T-0 → 作業1(構成特定・見込み費用) → 本実行 → 集計 → テスト → 作業4 → commit/push → 報告。

## Git(明示add対象・コミットメッセージ)

- SSOT編集権: `OPEN_ITEMS.md`の1行、`REPORT_LEDGER.md`の1行、REPORTの追記。`CURRENT_SPEC.md`/`DECISION_LOG.md`/`PM_GOVERNANCE.md`は編集しない。
- commit対象: 実行・集計スクリプト、`er052_output/open233_self_recovery_flow_runner_01_rep24/`配下、REPORT、`OPEN_ITEMS.md`、`REPORT_LEDGER.md`、委任ログ`_63.md`・`_check.json`。メッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 承認済み対策を全て有効にした29件横断rep24(N instance-run、¥X)を1回実施し項目別に集計【結果】、STOP(次TrialはユーザーGO待ち、Production未変更)(委任_63)`
- commit前に`git status --porcelain`で混入なしを確認。競合・失敗は自動解決せず報告。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`と最終メッセージに: (1)結論10行以内、(2)構成、(3)項目1〜10の結果表、(4)解放ログ全件、(5)`residual_at_pass`全件と仮ラベル、(6)説明文混入対策の採用範囲全件、(7)即時STOP条件の該当有無、(8)費用、(9)テスト、(10)SSOT更新箇所、(11)T-0・commit・push・raw URL、一覧外Read、確認できたことと推測の区別、(12)Fableへの論点。

(注: 本保存は委任文の主要部を保存したもの。T-0/T-2/T-3の定型文は要約表記を含む。)
