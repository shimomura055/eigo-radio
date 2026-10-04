## 管理ID

`OPEN-233-KPI-RECOVERY-REDESIGN-02`(委任_07)。親: `OPEN-233-SELF-RECOVERY-TRIAL-01`。並行タスクなし。¥0(API課金なし)。

## 性質/到達上限Status/禁止事項

- 性質: Step 7再ループ3回目の前半。rep28(委任_06)でSafety 0・Cost達成・**Human Review 3件**(全てStage 3 Rewrite側: `actor_guard_rejected`によるladder枯渇2件[`safety_er009_changed_scope` s1・`meta_run03_advanced` s2]、title単独claimの決定論deleteによる`degenerate_rewrite_output` 1件[`safety_er009_unsupported_new_claim` s1])と、新発見のバグ(Recheckの`all_prior_issues_resolved`が**件数一致**で判定され、Checkerが1 prior issueに対し2項目[同index]を返すだけで自己矛盾→再確認callが毎回発生)について、(a)¥0 RCA、(b)技術是正の実装(件数一致バグ・title delete)、(c)`actor_guard`の是正設計(Safety guardの変更のためOpus批判レビュー前提、実装しない)、(d)Opus packet。有料runは次委任。
- KPI(変更・緩和禁止): Primary=USER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均追加+¥2/記事以内、Cap=+¥3/記事以内。QCD優先: 1重大見逃し0 2Human Review 0 3不要Rewriteを増やさない 4+¥2 5非決定性・追加call最小 6Production複雑化回避。
- 到達上限Status: `IN_PROGRESS`のまま。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ進まない。
- Fableの事前判断(SSOTへ記録。変更しない):
  1. **件数一致バグは実装バグ(技術是正)**: `all_prior = (len(resolved)==len(prior_issues)) and all(resolved)`は、Checkerが1 prior issueを複数項目(同`index`)に分けて返した場合に誤って`False`になる。是正: `index`でグループ化し、全prior issueのindexが揃い、各グループが全てresolved=trueなら`True`。indexが欠けたprior issueは`False`(安全側)。Checkerの判定規則は変えない(応答の集約方法の是正)。er003 vfl01 826行に同じ式があることは`OPEN-233-A1-PROD`に配線時の整合項目として記録(Production変更はしない)。
  2. **title単独claimの決定論deleteは技術是正**: タイトル・In one line等の構造要素を空にするdeleteは常に劣化。ladderで構造要素が対象のときはdeleteを選ばず、E1(語句)→③(文)の書き換えを使う(hintはChecker issue+Ledger notesから)。構造要素の書き換えでも`degenerate`になる場合の扱いは設計で明示(Human Reviewへ倒さない: 構造要素はLedgerの`headline`/`in_one_line`相当のfactがあればそれに沿って再生成、なければ段落水準①→③→④の既存ladderで文として書き換え)。
  3. **`actor_guard`はSafety guard**(Rewriteが主体を変える・増やすことを防ぐ)。過剰拒否の是正は「緩める」方向になりうるため、¥0集計で過剰拒否率と拒否された案の妥当性を確認し、設計案を比較してOpus批判レビュー(条件A)を経てから実装する。方向性: Ledgerの関連factに存在する主体(actor)への言い換え・追加は許容、Ledgerに無い主体は拒否(=Ledger照合に基づく決定論)。Checkerの`issue`が主体の修正を求めている場合(例: 「credit-card users」への限定)はその主体を許容。
- 禁止事項: Production正式path変更禁止(編集は`er052_open233_*`のみ)。Checker本体Prompt・Schema・判定規則・V7b不変。`actor_guard`の緩和は実装しない(設計のみ)。新しいretry loopを作らない。`git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。`PM_GOVERNANCE.md`は編集しない。
- 費用上限: ¥0。Phase累計¥667.19、上限¥900、残¥232.81。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_07.md`。**委任文は全文そのまま保存。** 一時ファイルはリポジトリ外。スクリプトはWrite/Editで作る。全体回帰は`PYTHONIOENCODING`なしのシェルで実行。

## ユーザー指示(原文、該当部分)

````
Step 7
まだ未達なら、自律的に原因分析→改善ループをもう一度回す。
合理的な改善余地が残っている限り、ユーザーへKPI緩和を提案しない。
(略)
以下はUSER_DECISION_REQUIREDではありません。
- 実装バグ
(略)
- 後段の判定ロジックにSafety holeがある
- Opusが改善案を出した
````

