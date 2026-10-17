# RLCT Stage 1a 実測結果(STAGE_1A_RESULTS_01)

- 管理ID: FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_05 / 実走日: 2026-10-17(JST) / 性質: Trial(Production不変、未承認・採否判断なし)
- Status: STAGE_1A_COMPLETE_PENDING_FABLE(1b進行、B3構成差3段階、品質一対比較の人手判定はFable/後続)
- 実測基準: すべて OFFICIAL_API_RESPONSE(raw_usage_log.jsonl 20行、全 success=True、attempt_number最大1=技術retry 0)。web_search費用は harness pricing_snapshot($10/1,000 call=約JPY1.6/call)で、open_page/find_in_pageも課金callとして数える保守側(課金対象かは未確認)。
- 使用モデル(raw_usage_log.model_id実記録): Verifier=gpt-6-luna 11回 / B3=gpt-6.1-sol 9回(M0と同一設定、最新世代)。
- 注意: `aggregate.md`(er082_rlct_trial_01_aggregate.py出力)冒頭の「dry-runの値はSYNTHETIC(stub)」は固定キャプションで、本Stage 1aの値は実測。scriptは無変更(Trial範囲外の改修を避けた)。
- 生データ: `er082_output/rlct_trial_01/<article>/<method>/result.json`、`raw_usage_log.jsonl`、`aggregate.json/md`、`integrity/`(run別 before/after/check/run_summary)、`console_0*.txt`。

## 1. 費用(実測、JPY)

| 記事 | 方式 | LLM | web_search | 合計 | 本番換算 | M0比削減JPY | 削減% |
|---|---|---|---|---|---|---|---|
| coffee_prices | M0 | 0.0 | 0.0 | 0.0 | 55.919 | 0.0 | 0.0 |
| coffee_prices | M0b | 12.695 | 0.0 | 12.695 | 57.677 | -1.758 | -3.1 |
| coffee_prices | M0p | 1.996 | 16.0 | 17.996 | None | None | None |
| coffee_prices | M1 | 12.956 | 20.8 | 33.756 | 53.603 | 2.316 | 4.1 |
| coffee_prices | M2 | 23.781 | 8.0 | 31.781 | 51.628 | 4.291 | 7.7 |
| coffee_prices | M3 | 12.003 | 6.4 | 18.403 | 49.65 | 6.269 | 11.2 |
| inbound_tourism | M0 | 8.465 | 0.0 | 8.465 | 65.283 | 0.0 | 0.0 |
| inbound_tourism | M0b | 8.328 | 0.0 | 8.328 | 65.146 | 0.137 | 0.2 |
| inbound_tourism | M0p | 2.326 | 22.4 | 24.726 | None | None | None |
| inbound_tourism | M1 | 12.271 | 17.6 | 29.871 | 58.432 | 6.851 | 10.5 |
| inbound_tourism | M2 | 11.378 | 6.4 | 17.778 | 46.339 | 18.944 | 29.0 |
| inbound_tourism | M3 | 1.001 | 8.0 | 9.001 | 48.029 | 17.254 | 26.4 |

- Stage 1a合計(任意A除く): LLM 107.200 + web_search 105.600 = **JPY 212.800**(Coffee 114.631 / inbound 98.169)
- 見積(期待267.6、上限493.0)に対し 実測÷期待 = **0.795**、実測÷上限 = 0.432。
- 任意A(Coffee、別枠上限54): JPY 10.882。Trial総計(1a+任意A) = JPY 223.682(累計上限1,040の21.5%)。
- 本日累計(JST、他タスク分60.4を加算) = 約JPY 284.1 / 日次soft 1,000。超過なし。
- 本番換算は aggregate.py の定義(Research+Ledger+B3[+再選定]を共有分も帰属)。Coffee M0のB3は既存Sol B3の再利用(API 0)で、Trial費用0.0を確認。

## 2. web_search呼出(action.type別)と上限3の遵守(M1/M3)

