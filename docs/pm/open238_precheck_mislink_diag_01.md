# OPEN-238-PRECHECK-MISLINK-DIAG-01 診断(¥0・read-only・修正なし)

作成: 2026-10-07 / 対象run: `er052_output/open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep2/`
Checker結果json: `.../rep2/checker/runs/meta_run03_advanced.json`(instance_id=meta_run03_advanced。ファイル名はテンプレ流用で、中身はai_control rep2)

## 0. 結論(先に)
- 起票時の推測「fact_id紐付けずれ」は**不正確**。実際の原因は precheck の**数値抽出の偽陽性**: 文中の「a third party」の「a third」が、分数語辞書で**33.3%**として抽出され、Ledgerの他factの数値(EVID-006=84%、CONTROL-004=50%未満)と不一致扱いされ`number_mismatch`が発火した。**精査済み**(同一コードを再実行して再現確認)。
- 「紐付け」は文ごとではなく、**記事全体の抽出値集合 x 単一%を持つ全fact**の総当たりで決まる(文↔factの意味的対応付けは存在しない)。
- 発火後はStage 2(LLM判定)を**スキップして無条件BLOCKING化**(`precheck_floor_bypass`)され、Rewriteへ「fact_id=EVID-006のLedger値へ置換する」と指示された。これが84%文への置換を直接生んだ(**精査済み**)。

## 1. 事象トレース(cycle1、JSON逐語。パスは `cycles[0]`)
1. 対象文(unit S3.2): `The evaluation environment set up by a third party was not properly configured, so it might connect to the internet.`
2. Stage1(LLM, route r3): 同文を `related_fact_id=EVID-008`, `causal_not_in_fact` として検出(`stage2_results[5]`)。Stage2判定は `materiality=ACCEPTABLE`, `basis=none`(second_opinionもACCEPTABLE、`confirmed_downgrade=true`)= **意味的にはBLOCKINGにならなかった文**。
3. 同文に対しprecheckが別途2件発火(`stage2_results[13]`, `[14]`):
   - `[13]` `detected_by=precheck`, `related_fact_id=EVID-006`, issue=`precheck detected number_mismatch vs ledger_value=84% of rollouts (numeric_scope: Claude Opus 4 blackmail scenario ...)`, `precheck_locate_method=precheck_number_locate`, `materiality=BLOCKING`, `basis=precheck_floor`, `stage2_route=precheck_floor_bypass`, `floor_reason=precheck_floor`
   - `[14]` 同、`related_fact_id=CONTROL-004`, ledger_value=`Models described cheating as wrong less than 50% of the time ...`
   - いずれも `dev.changed_number=false`(floor flag経由ではなくprecheck経路。OPEN-235の`number_not_in_fact→changed_number`未変換とは無関係な経路)。
4. `build_precheck_floor_claims`は「Stage1が既に同じrelated_fact_idを出していればprecheck claimを追加しない」(L8165)。Stage1はEVID-008を出していたがEVID-006/CONTROL-004は出していなかったため、precheck claimが追加された。
5. rewrite_hint(`stage2_results[13]`): `'The evaluation environment set up by a third party was not p' を、fact_id=EVID-006のLedger値へ置換する。issue: precheck detected number_mismatch vs ledger_value=84% of rollouts ...`(日本語部分はjson内で文字化け表示、コードL8785-8786で確認)。
6. Rewrite(`rewrite_records[1]`, `claim_identity=fact:EVID-006`, `rewrite_kind=replace_with_ledger_value`): L1(word_connective)=declined、L3(sentence)で
   before=`The evaluation environment set up by a third party was not properly configured, so it might connect to the internet.`
   after=`In a simulated safety evaluation, Claude Opus 4 attempted blackmail in 84% of rollouts.`(actor_guard ag1_strict ok)
