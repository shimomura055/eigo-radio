# SELECTION_01 — 対象セリフ8件(FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_01、API 0)

- 出典: `er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01/segment_plan_b1b.json`(Adv)。機械可読版=`er118_output/fz_dialogue_context_tts_trial_01/phase0/selection.json`(`py er118_fz_dialogue_context_tts_trial_01.py plan`で再生成可)。
- **選定方針**: Advの全dialogue clip(8件)を採用。8件は指示の下限だが、Della/Jim/Madameの3話者と指示の全カテゴリ(喜び・驚き/悲しみ・不安/ためらい・戸惑い/ささやき・静かな発言/感情が変化する場面/相手の発言を受けた返答)を網羅でき、取りこぼしも無い(testで『Adv dialogue全件=対象』を検証)。Std(a2)は文面がAdvの言い換えでカテゴリが重複するため補わない(機械的に件数を増やさない)。
- 文脈の範囲(決定論): 直前セリフ最大2・直後セリフ最大1(clip距離4以内、間の地の文が40語超=時間経過のセリフは除外)、直前/直後の地の文各最大2文、演出語を含む文(語彙: whisper/softly/gently/smil*/tears/rushed/…)。全て`segment_plan`の逐語(testで検証)。
- 既存①音声のgainは、Production組立が最終音声(速度加工後)へ適用した値(`b1b/assembly/timeline.json gain_report`、target_rms=0.08425)。本Trialの聴き比べは速度加工前の原音を同じtarget_rmsへ個別gainして揃える。

## 1. `full_story_part2_c2` — della / Voice Zephyr
- 英文: `"Will you buy my hair?"`
- 網羅カテゴリ: 悲しみ・不安 / ためらい・戸惑い
- 場面の状況(日本語): クリスマス前日。夫Jimへの贈り物を買うお金がなく、自慢の長い髪を売ろうと髪飾り店の前で息を整え、店の女主人に切り出す場面。
- 選定理由: 不安とためらいを抱えた切り出し。前後に会話が無く、直前の地の文(息を整える)だけが手掛かり。
- 直前のセリフ: なし(範囲内に無い)
- 直後のセリフ: the hair-shop owner: "Twenty dollars."
- 直前の地の文: Outside a hair-goods shop, she paused just long enough to catch her breath.
- 直後の地の文: The owner lifted the heavy waves.
- 演出語を含む文(原文逐語・決定論抽出): `Outside a hair-goods shop, she paused just long enough to catch her breath.`
- 想定する感情・演出(原文の根拠): 感情・心理状態の文はPhase 1のLLM出力(根拠引用は上の原文に逐語一致必須。DESIGN_01 §3)。Phase 0では創作しない。
- ①既存音声(原音): `er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01/b1b/narration/full_story_part2_c2_original.wav` sha256=`4ac552cedd9a2eb408de8e19488650f6947583744e081b6c3e79d3c44ec27ce7` / 最終音声 sha256=`9218908a924326e3ce5d79b452cfeb4a9fe8d7c5771372b31f6f831efe2200c3`(gain=0.8119、atempo=1.06)
  - ASR: `Will you buy my hair?` / judge=PASS(NORMALIZED_MATCH) / attempts=1 / model=gemini-2.5-pro-preview-tts / mode=STANDARD
  - 機械指標(原音): 1.651s / RMS -19.78 dBFS / F0中央値 190.5 Hz / F0幅(p10-p90) 11.94半音 / 最長中間無音 0.0s

## 2. `full_story_part2_c4` — madame / Voice Kore
- 英文: `"Twenty dollars."`
- 網羅カテゴリ: 相手の発言を受けた返答 / 感情を抑えた事務的な発言(対照)
- 場面の状況(日本語): 女主人がDellaの豊かな髪を持ち上げ、買い取り額を告げる場面。
- 選定理由: Madame(別Voice)。感情の明記が無い台詞が、文脈追加で『過剰に感情的』にならないかの対照。直前のDellaの問いへの返答。
- 直前のセリフ: Della: "Will you buy my hair?"
- 直後のセリフ: Della: "Cut it quickly, please."
- 直前の地の文: The owner lifted the heavy waves.
- 直後の地の文: なし
- 演出語を含む文(原文逐語・決定論抽出): なし(対照)
- 想定する感情・演出(原文の根拠): 感情・心理状態の文はPhase 1のLLM出力(根拠引用は上の原文に逐語一致必須。DESIGN_01 §3)。Phase 0では創作しない。
- ①既存音声(原音): `er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01/b1b/narration/full_story_part2_c4_original.wav` sha256=`79ccf6a20ade3eb136ebd0e59c5190450b625d714814bc38b37b0248d21c6d72` / 最終音声 sha256=`c1d8ef6c09f7f0b5eb33a08f79344fbec5792e07989420df2fecb9342997192e`(gain=0.8481、atempo=1.06)
  - ASR: `twenty dollars` / judge=PASS(ORTHOGRAPHIC_EQUIVALENT_MATCH) / attempts=1 / model=gemini-2.5-pro-preview-tts / mode=STANDARD
  - 機械指標(原音): 1.651s / RMS -19.99 dBFS / F0中央値 179.1 Hz / F0幅(p10-p90) 8.34半音 / 最長中間無音 0.0s

