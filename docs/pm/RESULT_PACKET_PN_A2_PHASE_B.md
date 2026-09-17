# RESULT_PACKET: PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B(累積Full Report)

管理ID: `PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B`(前段: Phase A
`docs/pm/RESULT_PACKET_PN_A2_GAP_PHASE_A.md`[結論: STOP/`USER_DECISION_
REQUIRED`、ユーザー正式決定3点取得]、PREFLIGHT `docs/pm/RESULT_PACKET_
PN_A2_PREFLIGHT.md`)。

★★★★報告ここから★★★★

## 0. T-0(委任文検証)

`docs/pm/delegation_log/PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B.md`
を保存し`check_delegation_prompt.py`を実行。結果=`FAIL`(既知パターン:
「事前指定Grep一覧+追記位置・更新位置の手順」を「事前指定Read/Grep一覧」
統合見出しにしたため単独keyword不一致、「実行コマンド全文」セクション
見出しも欠落。他の必須項目6/8 OK、固定ブロックE-1/D-1/G-1/F-1 OK)。
ルールどおりFAILでも継続。JSON: `docs/pm/delegation_log/
PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B_check.json`。

## 1. 現在Status

**`WIRING_INCOMPLETE`**。B-Family新規topic A2 E2E Production配線自体は
完了しregression PASS(下記14節)。Personalized News A2の記事stage
(Writer/Fact Checker/Ledger Deviation/Comment Contract/Key Phrase/日本語
タイトル)は完走したが、Narrator見出し2segmentがHuman Review Lockへ
滞留し、完成episode/playerは生成できていない(user decision待ち、9節・
20節参照)。Preflight/Phase Aの結論(1〜2行): Preflight=B-Family A2新規
topic Writer入口が不在と判明・`USER_DECISION_REQUIRED`。Phase A=Family
横断監査でLedger→A2 Writer直接生成が共通パターンと確認、ユーザー正式
決定3点(A2生成方式/Key Phrase選定元/日本語タイトル供給方式)を取得。

## 2. Family横断原則との整合

`docs/pm/PM_GOVERNANCE.md`18節「Family横断共通化原則」のとおり、B-Family
新規topic A2をA-Family標準パターン(Ledger→level別独立Writer)へ統一した。
Fact Checker/Ledger Deviation Checker/TTS・ASR安全機構/Audio Validation
Gate/Human Review Lockは全て既存共有primitiveをそのまま再利用し、新しい
Family固有QA機構は追加していない。Key Phrase選定機構(Strategy L+
Canonicalization)も共有primitiveを再利用し、「選定元は自分自身の本文」
というA-Family標準原則をB-Familyへ適用した。

## 3. 実装したA2 E2E構成(ファイル:関数、呼び出し順)

1. `er012_b_family_voices_theme_personalized_news_a2_01.py`(新規): テーマ
   固有データ(Ledger path/Voice Card 2件/Tension content/`JAPANESE_
   TITLE_A2`)。
2. `er012_b_family_voices_writer_generic_01.py::run_writer_stage_generic()`
   (`instruction`引数追加、既定None=`gen.B1_B_DIRECT_INSTRUCTION`不変)
   → 内部で`run_pipeline_2v`→`run_voices_pattern_2v`(Writer→Overlap
   monitoring→Fact Checker A'[`run_fact_check_a_prime_2v`]→Ledger
   Deviation+Local Rewrite→Directional Fact Precheck)→Analytical
   Leakage Check(是正retry込み、最大3 attempts、既存関数無変更)。
3. `er012_b_family_production_runner_01.py::main_a2_2v()`(新規、
   `level="a2_2v"`): `write_new_theme`(上記2呼び出し)→`comment`
   (`a2prod.run_scaffold_a2`、既存関数そのまま)→`key_phrases`
   (`a2prod.run_key_phrases_a2_from_own_text`新規)→`japanese_title`
   (`a2prod.generate_japanese_title_for_new_topic`新規)→`voice_check`
   (`b1prod.run_voice_availability_check`/`resolve_voice_names`既存)→
   `tts`(`run_tts_a2_2v_new_topic`新規、`a2prod.generate_narrator_
   heading_with_a2_slowdown`/`generate_narration_wide_margin_with_a2_
   slowdown`新規合成関数+既存`generate_voice_body_wide_margin_with_a2_
   slowdown`+`run_comment_audio_a2_2v_new_topic`新規)→`assemble`
   (`run_assembly_a2_2v_new_topic`新規、内部は既存`a2prod.load_a2_
   sources_for_b_family`/`build_a2_voices_timeline`/`asm.*`そのまま)→
   `player`(`build_player_html_a2_2v_new_topic`新規、内部`a2prod.row_
   info_a2`既存そのまま+`export_web_delivery_a2_2v_new_topic`新規)。

