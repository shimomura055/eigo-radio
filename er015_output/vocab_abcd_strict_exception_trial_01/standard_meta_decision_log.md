# standard_meta_decision_log.md

凡例: surface=表層形のtop20000内順位, lemma=採用されたlemma候補(word:順位、未使用または表外は(none)), rank=min(surface,lemma)としてモデルへ渡した値, level=standard/advanced, 旧判定=前回Trial(閾値のみ異なる同一素材)での判定, 新判定=本Trial(厳格定義)での判定, KEEP/SIMPLIFY=新判定の粗い分類, 理由=モデルの判定理由, 置換案=replacement_if_simplify, 意味差・Fact差=meaning_or_fact_change。

### standard_meta Decision Log (strict)

旧判定の出典: STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01 (閾値6,000版)

| surface | lemma | rank | level | 旧判定 | 新判定 | KEEP/SIMPLIFY | 理由 | 置換案 | 意味差・Fact差 |
|---|---|---|---|---|---|---|---|---|---|
| (none in top20000) | (none) | > 20,000 (zipf=1.70, extremely rare) | standard | KEEP -- proper noun | KEEP-C | KEEP | This is a specific designation that Meta itself reportedly gave these workers, so it meets C as an organization's quoted designation. It is not being kept merely because it appears in quotation marks or because it is a general noun. | N/A | none |
| 6,160 | (none) | 6,160 | standard | KEEP -- established Japanese loanword | KEEP-B | KEEP | The English verb directly matches the familiar everyday Japanese loanword リーク, and its information-escape meaning is readily understood in this context. This judgment is based on a well-established ordinary use, not merely on the existence of a katakana spelling or on a narrow technical meaning. | N/A | none |
| 7,166 | (none) | 7,166 | standard | KEEP -- established Japanese loanword | SIMPLIFY | SIMPLIFY | Although ポーズ exists in Japanese, the correspondence is not sufficiently unambiguous here because it can suggest the different word “pose,” and this feature-related use is not reliably understood from the loanword alone. “Temporarily turn off” is simpler and natural while preserving the temporary meaning. | temporarily turn off | none |
| 17,689 | pause:7,166 | 7,166 | standard | KEEP -- established Japanese loanword | SIMPLIFY | SIMPLIFY | The inflected form has the same strict B problem as “pause”: the Japanese form ポーズ is not sufficiently unambiguous in this sentence. “Temporarily turned off” is a simpler, natural replacement that keeps the original meaning. | temporarily turned off | none |
| 8,719 | (none) | 8,719 | standard | KEEP -- proper noun | KEEP-C | KEEP | Reuters is the official name of a real news organization, so it meets C as a proper organizational name. It is not an ordinary noun being kept because of quotation marks or technical usage. | N/A | none |
| 8,776 | (none) | 8,776 | standard | KEEP -- established Japanese loanword | KEEP-B | KEEP | Curtain directly corresponds in form and pronunciation to the familiar everyday Japanese loanword カーテン, and the ordinary object is clear in this sentence. It is not a narrow specialist term, and this decision is based on established everyday understanding rather than katakana spelling alone. | N/A | none |
| 9,646 | (none) | 9,646 | standard | KEEP -- predictable morphology/compound | KEEP-A | KEEP | The word is transparently formed from the already familiar word “perform” and the predictable person-noun ending “-er,” giving the natural meaning “a person who performs.” This meets A through predictable morphology, not merely through general decomposability or the storytelling context. | N/A | none |
| 10,629 | (none) | 10,629 | standard | KEEP -- predictable morphology/compound | KEEP-A | KEEP | This is the predictable form of the easy word “understand” plus “-able,” so a learner can naturally infer its meaning. It meets A directly and is not being kept merely for stylistic preference. | N/A | none |
| 12,912 | (none) | 12,912 | standard | KEEP -- predictable morphology/compound | KEEP-A | KEEP | Backstage is a predictable compound of the easy words “back” and “stage,” allowing a learner to infer “behind the stage.” This meets A because the compound meaning is naturally guessable, rather than because it is part of a fixed expression. | N/A | none |
| 15,670 | (none) | 15,670 | standard | KEEP -- predictable morphology/compound | KEEP-A | KEEP | Onstage is a predictable compound of “on” and “stage,” so its meaning can be naturally guessed from the structure. This is the strict A case of an understandable compound, not an appeal to idiom or style. | N/A | none |

### notes_on_ambiguous_cases

The hardest judgment was “pause”: Japanese ポーズ exists, but it is not sufficiently unambiguous in this feature-related sentence under the strict B standard. “Leak” and “curtain” have more direct, familiar everyday Japanese correspondences in the meanings used here.
