# 委任_E1 OPEN-233-META-ALLFACT-NOTE-ENT-TRIAL-01: Meta記事で全fact一律の多義語注意2パターン(P1多義のみ/P2多義+従来notes)×N=1をJA→EN→Checkerまで実行し、精度・エンタメ性を見る。上限¥200。

## 管理ID
OPEN-233-META-ALLFACT-NOTE-ENT-TRIAL-01(委任_E1)。ユーザー承認済み。

## 性質/到達上限Status/禁止事項
性質: Trial実行(有料)+評価+Closeout。到達上限: USER_DECISION_REQUIRED。禁止: 新framework、Note文言変更、Production変更、CURRENT_SPEC編集、Control再実行、git add -A、E2E state書込、残11 run再開。E-1上限¥200、D-1 cost.json、G-1 Trial限定、F-1 fail-closed(停止時は各1回のみ再実行)。T-2 TTSなし。T-3 対象外。実費¥120で有料実行停止。

## 事前指定Read一覧
- er052_output/open233_meta_rollback_minimal_note_01/runs/manifest.json と _launch.sh(phase1コマンド)
- 同 ledger/control/research_ledger/verified_fact_ledger.txt、FREEZE.json
- er052_open233_polysemy_nb_dev_01.py L38-51、docs/pm/polysemy_trial_04/phase2_readme.md
- er052_output/open233_ledger_clarity_p_trial_01/tools/{ja_copy_rate_p01,ent_metrics_p01,pairwise_p01}.py

## 事前指定Grep一覧+追記位置・更新位置の手順
- REPORT末尾に§93追記、DECISION_LOG末尾に1エントリ、OPEN_ITEMS OPEN-237行へ追記、ACTIVE_TASKへ本ID行追加(他行維持)。
- Grepは追記位置確認用(## §92見出し、OPEN-237行)のみ。

## 実行コマンド全文
- python er052_output/open233_meta_allfact_note_ent_01/tools/gen_ledgers.py --out ledger (台帳生成)
- python er052_output/open233_meta_allfact_note_ent_01/tools/check_diff.py --json-out diff_report.json (決定論diff)
- bash er052_output/open233_meta_allfact_note_ent_01/runs/_launch.sh p1 "注意(多義):" phase1 8 内部: er052_open233_polysemy_nb_dev_01.py --phase phase1 --slug meta --budget-jpy 8 --yes-run-paid (p2は prefix "注意:")
- 同 _launch.sh phase2 15 内部: er052_open233_polysemy_nb_dev_01.py --phase phase2 --budget-jpy 15 --yes-run-paid (EN+Checker)
- 注: runner制約で out-dir は runs/meta/nb/p1(p2)/rep1(/nb/必須)。

## SSOT追記文
REPORT §93(§93-1〜6、40行以内)、DECISION_LOG末尾1エントリ(決定=Trial実施のみ)、OPEN-237追記、ACTIVE_TASK行。詳細は評価ファイル eval/E_allfact_ent_01.md。

## Git
個別add: OPEN_ITEMS.md DECISION_LOG.md OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md er052_output/open233_meta_allfact_note_ent_01/ 本delegation_log。commit後 push origin main。

## 報告
RESULT_PACKET: 台帳diff/実行状況/brief転記/rollback3分類/指標表/pairwise/Checker/実費/Production無変更/commit/T-0/記事全文パス。
