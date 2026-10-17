# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_17(Fable決定B1/B2の反映+「走れメロス」`run_e2e_03` 正式Production E2E実走(有料、上限JPY100)+runtime evidence収集+試聴ページ+SSOT記録)。日付: 2026-10-17。

## 性質・到達上限Status・禁止事項
- 性質: 承認済み仕様の正式Production実走(ユーザー2026-10-17 #108承認=別枠JPY100、期待約45)。有料。
- 到達上限Status: `AUDIO_E2E_COMPLETE_EVIDENCE_RECORDED_PENDING_FABLE`。**PRODUCTION_WIREDはSonnetが宣言しない**(Fableが受入10条件で判定)。聴感PASSはユーザー試聴前に扱わない。
- 禁止: 累計JPY100超過見込みでの続行/`run_e2e_01`・`run_e2e_02`の`--mode real`起動/有料runの自動再起動(26節: 異常終了・STOP時は再起動せず状態を報告)/HR Lock・review_lock・Style Gate・SRC STOP・AUW Gateの迂回・削除/Style・Voice・Prompt・KP選定方針の変更/品質基準の緩和/新Trial/Landing更新/`er006_output/pronunciation_ledger_01/ledger.json`のcommit/run_e2e_02の試聴ページ`user_test/family_z_melos_01/`の上書き。
- 固定ブロック: **E-1**(FZ_COMPLETION_PLAN_01 §6・§10、CURRENT_SPEC Status表、委任_16成果に整合。新仕様なし)/**D-1**(不適用=承認済み仕様の正式配線)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。commit直列)/**F-1**(費用は`cost_log.jsonl`実測を出典に、実測/推定/未取得を区分。未確認の数字は出さない。¥300枠の既存累計(run_e2e_01 108.11/run_e2e_02 62.83、出典=委任_16報告)とは分離)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-17_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_委任_17.md`へ保存し`check_delegation_prompt.py`実行、`_check.json`保持。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZ17.md`、`docs/pm/ACTIVE_TASK.md`先頭へ新ヘッダ追加・旧ヘッダ保持)。
- 使用モデル: Production配線済みのrouting(変更しない)。報告に実model_idを記載。

## Fable決定(委任_16 判断候補への回答。再質問しない)
- **B1(stop_scope_check解除)=案1採用**: `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_STOP_NOTICE.md`の「## 解除通知(Fable、2026-10-17)」節に構造化欄 `status: RELEASED` / `issuer: Fable` / `scope: run:run_e2e_03`(解除対象の明示) を追記(ファイル削除・既存本文の削除はしない)。併せて`C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_02\STOP`センチネルを26-5の正規書式で設置(reason=`SUPERSEDED_BY_run_e2e_03 (Fable 2026-10-17): run_e2e_02は再利用元として凍結、--mode real禁止`。`RUN_CLOSED`は使わない=将来の正規解除を残す)。`run_e2e_01/STOP`は既存のまま。実走前に`tools/stop_scope_check_01.py`を再実行し**rc=0・stop=falseを確認できた場合のみ**実走する(rc≠0ならSTOP報告)。
- **B2(pages_dir)=`user_test/family_z_melos_02`へ変更**: `er026_family_z_fiction_production_runner_01.py:817`の`E2E_PAGES_DIR`を`"user_test/family_z_melos_02"`へ。既存test/evidenceが`family_z_melos_01`を固定していれば、その参照を更新(履歴記録の文字列は不変)。commitは実走前。
- C1(kp_expl_b1b再生成、実LLM 1呼出、guard JPY2.0)=承認(#108枠内)。C2(budget: CLI 100、`limit()=100`、run_e2e_03専用cost_logで分離)=了承。C3(stop_sentinel隔離testによるtracked log書換え)=commitしない。
- Ledger entry `ec716e185835dba3`=作業ツリー維持(委任_16 F2)。Std part1_c5「Melos said.」がPASS_WITH_WARNINGなら試聴リストへ明示、HR Lockが発火したらSTOP・報告(迂回しない、事前承認なし)。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01\FZ_COMPLETION_PLAN_01.md` §6(L95-101)・§10(L123以降、実走CLI・Gate・STOP条件)
- `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZ16.md`
- `C:\Users\tensh\eigo-radio\docs\pm\PM_GOVERNANCE.md` 26-2〜26-5(L3394-3412)
- `C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py` L800-830(E2E_PAGES_DIR)・`stage_pages`/`page_verify`該当関数・STOPセンチネル書式(Grep `RESTART_STORM_LOCK|audit_stop_sentinel|def _write_stop`)
- BAPEのevidence scriptを参考: `C:\Users\tensh\eigo-radio\er019_bape_style_table_04.py`、`er019_bape_play_verify_04.py`、`er019_bape_cost_04.py`(Z用に同等の集計を作る)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `CURRENT_SPEC.md`: Grep `共通仕様のFamily別配線Status表`→Z列を「runtime evidence取得済み(run_e2e_03、commit sha)・Fable判定待ち」へ(PRODUCTION_WIREDとは書かない)/Grep `別枠JPY100`→実測累計を追記。
- `OPEN_ITEMS.md`: Grep `OPEN-412`→実走結果(evidence path・費用)追記、Status=`AUDIO_E2E_COMPLETE_EVIDENCE_RECORDED_PENDING_FABLE`。
- `DECISION_LOG.md`: 末尾に委任_17エントリ(B1/B2決定、実走結果の事実、未宣言事項)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#23`→「新試聴ページ完成(URL)、ユーザー試聴待ち」へ更新(判断済みにしない)。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。
- `FZ_COMPLETION_PLAN_01.md`: 「## §11 委任_17 実走記録」を追記(事実のみ)。

## 作業(順序)
### A. 実走前(commit 1、JPY0)
1. T-0保存・check。2. B1: STOP_NOTICE構造化欄追記+run_e2e_02 STOPセンチネル設置+stop_scope_check再実行(rc=0必須)。3. B2: E2E_PAGES_DIR変更+関連test更新→`er026`runner test・integration testを再実行しPASS。4. secret_scan→commit→push。5. 本日費用照合: 当日累計約JPY394(概算、ACTIVE_TASK旧ヘッダ)+本run上限100 ≤ 1,000を記録。
### B. 実走(有料、1回起動、foreground)
- 環境変数`TTS_EXECUTION_MODE=STANDARD`を明示。実走CLI(下記)を**1回だけ**起動し、終了まで待つ(別プロセス・ラッパ・監視再起動は作らない)。
- 進行中は`run_e2e_03/cost_log.jsonl`と`e2e_stage_log.jsonl`の`spent_jpy_cumulative`を確認し、**残り工程の見積を加えて100超過見込みになった時点で**runnerのSTOP手段(`--clear-stop`の逆=`<run>/STOP`設置、または既存の停止手順)で停止し報告。
- HR Lock/review_lock/Style mismatch STOP/SRC STOP/AUW NG上限/ProvenanceMismatch で停止した場合: 迂回せず、停止時点の状態(stage、費用、該当segment、理由)を報告してSTOP。
### C. 実走後evidence(JPY0、read-only並列可)
1. SRC: `run_e2e_03/*/audit/src_z_posthoc_01.json`の全KP(a2/b1b)について source_sentence_id/resolution_method/quote_boundary_truncated の一覧表。
2. Style runtime: `audit/style_record.json`の全Role(Narrator PD06/Std JA Preview・Comment S3/Adv Preview E1/KP K2/Std KP JA P8-KP/Adv KP解説 P7/Adv Comment E2_UPBEAT=Z固有)について、実clipごとの style sha・actual model_id・voice・routing を表に(BAPEの`e2e_segment_style_table`相当。exp_match true/false件数)。X定数shaと一致するか。
3. Dialogue別Voice: speaker_table/dialogue_attributionと実clipのvoiceを突合(Dialogue clipにPD06が適用されていないこと、speaker→Voice対応がrun_e2e_02と同一)。
4. AUW/ASR・6%減速(`verify_std_english_slowdown`相当)・Assembly結果、PASS_WITH_WARNING一覧(Melos said含む)、HR Lock発火有無。
5. 試聴ページ: `user_test/family_z_melos_02/index.html`(Std/Adv)。commit・push後にGitHub Pagesで実再生検証(HTTP 200、audio要素数、console error)。URL=`https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_02/index.html`。
6. 費用: stage別(kp_expl再生成LLM/TTS a2/TTS b1b/ASR/その他)、Web検索0、実測/推定/未取得区分、合計/100、¥300枠累計とは分離表示。
7. Regression: 委任_16と同じtest群を再実行しPASS数。Dangling Reference Check再走。
### D. 記録(commit 2〜3)
- run_e2e_03のgit追跡対象(wav以外のテキスト成果・audit json・pages)をcommit(既存runの追跡範囲に合わせる。巨大binaryは追加しない)。SSOT更新(上記Grep手順)。§11追記。push。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-17_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_委任_17.md`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\stop_scope_check_01.py --managed-id FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03 --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03\stop_scope_check_17.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I -m pytest C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01_test_01.py C:\Users\tensh\eigo-radio\er026_family_z_e2e_integration_test_01.py C:\Users\tensh\eigo-radio\er026_family_z_src_posthoc_01_test_01.py C:\Users\tensh\eigo-radio\er063_family_z_audio_01_test_01.py C:\Users\tensh\eigo-radio\er063_family_z_common_style_wiring_01_test_01.py -q`(runner test名が異なる場合は実在名へ置換し報告)
- 実走(PowerShell): `$env:TTS_EXECUTION_MODE="STANDARD"; C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py --run run_e2e_03 --mode real --stage all --approved-budget-jpy 100 --tts-execution-mode STANDARD --regenerate-stage kp_expl_b1b 2>&1 | Tee-Object -FilePath C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03\run_17_console.log`
- 費用集計: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er026_fz_cost_17.py --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03 --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03\audit\cost_by_stage_17.json`(新規script、BAPEの`er019_bape_cost_04.py`を雛形に)
- Style表: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er026_fz_style_table_17.py --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03 --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03\audit\segment_style_table_17.json`(新規script。X側の`er019_family_x_fx_20261016_wiring_01_test_01`の許可集合に読み取り専用として必要なら登録)
- Pages再生検証: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er026_fz_play_verify_17.py --url https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_02/index.html --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03\audit\pages_play_evidence_17.json`(`er019_bape_play_verify_04.py`を雛形に)
- secret scan: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py`(実在するscan script名に置換)

## SSOT追記文(要点)
- CURRENT_SPEC Status表: 「Z: run_e2e_03でruntime evidence取得(style_record全Role一致 N/N、SRC a2 5/b1b 5解決、Dialogue別Voice維持)、Fable受入判定待ち(2026-10-17 委任_17)」。
- DECISION_LOG: 「2026-10-17 委任_17: Fable決定B1(STOP_NOTICE status RELEASED・run_e2e_02 STOP凍結)/B2(pages dir melos_02)。run_e2e_03 実走結果(完走可否・費用JPY x/100・Gate結果)。PRODUCTION_WIRED・聴感PASSは未宣言」。
- OPEN-412: 上記事実+evidence path。REGISTER #23: 新試聴ページURL提示、ユーザー試聴待ち。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1(実走前): delegation_log 委任_17+_check.json、STOP_NOTICE.md、`er026_family_z_fiction_production_runner_01.py`(E2E_PAGES_DIR)、更新test。msg: `FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_17: Fable決定B1(STOP_NOTICE status RELEASED・run_e2e_02 STOP凍結)/B2(E2E_PAGES_DIR=family_z_melos_02)+stop_scope_check rc=0(実走前、JPY0)`
- commit 2(実走後): run_e2e_03追跡対象、`user_test/family_z_melos_02/`、新規evidence script 3本、audit json。msg: `FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_17: 「走れメロス」run_e2e_03 正式Production E2E実走(PD06/S3/E1/K2/P8-KP/P7・Dialogue別Voice・SRC D1・6%減速・AUW・Assembly・試聴ページ)+runtime evidence+工程別費用(JPY x/100)`
- commit 3: SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REGISTER/REPORT_LEDGER/FZ_COMPLETION_PLAN §11)。msg: `FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_17: SSOT記録(runtime evidence・費用・Fable判定待ち、PRODUCTION_WIRED未宣言)`
- `*_output/`のwav・ledger.json・他runのruntime差分はaddしない。

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZ17.md`)
ユーザー§9の順で事実のみ: (1)完走可否(stage一覧とrc)(2)試聴URL(Std/Adv)(3)SRC適用結果(KP別表)(4)PD06/S3/P7/P8-KP/E1/K2のruntime証拠(clip数・sha一致数・model_id)(5)Dialogue別Voice確認(6)再利用範囲(allowlist 60 file、reuse stage一覧)(7)実測費用/100(stage別、¥300枠と分離)(8)Regression/AUW/ASR/Assembly結果+PASS_WITH_WARNING一覧+HR Lock有無(9)各仕様の配線状態の事実(判定はFable)(10)未解決Open Item。4行+`判定整合:`+`判断候補:`[A]〜[D]。T-0 check結果。自己チェック: 1回起動か/再起動なしか/Gate迂回なしか/累計≤100か/ledger.json未commitか/`family_z_melos_01`未上書きか/PRODUCTION_WIRED・聴感PASSを書いていないか。
