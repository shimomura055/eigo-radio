# IMPLEMENTATION_08 — Y Voice説明文の承認文言化 + 開発用Chunk境界マーカー(audience=dev|public、X/Y/Z共通)(委任_08、API 0・JPY0)
根拠: `USER_04.md` §1-B/C・§3・§4(2026-10-27)。設計: `CHUNK_MARKER_DESIGN_01.md` / `CLOSEOUT_PLAN_01.md` / `CHUNK_MARKER_INVENTORY_01.md`。到達=IMPLEMENTED+test(Production到達の判断はFable)。

## 1. Voice説明文(B)
| 項目 | 実装(ファイル:行は`git diff`参照) |
|---|---|
| 単一ソース | `er121_family_y_structure_01.py` `PAGE_NOTICE_JA`=「Voice 1〜3は実在人物の発言をそのまま再現したものではなく、実際に投稿された意見をもとに、AIが編集・再構成したものです。」(逐語)。アプリ表示も同定数を参照(アプリ開発は範囲外) |
| 適用条件 | `theme_package_is_post_based(tp)`: sheetsが全Voice枠(3)分あり、全経験(`experiences[]`)に非空`source_ids`のときだけTrue。`notice_html_for_theme_package`。空/欠落/dict以外=False=注意書きを出さない(根拠のない出典主張を生成しない) |
| pages stage | `er121_family_y_runner_01.py` `_page_notice_applies(ctx)`: Theme Package読めない=`FAMILY_Y_THEME_PACKAGE_MISSING_FOR_NOTICE`でSTOP(黙って落とさない)。`render_y_page(..., show_notice=)` |
| page_verify | `evaluate_page_verify(..., expect_notice)`/`ys.check_y_page_notice(expect_notice=)`: 出すべき記事は1件・本文外、出さない記事は0件 |
| DEV `er110_family_y_redelivery_revision_01.py:39` | 無変更(凍結)。Production(er121)は参照しない |
| X/Z | 説明文なし(新設せず)。`test_no_xz_page_in_repo_contains_the_y_notice`維持(Yの`evidence_runs/y*`を許可リストへ) |

## 2. Chunk境界マーカー(C、`audience`)
| 項目 | 実装 |
|---|---|
| 共通機構 | `er_user_listening_page_common_01.py`: `AUDIENCE_PUBLIC="public"`(既定)/`AUDIENCE_DEV="dev"`、`normalize_audience`(未知値/None=ValueError=fail-closed)、`script_block(text, chunk_texts=None, audience="public", warnings=None)`(既定はバイト同一)、`script_html_with_chunk_markers`、`chunk_texts_of_plan`、`load_chunk_plans`、`count_chunk_markers`(⏸/`&#9208;`)、`count_boundary_marker_spans` |
| 表示 | 実Chunk境界(chunk iとi+1の間)にだけ`<span class='chunk-mark'>&#9208;</span>`。秒数・title・説明なし。chunk本文が台本に見つからない境界は出さない(推定位置なし、warnings) |
| 境界の取得元 | `audit/chunk_plan_<level>.json`の`plans[親id].chunks[].text`(`er117`のplan出力)。ASR/音声解析ポーズは使わない |
| 公開物ガード | `check_page(..., audience="public")`が`no_chunk_marker_in_public`を検査(公開用にマーカーがあればFAIL)。Y `stage_pages`/X `build_player_html`も公開出力前に0件を確認(あればSTOP) |
| Y | `build_page_rows(..., audience)`/`render_y_page(..., audience)`/`page_legend_html(decisions, audience)`。`dev`のときだけ凡例に1行「⏸=TTS Chunk分割境界(開発確認用)」 |
| Z | `er063_family_z_audio_01.py` `build_pages(..., audience)`/`_user_page_rows(..., audience)`(Full Story clipのplanで境界表示) |
| X | `er019_...runner_01.py` `build_player_html(..., audience)`/`_build_level_table(..., audience)`(Full Story本文のplan境界表示) |

### devの指定方法(公開用を上書きしない・env/設定での暗黙ONなし)
| Family | 指定 | 出力 |
|---|---|---|
| Y | `py er121_family_y_runner_01.py ... --stage pages --page-audience dev` | `<pages_dir>/index_dev.html`(公開用`index.html`は上書きしない)。`page_verify`はpublic専用(devはSTOP`FAMILY_Y_PAGE_VERIFY_DEV_PAGE`。final manifest対象外) |
| X | `py er019_family_x_audio_production_runner_01.py ... --stage player --page-audience dev` | `<out_dir>/player_dev.html`(`player.html`は上書きしない) |
| Z | `er063.build_pages(run_dir, pages_dir, audience="dev")`(Python呼出の明示引数のみ。Z runner(er026)は既定public) | `<pages_dir>/index_dev.html` |
| 開発用試聴ページ(`user_test/`向け) | 上記のdev出力を`user_test/`へ手動配置(本委任ではしない) | |

## 3. 撤去(`REMOVAL_RESULT_02.md`)/検証(`VERIFY_06.md`)
## 4. 範囲外・注意
- pages再生成なし(`_03`は静的ページのまま)。音声・Chunk分割・ポーズ長・TTS/Style/Voice/Fallback/Gateは不変。
- `pause_scan`/`pause_align`/`pause_stats`はVoice 1候補表の停止統計(解析表)用に残置(Fable判断(b))。
