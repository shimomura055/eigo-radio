# PREREGISTRATION_01: WRITER-RISK-FLAGGER-A4-DUALMODEL-OR-TRIAL-01 Phase 2(2026-10-10、実行前登録)

Trial/DEVのみ。Production・CURRENT_SPEC・Promptは変更しない。結果を見た後の条件変更・再実行はしない。

## 1. 目的
Risk Flaggerの A3 を省略し、**A4を2モデル(Luna / Gemini 3.5 Flash-Lite)でORした出力(A4-OR)**で、既存のSol A3+A4 Union(29文)相当のFact Risk候補を拾えるか、Human Review量はどう変わるかを機械的に整理する。Claude側は**Blind**(Human A/B/C/D判定は不使用・不参照・Promptにも入れない)。ユーザー判定との照合はTrial完了後にChatGPT側。A3を外せるかの最終判定(A3_REMOVAL_SUPPORTED等)はClaude側で確定しない。

## 2. 評価セット
POST-EN-TRIAL-01 の英語稿11本(U01-U08, X09-X11)。既存の完全台帳・splitter(post_en_common.build_unit)・入力構築・出力schema・validate_flags・retry機構をそのまま使用(`post_en_trial_01/manifest_post_en_01.json`)。A3 system sha256 `9d9950428419c3af824cc5b8676a4b564f96aeb87657c547d418cc86ef3538e9`、A4 `c87b95e5bcf1b5c266b8978c5688849eb339a6087efbcaf56bb7399ed128ef01`。母集団外: META rollback s23(CROSSMODEL-01結果は参考付記のみ)。

## 3. 4条件
| 条件 | model_id | effort/thinking | max出力 | 再利用判定 |
|---|---|---|---|---|
| Luna A3 / Luna A4 | `gpt-6-luna`(OpenAI Responses API) | reasoning effort=medium(META CROSSMODELと同一) | max_output_tokens=8000 | **新規22 call**(Luna A3/A4のPOST-EN artifactは存在しない。Phase 1棚卸し) |
| Gemini A3 / Gemini A4 | `gemini-3.5-flash-lite`(Gemini REST generateContent) | Provider既定(thinkingConfig送らない。CROSSMODELと同一) | maxOutputTokens=8000 | **新規22 call** |
| 参考: Sol A3 / Sol A4 | `gpt-6.1-sol` | medium | 8000 | **既存22 call再利用**(POST-EN-TRIAL-01、Union 29)。再実行しない。補助指標のみ |

- Gemini指定名は「Gemini 3.5 Flash-Lite」(ユーザーがCROSSMODEL-01で指定)=最新世代Flash-Lite。**より安価な旧世代 gemini-3.1-flash-lite($0.25/$1.50)・gemini-2.5-flash-lite($0.10/$0.40)がmodels listに実在するが、置換しない**(25節の最新原則)。呼べない場合は置換せずSTOP。
- 価格(USD/1M tokens in/cached/out、公式取得 2026-10-10、xm_prices_01.json): Luna 0.10/0.01/0.50、Gemini 3.5 Flash-Lite 0.30/0.03/2.50(thinking込み)。USD/JPY=160。
- 25節(最新モデル原則): Luna=OpenAIの効率系最新世代(gpt-6-luna、ユーザー指定条件)、Gemini 3.5 Flash-Lite=最新世代Flash-Lite、Sol(既存)=gpt-6.1-sol最上位系。旧世代の使用なし。
- 費用ガード: 累計 JPY100 到達で残りを実行せずSTOP(1セル上限 JPY8)。Phase 1見積 中央10.3/高位33.6/最悪67。

## 4. 同一条件・dry-run
`dm_driver.py dry` が44 request payload(model2 x 記事11 x A3/A4)を `dry_run/` へ保存し、A3/A4のsystem文字列・user文字列が既存 `post_en_trial_01/logs/d2_gpt-6.1-sol_pe_A*_raw.jsonl` の request と**記事ごとに完全一致**することを assert 済み(22/22一致、全記事で成立)。`dry_run/dry_run_report_01.json` sha256 `f7d6239296b9bb21c454d4ba2bd71e73264ee0ea8a4350cdc09543ec3dc10fd3`(記事別 system_sha/user_sha 記録)。Provider固有差分は adapter 必須分のみ(xm_driver.py流用、無変更)。JSON mode・temperature・seed等は送らない。

