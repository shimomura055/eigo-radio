# EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-01

管理ID: EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-01(Lane B、HIGH、Opus設計レビュー済み)。
**Trial専用**(Production/Trial-07/registry/Contract編集禁止、SSOT・Git操作禁止)。同一管理IDでの
再開作業(前回セッションがユーザーの誤操作により途中停止)。

## 1. 中断時点の状態(再開時に確認した内容)

- 新規ファイル `er012_editorial_b_voices_4v_article_trial_01.py`(前回セッションで作成済み、
  約1680行)と `er012_output/editorial_b_voices_4v_article_trial_01/` は存在していた。
- Writer stage(Diagnostic Full Retry、`MAX_WRITER_ATTEMPTS=3`)のattempt1・attempt2は
  完全に完了済み(article.md/fact_qa.json/ledger_deviation.json/analytical_leakage_check_4v_
  attemptN.json/point_overlap_qa_monitoring_4v.json 一式が存在、いずれもFact Check verdict=PASS、
  Analytical Leakage Check any_flagged=True → 是正メモ付きで次attemptへ)。
- attempt3は Writer生成→Evidence Compression→Fact Checker A'(verdict=PASS、fact_qa.json保存済み)
  まで完了していたが、`run_ledger_deviation_and_local_rewrite()` 呼び出し中(Ledger Deviation
  Checker以降)で中断していた(ledger_deviation.json・analytical_leakage_check_4v_attempt3.jsonが
  未生成)。トップレベルの `b1b_run01_attempt_history.json`/`b1b_run01/summary.json` は、この中断より
  前の(4V化直後にProduction共通ゲート `h3_count!=2` に無条件で弾かれた)別の失敗run(1 attemptのみ、
  status=STRUCTURE_INVALID)の内容のまま残っていた。
- 発見済みのReconciliation finding(前回セッションが既にコード内コメントに記録): Production共通の
  `vfl01.run_writer_with_technical_retry()`→`validate_point_structure()`が`h3_count!=2`を無条件で
  STRUCTURE_INVALIDにするため、4V(見出し4つ)は必ず弾かれる。この汎用ゲートはB-Family Voices用途を
  想定しておらずProduction側の承認が必要なため変更せず、代わりに`vfl01.run_writer_no_search()`を
  直接呼ぶ`_generate_and_compress_article_4v()`をTrial側に用意し回避する対応が既に実装済みだった
  (再利用、変更なし)。
- 費用ログ`raw_usage_log_4v_writer.jsonl`(26件)は中断前まで記録済みで再開後もそのまま追記継続した。

## 2. 再開作業内容

1. `run_writer_stage_resume_from_interrupted_attempt3()`を新規追加(このTrialファイル自体への追記、
   Production/Trial-07/registry無変更)。attempt1/2の既存生成物は一切再生成せず、attempt3のみ
   Ledger Deviation Checker→Local Rewrite→比較方向Fact事前チェック→Analytical Leakage Checkを
   `run_voices_pattern_4v`/`run_pipeline_4v`と同一のPrimitive呼び出しで続行し、
   `b1b_run01_attempt_history.json`・`b1b_run01/summary.json`を実態(attempt1/2/3全て)に合わせて
   再構築した。
2. QA stage実行中に発見したバグ: `run_overlap_controls`/`build_word_count_and_duration_estimate`が
   参照する`b1prod.ARTICLE_PATH`が実在しない(Production側に該当定数が無い、`AttributeError`で
   停止)。design.md B-6が実測基準として引用する`EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-
   AND-FULL-EPISODE-03_REPORT.md`(301.795秒実測)に対応する実article
   (`er012_output/editorial_b_voices_trial_09_audio/b1b/article.md`)を`EXISTING_2V_ARTICLE_PATH_
   TRIAL09`定数として新規追加し参照するよう修正(Production側は読み取り専用のまま、書き込みなし)。
