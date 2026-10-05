# 委任_01 OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01(2026-10-05、Fable→Sonnet)

## 管理ID

`OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`(委任_01)。関連: `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`(配線STOP中、後段は`APPROVED_FOR_PRODUCTION`維持)。並行タスクあり: 委任_02(PM Failure RCA、新規文書`docs/pm/pm_rca_open233_stage1_closeout_01.md`のみ作成、git操作なし)。本委任はその文書に触れない。

## 性質/到達Status/禁止事項

- 性質: ¥0・記録と技術RCAのみ(有料APIなし、コード変更なし)。(a)ユーザー指示(下記原文)をDECISION_LOGへ逐語記録(スクリプト転写)、新管理IDのACTIVE_TASK/OPEN_ITEMS行作成、(b)Stage 1 Checkerの技術RCA(ユーザー§3): 既存Evidenceを整理し、非決定性と設計問題を分離する。Prompt修正・設計案の確定は本委任で行わない(次委任で設計→Opus)。
- 到達Status: Trial管理ID、最大`VALIDATED`。本委任は`IN_PROGRESS`。Production配線しない。後段`APPROVED_FOR_PRODUCTION`と混同しない。
- 禁止: Production・Trialコード変更禁止。有料API禁止。Safety-criticalの定義・gold・母数の変更禁止。「LLMは揺れるから仕方ない」を結論にしない。`CURRENT_SPEC.md`/`PM_GOVERNANCE.md`編集禁止。`git add -A`/`stash`/`amend`禁止。既存M差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。1回の書き込みは2,500文字以下。
- T-0: 本ログに全文保存(分割)、check実行・結果記録。ユーザー指示原文は本ログの4連バッククォートブロックが転写元。
- 固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## 作業(要約)

1. T-0(分割保存)→check。
2. 記録: DECISION_LOG.md末尾に見出し「## 2026-10-05 ユーザー指示 OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01(Stage 1 Checker再検証・改善Trial+PM Failure RCA)」+原文逐語(スクリプト転写)+Fable判断3行(Trial管理IDとして開始。最大VALIDATED。改善ループ3回Cap。E2E KPIはfresh Stage 1必須、条件付き評価と分離。PM RCAは委任_02で並行。Production配線はSTOP維持、後段APPROVED_FOR_PRODUCTIONは不変。残予算約¥138を前提に¥0分析→小規模→E2Eの順)。OPEN_ITEMS.md新行(IN_PROGRESS、ループ0/3、KPI欄、次工程)。ACTIVE_TASK.md新ヘッダ(addしない)。
3. Stage 1技術RCA(新規`docs/pm/rca_open233_stage1_checker_01.md`): 既存Evidenceのみ(Grep→範囲Read)。各項目に出典パス・行番号・確認/推測。(1)V4A採用経緯 (2)既観測の見逃し(85%等) (3)frozen/reuse/V0差替え導入理由 (4)fresh再現失敗(A4-0 2/4、neg5 B3-same 0/2、B2_hormuz HF-011 0/2、B4非SC 4件0/2)の原因候補(i)非決定性(ii)Prompt(iii)入力(iv)schema(v)candidate generation(vi)deterministic処理欠如(vii)役割分担を支持/不支持/未確定で判定 (5)単発LLM Checker設計の妥当性と設計案比較論点(確定しない) (6)既存資産棚卸し (7)E2E評価設計要件・費用見込み(残予算約¥138)。
4. docs/pm/REPORT_LEDGER.md 1行。
5. commit/push(明示add: DECISION_LOG、OPEN_ITEMS、RCA文書、REPORT_LEDGER、委任ログ+check.json)。メッセージ: `OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01: ユーザー指示を逐語記録、Stage 1 Checker技術RCA(非決定性と設計問題の分離、既存資産棚卸し、E2E評価要件)(委任_01、¥0)`

## 事前指定Read

