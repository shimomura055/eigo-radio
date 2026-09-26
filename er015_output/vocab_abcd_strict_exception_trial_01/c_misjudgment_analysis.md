# c_misjudgment_analysis.md

## 前回誤判定の事実

STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01(v2閾値6,000版)のSewer Decision Logより、`septic`(記事内では「combined septic tank」という一般名詞句の一部としてのみ登場、固有名詞・公式名称ではない)が"KEEP -- proper noun"(C)と判定された。該当行を逐語引用する:

```
| septic | (none in top20000) | (none) | > 20,000 (zipf=3.21, extremely rare) | KEEP -- proper noun | “Septic” appears inside the quoted designation “combined septic tank,” which the article reports as wording used by a news report and must keep exactly. The same technical term is retained consistently in the surrounding article. | When a news report says “combined septic tank,” you may wonder. | When a news report says “combined septic tank,” you may wonder. |
```

モデル自身の理由付け(逐語): "‘Septic’ appears inside the quoted designation ‘combined septic tank,’ which the article reports as wording used by a news report and must keep exactly."

## 構造上の原因

原因は当時のRULE_BLOCK_EN_V2(ADVANCED-VOCAB-RULE-TRIAL-01 v2でFable差し戻し修正Bとして追加、STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01がそのまま流用)のC(固有名詞)節に、Meta記事の "human concierges"(Metaが実際にそう呼んだ、という記事内のFactそのもの)を守るために追加された、以下の一文にある(逐語引用):

```
Words that appear inside quotation marks in the article, and titles, designations, or nicknames that a specific person or organization is reported to have actually used (for example, if the article states that Meta called certain workers "human concierges", the word "concierges" here is part of that reported fact, not an ordinary vocabulary choice) are facts of the article. Do not simplify such a word even if it appears in the candidate list below; treat it under exception C (a proper noun / quoted designation) and mark it "KEEP -- proper noun", explaining in reasoning that it is a quoted designation that must be kept exactly as reported.
```

この一文は「Metaのような特定の人物・組織が実際に使った呼称」を想定していたが、文言上は **"Words that appear inside quotation marks in the article"** という条件が、後半の「特定の人物・組織が実際に使った呼称」という条件から独立した、単独で十分な条件として読める構造になっていた。結果として、モデルは「記事内で引用符に入っている語 = C(固有名詞/固有の引用名称)として保護してよい」と解釈できてしまい、Sewer記事のWriterが読者への導入表現として引用符を使っただけの一般名詞句 "combined septic tank" にまでこの保護を適用した。これは:

- 固有名詞と「単なる引用」の区別が定義上なされていなかった
- Fact不変の一般原則(記事の事実を変えない)と、C(固有名詞)という個別の例外カテゴリとの境界が曖昧だった(引用符内の語なら何でもFactとして固定してよい、という拡大解釈を許した)
という2点に起因する。

## 本Trialでの是正

本TrialのRULE_BLOCK_EN_STRICTでは、C定義を「本当の固有名詞・公式名称・固有の引用名称だけ」に限定し、「一般名詞が引用符に入っているだけ」「一般的な技術用語」「記事中で引用されているだけ」「Writerが強調のため引用符を付けただけ」を明示的な否定条件として追加した(個別語名"septic"はPromptに書かず、定義文のみで正しい判定へ導けるかを検証する)。実際の再判定結果はstandard_sewer_decision_log.md / advanced_sewer_decision_log.md のsepticの行、および本REPORT §7を参照。
