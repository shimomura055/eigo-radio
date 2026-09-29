# OPEN-233-SELF-RECOVERY-TRIAL-01: Production Self-Recovery Flow 設計書

**Status**: `DESIGN_READY_FOR_OPUS_L2`(本書は設計のみ。API呼び出し¥0、
Production非接続、実装なし)。委任_01(2026-09-30)で作成。

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
   │         │          再実行=fail-closed、局所チェックに限定しない)
   │         │
   │   ┌─────┴─────┐
   │   │             │
   │ ACCEPTABLE   BLOCKING-candidate(claimが同一/新規いずれも)
   │   │             │
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
  `stage1_variant`(Trial期間中は`V4A`固定)。

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
  即Stage 4。

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
- **ACCEPTABLE**: 新しい固有名詞・数値・時期・主体・因果を一切加えず、
  Ledgerが確認した事象の一般常識レベルの背景説明・条件付きの一般論に
  とどまる。
- **tie-break(fail-closed)**: 上記のどれに該当するか迷う場合は
  BLOCKINGとする(LLM Prompt本文にこの一文を明記)。

### 4-3. deterministic safety floor(§2で確定済み、再掲)

Stage 1のdeviationレコードで`changed_actor`/`changed_number`/
`changed_negation`/`changed_comparison`/`changed_time`のいずれかが
`true`の場合、Stage 2はBLOCKING以外を出力してはならない(LLM出力に
関わらずpost-hocでBLOCKINGへ強制上書き)。この5フラグを選んだ根拠:
前Phase Trial 2 Step1(changed_actor n=5)でSafety 100%を達成した
実績がある「主体・数値・否定・比較・時期」の直接改ざんは、Ledgerとの
矛盾が機械的に一意(paraphraseの余地が最も小さい)であり、Second Judge
という追加LLM判定を経由させるリスクに見合わない。**changed_scope/
changed_causality/changed_certainty/changed_fact/unsupported_new_claim
の5種はfloor対象外**(materiality判定に委ねる。B3[changed_causality]/
hormuz_run03_standard[changed_scope]のようにfloor対象外でもmaterialな
ケースがあることは、Prompt本文のBLOCKING基準1「Ledgerが別の原因を
明記しているのに異なるものを述べる」「scopeと矛盾する」で個別にカバー
する設計とする)。

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
- Stage 1のdeviation出力全体(10 category flags/severity/explanation/
  origin/related_fact_id)。
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
  "reasoning_summary": string  # 短い理由(Trial観測用、判定には使わない)
}
```

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

## 5. Stage 3 Automatic Rewrite設計

### 5-1. 段階別方針

**JA側(origin=ja_source)**: 既存案B(`er012_e_family_entertainment_
two_level_runner_01.py::run_writer_stage()`のJARecheckRequiredError
捕捉→`jaw.run_ja_writer_o_r1_r2()`をmust_fix付きで実行→Original→
R1→R2→JA Fact Checkの全体を再生成)を**Phase 1のJA側Rewrite実装として
そのまま再利用**する(コード変更なし、既にProduction code)。この経路
はStage 2のBLOCKING確定を経てから発火する点が既存案Bとの違い(既存は
Stage 2を経由せず、ja_source MAJORが検出された瞬間に無条件で発火)。

**局所Rewrite候補(設計のみ、Phase 1では未実装)**: 現行案Bは「Original
段の該当claimに関する箇所だけ」をmust_fixで指定しつつも、Original→
R1→R2の全段を再生成するため、**該当claimと無関係な箇所まで変わり得る**
(Hormuz run_03で、Advanced側は案Bで解消したのに、Standard側で全く
別のclaim[HF-009関連]が新規にja_source MAJORとして検出された事例は、
この「全文再生成が新しい逸脱を生む」リスクの実例)。より局所的な案
(JA Original段のうち該当paragraphのみをmust_fixで再生成し、他
paragraphはR1/R2をスキップしてOriginal→即座に確定)は、JA Writer O
の既存構造(Original→R1→R2は文体洗練の連鎖であり、paragraph単位の
部分スキップは現行実装に存在しない)を変更する必要があるため、**Phase
1のスコープ外**とし、Phase 2以降の改善候補としてOpus L2へ問う
(§11)。

**EN側(origin=translation、Advanced/Standard内で新規に生じた逸脱)**:
現行Productionの「must-fix retry 1回」(`adv_gen.generate_family_x_
faithful_translation(..., must_fix=...)` / `std_gen.generate_family_
x_standard_a2_no_heading(..., must_fix=...)`)は**全文再生成**であり、
局所編集ではない。Self-Recovery Flowでは、これを**Phase 1のbaseline**
として維持しつつ(実装コストゼロ、既にProduction code)、**局所Rewrite
を優先候補として設計する**(以下)。

### 5-2. 局所Rewrite(EN側、設計提案。Phase 1 Trialで新規実装・検証対象)

- **入力**: 記事全文のうち、Stage 2の`rewrite_hint`が指す該当claimを
  含む文±1文のみを抽出し、そのローカルcontext・Ledger該当箇所・
  `rewrite_hint`を渡して**その部分だけ**の書き換え文を生成させる。
  記事の他の部分は一切渡さず、生成後にプログラム側で文字列置換する
  (LLMに全文を書き直させない)。
- **利点**: 全文再生成による「無関係箇所での新規逸脱」を構造的に
  防げる(Hormuz run_03のStandard側新規MAJORのような事象を減らせる
  可能性が高い、ただし未検証)。
- **guard(構造破壊防止)**: 置換後、既存`sc.split_family_x_article_
  text_v2()`のNG条件(`TOO_FEW_PARAGRAPHS`/`NG_MISSING_TITLE`/
  `NG_MISSING_IN_ONE_LINE`/`NG_HEADING_IN_BODY`)をそのままguardとして
  再利用する。置換後にNGが出た場合、Rewrite自体を失敗として扱い、
  **cycleを1消費した上でStage 4へフォールバック**する(段落数retry
  [既存の別axis、1回]は温存し、局所Rewrite失敗を段落数retryの
  対象にはしない=軸を混在させない)。
- **Recheckの範囲**: **全文Checker(fail-closed推奨)**。局所編集の
  範囲だけを再チェックする案(コスト減)も検討したが、Stage 1 Prompt
  は記事全文とLedger全文を突き合わせる設計であり、局所的な再チェック
  用の別Promptを新設すると「新しいPromptがSafety regressionを生む」
  リスクをStage 2に続いて二重に抱えることになるため、**Phase 1では
  採用しない**(全文Checkerを毎回フルで再実行する。コスト増だが
  Safety最優先)。

### 5-3. loop上限・順序

- 記事あたり最大2 cycle(§3-5)。1 cycle目でJA側Rewriteを使った場合、
  2 cycle目はEN側局所Rewrite(または既存全文must-fix retryのいずれか、
  §9で確定)に限定する(**同一記事で案Bを2回使わない**、既存の
  「1回上限」思想を尊重しつつ、2つ目の異なる原因への対応余地だけを
  追加する設計)。
- Rewriteは常にStage 2でBLOCKING確定した後にのみ実行する(Stage 2を
  経ずに即Rewriteしない。これにより「本当にmaterialか」を必ず一度
  問い直してから書き換えるため、無駄なRewrite回数を削減する)。

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

### 9-1. Phase 1(既存fixture/artifact reuse、次回委任で実施)

**目的**: Stage 2/Stage 3の設計が既存fixtureに対して機能するかを、
Stage 1の再課金なしで検証する。

- **Stage 2単体検証**: 既存Trial 1/2/n=20のdeviation json
  (`er051_output/open233_checker_trial_01/trial_01/`、`trial_01_
  step2_diag/`、`trial_02/`、`trial_03_stability_n20/`)から、
  BLOCKING-candidateとして保存済みのdeviationレコードをそのまま
  Stage 2の入力として再利用する(Stage 1呼び出し不要、¥0)。対象
  レコード数(概算): Safety群(重大fixture12種+changed_actor n=5、
  複数MAJORを含むためdeviation件数はfixture数より多い)約20件+B群
  (V2/V3診断10 call+Trial2 V4A 5 call由来のdeviation)約20〜25件=
  **合計約40〜50件のStage 2判定を新規に実行**。
- **Stage 3検証**: Stage 2でBLOCKING確定した候補のうち、Real-but-
  fixable群(B1-c/B3/B4-a/B4-d)+Safety群の代表例(hormuz_run03_
  standard実データ+er009代表3〜4種)を対象に、実際のRewrite→Recheck
  サイクルを実行する(こちらはStage 1相当のRecheck callが新規に
  発生するため有料)。想定件数: 約12〜18 cycle。
- **費用見積(概算、要実測)**: 公式単価gpt-6-luna(In $0.10/Cached
  $0.01/Out $0.50、為替¥156.88/$換算)を基準に、Stage 2は入力が
  claim単位で短い(Stage 1の1/3〜1/2程度のトークン量と推定)ため
  1 call約¥0.10〜0.20、40〜50件で**約¥6〜10**。Stage 3のRewrite+
  Recheckは1 cycleあたりRewrite(writer regen相当、¥0.3〜0.8)+
  Recheck(Stage 1相当、¥0.25〜0.4)で約¥0.6〜1.2、12〜18 cycleで
  **約¥8〜22**。**Phase 1合計概算: 約¥15〜35**(総枠¥400のうち
  少額、Guardrailは委任文で別途設定)。この見積もりは前Phase実測
  単価からの外挿であり、Phase 1実行後に実測値へ更新する。
- **モデル**: gpt-6-luna(前Phase Trial資産との直接比較のため統一、
  §4-6参照)。Production Stage 1のgpt-5.6-lunaとの差異は既知の
  未解決事項として記録し、Phase 2で扱う。
- **Guardrail**: 次回委任で個別設定(委任文の慣例どおり、想定費用の
  1.5〜2倍程度を上限とし、超過見込みでSTOP)。

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

### 13-6. Worst case / P95(委任_03でV4A反映へ更新)

期待値とは別に、稀な記事でCapを超過しないかを確認する。

**設計上の制約(§5-3)を守った場合**(cycle 1でJA全文Rewriteを使ったら
cycle 2はEN局所Rewriteのみ、同一記事でJA全文Rewriteを2回使わない、
Recheckは全てV4A単価):
worst case(cycle部分) = cycle1(Stage2 2call¥0.70+JA全文Rewrite¥4.02+
2段recheck¥1.274[V4A]=¥5.994)+cycle2(Stage2 2call¥0.70+EN局所
Rewrite2件¥0.70+recheck2件¥1.274[V4A]=¥2.674)=**¥8.668**。現行が
同じ記事に対し1 cycleのみ実行してSTOPする費用(JA全文Rewrite¥4.02+
recheck¥0.98[現行はV0のまま]=¥5.00)を差し引くと、cycle部分の純増分
≈¥3.668/記事。これに**Stage1固定費増分¥0.294/記事**(§13-4-補、
新方式は毎回V4Aで2 call実行するため、現行のV0 2 callとの差分が全記事に
発生)を加えると、**純増分worst case(V4A反映後) ≈ ¥3.96/記事**
(**+¥3 Capを約32%[¥0.96]超過**、V4A採用前の¥2.88[Cap内、余裕¥0.12]
から悪化)。

**発生確率(概算、中央シナリオの独立近似)**: この worst caseは
「Advanced/Standard**両方**がBLOCK(35%×35%≈12.3%、独立仮定の粗い
近似)」×「JA-origin(40%)」×「cycle 2まで必要(20%)」の複合条件で
発生する稀な尾部事象であり、概算発生率は**記事あたり約1%程度**
(粗い近似、Phase 1実測が必要)。委任文のUSER_DECISION_REQUIRED条件
3-3「worst case/P95が**恒常的[稀な例外でなく一定割合]**に+¥3を超える」
には現時点では該当しないと判断するが(尾部確率が低いため)、**この
判断はPhase 1実測前の概算に基づく**。Phase 1実測でこのtail確率が
想定より高いと判明した場合は直ちに報告する。

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

### 14-3. 結論: S1-Bを採用する

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
