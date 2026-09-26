# advanced_sewer_decision_log.md

凡例: surface=表層形のtop20000内順位, lemma=採用されたlemma候補(word:順位、未使用または表外は(none)), rank=min(surface,lemma)としてモデルへ渡した値, level=standard/advanced, 旧判定=前回Trial(閾値のみ異なる同一素材)での判定, 新判定=本Trial(厳格定義)での判定, KEEP/SIMPLIFY=新判定の粗い分類, 理由=モデルの判定理由, 置換案=replacement_if_simplify, 意味差・Fact差=meaning_or_fact_change。

### advanced_sewer Decision Log (strict)

旧判定の出典: ADVANCED-VOCAB-RULE-TRIAL-01 v2 (閾値12,000版)

| surface | lemma | rank | level | 旧判定 | 新判定 | KEEP/SIMPLIFY | 理由 | 置換案 | 意味差・Fact差 |
|---|---|---|---|---|---|---|---|---|---|
| (none in top20000) | (none) | > 20,000 (zipf=3.21, extremely rare) | advanced | SIMPLIFY | SIMPLIFY | SIMPLIFY | No strict exception applies: “septic” is not a predictable form or compound from an easy word, an established everyday Japanese loanword, or a proper or official designation. Because “household wastewater treatment” is a clear natural descriptive replacement, the technical term is not indispensable under D. | household wastewater treatment | minor |
| 12,006 | (none) | 12,006 | advanced | KEEP -- indispensable / natural replacement unavailable | SIMPLIFY | SIMPLIFY | “Main pipe” is a simpler, natural expression that preserves the fact that the sewer is a major underground pipe. Although “artery” appears in a metaphor, that storytelling use alone does not satisfy the strict D exception. | main pipe | minor |
| 12,324 | (none) | 12,324 | advanced | SIMPLIFY | SIMPLIFY | SIMPLIFY | “Wastewater collection system” is a natural, transparent replacement that preserves the relevant infrastructure meaning. The word is not being kept merely because it is a technical term or central to the article, so D does not apply. | wastewater collection system | none |
| (none in top20000) | sewer:12,324 | 12,324 | advanced | SIMPLIFY | SIMPLIFY | SIMPLIFY | The plural form can naturally be replaced with “wastewater collection systems,” which clearly identifies the systems that carry household wastewater. Its technical meaning and importance to the article do not by themselves satisfy the strict D exception. | wastewater collection systems | none |
| 18,216 | (none) | 18,216 | advanced | KEEP -- predictable morphology/compound | KEEP-A | KEEP | “Wastewater” is a predictable compound of the already-known words “waste” and “water,” and learners can naturally infer its meaning from that structure. It is being kept under A, not because it is a loanword, proper noun, or indispensable technical term. | N/A | none |

### notes_on_ambiguous_cases

“Artery” was close to the threshold, but “main pipe” preserves the factual meaning and the metaphor alone is not a strict D exception. “Septic” and “sewer” are technically precise terms, but the article can use clear descriptive alternatives without losing its central point.
