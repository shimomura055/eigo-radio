# OPEN-233-CHECKER-REDESIGN-V02-01: Ledger / Deviation Checker 根本再設計案 v0.2

**Status**: PROPOSED / REVIEW(設計のみ、Production code・Checker Prompt・
severity・routing・Ledger schema・SSOTの変更なし。Production Trial未開始。
API呼び出しなし、¥0)。本書はv0.1(ChatGPT素案)への
`LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_REPORT.md`(Claude批判レビュー)
と`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`§Phase B(実測データ)を統合し、
v0.2として再構成したものである。★は★ユーザー判断が必要な事項(第14章に集約)。

**机上シミュレーション**: 本書の表の一部は、既存`er050_output/
gpt6_checker_comparison_trial_01/`配下の実行済みrun json(構造化された
`severity`/10フラグ/`origin`/`related_fact_id`、67件のdeviationレコード、
84 run file由来)へ候補ruleを機械的に適用した結果である
(scratchpad自作スクリプト`simulate_rules_c233.py`、API呼び出しなし、
repo外)。既存Production記録(REPORT記載のFamily X実運用A/B群15件)と
GPT-6 Trial fixture記録の両方を出典として明示し、混同しないよう表ごとに
出典欄を付す。

---

## 1. 問題構造の再整理(Evidence付き)

### 1-A. 過剰BLOCK

| # | 事例 | 内容 | category/origin | Evidence |
|---|---|---|---|---|
| B-1 | 原油→ガソリン価格ブリッジ文(**4回独立発生**) | JA Writer Prompt自身が要求するブリッジ文(`jaw.py:58`)が`unsupported_new_claim`でMAJOR | ja_source | `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`第3章B-1、`er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/ja_writer/audit/deviation_checks/ja_original_attempt1.json`ほか3件 |
| B-2 | Hormuz「料金案消失→原油下落せず」 | `changed_causality`、HF-011のnotes_for_writer明示禁止パターンと同型。origin=ja_source | ja_source | `er019_output/family_x_refresh_e2e_01/hormuz/run_02/b1b/audit/deviation_checks/advanced_attempt1.json`。GPT-6 Trial Step2ではn=1再実行で新旧ともLEDGER_COMPLIANT(検出自体消失、`er050_output/gpt6_checker_comparison_trial_01/step2/B2_hormuz/*/run_1.json`) |
| B-3 | 接続詞"so"による因果連結 | 2つの独立事象を単一因果に結ぶ、HF-007相当 | ja_source | `er037_output/family_xy_concreteness_control_trial_01/hormuz/task_b_cleanup/B1_deviation.json`。GPT-6 Trial Step2で新旧完全一致(severity/flag/origin/fact_id、`er050_output/.../step2/B3/*/run_1.json`) |
| B-4 | Meta従業員→一般読者心理への一般化3件 | `unsupported_new_claim`中心 | ja_source×2/translation×1 | `er019_output/family_x_b3_production_wiring_01/run_01/b1b/audit/deviation_checks/advanced_attempt1.json` |

本シミュレーション(Table D、後掲)で確認した事実: B1/B3/B4のMAJORレコードは
いずれも「changed_causalityまたはunsupported_new_claim等、単一または複数flag」
の組合せであり、**GPT-6モデルへの変更だけではこれらのflag構成自体は変わらない**
(B3は新旧で完全一致)。不要BLOCK率(B群4件のLEDGER_DEVIATION維持率)は
GPT-6 Trialで**baseline 75%=gpt-6-luna 75%、同値**(`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`
§Phase B-7)。**モデルを強くするだけでは過剰BLOCKは解決しなかった**という
ユーザー既述の前提は、本Trial実測データで裏付けられる。

### 1-B. 重大見逃し

| # | 事例 | 内容 | Evidence |
|---|---|---|---|
| A-1 | JA「ロールバックされます」(未来形、上流ドリフト)を英訳も継承 | Checkerが2回とも誤ってCOMPLIANT判定(検出漏れ、severity設計の対象外) | `NEWS-FAMILY-X-B3-ADVANCED-RETRY-ROOTCAUSE-01_REPORT.md`§3/§9-B |
| changed_actor MISS | `changed_actor=true`なのにseverity=MINORのまま出力 | baseline(gpt-5.6-luna)は**6回中6回(0%)系統的に見逃す**(n=1+n=5計6回、post-hoc非対称のためMINOR→MAJOR補正なし) | `er050_output/gpt6_checker_comparison_trial_01/summary_step1_er009_changed_actor_n5.json`、REPORT§Phase B-6 |
| category検出自体のMISS | gpt-6-lunaはn=1実行で`changed_actor`フラグ自体をfalseと判定(完全に検出しない) | `er050_output/gpt6_checker_comparison_trial_01/step1/er009_changed_actor/gpt-6-luna/run_1.json` |

**GPT-6での変化**: changed_actorカテゴリの検出力はgpt-6-lunaの方が明確に高い
(3/6=50% vs baseline 0/6=0%、REPORT§Phase B-6)。ただしgpt-6-lunaも**半数は
なお見逃す**。B4(4件中検出できた件数)はgpt-6-lunaの方がbaselineより
**さらに少ない**(2件 vs 3件、うち1件はfact_id重複)。モデル変更は
category単位で改善/悪化の両方を生み、一様な安全性向上ではない
(REPORT§Phase B-9〜B-12)。

### 1-C. 非決定性

