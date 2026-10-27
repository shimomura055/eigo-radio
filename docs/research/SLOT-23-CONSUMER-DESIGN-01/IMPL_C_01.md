# IMPL_C_01 委任_04C(C班): Family X 配線の実装記録(API 0 / JPY 0)
設計正本=`DESIGN_03.md`(§A/§B/§C/§C-追補/§D/§E/§J)、契約=`CONTRACT_03.md`(本委任で実装に合わせて改訂)、A班=commit 22f3a09ef、B班=commit 374cfc941(着地済み、待機0分)。
ユーザー正式決定=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md`。**マーク発行(`new_review`接続)はしない**(M14)。AI島の再ビルド・公開はしない(HR承認後の別委任)。

## 1. 表示有効化と既定動作(隔離)
- 表示有効化=`er128.display_spec_of(run, level)`(flag非経由。`EIGO_KP_CONFIRMED_PROTECTION=0`でも変わらない)が真のrun・levelだけ。無い=従来描画(バイト同一)。
- 環境変数・引数・設定dictでONにする経路なし(test `DefaultOffIsolation`)。`display_spec`/`std_part1`を**書く**コードはC班に0件(付与は`new_review`の1箇所のみ=B班、未接続)。
- 現状 `new_review` へマーク発行は未接続のため、新規のa2 reviewは従来どおりマーク無し=本配線は休眠(AI島など`reconsume`済みのrunが出るまで発火しない)。

## 2. 変更点(file:line。`er019_family_x_audio_production_runner_01.py`)
| 項目 | 場所 | 内容 |
|---|---|---|
| Part 1 level化(R4) | `:413-650` | `generate_part1`/`generate_part1_ja`/`generate_part1_all`/`assemble_part1_x`/`run_study_text_stage`/`part1_study_html_for_player`/`_part1_kp_items`/`_part1_explanations_path`/`_part1_ja_path`/`_require_part1_*`/`part1_next_command` に `level="b1b"`(既定引数のみ)。旧`*_for_b1b`は互換別名なしで置換 |
| Part 1対象level | `:425,438-450` | `PART1_ALWAYS_LEVEL="b1b"`(Advは常に)+`part1_enabled`/`part1_levels`(Stdは`display_spec`付きのみ) |
| 失敗marker | `:456-458`(`_part1_failed_markers`) | b1b限定フィルタ撤去(全levelのmarkerを見る)。案内コマンドは`--level <level>` |
| scaffold | `:925-940` | `level == "b1b"` → `part1_enabled(out_dir, level)`、`generate_part1_all(level=)`/`assemble_part1_x(level=)` |
| study_text stage | `:3783-3795` | `part1_levels`でループ(各levelの`run_study_text_stage`) |
| tts/assemble/player入口 | `:3816-3835` | marker→level別案内、M2確認(`_require_part1_fresh_x`/`_ja_`)を`part1_levels`で |
| Part 2 pool | `:679-690` | `_part2_pool_x`をPart 1対象level(マーク付きStdを含む)へ |
| player | `:3158-3225`(`_build_level_table`)、`:3237-`(`build_player_html`) | `highlights`引数(Noneは従来コードそのまま=未escape・バイト同一)。Full Story 3段+In One Lineのscript cellを`render_script_html`(escape+装飾)+当該Part直後の③`ul.lk-meaning`、表の前に凡例、表示範囲外の③訳は表の後。`⏸`は装飾の外(dev)。CSS=`PLAYER_CSS_WITH_HIGHLIGHT`(`:3020`、runner内で`audio_review_player.PLAYER_STANDARD_CSS`+`HIGHLIGHT_CSS`を連結。**共有`audio_review_player`は無編集**=Family A等の出力もバイト同一。`test_family_a_files_have_no_working_tree_diff`も維持) |
| ハイライト配線 | `:3014-3125` | `x_display_units`(Full Story 3段+`in_one_line`)/`x_source_dir_of`(`entry_point.json`のsource_dir)/`resolve_x_highlights`(article=`{source_dir}/{lv}/article.md`、cands=`<run>/<lv>/key_phrases/kp_candidates.json`、items=`items_from_record(確定レコード)`。ISSUEは`HighlightStop`=ページ生成前STOP)/`x_script_cell_html`/`validate_part1_block_count`/`verify_x_level_page`/`resolve_x_highlights_for_levels`/`verify_x_player` |
| main(player stage) | `:3886-3925` | Part 1を`part1_levels`で、Std側`compose_page_html(Part 1, Part 2)`、解決→`build_player_html(highlights_by_level=)`→`verify_x_player`(G3+Part 1ちょうど1個。違反=rc=3)、`verify_selection_matches_outputs`のstudy_text/vocab_pageをlevel化 |

## 3. 新規ファイル
- `er019_family_x_listening_page_01.py`(標準builder): `tools/build_aif3_listening_page_01.py`を昇格。引数 `--slug --run-name --web [--intro-note --run-root --source-root]`。AI島固有(SLUG固定・「後続反映予定」・「文法0件」)を除去。必須検査(check_page[public]、G3、Part 1ちょうど1個[vocab対象level]/0個[対象外level]、Part 2四者一致、ハイライト解決)をPASSするまで**index.htmlも音声も書かない**(音声mp3は検査PASS後に変換)。ハイライトありページだけ`</head>`直前に`HIGHLIGHT_CSS`と凡例。
- `tools/build_aif3_listening_page_01.py` → 標準builderを呼ぶだけの薄いwrapperに置換(音声ファイル名が`<slug>_<level>.mp3`に変わる旨を明記)。`docs/research/AI-ISLAND-FORM-PRODUCTION-01/BUILD_01.md`末尾に注記。
- `er019_x_page_guard_01.py`: 旧per-article公開ページscript(`er019_*page*.py` 14本)へ**1行importのみ**追加。import時に`sys.addaudithook`で、`<run>/<level>/`の入力(`parts.json`・`audit/timeline.json`・`audit/tts_generation_results.json`・`key_phrases/keywords_canonicalized.json`・`assembled/*`のopen/glob)へ最初に触れた時点で、確定レコードに`display_spec`があれば`X_PAGE_GUARD_DISPLAY_SPEC_RUN`でSTOP(音声変換・ページ出力の前)。`display_spec`無しの旧run=素通し。モジュール変数`ENABLED`はtest専用で環境変数・引数では切替不可。標準builderはimportしない。
- `er019_nws2_final_page_01.py`: `study_html_for_audio_dir(pp.RUN, level="b1b")`へlevel明示+docstringに「旧仕様の既存記事用・新規記事は標準builder」を明記(`CURRENT_SPEC.md:2095`の正式入口記述の更新はFable/別委任)。
- `er019_x_highlight_wiring_test_01.py`(新規test 30件)。

## 4. 旧経路撤去(R4/S一覧のX分)のGrep
- 完了基準「Part 1系関数内の`"b1b"`リテラルが既定引数以外で0件」: AST test `test_no_b1b_literal_in_part1_functions_except_defaults`がPASS(対象15関数)。Grep結果(`er019_family_x_audio_production_runner_01.py:413-655`の`"b1b"`): `:425` `PART1_ALWAYS_LEVEL`定数1件(Advは常にPart 1対象という**方針定数**であり固定パスではない)と、`level: str = "b1b"`の既定引数のみ(`:452,461,483,498,502,533,549,581,595,609,625,639`)。
- 旧名: `generate_part1_for_b1b`/`generate_part1_ja_for_b1b`/`generate_part1_all_for_b1b`/`assemble_part1_for_b1b`はrunner・builder・toolsから0件(残存Grep=本委任のtest内のassert文字列のみ)。既存testのmock名(`er030_..._m2_supply_01_test_01.py`/`er053_c3_audio_guard_test_01.py`)は新名へ更新。
- 旧`:434-436`(b1b限定の失敗marker)・`:439-443`(`--level b1b`固定の案内)・`:461-524,573-624`(b1b固定パス)・`:603-614`(study_text stageのb1b限定)=全て撤去/level化済み。

## 5. 実データ確認(AI島のJSONコピー上のみ。run dir本体・公開物・API=0)
`ai_island_temple__run_form_prod_01`のjsonだけをscratchへコピーし、確定レコードへ`display_spec`を**コピー上のみ**注入、assembleがM3 Style Gate BLOCKのためコピー上で`run_summary_assemble.json`を合成OKにして実行:
- 解決: Std 10/10装飾(NOTICE `HL_OCCURRENCE_RELOCATED` 1件=Strategy S2→S8、停止せず)、Adv 10/10装飾(NOTICE 0)、ISSUE 0。
- player: ①(lk1)6・②(lk2)4・③(lk3)10要素(=Std/Advで3+2+5ずつ)、③訳リストのli 10(各5)。G3(`verify_highlights`)Std/Adv PASS。
- 実AI島runは**未変更**(`git status`で当該run dirのplayer.html等に新規差分0)。再ビルドはHR承認後。

## 6. 判断・注意(分類B=承認範囲内、報告に明記)
1. 表示範囲に「In one line」を含める(Fable決定)。A班の残ISSUE(`year over year`)は構造的に解消(test `test_in_one_line_only_phrase_resolves_...`)。
2. 共有`audio_review_player.PLAYER_STANDARD_CSS`は無編集とし、連結CSSはX runner内に置いた(`test_family_a_files_have_no_working_tree_diff`=Family A無変更を保つ。委任文の「`PLAYER_STANDARD_CSS`にHIGHLIGHT_CSS連結」は、連結した版をXが使う形で満たす)。他Family(D/E)は各自の共通CSS経路で連結する。
3. `er128.load_verified_items(which="highlight")`はB班の実装予定だったが未着地のため、Xは`display_spec_of`+`load_record`(G1[`require_final_consistent`]は各stage入口で既に実行)で読む。B班が`which="highlight"`を提供した場合は`resolve_x_highlights`の1箇所を差し替える。
4. Validator(vocab対象levelのPart 1ちょうど1個、判断記録なし=0個=STOP)は、X playerでは`display_spec`付きrunにのみ適用(マーク無し旧AdvのPart 1ゼロを新たに止めると既存run/既存testの挙動が変わるため)。標準builderはvocab対象level(Adv常に+マーク付きStd)全てに適用。
5. 時間: B班着地待ち0分(着手時点で374cfc941がorigin/main・ローカルHEADに存在)。
