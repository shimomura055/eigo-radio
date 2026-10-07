# 2026-10-07 OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 委任_02(実行: 旧Note規則再現→18 run 単層4並列→転記確認→評価パック生成)

Management-ID: OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01(委任_02)

## 並行タスク
なし。直前commit 5dbf14c7(委任_01 PLAN_READY)。

## Fable決定(委任_01 §2 要判断1〜7)
1=案A(0/12当時のNote引き継ぎ規則 sha abd16d9a をDEV wrapper `er052_open233_polysemy_nb_dev_01.py` 側で再現。Production runner er019は触らない。単体テスト追加)。2=了承(Meta=nb+固定Note、他4=control)。3=了承(現行Checker=OPEN-238配線後)。4=了承(Rollback主指標JA R2、EN前後併記)。5=了承(`runs/<slug>/<variant>/rep<k>/`)。6=了承(任意フィールド+rollback_X)。7=了承(記録のみ)。

## 性質/到達上限Status/禁止事項
- 性質: Trial(Production経路=未パッチ `runner.run_instance`・承認スイッチ既定、公開なし)。有料。
- 到達上限Status: `RUNS_COMPLETE`(18 run完走+Note到達確認+評価パック生成)または予算/infra STOP。
- 予算: 上限¥500、累計¥480見込みでSTOP、1 run ¥25超でSTOP。checker予算は計画どおり¥15。
- 並列: 単層4(driver_stage2.py流用の `tools/driver_ccp.py`、xargsとの二重並列禁止、memmon、降格4→2→1、infra連続失敗3でSTOP)。Writer内部Gate STOPは回避せず同枠1回のみ再実行(全体上限4回)。
- 禁止: Production変更(er019・Production runner・Checker仕様・承認スイッチ・CURRENT_SPEC)、台帳の内容変更(固定Note追記以外、sha固定)、新テーマ、条件追加、評価の開始(評価者はFableが別起動)、MAP開封、`git add -A`。
- 固定ブロック: E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(TTSなし。T-0=本委任文保存+check.json)。

## 事前指定Read
- `docs/pm/control_checker_polysemy_trial_01/plan_01.md`(全文)、`preregistration_01.md`(全文)、`tools/make_eval_pack_ccp.py`、`approved_switches_dump_plan_dryrun.json`
- `er052_open233_polysemy_nb_dev_01.py`(Note引き継ぎ規則の現行実装と、commit 1fefd10f での変更差分)
- `er052_output/open233_b3_trial_01/tools/driver_stage2.py`、`memmon.py`
- `er052_output/open238_precheck_fix_trial_01/runtime_evidence/provenance.json`

## 事前指定Grep一覧+追記位置・更新位置の手順
Grep: 無し(SSOT編集は本委任の範囲外)。更新位置: `docs/pm/ACTIVE_TASK.md`固定ヘッダ+末尾1行、`docs/pm/RESULT_PACKET.md`上書き。SSOT追記文: なし(REPORT/DECISION_LOG/OPEN_ITEMS反映は別委任)。

## 実行コマンド全文
0. `Get-Process python*` 0件確認。
1. 案A実装: wrapperに旧規則を環境変数 `OPEN233_NOTE_RULE=legacy_abd16d9a` で切替可能に追加(既定は現行のまま)。単体テスト追加→PASS。phase1 dry-runで `transfer_block_sha256=abd16d9a…` を確認。
2. 18コマンドのdry-run → `provenance.json`(未パッチrun_instance、approved_switches_dump一致、台帳sha、wrapper sha、Note規則、git HEAD)。
3. `python docs/pm/control_checker_polysemy_trial_01/tools/driver_ccp.py`(Meta nb rep1〜10、hormuz/space_weapons/sewer/ai_control control rep1〜2)。10 runごとに累計費用記録。完了判定は `runs/driver_result.json`。
4. 完了後: `python er052_output/open233_allfact_note_e2e_02/tools/check_brief_transfer.py <brief.md> <ledger.txt>` でMeta 10本のNote到達を記録。cost集計・Gate STOP・再実行・Checker発火・infra失敗・メモリ最大・降格履歴を `runs/RUN_CHECK.md` に記録。
5. `python docs/pm/control_checker_polysemy_trial_01/tools/make_eval_pack_ccp.py`(完了数18でなければSTOP)。
6. `git diff --name-only` でer019/Production runner/CURRENT_SPEC差分なし確認。
7. `docs/pm/ACTIVE_TASK.md` 更新(RUNS_COMPLETE/評価待ち)、`docs/pm/RESULT_PACKET.md` 上書き(12行以内)。

## Git
個別add(wrapper+test、`docs/pm/control_checker_polysemy_trial_01/*`、`er052_output/open233_control_checker_polysemy_trial_01/`(`_private/`・`__pycache__`・0バイトログ除く)、delegation_log本件)。commit「OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 委任_02: …」+ trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`。push origin main。`git add -A`禁止。

## 報告
20行以内(到達Status、案A実装・テスト・sha確認、18 run内訳、費用、Note到達、Checker発火概況、メモリ・降格、Production未変更根拠、評価パック所在と評価者最小委任文、commit hash・push結果、raw URL)。
RESULT_PACKET項目: 上記報告項目の短縮版。

## 固定ブロック
E-1: Production変更禁止・API支出は上限内。D-1: 詳細証跡は`er052_output/open233_control_checker_polysemy_trial_01/`。G-1: Gate回避禁止・上限超過STOP。F-1: 結果を見て基準を変えない。T-0: 本ファイル保存。T-1/T-2/T-3: TTSなし。
