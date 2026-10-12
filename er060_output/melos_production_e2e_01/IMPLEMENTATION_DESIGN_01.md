# IMPLEMENTATION_DESIGN_01(FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_02、2026-10-12、Opus独立レビュー条件A対象)

設計のみ。コード実装・有料API・Prompt/Routing変更なし(課金0)。ユーザー正式決定①〜⑤(`DECISION_LOG.md`、APPROVED_FOR_PRODUCTION)を前提とする。衝突整理は`CONFLICT_RESOLUTION_01.md`(以下CR)。行番号は2026-10-12時点main(HEAD 7d9afc82)。

## 0. 先に確認してほしいこと(Fable/Opusへ)
1. **CR-B2**: OPEN-297の「X音声仕様Fixまで保留」を、本決定で解除されたと解釈してよいか(本書は解除前提で設計)。
2. **既存機構の再利用で判明した重要事実**(重複機構を作らないための根拠):
   - Family Xに「Advanced→Standard」の既存正式機構がある(`er003_v1_n3_01_standard_a2_generate.py::generate_family_x_standard_a2_no_heading`)。ただしPromptが `## In one line` 節の保持を要求する(L519)ため、IOLなしのFamily Zには**そのままは使えない**。→(a)で共有部品(`STANDARD_A2_NEW_VOCAB_BLOCK`等)を再利用するZ専用Promptを提案。
   - X B1(Advanced)の `COMMENT_1_ROLE`/`COMMENT_2_ROLE`/`FAMILY_X_B1_COMMENT_3_ROLE`(Comment3=「Mid-story Recovery + Bridge to Part 3」、`er019_family_x_audio_plan_01.py` L182)は、決定①の「Comment×3、Part1-2間・Part2-3間」配置とそのまま一致し、IOLへの橋渡しを含むのはComment4のみ。→ Advanced英語Commentは**無改変再利用**可。
   - Dialogue clipには従来系の既存関数がある(`er012_b_family_voices_production_01.generate_voice_body_wide_margin`、`er012_b_family_voices_a2_production_01.generate_voice_body_wide_margin_with_a2_slowdown`。Connected Speech・repetition QA・style_prefix_override・6%減速対応)。決定④「セリフは既存別Voice・従来Dialogue Style」と一致。
3. Coffee evidence内の表記不一致: `FINAL_V3_BUILD_PLAN_01.md`はStd Preview/Commentを「R2」、`STYLE_APPLICATION_EVIDENCE_V3_01.md`は「P2」と表記。OPEN-295はR2選択。決定④もR2。→ 実装時にPrompt本文の**sha256照合**(R2=`625826c1…`)で確定する(新規OPEN-303)。

## 1. 全体像・ファイル分割(並列実装用)

| 新規/変更 | ファイル | 内容 | 種別 |
|---|---|---|---|
| 変更 | `er026_family_z_fiction_production_runner_01.py` | stage順序・CLI・resume・budget・provenance記録・各moduleの呼出(オーケストレーション)。`stage_tts`/`stage_assemble`の本体は下記moduleへ | 既存拡張 |
| 新規 | `er061_family_z_semantic_validator_01.py` | 意味保持Validator(2層)+`_test_01.py`+fixtures | 新規(Z一般仕様) |
| 新規 | `er062_family_z_writer_01.py` | `writer_adv`(R0→R1→R2)・`level_adjust_std`・provenance sha chain | 新規 |
| 新規 | `er063_family_z_audio_01.py` | Role Style表・Dialogue Voice override・TTS(narrator/dialogue/support/KP)・assemble・Gate・player | 新規 |
| 変更(追加のみ) | `er006_model_routing_contract_01.py` | routing key追加(下記) | 共有層・追加のみ |
| 変更(1行追加) | `er020_tts_retry_local_rewrite_01.py` | `resolve_narrative_role`の正規表現追加(CR-B4) | 共有層・後方互換 |
| 不変 | `er013_*`(Family C)、`er019_*`(Family X)、`er033`(X Style定数)、`er003_*` | 関数呼出(import)のみ | read-only参照 |

追加routing key(リテラル固定、環境変数上書きなし、既存キー不変。X `FAMILY_X_FACTLOCK_*`と同型):
`FAMILY_Z_WRITER_ADV_R0`/`FAMILY_Z_WRITER_ADV_REVISE`/`FAMILY_Z_LEVEL_ADJUST_STD`=`gpt-6.1-sol`、`FAMILY_Z_SEMANTIC_JUDGE`=`gpt-6-luna`。`FAMILY_Z_TRIAL_*`(Trial用)は不変。

