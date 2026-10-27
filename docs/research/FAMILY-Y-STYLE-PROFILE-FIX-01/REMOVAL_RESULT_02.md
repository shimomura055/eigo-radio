# REMOVAL_RESULT_02 — 旧表示処理・旧test・旧文言の撤去/残置(委任_08)
| 識別子 | 場所 | 扱い | 残存Grep |
|---|---|---|---|
| `_script_with_pauses`(実測ポーズ⏸重畳) | `er121_family_y_audio_01.py` | 撤去(共通`script_block`の実Chunk境界へ置換) | 0 |
| `PAUSE_MARK_MIN_MS` | 同 | 撤去 | 0 |
| `_PZ_STYLE`(⏸用span style) | 同 | 撤去 | 0 |
| `_mmss`(上記専用helper) | 同 | 撤去 | 0 |
| `pause_align(pause_scan(...))`の`build_page_rows`内呼出 | 同 | 撤去 | 0 |
| `page_legend_html`の⏸見本「&#9208;1.25s@0:13.7」「実測…推定」「&#9660;(TTS実分割位置)…」 | 同 | 撤去(devのみ1行) | 0 |
| 旧`PAGE_NOTICE_JA`「本コンテンツのVoiceは、実在する人々の意見を参考に…」 | `er121_family_y_structure_01.py` | 承認文言へ置換 | Production py: 0(下記の履歴/凍結を除く) |
| 旧test: `PauseScanTest.test_stats_keys_and_align...`の`_script_with_pauses`assert、`test_below_mark_threshold_not_shown`、`test_r5_legend_last_sentence...`(『今回はありません』)、`test_page_notice...matches_dev_when_available`(旧文言+DEV一致) | page_pause test/std_chunk_opus test/text_core_article test | 更新/置換(`test_asr_pause_is_never_rendered_into_script`等) | 0 |
| **残置(意図的)** `pause_scan`/`pause_align`/`pause_stats`/`PAUSE_SCAN_*`/`PAUSE_MID_CLAUSE_MIN_MS` | `er121_family_y_audio_01.py` | Voice 1候補表の停止統計(解析表。Fable判断(b)) | 使用箇所=`voice1_candidates_aux_html`のみ |
| **凍結(無変更)** DEV `PAGE_NOTICE_JA`(旧文言) | `er110_family_y_redelivery_revision_01.py:39` | DEV Trial。Production非参照 | 1(意図) |
| 履歴(変更しない) | `docs/research/**`の設計doc・旧tool(`build_page_04/05.py`)、`user_test/family_y_production_redelivery_fee_01`(旧版) | 履歴 | 履歴のみ |

Grep(`git grep -nE "_script_with_pauses|PAUSE_MARK_MIN_MS|_PZ_STYLE|def _mmss"` *.py): 0件(自己参照のtestファイル`er_page_audience_marker_test_01.py`/`er121_family_y_page_pause_test_01.py`の「撤去確認」記述のみ)。旧文言(`実在する人々の意見を参考に`)のProduction py: 0(`er110`凍結・testの「旧文言は無い」assert・履歴docのみ)。
