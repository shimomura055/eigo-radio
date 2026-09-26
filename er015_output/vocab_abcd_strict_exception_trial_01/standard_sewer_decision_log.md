# standard_sewer_decision_log.md

凡例: surface=表層形のtop20000内順位, lemma=採用されたlemma候補(word:順位、未使用または表外は(none)), rank=min(surface,lemma)としてモデルへ渡した値, level=standard/advanced, 旧判定=前回Trial(閾値のみ異なる同一素材)での判定, 新判定=本Trial(厳格定義)での判定, KEEP/SIMPLIFY=新判定の粗い分類, 理由=モデルの判定理由, 置換案=replacement_if_simplify, 意味差・Fact差=meaning_or_fact_change。

### standard_sewer Decision Log (strict)

旧判定の出典: STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01 (閾値6,000版)

| surface | lemma | rank | level | 旧判定 | 新判定 | KEEP/SIMPLIFY | 理由 | 置換案 | 意味差・Fact差 |
|---|---|---|---|---|---|---|---|---|---|
| (none in top20000) | (none) | > 20,000 (zipf=2.99, extremely rare) | standard | KEEP -- predictable morphology/compound | KEEP-A | KEEP | Strict exception A applies: “faraway” is a transparent compound of the already-easy words “far” and “away,” so its meaning is naturally guessable. No specialist knowledge or quoted-term exception is needed. | N/A | none |
| (none in top20000) | (none) | > 20,000 (zipf=3.21, extremely rare) | standard | KEEP -- proper noun | SIMPLIFY | SIMPLIFY | No strict exception applies: “septic” is not predictable enough under A, is not an unambiguous everyday Japanese loanword under B, and the quotation is only a common technical term, not a specific designation under C. Exception D is also unnecessary because “treatment” is a natural simpler alternative that preserves the article’s point. | treatment | minor |
| 6,153 | (none) | 6,153 | standard | KEEP -- predictable morphology/compound | SIMPLIFY | SIMPLIFY | Although the negative prefix is partly transparent, the base “visible” is not clearly an already-easy, already-known base for this strict A exception. “Hidden” is a simpler, natural synonym, and no B, C, or D exception is needed. | hidden | none |
| 9,610 | (none) | 9,610 | standard | KEEP -- indispensable / natural replacement unavailable | SIMPLIFY | SIMPLIFY | The verb does not have an unambiguous everyday Japanese loanword connection under strict B, and the toilet action is not indispensable under D. “Use the toilet” is a natural simpler expression that preserves the relevant meaning here. | use the toilet | minor |
| 12,006 | (none) | 12,006 | standard | KEEP -- indispensable / natural replacement unavailable | SIMPLIFY | SIMPLIFY | The metaphor alone does not qualify for D: “main pipe” naturally conveys the needed infrastructure meaning without losing a fact the reader needs. No A, B, or C exception applies. | main pipe | minor |
| 12,324 | (none) | 12,324 | standard | KEEP -- indispensable / natural replacement unavailable | SIMPLIFY | SIMPLIFY | “Sewer” is not an unambiguous everyday Japanese loanword under B, and D does not apply because “underground pipe system” is a natural simpler description that remains accurate in this context. Its technical specificity is not necessary for understanding the article’s point. | underground pipe system | minor |
| (none in top20000) | sewer:12,324 | 12,324 | standard | KEEP -- indispensable / natural replacement unavailable | SIMPLIFY | SIMPLIFY | The plural form has no strict A, B, or C exception, and D is not needed because “underground pipe systems” is a natural, meaning-preserving alternative in the surrounding context. The word is not being kept merely because it is a technical term. | underground pipe systems | minor |
| 18,216 | (none) | 18,216 | standard | KEEP -- predictable morphology/compound | KEEP-A | KEEP | Strict exception A explicitly applies: “wastewater” is a predictable compound of the already-easy words “waste” and “water,” and its meaning can be naturally guessed from that structure. It does not rely on a specialist loanword or quoted-term exception. | N/A | none |

### notes_on_ambiguous_cases

The closest calls were “invisible” and “septic.” I treated “invisible” as too dependent on the less-basic base “visible” for strict A, while “septic” was simplified because the article can explain the system with the natural phrase “treatment tank” without needing the technical term.