| 記事 | 方式 | 呼出計 | search | open_page | find_in_page | クエリ | 検索課金換算JPY | calls/Fact平均(各request) | soft cap超過見込み |
|---|---|---|---|---|---|---|---|---|---|
| coffee_prices | M0 | 0 | 0 | 0 | 0 | 0 | 0.0 | - | なし |
| coffee_prices | M0b | 0 | 0 | 0 | 0 | 0 | 0.0 | - | なし |
| coffee_prices | M0p | 10 | 4 | 4 | 2 | 16 | 16.0 | full=0.588 | なし |
| coffee_prices | M1 | 13 | 6 | 6 | 1 | 23 | 20.8 | full=0.765 | なし |
| coffee_prices | M2 | 5 | 3 | 1 | 1 | 10 | 8.0 | r0=1.25 | なし |
| coffee_prices | M3 | 4 | 2 | 1 | 1 | 7 | 6.4 | r0=0.75; r1=1.0 | なし |
| inbound_tourism | M0 | 0 | 0 | 0 | 0 | 0 | 0.0 | - | なし |
| inbound_tourism | M0b | 0 | 0 | 0 | 0 | 0 | 0.0 | - | なし |
| inbound_tourism | M0p | 14 | 5 | 8 | 1 | 17 | 22.4 | full=0.933 | なし |
| inbound_tourism | M1 | 11 | 5 | 4 | 2 | 20 | 17.6 | full=0.733 | なし |
| inbound_tourism | M2 | 4 | 2 | 1 | 1 | 7 | 6.4 | r0=1.0 | なし |
| inbound_tourism | M3 | 5 | 3 | 2 | 0 | 9 | 8.0 | r0=1.25 | なし |

- 遵守率(M1/M3、記録できた範囲): M1 Coffee 0.765 / inbound 0.733、M3 Coffee 0.75・1.0 / inbound 1.25 calls/Fact(いずれも3以下)。soft cap超過見込みのrequest=0件(遵守率 100%)。
- 限界: 呼出はrequest単位で記録され、Fact別の呼出数はAPIレスポンスから帰属できない(平均値のみ)。個々のFactが3回を超えたかは判定不能。Verifierへの上限は「Prompt指示」であり強制ではない。
- open_page/find_in_page込みの総数で上限相当を評価している(保守側)。課金対象がsearchのみなら費用は表の検索課金換算より小さくなる(Production集計もweb_search_call全件課金扱い)。

## 3. verdict遷移(M0 Ledger → 方式の最終verdict)

| 記事 | 方式 | 遷移件数 | 降格(VERIFIED→) | 昇格(→VERIFIED等) |
|---|---|---|---|---|
| coffee_prices | M0 | {"VERIFIED->VERIFIED": 13, "AMBIGUOUS->AMBIGUOUS": 4} | - | - |
| coffee_prices | M0b | {"VERIFIED->VERIFIED": 13, "AMBIGUOUS->AMBIGUOUS": 4} | - | - |
| coffee_prices | M0p | {"VERIFIED->VERIFIED": 12, "VERIFIED->AMBIGUOUS": 1, "AMBIGUOUS->AMBIGUOUS": 2, "AMBIGUOUS->VERIFIED": 2} | F02 | F12,F17 |
| coffee_prices | M1 | {"VERIFIED->VERIFIED": 13, "AMBIGUOUS->AMBIGUOUS": 1, "AMBIGUOUS->VERIFIED": 3} | - | F12,F16,F17 |
| coffee_prices | M2 | {"VERIFIED->VERIFIED": 3, "AMBIGUOUS->REJECTED": 1} | - | - |
| coffee_prices | M3 | {"VERIFIED->VERIFIED": 4, "AMBIGUOUS->REJECTED": 1} | - | - |
| inbound_tourism | M0 | {"VERIFIED->VERIFIED": 11, "AMBIGUOUS->AMBIGUOUS": 2, "REJECTED->REJECTED": 2} | - | - |
| inbound_tourism | M0b | {"VERIFIED->VERIFIED": 11, "AMBIGUOUS->AMBIGUOUS": 2, "REJECTED->REJECTED": 2} | - | - |
| inbound_tourism | M0p | {"VERIFIED->VERIFIED": 11, "AMBIGUOUS->VERIFIED": 1, "REJECTED->REJECTED": 2, "AMBIGUOUS->AMBIGUOUS": 1} | - | F04 |
| inbound_tourism | M1 | {"VERIFIED->VERIFIED": 11, "AMBIGUOUS->VERIFIED": 1, "REJECTED->AMBIGUOUS": 1, "AMBIGUOUS->AMBIGUOUS": 1, "REJECTED->VERIFIED": 1} | - | F04,F05,F12 |
| inbound_tourism | M2 | {"VERIFIED->VERIFIED": 2, "AMBIGUOUS->VERIFIED": 1, "REJECTED->AMBIGUOUS": 1} | - | F04,F05 |
| inbound_tourism | M3 | {"VERIFIED->VERIFIED": 2, "AMBIGUOUS->VERIFIED": 1, "REJECTED->AMBIGUOUS": 1} | - | F04,F05 |