runner: Grep `substitute_baseline_on_stage1_miss|def run_stage1|stage1_fresh_with_enumeration|ACCEPTABLE_STAGE1|causal_floor_guard|SAFETY_CRITICAL_CLAIM_DEFS|expand_same_fact_id_locations`。er051: Grep `V4A|RELATED_FACT_ID_INSTRUCTION|developer|schema`。er050: ヘッダ+Grep。Opus#10 `docs/pm/opus_l2_review_open233_self_recovery_10.md`。`docs/pm/rep30_stage1_provenance_01.md`。`agg_stage1_variance_impact_01.md`、`agg_a_frozen.json`。

## 報告形式

(1)結論10行以内 (2)原因候補(i)〜(vii)支持/不支持表 (3)E2E評価要件と費用見込み (4)SSOT・T-0・commit・push・raw URL、一覧外Read、確認/推測 (5)Fableへの論点(次委任=設計案比較+Opus packetに必要な決定事項)。

## ユーザー指示(原文、全文。DECISION_LOGへ逐語記録)

````
Claude Code 指示
管理ID：OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01
目的
OPEN-233で未解決となっている Stage 1 Checker（最初に重大なFact問題を検出する入口）を直ちに再検証・改善する。
今回の問題は、rep30で後段Self-Recoveryは十分検証した一方、Stage 1の重大問題検出がfresh Production相当で安定していなかったこと。
既存Checkerへの小修正ありきにしない。
現設計でKPIを満たせないなら、Stage 1の役割・構造・判定方式から根本的にやり直してよい。
ただし今回はTrialであり、Productionコードへ新仕様を勝手に配線しない。
1. 正式KPI
前回と同じ以下3点を維持する。緩和しない。
Primary KPI
USER_DECISION_REQUIRED / Human Review：0件
Safety KPI
重大Fact見逃し：0件
Cost KPI
平均追加費用：+¥2 / 記事以内
補足：
- 単発runが¥3を超えた場合は必ず報告・記録する。
- 単発¥3超だけを理由にFAILとはしない。
- 平均費用を主要KPIとする。
2. Checker改善の基本原則
重大な問題に対してCheckerを甘くすることは禁止。
重大な問題を拾わなくすればSafety KPI「重大Fact見逃し0件」を達成できない。
一方、
- 軽微
- 問題なし
- 自然な推論
- 過剰検出
を必要以上にMAJOR扱いしないよう改善することは可。
目標は、
重大な問題は確実に拾う。重大でないものへの過剰検出はできるだけ減らす。

