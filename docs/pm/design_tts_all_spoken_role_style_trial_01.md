# design_tts_all_spoken_role_style_trial_01.md

管理ID: TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01(Trial、Production実装なし)
作成: 2026-09-28(Sonnet実行層)

## §1 Existing Spec / Prior Trial Check

### 1-1. 既存6-role(Production採用済み、Family Xのみ)
`er033_tts_flash_lite_family_x_styles_01.FAMILY_X_ROLE_STYLE_EN`:
TOPIC_INTRO / PREVIEW / COMMENT / FULL_STORY / HEADING_READOUT / IN_ONE_LINE の
6つ。`FAMILY_X_ROLE_STYLE_EN_FALLBACK = ["natural, clear, conversational", "clear"]`。
JA側はTrial未検証のまま既存`p9a.JAPANESE_STYLE_PREFIX`/minimal instructionを
そのまま流用する設計方針(モジュールdocstring)。

### 1-2. 既存shell segment(役割styleを一切持たない既知Gap)
`TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02_REPORT.md:725`
(Opus L2所見): 「Family X内のshell segment(welcome/preview_intro/
key_phrases_intro/full_story_intro/num_one〜five/point_explanation)だけが
role styleを一切持たない状態になっている(仕様未充足)」と明記済み。
実装確認(`er006_audio_cost_pilot_02_shared_narration.py:95-99`)でも、
Flash-Lite backend時は全shell EN segmentに単一の
`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`("natural, clear, conversational")が
一律適用されており、segment名ごとの区別は無い。JA shell(point_explanation)は
`voice01.generate_charon_japanese`自体に`style_prefix_override`が無いため
style自体は完全に無変更(`:119-130`のコメントで明記)。
→ 本Trialが埋める対象(Role漏れ)として確認済み。

### 1-3. 既存Advanced Key Phrase仕様の確認(二重実装回避のための必須確認)
コード実測(`er019_family_x_audio_production_runner_01.py`
`_generate_key_phrase_segments_b1`/`_generate_key_phrase_segments_a2`、
:633-657/:836-858)を確認した結果、**現行Productionでは Standard(A2)・
Advanced(B1B)のKey Phrase音声はいずれも「英語Key Phrase+日本語意味
(japanese_gloss_tts)」の同一構成であり、Advanced固有の英語解説トラックは
存在しない**(両者とも`n3_tts.resolve_key_phrase_ja_gloss_tts(item)`で
得た同じ`japanese_gloss_tts`を、B1Bは`generate_charon_japanese_with_reading_
safety`、A2は`generate_a2_japanese_with_reading_safety`へそのまま渡すのみ。
KP canonicalized schema実物(`hormuz__run_06_flashlite_full_kp/b1b/key_
phrases/keywords_canonicalized.json`)にも英語解説フィールドは存在しない
[`rank/source_span/source_sentence/display_phrase/key_phrase/used_form/
japanese_gloss/japanese_gloss_tts/...`のみ])。
過去Trial`KEY-PHRASE-LEVEL-SPEC-TRIAL-01`(er017、Standard=`explanation_ja`/
Advanced=`explanation_en`というLLM Prompt方式)は**REJECTED**(Trial Prompt v1、
狙いのPhrase再現率25%、`KEY-PHRASE-LEVEL-SPEC-TRIAL-01_REPORT.md`§12)であり、
Production未配線のまま。CURRENT_SPEC/OPEN_ITEMSにも本Trial以外でAdvanced
KP英語解説をFamily Xへ配線した記録は無い。
**結論**: 「Advanced=英語Key Phrase+英語での解説」という既存Production仕様・
既存テキストartifactは存在しない。二重実装ではなく、本Trialが最初に
`KEY_PHRASE_EXPLANATION_EN`というRoleを"定義"する。ただし本Trialは
「既存テキストartifactの再利用のみ、新規Key Phrase再選定・新規テキスト
生成はしない」という制約下にあるため、Hormuz run_06のKP itemには英語解説
テキスト自体が存在しない。**本Trialでは`KEY_PHRASE_EXPLANATION_EN`を
Role分類表には明記するが、実音声は生成しない(§9で新発見として報告、
Production新規実装の要否はユーザー判断)**。Advanced KPの実音声は、現行と
同じ「英語Key Phrase+日本語意味」構成のまま`KEY_PHRASE_JA`スタイルを
適用して比較する(Baselineとのコンテンツ差分は無し、style差分のみ)。

### 1-4. 過去Trial重複確認(role style/6-role/slowdown/日本語style)
`OPEN_ITEMS.md` OPEN-201に「role別styleはStage3の6-role最小案を初期仕様
採用」とあるのみで、全spoken要素への拡張Trialは過去に実施記録なし。
`A2_SLOWER_PACE_INSTRUCTION`/6% post-process(`apply_a2_slowdown_
postprocess`は`generate_a2_segment_with_slowdown`内に統合済み、runner側は
個別呼び出し不要)はER-008系で承認済み・無変更のまま利用する。

