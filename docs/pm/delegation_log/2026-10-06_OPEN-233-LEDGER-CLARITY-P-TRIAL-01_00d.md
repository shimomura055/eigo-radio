## 管理ID
OPEN-233-LEDGER-CLARITY-P-TRIAL-01(委任_00d: 評価表テンプレートとBefore/After決定論diffスクリプトの先行準備、Phase 0並行、¥0)

## 性質/到達上限Status/禁止事項
性質: Trial用DEVツール準備(新規ファイルのみ)。到達上限: 準備完了報告。禁止: 既存コード(runner/er003/checker)の変更/有料API/Trial実行/Production変更/SSOT編集/git。他の並行委任が書く `docs/pm/ledger_clarity_p_trial/00a_*.md`・`00b_*.md`・`00c_*.md`・`er052_output/open233_ledger_clarity_p_trial_01/phase0/FREEZE_P01.json`・`docs/pm/ACTIVE_TASK.md` には触らない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1/D-1/G-1/F-1: 該当なし(¥0)。T-0: 本委任文を `docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_00d.md` に逐語保存し `python docs/pm/tools/check_delegation_prompt.py --file <パス> --json-out <同名_check.json>`(FAILでも続行)。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
「④Factそのものの安全性: P'による明確化で、新しいFactの追加/原資料にない主体・因果・時系列/否定・肯定の反転/数字・日付・固有名の変化/原資料より強い断定を作っていないこと。必須条件。」「Before/Afterについて最低限、Fact意味一致/HC-012型の曖昧さ/B3 brief/Writer記事/真の重大NG/Checker判定/Entertainment品質まで比較する。」「独立作業は並列化、評価表準備・Trial用script準備を先行」。

## 事前指定Read一覧
- `docs/pm/ledger_clarity/05_trial_plan.md` §1と §4
- `docs/pm/ledger_clarity/04_design.md` §3「M3」「M4」段落のみ
- `er052_open233_stage1_coverage_checker_01.py` L437-526
- `er003_v1_en_direct_vfl_01_generate.py` L275-305

## 事前指定Grep一覧+追記位置・更新位置の手順
1. 決定論diffスクリプト `er052_output/open233_ledger_clarity_p_trial_01/tools/ledger_diff_p01.py`(新規)。判定はしない。IDが一致しないfactは類似claim(Jaccard上位1件)を候補併記、自動対応付けは確定しない。
2. 評価表テンプレート `docs/pm/ledger_clarity_p_trial/00d_eval_template.md`(新規、60行以内)。品質①〜④。
3. After側Entertainment指標スクリプト `er052_output/open233_ledger_clarity_p_trial_01/tools/ent_metrics_p01.py`(新規)。
4. 動作確認(¥0): meta run_03台帳で自己diff(差分0)、ent_metricsをmeta b1b article.mdで実行。結果は報告のみ。

## 実行コマンド全文
- `python er052_output/open233_ledger_clarity_p_trial_01/tools/ledger_diff_p01.py --before er019_output/meta/run_03/ledger/verified_fact_ledger.txt --after er019_output/meta/run_03/ledger/verified_fact_ledger.txt --out er052_output/open233_ledger_clarity_p_trial_01/tools/selftest_diff`
- `python er052_output/open233_ledger_clarity_p_trial_01/tools/ent_metrics_p01.py --article er019_output/meta/run_03/b1b/article.md --ledger er019_output/meta/run_03/ledger/verified_fact_ledger.txt --out er052_output/open233_ledger_clarity_p_trial_01/tools/selftest_ent.json`
- `python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_00d.md --json-out docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-P-TRIAL-01_00d_check.json`

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目、8行以内)
(1)作成ファイル3本のパス・行数 (2)自己diffの結果(差分0か) (3)ent_metricsのBefore値(meta b1b) (4)regex再利用可否 (5)T-0結果
(注: 本ファイルは委任文の要点圧縮を含む保存版。詳細な事前指定文言は一部要約)
