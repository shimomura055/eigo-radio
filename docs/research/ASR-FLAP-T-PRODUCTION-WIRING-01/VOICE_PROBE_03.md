# ASR-FLAP-T-PRODUCTION-WIRING-01 委任_02A: 追加Voice probe(2026-10-31。Production code変更0)

生データ=`voice_probe_03.json`、clip単位=`probe_03a|03b/results.jsonl`(2 shard)、速度=`probe_03c/results.json`(初回は`results_run1_azure_init_error.json`=Azure logger未初期化の自作script不備でAzure全件エラー→logger install追加で全再実行)。実装=Trial `tools/flapt_voice_probe_02.py`を**無変更で再利用**(Production leaf `generate_narration_snippet`+`voice_override`)、速度=`tools/flapt_speed_probe_03.py`(Production `apply_a2_slowdown`にZ`Z_ADV_DIALOGUE_SLOWDOWN_PCT`=tempo1.06)、集計=`tools/flapt_probe_analyze_03.py`(API 0)。clip wavはcommitしない(shaで同定)。

## 1. プロトコル(Trial VOICE_PROBE_02と同一)
同一probe文(観測7項目: latter/metal/betting/atom/waiting/coating/"the latter one"、各1 clip=7 clip/組合せ。対照語5は不要=DESIGN 4節)、同一ASR 3系統(OpenAI gpt-4o-mini-transcribe/Azure/ローカルWhisper small)、同一判定(>=2観測項目で>=2系統がd綴り=FLAP_DEMONSTRATED→confirmed、d綴り皆無かつt綴り完全一致>=5/7=T_SPELLED、他=INDETERMINATE→not_confirmed)。Trialのsha(`ASR-FLAP-T-EQUIVALENCE-TRIAL-01/tools/`)と同一fileを使用。
- 使用モデル: TTS=`gemini-2.5-pro-preview-tts`(Productionのpro経路・Gemini TTSの現行推奨proで、本番Z実使用model。評価用最新原則[PM_GOVERNANCE 25]上は本番と同一modelで測る必要があるため意図的)。ASR=gpt-4o-mini-transcribe(最新世代の小型転写、Production同一)/Azure STT/Whisper small(Production同一)。「最新か」=Productionの実使用modelそのもの(評価対象がProduction挙動のため旧/下位モデル例外ではない)。
- clip数を12へ増やさなかった理由: 7観測項目で判定に十分(対照語は判定に使わない)で、費用最小(速度優先でなくQ=Trialと同一基準を保つ)。

## 2. 結果(組合せ別。d/t転写数は3系統x7clip=21転写中)
| 組合せ | clips | d綴り転写数 | t綴り(完全一致)転写数 | flap観測項目(>=2系統) | 判定 |
|---|---|---|---|---|---|
| Zephyr\|pro(独立) | 7/7 | 7 | 11 | betting, atom, coating | **confirmed** |
| Schedar\|pro(独立) | 7/7 | 8 | 7 | latter, atom, coating | **confirmed** |
| Algieba\|pro | 7/7 | 9 | 7 | latter, atom, coating | **confirmed** |
| Charon\|pro | 7/7 | 10 | 9 | latter, betting, atom, coating | **confirmed** |
| Aoede\|pro | 7/7 | 10 | 7 | latter, betting, atom, coating | **confirmed** |
| Fenrir\|pro | 7/7 | 9 | 5 | latter, atom, coating | **confirmed** |
| Puck\|pro | 7/7 | 4 | 10 | atom のみ(1項目) | **not_confirmed**(INDETERMINATE=d綴りは出るが基準の2項目に届かず。T_SPELLEDではない) |
未取得: なし(49 clip全件取得、TTS失敗0、Cap停止0)。Zephyr|pro latterはOpenAI「lar」/Azure「Latter.」/Whisper「ladder.」=Bertie→Birdie以外でもd綴り転写が独立clipで実在。

## 3. Z Adv dialogue 1.06x高速化後wavのASR(既存probe wavへatempo、ASRのみ。7項目x6=42 clip)
| Voice\|path | 高速化後flap観測(>=2系統) | 通常 | 維持 |
|---|---|---|---|
| Aoede\|fl | latter, atom, coating | latter, betting, atom, coating | 維持(判定FLAP_DEMONSTRATED) |
| Schedar\|fl | latter, atom, coating | 同左 | 維持 |
| Zephyr\|fl | latter, atom, coating | 同左 | 維持 |
| Fenrir\|fl | atom, coating | 同左 | 維持 |
| Orus\|pro | atom, coating | 同左 | 維持(Azure空2clip) |
| Kore\|pro | latter, atom, coating | 同左 | 維持(Azure空1clip) |
- 1.06x後もd綴り転写は6/6 Voiceで維持(消失0)。速度確認は**この6 Voiceのみ**。他(Algieba/Charon/Puck/Erinome/Leda等の|fl,|pro)は未probe=表の`fast106_confirmed=false`(Z Adv dialogueの高速化版は不適用に倒す=fail-closed)。拡張は追加probe(約¥0.05/clip)で可能。
- 自己申告: 初回速度runはAzure logger未初期化(`init_logger()`未呼出)でAzure全件エラー(OpenAI+Whisperは取得済み)。原因=自作scriptがTrialのcl.install相当を欠いた不備。install追加後に42clip全件再実行(判定は再実行結果のみ使用)。初回分のOpenAI費用は上限見積¥2.17をそのまま費用に計上(重複計上=保守側)。

## 4. 静的Voice表(`er139_flapt_voice_table_01.json`、DESIGN_01 2節の表file名。形式=Voice,path,confirmed,evidence_ref,sha+model_id/fast106_confirmed/slow6_confirmed)
- 20行: confirmed=true 19(|fl 7: Aoede/Charon/Algieba/Puck/Schedar/Zephyr/Fenrir、|pro 12: Orus/Kore/Erinome/Sulafat/Leda/Iapetus[Trial]+Zephyr/Schedar/Algieba/Charon/Aoede/Fenrir[本probe])、**confirmed=false 1: Puck|pro**。
- Zephyr|pro・Schedar|pro: Trial表の「保存記録(FZ Bertie)由来」を撤回し本probeの独立証拠(`voice_probe_03.json#combos`)へ置換(循環解消)。Zephyr|proのTrial 2 clip(INDETERMINATE)は使用しない。
- 表に載らない組合せ(例 Kore|fl等)は不適用(fail-closed)。fast106_confirmed=true: Aoede/Schedar/Zephyr/Fenrir(|fl)、Orus/Kore(|pro)。slow6_confirmed=true: Aoede/Schedar/Zephyr(|fl、Trial)。evidence_ref/shaは各証跡file(`voice_probe_02.json`/`voice_probe_03.json`)のsha256。

## 5. 費用台帳(実測。Cap ¥30固定)
| 項目 | TTS | ASR | 計 |
|---|---|---|---|
| probe_03a(Zephyr/Schedar/Algieba|pro 21clip) | 4.293 | 1.152 | 5.445 |
| probe_03b(Charon/Aoede/Fenrir/Puck|pro 28clip) | 5.468 | 1.452 | 6.919 |
| 速度 初回(Azure失敗) | 0 | 2.172(上限) | 2.172 |
| 速度 再実行 | 0 | 2.172 | 2.172 |
| **合計** | 9.761 | 6.948 | **約¥16.7(Cap内、約56%)** |
運用: 2 shard、起動間隔150秒以上(storm guard発動0、再起動0)、各run前に`stop_scope_check_01.py`rc=0。
