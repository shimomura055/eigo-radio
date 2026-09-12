# FAMILY-A-DISCOVERY-GENERALIZATION-TRIAL-12-OPUS-L2-INTERPRETATION-01 — Report

管理ID: `FAMILY-A-DISCOVERY-GENERALIZATION-TRIAL-12-OPUS-L2-INTERPRETATION-01`(opus-consultant、読み取り専用L2解釈)。実施日: 2026-09-12。

入力方式: **Token効率Phase 2(PM-TOKEN-EFFICIENCY-PHASE2-CONTEXT-PACKET-TRIAL-01)のAfter測定として、context packet方式**(`er011_output/discovery_generalization_wake_before_alarm_trial_12/opus_context_packet.md`、15,211字)**+ progressive disclosure**(必要と判断した個別ファイルの追加開示、下記「追加開示ログ」参照)で実施した。REPORT全文・`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`・`*_HISTORY.md`はOpusに一切読ませていない(Grepでの部分一致確認を除く)。

本タスクは**読み取り専用診断**である。ファイルの作成・編集・テスト実行・コード変更・Git操作・API呼び出しは行っていない。

本REPORTの提案(論点3の修正候補A/B/C、論点4の対照アーム設計・型分散設計、論点4③の報告フォーマット必須欄など)は**すべて候補**であり、採用・実装着手の可否はすべて人間ユーザーの判断に委ねる。

以下、Opus(opus-consultant)の出力を一字も改変せず転記する(HTMLエンティティ化されていた `<` `>` のみ、転記経路上の表示用エスケープと判断し原文の記号へ復元して転記。内容の追加・削除・言い換えは一切行っていない)。

---

## 要点(5行)

1. **Trial-12は「Trial-11より一段クリーン」ではない。軸を分けると逆**: プロセス軸(Local Rewrite 0・Fact Checker一発PASS・REVIEW 0)は改善したが、テキスト軸は悪化している(A2 point_one 71→**79語**でtolerance超過幅が拡大、near-duplicate A2 0→**1**、B1B 1→**2**)。しかもそのテキスト軸の悪化が、そのまま音声工程のHuman Review Lock(STOPPED)を引き起こしている。REPORTの総括は自らの最大失敗と因果が逆向きになっている。
2. **A2 point_oneのtolerance超過は「見落とし」ではなく「N=2/2で同方向に再現した系統的signal」**。Trial-11 Opus L2見落とし④と同一パターン、かつ超過幅は悪化。本Trialで最も再現性が高いのは成功側ではなく失敗側である。REPORT全文に`tolerance`/`語数`/`exceeds_`の語が**1件も存在しない**ことをGrepで確認した。
3. **再現性は部分的に「Prompt由来の型の再現」**。Trial-11 B1B `in_one_line`「the **meeting point** of fabric, moisture, bacteria, …」とTrial-12 B1B「the **meeting point** of a steady body clock and a learned expectation—**not proof of** a perfect internal countdown」が同一修辞slotで一致。house phraseはTrial-11の"quiet lesson"から"meeting point / not proof of a perfect X"へ入れ替わっただけで、型固定は継続している(Trial-11見落とし⑤⑥の再現)。
4. **RECONCILE-03の根本原因特定はコード照合で正確**(canonical側`text.split()`のみ/ASR側は`-`を除去しない、を実コードで確認)。ただし一般化予見が**弱すぎる**: これは「今後再発しうる」ではなく「**A2レベルで数値付きハイフン複合修飾語が2回出れば構造的に必ず再発する**」。狭い修正案は失敗クラスより狭く、"two-hour"/"thirty-minute"型を取り残す可能性が高い。
5. **Production採用判断には依然として致命的に不足**。対照アーム0、題材の型分散0(2件とも「身の回りの謎→機序説明」型)、comparison artifact不明。N=2は「Part Aの効果」の証拠にならず、現状で言えるのは「Part A条件下でA2 point_oneが一貫して長すぎる」ことだけ。