7. `[14]`(CONTROL-004)は `covered_by_earlier_rewrite_in_cycle`(`rewrite_records[2]`)でスキップ。
8. cycle2: 置換後の84%文がStage1でEVID-006/CONTROL-004としてBLOCKING(`basis=unsupported_relationship`)→ `rewrite_records[0]`が4_paragraphで当該文を含む段落から削除。`final_state=RESOLVED_REWRITE_THEN_DOWNGRADE`。元のEVID-008内容(第三者評価環境の誤設定)は最終ENから欠落。

## 2. 原因と決定箇所
| 処理 | 場所 | 内容 | 確度 |
|---|---|---|---|
| 分数語辞書 | `er052_open233_self_recovery_precheck_01.py` L108-115("a third": 33.3はL112) | 「a third」を33.3%と見なす | 精査済み |
| 抽出 | 同 L149-156 `extract_percentages` | `\ba third\b`に一致すれば無条件に33.3を追加。後続語(party/of)を見ない | 精査済み |
| mismatch判定 | 同 L216-285 `check_number_mismatch` | factが単一%(EVID-006=84、CONTROL-004=50)かつ記事側観測値{33.3}が近似・自然丸め・他fact値のどれにも当たらないとnumber_mismatch。**文とfactの意味的対応は見ない** | 精査済み |
| 文の特定 | runner L8086-8095 `resolve_precheck_target_sentence` | foreign_values(33.3)を含む最初の文を採用 → 「third party」文 | 精査済み |
| claim化 | runner L8161-8190 `build_precheck_floor_claims`(L8165の重複除外のみ) | findingごとに1 claim(同文が2件) | 精査済み |
| BLOCKING化 | runner L8784-8800(hint L8785-8786、`precheck_floor_bypass`) | Stage 2を経由せず無条件BLOCKING、hintは「fact_id=Xのledger値へ置換する」固定文 | 精査済み |
| 承認構成 | runner L496-523(`PRECHECK_MODE: "number_only"` L504)、L8147-8158 `filter_precheck_findings` | number_mismatchのみ残す設計 → 本件は承認構成が設計どおり動いて発生 | 精査済み |

再現確認(read-only): 同ledgerと`cycles[0].en_text_before_rewrite`に`precheck.run_precheck`を実行 → `number_mismatch EVID-006 foreign_values=[33.3]`、`number_mismatch CONTROL-004 foreign_values=[33.3]`。`extract_percentages(本文)={33.3}`で、33.3を含む文は当該1文のみ。actor_missing等も発火するが`PRECHECK_MODE=number_only`で除外される。

## 3. 再現条件・他runでの件数
- er052_output配下のjson 1,795件を走査し、`detected_by=precheck`のnumber_mismatch claimは**4件(=本run 2ファイル x 2fact)のみ**。他runでは0件。
- b1b/article.md + research_ledgerを持つ18 run dirを同一precheckで再実行: 発火は本run(ai_control P2 rep2)のEVID-006/CONTROL-004の2件のみ。ai_control P2 rep1、従来版polysemy_trial_04 ai_control control/rep1、prod_e2e_02の9 run jsonに同型は**0件**(分数語を含むarticle.mdも本run以外に0件)。
- 発火条件: (a)記事に分数語(a third/half/a quarter/a fifth/a tenth/one third/two thirds/three quarters等)、(b)ledgerに「単一の%または単一のcount」のfactがある、(c)その分数相当値がどのledger fact値にも近似しない。「a third party」は第三者評価を扱うai_controlで出やすい語(EVID-008自体が"third-party evaluation environments")。
- 限界: 頻度の定量はこの範囲(1,795 json / 18 run dir)のみ。

