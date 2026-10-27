# CHUNK_MARKER_DESIGN_01 — 開発用Chunk境界マーカー `⏸` 表示仕様の設計(X/Y/Z共通・開発用限定、委任_07。実装は委任_08)
根拠: USER_04 §1-C・§4。棚卸し=`CHUNK_MARKER_INVENTORY_01.md`。音声生成・Chunk分割・追加0.2秒ポーズは変更しない(表示専用、API 0)。

## 1. 表示仕様
- 実TTS Chunk分割境界(chunk i と i+1 の間、i<最終)にだけ、台本テキスト上で `⏸` を1個置く。秒数・タイムスタンプ・説明文・title属性なし。
- ASR/音声解析の通常ポーズは一切表示しない。
- 境界が0件の記事・segment(例: `_03`)は何も表示しない。
- 凡例は不要(説明文不要の決定)。開発確認用ページ冒頭の既存『この試聴ページの見方』noteには1行(『⏸=TTS Chunk分割境界(開発確認用)』)のみ可。ユーザー指示は『説明文は不要』なので、凡例を残すかはFable判断(`_03`では1行を残置)。

## 2. 開発用/公開用の分離
- 既存に`audience=dev|public`相当の機構は**ない**(`git grep "audience|dev_only|public_only"`=0件)。新設する。
- 新規純関数(提案・単一flag/引数読取、API 0): `chunk_boundary_markers(plan_chunks, audience)`。`audience="dev"`のときだけマーカーを返し、**既定は`"public"`(マーカーなし)**。呼出側がdev指定するのは `pages` stage の `user_test/` 向け試聴ページ生成関数のみ。量産スクリプト(`study_text`/`article.md`/`parts.json`/exporter/将来アプリ出力)は関数を呼ばない(型として呼べない)。
- 禁止: env/設定dict/起動scriptでの暗黙ON(PM_GOVERNANCE 11-7と同趣旨)。
- 公開物への混入防止: (a)`user_test/*/index.html`以外の成果物(`parts.json`/`study_text`/exporter出力/`article*.md`)に`⏸`が含まれないことをtest、(b)`evaluate_page_verify`/`lint_page_html`/`check_page`の検査に『dev指定でない出力にU+23F8/`&#9208;`が含まれたらNG』を追加。

## 3. X/Y/Z共通化の配線点(読むだけで確認済み。編集は並行Agentが触る可能性のため委任_08)
| Family | 配線点 | 境界の取得元 |
|---|---|---|
| Y | `er121_family_y_audio_01.py:1488`(現`_script_with_pauses`→chunk境界版へ置換)、`:1370 page_legend_html` | `audit/chunk_plan_<level>.json`の`plans[sid]["chunks"]`(text/boundary_kind) |
| X | `er019_family_x_audio_production_runner_01.py`のpages生成(`build_player_html :3022`系/各`er019_*page*`)。現状マーカー表示なし=新規追加 | `plan_x_part`(`er117:101`)、`_chunk_plans` |
| Z | `er063_family_z_audio_01.py:2487 _user_page_rows`(script行生成) | `plan_z_clip`(`er117:150`)、`rows`のclip→chunk plan |
| 共通 | 新規共通モジュール(例`er_chunk_marker_display_01.py`)。`er_user_listening_page_common_01.py`の`script_block :40`にaudience引数を足す案も可(要:並行Agent確認後) | `er117`のchunk plan |
マーカー位置: chunk[i].textの末尾直後(台本テキストにchunk textが含まれることを前提。完全一致しない場合は『位置不明』として**表示せずtest/evidenceにWARN**。推定位置は出さない)。

## 4. 撤去する旧表示・旧test(委任_08)
| 識別子 | 場所 | 扱い |
|---|---|---|
| `_script_with_pauses`・`PAUSE_MARK_MIN_MS`・`_PZ_STYLE`(⏸用span) | `er121_family_y_audio_01.py:1233,1236,1337-1353` | 撤去(置換) |
| 配線 `pause_align(pause_scan(row_arr, sr), ...)` の呼出 | `:1488` | 撤去 |
| `page_legend_html`の⏸見本・『実測停止』『▼』文言 | `:1370-1383` | 撤去/1行化 |
| `pause_scan`/`pause_align`本体(`:1236-1335`) | 同 | **Voice 1候補表の停止統計(`:1321 pause_stats`)が使用中**。候補表は『ポーズ表示』ではなく解析表。残置するか、候補表も撤去するかをFable判断(推奨: 解析関数は残置・script表示のみ撤去。ユーザー決定『ASR等のポーズは表示しない』はscriptマーカー対象と解釈) |
| test | `er121_family_y_page_pause_test_01.py`(9件のうち`_script_with_pauses`系を『マーカー0件』assertへ更新)、`er121_family_y_std_chunk_opus_test_01.py:68-70` | 更新 |
| 研究tool `yfb_*`/`yvp_*` | docs/research | 履歴として残置 |

## 5. 検証方法(委任_08)
1. unit: 境界2個のplan→dev出力に`⏸`ちょうど2個、public出力に0個、境界0件→0個、textが台本に見つからない→0個+WARN。
2. 公開物grep: `parts.json`/`study_text`/exporter出力/`article*.md`に`⏸`(U+23F8)・`&#9208;`が0件。
3. X/Y/Z各1runの実`pages`出力(API 0再生成)で、実chunk数(`chunked=true`のsegment)とマーカー数が一致。`_03`は境界0=マーカー0。
4. 旧識別子の残存Grep(`_script_with_pauses|PAUSE_MARK_MIN_MS|&#9208;\d`)=0。
