# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_16(ユーザー#108/#109承認の反映+SRC D1方式のProduction実装・test+既存FAIL 9件切り分け+STOP_NOTICE解除通知+run_e2e_03 実走準備。**JPY0=有料API呼出0**)。日付: 2026-10-17。

## 性質・到達上限Status・禁止事項
- 性質: SSOT記録+Production code実装(承認済み仕様の正式配線)+test+実走準備(dry-run/read-onlyまで)。
- 到達上限Status: `SRC_D1_WIRED_CODE_TESTED_RUN03_READY_PENDING_FABLE_CP`。本委任でPRODUCTION_WIREDは宣言しない(runtime evidenceは次委任_17の有料実走後にFableが判定)。
- 禁止: 有料API呼出(LLM/TTS/ASR/Web)一切/音声・原稿・KPの再生成/`run_e2e_03`の`--mode real`起動/KP選定Prompt・優先順位・候補供給方式の変更/Family X M2P0等の候補ID方式のZ導入/既存Source Consistency Gate・canonicalization等の品質検証の緩和/D2等への方式変更/Style・Voice・Prompt変更/Landing更新/新Trial。
- 固定ブロック: **E-1**(既存仕様・過去Trial照合: SRC正本=CURRENT_SPEC.md:1919付近 candidate_id_v1、Z設計=FZ_COMPLETION_PLAN_01 §5(c)(d)・SRC_Z_POSTHOC_DRYRUN_01・OPUS_REVIEW_C R-C3)/**D-1**(DefaultOff隔離は不適用=ユーザー承認済み仕様の正式配線。承認根拠=本委任のユーザー原文#109)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0確認後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。commitは直列・同時1件)/**F-1**(本委任JPY0。費用数字は出典付き、未確認は出さない)/**T-0**(本委任文を全文そのまま`docs/pm/delegation_log/2026-10-17_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_委任_16.md`へ保存し`check_delegation_prompt.py`を実行、`_check.json`保持。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`docs/pm/RESULT_PACKET_FZ16.md`、ACTIVE_TASK.md先頭へ新ヘッダ追加・旧ヘッダ保持)。

## ユーザー指示原文(2026-10-17、逐語。`docs/pm/delegation_log/2026-10-17_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_PHASE2-RESUME-108-109_USER.md`へ原文のまま保存し、文字数とsha256を報告)
---
# Claude Code／Fableへの回答・指示
## Family Z「走れメロス」Production E2E — Phase 2再開

**管理ID：FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01（継続）**

### 1. ユーザー正式判断

**#108：追加費用100円を承認**

- 「走れメロス」Production完成作業に、既存300円枠とは別枠で**JPY100**を承認する。
- 期待費用：約45円。
- 追加100円を超過する見込みが生じた場合はSTOP。
- 既存費用と今回の追加費用を分離して記録する。

**#109：SRCのD1方式を正式採用**

Family Zの既存KP選定方式（Strategy L）を維持し、選定結果をPythonで元英文と照合する方式を採用する。

具体的には、

1. 従来どおり、AIが本文からKPを選定する。
2. 選定されたKPについて、Pythonが元英文の該当箇所・文ID・位置を特定する。
3. 対応が一意に確認できれば、出典情報を決定論的に記録する。
4. 対応を確認できない場合は、推測で補完せずSTOPする。

**目的はKPの出典保証であり、KP選定品質や選定方針の変更ではない。**

Family Xの候補ID選定方式（M2P0等）をFamily Zへ導入しない。既存KP選定結果を最大限再利用する。

本方式をFamily ZにおけるSource Reference Contractの正式実装方式として`APPROVED_FOR_PRODUCTION`に記録する。

### 2. Phase 2の実施範囲

先のユーザー指示およびPhase 1棚卸し結果に従い、承認済みのProduction整備を再開すること。

対象：

- Family Z「走れメロス」
- Story 3分割＋Comment 3つ
- Sol R0→R1→R2、Advanced→Standard調整
- Family Xと共通化する音声仕様
- Dialogue別Voice
- Source Reference Contract（D1方式）
- 正式Production E2E、ASR、Assembly、試聴ページ

新しい記事・Prompt探索・追加Trialは行わない。

### 3. 既存成果の再利用

既存`run_e2e_02`の以下を原則再利用する。

- Advanced／Standard本文
- Story 3分割
- Preview／Comment
- KP選定結果

原稿から無条件に作り直さない。

正式Production経路のprovenance・Stage整合を確認したうえで、新規runへ引き継ぐ。

過去のHuman Review承認は、Style変更後の新規生成音声へ自動継承しない。

### 4. 音声Production配線

Family Xで正式採用された以下の音声仕様をFamily Zへ適用する。

| Role | 適用Style |
|---|---|
| Full Story Narrator | PD06 |
| Standard日本語Preview／Comment | S3 |
| Advanced英語Preview | E1 |
| KP英語 | K2 |
| Standard KP日本語意味 | P8-KP |
| Advanced KP英語解説 | P7 |
| Standard英語Full Story | 既存6%減速 |
| ASR／音声品質 | 承認済みAUW |

既に適用済みのE1・K2等は、不要に再実装・再生成しない。

**FictionのDialogueはFamily Z固有仕様として別Voiceを維持する。** NarratorのPD06をセリフに一律適用しない。

retry／fallback／regeneration／resumeを含め、承認済みStyleとVoice割当の整合性を確認する。

### 5. SRC D1方式の実装条件

D1は、Family Zの既存Strategy Lに適合させるための実装方式である。

- KP選定Prompt・優先順位・候補供給方式は原則変更しない。
- Pythonによる出典特定は決定論的に行う。
- 既存のSource Consistency Gate／canonicalization等の品質検証を弱めない。
- 同一表現が複数箇所にあるなど、一意に特定できない場合は勝手に採用箇所を決めない。
- 曖昧・不一致の場合は既存の安全なSTOP／再確認経路と整合させる。
- 初回生成だけでなくretry／fallback／再生成でもSRCが有効であることを確認する。

Opus独立レビューで承認方式に抵触する重大な問題が見つかった場合は、独断でD2等へ変更せずSTOP・報告すること。

### 6. Production Wiring Gate

今回の到達目標は、対象仕様の`PRODUCTION_WIRED`と、正式E2Eの技術的完走である。

以下をすべて確認すること。

1. 正式Production初回経路への実装
2. retry／fallback／regeneration／resumeとの整合
3. Trial／DEV専用経路ではないこと
4. 正式runtimeでの実発火証拠
5. actual model_id・Style SHA・Voice・routingの一致
6. 必要なRegression／Validator／integration testのPASS
7. AUW／ASR・6%減速・Dialogue切替・AssemblyのPASS
8. Dangling Reference Check
9. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSの更新
10. commit／push／mergeの確認

Phase 1で確認された既存テストFAIL 9件は、原因を切り分けること。今回の変更に起因するFAILや必須品質GateのFAILを放置して完了扱いにしない。

### 7. 費用・作業効率

- 今回の追加承認枠：**JPY100**
- 期待：約JPY45
- Web／LLM／TTS／ASR／再試行等を含めて実費記録
- 日次JPY1,000のsoft budget維持
- 既存成果を最大限再利用
- 不必要な再生成・再検索を避ける
- 独立して安全に実行できるread-only作業・検証は並列化してよい
- Git変更・commit作業の競合を避ける

費用上限超過見込み、重大品質問題、未承認仕様変更が必要になった場合はSTOP。

### 8. Cross-Family運用・既存判断

Cross-Family同時Production配線原則は、先に承認された上位ルールとしてPM_GOVERNANCE／CURRENT_SPEC等へ正式反映すること。

今回のFamily Zへの音声仕様展開とSRC配線を、Family別のStatus表で追跡する。

Family固有仕様や明示的な不採用仕様は維持する。

Preview／Comment 1については既存方式を維持し、新しいA/B方式は採用しない。追加Trialは不要。

Risk FlaggerはFamily X固有仕様のため、Family Zには追加しない。

### 9. 最終報告

作業終了時に以下を簡潔に提示すること。

1. 「走れメロス」正式Production E2Eの完走可否
2. Standard／Advanced試聴ページURL
3. SRC D1方式の適用結果と実際の出典照合結果
4. PD06・S3・P7・P8-KP等のruntime適用証拠
5. Dialogue別Voiceの確認結果
6. 既存成果の再利用範囲
7. 実測費用／100円上限との差額
8. Regression／AUW／ASR／Assembly結果
9. 各仕様の`PRODUCTION_WIRED`判定
10. 未解決Open Item・ユーザー判断事項

**E2E技術的完走とユーザー試聴PASSは区別すること。**

最終音声が完成した段階で試聴ページを提示し、ユーザー判断を求めてSTOPする。

今回承認した#108・#109について、重複してユーザー判断を求めないこと。
---

## Fable決定(本委任で確定。再質問しない)
- F1 STOP_NOTICE(2026-10-12)の解除: Fable権限で解除する。ファイルは削除せず、末尾へ「## 解除通知(Fable、2026-10-17)」節を追記(内容: ユーザー2026-10-17指示(#108承認・Phase 2再開)により、`run_e2e_03`(新run)に限り有料実行を再開可。`run_e2e_01`/`run_e2e_02`の`--mode real`再起動は引き続き禁止。26節の実行層ルールは維持)。追記後`tools/stop_scope_check_01.py`を実行し結果(rc/stop)を記録。`run_e2e_01`配下の`STOP`センチネルは触らない。
- F2 Pronunciation Ledger entry `ec716e185835dba3`(作業ツリー未commit): **維持(commitしない)**。Production cascadeが正規経路で追記した実データであり、M1監査=承認範囲内(α)。Phase 3はこの作業ツリー状態で実走する。DECISION_LOGに「run_e2e_03はLedger entry `ec716e185835dba3`が作業ツリーに存在する状態で実行。Std part1_c5『Melos said.』がM1融合受理でPASS_WITH_WARNINGになった場合も、ユーザー試聴リストへ明示し、人手Review Lockが発火した場合はSTOP・報告(事前承認なし)」と記録。`er006_output/pronunciation_ledger_01/ledger.json`は本委任でcommitしない。
- F3 SRC D1の引用符内分割(SRC_Z_POSTHOC_DRYRUN_01 §結論2): **後者を採用**=spanを含む1文のみを`source_sentence_id`として採用し、引用符跨ぎ(前半文脈欠落)をtelemetry(`quote_boundary_truncated: true`)に記録。採用理由をDECISION_LOGに1行。
- F4 Opus: SRC D1強化版はOPUS_REVIEW_C(R-C3、GO_WITH_FIXES)でレビュー済み。設計が変わらない限り再レビューしない。実装中に承認方式(D1)に抵触する重大問題が出たらD2等へ変更せずSTOP・報告。
- F5 Adv Comment Style: ユーザー表に記載なし→Z既存(E2_UPBEAT)を維持(Family固有の現状維持、ユーザー§8「Family固有仕様は維持」に整合)。CURRENT_SPEC Status表に「Z固有・現状維持」で1行記録。再質問しない。
- F6 本委任は有料実行をしない。実走(`run_e2e_03 --mode real`)はFable CP後の委任_17。

## 事前指定Read一覧(全文読込禁止ファイルは該当行のみ)
- `docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/FZ_COMPLETION_PLAN_01.md` §5(c)(d)(f)・§6(L86-101)
- `docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/SRC_Z_POSTHOC_DRYRUN_01.md`(全文、短い)+`src_z_posthoc_dryrun_01.py`(再利用して実装の核にする)
- `docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/OPUS_REVIEW_C_01_VERBATIM.md` R-C3・R-C4該当部のみ
- `docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/M1_MELOS_SAID_AUDIT_01.md` 結論部
- `er030_key_phrase_db_hybrid_source_reference_contract_01.py`(X側SRC実装。telemetry/監査記録の形式を揃える参考)
- `er026_family_z_fiction_production_runner_01.py` KP stage周辺(Grep `ensure_stage|install_kp_assets|regenerate-stage|resume|retry`の該当関数)
- `er063_family_z_audio_01.py`の`plan_reusable_run_assets`/`copy_reusable_run_assets`/`classify_reuse_path`定義部
- `docs/pm/delegation_log/2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_STOP_NOTICE.md`末尾
- `docs/pm/PM_GOVERNANCE.md` 26-2・26-3・26-5(L3394-3412)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `CURRENT_SPEC.md`: Grep `Source Reference Contract|candidate_id_v1`(1919付近)→直後にZ正式方式の追記/Grep `共通仕様のFamily別配線Status表`(1654付近)→SRC行のZ列を「APPROVED_FOR_PRODUCTION(D1方式、2026-10-17 #109)・コード配線済み・runtime evidence待ち」へ、Adv Comment行(無ければ追加)を「Z固有・現状維持(E2_UPBEAT)」/Grep `1608`付近の¥300承認行→「別枠JPY100承認(2026-10-17 #108、期待約45、超過見込みSTOP、既存累計と分離記録)」を追記。
- `DECISION_LOG.md`: Grep `^## ` 末尾3件で書式確認→末尾に新エントリ(ユーザー2026-10-17 #108/#109承認、F1〜F5のFable決定、SRC D1=APPROVED_FOR_PRODUCTION(Z)、PRODUCTION_WIREDは未)。
- `OPEN_ITEMS.md`: Grep `OPEN-412`→Status更新(SRC: APPROVED_FOR_PRODUCTION・コード配線済み・runtime待ち)/Grep `OPEN-414`→9件の切り分け結果を追記/Grep `OPEN-413`→「ユーザー§8で正式反映確認」注記。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#108|#109`→判断済み(2026-10-17、原文sha)へ。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。
- 既存FAIL 9件: `OPEN_ITEMS.md` OPEN-414 と `FZ_COMPLETION_PLAN_01.md` §1(g)(L38-43)の一覧を正とする。

## 作業(順序。A〜Dはcommit単位で直列、Eは並列可のread-only)
### A. 記録(commit 1)
ユーザー原文保存/REGISTER #108・#109判断済み/CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS更新(上記)/STOP_NOTICE解除通知追記(F1)+stop_scope_check実行記録。
### B. SRC D1方式のProduction実装(commit 2)
1. `src_z_posthoc_dryrun_01.py`の`build_sentence_units`/`restore_source_fields`を正式moduleへ昇格(例: `er026_family_z_src_posthoc_01.py`、Trial/DEV専用経路ではなく正式runnerがimport)。ラベル`z_sentence_id_posthoc_v1`。
2. 配線位置: er026 runnerのKP stage=`ensure_stage(kp)`成功後・`install_kp_assets`前の**Gate関数**として組み込む。**初回生成・再利用(provenance経由reuse)・`--regenerate-stage kp_*`・retry(外側3回)・resume のすべてで同じGateを通る**ことをコード経路で保証(各経路のcall siteを列挙して報告)。
3. 動作: 各KPについて一意(unique_containment)に文IDを解決→`source_sentence_id`/`source_span`/`source_sentence`/`resolution_method`/`quote_boundary_truncated`をKP成果物とaudit(`audit/src_z_posthoc_01.json`)へ決定論的に記録。曖昧(複数一致)・不一致(0一致)は**推測補完せず**、既存の安全STOP経路(KP stageの既存STOP/再確認の仕組みに合わせる。無ければ`FamilyZSourceReferenceStop`例外でstage失敗→既存retryへ)で停止。既存Source Consistency Gate・canonicalizationは一切緩めない(呼出順序・判定を変更しない)。
4. 「KP選定Prompt・優先順位・候補供給方式」は不変であることをdiffで示す(Prompt文字列・候補供給関数に変更なし)。
5. test: 新規`er026_family_z_src_posthoc_01_test_01.py`(一意解決/曖昧STOP/不一致STOP/引用符跨ぎtelemetry/正規化差の扱い/reuse経路・regenerate経路でGateが呼ばれること(monkeypatchでcall確認)/kp_expl署名(委任_15で指摘のsig fix)を含む)。既存Z回帰(er063* / er026 Z系4 module / er006)を再実行しPASS数を報告。
6. run_e2e_02のKP 10件に対して正式Gate関数をoffline適用(有料0)し、10/10解決・曖昧0・引用符跨ぎ件数を`audit`相当の一時出力(`er026_output/family_z_production_e2e_01/melos/_src_offline_check_16.json`)で示す。
### C. 既存FAIL 9件の切り分け(commit 3、記録のみか軽微是正)
各FAILを「今回変更起因/既存・環境起因/Ledger依存(是正済み)/隔離実行が必要/必須品質Gate該当か」に分類し、OPEN-414へ表で記録。今回変更起因または必須品質Gate該当は必ず是正。er020は別管理のまま(触らない)。`er026_family_z_stop_sentinel_test_01`は隔離実行(単独process)でPASSするかを確認し結果を記録。
### D. run_e2e_03 実走準備(有料0、commit 4=計画書追記)
1. `plan_reusable_run_assets`で run_e2e_02→run_e2e_03 のcopy計画をdry-run出力(allowlist対象・除外(review_lock_state/human_approved_segments/audit/wav)を列挙)。実copyは行ってよい(ファイル操作のみ、課金なし)が、`--mode real`は起動しない。
2. provenance/ensure_stageで writer/std_adjust/plan/support/kp が「reuse」になることをdry-run(`--mode dry`等、存在する非課金モード)で確認。非課金モードが無ければ静的に経路を示す。
3. 費用見積: 全Role TTS再生成+ASR(AUW 3回フロー上限)+SRC(LLM 0)の内訳を、run_e2e_02の`cost_log.jsonl`実測単価から算出(出典明記)。上限=JPY100、期待≈45。超過見込みなら理由を報告。`--approved-budget-jpy 100`で起動する前提で、runner側の累計がrun_e2e_01/02の既存費用と分離して記録されることを確認(分離方法を明記)。
4. `FZ_COMPLETION_PLAN_01.md`へ「## §10 委任_16 実走準備記録」を追記: 実走CLI全文、stop_scope_check結果、copy計画、見積、Gate一覧(AUW/6%減速/Voice assignment/Dialogue切替/Assembly/HR Lock)、STOP条件(累計>100見込み/HR Lock発火/Style sha不一致/SRC STOP)。
### E. 並列可(read-only): Dangling Reference Check再走(er071/er078の歴史script2件は記録のみ)、`er019_family_x_style_profile_01`定数sha vs `er063`固定shaの一致確認。

## 実行コマンド全文(代表。pythonは`.venv\Scripts\python.exe`、`-I`付き)
- `.venv\Scripts\python.exe -I docs\pm\tools\check_delegation_prompt.py docs\pm\delegation_log\2026-10-17_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_委任_16.md`
- `.venv\Scripts\python.exe -I tools\stop_scope_check_01.py`(引数は既存usageに従う。結果をRESULT_PACKETへ)
- `.venv\Scripts\python.exe -I -m pytest er026_family_z_src_posthoc_01_test_01.py er063_family_z_audio_01_test_01.py er063_family_z_common_style_wiring_01_test_01.py er063_family_z_audio_01_pd06_run_style_test_01.py er026_family_z_e2e_integration_test_01.py er026_cs_audit_regression_01_test_01.py er026_post_slowdown_cascade_rescue_01_test_01.py er006_model_routing_pricing_coverage_test_01.py -q`
- `.venv\Scripts\python.exe -I -m pytest er026_family_z_stop_sentinel_test_01.py -q`(隔離・単独)
- `.venv\Scripts\python.exe -I er026_family_z_fiction_production_runner_01.py --run run_e2e_03 --mode dry --stage all --stop-after kp --approved-budget-jpy 100 --tts-execution-mode STANDARD`(非課金モード名は実装のusageで確認し、実在するものに置換。`--mode real`禁止)
- `.venv\Scripts\python.exe -I tools\secret_scan*.py`(既存scan、hits=0確認)
- 実走CLI(**本委任では実行しない**、§10へ記載のみ): `.venv\Scripts\python.exe -I er026_family_z_fiction_production_runner_01.py --run run_e2e_03 --mode real --stage all --approved-budget-jpy 100 --tts-execution-mode STANDARD`

## SSOT追記文(要点。文言は既存書式に合わせる)
- CURRENT_SPEC(SRC節): 「Family Z正式方式=D1(`z_sentence_id_posthoc_v1`): Strategy L選定結果へPythonが決定論的に文ID/spanを事後付与。一意解決のみ採用、曖昧・不一致はSTOP(推測補完なし)。Prompt・優先順位・候補供給不変。引用符跨ぎは1文採用+telemetry。2026-10-17ユーザー#109 APPROVED_FOR_PRODUCTION。PRODUCTION_WIREDはrun_e2e_03 runtime evidence後」。
- CURRENT_SPEC(費用): 「FZ別枠JPY100(2026-10-17 #108)、期待約45、超過見込みSTOP、¥300枠の既存累計とは分離記録」。
- DECISION_LOG: ユーザー#108/#109+Fable決定F1〜F5。
- OPEN_ITEMS: OPEN-412/413/414更新(上記)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1: delegation_log 2件(USER原文・委任_16+_check.json)、CURRENT_SPEC.md、DECISION_LOG.md、OPEN_ITEMS.md、USER_DECISION_REGISTER_01.md、REPORT_LEDGER.md、STOP_NOTICE.md(追記分。git追跡済みなら含める)。msg: `FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_16: ユーザー#108(別枠JPY100)/#109(SRC D1正式採用=APPROVED_FOR_PRODUCTION)原文保存+SSOT反映+STOP_NOTICE解除通知(run_e2e_03限定)+Fable決定F1〜F5`
- commit 2: 新module・runner変更・新test・既存test更新・`_src_offline_check_16.json`。msg: `FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_16: SRC D1方式(z_sentence_id_posthoc_v1)を正式KP経路へGate配線(初回/reuse/regenerate/retry/resume共通、曖昧・不一致STOP、引用符跨ぎtelemetry)+test(JPY0)`
- commit 3: OPEN_ITEMS.md(+是正test)。msg: `OPEN-414: 既存FAIL 9件の切り分け(分類表・隔離実行結果・是正分)`
- commit 4: FZ_COMPLETION_PLAN_01.md §10(+copy計画json)。msg: `FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_16: run_e2e_03 実走準備記録(copy計画・見積・Gate・STOP条件、有料0)`
- `er006_output/pronunciation_ledger_01/ledger.json`および他の`*_output/`runtime差分はaddしない(作業ツリー維持)。

## 報告(RESULT_PACKET項目: `docs/pm/RESULT_PACKET_FZ16.md`)
4行: (1)整合(SSOT編集行番号、SRC正本との整合)(2)Production到達経路(SRC Gateのcall site一覧=初回/reuse/regenerate/retry/resume、Prompt不変のdiff証拠)(3)最終成果物とcommit sha 4件、test PASS数、offline SRC 10件結果、stop_scope_check結果、見積(出典)、実走CLI(4)撤去/残置(FAIL 9件分類表の要約、Dangling結果)。`判定整合:` 重大NGの有無。`判断候補:` [A]〜[D]形式(なければ「なし」)。T-0 check結果。自己チェック: 有料0か/`--mode real`未起動か/Prompt・候補供給不変か/品質Gate未緩和か/#108・#109を再質問していないか/ledger.json未commitか。
