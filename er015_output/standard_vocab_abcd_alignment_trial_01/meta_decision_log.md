# meta_decision_log.md

凡例: surface=表層形のtop20000内順位, lemma=採用されたlemma候補(word:順位、未使用または表外は(none)), 採用rank=min(surface,lemma)としてモデルへ渡した値, 例外/理由=モデルの判定理由(A/B/C/Dまたは平易化理由)。

### Meta Decision Log

| Word | surface | lemma | 採用rank | 判定 | 例外/理由 | Before | After |
|---|---|---|---|---|---|---|---|
| concierges | (none in top20000) | (none) | > 20,000 (zipf=1.70, extremely rare) | KEEP -- proper noun | This appears inside Meta’s reported designation “human concierges,” so it is a quoted designation that must be kept exactly as reported. | Meta called these workers “human concierges.” | Meta called these workers “human concierges.” |
| leak | 6,160 | (none) | 6,160 | KEEP -- established Japanese loanword | リーク is an established Japanese term, especially for information becoming known outside an organization, and its connection to the English pronunciation is clear in this context. | Meta employees worried that call details might leak outside the company. | Meta employees worried that call details might leak outside the company. |
| pause | 7,166 | (none) | 7,166 | KEEP -- established Japanese loanword | ポーズ is a familiar Japanese term for temporarily stopping audio, video, or an activity, and its connection to the English pronunciation is clear here. | ### Privacy concerns led Meta to pause the feature | ### Privacy concerns led Meta to pause the feature |
| paused | 17,689 | pause:7,166 | 7,166 | KEEP -- established Japanese loanword | This is the regular past form of pause, whose meaning is familiar through the established Japanese term ポーズ in this context. Replacing it with “stopped” would lose the sense that the feature may be resumed. | The executive said the company had paused the feature. | The executive said the company had paused the feature. |
| Reuters | 8,719 | (none) | 8,719 | KEEP -- proper noun | Reuters is the proper name of a news organization and must be kept unchanged. | Reuters reviewed internal posts about the feature. | Reuters reviewed internal posts about the feature. |
| curtain | 8,776 | (none) | 8,776 | KEEP -- established Japanese loanword | カーテン is a commonly understood Japanese loanword, and its meaning is easily connected to the English pronunciation. | And who is behind the curtain? | And who is behind the curtain? |
| performer | 9,646 | (none) | 9,646 | KEEP -- predictable morphology/compound | Performer is transparently formed from the familiar verb perform with the regular -er ending, meaning a person who performs. | But another performer was hidden inside the piano. | But another performer was hidden inside the piano. |
| understandable | 10,629 | (none) | 10,629 | KEEP -- predictable morphology/compound | Understandable is directly formed from the familiar word understand with the predictable -able ending. | That makes this approach understandable. | That makes this approach understandable. |
| backstage | 12,912 | (none) | 12,912 | KEEP -- predictable morphology/compound | Backstage is a transparent compound of the easy words back and stage, so its meaning can be readily guessed. | But people who looked backstage found something unexpected. | But people who looked backstage found something unexpected. |
| onstage | 15,670 | (none) | 15,670 | KEEP -- predictable morphology/compound | Onstage is a transparent compound of the easy words on and stage, so its meaning is readily guessable. | Who is speaking onstage? | Who is speaking onstage? |

### notes_on_ambiguous_cases

The closest calls were “leak” and “pause.” Both are kept because リーク and ポーズ are established Japanese terms in these meanings, not merely because they can be written in katakana.
