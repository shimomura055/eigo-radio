FABLE-DELEGATION-MARKER: TEST-HYGIENE-FIX-委任_01-20261022

# 委任(TEST-HYGIENE-FIX-01 委任_01: 本日の切り分けで「既存失敗(本日由来でない)」と確定した2件のtest是正。(1)`er011_open112_trend_synthesis_mode_production_wiring_01_test_01` DefaultByteParity 3件=承認済みTTS記号正規化修正(commit d89e9068b、2026-09-27)でPromptの`COMMON_BLOCK_TEMPLATE`に時刻コロン例外文が入った後、fixture `er011_output/open112_trend_synthesis_mode_production_wiring_01/fixtures/common_block_baseline_*.txt`が未更新。(2)`er007_ja_scg_test_01` AzureStrictCancelTests 3件=`mock.patch("azure.cognitiveservices.speech...")`が単独実行時にsubmodule未importでAttributeError。API 0・JPY0)

## 管理ID
TEST-HYGIENE-FIX-01 委任_01(新規・軽微。並行: PNAP 委任_02(er006/er019/er063/Store)、KP3V 委任_02(er104/er078)、KPFT 委任_01(設計)。本委任が触るのは上記fixture・er007 test・OPEN_ITEMS/REPORT_LEDGERのみ。共有SSOTは`git status`→該当行再Grep→自分の行だけ→即add+commit、`index.lock`は30秒待ち)。

## 性質/禁止
- test/fixture整備(Production無変更)。到達Status: 新規OPEN「TEST-HYGIENE-FIX-01」`FIXED_RECORDED`。Opus非該当。JPY0。
- **(1)の前提確認が必須**: fixture更新は「現在のProduction Prompt(`COMMON_BLOCK_TEMPLATE`)が承認済み内容である」場合のみ可。`git log -S"時刻" -- <template file>`等でd89e9068bが承認済み修正(DECISION_LOG Grep `TTS記号正規化|d89e9068b|OPEN-`該当)であることを確認し、**それ以外の差分(未承認のPrompt変更)がfixture差分に含まれていないこと**をdiffで確認してから、fixtureを現行templateから再生成する(生成手順は当該test/fixture作成scriptに従う)。未承認差分が混じっていれば更新せず報告。
- (2)はtest先頭で`import azure.cognitiveservices.speech  # noqa`(try/exceptでskipに落とす形が既存慣習ならそれに合わせる)を追加。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret_scan hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore。SSOT全文読込禁止。他agentの未commit差分を混ぜない。Production .py・Prompt本体の編集禁止。

## 実行
1. (1)確認→fixture再生成→`.venv\Scripts\python.exe run_project_regression.py --pattern "er011_open112*_test*.py"` PASS。
2. (2)修正→`.venv\Scripts\python.exe -m unittest er007_ja_scg_test_01` 46/46 PASS(単独実行)。
3. 併せて`er019_family_x_audio_production_runner_01.py`の`--scaffold-only kp`再実行がKP残骸で`_kp_already_generated` guardに当たる件(KPMP 委任_03の判断候補)は、**記録のみ**: OPEN-452へ「再実行は`--stage scaffold`で可。`--scaffold-only kp`の残骸退避は運用手順として必要時にFableが明示判断」と1句追記(コード変更なし)。
4. SSOT: OPEN_ITEMS新規行(最新+1)、REPORT_LEDGER 1行。T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_TEST-HYGIENE-FIX-01_委任_01.md`(Nは`FABLE-DELEGATION-MARKER: TEST-HYGIENE-FIX-委任_01-20261022`を含むAgent tool_useの通番、288前後。先頭行で一致確認)。
5. commit(`TEST-HYGIENE 委任_01: 既存失敗test 2件是正(er011 parity fixtureを承認済み現行templateへ再生成/er007 azure import)、Production無変更、¥0`)→push。`RESULT_PACKET_TH1.md`(確認結果・差分・Regression・RESULT_PACKET 4行・raw URL)。