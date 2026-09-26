# old_vs_new_comparison.md — 旧記事との違い(事実ベース、断定なし)

## 1. small_bag(「小さいバッグがまた流行?」)

- 旧記事: `er014_output/user_test_news_light_01/tiny_bags/`
  (USER-TEST-NEWS-LIGHT-TOPIC-01、生成2026-09-17、Family A/N3
  「Full Ledger全投入」方式 = `er003_v1_n3_01_articles_generate.
  run_one_pattern()`がVerified Fact Ledger[17 Facts]から直接A2/B1本文を
  1回のWriter呼び出しで生成。Storyline決定・B3 Fact選定の段は無い)。
- 新記事: `er019_output/family_x_b3_diversity_trial_01/small_bag/run_01/`
  (NEWS-FAMILY-X-B3-DIVERSITY-TRIAL-01、Storyline+B3→Selected Brief→
  JA Writer O/R1/R2→Advanced→Standard。入力Ledgerは旧記事と完全に
  同一ファイル[sha256=d07b52fa...、再利用・再Researchなし])。

### 1-1. 以前使ったFact / 今回使ったFact

| | 使用Fact数/全体 | 使用Fact ID |
|---|---|---|
| 旧記事(Family A、全投入) | ほぼ全17件相当を本文内で言及(F001系反証・F003 Coach/Fendi・F005・F006/F009系媒体差・F010系ブランド列挙・F011小売44%・F012 Chanel完売・F013 152%増・F015検索倍増・F016/F017セレブ言及、を全てMain Story/Point内に配置) | F001〜F013・F015〜F018相当(17件中ほぼ全件を本文に反映) |
| 新記事(Storyline+B3) | 3/17件 | F004、F006、F007 |

### 1-2. 削られたもの/追加されたもの

- **削られたもの(新記事で不採用)**: 具体的な数字を伴う補強Fact
  (152%増[F013]、小売44%増[F011]、検索倍増[F015]、Chanel完売[F012]、
  セレブ画像がItバッグを作る[F016/F017]、Coach/Fendi・Prada/Loewe等の
  ブランド列挙[F003/F005/F009/F010/F018])。B3の4テスト適用結果
  (`storyline_b3/fact_selection_evidence.json`)では、これらは
  「F004/F006/F007と役割が重複する」「中心Storylineの理解に必須では
  ない」という理由で除外されている。
- **追加されたもの**: 新記事側で完全新規のFactは無い(新規Researchを
  行っていないため、Ledger外のFactは存在しない)。ただし新記事は
  「大きいバッグと小さいバッグの役割分担(荷物係/演出係)」という
  比喩的枠組みを本文中で明示的に展開しており、これは旧記事の並列列挙
  スタイルには無い構成上の違いである(Ledgerにない新事実の追加ではなく、
  既存Factの解釈・比喩表現の追加)。

### 1-3. 話の中心の変化

- 旧記事の中心: 「tiny bagsは本当に流行っているのか?」という検証型の
  問いに対し、複数のカウンターエビデンスを提示しながら「単純な流行では
  ない」という限定的結論へ着地する構成(反証多め)。
- 新記事の中心: 「ミニバッグと大型バッグは対立ではなく役割分担」という
  単一のStoryline(`selected_storyline`)を最初から掲げ、そのStorylineに
  必要な最小Factだけで一貫して説明する構成。

### 1-4. 冗長性・Fact stuffing

- 旧記事(A2、444語)は新記事(A2、352語)より約26%長く、数値の異なる
  複数のFact(152%、44%、doubled等)が短い記事内に並び、個々の数字の
  文脈(何のシェア、いつの調査か)を毎回簡潔に説明する必要があり、
  情報密度が高い(Fact stuffingの傾向が見られる、と言えるだけの根拠は
  ある: 1記事あたりのFact言及数が旧17件相当 vs 新3件)。
- 新記事はFact数が絞られている分、同じFactの意味(F004: 併存/F006:
  ELLEの評価/F007: なぜ注目されるか)を複数の言い回しで繰り返し説明する
  傾向がある(例: 「大容量バッグは収納を担当し、ミニバッグは視線と
  ムードを担当する」という趣旨を、本文後半で3回言い換えている)。

### 1-5. Story coherence / 読み物としての魅力(事実ベースの所見、断定なし)

- 新記事は単一の比喩(荷物係/演出係)で本文全体が一貫しており、
  Point One/Point Twoも同じ比喩を継続利用している。
