# COST_PLAN_02 (委任_02、実行前見積、2026-10-13)

管理ID: FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_02。上限JPY35(ハードストップ38)、run dir累計上限80(現在26.77、`--budget-jpy 61`=26.77+35の切上げ基準)。

| step | 内容 | 見積(期待) | 最悪 | 出典 |
|---|---|---|---|---|
| 1 | Std KP選定+canonicalization(LLM gpt-6-luna、1回) | JPY1.1 | JPY3 | 前回実績JPY1.07(`completion_01`/委任_01報告)、`COST_ESTIMATE_01.md` §2-1 |
| 2a | Std Full Story part2 N01再生成(Gemini+ASR、6%減速、標準2+fallback1) | JPY1.5 | JPY12 | `cost_03.json`: Gemini 19呼出JPY11.5(約0.6/呼出)、ASR 23呼出JPY3.3(約0.14/呼出)、Azure(fallback)4呼出JPY8.84(約2.2/呼出)。fallbackに落ちた場合は止めて報告(STOP) |
| 2b | Std KP音声 英語5+日本語意味5 clip | JPY3 | JPY8 | `COST_ESTIMATE_01.md` §2-2(期待約4/最悪約8は20clip想定、Std10clipに半減) |
| 2c | Std japanese_title(J3再生成、1clip) | JPY0.5 | JPY2 | 同上clip単価 |
| 3 | Adv comment_1〜4 正式経路再生成(calm, conversational、Charon+ASR) | JPY3.2 | JPY6 | 約0.8/clip(Gemini 0.6+ASR 0.14) x4 |
| 合計 | | **約JPY9〜10** | **約JPY31** | 上限35以内 |

- Adv Preview(E1)は承認Style未配線のためSTOP(`ADV_STYLE_FACTCHECK_02.md`)。費用なし。
- 再生成を上限回数を超えて繰り返さない(標準2+fallback1、既存retry機構のまま)。
- 為替・単価の変動はcost_log(`compute_cost_jpy_so_far`)の実測で置換し、報告に実績を載せる。
