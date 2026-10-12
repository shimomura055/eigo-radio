# run_e2e_02 Melos含有clipの全ASR転写一覧(OpenAI Primary、時系列)

出典: `er011_output/attempt_history.jsonl`(theme_id=run_e2e_02)と`{b1b,a2}/audit/tts_generation_results.json`。read-onlyで抽出。
Azure(Secondary)転写はPASS時には保存されない仕様(HR queue入りclipのみ`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`にstepsとして保存)。


#### b1b comment_1 (最終status=OK)
原文: `Listen for what Melos promises before he leaves.`
- 17:47:01 減速前 standard#1 転写=`Listen for what Mellos promises before he leaves.` 判定=SECONDARY_ASR_CORROBORATED_MATCH

#### b1b comment_2 (最終status=OK)
原文: `Melos promised to return, and his friend chose to trust him. What will happen as Melos makes his way back to the city?`
- 17:47:08 減速前 standard#1 転写=`Melos promised to return, and his friend chose to trust him. What will happen as Melos makes his way back to the city?` 判定=EXACT_MATCH

#### b1b comment_3 (最終status=OK)
原文: `Melos is badly hurt, and for a moment he thinks about giving up. What will make him keep going, and will he reach the city in time?`
- 17:47:18 減速前 standard#1 転写=`Mellos is badly hurt, and for a moment, he thinks about giving up. What will make him keep going? And will he reach the city in ti` 判定=SECONDARY_ASR_CORROBORATED_MATCH

#### b1b full_story_part1_c1 (最終status=OK)
原文: `Melos's voice rang through the hall.`
- 17:48:19 減速前 standard#1 転写=`Mello's voice rang through the hall.` 判定=SECONDARY_ASR_CORROBORATED_MATCH

#### b1b full_story_part1_c5 (最終status=ASR_VALIDATION_UNCERTAIN)
原文: `Melos said.`
- 17:49:42 減速前 standard#1 転写=`Mello said.` 判定=ASR_VALIDATION_UNCERTAIN

#### b1b full_story_part1_c9 (最終status=OK)
原文: `Melos turned to his friend, but before he could speak, his friend held out his hands for the chains.`
- 17:50:21 減速前 standard#1 転写=`Melo started to his friend, but before he could speak, his friend held out his hands for the chains.` 判定=TRUE_CONTENT_MISMATCH
- 17:50:21 減速前 standard#2 転写=`Mallow turned to his friend, but before he could speak, his friend held out his hands for the chains.` 判定=SECONDARY_ASR_CORROBORATED_MATCH

#### b1b full_story_part1_c11 (最終status=OK)
原文: `At the wedding, his sister's laughter rose above the other voices. Melos listened closely. He wanted to remember exactly how it sounded. Bef...`
- 17:50:45 減速前 standard#1 転写=`At the wedding, his sister's laughter rose above the other voices. Meloce listened closely. He wanted to remember exactly how it s` 判定=SECONDARY_ASR_CORROBORATED_MATCH

#### b1b full_story_part2_c1 (最終status=OK)
原文: `At the river, he stopped. The bridge was gone. Rain had turned the water brown and violent. He stepped back, ran, and threw himself into the...`
- 17:51:25 減速前 standard#1 転写=`At the river, he stopped. The bridge was gone. Rain had turned the water brown and violent. He stepped back, ran, and threw himsel` 判定=HIGH_SIMILARITY_SAFE

#### b1b full_story_part3_c1 (最終status=OK)
原文: `Then he remembered the hands held out for the chains. His friend had trusted him without asking for another promise. Water dripped from a cr...`
- 17:53:11 減速前 standard#1 転写=`Then he remembered the hands held out for the chains. His friend had trusted him without asking for another promise. Water dripped` 判定=ASR_VALIDATION_UNCERTAIN
- 17:53:11 減速前 standard#1 転写=`Then he remembered the hands held out for the chains. His friend had trusted him without asking for another promise. Water dripped` 判定=NUMERIC_EQUIVALENCE_MATCH

#### b1b full_story_part3_c3 (最終status=OK)
原文: `His friend turned. Melos fell against him.`
- 17:53:26 減速前 standard#1 転写=`His friend turned, mellows fell against him.` 判定=SECONDARY_ASR_CORROBORATED_MATCH

#### a2 japanese_title (最終status=OK)
原文: `走れメロス`
- 18:22:35 減速前 standard#1 転写=`가시 레메로스` 判定=TRUE_CONTENT_MISMATCH
- 18:22:35 減速前 standard#2 転写=`はしれメロス` 判定=PHONETIC_MATCH

