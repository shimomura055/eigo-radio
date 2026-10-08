# RESULT: ALL-6-LUNA-WRITER-REDESIGN-NECESSITY-TRIAL-01(2026-10-08、委任_01)

Status=**MEASURED**(数値化完了。VALIDATED/APPROVED_FOR_PRODUCTION は宣言しない)。合否しきい値なし(ユーザー指示)。Production変更なし(Routing契約・er019・er003は無編集、Trial harnessのmonkeypatchのみ)。実費 合計 ¥382.6 / ¥500(再計算値、下記)。

## 0. 設計の要点
- 2群: baseline(Writer/JA・EN Fact Check/EN=gpt-5.6-luna)対 all6(同工程を全てgpt-6-luna)。Checkerは両群とも別processでgpt-6-luna、`OPEN233_APPROVED_FLOW_SWITCHES`既定(スイッチdump sha256は両群の完走19+19本で同一 `66d18a3a...`)。夜間ループの新スイッチは既定OFF。
- 差替え対象と実測model_id: baseline 24/24本の全Writer系工程=`gpt-5.6-luna`、all6 24/24本=`gpt-6-luna`(各runの`raw_usage_log.jsonl`のAPIレスポンスmodelから実測、`MANIFEST.json`)。R0->R1->R2の`previous_response_id`連鎖はall6でも成立(smokeで`chain_method=previous_response_id`)。
- brief 12本(B3 V0 b1-b4 x meta/hormuz/space_weapons)固定、各2反復=48本(smoke 2本を含む)。両群を同一driverで交互投入、4並列、再実行0、メモリ降格0、Checker ON。
- 重要な注意: out_dirは `runs/<slug>/control/b<i>__<arm>__r<j>`(DEV runnerのガードが`/control/`を要求するため委任文の規約から変更)。既存cost.json(`compute_stage_cost_breakdown`)はgpt-6-lunaがpricing表に無く0円計上になったため、費用は`raw_usage_log`から$/1M(5.6=0.20/0.02/1.20、6=0.10/0.01/0.50、USD/JPY=160)で再計算。

## 1. T-A(生成側、fresh 48本)

### 1-1. STOP・完走(記事が成立した本数)
| 指標 | baseline | all6 |
|---|---|---|
| 完走(Checkerまで) | 19/24 | 19/24 |
| Writer内部Gate STOP(JA_FACT_CHECK_STOP) | 2 | 2 |
| Writer内部Gate STOP(JA_RECHECK_REQUIRED) | 1 | 1 |
| Writer内部Gate STOP(EN Advanced deviation) | 0 | 2 |
| `--budget-jpy 12`のBUDGET_GUARD停止 | 2(¥14.08、¥12.98) | 0 |
STOP合計は5対5。Gate由来のSTOPは baseline 3 対 all6 5。baselineのBUDGET_GUARD 2本は本Trialの`--budget-jpy 12`設定による停止で、内容起因のGateではない(完走集合の評価は完走19本対19本)。

### 1-2. 盲検評価(完走19対19、LLMジャッジ単独・人間確認なし)
| 区分 | 指標 | baseline | all6 | 差 | 比 |
|---|---|---|---|---|---|
| JA R2 | 重大 件数 | 0 | 1 | +1 | - |
| JA R2 | 軽微 件数(/記事) | 10(0.53) | 7(0.37) | -3 | 0.70 |
| EN | 重大 件数 | 1 | 1 | 0 | 1.00 |
| EN | 軽微 件数(/記事) | 14(0.74) | 12(0.63) | -2 | 0.86 |
| R0(修正前JA) | 重大/軽微 | 0/11 | 1/12 | +1/+1 | - / 1.09 |
| 全体 | 保留/記事 | 0.05 | 0.26 | +0.21 | 5.0 |
| JA R2 | 軽微を1件以上含む記事 | 9/19 | 5/19 | | |
| EN | 軽微を1件以上含む記事 | 11/19 | 9/19 | | |
重大は全体で2件(baseline EN 1=MUSE-HC-012「callers」、all6 JA R2+EN 1=MUSE-HC-005 電話機能の範囲)。件数が小さく、差と比のみ示し有意性は主張しない。

