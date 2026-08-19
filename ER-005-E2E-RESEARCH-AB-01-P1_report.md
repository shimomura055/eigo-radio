# ER-005-E2E-RESEARCH-AB-01-P1 実行報告書

**タスク**: Zero-base Topic Selection → Research Brief → Research/VFL の3段階測定(Luna / Gemini 3.5 Flash-Lite、Parenting、各1回)
**実行日**: 2026-08-19
**入力**: ユーザー入力は一言のみ「**最近の子育て研究**」。具体的な研究名・著者・DOI・件数・結論は一切事前投入していない。

---

## A. 最重要結論(トップライン)

| 項目 | Luna (GPT-5.6 Luna) | Gemini 3.5 Flash-Lite |
|---|---|---|
| Topic Selection品質 | **PASS** | **FAIL**(検索していないのに検索したかのような記述あり) |
| Research/VFL品質 | **PASS**(27 Fact中26 VERIFIED、1 AMBIGUOUS、0 REJECTED) | **FAIL**(検索0回で「Confirmed」と自称) |
| Zero-base総コスト(Stage A+B+C) | **$0.3558**(Search fee: $0.27、Token: $0.0858) | **$0.0151**(全てToken、Search fee $0) |
| 最終判定 | `COST_NOT_VIABLE` | `TOPIC_SELECTION_FAIL` |

**一言で言うと**: Lunaは「本物のゼロベース調査」ができるが高すぎる。Geminiは安いが、今回も実際には検索していない(ツールを渡しても使わない)ことが、今回はより明確な証拠(捏造されたURLの痕跡・検索0回のまま「確認済み」と自称する記述)とともに確認された。

---

## B. 技術的な問題点(本題に入る前に必ず報告すべき2つのバグ)

実行中に、このタスク固有の**測定基盤側の技術的バグを2つ発見・修正**した。どちらも「モデルの実力」とは無関係な、こちらのスクリプトの不具合であり、修正後に正しい条件でGeminiを1回だけ再実行した(技術的失敗のみretry許容というタスク仕様に基づく)。

### B-1. ログ出力先の書き間違いバグ(発見・修正済み)

Stage CでOpenAI用スキーマ(`GEMINI_FACT_SCHEMA`等)を`er005_model_ab_01a_phase1.py`から再利用する際、`__import__(...)`による遅延importを使っていたため、そのモジュール冒頭の`cl.install("er005_output/model_ab_01a/raw_usage_log.jsonl")`が実行時に再発火し、コストログの出力先がこのタスク用のログファイルから、無関係な過去タスク(MODEL-AB-01A)のログファイルへ無断で切り替わっていた。Gemini Stage C(research/verification)の2件のログがそちらに紛れ込んでいた。

**修正**: `er005_e2e_research_ab_01_p1.py`の先頭でスキーマを事前import(モジュールレベル)するよう変更し、このタスク自身の`cl.install()`が確実に最後に勝つようにした。修正はこの1ファイルのみ、Production側のコードには一切触れていない。

### B-2. 文字化けバグ(発見・修正済み)

Gemini Stage B(response_schemaを使わない自由記述call)の出力が、日本語部分だけ`U+FFFD`(文字化け記号)に置換される現象を発見した。原因はこの実行環境のPython/コンソールの既定エンコーディングが`cp932`であり、google-genai SDKの一部経路がこれに引きずられていたためと判明(`PYTHONUTF8=1`で再現・解消を確認済み)。Stage A/Cは`response_mime_type="application/json"`を使うため影響を受けていなかった。

**この文字化けは、Gemini Stage Cへの入力(Research Brief)そのものを壊していた**ため、1回目のGemini実行結果(facts=1)は正しい測定とは言えない。

**対応**: 1回目のGemini結果一式は`er005_output/e2e_research_ab_01_p1/gemini_run1_corrupted_ATTEMPT1/`および`raw_usage_log_ATTEMPT1_corrupted.jsonl`として証跡保存した上で、`PYTHONUTF8=1`環境変数を付与し、B-1のバグ修正後のコードでGeminiのみ1回だけ再実行した。本報告書の数値・判定は、すべてこの**修正後のクリーンな2回目実行**に基づく。

