# RUNTIME_EVIDENCE_02 (FAMILY-X-MOON-SHRINKING-PRODUCTION-01 委任_03、2026-10-25)

- Status: **STOPPED_AT_TEXT(数値再脱落)**。audio・試聴ページ差替えは未実施(欠陥のある本文を音声化しない)。公開ページ `user_test/family_x_moon_shrinking_01/` は run_ms_01 版のまま(未変更)。
- 入口: `er019_family_x_entertainment_production_runner_01.py --stage all --run-label run_ms_02 --budget-jpy 80`(新run dir `er019_output/moon_shrinking/run_ms_02`、1起動、PID 10226、JST 00:07:54起動、rc=0、再起動0)。直前 `tools/stop_scope_check_01.py` rc=0(`stop_check_03_text.json`)。
- 再利用: `run_ms_01/research_ledger`・`storyline_b3`を新run dirへ複製(runnerの既存再利用分岐: Ledger再利用 / 既存Selected Fact Brief再利用 / 丸めoverlay `reused=True api_calls=0`、overlay_sha256同一)。再実行された段=W-1(R0/R1/R2)→Advanced→Adv RF→Standard→Std RF。入力(B3・注記・theme.txt)・Prompt・コードはrun_ms_01と同一(Production変更0)。
- model_id: W-1 R0/R1/R2=`gpt-6.1-sol`(最新世代上位系、routing固定)、Advanced/Standard/RF A3A4=`gpt-6-luna`、RF=`gemini-3.5-flash-lite`。
- Gate: 記号QA R0再生成なし(findings 0)、RF(Adv/Std)実行済み(issueは非Blocking)、HR・Style Gate・TTSは未到達。
- 結果: 本文の数値は『8,900本超』のみ(FACT_CHECK_03.md)。停止。
- 費用: run_ms_02 text 18.018円(w1_r0 7.607 / r1 3.925 / r2 4.246 / adv 0.253 / std 0.311 / RF 計約1.68)。作品累計=run_ms_01 63.78 + 18.02 = **81.80円**(委任_03上限150円内。70円目標との差+11.80円、audio未実施分を含まず)。日次は10-25 JSTで本run分18.02円/1,000円。
- 所要: 約6分(00:07:54起動〜完了)。
- KP/ASR/HR: 未実施(audio段なし)。
