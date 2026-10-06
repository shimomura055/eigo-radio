# 委任_03b 逐語保存(OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01)

## 管理ID

OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01(委任_03b: 設計結果・Opus条件Aレビュー・Fable判定=USER_DECISION_REQUIREDのSSOT反映)。並列委任_03aが設計docとopus_l2_reviewを編集中のため、この2ファイルは読まない・触れない。git操作なし(commitはFableが別委任で実施)。

作業方式(必須): Editは1回30行以内、Bash heredoc不使用、説明最小。T-0はWrite新規+Edit追記で逐語保存。時間目安20分。

## 性質/到達上限Status/禁止事項

- 性質: SSOT記録(¥0)。Status: DIRECTIONAL-MISREAD-SAFETY-DESIGN-01=USER_DECISION_REQUIRED(設計docはDESIGN_READY_FOR_REVIEW相当、Opus条件A済み)。VALIDATED/APPROVED/PRODUCTION_WIRED不可。
- 禁止: 残11 run/Production変更/gold・KPI変更/有料API/コード変更/Fableやユーザーが決めていないことを「決定」と書くこと。
- Opus Gate: 条件A必須レビュー実施済み(Part 1事前スキャン+Part 2設計評価、計2回、read-only ¥0)。

## 固定ブロック

E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(T-0: 委任文を本ファイルへ逐語保存しcheck_delegation_prompt.py実行、結果1行をRESULT_PACKETへ)。

## ユーザー指示(要点)

E2E残11 runはユーザーが再開を明示するまで待機。系統的な読み違い専用Safety設計(決定論検査=センサー→専用独立確認、一律floorでない)。¥0反実仮想。Opusレビュー必須。禁止: 残11 run/Production変更/全機械floor復活/一律Checker厳格化/gold変更/KPI変更/Human Reviewへの安易な振替/有料E2E。到達Status上限 DESIGN_READY_FOR_REVIEW / USER_DECISION_REQUIRED。

## 記録すべき事実(A〜H)

A. 原因: HC-012見逃しはAI3段階の同一誤読(「ロールバック」多義語)。決定論negation_polarity_mismatchは「適切な開示なしに」の「なし」への偶発反応で方向は見ていない。新9 runのnegation反応39件=問題なし38/重大1。比較・方向専用センサーはchecker不在。number/causal反応は新9 runで0。
B. 系統的読み癖。T1状態変化の向き反転/T2推移・比較反転/T3当事者取り違え/T4未指定役割充填/T5因果捏造/T6可能性の既成事実化。
C. 反実仮想: 新9 run 123件中T-A/T-B 43件(重大1/問題なし42)、T-C 55件(重大1/軽微3/問題なし51)。旧floor誤爆24件: T-A/T-B 0、T-C 8。
D. 案A〜F。Sonnet推奨=案E、Opus修正版=案E'。起動=T-D'。
E. Opus Part 2: 条件付きで進める(必須修正3点)。ユーザー判断事項7点。
F. Fable照合: 方向性一致(案E)。STOP条件該当→USER_DECISION_REQUIRED。残11 run待機。
G. 費用: 全体¥0。H. 追加費用見込み【推測】T-E約¥0.27〜0.81/run、限定Trial約¥15以内。

(詳細数値・出典は原委任文のとおり。本ファイルは要点保存。)

## 作業内容

1. OPEN_ITEMS.md進捗追記(3行以内)。2. DECISION_LOG.md同日エントリへ(h)設計結果追記。3. REPORT §82新設。4. OPUS_FINDINGS_LEDGER.md Part1/Part2追加。5. ACTIVE_TASK.md全面更新。6. RESULT_PACKET.md(変更ファイル・T-0結果・Dangling Reference・commit対象案)。

## 実行コマンド

1. T-0: .venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_03b.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_03b.md_check.json
2. OPEN_ITEMS本体行文字数確認。

## Git / 報告

git操作なし。報告はdocs/pm/RESULT_PACKET.md、最終報告8行以内。
