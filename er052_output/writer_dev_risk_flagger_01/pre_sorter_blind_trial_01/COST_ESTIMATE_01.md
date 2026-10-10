# COST_ESTIMATE_01: POST-EN-HUMAN-PRE-SORTER-BLIND-TRIAL-01 費用見積(すべて「見積」。API実測は RESULT_01.md。USD/JPY=160、pricing_snapshot.json登録値のみ)

根拠データ: `cost_estimate_01.json`(estimate_cost.py)。入力トークンは flagger_lib.estimate_tokens(ASCII/4+非ASCII*1.3)による**概算**で実測tokenizerではない。
バッチ構成: 3バッチ(10/10/9件)、各バッチにrubric全文を含む。入力概算 バッチ1=8,445 / バッチ2=13,382 / バッチ3=13,196、合計 **約35,023 tokens/モデル**(見積)。
出力概算(見積): 可視出力 29件x約130=約3,770 tokens + reasoning(推論)トークン。reasoningはバッチ当たり 中央5,000 / 高位12,000 と仮定(推測。Flagger過去実測は1件判定で約100〜200tokenと小さいが、10件判定でどれだけ増えるか不明のため上振れ側に置く)。出力合計: 中央 18,770 / 高位 39,770 tokens。

## モデル別(1回のTrial総額=29件全体=3バッチ合計)
| モデル | 状態 | 単価 $/1M (in / out) | 登録 | 入力 tok(見積) | 出力 tok(見積 中央/高位) | 費用 中央 | 費用 高位 |
|---|---|---|---|---|---|---|---|
| gpt-6-luna | 実行対象 | 0.10 / 0.50 | 登録(PROJECT_INTERNAL_RECORD) | 35,023 | 18,770 / 39,770 | JPY 2.06 | JPY 3.74 |
| gpt-6.1-sol | 実行対象 | 2.00 / 10.00 | 登録(OFFICIAL_PRICING_PAGE_FETCHED) | 35,023 | 同 | JPY 41.24 | JPY 74.84 |
| gpt-6-astra | 実行対象 | 10.00 / 50.00 | 登録(OFFICIAL_PRICING_PAGE_FETCHED) | 35,023 | 同 | JPY 206.20 | JPY 374.20 |
| claude-fable-5-1 | **UNAVAILABLE** | 未確認(参考: docs/pm/dev_eval_model_inventory_01.md記載 $10/$50、pricing_snapshot未登録) | 未登録 | - | - | (参考)JPY 206 | (参考)JPY 374 |
| claude-opus-5-5 | **UNAVAILABLE** | 未確認 | 未登録 | - | - | 未確認 | 未確認 |
| claude-sonnet-5-5 | **UNAVAILABLE** | 未確認(参考: 同inventory $2/$10、未登録) | 未登録 | - | - | (参考)JPY 41 | (参考)JPY 75 |

- **実行対象3モデル合計(見積)**: 中央 約JPY 249.5 / 高位 約JPY 452.8。
- **費用ガード(Fable指示: 実行対象モデル合計の見積が JPY300 を超える場合は STOP)**: 中央JPY249.5は300以内。高位(推論トークン上振れ想定)は300超だが、高位は意図的に悲観側に置いた仮定であり、中央値で判定する(POST-EN-TRIAL-01と同じ判定方式)。ただし上振れに備え、実行時に**累計実費JPY300以上で以後のcallを拒否するランタイムガード**をdriver(run_presorter.py)に実装済み(Astraが支配的なため)。1callのmax_output_tokens=16,000。
- Anthropic 3モデル(Fable/Opus/Sonnet)はAPI経由で呼べない(鍵・SDKなし、PREREGISTRATION_01.md参照)ため費用は発生しない(参考値のみ)。置換はしない。

## 量産想定(参考値。仮定を明示)
仮定: (1) 10記事/日。(2) A3+A4後のUnion Flag件数 = POST-EN-TRIAL-01実測の1記事平均 2.6件(29件/11本=2.64)→ 約26件/日。(3) 1件当たりの入力・出力量は本Trial平均(=Trial費用/29件)。今回packetには台帳全体を渡した4件(Fact未指定)が含まれ平均を押し上げるため、量産時の実単価と同一とは限らない(保守側)。(4) 1件ずつ/バッチ呼びの差・rubric反復コストは考慮せず比例計算。(5) 30日/月。(6) Trial見積の中央/高位をそのまま比例。
| モデル | 1日 中央 | 1日 高位 | 1か月(30日) 中央 | 1か月 高位 |
|---|---|---|---|---|
| gpt-6-luna | JPY 1.85 | JPY 3.35 | JPY 55 | JPY 101 |
| gpt-6.1-sol | JPY 36.97 | JPY 67.10 | JPY 1,109 | JPY 2,013 |
| gpt-6-astra | JPY 184.87 | JPY 335.49 | JPY 5,546 | JPY 10,065 |
| claude-fable-5-1(参考、単価未登録) | JPY 185 | JPY 336 | JPY 5,546 | JPY 10,065 |
| claude-sonnet-5-5(参考、単価未登録) | JPY 37 | JPY 67 | JPY 1,109 | JPY 2,013 |
| claude-opus-5-5 | 未確認 | 未確認 | 未確認 | 未確認 |
注: 量産コストの採否判断材料ではない(Production採用は人間ユーザーのみ承認)。Trial後に実測トークンで再計算可能。
