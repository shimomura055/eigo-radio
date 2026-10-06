## 管理ID

OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01(委任_06-W3: 新仕様E2E 9 runの事後評価ラベル付け、担当run=bgroup_B3/neg3/neg2[48 claim]。¥0)。並行タスク: 委任_06-W1(neg1/meta_std/hormuz_std)、委任_06-W2(neg7/meta_adv/hormuz_adv)が同時にラベル付け中。**互いの出力を読まない。git操作・SSOT編集・コード変更をしない。** 書き込み先: `er052_output/open233_prod_e2e_02/labels/labels_w3.json`(新規)、同`labels_w3_notes.md`(新規)、`docs/pm/RESULT_PACKET_LABEL_W3.md`(新規)、`docs/pm/delegation_log/`。

**作業方式**: `Write`/`Edit`で小分け(1回40行以内)、Bash heredoc不使用。T-0の委任文保存はWriteを2分割して逐語保存。説明は最小限。

## 性質/到達上限Status/禁止事項

- 性質: 事後評価(Sonnet推測ラベル、Fable/ユーザー確認前提)。到達上限: 担当claim全件にラベル+1行理由。
- 判定基準: `er052_output/open233_prod_e2e_01/labeling_guide_01.md`(§1用語/§2手順/§3禁止/§4シート)と`labeling_examples_old9.md`(見本)を**そのまま**使う。新しい基準・原則を作らない。gold定義を広げない。**担当にSafety-critical instance(bgroup_B3: gold B3「因果接続語+flashy 20% plan」)と時期gold(neg3: HF-009「一時的な上げ幅縮小」をprices began to fall等に変えるもの)が含まれる。gold定義は`er052_open233_self_recovery_flow_runner_01.py` L9655-L9680の`SAFETY_CRITICAL_CLAIM_DEFS`を正とし、該当文のtrue_criticalを判定する。**
- **判定前にfloor/AI判定列(floor_reason・llm_materiality・s1等)を見ない**: label_sheet.csvから担当run行を抜き出す際、claim_text/fact_id/run/cycle/claim_keyのみを作業用シートに写し、判定列は写さない(§3)。
- 禁止: 有料API/Ledger原文の推測補完/記事全体の印象での判定/他workerの出力参照/run jsonの判定部分の参照(Ledger原文とclaim_textの照合のみ)。
- 費用: ¥0。Opus Gate: 非該当。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read。G-1: git出力不使用。F-1: transcript退避不要。T-1: 事前指定Read/Grep一覧に従う(一覧外は理由を記録)。T-0(2026-09-13、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。T-2(2026-09-25): TTSなし。T-2追記(7-5): TTSなし。T-3(2026-09-26): ¥0のため適用対象外。

## ユーザー指示(原文、要点)

> 事後評価として、真に問題があった件数/不要に候補化した件数(Checker)、真に重大だった件数/不要に重大判定した件数/真に重大だったのに軽微・問題なしとした件数(後段AI)、必要だったRewrite件数/不要だったRewrite件数(Rewrite)、真の重大Fact見逃し件数/重大Fact検出件数(Safety)を出す。

## KPI provenance欄

ラベル=事後評価(label_source=`sonnet_w3_2026-10-06`、confirmed_by=空欄[Fable/ユーザー確認前])。対象=fresh E2E(`er052_output/open233_prod_e2e_02/runs/`)。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

1. `er052_output/open233_prod_e2e_01/labeling_guide_01.md`: 全文。
2. `er052_output/open233_prod_e2e_01/labeling_examples_old9.md`: 全文。
3. `er052_output/open233_prod_e2e_02/report/label_sheet.csv`: Grep `^bgroup_B3|^neg3|^neg2|,bgroup_B3,|,neg3,|,neg2,` →担当run行のみ(列構成は先頭行で確認)。判定列は写さない。
4. 各instanceのLedger(fact list+notes_for_writer)と記事本文: run json `er052_output/open233_prod_e2e_02/runs/<instance>.json`をGrep `"ledger"|"facts"|"fact_id"|"notes_for_writer"|"article"|"body"` →Ledger部分と最終本文のみRead(判定部分`stage2_results`/`floor`/`materiality`は読まない)。Ledgerが別ファイル参照の場合はそのファイル(Globで特定)をRead。
5. `er052_open233_self_recovery_flow_runner_01.py`: L9655-L9680(gold定義)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 手順(§2): 1 claimごとに claim_text→fact_id(複数可)→Ledger原文+notes_for_writerを逐語照合→4観点(主体/相手先・対象/範囲/限定条件)+数値・日付・因果・否定・比較→`severity_eval`(重大/軽微/問題なし)→`true_problem`(Y/N)→`true_critical`(Y/N、gold定義+線引き例に照らす)→`rewrite_needed`(Y/N/N_A: そのclaimがRewrite対象だった場合のみ。対象かどうかはlabel_sheetの該当列があれば用い、無ければN_A)→`reason`1行→UNDECIDABLEは理由必須。
- 出力`labels_w3.json`: 集計script互換(`docs/pm/RESULT_PACKET_AGG.md` Grep `--labels|json形式` で形式確認。キー=claim_key[run/cycle込み]、値={true_problem, true_critical, severity_eval, rewrite_needed, reason, label_source, confirmed_by})。
- `labels_w3_notes.md`: run別の集計(件数: severity_eval別/true_problem Y・N/true_critical Y/UNDECIDABLE)、重大Y・UNDECIDABLEの全件逐語(claim_text・fact_id・Ledger抜粋・理由)、gold該当文(B3・neg3 HF-009型)の判定と根拠、境界例の所感(【推測】)。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_06-W3.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_06-W3.md_check.json`
2. 作業用シート作成→ラベル付け→`labels_w3.json`・`labels_w3_notes.md`出力。
3. 自己検算: 担当48件すべてにラベルがあること(件数一致)、jsonがparse可能なこと(`.venv\Scripts\python.exe -c "import json;d=json.load(open(r'er052_output/open233_prod_e2e_02/labels/labels_w3.json',encoding='utf-8'));print(len(d))"`)。
4. git操作なし。

## SSOT追記文

なし。

## Git

git操作なし。SSOT編集権なし。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_LABEL_W3.md`へ: 1. T-0結果。2. 担当件数と完了件数。3. run別集計(severity/true_problem/true_critical/UNDECIDABLE)。4. 重大Y・UNDECIDABLEの一覧(逐語)+gold該当文の判定。5. 一覧外Read理由。6. 成果物パス。最終報告は8行以内。
