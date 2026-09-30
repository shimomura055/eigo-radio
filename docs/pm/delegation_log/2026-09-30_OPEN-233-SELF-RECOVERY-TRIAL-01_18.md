# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_18(2026-09-30)

## 0. 委任_18a(先行、read-only分析、¥0)

委任_18aはiter6の全体Rewrite3件・不要Rewrite4件・real_run Escalation2件
・局所QA未統合の全件をread-onlyで開示分析し(`docs/pm/open233_iter6_
rewrite_disclosure_01.md`新規作成のみ、既存ファイル無編集、¥0)、
「①〜④のladderが一度も試行されずに⑥へ落ちる」等の構造的原因を機械
確認した。本委任_18はこの開示結果を根拠にコード修正・rep9 Trialを行う。

## 1. 委任内容(要旨)

ユーザー新指示12項目(局所QA統合/全体Rewrite経路の是正/不要Rewrite4件の
解決策実装/Escalation 2 runの解消/コスト是正)の反映+代表ケース拡張
再試行。広いTrialは含めない。Guardrail¥25(A=¥0/B≤¥20)。

## 2. 実施内容

- 作業A(¥0): 2-1(precheck合成マーカー実文解決`resolve_precheck_
  target_sentence`+`found=False`早期return[target_not_locatable]+
  degenerate output guard[title_degenerate/hook_degenerate])、2-2
  (disclosure-gap downgrade`apply_disclosure_gap_downgrade`、Trial
  限定)、2-3(a既存Evidence確認+b`same_fact_id_new_location`cycle拡張)、
  2-4(局所QA fastpath`run_local_qa_fastpath`+`full_recheck_required`
  5条件)を実装。design書§4-15/§5-9/§6-5新設。unittest新規39件+既存
  214件全PASS(`.venv/Scripts/python.exe -m unittest`)。
  `docs/pm/ACTIVE_TASK_C233V.md`で開始前チェック表(指示1〜12、未反映
  0件)を作成。
- 作業B(¥20.0358): 代表12 instance(neg1_meta_b3prod_a2/bgroup_B3/
  hormuz_run03_standard/safety_er009_changed_actor・changed_number・
  unsupported_new_claim/neg2_meta_refresh_a2/meta_run03_advanced/
  neg3_hormuz_prodrunner_b1b/meta_run03_standard/safety_A2A3/
  safety_A5)をn=2実行(新規`er052_open233_self_recovery_flow_runner_
  01_rep9_representative_01.py`、OUT_DIR=`er052_output/open233_self_
  recovery_flow_runner_01_rep9`、TOTAL_BUDGET_JPY=20.0)。Guardrail
  ¥20到達により`safety_A2A3`/`safety_A5`のsample2は未実行(10/12
  instanceはn=2完走)。
- 作業C(報告): REPORT§18、DECISION_LOG新規エントリ、OPEN_ITEMS.md
  OPEN-233行更新、本ファイル。

## 3. 得られた結論(要約)

主要3目標を達成: (1) `safety_er009_changed_number`が`6_full_article`
(⑥)を一度も経由せず`1_word_connective`/`3_sentence`で解消(precheck
locate是正の実測確認)、(2) `neg2_meta_refresh_a2`が2/2 sampleで
BLOCKING→QUALITY downgradeしRewriteなしで通過、(3) `meta_run03_
standard`が2/2 sampleともSTAGE4_ESCALATIONに至らなかった(人間確認率
0達成)。`safety_er009_unsupported_new_claim`の題名空文字化を2/2で
正しく検出しSTAGE4へ回した(disclosure §1-1-4の静かなfalse PASSを
解消、ただし根本Rewrite精度は未改善と正直に記録)。局所QA fastpathは
3回試行され3回とも安全側に既存の全文Recheckへフォールバックしたが、
コスト削減効果は今回のデータでは実証できなかった。

**新規観測(未解決)**: `hormuz_run03_standard`(sample1)で新規STAGE4
(`cycle_limit_exhausted_after_recheck`)を観測。根本原因分析により
本委任の変更由来ではなく既存の構造的限界(claim言い換えcycleパターン、
Phase2課題item8と同型)と判断したが、実測FAILとして正直に記録し、
追加の単発再実行はGuardrail安全側判断で見送った(§18-3参照)。Safety
側は全Safety claimでBLOCKING/floor維持を確認(disclosure-gap
downgradeの誤混入なし)。

29 instance全量ではないため広いTrialのGateは判定保留。Status=
`REP9_PARTIAL_GUARDRAIL_REACHED_MIXED_RESULTS`。

## 4. USER_DECISION_REQUIRED該当有無

該当なし(6条件いずれも非該当)。既存の安全装置(deterministic floor・
pre-check floor・既存post-hoc downgrade・cycle上限3)はいずれも変更・
回避していない。`apply_disclosure_gap_downgrade`はTrial限定の判定
候補でありProduction採用には別途ユーザー承認が必要(design書§4-15に
明記)。`hormuz_run03_standard`の新規観測はFable/ユーザーへの判断材料
として提示する。予算は¥20.0358/Guardrail¥25内(A=¥0/B=¥20.0358)、
Phase累計¥317.8415/総枠¥500内。

## 5. Git

commit予定(本ファイル含む)。パス指定`git add`(`-A`不使用)。

## 6. 報告(handback)

SubagentHandbackで報告(REPORT§18と同内容の要約)。
