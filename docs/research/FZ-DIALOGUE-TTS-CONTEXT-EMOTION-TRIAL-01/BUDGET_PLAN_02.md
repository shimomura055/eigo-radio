# BUDGET_PLAN_02 — 追加2作品の費用計画(FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_04、2026-10-26、Phase 0はAPI 0)

- 上限: **追加Trial予算 30円 = 追加2作品の合計**(ユーザー指示2026-10-26 §6。Round 1の30円とは別枠・分離。他案件の予算の流用なし)。案件見積は300円以下・承認済みScope・個別Cap内(PM_GOVERNANCE 7-7)。予算分割・日付分割による回避なし。
- 単価の根拠: Round 1実測(`BUDGET_LOG_01.md`)= TTS 26 call 9.46円(retry 2含む、平均0.364円/call)、ASR 26 call 0.38円(0.0146円/call)、Azure secondary 1 call 0.12円、感情LLM(gpt-6-luna)1 call 0.0975円。
- 見積式: `est_tts_jpy(prompt字数, 音声秒)`(`er118_..._01.py`、為替160円/$、gemini-2.5-pro-preview-tts Standard 入力$1/M・出力$20/M・音声25 token/秒=`er005_output/cost_baseline_01/pricing_snapshot.json`)。ctx arm = 決定論CONTEXT + LLM由来350字を加算したprompt・音声長×1.05、base arm = 既存styleのみ。Round 1で同式を適用すると「2ctx+1base(retry無し24 call)=9.35円」、実測は retry 2 call を除くと約8.7円 → **見積は実測より約7%保守的**(較正の記録、見積を割り引かず保守値を採用)。

## 1. セリフ数の確定: 各作品8件、計16件(30円内)

セリフ数を減らす案(各7件など)も検討したが、Round 1と同じ構造(方向あり5・過剰演技の監視2・安定監視1)を保つために各8件とし、費用の大きいセリフを選定段階で置き換えた(`SELECTION_02.md` §3)。**予算を超えない範囲で最大限の比較(16件×3 take)を維持**する。

### 1-1. 作品別・arm別のTTS見積(円/take)

| 作品 | clip | ①音声長(秒) | ctx(1 take) | base(1 take) |
|---|---|---|---|---|
| 開いた窓 | part1_c7 | 4.24 | 0.512 | 0.421 |
| | part1_c10 | 1.84 | 0.307 | 0.228 |
| | part1_c12 | 6.17 | 0.676 | 0.577 |
| | part2_c4 | 12.09 | 1.171 | 1.054 |
| | part2_c6 | 2.53 | 0.352 | 0.283 |
| | part3_c8 | 4.69 | 0.536 | 0.457 |
| | part3_c9 | 2.17 | 0.329 | 0.255 |
| | part3_c11 | 11.76 | 1.135 | 1.026 |
| | **小計** | 45.5 | **5.02** | **4.30** |
| 猿の手 | part1_c4 | 4.33 | 0.503 | 0.429 |
| | part1_c13 | 4.65 | 0.540 | 0.454 |
| | part1_c15 | 3.53 | 0.443 | 0.364 |
| | part2_c2 | 2.41 | 0.341 | 0.274 |
| | part2_c6 | 6.22 | 0.673 | 0.581 |
| | part2_c8 | 5.32 | 0.599 | 0.508 |
| | part2_c10 | 3.93 | 0.477 | 0.397 |
| | part3_c1 | 2.89 | 0.389 | 0.312 |
| | **小計** | 33.3 | **3.97** | **3.32** |

### 1-2. 合計(call数と円)

| 項目 | call数 | 円 | 根拠 |
|---|---|---|---|
| 感情LLM(gpt-6-luna、1作品1 call) | 2 | **0.194(実測・確定)** | Phase 1a実行済み(`BUDGET_LOG_02.md`) |
| 開いた窓 TTS: ctx_t1 + base_t1 + ctx_t2 | 24 | 14.34 | 5.02×2 + 4.30 |
| 猿の手 TTS: ctx_t1 + base_t1 + ctx_t2 | 24 | 11.26 | 3.97×2 + 3.32 |
| **TTS小計(retry無し、保守見積)** | **48** | **25.60** | |
| 生成時ASR(Production生成関数内) + Azure secondary予備 | 48 | 1.2 | Round 1実測 0.0146円/call×48=0.70 + secondary予備0.5 |
| retry予備(TTS見積の10%) | 約4〜5 call | 2.56 | Round 1実績のretry率 2/24=8.3% |
| **保守上限(見積を割り引かない)** | | **約29.6** | 25.60+1.2+0.19+2.56 |
| **期待値(Round 1較正 ×0.93、retry 8.3%)** | | **約26.8** | 23.8 + 0.7 + 0.12 + 0.19 + 2.0 |

**30円内に収まる根拠**: 保守上限29.6円 < 30円、期待値26.8円(余裕約3円)。**①(Production既存clip)の再利用でA条件の1 takeはAPI 0**: A条件2 take = {①既存音声(API 0), base_t1(新規)}、B条件2 take = {ctx_t1, ctx_t2}(新規)。追加TTSを減らせる再利用はこれ以上ない(base_t2を作らない設計は事前登録02の `①側n=2={既存take, base_t1}` と同一)。Round 1のctx/base生成物は別作品のため再利用不可。

### 1-3. 超過防止(Cap guard、PHASE1_GO.json方式を踏襲)

- `er118_output/fz_dialogue_context_tts_trial_02/PHASE1_GO.json`(cap_jpy=30、2作品の `raw_usage_log.jsonl` を共有=合算でCap判定)。Round 1の出力dir・GO・cost logとは分離。
- **Phase 1a時点のGOは `arms: []`(TTS arm無し)**でTTS生成は起動不可(test `test_round2_go_cap_over_30_rejected_and_tts_arms_blocked_without_go_scope`)。Phase 1bの前にFableが `arms=["ctx","base"]` へ更新する。
- 各clip開始前に実績をcost logから再計算し、**`実績 ≥ Cap` に加え、`実績 + 次clipの1 call見積 > Cap` でも開始しない**(Round 2で追加した先読み。test `test_round2_cap_lookahead_stops_before_exceeding_without_api`)。ctx_t2が最後に走るため、万一超過見込みになった場合に切られるのはctx_t2末尾で、その場合は2 take完結不能として報告(自動で続行・予算分割はしない)。
- 実行順(Opus R1)は作品ごとに `ctx_t1 → base_t1 → ctx_t2` を同一process連続。2作品は**直列**(並列にするとcost logの競合でCap判定が遅れ、保守上限が30円に近いため直列を選ぶ。所要は約5分/作品)。
- 日次(JST)累計は本委任の開始前0.17円→Phase 1a後0.37円(`daily_dev_cost_01.py`)。Phase 1b(約27円)を足しても日次1,000円に対し十分小さい。

## 2. 費用が増えるシナリオと対処

- retryが想定(8%)より多い: Cap先読みで30円を超える前に停止。停止した場合、事実(完了したarm/clip・実費)をFableへ報告し、(a)残りclipだけの追加はCap内で可能か、(b)セリフを減らして再構成するかを判断(予算の追加は求めない・本Trialの上限30円内で判断)。
- 長いセリフで連続不合格(例: ASR転写ゆれ): 選定時に固有名詞転写ゆれのあるclip(`Bertie`系)を外してリスクを下げ済み。