| # | 事例 | Evidence |
|---|---|---|
| 同一inputがCOMPLIANT↔MAJOR | Hormuz run_02: JA R2 Fact Check=`LEDGER_COMPLIANT`(0件) vs 同一論点のEN Advanced Deviation Check=`LEDGER_DEVIATION`(MAJOR、HF-011) | `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`第7-1章 |
| Advanced/Standardで判定差(同一JA由来) | GPT-6 Trial Step3: hormuz_run03 advanced(gold=COMPLIANT)はbaselineが5/5完全一致・gpt-6-lunaは4/5(80%)。standard(gold=MAJOR)はgpt-6-lunaが5/5完全一致・baselineは2/5(40%)。**勝敗が逆転**する | `er050_output/gpt6_checker_comparison_trial_01/summary_step3.json`、REPORT§Phase B-8 |
| severity/flag/originのrun間揺れ | Meta_run03_standard: gpt-6-lunaがgold(fact_id=MUSE-HC-010, origin=translation)と異なる(fact_id=MUSE-HC-012, origin=ja_source)claimを検出 | `er050_output/gpt6_checker_comparison_trial_01/step2/Meta_run03_standard/gpt-6-luna/run_1.json` |
| prompt cacheの影響有無 | **未確認**(本Trial・本設計いずれも実測なし、推測しない) | — |

ja_original/ja_r2(gold未固定)は**両モデルとも高い非決定性**を示す
(完全一致率0%、REPORT§Phase B-8)。これはモデル固有ではなくCheckerの
設計特性(reasoning effort="high"のLLM-as-judge+claim単体判定)である。

### 1-D. Checker実装上の非対称

`_apply_deviation_post_hoc_validation()`(`er003_v1_en_direct_vfl_01_generate.py:544-561`)
はMAJOR→MINORの自動降格のみを行い、MINOR→MAJORへの補正を行わない。
本シミュレーション(Table A)で、changed_actorについて**flag=true全12件中
8件がMINORのまま**(rescue対象、下記5章)である一方、changed_number/
changed_negation/changed_comparisonは本データ中では既に全件MAJOR
(rescue対象0件、ただしサンプルが小さいため安全網としての価値は残る)。

### 1-E. origin判定

Meta_run03_standardでgpt-6-lunaがgoldと異なるorigin(ja_source vs
translation)・異なるfact_id(MUSE-HC-012 vs MUSE-HC-010)を報告(上記1-C)。
B4でもbaseline/gpt-6-lunaの検出origin構成が異なる(REPORT§Phase B-7)。
**本シミュレーションの重要な追加発見**: JA段Fact Check(JA Original/JA R2)は
`source_article_text`を渡さないためorigin判定自体を行わず、常に
`origin=None`になる(`er003_v1_en_direct_vfl_01_generate.py`の仕様どおり、
REPORT第1-3章)。Table Cで「causality-only & origin!=ja_source→demote」
という素朴なルールをデータ全体へ機械適用したところ、**JA段の
causality-onlyレコード2件(hormuz_run03_ja_r2)が「origin=None≠ja_source」
という理由だけでdemote対象になってしまう**ことを確認した。これは
「JA段は安全側(origin相当の判定材料が無い)」であることの誤読であり、
origin基準の非STOP化ルールをJA段へそのまま適用してはならないという
**設計上の罠**を実データで確認した(第6章で詳述)。

### 1-F. QCD

| 指標 | 値 | Evidence |
|---|---|---|
| call数/記事 | 4(JA Original/JA R2/Advanced/Standard) | REPORT第1章 |
| Checker単発latency中央値 | 33.16秒(n=12小サンプル)/11.93秒(GPT-6 Trial全84call、baseline) | REPORT第5章、`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`§Phase B-9(測定条件が異なるため直接比較しない) |
| Checker単発コスト中央値 | ¥0.9024 | REPORT第5章 |
| retry・STOP率 | Hormuz run_01/02/03、**3 run連続でja_source起因MAJORによりSTOP**(`OPEN_ITEMS.md` OPEN-233本文2026-09-29追記2参照) | `OPEN_ITEMS.md`、`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` |
| 完成記事率 | Family X E2E(Hormuz)2/2試行が未完成(run_01/run_02とも未完成、run_03はGate 3 PASS済みだがHormuz自体はDEFERRED維持) | REPORT第5章、`OPEN_ITEMS.md` OPEN-233 |

### 1-G. 問題の起因分類

| 問題 | モデル起因 | Prompt起因 | post-hoc起因 | 呼び出し側(Action)起因 | Ledger起因 |
|---|---|---|---|---|---|
| B-1(ブリッジ文) | △(GPT-6でも不変) | ○(許容範囲規定の境界未定義) | - | - | - |
| B-2(Hormuz causality) | △(GPT-6でも検出自体が消失=非決定性) | ○(context window無視) | - | ○(origin=ja_source即STOP) | ○(notes_for_writer事実上hard化) |
| B-3(接続詞so) | △(GPT-6で不変、完全一致) | ○(境界定義なし) | - | - | ○(notes_for_writer HF-007) |
| changed_actor見逃し | ○(baseline系統的0/6、GPT-6は3/6へ部分改善) | - | ○(MINOR→MAJOR補正なし) | - | - |
| 非決定性全般 | ○(LLM-as-judge固有、GPT-6でも解消せず) | - | - | ○(反復判定の不在) | - |
| origin揺れ | ○(モデル・run間で揺れる) | △(origin判定基準がclaim単位のみ) | - | - | - |

---

## 2. 過剰BLOCKの原因(1段掘り)

1. **notes_for_writerの事実上のhard化**: `build_verified_ledger_text()`
   (`vfl01.py:302-303`)がnotes_for_writerを他fieldと区別なくLedgerテキスト
   へ埋め込み、`DEVIATION_PROMPT_TEMPLATE`(`vfl01.py:502-541`)自体には
   notes_for_writerを判定根拠から除外する規定が存在しない。Hormuz HF-001〜012
   全12件を分類した結果**12/12がfactual constraint**であり(0件が純粋な
   writer guidance、`LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_REPORT.md`
   Part B)、Researcherが「危険」と予見して書いた警告がそのままCheckerの
   BLOCKING根拠として機能している(B-2で実証)。