3. `run_qa_stage()`に再開安全性(既存comments_1_to_4.json/pairwise_voice_distinctness_check.jsonが
   あれば再利用し再生成しない)を追加。中断が無い通常実行には影響しない。

## 3. Writer stage結果

- 3 attemptsすべてFact Checker A' verdict=PASS(Production経路`runner.run_fact_check_b1`→
  `b1prod.run_fact_checker`→`r3.build_fact_check_prompt`、opt-in ON。block保存先:
  各attemptの`audit/fact_check_prompt_with_attribution.txt`)。
- Ledger Deviation: attempt1 MAJOR 1件→Local Rewrite 1 cycleで解消・LEDGER_COMPLIANT、attempt2
  MAJOR 0件・LEDGER_COMPLIANT、attempt3 MAJOR 1件→Local Rewrite 1 cycleで解消・LEDGER_COMPLIANT
  (human_review_required無し、cycle_exhausted=False)。
- Analytical Leakage Check(any_flagged): attempt1=True(4 Voice全て)、attempt2=True(4 Voice全て)、
  attempt3=True(voice_2/3/4、voice_1は是正で解消)。MAX_WRITER_ATTEMPTS(3)到達のため、attempt3を
  flagged状態のまま最終結果として確定(既存仕様どおり)。
- 最終status=OK、final_attempt_dir=`.../b1b_run01_attempt3`。

## 4. 7 section語数・尺見積り(最終article.md、post-Local Rewrite)

hook=56, voice_1=74, voice_2=81, voice_3=79, voice_4=91, tension=78, closing=50
(seven_section_length_report.json記載の509語はLocal Rewrite前のスナップショットのため、
QA stageで再集計した最終語数523語と差異あり、既存仕様どおりファイル更新なし)。
2V実測(Trial-09実測301.795秒)の秒/語比で換算した推定尺: **411.9秒**(目標380〜430秒の
monitoring範囲内、gate・正式検証ではない)。

## 5. Point Overlap Monitoring(16値、合否には使わない)

有向12ペア+ vs Hook 4値、全16値とも overlap_ratio 0.042〜0.171(閾値0.40を大きく下回る、
any_flagged=false)。¥0 control群: positive=0.857(flagged、想定どおり高overlap)、
deterministic=0.711(flagged、職名だけ違う合成ペアで指標の盲点を実証)、negative=0.14
(2V実採用ペア[Trial-09 article.md]再計算、flagged=false)、theme_vocab_dummy=0.389
(閾値付近、偽陽性リスクの近さを記録)。

## 6. Analytical Leakage Check 4V版 / Pairwise Distinctness Check

Leakage Check詳細(attempt3): voice_2(leak_evidence_subject軽微)、voice_3(5項目、Hilton
85%等の数値・Discovery型構成が経営者自身の経験描写より前面に出る)、voice_4(2項目、
NYC/EU規制説明が報告記事型に戻る)。Distinctness Check: 有向12ペア(個別呼び出し)+一括判定
(1回で4Voice・6ペア同時評価)を実施。direction_agreement_rate=0.9(30組中27致)、
method_agreement_rate=0.767(個別 vs 一括、30組中23致)。所要時間: 有向64.4秒/一括21.3秒。

## 7. Perspective Diversity(人手対応表、自動QAではない)

Voice 1〜4本文と`perspective_map.md`を目視で突合。Voice 1(動画面接評価・reliability
scoring・opt-out不可)、Voice 2(screening tool・audit summary・AI作成応募書類論争)、
Voice 3(Hilton 85%短縮・法的/評判リスク)、Voice 4(NYC LL144・EU AI Act・Amazonバイアス
事例)いずれもLedger根拠と一致。特定Voiceへの証拠偏重・他Voiceの証拠混入は確認されなかった。

## 8. 一人称/2対2/Tension/Closingの所見(重要な新規failure mode)

