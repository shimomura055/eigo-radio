# ER-005-SUPPORT-COST-QUALITY-01 実行報告書

**タスク**: Support Content(Preview/Key Phrases/Comment 1-4)Clean Cost/Scope Boundary計測
**実行日**: 2026-08-20
**入力**: ER-005-WRITER-COST-QUALITY-01のB1/A2記事全文+VFL/Evidence Packベースのledger text。Topic Selection・Source取得・Research・Writerは再実行していない。
**モデル**: GPT-5.6 Luna固定(モデル比較なし)
**為替**: 1ドル=160円換算(主表示は円)

---

## 完了報告の最上段(16章の必須回答)

1. **Writerですでに生成済みだったcomponentは何か**: Title、Full Story(Main Story本文)、Point One、Point Two、In One Line(いずれもER-005-WRITER-COST-QUALITY-01で完成済み)
2. **今回新たに生成したSupport componentは何か**: Preview、Key Phrases(5件、Strategy L+Canonicalization)、Comment 1〜4(B1/A2それぞれ独立)
3. **二重生成は回避できたか**: **回避できた**。Full Story/Point One/Two/In One Lineは一切再生成していない(下記A章のScope Audit参照)
4. **B1 Support生成+Fact Checkはいくらか(円)**: **2.030円**(Support本文0.485円 + Key Phrases 1.324円 + Fact Check 0.220円)
5. **A2 Support生成+Fact Checkはいくらか**: **2.860円**(Support本文0.526円 + Key Phrases 2.061円 + Fact Check 0.273円)
6. **記事+Support完成までのB1累積コストはいくらか**: **9.859円**(Topic Selection 3.0円 + Research Layer 3.3円 + B1 Writer/Fact Check 1.529円 + B1 Support 2.030円)
7. **記事+Support完成までのA2累積コストはいくらか**: **10.307円**(同上 + A2 Writer/Fact Check 1.147円 + A2 Support 2.860円)
8. **重大なFact/Level問題はあったか**: **無かった**。B1・A2ともSupport Fact Check verdict=`PASS`、issue 0件。
9. **Spoken-first Number Treatmentタグ欠落は次工程へのBlocking issueか**: **現時点ではBlocking issueではない**が、OPEN ITEMとして明記する(下記H章)。今回のSupport生成は、Article本文にすでに反映済みの数値密度(方向性優先、精密値を持ち込まない)をそのまま引き継ぐ形で機能しており、タグの欠落によるSupport側の実害は確認できなかった。ただしTTS化以降、Comment等で新たに数値に言及する設計変更が入る場合は、再度検討が必要。
10. **次にTTS込みEnd-to-End Cost計測へ進めるか**: **進める水準にある**。B1で約9.86円、A2で約10.31円という、テキストEpisode完成までの実測値が確定した。目標の16円以内(Customized Episode総変動費)に対し、TTS/ASR/Audio QAに残された予算はB1で約6.14円、A2で約5.69円となる。

---

## A. Scope Audit(2章、CURRENT_SPEC.mdとの突き合わせ)

CURRENT_SPEC.mdの「全体構造(11パート)」定義(A2/B1共通、`DECIDED`、ER-003-A2-STRUCT-02〜04): `Preview→Key Phrases→Comment1→Full Story Part1→Comment2→Full Story Part2→Comment3→Point One→Point Two→Comment4→In One Line`

| Component | 分類 | 状態 |
|---|---|---|
| Title | A(Writer完成済み) | ER-005-WRITER-COST-QUALITY-01で生成済み、再生成せず |
| Full Story(Main Story) | A(Writer完成済み) | 同上。ただしPart1/Part2への機械的分割(非LLM)は本タスクで実施(下記参照) |
| Point One | A(Writer完成済み) | 同上、再生成せず |
| Point Two | A(Writer完成済み) | 同上、再生成せず |
| In One Line | A(Writer完成済み) | 同上、再生成せず |
| Preview | B(Support工程で新規生成) | 本タスクで生成 |
| Key Phrases | B(Support工程で新規生成) | 本タスクで生成(Strategy L + Canonicalization) |
| Comment 1〜4 | B(Support工程で新規生成) | 本タスクで生成 |
| Full Story Part1/Part2分割 | **C(仕様上どちらに属するか曖昧)** | 下記参照 |

