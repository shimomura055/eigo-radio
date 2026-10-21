# TRIAL_DESIGN_01 (事前登録・生成前, 2026-10-21)
管理ID: FAMILY-Z-COMMON-DIALOGUE-VOICE-SELECTION-TRIAL-01 委任_01

## (a) TTS条件(Family Z Dialogueの実コードを再利用)
- 呼出: `er012_b_family_voices_production_01.generate_voice_body_wide_margin(text, out_path, voice)`
  (Family Z Dialogue Adv側、`er063_family_z_audio_01.py` L788-792 `dialogue()`と同一関数・style_prefix_override=None)。関数importのみ、コピーなし。
- model: `p9a.ENGLISH_MODEL_NAME` = `gemini-2.5-pro-preview-tts`(`er002_common.py` L53、実測でもmelos run_e2e_06のDialogue clipがこのmodel)。
  注記: 委任文の「backend `speech_metadata_flash_lite`」は`TTS_BACKEND`(er063 L38)でNarrator/Support系に渡される値。Dialogue経路(er063 L788-792)は
  tts_backendを渡さず上記関数が`p9a.ENGLISH_MODEL_NAME`を直接使う。比較目的は「実際のDialogue条件」なのでDialogue実経路(2.5 pro)を採用。
- style: 既定Dialogue Style `p9a.ENGLISH_STYLE_PREFIX`(=`common.build_style_prefix()`)1種類固定。速度: 生成指示なし、**減速なし**(Adv条件=生成そのまま。Std側6%減速は生成後の後処理)。
- `TTS_EXECUTION_MODE=STANDARD`(同期)。ASR検証・retry(最大3回)はProduction関数のまま。profile: 該当なし(Voice別に独立)。

## (b) 候補10名(Aoede/Charon除外)
男性的: Algieba(既存) / Schedar(既存候補) / Fenrir(新規) / Orus(新規) / Puck(新規)
女性的: Erinome(既存) / Sulafat(既存候補) / Kore(新規) / Leda(新規) / Zephyr(新規)

## (c) セリフ(全Voice共通、固有名・性別語・ネタバレなし)
- calm(落ち着いた会話・24語): I think we should take the earlier train tomorrow morning. That way we can have a quiet breakfast together before the long meeting starts.
- emotional(感情・22語): I can't believe you did that without telling me! I was so worried, and now I'm just really, really happy you're safe.

## (d) 費用見積
実測出典: `er026_output/family_z_production_e2e_01/melos/run_e2e_06/cost_log.jsonl` の gemini-2.5-pro-preview-tts 21 call(input 9,439 tok / output 1,790 tok)
× `er005_output/cost_baseline_01/pricing_snapshot.json`(Standard in $1.0/Mtok, out $20.0/Mtok)× USD_JPY 160 = 約JPY7.2/21 call = **約JPY0.34/call**(+ASR gpt-4o-mini-transcribe 数銭)。
20 clip ≒ JPY7〜15(retry込み)。Guardrail: JPY80超見込みで生成前STOP。本日既使用JPY73.47(daily_dev_cost_01実測)。

## (e) 差し替え規則
利用不可(API拒否/Voice名無効)、または平均F0の男女逆転(男性的群のF0が女性的群の最小値を上回る等、想定と逆)のVoiceは、同backendの他Voice(Aoede/Charon以外)へ差し替え、理由を記録。

## (f) 聞き分け指標
各clipの中央F0[Hz]・発話時間[s]・ファイルサイズ。F0は既存`er008_a2_timestretch_abc_10.estimate_median_f0`(autocorr、numpyのみ、新規install無し)を再利用。
