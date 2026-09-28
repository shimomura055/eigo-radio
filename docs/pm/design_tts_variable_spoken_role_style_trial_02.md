# design_tts_variable_spoken_role_style_trial_02.md

管理ID: TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02(Trial、Production実装なし)
作成: 2026-09-28(Sonnet実行層)

## §1 Existing Spec確認(重要な発見を含む)

### 1-1. EN側(B1B FULL_STORY/IN_ONE_LINE/TOPIC_INTRO): delegation想定どおり
`er033_tts_flash_lite_family_x_styles_01.FAMILY_X_ROLE_STYLE_EN`(Production定数、
無変更)が実際に`er019_family_x_audio_production_runner_01.generate_family_x_b1_
segments`内`_role_style()`経由で`tts_backend=="speech_metadata_flash_lite"`時に
無条件適用されていることをコード実測確認した(:491-497,532)。
`FULL_STORY="calm, steady news narration"`/`IN_ONE_LINE="concise, clear"`/
`TOPIC_INTRO="brief, clear, engaging news topic introduction"`。
`er038_tts_all_spoken_role_style_trial_01.TRIAL_ROLE_STYLE_EN`は同じ値をそのまま
転記しており、E0のreuse元として使える(§4-1)。

`speech_metadata_flash_lite`backend時、最終的にTTSへ渡る文字列は
`er033_tts_flash_lite_backend_wiring_01.resolve_tts_call_and_prompt`が
`prompt = (text, style_prefix)`をそのまま`types.SpeechMetadata(style=style)`へ渡す
実装(:187-191,406)であり、**Production側で追加の接頭・接尾・fallback文言の連結は
一切ない**(EN側`p9a.generate_narration_snippet`のen分岐も
`style_prefix_override or ENGLISH_STYLE_PREFIX`のみ、:224-225)。ただし
`enable_pronunciation_resolver=True`時は`er025_entity_pronunciation_resolver_
core_01.resolve_and_augment_en_style_prefix()`が固有名詞発音ヒントをstyleへ
条件付き追加しうる(Ledgerに該当entryがある場合のみ)。Hormuz記事の既存B1B
baseline実測(`er038_output/.../hormuz/b1b/audit/tts_generation_results.json`)では
全segment`en_pronunciation_resolver_info.hints_applied=false`であり、本Trialの
対象記事・対象segmentでは発生しないことを実測確認済み。したがって**E0〜E3の
「実際にTTSへ渡したStyle Prompt全文」は、本設計書に記載するstyle文字列そのもの
(接頭・接尾なし)である**。本Trial実行後、各生成結果の`en_pronunciation_
resolver_info.hints_applied`を必ず確認し、trueの場合は例外としてページに
明記する。

### 1-2. JA側(A2 preview/comment_1〜4): delegation想定と実際のProductionが乖離(重要な発見)
delegation文は「J0=現状『落ち着いた、自然な話し言葉で』」としているが、これは
`TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01`(Task B、er038)がTrial内で**新規に導入した**
JA style値であり(同Trial設計書§3で「EN既存/JA新規」と明記)、**現行Production
には一切配線されていない**ことをコード実測で確認した。

実測根拠(`er019_family_x_audio_production_runner_01.generate_family_x_a2_
segments`, :685-688コメント原文): 「JA segment(japanese_title/preview/
comment_1-4)は既存`generate_a2_japanese_with_reading_safety`が
`style_prefix_override`自体を持たないため無変更(既存`JAPANESE_STYLE_PREFIX`/
minimal instructionテキストをそのまま流用)」。関数シグネチャ実測
(`er003_v1_n3_01_tts_generate.py:582`)でも`style_prefix_override`引数は存在
しない。呼び出し先`c.generate_narration_snippet_verified_strict(text, "ja", ...)`
(`crosslevel_common`経由、実体`er003_v1_repro01_main_generate`)はja分岐で
`p9a.generate_narration_snippet`へ委譲し、そちらも`language=="ja"`時は
`style_prefix_override`を一切参照せず`JAPANESE_STYLE_PREFIX`固定
(`er003_b1_p9a_audio.py:227-229`、Task B design doc§4-2で既出のdead
parameter確認と同型)。

