# HR_FULL_STORY_PART1_K2_01 Human Review 2 segment(AI島 Std/Adv、委任_03、2026-10-27)
公開: https://shimomura055.github.io/eigo-radio/user_test/family_x_ai_island_form_01/hr_01.html (生成: `tools/build_hr_packet_aif3_01.py`、API 0)。データ: `<run>/audit/hr_packet_data_01.json`。承認はユーザーのみ。

## 停止の事実
- 停止箇所: `--stage assemble`(rc=0だが両level `BLOCKED_STYLE_PROFILE_GATE`)。M3 Style Gate(`er019_family_x_style_profile_01.m3_assembly_gate`)が `full_story_part1_k2`(第1部2段落目)だけをBLOCK。Std: `STD_FALLBACK_USED_OR_UNKNOWN`+`LOCAL_REWRITE_RECOVERY` / Adv: `LOCAL_REWRITE_RECOVERY`。他の全segment(Std 19/Adv 18)・KP音声は status=OK、Human Review Lock 0件。
- 原因(観測): 本文の `The AIs sent to the island …` の複数形 `AIs` を音声認識が `AI` と書き起こし(ASR_VALIDATION_UNCERTAIN)。Std=標準2+fallback1の3回すべて(生成直後は二次ASR確認で通るが、6%減速の後処理後の再検証が3回とも不一致:`slowdown_attempts_log` attempt1-3)。Adv=標準2+fallback1の3回すべて不一致。→ 承認済みLocal Rewrite規則で `AIs`→Std `AI agents`(案1)/Adv `AI systems`(案2)に言い換え再生成、再検証は通過(Std 二次ASR確認/Adv 二次ASR確認)。根拠: `<run>/{a2,b1b}/audit/tts_generation_results.json` segments.full_story_part1_k2 `.local_rewrite_recovery` / `.standard_attempts_log` / `.slowdown_attempts_log`。
- 本文(承認済み)は不変。ページ表示は承認済み原稿のまま「AIs」、音声のみこの1箇所が言い換え語。

## 提示内容(新形式)
原稿 / ASR全文(一次・二次) / 相違点(1箇所) / NG理由 / 推奨音声1つ(各level 約14.3秒/13.5秒) / AI評価(意味・事実不変、聞いての最終確認は耳) / 質問1つ「この音声でよいですか?」(Take比較は求めない)。

## 承認後の手順(API 0。Gate緩和・Lock直接編集なし)
1. ユーザーの承認原文を `docs/pm/delegation_log/` に保存。
2. 正規関数 `er003_v1_n3_01_assemble.record_human_approval(<run>/<level>, "full_story_part1_k2", <元の原稿canonical_text>, "user")` を承認されたlevelで実行(承認キーは言い換え前の元原稿=entryの`canonical_text`。事前にin-memoryでM3 Gateを模擬: 承認ありで両level PASS、承認なしBLOCKを確認済み、ファイル書込なし)。
3. `--stage assemble --level both` → `--stage player --level both`(API 0)→ `tools/build_aif3_listening_page_01.py`(作成済み)→ ページ標準検査・公開確認。
4. 一方のlevelのみ不可の場合: 当該levelは別手段(本文の複数形表記への発音供給/本文変更はユーザー承認事項)をFableが判断。
