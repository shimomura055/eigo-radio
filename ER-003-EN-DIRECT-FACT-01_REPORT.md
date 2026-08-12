# ER-003-EN-DIRECT-FACT-01 実行報告(B版事実誤り Root Cause Audit)

**管理ID: ER-003-EN-DIRECT-FACT-01**
**実施日: 2026-08-12**
**ステータス: `AUDIT COMPLETE`(read-only監査のみ。Production・prompt・生成コード・仕様・音声はいずれも変更していない)**

## A. Root Cause Summary

2件のERRORは**原因が異なる**。まとめて「英語直接生成だから起きた」と
一般化しない。

- **ERROR-1(autoplay/feedのタイミング誤り)**: writerが実際に参照した4件の
  ソースのうち、参照元(GOV.UK press release)の該当文自体が構造的に
  **曖昧**だった(「curfewの説明の直後に"also"で続ける」という書き方が、
  時間帯限定かどうかを明示していない)。この曖昧さは**日本語版(A版の
  R4生成)にも同じ形で存在していた**が、A版だけが持つ追加QA層
  (ER-003-P1Bのfidelity QA)がこれを検出しREVIEW_REQUIREDへ落とした。
  B版にはこの追加層がなく、単独のfact checkerが独自に、より明確な別文書
  (Fact sheet)を新たに検索して初めて矛盾と断定した。**「検索不足」と
  「QA層不足」の複合**が原因。
- **ERROR-2(309 vs 81の混同)**: writerは309と81を区別できる一次資料
  (Savanta試行報告書)を**実際に取得していた**。にもかかわらず、
  「A pilot involving 309 families tested X」という直接的で説得力のある
  一文を作るために、母集団全体の数(309)を特定の介入群(夜間制限、81)
  へ誤って結び付けた。**これは明確な INTERPRETATION / COMPOSITION
  FAILURE(数字のscope誤認)であり、検索不足ではない**。同じ日本語
  R4記事は、同じソースから「309家族が参加した試行では…夜間制限が
  最も運用しやすく」という、母集団と個別条件を混同しない、より慎重な
  文型を選んでおり、この一件に限って言えば英語writerの文体選択が
  精度を犠牲にした。

## B. ERROR-1 Trace

**Source → writer記述 → Fact checker判定**

