# C4-7 W-1下流 開発用確認run 実行計画書(RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C4、2026-10-10)

**本書は計画のみ。本委任(委任_10)では実行していない(課金API 0件)。実行はFable/ユーザーの指示後。**
呼称: 「**W-1下流 開発用確認run**」(`--run-label W1_DOWNSTREAM_DEV_CONFIRM`)。禁止表現: 「W-1完全Production E2E」「最終L3」「L3 PASS」「新規記事E2E PASS」「W-1 PRODUCTION_WIRED」。
許容表現: 「正式annotated B3 producer(D-det v2+決定論assembler)+W-1下流+RF+Queue+TTS+技術QAの実機確認(research/ledger/B3は既存テーマの実データ再利用・新規生成は未確認)」。

## 1. 入力テーマの推奨

推奨(1本): **`semiconductor_earnings`**(ROOTFIX-02 E9の問題5の1本。台帳・B3実データ=`er052_output/factlock_astra_e2e_trial_01/g0_real_annotation_01/semiconductor_earnings/shared/`が揃っている)。
理由: 5Fact・AMBIGUOUS 1件(固定限定文の動作確認)・制約ブロック4件・中核/周辺の上限(cap 5)にちょうど達し cap超過の周辺化notes 2件を持つ=producerの全機能が1本で動く。
代替(軽量): `byd_recall`(5Fact・制約4件・cap 3、数値5)。他の候補の特徴(producer実測、`c4_candidate_features` 参照): small_bag(3Fact軽量)/space_weapons(制約5)/hormuz(数値11)/central_bank_mortgage(数値20・最重)。
新規記事ではなく既存Trial入力の再利用なので PM_GOVERNANCE 13節(新規記事テーマ選定ルール)の対象外の見込み(Fableが確認)。

## 2. 手順(Production正式入口 `main()` を実コードで駆動)

0. 作業ブランチ `feature/factlock-rf-wiring-01`(C4 commit後のHEAD)で実行。stubは使わない(client/英訳/RF/TTSすべて実API)。
1. 入力準備(adapter、課金0): `py -X utf8 -c "import er053_dev_b3_fixture_adapter_01 as a; a.copy_inputs('semiconductor_earnings', 'er019_output/_w1_down_confirm_01/run_01')"`
   (台帳・`selected_brief.md`・`fact_selection_evidence.json`を複製するのみ。注記artifactは作らない=`trial_fixture`は廃止済み。)
2. Writer〜Advanced〜Standard(正式入口): 
   `py -X utf8 er019_family_x_entertainment_production_runner_01.py --theme "<topic.txt>" --slug _w1_down_confirm_01 --out-dir er019_output/_w1_down_confirm_01/run_01 --budget-jpy 300 --run-label W1_DOWNSTREAM_DEV_CONFIRM`
   実行順(コード上の固定): (既存Ledger再利用) → (既存`selected_brief.md`再利用) → **正式producer(LLM 0)** → 契約検証(T-19) → W-1 R0 Luna → 記号QA → R1 Astra → R2 Astra → Advanced EN(M1(a)) → **Advanced RF** → Standard → **Standard RF** → Queue保存 → Mandatory STOP。
   (`--budget-jpy 300` は `efam.assert_budget_ok` の各ガード=R0前/R1前/R1-R2間/EN後/RF後で効く。cap超過は既存どおりSTOP。)
3. ユーザー確認(Mandatory STOP)後、audio側(同じ`--budget-jpy 300`):
   `py -X utf8 er019_family_x_audio_production_runner_01.py --slug _w1_down_confirm_01 --run run_01 --stage scaffold --tts-backend speech_metadata_flash_lite --budget-jpy 300`
   → `--stage tts`(TTS直前に三者sha照合=C3-1。一致ならRF再実行なし)。assemble/playerは本runの範囲外(必要ならFable判断)。
4. 各段後に `cost.json`・`raw_usage_log.jsonl`・`storyline_b3/audit/annotation_producer_evidence.json`・`ja_writer/runtime_evidence.json`・Queue(index.jsonl)を保存。

## 3. 費用見積(根拠=委任_10指示+DESIGN_03 11-4。未測定は未測定と明記)

