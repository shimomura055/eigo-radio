# 委任文(全文保存) FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_04b (2026-10-08)

## 管理ID

FACTLOCK-WRITER-REDESIGN-TRIAL-01(委任_04b: sweep 変種追加・smoke・生成・照合・文体指標。**LLM評価は委任_04cで別途**)。並行タスクあり: `PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01`委任_03(Production配線・git commit中)、同管理ID委任_05(残NG突合、`eval/residual_analysis/`)。本委任はそれらのファイルに書き込まない。**git操作禁止・SSOT編集禁止**。

## 性質/到達上限Status/禁止事項

- 性質: Trial(prompt変種sweepの生成側)。到達上限Status: `GENERATED`(33本生成+照合+文体指標まで)。しきい値・推奨なし。
- 隔離規則: 書込は `er052_output/factlock_writer_trial_01/sweep_01/` 配下、`er052_factlock_sweep_01_run.py`・`er052_factlock_sweep_01_test_01.py`(変種追加・共通修正Tのための最小編集)、`docs/pm/RESULT_PACKET_FACTLOCK_SWEEP.md`、`docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_04b.md`(+`_check.json`)のみ。Production code編集禁止。既存harness `er052_factlock_writer_trial_01_run.py` 編集禁止。
- 費用: 上限¥300(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。本委任の見込み≈¥250(33本×≈¥5+照合+再付与)。
- STOP条件: S8/S9 smokeで事後タグ再付与・R3経路が動かず1回の最小修正でも直らない→当該変種を除外して続行(報告)。1枠再実行1回まで、全体8回まで。
- Opus独立技術レビューGate: 構造は条件A済み。評価設計はFableが並行で任意レビュー中(委任_04cへ反映)。
- 時間見込み: ≈100分(変種追加・テスト20分/smoke 2本15分/生成33本[4並列]60分/照合・文体指標は生成と並行)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read、全文Readは構造変更時のみ。G-1: git出力は使わない(git操作禁止)。F-1: transcript退避不要。
T-0: 受領した委任文を本ファイルへ全文保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。
T-2: TTSなし(音声生成禁止)。T-3: 費用上限はGuardrailであり自動STOP閾値ではない(上記定型文)。

## ユーザー指示(原文)

「AIは禁止、誘導すると上手くいきません(特にエンターテイメント性については)。また指定を多くすると1パターン化します。…5でも10でもパターンを振って方向性を決めるのが良い…時間重視で一回の評価で広く知見がえられる、方向性が決めれる、そのような評価を考えてください。」(2026-10-08)。sweep費用上限¥300はFableが提示済み(ユーザー異議なし)。

## KPI provenance欄

生成33本の照合指標・文体指標・JA FC/STOP/費用: fresh(Trial harness)。S0/S5参照: reuse。E2E自己確認: No。

## Opus台帳更新: 該当なし。

## 事前指定Read一覧

- docs/pm/RESULT_PACKET_FACTLOCK_SWEEP.md 全文(委任_04a結果)
- sweep_01/variants.json 全文、DESIGN_SWEEP_01.md 付録A、PREREGISTRATION_SWEEP.md 全文
- v2_design/DIAGNOSIS_01.md 全文(診断: 数字2.6倍・常体化・比喩種増・タグ番号取り違え・judge誘導語・位置バイアス)
- v2_design/DESIGN_02.md 案Aのブロック全文(S12として採用)、共通修正Tの文言
- er052_factlock_sweep_01_run.py: Grep `variants|def apply_variant|postprocess|retag|R3` →該当範囲Read

## 事前指定Grep一覧+追記位置・更新位置の手順

- variants.jsonへ追加: **S11**=S4と同一だが数値規則を「中核数値も原則書かない。記事の理解に本当に必要な場合だけ、台帳の表記そのままで最大1つ」に差し替え(診断の「数字2.6倍」を切り分け)。**S12**=DESIGN_02の案A(v1規則維持+語り口規則。ユーザー仮説「誘導は効かない」の検証端点)。合計 新規11変種×3 brief=33本。
- 共通修正T(【事実N】のNはbrief内連番のみ、台帳IDを入れない、の1文)を全タグ付き変種(S1〜S4、S6、S9〜S12、S8のR0)のR0ブロックへ追加。S7(目標形)には追加しない(規則を書かない変種のため。ただしタグの書式例は示す)。
- build_variants.pyで再生成→variants.json sha更新→テスト追加(S11/S12注入・共通修正T含有)→ `.venv\Scripts\python.exe -X utf8 -m pytest er052_factlock_sweep_01_test_01.py -q` PASS。
- 文体指標の計測script `sweep_01/tools/style_metrics.py`(決定論、¥0): 記事ごとに です・ます文の割合/アラビア数字の個数/推量・仮定語(かもしれ・もし・だろう・はず・ようだ)の個数/問い(?・?)の個数/比喩系語の異なり数(DIAGNOSISの語彙表を再利用)/字数/「ではありません」型の個数。全33本+S0/S5参照(既存R2本文)に適用し `sweep_01/eval/STYLE_METRICS.md`(変種別平均)。
- 追記位置: sweep_01/MANIFEST.json(run別: variant・slug・brief・sha・model_id実測・cost・exit・JA FC must-fix・EN再生成・STOP・R3採否)、sweep_01/eval/CHECK_SUMMARY_SWEEP.md(照合(i)〜(iv)の変種別集計、S8は再付与ベースと明記)、PREREGISTRATION_SWEEP.mdに改訂履歴(S11/S12追加・共通修正T・判定文中立化と不戦勝除外を委任_04cで適用する旨)。

## 実行コマンド全文

cwd=C:\Users\tensh\eigo-radio、python=.venv\Scripts\python.exe -X utf8。

0. 委任文全文保存+検証: .venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_04b.md --json-out docs\pm\delegation_log\2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_04b.md_check.json
1. 変種追加・共通修正T・テスト(上記)。
2. smoke: S8とS9を hormuz b4 で各1本: .venv\Scripts\python.exe -X utf8 er052_factlock_sweep_01_run.py --variant S8 --slug hormuz --brief-md er052_output\factlock_writer_trial_01\briefs\hormuz\b4\selected_brief_factlock.md --core-numbers-json er052_output\factlock_writer_trial_01\briefs\hormuz\b4\core_numbers.json --ledger-txt er052_output\open233_b3_trial_01\runs\hormuz\nb\V0\b4\research_ledger\verified_fact_ledger.txt --out-dir er052_output\factlock_writer_trial_01\sweep_01\runs\hormuz\control\b4__S8__r1 --budget-jpy 12 --yes-run-paid (S9も同様に--variant S9・out-dir b4__S9__r1)。確認: 事後タグ再付与が動く・連鎖切りログ・R3採否・タグ残存0・model_id実測6-luna。smoke 2本は本番に含める。
3. 本番: 残り31本(11変種×3 brief[meta b2、hormuz b4、space_weapons b3]−smoke2)。sweep_01/tools/driver_sweep.py(driver_fl.py相当、4並列・自動降格)で投入。出力 sweep_01/runs/<slug>/control/b<i>__S<k>__r1/。各run --budget-jpy 12。
4. 照合集計・文体指標・MANIFEST。
5. docs/pm/RESULT_PACKET_FACTLOCK_SWEEP.md上書き。

## SSOT追記文: なし。

## Git: git操作禁止。commit候補(後続): er052_factlock_sweep_01_run.py, er052_factlock_sweep_01_test_01.py, er052_output/factlock_writer_trial_01/sweep_01/**(eval/_private/除外), 委任文(+check.json), docs/pm/RESULT_PACKET_FACTLOCK_SWEEP.md。

## 報告(RESULT_PACKET項目)

RESULT_PACKET_FACTLOCK_SWEEP.md上書き(ヘッダ: 管理ID・Status=GENERATED・実費/¥300・Production変更なし・git未操作)。本文: 1.生成結果表(変種×brief: 完走/STOP理由、費用、所要秒、JA FC must-fix、EN再生成、R3採否[S9]) 2.照合指標の変種別表(不整合率・unsupported/記事・タグなし断定文・数値一致・残存タグ、S8は再付与ベース) 3.文体指標の変種別表(S0/S5参照込み) 4.smoke所見(S8/S9の実動作) 5.変種追加・共通修正Tの反映箇所とsha 6.委任_04c(LLM評価)へ渡す盲検化の準備状況(blind copy作成は04cで行う旨) 7.問題・残作業(blockingか明示) 8.check_delegation_prompt結果1行、一覧外Readの理由。推奨は書かず事実のみ。