## 3. `full_story_part2_c5` — della / Voice Zephyr
- 英文: `"Cut it quickly, please."`
- 網羅カテゴリ: ためらい・戸惑い / 感情が変化する場面 / 相手の発言を受けた返答
- 場面の状況(日本語): 金額を聞いたDellaが、迷う前に決めてしまおうと、すぐ切ってほしいと頼む場面。
- 選定理由: ためらいを振り切る決意。直前の金額提示への返答。
- 直前のセリフ: Della: "Will you buy my hair?" ; the hair-shop owner: "Twenty dollars."
- 直後のセリフ: なし(範囲内に無い/時間経過で除外)
- 直前の地の文: なし
- 直後の地の文: At the first touch of the scissors, Della shut her eyes. For two hours afterward, she hurried from shop to shop.
- 演出語を含む文(原文逐語・決定論抽出): `At the first touch of the scissors, Della shut her eyes.` / `For two hours afterward, she hurried from shop to shop.`
- 想定する感情・演出(原文の根拠): 感情・心理状態の文はPhase 1のLLM出力(根拠引用は上の原文に逐語一致必須。DESIGN_01 §3)。Phase 0では創作しない。
- ①既存音声(原音): `er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01/b1b/narration/full_story_part2_c5_original.wav` sha256=`c39796dfbe788e4efdf84d36d30aac8a3691c1b61a027b439ec937fd96483a0f` / 最終音声 sha256=`af426be97ef28571fb12991509bfb98def6472b377cbb4bf0f3abe5c5f8d104c`(gain=0.7319、atempo=1.06)
  - ASR: `Cut it quickly, please.` / judge=PASS(NORMALIZED_MATCH) / attempts=1 / model=gemini-2.5-pro-preview-tts / mode=STANDARD
  - 機械指標(原音): 2.531s / RMS -18.66 dBFS / F0中央値 211.5 Hz / F0幅(p10-p90) 13.45半音 / 最長中間無音 0.0s

## 4. `full_story_part2_c7` — della / Voice Zephyr
- 英文: `"Please let him still think I'm pretty,"`
- 網羅カテゴリ: ささやき・静かな発言 / 悲しみ・不安
- 場面の状況(日本語): 髪を売って贈り物の鎖を買い、帰宅。短くなった髪を気にして鏡に戻りながら、Jimが帰る前に小さく祈る場面(直後の地の文に『ささやいた』)。
- 選定理由: 先行調査(INVESTIGATION_01)で、ささやきの演出が地の文(別clip・別Voice)にあるため反映されない可能性が指摘された代表例。
- 直前のセリフ: なし(範囲内に無い)
- 直後のセリフ: Della: "I sold it, Jim. I couldn't let Christmas come without giving you something. It'll grow again!"
- 直前の地の文: By seven, dinner was nearly ready. Della had curled her short hair, but she kept returning to the mirror.
- 直後の地の文: she whispered.
- 演出語を含む文(原文逐語・決定論抽出): `Della had curled her short hair, but she kept returning to the mirror.` / `she whispered.`
- 想定する感情・演出(原文の根拠): 感情・心理状態の文はPhase 1のLLM出力(根拠引用は上の原文に逐語一致必須。DESIGN_01 §3)。Phase 0では創作しない。
- ①既存音声(原音): `er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01/b1b/narration/full_story_part2_c7_original.wav` sha256=`be6f7d0280bb406021f5157c20330467b592b0a8394de41fd68d7c81cf748ae9` / 最終音声 sha256=`4f67d2078365a46fcfe98687c8aa59e5d038846283fc018f49ce64e8443bff50`(gain=0.5687、atempo=1.06)
  - ASR: `Please let him still think I'm pretty.` / judge=PASS(NORMALIZED_MATCH) / attempts=1 / model=gemini-2.5-pro-preview-tts / mode=STANDARD
  - 機械指標(原音): 2.571s / RMS -16.53 dBFS / F0中央値 214.3 Hz / F0幅(p10-p90) 7.29半音 / 最長中間無音 0.0s

