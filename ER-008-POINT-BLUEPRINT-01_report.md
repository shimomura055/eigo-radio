# A2/B1 Point Structure Semantic Alignment 完了報告

管理ID: ER-008-POINT-BLUEPRINT-01(ER-008-A2-STORY-B1-SUPPORT-COMPATIBILITY-AUDIT-01/OPEN-63の後継Decision実装)

## 総括(実装状況の要約、推測での「解決済み」宣言はしない)

| 項目 | 状態 |
|---|---|
| Shared Point Blueprint Schema | **実装済み**(コード完全動作、fixtureで検証済み) |
| Blueprint生成(LLM呼び出し) | **コード実装済み・未実行**(有料API呼び出しのため承認待ち、下記6節) |
| Writer Pipelineへの配線(A2/B1) | **実装済み**(オプション引数、Blueprint未指定時は既存Topicへ完全に無影響であることをコードで確認済み) |
| Support(Comment)Pipelineへの配線 | **実装済み**(B1のComment 3/4のみ対象、同上の後方互換確認済み) |
| 決定論的Structural Validator | **実装済み・fixture(18件)で全PASS** |
| No.4〜6への適用Simulation | **Dry Run(机上Simulation)のみ**。手作業で構築した後付けBlueprint+実記事の手動読解による自己申告相当データを用いた。実LLM生成のBlueprint・実Writer再生成による検証は未実施 |
| 実記事での検証 | **未実施**(新規Writer API呼び出しが必要なため、実行前承認待ち) |
| 音声での検証 | **未実施**(本タスクは新規TTS/ASRを行わない非対象事項) |
| Productionへの配線 | **未配線**(コードはオプトイン設計のため、既存No.1〜6を含む全既存Topicの生成には一切影響しない。No.7以降での使用はユーザー判断待ち) |
| 既存No.4〜6記事の再生成 | **行っていない**(非対象事項として明示的に除外) |

## 1. 現行Pipeline Audit結果

### 1-1. Writer Pipeline(実際にNo.4〜6を生成した経路)

`er006_pool_n4n6_production_01_run.py` → `er006_pool_pilot_01_writer.run_writer_for_theme()` →
`er003_v1_n3_01_articles_generate.run_one_pattern()`という経路を確認した。