## (a) Writer: Advanced新規作成 + Standard調整

**問題**: Z ProductionにはWriterが無い(`load_trial_seed_and_story`がTrial story.mdを読むのみ)。Trial②のStandard R2(A2指示で生成)は正式採用されない(決定③)。Advancedが存在しない。
**変更**:
- `er062.run_writer_adv(seed, out_dir, budget, client)`: Trial②(`er059_melos_sol_b3z_trial_01.py::run_chain`)と同じ構造を正式化。R0=`e_axis.WRITER_DEVELOPER_MESSAGE`+Seed由来Prompt、R1/R2=`previous`本文+`REVISE_USER_TMPL`(「事実・人物・因果を変えずにより魅力的に」)。model=routing `FAMILY_Z_WRITER_ADV_R0/REVISE`(gpt-6.1-sol)、reasoning effort=high(Trial②と同一)、各callでresponseのactual model_idを記録し、要求modelと不一致ならSTOP(X `FAMILY_X_FACTLOCK_REVISE`の運用に倣う)。B3Zは使わない(REJECTED)。
- **Trial②からの必須変更(Advanced化)**: (i)R0 Promptの「A2 / simple / 300-350 words」を「natural English for CEFR B1 learners(Advanced)、about 〔語数範囲〕」に置換(A2語彙/文長指示を除く)。(ii)R1/R2テンプレの「Keep it at A2 level ... only Melos may have a personal name」を「natural, vivid English at B1 level; names are allowed but not required (foreign names: one of first/last only); do not invent names」に置換。(iii)A2のシンプル化指示は一切入れない。Prompt変更点はdiffとsha256を`writer/prompts/`に保存。
- **語数範囲(提案、新規OPEN-302で承認待ち)**: Advanced 400〜560語(目標約480)。根拠: 3分割×約130〜190語、約3分前後の物語音声、X Advancedは語数上限なし(CURRENT_SPEC全体語数「上限なし」)ゆえ範囲外れはGateでなくwarn扱いに近いが、Fiction短編の尺管理のためZ独自のhard rangeを置く。
- `er062.run_level_adjust_std(adv_text, ...)`: モデル=`FAMILY_Z_LEVEL_ADJUST_STD`(gpt-6.1-sol、理由: Advancedと同一モデルで語り口・解釈の一貫性、Writer系とは別routing key)。Prompt要件: Advanced最終稿を入力に、(1)出来事・人物関係・因果・順序・結末・会話の要点を維持、(2)語彙・文構造・難易度のみCEFR A2へ調整(`STANDARD_A2_NEW_VOCAB_BLOCK`、平均文長9〜11語目安・最長約18語目安をX既存Promptから共有定数として再利用)、(3)新Fact・新解釈・要約禁止、(4)見出し/IOL節なし、`# Title`+本文のみ、(5)「児童書調にしない、読み上げで自然」、(6)**Advancedと同一本文にしない**。**X既存関数 `generate_family_x_standard_a2_no_heading` はIOL節保持指示を含むためそのままは使わず**、同ファイルの共有ブロック(NEW_VOCAB_BLOCK等)をimportして**Z専用Prompt定数**を`er062`に置き、呼出は`vfl01.run_writer_no_search`(Xと同じ低レベル入口)。Prompt sha256をmoduleロード時にassert(Xの`STANDARD_A2_PROMPT_SHA256`方式)。
- **Standard受入ゲート**: 語数=Advanced語数の90〜115%かつ絶対320〜560語(提案、OPEN-302)。平均文長/最長文は診断記録(A2仕様「生成方針・機械gateでない」を踏襲)。Advancedとの文一致率(sentence単位`difflib`)が一定以上なら「同一本文」としてFAIL。意味保持Validatorをvs Seed・vs Advancedの両方でPASSが必須。
- B3Zなし、Trial②R2は参照のみ(来歴に比較参考として記載、採用しない)。

**改善**: 正式なAdvanced原稿とStandard原稿が量産経路で再現可能に作られる。
**リスク**: (1)Solのeffort=highは遅延/費用が増える(下記(i))。(2)Std調整で魅力が落ちる→Validatorの「appeal」項目+ユーザー試聴で確認。(3)語数範囲は未承認の提案値。

## (b) 原稿受入・来歴(sha chain)

