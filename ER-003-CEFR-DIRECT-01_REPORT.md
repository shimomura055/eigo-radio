# ER-003-CEFR-DIRECT-01 実行報告(A02 3-Level x 3-Variation Direct Difficulty Test)

**管理ID: ER-003-CEFR-DIRECT-01**
**実施日: 2026-08-13**
**ステータス: `PROTOTYPE / EXPERIMENT`(N増し検証。Production仕様化はしていない)**

## A. Executive Summary

**9版の生成自体は成功。ただし2件の実運用上の課題を発見した。**

English Master(制約なしの自然な英語記事、本文のみ)を1版固定し、
A2/B1/B2 × Variation 1(Reader Profile)/2(Listening-Cognitive Load)/
3(English Master Distance)の9版を、語彙リスト・平均文長等の機械的
制約を一切使わず、自然言語の難易度指示だけで生成した。

- 9版すべてSTRUCTURE_PASS(見出し混入なし、技術的再試行0回)
- Fact Checker: `PASS` 5件、`REVIEW_REQUIRED` 5件(Master含む)、`FAIL` 0件
- Ledger Deviation: `LEDGER_COMPLIANT` 9件、`LEDGER_DEVIATION` 1件(B2
  Variation 2、MINOR)
- **Variation 3(English Master Distance)が最もクリアなB2>B1>A2の
  難易度差を作れた**(CLEAR)。Variation 1・2はSOMEWHAT CLEARにとどまる
- **A2 Variation 2で、Point One相当の情報(pilot試行の詳細)が本文へ
  前倒しされる問題を発見した**(G節)。他8版ではこの問題は発生していない
- B2 Variation 3は、English Masterとほぼ同一の文章になった(文体距離を
  「非常に近く」保つ指示の効果としては想定通りだが、独立した3版目としての
  価値をどう評価するかは要検討、G節・J節参照)

## B. English Master

**生成条件**: 日本語阪神master + 既存A02 Verified Fact Ledger
(`er003_output/en_direct_vfl_01/A02/verified_fact_ledger.txt`、新規調査
なし) + English Narrative Writer方式(Web検索なし、Ledgerのみ使用) +
「今回は本文部分のみを出力する」指示 + 「CEFRレベルを狙わず制約のない
自然な英語記事として書く」指示。1版のみ生成し、全比較で共有した(全文は
比較Artifact参照)。

**語数**: 198語(14文、平均14.3語/文、最大27語/文)

**Fact Checker**: `REVIEW_REQUIRED`。矛盾は0件。指摘は「"Let the night
feel like night again."という引用符付き表現の出典が確認できない」という
1点のみ(F節で詳述)。

**Ledger Deviation**: `LEDGER_COMPLIANT`(逸脱0件)。

## C. A2 Comparison