## 4. Production entrypoint(CLI実行例全文)

```
python er012_b_family_production_runner_01.py write_new_theme a2_2v er012_b_family_voices_theme_personalized_news_a2_01 er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2
python er012_b_family_production_runner_01.py comment a2_2v er012_b_family_voices_theme_personalized_news_a2_01 er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2
python er012_b_family_production_runner_01.py key_phrases a2_2v er012_b_family_voices_theme_personalized_news_a2_01 er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2
python er012_b_family_production_runner_01.py japanese_title a2_2v er012_b_family_voices_theme_personalized_news_a2_01 er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2
python er012_b_family_production_runner_01.py voice_check a2_2v er012_b_family_voices_theme_personalized_news_a2_01 er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2
python er012_b_family_production_runner_01.py tts a2_2v er012_b_family_voices_theme_personalized_news_a2_01 er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2
python er012_b_family_production_runner_01.py assemble a2_2v er012_b_family_voices_theme_personalized_news_a2_01 er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2
python er012_b_family_production_runner_01.py player a2_2v er012_b_family_voices_theme_personalized_news_a2_01 er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2
```
(`all`stageで一括実行も可。既存`main_a2()`[free_address]・`main_b1_2v()`
は無変更のまま利用可能。)

## 5. A2 Writer方式(instructionの要点、CURRENT_SPEC整合)

`er003_v1_n3_01_articles_generate.py::A2_KAI1_INSTRUCTION`(A-Family全体で
既に共有承認済み、CURRENT_SPEC「CEFR-A2構造」節Core Explanatory Logic
Preservation原則を含む)をそのまま流用し、新しいinstruction文言は一切
創作していない。B-Family既存承認済みFocus Module構造(2V/5区切り:
Hook/Voice A/Voice B/Tension/Closing、一人称"I"、体験claim根拠付け恒久
原則)は無変更のまま維持し、末尾の【難易度指示】節だけをB1用から
A2_KAI1_INSTRUCTIONへ差し替えた(`build_candidate_prompt`の`instruction`
引数)。

## 6. Key Phrase方式

`run_key_phrases_a2_from_own_text()`がA2確定本文(Local Rewrite後の最終
article_text)から`sc.run_key_phrases(process="A2_SUPPORT")`(既存
Strategy L+Canonicalization共有primitive)で新規選定。5件選定・
`REDUNDANCY_PASS`。英語Componentは既存Master Audio Store経由(Aoede)、
日本語glossは標準A2 Aoede経路で新規生成。schemaは既存consumer
(`load_a2_sources_for_b_family`/`row_info_a2`)と完全一致(変更なし)。

## 7. 日本語タイトル方式(contract定義箇所)

Contract: theme_moduleが`JAPANESE_TITLE_A2`(str)をexportし、
`main_a2_2v()`がそれを`a2prod.generate_japanese_title_for_new_topic()`
(新規、`CURRENT_SPEC.md`「B-Family(Voices)Editorial Type」節「新規topic
A2 Production経路」行に記載)へ渡す。write_new_theme stage実行後、A2
Writerが実際に確定した英語タイトル("The News You See, and the News You
Miss")を確認してから、その自然な直訳(「見えているニュースと、見えて
いないニュース」、新規主張・数字なし)へtheme module側を更新した。

## 8. QA/retry/fallback(配線一覧+runtime結果)