#### a2 preview (最終status=OK)
原文: `結婚式を終えたメロスは、三日目の夜明け前に町へ戻り始めます。帰り道には、橋のない川と、道をふさぐ男たちがいます。川は雨で茶色くなり、流れもとても速くなっています。`
- 18:22:43 減速前 standard#1 転写=`結婚式を終えたメロスは、三日目の夜明け前に町へ戻り始めます。帰り道には、橋のない川と道を塞ぐ男たちがいます。川は雨で茶色くなり、流れもとても速くなっています。` 判定=PHONETIC_MATCH

#### a2 comment_1 (最終status=STOPPED)
原文: `メロスは、恐怖から人を殺し、話す機会も与えない支配者を責め、死刑を命じられます。妹の結婚式に出るため三日間の猶予を求め、友人を残して出発しますが、遅れて戻れば友人が代わりに死ぬことになっています。`
- 18:23:10 減速前 standard#1 転写=`メロスは恐怖から人を殺し、話す機会も与えない支配者を責め、死刑を命じられます。妹の結婚式に出るため3日間の猶予を求め、友人を残して出発しますが、遅れて戻れば友人が代わりに死ぬことになっています。` 判定=TRUE_CONTENT_MISMATCH
- 18:23:10 減速前 standard#2 転写=`メオスは恐怖から人を殺し、話す機会も与えない支配者を責め、死刑を命じられます。妹の結婚式に出るため3日間の猶予を求め、友人を残して出発しますが、遅れて戻れば友人が代わりに死ぬことになっています。` 判定=TRUE_CONTENT_MISMATCH
- 18:23:10 減速前 fallback#1 転写=`メロスは恐怖から人を殺し、話す機会も与えない支配者を責め、死刑を命じられます。妹の結婚式に出るため3日間の猶予を求め、友人を残して出発しますが、遅れて戻れば友人が代わりに死ぬことになっています。` 判定=TRUE_CONTENT_MISMATCH

#### a2 comment_3 (最終status=OK)
原文: `メロスは、鎖を受け入れるために差し出された友人の手を思い出します。友人は、もう一度約束を求めずに彼を信じていました。岩の割れ目から水が少しずつ流れ、メロスはそれを飲んで立ち上がり、一歩ずつ進みます。`
- 18:23:51 減速前 standard#1 転写=`メロスは、くさりを受け入れるために差し出された友人の手を思い出します。友人は、もう一度約束を求めずに彼を信じていました。岩の割れ目から水が少しずつ流れ、メロスはそれを飲んで立ち上がり、一歩ずつ進みます。` 判定=PHONETIC_MATCH

#### a2 full_story_part1_c1 (最終status=STOPPED)
原文: `Melos called across the hall,`
- 18:24:38 減速前 standard#1 転写=`Mellos called across the hall.` 判定=SECONDARY_ASR_CORROBORATED_MATCH
- 18:24:38 **減速後**再検証#1 転写=` Mellows called across the hall.` 判定=ASR_VALIDATION_UNCERTAIN -> status=STOPPED
- 18:24:43 減速前 standard#1 転写=`Mellos called across the hall.` 判定=SECONDARY_ASR_CORROBORATED_MATCH
- 18:24:44 **減速後**再検証#2 転写=`Mellow's called across the hall.` 判定=ASR_VALIDATION_UNCERTAIN -> status=STOPPED
- 18:34:51 減速前 standard#1 転写=`Mello's called across the hall.` 判定=NORMALIZED_MATCH
- 18:34:52 **減速後**再検証#3 転写=`Mellos called across the hall.` 判定=ASR_VALIDATION_UNCERTAIN -> status=STOPPED

#### a2 full_story_part1_c5 (最終status=STOPPED)
原文: `Melos said.`
- 18:35:24 減速前 standard#1 転写=`Mello said.` 判定=SECONDARY_ASR_CORROBORATED_MATCH
- 18:35:25 **減速後**再検証#1 転写=`Mello said` 判定=ASR_VALIDATION_UNCERTAIN -> status=STOPPED
- 18:45:37 減速前 standard#1 転写=`Mello said.` 判定=ASR_VALIDATION_UNCERTAIN
- 18:45:37 減速前 fallback#1 転写=`Mello said.` 判定=CONNECTED_SPEECH_ACCEPT
- 18:45:38 **減速後**再検証#2 転写=`Mello said.` 判定=ASR_VALIDATION_UNCERTAIN -> status=STOPPED

