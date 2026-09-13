# EDITORIAL-FUTURE-ARTICLE-DESIGN-01_REPORT.md

管理ID: EDITORIAL-FUTURE-ARTICLE-DESIGN-01
性質: 設計+Trial準備(¥0、API呼び出しなし)。Discovery Focus Module再検証
(FAMILY-A-DISCOVERY-FOCUS-MODULE-REVALIDATION-01)と並行実施。Production
経路・Discovery進行中の成果物・SSOT本文・Git は無変更。Status:
`USER_DECISION_REQUIRED`(設計選択・テーマ選定・Trial費用承認待ち)。

## 0. ユーザー指示(原文)

> Futureの記事設計を、Discovery Focus Module再検証と並行して進めてください。まず現行リポジトリの正式仕様・Writer・QA経路を確認し、以下の編集方針を満たす独立したTrial設計を作ってください。
> Futureの主役は「未来を描く面白さ」です。聞き手が強くわくわくする、または暗い未来なら強い不安を感じるような、印象に残る記事を目指します。現在のエビデンスは制作時の足場と内部の整合性確認に使いますが、完成記事で研究・出典・データの説明を前面に出さないでください。DiscoveryやTrendのような「現在の根拠を解説する記事」に寄せないことが重要です。
> 決定済みの条件は次のとおりです。
> * ナレーターは1人。時間軸はテーマごとに選び、記事内で自然に分かるようにする。
> * 描く未来は意味のある1〜3通り。数合わせの分岐は作らない。希望のある未来も、不安を呼ぶ未来も扱える。
> * 未来の具体像と、そこに至る変化・条件の両方を扱い、重点はテーマごとに選ぶ。
> * 仮想の未来の場面は使ってよいが必須ではない。冒頭や展開の型も固定せず、題材に最も合う構成を選ぶ。
> * 自由な想像を許す。ただし、確認済みの現在の事実と想像した未来を混同し、未来を確定事実として語らない。
> 現行A-Familyの型分類にはFutureがなく、Writerの型別登録はTrendのみです。また共通PromptはLedger外の具体的事実を禁じ、Main Story・2つのPoint・In One Lineを要求しています。既存の仕組みにFutureの文言を足すだけで済むと決めつけず、①FutureをどのFamily・経路に置くか、②内部で「確認済みの事実/仮定/想像した未来」をどう区別しQAするか、③既存の2Point構成やPoint Role Planningをどう扱うか、を設計してください。未来の分岐数とPoint数は対応させないでください。想像を許すために事実確認を一律に緩める案は避け、事実の誤りと、明確に仮想として描いた内容を区別してください。
> まず¥0で設計とTrial用の準備を進め、現行経路への影響、比較方法、記事の面白さ・Futureらしさ・事実と想像の区別を評価する観点、費用上限を報告してください。新規記事のテーマは既存の選定ルールに従って候補を提示し、私が選びます。API費用が発生するTrialとProduction採用は、設計・費用を確認してから別途判断します。Discoveryの進行やProduction経路には、この作業で変更を加えないでください。

## 1. 読んだファイル・該当行(範囲限定Read/Grep)

- `CURRENT_SPEC.md`: L685-736(A-Family Editorial Type 2軸判定、Discovery/
  Why・News・Trend Synthesisの3分類)、L736-834(News Editorial Mode
  [Trend Synthesis]節、`editorial_type_module_block`配線・
  `resolve_editorial_type_module_block()`のPRODUCTION_WIRED記述)、
  L837-850(Discovery/Why[Pool型]節、最小節)、L564-621(A2/B1構造11パート、
  In One Lineの構成)、L571(In One Line=新規fact追加禁止)。**Future型の
  記述はCURRENT_SPEC.mdに一切なし(既存指摘どおり)**。
- `er012_b_family_editorial_type_registry_01.py`: 全文Read(1回)。
  B-Family Voices専用のregistryであり、Trendの型別登録は含まれない
  (A-Family側は別ファイル)。5区切り物理構造(Hook/Voice A/Voice B/
  Tension/Closing)、Voice複数話者前提であることを確認。
