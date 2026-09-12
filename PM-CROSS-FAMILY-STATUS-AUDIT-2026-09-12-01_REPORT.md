# PM-CROSS-FAMILY-STATUS-AUDIT-2026-09-12-01

**種別**: 横断現在地監査(read-only、SSOT編集・Git操作・コード変更・API支出なし)
**実施**: Sonnet(sonnet-worker)、2026-09-12。前回同管理IDはClaude API上限で中断、永続成果物なし(本タスクが実質初回完走)。
**方法**: `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`は全文読込せずGrep+行内オフセット抽出のみ。`OPEN_ITEMS.md`本体の巨大単一行(最大27,078字、OPEN-135行)はPythonでキーワード周辺のみ抽出。

---

## A-Family / Discovery

1. **現在Status**: タオルTrial-11(A2/B1B)= Gate1`VALIDATED(Trial)`のまま維持。ユーザーが標準playerで試聴し「A2/B1B試聴=OK/内容=OK/音声=OK/全体体験=OK」と正式評価(2026-09-12、`PM-CLOSEOUT-DISCOVERY-NPLUS1-AND-CROSS-FAMILY-STATUS-FOLLOWUP-01`、DECISION_LOG.md L3634-3689)。ユーザー指示により**Status/Gateは変更していない**(良好評価を理由にProduction自動採用していない)。
2. **完了済み**: A2/B1B双方Assembly PASS、GitHub経由配布(mp3+標準player.html、HTTP 200確認)。
3. **残作業**: Discovery仕様(discovery_why module登録等)のProduction採用は引き続き別途`USER_DECISION_REQUIRED`。
4. **ユーザー判断要否**: 不要(現状維持で確定)。
5. **次Action**: N=1追加Trial-12(`FAMILY-A-DISCOVERY-GENERALIZATION-WAKE-BEFORE-ALARM-TRIAL-12`、テーマはユーザー選定済み「Why do we sometimes wake up just before the alarm?」)が進行中。本タスク時点でA2記事生成済み(`er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/`、run_summary.json等あり)、B1Bはwriter_attempts段階まで(音声未生成)、コスト実績¥44.68時点、REPORT未作成。並行稼働中であり本監査では触れていない。
6. **Production wiring**: 未実施(Trial止まり)。

---

## A-Family / News

### 1. Point品質改善(Hanshin系Trial-12/12b/14)
1. **現在Status**: 主仮説「Fact数ではなく非headline角度のEvidence供給が重要」は`USER_DECISION_REQUIRED`のまま(`VALIDATED`未到達)。副仮説「fact数が多いほど良い」は**REJECTED**(条件C[fact10]最終NG率83.3%が条件A[fact5]と同率、単調性なし)。
2. **完了済み**: Trial-12(条件A/B)→Trial-12b(条件C/D)→Trial-14(条件E含む曖昧性解消)まで完走。Point生成段階の構造指標(初回Value QA flag 6/6→0/24)は主仮説を支持するが、Fact Checker以降の合否はFisher正確検定p=0.08で有意差未達。
3. **残作業**: 新規発見(Fact Checker FAIL 9件中7件=77.8%が人名ローマ字誤り)が主仮説とは独立の交絡要因と判明し、これが下記OPEN-146へ分岐。主仮説自体のUDR選択肢(a)人名対策を先に切り分ける/(b)他題材への一般化/(c)現状のまま主軸移動、は未回答のまま。
4. **ユーザー判断要否**: 要(UDR、上記a/b/c)。
5. **次Action**: 回答待ち。OPEN-135行(News節)に選択肢記載。
6. **Production wiring**: なし(Trial仮説段階)。