**C分類の扱い**: 「Full Story Part1/Part2への分割」は、新しい文章を生成する工程ではなく(Writer出力のテキストをそのまま2つに割るだけ)、かつComment 2(Part1→Part2間に挿入)の生成に先立って必ず必要な構造決定でもあるため、厳密には「純粋なWriter完成物」でも「新しいSupport文章生成」でもない、中間的な処理である。CURRENT_SPEC.mdの規定(「機械的な50:50分割は禁止。意味上の転換点を優先」)に従い、production既存の`split_article_text()`(`er003_v1_n3_01_scaffold_generate.py`、非LLM・段落単位の語数バランスによる分割ロジック、無変更で再利用)をそのまま適用した。**新しいLLM呼び出しは発生しておらず、コストは$0**。この分割結果自体はB1/A2で独立(それぞれ自身のFull Story本文から独立して分割)。

**二重生成の回避確認**: Support生成に使った`run_b1_scaffold`/`run_a2_scaffold`関数は、Comment生成時にFull Story Part1/Part2やPoint本文をcontextとして「参照」するのみで、それらの本文自体を再生成する呼び出しは一切含まれていない(関数のコード上、Comment/Previewの生成呼び出しのみが行われる)。

---

## B. 使用したProduction機構(無変更でimport)

- `er003_v1_n3_01_scaffold_generate.py`: `split_article_text()`(非LLM分割)、`run_b1_scaffold()`/`run_a2_scaffold()`(Comment/Preview生成の呼び出し構造)
- `er003_v1_b1_scaffold_01_generate.py`: B1の`COMMENT_1〜4_ROLE`/`PREVIEW_ROLE`/`SUPPORT_ENGLISH_PRINCIPLE`/`SUPPORT_PROHIBITIONS`(役割定義・禁止事項、文言は無変更)
- `er003_v1_iran01_a2_generate.py`: A2の`COMMENT_1・2・4_ROLE`/`PREVIEW_ROLE`(同上)
- `er003_v1_n3_01_scaffold_generate.A2_COMMENT_3_ROLE_N3`: A2 Comment 3専用role(N3-01で新設、Point内容の軽い先出しを許容する版)
- `er003_b1_p2_keywords.py` / `er003_key_words_production.py` / `er003_key_words_canonicalization.py`: Key Phrase選定(Strategy L)+Canonicalizationの全ロジック(schema・developer message・QA 11フィールド、無変更)

**モデルのみの差し替え方法**: `b1s.run_support_text`/`a2gen.run_support_text`は呼び出し時にモジュール変数`MODEL`を参照する実装のため、スクリプト側で`b1s.MODEL = "gpt-5.6-luna"`/`a2gen.MODEL = "gpt-5.6-luna"`を代入するだけでLunaへ切り替わった(production側ファイル自体は一切編集していない)。Key Phrase選定・Canonicalizationは、`prod.make_production_selector_fn()`/`kc.make_canonicalization_fn()`がもともと`model`引数を明示的に受け取れる設計だったため、呼び出し時に`model="gpt-5.6-luna"`を渡すだけで済んだ。

**Web Search不使用の確認**: 全呼び出しでコストログの`web_search_call_count=0`を実測確認。Key Phrase選定・CanonicalizationはPrimary Source側の設計自体が`uses_web_search_tool = False`(production既存コードのコメントで明記)。

---

## C. 生成結果(Human Review、抜粋)

### B1 Support(English)

- **Preview**: "This episode looks at the links among family conflict, screen time, and behavior problems in the preschool years. ... By the end, you will understand what the researchers were trying to find out and how to read the results carefully."
- **Comment 1**(Listening Focus): "Listen for what the researchers measured and how they studied the relationship between screen time and children's relationships with their mothers."
- **Comment 2**(Mid-story Recovery + Next Question): "The study is looking at whether conflict between children and their mothers is related to how much screen time the children have. Next, listen for how screen time and conflict are connected with children's behavior problems."
- **Comment 3**(Story Meaning + Bridge): "The study shows links among the relationship between children and their mothers, screen time, and behavior problems. Next, we will look more closely..."
- **Comment 4**(Point Recovery + Bridge): "The study looks at more than one kind of behavior, and its results show a pattern over time rather than proving cause and effect. Now, let's bring these points together in the closing summary."

### A2 Support(Japanese)

