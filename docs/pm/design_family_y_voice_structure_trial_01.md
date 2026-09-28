# FAMILY-Y-VOICE-STRUCTURE-TRIAL-01 設計書

管理ID: FAMILY-Y-VOICE-STRUCTURE-TRIAL-01(ユーザー承認済みTrial、Production配線なし)。

## §1 Existing Spec Check(実装着手前の必須確認)

### 分類

- 分類A(Family Xに同等の正式名称が既にある。Family Y専用の別名称は作らず統一): (1) News全体から本質的Factのみ抽出、(2) Writerへ渡すFact数を絞る仕組み。
- 分類B(Family Xに存在するが英語Voiceへの「そのまま適用」に制約があり、解釈判断が必要): R1→R2 Entertainment性向上Revision。
- 分類C(Family Xに該当なし、Family B[legacy read-only]に既存Voice QA機構あり、流用): Voice重複チェック(diversity/leakage)。

### Family X正式名称 → 本Trialでの使用箇所(対応表)

| Family X正式名称 | 出典 | 本Trialでの使用 |
|---|---|---|
| Storyline決定+B3 Fact選定(LLM 1 call、Selected Fact Brief) | `er019_family_x_storyline_b3_fact_selection_01.py::run_storyline_b3_selection()`。B3の4テスト(`FACT_TEST_DEFINITIONS_JA`)・JSON schema(`STORYLINE_B3_JSON_SCHEMA`)・目安3〜5件(6件以上はrecheck_note必須)は逐語・無変更でimport使用 | Trial Step 1(Fact Selection)。**入力データ形式の橋渡し**: Family Xの`extract_fact_ids_from_ledger()`は`^\[VERIFIED\]\s+fact_id:`形式の行を前提とするが、本Trialの入力Fact材料(`er012_output/ai_screening_ledger_trial_01/research/verified_fact_ledger.txt`、Family B 3V/4V Trial用Verified Fact Ledger)は`[VOICE_N_EVIDENCE] N-NN(fact_id): ...`形式であり、タグ語彙・fact_id位置が異なる。B3関数自体・Prompt・schemaは無変更のまま、**入力ledger_textをFamily X期待形式へ変換するアダプタのみ**をTrialスクリプト内に実装する(Family B既存関数`build_ledger_fragment_visible_voices_only(ledger_text, num_visible_voices=3)`[`er012_b_family_voices_writer_generic_01.py`、無変更import]でVoice 4分を除外した後、CONFIRMED各factを`[VERIFIED] {fact_id}: {text}`行へ変換する)。これはFamily Xのスクリプト/Prompt/処理自体の変更ではなく、別Trialの生データを既存関数の入力契約に合わせるデータ整形である。 |

### R1→R2 Entertainment性向上Revision(分類B、判断が必要だった点)

- Family Xの唯一のR1→R2実装は`er019_family_x_ja_writer_o_r1_r2_01.py`(日本語Entertainment読み物専用)。`REVISION_INSTRUCTIONS = {"r1": "この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。", "r2": "この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。"}`(逐語日本語文)と、`call_fresh()`/`call_with_previous_response_id()`(`previous_response_id`連鎖、model=`WRITER_MODEL`)が中核。英語本文向けのR1→R2実装はCURRENT_SPEC.md上に存在しない(English側は「Advanced=Natural English Adaptation」「Standard=6,000語Band簡略化」であり、いずれもR1→R2型のEntertainment revisionではない)。
- 同ファイルの`run_ja_writer_o_r1_r2()`本体は、R1→R2の周囲にJA専用のFact Check(`vfl01.run_deviation_check()`、JA Full Ledgerとの逐語照合)・JA専用の音声化禁止記号チェックを同居させており、これらは英語Voice本文には意味的に適用不能(JA Full Ledger形式必須・JA専用記号)。
- **判断(Fable/ユーザー確認事項として明記)**: 「そのまま適用できるか」を、(a) 中核のRevision指示文言+previous_response_id連鎖の呼び出し関数、と(b) 周辺のJA専用Fact Check/記号チェック、に分けて評価した。(a)はテキスト・呼び出し方式ともに言語非依存であり、英語記事に対してこの逐語日本語指示文をそのまま2ターン適用することは技術的に可能(モデルは多言語指示追従可能)であり、Family Xのスクリプト・Prompt・処理を「そのまま使う」という指示に文字通り合致する。(b)はJA専用の安全機構であり、本Trialでは適用対象外(そもそもJA Full Ledgerを持たず、TTSも行わないため音声化禁止記号チェックも無関係)。
- 採用: `REVISION_INSTRUCTIONS["r1"]`/`["r2"]`(逐語)と`call_fresh`/`call_with_previous_response_id`(無変更import)のみを再利用し、JA専用Fact/記号チェックは適用しない。STOPはしていない(完全な流用不能ではなく、部分的に言語非依存な中核部分を特定できたため)。**この解釈はSonnetの判断であり、Fable/ユーザーによる確認が必要な点として報告する**(RESULT_PACKET参照)。

### Family B(Voices)既存Voice重複/leakage対策(分類C、流用)

