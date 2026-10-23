FABLE-DELEGATION-MARKER: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-委任_05-B-STAGE-OPEN-WINDOW-COMPLETION-AND-Z-EVIDENCE-20261023

# ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 委任_05(B工程): Family Z『開いた窓』の制作再開・完成(Bertie 4clip再生成、Adv c12 `forte`→`speciality`復元・再生成、正式Gate、組立、試聴ページ更新、page_verify)+ ASR①RET/②UKUSのZ runtime evidence取得。費用上限20円(TTS含む)。

## 0. 先に読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(固定ヘッダ、line 2 Git注意、ASR行・FAMILY-Z-SOURCE-FIDELITY行[line 25付近])、`.claude/agents/sonnet-worker.md`、ユーザー原文 `docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER_02.md`(§1-B・§3『開いた窓』、§2受入条件9項目、§4報告)、`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/PN/{IMPLEMENTATION_01,RUNTIME_EVIDENCE_01,WIRING_DESIGN_02}.md`(§5 Z手順)、`UKUS/{IMPLEMENTATION_01,RUNTIME_EVIDENCE_01}.md`(§3 Z手順・§4)、`docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/{PHASE4_RESULT_01,BERTIE_LEDGER_CANDIDATE_01}.md`、`docs/pm/RESULT_PACKET_ASRQ_PN4.md`、`docs/pm/RESULT_PACKET_ASRQ_UKUS4.md`。

