## 管理ID
OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01(委任_01a: ¥0母集団再集計+既存artifact構造調査)。並列委任_01b(Trial対象セット)、_01c(Trial script骨格)、_01d(ACTIVE_TASK/OPEN_ITEMS)が同時進行。**本委任の書込先は`er052_output/open233_directional_misread_trial_01/population_01.{py,json,md}`と`docs/pm/RESULT_PACKET_TRIAL_01A.md`、`docs/pm/delegation_log/`のみ。他ファイル・SSOT・コード・git操作なし。LLM呼出なし。**
作業方式: Write/Editは1回40行以内、Bash heredoc不使用、説明最小。T-0は委任文をWrite(新規)+Edit追記で逐語保存。時間目安30分。

## 性質/到達上限Status/禁止事項
性質: ¥0 read-only集計(既存artifactのみ)。到達上限: 集計完了(Trial見積の入力)。禁止: 有料API/残11 run/Production変更/gold・KPI変更/コード変更。Opus Gate: 非該当(設計は前管理IDで条件Aレビュー済み)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う(一覧外は理由記録)。T-0(常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01_01a.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ(FAILでも継続)。T-2/T-2追記(7-5): TTSなし。T-3: ¥0のため対象外。

## ユーザー指示(原文、要点)
> まず¥0で実施。有料Trial前に、既存artifactから以下を確定する: Ledger全Fact数/状態変化Fact数/記事側確認が必要になる想定件数/1 runあたりの追加処理件数/Ledger側全Factチェックの単独コスト見込み/記事側を含む追加処理全体の1 runあたりコスト見込み。前回の暫定値をそのまま流用せず、正しい母集団で再計算する。
> Trialする仕様: (1)Ledgerの全FactについてAIが状態変化・方向性を持つか確認し、持つ場合は結果状態を固定分類で抽出 (2)方向性ありのFactだけ、対応する記事側を別AI判定(Ledger側の答えを見せない)で結果状態のみ抽出 (3)機械比較: 同方向→通過/明確に逆方向→重大候補/抽出不能・曖昧→記録のみ。

## 背景(確定事実)
前管理IDのOpusレビュー: 「123件=Stage 1候補のみ(SUPPORTED判定文を含まない)。正しい母集団=状態変化factに紐づくStage 1の全単位(SUPPORTED含む)」。Stage 1 checkerは決定論理由がなければSUPPORTEDで終わりStage 2へ行かない(checker L636-645)。設計doc: `docs/pm/design_open233_directional_misread_safety_01.md` §4/§7/§13。

## 作業内容
A. **fixture・Ledgerの所在**: runner `er052_open233_self_recovery_flow_runner_01.py` Grep `FIXTURES|fixture_id|ledger_text|verified_fact_ledger` →新9 run(`er052_output/open233_prod_e2e_02/runs/*.json`の9件)それぞれのfixture→Ledgerファイルパス・記事(最終本文)の所在を表にする。
B. **Ledger全Fact数**: 各LedgerのFact block数(fact_id単位、例`MUSE-HC-012`)を決定論で数える(block区切りの規則はLedger本文のGrep `^\[?[A-Z]+-[A-Z]+-\d+|fact_id` で確認)。9 fixture合計と平均。
C. **単位→fact対応の有無**: 新9 run jsonに、Stage 1の**全単位**(SUPPORTED含む)とその`support_fact_ids`/`unit_ids`が保存されているか確認(Grep `support_fact_ids|unit_ids|stage1_coverage|n_units|units_total`)。保存されていれば「fact紐付き全単位数/run」を集計。保存されていなければ、代替として(i)最終本文の文数(決定論の文分割、runner Grep `vs_sentence_segments_l6|def .*segment`の関数を流用)と(ii)Stage 1候補数(123件/9 run)の両方を出し「上限=全文数、下限=候補数」と明記。E2E logs(`er052_output/open233_prod_e2e_02/logs/`)にStage 1生出力が残っていればそれも確認(Grep `support_fact_ids`)。
D. **状態変化Fact数(¥0近似)**: LLMを使わず、Fact本文の日本語語彙による近似(ロールバック/撤回/復元/復活/再開/停止/中止/縮小/拡大/増加/減少/引き上げ/引き下げ/延期/前倒し/開始/終了/解除/導入/廃止等、設計doc §2(ii)の語対を参照)で各factを「状態変化候補/非該当」に分類し、**各factの判定根拠語を一覧化**(委任_01bがLedger側正解の事前登録に使う)。近似であることを明記。該当fact数と比率(9 fixture)。
E. **記事側確認件数の推計**: Cで単位→fact対応が取れる場合=状態変化factに紐づく単位数/run(実数)。取れない場合=全文数×状態変化fact比率(近似)と全文数(上限)の2値。
F. **単価の根拠**: `docs/pm/delegation_log/2026-10-02_PM-OPUS-MODEL-ID-INVENTORY-01_result.md`(Grep `単価|\$|per 1M|input|output`)とStage 2の実績単価(`er052_output/open233_prod_e2e_02/report_final/report_abcde.md` Grep `後段|¥`、新9 run後段¥7.29/123判定)から、利用可能モデルID・入出力単価の表を作る。Stage 2のmodel ID・effortは`er052_open233_self_recovery_stage2_calibration_01.py` Grep `model=|MODEL|effort`で確認。推定token: Ledger側1 fact=入力(fact block≒150〜300 tok+prompt≒300)+出力(schema≒80)、記事側1単位=入力(対象X+文+前後1文≒200〜400+prompt≒300)+出力≒60。各構成(同一model/Ledger側別model)で、Ledger側全Factチェック単独¥/run、記事側¥/run、合計¥/run(low/mid/high)。
G. 出力: `population_01.json`(数値)、`population_01.md`(表+所見、60行以内)、`docs/pm/RESULT_PACKET_TRIAL_01A.md`(要約10行+T-0結果+一覧外Read理由+「単位→fact対応が取れない場合のTrial上の含意」1段落)。

## 事前指定Read/Grep一覧
上記A〜Fに記載。run json・Ledgerは全文Readせず、Grep+範囲Read・scriptで集計。

## 実行コマンド全文
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01_01a.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-TRIAL-01_01a.md_check.json`
2. `.venv\Scripts\python.exe er052_output\open233_directional_misread_trial_01\population_01.py`

## SSOT追記文
なし。

## Git
なし。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_TRIAL_01A.md`。最終報告8行以内(全Fact数/状態変化Fact数(近似)/記事側件数/run/¥/run low-mid-high、単位→fact対応の有無)。