**すなわち、現行Production JAは「role別style」自体が存在せず、tts_backendに
関わらず常に単一の長文instruction(`p9a.JAPANESE_STYLE_PREFIX` =
`er003_b1_p3y_audio.build_japanese_style_prefix()`が返す
`COMMON_BASE_INSTRUCTION`+`LEVEL2_INSTRUCTION`合成文字列、実測全文は§2参照)が
適用される。** この文字列は「落ち着いた、自然な話し言葉で」とは正反対に、
「Give the narration a noticeably animated, emotionally present, and expressive
delivery. Use a clearly wider vocal range, stronger emphasis...」という、既に
かなり表情豊かな方向の長大な指示である(全文§2)。

**対応方針**: J0を「Production/Task Bで実際に渡している文言」の**Production側**
(真の現状)に訂正し、この長文instructionの全文をJ0のStyle Prompt欄へそのまま
表示する(delegationの「省略表記禁止」要件を満たすには、真の現状を正確に表示する
必要があるため)。J1〜J3はTask Bが導入した短い方向性(「落ち着いた自然な話し言葉を
維持しつつ、意味・流れ・強調点・転換に応じて自然な抑揚」)を新規Role Styleとして
比較する(delegationのユーザー意図=「短くシンプルな新style候補の比較」自体は
達成できる。単に「J0=現状」の値をユーザー記憶ではなく実測値に訂正するのみ)。
本件はOPEN候補として報告する(§9)。

### 1-3. JA J0音声のreuse可否(Fable指示「一致しなければ新規生成し理由記録」の適用)
`er038_output/.../hormuz/a2/`のTrial音声はJA新規style(「落ち着いた、自然な
話し言葉で」)を使っており、真のProduction styleとは一致しないため、reuse対象
としない(理由記録済み、上記§1-2)。

代わりに、**真にProduction同一コードパス(style override無し)で生成された
既存verified音声**を実測発見した: `er019_output/family_x_audio_production_
wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp/a2/
narration/{preview,comment_1,comment_2}.wav`(`tts_generation_results.json`実測:
`tts_backend="speech_metadata_flash_lite"`、`model="gemini-3.8-flash-lite-tts"`、
`asr_verified=true`、`canonical_text`が現在の`a2_support_texts.json`と完全一致)。
このrunは`er038`自身が`--source-run`として採用している記事textの一次ソースで
あり(Task B design doc§1-5と同一run)、A2 JAのstyle override機構自体が
Production/このrunとも存在しないため、生成コードパスは実質的に同一
(=真の現状音声として使ってよい)。本Trialでは、これら3ファイルをJ0としてread-only
コピー再利用する(このソースディレクトリ自体は書き込まない)。

## §2 JAPANESE_STYLE_PREFIX全文(J0のStyle Prompt欄にそのまま表示する)

```
次の文章を、翻訳・言い換えせず、日本語のまま読み上げてください。

Speak directly to one interested listener rather than announcing to a large crowd.

Create a natural emotional arc that follows the meaning already present in the script. Let the energy, weight, and pace rise or fall when the story itself changes. Do not add excitement, sadness, urgency, or drama that is not supported by the words.

Carry the meaning naturally across sentence boundaries. Do not reset your pitch, energy, or rhythm after every sentence. Group related sentences into complete thoughts, while keeping important contrasts and turning points clear.

Treat the narration as one continuous program, even when it is generated in separate sections.

Read every title, section heading, and subsection heading exactly as written. Never skip, paraphrase, shorten, or silently absorb a heading into the following text.

Do not shout, sound like a movie trailer, become gloomy or sleepy, or use a distant and overly formal newsreader style.

Give the narration a noticeably animated, emotionally present, and expressive delivery.

Use a clearly wider vocal range, stronger emphasis on important words and turning points, and more distinct rises and falls in energy.

Make the listener feel that the story matters and that you genuinely want them to keep listening.

Keep the narration moving with confident momentum, including during explanatory passages. Avoid becoming passive, flat, or overly restrained.

Allow the most important moments, contrasts, and conclusions to land with clear emotional impact.

Use stronger expression than Level 1, but vary the intensity across the story. Do not stay at maximum intensity throughout.

Do not shout, force emotion, exaggerate feelings that are not present in the script, or sound like a sports commentator or movie trailer.
```
(実測値、`er003_b1_p9a_audio.JAPANESE_STYLE_PREFIX` 2026-09-28時点、`repr()`で確認)