- 旧記事は複数のカウンターエビデンスを並べる分、「事実確認記事」としての
  性格が強く、単一の比喩や結論への収束は薄い。
- どちらが「進化した」かは本Trialのみでは判断できない(用途[検証型
  ファクトチェック記事 vs 単一の切り口で聞かせる記事]が異なるため、
  単純比較は困難)。

## 2. hormuz(ホルムズ海峡)

**新記事はAdvanced段でLedger Deviation MAJOR(STOP)となり、Advanced/
Standard本文が存在しない**(詳細は`NEWS-FAMILY-X-B3-DIVERSITY-TRIAL-01_
REPORT.md`参照)。そのため本文全文同士の比較はできないが、JA R2
(`hormuz/run_01/ja_writer/revision2.md`、Advanced/Standardの入力元)と、
比較可能な旧記事(`er003_output/en_direct_vfl_02/ADD03/article.md`、
Full Ledger[HF-001〜012、12件]から1回のWriter呼び出しで直接生成する
旧アーキテクチャ、LEDGER_COMPLIANT/PASS確定済み)との間で、以下が
観察できた。

### 2-1. 以前使ったFact / 今回使ったFact

| | 使用Fact数/全体 | 使用Fact ID |
|---|---|---|
| 旧記事(Full Ledger直接投入) | 12/12件(HF-001〜HF-012、IMO決議・撤回後の記者発言まで含めほぼ全件を本文に反映) | HF-001〜HF-012 |
| 新記事(Storyline+B3、JA R2まで) | 3/12件 | HF-002、HF-007、HF-009 |

### 2-2. 削られたもの

- IMO理事会の決議(HF-001)、20%案の制度設計の欠如(HF-003)、貨幣換算の
  試算(HF-004)、Brent/WTIの詳細な日中高値・安値・清算値の内訳
  (HF-005・HF-006・HF-010・HF-011・HF-012)、記者団への発言(HF-008)が
  新記事では不採用。B3の4テストでは「中心Storyline([20%案発表→撤回→
  それでも高値維持])の理解に必須ではない」「同じ役割を果たすFactと
  重複する」という理由で除外されている。

### 2-3. 話の中心の変化・因果関係の一貫性(重要な違い)

- **旧記事**は同種の「危険性の方が20%案より重要だった」という趣旨の
  主張を含むが、必ず限定的な言い回しを使っている: 「helps explain why
  the initial relief faded」(faded"を"helps explain"という緩やかな
  接続で結ぶ)、IMO決議についても「The record does not establish that
  this caused Trump's reversal」と明示的に因果否定を書き添えている。
- **新記事(JA R2およびAdvanced)**は同種の趣旨をより断定的な言い切りで
  表現していた: 「The danger in the water mattered more than the 20%
  number.」「Fees can change in a day, but dangerous waters cannot.」
  「Higher oil prices can affect gasoline and transport costs.」
  (JA R2でも「料金の仕組みは一日で変えられても、危険な海の状況は、
  発表ひとつでは変わりません」「原油価格が上がれば、ガソリンや輸送費に
  影響します」と同種の断定表現がすでに存在していた)。
- Advanced段の`vfl01.run_deviation_check`(Full Ledger照合)は、この
  断定的な因果・比較表現をMAJOR deviation(`changed_causality`/
  `changed_certainty`/`changed_comparison`=true)として検出し、技術retry
  1回後も解消しなかったため、既存のProduction Gate(`efam.
  run_writer_stage`のRuntimeError STOP)が正しく作動した。
- **観察(断定なし)**: 同種の因果的な「まとめの一文」は旧記事にも新記事
  にも現れていた。違いは断定の強さ(旧記事は緩やかな接続語・明示的な
  因果否定の但し書きを使い、新記事はより強い断定形を使っていた)であり、
  これが新記事だけがGate STOPになった理由と整合する。ただし、JA Writer
  (Original→R1→R2)自体にはこのFull Ledger照合Gateが掛かっておらず、
  Advanced段で初めて検出された点は、既存パイプライン構造上の事実として
  記録しておく(是正の実装は本Trialの範囲外、Production module変更禁止)。

### 2-4. 不要Fact混入の有無

- 新記事(JA R2まで)・旧記事とも、Ledgerに存在しないFactの混入は
  確認できなかった(数値・日付は両記事ともHF-002/HF-007/HF-009または
  対応するHF系Factの範囲内)。
