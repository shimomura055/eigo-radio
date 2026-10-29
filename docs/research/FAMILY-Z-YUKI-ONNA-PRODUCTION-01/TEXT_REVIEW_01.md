# TEXT_REVIEW_01 (FAMILY-Z-YUKI-ONNA-PRODUCTION-01 委任_02、2026-10-30)

対象run: er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01 / Seed sha: seed.json 13d86f74cc5e, primary_text_excerpt.md 95dba57bbdf7 / Writer再生成: なし(初回の3段chain r0->r1->r2のみ)

## 本文全文(Adv = writer/r2.md、sha 09031ab9f23c、405語)

# The Woman in White

One winter night in Japan, two woodcutters struggled through a snowstorm. Minokichi was eighteen; the old man was his master. When they could go no farther, they took shelter in a hut beside a river. They barred the door and lay under their straw coats. Soon the old man slept.

Minokichi woke with snow brushing his face. The door stood open. A woman dressed in white was bending over his master. In the pale light, her breath flowed across the old man’s face like white smoke.

Then she turned. Minokichi tried to rise, but his body would not move. Her beautiful face came close to his.

“I meant to kill you too,” she whispered. “But you are young, so you may live. Tell anyone what you saw tonight—even your own mother—and I will know. Then I will kill you. Remember.”

She stepped out into the storm. Minokichi barred the door and touched his master’s face. It was icy cold. The old man was dead.

After that night, Minokichi told nobody what had happened. He kept silent even about his master’s death.

The next winter, on the road home, he met a beautiful girl called Yuki. Her skin was white, and her voice was gentle. He took her home to his widowed mother, who welcomed the girl and persuaded her to stay.

Minokichi and Yuki married. In time they had ten fair-skinned children. The children grew, but Yuki seemed never to grow old.

Years later, one evening in their home, Minokichi watched his wife sewing by the lamp. Their children were asleep, and the light lay softly on Yuki’s face.

“I once saw a woman who looked very like you,” he said.

“Where did you see her?” Yuki asked.

Minokichi told her the whole story: the hut, his master’s death, the woman’s white breath, and the warning that had kept him silent.

Yuki let her sewing fall. She stood and bent over him.

“It was me!” she cried. “I told you I would kill you if you ever said one word about it! Only those sleeping children keep me from killing you now. Take very good care of them. If they ever have reason to complain of you, I will treat you as you deserve!”

Her voice grew thin, like the crying of the wind. She melted into white mist, rose towards the roof beams, and slipped away through the smoke-hole.

She was never seen again.

## 本文全文(Std = writer/std.md、sha 4b9135ddbf08、399語)

# The Woman in White

One winter night in Japan, two woodcutters faced a snowstorm. Minokichi was eighteen and worked for the older man. They could not continue, so they entered a riverside hut. They shut the door with a bar. Both lay under straw coats, and his master soon slept.

Snow touched Minokichi’s face and woke him. The open door let in the storm. A woman in white bent over his master. In the pale light, her breath crossed his face like white smoke.

The woman turned towards Minokichi. He wanted to get up, but his body stayed still. She brought her beautiful face close to his.

“I planned to kill you too,” the woman whispered. “But you can live because you are young. Never tell anyone about tonight, not even your mother. If you do, I will know and kill you. Do not forget.”

She left him and went back into the storm. He put the bar across the door again. His master’s face felt cold as ice; the man was dead.

Afterwards, Minokichi told nobody, not even about his master’s death.

The next winter, Minokichi met a beautiful girl called Yuki. Her skin was white, and she spoke in a gentle voice. He took her home to his mother, whose husband had died. His mother welcomed Yuki and talked her into staying.

Yuki became Minokichi’s wife, and they later had ten light-skinned children. The children grew older, but she did not seem to age.

One evening years later, Minokichi watched Yuki sewing at home. A lamp lit her face softly while their children slept.

“Once, I saw a woman who looked much like you,” Minokichi said.

“Where was that?” his wife asked him.

He told Yuki everything about that night in the hut. He described his master’s death, the woman’s white breath, and her warning.

Yuki dropped her sewing, got up, and bent down over Minokichi.

“That woman was me!” Yuki cried. “I warned you that I would kill you for telling anyone! Only our sleeping children keep you alive now. You must look after them very well. If they ever have reason to complain about you, you will get what you deserve!”

Her voice grew weak, like the sound of crying wind. She melted into white mist and rose towards the roof beams. Then she slipped away through the smoke-hole in the roof.

No one ever saw Yuki after that.