### 1-5. Master Audio Store(Trial隔離の必要性・方法)
`er006_master_audio_store_01.py`は`STORE_DIR`/`AUDIO_DIR`/`MANIFEST_PATH`/
`TELEMETRY_PATH`をモジュールレベル定数として保持し、`get_or_generate()`
内部で(パラメータではなく)これらのモジュールグローバル名をそのまま参照する
実装のため、**呼び出し時に動的に解決される**(defのbind時ではなく呼び出し時
のlookup)。よって`er006_master_audio_store_01.py`自体を編集せず、Trial
script側から実行時に`store.STORE_DIR = "<trial dir>"`等4定数を上書き
(モンキーパッチ)するだけでStoreを完全に分離できる(Production
`er006_output/master_audio_store_01/`は一切書き換えない)。

## §2 全spoken要素棚卸し + Role表

対象: `er019_family_x_audio_production_runner_01.generate_family_x_b1_
segments`/`generate_family_x_a2_segments`+`_generate_key_phrase_segments_
b1/a2`+`er006_audio_cost_pilot_02_shared_narration.ensure_all_shared_
narration_b1/a2`が生成する全segment(Hormuz run_06 baseline実データの
segment一覧で裏取り済み、b1b 12 segments+KP 5件×2+shared 9件、a2
13 segments+KP 5件×2+shared 10件)。

| segment_id | Level | Voice | 言語 | 既存生成関数 | Trial Role |
|---|---|---|---|---|---|
| welcome | 両方 | Charon | EN | shared_narration経由voice01.generate_charon_english | PROGRAM_SECTION_INTRO |
| preview_intro | 両方 | Charon | EN | 同上 | PROGRAM_SECTION_INTRO |
| key_phrases_intro | 両方 | Charon | EN | 同上 | KEY_PHRASE_INTRO |
| full_story_intro | 両方 | Charon | EN | 同上 | FULL_STORY_INTRO |
| num_one〜five | 両方 | Charon | EN | 同上 | NUMBER_LABEL |
| point_explanation | A2のみ | Charon | JA | shared_narration経由voice01.generate_charon_japanese | NUMBER_LABEL(JA) |
| topic_intro | B1B | Charon | EN | voice01.generate_charon_english | TOPIC_INTRO |
| topic_intro | A2 | Aoede | EN | crosslevel_common.generate_english_segment_with_fallback | TOPIC_INTRO |
| japanese_title | A2のみ | Aoede | JA | n3_tts.generate_a2_japanese_with_reading_safety | TITLE |
| preview | B1B | Charon | EN | voice01.generate_charon_english | PREVIEW |
| preview | A2 | Aoede | JA | n3_tts.generate_a2_japanese_with_reading_safety | PREVIEW(JA) |
| comment_1〜4 | B1B | Charon | EN | voice01.generate_charon_english | COMMENT |
| comment_1〜4 | A2 | Aoede | JA | n3_tts.generate_a2_japanese_with_reading_safety | COMMENT(JA) |
| full_story_part1 | B1B | Aoede | EN | news_tail_fix.generate_news_narration_wide_margin | FULL_STORY |
| full_story_part1 | A2 | Aoede | EN | n3_tts.generate_a2_segment_with_slowdown(6%内蔵) | FULL_STORY |
| full_story_part2/3_heading | 両方 | Aoede | EN | point_headings.generate / n3_tts.generate_a2_segment_with_slowdown | HEADING |
| full_story_part2/3(body) | 両方 | Aoede | EN | news_tail_fix.generate_news_narration_wide_margin / generate_a2_segment_with_slowdown | FULL_STORY |
| in_one_line | 両方 | Aoede | EN | 同上(FULL_STORYと同じ関数群) | IN_ONE_LINE |
| kp{rank}_english | 両方 | Aoede | EN | shared_narration.ensure_key_phrase_english_component→repro01.generate_key_phrase_component_verified | KEY_PHRASE_EN |
| kp{rank}_japanese(B1B)/meaning_{i}(A2) | 両方 | Charon(B1B)/Aoede(A2) | JA | n3_tts.generate_charon_japanese_with_reading_safety / generate_a2_japanese_with_reading_safety | KEY_PHRASE_JA |
| (未生成) | Advanced想定 | — | EN | 既存テキストartifact無し(§1-3) | KEY_PHRASE_EXPLANATION_EN(定義のみ、本Trialでは不使用) |

