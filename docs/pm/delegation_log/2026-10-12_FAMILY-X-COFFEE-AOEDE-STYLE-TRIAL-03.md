# FAMILY-X-COFFEE-AOEDE-STYLE-TRIAL-03(2026-10-12、Status=VALIDATED、Trial限定、Production不採用、USER_DECISION_REQUIRED=ユーザー試聴待ち)

## ユーザー指示(要旨)
Coffee v3 Full Story(Aoede+PD8)について「速度は維持/抑揚をもう少し/もう少し元気/もう少しクリア」を目指すStyle改善Trial。現行PD8=P0(既存音声再利用)+新規P1〜P8(P1抑揚少し/P2抑揚中程度/P3明るさ少し/P4明るさ中程度/P5明瞭さ/P6抑揚+明瞭/P7明るさ+明瞭/P8バランス)。固定=Aoede、gemini-3.8-flash-lite-tts、原稿・生成条件はStyle以外同一、短い共通サンプルのみ(全編生成・Assembly禁止)。速度機械測定(総秒/全体WPM/発話WPM/P0比%/無音)必須、Primary ASR・peak/headroom/無音のQA、9パターン連続比較の試聴ページ。最良Styleの正式決定はしない。費用上限JPY40。Coffee v3完成音声/Production Prompt/Master Store不変。OPEN-298/299/300は未解決のまま。

## 結果(非エンジニア向け)
- 試聴URL: https://shimomura055.github.io/eigo-radio/user_test/coffee_aoede_style_trial_03/index.html (公開URLでPlaywright実再生9/9成功)
- 試した内容: Coffee v3 AdvancedのPart1(約46秒、131語)を共通サンプルに、現行Style(P0)の文はそのまま、その後ろに「抑揚/明るさ/明瞭さ」の一文を足した8通り(P1〜P8)を作成。「ゆっくり(unhurried)」の指示は全て残し、速度を上げやすい語(lively等)は使っていない。
- 速度: 全体WPMは全候補P0(169.8)の±5%以内(最大P7 -4.7%、P3 +4.4%)。P5だけ発話WPMが+6.0%(500ms基準)で5%超。詳細は er057_output/aoede_style_trial_03/REPORT_03.md の表。
- 品質(機械指標のみ): Primary ASR 全9本OK(P2のみ初回UNCERTAINで1回再生成)、clipping 0、headroom 0.93dB以上。読み間違い・不自然な強調は機械では断定できず、聴感確認はユーザー試聴に委ねる。
- 有望候補(推薦のみ): 速度維持の観点でP1・P2・P4・P6、複合の比較にはP8。試聴優先 P8→P2→P4→P6。P5は発話が速め、P7は遅めの傾向。
- 実費: 約JPY12.2/上限40(TTS 10.02+ASR推定2.14、model=gemini-3.8-flash-lite-tts、Production同一モデル=例外種別2)。
- Status: VALIDATED(Trialのみ、Production不採用、APPROVED_FOR_PRODUCTION未取得)。
- 未決事項: ユーザー試聴評価(OPEN新規)、Production採用可否・Coffee v3差替・他Family横展開は未決定。
- 証跡: er057_output/aoede_style_trial_03/(prompts/、measurements.json、MEASUREMENTS_03.md、REPORT_03.md、PLAY_EVIDENCE_01.md、generation_log_03.jsonl、COST_ESTIMATE_03.md)。
- raw URL: https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er057_output/aoede_style_trial_03/REPORT_03.md