---

## 論点1: 再現性の解釈と一般化可能性

**判定: 「Part Aの効果の一般化証拠」にはならない。観測されたのは (i) 同一Promptの型再現 + (ii) 題材依存の交絡 であり、因果推論は不可能。**

根拠:

- **対照アームがない**(packet (a)論点4、(c) Trial-11論点5)。baseline(Part Aなし)で同テーマを走らせていないため、「Local Rewrite 0・FC一発PASS」がPart Aの効果なのか、テーマが平易だったのかを分離できない。Trial-11レビュー論点1が「最大の構造問題」としたものが未解消のまま2件目に進んでいる。
- **題材の型が同一**。Trial-11(タオルが臭う)/Trial-12(目覚まし前に起きる)はどちらも「身の回りの素朴な謎 → 生理/物理機序の説明 → 限界の言及」型。Trial-11レビューが要求した「争いのある消費者向け助言テーマ」「別の型」は1件も投入されていない。したがってN=2ではなく実質「同一型N=2」。
- **型再現の実証(新規)**: 追加で読んだ両Trialの`parts.json`の`in_one_line`/heading に、以下の共通鋳型がある。
  - 締め文: Trial-11 B1B「…the **meeting point** of fabric, moisture, bacteria, and the washing system around them.」 / Trial-12 B1B「…may be the **meeting point** of a steady body clock and a learned expectation—**not proof of** a perfect internal countdown.」 / Trial-12 A2「…**not proof of** a perfect inner timekeeper.」
  - heading: Trial-11「A wash is **not** a simple switch」 / Trial-12「A clock that can keep time, **but not** count perfectly」— いずれも否定・対比フレーム。
  - つまり「単一原因ではなく複合/接点である、ただし完全な○○の証拠ではない」という結論テンプレートが4記事すべてに共通。これは題材が変わっても出力の骨格が変わらないことを示し、「再現した」という観測の一部はPromptの鋳型が再現しただけと解釈すべき。
- **一方で新規の真の改善もある**: `cross_point_overlap`はTrial-11が4値すべて0.22〜0.24だったのに対し、Trial-12はA2 0.149/0.226、B1B **0.037/0.024**。特にB1Bの1桁改善は題材依存だけでは説明しにくく、Point分化に関しては本物の改善候補。ただしこの指標は**記事内**のPoint間距離しか測らず、上記の**記事間の型重複**はゼロ測定である(論点2③参照)。

---

## 論点2: 観察10項目の解釈

