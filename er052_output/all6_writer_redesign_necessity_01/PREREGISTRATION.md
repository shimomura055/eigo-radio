# PREREGISTRATION: ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01(2026-10-08)

性質: Trial(比較実験、Production経路ではない)。Status上限=MEASURED。合否しきい値なし(ユーザー指示)。

## 1. 問い
現在gpt-5.6-lunaを使っている工程をgpt-6-lunaへ切り替えると、記事の事実NG率・重大見逃しがどれだけ良化/悪化するか。数値化のみ。Writer根本設計の要否はこの数値を見てFable/ユーザーが判断する。

## 2. 2群
- baseline: 現行構成(Writer/Fact Check/EN=gpt-5.6-luna、Checker=gpt-6-luna)。harnessは無変更。
- all6: 5.6-lunaを使う全工程をgpt-6-lunaへ差替え(下表)。Checkerは両群同一(gpt-6-luna)。

## 3. 差替え対象表(Grepで確定)
| 工程 | 参照箇所 | baseline | all6 | 差替え手段 |
|---|---|---|---|---|
| JA Writer R0/R1/R2/must-fix再生成 | `er019_family_x_ja_writer_o_r1_r2_01.WRITER_MODEL`(=`vfl01.MODEL`=Routing `WRITER_MODEL`、L48、使用L211/L225) | gpt-5.6-luna | gpt-6-luna | harnessでmodule属性を書換(`require_model_or_override("B1_WRITER", ..., override_reason)`) |
| JA Fact Check(Original/R2、再判定) | `vfl01.run_deviation_check`(model既定=def時束縛`MODEL`) | gpt-5.6-luna | gpt-6-luna | 関数をラップし既定model注入(`"WRITER_FACT_CHECK"` override) |
| EN Advanced(忠実英訳+In one line) | `er003_v1_n3_01_advanced_adaptation_generate.generate_family_x_faithful_translation/_in_one_line`(`model or routing.require_model(..., WRITER_MODEL)`) | gpt-5.6-luna | gpt-6-luna | 関数をラップしmodel引数注入(`"A2_WRITER"` override) |
| EN Fact Check(Advanced deviation) | 同`vfl01.run_deviation_check`(`er012`L382/L415) | gpt-5.6-luna | gpt-6-luna | 上に同じ |
| Checker(`run_checker_after_p01.py`→`runner.MODEL`、`OPEN233_APPROVED_FLOW_SWITCHES["MODEL"]`) | `er052_open233_self_recovery_flow_runner_01.py` L281/L523 | gpt-6-luna | gpt-6-luna | 別process起動のため両群同一(harnessは触れない) |
| Researcher/Verification/ledger | 固定台帳を使用し実行されない(`research_calls==0`をDEV runnerがassert) | 対象外 | 対象外 | - |

実使用model_idは各runの`raw_usage_log.jsonl`(APIレスポンスのmodel)から`manifest.json`へ実測記録する。

## 4. Checker構成(ユーザー質問「前回Trialと同じValidatedされた仕様か」の材料)
- DEV runner phase2が呼ぶ`run_checker_after_p01.py`は`runner.apply_open233_approved_flow_switches()`(`OPEN233_APPROVED_FLOW_SWITCHES`既定)を適用。直近のOPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01と同じ構成(同スイッチdumpのsha256を各runのmanifestに記録し、E2E_02 dumpとの一致フラグも`checker_after_provenance.json`に残る)。
- OPEN_ITEMS行 `OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01` の行頭Status文字列(引用): **`APPROVED_FOR_PRODUCTION(配線中・実装完了・E2E9/20完走・正式集計済・9/20で一旦停止・PRODUCTION_WIRED未)`**。VALIDATEDではなくAPPROVED_FOR_PRODUCTION(配線中)。Checkerの再分類(RECLASSIFY-02)側がVALIDATED。
- 夜間ループで追加した新スイッチ(①v3/②読者信念テスト/W1-W2)は既定OFFのまま(`OPEN233_APPROVED_FLOW_SWITCHES`に含まれない)で、両群同一。

