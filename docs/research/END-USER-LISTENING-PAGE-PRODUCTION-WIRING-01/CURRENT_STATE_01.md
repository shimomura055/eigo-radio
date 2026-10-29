# CURRENT_STATE_01(END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 委任_01、2026-10-29、API 0・コード変更0・Production変更0)

原文=`docs/pm/delegation_log/2026-10-29_END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01_USER.md`。管理=OPEN-597(OPEN-590末尾にも追記)。調査時点HEAD=origin/main(本委任の原文保存commitを含む)。
凡例: [仕様]=CURRENT_SPEC等の承認済み記述 / [実装]=稼働コード・生成済みページ / [未確認]=本委任で確認していない。DEV/Trial資産のpathは `D=user_test/dev_enduser_page_01`、`T=docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01`。

## 0. 要点(先に結論)
1. **DEVデータは「公開済み/候補の開発者向けindex.htmlをHTMLスクレイピング」して作っている**(T/tools/build_data_01.py:111-208)。X以外(Y/Z)では未検証。X/Y/Zの開発者向けページは行形式(`<tr><td><b>label</b>…data-t='…'<audio src=…>`、`div.script`、`section.study`)を共有する(§B)ため、**最終dev `index.html`+run補助データ→End User JSON**という単一アダプタ構成が最小変更で成立する(builder本体・Prompt・Gate不変)。
2. **日本語訳**: 承認済みデータが存在するのは「X: Full Story(`ja_writer/revision2.md`の段落)」「Y: Full Story各segment+Voice紹介(`text/article_ja.md`分割。開発者向けページが既に`日本語の元原稿`として表示)」のみ。**Z: 承認済み日本語訳は皆無**(Zは英語脚色を直接生成。T1訳はKP引用英文のみ=OPEN-512)。X/YのAdvanced英語Comment・Preview・In One Line・Topic introにも承認済み訳なし。DEVの未承認訳11ブロックは全て「X: Adv Comment1-4+In One Line(AI島・月)、Std In One Line(AI島)」。種別ごとの表は§C-2。
3. **文法/ニュアンス**: 0件・不採用の非表示は既存の共通合成関数が実装済み(`er120_part2_grammar_production_01.compose_study_html`:1543、`render_html_block`:1473は非SELECTEDで空文字、`render_nuance_html_block`:1528は非ADOPTEDで空文字)。End Userアダプタは「最終dev HTML内の`section.study`」を読むだけなので同じ表示制御を継承する(空枠検査は`count_empty_study_sections`:1561)。DEVの仮データは`grammar_source`/`nuance_source=placeholder_for_layout_check`(D/data/ai_island.json、D/app.js:103-110、build_rev_d_01.py:21)でありProduction資産に持ち込まない。
4. **音声同期の承認済み仕様はSSOTに存在しない**(CURRENT_SPEC/DECISION_LOGをGrep: 文単位ハイライト・同期失敗時の扱いの承認記述なし。T/PRODUCTION_IMPACT_01.md:20は「失敗時方針は仕様判断(ユーザー)」と明記し、試作は『ハイライトなし公開』を前提にしていた)。→ §D・判断候補1。
5. **faster-whisperはProduction環境に既存**(`.venv` faster-whisper 1.2.1/ctranslate2 4.8.1/av 18.1.0、HFキャッシュにmedium/small/small.en/tiny。Production既存利用=`er008_disfluency_qa_18.py:40`ほか。T/PRODUCTION_IMPACT_01.md §2の「Production未使用」は不正確)。実行はしていない(import可否のみ)。
6. **新たに見つかった要件ギャップ(DEV未対応)**: (a) FamilyY開発者向けページ冒頭の承認済み「Voice説明文」(実投稿記事のみ。CURRENT_SPEC:3202-3206、`er121_family_y_structure_01.py:110 notice_html`)をEnd Userページに載せる設計が未定義。(b) 開発者向けページの⏸(Chunk境界)・LR赤・Fallback濃青はエンドユーザー向けには出さない承認済み仕様(CURRENT_SPEC:3203)→アダプタで除去し、validatorで残存0を確認。(c) KP英語区間の検出が`assert len(blocks)==4`(T/tools/build_rev_01.py:160)で、実測でZ Adv KP2が5ブロックとなり不成立(§D-3)。(d) Xには「pages stage」が無い(§B-1)。

