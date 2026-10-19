# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_07(Phase 3: 「走れメロス」新run `run_e2e_04` で①〜④反映の正式Production E2E実走(テキスト系再利用・音声全再生成)+runtime evidence+標準フォーマット試聴ページ更新+SSOT。**有料、上限JPY80(Fable設定、日次1,000円内)、期待約35〜40**)。日付: 2026-10-19(JST)。

## 性質・到達上限Status・禁止事項
- 性質: 承認済み仕様①〜④(コード配線済み: commit ac0ea83fe/6400b20a6/0b876f153)の正式runtime実走とevidence収集。
- 到達上限Status: `PHASE3_E2E_COMPLETE_EVIDENCE_RECORDED_PENDING_FABLE`。PRODUCTION_WIRED(項目別)はFable判定。聴感PASSはユーザー試聴前に扱わない。
- 禁止: 累計JPY80超過見込みでの続行/`run_e2e_01〜03`の`--mode real`起動/有料runの自動再起動(26節)/HR Lock・review_lock・Style Gate・SRC STOP・人称整合関所・AUW Gateの迂回・削除/Prompt・Style・Voice・コードの変更(evidence script新設は可。Production codeに不具合が見つかった場合は修正せずSTOP報告)/旧runのwav・`tts_generation_results`・audit・承認(`human_approved_segments`等)の持込/`ledger.json`のcommit/`user_test/family_z_melos_01`の変更/メロス本文の再生成(writer/std_adjustはreuse必須。reuseにならなければSTOP報告)。
- 固定ブロック: **E-1**(OPUS_REVIEW_E R-E6 F6-1/F6-2、ITEMS234_DESIGN_01 §4-6(prompt.txt退避)、FZ_COMPLETION_PLAN_01 §10/§11(run_e2e_03の実走手順)、`er063`の`REUSE_*`許可リスト、ユーザー試聴ページ標準フォーマット(CURRENT_SPEC 2026-10-18節、`tools/user_test_page_standard_check_01.py`))/**D-1**(不適用)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。並行agentなし。SSOTは自分の変更行のみstaged blob)/**F-1**(`run_e2e_04/cost_log.jsonl`実測を出典に工程別・種別(LLM/TTS/ASR)・実測/推定区分。¥300枠・別枠JPY100(run_e2e_03 36.38)とは分離し本件枠JPY80として記録)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_07.md`へ保存し`check_delegation_prompt.py --file <path> --json-out <path>_check.json`実行。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI7.md`、ACTIVE_TASK.md先頭へ自分のブロックのみEdit追記)。
- 使用モデル: Production配線済みrouting(変更しない)。実model_idを報告。

## Fable決定(記録用)
- Phase 3方式=Opus_E F6-1: 新run `run_e2e_04`を公式copy機構(`plan_reusable_run_assets`/`copy_reusable_run_assets`、テキスト系のみ)でrun_e2e_03から作成し、Std/AdvともTTSを全再生成。代償(Adv音声も再生成=試聴対象が全編)は最終報告に明示。
- 費用枠: 本件Phase 3上限JPY80(期待35〜40)。`--approved-budget-jpy 80`。超過見込みでSTOP。
- run_e2e_03は`STOP`センチネル(reason=`SUPERSEDED_BY_run_e2e_04 (Fable 2026-10-19)`、RUN_CLOSED不使用)で凍結。STOP_NOTICE(2026-10-12)は`status: RELEASED`済みで解除状態(再確認のみ)。
- 試聴ページは既存の`user_test/family_z_melos_02/`を**更新**(ユーザー指示§5「更新する」。旧版はgit履歴に残る)。標準フォーマット(共通builder)で生成し、標準適合check必須。
- 実行順序(F6-2): seed_check→writer(reuse)→std_adjust(reuse)→plan(reuse)→support: Adv reuse/Std=`--regenerate-stage support_a2`(新方式)→kp(reuse+人称整合関所がa2 rank2で発火し修復+provenance更新)→kp_expl(b1b: sig不変ならreuse)→tts_a2/tts_b1b(全再生成)→gate(AUW/6%減速/Dialogue)→assemble→pages→page_verify。runnerの`--stage all`で順序が担保されるならそれを使い、`--regenerate-stage support_a2`を併用。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01\OPUS_REVIEW_E_01_VERBATIM.md` R-E6
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01\ITEMS234_DESIGN_01.md` §4-6・§5
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01\FZ_COMPLETION_PLAN_01.md` §10・§11・§13(run_e2e_03実走・evidence・ページ生成の先例)
- `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZ17.md`・`RESULT_PACKET_FZ19.md`・`RESULT_PACKET_FZQI5.md`(関所の挙動)・`RESULT_PACKET_FZQI6.md`
- evidence script先例: `er026_fz_cost_17.py`、`er026_fz_style_table_17.py`、`er026_fz_play_verify_19.py`、`tools/user_test_page_standard_check_01.py`
- `C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py` `_gloss_person_gate`(:1317付近)・`stage_support`・`stage_pages`/`stage_page_verify`

## 事前指定Grep一覧+追記位置・更新位置の手順
- `CURRENT_SPEC.md`: Grep `OPEN-419|2026-10-19`(Family Z節の①〜④仕様文)→各項目に「runtime evidence取得済み(run_e2e_04、commit sha)・Fable判定待ち」を追記(PRODUCTION_WIREDとは書かない)。Grep `共通仕様のFamily別配線Status表`→変更不要(①はKP日本語意味行がなければ「X/Z共通module: Z=runtime evidence済み/X=コード配線(STOPのみ)・runtime待ち」を1行追加)。
- `OPEN_ITEMS.md`: Grep `OPEN-419`→Phase 3結果(evidence path・費用・項目別事実)。
- `DECISION_LOG.md`: 末尾に委任_07エントリ(事実のみ)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#23`→「改善版ページ(run_e2e_04)提示、ユーザー試聴待ち」へ更新(判断済みにしない)。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。
- 新規: `docs/research/FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01/PHASE3_RUN_E2E_04_RECORD_01.md`(実走記録・evidence一覧・費用・前後比較)。

## 作業(順序)
A. 実走前(JPY0): T-0。run_e2e_03へSTOPセンチネル設置。`*_prompt.txt`退避(設計書§4-6のコマンド)。copy計画dry-run→実copy(allowlist/deny件数を記録)。stop_scope_check(run_e2e_04)rc=0必須。当日費用照合(本日累計+80≤1,000)。runner dry-run(非課金モード)で stage計画・reuse見込み・Budget上限80を確認。
B. 実走(有料、1回起動、foreground、`TTS_EXECUTION_MODE=STANDARD`明示)。進行中に`cost_log.jsonl`/`e2e_stage_log.jsonl`を確認し80超過見込みでSTOP。HR Lock/各STOPは迂回せず報告。
C. evidence(JPY0、並列可):
 1. ①: `a2/key_phrases/*result.json`のrank2 gloss(旧「あなたの代わりに」→新)、`gloss_alignment_status=ALIGNED`、関所の修復記録(provenance entryの`output_sha256`更新・rank・理由・旧/新gloss)、`audit/src_z_posthoc_01.json`不変(S8 unique_containment)、P8-KP kp2_ja clipのテキスト。
 2. ②: `a2/support/support.json`の`method=adv_method_ja_v1`、`lint_warn`、`overlap_notes`、新旧のPreview/Comment1〜3全文(run_e2e_03 vs run_e2e_04の対照表)。Comment1の注目点が本文事実と整合するかの照合材料(該当Part抜粋)をFable用に添付(F3-2)。
 3. ③: Std Dialogue 10 clipの`effective_style_prefix_sha256`がAdvと同一(`add26d27…`)、`slowdown_applied=True`、比率(1.03〜1.09内)、ASR結果、王のセリフ(part1_c8相当)の長さ(旧run_e2e_03 Std 8.645秒/Adv 5.641秒との比較は参考値、WPM基準なし)、Voice割当21/21不変、Dialogue clipにPD06適用0。
 4. ④: writer/std_adjust が`reused`、語数WARN 0(408/387)、`*_prompt_gen350.txt`退避の存在、新prompt.txtに400が含まれる。
 5. 共通: `audit/style_record.json`(NEW_RUN、全Role)、segment style table(exp_match true/false、PD06/S3/E1/K2/P8-KP/P7/Dialogue)、Pages: 標準フォーマットで`user_test/family_z_melos_02/`更新→標準適合check PASS→commit/push→公開URL実再生(通し再生・シーク・audio数・console error 0)。
 6. 費用: `audit/cost_by_stage_04.json`(stage別・LLM/TTS/ASR別、合計/80、他枠と分離)。
 7. Regression再実行(er062/er026/er063/er003 gloss系)PASS数。
D. 記録: run_e2e_04の追跡対象(テキスト・audit json・pages。wav不可)commit→SSOT→PHASE3記録→commit→push。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_07.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_07.md_check.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\stop_scope_check_01.py --managed-id FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 --managed-id FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04 --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\stop_scope_check_fzqi7.json`
- copy: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -c "import er063_family_z_audio_01 as z; print(z.plan_reusable_run_assets(r'C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03', r'C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04'))"`(関数シグネチャは実装に合わせ、委任_16/_17で使った実手順(`run_e2e_03_copy_plan_16.json`生成時)を踏襲)
- dry-run: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py --run run_e2e_04 --mode dry-run --stage all --approved-budget-jpy 80 --tts-execution-mode STANDARD --regenerate-stage support_a2 2>&1 | tee C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\dryrun_07_console.log`
- 実走(PowerShell): `$env:TTS_EXECUTION_MODE="STANDARD"; C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py --run run_e2e_04 --mode real --stage all --approved-budget-jpy 80 --tts-execution-mode STANDARD --regenerate-stage support_a2 2>&1 | Tee-Object -FilePath C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\run_07_console.log`(kp_expl_b1bがProvenanceMismatchになる場合のみ`--regenerate-stage kp_expl_b1b`を追加して再計画。runner起動は1回のみ=再計画が必要ならdry-runで確認してから1回起動)
- 費用: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er026_fz_cost_17.py --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04 --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\audit\cost_by_stage_04.json`
- Style表: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er026_fz_style_table_17.py --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04 --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\audit\segment_style_table_04.json`
- 標準適合check: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\user_test_page_standard_check_01.py --page C:\Users\tensh\eigo-radio\user_test\family_z_melos_02\index.html --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\audit\page_standard_check_04.json`
- Pages実再生: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er026_fz_play_verify_19.py --url https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_02/index.html --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\audit\pages_play_evidence_04.json`
- 回帰: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I -m pytest C:\Users\tensh\eigo-radio\er062_family_z_writer_01_test_01.py C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01_test.py C:\Users\tensh\eigo-radio\er026_family_z_e2e_integration_test_01.py C:\Users\tensh\eigo-radio\er003_test_kp_gloss_person_alignment.py C:\Users\tensh\eigo-radio\er063_family_z_audio_01_test_01.py -q`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`(実在script名に置換)

## SSOT追記文(要点)
- CURRENT_SPEC(Family Z節 ①〜④): 「runtime evidence: run_e2e_04(2026-10-19、commit)。①関所発火・修復(rank2 旧→新)/②method=adv_method_ja_v1・lint_warn/③Std Dialogue sha=Adv同一・slowdown比/④writer reused・WARN 0。Fable判定待ち」。
- OPEN-419: 同旨+費用+試聴ページURL。REGISTER #23: 改善版提示・試聴待ち。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1(実走前): delegation_log 委任_07+_check.json、run_e2e_03 STOP(追跡対象なら)、退避prompt(追跡対象なら)。msg: `FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_07: Phase 3準備(run_e2e_03凍結・prompt退避・run_e2e_04 copy計画、JPY0)`
- commit 2(実走後): run_e2e_04追跡対象、`user_test/family_z_melos_02/**`、audit json、PHASE3記録。msg: `FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_07: 「走れメロス」run_e2e_04 正式Production E2E(①KP人称整合修復・②Std Preview/Comment Adv方式日本語・③Std Dialogue Adv同一Style+6%減速・④400±70 reuse)+音声全再生成+runtime evidence+標準フォーマット試聴ページ更新(JPY x/80)`
- commit 3: SSOT。msg: `FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_07: SSOT(runtime evidence・費用・#23試聴待ち、PRODUCTION_WIRED未宣言)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI7.md`)
ユーザー§6の順で事実のみ: (1)4項目の到達状態(事実)(2)①修復結果(旧→新gloss、ALIGNED、provenance更新、関所発火log)(3)②Preview/Comment前後対照全文+F3-2照合材料(4)③Dialogue sha/比率/長さ/ASR(5)④reuse・WARN 0(6)費用(stage別・/80・他枠分離)・所要時間(7)Git/SSOT/evidence path(8)試聴URL・未解決。4行+`判定整合:`+`判断候補:`。T-0 check。自己チェック: 1回起動/再起動なし/Gate迂回なし/累計≤80/本文再生成なし/旧承認持込なし/PRODUCTION_WIRED・聴感PASS未記載。
