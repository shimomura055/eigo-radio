# FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01 E2E_PLAN_01(委任_01、2026-10-21、JPY0・有料API呼出0・`--mode real`未起動)

Status: `PHASE1_SEED_RIGHTS_REGISTRY_DRYRUN_READY_PENDING_FABLE`。性質=既存Family Z正式Production経路による新規作品制作の準備(新仕様Trialではない)。実走は委任_02(Fable照合後)。

## §0 T-0 / ユーザー指示原文 / stop_scope
- 委任文逐語保存: `docs/pm/delegation_log/2026-10-21_FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01_委任_01.md`(13,842文字、sha256=149f1b121c41a62693761772d434bc2a45ef89b0e4319daaef17a703d4dcaa67、`extract_delegation_from_jsonl_01.py --index 192`)。`check_delegation_prompt.py`結果=`status=FAIL`(理由1件=固定見出し「事前指定Grep一覧+追記位置・更新位置の手順」の語が委任文では「事前指定Read/Grep一覧」表記のため欠落判定。内容上は事前指定Read/Grep一覧節あり。警告4件[TTS差分再生成言及・KPI provenance・Opus台帳・QDC記録]は本委任[JPY0・準備]に該当しない)。チェック結果JSON=同名`_check.json`(`..._委任_01.md_check.json`)。
- ユーザー指示原文逐語保存: `docs/pm/delegation_log/2026-10-21_FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01_USER.md`(先頭2行ヘッダ込み3,003文字、sha256=3517c47f1d2d15ac3042c8b5349d04f0fe235f552aebb2b49f55c4fed4d0a3cf)。原文本体(「原文ここから/ここまで」の間)は委任文から機械抽出(打ち直しなし)。
- stop_scope_check(`--managed-id FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01 --run-dir ...\the_open_window\run_e2e_01`、run-dir未作成の状態): rc=0・`stop=false`・適用NOTICE0(既存Melos NOTICE 1件は`a_status_inactive`で非適用)。出力=`er026_output/family_z_production_e2e_01/_stop_scope_check_ow_01.json`。`tools/stop_scope_check_01.py`は管理IDを`--managed-id`引数としてNOTICE本文の語照合に使うだけで、管理IDの事前登録は不要(Grep `managed.id|MANAGED`: L12,108,169-232)。監査記録の管理IDはrunnerの`ctx.management_id`(STORY_REGISTRY)が`summary`/`dry-run plan`/er063の`style_record`・`tts_generation_results.json`へ書く。

