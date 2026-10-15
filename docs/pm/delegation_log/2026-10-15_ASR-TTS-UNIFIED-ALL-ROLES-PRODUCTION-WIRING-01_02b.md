## 管理ID

`ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01`(AUW)委任_02b(Phase 3-1: 作業branch上で共通判定モジュール・値ガード・PASS_WITH_WARNING registry・Unit test・import graph静的監査testを実装。**Production配線はしない**=既存2関数のadapter化は委任_03/04)。前提: DESIGN_01(`3953de4ff`)+DESIGN_02_ADDENDUM_01(`9ed5754e2`、Opus条件A所見反映済み、**食い違う場合は追補が優先**)。Status `APPROVED_FOR_PRODUCTION`。到達上限 `UNIT_READY_ON_BRANCH`。並行: CRB採点(Repo外)。費用JPY0(有料API 0。mock engineのみ)。時間見込み約3h。

## 性質/禁止

- **branch運用(OF-AUW-02)**: `git checkout -b feat/auw-unified-asr-01`(mainから)。以後の委任_02b〜05は同branchにcommit・push(`git push -u origin feat/auw-unified-asr-01`)。**mainへのmerge禁止**(委任_07でFable判断後に1回だけ)。mainのSSOT・Productionは触らない。
- 禁止: 既存Production関数の挙動変更(本委任は新規モジュール追加+testのみ。`er006_secondary_asr_01.py`/`er007_*`/runner群は**無変更**)。有料API。承認範囲外の仕様追加。git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f(branch作成の`checkout -b`は可)。
- T-0(恒久運用): 本委任文を`docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_02b.md`へ全文保存(branch上でcommit)し`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`(FAILでも継続)。E-1/D-1/G-1/F-1従来どおり。T-2: TTSなし。T-3: 費用0。
- Fable補正(追補§1-2の1点): **EN "one"の脱落/挿入は`DIFF(b)`ではなく`UNKNOWN`**とする(Opus OF-AUW-01の誤NG指摘のとおり。"one"は代名詞・冠詞的用法が多く、Tier1が数値atom扱いするため拒否側へ流用しない)。"one"が明確な数量(単位・助数詞・可算名詞と対になり、相手側に別の数詞がある)場合のみ`DIFF(a)`。testに両ケースを固定。

## 事前指定Read一覧

1. `er058_output/unified_all_roles_production_wiring_01/DESIGN_02_ADDENDUM_01.md` §1(5値意味論・判定表・擬似コード・test追加パターン)・§3-2(静的監査)・§4(障害処理)・§7(費用)・§8(registry)・§13(分割)
2. `er058_output/unified_all_roles_production_wiring_01/DESIGN_01.md` §4-2(擬似署名)・§4-5(SecondaryCache)・§4-6(監査record・試聴リスト)・§5(数値S1: 再利用元`er066_ja_asr_orthographic_equivalence_01_trial.py` Stage 1/EN Tier1 atom+`normalize_numeric`)・§5-7(9例)・§7(変更箇所)・§8-1(Unit計画)
3. 再利用元: `er066_ja_asr_orthographic_equivalence_01_trial.py`(Stage 1 値署名: Grep `def |kansuji|value_signature|has_ambiguous`)、`er021_en_asr_semantic_equivalence_production_01.py`(Tier1 atom抽出: Grep `def |atom|normalize_numeric|percent`)、`er006_preprod_hardening_01_validation.py`:600-640(`_is_number`)・:1060-1072(`HOMOPHONE_MATCH_NUMBER_EXCEPTION`)、`er007_ja_asr_validator_01.py`:60-70・:250-290(読み一致)、`er007_ja_secondary_asr_01.py`:80-100(許容集合・単価式 `JPY/秒`)、`er006_secondary_asr_01.py`:240-250(COST_GUARD)・:395-420(Azure呼出)
4. 既存test様式: `er003_test_key_words_gloss_alignment.py`:1-40(unittest/pytest形式の確認)、`rg -l "def test_" er021*test*.py er007*test*.py | head`

## 実装(新規ファイルのみ)

