# ER-003-CEFR-DIRECT-03 実行報告(A01・ADD03 CEFR Direct Cross-Genre Validation)

**管理ID: ER-003-CEFR-DIRECT-03**
**実施日: 2026-08-13**
**ステータス: `PROTOTYPE / EXPERIMENT`(N増し検証。Production仕様化はしていない)**

## A. Executive Summary

**6版すべて完全記事構成で生成成功。3ジャンル(A02/A01/ADD03)を通して、
B1 V2だけがFact Safety上の問題を起こすという一貫したパターンを確認
した。**

- A01(スポーツ)・ADD03(経済)とも、B2 V2・B1 V2・A2 V2改1の3版が
  STRUCTURE_PASS、技術的再試行0回で生成できた
- Fact Checker: 6版すべて`PASS`(矛盾0件)
- **Ledger Deviation Check: B1 V2だけが両ジャンルで逸脱を検出した**
  (A01: MAJOR 3件、ADD03: MINOR 2件)。B2 V2・A2改1はいずれも
  `LEDGER_COMPLIANT`
- **これで3ジャンル(A02/A01/ADD03)すべてにおいて、B1 V2だけが何らかの
  Fact Safety上の問題(A02: Fact Checker FAIL、A01: Ledger Deviation
  MAJOR3件、ADD03: Ledger Deviation MINOR2件)を起こしている。**
  B2・A2改1はこの3ジャンルを通じて無傷(Fact Checker PASS・Ledger
  Deviationなし)である
- Point One/Two: 全6版が目標30〜60語の範囲内(34〜49語)
- A2改1は、スポーツの試合展開の緊張感・経済記事の制度説明の両方で、
  「幼い英語」「教材調」に崩れることなく機能した(F節)

これは単なる偶然ではなく、B1のDifficulty instruction自体(「話の
つながりをより明示的にする」「圧縮された表現より明確な直接説明を
優先する」)が、Ledgerが裏付けていない解釈的な接続を書き手に誘発
しやすいという、再現性のある構造的傾向である可能性が高い(H-2節)。
最終的な採否判断はユーザーに委ねる。

## B. A01 Comparison

Original(既存VFL-02最終版)・B2 V2・B1 V2・A2 V2改1の全文は比較
Artifact(J節)参照。

## C. ADD03 Comparison

同上。全文は比較Artifact参照。

## D. A01 Difficulty QA

| 軸 | B2 V2 | B1 V2 | A2 V2 改1 |
|---|---|---|---|
| 1. Naturalness | 高、絵文字・引用修辞("Protect this lead...")あり | 良好、平易な宣言文中心 | 良好、平易だがテンポは維持 |
| 2. Listening ease | 中 | 中〜易 | 易しい |
| 3. Vocabulary burden | 中〜高("expected-goals"等) | 中 | 低〜中 |
| 4. Sentence-processing burden | 中 | 中 | 低〜中 |
| 5. Abstractness | 中(統計への解釈付与、ただし慎重に留保) | 中(統計への解釈付与、留保が弱い) | 低(統計を単純列挙) |
| 6. Amount of inference required | 中 | 中 | 低 |
| 7. Narrative clarity | 高 | 高 | 高 |
| 8. Editorial engagement | 高(絵文字・修辞的引用・"door"比喩) | 中〜高 | 中〜高("Then came the final blow."等) |
| 9. Adult-news feel | 強い | 強い | 強い、緊迫感を維持 |
| 10. Fact accuracy | `PASS`・`LEDGER_COMPLIANT` | `PASS`だが`LEDGER_DEVIATION`(H-2節) | `PASS`・`LEDGER_COMPLIANT` |

## E. ADD03 Difficulty QA

| 軸 | B2 V2 | B1 V2 | A2 V2 改1 |
|---|---|---|---|
| 1. Naturalness | 高、対句的な文構成("the rate was announced, but the system behind it was not") | 良好、平易な短文中心 | 良好、引用修辞("Twenty percent of what?")で興味を引く |
| 2. Listening ease | 中 | 中 | 易しい |
| 3. Vocabulary burden | 高 | 中 | 低〜中 |
| 4. Sentence-processing burden | 中〜高 | 中 | 低〜中 |
| 5. Abstractness | 中〜高 | 中(結論部でやや性急な一般化、H-2節) | 低〜中 |
| 6. Amount of inference required | 中 | 中 | 低〜中 |
| 7. Narrative clarity | 高 | 高 | 高 |
| 8. Editorial engagement | 高 | 中〜高 | 中〜高 |
| 9. Adult-news feel | 強い | 強い | 強い |
| 10. Fact accuracy | `PASS`・`LEDGER_COMPLIANT` | `PASS`だが`LEDGER_DEVIATION`(H-2節) | `PASS`・`LEDGER_COMPLIANT` |

