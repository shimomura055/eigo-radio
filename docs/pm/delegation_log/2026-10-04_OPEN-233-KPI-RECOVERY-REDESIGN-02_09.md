## 管理ID

`OPEN-233-KPI-RECOVERY-REDESIGN-02`(委任_09)。親: `OPEN-233-SELF-RECOVERY-TRIAL-01`。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: 委任_08で判明した「Checkerが`related_fact_id`を空で返すclaim(Safety系fixtureのBLOCKING claimの19.6%)に対し、AG1-strictのfail-closedがfaithfulなRewrite案を全拒否→ladder枯渇→Human Review」の是正(Fable判断、下記)を実装し、負例・差分0確認をやり直し、rep29a再確認(有料≈¥3)→Step 6再確認rep29(有料≈¥21)→KPI判定。
- KPI(変更・緩和禁止): Primary=USER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均追加+¥2/記事以内、Cap=+¥3/記事以内。QCD優先: 1重大見逃し0 2Human Review 0 3不要Rewriteを増やさない 4+¥2 5非決定性・追加call最小 6Production複雑化回避。
- 到達上限Status: Step 6のKPI判定まで。4つ同時達成→`VALIDATED`(Trial評価)。未達→`IN_PROGRESS`のままFableへ。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ進まない。既存の個別APPROVED項目のStatusも変更しない。
- Fable判断(SSOTへ逐語記録。変更しない):
  1. **`related_fact_id`が空のときはLedger全体を照合先にするfallback(AG1-ledger相当)を採用**。根拠: (ア)現行guardの設計意図(runner L562〜567、`ledger_text`全体との照合)は元々Ledger全体が照合先であり、AG1-strictの「関連factに限定」はそれより厳しい追加条件。fallbackは元の意図に戻すもので「緩める」ではない。(イ)`related_fact_id`空はCheckerの出力仕様上の欠落(Safety系で19.6%)であり、Checker出力変更は禁止のため後段で吸収する。(ウ)後ろ盾はStage 2 floor `changed_actor`とRecheck全文(構造要素の対渡し含む)。(エ)関連factが**ある**場合は従来どおりAG1-strict(関連fact優先、他factは2条件ANDのみ)で、別factの主体持ち込みの抑止は維持。
  2. 照合順: 新主体語ごとに (i)元文に同クラス → 許容 / (ii)関連factあり: 関連factに同クラス → 許容、無ければ(iii)2条件AND → 許容、どちらも不成立 → 拒否 / (ii′)関連fact空: Ledger全体(全fact本文、`notes_for_writer`含む)に同クラス表現が語境界付きで存在 → 許容(`basis=ledger_wide_fallback`を記録)、無ければ拒否。Ledgerにまったく無い主体は常に拒否(fail-closed)。
  3. 負例を追加: (f)`related_fact_id`空かつLedger全体にも無い主体 → 拒否、(g)`related_fact_id`空かつ近接クラス(Ledgerにcontractorはあるがemployeeは無い状況でemployeeを導入) → 拒否、(h)`related_fact_id`ありで他factにしか無い主体をissue名指しなしで導入 → 拒否(fallbackが発動しないこと)。既存(a)〜(e)も全て再実行。差分0確認(許容→拒否 0件)も再実施。
  4. Opus再レビューは本委任では行わない: Opus#13が評価したAG1-strict/AG1-ledgerの範囲内での条件分岐(関連factの有無で切替)であり、実測(19.6%欠落)に基づく「修正して採用」。Closeout時の条件Cレビューで一括確認。
  5. 委任_08の委任ログがOpus#13全文を要旨化していた点、T-0 FAIL(見出し語不足)は運用メモに記録(本委任では全文保存)。
