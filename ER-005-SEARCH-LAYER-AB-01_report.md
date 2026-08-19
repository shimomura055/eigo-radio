# ER-005-SEARCH-LAYER-AB-01 実行報告書

**タスク**: Search Layer分離型Architecture(Query Planner → 外部Search API → Topic Selector)の成立性検証
**実行日**: 2026-08-19
**Query Planner / Topic Selector**: GPT-5.6 Luna(built-in web_search不使用)
**Search API**: Tavilyのみ(Brave / Perplexityは`CREDENTIAL_REQUIRED`のため未実行)
**User Input**: 「最近の子育て研究」のみ

---

## A. Provider readiness(実行前確認、9章)

| Provider | Credential | 判定 | 備考 |
|---|---|---|---|
| Brave Search | 未設定 | **CREDENTIAL_REQUIRED** | 2026年2月に無料枠廃止、新規取得はユーザー確認待ちのため今回は未実行 |
| Perplexity Search | 未設定 | **CREDENTIAL_REQUIRED** | 同上 |
| Tavily | **`TAVILY_API_KEY`をユーザーが設定済み** | **OK** | 月1,000クレジット無料枠。接続確認(HTTP 200、`url/title/content/score/raw_content/id`フィールド確認)済み |

ユーザーの指示により、今回はTavily 1社のみで検証を実施した。Brave/Perplexityは仕様9章の規定通り、私からアカウント新規登録は行っていない。

---

## B. Stage A1: Query Planning(Luna、1回のみ)

Lunaに`web_search`ツールを与えず、User Input+Service Policyのみから検索queryを生成させた。

生成されたquery(6件、上限内、切り捨てなし):

1. `parenting research OR child development study 2023..2025 surprising findings newsworthy`
2. `recent parenting research systematic review meta-analysis 2023..2025 family child outcomes`
3. `site:sciencedirect.com OR site:springer.com OR site:apa.org parenting child development study 2023..2025`
4. `site:nih.gov OR site:pubmed.ncbi.nlm.nih.gov parenting child development research 2023..2025`
5. `site:newswise.com OR site:eurekalert.org OR site:phys.org parenting research child development 2023..2025 university study`
6. `recent longitudinal study parenting family life children 2023..2025 unexpected findings`

特定の研究・分野への早期収束はなく、学術DB・大学プレスリリース・一般的な意外性キーワードの3方向をカバーしている。このquery群は、Tavily 1社のみの検証となった今回も含め、**1回だけ生成し使い回した**(3プロバイダ共通利用を想定した設計のまま、Brave/Perplexityが動く際も同じqueryを再利用できる)。

コスト: $0.000471(532 input tok + 304 output tok、search callなし)

---

## C. Stage A2: Tavily Search

同一の6 queryをTavily Search API(`search_depth=basic`, `max_results=10`)へ投入。

| 指標 | 値 |
|---|---|
| Raw result数(6 query合計) | 57件 |
| Dedup後(URL完全一致のみ除外) | 54件 |
| Candidate Pool上限(20件)適用後 | 20件(34件を relevance/source quality のみで機械的に削減) |
| Duplicate率 | 3/57 = 5.3%(低い) |
| Noise率(明らかにUser Input無関係と判定した件数) | 0件(全件が育児・子ども発達研究に関連) |
| Primary/academic source比率(20件中) | 20/20(PMC・PubMed・Springer・Nature・SAGE・ScienceDirect・MDPIのみ) |
| `published_date`が取得できた件数 | **0/57**(Tavily basic searchのレスポンスでは常にnull) |

**Tavilyの制約として今回判明した点**: `published_date`フィールドは、Tavily公式ドキュメント上はレスポンスに含まれる仕様だが、今回のbasic search(`topic`未指定=`general`)では57件全てで`null`だった。日付フィルタ自体(`time_range`パラメータ)はAPI側に存在するが、個々の結果に発行日を機械的に付与する機能ではないため、freshness判定はLuna(Topic Selector)がスニペット中の年号やDOIパターンから推測する形になった。この点はBrave/Perplexity比較時に再検証すべき差異として記録する。

Dedupは仕様12章の規定通り、URL完全一致のみを機械的な除外基準とし、内容の面白さによる手動除外は行っていない。20件への絞り込みも、Tavily自身の`relevance_score`と機械的なprimary-source-likelihood分類(ドメインパターンのみ)のみを用いた。

コスト: 6 request。今回は月次無料枠(1,000クレジット)内のため実費$0。Production-equivalent(従量課金 $0.008/credit)なら$0.048、Growth plan単価($0.005/credit)なら$0.03。

---

## D. Stage A3: Topic Selection(Luna、Tavily候補のみ、1回)

Tavilyの20件Candidate PoolのみをLunaに渡し(Luna自身は検索していない)、Service Policyに基づく評価・選定を実施。