## §3 対象segment棚卸し

| # | 言語 | Level | segment_id | 必須/任意 | 理由 |
|---|---|---|---|---|---|
| 1 | JA | A2(Standard) | preview | 必須 | delegation必須指定 |
| 2 | JA | A2 | comment_1 | 必須 | delegation必須指定 |
| 3 | JA | A2 | comment_2 | 必須 | delegation必須指定 |
| 4 | JA | A2 | comment_3 | 任意(予算余裕時) | 比較充実 |
| 5 | JA | A2 | comment_4 | 任意(予算余裕時) | 比較充実 |
| 6 | EN | B1B(Advanced) | full_story_part1 | 必須 | delegation必須指定(最短part) |
| 7 | EN | B1B | in_one_line | 必須 | delegation必須指定 |
| 8 | EN | B1B | topic_intro | 任意(予算余裕時) | Existing Specで可変EN segmentと確認(§1-1) |

除外(固定phrase、Master対象): welcome/preview_intro/key_phrases_intro/
full_story_intro/num_one〜five/point_explanation(Task 2専用、本Trial対象外)。
除外(Key Phrase系): kp_english/kp_japanese/meaning_*(Key Phrase EN/JA解説は
Task 1専用、本Trial対象外)。除外(コスト抑制): full_story_part2/part3
(body2=600字/body3=329字、part1=669字と同等以上に長く、delegation「part2/3は
費用余裕がある場合のみ」に該当。今回は必須2segment+任意3segmentで比較目的を
十分満たすため見送り、理由記録)。japanese_title/point_explanationはJA対象棚卸し
外(A2固有shell/title、preview/commentの基本方針統一というユーザー指示の対象外)。

Standardの6%減速post-process(`generate_a2_segment_with_slowdown`)はJA
segment(preview/comment)には適用されない(A2側の6%減速はEN本文segmentのみ、
JA generatorは別関数`generate_a2_japanese_with_reading_safety`)。よってJ0〜J3
生成にpost-process差異は無い。EN側(full_story_part1/in_one_line)はB1Bのため
slowdown対象外(§1-2 Task B design doc既出のとおり)。

## §4 Pattern文言(全文、短くシンプル)

### 4-1 JA(J0〜J3)
- J0(現状、Production実測): §2の全文(長文instruction、既存Production
  そのまま、無変更)。
- J1(軽い抑揚): 「落ち着いた、自然な話し言葉で。意味の流れに合わせて軽く抑揚を
  つけてください。」
- J2(中程度の抑揚): 「落ち着いた、自然な話し言葉で。強調点や話の転換に応じて
  抑揚をつけてください。大げさにしないでください。」
- J3(J2より少し表情豊か): 「落ち着いた、自然な話し言葉で。意味の流れ・強調点・
  転換に応じて表情豊かに抑揚をつけてください。演技がかった話し方は避けて
  ください。」

J1〜J3はいずれも`common.assert_no_wpm_specification()`を通過済み(数値WPM
指定なし)。

### 4-2 EN FULL_STORY(E0〜E3)
- E0(現状、Production実測): "calm, steady news narration"(無変更)。
- E1(軽い自然な抑揚): "calm, steady news narration, with a touch of natural
  inflection that follows the meaning."
- E2(中程度の抑揚): "calm, steady news narration with natural emphasis at key
  points and turns; not dramatic."
- E3(E2より少し表情豊か): "calm, steady news narration, naturally expressive at
  key points, contrasts, and the conclusion; understated, not theatrical."

### 4-3 EN IN_ONE_LINE(E0〜E3)
- E0(現状、Production実測): "concise, clear"(無変更)。
- E1: "concise, clear, with a natural closing tone."
- E2: "concise, clear, landing naturally as a settled conclusion; not flat, not
  dramatic."
