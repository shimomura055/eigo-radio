# PHASE_A_SURVEY_01(FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_01 Phase A、2026-10-12)

read-only調査。課金0・コード/Prompt/Routing/SSOT無変更。実行したのは (a) er026 pytest 19件(PASS、API無し)、(b) R2本文をfam_c関数に通すローカル計算(書込無し)のみ。
行番号は2026-10-12時点のmain(HEAD 0177ab92)基準。旧設計書 `docs/pm/design_family_z_melos_production_e2e_and_latest_spec_wiring_01.md`(2026-09-29)は行番号が古い(L1239が現L1373等)ので本書の番号を正とする。
Status略称: 実装済み / 未実装 / Trialのみ / 要決定。

## 0. 先に報告すべき重要所見(PM判断用)
1. **「Family Cベース」の逐語決定は CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS のGrepで見つからなかった**(`Family Cベース`/`Cベース` 0件、`Family Z`+構成/3分割/Comment系の検索でも該当なし)。SSOT上の関連正本はZ-2(下記1)のみ。Fableに決定原文の提示(または再確認)を要請する。
2. **Z-3(In One Line、APPROVED_FOR_PRODUCTION)とFamily C構造の関係は要決定**。Family CにはIn One Lineが無い(CURRENT_SPEC L1511-1513)。「Z-3を無条件に復活させない」の解釈(IOLを廃止するか/保持するか)はユーザー決定事項。
3. **R2は現行Zの検査に不合格になる**: R2は主人公Melosのみ固有名で、`Dionysius`/`Selinuntius`を含まない(統治者=the ruler、友人=his friend)。er026 `check_character_name_rule`(L239-250)は両名を必須としFAIL、`restore_character_names`(L252-)は元Luna版の文言アンカーを探して`RuntimeError`で落ちる。さらに`strip_markdown_title`(L223)は`### `見出し前提だがR2は`# Before Sunset`(#1個)で、題名が本文に残る。**原作保持条件(CURRENT_SPEC L1401-1406 項目2)とR2の整合はユーザー判断**(私は再解釈しない)。
4. **Advanced用Z原稿が存在しない**: Zは現状A2(Standard)のみ(`run_keyphrase_stage` L732が`"A2"`固定、B1B trackなし)。R2はA2指示で生成されたもの。Advanced本文の作り方は未決で、Production採用済み仕様は無い。
5. **Coffee最新Style(A5/B5/E1/PD8/R2/K2/M2)はCoffee限定承認**(`er057_output/coffee_final_audio_assembly_01/FINAL_V3_BUILD_PLAN_01.md` L3「Coffee記事限定。全記事共通Styleは未承認」)。実体はTrial script(er057_*)内定数で、Production経路(er033等)には未配線。ZへのStyle適用は別途ユーザー承認が必要。
6. **Key Phrase artifactは再利用不可**: `er035_output/kp_4plus1_evidence_01/melos_a2/`は旧Luna本文用。R2は別本文なのでKP再選定が必要(LLM課金あり)。
7. **R2本文はfam_cのDialogue分割で12 segment**(下記2-E)。voice keywordsに`friend`が必要(現行はdionysius/rulerのみ)。ruler台詞の一部はnarratorに落ちる(要override)。

## 1. Family Zの正式Story分割・Comment構成(項目1)
SSOT正本(逐語):
- CURRENT_SPEC L1460-1462(Z-2): 「Family Z専用runner(新設)を作るが、Family C既存関数(`plan_story_segments()`等)を再利用する方式とする。`APPROVED_FOR_PRODUCTION`。Family C本体を不要に変更しない。」
- L1463-1464(Z-3): 「既存In One Line Promptを、Fiction向けに最小変更して流用する。`APPROVED_FOR_PRODUCTION`。新しい独立機構を追加で作らない。」
- L1465-(Z-4): Story本文は単一canonical text、Dialogue部分は既承認Voice assignmentルール(Family C `classify_quote_voice_window`+`voice_tts_names`)。
- L1523-(Family体系、2026-09-27): Family A/B/CはLegacy/Backup。「新規実装を行わない/最新仕様へ追従させない/read-onlyの参照元としてのみ使う(例: Z-2/Z-4が`plan_story_segments()`/`classify_quote_voice_window()`を再利用する場合)」。
- 3分割+Comment1〜4(旧Phase A設計): `docs/pm/design_family_z_...01.md` §3(a)(b)。`docs/pm/design/2026-10-11_FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01_Z_INVENTORY_01.md` L65-68は「Phase A設計(未承認・未実装)」「3分割+Comment4構造の採用承認は未取得」と明記。**つまり3分割+Comment4はSSOT正式仕様ではなく旧Phase Aの案**。

Family Cの実際の構成(`er013_family_c_production_runner_01.py::build_family_c_episode_sequence` L485-554、実装済み): Intro, Welcome, Topic intro, (JA title), Notification, Preview intro, Preview, Notification, Key phrases intro, KP×5, Notification, Full story intro, **Comment1**, Story voice-segments(`comment_after_segment_id`で指定した位置へ**Comment2/Comment3**), Outro。Comment4・In One Line・3分割Full Story・Standard/Advanced 2レベルは無い(Family CのA2/B1は別runnerパスで、Zと同種の2レベルではない)。
- 矛盾の有無: (a)Family C構造にIn One Lineが無く、Z-3(APPROVED)と衝突しうる。(b)Family X構造(Part1-3・Comment1-4・IOL)とも異なる。(c)Z-2は「関数の再利用」であって「構成のベース」を述べておらず、構成の決定原文は未発見(0-1)。**構成確定はFable/ユーザー決定が前提(Phase Bの最初のGate)**。
- 現状のZ実装: Preview/Comment1/IOLのみ(`run_text_stage` L577-)。Comment2/3(Family C関数呼出で可)は未実装、Comment4はFamily Cに無く未実装。

## 2. Family Cの既存実装と再利用可能範囲(項目2)
| 機能 | ファイル:関数(行) | 入力 | 現状 | Z再利用 |
|---|---|---|---|---|
| segment planner | `er013_family_c_production_01.py`: `split_into_paragraphs` L62, `build_flat_voice_chunks` L122, `plan_story_segments` L306, `reconstruct_article_from_segments` L333 | 本文str、`voice_keywords{voice:[kw]}` | 実装済み。Zのer026 `build_segment_plan` L333が既に呼ぶ | 可(無変更) |
| Dialogue Voice判定 | 同: `classify_quote_voice_window` L66(前後80字のキーワード)、`split_paragraph_by_quotes` L98、`build_flat_voice_chunks`の`quote_voice_override_paragraphs`引数 | 同 | 実装済み(Trial VALIDATED、OPEN-156) | 可。R2は誤判定をoverrideで補正する必要(2-E) |
| Dialogue多声clip TTS | `er013_family_c_production_runner_01.py::tts_call_for_voice` L356(narrator=`repro01.generate_narration_snippet_verified_strict`、他=`bvoices.generate_voice_body_wide_margin(text,out,voice_name)`) | voice,text,`voice_tts_names` | 実装済み。**ただし旧TTS入口**: `enable_connected_speech_equivalence_layer`/`enable_pronunciation_resolver`/Flash-Lite/Role Styleを渡していない(runner内grep 0件) | 呼出先関数は流用可。**ZはConnected Speech/resolver/symbol normalizationを渡す新ラッパが必要**。Family C runner自体は改変しない |
| Assembly順序 | `build_family_c_episode_sequence` L485、`assemble_mod.assemble_with_timeline` L943、`apply_headroom_safety_valve` L980 | seq=(label,stereo) | 実装済み | sequence関数はCの構成固定(Comment1-3/Outro/Notification)。Z用は新規またはパラメータ流用(構成決定後) |
| Audio Validation Gate | `er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate` L469(Family Cは`level_string="FAMILY_C_PRODUCTION_A2"`、required_structureなしで呼出) | out_dir, `audit/tts_generation_results.json` | 実装済み・Family非依存 | 可。level文字列が`"A2"`だと6%減速必須チェック(`_segment_missing_mandatory_a2_slowdown`)が効く(名前一致する`full_story_part*`等のみ)。Z用required_structureは未定義 |
| player/web_delivery | `er013...runner::write_evidence_player` L990、`audio_review_player`、`convert_all_to_mp3` L959 | run_summary | 実装済み | 可(Z用出力パスで呼出) |
| Comment生成 | `generate_family_c_a2_comment` L460(comment_num 1..3のみ、他は`ValueError`)、`FAMILY_C_A2_COMMENT_ROLE_JA_1/2/3` | article, content_facts, scene_transition | 実装済み | Comment1(Z実装済み)・2・3可。Comment4は不可(Z新Prompt要、Family C本体変更禁止) |
- Family C本体の変更は不要(read-only参照)。Family X共有層の変更要否は項目9。

### 2-E. R2本文のローカル検証結果(ローカル計算、書込無し)
`er059_output/melos_sol_b3z_trial_01/m2_sol_only/r2.md`(`# Before Sunset`、364語、語数受入280-420内)を、`voice_keywords={selinuntius:[selinuntius,friend], dionysius:[dionysius,ruler]}`で`fam_c.build_flat_voice_chunks`+`plan_story_segments`へ通した実測: 12 segment。語数(voice): 27(narrator), 6(dionysius), 31(narrator), 6(selinuntius), 3(narrator), 15(dionysius), 5(narrator), 3(selinuntius), 108(narrator), 112(narrator), 4(selinuntius), 44(narrator)。再構成一致(`reconstruct_article_from_segments`)は未検証でPhase Bで確認する。
所見: 3〜6語の短segmentが6つ(Voice境界の不可避短segmentとして仕様Aの許容範囲)。ruler台詞「What if you run away?」「Let them both go...」はキーワード不在でnarratorに落ちる(要override)。Melos台詞は`he said`等の属性でnarrator(Aoede)になる(Melos専用voiceの仕様は無く、Z-4どおり主人公=narrator声か要確認)。

## 3. Family Z正式初回経路とretry/fallback/regeneration/resume(項目3)
- 入口: `er026_family_z_fiction_production_runner_01.py` `--stage text|keyphrase|all|tts|assemble`(`main` L787-)。
- 実装済み: `check_rights_gate` L114(fail-closed)、`MELOS_RIGHTS_BLOCK` L128、`STORY_REGISTRY` L182、canonical text受入(語数280-420: `ACCEPT_WORD_RANGE`/`check_word_count` L232)、人物名ルール検査(L239)、`build_segment_plan` L333、`build_story_type_metadata` L560、`run_text_stage` L577(Preview/Comment1/IOL生成+`article_config.json`書出)、`run_keyphrase_stage` L736(`scaffold.run_key_phrases(..., "A2")`)。pytest 19件PASS(今回実測)。
- **未実装(NotImplementedError)**: `stage_tts` L765、`stage_assemble` L778。retry/fallback/regeneration/resumeはZ側に**一切未実装**。Family Cの`resumable_reuse` L323/`purge_segment_outputs` L313/`--only-segments`、および共有TTS関数内蔵のattempt cascade(`er003_v1_crosslevel_audio_02_common.generate_english_segment_with_fallback` L83-)は存在するが、Zからは未接続。
- OPEN-185(OPEN_ITEMS L366): 構造論点(2)(3)(4)はZ-2/3/4で解消、権利(Z-1)も解消。PRODUCTION_WIRED条件(CURRENT_SPEC L1451-)は未充足。
- 本文は **Trialのstory.md(Luna単発)を`load_trial_seed_and_story` L213で読む**(Z専用Production Writerは存在しない)。

## 4. Sol+R0→R1→R2の正式Writer配線(項目4)
- Z側Writer配線: **なし**。er026はWriterを呼ばず、`er018_output`のTrial story.mdを読むのみ。routing keyにZ Production Writer用は無い(`er006_model_routing_contract_01.py` L142-143は`FAMILY_Z_TRIAL_STORY_QUALITY_EVAL`/`FAMILY_Z_TRIAL_RIGHTS_INTERPRET`のTrial評価用のみ)。
- Trial②: `er059_melos_sol_b3z_trial_01.py`(Trialのみ)。R0/R1/R2は`er059_output/melos_sol_b3z_trial_01/m2_sol_only/{r0,r1,r2}.md`、`chain_meta.json`(model=gpt-6.1-sol, effort=high, 各attempt=1)。R2は364語。R2のsha256は実行時に取得(未固定)。
- X側参考: routing key `FAMILY_X_FACTLOCK_R0`/`FAMILY_X_FACTLOCK_REVISE`=gpt-6.1-sol(er006 L137-138)。**`--approved-quality-master`という引数名はコード内に存在しない**(grep 0件)。実在する類似機構はer019 `load_reused_ja_text` L234-256(U-1): `runtime_evidence.json`の`chain_method=="W-1"`+`annotated_md_sha256`一致を確認し、不一致なら`LegacyWriterProvenanceStop`でSTOP。この「来歴+sha一致で受理、不一致でSTOP」の考え方は参考になる。
- 最小配線案(参考、実装はPhase B以降): Z用`approved_manuscript`受入関数を追加し、(i)`chain_meta.json`のmodel/chain(R0→R1→R2)と`r2.md`のsha256を`article_config.json`へ固定記録、(ii)sha不一致はSTOP、(iii)`resolve_canonical_text`の入力を`load_trial_seed_and_story`からこの経路へ切替(`# `見出し除去・斜体`*...*`記号の扱いを含む)。Writer再実行(LLM)は含めない。Z用routing keyは「R2を受理する」だけなら不要。将来Sol Writerを量産経路へ配線する場合のみZ用routing key新設(未決)。

## 5. 読み解決・TTS正規化・ASR・Local Rewrite・Gate(項目5)
| 機構 | 所在 | Z適用 |
|---|---|---|
| 読み解決resolver | `er025_entity_pronunciation_resolver_core_01.py`(`seed_work_canon_reading` L408、`source_context="family_z_melos"` L276) | **未接続**(TTS stage未実装)。英語TTS入口に`enable_pronunciation_resolver=True`をZが渡す必要がある(Family C runnerは渡していない)。R2は固有名がMelosのみで影響小。日本語のメロス読みはwork_canon seedが要 |
| TTS記号正規化 | `er003_v1_n3_01_tts_generate.py::tts_safe_news_en` L816(+`er003_audio_tts_asr_safety`) | 共有関数としてZから呼べる。**R2は斜体`*“I will wait.”*`を含む**ので適用必須(CURRENT_SPEC L2127-2129「Family Z Writer実装時の必須適用」)。Z未接続 |
| Connected Speech/Local Rewrite | `er020_tts_retry_local_rewrite_01.py::resolve_narrative_role` L120 | **Z固有の欠落**: `full_story_part1/2/3`完全一致のみFULL_STORY(L127)。R2は12 segmentでpart4以降が対象外。正規表現追加(後方互換)かZ側で3 partに束ねる命名かの決定が必要。既知gapは`segment_plan.json`の`known_gap`に記録済み |
| ASR(英語Primary/Secondary、日本語Primary+SCG) | 共有`er003_*`/`er007_ja_secondary_asr_01.py`(CURRENT_SPEC L1945/L1994) | TTS関数内蔵のため、Zが共有TTS関数経由なら自動適用。Zの日本語固定文(JAタイトル等)の読み検証は未配線 |
| Audio Validation Gate | `verify_episode_audio_validation_gate` | 共有可(項目2)。Z用`required_structure`未定義 |
- 備考: X側は`generate_a2_segment_with_slowdown`/`generate_a2_japanese_with_reading_safety`(`er003_v1_n3_01_tts_generate.py` L208/L627)を使う。関数単体は`text, out_path, expected_substring, style_prefix_override`等で呼べる設計だが、`parts`/`support`辞書のX構造向けなので、Zのvoice clip単位に流用可かはPhase Bで確認する。

## 6. Coffee最新Style(A5/B5/E1/PD8/R2/K2/M2)のZ適用可否(項目6)
出典: `er057_output/coffee_final_audio_assembly_01/FINAL_V3_BUILD_PLAN_01.md`(role別表)。承認範囲は「Coffee記事限定」、全記事共通は未承認。実体はTrial script `er057_coffee_final_v3_gen_01.py`(PD8は`er057_output/pace_trial_02/prompts/prompts_pace_02.md`からsha照合ロード)で、**Production経路へは未配線**。
| Z role | Xでのcoffee Style | Z適用可否 |
|---|---|---|
| Intro A/B(固定Master) | A5/B5(Charon) | 固定Master再利用で可(Master Storeは汎用cache)。Coffee限定承認 |
| Preview(JA, Standard) | R2(Aoede) | Z JA PreviewはAoede。R2適用はユーザー承認要 |
| Preview(EN, Advanced) | E1(Charon) | Zに英語Preview生成工程が無い(項目7) |
| Comment1-4(JA, Std) | R2 | Z JA Commentに同上 |
| Comment(EN, Adv) | E2_UPBEAT(既存承認) | Zに英語Commentが無い |
| KP英語/日本語 | K2 / M2 | role=KEY_PHRASE共通なので技術的には可。Coffee限定承認 |
| Full Story | PD8 | **Dialogue clipへの適用は未検証**(PD8は単一narrator想定の「ラジオ・フィーチャー調」。Erinome/Charonの台詞clipに同じstyleを付けるか、narratorのみかは未決。PD8のWPM 183.2はCoffee Advanced実測であり、Fiction台詞に妥当かは未検証) |
| In One Line | 現行Style | 可 |
結論: Style適用は`style_prefix_override`/Role Style経由で技術的には可能だが、ZのDialogue Voice×新Styleは未検証、かつ共通採用は未承認。

## 7. 日本語Preview/CommentのZ原稿生成、Key Phrase、In One Line(項目7)
- JA Preview: `generate_family_z_preview` L460(Z所有prompt `_FAMILY_Z_PREVIEW_ROLE_JA` L426-、実装済み。`a2gen.run_support_text`、model=routing `A2_WRITER`)。
- JA Comment1: `generate_family_z_comment_1` L518(Family C `generate_family_c_a2_comment(comment_num=1)`呼出、実装済み)。Comment2/3: 同関数で可(未実装、content_facts/scene_transitionをZ側で用意)。Comment4: 未実装(構成決定後)。
- 英語Preview/Comment(Advanced用): **Zに存在しない**。
- Key Phrase: Strategy L(`scaffold.run_key_phrases(...,"A2")`)実装済みだがrun_01は4+1導入前schema。4+1 artifactは旧本文用(0-6)。Advanced用KP英語解説(B1B仕様)はB1B trackが無く未対象。
- In One Line: `generate_family_z_in_one_line` L481(Z-3、英語、Z所有prompt)。構成決定待ち。
- 固定語(welcome/topic_intro/japanese_title/num_*): Master Store再利用。topic_introはZ未実装。`japanese_title_text`は`STORY_REGISTRY`(L186)に`走れメロス(The Three-Day Promise)`が固定(R2の題名はBefore Sunsetなので整合確認要)。

## 8. 権利Gate・外国人名ルール・Story Type metadataとR2(項目8)
- 権利Gate: `check_rights_gate` L114、`MELOS_RIGHTS_BLOCK` L128(原作固定、`STORY_REGISTRY['melos']['rights_block']`)。R2は同一Seedの翻案なので権利ブロックは再利用可の見込み。ただしCURRENT_SPEC L1407-(3)は「adaptationは確認済み原文/正式Seedから自前生成」なので、`er059`が使ったSeed入力と`seed.json`の同一性(sha)をPhase Bで照合する。
- 外国人名ルール(CURRENT_SPEC L1426-): First/Last片方のみ。R2は`Melos`のみ→ルール違反なし。一方、項目2(L1401-)と`check_character_name_rule`は`Dionysius`/`Selinuntius`の保持を要求→**R2とZ既存検査が衝突(0-3)**。ユーザー決定が要る。私は再解釈しない。
- Story Type metadata: `build_story_type_metadata` L560。`literature`=UI表示なし・音声冒頭追加なし(CURRENT_SPEC L1437-)。所在=`er026_output/family_z_production_e2e_01/melos/run_01/article_config.json`の`story_type_metadata`。R2に追加の付帯情報は不要だが、**来歴情報**(Writer=gpt-6.1-sol、R0→R1→R2、`r2.md` sha256、`chain_meta.json`、比較Trial②由来、B3Z REJECTED)を`article_config.json`へ追加するのが望ましい。

## 9. 実装範囲見積・リスク・費用・時間(項目9)
サイズ(S=小/M=中/L=大の相対規模):
| 対象 | 内容 | サイズ | 変更種別 |
|---|---|---|---|
| `er026_family_z_fiction_production_runner_01.py` | R2受入(来歴固定・見出し/斜体処理・名前検査の扱い)、Comment2〜(4)、Advanced用原稿経路(要決定)、`stage_tts`(Flash-Lite/Role Style/Connected Speech/resolver/ASR/retry/resume/regen)、`stage_assemble`(Z用sequence、Gate、player) | L | Z側のみ |
| `er020_tts_retry_local_rewrite_01.py` | `resolve_narrative_role`に`full_story_part\d+`等を追加(既存3完全一致は不変)。Z側で3 partに束ねれば不要 | S(不要になる可能性あり) | 共有層(X挙動不変を`run_project_regression.py`で確認) |
| Style定数(`er033_tts_flash_lite_family_x_styles_01.py`) | ZへのCoffee Style採用(承認後)。Z専用Style表をZ側に置けばXを触らない | S〜M | 要承認 |
| テスト | R2受入、segment plan、voice override、role map、stage_tts mock、Gate | M | 新規 |
| Family C(er013) | 変更不要(read-only参照) | なし | - |
| Family X(er019等) | 変更不要見込み。共有`er020`のみ上記最小変更の可能性 | - | - |
Family X/Cコード変更の要否: C=不要。X=原則不要。`er020`だけ「ZがFULL_STORY判定を12 segmentに延ばす」場合の追加正規表現が最小案。影響範囲は`resolve_narrative_role`/`connected_speech_enabled_for`の全呼出元(X/B1/A2のTTS入口)。既存IDは不変なので回帰で確認可能。

費用概算(未実測の見積。Writer再実行なし=R2再利用。LLM 1回約¥3、TTSは直近実測¥0.86/clip[Flash-Lite、ASR込み]を基準):
- Standard: JA Preview+Comment1〜4(5 call)約¥15、KP再選定(Strategy L)約¥10〜30、IOL約¥3、TTS約28clip(story 12+Preview+Comment×4+IOL+KP10、固定語はMaster再利用)約¥24+retry余地。
- Advanced: 原稿作成(未決。新Sol R0〜R2相当ならTrial②実績約¥8/式)+英語Preview/Comment生成(工程新設)+KP英語解説+TTS約¥25+retry余地。
- 合計: 約¥100〜180(2レベル、Advanced原稿工程の決定次第)。Guardrail案は承認後に設定(Z BudgetGuard L75は既存¥200/警告¥150)。
- Azure(Secondary ASR): 不一致時のみ(Cascade内蔵)で、共有設定の上限に従う。

所要時間(見込み): 構成決定後、Z TTS/Assembly実装+test 1〜2セッション、E2E実行(両レベルTTS)1セッション。TTS Batch APIのレイテンシに注意(Family C記録で90分超の例あり、CURRENT_SPEC L1110付近)。
並列化可能: (a)Advanced原稿方針の決定待ち中にStandard側のTTS stage実装、(b)Preview/Comment/IOL/KPのLLM生成(互いに独立)、(c)Dialogue clipとnarrator clipのTTS(clip単位で独立、条件同一)、(d)test作成とE2E runner、(e)Advanced英語Preview/Comment工程。直列必須: 構成決定、Writer原稿(R2受理)、KP選定(原稿依存)、TTS、Assembly、Gate、試聴ページ。`er020`編集は他タスクと競合しうるため単一担当にする。
リスク: (R-1)Family C構造・Z-3・旧Phase A案の三者不一致、(R-2)R2が名前保持条件と衝突、(R-3)Dialogue Voice×新Style未検証、(R-4)ruler台詞のvoice誤割当(override要)、(R-5)Advanced原稿が無い、(R-6)`resolve_narrative_role`の12 segment問題、(R-7)Coffee限定Styleの横展開未承認、(R-8)Family C旧TTS入口を流用すると新Production機構(resolver/CS/Flash-Lite)が抜ける、(R-9)X音声仕様のFix待ち保留: OPEN-297(L800)は「Family Z TTS/AssemblyはX音声仕様Fixまで保留」と記載。OPEN-276(Std part2 6%減速未適用)、OPEN-279(Trial限定条件)、OPEN-281は未解決のままのX側論点で、解除状況をFableが確認すること。

## 10. Dangling候補・既存承認事項との矛盾(列挙のみ、再解釈しない)
1. 「Family Cベース」決定原文が未発見(0-1)。
2. Z-3(IOL、APPROVED)とFamily C構造(IOLなし)と「Z-3を無条件に復活させない」の関係。
3. R2(固有名Melosのみ)とCURRENT_SPEC L1401-1406項目2+`check_character_name_rule`(Selinuntius/Dionysius必須)。
4. R2見出し形式(`# `)と`strip_markdown_title`(`### `)、斜体記号とTTS記号QA。
5. `STORY_REGISTRY['melos'].japanese_title_text`(走れメロス(The Three-Day Promise))とR2題名(Before Sunset)。
6. 旧設計書(2026-09-29)のSSOT行番号が現行と不一致。同書はJ3/E2「適用範囲」記述をZにも及ぼす更新を提案しているが未承認・未実施。
7. 旧設計書は`num_three/num_five`が「B take1」と「CURRENT_SPEC未確定」で不一致としていた。現行状況は再確認要。
8. OPEN-297(L800)の判断待ち(c)Sol採用(e)R0→R1→R2のZ Production化は、今回のユーザー確定(2026-10-12)で決着するはずだが、SSOT本体(OPEN_ITEMS/DECISION_LOG/CURRENT_SPEC)には未反映(反映はFable/次工程)。
9. CURRENT_SPECのX W-1記述(「R1・R2=gpt-6-astra」)とrouting実値(`FAMILY_X_FACTLOCK_REVISE`=gpt-6.1-sol)に食い違い(X側のドキュメント遅れ、Z範囲外)。
10. Coffee限定承認Styleの共通化は未承認(ZへのPD8/R2/K2/M2適用はユーザー承認を要する)。

## 11. PM向け一覧
| 項目 | 区分 |
|---|---|
| Z segment planner/Dialogue判定/権利Gate/story_type/人物名検査/Preview/Comment1/IOL/KP stage | 再利用可(実装済み、無変更) |
| Family C Comment2/3、Gate、assemble_with_timeline、player | 再利用可(呼出のみ) |
| Z stage_tts / stage_assemble / retry・resume・regen | 実装必要(L) |
| R2受入(来歴固定、見出し・斜体処理、名前検査の扱い) | 実装必要(M)+ユーザー決定 |
| Connected Speech用segment_id | 実装必要(S、`er020`共有)または命名設計で回避 |
| Comment4、英語Preview/Comment(Advanced)、Advanced原稿 | 未実装・未決(構成/方針決定が前提) |
| Coffee Style(A5/B5/E1/PD8/R2/K2/M2)のZ適用 | 未決(Coffee限定承認、承認が必要) |
| Z構成(Family Cベース vs 旧Phase A 3分割)・IOLの扱い | 未決(USER_DECISION_REQUIRED) |
| R2と原作保持(固有名)条件の整合 | 未決(USER_DECISION_REQUIRED) |
| KP再選定 | 実装不要・実行必要(R2依存、LLM課金) |

## 12. Phase B/C実施計画案とSTOP候補
- Phase B0(決定、実装前): 構成確定(Family C構成でIOL/Comment4/3分割をどうするか)、R2と名前条件、Advanced原稿方針、Style適用範囲、予算上限。いずれもユーザー決定。
- Phase B1: Z runnerにR2受入(来歴sha固定、STOP条件付き)+Comment2/3(必要なら4)+Z test。課金は少額(Comment等LLM)。
- Phase B2: `stage_tts`(Standard、共有TTS関数の新Production機構ON)+voice override+Connected Speech対応+test(mock)。
- Phase B3: `stage_assemble`+Gate+player+Standard E2E(実TTS)。続けてAdvanced(原稿決定後)を同手順で。共通部を先に作れば両レベルを分担可。
- Phase C: 試聴ページ、SSOT反映(Fable)、Closeout、Opus独立レビュー(新構造設計=条件A、実装後)。
STOP候補: (S1)Family C構成の決定原文が無い/Z-3と矛盾、(S2)R2が名前保持条件に未適合、(S3)Advanced原稿方針なし、(S4)Dialogue Voice×新Styleが不採用/未承認、(S5)Dialogue clipのASR連続NG(Local Rewrite上限到達)、(S6)予算超過、(S7)OPEN-297の「X音声仕様Fix待ち」が未解除、(S8)`er020`編集が他タスクと競合。