## F. A2 Cross-Genre Evaluation(A2改1がジャンルを超えて機能したか)

| 評価観点 | A02(参考、DIRECT-02) | A01(スポーツ) | ADD03(経済) |
|---|---|---|---|
| one main idea at a timeが機能しているか | 機能した | 機能した(例: "England led 1-0."と得点経過を短文で分離) | 機能した(例: "So, this was a proposal. It was not an active fee."と2文に分離) |
| 難しい概念を易しい単語へ置換しただけか | いいえ、概念自体を再構成 | いいえ。統計の解釈を加えず単純列挙にとどめ、B1のような性急な一般化を避けた | いいえ。「提案が制度になっていない」という核心を、B1のような性急な結論なしに保った |
| Listening時に情報を複数保持させないか | 概ね回避 | 概ね回避(得点経過を1文1情報で提示) | 概ね回避 |
| 幼い英語になっていないか | なっていない | なっていない。緊迫感のある展開表現("Then came the final blow.")を維持 | なっていない。引用修辞("Twenty percent of what?")で大人向けの興味を保持 |
| 教材調になっていないか | なっていない | なっていない | なっていない |
| 記事の勢いを失っていないか | 失っていない | **失っていない。**"Then Argentina changed everything."等、ドラマ性のある短文を残しつつ易しい語彙で構成できている | 失っていない。市場の緊張感("The oil market moved quickly, but not in a straight line.")を維持 |

**結論**: A2 V2改1(Cognitive Load Reduction)は、A02(制度/SNS)・A01
(スポーツ)・ADD03(経済/地政学)の3ジャンルすべてで、「易しいが幼く
ない自然なニュース英語」として一貫して機能した。特にA01では実況的な
緊張感を保ったまま情報量を絞り、ADD03では制度説明を順序立てて展開
できており、12節・13節で懸念されていた「勢いの喪失」「概念の圧縮
不足」は確認されなかった。

## G. B1 vs B2 Value Evaluation(3ジャンル横断)

**今回の最重要な所見**: B1専用英文を別途生成・Fact Check・Ledger
Deviation Check・(将来的には)音声化する制作コストに見合う実用差が
あるかについて、3ジャンルの結果は一貫して否定的な材料を示した。

| Article | B2→B1の差 | B1固有のFact Safety問題 | B1専用英文の実用価値 |
|---|---|---|---|
| A02(参考、DIRECT-02) | SOMEWHAT CLEAR | Fact Checker `FAIL`(1件) | UNCERTAIN〜NO |
| A01 | WEAK〜SOMEWHAT CLEAR | Ledger Deviation `MAJOR`×3(Point Two集中) | **NO** |
| ADD03 | SOMEWHAT CLEAR | Ledger Deviation `MINOR`×2 | UNCERTAIN〜NO |

**難易度差の大きさについて**: B2→B1の語彙・抽象度の差は実在するが、
B1→A2改1の差(具体性・単純化の踏み込みが明確に大きい)と比べると
一貫して小さい。文の平均語数で見ても、A01はB2=14.2語→B1=12.7語
(-1.5)に対しB1→A2改1は12.7語→10.1語(-2.6)、ADD03はB2=16.8語→
B1=14.2語(-2.6)に対しB1→A2改1は14.2語→13.2語(-1.0、ただし文数が
B1=28→A2改1=30に増え、1文あたりの情報量はさらに下がっている)と、
B2→B1のステップがB1→A2ほど際立たない。

**Fact Safetyについて(今回新たに確認された最重要の知見)**: 3ジャンル
すべてで、Fact Checker PASS・Ledger Deviationなしを両方満たしたのは
B2とA2改1のみだった。B1 V2は3ジャンルすべてで何らかの問題を起こして
おり(A02: Fact Checker FAIL、A01: Ledger Deviation MAJOR3件、ADD03:
Ledger Deviation MINOR2件)、これは特定ジャンルに固有の偶然ではなく、
B1のDifficulty instruction自体に起因する再現性のある傾向である可能性
が高い(H-2節で機序を分析)。