**問題**: 再開(resume)時に、どの原稿から下流が作られたか検証できない。XはU-1(`load_reused_ja_text`、`er019_family_x_entertainment_production_runner_01.py` L233)で来歴とshaを検査する。
**変更**: run dir `er026_output/family_z_production_e2e_01/<slug>/<run>/writer/`に`provenance.json`を書く。鎖: `seed_sha256 → r0_prompt_sha → r0_sha → r1_sha → r2_sha(=adv_final_sha) → std_prompt_sha → std_sha`。各entryにactual model_id・effort・response_id・attempt数・cost。再開時は各成果物ファイルのshaを再計算し、記録・親shaと一致する場合のみ再利用。不一致は`FamilyZProvenanceMismatchStop`でSTOP。再生成は明示の`--regenerate-stage writer`のみ(下流は自動再生成せず、staleを`provenance.json`に`downstream_stale`として記録して警告=Xの運用と同じ安全側)。Trial②のr2.mdは`reference_only`としてshaのみ記録。
**改善**: 来歴の追跡可能性、stale音声の再利用防止。
**リスク**: 手編集した原稿は不一致でSTOPになる(意図通り)。人手修正が必要なら`--regenerate-stage`か、ユーザー承認の来歴追記手順を別途定義。

## (c) 意味保持Validator(Family Z一般仕様)

**問題**: 現行は固有名詞(Dionysius/Selinuntius)の有無だけで判定し、名前を機械復元する(`check_character_name_rule` L239、`restore_character_names` L252)。意味保持の検証ではなく、名前のない良い稿をFAILにし、名前を足せば意味が壊れた稿もPASSになりうる。
**変更**: `er061_family_z_semantic_validator_01.py`(Z一般仕様、story_key非依存。Melos固有定数はSeed側データ)。`validate_semantic_preservation(seed, candidate_text, reference_text=None, level) -> verdict`。
- 入力: 原作情報=既存Seed(`seed.json`の`original_summary`/`seed_elements`、`primary_text_excerpt.md`の日本語抜粋)+英語稿(Adv/Std各)。Stdはさらに`reference_text`=Adv最終稿でも検証。
- **第1層(決定論)**: (i)Seed要素ごとの概念family照合(各`seed_elements`に対し、人物役割/行為/因果を表す語彙familyを`seed.json`の`validator_anchors`として持たせる[新規フィールド、Seed登録時に作成・レビュー対象]。固有名詞は必須にしない)。(ii)**順序**: 重要出来事のアンカーが原作順序で現れるか(逆転=FAIL)。(iii)**結末矛盾**: 末尾段落が許容結末family(解放・和解・共に去る等)を含み、禁止family(両者処刑等)を含まないか。(iv)外国人名ルール: 同一人物の姓名併記等を検出(WARN→重複形式のみFAIL)、権利Gate(`check_rights_gate`)は既存のまま維持。(v)Melos等の主人公名がゼロでも、主人公が代名詞/役割で一貫して識別できればPASS(名前の有無を判定に使わない)。
- **第2層(LLM判定)**: model=routing `FAMILY_Z_SEMANTIC_JUDGE`=gpt-6-luna(最新世代推奨系。**執筆モデル(Sol)と別系統**にして自己同調を避ける。効果: 判定コストを1callあたり1円未満に抑えつつ独立性を確保)、N=1、temperature指定なし(推論モデル)、JSON schema強制。出力: `items[]`={category(role_relation/event/causality/ending/appeal)、seed_element_id、status(preserved/altered/missing)、severity(none/minor/major)、evidence_quote(英語稿からの引用)、reason(日本語)}+`overall`。**判定規則**: role_relation/event/causality/endingのaltered/missingでmajorが1件でもあればFAIL。minorまたはappeal欠落はWARN。
- **統合**: FAIL(第1層hard)またはFAIL(第2層)=FAIL。両層PASS=PASS。第1層FAIL×第2層PASSの食い違い=`NEEDS_REVIEW`としてSTOP(自動通過させない、Fable/ユーザーへ)。WARNは記録して続行。
- 既存`check_character_name_rule`/`restore_character_names`は量産経路から外す(関数は削除せず`superseded`注記。既存test 19件のうち当該名前系testは「旧仕様」として更新または`skip`理由付与=決定②の反映。削除しない)。名前の機械復元は行わない。
- 追加の誤検知対策: 第1層は「明白な矛盾・欠落」に限定し、曖昧さは第2層へ回す。