である。
Safety KPIを良く見せるために、Safety-criticalの定義・gold・母数を都合よく変更してはならない。
既存ユーザー判断による重大/軽微/問題なしの線引きを正本とする。
3. まずRCAを行う
いきなりPrompt修正を始めない。
まず、Stage 1についてこれまでのEvidenceを整理し、
- 以前V4Aが良好に見えた理由
- n=20で85%などの見逃しが既に観測されていたこと
- rep30でfrozen/reuse/V0差替えを行った理由
- なぜfresh Stage 1の未解決問題を残したままrep30 Closeoutできたのか
- 今回fresh復元でA4 / neg5 / Hormuz等が再現できなかった原因候補
- 単純なLLM非決定性なのか
- Prompt / 入力 / schema / candidate generation / deterministic処理 / 役割分担の設計問題なのか
を分離する。
「LLMは揺れるから仕方ない」で終わらせない。
重大Fact見逃し0を現実的に達成するために、LLM単発Checkerだけに依存する設計自体が適切かも含めて見直すこと。
4. 根本設計も検討対象
RCAの結果、単一Checker callの改善だけではKPI達成が難しい場合は、より根本的な方式を検討してよい。
例として、
- deterministicな候補抽出との役割分担
- 重大カテゴリごとの機械的pre-check
- 複数候補を漏れなくStage 2へ渡す構造
- Stage 1の複数回実行・和集合
- 最終PASS前の安全確認
- 既存Checkerと補完層の役割分担
等は検討対象になり得る。
ただし上記をそのまま採用せよという意味ではない。
QCD・単純性・既存資産再利用・非決定性・Production運用性を比較して、最も合理的な構造を設計すること。
5. Opusレビュー
今回は以下に該当するため、必要なタイミングでOpus独立レビューを必須とする。
- Stage 1構造変更の可能性が高い
- Safety判定に関わる
- 過去に同じ問題へ複数回改善している
- Production採用候補になり得る重要変更
Opusには追認させず、最低限以下を問うこと。
- 単一Checker方式を維持する必要があるか
- より単純で堅牢な方法はないか
- 重大見逃し0に対して構造的な穴がないか
- 過剰検出・Rewrite・Human Review・費用を増やしすぎないか
- deterministic / LLMの責務分担は適切か
- retry / fallback / regenerationを含めProductionで成立するか
- Stage 1だけでなくE2E KPIとして成立するか
6. 改善ループ
既存PMルールどおり、最大3ループまで自律的に改善してよい。
1ループは最低限、
RCA / 設計 → 必要なOpusレビュー → Fable評価 → 実装 → 限定Trial → KPI評価
とする。
KPI未達なら原因を分析し、次ループへ進んでよい。
単なるPrompt文言変更を惰性的に3回繰り返すのは禁止。
根本原因が構造なら構造を直す。
4回目以降
4回目が必要になった時点でSTOP。
以下をユーザーへ報告すること。
- 3ループまでの結果
- 現在どのKPIが未達か
- 根本原因
- 次のTrialで何を変えるか
- なぜ改善が期待できるか
- 想定費用
明示的なユーザー指示なしに4回目へ進まない。
5回目以降も毎回同様にユーザーGateを必要とする。
7. Trialの評価方法
今回はfresh Stage 1を含むE2E評価を必須とする。
以下を混同しない。
A. 条件付き評価
Stage 1出力をfrozen / reuse / 手動差替えした後段評価
B. E2E評価
fresh Stage 1から最終結果までProduction相当で通した評価
正式KPI判定は B で行う。
frozen / reuse / 手動差替えを使ったrunをE2E Safety KPIの分母へ入れない。
後段単体確認として使う場合は「条件付き」と明示すること。
8. Safety検証
既存のSafety-critical / Majorパターンを使用し、少なくとも、
- 主体取り違え
- 数字
- 否定
- 比較・方向
- 時期
- 因果の創作
- 相手方取り違え
- neg5 / B3-same
- Hormuz等の既知実例
を含める。
既存goldの変更が必要に見える場合、KPI達成のために変更してはいけない。
ユーザー承認済みmateriality基準と明確に矛盾する場合のみ、STOPして報告すること。
9. Cost / Productivityも同時に見る
重大見逃し0だけを達成して、全記事を大量MAJOR扱いする方式も成功ではない。
以下も測る。
- 正常/負例へのMAJOR誤検出
- Stage 2発動率
- Rewrite率
- cycle数
- Human Review / USER_DECISION_REQUIRED
- 平均追加費用
- worst run
- runtime
ただし、Safety KPIを過剰検出削減のために緩めない。
10. PM運営FailureのRCA
Checker技術改善と並行して、今回のPM Failureを別軸でRCAする。
最低限、以下を答えること。
1. Opus #10が「Stage 1 recallが支配的リスク」と警告していたのに、なぜrep30 Closeoutでblocking issueとして扱われなかったか。
2. Opusは「条件付きSafety値」と「代替なしE2E値」を分けるよう指摘していたが、実際にどう処理されたか。
3. Fable自身もその指摘を採用していたのに、なぜ最終KPI報告へ反映されなかったか。
4. Stage 1 recallはOPEN_ITEMS / ACTIVE TASK / KPI Gateのどこで管理され、どこで脱落したか。
5. 誰がnon-blocking / deferredと判断したのか。明示判断が無ければ、なぜ自然消滅したのか。
6. rep30の「重大Fact見逃し0」を算出するとき、なぜfrozen / V0差替えを含む条件付き評価だと検出できなかったか。
7. Trial closeoutで、Production初回pathを本当に通しているかをなぜ確認できなかったか。
8. Opusの警告を「レビュー済み」で終わらせず、Closeoutまで追跡する仕組みがなぜ働かなかったか。
責任追及ではなく、同種事故を防ぐためのプロセスRCAとする。
11. 再発防止
RCA後、最低限以下を正式PMルールへ反映する案を作り、Fableが評価すること。
A. KPI provenance
各KPIについて必ず、
- fresh
- frozen
- reuse
- manual substitution
- synthetic
- Production formal path
のどれで測ったかを記録する。
B. 条件付きKPIとE2E KPIの分離
固定入力や差替えが1件でも含まれる場合、
E2E Safety KPI
と呼ばない。
C. Opus指摘トレーサビリティ
重要なOpus警告は、
Opus指摘 → Fable採否 → 実装/Trial反映 → 検証Evidence → Closeout確認
まで追跡する。
未解決のBLOCKER / MAJOR / Safety警告がある状態でCloseout禁止。
D. Closeout自己確認
Trial終了時に必ず、
このKPIはfresh Production初回pathを含むE2E値か？