- `er006_pool_pilot_01_writer.py`: L23-107、`run_writer_for_theme()`が
  `editorial_mode`引数→`gen.resolve_editorial_type_module_block()`を
  呼び、`run_metadata.json`へ記録する経路を確認(Production Writer正式
  初回経路)。
- `er003_v1_n3_01_articles_generate.py`: L110-278(COMMON_BLOCK_TEMPLATE、
  Main Story/Point One/Point Two/In One Line構成要求、L219
  「Verified Fact Ledgerに無い新しいFactの追加」禁止、L268-277
  「Fact Ledger使用上の制約」)、L298-346(Evidence Compression Block、
  opt-in方式の前例)、L349-469(Trend Synthesis Editorial Type Module:
  `TREND_SYNTHESIS_FOCUS_MODULE_BLOCK`/`TREND_SYNTHESIS_ENGAGEMENT_BLOCK`/
  `EDITORIAL_TYPE_MODULE_BLOCKS`辞書/`resolve_editorial_type_module_block()`)、
  L472-495(`build_common_block()`、`editorial_type_module_block`引数の
  差し込み位置=【Spoken-first原則】直前)。
- `er002_ja_web_research_r3.py`: `^def |^class`一覧(全16件)、L237-300
  (`build_fact_check_prompt()`のvoice_attribution_block/
  canonical_spelling_block opt-in引数パターン=Future用block追加の前例)。
- `er009_ledger_deviation_recalibration_02.py`: L1-135(Ledger Deviation
  Checker候補v2の設計思想、`DEVIATION_FLAG_KEYS`10種、
  `unsupported_new_claim`/`changed_certainty`等の定義文言、MAJOR/MINOR
  自動降格ロジック)。
- `er011_point_role_value_planning_01.py`: L1-55(モジュールdocstring、
  Point Role Planning+Point Value QAの2段構成の背景)、`^def|^class`一覧。
- `er008_point_overlap_qa_18.py`: `^def|^class`一覧(lexical overlap判定、
  Full Storyとの重複検出)。
- `er010_ledger_local_rewrite_09.py`: `^def|^class`一覧(Local Rewrite+
  差分QA、`classify_deviation_role()`等、claim単位でcontextを見る既存
  実装パターン)。
- `docs/pm/PM_GOVERNANCE.md`: 13節(L1519-1563、新規記事テーマ選定ルール、
  Fable/Claudeが単独で決めない・複数候補提示・13-4対象外[regen/retry/
  Local Rewrite]・13-5最終版候補前提)。
- `er011_discovery_generalization_towels_trial_11_run.py`: L86-142
  (Discovery/Why Focus Moduleのeditorial_type_module_block注入パターン
  =Trend Synthesisと同型のTrial駆動方式)、L250-298(Research→Ledger
  Verification2段呼び出しの実装パターン)。
- `FAMILY-A-DISCOVERY-FOCUS-MODULE-REVALIDATION-01_REPORT.md`: L151-164
  (4記事[A2/B1×baseline/focus]の費用実測合計¥113.91、上限¥320)。
- `FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-COST-01_REPORT.md`:
  L48-59(Research¥27.87+Ledger Verification¥27.60、text-gen合計
  ¥117.72/1テーマ[A2+B1B])。
- `POOL_TOPIC_MASTER.md`: 本タスクで検討したテーマ候補語(cashless/
  autonomous vehicle/robot/four-day workweek/sea level/workweek等)を
  grep、既存登録なし(新規Research前提と確認)。

Analytical Leakage Check(B-Family)は独立ファイルが存在せず、
`er012_b_family_editorial_type_registry_01.py`の`PHASE2_PENDING_NOTES`内で
「正式化可否USER_DECISION_REQUIREDのまま未確定」とコメント記載されている
のみ(実装ファイルなし)。指定Read対象が実在しなかったため、この事実を
そのまま記録する。

