# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_20(2026-09-30)

## 1. 委任内容(要旨)

Opus L2レビュー#4の是正W1〜W5+微小Trial rep11(広いTrialは含めない)。
Guardrail¥12。

## 2. Opus L2レビュー#4の要点(付録として逐語保存)

`docs/pm/opus_l2_review_open233_self_recovery_04.md`へ委任文の付録を
逐語保存した。最重要の新規発見: rep10 `hormuz_run03_standard` sample1
cycle2で、paired J-1の段落Rewriteが指摘されたJA文を一字も変えず、別
段落の無関係なJA文(+2.6%/$85の記述)を削除し、
`ja_recheck_overall_status: LEDGER_DEVIATION`・`ja_en_equivalence_
verdict: FAIL`だったにも関わらず`RESOLVED_REWRITE_THEN_DOWNGRADE`
(false PASS)として完了していた(「JA fail-open」)。

## 3. 実施内容(W1〜W3、¥0)

- **W1(JA fail-open封鎖)**: (i)未解消時の次cycle再構築へJA recheckの
  MAJOR deviationsを合流(`origin="ja_source"`明示)+`ja_pending_
  deviation`フラグによるSTAGE4安全網(`stage4_reason=
  "ja_deviation_unresolved"`)新設、(ii)`ja_en_equivalence_verdict`を
  測定専用からgating化、(iii)¥0決定論JAガード`ja_fail_open_guard`
  (新設関数)。新設ヘルパー`extract_quoted_fragment_present_in`は
  既存`extract_quoted_fragment`(最長一致)の既知の曖昧性(rewrite_hint
  中の「置換後の文」を誤って返す、rep10実データで実際に発生)をJA本文
  [Rewrite前]への実在確認で回避する。
- **W2(Stage1同一fact_id列挙)**: `stage1_fresh_with_enumeration`
  (新設)・`run_recheck`(拡張)の出力schemaへ`same_fact_id_locations`
  を追加(追加callなし)、`expand_same_fact_id_locations`(¥0・決定論)
  で独立deviationへ展開。er051(共有モジュール)は変更せず本runner内の
  ローカル拡張のみで実装。reuse fixtureは安全側fallback。
- **W3(全文Recheck条件更新)**: (c)を「paired かつ(ladder≥④ or JA
  ガード不通過)」へ縮小(`full_recheck_required`に`ja_guard_ok`/
  `ja_equivalence_verdict`引数追加)、(g)`section_type`がtitle/hook/
  in_one_lineの場合、(h)equivalence非PASSの場合を新設。(b)は実証例
  なしと明記のうえ保守側で維持、(e)にTrial限定の但し書きを追加。
- CLI拡張: `--instance_ids`(comma-separated allowlist)・
  `--force_fresh_stage1`(comma-separated instance_id、stage1_modeを
  fresh上書き)を新設(既定None、既存呼び出しの挙動は変えない)。
- OUT_DIR_REP11/BUDGET_STATE_PATH(`budget_state_c233x_20.json`)を
  新規定義(既存rep9/rep10のパスとは独立、委任_19の事故の再発防止)。

## 4. unittest(¥0)

新規16件(`TestJaFailOpenGuard`4件[rep10実データfixture含む]・
`TestExpandSameFactIdLocations`4件・`TestJaPendingDeviationSafetyNet`
1件・`TestFullRecheckRequired`系の更新[既存1件を置換+新規6件])+
既存180件=**計196件全PASS**(`.venv/Scripts/python.exe -m unittest
er052_open233_self_recovery_flow_runner_01_test_01`、regressionなし)。

## 5. rep11実測(代表4 instance×n=2、¥8.0288)

`hormuz_run03_standard`(`--force_fresh_stage1`でStage1新規実行)・
`bgroup_B3`・`meta_run03_standard`・`neg1_meta_b3prod_a2`をn=2実行
(OUT_DIR=`er052_output/open233_self_recovery_flow_runner_01_rep11`、
TOTAL_BUDGET_JPY=12.0)。**8/8 instance-run完走・API error 0件・
false PASS 0/8**。

主要な実測結果(詳細REPORT§20-2):
- `meta_run03_standard` sample1で、W1(i)の主機構(merge+pending flag)
  がrep10型欠陥パターンを実際に防止することを確認(cycle2で
  `ja_recheck_overall_status=LEDGER_DEVIATION`を主経路が直接検出、
  cycle3で`ja_pending_deviation=True`により正しく`STAGE4_ESCALATION`
  [`ja_deviation_unresolved`]へ到達)。
