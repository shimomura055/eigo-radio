# static_eval_01: 改善Prompt(After)の机上評価(JPY0、LLM呼出なし)

評価は「Afterの各文が、既存shortlistの各候補にどう働く想定か」の机上判定であり、**実測ではない**。○=文面が確実に狙い通り働く構造(候補の有無や機械処理に依存して保証される) / △=LLM判断依存の期待(未検証) / ×=満たさない見込み。Trial結果でもProduction仕様でもない。
受入条件の番号は設計書 `KP-CANDIDATE-SELECTION-QUALITY-DESIGN-01` §7-2 に従う: 1 `time lag`>`lag`(上流=Phase 1-A領分、本Phaseは対象外)/ 2 記事独自比喩をImportantに選ばない / 3 Topic候補として評価可 / 4 `in the ring`型の断片回避 / 5 `push prices up`・`be behind price increases`の評価 / 6 `take time`・`right away`が有益候補を押し出さない / 7 Std・Adv両方で改善。

対象shortlist: (S1) Coffee v5実run Std/Adv(`er019_output/family_x_audio_production_wiring_01/coffee_prices__run_v5_ms_01/{a2,b1b}`)/ (S2) Phase D V2 shortlist(`pumps its fist`等のLLM補助抽出3件入り、ABC固定候補=`er064_output/kp_idiom_priority_abc_01/runs/{std,adv}_A_run1/selector_prompt.txt`)/ (S3) meta run_03 Std/Adv / (S4) hormuz run_02 Std/Adv(候補名は`er064_output/kp_candidate_selection_design_01/upstream_trace_01.json`)。Phase 1-Aの改善shortlist(`time lag`・`含む/含まれる`注釈入り)は本委任時点で未入手のため、「入った場合」を条件付きで記す。

## 1. 文ごとの想定動作(After各文 × 候補)

| After の文(要約) | 想定される扱い(候補例) | 備考 |
|---|---|---|
| 【判断の基準】6指標の順序(逐語維持)+同格+透明表現を下げる | 現行と同じ土台。`price measure`/`retail prices`/`usual cup`(透明名詞連語)は従来どおり下がる | 順序入替は無効(ABC)なので維持が正 |
| 同程度なら定着した自然な表現を優先、区分名/evidenceラベルだけでは選ばない | Std v5: `feels like`/`based on`/`waiting for`はラベル(idiom/phrasal_verb)だけなので不利。`push prices up`(prices up)・`come down`(Adv)・`show up`(Adv、抽象主語)は有利。`take time`/`right away`/`on a regular basis`は次の文でさらに下がる | ラベル誘導の抑止はPhase D (d) と同方向 |
| 既知の基本連語は同程度の他候補があれば下げる(乏しければ可、句動詞・非字義は下げない)+LEVEL_RULE | Std v5: `take time`/`right away`/`on a regular basis`が下がる。代わりに入る候補は`Roasting`・`pumps`(word)・`prices up`等。D14(基本連語しか無い場合もword補完可)が無いと区分優先で残る | Advは`go down`/`came from`/`comes with`(構成語どおり)が下がり、`show up`/`come down`(抽象主語)は保持 |
| 【学ぶ単位】用法が成り立つ最小のまとまり、含む/含まれる注釈、付け足しだけなら短い側 | S2 Adv: `been behind price increases`(目的語を含む)を選び、`been behind`単独には倒れない。Phase 1-Aが`含まれる:`を付けた場合は同内容の二重選択を避ける。S4: `give back gains`型が候補にあれば`gave back`単独より優先(現shortlistには`gave back`のみ) | Rule7(`been`→`be`)でのINVALIDは別問題(§4) |
| 【役割】Topic=本文理解への貢献、Important=他記事でも使える定着表現、記事独自の創作的比喩はImportantに選ばない | S2: `two numbers in the ring`/`its own hidden clock`/`in the ring`は、LLMが記事独自と判断すればImportantから外れTopic比較へ回る。`pumps its fist`は`pump one's fist`(他記事でも使える定着した動作表現)としてImportant可と読める。Topic=`raw bean`(Std)・`price tag`/`lag`(Adv)等 | ABCで現行LLMは記事独自比喩にidiom・importantを付けた実績あり=LLM判断依存 |
| `established_or_article_specific`を記録(選定可否には使わない) | 記録のみ。Important×article_specificの組はflagとして集計(retryなし) | 費用増はoutput約+50〜70token/job |
| 【日本語グロス】統合 | 制約は保持。出力変化は未検証 | Phase 2で機械検査 |
| 出力ルール(候補ID、backup、区分優先+基本連語のみの場合のword補完) | 契約不変 | - |