| QA | 配線 | runtime結果 |
|---|---|---|
| Fact Checker A' | `run_fact_check_a_prime_2v`(既定接続、opt-inではない) | attempt1 PASS→attempt2 PASS→attempt3 REVIEW_REQUIRED |
| Ledger Deviation Checker + Local Rewrite | 既存`run_ledger_deviation_and_local_rewrite` | 全attemptでMAJOR 1件検出→Local Rewrite 1 cycleで解消、最終`LEDGER_COMPLIANT` |
| Analytical Leakage Check(是正retry最大3) | 既存`run_analytical_leakage_check_2v`+`build_leakage_corrective_note_2v` | attempt1 flagged(voice_b 3項目)→attempt2 flagged(voice_b 1項目)→attempt3 flagged(voice_a 1項目・voice_b 2項目)、3attempt上限到達で残存(USER_DECISION_REQUIRED候補、既存B1/3V仕様と同型) |
| Directional Fact Precheck | 既存(rule-based、¥0) | 全attempt PASS |
| Key Phrase Redundancy QA | 既存 | `REDUNDANCY_PASS`(retry不要) |
| Human Review Lock | 既存`review_lock.guarded_generate` | `point_one_heading`/`point_two_heading`が`HUMAN_REVIEW_REQUIRED`へ遷移(9節参照)、override無し |
| Audio Validation Gate(B_FAMILY_A2) | 既存`verify_episode_audio_validation_gate` | 上記2segment未検証を理由に`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`(Gate緩和なし、正しく機能) |

## 9. Personalized News A2 runtime

- タイトルEN: "The News You See, and the News You Miss" / JA: 「見えて
  いるニュースと、見えていないニュース」
- 語数: 410語(280〜500の範囲内、追加の明記事項なし)
- Writer attempts: 3(3attempt上限到達、Leakage残存のため)
- Fact Checker: PASS→PASS→REVIEW_REQUIRED(最終)
- Ledger Deviation: 全attempt`LEDGER_COMPLIANT`(Local Rewrite 1件resolved)
- Leakage: 3attempt上限到達後も残存(voice_a: `leak_discovery_syntax`、
  voice_b: `leak_numbers_foreground`/`leak_discovery_syntax`)
- TTS segment数: 14(topic_intro/point_one_heading/point_two_heading/
  point_one/point_two/full_story_part1/full_story_part2/tension_
  reflection/in_one_line/preview/comment_1-4)+Key Phrase 5件+日本語
  タイトル1件
