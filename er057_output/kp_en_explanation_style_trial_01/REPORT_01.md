# REPORT_01(FAMILY-X-COFFEE-KP-EN-EXPLANATION-STYLE-TRIAL-01、2026-10-12、Trial、到達Status=VALIDATED(Trial))
試聴URL: https://shimomura055.github.io/eigo-radio/user_test/coffee_kp_explanation_style_trial_01/index.html
詳細表: `MEASUREMENTS_01.md` / `measurements.json`、Prompt差分表: `prompts/prompts_kp_en_explanation_style_01.md`、実再生: `PLAY_EVIDENCE_01.md`、費用: `COST_01.md`(JPY5.353/30)。

## 設計・固定条件
- P0=現行Variant B(`KEY_PHRASE_EXPLANATION_EN`="clear, precise, at a measured pace, without dragging"。v4使用clip(kpN_explanation_en.wav)のattempt jsonのinstruction_textと一致を確認)。Voice Aoede、model gemini-3.8-flash-lite-tts、解説原稿=v4使用clip逐語、trim=KEY_PHRASE margin 0.30s、Phrase=v4のK2 clip再利用、Phrase/解説間pause=0.4s(Production assembler定数)、gain=v4と同一target_rms 0.12584規則。
- 実行はStandard同期(Productionの実行はBATCH、Style経路は同一)。P0はv4実音声(P0v4、参考)とは別に同条件で再生成し基準とした。
- 対象: KP4「to become lower in amount or level」(主、v4 clipの無音合計0.93s=先頭0.29+文中0.33+末尾0.31が5件中最大、文中最長0.33sもKP1 0.32sと並び最大)、KP1「a delay between one event and another」(2件目)。
- 3サンプル化: 解説clipは7語・約3秒で、同一PromptでもTTS生成ごとの差が大きい(P0 3回でKP4 core WPM 148〜175、文中無音計0.18〜0.51s)。単一サンプル比較は誤判定になるため、全パターン同一Promptで3回生成しその平均を併記(候補追加ではない)。r1(ページ音声)のP0比%はP0 r1が速い個体のため偏る→評価は3サンプル平均を主とする。

## 重要な所見
1. **解説clip内の無音は元々短い**: v4実clipの文中無音は最大0.33s(KP4)/0.32s(KP1)。ユーザーが聞いた「長い無音」の大半は、clip前後の固定margin(約0.3s、`KEY_PHRASE_TRIM_SAFETY_MARGIN`)+Phrase間固定pause 0.4s(`KEY_PHRASE_INTERNAL_PAUSE_SECONDS`)+前後のclip端無音で、v4実音声のKP内clip間無音は約0.9〜1.4s(final wav実測)。Style(Prompt)で変わるのは文中の短い間のみ(P0平均で0.21〜0.35s程度)。境界側の無音を減らすには別途 Trim margin/pause設計の変更が要る(本Trial範囲外、報告のみ)。
2. Styleは文中の間を減らせるが、発話速度も動く: 3サンプル平均のcore WPM P0比は-5.7〜+8.7%。P0自身のサンプル間ばらつき(±8%程度)と同程度で、±5%の差は有意とは言えない。

## 結果(3サンプル平均、P0比。表: core WPM% / 文中無音計差s / 全体WPM%) ASRは全54件verified(P8r2 1回のみ同一Promptで再生成)
| ID | 特徴 | KP4 | KP1 |
|---|---|---|---|
| P1 | 文中ポーズ抑制 | +7.5 / -0.113 / +8.9 | +4.7 / -0.013 / +3.1 |
| P2 | 句のつながり | -2.5 / -0.167 / +3.3 | +8.2 / -0.070 / +8.3 |
| P3 | 流れ(途切れない) | +8.7 / -0.213 / +13.2 | +2.7 / -0.157 / +7.1 |
| P4 | 文末処理 | +8.2 / -0.053 / +6.2 | +6.6 / +0.070 / +3.9 |
| P5 | 自然な説明口調 | -0.5 / -0.243 / +6.8 | -1.6 / -0.077 / +1.4 |
| P6 | P1+P4 | +6.2 / -0.213 / +12.0 | +7.1 / -0.037 / +6.1 |
| P7 | P2+P5 | -5.7 / -0.137 / -1.1 | +2.2 / -0.103 / +5.3 |
| P8 | P1+P4+P5 | +0.2 / -0.350(文中無音0回) / +11.8 | +7.6 / -0.157 / +11.6 |
P0基準(3平均): KP4 core 157.4 WPM、文中無音計0.35s、総3.59s / KP1 core 150.9、0.21s、総3.58s。全体WPM上昇は、coreが動かない候補(P5,P8のKP4)では無音短縮由来、core+のもの(P1,P3,P4,P6)は発話高速化を含む。
各候補の特徴・P0r2/r3等の個別値は MEASUREMENTS_01.md。audio QA: 全clip gain後peak<=0.95(<=0.98)、clipping/headroom問題なし。境界無音(解説前後)はclip端のtrimで0.4〜0.92sとサンプルごとに変動(P3 KP1で後ろ0.92s)。

## 推奨(推薦のみ、採用はユーザー判断)
- 第1候補 **P5**(自然な説明口調): 両KPで発話速度がほぼ不変(-0.5%/-1.6%)のまま文中無音が減少(KP4 -0.24s、KP1 -0.08s)。「速度は現状でよい」に最も合致。
- 第2候補 **P8**(バランス型): 文中無音の削減が最大(KP4で0回/3サンプル、KP1で0.05s)だが速度がKP1で+7.6%(ノイズ範囲)。
- 共通の注意: 効果量は小さく(文中無音で最大0.35s)、サンプルは各3。耳で判断を推奨。主訴の「長い無音」は上記所見1の境界側(固定margin+固定pause)が主因の可能性が高く、Style変更単独での改善は限定的。

## 新規仕様候補(未実装・要判断、USER_DECISION_REQUIRED)
解説clip前後の境界無音(固定margin約0.3s+pause0.4s+端)を詰める案(KP解説に限りtrim margin縮小 or 固定pause短縮)。Production assembler/trim定数の変更を伴うため本Trialでは実装せず、OPEN項目に記録。
