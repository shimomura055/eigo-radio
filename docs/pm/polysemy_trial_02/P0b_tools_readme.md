# P0b tools readme (OPEN-233-LEDGER-POLYSEMY-NOTE-TRIAL-02 委任_P0b)
DEV/Trial専用。Production非接続。入力はBaseline固定のdraft+verification(B_design §12)。

## コマンド(テーマごと、slug=meta/hormuz等、run_03前提)
1. dry-run(API無し): `.venv/Scripts/python.exe er052_output/open233_polysemy_trial_02/tools/gen_notes_p02.py --draft er019_output/<slug>/run_03/research_ledger/fact_ledger_draft.json --verif er019_output/<slug>/run_03/research_ledger/fact_ledger_verification.json --out-dir er052_output/open233_polysemy_trial_02/ledgers/<slug> --dry-run`
2. 本実行(有料1 call、上限5円): 同コマンドから `--dry-run` を外す(`--budget-jpy 5`)。
3. 検査: `.venv/Scripts/python.exe er052_output/open233_polysemy_trial_02/tools/check_notes_only_diff_p02.py --control er052_output/open233_polysemy_trial_02/ledgers/<slug>/verified_fact_ledger_control.txt --nb er052_output/open233_polysemy_trial_02/ledgers/<slug>/verified_fact_ledger_nb.txt --out er052_output/open233_polysemy_trial_02/ledgers/<slug>/diff_report` (PASS=exit0)
4. test: `.venv/Scripts/python.exe -m pytest er052_output/open233_polysemy_trial_02/tests/test_gen_notes_p02.py -q`

## 出力(--out-dir)
verified_fact_ledger_control.txt / verified_fact_ledger_nb.txt / draft_nb.json / rejected.json / notes_raw_response.json / notes_prompt.txt / notes_provenance.json(dry-runはnotes_provenance_dryrun.json)

## 配置規約(er019 runnerの既存Ledger再利用 L92-97)
runnerは `<ledger_dir>/verified_fact_ledger.txt` が存在すれば再利用する。条件別に次へコピー:
`er052_output/open233_polysemy_trial_02/ledgers/<slug>/control/research_ledger/verified_fact_ledger.txt` <- verified_fact_ledger_control.txt
`er052_output/open233_polysemy_trial_02/ledgers/<slug>/nb/research_ledger/verified_fact_ledger.txt` <- verified_fact_ledger_nb.txt
(コピーは本ツールでは行わない。runner起動側で実施)。Controlは再構築版(metaで元txtとsha256一致を確認済み)。

## 費用見込み
1テーマ1 call。入力は台帳15fact程度のJSON+規則で数千トークン、検索はURL限定。見込み約1〜3円、上限5円(`--budget-jpy`は超過フラグ記録のみで、事前停止はしない)。
