# SOURCE_FIDELITY_CHECK_01 (FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_07、2026-10-29、API 0)

対象: Adv=b1b実TTS入力(b1b/audit/tts_generation_results.json の full_story_* canonical_text を連結したものが writer/r2.md 本文と一致=確認済み、引用符・空白除去で完全一致)。Std=writer/std.md(a2のTTSは未実施[Cap停止]のため**TTS入力ではなくTTS入力の元となる確定本文**での確認。a2 TTS実施後に再確認要)。原作構造の基準=SOURCE_CHECK_01.md §3。

## 1. 7証言の順序(原作 木樵り→旅法師→放免→媼→多襄丸→真砂→死霊)
| # | Std(std.md)冒頭 | Adv(r2.md)冒頭 |
|---|---|---|
| 1 woodcutter | "I found him in the bushes this morning," the woodcutter said. | "One stab in the chest. That's what I saw," said the woodcutter. |
| 2 monk | "I saw the couple yesterday at noon," the traveling monk said. | "I passed them yesterday at noon," said the monk. |
| 3 constable | "I caught the famous bandit Tajomaru near the bridge," the constable said. | "I caught Tajomaru, the famous bandit, by the stone bridge," said the constable. |
| 4 old woman | "Takehiro, a kind samurai, married my daughter Masago," the old woman said. | "Takehiro was my daughter's husband," said the old woman. |
| 5 Tajomaru | "I killed him fairly," Tajomaru said. | "Yes, I killed him," said Tajomaru. |
| 6 Masago | "I crawled towards my husband," Masago said at the temple. | "I crawled towards my husband after the bandit left," said Masago at the temple. |
| 7 Takehiro | "I heard him speaking kindly to her," Takehiro's spirit said through a medium. | "I heard the bandit comforting her," said Takehiro's spirit through the medium. |
→ 両levelとも7証言・原作順。地の文(語り手)の追加なし(speech tagのみ)。

## 2. 3つの矛盾する証言(死因の主張が両立しない)
- Tajomaru: Std "I freed him for a fair sword fight. Twenty-three blows—no other man had lasted twenty! She was gone when he fell." / Adv "We fought fairly, sword against sword. Twenty-three strokes! ... When he fell, she was gone."(刀の決闘)。
- Masago: Std "‘Kill me,’ he said, so I stabbed him." / Adv "His lips moved: ‘Kill me.’ So I stabbed him."(自分が小刀で刺す)。
- Takehiro: Std "I got up beside the cedar and picked up her small dagger... I pushed it into my own chest." / Adv "I rose from the cedar and picked up the small dagger she had dropped. I stabbed myself in the chest."(自害)。
- 3証言は互いに両立せず、作中に裁定・解決の記述はない。

## 3. 結末(見えない手が小刀を抜く→闇へ沈む)
- Std: "Someone came slowly towards me on silent feet. A hand I could not see quietly pulled the dagger from my chest. / “I sank into the darkness and never came back.”"
- Adv: "Then someone crept towards me on soft feet. An unseen hand quietly drew the dagger from my chest. / “I sank for ever into the darkness.”"
- 抜いた者の特定・説明なし。原作最終段(SOURCE_CHECK_01.md §4)と一致。

## 4. 評決/真犯人/決定的証拠の創作なし
- 両levelとも、検非違使・語り手による裁定、真犯人の指名、新規の決定的証拠(目撃者・遺留品による確定)の記述なし(地の文なし)。外部証言の事実(胸の傷・縄と櫛・弓)は原作の証言1〜3に対応。
- Preview/Comment(b1b実音声原稿): Preview「A death in a mountain thicket begins this short, unsettling story. As the mystery unfolds, consider what it takes to understand what really happened.」/ Comment 1-3は各セクションまでの出来事の確認と問いかけのみ(comment_3「Tajomaru says he freed Takehiro, and they fought with swords. What does Masago say happened after the bandit left?」)。後続証言の内容・真相の先取りなし。Std側Preview/Commentはa2 TTS未実施のため未確認。

## 5. Std性表現の非グラフィック化維持
- Std: "The wind lifted her face covering, and I wanted her. I promised him buried treasure and led him into the bushes... She fought with her dagger."(暴行の描写・直接語なし。std.md調整版)。
- Adv: "A breeze lifted her veil, and I wanted her... She fought with her dagger, but I took her by force."(Seedの「off the page・非グラフィックな1句」範囲。描写なし)。
- 自殺・刺傷表現は原作の筋に必要な範囲(stabbed / dagger / chest)で、流血・身体描写の詳細化なし。Std/Advとも非グラフィックを維持。

## 結論
b1b: 実TTS入力で上記4点OK、Preview/Comment先取りなし。a2: 確定本文で同OK、**a2のTTS入力(Preview/Comment含む)での最終確認は未実施**。

## 委任_12(2026-10-29、API 0): a2(Std) TTS入力の最終確認(委任_07で未実施だった項目)
- Std TTS入力: a2/audit/tts_generation_results.json の full_story_* 22 clip の canonical_text(連結)= writer/std.md 本文と一致(引用符・空白除去後、差は見出し`# The Thicket`の11文字のみ)。Adv(b1b)も同法で writer/r2.md と一致(差は見出しのみ)。
- confirmed_selection(a2): `a2/audit/confirmed_selection.json` sha256 9bf2f55ea955784d…(`key_phrases/a2/confirmed_selection.json`と同一)。KP=on silent feet / constable / drown(vocab一致、kp_selection_verified ok)。Adv KP=cold contempt / on soft feet / medium。
- Voice map(voice_assignment.json、Z APPROVED 2026-10-23): woodcutter=Algieba / monk=Schedar / constable=Fenrir / old_woman=Zephyr / tajomaru=Orus / masago=Kore / takehiro=Puck、ナレーター=Aoede(Std)・Charon(Adv comment/preview)。Std comment_3(日本語ナレ)=Aoede、part1_c3=Algieba(きこり、ユーザー採用#2)。
- 7証言・3矛盾証言・結末・評決なし・非グラフィック(委任_07 §1〜5)はStd最終確定本文でも不変(std.md/r2.md無変更、TTS入力一致を上記で確認)。

## 委任_13(2026-10-29、API 0): 本文差分と忠実性(修正①②)
- **本文(writer/std.md・r2.md)は一字も変更していない**(std.md sha 4f7fb3dc… / r2.md 4573e7c9…、provenance `std_sha256`/`adv_final_sha256` 不変)。引用符の扱いは本文ではなく処理側(閉じ引用符の無い発言の認識=`er062 quote_spans`)で解決したため、『修正前後の本文差分=0バイト』。7証言の順序・3矛盾証言・結末・評決なし・非グラフィックの記述(§1〜5)は修正前後で完全に不変。
- 閉じ引用符の無い発言(段落末を閉じず次段落を“で再開する慣習)の一覧と話者(LLM判定=決定論/文脈と不一致0): Std q4_2 多襄丸「The wind lifted her face covering… She fought with her dagger.」/q6_2・q7_1 真砂/q9_2・q10_1・q11_1・q12_1 武弘、Adv q4_2 多襄丸「But listen before you call me a coward!…」/q6_2・q7_1 真砂/q9_2・q10_1・q11_1・q12_1 武弘。他4証言者(木樵り・旅法師・放免・媼)は全引用が閉じており同種問題なし。
- Std KP: `bandit`(S8『I caught the famous bandit Tajomaru near the bridge』・真砂証言『The bandit had left him tied up』に出現、全Gate PASS・gloss=盗賊/ALIGNED)。constableは追加解説。Adv KPは cold contempt / on soft feet / medium(不変)。