English Master・Variation 1・2・3の全文、10観点QA、Fact Safety、
metricsは比較Artifact(H節)の[A2 Comparisonセクション](https://claude.ai/code/artifact/d3829795-ffdb-420d-be43-e91e1d75a98e#a2)参照。

**要点**:
- V1(239語)・V3(191語)は本文のスコープを守り、具体的な一つ一つの
  出来事を順に示す平易な文体になった
- V2(261語)は、pilot試行の詳細(309世帯・4グループ・81世帯・
  9pm-7amアクセス遮断・睡眠改善報告)を本文に含めてしまった。これは
  本来Point Oneが扱う内容であり、G節の問題として扱う
- V1・V2・V3すべてFact Checker `PASS`、Ledger `LEDGER_COMPLIANT`

## D. B1 Comparison

全文・QA・Fact Safety・metricsは[B1 Comparisonセクション](https://claude.ai/code/artifact/d3829795-ffdb-420d-be43-e91e1d75a98e#b1)参照。

**要点**:
- V1(250語)は最大文長38語の1文があり、B1として意図した水準よりやや
  複雑な構文が残った
- V1・V3はMasterと同様の「引用符付き未出典の一文」を含み、Fact Checker
  `REVIEW_REQUIRED`(F節)
- V2(256語)はFact Checker `PASS`。ただし語数はB1の中で最長

## E. B2 Comparison

全文・QA・Fact Safety・metricsは[B2 Comparisonセクション](https://claude.ai/code/artifact/d3829795-ffdb-420d-be43-e91e1d75a98e#b2)参照。

**要点**:
- V1(249語)はMasterと同程度の慣用表現・比喩を保ちつつ、独自の展開
  ("log off now" vs "turning down the volume"の比喩)を作れている
- V2(265語)は3連の引用断片("One more video."/"One more message."/
  "One more quick look.")という独自の演出を使い、B2の中で最も抽象度の
  高い結び文を持つ。ただしLedger Deviation 1件(F節)
- V3(197語)はEnglish Master(198語)とほぼ同一の文章になった(G節)

## F. Fact Safety(詳細)

### F-1. REVIEW_REQUIRED 5件の内訳

このうち4件(Master・B1 V1・B1 V3・B2 V1・B2 V3、実際は5件中4件)は、
記事が引用符付きで挿入する短い一文("Let the night feel like night
again." / "After midnight, social media should become quieter by
default." / "Night should be a time to switch off." など)が、政府の
実際の発言・公式資料として確認できない、という指摘に起因する。

これらは記事オリジナルの編集的な要約フレーズであり、Fact Checkerは
いずれも「明確な矛盾ではない」と明記した上でREVIEW_REQUIREDと判定
している(contradictionsは全件0件)。この種の「引用符で囲んだ要約的な
一言」は、SPOKEN-FIRST-02/03のA02本編でも実際に使われてきた編集手法
("Put the phone away."等)であり、今回新たに導入されたリスクではない。
ただし、今回のように複数版で独立にFact Checkerが同種の懸念を示した
ことは、**「未出典の引用符付き一文」は今後もFact Checkerの注意対象に
なりやすい**という実務上の知見として記録する。

**B1 Variation 1**はこれに加え、"Nothing is demanding your attention
right now."という一文について、SNS通知に限定されない全体的な通知停止
であるかのように読める、という指摘を受けた。これは簡略化の過程で
scopeがやや広がった可能性がある表現であり、単なる引用符の問題より
一段実質的な指摘である。

**B2 Variation 1**は、記事が夜間措置を「通知の消音」中心に説明して
おり、制度の内容を狭く伝えている可能性がある、という指摘を受けた。
ただしVerified Fact LedgerのPOL-03は「通知停止だけが夜間制度の全内容
だとも、通知停止に加えて必ず完全アクセス遮断が行われるとも断定しない」
とあり、政府資料自体がこの点を明確にしていない。B2 Variation 1の
記述はLedgerの範囲を超えておらず、Fact Checkerは「明確な反対事実を
断定しているわけではない」とした上でREVIEW_REQUIREDとしており、
実質的な誤りではなくFact Checker側の慎重な判断と評価する。

### F-2. Ledger Deviation 1件(B2 Variation 2、MINOR)

該当箇所: "Britain is therefore preparing more than a technical
adjustment. It is testing whether a small change in the digital
environment can influence... the urge to keep scrolling..."

指摘: Ledgerは、午前0時〜6時の政策案そのものを英国が現在「testしている」
とはしていない。睡眠改善等が報告されたpilotは、政策案とは異なる時間帯
(午後9時〜午前7時)・異なる技術方式(アクセス遮断)を用いた、既に完了
した別の研究である。この一文は、政策案自体が現在進行形で試験中である
かのように読め、pilotと政策案を混同する恐れがある。

これは**実質的な誤りとして扱うべき、今回唯一のケース**である。B2
Variation 2の「抽象的な考えを許容する」という難易度指示が、pilotと
政策案の時系列的な違いを圧縮しすぎる方向に働いた可能性がある。

## G. Output-truncation Impact(本文のみ出力の影響)

**A2 Variation 2で、本来Point Oneが扱う内容(pilot試行の詳細)が本文へ
前倒しされる問題が発生した。**

該当箇所(A2 Variation 2の後半):
> A separate UK pilot tested a stronger kind of night rule. The full
> pilot included 309 households in four groups. In one group, 81
> households were assigned a rule that blocked selected social media
> apps from 9 p.m. to 7 a.m. Among the three types of limits tested,
> families said the night rule was the easiest to fit into daily
> life. People in that group also reported earlier bedtimes, faster
> sleep, and feeling more awake the next day. However, the study was
> small and was based mainly on what families said...

これは、既存のA02記事構成における**Point One相当の内容**(pilot試行の
規模・結果・限界)そのものである。共通prompt(全版共通)で明示的に
禁止していた「Pointで扱う予定だった補足Factを本文へ前倒しすること」
に該当する。

**発生範囲の確認**: 他8版(Master、A2 V1/V3、B1 V1/V2/V3、B2 V1/V2/V3)
は、いずれもpilotの詳細に踏み込まず、政策の説明のみで本文を構成して
おり、この問題はA2 Variation 2に限定される。

**原因の推定**: Variation 2(Listening/Cognitive Load方式)のA2向け
指示は「出来事の間の関係を明示的にする」「一度に複数の考えを保持
させない」ことを求めている。この結果、writerが「pilotの結果とその
限界」という関係性の強い情報を、本文の中に完結させて説明しようとした
可能性がある。禁止事項は共通prompt内に明記していたが、A2×V2の組み合わせ
特有の指示("make relationships between events explicit"、"present
information in a clear sequence")が、この禁止よりも強く作用したと
考えられる。

**その他の確認事項**(全9版共通):
- 本文が通常より説明過多になっていないか: A2 V2(261語)を除き、
  他8版は170〜265語のレンジに収まっており、極端な説明過多は見られない
- 結論を早く言いすぎていないか: 該当なし
- 本文だけで完全完結させようと不自然に長文化していないか: 明確な
  該当例はA2 V2のみ

**Fact accuracy自体は問題ない**(A2 Variation 2はFact Checker `PASS`)。
pilotの数字・時間帯・限界の記述は正確だが、**出力すべき範囲(本文の
役割)を超えた**という、Fact safetyとは別種の問題である。

## H. Comparison Artifact

English Master・9パターンの全文(先頭配置)、レベル別10観点QA、Fact
Safety、metrics、Cross-level比較表をまとめた。

**URL**: https://claude.ai/code/artifact/d3829795-ffdb-420d-be43-e91e1d75a98e

リポジトリ内の原本: `er003_output/cefr_direct_01/comparison.html`

## I. Production非変更確認

- **CURRENT_SPEC.md・R4 Production prompt・VFL/spoken_first関連
  スクリプト**: 無変更。新規の独立ファイル
  (`er003_v1_cefr_direct_01_generate.py`)から、これらの関数を読み取り
  専用でimportした
- **既存CEFR仕様**: 廃止・変更していない
- **Point One/Point Two/In One Line/Key Phrase生成**: 実施していない
- **B1/A2/B2音声生成・TTS・WPM調整**: 実施していない
- **新規Topic E2E**: 実施していない(既存A02のTopic・Ledgerのみ使用)

## J. 次のDecision

以下から提案する。

1. 最も良いVariationを選定する(現時点の所見: Variation 3が
   B2>B1>A2の差の明確さで最も優れるが、B2版がMasterとほぼ同一化する
   という特性を許容するかどうかは別途判断が必要)
2. 必要ならVariationを組み合わせてR2を実施する(例: 「Variation 3の
   distance指示」+「Variation 2の関係明示指示」のハイブリッド、
   または今回発見した2件の課題への対処を明示的に追加)
3. 全文構成(Point One/Point Two/In One Line含む)で再検証する
4. その後Production候補化を検討する

**今回の結果を踏まえた所見**:

- **難易度差そのものについて**: 自然言語による難易度指示だけでも、
  少なくともVariation 3(English Master Distance)では、機械的な
  文長制約なしにCLEARなB2>B1>A2の差を作れることを確認した。ただし
  Variation 3のB2版はMasterとほぼ同一の文章になっており、これが
  「B2はMasterに近いことが望ましい」という設計意図の成功なのか、
  それとも「B2 Variation 3は独自の生成的価値をほとんど加えていない」
  という限界なのかは、追加の判断が必要である
- **本文のみ出力という制約について**: 8/9版では本文スコープが守られた
  が、A2 Variation 2で1件、Point情報の前倒しが発生した。これは
  「difficulty指示の強さが、本文スコープの制約より優先されてしまう
  組み合わせがある」ことを示しており、全文構成での再検証(選択肢3)を
  行う場合は、この教訓を踏まえてスコープ制約の書き方を見直す必要がある
- **Fact safetyについて**: FAILは0件だが、REVIEW_REQUIREDが10版中5版と
  多く、そのほとんどは「引用符付きの編集的な一言」という同一パターンに
  起因する。これはFact Checker側の慎重な運用の結果であり記事の実質的な
  誤りではないケースが大半だが、唯一のLedger Deviation(B2 Variation
  2、pilotと政策案の時系列混同)は実質的な誤りであり、抽象度の高い
  難易度指示(V2のB2)が事実の時系列を圧縮しすぎるリスクを示唆している

最終判断はユーザーに委ねる。

## 対象ファイル・新規Artifact一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_cefr_direct_01_generate.py`(新規) | English Master + 9パターン生成パイプライン。VFL-01・en_direct_ab_01のProduction関数を読み取り専用でimport |
| `er003_output/cefr_direct_01/A02/english_master/`(新規) | English Master(本文のみ)のarticle.md・metrics.json・fact_qa.json・ledger_deviation.json・audit記録 |
| `er003_output/cefr_direct_01/A02/{A2,B1,B2}/{v1,v2,v3}/`(新規) | 9パターンそれぞれのarticle.md・metrics.json・fact_qa.json・ledger_deviation.json・audit記録 |
| `er003_output/cefr_direct_01/A02/run_summary.json`(新規) | 実行要約 |
| `er003_output/cefr_direct_01/comparison.html`(新規) | 比較Artifact原本 |

## 受入条件(Git操作報告)

Git操作を行った場合のcommit/push状態は、本報告の送付メッセージ末尾を参照。
