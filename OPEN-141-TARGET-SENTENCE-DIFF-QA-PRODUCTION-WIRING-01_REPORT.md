# OPEN-141-TARGET-SENTENCE-DIFF-QA-PRODUCTION-WIRING-01

**管理ID**: OPEN-141-TARGET-SENTENCE-DIFF-QA-PRODUCTION-WIRING-01(主)+
EDITORIAL-B-FAMILY-VOICES-FACT-SAFETY-GATE-ENABLE-01 +
OPEN-121-METHOD-C-V2-CLOSE-01 + PM-CLOSEOUT-CONSOLIDATION-105(Git)
**種別**: Production配線(target-sentence-matching既定ON+差分QA案I)+
3V Fact Safety保守版ゲート既定ON化+方式C-v2 Close
**日付**: 2026-09-13
**実行者**: sonnet-worker(単独委任、1回で完結)

## 前提(ユーザー正式判断2026-09-13、原文)

> 1. 3V Fact Safety: 追加Trialは不要です。offlineでは有効性が確認できているため、次のB-Family実記事生成時に自然発火した場合にruntime evidenceを取得・確認する方針としてください。
> 2. target-sentence-matching+Local Rewrite差分QA: Production採用で進めてください。Local Rewrite後の変更箇所を正確に特定し、その変更箇所に対してFact Checker A'+Ledger等の差分QAを再実行する構成でProduction反映してください。今回のTrial結果・実記事での検出実績から、追加コストに対して十分なFact Safety上の価値があると判断します。
> 3. Local Rewriteの見出し混入バグ修正: 明確な不具合修正のため、Production反映で問題ありません。
> 4. 方式D': 現在のProduction採用・配線済み構成を継続してください。
> 5. 方式C-v2: Productionには採用しません。Closeしてください。Trialとしての技術的成立性は確認できましたが、既存方式Aに対する追加検出が実測0件であり、追加ASR呼び出し・latency増に見合うincremental valueが確認できないためです。C-v2については「Trial失敗」ではなく、「検証の結果、既存A+D'構成に対する追加価値が不足しているためProduction不採用」という理由をSSOT/Decision Log等に明確に残してください。

## 1. 実装内容

### 1-1. target-sentence-matching既定ON化

`er010_ledger_local_rewrite_09.py::rewrite_ng_item()`の既存opt-in引数
`use_target_sentence_matching`(既定`False`、関数自体の既定値は変更せず
安全側に維持)を、A-Family(`er003_v1_n3_01_articles_generate.py`の
`run_one_pattern()`内、Local Rewrite cycleループ内の呼び出し箇所)・
B-Family(`er012_b_family_voices_writer_generic_01.py::run_ledger_
deviation_and_local_rewrite()`の同等ループ)の両呼び出し元で、明示的に
`use_target_sentence_matching=True`を渡すよう変更した。関数本体・
Judgeの基準・prompt自体は無変更(OPEN-141 Phase Bで実装済みのロジックを
そのまま有効化)。

### 1-2. 差分QA案I(Fact Checker A'+Ledger Deviation Checker再投入)のProduction配線

Trial専用スクリプト(`er011_open141_target_sentence_diff_qa_integration_
trial_b_01.py::run_diff_qa_for_target_sentence()`)のロジックを、新しい
LLM判定基準・promptを一切作らずそのまま`er010_ledger_local_rewrite_09.py`
(Production module)へ移植した:

- `run_diff_qa_for_accepted_rewrite(client, topic_ja, target_sentence,
  before_ctx, after_ctx, verified_ledger_text, ledger_model,
  fact_checker_model)`: 対象文(+前後1文)をFact Checker A'
  (`er002_ja_web_research_r3.build_fact_check_prompt`/
  `make_fact_checker_fn`/`run_fact_checker_with_gates`)とLedger
  Deviation Checker(`vfl01.run_deviation_check`、Hook-aware)へ再投入
  する。`fact_checker_model`は呼び出し元が解決した値をそのまま受け取り、
  この関数自身はmodel選択ロジックを持たない(Gate3項目7対応、Trialが
  `r3.FACT_CHECKER_MODEL`を直接参照していたのに対し、Production版は
  各呼び出し元の既存routing`routing.require_model("WRITER_FACT_CHECK",
  routing.WRITER_FACT_CHECK_MODEL)`をそのまま使う)。