**Regression test設計**(`er061_family_z_semantic_validator_01_test.py` + `fixtures/`、固定fixture、LLM部分はmock、実呼出smokeは別):
| fixture | 内容(作成元) | 期待 |
|---|---|---|
| F1 正常(名前なし) | Trial②R2(`er059_output/.../m2_sol_only/r2.md`、Melosのみ固有名) | **PASS**(旧ルールではFAILだった例=改修の主目的) |
| F2 正常(名前あり) | 既存Luna版 `er018_output/.../03_japanese_lit_2/story.md` | PASS |
| F3 名前省略 | F2の`Dionysius`/`Selinuntius`を`the ruler`/`his friend`へ決定論置換 | PASS |
| F4 人物関係欠落 | R2から「友人が人質になる」くだりを削除、または友人を「見知らぬ旅人」に改変 | FAIL(role_relation/event) |
| F5 結末改変 | R2の末尾を「友人は処刑された/Melosは間に合わず」に改変 | FAIL(ending) |
| F6 因果反転 | 王の改心の理由を「信頼」から「恐怖/金銭」へ改変、またはMelosが約束を自分で破棄 | FAIL(causality) |
| F7 順序逆転 | 洪水・襲撃と約束の順序を入替 | FAIL(第1層order) |
| F8 外国人名違反 | 同一人物の姓名併記を含む | FAIL(名前ルール) |
- mock層(第2層をstubし、第1層と統合ロジックをテスト)で上記全件。**受入条件: F4〜F8すべてFAIL、F1〜F3すべてPASS**。食い違い(第1層FAIL×第2層PASS)=NEEDS_REVIEW のtestも含む。
- **実呼出**: 最低1回(F5結末改変をgpt-6-lunaで判定、FAILを確認)。推奨は**F1〜F6の6件を各1回(N=1)**(約¥2、第2層の判別能力が実証されない状態でProduction採用しないため)。結果は`er060_output/melos_production_e2e_01/validator_calibration_01.json`へ保存。

**改善**: 名前の有無でなく意味保持で合否を判定。改変はFAIL、名前省略の良稿はPASS。
**リスク**: (1)LLM判定のばらつき(N=1)→重大改変はmajor1件でFAILする保守設計+第1層hard規則との併用。(2)`validator_anchors`をSeed側データとして管理するため、新Story追加時にanchor作成が必要。(3)新構造のためOpus条件A対象。

## (d) 構成(Family C方式 + Story3分割 + Comment×3)

**問題**: 現行Zは構成が未確定(Preview/Comment1/IOLのみ生成、`build_family_c_episode_sequence`はComment1-3・IOLなしだがStoryはDialogue分割clip列)。決定①はStory 3分割とDialogue clip分割の区別を要求。
**変更**:
- **エピソード列(Family C `build_family_c_episode_sequence` L485をそのまま利用)**: Intro / Welcome / Topic intro / JA title / Notification1 / Preview intro / **Preview** / Notification2 / Key phrases intro / KP×5 / Notification3 / Full story intro / **Comment1** / **Story Part1**(clip列) / **Comment2** / **Story Part2** / **Comment3** / **Story Part3** / Outro。In One Line・Comment4・Literature Intro・REAL STORY/TRUE CRIME導入なし。`comment_after_segment_id={"2": Part1最終clip id, "3": Part2最終clip id}`をFamily C関数へ引数で渡す(関数は無変更)。
- **Story 3分割**: 場面・意味の転換点で分割。方式: `er062.split_story_into_parts(text)` = 段落に番号を付け、LLM(gpt-6-luna、1 call、約¥0.3〜1)が「2つの分割境界(段落番号)と各境界の意味転換の理由」をJSONで提案 → **決定論検証**(境界は段落境界のみ、各Partが全体語数の20〜45%、Part1<Part2<Part3順、境界直後に新場面の手掛かり[時間・場所・状況変化]が提案理由に含まれる)。検証NGは1回再提案、再NGでSTOP(**固定語数フォールバックはしない**=決定①)。分割結果と理由を`segment_plan.json`に記録。→ **新規構造のためOpus条件A対象**。代替案(Writer出力に場面マーカーを埋め込む)は、Writerの出力契約を増やし来歴検証が複雑になるため不採用。
- **Dialogue clip分割は別層**: 各Partを`fam_c.split_into_paragraphs`/`build_flat_voice_chunks`/`plan_story_segments`(無変更再利用)で話者別clip化。clip id=`full_story_part{n}_c{k}`。Part境界をclipが跨がない(planner呼出をPart単位で行う)。
- **Std Comment(日本語)**: `fam_c.generate_family_c_a2_comment(client, n, article, content_facts, ...)`(n=1〜3、品質retry内蔵)を再利用。`content_facts`/`scene_transition`はZ側で用意するが、Melos固有文字列のハードコード(現`generate_family_z_comment_1`内)をやめ、(c)の`seed_elements`から生成(ValidatorとAnchor共用=重複機構を作らない)。「理解を助ける具体的内容」は既存Family C Contract(understanding-guide、banned phrase)に従う。**Adv Comment/Preview(英語)**: X B1の`b1s.COMMENT_1_ROLE`/`COMMENT_2_ROLE`/`plan.FAMILY_X_B1_COMMENT_3_ROLE`と`b1s.PREVIEW_ROLE`を無改変再利用(model=X `_b1_support_model()`相当のroutingキー、新規キー不要)。Comment4は呼ばない。
- **Preview**: Std=日本語(現`generate_family_z_preview`再利用、「A2レベル」文言のみ新稿に合わせ要確認)、Adv=英語(X B1 PREVIEW_ROLE)。Previewは`comment_1/2`を材料にするX方式のため、生成順は Comment1→2→Preview。
- **Key Phrase**: 新稿から両レベルで`scaffold.run_key_phrases(article, kp_dir, id, level, process=None)`(Strategy L=Zの既存設定、DB Hybridは使わない)。Advancedは英語解説(W4機構、Variant B、`er019 _generate_key_phrase_segments_b1`系)を共有module経由で付与。旧`kp_4plus1_evidence_01/melos_a2/`は再利用しない。
**改善**: 決定①どおりの構成を既存関数の組合せで実現。
**リスク**: 3分割境界の自動決定は新規ロジック。短い物語で場面転換が少ない場合に検証NGになりうる(STOP時は人間が境界を指定する手順を別途用意)。