1. `er078_asr_value_guard_01.py`: `value_guard(src, hyp, lang) -> ValueGuardResult(kind in {NO_VALUES,EQUAL,DIFF,AMBIGUOUS,UNKNOWN}, pairs, reasons)`。atom抽出(JA: 算用/漢数字[位取り〇含む]/かな数詞[同読み数詞変種辞書: 一人/ひとり、一つ/ひとつ、二十歳/はたち等]/助数詞・単位/割合、EN: 数字/数詞/percent・%/単位)、位置対応align、値+単位比較、閉集合マーカー(「十分間/十分後/十分ほど」等)による「十分」の解消、不規則読みのWARNINGフラグ、集約優先順位 DIFF>UNKNOWN>AMBIGUOUS>EQUAL>NO_VALUES。**既存の`normalize_numeric`/Tier1 atom/er066 Stage 1を関数import or 移設で再利用(コピペ重複を避け、再利用元を docstring に明記)**。
2. `er078_asr_unified_judge_01.py`: `unified_judge(ctx: AttemptCtx, primary_result, secondary_fn, *, lang, role, final_and_gate=True) -> JudgeResult(state in {PASS, PASS_WITH_WARNING, NG_PROTECTED, NG_EXCLUDED, NG_BOTH, NG_SECONDARY_UNAVAILABLE, NG_PRIMARY_ASR_FAILURE}, warning_labels, audit_record)`。状態機械は追補§1-3で改定したDESIGN_01 §4-3(Primary PASS→最終ANDゲート→PASS/PASS_WITH_WARNING、Primary NG→P1保護差[値DIFF/否定差]→NG_PROTECTED、P2除外表→NG_EXCLUDED、P3→Secondary 1回[`SecondaryCache` key=(sha256(wav),engine,lang,phrase_hash)、失敗は非キャッシュ]→保護差ならNG_BOTH/許容集合PASSかつ最終ANDゲートOK→PASS_WITH_WARNING/それ以外NG_BOTH、AMBIGUOUSはP3でSecondary同一表層のみ`NUMERIC_AMBIGUOUS_SURFACE`)。最終ANDゲートは承認済みequivalence(`HOMOPHONE_MATCH_NUMBER_EXCEPTION`・Tier1 diff-anchored・読み一致)を再否定しない(根拠ラベルをctxで受け取りskip)。言語別Secondary許容集合はDESIGN_01 §4-3c(JA=EXACT/NORMALIZED[値等価正規化後一致含む]+`ORTHOGRAPHIC_VARIANT_CONFIRMED`2エンジン、EN=既存分類器`should_pass`集合)を**関数引数の注入(callable)**で受け、本モジュール内に既存分類器を再実装しない。Secondary障害: PASS不可・`secondary_unavailable=True`・run単位circuit breaker用カウンタをctxへ・技術STOP記録(Lock状態は増やさない)。audit_record: primary/secondary転写・分類ラベル・value_guard結果・warning・`est_jpy`(秒数ベース、SCGと同じ式)・所要ms・cache hit。既存除外表はデータ化(`SCG_EXCLUSIONS`: 数字差→値DIFFのみ/否定差/length NG/C2同形異音/【U1待ち】C1固有名詞・類似度<0.4=現行維持フラグ)。
3. `er078_pass_with_warning_registry_01.py`: `derive_listening_list(tts_generation_results: dict) -> list[entry]`(二重管理なし。entry=segment_id/role/level/lang/warning_labels/audio path/primary・secondary転写/判定理由)、`write_listening_list(run_dir)`→`audit/pass_with_warning_listening_list.json`、`render_html_section(entries)->str`(X/Zページ節用)、`render_standalone_html(entries)->str`(legacy用)。run途中STOP時にも呼べる純関数。
4. test: `er078_asr_value_guard_01_test_01.py`(ユーザー提示9例[三人/3人 EQUAL、三人/四人 DIFF、三十人/30人 EQUAL、三十人/40人 DIFF、十分(10分)/10分 閉集合マーカーありEQUAL・なしAMBIGUOUS、100円/百円 EQUAL、20%/20 percent EQUAL、20%/30% DIFF、25%/26% DIFF]+追補§1-6パターン+Fable補正の"one"2ケース+**Production同一前処理後の原稿**[`tts_safe_number_words_en`等をimportして通す])、`er078_asr_unified_judge_01_test_01.py`(mock engineで全状態遷移: Primary PASS/保護差でSecondary不呼出[呼出回数0をassert]/P3でSecondary 1回のみ[同一wavで2回呼んでも1回=キャッシュ]/Secondary PASS→PASS_WITH_WARNING/Secondary保護差→NG_BOTH/Secondary障害→NG_SECONDARY_UNAVAILABLE・PASS不可・非キャッシュ/最終ANDゲートが承認済みequivalenceを再否定しない/否定差NG/`est_jpy`秒数計算)、`er078_pass_with_warning_registry_01_test_01.py`(導出・HTML・途中STOP時)、`er078_asr_unified_wiring_static_audit_01.py`(**import graph方式**: entrypoint `er019_family_x_audio_production_runner_01.py`/`er063_family_z_audio_01.py`/`er026_family_z_fiction_production_runner_01.py`/`er012_b_family_voices_a2_production_01.py`/`er013*`/`er012_e*`/`er003_v1_n3_01_tts_generate.py`からASTでimportを辿り、到達module内の`transcribe|classify_asr_match|classify_ja_asr_match|evaluate_attempt`呼出を列挙し、allowlist(`er078_asr_unified_wiring_allowlist_01.json`、理由付き)と突合。**本委任時点では配線前なので「現状の呼出一覧をsnapshot化しallowlist初期版を生成」まで**。配線後(委任_03/04)に「adapter経由以外の呼出0」をassertへ切替える旨をtest内コメントに)。
5. `er058_output/unified_all_roles_production_wiring_01/IMPLEMENTATION_02b.md`: 実装概要・再利用元対応表・test結果(件数・PASS/FAIL)・静的監査snapshot(判定点一覧=DESIGN J1〜J11との突合)・未実装(配線は03/04)・U1/U2待ちの箇所(flag名)。