## §1 原作Seed・権利Gate記録
### 1-1 原作本文(一次資料を直接取得)
- 取得元: Project Gutenberg eBook #269 *Beasts and Super-Beasts*(Saki、1914年短編集)。`https://www.gutenberg.org/cache/epub/269/pg269.txt` HTTP 200(`curl.exe -sSL -w "%{http_code}"`)、`https://www.gutenberg.org/ebooks/269` HTTP 200。取得日時=2026-10-21T08:23:38+09:00。
- 抽出: `pg269.txt` L1256-1399(見出し`THE OPEN WINDOW`〜次作`THE TREASURE SHIP`の前)。生抽出=`er026_seeds/the_open_window/source_gutenberg_raw_extract.txt`。
- `er026_seeds/the_open_window/story.md`: 先頭`### The Open Window`、本文は原文のまま(**空白正規化のみ**: 行頭折返しを連結・連続空白を1つに・段落は空行区切り。語・語順・句読点は不変。testで生抽出と語列一致を検証)。**29段落・1,208語**。sha256(story.md)=`ead6768174a07f6cfe6506b65236ae6e9109dc1a2eb5a1ba9f4a02351023438b`、生抽出=`5009fa9e74f5df1b2ef8934e96ab72f0d6160fd2366332983354644781c10c5a`、`pg269.txt`全体=`058d0cda5a3c8449cbce06e0698048251881be4c6fc8d06fd0bc3a1bb8ec8587`。詳細=`SOURCE_PROVENANCE.json`。
- 使用しなかったもの: 検索要約・Wikipediaの梗概・現代の第三者翻訳/翻案(原文のみから`seed.json`を自作)。
- Production seed置き場(Writerが参照): `er026_output/family_z_production_e2e_01/the_open_window/seed/{seed.json,primary_text_excerpt.md(=story.md全文),SEED_PROVENANCE.json}`(Melosと同形式。er061 `validator_anchors`は撤廃済みのため無し)。`stage_seed_check`のsha突合でdry-run/mock通過を確認。
### 1-2 日本国内権利Gate(`OPEN_WINDOW_RIGHTS_BLOCK`、runner L179-225)
| フィールド | 値 | 出典(確認2026-10-21) |
|---|---|---|
| author | Hector Hugh Munro(筆名Saki) | Gutenberg #269 / en.wikipedia.org/wiki/Saki(HTTP 200) |
| author_death_date | 1916-11-14(Beaumont-Hamel、フランス) | en.wikipedia.org/wiki/Saki(HTTP 200、infobox「Died 14 November 1916」) |
| jp_public_domain_basis | 旧法=死後50年(没年の翌年起算→1966-12-31満了)+戦時加算3,794日(英国=連合国、1941-12-07以前取得の著作権、昭和27年法律第302号)=**1966-12-31+3,794日=1977-05-21に日本で保護満了(計算値)**。2018年70年化は1999〜2018-12-29に満了済みの作品に遡及しない→日本でPD | en.wikipedia.org/wiki/Copyright_law_of_Japan(HTTP 200: 「wartime…3,794 days (including…United Kingdom…)」「not applied retroactively; works that had entered the public domain between 1999 and 29 December 2018」)、ja.wikipedia.org/wiki/著作権の保護期間(HTTP 200: 戦時加算「イギリス…3794日…1978-12-31満了→1989-05-21」の例。同式で検算: 1978-12-31+3,794日=1989-05-21を確認)、同 戦時加算(HTTP 200)/連合国及び連合国民の著作権の特例に関する法律(HTTP 200) |
| source_url | `https://www.gutenberg.org/cache/epub/269/pg269.txt`(+card=`/ebooks/269`) | HTTP 200 |
| confirmed_date | 2026-10-21 | - |
| us_copyright_status_record_only | 1914年出版=1931年より前=米国PD(記録事項、必須条件ではない) | copyright.cornell.edu/publicdomain(HTTP 200、「Before 1931 … In the public domain」) |
| legal_use_basis | Melosと同じユーザー決定(2026-09-26、`FICTION-FAMILY-Z-RIGHTS-RECHECK-01_REPORT.md` §6)の(1)〜(5)と採用文を逐語転記。Melos固有文(「走れメロスは…差し替え不要」)のみ省略 | REPORT §6(L252-261) |
| gate_reference | REPORT §6 + 本管理ID | - |
- 疑義の有無: **残らず**(没年・本人の国籍[英国=連合国]・出版年[1914=開戦前]・満了日[1977-05-21]が全て日本の旧50年+加算の範囲で、2018年改正の非遡及にも該当)。**法的最終判断ではない**(記録は計算と出典のみ)。注意として、ja.wikipediaの戦時加算の例示日付は一般例で、Saki個別の満了日は上記の計算値(3,794日の加算式は出典例で検算済み)。
- `check_rights_gate(OPEN_WINDOW_RIGHTS_BLOCK)`: `RIGHTS_REQUIRED_FIELDS`7項目全充足でPASS(test `RightsGateTest`)。欠落時は`RightsGateError`(fail-closed、test済み)。
- 第三者翻訳・翻案の流用なし(Writerは自作`seed.json`のみ入力、原文は`primary_text_excerpt.md`で出所保持)。