- **Preview**: "今回のニュースは、幼い子どもの家庭での様子を、時間をおいて調べた研究についてです。...研究の結果と、その結果から言えること、言えないことを聞いていきます。"
- **Comment 1**: "このあと、親とのもめごとと、子どもの画面時間や行動の問題がどう関係するのかに注目してください。"
- **Comment 2**: "ここまでで、この研究は親子の衝突と、子どもの画面時間や行動の問題の関係を調べたものだと分かりました。では、親子の衝突が多いと、その後の画面時間や行動にどんな関係が見られたのでしょうか。"
- **Comment 3**: "この研究は、親子の対立、子どもの画面を見る時間、行動の問題が、時間の中でどのようにつながっていたかを調べました。親子関係の近さと対立は分けて考える必要があり、研究結果も一つの手がかりとして読むことが大切です。"
- **Comment 4**: "ここまでの話から、親子の近さと、問題行動や画面時間との関係は、単純に同じ形ではないことが分かります。また、この研究だけで原因まで決めることはできません。それでは、記事の内容を英語でまとめて聞いてみましょう。"

いずれも、Point One/Twoの結論を先出ししていない、新しいFactを追加していない、adult toneを維持している点を確認した。

### Key Phrases(各5件、全項目11 QAフィールドPASS)

| Level | Key Phrase | 日本語gloss |
|---|---|---|
| B1 | account for | 一部を説明する・占める |
| B1 | conflictual relationship | 葛藤の多い関係 |
| B1 | internalizing problems | 内向化問題 |
| B1 | externalizing problems | 外向化問題 |
| B1 | association | 関連・相関 |
| A2 | mirror image | 鏡像、単純な裏返し |
| A2 | conduct problem | 行動上の問題 |
| A2 | not the whole story | それがすべてではない |
| A2 | explain only part | 一部しか説明しない |
| A2 | significantly predict | 統計的に有意に予測する |

B1/A2で完全に別々の本文から独立選定されており(B1 Key PhraseのA2への流用、逆方向とも無し)、CURRENT_SPEC.mdの規定(「A2最終本文から改めて選定する」「B1本文確定後、B1自身の本文から選定する」)と一致する。

---

## D. Support Fact Check結果

| Level | Verdict | Issue数 |
|---|---|---|
| B1 | `PASS` | 0 |
| A2 | `PASS` | 0 |

B1 summary: 「Support全体に、ArticleおよびVerified Fact Ledgerと不一致する主張、数値の誤り、因果関係の過度な断定、新規Factの追加、意味ズレは見られません。」
A2 summary: 「未記載の事実、数値の誤り、因果の過度な断定、意味のズレ、Level不適合は確認されませんでした。」

Writer段階のFact Check(B1/A2ともMINOR_FIX、各2件)と異なり、Support段階では0件だった。これはSupport(Preview/Comment)が、記事本文で既に確定した内容を要約・橋渡しするだけの役割であり、Article自体が持つ細かい統計的ニュアンス(原論文内部の不一致等)にまで踏み込んでいないためと考えられる(Support Fact Checkの対象範囲がArticle本文より狭いことの自然な帰結であり、チェックが甘いことを意味しない)。

---

## E. Cost計測(10章、円建て)

| 工程 | B1 | A2 |
|---|---:|---:|
| Support本文(Preview+Comment1〜4、5 call) | 0.485円 | 0.526円 |
| Key Phrases(selection+canonicalization、2 call) | 1.324円 | 2.061円 |
| Support Fact Check(1 call) | 0.220円 | 0.273円 |
| **Level合計** | **2.030円** | **2.860円** |

**Retry/Fallback**: 全呼び出しが1回で成功し、technical retry・fallbackとも発生しなかった。**Clean Cost = Actual Cost**。

**B1/A2のコスト差の主因**: Key Phrase selection段階の出力トークン量の差(B1: 4,743 tok、A2: 6,467 tok)。A2記事は日本語Support中心のため、Key Phrase selection自体は英語記事(A2本文)を対象にしているが、生成過程でのreasoning token消費がB1よりやや大きかった(自然なばらつきの範囲)。

---

## F. 累積コスト更新(11章)

| 工程 | B1 | A2 |
|---|---:|---:|
| Topic Selection(共通) | 3.0円 | 3.0円 |
| Research Layer(共通) | 3.3円 | 3.3円 |
| Writer + Fact Check(Level固有) | 1.529円 | 1.147円 |
| Support + Key Phrases + Fact Check(Level固有) | 2.030円 | 2.860円 |
| **累積合計(テキストEpisode完成まで)** | **9.859円** | **10.307円** |

