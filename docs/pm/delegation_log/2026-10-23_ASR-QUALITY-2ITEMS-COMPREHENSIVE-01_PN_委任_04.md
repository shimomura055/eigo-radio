FABLE-DELEGATION-MARKER: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-PN-委任_04-PRODUCTION-IMPL-20261023

# 委任_04(①RET): Opus条件Cレビュー(必須OF-PN-W-01〜07、推奨08〜15)を反映してProduction実装→test/回帰→X runtime evidence。Z evidence(Bertie 4clip)は後続のB工程委任で取得(本委任ではZ実行しない)。APPROVED_FOR_PRODUCTION(UDR #168)に基づく正式実装。費用上限15円(X evidence)。

## 前提読込
`docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/PN/{WIRING_DESIGN_01,DESIGN_02,TRIAL_RESULT_01,OPUS_REVIEW_01}.md`、`docs/pm/RESULT_PACKET_ASRQ_PN3.md`、受入条件=`docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER_02.md` §2。Trial実装 `er111_pn_*`。

## T-0・Git運用(厳守)
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_PN_委任_04.md`(index 370以降、先頭MARKER一致)。
2. **Opusレビュー本文を保存**: 下記所見を `PN/OPUS_REVIEW_02_COND_C.md`(Fable転記と明記)。
3. ACTIVE_TASK自分の行のみ(並行: UKUS実装[er109系、同時にer078_reuse_value_guard/er019継承/allowlistの近接hunkを触る]、FX-KP 委任_05、FAMILY-Y 委任_08[有料run中の可能性])。**pythonプロセスは自分が起動したPIDのみ終了可、イメージ名一括kill禁止。commitは `git commit --only -- <path…>` でpath限定、直前に `git diff --cached --name-status` で意図しないD/Aが無いことを確認。一時index/commit-treeは使わない。共有ファイル(er078/er019/allowlist/SSOT)は編集直前に `git pull --ff-only` 相当の最新化→自分のhunkのみ→即commit→push。競合時はrebaseせずFableへ報告。TTS実行前に他行「有料run(TTS)進行中」を確認・待機。**

## Fable判定(記録用)
Opus総合判定=「必須修正後に実装可、再設計不要」。骨格(新module+er103本体統合、PNAP scope、既定ON+1行rollback、hook 1か所、保存entryからの復元)は一致。対立点6(寄与判定の反実仮想化/等価性testの強化/増分表をそのまま判定に使わない/表の自動取得範囲/発火証拠の取り方/LR後text)はいずれも安全性・検証の技術修正→**Fable判断で実装へ進む**。PRODUCTION_WIREDはFable受入後(X/Z双方のevidence必須)。

## Opus所見(逐語要約)
- W-01[必須] 「表が受理に寄与したか」は反実仮想で判定: Primary句ごとにまず元の `ledger_surfaces` で `_noun_checks` を実行し、`R_NOT_PROPER_EVIDENCE` で落ちたときだけ `ls|grant` で再判定、その場合だけ `per_diff`/`entries_used`/`alarm_labels`/`entity_table` キーを付ける(Secondary同様)。grantで変わるのは `proper_noun_evidence` のみ(`is_general_word` はledger非依存 er103:267)。
- W-02[必須] 等価性test強化: (a)単調性test=D1/D2/fixtureにTrial実表を与え、表なし受理は表ありでもバイト一致 (b)差分test=Trialの `evaluate_alarm_eligibility_pn` をtestからのみimportし全コーパスで accept/reason/diffs(canonical)一致 (c)無関係表でもG3不受理分岐で `ret3_rejected` が付く矛盾→期待値を「accept/reason一致、detailは追加キーのみ許容」にするかキーを付けない設計に。署名は `evaluate_alarm_eligibility` への入力(cls diffs直列化)で凍結(上流再計算だと②UKUS導入で署名が動く)。
- W-03[必須] 表の導出属性(eligible `lowercase_seen`、見出し除外、`_det_support`)は全textに依存→保存はLLM生候補+coverageのみ、判定用の表は毎回の構築点で「今のprovider textの和集合」に対し決定論(API 0)で再計算、今のtextに逐語出現しない旧entryは外す。Zも両levelの脚本が揃えば和集合を渡す(Zは1構築あたり最大2(A+B)×2 level=4 callになり得る点を是正)。
- W-04[必須] 継承・Store再判定経路では `current_table()` を自動取得しない: 自動取得はadapter経路(er006_secondary_asr_01.py:827)に限定(センチネル引数または明示渡し)。継承は復元表かNoneを必ず明示。継承で受理したら `pronunciation_alarm.entity_table` を `dec.detail` で更新。
- W-05[必須] RET-3: span内tokenが `supply_map` に含まれる場合は不適用(`ret3_rejected="supplied_token_in_span"`)、test固定。
- W-06[必須] Store再利用: `guard_entry` は再判定NGでも保護理由でなければ `blocked=False`(REJUDGE_NG_NOT_PROTECTED er078:92-96)→呼出元(Z `generate_or_reuse_z`、X)が再生成するか確認。しなければA-11条件を `entity_contributed ∧ (not ret.is_active_for_run() or not 復元可能[builder_version不一致])` に広げ明示block。
- W-07[必須] 発火証拠はX/Zとも正式runner経由: X-2の対象を `pool_n8_airport_line` の `point_two`(Kristie Tse、系統的誤読)にし正式入口 `--only-segments` で再生成(自然発火の可能性高)。Zは Bertie 4clipを正式runnerで(B工程)。発火しなければ予備策=正式runnerの生成器差し替え(Z `run_tts_stage(generators=...)`)で保存誤読wavをreplay(隔離run_dir、Store書込は隔離/無効化)。harnessのみの証拠では PRODUCTION_WIRED にしない(証拠区分を受入記録に明記)。
- W-08[推奨] LR時NERなしは許容(fail-closed)だが「LRで新たに出た固有名詞は表外=現行挙動(受理範囲は縮小方向)」とDECISION_LOGに記録。LRで名前を残したtextも既存entryの `occurrences` で証拠付与されることをtest固定。
- W-09[推奨] NER失敗textは `covered_text_sha256` に入れず再試行、statusは構築ごと記録。
- W-10[推奨] `builder_version` 対象にwordfreq/pronouncing version・`GENERAL_WORD_MIN_ZIPF`・`CMU_OK_CATEGORIES`/`USABLE_GRADES`・`_verify_llm`/`_merge_initials`/見出し除外規則・model idを含め、明示定数+関連source hash照合のgolden test。任意で「継承無効化版(eligible規則)」と「resume再構築版(prompt/model)」を分離。
- W-11[推奨] 並行書込はlockfile(O_EXCL)。
- W-12[推奨] 逐語検証は供給前script textに加え `tts_safe_*` 変換後text(X er019:303-306)でも行い、正規化ずれをtest固定。
- W-13[推奨] Perplexity Stage1 resolveは受理diffごとに呼ばれる(er006:839-846)→run単位の名詞memoの有無確認(無ければ追加推奨)。Perplexity結果は受理を左右しない(記録のみ)ことをtest固定、operator報告で表の根拠とPerplexity根拠を別欄。
- W-14[推奨] B工程のHR Lock解除根拠=ユーザー原文USER_02 §1-B・§3を受入記録に明記(11-8維持境界)。
- W-15[推奨] commit手順: `git commit --only -- <path>`、`git diff --cached --name-status` 確認、worktree分離、baseline署名commitは単独path限定。(indexの誤staged削除11件はFable側で解消済み)
- 情報: PNAP scope選択は正しい、X dry_runはAPI 0、Z hook非経由、decorator重なり問題なし、NER費用は `cl.install` 後で予算に含まれる。11-7限定例外は使わない整理で可。②との干渉は近接hunkのみ、処理順で安全条件は緩まない。Z Seed key_rolesはBertie検証に無関係(Bertieはcall B由来confirmed)。XのSTOP確認箇所はfile:lineを明記。

## 実装
1. `WIRING_DESIGN_02.md`(OF反映差分表)。
2. **baseline署名の凍結**(実装前): `evaluate_alarm_eligibility` への入力(cls diffs直列化)でD1 88件・D2・fixtureの出力署名を保存し単独path限定commit。
3. 新module `er103_run_entity_table_01.py`(Trial移植+W-03の決定論再計算+W-09/10/11)、`er103_proper_noun_alarm_policy_01.py` 本体(G5位置紐づけ[W-01反実仮想]、G3不受理分岐内RET-3[W-05]、`entity_table` 引数、adapter経路限定の自動取得[W-04]、audit additive)、`er103_pnap_runner_hooks_01.py`(構築hook、`_ret_provider`)、X `family_scope` wrapper/Z `run_tts_stage` provider(Zは両level和集合)、`er019_family_x_validation_inheritance_01.py`(復元表/None明示、受理時detail更新)、`er078_reuse_value_guard_01.py`(`entity_contributed`+W-06)、`er006_model_routing_contract_01.py`(NER model定数)、flag `RUN_ENTITY_TABLE_ENABLED=True`+`is_active_for_run()`(PNAP scope ∧ flag)、STOPセンチネル確認(XのSTOP箇所file:line明記)、W-12 tts_safe後text検証、W-13 memo確認。
4. test: 13群(設計)+W-02(a)(b)(c)+W-05/06/08/12/13固定+DefaultOnScope isolation+AST(Productionから `er111_*` import 0)。Trial複製依存test(`er111_pn_*_test`)は本体変更で落ちるため **skipではなく「差分test(W-02(b))として再構成」**(Trial関数はtestからのみimport)。allowlist更新。既存er103/er019/er063/er078/er104/er109 test PASS。
5. **全回帰** `run_project_regression.py` 単独実行(他agentのTTS/commit中は避ける)、failed/errorsを分類、自分起因0。
6. **X runtime evidence**(費用≤15円): X-2=正式入口 `--only-segments point_two` で `pool_n8_airport_line` を再生成(`--mode real`、STANDARD、STOP rc=0、TTS直列化)。確認: entity_table構築(call数・費用)、`Kristie Tse` の証拠供給→`ENTITY_ONLY_ACCEPT`/アラーム記録/HR 0/Store反映/operator report(表の根拠とPerplexity根拠別欄)。自然発火しなければW-07予備策(隔離run_dirでreplay)まで実施し、証拠区分を明記。X-1(保存wav+正式adapter+実ASR)・X/Z-3(継承再判定API 0)・X/Z-4(A/B/C不変・rollback署名)も実施。
7. SSOT: OPEN-472 Status=`IMPLEMENTED_X_EVIDENCE_DONE_PENDING_Z_EVIDENCE_AND_FABLE`、CURRENT_SPEC(PNAP節へRET追記: 配線点・flag・安全条件不変・費用。PRODUCTION_WIRED表記はFable受入後)、DECISION_LOG(W-08の記録含む)、REPORT_LEDGER。
8. 証跡 `PN/RUNTIME_EVIDENCE_01.md`(X分)、`PN/IMPLEMENTATION_01.md`。

## 禁止
Z stage実行(B工程で実施)、Bertie HR Lock解除、Ledger `upsert`、`er109`系の編集(②担当)、`er111_*` の削除(残置)、受理境界の変更、Prompt/閾値変更、15円超過、rebase/force push/一時index。

## 報告(docs/pm/RESULT_PACKET_ASRQ_PN4.md)
(1)OF反映表 (2)変更ファイル一覧(file:line) (3)test結果(新規/既存/W-02等価性/全回帰) (4)X evidence(証拠区分明記) (5)Z evidence手順(B工程向け) (6)費用・時間 (7)commit・raw URL・SSOT (8)残存リスク + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。