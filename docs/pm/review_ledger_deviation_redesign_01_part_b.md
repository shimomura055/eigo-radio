# LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01 Part B レビュー

**Status**: read-onlyレビュー(委任_02)。Production code/Prompt/Ledger schema/
Checker severity/SSOT4点/REPORT_LEDGERの変更なし。Trial実行・API呼び出し
なし(¥0)。以下は「調査REPORT(`LEDGER-DEVIATION-CHECK-REDESIGN-
INVESTIGATION-01_REPORT.md`)」と、ChatGPT再設計素案(委任文記載)を対象と
した批判的レビューであり、採用・実装の提案ではない。断定と論点は明示的に
分けて記載する。

---

## A. Product設計レビュー

**既存最低ラインとの差分(調査§6基準)**: 現行は10カテゴリいずれかtrueで
機械的にMAJOR(post-hoc validationがモデル自己申告を上書きする、
`vfl01.py:544-561`)。素案は同じ10カテゴリ検出は維持しつつ、
severity決定を「主要Fact理解を誤らせるか」というLLM(または
deterministic post-processing)の追加判断へ委ねる。**落ちるもの**: 素案
B-1型(原油→ガソリン価格の一般化、4回独立発生)・B-3型(接続詞"so")は
ACCEPTABLE/QUALITY化候補として通過しやすくなる。**残るもの**: A-2
(価格方向反転)・A-5(ロールバック↔再有効化)は素案でもBLOCKING分類の
候補(§本レビュー「重大事例への適用評価」参照)。

**「主要Fact理解を誤らせるか」基準の弱点**:
- 判定主体が曖昧: 「主要」を決めるのはLLM自身であり、その判断根拠は
  記事ごとに変わる。現行の10カテゴリ機械的トリガーと違い、判定に
  もう1段階の主観的推論(「これは記事理解の中心か」)が入る。これは
  検出精度の非決定性の上に**severity判定の非決定性**を追加で重ねる
  ことを意味する(既存の非決定性自体は調査済み: ER-009-N1-LEDGER-
  DEVIATION-RECALIBRATION-02、REPORT第1-0章・7-3章)。
