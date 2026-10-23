# CP_CHECK_01 (原作忠実性チェックポイント、Sonnet記入→Fable確認待ち、2026-10-23)

対象: writer/r2.md(Advanced 426語・28段落)、writer/std.md(Standard 443語・28段落)。Seed essentials sha 28aec0d24dfb。原作 `er026_seeds/after_twenty_years/story.md`(最終段落=手紙)と照合。
r0/r1は中間稿のため引用省略(最終稿r2/stdで判定)。

| # | 項目 | Adv(r2)本文の引用 | Std(std_adjust)本文の引用 | 判定 |
|---|---|---|---|---|
| 1 | ending_reveal(最終が手紙で種明かし) | "Bob, it's Jimmy. I was the patrolman you spoke to. I came on time to keep our promise. When you struck that match, I recognized your face as the man wanted in Chicago. But I couldn't bring myself to arrest my old friend, so I found a plain-clothes officer to do it for me."(最終段落) | "Bob, this is Jimmy. I was the officer who spoke to you. ... I couldn't arrest my old friend myself, so I found an officer in ordinary clothes to do it for me."(最終段落) | OK |
| 2 | withhold_until_end(手紙前に示唆なし、結末直前の付加文なし) | 手紙の直前=`"Before we go, there's a note for you." / Bob unfolded it under the bright window.` 警官の正体・Bobの手配への示唆なし(「you're wanted in Chicago」は原作どおり私服刑事の逮捕告知=手紙の直前の本筋) | `"I have a note for you before we leave." / Bob opened the note in the light from the window.` 同上 | OK(付加文なし) |
| 3 | setup/payoff | setup: `"Half an hour."` / `The patrolman walked on.` payoff: `"You're not Jimmy..."` / `"You're under arrest, Bob. You're wanted in Chicago."` | setup: `"I'll give him thirty minutes."` payoff: `"You can't be Jimmy!..."` / `"I'm arresting you, Bob, because Chicago's police are looking for you."` | OK |
| 4 | keep_name Bob | Bob(全編で一貫、他の人名の増加なし) | 同左 | OK |
| 5 | keep_name Jimmy | `My best friend, Jimmy.` / `"Jimmy!"` / 手紙署名相当 `Bob, it's Jimmy.` | `Jimmy and I ate there...` / `Jimmy, you're here!` | OK |
| 6 | 警官は役割で表現(無名) | `A patrolman stopped beside him.` / `The patrolman walked on.` | `A police officer stopped...` / `The officer continued down the street.` | OK |
| 7 | 背の高い男は役割で表現(無名) | `a tall man in a long overcoat` / `the tall man replied` | 同左 | OK |
| 8 | key_causality(match光で認識→友を捕らえられず私服に頼む→手紙) | `When you struck that match, I recognized your face ... I couldn't bring myself to arrest my old friend, so I found a plain-clothes officer to do it for me.` | `Your match lit your face, and I recognized you. ... I couldn't arrest my old friend myself, so I found an officer in ordinary clothes to do it for me.` | OK |

## 所見(軽微・処置不要の範囲として記録、Fable確認)
- A: 到着時刻 `At half past ten`(Adv)/`At ten thirty`(Std)。原作は約20分後(待機上限30分の内側)。「30分待つ」の期限ちょうどになる点が原作と僅差。因果・結末・人物関係に影響なしのため「重大」ではない。
- B: Advの語数426(330-470内)、Std 443(330-470内)。段落数一致(28/28)。
- C: 「Silky」Bob・Big Joe Brady・Chicagoの手配理由等は省略(free_to_cut/discarded相当)。固有名詞の増加なし。