Role漏れ0確認: 上記表の右列(Trial Role)がProduction runner生成segment_id
全件を1:1以上でカバーしていることを、`er038_..._test_01.py`の
`test_role_coverage_no_gap()`で機械的に検証する(baseline
`tts_generation_results.json`のsegments/key_phrases/shared_narration
キー集合と、Trial側のRole割当tableのsegment_idキー集合を突合)。

## §3 Trial Role style表(EN/JA、短いdescriptor方針)

既存6-roleの文言は**据え置き**(変更しない)。追加分は「短く単純な
descriptor」という既存方針を踏襲し、各Roleの発話目的に対応する最小限の
表現とした(長い演技Promptは新設しない)。

| Role | EN style(style_prefix_override) | JA style(該当segmentのみ) | 既存/新規 |
|---|---|---|---|
| TOPIC_INTRO | "brief, clear, engaging news topic introduction" | – | 既存(無変更) |
| PREVIEW | "calm, conversational" | "落ち着いた、自然な話し言葉で" | EN既存/JA新規 |
| COMMENT | "calm, conversational" | "落ち着いた、自然な話し言葉で" | EN既存/JA新規(PREVIEWと同一、発話意図が同じため) |
| FULL_STORY | "calm, steady news narration" | – | 既存(無変更) |
| HEADING | "brief and clear" | – | 既存(無変更、HEADING_READOUTから改称、値は同一) |
| IN_ONE_LINE | "concise, clear" | – | 既存(無変更) |
| PROGRAM_SECTION_INTRO | "warm, brief, welcoming" | – | 新規 |
| KEY_PHRASE_INTRO | "brief, clear, inviting" | – | 新規 |
| FULL_STORY_INTRO | "brief, clear, transitional" | – | 新規 |
| NUMBER_LABEL | "brief, clear, neutral" | "簡潔に、はっきりと" | EN新規/JA新規(point_explanation用) |
| TITLE | – | "はっきりと、聞き取りやすく" | JA新規(A2のみ) |
| KEY_PHRASE_EN | "clear, precise, unhurried" | – | 新規 |
| KEY_PHRASE_JA | – | "はっきりと、落ち着いて" | JA新規 |
| KEY_PHRASE_EXPLANATION_EN | "clear, precise, explanatory" | – | 新規・定義のみ(§1-3、本Trialでは音声生成しない) |

JA styleは英語の直訳ではなく、同じ発話意図(calm/brief/clear等)を保った
自然な日本語表現にした(ユーザー指示どおり)。`assert_no_wpm_
specification()`を全EN/JA style文字列へ適用し、数値WPM指定が紛れ込んで
いないことを確認する(N-7是正と同じ安全網)。

Standard(A2)固有の速度調整: 本Trialでは`A2_SLOWER_PACE_INSTRUCTION`
(自然言語の「少し遅く」指示)を**一切連結しない**。6% time-stretch
post-processは`generate_a2_segment_with_slowdown`内に既に統合されており、
呼び出し側が個別に呼ぶ必要はないため、Trial側もstyle文字列を短いRole
styleのみにするだけで、既存の機械的減速はそのまま適用される
(post-process自体は無変更、"instruction"部分だけを取り除く実験)。
Advanced(B1B)側は元々slowdown対象外のため変更なし。

## §4 実装方式(既存パラメータの有無、最下層関数への委譲方針)

### 4-1. EN segment: 既存`style_prefix_override`パラメータをそのまま利用
`voice01.generate_charon_english`/`news_tail_fix.generate_news_narration_
wide_margin`/`point_headings.generate`/`crosslevel_common.generate_english_
segment_with_fallback`(=`repro01.generate_narration_snippet_verified_
strict`のエイリアス)/`n3_tts.generate_a2_segment_with_slowdown`はいずれも
`style_prefix_override`を既に持ち、EN分岐(`p9a.generate_narration_
snippet`:225)は`style_prefix_override or ENGLISH_STYLE_PREFIX`という
正しい上書き実装のため、**Trial scriptはこれらの既存Production関数を
無変更のまま呼ぶだけでよい**。KP英語(`shared_narration.ensure_key_
phrase_english_component`→`repro01.generate_key_phrase_component_
verified`)のみ、内部で`KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX`/
`KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION`を固定使用し`style_prefix_
override`を公開していないため、Trial側はこの関数を経由せず、共通の
`repro01.generate_narration_snippet_verified_strict(text, "en", out_path,
expected_substring, style_prefix_override=<KEY_PHRASE_EN style>,
disfluency_qa=True, tts_backend=tts_backend)`を直接呼ぶ(§4記載どおり
「既存パラメータが無い関数はその旨を記録し、最下層のTTS call関数を同じ
引数で呼ぶ」を適用。同一の検証済み共有関数であり、二重実装ではない)。

