# ER-005-WRITER-COST-QUALITY-01 実行報告書

**タスク**: Writer工程(B1/A2) Clean Cost / Quality Baseline計測
**実行日**: 2026-08-20
**入力**: ER-005-RESEARCH-MODEL-AB-01のLuna版VFL(16 Fact)・Evidence Pack(15 Evidence)をそのまま使用。Topic Selection・Research・Source取得は再実行していない。
**Writer/Fact Checkモデル**: GPT-5.6 Luna(現行production Writer prompt構造をそのまま使用、モデルのみLunaへ差し替え)
**為替**: 1ドル=160円換算(主表示は円)

---

## 完了報告の最上段(20章の必須回答)

1. **B1 Writer Clean Costはいくらか(円)**: **0.872円**(5,837 input tok + 3,568 output tok)
2. **B1 Fact Check Costはいくらか**: **0.657円**(9,872 input tok + 1,776 output tok)
3. **B1合計はいくらか**: **1.529円**
4. **A2 Writer Clean Costはいくらか**: **0.464円**(5,700 input tok + 1,467 output tok)
5. **A2 Fact Check Costはいくらか**: **0.683円**(9,843 input tok + 1,919 output tok)
6. **A2合計はいくらか**: **1.147円**
7. **B1/A2のどちらが高かったか**: **B1の方が高い**(1.529円 vs 1.147円、+33%)。差の主因はWriter本体のoutput token量(B1: 3,568 vs A2: 1,467)。
8. **Topic Selection + Research + Writerまでの合計はいくらか**: 前段Baseline(Topic Selection 約3.0円 + Research Layer 約3.3円 = 6.3円)と合わせて、**B1版で約7.83円、A2版で約7.45円**(記事本文完成まで、Preview/Key Phrases/Comments等は含まない)。
9. **Fact Checkで重大問題は出たか**: **出ていない**。B1・A2ともに`MINOR_FIX`(各2件、いずれもMINOR severity)。数値誤り・捏造Fact・因果の過剰主張は0件。
10. **Writer工程は今後Cheap Model比較する価値があるコスト水準か**: コスト自体は既に非常に低い(記事1本あたり1円台)。Research LayerでのDeepSeek比較(ER-005-RESEARCH-MODEL-AB-01)がコスト面で明確な優位を示せなかった実績も踏まえると、Writer工程を追加でモデル比較する優先度は**現時点では低い**と考えられる(下記L章で詳述)。

---

## A. 入力条件

- VFL: `er005_output/research_model_ab_01/luna/vfl.json`(16 Fact、全件source_id/evidence_id付き)
- Evidence Pack: `er005_output/research_model_ab_01/luna/evidence_pack.json`(15 Evidence item)
- 上記をそのまま機械的に再フォーマットしたテキストLedgerをWriterへ渡した(新しいFactの追加・削除なし。変換ロジックは`build_ledger_text_from_vfl()`、コード上で確認可能)
- Primary Source全文(論文本文)はWriterへ渡していない(仕様6章の規定通り)
- Writer prompt構造(COMMON_BLOCK_TEMPLATE、B1_B_DIRECT_INSTRUCTION、A2_KAI1_INSTRUCTION)は`er003_v1_n3_01_articles_generate.py`から**無変更でそのままimportして使用**した

**Spoken-first Number Treatmentに関する重要な留保**: 今回のLedgerは、Evidence Pack型Research Layer(ER-005-RESEARCH-LAYER-REDESIGN-01)由来のため、production本来のLedgerが持つ`number_classification`(ANCHOR/SUPPORTING/DISPENSABLE)・`exactness_requirement`(EXACT_REQUIRED/APPROXIMATE_OK/DIRECTION_ONLY)の個別タグを含んでいない。このため、Spoken-first原則のうちタグ参照を前提とするF・G項目は今回は実質的に不使用となり、A〜E(数字を恣意的に削らない、方向性優先可、丸め可、同時比較数字は2つ以内、単位連続を避ける)という一般原則のみがWriterの編集判断に委ねられた。この点は、Writer出力の数値密度を評価する際の重要な前提条件としてC章で扱う。

---

## B. B1記事(全文)

