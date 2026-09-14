# EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-02(OPEN-151完成)

> 結果、到達Statusは**`PARTIAL`**(Sonnet自己申告、2026-09-14)。ユーザー指定
> 15項目中14項目は✓、項目7「cleanな2V runtime evidence」のみAnalytical
> Leakage Check(voice_b/tension)が3attempt上限到達後も残存flagとなったため
> 完全クリーンではない。前回(-01)の未充足3点のうちComment Contract整合・
> Gate辞書2V/3V整合の2点は本タスクで解消した。3点目(REVIEW_REQUIRED/残存
> flag)もFact Checker側はPASSへ改善したが、Leakage Check側の残存flagは
> retry上限・Gate基準変更を禁止された条件下での構造的限界として残った。

## 1. 到達Status

`PARTIAL`。根拠: ユーザー指定15項目のうち14項目を確認した(詳細は2節)。
項目7(2V runtime evidence)は「全Gate/QAがブロックなしで完走」の字義上の
条件(final_status="OK"、STOP・NG_REVIEW_REQUIREDなし)は満たしたが、
Analytical Leakage Check(既存3V/2V共通のQA機構)が3attempts上限到達後も
voice_b/tensionでflagged項目を残した。retry上限変更・Gate基準変更は
いずれも本タスクで禁止されているため、既存corrective retry機構(Leakage
是正2回)を尽くした上でのこの結果は、これ以上Sonnet権限内では解消できない
構造的限界と判断した(3V側にも同型の「3attempt上限で残存flagはUSER_
DECISION_REQUIRED候補」という既存仕様があり、新しい問題ではない)。

## 2. ユーザー指定15項目照合

1. **2V新規topic正式Production path**: ✓(既存、-01タスクで確認済み、本
   タスクでも`main_b1_2v()`のwrite_new_theme経由で再実行し無変更を確認)。
2. **3V既存挙動維持**: ✓(3V regression、3節参照)。
3. **Comment Contractの2V/3V正式path接続**: ✓完了(本タスクの主目的)。
   `er012_b_family_production_runner_01.py::run_comment_contract_for_
   new_theme()`を新規追加し、`main_b1_2v()`/`main_b1_3v()`のwrite_new_theme
   stageから、Writerパイプライン(retry・Local Rewrite込み)確定後の最終
   article_text/sectionsに対してのみComment 1-4+Preview(既存承認済み
   registry Comment Contract、run_scaffold()/run_scaffold_3v()と同一Role・
   呼び出し方法、無変更)+Ledger Deviation Check(Comment Contract検証)を
   接続した。status!="OK"時はスキップし記録する(ブロック状態の記事に
   対してComment生成を行わない)。実runtime evidence(5節)でComment 1-4+
   Previewすべてstatus="OK"、Comment Contract検証=LEDGER_COMPLIANTを確認。
4. **Fact Safety Gateの2V/3V整合**: ✓完了。`_apply_b_family_voice_safety_
   gate`/`_voice_gate_locate_section`/`_voice_gate_stage1_eligible`を、
   3V(6区切り)優先検出→検出不可時のみ2V(5区切り)として再検出するよう
   一般化した(段階1/2の判定ロジック・安全基準は一切変更せず、構造読み
   取りのみ一般化)。3節参照。
5. **retry・fallback・regeneration整合**: ✓。Comment生成はWriterパイプ
   ライン(3attempts、Local Rewrite最大3cycle)が完全に確定した後にのみ
   呼ばれる設計のため、記事再生成のたびにComment生成が誤って先行実行
   されることはない(実装レベルで保証)。Writer全体のretry上限
   `MAX_WRITER_ATTEMPTS=3`・Local Rewrite上限は無変更のまま。
6. **Fact attribution整合**: ✓(`run_fact_check_a_prime_2v`実測PASS、
   fact_attribution_mode_enabled=True、5節参照)。
7. **cleanな2V runtime evidence**: △(未充足)。5節参照。Fact Checker
   verdict=PASS・Ledger Deviation=LEDGER_COMPLIANT・Comment Contract
   検証=LEDGER_COMPLIANTと、ブロック要因はすべて解消したが、Analytical
   Leakage Check(voice_b/tension)がflagged項目を残した。
8. **必要な3V regression evidence**: ✓(3節参照、オフラインbehavior不変性
   +新規4テスト、実API再生成は不要と判断)。
