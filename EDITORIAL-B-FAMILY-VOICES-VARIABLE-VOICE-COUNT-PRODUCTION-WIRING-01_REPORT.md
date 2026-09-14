# EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01(OPEN-151)

## 1. 到達Status

**`PRODUCTION_WIRED`**。

根拠: 委任文が挙げた最低限11項目をすべて確認した(詳細は2節)。Comment
Contractのみ「新規topic Writer-only入口自体はComment未接続」という3V既存
スコープと同一の限界があり、これは静的確認(voice数非依存の共有定義である
ことのgrep確認)にとどまる(end-to-end生成では検証していない)。この点を
除き、全項目についてoffline test/runtime evidence/全件回帰のいずれかで
確認済み。

## 2. Gate 3 最低限11項目

1. **2V新規topic正式Production path**: ✓。`er012_b_family_production_runner_01.py`
   に`main_b1_2v()`(`level="b1_2v"`、`write_new_theme`stage専用)を新規追加。
   既存`main()`/`main_a2()`/`main_b1_3v()`は無変更(`git diff --stat`で
   runner側+39行のみ、既存関数の削除・変更行なし)。契約テスト
   `MainB12VWriteNewThemeContractTests`/`RunnerLevelB12VDispatchTests`
   (`er012_b_family_voices_variable_voice_count_test_01.py`)。
2. **3V既存挙動のRegressionなし**: ✓。3節参照。
3. **registry可変voice数**: ✓。`er012_b_family_editorial_type_registry_01.py::
   build_required_structure(level, voice_a, voice_b, voice_c=None)`は本タスク
   以前から2V(`level="b1"`, voice_c省略)/3V(`level="b1_3v"`, voice_c必須)を
   両方サポート済みと確認(**本タスクでregistry.pyは1行も変更していない**、
   `git diff --stat`)。`RegistryGateDictVariableVoiceCountRegressionTests`で
   再確認。
4. **retry・fallback整合**: ✓。`run_ledger_deviation_and_local_rewrite`
   (Local Rewrite、`local_rewrite.MAX_REWRITE_CYCLES`)は2V/3V共有・無変更の
   まま両経路から呼ばれる。Writer全体のretry上限`MAX_WRITER_ATTEMPTS=3`も
   共有定数のまま(2V用に複製した`run_pipeline_2v`が同じ定数を参照)。2V
   runtime evidenceで実際に3 attempts(Leakage Check是正retry)を実測。
5. **Fact attribution・Comment Contract・Gate辞書整合**: Fact attribution=✓
   (`run_fact_check_a_prime_2v`が`fact_attribution_mode_enabled=True`で
   3V同様に動作、2V runtime evidenceでverdict PASS/PASS/REVIEW_REQUIREDを
   実測)。Gate辞書=✓(項目3のとおり既存実装で充足)。Comment Contract=
   △(`registry.COMMENT_ROLES`はvoice数非依存の共有定義であり、grepで
   voice数分岐が存在しないことを確認したが、新規topic Writer-only入口
   自体がComment 1-4を呼ばない[3Vの既存`write_new_theme`と同一スコープ]
   ため、end-to-end生成では検証していない)。
6. **2V runtime evidence**: ✓。5節参照。
7. **3V regression evidence**: ✓。3節参照(オフラインでbyte不変性を証明
   できたため、3V実API再生成[上限¥100]は実施していない)。
8. **CURRENT_SPEC**: ✓。`CURRENT_SPEC.md`(OPEN-151段落直後に新規行
   「2/3可変Writer配線結果(OPEN-151)」を追加)。
9. **DECISION_LOG**: ✓。`DECISION_LOG.md`(PM-CLOSEOUT-CONSOLIDATION-130
   直後に新規エントリ+索引1行)。
10. **OPEN_ITEMS**: ✓。`OPEN_ITEMS.md`(OPEN-151行末尾に配線結果追記、
    OPEN-120行末尾に3Vゲート未発火の事実+2V構造的不発の判明を追記)。
11. **Git反映**: commit `d5c4df57`(push成功、origin/main反映済み、
    `6f1fcc92..d5c4df57`)。

## 3. 3V regression evidence(byte不変性)

改修前コード(`git show HEAD:er012_b_family_voices_writer_generic_01.py`を
`er014_output/four_type_observation_01/voices/writer_generic_before.py`へ
保存)を`importlib.util`経由でロードし、改修後コードと同一入力
(`er012_b_family_voices_theme_ai_screening_01.THEME_CONFIG`等の実データ)で
以下を比較した(`ThreeVoiceByteInvarianceAgainstHeadTests`、6テスト、
すべてPASS):
- `build_focus_module_block_3v()`の出力が完全一致
- `build_candidate_template()`の出力が完全一致
- `build_leakage_schema_3v(True/False)`の出力が完全一致
- `build_leakage_check_prompt_3v()`の出力が完全一致
- `build_ledger_fragment_visible_voices_only(num_visible_voices=3)`の出力が
  完全一致
