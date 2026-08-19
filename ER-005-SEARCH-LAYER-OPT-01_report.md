# ER-005-SEARCH-LAYER-OPT-01 実行報告書

**タスク**: Perplexity Search Multi-query化 / Date Handling整理 / Pruning Audit
**実行日**: 2026-08-19
**対象**: ER-005-SEARCH-LAYER-AB-01のPerplexity経路のみ最適化(Architectureは変更しない)

---

## 完了報告の最上段(17章の必須回答)

1. **6 queryを何requestに圧縮できたか**: **2 request**(Request 1: query1〜5、Request 2: query6。仕様3章の指定通り)
2. **Search Costはいくらになったか**: **$0.01**(2 request × $5/1,000。旧6-request版の$0.03から66.7%削減)
3. **Topic Selection総Costはいくらになったか**: **$0.018837**(Query Planner $0.000471 + Search $0.01 + Luna Topic Selector $0.008366)
4. **旧6-request版と比べCandidate Pool品質は維持されたか**: **ほぼ維持**。Primary source比率20/20は同一、Duplicate率はむしろ改善(3.3%→2.5%)。ただしraw結果数は60→40に減少(4章・7章で詳述)。
5. **Final Topic品質は維持されたか**: **維持**。実在する2026年5月の縦断研究(Frontiers、親子の葛藤とスクリーンタイムの関係)を選定、Shortlist・Rejected reasonsとも一貫した論理で構成された。
6. **date / last_updated問題は整理できたか**: **整理できた**。旧版は`last_updated`のみを`published_date`として渡していたため、Luna自身が20件中4件で「日付が内容と食い違う」と検出していた。今回は`date`(出版日候補)と`last_updated`(更新日候補)を別フィールドとして渡し、Topic Selectorにも両者を混同しないよう明示指示した結果、**日付不整合の指摘は0件**になった(=そもそも正しいフィールドを見ていなかったことが前回の「不整合」の主因だったと判明)。
7. **58→20件pruningは完全にdeterministicか**: **`DETERMINISTIC_PIPELINE_SAFE`**(7章で詳述)。
8. **Topic Selection $0.02以下に到達したか**: **到達した**($0.018837 < $0.020、Target達成。Excellent基準の$0.015には僅かに届かず)。
9. **次にResearch/VFL Cost Redesignへ進む価値があるか**: 価値はあるが、本タスクの範囲では判断材料が不足している(下記K章参照)。まずTopic Selection側の3provider揃え(Brave)か、この結果を土台にしたResearch Brief/VFL側のコスト設計に進むかは、ユーザー判断が必要。

---

## A. 検証A: Perplexity Multi-query化

### API仕様の実測確認

| 確認事項 | 結果 |
|---|---|
| multi-query受理 | **受理される**(`query`パラメータにstring配列を渡すとHTTP 200) |
| 6 queryすべての検索意図が反映されるか | **部分的に反映される、ただし制約あり**(下記参照) |
| `max_results`の挙動 | **request全体で1〜20(default 10)、query数に応じて自動拡大しない** |

**重要な発見**: `max_results`はrequest単位の上限であり、query配列の要素数とは無関係に固定の1〜20件しか返らないことを実測で確認した(2 query + max_results=3 → 合計3件、5 query + max_results=20 → 合計20件)。したがって、5 queryを1 requestへ束ねると、1 queryあたりの実質的な結果深さは**旧来の10件/queryから、平均4件/query相当まで薄まる**。この制約はPerplexity公式ドキュメントの「best practiceとして1 requestあたり最大3 query程度を推奨」という記述とも整合する(今回は仕様3章の指定通り5+1で実行したが、この制約は必ず今後の設計に反映する必要がある)。

このため、Request 1(5 query束ね、max_results=20)は5 query合計で20件、Request 2(1 query単独、max_results=20)はその1 queryだけで最大20件、という非対称な結果になった(実測: Request 1由来12件、Request 2由来8件が最終Poolに残存)。

### Multi-queryのresponse構造

`results[]`は**request全体で1つのflatな配列**として返り、個々の結果がどのqueryに対応するかを示すAPI側の帰属情報は無い(公式ドキュメント・実測とも確認)。そのため、旧版にあった「1件ごとに発見queryを1つ特定する」フィールド(`query_that_found_it`)は維持できず、今回は`query_batch_that_found_it`(そのrequestで使った query配列全体)として正直に記録した。**これはmulti-query化に伴う実質的な情報損失であり、品質低下要因として明記する。**

---

## B. 検証Bとの統合実施: Date handling整理

`date`(出版日候補)と`last_updated`(更新日候補)は、Perplexity公式APIレスポンス上、**別々のフィールドとして最初から提供されている**ことを実測で確認した(2026-08-19取得)。ER-005-SEARCH-LAYER-AB-01時点のコードは誤って`last_updated`のみを取得し、それを`published_date`として記録・Topic Selectorへ渡していた。これが前回「日付が内容と食い違う」という問題の直接の原因だったと判明した。

**実測例**(2 queryのテスト呼び出しより):

