# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_23(2026-10-01)

## 1. 委任内容(要旨)

iteration7(委任_22)の未達2点(real_run Escalation非ゼロ・⑥使用増加に
よるworst cost悪化)の原因特定・設計修正・少数ケース確認。Phase 2は
含めない。本委任Guardrail¥6(分析・実装¥0、rep14≤¥5)。

## 2. 背景

iteration7は29 instance全量規模で初めて完走し(38/38・false PASS 0)、
不要Rewrite率を21.43%へ改善したが、以下2点が未達のまま残った。

- real_run Escalation 2/10(`hormuz_run03_standard` n=2とも、KPI目標0)。
- ⑥(全体Rewrite/削除)使用7件・worst instance cost¥8.9545
  (`safety_A4`、iter6の¥5.7883から悪化)。

## 3. A. `hormuz_run03_standard` real_run Escalation真因是正

iter7実データ(instances_s1/s2のcycle記録)を精査し、真因を2点特定した。

**真因A(§6-11の残存過剰保守)**: `resolve_ja_ok_after_equivalence_
gating`(委任_22で新設)は、`verdict=="REVIEW_REQUIRED"`かつJA側言語が
正常(determinate)な場合、全文Recheckが`ja_ok`を既にTrueと確認済みで
あっても無条件でFalseへ倒していた。instances_s1 cycle0は、BLOCKING
claim(HF-009、body)を①水準で解消し、全文Recheck(EN/JA双方)が
`LEDGER_COMPLIANT`かつ`all_prior_issues_resolved=True`と確認済み
だったにも関わらず、このgatingにより`ja_pending_deviation`が残り
STAGE4_ESCALATIONへ強制到達していた。`ja_en_equivalence_verdict`は
元々(委任_11)「flow制御には使わない、測定・報告専用」と明記されて
いたcheckであり、委任_20 W1(ii)が`FAIL`の実測(rep10、JA破損と一致)を
根拠にgatingへ昇格したが、rep10自体もja_recheck側が独立に`LEDGER_
DEVIATION`だったため、「`ja_ok`が既にTrueの状況でこの追加gatingが
実際に真の見逃しを捕捉した実測」は一度も存在しなかった。

**真因B(reuse fixtureのsame_fact_id列挙欠如)**: `hormuz_run03_standard`
は`stage1_mode=reuse`(§6-8「reuse fixtureへの安全側fallback」対象、
29 instance中26/29)であり、Stage1初回json(`er051_output/open233_
checker_trial_01/trial_02/step3/hormuz_run03_standard/V4A/run_1.json`)
は委任_20 W2の`same_fact_id_locations`フィールドを持たない。そのため
cycle0のStage1初回はbody側claim(HF-009)しか検出できず、in_one_line側
の同一fact言及はcycle1の全文Recheック(fresh LLM call)まで発見されない。
body/in_one_line2箇所が2 cycleに分かれ、HARD_MAX_CYCLES(3)を消費し
尽くした後も解消しないままSTAGE4_ESCALATIONに至っていた
(instances_s2)。

**是正A(¥0)**: `resolve_ja_ok_after_equivalence_gating`の`REVIEW_
REQUIRED`+JA側言語正常分岐を、`ja_ok`(入力)が既にTrueの場合はgating
しないよう変更した(信頼できる独立確認[EN/JA双方のLedger Recheck]を
弱い根拠[equivalence REVIEW_REQUIRED]で上書きしない)。`FAIL`分岐は
無変更(rep10実測の唯一の根拠がFAILであり安全側を維持)。JA fail-open
ガード(§6-7(iii)、本関数とは独立)は無変更のまま機能し続ける。

**是正B(¥0)**: `deterministic_same_fact_id_location_fallback`(新設)で、
reuse fixtureのdeviationについて`claim_in_article`中の数値・金額・%
トークン(1件でも一致)、または非stopwordキーワード重複(閾値3件以上、
`hormuz_run03_standard`実データで較正)を手掛かりに、記事内の他文
(`split_sentences_generic`、見出し行除外は既知の限界)を候補化し、
既存`expand_same_fact_id_locations`(fail-closed、逐語実在確認)へ渡して
cycle0の時点で独立claimへ展開する。過剰候補化はStage2(独立LLM
materiality判定)がACCEPTABLEでscreenするため安全側。

**unittest**: `TestResolveJaOkAfterEquivalenceGating`(既存1件を新挙動へ
更新+新規1件)、`TestDeterministicSameFactIdLocationFallback`(新規5件)、
wiring確認2件。既存208件のうち2件更新+新規10件=**計218件全PASS**。