2. **claim単体判定・context window無視**: `DEVIATION_PROMPT_TEMPLATE`は
   `claim_in_article`単位で判定する設計であり、記事全体の文脈上の自己限定
   (留保文)との整合を評価する指示を持たない(REPORT7-3節で事実確認済み)。
3. **許容範囲規定(`vfl01.py:523-529`)の境界未定義**: 「明確な新規Factを
   伴わない一般的な情景描写」という基準はあるが、「一般常識レベルの経済
   知識」(B-1: 原油→ガソリン価格)がこれに該当するかどうかの判定基準が
   Prompt上に明記されておらず、実際には該当しないと判定され続けている
   (4回独立発生)。
4. **GPT-6 Trialで変わらなかったもの**: 上記1〜3はいずれもPrompt/post-hoc
   自体の構造であり、モデル変更だけでは触れられない。実測でも不要BLOCK率は
   75%=75%で不変(REPORT§Phase B-12)。**変わったもの**: B2の検出自体が
   両モデルで消失した(非決定性、モデル差ではない)。

---

## 3. 重大見逃しの原因(1段掘り)

1. **post-hoc validationの非対称設計**: MAJOR→MINORの自動降格のみを行い、
   MINOR→MAJORへの補正ロジックが存在しない(`vfl01.py:544-561`)。モデルが
   「flag=trueだがseverity=MINOR」という、Prompt自身の判定ルール
   (「10種類のいずれかが明確にtrueである場合のみMAJORに」)と矛盾する出力を
   返した場合、この矛盾を機械的に是正する仕組みがない。
2. **changed_actorカテゴリの構造的弱さ**: 全母集団(224件)でもchanged_actor
   はMAJOR0件・MINOR7件(REPORT第4章クロス集計)であり、実運用データでも
   このカテゴリがMAJORへ到達した実績が無い。baselineは合成fixture
   (gold=MAJOR)に対しても6/6(100%)見逃す(系統的、非決定性のノイズでは
   ない、REPORT§Phase B-6)。
3. **GPT-6で変わったもの**: changed_actor検出力が0/6→3/6へ改善(モデル
   自体の推論力向上と考えられる)。**変わらなかったもの**: post-hoc
   非対称設計自体(Prompt/post-hoc無変更のため当然)。B4の検出網羅性は
   むしろ悪化(baseline3件→gpt-6-luna2件、うち1件fact_id重複)。
   「モデルを強くする」ことは特定カテゴリの検出力を上げる場合もあるが、
   別カテゴリでは下げる場合もあり、**一様な安全性向上策ではない**。

---

## 4. 非決定性の原因(1段掘り)

1. **LLM-as-judge固有のばらつき**: reasoning effort="high"のResponses API
   呼び出しであり、temperature/seed制御がAPI上で可能かはPhase A probeでも
   未確認(`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`§4「未解決・未確認
   事項」に明記、推測しない)。
2. **claim切り出し自体の揺れ**: モデルがどの文をdeviationとして報告
   対象に選ぶか自体が非決定的(Meta_run03_standardのfact_id不一致、B4の
   検出件数の揺れ)。
3. **Advanced/Standard独立同一Ledger判定**: 両者は同一Ledgerを判定する
   構造上似た設計だが、Standard生成はAdvanced本文からの再生成であり
   (`er012_e...py:460`)中身自体が異なるため、「判定が食い違う」ことが
   即座に「Checkerの欠陥」とは断定できない側面もある(Part A D-3の指摘)。
4. **GPT-6で変わったもの**: gold既知の2fixture(advanced/standard)平均で
   gpt-6-lunaのgold一致率がbaselineより高い(90% vs 70%)。**変わらなかった
   もの**: fixtureごとに勝敗が逆転する(standardはgpt-6-luna完勝、advanced
   はbaseline完勝)ため一様な優位ではない。ja_original/ja_r2(gold未固定)
   は両モデルとも高い非決定性を維持し、**Checker全体の設計特性(反復判定の
   不在)がモデルに依らず存在する**ことが確認された(REPORT§Phase B-11)。

---

## 5. deterministic rule候補(安全側=昇格)

本シミュレーション(Table A、`simulate_rules_c233.py`)で、GPT-6 Trial
fixture記録(67件のdeviationレコード)へ以下の昇格ルールを機械適用した。

| rule | 現行audit jsonのみで判定可能か | Ledger構造化値との突合要否 | 誤昇格リスク | 本シミュレーション適用結果 |
|---|---|---|---|---|
| `changed_actor=true` → BLOCKING(severity非依存) | **可能**(flag自体が構造化フィールド) | 不要(flagのみで判定、Ledger値との値レベル突合はしない) | Prompt許容規定「出典名を一般的な言い方に置き換えること自体は許容」(`vfl01.py:525`)との境界で、主体の言い換えをモデルが誤ってchanged_actor=trueと判定した場合に過剰昇格するリスクは**本データでは0件観測**(ただし負例fixture不足のため未検証、Trial候補) | **flag=true全12件中8件がMINORのまま**(rescue対象)、ER-009_changed_actor(gold=MAJOR)を含む。B群には出現なし(誤昇格0件、B群サンプルが小さい点に留意) |
| `changed_number=true` → BLOCKING | 可能 | 不要 | 単位換算のみの言い換え(`vfl01.py:516`括弧書きで除外規定あり)をモデルが誤検知した場合のフィルタは現状jsonのみでは不可 | 本データでは4/4件が既にMAJOR(rescue対象0件だが安全網として有効) |
| `changed_negation=true` → BLOCKING | 可能 | 不要 | 二重否定構文(B-2型"did not lead to")をモデル自身がchanged_negation=trueと判定した場合、記事側の意図的な否定表現かLedger側との不一致かを区別できない懸念(未観測) | 4/4件が既にMAJOR(rescue対象0件) |
| `changed_comparison=true`(比較方向反転含む) → BLOCKING | 可能 | 不要 | 低い(単体判定・数値方向の話) | 4/4件が既にMAJOR(rescue対象0件) |
| material time inversion → BLOCKING | `changed_time=true`で代替可能 | 「重大」の判定(相対時間表現の粒度)にはLedgerの`date_or_period`との突合が要る場合がある(schema拡張の余地) | 未検証 | 本データにchanged_time flagを持つMAJOR/MINORレコードなし(サンプル外) |
| comparison方向反転 → BLOCKING | `changed_comparison`で代替可能(専用rule不要) | 同上 | 同上 | 同上 |
| `changed_causality=true` **単独では** 自動BLOCKINGにしない | — | — | — | Table B/Cで確認(下記6章参照)。causality-onlyのMAJORレコード4件中2件(B3、origin=ja_source)は既存どおりBLOCKING維持が妥当という結果が出ており、「causalityは単独では機械的に安全側判定できない」ことをデータが裏付ける |