### 1-3. R0->R2初出(増幅)・NG型
- R2で初出(R0に無い): baseline 4(重大0/軽微4)、all6 5(重大1/軽微4)。ENで初出: baseline 5(重大1/軽微4)、all6 6(重大0/軽微6)。R0にありR2で解消: baseline 5、all6 10。
- NG型(JA R2+EN存在、軽微): baseline subject1・scope2・time2・negation1・causal1・added_fact7 / all6 subject3・scope6・added_fact4(time/negation/causal 0)。重大: baseline object1 / all6 scope1。
- テーマ別(JA R2+EN、重大/軽微): meta 1/6対1/4、hormuz 0/2対0/3、space_weapons 0/6対0/6。
- 評価者別(重大/記事,軽微/記事,保留/記事、評価者とarmの割当は各評価者に両群同数): 評価者gpt-5.6-luna: baseline 0.00,0.90,0.00(n=10)/ all6 0.10,1.00,0.40(n=10)。評価者gpt-6-luna: baseline 0.11,0.56,0.11(n=9)/ all6 0.00,0.33,0.11(n=9)。評価者による差が群間差より大きく、群間の方向も評価者で割れる(5.6評価者は同等〜やや悪化、6評価者は改善)。

### 1-4. 副指標(完走19本平均/全24本)
| 指標 | baseline | all6 |
|---|---|---|
| JA Fact Check must-fix発動(original+R2判定単位) | 12/44 | 12/44 |
| JA Fact Check 最終status非COMPLIANT(完走分) | 0/44 | 0/44 |
| EN Advanced deviation must-fix再生成発動(完走分) | 0/19 | 6/19 |
| Checker stage1候補数/本 | 8.26 | 5.95 |
| Checker call数/本 | 8.95 | 7.47 |
| Checker final_state | STAGE2_DOWNGRADE 12 / REWRITE_THEN_DOWNGRADE 7 | STAGE2_DOWNGRADE 17 / REWRITE_THEN_DOWNGRADE 2 |
| 費用/本(完走、Writer系+Checker) | ¥9.46 | ¥4.29(約0.45倍) |
| 所要時間/本(完走、秒) | 491 | 341 |
| 費用合計(全24本) | ¥222.5 | ¥93.8 |

## 2. T-B(検出側、frozen 既知NG再判定、n=2)
入力=既知NGを含む固定記事+全台帳を`vfl01.run_deviation_check`(同一prompt/schema)へ。重大は解決できた**7件**(委任文の8件のうちai-p2r2-07は最終記事に残らず入力不能で除外。89wfはsw-p2r2-01/02と同事象)。軽微は型別4件ずつ16件(比喩は該当なし)。検出=NG文とのbigram重なり>=0.4の逸脱がMAJOR(重大)/MAJORまたはMINOR(軽微)。
| 指標 | gpt-5.6-luna | gpt-6-luna |
|---|---|---|
| 重大7件の検出(NG文に対応するMAJOR、試行単位 n=14) | 1/14(7%) | 4/14(29%) |
| 同、反復別 r1 / r2 | 1/7 / 0/7 | 2/7 / 2/7 |
| 軽微16件の検出(MAJORまたはMINOR、n=32) | 3/32(9%) | 4/32(12%) |
| 軽微16件のうちMAJOR判定 | 2/32 | 4/32 |
| (別指標)重大記事の記事内にMAJORが1件でもある | 4/14(29%) | 9/14(64%) |
| (別指標)軽微記事の記事内にMAJORが1件でもある | 4/32(12%) | 16/32(50%) |
| 同一rep比較でより重く/軽く/同じ(6が基準) | 重く5 / 軽く0 / 同じ41 | |
| NG文に対応しないMAJOR逸脱の延べ数(未検証、偽陽性含む) | 10 | 32 |
item別内訳は`T-B/TB_SUMMARY.md`。両モデルとも0/2の重大: PAST-meta-p2r2-02、PAST-ai-p2r1-01、PAST-sw-p2r2-02、PAST-hormuz-T0M0r2-01、PAST-jb9k-03(hormuz-T0M0・sw-p2r2-02は記事内に別のMAJORはあるがNG文に対応せず)。検出差は2件のみ: PAST-ai-p2r1-02(EN主体入替)は5.6が0/2・6が2/2、PAST-sw-p2r2-01は5.6が1/2・6が2/2。

