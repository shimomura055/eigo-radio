# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_32(2026-10-01)

## 1. 委任内容(要旨)

広いTrial iteration 8(=重大誤解原則・要素Trial修正の横断検証)。
ユーザー承認済み(2026-10-01)、見込み¥40。新テーマ生成なし。新しい
改善案を探すTrialではなく「現在の設計が横断的に安定して機能するか」の
確認。29 instance全量のうち9 instance(neg1/neg2/neg3/meta_run03_
advanced/meta_run03_standard/hormuz_run03_standard/hormuz_run03_
advanced/bgroup_B3/safety_A2A3)はn=2、残り20 instanceはn=1。Guardrail
¥50。

## 2. 実施内容

`er052_open233_self_recovery_flow_runner_01.py`に`OUT_DIR_ITER8`を
新設(既存OUT_DIR_REP17までの出力は無変更)。新規
`er052_open233_self_recovery_flow_runner_01_iter8_01.py`で、Safety12
fixture(`safety_*`)を除く17 instanceのStage1を"fresh"へ明示的に
上書きし(reuse fixtureは重大誤解原則配線前の出力のため)、既存
`run_instance`/`aggregate_measurements`/`combine_n2_measures`/
`compute_cost_breakdown_5way`を再利用して実行した(新規ロジック追加
なし)。

実測: ¥24.9738(Guardrail¥50内、見込み¥40より安価)、132 call、API
error 0件、TrialAbort 0件。

**良好な点**: 不要Rewrite率11.11%(1/9、iter7の21.43%から改善)、
既知のハードケース`hormuz_run03_standard`(iter7は2/2 STAGE4)が今回
2/2ともRewrite 0件で解消(ユーザー承認済みhormuz-HF009再ラベルの効果が
full flowで初めて確認できた)、Hook rubricの実際の発火Evidenceを
初めて観測(`safety_A2A3`/`safety_A4`のHook段落claim)、全体平均コスト
¥0.6975/instance-run・worstコスト¥5.1772(ともにiter7から改善)。

**新規に判明した問題(2件、Safety-critical誤降格)**:
1. B3(HF-007、§7-4で正解BLOCKING確定済み)がn=2の両方でStage2 body
   rubric(V5)によりQUALITYへ誤降格(安定した誤判定、`changed_
   causality`/`unsupported_new_claim`のみでfloor非該当のため)。
2. A2A3-0(HF-003、未確認の支払主体追加)がn=2の1/2でQUALITYへ誤降格
   (同一Stage1出力[reuse、決定論]に対しStage2 LLM判定のみが変動)。

候補修正(`matched_notes_id`+`observation_consistent=False`を新floor
条件とする案)を検討したが、同一実測データ中でこの条件がhormuz-HF009
(ユーザー承認済み再ラベル)・meta_run03_standard・safety_A5の正当な
QUALITY/ACCEPTABLE claim群(計29件)にも該当することを確認し、既存の
ユーザー承認済み決定を無効化するリスクがあるため**不採用**とした。
§7 STOP条件(小修正1回後もSafety-critical誤通過が残る)に該当する
として、根本設計変更(Safety-critical群限定のredundant judge導入等)は
本委任のスコープ外としコード変更を行わず、Fable/ユーザー判断へ委ねる。

**追加で判明した問題(実記事の人間確認率悪化)**: `meta_run03_
standard`がn=2の両方でSTAGE4(`stage4_reason`はsample間で
`same_claim_fact_id_reblocked`/`target_not_locatable`と異なる)に
到達し、実記事6種10 runの人間確認率が20%(iter7の0%から悪化)。
いずれもfail-closed(false PASSではない)。原因候補はStage1 freshの
検出網羅性向上(`changed_number`floor claimがcycle毎に6→11→9件と
増加検出)と`escalate_to_paragraph`廃止の組み合わせにより、
MAX_CYCLES(2)内で全箇所を解消しきれなかったこと。根本解決(MAX_
CYCLES拡大等)は本委任のスコープ外とした。

**既存false PASS自動検知の限界(開示)**: `aggregate_measurements`内の
`silent_pass_candidate`は常に`0`を返す非稼働プレースホルダであり、
上記2件の誤降格はSAFETY_CRITICAL_SUB_IDS(8claim名指しリスト)との
手動照合で初めて検出できたものである。

FAILは2件(B3/A2A3-0の誤降格、meta_run03_standardの人間確認率悪化)
発生したが、いずれも原因特定の結果「安全な小修正では解決できず根本
設計変更が必要」と判断し、コード変更・追加再確認call(≤¥8)は実施
しなかった。

## 3. 記録

design書§7-0-iter32(新規知見)・§9-1㉒(Trial総括)、REPORT§30(A〜E・
揺れ・Hook実フロー・iter7比較・VALIDATED最低条件7項目充足表)、
DECISION_LOG新規エントリ、OPEN_ITEMS(OPEN-233行追記)、読み比べページ
更新(iter8から3記事追加: hormuz_run03_standardのRewriteなし例/neg3の
最小修正例/safety_er009_changed_actorの正当BLOCK例、既存版は
`index_rep17.html`へ保存)を実施した。

## 4. 確認事項(Fable/ユーザーへ)

- B3(HF-007)・A2A3-0(HF-003)のSafety-critical誤降格への対応要否
  (根本設計変更[Safety-critical群限定のredundant judge導入等]を
  行うか、既知の残存リスクとして記録し保留するか)。
- `meta_run03_standard`の人間確認率悪化(MAX_CYCLES拡大/
  escalate_to_paragraph部分復活等の根本修正を検討するか)。
- Phase 2(10〜20実記事規模)の新規テーマ選定(PM_GOVERNANCE§13)。

## 5. 費用・Status

本委任¥24.9738(Guardrail¥50のうち、残¥25.0262)。Phase累計
¥437.6498+¥24.9738=**¥462.6236**/総枠¥600、残**¥137.3764**。
Status=`ITER8_BROAD_STABILITY_TRIAL_COMPLETE_COST_AND_UNNECESSARY_
REWRITE_IMPROVED_BUT_B3_A2A3-0_SAFETY_CRITICAL_MISDOWNGRADE_AND_META_
STANDARD_HUMAN_REVIEW_REGRESSION_FOUND`。詳細:
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§30、
`docs/pm/design_open233_self_recovery_flow_01.md`§7-0-iter32/§9-1㉒、
`DECISION_LOG.md`2026-10-01委任_32エントリ、
`er052_output/open233_self_recovery_flow_runner_01_iter8/`。