## 2. ①配置(最低3案の比較+推奨)

| 案 | 変更ファイル(想定) | 実装コスト | opt-in可否 | Discovery/Trend/News無影響 | Future編集方針との適合 |
|---|---|---|---|---|---|
| **A. A-Family新型`future`(共通Writer+型別モジュール)** | `er003_v1_n3_01_articles_generate.py`(`EDITORIAL_TYPE_MODULE_BLOCKS`へ`"future"`キー追加のみ、Trend Synthesisと完全に同型)。Writer呼び出し側(`er006_pool_pilot_01_writer.py`)は`editorial_mode="future"`を渡すだけで無改修。Trial駆動はDiscovery Trial-11同型の専用runner(新規ファイル、Production runner無変更) | 低(既存`editorial_type_module_block`placeholder機構をそのまま再利用、新規関数1個+定数2〜3個) | 高。`editorial_mode`文字列が未指定の全既存記事はバイト単位不変(既存単体テストパターンを踏襲可能) | 担保できる(Trend Synthesisと同じfail-closed設計。未知mode文字列はValueError、Discovery/News/Trend側のmode文字列とは独立したキー) | 良好。Main Story/Point One/Point Two/In One Lineという物理コンテナ(TTS用11パート構造・Audio Gate)は維持しつつ、モジュールブロックで意味づけ(未来像/分岐/条件)を差し替えられる。ただし②③の追加設計(層分け・QA)が別途必要 |
| **B. B-Family系独立Writer(generic template+theme data方式)** | `er012_b_family_voices_writer_generic_01.py`型の新規Writerファイル、独自QA配線一式(Fact Checker呼び出し・Ledger Deviation Checker呼び出しを個別に再実装) | 高(Fact Checker/Deviation Checker/Local Rewriteの呼び出し配線をB-Family用に別途複製する必要。現行B-FamilyはVoice A/B/Cの複数話者・5区切り物理構造が前提で、Point Overlap QA/Point Role Planningを現状使っていない) | 中(新規ファイルなので既存A-Family出力への影響はゼロだが、Fact Safety系の安全装置を独自に再実装するリスクが伴う) | 担保できる(独立ファイルのため無影響) | **適合が低い**。B-Family物理構造(Hook/Voice A/Voice B/Tension/Closing)は「複数の声が異なる立場を語る」設計であり、ユーザー決定「ナレーターは1人」と構造的に矛盾する。Voice構成を1声に潰すのはB-Family設計思想の転用にすぎず、実質的に新規設計と同じコストがかかる |
| **C. 新規Family C(独立経路、共通QAの一部のみ再利用)** | 新規Writer・新規Prompt・新規runner一式、Fact Checker A'/Ledger Deviation Checkerの呼び出し関数だけを再利用 | 最高(研究/Ledger生成部分[er002_ja_web_research_r3.py等]は既存共有可能だが、Writer本体・構成規約・Audio Gate required_segments定義まで全て新規に設計・実装・検証する必要) | 高(独立ファイルのため既存Family無影響) | 担保できる | 理論上は最も自由(「冒頭や展開の型も固定せず」の要求に一番忠実になれる)。ただし①Local Rewrite・Point Overlap QA・Audio Validation Gateのrequired_segments・Point Role Planning等、A-Familyが既に持つ安全装置を全て作り直す必要があり、Trial規模(¥0設計+4記事Trial)に対して過大なコスト。Production化までの距離も最も遠い |

**推奨: 案A(A-Family新型`future`、`editorial_type_module_block`方式)**。
理由:
1. Trend Synthesisが同じ機構で2026-09-08に`PRODUCTION_WIRED`済みであり、
   「既存A-Family全出力はバイト単位で不変」という安全性が実証済みの
   パターンに乗れる。
2. Fact Checker A'・Ledger Deviation Checker・Point Overlap QA・Local
   Rewrite・Point Role Planningという既存の安全装置(Gate)をそのまま
   利用でき、Future固有に必要な追加は「②のQA層分け」だけに限定できる。
