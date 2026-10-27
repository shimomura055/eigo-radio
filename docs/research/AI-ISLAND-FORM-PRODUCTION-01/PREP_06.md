# PREP_06 HR承認後の手順書(AI-ISLAND-FORM-PRODUCTION-01、AI島Std/Adv、2026-10-27)
前提: reconsume・Std Part 1生成・ハイライト解決確認は完了(`RECONSUME_01.md`)。M3 Style Gate(`full_story_part1_k2`、`LOCAL_REWRITE_RECOVERY`)のBLOCKのみ未解除。承認が出るまで以下は実行しない。以降の全工程で**API 0**(LLM/TTS/ASR呼出なし)。作業は全て`C:\Users\tensh\eigo-radio`、`.venv\Scripts\python.exe`。
各工程の前に`tools/stop_scope_check_01.py --managed-id AI-ISLAND-FORM-PRODUCTION-01 --run-dir <run> --out <json>`(rc=3なら停止)。runner起動間隔150秒以上。

R=`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01`

## 0. 承認原文の保存(ユーザー承認後)
`docs/pm/delegation_log/<日付>_AI-ISLAND-FORM-PRODUCTION-01_USER_05.md`へ逐語保存(承認level[Std/Adv/両方]を確認)。HR_PACKET_02=`HR_PACKET_02.md`/`user_test/family_x_ai_island_form_01/hr_02.html`。

## 1. record_human_approval(承認levelのみ。所要数秒)
canonical textは`tts_generation_results.json`のsegmentの`canonical_text`(=元原稿の文、`The AIs sent to ...`。LR後の`text`ではない)。
```
.venv\Scripts\python.exe -c "import json,er003_v1_n3_01_assemble as a; R='er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01'
for lv in ['a2','b1b']:   # 承認したlevelだけに絞る
    d=json.load(open(f'{R}/{lv}/audit/tts_generation_results.json',encoding='utf-8'))
    a.record_human_approval(f'{R}/{lv}', 'full_story_part1_k2', d['segments']['full_story_part1_k2']['canonical_text'], 'user')"
```
(`<R>/<lv>/audit/human_approved_segments.json`へshaが書かれる。Gateの`_approved`=`er019_family_x_style_profile_01.py:629-634`と同一canonical。片方のみ承認の場合は該当levelのみ実行し、未承認levelはBLOCKのまま=下記2は承認levelだけ`--level a2|b1b`で。)

## 2. assemble(API 0、目安1〜3分/level。前回BLOCK時は約10秒)
```
.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug ai_island_temple --run run_form_prod_01 --stage assemble --level both
```
確認: rc=0、両level `BLOCKED_STYLE_PROFILE_GATE`が消え、`<R>/<lv>/assembled/`に通しmp3(wav)+Audio Validation Gate PASS、`run_summary_assemble.json`。BLOCKが残る場合は`LOCAL_REWRITE_RECOVERY`/`STD_FALLBACK_USED_OR_UNKNOWN`の別違反が残っていないか確認(Stdは両方出ていたため`_approved`のみで解除されるかをここで確認)。

## 3. player(API 0、目安数秒。前回実績約11秒)
```
.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug ai_island_temple --run run_form_prod_01 --stage player --level both
```
`player.html`にhighlights・Std Part 1(ちょうど1個)・Part 2が入る。`validate_part1_block_count`/`verify_x_player`(G1-G4)がrc=0。

## 4. 標準builder(公開ページ。API 0、目安数十秒)
```
.venv\Scripts\python.exe er019_family_x_listening_page_01.py --slug ai_island_temple --run-name run_form_prod_01 --web user_test/family_x_ai_island_form_01
```
内部で必須検査(いずれか落ちたらindex.htmlを書かない=PageStop): (1)ハイライト解決(ISSUE 0、Std `Strategy`のNOTICE=記録のみ) (2)`check_page(public)`(⏸/chunk-mark 0) (3)G3`verify_highlights`(装飾10/10×2、③訳、本文不変、public混入なし) (4)Part 1個数(Std・Adv各ちょうど1個) (5)Part 2四者一致(文法0件=ZERO)。出力: `user_test/family_x_ai_island_form_01/index.html`+`audio/ai_island_temple_{Standard,Advanced}.mp3`(名称は標準builder仕様)。既存の`hr_01.html`/`hr_02.html`/`hr/`は上書きしない。

## 5. 公開とpage_verify
```
git add user_test/family_x_ai_island_form_01/index.html user_test/family_x_ai_island_form_01/audio <担当docs>
git commit -m "AI-ISLAND-FORM-PRODUCTION-01: AI島Std/Adv最終試聴ページ公開(新表示仕様、HR承認後)"
git push origin HEAD:main
```
GitHub Pages反映後(数分): `curl.exe -sI https://shimomura055.github.io/eigo-radio/user_test/family_x_ai_island_form_01/index.html`(200)・`curl.exe -s ... | findstr` で装飾マーク/Part 1見出し/凡例を確認、音声URL 2本200。必要に応じ`docs/research/AI-ISLAND-FORM-PRODUCTION-01/tools/browser_check_aif*.mjs`系のheadless確認(用法は先頭コメント)で実DOM確認(Std/Advの①②③装飾・Part 1表示)。
API 0確認: 各工程後に`<R>/raw_usage_log.jsonl`行数・`cost_breakdown`累計が36.94円から不変であること。

## 注意
- 承認前にassemble/player/公開を実行しない。承認は人間ユーザーのみ(Gate緩和ではなく`record_human_approval`の正規経路)。
- 再生成が必要になった場合(承認NG等)は新たなHR/有料判断(HR_PACKET_02の判断候補a〜c)が前提。