| 項目 | 私の判定 | 根拠 |
|---|---|---|
| ①Full Story/Point構成 | **条件付き成立**。構成の器は成立しているが、A2 point_oneはtolerance超過(79語)で「成立」と「規格内」を混同してはならない | (b)実測表。追加確認: A2 point_one本文は独立3研究(ACTH 1時間前/前頭右 30分前/心拍 3分前)を1段落に詰め込んでおり、超過は偶発ではなく「複数発見の列挙」に起因する構造的なもの |
| ②言い換え回避 | **QA PASSは額面どおりでよい**(Point↔Full Storyの言い換えは実文面でも見られない)。ただし別種の重複が残存 | A2 part1は機序、point_oneは段階性で内容が異なる。B1B point_one(実験値)はpart1(概説)の詳細化で反復ではない |
| ③Pointごとの発見差 | **記事内の差は実在。ただし「多様性」は未測定** | A2は生理準備 vs 睡眠段階、B1Bは時計精度 vs 練習効果で実文面も別内容。しかし論点1の型固定は本指標に現れない。指標が隠しているのは「記事間の多様性」であり、これは`cross_point_overlap`では原理的に測れない |
| ④保険文 | **0件は題材依存でほぼ説明可(Trial-11論点1(a)の説明がそのまま当てはまる)。加えてregexの射程外にcaveat文が複数実在** | 実文面のcaveat: A2「But research does not yet show that the body can predict the exact moment an alarm will ring.」、B1B「But this is not proof that the body can read an alarm with perfect accuracy.」「…a broadly reliable ability is not established.」「Most studies tested planned waking, not accidental waking…」。Trial-11見落とし⑨(独立caveat文を検出しないregex)が**Trial-12でも有効なまま**。「保険文0件」は「注意喚起文が0件」を意味しない |
| ⑤Ledger Deviation/Local Rewrite | **副作用の再現有無は評価不能で正しい。ただし「0件=改善」と読むのは誤り** | Rewriteの前提(FC指摘)自体が発生していない。Trial-11論点2の副作用(near-duplicate文生成)は未検証のまま据え置き、という扱いが妥当 |
| ⑥Fact Checker | **「悪化なし」は妥当だが弱い証拠** | Trial-11のREVIEW_REQUIREDはB1B 1/2、Trial-12は0/2。N=2同型題材でのbaselineなし比較のため、率の議論に統計的意味はない。advisory 0件はTrial-11見落とし①(FCがLocal Rewrite出力を見ない構造的blind spot)がRewrite 0のため今回発火しなかっただけで、gapは残存 |
| ⑦Point Overlap/Value QA | **数値具体性の逆転は解消していない。新規事例を1件発見** | A2は「the **front-right** part of the brain」と側性を明示、B1Bは「a **front** part of the brain」と側性を落としている。**易しいA2が難しいB1Bより解剖学的に詳細**という逆転。Trial-11見落とし②と同型の新規発生。一方、数値面ではB1B(23.5/24.6時間、11人、82%、643人)>A2(hundreds of people)で正常方向 |
| ⑧Support/Key Phrase | **PASSの中身は本packetでは検証不能**(成果物本文が渡されていない) | packetはselection/canonicalization/redundancy「全PASS」の集計値のみ。実文面未確認。ここは判断を保留すべき箇所で、断定的に「PASS妥当」と書くのは不誠実 |
| ⑨A2/B1成立性 | **同一見落としパターンの再現。かつ悪化** | Trial-11 A2 71語→Trial-12 **79語**。Trial-11 A2 71語が`exceeds_tolerance_upper=true`である事実からA2のtolerance上限は≦70語と逆算でき、79語は**少なく見ても13%超過**(Trial-11は最大でも1.4%超過)。Grep実測: Trial-12 REPORT本文に`tolerance`/`語数`/`word_count`/`exceeds_`の**いずれも0件** |
| ⑩音声工程 | **記事テキスト軸の悪化の直接の帰結。tool側bugだけの話にすべきでない** | 下記 |

**⑨の重みについて(最重要)**: これは「報告漏れ」ではなく、**Discovery Focus Module Part Aの系統的副作用の候補**として扱うべき。理由は (i) A2 point_oneがtolerance超過したのが2/2、(ii) 超過方向が両方とも上方、(iii) 超過幅が拡大、(iv) 実文面で超過の機序(Part Aが「異なる発見」を要求→writerが複数研究を列挙→A2の語数枠を突破)が説明できる、の4点。一方で報告体制側の問題も重い: **前回Opus L2が明示的に指摘した指標が、次のTrialの報告フォーマットに組み込まれていない**(Trial-11論点5が観測6指標の1つに「tolerance逸脱記録」を挙げているにもかかわらず)。レビュー指摘が次Trialの計測項目にフィードバックされない運用gapがあり、これはTrial単体の質より重い構造問題。

**⑩の追加解釈(packetにない論点)**: A2 part1の該当2文は
```
Light helps this clock match the twenty-four-hour day.
… usually matched a twenty-four-hour day.
```
で、記事側QAは`near_duplicate_sentence_pairs` ratio **0.554**として**検出していたがPASSさせた**。下流の音声Repetition QAは同じ現象を**ブロッキング**扱いにした。すなわち**層間で閾値の整合が取れていない**。したがってこの事象には独立した2つの欠陥がある: (A) tool側のトークン境界非対称(RECONCILE-03)、(B) 記事側で0.554のnear-duplicateを通す一方で音声側で止める層間不整合 + A2レベルとして実際に文章が冗長。(A)を直しても(B)は残り、A2本文の「同一4語句を2文で反復」という品質問題はそのまま残る。RECONCILE-03と本Trial REPORTはいずれも(B)を論点化していない。