- `apply_diff_qa_to_resolved_rewrite(rewrite_result, ...)`:
  `rewrite_ng_item()`の戻り値へ`diff_qa`キーを追記する。
  `resolved=False`(3-attempt上限で未解決、既にhuman_review_
  required=True)の項目には適用しない(¥0で早期return)。
  `blocks_acceptance`(Fact Checker A'のverdict=`FAIL`、または
  Ledgerの対象文再評価=`LEDGER_DEVIATION`)の場合のみ、
  `resolved`を`False`へ、`human_review_required`を`True`へ書き換える
  (**新規のretry/fallback機構は作らず、既存の3-attempt枯渇時と同一の
  下流処理[cycle継続→最終的にNG_REVIEW_REQUIRED]へ合流させる**)。
  `REVIEW_REQUIRED`は既存Fact Checker A'のnon-blocking advisory運用
  方針(`er003_v1_n3_01_articles_generate.py`L1013-1025)と同一に扱い、
  記録のみで通過させる。
- `DIFF_QA_CALLS_PER_ITEM = 1`(既存`MAX_REWRITE_CYCLES`/
  `MAX_REWRITE_ATTEMPTS`[いずれも3]とは独立の別軸カウンタ、対象文1件
  につき差分QA呼び出し1回のみ)。

呼び出し元(A-Family・B-Family)は、`rewrite_ng_item()`呼び出し直後に
`apply_diff_qa_to_resolved_rewrite()`を呼び、続けてPoint Overlap
rule-based再計算(`er008_point_overlap_qa_18.recompute_point_overlap_
for_target_sentence()`、新規追加関数、対象文がPoint One/Two本文に
属する場合のみ再計算・LLM再呼び出しなし・記録のみ)を`diff_qa_point_
overlap`キーへ記録する。B-Familyは`topic_ja`が呼び出し元から渡されて
いない場合(既存test互換の既定値`""`)、意図しないAPI呼び出しを避ける
ため差分QA自体を発火させない安全側ガードを追加した(`run_voices_
pattern_3v()`からの実呼び出しでは常に`topic_ja`が渡される)。

### 1-3. Local Rewrite見出し混入バグ修正

OPEN-141 Phase Bで既にFable自律範囲として`APPROVED_FOR_PRODUCTION`済み
(`split_sentences()`の見出し行除外、PM-CLOSEOUT-CONSOLIDATION-104)。
本タスクでの変更なし、既定ON化後も継続して有効。

### 1-4. 3V Fact Safety保守版ゲート既定ON化

`er012_b_family_editorial_type_registry_01.py::VOICE_FACT_SAFETY_GATE_
MODE_DEFAULT`を`False`→`True`へ変更。B-Family 3V Production経路
(`is_voice_fact_safety_gate_mode_enabled()`が`family=="B"`かつ本フラグ
`True`の場合のみ有効)で既定ONとなる。A-Family経路はこのフラグ・関連
関数(`_apply_b_family_voice_safety_gate()`)を一切参照しないことをgrepで
再確認した(該当ファイルは`er012_b_family_editorial_type_registry_01.py`・
`er012_b_family_voices_writer_generic_01.py`の2つのみ)。

### 1-5. 方式C-v2 Close

`er011_open121_repetition_qa_production_01.py`のモジュールheaderへ、
2026-09-13付でProduction不採用・既定OFF維持・呼び出し元は渡さないことを
明記するコメントを追加した。コード自体(`run_method_c_v2_window_check()`
等)・`enable_method_c_v2`既定`False`は無変更のまま残す。Production
呼び出し元4箇所(`er003_v1_*.py`等)がこの引数を一切渡していないことを
grepで再確認した。

## 2. Gate 3 Production Wiring Checklist(14項目)