## 作業1: RCA(¥0、設計書`docs/pm/design_open233_kpi_recovery_02.md` §14)

- 1-1 `actor_guard`: runnerの実装(Grep `actor_guard|actor_guard_rejected|_extract_actors|ACTOR`)を行番号付きで整理(何を主体とみなすか、何と比較して拒否するか[元文/記事/Ledger]、拒否条件)。全ログ(`er052_output/open233_self_recovery_flow_runner_01_*`)の`rewrite_records`から`actor_guard_rejected`の全件を抽出し、(ア)拒否された書き換え案、(イ)元文、(ウ)Checkerの`issue`、(エ)関連Ledger fact(主体の記載)、を並べて、「拒否が正当(Ledgerに無い主体の導入)/過剰(Ledgerにある主体への限定・言い換え/Checkerが求めた修正)」を1件ずつ仮ラベル。過剰拒否率、過剰拒否→ladder枯渇→STAGE4になった件数。rep28の2件(`changed_scope` s1「credit-card users」、`meta_run03_advanced` s2)は逐語で。
- 1-2 title delete: `degenerate_rewrite_output`の全件(旧ログ含む)と、ladderがdeleteを選ぶ条件(Grep `delete|degenerate|structural|headline|title`)。rep28 `unsupported_new_claim` s1の逐語(claim=タイトル行、Ledgerの該当fact、delete後の本文)。
- 1-3 件数一致バグ: 全ログのRecheck応答で「`prior_issues`件数≠返却項目数」の発生件数・instance別、そのうち全項目resolved=trueだったのに`all_prior=False`になった件数(=偽の自己矛盾)、それが再確認callを発生させた件数と費用(推定)。neg3/neg2の恒常的自己矛盾(23/28・7/8)がこの機序で説明できる割合。
- 1-4 rep28の`remains_in_final_en` 3件(B3 s1・s2、neg5 s1)の中身を逐語で確認し、「目印文字列の部分一致残存(委任_63のB3 s1と同型: 因果`so`は修正済み)」か「実際に未修正」かを判定。

## 作業2: 技術是正の実装(runner、KPI構成でON)

- 2-1 件数一致バグ: `aggregate_prior_issues_resolved(prior_issues, items)`(index別グループ化、Fable事前判断1)。既存式を置換(スイッチ不要=バグ修正。ただし旧挙動のテストは更新し、変更理由をテスト名に残す)。記録: `prior_issues_resolved_by_index`。
- 2-2 title delete: ladderで対象範囲が構造要素(タイトル行・`## In one line`直下行・見出し)のときdeleteを選択肢から外し、E1→③で書き換える。書き換え案が空・劣化(`degenerate`)なら、Ledgerの`headline`/`in_one_line`相当factがあればそれに沿った再生成(既存のRewrite promptで範囲=構造要素、hint=Ledger fact)を1回、なければ④段落水準の既存ladderへ。Human Reviewへ倒す新経路なし。記録: `structural_element_rewrite`。
- テスト: 2-1(件数不一致で全true→True/index欠落→False/同index複数→グループ判定/旧式との差分)、2-2(構造要素のdelete禁止・書き換え・fallback)、OFF不変、全体回帰(基準11件以外新規なし)。
- ¥0 replay: rep28 `unsupported_new_claim` s1の記録でdeleteが選ばれないこと、neg3のrep28 Recheck応答(2項目・同index)で`all_prior=True`になることを決定論replayで確認。

## 作業3: `actor_guard`是正の設計(実装しない、§14-3)

- 案AG1: Ledger照合型 — 書き換え案に現れる主体が、(i)元文の主体、(ii)関連fact(`related_fact_id`)および同Ledger内のfactに記載の主体、(iii)Checker `issue`/`explanation`が名指しした主体、のいずれかに(正規化後に)一致すれば許容。それ以外の新主体は拒否。
- 案AG2: 現行guard維持+拒否時のhint強化(「主体を変えずに書き換える」を明示)で再試行(追加call 1回)。
- 案AG3: 拒否時にladder段を進めず、同段で1回だけ別案を求める(追加call 1回)。
- 比較: 1-1の全件に対する「正当拒否を維持/過剰拒否を解消」の件数(¥0 replay可能な決定論部分)、Safety(Ledgerに無い主体の導入を防げるか、Stage 2 floor `changed_actor`とRecheckが後ろ盾になるか)、不要Rewrite、追加call・費用、非決定性、Production配線。推奨案。

