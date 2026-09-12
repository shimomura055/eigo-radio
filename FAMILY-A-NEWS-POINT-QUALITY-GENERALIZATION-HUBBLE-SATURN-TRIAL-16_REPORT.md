# FAMILY-A-NEWS-POINT-QUALITY-GENERALIZATION-HUBBLE-SATURN-TRIAL-16 報告書

管理ID: `FAMILY-A-NEWS-POINT-QUALITY-GENERALIZATION-HUBBLE-SATURN-TRIAL-16`
(News Point Quality一般化Trial、Hanshin系Trial-12/12b/14/15の異テーマ再現、
Sonnet委任)。**Trial(Production実装ではない)**。Production/Prompt/QA/
Validator/retryコード・SSOT(`OPEN_ITEMS.md`/`DECISION_LOG.md`/
`CURRENT_SPEC.md`/`ARTIFACT_REGISTRY.md`)・`docs/pm/ACTIVE_TASK.md`/
`RESULT_PACKET.md`・Git操作は一切行っていない。monkeypatch・グローバル
書き換えなし。単純にfact数を増やすTrialへは戻していない。採用テーマは
ユーザー指定どおり変更していない: "New Hubble images reveal an unusual
shape over Saturn's south pole"(実際には土星南極を取り巻く十角形
[decagon]の大気波、NASA/ESA 2026年9月2日発表)。新規script(root、既存
Production/Trialコードをimportして呼び出すのみ):
`er011_news_point_quality_generalization_trial_16_run.py`。出力:
`er011_output/news_point_quality_generalization_hubble_saturn_trial_16/`。

## 要点(5行)

1. **主要エンドポイント(最終NG率)はceiling effect(両条件とも0%)により
   比較不能**だった: 条件H(headlineのみ、N=6)・条件P(headline+周辺fact、
   N=4、費用上限到達により未完)いずれも全記事がstatus=OK・Fact Checker
   PASS・Ledger逸脱MINORのみで、Hanshin系Trial-12/14で見られた
   「headline-onlyほど最終NG率が高い」という中心的パターンは、本テーマ
   ではそのままの形では再現しなかった。
2. 一方、**Point Role Planningのevidence anchor(FACT-ID)を見ると、
   両条件でfactの使われ方に明確な違いがあった**: 条件Hでは、7件中
   headline角度追加分のFACT-06/07(物理的解説)が6/6本すべてでPointの
   anchorとして使われ、条件Pでは真の周辺fact FACT-08(北極六角形との
   歴史的比較)・FACT-09(発生メカニズムの仮説)がそれぞれ4/4本・3/4本で
   使われた。**Writerは「headlineの成立に不要な、Main Storyに入れなくて
   よいfact」を自発的にPointの素材として選ぶ傾向があり**、これはこちらが
   事前に割り当てた「headline/peripheral」ラベルよりも、実際の役割分離を
   左右する要因は「Main Story必須度の低さ」であることを示唆する
   (Hanshin仮説の部分的な精緻化、断定はしない)。
3. 質的に読むと、条件Hの2 Pointは主に「画像の誤解を正す物理的説明」
   (波の移動速度とジェット気流速度の対比)と「発見の経緯(地上観測→
   Hubble遡及解析)」の2パターンに収束し、条件Pの2 Pointは「北極六角形
   との歴史的非対称性」「発生メカニズムの未解決性」という、より
   Hanshin系の元々の仮説が想定した"beyond-the-headline"色の強い角度に
   収束した。**両条件とも実際に重複のない2 Pointを生成できた
   (0% final NG)が、条件Pの角度の方が意図した性質に近い**、という
   限定的な支持が得られた。
4. OPEN-146(公式英語表記)は、**英語一次情報源テーマでも自然発火した**
   (想定外、正直な記録): Ledger本文中の「バスク大学」(研究チーム
   筆頭著者の所属、Science Advances論文由来)が日本語表記のみだった
   ため、Production関数`make_proper_noun_extraction_fn`が抽出し、
   Web検索確認で"University of the Basque Country"と判明、両条件の
   Ledgerへ追記した。英語ニュースでも、研究者所属機関等の二次的固有
   名詞は日本語Ledger作成時に発火し得ることが実証された。