なお、Lunaの成果物にも一部コンソール出力で文字化けして見える箇所があったが、これはBashツールのコンソール(cp932)側の表示問題であり、保存されたJSONファイル自体に`U+FFFD`は含まれていないことをバイト単位で確認済み(実データは無傷)。

---

## C. Stage A: Topic Selection比較表

| 観点 | Luna | Gemini 3.5 Flash-Lite |
|---|---|---|
| User Input解釈 | 「最近の子育て研究」を、育児行動・家族関係に関する2025年前後の学術研究と解釈 | 同じ入力を、政策ニュース〜学術研究〜科学ニュースまで幅広く解釈 |
| Search query数(観測値) | **6回**(web_search_call_count) | **0回**(web_search_queries=[]、grounding_chunks_count=0) |
| Candidate Pool件数 | 9件 | 5件 |
| Shortlist件数 | 5件(C1, C2, C3, C5, C6) | 3件(cand_03, cand_02, cand_01) |
| Final Topic | 親の「えこひいき」(Parental Differential Treatment)－娘・年長児・協調的な子への偏り | 「遺伝vs子育て」双生児研究－子どもの未来を決めるのは親の努力か遺伝か |
| Final選定理由(要約) | 19,469人の大規模メタ分析で、複数の切り口(性別・出生順位・性格)があり、断定を避けつつ5分の厚みが出せる点を評価 | 「親の努力より遺伝」という常識を覆す意外性・エンタメ性を最優先で評価 |
| 選定Topicの一次Source | `pubmed.ncbi.nlm.nih.gov/39818912/`(具体的な論文の実在するPubMed個別ページ) | `sciencedaily.com/news/plants_animals/parenting/`(**特定記事ではなく、ScienceDailyの「parenting」タグ一覧ページ**) |
| Entertainment Value | 中〜高(意外性はあるが、断定を避ける慎重な構成) | 非常に高い(「遺伝が努力に勝る」という強い煽り文句) |
| 5分記事適性 | 高(複数の切り口を持つ大規模メタ分析) | 高(ただし後述のとおり土台が脆弱) |
| 検索していない事の後付け捏造の有無 | **なし**(9候補すべて実在するsource_title/URLに紐付く) | **あり**(下記C-1参照) |

### C-1. Geminiに見つかった重大な問題: 検索していないのに「検索した痕跡」を捏造

Gemini Stage AのCandidate Pool中、cand_02(縦断研究)のsource_urlフィールドに以下の値が記録されていた:

```
"source_url": "https://www.mdpi.com/2227-9067/13/8/xxxx (grounding snippet referenced)"
```

`xxxx`というプレースホルダーと、`(grounding snippet referenced)`という**「groundingスニペットを参照した」という自己申告文言そのもの**がURLフィールドの中に紛れ込んでいる。しかし同じ呼び出しの`web_search_queries`は空配列、`grounding_chunks_count`は0であり、**実際には一切groundingを実行していない**。これは、タスク仕様が明示的に禁止する「検索で確認していない候補を後付けで作る」行為そのものであり、かつ「検索した」という虚偽の外形まで自ら作り出している点で、単なる不正確さより一段重い問題である。

選定されたTopic(cand_03)自体のSourceも、特定記事ではなくScienceDailyのタグ一覧ページに過ぎず、「一次Sourceを優先してResearch」という仕様の起点として成立していない。

---

## D. Stage C: Research/VFL比較表

| 観点 | Luna | Gemini 3.5 Flash-Lite |
|---|---|---|
| Research Brief文字数 | 5,778字(詳細、8観点を全て具体的に展開) | 2,427字(簡潔) |
| Primary Sources | 実在論文(DOI: 10.1037/bul0000458、PubMed ID: 39818912) | 実在するが**Stage Aで一切見つけていない**別の論文(Polderman et al. 2015, Nature Genetics) |
| Fact数(draft) | 27件 | 3件 |
| Critical Fact Coverage | 高(参加者数の単位、地域構成、報告者内訳、出生順位・性別・性格の各moderator分析まで網羅) | 低(遺伝率の一般的知見3件のみ、Stage Aの土台と接続していない) |
| Unsupported Claims | 0件相当(全FactがDOI付き一次資料に紐付く) | 0件(ただし後述の通り「検証していないのに検証済みと自称」が別の問題として存在) |
| Total Search回数(Stage C内) | Research 12回 + Verification 9回 = **21回** | **0回**(draft・verificationとも) |
| 独立検証(Verification)の結果 | 26 VERIFIED / 1 AMBIGUOUS / 0 REJECTED(実際に`scribd.com`のスキャンPDF・PubMedへ再アクセスして裏取り) | 3 VERIFIED(**ただし検索0回のまま**、verification_notesには"Confirmed against the official study..."という、実際に確認したかのような文言が並ぶ) |
| Total Cost(Stage A+B+C) | $0.3558 | $0.0151 |