## (e) Dialogue Voice

**問題**: (1)王(ruler)の台詞の一部がキーワード不在でnarratorに落ちる、`friend`未登録(Phase A 2-E)。(2)`resolve_narrative_role`が`full_story_part1/2/3`完全一致のみで、Part内の複数clipがConnected Speech/Secondary ASR role gating(`er006_secondary_asr_01.py` L611-613、`er006_preprod_hardening_01_validation.py` L1156もsegment_idで再解決)の対象外になる。
**変更**:
- 判定: Family C `classify_quote_voice_window`+`voice_keywords`(無変更再利用)。`STORY_REGISTRY`のkeywordsを拡張(selinuntius:[selinuntius, friend]、dionysius:[dionysius, ruler, king, tyrant])。voice割当は決定済み(narrator=Aoede、Selinuntius=Erinome、Dionysius=Charon)をそのまま使用。Melosの台詞はnarrator声(Phase A確認事項、Z-4どおり新Voice仕様は作らない)。
- override: (i)`dialogue_attribution_report.json`を毎回生成(全引用符の周辺80字・判定voice・根拠)。(ii)自動検査: 引用符paragraphで、判定がnarratorかつ周辺に発話動詞+主語代名詞もMelos名も無い「話者不明」引用を検出。(iii)話者不明引用は、`fam_c.build_flat_voice_chunks`既存引数`quote_voice_override_paragraphs`で上書き。overrideの値は、LLM(gpt-6-luna、各レベル1 call、約¥0.3)による話者判定を**決定論判定と照合**して決める: 一致=確定、不一致=`dialogue_override.json`に両案を記録してSTOP(自動で採用しない)。(iv)ユーザー試聴で最終確認。
- **Connected Speech用segment_id(CR-B4/B5)**: 採用案=**`er020.resolve_narrative_role`へ後方互換の正規表現追加**: `re.fullmatch(r"full_story_part[1-3](_c\d+)?", segment_id)`をFULL_STORYに追加(既存の完全一致3種・`point_one/two`は不変、Xは`_c\d+`付きIDを生成しない=X挙動は変化しない)。比較した代替案: Z側aliasで`connected_speech_enabled_for("full_story_part1")`の戻り値だけ渡す方式は、Secondary ASR/Gate層がsegment_idで再度role解決する(`er006_secondary_asr_01.py` L613)ため**検証層で解決されず**不十分。Part内を無理に3clipに束ねる案はDialogue別Voiceと矛盾。→採用案。単一担当でer020を編集し、`run_project_regression.py`+X関連testで回帰確認(S8競合回避)。
**改善**: 誤voice割当の可視化・補正、Part内全clipがConnected Speech/ASR gating対象になる。
**リスク**: er020は共有層(影響範囲=`resolve_narrative_role`/`connected_speech_enabled_for`の全呼出元)。既存ID不変+新規パターンのみのため低リスクだが、Opus条件A対象。

## (f) TTS / Assembly

