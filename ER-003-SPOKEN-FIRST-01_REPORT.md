# ER-003-SPOKEN-FIRST-01 実行報告(ADD03 Listening-first小規模検証)

**管理ID: ER-003-SPOKEN-FIRST-01**
**実施日: 2026-08-13**
**ステータス: `PROTOTYPE / EXPERIMENT`(ADD03限定の実験系。Production仕様は変更していない。A01/A02への展開はユーザー判断待ち)**

## A. Executive Summary

**Listening-first化は成功したと判断できる。** ER-003-EN-DIRECT-VFL-02で
Fact Check PASSとなったADD03のVersion V(既存VFL記事)を、新規Web
researchなしに既存のVerified Fact Ledgerだけを事実源としてVersion L
(Listening-first版)へ書き換えた。

- Version Lの独立Fact Checker: **`PASS`**(矛盾・未確認主張ともに0件)
- Ledger Deviation Check: **`LEDGER_COMPLIANT`**(逸脱0件)
- 数字の実質的な密度: Version Vの15個の異なる数値表現→Version Lは
  約8個(ANCHOR3件+SUPPORTING5件程度)まで整理。近接する重複数値
  (例: $7.29と9.59%、$1.43と1.7%)を1つに統合し、時刻(10:16 a.m./
  11:04 a.m.)・IMO会合番号(137th)・近似値の重複($32M)を省略
- 20%提案・7/13→7/14の時系列・scenarioと実際の料金の区別は
  すべて維持
- word countはVersion V(418語)からVersion L(472語)へ**増加**した。
  これは数字を削った分、説明的な言い換え("It did not identify who
  would collect the money or who would pay."等)が増えたためであり、
  「数字密度の低下」と「語数の増減」は別軸であることが今回確認できた
  (H節で扱う)

## B. Before / After

比較Artifact(E節)に全文を掲載。要点のみ:

**Version V(冒頭)**: "Brent crude ended July 13 at $83.30 a barrel, up
$7.29, or 9.59%."(1文に3つの数値)

**Version L(該当箇所)**: "On July 13, Brent crude settled at about 83
dollars a barrel, up nearly 10 percent."(1文に2つの丸めた数値)

**Version V**: "Brent climbed as much as 4.6% to an intraday high of
$87.08 on July 14 before reports of the withdrawal helped narrow its
gains. But oil did not finish the day lower. Brent closed at $84.73,
still up 1.7% from the previous session."(intraday高値・下落・終値・
上昇率の4つの数値情報が3文に凝縮)

**Version L**: "Brent soon returned close to its earlier elevated
level. It settled at about 85 dollars a barrel, finishing the day
higher as concerns about the blockade, attacks, and tanker safety
continued."(intraday高値の具体的数値は省き、「高い水準へ戻った」
という方向性のみ提示。終値は丸めて1回だけ)

## C. Number Treatment

主要数字18件の分類・変換結果(全件は比較Artifactの表を参照)。

| Original | Classification | Exactness | Listening-first treatment | Reason |
|---|---|---|---|---|
| 20% | ANCHOR | EXACT_REQUIRED | "20 percent"のまま維持 | 提案と撤回を結ぶ中心的数字 |
| July 13 / July 14 | ANCHOR | EXACT_REQUIRED | 日付のまま維持 | 時系列を確定する基準 |
| 10:16 a.m. EDT / 11:04 a.m. EDT | DISPENSABLE | APPROXIMATE_OK | 時刻を省略、日付のみ残す | 分単位の精度は記事理解に不要 |
| 24 hours 48 minutes | SUPPORTING | APPROXIMATE_OK | "just over a day later" | 撤回の速さは重要だが分単位は不要 |
| $34 million | SUPPORTING | APPROXIMATE_OK | "about 34 million dollars"、仮説と明示 | 20%案の規模を示す主要な具体例 |
| near $32 million | DISPENSABLE | APPROXIMATE_OK | 省略 | $34Mとほぼ同じ情報、近接する2つの金額は聞き取りにくい |
| $83.30 / up $7.29 / 9.59% | SUPPORTING+DISPENSABLE | APPROXIMATE_OK | "about 83 dollars...up nearly 10 percent"(ドル差分は省略、%は丸め) | 3数値の重複を解消 |
| $84.73 / up $1.43 / 1.7% | SUPPORTING+DISPENSABLE | APPROXIMATE_OK/DIRECTION_ONLY | "about 85 dollars...finishing the day higher"(%も方向のみに) | 同上 |
| 137th session | DISPENSABLE | EXACT_REQUIRED | 省略 | 識別番号であり、聞き手には不要な情報 |

