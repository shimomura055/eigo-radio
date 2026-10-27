## 管理ID

FAMILY-Y-STYLE-PROFILE-FIX-01 委任_08(ユーザー正式決定2026-10-27 B/C(原文=`docs/pm/delegation_log/2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_USER_04.md` §1-B/C・§3・§4)のProduction実装: (B)Family Y共通Voice説明文の単一ソース`PAGE_NOTICE_JA`を承認文言「Voice 1〜3は実在人物の発言をそのまま再現したものではなく、実際に投稿された意見をもとに、AIが編集・再構成したものです。」へ置換(実投稿に基づく記事=Theme Packageの`experiences[].source_ids`で機械判定、根拠のない出典主張を生成しない)、旧文言のtest 3件更新、(C)開発用Chunk境界マーカー: 実TTS Chunk分割境界(`er117_chunk_tts_production_01.py`の`boundary_offsets_s`等)のみ`⏸`(秒数・説明なし)、ASR/音声解析ポーズ表示(`_script_with_pauses`/`PAUSE_MARK_MIN_MS`、`er121_family_y_audio_01.py:1337-1353,:1488`)は撤去、`audience=dev|public`(既定`public`=マーカーなし、開発用ページのみ`dev`)をX/Y/Z共通の表示機構として新設、公開物にマーカー0件のtest、旧表示処理・旧testの整理、`_03`との整合確認(pages再生成はしない)。設計=`CHUNK_MARKER_DESIGN_01.md`/`CLOSEOUT_PLAN_01.md`/`CHUNK_MARKER_INVENTORY_01.md`(委任_07、commit 945b07a28)。API 0・JPY0)。並行Agent: (a)GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05A(`er120`核/`er119_grammar_review`/`er128`/CLI/exporter=編集しない)、(b)AI-ISLAND-FORM-PRODUCTION-01 委任_02(フォーム=編集しない)。runner/ページbuilderは委任_03完了済み(origin/main c3b83a3e0)=編集可。あなたの所有=`er121_family_y_structure_01.py`、`er121_family_y_audio_01.py`(表示部のみ。Style Gate/TTS/KP部は不変)、`er121_family_y_runner_01.py`(pages stageの`audience`引数配線のみ)、`er063_family_z_audio_01.py`/`er019_family_x_audio_production_runner_01.py`/`er_user_listening_page_common_01.py`(`audience`引数の受け口・マーカー描画の共通化のみ)、`er117_chunk_tts_production_01.py`(読み取りのみ。境界記録の取得関数を追加する場合は非破壊で)、関連test(`er121_family_y_text_core_article_test_01.py:988-1000`、`er121_family_y_runner_01_test_01.py:262`、`er121_family_y_structure_match_test_01.py:267`、page_pause test、新規`er_page_audience_marker_test_01.py`)、`docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{IMPLEMENTATION_08,REMOVAL_RESULT_02,VERIFY_06}.md`、`docs/pm/delegation_log/2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_08.md`(+check.json)、`docs/pm/RESULT_PACKET_YSP8.md`(gitignore、`-f`禁止)。SSOT編集権なし。pathspec付きcommit(他Agentのstage分を巻き込まない)。

## 性質/禁止