**結論**: changed_actor/changed_number/changed_negation/changed_comparisonの
4カテゴリは、既存audit jsonの構造化フィールドのみで実装可能な昇格ルール
(flag=true→BLOCKING)を安全に追加できる可能性が高い(本データでは
誤昇格0件)。ただし**負例(主体の一般的言い換え等)fixtureが現状ゼロ**
であり、Trialでの追加検証が前提(第11章)。

---

## 6. deterministic rule候補(生産性側=非STOP化)

### 6-1. causality系

本シミュレーション(Table B/C)で、`changed_causality=true`かつ他の
9フラグが全てfalse(=causality-only)のMAJORレコードをGPT-6 Trialデータ
から抽出した結果、**全67件中4件のみ**該当した:

| fixture | model | origin | 出典 |
|---|---|---|---|
| B3 | gpt-5.6-luna | ja_source | `er050_output/gpt6_checker_comparison_trial_01/step2/B3/gpt-5.6-luna/run_1.json` |
| B3 | gpt-6-luna | ja_source | `.../step2/B3/gpt-6-luna/run_1.json` |
| hormuz_run03_ja_r2 | gpt-6-luna(run_3) | None(JA段、source_article_text未指定) | `.../step3/hormuz_run03_ja_r2/gpt-6-luna/run_3.json` |
| hormuz_run03_ja_r2 | gpt-6-luna(run_5) | None(同上) | `.../step3/hormuz_run03_ja_r2/gpt-6-luna/run_5.json` |

候補ルール「causality-only & origin!=ja_source → 非STOP(QUALITY)」を
このデータへ機械適用した結果:

- B3(2件、origin=ja_source): **STAY BLOCKING**(rule条件を満たさない)。
  これはPart Bの独立評価(「B3は原文が並列かの確認が要る境界事例」)と
  整合し、**この単純ルールではB3は緩和されない**(意図どおり、B3は
  HF-007のnotes_for_writer[時系列固定]に抵触するため安全側に倒れる)。
- hormuz_run03_ja_r2(2件、origin=None): **DEMOTE**(条件を満たしてしまう)。
  ただし1-E節で述べたとおり、この`origin=None`はJA段が構造的に
  `source_article_text`を渡さないために発生する値であり、「安全という
  判定結果」ではない。**この単純ルールをそのままJA段へ適用すると誤った
  非STOP化を引き起こす**(設計上の罠、実データで確認)。

**結論**: 「causality-only + origin!=ja_source」という単純ルールは、
**EN段(Advanced/Standard)に限定して適用すべき**であり、JA段
(origin概念が存在しない)には適用してはならない。かつ、EN段に限定しても
本データではB2/B3のような実際の過剰BLOCK候補を**1件も救済できない**
(B3はja_source、B2はそもそも今回検出されず対象外)。**causality単独の
非STOP化は、現行audit jsonの構造化フィールドだけでは実質的な生産性改善に
つながらない**というのが本シミュレーションの結論であり、Part A/Bの
「LLM判断に残す部分」という評価と一致する。真の効果を得るには、
`notes_for_writer`の`factual_constraint`との一致判定(第8章)や
qualifier/hedge検出のような**新しい構造化フィールド**(モデルへ追加出力
させる、schema拡張)が前提になる。

### 6-2. B-1型(unsupported_new_claim-only、一般化ブリッジ文)

Table D(B-group flag構成)より、B1の全MAJORレコード(3件、baseline1+
gpt-6-luna2)は`unsupported_new_claim`単独flagである(causalityではない)。
現行audit jsonには「一般常識レベルの経済知識」か「Ledgerに無い新規の
具体的主張」かを区別する構造化フィールドが存在しない(Part A C-5で確認済み、
`explanation`は自由文のみ)。したがって**B-1型の非STOP化ルールは、現行
schemaのままでは決定論的に実装できない**。新schema候補(モデルへ追加
出力させる、例: `plausible_common_knowledge: bool`または
`general_scene_description: bool`)を第11章のTrial候補として位置づける。

### 6-3. 免罪符化を防ぐ条件設計

Part Bの指摘どおり、「hedge(留保文)の有無」を非STOP化の主条件にすると、
Hormuz記事の留保文が定型パターンであるため**機械的に免罪符化**される
リスクが高い(B-2/B-3双方でJA/EN両方に類似の定型留保文が存在、REPORT
7-3節)。本設計では以下を推奨する:

- **主条件**: claim(記事側の主張)が、Ledgerの構造化フィールド
  (`numeric_value`/`subject`/`date_or_period`/`causal_strength`)と
  矛盾しないこと。矛盾しない場合のみ非STOP化候補とする。
- **補助条件**: hedge/qualifier(限定語・留保文)の存在は、あくまで補助的な
  加点要素とし、単独では非STOP化の根拠にしない。