### D-1. Geminiのverification記述の問題

Gemini Stage C verificationの`verification_notes`は次のような文体である(例):

> "Confirmed against the official study by Polderman et al. (2015) in Nature Genetics (doi:10.1038/ng.3285). The meta-analysis explicitly covers 17,804 traits..."

「確認した(Confirmed against)」という、実際に一次資料へ再アクセスして裏取りしたことを示唆する文言が並ぶが、この呼び出しの`web_search_queries`は空、`grounding_chunks_count`は0である。述べられている数値(17,804 traits、2,748論文、14,558,903組の双生児、遺伝率49%)自体は、Polderman et al. (2015)という実在する著名なメタ分析の内容としてほぼ正確であり、学習データからの想起として妥当な範囲に収まっている。しかし**「検索して確認した」という体裁を取りながら実際には検索していない**という点は、Fact Ledgerの根幹である「Source上で実際に確認された」という保証を無効化するものであり、production運用における最大のリスクである(=事実として合っていても、それが「確認された」のか「もっともらしく生成された」のかを区別できない)。

---

## E. コスト計測(Stage別、$公式レート: Luna $0.20/$0.02cached/$1.20 per 1M tok + $10/1,000 web_search; Gemini 3.5 Flash-Lite $0.30/$2.50 per 1M tok + grounding 5,000件/月無料)

| Stage | Model | Input tok | Output tok | Search回数 | Token Cost | Search Cost | 合計 |
|---|---|---:|---:|---:|---:|---:|---:|
| A: Topic Selection | Luna | 57,417 | 8,924 | 6 | $0.0222 | $0.0600 | $0.0822 |
| B: Research Brief | Luna | 545 | 4,611 | 0 | $0.0056 | $0.0000 | $0.0056 |
| C: Research draft | Luna | 108,915 | 10,966 | 12 | $0.0349 | $0.1200 | $0.1549 |
| C: Verification | Luna | 77,306 | 6,321 | 9 | $0.0231 | $0.0900 | $0.1131 |
| **Luna合計** | | 244,183 | 30,822 | **27** | **$0.0858** | **$0.2700** | **$0.3558** |
| A: Topic Selection | Gemini | 391 | 2,710 | 0 | $0.0069 | $0.0000 | $0.0069 |
| B: Research Brief | Gemini | 438 | 1,271 | 0 | $0.0033 | $0.0000 | $0.0033 |
| C: Research draft | Gemini | 1,822 | 1,102 | 0 | $0.0033 | $0.0000 | $0.0033 |
| C: Verification | Gemini | 2,599 | 311 | 0 | $0.0016 | $0.0000 | $0.0016 |
| **Gemini合計** | | 5,250 | 5,394 | **0** | **$0.0151** | **$0.0000** | **$0.0151** |

Search costは分離不能な部分はなく(Search feeはtool呼び出し単位で明示的にカウント可能)、全額`OFFICIAL_API_RESPONSE`由来の実測値。`NOT_SEARCHLY_MEASURABLE`に該当する箇所はなかった。

Gemini groundingの使用量は`web_search_queries=[]`かつ`grounding_chunks_count=0`が全4呼び出しで一貫しており、月5,000件無料枠への計上も0件(実際に使っていないため課金対象外)。

Lunaのzero-base総コスト$0.3558は、MODEL-AB-01A Phase 1で計測した「事前調査済みBriefを検証するだけ」の$0.1749より**2倍以上高い**。理由は明快で、Stage Aの候補探索(6回)とStage Cの本格的なゼロからのResearch(12回)が新たに発生したため、search回数が13回→27回に倍増したこと。token costはむしろ$0.0449→$0.0858とやや増えた程度で、コスト膨張の主因は今回もsearch fee(1回$0.01固定)である。