- ASR: 上記14中12件`OK`、2件(`point_one_heading`/`point_two_heading`)
  `ASR_VALIDATION_UNCERTAIN`(見出し冒頭の接続句"One Voice:"/"Another
  Voice:"がASR文字起こしで脱落するclassでretry打ち切り、詳細20節)
- **Human Review Lock有無**: **あり**(上記2segment、
  `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`
  へ記録)。委任文の指示どおりoverride・承認代行せずSTOP(承認記録なし)。

## 10. Audio Gate

`assemble`stage実行結果: `GATE_BLOCKED`(`EPISODE_BLOCKED_BY_AUDIO_
VALIDATION`、`point_one_heading=UNVALIDATED`/`point_two_heading=
UNVALIDATED`、override無し)。Gateが正しく機能していることの実測evidence
(安全≠成功原則、Gate緩和なし)。

## 11. player URL

**未生成**(9〜10節のHuman Review Lock/Gate Blockにより完成episode自体が
存在しないため)。Human Review Lock解消(user decision)後、`player`stage
再実行で`player.html`+`web/episode.mp3`(+segments)+raw.githack URLを
別途生成する。

## 12. cost(実測、model別)

合計¥71.84。内訳: Writer/Fact Checker/Ledger Deviation/Local Rewrite/
Comment Contract(OpenAI, `gpt-5.6-luna`)=¥33.89(Writer段階の別ログ集計、
`personalized_news_2v_a2_writer/raw_usage_log_writer.jsonl`)。Key Phrase
選定(OpenAI)+TTS(Gemini `gemini-2.5-pro-preview-tts`[英語]/
`gemini-3.1-flash-tts-preview`[日本語])+ASR(`gpt-4o-mini-transcribe`/
`azure-speech-stt`)=¥37.95(`personalized_news_2v_a2/audit/raw_usage_
log.jsonl`)。予算目安(累積¥250)以内。

## 13. model_id/routing

Writer/Fact Checker/Ledger Deviation/Comment: `gpt-5.6-luna`(routing
`A2_WRITER`/`A2_SUPPORT`/`WRITER_FACT_CHECK`、`label="A2"`指定で正しく
A2_WRITER routingへ到達、実測確認)。TTS英語: `gemini-2.5-pro-preview-
tts`(Aoede/Algieba/Erinome)。TTS日本語: `gemini-3.1-flash-tts-preview`
(Aoede)。ASR: `gpt-4o-mini-transcribe`(primary)+`azure-speech-stt`
(secondary cascade)。

## 14. regression(test名・件数・PASS/FAIL)

- `er012_b_family_voices_variable_voice_count_test_01.py`+
  `er012_b_family_voices_writer_generic_01_test_01.py`+
  `er012_editorial_b_family_production_phase1_test_01.py`+
  `er012_editorial_b_family_voices_3v_production_wiring_phase1_test_01.py`+
  `er012_open131_fact_attribution_production_wiring_01_test_01.py`: 185件PASS。
- `er013_family_c_production_test_01.py`: 39件PASS(共有primitive無変更確認用)。
- 新規`er012_b_family_voices_a2_new_topic_production_01_test_01.py`: 13件PASS
  (Trial非import3件、引数検証3件、instruction一般化後方互換3件、日本語
  タイトルconfig契約2件、Key Phrase選定元契約2件)。
- project-wide regression(`run_project_regression.py`、pattern
  `er0*_test_*.py`、129 test files): **2891/2894 PASS**。既知FAIL3件
  (`er003_test_bad.FixtureTests.test_case_0`、
  `er003_test_p2j_investigate.CollectionCountTests.
  test_combined_equals_sum_of_er002_and_er003`、
  `er003_test_p2j_investigate.ReconciliationArithmeticTests.
  test_p2h/test_p2i_...`)のみ、いずれも本タスクと無関係な既存FAIL
  (歴史的reconciliation算術テスト・意図的な"bad fixture"テスト)。
  新規FAILなし。summary: `docs/pm/delegation_log/
  pn_a2_phase_b_regression_summary.json`。

## 15. CURRENT_SPEC更新行

`CURRENT_SPEC.md`「B-Family(Voices)Editorial Type」節: L667(日本語
タイトル)・L668(Key Phrase)行へ「既存固定記事経路では従来どおり、新規
topic経路では下記行を適用」を併記(既存行削除なし)。新規行「新規topic
A2 Production経路(Ledger直接A2 Writer/Key Phrase=A2本文から選定/日本語
タイトル=config供給)」を追加、Status=`WIRING_INCOMPLETE`(実測結果反映)。

## 16. DECISION_LOG行

`PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B`エントリを新設
(`## 参照元`節の直前)。実装内容・Personalized News A2 runtime結果・
cost・regression・Status=`WIRING_INCOMPLETE`を記録。

## 17. OPEN_ITEMS更新

- OPEN-132: 項目(1)「Fact Checker A'既定stage接続」が、B-Family**新規
  topic A2入口**については解消済みである旨を追記(既存固定記事経路は
  対象外・無変更のまま)。
- OPEN-151: 2026-09-17追記として、本Phase Bの配線結果・Personalized
  News A2 runtime結果(Human Review Lock滞留・Status=`WIRING_INCOMPLETE`)
  を追記。
- A2 E2E gap自体は新規登録しない(委任文の指示どおり)。

## 18. Git commit/push

(このRESULT_PACKET・SSOT反映commitは本レポート確定後に実施。commit SHA
は次のcommitで別途追記する。)

## 19. Dangling Reference Check(6項目)

1. 新A2 Writer instructionがCURRENT_SPECと整合: ○(`A2_KAI1_INSTRUCTION`
   はCURRENT_SPEC「CEFR-A2構造」節のCore Explanatory Logic Preservation
   原則を含む既存承認済みinstructionをそのまま流用)。
2. retry/fallbackも同じinstruction・仕様を見る: ○(`run_pipeline_2v`は
   全3 attemptで同一`candidate_prompt`[+corrective_note]を使用)。
3. Key Phrase contractが初回pathと後段(TTS・player)で一致: ○(schema
   `used_form`/`japanese_gloss`/`rank`は既存consumer関数と完全一致、
   変更なし)。
4. 日本語タイトルcontractが正式仕様として存在(CURRENT_SPECへ記載): ○
   (15節のとおり追記済み)。
5. Trial定義をProductionが参照していない: ○(新規test`NoTrialOrFixed
   TopicImportTests`3件+既存test`NoTrialScriptModuleLevelImportTests`
   [runner module含む]で確認、regression PASS)。
6. B1→A2翻案の旧Trial codeが新Productionから参照されていない: ○
   (`run_writer_adapt`/`build_adapt_prompt`は新規コードから一切呼ばれて
   いないことをgrepで確認、コメント内の言及のみ)。

## 20. 未決事項/同時解消した独立問題/Open Item候補

- **user decision待ち(本タスクのSTOP事項)**: Human Review Lock
  (`point_one_heading`/`point_two_heading`、`ASR_VALIDATION_UNCERTAIN`)。
  見出し冒頭の接続句("One Voice:"/"Another Voice:")がASR文字起こしで
  脱落する現象。実際の音声が誤読か、単なるASRの短い接続句取りこぼしかは
  未確認(音声を人間が試聴して判断する必要がある)。承認代行はしていない。
- **Open Item候補(新規登録は本タスクでは行わない、Fable/ユーザー判断
  待ち)**: B-Family A2新規topicのNarrator見出し("One Voice:"/"Another
  Voice:"という接続句を含む短い見出し文)で、ASRが接続句を脱落させ
  `ASR_VALIDATION_UNCERTAIN`になりやすい可能性(自由地N=1、再現性未確認。
  新規Voice/新規topicで今後同型の見出しを生成するたびに発生しうる
  構造的パターンかどうかは追加サンプルでの確認が必要)。
- Analytical Leakage Check残存flag(voice_a/voice_b、3attempt上限到達)
  は既存B1/3V仕様と同型のUSER_DECISION_REQUIRED候補として記録済み(9節)。
  同時解消(記事の追加is-hoc手直し等)は行っていない(委任文の禁止事項
  「Gate緩和」「Editorial原則の追加」に抵触しうるため)。
- 独立問題の同時解消: なし(発見した問題はいずれもuser decision待ちとして
  記録するにとどめた)。

## 21. 無変更証跡・事前指定外Read

`git status --porcelain er003_*.py er006_*.py er008_*.py er011_*.py
er005_*.py er013_*.py` = 変更なし確認済み(表示された`??`[未追跡]4件・
`M`[変更]の一部は並行タスク[`USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-05`]
由来であり本タスクでの変更ではない。本タスクによるsourceファイル変更は
`er012_*.py`3件[既存]+新規2件のみ)。

**並行タスクとの共有store競合について**: marker
`docs/pm/RESULT_PACKET_NEWS_2EP_RESUME3.md`の存在を確認後に音声stageを
開始した。ただし`git status`確認時点で共有store(`er006_output/master_
audio_store_01/manifest.json`等)に並行タスク[RESUME-05まで進行]由来の
未commit変更が既に存在していたため(python.exeプロセス非稼働を確認して
から実行、競合リスクを最小化)、これらの共有store file(manifest.json/
pronunciation_ledger_01/ledger.json/human_review_queue.jsonl等)は本
タスクのcommit対象に含めない(自分の変更と混在しており分離できないため、
無関係な差分を誤commitしないルールに従う)。

事前指定外Read(理由付き): `er014_output/four_type_observation_01/voices/
audio/b1_2v_v2/b1b/article.md`(確定英語タイトル・B1完成記事の位置確認
目的、Voice Card作成時は本文言を転記せずLedgerのみを根拠にした)、
`er003_key_words_canonicalization.py::merge_canonicalization_result`
(Key Phrase schemaのフィールド名確認、呼び出すだけで変更なし)、
`er006_audio_cost_pilot_02_shared_narration.py`全体(`ensure_all_shared_
narration_a2`のFIXED_ENGLISH_TEXTS内容確認、呼び出すだけで変更なし)、
`er011_human_review_lock_01.py::record_outcome`(Human Review Lock発火
条件の確認目的、変更なし)、`user_test/unified.html`(事前指定どおり、
`table.timeline`+`audio.main`/`audio[id*="episode"]`との互換性を確認、
本player.htmlの出力["Episode audio"見出し・`audio id="episode_audio"
class="main"`・`render_timeline_table`の`class="timeline"`]は互換と
確認、変更なし)。

★★★★報告ここまで★★★★
