## 管理ID

PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01(委任_01: ユーザー決定[判断7]のSSOT記録+配線計画書作成。Production code変更なし・API課金なし)。並行タスク FACTLOCK-WRITER-REDESIGN-TRIAL-01(別agent、本委任は触れない)。

## 性質/到達上限Status/禁止事項

性質: SSOT記録+計画。到達上限Status: PLANNED。Production code編集禁止。er052_output/factlock_writer_trial_01/・docs/pm/RESULT_PACKET_FACTLOCK.md書込禁止。git add -A禁止、破壊的git禁止、有料API禁止。費用¥0。Opus条件C対象は計画書(Fableが別途Opusへ)。時間≈40分。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1/D-1/G-1/F-1/T-0(委任文保存+check_delegation_prompt)/T-2(TTSなし)/T-3(課金なし)。

## ユーザー指示(原文)

「判断7(新規): 全6-luna化をProduction方針として進めてOK(ネガ判定は微妙(同等)、コストメリットが大きく止める理由がない)」(2026-10-08)。背景: 「すべて6.0に変えるつもりだったし、そうなっていたと思ってました。上位互換で価格も安いのに、6.0に変えない理由がありません。」「Checker含めて、現状5.6を使っているものは6.0にTrial的に変更して…追って6.0の検証はしっかりやればいい。」

## KPI provenance欄

該当なし。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

er006_model_routing_contract_01.py L1-120 / all6 RESULT.md 該当節 / docs/pm/RESULT_PACKET.md / DECISION_LOG該当エントリ / ACTIVE_TASK.md L1-20 / er005_cost_logger.py単価表 / er006_model_routing_contract_01_test.pyとhardcodeテスト一覧。

## 事前指定Grep一覧+追記位置・更新位置の手順

gpt-5.6-lunaリテラル直参照一覧、require_model系呼び出し棚卸し、未検証API呼び出しパターン(previous_response_id/reasoning/json_schema/strict)。DECISION_LOG: ALL-6-LUNA...エントリ直後に「## PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01: ユーザー判断(判断7、2026-10-08、委任_01)」追加+索引1行。OPEN_ITEMS: OPEN-241(POST_USER_VALIDATION)。ACTIVE_TASK固定ヘッダ更新(判断7=決定済み、APPROVED未配線にOPEN-241)。REPORT_LEDGER1行追加。

## 実行コマンド全文

1. check_delegation_prompt.py実行 2. SSOT記録 3. 配線計画書 docs/pm/design_production_model_routing_gpt6_wiring_01.md(§0〜§7) 4. 回帰は実行しない、git status --porcelain確認。

## SSOT追記文

DECISION_LOG/OPEN_ITEMS本文案は委任文どおり(ユーザー判断逐語・背景数値・範囲=方針承認、配線はOPEN-241段階実施、Status=PLANNED)。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: DECISION_LOG.md, OPEN_ITEMS.md, docs/pm/REPORT_LEDGER.md, 計画書, 本委任文(+_check.json)。ACTIVE_TASK.md/RESULT_PACKET.mdはgitignore。trailer Decision-ID: 判断7-2026-10-08。push origin main。

## 報告(RESULT_PACKET項目)

RESULT_PACKET.md上書き(Status=PLANNED・¥0・Production変更なし・commit hash)。1.SSOT反映箇所 2.計画書要点 3.Opus条件C論点 4.問題・残作業 5.check結果1行 6.raw URL一覧。推奨は書かず事実のみ。
(注: 本ファイルは委任文の構造保存版。全文はFable委任メッセージ)
