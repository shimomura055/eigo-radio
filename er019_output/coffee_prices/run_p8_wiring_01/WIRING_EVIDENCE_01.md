# WIRING_EVIDENCE_01(FAMILY-X-COFFEE-P8-FINAL-AUDIO-AND-PRODUCTION-WIRING-01 委任_03、2026-10-12)

Status: runtime evidence取得済み。**PRODUCTION_WIRED判定はFable/ユーザー確認待ち(本書は判定しない)**。本episodeは配線証跡であり、Coffee v4(01A成果物)を置換しない(M6)。試聴ページなし。

## 0. 実行条件
- 正式Production runner `er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_l3_01 --out-dir er019_output/coffee_prices/run_p8_wiring_01 --style-profile coffee_p8 --tts-backend speech_metadata_flash_lite --stage tts` を `--level b1b` -> `--level a2` の順、続けて `--stage assemble --level both`(`.env`はscript内load_dotenvのみ、`--budget-jpy 30`)。
- 新out_dir(実行前に `tts_generation_results.json`/Review Lock/承認ファイルなし、dry-runのplan/parts/style_profile.jsonのみ)。scaffold成果物は `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_l3_01` から出所記録付き明示コピー(`audit/scaffold_copy_provenance.json`、26 file sha256、LLM scaffold再実行なし=費用0。Review Lock/承認/attempt/narrationはコピーせず)。
- 使用モデル(最新原則の報告): TTS = `gemini-3.8-flash-lite-tts`(Aoede、raw_usage_logのmodel_idで全Gemini call実測。承認済み正式backend、最新世代)、ASR = `gpt-4o-mini-transcribe`(既存Production ASR、変更なし)。
- **重要な前提差異(要Fable判断)**: Coffee v3/v4のFull Story原稿("Beans cost less now!"系。`er057_tone_trial_final_build_03.jobs_def()`、`er057_output/coffee_final_listening_tone_trial_01/part_45/evidence_snapshot/*/parts.json`)は、現行の `er019_output/coffee_prices/run_l3_01/{a2,b1b}/article.md`(委任_02で指定したscaffold元 `family_x_audio_production_wiring_01/coffee_prices__run_l3_01` も同じ)の原稿("Coffee prices are falling! Great!"系)と**別の原稿**だった。Production runnerは `source_dir/<level>/article.md` から読むため、本runは現行run_l3_01原稿で実施した。配線の全Checklist(sha/Gate/retry/resume/regen/ASR)は原稿非依存で成立するが、WPM比較(4節)はv4と**原稿が異なる**ため参考値。v4と同一原稿での再現が必要なら、v3原稿用のsource_dir(article.md+Ledger)の用意が前提(別委任・追加約JPY12)。

## 1. Full Story segment x 経路 x sha x 判定
| level | segment | 経路 | TTS生成回数 | style_base_sha256(hint追記前) | 最終style全文sha256 | hint/cache_hits | instruction_type | ASR判定 | model | fallback/LR |
|---|---|---|---|---|---|---|---|---|---|---|
| Adv(b1b) | part1 | 初回 | 1 | 3eadf4f6==P8 | 3eadf4f6==P8 | False/0 | english_style_prefix_wide_margin | NORMALIZED_MATCH | gemini-3.8-flash-lite-tts | なし |
| Adv(b1b) | part2 | 初回 -> **regen(3節)** | 1 +1 | 3eadf4f6==P8 | 3eadf4f6==P8 | False/0 | 同上 | NORMALIZED_MATCH | 同上 | なし |
| Adv(b1b) | part3 | 初回 | 1 | 3eadf4f6==P8 | 3eadf4f6==P8 | False/0 | 同上 | NUMERIC_EQUIVALENCE_MATCH | 同上 | なし |
| Std(a2) | part1 | 初回 + **外側減速loop retry(attempt2,3)** | **3** | 3eadf4f6==P8 | 3eadf4f6==P8(attempt style_prefix.len=402) | False/0 | (Std custom) | NORMALIZED_MATCH(attempt1,2は減速後TRUE_CONTENT_MISMATCHでSTOPPED、attempt3でOK) | 同上 | なし |
| Std(a2) | part2 | 初回 | 1 | 3eadf4f6==P8 | 3eadf4f6==P8 | False/0 | 同上 | NORMALIZED_MATCH | 同上 | なし |
| Std(a2) | part3 | 初回 | 1 | 3eadf4f6==P8 | 3eadf4f6==P8 | False/0 | 同上 | NUMERIC_EQUIVALENCE_MATCH | 同上 | なし |
- P8 sha256 = `3eadf4f6f788b822c90f17ba56d893bccb5fab840358cf48845472cd4f4e5595`、長さ402。`audit/style_profile.json`: profile_id=coffee_p8、overridden_roles=["FULL_STORY"]、std_append_slower_instruction=false(S1: Std逐語+6%減速は音声後処理のみ、`slowdown_pct_actual` 5.966〜5.976%)。
- **S2(Ledger hit 0件)実測**: 全6 segmentで `hints_applied=False`、`cache_hits=[]` -> hintなし最終sha==P8を直接確認。
- **per-call照合**(`audit/wiring_evidence_data_pre_regen.json`/`post_regen.json`、`raw_usage_log.jsonl` の全Gemini TTS call 36件): 実送信styleのhead200(P8の先頭200字。raw_usage_logのstyleは200字切詰め記録のため、全文shaは結果JSONのstyle_prefixで補完)がFull Story 9 call(初回6 + Std part1のretry 2 + regen 1)の**全てでP8一致**。**Full Story以外の全role(topic_intro/preview/comment/IOL/KP等、27 call)でP8は使われていない**(overridden_roles=FULL_STORYのみ、他role影響0)。
- 全Gemini call model_id = gemini-3.8-flash-lite-tts(実測)。