---

## 論点3: RECONCILE-03の根本原因特定の正確性と修正案の評価

**(1) 根本原因特定は正確。コードで直接確認した。**

- `er011_open121_repetition_qa_production_01.py:393-395`
```python
def _normalize_tokens(text):
    text = re.sub("—", " ", text)
    return [_normalize_token_numeric_equiv(w) for w in text.split()]
```
→ canonical側は空白分割のみ。`"twenty-four-hour"`は1トークンで残る。
- `er008_disfluency_qa_18.py:44-45`
```python
def _normalize_token(word: str) -> str:
    return re.sub(r"[.,!?\"'…]", "", word.strip().lower())
```
→ 除去対象に`-`が**含まれない**。ASR側word-level出力`"24"`, `"-hour"`はそのまま2トークン。
- `_NUM_WORD_TO_DIGIT_EN`(379-382行)は`two`〜`twelve`のみ。
→ **canonical 2トークン列 `["twenty-four-hour","day"]` と ASR 3トークン列 `["24","-hour","day"]` は原理的に一致しない**。RECONCILE-03の (a)レンジ外 + (b)トークン境界非対称、および「OPEN-121/RECONCILE-02はこのケースに構造的に無関係」という結論は**いずれも正しい**。仮にレンジを2〜24へ広げても(b)が残るため誤flagは解消しない、という優先順位付け((b)がより根本的)も妥当。

**(2) 一般化予見は正しい方向だが弱い。過小評価のリスクがある。**

- packetの表現「時間・期間・年齢等の複合修飾語を含む今後の記事テーマで再発しうる」は確率的すぎる。実際には**決定論的**: A2レベルのcanonical本文に数値付きハイフン複合修飾語が2回出現し、その語句を含むn-gramをASRが反復検出すれば、canonical repeat countは必ず0になり必ずNGになる。
- **再発条件にレベル依存性がある(新規発見)**。同一記事のB1B point_oneは`"24-hour day"`と**算用数字**で書かれており(`b1b/parts.json`)、A2だけが`"twenty-four-hour"`と綴りで書かれている。さらにTTS前処理側は`er003_v1_n3_01_tts_generate.py:582`で`(?<!-)`否定後読みによりハイフン複合数を**意図的に変換しない**(ER-010-NO9再発防止の既存設計)。よって「A2の綴り表記 → TTSは綴りのまま発話 → ASRは数字で書き起こす」という経路が固定されており、**A2レベルが構造的に高リスク**。この非対称性はRECONCILE-03にもTrial-12 REPORTにも記載がない。
- したがって「横断集計9,832ファイルで同型1件」は**頻度の低さの証拠として使えない**。過去記事に「A2 + 数値付きハイフン複合 + 2回出現」が揃った例が1件しかなかったことを示すだけで、Discovery系のように数量を扱うテーマが増えれば発生率は上がる。

**(3) 修正案の評価(いずれも候補。採用可否はユーザー判断)**

- **候補A: 狭い修正(RECONCILE-03 prototype、tens-ones-付属語の3分割ハイフン複合のみ)**
  - 利点: 影響面積が小さく、既知true positive無変化をprototypeで確認済み、回帰risk最小。
  - **重大な欠点**: 失敗クラスより狭い。packetの記述どおり「tens-ones-付属語の3分割」限定なら、`two-hour`/`three-minute`(2分割・辞書レンジ内)、`thirty-minute`(2分割・レンジ外)、`10-year-old`(数字始まり)といった**同じ機序で同じように壊れる隣接ケースを取り残す**。つまり「今回の1件だけ塞ぐ」修正になり、次回別形で再発した際に再度Human Review Lock→Trial中断を招く。なお私はprototypeコード本体を読んでいないため、この評価はpacketの記述に依存する条件付き判定。