## 実行コマンド全文

- T-0: 上記。
- branch: `git checkout -b feat/auw-unified-asr-01`、`git push -u origin feat/auw-unified-asr-01`
- test: `.venv\Scripts\python.exe -m pytest er078_asr_value_guard_01_test_01.py er078_asr_unified_judge_01_test_01.py er078_pass_with_warning_registry_01_test_01.py er078_asr_unified_wiring_static_audit_01.py -q`、既存影響確認 `.venv\Scripts\python.exe -m pytest er021*test*.py er007*test*.py er006*test*.py -q`(新規モジュール追加のみなので全PASS維持を確認。PASS/FAIL件数を記録。既存FAILがあれば「既存」と区別)
- secret scan: `.venv\Scripts\python.exe tools/secret_scan_01.py --staged`
- git: `git status --porcelain`(add対象のみ)、`git log --oneline -3`、`git branch --show-current`

## Git

branch `feat/auw-unified-asr-01`。明示add: 新規4モジュール+4 test+allowlist json+IMPLEMENTATION_02b.md+delegation_log。コミットメッセージ: 「AUW 委任_02b(branch): 共通判定er078_asr_unified_judge_01+値ガードer078_asr_value_guard_01(5値意味論・9例+追加パターン固定)+PASS_WITH_WARNING registry+Unit test+import graph静的監査snapshot。Production配線なし、JPY0」。push to origin/feat/auw-unified-asr-01。**mainは無変更。**

## 報告(`docs/pm/RESULT_PACKET_AUW2b.md`)

(1)T-0 (2)branch名・commit hash・push先 (3)test結果(新規: 件数/PASS、既存: 件数/PASS・既存FAIL) (4)9例+追加パターンの判定結果表(期待どおりか) (5)静的監査snapshot(判定点一覧とJ1〜J11の突合、allowlist件数) (6)再利用元対応表 (7)U1/U2待ちのflag名と現状値 (8)逸脱・未確認 (9)Fable向け: 委任_03(EN配線)の注意点。

Fableは(3)(4)(5)を照合する(受領≠受入)。
