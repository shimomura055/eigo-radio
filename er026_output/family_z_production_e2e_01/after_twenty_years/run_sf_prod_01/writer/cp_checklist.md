# Fable CPチェックリスト(機械生成: after_twenty_years、essentials sha 28aec0d24dfb)

各行の『本文の該当引用』欄にstage別の本文引用(逐語)を記入する。引用できない=欠落。判定・記入はCP担当(Fable/Sonnet記入→Fable確認)。

処置規則(ユーザー承認2026-10-23): (A)重大=ending_reveal・key_roles(keep_name人物の脱落/他人名の増加)・key_causality・setups_and_payoffsのいずれかの欠落 -> CP不合格。TTS前に修正(Writer再実行=承認済みの明示--regenerate-stage、または決定論パッチ)し、原因分析を記録し、C案(軽量事後確認)要否をユーザーへ提示する(報告で`判断候補`)。(B)軽微=結末直前の付加文など、結末前の示唆(withhold_until_end)を希釈する不要文のみ -> 決定論の削除パッチ(exact文字列の削除)を適用し、削除した文・理由・前後sha・対象stageを記録する。所見を処置せずTTSへ進めてはならない。自動判定・LLM検査・retry・Human Reviewは無い。

| # | 深刻度 | 項目 | 内容 | 本文の該当引用(r0) | 本文の該当引用(r1) | 本文の該当引用(r2) | 本文の該当引用(std_adjust) | 判定 |
|---|---|---|---|---|---|---|---|---|
| 1 | 重大 | ending_reveal(種明かしが最終に在る) | The story ends with the note from Patrolman Wells, which reveals that the patrolman Bob spoke with at the start was Jimmy himself: Jimmy kept the promise and came on time, recognized Bob as the man wanted in Chicago, and could not arrest his old friend, so he had a plain clothes man do it. [原作最終文: Somehow I couldn't do it myself, so I went around and got a plain clothes man to do the job.] |  |  |  |  |  |
| 2 | 軽微 | withhold_until_end(結末前の示唆・結末直前の付加文が無い) | Before the note, do not hint that the patrolman is Jimmy, that Bob is a wanted man, or that the tall man is not Jimmy. |  |  |  |  |  |
| 3 | 重大 | setup と payoff | Bob tells the patrolman about the twenty-year promise with his best friend Jimmy and says he will wait half an hour; the patrolman listens calmly and walks on.  ->  The tall man who comes at the half-hour mark pretends to be Jimmy; under the drugstore light Bob sees it is not Jimmy, and he is arrested as the man wanted in Chicago. |  |  |  |  |  |
| 4 | 重大 | key_role keep_name=Bob(名前が維持され他人名が増えていない) | the man from the West who waits in the doorway, keeps the twenty-year promise and is arrested |  |  |  |  |  |
| 5 | 重大 | key_role keep_name=Jimmy(名前が維持され他人名が増えていない) | Bob's best friend and the other half of the promise, who turns out to be the patrolman |  |  |  |  |  |
| 6 | 重大 | key_role(役割・関係で表され名前が付いていない) | the patrolman on the beat who talks with Bob and walks on (he is Jimmy, but this is revealed only by the final note) |  |  |  |  |  |
| 7 | 重大 | key_role(役割・関係で表され名前が付いていない) | the tall man in the long overcoat, a plain clothes officer who pretends to be Jimmy and arrests Bob |  |  |  |  |  |
| 8 | 重大 | key_causality | Jimmy comes to keep the promise and, by the light of the match, recognizes Bob as the man wanted in Chicago; unable to arrest his friend himself, he has a plain clothes man pose as Jimmy and make the arrest, and leaves a note for Bob. |  |  |  |  |  |

## 各stageの最終段落(機械抽出、参考。結末直前の付加文の有無はこの直前段落も確認)

### r0(段落数25、語数380)
- 最終段落: “Bob, I was at our meeting place on time. When you struck the match, I recognized you as the man wanted in Chicago. Somehow I couldn’t arrest you myself, so I went and found a plain-clothes man to do the job. —Jimmy”
- 最終の直前段落: Bob unfolded the paper beneath the drugstore light.

### r1(段落数26、語数411)
- 最終段落: “Bob, it’s Jimmy. I was at our meeting place on time. When you struck that match, I recognized your face as the man wanted in Chicago. I came to keep our promise, but I couldn’t bring myself to arrest my old friend, so I found a plain-clothes officer to do it for me.”
- 最終の直前段落: Bob unfolded it beneath the drugstore light.

### r2(段落数28、語数426)
- 最終段落: “Bob, it’s Jimmy. I was the patrolman you spoke to. I came on time to keep our promise. When you struck that match, I recognized your face as the man wanted in Chicago. But I couldn’t bring myself to arrest my old friend, so I found a plain-clothes officer to do it for me.”
- 最終の直前段落: Bob unfolded it under the bright window.

### std_adjust(段落数28、語数443)
- 最終段落: “Bob, this is Jimmy. I was the officer who spoke to you. I came at ten to keep our promise. Your match lit your face, and I recognized you. I knew Chicago’s police were looking for you. I couldn’t arrest my old friend myself, so I found an officer in ordinary clothes to do it for me.”
- 最終の直前段落: Bob opened the note in the light from the window.

