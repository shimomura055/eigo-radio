# sewer_decision_log.md

凡例: surface=表層形のtop20000内順位, lemma=採用されたlemma候補(word:順位、未使用または表外は(none)), 採用rank=min(surface,lemma)としてモデルへ渡した値, 例外/理由=モデルの判定理由(A/B/C/Dまたは平易化理由)。

### Sewer Decision Log

| Word | surface | lemma | 採用rank | 判定 | 例外/理由 | Before | After |
|---|---|---|---|---|---|---|---|
| faraway | (none in top20000) | (none) | > 20,000 (zipf=2.99, extremely rare) | KEEP -- predictable morphology/compound | The meaning of “faraway” is easily guessed from the familiar words “far” and “away.” | Then it carries the water to a faraway treatment plant. | Then it carries the water to a faraway treatment plant. |
| septic | (none in top20000) | (none) | > 20,000 (zipf=3.21, extremely rare) | KEEP -- proper noun | “Septic” appears inside the quoted designation “combined septic tank,” which the article reports as wording used by a news report and must keep exactly. The same technical term is retained consistently in the surrounding article. | When a news report says “combined septic tank,” you may wonder. | When a news report says “combined septic tank,” you may wonder. |
| invisible | 6,153 | (none) | 6,153 | KEEP -- predictable morphology/compound | The meaning is readily guessed from the familiar word “visible” and the prefix “in-,” meaning not. | A sewer is like an invisible main artery beneath the town. | A sewer is like an invisible main artery beneath the town. |
| flush | 9,610 | (none) | 9,610 | KEEP -- indispensable / natural replacement unavailable | “Flush the toilet” precisely describes sending water through the toilet. Simpler options such as “use the toilet” would change the meaning, while alternatives would be less natural. | We turn on the tap and flush the toilet. | We turn on the tap and flush the toilet. |
| artery | 12,006 | (none) | 12,006 | KEEP -- indispensable / natural replacement unavailable | “Main artery” is a deliberate image for the town’s main underground route, and replacing it with “pipe” or “line” would weaken the article’s central metaphor. No simpler natural alternative preserves both the meaning and the imagery. | A sewer is like an invisible main artery beneath the town. | A sewer is like an invisible main artery beneath the town. |
| sewer | 12,324 | (none) | 12,324 | KEEP -- indispensable / natural replacement unavailable | “Sewer” is the precise term for the underground network carrying wastewater in this article. Alternatives such as “drain” or “pipe” would lose important meaning or be unnatural in these sentences. | Some local governments are considering replacing old sewer systems with combined septic tanks. | Some local governments are considering replacing old sewer systems with combined septic tanks. |
| sewers | (none in top20000) | sewer:12,324 | 12,324 | KEEP -- indispensable / natural replacement unavailable | The plural form precisely refers to the existing underground wastewater networks. Replacements such as “pipes” or “drains” would be less accurate and would weaken the article’s distinction between the old systems and the proposed tanks. | This does not mean removing all sewers. | This does not mean removing all sewers. |
| wastewater | 18,216 | (none) | 18,216 | KEEP -- predictable morphology/compound | The meaning is readily guessed from the familiar words “waste” and “water,” especially in this household context. | It would treat wastewater near each home, instead of connecting the whole town. | It would treat wastewater near each home, instead of connecting the whole town. |

### notes_on_ambiguous_cases

The closest calls were “artery” and “sewer,” but both are retained because simpler replacements would either weaken the central metaphor or reduce the precision of the infrastructure description.