### 4-2. JA segment: 既存パラメータの有無を実測確認した結果と対応
- `voice01.generate_charon_japanese`(B1B KP JA/point_explanation経由)は
  `style_prefix_override`パラメータ自体が存在しない
  (`flw.resolve_tts_call_and_prompt(text, p9a.JAPANESE_STYLE_PREFIX, ...)`
  とハードコード、`:465-467`)。
- `repro01.generate_narration_snippet_verified_strict`は
  `style_prefix_override`パラメータを**持つ**が、内部で呼ぶ
  `p9a.generate_narration_snippet`が`language=="ja"`の場合に
  `style_prefix_override`を一切参照せず`JAPANESE_STYLE_PREFIX`固定
  (`er003_b1_p9a_audio.py:227-229`)という**dead parameter**であることを
  実測確認した(A2のJA呼び出し元[`generate_a2_japanese_with_fallback`]も
  この関数へ`style_prefix_override`自体を渡していない)。
- したがってJA側は「既存パラメータが無い(または機能しない)関数」に該当
  するため、委任文の指示どおり**最下層のTTS call関数
  (`er033_tts_flash_lite_backend_wiring_01.resolve_tts_call_and_prompt`)を
  同じ引数(text, style_prefix, model_name, voice_name, out_path,
  tts_backend, build_tts_prompt, make_batch_tts_call_fn)で直接呼ぶ**。
  Trial script内`_generate_ja_role_style()`が、
  (1) 既存の発音・記号・placeholder安全処理
  (`safety.detect_gloss_placeholder_notation`/`detect_prohibited_symbols`/
  `pron_resolver_core.resolve_unknown_ja_tokens`/
  `safety.classify_foreign_tokens_in_japanese_text`/
  `safety.to_tts_safe_japanese_fraction_reading`、
  `generate_charon_japanese_with_reading_safety`/`generate_a2_japanese_
  with_reading_safety`が呼ぶのと同一の共有関数)をそのまま呼び出し、
  (2) 標準経路(最大`review_lock.PRODUCTION_STANDARD_TTS_ATTEMPTS`=2回、
  ASR検証は`routing.transcribe`+`ja_secondary.evaluate_attempt_ja_with_
  cascade`という既存Production Cascadeをそのまま使用)、
  (3) fallback経路(既存の無変更Production関数
  `voice01.generate_charon_japanese_minimal_instruction`[Charon]/
  `n3_tts._generate_a2_japanese_minimal_instruction`[Aoede]を**そのまま
  再利用**、minimal instructionのテキスト自体は一切変更しない)、
  という構造で、既存関数`generate_charon_japanese`/`generate_a2_japanese_
  with_fallback`の標準+fallback 3回上限(`PRODUCTION_MAX_TTS_ATTEMPTS`)
  という契約をそのまま踏襲する。既知の簡略化(Trial限定、Production挙動
  自体は無変更): `@review_lock.guarded_generate`デコレータ(Human Review
  Lock状態ファイルへの記録)と`review_lock.save_tts_attempt_audio`
  (attempt別音声の個別保存)は適用しない(Trialは独立out-dir/Storeで
  完結し、Production Lock状態[`audit/review_lock_state.json`等]を一切
  読み書きしないため、Lock機構自体への影響はゼロ)。

### 4-3. Master Audio Store隔離
`er038_output/tts_all_spoken_role_style_trial_01/trial_master_audio_
store/`へ`store.STORE_DIR`等4定数をTTS実行直前にモンキーパッチする
(§1-5)。Production Store(`er006_output/master_audio_store_01/`)は
一切書き込まない(`git diff`で確認、§8参照)。

### 4-4. Assembly
`er019_family_x_audio_production_runner_01.stage_assemble_family_x_b1/a2`
を無変更のままTrial out-dirに対して直接呼ぶ(既存の`load_family_x_b1/a2_
sources`が期待するファイル名規約[`welcome_charon.wav`等]・
`audit/tts_generation_results.json`のsegments/key_phrases/shared_
narrationスキーマ・`verify_episode_audio_validation_gate`(status==
"OK"→"VALIDATED"通過)・`_assert_shared_narration_ok`をすべて満たす形で
Trial側の生成結果を書き出す)。既存のAudio Validation Gate・disfluency QA
必須segment判定・A2 slowdown必須判定は迂回しない(同一の下位生成関数を
呼ぶことで自然に満たされる)。

## §5 コスト・実行計画
1記事(Hormuz)×Standard(A2)/Advanced(B1B)×全spoken segment、既存テキスト
artifact再利用(記事生成・Key Phrase再選定なし)。実行順: b1b→a2、各
`--budget-jpy 22`(合計Guardrail ¥45以内、実測前例1レベル約¥10.8を参考)。