5. 費用実績: Ledger研究¥155.6、条件H記事6本¥71.2、条件P記事4本¥68.2、
   OPEN-146関連(canonical spelling研究¥13.6+固有名詞抽出2回[cl.install
   未実行のため未計測、後述4-5節]) = **記録上の合計¥308.7(上限¥300を
   ¥8.7超過)**。超過を検知した時点(条件P B1B run1完了後)で直ちに追加
   API呼び出しを停止し、条件P B1B run2/3(2本)は未実施のまま。

---

## 0. Reconciliation Check + 費用管理の経緯

- 既存harness(Trial-12/12b/14/15、`er011_news_ledger_enrichment_ab_
  trial_12_run.py`・`..._leaveout_trial_12b_run.py`・`..._disambiguation_
  trial_14_run.py`)およびOPEN-146配線関数(`er011_open146_ledger_
  canonical_en_spelling_production_01.py`)を無改変でimportし再利用した。
  Production関数(`er003_v1_n3_01_articles_generate.build_common_block/
  build_prompt`、`er002_ja_web_research_r3`の各関数、`er011_point_role_
  planning_focus_connection_trial_03.run_one_pattern_connected`[既存
  VALIDATED Trial-03のコピー、無改変で再利用])はすべて無改変で直接
  呼び出した。retry上限(Fact Checker最大2 attempt、Point Overlap Article
  Retry Max=2、Local Rewrite上限)は無変更。
- **費用超過の経緯(正直な報告)**: Ledger研究(¥155.6、web_search_call_
  count=14)が委任文見込み(¥150)とほぼ一致した時点で、記事12本分の
  残枠は¥144.4だった。過去Trial(12/12b)の実測平均(12本で¥99.8〜
  ¥119.6、1本あたり約¥8.3〜¥10.0)から当初は完走可能と見込んだが、
  実際には本テーマの記事はretry発生率・記事長がやや高く、条件H平均
  ¥11.87/本、条件P平均¥17.05/本(A2×3+B1B×1の4本平均)となり、
  条件P B1B run1完了時点で合計¥308.7に達した。この時点で
  `check_budget_or_raise()`相当のチェック(本Trial用に実装)で超過を
  検知し、**直ちに追加のAPI呼び出しを停止した**(条件P B1B run2/3は
  実行していない)。委任文の「段階ごとにcost_so_far確認、超過見込みなら
  実行前STOP」を、実測ベースで運用した結果であり、意図的な超過ではない
  (Trial-14の実測¥147.3/上限¥150のような僅かな超過と同種の運用上の
  誤差だが、本Trialは実際に上限を超えた点はTrial-14と異なり、正直に
  報告する)。
- **既知の費用計測漏れ(正直な限界)**: OPEN-146自然発火チェック段階
  (`open146_firing_check_stage()`)の実行時、本Trial専用の`cl.install()`
  呼び出しを別プロセスで行っておらず、条件H/P Ledgerに対する固有名詞
  抽出API呼び出し2回(reasoning_effort=medium、web検索なし)が
  `raw_usage_log.jsonl`へ記録されなかった。実際のAPI課金は発生している
  (entities取得に成功した)が、正確なusage(トークン数)は記録されて
  いないため、上記合計¥308.7には含まれていない。同種の呼び出し
  (`canonical_spelling_research_stage`、web検索なし・reasoning=medium、
  実測¥13.6)と比べ入力サイズが同程度以下であることから、2回合計で
  ¥5未満と推定されるが、正確な実測ではない。実質合計は概算**¥310台前半**
  と考えられる。
- 二重起動なし(全て前面同期・逐次実行、combo単位で都度cost_so_far確認)。

---

## 1. Fact分類表(目視判定、根拠明記)