> # When Family Conflict and Screen Time Move Together in Preschool Years
>
> For preschool children, screen time is only one part of daily life. A 2026 study published in *Frontiers in Psychology* asks whether it is also connected with the relationship between children and their mothers.
>
> The study followed children aged 3 to 6 in Fuyang, Anhui, China. It used three surveys, with four months between each one. The first survey included 619 children. The final analysis included 532 children, with mothers answering the questionnaires.
>
> The researchers measured two sides of the parent-child relationship: closeness and conflict. They also measured each child's average daily screen time.
>
> Finally, they looked at two types of behavior problems. One type involves difficulties turned inward, such as emotional and peer problems. The other involves behavior seen outwardly, such as hyperactivity, inattention, and conduct problems.
>
> The main pattern was this: a more conflictual relationship was linked with more screen time at a later point. More screen time was then linked with both types of behavior problems. Conflict was also directly linked with those problems.
>
> In the study's statistical model, screen time accounted for part of the connection between conflict and later behavior problems. It did not account for the whole connection.
>
> A closer parent-child relationship was linked with fewer behavior problems. However, closeness did not show a significant path to later screen time.
>
> ### Point One: "Behavior problems" is not one single picture
>
> The study separated internalizing problems from externalizing problems. That matters because children may show emotional or peer difficulties, or they may show hyperactivity, inattention, or conduct problems. Looking at both gives a wider picture than simply counting difficult behavior.
>
> ### Point Two: A pattern, not a final cause
>
> The study followed children over time, but it was short and came from one region. The main measures were reported by mothers, and starting levels of screen time and behavior were not included in the model. So the findings show a time-linked pattern—not proof that conflict causes screen use or that screen use causes behavior problems.
>
> ## In one line…
>
> When parent-child conflict is higher, screen time and child behavior problems may become connected—but this study shows an association, not a simple cause-and-effect story.

**Metrics**: 総語数332語(intro 211 / Point One 39 / Point Two 57 / In One Line 25)、平均文長13.6語、最長文28語。Point One/Twoともに目標範囲(30〜60語)内。

---

## C. A2記事(全文)

> # When Family Tension Meets Screen Time: A Study of Young Children
>
> A quiet question at home may become an important research question:
>
> What happens when a young child often has conflict with a parent?
>
> A 2026 study looked at this question through family relationships, screen time, and children's behavior.
>
> The study followed children aged 3 to 6 in Fuyang, Anhui, China. The final analysis included 532 children. Their mothers answered questions about the children and their family relationships.
>
> The researchers collected information three times. Each check was four months apart.
>
> They asked about two parts of the parent-child relationship: closeness and conflict. They also asked about the children's daily screen time and behavior problems.
>
> The main result was clear in its direction.
>
> When mothers reported more conflict earlier in the study, the children tended to have more screen time later. More screen time was also linked with more behavior problems.
>
> These problems included emotional and peer difficulties. They also included hyperactivity and conduct problems.
>
> Conflict was linked with these problems in another way, too. The study found a direct link between conflict and later behavior problems.
>
> This means screen time explained only part of the connection. It was not the whole story.
>
> The researchers did not say that conflict definitely caused screen time, or that screen time definitely caused behavior problems. Their study showed a pattern over time.
>
> ### Point One: Warmth and conflict were not mirror images
>
> A closer parent-child relationship was linked with fewer behavior problems. But closeness did not significantly predict later screen time. So, feeling close and having conflict were not simply two opposite roads to the same result.
>
> ### Point Two: The study shows a path, not a final answer
>
> The research lasted about eight months and took place in one city. Mothers also reported the main information. The authors noted that earlier levels of screen time and behavior were not included in the model, so the pattern cannot be read as proof of cause and effect.
>
> ## In one line…
>
> Family conflict, screen time, and children's behavior appeared to be connected over time—but this study shows a possible path, not a simple verdict.

**Metrics**: 総語数319語(intro 213 / Point One 35 / Point Two 47 / In One Line 24)、平均文長12.0語、最長文29語。Point One/Twoともに目標範囲内。

**B1とA2の独立性の確認**: 両記事は同一VFLから完全に独立生成されており(15章の規定通り、一方から他方への変換は行っていない)、構成・導入・語彙選択が明確に異なる別のnarrativeになっている(例: A2は導入で読者への直接的な問いかけを使うが、B1は使わない)。

