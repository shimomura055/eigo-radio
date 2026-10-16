# 委任_04 受領委任文(T-0保存、FXPW、全文)

## 管理ID
`FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01`(FXPW)委任_04(Phase 2統合: トラックA/Bの結合[audio runnerへのIn One Line scope 1行]+全体回帰test+CLI未指定dry-run+SSOT追記+明示add・commit・push。**有料API・Coffee生成は禁止**。Coffee E2Eはユーザーへの費用提示後に別委任)。並行委任: なし(02A/02B/DQIはすべて終了)。Git: `.git/index.lock`は60秒待ち再試行。mainへは`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only origin main`→`git merge --ff-only work/post-merge-01`→`git push origin main`→main dirで`git merge --ff-only origin/main`。

## 前委任の受入記録(Gate 7)
- 委任_02A(トラックA): TRACK_A_IMPLEMENTED_TESTS_PASS。当初目的=原文§4「6仕様をFamily Xの既定profileとして適用する。CLIによる特別指定を忘れた場合でも、承認済みStyleが自動適用されるようにする。Master Audio Storeでは、Style変更後の音声を旧Style音声として誤再利用しない。」成果物=新profile fx_20261016・K2 2段key(新module er019_family_x_kp_en_k2_store_01.py、SN/Store/repro01/Z本体は差分0)・P8-KP role分離・M3/M4 role別判定・--tts-backend既定flash-lite・新規test 72 PASS・回帰658 PASS/1 FAIL(無関係: er078_…06c dirty ledger.json起因)。判定: ACCEPTED(統合条件付き)。重大NG=なし。
- 委任_02B(トラックB): TRACK_B_IMPLEMENTED_TESTS_PASS。当初目的=原文§4「In One Line」。成果物=新Prompt(er003_v1_n3_01_advanced_adaptation_generate.py:551付近)・Std継承1文・中立module er081_family_x_in_one_line_01.py・Writer段fail-closed STOP・LR gate 8_sentence_count_unchanged(Family X scope限定)・evidence保存・新規21 test、248 PASS。部分一致: LR scopeをTTS段で立てる1行が未配線(本委任で実施)。T-0要約保存=逸脱(記録)。判定: ACCEPTED(統合条件付き)。重大NG=なし。
- Fable判断: K2 fallback(旧MINIMAL+ENGLISH_LOCK)は非ブロッキングwarning維持(BLOCK化は新Blocking QA条件=Coffee E2E観測後、区分C)。--tts-backend既定変更は承認済みflash-lite統一の範囲内で採用。

## 性質/到達上限Status/禁止事項
- 性質: 統合・回帰・SSOT・Git。到達上限Status: PHASE2_WIRED_CODE_COMMITTED_RUNTIME_EVIDENCE_PENDING(PRODUCTION_WIREDとは書かない: Coffee正式実走のruntime evidence[ユーザー受入条件4・5・7]が未取得)。
- 禁止: 有料API、Coffee生成、既存Gateの緩和、Family A/B/C/Zの挙動変更(統合で差分が出たら戻す)、FamilyAUnchangedTest等のguard testの改変、旧仕様へ戻す形のtest修正、Open Item close、既存SSOT行の書換え(追記のみ)、git add -A/-u。
- Opus Gate: 条件A実施済み(反映済み)。統合で設計から外れる変更が必要なら実装せず報告。
- 時間見込み: 60〜90分。費用JPY0。承認区分: A。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない。 D-1: Grep→該当行範囲Readを基本、全文Readは構造変更時のみ。 G-1: git出力は--porcelain/--stat/--short等で最小化。 F-1: transcript退避不要。
T-0: 受領委任文を本ファイルへ保存し check_delegation_prompt.py を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。
T-2: TTSを伴う委任はTTS_EXECUTION_MODE=STANDARD明示(本委任はTTSなし)。 T-3: 費用上限なし(JPY0)。

## ユーザー指示(原文)
docs/pm/delegation_log/2026-10-16_FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01_USER.md §4(「初回生成だけでなく、Standard継承、Local Rewrite、retry、regenerationにも適用する。」「retry／fallback／regeneration／resumeへの整合」「必要Validator／QA／Regression test」)、§9受入条件1〜12(特に6「必要なValidator／Regression／integration test PASS」、11「必要なcommit／push／merge確認済み」)、§8「有料E2E開始前に費用見積を提示し、承認済み予算・既存Gateを守る。」

