# BUDGET_PLAN_01 (委任_29 Phase 0: 残枠確認と費用見積。API 0)

## 1. 現在有効な承認枠と残額(確認結果)
- **Y固有の累計上限は2026-10-24に撤廃済み**(`BUDGET_POLICY_CHANGE_01.md`、ユーザー決定)。以後は日次1,000円(JST、全体)。
- 委任_28の個別Cap 40円(`er110_output/family_y_redelivery_audio_01/revision_01/BUDGET_APPROVED.json`)は実費31.65円(`REDELIVERY_REVISION_01/BUDGET_LOG_01.md`)。**残約8.35円**は委任_28のCapの残りで、委任_29のCapではない。委任_29にはFableから個別Cap額の付与がない(Fable指示=残額内のみ有料可、収まらなければSTOP)。
- 日次(2026-10-25 JST): `docs/pm/tools/daily_dev_cost_01.py` adopted_jpy = **894.03円**(残105.97円)。
- 案件見積は全案とも300円未満(PM_GOVERNANCE 7-7の都度承認閾値内)だが、**8.35円残額の指示と日次残105.97円に収まる範囲**を超える案はFableの個別Cap付与が必要。

## 2. 単価の根拠(委任_28実績、`raw_usage_log.jsonl`)
| call | input tok | output tok(うち reasoning) | 実費円 |
|---|---|---|---|
| yrv_closing_B (sol, high) | 1,961 | 2,240 (2,070) | 4.212 |
| yrv_closing_C (sol, high) | 1,991 | 2,985 (2,821) | 5.413 |
| Leakage判定 (luna, high) | 約940 | 395〜3,435 | 0.047〜0.542 |
- 回帰: 約0.32円/千input tok、約1.6円/千output tok。
- 本方式の1生成: input約3.5〜4k tok(Prompt約6千字は日本語約3k tok+入力データ)、output = reasoning + 分析JSON(観察・候補3〜5・選定理由)+Closing ≒ **4.5〜7k tok**。→ **1生成 ≈ 8.5〜12.5円**(中央10.5円)。Fable想定の3〜6円は、分析を出力する構造化方式では過小(Closingのみ生成の実績が4.2〜5.4円であり、分析出力を加えるため)。
- Leakage判定(luna) 0.05〜0.6円/回。再生成(契約違反時のみ最大1回)は+1生成分。

## 3. 見積(2案+代替)
| 案 | 内容 | 期待 | 最悪(再生成が各生成に1回ずつ入った場合) |
|---|---|---|---|
| **S(最小)** | 2テーマ×1生成 +判定2回 | 約17〜26円(中央約22円) | 約45円 |
| **F(安定性込み)** | 2テーマ×2生成 +判定4回 | 約34〜52円(中央約43円) | 約90円 |
| L(代替・未検証) | F案を effort=medium で(reasoning減) | 約22〜36円(推定。**未検証**。委任_28のhighとの比較条件が変わるため非推奨) | — |
- いずれも**残8.35円(=1生成も賄えない)を超える**。→ **Phase 0完了後に有料実行前でSTOP**(Fable指示どおり)。
- 日次残105.97円に対しては S/F とも収まる。F最悪90円でも収まるが、並行agentの消費で変動。実行時は予約方式guard(各call前に実費累計+見積>テーマCapなら停止)が働く。
- 推奨: **S案を先に実行し(約22円)、Voiceから自然に魅力的な切り口を発見できているかを見て、安定性確認(2回目の生成)を追加するか判断**(Sで品質が成立しなければFを無駄に実行しない。成立していれば追加1生成×2テーマ約22円)。ただし「同じPromptからの結果の安定性」は委任の要望のため、最初からF(約43円)としてもよい。この選択と個別Cap額(S: 30円、F: 60円を提案)をFableが決める。
- 実行時間: 1生成あたり約1〜3分(sol high)。2テーマは別processで並列、wall time約3〜8分。

## 4. 有料run手順(承認後)
1. `er110_output/family_y_closing_general_01/BUDGET_APPROVED.json` に `{"cap_jpy": <総Cap>, ...}` を作成(Fableの承認額。テーマ別にCap/2)。
2. `stop_scope_check_01.py` rc=0確認後、テーマごとに別process: `.venv\Scripts\python.exe er110_family_y_closing_general_trial_01.py gen --theme redelivery_fee --gens N --paid` と `... --theme sns_age_limit ...`(各1起動。再起動は明示許可のみ)。