| 工程 | 見積 | 根拠 |
|---|---|---|
| research / ledger / B3 | ¥0 | 既存テーマの実データ再利用(adapter複製。`run_research_and_ledger`/`selected_brief.md`再利用分岐) |
| 正式producer(D-det v2+assembler)+契約検証 | **¥0** | 決定論・LLM call 0・API 0 |
| W-1 R0 (Luna gpt-6-luna) | ¥0.45〜1.24 | 実測レンジ(委任_10指示) |
| W-1 R1+R2 (Astra gpt-6-astra) | raw ¥30.6 / budget guard×1.5=¥45.9 | REPORT §111(raw実測)。係数はOPEN-246請求照合まで |
| EN(Advanced+Standard、Checkerなし) | ≤¥4.22 | 既存実測(Checker込み上限。Checkerなし単独は未測定) |
| RF 4条件(Level別) | 約¥1.49 | Adv実測。Std外挿=未確認 |
| **(a) JA→RF→Queue 小計** | **¥36.8(raw下限)〜¥52.9(Astra×1.5・Luna上限)** | 上の和 |
| TTS+ASR+KP | ¥24〜89 | run間差・条件差は未確認 |
| **(b) TTS込み合計** | **¥60.8〜¥141.9** | (a)+TTS |
| retry余裕(最悪ケース加算) | +約¥30 | R0記号QA再生成(+¥1.2)・R2記号QA再実行(raw +¥15.3/guard×1.5 +¥23)・EN段落retry(+¥4.2)の同時発生を仮定 |
| **最悪ケース見積** | **≈¥172** | |
| **Cap** | **¥300**(ユーザー承認済み) | 最悪ケースの約1.7倍。通常ケース(〜¥142)の2.1倍 |

注: RF追加実行(TTS guardでscaffold sha不一致時)は1 Level約¥0.75〜。Astra請求照合(OPEN-246)は未了のため guard×1.5 は暫定係数。

## 4. 確認項目(Runtime evidence)

producer系(C4新規):
- P1 `storyline_b3/annotation_manifest.json`: `producer="deterministic_v2"`(`trial_fixture`でない)・`llm_calls=0`・`rules_sha256`=`c4_port_sha_table.json`の値・`input_shas`(selected_brief.md/台帳/evidence)が実ファイルshaと一致
- P2 `ja_writer/runtime_evidence.json`: `annotation_manifest_producer`・`annotation_rules_sha256`・`annotation_input_shas`・`writer_constraints_sha256`・`news_field_sha256` が記録され、producer evidenceと一致
- P3 R0 Promptの[ニュース]欄=注記済みFacts+制約ブロック(`r0_meta.json`の`r0_prompt_sha256`とnews field shaの再計算一致。R0 Prompt本体=`verbatim_shas`がC1/C2のpinned値のまま)
- P4 `fact_selection_evidence.json`: `selected_fact_brief_text`が決定論出力・`b3_llm_selected_fact_brief_text`に元のB3文が退避
- P5 `raw_usage_log.jsonl`にproducer由来のAPI recordが0件(stage tag `annotation*`なし)
DESIGN_03 11-5由来(E1〜E15から抽出): E1(W-1がProduction経路で実行・Trial module非import) / E2(model_id requested/returned・mismatch 0) / E3(旧Checker呼出0) / E4(Advanced RF→Standard生成→Standard RFの順序timestamp) / E10/E11(Queue保存・index.jsonl) / E13(TTS以降の技術QA) / E15(費用実績 vs 見積) / 契約検証V1〜V10の合格ログ。
併せて(¥0・stubで既に確認済みの経路を、実機で再確認する場合のみ): 初回以外の経路(`--stage standard`再開・`--regenerate-stage storyline_b3`)でproducerが先行し契約検証が通ること。

## 5. 停止条件

producer失敗(`AnnotationProducerError`)・契約違反・`BudgetCheckStop`・`JASymbolCheckStopError`・R0/R1/R2のmodel_id不一致・累計 ¥300到達 → その時点でSTOPしFable/ユーザーへ報告(再試行は既存のretry上限内のみ。上限を独自に変えない)。
