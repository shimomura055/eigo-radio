# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_24(2026-10-01)

## 1. 委任内容(要旨)

`hormuz_run03_standard` real_run Escalationの第三要因(ラダー未昇段の
まま§3-3安全網が先に発火)の是正+少数確認rep15。Phase 2は含めない。
本委任Guardrail¥8(実装¥0、rep15≤¥7)。

## 2. 背景

委任_23のrep14実測で、真因A・B是正後も`hormuz_run03_standard`が2/2
STAGE4_ESCALATIONのまま残り、理由が`same_claim_fact_id_reblocked`
(「Stage3 Rewrite品質の限界という第三の要因」)へ変化したと報告されて
いた。

## 3. 真因の再特定(コード上の判定順序)

`run_instance`のメインループはcycle>1で、(i)`matched_records`判定
(§3-3安全網、fact_id一致+claim本文近似一致で「同一claim再発」を検出
したら直ちにSTAGE4)と、(ii)`repeat_fact_ids_for_recheck`判定(§6-6
A-2、fact_id再出現時に`escalate_to_paragraph=True`を立てて④段落水準
から試す)を順に評価する。是正前は(i)が(ii)より先にreturnする構造
だったため、①水準Rewrite後にcycle2の全文Recheckが同一claimを近似
一致で再検出した時点で、④段落水準のRewriteが一度も試行されないまま
STAGE4へ強制到達していた。これはRewrite品質の限界ではなく、ラダーが
実際には一度も昇段していなかったことが真因だった。

## 4. 是正(¥0)

`prior_blocking_records`の各エントリへ、そのRewrite試行時点で
`escalate_to_paragraph`が立っていたかを`escalated_to_paragraph`として
保存するよう拡張した。cycle>1の`matched_records`判定を二分岐させた:
(a) 既に④段落水準まで試行済みで再発(`exhausted_matched_records`)の
場合のみ、従来どおり直ちに`stage4_reason="same_claim_fact_id_
reblocked"`。(b) まだ①・③水準までしか試していない再発
(`escalatable_matched_records`)の場合は、STAGE4にせず該当claimへ
`escalate_to_paragraph=True`を明示的に付与してループを継続する(既存
の§6-6 A-2機構へ合流、新しい機構は作らない)。`find_matching_prior_
record`は直近cycleの一致レコードを優先するよう`reversed(prior_
records)`走査へ変更した。cycle上限・JA fail-open封鎖・等価FAIL
gating・Safety floor-strictは無変更。

**設計判断の開示**: 委任文は「次のラダー段(②→③→④)へ」と表現して
いたが、②はコード上の独立水準として存在せず(§5-7で既に①へ統合済み)、
既存の§6-6 A-2機構は①・③を両方スキップして④へ直接進む設計(rep10実測
で解消実績あり)である。本委任は新しい「1段ずつ昇段する」機構を新設せず、
既存のこの直接④ジャンプ機構へ合流させる最小変更を選んだ(委任文の字面
とは完全には一致しないため明示的に報告する)。また委任文が言及した
「局所QA判定後に全文Recheckが同一claimを再検出した場合の『前後2文で
再判定1回』ルール(委任_19 §6-6)」は、design書§6-6を確認した限り
verbatimでは存在しない(該当する既存機構は局所QA fastpathの±1文window
[§4-14]のみ)。新しい機構を勝手に発明することは避け、本節でFable/
ユーザーへ差異を報告するに留めた(実装していない)。

## 5. unittest(¥0)

`TestFindMatchingPriorRecord.test_multiple_prior_records_same_fact_id_
returns_most_recent`(新規1件)、`TestSameClaimReblockedLadderEscalation
Wiring`(新規3件、source inspection)。既存218件+新規4件=**計222件全
PASS**(`.venv/Scripts/python.exe -m unittest er052_open233_self_
recovery_flow_runner_01_test_01`実行確認)。

## 6. rep15実測(¥7.1025、Guardrail¥7)

`OUT_DIR_REP15`、`BUDGET_STATE_PATH`をrep15専用(`budget_state_c233ab_
24_rep15.json`)。CLI: `--groups=hormuz --instance_ids=hormuz_run03_
standard --n_runs=2`。