- **必須の除外条件**: `notes_for_writer`の`factual_constraint`
  (第8章)が明示的に禁止する推論パターンと一致する場合は、hedgeの有無に
  関わらず非STOP化しない(B-2はこの除外条件に該当するため、hedgeが
  あってもBLOCKING維持が妥当という第7-1章のPart B独立評価と一致する)。

この「claimがLedgerの観測と矛盾しないことを主条件にする」設計は、
現行audit jsonの自由文`explanation`だけでは判定できず、
`ledger_field_basis`のような新フィールド(Prompt/schema変更、Trial候補)
が前提になる(Part A C-5「不可」判定と整合)。

---

## 7. Severity 3層とActionの分離設計(v0.1を継承・修正)

### 7-1. 3層定義

- **BLOCKING**: STOP/must-fix対象。既存の「MAJOR」に相当する重大逸脱の
  うち、第5章の昇格ルールに該当するもの、または現行Promptが明確に
  MAJORと判定したもの。
- **QUALITY**: 通過するが、ログへ記録する(逸脱として検出はしたが、
  記事の理解を実質的に誤らせない、または第6章の非STOP化条件を満たす)。
- **ACCEPTABLE**: 通過し、通常の許容範囲内として扱う(現行Prompt
  `vfl01.py:523-529`の許容範囲規定に該当するもの)。

### 7-2. 後方互換方式

既存`severity`(MAJOR/MINOR)フィールドは**そのまま維持**し、新フィールド
`severity_final`(BLOCKING/QUALITY/ACCEPTABLE)・`action`
(STOP/LOG_AND_PASS/PASS)・`basis`(hard field由来かnotes由来か)・
`rule_id`(どのdeterministic ruleが適用されたか)を追加する方式を推奨する
(Part A C-3、Part分析どおり)。既存481ファイル・224件個票のMAJOR/MINOR
統計・過去REPORT集計との互換性を壊さない。

### 7-3. Action表(origin × severity_final × 段)

| 段 | origin | severity_final=BLOCKING | =QUALITY | =ACCEPTABLE |
|---|---|---|---|---|
| JA(Original/R2) | (origin概念なし) | must-fix retry 1回→なおBLOCKINGなら`JAFactCheckStopError` | 通過+ログ | 通過 |
| Advanced/Standard、origin=ja_source | ja_source | 現行どおり即STOP(`JARecheckRequiredError`)または案B(JA差し戻し1回、既存Production配線) | **★ユーザー判断**(即STOPを維持するか、QUALITYとして通過させログに残すか。第14章★1) | 通過 |
| Advanced/Standard、origin=translation | translation | must-fix retry 1回→なおBLOCKINGならSTOP | 通過+ログ | 通過 |

### 7-4. fail-closed原則との整合

**BLOCKING**は従来どおりfail-closed(検出したら必ずSTOP/must-fix、
安全側に倒す)を維持する。**QUALITY**はログ記録の上で通過させる設計であり、
これは**fail-closedの適用範囲をBLOCKINGに限定する設計変更**である
ことを明示する。この適用範囲変更自体が、`CURRENT_SPEC.md`の既存fail-closed
記述(origin=ja_source即STOP、「安全≠成功」原則どおり)の実質的な修正に
当たるため、★ユーザー判断が必要(第14章★2)。

### 7-5. QUALITYログの置き場・運用

`er019_output`/`er012_output`等の既存`audit/deviation_checks/`配下に
`quality_log.jsonl`のような専用ログを追加し、記事ごとの累積を可視化する
設計を提案する(採用しない、案のみ)。閲覧責任者・週次確認・OPEN化基準
(Part Bの改善提案6)をセットで定義する必要がある。

### 7-6. Key Phrase/Comment/In One Lineへの伝播対策

Key Phraseは各レベル自身の最終確定本文から独立選定(`CURRENT_SPEC.md:1677`)、
In One LineはFull Story/Points既出情報のみを使う(`CURRENT_SPEC.md:582`)。
QUALITY判定で通過した逸脱文が本文に残れば、これらの入力になり得る。
現行設計にはKey Phrase/In One Line生成後の再チェック工程がない(調査範囲
では未確認)。本設計では、QUALITY通過分についても本文確定後にKey Phrase/
In One Line生成前段で**再度Deviation Checkの対象に含める**(追加callが
必要、QCDへの影響は第9章参照)か、QUALITYを許容する範囲を「Key Phrase/
In One Lineへ抽出されにくい文脈情報に限定する」等の追加設計が必要
(★ユーザー判断、第14章★3)。

### 7-7. 案B・must-fix・Human Review Lockとの関係

既存の「案B」(ja_source MAJOR時のJA差し戻し1回retry、
`CURRENT_SPEC.md`4節、`APPROVED_FOR_PRODUCTION`・Gate3待ち)は、
本設計のBLOCKING×origin=ja_source列の現行運用と一致する。3層化導入時も
案Bの仕組み(`build_must_fix_block()`の再利用)自体は変更せず、
「BLOCKINGと判定された場合にのみ」案Bを発動する形に位置づける。
Human Review Lock(既存は`er011_human_review_lock_01.py`、音声TTS/ASR
attempt専用、`out_path`/`text`/`language`/`wav_path`を前提とするAPI)は
記事本文のFact逸脱という異なる種類の承認対象を扱っておらず、統合するには
新規APIまたは新規queueが必要(Part A確認済み、★ユーザー判断、第14章★4)。

---

## 8. notes_for_writerの扱い

**soft化しない**(ユーザー指定どおり)。Hormuz Ledger HF-001〜012全12件の
分類結果は**12/12がfactual constraint**、0件が純粋なwriter guidance
(`LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_REPORT.md`Part B)。

### 8-1. factual_constraint / writer_guidance分離schema案

`FACT_LEDGER_JSON_SCHEMA`(`vfl01.py:78-126`)のResearcher出力段階で、
現行の単一`notes_for_writer`フィールドを以下2つに分離する案:

- `factual_constraint`(string, nullable): 禁止する推論パターン・時系列
  固定・numeric_scope固定・certainty文言指定等、10カテゴリ判定の境界を
  具体的に補強する記述。**Deviation Checkの判定根拠として引き続き使用
  する(hardのまま)**。
- `writer_guidance`(string, nullable): トーン・文体・エンタメ性等、
  純粋な執筆助言。**Deviation Checkの判定入力から除外する**候補
  (Ledgerテキスト化時に含めない、またはPrompt側で明示的に「参照しない」
  指示を追加)。

### 8-2. Checkerへの渡し方

Prompt変更(`DEVIATION_PROMPT_TEMPLATE`本文)が不可避(Part A C-4)。
`build_verified_ledger_text()`(`vfl01.py:302-303`)の改修に加え、
Prompt側に「factual_constraintは判定根拠として使用し、writer_guidanceは
判定に使用しない」という除外規定を明記する必要がある(post-hocでの
事後除外では「一度hard判定させてから打ち消す」形になり、素案の意図と
異なる、Part A C-4)。

### 8-3. 過去Ledger資産の互換

過去のLedgerはテキスト化済み(`verified_fact_ledger.txt`)で保存されて
おり、schema自体を再パースする用途では使われていない可能性が高いため、
実害は小さい可能性がある(**未確認**、Part A C-3)。`FACT_LEDGER_JSON_SCHEMA`
の`required`配列(`vfl01.py:113-117`)にnotes_for_writerが含まれるため、
分離先を新フィールドにする場合はResearcher出力schema自体の変更となる。

### 8-4. Trial候補としての位置づけ

本分離はschema変更を伴うため、**Production変更ではなくTrial候補**
として位置づける(第11章)。Hormuz Ledgerの12件のfactual constraint分類
結果を「gold」として、新Researcher Promptで実際に2フィールドへ正しく
分離できるかを検証する。

---

## 9. 非決定性対策

### 9-1. 反復判定

GPT-6 Trial Step3(n=5、`er050_output/gpt6_checker_comparison_trial_01/
summary_step3.json`)の実測により、**Checker全体が非決定的である**ことが
確認された(ja_original/ja_r2の完全一致率0%、gold既知fixtureでも
baseline/gpt-6-lunaいずれかが40〜80%に留まる)。反復判定(n回多数決)は
非決定性を吸収する現実的な手段候補である。「BLOCKING判定は2回中2回」等の
閾値案は、B3(新旧で完全一致、安定)のような高信頼度fixtureでは1回でも
十分な可能性がある一方、standard/advancedのような判定割れfixtureでは
n=2では不十分な可能性がある(fixtureごとに必要反復数が異なりうる、
Trialで検証が必要)。

### 9-2. temperature/seed

Responses API上でtemperature/seed制御が可能かは、Phase A probeでも
**未確認**(`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`§4)。推測しない。
本設計では「確認できれば非決定性対策の第一候補」とのみ位置づける
(★ユーザー判断、第14章★5)。

### 9-3. prompt cacheの影響

未確認。GPT-6 Trialでもcached_input_tokensは実測記録されている
(`usage.cached_input_tokens`)が、判定一致率との相関分析は本設計では
行っていない(Trial候補)。

### 9-4. Advanced/Standard統合案の費用対効果

Part A D-1の機械集計(Family X系26ファイル・15 run、related_fact_id突合)
では、JA/EN間の重複検出は**0件**であり、「JA canonical確定後、EN側は
translation-diff限定」という素案Gの前提を裏付けるデータは得られなかった。
Standardの再翻訳元はAdvanced本文であり(`er012_e...py:460`)、JA原文を
直接参照しないため、Standard側で新たに生じるtranslation起因の逸脱を
Advanced段のDiffだけで検出できるかは未検証(Trial対象)。**現時点では
call削減による費用対効果は「未確立」**として扱う(Part A/Bと同じ結論)。

---

## 10. 実装配置案(Production変更はしない、案のみ)

### 10-1. 単一分類関数

`vfl01.py`内に`classify_severity(deviation: dict, stage: str, origin: str|None) -> dict`
のような単一関数を新設し、`_apply_deviation_post_hoc_validation()`の
骨格(raw_parsed→加工→overall_status再計算という構造)を拡張する形で
実装する案。戻り値に`severity_final`/`action`/`basis`/`rule_id`を含める。
呼び出し側(`er012_e...py`/`er019...py`/将来の他Family runner)はこの
関数の戻り値のみを見てAction分岐する(現状`_major_deviations()`が両
ファイルにほぼ同一コードで重複している軽度drift、Part A C-7の解消策)。

### 10-2. drift回避

選択肢1(単一関数への集約)を推奨する。選択肢2(呼び出し側ごとに独自
Action表)はdrift再発リスクが高い(Part A C-7)。

### 10-3. Family A/B/C/X/Zへの波及範囲

`run_deviation_check()`はFamily A(`er003_v1_n3_01_articles_generate.py`、
hook_aware=True固定)・Family B(`er012_b_family_production_runner_01.py`
等)・Family C(`er013_family_c_future_safety_06.py`)・Family X
(`er012_e_family_entertainment_two_level_runner_01.py`+
`er019_family_x_ja_writer_o_r1_r2_01.py`)が共有する。Family Z
(`er026_family_z_fiction_production_runner_01.py`)は`vfl01`をimportするが
`run_deviation_check()`は未呼び出し(将来利用)。**severity 3層化は
これら全ての呼び出し元のoverall_status判定・Gate分岐・REPORT集計
(224件個票の既存統計)へ同時に影響する**(Part A C-8)。Family A
(hook_aware)は`HOOK_AWARE_DEVIATION_PROMPT_TEMPLATE`も二重に書き換える
必要がある。

### 10-4. Dangling Referenceの可能性