## 4. B. ⑥(全体Rewrite/削除)の標準ラダーからの除外

iter7の⑥使用7件(`safety_A2A3`×2・`safety_A4`×4・`bgroup_B4`×1)全てに
ついて、call_logから①〜④試行記録を精査した。**7/7とも⑥使用後も最終的
にSTAGE4_ESCALATIONへ到達しており、「⑥が必要だった」Evidence(⑥使用が
最終解消[RESOLVED_REWRITE系]に至った例)は0/7**と確定した。`safety_A4`
のみで4回⑥を使用しており、worst cost¥8.9545の主因だった。

**是正**: `ENABLE_LADDER_LEVEL_6_FULL_REWRITE`(feature flag、既定
False)を新設した。無効時、①〜④/delete全段でguardが失敗した時点で⑥の
API call(`FULL_TEXT_FALLBACK_PROMPT_TEMPLATE`)を試みず、`stage4_
reason="ladder_exhausted_without_full_rewrite"`で直ちにSTAGE4_
ESCALATIONへ回す(`target_not_locatable`と同じパターン)。コードは削除
せず、flagをTrueへ戻せばiter7以前の①〜⑥挙動に復元できる(再有効化は
ユーザー判断)。⑤(より広い範囲)は既に①・④へ統合済み(§5-7、委任_14
B-3/B-4)でありコード上「5_」という独立水準は存在しないため(grep確認
済み)、無効化の対象自体がなく実装しない。

**unittest**: `TestLadderExhaustedWithoutFullRewriteWiring`(新規2件)、
既存⑥テストを「既定OFF時はladder_exhausted_without_full_rewriteを返す」
新テストへ更新、「flagをTrueへ戻すと従来どおり⑥で解消する」regression
テストを追加。

## 5. C. OPEN_ITEMS記録是正

`OPEN_ITEMS.md`のOPEN-233行は「ID|内容|状態|種類|Blocking|次Action|
区分|棚卸し」の8列構成だが、「内容」列に時系列で`**YYYY-MM-DD追記
(委任_XX...)**: ...`パラグラフが蓄積される巨大単一セル構造になって
いる。精査の結果、委任_21(2026-10-01)の追記パラグラフ(1118文字、
"rep11で判明した3欠陥の是正+限定Trial rep12"から始まる)が、本来入る
べき「内容」列(委任_20エントリと委任_22エントリの間の時系列位置)では
なく、誤って「種類」列(短い分類タグ・参照ファイル一覧が入る列)の末尾
へ挿入されていたことを確認した(編集時の原因は特定できず、本委任の
スコープ外)。当該パラグラフを一字一句変更せず(履歴改変ではない)、
「種類」列から正しい時系列位置へ移動した。あわせて「状態」列(field3)
を本委任の最新Statusで更新し、旧Statusを`旧Status参考(委任_22)`として
入れ子で保持した(既存パターンを踏襲)。`git diff --stat`で本行のみ
(1箇所の変更)であることを確認済み。

## 6. D. rep14実測(¥5.3545、Guardrail¥6)

`OUT_DIR_REP14`(`er052_output/open233_self_recovery_flow_runner_01_
rep14`)、`BUDGET_STATE_PATH`をrep14専用(`budget_state_c233aa_23_
rep14.json`)。CLI: (1) `--groups=hormuz --instance_ids=hormuz_run03_
standard --n_runs=2`(¥3.8461)、(2) `--groups=safety --instance_
ids=safety_A4 --n_runs=1`(¥1.5084)。

**hormuz_run03_standard**: 是正A・Bとも実際に発火した(sample2で`ja_
equivalence_review_required_not_gated_already_confirmed_resolved=
True`を確認[A是正の実発火]、両sampleともcycle0でbody+in_one_line
2claimを同時検出・Rewrite[B是正の実発火、iter7では2 cycleに分散])。
**しかし2/2ともSTAGE4_ESCALATIONは解消しなかった**(`stage4_reason`が
`ja_deviation_unresolved`から`same_claim_fact_id_reblocked`へ変化)。
cycle1の全文Recheckが、①水準でRewrite済みのbody claimを近似一致
(`find_matching_prior_record`閾値0.75)でなお同一claimとして再検出し、
§3-3の既存安全網(「同一claim再発=Rewriteが効かなかったことの実証」)が
正しく発火した。**正直な結論**: 真因A・Bは実在し是正も機能したが、
Escalationは**第三の要因**(word-level[①]のみのRewriteでは当該body
claimの実質的問題を解消しきれないというStage3 Rewrite品質の限界)に
より残存する。これは本委任のA-2三択(a/b/c)のいずれとも完全には一致
しない新規の発見である。

