# plan_01 (事前登録、Phase 2有料の前。FAMILY-Z-KP-DB-HYBRID-M2P0-MIGRATION-TRIAL-01 委任_01)

## 登録内容
- 対象テキスト(全てFamily Zの既存原稿、再生成しない): (1) melos_std = run_e2e_02/writer/std.md(Std、process=A2_SUPPORT) (2) melos_adv = run_e2e_02/writer/r2.md(Adv、B1_SUPPORT) (3) lemon_l11 = er055_output/family_z_d_predictive_validation_trial_01/L11/story_en.md(別Z原稿、一般化用、A2_SUPPORT)
- arm:
  - 対照 Strategy L: Melos Std/Advは**既存出力を再利用**(run_e2e_02/key_phrases/{a2,b1b}、再生成しない)。Lemonのみ対照が存在しないため、Z現行経路(`w62.run_kp_with_outer_retry`既定select_fn)を**1回**実行(Trial原稿・Production KPではない)。
  - DB Hybrid + M2P0(案1): `w62.run_kp_with_outer_retry`の`select_fn`を`sc.run_key_phrase_selection(kp_backend="db_hybrid")`に差し替え。n=3/テキスト、各runでshortlist_cacheは新規(M2供給も毎回実施)。
- モデル: gpt-6-luna(Production同一、比較可能性の例外。`routing.require_model`で解決、実測model_idを記録)。
- 並列化: テキスト単位に3 process(独立out dir、同一ファイル競合なし、Wiktionary待ちが律速のため)。各processは自分のcost logをout-dir内に追記、全process合算でbudget guard。

## 費用見積(job数×単価)
| 項目 | job数 | 単価(出典) | 小計(期待) | 最悪 |
|---|---|---|---|---|
| DB Hybrid run 1回(selection 1 + canon 1 + redundancy 1 = 1 attempt) | 9 run × 期待1.5 attempt | 1 attempt約JPY1.0 = selection 0.29-0.40(er064 cost_r1.json) + canon/redundancy 約0.4+0.2(Melos run_e2e_02 cost_log.jsonl stage=kp 13 call JPY5.35の平均0.41/callから) | 約13.5 | Z外側retry3 attempt + redundancy retry = 約JPY5/run -> 45 |
| Strategy L対照(Lemon) | 1 run | 1 attempt約1.0 × 期待2.5 attempt(Melos Stdで3 attempt実績) | 約2.5 | 5 |
| M2供給(Wiktionary) | 9 run | 外部API無料 | 0 | 0 |
| 合計 | | | **約JPY16** | guardで **JPY50 hard** |
- 上限: 全process合算 JPY50(Guardrail)、soft JPY35。各call前に合算実費(cost log + er009 pricing)を確認し、JPY50到達でSTOP。soft到達は記録して継続可否判断。
- 見積はJPY50以内(縮小不要)。fallback(Strategy L)はProduction契約どおり発火しうる。発火時は別途カウントし、DB Hybrid成功とは扱わない。

## 評価指標(事前登録)
(1) 選定品質: 最終KP(canonicalization後)をP0価値基準(慣用句・比喩・句動詞・学習価値)で目視ラベル(正/粒度不良/誤/低価値)。Strategy L既存結果との差分、Strategy Lで選ばれていた良いKPが失われたか。Fiction固有(台詞の口語・固有名詞・比喩)。
(2) Validator整合: 選定gate/canonicalization/Redundancy/symbolのPASS率、Rule7 INVALID率、fallback発火率。
(3) 費用・処理時間(Strategy L比)。
(4) 品質劣化の有無。
(5) 安定性: n=3の最終KP集合のJaccard(display_phrase小文字化)。
- Status基準(事前): VALIDATED = gate PASS率>=所定、かつ目視で品質劣化なし(Strategy Lの良質KPを失わない)。REJECTED = 劣化が明確かつ再現。USER_DECISION_REQUIRED = 移行方式の採用判断が必要(Productionは常にユーザー判断)。
- state_guard: run_e2e_02配下のsha256 manifest、Production py sha256、telemetry系ファイル行数、作業前後で比較。
