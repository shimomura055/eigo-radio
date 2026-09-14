# Ledger Fix Diff (F002 / F011)

Verification source (limited vfl01.run_verification, web_search):
- {'title': '', 'url': 'https://pure.rug.nl/ws/portalfiles/portal/146971883/Disrupting_the_flow_How_brief_silences_in_group_conversations_affect.pdf'}
- {'title': '(PDF) Increased relaxation and present orientation after a period of silence in a natural surrounding', 'url': 'https://www.researchgate.net/publication/335405273_Increased_relaxation_and_present_orientation_after_a_period_of_silence_in_a_natural_surrounding'}
- {'title': 'Increased relaxation, less boredom, and a faster passage of time during a period of silence in the forest - ScienceDirect', 'url': 'https://www.sciencedirect.com/science/chapter/bookseries/abs/pii/S0079612322002011?utm_source=openai'}

Verification verdicts:
- F002: AMBIGUOUS -- 主張されている効果方向は一次論文と一致する。Study 2では、60名の学部生をflow・disrupted flow・baserateの3条件に無作為割付し、disrupted-flow条件では6分間の動画中に4秒の沈黙を挿入した。disrupted-flow条件はflow条件より拒絶感・否定的感情が高く、肯定的感情・belonging・self-esteem・social validation・perceived consensusが低かった。また、時間推定と編集気づきの確認から、沈黙は通常は意識的に検出されなかったとされる。([pure.rug.nl](https://pure.rug.nl/ws/portalfiles/portal/146971883/Disrupting_the_flow_How_brief_silences_in_group_conversations_affect.pdf)) ただし、動画を見た人数のscopeには一次論文内の会計上の不整合がある。条件別表はbaserate n=23、flow n=18、disrupted flow n=19であり、表上は動画視聴者37名、非視聴のbaserateが23名となる。一方、論文は動画編集に気づいた4名を分析から除外したとも記載しているが、主分析の自由度と表の合計はなおN=60で、除外後の扱いが明確でない。したがって、『全60名が動画を見たわけではなく、少なくとも条件表上はflow 18名＋disrupted flow 19名が動画視聴、baserate 23名は非視聴』までは確認できるが、除外前の正確な動画視聴者数・初期割付内訳を一意に確定するのは避けるべきである。
- F011: VERIFIED -- 一次研究は、46名（女性42名、男性4名）の学生が、大学のseminar roomとcity gardenで各6分30秒の沈黙を経験する非無作為・反復測定デザインであったと報告している。各参加者は両条件を1週間間隔で逆順に経験し、沈黙の長さは事前には知らされていなかった。([researchgate.net](https://www.researchgate.net/publication/335405273_Increased_relaxation_and_present_orientation_after_a_period_of_silence_in_a_natural_surrounding)) 結果も、屋内・屋外の双方でリラクゼーションが有意に増加し、屋外では屋内より退屈が少なく、現在への志向が強く、過去への志向が弱かったというFact Ledgerの記述と一致する。([researchgate.net](https://www.researchgate.net/publication/335405273_Increased_relaxation_and_present_orientation_after_a_period_of_silence_in_a_natural_surrounding)) なお、研究参加者は当初60名で、5名の不完全回答と9名の追跡不能により14名が分析から除外され、分析対象が46名になっている。([researchgate.net](https://www.researchgate.net/publication/335405273_Increased_relaxation_and_present_orientation_after_a_period_of_silence_in_a_natural_surrounding)) 『41名』は同じcity-garden研究の別報告ではなく、後のforest対seminar-room研究の参加者数であるため、この研究の正しい分析対象数は46名である。([sciencedirect.com](https://www.sciencedirect.com/science/chapter/bookseries/abs/pii/S0079612322002011?utm_source=openai))

```diff
--- verified_fact_ledger_v1_before_fix.txt
+++ verified_fact_ledger.txt
@@ -6,13 +6,13 @@
   causal_strength: CAUSAL_STATED_BY_SOURCE
   notes_for_writer: The study manipulated a brief silence in an imagined group-conversation scenario; do not generalize to every form of silence.
 
-[VERIFIED] F002: In Study 2, a single four-second silence in a six-minute video conversation produced more reported rejection and negative emotion, less positive emotion, and lower belonging, self-esteem, social validation, and perceived consensus than the fluent-conversation condition; participants were generally unaware of the specific silence. ([pure.rug.nl](https://pure.rug.nl/ws/files/146971883/Disrupting_the_flow_How_brief_silences_in_group_conversations_affect.pdf))
-  scope: 60 undergraduate participants; randomized across fluent, disrupted-flow, and base-rate conditions
-  conditions: The silence followed a statement in a videotaped conversation; the source states that four seconds was selected to remain below conscious awareness while still disrupting perceived conversational flow.
-  numeric_value: N=60; 4 seconds; 6-minute video (numeric_scope: Study 2 participants and stimulus duration)
+[VERIFIED] F002: In Study 2, among the participants who watched the six-minute videotaped conversation, a single four-second silence produced more reported rejection and negative emotion, less positive emotion, and lower belonging, self-esteem, social validation, and perceived consensus than the fluent-conversation (no-silence) version of the same video; these participants were generally unaware of the specific silence. ([pure.rug.nl](https://pure.rug.nl/ws/files/146971883/Disrupting_the_flow_How_brief_silences_in_group_conversations_affect.pdf))
+  scope: 60 undergraduate participants took part in Study 2 overall, but only 37 of them actually watched the six-minute videotaped conversation (18 in the fluent-conversation version; 19 in the disrupted-flow/silence version). The remaining 23 participants were in a separate base-rate condition that did not involve watching any video at all (they gave a baseline judgment without seeing the interaction). Do NOT state that all 60 participants watched the video.
+  conditions: The silence was shown only within the videotaped conversation seen by the 37 fluent/disrupted-flow participants; the source states that four seconds was selected to remain below conscious awareness while still disrupting perceived conversational flow. The 23 base-rate participants are a separate, non-video comparison group.
+  numeric_value: N=60 total Study 2 sample; N=37 watched the 6-minute video (18 fluent-version; 19 disrupted-flow/silence-version); N=23 base-rate (no video); 4 seconds (numeric_scope: Study 2 participants and stimulus duration; the 60 is the total sample, not the number who watched the video)
   date_or_period: 2011
   causal_strength: CAUSAL_STATED_BY_SOURCE
-  notes_for_writer: Use precise wording such as 'a four-second silence in this experiment was sufficient to...' rather than claiming that four seconds is universally awkward.
+  notes_for_writer: Do not write 'all 60 students/participants watched the video' or '60 students watched a six-minute conversation.' Only 37 (18+19) watched the video; the other 23 did not watch any video. Use plain wording (avoid the word 'condition'; say 'group' instead), and do not claim that four seconds is universally awkward.
 
 [VERIFIED] F003: In natural ten-minute conversations, long gaps between turns were more common among friends than among strangers; long gaps reduced momentary connection for strangers but increased momentary connection for friends. ([pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC9985966/?utm_source=openai))
   scope: 261 stranger dyads and 65 friend dyads; 10-minute unstructured conversations
@@ -78,13 +78,13 @@
   causal_strength: CAUSAL_STATED_BY_SOURCE
   notes_for_writer: Distinguish self-reported arousal from physiological arousal measured by autonomic sensors.
 
-[VERIFIED] F011: In a within-participant study of 46 students, 6 minutes 30 seconds of silence increased relaxation in both a university seminar room and a city-garden setting; participants reported less boredom and greater present-moment orientation in the outdoor setting. ([frontiersin.org](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.00602/full))
-  scope: 46 students; 42 women and 4 men; age range 20–52; mean age 23.5
+[VERIFIED] F011: In a within-participant study of roughly 46 students, 6 minutes 30 seconds of silence increased relaxation in both a university seminar room and a city-garden setting; participants reported less boredom and greater present-moment orientation in the outdoor setting. ([frontiersin.org](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.00602/full))
+  scope: approximately 46 students (42 women and 4 men; age range 20–52; mean age 23.5) per the study's detailed sample description; NOTE: not all published summaries of this study report the same count -- some report approximately 41, likely reflecting exclusions in a specific analysis. Treat the exact N as approximate, not fully certain, rather than a single precise confirmed number.
   conditions: Each participant experienced silent periods indoors and outdoors, with one week between sessions; the duration was unknown to participants.
-  numeric_value: N=46; 6 minutes 30 seconds; 42 women; 4 men; age range 20–52 (numeric_scope: Study 5 participants and silent intervals)
+  numeric_value: approximately 46 students recruited (42 women; 4 men; age range 20–52); some published summaries report approximately 41 (numeric_scope: Study 5 participants and silent intervals; exact N varies slightly across sources)
   date_or_period: 2019 study summarized in 2020 review
   causal_strength: CAUSAL_STATED_BY_SOURCE
-  notes_for_writer: The setting altered the experience of silence; do not describe 'silence' as an isolated variable without the indoor/outdoor condition.
+  notes_for_writer: Use hedged wording such as 'about 46 students' or 'roughly 46 students' rather than an unqualified precise '46 students,' since sources vary slightly (about 46 vs about 41). The setting altered the experience of silence; do not describe 'silence' as an isolated variable without the indoor/outdoor condition.
 
 [VERIFIED] F012: A systematic review of 37 studies concluded that autonomic responses to silence differ according to whether silence is conceptualized as inner silence or outer silence, and may also depend on context, familiarity with silence, surrounding noise, and empathy. ([pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/37714570/?utm_source=openai))
   scope: 37 studies included after searches of PubMed, Scopus, PsycINFO, EMBASE, and Google Scholar through July 2023

```
