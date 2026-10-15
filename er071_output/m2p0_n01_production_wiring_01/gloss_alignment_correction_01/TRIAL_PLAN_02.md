# TRIAL_PLAN_02 (KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_02、2026-10-15)

TRIAL_PLAN_01からの差分のみ記す(OF-KGDC-07/08/09/10反映)。全結果はDEV/Trialであり、`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない。
順序: オフライン(O1/O2/relabel/unit/T3、JPY0)→ 有料T1(+P7)→ T2。独立batchは並列実行(最大7並列)。

## 実装mode
`align_glosses(..., mode="corrected")`(Trial専用、Production既定=legacy)。Trial runner `er071_gloss_alignment_correction_01_trial.py` は承認済み規則(sha256 447e07cb…、実行時抽出)込みの課題指示文(DESIGN_DRAFT_01 3.3+OF-KGDC (b))で、強制投入item(5件/batch)を `run_alignment_gate_corrected` へ直接かける(Production runner/Prompt/Gateは通らない)。
- 合否の主=LLM判定(`qa_reflects…=PASS`、真⇔不変の矛盾なし、記号チェック)。追加内容語→日本語span対応の機械検査(`machine_check`)は**record-only**で常時記録し、gate判定結果(`machine_check_pass_gate`)を**並記**する(誤NG・誤PASSの採否材料。gate化はユーザー判断)。
- retryはitem単位(未解決itemのみ再構築、各itemは最初の有効出力を採用、上限2回)。
- モデル: `routing.require_model("A2_SUPPORT")` = 現行SUPPORT_MODEL `gpt-6-luna`(最新世代系の現行ライン。旧/下位モデルは使わない。最新性の再確認は本Trialではしていない=VALIDATION_02に記載)、reasoning effort high(現行と同一)。

## T1 パターン(item数 × 2rep、5 item/batch)
| ID | 内容 | items | evals | 期待(自動近似) |
|---|---|---|---|---|
| P1 | 拡張KP・既知不整合(実記録由来6: based on interviews×『～』『〜』2表記/raw-bean prices/bring in a human helper/close around me/urge to watch) | 6 | 12 | 欠落語が反映(keyword近似+目視) |
| P2 | 既に正しいgloss(locked into a narrow view/インタビューをもとにした) | 2 | 4 | 不変 |
| P3 | 『～』を含む正当な辞書表現(point to/answer for/keep up with/fall into/speak for/turn out not to be/be associated with/put good odds on)。**`put solo travel at`は外した(規則15行型)** | 8 | 16 | 不変・誤NG 0 |
| P4 | 具体語欠落の注入(合成6) | 6 | 12 | 欠落語が反映 |
| P4b | 規則15行型 `put solo travel at`(期待NG側の**観察のみ**、再整合段の合否に使わない) | 1 | 2 | 観察 |
| P5 | 人称・主語語(close in on me/take one's time/catch one's breath、合成) | 3 | 6 | 欠落語が反映 |
| P6 | KP短縮・一般化 | - | - | 対象外(LLMに渡らない。O1でオフライン検証) |
| P7 | **追加語あり×自然な慣用的訳が正解**(bring in a human helper→人の手を借りる/raw-bean prices→生豆の値段/close around me→私を取り囲むように迫る/make ends meet→やりくりする/break the ice→緊張をほぐす/spill the beans→うっかり秘密をばらす) | 6 | 12 | 不変・record-only誤NG 0(gate判定の誤NGは並記) |
| 合計 | | 32 | 64 | 14 batch |

## T2(span実在・意味違い注入の誤PASS検出力)
12 item × 2rep = 24 eval = 6 batch。currentは「span対応は作れるが意味が誤り/直訳」(prices→量、me→彼ら、human→機械、costs→利益、small→大、cause→結果、local→外国、fresh→塩、意味反転、spill the beans→豆をこぼす 等)。LLMが不一致と判定し修正すれば検出成功、`current_gloss_consistent=真`で通せば誤PASS。独立verifier(案E)は採らない(Fable決定)。

## 報告指標(item単位、provenance=fresh)
- 1回目INVALID率 = 1回目attemptのverdict≠VALIDのeval数/eval数。2回とも失敗した率(=HR到達相当) = unresolved/eval数。各率は点推定+Clopper-Pearson片側95%上限を併記。
- 不変保証: P2/P3/P7の書換率(`changed`)・unresolved率・record-only誤NG(=unresolved or changed)・gate判定の追加誤NG(valid・不変だが `machine_check_pass_gate=False`)。
- 誤PASS: P1/P4/P5/T2で最終glossが不変、または欠落語keywordを含まない件数。gate判定が捕捉できたがrecord-onlyで採用された件数。
- 目視評価(Sonnet目視、ユーザー未確認): 直訳化(承認規則19行「直訳調を避ける」)・過剰具体化・意味ずれを全出力行について確認し、VALIDATION_02に記載。
- usage/cost_jpyは全呼出で記録(attempts[].usage / cost_jpy)。

## Status分類基準(TRIAL_PLAN_01 4節に追記)
- **REJECTED**: (a)機械検出可能な欠落(span欠落)がrecord-only+LLM判定をすり抜けて最終不整合(P1/P4/P5で最終gloss不整合が目視で残る)(b)FAILED itemのTTSが生成/Gateが通る(T3)(c)HR通知4条件のいずれかを欠いたまま下流が進む(T3)(d)対象外itemの差分>0(O1)(e)legacy既定の挙動が変わる(T3 k)(f)実測費用が上限JPY10超で暴走疑い。
- **VALIDATED**(Trial範囲。Production採用ではない): O1差分0・呼出0、O3/T3全件PASS、T1でP1/P4/P5の最終不整合0(目視)、P2/P3の書換・誤FAIL 0、**P7のrecord-only誤NG 0**、直訳化の目視評価で問題なし。量産判断は決定論部分(O1/O3/T3)+誤NG・HR率の点推定と95%上限の併記で行い、少数標本を超える主張はしない。
- **USER_DECISION_REQUIRED**: Production採用(常に)/機械検査のgate化(gate判定の追加誤NG・誤PASS捕捉数を材料にユーザー判断)/既定ON/OFF(別UDR)/P2,P3,P7で書換1件以上(許容度判断)/HR到達率が許容を超える見込み。
- いずれも`APPROVED_FOR_PRODUCTION`を意味しない。

## 費用見積り(出典: `gloss_alignment_01/cost_01.json`実測、5 item/batch high平均0.1137)
T1 14 batch ≈1.6(+retry・新スキーマ増分を見込み最大約3)、T2 6 batch ≈0.7(想定単価、実測で更新)。合計約3〜4円見込み、Guardrail上限JPY10(日次1,000円に対し約0.4%)。
