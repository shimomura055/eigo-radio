# FAMILY-Z-STYLE-ACTUAL-GATE-01 IMPLEMENTATION_01

管理ID: FAMILY-Z-STYLE-ACTUAL-GATE-01 委任_01 / 2026-10-27。到達=IMPLEMENTED(正式経路mock確認)。API 0、JPY 0。設計=DESIGN_01.md。

## 変更ファイル
| ファイル | 変更 |
|---|---|
| `er063_family_z_audio_01.py` | (1)`build_entry`に`entry["style_actual"]=build_style_actual_record(spec,result)`(additive)。(2)`run_tts_stage`で新規level開始時のみ`write_style_actual_marker_if_fresh`(マーカー`audit/style_actual_gate.json`)。(3)`run_audio_gate`がM2/M1/品質確認の後・共有Gateの前に`z_style_actual_gate`を呼ぶ(BLOCK=`FamilyZStyleActualGateStop`)。gate結果JSONへ`style_actual_gate`要約を追記。(4)新節「8-S」: `Z_ROLE_COVERAGE`/`Z_ROLE_ANY_OF`/`build_style_actual_record`/`z_style_actual_gate`/`_z_row_for_clip`/`FamilyZStyleActualGateStop`。 |
| `er063_family_z_style_actual_gate_test_01.py`(新規) | 31 test(下記) |
| `er063_family_z_audio_01_test_01.py` `fake_generators` / `er117_z_chunk_wiring_test_01.py` `Gens` / `er026_family_z_fiction_production_runner_01.py` `mock_tts_generators` | 不整合fixture是正: `style_prefix.sha256="ab"*32`(承認Styleと無関係)→そのroleの承認Styleを送った記録。Dialogueはleafが送信prefixを返さないため記録なし。本番コード経路の変更ではなくmock(`mock_tts_generators`は`--mode mock`専用)のみ |
- 非変更: `er019_family_x_style_profile_01.py`、`er121`(Y)、`er003_v1_*`(leaf)、`er012`、`er127`、`er062`、過去run dir、公開ページ。Style文面/Prompt/Voice/回数、reuse_key不変。

## 実測記録(`entry["style_actual"]`)
`{schema, role_key, kind(measured|unmeasured), source(adopted_attempt.style_prefix|result.style_prefix|null), sha256, len, head200, form(full_text|record), hint_applied, adopted_phase, adopted_instruction_type, result_fallback_used, expected_sha256, [startswith_expected], [secondary_top_level]}`。実leafの戻り値のみ使用(新規LLM/TTS呼出なし)。leaf別の取得元(Grepで確認した事実):
- Adv narrator: `er003_v1_sing01_news_tail_fix.py:364,399` top-level `style_prefix`(str、hint追記後の全文、③minimal時はminimal側の値)。
- Adv preview/comment/topic_intro(Charon英語): `er003_v1_sing01_voice01_generate.py:369,395` top-level `style_prefix`(str)。
- Std narrator/KP_EN/topic_intro(Std): repro01系`style_prefix_record`(dict sha/len/head200)をattempts_logに保持(`er003_v1_repro01_main_generate.py:443,664`)。
- 日本語(Std preview/comment/title、KP_JA): top-level `style_prefix`(str、`p9a.generate_narration_snippet`が`style_prefix_override`時に実値を返す。`er003_b1_p9a_audio.py:299`、Yのaudit実データでstr確認[`er121_output/…/run_style_fix_01/a2` comment_1・kp japanese_meaning])。
- Dialogue: leafは送信prefixを返さない(`er012:525-560`)→ 実測なし(DESIGN 2-2)。