## 3. 悪化した項目(all6で増えた/悪化した)
- 重大: JA R2の重大 0->1(全体では2件のみ、JA R2+EN合算 baseline 1 対 all6 2)。R2で初出した重大 0->1。
- Writer内部Gate STOP: 3->5(特にEN Advanced deviation STOP 0->2)。EN Advanced deviation must-fix再生成 0/19->6/19(T-Bと同方向: 6-lunaはFact Checkで重め判定、MAJOR逸脱が多い)。
- 保留/記事 0.05->0.26。軽微のNG型で scope 2->6、subject 1->3(増加)。ENで初出した軽微 4->6。R0の軽微 11->12。
- 悪化なし側: 軽微/記事(JA 0.53->0.37、EN 0.74->0.63)、Checker候補/call、費用(約0.45倍)、所要時間(約0.7倍)は減少。

## 4. 限界
- N: 完走19対19、重大は全体2件で床効果。差と比のみ。同一ジャッジ設計の評価者はgpt-5.6-luna/gpt-6-lunaのLLM単独判定(人間確認なし)で、評価者による差が群間差を上回る。ジャッジがgpt-6-lunaの場合の自己選好は排除できない(armは盲検)。
- STOPした10本(baseline 5/all6 5)は記事が成立せず評価対象外(生存者バイアス)。baselineのBUDGET_GUARD 2本は設定起因。
- T-B: 重大は7件(8件ではない)。検出判定は文字重なりの機械マッチで、偽陽性/偽陰性が混じる。EN由来の2件はEN本文+JA R2をsourceとして入力(production EN deviation check相当)。ai-p2r2-07は除外。
- Checkerは両群とも既にgpt-6-lunaのため、5.6->6の差は含まれない(両群同一)。Checker出力で書き換えられた後の最終ENは採点していない(`b1b/article.md`=Checker前ENを採点)。
- reasoning effortはhigh固定、ジャッジも同一。brief 12本のみ(3テーマ)。

## 5. 費用(再計算、参考換算はUSD/JPY=160)
- Phase 1 smoke(T-Aに含む)+Phase 3 T-A 48本: ¥316.3(baseline ¥222.5、all6 ¥93.8)。うち1 run最大 ¥13.4(baseline)。
- Phase 2 T-B 92判定: ¥31.4(5.6=¥22.7、6=¥8.8)。
- Phase 4 盲検評価38記事(+smoke判定2): ¥34.9(5.6=¥29.1、6=¥5.8)。
- 合計 ¥382.6 / ¥500。超過なし、暴走・再実行なし(driver再実行0、メモリ降格0)。

## 6. artifactパス
- `er052_output/all6_writer_redesign_necessity_01/`: PREREGISTRATION.md、MANIFEST.json(全48run)、runs/(48本+_logs)、T-B/(items.json、results/、TB_SUMMARY.md)、eval/(blind/、judgments/、SUMMARY_TA.md、HUMAN_CHECK_TA.md)、tools/、logs/。`eval/_private/MAP.json`はgit管理外(盲検)。
- コード: `er052_all6_writer_trial_01_run.py`、`er052_all6_writer_trial_01_tb_run.py`、`er052_all6_writer_trial_01_test_01.py`(5テストPASS)。