- 補足: M2/M3は選定Fact(再選定込み)のみ検証するため遷移は検証対象Factのみ。M1/M0pは全Fact再検証。M0pでCoffee F02が VERIFIED→AMBIGUOUS(同日上限なし再検証でも降格が起こり得る=R-04の観測)。

## 4. 選定Fact・Jaccard(M0比)・再選定

| 記事 | 方式 | 選定Fact | Jaccard vs M0 | 再選定回数 | 再選定追加費用JPY(b3_reselect) | 未成立 |
|---|---|---|---|---|---|---|
| coffee_prices | M0 | F02,F07,F09,F11 | - | - | 0 | なし |
| coffee_prices | M0b | F02,F07,F09,F11 | 1.0 | - | 0 | なし |
| coffee_prices | M0p | - | - | - | 0 | なし |
| coffee_prices | M1 | F02,F07,F09,F15 | 0.6 | - | 0 | なし |
| coffee_prices | M2 | F01,F09,F15 | 0.167 | 1 | 11.346 | なし |
| coffee_prices | M3 | F01,F09,F10,F15 | 0.143 | 1 | 11.055 | なし |
| inbound_tourism | M0 | F01,F02,F09 | - | - | 0 | なし |
| inbound_tourism | M0b | F01,F02,F03,F09 | 0.75 | - | 0 | なし |
| inbound_tourism | M0p | - | - | - | 0 | なし |
| inbound_tourism | M1 | F01,F02,F04,F05 | 0.4 | - | 0 | なし |
| inbound_tourism | M2 | F01,F02,F04,F05 | 0.4 | 0 | 0 | なし |
| inbound_tourism | M3 | F01,F02,F04,F05 | 0.4 | 0 | 0 | なし |

- 再選定loop: Coffee M2/M3は共有初回B3の選定にREJECTED(F07)が含まれ、再選定1回で解消(M2: F01,F09,F15 / M3: F01,F09,F10,F15)。inbound M2/M3は再選定0回(初回選定にREJECTEDなし)。再選定上限2回到達・未成立: 0件。設計は「inbound再選定がほぼ確実」だったが実測はCoffeeで発生、inboundでは未発生(loop動作はCoffeeで実走確認)。
- 再選定の追加費用: Coffee M2 JPY11.346 / M3 JPY11.055+検証JPY1.883(いずれもB3再呼出が支配)。
- 注意: Jaccardは採否基準ではなく指標。M2/M3は初回B3が共有(同一Prompt)で、M0と選定が異なる主因はVerifier verdictがB3入力に含まれる/含まれないというPrompt差に由来(B3構成差3段階の判定は本委任の範囲外)。

