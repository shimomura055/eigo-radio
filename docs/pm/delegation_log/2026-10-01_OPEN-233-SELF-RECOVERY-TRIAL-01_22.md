# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_22(2026-10-01)

## 1. 委任内容(要旨)

bgroup_B3の等価QA gating是正(¥0+再確認≤¥1)→ Gate 9項目確認 → 広い
Trial iteration 7(29 instance全量)。Phase 2は含めない。Guardrail¥48
(Part A≤¥1、Part B≤¥45)。

## 2. 背景(rep12で判明したKPI後退)

rep12(委任_21)実測で`bgroup_B3`が2/2 STAGE4_ESCALATIONへ回っていた。
調査の結果、fixtureの`source_article_text`(「JA」側)が実際には英語で
あり、JA↔EN等価チェック(`ja_en_equivalence_verdict`)自体が両者を比較
できず`REVIEW_REQUIRED`を返していた。委任_20 W1(ii)の「FAIL/
REVIEW_REQUIREDなら無条件でja_okをFalseへ倒す」gating方式は、実際の
全文Recheckが英語版・JA版とも`LEDGER_COMPLIANT`かつ全解消済みと判定
していたにも関わらずja_okを強制Falseへ倒し続け、次cycleで
blocking_count=0でも`ja_pending_deviation`が解消されず
`STAGE4_ESCALATION(ja_deviation_unresolved)`へ誤って強制到達させて
いた。

## 3. A-1是正(¥0)

`resolve_ja_ok_after_equivalence_gating`(新設、既存の巨大なインライン
処理を純粋関数として抽出)で、gating方式を整理した:

- `verdict=="FAIL"`(実際に不一致検出): 従来どおりja_okをFalseへ倒す。
- `verdict=="REVIEW_REQUIRED"`かつ`is_predominantly_ja`で判定したJA側
  言語がindeterminate(実際には非JA): ja_okを強制せず全文Recheckの
  実際の判定をそのまま使う(STAGE4直行を強制しない、`full_recheck_
  required`条件(h)により全文Recheck自体は既に維持されているため安全側
  は保たれる)。
- `verdict=="REVIEW_REQUIRED"`かつJA側言語が正常: 従来どおりgating
  する(理由を記録)。

unittest新規6件(`TestResolveJaOkAfterEquivalenceGating`、rep12
`bgroup_B3`実データ・rep10 hormuz実データを使用)+既存202件=計208件
全PASS(`.venv/Scripts/python.exe -m unittest
er052_open233_self_recovery_flow_runner_01_test_01`)。

## 4. A-2 rep13実測(¥0.9448、Guardrail¥1内)

`OUT_DIR_REP13`・`BUDGET_STATE_PATH`(`budget_state_c233z_22_repA.json`)
をrep13専用へ明示設定、`TOTAL_BUDGET_JPY=1.0`。CLI:
`--groups=b_group --instance_ids=bgroup_B3 --n_runs=2`を2回実行した
(Stage1はreuse fixture、fresh化しない)。

1回目(¥0.1766): Stage2非決定性でHF-007がQUALITYと判定され等価チェック
自体が発火せず、2/2 RESOLVED_STAGE2_DOWNGRADE。
2回目(¥0.7682): Stage2がHF-007をBLOCKINGと判定。2/2とも
`verdict=REVIEW_REQUIRED`・`lang_indeterminate=True`・`not_gated_
indeterminate_lang=True`となり、全文Recheck(EN/JA双方LEDGER_COMPLIANT)
の実際の判定がそのまま採用されRESOLVED_REWRITE(ladder_level_used=
1_word_connective、最小変更)で解消。

**4/4 instance-run全てSTAGE4に至らず**(rep12の2/2 STAGE4から改善)、
false PASSでもない(実Recheckが真に解消を確認した場合のみ通過)。

## 5. A-3 Gate 9項目充足表(Evidence列挙、判定はFableへ委ねる)

REPORT§22-3参照。9項目全てにEvidenceを記載し、1項目もEvidence欠落は
なかった(STOP非該当)。ただし項目2(⑥使用)・項目9(平均コスト)は、
後続の広いTrialで従来の小規模subset時点より悪化した数値が判明した。

## 6. Part B: 広いTrial iteration 7(29 instance全量、38 instance-run)

`OUT_DIR_ITER7`・`BUDGET_STATE_PATH`(`budget_state_c233z_22_repB.json`)
をPart B専用へ明示設定、`TOTAL_BUDGET_JPY=45.0`。非決定性が実測されて
いた9 instance(`safety_A2A3`/`bgroup_B3`/`meta_run03_standard`/
`meta_run03_advanced`/`hormuz_run03_standard`/`hormuz_run03_advanced`/
`neg1_meta_b3prod_a2`/`neg2_meta_refresh_a2`/`neg3_hormuz_prodrunner_
b1b`)はn=2(18 instance-run、¥21.4374)、残り20 instanceはn=1
(20 instance-run、¥18.1101)で実行した。Stage1は既存reuse fixtureを
使用(fresh化しない)。

