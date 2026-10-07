# 2026-10-08 OPEN-233-SENTENCE-FACT-LINK-PRECISION-TRIAL-01 委任_01(T3: Stage1 r3 `support_fact_ids` の文→factリンク精度測定、上限¥40)

Management-ID: OPEN-233-SENTENCE-FACT-LINK-PRECISION-TRIAL-01(委任_01)

## 並行タスク(衝突回避)
委任(STAGE2-01_03: ①v3 replay、runner構造要素Rewrite部分、`er052_output/open233_stage2_01/v3/`)が並行してAPIを使う。本委任の書込先: `er052_output/open233_link_precision_01/`、`docs/pm/link_precision_01/`、delegation_log。**runner/checkerコードは編集しない**(`OPEN233_SAVE_R3_SUPPORT_IDS=1` は委任_01で実装済み・既定OFF。本委任ではONで呼ぶだけ)。SSOT/ACTIVE_TASK/RESULT_PACKET編集禁止、git禁止。起動前に `Get-Process python*` を確認し、二重起動を避ける(同時プロセスは自分の分1〜2本まで)。**API上限¥40、¥35でSTOP**。held-outは手順4まで開かない。

## 背景(なぜ測るか)
段階0-B(規則ベース危険文: 自動リンク63% vs 正解94%で成立/不成立が分かれる)とT1(決定論検出器: 正解リンクで主体型の再現率2倍)の両方で「文→台帳factのリンク精度」が検出成立の鍵と判明。Stage1 r3は `support_fact_ids` を返すが保存されていなかった(委任STAGE2-01_01で保存スイッチ実装)。このリンクの精度を測り、「リンク供給源として使えるか」を判定する。Writer自己注釈④は本委任では実装しない(別判断)。

## 事前指定Read
- `er052_output/open233_stage2_01/precheck/{r3_support_ids_inventory.md,replay_targets.json,stage1_candidate_rate.md}`、`er052_open233_stage1_coverage_checker_01.py` の `save_r3_support_ids_enabled` 周辺(呼び方のみ)
- `er052_output/open233_stage0_01/reclass/known_relation_ng.jsonl`(dev項目: 評価JSON由来のfact_id=oracle)と `split.json`(held-outは手順4まで開かない)
- `er052_output/open233_reversal_detect_01/T1_RESULT.md`(リンクが鍵という所見、未提示→不在断定型)

## 作業(M2: 先に事前登録)
1. `docs/pm/link_precision_01/preregistration_T3.md`(時刻付き): 対象=replay対象33記事のうちdev項目に紐づく記事(CCP 18・E2E_02 P2 10・polysemy_04 5)のEN最終本文。測定=Stage1 r3を `OPEN233_SAVE_R3_SUPPORT_IDS=1` で1回replay(Stage1のみ、Stage2/Rewriteは回さない)し、文(unit)ごとの `support_fact_ids` を保存。oracle=評価JSONの既知NG項目のfact_id(dev)、および台帳の fact_selection_evidence / brief の selected_fact_ids(記事全体の正解集合)。指標: (a) 既知NG文について、r3の support_fact_ids が oracle fact_id を含む率(再現率)、(b) 全文について、support_fact_ids が記事の selected_fact_ids の部分集合である率(妥当性)、(c) 空(リンクなし)の文の割合と、その中に既知NG文(特に「未提示→不在断定」型・新世界主張型)がどれだけ含まれるか、(d) 3記事×3回の反復一致率(同一文で support_fact_ids が一致)。合格ライン(件数ベース): (a)≥ 既知NG文の70%、(d) 3/3一致 ≥80%、費用≤¥40。held-out 1回のみ(方向一致確認)。
2. 実行(dev)→集計→(必要なら)解釈の記録。調整は行わない(r3 promptは変えない)。
3. 「未提示→不在断定」型の検出可能性の評価(¥0): リンクなし文 ∧ 否定語 ∧ 台帳に「未提示(not stated)」の記述がある実体語を含む、という決定論規則が、T1で見逃した既知NG(jb9k-n3以外の否定型5件、475j-n1)をdevでいくつ拾うか、負荷(印の付く文/記事)はいくらか。regular rule evaluation only(APIなし)。
4. held-out 1回。
5. `er052_output/open233_link_precision_01/T3_RESULT.md`(事前登録照合、PASS/FAIL、リンク供給源としての可否、次の設計への含意=事実のみ)。
6. T-0: 本委任文を `docs/pm/delegation_log/2026-10-08_OPEN-233-SENTENCE-FACT-LINK-PRECISION-TRIAL-01_01.md` へ保存+check.json。

## 報告
12行以内: (a)〜(d)の数値、合格ライン照合、リンクなし文の割合とNG含有、未提示→不在断定規則の再現率/負荷、held-out方向、費用、ファイルパス。
