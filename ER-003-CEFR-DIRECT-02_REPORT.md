# ER-003-CEFR-DIRECT-02 実行報告(A02 V2 Full-Article Difficulty Calibration)

**管理ID: ER-003-CEFR-DIRECT-02**
**実施日: 2026-08-13**
**ステータス: `PROTOTYPE / EXPERIMENT`(N増し検証。Production仕様化はしていない)**

## A. Executive Summary

**5版すべて完全記事構成で生成成功。前回(CEFR-DIRECT-01)のPoint情報
前倒し問題は解消した。一方、B1版で1件のFact Checker `FAIL`が発生し、
詳細分析の結果、他の4版との比較から見て記事固有の誤りというより
Fact Checker側の判定ゆれの可能性が高いと判断した(K節)。**

- 5版すべてSTRUCTURE_PASS(H3見出しちょうど2つ、技術的再試行0回)
- Fact Checker: `PASS` 4件、`FAIL` 1件(B1 V2)、`REVIEW_REQUIRED` 0件
- Ledger Deviation: 5版すべて`LEDGER_COMPLIANT`(逸脱0件)
- Point One/Two: 5版すべて目標30〜60語の範囲内(45〜55語)
- 総語数: 277〜348語。A2改2(277語)のみsoft range(280〜420語)を
  わずかに下回るが、不自然な削除によるものではない(J節)
- **前回問題だったPoint情報の本文前倒しは、5版すべてで発生しなかった**
  (完全記事構成にしたことで解消)
- Cross-level(B2→B1→A2 Original): `SOMEWHAT CLEAR`
- A2 Calibration(Original→改1→改2): 改1・改2とも明確にOriginalより
  認知負荷が下がったが、改1と改2のどちらがより易しいかはデータからは
  明確に判定できない

勝者の最終決定はユーザーに委ねる。

## B. English Master(参照専用)

ER-003-CEFR-DIRECT-01で生成した本文のみの固定版(198語)をそのまま
参照表示した。今回は再生成せず、5版いずれのwriter入力にも使用して
いない(Variation 2はDirect Generation方式のため)。全文は比較
Artifact(L節)参照。

## C. B2 V2

**語数**: 総348語(Main Story 216 / Point One 52 / Point Two 49 /
In One Line 31)

期待通り、English Masterに近い自然な成人英語になった。"there are two
clocks at work"(比喩)、"a crystal ball"(慣用表現)等、抽象度・
慣用表現をある程度残しつつ、過剰な簡略化はしていない。

**Fact Checker**: `PASS`(矛盾0件、Web検索12回)。**Ledger Deviation**:
`LEDGER_COMPLIANT`。全文は比較Artifact参照。

## D. B1 V2

**語数**: 総326語(Main Story 197 / Point One 55 / Point Two 47 /
In One Line 27)

B2より明確に理解負荷が低く、比喩・慣用表現を抑えて直接的な説明を
優先している。話の展開も明示的(However/In simple terms等の接続表現)。

**Fact Checker**: `FAIL`(K節で詳述)。**Ledger Deviation**:
`LEDGER_COMPLIANT`。全文は比較Artifact参照。

## E. A2 V2 Original

**語数**: 総337語(Main Story 197 / Point One 55 / Point Two 55 /
In One Line 30)