- E3: "concise, clear, with a slightly more expressive, confident closing
  landing; understated, not theatrical."

### 4-4 EN TOPIC_INTRO(E0〜E3、任意)
- E0(現状、Production実測): "brief, clear, engaging news topic introduction"
  (無変更)。
- E1: "brief, clear, engaging news topic introduction, with a touch of natural
  lift."
- E2: "brief, clear, engaging news topic introduction with natural emphasis on
  the topic; not dramatic."
- E3: "brief, clear, engaging news topic introduction, naturally expressive but
  understated; not theatrical, not a trailer voice."

全EN style文字列も`assert_no_wpm_specification()`を通過済み。

## §5 実装方式

`er044_tts_variable_spoken_role_style_trial_02.py`は新規scriptとして、
`er038_tts_all_spoken_role_style_trial_01`(以下t01、import・読み取りのみ、
無変更)の既存関数を再利用する。

- JA生成: `t01.generate_ja_role_style(text, out_path, style, "Aoede",
  n3_tts._generate_a2_japanese_minimal_instruction, tts_backend,
  max_extra_chars=40)`をそのまま呼ぶ(t01が既に実装済みの、標準
  `standard_attempts`回+fallback(既存`_generate_a2_japanese_minimal_
  instruction`、無変更)という`PRODUCTION_MAX_TTS_ATTEMPTS=3`上限構造を継承)。
  J0はTTS生成せず、§1-3のread-only reuseのみ(コピー+sha256記録)。
- EN FULL_STORY/TOPIC_INTRO生成: `voice01.generate_charon_english`
  (topic_intro)/`news_tail_fix.generate_news_narration_wide_margin`
  (full_story_part1)を、`style_prefix_override=<pattern style>`,
  `enable_pronunciation_resolver=True`(Production実挙動と揃える),
  `tts_backend="speech_metadata_flash_lite"`で直接呼ぶ(Production runnerの
  呼び出し引数と同一、既存の`style_prefix_override`パラメータが機能するため
  Task B design doc§4-1と同じく既存関数をそのまま利用)。E0はt01の既存
  b1b出力(`er038_output/.../hormuz/b1b/narration/{full_story_part1,
  in_one_line}.wav`、style値が一致確認済み§1-1)をread-onlyコピー再利用。
- Master Audio Store: `t01.trial_master_audio_store()`を本Trial専用の
  `er044_output/tts_variable_spoken_role_style_trial_02/master_store/`へ向けて
  使う(Production Store `er006_output/master_audio_store_01/`は不使用、
  読み書き一切なし)。
- `--stage all`/`run_tts_stage`全体は一切呼ばない。本scriptはsegment×pattern
  単位の直接関数呼び出しのみを提供し、CLIは`--patterns`/`--segments`で対象を
  明示指定した部分実行のみ受け付ける(全件一括実行フラグは実装しない)。

## §6 実行計画(Guardrail、実行前にACTIVE_TASK_VR2へ記録)

必須segment 5件(JA 3×J1-J3=9新規、EN 2×E1-E3=6新規、E0/J0はreuseで¥0)=
新規TTS呼び出し想定15回(標準attempt上限2回+fallback1回=segment当たり最大3回、
理論上限45回)。任意segment追加時(comment_3/4×J1-J3=6、topic_intro×E1-E3=3)は
+9新規(理論上限+27回)。ASR(OpenAI/Google)はTTS成功ごとに1回。

想定費用: Task Bの実測単価(b1b¥9.57/19segment≈¥0.50、a2¥13.84/約20segment≈
¥0.69)を参考に、必須15segment×¥0.7想定+retry余裕で¥15前後、任意9segment追加で
+¥7前後。合計想定¥25前後、Guardrail上限¥60に対し十分な余裕(delegation
budget-jpy 60)。

Guardrail: 各バッチ実行後に`fx_runner.compute_cost_jpy_so_far`相当で累計を確認し、
¥60接近時は残segmentを打ち切り理由記録。異常retry(同一segmentがFallbackも含め
3回全滅=Human Review Lock到達)はOPEN-222と同型の既知非決定的挙動として記録し、
独自の上限拡張はしない。