## D. Fact Safety

- **独立Fact Checker**: `PASS`(Web検索14回、矛盾・未確認主張ともに0件)。
  丸めた数値("about 83 dollars"="nearly 10 percent"等)がすべて元の
  正確な値の妥当な丸めであることも確認済み
- **Ledger Deviation Check**: `LEDGER_COMPLIANT`(逸脱0件)。Verified
  Fact Ledger外の新規Factは追加されていない
- **技術的再試行**: Rewrite呼び出しは1回で構造(###見出し2つ)に合格、
  再試行なし

## E. Listening QA

比較Artifactに9観点の全比較を掲載。要点:

1. **Listening ease**: Version Vは近接する重複数値(ドル差分と%等)を
   同時に処理する必要があったが、Version Lは各情報が1回ずつ提示される
2. **Number density**: 15個の異なる数値表現→約8個相当まで整理
3. **Number necessity**: 137th sessionや$32Mのような、精度はあるが
   意味理解に寄与しない数字を削除
4. **Cognitive load**: 「価格・差分・率」の3点セットを2回記憶する
   必要があったVersion Vに対し、Version Lは丸めた価格1つ+方向性の
   組み合わせのみ
5. **Narrative clarity**: 「何が起きた→何が変わった→なぜ重要か」の
   流れは両版とも維持、Version Lの方が数字に気を取られず追いやすい
6. **Editorial engagement**: "The number was clear. The mechanism was
   not."等のフック文はほぼそのまま維持されている
7. **Master-style transfer**: 短い断定文のリズムは維持
8. **Fact accuracy**: 両版ともPASS(D節)
9. **Downstream suitability**: Version Lの方が音声ナレーション用
   Sourceとして数字面の負荷が軽い

## F. 比較Artifact

Version V・Version Lの全文(先頭から読める配置)、数字変換表、Fact QA・
Ledger deviation結果、9観点QAをまとめた。

**URL**: https://claude.ai/code/artifact/e9b855d6-c8dc-43e8-ac35-6b299b0108c6

リポジトリ内の原本: `er003_output/spoken_first_01/ADD03/comparison.html`

## G. Production非変更確認

- **CURRENT_SPEC.md**: 無変更
- **R4 Production prompt・VFL関連スクリプト**: 無変更。今回のスクリプトも
  新規の独立ファイル(`er003_v1_spoken_first_01_generate.py`)であり、
  VFL-01・R4の関数を読み取り専用でimportして使用した
- **A01・A02**: 変更していない(今回の対象はADD03のみ)
- **B1/A2/B2生成・TTS・audio assemble**: 実施していない
- **OPEN-35**: 変更・CLOSEしていない

## H. 次のDecision

以下から提案する。

1. **成功**: A01・A02へListening-first方式を展開しN増し確認
2. **一部改善必要**: ADD03でルール調整後、再試験
3. **不採用**: VFL記事(Version V)をそのままNatural English Source候補として維持

成功条件10項目(受入条件11節)との対応:

| # | 条件 | 結果 |
|---|---|---|
| 1 | Version LのFact CheckerがFAILではない | PASS(`PASS`判定) |
| 2 | Ledger deviationがない | PASS(0件) |
| 3 | 7/13→7/14の時系列を維持 | PASS |
| 4 | 20% proposalの意味を維持 | PASS |
| 5 | scenarioとactual chargeを混同していない | PASS("hypothetical calculation. It was not an actual charge."を維持) |
| 6 | oil price変動の方向を正しく維持 | PASS |
| 7 | 数字密度がVersion Vより明確に低下 | PASS(15→約8) |
| 8 | Listening easeが改善 | PASS(E節) |
| 9 | Editorial engagementを大きく失わない | PASS(E節) |
| 10 | ユーザーが「聞く前提として改善」と評価できるか | **ユーザー判断待ち** |

技術的な成功条件1〜9はすべて満たしていると判断する。10番目(主観評価)は
比較Artifactを実際にお読みいただいた上でのご判断をお願いしたい。

**提案**: 条件1〜9の結果を踏まえると、選択肢1(A01・A02への展開)を
推奨する材料は揃っていると考えるが、word countがVersion Vより増加した点
(数字を削った分、説明的な言い換えが増えたため)がListening-first化の
意図と完全に一致するかは、実際に音声化した際の尺(WPM換算)で改めて
確認する価値がある。最終判断はユーザーに委ねる。

## 対象ファイル・新規Artifact一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_spoken_first_01_generate.py`(新規) | Number Classification→Rewrite→Fact Checker→Ledger Deviation Checkのパイプライン。VFL-01・R4のProduction関数を読み取り専用でimport |
| `er003_output/spoken_first_01/ADD03/number_classification.json`(新規) | 18件の数字分類結果(ANCHOR/SUPPORTING/DISPENSABLE、Exactness、treatment、理由) |
| `er003_output/spoken_first_01/ADD03/version_l.md`(新規) | Listening-first rewrite本文 |
| `er003_output/spoken_first_01/ADD03/fact_qa.json`(新規) | Version Lの独立Fact Checker結果 |
| `er003_output/spoken_first_01/ADD03/ledger_deviation.json`(新規) | Ledger Deviation Check結果 |
| `er003_output/spoken_first_01/ADD03/run_summary.json`(新規) | 実行要約 |
| `er003_output/spoken_first_01/ADD03/comparison.html`(新規) | 比較Artifact原本 |
| `er003_output/spoken_first_01/ADD03/audit/`(新規) | 各API呼び出しのprompt全文・応答詳細等の監査証跡 |

## 受入条件20項目

| # | 条件 | 結果 |
|---|---|---|
| 1 | ADD03のみを対象にしている | PASS |
| 2 | 既存VFL記事をBaseにしている | PASS |
| 3 | 新しいWeb Researchから記事を作り直していない | PASS(Rewriteはweb検索なし) |
| 4 | 数字をANCHOR/SUPPORTING/DISPENSABLEへ分類している | PASS(C節、18件) |
| 5 | ExactnessをEXACT_REQUIRED/APPROXIMATE_OK/DIRECTION_ONLYへ分類している | PASS(C節) |
| 6 | 数字を削減・丸め・方向化する判断理由を保存している | PASS(number_classification.json) |
| 7 | 20% proposalの意味を維持している | PASS |
| 8 | scenarioとactual feeを混同していない | PASS |
| 9 | 7/13→7/14時系列を維持している | PASS |
| 10 | Ledger外Factを追加していない | PASS(deviation 0件) |
| 11 | Listening-first版を独立Fact Checkしている | PASS(D節) |
| 12 | Ledger Deviation Checkを実施している | PASS(D節) |
| 13 | 9観点Listening-first QAを実施している | PASS(E節) |
| 14 | Version V/Version L比較Artifactを作っている | PASS(F節) |
| 15 | Production仕様を変更していない | PASS(G節) |
| 16 | A01/A02を変更していない | PASS(G節) |
| 17 | B1/A2/B2/TTS/audioを生成していない | PASS(G節) |
| 18 | OPEN-35を変更・CLOSEしていない | PASS(G節) |
| 19 | 変更・新規ファイル一覧を報告している | PASS(上表) |
| 20 | Git操作を行った場合はcommit/push状態を報告している | 本報告の末尾を参照 |