- `bgroup_B3`(2/2)で`ja_fail_open_guard`が発火し全文Recheckへ強制
  フォールバック。ただし当該fixtureの`source_article_text`が実際には
  英語であるため句点分割(`split_ja_sentences`)が機能せず「1文丸ごと
  消失」という粗い発火だったことを正直に報告する(安全側だが診断精度
  の粗い既知の限界)。
- `hormuz_run03_standard`のforce fresh Stage1(gpt-6-luna+W2enumeration
  instruction)はdeviationを1件も検出せず(`ACCEPTABLE_STAGE1`、
  recall miss)、W2の「headline/one-line surface」検証はrep11実runでは
  不成立(機構自体はunittestで別途確認済み)。
- 局所QA fastpathは2/8(`meta_run03_standard`cycle1)で`full_recheck_
  required=False`に到達したが、`find_sentence_context`の既存locate
  バグ(`revised_sentence_not_locatable_in_context`、委任_19の
  SequenceMatcher fallbackでも解消せず)により局所QA自体のAPI call
  に到達できずskip、全文Recheckへ正しくフォールバックした(fastpath
  実call成功は今回も0件)。
- 全体Rewrite(⑥)は0件を維持。
- `neg1_meta_b3prod_a2`(負例群)で2/2 sampleともRewriteが発生した
  (新規claim「MUSE-HC-006」、hook区分、既知の解消済みclaim[「Ring,
  ring」]とは別)。原因分析は次回委任の課題として持ち越す。

## 6. W5(記録是正、¥0)

- neg3両建て集計(Opus L2レビュー#4 Q2): iter6込み4/9=44.4%、
  disputed除外[分子・分母とも]3/8=37.5%、分子のみ除外3/9=33.3%。
  決定はしない(Fable/ユーザー判断)。
- `safety_A2A3`のrep10 `RESOLVED_REWRITE_THEN_DOWNGRADE`(2/2)経路を
  既存json読み取りで確認(¥0): floor経由BLOCKING 1件+裁量的QUALITY
  2件がRewrite後に解消、`safety_fixture`条件による全文Recheck維持を
  確認、fail-open型の懸念には該当せず。
- 設計書§4-16(§4-18指定だが実採番§4-15の次として§4-16、§4-15の前例
  踏襲)・§6-7(W1)・§6-8(W2)・§6-9(W3)を新設。REPORT§20を追加
  (§0対応表/§20-1実装/§20-2 rep11実測/§20-3全体Rewrite/§20-4不要
  Rewrite・人間確認残存/§20-5コスト/§20-6 Gate 9項目/§20-7 STOP条件・
  Status)。DECISION_LOG・OPEN_ITEMS・ACTIVE_TASK更新。

## 7. Gate 9項目充足表(Opus L2レビュー#4判定からの変化)

充足3/部分4/未充足2(Opus#4時点)→**充足5/部分3/未充足0**(rep11後)。
最重要だった項目7(Safety誤通過なし)が解消(false PASS 0/8実測)。
項目1(局所QA基本形)は引き続き未達(fastpath発火はしたが実call成功
0件、既存locateバグが主因)。詳細REPORT§20-6。

## 8. 費用

実装W1〜W3: ¥0(追加API callなし)。rep11: **¥8.0288**(8 instance-run、
Guardrail¥12内)。本委任合計: **¥8.0288**。Phase累計(前回まで
¥330.499)+本委任¥8.0288=**¥338.5278**。Phase残額(**上限¥500**の
うち)=**¥161.4722**。

## 9. STOP条件・USER_DECISION_REQUIRED該当確認

¥12超え見込み(該当せず、¥8.0288)/API error 3連続(該当せず、0 error)/
Production・既存証跡変更(該当せず、`git diff --stat`で確認)/
USER_DECISION_REQUIRED6条件(該当せず)/開始前チェック未反映(0件)/
最小修正1回後もFAIL(該当なし、rep11は1回で8/8完走)/Safety-critical
10claim・Safety 12がBLOCKINGでなくなった(該当せず)/false PASS
(JA逸脱残存でRESOLVED)がrep11で1件でも発生(**該当せず、0/8**)。

## 10. Status

`W1_W3_IMPLEMENTED_REP11_8_OF_8_COMPLETE_FALSE_PASS_ZERO`。