## 1. Fable受入(2026-10-23)の前提
- ①RET(OPEN-472)・②UKUS(OPEN-471)は、ユーザー正式採用(UDR #168、APPROVED_FOR_PRODUCTION、X/Z共通)に基づきProduction実装済み(commit 8dd3d4d7e/81bf6ef1c、719de3adc/110977878)。Fableは受入条件1〜9のうち**X側を受入**(①=正式runner関数+実ASRでの発火証跡、②=正式TTS段関数の実runでの発火証跡。①のCLI入口での自然発火は次回のX記事runで追認、限界として開示)。**X=PRODUCTION_WIRED(Fable受入2026-10-23)**とSSOTに記してよい(①②とも)。**Z=本委任のruntime evidence取得後にFableが判定**(本委任では「Z evidence取得済み・Fable最終確認待ち」までを書く)。
- 『開いた窓』run: `er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01/`(a2 37 OK/2 STOPPED、b1b 36 OK/2 STOPPED。Bertie HR Lock=`full_story_part1_c14`・`full_story_part3_c2`(両level計4clip)、b1b `full_story_part3_c12` はLRで `forte`、`review_lock_state` RESOLVED cumulative 4)。
- Bertie HR Lockの解除: ユーザー原文§1-B「Bertie関連の停止音声4件を再生成」・§3がFableの `approve_regenerate` 根拠(W-14)。Ledgerへの個別手動登録・speciality個別例外は禁止(ユーザー既決)。正式経路の自動処理(例: Perplexity発音調査が復旧済みのため、pipelineが通常処理としてBertieを調査・Ledger登録すること)は正規動作として許容し、事実を記録する。

## 2. 作業
### T-0 記録・予算(API 0)
- 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_委任_05.md`(先頭MARKER一致確認)。
- `ACTIVE_TASK.md`: ASR行(自分の管理IDの行のみ)へ 委任_05 Status=`B_STAGE_IN_PROGRESS`、上限20円、報告=`docs/pm/RESULT_PACKET_ASRQ_B5.md`を記す。FAMILY-Z-SOURCE-FIDELITY行(line 25付近)は本委任の『開いた窓』再開に伴い同じagent(あなた)が更新してよい(他案件の行は不可)。
- 予算: 当日累計を `daily_dev_cost_01` で確認(当日上限1,400円。他案件予約枠=Family Y 残334.25円、KP Trial 70円)。見込み(Bertie 4clip+c12 1clip+retry余裕≒5〜15円)を記録。累計16円到達で見込み再計算、20円超過見込みなら停止前にFableへ報告。
- **保全**: 再生成前に run_sf_prod_01 の対象clip・`review_lock_state`・provenance・checkpoint・manifest を保全コピー(`..._preserve_20261023/`、gitignore対象なら追跡しない)。
### T-1 TTS直列化
ACTIVE_TASKの他行に「有料run(TTS)進行中」(Family Y agentが使用中の可能性大)があれば終了まで待機(最大45分。超えたらFableへ報告)。開始時に自行へ「有料run(TTS)進行中」、終了時に「終了(時刻・実費)」。
### T-2 Bertie 4clip(①RET Z evidence)
1. HR Lock 4clipを `approve_regenerate`(根拠=USER_02 §1-B/§3、Fable承認、本委任文path)で解除記録し、正式 `run_tts_stage`(Z)を対象clip限定で実行(a2 2clip・b1b 2clip)。再起動は1回まで(rc≠0の場合のみ)。
2. 確認: `audit/entity_table.json` 生成、受理のbasis(`entity_table:*` か Ledger か)、`entity_table_basis` 付きアラーム受理、HR 0、他levelの表の和集合、再開時NER 0、operator報告の別欄表示、`RUN_ENTITY_TABLE_ENABLED` と `UKUS_SPELLING_EQUIVALENCE_ENABLED` 両方ONでの動作(T-K Z実run)。
3. **もし正規動作としてLedger経由で受理されRETが寄与しなかった場合**: それは正しい挙動として記録し、①のZ runtime evidenceは別途、正式Z `run_tts_stage`関数を隔離run_dir(`er103_output/ret_prod_z_evidence_01/`等、Production runには触れない)でLedger空の条件で1clip(Bertie含む既存wav replayまたは最小TTS 1clip≤2円)実行して取得する(X-2と同じ区分(A)方式)。
### T-3 c12 speciality復元(②UKUS Z evidence)
UKUS/RUNTIME_EVIDENCE_01.md §3の手順どおり: checkpoint不在確認→c12 entryへ `reuse_blocked` 印(segmentsキー削除なし)→原稿を `speciality` に戻す(原稿本来の語。LR履歴はprovenanceにsuperseded注記)→`--only-clips full_story_part3_c12` を1回実行→PASS理由に `ukus_spelling_variant`・`pron_differs=true` が記録されることを確認→原稿・字幕・音声の一致確認。失敗時は保全コピーから復元しFableへ。累積カウンタ(RESOLVED cumulative 4+≤3=7≤15)を記録。
### T-4 正式Gate→組立→試聴ページ
1. 既存の正式品質Gate(speed v2含む)→assemble(Std/Adv全編)。Gateは迂回しない。新たなHR Lockが出たら当該clipで止めて報告。
2. 試聴ページ `user_test/family_z_open_window_01/` を差し替え更新(全体再生・個別再生・スクリプト整合、Bertie箇所・c12 speciality箇所を明記)。page_verify(既存checker)実行、結果を `PHASE4_RESULT_02.md` 相当(`docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/PHASE4_RESULT_02.md`)へ。
3. speciality clipは最終試聴の確認点(英式/米式の読み)としてユーザー向けに明示する。
### T-5 SSOT・Git・報告
- OPEN-471/472: 「X=PRODUCTION_WIRED(Fable受入2026-10-23)/Z=runtime evidence取得済み・Fable最終確認待ち」(evidenceが揃わなかった場合はその事実と理由)。OPEN-465(『開いた窓』paused)更新。`CURRENT_SPEC.md`に①②のX/Z状態表記が必要なら1〜2行。`DECISION_LOG.md`にFable受入(X)と approve_regenerate 記録。`docs/pm/REPORT_LEDGER.md`。UDR #157(『開いた窓』試聴待ち)の更新があれば反映。
- Git: `secret_scan --staged` hits=0 → `git diff --cached --name-status`(意図しないD/A確認)→ `git commit --only -- <path…>` → `git push origin HEAD:main`。wav/raw_usage_logは追跡しない。raw URL添付。
- 報告=`docs/pm/RESULT_PACKET_ASRQ_B5.md`: (A)①②のZ evidence結果(clip別basis・flag状態・T-K)、(B)『開いた窓』修正音声の検証結果・Std/Adv完成状況・最終試聴URL・ユーザー試聴待ち事項(speciality読み)、(C)費用(出典付き)・時間、(D)Closeout項目(手段の成否と目的達成の区別、撤去・残置、残リスク)。使用model名・最新か明記。

## 3. 禁止・制約
Production code/Prompt/flag/閾値の変更0(本委任は運用実行のみ。不具合発見時は修正せずFableへ)。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。一時index禁止。pythonプロセスは自分が起動したPIDのみ終了可(26-6)。Gate/HR Lock/STOP迂回禁止(approve_regenerateは上記4clipのみ)。Ledgerへの手動個別登録・個別例外禁止。`TTS_EXECUTION_MODE=STANDARD`。秘密情報出力禁止。他agent(Family Y・KP Trial)と共有ファイル(attempt_history等)への書込があれば自分の行だけを扱い、他agentの行を消さない。
## 4. handback
完了/予算警告/新たなHR Lock/blocker のいずれかで。途中経過は小刻みに返さない。