3. 「ナレーター1人」という決定済み条件と、A-Familyの単一ナレーター
   前提が自然に一致する(B-Family[複数Voice]と概念的に矛盾しない)。
4. Discovery/Trend/News/既存Voicesは、いずれも無改修または
   opt-inガード(`family == "B"`のような既存code-level gating前例)で
   完全に無影響を維持できる。

## 3. ②事実/仮定/想像の区別とQA(データ構造案+QA要件、未実装)

### 3-1. Ledger 3層スキーマ案(draft、`er013_future_article_design_draft_01.md`に本文転記)

既存Ledgerのタグ規約(`[VOICE_n_EVIDENCE]`、`build_voice_attribution_block()`
の前例)を踏襲し、以下3層のタグをVerified Fact Ledger内に追加する案:

1. `[PRESENT_FACT]` — 既存のConfirmed Fact(現行Researcher/Verification
   経路で検証済みの「現在の事実」、既存フォーマットを完全に踏襲、無変更)
2. `[FUTURE_ASSUMPTION]` — 明示的な仮定・条件(例: 「このトレンドが今の
   ペースで続いた場合」)。仮定自体はLedger外での独立検証対象ではないが、
   「どのPRESENT_FACTを根拠にした延長か」を`based_on:`フィールドで
   PRESENT_FACTへ紐づける(捏造防止、根拠のない仮定を禁止するため)
3. `[IMAGINED_FUTURE]` — 想像した未来の具体的場面・情景の下書き材料。
   これ自体はFact Checkの対象外だが、「明確に想像として書かれているか」
   だけを新QAで検証する

### 3-2. QA設計方針(実装しない、要件定義のみ)

- **Layer 1(PRESENT_FACT)に紐づく文**: 既存Fact Checker A'
  (`WRITER_FACT_CHECK`/`build_fact_check_prompt()`)・既存Ledger Deviation
  Checker(10 flags)を**現行のまま厳格に適用**(閾値・スキーマ変更なし)。
- **Layer 2/3(FUTURE_ASSUMPTION/IMAGINED_FUTURE)に紐づく文**: 新設
  「Future Framing QA」(draft名、未実装)を要件定義する。判定項目案:
  1. **Framing(確定事実化していないか)**: 未来の記述が"will"のような
     断定調ではなく、明示的なhedging(may/might/could/one possible
     future等、日本語なら「〜かもしれない」「もし〜なら」)で書かれて
     いるか
  2. **現在事実の捏造がないか**: 想像パッセージ内に紛れ込んだ「現在は
     既に〜だ」という現在時制の主張が、Layer 1のLedgerと矛盾していない
     か(これは想像許容の対象外、Layer 1相当のFact Safetyをこの一点
     だけ想像パッセージ内でも適用する)
  3. **仮定の明示性**: 想像の前提となる仮定が本文中で読者に分かる形で
     示されているか(暗黙の仮定のまま断定していないか)
  4. **Discovery/Trend化していないか**: 研究名・出典・サンプルサイズ・
     方法論の説明が、想像パッセージの主役になっていないか(根拠解説の
     前面化検出)

### 3-3. Ledger Deviation Checkerの誤検知対策(一律緩和を避ける具体策)

`unsupported_new_claim`/`changed_certainty`は、Layer 3の想像文に対して
高確率で誤爆する(想像した未来像はLedgerに存在しない具体的主張そのもの
であるため)。対策案:
- 一律の閾値緩和・フラグ無効化は行わない(ユーザー指示どおり回避)。
- 代わりに、**チェック対象のルーティングを変える**: `claim_in_article`
  ごとに、まずLayer(1/2/3)を判定し、Layer 1のみ既存10-flag Checkerへ、
  Layer 2/3のみ新Future Framing QAへ振り分ける。