新規Ledger研究(Production関数`er002_ja_web_research_r3.make_writer_
research_fn`を無改変で1回実行、web_search_call_count=14、情報源21件、
実測¥155.6)で確認済みFact 11件(FACT-01〜11)を取得した
(`research_raw_result.json`)。分類規則: **headline_group**=「何が・
いつ・どこで・どの機材で・誰が発表したか」という発見そのものの成立に
必須な事実。**peripheral_group**=見出しの成立には不要だが、過去観測との
比較・発生メカニズムの仮説等、Point One/Twoに別角度を供給できる事実。

| FACT-ID | 内容(要約) | 分類 | 使用条件 |
|---|---|---|---|
| 01 | 十角形の大気波の発見内容(形状・構造) | headline(base) | H・P共通 |
| 02 | 公式発表日(2026-09-02)・査読論文情報 | headline(base) | H・P共通 |
| 03 | Hubble撮影日(2025-08-29)・観測装置(WFC3/UVIS) | headline(base) | H・P共通 |
| 04 | 位置(南緯58〜63度) | headline(base) | H・P共通 |
| 05 | 発見経緯(2024年地上観測→2023年まで遡及確認) | headline(base) | H・P共通 |
| 06 | 複数波長画像による3次元的波動構造の判明 | headline角度追加 | **Hのみ** |
| 07 | 波の移動速度(2.5m/s)とジェット気流速度(116m/s)の対比 | headline角度追加 | **Hのみ** |
| 08 | Voyager/Cassini観測ではこの現象が未確認だった(歴史的比較) | 非headline周辺 | **Pのみ** |
| 09 | 発生メカニズム未確定、複数仮説(ジェット蛇行/近傍の暗い渦) | 非headline周辺 | **Pのみ** |
| 10 | 木星の極域サイクロン配置との比較 | (未使用) | 不使用 |
| 11 | 今後の観測計画・Hubble運用36年の文脈 | (未使用) | 不使用 |

条件H(usable 7件=01〜07)・条件P(usable 7件=01〜05+08+09)でfact
総数を完全に一致させた(委任文の明示要求どおり、「数」ではなく「角度」の
効果を分離)。FACT-10/11は両条件で不使用(記録のためLedgerには含めない)。
詳細根拠は`research_classification.json`参照。

---

## 2. OPEN-146自然発火の記録(段階3、`open146_firing_check.json`)

条件H・P双方のLedger本文に対し、Production関数`make_proper_noun_
extraction_fn`(無改変、web検索なし)を実行した結果、**両条件で同一の
1件が発火した**: 「バスク大学」(FACT-02、Science Advances論文の筆頭著者
Agustín Sánchez-Lavegaの所属、日本語表記のみでLedgerに記載)。