### 2. Ledger公式英語表記(OPEN-146)
1. **現在Status**: Trial-15(本体+修正1回目)= Trial closeout`VALIDATED`。SSOT上のStatus欄は`APPROVED_FOR_PRODUCTION`(実装済み、Gate 3進行中、`PRODUCTION_WIRED`は未宣言)。
2. **ユーザー承認証拠の検証結果(重要・要報告)**: `DECISION_LOG.md`全文で「⇒採用」の文字列は**0件**(grep実測)。`CURRENT_SPEC.md` L837に「ユーザー決定2026-09-12『#12 A-Family/News Ledger公式英語表記のProduction採用⇒採用』」という引用があるが、この引用の出典となるはずの`DECISION_LOG.md` `PM-CLOSEOUT-CONSOLIDATION-82`(UDR#12起票、L3402-3407、「Production採用は未承認」と明記)・`PM-CLOSEOUT-CONSOLIDATION-83`(L3442-3503、ユーザー指示原文はファイル`file:///`リンク運用是正のみを内容とし、UDR#12選択への言及は原文中に一切ない)のいずれにも、UDR#12で(a)/(b)/(c)のどれをユーザーが選んだかを示す記述がない。`PM-CLOSEOUT-CONSOLIDATION-83`本文は「OPEN-145/146行を`APPROVED_FOR_PRODUCTION`(2026-09-12ユーザー採用...)へ更新した」と記載するが、直前に転記されている「ユーザー指示原文」自体にはこの採用判断が含まれていない。**`CURRENT_SPEC.md`の「#12」は`PM-CLOSEOUT-CONSOLIDATION-84`(L3507-3508)で使われている並列タスクの通し番号ラベル(`#11`=OPEN-145担当タスク、`#12`=OPEN-146担当タスク)であり、UDR番号やユーザー発言の引用ではない可能性が高い。**
3. **結論**: 現時点で`DECISION_LOG.md`上に、UDR#12(a)/(b)/(c)いずれかをユーザーが選択したことを示す一次証拠(ユーザー指示原文の引用)は確認できない。にもかかわらずProduction配線(`er011_open146_ledger_canonical_en_spelling_production_01.py`新規作成、`er003_v1_n3_01_articles_generate.py`・`er002_ja_web_research_r3.py`への実装、commit `89f633d`)が既に実施され、SSOT上のStatusも`APPROVED_FOR_PRODUCTION`へ格上げされている。**これは「承認証拠が無いままAPPROVED_FOR_PRODUCTIONとして扱われている」STOP条件該当事案と判定する。**
4. **配線状況**: `er011_open146_ledger_canonical_en_spelling_production_01.py`(新規)、`er003_v1_n3_01_articles_generate.py::run_theme()`(Ledger読込直後、`canonical_en_spelling`行がある場合のみ発火・無ければbyte不変)、`r3.build_fact_check_prompt()`への後方互換引数`canonical_spelling_block`追加。新規回帰24/24 PASS、既存test 18/18 PASS、project-wide regression PASS。`CURRENT_SPEC.md` L837に記載済み。
5. **Gate 3残項目**: 「実News Production runでのruntime evidence」が未完了(新規記事テーマはPM_GOVERNANCE 13節によりユーザー選定必須のため未実施)。既存Ledgerへの遡及適用要否・固有名詞抽出コスト実測もUDR未回答のまま。
6. **ユーザー判断要否**: 要——(a)UDR#12(a)/(b)/(c)選択の事実確認そのもの(本当に(a)を承認したか)、(b)遡及適用要否、(c)コスト実測タイミング。

---

## B-Family / Voices(3V、OPEN-120)

1. **現在Status**: `APPROVED_FOR_PRODUCTION`(2026-09-11、`PM-CLOSEOUT-CONSOLIDATION-73`でユーザーが3Vを正式採用済みと確認。`VALIDATED(Trial)`から是正)。`PRODUCTION_WIRED`は未宣言。
2. **Production正式経路への配線範囲**: `er012_b_family_production_runner_01.py::main_b1_3v`ほか3V専用関数群(`prepare_3v`/`voice_check_3v`/`run_scaffold_3v`/`finalize_tts_results_3v`/`run_assembly_3v`/`assert_budget_ok_3v`)は実装済み。Voice衝突ガード、content integrity check(scaffold内fail-closed)、Ledger Deviation Check接続(monitoring専用)も実装済み(Phase 1+Phase 1b-02)。予算ガード(`BUDGET_JPY_CAP_3V=150.0`、TTS前後で判定)実装済み(Opus L2指摘1-bへの対応、Grepで実測確認済みとSSOT記載)。
3. **Writer/Ledger/Key Phrase**: **未配線**。Ledger作成のProduction化・Writer retry上限・新規記事に対するKey Phrase選定は、既存記事のみを扱うPhase 1/1bの範囲外であり、意図的に未実装(コード冒頭コメントに明記)。これがPhase 2(新テーマ3V記事)着手の前提を崩す不一致として記録されている。
4. **retry/fallback/regeneration整合**: 既存2Vと同型の安全機構(Human Review Lock、Local Rewrite、Fact Attribution)を再利用する設計方針は明記されているが、新規記事生成が発生しないため実発火は未確認。
5. **Production runtime実発火/runtime evidence/model_id・routing確認**: いずれも**未達**(REPORT内Gate 3チェックリストで「Phase 2待ち」と明記)。regression/integration testはoffline test 54/54 PASS(2026-09-11独立再実行確認)、project-wide regression PASS(既知3件failureのみ)。
6. **SSOT/Git反映**: `OPEN_ITEMS.md` OPEN-120行・`CURRENT_SPEC.md`に反映済み。Git側は commit `d742335`ほかで反映済み(現在の`git status`ではこれら4ファイルに未commit差分なし)。
7. **PRODUCTION_WIREDまでの未配線事項一覧**: (a) Phase 1b本体(Writer/Ledger/Key Phrase glue、見込み2〜3セッション・¥0、着手はユーザー承認済み[V-2]だが本タスク時点で未実施)、(b) 新テーマ3V記事1本のProduction runtime実行(見込み¥90〜150)、(c) 2V比較記事1本、(d) OPEN-132(Writer未配線起因のPhase 2前提不一致)の解消、(e) Gate 3の「実runtime evidence・model_id確認」。