## 事前指定Read一覧
RESULT_PACKET_FXPW2A.md / RESULT_PACKET_FXPW2B.md、WIRING_DESIGN_01.md §J・§K、COFFEE_E2E_PLAN_01.md、er019_family_x_audio_production_runner_01.py(with_secondary_run 2箇所・import部)、er081_family_x_in_one_line_01.py(family_x_in_one_line_scope)。

## 手順
0. git status --short(02A/02B以外の既存dirtyは触らない)。
1. T-0保存+check。
2. 結合: er019 audio runnerに `import er081_family_x_in_one_line_01 as fx_iol` を追加、generate_family_x_b1_segments / generate_family_x_a2_segments の @secondary_run_scope.with_secondary_run 直下に @fx_iol.family_x_in_one_line_scope() を追加(シグネチャ・戻り値不変)。Family Z runner(er063)はscopeを立てない(差分0)ことを確認。
3. 結合testを er081_family_x_in_one_line_01_test_01.py に追加(b1/a2生成関数内で is_family_x_in_one_line_scope() がTrue、Zの経路ではFalse)。
4. 全体回帰: 02Aの24ファイル+02Bの10ファイル(重複除く)+er019_family_x_pointless_01_test_01.py+er026_cs_audit_regression_01_test_01.py+er078_asr_unified_wiring_06c_test_01.py+er020_tts_retry_local_rewrite_fullseg_test_01.py を .venv\Scripts\python.exe -m pytest -q で実行。結果を表(PASS/FAIL/原因/HEAD比較)。本件起因のFAILは直す(Gateを緩めない)。無関係FAILは直さず原因と証拠(HEAD worktree eigo-radio-crbnでの結果)を記録。追跡済み出力ファイルへの追記はstageしない。
5. CLI未指定dry-run(API 0): COFFEE_E2E_PLAN_01.md記載のplan stageコマンド(--stage plan、--style-profileなし、--tts-backendなし)を新規一時out_dir(er019_output/_fxpw_dryrun_04/、追跡対象なら実行後削除)で実行し、audit/style_profile.jsonのprofile_id==fx_20261016・6role sha・style_profile_sourceを確認。API未呼出をコードで事前確認、確認できなければ実行しない。
6. 撤去確認Grep(Production module): `Exactly one sentence`/`12-18`/`Trial-only`/`ONE short`/`single most important`/`for the listener`/`default_new_run_n01`/`P8対象segmentがP8で` =0件。
7. SSOT追記(既存行不変): CURRENT_SPEC.md Family X 2026-10-16小節末尾に「Phase 2配線 実装記録…Status=実装・test完了、runtime evidence(Coffee正式実走)待ち。PRODUCTION_WIREDではない」。OPEN_ITEMS.md: OPEN-299/298/300/343に行内追記(closeしない)。DECISION_LOG.md末尾に委任_02A/02B/04エントリ。USER_DECISION_REGISTER_01.md FXUD-1〜8備考・#97・#98。OPUS_FINDINGS_LEDGER.mdにOF-FXPW-R-01〜-12。REPORT_LEDGER.md 1行。ACTIVE_TASK(gitignore)。
8. Coffee E2E実行準備(実行しない): COFFEE_E2E_PLAN_01.md末尾に「§実行直前チェック(委任_04時点)」を追記(stage(a)text全文コマンド[新out_dir run_fxpw_01、TTS_EXECUTION_MODE=STANDARD]、前提条件、費用見積再掲[期待約JPY96/最悪約162]、本日累計再計算、7-7・日次1,000円との関係)。
9. secret scan hits=0 → 明示add(02A変更6+新規5、02B実装5+test5+文書4、本委任の結合・test・SSOT・delegation_log)→git diff --cached --stat で出力物混入なし確認→commit(メッセージ指定: "FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 委任_02A/02B/04: Family X承認仕様のProduction配線(…)+test(新規93+結合)+SSOT。runtime evidence待ち(PRODUCTION_WIRED未判定)")→crbn経由でmainへff・push→main dirでff。

## 報告
docs/pm/RESULT_PACKET_FXPW4.md: 1 T-0 / 2 結合箇所と結合test / 3 全体回帰表 / 4 dry-run / 5 撤去Grep / 6 SSOT追記一覧 / 7 commit・push・diff --cached --stat・secret scan / 8 Coffee直前チェック要点 / 9 逸脱 / 10 費用・所要 / 11 受入記録5項目 / 12 判定整合行。
