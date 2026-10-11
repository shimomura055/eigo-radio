# RESULT_01: JA記事品質 工程別モデル配置Trial(委任_03、Phase 2実行結果)

管理ID: FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01 委任_03 / 2026-10-11 / DEV/Trial専用(Production code・Prompt・Routing・CURRENT_SPEC不変、Research/Fact Ledger再実行なし、英訳・RF・TTS・Audioなし)
Status案: **MEASURED(N=1、A/C/D/E 4案)**。B案は**課金前STOP**(旧仕様を代替仕様へ変えず正確に再現できないため。選択肢は5節)。VALIDATED/採用の判断はユーザーBlind評価後。

## 1. 正式比較表(再掲)と費用(円=USD×160、実測は各案response.usageをpricing_snapshot単価で再計算)
| 案 | B3 | B3→R0入力 | R0 | R1 | R2 | 当初概算 | 今回見積 | 今回実測 | 状態 |
|---|---|---|---|---|---|---|---|---|---|
| A | Luna | 新仕様 | Luna | Astra | Astra | 約37 | 35.65(既存実測) | **35.64(既存再利用、新規0円)** | 既存複製 |
| B | Luna | 旧仕様 | Luna | Astra X | Astra X | 約37 | 約35(参考) | **未実行(0円)** | **課金前STOP**(5節) |
| C | Luna(A再利用) | 新仕様 | Astra | Luna | Luna | 約44 | 約32.13 | **37.40** | OK |
| D | Astra | 新仕様 | Luna | Luna | Luna | 約56 | 約41.22 | **50.17** | OK |
| E | Sol 6.1 | 新仕様 | Sol | Sol | Sol | 約54 | 約21.37 | **21.55** | OK |

新規課金合計 **JPY109.11**(C 37.40 + D 50.17 + E 21.55)/ 上限250 → 残140.89。案cap(C55/D75/E45)内。見積との差の主因: C=R0 Astraのreasoningが多い(出力4,289tok、見積3,567)、D=B3 Astraの出力が多い(5,368tok、見積4,254)。E=見積とほぼ一致。

### 工程別金額(円)
| stage | A(既存) | C | D | E |
|---|---|---|---|---|
| B3 | 0.406 | 0(Aの再利用) | 49.469 | 7.107 |
| R0 | 0.314 | 37.147 | 0.464 | 8.373 |
| R1 | 18.648 | 0.095 | 0.081 | 2.195 |
| R2 | 16.277 | 0.157 | 0.154 | 3.871 |
| 合計 | 35.644 | 37.399 | 50.168 | 21.545 |
(C合計にA側B3の0.406は含めない=新規発生なし。単独で配置コストを見るなら+0.41)

## 2. 各案の実行結果(actual model_id、token、秒。秒は3案を並列実行した値で参考)
| 案 | stage | 返却model_id | in | out(reasoning) | 秒 |
|---|---|---|---|---|---|
| C | R0 | gpt-6-astra | 1,772 | 4,289(3,624) | 70.3 |
| C | R1 | gpt-6-luna | 688 | 1,048(405) | 10.1 |
| C | R2 | gpt-6-luna | 682 | 1,823(1,191) | 14.6 |
| D | B3 | gpt-6-astra | 4,078 | 5,368(3,071) | 88.2 |
| D | R0 | gpt-6-luna | 1,773 | 5,440(4,896) | 44.5 |
| D | R1 | gpt-6-luna | 563 | 903(255) | 9.6 |
| D | R2 | gpt-6-luna | 687 | 1,787(1,163) | 17.2 |
| E | B3 | gpt-6.1-sol | 4,078 | 3,626(1,034) | 56.7 |
| E | R0 | gpt-6.1-sol | 1,935 | 4,846(4,142) | 85.3 |
| E | R1 | gpt-6.1-sol | 719 | 1,228(516) | 22.8 |
| E | R2 | gpt-6.1-sol | 751 | 2,269(1,552) | 35.6 |
全案: 記号QA findings 0(R0再生成・R2再実行とも発火なし)、Provenance不一致なし、タグ残存なし、再試行なし、Production module 6本のsha実行前後一致。**互換性**: `gpt-6.1-sol`のmodels一覧存在(無料取得)、effort=high・B3 json_schema(strict)ともSolで受理、Astra B3 json_schemaも受理(最初の課金call自体で確認)。降格なし。
詳細: `runs/<案>/runtime_evidence.json`(call_records=stage別usage/prompt sha/入力sha/response_id)、`runs/<案>/usage.json`、`runs/<案>/cost_ledger_maq_01.jsonl`、`runs/<案>/raw_usage_log.jsonl`、`run_{C,D,E}.log`。

## 3. 各案R2(日本語、最終全文)
`runs/A/export/r2.md` / `runs/C/export/r2.md` / `runs/D/export/r2.md` / `runs/E/export/r2.md`(各案のB3出力=`export/selected_fact_ids`・`storyline`、注記済みB3=`export/selected_brief_annotated.md`)。B案R2なし。参考(混同注意): 旧Trialの既存R2 `er052_output/factlock_astra_e2e_trial_01/runs/meta/new/new_writer/r2.raw.md`(今回のB案ではない)。
Blind比較ページ: `user_test/ja_quality_model_allocation_01/index.html`(4本、対応表は`BLIND_MAP_01.json`、評価前に開示しない)。

