# FALLBACK_REAL_PROBE_01(FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_07 Step 2、2026-10-11、有料実測)

方法: `er003_fallback_real_probe_01.py`(.venv)。fallback関数を**直接呼出**(標準経路を不合格にする方式より安価)。TTS backend=`speech_metadata_flash_lite`(Production既定のBATCH実行)、model_id=`gemini-3.8-flash-lite-tts`(最新世代のFlash-Lite TTS、Production正式モデル)、ASR=`gpt-4o-mini-transcribe`(Production正式ASR)。
- J2: `n3_tts._generate_a2_japanese_minimal_instruction`(fallback_style_prefix=J2逐語)+JA全文ASR Validator
- F1_5(A2、減速連結)/F1_5(B1B): `repro01.generate_english_component_minimal_instruction`(fallback_style_prefix、発音resolver有効=Production同条件)+EN ASR Cascade
- E2_UPBEAT(Charon): `voice01.generate_charon_english`の**技術的fallback実経路**。標準1回目のTTS呼出のみ例外化(API非送信)し、fallback以降は実関数・実API
- 本文: coffee run_l3_01のEN原稿/E_master日本語から、数詞(9か月/twenty-five percent/three months)・固有名詞(ロイター/Reuters/ICE/USDA/Brazil/Vietnam)・極短文("Prices will not drop for nine months." / "値札は、まだ旅の途中？")を選択。

## 結果(8呼出、全件 (a)(b)(c) PASS)
| # | 対象(voice) | 本文種別 | fn status | 送信style=承認値(startswith) | 400/空応答 | ASR | classification | 所要(Batch) |
|---|---|---|---|---|---|---|---|---|
| 1 | J2(Aoede) | 数詞+固有名詞(ロイター/約9か月) | OK | OK(`approved_role_style:JA_J2_BRIGHT`) | 0 | PASS | PHONETIC_MATCH | 148s |
| 2 | J2(Aoede) | 極短文 | OK | OK | 0 | PASS | NORMALIZED_MATCH | 190s |
| 3 | E2_UPBEAT(Charon) | 固有名詞+数詞(Reuters/nine months) | OK(instruction_type=minimal_fallback) | OK(`approved_role_style:EN_COMMENT_E2_UPBEAT`) | 0 | PASS | EXACT_MATCH | 123s |
| 4 | E2_UPBEAT(Charon) | 短文 | OK(minimal_fallback) | OK | 0 | PASS | EXACT_MATCH | 169s |
| 5 | F1_5+減速(Aoede, A2) | 固有名詞(Brazil/Vietnam) | OK | OK(`approved_role_style:EN_FULLSTORY_F1_5`、+A2_SLOWER_PACE連結) | 0 | PASS | NORMALIZED_MATCH | 114s |
| 6 | F1_5+減速(Aoede, A2) | 数詞(three months)+US | OK | OK | 0 | PASS | NORMALIZED_MATCH | 147s |
| 7 | F1_5(Aoede, B1B) | 数詞(twenty-five percent/seven months)+USDA | OK | OK | 0 | PASS | NORMALIZED_MATCH | 97s |
| 8 | F1_5(Aoede, B1B) | 固有名詞(ICE/arabica) | OK | OK | 0 | PASS | NORMALIZED_MATCH | 136s |

- (a) 実際にTTSへ渡した`speech_metadata.style`(prompt[1]、`flw.resolve_tts_call_and_prompt`の捕捉値)が承認値で始まる(A2は承認F1.5+減速指示連結値、E2/J2/B1B F1.5は承認逐語)。旧FALLBACK style(`natural, clear, conversational`)・旧JA minimal文は送信されていない。`style_source`は全件`approved_role_style:*`。
- (b) 承認Style+本文で400/空応答/例外: 0件(raw_usage_log・例外記録とも)。
- (c) ASR合格: 8/8(SCG発火の有無: J2はscg_info記録あり、判定はPHONETIC/NORMALIZED内で合格)。
- 注意: 救済率の統計的証明は本probeの目的外(N=2×4種、全件初回で成功)。「style起因失敗時の救済が弱まる可能性」は引き続き未定量(設計書§4の留保どおり)。

## 費用(登録単価換算、`compute_cost_jpy_so_far`)
合計 **¥1.37**(TTS Batch ¥0.98 + ASR ¥0.39、8呼出)/ 上限¥6.0に対し22.8%。個別: raw_usage_log.jsonl参照。
証跡: `er053_output/coffee_new_tone_e2e_01/fallback_real_probe_01/`(probe_results.json=全呼出の本文・captured style・ASR全文、raw_usage_log.jsonl、wav 8本[git非管理])。