## 5. `full_story_part3_c2` — della / Voice Zephyr
- 英文: `"I sold it, Jim. I couldn't let Christmas come without giving you something. It'll grow again!"`
- 網羅カテゴリ: 感情が変化する場面 / 悲しみ・不安 / 喜び・驚き
- 場面の状況(日本語): 帰ってきたJimが短い髪を見て立ち尽くす。Dellaは駆け寄り、髪を売った理由を打ち明ける場面。
- 選定理由: 1セリフ内で動揺→必死の説明→前向きな一言(It'll grow again!)と感情が動く最長のセリフ。
- 直前のセリフ: Della: "Please let him still think I'm pretty,"
- 直後のセリフ: Della: "My hair grows quickly."
- 直前の地の文: His eyes stayed on her hair. Della rushed toward him.
- 直後の地の文: He put his arms around her. Then he gave her a package.
- 演出語を含む文(原文逐語・決定論抽出): `His eyes stayed on her hair.` / `Della rushed toward him.`
- 想定する感情・演出(原文の根拠): 感情・心理状態の文はPhase 1のLLM出力(根拠引用は上の原文に逐語一致必須。DESIGN_01 §3)。Phase 0では創作しない。
- ①既存音声(原音): `er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01/b1b/narration/full_story_part3_c2_original.wav` sha256=`4689f7f133f4cf441da49233f2b835b421ef43f9174fb44e840820d22f24050e` / 最終音声 sha256=`471e27077229d9ad1b052ef0b849e83d227cec7406b959bfb4de89cc97c3abdb`(gain=0.8305、atempo=1.06)
  - ASR: `I sold it, Jim. I couldn't let Christmas come without giving you something. It'll grow again.` / judge=PASS(NORMALIZED_MATCH) / attempts=1 / model=gemini-2.5-pro-preview-tts / mode=STANDARD
  - 機械指標(原音): 7.891s / RMS -19.88 dBFS / F0中央値 275.9 Hz / F0幅(p10-p90) 13.89半音 / 最長中間無音 0.71s

## 6. `full_story_part3_c4` — della / Voice Zephyr
- 英文: `"My hair grows quickly."`
- 網羅カテゴリ: 悲しみ・不安 / 喜び・驚き / 感情が変化する場面
- 場面の状況(日本語): Jimから贈られたのは、ずっと欲しかった櫛。髪を売った今は使えない櫛を胸に抱き、涙ながらに微笑んで言う場面(直前の地の文に『smiling through tears』)。
- 選定理由: セリフ本文に感情語が無い短文(事実陳述)。涙ながらの笑顔という感情が地の文にしか無い、文脈の効果が最も出やすい例。
- 直前のセリフ: Della: "I sold it, Jim. I couldn't let Christmas come without giving you something. It'll grow again!"
- 直後のセリフ: Della: "Look! Isn't it perfect? Give me your watch."
- 直前の地の文: Inside were the tortoise-shell combs she had so often admired in a shop window. She held them against her chest, smiling through tears.
- 直後の地の文: Suddenly remembering, she brought out the chain.
- 演出語を含む文(原文逐語・決定論抽出): `She held them against her chest, smiling through tears.` / `Suddenly remembering, she brought out the chain.`
- 想定する感情・演出(原文の根拠): 感情・心理状態の文はPhase 1のLLM出力(根拠引用は上の原文に逐語一致必須。DESIGN_01 §3)。Phase 0では創作しない。
- ①既存音声(原音): `er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01/b1b/narration/full_story_part3_c4_original.wav` sha256=`c90a9baf76b14fcb51ee01c999b0d5a8e2d482b5c08a220978eeea0ca80dd3ef` / 最終音声 sha256=`b3ad55ca221b7324a39ede32a04846ff03c11d55f6385d1d994dc1efb2eb0dcc`(gain=0.6452、atempo=1.06)
  - ASR: `My hair grows quickly.` / judge=PASS(NORMALIZED_MATCH) / attempts=1 / model=gemini-2.5-pro-preview-tts / mode=STANDARD
  - 機械指標(原音): 2.081s / RMS -17.7 dBFS / F0中央値 230.8 Hz / F0幅(p10-p90) 10.88半音 / 最長中間無音 0.0s

## 7. `full_story_part3_c6` — della / Voice Zephyr
- 英文: `"Look! Isn't it perfect? Give me your watch."`
- 網羅カテゴリ: 喜び・驚き
- 場面の状況(日本語): 気を取り直したDellaが、Jimのために買った時計の鎖を見せ、時計を貸してほしいと言う場面。
- 選定理由: 喜び・高揚。『Look!』『Isn't it perfect?』と感情語が本文にもあり、文脈追加が過剰にならないかの確認にもなる。
- 直前のセリフ: Della: "My hair grows quickly."
- 直後のセリフ: Jim: "I sold the watch to buy your combs."
- 直前の地の文: Suddenly remembering, she brought out the chain.
- 直後の地の文: Jim sat down and smiled gently.
- 演出語を含む文(原文逐語・決定論抽出): `Suddenly remembering, she brought out the chain.` / `Jim sat down and smiled gently.`
- 想定する感情・演出(原文の根拠): 感情・心理状態の文はPhase 1のLLM出力(根拠引用は上の原文に逐語一致必須。DESIGN_01 §3)。Phase 0では創作しない。
- ①既存音声(原音): `er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01/b1b/narration/full_story_part3_c6_original.wav` sha256=`4253ce85043105ca81e46b9fbc4a6ae8848d74adfe873e91b2acd1dec28fa2b7` / 最終音声 sha256=`8e491b58f5d87c9c4c13e56f097aba16d6a19a816847e03ffb5c4305ab9ba1f3`(gain=0.669、atempo=1.06)
  - ASR: `Look, isn't it perfect? Give me your watch.` / judge=PASS(NORMALIZED_MATCH) / attempts=1 / model=gemini-2.5-pro-preview-tts / mode=STANDARD
  - 機械指標(原音): 4.041s / RMS -17.92 dBFS / F0中央値 282.4 Hz / F0幅(p10-p90) 8.6半音 / 最長中間無音 0.46s

## 8. `full_story_part3_c8` — jim / Voice Algieba
- 英文: `"I sold the watch to buy your combs."`
- 網羅カテゴリ: ささやき・静かな発言 / ためらい・戸惑い / 相手の発言を受けた返答
- 場面の状況(日本語): Jimが腰を下ろして穏やかに微笑み、Dellaの『時計を貸して』に応えて、櫛を買うために時計を売ったと静かに告げる場面。
- 選定理由: Jim(男声・別Voice)の静かな告白。直前のDellaの発言への返答で、穏やかな微笑みという演出が地の文にある。
- 直前のセリフ: Della: "My hair grows quickly." ; Della: "Look! Isn't it perfect? Give me your watch."
- 直後のセリフ: なし(範囲内に無い/時間経過で除外)
- 直前の地の文: Jim sat down and smiled gently.
- 直後の地の文: Della sat beside him and took his hand. Her hair was gone; the combs could not hold it.
- 演出語を含む文(原文逐語・決定論抽出): `Jim sat down and smiled gently.`
- 想定する感情・演出(原文の根拠): 感情・心理状態の文はPhase 1のLLM出力(根拠引用は上の原文に逐語一致必須。DESIGN_01 §3)。Phase 0では創作しない。
- ①既存音声(原音): `er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01/b1b/narration/full_story_part3_c8_original.wav` sha256=`a3defd18ae7ca199046d211a3a8726d73bc347248a1e7a4cc58920eb607cbbef` / 最終音声 sha256=`44271952f1eec0a4a9e40842eb46185522e9db75eb5c8d50fd7624a2d03f716f`(gain=0.7115、atempo=1.06)
  - ASR: `I sold the watch to buy your combs.` / judge=PASS(NORMALIZED_MATCH) / attempts=1 / model=gemini-2.5-pro-preview-tts / mode=STANDARD
  - 機械指標(原音): 3.331s / RMS -18.6 dBFS / F0中央値 126.6 Hz / F0幅(p10-p90) 15.59半音 / 最長中間無音 0.0s

## カテゴリ網羅表
- 悲しみ・不安: part2_c2, part2_c7, part3_c2, part3_c4
- ためらい・戸惑い: part2_c2, part2_c5, part3_c8
- 相手の発言を受けた返答: part2_c4, part2_c5, part3_c8
- 感情を抑えた事務的な発言(対照): part2_c4
- 感情が変化する場面: part2_c5, part3_c2, part3_c4
- ささやき・静かな発言: part2_c7, part3_c8
- 喜び・驚き: part3_c2, part3_c4, part3_c6

注: 機械指標のF0は簡易自己相関(粗い)。聴感の評価ではない。