## 2. 受入条件2〜5(+6,7)の○△×

凡例: 現行=現行Prompt+その候補リスト、After=改善Prompt+同じ候補リスト(静的判定)。

| shortlist | 受入2 記事独自比喩をImportantにしない | 受入3 Topic評価 | 受入4 断片(in the ring)回避 | 受入5 push prices up / be behind price increases | 受入6 take time等 | 受入7 Std/Adv |
|---|---|---|---|---|---|---|
| S1 Coffee v5 Std(現行shortlist) | ○(該当候補が無い=偶然。現行も同じ) | △(`raw-bean`/`price tag`/`bean prices`。役割基準が「理解への貢献」に具体化されるが効果は未検証) | ○(該当候補が無い=自明) | △(`prices up`のみ。「用法が成り立つ最小のまとまり」で`push prices up`型が有利になる期待) | △(基本連語が下がり、word候補`Roasting`/`pumps`が入る。LLM依存) | Std △ |
| S1 Coffee v5 Adv | ○(同上) | △(`lag`単独がTopicに残る=`time lag`が供給されない限り改善しない) | ○(自明) | △(`show up`/`come down`は保持される見込み。`be behind price increases`は候補に無い) | △ | Adv △(句動詞保持は○に近い、供給不足は上流依存) |
| S2 V2 Std(+LLM補助3件) | △(`two numbers in the ring`/`its own hidden clock`をarticle_specificと判断して外す期待。ABC現行はimportant採択) | △(`raw bean`/`two numbers in the ring`がTopic比較。貢献が大きいほうをTopicに回す設計) | △(Stdは`two numbers in the ring`で完結形。断片ではない) | △(`push prices up`は維持見込み) | ○寄り(V2供給で既に`take time`等は押し出されている。Afterでも維持の見込み) | Std △ |
| S2 V2 Adv(+`in the ring`/`been behind price increases`/`pumps its fist`) | △(`in the ring`が記事独自の言い回しと判断されImportantから外れる期待。ただし`in the ring`は辞書的にも実在表現で判断が割れ得る) | △ | △(`in the ring`は動詞を欠く断片。「用法が成り立つ最小のまとまり」で不利になる期待。ただし5語上限で`putting the two figures in the ring`は不可=完全な解消は抽出側) | ○〜△(`been behind price increases`を選ぶ。INVALIDはRule7側) | △ | Adv △ |
| S3 meta Std/Adv | ○(記事独自比喩候補なし) | ○(`Behind the Scenes`(タイトル)・`contract workers`・`concierge`) | ○寄り(`of a`/`calls to`/`calls it`/`end of`/`needed to`は断片。ラベル(idiom)だけでは選ばない、完結したまとまりを優先=Afterで下がる) | -(該当表現なし) | △(`ask for`/`instead of`/`no way`は基本連語として下がる) | Std/Adv △ |
| S4 hormuz Std/Adv | ○(候補なし) | ○(`sea blockade`/`center stage`) | △(`gave back`/`pulled back`/`taken back`は目的語を欠く。`give back gains`は現shortlistに無い=上流のPhase 1-Aが決める) | -(該当なし) | △(`no one`/`by trade`/`feels like`は下がる見込み) | △ |

総括: 既存shortlistに対してAfterが**確実に効く(○)**のは、(a) 候補に問題の表現が無い場合の無害性(現行と同じ)と、(b) ラベルだけで選ばれていた断片・基本連語を下げる方向(meta `of a`等)。**記事独自比喩のImportant回避(受入2)・断片回避(受入4)・Topic評価(受入3)は、LLM判断に依存する△**であり、ABCで現行LLMは記事独自比喩にidiom/importantを付けた実績がある。効果の有無はPhase 2でしか確認できない。