を明示的にYes/No判定する。
NoならE2E達成扱い禁止。
E. Open Item消失防止
Stage 1 recallのようなSafety未解決項目を、ユーザー合意なしにnon-blocking / deferred化しない。
12. Status
今回のStage 1新設計・改善は新しいTrialである。
Trial終了時に必ず、
- REJECTED
- VALIDATED
- USER_DECISION_REQUIRED
のいずれかへ分類する。
KPIを満たしても、自動的にProduction採用しない。
今回到達してよい最大Statusは、
VALIDATED
まで。
Production正式採用は、その結果をユーザーへ報告し、ユーザーが正式採用を判断した後。
既存の後段Self-Recoveryの APPROVED_FOR_PRODUCTION Statusとは混同しない。
13. 費用・作業方針
無駄な大規模Trialを先に行わない。
各ループとも、
¥0分析 → 小規模Safety/normal確認 → KPI見込み確認 → 必要なら広いE2E
の順で進める。
既存Evidenceは積極的に再利用するが、E2E KPI確認時はfresh runを使う。
単発¥3超は報告する。
14. STOP条件
以下のみSTOPして報告する。
- 3ループ終了してもKPI未達
- 4回目の改善が必要
- ユーザー承認済みmaterialityを変更する必要がある
- Safety KPIと他KPIが構造的に両立しない可能性
- Production仕様変更の正式採用判断が必要
- 想定外の大規模API発火
- 既存承認仕様との重大な衝突
通常の技術的修正・テスト・RCAはユーザーへ戻さず自律的に進めること。
今回のゴールは、「後段だけ良い」ではなく、fresh Stage 1から最終出口まで通したE2Eで3 KPIを満たす構成をVALIDATEDすること。
````

## 事前指定Grep一覧+追記位置・更新位置の手順

DECISION_LOG末尾(スクリプト転写)。OPEN_ITEMS: 既存`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`行の直後に新行。REPORT_LEDGER末尾。

## 実行コマンド全文

T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_01.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_01.md_check.json
転写: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\append_decision_log_from_sources_01.py --dry-run --block T:<見出し> --block F:<本ログ>@^````$@... → 本実行。

## Git(明示add対象・コミットメッセージ・trailer)

`git status --porcelain`→明示add(DECISION_LOG、OPEN_ITEMS、RCA文書、REPORT_LEDGER、本ログ+check.json)→commit(メッセージは作業5、trailer: Co-Authored-By: Claude Sonnet 5.5)→`git push origin main`→`git log --oneline -1`。