**Shortlist**: TAV-003, TAV-004, TAV-006, TAV-008, TAV-014

**Final Selection**: **TAV-003** — 「86研究のメタ分析で見る、子育てストレスと親の幸福」
(Parental Stress and Well-Being: A Meta-analysis、PMC12162691、2024年9月までに収集された86研究の統合)

**選定理由(Lunaの記述、要約)**: ユーザー入力「最近の子育て研究」に最も直接的に合致し、86研究を統合したメタ分析であるため最新性・信頼性・ニュース価値のバランスが良い。育児テクニックではなく親自身のウェルビーイングを扱う点がリスナーに身近で興味を引きやすく、PMCの全文一次論文へ到達できるため約5分の記事として研究規模・関連傾向・限界を説明できる。

**Rejected Shortlist**(主要理由の要約):
- TAV-004(親子関係と成人後幸福、Nature Communications Psychology): 魅力的だが多国間比較の因果関係を誤解なく説明する必要があり、当事者への直接性でTAV-003に譲る
- TAV-008(文化的文脈と子育て理論、PubMed): 国際的な価値は高いが、TAV-003よりニュース価値がやや弱い
- TAV-006(ADHD児への親トレーニング、SAGE): 最新で具体的だが対象が限定的
- TAV-014(家庭ストレス・レジリエンス、PMCスコーピングレビュー): 高評価だが個別研究ではなく整理型レビューでTAV-003に譲る

candidate_assessmentは20件全件に対して8観点(user_intent_fit / freshness / news_value / entertainment_value / surprise / curiosity / five_minute_story_depth / source_quality)+primary_source_reachabilityで実施。`published_date`が取得できなかった候補については、一貫して「掲載日は未確認」「スニペット上は◯◯年」等、断定を避ける記述になっており、確認していない情報を確定情報として書く違反は見られなかった。

コスト: $0.007552(4,597 input tok + 5,527 output tok、search callなし)

---

## E. Human Review用比較Artifact(21章)

| 項目 | Brave | Perplexity Search | Tavily |
|---|---|---|---|
| Query数 | — | — | 6 |
| Raw result数 | — | — | 57 |
| Dedup後候補数 | — | — | 54 |
| Primary-source候補数(Pool内20件中) | — | — | 20 |
| Shortlist | — | — | TAV-003, TAV-004, TAV-006, TAV-008, TAV-014 |
| Final Topic | — | — | 86研究のメタ分析で見る、子育てストレスと親の幸福(PMC12162691) |
| Entertainment Value | — | — | 中〜高(Lunaの評価) |
| 5分記事適性 | — | — | 非常に高い(Lunaの評価) |
| Source Quality | — | — | 非常に高い(PMC全文アクセス可) |
| Search API Cost(実費/production-equivalent) | CREDENTIAL_REQUIRED | CREDENTIAL_REQUIRED | $0.000(free tier)/ $0.048(pay-as-you-go) |
| Luna Planner/Selector Cost | — | — | $0.008023(Query Planner $0.000471 shared + Topic Selector $0.007552) |
| **Total Topic Selection Cost** | — | — | **$0.008023(実費)** / **$0.056023(production-equivalent)** |

Brave/Perplexityは列全体が`CREDENTIAL_REQUIRED`のため今回比較不可。

---

## F. Architecture成立判定(Tavily path)

**`ARCHITECTURE_PASS`**

判定根拠:
- Candidate Poolは学術一次資料(PMC/PubMed/Nature/Springer/SAGE等)に強く偏っており、Noise率0%、Duplicate率5.3%と質が高い。
- Lunaは20件全件を実際に評価し、根拠のある(かつ不確実性を隠さない)Shortlist・Final Selectionを構成できた。
- Final Topic(親のストレスとウェルビーイングに関する86研究メタ分析)は、実在する一次資料に裏付けられ、5分番組として十分な厚みを持つ、eigo-radioに適した題材である。
- コストは$0.008(実費)〜$0.056(production-equivalent)と、Business Target($0.10/episode)に対して十分小さい。

---

## G. Architecture全体の判断(25章 Q&A)

**Q1. Luna + 外部Search API分離型は成立するか？**
Tavilyについては**成立する**。検索ツールを持たないLunaでも、外部から供給された高品質なCandidate Poolがあれば、Service Policyに基づく実務的なTopic Selectionができることが確認できた。ただしBrave/Perplexityは未検証のため、「Search Layer分離Architecture全般」としての結論は本タスクの範囲では出せない(Tavily限定の結論)。

**Q2. 3providerのうち最も良いCandidate Poolを作ったのはどれか？**
今回はTavilyのみ実行のため比較不可。Brave/Perplexityの credential が揃い次第、再検証が必要。

