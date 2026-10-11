# PHASE C 品質評価 設計(乾式のみ実施、有料実行は承認待ち)

driver: `er054_family_z_story_pool_quality_eval_trial_01.py`(Trial専用、Productionから参照されない)。
状態: モックでの乾式確認済み。`--mode real`は`--approved-budget-jpy`(ユーザー承認の課金上限)が無いと起動しない。
Status上限: `VALIDATED`。Production採用・Wiring禁止。

## 1. モデル選択と理由(PM_GOVERNANCE 25-3テンプレ)
| 使用モデル名 | 最新モデルか | 最新でない場合の理由 |
|---|---|---|
| gpt-6-astra(主) | はい(最新世代の最上位系・旗艦、公式 https://developers.openai.com/api/docs/models ・pricing 2026-10-09取得、`docs/pm/dev_eval_model_inventory_01.md`) | - |
| gpt-6.1-sol(比較・次点) | はい(最新世代の推奨系=バランス、同上) | - |
- 既存Routing(`er006_model_routing_contract_01.py`)は全Production工程がgpt-6-luna(Family X B3等はgpt-6.1-sol)。評価用途の工程名は無く、「ライン組み込み候補の性能確認」ではなく「評価者」なので25節の最新モデル原則が適用される。Luna(最上位ではなく、Production Writer側のモデルでもある)は評価者に使わない(旧/下位の例外理由が無い)。driverは許可モデルを上記2つに固定し、他は起動拒否。
- 単価: pricing_snapshot.json登録済み(gpt-6-astra 10/1/50、gpt-6.1-sol 2/0.10/10 USD/1M、OFFICIAL_PRICING_PAGE_FETCHED)。
- 推論量: reasoning effort=medium(Trial-02のcall方式を踏襲)。

## 2. 評価単位と原文の与え方(要約しない)
- 原則: 評価単位の**全文を原文のまま**1 callで渡す(章/段落単位の要約はしない)。評価単位が全文に収まらない場合のみ、章単位に固定(下記)。
- 日本語短編8本(L01,L02,L03,L05,L07,L08,L09,L10): 青空文庫本文領域の全文(`sources/<ID>/text_plain.txt`、ルビ除去済み)。4,435〜9,987文字。
- L04: Gutenberg短編集から『The Bet』本文のみ(見出し位置で決定論スライス、約2,691語)。
- L06: 自伝全体は約74万字で短編化評価の単位にならないため、第IV章(約1,060語)を仮設定。**これは設計仮定でユーザー確認事項**(L06は権利NGの意図的負例。既定では評価対象外、`--include-control`で明示した場合のみ評価)。
- 権利Gate連動: 既定の評価対象は権利判定PASSのみ。REVIEW_REQUIREDは`--include-review`、NGは`--include-control`の明示が必要。
- トークン見積(tokenizer未取得の代理値、実測で補正): 日本語1.0 token/文字、英語1.4 token/語、promptオーバーヘッド1,800 token。

## 3. Prompt案(driver内 `DEVELOPER_MESSAGE` / `USER_TEMPLATE`)
- developer: 与えられた原作本文だけを根拠に、英語短編(280〜420語、A2〜B1)再話素材として評価。知名度・記憶・過去評価に頼らない。各項目PASS/FAILのどちらか、根拠引用は本文の連続した文字列のみ(言い換え禁止、1項目1〜3個、各60文字/25語以内)。
- user: 評価対象(ID・タイトル・言語・評価単位・長さ)+4項目の定義(正本=Trial-02 REPORT §2の文言を転記: A中心事件・変化/B読者の関心/C展開・余韻/D短編化適性280〜420語)+手順(1)key_facts抽出(2)A〜D判定(3)appeal(4)compression_risk(5)diversity(6)JSONのみ+原作全文(`<<<BEGIN_SOURCE_TEXT ... END_SOURCE_TEXT>>>`)。
- 出力JSON schema(strict json_schema): `key_facts{central_event,main_characters,turning_point,ending,notable_quotes}`、`A/B/C/D{verdict:PASS|FAIL, evidence_quotes[1-3], reason, confidence}`、`appeal`、`compression_risk{level,notes,cut_candidates}`、`diversity{theme,mood,era,region,narrator}`。

## 4. 決定論の後処理(LLMに任せない)
1. 引用検証: すべての`evidence_quotes`/`notable_quotes`が原文(空白除去)の部分文字列か。不一致があれば`REVIEW_REQUIRED`(PASSでも降格、根拠の信頼性要確認)。
2. 総合判定: `pass_count>=3 かつ D==PASS`(Trial-02 §2のGate3必須+4項目中原則3項目以上に準拠。**この「かつD」の扱いはTrial-02の運用を踏襲した設計であり、Z-1(d)「原則3項目以上」とは厳密には異なる**: Phase D比較時に両ルールの結果を併記できるよう`pass_count`を別保存)。
3. Blind: driverは`SEALED_PAST_RESULTS_L01_L06.json`を読まない。新評価の確定後にPhase Dで開示・比較する。

## 5. 並列化設計
- 作品別・モデル別に別ファイル(`phase_c_eval/<model>/<ID>.json`)へ書く。同一ファイル書込みなし。`ThreadPoolExecutor(--workers 4)`で作品を並列call可。
- 直列化が必要な点: (a)実call前の保守見積と承認上限の照合(前工程)、(b)rate limit時のworkers低減。モデル間(Astra/Sol)は独立なので並列可だが、課金上限を共有するため合算の上限照合を先に行う。
- 所要見込み(実行時、並列4): 1 call 1〜3分(Astra, medium) → 全10 call 約5〜10分。直列だと約20〜30分。

## 6. 乾式確認の結果(API呼出なし、モック)
- `--mode dry-run --include-review --include-control`: 10作品すべてでprompt組立・JSON検証・引用検証・総合判定が動作(mock_calls=10)。偽引用を返すモックでは`REVIEW_REQUIRED`に降格し検出できることを確認。
- 許可外モデル(gpt-6-luna)指定は起動拒否、`--mode real`は承認上限なしで起動拒否。
- 出力: `phase_c_dry_run/`(モック結果。実評価結果ではない)。

## 7. ユーザー確認事項(USER_DECISION_REQUIRED)
1. 課金上限(`PHASE_C_COST_ESTIMATE_01.md`の案から選択)。
2. L06の評価単位(第IV章仮設定の可否)と、L06を負例として品質評価するか(権利NGのため既定は評価しない)。
3. L04(権利REVIEW_REQUIRED)を品質評価に含めるか。
4. 総合判定を「3項目以上かつD」とするか「3項目以上のみ」とするか(両方を保存するので事後切替は可能)。