Prompt変更は`vfl01.run_deviation_check()`という共有関数のため、
Family A/B/C/Xの全呼び出し元へ**同時に**波及する(同一関数という事実、
REPORT第1-0章)。Family X限定の文言変更をしたい場合は`hook_aware`と
同様の新しい`prompt_variant`引数の追加が必要(現状汎用フラグなし、
Part A C-4)。この設計変更自体がFamily横断影響を持つため★ユーザー判断
(第14章★6)。

### 10-5. schema追加の後方互換

既存481ファイル・224件個票のseverity値(MAJOR/MINOR固定)、`strict:True`
(additionalProperties:False)のJSON Schemaとの非互換リスク(Part A C-3)。
新フィールド追加方式(既存`severity`維持+`severity_final`等追加)を推奨。

---

## 11. Trial案(既存fixture使用、追加fixtureは最小)

### 11-1. 受入条件

- **Safety**: 重大fixture群(ER-009-N1 9種+A群5件+changed_actor n=5)の
  BLOCKING維持率**100%**(1件でも落ちたら不採用)。GPT-6 Trialの実測
  (ER-009-N1 8/9維持、changed_actor n=5でgpt-6-luna 3/5)を踏まえ、
  changed_actorは**第5章の昇格ルール込みで**100%を目指す設計とする
  (昇格ルールがrescueする8件、本シミュレーションTable A参照)。
- **Productivity**: 不要BLOCK率をB群baseline **75%から明確に下げる**
  (目標値案: ≤25%、根拠は本シミュレーション第6章の結果を踏まえ再検討
  必要=causality単独ルールでは0%しか下がらないため、notes_for_writer
  分離+qualifier検出等の複合ルールが前提になる可能性が高い。★ユーザー
  判断、目標値自体の妥当性、第14章★7)。
- **Stability**: 同一input一致率。現行40〜100%(fixtureにより大きく
  異なる、GPT-6 Trial Step3実測)→目標値案は「gold既知fixtureの
  gold一致率平均≥80%」等(★ユーザー判断)。
- **QCD**: cost・latency・retry・STOP率・completion率。

### 11-2. 比較構成

| 構成 | 内容 |
|---|---|
| 構成1 | 現行Prompt+post-hoc v2のみ(baseline、両モデル) |
| 構成2 | Prompt変更あり(context window指示追加、notes_for_writer分離除外規定) |
| 構成3 | 構成2+反復判定(n=3〜5多数決) |

モデルは`gpt-5.6-luna`と`gpt-6-luna`の両方で実施(GPT-6単価は
`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`時点で**未確認**、
参照先: 同REPORT§Phase B-4/B-9の参考換算値[gpt-5.6-luna単価流用]。
確定単価が別途得られていればそちらを優先する)。

### 11-3. 反復数・費用概算

GPT-6 Trialの実測(Checker単発コール、baseline中央値¥0.90/n=42、
gpt-6-luna中央値相当¥0.48換算[84 call合計¥41.27÷84]、
`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`§Phase B-9)を根拠にすると、
fixture 30件×n=5×2モデル×3構成=900 call、概算¥0.5〜1.6/call
(REPORT第5章)想定で**¥450〜1,440程度**(確定額ではない、単価未確認
リスクを含む)。Guardrail段階発火案・STOP条件(予算超過見込み・API error
継続・schema非互換・harness不具合・fixture破損・Production影響)は
GPT-6 Trialのharness設計(`er050_gpt6_checker_comparison_trial_01.py`)を
踏襲する。

### 11-4. gold確定が必要なfixture(USER_DECISION_REQUIRED)

- `er009_changed_actor`: baseline系統的0/6見逃し vs gpt-6-luna 3/6 PASS。
  昇格ルール(第5章)適用後のgold再定義が必要。
- Meta run_03 Standard: gpt-6-lunaがgoldと異なるclaim(fact_id/origin)を
  検出。「別のclaimを検出した」のか「たまたま別の理由でMAJORになった」
  のか未確定。
- B-2(Hormuz causality): BLOCKING/QUALITY/ACCEPTABLEのいずれにするかの
  Product判断(第14章★1と同一論点)。
- B-4: gold4件中、新旧とも一部しか検出できず(baseline3件、gpt-6-luna
  2件)、検出網羅性自体のgold再確認が必要。

---

## 12. 既存仕様との競合

| 既存決定 | 競合点 |
|---|---|
| fail-closed設計(origin=ja_source即STOP、`CURRENT_SPEC.md`4節「安全≠成功」原則どおり) | 第7章のQUALITY層導入は、fail-closedの適用範囲をBLOCKINGに限定する実質的な緩和。★ユーザー判断(第14章★2) |
| 案B(ja_source MAJOR時のJA差し戻し1回retry、`CURRENT_SPEC.md`5節、`APPROVED_FOR_PRODUCTION`・Gate3待ち) | 3層化後もBLOCKING×ja_source列では現行どおり維持する設計だが、QUALITY判定の導入により「案Bが発動する条件」自体が変わる可能性がある |
| JA Fact Check配線決定(`NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01`、2026-09-27、`PRODUCTION_WIRED`) | Action判定部分(現状「MAJOR=1件でも即retry/STOP」)の事実上の再設計になる |
| ER-009-N1 recalibration(危険9種fixture全MAJOR維持) | 3層化後の再検証必須(GPT-6 Trialでは8/9維持を確認済み、changed_actorのみ要再設計) |
| OPEN-189(JA Fact Check固定費・latency最適化) | 素案Gの4call見直しと重複、統合または重複整理が必要 |
| Human Review Lock(音声専用) | 記事Fact逸脱への統合可否未確認(第7-7章) |
| OPEN-233自体(2026-09-29 W6でdeferred/non-blocking化) | 本設計はOPEN-233の再開時評価に使う材料として位置づけ、再開判断自体は別途(GPT-6 Trial/Production Routing判断後という既存の再開順序と整合させる必要がある、★第14章★8) |