## §2 Story品質基準充足表(CURRENT_SPEC「Family Z(Fiction)」項目3(d)、基準定義=`FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02_REPORT.md` L33-41)
| 基準 | 判定 | 根拠(原文確認箇所) |
|---|---|---|
| A 中心となる出来事・変化 | PASS | 少女Veraが訪問客Framtonに「開いた窓」の悲劇(叔母の夫と二人の弟が3年前の今日、窓から狩りに出て沼に呑まれた)を語る→叔母が窓を見ながら夫たちの帰りを待つ様子で話が裏付けられる→夕暮れに3人の人影と犬が窓へ近づき歌が聞こえる→Framtonが逃走→少女が犬への恐怖という作り話でごまかす |
| B 関心維持(Hook・緊張・意外性・皮肉) | PASS | 冒頭から不気味な語り、伏線(窓・白い防水コート・『Bertie, why do you bound?』の歌・茶色のスパニエル)、人影が現れる緊張、最後の種明かしと少女の巧みな嘘のブラックユーモア |
| C 意味のある展開・余韻 | PASS | 最終行「Romance at short notice was her speciality.」で、語りの全体が少女の即興の作り話だったと反転し余韻を残す |
| D 短編化しても魅力が残る | PASS(条件付き) | 原文1,208語→目標400語(約1/3)。魅力は文体の長い心理描写より構造(伏線→裏付け→人影→逃走→ごまかし)にあり、窓・コート・歌・犬の4つの伏線と最後の嘘を残せば成立。圧縮対象は訪問客の背景説明・叔母の雑談(`seed.json` `discarded_elements`) |
- 4項目中4項目充足(原則3以上)。Seed必須条件(a)原文直接確認=Gutenberg(上記)、(b)日本国内PD=§1-2、(c)中心Story保持=上表+`seed.json` `conversion_plan`、(d)検索要約だけをSeedにしない=原文から自作。
### 2-1 ユーザー§2「守るべき魅力4点」「結末の意外性を損なわない」のWriter入力への記録
- 既存の渡し口=`seed.json`の`seed_elements`(R0 `[Story Seed]`箇条書き)と`conversion_plan`(R0 `[How to convert it]`)。**新Prompt文は作っていない**。`seed_elements`6点に(1)少女の不気味な話と訪問客の心理(2)窓の伏線(3)人影の緊張(4)種明かしと嘘のユーモアを入れ、`conversion_plan`に「中心Story・人物関係・因果・結末を維持」「結末前に仕掛けを説明/示唆しない」「伏線を削らず訪問客の背景と叔母の雑談で圧縮」「最後の行の後に教訓・解説を足さない」を記載した。
- Familyの人物名方針(Writer Prompt `REVISE_USER_TMPL`、主人公のみ固有名・外国人名はFirst/Last一方のみ)の本作適用案(1行): 固有名は主人公**Framton Nuttel**のみ、他は役割語(the girl/her niece, her aunt, the aunt's husband and two brothers)。`REVISE_USER_TMPL`の「only <名前> may have a personal name」の名前部分はStory名差替えのみで`Framton Nuttel`に置換(§3)。
### 2-2 Fable CPの照合観点(委任_02の text stage 後、TTS前に確認する観点)
1. 少女が語る不気味な出来事と、信じる訪問客の心理が残っているか(訪問客が「信じて怯える」過程)。
2. 開いた窓の伏線(窓が開いている理由・毎晩夕暮れまで開けておく・白いコート・Bertieの歌・茶色の犬)が人影の場面で回収されるか。
3. 人影が現れる場面の緊張(三人・銃・夕暮れ・無言で近づく→歌)が保たれているか。
4. 最後の種明かしと少女の巧みな嘘(犬への恐怖という作り話)のユーモアが残り、**結末の前に嘘だと分かる説明や示唆がない**か、最後の行の後に解説が追加されていないか。
5. Standard/Advancedで中心Story・結末が変わっていないか。
- 要注意(Fable判定事項): CURRENT_SPEC 2026-10-12追記④(Family Z編集方針=エッセンス優先・原作と異なる展開も許容、旧「原作保持条件」はWriter Prompt `R0_BLOCK_PRESERVATION`へ置換)と、ユーザー2026-10-21指示§2(中心Story・人物関係・因果関係・結末を維持)は文言上の強さが異なる。既存Promptは変更しない前提で、上記は`seed.json`のデータ側で担保した。text stage後の観点1〜5でNGなら、Prompt変更ではなくFableが11-6で扱う(新仕様候補)。

## §3 Melos固有ハードコード棚卸しと変更差分
### 3-A 棚卸し表(Grep `melos|Melos|MELOS|メロス|selinunt|dionys`、現在の行番号)
種別: C=コメント/docstring、K=定数(story別値)、P=Prompt文、B=分岐/ロジック、T=test fixture/mock、L=legacy(Phase 1経路、E2E非使用)。対応: ✓=実装(Melos不変)、D=設計案のみ(実装せず)、-=変更不要。
| ファイル:行 | 種別 | 内容 | 対応 |
|---|---|---|---|
| er026 runner:128-176 | K | `MELOS_RIGHTS_BLOCK`(Melosの権利) | -(`OPEN_WINDOW_RIGHTS_BLOCK`をL179-225に追加) |
| er026:234-260 | K | `STORY_REGISTRY["melos"]`(+新keys `e2e_management_id/e2e_theme_tag/e2e_pages_dir/page_title_ja/audio_file_prefix`) | ✓ |
| er026:261-290 | K | `STORY_REGISTRY["the_open_window"]` | ✓ |
| er026:332-374 | L | `check_character_name_rule`/`restore_character_names`(SUPERSEDED、E2E非使用) | -(Phase 1 test互換のみ) |
| er026:654-657,742-743 | L | Phase 1 `run_text_stage`/`run_keyphrase_stage`の日本語Prompt断片・plan note | -(legacy `--stage text/keyphrase`専用。E2E非使用) |
| er026:899-902 | K | `E2E_MANAGEMENT_ID/E2E_THEME_TAG/E2E_PAGES_DIR` | ✓(定数名は維持し、値は`STORY_REGISTRY["melos"]`から取得=Melos値不変) |
| er026:1000-1005,~1016-1024 | B | `E2EContext`(`pages_dir`既定None→registry、`management_id`/`theme_tag` property、`stage_context`のtheme tag) | ✓ |
| er026:1087,1102-1109 | C/B | `stage_seed_check`の`check_melos_voice_mechanism`呼出(Voice機構の一般確認。結果key名`melos_voice*`) | -(機構確認でstory依存でない。出力key名のみMelos由来) |
| er026:1181 | P/B | `_check_plan_after`のSTOP文言「Melos・王・友以外の話者」 | D(文言のみ。§3-C) |
| er026:1788,1799 | B | dry-run `pages`行の表示文字列 | ✓(`ctx.pages_dir`から生成。Melosは従来表記と同一) |
| er026:~1568 | B | `stage_pages` → `a63.build_pages(..., page_title, audio_file_prefix)` | ✓ |
| er026:1761 | B | `run_stages`が`a63.MANAGEMENT_ID`をctxの値に設定(監査記録用) | ✓ |
| er026:1834,1842 | T | mock話者判定が判定不能時`melos`を返す | ✓(委任_01b: story別fallback) |
| er026:~1970,2045 | B | `build_mock_context(story_key, slug)`、`--story`既定 | ✓(mockが`--story`を無視してmelosのrun dirに書く不具合=**11-8修正**。下記) |
| er062 writer:43 | K | `THEME_TAG`(smoke/CLI用) | -(real runはrunnerの`ctx.theme_tag`でcost loggingを包む) |
| er062 writer:141 | P | `REVISE_USER_TMPL`「only Melos may have a personal name」 | ✓(Story名差替えのみ`{main_character}`化。Melosは**バイト同一**をtestで固定) |
| er062 writer:199-212 | P | `ATTR_USER_TMPL`(話者roster: melos/king/friend/other/narrator+例文) | ✓(委任_01b: story別化。§3-C) |
| er062 writer:221 | B | `ATTR_SCHEMA` speaker enum=`st.SPEAKERS` | ✓(委任_01b: `build_attr_schema(story_key)`) |
| er062 writer:387-388,596 | K/B | `check_adv_guardrails`の禁止名(WARNのみ)が`STORY_LINT_CONFIG["melos"]`固定 | ✓(`story_key`引数追加。Melos既定は同一) |
| er062 writer:869,1143,1161-1164 | C/T | カタカナ除外コメント・mock・smoke文言 | -(Melos用smoke/mockはtest fixture) |
| er062 writer:1283 | B | CLI `--story` 既定melos | - |
| er062 structure:21,24-28 | K/B | `SPEAKERS`/`Z_VOICE_KEYWORDS`(melos/king/friend固定) | ✓(委任_01b: `STORY_SPEAKER_CONFIG`) |
| er062 structure:622-639 | K | `STORY_LINT_CONFIG`(story_key別、Preview/Commentのforbidden_names・spoiler語) | ✓(`the_open_window`のentry追加。既存機構の値) |
| er063 audio:35 | K | `MANAGEMENT_ID`(監査記録2箇所) | ✓(runnerが実行時にstory別へ設定) |
| er063 audio:42,1089,1439 | K | `DEFAULT_SLUG="melos"`(`story_key`既定。runnerは`ctx.slug`を渡す) | - |
| er063 audio:333-360 | K/B | `FAMILY_Z_DIALOGUE_VOICE_KEYWORDS/TTS_NAMES`・`SPEAKER_ALIASES`・`MELOS_VOICE_STATUS` | ✓(委任_01b。`MELOS_VOICE_STATUS`はMelos用のまま) |
| er063 audio:377-384 | B | `check_melos_voice_mechanism` | - |
| er063 audio:1492-1495 | K | `PAGES_DIR`(= `build_pages`既定) | -(Melos既定のまま。runnerは`ctx.pages_dir`を渡す) |
| er063 audio:1506,1556,1680,1734 | P/K | 試聴ページのタイトル`走れメロス`・音声ファイル名`Melos_*_full.mp3` | ✓(`page_title`/`audio_file_prefix`引数、既定=Melos従来値、test固定) |
| er063 page_verify:4-5 | C | usage例のURL | - |
| er067 trial:3,15,158,161 | T | Std Preview Trial(`lint_support_text(...,"melos")`) | -(Trial、E2E非使用) |
| tools/stop_scope_check_01.py | - | `melos`語のGrep該当0。管理IDは引数 | - |
### 3-B 実装した変更(ファイル:行、Melos不変の根拠)
- `er026_family_z_fiction_production_runner_01.py`: `OPEN_WINDOW_RIGHTS_BLOCK`追加(L179-225)、`STORY_REGISTRY`に`the_open_window`と全story共通の新keys追加(L234-290)、`E2E_MANAGEMENT_ID/THEME_TAG/PAGES_DIR`をregistry参照へ(L899-902、値は従来と同一文字列)、`E2EContext`(`pages_dir=None`→`__post_init__`でregistry、`management_id`/`theme_tag` property)、`stage_pages`/`describe_plan`/`summary`/`run_stages`/`build_mock_context`/`main`のmock分岐がstory別値を使う。
  - **11-8不具合是正(範囲内)**: 従来`main()`の`--mode mock`は`--story/--slug`を`build_mock_context`へ渡さず常にslug=`melos`のrun dir(`melos/<run>_mock`)へ書いていた(委任文「Melos run成果物に書き込まない」要件と矛盾、`--story`の意味と矛盾)。`story_key`/`slug`を渡すよう修正。Melos指定時の出力先は従来と同一(`melos/<run>_mock`)。
- `er062_family_z_writer_01.py`: `REVISE_USER_TMPL`の主人公名を`{main_character}`化(`STORY_MAIN_CHARACTER`)、`build_revise_prompt(body, story_key="melos")`、`check_adv_guardrails(..., story_key)`、`run_writer_chain`から`story_key`を渡す。
- `er062_family_z_structure_01.py`: `STORY_LINT_CONFIG["the_open_window"]`追加(同一機構のstory別値)。
- `er063_family_z_audio_01.py`: `build_pages`/`build_page_rows`/`build_listening_page_html`/`build_index_html`に`page_title`/`audio_file_prefix`(既定=Melos従来値)。
- **Melos不変の根拠(test)**: 新規`er026_family_z_story_registry_open_window_test_01.py`の`MelosUnchangedSnapshotTest`がパラメータ化前(HEAD dc0e40811)の値(管理ID・theme tag・pages dir・registry・voice表・`STORY_LINT_CONFIG["melos"]`・`REVISE_USER_TMPL`整形結果・ページタイトル・`E2EContext`既定のout/seed dir)を逐語固定。既存`er026*`/`er062*`/`er063*` test全PASS(§8)。
### 3-C 話者roster/Voice表のstory別化(委任_01b、Fable判定=11-8是正[Family Z仕様は一般仕様なのにMelos固定だった乖離]・Opus条件A非該当で実装)
**委任_01では設計案に留めた(§3-A表のD行)が、委任_01bでFableの判定を受け実装した。**
- **値の出所(一箇所)**: `er062_family_z_structure_01.py` `STORY_SPEAKER_CONFIG[story_key]`(speakers / z_voice_keywords / attr_roster_text / attr_caution_text / dialogue_voice_keywords / dialogue_voice_tts_names / speaker_aliases)。`er026 STORY_REGISTRY[story]["speaker_config"]`は同一objectの参照(二重定義なし)。er062 structureはer013のみimportの純粋関数moduleのため、er026⇄er062の循環importを避けるため出所をstructure側に置いた(registryが参照)。旧定数`SPEAKERS`/`Z_VOICE_KEYWORDS`/`FAMILY_Z_DIALOGUE_VOICE_KEYWORDS`/`FAMILY_Z_DIALOGUE_VOICE_TTS_NAMES`/`SPEAKER_ALIASES`はMelos値を指す互換aliasとして残置(testで`assertIs`固定)。
- **差分**: `er062_family_z_structure_01.py` L21-110(STORY_SPEAKER_CONFIG・`speaker_config()`・`speakers_for()`・互換alias)、`deterministic_attribution`/`reconcile_attribution`に`story_key`(既定melos)。`er062_family_z_writer_01.py` `ATTR_USER_TMPL`を`{roster_text}/{caution_text}/{tagged_story}`化+`build_attr_user_prompt`/`build_attr_schema`(L203-232)、`llm_attribute_quotes`/`attribute_dialogue`/`apply_human_confirmed_override`/`run_plan`/`stage_plan`に`story_key`(既定melos。従来`run_plan`のplan jsonの`story_key`は呼出側未指定のため常に"melos"だった不整合も是正)。`er063_family_z_audio_01.py` `normalize_speaker`/`resolve_dialogue_voice`/`build_level_plan`/`build_z_sequence`に`story_key`(既定melos)、Voice値`None`=未割当は`VOICE_UNASSIGNED`で`FamilyZVoiceMappingStop`(fail-closed、新Gateではなく値欠落の検出)。`er026`runner: registryに`speaker_config`、`stage_plan`/`write_speaker_table`/`stage_seed_check`(dialogue_voices)/`build_level_plan`呼出/mock attribution・`mock_writer_hook`が`ctx.story_key`で解決。
- **『開いた窓』roster**: `framton`(Algieba)/`vera`(Erinome)/`mrs_sappleton`(**None=未割当、ユーザー判断待ち**)/`men`(叔母の夫・弟Ronnie等+歌声、Charon)/`other`(想定外話者=Melos同様`FAMILY_Z_DIALOGUE_SPEAKER_OTHER`でSTOP、既存Gate不変)/`narrator`(Aoede)。委任文では「other=男性端役=Charon」とあったが、`_check_plan_after`の`other`→STOP Gate(判定ロジック不変の条件)と衝突するため、本設計案どおりkey名を`men`とし`other`は想定外話者のまま(判断候補ではなく委任文の条件「Gate・判定ロジックは変えない」を優先した実装判断)。
- **Lint config(承認済)**: `STORY_LINT_CONFIG["the_open_window"]`のspoiler語を結末先回りの最小限に縮小(ja: 作り話/でっち上げ/嘘/うそ/偽り/種明かし/ハッタリ、en: made up/made-up/invented/a lie/was lying/lied/tall tale/the truth is/romance at short notice/a hoax)。一般語(最後に/結末/turns out/in the end/the trick/a prank)は除外。forbidden_names=Sappleton/Ronnie/サプルトン/サップルトン/ロニー/ヴェラ(不変)。
- **Melos不変の根拠**: 新規`er062_family_z_speaker_roster_story_test_01.py`(16件)=旧`ATTR_USER_TMPL`展開結果・旧`ATTR_SCHEMA`・SPEAKERS・keywords(挿入順)・Voice表・aliasesを逐語固定。さらに**HEAD(65a1080d5)の4 moduleで`--story melos --mode mock --stage all`を実行した出力と、変更後の同mock出力を比較**: 314ファイル中、差は時刻・port・pid・run名のみ(wav/mp3/plan/attribution/speaker_table等すべてバイト同一)。
- **test結果(逐次)**: `er062*_test*.py` 95件(既存79+新規16)PASS / `er063*_test*.py` 84件PASS / `er026*_test_*.py` 129件PASS(失敗0)。
- **mock**: `--story the_open_window --run run_mock_02 --mode mock --stage all` rc=0 / `--story melos --run run_mock_02 --mode mock --stage all` rc=0(mockのWriter fixtureはMelos文なので『開いた窓』mockは配管確認のみ。speaker_tableはframton/vera等のroster語彙で出力)。
- **residual risk(委任_02 plan stage)**: 決定論話者判定はFamily Cのkeyword窓判定(substring一致、挿入順優先)のため、Framton/Veraが同一窓に現れる場合や`aunt`が`haunt`等に部分一致する場合にdeterministic≠LLMのmismatch→`FamilyZDialogueMismatchStop`(dialogue_override.json、人間確認)になり得る。既存機構の挙動でありMelosでも同様。

## §4 Voice割当案(『開いた窓』)
- 参照: CURRENT_SPEC Z-4(L1539-1553)=narrator=Aoede・登場人物=Erinome/Charon等。Melos run_e2e_02で実使用された承認済みVoiceは`Aoede`(narrator)・`Algieba`(Melos、`PROVISIONAL_UNAPPROVED`表記のまま21/21使用[CURRENT_SPEC L1694])・`Erinome`・`Charon`。
| 話者 | 案 | pool |
|---|---|---|
| narrator | Aoede | Z-4承認 |
| framton(訪問客、神経質な青年) | Algieba | Melos主人公で使用実績 |
| vera(15歳の姪) | Erinome | Z-4参照先 |
| men(叔母の夫・弟Ronnie。歌う声) | Charon | Z-4参照先 |
| aunt(Mrs. Sappleton) | **未割当** | 承認pool内で第2の女性Voiceが賄えない |
- `STORY_REGISTRY["the_open_window"]["voice_tts_names_plan"]`には上記4件のみ記載(plan only。§3-Cの理由でrunには反映されない)。Sappletonは判断候補(§9)。
- 人物名ルール(Prompt変更なし)の本作適用案: 固有名は主人公Framton Nuttelのみ(§2-1)。

## §5 工程表(委任_02用)
- 前提: Fable照合 → (推奨)委任_01b: 話者roster story別化(§3-C、JPY0) → `TTS_EXECUTION_MODE=STANDARD`。
- 事前: `.venv\Scripts\python.exe tools\stop_scope_check_01.py --managed-id FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01 --run-dir er026_output\family_z_production_e2e_01\the_open_window\run_e2e_01 --out <json>`(rc=3なら新規API呼出なしで報告。rc=0のみ続行)。
- **実走コマンド(real)**: `$env:TTS_EXECUTION_MODE="STANDARD"; $env:PYTHONIOENCODING="utf-8"; .venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --story the_open_window --run run_e2e_01 --mode real --stage all --approved-budget-jpy 300 --warn-threshold-jpy 200 --tts-execution-mode STANDARD`
- **起動回数の推奨**: 原作の伏線・結末の保持は完成条件3であり、TTS(約JPY27〜40)の前にFable CPで確認したほうが手戻りが小さい。案A(推奨)=1回目`... --stage all --stop-after kp`(writer→std_adjust→plan→support→kp、約JPY22)でFable CP(§2-2の観点1〜5)→OKなら2回目`... --stage all`(同run、provenance sha一致で上流を再利用)。案B=`--stage all`を1回。案Aは有料runの2回起動となるため、委任_02で「2回起動(計画的分割)」を明示許可すること(再起動規則[26節]の例外として明記が必要)。「不合理な日付分割・待機」にはあたらない(同日・連続実施、品質確認のための工程内CP)。
- 各stage前のSTOP確認: runnerは各stage前とAPI呼出前・各clip前に`<run>/STOP`・`STOP_ALL`を確認(`_stop_sentinel`)。外部のstop_scope_checkは各起動の直前に1回。
- Gate一覧(Melos run_e2e_03/06と同一): AUW(統一ASR/音声品質、Primary→Secondary→Local Rewrite→再検証) / Pronunciation Ledger+Azure Phrase List(重み2.0) / Std 6%減速(`verify_std_english_slowdown`、Dialogueは生成後6%減速のみ) / Voice assignment(`speaker_table.md`・`dialogue_attribution_*.json`) / Dialogue切替 / Assembly(`provision_shell`→`gate`→`assemble`) / Human Review Lock / Style sha(`style_record.json`) / SRC(`FAMILY_Z_SRC_UNRESOLVED`) / gloss HR / page_verify(`user_page_standard_check`)。
- STOP条件: 権利Gate不合格(`RightsGateError`)/ 累計費用が`--approved-budget-jpy 300`・警告200超見込み(`E2EBudget`がAPI呼出前にSTOP)/ Human Review Lock発火(Human Review待ち。再起動禁止、ユーザー承認記録後のresumeのみ)/ BLOCK / rc≠0の原因不明が2回(26-2)・外部停止 / STOPセンチネル・RESTART_STORM / stop_scope rc=3 / `FAMILY_Z_DIALOGUE_SPEAKER_OTHER`(§3-C未解消時)。rc≠0は再起動せずFableへ。
- 費用上限の出典: CURRENT_SPEC「Family Z(Fiction)」2026-10-12追記「費用上限: 本E2Eの追加API費用上限¥300」(L1604)、runner `E2E_APPROVED_BUDGET_MAX_JPY=300`/`E2E_WARN_THRESHOLD_JPY=200`、PM_GOVERNANCE 7-7(案件見積300円以下はAI自律)。推定上限を新設していない。

## §6 費用見積(出典付きのMelos実測のみを根拠、新規推定なし)
| 工程 | 見積JPY | 根拠(出典) |
|---|---|---|
| text(writer R0/R1/R2+std_adjust+plan+support+kp選定) | 約22.3 | Melos run_e2e_02実測 text 22.33(`FZ_COMPLETION_PLAN_01.md` §10-5)。語数目標400語はMelos run_e2e_03実測(408/387語)と同規模 |
| TTS/ASR(Adv+Std 全clip) | 約27.6〜40.2 | Melos run_e2e_06実測 27.58(tts_b1b 12.76+tts_a2 14.82、`MELOS_REGEN_RUN_E2E_06_RECORD_01.md`)〜run_e2e_02実測 40.17(tts_b1b 17.00+tts_a2 23.17)。run_e2e_03は36.38(tts 13.90+22.45) |
| 合計(期待) | **約50〜62(中心約56)** | 上記合算。量産目標70円/記事セットの範囲内、承認枠¥300・警告¥200に対して余裕あり |
- 原価増加要因(Melosとの差): (1)台詞密度が高い原作→Dialogue clip(gemini-2.5-pro-preview-tts)増加の可能性 (2)固有名詞が少なく[Framton/Nuttel/Sappleton/Bertie/Vera]Pronunciation Ledger新規登録・Secondary ASR頻度の差 (3)固定shell(Master Audio Store)は再利用想定=新規費用ほぼ0。上振れ見込みは+10〜15程度(LR/Secondary増)。**ここに新規の推定値はなく、Melos実測のレンジで置いた**。実費は実走後にstage別で記録する(`er026_fz_cost_17.py`相当の集計)。

## §7 試聴ページ要件
- 公開先: `user_test/family_z_open_window_01/`(`index.html`[ユーザー試聴ページ標準フォーマット]+`standard.html`/`advanced.html`[詳細確認]+`audio_standard/`・`audio_advanced/`)。URL(公開後): `https://shimomura055.github.io/eigo-radio/user_test/family_z_open_window_01/index.html`(`#std`/`#adv`)。**既存`family_z_melos_02`は上書きしない**(registry `e2e_pages_dir`)。
- 構成はMelos `family_z_melos_02`と同じ(`build_pages`+`er_user_listening_page_common_01`): (1)Standard/Advancedそれぞれ「全編を通し再生」(完成音声`OpenWindow_{a2,b1b}_full.mp3`) (2)Section別の全文原稿(再生順スクリプト表: Part1-3・Comment・Preview・Key Phrases各セクションの原稿、「全編のこの位置へ」ボタン) (3)Key Phrases(英語/日本語2列) (4)補助情報(ASR警告の事後試聴リスト、詳細ページ)。(A2)/(B1)/B1Bラベル非表示、`file:///`禁止。
- 公開前検証: `stage_page_verify`(Playwright `--local`)=`user_page_standard_check.overall=PASS`、全audio再生OK、console error 0。公開後はGitHub Pages実URLで再生確認(Melos §13と同手順)。完成後は`USER_LISTENING_PENDING`(Production完成とユーザー試聴PASSを区別)。

## §8 mock / dry-run 結果(JPY0)
- dry-run: `--story the_open_window --run run_mock_01 --mode dry-run --stage all` rc=0。`management_id=FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01`、`out_dir=er026_output/family_z_production_e2e_01/the_open_window/run_mock_01`、`pages_dir=user_test/family_z_open_window_01`、13 stage計画、preflight(seed_check)成功: `seed.json`=9abe50b85551、`primary_text_excerpt.md`=ead6768174a0、routing=Sol R0-R2/Std調整・luna(split/attribution)、Style表11キー、`er020_full_story_clip_pattern=true`、権利Gate PASS。副作用0(ファイル作成0)。
- mock: `... --run run_mock_01 --mode mock --stage all`(`TTS_EXECUTION_MODE=STANDARD`)。出力=`er026_output/family_z_production_e2e_01/the_open_window/run_mock_01_mock/`(316 files)。1回目は`timeout 110`で`page_verify`(Playwright、約162秒)途中でrunnerがkillされ(rc=124、RUN_LOCK残置)、2回目(再実行、provenance再利用)をrc=0で13 stage完走(seed_check/writer/std_adjust/plan/support/kp/tts_b1b/tts_a2/provision_shell/gate/assemble/pages/page_verify)。`spent_jpy=0.0`、`mock_api_calls.jsonl`117行(全mock境界)、実API呼出0。`page_verify_local.json` `user_page_standard_check.overall=PASS`、`index.html` plays_ok 37/37・console_errors 0、`seek_ok_all=False`はMelos run_e2e_03/05/06と同じ前例(mockの合成音)。ページタイトル`開いた窓 試聴(Standard / Advanced)`、音声ファイル名`OpenWindow_{a2,b1b}_full.mp3`、「走れメロス」文字列0件。
- mockのページ出力先は設計どおりrun dir配下`.../run_mock_01_mock/pages_mock/`(`user_test/`を汚さない既存設計。`family_z_open_window_01`の実体はdry-run planと`E2EContext`のtestで確認)。**Melosのrun・pages_dirへの書込0**(git status差分で確認: 本作業で`melos/`・`user_test/family_z_melos_02`の追加変更なし。着手前から存在した無関係な既存差分は触れていない)。
- **重要な限界**: mockのWriter/話者判定/KP候補は内蔵のMelos fixture(`er061_fixtures/F1_trial2_r2_normal.md`等)を返すため、mockが通ることは『開いた窓』の**配管・出力先・管理ID・seed・ページ生成**の通過を示すだけで、話者roster(§3-C)・原稿品質の検証ではない。
- Regression(各1回、unittest、JPY0): `run_project_regression.py --pattern "er062*_test*.py"` 79件 PASS / `"er063*_test*.py"` 84件 PASS / `"er026*_test_*.py"` 129件(新規test 24件を含む)。補足: 1周目のer026でmock実走と並列実行したため共有状態ファイルtest(`MockFullPipelineTest.test_shared_state_files_unchanged_by_mock_run`)が1件FAILしたが、単独再実行でPASS(原因=並列実行による共有state書込の競合。コード起因ではない)。最終の逐次(並列なし)全件再実行結果=er062 79/79・er063 84/84・er026 129/129 PASS(FAIL 0、writer/structure変更後)。

## §9 SSOT文案(CURRENT_SPEC/DECISION_LOGは委任_02完了時にまとめて編集。本委任では編集していない)
- CURRENT_SPEC案: 「Family Z(Fiction)」節への追記=『第2作『開いた窓』(Saki)』Seed/権利Gate結果(1977-05-21満了計算)、STORY_REGISTRYのstory別化(管理ID・pages dir・タイトル・音声ファイル名・Lint config)、Melos不変のRegression、話者roster story別化の状態(設計済み/実装済み)。
- DECISION_LOG案: 2026-10-21 ユーザー指示(原文=`..._USER.md` sha3517c47f)、Phase 1結果、判断候補(§10)。
- OPEN-428: `OPEN_ITEMS.md`に新規1行(POST_USER_VALIDATION区分、`PHASE1_READY_PENDING_FABLE`)を追記済み。

## §10 判断候補・Fable確認事項(USER_DECISION_REQUIREDラベルはFableのみが付ける)
1. **話者roster story別化(§3-C)**: 条件A(新しい構造・Prompt/Voice割当ロジックの変更)該当の判定。実装しないとreal runは`plan`でSTOP。区分: C(現タスク範囲外の追加実装)、ユーザー判断ではなくFable判定。
2. **Mrs. Sappletonの第2女性Voice**: 承認pool(Aoede[narrator]/Erinome[Vera]/Charon[男性陣]/Algieba[Framton])では賄えない。選択肢=(a)Erinome共用[承認pool内、Veraと同一Voiceで聞き分けが弱い]、(b)Sulafat[CURRENT_SPEC L297の6候補pool内だがZ-4で未使用=新Voice採用扱い]、(c)Aoede共用[narratorと同一で最弱]。推奨=(b)。(b)を採るにはユーザー(またはFable)の新Voice承認が必要。区分: D(真に新しい判断)の候補。
3. **ユーザー§2と既存Prompt `R0_BLOCK_PRESERVATION`の強さの差**(§2-2): Prompt変更は本委任では行わず`seed.json`で担保。text stage後のFable CP結果次第。区分: C(CP結果待ち)。
4. **Preview/Commentのforbidden_names/spoiler語**(`STORY_LINT_CONFIG["the_open_window"]`)を追加: 既存機構(story_key別config)の値で新方式ではないが、blocking語彙の追加であり、過剰一致時はretry費用が出る。Fableが受理面の新設に当たらないか確認すること。区分: B(承認範囲内で自己解決)と判断して実装。
5. **起動回数**(§5案A推奨、2回起動)。区分: Fable/委任_02で明示許可。