- ルーティングの実現方法(未確定、Trial設計課題として明記): 現行の
  Ledger Deviation Checkerはarticle_text全体を渡す方式であり、
  センテンス単位のLayerタグを持たない。案(a) Writerに、想像パッセージを
  本文中で明確な文体・書式規約(例: 導入句"Picture this:"固定、または
  段落レベルの明示マーカー)で区切らせ、QA側がその区切りで自動的に
  Layer判別する。案(b)
  `er010_ledger_local_rewrite_09.py::classify_deviation_role()`の
  文脈判定パターンを拡張し、`claim_in_article`前後の文脈からLayerを
  推定する(既存コードの前例はあるが、Future用の新規分類器が必要)。
  どちらも**実装はせず、Trial設計上の論点として提示するのみ**。

## 4. ③2Point構成とPoint Role Planningの扱い(比較+推奨)

| 案 | 内容 | 評価 |
|---|---|---|
| 維持案 | 現行Main Story/Point One/Point Two/In One Lineの役割定義を無変更のまま使う | 分岐1〜3・仮想未来像という新要素と噛み合わず、Point Balance原則(「本文とは別の切り口」等)がFuture向けに再定義されないまま流用されるリスク |
| **Future専用再解釈案(推奨)** | Main Story=未来像本体(1〜3通りの分岐は全てMain Story内で扱う)。Point One・Point Twoは固定役割にせず、テーマごとに以下の候補リストから異なる役割を1つずつ選ぶ: 「至る変化・条件」「別の未来(反転・分岐)」「見えなかった実生活上の意味」「希望/不安のどちらに転ぶかの分かれ目」。In One Line=事実要約ではなく「聞き手が持ち帰る印象」 | Trend Synthesisが既に採用している「Point One/Twoに役割の候補リストを与え、テーマごとに選ばせる」方式(L380-384「候補: 最も強いSignal・要因/仕組み、または反証Signal・限界...」)と同型で実装コストが低い。分岐数(1〜3)とPoint数(2)を意図的に対応させない設計を明文化できる |
| 完全可変案 | Point自体を固定2つにせず、記事ごとに1〜3個へ可変にする | Audio Validation Gateのrequired_segments(`point_one`/`point_two`固定)・Point Overlap QA・Point Value QAが全てPoint数=2を前提にしており、変更コストが最も高い。ユーザー指示は「分岐数とPoint数を対応させない」であり「Point数自体を可変にせよ」ではないため、過剰対応と判断 |