- **候補B: 対称正規化層(ハイフンを両側で一様に分割 + 数詞↔数字の同値化を拡張)**
  - 利点: failure classを面で塞ぐ。canonical/ASRのトークン粒度という根本非対称を除去。
  - 欠点/risk: (i) A-Family全Production音声経路の共通層であり、span index・`min_words`閾値・`find_repeated_spans`の最長一致挙動に影響しうる(トークン数が変わるため3語spanの意味が変わる)。(ii) 同値化拡張はtrue positiveのmaskingを増やす方向に働く(canonical repeat countが偶発的に2に達しやすくなる)。(iii) `(?<!-)`が守っているER-010-NO9の不変条件と干渉しないことの確認が必要。よって回帰35件では不十分で、既存Human Review queueの遡及再判定(true positive維持の確認)が必須。
- **候補C(packetに無い軸): 発生源側で抑える**
  - A2 writerに対し「数値付き複合修飾語は算用数字で書く」表記規約を与える(B1Bが既にそうしている)、または記事側near-duplicate閾値(今回0.554をPASS)を音声側QAと整合させる。(A)のtool修正と独立に効き、音声layerに到達する前に潰せる。ただしPrompt制約の追加はDiscovery Part B案1が不採用となった経緯(packet (c) `CURRENT_SPEC.md` 794-810行)と同じ「Prompt制約で品質を作る」方向であり、同じ懸念が当てはまる。
- **推奨の考え方**: 緊急度の観点ではA(狭い)で今回のLockを解くのが安全だが、**Aだけで閉じると「修正済み」という誤った安心を生む**。Aを採るなら「残余の隣接ケースは未修理」であることをOPEN項目として明示的に残すのが最低条件。恒久解はB+C。いずれもProduction採用可否はユーザー判断。

---

## 論点4: Production採用判断に持ち込むための不足材料

Trial-11レビュー論点5の推奨設計(packet (c) 145-167行)に対する充足状況:

| 要求 | Trial-12の充足 | 
|---|---|
| (1) 対照アーム(baseline vs Part A)= **最重要・必須** | **未充足**(0本) |
| (2) 題材の型を意図的に分散(争いのある消費者向け助言型を最低1つ、Household/Towels以外の型を1つ以上) | **未充足**。「身の回りの謎→機序」型のままで、型はむしろ固定化の証拠が増えた(論点1) |
| (3) 3テーマ×2条件×A2/B1B×N=3=36本 | **1テーマ×1条件×2本**(進捗 5.6%) |
| (4) 観測6指標(REVIEW率・保険文hit・caveat文カウント・Rewrite件数と語数差・**tolerance逸脱記録**・記事間の型重複) | **部分充足**。REVIEW率・保険文hit・Rewrite件数は取得。tolerance逸脱はJSONに存在するがREPORT本文に未記載。**caveat文カウントと記事間型重複は未実装**(この2つが今回まさに問題を隠した指標) |
| (5) comparison.html(目視多様性artifact) | packet記載なし=**不明/未確認**。Trial-11も未生成 |

**不足材料(何件・どの条件・何を観測すべきか)**

