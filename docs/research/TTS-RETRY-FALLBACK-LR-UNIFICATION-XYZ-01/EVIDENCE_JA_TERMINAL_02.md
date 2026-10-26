# EVIDENCE_JA_TERMINAL_02 (委任_06: JA終端HRQ二重登録の是正後 実経路再確認)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 / 実行: 2026-10-27 / 到達上限: FIXED + 実経路確認

- case `JA_02`(JA_01と同条件: X Std a2 `japanese_title`、Primary/Secondary転写に1語置換[コーヒー豆→天気予報]を注入し、JA判定器自身にNGを出させる)。driver `tools/tru_ev_ja_02.py`(`tru_ev_ja_01.py`の case id / 出力名のみ変更)。run dir `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_tru_ev_ja_02`(不追跡)。
- 起動: `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/tools/tru_ev_ja_02.py --tts-execution-mode STANDARD --budget-jpy 2`(1回のみ、再起動なし)。事前 `stop_check_ja_02.json` rc=0。
- 証跡: `evidence_runs/JA_02.json`。

| 項目 | JA_01(是正前) | JA_02(是正後) |
|---|---|---|
| HRQ行(合計) | 2(JA queue 1 + EN queue 1) | **1(JA queueのみ)** |
| EN queue行 | 1(TERMINAL_NG) | **0**(ファイル未作成) |
| `register_ja_terminal_hr` | 呼出・EN queueへ書込 | 呼出・JA queueの`_log_human_review`へ。既に判定器行あり(rows_before=1)→`wrote_row=false`(重複抑止) |
| TTS / 待機 / LR | 3 / 1回180.0s / 0 | 3 / 1回180.0s / 0 |
| 最終status / Lock | STOPPED / HUMAN_REVIEW_REQUIRED | STOPPED / HUMAN_REVIEW_REQUIRED |
| 実費 | ¥0.56 | ¥0.585(openai 0.07+gemini 0.17+openai_asr 0.04+azure 0.30) |

HRQ 1行 = JA判定器が最終slotで書いた行(final_status=TRUE_CONTENT_MISMATCH)。終端登録は同一(wav_path, canonical_text)を検出して2行目を作らない。例外なし。
判定: 「終端NG1件=HRQ1行」実経路で達成(PASS)。