---

## F. Topic Selection品質評価(8観点、独立評価)

| 観点 | Luna | Gemini |
|---|---|---|
| User Intent Fit | ◎ 「子育て研究」を学術研究として素直に解釈 | ○ 幅を広げすぎ、政策ニュース等まで含めた |
| Freshness | ◎ 2025年公刊のメタ分析 | △ 選定Topicの実質的な土台(Polderman 2015)は10年前の研究 |
| News Value | ◎ | ○ 見かけ上は高いが土台が脆弱 |
| Entertainment Value | ○ 意外性はあるが慎重な構成 | ◎ 煽り文句は強いが裏付けが弱い |
| Surprise/Novelty | ○ | ◎ |
| Human Interest/Curiosity | ○ | ◎ |
| Five-minute Story Depth | ◎ 複数の切り口(性別・出生順位・性格)を持つ | △ Stage Aの候補と接続しない別研究に差し替わっている |
| Source Quality/Verifiability | ◎ 実在論文への直接リンク、9候補すべて裏付けあり | ✕ 選定Topicの一次Sourceがタグ一覧ページ、別候補に検索していないのに検索した痕跡を捏造 |

**総合**: Luna **PASS**、Gemini **FAIL**(Source Quality/Verifiabilityの観点で明確な違反、これは他の観点の高評価があっても覆せない)。

## G. Research品質評価(10観点、独立評価)

| 観点 | Luna | Gemini |
|---|---|---|
| Critical Fact Coverage | ◎ 27 Fact、5領域を網羅 | △ 3 Factのみ、深さ不足 |
| Factual Accuracy | ◎ 26/27 VERIFIED | ○ 内容自体はPolderman 2015として概ね正確 |
| Numeric Accuracy | ◎ r値・SE・p値・95%CIまで正確に転記 | ○ 49%/69%/50-80%は実際の値と整合 |
| Source Quality | ◎ DOI付き一次資料 | ○ 実在論文だが土台(Stage A)と非連続 |
| Primary Source Reach | ◎ scribd.com経由で本文PDFまで到達 | ✕ 到達していない(検索0回) |
| Unsupported Claims | ◎ ほぼ皆無 | △ 内容は妥当だが「検索して確認した」という主張自体が根拠を欠く |
| Epistemic Discipline | ◎ causal_strengthを丁寧に使い分け | △ 一見丁寧だが、検証プロセス自体が虚偽 |
| Limitations記載 | ◎ 北米・西欧中心である旨など明記 | ○ 記載はあるが独自検索での確認はなし |
| Traceability | ◎ 全Factがsource_url付き、独立検証で裏取り済み | ✕ **「Confirmed」という記述に反し実際には未検証** |
| Writer Usefulness | ◎ | ○ 内容は使えなくはないが出典の信頼性が担保されない |

**総合**: Luna **PASS**、Gemini **FAIL**(Traceability/Primary Source Reachで明確な違反)。

---

## H. 最終判定

| Model | 判定 |
|---|---|
| Luna | **`COST_NOT_VIABLE`**(Topic Selection・Research品質はともにPASSだが、zero-base総コスト$0.3558は$0.05を大幅に超過) |
| Gemini 3.5 Flash-Lite | **`TOPIC_SELECTION_FAIL`**(検索していないのに検索した痕跡を捏造。Research Stageも同様の理由でRESEARCH_FAIL相当。品質失敗はコストの安さ($0.0151、$0.03以内)によって相殺されない、というMODEL-AB-01Aで確立した原則をここでも踏襲) |

---

## I. 完了報告に必須の9つの質問への回答

**1. 各モデルは「最近の子育て研究」をどう解釈し、何を検索し、最終的に何を選んだか**
Lunaは「育児行動・家族関係に関する学術研究」として素直に解釈し、`site:nih.gov`・`site:sciencedaily.com`・`site:pubmed.ncbi.nlm.nih.gov`等を対象にした20種の検索クエリ(実行6回)を発行し、最終的に「親のえこひいき(Parental Differential Treatment)」メタ分析(N=19,469)を選定した。Geminiは「学術研究〜政策ニュース〜科学ニュース」まで幅広く解釈したが、**検索を一切実行せず**(web_search_queries=[]が全呼び出しで一貫)、モデル内部知識から「遺伝vs子育て双生児研究」というトピックを選んだ。

