# IMPL_D_01 委任_04D(D班): Family Y の配線(本文ハイライト①②③・③訳リスト・Std Part 1 level化・Validator置換・page_verify G3)
API 0 / JPY0(testはmock)。設計=`DESIGN_03.md` §A/§B/§C/§D/§E、契約=`CONTRACT_03.md`(A班実装が正)、A班成果=`RESULT_PACKET_S23A.md`(1)(4)、B班API=`IMPL_B_01.md` §2(commit 374cfc941、着地済み=待機不要)。
**マーク発行(`new_review`への`issue_std_part1_mark`接続)は未接続**(M14=B班の最後の1commit)。接続前は全Yパスが従来どおり(マーク無し=バイト同一)。**実run・再ビルド・公開はしていない。**

## 1. 動作の要点
| 項目 | 内容 |
|---|---|
| 表示有効化 | 確定レコードの`display_spec`(`er128.display_spec_of`を`er119._cc()`経由で参照。flag/環境変数/設定dictで切替不可)。マーク無しlevel=従来描画(バイト同一)。 |
| 表示範囲(DisplayUnit) | Yページの台本ブロック(Full Storyの8 segment: lead/intro1-3/voice1-3/closing)を公開順。`texts=[segment本文]`、key=segment ID。`translate/<level>.md`の`split_y_article`(=`parts.json`と同じ導出)から作るためTTS前に解決できる。 |
| 候補生成に使った本文 | `ys.canonical_body(translate/<level>.md)`(`_kp_review_step`の入力と同一)。`resolve_highlights`が`text_sha256`一致を検査(不一致=`HL_TEXT_SHA_MISMATCH`でISSUE)。 |
| 解決 | `er_learning_highlight_01.resolve_highlights(article_text, cands_doc, items, display_units)`を1箇所で呼ぶ(再実装なし)。ISSUE=原因コード付きSTOP(部分適用なし)、NOTICEは`audit/highlight_resolution_<level>.json`へ記録。 |
| 解決のタイミング | (1)`stage_tts`入口(有料TTS前・API 0でSTOP)(2)`stage_pages`(mp3化前)(3)`stage_page_verify`(再解決してG3)。 |
| 描画 | `build_page_rows(..., highlights_result=)`→`cp.script_block(..., highlights=hl.highlights_for_text(...))`。`⏸`(dev)は装飾の外(A班`render_script_html`)。public混入0。③訳リスト(`ul.lk-meaning`)はlevel節の台本表(table)の直後・Part 1の前(table/div.script/h2の外)に1個。凡例1行はページ冒頭(Voice説明文・Chunk凡例の後)。`HIGHLIGHT_CSS`は`render_y_page(highlight=True)`のときだけ`<head>`へ連結。 |
| Std Part 1 | Advancedは常に、Standardは`khr.vocab_enabled(level, review)`(=review.std_part1=display_spec付き)のときだけ、level別stage(`kp_part1_<lv>`/`kp_part1_ja_<lv>`)・level別dir(Adv=`<out>/study_text`従来どおり、Std=`<out>/a2/study_text`)で生成。Part 1→Part 2の順(`compose_page_html(part1_html, p2res)`)。失敗はそのlevelのTTS前ではなくkp stage内でSTOP(KP確定は保持)。 |
| Validator置換 | 旧「StandardにPart 1があるとSTOP」「Part 1が0個でも通る」を撤去。vocab対象level(Adv常に/マーク付きStd)=Part 1がちょうど1個かつPart 2の直前(0個・2個・逆順はSTOP)、対象外level(マーク無しStd)=Part 1は0個(あればSTOP=遡及なし)。`FAMILY_Y_PART1_OUTPUT_MISMATCH(<lv>)`。判断記録(訳欄)なしで描画が空になる場合は個数0としてSTOP(黙った欠落なし)。 |
| page_verify G3 | 既存検査(check_page・Voice説明文・Part 2 4者一致・KP選定)に加え、`_verify_highlights_on_page`: level節ごとに`verify_highlights`(網羅=data-hl単位ちょうど1出現/本文不変/③訳一致/public混入0)、マーク無しlevelに`data-hl`/`lk-meaning`があればSTOP。確定内容保護のkill switch無効時は`SKIPPED_DISABLED`を記録。 |
| 不変 | Voice説明文`PAGE_NOTICE_JA`・`audience=dev|public`マーカー・Style継承(OPEN-537 WIRED)は未変更(回帰test PASS)。 |

## 2. 配線点(file:line)
- `er121_family_y_audio_01.py`: `y_highlight_display_units`:1431 / `y_highlight_article_text`:1438 / `resolve_y_highlights`:1443 / `highlight_meaning_html`:1460 / `build_page_rows(highlights_result=)`:1467,装飾呼出:1516-1522 / `render_y_page(highlight=)`:1551。
- `er121_family_y_runner_01.py`: `ADV_LEVEL, STD_LEVEL`:40 / `PART1_STAGES`:321 / `stage_kp`のPart 1 level別ループ:672-682 / `_part1_level_enabled`:707 / `_part1_items`:714 / `_assemble_study_rows`:764 / `_stage_kp_part1`:777 / `_stage_kp_part1_ja`:807 / `_part2_pool`:975 / `_assert_study_ready`:998 / `_assert_std_study_ready`:1007 / Validator置換`_verify_part2_outputs`:1025-1053 / `stage_tts`入口の事前STOP:1122 / `_resolve_highlights_or_stop`:1218 / `stage_pages`:1244(解決:1254、Part 1+Part 2合成:1255-1265) / `_verify_kp_selection`:1300(Std Part 1のstudy_text/ページ照合を追加) / `_verify_highlights_on_page`:1319 / `stage_page_verify`呼出:1358。
- `er121_family_y_mock_01.py` `mock_kp_fn`: 実候補docと同形(`source_sentence`=本文の文そのもの、`source_sentence_id`付き)に是正(従来は語句そのもの+ID無しで、ハイライト解決が成り立たなかった)。Part 1の引用英文も本文の文になるが既存test全PASS。

