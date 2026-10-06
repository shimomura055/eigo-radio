## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03(委任_02: held-out検証セットの固定、testset_03、正解データ(phase付き)、実行前凍結)。並列委任_01(script)、_03(集計)、_04(SSOT)が同時進行。**書込先: `er052_output/open233_directional_misread_trial_03/{testset_03.json,testset_03.md,ledger_truth_03.json,ledger_truth_03.md,FREEZE_03.json}`、`docs/pm/RESULT_PACKET_T03_02.md`、`docs/pm/delegation_log/`。他ファイル・gold定義・SSOT・git操作なし。LLM呼出なし。**
作業方式: Write/Edit 1回40行以内、Bash heredoc不使用、説明最小。T-0はWrite+Edit追記で逐語保存(必須見出し3つを含む)。時間目安25分。

## 性質/到達上限Status/禁止事項
性質: ¥0データ準備・事前登録。禁止: 有料API/gold定義変更/KPI変更/新しい重大カテゴリの定義(D61は既存の重大Fact誤り基準のまま。内部ラベル「D61型」は分析用のみ)/実行後の変更(凍結)。Opus Gate: 非該当。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_02.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ。T-2/T-2追記(7-5): TTSなし。T-3: 対象外。

## ユーザー指示(原文、要点)
> D61だけへの過学習を避けるため、実行前にheld-out検証セットを固定する。最低限: HC-012/A5-0/D61・HF-009/正常文43件/前回誤爆3件/held-out重大例/held-out正常例。実行後に都合よくtestsetや正解を変更しないこと。
> 合格基準(事前固定): HC-012 3/3、A5-0 3/3、D61 2/3以上、held-out重大例 平均2/3以上かつ全例1/3以上、正常43件+held-out正常例の不要重大判定0、不要Rewrite見込み0、新たな重大見逃し0、前回解消誤爆3件の再発なし。
> D61型を新しい重大カテゴリにしない。既存の重大Fact誤り基準のまま評価する。

## 作業内容
A. `testset_03.json`: `../open233_directional_misread_trial_02/testset_02.json`(63項目)をコピー(内容・expected・repeat設定は変更しない。G-01/G-02/G-03/F-09/F-10/F-19/G-04〜06はrepeat 3)。各項目に`heldout: false`を付与。
B. held-out追加(Opus提案を基に、**D61を見ずに作る**、各`heldout: true`、`repeat: 3`、`origin: "heldout_trial03"`):
 - 重大例4件(既存重大Fact誤り基準で重大=Ledgerの結末と逆): H-G1 "Oil prices dropped after the withdrawal."(HF-009、水準↑に対しFINAL↓) / H-G2 "Brent fell after the plan was dropped."(同) / H-G3 "Prices ended lower."(同) / H-G4 HC-012系の結末反転1件(例: "Meta kept the human concierge feature running."=機能PAUSEDに対しAVAILABLE)。
 - 正常例6件: H-F1 "Prices initially fell but recovered."(HF-009、INTERIM↓+FINAL↑=SAME) / H-F2 "Oil prices briefly dipped."(INTERIM、上げ幅と整合=SAME) / H-F3 "Oil prices stayed near earlier highs."(FINAL=SAME) / H-F4 主語省略のfaithful(例: "The drop was short-lived."、INTERIM) / H-F5・H-F6 比較・否定のfaithful 2件(例: "Prices did not fall across the board." "Brent did not end lower than before.")。
 - 各項目に fact_id/ledger_fact_text(Ledger本文逐語)/expected_event_subject/expected_phase(INTERIM|FINAL|UNSPECIFIED)/expected_compare/acceptable_compare を事前登録。文はLLMを使わず手書き(上記例文をそのまま使ってよい)。
C. `ledger_truth_03.json`: `ledger_truth_02.json`をコピーし、各eventに`phase`(INTERIM/FINAL/SINGLE)を追加。HF-009=上げ幅DECREASED(INTERIM)+水準INCREASED(FINAL)。HC-012=電話テストSTARTED(SINGLE or INTERIM、Ledger本文に即して)+機能PAUSED(FINAL)。他factはSINGLE。根拠quoteはLedger本文に部分一致することをassert。採点規則(phase一致率を追加)をmdに。
D. `FREEZE_03.json`: testset_03.json/ledger_truth_03.jsonのsha256・作成時刻・項目数(63+10)・repeat合計・凍結宣言「実行後の変更禁止」。
E. `testset_03.md`: 内訳表(既存63+held-out 10、repeat、call見込み=Σrepeat)、合格基準8項目(逐語)と各基準の母数(どのidが対象か)。
F. `docs/pm/RESULT_PACKET_T03_02.md`: 要約8行+sha256+T-0結果。

## 事前指定Read一覧
1. `er052_output/open233_directional_misread_trial_02/testset_02.json`: 先頭30行(構造)、以降はPythonでコピー。
2. `er052_output/open233_directional_misread_trial_02/ledger_truth_02.json`: 全文(短い)。
3. Ledger本文: `er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/verified_fact_ledger.txt` Grep `HF-009` →block範囲、`er019_output/meta/run_03/ledger/verified_fact_ledger.txt` Grep `HC-012` →block範囲。

## 事前指定Grep一覧+追記位置・更新位置の手順
上記3のGrep。新規ファイルのため追記位置なし。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_02.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-03_02.md_check.json`
2. json妥当性+sha256: `.venv\Scripts\python.exe -c "import json,hashlib;[print(p,hashlib.sha256(open(p,'rb').read()).hexdigest()) for p in ['er052_output/open233_directional_misread_trial_03/testset_03.json','er052_output/open233_directional_misread_trial_03/ledger_truth_03.json']]"`

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_T03_02.md`。最終報告6行以内(内訳、call見込み、sha256)。
