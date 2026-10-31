# TRIAL_PLAN_05 KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01 委任_05(事前登録・有料実行前、2026-10-31)

原文=`docs/pm/delegation_log/2026-10-31_KP-N5-TRIAL-05_FINAL_KP_COMPARISON_USER.md`。目的=現行N5(cap7)とA案(E2網羅抽出+A10区間分散+cap10)について、学習者が実際に見る「N5一般化後のKey Phrase」を記事別に並べ、ユーザーが採否を判断できる状態にする。Production実装・正式採用なし(Trial、未承認、配線なし、新flagなし)。

## 1. 比較セル(Phase 1棚卸し、API 0。`tools/n5r_inv_05.py`→`ev05/inventory_05.json`)
Trialで実際に抽出・選定を回した記事×レベルは**5セル**(委任文想定の24セルは誤り): untidi_a2(X Std、E2 rep 11)・untidi_b1b(X Adv、13)・surname_b1b(Y Adv、2)・moon_b1b(X Adv、2)・melos_a2(Z Std、2)。全セルrep>=2のため**再現性用の追加抽出は不要**(追加抽出0)。ev01のprobe(ai_cha/melos/untidi 他レベル)はB1抽出のみで、E2+SEL+A10のプールが無いため対象外。

## 2. 比較の定義
- **現行N5 cap7**: 公開済みProduction出力(`er019_output/untidiness_family_resource__run_fx4_01`等、生成2026-10-27〜29)はN5配線(2026-10-30/31)前でN5一般形を含まないため比較に使えない。よって**Trial03のN5正式出力**(`KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/fixtures/n5_trial_replay_fixture_01.json` `cases.<case>.trial_items`、同一本文。N5配線時に記録応答replayでProductionと19ケースexact一致確認済み)を使用。参考としてN5配線後のProduction実run(M10、同一本文、3セル、ev02/ev03 m10)の phrase kind最終候補を併記。
- **A案cap10**: 各repのE2プール(`ev02/rep_*.json` pools.E2.judged、SELラベル保存済み)に `n5r_lib_02.pick_A10(judged, text, 10)` を再計算(決定論、API 0)。主表の代表repは「各repのcap10 span集合(重複判定=n5._contains/norm_key同一)の他repとのJaccard平均が最大のrep、同点は若いrep番号」。全repの出現頻度と入替も別表。
- **区分**: 同一セルで 共通=A案cap10の項目がsource_spanまたはdisplay_formが現行N5項目と一致/包含関係、追加=現行N5に無い、脱落=現行N5にあるがA案cap10に無い、QA脱落=A案cap10候補だがGEN5/VER5/CHK5/CMU/5語検査で落ちた(段と理由を記録)。
- **下流処理**: GEN5→VER5→CHK5(`er138.generalize_verify_check`、<=7件batch)+API 0検査(CMU・5語)。Prompt・モデル・閾値は正式採用済みのまま(gpt-6-luna / gemini-3.8-flash / gpt-6.1-sol=Production既定の最新系)。手作業の一般形は実測として使わない。対象外(限界): er119 canonicalization QA/人称整合/presentable filter/backfill(両方式とも未適用)。

## 3. GEN5対象集合・見積・Cap
- 対象=(A)全repのA10 cap10の和集合 + (B)現行B1方式A0 cap7の和集合(比較用) のうち、既存cache(`ev02/gen_cache_*`)・fixture trial_items・ev05 cacheに無いspan。実測 **67件・12 batch**(untidi_a2 19/3、untidi_b1b 16/3、surname_b1b 9/2、moon_b1b 13/2、melos_a2 10/2)。(X)N5外の学習価値評価用に、結果を見た後に選ぶ追加span<=14件(2〜3 batch)を予備枠とする。
- 1 batch費用の実測: ev02 gen(6件2.81円・7件2.63円・1件1.04円、記事全文入力のため件数に比例しない固定費が大きい)。見積=12 batch x 約2.7 + surname/moon長文補正 約2 = 約34円 + 予備枠約6円 = **約40円、Cap 52円(x1.3)、止め線47円**。本日累計(約521円)+Cap 52円=573円<1,000円、案件見積<300円=自律実行条件を満たす。
- 実行規則: 2プロセス(起動間隔>=150秒・300秒窓<=2)、cost logはev05/cost_log_<proc>.jsonl、STOP sentinelは`ev05/`、`stop_scope_check_01.py`を起動前に実行。途切れ/rc!=0が2回続いたら再起動せずSTOP。

## 4. 成果物
`COMPARISON_05.md`(冒頭に記事別比較表→学習価値比較→N5外表現→`put away`/`in the way`最終到達→再現性→限界)、`RESULT_PACKET_N5_05.md`、集計=`ev05/`、コード=`tools/n5r_*_05.py`。判定は行わずユーザー判断材料のみ(Status候補=USER_DECISION_REQUIRED継続)。
