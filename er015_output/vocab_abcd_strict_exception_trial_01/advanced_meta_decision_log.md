# advanced_meta_decision_log.md

凡例: surface=表層形のtop20000内順位, lemma=採用されたlemma候補(word:順位、未使用または表外は(none)), rank=min(surface,lemma)としてモデルへ渡した値, level=standard/advanced, 旧判定=前回Trial(閾値のみ異なる同一素材)での判定, 新判定=本Trial(厳格定義)での判定, KEEP/SIMPLIFY=新判定の粗い分類, 理由=モデルの判定理由, 置換案=replacement_if_simplify, 意味差・Fact差=meaning_or_fact_change。

### advanced_meta Decision Log (strict)

旧判定の出典: ADVANCED-VOCAB-RULE-TRIAL-01 v2 (閾値12,000版)

| surface | lemma | rank | level | 旧判定 | 新判定 | KEEP/SIMPLIFY | 理由 | 置換案 | 意味差・Fact差 |
|---|---|---|---|---|---|---|---|---|---|
| (none in top20000) | (none) | > 20,000 (zipf=1.70, extremely rare) | advanced | KEEP -- proper noun | KEEP-C | KEEP | The phrase “human concierges” is a specific quoted designation that the article reports Meta used for these workers, so strict condition C is met. It is not being kept merely because it is quoted or because it is a general term. | N/A | none |
| 15,670 | (none) | 15,670 | advanced | KEEP -- predictable morphology/compound | KEEP-A | KEEP | “Onstage” is a predictable compound of the already-easy words “on” and “stage,” and a learner can naturally guess that it means “on the stage.” This is a structural A exception, not an appeal to a fixed expression or stylistic preference. | N/A | none |

### notes_on_ambiguous_cases

No genuinely ambiguous cases. “Human concierges” qualifies narrowly as Meta’s reported specific designation, while “onstage” is a transparent compound of easy words.