- 学習者は英語話者よりも誤読しやすい(「留保文があるから安全」という
  ChatGPT側の論拠は、母語話者的な読解力を前提にしている可能性が
  ある。B-2の英文は"did not lead to a large, lasting fall in
  prices"という**二重否定的な因果構文**であり、A2/B1学習者がこの
  構文だけを聞いて「価格は上がった」と正確に理解できるかは、英語
  学習サービスとしての固有リスクとして評価が必要。この点は素案に
  記述がない。★
- Key Phrase/Comment/In One Lineへの増幅伝播経路(`CURRENT_SPEC.md`
  Grep結果): Key Phraseは「そのレベル自身の最終確定本文から独立選定」
  (`CURRENT_SPEC.md:1677`)、In One Lineは「Full Story/Points既出情報
  のみを使い、新規factを追加しない」(`CURRENT_SPEC.md:582`)。つまり
  Deviation CheckがQUALITY判定で通過させた逸脱文が本文に残れば、
  その文がKey Phrase選定・In One Line要約の**入力**になり得る。現行
  Deviation CheckはFull Story本文のみを検証対象にしており、Key
  Phrase/In One Line生成後に再チェックする工程はない(調査範囲では
  未確認)。**QUALITY蓄積ログが増えるほど、この経路の露出も増える
  可能性がある(論点、実測なし)**。

**緩すぎる/過剰品質の候補**: 過剰品質はB-1(4回独立発生、`jaw.py:58`
のPrompt自身が要求するブリッジ文と衝突、REPORT7-2節)が最有力候補。
緩すぎる懸念は下記「Fact Safety」節参照(numeric_scope・出典すり替え等)。

**Disclaimerとの役割分担**: 委任文Jは「Disclaimerは残余リスク説明で
あり品質低下の理由にしない」と明記。妥当な原則だが、素案自体には
Disclaimer文言・提示場所の記述がなく、「QUALITY通過率が増えた分だけ
Disclaimerの実効的な守備範囲が広がる」という定量的な結びつきの検討が
欠けている。★(Disclaimer文言未定のまま品質基準を緩めることの当否は
Product判断)

---

## B. Fact Safetyレビュー

**BLOCKINGに残すべきものの抜け(素案の列挙漏れ候補)**:
- 出典・帰属のすり替え(changed_actorの一種、狭義の帰属改変): HF-010
  notes_for_writerが「87.55ドルを使用する場合はFTのヒストリカル表に
  よると帰属を付ける」と明記するように、数値そのものは合っていても
  出典を落とす/変えるケースはchanged_actor単体では拾いにくい。
- numeric_scope(母集団の混同): HF-005「日中高値と終値を混同しない」
  ・HF-010「速報時点値と日次高値を区別する」は、数値自体(changed_
  number)は変えずに**その数値が何を指すか**を混同する逸脱であり、
  10カテゴリのどれにも明示的に対応しない(changed_scopeに準ずるが、
  「対象範囲の一般化」ではなく「同じ記事内の複数の類似数値の取り違え」
  という別種)。
- 日付の相対表現(「その翌日」「約24時間48分後」等の相対時間表現の
  改変): HF-007 notes_for_writerが要求する時系列固定はchanged_timeで
  拾えるが、相対表現(before/after/soon等)の粒度違いは境界が曖昧。
- 引用発言の改変: 本調査のFamily X事例には直接該当がないが、
  10カテゴリに「発言の逐語性」を保証する項目がない(changed_factで
  拾える場合もあるが専用カテゴリではない)。
- 極性語("最初/唯一/最大"等): 素案には言及なし。

**causality緩和のリスク**: 素案Cは「ニュース理解の中心か」を判定軸に
するが、**誰がどう判定するかが未定義**。Hormuz事例(B-2)はまさに
「因果関係が記事の主題そのもの」であるケース(記事全体が「料金案は
消えたが原油の不安は残った」という因果的対比構造で組み立てられている、
REPORT7-1節の本文引用参照)。この場合、causalityを緩和対象にすると、
**記事の中心的主張そのものを検証対象から外す**リスクがある(下記
Hormuz独立評価で詳述)。

**notes_for_writer soft化の危険(Hormuz Ledger HF-001〜012、全12件を
実際に分類)**:

| fact_id | notes_for_writer(要約) | 分類 |
|---|---|---|
| HF-001 | この決議と7/14撤回の因果関係は一次資料で確認不可、撤回の原因として記述しない | **factual constraint**(禁止する因果主張を名指し) |
| HF-002 | 7/13提案が先、7/14撤回は後。7/14を7/13の価格上昇の原因として扱わない | **factual constraint**(時系列+因果方向の固定) |
| HF-003 | 「導入した」と確定形で書かず「提案した」とする | **factual constraint**(changed_certaintyの境界を具体的文言で指定) |
| HF-004 | 実額/確定通航料として扱わない、「試算」と明示 | **factual constraint**(numeric_scopeの固定) |
| HF-005 | 日中高値と終値を混同しない | **factual constraint**(numeric_scopeの固定) |
| HF-006 | 7/13上昇を「20%料だけが原因」と断定しない、撤回はこの後の出来事 | **factual constraint**(因果+時系列の固定) |
| HF-007 | 投稿は7/13提案の約24時間48分後、必ず後に位置付ける | **factual constraint**(時系列固定) |
| HF-008 | 撤回を確認する補強Fact、7/13の発言と混同しない | **factual constraint**(時系列固定) |
| HF-009 | 撤回後に原油価格が全面的に下落したとは書かない、観測は一時的縮小+回復 | **factual constraint**(B-2に直結) |
| HF-010 | 速報値と日次高値を区別、87.55ドル使用時は帰属を付ける | **factual constraint**(numeric_scope+帰属) |
| HF-011 | 撤回があったにもかかわらず清算値は上昇、これだけで因果推論しない | **factual constraint**(B-2で実際にMAJOR根拠となった note) |
| HF-012 | Brentの反応として転用しない、複数回反転の補助Factとしてのみ使用 | **factual constraint**(scopeの転用禁止) |

**分類結果: 12件中12件がfactual constraint、0件が純粋なwriter guidance
(トーン・文体・エンタメ性等の助言)**。調査REPORT第2章が引用する
Researcher Prompt(`vfl01.py:157`)の設計意図(「後工程のwriterが強い
因果表現を使わないよう」)どおり、**このLedgerのnotes_for_writerは
「執筆ガイダンス」という名目のフィールドでありながら、実質的には
scope/causality/certaintyという既存10カテゴリの境界を、Fact単位で
具体的日本語文として再言語化したものである**。これは素案Eの前提
(「Ledger Fact=hard、notes_for_writer=soft」という二分自体)を覆す
実データであり、**soft化した場合、単なる助言ではなく、10カテゴリ判定
の実質的な精度を支える具体的境界情報そのものを失う**(観察、断定は
しない。他のLedger・他Familyでのnotes_for_writerの実態は本調査未確認)。

**context window採用のリスク**: B-2の記事は問題文の直後(1〜2文後)に
留保文「Of course, this price movement alone cannot tell us...」を
含むが、この留保文自体がHormuz記事全体で**繰り返し使われる定型的
ヘッジ表現**であり(JA原文にも同一パターンの留保文が存在、REPORT7-3
節)、window判定が「留保文の有無」という表層パターンだけを見るなら、
**同じ定型ヘッジを機械的に文末に置くことで実質的な逸脱を免罪符化**
できてしまうリスクがある。これは素案には記述がない。★

---

## Hormuz事例(B-2)への適用評価(Claude独立判定)

**独立判定: BLOCKING dependent(境界だが、現行素案の基準だとACCEPTABLE
寄りに緩めすぎるリスクがある。ChatGPT見解[QUALITY/ACCEPTABLE候補]には
賛成できない)**。

根拠:
1. HF-011のnotes_for_writerは「撤回が価格を**上昇させた、または下落
   させなかったと因果推論しない**」と明記している。EN記事の該当claim
   "The disappearance of the fee plan did not lead to a large,
   lasting fall in prices."は、まさに**この literally 禁止された推論
   パターン(「撤回が下落させなかった」)とほぼ同型**である。"large,
   lasting"という限定語は存在するが、限定語の有無は「因果推論するか
   否か」という禁止事項の本質(方向性の因果的結び付け)を変えない。
2. この因果関係(料金撤回と原油価格の関係)は、記事の**中心テーマ**
   そのものである(タイトル自体が「二十パーセントは退場した。それでも
   原油の不安は残った」という因果的対比構造)。素案Cの基準「ニュース
   理解の中心か」で判定するなら、**この一節こそが中心そのもの**であり、
   非中心的なNon-blocking causal phrasingには該当しない。
3. ChatGPT見解が挙げる「元Ledgerに『上げ幅縮小後、高水準へ戻った』
   観測あり」という点は事実だが、これは**Ledgerの観測データがHF-009/
   HF-011のnotes_for_writerの禁止事項と表裏一体**であることを見落とし
   ている。Researcher自身がこの観測データから「安易に因果推論される
   危険」を予見して2つのFact双方にほぼ同内容の警告を重複して書いて
   いる(HF-009とHF-011で酷似した文言が2回出現)ということは、**この
   境界事例はResearcher段階で既に「危険」と認識されていたことの
   直接証拠**であり、緩和候補として軽く扱うべきではない。
4. 一方で、記事側の直後の留保文・"large, lasting"の限定語自体は、
   「絶対的な因果主張ではなく相対的な観測記述」への配慮の跡であり、
   A-2(価格方向そのものを反転させた"prices began to fall")ほど
   明確な事実誤認ではない。したがって(i)絶対STOPと同列には置かない
   が、(iii)「品質改善の意味はあるがSTOP必須か疑問」区分よりは
   厳しい評価が妥当と考える。

結論(Claude独立見解): **QUALITY/ACCEPTABLE降格には反対**。少なくとも
「notes_for_writerが明示的に禁止した推論パターンと一致するか」を
deterministic post-processingでチェックする追加ルール(素案Hの拡張)が
なければ、この種の事例は再現的に見逃される。

---

## 重大事例(A-1〜A-5)への適用評価

| # | 内容 | 新設計での分離ルール | 分離失敗し得る条件 |
|---|---|---|---|
| A-1 | 時制drift「ロールバックされます」(未来形)、2回ともCheckerが誤ってCOMPLIANT判定 | 該当なし。**これはCheckerの検出漏れ(既存10カテゴリでも拾えるはずのchanged_timeが発火しなかった)であり、severity設計(BLOCKING/QUALITY/ACCEPTABLE区分)の問題ではない** | severity再設計をしても、そもそも「検出されなかった」ケースは区分方法によらず素通りする。**新設計は検出率の問題を解決しない**(委任文自身も明記) |
| A-2 | 「上げ幅縮小」→"prices began to fall"(価格方向反転) | 素案B(BLOCKING列挙: 値動き方向の反転)で明確にBLOCKING。changed_comparison/changed_factがtrueで単体判定でも拾える | 分離失敗リスクは低い(単体判定・数値方向の話であり文脈window不要) |
| A-3 | 支払義務者を「those carrying the cargo」と具体化 | 素案B(BLOCKING列挙: 根拠のない重要Fact追加)でBLOCKING。unsupported_new_claimが該当 | 「重要」の判定基準次第では「単なる自然な補完」とQUALITY降格される余地がある(誰が支払うかは記事の実務的な理解に直結するため、本来はBLOCKING維持が妥当) |
| A-4 | 「相手」(企業・店舗)→「users」(Museのユーザー) | 素案B(BLOCKING列挙: 対象取り違え)でBLOCKING。changed_scopeが該当し、プライバシー文脈のため重要 | 対象がuser個人か企業かはプライバシー論点の核心であり、分離失敗のリスクは相対的に低いと考えるが、「範囲の一般化」程度の軽い逸脱と誤認されるリスクは残る |
| A-5 | 「元に戻しました」(ロールバック)→"put back the feature"(再有効化と読める、意味反転) | 素案B(BLOCKING列挙: 肯定否定反転に準ずる意味反転)でBLOCKING。changed_negationまたはchanged_factが該当 | "put back"という英語表現の多義性(戻す/再設置)をLLMがどちらの意味で読むかは非決定的であり、境界例的にQUALITY降格されるリスクがある(実際に現行機構はmust-fix retryで検出・是正済みだが、新設計のcontext window判定がこの多義性をどう扱うかは不明) |

**総評**: A-2〜A-5は素案Bの列挙型BLOCKINGでおおむね維持可能と評価する。
ただしA-3・A-5は「重要」「意味反転」の判定基準が曖昧なままだと、
QUALITY側へ滑り落ちるリスクが残る。A-1は設計変更では解決しない
既存の検出漏れ問題であり、severity再設計の議論に含めるべきではない
(委任文の想定どおり)。

---

## 過剰品質候補(B-1〜B-4)への適用評価

| # | 内容 | 分離ルール | 分離失敗し得る条件 |
|---|---|---|---|
| B-1 | 原油→ガソリン価格の一般化ブリッジ文、4回独立発生、JA Writer Prompt自身が要求する構造(`jaw.py:58`) | 素案の「明確な新規Factを伴わない一般的な情景描写」許容規定(既存Prompt`vfl01.py:527-528`)を拡張適用しACCEPTABLE候補にできる。素案には専用の列挙はないが、H(deterministic rule)で「一般常識レベルの経済知識」を許容パターンとして追加すれば分離可能 | 「一般常識」と「新規の具体的主張」の境界線基準が素案にも明記されておらず、依然LLM次第。4回独立発生という再現性の高さは、ルール化すれば安定して分離できる可能性を示すが、ルール自体が素案に存在しない(★Product判断が必要) |
| B-2 | Hormuz causality(上記で詳述) | 素案C(causality区別)候補だが、上記の独立評価どおり**分離に失敗するリスクが高い**(notes_for_writerの明示禁止パターンと一致するため) | 前述のとおり |
| B-3 | 接続詞"so"による因果連結(B1「7/14に懸念が続いたので20%案は退場したが、値は一時後退のみで回復した」) | 素案D(context window)で「観測事実の自然な文章化」と判定できる可能性はあるが、この文は**2つの独立した出来事(懸念継続/料金撤回)を"so"で単一因果に結んでおり**、Ledgerが因果関係を確認していないと明記した領域(HF-007 notes_for_writer相当)に抵触する | 「そのように読める」接続詞は、Non-blocking causal phrasingとBlocking causalityの境界が最も曖昧なパターンであり、"so"の使用は日本語原文にはなく英訳時に新たに生まれた因果的含意である可能性が高い(originはja_source判定だが、原文は単なる並列の可能性がある。原文再確認は本レビューのスコープ外) |
| B-4 | 一般読者心理への一般化3件(MUSE-HC-004/006/010) | 素案のBLOCKING列挙(根拠のない重要Fact追加)に該当し得るため、必ずしもQUALITY降格されない可能性がある。実際にはmust-fix retry 1回で解消済み(現行機構で既に対応できている) | 「一般読者の心理」への一般化は、Ledgerが確認したのはMeta従業員の個別報告のみ(scope超過)であり、素案のACCEPTABLE候補(一般的情景描写)とunsupported_new_claim(BLOCKING候補)の境界が曖昧。4件中3件がMAJORのまま確定した実績(現行retry機構で解消)を踏まえると、**新設計で緩めた場合に現状より品質が下がる可能性がある**(論点) |

---

## Trial設計レビュー

- **fixtureの不足**: 重大15件(実データ)は母数として小さすぎる
  (統計的判断には不十分)。カテゴリ×origin×Family(X/Y/Z)の被覆が
  必要。特に**negative example(通すべきものの正解セット)が現状ゼロ**
  であり、「不要BLOCK率」を測る基準がない。境界例(B-2/B-3のような
  causality境界)を意図的に増やす必要がある。
- **合成fixture(ER-009-N1の9種)との併用**: 調査REPORT第6章・第8-1節
  によれば、既存9種の意図的危険fixtureは全てMAJOR判定を維持している
  実績がある。これは**BLOCKING維持率の下限を保証する既存の資産**
  であり、Trial設計はこれを流用しつつ、新たに「通すべきもの」10件
  程度(B-1型の一般化ブリッジ文など)を追加すべき。
- **非決定性測定**: 委任文が求めるn=5〜10回×fixtureの反復は、調査で
  「実行間の非決定性は既知だが未実測」(REPORT第7-3章・8-6節)と明記
  されている核心的なギャップに対応する。この測定なしに新設計を評価
  しても、「新設計が改善したのか、たまたま今回の実行が一致しただけ
  か」を区別できない。★(Trial設計の必須項目として明記すべき)
- **gold labelの再現性**: 「誰が正解ラベルを付けるか」は、委任文にも
  「ユーザー/合議」と示唆されているが、本調査自体が「4区分は1回限り
  の目視分類、合議・再現性検証は未実施」(REPORT第4章末尾)と自己申告
  している。**Trial自体のgold labelが、今回のレビューで批判した
  非決定性・主観性の問題を内包している**(構造的な堂々巡りのリスク)。
- **最小sample数**: Family Xの実データは現状Hormuz/Meta Museの2記事
  ×数run程度。Production採用判断に必要な最小記事数・Family数は
  素案・調査いずれにも定量的基準がない。★
- **費用概算**: Checker中央値¥0.90/回(REPORT第5章)。fixture 25件
  (重大15+境界10と仮定)×反復8回=200回で概算¥180(Checker単体、
  retry・GEN費用は別途)。これは既存Family X実測コスト(¥5〜6/記事)
  と比べ小さいが、**新設計のdeterministic post-processingルール実装
  自体の開発コスト**は本調査のスコープ外であり未計上。

---

## リスク / 抜け漏れ

- QUALITY蓄積ログの置き場・閲覧責任者が素案に未定義。「通すが記録は
  残す」という設計は、記録が実際に見られなければHuman Reviewの
  非常口(素案I)より弱い安全網になる。★
- QUALITYがKey Phrase抽出・Comment生成へ伝播する経路(本レビュー
  「A. Product設計」節参照)への対策が素案にない。★
- Severity変更がREJECTED/VALIDATED判定・既存REPORTの再解釈に与える
  影響: 過去のUSER_DECISION_REQUIRED(B-2含む)は現行10カテゴリ基準で
  下された判断であり、新設計適用後に遡って「実は通せた」と再解釈
  すると、**過去のSTOP判断の正当性そのものが揺らぐ**。再解釈の要否・
  範囲はProduct判断が必要。★
- Disclaimerと学習者への説明責任: 素案Jは「Disclaimerは品質低下の
  理由にしない」とするが、具体的な文言・提示場所が未定のまま品質
  基準の緩和を先行させることの当否。★
- Family Z(Fiction)への適用可否: `CURRENT_SPEC.md`をGrepした結果、
  「Family Z」節はFact Safety/Deviation Checkとの関係を明記して
  いない(該当Grepヒットなし)。Family Zはニュース由来Factではなく
  文学作品由来のため、10カテゴリ・severity区分がそのまま適用できる
  かは未検証。**新設計をFamily Xだけでなく将来Family Zにも流用する
  前提があるなら、この論点は素案に含まれるべきだが現状ない**。★

---

## 改善提案(採用しない、提案のみ)

1. notes_for_writerを一律soft化せず、**Researcher段階でnotes_for_writer
   を「factual constraint」と「style guidance」の2フィールドに分離する
   schema変更をTrialで先行検証**(実データで12/12がfactual constraint
   だった今回のサンプルを踏まえると、単純なsoft化は危険度が高い)。
2. causality緩和には「Ledgerのnotes_for_writerが明示的にその推論を
   禁止しているか」をdeterministic post-processingで機械的にチェック
   する専用ルールを追加する(B-2のような「notes_for_writerの文言と
   ほぼ同型の推論」を自動検出できれば、context window判定より確実)。
3. QUALITY判定には「同一fixtureでのBLOCKING維持率100%」を必須受入
   条件とする(委任文の想定どおりだが、具体的な閾値として明記)。
4. B-1型(一般常識レベルの経済知識)は、JA Writer Prompt自身が要求
   する構造的ブリッジ文と衝突する既知パターンであるため、**Prompt側
   (Writer Prompt)とChecker側の整合を先に取ってからseverity区分を
   変更する**方が安全(Checkerだけを緩めると、Writer Promptの要求
   との矛盾自体は残る)。

---

## ★新しいProduct判断が必要な事項(まとめ)

1. Hormuz B-2の因果境界の最終判定(BLOCKING/QUALITY/ACCEPTABLE)。
2. "large, lasting"等の限定語・留保文が定型ヘッジ化した場合の免罪符化
   リスクへの対応方針。
3. Key Phrase/Comment/In One LineへのQUALITY逸脱伝播を防ぐ追加検証
   工程の要否。
4. QUALITYログの置き場・閲覧責任者・レビュー頻度。
5. Severity再設計が過去のUSER_DECISION_REQUIRED判断(B-2等)の遡及的
   再解釈に与える影響の扱い。
6. Disclaimer文言・提示場所の確定を品質基準緩和より先行させるか。
7. Family Z(Fiction)への新設計適用可否・スコープ。
8. notes_for_writerのfactual/guidance分離schema変更の要否(Trial先行
   検証が必要か)。

---

## 出典一覧

- `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`(全文)
- `er037_output/family_xy_concreteness_control_trial_01/hormuz/task_a_advanced/A3_deviation.json`(A-2/A-3)
- `er037_output/family_xy_concreteness_control_trial_01/hormuz/task_b_cleanup/B1_deviation.json`(B-3)
- `er039_output/family_xy_concreteness_control_trial_02/meta/cells/AN2-T1_deviation.json`(A-4)
- `er045_output/family_x_no_heading_segmentation_trial_01/meta/v2/must_fix_retry_result.json`(A-5)
- `er019_output/family_x_refresh_e2e_01/hormuz/run_02/b1b/audit/deviation_checks/advanced_attempt1.json`(B-2、Hormuz Ledger HF-001〜012全文含む)
- `er019_output/family_x_b3_production_wiring_01/run_01/b1b/audit/deviation_checks/advanced_attempt1.json`(B-4)
- `er019_output/family_x_b3_production_wiring_01/run_01/audit/fact_fidelity_fix_01_recheck_summary.json`(A-1解決記録)
- `CURRENT_SPEC.md`(Key Phrase/Comment/In One Line/Family Z該当箇所、Grep)