- 禁止事項: Production正式path変更禁止(編集は`er052_open233_*`のみ)。Checker本体Prompt・Schema・判定規則・V7b不変。同義語表(`ACTOR_SYNONYM_CLASSES`、commit `f513695c`)は変更しない。新しいretry loop・Human Reviewへ倒す新経路を作らない。Step 6の母数・nは固定(29 instance・38 run)、再実行・n増しなし。採否基準を結果を見て変えない。`git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。`PM_GOVERNANCE.md`は編集しない。
- 費用上限: 上限¥30(Guardrail。内訳の目安: rep29a再確認[`safety_er009_changed_scope`×n=2、委任_08の再実行枠]≈¥3、rep29≈¥21)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計¥669.75、上限¥900、残¥230.25。有料実行前に費用概算を出し実測と並記。
- 即時STOP(有料run中): JA変更/例外2 instance以上/1 instance-run費用>¥7。重大見逃し・STAGE4は止めずに完走し、件数と原因を特定して報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_09.md`。**委任文は全文そのまま保存(要旨化不可)。** 一時ファイルはリポジトリ外。スクリプトはWrite/Editで作る。全体回帰は`PYTHONIOENCODING`なしのシェルで実行。10分制限で中断した場合は`skip existing`で1回だけ再開し記録。

## ユーザー指示(原文、該当部分。全文は`DECISION_LOG.md`末尾の`OPEN-233-KPI-RECOVERY-REDESIGN-02`)

````
Step 6
Safety-critical群＋既存29件を再確認。
ここで最低限、
- Human Review 0件
- 重大見逃し 0件
を同じ構成で同時に確認すること。
Step 7
まだ未達なら、自律的に原因分析→改善ループをもう一度回す。
合理的な改善余地が残っている限り、ユーザーへKPI緩和を提案しない。
````

## 作業1: 記録(¥0)

設計書`docs/pm/design_open233_kpi_recovery_02.md` §16「related_fact_id欠落時のLedger全体fallback(Fable判断、委任_09)」に上記判断1〜5を逐語で記録(現行guardの設計意図の行番号・引用を添える)。`docs/pm/open233_closeout_check_2026-10-04.md`末尾「運用メモ」に委任_08のT-0 FAILと委任ログ要旨化を追記。

## 作業2: 実装(runner)

- `actor_rewrite_guard_decision`に(ii′)fallbackを追加(Fable判断2)。記録`basis`に`ledger_wide_fallback`を追加。`legacy`不変。
- テスト: 負例(a)〜(h)各≥3ケース→全拒否、正例(rep28の6試行、rep29a s2の`passengers`[`related_fact_id`空・F-004に乗客])→許容、関連factありのとき他fact主体はissue名指しなしで拒否(fallback非発動)、`legacy`不変。runner単体・er052回帰・全体回帰(基準11件以外新規なし)。
- ¥0差分確認(`agg_actor_guard_diff_01.py`再実行): 許容→拒否0件、拒否済み試行の許容件数(rep28 6+rep29a s2の3水準)。

## 作業3: rep29a再確認(有料≈¥3)

`safety_er009_changed_scope`×n=2(委任_08の再実行枠)。出力は`rep29a`配下に`rerun_01/`。確認: STAGE4 0/見逃し0/actor_guard判定逐語(`ledger_wide_fallback`の発動)/Rewrite案がLedgerに沿うか(目視相当)/費用/JA 0。STAGE4が出たら原因を特定しFableへ(Step 6へ進まない)。

## 作業4: Step 6再確認 rep29(有料≈¥21、1回)

委任_08作成済み`er052_open233_self_recovery_flow_runner_01_rep29_full_01.py`/`_rep29_agg_01.py`(KPI構成: AG1-strict+fallback・件数一致修正・構造要素補強・N1′・因果floor known6+issue_actor・S1・L6・prior_issues現行本文・NORMAL群OFF・P+Q/U-2(1)・VS_MATCH_EXT・english_only・V7b・time_only)。29 instance・38 run。
- 集計(rep28・rep24・iter7比): Human Review(統一定義)件数・理由/重大見逃し(旧・新定義・`text_pattern`版、`residual_at_pass`全件仮ラベル)/Safety-critical 6件の検出・経路/各機構の発火(Tier 0・S1・L6・N1′・actor_guard判定[basis別]・構造要素・件数一致)/Recheck自己矛盾率・再確認call数(rep28比)/不要Rewrite/過剰Major/cycle分布/JA 0/費用(合計・平均追加/記事[rep24比・iter7比]・worst・Cap超)/モデル・構成。
- **KPI判定**: Human Review 0∧重大見逃し0∧平均追加≤+¥2∧worst追加≤+¥3 → `VALIDATED`。未達→原因分析をREPORTに書きFableへ。