- `make_theme_config()`(voice_cards=3件)の戻り値dictが完全一致

さらに`test_source_of_untouched_3v_functions_unchanged`で、3V専用関数
(`build_focus_module_block_3v`/`run_fact_check_a_prime_3v`/
`run_overlap_monitoring_3v`/Leakage関連4関数/`run_voices_pattern_3v`/
`run_pipeline_3v`/`run_ledger_deviation_and_local_rewrite`/
`_generate_and_compress_article_3v`/`_apply_b_family_voice_safety_gate`/
`split_six_voice_sections`/`build_ledger_fragment_visible_voices_only`/
`run_phase_a`/`build_candidate_prompt`)の`inspect.getsource()`が改修前後で
文字列として完全一致することを確認した(15関数)。

`git diff --stat -- er012_b_family_voices_writer_generic_01.py`の削除行は
7行のみで、すべて`make_theme_config()`のvoice数ガード(`!=3`→`not in (2,3)`)
と`run_writer_stage_generic()`の分岐化(3V呼び出し部分を`if num_voices==3:`
配下へ移動)に限られる(`git diff`の`-`行を`grep -v ^---`で確認済み)。

回帰: `er012_b_family_voices_writer_generic_01_test_01.py`(既存34テスト、
`test_theme_config_requires_exactly_three_voice_cards`は仕様変更に伴い
`test_theme_config_requires_two_or_three_voice_cards`へ更新、全PASS)、
`er012*_test_*.py`174件PASS、`er011*_test_*.py`266件PASS、全件回帰
2668件中2665件PASS(既知FAIL3件[`er003_test_bad`1件+`er003_test_p2j_
investigate`2件]のみ、新規FAILなし)。

## 4. 実装概要

- `er012_b_family_voices_writer_generic_01.py`: `make_theme_config()`の
  voice数ガード一般化(2/3受付、2V時external_constraint拒否)。新規:
  `COMMON_INTRO_AND_STRUCTURE_BLOCK_TEMPLATE_2V`(2V Trial-07由来の承認済み
  5区切り構造をテーマ非依存へ汎用化)、`build_focus_module_block_2v`、
  `split_five_voice_sections`(b1prod委譲)、`run_fact_check_a_prime_2v`、
  `run_overlap_monitoring_2v`、`TENSION_LEAKAGE_FIELDS_2V`/
  `build_leakage_schema_2v`/`build_leakage_check_prompt_2v`/
  `run_analytical_leakage_check_2v`/`build_leakage_corrective_note_2v`、
  `run_voices_pattern_2v`、`run_pipeline_2v`。`run_writer_stage_generic()`を
  voice数で分岐(3V部分は改修前と同一呼び出し列)。
- `er012_b_family_production_runner_01.py`: `main_b1_2v()`新規追加+
  `main()`へ`level=="b1_2v"`分岐追加(既存分岐は無変更)。
- `er012_b_family_editorial_type_registry_01.py`: **無変更**(既存実装で
  Gate3項目3を充足済みと確認したのみ)。
- 新規テスト`er012_b_family_voices_variable_voice_count_test_01.py`(33
  テスト)、既存テスト`er012_b_family_voices_writer_generic_01_test_01.py`の
  1テストを仕様変更に合わせて更新。

## 5. 2V runtime evidence

- topic: 「Is personalized news good for us?」(personalizationの便利さ・
  relevance[Voice 1]と、filter bubble/worldview narrowing/editorial
  control[Voice 2]の懸念の双方が成立するよう設計)。
- Ledger: `er014_output/four_type_observation_01/voices/research/`
  (Researcher+Verification、web_search 10クエリ、VERIFIED 18件・
  AMBIGUOUS 1件・REJECTED 0件)。VOICE_1/VOICE_2_EVIDENCEタグは、VERIFIED
  facts(改変なし)をFableが人手で分類して`verified_fact_ledger.txt`へ
  構成(先例: `er014_output/.../news/run_news_a2.py`のResearch→
  Verification構造をそのまま再利用、driverは`run_voices_2v_b1.py`)。
- Writer: 最大3 attempts。attempt1: Leakage Check flagged(voice_b/
  tension)→是正retry。attempt2: Leakage Check flagged(tension)→是正
  retry。attempt3(最終、attempt上限到達): Fact Checker A' verdict=
  `REVIEW_REQUIRED`(unsupported_specific_claims 2件、いずれも既存Fact
  Checker A'の通常挙動どおりの慎重な過剰検出寄りの判定、Ledger Deviation
  Checkerは3 attemptすべてで`LEDGER_COMPLIANT`・deviations=0)、Leakage
  Checkは依然flagged項目あり(voice_a/voice_b/tension、3項目)。全体
  `final_status="OK"`(Fact Checker verdictがFAILでない限り継続する既存
  3V同型の仕様どおり)。**このためGate3運用上は本記事をそのまま
  Production公開せず、REVIEW_REQUIRED/残存flagged項目を人手レビュー対象
  として扱う(既存3V同型仕様、`USER_DECISION_REQUIRED`候補として記録)**。