**Q3. 最も良いFinal Topicを生んだproviderはどれか？**
同上、比較不可(Tavilyの結果のみ存在)。

**Q4. Luna built-in Search時と比べ、Topic品質は維持されたか？**
維持されている、というより**構造的な質の高さでは同等以上**と評価できる。ER-005-E2E-RESEARCH-AB-01-P1でのLuna built-in Search結果(親のえこひいき、PMC/DOI付き、9候補)と比較すると、Tavily供給の今回は20候補と母数が多く、全件PMC/PubMed等の一次資料が確保されており、Sourceの多様性・到達性の面でむしろ優れている。ただし選ばれたTopicそのものは別の研究であり、「同じTopicを選ばなければFAILではない」という20章の原則通り、この違い自体は問題ではない。

**Q5. Search API分離によってCost削減余地は見えたか？**
明確に見えた。Luna built-in Searchでの零ベースTopic Selection(Stage A、ER-005-E2E-RESEARCH-AB-01-P1)は$0.0822(57,417 input tok、6 search call×$0.01)だったのに対し、Search Layer分離(Query Planning + Tavily + Topic Selection)は$0.008(実費、free tier)〜$0.056(production-equivalent)。token消費面でも、Luna自身が検索・閲覧を繰り返す必要がなくなったため、Topic Selector呼び出しのinput tokenは4,597(built-in Search版の約1/12)に減少した。

**Q6. 次にGemini / DeepSeekへ同じCandidate Poolを渡すSelector比較へ進む価値があるか？**
価値はあると考えられるが、本タスクの範囲では実行しない。まずはBrave/Perplexityの credential を揃え、3provider横並びでのSearch Layer品質比較を完了させる方が優先度が高い(今回はTavily 1社の結果のみのため、「外部Search API層」自体の一般的な結論としてはまだ材料が不足している)。

---

## H. 受入条件確認(28章)

- User Inputは「最近の子育て研究」のみ: **確認済み**
- Service Policyは承認済み文面を使用: **確認済み**(前タスクと同一定数を再利用)
- Query PlannerはLuna: **確認済み**
- Query Plannerは1回のみ: **確認済み**(`stage_a1_query_plan.json`を再利用し、再生成していない)
- Query群は3provider完全同一: **該当providerがTavily1社のみのため実質的に自明に満たす**(同一のquery群を使う設計はそのまま維持、Brave/Perplexity実行時も同じqueryを再利用する)
- Claude Codeがqueryを手作業補完していない: **確認済み**(6件ともLuna自身の生成、切り捨てなし)
- Luna built-in web_search不使用: **確認済み**(Stage A1・A3ともにtools未指定)
- Candidate Poolをprovider別に保存: **確認済み**(`tavily/stage_a2_candidate_pool.json`)
- Dedupルールを記録: **確認済み**(URL完全一致のみ、本報告書C章)
- Shortlist / Final Topicを保存: **確認済み**(`tavily/stage_a3_topic_selection.json`)
- Search API costを実測: **確認済み**(6 request、実費$0/production-equivalent$0.048)
- Luna costを実測: **確認済み**(Query Planner $0.000471 + Topic Selector $0.007552)
- Production-equivalent path costを算出: **確認済み**($0.056023)
- Human review可能な比較Artifactあり: **確認済み**(本報告書E章、ただしBrave/Perplexity列はCREDENTIAL_REQUIREDのまま)
- Research/VFL未実行: **確認済み**
- Production/CURRENT_SPEC未変更: **確認済み**(触れたのは本タスク専用スクリプト`er005_search_layer_ab_01.py`のみ)

## I. Stop条件

Tavilyでの Query Plan×1 → Search×6 → Topic Selection×1 → 比較レポート作成が完了したため、ここでSTOPする。Brave/Perplexity・Gemini/DeepSeekへのSelector比較・Research/VFLへは進まない。

---

## J. 成果物一覧

- `er005_search_layer_ab_01.py` — 実行スクリプト
- `er005_output/search_layer_ab_01/stage_a1_query_plan.json` — Query Plan(共有、1回のみ)
- `er005_output/search_layer_ab_01/tavily/connectivity_check.json` — 接続確認記録
- `er005_output/search_layer_ab_01/tavily/stage_a2_raw_results.json` — Tavily生レスポンス(6 query分)
- `er005_output/search_layer_ab_01/tavily/stage_a2_candidate_pool.json` — Dedup・20件上限後のCandidate Pool
- `er005_output/search_layer_ab_01/tavily/stage_a3_topic_selection.json` — Luna Topic Selection結果
- `er005_output/search_layer_ab_01/raw_usage_log.jsonl` — 全8呼び出し(Luna×2、Tavily×6)のコストログ
- 本報告書 `ER-005-SEARCH-LAYER-AB-01_report.md`