```
結果1: date=null,          last_updated="2024-09-26"
結果2: date="2024-08-16",  last_updated="2026-05-05"
```

結果2は本文スニペットが「2024 Aug 16」と明記しており、`date`フィールドがこれと一致する一方、`last_updated`(2026-05-05)は明らかに別物(クロール・インデックス更新日相当)である。`date`が欠損する結果もあり(結果1)、`last_updated`だけの候補は今回も残り得る。

**対応**: Candidate Pool schemaに`date`と`last_updated`を別フィールドとして追加し、Topic Selector developer messageに「`date`は出版日候補、`last_updated`は更新日候補であり出版日そのものではない。`date`欠損時は出版日未確認と明示する」ことを明文で指示した。結果、今回のLuna評価では**日付不整合の指摘が0件**になった(前回4/20 → 今回0/20)。

**Publication date filter**: `search_after_date_filter`(MM/DD/YYYY形式)が利用可能であることを確認し、既存query文字列内の年範囲(`2023..2025`)と揃える形で`search_after_date_filter=01/01/2023`を1パターンのみ実際のmulti-query呼び出し内に設定した(複数パターンの比較実行は行っていない、6章の規定通り)。

---

## C. 旧6-request版 vs 新Multi-query版 比較表(12章)

| 項目 | 旧Perplexity 6-request | 新Perplexity multi-query |
|---|---|---|
| Query数 | 6 | 6 |
| Request数 | 6 | **2** |
| Search Cost | $0.030 | **$0.010** |
| Raw results | 60 | **40** |
| Unique results(dedup後) | 58 | 39 |
| Duplicate率 | 3.3%(2/60) | 2.5%(1/40) |
| Top20 primary-source比率 | 20/20 | 20/20 |
| Noise率 | 0% | 0% |
| Date field | `last_updated`のみ、出版日と誤認しやすい | `date`(出版日候補)+`last_updated`(更新日候補)を分離 |
| 日付不整合の指摘件数(Luna評価) | 4/20 | **0/20** |
| Luna Selector Cost | $0.006951 | $0.008366(候補データにdate/last_updated2フィールド追加のため若干増) |
| **Total Topic Selection Cost** | **$0.037422** | **$0.018837** |
| Final Topic | 幼児のデジタル技術利用とウェルビーイング(ScienceDirect、2025年9月) | 親子の葛藤とスクリーンタイムの関係(Frontiers、2026年5月) |
| Architecture Quality | PASS | **PASS** |

**品質トレードオフの評価**: Raw resultsは60→40(-33%)、Duplicate後の候補プールも58→39(-33%)と明確に減少した。これはB章で確認した「max_resultsがquery数でスケールしない」というAPI制約の直接的な帰結である。ただし、**Top20 Poolに限れば**primary source比率(20/20)、Noise率(0%)ともに劣化しておらず、Lunaの最終選定も一貫して質の高い、実在する一次資料に基づくTopicを選べている。つまり「候補プールの母数は薄くなったが、最終的にLunaへ渡る20件・そこから選ばれるTopicの質は維持された」というのが実測結果である。

---

## D. 検証C: Pruning Audit(7〜8章)

### D-1. pruning処理のコード所在

`er005_search_layer_ab_01.py`内、`run_stage_a2_perplexity_search_multiquery()`関数(旧6-request版は`run_stage_a2_perplexity_search()`、ロジックは同一)。

### D-2. 使用しているranking key

1. **Dedup(60→58 / 40→39相当)**: `_normalize_url(url)`によるURL正規化(scheme+host小文字化+末尾スラッシュ除去)後の完全一致のみ。Pythonの`dict`で最初に出現した候補を残し、以降の同一URLは`also_found_in_batches`(旧版は`also_found_by_queries`)へ追記するのみで、候補自体としては採用しない。
2. **Top20への絞り込み**: `sorted(deduped, key=lambda c: (source_rank[primary_source_likelihood], -(result_rank_in_batch or 99)), reverse=True)`。

### D-3. 各判定基準の実装根拠

| 確認項目 | 回答 |
|---|---|
| provider relevance scoreを使っているか | 不使用(PerplexityにはTavilyのような`score`フィールドが無いため、`relevance_score`は常に`None`) |
| domain/source quality ruleを使っているか | **使用**。`_classify_primary_source_likelihood(url)`が、固定のドメイン文字列タプル(`PRIMARY_SOURCE_DOMAIN_HINTS_HIGH`/`_MID`、コード冒頭で定義済みの静的リスト)に対する`in`演算子のみで「高/中/低」を判定する。実行時に変化しない。 |
| freshnessを使っているか | 不使用(pruning段階では`date`/`last_updated`はランキングに一切使っていない。Freshness評価はStage A3のLunaが行うのみ) |
| primary-source-likelihoodの判定方法 | 上記の通り、静的ドメインリストとの文字列包含判定のみ |
| Claude/LLMによる意味判断が入っているか | **入っていない**。pruning関数内にLLM呼び出しは一切ない(Stage A3のLuna呼び出しは、pruning完了後の別関数) |
| 人手判断が入っているか | **入っていない**。私(Claude Code)が個々の実行結果を見てその場で候補を選別・除外したことはない |
| 同じ入力なら常に同じ20件になるか | **Yes**(Perplexity APIから返る生の`results[]`が同一であれば、dedup・ranking・cap処理は完全に決定的に同じ20件を返す。ドメインリストは実装時に静的に定義されたコードであり、実行のたびに変わらない) |