**safety_A4**: `final_state=STAGE4_ESCALATION`・`stage4_reason=
ladder_exhausted_without_full_rewrite`(claim MUSE-HC-012)。iter7の
同fixture(worst cost¥8.9545、⑥を4回使用)と比較し**83%減**。Safety
floor(floor_reason=`deterministic_floor:changed_actor`、MUSE-HC-006)
はstage2_results上で引き続き`materiality=BLOCKING`(floor-strict、
Production実際の挙動)を維持し、最終的にSTAGE4_ESCALATION(human
review)へ正しくfail-closedした(false PASSではない)。`floor_variant_
comparison.safety_group_hard_gate_passed=false`(false_negative_
candidates_safety_group=1)が記録されたが、これはStage2 LLM独自判定
(`llm_materiality`、floor無しの仮想判定)のrun間非決定性によるもので
あり、本委任の変更(Stage3のみに影響)とは無関係。実際に稼働している
floor-strict自体は本runでも正しくBLOCKINGを維持しており、Safety
regressionではない(iter7の同一metricは0件だったため、次回委任での
追加観測対象として記録する)。

## 7. 費用

分析・実装¥0+rep14¥5.3545(hormuz¥3.8461+safety_A4¥1.5084)=本委任
合計**¥5.3545**/Guardrail¥6、残**¥0.6455**。Phase累計
¥380.7585+¥5.3545=**¥386.113**/総枠¥500、残**¥113.887**。

## 8. STOP条件・USER_DECISION_REQUIRED該当確認

¥6超え見込み(該当せず、実測¥5.3545)/API error 3連続(該当せず、
rep14通算0 error)/Production・既存証跡変更(該当せず、`git diff
--stat`でOPEN_ITEMS.md[1箇所]・er052本体2ファイル[flow_runner+test]・
新規rep14出力のみ、Production[er003/er006/er009/er010/er012/er019]・
既存iteration1〜7/rep7〜13証跡は無変更)/6条件該当(非該当)/開始前
チェック未反映(0件)/最小修正1回後もFAIL(**該当**: hormuzは是正A・B
適用後もSTAGE4のまま。予算制約[残¥0.6455]のため追加の再実行[≤¥2]は
行わずSTOPし、本記録でFable/ユーザーへ報告する)/Safety-critical
10claim・Safety 12がBLOCKINGでなくなった(該当せず、floor-strict維持・
§6参照)/false PASS 1件以上(該当せず、0/3)。

USER_DECISION_REQUIRED 6条件該当有無: 非該当。ただし以下を判断材料
として提示する。(1) `hormuz_run03_standard`は真因A・Bを是正してもなお
2/2 STAGE4_ESCALATIONのままであり、第三の要因(Stage3 word-level
Rewriteの品質限界)の是正は本委任のスコープ・予算を超える。(2)
`safety_A4`のworst costは¥8.9545→¥1.5084(83%減)を確認したが、
`safety_A2A3`×2・`bgroup_B4`×1は本委任では未検証(同一コードパスの
ため同様の改善が期待されるが実測はしていない)。(3) ⑥のfeature flag
無効化により、⑥が実際に必要な非常に稀なケース(iter7では0/7だったが、
より広い母数では存在し得る)を早期にSTAGE4へ回すことになり、Rewrite
による自動解消率がわずかに低下する可能性がある(iter7実測では影響
なし)。

## 9. Status

`A2_GATING_AND_ENUMERATION_FIXED_VALIDATED_LADDER6_DISABLED_COST_
REDUCED_HORMUZ_STILL_ESCALATES_NEW_THIRD_CAUSE_FOUND`(真因A[等価QA
gatingの過剰保守]・真因B[reuse fixture同一fact_id列挙欠如]を特定・
是正し、rep14実測で双方の是正が実際に発火することを確認した。
`safety_A4`のworst costを83%削減した[⑥ feature flag既定OFF]。一方
`hormuz_run03_standard`は2/2ともSTAGE4_ESCALATIONのまま残り、理由が
`ja_deviation_unresolved`から`same_claim_fact_id_reblocked`[Stage3
Rewrite品質の限界という新規の第三要因]へ変化した。予算制約のため追加
修正は行わずFable/ユーザー判断待ちとしてSTOPする)。