## 5. 中心FactのAMBIGUOUS断定(機械抽出のみ。断定判定はSonnet+Fable/人手)

| 記事 | 方式 | 中心Fact内のAMBIGUOUS Fact | 件数 |
|---|---|---|---|
| coffee_prices | M0 | F12 | 1 |
| coffee_prices | M0b | F07,F12 | 2 |
| coffee_prices | M0p | (選定なし/M0p) | - |
| coffee_prices | M1 | F07 | 1 |
| coffee_prices | M2 | - | 0 |
| coffee_prices | M3 | - | 0 |
| inbound_tourism | M0 | F04 | 1 |
| inbound_tourism | M0b | F04,F06 | 2 |
| inbound_tourism | M0p | (選定なし/M0p) | - |
| inbound_tourism | M1 | F05,F06 | 2 |
| inbound_tourism | M2 | F05 | 1 |
| inbound_tourism | M3 | F05 | 1 |

- 機械抽出はStoryline内でAMBIGUOUS Factが中心(central)扱いされている件数。Writerへ「断定」として渡るか否かの判定は人手(原文: `<article>/<method>/storyline_b3/`配下)。

## 6. 契約検証(B3 annotation producer/validate/ledger完全性)

| 記事 | 方式 | producer | validate | ledger_complete | all_pass |
|---|---|---|---|---|---|
| coffee_prices | M0 | PASS | PASS | PASS | True |
| coffee_prices | M0b | PASS | PASS | PASS | True |
| coffee_prices | M0p | (M0p: B3なし) | - | PASS | - |
| coffee_prices | M1 | PASS | PASS | PASS | True |
| coffee_prices | M2 | PASS | PASS | PASS | True |
| coffee_prices | M3 | PASS | PASS | PASS | True |
| inbound_tourism | M0 | PASS | PASS | PASS | True |
| inbound_tourism | M0b | FAIL(AnnotationProducerError d_tags 【2019年…】) | - | PASS | False |
| inbound_tourism | M0p | (M0p: B3なし) | - | PASS | - |
| inbound_tourism | M1 | FAIL(AnnotationProducerError d_tags 【2019年…】) | - | PASS | False |
| inbound_tourism | M2 | FAIL(AnnotationProducerError d_tags 【2019年…】) | - | PASS | False |
| inbound_tourism | M3 | FAIL(AnnotationProducerError d_tags 【2019年…】) | - | PASS | False |

- OPEN-407の影響: inboundでF03(M0b)またはF04(M1/M2/M3)を選定した方式のみFAIL。**inbound M0(F01,F02,F09選定)とCoffee全方式はPASS**=「全方式で同一のpre-existing事象」ではなく、「ラベル付きclaim(F03/F04)が選定された方式でのみ発生」するProducer側の既存挙動。Trial方式の欠陥ではなくFact選定内容に依存。Trialは止めずに記録(委任のとおり)。
- 含意: inboundでF04を選ぶ方式(M1/M2/M3)をProduction化する場合、OPEN-407が現行Productionでも課金前STOP要因になり得る(是正要否はFable/ユーザー判断)。

## 7. 既知欠陥3値(a_selected_detected / b_selected_missed / c_not_selected)

| 記事 | 方式 | 状態 |
|---|---|---|
| coffee_prices | M0 | {"F12": "c_not_selected", "F07": "a_selected_detected", "F16": "c_not_selected", "F17": "c_not_selected"} |
| coffee_prices | M0b | {"F12": "c_not_selected", "F07": "a_selected_detected", "F16": "c_not_selected", "F17": "c_not_selected"} |
| coffee_prices | M0p | - |
| coffee_prices | M1 | {"F12": "c_not_selected", "F07": "a_selected_detected", "F16": "c_not_selected", "F17": "c_not_selected"} |
| coffee_prices | M2 | {"F12": "c_not_selected", "F07": "c_not_selected", "F16": "c_not_selected", "F17": "c_not_selected"} |
| coffee_prices | M3 | {"F12": "c_not_selected", "F07": "c_not_selected", "F16": "c_not_selected", "F17": "c_not_selected"} |
| inbound_tourism | M0 | {"F05": "c_not_selected", "F12": "c_not_selected"} |
| inbound_tourism | M0b | {"F05": "c_not_selected", "F12": "c_not_selected"} |
| inbound_tourism | M0p | - |
| inbound_tourism | M1 | {"F05": "a_selected_detected", "F12": "c_not_selected"} |
| inbound_tourism | M2 | {"F05": "a_selected_detected", "F12": "c_not_selected"} |
| inbound_tourism | M3 | {"F05": "a_selected_detected", "F12": "c_not_selected"} |

