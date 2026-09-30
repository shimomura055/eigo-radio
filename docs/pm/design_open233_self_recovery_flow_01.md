# OPEN-233-SELF-RECOVERY-TRIAL-01: Production Self-Recovery Flow 設計書

**Status**: `DESIGN_READY_FOR_OPUS_L2` → **[委任_04更新]**
`PHASE1_READY`(Opus L2レビュー#1完了・所見反映済み[§15]、Phase 1
実行前チェックリスト§9-0全項目確認済み。API呼び出し¥0、Production
非接続、実装なし)。委任_01(2026-09-30)で作成。→ **[委任_06更新]**
`PHASE1_STEP2_DONE`(既存Rewrite機構棚卸し[委任_05]を§5-0三分類表へ
統合、EN/JA局所Rewriteをそれぞれ既存ベース案[E-1/J-1]と新方式案
[E-2/J-2]の両論併記へ再構成[Phase 1 ⑤で比較実測予定]、deterministic
pre-check[`er052_open233_self_recovery_precheck_01.py`]をTrial実装、
Phase 1 ①[precheck FP率0%実測]・②[hormuz見逃し3attempt、Stage 2
診断3/3検出実測]完了。実測費用¥0.6285[Guardrail¥10、Phase累計]。
③以降・Production実装は未着手)。→ **[委任_07更新]**
`PHASE1_STEP4_DONE`(Phase 1 ③[Stage 1 variant実測確定: V0/V4-A/
S1-D比較、V4-Aを最終確定・S1-D不採用、根拠§14-5]・④[Stage2実単価・
batch化・prompt caching実測、per-claim vs batch判定一致率100%・
batch化でcost/latency改善、prompt caching費用削減率63〜64%実測、
Stage2較正リスク[Real-but-fixable群のQUALITY誤降格]を新規発見・
報告]完了。実測費用¥14.6598[Guardrail¥35のうち、Phase累計
¥15.2883]。⑤⑥は次回委任予定、Production実装は未着手)。→
**[委任_08更新]** `PHASE1_STEP5_DONE`(Stage2 rubric較正Trial実測・
確定[§4-8、R2採用・R3floor不採用、Safety群14/14維持・既知miscalib
6/6解消・negative群87.5%改善]、Phase 1 ⑤[Stage3型別Rewrite成功率
実測、§5-4-補2]完了: delete型baseline測定、replace型はE-1/E-2とも
100%[n=2]、**narrow_scope型[hormuz HF-009]はJ-1で完全解消・J-2は
未解消[drift 1件検出]**。採用案: narrow_scope=J-1、
replace_with_ledger_value=E-2第一候補(E-1はfallback)。実測費用
¥6.208[Guardrail¥45のうち、Phase累計¥21.4963]。⑥[統合dry-run]は
次回委任予定、Production実装は未着手)。→ **[委任_09更新]**
`PHASE1_DONE_IMPROVEMENT_NEEDED`(⑥統合dry-run完了: 新規runner
`er052_open233_self_recovery_flow_runner_01.py`で29 instance・92 call・
¥16.7806・0 errorを実測[§9-1⑥]。Self-Recovery 6項目実測[Initial
BLOCK23/Rewrite自動解消13/Final STOP9]、Escalation率9/29[Wilson
95%CI 17.3〜49.2%]、worst caseコスト¥2.2721でCap[+¥3]未超過。
**新規発見(いずれも報告のみ・独断で修正せず)**: (1) Stage1(V4A)
recall missを3instanceで実測(うち1件は現行Production STOP実例
hormuz_run02_advancedそのもの、Self-Recovery Flow到達前の見逃し)、
(2) Stage2出力schemaに`rewrite_hint`欠落がRewrite失敗の主要因、
(3) J-1汎用対象文特定の失敗率63.6%(委任_08手動アンカー実験との
乖離)、(4) **委任_08のnegative群R2測定[87.5%]がplaceholder文字列
[claim_text="(claim not found in baseline)"]に対する測定であり
無効、実クレーム文言での実測は0/4(0%)**。Phase 1計画①〜⑥完了、
Phase 2着手前に上記改善優先順位[§9-2]の解消を推奨。実測費用
¥16.7806[Guardrail¥45のうち、Phase累計¥38.2769]。USER_DECISION_
REQUIRED非該当[7条件いずれも]。Production実装は未着手)。

本書は前Phase`OPEN-233-CHECKER-REDESIGN-TRIAL-01`(以下「前Phase」)の
成果(Trial 1/2実測、Opus L2レビュー#1、Stability n=20実測、negative
claim候補16件、claim単位gold候補表)を踏まえ、目標を「Checker単体の
過剰品質率改善」から「**Production運用全体としてLedger/Deviation Check
起因のUSER_DECISION_REQUIREDを実質ゼロにするSelf-Recovery Flow**」へ
転換した新Phaseの設計書である。

---

## 1. 目的・ユーザー意図(2026-09-30、逐語要旨)

**最終目標**: 通常のProduction運用中に、Ledger/Deviation Checkを理由に
ユーザー判断を求められる状態を実質ゼロにする。現状「数記事に1〜2件
Checker STOP→USER_DECISION_REQUIRED」は量産性・開発速度の両面で
許容できない。

**基本方針**: Checker単体の完璧化が目的ではない。Productionフロー全体
として「初回Check→必要なら再スクリーニング→必要なら自動Rewrite→
再Check→Production継続」までシステム側で安全に完結させる。ユーザーへ
上げるのは「自動処理では安全に解決できない、本当に例外的なケース」だけ。

**Safety(絶対条件)**: Fact反転/actor取り違え/number・numeric scope重大
変更/negation反転/comparison方向反転/time・chronology重大変更/
unsupported material fact/主要Fact理解を変えるcausalityは確実に止める。
**重大fixtureの見逃し0件**を維持する。

**Self-Recovery Flowの構成(4段階)**:
- Stage 1 Initial Check: ACCEPTABLE/QUALITY/BLOCKING分類。ACCEPTABLE/
  QUALITYは継続候補、BLOCKINGのみ次段。
- Stage 2 Re-screening: 同じ判定の機械的反復ではなく「本当にProduction
  を止めるべきmaterial errorか」を再評価する。目的=初回Checkerの過剰
  品質・非決定性の吸収。
- Stage 3 Automatic Rewrite: 問題claimのみ・該当sentence/local context・
  必要最小範囲を修正→再Checker。
- Stage 4 Final Escalation: Re-screening+Rewrite+Recheckでも安全に解消
  できない場合のみUSER_DECISION_REQUIRED(通常運用では実質ゼロ)。

**主要受入条件の変更**: 「不要BLOCK率≤25%」は主要受入条件から外し
**診断用の中間指標**として残す。Primary KPI=**10〜20記事規模のProduction
相当TrialでLedger/Deviation Check起因のUSER_DECISION_REQUIRED=0件**。
Safety=重大Fact事故の見逃し0件。ゼロSTOPを無制限retryや高コストで
実現するのはNG。

**Trialの考え方**: まず既存fixture/artifactを最大限reuseしてSafety/
過剰BLOCK/re-screening/rewrite recoveryを検証(Phase 1)。設計が成立
したらProduction相当の記事Trialへ拡大する(Phase 2)。

**予算**: 新たに最大¥400(前Phaseの¥45.6803とは別管理)。

**目指す挙動**:
| ケース | 経路 |
|---|---|
| Normal | Check→PASS→継続 |
| False・borderline BLOCK | Check→BLOCK→Re-screen→QUALITY/ACCEPTABLE→継続 |
| Real but fixable | Check→BLOCK→Re-screen→Rewrite→Recheck→PASS→継続 |
| True exceptional | それでも解消不能→USER_DECISION_REQUIRED(通常運用ではほぼ発生しない) |

逐語全文はDECISION_LOG.mdの本エントリを参照(本書は要旨)。

## 2. Fable判定(設計の前提)

- 前Phaseの3件のUSER_DECISION_REQUIRED(指標定義/gold/materiality軸)は、
  本Phaseでは次のように再構成し、**Checkpoint Aでユーザー確認を取る
  (独断確定しない)**。
  - (a) 不要BLOCK率は診断指標へ格下げ(ユーザー指示、既に確定)。
  - (b) goldは**「最終到達状態」ベース**へ再構成する(§7参照)。重大
    fixture(ER-009-N1 9種・A群・changed_actor)はStage 1/2で必ず
    BLOCKING維持(Stage 2で通過させたらSafety事故)、その後Rewrite→
    PASSが期待到達状態。B2=Stage 2でQUALITY通過が期待。B1/B4は
    Opus claim単位評価どおりmaterial claim(B1-c/B4-a)はRewrite対象、
    非material claim(B1-a/b、B4-b/c)はStage 2通過が期待、fixture
    としてはRewrite→PASS到達が期待。B3=material(HF-007 conditions)
    につきRewrite→PASSが期待。negative claim候補16件=Stage 1または
    Stage 2で通過が期待。**いずれも「候補gold(ユーザー確認待ち)」**。
  - (c) materiality軸はStage 2 Second Judgeの判定基準として設計する
    (**真のProduction Promptは不変**)。**注(委任_03追記)**: これは
    真のProduction Deviation Check(`er003_v1_en_direct_vfl_01_
    generate.py`)については引き続き維持するが、Self-Recovery Flow
    Trial実装における「Stage 1」自体の構成(どのTrial variantを使うか)
    は§14で再検討し、V4A採用へ更新した(詳細§3-1/§14)。
- Stage 2の**deterministic safety floor**: Stage 1でchanged_actor/
  changed_number/changed_negation/changed_comparison/changed_timeの
  いずれかがtrueのdeviationは、Stage 2でACCEPTABLE/QUALITYへ降格
  させない(Rewrite必須)。Stage 2が降格できるのは、これらflagが全て
  falseのdeviationのみ。降格判断は「迷ったらRewriteへ」(fail-closed)。
- 既存案B(ja_source MAJOR→JA差し戻し1回)はStage 3のJA側Rewriteとして
  位置づけ直し、無駄な全文再生成を避ける「局所Rewrite」を優先候補と
  する(§5)。
- loop上限は設計で固定する。Stage 2は1回(BLOCKING確定時)、Stage 3
  Rewriteは記事あたり最大2回、Recheckは Rewriteごと1回、合計Checker
  call上限/記事を明記する(§3)。無制限retry禁止。

**Production Checkerのモデルに関する重要な既存事実(本Phase新規確認)**:
現行Production(`er003_v1_en_direct_vfl_01_generate.py::MODEL =
routing.WRITER_MODEL`、実体`gpt-5.6-luna`)は、前Phase Trial(er051系
harness、`gpt-6-luna`固定)とは**異なるモデル**でDeviation Checkを実行
している。Hormuz/Meta run_01〜03のE2E STOPは全てgpt-5.6-luna実測であり、
前Phase Trialのgpt-6-luna実測データとは直接比較できない(§10リスク
参照)。本設計のStage 1は既存Production Prompt/モデルを不変のまま
前提とし、Stage 2以降のTrial実装でどのモデルを使うかは別途明記する
(§9)。

## 3. Self-Recovery Flow設計(Stage 1〜4)

### 3-0. 全体像(状態遷移、テキスト図)

```
[Writer出力(Advanced or Standard)]
        │
        ▼
  Stage 1: Initial Check(Trial variant V4A、真のProduction Checkerは
  不変。§3-1/§14参照)
        │
   ┌────┴─────┐
   │            │
 ACCEPTABLE   BLOCKING-candidate(overall_status=LEDGER_DEVIATION、
 (deviations   MAJOR 1件以上)
 =[]、または          │
 全件MINOR)           ▼
   │          Stage 2: Second Judge(独立Prompt、claim単位)
   │                   │
   │         ┌─────────┼─────────┐
   │         │                   │
   │   deterministic floor   floor該当なし
   │   該当 → BLOCKING確定    → materiality判定
   │         │                   │
   │         │        ┌──────────┼──────────┐
   │         │     BLOCKING    QUALITY    ACCEPTABLE
   │         │        │           │           │
   │         ▼        ▼           └─────┬─────┘
   │    (cycle残数確認)                  │
   │         │                          ▼
   │   cycle枯渇 → Stage 4         継続(Production続行、
   │         │                     ラベルのみ記録)
   │         ▼
   │   Stage 3: Automatic Rewrite(局所優先、cycle消費+1)
   │         │
   │         ▼
   │   Stage 1: Recheck(Rewrite後の全文、既存Production Checkerを
   │         │          再実行=fail-closed、局所チェックに限定しない。
   │         │          **[委任_04改訂/A1]** 必ず`prior_issues`
   │         │          [直前cycleのBLOCKING確定claim一覧]を渡し、
   │         │          継続条件は「`overall_status==LEDGER_COMPLIANT`
   │         │          かつ`all_prior_issues_resolved==True`」の両方
   │         │          (既存Production gateと同一の厳しさを維持)
   │         │
   │   ┌─────┴─────┐
   │   │             │
   │ ACCEPTABLE   BLOCKING-candidate(claimが同一/新規いずれも。
   │   │             同一claim/fact_id再発は§3-3参照)
   │   ▼             └──→ Stage 2(cycle残数があれば再度)、
   │  継続                  枯渇していればStage 4
   ▼
  継続(Production続行)

(Stage 1 Recheckも同一Trial variant[V4A]で再実行する。§5-2参照)

Stage 4: Final Escalation(cycle上限[最大2]到達後もBLOCKING、または
JA Fact Check自体がSTOPした場合) → USER_DECISION_REQUIRED
```

### 3-1. Stage 1: Initial Check

**Stage 1設計の確定(委任_03、結論のみ。根拠の全文は§14)**: 本Self-
Recovery Flow TrialにおけるStage 1は、真のProduction Prompt(V0)を
無変更のまま使う案(§14 S1-A)ではなく、**Family X限定Trial variant
V4-A**(`er051_open233_checker_trial_variant_01.py`、
`build_trial_prompt_template("V4A")`/`build_trial_deviation_schema
("V4A", ...)`、post-hoc層は`classify_deviation_trial()`[V2と同一]、
前Phase委任_03で実装・実測済み、Prompt全体sha256
`e9c939930496ebed00a198455279bac1d61e6f5a162063f41ef5fde52cf81c97`)を
採用する(§14 S1-B)。**真のProduction Deviation Check
(`er003_v1_en_direct_vfl_01_generate.py::MODEL = "gpt-5.6-luna"`、
`DEVIATION_PROMPT_TEMPLATE`)は本委任を通じて一切無変更**(Family X
限定Trial harness内でのみV4Aを使う。V4AをProduction Stage 1として
正式採用する場合は、Self-Recovery Flow全体の採用とは別建ての
Production Prompt変更承認[USER_DECISION_REQUIRED条件(4)]が必要)。

- **入力/出力**: `vfl01.run_deviation_check()`相当の呼び出しに、
  Trial Prompt(V4A)とTrial schema(V4A)を渡す。`hook_aware=False`、
  Family X経路。severity算出ルール自体(「10種類のいずれかが明確に
  trueである場合のみMAJOR」)はV0から一切変更しない(V4Aはカテゴリ
  境界の明確化文のみを追加する差分ブロック)。
- **分類**: 既存の二値出力(`overall_status`)をSelf-Recovery Flowの
  3値語彙へ写像する。`LEDGER_COMPLIANT`(MAJOR無し)→**ACCEPTABLE**
  (継続、Stage 2以降へ進まない)。`LEDGER_DEVIATION`(MAJOR 1件以上)→
  **BLOCKING-candidate**(Stage 2へ)。**Stage 1アーキテクチャはQUALITY
  を直接出力しない**(materiality軸がないため、V4A採用後も変わらない)。
  QUALITYという出力値はStage 2でのみ生成される。これは既存Fable判定
  (c)と整合する設計上の制約であり、委任文の「ACCEPTABLE/QUALITY/
  BLOCKING分類」という表現は、実装上「ACCEPTABLE(継続) / BLOCKING-
  candidate(Stage 2で3値化)」の2値ルーティングとして実現する。
- **deterministic層**: V2 post-hoc(フラグ全falseでMAJORならMINORへ
  自動降格)はそのまま維持。
- **loop上限**: Stage 1自体はretryしない(1回のみ)。既存の「MAJOR時
  must-fix retry1回」(現行Production)は、Self-Recovery Flowでは
  Stage 3 Rewriteの一形態として再定義する(§5)。
- **STOP条件**: なし(Stage 1単独ではSTOPしない。BLOCKING-candidateは
  必ずStage 2へ渡す)。
- **コスト**: V4AはV0比call単価約+30%・latency約+60%(前Phase実測、
  §13-4/§14で費用モデルへ反映)。