- `build_common_block()`が構築する`COMMON_BLOCK_TEMPLATE`は、Verified Fact
  Ledger全文(`verified_ledger_text`)と、Point One/Two運用ルール("### 見出しを
  ちょうど2つ"等)を**A2・B1で完全に同一のテキストとして**渡している
- その後、`B1_B_DIRECT_INSTRUCTION`/`A2_KAI1_INSTRUCTION`という難易度別
  instructionを追加し、**それぞれ独立したLLM呼び出し**(`run_one_pattern`)を実行する
- **重要な発見**: 両者を接続する仕組みが一切無い。A2 WriterとB1 Writerは、
  同じLedgerを見ながら、どのFactをPoint One/Twoのどちらに置くかを完全に
  独立して(お互いの出力を知らずに)決定している。これが、ER-008で発見
  したNo.5・No.6の不整合の直接的な設計上の原因である

### 1-2. Verified Fact Ledger構造

`er003_v1_en_direct_vfl_01_generate.build_verified_ledger_text()`が、各Factを
`fact_id`(例: `FACT-007`。No.6のみ`F-008`のような短縮形式で、fact_id命名が
Topicによって完全には統一されていないことも判明した、17節参照)付きの
テキストブロックとして整形し、Writerへ渡していることを確認した。この
fact_idが、Blueprintのfact所属を表現する既存の一意識別子としてそのまま
再利用できることを確認した(新しいID体系を導入する必要が無かった)。

### 1-3. Support(Comment)Pipeline

`er006_pool_pilot_01_support.run_support_for_theme()` → `er003_v1_n3_01_
scaffold_generate.run_b1_scaffold()`/`run_a2_scaffold()`を確認した。

- **重要な発見**: Comment 3・4の生成context(`c3_context`/`c4_context`)は、
  **そのレベル自身が既に書き終えた記事本文の`parts['point_one_body']`/
  `parts['point_two_body']`をそのまま渡している**。つまりComment生成は
  「そのレベルの記事が実際に何を書いたか」だけを見ており、他レベルとの
  整合性を一切考慮しない設計だった。これがNo.5のComment 4問題(B1限定
  Factの参照)の直接的な原因である
- Comment 1・2・Previewは、Full Story Part1/Part2(本文)のみに依存しており、
  ER-008監査でも大半が互換性ありと確認済みのため、今回のBlueprint配線
  対象から外した(2節・非目標「必要以上に複雑なスキーマにはしない」に
  従い、実際に問題が見つかった範囲[Comment 3・4]にのみ変更を絞った)

### 1-4. B1_B_DIRECT_INSTRUCTION / A2_KAI1_INSTRUCTION

いずれも、Point One/Twoが「本文とは別の切り口・示唆・背景」を扱うべき
ことを規定しているが、**A2/B1間でどのFactをどちらのPointに置くべきかを
指定する記述は一切無かった**(2記事は完全に独立生成されるという設計を
そのまま反映している)。

## 2. Shared Point Blueprintの正式Schema

新規モジュール[er008_shared_point_blueprint_01.py](er008_shared_point_blueprint_01.py)に実装した。

```python
@dataclass
class PointBlueprint:
    role: str
    common_claim: str
    common_fact_ids: list          # 両レベル共通、必ずこのPointに置くfact_id
    optional_b1_fact_ids: list     # B1のみ使ってよい追加根拠のfact_id
    required_in_a2_fact_ids: list  # common_fact_idsのsubset、A2でも省略しない
    comment_anchor: str            # このPoint後の共通Commentが参照してよい内容
    prohibited_reference_fact_ids: list  # この時点で未提示、参照するとネタバレになるfact_id

@dataclass
class SharedPointBlueprint:
    topic_id: str
    point_1: PointBlueprint
    point_2: PointBlueprint
    point_transition: str  # 任意: Point1->Point2の関係
```

タスク仕様のYAML例とほぼ1対1で対応させた(`fact_id`はVerified Fact
Ledgerの既存`fact_id`をそのまま再利用、`reveal_stage`相当は
`prohibited_reference_fact_ids`で表現、`support_safe_summary`相当は
`comment_anchor`で表現)。`point_transition`のみ、タスク仕様の「Point 1/2は
並列だけでなく因果関係等でもよい」という要件を満たすために追加した。
これ以上のフィールドは追加していない(過剰なスキーマ化を避ける)。

## 3. Writer/Support Promptの変更内容

### 3-1. Writer(`er003_v1_n3_01_articles_generate.py`)

- `COMMON_BLOCK_TEMPLATE`の末尾に`{shared_point_blueprint_block}`
  placeholderを追加(既定は空文字列)
- `build_common_block()`にオプション引数`shared_point_blueprint_block: str
  = ""`を追加。**空文字列の場合、生成されるテキストは変更前と完全に
  バイト単位で同一であることを確認済み**(下記6節)
- Blueprintが渡された場合、`er008_shared_point_blueprint_01.render_
  blueprint_for_writer(blueprint, level)`が、A2/B1向けにそれぞれ以下を
  追加する:
  - 両Pointのrole・common_claim・common_fact_ids(必ずこのPointに置く)
  - A2向け: `required_in_a2_fact_ids`(省略しない最低限)の明示、それ以外の
    common_fact_idsは平易さのため省略してよいという許可
  - B1向け: `optional_b1_fact_ids`(B1のみ使ってよい追加根拠)の明示
  - 記事本文の末尾に、実際に使用したfact_idを申告する` ```json `
    fenced blockを追加するよう指示(下記3-3)

### 3-2. Support(`er003_v1_n3_01_scaffold_generate.py`)

- `run_b1_scaffold()`にオプション引数`blueprint=None`を追加
- Blueprintがある場合、Comment 3のcontextへ`comment_anchor`(Point One分、
  `prohibited_reference_fact_ids`も明記)を追加し、Comment 4のcontextへ
  `comment_anchor`(Point Two分)を追加する。role instructionの末尾へも、
  「comment_anchorの範囲だけを参照する」「まだ聞いていないPointやB1限定の
  詳細情報には触れない」という指示、および末尾fact_id申告blockの指示を
  追加する
- Comment 1・2・PreviewはBlueprintの影響を受けない(1-3節の理由)

### 3-3. 出力形式の追加(Writer/Comment共通のパターン)

Writer本文・Comment本文それぞれの末尾に、以下のような1つのfenced code
blockを追加するよう求める設計にした(既存の応答形式を破壊しない、
最小限の追加):

```json
{"point_1_fact_ids_used": ["FACT-003", "FACT-004"], "point_2_fact_ids_used": ["FACT-011"]}
```

Writerの応答自体は引き続き**構造化されていない自由記述**(既存の
`responses.create()`呼び出しをJSON Schema化していない)。これは、
Writer呼び出しの出力契約(`raw_text`)を変更すると、この呼び出しを
共有する既存の他Topic(hanshin/health/household等)・他callerへの
影響範囲が広がりすぎるため、**あえて選ばなかった**設計判断である
(タスク仕様「1... 最小限の変更で導入する」に従う)。

## 4. コード変更(ファイル一覧)

新規:
- [er008_shared_point_blueprint_01.py](er008_shared_point_blueprint_01.py) — Schema・prompt構築・末尾JSON抽出
- [er008_point_blueprint_validator_01.py](er008_point_blueprint_validator_01.py) — 決定論的Structural Validator
- [er008_point_blueprint_validator_test_01.py](er008_point_blueprint_validator_test_01.py) — fixture(18件)
- [er008_point_blueprint_simulation_01.py](er008_point_blueprint_simulation_01.py) — No.4〜6 Dry Run Simulation

変更(いずれもオプション引数の追加のみ、既定値では旧来の挙動と完全に
同一であることをコード上で確認済み):
- [er003_v1_n3_01_articles_generate.py](er003_v1_n3_01_articles_generate.py) — `build_common_block()`/`run_theme()`
- [er003_v1_n3_01_scaffold_generate.py](er003_v1_n3_01_scaffold_generate.py) — `run_b1_scaffold()`
- [er006_pool_pilot_01_writer.py](er006_pool_pilot_01_writer.py) — `run_writer_for_theme()`
- [er006_pool_pilot_01_support.py](er006_pool_pilot_01_support.py) — `run_support_for_theme()`

`er003_v1_n3_01_scaffold_generate.run_a2_scaffold()`、B1_B_DIRECT_
INSTRUCTION/A2_KAI1_INSTRUCTION本体、Verified Fact Ledger生成ロジック
(`er003_v1_en_direct_vfl_01_generate.py`)は無変更。

## 5. 新規Fixture/テスト

[er008_point_blueprint_validator_test_01.py](er008_point_blueprint_validator_test_01.py)、18件全PASS(API呼び出し無し)。
タスク仕様「Regression/品質条件」に明記された6件を含む:

| # | Fixture | 結果 |
|---|---|---|
| 1 | A2がB1 optional factを省略してもPASSする | PASS |
| 2 | 同じFactをA2/B1で別Pointへ配置するとFAILする | PASS(`fact_moved_to_different_point`/`fact_point_mismatch_across_levels`を検出) |
| 3 | Point 1 CommentがPoint 2 Factを参照するとFAILする | PASS(`comment_references_other_point_fact`を検出) |
| 4 | 共通CommentがB1-only Factを参照するとFAILする | PASS(`comment_references_b1_only_fact`を検出) |
| 5 | B1が同じPoint内に追加Evidenceを持つことはPASSする | PASS |
| 6 | Point 1／2の語数が不均等でもPASSする | PASS(Validatorは語数を一切見ない設計) |

上記6件に加え、Blueprint自体のスキーマ検証(必須項目・fact_id重複割当・
required_in_a2の部分集合性)、末尾JSON blockの抽出・除去(正常系/blockが
無い場合/壊れたJSONの場合)、そしてB1がcommon_fact_idsを欠落させた場合の
検出(7節で後述する追加check)の計12件を独自に追加した。

## 6. No.4〜6への適用Simulation結果(Dry Run、実LLM呼び出し無し)

**重要な位置づけの明示**: 以下は、担当者(Claude)が既存のVerified Fact
Ledger(`stage_b3_vfl.json`)と、ER-008監査で読み込み済みの実際の公開
記事本文を手作業で突き合わせて構築した「後付けBlueprint」および
「後付けfact利用申告」による机上Simulationである。実際にBlueprint
生成LLMやWriter LLMがこれらのfact_id割り当てを出力したわけではない。

[er008_point_blueprint_simulation_01.py](er008_point_blueprint_simulation_01.py)の実行結果:

```
No.4: ok=True   (violation無し)
No.5: ok=False  [FAIL] b1_common_fact_missing: B1のpoint_2が共通factを使用していない
                [FAIL] comment_references_b1_only_fact: Comment(point_2後)がFACT-008を参照
                [FAIL] comment_references_b1_only_fact: Comment(point_2後)がFACT-009を参照
No.6: ok=False  [FAIL] fact_moved_to_different_point: B1がF-008をpoint_2で使用(Blueprintではpoint_1)
                [FAIL] fact_point_mismatch_across_levels: F-008がA2ではpoint_1、B1ではpoint_2
                [FAIL] b1_common_fact_missing: B1のpoint_1がF-008(共通fact)を使用していない
                [FAIL] comment_references_other_point_fact: Comment(point_2後)がF-008(Point One分)を参照
```

**No.4が引き続きDIRECTLY_REUSABLEとなるか**: なる(ok=True)。A2/B1とも
Point One(Greeceの205人研究)・Point Two(2022年データ駆動研究)で同じ
fact_idを使っており、Comment 4も両レベル共通のfactのみを参照していた。

**No.5のComment 4不整合が構造的に防げるか**: 検出できることを確認した。
A2実際のPoint Two(「方針の明確さ」、研究の中心的結論=FACT-010)と、
B1実際のPoint Two(「支払い以上の価値」、FACT-008/009)が、後付け
Blueprint上でも実際に異なるfactへ発散していたことが、`b1_common_fact_
missing`(B1が共通factのFACT-010に触れていない)と`comment_references_
b1_only_fact`(共通CommentがB1限定のFACT-008/009を参照)の両方で検出
された。もしこのBlueprintが実際にB1 Writerへ生成前に渡されていれば、
B1はFACT-010(common_claim)を含めるよう誘導され、Comment 4も安全な
comment_anchorの範囲に収まっていたはずである(ただし、これは"はず"の
域を出ない。実際にB1 Writerが指示にどこまで従うかは、実際のLLM呼び出し
[6-1節]で確認する必要がある)。

**No.6のPoint間Fact移動が構造的に防げるか**: 検出できることを確認した。
実験の詳細(F-008、28人の実験)がA2ではPoint One、B1ではPoint Twoに
配置されているという、ER-008で発見した「Point間でのFact入れ替わり」を、
`fact_moved_to_different_point`と`fact_point_mismatch_across_levels`の
両方が正確に検出した。

## 7. 回帰テスト結果

`run_project_regression.py`: **1774/1775 PASS**(1件は既知のharness自己
テスト失敗`er003_test_bad.FixtureTests.test_case_0`、実際の回帰では
ない)。新規18件(Blueprint関連fixture)を含む。既存の1757件は全て
無影響のままPASSしており、Writer/Support pipelineへのオプション引数
追加が既存Topicの挙動を一切変えていないことを確認した。`build_common_
block()`が既定引数で生成する出力が、変更前のテンプレートを直接
`.format()`した場合と**バイト単位で完全一致**することもコードで直接
確認した(3-1節)。

## 8. コスト影響

**実測ではなく、既存の同種呼び出し(Verified Fact Ledger生成)のトークン
数と、確認済みのgpt-5.6-luna実価格(`er005_output/cost_baseline_01/
pricing_snapshot.json`: input $0.2/1M tokens、output $1.2/1M tokens)から
概算した見積りである**。

- **Blueprint生成(新規追加呼び出し、1 topicあたり1回)**: 入力はVerified
  Fact Ledger全文を含むため、既存のVFL生成呼び出し(No.5実測: input
  5,238 tokens / output 4,647 tokens)と同程度の入力規模になると想定する。
  出力はBlueprint(2 Point × 7フィールド、Ledgerの全Fact詳細を再掲する
  VFLよりコンパクト)のため、VFLより少ない約800〜1,200 tokens程度と見積る。
  概算: 入力 ~5,500 tokens × $0.2/1M ≈ $0.0011、出力 ~1,000 tokens ×
  $1.2/1M ≈ $0.0012、**合計 約$0.0023/topic(約¥0.4 @160円/$)**
- **Writer/Comment呼び出し自体の追加コスト**: 既存のprompt/contextへ
  Blueprint制約(数百文字程度)を追加するのみで、呼び出し回数は増えない
  (既存のA2 Writer 1回・B1 Writer 1回・B1 Comment 3/4各1回は変更なし)。
  追加される入力トークンは1呼び出しあたり数百tokens程度、追加コストは
  1 topicあたり$0.001未満と見積る
- **概算合計**: 1 topicあたり**$0.005未満(¥1円未満〜数円程度)**の追加
  コストと見積る。これはOPEN-63の「ほぼ無料で1仕様増やせる」という
  仮説の延長として、妥当な水準と判断する
- 上記はいずれも**見積りであり実測ではない**。実際にBlueprint生成を
  実行すれば、正確な実測値を得られる(6節で述べた通り未実施)

## 9. 既知の限界

1. **自己申告メタデータの正確性はLLMの指示追従性に依存する**。
   Structural Validator自体は決定論的(集合演算のみ)だが、その入力
   (Writer/Commentが申告する`fact_ids_used`)がWriter LLMの自己申告
   である以上、Writerが実際に使ったfact_idを誤って/不完全に申告する
   リスクは残る(意味理解を伴う新しいRuntime Checkerを追加しないという
   タスクの制約上、この限界は受容する設計判断とした)
2. **fact_id命名の不統一**: No.4/No.5は`FACT-001`形式、No.6は`F-001`
   形式と、既存のVerified Fact Ledger生成が一貫していないことが今回の
   Audit中に判明した(6節Simulationスクリプト内でも実際にこの違いを
   反映している)。Blueprint/Validator自体はfact_idを不透明な文字列として
   扱うため機能上の支障は無いが、将来的な一貫性改善の余地として記録する
3. **実LLM未検証**: Blueprint生成・Writer/Comment生成いずれも、
   Blueprintを実際に渡した場合にLLMが指示にどこまで従うか(fact所属を
   本当に守るか、comment_anchorの範囲を本当に守るか)は、実際のAPI
   呼び出しでの検証が必要(6節参照、非対象事項として今回は未実施)
4. **B1のEvidence Density/自然さへの影響は理論上は無いはずだが未検証**。
   B1 Writerのcommon_fact_ids/optional_b1_fact_idsの区別自体は「情報を
   削れ」という指示ではなく「所属Pointを守れ」という指示のため、
   理論上はB1のEvidence Densityやspoken-firstの自然さを損なわないはず
   だが、これも実LLM検証が無いため確定的には言えない
5. **Comment 1・2は今回対象外**。ER-008監査では大半が互換性ありと確認
   済みだが、将来他のTopicで同様の不整合が見つかった場合は、同じ
   パターン(comment_anchor化)を適用する拡張が必要になる

## 10. Production採用可否の推奨

**推奨: 条件付きで次段階(実LLM検証)へ進む価値がある。ただし現時点で
Production配線済みとは言えない。**

根拠:
- 決定論的Structural Validator自体は完成し、fixtureと実データ
  (No.4〜6)の両方で、ER-008が発見した具体的な問題を正確に検出できる
  ことを示した(6節)
- 実装は完全にオプトインであり、既存Topic・既存Pipelineへの影響が
  ゼロであることをコード・regression両面で確認した
- 一方、「Blueprintを実際にLLMへ生成させ、そのBlueprintに従ってA2/B1
  Writerが実際に望ましい記事を書けるか」という、このタスクの中心的な
  価値仮説そのものは、まだ実LLM呼び出しでの検証を経ていない(新規Writer
  API呼び出しが必要なため、タスク仕様の承認プロセスに従い今回は実施
  していない)

次のステップとして、以下の少数回・低コストな検証を提案する(ユーザー
承認が前提):
1. No.7以降の次期新規Topic 1件(またはNo.4〜6のいずれか1件の再生成、
   ただし既存記事の置き換えになるため要判断)で、実際にBlueprint生成→
   A2/B1 Writer→Comment生成のフルパイプラインを実行し、Structural
   Validatorを通す
2. 生成された記事・Commentを人手で読み、8節の見積りコストが妥当か、
   B1のEvidence Density/自然さが実際に維持されているかを確認する

## 11. CURRENT_SPEC.md / DECISION_LOG.md / OPEN_ITEMS.mdの更新

- **DECISION_LOG.md**: 本タスクのDecision(Shared Point BlueprintをA2/B1
  Point構造のSSOTとして採用する設計方針)を新規記録した
- **OPEN_ITEMS.md**: OPEN-63を、Blueprint実装完了・実LLM検証待ちとして
  更新した
- **CURRENT_SPEC.md**: 今回は更新していない。理由: CURRENT_SPECは
  「現在正式に採用されている仕様」を記録する場所であり、本タスクは
  コード実装が完了した段階に留まり、実LLM検証・Production配線を
  経ていないため、正式仕様として記載するのは時期尚早と判断した
  (10節の次ステップ完了後、正式仕様化のタイミングで追記する)

## 非対象・完了

有料Writer APIによる新規記事生成、新規TTS/ASR生成、既存No.1〜6記事の
一括再生成、新しいRuntime LLM Checkerの追加、いずれも実施していない。
無関係な既存OPEN項目の修正も行っていない。
