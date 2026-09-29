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
    (**Stage 1 Production Promptは不変**)。
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
  Stage 1: Initial Check(既存Production Checker、Prompt/schema不変)
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

Stage 4: Final Escalation(cycle上限[最大2]到達後もBLOCKING、または
JA Fact Check自体がSTOPした場合) → USER_DECISION_REQUIRED
```

### 3-1. Stage 1: Initial Check

- **入力/出力**: 既存Production Deviation Check(`vfl01.run_deviation_
  check()`、`DEVIATION_PROMPT_TEMPLATE`、`hook_aware=False`、Family X
  経路)をそのまま使う。**Prompt本文・schema・severity算出ルール・
  モデル(gpt-5.6-luna)は一切変更しない**。
- **分類**: 既存の二値出力(`overall_status`)をSelf-Recovery Flowの
  3値語彙へ写像する。`LEDGER_COMPLIANT`(MAJOR無し)→**ACCEPTABLE**
  (継続、Stage 2以降へ進まない)。`LEDGER_DEVIATION`(MAJOR 1件以上)→
  **BLOCKING-candidate**(Stage 2へ)。**現行Stage 1アーキテクチャは
  QUALITYを直接出力しない**(materiality軸がないため)。QUALITYという
  出力値はStage 2でのみ生成される。これは既存Fable判定(c)「materiality
  軸はStage 1に持ち込まない」と整合する設計上の制約であり、本書では
  明示的にそのまま扱う(Stage 1で「ACCEPTABLE/QUALITY/BLOCKING分類」を
  行うという委任文の表現は、実装上は「ACCEPTABLE(継続) / BLOCKING-
  candidate(Stage 2で3値化)」の2値ルーティングとして実現する)。
- **deterministic層**: 既存の`_apply_deviation_post_hoc_validation()`
  (フラグ全falseでMAJORならMINORへ自動降格)はそのまま維持。
- **loop上限**: Stage 1自体はretryしない(1回のみ)。既存の「MAJOR時
  must-fix retry1回」(現行Production)は、Self-Recovery Flowでは
  Stage 3 Rewriteの一形態として再定義する(§5)。
- **STOP条件**: なし(Stage 1単独ではSTOPしない。BLOCKING-candidateは
  必ずStage 2へ渡す)。
- **ログ項目**: `article_id`/`writer_stage`(advanced/standard)/
  `deviation_id`/`claim_in_article`/`10 category flags`/`severity`/
  `origin`/`related_fact_id`/`cost_jpy`/`elapsed_seconds`/`raw_response_id`。

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

### 4-4. 入力

- Ledger全文(該当fact_idの前後だけでなく全文。理由: 別の原因/別の
  条件が離れた箇所に記載されている場合があるため[B3のHF-007
  conditionsが好例]、部分入力では見逃すリスクがある)。
- source context(JA原文、origin=ja_source/translationの場合のみ、
  既存`source_article_text`引数をそのまま流用)。
- 対象claim(Stage 1の`claim_in_article`)。
- Stage 1のdeviation出力全体(10 category flags/severity/explanation/
  origin/related_fact_id)。
- 前後sentence(±1文、記事全文からの抽出。局所的な文脈のみで判定
  できない場合に備え、記事全文も併せて渡す)。

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

## 7. gold(最終到達状態ベース)とfixture群の再編

**位置づけ**: 以下は全て「候補gold(ユーザー確認待ち)」であり、本書が
独自に確定するものではない(§2(b))。既存fixture単位gold表
(design_open233_checker_redesign_trial_01.md §2)・claim単位gold
候補表(同§2-補)を変更するものではなく、それらを「Self-Recovery Flow
のどのStageで、最終的にどの状態へ到達することが期待されるか」という
軸で再編した新しい視点の表である。

### 7-1. Safety群(Stage 1/2で必ずBLOCKING維持、その後Rewrite→PASSが期待)

| fixture | 現行gold | 理由(floor/rubric) | 期待Stage経路 |
|---|---|---|---|
| er009_changed_number/actor/negation/comparison/time(5種) | BLOCKING | deterministic safety floor該当(§4-3) | S1 BLOCK→S2 floor→BLOCKING確定(LLM判定を待たず)→S3 Rewrite→S1 Recheck→PASS |
| er009_changed_scope/causality/certainty/unsupported_new_claim(4種) | BLOCKING | floor対象外だがrubric基準1(Ledgerとの明示矛盾)に該当 | S1 BLOCK→S2 rubric判定でBLOCKING→S3 Rewrite→S1 Recheck→PASS |
| A2A3/A4/A5(実データ、価格反転・対象取り違え・意味反転) | BLOCKING | rubric基準1(Ledger矛盾) | 同上 |
| hormuz_run03_standard(HF-009 changed_scope) | BLOCKING(Confirmed) | rubric「scopeと矛盾」該当(Brent先物→市場全体への一般化) | S1 BLOCK(recall問題あり、§10)→S2 rubric判定でBLOCKING→S3局所Rewrite→S1 Recheck→PASS |
| Meta_run03_standard(negative control) | BLOCKING | rubric基準1 | 同上 |

### 7-2. False・borderline群(Stage 2でQUALITY/ACCEPTABLE通過が期待、Rewrite不要)

| claim | Opus評価 | 期待Stage経路 |
|---|---|---|
| B1-a(ホルムズ海峡=重要航路) | ACCEPTABLE | S1 BLOCK(過剰検出)→S2 rubric「一般常識」でACCEPTABLE→継続 |
| B1-b(原油高→ガソリン等波及) | ACCEPTABLE | 同上 |
| B2(料金案消滅と価格回復の因果連結) | QUALITY(ユーザー暫定gold) | S1 BLOCK→S2 rubric「Ledgerが保証しない関係付け」でQUALITY→継続 |
| B4-b/c(人間心理の一般論・AI/人間判別への関心) | ACCEPTABLE〜QUALITY | S1 BLOCK(過剰検出)→S2でACCEPTABLE/QUALITY→継続 |

### 7-3. Real-but-fixable群(Stage 2でBLOCKING確定、Rewrite→PASSが期待)

| claim | Opus評価 | 理由 | 期待Stage経路 |
|---|---|---|---|
| B1-c(市場動機・価格回復理由の断定) | BLOCKING寄り(material) | HF-011 notesが因果推論を明示禁止 | S1 BLOCK→S2 BLOCKING確定→S3局所Rewrite→S1 Recheck→PASS |
| B3(接続詞so、政策決定理由の取り違え) | BLOCKING(gold支持) | HF-007 conditionsに別原因明記(rubric基準1) | 同上 |
| B4-a(AIフォールバック機構の新規主張) | BLOCKING | MUSE-HC-006の範囲外の製品仕様捏造 | 同上 |
| B4-d(テスト結果の確実性強化、V4A run) | QUALITY〜BLOCKING(境界、gold未確定) | certainty変化、floor対象外 | S1 BLOCK→S2境界判定(要Trial実測で分布確認)→BLOCKINGならS3→PASS、QUALITYなら継続 |

### 7-4. Normal群(Stage 1またはStage 2で通過が期待、既にAPI¥0で実証済み)

negative claim候補16件(`docs/pm/negative_claim_candidates_open233_
01.md`)。現行Production実行で既に`LEDGER_COMPLIANT`(deviations=[])
として通過した実績があるため、Self-Recovery Flow下でも**Stage 1のみで
ACCEPTABLE、Stage 2以降に到達しないことが期待**される。ただし
Standard/Advancedの表現断定度によって同一Ledgerでも判定が割れる実例
(候補1〜3 vs 同一runのAdvanced版B4 fixture)があるため、非決定性に
より稀にBLOCKING-candidateとしてStage 2へ到達する可能性は残る
(その場合はFalse・borderline群と同じ経路でACCEPTABLE/QUALITYへ戻る
ことが期待される)。

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

Opus論点2推奨1に従い、claim単位で再定義する: `不要BLOCK率 = gold=
ACCEPTABLE/QUALITYのclaimがStage 1でBLOCKING判定された率`。目標値は
設定せず(前Phaseの≤25%は撤回、診断のみ)、Self-Recovery Flowが
False・borderline群をどれだけStage 2で正しく拾えているかの内部指標
として参照する。

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

## 11. Opus L2に問う論点(次回Opus発火時)

1. Stage 2 Second Judge(独立Prompt・2段階呼び出し)の設計は、前Phase
   Opus論点1推奨4の踏襲だが、deterministic safety floor(5フラグ)の
   選定根拠(§4-3)は十分か。floor対象外のchanged_causality/changed_
   scope等でmaterialなケース(B3/hormuz_run03_standard)を、rubric
   文言だけで安全に止められるという設計判断は妥当か。
2. Stage 3局所Rewrite(§5-2、Phase 1では未実装、設計提案のみ)は、
   全文再生成(既存案B/既存must-fix retry)と比較してSafety/生産性の
   トレードオフ上、優先的に実装する価値があるか。Hormuz run_03の
   実例(全文再生成が新しい逸脱を誘発)は局所Rewriteの必要性を示す
   十分な根拠か、それとも単なるn=1の偶発事象か。
3. cycle上限(記事あたりRewrite最大2回)は、Safety(重大fixture見逃し
   0件維持)と生産性(USER_DECISION_REQUIRED実質ゼロ)のバランスとして
   妥当か。2回で足りないケース(Hormuz run_03のような「2箇所で別々の
   ja_source MAJOR」パターンが3箇所以上に増える場合等)への備えは
   十分か。
4. Stage 1のrecall非決定性(n=20実測85〜100%)を本Flowが改善しない
   という設計判断(§10リスク6)は許容できるか。Self-consistency
   (前Phase Opus論点4推奨2、Stage 1の複数call union)をどのタイミング
   でこのFlowへ組み込むべきか、あるいは別トラックで進めるべきか。
5. Stage 4 Escalation発生率を実質ゼロに近づけること自体が、人間確認
   ゼロの記事が増えることを意味する。これは「安全≠成功」原則
   (PM_GOVERNANCE.md 6節)との関係でどう位置づけるべきか(Self-Recovery
   Flowで継続した記事は、従来なら人間が見ていたはずのGrayゾーンの
   判断を全てシステムに委ねることになる)。
6. Production Checkerモデル(gpt-5.6-luna)とPhase 1 Trialモデル
   (gpt-6-luna)の不一致(§10リスク8)は、Phase 1の結論をPhase 2
   (Production相当10〜20記事)へ一般化する上でどの程度の障害になるか。
7. HOOK_CLAUSE整合(§10リスク7)について、Stage 2/Stage 3のPrompt
   文言を将来共通Promptへ統合する際の優先順位付け(前Phase Opus論点5
   推奨4「HOOK_CLAUSE優先、それ以外は重複true原則」)は、本Flowの
   materiality軸導入とどう組み合わせるべきか。

## 12. ユーザー判断11該当有無

**本設計書自体はUSER_DECISION_REQUIRED非該当**(文書のみ、API呼び出し
なし、実装なし、Production変更なし、¥0)。

ただし、次のPhase 1 Trial実行(次回委任)着手前に、以下の点について
ユーザー確認を得ることを**Checkpoint Aで提案する**(独断で進めない):

- 本設計のStage 2は、前PhaseのOpus L2レビュー#1論点1で「Trial variant
  としてBLOCKING判定基準そのものを変更することの事前了承が必要
  (USER_DECISION_REQUIRED該当)」と明示的に指摘されたmateriality軸
  導入(旧C1相当)を前提としている。Family X限定・Production非接続の
  Trialとして、この materiality軸導入(Stage 2として独立Prompt化した
  形)を進めてよいか。
- 不要BLOCK率≤25%という前Phase主要受入条件を撤回し、Primary KPIを
  「USER_DECISION_REQUIRED=0件」へ変更する(本書§1のユーザー指示を
  正式にDECISION_LOGへ記録済み、確認のみ)。
- gold候補表(§7)は最終到達状態ベースの新しい整理であり、既存gold
  表(前Phase design書§2/§2-補)を上書きするものではないことの確認。

該当なしのため、本書提出をもって次のPhase 1 Trial実行(有料API呼び出し
を伴う委任)へ進めることをFableへ提案する。
