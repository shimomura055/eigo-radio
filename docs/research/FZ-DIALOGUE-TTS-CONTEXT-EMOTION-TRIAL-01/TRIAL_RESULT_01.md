# TRIAL_RESULT_01 — 『賢者の贈り物』セリフ音声: 現行方式 vs 文脈・感情追加(FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 Phase 1b)

状態: Trial(DEV専用、Production変更0)。Production採用ではない。ユーザー試聴前の提出資料。

## 1. 試聴URL
https://shimomura055.github.io/eigo-radio/user_test/fz_dialogue_context_trial_01/index.html
(開発者向け詳細: 同ディレクトリ `dev_details.html`)。各カードでA=現行方式(本番最終音声)とB=改善方式(ctx_t1最終相当)を同じ行で聞き比べ。A'=現行方式の別take、B'=改善方式の別take(折りたたみ内)。音量は揃えてあります。「本番でも各セリフの音量は揃えられるため、音量の大小ではなく、声の柔らかさ・息づかい・速さ・抑揚で比べてください」。

## 2. 対象一覧と選定理由(Adv=b1bの全dialogue 8件)
- full_story_part2_c2: 悲しみ・不安, ためらい・戸惑い — 不安とためらいを抱えた切り出し。前後に会話が無く、直前の地の文(息を整える)だけが手掛かり。
- full_story_part2_c4: 相手の発言を受けた返答, 感情を抑えた事務的な発言(対照) — Madame(別Voice)。感情の明記が無い台詞が、文脈追加で『過剰に感情的』にならないかの対照。直前のDellaの問いへの返答。
- full_story_part2_c5: ためらい・戸惑い, 感情が変化する場面, 相手の発言を受けた返答 — ためらいを振り切る決意。直前の金額提示への返答。
- full_story_part2_c7: ささやき・静かな発言, 悲しみ・不安 — 先行調査(INVESTIGATION_01)で、ささやきの演出が地の文(別clip・別Voice)にあるため反映されない可能性が指摘された代表例。
- full_story_part3_c2: 感情が変化する場面, 悲しみ・不安, 喜び・驚き — 1セリフ内で動揺→必死の説明→前向きな一言(It'll grow again!)と感情が動く最長のセリフ。
- full_story_part3_c4: 悲しみ・不安, 喜び・驚き, 感情が変化する場面 — セリフ本文に感情語が無い短文(事実陳述)。涙ながらの笑顔という感情が地の文にしか無い、文脈の効果が最も出やすい例。
- full_story_part3_c6: 喜び・驚き — 喜び・高揚。『Look!』『Isn't it perfect?』と感情語が本文にもあり、文脈追加が過剰にならないかの確認にもなる。
- full_story_part3_c8: ささやき・静かな発言, ためらい・戸惑い, 相手の発言を受けた返答 — Jim(男声・別Voice)の静かな告白。直前のDellaの発言への返答で、穏やかな微笑みという演出が地の文にある。
詳細は `SELECTION_01.md`。

## 3. ①②の具体的Style Promptと文脈情報
- ①(現行方式)のstyle: Production既存の汎用Dialogue Style(変更なし)。全文sha256=`add26d27a79c2cbee982eb5ddc32616b8294494a316b973215c94cccc76ede26`(base armが同一shaで生成済み)。全文は各 `er118_output/fz_dialogue_context_tts_trial_01/gen/base_t1/<clip>/request_full.json` の `prompt` の STYLE INSTRUCTIONS 区画。
- ②(改善方式): ①のstyle全文に、下記CONTEXT区画を追加しただけ(TEXT TO SPEAKは当該セリフのみ。同一Voice・model=gemini-2.5-pro-preview-tts・設定)。感情情報はLLM(gpt-6-luna、1 call)が原文のみから作成し、Fableが8件accept。NO_EXPLICIT_CUE 5件は状態行なしで地の文引用で伝える形。
#### full_story_part2_c2(実送信prompt sha f1340bb0c17c…)
```
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Della.
Scene: Outside a hair-goods shop, she asks the owner if they will buy her hair.
Narration just before: "Outside a hair-goods shop, she paused just long enough to catch her breath."
Spoken line after (said by the hair-shop owner; not part of this line): Twenty dollars.
Narration just after: "The owner lifted the heavy waves."
Manner words from the narration: breath, paused
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
=== END STYLE INSTRUCTIONS ===
```

#### full_story_part2_c4(実送信prompt sha dda7504a65be…)
```
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: the hair-shop owner.
Scene: At the hair-goods shop, the owner names the price after lifting Della’s hair.
Spoken line before (said by Della; not part of this line): Will you buy my hair?
Narration just before: "The owner lifted the heavy waves."
Spoken line after (said by Della; not part of this line): Cut it quickly, please.
How this line answers the previous one: The owner answers Della’s question about buying her hair with a price.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
=== END STYLE INSTRUCTIONS ===
```

#### full_story_part2_c5(実送信prompt sha 2df3db382187…)
```
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Della.
Scene: At the hair-goods shop, Della asks the owner to cut her hair after hearing the offer.
Spoken line before (said by Della; not part of this line): Will you buy my hair?
Spoken line before (said by the hair-shop owner; not part of this line): Twenty dollars.
Narration just after: "At the first touch of the scissors, Della shut her eyes. For two hours afterward, she hurried from shop to shop."
Manner words from the narration: hurried, shut her eyes
How this line answers the previous one: She accepts the offer by asking the owner to cut her hair.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
=== END STYLE INSTRUCTIONS ===
```

#### full_story_part2_c7(実送信prompt sha a43fd80f37b2…)
```
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Della.
Speaker's state of mind: She is a little worried about whether he will still find her pretty.
Scene: At home by the mirror, Della whispers to herself after curling her short hair.
Narration just before: "By seven, dinner was nearly ready. Della had curled her short hair, but she kept returning to the mirror."
Spoken line after (said by Della; not part of this line): I sold it, Jim. I couldn't let Christmas come without giving you something. It'll grow again!
Manner words from the narration: kept returning, whispered
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
=== END STYLE INSTRUCTIONS ===
```

#### full_story_part3_c2(実送信prompt sha ed9f520382cf…)
```
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Della.
Speaker's state of mind: She sounds eager to explain and reassure Jim about selling her hair.
Scene: After Jim looks at her hair, Della rushes toward him and explains why she sold it.
Spoken line before (said by Della; not part of this line): Please let him still think I'm pretty,
Narration just before: "His eyes stayed on her hair. Della rushed toward him."
Spoken line after (said by Della; not part of this line): My hair grows quickly.
Narration just after: "He put his arms around her. Then he gave her a package."
Manner words from the narration: eyes stayed, rushed
How this line answers the previous one: She follows her private worry about being thought pretty by explaining the sale and its purpose.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
=== END STYLE INSTRUCTIONS ===
```

#### full_story_part3_c4(実送信prompt sha 70f2de9d4ccc…)
```
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Della.
Scene: After opening Jim’s package of combs, Della holds them against her chest and says her hair grows quickly.
Spoken line before (said by Della; not part of this line): I sold it, Jim. I couldn't let Christmas come without giving you something. It'll grow again!
Narration just before: "Inside were the tortoise-shell combs she had so often admired in a shop window. She held them against her chest, smiling through tears."
Spoken line after (said by Della; not part of this line): Look! Isn't it perfect? Give me your watch.
Narration just after: "Suddenly remembering, she brought out the chain."
Manner words from the narration: smiling, suddenly, tears
How this line answers the previous one: She adds reassurance that her hair will grow quickly after explaining that she sold it.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
=== END STYLE INSTRUCTIONS ===
```

#### full_story_part3_c6(実送信prompt sha 5ae2680ffc4a…)
```
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Della.
Speaker's state of mind: She sounds pleased with the chain and asks Jim to show her his watch.
Scene: At home, Della brings out the chain and shows it to Jim after receiving the combs.
Spoken line before (said by Della; not part of this line): My hair grows quickly.
Narration just before: "Suddenly remembering, she brought out the chain."
Spoken line after (said by Jim; not part of this line): I sold the watch to buy your combs.
Narration just after: "Jim sat down and smiled gently."
Manner words from the narration: gently, smiled, suddenly
How this line answers the previous one: She shifts from saying her hair will grow back to showing Jim the chain and asking for his watch.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
=== END STYLE INSTRUCTIONS ===
```

#### full_story_part3_c8(実送信prompt sha 66916118476b…)
```
CONTEXT FOR THIS ONE LINE (delivery reference only. This block is NOT part of the story to be spoken, and its labels are not script headings. Do NOT read, quote, or paraphrase anything in this CONTEXT block aloud. Only the TEXT TO SPEAK section is spoken.)
Speaker of this line: Jim.
Scene: At home, Jim explains that he sold his watch to buy Della’s combs.
Spoken line before (said by Della; not part of this line): My hair grows quickly.
Spoken line before (said by Della; not part of this line): Look! Isn't it perfect? Give me your watch.
Narration just before: "Jim sat down and smiled gently."
Narration just after: "Della sat beside him and took his hand. Her hair was gone; the combs could not hold it."
Manner words from the narration: gently, smiled
How this line answers the previous one: He answers Della’s request for his watch by explaining that he sold it to buy her combs.
Use this only to choose a natural tone, pace, and energy for this one line, as a good audiobook reader would. The story's own narration above is what supports the feeling of this line. Where this context shows a quiet, soft, or gentle line, it may be quieter, softer, and slower than the general guidance above; otherwise follow the general guidance. Express the feeling mainly through pace, softness, and small changes in pitch, without theatrical over-acting, without added sounds (no sighs, sobs, laughs, or audible breaths), and without adding any emotion beyond what is described. If the story says the line is whispered, use a soft, hushed voice rather than a true whisper, and keep every word clear for English learners. Do not read any word of this CONTEXT block.
=== END STYLE INSTRUCTIONS ===
```

## 4. Fable比較評価
(空欄 — Fable記入)

## 5. 発話正確性・生成条件・再利用分離の確認(Sonnet機械所見、詳細 `EVAL_01.md`)
- 発話正確性: ②16/16 ASR本文逐語一致、leakage(全attempt)0件、needs_listen 0件、comparison_valid 16/16(実送信promptのsha一致)。
- 機械指標の主指標: 方向あり5件のうち正方向の完全分離=1件(part3_c4のみ)、逆向き0件 → 事前登録02の写像で「機械的には効果なし」。
- Madame安定監視(e): 不成立(part2_c4の調音話速・F0幅が①側±20%の外。2語clipで指標が不安定な点は注記)。
- 条件: Voice・model・設定は①側と同一。protected_diff・repo mtime走査はすべて空(Production保存音声・Master Audio Store・sink不変)。
- 限界: 速度加工後のProduction ASR再検証は未実施 / 聴感評価はユーザーのみ / F0・話速は粗い補助指標。

## 6. 実費と量産単価影響
- 実費(raw_usage_log.jsonl): 合計 10.07円(LLM 0.1円 + TTS 26 call 約9.46円[8×3 arm+retry2] + ASR 0.38円 + Azure 0.12円)。Cap 30円内。詳細は `BUDGET_LOG_01.md`。
- 量産単価影響(概算、Productionに採用した場合の仮定): ②は各dialogue clipのprompt入力が約+1,500字(約+0.06円/call)と、clip単位の感情情報LLM(約0.012円/clip)の追加。Magi Advの8セリフなら約0.6円/レベル程度の増。ただしZ会話の再利用キー(style hash)拡張と再生成コストが別途かかる見込みで、採用判断には未試算分がある。70円/記事セット目標への影響は小さい見込み(概算、未検証)。

## 7. Status候補とProduction採用に向けた判断事項
- 事前登録02の機械写像: (a)(b)(c)(f)(g)成立、(e)不成立 → 提出時Status候補は **REJECTED(下位ラベル TRIAL_FAILED_QUALITY相当)**。(d)機械的効果も1/5で弱い。
- 判断事項(Fable→ユーザー): (1) (e)の2語clipへの適用をどう扱うか(事前登録どおりREJECTED、または計測不安定として試聴判断へ進めるか。結果後の基準変更になるためFable判断) (2) 試聴で「改善」ならVALIDATED(Production採用ではない)。量産化にはreuse key拡張・新Gate等が別途必要 (3) 再Trial(Style改訂・決定論のみ②'等)の要否。
- 試聴ページは公開済みのため、ユーザーは聴感での判断が可能。

## 8. SSOT・Git
OPEN-516・OPEN-511を更新。DECISION_LOG.mdは変更なし(Trial)。コード/証跡: `er118_fz_dialogue_context_tts_trial_01.py`、`er118_output/fz_dialogue_context_tts_trial_01/`。