1. **writerが実際に取得した情報源**(`er003_output/en_direct_ab_01/A02/writer_sources.json`、
   検索3回):
   - GOV.UK press release("New social media curfews and crackdown on
     addictive features...")
   - GOV.UK consultation summary("Growing up in the online world...")
   - Ofcom "Protective defaults for social media platforms"
   - GOV.UK "Social Media Intervention Research 2026"(試行報告書)

2. **press releaseの実際の文言**(本監査でBrowserにより直接取得・確認):
   > "Default overnight curfews from midnight to 6am will be switched on
   > for 16 and 17-year-olds on social media apps..."
   >
   > "Features that can keep users scrolling for longer - such as videos
   > that automatically play one after another and feeds that continually
   > serve up personalised content - **will also be switched off by
   > default** for older teenagers."

   この2文は別々の文であり、2文目に時間帯の言及はない。厳密に読めば
   「常時デフォルトでオフ」とも取れるが、"also"という接続だけで前文の
   curfewとの時間的関係が明示されておらず、**曖昧**である。

3. **writerの本文**: 「Midnight arrives—and...Autoplay stops doing the
   deciding, while personalised feeds lose their automatic grip.」
   →曖昧な原文を、物語上の1つの瞬間(真夜中)へ統合する形で**誤った
   確定的な読み**を選んだ。

4. **Fact checkerの判定根拠**: writerが取得していなかった別文書
   「Fact sheet: New rules to protect children online」を独自に検索・
   取得(本監査でBrowserにより直接確認)。この文書は同じ内容を以下の
   ようにより明確に2文へ分離して記載している:
   > "This is why we will introduce overnight curfews for 16- and
   > 17-year-olds from midnight to 6am, alongside switching off
   > notifications **during this period**.
   >
   > We will also switch off by default autoplay and personalised feeds
   > for 16- and 17-year-olds."

   2文目には「during this period」に相当する限定がなく、curfewの文とは
   独立している。この文書はwriterが検索3回のいずれでも取得していない。

**分類**: **SEARCH FAILURE(一次source未取得)と COMPOSITION FAILURE
(曖昧なsourceを物語構成の都合で確定的に読んだ)の複合**。writerが
取得した最良のsourceは曖昧、より明確なsourceは未取得だった。

## C. ERROR-2 Trace

**Source → writer記述 → Fact checker判定**

1. **writerが実際に取得した情報源**: 上記4件のうち
   「Social Media Intervention Research 2026」(Savanta試行報告書)。

2. **報告書原文の実際の記載**(本監査でBrowserにより直接取得・確認、
   Methodology節):
   > "Pre-intervention: The Savanta research team conducted **309** online
   > in-depth interviews (IDIs) with young people aged 13–17 and their
   > parents/carers between 30 March 2026 and 1 May 2026.
   >
   > Intervention: Participants were allocated across **4 groups** based
   > on preference: a control group... and 3 intervention groups...
   > Intervention 1: Limiting usage... Intervention 2: **9pm–7am curfew**...
   > Intervention 3: complete removal..."

   309は前段階(介入前)の全参加者数であり、その後**4群へ配分**されたと
   明記されている。夜間制限(Intervention 2)は4群のうちの1つ。

   なお、fact checkerが結果JSON内で述べた「夜間制限群は81人」という
   具体的な内訳数値そのものは、本監査で当該ページのテキスト取得範囲内
   では独立に再確認できなかった(付録の表など、別セクションにある
   可能性がある)。**「309=全体、4群へ配分」という枠組みは直接確認できた
   が、「81」という具体的な数値は今回未検証のまま**とする(推測では
   埋めない)。

3. **writerの本文**: 「A government-backed pilot involving 309 families
   tested a stricter 9 p.m.-to-7 a.m. curfew.」
   → 309(全体)を、4群の1つである夜間制限に直接結びつけて記述。
   writerが取得した同じ報告書に、この結び付けが誤りであることを示す
   情報(4群への配分)が含まれていた。

4. **A版(日本語R4)の同一事実の扱い**(比較): 「309家族が参加した試行
   では、午後9時～午前7時の夜間制限が、三つの方法の中で最も運用しやすく」
   → 「309家族が参加した試行**では**」(trial全体の文脈)＋「夜間制限が
   …最も運用しやすく」(3方式中の評価)という構文で、309を夜間制限
   グループの人数だと断定していない。**同じsourceから、母集団と個別
   条件を混同しない文型を選んでいる**。

**分類**: **明確な INTERPRETATION / COMPOSITION FAILURE(数字のscope
誤認)**。検索は成功しており、正しい情報に到達していた。

## D. A版との違い(日本語経由・Source取得・QA層の分解)

| 項目 | A版(R4、日本語) | B版(実験、英語) |
|---|---|---|
| writerが取得したsource(A02) | GOV.UK press release / Savanta試行報告書 / Ofcom(3件、`er002_output/v1_2m_r4/condition_l/A02/writer_sources.json`) | GOV.UK press release / consultation summary / Ofcom / Savanta試行報告書(4件) |
| Web検索回数(writer) | 記録上available(検索利用は確認済み、具体的回数は本監査では未再取得) | 3回 |
| Fact sheet(より明確な文書)取得の有無 | **していない**(sourceリストに含まれない) | **していない**(同上) |
| 309/81の扱い | 文型上、母集団と個別条件を混同しない書き方(正確) | 母集団を個別条件へ直接結び付け(誤り) |
| autoplay/feedのタイミング表現 | 「対象アプリは初期設定では使えず…自動再生と…おすすめフィードも、最初からオフになる」(「最初から」も時間限定かどうか曖昧、**同種の曖昧さが存在**) | 「Midnight arrives...Autoplay stops」(曖昧なsourceを確定的な誤りへ変換) |
| この段階のfact checker判定 | **PASS**(自動再生/フィードの曖昧さは指摘されず) | (writer直後のfact checkerは実行していない設計。独立fact checkerが本文全体を検証しFAIL) |
| 追加QA層 | **あり**: ER-003-P1B fidelity QA(JA→EN翻訳の意味整合性チェック)が、まさにこの曖昧さを「During those hoursが自動再生・フィードにもかかるため時間帯限定の解釈上の差がある」として**独立に検出**、REVIEW_REQUIREDへ | **なし** |

**結論**: autoplay/feedの曖昧さは**日本語生成の時点でも解消されていな
かった**(A版のR4 fact checkerもPASSにしている)。A版がB版より安全
だった直接の理由は、「日本語だから正確だった」のではなく、**A版の
パイプラインにP1Bという追加のQA層が存在し、そこで初めて検出された**
ため。一方309/81については、A版のwriterが**たまたま**より慎重な文型を
選んでいたという、生成試行そのものの違いによる部分が大きい。

## E. Narrativeとの関係

- **narrative deviceがFact誤認を誘発したか**: ERROR-1について**支持
  される**。「It is 11:59 p.m.」→「Midnight arrives」という時間軸に沿った
  場面転換の構成上、curfew発動・通知停止・自動再生停止・フィード停止の
  **4つの制度項目を同一の瞬間に揃える**ことが物語上望ましく、これが
  曖昧なsourceを「すべて真夜中に起きる」という確定的な(誤った)方向へ
  読ませた可能性が高い。sourceにない場面描写(11:59 p.m.、クリップを
  見る10代)自体はFact claimとして扱われておらず(fact checkerもこの
  部分を矛盾としては指摘していない)、**演出そのものは無害**だが、
  演出が要求する「時間的統一感」が隣接する事実記述の解釈を歪めた
  可能性がある。
- **309/81混同との関係**: こちらはnarrative deviceとの結びつきが
  ERROR-1ほど明確ではない。「A pilot involving 309 families tested X」
  という一文単位の説得力(具体的な数字を主語近くに置く書き方)を
  優先した結果と考えられるが、これは特定の物語装置というより、
  一般的な「数字を使った説得力のある書き出し」という文体選択の
  副作用に近い。
- **master-style transferの強さとFact accuracyのtrade-off**: 部分的に
  **確認できる**。ERROR-1は「場面を1つの瞬間へ統合する」演出的判断が
  誘因となった可能性が高く、ERROR-2は「数字を使った直接的な書き出し」
  という文体選択が誘因となった可能性が高い。ただしいずれも、
  **演出そのものを弱めなくても**、事実確定を演出より前の工程へ分離
  すれば両立できる問題であり(H節)、「勢いのある文章=不正確」という
  必然的な関係ではない。
- **reasoning内部の扱い**: 本監査で使用したAPI(Responses API、
  `reasoning={"effort":"high"}`)は、生のreasoning過程(chain-of-thought)
  を応答に含めない仕様であり、本スクリプトもreasoning summaryを取得・
  保存していない。したがって上記の判定はすべて、**確定した本文
  ・source・fact checker出力という外部から観測可能な証拠のみ**に基づく
  ものであり、writerモデル内部の意思決定過程そのものを直接確認した
  ものではない。

## F. 仮説A〜D

| 仮説 | 判定 | 根拠 |
|---|---|---|
| **A**: 日本語を介したこと自体が精度を高めた | **NOT SUPPORTED**(ERROR-1について) / **UNKNOWN**(ERROR-2について) | ERROR-1の曖昧さは日本語版にも同じ形で存在し、日本語版のfact checkerもPASSにしていた。日本語であること自体が精度を高めたわけではない(D節)。ERROR-2について日本語版はたまたま正確な文型だったが、これが「日本語という言語の性質」によるものか「その回の生成のたまたまの結果」かを区別する証拠はない |
| **B**: 日本語writer直後のfact check + P1B fidelity QAというQA層の多さが効いた | **SUPPORTED**(ERROR-1について) | ERROR-1はA版のR4段階のfact checkでは検出されず、A版だけが持つ追加のP1B fidelity QA層で初めて検出された(D節)。QA層が1つ多いことが、この種の誤りの捕捉に直接寄与した明確な証拠がある |
| **C**: 単なる生成試行差・source取得差だった | **SUPPORTED** | ERROR-2の309/81の扱いは、同一sourceに対する文型選択の違いであり、生成試行ごとの表現ゆれの範囲内と考えられる。ERROR-1についても、A/B間で実際に取得したsourceの組み合わせ(どちらもFact sheetは未取得)がほぼ同一である以上、search自体の系統的な優劣というより実行ごとの検索結果のばらつきに近い |
| **D**: 複数要因 | **SUPPORTED**(最も正確な要約) | ERROR-1はB(QA層)とC(source取得のばらつき)の複合、ERROR-2は主にC(生成試行差)。単一の要因(「英語だから」「日本語だから」)には還元できない |

## G. 対策比較

まだ実装しない。比較のみ。

| Option | Fact accuracy改善期待 | 阪神masterの編集センス維持 | 実装複雑性 | APIコスト | Latency | 量産時の安全性 | 新しいfailure mode |
|---|---|---|---|---|---|---|---|
| **1. B方式撤回、A方式維持** | 高(実績あり) | 該当なし(B自体を使わない) | なし | 変化なし | 変化なし | 高(実績あり) | なし。ただしB版で確認された文体上の強みを活かす機会を失う |
| **2. writer検索指示の強化のみ**(primary source優先・数字scope確認等) | ERROR-1には部分的に有効(Fact sheet等のprimary文書を優先させれば検出率は上がりうる)。**ERROR-2には効果が薄い**(writerは既に正しいsourceを取得済みだったため) | 維持される(文体指示は変更しない) | 低(user prompt末尾に短い指示を追加するのみ) | 微増(検索回数がやや増える可能性) | 微増 | 中(根本的な構成段階の誤りは残る) | 過剰な確認指示が新たな冗長表現を生む可能性は低いが、ゼロではない |
| **3. writerの前にFact確定工程を追加**(Topic→Web research→verified fact ledger→阪神master+verified facts→English direct writer→独立fact checker) | **高**。ERROR-2のような「正しいsourceを持っているのに構成段階で誤る」問題に直接対応する(scopeを含めて数値を先に確定させるため)。ERROR-1も、fact ledger作成時に複数sourceを横断的に確認する設計にすれば検出率が上がる | **維持される**。文体で勝負する箇所(narrative writer呼び出し)はfactが確定した後段に置かれ、事実確認と演出を分離できる | 中(新規のAPI呼び出し1回+スキーマ設計が必要。ただし本セッションのfact checker実装や、旧J1のfact_id_map方式と同種のロジックを再利用できる) | 増(fact ledger確定用のAPI呼び出しが1回増える) | 増(直列で1呼び出し増える) | 高(root causeに直接対応) | fact ledger自体の誤り・省略が新たなfailure modeになりうる(fact checkerでの検証は引き続き必要) |
| **4. 現行B方式のまま、FAIL時に自動修正→再check** | 中(事後的な安全網としては有効だが、根本原因(なぜ誤るか)には対処しない) | 維持されるが、修正パスの実装次第で文体が変わるリスクがある | 中〜高(修正プロンプト設計・再checkループの終了条件設計が必要) | 増(FAIL時のみだが、修正+再check分が増える) | 増(FAIL時のみ) | 中(繰り返しによる収束が保証されない) | 自動修正が別の新しい誤りを生成する「もぐらたたき」型のfailure modeが生じうる |
| **5(参考). Option 3への軽量な追加として、fact checkerが検索したFact sheet相当の文書をwriterのsearch queryにも事前ヒントとして与える** | ERROR-1側の検索カバレッジ改善に直接寄与 | 維持される | 低〜中(ヒント文言の追加のみ) | 微増 | 微増 | 中 | ヒントが特定トピックに偏ると汎用性を損なう可能性 |

## H. 推奨案

**Option 3(writerの前にFact確定工程を追加)を推奨する。**

理由:
- A・B節の証拠から、2件のERRORの主因は「writerがfactを知らなかった」
  ことではなく、「factを取得済みだった、あるいは取得可能だったのに、
  物語構成の過程でscopeを誤った」ことにある(特にERROR-2は完全に
  この型)。この根本原因に最も直接効くのは、**事実確定と物語構成を
  別工程に分離すること**であり、Option 3がこれに該当する
- ユーザー評価でB版が高く評価した「文体・フック・master-style
  transfer」は、まさに物語構成(narrative writer)の呼び出しで生まれて
  おり、Option 3はこの呼び出し自体には一切手を加えない。**文章の
  勢いを弱める対策ではない**という今回の制約に合致する
- Option 1(A方式維持)はfact accuracyでは最も安全だが、B版で確認できた
  文体面の長所(E節参照、master方式のリズムの再現度)を活かす機会を
  放棄することになる
- Option 2(検索指示強化のみ)はERROR-1には部分的に効くが、ERROR-2の
  ような「正しいsourceを既に持っていたのに構成段階で誤る」パターンには
  ほぼ効果がない。今回の2件中1件に効かない対策を主対策にはできない
- Option 4(事後の自動修正)は安全網としては有用だが、根本原因への対処
  ではなく、実装するとしてもOption 3と併用する副次的な対策と位置付ける
  べき

## I. 次回実証

Option 3を実装した場合の再テスト条件案(実装はしない、条件の提案のみ):

- **対象**: 引き続きA02、同一Topic("英国の未成年向け夜間SNS設定")を使用する
  (Topicを変えると比較変数が増えるため)
- **方法**: 旧B本文を人間が修正して再評価するのではなく、**Option 3の
  fact確定工程を経た新しい1回のフルパイプライン実行**で新規生成し、
  そのfact checker結果が今回のERROR-1・ERROR-2と同種の誤りを再発するか
  どうかを見る
- **試行回数**: **最低2回**を提案する。理由は、F節で「単なる生成試行差」
  (仮説C)が実際に有意な要因として確認されているため、1回のPASSだけでは
  「対策が効いた」のか「今回もたまたま良い試行だった」のかを区別できない。
  2回とも同種の誤り(特にERROR-2型の数字scope誤認)が発生しなければ、
  対策の有効性を暫定的に支持する材料とする。3回目以降の追加は、2回の
  結果が割れた場合にのみ検討する
- **評価軸**: 今回と同じ独立fact checker(PASS/REVIEW_REQUIRED/FAIL)に加え、
  特にERROR-1・ERROR-2と同一カテゴリ(制度の適用範囲・時間条件、
  サンプルサイズ/母集団のscope)の誤りが再発していないかを個別に確認する
- **文体評価**: 9観点QA(前回ER-003-EN-DIRECT-AB-01と同一の軸)を再実施し、
  fact accuracy改善と引き換えに文体面のスコアが低下していないかを
  必ず確認する

## J. 非変更確認

- Production prompt(`er002_ja_article_generation.py`・`er002_ja_web_research_r3.py`等): 無変更
- B版生成ロジック(`er003_v1_en_direct_ab_01_generate.py`): 無変更(再実行もしていない)
- 新規記事生成: 実施していない(既存のB版生成結果を読み取り専用で分析したのみ)
- fact checkerによる本文修正: 実施していない
- B1/A2生成・TTS/audio生成: 実施していない
- CURRENT_SPEC.md: 無変更
- ER-003-P1B: 無変更(廃止していない)
- A方式・B方式の採否: 未決定(今回はA/B双方とも維持)
- OPEN-35(音声処理): 触れていない

本監査でBrowserを使い、GOV.UK press release・Fact sheet・Savanta試行
報告書の3ページを直接閲覧し、writerが参照したsourceの実際の記載内容を
確認した。これはB版本文・source・fact checker結果というすでに確定済みの
証拠を検証するための調査行為であり、新規記事生成やB版の再生成は
行っていない。

## 調査対象ファイル・ログ一覧

- `er003_output/en_direct_ab_01/A02/raw_article.md`(B版本文)
- `er003_output/en_direct_ab_01/A02/writer_sources.json`(B版writerの参照source)
- `er003_output/en_direct_ab_01/A02/audit/writer_attempts_detail.json`(B版writer検索クエリ・応答詳細)
- `er003_output/en_direct_ab_01/A02/fact_qa.json`(B版独立fact checker結果)
- `er002_output/v1_2m_r4/condition_l/A02/raw_article.md`(A版元となった日本語R4記事)
- `er002_output/v1_2m_r4/condition_l/A02/writer_sources.json`(日本語R4 writerの参照source)
- `er002_output/v1_2m_r4/condition_l/A02/fact_qa.json`(日本語R4段階のfact checker結果)
- `er003_output/p1b/A02/fidelity_qa.json`(P1B fidelity QA、前回セッションで既読、ERROR-1と同種の指摘を再確認)
- 外部一次資料(本監査でBrowserにより直接閲覧・引用):
  - GOV.UK press release: "New social media curfews and crackdown on addictive features..."
  - GOV.UK "Fact sheet: New rules to protect children online"
  - GOV.UK "Social Media Intervention Research 2026"(Savanta試行報告書)

## 受入条件15項目

| # | 条件 | 結果 |
|---|---|---|
| 1 | ERROR-1のwriter source追跡ができている | PASS(B節) |
| 2 | ERROR-2のwriter source追跡ができている | PASS(C節) |
| 3 | 各ERRORをSEARCH/INTERPRETATION/COMPOSITION等に分類している | PASS(B節・C節末尾) |
| 4 | 正しい一次情報をwriterが取得していたか明示している | PASS(ERROR-1=部分的、ERROR-2=取得済み) |
| 5 | narrative構成とFact誤りの関係を評価している | PASS(E節) |
| 6 | A版R4 writerのsource/生成条件と比較している | PASS(D節) |
| 7 | 「日本語を介したこと」と「QA層が多いこと」を区別している | PASS(D節・F節) |
| 8 | 仮説A〜Dを評価している | PASS(F節) |
| 9 | Option 1〜4以上を比較している | PASS(G節、5案) |
| 10 | B版の文章上の長所を維持する対策を優先している | PASS(H節) |
| 11 | 推奨する最小対策を1つ提示している | PASS(H節、Option 3) |
| 12 | 次のA02再実証方法を提示している | PASS(I節) |
| 13 | Productionコード・prompt・仕様・音声を変更していない | PASS(J節) |
| 14 | 不明事項を推測で埋めていない | PASS(C節、81の内訳は未検証と明記) |
| 15 | 調査対象ファイル・ログ一覧を提示している | PASS(上記一覧) |
