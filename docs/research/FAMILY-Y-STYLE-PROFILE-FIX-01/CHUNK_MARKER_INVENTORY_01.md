# CHUNK_MARKER_INVENTORY_01 — X/Y/Zの開発用スクリプト表示のポーズ/chunk表示の棚卸し(委任_07、読むのは`git show origin/main:`のみ)
## 1. 表示の生成元(origin/main、Grep `&#9208|⏸|&#9660|▼`)
| 表示 | 生成元(file:line) | 情報源 | Family |
|---|---|---|---|
| `⏸{秒}s@{m:ss}`(例`⏸0.70s@0:39.0`) | `er121_family_y_audio_01.py:1337-1353 _script_with_pauses`(span生成`:1353`、閾値`PAUSE_MARK_MIN_MS=700 :1233`) | **ASR/音声解析**: `pause_scan`(10msフレームRMS<-40dBFS、`:1236`系)+`pause_align`(`:1279`、台本語へ推定割当て) = 完成音声の実測停止。**Chunk分割境界ではない** | Yのみ |
| 凡例note(`⏸1.25s@0:13.7`の見本・『実測した700ms以上の停止』・『▼(TTS実分割位置)の表示は分割があるsegmentでのみ出ます』) | `er121_family_y_audio_01.py:1370-1383 page_legend_html` | 凡例文言 + `chunk_tts_decision.json`の`chunked`集計 | Yのみ |
| 配線点(各パートの台本ブロックへ重畳) | `er121_family_y_audio_01.py:1488`(`_script_with_pauses(..., pause_align(pause_scan(row_arr, sr), ...))`) | 同上 | Yのみ |
| TTS生成単位バッジ | `er121_family_y_audio_01.py:1357-1368 _tts_unit_badge` | `chunk_tts_decision.json`(**実Chunk判定**) | Yのみ(文言のみ・マーカー位置は出さない) |
| `▼`(TTS実分割位置)マーカー | **実装なし**(凡例の文言にのみ登場。`git grep "&#9660\|▼" -- '*.py'`は`:1382`の凡例文のみ) | - | - |
| X(`er019_family_x_audio_production_runner_01.py`)・Z(`er063_family_z_audio_01.py`)・common(`er_user_listening_page_common_01.py`) | **ポーズ/chunkマーカー表示なし**(`&#9208\|⏸\|&#9660\|▼\|pause_align\|chunk.*marker`のGrep=0件)。X: `build_player_html`、Z: `build_listening_page_html :2374`/`_user_page_rows :2487`はscript本文のみ | - | X/Z=現状マーカーなし |
| 旧test | `er121_family_y_page_pause_test_01.py`(9件、`ya._script_with_pauses`/`pause_scan`/`pause_align`/`_tts_unit_badge`/`page_legend_html`をassert)、`er121_family_y_std_chunk_opus_test_01.py:68-70`(`page_legend_html`) | - | Y |
| 研究tool | `docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/tools/yfb_{silence_scan,pause_stats,pause_align}_01.py`、`FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01/tools/yvp_*` | 調査用(測定値の同一性をtestで固定: ya.pause_scan docstring) | 研究 |

## 2. 実Chunk分割境界の正本(音声生成側の記録)
| 記録 | file:line | 内容 |
|---|---|---|
| chunk plan | `er117_chunk_tts_production_01.py:101 plan_x_part`(X: 段落分割、`boundary_kind="paragraph"` `:110`)、`:150 plan_z_clip`(Z: 段落/文境界、`boundary_kind`は`paragraph`or`sentence` `:193`)。Y: `_record_chunk_decision`(`er121_family_y_audio_01.py:405`)が`audit/chunk_plan_<level>.json`+`chunk_tts_decision.json`を保存 | `plan["chunks"][i]`: chunk_id/index/text/words/boundary_kind |
| 境界の時刻 | `er117:294-305 compose_gained_parent` `boundary_offsets_s`(各0.2秒無音の開始・終了秒、part内) + `er019:2458 _chunk_assembly_summary_x`(episode内`gap_offsets_in_episode_s`) / Y: `_chunk_assembly_summary_y`(`er121_family_y_audio_01.py:1212`) | **分割境界はASR不要で台本テキスト上の位置(chunk text境界)と音声内offsetが記録済み** |
| 今回`_03`の実Chunk境界 | `run_style_fix_01/{a2,b1b}/audit/chunk_tts_decision.json`: 全8 segment `chunked=false`(`paragraphs=1`) | **0件**(実境界なし) |

## 3. 区別の整理
- ⏸の現行意味 = ASR/音声解析で検出した通常の音声ポーズ(ユーザー決定Cで『表示しない』対象)。
- 承認仕様の⏸ = 実Chunk分割境界のみ(上記2の記録から決定論的に導出可能)。両者は情報源が異なる。
- Y以外(X/Z)は現状どちらも表示なし → 『X/Y/Z共通仕様』は現状Yの是正+X/Zへの新規追加(開発用表示のみ)となる。