## test(31件、すべてPASS)
- 一致: a2/b1b全role(Adv narrator/preview/comment、日本語role、Dialogue意図sha、KP)、production形のAdv plan(KP_EXPL_EN)、`run_audio_gate`配線と要約、hint追記prefix(hint flag・先頭一致・startswith)
- BLOCK: 不一致注入(role群別7件)、未記録(strict)、未実測(`意図sha(実測なし)`は一致扱いにならない)、checked空、必須role欠落(`STD_JA_COMMENT`/`KP_THIRD`)、level外role、表drift
- fallback: Style落ち採用=承認なしBLOCK/別text承認でBLOCK/正しい承認でPASS、fallback段でも承認Style=違反なし、猿の手型(標準=承認・fallback=落ちStyle・top-levelは旧段)でfallbackを採用attemptとして検出
- 過去run: 未記録=警告のみ(PASS)、attempts由来の不一致は`Z_STYLE_LEGACY_DERIVED_MISMATCH`警告、記録のあるclipは過去run内でも厳格、マーカーは新規levelのみ・dry-runは書かない
- Dialogue: 意図sha食い違い=BLOCK、ctx採用はctx sha許容、従来方式切替は違反でない、実測値は既定shaと一致必須
- 正式経路mock: er026 runner `build_mock_context`のstage tts_b1b/tts_a2/provision_shell/gateでGate発火(両levelでstrict PASS、照合表・マーカー・gate_result要約あり)、`mock_tts_generators`の`preview`が承認E1を落としたStyleを送ったことにすると`stage gate`が`FamilyZStyleActualGateStop`でBLOCK(Gate PASS成果物なし)
- 独立: Z側でX `m3_assembly_gate`/Y `y_style_gate`/`resolve_run_profile`を呼ばない

## 回帰(実行結果、本委任の差分に起因する失敗0)
`er063*` 161 passed(新規31含む) / `er117*` 106 / `er062*` 147 / `er127*` 102 / `er118*` 89 / `er026*` 222 passed 2 skipped / `er120*` 14 / `er104*` 66 / `er103*` 52 / `er078*` 4 / `er061*` 54 / `er121*`(Y) 368 passed 1 skipped / er122(pytest) 69 passed。
本委任と無関係の既存失敗: `er119*` 2件(未追跡`er119_output/`残存、`er121/er123/er124`のer119 import)・`er109*` 5件(`er118_fz_*`/`er122_fz_ctx_fakes_01.py`/`er121_e1_slowed_asr_recheck_01.py`等のscope import固定listとgolden署名差)。触っていないファイル群に起因(分類=修正へ進む・別委任)。

## 実データでの確認(read-only、tmpコピー、run dirは不変)
猿の手`run_sf_prod_01`のa2/b1b既存resultsを、planをentryから復元して新Gateに通した(マーカー無=過去run扱い):
- a2: status=PASS、mode=`legacy_run_warning_only`、42行すべて`Z_STYLE_ACTUAL_UNRECORDED_LEGACY_RUN`警告、attempts由来の不一致警告=`full_story_part1_c10`のみ(fallback採用attemptのsha `dba23e66…`≠承認PD06)。
- b1b: PASS、45行すべて未記録警告、不一致導出なし。
=遡及BLOCKせず、Gate導入前のrunは「未記録」警告で通り、c10はattempts由来で可視化される。

## 残課題・制約(Open Item候補の分類つき)
1. Dialogue実測化(leaf `er012`が送信prefixを返さない): 分類=**ユーザー判断不要・次委任案**(leaf追加はX/Y/Z共有のためFable判断、分類C相当[現タスクと独立の改善]。当面は意図sha検査+`measurement_gap`明示)。
2. 実leaf結果での最終確認(実API): 本委任はmock確認まで(到達上限=IMPLEMENTED)。**実Z run(次の新規Zrunの`tts_*`/`gate`)で初めて実leafのstyle_prefix戻り値がGateを通る**。取得元はGrepで確認済みだが、未確認箇所があれば初回実runのGate BLOCKとして現れ(fail-closed)、人間承認または`style_actual`取得修正で対応する。分類=**修正へ進む(実run時に検証)**。
3. Gate導入前に生成済みの公開版(猿の手Std c10): PUBLISHED_CLIP_CHECK_01.md。分類=**ユーザー判断要**(公開物差替え)。
