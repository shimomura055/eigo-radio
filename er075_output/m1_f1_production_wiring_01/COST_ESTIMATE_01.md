# COST_ESTIMATE_01 費用見積

## 本委任(委任_02)の実費
JPY0(有料API呼出0、LLM不使用、TTS/ASR再生成なし)。根拠: 全scriptが既存転写のread-only再判定。`api_calls: 0` を出力JSONに記録(oov_options_12take_01.json / f1_census_01.json)。

## 実装・検証フェーズの追加有料runの要否
| 項目 | 要否 | 見積 | 出典 |
|---|---|---|---|
| F1 Validator変更の回帰(census・unit) | 不要 | JPY0 | 本委任の再現手順 |
| M1配線のreplay証拠(転写固定・ASRスタブ) | 不要 | JPY0 | EVIDENCE_PLAN_01 §2 |
| 正式経路での到達証拠(進行中のFamily X Coffee run内ログ) | 追加run不要(読取りのみ) | JPY0 | 委任_03管轄の既存run |
| 正式経路でM1「受理」を実際に発火させる短clip run(任意・UDR-1確定後のみ) | 要承認 | 短clip 24本(Std減速前後+Adv各、2エンジンASR): **約JPY3.3** | er069 results_02: 126観測(TTS+OpenAI ASR+Azure ASR)の合計 JPY17.27(TTS 3.90 + ASR 13.38)= 1観測 約JPY0.137、これに24を乗じた概算(桁の見積) |
| 長文(記事本編)のStd減速後実生成での実行証拠 | 要見積(現時点で出典なし) | 要Fable/委任_03の既存コスト表から算出(TTS+ASR各1記事分) | — |

## QCD
- Quality: F1は厳格化のみ(緩和0)、M1は承認済み範囲(OOV不採用)で誤PASS増なし。
- Cost: 本委任JPY0、実装後の追加ASR呼出は増えない設計(M1/F1は既存Primary転写を再判定するだけで追加APIなし。fallback時のSecondary呼出は既存回数の範囲)。
- Delivery: 本委任は設計・集計まで。実装・配線・証拠取得は後続。