## 作業4: Opus packet

`docs/pm/opus_packet_open233_kpi_recovery_02_03.md`(雛形、条件A、独立レビューブロック逐語、2万字以内)。論点: 1.`actor_guard`の過剰拒否のRCAと案AG1〜AG3(Safety guardを緩めずにHuman Reviewを0にできるか、Ledger照合の決定論性、後ろ盾[floor changed_actor・Recheck]の妥当性) 2.title/構造要素の書き換えfallback(Human Reviewへ逃げていないか、劣化を防げるか) 3.件数一致バグ是正の安全性(index欠落の扱い) 4.`remains_in_final_en`の判定 5.より単純な方法 6.Production整合(er003 826行の同一式、er010のactor guard相当の有無)。

## 作業5: SSOT

- `OPEN_ITEMS.md` KPI-RECOVERY-02行Status: 「委任_07: rep28 Human Review 3件のRCA(actor_guard過剰拒否2・title delete劣化1)+件数一致バグ(偽の自己矛盾)の是正実装、actor_guard設計AG1〜AG3、Opus#13 packet。次: Opus#13→Fable→委任_08=実装+影響instance再確認+29件再確認」。`OPEN-233-A1-PROD`行に「er003 vfl01 826行の件数一致式の整合」を追加。`docs/pm/REPORT_LEDGER.md`、REPORT §57、`docs/pm/ACTIVE_TASK.md`(addしない)。

## 事前指定Read一覧

- runner: Grep(上記)+`rewrite_ranges_ladder|E1_RANGES|degenerate_rewrite_output|structural|all_prior_issues_resolved|prior_issues_resolved|resolved\)==len` → 該当範囲(全文Read禁止)。
- rep28 instance JSON: `safety_er009_changed_scope` s1、`safety_er009_unsupported_new_claim` s1、`meta_run03_advanced` s2、`neg3` s1/s2、B3 s1/s2、neg5 s1(Pythonで該当フィールド抽出)。全ログ走査はPython。
- `er003_v1_en_direct_vfl_01_generate.py` 820〜830(件数一致式、read-only)。`er010_ledger_local_rewrite_09.py` Grep `actor`(read-only)。
- Ledger: 該当factの主体記載(Grep)。
- テンプレート: `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`、`OPUS_INDEPENDENT_REVIEW_BLOCK.md`。
- SSOT: Grep `KPI-RECOVERY-REDESIGN-02`、`OPEN-233-A1-PROD` → 更新位置。

## 事前指定Grep一覧+追記位置

- 上記のとおり。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`(0件確認)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_07.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_07.md_check.json

テスト・回帰:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py

¥0集計・replay: `er052_output/open233_kpi_recovery_02_offline_01/agg_actor_guard_01.py`、`agg_prior_count_mismatch_01.py`、`replay_title_delete_01.py`(新規)。

順序: T-0 → 作業1 → 2(テスト・replay含む) → 1回目commit/push → 3 → 4 → 5 → 2回目commit/push → 報告。

## Git(明示add対象・コミットメッセージ)

- SSOT編集権: `OPEN_ITEMS.md`の2行、`REPORT_LEDGER.md`の1行、REPORT。
- 1回目commit: runner、テスト、集計・replay、設計書§14-1/14-2、委任ログ。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: rep28 Human Review 3件のRCA、Recheck解消判定の件数一致バグ(偽の自己矛盾→再確認call毎回発生)をindex別集約へ是正、構造要素(タイトル等)のdelete禁止と書き換えfallbackを実装(Production未変更)(委任_07)`
- 2回目commit: 設計書§14-3、packet、SSOT。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: actor_guard過剰拒否の全件集計と是正設計AG1〜AG3、Opus#13向けpacket(委任_07)`

## 報告(RESULT_PACKET項目)

(1)結論10行以内、(2)RCA(actor_guard全件の正当/過剰の集計表と逐語2件、title delete、件数一致バグの発生件数・偽自己矛盾件数・推定費用、remains_in_final_en 3件の判定)、(3)技術是正の実装箇所・テスト・replay、(4)案AG1〜AG3比較表と推奨、(5)packet文字数、(6)SSOT、(7)T-0・commit・push・raw URL、一覧外Read、確認/推測の区別、(8)Fableへの論点。