**問題**: `stage_tts`/`stage_assemble`は`NotImplementedError`。Family C旧TTS入口にはresolver/Flash-Lite/Role Styleが無い(Phase A 2)。
**変更**(`er063_family_z_audio_01.py`):
- **Narrator Story clip**: X `generate_a2_segment_with_slowdown`(Std)/`generate_english_segment_with_fallback`(Adv)を、`tts_backend="speech_metadata_flash_lite"`、`enable_connected_speech_equivalence_layer=connected_speech_enabled_for(clip_id)`(er020追加後はTrue)、`enable_repetition_qa=True`、`tts_safe_news_en`(斜体等記号正規化、PRODUCTION_WIRED)、Pronunciation Resolver有効、Primary/Secondary ASR・attempt cascade(標準2→fallback1→cool-down→Local Rewrite)を内蔵のまま利用(Xと同じ入口、独自に上限回数を変えない)。
- **Dialogue clip**: `bvoices.generate_voice_body_wide_margin`(Std=`..._with_a2_slowdown`)、voice名=`voice_tts_names_plan`。従来Dialogue Style(PD8を無条件適用しない)。resolver/正規化は同関数の対応範囲を実装時に確認し、不足があればclip投入前のテキスト前処理(`tts_safe_news_en`)と事後ASRで補う(共有関数は改変しない)。
- **Role→Style表(Family Z専用Production定数、`er063`内、`FAMILY_Z_ROLE_STYLE_VERSION`でreuse判定)**:
| Role | Standard | Advanced | 値の出典(逐語転記・sha照合) |
|---|---|---|---|
| Narrator Full Story | PD8 + A2減速指示 + 6%減速 | PD8 | `prompts_pace_02.md`(sha `329ff46a5ec3877f…`)。Std連結形式はCoffee Std v3と同一(`n3_tts.A2_SLOWER_PACE_INSTRUCTION`連結) |
| Dialogue clip | 従来Dialogue(Std=`A2_ENGLISH_STYLE_PREFIX_SLOWER`+6%、Adv=`ENGLISH_STYLE_PREFIX`既定) | 同左(Std/Advの差のみ) | 既存関数の既定値(新style考案なし) |
| JA Preview / Comment | R2(Aoede) | - | `prompts_R.md` R2(sha `625826c1187b6381…`) |
| EN Preview | - | E1(Charon): "calm, composed news anchor; steady and unhurried, clear and natural." | `er057_tone_trial_tts_gen_01.py` L65-66 |
| EN Comment | - | E2_UPBEAT(既存承認): "warm, upbeat and engaging; ..." | `er053_output/tts_voice_tone_brightness_trial_01/tone_trial_01.py` L39 |
| Key Phrase 英語 | K2 | K2 | Coffee evidence(`er057_ja_aoede_style_trial_02.py`の`g.C_SPECS`系。原典sha照合) |
| Key Phrase 日本語意味 | M2 | - | sha `e7617e15c29e43cb…` |
| Key Phrase 英語解説(Adv) | - | `KEY_PHRASE_EXPLANATION_EN`(既存、Xと共通) | `er033` |
| shell(Intro/Welcome/Preview intro/Full story intro/num/Notification等) | 既存Master Store再利用 | 同左 | 変更なし |
| topic_intro / japanese_title | 既存承認(変更なし) | 既存承認 | 変更なし |
  Style実装形態: `er063`内の**Family Z role style定数**として追加(Coffee限定のX定数`FAMILY_X_ROLE_STYLE_EN`は変更しない。OPEN-300=記事別override層とは独立)。Coffee限定承認とFamily Z採用は**別記録**(CURRENT_SPEC/DECISION_LOGに記載)。値は実装時に原典ファイルからsha256照合して転記し、一致しなければSTOP。
- **resume/reuse**: Xの`_generate_or_reuse`(`er019_..._audio_production_runner_01.py` L406、cached canonical_text+style_version一致のみ再利用)を再利用。Zの`style_version`=`FAMILY_Z_ROLE_STYLE_VERSION`。
- **Assembly**: `fam_c.build_family_c_episode_sequence`をclip列+`comment_after_segment_id`で呼ぶ(L485、無変更)、`assemble_mod.assemble_with_timeline`/`apply_headroom_safety_valve`/`convert_all_to_mp3`/`write_evidence_player`をFamily C runnerから呼ぶ。両レベル(std/adv)を別episodeとして組立。
- **Audio Validation Gate**: `verify_episode_audio_validation_gate(out_dir, level_string, required_structure)`。Zの`required_structure`(Part1-3の各clip必須、Comment1-3必須、KP5、shell)を新規定義。StdはlevelをA2系として**6%減速必須チェック**を有効化(OPEN-276型の穴を塞ぐため、Human Review経由採択clipにも最終段で減速後ASR+Gateを実行するtestを含める)。
- **日本語**: JA Preview/Commentは`generate_a2_japanese_with_reading_safety`(X既存、SCG・日本語Primary ASR)にR2を`style_prefix_override`で渡す。
**改善**: Production正式機構(Flash-Lite/resolver/Connected Speech/ASR cascade/Gate)でZが量産できる。
**リスク**: (1)backend混在(narrator=flash-lite、dialogue=従来経路)による音色/音量差→assembleのgain正規化+ユーザー試聴。(2)Dialogue短clip(3〜6語)のASR連続NG→human review queue/STOP(上限回避しない)。(3)Std英語全clipへの6%減速一律適用(CR-B15)。