**総合評価**: 現時点のデータは、「B2本文を共通化し、B1は学習支援
(vocabulary hint、pre-listening summary等)によって理解可能にする」
というDecision候補2を支持する材料の方が、「B1専用英文を維持する」
Decision候補1・3を支持する材料より多い。ただし、これは3記事×1回
生成の結果であり、best-ofではなくサンプルサイズも小さいため、断定
はしない。

## H. Fact Safety

### H-1. 集計

| Article | Version | Fact Check | Ledger Deviation | 技術的再試行 |
|---|---|---|---|---|
| A01 | B2 V2 | `PASS` | `LEDGER_COMPLIANT` | 0 |
| A01 | B1 V2 | `PASS` | `LEDGER_DEVIATION`(MAJOR×3) | 0 |
| A01 | A2 V2改1 | `PASS` | `LEDGER_COMPLIANT` | 0 |
| ADD03 | B2 V2 | `PASS` | `LEDGER_COMPLIANT` | 0 |
| ADD03 | B1 V2 | `PASS` | `LEDGER_DEVIATION`(MINOR×2) | 0 |
| ADD03 | A2 V2改1 | `PASS` | `LEDGER_COMPLIANT` | 0 |

### H-2. B1 V2のLedger Deviation詳細分析

#### H-2-1. A01(MAJOR 3件、すべてPoint Two集中)

該当箇所: "### The numbers show Argentina's growing pressure" /
"Argentina also had more of the ball and spent more time finding
space in the final third." / "The late comeback was dramatic, but
it did not appear from nowhere."

- 見出し自体が「圧力が高まっていった」という時間的推移を示唆するが、
  Ledgerの統計は試合全体の集計値であり、推移を示すものではない
- 「ファイナルサードでスペースを探すのに長い時間を費やした」は、
  Ledgerの実際のFact(ファイナルサードでのレセプション回数230対87)を
  「時間」という別の指標へ置き換えている
- 「終盤の逆転は前触れなく起きたわけではない」という一文は、試合全体
  の統計と終盤の逆転劇との間に、Ledgerが裏付けていない因果的・予兆的
  関係を持ち込んでいる

#### H-2-2. ADD03(MINOR 2件)

該当箇所: "The 20% plan was therefore dropped before a collection
system was created." / "The 20% charge lasted only about a day"

- 前者は、Ledgerが確認しているのは「制度設計の詳細が示されないまま
  翌日に撤回された」ことまでであり、「制度が実際に作られなかった」
  という否定形の断定はLedger外の具体的事実である
- 後者(In One Line)は、本文では「提案(proposal)であって実施済みの
  料金ではない」と明記しているにもかかわらず、結びの一文だけを見ると
  実際に料金が課され1日間存続したかのように読める

#### H-2-3. 共通する機序(仮説)

A01・ADD03のいずれも、**Fact Checker(実世界のWeb検索と照合)では
`PASS`**だった一方、**Ledger Deviation Check(あらかじめ確定した
Verified Fact Ledgerとの整合性のみを確認)では逸脱**と判定された。
これは、記事の主張が実世界的には広く裏付けられていても、Verified
Fact Ledger方式が意図的に採用している「Ledgerに明記された範囲内
だけを事実源とする」という制約を超えていたことを意味する。

