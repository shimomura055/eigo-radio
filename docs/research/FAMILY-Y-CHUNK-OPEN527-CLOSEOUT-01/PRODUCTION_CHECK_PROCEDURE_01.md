# PRODUCTION_CHECK_PROCEDURE_01 — 複数段落のY記事が正式に生成された時のruntime evidence取得とPRODUCTION_WIRED判定手順(実行しない。手順書のみ)
前提: 現行の本文契約(段落5固定・Voice本文1行)ではY chunkは実記事で発火しない。本契約をユーザーが変更し、複数段落のY記事が正式CLIで生成された時にのみ本手順を使う。
本文契約の変更自体は未承認(本手順の対象外)。検証のために記事本文を改変しない・無理に発火させる有料Trialをしない(ユーザー原文2026-10-26)。

## 手順
1. 事前: `py tools/stop_scope_check_01.py --managed-id <ID> --run-dir <run> --out <json>`(rc=3なら停止)。費用承認は7-7(300円以下・承認済みScope内)。
2. 正式CLIで通常生成(例: `py er121_family_y_runner_01.py --stage tts_a2` / `--stage tts_b1b`。TTS_EXECUTION_MODE=STANDARD明示)。dev driverは使わない(記事自体が複数段落のため不要)。
3. 確認項目(各level):
   - `<run>/<level>/audit/chunk_tts_decision.json`: 対象segmentの`chunked=true`、`paragraphs>=2`、`chunk_ids`が`<segment>_k<j>`。
   - `audit/tts_generation_results.json`: 各chunk status=OK、Std(a2)は各chunk `slowdown_applied=true`、親`chunk_tts.extra_pause_seconds=0.2`。
   - `audit/chunk_tts_evidence_<level>.json`: 親ごとのchunk列、`boundary_kind=paragraph`。
   - Gate: `y_style_gate` PASS、`y_body_checks`にchunk単位が含まれる。
   - 組立: `audit/chunk_tts_assembly_<level>.json`の`gap_offsets_in_segment_s`が(chunk数-1)個、各差=0.2秒±0.001。Std/Advで他levelのevidenceが混入しない。
   - 実測: 結合wavの長さ=Σchunk+0.2×(n-1)。ポーズが減速されていない。
4. 判定: 3.の全項目が正式CLI経路の実生成物で確認できたら、FableがPRODUCTION_WIREDへ更新(`WIRED_NOT_FIRING`→`PRODUCTION_WIRED`)。1つでも欠ければ更新しない。
5. 失敗時: 再実行はresume(OK chunk再利用)。原因不明のrc≠0が2回続いたらSTOP。
## 回帰
`.venv\Scripts\python.exe run_project_regression.py --pattern "er121*_test_*.py"`(接続試行0)を実生成前後に実行。