## 5. 実行規則
Luna 22 call → Gemini 22 call(安価順。独立Providerのため並行process実行可、ledgerはappend)。結果を見た再実行・追加run禁止。許されるretryは既存機構のみ(format再試行1回 = 出力が validate_flags 不合格のとき、transient再試行2回 = API例外)。件数・理由を記録。**出力無効**(2回とも validate_flags 不合格 = schema外type等)は「出力無効」として集計対象外(Flagなし扱いにせず `invalid` と明記)、無効出力の中身は参考節にのみ残す。保存: `runs/<model_key>/<article_id>/A3.json, A4.json`(raw response含む)、`cost_ledger_dm_01.jsonl`。既存結果があれば上書きせず停止。前タスクdirへは書き込まない。

## 6. Blind
Human A/B/C/D判定は不使用。Claude側で有用/ノイズ判定しない。Promptに既知例・Union 29・Human評価を入れない(system/userは既存と同一)。表のHuman評価・有用/ノイズ・「A3なしで失うか」列は空欄(ChatGPT側記入用)。

## 7. 定義
- **主キー**: (記事ID, 文ID)。MATCHING_RULE_01.md準拠。typeの差は別issueにしない(同一文なら同一候補)。文ID不一致は不採用でなく「文ID未特定」として別掲。
- **OR**: A3-OR = Luna A3 ∪ Gemini A3、A4-OR = Luna A4 ∪ Gemini A4(主キーの和集合。related Factは和集合を表示)。出力無効の回は空集合でなく「欠損」として注記し、ORはその回を除いた和で算出し明記する。
- **semantic issue単位**: 同一記事内の文を、**既存の束ね方**(aggregate_post_en.py BUNDLE。U03 s1/s5/s13/s33、U04 s7/s15、U06 s8/s9、X11 s4/s17)に従って束ね、それ以外は1文=1 issue。既存に無い新規Flagは束ねない(1文=1 issue)。表の1行は(記事ID+文ID+related Fact)。
- **既存Union 29**: POST-EN-TRIAL-01のSol A3∪A4のFlag文(U01-s18 …)29件(`post_en_trial_01/flags/A3, A4`から機械生成)。**未評価** = Luna/Gemini のFlagのうち、(記事ID, 文ID) が既存Union 29に一致しないもの。
- **主評価**(A3を外せるか): A3-OR の全項目(sentence単位)に対し、A4-ORでカバーされるか。「A3のみ検出」件数 = |A3-OR \ A4-OR|(機械的事実)。補助表1b: Sol A3 Flag各項目の A4-OR / Luna A4 / Gemini A4 カバー。カバー率 = カバーされたSol A3 Flag数 / Sol A3 Flag総数。
- **副評価**(Human Review量): A4-OR の raw Flag数 / sentence重複除去後 / semantic issue数 / 既存Union 29一致数 / 未評価数 / 1記事平均(=件数/11、出力無効除く記事数は注記)。比較: Luna A4、Gemini A4、A4-OR、参考Sol A4(既存)。
- A/B/C/D 列は空欄。confidenceは相対比較・分布のみ、絶対評価に使わない。
- 最終判定(A3_REMOVAL_SUPPORTED/NOT_SUPPORTED 等)は**Claude側で確定しない**。Status提案は USER_DECISION_REQUIRED(ChatGPT側照合後に判定)。

## 8. 出力物
INVENTORY_01.md(既存)、dm_driver.py、aggregate_dm_01.py → aggregate_dm_01.json、RESULT_01.md(表1/1b/2/3、4条件Flag一覧、未評価Flag一覧(confidence・モデル名あり/なし2版)、費用、retry、非エンジニア向け3点)、matching_packet_01.json/.md(全Flag x 4条件を Union 29 ID へ突合)。

## 9. やらないこと(9項目)
1. Production変更 2. CURRENT_SPEC変更 3. Prompt変更・Providerごとの最適化 4. Human判定の使用・推測、Human情報のPrompt/Blind packetへの混入 5. 結果を見た再実行・追加run・失敗条件のモデル置換 6. A5/A6・強制TopN・Rewrite・再生成・STOP処理の追加 7. 最終判定(A3削除可否)の確定・Production採用判断・APPROVED項目のStatus変更 8. META rollback s23を母集団に含める(参考付記のみ) 9. pip install・前タスクdirへの書き込み

## 10. Status不変更
A3+A4英訳後配置=VALIDATED。R0後/翻訳後Hard STOP Check除去・新Writer+Checkerなし+A3/A4+Human Review(OPEN-244)=APPROVED_FOR_PRODUCTION、いずれも未PRODUCTION_WIRED。本Trialで変わらない。AI Pre-sorter=新規Trial、Production採用未決。

## 11. STOP条件
dry-run不一致 / 累計JPY100到達 / Gemini 3.5 Flash-Liteが呼べない(置換せずSTOP) / Prompt変更が必要と感じた場合。