前回(CEFR-DIRECT-01)と同一指示。B1よりさらに直接的・具体的な表現に
なった("The plan also does not say that every social media app must
become impossible to open at night."のような明示的な打ち消し)。

**Fact Checker**: `PASS`(矛盾0件、Web検索6回)。**Ledger Deviation**:
`LEDGER_COMPLIANT`。全文は比較Artifact参照。

## F. A2 V2 改1(Cognitive Load Reduction)

**語数**: 総342語(Main Story 221 / Point One 53 / Point Two 45 /
In One Line 23)。5版中もっとも文数が多く(33文)、平均文長がもっとも
短い(10.5語/文)。

Originalの"Autoplay—the feature that starts the next video by
itself—would be off by default."のような、ダッシュで挿入句を埋め込む
1文を、改1では"Autoplay would be off by default. This feature
normally starts the next video by itself."という2つの短文へ分解して
いる。これは狙い通り「1つの文・意味ブロックに複数の考えを詰め込まない」
という原則が具体的に働いた例である。

**Fact Checker**: `PASS`(矛盾0件、Web検索5回)。**Ledger Deviation**:
`LEDGER_COMPLIANT`。全文は比較Artifact参照。

## G. A2 V2 改2(Conceptual Rebuilding)

**語数**: 総277語(Main Story 157 / Point One 49 / Point Two 46 /
In One Line 25)。5版中もっとも短く、Main Storyも5版中最短(157語)。

「簡単な単語で難しい内容を言う記事にしない」という狙い通り、
説明の組み立て自体を圧縮している(例: "Autoplay will be off, so
videos will not start by themselves."と、cause-and-result接続詞
"so"を使って1文で完結させている)。一方、autoplay/personalised
feedsが「夜間だけでなく終日適用される」という対比説明が、Original・
改1に比べてやや弱い("There will also be protection during the
day."のみで、"not only at night"のような明示的対比がない)。これは
明確な事実誤りではないが、情報の圧縮によって対比の解像度がわずかに
下がった例として記録する。

**Fact Checker**: `PASS`(矛盾0件、Web検索8回)。**Ledger Deviation**:
`LEDGER_COMPLIANT`。全文は比較Artifact参照。

## H. Cross-level Difficulty(B2 → B1 → A2 Original)

| Variation | 評価 |
|---|---|
| B2 V2 → B1 V2 | SOMEWHAT CLEAR |
| B1 V2 → A2 V2 Original | SOMEWHAT CLEAR〜CLEAR |
| **Overall** | **SOMEWHAT CLEAR** |

10観点QAの詳細は比較Artifact参照。B2→B1は語彙・抽象度の差は実在する
ものの、文構造の骨格(短い宣言文の積み重ね)自体は近く、劇的な差では
ない。B1→A2 Originalは、具体性・直接性(打ち消し表現の明示化等)の
差が比較的明確だが、総語数はB1(326語)よりA2 Original(337語)の方が
やや多く、「レベルが下がるほど短くなる」という単純な傾向にはなって
いない(これは今回の仕様(6・7節)が明示的に許容している挙動であり、
問題ではない)。

前回(CEFR-DIRECT-01、本文のみ)のV2結果もSOMEWHAT CLEARだったが、
今回は前回発生していたスコープ逸脱(Point情報の本文前倒し)による
比較の混線が解消されており、より純粋な形でのSOMEWHAT CLEAR評価と
言える。

## I. A2 Calibration(Original → 改1 → 改2)

| 評価観点 | 改1(Cognitive Load Reduction) | 改2(Conceptual Rebuilding) |
|---|---|---|
| 難易度は下がったか | 下がった。1文1情報化が明確 | 下がった。概念の提示自体を圧縮 |
| 自然さを失ったか | 失っていない("Ping."等でむしろ物語性維持) | ほぼ失っていない、やや機能的 |
| Adult-news feelを失ったか | 失っていない | 3版中もっとも平易だが教材調ではない |
| 情報を削りすぎたか | 削りすぎていない | 軽微な圧縮あり(G節、終日適用の対比説明がやや弱い) |
| Listening easeは改善したか | 改善(平均文長13.0→10.5語) | 改善(平均文長13.0→10.7語) |

**仮説「A2 Original > 改1 > 改2」は部分的に支持される**: 改1・改2とも
明確にOriginalより認知負荷が下がった。ただし改1と改2のどちらがより
易しいかは、平均文長がほぼ同一(10.5語 vs 10.7語)であり、機械的な
指標からは判定できない。人間の読み比べでは、改1は「同じ内容をより
多くの短い文に分解する」方式、改2は「内容の提示自体をより少ない語数へ
圧縮する」方式という、異なるアプローチで負荷を下げていることが分かる。

いずれも「子供向け英語」「教材調」「不自然に幼い英語」への劣化は
見られなかった。改2はもっとも平易だが、結びの比喩("not a locked
door")を保つなど、成人向けニュースとしての体裁は維持している。

## J. Point / Length Analysis

| Version | Main Story | Point One | Point Two | In One Line | Total | Sentences | Avg len | Max len |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B2 V2 | 216 | 52 | 49 | 31 | 348 | 25 | 14.2 | 31 |
| B1 V2 | 197 | 55 | 47 | 27 | 326 | 25 | 13.2 | 26 |
| A2 Original | 197 | 55 | 55 | 30 | 337 | 26 | 13.0 | 48* |
| A2 改1 | 221 | 53 | 45 | 23 | 342 | 33 | 10.5 | 18 |
| A2 改2 | 157 | 49 | 46 | 25 | 277 | 26 | 10.7 | 25 |

**全版でPoint One・Point Twoは目標30〜60語の範囲内**(45〜55語)に
収まった。範囲外事項は発生しなかった。

**総語数の範囲外事項**: A2改2の総語数277語のみ、observation用soft
range(280〜420語)をわずか3語下回った。これはMain Story(157語、
5版中最短)の圧縮によるもので、Point/In One Lineは他版と遜色ない
分量を維持している。語数合わせのための不自然な追加は行っていない。

**metricsの制約に関する注記**: A2 Originalのmax_sentence_length=48は
実際の最長文ではない。参考metricsの文分割ロジック(正規表現ベース)が、
太字強調(`**...**`)の直前で文境界を検出できず、"...others moved to
television or games."と直後の"**The UK is not planning to lock...**"
を1つの文として誤って結合したことによる計測上のアーティファクトである。
実際の記事は正常な文長で構成されており、内容上の問題ではない(全版で
`**`強調を使用しているため、他版のmax_sentence_lengthにも同種の
誤差が含まれている可能性がある。metricsは仕様通り参考値としてのみ
扱い、難易度判定には使用していない)。

## K. Fact Safety

| Version | Fact Check | Ledger Deviation | 技術的再試行 |
|---|---|---|---|
| B2 V2 | `PASS` | `LEDGER_COMPLIANT` | 0 |
| B1 V2 | `FAIL` | `LEDGER_COMPLIANT` | 0 |
| A2 Original | `PASS` | `LEDGER_COMPLIANT` | 0 |
| A2 改1 | `PASS` | `LEDGER_COMPLIANT` | 0 |
| A2 改2 | `PASS` | `LEDGER_COMPLIANT` | 0 |

### K-1. B1 V2のFAILについて(詳細分析)

**指摘内容**: B1 V2の結び("The UK is not planning to lock social
media away at night. It is planning to make quiet, less
attention-grabbing settings the starting point...")が、夜間措置を
通知の消音中心に描いており、政府案には対象アプリへのデフォルトの
アクセス制限も含まれる可能性がある、という点を十分に伝えていない、
との判定だった。

**5版の記述を横並びで確認した結果**: B2 V2("the screen would not be
seized, and social media apps would not necessarily disappear")、
A2 Original("does not say that every social media app must become
impossible to open at night"、結び"not planning to lock older teens
out of social media after midnight")、A2改1(結び"not a hard
night-time ban")、A2改2(結び"not a locked door")は、**いずれも
B1 V2とほぼ同種の打ち消し表現**(「完全な締め出しではない」)を使って
いる。これらはすべて`PASS`と判定された。

**評価**: Verified Fact Ledgerの該当項目(POL-03)は、そもそも
「通知停止だけが夜間制度の全内容だとも、通知停止に加えて必ず完全
アクセス遮断が行われるとも断定しない」と、この点を意図的に未確定
としている。したがって、この論点自体が一次資料の記述の曖昧さに
起因する構造的なグレーゾーンであり、5版中この1版だけがFAILになった
のは、記事固有の重大な誤りというより、**独立Fact Checker呼び出し
ごとのWeb検索結果のばらつき**(この回だけ、より断定的にアクセス制限を
報じるSource(BMJ/ITV等)を強く参照した)による判定ゆれである可能性が
高いと判断する。

ただし、これは「B1 V2の記述が完全に問題ない」という意味ではない。
5版の中でB1 V2の結びは、他版よりもやや強い断定("The UK is not
planning to lock social media away at night")になっており、この
表現がFact Checkerの慎重な判定を誘発しやすかった可能性はある。

**今回の対応**: 成功条件5「Fact Checkerで重大なFAILなし」は、この
1件により厳密には満たしていない。再生成によるFAIL解消(実質的な
best-of)は行わず、`FAIL`のまま記録し、原因分析を添えて報告する
という今回のルールに従った。

## L. Comparison Artifact

English Master(参照)・B2 V2・B1 V2・A2 V2(Original/改1/改2、
近接配置)の全文(先頭配置)、Cross-level QA、A2 Calibration QA、
Point/Length Analysis、Fact Safetyをまとめた。

**URL**: https://claude.ai/code/artifact/d434da81-1e64-4d74-b1f1-b20d5e405c25

リポジトリ内の原本: `er003_output/cefr_direct_02/comparison.html`

## M. Production非変更確認

- **CURRENT_SPEC.md・R4 Production prompt・VFL/spoken_first/
  cefr_direct_01関連スクリプト**: 無変更。新規の独立ファイル
  (`er003_v1_cefr_direct_02_generate.py`)から、これらの関数を
  読み取り専用でimportした
- **Variation 1・Variation 3の再検証**: 実施していない
- **既存CEFR仕様**: 廃止・変更していない
- **Key Phrase生成・TTS/audio・WPM検証**: 実施していない
- **OPEN-35**: 変更・CLOSEしていない
- **新規Topic E2E**: 実施していない(既存A02のTopic・Ledgerのみ使用)

## N. 次のDecision

ユーザー評価を受けて、以下を整理する。

1. B2 V2の採否
2. B1 V2の採否(K節のFAIL分析を踏まえた判断が必要)
3. A2 Original / 改1 / 改2からの候補選定(I節参照。改1・改2のどちらが
   優れるかは人間の読み比べによる判断が必要)
4. 必要なら選んだA2指示の微修正
5. 他記事(A01・ADD03)でのN増し
6. その後CEFR Direct方式のProduction候補化

**今回の結果を踏まえた所見**: 完全記事構成にしたことで、前回
(CEFR-DIRECT-01)の本文スコープ逸脱問題は解消され、Point Balance
原則(30〜60語目標)も5版すべてで達成された。CEFR難易度差は
SOMEWHAT CLEARにとどまり、CLEARと呼べるほど劇的ではないが、
B1→A2 Originalの具体性・直接性の差は比較的明確だった。A2の3版
比較では、改1・改2のどちらも認知負荷低減に成功しており、優劣は
今回のデータだけでは決めがたい。B1 V2のFAILは、記事固有の欠陥という
より一次資料自体の曖昧さとFact Checker呼び出しごとのばらつきに
起因する可能性が高いと分析したが、最終判断はユーザーに委ねる。

## 対象ファイル・新規Artifact一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_cefr_direct_02_generate.py`(新規) | B2/B1/A2(3版)の完全記事生成パイプライン。VFL-01・en_direct_ab_01・spoken_first_01_r1のProduction関数を読み取り専用でimport |
| `er003_output/cefr_direct_02/A02/{B2_v2,B1_v2,A2_original,A2_kai1,A2_kai2}/`(新規) | 各版のarticle.md・metrics.json・length_report.json・fact_qa.json・ledger_deviation.json・audit記録 |
| `er003_output/cefr_direct_02/A02/run_summary.json`(新規) | 実行要約 |
| `er003_output/cefr_direct_02/comparison.html`(新規) | 比較Artifact原本 |

## 受入条件(Git操作報告)

Git操作を行った場合のcommit/push状態は、本報告の送付メッセージ末尾を参照。
