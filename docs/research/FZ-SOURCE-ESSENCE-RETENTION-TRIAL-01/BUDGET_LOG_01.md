# BUDGET_LOG_01: FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_02 費用台帳

案件上限150円(Fable設定。Opus見積約121円+予備16円)。出典=各`meta.json`/`*_run_summary.json`/`cost_log.jsonl`(1c)。Production同一モデル(gpt-6.1-sol effort=high、最新世代推奨モデル原則に該当)。評価LLMは使わない(評価費用0)。日付はJST(2026-10-25のみ=日付分割なし)。

| 起動(JST) | run | 内容 | 実費(円) | 累計(円) | 起動回数 | 再起動 | 備考 |
|---|---|---|---|---|---|---|---|
| 07:59:08〜約08:02 | 1a | R1のみ 3アーム×2本=6 call | 18.813 | 18.813 | 1 | 0 | 見積17円(委任文)に対し+1.8円 |
| 08:03:00〜約08:08 | 1b | 全段チェーン2サンプル(r0,r1,r2,std×2=8 call) | 30.557 | 49.370 | 1 | 0 | 見積32.2円。s1 14.70+s2 15.86 |
| 08:10:33〜約08:17 | 1c | Adv音声化(plan,support,kp,tts_b1b,gate,assemble) | 9.098 | 58.468 | 1 | 0 | 見積≤12円。plan/support/kpにStd分の少額LLMを含む(経路仕様) |
| 08:10:52〜約08:14 | Phase 2 賢者 | 全段1サンプル | 16.926 | 75.394 | 1 | 0 | 見積12.5円。reasoning token変動 |
| 同上 | Phase 2 開いた窓 | 同上 | 15.628 | 91.022 | 1 | 0 | 見積12.6円 |
| 同上 | Phase 2 猿の手 | 同上 | 17.788 | 108.810 | 1 | 0 | 見積19.4円 |
| 合計 | | | **108.81** | | 6 launch | 0 | 案件上限150円の72.5%。予備16円は未使用。 |

- 並列: Phase 2の3 processは独立のため同時起動(1cと並走)。同一run dirの再起動はなし。起動間隔150秒以上(同一run系列)は遵守(1a→1b 3分52秒、1b→1c 7分33秒)。
- 日次1,000円(JST)への寄与: 本委任108.81円(他案件の当日分は別)。
- 単価の根拠: 1a/1b/Phase 2=`provenance.json chain[].cost_jpy`、1c=`cost_log.jsonl`集計(e2e_stage_log `spent_jpy_cumulative` 9.0984)。再計算可能。

## 委任_04 再生成(『告げ口心臓』run_sf_prod_02、案A配線後の正式Production再生成、2026-10-25 JST)
承認=UDR #193(再生成・公開差替え承認、概算約40円)。`--approved-budget-jpy 80`(Fable判断: 300円以下の自律範囲でguard余裕のため70→80円)。出典=`e2e_stage_log.jsonl`の`spent_jpy_cumulative`差分(再計算可能)・`provenance.json chain[].cost_jpy`。モデル: writer/std=gpt-6.1-sol(Production既定=最新世代推奨)、TTS=gemini-3.8-flash-lite-tts+gemini-2.5-pro-preview-tts(Production正式)。

| 起動(JST) | 段 | 実費(円) | 累計(円) | 所要 | 再起動 |
|---|---|---|---|---|---|
| ① 10:35:57 | seed_check / writer(r0 2.57+r1 2.82+r2 5.34) / std_adjust 6.50 | 17.2400 | 17.24 | 約2.5分 | 0 |
| ② 10:42:17 | plan 0.13 / support 0.38 / kp 2.35 | 2.8691 | 20.1091 | 約4.7分 | 0 |
| ③ 10:47:42 | tts_b1b 6.70 / tts_a2 7.83 / provision_shell・gate・assemble・pages・page_verify 0 | 14.5307 | 34.6398 | 約8.3分 | 0 |
| 合計 | | **34.64** | | 起動3回 | 再起動0 |

- 概算約40円に対し**-5.36円**(retry 0・Human Review Lock 0・KP外側retry 0)。`--approved-budget-jpy 80`の43%。run_sf_prod_01(39.97円、KP再選定・TTS差替え込み)より低い。
- 追加LLM呼出0・新Validator 0・新retry 0。案Aによる増分はPrompt約+90 token/段(量産単価への影響は無視できる水準。実測: Std/Advのwriter 4段合計17.24円は`run_sf_prod_01` writer9.26+std6.84=16.10円に対し+1.14円[reasoning token変動を含むため案A単独の増分とは断定できない]。この差は今後の量産単価の観測対象だが、Trial時の+約0.05円の見積と矛盾しない範囲のばらつきと判断)。
- 日次(JST 2026-10-25): 起動前の`daily_dev_cost_01.py`採用値 665.93円(他案件のFX-CORE-NUMERIC等を含む全体、本再生成の①②を含む)。本再生成の寄与34.64円。1,000円以内。
- 退避: 旧公開ページ(58ファイル)をscratchpadへ退避してからpagesを再生成。旧run_sf_prod_01は`run dir`に残置(退避扱い)。
