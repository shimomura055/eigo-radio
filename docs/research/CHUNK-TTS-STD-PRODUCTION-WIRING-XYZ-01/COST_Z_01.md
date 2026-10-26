# COST_Z_01 — 委任_03 費用(JPY)

| 項目 | 実費 | 根拠 |
|---|---|---|
|offline test・回帰・golden・事前確認|0円|API 0(mock generator、偽generator)|
|Z Std evidence 起動1(16:36:58)|1.6653円|runnerの`spent_jpy`(cost_log: TTS 2・ASR 4・NER hook 1)|
|Z Std evidence 起動2(16:39:38)|0円|新規API 0(cost_log 7件のまま、chunk再利用)|
|合計|約1.67円(Cap 60円に対し約2.8%)|`measure_z/run_artifacts/cost_log.jsonl`|

課金前に落ちた起動=0回。429/5xx=0件。Cap接近なし。見積(数円〜約17円)内。当日JST累計(本委任分)=約1.67円。