---

## 共通 / 日本語ASR表記ゆれ一般化(OPEN-145)

1. **Trial最終結果**: `JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01`(初回+修正1回目+修正2回目)= Trial closeout**VALIDATED**。自作テスト82/82(100%)、実データMISMATCH5/7解消(残り2件は真の内容誤りで意図的に未解消)、過去PASS72件でregression0件。
2. **残存ギャップ**: カタカナ長音符・助数詞ヶ月表記(候補C領域)は本Trialで一部対応(3モーラ以上の外来語長音符省略差・ヶ月/ヵ月/カ月→か月統一はCandidate Cで実装済みとSSOT記載)だが、追加検証(長音符・助数詞ギャップ等)まで保留する選択肢(UDR#11(b))も提示されたまま。
3. **closeout**: VALIDATED(Trial)。
4. **ユーザー承認証拠**: OPEN-146と同様の問題がある。`DECISION_LOG.md`に「⇒採用」の文字列は0件。UDR#11は`PM-CLOSEOUT-CONSOLIDATION-82`(L3386-3387)で(a)配線案どおり採用/(b)追加検証まで保留、の2択として提示されたのみで、その後どちらが選ばれたかを示すユーザー指示原文の引用が`DECISION_LOG.md`に見当たらない。`CURRENT_SPEC.md` L1029は「ユーザー正式決定(2026-09-12、`APPROVED_FOR_PRODUCTION`)」と記載するが、対応する引用原文は無い。**OPEN-146と同一のSTOP条件該当パターン(承認証拠不明のままAPPROVED_FOR_PRODUCTION表示)**。
5. **配線状況**: 新規module`er011_ja_asr_variant_layer_01.py`(A2専用、B1へは非適用)、`er007_ja_asr_validator_01.py`/`er007_ja_secondary_asr_01.py`への追加型配線(既定ON、feature flag`FEATURE_FLAG_JA_ASR_VARIANT_LAYER_ENABLED`既定True、fugashi/unidic-lite import失敗時は自動的にFalseへfail-safe)。project-wide regression(collected=2346、failed=3=既知の無関係failureのみ)PASS。`CURRENT_SPEC.md`に反映済み。
6. **時系列整合**: タオルTrial-11 A2 `comment_2`は配線後のValidatorでoffline再判定されPHONETIC_MATCHでPASS採用(`PM-CLOSEOUT-CONSOLIDATION-84`)。承認→配線→再判定という順序自体はDECISION_LOG上のconsolidation番号順(82→83→84)で一貫しているが、**「承認」の実体(82→83の間でのユーザー選択)が確認できないため、この時系列全体が未確認の承認を前提に進んでいる**。

---

## 共通 / Repetition QA 数字↔数詞(OPEN-121)

1. **現在Status**: `APPROVED_FOR_PRODUCTION`(Gate 3進行中、2026-09-12`PM-CLOSEOUT-CONSOLIDATION-79-USER-CORRECTION-2026-09-12-02`でユーザーが正式決定と明記)。
2. **Gate 3進捗**: Production正式初回経路への組込みは「済」(`er011_open121_repetition_qa_production_01.py`が既存Production経路[`er003_v1_n3_01_tts_generate.py`等]からimport・呼び出し済みとGrep実証)。修正は同一共有module内部関数のみのため既存配線経由で自動反映。
3. **retry/fallback整合**: 判定閾値・`canonical_repeat_count >= 2`の意味は不変、比較前の正規化のみ追加。新規retry/Cost Guardの追加なし。
4. **runtime実発火/runtime evidence**: **未完了2項目**(「Production runtimeでの実発火」「runtime evidence」)が残る。
5. **regression**: 実施済み(既存flag記録の再判定、真陽性が消えないことを確認)。
6. **Production wiring残り**: 上記2項目の完了が前提。完了までは`PRODUCTION_WIRED`を宣言しない。既に`PRODUCTION_WIRED`の既存音声(pool_pilot_01等)は¥0の機械的遡及再判定のみ実施し、音声再生成・成果物差し替えは行っていない。

**このUDR#12/OPEN-121は「#11 ... ⇒採用」のような曖昧な引用ではなく、`PM-CLOSEOUT-CONSOLIDATION-79-USER-CORRECTION-2026-09-12-02`のエントリ自体がユーザー正式決定として明記されており、OPEN-145/146とは異なり承認経路は比較的明確である。**

---

## 共通 / TTS 20分cool-down観測Trial

1. **harness準備状況**: 3系統(A-Family Discovery Trial harness・News Trial harness・B-Family Trial harness)への配線完了(`er011_tts_cooldown_observation_harness_helpers_01.py`、`PM-CLOSEOUT-CONSOLIDATION-84`)。`TTS_COOLDOWN_OBSERVATION`未設定時は既定no-op(既定OFF相当)。
2. **Production retry仕様**: 不変。Production runnerには組み込んでいない(offline回帰・project-wide regressionで新規failureなしを確認)。
3. **条件維持確認**: 「3回連続NG→約20分→条件変更なし4回目1回」という観測条件自体は本タスク時点でのhook配線のみであり、条件のロジック確認はソースまで踏み込んでいない(read-only制約のため未検証)。
4. **観測件数N**: `er011_output/tts_cooldown_observation_01/`ディレクトリを確認したところ、**空(ファイル0件、N=0)**。データ収集は次回以降のTrial実行で自然発生する3連続NGから開始する設計(まだ発生していない)。
5. **旧・別系統の観測データ**: `er011_output/tts_retry_timing_monitor_01/observations.jsonl`(483行)、`er011_output/tts_retry_cooldown_analysis_01/cooldown_pairs.jsonl`は本Trial harnessとは別の既存分析(過去ログ集計)であり、両分析(主N=8・副N=15)は**母集団の100%が人的介入を含む**ため、新harnessでの「自然発生・人的介入混入なし」観測が別途必要という位置づけ。
6. **人的介入混入なし**: 新harness自体はまだデータが無いため判定不能(N=0)。過去の集計(即時<150秒 vs 非即時≥150秒、Fisher p=0.6851/p=0.578、いずれも有意差なし)は人的介入混入ありのため参考程度。

---

## Git状態

- 追跡済み変更(M、6件、いずれもrun-time状態ファイルでSSOT・コードではない): `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`、`er006_output/pronunciation_ledger_01/ledger.json`、`er011_output/attempt_history.jsonl`、`er011_output/family_a_completion_a2_trend_end_to_end_01/b1b/audit/{review_lock_state.json, tts_generation_results.json}`、`.../key_phrases/keywords_canonicalized.json`。これらはタオルTrial-11のOPEN-121/145配線後resync等、進行中の並列作業由来と推定され、SSOT不整合ではない。
- 未追跡(??、325件)。大半は`er002_output/`・`er003_output/`配下の既知未整理ファイル(OPEN-124で「発見の記録のみ、分類・整理は未着手」と記録済み)。新規追加分としてはDiscovery Trial-12(`er011_output/discovery_generalization_wake_before_alarm_trial_12/`)が並列稼働中の生成物として未追跡のまま存在(進行中のため妥当)。
- 会話開始時点のgitStatusスナップショット(er012_b_family系4ファイルがM)は、本タスク実施時点では既にcommit済み(`git diff`空、直近commit`d742335`)で解消しており、現在の実態と一致していない(スナップショットの陳腐化であり、SSOT不整合ではない)。
- SSOT本体(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)に未commit差分なし(git statusに該当ファイル名なし)。

---

## 一覧表

| Family / 項目 | 現在Status | 残作業 | ユーザー判断 | 次Action |
|---|---|---|---|---|
| Discovery(タオルTrial-11) | `VALIDATED(Trial)`維持、ユーザー試聴OK記録済み | Production採用判断 | 要(UDR、Production採用可否) | ユーザー回答待ち |
| Discovery(N=1 Trial-12) | 進行中(A2完了・B1B途中、REPORT未作成) | 記事制作完走、closeout判定 | 不要(現時点) | 並行作業継続 |
| News Point品質(Trial-12/14) | `USER_DECISION_REQUIRED`(主仮説未確定) | UDR(a)/(b)/(c)選択 | 要 | ユーザー回答待ち |
| News Ledger英語表記(OPEN-146) | `APPROVED_FOR_PRODUCTION`(配線済、Gate3進行中)だが**承認証拠不明** | 承認事実の再確認、Gate3(runtime evidence) | **要(緊急、承認有無の確認)** | Fable/ユーザーへ承認事実確認を要請 |
| B-Family 3V(OPEN-120) | `APPROVED_FOR_PRODUCTION`(未配線多数) | Phase 1b(Writer/Ledger/KeyPhrase)、Phase2 runtime evidence | 要(Phase1b着手タイミングは既承認、実行判断は次アクション) | Phase 1b実装着手 |
| JA ASR表記ゆれ(OPEN-145) | `APPROVED_FOR_PRODUCTION`(配線済)だが**承認証拠不明** | 承認事実の再確認 | **要(緊急、承認有無の確認)** | Fable/ユーザーへ承認事実確認を要請 |
| Repetition QA数字↔数詞(OPEN-121) | `APPROVED_FOR_PRODUCTION`(Gate3進行中、承認経路明確) | runtime実発火・runtime evidence | 不要(既に承認済み) | 実News/実記事runでのruntime evidence取得 |
| TTS 20分cool-down | harness配線完了、N=0 | 自然発生データ蓄積待ち | 不要 | 次回Trial実行時に自然発生3連続NGを観測 |

---

## STOP条件該当一覧

1. **APPROVED_FOR_PRODUCTIONだがユーザー承認証拠が確認できない(OPEN-146、News Ledger公式英語表記)**: `DECISION_LOG.md`にUDR#12の選択結果(a/b/c)を示すユーザー指示原文が見当たらない。`CURRENT_SPEC.md`の「#12...⇒採用」引用は、出典と主張される`DECISION_LOG.md`側に対応する原文がなく、並列タスク番号ラベル(#11/#12)との混同の疑いがある。にもかかわらずProduction code(`er011_open146_ledger_canonical_en_spelling_production_01.py`ほか)が既にcommit済み。
2. **同様の事案(OPEN-145、JA ASR表記ゆれ一般化)**: UDR#11の選択結果を示すユーザー指示原文が`DECISION_LOG.md`に見当たらないが、`er011_ja_asr_variant_layer_01.py`が既定ONでProduction配線済み(`er007_ja_asr_validator_01.py`/`er007_ja_secondary_asr_01.py`に組込)。
3. **上記1・2は同一の`PM-CLOSEOUT-CONSOLIDATION-83`エントリ内で発生**しており、当該エントリの「ユーザー指示原文」欄には試聴リンク運用(`file:///`禁止)の指示のみが記載され、OPEN-145/146のAPPROVED_FOR_PRODUCTION化への言及が原文中に存在しない点が構造的な問題(1件のconsolidationエントリ内で、原文にない決定がSSOT更新根拠として記載されている)。

上記2件以外(Discovery、News Point品質、B-Family 3V、Repetition QA、TTS cool-down)については、本監査で確認した範囲でVALIDATED/APPROVED_FOR_PRODUCTIONの混同・Gate 3未完了の未申告・runtime evidenceなしのPRODUCTION_WIRED宣言・Trial/DEV pathのProduction誤認・SSOT三点(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)間の不整合・未報告Trial・未登録Open Itemには該当しない(いずれも各Status欄に限界・未達項目が正直に明記されている)。
