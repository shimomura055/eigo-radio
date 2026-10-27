## 管理ID

GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05

(抽出不可・要約再構成: jsonl抽出で現セッションに該当ブロックが見つからないため、受領した委任文の要点を再構成)

## 性質/禁止

- 性質: 全6経路(X/Y/Z x Std/Adv)の実run evidence(DEV run dir、公開なし)。到達上限=EVIDENCE取得(PRODUCTION_WIRED判定はFable)。有料・上限JPY150。
- 禁止: TTS/音声再生成、STOP/HR Lock/Gate迂回、HRなし宣言、Production既定動作変更、データ手直し、禁止Git操作、Productionコード編集。

## 事前指定Read一覧

EVIDENCE_PLAN_02.md、IMPLEMENTATION_05B.md、SCHEMA_CONTRACT_01.md、KCP EVIDENCE_RESULT_03.md、er120_part2_wiring_01.py(pregen_stage/finalize_stage/require_final)、er119_kp_human_review_cli_01.py。

## 事前指定Grep一覧+追記位置・更新位置の手順

各Family runnerの --regenerate-stage / --resume / study_text / part2 引数をGrep。追記位置=docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{EVIDENCE_RESULT_05,COST_05,ROUTE_STATUS_05}.md。更新位置=docs/pm/RESULT_PACKET_GPG5.md。

## 実行コマンド全文

py tools/stop_scope_check_01.py --managed-id GRAMMAR-PREGEN-ALL-LEVELS-01 --run-dir <run> --out <json>
.venv\Scripts\python.exe <family runner> (TTS_EXECUTION_MODE=STANDARD)

## 実施事項

経路別に(i)Top1/Top2 (ii)1件採用 (iii)0件omit (iv)2件拒否 (v)finalize LLM 0 (vi)ページ (vii)KCP G0-G4 (viii)凍結後model変更耐性 (ix)費用 (x)HR actor=evidence。

## SSOT追記文

OPEN-559/556/545 6経路Status文案をRESULT_PACKETに記載(SSOT編集権なし)。

## Git

pathspec付きcommit。メッセージ「GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05: ...」、trailer Delegation: GRAMMAR-PREGEN-ALL-LEVELS-01/05。

## 報告

RESULT_PACKET_GPG5.md (0)-(7)。

## 固定ブロック
E-1 D-1 G-1 F-1 従来どおり。
