## 管理ID

TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_06(委任_04で追加した`register_ja_terminal_hr`がEN queueへ書き、JA判定器のJA queue行と二重(HRQ 2行)になる不具合の是正+実経路再確認。Production軽微修正、費用≤¥2)。**注意: 同じ問題(JA終端HRQ)への2回目の修正。これで再発すれば3回目はOpus条件B必須のため、根本原因(queueの書込先と重複抑止の単位)を確実に押さえること。** 並行Agent: FAMILY-Z-STYLE-ACTUAL-GATE-01(`er063_*`)。あなたの所有=`er127_tts_block_policy_01.py`(`register_terminal_hr`/`register_ja_terminal_hr`)、必要なら`er003_v1_n3_01_tts_generate.py`/`er003_v1_sing01_voice01_generate.py`のJA終端呼出(引数のみ)、test、`docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/{FOLLOWUP_02,EVIDENCE_JA_TERMINAL_02}.md`+`evidence_runs/`+driver、新run dir `run_tru_ev_ja_02`、`docs/pm/delegation_log/2026-10-27_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_06.md`(+check.json)、`docs/pm/RESULT_PACKET_TRU6.md`。`er006_*`/`er007_*`(queue書込本体)は編集禁止(関数を引数で受ける形で解決)。SSOT編集権なし。pathspec付きcommit。

## 性質/禁止

- 性質: U-04「終端NG1件=HRQ1行」の実装不具合是正(B)。到達上限=FIXED+実経路確認(hrq_rows==1)。
- 禁止: Gate/回数/待機/Style変更、`er006`/`er007`編集、禁止Git操作。
- 費用: 上限¥2(Guardrail、T-3定型どおり)。再実走1回≈¥0.6。
- 時間見込み: 約1h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2: `TTS_EXECUTION_MODE=STANDARD`明示・`--only-segments`差分・`--budget-jpy 2`。T-3: 上記。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_06.md` をN=697から順に試し、先頭「## 管理ID」+「TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_06」のものを採用。

## 事前指定Read一覧

- `docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/{EVIDENCE_JA_TERMINAL_01,FOLLOWUP_01}.md`、`evidence_runs/JA_01.json`(`driver_observation.log_human_review`)、`tools/tru_ev_ja_01.py`
- `er127_tts_block_policy_01.py:540-600`(`register_terminal_hr`/`register_ja_terminal_hr`、重複抑止キー)
- `er006_secondary_asr_01.py` Grep `_log_human_review|human_review_queue` ±10、`er007_ja_secondary_asr_01.py:42-60`(JA queueの書込とdedupeキー)
- JA終端呼出: `er003_v1_n3_01_tts_generate.py` Grep `register_ja_terminal_hr` ±10、`er003_v1_sing01_voice01_generate.py` 同

## 事前指定Grep一覧+追記位置・更新位置の手順

- `py tools/stop_scope_check_01.py --managed-id TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 --run-dir <run_tru_ev_ja_02> --out docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/stop_check_ja_02.json`

## 実施事項

1. **根本原因の確定**: (a)JA判定器が最終slotでJA queueへ書く条件と、書かない終端(disfluency/repetition単独NG・cascade打切り)を列挙。(b)`register_terminal_hr`の重複抑止がファイル単位(EN queue内)である事実。(c)したがってJA終端の登録は**JA queueへ、JA判定器と同じdedupeキー(wav_path+canonical_text等)で**書く必要がある。
2. **是正(案A)**: `register_terminal_hr`に書込関数(`log_fn`)とdedupe判定を引数化し、`register_ja_terminal_hr`は`er007_ja_secondary_asr_01._log_human_review`相当をJA queueへ使う。JA判定器が既に同一(wav_path, canonical_text)行を書いていれば**書かない**(JA queueを読んで判定、または判定器の戻り値/最終slot記録で判定)。EN側(英語部位)の既存挙動は不変。
3. **test**: (i)判定器が行を書いた終端→合計1行(JA queue)、(ii)判定器が行を書かない終端(disfluency単独NG等)→`register_ja_terminal_hr`が1行、(iii)EN queueへJA行が書かれない、(iv)英語部位の既存test不変。負の対照(helper無効化で(ii)が0行)。er127全件・er003・er011・er007/er006関連test。接続0。
4. **実経路再確認**: `tru_ev_ja_01.py`を`run_tru_ev_ja_02`で再実行(転写置換注入、同segment)。観測: `hrq_rows==1`(JA queue)、EN queue増分0、Lock/STOPPED/TTS 3/待機180秒1回。`EVIDENCE_01.md`行4を更新。
5. `FOLLOWUP_02.md`: 原因・修正・test・evidence。

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_06.md --json-out docs\pm\delegation_log\2026-10-27_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_DELEGATION_06.md_check.json`
- 回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er127*_test_*.py"`、`--pattern "er003*_test_*.py"`、`--pattern "er011*_test_*.py"`、`--pattern "er007*_test_*.py"`、`--pattern "er006*_test_*.py"`
- 実走: `.venv\Scripts\python.exe docs\research\TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01\tools\tru_ev_ja_01.py --run run_tru_ev_ja_02 ...`(実引数は前回JA_01の記録を踏襲し全文記録、`TTS_EXECUTION_MODE=STANDARD`)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_TRU6.md`にOPEN-540限定解除文案(JA終端HRQ=FIXED+JA_02で1行確認)。

## Git

- commit message: `TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_06: JA終端HRQの二重登録是正(JA queueへ・判定器と同一dedupe)+実経路再確認 hrq_rows==1(実費¥X)`。trailer: `Delegation: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/06`。push。

## 報告

`docs/pm/RESULT_PACKET_TRU6.md`: (0)T-0、(1)根本原因、(2)修正差分、(3)test・回帰、(4)実経路再確認(hrq_rows・queue別行数・費用)、(5)必須4行+「判定整合: 重大NG=<なし|あり>」、(6)SSOT文案、commit hash・raw URL。末尾3行要約。