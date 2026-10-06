## 管理ID

OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01(委任_02d: 決定論センサーの「当たりの質」¥0検証。Opus前段スキャンの指摘「HC-012の`negation_polarity_mismatch`はLedger事実行の『開示なし』に偶然反応しただけ」の真偽を確認し、fact_id別のセンサー反応分布を集計する)。**git操作・SSOT編集・コード変更(runner/checker)・設計doc(`docs/pm/design_open233_directional_misread_safety_01.md`)への書込をしない**(別委任が同時編集中)。書込先は`er052_output/open233_directional_misread_offline_01/sensor_quality_01.{py,json,md}`と`docs/pm/RESULT_PACKET_SENSOR.md`、`docs/pm/delegation_log/`のみ。

**作業方式**: 出力は小分けWrite(1回40行以内)、Bash heredoc不使用、説明は最小限。T-0の委任文保存はWrite 2分割で逐語。時間目安25分。

## 性質/到達上限Status/禁止事項

- 性質: ¥0 read-only分析(既存artifact+既存checker関数のローカル再実行のみ、LLM呼出なし)。到達上限: 分析完了(設計入力)。
- 禁止: 有料API/残11 run/Production変更/gold・KPI変更/checkerコード変更(importして呼ぶのは可)。
- Opus独立技術レビューGate該当判定: 本委任は分析のみで非該当(設計全体は条件A該当、別途Part 2)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う(一覧外は理由記録)。T-0(2026-09-13常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_02d.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKETへ(FAILでも継続)。T-2/T-2追記(7-5): TTSなし。T-3: ¥0のため対象外。

## ユーザー指示(原文、要点)

> ¥0で先に検証すること: 今回HC-012を捕捉できるか/既知goldを維持できるか/正常文を再び大量に重大化しないか/追加確認へ送る件数がどの程度になるか。
> 決定論検査は「センサー」として扱い、専用の独立確認を起動する(ユーザー仮説)。

Opus前段スキャンの指摘(検証対象): 「是正案a(`STAGE1_NEGATION_MODE="a"`)では『なし』を否定の印として数えるため、HC-012を根拠とする肯定文はすべて極性食い違いと判定される。本当の誤り(ロールバック→restoredの向き反転)を見つけたのではない【推測】」「T1(状態変化の向き反転)専用のセンサーは現在存在しない」「`number_not_in_fact`が`changed_number`へ変換されず、承認構成の数字floor(`FLOOR_MODE=number_only`)も発火しない」。

## KPI provenance欄

すべて決定論的集計・ローカル関数再実行【確認】。LLM未実行。「拾えるか」の判断は関数出力の事実のみ(推測を書く場合【推測】を付す)。

## Opus台帳更新

該当なし。

## 事前指定Read/Grep一覧

1. `er052_open233_stage1_coverage_checker_01.py`: Grep `negation_polarity_mismatch|STAGE1_NEGATION_MODE|NEG_MARKERS|def .*negation|def .*polarity|number_not_in_fact|changed_number` → 該当関数の範囲Read(否定語リスト・判定ロジック・fact側/記事側の極性算出方法・「なし」の扱いを逐語で確認)。
2. `er052_open233_self_recovery_flow_runner_01.py`: Grep `FLOOR_MODE|MECHANICAL_FLOOR_FLAGS|def apply_floor|def precheck_floor|PRECHECK_MODE|number_not_in_fact` → 範囲Read(数字floorがどのフラグ/sub_reasonを見ているか)。
3. `er019_output/meta/run_03/ledger/verified_fact_ledger.txt`: Grep `HC-012` → 該当ブロック全文(否定語の有無を逐語確認)。
4. `er052_output/open233_prod_e2e_02/runs/meta_run03_advanced.json`: L325–410(HC-012 claim recordの`stage1_coverage`、`sub_reasons`、`dev`)。
5. `er052_output/open233_directional_misread_offline_01/trigger_replay_01.py`: 全文(run json走査・T-A抽出ロジックを流用)。
6. gold定義: `er052_open233_self_recovery_flow_runner_01.py` Grep `SAFETY_CRITICAL_CLAIM_DEFS` → 範囲Read(A5-0・B3・HF-009等のfixture/fact_id/記事文の特定)。A5-0の記事文とLedger事実行の所在(fixture path)を確認。
7. 委任_61の方向反転ケース: `docs/pm/delegation_log/` Grep `委任_61|方向反転|comparison.*反転` → 該当ファイルの範囲Read(記事文・Ledger行が特定できる範囲)。

## 手順

A. **HC-012反応機構の特定**: checkerの否定判定関数をimportまたは同等ロジックで再実行し、HC-012のLedger行と記事文「...restored the human concierge feature...」に対し、fact側/記事側のどの語が否定マーカーとして数えられたかを出力。さらに同fact_idを根拠とする**他の肯定文**(meta advanced内のHC-012 4文、および他runのHC-012根拠文)でも同じ理由が出るかを確認(=「fact行の否定語だけで反応している」かの判定)。
B. **fact_id別センサー反応分布**: 新9 run+旧9 runの全claim recordで`sub_reasons`に決定論理由を含むものをfact_id×理由名で集計。各fact_idのLedger行に否定語があるか(手順Aのマーカーで判定)を列に付け、「fact行否定語あり」に反応が集中しているかを示す。上位fact_idと反応数、ラベル(重大/問題なし)を表に。
C. **gold T1/T2への感度**: A5-0(状態変化反転)、HF-009(推移反転、K16/K19)、委任_61比較反転ケース、HC-012について、記事文(誤文)とLedger行を決定論検査(否定・比較・数値)に直接かけ、発火するか(理由名)を表に。「モデルが見逃した場合にセンサーが拾えるか」の事実確認。
D. **数字floor穴の事実確認**: `number_not_in_fact`がどこで生成され、`changed_number`/floorへどう接続しているか(または接続していないか)を行番号付きで記録。新9 runで`number_not_in_fact`がsub_reasonsに出た件数とそのfloor発火有無。**修正はしない。**
E. 出力: `sensor_quality_01.json`(集計)、`sensor_quality_01.md`(A〜Dの表+所見、60行以内)、`docs/pm/RESULT_PACKET_SENSOR.md`(要約10行+T-0結果+一覧外Read理由+Dangling Reference確認)。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_02d.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_02d.md_check.json`
2. `.venv\Scripts\python.exe er052_output\open233_directional_misread_offline_01\sensor_quality_01.py`(標準出力は`sensor_quality_01.log`へ)。

## SSOT追記文

なし。

## Git

git操作なし。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_SENSOR.md`。最終報告は10行以内(Opus指摘の真偽判定を1行目に)。