---

## D. Fact Check結果

| 記事 | Verdict | Issue数 | 主な指摘 |
|---|---|---|---|
| B1 | `MINOR_FIX` | 2件(いずれもMINOR) | ①媒介効果("screen timeが関連の一部を説明")をLedger上のambiguity(p値と95%信頼区間の不一致)に触れず断定的に要約している ②クラス/学校の入れ子構造という限界の欠落 |
| A2 | `MINOR_FIX` | 2件(いずれもMINOR) | ①同様に媒介効果を「明確な結果」と表現し統計的曖昧さに触れていない ②同様にクラス/学校の入れ子構造の限界が欠落 |

**この結果の評価**: 両記事とも、数値の誤転記・捏造Fact・因果の過剰表現(「causes」「proves」等の強い言い切り)は無く、むしろ本文中で明示的に相関と因果を区別する表現("linked with"、"not proof that..."、"a pattern, not a final cause"等)を一貫して使っていた。Fact Checkが指摘した2件は、いずれも「Ledgerの`claim`本体は正しく反映しているが、`ambiguity`フィールドに記録された統計的な留保までは反映していない」という、より踏み込んだ精度の指摘であり、Writer出力の信頼性を損なう重大な問題ではない。むしろ、ER-005-RESEARCH-MODEL-AB-01でLuna自身が検出した「p<0.05だが95%CIは0をまたぐ」という原論文内部の統計的不整合を、Fact Checkが独立してもう一度捕捉できたことは、VFL/Evidence Pack主体・Web検索不使用のFact Checkでも実用的な検証能力があることを示している。

---

## E. Writer出力の品質確認(14章)

| 観点 | B1 | A2 |
|---|---|---|
| VFLとのFact trace | 良好(サンプルサイズ619→532、3時点・4か月間隔、closeness/conflict、内在化/外在化の分類、方向性、いずれもLedgerと一致) | 同左 |
| Fact Check結果 | MINOR_FIX(2件、severity MINOR) | MINOR_FIX(2件、severity MINOR) |
| 数値保持 | 619/532、3時点/4か月間隔を保持。個別のβ値・p値・95%CIはNarrativeへ持ち込まず、方向性("linked with more/fewer")で表現 | 同様の傾向。加えて「約8か月」という、4か月×2区間から導出した期間表現を使用(Ledgerに明示されていない計算だが、算術的に導出可能で意味を変えていない) |
| causal discipline | 高い。"linked with"を一貫使用し、Point Twoで明示的に因果解釈を否定 | 高い。同様の一貫性 |
| Level適合性 | Spoken-first・adult tone・自然な文体を維持しつつB2ほど複雑ではない構造(平均文長13.6語) | よりシンプルな導入(問いかけ形式)、one-idea-at-a-timeの傾向が明確(平均文長12.0語) |
| articleとして自然か | 自然。ニュースの語り口を保っている | 自然。A2らしい平易さを保ちながら子供向けにはなっていない |
| 5分前後のニュース素材としての厚み | Full Story単体は約2.5分相当(332語)。Preview/Key Phrases/Comments等は本タスクの対象外のため、完成尺への到達は別工程で判断が必要 | Full Story単体は約2.4分相当(319語)。同上 |

**Spoken-first原則(A〜E)の遵守状況**: 個別のβ値・p値・95%信頼区間はどちらの記事にも直接引用されておらず、方向性中心の記述("more conflict → more screen time → more behavior problems")に置き換えられている。これはA〜E原則(特にB「方向性優先可」、D「同時比較数字は2つ以内」)に沿った編集判断であり、F・G(タグ参照)が使えない条件下でも、Writerが数字の精度を適切に抑えた記事を書けることを確認できた。

---

## F. Cost計測(11・19章、円建て)

| 工程 | B1 | A2 |
|---|---:|---:|
| Writer | 0.872円(5,837 in / 3,568 out) | 0.464円(5,700 in / 1,467 out) |
| Fact Check | 0.657円(9,872 in / 1,776 out) | 0.683円(9,843 in / 1,919 out) |
| **Level合計** | **1.529円** | **1.147円** |

