# FAMILY-X-JA-MODEL-ALLOCATION-SOL61-PRODUCTION-WIRING-01 委任_02 (2026-10-11)
範囲: E案(B3/R0/R1/R2=gpt-6.1-sol、APPROVED_FOR_PRODUCTION)の実装・test(課金0)。runtime実行なし。Branch `feature/sol61-ja-allocation-01`(main未merge)。

## 変更
- routing: FAMILY_X_FACTLOCK_R0/REVISE=gpt-6.1-sol、FAMILY_X_STORYLINE_B3新設(gpt-6.1-sol)。
- runner run_storyline_b3: 従来のvfl01.MODEL(Luna暗黙)をrouting+require_model+返却model不一致STOPへ。
- W-1: R0_MODEL/ASTRA_MODELをroutingから取得(直書き廃止)、CHAIN_METHOD_DETAIL文字列更新(U-1はchain_method=="W-1"のみ参照で影響なし)。Prompt sha不変(pinned test通過)。
- pricing_snapshot gpt-6.1-sol note更新(値不変)、er009 PRICING_USD_PER_Mへ(2.00,0.10,10.00)転記。
- test更新/新規: routing allowlist 3キー、pricing coverage、W-1(Sol/mismatch STOP R0・R1/全段Sol/actual記録)、B3(Sol/mismatch STOP/prompt sha固定/routing違反API前STOP)、er009 Sol単価、cost_aggregate/risk_flagger routing pin。
- CURRENT_SPEC: Family X節にE案追記(実装済み・runtime evidence待ち)。DECISION_LOGは未編集。

## 検証
- 関連171 passed。全suite(er*test*.py、--continue-on-collection-errors): 修正前41 failed(=baseline 37 + 4新規=routing/pricing pin test)→4件更新後、baseline 37集合と同一・新規0。収集error1件(er015_standard_a2_6000...)は既存(委任_06/_07記録済み、配線非起因)。
- Dangling check: 既存baselineと同一(Production scope内の新規参照0、旧model id直書き残存0: Production JA経路にgpt-6-luna/astra/gpt-5.x literal無し。RFのLunaは対象外で不変)。
- retry/fallback/regeneration: R0記号QA再生成=call_luna_r0(同routing)、R2再実行=call_astra(同)、--regenerate-stage storyline_b3/resume=run_storyline_b3(同)、再利用B3は未呼出、U-1はmodel非参照(旧Luna/Astra生成済みJAも再利用可=既存仕様、判断はFable)。
## runtime見積(未実行)
最終報告参照(1記事 ¥19〜27(writerまで)、+EN/RF ≈¥3)。
