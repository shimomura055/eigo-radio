## 管理ID

CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_03(Z Standard: Opus M2/M3/R6/R7を反映した`er063`/`er117`の実装+test+Z Std runtime evidence。`er063`はZ文脈TTS evidence取得が完了したため編集可)。並行Agent: (1)同管理ID 委任_02(X/Y是正+evidence。所有=er117のX/Y部分・er019・er121・`docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/{DESIGN_02,FIX_02,EVIDENCE_01,COST_01}.md`。**er117を両者が編集するため、本委任はer117の`plan_z_clip`レベル条件(:143-157付近)のみを編集し、他は触れない。commit前に`git fetch origin`+最新HEAD基準でhunk適用、競合時はSTOP**) (2)FZ SSOT同期(docs/SSOTのみ) (3)KP区分1(er105/er003_key_words_*) (4)Y男性7Voice Trial(有料)。本委任の所有=`er063_family_z_audio_01.py`(chunk関連)、`er117_chunk_tts_production_01.py`(Z条件のみ)、`er117_z_chunk_wiring_test_01.py`、新規`er063_z_std_chunk_test_01.py`、`docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/{DESIGN_Z_01,FIX_Z_01,EVIDENCE_Z_01,COST_Z_01}.md`+`measure_z/`、evidence run dir(`er026_output/family_z_production_e2e_01/<work>/run_stdchunk_ev_01`)、`docs/pm/delegation_log/2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_DELEGATION_03*`、`docs/pm/RESULT_PACKET_CHKW3.md`。SSOT・ACTIVE_TASKは編集しない。

## 性質/到達上限Status/禁止事項

