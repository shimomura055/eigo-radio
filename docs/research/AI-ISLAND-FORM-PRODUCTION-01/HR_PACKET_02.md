# HR_PACKET_02(AIの仮想の島 Std/Adv `full_story_part1_k2`、ユーザー指定8項目、2026-10-27)
公開(試聴付き): https://shimomura055.github.io/eigo-radio/user_test/family_x_ai_island_form_01/hr_02.html (生成: `tools/build_hr_packet_aif3_01.py --v2`、API 0)。承認はユーザーのみ。

**先に結論**: 本文は変更なし。音声に読ませた文だけ、第1部2段落目の「The AIs sent to the island…」の `AIs` を Std=`AI agents`/Adv=`AI systems` に自動言い換え(承認済みLocal Rewrite)。ページ本文は「AIs」のまま(本文に `AI systems` が無いのは当然)。音声品質の問題ではなく、言い換え音声は承認済み安全規則(M3 Style Gate `LOCAL_REWRITE_RECOVERY`)で人の確認が必須。
1. 元原稿: Std "The AIs sent to the island had no set tasks or rewards. But their starting settings led them to be curious, explore, and learn. They had no homework, but they were ready to explore." / Adv "The AIs sent to the island had no specific tasks or rewards. But their initial settings guided them to be curious, explore, and learn. They had no homework, but they were in exploration mode."(本文SHA一致)
2. 書換え前後: 変更前 "The **AIs** sent to the island…" → 変更後 Std "The **AI agents** sent…"/Adv "The **AI systems** sent…"(他は同一)
3. 推奨音声1件(各level): hr_02.html内(Std 14.3秒/Adv 13.5秒)
4. ASR: 元原稿での3回(標準2+代替指示1)は OpenAI・Azure とも "The AI sent…"(Stdは6%減速後。生成直後は一部Azure "AIS"/OpenAI "AIs"で通過)。採用音声: Std OpenAI "…AI agents sent … awards…"/Azure "…AI agents sent … rewards…"(救済)、Adv OpenAI "…AI systems sent … initial setting guided…"
5. 不一致箇所: 元原稿側 `AIs`→`AI`(複数形sが認識されない)。採用音声側は Std rewards→awards(OpenAIのみ)、Adv settings→setting(複数形)
6. 自動解消不能の理由: Tier3救済(Azureも"AI")・PNAP(固有名詞でない)・er109(同音異表記でない)・台帳/Phrase List(AI/AIs無し)のいずれも対象外。通常retry上限消化済み。M3 Style Gate は人の承認以外で解除不可(Gate緩和はユーザー承認事項)
7. AI評価と確認内容: 意味・事実不変(1語句のみ、7検査通過)。聞いて違和感がないか、本文「AIs」と音声「AI agents/systems」の1語差を許容できるか(推定原因=z+s融合の仮説・未検証)
8. 質問(1つ): 上の2音声で、この段落の「AIs」を「AI agents／AI systems」と読む形でよいですか?