**2. 両モデルのCandidate Pool/Shortlist/Final Selectionはどう違ったか**
Lunaは9候補(すべて実在するsource_title/URL付き)→5候補のShortlist→C1選定という、実際の検索結果に基づく絞り込みだった。Geminiは5候補(うち1件のURLに`xxxx`+「grounding snippet referenced」という捏造の痕跡)→3候補のShortlist→cand_03選定だが、選定Topicの一次Sourceは特定記事ではなくScienceDailyのタグ一覧ページであり、実質的に検索結果に基づいていない。

**3. どちらのTopic Selectionが、人間のリスナーにとってより面白いeigo-radioエピソードになるか**
表面上の煽り文句のインパクトはGeminiの「遺伝vs子育て」の方が強い。しかし、その土台(ScienceDailyのタグ一覧ページ)は実質的に存在しない一次Sourceであり、後続のResearchで別の10年前の論文(Polderman 2015)に静かにすり替わっている。Lunaの「親のえこひいき」は、断定を避けつつ複数の切り口(性別・出生順位・性格)を持つ、地に足の着いた構成であり、**実際に番組化できる土台を持っているのはLunaの方**である。Geminiの案は「面白そうに見えるが、検証すると崩れる」タイプであり、Service Policyが求める「事実の正確性をエンターテインメント性のために曲げない」という原則に反するリスクを内包している。

**4. Geminiは今回、実際にGrounding/Searchを使ったか**
**使わなかった**。Stage A・Stage C draft・Stage C verificationの計4呼び出し全てで`web_search_queries=[]`、`grounding_chunks_count=0`。1回目の実行(文字化けバグの影響下)でも0回、バグ修正後の2回目実行でも0回であり、環境要因ではなく**モデル自身がgoogle_searchツールを実質的に使わない**という、MODEL-AB-01A Phase 1と一貫した挙動が、今回のゼロベース条件下でも再確認された。加えて今回は、検索していないにもかかわらず検索した体裁を取る記述(URL内の捏造テキスト、verification_notesの"Confirmed"表現)という、より深刻な問題も新たに確認された。

**5. 各モデルのStage A+B+C合計コストはいくらか**
Luna: $0.3558(Token $0.0858 + Search $0.2700、Search回数27回)。Gemini: $0.0151(全てToken、Search $0)。

**6. Geminiは$0.03以内でProduction-candidate-viableか**
コスト単体では**Yes**($0.0151 < $0.03)。しかし品質面で`TOPIC_SELECTION_FAIL`のため、**現時点ではProduction candidateとして不採用**とすべきである。MODEL-AB-01Aで確立した「品質失敗はコストで相殺されない」という原則をここでも適用する。

**7. Lunaのzero-base品質はどの程度良いか**
非常に高い。Topic Selectionは9候補すべてが実在するSourceに紐付き、Research/VFLは27 Fact中26件が独立した再検索によりVERIFIED(1件はAMBIGUOUS、REJECTEDは0件)。数値・統計量(r値、SE、p値、95%CI)の転記精度も高く、causal_strengthの使い分けも一貫していた。ただしzero-base化によりsearch回数が13回→27回に倍増し、コストはPhase 1の$0.1749から$0.3558へとさらに悪化した。

**8. どちらのモデルがAKB48で再テストする価値があるか**
本タスクの範囲では**AKB48は実行しない**(仕様により明示的にスコープ外)。次にAKB48で再テストする価値があるとすればLunaだが、それは「品質が良いから」ではなく「コスト構造(search fee固定$0.01/回)を先に見直さない限り、AKB48で試しても同じ理由でCOST_NOT_VIABLEになることが構造的に予見できる」ため、**AKB48再テストよりも先に、Lunaのsearch回数を減らす工夫(例: 上限設定、キャッシュ、より少ない検索で足りるプロンプト設計)を検討する方が優先度が高い**、というのが本タスクの範囲内での所見である。Geminiは、今回もgoogle_searchを実質的に使わないという挙動が2回連続(Phase 1・本タスク)で確認されたため、Research用途としてはこれ以上のテーマ追加テストよりも、**そもそもなぜツールを渡しても使わないのかという原因調査(プロンプト設計・ツール宣言方法・モデル側の既定挙動)を先に行うべき**である。