## 3. 矛盾チェック(Afterの指示が互いに打ち消さないか)

| 組合せ | 判定 | 説明 |
|---|---|---|
| 6指標の順序 × 「同程度なら定着度」 | 問題なし | タイブレークは「同程度のとき」に限定。順序は逐語維持(test T2) |
| 透明表現を下げる × 「自然なコロケーションを優先」 | 低リスク | 前者は優先順位(推測困難)、後者は同程度のタイブレーク。ただし`push prices up`型(構成語は易しいが連語として定着)は「透明」と「自然なコロケーション」の両方に当たり得る。△。Phase 2で`push prices up`の採択率を見る |
| 基本連語を下げる × phrase区分優先(G03) | 解消(D14) | 「基本的な連語しか無い場合を含む」を追加し、word補完を許容 |
| 基本連語を下げる × CEFRを主要軸にしない | 解消(D13) | 語彙表の等級ではなく表現の定着度で判断、に書換え |
| 長いまとまり優先(目的語・補語まで)× 1〜5語上限 | **残存** | 6語以上の完結形(`putting the two figures in the ring`)は選べない。Promptで解けないので抽出側(Pkg E)の領分。Afterは上限を維持(gate制約) |
| 長いまとまり優先 × 速度(短い表現を学ぶ価値)| 低リスク | 「付け足しだけなら短い側」で打ち消しを明示。主語・時・場所と、目的語・補語を区別する基準が曖昧なケース(前置詞句の場所/補語)が△ |
| Important=定着表現 × Topic=記事特有の比喩可 | 問題なし | 役割で分担。ただし「比喩だから」で決めない文と「本文理解への貢献が大きい比喩はTopic可」は同時に働く。貢献の大小判断はLLM |
| Level別の既知基準 × 役割・タイブレーク | 低リスク | Std/Advの差はLEVEL_RULE 1文のみ。Stdで`pumps its fist`を「基本的な句」と誤認する恐れは低い(日常頻出ではない)が△ |
| S07「同格」(区分間)× G03「区分優先」 | **残存(Productionと同じ)** | 現行にも存在。AfterはD7(ラベルだけで選ばない)で緩和したのみ |
| グロス統合 × 元の個別規則 | 要確認 | 制約は保持(testで漢数字・括弧語を確認)。出力への影響はPhase 2で機械検査 |

## 4. Rule7起因の正規化INVALIDは選定品質と切り分ける
ABCの非PASS(B 4/6、C 5/6)は、`be behind`→`be behind price increases`(語追加+`been`→`be`)、`raw-bean`→`raw-bean prices`、`its`→`something's`というRule7(canonicalization)のINVALID/REVIEWが主因で、選定そのものの良し悪しではない。Afterの【学ぶ単位】は「目的語を含む側」を選ばせるため、displayの語追加が増えて**Rule7 INVALIDが増える可能性**がある(逆に、最初から長い側のcandidateを選べばLLMが後で語を足す必要が減り、減る可能性もある=方向は未検証)。評価時は次の2層に分ける: (層1) 選定品質=gate前の選定結果(INVALIDでも選ばれた候補・role・自己申告は評価に含める)、(層2) gate通過率=canonicalization/Redundancy QA後(INVALID/REVIEW/NGは原因をRule7・語追加・QA失敗に分類して別集計)。Production関数をそのまま使い、retryはしない(ABCと同条件)。

## 5. 静的評価の限界
- ○の多くは「候補が無いので偶然満たす」型で、改善の証拠ではない。
- 実LLMがどの候補を採るかは未測定。受入2・3・4は特にLLM判断依存。
- 机上評価は、Phase 1-Aの改善shortlist(注釈`含む:`/`タグ:`の有無)に依存する部分がある。注釈が付かなくてもAfterは動くが、受入5の`含まれる:`利用は注釈なしでは働かない(一般則の【学ぶ単位】だけが残る)。