**Retry/Fallback**: 両記事とも1回で構造検証(`STRUCTURE_PASS`)に成功し、technical retryもfallbackも発生しなかった。**Clean Cost = Actual Cost**(差はゼロ)。

**記事本文完成までの累積コスト**(13章のBaseline、Topic Selection 約3.0円 + Research Layer 約3.3円 = 6.3円と合算):

| Level | Topic Selection + Research | Writer + Fact Check | **合計** |
|---|---:|---:|---:|
| B1 | 6.3円 | 1.529円 | **7.829円** |
| A2 | 6.3円 | 1.147円 | **7.447円** |

---

## G. Human Review Artifact

- B1記事全文: 本報告書B章、および`er005_output/writer_cost_quality_01/b1/article.md`
- A2記事全文: 本報告書C章、および`er005_output/writer_cost_quality_01/a2/article.md`
- VFLとのFact trace: `er005_output/writer_cost_quality_01/ledger_text.txt`(Writerへ渡したLedger全文)
- Fact Check結果: `er005_output/writer_cost_quality_01/{b1,a2}/fact_check.json`
- Writer呼び出し詳細(prompt全文含む): `er005_output/writer_cost_quality_01/{b1,a2}/prompt.txt`、`writer_attempts.json`

---

## H. 受入条件確認(21章)

- 同一Luna版VFL/Evidence Packを使用: **確認済み**(ER-005-RESEARCH-MODEL-AB-01のluna/vfl.json・evidence_pack.jsonをそのまま使用)
- Research再実行なし: **確認済み**
- Source全文をWriterへ再投入しない: **確認済み**(Ledgerテキストのみ渡した)
- B1/A2は独立生成: **確認済み**(15章の規定通り、一方から他方への変換なし)
- Writer単体コストを分離: **確認済み**(F章)
- Fact Checkコストを分離: **確認済み**(F章)
- Fact CheckはVFL/Evidence Pack主体: **確認済み**
- Web Search不使用: **確認済み**(全呼び出しで`web_search_call_count=0`をコストログで実測)
- Clean CostとActual Costを分離: **確認済み**(両記事ともretryなし、Clean=Actual)
- 円表示(160円/USD): **確認済み**
- Human Review用記事全文あり: **確認済み**(B・C章)
- Production/CURRENT_SPEC変更なし: **確認済み**(触れたのは`er005_writer_cost_quality_01.py`のみ。production側の`er003_v1_n3_01_articles_generate.py`等は読み取りのみでimportし、一切変更していない)

## I. Stop条件

B1 Writer×1 → B1 Fact Check×1 → A2 Writer×1 → A2 Fact Check×1 → Cost集計 → Human Review artifact → Reportが完了したため、ここでSTOPする。Support生成・TTSへは進まない。

---

## J. 参考: Writer工程のCheap Model比較の要否について

Writer+Fact Checkの合計コストは、B1で1.529円、A2で1.147円と、既に記事1本あたり2円未満という水準にある。ER-005-RESEARCH-MODEL-AB-01でDeepSeekがLunaに対して明確なコスト優位を示せなかった実績(むしろ実費ベースでは高くなるリスクがあった)を踏まえると、絶対額が小さいWriter工程で追加のモデル比較を行っても、得られる削減余地は限定的である可能性が高い。次に取り組む価値があるとすれば、モデル比較よりも、Preview/Key Phrases/Comments等の残りのSupport生成工程を含めた「記事1本のEnd-to-End完成コスト」の実測の方が優先度が高いと考えられる(ただしこれは本タスクの範囲外の所見であり、実行はしていない)。

---

## K. 成果物一覧

- `er005_writer_cost_quality_01.py` — 実行スクリプト
- `er005_output/writer_cost_quality_01/ledger_text.txt` — Writerへ渡したVerified Fact Ledgerテキスト
- `er005_output/writer_cost_quality_01/b1/` — B1記事・Fact Check結果・prompt・attempts
- `er005_output/writer_cost_quality_01/a2/` — A2記事・Fact Check結果・prompt・attempts
- `er005_output/writer_cost_quality_01/run_summary.json` — 両Levelの実行サマリ
- `er005_output/writer_cost_quality_01/raw_usage_log.jsonl` — 全4呼び出しのコストログ
- 本報告書 `ER-005-WRITER-COST-QUALITY-01_report.md`