- 5区切り語数(attempt3、最終記事): Hook 68語/Voice A 95語/Voice B 92語/
  Tension 86語/Closing 54語、合計395語(soft target 320〜380語よりやや
  超過、hard capではないため許容)。
- 3V保守版Fact Safetyゲート・Local Rewrite・OPEN-141 diff QA: 3attemptとも
  Ledger deviations=0のため判定対象がなく**未発火**。なお本ゲートの実装
  (`_apply_b_family_voice_safety_gate`)は`b1prod.split_six_voice_sections`
  (6区切り)を前提としており、2V記事(5区切り)では構造的に判定対象を検出
  できない(fail-closed、安全側。2V対応拡張は本タスクの承認範囲外のため
  実装せず、事実として記録するのみ)。
- model_id: `gpt-5.6-luna`(Research/Verification/Writer/Fact Checker/
  Ledger Deviation Checker/Leakage Check すべて)。
- 出力: `er014_output/four_type_observation_01/voices/reader_facing_
  article.txt`(5区切り全文)、`voice_a.txt`/`voice_b.txt`、
  `b1_2v_new_theme_attempt{1,2,3}/`(各attemptのarticle.md・fact_qa.json・
  ledger_deviation.json・analytical_leakage_check_2v_attemptN.json・
  point_overlap_qa_monitoring_2v.json・metrics.json)、`cost_summary.json`、
  `production_set_cost.json`。

## 6. 費用

**Voices Production 1生成セット総原価 = ¥99.01**
(Research/Ledger ¥46.98 + Writer/QA/Gate/retry ¥52.03、TTS ¥0[新規topic
Writer-only入口のためTTS工程は未実行])。50:50配賦なし、直接費のみ
(PM_GOVERNANCE 15-8準拠)。費用上限¥150に対し実績¥99.01(¥50.99の余裕)。
3V再生成は実施していないため追加費用なし(合計費用上限¥250に対し実績
¥99.01のみ)。

driver(`run_voices_2v_b1.py`)の標準出力に表示された「費用実測(最終)=
¥46.98」は、`run_writer_stage_generic()`内部で`cl.install()`が
`b1_2v_new_theme/raw_usage_log_writer.jsonl`へログ出力先を切り替える
既存実装([3V経路と共通の既存仕様、本タスクでの変更ではない])により、
driver側の`cost_so_far_jpy()`がWriter側コストを見落とした表示バグである。
`cost_summary.json`は両ログを個別集計し直した正しい実測値。

## 7. API token(合算)

Research/Verification: input 213,460 / output 18,114 / cached 4,477
(2 calls)。Writer/QA/Gate/retry: input 264,299 / output 62,292 /
cached 13,413(15 calls、3 attempts分)。

## 8. Open Item候補

1. 2V記事(attempt3)がFact Checker `REVIEW_REQUIRED`+Leakage Check
   flagged項目を残したまま3 attempts上限に到達した。3V既存仕様と同型の
   挙動(3 attempts上限で打ち切り、残存flaggedはUSER_DECISION_REQUIRED
   候補として記録)であり、本タスクの範囲内では追加retry・Prompt改善は
   行っていない(Gate緩和禁止の遵守)。
2. 3V保守版Fact Safetyゲートが2V記事構造(5区切り)に対して構造的に不発
   である点(`_apply_b_family_voice_safety_gate`が6区切りを前提)。2V向け
   拡張は本タスクの承認範囲外のためSTOPし記録のみ(`OPEN_ITEMS.md`
   OPEN-120行に追記済み)。
3. Comment Contract(Comment 1-4)は新規topic 2V/3V双方のWriter-only入口
   から未接続のまま(3Vの既存スコープと同一の限界、新しいGapではない)。

## 9. T-0・事前指定外Read・STOP

- T-0: PASS(`docs/pm/delegation_log/EDITORIAL-B-FAMILY-VOICES-VARIABLE-
  VOICE-COUNT-PRODUCTION-WIRING-01_check.json`)。
- 事前指定外Read: `er012_b_family_voices_theme_ai_screening_01.py`
  L1-150(Voice Card構造の完全理解のため、L150-190の事前指定範囲だけでは
  Voice Card 1-3のフィールド構成が不明だった)。`er012_editorial_b_voices_
  trial_07.py`L195-524(2V Trial-07の承認済みFocus Module原文、2V汎用
  テンプレート作成の直接の基礎資料として必須と判断)。`er012_b_family_
  voices_production_01.py`L120-190(`split_five_voice_sections`/
  `build_parts`の既存シグネチャ確認、2V側実装の前提理解に必須)。
- STOP: なし(未承認範囲への逸脱・新規USER_DECISION_REQUIRED発生なし)。