## (g) Production経路(`er026`)

- **stage順序**: `rights → writer_adv → validate_adv → level_adjust_std → validate_std → split_story → support_text(Comment1→2→3→Preview、両レベル) → keyphrase(両レベル) → tts(両レベル) → assemble(両レベル) → gate/player`。CLI: `--stage writer|validate|split|support|keyphrase|tts|assemble|all`、`--level std|adv|both`、`--regenerate-stage <stage>`、`--only-clips`、`--budget-jpy`(既定300)、`--resume`(既定ON、sha一致のみ再利用)、`--dry-run`(副作用ゼロ、既存契約維持)。
- 旧`--stage text`(Trial story.md読込、IOL生成)は量産経路から外す(関数は残し`legacy`注記、既存test互換)。
- **BudgetGuard**: 上限¥300(現コード¥200/WARN¥150を差替、WARNは¥200)。各call前に`check_before`、累計+次call保守見積が上限超なら実行前STOP。実績はraw usage logから`compute_actual_cost_jpy`(model別単価、fail-closed)。
- **retry/fallback/regeneration/resume整合**: LLM=技術retry最大1(parse不能等)、品質retry=Validator FAIL時にその鎖を1回だけ再実行、2回目FAILで`USER_DECISION_REQUIRED`としてSTOP。TTS=既存cascade(標準2→fallback1→cool-down→Local Rewrite→human review)をそのまま使い、Z側で上限/Gateを緩和しない。resume=sha一致のみ再利用。regenerate=明示指定のみ、下流staleは警告のみ(自動再生成しない)。
- DEV/Trialスクリプト(`er059`等)にimport依存しない(Prompt/定数はZ module内に正式化、Trial②への依存は参照記録のみ)。
- **runtime evidenceに必ず出す項目**: 各stageのrouting key、要求model/actual model_id/effort、stage別cost、Style(role→style名→prompt sha)、voice名、attempt履歴、provenance sha chain、Validator verdict(第1層/第2層)、segment_id→role→connected_speech_enabled表、Gate結果。

## (h) tests(新規)

| test | 対象 | 方式 |
|---|---|---|
| `er061_..._validator_test_01.py` | (c)のF1〜F8、統合ロジック、NEEDS_REVIEW | fixture+mock(+実呼出smoke別) |
| `er062_..._writer_test_01.py` | R0→R1→R2の呼出順・model_id不一致STOP・sha chain生成/再開一致/不一致STOP・Std Prompt sha assert・Std同一本文FAIL・語数Gate | mock LLM |
| `er063_..._audio_test_01.py` | Role→Style表(sha照合・Std/Adv差・Dialogueへ PD8が付かないこと)、segment_id→role表、Dialogue override(話者不明引用の検出/不一致STOP)、`_generate_or_reuse`のstyle_version不一致時再生成、sequence順序(Comment1-3位置・IOL/Comment4が無い)、Gate required_structure、6%減速必須(Human Review経由含む) | mock TTS |
| `er026_..._test.py`(既存19件) | stage順序・`--regenerate-stage`・budget¥300・dry-run副作用ゼロ・名前系testの更新 | 更新+新規 |
| `er020`関連 | `resolve_narrative_role`: 既存ID不変(全既存ID表を固定)、`full_story_part2_c3`がFULL_STORY、`full_story_part4`/`foo_c1`はNone | 既存er020 testに追加 |
| 回帰suite | `python run_project_regression.py`(er0*_test_*.py全件)、Family C(er013)・Family X(er019)・Gate(er003)関連test、実行して全PASS確認 | 実行 |

## (i) 費用概算(上限¥300)・時間・並列化

