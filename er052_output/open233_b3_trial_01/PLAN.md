# OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 実行計画(未実行、Opus条件A・ユーザー承認・予算確定後)
環境: すべて `.venv\Scripts\python.exe`、cwd=repo root。DEV runnerは無変更。
## 手順
1. B3 36本(6条件V0/V1/V2/V3/V5/V6 × slug meta/hormuz/space_weapons × i=1,2。独立なので並列可、APIレート注意で3並列程度):
   `python er052_output/open233_b3_trial_01/tools/run_b3_variant.py --variant <V> --slug <slug> --out-dir er052_output/open233_b3_trial_01/runs/<slug>/nb/<V>/b<i> --budget-jpy 5 --yes-run-paid`
   完了後 `.../b<i>/storyline_b3/selected_brief.md` を固定。目視で「## Storyline」「## Selected Facts」形式・fact数・書式を確認(parse不能=停止)。
2. Writer phase1(各brief×j=1,2、72本、並列可):
   `$env:OPEN233_RUNS_ROOT="er052_output/open233_b3_trial_01/runs"; $env:OPEN233_B3_VARIANT="nb"; python er052_open233_polysemy_nb_dev_01.py --theme "<topic.txt>" --slug <slug> --ledger-txt <ledgers/<slug>/control/research_ledger/verified_fact_ledger.txt> --out-dir er052_output/open233_b3_trial_01/runs/<slug>/nb/<V>/b<i>/w<j> --phase phase1 --budget-jpy 12 --brief-md <.../b<i>/storyline_b3/selected_brief.md> --yes-run-paid`
3. EN phase2: 同out-dir・`--phase phase2 --no-checker --budget-jpy <phase1実績込み累積上限。例25>`(--budget-jpyはphase1込み累積。前回driver不具合の再発防止として、phase2はphase1のcost.jsonを確認してから起動し、driverは各枠のcost.json totalを超過判定に使う)。
## out-dir規約
`er052_output/open233_b3_trial_01/runs/<slug>/nb/<V>/b<i>/{storyline_b3,...}` と `.../b<i>/w<j>/`(Writer。DEV runnerの`/nb/`規約を満たす)。B3 out-dirはB3のみ(JA/EN無し)。
## manifest(`er052_output/open233_b3_trial_01/MANIFEST.json`)項目
variant・slug・b_i・w_j・instruction_sha256・full_prompt_sha256・brief_md_sha256・fact数・brief文字数・B3 model_id_actual・run別cost・phase1/phase2 exit_reason・再実行回数。
## 予算guard
各runはout-dir別`--budget-jpy`。全体累計はdriverが各枠後に集計し、**累計≥¥500見込みでSTOP**。見積≈¥544(再実行込み≈¥600)は既に超過 → 本計画は**Fable判断前に起動しない**(縮小案: Writer1本/brief=36記事≈¥305)。
## 停止時規則
各枠(variant×slug×b×w)は停止時1回だけ再実行、全体で合計8回まで。9回目到達でSTOP。再実行前の成果物は`_failed_a1`へ退避(MX方式)。内容の善し悪しで再実行しない。B3がJSON/ID不整合でRuntimeErrorの場合のみ上記再実行枠を消費。
## 禁止
Production変更・`er052_output/open238_precheck_fix_trial_01/`への書込・Checker実行・`git add -A`。
