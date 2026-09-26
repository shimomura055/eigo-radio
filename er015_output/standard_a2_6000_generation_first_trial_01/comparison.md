# comparison.md

STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01。総合客観比較(Meta/Sewer)。
採否推奨は書かない。

## 客観指標サマリー

| 記事 | 版 | 語数 | 文数 | 平均文長 | FK概算 | 段落数 | 6,000超残存語数 | fact_tokens match(vs Advanced) |
|---|---|---|---|---|---|---|---|---|
| Meta | Advanced | 329 | 23 | 14.3 | 7.53 | 13 | 9 | - |
| Meta | A(Control v5) | 290 | 32 | 9.06 | 5.77 | 13 | 10 | False(見かけ上。目視で実質none、下記参照) |
| Meta | B(Gen-First) | 321 | 30 | 10.7 | 5.79 | 14 | 10 | False(同上) |
| Sewer | Advanced | 328 | 23 | 14.26 | 7.6 | 10 | 9 | - |
| Sewer | A(Control v5) | 322 | 28 | 11.5 | 6.3 | 10 | 10 | **True** |
| Sewer | B(Gen-First) | 324 | 26 | 12.46 | 6.31 | 10 | 9 | **True** |

Meta のfact_tokens_check(数字・引用符・大文字語)が機械的にFalseと出るのは、
"Reuters"等が文再構成で文頭(sentence-initial)位置に移動し、既存の
「文中非先頭の大文字語のみを固有名詞候補としてカウントする」ヒューリス
ティックが検出できなくなったためであり、目視確認の結果、実際の固有名詞
・数字・引用句はすべて保持されていた(意味/Fact上のMajor差分は0件、詳細は
meta/analysis.md参照)。

## 6,000超残存語数だけを見た印象と、その限界

Meta: A=10, B=10(同数)。Sewer: A=10, B=9(Bが1語少ない)。この差は
Sewerで唯一"inspect"(A)が"check"(B)へ自然に言い換えられたことによる。
ただし全体として、Meta/Sewerとも「不要な難語」(固有名詞でも主題語でも
Metaphorでもない語)は元々ほとんど存在せず、Advanced自体の残存語数
(9,9)とA/Bの残存語数(10,10 / 10,9)の差は僅少だった。これは
**本Trialの入力2記事が、いずれも現行Advanced v2 Production Prompt
(語彙ルールv2込み)によって既に相当程度平易化された状態だったため**で
あり(下記「入力の由来」参照)、6,000語Generation-Firstの効果を強く
判別する材料としては、この2記事だけでは限界がある(残存語数という単一
指標だけでは、AとBの効果差はほぼ観測できなかった)。

## 意味・Fact保持の客観的な最重要所見

前回Trial(VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01)で問題になった
`septic->treatment`、`flush->use`、`sewer->underground pipe system`と
いった**意味を変える事後置換は、本TrialのA(現行Control v5)・B
(Gen-First)のどちらの方式でも一切発生しなかった**。Sewer記事の
fact_tokens_check(数字・引用符内フレーズ・固有名詞候補)はA/Bとも
Advancedと完全一致(True)。この点はA/B共通の観測であり、B固有の効果
ではない(現行Standard v5 Prompt自体が既に"Do not force a replacement
if it makes the sentence less natural or changes the meaning."という
歯止めを持っており、今回のような自然な記事に対しては機能していた)。

## English quality / Storytelling の差(具体例、目視)

- Meta P9: Aは"...onstage. And who is behind the curtain."と2文へ機械的
  分割し、"And"始まりの短い文断片がやや不自然。Bは原文のダッシュ構造を
  保持し1文のまま、より自然だった(1箇所のみの差)。
- Meta P3: Bは"behind the stage"を"behind the scenes"へ変更(誤りでは
  ないが、記事内のstage比喩ファミリーからわずかに逸脱)。
- Sewer P5: Bは"installed"を"put in"(平易な句動詞)へ自然に言い換え、
  Gen-First方式が意図した「最初から簡単な表現で書く」効果の分かりやすい
  例になった。
- Sewer P6: Bは逆接"Still,"を省略しており、直前段落との対比のニュアンス
  がA/Advancedよりわずかに弱い(Fact変化ではなく結束性の軽微な変化)。
- 段落数: Meta のみBで13->14(1段落を2分割、内容欠落なし)。Sewerは
  Advanced/A/Bとも10段落で完全一致。
- Storyline・中心比喩(Meta: 舞台裏/ピアノ、Sewer: 見えない大動脈/
  洗濯機)は、A/Bとも維持されていた。要約化・Detail削除の兆候は両記事・
  両方式とも観測されなかった。

## 入力の由来(重要、委任文からの逸脱点の記録)

委任文が提示した入力候補(`er015_output/vocab_abcd_strict_exception_
trial_01/advanced_meta_before.md` / `advanced_sewer_before.md`)は、
事前調査の結果、以下が判明したため**本Trialでは使用せず**、日本語R2原文
から現行Advanced v2 Production Prompt(`er003_v1_n3_01_advanced_
adaptation_generate.generate_advanced_adaptation`、Production module
無変更・読み取り専用import)を直接呼び出して両記事を新規に再生成した:

1. Sewer側の実体(`er015_output/news_natural_advanced_standard_a2_
   trial_01/a1_advanced_sewer.md`)は、Advanced v2 Production Prompt
   ではなく、その前身のTrial(NEWS-JA-TO-EN-ADAPTATION-TRIAL-01 arm3
   "Natural English"、Sewer固有のpreserve bullet文言)で生成されたもの
   だった(`prompt_advanced_a1.txt`で文言差を確認)。
2. Meta側の実体(`er012_output/e_family_two_level_wiring_01/meta/b1b/
   article.md`)はer012ランナー経由でAdvanced v2 Production関数を直接
   呼び出して生成された点は正しかったが、生成コミット(0e028301、
   2026-09-25)が語彙ルールv2をProductionへ組み込んだコミット
   (7c93d146、ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01)より前であり、
   **現行(語彙ルールv2込み)のAdvanced v2 Production Promptの出力では
   なかった**。

上記により、Meta/Sewerとも現行Advanced v2 Production Promptの出力として
整合性を持たせるため、両記事を同日・同モジュールで新規再生成した(日本語
原文・Fact変更なし、Production module変更なし)。日本語R2原文:
- Meta:  `docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/
  ai_phone_revision2.md`(sha256[text-mode LF正規化]=
  a5d77646cf162974ab53e196da6ba8bc29a8e35172294336a9d12ba777c1cb81、
  raw bytes sha256=474c2a1669b6f90f835d3901cbe6b4fd80f556edf440f0c610fb3589767b1a48)
- Sewer: `docs/evidence/news_iterative_r2_adoption_2026-09-24/articles/
  sewer_revision2.md`(sha256[raw bytes]=
  a7fa4fd7dcd02b5570521eff361153eef24885de7ec79edeb518740386040769)
