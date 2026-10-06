## 管理ID

OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01(委任_06-W1: 新仕様E2E 9 runの事後評価ラベル付け、担当run=neg1/meta_std/hormuz_std[51 claim]。¥0)。並行タスク: 委任_06-W2(neg7/meta_adv/hormuz_adv)、委任_06-W3(bgroup_B3/neg3/neg2)が同時にラベル付け中。**互いの出力を読まない。git操作・SSOT編集・コード変更をしない。** 書き込み先: `er052_output/open233_prod_e2e_02/labels/labels_w1.json`(新規)、同`labels_w1_notes.md`(新規)、`docs/pm/RESULT_PACKET_LABEL_W1.md`(新規)、`docs/pm/delegation_log/`。

**作業方式**: `Write`/`Edit`で小分け(1回40行以内)、Bash heredoc不使用。T-0の委任文保存はWriteを2分割して逐語保存。説明は最小限。

## 性質/到達上限Status/禁止事項

- 性質: 事後評価(Sonnet推測ラベル、Fable/ユーザー確認前提)。到達上限: 担当claim全件にラベル+1行理由。
- 判定基準: `er052_output/open233_prod_e2e_01/labeling_guide_01.md`(§1用語/§2手順/§3禁止/§4シート)と`labeling_examples_old9.md`(見本)を**そのまま**使う。新しい基準・原則を作らない。gold定義を広げない。
- **判定前にfloor/AI判定列(floor_reason・llm_materiality・s1等)を見ない**: label_sheet.csvから担当run行を抜き出す際、claim_text/fact_id/run/cycle/claim_keyのみを作業用シートに写し、判定列は写さない(§3)。
- 禁止: 有料API/Ledger原文の推測補完/記事全体の印象での判定/他workerの出力参照/run jsonの判定部分の参照(Ledger原文とclaim_textの照合のみ)。
- 費用: ¥0。Opus Gate: 非該当。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read。G-1: git出力不使用。F-1: transcript退避不要。T-1: 事前指定Read/Grep一覧に従う(一覧外は理由を記録)。T-0(2026-09-13、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。T-2(2026-09-25): TTSなし。T-2追記(7-5): TTSなし。T-3(2026-09-26): ¥0のため適用対象外。

## ユーザー指示(原文、要点)

> 事後評価として、真に問題があった件数/不要に候補化した件数(Checker)、真に重大だった件数/不要に重大判定した件数/真に重大だったのに軽微・問題なしとした件数(後段AI)、必要だったRewrite件数/不要だったRewrite件数(Rewrite)、真の重大Fact見逃し件数/重大Fact検出件数(Safety)を出す。

## KPI provenance欄

ラベル=事後評価(label_source=`sonnet_w1_2026-10-06`、confirmed_by=空欄[Fable/ユーザー確認前])。対象=fresh E2E(`er052_output/open233_prod_e2e_02/runs/`)。

## Opus台帳更新

該当なし。