### D-4. 判定

**`DETERMINISTIC_PIPELINE_SAFE`**

Perplexity API自体が同一queryに対して常に同一の生結果を返すかどうかは、外部APIの挙動でありこの監査の対象外だが、**このリポジトリのコードが行っているpruning処理自体には、Claude/LLM判断も人手判断も一切混入していない**ことをコードレベルで確認した。

なお本監査でバグ(スコアの昇順/降順逆転、URL重複除去不備、fieldの参照ミス等)は見つからなかったため、8章の「明らかなbugのみ修正」は不要だった。

---

## E. Cost計測詳細(10章)

| 項目 | 値 |
|---|---|
| Query Planner(既存値を再利用、再課金なし) | $0.000471 |
| Perplexity Search(2 request × $5/1,000) | $0.010000 |
| Luna Topic Selector(4,942 input tok + 6,148 output tok) | $0.008366 |
| **Production-equivalent Total** | **$0.018837** |

Cost目標(11章)との対比: **Target($0.020以下)を達成**。Excellent($0.015以下)には僅かに届かなかった(主因はLuna Topic Selectorの出力トークンが旧版比+21%増えたこと。候補データに`date`/`last_updated`2フィールドを追加した分、Lunaの各候補評価の記述がわずかに長くなったため)。

---

## F. 成立判定

**`OPTIMIZATION_PASS`**

判定根拠:
- Multi-query化によりRequest数を6→2(-66.7%)、Search Costを$0.030→$0.010(-66.7%)に圧縮できた。
- Total Topic Selection Costは$0.037422→$0.018837(-49.7%)で、目標の$0.02以下を達成した。
- Top20 Candidate Poolの質(Primary source比率20/20、Noise率0%)は維持され、Final Topicも実在する一次資料に基づく、eigo-radioとして成立する題材を引き続き選べている。
- date/last_updated問題はフィールド分離により実質的に解消された(不整合指摘4/20→0/20)。
- Pruning処理はコード監査によりLLM/人手判断の混入なしと確認された(`DETERMINISTIC_PIPELINE_SAFE`)。

一方で、raw結果数が60→40(-33%)へ減少した点は、Multi-query化の構造的なトレードオフとして明記しておく。Top20という今回の枠内では実害が確認できなかったが、将来的にPool上限を大きくする設計変更を行う場合は、この「max_resultsがquery数に応じてスケールしない」という制約が直接のボトルネックになる。

---

## G. 受入条件確認(17章)

- Query Planner再実行なし: **確認済み**(`stage_a1_query_plan.json`を再利用)
- 既存6 queryをそのまま使用: **確認済み**
- Perplexity multi-queryを使用: **確認済み**(6 query→2 request)
- 可能なら6 query→2 request: **達成**
- built-in web_search不使用: **確認済み**(Stage A1・A3ともにtools未指定)
- old/new Candidate Pool比較あり: **確認済み**(本報告書C章)
- dateとlast_updatedを分離: **確認済み**(本報告書B章)
- pruningの実装根拠提示: **確認済み**(本報告書D章)
- pruningにClaude/人手判断がないことを確認: **確認済み**(`DETERMINISTIC_PIPELINE_SAFE`)
- Luna Topic Selector 1回のみ: **確認済み**
- Cost実測: **確認済み**(本報告書E章)
- Research/VFL未実行: **確認済み**
- Production/CURRENT_SPEC未変更: **確認済み**(触れたのは`er005_search_layer_ab_01.py`のみ)

## H. Stop条件

Multi-query Perplexity Search → Candidate Pool生成 → pruning Audit → Luna Topic Selector×1 → Cost比較 → Date metadata整理 → レポート作成が完了したため、ここでSTOPする。Brave・Tavily再実行・Gemini/DeepSeek Selector・Research/VFLへは進まない。

---

## I. 成果物一覧

- `er005_search_layer_ab_01.py` — 実行スクリプト(multi-query機能・date field分離を追加)
- `er005_output/search_layer_ab_01/perplexity_multiquery/stage_a2_raw_results.json` — 2 request分の生レスポンス
- `er005_output/search_layer_ab_01/perplexity_multiquery/stage_a2_candidate_pool.json` — Dedup・20件上限後のCandidate Pool
- `er005_output/search_layer_ab_01/perplexity_multiquery/stage_a3_topic_selection.json` — Luna Topic Selection結果
- `er005_output/search_layer_ab_01/raw_usage_log.jsonl` — 全18呼び出しの累積コストログ
- 本報告書 `ER-005-SEARCH-LAYER-OPT-01_report.md`
