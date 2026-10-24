# RUNTIME_EVIDENCE_01 (SHORT-CLIP-SPEED-GATE-01 委任_01、2026-10-24) Family Z 極短clip速度Gate

API 0円・音声再生成0・公開物変更0。

## 実装
`er063_family_z_audio_01.py`: 定数`ADV_SHORT_CLIP_ORIGINAL_SECONDS=1.5`、`ADV_SHORT_CLIP_RATIO_MIN/MAX=0.90/1.00`、関数`adv_dialogue_ratio_range(original_seconds)`(`< 1.5`のみ短clip、1.5ちょうど=従来0.93〜0.96)。`verify_z_speed_profile`のAdv会話分岐が原音長に応じて範囲を選択(旧固定0.93〜0.96判定は撤去、`ADV_DIALOGUE_RATIO_MIN/MAX`は>=1.5秒の範囲定数として残置)。gate detailに`original_seconds/ratio/ratio_range`を追記。flagなし、速度設定(atempo 1.06)・他の品質条件は不変。

## 呼出箇所(initial/retry/fallback/regeneration/resume共通)
`verify_z_speed_profile`の呼出は`run_audio_gate`(er063:1658)1箇所のみ。Z runnerは全経路(初回・resume・`--only-clips`再生成・Local Rewrite後)で同じ`gate` stageを経由して`run_audio_gate`を呼ぶ(runner:1821)。TTS段(retry/fallback/regeneration)は比Gateを持たず、Gate段が最終判定。`Grep`: `verify_z_speed_profile`の他の呼出元=testのみ。旧範囲の重複実装なし。

## test
`er063_family_z_speed_v2_test_01.py`に`ShortClipSpeedGateTest`7件追加(<1.5で0.90〜1.00 / >=1.5で0.93〜0.96 / 境界1.5・1.4999 / 0.90・1.00内外 / 『Wait!』0.771s・0.7455s比0.9670 PASS / 0.77sで比0.85・1.05 NG・2.0sで比0.97・1.00 NG)。既存`test_legacy_adv_dialogue_unprocessed_is_detected`の「処理漏れ」ケースは原音1.0s・比1.00を使っていたが、ユーザー採用仕様で比1.00が短clipの許容上限になったため原音2.0s(>=1.5s)へ変更(検出対象は同一=処理漏れ、長いclipで引き続きNG)。結果は報告(RESULT_PACKET)参照。

## 正式経路runtime evidence(『猿の手』run_sf_prod_01の**コピー**で実施)
- コピー=`.../the_monkeys_paw/run_sf_prod_01_gatecopy_20261024`(実行後削除、公開物・原runは未変更)。コマンド: `py er026_family_z_fiction_production_runner_01.py --story the_monkeys_paw --run run_sf_prod_01_gatecopy_20261024 --stages provision_shell,gate --mode real --approved-budget-jpy 60 --tts-execution-mode STANDARD`(1起動、rc=0、API 0、assemble/pages/page_verifyは実行せず)。起動前 `tools/stop_scope_check_01.py` rc=0。
- 結果: Adv/Std とも shared_gate=PASS。Adv会話の全17clipの原音長・比・適用範囲・結果は `_gate_table_and_old_take_01.txt` と `gate_result_b1b_new_rule.json`。<1.5秒の5clip(part1_c5 1.371s/0.9528, part1_c9 0.961s/0.9588, part2_c11 1.451s/0.9514, part3_c3 1.491s/0.946, part3_c5 1.051s/0.9535)は範囲0.90〜1.00、>=1.5秒はすべて0.93〜0.96で全PASS(新旧とも全clip PASS=既存の正常音声を不要に再生成しない)。
- 旧テイク(`_regen_backup_part3_c5_20261024/`、原音0.7710s・出力0.7455s・比0.9670)を正式関数`verify_z_speed_profile`へ入力(一時dirにcopy、runは非汚染): 新条件=PASS(範囲0.90〜1.00)、旧固定範囲0.93〜0.96=FamilyZSlowdownGateStop(同ログ)。
