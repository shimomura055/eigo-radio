# 委任文(Fable→sonnet-worker) ※session JSONLに未記録のため委任文本文から手動転記(要旨を保つ短縮なし主要節)

## 管理ID
FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_03(方式Bの検索込み追加検証[Production同一経路、mey、2 sample]+CTRL低下・Fact増の原因分析+Closeout v02更新+SSOT更新)。2026-10-20。
並行タスク衝突確認: 並行委任なし(委任_02完了 9c22750b3)。SSOT編集権: あり(OPEN_ITEMS.md OPEN-427行、DECISION_LOG.md末尾、docs/pm/USER_DECISION_REGISTER_01.md #127行、docs/pm/REPORT_LEDGER.md)。

## Fableの照合結果と決定(前提)
- 委任_02結果: 検索なし36 cellでBのみmey背景12/12保持(E0 0.75)だが、mey CTRL 0.5(E0 1.0)・muse Δfacts +2.5・coffee +0.083で基準未達=NOT_VALIDATED_CRITERIA_UNMET。A/C/D/E=REJECTED。検索込み(E0/A/D)は主体6/6保持、背景はE0 0/10・A 2/10・D 2/7で脱落。検索回数はA/Dで増えず。創作UNSUPPORTED 1件(地理付加「ダンマーム近郊」、A/D mey s2)。
- Fable決定: (1)Bの検索込み追加検証を実施(約JPY35〜55、案件合算≈205〜225≤300、承認区分C)。(2)Bの CTRL低下(mey 0.5)とFact増(muse +2.5)の原因を検索なし出力から分析。(3)地理付加1件は軽微としREJECTED根拠にしないが、全方式で同種付加が検索込みで再発するか計数し検証観点として記録。(4)判定基準は不変(v02)。
- 禁止: Production変更。追加Web検索はProduction経路内のみ。git add -A/-u/-f・amend・rebase・force push・stash。有料run再起動は費用重複なしを確認できる場合1回まで。

## 性質/到達上限Status
- Trial追加検証+Closeout更新。到達上限Status: XRFR_TRIAL_CLOSEOUT_V02_PENDING_FABLE。方式Bの最終ラベルはFable。Production採用はユーザーのみ。
- 費用: 当日実費累計JPY480.41/本委任見積JPY35〜55/承認区分C。T-3上限¥60(Guardrail、暴走疑い時のみSTOP、1 runの検索回数がProduction実績20の2倍超でSTOP)。

## 作業
W1. B検索込み: er085_research_fact_retention_trial_01_search_arm.py --variants B --topic mey --samples 2 --budget-jpy 55 (委任_02と同一採点規則・出典取得規則)。検索回数・token・費用・時間、主体・背景保持、CTRL、Fact数、創作フラグ→逐語照合(地理付加再発計数含む)。
W2. 原因分析(API 0): 検索なしBのmey CTRL 0.5・muse Δfacts +2.5について、CTRL項目の消失先、増えたFactの分類(同一事実分割/新規必要/不要)。採点規則の限界は区別して記す(規則は変えない)。
W3. Closeout v02: TRIAL_CLOSEOUT_01.mdへ「§v02追記」節。
W4. SSOT: OPEN-427行末・DECISION_LOG末尾・REGISTER #127行末・REPORT_LEDGER更新。ACTIVE_TASK先頭ヘッダ。

## Git/報告
commit1: 結果+eval+原因分析+Closeout v02+委任文 / commit2: SSOT。trailer: Delegation: FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01/委任_03。報告: docs/pm/RESULT_PACKET_XRFR3.md (1)〜(11)+判定整合行。