- 性質: 承認済み表示仕様(文言・マーカー)のProduction実装。品質基準・音声仕様の変更なし。到達上限=IMPLEMENTED+test。
- 禁止: Chunk分割・ポーズ長・TTS/Style/Voice/Fallback仕様の変更、`_03`のpages再生成(静的ページは委任_07で是正済み。再生成すると旧表示が戻る可能性があったが本委任後は新表示=再生成は不要なので行わない)、公開物(public)へのマーカー出力、Y以外の説明文新設(X/Zに同文言を入れない)、所有外編集、禁止Git操作(`add -f`/`pull --rebase`/pathspecなしcommit)。
- 時間見込み: 約2.5h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_08.md` をN=726から順に試し、先頭「## 管理ID」+「FAMILY-Y-STYLE-PROFILE-FIX-01 委任_08」のものを採用。

## 実施事項

1. **Voice説明文**: `er121_family_y_structure_01.py:100 PAGE_NOTICE_JA`を承認文言へ(逐語)。適用条件=Theme Packageの`experiences[].source_ids`が非空(実投稿に基づく)の場合に表示、それ以外は表示しない(根拠のない出典主張を生成しない)。旧文言のassert 3件を新文言へ更新。DEV `er110_family_y_redelivery_revision_01.py:39`は凍結(無変更)。将来のアプリ表示用に同文言を定数として参照可能に(SSOT文案に「アプリ表示でも同一文言」)。
2. **Chunk境界マーカー(X/Y/Z共通)**: `er_user_listening_page_common_01.py`に`audience`引数(`public`既定/`dev`)と、実Chunk境界のみ`⏸`を本文スクリプトに差し込む共通関数(境界情報=`er117`のplan/`boundary_offsets_s`等、ASRポーズは使わない)を新設。Y `er121_family_y_audio_01.py`の`_script_with_pauses`(実測ポーズ表示)を撤去し共通関数へ置換、`▼`凡例文の整理、`PAUSE_MARK_MIN_MS`等の旧定数撤去(pause_scan/pause_align/Voice 1候補表の停止統計は残置=Fable判断(b))。X/Zは共通関数の受け口のみ(現状マーカー表示なし=publicで不変、devで境界表示可)。runnerのpages stageは既定`public`。開発用試聴ページ(`user_test/`向けのbuild tool経路)は`dev`を明示できるように(どのtool/引数で`dev`を指定するかを`IMPLEMENTATION_08.md`に明記)。
3. **test**: 公開物(public)に`⏸`/`&#9208;`が0件、devで実Chunk境界数と一致、ASRポーズでは出ない、Y説明文の条件付き表示、X/Zに説明文が出ない、既存page_pause test(9件)の置換/撤去、Y Style/HR guard testの回帰。全体回帰: `er121_*`、`er019_*`、`er026_*`/`er063_*`、`er062_*`、`er117_*`。
4. `REMOVAL_RESULT_02.md`(撤去識別子と残存Grep 0件)、`VERIFY_06.md`(`_03`の現行静的ページがProduction builderの新出力と整合することをdry build(ファイル出力なし or scratchへ出力)で比較=本文/KP/音声参照不変、説明文一致、マーカー0件)。

## 事前指定Read一覧

- `docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{CHUNK_MARKER_DESIGN_01,CHUNK_MARKER_INVENTORY_01,CLOSEOUT_PLAN_01,VERIFY_05}.md`、`tools/build_page_05.py`
- `er121_family_y_structure_01.py:90-115`、`er121_family_y_audio_01.py`(Grep `_script_with_pauses|PAUSE_MARK|⏸|▼|PAGE_NOTICE|pause_scan|pause_align` ±10)、`er121_family_y_runner_01.py`(Grep `pages|build_pages|PAGE_NOTICE|source_ids` ±5)、`er117_chunk_tts_production_01.py:95-110,145-155,290-310`、`er_user_listening_page_common_01.py`(全体)、`er063_family_z_audio_01.py`(Grep `build_pages|study_html_by_level` ±5)、`er019_family_x_audio_production_runner_01.py`(Grep `build_player_html|level_section_html` ±5)
- test: `er121_family_y_text_core_article_test_01.py:980-1005`、`er121_family_y_runner_01_test_01.py:255-270`、`er121_family_y_structure_match_test_01.py:260-275`、page_pause test(Grep `pause` in `er121_*test*`)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_FAMILY-Y-STYLE-PROFILE-FIX-01_DELEGATION_08.md --json-out ...\_check.json`
- test: `.venv\Scripts\python.exe run_project_regression.py --pattern "er121_*_test_*.py"`、`--pattern "er019_*_test_*.py"`、`--pattern "er026_*_test_*.py"`、`--pattern "er063_*_test_*.py"`、`--pattern "er062_*_test_*.py"`、`--pattern "er117_*_test_*.py"`、`--pattern "er_page_audience_marker_test_01.py"`(既存失敗=OPEN-543・GPG3報告の3件は切り分け)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_YSP8.md`にCURRENT_SPEC文案(Y Voice説明文の正式文言・適用条件・アプリ表示同一、Chunk境界マーカー表示仕様=開発用限定・X/Y/Z共通・既定public)、OPEN-537/539追記、OPEN-543関連。

## Git

- commit message: `FAMILY-Y-STYLE-PROFILE-FIX-01 委任_08: Y Voice説明文を承認文言へ(実投稿記事のみ表示)+Chunk境界マーカー⏸を開発用表示(audience=dev)に限定しASRポーズ表示を撤去(X/Y/Z共通機構、公開物マーカー0件test)(API 0)`。trailer: `Delegation: FAMILY-Y-STYLE-PROFILE-FIX-01/08`。push。

## 報告

`docs/pm/RESULT_PACKET_YSP8.md`: (0)T-0、(1)差分(ファイル:行)、(2)test・回帰(切り分け)、(3)`_03`整合(VERIFY_06)、(4)判断候補、(5)必須4行+「判定整合: 重大NG=<なし|あり>」、(6)SSOT文案、commit hash・raw URL。末尾5行要約。