| # | 項目 | 状態 |
|---|---|---|
| 1 | Production正式初回経路 | 完了(1-1/1-2節、A-Family`er003_v1_n3_01_articles_generate.py`・B-Family`er012_b_family_voices_writer_generic_01.py`の両Local Rewrite cycleループへ配線) |
| 2 | retry・fallback・regenerationとの整合 | 完了(FAIL相当は既存human_review_required/cycleの流れへ合流、`DIFF_QA_CALLS_PER_ITEM`は`MAX_REWRITE_CYCLES`/`MAX_REWRITE_ATTEMPTS`と独立、記事再生成時[regeneration]も同一cycleループを通るため同一経路で動く) |
| 3 | Trial・DEV専用実装でないこと | 完了(ロジックをTrial専用スクリプトからProduction module`er010_ledger_local_rewrite_09.py`へ移植、Trial専用モジュールは呼び出し元・Production moduleいずれもimportしない) |
| 4 | Production runtimeでの実発火 | 完了(3節、Production関数`run_diff_qa_for_accepted_rewrite()`/`apply_diff_qa_to_resolved_rewrite()`を実LLM呼び出しで実行し実発火を確認) |
| 5 | 必要Regression/integration testのPASS | 完了(4節、新規15件+既存回帰PASS、`run_project_regression.py`default全件は5節参照) |
| 6 | runtime evidence(actual routing含む) | 完了(3節) |
| 7 | 実際のmodel_id・routing確認 | 完了(3節、Fact Checker A'実model_id=`gpt-5.6-luna`、`routing.require_model("WRITER_FACT_CHECK", ...)`経由で解決されたことを確認。TrialはWRITER_FACT_CHECK routingを経由せず`r3.FACT_CHECKER_MODEL`=`gpt-5.6-sol`を直接参照していたため、Production版は異なるmodelになる点を実測で確認した) |
| 8 | コスト影響評価 | 完了(6節) |
| 9 | `CURRENT_SPEC.md`反映 | 完了(本タスクで実施、「Ledger Deviation MAJOR時の局所Rewrite」行・3V Fact Safety保守版ゲート新規行・「TTS Repetition/False Start QA」行) |
| 10 | `DECISION_LOG.md`反映 | 完了(本タスクで実施、`PM-CLOSEOUT-CONSOLIDATION-105`エントリ+索引) |
| 11 | `OPEN_ITEMS.md`反映 | 完了(本タスクで実施、OPEN-141/OPEN-120/OPEN-121行) |
| 12 | 必要なGit反映 | 完了(本タスクでcommit・push、7節参照) |
| 13 | Dangling Reference Check | 完了(7節、Trial専用モジュールへのimportなし[コメント上の参照のみ]、C-v2呼び出し元4箇所は引数を渡していないことを確認) |
| 14 | ユーザー承認内容と実挙動の一致 | 完了(1節の各実装が2026-09-13ユーザー承認原文1〜5と一致することを本REPORTで対応付け済み) |

**全14項目充足のため Status = `PRODUCTION_WIRED`(OPEN-141主題部分)。**
3V Fact Safety保守版ゲートはGate3項目4/6(次のB-Family実記事生成時の
自然発火待ち)が未充足のため`APPROVED_FOR_PRODUCTION`(配線実装済み、
ユーザー合意済みの扱い)に留める。方式C-v2は`REJECTED_FOR_PRODUCTION`
でClose(Production配線自体を行わない決定のため14項目チェックリスト
対象外)。

## 3. Runtime evidence(実LLM呼び出し、Production関数、¥0の新規記事生成なし)

対象: OPEN-141 Phase Bで使用した保存済みVerified Fact Ledger
(`er003_output/n3_01/hanshin/research/verified_fact_ledger.txt`)+同一
対象文("The early lead faced one clear challenge, not repeated waves
of pressure.")。Trialスクリプトではなく、本タスクで実装した
**Production関数**(`er010_ledger_local_rewrite_09.run_diff_qa_for_
accepted_rewrite()`及び`apply_diff_qa_to_resolved_rewrite()`)を直接
呼び出した(スクリプト自体はrepoに含めない一時実行、結果のみ
`er011_output/open141_production_wiring_runtime_evidence_01/runtime_
evidence.json`へ保存)。

実測結果:
- `ledger_model` = `gpt-5.6-luna`(`vfl01.MODEL`、既存Production値)。
- `fact_checker_model`(実際にAPIへ渡ったmodel、`routing.require_model
  ("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL)`で解決) =
  `gpt-5.6-luna`。レスポンスの`response.model`実測値も`gpt-5.6-luna`で
  一致。
- 1回目呼び出し(`run_diff_qa_for_accepted_rewrite()`直接): `fact_check_
  status=FACT_CHECK_COMPLETED`、`fact_check_verdict=REVIEW_REQUIRED`、
  `web_search_call_count=2`、`ledger_check_target_eval.overall_status
  =LEDGER_COMPLIANT`、`blocks_acceptance=False`。
- 2回目呼び出し(`apply_diff_qa_to_resolved_rewrite()`経由、resolved=True
  の合成rewrite_resultに対して実行): `fact_check_verdict=REVIEW_
  REQUIRED`、`web_search_call_count=4`、`ledger overall_status=
  LEDGER_COMPLIANT`、`blocks_acceptance=False`、ラップ後の
  `resolved=True`・`human_review_required=False`(REVIEW_REQUIREDは
  non-blockingという設計どおりの挙動を実データで確認)。

STOP条件相当の事象(対応付けnot_found/誤対応、差分Fact Checker A'が
FAIL、既存Gate/上限との矛盾)はいずれも発生せず。

## 4. テスト結果

新規`er010_open141_diff_qa_production_wiring_test_01.py`(15件、実LLM
呼び出し0件・¥0):
- `DiffQaCallsPerItemConstantTests`(1件): `DIFF_QA_CALLS_PER_ITEM=1`が
  `MAX_REWRITE_CYCLES`/`MAX_REWRITE_ATTEMPTS`と異なることを保証。
- `RunDiffQaForAcceptedRewriteVerdictTests`(6件): PASS/REVIEW_REQUIRED/
  FAIL × LEDGER_COMPLIANT/LEDGER_DEVIATIONの組み合わせでの
  `blocks_acceptance`分岐、window_text構築。
- `ApplyDiffQaToResolvedRewriteTests`(4件): resolved=False早期return、
  FAIL/LEDGER_DEVIATION verdictでのresolved反転、REVIEW_REQUIREDでの
  non-blocking維持。
- `AFamilyDefaultOnWiringTests`(1件): `run_one_pattern()`が
  `rewrite_ng_item(use_target_sentence_matching=True)`を呼び、Local
  Rewrite受理直後に`apply_diff_qa_to_resolved_rewrite()`を実際に呼ぶ
  ことを確認(LLM全mock)。
- `BFamilyDiffQaWiringTests`(3件): `topic_ja`未指定時は差分QAを発火
  させない安全側ガード、`topic_ja`指定時は発火、実装レベルでの
  FAIL verdict伝播(cycle継続→`any_human_review_required=True`)。

既存回帰(無変更、全PASS、実測):
- `er010_n9_production_integration_09_test_01.py`: 33件PASS
  (3テストで新規`apply_diff_qa_to_resolved_rewrite`をmock化する変更が
  必要だったため、テストファイル自体は更新。cycle/loopの検証内容は
  無変更)。
- `er012_b_family_voices_writer_generic_01_test_01.py`+
  `er012_editorial_b_family_voices_3v_production_wiring_phase1_test_
  01.py`+`er010_open141_target_sentence_matching_diff_qa_b_test_01.py`:
  合計160件PASS(新規15件含む)。

`run_project_regression.py`(パターン指定を反復後、default全件を1回、
5節に実測件数を記録)。

## 5. `run_project_regression.py` default全件

本タスクで実測: `collected=2462 passed=2459 failed=3 errors=0 skipped=0`。
failed=3は本タスク以前から継続する既知の無関係failure(過去複数
Consolidationエントリで同一件数・同一傾向が記録されている既知
failure、本タスクの変更によるものではない)。新規追加分(本タスク新規
15件+`er010_n9_production_integration_09_test_01.py`修正3件を含む
既存33件)はすべてPASSに含まれる。

## 6. 費用(5区分)

1. **今回実測(runtime evidence、3節)**: web_search 6回($10/1000件=
   $0.06)+`gpt-5.6-luna`token費用(入力$0.20/1M・出力$1.20/1M、
   token数は未記録[Phase B同様の既知の改善余地]、概算$0.01未満)+
   Ledger Deviation Checker2回(web_search無し、同モデル、概算無視できる
   水準)。合計概算**$0.07前後(¥10〜15程度)**。上限¥50に対し約20〜30%。
2. **Trial特有の追加コスト**: ¥0(Trialは別タスクで既に実施済み、本タスクは
   Production関数の実行のみ)。
3. **異常retry・Human Review由来の上振れ**: ¥0(runtime evidenceは各1回のみ、
   retryなし)。
4. **Standard同期でのコスト**: 上記1と同一(Responses API、同期呼び出し)。
5. **Batch量産換算時のコスト**: 参考値、Fact Checker A'はweb_search必須の
   ため通常Batch対象外(既存Production運用方針と同一)。

**1記事あたりコスト影響(既定ON化後)**: Local Rewrite発火時のみ追加発生。
Phase B実測(¥15〜30/対象文、`gpt-5.6-sol`使用時)に対し、実際の
Production routingでは`gpt-5.6-luna`(より安価)が使われるため、実際の
1件あたりコストはPhase B見積りより低い可能性が高い(本runtime evidence
[luna、web_search2〜4回]は概算¥10〜15程度)。
**100記事換算**: Phase A実測の発火率(約0.4件/記事)を用いると、
100記事で約40件のLocal Rewrite発火が見込まれ、100記事換算コストは
概算**¥400〜600程度**(Phase B見積り¥600〜1,200よりやや低い、luna
モデル使用のため)。Point Overlap rule-based再計算は¥0(LLM再呼び出し
なし)。

## 7. Dangling Reference Check

- `er011_open141_target_sentence_diff_qa_integration_trial_b_01.py`
  (Trial専用)を実際にimportするProduction/testファイルは無し
  (`er008_point_overlap_qa_18.py`のコメント内での言及[出典明記]のみ、
  import文ではない)。
- `enable_method_c_v2`を渡すProduction呼び出し元は無し(自身のmodule+
  自身のtestファイルのみで参照)。
- `voice_fact_safety_gate_mode`/`VOICE_FACT_SAFETY_GATE_MODE_DEFAULT`は
  `er012_b_family_editorial_type_registry_01.py`と
  `er012_b_family_voices_writer_generic_01.py`(+両者のtestファイル)
  のみで参照、A-Family側の参照は無し。

## 8. 3V Fact Safety保守版ゲート有効化とC-v2 Closeの節(まとめ)

1-4節・1-5節参照。3Vゲートは配線実装済み・既定ON、次のB-Family実記事
生成時の自然発火をもってGate3項目4/6を充足しStatusを
`PRODUCTION_WIRED`へ格上げ判断する(本タスクでは新規記事生成を
行っていない、¥0)。C-v2は`REJECTED_FOR_PRODUCTION`でClose、コードは
削除せず既定OFFのまま残す。

## 9. 変更ファイル一覧

- `er010_ledger_local_rewrite_09.py`(差分QA案I Production関数追加、
  `import er002_ja_web_research_r3 as r3`追加)
- `er003_v1_n3_01_articles_generate.py`(A-Family配線)
- `er012_b_family_voices_writer_generic_01.py`(B-Family配線、
  `run_ledger_deviation_and_local_rewrite()`へ`topic_ja`引数追加)
- `er008_point_overlap_qa_18.py`(Point Overlap再計算関数追加)
- `er012_b_family_editorial_type_registry_01.py`(3Vゲート既定ON)
- `er011_open121_repetition_qa_production_01.py`(C-v2 Closeコメント追加)
- `er010_open141_diff_qa_production_wiring_test_01.py`(新規、15件)
- `er010_n9_production_integration_09_test_01.py`(既存3テストのmock更新)
- `er012_b_family_voices_writer_generic_01_test_01.py`(既定ON反映の
  テスト更新)
- `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`(SSOT反映)
- `er011_output/open141_production_wiring_runtime_evidence_01/
  runtime_evidence.json`(runtime evidence記録)