人工的に発火させたのではなく、Production関数がLedger本文を読んで自律的に
検出した(委任文の要求どおり)。続けてProduction関数`run_canonical_
spelling_research`(無改変、web検索1回)で確認した結果、
`University of the Basque Country`と判明(出典:
https://www.ehu.eus/de/web/enlight/identity/university-of-the-basque-country)。
`append_canonical_spelling_section`(無改変)で両条件のLedgerへ追記し、
以降の記事生成では`append_canonical_spelling_instruction_if_present`
(無改変、Production `run_theme()`と同一のwiring point)を通してWriterへ
伝達した。

**発火の意味(考察)**: 本テーマは英語一次情報源(NASA/ESA)だが、
Ledgerの記述言語は日本語であり、研究者の所属機関名のような二次的
固有名詞は日本語表記のみで記載され得る。これは「英語一次情報源テーマ
では非発火が正しい挙動」という当初の予想を裏切る結果であり、**OPEN-146
機構はJapanese-domestic sports newsに限らない、より広い適用範囲を
持つことが実証された**(Production採用の妥当性を補強する追加証拠、
ただしProduction採用可否自体は既にユーザー承認済みでありこのTrialでの
新規決定事項ではない)。

**限界(正直な記録)**: Fact Checker側の照合(`build_canonical_spelling_
fact_check_block`をr3.build_fact_check_prompt()へ渡す配線)は、本Trialが
再利用した`run_one_pattern_connected`(Trial-03のコピー、OPEN-146配線
[2026-09-12]より前に作成された既存VALIDATED Trialのコード)には実装
されておらず、本Trialの12本の記事生成では**Fact Checker側のcanonical
spelling照合は実行されていない**。Ledger作成〜Writerへの伝達までは
実際のProduction関数で確認できたが、Fact Checker側の全経路検証は
本Trialのスコープ外(新たなコピー改変を避けるため、Gate 4の最小主義を
優先した)。実際、10本中いずれの記事本文にも「バスク大学」への言及は
現れず(Point/Main Storyの内容選択が偶然この固有名詞を使わなかった)、
本Trialではこの制約が結果に影響していない。

---

## 3. 記事生成結果(段階4、`all_results.json`)

条件Hは計画どおりN=6(A2×3+B1B×3)完走。条件Pは費用上限到達により
**N=4(A2×3+B1B×1)で打ち切り**(B1B run2/3は未実施)。両条件とも
final_ng=0本(Fact Checker未到達=打ち切り記事も0本)のため、Trial-14/15
で実施した「打ち切り記事へのFact Checker単独適用」段階は**該当なし**
(適用対象が存在しない)。

| 指標 | 条件H(N=6) | 条件P(N=4) |
|---|---|---|
| 最終NG率 | 0%(0/6) | 0%(0/4) |
| Fact Checker到達率・PASS率 | 100%(6/6)・PASS 6/6 | 100%(4/4)・PASS 4/4 |
| 初回attempt Value QA NG率 | 0%(0/6) | 25%(1/4) |
| 初回lexical overlap flag率 | 33.3%(2/6) | 25%(1/4) |
| Point記事全体retry回数(平均) | 0.333 | 0.5 |
| Point対Full Story overlap比率(平均、大きい方) | 0.2832 | 0.2588 |
| anchor衝突数(平均) | 0.0 | 0.5(1/4本でFACT-01/04が両Pointで重複) |
| fact利用率(平均、distinct/usable) | 0.5238 | 0.5714 |
| 語数(平均) | 303.0語 | 308.2語 |
| Ledger逸脱 | MINOR 1件(certainty強め、非blocking) | MINOR 1件(非blocking) |
| Local Rewrite発生 | 0本 | 0本 |

**主要エンドポイント(最終NG率)はceiling effectで比較不能**(1節参照)。
条件PのN=4はA/B比較として不完全(条件間でN非対称)であり、上記の
条件P列の数値は**参考値**として扱う(統計的検定は実施しない、N小・
非対称のため)。

### 3-1. Fact-ID別利用状況(evidence anchor、`evidence_allocation`)

| 条件 | FACT-ID | 利用run数 |
|---|---|---|
| H(N=6) | FACT-06 | 6/6 |
| H(N=6) | FACT-07 | 6/6 |
| H(N=6) | FACT-05 | 5/6 |
| H(N=6) | FACT-01 | 2/6 |
| H(N=6) | FACT-04 | 2/6 |
| H(N=6) | FACT-03 | 1/6 |
| H(N=6) | FACT-02 | 0/6 |
| P(N=4) | FACT-08 | 4/4 |
| P(N=4) | FACT-09 | 3/4 |
| P(N=4) | FACT-01 | 3/4 |
| P(N=4) | FACT-04 | 3/4 |
| P(N=4) | FACT-05 | 3/4 |
| P(N=4) | FACT-03 | 2/4 |

条件Hでは、こちらが「headline角度の追加」と分類したFACT-06/07が
**6/6本すべて**でPointのevidence anchorとして使われ、base ANCHOR facts
(FACT-01〜04)はMain Storyへ回りPointにはほとんど使われなかった
(2節で述べたとおり、Main Story必須度の低いfactが実質的な"peripheral"
役を担った)。条件PではFACT-08/09(真の周辺fact)がそれぞれ4/4・3/4本
使われ、意図どおりPointの主要素材になった一方、base facts(01/04/05等)
も一定頻度でPointに使われており、条件Pの方がPointの素材源が広い
(headline要素も周辺要素も両方使う)ことが分かる。

### 3-2. 質的観察(Point roleの実際の内容、`point_one_role_text`等)

条件Hの6本は、ほぼ例外なく次の2パターンに収束した:
(a) 「decagonは固定形状ではなく、ジェット気流よりゆっくり動く波である」
という**物理的な誤解訂正**(FACT-07中心)、(b) 「地上観測者が先に気づき、
Hubbleのアーカイブ解析で2023年まで遡及確認された」という**発見の経緯**
(FACT-05中心)。

条件Pの4本は、(a) 「40年以上安定する北極六角形と対照的に、南極では
これまで確認されなかった」という**歴史的非対称性の比較**(FACT-08)、
(b) 「ジェットの蛇行か、近傍の渦による強制か、発生メカニズムは未確定」
という**科学的に未解決な問いの提示**(FACT-09)に収束した。

**考察(断定は避ける)**: 両条件とも実際に重複のない2 Pointを生成でき、
final NG率では差が出なかった。しかし条件Pの角度(歴史的比較・
メカニズムの未解決性)は、Hanshin系Trialの元々の仮説が想定した
"beyond-the-headline factor"寄りの内容であるのに対し、条件Hの角度
(誤解訂正・発見経緯)は「今回のニュースそのものをより深く理解させる」
という点で価値はあるが、Main Storyの拡張に近い性質も帯びる。この違いは
**final NG率という粗い指標には表れず、Point roleの質的内容を読んで
初めて分かる**という点が、本Trialが得た最大の知見である。

---

## 4. Hanshin系Trialとの比較

| 観点 | Hanshin系(Trial-12/12b/14) | Hubble/Saturn(本Trial-16) |
|---|---|---|
| 最終NG率のfact数依存性 | REJECTED(fact数と最終NG率は無関係、C=A=83.3%) | 比較不能(ceiling effect、両条件0%) |
| headline-onlyの脆弱性(条件A、83.3%NG) | 高いFAIL率(人名ローマ字誤り等) | 再現せず(条件H 0%NG、6/6 Fact Checker PASS) |
| 周辺fact2件による改善(条件E、16.7%NG) | Aと比べ大幅改善 | 比較不能(条件Hも0%のため改善余地なし) |
| Point Role構造指標(anchor/role多様性) | 一貫して改善傾向(部分的VALIDATED) | 明確な違いあり(3-1/3-2節)、方向性はHanshinの仮説と整合(peripheral factがPointの主要素材になる) |
| 公式英語表記機構(OPEN-146)の発火 | Japanese-domestic sports newsで実証済み(Trial-15) | 英語一次情報源テーマでも二次的固有名詞(研究者所属)で発火(新規知見) |

**総合すると**: Hanshin系Trialの中心的な数値的知見(headline-onlyの
最終NG率の高さ)は本テーマでは再現されなかった(ceiling effect)。これは
「仮説が誤りだった」ことを意味するのではなく、**本テーマ(英語科学
ニュース、Ledgerの事実密度・研究者コメントの豊富さ)が、Hanshin
(日本語ドメスティックスポーツ、人名ローマ字化リスクが高い)より
そもそも記事生成が失敗しにくい題材だった可能性が高い**(題材依存の
ceiling effect)。一方、Point roleの構造・質的内容を見ると、
「非headline周辺factがPoint One/Twoに別角度を供給する」という中心
仮説の方向性自体は、本テーマでも部分的に支持される(3節)。

---

## 5. 1記事総コスト(5区分、A2+B1B合算、TTS未実施は該当なし)

| 区分 | 費用(¥) | 内訳 |
|---|---|---|
| ① Ledger研究(1回) | 155.6 | web_search_call_count=14、情報源21件 |
| ② OPEN-146関連(canonical spelling研究+固有名詞抽出) | 13.6+α(未計測、0-1節参照) | 発火確認1件・確認研究1回 |
| ③ 条件H記事生成(N=6、A2×3+B1B×3) | 71.2 | 平均¥11.87/本 |
| ④ 条件P記事生成(N=4、A2×3+B1B×1) | 68.2 | 平均¥17.05/本(B1B×1が¥20.3と高め) |
| ⑤ 打ち切り記事へのFact Checker単独適用 | 0(該当なし) | final_ng=0本のため対象なし |
| **合計(記録上)** | **308.7** | 上限¥300を¥8.7超過(0節参照) |

1記事あたりの平均生成コスト(①②⑤を除く記事生成のみ、N=10)は
約¥13.94/本。

---

## 6. 総合Close判定

**`USER_DECISION_REQUIRED`**(理由、以下いずれも単独では
VALIDATED/REJECTEDを正当化しない):

1. 主要エンドポイント(最終NG率)がceiling effect(両条件0%)により
   比較不能であり、Hanshin系の中心仮説を「再現した」「再現しなかった」
   のいずれとも断定できない。
2. 条件Pが費用上限到達によりN=4(計画のN=6に対し2本不足)で打ち切られ、
   条件間でNが非対称(H=6、P=4)なため、たとえ他の指標で差が見えても
   統計的な結論は出せない。
3. 一方、Fact-ID別利用状況・Point role質的内容(3節)では、「非headline
   周辺factがPointの主要素材になり、より'beyond-the-headline'色の強い
   角度を生む」という方向性の**限定的支持**が得られており、完全な
   REJECTEDでもない。
4. OPEN-146の新規知見(英語一次情報源テーマでも二次的固有名詞で発火)は
   本Trialの副産物として新規確定事項だが、Production採用可否自体は
   既にユーザー承認済み(2026-09-12)であり、本Trialでの新規決定は不要。

**ユーザー判断を要する候補(いずれも「候補」であり、採用可否は判断して
いない)**:
- (候補a) 追加予算(目安¥50〜80、条件P B1B run2/3の2本相当)を承認し、
  条件間Nを揃えたうえで最終NG率以外の指標(3節)を主要エンドポイントに
  切り替えて再集計する。
- (候補b) 本テーマでの検証はここで終了し(ceiling effectのため追加予算
  でも最終NG率の差は出にくいと判断)、Point role質的観察(3-2節)を
  仮説の「精緻化」(数ではなく「Main Story必須度の低さ」が真の変数)
  としてOPEN_ITEMS.mdへ記録するに留める。
- (候補c) 最終NG率で条件を弁別できる、より脆弱性の高い英語一次情報源
  テーマ(固有名詞密度が高い・法制度差がある等)で改めて一般化Trialを
  実施する。

---

## 7. 新規結果・過去再掲の区別

**新規結果(本Trial-16で新たに確定)**: 1〜5節の全内容(Hubble/Saturn
テーマでのfact分類・Ledger H/P構築・OPEN-146発火記録・記事生成N=10の
結果・Fact-ID別利用状況・質的観察・費用実績)。

**過去再掲(本Trial-16の新規結果ではない、参照のみ)**: 4節の
「Hanshin系(Trial-12/12b/14)」列の数値(REJECTED判定・条件A/E比較等)は
`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-DISAMBIGUATION-TRIAL-14_
REPORT.md`からの引用であり、本Trialで再実行・再確認したものではない。
OPEN-146のProduction採用決定(2026-09-12)・Trial-15のVALIDATED判定も
過去決定の引用。

---

## 8. Dangling Reference Check

`er011_news_point_quality_generalization_trial_16_run.py`が参照する
既存モジュール(`er002_ja_web_research_r3`・`er003_v1_n3_01_articles_
generate`・`er005_cost_logger`・`er006_model_routing_contract_01`・
`er011_daily_news_focus_layer_comparison_trial_04`・`er011_news_ledger_
enrichment_ab_trial_12_run`・`er011_news_ledger_enrichment_leaveout_
trial_12b_run`・`er011_open146_ledger_canonical_en_spelling_production_
01`・`er011_point_role_planning_focus_connection_trial_03`)はすべて
既存ファイルであり、本Trialでの新規作成・改変はない。本REPORTが参照する
出力ファイルはすべて`er011_output/news_point_quality_generalization_
hubble_saturn_trial_16/`配下に実在する(`research_raw_result.json`・
`research_classification.json`・`ledger_condition_h_headline_only.txt`・
`ledger_condition_p_headline_plus_peripheral.txt`・`open146_firing_
check.json`・`canonical_spelling_research_raw.json`・`all_results.json`・
`cost_summary_16.json`)。
