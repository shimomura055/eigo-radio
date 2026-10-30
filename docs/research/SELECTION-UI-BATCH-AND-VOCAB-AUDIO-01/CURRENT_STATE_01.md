# SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 CURRENT_STATE_01(Phase 1調査、2026-10-30、読取のみ・API 0)

原文=docs/pm/delegation_log/2026-10-30_SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01_USER.md。以下はfile:lineで確認した現行事実。

## A. 学習項目選定フォームV3(user_test/selection_form_v3/)
| 事項 | 現状 | 根拠 |
|---|---|---|
| 構成 | index.html(146行・単体画面)+form_logic.js(365行・DOMなし純ロジック、browser/node両用)+data/*.json(記事×レベル1ファイル)+data/articles.json(35枠索引、`?a=<slug>__<level>`で選択、プルダウン1つで1セットを編集) | index.html:5-146, articles.json |
| 件数規則 | 累積上限 LIMITS=[3,5,12]: ①KP<=3、①+②<=5、①+②+③<=12。**下限なし(0件でも送信可)**。候補は phrases<=7 + words<=5=最大12(validateArticle) | form_logic.js:7,19-24,330-331 |
| ①②③の意味 | ①Key Phrase(KP音声+詳細解説)/②追加解説(KPでないVocabulary)/③本文意味表示(本文ハイライトのみ)。フレーズ・単語は同一候補プールで区分(cat1-3)を選ぶ。kp_confirmed(ユーザー確定済み、例ai_island)は3/2/5固定で再選定不可 | form_logic.js:61-66,112-114,331-343 |
| 排他・重複 | 1候補は1区分のみ(choices[term]=cat)。重複termはvalidateでNG。優先順位の概念なし(ユーザーが区分を決める) | form_logic.js:15-24,326 |
| 候補適格性 | データ書出し時に決定(export_form_data_01.py=Gate通過・HR事前QA後の候補のみ。flags/human_selectableはdataにあるが**フォームJSは参照しない**=提示された候補は全て選択可) | export_form_data_01.py, data/*.json(human_selectable=False 0件) |
| 文法 | Top1/Top2のみ提示、ラジオ1件または「適切な候補なし(0件)」。grammar_spec付きdataで未決定なら送信/コピー阻止。提示0件=n/a(Z/Y多数) | form_logic.js:25-61 |
| コメント | **自由コメント1欄のみ・画面最下部**(textarea#comment)。normalizeComment(空/「なし」等=空)。st.commentに保存 | index.html(comment), form_logic.js:231-235 |
| 保存 | localStorage `eigo-kp-form-v3` { "<slug>__<level>": {choices, grammar, grammar_zero, comment} }。Done概念なし | index.html STORE_KEY, form_logic.js:84,102 |
| 出力(readable・AIF1) | 1セット=人間可読テキスト(記事名｜レベル / ①②③各`- term：日本語訳` / 文法名+【解説全文】 / 自由コメント)+末尾`照合コード AIF1-<stem>-<d6>-<c8>-<t8>-<s10>-<g10>-<m8>-<chk4>`(stem=dataファイル名、d6=data bytes sha、s10=選択、g10=文法、m8=コメント)。ニュアンス欄は廃止(AIF2は移行受理のみ) | form_logic.js:251-310 |
| 送信 | 「ChatGPTへ送信」(PREFACE付き+chatgpt.com URL)「選定結果をコピー」「技術情報付きコピー」。**今回の方針(コピー貼付のみ・自動送信なし)と差**: ChatGPT送信ボタンは新UIで撤去対象(自動送信ではなくURL起動だが「Claudeへの自動送信対象外」「新たな通知基盤なし」→削除でなく非表示化の要否はFable判断。推奨=一括画面では出さない) | index.html send/copy |
| 受入側 | er128_form_readable_restore_01.py: `restore(text)`は貼付中の**最後の**照合コードを採用し1セットのみ復元(:358-360)。コード検証(chk/d6/c8/t8/s10/g10/m8)・data版の履歴復元・term/日本語訳逐語照合・文法解説全文照合を経て payload v2 を生成。CLI `cmd_from_readable(text_path, run, level, ...)`(:597)は1セット/回。**ちょうど3件の検査は無い**(件数はフォーム側のみ) | er128:351-498, 597 |
| 既存test | `docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/selection_form_logic_test_01.js`(node)・`form1_selection_form_v3_test_01.py`・`er128_form_readable_restore_test_01.py`・fixtures/readable_cases_01(batch js)。X4記事用`FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01/tools/form_node_check.js` | git grep form_logic |
| Family/レベル差分 | フォームロジックはFamily非依存。差はdata側のみ: kp_confirmed有(AI島)=KP固定・文法のみ選定、grammar候補0(Z/Y多数)=文法n/a、候補数7〜12(yuki_onna a2=3+4=7、moon b1b=7+5=12)。Std=a2/Adv=b1b | data/*.json集計 |

## B. Vocabulary & Expressions(End User)と音声
| 事項 | 現状 | 根拠 |
|---|---|---|
| 5件の構成 | 例 月のしわAdv: vocab=['way off','over its entire history','porous','culprit','puzzling']。うちKP(部分音声あり)=way off/porous/culprit(①3件)、非KP=over its entire history/puzzling(②2件)。=**①3+②2=5**(Part1 vocab_confirmed+Part2) | user_test/dev_enduser_page_01/data/moon.json 実測、vocab_confirmed.json |
| ②の件数 | ②は現行「0〜2件の任意」。5件に満たない記事はVocab<5(「5件すべて」=掲載された全件の意味。**②を2件に強制する仕様は今回の原文に無い=変更しない**) | form_logic.js:7 |
| KP音声の物理形 | KP音声は**独立ファイルではなく記事音声のKP区間segment mp3**(番号→英語→日本語意味(Advは英語解説)→英語再掲)。End Userページは `parts[i].kp[k].en_audio={start,end}`(ffmpeg silencedetectで2番目の発話ブロック=最初の英語発話を検出+ローカルASR whisperで転写照合)をseg mp3に対し`playKp`で区間再生・終端で停止 | app.js:195-203, er135_enduser_page_01.py:492(compute_kp_audio), WIRING_DESIGN_01.md:146 |
| KP英語TTSの生成 | `kpN_en.wav`を`_generate_or_reuse_kp`+`_kp_english_generate_fn`で生成(KP3V=OpenAI/Azure/Whisper 3-ASR多数決、Master Audio Store key、K2 style)。Y/Zは同関数を共有(`xr._generate_key_phrase_segments_*`をer121_family_y_audio_01.py:632,749が呼ぶ。Zもrunner経由) | er019_runner:1316,1891-1907,1957, er104_kp_vote_reuse_01 |
| 再利用機構 | er006_master_audio_store_01.get_or_generate(MasterAudioKey)=同一key(text/voice/style)は同一master_audio_idを再利用(+reuse telemetry)。`_generate_or_reuse*`はcache(tts_generation_results.json)から再利用+値ガード(er078)+KP vote再利用ゲート。**retry/fallback/resumeは既存のgenerate_or_reuse契約に載る** | er006_master_audio_store_01.py:101-190, er019_runner:1255-1375 |
| ②追加解説2件の音声 | **現状なし**(記事音声に②の英語読み上げは含まれず、End User UIにも再生ボタンなし) | moon.json vocab非KP, app.js:94-100 |
| End Userカード | `<details class="vi" id="vi-<lv>-<n>"><summary><b class=vh>見出し</b><span class=vm>意味</span></summary><dl>本文中の意味/本文の英文/日本語訳/解説</dl></details>`(PC>=700pxは既定open)。KP見出しのみ別所(Full Story各partのKPボタン)で再生可 | app.js:94-100 |
| 配布形 | enduser_page_assets/rev01-e/{index.html,app.js,style.css}(DEV rev01-eの機械的派生、derive_assets_01.py EDITS)+各記事`enduser/data/article.json`(schema `enduser_article_v1`、additionalProperties=false)。公開済み5記事: Y再配達・Y姓・X月reselect・Z melos・Z藪の中(藪はお蔵入り) | er135_enduser_page_01.py:38,906, find article.json |
| 並行作業 | ENDUSER-EN-JA-LINKED-HIGHLIGHT-01が新build id **rev01-f**(`enduser_page_assets/rev01-f/`、ASSET_BUILD_ID更新、derive_assets EDITS追加、er135_enduser_page_01.py build_enduser・schema・validate・verify変更)を実装中(DESIGN_01 D3,D4) | ENDUSER-EN-JA-LINKED-HIGHLIGHT-01/DESIGN_01.md:28-38 |

## C. 原価の基礎数値(概算、確定値ではない)
- 既存基準(er005 cost_summary: 2026-08基準)の英語短文TTS+ASRは1clip当たり約0.004円(TTS)+0.002円(ASR)の桁。KP3V(OpenAI+Azure+whisperローカル)とK2 styleで1clipは数倍になり得るが、**追加2clip/レベルなら1記事セット(Std+Adv)=4clip、概算 約0.1〜1円**。一次見積は最初の実走で実測(Cap付き)。保存・配信=mp3数KB×4でGitHub Pages無料枠内(増分0円)。再利用率: 追加2表現はKPに含まれないため再利用はMaster Store hit(同一表現が他記事/他レベルに既出の場合のみ)。
- 既存5公開記事のバックフィル: 5記事×2レベル×最大2=最大20clip(藪の中を除くと16)。

## D. 過去の同種対策との整合
- 12件枠/3-5-12累積は参照HTML(docs/pm/Phrase_Form/eigo_radio_selection_form_reference.html)由来で維持。文法1件仕様(2026-10-27)・AIF1形式(2026-10-27 USER_03 §B)・ニュアンス廃止(2026-10-30、OPEN-617)を侵さない。
- KP-GATE-DROP-BACKFILL(候補を7+5へ補充)は「候補不足でも品質を下げない」基盤。ちょうど3件必須化は、①が3件に満たない候補不足記事(候補>=7が実測の最小)では現状発生しないが、将来の不足時は停止・理由表示とする。
- HR-SELECTION-FLOW(UDR対象U): 候補はHR提示前にQA済みで、フォームは追加の適格性検査をしない=「残り全選択」の適格性は提示候補=全て適格で足りる。