**38/38 instance-run完走・API error 0件**。false PASS候補0件
(`escalation_zero_breakdown.silent_pass_candidate=0`)。Safety hard
gate通過(`false_negative_candidates_safety_group=0`)。

STAGE4到達7件(`ja_deviation_unresolved`6+`cycle_limit_exhausted_
after_recheck`1)全件について`ja_equivalence_lang_indeterminate`を
確認した結果、**全件`False`**(genuineなJA言語による正当なfail-closed、
またはEN側自体のLEDGER_DEVIATION)であり、A-1が対象とする「JA側言語が
実際には非JAで判定不能」パターンによる誤STAGE4は0件だった。

## 7. iteration7全測定と主な発見(詳細REPORT§22-5)

- 不要Rewrite率: iter6(sample1、44.44%)→iteration7 21.43%(3/14)へ
  **改善**。
- ⑥(全体Rewrite/削除)使用: iter6 1件→iteration7 **7件(18.4%)**へ
  **悪化**(`safety_A2A3`×2・`safety_A4`×4・`bgroup_B4`×1、いずれも
  最終的にSTAGE4で正しくfail-closed、false PASSではない)。全量規模で
  初めて判明した新たなtail risk。
- worst instance cost: iter6 ¥5.7883→iteration7 **¥8.9545**
  (`safety_A4`、7 rewrite operations・ladder⑥を4回試行し最終的に
  STAGE4)へ**悪化**。
- real_run Escalation率: iter6 16.67%(2/12)→iteration7 20.0%(2/10)、
  同一既知ハードケース(`hormuz_run03_standard`)起因、新規regressionで
  はない。
- `meta_run03_advanced`は今回もblocking_count=0でA-1機構の実run検証
  機会を得られなかった(未検証のまま)。

## 8. 読み比べページ更新

`user_test/open233_rewrite_compare_01/index.html`をiteration7の実測
結果で更新した(iter6版は`index_iter6.html`として保存、削除・移動せず)。
3 instance収録: `neg1_meta_b3prod_a2`(Meta hookの非Rewrite例)・
`bgroup_B3`(B3因果のA-1修正例)・`neg3_hormuz_prodrunner_b1b`
(Hormuz由来記事の局所Rewrite例、`hormuz_run03_standard`自身は今回
2/2 STAGE4[genuine]のため代替採用しページ内に明記)。生成スクリプト:
`er052_open233_self_recovery_rewrite_compare_page_iter7_01.py`
(API呼び出しなし、¥0)。

## 9. 費用

A-1実装¥0+rep13¥0.9448+iteration7¥39.5475=本委任合計**¥40.4923**
(Part A Guardrail¥1内・Part B Guardrail¥45内)。Phase累計
¥340.2662+¥40.4923=**¥380.7585**/総枠¥500、残**¥119.2415**。

## 10. STOP条件・USER_DECISION_REQUIRED該当確認

Part A ¥1超え見込み(該当せず)/Part B ¥45超え見込み(該当せず)/
API error 3連続(該当せず、0 error全体)/Production・既存証跡変更
(該当せず、`git diff --stat`で確認)/USER_DECISION_REQUIRED6条件
(該当せず、⑥使用増加・worst cost悪化・`safety_A4`既知ハードケース
残存・`meta_run03_advanced`未検証・不要Rewrite根本解消未達は判断材料
として提示)/開始前チェック未反映(0件)/最小修正1回後もFAIL(該当なし、
A-1・Part Bとも1回で完走)/Safety-critical 10claim・Safety 12が
BLOCKINGでなくなった(該当せず)/false PASS 1件以上(該当せず、0/38)。

## 11. Status

`A1_EQUIVALENCE_GATING_FIXED_REP13_4_OF_4_NO_STAGE4_ITER7_38_OF_38_
COMPLETE_FALSE_PASS_ZERO_WORST_COST_TAIL_RISK_INCREASED`(A-1でJA/EN
等価チェックgatingを整理し`bgroup_B3`のrep13実測4/4でSTAGE4を解消、
Gate 9項目は全項目Evidence記載完了[STOP非該当]。29 instance全量規模の
広いTrial iteration 7を初めて完走[38 instance-run・¥39.5475・error 0・
false PASS 0]し、不要Rewrite率の改善[44.44%→21.43%]を確認した一方、
⑥使用[0→7件]・worst instance cost[¥5.79→¥8.95]という新たなtail risk
が全量規模で初めて判明した。Gate判定[VALIDATED/REJECTED]・tail risk
対応の要否はFable/ユーザー判断待ち)。
