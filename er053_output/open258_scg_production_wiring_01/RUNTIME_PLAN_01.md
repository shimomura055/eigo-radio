# RUNTIME_PLAN_01 (計画のみ。本委任では未実行・課金0)

新規TTS禁止のため、保存済みMETA a2 japanese_title attempt wavを使う。wav実体は gitignored (`*.wav`) でmain作業ツリーにのみ存在:
`er019_output/family_x_audio_production_wiring_01/meta__run_regen_01/a2/narration/attempts/japanese_title_attempt1_customb8f0ff16.wav`(6.12秒、原稿「AIの電話に人間が出演。問題は「キャスト変更」のお知らせでした」、ユーザー試聴=出演)。

## (a) Production関数を保存wavに直接適用
`er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail(canonical, <実OpenAI ASRの転写>, wav)`。Primary=`routing.transcribe`(gpt-4o-mini-transcribe実呼出)+SCGのAzure(実)。
見積: OpenAI ASR 約0.02円 + Azure 6.12秒(秒切上げ7秒) 約0.31円(登録単価$1/h x 160円/USD) = 約0.33円/回。期待: Primary「出現」=TCM -> SCG実行 -> Azure「出演」 -> final_status=SECONDARY_CONFIRMED_PRIMARY_FALSE_NG。Primaryが偶然「出演」と転写したらSCGは発火しない(結果を正直に記録、attempt2/3 wavで再試行)。

## (b) 呼び出し元経路ごと発火(新規TTSなし)
調査結果: Production側にTTS出力を差し込む既存hookは**ない**(`p9a.generate_narration_snippet(tts_call_fn=...)`はあるが、repro01/n3/voice01が内部でbatch_call_fnを組み立てるためcaller側から注入できない)。Production codeにhookを追加する案は採らない(Trial実装を本番経路へ混入させない原則)。
推奨: runtime evidence script(Production外、`er053_output/open258_scg_production_wiring_01/`配下)で、`repro01.p9a.generate_narration_snippet` だけを「保存wavをout_pathへcopyしてOKを返す」関数に差し替え、他はすべて実物(実Primary ASR・実`ja_secondary`・実Azure・実`generate_a2_japanese_with_reading_safety`->`generate_a2_japanese_with_fallback`->`repro01.generate_narration_snippet_verified_strict`・`guarded_generate`・`save_tts_attempt_audio`)で`n3.generate_a2_japanese_with_reading_safety`を呼ぶ。TTS=差し替え(課金0)、ASR/Azureのみ課金。
注意: `guarded_generate`は`er011_output/attempt_history.jsonl`(追跡ファイル)に書くため、isolated worktree/一時cwdで実行するか実行後`git checkout --`で戻す。出力先out_pathは専用ディレクトリ。

## 推奨案と費用
推奨 = (a)+(b)の両方。(b)は1 attempt想定: OpenAI ASR 約0.02円 + Azure 約0.31円 = 約0.33円。(a)も約0.33円。最悪ケース((b)でPrimaryが正しく転写せずSCG未発火を3回繰り返す等、attempt上限3)でも 3 x 0.33 = 約1.0円。合計見込み 約0.7円(最悪約1.4円) < 5円。新規TTS 0。判断事項: なし(¥5以内・新規TTSなし)。
