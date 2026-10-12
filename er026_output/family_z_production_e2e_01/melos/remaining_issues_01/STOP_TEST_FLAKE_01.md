# STOP_TEST_FLAKE_01 (FAMILY-Z-MELOS-E2E-REMAINING-ISSUES-01 項目4、2026-10-12、有料API 0)

## 事前の再現(修正前、同一条件で連続実行)
| run | 結果 | 備考 |
|---|---|---|
| pre_run1 | 16/16 OK | |
| pre_run2 | **13 tests、failures=4、skipped=2** | item3 `rc 2!=3`、item4b `FileNotFoundError .../run_stoptest_4b2_mock/writer/std.md`、item4d `rcs [3,3,3]!=[0,0,3]`、item6 `rc 3!=0`(STOP_ALL存在のSTOP_SENTINEL) |
| pre_run3 | **0 tests、skipped=8**(全クラスが setUpClass で「STOP_ALLが既に存在」→Skip) | |
| pre_run4〜6 | 16/16 OK | |
- 失敗は毎回別test・別内容(ユーザー報告と一致)。失敗時のstderrはcp932/UTF-8不一致の文字化け(`�`)も含む(症状であり原因ではない)。

## 切り分け(証拠)
1. **原因(主): 同じtestを複数プロセスが同時実行**していた。本testは共有の固定資源を使う:
   `melos/run_stoptest_*`(setUpClass/tearDownClassの`purge_test_runs`が全削除)、`evidence_12A/`、実パス`STOP_ALL`(item4a/4c/6/7が一時作成→削除)。
   2プロセス同時実行だと、片方のpurgeが相手のrun dirを消す(FileNotFoundError/rc不一致)、片方が置いたSTOP_ALLを相手が見てSkipまたはrc=3になる。
   - 再現実験: 修正前に同一testを2プロセス同時起動(pre_conc_A/B)→ item1 `0 not >= 3`(TTS段に到達せず)・item3 `0!=3`・
     item6系 `3!=0`(STOP_ALL存在)・`FileNotFoundError run_stoptest_01/STOP`・skipped=5 と、pre_run2/3と同種の失敗を再現。
   - 環境上、他agent(ASR調査・KP Idiom等)やFableが同じtestを並行実行しうるため、「再実行ごとに別test失敗」になる。
   - STOP機構の実装問題ではない(単独実行は12/12連続で16/16 PASS)。
2. **原因(副): tool `tools/stop_all_family_z.py` のsubprocessデコード脆弱性**。`subprocess.run(["powershell",...], text=True)`はlocale依存で
   デコードする。testにPYTHONUTF8=1を足すとPowerShell出力(cp932)をutf-8でdecodeして失敗→`stdout=None`→`AttributeError`/空stdout→
   item7 `JSONDecodeError`(post_conc_A/Bで実際に再現し発見)。素の環境でも他プロセスのcommand lineに変換不能文字があれば同じ破綻になり得る
   (緊急停止ツールとして好ましくない)。
3. **副次: testのsubprocess encoding未指定**(`capture_output=True, text=True`のみ6箇所)。子stderr/stdoutの日本語がcp932でデコードされ、
   文字化けや将来のdecodeエラー要因。

## 修正(最小)
- `er026_family_z_stop_sentinel_test_01.py`: (a)module全体のprocess間排他lock(`melos/.stoptest_exclusive.lock`、PID生存確認で stale lock奪取、最大900秒待機、
  setUpModule/tearDownModule/atexitで解放)(b)子processへPYTHONIOENCODING=utf-8/PYTHONUTF8=1を継承し、全`subprocess.run`に`encoding="utf-8", errors="replace"`を明示。
- `tools/stop_all_family_z.py`: PowerShell出力を`[Console]::OutputEncoding=UTF8`で固定し、bytesを`utf-8, errors=replace`で明示decode(BOM除去、`stdout=None`安全化)。
  実装機能(STOP_ALL作成/プロセス停止/audit)は不変。
- STOP機構本体(`er062_family_z_structure_01.py`/runner)は無改変。

## 修正後の検証
- 連続10回(順次): **10/10 rc=0、各回 16/16 OK**(`stoptest_post_run1..10.log`、summary `stoptest_post_summary.txt`)。
- 2プロセス同時起動(修正後): 2回目はlock待機で直列化され**両方 16/16 OK**(post2_conc_A=113秒、B=222秒=待機込み)。
  (修正途中のpost_conc_A/Bは tool未修正+PYTHONUTF8のitem7のみ失敗=上記2.の発見ログ)
- Regression(mock/dry-run、有料API 0): 本testがrunner実体を`--mode mock`で起動し、item1 STOP中断・item2 retry/fallback/cooldown・item3 regenerate/resume・
  item4a STOP_ALL(全起動経路)・item4b RUN_LOCK・item4d RESTART_STORM・item5 real run拒否/費用不変・item6 STOP解除・item7 緊急停止ツールを検証済み
  (12回連続16/16)。新しい別名runでの追加起動は不要と判断(同じ経路をtestが別名run `run_stoptest_*` で網羅しているため)。
- 実装(tool)を変更したため関連suiteを再実行: er026統合 42/42 OK(`regress_integ`、スクラッチ保存)、runner 21/21 OK、er062 64/64 OK、er063 47/47 OK。

## 注意・残課題
- 統合test `test_shared_state_files_unchanged_by_mock_run` は `er026_output/family_z_production_e2e_01` 全体のファイルサイズ/mtimeをsnapshotするため、
  同treeへ他agentやログが書込むと失敗する(今回、本委任のlogをその配下に置いた1回目に失敗→配下外へ出すと42/42 OK)。別種のflake(OPEN-324候補)。
- 本testは実パスSTOP_ALLを数秒間作成する。その間、他agentのreal runが誤って「STOP_ALL」でSTOPされる副作用リスクが原理的にある
  (lockはtest同士のみ排他)。STOP_ALL_PATHをtestごとに差替可能にする改修は実装変更が大きく本委任では行わない(要判断)。
