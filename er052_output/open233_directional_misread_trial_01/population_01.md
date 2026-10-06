# population_01 (OPEN-233 directional misread Trial 母集団再集計, ¥0, LLMなし)

## 所見
- 新9 run = 2種のLedgerのみ(hormuz系4run=12 fact / meta系5run=15 fact)。Ledger全Fact数: 計123件(run平均13.67)。
  注: 計123はStage 1候補『123件』とは別物(偶然の一致。Stage 1候補=66件/run平均7.33)。
- 状態変化Fact(語彙近似・LLMなし): 30件/123 = 24.4%(run平均3.33)。近似のため精度未検証。語は弱いもの(適用/上昇/再開等)を含み偽陽性・偽陰性あり。
- 単位→fact対応: run jsonに**保存なし**(per_route.unit_status/model_verdictは単位ID→SUPPORTED/CANDIDATEのみ、support_fact_idsはE2E出力全体で0件。checker L670の既知制約)。
- 記事側確認件数/run: 下限=3.33(状態変化fact数、各1単位と仮定) / 近似mid=7.46(判定単位30.56×状態変化比率) / 上限=30.56(Stage 1判定単位全数)。タイトル・見出し含む。最終本文でなく修正前fixture本文で計数(9 run分、文数再計算と保存値は273 vs 275でほぼ一致)。

## 表1 run別
| instance | fixture | facts | 状態変化近似 | 全単位 | 判定単位 | S1候補 |
|---|---|---|---|---|---|---|
| bgroup_B3 | B3 | 12 | 5 | 35 | 27 | 2 |
| hormuz_run03_advanced | hormuz_run03_advanced | 12 | 5 | 34 | 24 | 8 |
| hormuz_run03_standard | hormuz_run03_standard | 12 | 5 | 44 | 34 | 9 |
| meta_run03_advanced | meta_run03_advanced | 15 | 2 | 38 | 28 | 5 |
| meta_run03_standard | Meta_run03_standard | 15 | 2 | 47 | 37 | 11 |
| neg1_meta_b3prod_a2 | neg1_meta_b3prod_a2 | 15 | 2 | 52 | 38 | 14 |
| neg2_meta_refresh_a2 | neg2_meta_refresh_a2 | 15 | 2 | 43 | 33 | 7 |
| neg3_hormuz_prodrunner_b1b | neg3_hormuz_prodrunner_b1b | 12 | 5 | 27 | 20 | 5 |
| neg7_meta_prodrunner_b1b | neg7_meta_prodrunner_b1b | 15 | 2 | 44 | 34 | 5 |

## 表2 単価(実績逆算)
- Stage 2/Checker model=gpt-6-luna(runner L280)、effort=high。call_log135件から逆算: 入力¥10.7/1M tok、出力(reasoning含む)¥81.7/1M tok。公式単価表はrepo内に無く未確認。Anthropic側単価表もrepo内に無い(パイプラインはAnthropic API不使用、OPUS-MODEL-ID-INVENTORY結果)。
- 実績参照: Stage 2後段¥7.29/89判定=¥0.0819/判定(48 call)。現行E2E総額¥31.52/9run=¥3.50/run。

## 表3 追加処理コスト/run(¥、同一model gpt-6-luna、per-fact単独call)
| 水準 | Ledger側全Fact | 記事側 | 合計 |
|---|---|---|---|
| low | 0.155 | 0.034 | 0.189 |
| mid | 0.166 | 0.084 | 0.25 |
| high | 0.512 | 1.127 | 1.639 |
- low/mid=推論ほぼ無し(出力80/60tok)。highはreasoning上乗せ(+300tok)を許容。実際のeffort=highで運用すると出力が大幅増(Stage 1実績: 1 call出力約8.7k tok)で、highを超える可能性がある。
- Ledger側別model(単価0.5x/2x仮定、単価未確認): 合計mid ¥0.167/¥0.416。

## 表4 状態変化近似の根拠語(Ledger別、fact_id: 根拠語)
語彙: ロールバック/撤回/復元/復活/再開/停止/中止/縮小/拡大/増加/減少/引き上げ/引き下げ/延期/前倒し/開始/終了/解除/導入/廃止/上昇/下落/低下/許可/禁止/承認/却下/追加/削除/免除/適用/緩和/強化/取り下げ/見送り/撤廃/値上げ/値下げ/引き上/引き下/急落/急騰/凍結/再導入/可決/否決/再び
- B3系(12 fact): HF-003:免除; HF-004:適用; HF-006:上昇; HF-009:撤回/縮小; HF-011:上昇 / 非該当: HF-001,HF-002,HF-005,HF-007,HF-008,HF-010,HF-012
- meta_run03_advanced系(15 fact): MUSE-HC-003:許可; MUSE-HC-012:ロールバック/開始 / 非該当: MUSE-HC-001,MUSE-HC-002,MUSE-HC-004,MUSE-HC-005,MUSE-HC-006,MUSE-HC-007,MUSE-HC-008,MUSE-HC-009,MUSE-HC-010,MUSE-HC-011,MUSE-HC-013,MUSE-HC-014,MUSE-HC-015

## 所在
- fixture→Ledger: runner build_target_instances()の`fixture[ledger_text]`(source_pathは表1json参照、population_01.json rows[].source_path)。Ledger全文は各source_path(er019/er037配下audit/deviation_checks等)のledger_text。