B1のDifficulty instructionは「話のつながりをより明示的にする
(make the path from one idea to the next more explicit)」
「圧縮された表現より明確な直接説明を優先する」ことを求めている。
この指示が、Ledger上では独立している複数のFact(試合統計・逆転劇、
提案撤回・制度不存在)の間に、書き手が明示的な関係性(因果・時系列の
断定)を補って埋めようとする方向へ働いた可能性が高い。B2は抽象度を
残すことで安全にヘッジでき("those numbers do not guarantee a
result, but they suggest...")、A2改1は解釈を加えず事実を単純列挙
することで安全を確保できた一方、B1は「明示的だが単純化された説明」
という中間的な立ち位置を狙う過程で、Ledgerが支持しない解釈的な
接続を書いてしまうリスクの高い領域に入り込んだと考えられる。

## I. Point / Length Analysis

### A01

| Version | Main Story | Point One | Point Two | In One Line | Total | Sentences | Avg len | Max len |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B2 V2 | 222 | 41 | 37 | 18 | 318 | 23 | 14.2 | 27 |
| B1 V2 | 231 | 34 | 39 | 18 | 322 | 26 | 12.7 | 20 |
| A2 V2改1 | 229 | 34 | 37 | 17 | 317 | 32 | 10.1 | 24 |

### ADD03

| Version | Main Story | Point One | Point Two | In One Line | Total | Sentences | Avg len | Max len |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B2 V2 | 272 | 42 | 42 | 27 | 383 | 23 | 16.8 | 31 |
| B1 V2 | 278 | 44 | 49 | 25 | 396 | 28 | 14.2 | 29 |
| A2 V2改1 | 276 | 46 | 48 | 22 | 392 | 30 | 13.2 | 23 |

**全6版でPoint One・Point Twoは目標30〜60語の範囲内**(34〜49語)に
収まった。総語数もすべてsoft range(280〜420語)内。範囲外事項は
発生しなかった。

## J. Comparison Artifact

Original(参照)・B2 V2・B1 V2・A2 V2改1の全文(先頭配置)、Difficulty
QA、Fact Safety、Point/Length Analysis、Cross-Genre Summaryをまとめた。

**URL**: https://claude.ai/code/artifact/44c6d8c1-8ffd-4dff-9cb7-39cfba219f79

リポジトリ内の原本: `er003_output/cefr_direct_03/comparison.html`

## K. Production非変更確認

- **CURRENT_SPEC.md・R4 Production prompt・VFL/spoken_first/
  cefr_direct_01/02関連スクリプト**: 無変更。新規の独立ファイル
  (`er003_v1_cefr_direct_03_generate.py`)から、これらの関数を
  読み取り専用でimportした
- **A01・ADD03のOriginal**: 再生成していない(既存VFL-02最終rerun版
  をそのまま使用)
- **既存CEFR仕様**: 廃止・変更していない
- **B1/B2本文共通化のProduction決定・B1学習支援設計**: 実施していない
- **Key Phrase生成・TTS/audio**: 実施していない
- **OPEN-35**: 変更・CLOSEしていない
- **新規Topic E2E**: 実施していない(既存A01・ADD03のTopic・Ledgerの
  み使用)

## L. 次のDecision

以下から提案する。

### Decision候補1

B2/B1を別英文として維持する。

### Decision候補2

B2/B1本文を共通化し、B1は学習Supportで理解可能にする。

### Decision候補3

B1/B2 Difficulty gapを再設計して別英文を維持する。

**今回の結果を踏まえた所見**: G節で整理した通り、3ジャンル(A02/A01/
ADD03)すべてでB1 V2だけがFact Safety上の問題を起こしており、かつ
B2→B1の難易度差はB1→A2ほど大きくない。この2点から、**Decision候補2
(B2本文共通化+B1学習支援)がもっとも支持される**と考えるが、これは
3記事×1回生成というサンプルサイズの小さい検証結果であり、Decision
候補3(B1のDifficulty instructionを、H-2節で分析した機序—Ledgerが
裏付けない解釈的接続を持ち込みやすい点—を踏まえて再設計する)を
試す余地も残っている。

A2については、A2 V2改1が3ジャンルすべてで「易しいが幼くない自然な
ニュース英語」として一貫して機能したことが確認できた(F節)。この
結果は、A2改1をProduction候補としてN増し完了扱いにするための材料
として十分と考えるが、最終的な採否・次段階(B1/B2の扱いの確定、
新規Topic E2Eの要否を含む)の判断はユーザーに委ねる。

## 対象ファイル・新規Artifact一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_cefr_direct_03_generate.py`(新規) | A01/ADD03向けB2/B1/A2改1の完全記事生成パイプライン。VFL-01・en_direct_ab_01・spoken_first_01_r1・cefr_direct_02のProduction関数を読み取り専用でimport |
| `er003_output/cefr_direct_03/{A01,ADD03}/{B2_v2,B1_v2,A2_kai1}/`(新規) | 各版のarticle.md・metrics.json・length_report.json・fact_qa.json・ledger_deviation.json・audit記録 |
| `er003_output/cefr_direct_03/run_summary.json`(新規) | 実行要約 |
| `er003_output/cefr_direct_03/comparison.html`(新規) | 比較Artifact原本 |

## 受入条件(Git操作報告)

Git操作を行った場合のcommit/push状態は、本報告の送付メッセージ末尾を参照。
