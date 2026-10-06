## 管理ID
OPEN-233-LEDGER-CLARITY-DESIGN-01(委任_01b: 事例収集—HC-012/HF-009の原資料・現行台帳・Writer誤読実例、全fixture台帳の曖昧Fact候補棚卸し、held-out候補。read-only、¥0)。並列委任_01a(仕様調査)、_01c(Trial評価設計)、_01d(SSOT)が同時進行。**書込先: `docs/pm/ledger_clarity/02_cases.md`(新規、150行以内)、`docs/pm/delegation_log/`のみ。コード・SSOT・git変更なし。API呼出なし。**
作業方式: 説明最小、Bash heredoc不使用、Write/Edit 1回40行以内。T-0はWrite+Edit追記で逐語保存(必須見出し3つを含む)。時間目安25分。

## 性質/到達上限Status/禁止事項
性質: ¥0事例収集(設計・Trialの入力)。禁止: 有料API/台帳ファイルの変更/gold変更/「明確化後の文」の確定(案として【案】を付し、原資料との意味一致は未確認と明記)。Opus Gate: 非該当(入力)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う(一覧外は理由記録)。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_01b.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行を最終報告へ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
> A. Factは明確に記述する(何が起きたか/誰が何をしたか/何がどう変化したか/どの時点か/因果が確認されているか)。複数の意味に解釈できる表現を避ける。B. 複雑なFactは適切に分割する。例① HC-012「機能を当面ロールバックした」→「人間コンシェルジュ機能を当面取り下げた」のように。ただし原資料との意味の一致は必ず確認。例② ホルムズ原油価格: 途中で上昇幅が縮小したことと最終的に高水準だったことをWriterが取り違えないよう、必要なら2文に分割し時系列・対象・関係を明示。①事実を追加・改変しない。②Fact同士の関係を維持する。
> Trial: Meta HC-012、ホルムズHF-009を含む複数の事例で従来台帳と明確化台帳を比較。過学習を防ぐため未使用の検証例も含める。

## 調査内容
A. **HC-012**: 現行台帳block全文(`er019_output/meta/run_03/ledger/verified_fact_ledger.txt` Grep `HC-012`→block範囲、`storyline_b3/full_ledger.json` L3付近)、原資料(台帳の出典フィールド/quote/`er019_output/meta/run_03/`配下のsource・input・storylineファイルをGlobで特定し、該当原文を逐語)、Writer誤読の実例(`er052_output/open233_prod_e2e_02/runs/meta_run03_advanced.json` L331-400のclaim text「restored…」、他runの"put back"/"changed back"等、`er052_output/open233_directional_misread_trial_01/testset_01.json`のHC-012紐付き文一覧)。「ロールバック」の多義性(機能撤回/状態復元)と、原資料ではどちらの意味かを事実で示す。
B. **HF-009**: 同様に現行台帳block(`er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/`)、原資料、Writer側の文(F-09/F-10/G-03/K16/K19/S-06等、testset_01/02から)。「上げ幅縮小(途中)」と「水準は高い(最終)」の2要素が1 factに同居していることを逐語で示す。
C. **曖昧Fact候補の棚卸し**: 9 fixture(実体2 Ledger: meta 15 fact、hormuz 12 fact)の全27 factを、次の観点で機械的+目視チェックし表に: (i)多義語・抽象動詞(ロールバック/見直し/対応/調整等) (ii)1 factに複数事象(時系列・途中/最終) (iii)主体・相手先の省略 (iv)因果の強さの不明確さ(causal_strength欄の有無・値) (v)時点の不明確さ (vi)否定・限定条件。各factに「曖昧度(高/中/低)」と根拠語。過去の重大検出・見逃し・誤爆(HC-012/HF-009/HF-007 B3/HF-002/HF-011/HC-006 A4-0/HF-003 A2A3-0/B4-a)との対応を付ける。
D. **held-out候補**: Cのうち、これまでTrialのgold/testsetに使われていないfactで曖昧度中以上のものを5〜8件、「未使用の検証例」として列挙(理由付き)。他fixture(er019_output配下の別run/別テーマ)に台帳があればGlobで存在だけ確認し件数を記す(深掘り不要)。
E. **Before/After案(【案】、意味一致は未確認)**: HC-012とHF-009について、ユーザー方針A/Bに沿った明確化案を各2案(IDを維持し本文明確化/子事象へ分割)で示し、「追加した情報がないか」「失われた関係がないか」を自己チェック欄に。
出力: `docs/pm/ledger_clarity/02_cases.md`(A〜E、逐語引用+出典)。

## 事前指定Read一覧
台帳block・原資料はGrep→範囲Read(各40行以内)。testset/run jsonはPythonで該当recordのみ抽出。

## 事前指定Grep一覧+追記位置・更新位置の手順
上記A〜DのGrep/Glob。新規ファイルのため追記位置なし。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_01b.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-LEDGER-CLARITY-DESIGN-01_01b.md_check.json`

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目)
最終報告8行以内(原資料の所在と「ロールバック」の原義、HF-009の2要素、曖昧度高/中の件数、held-out候補数、T-0)。