## 原文§5の5項目 再点検(○=問題なし △=条件付き ×=不可)
| # | 項目 | Adv | Std | 根拠(本文引用・実測) |
|---|---|---|---|---|
| 1 | 音声だけで理解できるか | ○ | ○ | 一本道の直線時系列。因果の重要点が台詞か短い1文で明示される("Minokichi told nobody what had happened. He kept silent even about his master's death." / "It was me!")。視覚依存の描写なし(snow, breath like white smoke, thin voice)。最長の連続地の文は冒頭約95語(場面導入) |
| 2 | 人物関係が明確か | ○ | ○ | 名前はMinokichiとYukiの2つのみ。老人="the old man / his master"(Std "the older man")、母="his widowed mother"(Std "his mother, whose husband had died")、子="ten fair-skinned children"。白い女=妻の同一性は語り手が明言せず、最終場面のYuki台詞("It was me!" / Std "That woman was me!")とYuki(Leda)同一Voiceで伝える。Mosaku等の他人名の増加なし |
| 3 | 今どの場面かを追えるか(場面頭の1文) | ○(注記あり) | ○(注記あり) | 3場面とも場面頭に時・場所の1文が実在: 場面1 "One winter night in Japan, two woodcutters struggled through a snowstorm."、場面2 "The next winter, on the road home, he met a beautiful girl called Yuki."(Std "The next winter, Minokichi met a beautiful girl called Yuki."=Stdは場所語なし)、場面3 "Years later, one evening in their home, Minokichi watched his wife sewing by the lamp."(Std "One evening years later, Minokichi watched Yuki sewing at home.")。**注記**: plan段のPart境界は[4,9](=Part1: 段落0-3[出会い〜約束の台詞まで] / Part2: 段落4-8[小屋の後始末・沈黙・結婚・年月・ランプの夜の導入] / Part3: 段落9-15[男の台詞〜結末])で、場面境界とは一致しない(Part2が場面1末尾・場面2・場面3頭を含み、Part3が台詞から始まる)。Part境界は既存の承認済み機構(決定論候補+luna選択)の結果で、Part3頭は直前Part末尾の場面頭文("Years later... lamp")から連続して聴く前提。場面頭文自体は本文に在る |
| 4 | 怪談の雰囲気と説明不足 | ○ | ○ | 語り手のコメント・教訓なし。正体は語りでなくYuki台詞で明かす。結末直前の付加文なし("She was never seen again." / Std "No one ever saw Yuki after that." が最終文)。小さな手がかり(white skin / fair-skinned children / seemed never to grow old)は事実として1文ずつ。説明不足の欠落(因果の抜け)は下表のとおりなし |
| 5 | 台詞と地の文の比率(実測) | ○(注記) | ○(注記) | 引用符内の語数/本文語数: Adv 97/405=24.0%、Std 93/399=23.3%(引用6件ずつ、前文タイトル除く)。Seedの目安「約1/3」より低いが、台詞は小屋の囁き(Yuki)と最終場面の掛け合い(Minokichi/Yukiの2者)の山場2か所に集中し、地の文だけが続く最長区間は約95語(冒頭)。地の文が主体の怪談の語りとして偏りなし。**判定基準(○の閾値)に明文なし**のため○としたが、1/3を下回る点はFableが確認可 |

## 因果対応表(文単位)
| 因果 | Adv該当文 | Std該当文 |
|---|---|---|
| 吹雪の夜の出会い | "two woodcutters struggled through a snowstorm." / "A woman dressed in white was bending over his master." | "two woodcutters faced a snowstorm." / "A woman in white bent over his master." |
| 老人の死 | "The old man was dead." | "the man was dead." |
| 「誰にも話すな」の約束(提示1) | "Tell anyone what you saw tonight—even your own mother—and I will know. Then I will kill you. Remember." | "Never tell anyone about tonight, not even your mother. If you do, I will know and kill you. Do not forget." |
| 沈黙(提示2) | "After that night, Minokichi told nobody what had happened. He kept silent even about his master's death." | "Afterwards, Minokichi told nobody, not even about his master's death." |
| 再会・結婚 | "he met a beautiful girl called Yuki." / "Minokichi and Yuki married." | "Minokichi met a beautiful girl called Yuki." / "Yuki became Minokichi's wife" |
| 約束を破る | "Minokichi told her the whole story: the hut, his master's death, the woman's white breath, and the warning" | "He told Yuki everything about that night in the hut." |
| 正体の判明 | "“It was me!” she cried." | "“That woman was me!” Yuki cried." |
| 約束の繰り返し(提示3)と結果 | "I told you I would kill you if you ever said one word about it! Only those sleeping children keep me from killing you now." / "She was never seen again." | "I warned you that I would kill you for telling anyone! Only our sleeping children keep you alive now." / "No one ever saw Yuki after that." |
全因果が欠落なく本文に在る。CP_CHECK_01のSeed essentials 5件(ending_reveal / withhold / setup-payoff / keep_name Minokichi・Yuki)と key_roles(老人・母は役割名のみ・台詞なし)も充足。ending: 結末前の示唆の希釈(結末直前の付加文)なし。

## plan段の結果(runner出力、`segment_plan_{a2,b1b}.json`・`speaker_table.md`)
- 話者: narrator(Aoede) / yuki(Leda) / minokichi(Algieba) の3のみ。Adv/Std とも引用6件=clip6件(yuki 5・minokichi 1)。語り手Voice以外のclip: full_story_part1_c2,c4(yuki) / part3_c1(minokichi) / part3_c3,c5,c7(yuki)。
- 決定論vs LLM: Advは6件中決定論一致1件(q10_1)・LLMのみ5件(she/he型の引用)・不一致0。Stdは決定論一致4件・LLMのみ2件・不一致0。STOPなし。
- 未閉引用符: 本文の引用は全て開閉対(“ ”)で、閉じ引用符の無い発言なし。quote_spansの異常なし。
- 白い女の囁き 'I meant to kill you too,' whispered は引用が2分割(c2,c4)され間に地の文clip(c3 "she whispered.")が入る(既存仕様どおり)。
- Part語数: Adv 141/121/137、Std 140/129/136。

## 総合判定
×・△なし(上記の注記は「Part境界が場面境界と一致しない」「台詞比率24%<目安1/3」の2点を観察記録。いずれも承認済み仕様・Seed必須要件・目的要件〔音声で追える・因果が明示〕に抵触しないと判断)。Writer再生成は実施せず。次工程(support,kp)へ進行。実音声でnarrator(Aoede)とYuki(Leda)の聞き分けを確認するのは委任_03以降。