## 2. Checklist項目別
| # | 項目 | 結果 | 根拠 |
|---|---|---|---|
| 4 | 初回経路の実segment sha一致 | **充足** | 上表(Adv3 + Std3) |
| 4 | retry経路のsha一致 | **部分充足**: Std外側減速loopのretry(attempt1,2,3)は全てP8のcallで充足。標準retry(内側attempt2以降)は今回未発生のため未実測 | Std part1 TTS 3 call全てP8 head200一致、attempt3のstyle_prefix sha256==P8 |
| 4 | regen経路の実segment sha一致 | **充足** | 3節。b1b part2のみ再生成、再生成後 style_profile/style_prefix==P8、他9 segment+KP5は再利用 |
| 5 | fallback/LRの扱い(M3) | **Gateの正常通過(PASS)を実測**。fallback/LR発生時のBLOCK動作は今回**発生せず未実測**(test 32件でBLOCK各ケースはPASS済み) | `a2/audit/style_profile_gate.json`、`b1b/audit/style_profile_gate.json`: status=PASS、checked=part1〜3、blocked=[]。P8対象6 segmentでminimal_fallback/LR/Std fallback_used=Trueなし。なお非対象role(Std japanese_title)でminimal_fallbackが発生したがM3 Gate対象外のためGateは影響を受けず(過剰BLOCKなし) |
| 6 | resume(tts stage再実行で再利用・再課金なし) | **充足** | b1bでtts stage再実行: 3.8秒、raw_usage_log 86行->86行(増加0)、費用12.24->12.24、10 segment全て `reused_from_previous_run=True`、KP explanation5も再利用 |
| 7 | Std逐語+6%減速(実音声) | **充足** | Std Full Story 3 segment: style_prefix.len=402/sha==P8、減速指示の連結なし、`slowdown_applied=True`、`slowdown_pct_actual` 5.966〜5.976%、減速後ASR判定 NORMALIZED_MATCH/NUMERIC_EQUIVALENCE_MATCH |
| 9 | Audio Validation Gate/ASR/duration(既存閾値) | **充足** | 全6 segmentでPrimary ASR verified(Std part1は減速後ASRで2回TRUE_CONTENT_MISMATCH->3回目でOK=既存retry機構が上限3内で動作)、repetition QA flagged=False、clipping=False。assemble: Std 324.026s peak 0.8369 / Adv 317.95s peak 0.9177、headroom_valve未発動(`run_summary_assemble.json`) |
| 10 | runtime evidence(実TTS、新out_dir、両level) | **実施済み**(本書) | 費用は5節 |
| M3 | Assembly前Gate | **PASS(両level、regen後のb1b再assembleも)** | style_profile_gate.json |
| 8 | default非影響 | **充足** | `er019_family_x_style_profile_01_test_01` 32件OK(本run後の再実行、API 0、defaultバイト同一性test含む) |
| 11/12 | SSOT/Git、人間承認(Production採用) | SSOT記録済み/**人間のみ** | DECISION_LOG/OPEN_ITEMS |

## 3. 再生成(regeneration)実測(1 segmentのみ)
- 対象: Adv(b1b) full_story_part2。実行前に元wavを `audit/regen_evidence/b1b_full_story_part2_before_regen.wav`、元結果JSONを `audit/regen_evidence/b1b_tts_generation_results_before_regen.json` に退避。
- 方式: 人間承認API `approve_regenerate` は呼ばず、同等の技術経路を使用: 該当segmentのwavを退避(`_removed_to_force_regen.wav`)して `_generate_or_reuse` のcache missを起こし、同コマンドで `--level b1b --stage tts` を再実行。Review Lock状態はRESOLVED/OK(`er011` check_before_generation の仕様上ブロックなし)のため、人間承認の代行は発生していない。
- 結果: part2のみ `REGENERATED`、他は再利用。再生成segmentの `style_base_sha256`==P8、最終style_prefix全文sha256==P8、`raw_usage_log` 追加2行(gemini 1 + ASR 1)のstyle head200==P8、model gemini-3.8-flash-lite-tts、ASR NORMALIZED_MATCH。費用 +JPY0.95(12.24->13.19)。再assemble後もM3 Gate PASS。

## 4. Full Story WPM(`er019_coffee_p8_wiring_evidence_01.py`、measure_wpm_01.pyのcount_primary/frame_rms_db/find_pauses再利用)とv4比較(**原稿が異なる参考値**)
語数=Full Story `text` 語数。v4はStd 412語/Adv 462語、本runはStd 456語/Adv 471語(原稿差)。WPM=語数/尺、発話WPM=500ms以上ポーズ除外。Stdは6%減速後。
| level | 指標 | 本run(初回、regen前) | v4(MEASUREMENTS_V4.md) | 差% |
|---|---|---|---|---|
| Std | 全体WPM | 165.7 | 162.2 | +2.2% |
| Std | 発話WPM | 186.1 | 177.0 | +5.1% |
| Std | 尺(3 part計) | 165.13s | 152.43s | +8.3%(語数+10.7%) |
| Adv | 全体WPM | 172.9 | 180.7 | -4.3% |
| Adv | 発話WPM | 194.3 | 190.0 | +2.3% |
| Adv | 尺 | 163.45s | 153.4s | +6.6%(語数+1.9%) |
- Adv part2 regen後(同一text・同一Promptの再生成): part2尺 56.03s -> 56.79s(+1.4%)、Adv全体WPM 172.1。
- 解釈: 全体WPMの差は-4.3%〜+2.2%で、v4のP8実績と同水準。原稿が違うため「同一Promptの完全再現」とは言えない(同一textのばらつきは上記regenで約1.4%)。聴感は未実施。

## 5. 費用(JPY、`raw_usage_log.jsonl` 実測、上限30)
| 段階 | 累計 | 内訳 |
|---|---|---|
| b1b tts | 4.29 | gemini 3.04 / asr 1.21 / openai 0.04 |
| + a2 tts(Std part1の外側retry含む) | 12.24 | gemini 7.33 / asr 4.22 / openai 0.10 / azure 0.58 |
| resume(b1b tts再実行) | 12.24 | +0 |
| + regen(b1b part2) | **13.19** | gemini 8.02 / asr 4.48 / openai 0.10 / azure 0.58 |
- 実費 **JPY13.19 / 上限30**(見積10〜15内)。LLM scaffold費用0(明示コピー)。Coffee累計(COST_LEDGER_COFFEE_01.md 約JPY133.9[未集計項目除く] + 本run 13.19) = 約JPY147.1。

## 6. 残リスク/未実測
1. 原稿差(0節): v4と同一原稿での再現は未実施。
2. 内側標準retry(attempt2以降)のsha一致、fallback/LR発生時の実BLOCK動作は本runで未発生のため実測なし(test 32件のみ)。
3. Std japanese_title(非P8 role)で既存のminimal_fallbackが発生(既存挙動、P8と無関係、M3対象外)。
4. OPEN-312/313(既存の穴/Phase 2)は未解決のまま(範囲外)。
5. 聴感評価は未実施。PRODUCTION_WIRED判定はFable/ユーザー確認待ち。
