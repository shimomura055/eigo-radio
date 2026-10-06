# P0c 手順書(DEV、Production非変更)
前提: 固定台帳txt(P0b生成のcontrol用/nb用)。out_dir規約 er052_output/open233_polysemy_trial_02/runs/<slug>/<control|nb>/rep<k>、既存ならSTOP。env OPEN233_B3_VARIANT=control|nb。
Phase 1(B3+JA R0/R1/R2、--stop-after writer、既定budget JPY12):
`OPEN233_B3_VARIANT=nb .venv/Scripts/python.exe er052_open233_polysemy_nb_dev_01.py --theme "<topic>" --slug meta --ledger-txt <ledger.txt> --out-dir er052_output/open233_polysemy_trial_02/runs/meta/nb/rep1 --phase phase1 --yes-run-paid`
Phase 2(同out_dir、brief/R2再利用でENのみ→Checker、--stop-after advanced、既定JPY10+Checker JPY10):
`OPEN233_B3_VARIANT=nb .venv/Scripts/python.exe er052_open233_polysemy_nb_dev_01.py --theme "<topic>" --slug meta --ledger-txt <ledger.txt> --out-dir <同上> --phase phase2 --yes-run-paid`
dry-run(JPY0): `--yes-run-paid` を `--dry-run` に替える。
並列バッチ(既定3並列、結果 runs/batch_log.jsonl):
`.venv/Scripts/python.exe er052_output/open233_polysemy_trial_02/tools/launch_batch_p02.py --phase phase1 --jobs "meta=<topic>|<ledger.txt>" --jobs "hormuz=<topic>|<ledger.txt>" --variants nb --repeats 3 --parallel 3 --yes-run-paid`
注意: control/nbで台帳txtが異なる場合は--variantsを分けて別バッチで実行する。
Researcher不実行の保証: 台帳txtをコピーしrunnerの既存txt再利用(L92-97)に依存、実行後raw_usage_logのresearch/ledger段call=0をassert(provenance research_calls)。
費用見込み(1 run): Phase 1 約JPY8(B3 1.5+JA 6.7)、Phase 2 約JPY15(EN 3.1+Checker 2.5+deviation等)。12 run約JPY95。上限案: 2条件JPY130、3条件JPY200。
provenance: out_dir/nb_provenance_phase{1,2}.json(variant、転記ブロックsha、送信B3 prompt sha、台帳sha、FREEZE sha、model、research_calls、費用)。