- `er012_b_voices_3v_a2_user_test_01.py::run_structure_check_3v()`のコメントにより、2V専用`run_analytical_leakage_check`(voice_a/voice_b固定key)は3V(6見出し)には非適用であることが明記されている。
- しかし別モジュール`er012_b_family_voices_writer_generic_01.py`(Production、read-only import)に、Voice数非依存の汎用3V版が実装済み:
  - `run_overlap_monitoring_3v(sections, out_dir)`: 有向Voiceペア6通り(Permutation)+ vs Hook 3の lexical overlap/paraphrase検知(`er008_point_overlap_qa_18.flag_possible_paraphrase`、Production関数、monitoring専用でgateではない)。
  - `run_analytical_leakage_check_3v(client, sections, model, reasoning_effort, out_dir, attempt, external_constraint_enabled)`: LLM 1 callで各Voiceに7項目(`leak_evidence_subject`/`leak_numbers_foreground`/`leak_narrator_analysis`/`leak_unknowable_analysis`/`leak_discovery_syntax`/`leak_evidence_memorable`/`leak_position_blur`)、Tensionに6項目(`leak_binary_camp_split`含む)、Closingに1項目(`leak_closing_simple_summary`)を判定。`leak_position_blur`(2026-09-17ユーザー正式承認、B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01)は「あるVoiceが他Voiceの中心的懸念・反論を自分の主張として代弁していないか」を判定するcross-voice項目であり、まさに今回確認したい「同じ懸念/同じ結論への収斂」に直接対応する。
  - この7項目のうち`leak_evidence_subject`/`leak_numbers_foreground`/`leak_discovery_syntax`/`leak_evidence_memorable`は課題1(Fact言い直し)に、`leak_narrator_analysis`/`leak_unknowable_analysis`は課題4(記事解説に聞こえる)に、`leak_closing_simple_summary`/`leak_tension_reverts_to_research`は課題3(抽象論化)に、それぞれ既存の判定基準として直接対応する。
  - 実データ実績: `er012_output/b_family_voices_position_spec01_offline_reeval_01/analytical_leakage_check_3v_attemptreeval_ai_hiring_3v_a2.json`に、本Trial対象記事(ai_hiring 3V A2)そのものへの適用実績があり(voice_2/voice_3/tensionでFAIL項目あり)、既存Before記事の弱点が既にこの機構で機械的に検出されていたことを確認した。
- **採用**: `run_overlap_monitoring_3v`・`run_analytical_leakage_check_3v`を無変更でimportし、Before/R1/R2の3時点で実行する(Before記事は`article.md`のsections dictをそのまま入力できるため追加コストなしで評価可能)。新規の重複実装は行わない。

## §2 前段(Fact Selection→Voice Fact Assignment→Angle/Stakeholder)設計

- Step 1 Fact Selection: 上記アダプタ経由でFamily X `run_storyline_b3_selection()`をそのまま呼び出す(topic=`TOPIC_JA_3V`、`er012_b_voices_3v_a2_user_test_01.py`より逐語転記、新規テーマ選定はしていない)。出力Selected Fact Brief(目安3〜5件、Family X既定値をそのまま採用)。
- Step 2 Voice Fact Assignment + Angle/Stakeholder(新規、本Trial固有、LLM 1 call、構造化JSON): 入力=Selected Fact Brief+3 Voiceのstakeholder候補(Applicant/Recruiter・Hiring Manager/Business Owner、既存Before記事・ledgerの表記を踏襲)。出力: 各Voiceの`fact_ids`(1件、必要な場合のみ最大2件)・`stakeholder`・`angle`(1〜2文)。全Voice同一fact_ids集合を禁止(test対象)。
- Step 3 Voice Writer(新規、本Trial固有、LLM 1 call): Family B `a2prod.A2_KAI1_INSTRUCTION_PARA1_PARA3`・`a2prod.CORE_EXPLANATORY_LOGIC_PRESERVATION`(既存Production言語原則、逐語引用・無変更)を土台に、以下の方針文(禁止語リストではない)を追加: 「Fact is context, not script」「According to.../The study found.../The company said...のようなFact紹介文から書き始めない」「各Voiceは最後まで具体的なStakeholder/状況を保つ」。出力Markdown構造はFamily B `b1prod.split_six_voice_sections()`が要求する6見出し構造(`# Title`→`## Hook`→`### Voice1`→`### Voice2`→`### Voice3`→`## Tension`→`## Closing`)に厳密準拠(既存Before記事と同一構造、パース関数を無変更で共有利用するため)。

## §3 R1→R2(Family X既存処理の適用)

Voice Writerの初回応答(response_id)を起点に、`call_with_previous_response_id(client, REVISION_INSTRUCTIONS["r1"], effort, prev_id, stage="r1")`→`call_with_previous_response_id(..., REVISION_INSTRUCTIONS["r2"], ..., stage="r2")`をそのまま連鎖実行する(Family X Original→R1→R2と同じ連鎖方式)。JA専用Fact Check/記号チェックは適用しない(§1参照)。

## §4 評価設計

8確認項目それぞれについて、(a) 決定論的指標: Fact紹介型冒頭文の検出器(正規表現、"According to"/"The study found"/"The company said"/"A survey found"/"X% of..."等の冒頭パターン)、Voice間fact_ids重複(Step 2出力から直接算出)、抽象語(society/trust/the future/technology in general等)の出現位置(前半/後半、参考指標)、語数、(b) Family B既存`run_analytical_leakage_check_3v`/`run_overlap_monitoring_3v`(Before/R1/R2)、(c) 追加のLLM評価1 call(rubric: 4課題×Before/R1/R2、1〜5点+根拠引用)。判定案(REJECTED/VALIDATED/USER_DECISION_REQUIRED)はBefore→R1→R2比較で提示するのみとし、Sonnetは`VALIDATED`を自己宣言しない。

## §5 費用抑制の運用判断(Trial限定)

Production既定の`reasoning_effort="high"`は、Trial予算(¥40、Guardrail)の範囲内に収めるため、本Trial固有の新規呼び出し(Voice Fact Assignment/Voice Writer/LLM評価)では`medium`を使用する(Family X既存関数[B3 Fact Selection/R1/R2呼び出し]へ渡すeffort値も同様に`medium`を明示指定。関数・Prompt自体は無変更、呼び出し時引数のみのTrial限定判断)。