---

## 13. リスク・未解決

- QUALITYログの置き場・閲覧責任者・レビュー頻度が未定義(貯めるだけに
  なるリスク)。
- QUALITYがKey Phrase・Comment・In One Lineへ伝播する経路への対策が
  未確定(第7-6章)。
- Severity変更が過去のREJECTED/VALIDATED判定・既存REPORT統計の遡及的
  再解釈に与える影響(過去のUSER_DECISION_REQUIRED、B-2含む)。
- 免罪符化(定型ヘッジで通る)リスクへの対応は第6-3章で設計方針を示した
  が、実装には新schema(qualifier/hedge検出フィールド)が前提。
- notes_for_writer分離schemaの過去Ledger資産への実害は未確認(第8-3章)。
- Family Z(Fiction)への適用可否は未検証(Ledger概念が異なる可能性)。
- GPT-6単価が未確認のため、本書のTrial費用概算は全て仮値である
  (§11-3)。
- 本シミュレーション(第5〜6章)はGPT-6 Trial fixture(67件)という
  比較的小さいサンプルに基づく。Family X実運用データ(origin付き15件)
  との突合は限定的(B1/B2/B3/B4のみ重複、A群はA2A3/A4/A5のみ)であり、
  一般化には追加fixtureが必要(第11章)。
- `changed_time`/`changed_number`(材料時系列反転・値反転)については
  本シミュレーションデータ中に該当レコードが無く、昇格ルールの実データ
  検証ができていない(ER-009-N1合成fixtureのみ、実運用データなし)。

---

## 14. ★ユーザー判断が必要な事項

1. **Hormuz B-2型(観測と整合する「効果の不在」記述だが、notes_for_writer
   が明示禁止した因果推論と同型)を、Action表(第7-3章)でBLOCKING列に
   残すかQUALITY列へ動かすか**。本シミュレーションでは、B-2は今回の
   GPT-6 Trial n=1実行で検出自体が消失しており(新旧ともLEDGER_COMPLIANT)、
   非決定性の影響を強く受ける境界事例であることが確認された。Part Bの
   独立評価(BLOCKING dependent、QUALITY/ACCEPTABLE降格に反対)を維持
   するか、素案のQUALITY/ACCEPTABLE寄りの評価を採るかの最終判断。
2. **fail-closedの適用範囲をBLOCKINGへ限定する設計変更(QUALITY層導入)
   自体を承認するか**(`CURRENT_SPEC.md`の「安全≠成功」原則・fail-closed
   記述の実質修正を伴う)。
3. **QUALITY通過分のKey Phrase/Comment/In One Lineへの伝播対策**
   (追加再チェック工程を設けるか、QUALITYの許容範囲を限定するか)。
4. **Human Review非常口を既存の音声用Human Review Lock機構
   (`er011_human_review_lock_01.py`)に統合するか、新規queueを作るか**
   (既存APIは`out_path`/`text`/`language`/`wav_path`前提で音声attempt
   専用、記事Fact逸脱という異なる承認対象への流用可否は未確認)。
5. **Responses APIでのtemperature/seed制御可否の確認要否**(非決定性
   対策の前提調査、確認しなければ反復判定[n回多数決]のみが選択肢になる)。
6. **Family A/B/C/X横断でのPrompt変更の同時波及を許容するか、
   `prompt_variant`引数追加でFamily X限定に絞るか**(第10-4章、
   Dangling Referenceの可能性を含む)。
7. **不要BLOCK率の目標値(第11-1章、案≤25%)の妥当性**。本シミュレーション
   では、causality単独の非STOP化ルールだけでは実データ上の削減効果が
   ほぼ0であることが判明しており、目標達成にはnotes_for_writer分離+
   新schema(qualifier/ledger_field_basis検出)が前提になる可能性が高い。
   この複合設計をTrialへ含めることの承認。
8. **OPEN-233全体の再開タイミング**(現行SSOTの既定順序=Family X E2E完了
   →GPT-6 Trial/Routing判断→必要なProduction導入→本再評価、という順序を
   維持するか、本設計書の完成をもって前倒しで再開判断へ進めるか)。
9. **notes_for_writerのfactual_constraint/writer_guidance分離schema
   変更をTrialで先行検証するか**(第8章、Production変更ではなくTrial
   候補としての位置づけ自体の承認)。
10. **GPT-6モデル(`gpt-6-luna`)をChecker用途で採用候補に含めるか**
    (単価未確認、changed_actorでは改善・B4では悪化という非一様な結果を
    踏まえた上での判断。本設計はモデル選定自体を提案しない)。

---

## 出典一覧

- `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`(全文)
- `LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_REPORT.md`
- `docs/pm/review_ledger_deviation_redesign_01_part_a.md`
- `docs/pm/review_ledger_deviation_redesign_01_part_b.md`
- `GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md`(Phase B全体、§Phase B-1〜B-12)
- `er050_output/gpt6_checker_comparison_trial_01/`(step1/step1_er009_changed_actor_n5/step2/step3/summary_*.json、67件のdeviationレコード)
- `er003_v1_en_direct_vfl_01_generate.py:78-126,275-305,434-561,544-561,634-839`
- `er012_e_family_entertainment_two_level_runner_01.py:262-546`
- `er019_family_x_ja_writer_o_r1_r2_01.py`
- `OPEN_ITEMS.md`(OPEN-233)
- `CURRENT_SPEC.md`(4〜5節、Fact Check方針・ja_source MAJOR時の暫定retry拡張[案B]・fail-closed/「安全≠成功」原則)
- `er011_human_review_lock_01.py`(音声attempt専用APIであることの確認、`out_path`/`text`/`language`/`wav_path`前提)
- 机上シミュレーション: scratchpad自作`simulate_rules_c233.py`(repo外、API呼び出しなし、¥0)