- **ログ項目**: `article_id`/`writer_stage`(advanced/standard)/
  `deviation_id`/`claim_in_article`/`10 category flags`/`severity`/
  `origin`/`related_fact_id`/`cost_jpy`/`elapsed_seconds`/`raw_response_id`/
  `stage1_variant`(Trial期間中は`V4A`固定)/**[委任_04改訂/A2]**
  `detected_by`(`"stage1_llm"` | `"precheck"`。deterministic pre-check
  [§14-4]が単独で検出したdeviationは`"precheck"`とし、Stage 2の
  deterministic safety floor[§4-3]をStage 1の10 flagsに関わらず
  直接適用する[floor空振り防止、詳細§4-3])。
- **[委任_04改訂/A2]** `detected_by="precheck"`のdeviationは、Stage 2
  LLM materiality判定を経由せず**直接floor扱いでBLOCKING確定**とし、
  Stage 3(Rewrite)へ直送する(Stage 2をスキップ)。ただしPhase 1で
  precheckのFP率(§9-1①)が高いと判明した場合は、この扱いを「Stage 2へ
  強制送付するが棄却は不可としない(Stage 2で正当にACCEPTABLEへ戻す
  余地を残す)」という弱い分岐へ変更する(FP率実測後にどちらを採るか
  確定する。両案を設計として併記する)。
- **[委任_04改訂]** Stage 1のrouting述語は`overall_status`
  (`LEDGER_COMPLIANT`/`LEDGER_DEVIATION`)を用いる設計のまま維持する
  (`classify_deviation_trial`実装との整合、Opus所見論点2(A)Evidence
  参照)。`overall_action_trial`+`promote_deterministic_flag_v1`による
  ¥0のMINOR→BLOCKING昇格は、Phase 1で`overall_status`基準との比較実測
  対象として記録する(推奨のみ、Stage1採否確定は§9-1③実測後)。

### 3-2. Stage 2: Re-screening(Second Judge)

詳細設計は§4。概要: BLOCKING-candidateのclaim単位で、独立Prompt・
別callにより materiality(BLOCKING/QUALITY/ACCEPTABLE)を判定する。
deterministic safety floor該当時はLLM判定を待たずBLOCKING確定。

- **loop上限**: 1 claim あたり1回(Stage 3 Rewrite後のRecheckで再度
  BLOCKINGになった場合は、cycle残数の範囲内でもう1回発火する。つまり
  「Stage 2呼び出し回数」自体は cycle数(最大2)に連動し、記事あたり
  最大2回)。
- **STOP条件**: なし(Stage 2単独ではSTOPしない。QUALITY/ACCEPTABLEなら
  継続、BLOCKINGならStage 3または cycle枯渇でStage 4)。

### 3-3. Stage 3: Automatic Rewrite

詳細設計は§5。概要: origin(ja_source/translation)に応じてJA側
(既存案B、全文差し戻し)またはEN側(新設計、局所優先)のRewriteを実行し、
Stage 1へ戻してRecheckする。

- **loop上限**: 記事あたり**最大2 cycle**(1 cycle=Rewrite 1回+
  Recheck 1回)。JA側Rewrite(案B)を使った場合、そのcycleはAdvanced/
  Standard両方をリセットする(既存案Bの挙動を踏襲)。EN側局所Rewriteは
  該当stage(Advanced or Standard)のみに影響する。
- **STOP条件**: 2 cycle使い切ってもBLOCKING、または JA Fact Check自体
  がSTOP(`JAFactCheckStopError`、既存の別軸のfail-closed)した場合は
  即Stage 4。**[委任_04改訂/A5]** 加えて、Recheckで再びBLOCKINGとなった
  claim/fact_idがcycle 1でBLOCKING確定した claim/fact_idと**同一**の
  場合は、cycle残数に関わらず即Stage 4へ進む(Rewriteが当該claimに
  効かなかったことが実証されているため、同じ手段への追加投資をしない。
  Safety中立・コスト削減。異なるclaim/fact_idが新規にBLOCKINGとなった
  場合[Hormuz run_03型]のみcycle 2を発火する)。

### 3-4. Stage 4: Final Escalation

詳細設計は§6。

### 3-5. 記事あたりの上限(worst case)

| 項目 | 上限値 | 根拠 |
|---|---|---|
| Stage 2 call数/記事 | 最大2 × (Advanced+Standardの検出claim数) | cycle上限2 × 段階2 |
| Stage 3 Rewrite回数/記事 | 最大2 | 委任文指定 |
| Recheck(Stage 1再実行)/記事 | Rewriteごと1回、最大2 | 委任文指定 |
| JA全文Rewrite(案B相当)/記事 | 最大1(2 cycleのうち1つをJA側に使った場合) | 既存案Bの「1回上限」思想を維持、2つ目のcycleをJA側にも使うかはStage 3設計(§5)で条件分岐 |
| 総API call数/記事(worst case、実測ベースの概算) | 約20〜25 call | Hormuz run_03実測(¥10.35、Advanced 1回 STOP→案B JA regen[JA原本の実測構成: original+check+must_fix+check_retry+r1+r2+r2_check=7 call]+Advanced再実行[1 dev check]+Standard実行[1 dev check]で計10 call相当)に、Stage 2の軽量call(数call)とcycle 2回目のEN局所Rewrite(1〜2 call)を加算した概算。**要実測**(§9) |
| 総費用/記事(worst case、概算) | 約¥15〜25 | 上記call数 × 実測平均単価(Stage 1相当¥0.25〜0.4/call、Stage 2はclaim単位で入力が短いためより安価と推定、Opus論点1推奨4の「2倍未満」見積もりに準拠) |
| 総費用/記事(通常ケース、BLOCKINGなしでStage 2/3不要) | 既存Production実測と同等(¥0.8〜4.2程度、Meta run_03実測¥4.213) | Stage 1のみで完結する記事が大半である前提(既存run_03 Metaの実績) |

**[委任_04改訂/A9]** Stage 2 call数(claim単位、上表「最大2×検出claim数」)
は、instance単位1 callへのbatch化(claim配列入力→materiality配列出力)
を主案として比較する。per-claim callをbatch化前の比較対照として
Phase 1で同一入力に対し両方実行し(§9-1④)、実単価・降格判定の一致度を
実測してから採否を決める(claim間相互汚染のリスクがあるため即断しない)。

## 4. Stage 2 Second Judge設計

### 4-1. 独立Promptの位置づけ

Stage 1の`DEVIATION_PROMPT_TEMPLATE`とは**別物**の新規Prompt
(`SECOND_JUDGE_PROMPT_TEMPLATE_TRIAL`、Family X限定Trial variant、
Production非接続)を新設する。Opus L2レビュー#1論点1推奨4「2段階
呼び出し(detect→materialityを別callで判定)」を採用する。理由:
1回目(Stage 1)は現行Prompt完全据え置きのためSafety資産を保存でき、
Safety regressionリスクが構造的にゼロに近い(Opus所見どおり)。

### 4-2. materiality判定基準(Opus論点1推奨2をそのまま採用)

- **BLOCKING**: Ledgerの`claim`/`scope`/`numeric_value`/`date_or_
  period`/`conditions`のいずれかと**矛盾する**、または**Ledgerが
  別の原因・別の主体を明記しているのに異なるものを述べる**、または
  `notes_for_writer`が明示的に禁じた断定をしている。
- **QUALITY**: Ledgerの観測と矛盾しないが、Ledgerが保証していない
  関係付け(因果接続詞・動機の帰属・強調)が加わっている。
- **ACCEPTABLE**: **[委任_04改訂/A10]** Ledgerに**無い新規の**固有名詞・
  数値・時期・主体・因果を一切加えず(Ledgerに既出の固有名詞[例:
  「ホルムズ海峡」「中東」]を繰り返すことはこの制約に抵触しない、
  Opus論点3(C)への対応)、Ledgerが確認した事象の一般常識レベルの背景
  説明・条件付きの一般論にとどまる。
- **tie-break(fail-closed)**: 上記のどれに該当するか迷う場合は
  BLOCKINGとする(LLM Prompt本文にこの一文を明記)。

### 4-3. deterministic safety floor(§2で確定済み、再掲)

Stage 1のdeviationレコードで`changed_actor`/`changed_number`/
`changed_negation`/`changed_comparison`/`changed_time`/**[委任_04改訂/
A10]** `changed_certainty`のいずれかが`true`の場合、Stage 2はBLOCKING
以外を出力してはならない(LLM出力に関わらずpost-hocでBLOCKINGへ強制
上書き)。この6フラグを選んだ根拠: 前Phase Trial 2 Step1(changed_actor
n=5)でSafety 100%を達成した実績がある「主体・数値・否定・比較・時期」の
直接改ざんは、Ledgerとの矛盾が機械的に一意(paraphraseの余地が最も
小さい)であり、Second Judgeという追加LLM判定を経由させるリスクに
見合わない。**[委任_04改訂/A10]** `changed_certainty`をfloorへ追加した
理由: §7-0でB4-d(certainty変化)を「境界未確定のためTrial上はBLOCKING
[fail-closed]」と確定ラベルしているにも関わらず、floor対象外のまま
だとStage 2 LLMがB4-dを降格させ得るという矛盾(Opus論点3(E))を解消
するため。fail-closed側のラベルとfloorの扱いを一致させる。
**changed_scope/changed_causality/changed_fact/unsupported_new_claim
の4種はfloor対象外**(materiality判定に委ねる。B3[changed_causality]/
hormuz_run03_standard[changed_scope]のようにfloor対象外でもmaterialな
ケースがあることは、Prompt本文のBLOCKING基準1「Ledgerが別の原因を
明記しているのに異なるものを述べる」「scopeと矛盾する」で個別にカバー
する設計とする)。

**[委任_04改訂/A2]** `detected_by="precheck"`(§3-1)のdeviationは、
Stage 1のLLM出力にこの6フラグの値自体が存在しない(Stage 1がそもそも
検出しなかったため)。このケースはfloorの「フラグ判定」を経由できず
空振りする(Opus論点2(C)が指摘する穴)ため、**`detected_by="precheck"`
であること自体を上記6フラグと同格のfloor条件として扱い、Stage 2の
LLM降格を許さずBLOCKING確定**する(§3-1のとおり、precheck FP率実測
[§9-1①]次第でStage 2強制送付[棄却可]へ弱める場合がある)。

### 4-4. 入力(委任_03で確定、§13-3の不整合を解消)

**確定設計**: 記事全文は渡さない。以下4点のみを渡す(Fable第一候補、
委任文§5)。

- **Ledger全文**(該当fact_idの前後だけでなく全文。理由: 別の原因/別の
  条件が離れた箇所に記載されている場合があるため[B3のHF-007
  conditionsが好例]、部分入力では見逃すリスクがある。Ledgerは全文で
  渡す方針を維持=fail-closed優先)。
- source context(JA原文、origin=ja_source/translationの場合のみ、
  既存`source_article_text`引数をそのまま流用)。
- 対象claim(Stage 1の`claim_in_article`)。
- **[委任_04改訂/A8]** Stage 1のdeviation出力のうち`origin`/
  `related_fact_id`のみ渡す。**`explanation`・`severity`・10 category
  flagsはStage 2 LLMの入力から除外する**(Opus論点3(A)のanchoring
  懸念への対応。Stage 1の判断文をStage 2の同一モデルに読ませると
  「materialではない」への降格確率が構造的に下がり、fail-closed
  tie-breakと合わさって二重に保守化するため)。10 flags/severityは
  **Stage 2 LLM呼び出しの外側**でfloor判定(§4-3)にのみ機械的に使う。
- **対象claimを含む段落±1段落**(記事全文からの抽出。前Phase版は
  「前後±1文+記事全文」としていたが、記事全文入力は§13-3で判明した
  費用不整合[保守的見積りではStage 2単価がStage 1と同水準まで上昇]の
  直接原因だったため、段落単位(±1段落、文単位より広く記事全文より
  狭い)へ縮小する。**fail-closedの観点で不足する場合の条件**:
  (a) 対象claimが記事冒頭または末尾の段落にあり前後どちらか一方しか
  存在しない場合はある方のみ渡す、(b) Stage 2 LLMが`basis`判定に
  記事内の別段落の記述が必要と自己申告した場合(`reasoning_summary`に
  その旨が記録された場合)、Trial観測データとして記録し、Phase 1
  実測後に「段落±1で不足する実例があるか」を確認する。実例が確認
  された場合、段落範囲拡大[±2段落]または記事全文への切替えを検討する
  (Cap超過リスクとのトレードオフのためユーザー判断が必要になり得る)。
  Phase 1開始時点では段落±1を暫定確定とし、**実測不足の兆候が出るまで
  記事全文には戻さない**(コスト優先、Ledger全文で大半のfail-closedは
  担保できるという前提)。
  **[委任_04改訂/A8]** LLMの自己申告(上記(b))に加え、**決定論的な
  拡張条件**を設ける: ヘッジ語regex(`may`/`some`/`seems`/`would`/
  `not always`/`only one`等の固定語彙リスト、¥0)で段落±1の**外側**に
  ヘッジ表現が検出された場合、自己申告を待たずに機械的に±2段落へ拡張
  する(Opus論点3(D)、「記事末尾の総括段落のヘッジ」が段落±1で漏れる
  リスクへの対応。自己申告は非決定的で漏れるため、regexを主・自己申告を
  副とする)。

### 4-5. 出力schema(新規、Production schemaとは別)

```
{
  "materiality": "BLOCKING" | "QUALITY" | "ACCEPTABLE",
  "basis": "ledger_claim" | "ledger_scope" | "ledger_numeric_value" |
           "ledger_date_or_period" | "ledger_conditions" |
           "notes_for_writer" | "unsupported_relationship" | "none",
  "qualifier_present": bool,
  "rewrite_hint": string  # BLOCKING時のみ必須。Stage 3が使う具体的な
                          # 修正方針(何を削り何に置き換えるべきか)。
  "rewrite_kind": "delete" | "replace_with_ledger_value" | "narrow_scope",
                          # [委任_04新設/A11] BLOCKING時のみ必須。
                          # delete=Ledger外の付加物を削るだけで解消する型
                          # (B1-c/B3/B4-a相当)。replace_with_ledger_value=
                          # Ledgerの正しい値へ置換する型(changed_actor/
                          # changed_number相当)。narrow_scope=範囲の再限定
                          # が必要な型(hormuz_run03_standard changed_scope
                          # 相当、A2語彙制約と衝突しうる最難関の型)。
  "reasoning_summary": string  # 短い理由(Trial観測用、判定には使わない)
}
```

**[委任_04追記/A11]** `rewrite_kind`ごとの扱い: `delete`型は**LLMを
経由せずStage 3側で決定論的に該当文字列を削除できるか**をまず試す
(最も安く安全、Opus論点4推奨1)。`replace_with_ledger_value`/
`narrow_scope`型はStage 3のLLM局所Rewriteへ回す。Rewrite後、
`delete`型は当該文字列がRecheck対象本文から消えたことを、
`replace_with_ledger_value`型はLedgerの値が本文に出現したことを、
それぞれ機械検証する(Checkerの非検出に依存しない直接確認、Opus論点5
推奨3)。Phase 1では型別の成功率を測定項目に追加する(§9-1⑤)。

**Opus所見の反映**: `observation_consistent`/`ledger_field_basis`を
降格の自動トリガーとして使う設計(V5-C)は実データで既知のBLOCKINGを
複数見逃すことが実証されており**不採用**(§4-3のfloorとbasisフィールド
に置き換える)。`observation_consistent`相当のフィールドは`qualifier_
present`として観測用に残すが、判定ロジックには使わない(Opus論点4-D
「notes分離は判定に使わず観測用として残す」と同じ思想)。

### 4-6. Stage 1との独立性担保

- 別Prompt定数、別API call(Stage 1の出力を再利用するのみで、Stage 1
  Promptの内部状態を共有しない)。
- モデル/reasoning effort/温度パラメータはStage 1と別途明記(§9で
  Trial実装時に確定。Production Stage 1がgpt-5.6-lunaである一方、
  前Phase Trialはgpt-6-lunaを使用しているため、Phase 1 Trialでは
  **前Phase Trial資産(gpt-6-luna実測データ)との直接比較を優先し、
  gpt-6-lunaで統一する**。gpt-5.6-lunaとの整合確認は別途Phase 2で
  行う、§10リスク参照)。

### 4-7. Phase 1④実測(委任_07、per-claim vs batch・prompt caching・
Stage2較正リスクの新規発見)

**per-claim vs instance batch(B4=4claim/B1=2claim、gpt-6-luna、
`er052_open233_self_recovery_stage2_production_01.py`実装、§4-4
確定入力[Ledger全文+source context+対象claim+段落±1+origin/
related_fact_id、explanation/severity/10flags除外]どおり)**:
- **判定一致率100%**(batch callの各claim判定が、対応するper-claim
  callの判定と全件[B4 4/4、B1 2/2]完全一致。claim間相互汚染は
  観測されなかった)。
- **単価**: B4 per-claim合計¥0.4163(4call)→batch¥0.1862(1call、
  約55%減)。B1 per-claim合計¥0.1787(2call)→batch¥0.127(1call、
  約29%減)。
- **latency**: B4 per-claim合計19.3秒(4call逐次実行)→batch11.845秒。
  B1 per-claim合計7.87秒→batch6.485秒。batchはcall数・費用・
  wall-clock時間のいずれでもper-claimを上回った。
- **結論(A9)**: 本実測範囲(2 fixture、6 claim)ではbatch化を主案
  として採用する根拠が実測で補強された。claim数が増えた場合の
  相互汚染有無は未検証(n_claim=4が本実測での上限)。

**prompt caching**: 同一Ledger全文prefixで連続callを実行した結果、
**cached_input_tokensがinput_tokensの99.9%(B4: 4489/4492、B1:
4335/4338)を占めた**(gpt-6-luna Responses APIで自動キャッシュが
機能することを実測確認、A12)。**費用削減率≈63〜64%**(call全体、
出力token分はキャッシュ対象外のため入力token単体では約90%削減
[$0.10→$0.01/1M]、出力込みの実測削減率は63.2%[B1]〜64.4%[B4])。
**観測上の限界**: 本実測の「call1」は同一Ledgerを用いた直前の
per-claim/batch実測(5call、B4)と連続実行したため、厳密な
「未キャッシュ初回→キャッシュ済み2回目」の対比にはなっていない
(call1の時点で既にキャッシュが温まっていた)。それでも「同一Ledger
prefixの再利用でキャッシュが機能し、費用が実際に下がる」という
受理可否自体は実測で確認できた。

**[委任_07新規発見、重要]Stage 2較正リスク**: per-claim Stage2
(§4-4確定入力どおり、explanation/severity/10flags除外)で、V4Aが
BLOCKING確定していたB1-c相当claim(HF-009市場動機の断定)・B4-a相当
claim(AIフォールバック機構の新規主張、2件)の**全てがQUALITYへ
降格された**(§7-0の確定ラベルではB1-c/B4-aはRewrite対象の
Real-but-fixable群=BLOCKING期待)。rubric基準1(「Ledgerが別の原因・
主体を明記しているのに異なるものを述べる」)がこれらを捕捉することを
設計は期待していたが、実測ではQUALITY(「Ledgerの観測と矛盾しないが
保証されない関係付け」)側に倒れた。**これはS1-D固有の欠陥ではなく、
Stage2 rubric+§4-4入力制限[explanation/severity/10flags除外、
Opus論点3(A)のanchoring対策]自体の較正課題である可能性が高い**
(S1-D・per-claim Stage2の両方で同一方向の誤判定が独立に観測された
ため)。**現時点でProduction非接続のTrial実装であり、Safety事故には
至っていない**が、Phase 1⑤(Stage3 Rewrite成功率実測)実行時に、
B1-c/B4-a相当のReal-but-fixable群がRewrite段まで到達しない(Stage2で
QUALITY止まりになり、Rewriteが発火しない)事象が再現するかを確認する
必要がある。**新しい仕様候補として報告のみ行い、勝手にrubric文言を
変更しない**(rubric改訂[基準1の文言強化、または§4-3
deterministic floorへchanged_scope/causality/unsupported_new_claimの
一部を追加する等]はUSER_DECISION_REQUIRED相当の設計変更であり、
Phase 1⑤の追加実測結果を待ってFable/ユーザーへ提示する)。

### 4-8. Stage 2 rubric較正Trial実測・確定構成(委任_08)

**位置づけ**: §4-7で発見されたStage2較正リスク(Real-but-fixable群
B1-c/B4-aのQUALITY誤降格)への対応。Fable判定(2026-09-30委任文§1)
「Safety方向の較正であり、Trial専用rubric/rule改善はユーザー指示の
自律範囲」に基づき、rubric較正Trialを実行し確定した(Production
Prompt`er003_v1_en_direct_vfl_01_generate.py`は無変更、Trial限定の
`er052_open233_self_recovery_stage2_calibration_01.py`で完結)。

**variant**: R1=現行rubric(既存出力の再利用、0 call)。R2=較正rubric
(QUALITYを「Ledgerに記録された観測同士の関係付け・強調・言い回し」に
限定し、「Ledgerに存在しない新規の具体的主張[製品・仕組み・動機・
理由・因果・数値・主体・時期]は最優先でBLOCKING」を明文化、batch
callで新規実測)。R3=R2のLLM出力+post-hoc floor(Stage1の
`unsupported_new_claim=true`かつR2の`basis`が`ledger_claim`/
`ledger_scope`/`ledger_conditions`/`notes_for_writer`のいずれでもない
場合、BLOCKINGへ強制。新規callなし)。

**評価セット**: 13 batch call・23 claim(B1[a/b/c]、B2、B3、
B4[a/b/c/d]、Meta_run03_standard[2claim]、hormuz_run03_standard、
negative候補7件中V4A BLOCKした4件、Safety群A2A3/A4/A5)、n=2で
26 call実測。**実測費用¥3.1717**(Guardrail¥12、0 error)。

**結果(claim単位、correct labelは§7-0確定ラベル)**:
- **Safety群(A2A3/A4/A5・Meta・hormuz、7claim×2run=14 instance)**:
  R2で**100%(14/14)BLOCKING維持**(誤降格0件)。
- **§4-7で発見された誤降格claim(B1-c/B4-a/B4-d、3claim×2run=
  6 instance)**: R1では6/6ともQUALITYへ誤降格(0%正解)だったが、
  **R2では6/6ともBLOCKINGへ復帰(100%正解)**。既知の較正課題を解消。
- **ACCEPTABLE群(B1-a/B1-b、2claim×2run=4 instance)**: R2で
  4/4正解(over-block無し)。
- **QUALITY群(B2/B4-b/B4-c、3claim×2run=6 instance)**:
  R2で1/6のみ正解(B2が2試行中1回のみQUALITY、B4-b/B4-cは6/6とも
  誤ってBLOCKINGへ)。**新規のover-block(Productivity低下)を確認**
  (Safety強化の代償としての想定内トレードオフ)。
- **negative群(4 fixture×2run=8 instance、正解=非BLOCKING)**:
  R2で7/8(87.5%)が非BLOCKINGへ復帰(Stage1 V4Aは4/4ともBLOCKして
  いたため、Stage1単体の非BLOCK率0%→R2適用後87.5%)。
- **n=2判定一致率**: claim単位21/23(91.3%)で2試行とも同一ラベル
  (不一致はB2・neg3の各1claim)。

**R3(floor)の評価**: floorは**Productivityを大きく悪化させた**
(B1-b[正解ACCEPTABLE]が2/2ともBLOCKINGへ誤って強制降格、negative
4 fixtureのうち3件で少なくとも1試行がBLOCKINGへ誤って強制される)。
一方、floorが無くてもR2単体で本評価セットのSafety群は100%維持できて
おり、floorを追加する必要性がR2単体の実測で裏付けられなかった。
**理由**: Stage1(V4A)は誤検出(over-detection)claimに対しても
`unsupported_new_claim=true`を高頻度で付与するため(B1-b・negative
候補ともに`unsupported_new_claim=true`)、この生フラグを盲目的な
floor条件として使うと、Stage1側の誤検出をStage2が正しく訂正した
結果までも強制的に上書きしてしまう。

**確定構成(委任_08)**: **R2 rubricを採用し、R3 floor拡張[§1で
Trial対象とした案]は不採用とする**(Safety面でR2単独で本評価セットの
既知miscalibrationを解消でき、floor追加はPositive Safety効果が実測で
確認されずProductivity損失のみが観測されたため)。§4-2のrubric本文を
本節R2の文言へ更新し(`er052_open233_self_recovery_stage2_
calibration_01.RUBRIC_R2`)、§4-3のdeterministic floorは既存6フラグ
構成のまま変更しない。B1-c/B4-aをStage2で降格禁止とするregression
fixtureとして`er052_open233_self_recovery_stage2_calibration_01_
test_01.py`へ追加することを次回実装項目とする(本委任では実測のみ、
テスト追加は次回)。**新規の残存課題(報告のみ)**: B4-b/B4-c型
(Ledgerが確認した事象への一般論だが、Ledgerに無い一般的心理・因果を
述べる境界事例)のover-block率が高い(0/6)。これはSafety側には
振れていない(BLOCKINGはRewrite対象になるだけで誤って記事を止める
わけではないため過剰品質コストの範疇)が、Productivity指標として
継続観察が必要(Phase 2候補)。詳細ログ:
`er052_output/open233_self_recovery_stage2_calibration_01/
summary_stage2_calibration.json`。

## 5. Stage 3 Automatic Rewrite設計

### 5-0. 既存機構棚卸しの統合(委任_05/_06、三分類表)

**参照**: `docs/pm/inventory_local_rewrite_mechanisms_open233_01.md`
(委任_05、read-only調査、¥0)。既存Rewrite関連機構18件を、KPI
(Safety/Escalation/Cap)とQCD(cost/latency/実装リスク)の両観点で
「(A)そのまま再利用」「(B)拡張・改善して利用」「(C)今回KPIには
不適→新方式」の三分類へ整理する(ユーザー指示: 既存資産の無視も
既存方式への束縛も避け、QCD上より良い方法があればTrialする)。

| # | 機構 | 分類 | 理由(KPI/QCD) |
|---|---|---|---|
| 1 | EN Ledger Deviation Checker本体(`vfl01.run_deviation_check`) | (A)そのまま再利用 | Safety資産(Prompt/schema)を保存する設計原則そのもの。Stage 1/Recheckが直接呼ぶ。変更するとSafety regressionリスクが即座に生じる |
| 2 | EN 文単位Local Rewrite primitive(`er010`) | (B)拡張して利用 | 文特定・3段階escalation・差分QA・target-sentence-matchingは実装済み・実データ検証済みでQCD上安価(新規実装よりcost/リスクが低い)。rewrite_kind対応等の薄い拡張のみで足りる(§5-2 E-1) |
| 3 | EN Local Rewrite cycle制御(N3-01直接生成) | (C)新方式 | cycle上限(3回)・呼び出し規約がFamily B系専用の前提であり、Self-Recovery Flowのcycle上限(2、Stage2経由必須)と両立しない。流用すると上限混在のSafetyリスクを生む |
| 4 | EN Local Rewrite cycle制御(Family B generic writer) | (C)新方式 | 同上(#3と同一理由) |
| 5 | Family X EN 全文must-fix retry(Standard) | (A)そのまま再利用 | 既にProduction稼働中。局所Rewrite cycle上限到達時のフォールバックとして位置づけを変えず流用(§5-3) |
| 6 | Family X EN 全文must-fix retry(Advanced) | (A)そのまま再利用 | 同上 |
| 7 | Family X/E オーケストレーション(`_must_fix_from_deviations`ほか) | (B)拡張して利用 | 既存の呼び出し規約を保った上で、origin別Stage3分岐・cycle上限管理を追加する必要がある箇所 |
| 8 | JA Original/R2 must-fix全文(段単位)retry | (A)そのまま再利用 | 既にProduction稼働中。paired local rewrite(J-1/J-2)のguard抵触時フォールバックとして流用(§5-4) |
| 9 | JA→EN不整合時の「案B」(JA全文差し戻し) | (B)拡張して利用 | 発火条件を「Stage 2 BLOCKING確定後」へ限定し直す(既存は無条件発火)以外はProduction codeをそのまま使う |
| 10 | Family X構造Gate(`split_family_x_article_text_v2`) | (A)そのまま再利用 | 局所Rewrite後の構造検証guardとしてそのまま再実行するだけで足りる(§5-2/§5-4) |
| 11 | TTS発音NGspan Local Rewrite(`er020`) | (C)新方式(別ドメイン) | 発音・ASR比較が目的でFact逸脱とは無関係。ただしfail-closed設計思想(原文復帰・Human Review Lock)は§5-5で継承する |
| 12 | TTS Local Rewrite原型(cooldown) | (C)新方式(別ドメイン) | 同上(#11の移設元、参照のみ) |
| 13 | TTS 7-Gate自然英語QA原型 | (C)新方式(別ドメイン) | 同上 |
| 14 | Full Story専用TTS Local Rewrite回復 | (C)新方式(別ドメイン) | 同上(#11の呼び出し元の1つ) |
| 15 | Local Rewrite差分QA(`run_diff_qa_for_accepted_rewrite`) | (A)そのまま再利用 | 受理直後の¥0近い追加安全確認として既に確立済み(§5-5) |
| 16 | Local Rewrite原型ルール策定Trial(歴史、er009系) | 対象外 | 既に#2へ統合済みの過去Trialであり、再利用対象ではない(参考記録のみ) |
| 17 | Local Rewrite再利用のEvidence確認Script | 対象外 | #2の検証記録であり機構そのものではない |
| 18 | En ASR意味的同等性チェッカー | (C)新方式(別軸) | TTS後の発音検証でありLocal Rewriteの入力にならない |

**二重実装リスクへの対処**: 棚卸し§4で指摘された「Family Xに新規
Local Rewriteモジュールをゼロ設計するとer010と機能重複する」リスクは、
上表(B)分類(#2/#9)を「拡張」として位置づけることで解消する(新規
モジュール名を先に確定せず、既存資産への薄い拡張として実装する)。
優先順位(局所Rewrite第一→cycle上限到達時のみ既存の段単位/全文
must-fix retryへフォールバック→それでも解消しなければNG_REVIEW_
REQUIRED)は§5-3で維持する。

### 5-1. 段階別方針

**JA側(origin=ja_source)**: 既存案B(`er012_e_family_entertainment_
two_level_runner_01.py::run_writer_stage()`のJARecheckRequiredError
捕捉→`jaw.run_ja_writer_o_r1_r2()`をmust_fix付きで実行→Original→
R1→R2→JA Fact Checkの全体を再生成)を**Phase 1のJA側Rewrite実装として
そのまま再利用**する(コード変更なし、既にProduction code)。この経路
はStage 2のBLOCKING確定を経てから発火する点が既存案Bとの違い(既存は
Stage 2を経由せず、ja_source MAJORが検出された瞬間に無条件で発火)。

**局所Rewrite候補 → [委任_04改訂/A4] Phase 1の第一級実装項目へ繰り上げ**:
現行案Bは「Original段の該当claimに関する箇所だけ」をmust_fixで指定
しつつも、Original→R1→R2の全段を再生成するため、**該当claimと無関係な
箇所まで変わり得る**(Hormuz run_03で、Advanced側は案Bで解消したのに、
Standard側で全く別のclaim[HF-009関連]が新規にja_source MAJORとして
検出された事例は、この「全文再生成が新しい逸脱を生む」リスクの実例)。
実測ではBLOCK事象5件中4件(80%)が`origin=ja_source`であり(Opus所見
論点1(A))、JA全文再生成(¥3.5〜4.0)がJA側の唯一の回復手段である限り
Cap内でEscalationゼロは達成できないと判断した。そこで、より局所的な
**paired local rewrite**(該当JA 1文±1文とそれに対応するEN文を同一の
`rewrite_hint`で局所編集する案)を**Phase 1で新規実装・検証する第一級
項目**へ格上げする(旧: Phase 1スコープ外→Phase 2改善候補)。詳細設計は
新設§5-4。JA Original段のうち該当paragraphのみをmust_fixで再生成し
他paragraphはR1/R2をスキップする案(旧提案)は、JA Writer Oの既存構造
(Original→R1→R2は文体洗練の連鎖であり、paragraph単位の部分スキップは
現行実装に存在しない)を変更する必要があるため引き続き不採用とし、
**§5-4のpaired local rewrite(R2本文を直接局所編集し、Original→R1→R2の
連鎖には触らない)を代替案として採用する**(この障壁を回避できる、
Opus論点1推奨1)。§5-4のguard抵触時は、本節末尾(案B)を**フォール
バック**(記事あたり1回)として位置づけ直す。

**EN側(origin=translation、Advanced/Standard内で新規に生じた逸脱)**:
現行Productionの「must-fix retry 1回」(`adv_gen.generate_family_x_
faithful_translation(..., must_fix=...)` / `std_gen.generate_family_
x_standard_a2_no_heading(..., must_fix=...)`)は**全文再生成**であり、
局所編集ではない。Self-Recovery Flowでは、これを**Phase 1のbaseline**
として維持しつつ(実装コストゼロ、既にProduction code)、**局所Rewrite
を優先候補として設計する**(以下)。

### 5-2. 局所Rewrite(EN側、設計提案。Phase 1 Trialで新規実装・検証対象)

**[委任_06新設]** 本節はEN局所Rewriteの**既存ベース改善案(E-1)**を
記述する(以下本文はE-1そのもの、委任_04時点の記述を維持)。これとは
別に、**新方式案(E-2)**を§5-2-補で提示し、Phase 1 ⑤で同一fixtureに
対しE-1/E-2を実行し実測比較する(§5-0の棚卸し結論=#2「拡張して利用」
に対応する具体案がE-1、二重実装を避けつつQCD上より良い可能性を検証
する対照案がE-2)。

**[委任_04改訂/A4]** 本節のEN局所Rewriteは**`origin=translation`の
claimにのみ適用する**。`origin=ja_source`のclaimには適用しない(EN側
だけを書き換えるとJA本文とEN本文が意味的に乖離し、誰も検査しない
JA/EN不整合を生む、Opus論点1(A)・論点4【Safetyリスク】)。Rewrite
mechanismの選択は**cycle indexではなくclaimの`origin`で決める**(§5-3
改訂)。`origin=ja_source`の場合は§5-4のpaired local rewriteまたは
本節末尾(旧案B、フォールバック)を使う。

- **入力**: 記事全文のうち、Stage 2の`rewrite_hint`が指す該当claimを
  含む文±1文のみを抽出し、そのローカルcontext・**[委任_04改訂/A11]
  Ledger全文**(該当箇所だけではない。B3型のように別条件が離れた箇所に
  あるケースを見逃さないため、fail-closed優先でStage 2と同じ入力方針に
  揃える、Opus論点4推奨3)・`rewrite_hint`・`rewrite_kind`(§4-5)を
  渡して**その部分だけ**の書き換え文を生成させる。記事の他の部分は
  一切渡さず、生成後にプログラム側で文字列置換する(LLMに全文を
  書き直させない)。`rewrite_kind=="delete"`はまずLLMを経由せず該当
  文字列の決定論的削除を試みる(§4-5追記)。
- **利点**: 全文再生成による「無関係箇所での新規逸脱」を構造的に
  防げる可能性がある。**[委任_04改訂/A4]** ただしOpus論点4(B)の指摘
  どおり、Hormuz run_03の新規MAJORは「全文再生成が新逸脱を生んだ」
  例ではなく「JA上流の総取り替えが下流を全変化させた」例であり、局所
  Rewriteの真の利点は**新逸脱抑制ではなくコスト削減とJA/EN整合維持**
  と位置づけ直す。
- **guard(構造破壊防止)**: 置換後、既存`sc.split_family_x_article_
  text_v2()`のNG条件(`TOO_FEW_PARAGRAPHS`/`NG_MISSING_TITLE`/
  `NG_MISSING_IN_ONE_LINE`/`NG_HEADING_IN_BODY`)をそのままguardとして
  再利用する。**[委任_04改訂/A11]** 置換後にNGが出た場合の扱いを次の
  段階的フォールバックへ変更する(Opus論点4推奨4、旧「cycle消費+
  Stage4直行」は過剰に厳しいため): (1) 置換を破棄し元の全文へ戻す
  (¥0)、(2) 同一cycle内でrewrite再生成を1回だけ再試行、(3) それでも
  NGなら既存全文must-fix retry(既存Production機構)へフォールバック、
  (4) それも失敗した場合のみcycleを1消費してStage 4へ進む(段落数retry
  [既存の別axis、1回]は温存し、軸を混在させない)。
- **rewrite後の機械検証(§4-5追記、Opus論点5推奨3)**: `rewrite_kind==
  "delete"`は当該文字列の消滅を、`"replace_with_ledger_value"`は
  Ledger値の出現を、Recheck前にプログラム側で機械確認する。
- **Recheckの範囲**: **全文Checker(fail-closed推奨)**。局所編集の
  範囲だけを再チェックする案(コスト減)も検討したが、Stage 1 Prompt
  は記事全文とLedger全文を突き合わせる設計であり、局所的な再チェック
  用の別Promptを新設すると「新しいPromptがSafety regressionを生む」
  リスクをStage 2に続いて二重に抱えることになるため、**Phase 1では
  採用しない**(全文Checkerを毎回フルで再実行する。コスト増だが
  Safety最優先)。

### 5-2-補. EN局所Rewrite 新方式案(E-2、[委任_06新設]、Phase 1 ⑤で
E-1と比較実測対象)

E-1(§5-2、er010拡張)は3種の`rewrite_kind`すべてを同一のLLM局所
Rewrite callで扱う設計だが、E-2は`rewrite_kind`ごとに手段を分離し、
「LLMを使う範囲を最小化する」方向でE-1と対照的な設計にする。

- **`delete`型**: LLMを一切経由しない。Stage 2の`rewrite_hint`が指す
  対象文をプログラム側で直接削除する(該当文をピリオド区切りで特定し、
  `article_text.replace(target_sentence, "", 1)`相当。E-1もdelete型は
  既にLLM非経由だが[§4-5]、E-2は「削除後に前後の接続詞・代名詞の
  不整合[例: 削除した文を受ける"This"が次文に残る]をチェックする」
  軽量な決定論的後処理[代名詞・接続詞で始まる次文を検出したら該当文も
  併せて再確認対象にするフラグ立てのみ、書き換えはしない]を追加する
  点がE-1との差)。
- **`replace_with_ledger_value`/`narrow_scope`型**: E-1(§5-2)と同じ
  「文±1文+Ledger全文+rewrite_hint」の入力方針は共有するが、**Prompt
  自体を最小化**する(E-1はer010の3段階escalation[attempt1→2→3で
  情報を段階的に追加]をそのまま流用するため、1回で解決しない場合に
  平均call数が増える設計。E-2は"issue+rewrite_hint+rewrite_kind+
  Ledger該当箇所"を1回のPromptで全て提示し、escalationという段階構造
  自体を持たない[1回で解決しなければ即座に既存全文must-fix retryへ
  フォールバック、cycle消費は据え置き])。
- **狙い**: (a) delete型の後処理追加でE-1が拾わない「削除後の文脈破綻」
  を安価に補強できるか、(b) escalationを持たないシンプルなPromptで
  E-1と同等の解決率を、より少ないcall数(=より低いlatency/cost)で
  達成できるか、の2点をPhase 1 ⑤で実測する。
- **リスク**: 段階的escalationを持たないため、1回で解決しない場合の
  救済手段がE-1より弱い(即フォールバックのみ)。Safety面はE-1と同じ
  guard(構造Gate再確認・機械検証・全文Recheck)をすべて共有するため、
  Safety規性には差が生じない設計とする(差が出るのは解決率とcostのみ)。
- **採否**: Phase 1 ⑤の実測(型別成功率・実単価・guard抵触率・
  フォールバック発生率)をもってE-1/E-2のどちらを本採用候補とするか
  確定する(本節時点では両論併記、決定しない)。

### 5-3. loop上限・順序

- 記事あたり最大2 cycle(§3-5)。**[委任_04改訂/A4]** Rewrite
  mechanismは**cycle indexではなく、対象claimの`origin`で選ぶ**:
  `origin=ja_source`→§5-4のpaired local rewrite(guard抵触時のみ
  旧案Bへフォールバック)、`origin=translation`→§5-2のEN局所Rewrite。
  同一記事で**旧案B(JA全文Rewrite)を2回使わない**という既存のコスト
  guardは維持する(1 cycle目でフォールバックとして旧案Bを使った場合、
  2 cycle目でja_source claimが新規発生してもpaired local rewriteを
  優先し、それも失敗した場合のみ§10リスク9のworst caseガードに従い
  Stage 4へ進める)。
- **[委任_04改訂/A5]** cycle 2の発火条件に「cycle 1でBLOCKING確定した
  claim/fact_idとは異なるclaim/fact_idであること」を追加する(§3-3
  STOP条件参照)。同一claim/fact_idの再BLOCKINGはRewriteが効かなかった
  ことの実証であり、cycle残数があっても即Stage 4へ進める(無駄な追加
  投資をしない、Opus論点7推奨1)。
- Rewriteは常にStage 2でBLOCKING確定した後にのみ実行する(Stage 2を
  経ずに即Rewriteしない。これにより「本当にmaterialか」を必ず一度
  問い直してから書き換えるため、無駄なRewrite回数を削減する)。

### 5-4. paired local rewrite(JA側、[委任_04新設/A4]、Phase 1で新規
実装・検証対象)

**[委任_06新設]** 本節は既存に文単位JA Local Rewrite機構が無いことを
前提に、er010の骨格(文特定+3段階escalation+差分QA+cycle制御)を
日本語向けに薄く移植する**新設案(J-1)**を記述する(以下本文はJ-1
そのもの、委任_04時点の記述を維持、§5-0棚卸し結論#9に対応)。これとは
別に、新規モジュールを増やさない**代替案(J-2)**を§5-4-補で提示し、
Phase 1 ⑤でJ-1/J-2を同一fixtureに対し実行し実測比較する。

**位置づけ**: `origin=ja_source`のclaimに対する第一候補のRewrite手段
(§5-3)。既存案B(JA全文差し戻し、¥3.5〜4.0)は「guard抵触時の
フォールバック(記事あたり1回)」に格下げする。目的は(1) コスト削減
(概算¥1.0〜1.5/cycle、案Bの1/3以下)、(2) JA/EN乖離の防止(EN局所
Rewriteをja_source claimに使わないことの代替手段を提供する)。

**入力**:
- 該当claimに対応するJA本文(R2段)の該当1文±1文。
- 対応するEN文(Advanced/Standardのうち発火元)±1文。
- Ledger全文(該当箇所だけでなく全文、fail-closed優先。他のRewrite
  経路[§4-4/§5-2]と同じ方針)。
- Stage 2の`rewrite_hint`/`rewrite_kind`(§4-5)。

**編集方式**: JA Writer Oの既存構造(Original→R1→R2は文体洗練の連鎖)
には触らず、**R2確定後の本文を直接局所編集する**(部分スキップという
新しい制御構造を導入しない。§5-1で述べた旧提案の障壁を回避)。同一の
`rewrite_hint`でJA文とEN文を同時に編集し、両者の整合を維持する。

**Fact Check/Deviation Check**:
- JA側: 編集後のJA全文に対し`vfl01.run_deviation_check`相当を**1
  call**実行し、Ledgerとの整合を確認する(局所編集のみを見るのではなく
  全文、fail-closed優先)。
- EN側: 編集後のEN全文に対し既存Deviation Check(Stage 1 Recheck)を
  **1 call**実行する(§3-0の全体Recheckに統合、追加callではない)。

**guard(構造破壊防止、既存Gateの再利用)**:
- 文体Gate: JA Writer Oの既存文体検証(Original/R1/R2各段のvalidator)
  を局所編集後の全文に対して再実行する。
- 記号Gate: 既存`JAFactCheckStopError(stage="original_symbol"/
  "r2_symbol")`相当の音声化禁止記号チェックを再実行する。
- 段落数Gate: 既存`sc.split_family_x_article_text_v2()`のNG条件を
  EN側の局所編集結果に対して再実行する(§5-2と同一)。

**Recheck**: 全文Checker(Stage 1 Recheck、§3-0)で判定する。JA側は
上記JA Deviation Check 1 callの結果、EN側はStage 1 Recheckの結果を
両方確認する。

**上限**: 記事あたりcycle上限(最大2)の範囲内。paired local rewriteの
guard抵触(文体/記号/段落数いずれか)時は、§5-2と同じ段階的フォール
バック(置換破棄→同一cycle内1回再試行→旧案B[JA全文差し戻し]へ
フォールバック→それも失敗でStage 4)を適用する。旧案Bは記事あたり
最大1回(既存の「1回上限」思想を維持)。

**実装リスク(未検証、Phase 1で新規実装)**:
- JA本文の局所編集関数自体が新規実装であり、既存のJA Writer O
  paragraph構造との整合(文脈保持・助詞接続等)は前Phase・本Phase
  いずれの実測にも存在しない。
- 文体Gate/記号Gate/段落数Gateを局所編集後の**全文**に対して正しく
  再検証できるかは未検証(既存Gateは全文生成後の検証を前提に実装
  されているため、局所編集後の全文に対してそのまま適用できるかの
  確認が必要)。
- JA/EN双方を同一`rewrite_hint`で編集する際、両言語間で編集内容が
  意味的に一致することを機械検証する手段が現時点で無い(Recheckが
  Ledgerとの整合は見るが、JA↔EN整合そのものは見ない、Opus論点1(A)の
  指摘の裏返し)。Phase 1では人手併用ではなくRecheck結果とdiffログの
  記録による事後観測に留める(Guardrail内の暫定対応、完全な解決策では
  ないことを明記)。

**Phase 1測定項目**: 型別(delete/replace_with_ledger_value/
narrow_scope)成功率・実単価・guard抵触率・フォールバック発生率
(§9-1⑤)。

### 5-4-補. JA局所Rewrite 代替案(J-2、[委任_06新設]、Phase 1 ⑤で
J-1と比較実測対象)

J-1(§5-4)は新規モジュール(日本語文分割+対象文特定)を実装するが、
J-2は**新規モジュールを一切増やさず**、既存の「JA must-fix(全文、
`original_must_fix`引数)」に「対象文のみ修正・他は一字も変えない」という
局所指示を追加するだけで代替できないかを検証する。

- **入力**: 既存のJA Original段`build_must_fix_block`が受け取る
  `must_fix`引数へ、Stage 2の`rewrite_hint`(対象claim・修正方針)に加え
  「この指摘に対応する一文だけを修正し、他の文は一字も変更しないこと」
  という制約文を追加する。Original→R1→R2の既存カスケードはそのまま
  実行する(J-1と異なり部分スキップという新しい制御構造を導入しない、
  既存Gateの通過実績をそのまま使える)。
- **利点**: (a) 新規モジュール(文分割・対象文特定・差分QA)を実装
  しないため実装リスク・検証コストがJ-1よりはるかに小さい、
  (b) 既存の文体Gate/記号Gate/段落数Gateを無改造でそのまま通過できる
  ことが保証されている(J-1は局所編集後の全文に対してこれらGateが
  正しく再検証できるか自体が未検証、§5-4実装リスク参照)。
- **欠点**: 出力が全文(Original→R1→R2の再カスケード)であるため、
  cost自体は旧案B(全文差し戻し)に近い(J-1が狙う¥1.0〜1.5/cycleの
  コスト削減効果は得られない)。「対象文以外は変えない」という指示が
  LLMに厳密に遵守される保証はなく、Fact Check/再英訳の再抽選(Advanced/
  Standardの再生成)は避けられない点もJ-1(該当stageのみの局所編集)に
  劣る。
- **狙い**: Phase 1 ⑤で、J-1の実装コスト・guard抵触率と、J-2の
  cost・「本当に対象文以外が変わらないか」の実測diff率を比較し、
  QCD上どちらが本Phaseの規模(Family X限定Trial)に見合うかを判断する
  材料にする。
- **採否**: 本節時点では両論併記、決定しない(Phase 1 ⑤実測後に確定)。

### 5-4-補2. Phase 1 ⑤実測: rewrite_kind別成功率(委任_08、E-1/E-2/J-1/J-2)

**スコープ確定(委任_08時点の判断)**: §5-2の「EN局所RewriteはOrigin=
translationのclaimにのみ適用」・§5-1の「origin=ja_sourceはJA側
Rewriteを使う」という既存の経路選択ルールに従い、型ごとの担当経路を
次のとおり確定した(delete型3claimはいずれもorigin=ja_source相当の
ため決定論的削除の成否のみを共通baselineとして測定し、E-1/E-2の
機構差はreplace_with_ledger_value型で、J-1/J-2の機構差はnarrow_scope
型で検証する、これが実際に手法が分岐する型であるため)。

**(a) delete型baseline(B1-c[JA]/B3[EN]/B4-a[EN]、決定論的削除、
Recheck 1call/claim、計3call・¥1.0778)**: `locate_target_sentence`
(er010既存、fallback overlap方式)で対象文を特定し文字列削除、
Recheckで確認。**B3(単一deviation記事)は削除のみでLEDGER_COMPLIANT
達成(resolved=True)**。**B1-c/B4-a(いずれも同一記事内に他の
BLOCKING claimが複数存在する記事[B1=2claim、B4=4claim])は記事全体
Recheckが引き続きLEDGER_DEVIATIONを返した(resolved=False)**が、
これは対象claim以外の**未処理の別claimが記事に残っているための
記事レベルの結果**であり、削除自体が対象claimの問題を解消したかは
本実測の粒度(記事全体Recheckのみ)では独立に確認できていない
(claim単位の再出現有無を見るには、Recheckのdeviations配列を
claim単位で照合する追加実装が必要、次回実測項目の候補として記録)。
E-2の追加後処理(削除箇所付近の代名詞・接続詞検出、¥0)は全3件で
実行し、B1-c(「これ」「その」「この」)・B3(that/it/so)・B4-a
(this/that/it/so)いずれも記事全体では該当語が検出された(削除箇所
直後の文に限定した厳密な照合ではなく記事全体走査のため、削除と無関係な
箇所の一致を含む可能性が高く、Trial観測値としての精度は限定的)。

**(b) replace_with_ledger_value型(er009_changed_actor/changed_number、
origin=translation相当、E-1 vs E-2、計4claim実行[各claim×2手法]・
8call・¥0.4913)**: **両claim・両手法とも1 attempt目でresolved=True・
machine_verified=True(4/4=100%)**。E-1(er010.rewrite_ng_item、
既存3段階escalation骨格そのまま呼び出し)はchanged_actorで実在の
研究者名(Kareem Haggag and Giovanni Paci、Ledgerのsource行から)を
補って書き換え、E-2(最小1-shot Prompt)は`Researchers`という中立語へ
置換した。両手法ともescalationは発火せず(1 attemptで解決)、
**cost差は僅少**(changed_actor: E-1 ¥0.1828 vs E-2 ¥0.1735、
changed_number: E-1 ¥0.0949 vs E-2 ¥0.0906)。本実測範囲(n=2claim)
では**E-1の3段階escalation機構は発火せず、E-2の単純1-shotで同等の
解決率・同等コストを達成**した(escalationの真価はより解決困難な
claimでのみ発揮される可能性があり、本実測では判別できない)。

**(c) narrow_scope型(hormuz_run03_standard HF-009、origin=ja_source、
J-1 vs J-2、計7call・¥1.4167)**: **J-1(paired local rewrite、JA文
±1+EN文±1を1callで同時編集→JA Fact Check[V4A variant代用]1call+
EN Recheck[同]1call)がJA Check・EN Recheckとも`LEDGER_COMPLIANT`を
達成し、hormuz narrow_scope claimを完全に解消した(resolved=True、
対象文以外のJA文への影響=0を機械diffで確認、cost=¥0.4569・3call)**。
**J-2(既存方式に近い代替、JA全文を「対象文以外は一字も変えない」
指示付きで全文regen→対象文相当箇所を再翻訳→EN Recheck)は、JA Check
は`LEDGER_COMPLIANT`だったが、EN Recheckが`LEDGER_DEVIATION`のまま
残り、resolved=False(cost=¥0.9598・4call、J-1の約2.1倍)**。加えて
機械diff(非対象文の集合比較)で**非対象文1件の変化を検出**
(n_orig=20→n_upd=21、symmetric diff=1)。J-2は「対象文以外は一字も
変えない」と明示指示したにもかかわらず、全文regenという性質上、
軽微な drift が実際に発生することを実測で確認した。

**結論(採用案)**: **narrow_scope型はJ-1を採用候補とする**(cost・
解決率・JA/EN整合[drift 0件]のいずれでもJ-2を上回った)。
**replace_with_ledger_value型はE-1/E-2いずれも同等の性能(本実測範囲
では差が付かず)であり、実装コスト・保守性(E-2は3段階escalation
骨格を持たずコードがより単純)を考慮するとE-2を第一候補とし、E-1を
「E-2で1 attempt目に解決しない場合のfallback」として位置づける
両論併記を維持する**(n=2という小標本のため、より解決困難なclaimでの
追加実測[Phase 2候補]でE-1のescalationが真に必要になるケースが
無いかを確認してから最終確定する)。

**[重要、委任_08の主要な問いへの回答]hormuz narrow_scopeの解消可否**:
**J-1により解消可能であることを実測で確認した**(§13-10課題2で
「Cap超過リスク」として記録されていたhormuz型の解決手段が、Phase 1⑤
実測で実証された)。「どちらの手法でも解消できない」という最大リスク
シナリオは本実測では回避された。

**実装スコープ上の限界(次回実装時の課題として明記)**:
- 本実測のJ-1/J-2の「JA Fact Check」「EN Deviation Check(Recheck)」は、
  真のProduction JA Fact Check(`er002_ja_web_research_r3`系、
  web_search併用)・真のJA Writer O cascade
  (`er019_family_x_ja_writer_o_r1_r2_01.py`、Original→R1→R2)は
  一切呼び出さず、既存V4A variant checker(`er051_open233_checker_
  trial_variant_01.run_trial_deviation_check`)をJA/EN両方の文面に
  適用する近似で代用した(読み取り専用の遵守・予算/実装時間制約に
  よる意図的なスコープ縮小、Production非接続であることは維持)。
  §5-4が要求する「句点分割移植」相当の汎用JA文分割モジュールも、
  本Trialでは対象文を直接指定する簡易実装に留めた(delete型B1-cの
  `locate_target_sentence`[英語文末記号ベースの正規表現]がJA全文を
  1文として誤認識する不具合を実地で確認、§5-4の課題認識が実測で
  裏付けられた)。真のJ-1/J-2実装(Production配線候補とする場合)は、
  上記2点([1]真のJA Fact Check/JA Writer O連携、[2]汎用JA文分割
  モジュール)を別途実装する必要がある。
- delete型のclaim単位再出現確認(記事全体Recheckではなく、対象claimの
  issueが個別に再検出されるかを見る)は本実測で未実装(次回実測項目)。

詳細ログ: `er052_output/open233_self_recovery_stage3_rewrite_trial_01/
summary_stage3_rewrite_trial.json`。

### 5-5. 継承するguard/retry/再検証(棚卸し§3の統合、[委任_06新設])

E-1/E-2・J-1/J-2いずれの案を採用する場合でも、以下は既存資産からの
継承として維持する(独自の新しい安全装置を発明しない、
`docs/pm/inventory_local_rewrite_mechanisms_open233_01.md`§3準拠)。

1. **対象はMAJORのみ**。MINORは記録のみで対象外(er010既存方針)。
2. **文単位retry上限3回+記事全体cycle上限の二軸独立カウンタ**
   (E-1/J-1のattempt escalationに適用。ただしSelf-Recovery Flow全体の
   記事cycle上限は§3-5の2回を優先し、er010固有の`MAX_REWRITE_CYCLES=3`
   はE-1/J-1内部のattempt軸としてのみ使う。二重の上限概念を混同しない)。
3. **受理直後の差分QA**(`run_diff_qa_for_accepted_rewrite`/
   `apply_diff_qa_to_resolved_rewrite`、Fact Checker A' web_search +
   Ledger再確認)を、E-1のRewrite受理後に適用する(J-1/J-2は同型のJA版
   差分QAが無いため、Phase 1では全文Recheckの結果とdiffログの事後観測に
   留める、§5-4実装リスク参照)。
4. **ambiguous時はwindow全体判定へ安全側フォールバック**
   (`evaluate_target_sentence_status`のtarget-sentence-matchingロジック、
   隣接文の逸脱に対象文のRewriteが誤ってblockされないようにする一方、
   対象文自体の判定が曖昧な場合は安全側[window全体]で判定する)。
5. **置換失敗時は原文復帰**(TTS Local Rewrite[#11]のfail-closed思想。
   E-1/E-2のguard抵触時「置換を破棄し元の全文へ戻す」[§5-2 (1)]、
   J-1/J-2のguard抵触時の段階的フォールバック[§5-4]は、いずれもこの
   思想を踏襲する。silent failで出荷しない)。
6. **`prior_issues`による個別解消確認**(既存Family X `must-fix
   retry`[#2.2、`run_deviation_check(..., prior_issues=...)`]の
   インターフェースをStage 1 Recheck全体[§3-0 A1]へ統合する)。

## 6. Stage 4 Escalation条件と人間への提示情報

### 6-1. Escalation条件

- Stage 3が2 cycleを使い切った後もStage 1 RecheckでBLOCKING-candidate
  が残る。
- JA Fact Check自体がSTOP(`JAFactCheckStopError`、既存の独立した
  fail-closed機構)した場合は、Stage 3のcycle上限を待たず即Escalation
  (これは「JA差し戻し後の再生成がそもそも安全な文章を作れなかった」
  という、Rewriteの土台自体が壊れているケースであり、Rewriteを重ねる
  対象ではない)。
- Stage 2が「判断不能」(materiality判定自体がスキーマエラー・
  API失敗等)を返した場合も、fail-closedでBLOCKING確定として扱い、
  Stage 3へ進める(Escalationの直接理由にはしない。Stage 3 cycleの
  中で吸収する)。
- **[委任_04改訂/A1]** Stage 1 Recheckで`overall_status==
  LEDGER_COMPLIANT`だが`all_prior_issues_resolved==False`の場合は
  BLOCKING-candidate扱いとし、cycle残数があればStage 2へ、枯渇して
  いればStage 4へ進める(§3-0参照。既存Production gateと同一の
  厳しさを維持、Opus論点5推奨1)。
- **[委任_04改訂/A7]** cycle 1と同一のclaim/fact_idが再度BLOCKINGに
  なった場合は、cycle残数に関わらず即Stage 4(§3-3/§5-3参照、Opus
  論点7推奨1)。
- **[委任_04改訂/A7]** `assert_budget_ok()`(既存Production予算abort、
  `er012_...py` L455/L547)がtripした場合は即Stage 4(Rewrite/Recheckを
  重ねる前に予算超過を検知した時点で停止、Opus論点1(D))。
- **[委任_04改訂/A7]** Stage 1(初回またはRecheck)のAPI呼び出し自体が
  失敗、またはschemaパース失敗した場合は、**fail-closedとして
  BLOCKING-candidate扱いでStage 2へ強制送付**する(「deviationなし」
  として無検査で通さない、Opus論点5推奨4)。cycle残数が枯渇していれば
  Stage 4。

**[委任_04新設/A7] Stage 4到達理由とコード上の例外型・条件の対応表**
(Phase 1観測項目として必須、Opus論点1推奨3):

| Stage 4到達理由(区分) | 対応する既存コード/条件 |
|---|---|
| cycle上限(最大2)使い切ってもBLOCKING | 本設計のcycle counter(新規実装) |
| JA Fact Check自体がSTOP | `JAFactCheckStopError`(`stage="original"` / `"r2"` / `"original_symbol"` / `"r2_symbol"`、`er019_family_x_ja_writer_o_r1_r2_01.py` L276-344) |
| `all_prior_issues_resolved==False` | `vfl01.run_deviation_check(..., prior_issues=...)`の返り値(`er003_v1_en_direct_vfl_01_generate.py` L649-656) |
| 同一claim/fact_id再BLOCKING | 本設計のclaim/fact_id比較ロジック(新規実装、§3-3/§5-3) |
| 予算abort | `assert_budget_ok()`(`er012_...py` L455/L547) |
| Stage 1 API/schema失敗 | 既存の例外処理(呼び出し元でのtry/except、fail-closedとして本設計で明示追加) |
| 段落数retry枯渇後のNG | `_family_x_ensure_split_or_paragraph_retry`1回上限後のNG(`er012_...py` L294-325、L408-414/L502-508) |

### 6-2. 人間へ渡す情報(一意に確認できる形)

- `article_id`/`writer_stage`/該当claim本文/該当fact_id/Stage 1の
  10 flags/Stage 2の`materiality`+`basis`+`rewrite_hint`(cycle 1・2
  両方)/Stage 3で実際に何を書き換えたか(diff)/Recheck結果(cycleごと)。
- 「なぜ自動回復できなかったか」の一文要約(例: 「cycle 2回とも
  Rewriteで別のBLOCKINGを誘発した」「JA Fact Check自体がSTOPし
  Rewriteの土台が作れなかった」等、パターン別の定型文)。
- 「人間が確認すべき一意の問い」: 該当claimをどう修正すべきか
  (Ledgerのどのfactに合わせるべきか)、または当該記事全体を作り直す
  べきか、の二択を明示する。

## 7. Trial上の正解ラベル(claim単位、最終到達状態ベース)とfixture群の再編

**位置づけ・用語(委任_03で全面改訂)**: 本節は「gold」という語を使わず
**「Trial上の正解」「正解ラベル」**で統一する(前Phase文書
[`design_open233_checker_redesign_trial_01.md`等]は変更しない。用語
統一は本書と本Phase REPORTの範囲のみ)。**claim単位で評価する**
(fixture単位ではない。1 fixture=1記事に、許容すべきclaimとBLOCKING
すべきclaimが混在するB1/B4のような例があるため)。以下は
`design_open233_checker_redesign_trial_01.md`§2(fixture単位)・§2-補
(claim単位、Opus L2レビュー#1論点2の独立評価)を、ユーザー確定事項
(B2=QUALITY、B3=BLOCKING、B1/B4=claim単位で混在)と統合し、**確定
ラベル**を付けたものである。**claim単位の正解ラベル整理はユーザー
承認済み(2026-09-30委任文§1・§4)。KPI(Primary=USER_DECISION_REQUIRED
0件、Safety=重大Fact見逃し0件)の意味は変えていない**(既存fixture単位
表・§2-補claim単位候補表そのものを上書きするのではなく、Self-Recovery
Flowの評価用に確定ラベルを付与する新しい層)。

### 7-0. claim単位 確定ラベル表

| claim | 確定ラベル | fail-closed側に倒したか | 根拠(要旨) |
|---|---|---|---|
| B1-a(ホルムズ海峡=重要航路) | **ACCEPTABLE** | いいえ | 地理的一般常識、新規固有名詞・数値・主体を加えない(Opus論点2一致) |
| B1-b(原油高→ガソリン等波及) | **ACCEPTABLE** | いいえ | 条件付き一般経済常識、`observation_consistent=true`実測済み |
| B1-c(市場動機・価格回復理由の断定) | **BLOCKING** | いいえ(Opus評価どおり) | HF-011 notesが因果推論を明示禁止、主要Fact理解(なぜ価格が戻ったか)を変える |
| B2(料金案消滅と価格回復の因果連結、"so") | **QUALITY** | いいえ(ユーザー確定) | Ledgerが記録した2観測の共起を因果接続詞で連結。Ledgerと矛盾はしないが明文で禁じた書き方 |
| B3(接続詞"so"、政策決定理由の取り違え) | **BLOCKING** | いいえ(ユーザー確定+Opus/v0.2/Step2診断3系統一致) | HF-007 conditionsに別原因(中東指導者協議)が明記、政策決定理由を取り違えさせる |
| B4-a(AIフォールバック機構の新規主張) | **BLOCKING** | いいえ | MUSE-HC-006範囲外の製品仕様捏造、材料的誤伝達 |
| B4-b(人間心理の一般論) | **ACCEPTABLE〜QUALITY(Trialでは QUALITY扱い)** | **はい**(ACCEPTABLE〜QUALITYの幅をQUALITY側=やや厳しい側に倒す) | Metaの事実を歪めないが、Checkerの過剰検出(changed_scope)との境界が曖昧なため、Trial評価では「継続はするが要観察」のQUALITY側で統一し、ACCEPTABLE即時通過とは区別する |
| B4-c(AI/人間判別への関心の一般論) | **ACCEPTABLE〜QUALITY(Trialでは QUALITY扱い)** | **はい**(同上) | 同上 |
| B4-d(テスト結果の確実性強化、V4A run) | **QUALITY〜BLOCKING(Trialでは BLOCKING扱い)** | **はい**(fail-closed側=BLOCKING) | certainty変化(「思わせるテスト」→「実際に驚きを生じさせた」)はfloor対象外(changed_certaintyはdeterministic floor非対象、§4-3)だが、境界が未確定である以上Trial評価では安全側=BLOCKINGとして扱い、Stage 2が実際にQUALITYへ降格させた場合はその挙動を観測記録する(正解ラベル自体をACCEPTABLE側へ緩めない) |

### 7-1. Safety群(Stage 1/2で必ずBLOCKING維持、その後Rewrite→PASSが期待到達経路)

| fixture | 正解ラベル | 理由(floor/rubric) | 期待到達経路 |
|---|---|---|---|
| er009_changed_number/actor/negation/comparison/time(5種) | BLOCKING | deterministic safety floor該当(§4-3) | S1 BLOCK→S2 floor→BLOCKING確定(LLM判定を待たず)→S3 Rewrite→S1 Recheck→PASS |
| er009_changed_scope/causality/certainty/unsupported_new_claim(4種) | BLOCKING | floor対象外だがrubric基準1(Ledgerとの明示矛盾)に該当 | S1 BLOCK→S2 rubric判定でBLOCKING→S3 Rewrite→S1 Recheck→PASS |
| A2A3/A4/A5(実データ、価格反転・対象取り違え・意味反転) | BLOCKING | rubric基準1(Ledger矛盾) | 同上 |
| hormuz_run03_standard(HF-009 changed_scope) | BLOCKING(Confirmed) | rubric「scopeと矛盾」該当(Brent先物→市場全体への一般化) | S1 BLOCK(recall問題あり、§10リスク6/§14)→S2 rubric判定でBLOCKING→S3局所Rewrite→S1 Recheck→PASS |
| Meta_run03_standard(negative control) | BLOCKING | rubric基準1 | 同上 |

### 7-2. QUALITY群(Stage 2でQUALITY通過が期待、Rewrite不要、ただし要観察ログ)

| claim | 正解ラベル | 期待到達経路 |
|---|---|---|
| B2(料金案消滅と価格回復の因果連結) | QUALITY | S1 BLOCK→S2 rubric「Ledgerが保証しない関係付け」でQUALITY→継続(表現修正の余地は残すが自動Rewriteは強制しない) |
| B4-b(人間心理の一般論) | QUALITY(Trial扱い) | S1 BLOCK(過剰検出)→S2でQUALITY→継続 |
| B4-c(AI/人間判別関心の一般論) | QUALITY(Trial扱い) | 同上 |

### 7-3. ACCEPTABLE群(Stage 2でACCEPTABLE通過が期待、Rewrite不要)

| claim | 正解ラベル | 期待到達経路 |
|---|---|---|
| B1-a(ホルムズ海峡=重要航路) | ACCEPTABLE | S1 BLOCK(過剰検出)→S2 rubric「一般常識」でACCEPTABLE→継続 |
| B1-b(原油高→ガソリン等波及) | ACCEPTABLE | 同上 |

### 7-4. Real-but-fixable群(Stage 2でBLOCKING確定、Rewrite→PASSが期待到達経路)

| claim | 正解ラベル | 理由 | 期待到達経路 |
|---|---|---|---|
| B1-c(市場動機・価格回復理由の断定) | BLOCKING | HF-011 notesが因果推論を明示禁止 | S1 BLOCK→S2 BLOCKING確定→S3局所Rewrite→S1 Recheck→PASS |
| B3(接続詞so、政策決定理由の取り違え) | BLOCKING | HF-007 conditionsに別原因明記(rubric基準1) | 同上 |
| B4-a(AIフォールバック機構の新規主張) | BLOCKING | MUSE-HC-006の範囲外の製品仕様捏造 | 同上 |
| B4-d(テスト結果の確実性強化、V4A run) | BLOCKING(Trial扱い、fail-closed) | certainty変化、floor対象外、境界未確定のため安全側 | S1 BLOCK→S2 BLOCKING(fail-closed)→S3局所Rewrite→S1 Recheck→PASS。Stage 2が実際にQUALITYへ降格させた場合はその挙動を観測記録し、Phase 1実測後に正解ラベルの再検討材料とする(ラベル自体は今回変更しない) |

### 7-5. Normal群(Stage 1のみでACCEPTABLE到達が期待、既にAPI¥0で実証済み)

negative claim候補16件(`docs/pm/negative_claim_candidates_open233_
01.md`)。現行Production実行で既に`LEDGER_COMPLIANT`(deviations=[])
として通過した実績があるため、Self-Recovery Flow下でも**Stage 1のみで
ACCEPTABLE、Stage 2以降に到達しないことが期待**される正解ラベル=
ACCEPTABLE。ただしStandard/Advancedの表現断定度によって同一Ledgerでも
判定が割れる実例(候補1〜3 vs 同一runのAdvanced版B4 fixture)があるため、
非決定性により稀にBLOCKING-candidateとしてStage 2へ到達する可能性は
残る(その場合の期待到達経路: S1 BLOCK[過剰検出、非決定性]→S2で
ACCEPTABLE/QUALITYへ戻る→継続。16件全てのTrial扱い正解ラベルは
ACCEPTABLE、Stage 2到達は非決定性による例外扱い)。

### 7-6. Phase 1 Trial評価基準としての使い方

上記7-1〜7-5の「期待到達経路」を、Phase 1 Trial実行結果の合否判定基準
とする。具体的には: (1) 7-1(Safety群)は全fixtureが必ずBLOCKING確定を
経てRewrite→PASSへ到達すること(1件でもStage 2がACCEPTABLE/QUALITYへ
降格させたらSafety regressionとして即報告)。(2) 7-2/7-3(QUALITY/
ACCEPTABLE群)はRewrite無しで継続することが期待値だが、Stage 3が発火
しても即Safety事故ではない(過剰Rewrite=生産性課題として記録)。(3)
7-4(Real-but-fixable群)はBLOCKING確定→Rewrite→PASSの到達を確認する。
(4) 7-5(Normal群)はStage 1のみで完結することを確認する。

## 8. 測定項目の定義と算出方法

### 8-1. Self-Recovery 6項目

| 項目 | 定義 |
|---|---|
| Initial BLOCK件数 | Stage 1がBLOCKING-candidateを返した回数(writer-stage-instance単位、Advanced/Standard別カウント) |
| Re-screening自動解消件数 | Stage 2がQUALITY/ACCEPTABLEを返し、Stage 3を経ずに継続した件数 |
| Rewrite進行件数 | Stage 2がBLOCKING確定し、Stage 3が発火した件数(cycle 1・2の合計) |
| Rewrite自動解消件数 | Stage 3実行後のStage 1 RecheckでACCEPTABLE/QUALITYになった件数 |
| Final STOP件数 | Stage 4へ到達した記事数(cycle上限到達またはJA Fact Check STOP) |
| USER_DECISION_REQUIRED件数 | Final STOPのうち実際にユーザーへ提示した件数(通常はFinal STOP件数と一致する設計だが、将来同一記事内の複数STOPを集約提示する場合に備え区別して定義する) |

**[委任_04新設/A13] Escalation 0件・Rewrite解消・QUALITY通過の内訳
測定項目(必須、Trial報告テンプレートにも必須項目化、Opus論点8推奨1/3
への対応)**:

| 項目 | 定義 |
|---|---|
| Escalation 0件の内訳 | 「真の解消」(Stage 2降格またはRewrite解消で`all_prior_issues_resolved==True`により裏付けられた件数)/「QUALITY通過」(Stage 2がQUALITYを返し継続した件数)/「`all_prior_issues_resolved`未確認」(Recheckで`overall_status`のみ確認し`all_prior_issues_resolved`を未実装・未確認のまま継続した件数、A1適用前の旧経路が残っていないかの検出用)/「誤PASS候補」(同一claimがRecheckで無言消滅した[前回BLOCKINGだったclaimがdeviation自体として出力されなくなった]件数)に分類し、全てを報告する |
| Rewrite自動解消件数のうち`all_prior_issues_resolved==True`裏付け件数 | Rewrite実行後のRecheckで`all_prior_issues_resolved==True`が実際に確認された件数(§3-0/§6-1のA1適用結果) |
| QUALITY通過件数・claim内容 | Stage 2がQUALITYを返した件数と、該当claim本文(Opus論点8(B)の「品質下限が下がっていないか」を人間が事後確認できるようにする) |

### 8-2. QCD 7項目

| 項目 | 算出方法 |
|---|---|
| Checker call数/記事 | Stage 1(Advanced+Standard)+Stage 2の合計call数の記事平均 |
| Rewrite回数/記事 | Stage 3発火回数(cycle数)の記事平均 |
| 平均追加cost | (Self-Recovery Flow総費用 − Stage 1のみのベースライン費用[既存Production実測])の記事平均 |
| P50/P95 latency | 記事1本の全Stage合計wall-clock時間の中央値・95パーセンタイル |
| completion率 | Stage 4に到達せず継続(ACCEPTABLE/QUALITYで完結)した記事の比率 |
| retry率 | Stage 3が1回以上発火した記事の比率 |
| loop率 | Stage 3のcycleを2回とも消費した記事の比率(上限接近度の指標) |

### 8-3. 不要BLOCK率(診断指標、主要受入条件ではない)

Opus論点2推奨1に従い、claim単位で再定義する(委任_03で用語統一):
`不要BLOCK率 = 正解ラベル=ACCEPTABLE/QUALITYのclaim(§7-0)がStage 1で
BLOCKING判定された率`。目標値は
設定せず(前Phaseの≤25%は撤回、診断のみ)、Self-Recovery Flowが
False・borderline群をどれだけStage 2で正しく拾えているかの内部指標
として参照する。

### 8-4. Stage別コスト計測(委任_02追加、2026-09-30ユーザー追加指示)

継続コストCap(§13)判定のため、記事単位ではなくStage単位で以下を
分離して計測する(全てTrial harnessが`usage`ログへstage識別子付きで
記録する。§9-3参照)。

| Stage | 発動率(対象母数) | 1回コスト(call単位、$/1M単価から算出) | 1記事平均追加コスト | worst case | P50/P95 |
|---|---|---|---|---|---|
| Stage 1 Initial Check | 100%(writer-stage-instance単位、Advanced/Standard別) | ○ | ○(既存ベースライン、Self-Recovery追加費ではない) | ○ | ○ |
| Stage 2 Re-screening | BLOCKING-candidate発生時のみ | ○ | ○ | ○ | ○ |
| Stage 3 Rewrite(局所EN/JA全文) | Stage 2でBLOCKING確定時のみ | ○(JA/EN別) | ○ | ○ | ○ |
| Stage 1 Recheck | Rewrite実行時のみ(cycleごと1回、JA全文Rewrite時はAdvanced+Standard 2回分) | ○ | ○ | ○ | ○ |
| cycle 2(Stage2+Rewrite+Recheckの再発火) | cycle 1で解消しない場合のみ | ○ | ○ | ○ | ○ |

**固定費(毎記事必ず発生)と条件付き費(BLOCK時だけ発生)の分離**:
固定費=Stage 1のみ(既存ベースライン、Self-Recovery Flow導入によって
増減しない)。条件付き費=Stage 2以降の全て(BLOCKING-candidateが
発生した場合のみ発火し、Stage 1がACCEPTABLEを返した大多数の記事では
追加費用¥0)。この分離が§13のCap計算の前提。

## 9. Trial計画

### 9-0. Phase 1実行前チェックリスト([委任_04新設]、A1〜A13が設計へ
反映済みかの機械的確認。実行前に全項目を確認する)

| # | 項目 | 反映節 | 確認 |
|---|---|---|---|
| A1 | Recheckに`prior_issues`を渡し継続条件=`LEDGER_COMPLIANT`かつ`all_prior_issues_resolved==True` | §3-0/§6-1 | 済 |
| A2 | precheck由来検出はfloor扱い(`detected_by`フィールド、Stage2降格不可、FP率次第で弱め分岐) | §3-1/§4-3 | 済 |
| A3 | precheck FP率¥0測定をPhase1最初に置く | §9-1① | 済 |
| A4 | origin=ja_sourceにEN局所Rewrite不適用、paired local rewriteをPhase1第一級項目へ | §5-1/§5-2/§5-3/§5-4 | 済 |
| A5 | cycle2発火条件に「cycle1と異なるclaim/fact_id」追加 | §3-3/§5-3/§6-1 | 済 |
| A6 | §13-6を式へ書き換え、二重計上精査、JA-origin比率実測反映 | §13-6 | 済 |
| A7 | Stage4条件表をコード上の例外型と1対1対応 | §6-1 | 済 |
| A8 | Stage2入力からexplanation/severity/10 flagsを除外、ヘッジ語regexで段落範囲拡張 | §4-4 | 済 |
| A9 | Stage2をinstance単位1 callへbatch化(主案)、per-claim比較対照 | §3-5/§4-1(§9-1④) | 済 |
| A10 | rubric ACCEPTABLE定義明文化、changed_certaintyをfloorへ | §4-2/§4-3 | 済 |
| A11 | rewrite_hint schemaに`rewrite_kind`追加、機械検証追加、guard抵触時の段階的フォールバック | §4-5/§5-2 | 済 |
| A12 | prompt caching受理可否・削減率をPhase1で実測 | §9-1④/§13 | 済 |
| A13 | Escalation 0件内訳等の測定項目必須化 | §8-1 | 済 |

### 9-1. Phase 1(既存fixture/artifact reuse、次回委任で実施。
**[委任_04改訂/A3・A14・A15]** 実測項目の優先順序を以下①〜⑥へ確定)

**目的**: Stage 2/Stage 3の設計が既存fixtureに対して機能するかを検証
しつつ、**モデル非依存の構造的結論(prior_issues併用・pre-check FP・
JA/EN乖離ルール・call数/batch/caching)を、モデル依存の結論(Stage1
variant最終確定)より先に確定させる**(Opus論点8推奨4、A15)。Stage 2
評価はV4-A由来レコードに限定する(V2/V3混在を排除、Opus論点8(C))。

**① precheck FP率実測(¥0、最優先)** **[委任_06実測完了]**: 既存
`LEDGER_COMPLIANT`(deviations=[])記事28件のうち、既存の逆展開ユーティリティ
(`er050_gpt6_checker_comparison_trial_01.extract_inputs_from_prompt`)で
再構成できた20件(残り8件はJA writerのretry後attempt[`prior_issues`
instructionを含むprompt]であり、当該ユーティリティが未対応のため対象外、
既知の限界として記録)にdeterministic pre-check(`er052_open233_self_
recovery_precheck_01.py`)を適用した。**記事単位FP率=0/20=0%**(finding単位
0件)。実装は反復修正を経ている(初回実装では小物Ledger[F001-F018]記事2件
[a2/b1b]でactor_missing誤検知10件が発生。原因は(a)所有格差[`Celine's`
vs Ledgerの`Celine`]の非正規化、(b)Markdown見出し内のTitle Case連続語を
複合固有名詞と誤認、(c)文頭大文字化された一般語[`Can`/`Looking`等]の
誤検出、(d)同一Ledgerの別Factが持つ数値・日付・語彙を「別Factの主体・
値」と正しく除外できていなかったこと。(a)〜(d)を全て補正するregression
testを`er052_open233_self_recovery_precheck_01_test_01.py`へ追加した上で
再測定し0%を確認した)。design書§3-1が定めた判断基準(記事単位FP率が
10%超なら「Stage 2強制送付[棄却可]」の弱い分岐へ切替え)に照らし、
**0%(10%を大きく下回る)のため、precheckのfloor扱い(§3-1/§4-3の強い
分岐、Stage 2をスキップし直接BLOCKING確定)をそのまま維持する**。
Safety群(er009 9種+A2A3/A4/A5、計12件)への適用では、precheck単独の
検出率=1/12(8.3%、`er009_changed_number`のみnumber_mismatchで検出)。
残り11件は非検出(構造的理由: er009系Ledgerの一部[ER-006 pool形式]は
actor名が`claim`ではなく`source:`引用行にのみ存在し、現行の正規表現は
`claim`等の主要フィールドのみを走査するため対象外。changed_scope/
causality/certainty/negation/comparison/time/unsupported_new_claimは
意味的判断が必要でありdesign書§14-4の既知の限界どおり機械照合不可)。
これは想定どおりであり、precheckはStage 1 LLMの代替ではなく補完層で
あることを裏付ける。**費用¥0(API呼び出しなし)**。詳細ログ:
`er052_output/open233_self_recovery_precheck_01/phase1_step1_fp_rate.json`
/`phase1_step1_safety_group_detection.json`。

**② hormuz n=20見逃し3 attempt補完実験(¥0〜数円)** **[委任_06実測完了]**:
hormuz_run03_standardのn=20 stability実測(`er051_output/open233_
checker_trial_01/trial_03_stability_n20/`)でV4-Aが非検出だった3
attempt(attempt 8/13/14、いずれもprompt_sha256が同一=同一入力に対する
繰り返し測定)を特定した。(a) precheckを適用した結果、**非検出**
(0 findings、期待どおり。HF-009 changed_scope[Brent先物→石油市場全体
への一般化]は意味的逸脱であり機械照合対象外という§14-4の既知の限界を
裏付ける)。(b) Stage 1出力を一切見せない独立Stage 2診断Prompt
(`er052_open233_self_recovery_stage2_01.py`、gpt-6-luna、§4のrubricを
継承しStage 1出力なし版に適合させた新規Trial実装)を、当該記事(全文)+
Ledger全文+JA原文へ3 call適用した結果、**3/3(100%)がHF-009を
`materiality=BLOCKING, basis=ledger_scope`として独立に検出**した(3回とも
"HF-009 establishes the reported movement for Brent[crude futures]
only... does not establish...oil market[generally]"という同一趣旨の
理由付け)。**Stage 1のrecall欠落[85%→n=20中3件]を、独立したStage 2
診断が3/3で埋められることを実データで確認した**(design書§11-5/§14-4
が示していた「Self-Recovery Flowで解決されない構造的限界」への実証的な
反証材料。ただし本実験はStage 1がBLOCKINGと判定した後にのみStage 2が
発火する通常設計[§3-0]の前提を外した診断目的の特例であり、そのまま
Production設計へ組み込めるわけではない[全記事へ常時2nd Checkerを回す
運用コストの問題は§14-4「PASS時の限定2nd run」不採用の理由と同じ]。
Phase 2での扱いは§11-5への追記候補とする)。**費用**: Stage 2診断3call
合計¥0.6285(単価¥0.185〜0.225/call、gpt-6-luna実測)。3/3で結果が
一貫していたためn=2への拡張(computed guardrail上限¥2に対し実測は
その約1/3)は行わなかった。詳細ログ:
`er052_output/open233_self_recovery_phase1_hormuz_followup_01/summary.json`。

**③ V4-A BLOCK率増分+changed_actor有意性実測(¥1.5〜3+¥6=約¥8〜9)**
**[委任_07実測完了]**: 当初計画のV0/V4-A 2variant比較に加え、ユーザー
方針(既存方式に縛られないQCD比較)に基づき**S1-D(一体型、§14-2で
理論上不採用としていたものを実測対象へ追加)**を同一fixtureで比較した
(実測結果・費用内訳は§14-5参照)。(a) Safety群12 fixture: S1-D
12/12(100%)、費用¥3.0542。(b) `er009_changed_actor` n=15追加実測:
V0=7/15(46.7%)・V4-A=15/15(100%)・S1-D=15/15(100%)、Fisher検定
V0 vs V4-A/S1-D共にp=0.00220(有意)。(c) negative候補7記事BLOCK率:
V0=0/7・V4-A=4/7(57.1%)・S1-D=6/7(85.7%、V4-Aより過剰BLOCK)。
(d) B群5 fixture claim単位ラベル一致: S1-DはB3/Meta_run03_standardで
確定ラベルと一致したが、B1/B4でReal-but-fixable群(B1-c/B4-a)を
QUALITYへ誤降格させる実例が観測された。(e) hormuz/Meta n5:
S1-D=10/10(100%)。**Stage 1最終確定: V4-A(変更なし、S1-Dは不採用、
根拠§14-5)**。費用: (a)¥3.0542+(b)¥4.0283+(c)¥3.3103+(d)¥1.2379+
(e)¥1.8927=**¥13.5234**(76 call)。

**④ Stage2実単価/batch化/prompt caching実測(数円〜¥10程度)**
**[委任_07実測完了]**: per-claim call vs instance単位batch call
(B4=4claim/B1=2claim、gpt-6-luna、`er052_open233_self_recovery_
stage2_production_01.py`新規実装、§4-4確定入力どおり)を実測した
結果、判定一致率100%(claim間相互汚染なし)・batch化でcall数/費用
(55%減/29%減)/latency全てが改善(§4-7)。prompt caching受理可否も
実測確認(cached_input_tokens比率99.9%、費用削減率63〜64%、§4-7)。
**[委任_07新規発見]** per-claim Stage2でReal-but-fixable群
(B1-c/B4-a)がQUALITYへ誤降格される較正リスクを発見(S1-D実測と
独立に同一方向の誤判定、詳細§4-7)。費用¥1.1364(12 call)。

**⑤ Stage3型別Rewrite成功率実測(約¥8〜22)** **[委任_08実測完了]**:
delete型(B1-c/B3/B4-a、決定論的削除+Recheck)・replace_with_ledger_
value型(er009_changed_actor/changed_number、E-1 vs E-2)・narrow_scope
型(hormuz_run03_standard HF-009、J-1 vs J-2)を実測した。delete型は
単一deviation記事(B3)でresolved=True、複数deviation記事(B1-c/B4-a)は
記事全体Recheckが他claim残存のためLEDGER_DEVIATIONのまま(claim単位の
再出現確認は次回実装項目)。replace型はE-1/E-2とも4/4(100%)が
1 attempt目で解決、cost差僅少。**narrow_scope型はJ-1が完全解消
(resolved=True、drift 0件)、J-2は未解消(EN Recheck LEDGER_DEVIATION
のまま、非対象文drift 1件検出)**。採用案: narrow_scope=J-1、
replace_with_ledger_value=E-2第一候補(E-1はfallback)。詳細は§5-4-補2。
費用¥3.0363(18 call、Guardrail¥30のうち)。

**⑥ 統合dry-run実測(委任_09完了)**: ①〜⑤の確定設計(V4A Stage1・R2
rubric+floor・narrow_scope=J-1/replace=E-2・cycle上限2・A1/A5/A7)を
1本のTrial runner(`er052_open233_self_recovery_flow_runner_01.py`+
test)へ統合し、29 instance(Hormuz run_01/run_02 Advanced各1[現行
Production STOP実例、Standardは同run内で未生成のため対象外]・run_03
Advanced/Standard、Meta run_03 Advanced/Standard、B群4[B1/B2_hormuz/
B3/B4]、negative候補7、Safety群12[er009 9種+A2A3/A4/A5])で通し実行
した(92 call、¥16.7806、0 error、Guardrail¥45の約37%)。

**Self-Recovery 6項目(instance単位)**: Initial BLOCK=23/29、
Re-screening自動解消=1(hormuz_run01_advanced、HF-006「一般的な経済
連動性の言及」をStage2がACCEPTABLEへ正しく降格、Rewrite不要で現行
Production STOPを自動回避=設計が目指す典型的成功例)、Rewrite進行=22、
Rewrite自動解消=13(RESOLVED_REWRITE=11[`all_prior_issues_resolved=
True`確認済み]+RESOLVED_REWRITE_THEN_DOWNGRADE=2)、Final STOP=9、
USER_DECISION_REQUIRED(Stage4到達)=9(全件到達理由=
`same_claim_fact_id_reblocked`、cycle 2で同一fact_id再BLOCKingを検出
し即STOPというA5設計どおりの動作)。

**0件の内訳(A13)**: 真の解消(`all_prior_issues_resolved=True`)=11、
QUALITY通過=0(本評価セットでQUALITY止まりのまま継続したclaimは無く、
全BLOCKING-candidateがRewrite対象化または非BLOCKING降格のいずれかへ
分岐)、`all_prior_issues_resolved`未確認=0、誤PASS候補=0(全件Recheck
で明示確認、無言消滅なし)。

**重大Fact見逃し(Stage1 recall、Safety観点で最重要の発見)**: V4A単発
実行(n=1)で、Real-but-fixable/Safety隣接群のうちB2_hormuz・B3・
**hormuz_run02_advanced(現行Production STOP実例そのもの)**の
3 instanceで、既知のBLOCKING claim(HF-011/HF-007/HF-011相当)が**一切
検出されずLEDGER_COMPLIANTとなった**(§10/§14既知の「Stage1 recall
欠落」リスクが、統合dry-runで実データ3件同時に再現)。B2_hormuz/B3は
`baseline_parsed`(実Production V0、既にMAJOR検出済み)へ代替して
Stage2/3経路自体は検証したが(代替の事実を`stage1_recall_miss_
substituted=true`として明記)、**hormuz_run02_advancedは代替を適用
せず、素の結果としてACCEPTABLE_STAGE1で完結した**(Self-Recovery
Flow自体が発火する前にStage1が見逃したため、Stage2/3では捕捉不可能な
既知の構造的限界の実例)。floor機構自体はfloor適用対象48 BLOCKING
claim中0件のfalse-negativeを維持したが、**Stage1自体の検出漏れは本
設計の範囲外であり未解決のまま**。

**QCD(instance単位)**: 総call数92、総費用¥16.7806、平均追加cost/
instance=¥0.5786(全29)/¥0.7118(BLOCKING発生23件のみ)、P50=¥0.377
(全29)/¥0.5918(BLOCKING23)、P95=¥1.9421、worst=¥2.2721(safety_A4、
3claim分のJ-1/E-2 rewrite)。**worst caseでも+¥3/記事Capを下回った**
(§13-7のCap判定を実測で裏付け)。latency P50=17.27秒/P95=143.5秒。
completion率=69.0%(20/29、Stage4未到達)。retry率=75.9%(22/29で
Rewrite発火)。loop率=41.4%(12/29でcycle上限2まで消費)。

**現行Productionとの対比(Hormuz 3記事)**: run_01 Advanced=現行STOP→
本フローはRewrite不要でRe-screening自動解消(ACCEPTABLE)。run_02
Advanced=現行STOP→本フローは**Stage1 recall missによりACCEPTABLE_
STAGE1**(見かけ上「解消」だがStage1が見逃しただけでありSelf-Recovery
Flowの機能とは無関係、上記重大Fact見逃し参照)。run_03 Standard
(HF-009)=現行STOP→本フローは**STAGE4_ESCALATION**(cycle2で同一
fact_id再BLOCKing、J-1汎用ロケータが対象文特定に失敗
[`j1_pair_not_located`]、委任_08の手動アンカー実験[J-1が100%解消]を
汎用実装では再現できず)。

**事象(claim)単位の段階別成功率**: floor後BLOCKING確定claim48件
(cycle1+cycle2合計)のうちRewrite実行33件、初回cycleで再発せず解消=
20/33(60.6%)。機構別: `deterministic_delete`=1/1(100%)、
`e2_generic_rewrite`(単一言語E-2)=13/18(72.2%)、`target_not_found+
fulltext_fallback`=3/3(100%、全文最小編集フォールバックが有効に機能)、
`paired_ja_en(J-1)`全体=3/11(27.3%)、うち`j1_paired_rewrite`(対象文
特定に成功した場合)=2/3(66.7%)、`j1_pair_not_located`(対象文特定
失敗)=1/7(14.3%)。**J-1機構の対象文特定(汎用JA/EN文分割・対応付け)
が本統合runで最大の失敗要因**(11回中7回[63.6%]が対象文特定自体に
失敗)。Escalation率のWilson 95%上限(instance単位9/29=31.0%、
95%CI=[17.3%, 49.2%])。

**Stage4到達9件の原因分類**:
(a) **J-1対象文特定失敗**(汎用ロケータの限界、§5-4既知の限界の実測
裏付け)= safety_A2A3(2claim)・bgroup_B2_hormuz(1)・bgroup_B4(2/4claim)
・meta_run03_standard(1/2claim)・hormuz_run03_standard(1claim)の計
5 instance。
(b) **局所編集は実行された(guard_ok=True)がRecheckが引き続き
LEDGER_DEVIATION**(Rewrite内容が実質的にLedger適合しなかった)=
safety_A4(3claim中2claim再発)・bgroup_B1(1claim)・neg1/neg2(各1claim)
の計4 instance。

**(b)の根本原因(新規発見、報告のみ・独断で修正せず)**: **Stage2出力
schema(`er052_open233_self_recovery_stage2_production_01.py::
_ITEM_PROPS`)に、design書§4-5が要求する`rewrite_hint`(自由記述、
BLOCKING時必須)フィールドが実装されていない**。本runnerはやむを得ず
`rewrite_hint`代替として`f"materiality={...}, basis={...}"`という
空疎なplaceholderをE-2 Promptへ渡しており、実際に「何をどう直すべきか」
という具体的指示がRewrite LLMへ渡っていなかった。既存個別実験
(委任_08のstage3_rewrite_trial)は各fixtureのrewrite_hintを人手で
作文していたため、この欠落は独立実験では顕在化せず、**統合dry-runで
初めて発見された**。次回実装候補: Stage2 batch schemaへ
`rewrite_hint`(string、BLOCKING時必須)を追加し、Stage3 Prompt側で
実際に使用する。

**[最重要の是正発見]negative群R2 Productivity評価のやり直し**: 委任_08
のStage2較正Trial(`er052_open233_self_recovery_stage2_calibration_01.
py::build_eval_groups()`)のnegative群4 fixture(neg1/neg2/neg3/neg5)
は、`fx["baseline_parsed"]["deviations"]`(実Production V0の記録、
これらのfixtureは定義上`deviations=[]`=LEDGER_COMPLIANT)からclaim_
textを取得しようとしたため`devs`が空となり、**`claim_text="(claim
not found in baseline)"`という無意味なplaceholder文字列がStage2へ
渡っていた**(該当コード行確認済み)。この結果、既報告の「negative群
R2で7/8(87.5%)が非BLOCKINGへ復帰」は、**実際にV4Aが誤検出した本物の
claim文言ではなく、空のplaceholder文字列に対するStage2判定を測定して
いた**ため、Productivity評価として妥当性を欠く。本統合dry-runは
(Stage1のreuse元がV4Aの実出力そのものであるため)実際の誤検出claim
文言をStage2へ正しく渡しており、**同じ4 fixture(neg1/neg2/neg3/
neg5)の実測結果は「Stage2単独でBLOCKING非該当へ降格した件数=
0/4(0%)」**(全4件がBLOCKING確定、うち2件[neg3/neg5]はRewriteで
自動解消、2件[neg1/neg2]はStage4へ到達)。**既存DECISION_LOG/
REPORT§7/本設計書§4-8のnegative群測定値(87.5%)は撤回・訂正しない
(履歴改変禁止、既存エントリはそのまま保持)が、本節で実測に基づく
訂正値を明記し、Phase 2計画・Opus L2 #2論点へ引き継ぐ**(新しい仕様
変更の実装はしない、報告のみ)。

**その他観測**: negative群7件中3件(neg4/neg6/neg7)はStage1(V4A)自体
でACCEPTABLE(過剰検出なし)、残り4件(neg1/neg2/neg3/neg5)全件が
Stage1で過剰BLOCKされ、そのうちStage2も全件BLOCKING確定(over-block
是正0%)。Stage2出力の`basis`は"unsupported_relationship"に強く偏り
(BLOCKING確定48件中28件[58.3%])、`rewrite_kind`は"narrow_scope"に
強く偏る(33件/48件[68.8%])。rewrite_hint欠落と合わせ、Stage2較正
(R2)の出力多様性そのものにも改善余地がある(Phase 2候補)。

**実装上の不具合発見・修正(報告)**: 統合runの実行中、
`er052_open233_self_recovery_stage3_rewrite_trial_01.py`(委任_08
既存資産)の`simple_llm_call`をそのまま呼び出すと、そのモジュール自身
の`save_budget_state`が**既存委任_08の証跡ファイル(`budget_state_
c233l_b.json`)を上書きする**実害を検出した(`git diff`で発覚、
`git checkout`で復元済み、既存証跡データの実質破損なし)。本runner
自身の独立した`simple_llm_call`実装へ差し替え、再発防止のregression
test(`er052_open233_self_recovery_flow_runner_01_test_01.py::
TestNoCrossModuleBudgetStateContamination`)を追加した(この修正は
Stage1/2/3の判定ロジック自体には影響しない。実測結果[92 call・
¥16.7806・0 error]はこの修正前後で同一)。

**スコープ上の限界(既存委任_08と同一、再掲)**: J-1/J-2型のJA Fact
Check/EN RecheckはV4A variant checker代用、汎用JA文分割は簡易実装の
まま(§5-4-補2)。E-1 fallback(replace_with_ledger_value型)は本統合
runでは未実装(§5-4-補2でE-2を第一候補・E-1をfallbackと確定したが、
fixture横断的なper-claim機械検証[verify_fn]が個別実装を要するため、
全文Recheckのfail-closed判定に委ねる設計とした。次回実装候補)。

**USER_DECISION_REQUIRED該当有無**: 該当なし(7条件いずれも非該当。
worst case実測¥2.2721は+¥3/記事Cap未超過[条件3]。Stage1 recall
miss・negative群Productivity訂正はいずれもSafety「緩和」ではなく既知
リスクの実測確認・既存測定の透明な訂正であり条件2には該当しない
[Safetyはfloor機構により48件中0件のfalse-negativeを維持]。Rewrite
mechanism改善提案はいずれも未実装のTrial改善候補でありProduction
採用[条件4]には未到達)。

詳細ログ: `er052_output/open233_self_recovery_flow_runner_01/
summary_flow_runner.json`、`er052_output/open233_self_recovery_
flow_runner_01/instances/*.json`(29件)。

**費用見積(概算、要実測)**: 公式単価gpt-6-luna(In $0.10/Cached
$0.01/Out $0.50、為替¥156.88/$換算)を基準に、①¥0+②¥0〜¥2+
③¥8〜9+④数円〜¥10+⑤¥8〜22+⑥(④⑤に準ずる、追加数円)=
**Phase 1合計概算: 約¥18〜45**(総枠¥400のうち少額)。この見積もりは
前Phase実測単価からの外挿であり、Phase 1実行後に実測値へ更新する。
①〜⑥の合計Guardrail上限(各項目上限の合計): 約¥70(想定費用の1.5〜2倍
程度を上限とする既存慣例と整合)。Phase予算¥400に対する配分は①〜⑥の
実測(上限合計約¥70)を第一弾とし、残額(約¥330)は⑤⑥の追加実測・
Phase 2準備に充てる想定とする(次回委任で個別確定)。

**[委任_06実測]** ①=¥0(実測、確定)。②=¥0.6285(実測、確定。
見積り上限¥2の約31%)。①②実測合計=**¥0.6285**(Phase累計、後述の
Guardrail上限¥10のうち)。

**[委任_07実測]** ③=¥13.5234(実測、確定。見積り¥8〜9比+約¥5、
S1-D追加実測分を含むため)。④=¥1.1364(実測、確定。見積り数円〜¥10の
範囲内)。③④実測合計=**¥14.6598**。①〜④累計=**¥15.2883**
(Phase累計、Guardrail¥400のうち)。⑤⑥は本委任(委任_07)未実施
(次回委任で実施予定)。

**[委任_08実測]** Stage2 rubric較正Trial(§4-8)=¥3.1717(26 call、
Guardrail¥12)。⑤=¥3.0363(18 call、Guardrail¥30、見積り¥8〜22の
下限を下回った。理由: E-1/E-2・J-1とも1 attempt目で解決しescalation
未発火だったため)。委任_08合計=**¥6.208**。①〜⑤累計=
**¥21.4963**(Phase累計、Guardrail¥400のうち、残¥378.5037)。
⑥(統合dry-run)は本委任(委任_08)未実施(次回委任で実施予定)。

**[委任_09実測]** ⑥統合dry-run(29 instance、92 call)=**¥16.7806**
(Guardrail¥45、約37%使用、0 error)。①〜⑥累計=**¥38.2769**(Phase
累計、Guardrail¥400のうち、残¥361.7231)。Phase 1計画(§9-1冒頭)の
①〜⑥全項目が完了。

- **モデル**: gpt-6-luna(前Phase Trial資産との直接比較のため統一、
  §4-6参照)。Production Stage 1のgpt-5.6-lunaとの差異は既知の
  未解決事項として記録し、Phase 2で扱う。
- **Guardrail**: 上記①〜⑥の個別上限に加え、次回委任で総額上限を
  個別設定する(委任文の慣例どおり、想定費用の1.5〜2倍程度を上限とし、
  超過見込みでSTOP)。

### 9-3. Stage別usage記録要件(委任_02追加、2026-09-30ユーザー追加指示)

Phase 1 Trial harnessは、全API callのusageログへ以下を必須で付与する
(§8-4のStage別コスト計測を可能にするため。現行`er051`系harnessの
usage記録スキーマへstage識別子を追加する形で実装する、次回委任で
確定): `article_id`/`writer_stage`(advanced/standard)/`recovery_
stage`(stage1_initial/stage2_second_judge/stage3_rewrite_en_local/
stage3_rewrite_ja_full/stage1_recheck)/`cycle_number`(1 or 2)/
`model_id`/`input_tokens`/`cached_tokens`/`output_tokens`(reasoning
含む)/`cost_jpy`(公式単価+実測為替レートで算出、仮単価流用禁止)。
これにより「固定費(Stage1)」と「条件付き費(Stage2以降)」を実測ベースで
事後集計できる。

### 9-2. Phase 2(Production相当10〜20記事、Checkpoint E前に別途計画)

Phase 1でStage 2/3の基本設計が機能することを確認した後、実際の
Family X新規記事生成(または既存Hormuz/Meta run再開)をSelf-Recovery
Flow込みで10〜20記事規模実行し、Primary KPI(USER_DECISION_REQUIRED
=0件、Safety見逃し0件)を測定する。Production Stage 1のモデル
(gpt-5.6-luna)とStage 2/3で使うモデルの整合確認もここで行う。詳細
計画は本書の対象外(次のCheckpoint前に別途設計)。

**[委任_09追記]Phase 1⑥の結果を踏まえた改善優先順位(Phase 2着手前に
解消すべき既知課題、実装せず提案のみ)**:
1. **Stage2出力schemaへの`rewrite_hint`追加**(§9-1⑥(b)根本原因、
   最優先)。現状Stage3へ渡る情報が`materiality`/`basis`のみで
   具体的な修正方針が無く、Rewriteの60.6%成功率(claim単位)の主要な
   下押し要因になっている。
2. **JA/EN paired local rewrite(J-1)の汎用対象文特定**(§5-4既知の
   限界、実測ではlocate失敗率63.6%[7/11]が最大の失敗要因)。委任_08
   のhormuz手動アンカー実験(100%解消)と本統合runの汎用ロケータ
   (27.3%)の差は、汎用実装の成熟度不足であり設計の限界ではない
   ことを示唆する。
3. **negative群Productivity評価の再測定**(§9-1⑥「最重要の是正発見」
   参照、既存87.5%は無効な測定に基づく。実測0/4[0%]を前提に、
   Stage2 R2 rubricのover-block是正力を再評価する必要がある)。
4. **Stage1(V4A) recallの底上げ**(3/複数instanceで既知BLOCKINGを
   n=1で見逃した。§9-1②の「独立Stage2診断3/3検出」知見をどう
   Production設計へ組み込むか[全記事2nd runのコスト増との比較]を
   Phase 2設計に含める)。
5. **新規記事のテーマ選定**: Phase 2で新規Family X記事を生成する場合、
   テーマは複数候補(英語・日本語・理由付き)を提示しユーザーが選択
   する(PM_GOVERNANCE.md§13「新規記事テーマ選定ルール」準拠。既存
   Hormuz/Meta run再開[regenerate]であればこの制約は適用されない)。

## 10. リスク

| # | リスク | 緩和策 |
|---|---|---|
| 1 | retry loop化(記事が延々と自動再生成を繰り返す) | cycle上限を記事あたり2に固定(§3)。上限到達で必ずStage 4へ抜ける設計とし、上限を動的に緩めるロジックは持たない |
| 2 | cost/latency肥大 | Stage 2はBLOCKING-candidateのみに発火(Stage 1でACCEPTABLEの大多数には追加費用ゼロ)。§8のQCD測定でPhase 1から実測し、Checkpoint Dで費用推移を確認する |
| 3 | 人間確認ゼロによる新規リスク(a): Stage 2がmaterialなclaimを誤って通す | deterministic safety floor(§4-3)+rubric基準1(Ledger本体フィールドとの矛盾)で機械的に補強。Phase 1でSafety群100%維持をStage 2にも要求する受入条件として設定(次回委任で明記) |
| 4 | 人間確認ゼロによる新規リスク(b): Stage 3 Rewriteが新たな逸脱を生む | 全文Recheck(局所チェックにしない、§5-2)をfail-closedの前提とする。Hormuz run_03の実例(Advanced修正後にStandardで別claimのMAJORが新規発生)が示すとおり、これは既に現行案Bでも発生している既知のリスクであり、Self-Recovery Flowはこれを「2 cycle目で拾う」ことで緩和するが、根絶はしない |
| 5 | 人間確認ゼロによる新規リスク(c): Rewriteが構造を壊す | `split_family_x_article_text_v2()`の既存NG guardをそのまま再利用(§5-2)。guard抵触時はcycleを消費してStage 4へフォールボックする設計とし、guardを回避してRewriteを繰り返さない |
| 6 | Stage 1非決定性(recall 85〜100%、n=20実測)がStage 2以降で拡大しないか | Stage 2はStage 1がBLOCKINGと判定した場合にのみ発火するため、Stage 1が見逃した(ACCEPTABLE誤判定)ケースはStage 2の対象外のまま残る。**これはSelf-Recovery Flowでは解決されない既存のrecall問題**であり、本設計のスコープ外として明記する(self-consistency等のrecall改善策は§11でOpusへ問う別論点とする) |
| 7 | HOOK_CLAUSE衝突(Family横断時) | 前Phase Opus論点5(D)で特定済みの`changed_comparison`正面衝突は、本Flowが現時点でFamily X限定(`hook_aware=False`経路のみ)である間は無害。Stage 2/Stage 3のPrompt文言がHOOK_CLAUSEと将来同一Promptへ統合される際は、前Phase同様Family N3の危険Hook fixture 3種でregressionを回すことを必須とする(本Phaseでは統合しない) |
| 8 | Production Checkerのモデル差異(gpt-5.6-luna vs Trial gpt-6-luna) | §2/§4-6で明記済み。Phase 1はgpt-6-lunaで統一し前Phase資産と比較可能にするが、Phase 2でProduction実配線を検討する際は、Stage 1(gpt-5.6-luna、既存Production不変)とStage 2/3(Trial用に検証したモデル)のモデル差自体がSafety regressionを生まないかの追加確認が必要になる(Opus論点として§11に計上) |
| 9(委任_02追加) | コスト肥大(loop×高単価)。特にStage 3 JA全文Rewrite(案B相当、1回¥3.49〜4.02)を2 cycleとも使い、かつAdvanced/Standard両方が同時にBLOCKING確定するworst caseでは、§13の試算上+¥3/記事Capを超過し得る(期待値ベースでは大きく下回るが、稀なworst case記事では超過し得る) | cycle上限(記事あたり最大2、既存設計)を維持しつつ、§13で示す優先順位(局所Rewriteを優先しJA全文Rewriteの発火自体を減らす)で緩和する。それでもP95/worst caseがCapに接近する場合は、次項(#10)のUSER_DECISION_REQUIRED条件に従う |
| 10(委任_02追加) | Cap超過時のUSER_DECISION_REQUIRED条件 | Phase 1実測で(a)記事あたり期待追加コストの中央値シナリオが+¥3を超える、または(b)worst case/P95が恒常的(稀な例外でなく一定割合)に+¥3を超える、のいずれかが判明した場合、勝手にコストを積み増さず、§13の「+¥3以下で困難な場合の中間報告」項目に従い直ちにUSER_DECISION_REQUIREDとして報告する(委任文2026-09-30ユーザー追加指示) |

## 11. Opus L2に問う論点(委任_03で8項目へ整理、ユーザー指定の批判対象軸)

以下8項目は、ユーザーが批判的レビュー対象として明示指定した軸
(Self-Recovery全体設計/Stage 1設計/Second Judge/Rewrite戦略/Safety/
Cost/loop化リスク/Escalationゼロの現実性)にそのまま対応する。各項目に
「本設計の暫定答え」と「批判してほしい点」を付す。

### 11-1. Self-Recovery Flow全体設計

**暫定答え**: 4段階(Initial Check→Re-screening→Rewrite→Escalation)
は、Stage 1のSafety資産保存(Prompt不変維持の原則、ただしStage 1自体は
V4A採用へ変更、§14)・Stage 2のfail-closed tie-break・cycle上限2による
loop制御・deterministic floorの4層で、KPI(USER_DECISION_REQUIRED実質
ゼロ・重大Fact見逃し0件・+¥3/記事以内)を同時達成することを狙う。
**批判してほしい点**: 4段階という構成自体が最適か(例えば3段階[Stage 2
とStage 3を1回のLLM呼び出しで「materiality判定→必要ならrewrite_hint
生成」まで一体化する案]の方が呼び出し回数・コストを削減できるのでは
ないか)。Stage 2/3を分離する設計上の利点(materiality判定とrewrite_hint
生成を別々に検証できる)は、コスト増加分に見合っているか。

### 11-2. Stage 1設計

**暫定答え**: 真のProduction Checker(V0)は`changed_actor`を50%
(3/6)見逃す実測があり、Stage 1が検出しない限りStage 2以降は発火
しないという構造的事実から、Trial variant V4A(changed_actor 5/5、
Safety群12/12維持)を採用した(§14で確定)。真のProduction Prompt自体は
無変更のまま。**批判してほしい点**: V4A採用はhormuz_run03_standardの
n=20実測でV0比検出率が悪化する方向(100%→85%、統計的有意差なし)を
伴う。Safety観点で「1カテゴリ[changed_actor]を救うために別カテゴリ
[changed_scope]の検出率が[統計的に有意でないとはいえ]下がる可能性が
ある」trade-offを許容する設計判断は妥当か。deterministic pre-check
(§14、machine照合による補助検出、¥0)がこの残存リスクを十分に
補完できるという評価は正しいか。

### 11-3. Second Judge(Stage 2)設計

**暫定答え**: 独立Prompt・別call(前Phase Opus論点1推奨4)、
deterministic safety floor(5フラグ)、fail-closed tie-break。入力は
段落±1+Ledger全文(§4-4、委任_03で記事全文から縮小確定)。**批判して
ほしい点**: floor対象外のchanged_causality/changed_scope等でmaterialな
ケース(B3/hormuz_run03_standard)を、rubric文言だけで安全に止められる
という設計判断は十分か。段落±1への入力縮小(§4-4)が、B3のような
「離れた箇所[conditions]に別原因が記載されている」ケースの判定精度を
落とさないか(Ledgerは全文のまま渡すため直接の影響は限定的と考えるが、
記事側の文脈縮小が`qualifier_present`等の判定に影響しないかは未検証)。

### 11-4. Rewrite戦略(Stage 3)

**暫定答え**: JA側は既存案B(全文差し戻し、Production code再利用)、
EN側は局所Rewrite(§5-2、Phase 1で新規実装、既存NG guard再利用)。
Recheckは全文Checker(fail-closed優先)。**批判してほしい点**: 局所
Rewrite(§5-2)は、全文再生成(既存案B/既存must-fix retry)と比較して
Safety/生産性のトレードオフ上、優先的に実装する価値があるか。Hormuz
run_03の実例(全文再生成が新しい逸脱を誘発)は局所Rewriteの必要性を
示す十分な根拠か、それとも単なるn=1の偶発事象か。

### 11-5. Safety(重大Fact見逃し0件の維持可能性)

**暫定答え**: deterministic safety floor(5フラグ、昇格のみ)+rubric
基準1(Ledger本体フィールドとの矛盾)+全文Recheck(fail-closed)+Stage 1
V4A採用(§14)の4層で、Safety群100%維持を狙う。Stage 1のrecall
非決定性(n=20実測85〜100%)自体はこのFlowで解決されない(§10リスク6)。
**批判してほしい点**: Stage 1が検出しなかった(ACCEPTABLE誤判定の)
ケースは、Self-Recovery Flow全体の対象外のまま残る(Stage 2以降が
発火しない)という構造的限界は、「重大Fact見逃し0件」というPrimary
Safety KPIと矛盾しないか。矛盾するとすれば、KPI達成の前提として
Stage 1側のrecall改善(self-consistency等)が不可欠ではないか、それとも
§14のdeterministic pre-check(machine照合)で実務上十分と言えるか。

### 11-6. Cost(+¥3/記事Cap)

**暫定答え**: 案γ(Stage 1[V4A]固定費+BLOCK時のみStage 2+必要時のみ
局所/JA Rewrite、cycle上限2)が第一候補。§14でのV4A採用に伴う固定費
増(+30%/call)を織り込んで再計算した結果、楽観/中央シナリオは依然
節約方向、悲観シナリオは+¥1程度、**worst case(tail)はV4A採用前の
¥2.88から¥3.7〜3.8程度まで悪化し、Cap[+¥3]を超過する可能性がある**
(§13-7更新版、要Phase1実測)。**批判してほしい点**: 中央値シナリオは
Cap内で節約方向のまま維持できているが、worst caseがCapを超過し得る
という新しい結果は、「両Advanced/Standardが同時BLOCK、かつJA全文
Rewrite後もcycle2まで必要」という稀な尾部シナリオに限定される。この
tail riskをCap判定上どう扱うべきか(委任文のUSER_DECISION_REQUIRED
条件は「worst case/P95が恒常的[稀な例外でなく一定割合]に+¥3を超える」
場合としているが、本件がこの条件に該当するかはPhase 1実測が必要)。

### 11-7. loop化リスク

**暫定答え**: cycle上限を記事あたり2に固定、上限到達で必ずStage 4へ
抜ける設計とし、上限を動的に緩めるロジックは持たない(§10リスク1)。
**批判してほしい点**: cycle上限2は、Safety(重大fixture見逃し0件維持)と
生産性(USER_DECISION_REQUIRED実質ゼロ)のバランスとして妥当か。2回で
足りないケース(Hormuz run_03のような「2箇所で別々のja_source MAJOR」
パターンが3箇所以上に増える場合等)への備えは十分か。cycle上限自体は
ユーザー指定の固定値(委任文既定)であり本Phaseでは変更しないが、
上限に達した場合のフォールバック(Stage 4)が「安全側だが生産性を
失う」という設計選択で正しいか。

### 11-8. Escalationゼロの現実性

**暫定答え**: Stage 4 Escalation発生率を実質ゼロに近づけることが
Primary KPIそのものである。ただしこれは「従来なら人間が見ていたはずの
Grayゾーンの判断を全てシステムに委ねる」ことを意味する。**批判して
ほしい点**: Stage 4 Escalation発生率を実質ゼロに近づけること自体が、
人間確認ゼロの記事が増えることを意味する。これは「安全≠成功」原則
(PM_GOVERNANCE.md 6節)との関係でどう位置づけるべきか。Escalationが
「本当に例外的なケースだけ」に留まっているかを、Human Review無しの
運用下でどう継続的に検証すべきか(Phase 1/2のTrialで測定する指標以外に、
Production化後に必要な継続監視の仕組みはあるか)。

**[委任_04追記/A16] Production化後の継続監視案(Phase 2設計項目、
Opus論点8(D)への回答。採用判断はユーザー)**: (1) shadow sampling
(公開記事の5〜10%を対象に、公開後2回目のStage 1 Checkを別runで実行し
初回と不一致[2回目でMAJOR]なら人間へ通知、コスト¥0.03〜0.06/記事
相当でCap内)、(2) QUALITY通過件数の週次レビュー(claim単位サンプル、
品質下限が下がっていないかの事後確認)、(3) 決定論的指標の常時監視
(¥0。precheck発火率/Rewrite適用文字数/cycle消費率/`all_prior_issues_
resolved=false`率)。Human Reviewを通常運用にしない制約と両立する
(全数審査ではなくサンプリング+機械指標)。**これらはPhase 2設計項目
として記録するのみで、本Phase 1では実装しない**。

### 11-補. その他の既存論点(委任_02までに提起、削除せず維持)

- Production Checkerモデル(gpt-5.6-luna)とPhase 1 Trialモデル
  (gpt-6-luna)の不一致(§10リスク8)は、Phase 1の結論をPhase 2
  (Production相当10〜20記事)へ一般化する上でどの程度の障害になるか。
- HOOK_CLAUSE整合(§10リスク7)について、Stage 2/Stage 3のPrompt文言を
  将来共通Promptへ統合する際の優先順位付け(前Phase Opus論点5推奨4
  「HOOK_CLAUSE優先、それ以外は重複true原則」)は、本Flowのmateriality
  軸導入・V4A採用とどう組み合わせるべきか。

## 12. USER_DECISION_REQUIRED条件(委任_03で全面置換、ユーザー指定7項目)

**本設計書自体はUSER_DECISION_REQUIRED非該当**(文書のみ、API呼び出し
なし、実装なし、Production変更なし、¥0)。以下がユーザーが明示指定した
STOP条件の全て(2026-09-30委任文§1、原則これのみ)。これ以外の細かい
実装判断(Trial専用Prompt/schema variant・deterministic rule・Second
Judge・Rewrite方法・regression fixture・retry構造等)はGuardrail
(KPI・Safety・Cap・Production非変更)内でFable/Claudeが自律的に改善する
範囲であり、逐一ユーザー確認を求めない。

1. **KPI自体の変更**(Primary=USER_DECISION_REQUIRED 0件、Safety=重大
   Fact見逃し0件、Cost=+¥3/記事以内、のいずれかを変更する場合)。
2. **重大Fact Safetyの緩和**(Fact反転/actor取り違え/number・numeric
   scope重大変更/negation反転/comparison方向反転/time・chronology重大
   変更/unsupported material fact/主要Fact理解を変えるcausalityを
   「止めない」方向へ変更する場合)。
3. **+¥3 Cap超過が必要と判断した場合**(期待値ベースで超過が必要、
   または恒常的にCap超過が避けられないと判明した場合)。
4. **Production正式採用・配線**(Self-Recovery Flow全体、またはStage 1
   のV4A化のような個別要素をProduction Prompt/schema/Validator/
   routing/runnerへ組み込むこと自体)。
5. **Family X以外への正式展開**。
6. **新Product原則の設定**。
7. **予算¥400超過**。

**該当有無(委任_03時点)**: いずれも非該当。§14でのStage 1(V4A)採用は
条件2(Safety緩和)ではなく**Safety改善**(changed_actor検出率50%→
100%)であり、真のProduction Prompt自体は無変更のため条件4にも非該当。
§13で再計算したworst case(¥3.7〜3.8程度、要Phase1実測)はCapの中心
シナリオ(楽観/中央)を超えるものではなく、条件3の「超過が必要」という
判断はまだ行っていない(Phase 1実測前の概算のみ)。ただしこの点は
Checkpoint Aで明示的に報告し、Phase 1実測で悪化が確認された場合は
直ちに条件3としてUSER_DECISION_REQUIRED化する。

**[委任_04追記]** Opus L2レビュー#1(論点8(A)(D)、論点6(D))が提起した
以下3点は、Fable/Claudeが独断で決めず**ユーザー判断事項としてCheckpoint
Aで提示する**(条件1[KPI変更]に触れるため): (1) KPI判定方法の再定義
(記事単位「0件」→事象単位の段階別成功率から推定したEscalation率の
信頼区間上限、統計的検出力の観点で0/10〜20記事は実質ゼロの証拠になら
ない[Wilson上限0/20で約16.8%]という指摘への対応)、(2) Cap定義の解釈
確認(純増分がLedger/Deviation Check関連LLMコストに限るか、TTS等の
downstreamコストを含むか)、(3) QUALITY通過(現行STOPしていたB2型を
人間を通さず公開すること)が条件2(Safety緩和)に該当するかの判断。
**本設計書は現行KPI文言のまま進める**(記事単位「0件」を主要KPIとして
維持)。ただし上記(1)の「事象単位推定によるEscalation率」と「Escalation
0件の内訳」(§8-1、A13)は、KPI文言そのものを変更せず**追加報告項目**
としてPhase 1から併記する。

### 12-1. Checkpoint Aで提示する項目一覧(委任_02追加・委任_03更新、
2026-09-30ユーザー追加指示、各Mandatory Checkpointで必須報告)

- best variant(現時点の第一候補=§13-8案γ、Stage 1=V4A[§14])の追加
  コスト/記事(期待値)。
- 固定追加費(Stage 1[V4A化]分の増分を含む、§13-2/§14で再計算)。
- 条件付き追加費(Stage 2以降、BLOCKING-candidate発生時のみ)。
- BLOCK時のみ発生する平均recovery費用(Stage2+Rewrite+Recheck合計)。
- P50/P95(記事あたり追加コスト)。
- +¥3/記事Capまでの余裕(シナリオ別、worst caseのCap超過リスクを
  含む、§13-7更新版)。
- 現在best variantの重大Fact見逃し状況(Stage 1[V4A]のSafety実測、
  §14)。
- 上記に加え、本書§7-0のclaim単位確定ラベル・§12の7項目該当有無
  (現時点はいずれも非該当)の確認。
- **[委任_04追記]** Escalation 0件の内訳(真の解消/QUALITY通過/
  `all_prior_issues_resolved`未確認/誤PASS候補、§8-1 A13)。
- **[委任_04追記]** 事象単位推定によるEscalation率(信頼区間上限、
  上記12節追記(1)への回答が出るまでの参考値として)。
- **[委任_04追記]** JA-origin比率実測値(暫定80%、n=5)とn拡大の有無。
- **[委任_04追記]** paired local rewrite(§5-4)の型別成功率・guard
  抵触率・実単価。
- **[委任_04追記]** worst case式(§13-6)の`n_claim`実測分布とCap判定
  レンジ(単一数値ではなく幅で報告)。

## 13. コストモデルと+¥3/記事 Cap(委任_02新設、2026-09-30ユーザー
追加指示)

**前提**: ユーザー指示は「+¥3まで使ってよい」ではなく「できる限り安く
達成する」が大前提であり、同品質・同自動完結率なら安い方式を優先する。
本章はその判断材料を提供する。全数値は**Phase 1実測前の概算**であり、
Phase 1実行後に実測値へ更新する(既存章と同じ「概算(要実測)」の
位置づけ)。

### 13-1. 単価根拠(一次ソース、推測禁止)

| model | Input | Cached input | Output | 出典 |
|---|---|---|---|---|
| gpt-5.6-luna(現行Production Stage 1) | $0.20/1M | $0.02/1M | $1.20/1M | `GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`§C-2(`platform.openai.com/docs/pricing`一次ソース確認済み) |
| gpt-6-luna(前Phase Trial、Stage 2/3候補) | $0.10/1M | $0.01/1M | $0.50/1M | 同上(gpt-5.6-lunaの正確に半額) |

為替: ¥156.88/USD(Frankfurter API、ECB参照レート、2026-09-28付、同
レポート§C-4)。

**call単位の実測参考値**: 同レポート§C-3(固定fixture 84 call実測)で
gpt-5.6-luna 平均¥0.4911/call・中央値¥0.3719/call、gpt-6-luna 平均
¥0.2043/call・中央値¥0.1818/call。本委任でユーザーが指定した「1 call
≈ ¥0.49」(gpt-5.6-luna)はこの平均値と一致し、本章の基準単価として
採用する。

**新規Evidence(本委任で追加実測)**: 実Production run(`FAMILY-X-
REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`Meta run_03、`er019_output/
family_x_refresh_e2e_01/meta/run_03/raw_usage_log.jsonl`)のWriter段
7 call分を、上記単価で本委任にて独立に再計算したところ合計¥4.13
(レポート記載の実測¥4.213と概ね一致、キャッシュトークン未計上分の
誤差)。個別call費用は¥0.04(Advanced deviation check、MAJOR無し・
出力短)〜¥1.29(Standard deviation check、MAJOR検出・reasoning出力
大)まで幅があり、**harness平均¥0.49は中心値として妥当だが、BLOCKING
検出時のcallはより高コストになりうる**ことを実データで確認した(本
発見は§13-4のStage 2単価見積りの保守化根拠として使う)。

### 13-2. 現行Production Checker(Stage 1)の構成とベースライン費用/記事

`er012_e_family_entertainment_two_level_runner_01.py`の実装(L381-388
Advanced deviation check、L477-484 Standard deviation check)から、
**通常ケース(いずれもMAJOR無し)の現行Checker構成は2 call/記事**
(Advanced 1回+Standard 1回)と確定できる。

- ベースラインStage 1費用(通常ケース) = 2 call × ¥0.49 ≈ **¥0.98/記事**。
- 既存retry込み(BLOCKING発生時、**Self-Recovery Flow導入前から存在
  する現行Production仕様**であり新規コストではない): EN側must-fix
  retry1回(全文再生成+再deviation check)、ja_source起因なら既存案B
  (JA全文差し戻し、実測¥3.487[Meta run_03、must-fix込み]〜¥4.018
  [Hormuz run_03])。実測: Meta run_03 Writer段合計(Advanced+Standard、
  must-fix retry込み)¥4.213。

### 13-3. Stage 2入力設計(§4-4)と§9-1見積りの不整合(委任_03で解消)

§4-4はStage 2の入力に「記事全文」「Ledger全文」を明記していたが、
§9-1(Phase 1費用見積り)は「入力がclaim単位で短い(Stage 1の1/3〜
1/2程度)」という楽観的仮定でStage 2単価¥0.10〜0.20と見積もっていた。
**両者は矛盾していた**(§4-4どおりなら入力サイズはStage 1と同程度)。
**委任_03で解決**: §4-4を改訂し、Stage 2入力を「記事全文」ではなく
「**対象claimを含む段落±1段落**+Ledger全文+source context+Stage 1
deviation出力」へ縮小確定した(作業D、Fable第一候補)。Ledgerは
fail-closed優先で全文のまま維持する(§4-4改訂理由参照)。この縮小に
より入力トークン量は記事全文渡しより減るが、**縮小幅の実測はまだ
無い**ため、本章のCap判定は引き続き**保守的な¥0.30〜0.40/call
(gpt-6-luna)を維持**する(楽観的すぎる見積りで節約を過大評価しない、
fail-closedの原則を費用推定にも適用)。段落±1縮小の実際の削減効果は
Phase 1最優先実測項目とする。

### 13-4. Stage別 unit cost見積り(Phase 1実測前、外挿ベース)

| 項目 | 見積り(保守的、§4-4全文入力前提) | 見積り(楽観的、§9-1想定) | 根拠 |
|---|---|---|---|
| Stage 2(gpt-6-luna) | ¥0.30〜0.40/call | ¥0.10〜0.20/call | 保守的=Stage 1 gpt-6-luna実測平均(¥0.2043)に近い水準へ、出力schema縮小分を差し引きつつ材質判定reasoningの追加分を加算した外挿。楽観的=§9-1原文 |
| Stage 2(gpt-5.6-luna) | ¥0.65〜0.85/call | ¥0.35〜0.45/call | gpt-6-luna比、公式単価が正確に2倍のため概ね2倍で換算 |
| Stage 3局所Rewrite(EN、1〜2文のみ) | ¥0.15〜0.35/call | — | 実測(Meta run_03 Standard must-fix全文regen ¥1.106)の出力トークン規模比から、局所編集は出力トークンが1/5〜1/8程度と推定した外挿。**未実装・未実測(Phase 1で新規測定)** |
| Stage 3全文Rewrite(EN、既存must-fix retry baseline) | ¥1.1〜1.3/call | — | 実測(Meta run_03 Standard must-fix regen ¥1.106) |
| Stage 3 JA全文Rewrite(案B) | ¥3.49(Meta run_03実測、must-fix込み)〜¥4.02(Hormuz run_03実測) | — | `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`実測 |
| Recheck(全文Checker再実行) | Stage 1と同一単価(gpt-5.6-luna ¥0.49、Trial gpt-6-luna ¥0.20) | — | §5-2「全文Checker再実行」 |

以降のCap判定は**保守的見積り+Stage 2はgpt-6-luna**を基準ケースとする
(Fable第一候補、委任文§2)。gpt-5.6-lunaをStage 2に使う案は§13-7で
比較のみ行う。

**[委任_07実測、Stage2実単価確定]** §4-7の実測により、Stage2(claim
単位、per-claim、§4-4確定入力)の実単価は**¥0.087〜0.112/call**
(B4/B1実測4件平均¥0.1013)であり、上表の「楽観的¥0.10〜0.20/call」
に近い水準であることが確認された(「保守的¥0.30〜0.40/call」ほど
高くない)。**batch化(instance単位1call)を使う場合**、B4(4claim)
=¥0.1862/call・B1(2claim)=¥0.127/callで、**claim数で正規化した
実効単価はさらに下がる**(B4: ¥0.0466/claim相当)。**prompt caching
併用時**はcall全体費用が63〜64%減(§4-7)であり、Stage2を連続して
複数claim・複数記事へ適用する運用(同一Ledgerの記事群を連続処理)では
Ledger prefix共有によりさらに安価になる可能性がある(未実測、Phase 2
候補)。**結論**: §13-3が「削減効果は未実測」としていた段落±1縮小は
実際に機能しており(§4-4の入力設計どおり)、Stage2単価に関する
§13-10課題1(「Stage2の真の単価が最大の不確実性要因」)は
**解消方向(実測¥0.10前後、保守的見積りの下限に近い)**。§13-5〜
§13-9の期待値・worst case式の`c_stage2`変数は、次回委任(⑤⑥実測後)
で実測値へ差し替え、Cap判定を再計算する(Stage3実単価[局所Rewrite]が
未確定のため、本委任では式の再計算は行わない)。

### 13-4-補. Stage 1のV4A採用に伴う単価再計算(委任_03、§14で確定)

§14でStage 1をV0からV4Aへ変更したため、Stage 1呼び出し(初回2 call)と
Recheck(Stage 1相当の全文Checker再実行)の単価が**call単価+30%**
(前Phase実測、gpt-6-luna基準)上がる。§13-2以降の費用モデルは実
Production単価(gpt-5.6-luna、¥0.49/call)を基準に組み立てられている
ため、同じ+30%倍率をgpt-5.6-luna単価へも外挿する(**Prompt文字数増加
という単価に依存しない要因が主因のため比例関係が近似的に成立すると
仮定、未確認・Phase 2でのgpt-5.6-luna実測で要検証**)。

- V4A Stage 1単価(外挿) = ¥0.49 × 1.30 ≈ **¥0.637/call**。
- **Stage 1固定費の増分(常時、全記事)**: (¥0.637−¥0.49)×2 call ≈
  **+¥0.294/記事**(BLOCK有無に関わらず全記事で発生、既存¥0.98/記事
  ベースラインに上乗せ)。
- **Recheck費用の増分(BLOCK時のみ、cycleごと)**: JA-path recheck
  (2 call)は¥0.98→¥1.274(+¥0.294/回)、EN-path recheck(1 call、
  instance単位)は¥0.49→¥0.637(+¥0.147/回)。
- **rewrite+recheck加重平均の再計算**(§13-5の式に使う値):
  JA 40%×(JA rewrite¥3.7+recheck¥1.274=¥4.974)+EN 60%×(全文regen
  ¥1.2+recheck¥0.637=¥1.837) = 1.9896+1.1022 = **¥3.0918/instance**
  (旧¥2.886から+¥0.206)。

以降、§13-5〜§13-10はこの再計算値を反映した更新版とする(旧数値は
「V4A採用前(参考)」として残す)。

### 13-5. 発動率シナリオと「+¥3/記事」の定義

ユーザー指示の「量産時に増加する継続コスト」は文字どおり**新方式の
総コスト − 現行方式の総コスト**(純増分)であり、Self-Recovery Flow
全体の絶対支出額ではない。現行Production は**BLOCKING検出時、Second
Judgeの判断を待たずに無条件でEN側must-fix retry1回・ja_source起因なら
案B全文差し戻し1回を実行する**(§13-2)。Self-Recovery FlowはStage 2で
まずBLOCKING/QUALITY/ACCEPTABLEを判定し、QUALITY/ACCEPTABLEに降格
できた場合はこの既存retry/案Bの実行を**回避**できる(コスト削減)。
一方、Stage 2確認後もBLOCKINGが残るケースでは、現行が持たない
**cycle 2**(2巡目のRewrite+Recheck)を追加実行できる(コスト増、
ただしUSER_DECISION_REQUIRED回避という便益と表裏)。

BLOCK発生率・Stage 2解消率・cycle 2必要率は**Phase 1未実測**のため、
既存E2E実測(Hormuz run_01〜03は3回ともja_source起因のBLOCKで最終的に
Standard段STOP、Meta run_03はStandard 1回のmust-fix retryで解消)と
前Phase B群診断(不要BLOCK率75%、n小)を参考に、3シナリオで幅を持たせる
(**いずれも仮置き、Phase 1で実測必須**)。writer-stage-instance
(Advanced/Standard、記事あたり2件)単位のBLOCK率と条件分岐:

| シナリオ | BLOCK率/instance | Stage2で解消(Rewrite不要)率 | cycle1で解消/cycle2必要/Escalation(Rewrite必要側の内訳) | JA-origin比率(Rewrite必要側) |
|---|---|---|---|---|
| 楽観 | 15% | 70% | 90% / 10% / 0% | 40% |
| 中央 | 35% | 50% | 75% / 20% / 5% | 40% |
| 悲観 | 60% | 30% | 55% / 30% / 15% | 40% |

**計算式**(Stage2単価=¥0.35/call[gpt-6-luna、保守的]、rewrite+
recheckの加重平均=**¥3.0918/instance**[§13-4-補、V4A Recheck単価
反映済み]):

`純増分/instance = Stage2単価 − P(Stage2で解消)×既存rewrite+recheck費用
 + P(cycle2必要)×(Stage2単価+rewrite+recheck費用)`

| シナリオ | 純増分/instance(V4A反映後) | 純増分/instance(V4A採用前、参考) |
|---|---|---|
| 楽観 | −¥1.47 | −¥1.57 |
| 中央 | −¥0.51 | −¥0.69 |
| 悲観 | +¥0.46 | +¥0.50 |

**記事あたりの純増分(V4A反映後)** = 純増分/instance×2 instance×
BLOCK率 + **Stage1固定費増分¥0.294/記事**(§13-4-補、BLOCK有無に
関わらず常時加算):

| シナリオ | 条件付き部分(instance×BLOCK率) | +Stage1固定費 | **純増分/記事(V4A反映後)** | 参考(V4A採用前) |
|---|---|---|---|---|
| 楽観 | −¥0.44(15% BLOCK) | +¥0.294 | **−¥0.15/記事(節約)** | −¥0.47 |
| 中央 | −¥0.36(35% BLOCK) | +¥0.294 | **−¥0.06/記事(節約、僅少)** | −¥0.48 |
| 悲観 | +¥0.55(60% BLOCK) | +¥0.294 | **+¥0.84/記事** | +¥0.60 |

**結論(期待値ベース、V4A反映後)**: 楽観シナリオは依然節約方向、中央
シナリオも僅かに節約方向だが**margin縮小**(−¥0.48→−¥0.06)。悲観
シナリオは+¥0.84/記事に増加したがCap(+¥3)に対しなお余裕がある。
V4A採用(Stage 1のSafety改善)の代償として、期待値ベースの節約効果は
縮小するが、いずれのシナリオもCap内に留まる。

### 13-6. Worst case / P95(**[委任_04改訂/A6]** 式化・二重計上精査・
JA-origin比率実測反映)

期待値とは別に、稀な記事でCapを超過しないかを確認する。**Opus所見
(論点6(B))のとおり、旧版は§3-5(Stage2 call数=2×claim数)と§13-6の
「2 call固定」計算が不整合であり、かつ案B実測¥4.02には
`_run_writer_stage_once(only=None)`の再実行[Advanced+Standard生成+
deviation check]が既に含まれているため、旧版の「2段recheck¥1.274」を
別途加算するのは二重計上の疑いがある。以下、claim数を変数とした式へ
書き換え、二重計上を除去する。**

**変数定義**: `n_claim`=検出claim数/instance(実測前は1〜4と仮定、B4実例
で4件)、`c_stage2`=Stage2単価(gpt-6-luna、保守的¥0.30〜0.40/call、
§13-4)、`c_ja_full`=JA全文Rewrite実測(¥3.49〜4.02、うちAdvanced/
Standard再実行の全deviation check込み)、`c_en_local`=EN局所Rewrite
(¥0.15〜0.35/call、未実測・Phase1で実測)、`c_recheck_ja`=JA全文
Rewrite後のRecheck(**案B実測¥4.02に含まれる分は除き、追加で発生する
Advanced/Standard分のみ**、V4A単価¥0.637×2=¥1.274)、`c_recheck_en`=
EN局所Rewrite後のRecheck(V4A単価¥0.637×1=¥0.637)。

**式(cycle 1でJA側フォールバック[旧案B]、cycle 2でEN局所を使う
worst caseパターン)**:

`worst_case = [n_claim×c_stage2 + c_ja_full] (cycle1)
 + [n_claim×c_stage2 + n_claim×c_en_local + c_recheck_en] (cycle2)
 + Stage1固定費増分(¥0.294/記事)
 − 現行方式が同じ記事に対し1 cycleのみでSTOPする費用(c_ja_full+
   c_recheck_ja相当[現行はV0のためV4A差分は除く])`

`n_claim=1`(旧版相当)を代入すると、
worst_case ≈ (0.35+4.02) + (0.35+0.35+0.637) + 0.294 − (4.02+0.98)
≈ 4.37+1.337+0.294−5.00 = **¥3.00〜4.00程度**(単価レンジの幅により
変動、旧版¥3.96はこのレンジ内)。`n_claim=4`(B4実例の上限)を代入すると
Stage2部分が+¥1.4程度増え、worst_caseは**¥4.4〜5.4程度**まで悪化しうる。

**結論(A6)**: worst caseは**¥3.0〜5.4程度の幅**を持つ(claim数・
単価レンジ双方の不確実性による±¥1〜1.5超の誤差)。**単一数値(旧版
¥2.88/¥3.96)でのCap判定はしない**。Phase 1実測(§9-1③④⑤)で
`n_claim`の実際の分布とStage2/Rewrite実単価を確定した後に、上記式へ
代入してCap判定を行う。

**JA-origin比率の実測反映**: 旧版は§13-5でJA-origin比率を仮置き40%
としていたが、実データ(Hormuz run_01〜03+Meta run_03、n=5)は
**4/5=80%**であり、40%を支持していない。以後の期待値計算(§13-5)は
JA-origin比率**実測80%(n=5、要Phase1追加実測でnを増やす)**を使う
(旧40%は参考として残す)。worst case側は元々JA-origin前提の式であり
比率変更の影響を受けない。

**BLOCK率(V4A)の扱い**: 旧版の15/35/60%(楽観/中央/悲観)という
BLOCK率は据え置きのままV4A採用を反映していない不整合があった
(Opus論点2(B))。**この数値は§9-1③の実測(negative候補7記事のV4A
再実行)後に置換する**。実測前の暫定値として残すが、Cap判定の根拠
には使わない。

**発生確率(概算、中央シナリオの独立近似)**: この worst caseは
「Advanced/Standard**両方**がBLOCK」×「JA-origin(実測80%)」×
「cycle 2まで必要」の複合条件で発生する稀な尾部事象であり、概算発生率は
**記事あたり約1%程度**(粗い近似、Phase 1実測が必要)。委任文の
USER_DECISION_REQUIRED条件3-3「worst case/P95が**恒常的[稀な例外で
なく一定割合]**に+¥3を超える」には現時点では該当しないと判断するが
(尾部確率が低いため)、**この判断はPhase 1実測前の概算に基づく**。
Phase 1実測でこのtail確率が想定より高いと判明した場合、または
`n_claim`実測分布が上限側[3〜4件]に寄っている場合は直ちに報告する。

**設計制約を守らない場合(参考、不採用のはずの経路)**: 2 cycleとも
JA全文Rewriteを使うと純増分はさらに悪化する(V4A採用前で既に
¥6.40/記事、V4A反映後はより高い)。これは§5-3の「同一記事で案Bを
2回使わない」制約が**Cap遵守にとって構造的に必須**であることを裏付ける
(実装時に確実に守るべきguard、V4A採用によりこの制約の重要性は
さらに増した)。

### 13-7. Cap判定まとめ(委任_03でV4A反映へ更新)

| シナリオ/モデル | 期待値(純増分/記事、V4A反映後) | worst case(§5-3制約遵守、V4A反映後) | +¥3 Cap判定 |
|---|---|---|---|
| 楽観、Stage1=V4A、Stage2=gpt-6-luna | −¥0.15(節約) | 未算出(複合発生率が悲観よりさらに低い) | Cap内、余裕大 |
| 中央、Stage1=V4A、Stage2=gpt-6-luna | −¥0.06(節約、僅少) | ¥3.96(**Cap超過、約¥0.96オーバー**) | **期待値はCap内だがworst caseはCap超過(§13-6、tail確率約1%と推定)** |
| 悲観、Stage1=V4A、Stage2=gpt-6-luna | +¥0.84 | ¥3.96〜(悲観ではworst case発生率自体が上昇) | 期待値はCap内、worst caseはCap超過。要Phase1実測確認 |
| 中央、Stage2=gpt-5.6-luna(参考) | 約+¥0.1〜0.3(Stage2単価2倍のため節約消失) | 約¥4.2〜4.5(Cap超過方向、V4A分も加算) | **Cap超過リスクさらに高い、gpt-6-luna推奨の根拠は維持** |

Stage 2にgpt-6-lunaを使う案が、gpt-5.6-lunaを使う案よりCap遵守に
明確に有利な点は維持される(§2でFableが示した第一候補と整合)。
**新規の知見(委任_03)**: V4A採用(Stage1 Safety改善)により、**期待値
ベースの結論(楽観・中央=節約、悲観=Cap内)は維持されるが、worst
case(稀なtail)は+¥3 Capを超過する**。§13-6のとおりtail発生確率は
概算約1%と低いと推定されるため、現時点ではUSER_DECISION_REQUIRED
条件3(Cap超過が「恒常的」)には該当しないと判断するが、Phase 1実測で
この判断を検証する必要がある(§13-10で詳述)。

### 13-8. 段階案 α〜δ(優先順位①→④に沿った比較)

| 案 | 内容 | 追加call | 純増分/記事(期待値) | 到達見込み(自動完結率) |
|---|---|---|---|---|
| α | Stage 1 Prompt改善のみ(V4-A/C2相当) | 0 | ¥0(固定費0、条件付き費0) | 前Phase実測でchangedカテゴリ検出力は改善するが、不要BLOCK率課題(実測75%)は未解消。USER_DECISION_REQUIRED実質ゼロには届かない見込み(Second Judge層が無いため過剰BLOCKを吸収できない)。Production Prompt変更自体もユーザー承認事項として別途必要 |
| β | α + BLOCK時のみStage 2 | BLOCK時のみ+1〜2call | ほぼ¥0(Stage2単価分のみ、Rewrite無し) | False・borderline群(B1-a/b、B4-b/c)はStage2で救済見込みだが、Real-but-fixable群(B1-c/B3/B4-a)やHormuz型の複数箇所逸脱はcycle無しでは解消できず、USER_DECISION_REQUIRED残存の可能性が高い |
| γ | β + 必要時のみ局所/JA Rewrite(cycle上限2) | §13-5参照 | 楽観/中央: 節約、悲観: +¥0.60(§13-7) | Primary KPI(USER_DECISION_REQUIRED実質ゼロ)に最も近づく設計。Hormuz run_03型(複数箇所で別々のBLOCKING)もcycle2で吸収可能 |
| δ | γ + 限定self-consistency/Second Judge追加 | 常時+複数call | Cap超過確実(self-consistency常時実行はunit cost×複数倍) | ユーザー指示「コストを無視した対策は禁止」に直接抵触するため**不採用**。Stage 1 recall非決定性(§10リスク6)への対処は必要なら別トラックで、BLOCKING確定後のみの限定適用に留める設計が要る(Opus論点4、§11) |

### 13-9. 第一候補(委任_03でStage1をV4Aへ更新)

**案γ'**(Stage 1=V4A[固定追加費+¥0.294/記事、§14でSafety改善のため
採用]+BLOCK時のみStage 2+必要時のみ局所EN/JA全文Rewrite、cycle上限2)
を第一候補とする。理由: (1)優先順位①〜④のうち③まで(局所Rewrite
優先)で期待値ベースは依然Cap内(楽観・中央は節約、悲観は+¥0.84)、
(2)常時2重Checker・self-consistency常時実行(案δ)という「コストを
無視した対策」を回避できる、(3)Fableが委任文§2で既に示した第一候補
(β/γ路線)と整合する、(4)Stage 1=V4Aへの変更は「Stage 1が検出しなけ
れば下流が発火しない」という構造的制約(§14)への対応であり、Cost
Capより**Safety(重大Fact見逃し0件)を優先した結果の追加固定費**である
(委任文の優先順位「Safety最優先、その次にコスト最小化」と整合)。
worst case(tail)のCap超過(§13-7)は残存リスクとしてPhase 1実測で
検証する。

### 13-10. Cap内で困難な要素(委任_03で更新、中間報告)

+¥3 Capは、**期待値ベース(楽観・中央・悲観いずれも)では達成可能**と
判断するが、以下3点はPhase 1実測前の**未確定要素**として明記する
(勝手に膨らませず先に報告):

1. **Stage 2の真の単価が最大の不確実性要因**(§13-3)。段落±1縮小
   (§4-4)で入力トークンは記事全文渡しより減る見込みだが、削減効果の
   実測が無いため保守的見積り(¥0.30〜0.40/call)を維持している。実際に
   これより高くなる可能性がある(§13-1の実測が示すとおり、BLOCKING
   関連の判定callはharness平均より¥1超になることがある)。Stage 2単価
   が¥0.6/call超になった場合、§13-7の中央シナリオでも節約効果が消え、
   悲観シナリオ・worst case双方でCap超過の可能性がさらに高まる。
   **Phase 1の最優先実測項目**とする。
2. **worst case(§13-6、V4A反映後¥3.96/記事)はCap(+¥3)を約32%
   超過する**(V4A採用前は¥2.88[Cap内、余裕¥0.12]だった)。§5-3の
   「同一記事でJA全文Rewriteを2回使わない」制約を実装で確実に守ることが
   Cap遵守の前提条件である点は変わらないが、**V4A採用によりworst
   caseの絶対値自体がCapを超えるようになった**。§13-6の概算では発生
   確率が低い(記事あたり約1%程度)ためUSER_DECISION_REQUIRED条件3
   (恒常的な超過)には現時点で該当しないと判断するが、Phase 1実測で
   この発生率・実額を検証する必要がある(**新規、委任_03で判明**)。
3. **Stage 1のV4A化自体が固定費を+¥0.294/記事押し上げる**
   (§13-4-補)。これはSafety改善(changed_actor検出率50%→100%)の
   対価として意図的に許容した増分だが、期待値ベースの節約margin
   (特に中央シナリオ−¥0.06/記事)をほぼ消し去るほど大きい。中央
   シナリオの節約効果が「ほぼゼロ」まで縮小した点は、Checkpoint Aで
   明示的に報告する。

Cap超過が実測で確認された場合、想定される代替案(参考、実装せず):
Stage 2の入力をLedger全文ではなく該当fact_id周辺のみへさらに縮小する
(§4-4の設計判断を再検討)、cycle上限を1へ縮小する(自動完結率は
低下)、JA全文Rewriteの発火条件をさらに狭める、worst case tail
(両段階同時BLOCK+JA-origin+cycle2必要)専用の追加guard(例:
cycle1でJA全文Rewriteを使った場合はcycle2を発動せず直接Stage 4へ
[自動完結率は下がるがworst case費用を抑制できる])。いずれもSafety/
自動完結率とのトレードオフを伴うため、Phase 1実測後にユーザー判断を
仰ぐ。

### 13-11. Phase 1⑤実測反映(委任_08、Stage3実単価確定)

**実測値(§5-4-補2)**: `c_en_local`(EN局所Rewrite、replace型)は
E-1/E-2とも1 attempt解決時¥0.09〜0.18/claim(rewrite1call+recheck
1call)であり、§13-4の見積り¥0.15〜0.35/callの下限〜やや下回る水準
(escalation不要のため見積りより安価)。JA側narrow_scope型の採用案
J-1の実測costは**¥0.4569/cycle(3call: paired rewrite1+JA check1+
EN recheck1)**であり、§13-9設計時の想定(paired local rewrite
¥1.0〜1.5/cycle、旧案Bの1/3以下)をさらに下回った(実測は想定の
約半分弱)。J-2(不採用)は¥0.9598/cycleでJ-1の約2.1倍、かつ
未解決だったため採用しない。

**Cap判定への示唆**: §13-6のworst case式`c_en_local`
(¥0.15〜0.35/call)は実測¥0.09〜0.18/claimに、JA側paired local
rewriteの実測¥0.4569は既存の想定¥1.0〜1.5/cycleより有利な側に
置換できる見込みが得られた。ただし本実測はn=1〜2の小標本(claim単位
escalation未発火のケースのみ)であり、§13-6のworst case式全体の
再計算(cycle 2発火・escalation発火ケースを含む)は次回⑥(統合
dry-run)実測後に確定する(本委任では実単価の部分置換候補の報告に
留める)。

## 14. Stage 1設計判断(委任_03新設、Fable/Claude側で結論確定)

**位置づけ**: 委任文により「Stage 1の実装方法をユーザーに逐一確認
しない。KPI達成優先」と明示指定されたため、本節はユーザー確認を
待たずFable/Claude側で結論を確定する(USER_DECISION_REQUIRED非該当、
§12条件2[Safety緩和]には該当しない=改善であるため)。

### 14-1. 構造的前提(全選択肢に共通)

**Stage 1が検出しなければStage 2/3/4は一切発火しない**(委任文明記の
構造的事実)。Self-Recovery Flow全体のSafety(重大Fact見逃し0件)は、
Stage 1の検出(recall)が土台であり、Stage 2以降(materiality判定・
Rewrite・Escalation)はStage 1がBLOCKING-candidateとして拾った場合に
限り機能する。したがって「Stage 1をどう構成するか」は、Self-Recovery
Flow全体のSafety上限を決める最重要変数である。

### 14-2. 選択肢比較(S1-A/B/C/D)

| 選択肢 | 内容 | (1)重大Fact見逃し | (2)Initial BLOCK率→発動率→条件付きコスト | (3)非決定性耐性 | (4)Production採用時の変更範囲 |
|---|---|---|---|---|---|
| **S1-A** | 真のProduction Checker(V0、Prompt/schema無変更)、Trial実行時はgpt-6-luna | **changed_actor 3/6見逃し(50%)**(fixture単位gold表実測、baseline)。他カテゴリ[changed_number/scope/causality/certainty/negation/comparison/time/unsupported_new_claim]は合成fixtureで100%検出済みだが実データrecallは§10リスク6のとおり未保証 | BLOCK率は前Phase実測(B群不要BLOCK率75%)が示すとおり中程度〜高いが、changed_actorのような重大カテゴリを**そもそも拾わない**ため、Stage2/3が発動する前提のBLOCK-candidate自体が生成されない場合がある(見逃しは「発動しない」形で現れる、コストには表れないがSafety事故として現れる) | 未測定(V0のn=20 stability実測は本委任時点でhormuz_run03_standard 100%[20/20]・Meta_run03_standard 90%[18/20]、changed_actorカテゴリのn=20実測は無い) | 変更なし(Production Prompt自体が既にS1-A) |
| **S1-B(採用)** | Trial variant V4A(カテゴリ境界明確化のみ、schema/severity算出ロジック不変) | **changed_actor 5/5(100%)**、Safety群12/12(100%)維持。**残存リスク**: hormuz_run03_standard(changed_scope)がn=20でV0比悪化方向(100%→85%、Fisher p=0.23で統計的有意差なし) | call単価+30%・latency+60%(前Phase実測)。BLOCK率自体は不要BLOCK率2/4[n=1、非決定性と未分離]で、V0比横ばい〜やや改善の可能性 | V0比で明確な改善・悪化のいずれも統計的有意差なし(n=20、hormuz p=0.23、Meta p=0.49、併合p=1.0)。「測定不足」から「実測はしたが方向性が定まらない」段階 | Family X限定Trial variantとして即座にTrial利用可能。Production採用には別途Prompt変更承認が必要(§3-1明記) |
| S1-C(不採用) | V4A+一般常識許容規定の具体化(C2、前Phase「V5-A」相当) | 未実測。理論値のみ(不要BLOCK率1/4=25%へ改善する机上試算、前Phase D-補) | 理論上BLOCK率をさらに下げ、Stage2呼び出し回数を削減できる可能性 | 未実測 | Family X限定Trial variant止まりだが、Prompt変更が二重(V4A+C2)になり、Safety regressionの検証範囲が広がる |
| S1-D(不採用) | Stage1に直接materialityを出させる一体型(Stage1+Stage2統合) | 検出とmateriality判定を同一callに委ねるため、検出漏れとmateriality誤判定が独立に検証できなくなる(Opus L2レビュー#1推奨の「detect/materiality分離」に反する) | 呼び出し回数削減(理論上安い)だが未実測 | 未実測、かつ既存Trial 1/2/n=20資産(Stage1 deviation出力)がそのまま使えなくなる(再測定コストが発生) | Production Prompt全体の再設計に相当し、影響範囲が最大 |

### 14-3. 結論: S1-Bを暫定採用する(**[委任_04改訂/A14]** Phase 1実測
[§9-1③]後に最終確定)

**[委任_04改訂/A14]** Opus所見(論点2(A))により、S1-B採用根拠は
「合成fixture 1種・n=5」(Fisher両側p≈0.18)のみであり、§14-3が退けた
hormuz悪化(p=0.23)と同水準の非有意性であることが判明した。したがって
本節の結論は**Phase 1実測前の暫定採用**とし、§9-1③(negative候補7記事
のV4-A再実行+`er009_changed_actor` V0/V4-A各n=15追加実測)の結果を
もって最終確定する。実測前にV0へ戻す判断はしない(V0+pre-checkを
比較対照としてPhase 1に含めるのみ)。以下14-3の理由付けは暫定採用の
根拠として維持する。

**理由**:
1. **S1-Aは重大Fact見逃し0件というPrimary Safety KPIを構造的に満たせ
   ない**。changed_actor(actor取り違え、委任文§1で「確実に止める」と
   明記された絶対条件の1つ)を50%見逃す実測がある以上、S1-Aのまま
   Self-Recovery Flowを構築しても、Stage 2/3/4がいかに優れていても
   その50%はStage 1の時点でACCEPTABLEとして通過してしまう(§14-1の
   構造的事実)。
2. **S1-Bはこの見逃しを実測で解消する**(5/5=100%)唯一の検証済み
   選択肢であり、negative controlも劣化させない(Meta_run03_standard
   n=20でV0比改善)。
3. **S1-Cは未実測かつ二重のPrompt変更**であり、Stage 2がすでに
   False・borderline群(B1-a/b、B4-b/c)の吸収を担う設計(§7-2/7-3)に
   なっている以上、C2が狙う「不要BLOCK率削減」効果はStage 2で代替
   可能。S1-Cを追加することの限界便益(Stage2呼び出し削減によるコスト
   減)は、未検証のSafety regressionリスクに見合わないと判断し、
   **Phase 1では採用しない**(将来Phase 2以降の検討候補として保留)。
4. **S1-Dは既存Trial 1/2/n=20資産(Stage1 deviation出力、Phase 1計画
   §9-1が前提とする再利用元)を無効化し**、detect/materiality分離
   というOpus L2レビュー#1論点1の中核的推奨(Safety資産保存)に反する
   ため不採用。
5. 残存リスク(hormuz_run03_standardのn=20 V4A実測悪化方向、非有意)は
   14-4のdeterministic pre-checkで部分的に補完する。

**コストへの反映**: V4A採用により固定費が+¥0.294/記事増加する
(§13-4-補)。これはSafety改善の対価として許容する(§13-9)。

### 14-4. 検出漏れ型Safety対策(Cap内で可能な選択肢の検討)

Stage 1(V4A)は依然85〜100%のrecallに留まり(実データfixture、n=20)、
100%ではない。Stage 1が検出しなければ下流は発火しないため、検出漏れ
自体への対策を検討する。

| 選択肢 | 内容 | 費用 | 採否 |
|---|---|---|---|
| **deterministic pre-check(採用)** | Ledgerの構造化フィールド(`numeric_value`/`date_or_period`/主体名等)と記事本文を機械照合(regex/文字列一致)し、Ledgerと矛盾する数値・日付・固有名詞(actor名の置き換え等、機械照合可能な範囲に限定)を検出したら、Stage 1 LLMの判定結果に関わらず強制的にBLOCKING-candidateとしてStage 2へ送る(Stage1 LLMがACCEPTABLEと判定していても上書きする、fail-closedの追加層) | **¥0**(LLM呼び出し無し、Trial実装コストのみ) | **採用**。Opus L2レビュー#1論点4推奨5「機械的に照合可能な項目に限定すれば有効」と整合。汎用の解にはならない(scope一般化のような意味的逸脱は機械照合できない)ことを明記した上で、無料かつfail-closed方向にのみ作用する(誤って安全性を下げることがない)ため、Phase 1で実装対象に加える。実装詳細(対象フィールド・照合方式)はPhase 1委任で確定する |
| BLOCK時ではなくPASS時の限定2nd run | Stage 1がACCEPTABLEを返した場合にのみ、限定的に2回目のCheckerを実行する | Stage1 ACCEPTABLE(大多数のケース)に対して**常時発生する固定費**になる(記事の大半でACCEPTABLEが返るため、実質「毎回2重実行」に近い) | **不採用**(委任文原則どおり)。固定費が既存の+¥0.294/記事[§13-4-補]にさらに積み増しになり、Cap margin([中央シナリオ]わずか−¥0.06/記事)を即座に食い潰す |
| self-consistency(BLOCKING確定claimに限定したunion) | Opus L2レビュー#1論点4推奨2。BLOCKING相当のclaimのみ複数run union | BLOCK時のみの条件付き費用だが、**BLOCKになったclaimの安定性**を高める効果であり、**そもそもACCEPTABLE誤判定[検出漏れ]には無効**(Stage1が見逃した場合はunion対象にすら入らない) | 検出漏れ対策としては**不採用**(目的が異なる)。既存の§11-3/§11-8で「Stage1 recallの根本改善は別トラック」として保留済みの論点と整合、変更なし |

**結論**: deterministic pre-check(¥0、machine照合可能な項目限定)を
Phase 1実装対象として採用する。これによりchanged_number/changed_time/
一部のchanged_actor(固有名詞の機械的不一致)の検出漏れを追加で補完
できる可能性があるが、hormuz_run03_standardのようなscope一般化型の
検出漏れ(意味的判断が必要)は機械照合の対象外のままであり、**完全な
解決策ではない**ことを明記する。この残存リスクはPhase 1実測後も
継続的にリスク登録簿(§10)へ残す。

### 14-5. Stage 1最終確定(委任_07、Phase 1③実測結果に基づく確定)

**結論**: **Stage 1はV4-Aを最終確定とする**(S1-B、§14-3の暫定採用を
確定へ格上げ)。S1-D(一体型、§14-2で理論上は不採用としていたが、
ユーザー方針「既存方式に縛られない、QCDで最良の方法をTrialする」に
従い委任_07で実際にTrial実装・実測した)は、以下の実測結果に基づき
**Stage 1としては不採用**と確定する(Opus L2レビュー#1論点1の
「detect/materiality分離によるSafety資産保存」という推奨が、理論では
なく実測で裏付けられた)。

**(a) Safety群12 fixture(er009 9種+A2A3/A4/A5)**: S1-D 12/12
(100%)がBLOCKING確定。V0/V4Aと同水準([既存実測]V4A 12/12)。
費用¥3.0542(12 call、gpt-6-luna)。

**(b) er009_changed_actor n=15追加実測(既存n=5+新規n=10)**:
V0=7/15(46.7%、既存3/5+新規4/10)、V4A=15/15(100%、既存5/5+新規
10/10)、S1-D=15/15(100%、新規15/15)。Fisher両側検定: V0 vs V4A
p=0.00220、V0 vs S1-D p=0.00220(いずれもn=5時点のp=0.18から統計的
有意水準まで低下、A14が要求した実測完了)。**V4A・S1-Dともに
changed_actor検出でV0を統計的有意に上回ることを確認**。費用: 追加
V0 10call+V4A 10call+S1-D 15call=35call、¥4.0283(既存n=5分は
再利用、0 call)。

**(c) negative候補7記事のBLOCK率増分(V0は既存記録0 call、V4A/S1-D
新規実行)**: V0(既存)=0/7(0%)。V4A=4/7(57.1%、neg1/2/3/5がBLOCKING
確定、neg4/6/7はLEDGER_COMPLIANT)。**S1-D=6/7(85.7%、neg5のみ
QUALITY止まりでBLOCKING無し、他6件はBLOCKING確定)**。Fisher両側検定:
V0 vs V4A p=0.0699(有意水準未満だが増加傾向)、V0 vs S1-D p=0.00466
(有意)、**V4A vs S1-D p=0.559(有意差なしだがS1-Dが数値上より高い
over-block率)**。**S1-DはV4Aより不要BLOCK率が高い方向にある**
(86%>57%、既に本来ACCEPTABLEなfalse control記事に対しても、V4Aより
多くのclaimをBLOCKINGへ倒す)。費用: V4A 7call+S1-D 7call=14call、
¥3.3103(gpt-6-luna、記事によりLedger規模差で単価幅¥0.15〜0.6超)。

**(d) B群5 fixture(B1/B2_hormuz/B3/B4/Meta_run03_standard)claim単位
正解ラベル一致率(S1-D、新規5 call)**: **B3=BLOCKING(1/1一致、確定
ラベルどおり)**。**Meta_run03_standard=全4claim BLOCKING(確定ラベル
BLOCKINGと一致、ただしV4A gold[MAJORx1]よりclaim分割が細かい)**。
**B1=1 BLOCKING+2 QUALITY(V4Aが検出した2claimのうち1件[HF-009市場
動機claim、確定ラベルB1-c=BLOCKING]をQUALITYへ降格。もう1件は新規
BLOCKING[湾岸諸国貿易投資claim、V4A非検出]を独自検出)**。**B2_hormuz
=2 BLOCKING+2 QUALITY(確定ラベルはQUALITYのみだが、S1-Dは2claimを
BLOCKINGへ判定、過剰BLOCK方向)**。**B4=2 BLOCKING+3 QUALITY(V4Aが
BLOCKING確定した4claimのうち、確定ラベルB4-a[AIフォールバック機構の
新規主張、Real-but-fixable群]に対応する2claim["Meta had run a
test..."/"A person can take over..."]をいずれもQUALITYへ降格。
B4-b/c相当[human心理一般論]はQUALITY[確定ラベルどおり一致]。新規に
別claim[contract worker情報共有]をBLOCKINGへ判定)**。**正解ラベル
一致率(claim単位、目視対応付け)= 3/5 fixture(B3・Meta完全一致相当、
B1/B2/B4は部分不一致)**。費用¥1.2379(5 call)。

**(e) hormuz_run03_standard/Meta_run03_standard n=5(S1-Dのみ新規、
既存V0/V4A n=20は流用)**: hormuz_run03_standard=5/5(100%)BLOCKING
確定(V0実測85%[n=20]・V4A実測85%[n=20]と比べ、n=5では非検出0件)。
Meta_run03_standard=5/5(100%)BLOCKING確定(V0/V4A実測90%[n=20]と
比べ、n=5では非検出0件)。費用¥1.8927(10 call)。

**Stage 1最終判定の根拠**: (a)(b)(e)ではS1-DはV4Aと同水準(100%)の
recallを示すが、(c)ではS1-DがV4Aより高い不要BLOCK率(86%>57%)を示し、
(d)ではS1-Dが**Real-but-fixable群の確定BLOCKINGラベル(B1-c/B4-a)を
QUALITYへ誤って降格**させる実例が2件観測された(V4A→Stage2の2段構成
では、Stage2 rubric基準1[Ledgerが別原因・別主体を明記]がこれらを
BLOCKING確定させることを期待していたが、後述§4追記のとおり実際の
per-claim Stage2でも同様の降格が観測されており、これはS1-D固有の
欠陥ではなくStage2 rubric自体の較正課題である可能性が高い。ただし
S1-Dは「検出とmateriality判定を同一callで行う一体型」であるため、
この種の誤判定を第二の独立callで訂正する機会が構造的に存在しない
[Stage2を経由しないため]。V4A→Stage2の2段構成なら、Stage2の判定が
誤っていても「Stage2を改善する」余地が残るが、S1-Dは1callで確定して
しまうため、Opus L2レビュー#1が指摘した「detect/materiality分離に
よるSafety資産保存」の実利が実測で裏付けられた)。

**結論**: Stage 1=V4A(確定、変更なし)。S1-Dは検討対象として実測した
上で不採用(§14-2の理論的判断が実測で補強された)。S1-D関連の実装
(`er052_open233_self_recovery_s1d_trial_01.py`)はTrial記録として
保持するが、Self-Recovery Flowの構成(§3-0)には組み込まない。

## 15. Opus L2レビュー#1(委任_04)への対応(採否・反映節、[委任_04新設])

**位置づけ**: `docs/pm/opus_l2_review_open233_self_recovery_01.md`
(Opus L2批判的レビュー#1、read-only、runtime evidence: 実行モデル
`claude-opus-5[1m]`)の指摘への、Fable判定(採用/不採用/ユーザー判断
送り)と反映節の対応表。API呼び出しなし・¥0・Production非接続・
実装なし(本節は設計書改訂のみ)。

### 15-1. 採用(Phase 1前に設計へ反映済み)

| # | Opus所見(論点) | Fable判定 | 反映節 |
|---|---|---|---|
| A1 | 論点5(A)(B): Recheckで`prior_issues`未使用、既存fail-closed gateが無言で外れている | 採用。継続条件=`LEDGER_COMPLIANT`かつ`all_prior_issues_resolved==True` | §3-0/§6-1 |
| A2 | 論点2(C): precheck由来検出がfloor空振りしStage2で降格され得る | 採用。`detected_by`フィールド追加、precheck由来はfloor扱い(FP率次第で弱め分岐を併記) | §3-1/§4-3 |
| A3 | 論点2推奨1/論点8推奨1: precheck FP率が未測定のままPhase1へ入る | 採用。§9-1①(¥0、最優先)に配置 | §9-1 |
| A4 | 論点1(A)(D)/論点4推奨2: EN局所RewriteがJA/EN乖離を生む、cycle indexでmechanism選択が支配的ケースと噛み合わない | 採用。origin別選択+paired local rewriteをPhase1第一級項目へ | §5-1/§5-2/§5-3/§5-4 |
| A5 | 論点7推奨1: 同一claim再発でもcycle2を無条件発火 | 採用。同一claim/fact_id再BLOCKINGは即Stage4 | §3-3/§5-3/§6-1 |
| A6 | 論点6(B): §13-6が§3-5と不整合・二重計上疑い、JA-origin比率根拠薄弱 | 採用。式化、JA-origin実測80%(n=5)へ改訂、BLOCK率はV4A実測後に置換 | §13-6 |
| A7 | 論点1(D): Stage4条件表にsymbol gate/`all_prior_issues_resolved`/予算abort等の欠落 | 採用。コード上の例外型と1対1対応表を新設 | §6-1 |
| A8 | 論点3(A): Stage2入力にexplanation/severity/10 flagsを渡しanchoringを生む | 採用。除外し、floor判定のみ外側で使用。ヘッジ語regexで段落範囲拡張 | §4-4 |
| A9 | 論点1(C)/論点3推奨2: Stage2 call数=claim数がコスト膨張要因 | 採用(比較実施)。batch化を主案、per-claimを比較対照 | §3-5/§4-1/§9-1④ |
| A10 | 論点3(C)(E): ACCEPTABLE定義の新規性基準が曖昧、changed_certainty不整合 | 採用。「Ledgerに無い新規の」と明文化、changed_certaintyをfloorへ追加 | §4-2/§4-3 |
| A11 | 論点4(A)(D)/論点5推奨3: Rewrite型分類が無く、guard抵触時の扱いが過剰に厳しい | 採用。`rewrite_kind`追加、機械検証追加、段階的フォールバック | §4-5/§5-2 |
| A12 | 論点6推奨1: prompt cachingが未検討 | 採用(実測項目化)。Phase1④で受理可否・削減率を実測 | §9-1④/§13 |
| A13 | 論点5【Safetyリスク】/論点8推奨3: Escalation0件の内訳が区別できない | 採用。内訳測定項目を必須化 | §8-1 |
| A14 | 論点2推奨1/論点8(C): V4A採用根拠が単一fixture・n=5で弱い、BLOCK率実測が計画に無い | 採用。§9-1③へ実測を追加し、Stage1 variant最終確定を実測後に延期 | §9-1③/§14-3 |
| A15 | 論点8(C): モデル依存/非依存の結論の優先順位が未整理 | 採用。モデル非依存の結論(prior_issues/precheck FP/JA-EN乖離/call数)を優先確定する方針を明記 | §9-1 |
| A16 | 論点8(D): Production化後の継続監視策が未定義 | 採用(Phase2設計項目として記録、採否はユーザー) | §11-8 |

### 15-2. 不採用(理由付き)

| Opus所見(論点) | 内容 | 不採用理由 |
|---|---|---|
| 論点6推奨6/論点1(A)関連 | cycle上限を1へ下げる | 実観測パターン(Hormuz run_03型: Advanced解消→Standardで新claim)にcycle2が必要であり、上限1はKPI(Escalationゼロ)を確定的に落とす |
| 論点3推奨1関連の代替案(§13-10代替案1) | Stage2入力のLedgerを部分化(該当fact_id周辺のみ) | B3型(HF-007のように別条件が離れた箇所にある場合)を見逃すリスクがあり、fail-closedの原則に反する |
| 論点1推奨4/論点1(C) | Stage2/Stage3の統合(3段階化、materiality判定+rewrite_hint生成を1 callへ) | 検証可能性の観点で分離を維持(Opus自身も同結論)。統合すると降格判定callが常にrewrite出力トークンを払うため期待コストも悪化する可能性が高い |

### 15-3. ユーザー判断事項として提示(Fableが決めない、Checkpoint Aで提示)

| 論点 | 内容 | 該当条件 |
|---|---|---|
| 論点8(A)推奨2 | KPI判定方法の再定義(記事単位0件→事象単位推定によるEscalation率の信頼区間上限) | 条件1(KPI変更) |
| 論点6(D) | Cap定義の解釈(LLMコストのみかTTS等downstream込みか) | 条件1(KPIの解釈) |
| 論点8(B)1 | QUALITY通過(現行STOPしていたB2型を人間を通さず公開すること)がSafety緩和に該当するか | 条件2(Safety緩和)該当可能性 |

**設計書での扱い**: 上記3点は§12(USER_DECISION_REQUIRED条件)へ追記
済み。現行KPI文言はそのまま維持し、事象単位推定・Escalation0件内訳を
追加報告項目として併記する(§12/§12-1/§8-1)。
