# BUDGET_LOG_01 (委任_28: 再配達 構成・原稿改善Trial の費用台帳。実費はraw usage logで確定)

作成: 2026-10-25。為替USD/JPY=160(pricing_snapshot.json)。モデル: gpt-6.1-sol(生成・書き換え)、gpt-6-luna(Leakage判定。既存M7校正済み判定器)=いずれも既存正式構成・最新世代。日本語原稿生成のみ(英訳・音声化なし)。

## 1. 有料launch
| # | 内容 | 結果 |
|---|---|---|
| 1 | `gen --paid`(lead,intro,leadintro_gate,closing_A,B,C) | rc=0、全stage完了。累計22.711円 |
| 2 | `gen --paid --stages intro,leadintro_gate,closing_A`(人物紹介v2・案A v2。v1は検査語不足/Gate衝突の改善反復) | rc=1(`LEADINTRO_LEAKAGE_FLAGGED`=補助判定のTension専用項目が適用外なのに停止する私のコードの不具合。API応答は保存済み) |
| 3 | 同上(適用外2項目を除外する関数へ修正後に再実行) | rc=0。累計31.65円 |
- launch 3回(1回目は正常完了、2回目は自作コードの停止条件の不具合による停止、3回目は修正後の続行。同一処理の暴走再起動ではない。STOP通知0、外部停止0、原因不明のrc≠0 0回)。**既存の生成物は再利用(resume)で、生成済みstageを再課金していない**。

## 2. stage別実費(円)
| stage | 実費 |
|---|---|
| yrv_lead(1 call) | 2.140 |
| yrv_intro(2 call: v1+v2) | 5.431 |
| yrv_leadintro_leak(luna 2 call) | 0.211 |
| yrv_closing_A(sol: v1+v2) / gate leak(v1 2判定+v2 1判定)/ rewrite(v1 1回) | 10.939 / 0.542+0.096 / 2.422 |
| yrv_closing_B(sol 1) / gate leak1 | 4.212 / 0.047 |
| yrv_closing_C(sol 1) / gate leak1 | 5.413 / 0.197 |
| **合計** | **31.650** |

見積(DESIGN_01 §4)=期待22〜30円・最大38円に対し、31.65円(最大見積内、上限40円の79%)。見積超過の原因: Closingの生成がsol high effortで1 call 4〜11円(出力2〜3k token)、案Aの反復(v1の生成+Gate書き換え+v2の生成)で約+10円。

## 3. 日次(2026-10-25 JST)
| 時点 | 日次累計(`docs/pm/tools/daily_dev_cost_01.py`、adopted_jpy) |
|---|---|
| 着手時(有料前) | 862.38 |
| 完了後(全有料run終了後) | **894.03**(本Trial 31.65円+並行agent分を含む。残105.97円) |
- 有料前の判定: 862.38+上限40=902.38円<1,000円。超過なし。