## 4. 影響範囲
- 承認済み構成(`OPEN233_APPROVED_FLOW_SWITCHES`、未配線)が本番配線されれば、同じ`PRECHECK_MODE=number_only`・同じprecheckコードが使われるため、**同様の偽陽性は本番でも発生し得る**(発生には上記(a)(b)(c)が必要、実測では本件のみ)。
- 重さ: precheck floorはLLM判定をバイパスして無条件BLOCKING + 「Ledger値へ置換」指示。Stage2で明確にACCEPTABLEの文でも壊せる(本件)。
- OPEN-235(数字floor配線漏れ)とは**別経路**: 本件は`apply_floor`ではなくprecheck_floor_bypassで、`changed_number=false`のままBLOCKING。OPEN-235を是正しても本件は防げない。
- OPEN-236(two_of_two潜在)とは無関係(`STAGE2_NORMAL_TWO_OF_TWO=False`、precheck floorは2-of-2対象外)。ただし同文が2 factでclaim化され、fact:EVID-006のRewriteで他方が`covered_by_earlier_rewrite_in_cycle`扱いになる点は、claim_identity=fact:<id>系の脆さと近い領域。
- 残11 run再開: 本件はテーマ・文言依存の偽陽性で再開自体は妨げない。ただし第三者語や分数語を含む文が出るrunで再発し得る。Trial評価では、今回のai_control rep2の置換はWriter起因でなくChecker起因として区別して扱うべき。

## 5. 修正の選択肢(実装しない)
1. 語境界の限定: 「a third」「one third」等の分数語を、直後が`party/parties`の場合は抽出しない(または`of`が続く場合のみ採用)。変更箇所=precheck L112付近と`extract_percentages`。リスク=辞書の除外漏れ(別の同形語)。**Production仕様変更に該当**(precheck抽出仕様)。Opus条件C(Production採用前)レビュー推奨。
2. 算用数字・%を含まない文ではprecheck claimを作らない(分数語のみの文は対象外): `resolve_precheck_target_sentence`/L8161付近。リスク=分数語の本物の誤りを見逃す。**Production仕様変更に該当**。Opus条件Cレビュー推奨。
3. precheck floorもStage 2を通す、または`replace_with_ledger_value`の値置換指示を出さない形へ変更: runner L8784-8800。リスク=「数字は機械的に重大化」という承認済み設計の変更(最大)。**Production仕様変更に該当**。新しい処理フロー設計=Opus条件Aレビュー必須。
- 最小は案1。いずれも`APPROVED_FOR_PRODUCTION`済み仕様の変更になるため、人間ユーザー承認が前提。

## OPEN-238本文の訂正提案(報告のみ・SSOT未編集)
「fact_id紐付けずれ推測」を「precheck number_mismatchの分数語偽陽性(a third party→33.3%)+precheck_floor_bypassの無条件BLOCKING/置換指示」へ訂正することを推奨。

## Dangling Reference Check(2026-10-07実施)
- 引用ファイル: `er052_open233_self_recovery_precheck_01.py`、`er052_open233_self_recovery_flow_runner_01.py`、`OPEN_ITEMS.md`(L737 OPEN-235、L738 OPEN-236、L740 OPEN-238、L741 OPEN-239)、`er052_output/open233_allfact_note_e2e_02/ledger/ai_control/research_ledger/verified_fact_ledger.txt`、Checker json=存在確認済み。
- fact_id: EVID-006(ledger L31)、EVID-008(L47)、CONTROL-004(L99)をGrepで確認、引用文と一致。
- unit/index: json内`cycles[0].stage2_results[5]/[12]/[13]/[14]`、`rewrite_records[1]/[2]`、`cycles[1].stage2_results[0]/[1]`・`rewrite_records[0]`はPythonで内容読み出し確認済み。unit id `S3.2`は`stage1_coverage.unit_ids`の値。
- コード行(grep/sedで確認): precheck L108-115/L149-156/L216-285、runner L496-523(PRECHECK_MODE=L504)、L8086-8095、L8147-8158、L8161-8190(L8165)、L8737-8738、L8784-8800(hint L8785-8786)。
- 未確認/限界: Rewrite promptへのfact本文の渡し方(L6315付近のE2 prompt組立)は詳細未読。84%文になった直接要因は、hint(「fact_id=EVID-006のLedger値へ置換」)とhandoff記録に整合しており準精査(厳密な精査は未了)。