## 3. 旧経路撤去の完了基準(Grep結果)
- Part 1系関数内の`"b1b"`/`"a2"`リテラル: AST走査で0件(`NoLegacyAdvOnlyLiterals`test)。既定引数は定数`ADV_LEVEL`(`ADV_LEVEL, STD_LEVEL = LEVELS`の1定義のみがlevel文字列の出所)。残る`"b1b"`リテラル(行39,306,324,380,407,438,487,614,840,1022,1112,1123,1135)はLEVELS定義・text/support/TTS/Part 2(Adv既定)/ページ節ID等でPart 1系ではない。
- 撤去した識別子(コード上): `PART1_STAGE`/`PART1_JA_STAGE`(→`PART1_STAGES[level]`)、`_part1_items_b1b`(→`_part1_items(ctx, level)`)、`_assert_std_part2_ready`(→`_assert_std_study_ready`)。残存Grep: `grep -n "PART1_STAGE\b\|PART1_JA_STAGE\|_part1_items_b1b\|_assert_std_part2_ready"` → Y runner内はコメント1行(`PART1_STAGES`定義行の「旧…は撤去」注記)のみ、Y testは`ZFUNCS`(Z[er026]用の従来名)と`Y_RENAMED`注記のみ。
- 撤去した旧Validator文言: 「StandardにPart 1が{n1}個あります(Part 1はAdvancedのみ)」→ `grep -n "Part 1はAdvancedのみ\|StandardにPart 1が" er121_family_y_runner_01.py` = 0件。
- 更新した旧test: `StudyTextWiring.test_two_items_adopted_in_standard_...`(OPEN-543。文法2件採用=旧仕様→新仕様[最大1件]。2件選択は`Part2ReviewError`で拒否、1件採用はページ・4者一致を通る)。`PART1_STAGE*`参照2箇所は`PART1_STAGES[level]`へ。

## 4. test(API 0)
- 新規`er121_y_highlight_wiring_test_01.py`=24件PASS(マーク付き全stage通し[Adv/Std両levelでPart 1ちょうど1個・5項目各1出現・G3 PASS・check_page PASS・public⏸0]、③訳リストがtable/div.scriptの外でG3 PASS、dev⏸が装飾の外に共存、ISSUEがpages前/TTS前[API呼出0]にSTOP、G3の欠落/区分違い/余剰/⏸混入検知、Validatorの0個・2個STOP、マーク無しrun[装飾/凡例/CSS/訳リスト/Std Part 1が出ない・Std Part 1ブロック混入はSTOP・data-hl混入はSTOP]、golden)。
- golden: `fixtures/y_golden_run_style_fix_01.json`(配線変更**前**に`tools/y_golden_capture_01.py`で採取したsha256。既存run `run_style_fix_01`のpublic/dev両方の`build_page_rows`+`render_y_page`出力)。変更後も同一(public `b1cf73e0…`/dev `188df736…`)。
- 既存回帰: `er121_family_y_runner_01_test_01`=54件PASS(旧2件testを新仕様へ更新済み)、`er121_*`該当test・`er_page_audience_marker_test_01`・`er128_kp_confirmed_content_02b`・`er120_part2_wiring_integration`・`er119_kp_backfill`・`er125`・`er127`・`er019_family_x_fx_20261016_wiring`・A班29件 全PASS。

## 5. 残課題・他班への依頼(判断候補を含む。いずれも本委任の範囲外/記録)
1. **共有guard test `er128_kp_confirmed_content_test_01.TestIsolation.test_abc_and_shared_functions_do_not_import_er128`(B班所有)**: 全`*.py`で`^\s*(import|from)\s+er128_`を禁じ、許可はファイル名一覧のみ(`er128_kp_highlight_01.py`自身は許可済み)。X/Y/Zの配線(A班契約の`er128_kp_highlight_01.verify_highlights`をpage_verifyから呼ぶ)は必然的にこのimportを持つため、Yでは`er121_family_y_runner_01.py:1322`(関数内import)が検出される(C班の`er019_*`・E班の`er026`も同様)。Yは`er128_kp_confirmed_content_01`自体は`er119._cc()`経由で参照しimportを増やしていない(`FLAG_NAME`文字列もY側に残していない=`test_default_is_on_and_single_reader`のうちY起因分は解消)。**対応案**: B班/Fableがguard testの許可一覧を「X/Y/Zの表示builder入口が`er128_kp_highlight_01`をimportするのは可」に更新する(名前変更等の迂回はしない)。分類=B(承認範囲内・技術)。
2. **確定時(`confirm --from-form`)の事前解決(DESIGN B-3手順8)はer128側(B班)の範囲**。Y runnerは`stage_tts`入口(TTS費用前)で同じ解決を行う。
3. Y側`confirm`ルートで③を含む実確定レコードのE2E(実ブラウザ375/390px等)はF(evidence)の範囲。
4. `er109_xz_isolation_01_test_01`の2件失敗(scope module importer一覧: er118_fz_*/er122_fz_*/既存の`er121_e1_slowed_asr_recheck_01.py`)は本委任の変更ファイルを含まず無関係(Y側で`er121_e1_slowed_asr_recheck_01.py`は未変更)。
5. 環境: `.venv/Scripts/python.exe`で実行(システムPython 3.14は`google.genai`/`wordfreq`未導入でY系testがimportできない)。