## 4. 比較条件の一致・相違
- 同一(全案): Fact Ledger(sha ea0ce587…)、topic、B3 Prompt/schema/effort(sha一致)、R0/R1/R2 Prompt定数(R0_PROMPT 6108a7cd…、DEVELOPER d1fbb042…、R0_BLOCK 74b94871…、USER_TMPL 313120e9…)、effort=high、developerはR0のみ、previous_response_idなし、R2入力=R1 raw、記号QA上限、決定論producer(deterministic_v2、LLM0)。
- 無課金ドリフト検査(`maq_driver_01_test_01.py`、結果`maq_driver_01_test_01_result.txt`=ALL_PASS): A構成のstubでProduction `run_w1_writer`とdriverの**request列・出力ファイルが完全一致**(通常、R0記号再生成、R2再実行、R0/R2のSTOP分岐の5ケース)、B3呼出がProduction呼出と一致(model差替のみ差分)、単価再計算でA実測35.645円、予算guard、400非受理で停止。
- C: B3(LLM出力部)はAの既存成果物を複製、決定論producerの出力(注記済みB3・制約)がAとバイト一致を確認。C案のR0 Prompt sha=Aと同一(bc835749…)。
- 相違・限界: **選択Factが案で異なる**(A/C: HC-006+012の2件、D: HC-010+012、E: HC-006+010+012の3件)=B3モデル差がFact・storylineに波及(D/Eは配置全体の比較であり単一因子の効果分離ではない)。N=1(非決定性と配置効果を分離できない)。C/D/Eは並列process実行のため秒は参考値。A/B入力契約差(B案がSTOPのため比較できていない)。B3 rawの逐語はA既存artifactに無く、A/Cは`fact_selection_evidence.json`(parsed)が正。
- 観測: D案タイトル末尾が「、」になっているのは、モデル出力「……」をProduction共通のpostprocess(`normalize_ellipsis_pause_ja`)が決定論変換した結果(Aでも同じ処理が走る)。

## 5. B案(旧仕様の再現)が課金前STOPの理由と選択肢
- 一次資料(`er052_factlock_astra_e2e_runner_01.py`のFROZEN表・`factlock_astra_e2e_trial_01/annotation/`・`ANNOTATION_DELEGATION_TEMPLATE_v2.md`・`RUN_ANNOTATION.md`・`runs/meta/shared/`)から、旧Trial B案のB3→R0入力は **「凍結済みの旧B3出力(brief、`open233_b3_trial_01`由来)を、Claude Sonnet subagent 2名の独立二重注記+統合スクリプトで`【事実N】`化した成果物」**であり、(a)B3は新規LLM callではなく凍結入力、(b)注記工程はAPIではなくClaude側subagent作業(呼出し手順はRUN_ANNOTATION.mdのsubagent起動文言)、と特定された。
- 指示は「B3は新規にLunaで実行、注記工程は記録どおり、再現できなければ課金前STOP(代替仕様へ変更しない)」。新規Luna B3の出力を旧注記工程へ通すにはsubagent注記(本層はAgent起動禁止)が必要で、決定論producer(deterministic_v2)で代替すればA案と同じ入力契約になり旧仕様ではなくなる。よって**STOP**。他案(C/D/E)はB案に依存しないため継続し完了した。
- sha一致表(旧Trialと現HEAD、f71dbb41時点のjaw moduleを無課金で読込み比較): R0_PROMPT 6108a7cd…=一致、DEVELOPER_MESSAGE d1fbb042…=一致、SYMBOL_PREVENTION_BLOCK_JA 0629ab47…=一致、AN3_BLOCK 067030ff…=一致、R0_BLOCK(`factlock_r0_block_sha256`)74b94871…=一致、USER_TMPL(系列X)313120e9…=一致。**Promptは旧と現で同一**。旧のFact Checker(R0後)は撤去済みだがMETAの旧R0はmust_fix_applied=falseで本文に影響なし。
- 選択肢(Fable/ユーザー判断): (i)**凍結済み旧注記済みbrief(`runs/meta/shared/brief_annotated.md`、3事実HC-006/010/012、sha 6371e102…)を入力に固定し、R0(Luna、現Prompt)→R1/R2(Astra X)を再生成**(B3新規callなし、約¥35、cap65内。旧注記工程の成果物をそのまま使うため入力契約は記録どおり、ただしB3新規実行ではない=指示の「B3新規Luna」とは異なる)、(ii)新規Luna B3+Fable経由のSonnet subagent二重注記(Fable側で起動、追加手順・非決定)、(iii)B案を比較から外して4案評価、(iv)既存R2(2026-10-09生成)を参考として別枠で読ませる(再生成ではない)。いずれも本層は未実施(課金0)。B案を追加する場合、Blind割当は再生成し直す(現ページは4本)。

## 6. 補助指標の要約(詳細は`AUX_METRICS_01.md`。人間判断の代替ではなく、ユーザー評価前には提示しない)
本文字数 A943/C797/D777/E920、選択Fact数 2/2/2/3、Ledger外の数値0(全案、本文に数値なし)、制約文混入0、記号QA 0、タグ残存0。Aに英字「SF」(Ledger外、一般語)あり。生成秒 A135/C95/D160/E200(並列影響あり)。

## 7. Status分類案・未解決
- Status案: MEASURED(N=1)。VALIDATED/REJECTEDはユーザーBlind評価後。Production採用は`USER_DECISION_REQUIRED`、本Trialは採用提案を含まない。
- 未解決: (1)B案の扱い(5節の選択肢)、(2)Blind評価(4本ページ、順位・公開水準・コメント)、(3)費用対効果判断、(4)因子分離が必要なら別Trial、(5)Sol `gpt-6.1-sol`のpromotional価格期限は未確認(snapshot注記)、(6)Pages公開はpublic(META記事本文、既存`user_test/`と同運用)。