- 性質: 承認済み仕様(APPROVED_FOR_PRODUCTION 2026-10-26、Z=約70語を目安とした段落境界分割B_r1+0.2秒、Std/Adv)のZ Std配線+runtime evidence。到達上限=Z Std: EVIDENCE_COLLECTED(PRODUCTION_WIRED判定はFable)。
- Fable照合: Opus M2/M3/R6/R7は承認済み仕様内の設計反映→全件採用。B_r1規則(閾値100語超・k=ceil(語数/100)・等分割・最小25語)はAdvと同一、再確認不要(Opus論点5)。
- 禁止: 分割規則・減速率・ポーズ長の変更禁止/Z Advの挙動変更禁止(b1bの`_z_chunk_parent_display`=None維持、`er063:1805`検査維持、Adv golden一致)/Zセリフ経路(ctx policy、`er122_*`、`story_clips_from_plan`)の挙動変更禁止(R6 test)/既存公開run上書き禁止/公開page出力禁止/Git禁止操作(`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・`reset --hard`・`checkout -f`・`git checkout -- <file>`)/wav・raw_usage_log・STOP・lock・RUN_LOCKはcommitしない/`the_monkeys_paw/run_fzcw_e1_01`(RESTART_STORM STOP残置)には触れない。
- 有料run規律: `.venv\Scripts\python.exe`、`TTS_EXECUTION_MODE=STANDARD`、各起動前`py tools/stop_scope_check_01.py`(rc=0)、起動間隔150秒以上(`Get-Date`記録)、同一run 5分以内3回起動禁止(**課金前に落ちる起動も回数に数える**。直前の委任で準備段階の起動3回によりRESTART_STORMが発生した。起動前にdry-run/引数検証を済ませる)。並行有料案件あり: 429/5xxはevidence扱いせず記録・150秒以上空けて再実行。T-2追記4点。
- 費用上限: 「上限¥60(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」見積=Z Std長narrator 1〜2 clip(各2 chunk)のTTS+減速後ASR≒数円〜約17円(BUDGET_PLAN_01)。dialogueのTTSは0回(reuse)であることが前提=T-2追記(2)でcache有無を確認し、dialogueが再生成される見込みならAPI実行前にSTOP。
- 修正範囲(11-8): 範囲内=M2(速度Gate `_CLIP_ID_RE`2箇所の拡張+chunk idの厳格減速検査、`_original.wav`弱証拠不使用)、M3(`er117:156-157`レベル条件撤去+`er063:598`撤去+`attach_chunk_meta(level=spec.level)`+`_z_chunk_parent_display`a2のみ集約+`drop_cached_std_chunks_without_slowdown`を`load_results`直後、同一commit)、R6(Std chunk展開plan→`story_clips_from_plan`が非chunk時と同一のtest、dialogue TTS 0回)、R7(Std chunkでLocal Rewrite経由出力に減速が掛かるtest)。
- Opus独立技術レビューGate: 条件A実施済み(本委任は反映)。
- 時間見込み: 2.5〜3時間(実装+test 90分、evidence 60分、集計30分)。並列化: 他案件と並列。
- 費用/日次: 当日(JST 2026-10-26)既使用JPY約260+進行中(Y Trial Cap 250・Chunk X/Y Cap 100)/本委任見積JPY約5〜17/承認区分: C。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。上記定型文に従う。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

委任文保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 648 --out docs\pm\delegation_log\2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_DELEGATION_03.md`(先頭が「## 管理ID」+「CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_03」でなければ644〜660を順に試す)→check実行。

## ユーザー指示(原文)

`docs/pm/delegation_log/2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_USER.md` §2(保存済み)。要点: 「Z: 約70語を目安とした段落境界分割(B_r1)+0.2秒、Standard/Advanced」「Standardを除外することは認めない」「各Family／各レベルの正式runtimeで、分割位置・Chunk数・追加ポーズの発火証拠を取得する」「X/Zで既に確認済みのAdvanced動作を回帰させない」。

## 事前指定Read一覧

1. `docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/DESIGN_01.md` §6(Z設計)・§7、`OPUS_REVIEW_01.md`(保存済みなら。未保存なら委任_02が保存するため`docs/pm/RESULT_PACKET_CHKW1.md`と本委任文のM2/M3/R6/R7記述を正とする)、`FIX_01.md`(X/Y実装の方式を踏襲)。
2. `er063_family_z_audio_01.py` :580-640(chunk展開・`_z_chunk_parent_display`)、:1520-1570(load_results・only-clips再利用・Local Rewrite・attach_chunk_meta)、:1660-1680(速度Gate対象id)、:1725-1740(`_CLIP_ID_RE`関数内)、:1800-1810(b1b検査)、:1860-1870(呼出側)。`er117_chunk_tts_production_01.py` :140-160(`plan_z_clip`レベル条件)、:330-370(`std_chunk_slowdown_violations`・`std_parent_slowdown_fields`)、:400-475。
3. `er122_fz_ctx_notes_01.py` :165-195(`story_clips_from_plan`、R6)。
4. `er117_z_chunk_wiring_test_01.py` :120-140, :195-210(書換え対象)。Glob `er063*_test_*.py`。
5. Z正式run: `er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01`(Std narrator 129/139語)と`melos/run_fzcw_e1_01`(ctx方式のdialogue済み・直近)の`tts_generation_results.json`・plan(どのrunをevidence元にするか: **melos run_fzcw_e1_01のtext資産を新run `run_stdchunk_ev_01`へ許可リストcopy(音声・stateは持ち込まない)し、Std narrator 134語clipのみ`--only-clips <親id>`でTTS**を既定。dialogueはcache再利用=TTS 0回を期待。tell_taleはseed provenanceを確認してから選択)。
6. `er026`runner Grep `--only-clips|--stage|E2E_STAGES|--budget-jpy`→引数。`tools/stop_scope_check_01.py --help`。

## 事前指定Grep一覧+追記位置・更新位置の手順

- Adv不変golden: 実装前HEADでZ Adv 2 run(tell_tale/melos)のchunk plan+`_z_chunk_parent_display`出力を凍結→実装後バイト一致test。
- SSOT文案のみ(RESULT_PACKETへ): CURRENT_SPEC Chunk TTS節のZ Std行、DECISION_LOG、OPEN-532、OPUS台帳OF-CHKW-M2/M3/R6/R7。

## 実行コマンド全文

- 回帰(遮断下、`.venv`): `$env:PYTHONPATH="netblock_harness_01"; .venv\Scripts\python.exe run_project_regression.py --pattern "er117*_test_*.py"`、同`"er063*_test_*.py"`、`"er122*_test_*.py"`、`"er026*_test_*.py"`(前後PASS/FAIL集合比較、接続試行0または前後同数)。
- 新規test: `$env:PYTHONPATH="netblock_harness_01"; .venv\Scripts\python.exe -m pytest er063_z_std_chunk_test_01.py er117_z_chunk_wiring_test_01.py -q`(M2: 減速なしStd chunkで`FamilyZSlowdownGateStop`/M3: b1b display None維持・a2集約/R6: Std chunk展開→`story_clips_from_plan`同一・dialogue TTS 0/R7: LR経由出力に減速/Adv golden一致/`drop_cached_std_chunks_without_slowdown`位置)。
- evidence(例、実値で。起動前にdry-run等で引数検証を済ませ、課金前失敗を含め5分内3回起動を避ける): `py tools\stop_scope_check_01.py`→`Get-Date`→`$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er026_family_z_production_runner_01.py --work melos --run run_stdchunk_ev_01 --level a2 --stage tts,gate,assemble --only-clips <親narrator id> --budget-jpy 30`(runner実名・引数は`--help`で確認)。150秒後に同引数で再起動し新規TTS 0回(chunk再利用)を確認。
- 計測: `py docs\research\CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01\tools\chunk_evidence_measure_01.py --run <run dir> --out …\measure_z\<name>.json`(委任_02が同名scriptを作成中。存在しなければ`chunk_evidence_measure_z_01.py`として自作: chunk語数・分割位置・0.2秒無音位置/サンプル数・各chunkの減速比率・境界無音・peak・TTS call数・厳格Gate判定・dialogue TTS 0回)。
- Zセリフ経路不変: `git diff --stat -- er122_fz_ctx_policy_01.py er122_fz_ctx_notes_01.py er012_b_family_voices_production_01.py er003_v1_n3_01_tts_generate.py`(本委任由来0)。
- secret grep: `git diff --cached | findstr /R /C:"sk-[A-Za-z0-9]" /C:"AIza[A-Za-z0-9_-]" /C:"BEGIN PRIVATE KEY"`。

## 成果物

`DESIGN_Z_01.md`(M2/M3/R6/R7の実装設計・Adv不変・ctx経路不変)、`FIX_Z_01.md`(差分要約)、`EVIDENCE_Z_01.md`(Z Std: chunk数・語数・分割位置・0.2秒位置・減速比率・厳格Gate PASS・dialogue TTS 0回・再利用0回・境界無音・peak・費用。Z Adv既存evidence参照)、`COST_Z_01.md`、`docs/pm/RESULT_PACKET_CHKW3.md`。

## SSOT追記文

文案のみ(上記)。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: なし。
- commit 2分割: (1)実装+test+DESIGN_Z/FIX_Z (2)evidence(md/json/measure、wav不可)。er117は自hunkのみ(`git fetch origin`後の最新HEAD基準、競合はSTOP)。
- message例: (1)`CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_03: Z StandardへB_r1 Chunk分割+0.2秒を配線(Opus M2/M3/R6/R7: 速度Gate厳格化・レベル条件撤去同時実施・ctx経路不変test、Adv golden一致、API 0)` (2)`CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_03: Z Std runtime evidence(melos narrator 134語→2 chunk、減速比率・0.2秒・厳格Gate、dialogue TTS 0、実費<X>円)`。
- `git push origin HEAD:main`(non-fast-forwardは`git fetch origin`→`git merge --no-edit origin/main`→再push。競合は両方残してSTOP)。

## 報告(RESULT_PACKET項目)

(0)T-0 (1)結論(Z Std実装・evidence、PRODUCTION_WIRED判定材料の充足/不足) (2)M2/M3/R6/R7反映表(ファイル:行・test名) (3)evidence詳細 (4)test・Adv golden・ctx経路不変 (5)費用(起動時刻・実費/Cap 60、課金前失敗起動の回数) (6)SSOT文案 (7)commit×2・raw URL (8)一覧外Read (9)Fable向け懸念。最終行に要約10行以内。