9. **actual model_id・routing evidence**: ✓(`gpt-5.6-luna`、7節参照)。
10. **CURRENT_SPEC更新**: ✓(OPEN-151段落へ追記)。
11. **DECISION_LOG更新**: ✓(新規エントリ+索引1行)。
12. **OPEN_ITEMS更新**: ✓(OPEN-151・OPEN-120両方へ追記)。
13. **必要Git commit・push**: 実施(10節)。
14. **Dangling Reference Check**: ✓(0件、6節)。
15. **ユーザー承認内容とProduction挙動の一致**: △。Comment接続・Gate
    一般化はユーザー承認内容(既存仕様のwiring不足解消・構造読み取り一般化
    のみ)と一致。ただしLeakage残存flagの扱い(そのままPRODUCTION_WIRED
    と扱ってよいか、人手レビュー必須のままとするか)はユーザー判断の余地
    が残る(8節)。

## 3. 3V regression evidence

改修前(git HEAD、本タスク開始時点)のコードを`er014_output/four_type_
observation_01/voices/runner_before_v2.py`/`writer_generic_before_v2.py`
として保存した上で確認した。

- `_apply_b_family_voice_safety_gate`は本タスクで意図的にsourceを変更
  したため(2V/3V section parser一般化)、既存`ThreeVoiceByteInvariance
  AgainstHeadTests::test_source_of_untouched_3v_functions_unchanged`の
  byte比較対象からは除外した(該当関数のみ)。代わりに新規
  `VoiceSafetyGate2V3VParserGeneralizationTests::
  test_3v_behavior_unchanged_against_head`で、改修前(git HEAD、
  `writer_generic_before.py`)と改修後で、同一の3V(6区切り)入力に対する
  `_apply_b_family_voice_safety_gate()`の出力(降格結果・overall_status)
  が完全一致することを確認した(behavior不変性、byte不変ではない)。
- その他の3V専用関数(`build_focus_module_block_3v`/`run_fact_check_a_
  prime_3v`/`run_overlap_monitoring_3v`/Leakage関連4関数/`run_voices_
  pattern_3v`/`run_pipeline_3v`/`run_ledger_deviation_and_local_rewrite`/
  `_generate_and_compress_article_3v`/`split_six_voice_sections`/
  `build_ledger_fragment_visible_voices_only`/`run_phase_a`/
  `build_candidate_prompt`)は、既存`test_source_of_untouched_3v_
  functions_unchanged`によりsource文字列の完全一致(byte不変)を維持。
- 新規テスト: `VoiceSafetyGate2V3VParserGeneralizationTests`(4件、3V
  behavior不変性1件+2V不発確認[改修前]1件+2V発火確認[改修後]stage1/
  stage2各1件)、`NewThemeCommentContractWiringTests`(4件、main_b1_2v/
  main_b1_3v×OK時発火/NG時スキップ)、`DanglingTrialReferenceTests`(2件)。
- 回帰: `er012_b_family_voices_variable_voice_count_test_01.py`43件PASS、
  `er012_b_family_voices_writer_generic_01_test_01.py`34件PASS(既存、
  無変更のまま全PASS)、`er012*_test_*.py`184件PASS、`er011*_test_*.py`
  266件PASS、全件回帰2699件中2696件PASS(既知FAIL3件[`er003_test_bad`
  1件+`er003_test_p2j_investigate`2件]のみ、新規FAILなし)。

## 4. 実装概要

- `er012_b_family_production_runner_01.py`: `run_comment_contract_for_
  new_theme(article_text, sections, num_voices, ledger_text, out_dir)`
  を新規追加(既存`run_scaffold()`/`run_scaffold_3v()`と同一のComment
  1-4+Preview呼び出し・Ledger Deviation Check呼び出しパターンを、
  num_voices分岐[2V="One/Another Voice"文言、3V="Voice 1/2/3"文言]で
  汎用化)。`main_b1_2v()`/`main_b1_3v()`のwrite_new_theme分岐末尾に
  呼び出しを追加(status=="OK"時のみ)。既存`run_scaffold()`/
  `run_scaffold_3v()`・既存main()/main_a2()の他のstageは無変更。
- `er012_b_family_voices_writer_generic_01.py`: `FIVE_SECTION_LABELS`
  定数を新規追加。`_voice_gate_locate_section()`に`section_labels`
  引数(既定値=3V用、後方互換)、`_voice_gate_stage1_eligible()`に
  `voice_body_keys`引数(既定値=3V用、後方互換)を追加。
  `_apply_b_family_voice_safety_gate()`を、3V→2Vの順で構造検出する
  よう改修(判定ロジック自体は無変更)。