## 作業5: SSOT

- `OPEN_ITEMS.md` KPI-RECOVERY-02行Status: 「委任_09: related_fact欠落時のLedger全体fallback実装(負例(a)〜(h)全拒否・差分0)、rep29a再確認【STAGE4 a】、rep29【Human Review d・見逃しe・不要Rewrite f・平均追加+¥g・worst+¥h】→【VALIDATED/未達】。次: 【Closeout(委任_10)/再ループ】」。`docs/pm/REPORT_LEDGER.md`、REPORT §59、`docs/pm/ACTIVE_TASK.md`(addしない)。`CURRENT_SPEC.md`・`DECISION_LOG.md`は編集しない。

## 事前指定Read一覧

- runner: Grep `actor_rewrite_guard_decision|actor_rewrite_guard_ok|ACTOR_SYNONYM_CLASSES|ACTOR_EN_COMPOUNDS|ledger_text|related_fact_hits|issue_named|ACTOR_GUARD_MODE|KPI_TRIAL_SWITCHES` → 該当範囲(全文Read禁止)。L560〜600の設計意図コメント。
- rep29a `safety_er009_changed_scope` s2 instance JSON(`actor_guard_decision`・Rewrite案・Ledger F-004)。
- `er052_output/open233_kpi_recovery_02_offline_01/agg_actor_guard_diff_01.py`(再実行)。rep29スクリプト(作成済み)。
- 設計書§15。SSOT: Grep `KPI-RECOVERY-REDESIGN-02`。

## 事前指定Grep一覧+追記位置

- 上記のとおり。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`(0件確認)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_09.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_09.md_check.json

テスト・回帰:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py

¥0差分: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_kpi_recovery_02_offline_01\agg_actor_guard_diff_01.py

rep29a再確認(有料):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep29a_affected_01.py --stage main --instances safety_er009_changed_scope --n 2 --out-subdir rerun_01 --budget-jpy 5
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep29a_affected_01.py --stage agg --out-subdir rerun_01

rep29(有料、1回):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep29_full_01.py --stage main --budget-jpy 24
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep29_full_01.py --stage agg
(引数名は実装に合わせてよい。)

順序: T-0 → 作業1 → 2(テスト・差分含む) → 1回目commit/push → 3 → [STAGE4 0なら]4 → 5 → 2回目commit/push → 報告。

## Git(明示add対象・コミットメッセージ)

- SSOT編集権: `OPEN_ITEMS.md`の1行、`REPORT_LEDGER.md`の1行、REPORT、`open233_closeout_check_2026-10-04.md`の運用メモ。
- 1回目commit: runner、テスト、設計書§16、closeout運用メモ、差分出力、委任ログ。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: actor_guardにrelated_fact欠落時のLedger全体fallback(元の設計意図への復帰)を実装、負例(a)〜(h)全拒否・差分0確認(委任_09)`
- 2回目commit: rep29a rerun・rep29出力、SSOT。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: rep29a再確認【STAGE4 a】・Step 6再確認rep29 29件+Safety-critical【Human Review d・見逃しe・不要Rewrite f・平均追加+¥g・worst+¥h】→【VALIDATED/未達】(委任_09)`

## 報告(RESULT_PACKET項目)

(1)結論10行以内(KPI 4つの実測値、VALIDATED/未達)、(2)実装・テスト・差分0・負例結果、(3)rep29a再確認結果(actor_guard判定逐語)、(4)rep29結果表(rep28/24/iter7比、Safety-critical 6件、機構発火[basis別]、自己矛盾率、費用、モデル・構成)、`residual_at_pass`全件仮ラベル、(5)未達なら原因分析と再ループ案、(6)費用(概算/実測/Phase累計)、(7)SSOT、(8)T-0・commit・push・raw URL、一覧外Read、確認/推測の区別、(9)Fableへの論点(Closeoutへ進めるか)。