**sample1(¥4.0578、19 call)**: `final_state=STAGE4_ESCALATION`・
`stage4_reason=ja_deviation_unresolved`(rep14の`same_claim_fact_id_
reblocked`から変化)。cycle1で①水準+③水準の2claimをRewrite、cycle2で
残るclaimが`escalate_to_paragraph`により④段落水準でRewriteされ、EN/JA
Ledger Recheckとも「解消」を確認した(premature reblockが解消したこと
の直接実証)。cycle2で`ja_en_equivalence_verdict=FAIL`(委任_23で意図的
に無変更のまま維持したhard gate)が記録され、`ja_pending_deviation`が
持ち越されてcycle3で`ja_deviation_unresolved`によりSTAGE4_ESCALATIONへ
至った(false PASSではない、別の既存fail-closed機構が正しく発火)。

**sample2(未完走)**: 累計¥7.103がrep15 Guardrail¥7.0へ到達し、既存の
TrialAbort機構が正しく発火した。結果は未保存(既存仕様どおり)。

**`bgroup_B4`×1・`safety_A2A3`×1(未実施)**: rep15のGuardrailを
`hormuz_run03_standard`n=2だけで使い切ったため実行不能だった。sample1
のコスト(¥4.0578、19 call)はrep14の同fixture(¥1.87〜1.98、9 call)の
約2.1倍であり、是正が意図どおり追加cycleを許した結果(バグではない)だが、
同種パターンを持つ他instanceでも同程度のコスト増が見込まれることを
Fable/ユーザーへ開示する。

## 7. Phase 2候補(Production相当記事)一覧 — 正直な報告

OPEN-233全fixture(Safety群12・B群4・Hormuz・Meta)の`source_path`を
遡った結果、独立した実在記事テーマは「hormuz」(ホルムズ海峡・原油価格)
「meta」(Meta AI機能テスト)の2件のみで、Safety群・B群の全fixtureも
この2テーマの別pipeline段階・別trial変種からの抽出だった。真に独立した
既存記事runは6件(`hormuz_run01_advanced`/`hormuz_run02_advanced`/
`hormuz_run03_advanced`/`hormuz_run03_standard`/`meta_run03_advanced`/
`meta_run03_standard`)であり、**10本には届かない**(詳細REPORT§24-4)。
新規テーマは作っておらず、Phase 2の10記事規模検証には新規テーマ選定
(PM_GOVERNANCE§13、ユーザー判断)または既存run再利用方針の決定が必要
であることをFable/ユーザーへ報告する。

## 8. 費用

実装¥0+rep15¥7.1025=本委任合計**¥7.1025**/Guardrail¥8、残
**¥0.8975**。Phase累計¥386.113+¥7.1025=**¥393.2155**/総枠¥500、残
**¥106.7845**。

## 9. STOP条件・USER_DECISION_REQUIRED該当確認

¥8超え見込み(該当せず、実測¥7.1025。ただし`bgroup_B4`/`safety_A2A3`
追加実行はリスクが高いため見送った)/API error 3連続(該当せず、rep15
通算0 error)/Production・既存証跡変更(該当せず、`git diff --stat`で
er052本体2ファイル[flow_runner+test]・新規rep15出力・REPORT/design書/
DECISION_LOG/OPEN_ITEMS/delegation_logのみ、Production・既存iteration
1〜7/rep7〜14証跡は無変更)/6条件該当(非該当)/開始前チェック未反映
(0件)/最小修正1回後もFAIL(該当せず、本委任の是正自体はrep15で意図
どおり機能した)/Safety-critical/Safety 12がBLOCKINGでなくなった
(該当せず)/false PASS 1件以上(該当せず、0/1)。

USER_DECISION_REQUIRED 6条件該当有無: 非該当。判断材料は本文§7参照。

## 10. Status

`LADDER_ESCALATION_ORDER_FIXED_VALIDATED_HORMUZ_NO_LONGER_PREMATURE_
REBLOCK_BUT_SEPARATE_EQUIVALENCE_GATE_ESCALATES_COST_INCREASED_B4_
A2A3_UNTESTED_BUDGET_EXHAUSTED`。