1. **対照アームなしのN増しは何本走らせても採用判断材料にならない**。これは費用の問題ではなく設計の問題。次に1本でも走らせるなら、まず「同一テーマ×baseline条件」を先に埋めるべき。現状のTrial-11/12は、baselineを後から足せば事後対照として再利用可能(条件固定・同一Ledger)なので、ここは回収可能。
2. **型分散を最低3型**: (i)謎解明型(既に2件)、(ii)争いのある消費者向け助言型(保険文の発火条件を作る=Part Aの効果を検出できる唯一の条件)、(iii)Trend/News型など機序説明にならない型。(ii)がない限り「保険文0件」は情報量ゼロのまま(Trial-11論点1(a)、Trial-12でも同じ)。
3. **報告フォーマットを先に固定する(最優先・費用ゼロ)**: 各Trial REPORTに (a) section別word count + target/tolerance上限 + PASS/FAIL、(b) near-duplicate最大ratioと採用閾値、(c) caveat文(regex外の独立注意文)の手動カウント、(d) 記事間テンプレート類似(`in_one_line`/heading の定型句一致)、(e) 音声layerでのブロック発生の有無、の5項目を必須欄にする。今回の見落としは(a)欄がないことで2回連続発生している。
4. **費用の再見積り(新規)**: Trial-12実測¥141.55/2本=約¥70.8/本(音声込みStandard)。Trial-11レビューの「36本=¥1,100〜1,300」は音声込みでは合わず、36本は**約¥2,500規模**になる。内訳から記事側は¥78.98/テーマ(2レベル分・researcher込み)なので、**記事レベルのみで対照アームとN増しを回せば18 run ≈ ¥1,400程度**で推奨設計の主要部分が収まる。音声は代表subsetのみに限定するのが費用対効果上合理的(候補、判断はユーザー)。
5. **採用判断の最小到達点**: 「baselineあり × 3型 × A2/B1B × N=3」で (i) REVIEW率がbaselineより悪化しない、(ii) A2 point_oneのtolerance超過率がbaselineより有意に悪化しない(**現状2/2で超過なので、ここが最初に落ちる可能性が高い**)、(iii) 記事間テンプレート一致がbaselineより増えない、の3条件。現時点で(ii)(iii)は不合格方向の兆候があり、**現状のデータでProduction採用を検討できる段階には全く達していない**。

---

## 論点5: 新規結果/過去再掲/進行中の区別(5行)

1. **新規結果(妥当)**: 3節記事レベル観測、4.1節Human Review Lock/cool-down N=1、6節費用実測¥141.55、`cross_point_overlap`のB1B 1桁改善(0.037/0.024)、9節部分player設計 — Trial-12 REPORT 10節の自己申告どおり。
2. **新規結果だが未報告(自己申告の欠落)**: A2 point_one 79語のtolerance/target超過、B1B point_two 64語のtarget超過、near-duplicate件数の増加(A2 0→1、B1B 1→2)。これらは`comparison_vs_towels_trial_11.json`にあるがREPORT本文に不在で、10節の「新規結果」にも「過去再掲」にも分類されていない。**10節の区分は不完全**。
3. **過去再掲(妥当)**: 3節Trial-11列、4.6節Precheck一般論、OPEN-145/121/146の非発火(=既知層が今回も無関係だったことの再確認)。
4. **過去指摘の未解消の再現(区分外)**: Trial-11見落とし④(tolerance超過の無言及)、⑤⑥(型/house phrase)、②(数値具体性逆転)、⑨(caveat文regex射程外)が**いずれも再現**。Trial-11論点2の副作用検証はRewrite 0のため評価不能で据え置き。
5. **進行中・未結果**: RECONCILE-03 prototypeのProduction実装(4項目ユーザー判断待ち、repoコード未変更)、A2音声のUSER_DECISION_REQUIRED、Discovery仕様は`VALIDATED(Trial)`のままでProduction不承認(packet (c) `CURRENT_SPEC.md` 794-810行)。

---

## 追加開示ログ