- b_selected_missed(欠陥Factを選定しVERIFIEDで通した検出漏れ)は0件。inbound F05は M0 ではREJECTED(未選定)だが、M1/M2/M3 では最終 verdict=AMBIGUOUS で選定・中心Factに入った(a_selected_detected、REJECTED→AMBIGUOUS)。AMBIGUOUS断定リスクの人手判定対象(§5)。

## 8. 任意A(Coffee、故障注入3件×{上限なし,上限付き})

| 注入Fact | 種別 | 上限なし | 上限付き |
|---|---|---|---|
| INJ_F02_numeric_1 | numeric | REJECTED | REJECTED |
| INJ_F07_date_2 | date | REJECTED | REJECTED |
| INJ_F09_direction_3 | direction | REJECTED | REJECTED |

- 検出漏れ(重大NG)= **0件**(critical_ng=False)。元draft不変=True。費用JPY10.882。
- 限界: 3件のみで検出率の保証にはならない(ユーザー§5)。inbound/streamingの任意Aは1b後(未実施)。

## 9. 整合性(Production・再利用成果物sha)

- 01_smoke_coffee_M2_check.json: identical=True diffs=0
- 02_coffee_rest_check.json: identical=True diffs=0
- 03_inbound_check.json: identical=True diffs=0
- optA_integrity_check.json: identical=True
- Production 12ファイル: `git status --porcelain` で変更0(実走前後)。

## 10. 1b進行条件(TRIAL_DESIGN_02 4-8、事前定義)の機械判定(進行可否はFable判断)

| 条件 | 判定 | 根拠 |
|---|---|---|
| 上限遵守率の記録が取れている | 充足 | request別action.type・calls/Fact平均を全M1/M2/M3で記録、soft cap超過0。ただしFact別は取得不能(§2限界) |
| 再選定loopが仕様どおり動作 | 充足(Coffeeで実走確認) | Coffee M2/M3で再選定1回、REJECTED F07除外、検証済み再利用、未成立0。inboundは再選定が発生せず未実走 |
| 実測費用÷見積≦1.3 | 充足 | 212.8/267.6 = 0.795 |
| Production・再利用成果物sha不変 | 充足 | integrity_check全identical |

## 11. 人手判定に回す事項(本委任では実施しない)

- B3構成差3段階、品質一対比較、中心FactのAMBIGUOUS断定判定: 原文は `er082_output/rlct_trial_01/<article>/<method>/storyline_b3/` と `research_ledger/` 配下。
- 観測の要点(判定ではない): (1)Coffee M0p/M1でF12,F16,F17がAMBIGUOUS→VERIFIEDに昇格、F02はM0pでVERIFIED→AMBIGUOUS(Verifier結果の揺らぎ。M0'の意義)、inbound M1ではF12(既知欠陥、M0でREJECTED)がREJECTED→VERIFIEDに昇格(未選定のため実害はないが、Verifier判定の再現性が低い証拠。選定された場合のb_selected_missedリスク) (2)inbound M2/M3は費用削減26〜29%だがF05(M0でREJECTED)がAMBIGUOUSで選定される (3)Coffee M3はM2比でさらに安い(18.4 vs 31.8)が選定Factが異なる(F10追加)。
