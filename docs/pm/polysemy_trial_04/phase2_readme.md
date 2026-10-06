# Phase 2手順(OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-04、DEV、Production非変更)
前提: Phase 1(B3+JA R0/R1/R2)完了済みの10 run(5 slug x control/nb)。out-dir規約: er052_output/open233_polysemy_trial_04/runs/<slug>/<control|nb>/rep1/ 。Checkerは .../rep1/ と同階層の `.../<slug>/<control|nb>/checker/`。既存checkerがあればSTOP。
slug: meta, hormuz, space_weapons, sewer, ai_control。Phase 2対象は「必要なら」(ユーザー指示)で大規模反復はしない。rep1のみ。
1 EN継続(brief/R2再利用、--stop-after advanced、既定JPY10)。<topic>/<ledger.txt>はPhase 1と同一:
`OPEN233_B3_VARIANT=<control|nb> .venv/Scripts/python.exe er052_open233_polysemy_nb_dev_01.py --theme "<topic>" --slug <slug> --ledger-txt <固定ledger.txt> --out-dir er052_output/open233_polysemy_trial_04/runs/<slug>/<control|nb>/rep1 --phase phase2 --yes-run-paid`
(dry-run=JPY0は --yes-run-paid を --dry-run に替える。Phase 2コマンドはrunner内でChecker起動も含む場合があるため、先にdry-runでChecker起動有無を確認し、重複実行しない)
2 Checker DEV run(単独実行する場合、各条件の固定txtで):
`.venv/Scripts/python.exe er052_output/open233_ledger_clarity_p_trial_01/tools/run_checker_after_p01.py --out-dir er052_output/open233_polysemy_trial_04/runs/<slug>/<control|nb>/checker --ledger-path <各条件の固定ledger.txt> --article-path er052_output/open233_polysemy_trial_04/runs/<slug>/<control|nb>/rep1/b1b/article.md --source-path er052_output/open233_polysemy_trial_04/runs/<slug>/<control|nb>/rep1/ja_writer/revision2.md --budget-jpy 10 --yes-run-paid`
(--article-pathのb1b/article.md位置はrunner出力で要確認。--ledger-pathはcontrol用とnb用で別txt)
費用見込み(1 run): EN約JPY3.1 + Checker約JPY2.5 = 約JPY5.6。10 run約JPY56。pairwise(5記事x2 call)約JPY10は別枠(eval_plan.md)。
注意: Checker結果は承認根拠にしない(副作用・最終状態の比較のみ)。pairwise_p01.pyはBEFORE/AFTER/OUTがハードコードのため、記事別に引数化(別名コピー)が必要=P4a/Fable判断。