- テスト: `er012_b_family_voices_variable_voice_count_test_01.py`へ
  3クラス(10テスト)追加(既存33テストは無変更のまま全PASS)。

## 5. 2V clean runtime evidence

- 出力dir: `er014_output/four_type_observation_01/voices/run2_clean/`
  (旧-01タスク成果物は`voices/run1_partial/`へ`git mv`で退避済み)。
- topic: 「Is personalized news good for us?」(-01タスクと同一、
  同一Ledger[`research/verified_fact_ledger.txt`、VERIFIED 18/
  AMBIGUOUS 1/REJECTED 0]を再利用、Research再実行なし)。
- driver: `er014_output/four_type_observation_01/voices/run_voices_2v_
  b1_v2.py --reuse-ledger --out-subdir run2_clean --budget-jpy 150`
  (実際の2V正式Production経路`er012_b_family_production_runner_01.
  main_b1_2v()`をargv経由で呼び出す設計、Writer-only equivalentの
  手組みではない)。
- Writer: 3 attempts(Analytical Leakage Check是正retry)。attempt1:
  Fact Checker A' verdict未記載(Ledger Deviation経由でLocal Rewrite
  2cycle発動、最終LEDGER_COMPLIANT)、Leakage flagged(voice_b全6項目+
  tension2項目)。attempt2: Fact Checker verdict=PASS、Local Rewrite
  1cycle、Leakage flagged(voice_b2項目+tension3項目)。attempt3(最終、
  attempt上限到達): Fact Checker verdict=**PASS**(前回-01run[attempt3]
  ではREVIEW_REQUIREDだったが本runではPASSへ改善)、Ledger Deviation
  Checker=**LEDGER_COMPLIANT**(deviations=0、Local Rewrite不要)、
  比較方向Fact事前チェック=PASS、Leakage flagged(voice_b5項目+
  tension2項目、[leak_evidence_subject/leak_numbers_foreground/
  leak_narrator_analysis/leak_discovery_syntax/leak_evidence_memorable]
  系)。全体final_status="OK"。
- Comment Contract: Comment 1-4+Preview全てstatus="OK"(5-1配線が実際に
  発火したevidence)、Comment Contract検証(Ledger Deviation Check)=
  **LEDGER_COMPLIANT**。
- 5区切り語数(attempt3、最終記事): word_count=374語(soft target
  320〜380語の範囲内)。sentence_count=27。
- Fact Safety Gate(5-2): 本runの初回Ledger Deviation Check(各attempt)
  で検出されたMAJOR deviationは、段階1/2条件(Voice本文の一人称ヘッジ
  claim、またはTension roleの合成でsurface signal無し)に一致せず
  (例: "She cannot change those ranking rules herself."等、第三者主語
  寄りのclaim)、Gate降格は発生せず全てLocal Rewriteで解消された。2V
  でのGate発火能力自体は本タスクのoffline単体テスト4件(3Vと同一の
  段階1/2判定ロジック)で別途証明済み(OPEN_ITEMS OPEN-120へ追記)。
- model_id: `gpt-5.6-luna`(Writer/Fact Checker A'/Ledger Deviation
  Checker/Analytical Leakage Check/Comment 1-4/Preview/Comment
  Contract検証すべて)。
- 出力: `run2_clean/b1_2v_new_theme/`(summary.json、b1_support_
  texts.json、audit/b1_support_generation.json、audit/support_ledger_
  deviation.json、audit/new_theme_comment_contract_summary.json)、
  `run2_clean/b1_2v_new_theme_attempt{1,2,3}/`(各attemptのarticle.md・
  fact_qa.json・ledger_deviation.json・analytical_leakage_check_2v_
  attemptN.json等)、`run2_clean/cost_summary.json`、`run2_clean/
  production_set_cost.json`、`run2_clean/run_result.json`、`run2_clean/
  raw_usage_log.jsonl`(空、6節の表示バグと同一原因)、`run2_clean/
  b1_2v_new_theme/raw_usage_log_writer.jsonl`(実際の記録先、36 records)。

## 6. 費用