**最重要の発見**: ユーザー決定の設計原則「一人称"I"」が、3 attemptsすべてで**満たされていない**
(全記事とも三人称"The applicant..."/"She..."/"the recruiter..."で記述、"I"は0件)。既存の
2V本番採用記事(`er012_output/editorial_b_voices_trial_07/.../article.md`)は各Voiceが
"I look for..."のように明確に一人称で書かれており対照的。candidate_prompt_used.txtを確認したが
一人称指示自体が含まれておらず、Analytical Leakage Checkの6項目にも人称違反を検出する項目が無い
ため、3 attemptsとも検出されずに通過していた。賛否2対2分割は発生していない(Tension本文が
明示的に"These are not two teams"と述べ、4者それぞれ異なるリスクとして描写)。TensionはEvidence
要約に陥っておらず(具体的な数字の再掲なし、4者の経験の対比が中心)。ClosingはEvidence要約や
解決策提案ではなく問いの再定義("who has the power to judge...")になっている。

## 9. コスト実測(段階別、前回分込み)と量産時概算

- Writer stage(前回中断分+今回再開分合計、26 call): **¥35.0**
- QA stage(今回、15 call、Comment 1・4の2件+Distinctness 12+1件。Overlap Controls/Duration
  Estimate/Structure Reviewは¥0のrule-based処理): **¥2.1**
- **合計 ¥37.2**(上限¥300に対し十分な余裕)。
- 量産時概算(記事あたり): 現状のMAX_WRITER_ATTEMPTS=3をフルに消費してもtext-onlyで約¥35〜40/本。
  ただしLeakage Check flaggedが解消されないままattempt3で確定するケースが実測されており、
  一人称修正・Discovery型逆戻り修正を伴う場合はattempt数が増える可能性がある。

## 10. Gate 1分類・Gate 4

- **Gate 4**: Production(`er012_b_family_voices_production_01.py`・
  `er012_b_family_editorial_type_registry_01.py`・`er012_b_family_production_runner_01.py`)・
  Trial-07(`er012_editorial_b_voices_trial_07.py`)は`git diff`で無変更を確認(読み取り専用import
  のみ)。SSOT・Git操作は実施していない。
- **Gate 1分類**: 一人称"I"欠落・Voice 3/4のDiscovery型逆戻り(leakage flagged)という2つの新規
  failure modeが未解決のため、本記事は**USER_DECISION_REQUIRED**(Production採用判断は対象外、
  そもそもこのTrial記事自体の合否も現状では判定不可)。Fact Check/Ledger Deviation/Overlap/
  Perspective Diversityの各観点は個別にはVALIDATED相当。

## 11. 未承認仕様候補一覧

- Pairwise Voice Distinctness Check(有向12ペア+一括判定の枠組み自体、Opusレビュー2-HIGH起点)。
- Comment 2/3の4V版文言(design.md B-1手動ドラフト、registryへ未反映)。
- OPEN-129 4V required_structure(`voice_1..4`命名のvoice_map方式、正本統合はOPEN-132)。
- Overlap QA ¥0 control群の枠組み(Opusレビュー3-MED)。
- いずれも採用判断は別途USER_DECISION_REQUIRED。

## 12. STOP有無

**STOP**(新規failure mode: 一人称"I"欠落[全attempt]、Voice 3/4のDiscovery型逆戻り[attempt3も
未解消]。仕様を増やさず、完了済み部分のみ報告。プロンプト修正・再生成は行っていない)。

## 13. 新規ファイル一覧

- `er012_editorial_b_voices_4v_article_trial_01.py`(前回セッション作成、本セッションで
  resume関数追加・ARTICLE_PATHバグ修正・QA再開安全性追加)
- `er012_output/editorial_b_voices_4v_article_trial_01/` 配下一式(b1b_run01/b1b_run01_attempt1-3/
  qa/、attempt_history.json、summary.json、raw_usage_log_4v_writer.jsonl、
  raw_usage_log_4v_qa_stage.jsonl、required_structure_4v_trial_review.json)
- 本Report(`EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-01_REPORT.md`)
