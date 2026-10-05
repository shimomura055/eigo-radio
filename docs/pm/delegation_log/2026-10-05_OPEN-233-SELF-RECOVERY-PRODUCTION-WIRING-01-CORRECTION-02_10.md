# 委任_10 OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-02(全文保存、part1)

## 管理ID

`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-02`(委任_10、親 `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`)。並行タスクなし。

## 性質/禁止事項

- 性質: ¥0・記録と既存データのオフライン集計のみ(有料APIなし、コード変更なし)。委任_08のA構成fresh限定確認が事前固定受入条件(1)(2)(3)でFAIL、§6調査で復元差なし(prompt sha 26/26一致、model同一)=「同一構成でもrun間の揺れが大きく、frozen出力の検出能力はfreshで再現しない」ため、ユーザー是正指示02 §1「Safety-criticalを再現できない/rep30と大きく異なる検出傾向」に該当。FableはSTOPし`USER_DECISION_REQUIRED`候補として報告する。本委任はそのStatus記録と、ユーザー判断の材料となる**事実の影響分析(¥0)**を行う。
- Fable判断(逐語記録): 「A構成の復元は正確(sha 26/26)であり、FAILの主因は復元差ではなくStage 1 Checkerのrun間変動(非決定性)である。rep30のStage 1入力は『frozen V4A出力(単発サンプル)+Safety-critical見逃し時のV0差替え』で構成されており、同一構成のfresh実行では再現されない。したがってrep30のVALIDATEDはStage 1出力を所与とした後段の検証に限られ、Production初回pathのStage 1はrep30の忠実な再現としては成立しない。是正指示§6『それでも成立しない場合のみSTOPし報告』に該当。Fable/Claudeは新Checker仕様を新設・選定しない。ユーザー判断事項として、事実と影響(既存データからの¥0推定)を提示する。委任_08費用¥11.42(Guardrail¥10超過、暴走ではない)を記録。」
- 禁止: 有料API禁止。コード変更禁止。`CURRENT_SPEC.md`/`PM_GOVERNANCE.md`編集禁止。`DECISION_LOG.md`はFable判断3〜6行のみ。`git add -A`/`stash`/`amend`禁止。既存M差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。1回の書き込みは2,500文字以下。
- T-0: 委任ログ(本ファイル)に全文保存(分割)、check実行・結果記録。
- 固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## 作業

1. T-0。
2. **¥0影響分析**(スクリプト`er052_output/open233_kpi_recovery_02_offline_01/agg_stage1_variance_impact_01.py`、出力json/md): 既存データのみ使用 — A構成fresh(`er052_output/open233_stage1_phase1_recall_check_01/a_frozen_fresh_01/`、n=2、A4はn=4)、frozen記録(rep30が使った出力)、V0記録(Production記録n=1、委任_04cで使ったもの)。計算: (a)Safety-critical 6 claim(B3・B4-a・A2A3-0・A4-0・A5-0・neg5 B3-same)+B2_hormuz HF-011について、「A単発」「A 2回の和集合(run1∪run2)」「A単発∪V0記録」「frozen(rep30実使用)」の各検出有無の表。(b)負例/NORMAL群の各方式でのMAJOR誤検出率(和集合では誤検出も増える点を数値で)。(c)各方式の1記事あたりStage 1追加費用の推定(A 1 call実測平均¥0.34、V0@gpt-5.6-luna 1 call実測¥0.728[委任_05 cell_cand_56lunaは候補prompt。V0@5.6の実測call単価が無ければ委任_04c/05の単価から推定と明記])。(d)これらは**ユーザー判断の材料**であり、採用提案ではないことをmdの冒頭に明記。

# part2

3. **記録**: `DECISION_LOG.md`末尾に見出し「## 2026-10-05 Fable判断 CORRECTION-02 fresh確認FAIL→STOP(OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01)」+上記Fable判断(逐語)+影響分析のパス。`docs/pm/ACTIVE_TASK.md`: ヘッダStatus=`USER_DECISION_REQUIRED`(タスクStatus。仕様Statusは`APPROVED_FOR_PRODUCTION`維持と明記)、Fable判断、委任_08の受入条件表の要約、影響分析の要点、ユーザー判断事項: 「Production初回pathのStage 1をどう成立させるか(rep30の忠実再現が不成立のため)」。addしない。`OPEN_ITEMS.md`該当行Status→「APPROVED_FOR_PRODUCTION(配線STOP: A構成fresh確認FAIL[SC 4/5・neg5 B3-same 0/2・A4-0 2/4]、復元差なし=Stage 1非決定性。USER_DECISION_REQUIRED候補)」。`docs/pm/production_wiring_report_open233_01.md` §3にfresh確認結果(委任_08)と§11に未解決追記。`REPORT_LEDGER.md`1行。
4. commit/push(明示add: DECISION_LOG、OPEN_ITEMS、wiring report、REPORT_LEDGER、スクリプト・出力、委任ログ+check.json)。メッセージ: `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-02: A構成fresh確認FAIL(復元差なし・Stage 1非決定性)によりSTOP、影響分析(¥0)を記録、USER_DECISION_REQUIRED候補(委任_10)`

## 事前指定Read一覧

`a_frozen_fresh_01/agg_a_frozen.json`、各run json(Pythonで一括)、`agg_phase1.json`(V0記録の所在)、frozen記録はprovenance文書§2の表(Read)と`er051_output`該当run(Pythonで一括)。`docs/pm/production_wiring_report_open233_01.md` §3/§11見出し。

## 事前指定Grep一覧+追記位置・更新位置の手順

DECISION_LOG末尾。OPEN_ITEMS `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`行。wiring report `^## 3`/`^## 11`。REPORT_LEDGER末尾。ACTIVE_TASKヘッダ。

## 実行コマンド全文

T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-02_10.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-02_10.md_check.json
集計: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_kpi_recovery_02_offline_01\agg_stage1_variance_impact_01.py
Git: `git status --porcelain`→明示add→commit→`git push origin main`→`git log --oneline -1`

## 報告(短く)

(1)影響分析表(a)(b)(c)の要点8行以内、(2)SSOT更新・T-0・commit・push・raw URL(影響分析md/OPEN_ITEMS)、(3)確認/推測の区別。