| 対象 | 理由 | 実読込量(概算) |
|---|---|---|
| `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_wake_before_alarm_trial_12\a2\parts.json` | 論点2②④⑦⑧⑨・⑩の実文面検証(packetは集計値のみ) | 約1,900字 |
| `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_wake_before_alarm_trial_12\b1b\parts.json` | 同上(レベル間比較・数値具体性逆転の確認) | 約2,300字 |
| `C:\Users\tensh\eigo-radio\er011_open121_repetition_qa_production_01.py` 360-429行 | 論点3のroot cause正確性のコード照合 | 約2,600字 |
| `C:\Users\tensh\eigo-radio\er008_disfluency_qa_18.py` 44-45行(Grep -A8) | ASR側`_normalize_token`がハイフンを除去しないことの確認 | 約400字 |
| `C:\Users\tensh\eigo-radio\er003_v1_n3_01_tts_generate.py` 576/582行(Grep) | `(?<!-)`の実在位置確認(packetの帰属先検証) | 約200字 |
| `C:\Users\tensh\eigo-radio\FAMILY-A-DISCOVERY-GENERALIZATION-WAKE-BEFORE-ALARM-NPLUS1-TRIAL-12_REPORT.md`(Grep only、本文未読込) | 「tolerance超過が本文未記載」の事実検証 → **0件一致で確認** | 約50字(出力なし) |
| `C:\Users\tensh\eigo-radio\er011_output\discovery_generalization_towels_trial_11\{a2,b1b}\parts.json`(Grep、4フィールドのみ) | 論点1の「型固定」を印象論でなく証拠で判定 | 約800字 |

合計 約8,250字(packet 15,200字 + 追加8,250字 = 約23,450字。Before代替値135,397字の約17.3%)。REPORT全文・`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`・`*_HISTORY.md`は**一切読んでいない**。

---

## packet不足点(Phase 2改善用)

1. **記事本文(`parts.json`相当)が未転記**。観察10項目のうち②④⑦⑧は本文なしでは判定不能で、結局4ファイル読むことになった。A2/B1Bの`parts.json`は合計約4,200字で、packetに転記すればProgressive Disclosure 4回が0回になる。**最も費用対効果の高い改善点**。
2. **tolerance/targetの実数値が欠落**。booleanのみのため「79語がどれだけ超過か」を逆算(Trial-11 71語の超過事実から上限≦70)で推定するしかなかった。上限値そのものを表に入れるべき。
3. **near-duplicate pairの実文が未転記**。ratio 0.554という数値はあるが、どの2文かがpacketにないため、記事QAと音声QAの層間不整合(本レビューの主要発見)に到達するには本文読込が必要だった。
4. **Support/Key Phraseの成果物本文が未転記**。論点2⑧を「検証不能」として保留せざるを得なかった。論点に立てるなら材料も入れるべき(あるいは論点から外す)。
5. **`(?<!-)`の帰属が誤り**。packet (c) 111行は「OPEN-121実装が`(?<!-)`否定後読みで除外」と書いているが、実際の`er011_open121_..._01.py`の実装は辞書の**完全トークン一致**で除外しており、`(?<!-)`は`er003_v1_n3_01_tts_generate.py:582`(TTS前処理側)にある。修正設計を検討する際に実装箇所を誤認させるため要訂正。
6. **レベル間の表記差(A2 "twenty-four-hour" vs B1B "24-hour")がpacketに無い**。これがfailure modeのレベル依存性(A2が構造的高リスク)という一般化の核心だったが、`parts.json`を読むまで分からなかった。
7. **Trial-11の`in_one_line`/headingが未転記**。Trial-11見落とし⑤⑥(型/house phrase)の継続性判定を求める論点があるのに、比較対象の実文が無かった。定型句4行(約600字)の転記で足りる。
8. **comparison.htmlの生成有無が未記載**。Trial-11レビュー論点5が必須とした項目であり、論点4の充足判定で「不明」にせざるを得なかった。
9. (軽微)費用の按分単位(¥78.98がテーマ単位かレベル単位か)が曖昧で、論点4の規模見積りに推定を挟む必要があった。

---

本レビューは読み取り専用で実施し、ファイルの作成・編集・テスト実行は行っていない。仕様変更・修正実装(論点3の候補A/B/C、論点4の設計案、報告フォーマット必須欄化を含む)は**すべて候補**であり、Production採用・実装着手の可否は人間ユーザーの判断に委ねる。