**12章の規定に基づく確認**: 上記はCustomized Daily Deliveryの前提(ユーザー1人にはB1またはA2のいずれか1 Levelのみ提供)に従い、Level別に算出した。B1とA2の両方を1ユーザーの変動費として合算していない。

---

## G. 技術的なログ表示上の注意(透明性のための開示)

Key Phrase selection/canonicalizationの2呼び出しについて、`cl.logging_context()`をfactory関数の生成時点(実際のAPI呼び出しより前)でラップしてしまったため、コストログ上の`theme`/`stage`フィールドが`null`で記録された(実際の呼び出し自体・トークン数・費用計算には一切影響なし。呼び出し順序とtoken使用量パターンから、どの呼び出しがどのstageに対応するか一意に特定できることを確認済み)。F章までのコスト集計は、正しく対応付けた値を使用している。次回以降、同種の計測を行う場合はこの点を修正する。

---

## H. OPEN ITEM: Spoken-first Number Treatmentタグ欠落(13章)

ER-005-WRITER-COST-QUALITY-01で報告した通り、今回のEvidence Pack型VFLには`number_classification`(ANCHOR/SUPPORTING/DISPENSABLE)・`exactness_requirement`(EXACT_REQUIRED/APPROXIMATE_OK/DIRECTION_ONLY)の個別タグが存在しない。

**今回のSupport生成での影響評価**: Support(Preview/Comment)は、そもそも新しい数値を持ち込まない設計(`SUPPORT_PROHIBITIONS`に「本文にない新しい具体的Factを追加しない」と明記)であり、実際に生成されたPreview/Commentにも個別の数値(サンプルサイズ・β値等)は一切含まれていなかった(方向性中心の記述に終始)。そのため、**今回の範囲ではタグ欠落による実害は確認されなかった**。

**Blocking issueかどうかの判断**: 現時点ではBlockingではない。ただし、今後Comment等で数値への言及を許容する設計変更が入る場合、またはTTS工程でNumber Treatment分類(既存productionの`sf1`/`sf1r1`モジュールが前提とする分類体系)を利用する箇所がある場合は、Evidence Pack型VFLへタグを後付けするか、Number Treatment分類を別工程として追加するかの検討が必要になる。本タスクでは仕様変更を一切行っていないため、この判断は次工程(TTS)の設計時に持ち越す。

---

## I. 受入条件確認(17章)

- CURRENT_SPEC等SoTでScope確認: **確認済み**(本報告書A章)
- Writer生成済みcomponentを再生成しない: **確認済み**(Title/Full Story/Point One/Two/In One Line、一切再生成せず)
- B1/A2は独立処理: **確認済み**(それぞれ自身の記事・Key Phraseを独立生成)
- Web Searchなし: **確認済み**(`web_search_call_count=0`実測)
- Primary Source全文再投入なし: **確認済み**(Article本文+Ledgerテキストのみ使用)
- Support生成コスト分離: **確認済み**(E章)
- Support Fact Checkコスト分離: **確認済み**(E章)
- Clean/Actual Cost分離: **確認済み**(両者とも差なし、retryゼロ)
- 円表示: **確認済み**
- Customized DeliveryはB1 OR A2で評価: **確認済み**(F章、合算していない)
- Human Review Artifactあり: **確認済み**(C章、および成果物ファイル)
- Production/CURRENT_SPEC変更なし: **確認済み**(触れたのは`er005_support_cost_quality_01.py`のみ。productionモジュールは読み取り専用importとモジュール変数の実行時上書きのみで、ファイル自体は無変更)

## J. Stop条件

Writer/Support scope audit → B1未生成Support → A2未生成Support → Support Fact Check → Clean/Actual Cost計測 → 累積Cost更新 → Human Review Artifact → Reportが完了したため、ここでSTOPする。TTSへは進まない。

---

## K. 成果物一覧

- `er005_support_cost_quality_01.py` — 実行スクリプト
- `er005_output/support_cost_quality_01/b1/` — B1 Support texts、Key Phrases、Fact Check結果
- `er005_output/support_cost_quality_01/a2/` — A2 Support texts、Key Phrases、Fact Check結果
- `er005_output/support_cost_quality_01/run_summary.json` — 両Levelの実行サマリ
- `er005_output/support_cost_quality_01/raw_usage_log.jsonl` — 全16呼び出しのコストログ
- 本報告書 `ER-005-SUPPORT-COST-QUALITY-01_report.md`