## 5. 固定条件
- brief 12本(B3 Trial V0 b1-b4 x meta/hormuz/space_weapons)の`selected_brief.md`を`--brief-md`で固定(B3は実行しない)。台帳はpolysemy_trial_02/ledgers/<slug>/control(b3 V0 b*のledgerとsha一致)。brief sha256は各runのmanifestとMANIFEST.jsonに記録。
- reasoning effort=high、Checker ON(両群同一)、並列度4(自動降格4->2->1)、`--budget-jpy 12`(phase1/phase2各)・Checker `--checker-budget-jpy 10`。
- 2群は同一driverで交互投入(同時間帯)。反復2。計 12 x 2群 x 2 = 48本(smoke 2本を含む)。
- out_dir規約: `runs/<slug>/control/b<i>__<arm>__r<j>`(DEV runnerのout_dirガードが`/control/`を要求するため、委任文の`runs/<slug>/b<i>/<arm>/r<j>/`から変更)。
- 費用計算の注意: 既存のcost.json(`compute_stage_cost_breakdown`)はpricing tableにgpt-6-lunaが無く0円になる(smokeで確認)。集計では$/1M(5.6: 0.20/0.02/1.20、6: 0.10/0.01/0.50、DECISION_LOG L12925-12933)とUSD/JPY=160でraw_usage_logから再計算する。

## 6. 指標
T-A: 評価者採点の 重大件数・軽微NG/記事・保留/記事(JA R2・EN別、テーマ別、評価者別)、R0->R2初出件数、NG型分布、群間の差と比。副指標: JA Fact Check MAJOR率・must-fix率・STOP率、Checker findings/Rewrite件数、費用/本、所要時間/本。T-B: 重大の検出率(MAJOR判定、モデル別・反復別)、軽微の検出率(MAJORまたはMINOR)、MINOR->MAJOR非対称件数。
しきい値なし。Nが小さいため差と比のみ報告し、有意性は主張しない。

## 7. T-B対象(`T-B/items.json`)
既知重大のうち記事入力を解決できた7件(PAST-meta-p2r2-02、ai-p2r1-01、sw-p2r2-01/02、jb9k-03=JA R2/R0由来、ai-p2r1-02・hormuz-T0M0r2-01=EN由来[ENをEN本文+JA R2をsourceとして入力])。除外: PAST-ai-p2r2-07(Rewrite工程が一時生成した文で最終記事に存在しないため入力不能)。89wfはsw-p2r2-01/02と同事象(同一記事)のため重複計上しない。したがって「重大8件」ではなく解決できた**7件**。軽微は台帳(`known_relation_ng.jsonl`)のB3由来・R2に存在・軽微NGから型別(方向/極性・主体・範囲・未提示断定、各4件、seed=20261008)16件(比喩は該当NG無し)。検出判定=NG文との文字bigram重なり>=0.4の逸脱がMAJOR(重大)/MAJORまたはMINOR(軽微)。記事全体にMAJORが1件でもあれば別指標「記事単位MAJOR」として併記。

## 8. 盲検手順(T-A)
完了記事のJA R2・EN・R0を匿名コード化し`eval/_private/MAP.json`にarm対応を隔離、評価者へはarm・モデル名を非開示。両群を1パックに混在。評価者=APIジャッジ2系統(gpt-5.6-luna / gpt-6-luna、いずれもrubric適用)を記事へ無作為配分し、各評価者に両群同数(評価者とarmの交絡を避ける)。MAP開封は集計時のみ。評価者はLLM単独判定で人間確認なし(`HUMAN_CHECK_TA.md`に重大候補を列挙)。

## 9. 費用見積(上限¥500 Guardrail)
T-A 48本(baseline ≈¥9/本、all6 ≈¥5/本の見込み)≈¥330、T-B ≈¥40、盲検評価 ≈¥60〜90。合計は上限近辺の見込みで、超過時は承認済みscope内・原因把握済みの場合に限り記録して継続。暴走疑い時のみSTOP。