**推奨: Future専用再解釈案**。物理構造(###見出し2つ+In One Line)は
維持するため、既存のAudio Gate・Point Overlap QA・required_segments定義は
無変更のまま使える。

**Point Role Planningの扱い**: Trend Synthesisは`run_point_role_planning()`
を使わず、Focus Module Block内でPoint候補役割を直接指示する方式のみで
`PRODUCTION_WIRED`された前例がある。Futureも同じ理由(実装コスト最小、
Trend Synthesisと同型)で**Point Role Planningは当面不使用**とし、Module
Block内の候補役割リストのみで運用する案を推奨する。Trial結果でPointの
新規性不足(No.18型の問題)が確認された場合のみ、Future専用のRole
Planning拡張を追加検討する(段階的導入、Trendと同じ進化パス)。

**A2/B1レベル差**: 未来時制のhedging表現は両レベル共通で必須とする
(「この既定はCEFRレベルに関わらず共通」という既存の数字表現ルール
[L252]と同型の考え方)。A2は単純な"might"/"could"/明確な条件節、B1は
やや複雑な仮定法・条件構文を許容する、という語彙・文長差のみレベルで
分ける(確定事実化禁止のルール自体はA2/B1で差をつけない)。

## 5. 評価観点(採点表、各0〜2点)

| 観点 | 0点 | 1点 | 2点 |
|---|---|---|---|
| 面白さ(わくわく/不安の強度) | 感情喚起なし | ある程度の感情反応 | 強い感情反応(引き金となった文を引用可能) |
| Futureらしさ(未来像の具体性・印象) | 抽象的な一般論のみ | ある程度具体的な未来像 | 五感・具体的場面・数字化された変化が伝わる印象的な未来像 |
| Discovery/Trend化していないか | 研究・出典・データ説明が本文の主役 | 一部残る | 根拠説明が足場止まりで前面に出ない |
| 事実と想像の区別 | 確定事実として語られた未来文3件以上、または捏造された現在事実あり | 1〜2件のグレーな文 | 0件(未来は明示的仮定・想像として語られ、現在事実は正確) |
| throughline | バラバラ | 概ね一つの筋 | 明確な一つの筋+回収 |
| 1ナレーターの自然さ | 不自然な視点切替 | 概ね自然 | 完全に自然な一人語り |
| 時間軸の明示 | 不明 | 部分的に分かる | 記事内で自然にいつの未来か分かる |

採点は各項目で該当文の引用を要求する(未検証の推測で点をつけない)。

## 6. 比較方法

- baseline: 現行共通Prompt+Future題材、`editorial_type_module_block=""`
  (型モジュールなし)。
- future: 本設計案(Future Focus Module Block、Ledger 3層タグ)。新QA
  (Future Framing QA)は¥0段階では自動実装せず、**人手評価**で代替する
  (採点表適用)。
- 規模: 同一テーマ・同一Ledgerで A2×2(baseline/future)+B1×2
  (baseline/future)=4記事。Discovery Focus Module再検証
  (FAMILY-A-DISCOVERY-FOCUS-MODULE-REVALIDATION-01)と同規模。
- Trial駆動: 既存Production runner(`er006_pool_pilot_01_writer.py`、
  `er003_v1_n3_01_articles_generate.py`)は無変更のまま、Discovery
  Trial-11(`er011_discovery_generalization_towels_trial_11_run.py`)と
  同型のTrial専用driver(未作成、次work時に`er013_future_article_
  design_trial_run_01.py`のような新規ファイルとして作成する想定)を
  作り、その中だけで`editorial_type_module_block`を差し替える。Production
  ファイル側の変更は「`editorial_mode="future"`キーを
  `EDITORIAL_TYPE_MODULE_BLOCKS`辞書へ追加する」1箇所のみで、既存
  Trend/Discovery/News出力への影響はfail-closed設計により発生しない。

## 7. 費用上限見積

実測値(既存Trial):
- Discovery Focus Module再検証(4記事、Ledger再利用): 合計¥113.91
  (上限¥320)。
- Towels Trial-11(1テーマ分の新規Research+Ledger Verification):
  Research¥27.87+Ledger Verification¥27.60=¥55.47。text-gen合計
  ¥117.72(A2+B1B、QA込み)。

見積:
- 既存Ledger流用時(新規Research不要): 4記事(A2×2/B1×2、writer+QA)
  ≒¥115〜120円。上限提案: **¥300**(Discovery revalidation実績[¥320
  上限運用]を踏襲、Future Framing QA相当の追加人手評価では追加API費用
  は発生しないため据え置き)。
- 新規テーマ(新規Research+Ledger必要)の場合: 上記+¥55〜60円を加算。
  上限提案: **¥400**(新Ledgerの誤検知対応で想定外のLocal Rewrite/
  差分QAが増えた場合の安全マージンを含む)。

## 8. テーマ候補(PM_GOVERNANCE 13節準拠、5件、ユーザー選定待ち)

いずれも`POOL_TOPIC_MASTER.md`に既存登録なし(grep確認済み、新規Research
前提。既存Ledger流用候補は確認できなかった)。

1. **The Four-Day Workweek at Scale** / 「週4日労働制が当たり前になる
   未来」— 両義型。理由: 実際のパイロット導入データが既に存在し
   Ledger化しやすく、「本格普及/一部業界のみ定着/格差拡大」という
   意味のある分岐が作りやすい。
2. **Cities Designed Around Autonomous Vehicles** / 「自動運転車が
   前提の街づくりの未来」— 両義型。理由: 具体的な情景(道路・駐車場の
   再設計)を描きやすく、安全性データ等の現在の根拠が豊富。
3. **When Home Robots Do the Housework** / 「家庭用ロボットが家事を
   する未来」— 希望寄り(一抹の不安含む)。理由: 家庭内の具体的場面
   (夕方の一場面等)を描きやすく、自由時間の獲得という希望と、依存・
   スキル喪失という不安の両方を1つのテーマで扱える。
4. **The Disappearance of Physical Cash** / 「現金が消えていく未来」
   — 不安寄り(利便性という希望も含む両義)。理由: キャッシュレス化の
   進展データが既に世界的に蓄積されており、金融排除・監視への不安と
   利便性の両方を描ける。
5. **Rising Seas and the Cities That Must Move** / 「海面上昇で
   移転を迫られる都市の未来」— 不安型。理由: 感情的インパクトが強く、
   複数シナリオ(IPCC想定幅)が自然に1〜3通りの意味のある分岐へ
   対応しやすい。取り扱いには慎重な不確実性表現が必要(Fact Safety上の
   留意点として明記)。

Fable/Claudeは選定しない(ユーザー選択待ち)。

## 9. Trial用準備(¥0、Production未配線)

`er013_future_article_design_draft_01.md`(新規、root)を作成した。内容:
Future Editorial Type Module Block文面draft(Trend Synthesis Focus
Module/Engagement Blockと同型のプレースホルダー文面)、Future Framing QA
要件draft、Ledger 3層タグ規約draft。**いずれも既存のregistry/Writer/QA
ファイルへは一切importされておらず、Production経路への配線は行っていない**。

## 10. STOP/リスク

- 共通Promptの「Verified Fact Ledgerにない具体的Factを追加しないでください」
  (L219、L269)という既存不変条件と、Future方針「自由な想像を許す」は
  文言上そのままでは両立しない。Layer 2/3を明示的に「Fact Ledgerの
  対象外」として切り出す設計(本報告②)が必要であり、共通Prompt本体
  文言の変更が必要になる可能性がある(Trend Synthesisの前例と同じく、
  Module Block側で補足する形にとどめられるか、COMMON_BLOCK_TEMPLATE
  本体の一部書き換えが要るかは、実際のprompt文面draftを書いてみないと
  確定しない。draft作成時点では「補足Block追加」で対応可能と考えている
  が未検証)。
- Fact Checker A'・Ledger Deviation Checkerが想像文を「捏造」
  (unsupported_new_claim/changed_certainty)と誤判定するリスクは、
  ③のLayerルーティングが機能しない場合、高確率で顕在化する
  (Trial駆動前に自動ルーティングロジックの実装検証が必要、¥0段階では
  未着手)。
- Audio/TTS(声の表現・間・トーンでの「想像/事実」の切替表現)は今回
  対象外(現行タスクスコープ外、記事本文設計のみ)。
- 既存QAとの衝突点: Point Overlap QA(lexical overlap)・Point Value QA
  は「新しい価値を持つか」を判定するが、Future特有の「新しい未来像=
  新しい具体的主張」を許容しつつ「新しいFact(現在事実)」は許容しない
  という区別を、これらのQAが正しく扱えるかは未検証(既存QAはFuture
  想定で設計されていない)。
- 分岐数(1〜3)とPoint数(2)を意図的に対応させない設計自体が、Writer
  へ正しく伝わるかはprompt文面のwording次第であり、Trial実施までは
  「設計上そう意図している」段階に留まる。

## 11. Status

`USER_DECISION_REQUIRED`。以下3点についてユーザー判断待ち:
1. ①配置案の承認(推奨: 案A)
2. テーマ候補(8節)からの選定
3. Trial費用上限(推奨: ¥300[既存Ledger流用]/¥400[新規Ledger])の承認

上記承認後、Trial専用driver作成・4記事生成・QA・比較レポート作成の
次work(別管理ID)へ進む。