#### a2 full_story_part1_c9 (最終status=OK)
原文: `Melos turned to his friend, who offered his hands for the chains. Melos had no time to speak.`
- 18:46:13 減速前 standard#1 転写=`Melos turned to his friend, who offered his hands for the chains. Melos had no time to speak.` 判定=EXACT_MATCH
- 18:46:14 **減速後**再検証#1 転写=`Melos turned to his friend, who offered his hands for the chains. Melos had no time to speak.` 判定=EXACT_MATCH -> status=OK

#### a2 full_story_part1_c11 (最終status=OK)
原文: `At the wedding, his sister's laugh rose above everyone's voices. Melos listened closely to remember its exact sound. He left for the city be...`
- 18:46:38 減速前 standard#1 転写=`At the wedding, his sister's laugh rose above everyone's voices. Mellows listened closely to remember its exact sound. He left for` 判定=SECONDARY_ASR_CORROBORATED_MATCH
- 18:46:39 **減速後**再検証#1 転写=`At the wedding, his sister's laugh rose above everyone's voices. Melo listened closely to remember its exact sound. He left for th` 判定=ASR_VALIDATION_UNCERTAIN -> status=STOPPED
- 18:46:48 減速前 standard#1 転写=`At the wedding, his sister's laugh rose above everyone's voices. Melos listened closely to remember its exact sound. He left for t` 判定=NUMERIC_EQUIVALENCE_MATCH
- 18:46:49 **減速後**再検証#2 転写=`At the wedding, his sister's laugh rose above everyone's voices. Melos listened closely to remember its exact sound. He left for t` 判定=NUMERIC_EQUIVALENCE_MATCH -> status=OK

#### a2 full_story_part3_c1 (最終status=OK)
原文: `He remembered the hands held out for the chains. His friend trusted him without asking for another promise. Water came slowly through a crac...`
- 18:48:05 減速前 standard#1 転写=`He remembered the hands held out for the chains. His friend trusted him, without asking for another promise. Water came slowly thr` 判定=NORMALIZED_MATCH
- 18:48:06 **減速後**再検証#1 転写=`He remembered the hands held out for the chains. His friend trusted him, without asking for another promise. Water came slowly thr` 判定=TRUE_CONTENT_MISMATCH -> status=STOPPED
- 18:48:32 減速前 standard#1 転写=`He remembered the hands held out for the chains. His friend trusted him without asking for another promise. Water came slowly thro` 判定=NUMERIC_EQUIVALENCE_MATCH
- 18:48:33 **減速後**再検証#2 転写=`He remembered the hands held out for the chains. His friend trusted him without asking for another promise. Water came slowly thro` 判定=ASR_VALIDATION_UNCERTAIN -> status=STOPPED
- 18:59:01 減速前 standard#1 転写=`He remembered the hands held out for the chains. His friend trusted him without asking for another promise. Water came slowly thro` 判定=SECONDARY_ASR_CORROBORATED_MATCH
- 18:59:03 **減速後**再検証#3 転写=`He remembered the hands held out for the chains. His friend trusted him without asking for another promise. Water came slowly thro` 判定=NORMALIZED_MATCH -> status=OK

#### a2 full_story_part3_c3 (最終status=STOPPED)
原文: `His friend turned around, and Melos fell against him.`
- 18:59:17 減速前 standard#1 転写=`His friend turned around and Mellows fell against him.` 判定=SECONDARY_ASR_CORROBORATED_MATCH
- 18:59:18 **減速後**再検証#1 転写=`His friend turned around and mellowes fell against him.` 判定=ASR_VALIDATION_UNCERTAIN -> status=STOPPED
- 18:59:25 減速前 standard#1 転写=`His friend turned around and mellows fell against him.` 判定=SECONDARY_ASR_CORROBORATED_MATCH
- 18:59:25 **減速後**再検証#2 転写=`His friend turned around and mellows fell against him.` 判定=ASR_VALIDATION_UNCERTAIN -> status=STOPPED
- 19:09:33 減速前 standard#1 転写=`His friend turned around and mellows fell against him.` 判定=SECONDARY_ASR_CORROBORATED_MATCH
- 19:09:34 **減速後**再検証#3 転写=`His friend turned around, and Mellos fell against him.` 判定=ASR_VALIDATION_UNCERTAIN -> status=STOPPED