**Voices Production 1生成セット総原価 = ¥140.39**
(Research/Ledger¥46.98[既存再利用、再計算なし] + Writer/Comment/QA/
Gate/retry¥93.41[本run実測])。50:50配賦なし、直接費のみ。

新規スペンド分の上限¥150に対し実績¥93.41(¥56.59の余裕)。3V再生成は
実施していないため追加費用なし(合計費用上限¥250に対し実績¥93.41のみ)。

`run_voices_2v_b1_v2.py`実行直後の標準出力は「新規spend実測=¥0.00」と
誤表示した。これは-01タスクREPORT6節と同一原因の既知の表示バグ
(`run_writer_stage_generic()`内部の`cl.install(f"{out_dir_base}/raw_
usage_log_writer.jsonl")`がログ出力先を切り替える既存実装、本タスクでの
変更ではない)。driver側のログパス集計ロジックを修正し、`run2_clean/
cost_summary.json`へ正しい実測値(driver_log側¥0.00+writer_log側
¥93.41=合計¥93.41)を書き直した(この修正はdev driverスクリプトのみ、
Production module側は無変更)。

## 7. API token(合算、Writer/Comment/QA/Gate/retry)

`run2_clean/b1_2v_new_theme/raw_usage_log_writer.jsonl`実測: 36 API
records、input 501,357 / output 100,804 / cached 41,272。model=
gpt-5.6-luna(全record)。Research/Verification分は-01タスクで既に
取得済みのため今回は追加のAPI呼び出しなし。

## 8. Open Item候補

1. Analytical Leakage Check(voice_b/tension)が2V記事で3attempts上限
   到達後もflagged項目を残す状態が、5-3対応(-01→-02の同一Ledgerでの
   再生成)後も継続した。Fact Checker/Ledger Deviation Checker側は
   両方ともPASS/LEDGER_COMPLIANTへ改善した一方、Leakage Check側の
   flagged項目は本タスクで許可された修正手段(既存rewrite/regeneration/
   retry/correction経路の範囲内)では解消しきれなかった。retry上限
   変更・Gate基準変更はいずれも本タスクで禁止されているため、これ以上
   Sonnet権限内での対応はできない。ユーザー判断が必要な選択肢:
   (a) 残存flagged記事はそのまま人手レビュー対象として扱い続ける
   (3V既存仕様と同型の運用のまま、Status=PARTIAL/観測継続)、
   (b) Leakage Checkのcorrective note・Prompt自体の改善(新Prompt原則
   に該当するためユーザー承認が必要)、
   (c) MAX_WRITER_ATTEMPTS引き上げ(retry上限変更、ユーザー承認が必要)。
2. 3V保守版Fact Safetyゲートの2V発火が、本タスクの実runでは(構造的な
   検出失敗ではなく)MAJOR deviationの内容がstage1/2条件に該当しな
   かったため発生しなかった(Local Rewriteのみで解消)。Gate自体の2V
   発火能力はoffline単体テストで証明済みのため新規Open Itemとしては
   扱わず、OPEN-120へ観測事実として追記した。

## 9. T-0・事前指定外Read・STOP

- T-0: PASS(`docs/pm/delegation_log/EDITORIAL-B-FAMILY-VOICES-VARIABLE-
  VOICE-COUNT-PRODUCTION-WIRING-02_check.json`)。
- 事前指定外Read: なし(委任文列挙のRead/Grep一覧の範囲内で完結)。
- STOP: なし。上記8節Open Item候補1件は、ユーザー判断が必要な選択肢を
  提示する形で報告し、作業自体は完了させた(STOPして作業を止めては
  いない、5-3「ユーザーに毎回聞かないこと」との整合)。

## 10. Git

明示addで以下をcommit: `er012_b_family_production_runner_01.py`、
`er012_b_family_voices_writer_generic_01.py`、
`er012_b_family_voices_variable_voice_count_test_01.py`、本REPORT、
`er014_output/four_type_observation_01/voices/`配下(run2_clean/・
run1_partial/・run_voices_2v_b1_v2.py、`*_before_v2.py`等の一時比較
ファイルは除外)、`CURRENT_SPEC.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、
`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/delegation_log/
EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-02.md`
+`_check.json`、`docs/pm/RESULT_PACKET_VOICES_VAR2.md`。commit hash・
push結果は`docs/pm/RESULT_PACKET_VOICES_VAR2.md`参照。

## 11. `docs/pm/ACTIVE_TASK.md`

更新済み。