換算1USD=160円、Sol $2/$10 per 1M、Luna $0.1/$0.5 per 1M(`pricing_snapshot.json`)。TTSは直近実測約¥0.86/clip(Flash-Lite、ASR込み)。Trial②実績: Sol 3 call約¥9〜12。
| 項目 | 内訳 | 概算(円) |
|---|---|---|
| Writer Adv(Sol R0/R1/R2、effort high) | 3 call | 9〜12 |
| Level adjust Std(Sol) | 1〜2 call | 3〜6 |
| Validator第2層(Luna) | Adv/Std/Std vs Adv 各1〜2 call | 1〜2 |
| Validator calibration(実呼出6件) | Luna 6 call | 約2 |
| Story 3分割境界提案(Luna) | 2 call(両レベル)+再提案余地 | 1〜3 |
| Dialogue attribution(Luna) | 2 call | 1 |
| Std JA Preview+Comment1〜3 | 4 call | 約12 |
| Adv EN Preview+Comment1〜3 | 4 call | 約12 |
| KP選定(Strategy L、両レベル)+Adv解説 | 2〜3 run | 20〜46 |
| TTS: Std約28 clip+Adv約28 clip | 56 clip×¥0.86 | 約48 |
| TTS retry/cascade余地(約30%) | | 約15 |
| Azure Secondary ASR(不一致時のみ) | | 0〜5 |
| **合計(中央〜上側)** | | **約125〜175** |
| 上振れ(Writer鎖+Std調整の再実行1回、KP高め、retry多め) | | 約215〜245 |
上限¥300に対し中央想定は余裕がある。¥300到達見込みでSTOP。¥200で警告。Risk Flagger(X専用)はZに無く費用なし。**設計・実装・mock test段階の追加API費用は0、実呼出はValidator calibration約¥2〜smokeのみ**、E2E実行は別途Go。
所要時間(見込み): 実装(runner/validator/audio)各0.5〜1.5セッション、E2E(Writer 〜15分、KP/support 〜15分、TTS Batch待ち 30〜90分)、試聴準備。**並列化**: validator(er061)・writer(er062)・audio(er063)は別ファイルで依存が少なく並行実装可(共有はroutingキー追加とer020の1行のみ=先に単一担当で完了させる)。`er026`は最後に統合。E2Eの両レベルTTSは条件同一のまま2プロセス並列可。直列必須: Writer→Validator→split→support/KP→TTS→assemble→Gate(前工程出力依存)、er020編集(共有層、単一担当)。

## (j) リスク・STOP候補・Dangling予測

| # | リスク/STOP候補 | 対処 |
|---|---|---|
| R1 | Validatorの判別能力が未実証(LLM層) | calibration 6件を受入条件に。NG=Production配線せずSTOP |
| R2 | Std調整で魅力/自然さ低下 | appeal項目+ユーザー試聴。Std FAIL2回でSTOP |
| R3 | Story 3分割の境界検証NG | 人間指定手順。固定語数分割はしない |
| R4 | Dialogue短clipのASR連続NG | 既存cascade/human review。上限回避しない=STOP |
| R5 | backend混在の音色/音量差 | gain正規化+試聴 |
| R6 | er020共有編集の影響 | 後方互換正規表現のみ、回帰suite実行 |
| R7 | Style原典のsha不一致(R2 vs P2表記、E1/E2/K2逐語) | 不一致でSTOP(OPEN-303) |
| R8 | 予算超過 | 実行前保守見積STOP、¥200警告 |
| R9 | Opus条件A指摘(3分割方式、Validator構造、er020、Role style定数) | 実装前にOpus独立レビュー必須 |
| R10 | OPEN-276型(Human Review経由で6%減速未適用)がZ Stdで再発 | 最終段で減速後ASR+Gate(testで担保) |
| R11 | CR-B2解釈(保留解除)が誤り | Fable確認後に実装着手 |
Dangling予測: (1)旧`check_character_name_rule`等を参照するtest・docs、(2)`generate_family_z_in_one_line`の呼出元(量産経路から外す)、(3)`STORY_REGISTRY.japanese_title_text`の副題(新稿題名と同期)、(4)`BudgetGuard`既定値(¥200→¥300)の参照箇所、(5)CURRENT_SPEC Z-3文言(superseded注記済み)、(6)旧`er035_output/kp_4plus1_evidence_01/melos_a2/`(再利用しない旨の注記)、(7)Z-4追記の`voice_keywords`(拡張に伴う更新)。実装完了時に`Grep`で参照整合を確認する。

## 実装順(推奨)
1. routing key追加+er020正規表現(単一担当、先行)→回帰suite。
2. 並行: er061(Validator+calibration)、er062(Writer+sha chain、mock)、er063(Style表+Dialogue override+TTS+assemble、mock)。
3. er026統合・dry-run・budget testsを経て、**Opus独立レビュー(条件A)→Fable照合→(ユーザー承認不要の範囲で)実装→E2E実行(別Go)→試聴**。