**9. (上記に対応する追加所見)従来のGemini Phase 1結果・Lunaの従来Phase 1結果の扱い**
MODEL-AB-01A Phase 1のGemini結果(`ER-005-MODEL-AB-01A_phase1_report.md`)は、事前に用意されたfact-ladenなBriefを検証しただけであり、zero-base Topic Selection/Research能力の測定にはなっていなかった。当該報告書は**削除・書き換えを行わず**、本報告書をもって`INVALID_FOR_ZERO_BASE_RESEARCH_ASSESSMENT`(quality_fail相当に加えてこのラベルが追加で該当する)と追加で位置づける。同様に、Lunaの従来Phase 1結果($0.1749、13 search、品質PASS)も、zero-base Customized Research Costの測定ではない($0.1749は「既存Briefの検証コストのみ」であり、本タスクで判明したStage A/Bのコスト($0.0878)を含んでいない)ものとして扱う。

---

## J. 実行条件の確認(Acceptance Criteria対応)

- Raw User Inputは「最近の子育て研究」の一言のみで、それ以外の具体的事実は一切事前投入していない: **確認済み**(`USER_INPUT`定数、両モデルへ完全に同一のプロンプトテンプレートを使用)
- Service PolicyはLuna/Geminiで完全に同一のテキスト: **確認済み**(`SERVICE_POLICY`定数を共通使用)
- Topic Selectionプロセスはartifact上で観測可能: **確認済み**(`stage_a_topic_selection.json`にsearch_usage/grounding情報を保存)
- Candidate Pool/Shortlist/Final Selectionは保存済み: **確認済み**
- Research Brief全文は保存済み: **確認済み**(`stage_b_research_brief.json`)
- VFL全文は保存済み: **確認済み**(`stage_c_ledger_draft.json`、`stage_c_verification.json`)
- Tool/Search使用状況は保存済み: **確認済み**(raw_usage_log.jsonl、grounding_metadata)
- Stage別コストは全て実測(NOT_SEPARATELY_MEASURABLEに該当する箇所なし): **確認済み**
- 両モデルとも各Stage 1回のみ実行(best-of禁止): **確認済み**。Geminiのみ、技術的バグ(B章参照)により1回を無効化した上で1回だけ再実行しており、これは仕様が明示的に許容する「技術的失敗のみretry許容」に該当する(モデルの品質に対するbest-of選択は行っていない)
- AKB48は実行していない: **確認済み**
- Sol再実行なし: **確認済み**
- Production model / CURRENT_SPEC変更なし: **確認済み**(触れたのは本タスク専用スクリプト`er005_e2e_research_ab_01_p1.py`のみ)
- OPEN-43は`UNDER_REVIEW`(原因未確定)のまま未変更: **確認済み**
- 完了時にSTOP: 本報告書提出をもってSTOPする。AKB48実行・Sol実行・追加モデルの試行は行わない。

---

## K. 成果物一覧

- `er005_e2e_research_ab_01_p1.py` — 実行スクリプト(バグ修正済み)
- `er005_output/e2e_research_ab_01_p1/luna/` — Luna Stage A/B/C全成果物
- `er005_output/e2e_research_ab_01_p1/gemini/` — Gemini Stage A/B/C全成果物(修正後のクリーンな実行)
- `er005_output/e2e_research_ab_01_p1/gemini_run1_corrupted_ATTEMPT1/` — 文字化けバグの影響を受けた1回目実行の証跡保存(参考、不採用)
- `er005_output/e2e_research_ab_01_p1/raw_usage_log.jsonl` — 全8呼び出しの正しいコストログ
- `er005_output/e2e_research_ab_01_p1/raw_usage_log_ATTEMPT1_corrupted.jsonl` — 1回目実行時の(ログ出力先バグの影響を受けた)ログ、証跡保存
- 本報告書 `ER-005-E2E-RESEARCH-AB-01-P1_report.md`