## A. DEV版の構造とデータ出所(rev01-e)
構成: `D/index.html`(36行)・`D/app.js`(333行)・`D/style.css`(122行)・`D/data/<article>.json`+`sync_*.json`。1ページ=1記事(Std/Advタブ同居)。記事選択は`init(Q.get('a')==='moon'?'moon':'ai_island')`(D/app.js:333)=DEV専用。音声は`art.audio_base`(`../family_x_…/`)で既存dev pageのaudioを参照(D/app.js:19)。

| JSONフィールド | 出所(正式run/ページのどこ) | DEVでの作り方(file:line) | 仮/未承認の混入 |
|---|---|---|---|
| id/family/source_page/sha | 手設定 | T/tools/build_data_01.py:15-26,148 | なし |
| levels[lv].main・parts[].seg/start/dur | dev index.html の audio id=main_lv・各行audio src・data-t、run `audit/timeline.json` | build_data_01.py:149-167(行数=timeline数、data-t≒start のassert) | なし(X専用のrun path固定) |
| parts[].label/kind | 行ラベル正規表現 | build_data_01.py:121-139 | X命名のみ対応(Yは`Full Story: Voice 1`、Zは`Full Story Part 1 (Aoede / …)`は未対応) |
| parts[].paragraphs[].(sid,html,text) | 行内`div.script`→段落→文分割 | build_data_01.py:62-96(split_sentences)、clean_script_html:46-50(chunk-mark除去・rpt-lr剥離) | なし。Zは1行にdiv.scriptが複数(in_a_grove Part1=12個)で未対応 |
| parts[].meanings(③訳リスト) | 行内`ul.lk-meaning` | build_data_01.py:179 | なし |
| parts[].kp[].(en,text) | KP行の表 | build_data_01.py:99-104,185 | なし |
| levels[lv].vocab/grammar | `section.study`のh3=Vocabulary/Grammar → `div.study-item>dl` | build_data_01.py:107-117,186-196 | grammar末尾の区切り記号をDEV側で除去(sanitize_html:119。X builderは現在strip_trailing_delim済=OPEN-591 FIXED)。**ai_island grammarは月Advからの流用(grammar_source=placeholder)** |
| levels[lv].nuance | (正式)h3=ニュアンス解説のsection | DEVはNUANCE-…/evidence/*_nuance_fragment.htmlを流用(build_rev_d_01.py:7-22) | **全て仮(AI島Std/Adv・月Adv=3件)**。DEV版はnuanceをdev HTMLから読んでいない |
| parts[].ja / ja_source | X Full Story=`er019_output/<slug>/<run>/ja_writer/revision2.md`の段落(approved_ja_manuscript) | build_rev_01.py:15-18,77-90 | **Comment/In One Line英語=DEV_TR直書き11ブロック(dev_translation_unapproved、build_rev_01.py:20-31,92-102)** |
| parts[].glossary(覚えておきたい表現) | 本文中lk1/lk2/lk3ハイライトspan+Vocab+meanings | build_rev_01.py:104-154(下線対象/KP/Vocabを重複なく配置。assertで全KP・全Vocabが載ることを要求) | なし(display_spec付きrunのみ成立) |
| kp[].en_audio(KP英語のみ) | KP区間mp3をffmpeg silencedetect(-40dB,d=0.2)し2番目の発話ブロック | build_rev_01.py:34-52,156-165 | なし |
| sync_*.json | 全文/segment mp3→faster-whisper(medium,int8)→TTS入力台本の決定論文分割→difflib整列→無音(RMS<-40dBFS)スナップ→dev表示文へ文字整列 | T/sync_build_01.py、T/sync_common_01.py(X固定)、T/tools/build_sync_index_02.py:19-83 | sync_dummy_*(文字数比例)は確認用。実同期の聴感照合は未実施(T/SYNC_METHOD_01.md「未確認」) |
| title_ja/topic_en | Std Japanese title行 / Topic intro行 | build_data_01.py:181,205-209 | なし |

DEV専用で**Production資産から除くもの**: `[DEV]`タイトル(D/index.html:7、D/app.js:291)、`?sync=dummy|off`分岐(D/app.js:268-282)、dev_translation_unapproved表示(D/app.js:34-38、D/style.css:48)、phnote/仮表示(D/app.js:103-110、D/style.css:108)、記事id固定init(D/app.js:333)。

## B. 正式Production経路のページ生成
### B-1 Family X(`er019_family_x_listening_page_01.py`)
- X runner(`er019_family_x_audio_production_runner_01.py`)に**pages stageは無い**(stage=scaffold/plan/tts/assemble等。main:3791)。公開試聴ページは別CLI `er019_family_x_listening_page_01.py --slug --run-name --web`(「新規記事の正式入口」、CURRENT_SPEC記載)。`build_page`(:148)が入力=assemble/Gate通過済みrun、出力=`<web>/index.html`+`<web>/audio/*.mp3`(全編128k・segment 96k、assembled wavから切出し=TTS再生成なし。:79-103)。
- 出力前必須検査(:5-9,200-235): 本文ハイライト解決(HighlightStop)・check_page(public)・G3 verify_highlights・Part 1個数・Part 2四者一致(確定とpart2_resultとstudy_textとページ節)。1つでも落ちたらindex.htmlを書かない(PageStop)。書出し直前にstrip_trailing_delim(:246)。
- 学習ブロック=`er120_part2_wiring_01.public_study_html`(:637)→finalize_nuance→`compose_page_html`(:624)。LR後英文は`er132_lr_overlay_pages_01`でdev pageの表示本文に反映(:101-104)。⏸/LR赤/Fallback青は`er133_report_marks_01`(:106-127)。
- retry/regeneration/resume: pagesはAPI 0・冪等(再実行で上書き)。LR/Fallback/TTS再生成後は assemble→listening page再実行が既存運用。stale検出は各検査(四者一致等)が担う。

### B-2 Family Y(`er121_family_y_runner_01.py`)
- STAGES(:34)=…gate,assemble,pages,page_verify。`stage_pages`(:1315-1356): 学習テキスト確定確認(_assert_study_ready/_assert_std_study_ready/_assert_nuance_final)→compose_page_html(Part1→文法→ニュアンス)→`ya.build_page_rows`(audioを`<pages_dir>/audio`へ書出し)→`ya.render_y_page`→`<pages_dir>/index.html`(devは`index_dev.html`)。pages_dirは`<run>/pages`(公開dirではない・公開は別手順:169-184)。
- `stage_page_verify`(:1415-1431): evaluate_page_verify(:1358)+Part2四者一致+KP選定+G3ハイライト。失敗はYE2EStop。
- Y固有: 承認済みVoice説明文(notice_html、適用は`_page_notice_applies`:1255。判定不能=STOP)、各Voice別segment、`日本語の元原稿`(details>div.ja、`er121_family_y_audio_01.py:1558`)。

### B-3 Family Z(`er026_family_z_fiction_production_runner_01.py`)
- E2E_STAGES(:1183)=…assemble,pages,page_verify。`stage_pages`(:2653-2685)→`a63.build_pages(ctx.out_dir, ctx.pages_dir, …)`(er063)。Part1/文法/ニュアンスはcompose_page_html(:2678-2680)。出力=pages_dir(例`user_test/family_z_in_a_grove_01/`: index.html+audio_standard/+audio_advanced/+standard.html/advanced.html)。
- `stage_page_verify`(:2743-2788): Playwright --local(er063_family_z_page_verify_01)+Part2確認。evaluate_page_verify:2688。
- 完成段は`--stages provision_shell,gate,assemble,pages,page_verify`を1起動で指定(sonnet-worker.md)。**新stage名を足すとこの運用(RESTART_STORM回避)を壊す**→End User生成は既存pages/page_verify内に置く(設計§2)。

### B-4 共通
- 3 Familyの開発者向けページは`er_user_listening_page_common_01`(render_standard_page:218、script_block:187、kp_block:208、check_page:320)を共有。実ページ調査(`user_test/family_x_moon_shrinking_reselect_01`・`family_y_production_redelivery_fee_03`・`family_z_in_a_grove_01`の各index.html): 全て行形式(td内b=label、data-t、行内audio src)を持つ。h2 idはX/Z=std/adv、Y=standard/advanced。Z=1行に複数div.script(話者別clip)、Y=行ごとにdetails「日本語の元原稿」。
- 現行dev pageはaux/制作情報/PASS_WITH_WARNING等の内部情報を持つ(X: details.aux・#pww、Z: #aux、Y: #production)→End Userには出さない。

## C. 正式データの所在(Family×level)
### C-1 データ種別→所在
| 種別 | X | Y | Z |
|---|---|---|---|
| KP/Word/本文意味(display_spec付き) | `<run>/<lv>/key_phrases/confirmed_selection.json`→dev HTMLの本文lk1/lk2/lk3+ul.lk-meaning+Part1(vocab_confirmed.json) | 同左(Std Part1はdisplay_spec付きのみ) | 同左 |
| 文法 | `<run>/<lv>/study_text/part2_result.json`(SELECTED/ZERO)→render_html_block。ZERO=空文字=非表示 | 同左 | 同左 |
| ニュアンス | `<study_dir>/nuance_result.json`(ADOPTED以外は空文字)。nuance_for_display(er120_part2_wiring_01:442) | 同左 | 同左 |
| Part構成/Comment/Full Story/In One Line | audit/timeline.json+dev HTML行 | dev HTML行(Full Story: Lead/Voice N Introduction/Voice N/Closing、In One Lineなし) | dev HTML行(Full Story Part N (話者…)、In One Lineなし。Welcome等の定型行にもscript有) |
| 音声 | `<web>/audio/{slug}_{label}.mp3`・std_NN.mp3/adv_NN.mp3 | `<pages_dir>/audio/{std,adv}_full.mp3`・std_NN.mp3 | `<pages_dir>/audio_{standard,advanced}/…`(番号は欠番あり)→**dev HTMLのaudio srcを正とする** |
| KP音声 | 行ごとのKP clip(番号→英語→訳or英語解説→英語再掲) | 同構造 | 同構造(Z Adv KP2は5ブロック) |

### C-2 日本語訳の有無(承認済みデータ。「存在しない」は種別ごと)
承認済み根拠: X=`ja_writer/revision2.md`(derive_japanese_titleの優先順 revision2→revision1→original、er019_family_x_audio_production_runner_01.py:160-174)、Y=`text/article_ja.md`(er121_family_y_runner_01.py:280、translate/<lv>.mdでJA→EN)。Z=該当なし。T1訳工程(CURRENT_SPEC:2100)は『本文引用英文』のみ=ブロック訳ではない。旧translation_ja.json(CURRENT_SPEC:2744-2765)は旧Family A/B/C unified.html向けでX/Y/Zの新経路には無い。

| ブロック種別 | X Std | X Adv | Y Std | Y Adv | Z Std | Z Adv |
|---|---|---|---|---|---|---|
| Full Story(Part/Voice各段落) | 承認済み(ja manuscript段落。段落数一致assertはDEV検証済) | 同左 | 承認済み(日本語の元原稿) | 同左 | **なし** | **なし** |
| Voice紹介/Lead/Closing | - | - | 承認済み | 承認済み | - | - |
| Comment 1-4(英語のとき) | 日本語本文(訳不要) | **なし**(DEV訳=未承認) | 日本語本文(訳不要) | **なし** | 日本語本文 | **なし** |
| In One Line(英語) | **なし**(DEV訳=未承認、AI島のみ) | **なし**(DEV訳=未承認) | 行なし | 行なし | 行なし | 行なし |
| Preview/Topic intro/定型行 | Std Previewは日本語。Topic intro英語=訳なし(DEVも非表示) | 訳なし | 同左 | 同左 | 同左 | 同左 |

→ 「存在しない→非表示」が現行の承認範囲での扱い。ブロック訳を新設する場合は新翻訳仕様(判断候補2)。

## D. 音声・同期
1. **音声の所在**: §C-1。全編+segmentは既存dev pageのaudioをそのまま参照(`../audio/…`、新規TTS/mp3 0)。
2. **DEV同期処理**: faster-whisper medium(int8・CPU)、word_timestamps=True, beam_size=5, condition_on_previous_text=False, vad_filter=False(T/asr_raw_01.py:22-25)。台本=TTS入力を決定論分割(T/sync_build_01.py:25-48)、トークン整列(difflib)、境界スナップ(RMS<-40dBFS・>=0.18s最長、段階2/3は低信頼度タグ、:171-196)。検証(T/SYNC_METHOD_01.md 29-44、T/sync_match_report_02.json): 3記事31segment・151文で単調/重なり0、Chunk既知ギャップ16件全一致、medium対small境界差0.00s、無音にスナップできない境界0(短ポーズ低信頼度4文)、ASR境界>1.5秒外れ0、ページ表示文155文と同期文の対応(exact 147・split 8・unmatched 0。T/sync_match_report_02.json)。所要=small約85秒/セット、medium約4分/セット(T/PRODUCTION_IMPACT_01.md §1)。費用0円。
3. **KP英語のみ区間**(DEV: build_rev_01.py:156-165)を3 Familyの実KP clipでsilencedetect(API 0・本調査で実測): X Std 2/2、Y Std 3/3・Adv 3/3、Z Std 3/3・Adv 2/3が4ブロック。**Z Adv KP2のみ5ブロック**(解説内ポーズ)。2番目ブロック=英語KPとする規則自体は5ブロックでも成立するが、DEVの`==4`assertは落ちる→設計は「4以上かつ2番目を英語、ASR文字起こしでKP表現と一致確認」に変更。
4. **既存承認仕様の有無**: CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSに「文単位ハイライトの同期データ生成・失敗時の扱い」の承認記述なし(Grep)。DEVは最大VALIDATED(OPEN-590)。既存の**stage失敗時の標準扱い**はfail-closed(X page: index.htmlを書かない、Y/Z: YE2EStop/FamilyZE2EStop→再実行)。
5. **ローカル環境**: faster_whisper/av/numpy/ctranslate2/playwright import可(find_specのみ)。モデルキャッシュ: medium/small/small.en/tiny。

## E. 既存完成記事からEnd Userページを正式データだけで作れるか
| 記事 | 取得可 | 欠落/注意 |
|---|---|---|
| X 月のしわ reselect(公開済 88df63bb0) | 行・音声・KP・Vocab・Grammar・本文意味(display_spec付き)・Full Story訳(revision2.md) | ニュアンス=旧ページに無い(コーナー非表示で正)。Adv Comment/In One Line訳なし→非表示 |
| X AI島 form(公開済) | 同上 | Grammarの正式採用有無は要確認(DEVは仮) |
| Y 再配達料 fee_03 / sns_age_limit_01 | 行・音声・Full Story訳・Adv Part1/文法(fee_03) | 本文ハイライト(display_spec)なし→「覚えておきたい表現」は出せない(Vocab/KPコーナーのみ)。Std Part1なし。Voice説明文の扱い(設計) |
| Z 走れメロス melos_02 / 藪の中 in_a_grove_01 | 行・音声・KP(in_a_groveはVocab+本文意味も) | 日本語訳なし(全ブロック)→非表示。Zは話者別div.script複数・文が引用符/話者を跨ぐ |
| NXW02C copy-run(`C:\Users\tensh\eigo-radio-evidence\NXW02C\{x,y,z}`) | ニュアンス採用/不採用/0件のX/Y/Z実run | 存在確認済(x: nxm1/nxm2、y: nxw_y1/y2、z: nxz2/3/4)。pages再実行でニュアンス/0件表示のruntime evidenceが費用0で取れる見込み |

## F. 関連OPEN・整合・dangling risk
- OPEN-590(DEV。本件でAPPROVED_FOR_PRODUCTION追記済)、OPEN-597(本件)、OPEN-591(区切り記号。FIXED。X builderのstrip_trailing_delimがdev page側で効く)、OPEN-586(ニュアンス、PRODUCTION_WIRED)、OPEN-588(HEADで失敗する既存test14件。本件のRegression比較は旧失敗集合と同一で判定)、OPEN-596(Zの閉じ引用符欠落発言。Z文分割に影響しうる)。HR選定フローWorker(er119/er128/er134/er121)・藪の中Worker(er062/er026 run)と同一runner file競合。
- dangling risk: (1) 公開は手動copy(Y/Zのpages_dirは公開dirではない)→`enduser/`サブdirがcopyから漏れる。copy対象にenduserを含める手順をSSOT化。(2) 完成報告テンプレ(sandwich-pm受入基準・RESULT_PACKET)に両URL欄がない。(3) CURRENT_SPECにEnd Userページ節が無い。(4) `user_test/dev_enduser_page_01`(DEV URL)の扱い(残置/廃止)をFable判断。(5) CURRENT_SPEC:3203のエンドユーザー非表示要件(⏸等)。(6) Playwright/ffmpeg等の実行環境依存。
