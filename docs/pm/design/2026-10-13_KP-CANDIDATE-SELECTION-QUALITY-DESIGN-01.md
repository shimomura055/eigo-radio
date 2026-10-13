# KP-CANDIDATE-SELECTION-QUALITY-DESIGN-01 設計書(正本)

管理ID: FAMILY-X-KP-CANDIDATE-SELECTION-QUALITY-DESIGN-01 委任_01 / 2026-10-13(委任_02で訂正: Opus独立レビュー(条件A)必須修正6点+推奨修正を反映。変更箇所に「[委任_02訂正]」)
Status: **設計案提出・USER_DECISION_REQUIRED**(未承認。`APPROVED_FOR_PRODUCTION`ではない。Production code/Prompt/DB無変更)
費用: JPY0(LLM/TTS/ASR呼出0。Wiktionary公開APIを既存関数で1回だけ照会[17語、api_calls=1、無料]。委任_02ではWiktionary追加照会も行っていない)
モデル: 本委任自体はLLMを使っていない。引用するTrial/実runは `gpt-6-luna`(Production同一)。
読み取り元の証跡は全て既存ファイル。本委任で新規に作ったのは読取・集計scriptと `er064_output/kp_candidate_selection_design_01/` の結果JSONのみ。
注意: ABC/Phase Dは**v4原稿**、Coffee v5 Production実runは**v5原稿**(文面が違う。Std v5は "time lag" を含まず "feels like there is a delay")。以下で両者を区別する。

---

## 0. 先に結論(プロジェクト責任者向け)

1. **`lag`が残り`time lag`が選ばれなかったのは「抽出段」の問題**。選定LLMは候補に無い`time lag`を選べない。`time lag`はWiktionary(辞書)に実在する複数語表現(今回の照会で`True`)なのに、辞書への問い合わせ上限(60件)の並び順(語数昇順、内容語数降順、アルファベット順=`er027_..._stage1.py` L601のキー)のうち、**2語・内容語2語のグループ内ではアルファベット順**になるため、Advでは76番目で問い合わせ対象外だった(v4/v5とも76位)。[委任_02訂正: 「実質アルファベット順」を正確化]
2. **`in the ring`への短縮は「LLM補助抽出(Phase D extractor)の出力そのもの」**。Adv原稿は "putting the two figures in the ring" で、抽出LLMが最初から`span`/`core_span`とも `in the ring` と返した。Pythonの縮約・包含重複除外・正規化で短くなったのではない(Stdは `two numbers in the ring` と返しており、同じ抽出Promptでも原稿・runで揺れる)。
3. 既存機構は「Idiom・Collocation・単語・記事独自比喩」を**区別していない**。使える情報は辞書の出典ラベル(Wiktionaryの`idiom`は非透明性を意味しない)と、選定LLMが事後に付ける属性だけで、記事独自比喩かどうかを示す項目は存在しない。
4. 辞書・頻度表(CEFR-J/wordfreq)では「既知/未知」「連語の定着度」を**機械的に確定できない**ことを実測した(`right away`=A1+A1、`come with`=A1+A1、`show up`=A2+A2で区別不能。wordfreqの複数語Zipfは `time lag`=`lag`=3.67で連語の強さを表さない)。ここはハードルール化せず、LLM判断+上流は「注釈」にとどめる。
5. 提案は5パッケージ(§3〜§5, §8): **U(上流の機械処理、費用0)/P(選定guidance追記、Family X限定、+約400token)/E(LLM補助抽出v4=OPEN-325のb1、ユーザー判断待ち)/R(Rule7ヘッドワード=OPEN-310)/X(解説ページ用レコード、設計のみ)**。現行6指標の順序は維持し、指標は増やさず「タイブレーク1文+適格性注釈」で足す。
6. 机上の期待[委任_02訂正で弱め]: 受入7例のうち、機械的に実現できる見込みは`time lag`がshortlistに入り`lag`が除外されること(ただし**パイプライン全体での到達は未検証=△**。照会結果を注入した`run_stage1_and_shortlist`全体の再生が必須、§9 Step1)。`in the ring`型の回避は、発生源(Pkg Eの抽出Prompt)の粒度指示+断片注釈が必要で、Pkg U単独では実現しない(△)。記事独自比喩のImportant除外とStd改善はPkg P+Eが必要でLLM判断依存(△)。有料Trialは未実施(§9に計画)。
7. [委任_02追加] **Std側の改善(受入例7)は、OPEN-325(b1)=「本文全文をLLMへ送らない」原則(`CURRENT_SPEC.md:1847`)の改訂判断(Pkg Eの採否)に依存する**。Pkg U/P(上流・guidance)だけではStdの供給乏しさ(非透明な比喩候補が供給0)は解消しない。
8. [委任_02追加] U1(希少語を含む2語の優先)は唯一の案ではない。**「照会予算の拡大」(1回50件・待ち1.5秒なので、Advの2語プール312件でも約7回・十数秒で全件照会可)との比較**を§3-3に追加した。K=10固定は推奨せず、Step1の結果を見て案を決める。

---

## 1. 現行経路整理(Production、Family X DB Hybrid)

```
記事(level本文)
 → [1] stage1: n-gram生成(1〜5語, er023_key_phrase_db_extraction.py:85)
        → DB照合(CEFR-J / NGSL / Wiktionary idiom・phrasal・proverb の見出し一致 + 先頭語lemma + 不規則活用救済)
        → 重複除去 → 機械gate(too_easy/unnatural) → 文脈不一致除外 → lemma近重複merge
        → phrase_survivors を (db_match_count降順, canonical_formアルファベット順) に整列 [er030_..._core_01.py:384-385]
 → [2] 重要名詞句: 本文で2回以上反復する複合名詞ヒューリスティック(find_repeated_compound_noun_candidates, er027:432)
 → [3] Wiktionary online multiword照会: 未一致の2-3-gramのうち先頭60件のみ [core:442-444, budget=60 @core:64]
        先頭60件の並び = (語数昇順, 内容語数降順, アルファベット順=2語・内容語2語のグループ内はアルファベット順) [er027_..._stage1.py:601]
 → [4] 希少単語(rare single word)候補: Zipf<=3.3等のヒューリスティック+Wiktionary lemma確認(budget15) [core:195-262]
 → [5] shortlist: phrase上位15(cap) + 重要名詞句 + word(不足分を希少度順で補う、最低5) [er027:639-659]
 → [6] 選定LLM(Strategy Lテンプレート + _FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE)
        candidate ID方式で5件(topic1+important4)+backup1。構造validator(語数1〜5、4+1構成、ID enum等)
 → [7] canonicalization(LLM): display_phrase→key_phrase正規化 + QA12項目。
        Rule7 = key_phraseは source_span 内の連続部分文字列、または閉じた表(_PERSON_DEPENDENT_TO_GENERIC)による1対1の人称置換のみ [er003_key_words_canonicalization.py:286,304,397]
 → [8] Redundancy QA(LLM): 5件の意味重複。NGなら選定からretry(最大2回)
 → 未選択候補は kp_auxiliary_candidates.json に「未検証の参考候補」として保存(v5: Std 21件/Adv 27件)
```

- **Topic/Importantの役割は[6]の選定LLMが選定と同時に付ける**。構造validatorは「topic1+important4」のenum検証のみ。canonicalizationは役割を継承するだけ。
- 表現の分類(`phrase_type`: word/noun_phrase/phrasal_verb/collocation/idiom/technical_term/prepositional_phrase、`portfolio_category`、`inference_transparency`、`topic_exposure_dependency`等)は**選定LLMの出力フィールド**で、候補供給にも検証にも使われない(`er003_key_words_min_unit.py:108-114`)。
- 選定Prompt現行本文(逐語)は `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_v5_ms_01/b1b/key_phrases/key_phrases_db_hybrid/keywords_selector_prompt.txt`(全文)。優先順位は template 11行目:
  > 優先順位は、初回音声での処理困難、未知の可能性、瞬時の推測困難、本文の事実・感情・面白さへの影響、記事内重要度、汎用性の順です。
- Family X追加guidance(`er030_key_phrase_db_hybrid_source_reference_contract_01.py:177-196`)は「重要語区分から1件以上」「残りはphrase/idiom/phrasal verb区分を優先」「CEFR難易度を主要な判断軸にしない」「candidate ID・surface_echo・backup_item」のみ。**level差・非透明性・まとまり・役割別基準の記述は無い**。さらにStdの選定Promptも冒頭が「以下の**B1**英語記事本文から」のままで、a2とb1bで同一文面(v5 `a2/key_phrases/key_phrases_db_hybrid/keywords_selector_prompt.txt` 1行目で確認)。

---

## 2. 具体例で問題が生じた工程の原因分析(実証)

実証ファイル(新規作成分): `er064_output/kp_candidate_selection_design_01/` の `upstream_trace_01.json`, `budget_sim_01.json`, `wiktionary_probe_01.json`, `containment_pairs_01.json`, `containment_pairs_rare8_01.json`, `known_likelihood_signals_01.json`, `closed_class_fragments_01.json`。既存: `er064_output/kp_idiom_trial_01/phase_a|phase_d/`, `er064_output/kp_idiom_priority_abc_01/`, Coffee v5実run。

| # | 例 | 問題の工程 | 実証 |
|---|---|---|---|
| Q1 | `lag`が残り`time lag`が選ばれない | **抽出段(Wiktionary online lookupの予算)**。選定段ではない | (1) v5 Adv選定Promptの候補一覧に `C31 "lag"(word, occ1, ngsl_family)` はあるが `time lag` は無い。(2) 選定LLMは `surface_echo:"time lag"` と書きながら `source_candidate_id:C31(lag)` を指した=意図は`time lag`だったが候補に無かった(`b1b/key_phrases/keywords_canonicalized.json` rank1)。(3) 未一致2-3-gram poolは694件で`time lag`は**76番目**=予算60の外(`upstream_trace_01.json`、v4 Advでも76番目)。(4) 既存関数での照会で`time lag`は**Wiktionaryにヒット**(`wiktionary_probe_01.json`)。予算内なら拾えた。(5) Std v5原稿には"time lag"が無い(delay表記)ためStdでは該当しない。 |
| Q2 | `in the ring`への短縮 | **LLM補助抽出(Phase D extractor v3)の出力そのもの** | `phase_d/m1_recheck_02/coffee_adv/run1/extractor_raw.json`: `span:"in the ring", core_span:"in the ring"`(原稿は"putting the two figures in the ring")。`narrow_to_core_span`(`er064_kp_idiom_trial_01_extractor.py:130`)はspan⊃core_spanの時だけ働くが、spanが既に3語。包含重複除外は0件(`PHASE_D_REPORT_02.md` §4-1)。Std run1は同一Promptで`two numbers in the ring`(5語)を返しており、粒度は原稿・runで揺れる(M1表: `numbers in the ring`/`two figures in the ring`も出現)。**Rule7・正規化は短縮に関与していない**。[委任_02訂正] 構造的な寄与要因: (1)`KEY_PHRASE_MAX_WORDS=5`の語数上限(`two figures in the ring`は5語で上限内だが、`putting the two figures in the ring`は6語で上限超過のため、抽出LLMは動詞側を落として前置詞句から切り出しやすい)、(2)選定Prompt 5行目「完全文、主語と有限動詞を持つ節、記事固有の長い説明は禁止です」(`keywords_selector_prompt.txt`)が「長い=記事固有の説明」を避ける方向に働き、修飾先の名詞(`figures`)を落とした短い前置詞句を促す。 |
| Q3 | `be behind price increases`が`be behind`に割れる/INVALID | 選定+canonicalization(Rule7)。候補供給自体はLLM抽出が`been behind price increases`で成立 | ABC §3: display`be behind` → canonicalizationLLMが`be behind price increases`を提案 → `been`≠`be`でsource_spanの連続部分でなくRule7 INVALID(adv_B_run1, adv_C_run1/3)。活用形の戻し(been→be)を**LLMに任せている**のが根本(OPEN-310の領域)。 |
| Q4 | `push prices up` | 抽出・選定とも成立 | v5 Std: Wiktionary phrasal `prices up`(C4)が供給され選定が`push prices up`へ正規化(`normalization_reason: inherit_selection_normalization`)。**良い例として維持**。 |
| Q5 | Stdで`take time`/`right away`/`on a regular basis`が5枠中3枠 | **候補供給の乏しさ+選定のlevel非感応** | v5 Stdはphrase_survivors 8件のみ(`based on`/`feels like`/`on a regular basis`/`prices up`/`right away`/`take for`/`take time`/`waiting for`)。非透明な比喩候補は供給0(`pumps`は単語としてshortlistに入るが選ばれず)。Prompt冒頭は共通「B1」でlevel差指示なし。 |
| Q6 | Topic: Std `raw bean` / Adv `lag` | 選定段(Topic割当) | v5 keywords_canonicalized.json: Std rank1 `raw bean`(topic, `candidate_mismatch_suspected:true`、source_span`raw-bean`)、Adv rank1 `lag`(topic)。Topic比較対象に`time lag`型の概念連語や記事の比喩が候補として存在しなかった。 |
| Q7 | Idiom・Collocation・単語・記事独自比喩の分類 | **既存機構は区別しない** | 候補の`unit_type`は word/phrase/phrasal_verb/idiom/important_word、evidenceは wiktionary[idiom]/[phrasal_verb]/repeated_compound_noun/cefr_j/ngsl_family/heuristic のみ。Wiktionaryの`idiom`は非透明性を意味せず`of a`/`At that`/`take time`/`on a regular basis`も`idiom`(`phase_a/DIAGNOSIS_AND_DESIGN_01.md` §0)。Collocation辞書は無く、ACL/Oxford Phrase List/PHRASEはライセンスUNRESOLVEDでProduction不可(`docs/pm/db_survey_key_phrase_sources_01.md` §2,6,8)。「記事独自比喩」を表す項目は選定出力にも検証にも無い。Trialの`llm_noncompositional`だけが辞書外の非透明複数語を表す。 |
| Q8 | 辞書照合・活用形・所有格 | 先頭語のみlemma化(`lemma_candidates_for_phrase` er023:123-173)、不規則救済も先頭語のみ。`one's/someone's`見出しは本文の`his/her/its`にヒットしない(Wiktionary idiom 10,632件中1,505件=14.2%がplaceholder見出し) | `phase_a/DIAGNOSIS...md` §0/§5、`sim_inject_db_entries_01.json`。=OPEN-325(a)。`pump one's fist`がDBに在っても`pumps its fist`には当たらない。 |
| Q9 | 候補上限(cap15/予約枠3)・KEY_PHRASE_MAX_WORDS=5 | phrase cap=15は**アルファベット順**で切る(v5 Advはphrase_survivors 16件で1件脱落)。n-gram生成max_n=5、key_phraseも1〜5語(er003:151)。予約枠3(cap15の外側)はTrial(OPEN-325(c))のみ | core:385, er027:643, `upstream_trace_01.json`(coffee_v5_adv phrase_survivors=16)。`mark the date on your calendar`(6語)は5語上限で原理的に生成されない。[委任_02追加] さらに、Wiktionaryヒットのうち名詞句判定で外れた`demoted_to_phrase`は`phrase_survivors`の**末尾**に追加される(`er030_key_phrase_db_hybrid_core_01.py` L454-455)ため、capの先頭15件(`er027_..._stage1.py` L643)で先に切られる(U1でヒットが増えるほど顕在化)。 |
| Q10 | Std/Advの候補供給差 | v5 Std=phrase 8/word 146、Adv=phrase 16/word 164。Advは句動詞(`come down`/`show up`/`comes with`/`go down`)が豊富、StdはWiktionary一致が乏しい。meta/hormuzもphrase 6〜8件 | `upstream_trace_01.json` |
| Q11 | 閉じた語類のみの断片 | `of a`/`at that`が候補に入る(Adv: `at that`,`of a`、meta Std: `of a`) | `closed_class_fragments_01.json` |

### 2-1. 「確実に判断できないこと」の実測(ハードルール化しない根拠)

- **既知可能性**: `right away`(A1/A1)、`come with`(A1/A1)、`take time`(B1/A1)、`show up`(A2/A2)、`push prices up`(B1/-/A2)は、トークン単位のCEFR-J・Zipfでは区別できない(`known_likelihood_signals_01.json`)。ユーザー基準では`right away`/`take time`=Std低優先、`show up`/`come down`=Important可、`push prices up`=高評価で、トークン難易度の大小と一致しない。→機械判定不可。LLMの相対評価と、Level別の「既知とみなす基準」の文章化までに留める。
- **連語の強さ**: wordfreqの複数語Zipfは`time lag`=3.67=`lag`単独と同値で、連語頻度の代用にならない(`upstream_trace_01.json`)。
- **隣接bigramの機械拡張**: 希少語の隣接内容語bigramは`beans also`/`just beans`/`cheaper ask`等ノイズが多い(`upstream_trace_01.json` `word_containing_bigrams`)。→「隣接だから拡張」はハードルールにせず、拡張を認めるのは**辞書に実在する複数語**に限る。
- **記事独自比喩か否か**: Wiktionary未登録=記事独自、とは言えない(`pump one's fist`は未登録でも定着した動作表現)。登録は「定着の十分条件」であって必要条件ではない→LLM判断(Pkg E)を併用。

---

## 3. 上流機械判定改善案(Pkg U、LLM追加なし、費用0)

OPEN-325の(a)placeholder照合・(c)予約枠・(b1)LLM補助抽出は**そのまま別論点として残し**、ここでは新規4項目だけを提案する(U1〜U4)。いずれもProduction既存ファイルは変更せず、採用する場合は別委任でTrial→承認の順。

| ID | 内容 | 機械判定の範囲 | 実証/期待 | 判断しない範囲 |
|---|---|---|---|---|
| **U1** Wiktionary照会プールの並べ替え(**§3-3の「予算拡大」案と比較して採否を決める**) | online lookup(予算60は不変)の先頭に「shortlist候補の希少語[word_survivorsの希少度上位K=10]を含む2語」を置き、残りは従来順 | 完全に機械的 | Coffee v5 Advで`time lag`の順位 76→**9**(`budget_sim_01.json`)。先頭に置かれる2語は記事あたり19〜31件(6記事中4記事で確認)。Wiktionary実在は照会で確認(`time lag`=True)。**副作用[委任_02追記]**: 優先グループには固有名詞(`Muse`/`Brent`/`Strait`等)を含む2語も入る(例: `asked Muse`,`Brent crude`)。固有名詞や機能語で終わる2語がWiktionaryに無いのは通常で害は無いが、枠を消費する | 優先された2語がWiktionaryに無ければ何も起きない(害なし)。従来先頭60件のうち押し出される項目の損失は未測定(§9のオフライン再判定で測る)。K=10の妥当性も未検証 |
| **U2** 包含関係の注釈と、登録済み複数語による単語の整理 | 各候補について「同一文内の連続token列として含む/含まれる」関係を機械算出(活用語尾・所有格・大小文字を吸収)。(Tier-H・ハード)含む側が**辞書登録(Wiktionary見出し/online hit/placeholder照合)**かつ含まれる側がword候補で本文内の出現がすべて含む側の内側なら、含まれる側をshortlistから除外。(Tier-S・注釈)それ以外は除外せず、候補行に `含む:Cn`/`含まれる:Cn` を付与 | Tier-H: 機械的 / Tier-S: 注釈のみ | `lag`⊂`time lag`はU1と組でTier-H(Wiktionary hit)。`be behind`⊂`been behind price increases`はLLM抽出由来(登録外)なのでTier-S(注釈のみ、最終判断はLLM)。既存6記事(Coffee/meta/hormuz×Std/Adv)でTier-Hが既存候補に発火する件数=0、誤爆0(`containment_pairs_rare8_01.json`)。**[委任_02追記] 実効対象はCoffee 1件(`lag`⊂`time lag`)のみで、Tier-Hが効く場面は現時点でほぼ無い。Tier-S注釈だけで足りる可能性があるため、Trialで「Tier-H+S」と「Tier-Sのみ」を比較項目にする** | 含む側の方が良いか(意味が完結するか)の判断。`show up`⊂`show up in US retail prices`のような機能語で終わる拡張は登録外なのでTier-S/不採用 |
| **U3** 断片の機械検出(**[委任_02訂正] 左拡張による置換はやめた**) | (i)全トークンが閉じた語類(`of a`,`at that`)の**辞書一致**候補を除外(`select_unmatched_...`は既に同条件を適用済みだがDB一致経路にだけ無い)。(ii)**辞書登録外**(LLM抽出/ヒューリスティック由来)で、先頭が前置詞・冠詞・助動詞などの閉じた語類の候補は、辞書照合(Wiktionary見出し/online hit/placeholder照合)で**未登録を確認したうえで検出**し、(案1)shortlistから除外、または(案2)`fragment_risk`注釈のみ付与(除外しない)。**本文から左へ拡張して別形に置換することはしない**(拡張形が良い塊とは限らず、機械で作った新規表現がRule7・canonicalizationの前提を壊す恐れがあるため)。辞書登録済みの成句(`on a regular basis`等)には適用しない。**粒度の改善は発生源である抽出Prompt(Pkg E)側の責務**とし、「修飾先の主要語を含む最小限の完結したまとまり、5語以内」という指示として扱う(§3-4) | (i)(ii)とも機械的(検出のみ) | (i)Coffee v5 Advで`at that`,`of a`、meta Stdで`of a`が該当(`closed_class_fragments_01.json`)。(ii)`in the ring`はPkg Eの抽出出力(Stage1の外)なので、U3(ii)を効かせるには抽出結果に対しても同じ検出を通す必要がある=Pkg E前提で、**Pkg U単独では`in the ring`型を回避できない**。**[委任_02追記] U3(i)は`as well`/`at all`/`in fact`のような「閉じた語類のみの成句」にも当たり得る(辞書登録済みの定着表現)。Step1で該当件数と目視を集計し、必要なら成句例外リストまたは辞書一致を優先する** | 比喩が成立するか・断片が意味を保つか(`in the ring`以外の型)の意味判断。(ii)の「閉じた語類」リスト精度は実装時に既存`_CLOSED_CLASS_FUNCTION_WORDS`で検証 |
| **U4** phrase cap(15)の扱い(**[委任_02訂正] 旧案「内容語の最小Zipf順タイブレーク」を撤回**) | 旧案は、高頻度語を含む句動詞(`show up`/`come down`)がZipfの大きい側として常に末尾でcapに切られ、「句動詞を下げない」(§4)原則と**逆に働く**ため撤回。代替: **(a)cap自体を15→20程度へ緩和**(shortlistは最大約20件で足りるため、phrase枠を広げて切り捨てを減らす)、**(b)語頻度に依存しないタイブレーク**(例: `db_match_count`降順を保ち、同値内は「機能語断片でない→本文での出現順」)。**推奨は(a)**(cap緩和は規則を増やさず、アルファベット後方が体系的に切れる問題を単純に和らげる。ただしshortlist総数・Prompt長の増は要確認)。(b)は語頻度に依存せず出現順で決めるためバイアスが小さいが、効果は(a)ほど大きくない。あわせて**`demoted_to_phrase`(Wiktionaryヒットだが名詞句判定で外れたもの)がphrase_survivors末尾に追加されcapで先に切られる問題**に対処する: ヒット由来の`demoted_to_phrase`を、`db_match_count`が同値の通常phrase_survivorsと同じ整列キーに戻す(`er030_..._core_01.py` L454-455、`er027_..._stage1.py` L643の対象)。U1でヒットが増えるほど顕在化するためU1とセットで扱う | 機械的 | Advでphrase_survivors 16件中アルファベット後方が切れる問題(`phase_a/DIAGNOSIS...md` §3)の緩和。OPEN-325(c)予約枠(cap外3枠)とは別層で併用可 | どの候補が良いかの価値判断 |

### 3-1. 上流で行わないこと(明示)
- 「既知/未知」「定着度」「連語の自然さ」の機械的なスコア化・足切り(§2-1の実測根拠)。
- `right away`/`take time`の機械的除外。供給は残し、判断はLLMに任せる(受入例6は§4のP・§6で扱う)。
- 活用形の戻し(`been`→`be`)の機械化は**OPEN-310(Rule7)の範囲**。本設計ではPkg Rとして依存関係だけ記す(§8-2)。

### 3-3. [委任_02追加] U1(並べ替え)と「照会予算の拡大」の比較
Wiktionary online照会は**1回50件・回ごとの待ち1.5秒**。Advの2語プール312件(Std 290件)なら**約7回・十数秒で全件を照会**でき、並べ替え自体が不要になる可能性がある(3語プールを含めても同程度)。K=10固定のU1は、予算内に収めるための妥協案にすぎない。
| 比較項目 | U1(先頭を並べ替え、予算60) | 予算拡大(2語全件、約7回) |
|---|---|---|
| 新規ヒット | `time lag`等、優先グループ内のみ | プール全体(`time lag`含む) |
| 失うヒット | 従来先頭60件のうち押し出されるもの(未測定) | 無し(従来の60件を包含) |
| 所要時間 | 変化なし(2回) | 約7回=十数秒(+記事あたり約10秒) |
| rate limit | 変化なし | 7倍のcall。公開APIのrate limitに触れるかは**未検証** |
| cache | 不要 | 記事を跨ぐ共通2語(例: `price tag`)が多く、**cacheで大幅に削減**できる見込み |
| 副作用 | 固有名詞を含む2語が優先枠を消費 | ヒット増に伴い`demoted_to_phrase`も増える(§3 U4で対処) |
**推奨**: K=10固定を先に採らず、Step1(§9)で「U1」「予算拡大」「両方」の3方式を過去記事に適用して、新規ヒット数・失うヒット数・所要時間・rate limitを実測してから採用案を決める。
**[委任_02追加] 追加の費用0調査項目**:
- 候補供給の取りこぼしの記事横断頻度: `surface_echo`が候補`span`より**広い**ケース(選定LLMが候補より長い形を意図した)を、過去runで走査して測る。現行の`candidate_mismatch_suspected`(`er030_..._contract_01.py` L483-484)は`norm_echo not in norm_surface and norm_surface not in norm_echo`の条件のため、**包含関係を不一致と見なさない**(`surface_echo="time lag"` vs 候補`lag`は`lag`⊂`time lag`で不一致にならない)。包含ケースの検出を加えれば、Coffee専用でない「取りこぼし」の頻度が分かる。
- Wiktionary照会文字列の正規化: 文頭大文字(`Time lag`→小文字)、複数形(`beans`→`bean`)、活用形の扱いをStep1で確認する。
- 照会結果snapshotの保存: 照会結果(句→True/False、取得日時)をファイルに保存し、再現性とcacheを確保する。
- Step1の約400記事照会のcache・間隔計画: 2語を記事を跨いで共通cache化し、50件/回・1.5秒待ちで直列に実行する(概算の上限=400記事×7回≒2,800 call≒70分、cache効果で大幅減の見込み、実測する)。

### 3-4. [委任_02追加] 抽出Prompt(Pkg E)側の粒度指示
`in the ring`型の断片は発生源が抽出LLMなので、粒度の指示は抽出Prompt側に置く(Pkg Uの機械処理では置換しない)。案: 「**修飾先の主要語を含む最小限の完結したまとまり、5語以内**で抜き出す(例: 前置詞句だけでなく、前置詞句が修飾する名詞を含める)」。この指示の効果は、Std/Advとも抽出LLMの出力で測る(OPEN-325(b1)の判断が前提)。

### 3-2. 辞書・コーパス資源の評価(導入は提案のみ)
| 資源 | 状態 | 費用 | ライセンス/保守 | 評価 |
|---|---|---|---|---|
| Wiktionary online multiword照会(既存) | 稼働中 | 0 | CC BY-SA(既存利用)。API依存・オンライン | **U1で活用**。予算内の優先順位で拾える範囲が広がる |
| Wiktionary見出し(ローカル、idiom/phrasal/proverb) | 稼働中 | 0 | 同上 | `time lag`,`be behind`,`in the ring`は未収録(確認済み)。動詞+目的語型のコロケーションは網羅しない |
| WordNet(複数語見出し) | **未導入・未検証**(`nltk`未導入) | 0 | Princeton WordNet licenseは商用可と理解しているが**ライセンス原文は今回未確認** | `time lag`等の名詞連語を**オフラインで無予算照合**できる可能性。導入提案として§10-Dに記載(要ライセンス確認) |
| wordfreq(導入済) | 稼働中 | 0 | MIT/データCC BY-SA系 | 単語Zipfのみ有効。複数語Zipfは連語強度として不可(§2-1) |
| CMU辞書(導入済) | 稼働中 | 0 | 公開 | 発音用(聞き取り支援の参考情報)。選定判断には使わない |
| ACL(Academic Collocation List)/Oxford Phrase List/PHRASE List/Cambridge | 外部 | 要契約 | **UNRESOLVED**(Trial/評価参照のみ、`db_survey_key_phrase_sources_01.md`) | 内容は最適だがProduction不可。「コロケーション頻度の根拠」としては使えない |
| 大規模n-gram(Google Books Ngram等) | 外部 | 0〜(DL容量大) | CC BY系だが取得・保守負荷大 | コロケーション強度の本命だが今回は提案のみ(導入コスト大、判断はユーザー) |

---

## 4. LLM選定指標・Prompt改善案(Pkg P)

### 4-1. 方針
- **現行6指標の順序は維持**(A/B/C Trial: 優先順位入替は改善せず、Bはgate通過6/6→2/6、Cは1/6、`ABC_REPORT_01.md` §2)。
- 新しい**番号付き指標は増やさない**(指標増はcanonicalization側のINVALID誘発・出力揺れのリスク、§4-4)。足すのは次の4つだけで、全て**Family X限定guidance**(`_FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE`)への追記。共有テンプレート(`b1_p2_keywords_l_prompt_template.txt`)はFamily Z等と共有のため触れない。
  1. **同程度のときのタイブレーク1文**(表現全体の定着度・自然さ・コロケーション学習価値)
  2. **まとまり**(注釈`含む/含まれる`を使い、意味が完結する側を選ぶ)
  3. **役割別基準**(Important/Topic)
  4. **既知とみなす基準**(Std向けの1文。句動詞・非字義用法は下げない)
- 上流で確定できる事項は上流(Pkg U)、文脈・意味・学習価値の相対評価はLLM。

### 4-2. Prompt差分(現行→案)
**現行**(DB Hybrid追加guidance、`er030_..._contract_01.py:177-196` 該当部):
```
- 残りは、[phrase / idiom / phrasal verb候補]区分を優先してください。
  良い候補が不足する場合のみ[word候補]区分で補ってください。
- CEFR難易度・語彙レベルを主要な判断軸にしないでください。
```
**案**(追記のみ。Coffee語句はPromptに書かない=一般表現)[委任_02訂正: 2文目を書換え。旧文は「取り出した後も本文での意味と用法が保たれる、意味の完結した側を選び」「記事固有の文脈語を足しただけなら短い側」で、`be behind price increases`型が`be behind`へ倒れる恐れがあるため。受入確認は§7]:
```
- 残りは、[phrase / idiom / phrasal verb候補]区分を優先してください。
  良い候補が不足する場合のみ[word候補]区分で補ってください。
- CEFR難易度・語彙レベルを主要な判断軸にしないでください。
+ - 優先順位(上記の6項目)が同程度の候補どうしでは、定着した自然な表現(慣用句、自然なコロケーション、
+   本文で非字義的に使われる表現、聞き取りにくいが他の文脈でも使える表現)を、構成語どおりの連語や
+   この記事だけの言い回しより優先してください。
+ - 候補の行に「含む:Cn」「含まれる:Cn」がある場合、短い方は長い方の一部です。同じ内容を両方選ばないでください。
+   動詞の目的語・補語など、用法を成り立たせる要素を含む側を選んでください。長い側が主語・時・場所の
+   付け足しだけなら短い側を選んでください。
+ - Importantには、他の記事でも使える定着した表現を選んでください。行に「タグ:記事固有」とある
+   この記事だけの創作的な言い回しはImportantに選ばないでください。Topicには、本文の内容・展開・
+   重要概念の理解に必要な表現を選びます(記事固有の言い回しでも、本文理解への貢献が大きく他の候補より
+   優れる場合に限りTopicに選べます)。Topicを「比喩だから」という理由だけで決めないでください。
+ - 学習者がすでに知っている可能性が高い基本の連語(構成語どおりの意味で使われるもの)は、同程度の他の
+   候補があれば優先度を下げてください。句動詞や、本文で基本義と異なる意味で使われる表現は下げないでください。
```
- **候補行の注釈(Python付与、Pkg U/E)**: `... | evidence: ... | 含む:C31 | タグ:記事固有`。`タグ`は`登録済み`(辞書一致)/`記事固有`(抽出LLMが`article_specific`と自己申告)のみ。付与対象外の**候補行**は現行と完全同一。[委任_02訂正: 旧文「注釈が付かない記事では現行Promptと同一バイト列」は誤り。guidance追記でPromptは常に変わる。同一なのは注釈の付かない候補行のみ。後方互換テストは「候補行の同一性」で書く]
- Level別文(Std向け「既知とみなす」)は、Std/Advで共通Promptを使っているため**Level差の入れ方が論点**(§6, §10-C)。さらにStd選定Prompt冒頭が「B1英語記事本文」のままである点(Family Zと共有テンプレート)は§10-Jで扱う。

### 4-3. トークン増・費用の見積
| 項目 | 増分 | 根拠 |
|---|---|---|
| guidance追記 | 約400〜450token(日本語約600字) | 現行選定入力3.6k〜4.6k token(`PHASE_A DIAGNOSIS §10`のINV-01実測) |
| 候補行注釈 | 1行あたり約8〜15token × 注釈付き行(多くて5〜10行)=約50〜150token | Trial行長(約40token/行)からの推定 |
| 選定1回の費用 | +約JPY0.01〜0.03 | 現行選定1回JPY0.35〜0.48、入力増≒+10%でも出力(≒3.6k〜4.8k)が費用の大半のため。**推定であり未測定** |
| 1 job(選定+canonicalization+Redundancy QA)≒JPY0.9 | +2〜4%(推定) | ABC実績 6.45/9job≒0.72〜0.9 |
| Pkg E(LLM補助抽出)を併用する場合 | +JPY0.25/回/level(=記事あたり約0.5) | Phase D M1実測 6回JPY1.5018 |

### 4-4. 指標増の複雑化リスク評価
| リスク | 評価 | 対策 |
|---|---|---|
| 出力揺れ・gate通過率低下(ABC: B/Cでcanonicalization INVALID増) | 中。順序入替より小さい見込みだが追記量自体は増える | 追記は「タイブレーク」「注釈利用」「役割」「既知」の4点に固定。番号付き指標は増やさない。有料Trialで現行Aとgate通過率を比較(許容: A 6/6からの低下なし) |
| 「タグ:記事固有」への過剰依存(抽出LLMの自己申告の誤り) | 中 | タグは選定を**強制せず**guidanceで抑制(ハード除外にしない)。ハード強制はユーザー判断(§10-B) |
| 既知基準が句動詞を押し出す誤作動 | 中 | 句動詞・非字義用法は下げない一文を併記。Std/Adv両方でshow up/come down/push prices upが残ることを受入に含める |
| [委任_02追加] Topic/Importantの取り違え | 中 | guidanceに加え「記録だけの軽い検査」(§5 T6)を推奨。retryなし・費用増0 |
| Prompt内への記事語句の混入 | 低 | Coffee語句hardcode不在testを維持(Phase Dの既存方針) |

### 4-5. 評価観点の割り付け(上流 vs LLM)
| 評価観点 | 上流(機械) | LLM |
|---|---|---|
| 表現全体の定着度・自然さ | 辞書登録の有無を注釈(`登録済み`) | 相対評価(タイブレーク文) |
| コロケーション学習価値 | 登録済み複数語の拡張(U1/U2) | 動詞+目的語型(`be behind X`)の用法学習価値 |
| 単語vs句の適切さ | 包含注釈(U2)、登録済み複数語の内側の単語はTier-Hで除外 | 注釈を見て完結側を選ぶ |
| 切出し後も理由と意味が一致 | 断片検出(U3)、Rule7ヘッドワード(Pkg R) | selection_reasonとdisplay_phraseの整合 |
| Topic/Important役割差 | `タグ`注釈 | 役割別基準(§5) |
| 一般的慣用表現との誤認 | 登録済み/登録外の区別を注釈 | 本文での非字義性 |
| Std/Advレベル価値 | 供給差(Adv句動詞が豊富)を前提にする | 既知とみなす基準(Std)、Advは基本義と異なる意味の句動詞を同列評価 |
| 既知の基本表現より高度な自然表現を選ぶ | **機械不可**(§2-1実測) | 相対評価 |

---

## 5. Topic / Important 選定ルール

現行: 選定LLMが選定と同時に`key_phrase_role`を付ける。Topic定義(ユーザー2026-09-28確定): 「汎用性・一般的な学習重要度は必ずしも高くなくても、その記事に特有であり、事前に意味・用法・音を理解しておくことで本文全体を追いやすくなる語または表現」。

### 5-1. 提案ルール
| ルール | 内容 | 判定主体 |
|---|---|---|
| T1 Topic適格 | 本文の内容・展開・重要概念の理解に必要な表現。判断テスト=「これを知らないと主要な主張/展開を取り違えるか」。記事固有の比喩も、貢献が十分で他候補と比べて優れれば可(「比喩だから必ずTopic」にしない) | LLM。補助として機械算出の**中心性ヒント**(見出し語との重なり・出現文数)を注釈に付けられる(任意、§10で採否) |
| T2 Important適格 | 他記事でも使える定着表現(自然なコロケーション、定着慣用句、非字義用法、聞き取りにくいが再利用可能な表現)。**記事独自の創作的比喩は原則選ばない** | 辞書登録(機械)+抽出LLMの`reusability`自己申告(LLM)+選定LLM |
| T3 役割の排他 | 記事固有の言い回しはTopic専用。TopicにしたものをImportantと重複させない(Redundancy QAと整合) | LLM+既存QA |
| T4 Topic不在時 | 現行どおり「最も近い候補を選ぶ」(topic空にしない)を維持 | 既存 |
| T6 [委任_02追加・推奨] 記録だけの軽い検査 | 条件: **辞書未登録 かつ `article_specific` かつ `important`** の候補があれば、flagを記録(retryなし、validator差し戻しなし、LLM追加なし=費用増0)。違反率をTrialと運用で測り、T5への格上げ判断材料にする。根拠: ABC(v4)で現行LLMが`two numbers in the ring`/`in the ring`/`its own hidden clock`に`phrase_type: idiom`・important を付けた実証がある=guidanceだけでは守られない可能性が実測されている | Python(記録のみ) |
| T5 ハード強制(**任意・未推奨**) | `タグ:記事固有`の候補がImportantで返ったら構造validatorで差し戻し | Python。retry増=費用増、既存のretry上限(最大2回)を超えない設計が必要。ユーザー判断(§10-B) |

### 5-2. 分類の機械的な定義(混同を防ぐ)
- `登録済み`: Wiktionary見出し/online hit/placeholder照合のいずれかに一致(機械)。
- `登録外・定着`: 辞書に無いが他文脈で再利用できる(例: 動作を表す表現)。抽出LLMが`reusability: established`と自己申告(LLM)。
- `登録外・記事固有`: 辞書に無く、この記事の文脈だけで成立する創作的比喩(抽出LLMの`reusability: article_specific`)。
- `登録外・判定不能`: LLMが確信を持てない場合は`established`扱いにせず**タグなし**(注釈を付けない=現行と同じ扱い)。確実に判断できないものをハードルール化しない。

---

## 6. Std/Adv差を踏まえた評価

| 論点 | 現行 | 提案 | 備考 |
|---|---|---|---|
| 候補供給差 | Std v5: phrase 8/word 146、Adv: phrase 16/word 164。Stdは非透明比喩の供給0 | 供給差は**そのまま**(Levelで供給方式を変えない)。U1/U2/U3は両Levelに同一適用 | `upstream_trace_01.json` |
| Prompt | Std/Advとも共通テンプレ(冒頭「B1」) | (a)現状維持(Level差なし)/(b)Family X guidanceにLevel別の「既知とみなす基準」1文を差す(Std: A2相当で日常頻出の基本連語は優先度を下げる、Adv: 基本義と異なる句動詞を同列評価) | Phase Dで検証済みの文面(`prompts/trial_guidance_std_v2.txt`/`adv_v2.txt`)を再利用可。Trial全体はREJECTED as-isのため**(b)の効果単独は未検証** |
| 既知判定 | トークン難易度では機械判定不可(§2-1) | LLM相対評価。`right away`/`take time`は「他に同程度の候補があれば下げる」であり**除外しない**(候補が乏しい記事では残ってよい) | ユーザー基準「Standardでも低優先、相対評価」と整合 |
| 高度な自然表現 | 供給があれば選ばれる(ABC: Aで`pump one's fist`が5/6採択) | 変更なし | `ABC_REPORT_01.md` §2 |
| 句動詞 | Advで`show up`/`come down`選定 | 保持(下げない文を併記) | |

---

## 7. Coffee各例の期待選定結果と比較

注: (c)は**机上の期待**(有料run未実施、未検証)。○=機械的に保証または実測済 / △=LLM判断依存の期待(未検証) / ×=満たさない。比較表の機械可読版: `er064_output/kp_candidate_selection_design_01/comparison_table_01.json`。

### 7-1. 各例の期待
| 表現 | 基準 | (a)現行Production v5 | (b)Idiom供給Trial(Phase D V2/ABC-A, v4原稿) | (c)改善案(机上) |
|---|---|---|---|---|
| time lag | 優先採用検討 | Adv: 候補に無し→`lag`をTopic | ABC-A Adv: 候補に無く`lag`が9/9run採択(v4でも76位で照会外) | U1(または予算拡大)+U2でAdv候補に`time lag`が入り`lag`はshortlistから除外 → Topic/Important候補として`time lag`が残る。**△[委任_02訂正: パイプライン到達は未検証]**: 並べ替えの机上順位(76→9)は確認済みだが、照会ヒット→除外Gate`gate_and_merge_multiword_hits`→名詞句判定`refine_multiword_hits_noun_phrase_flag`→重複除去→capを経てshortlistに入るかは未再生。名詞句判定で外れれば`demoted_to_phrase`となりphrase_survivors末尾に付いてcapで切られ得る(§3 U4)。Step1で全体再生が必須 |
| lag | `time lag`があれば劣後 | Adv rank1(Topic) | 同上 | Tier-Hで除外(`time lag`がshortlistに入ることが前提。△[委任_02訂正]) |
| push prices up | Important高評価 | Std rank2 | Std-A 2/3 | 維持(○)。供給経路が変わらないため |
| be behind price increases | Important可 | 候補に無し | Adv-A 3/3採択(ただしB/Cで`be behind`切出し→Rule7 INVALID) | LLM抽出由来→Pkg E(b1)が前提。Rule7ヘッドワード(Pkg R=OPEN-310)が無いとINVALIDの恐れ(△)。**[委任_02追加] 受入確認(必須)**: 改訂Pkg Pの文(「動詞の目的語・補語を含む側を選ぶ」)により、`been behind price increases`(目的語`price increases`を含む)が`be behind`へ倒れないことをTrialで確認する |
| be behind(単独) | 低評価 | 候補に無し | Adv-B 1/3, C 2/3で選定(INVALID誘発) | Tier-S注釈で「含まれる:`been behind price increases`」を付与、完結側を選ぶ(△) |
| two numbers in the ring | Topic条件付き可・Important不可 | 候補に無し | Std-A 3/3採択(Adv側の同型`in the ring`はimportantで採択された実績あり) | 抽出で供給(Pkg E)。`タグ:記事固有`→Importantに選ばない、Topic比較対象(△)。[委任_02訂正] Advの原稿は`putting the two figures in the ring`で、`two figures in the ring`は**5語で上限内**(6語は`putting the two figures in the ring`)。Advの断片化(`in the ring`)は5語上限の副次効果と抽出Promptの粒度指示の欠如による |
| in the ring | 今回は避ける | 候補に無し(trivial○) | Adv-A 2/3採択(×) | **△[委任_02訂正]**: U3(ii)の左拡張置換は撤回。回避は(1)Pkg Eの抽出Promptで「修飾先の主要語を含む最小限の完結したまとまり、5語以内」(§3-4)、(2)辞書未登録かつ閉じた語類始まりの`fragment_risk`注釈/除外、(3)Pkg Pの`タグ:記事固有`+Important抑制の合成に依存し、Pkg U単独では実現しない |
| its own hidden clock | Topic条件付き可・Important不可 | 候補に無し | Std-A 2/3(+`one's own hidden clock` 1/3) | `タグ:記事固有`、Importantに選ばない(△) |
| raw bean | Topic候補として適切 | Std rank1 Topic | Std-A 3/3 | 維持(△: Topic比較で`two numbers in the ring`等と相対評価) |
| price measure | 低優先 | 候補にあるが未選定 | Adv-A 1/3、C 2/3 | 現行どおり低優先(△。透明名詞連語の優先度を下げる文で抑制) |
| right away / take time | Stdでも低優先、相対評価 | Std 5枠中2枠 | Std-A 0/3(V2供給で押し出し) | 候補が乏しいと残る(△)。既知基準文で相対的に下げる |
| show up / come down | Important可 | Adv rank3/4 | Adv-A 1/3,1/3 | 維持(○。句動詞は下げない文を併記) |
| come with | 文脈次第 | Adv rank5 | Adv-A 0/3 | 現行維持(△。中立) |
| roasting | 単語単体でも可 | 候補にある(C22) | Std-A 1/3 | 維持(△) |
| pumps its fist | (基準例に無し) | 候補に無し(`pumps`は単語候補) | A 5/6採択 | Pkg E前提。**定着した動作表現の擬人化用法**と私は分類したが、ユーザー基準に明示が無い→§10-Eでユーザー確認 |

### 7-2. 受入7例の充足(○△×)
| # | 受入例 | (a)現行 | (b)Trial V2/ABC-A | (c)改善案(机上) |
|---|---|---|---|---|
| 1 | `time lag` > `lag` | × | ×(候補に無い) | **△[委任_02訂正: 旧○]**(U1または予算拡大+U2。机上順位は確認済みだが、除外Gate→名詞句判定→重複除去→capを通ってshortlist入りするかのパイプライン到達は未検証。Wiktionary online lookup依存) |
| 2 | 記事独自比喩をImportantに選ばない | ○(候補に無いだけ=偶然) | ×(`two numbers in the ring`等がimportantで採択) | △(Pkg P+E、LLM判断依存。ハード強制はT5=未推奨) |
| 3 | Topic候補として評価可 | △(raw bean/lag) | △(比喩はimportant扱い) | △(T1+中心性ヒント。LLM) |
| 4 | `in the ring`型回避 | ○(偶然) | ×(Adv 2/3) | △[委任_02訂正: 旧○]。U3(ii)の左拡張置換は撤回。Pkg E抽出Promptの粒度指示+`fragment_risk`注釈+`タグ:記事固有`によるImportant抑制の合成で、いずれもLLM判断依存 |
| 5 | `push prices up`/`be behind price increases`評価 | △(前者のみ) | ○(A: 後者3/3、前者Std 2/3)。ただしB/CでRule7 INVALID | △(Pkg R依存。前者は○) |
| 6 | `take time`/`right away`が有益候補を押し出さない | ×(Std 2枠) | ○(Std-A 0/3、ただし供給追加による副次効果) | △(供給が無い記事では残る。LLM相対評価) |
| 7 | Std・Adv両方で改善 | — | Std ○/Adv △(`lag`残存・`in the ring`採択) | △(Adv: U1/U2/U3の機械処理+Pkg Pで部分改善の見込み。**Std: Pkg E[b1]が必須で、OPEN-325(b1)=「本文全文をLLMへ送らない」原則(`CURRENT_SPEC.md:1847`)の改訂判断に依存**) |

### 7-3. 別記事での正常例・反例(Coffee専用にならないことの確認、既存Family X記事2本)
対象: `meta/run_03`(Std/Adv)、`hormuz/run_02`(Std/Adv)の stage1 を読取専用で再現(`upstream_trace_01.json`, `containment_pairs_01.json`, `closed_class_fragments_01.json`)。

| 記事 | 正常例(提案が現行を壊さない) | 反例/注意(ルールが誤爆し得る箇所) |
|---|---|---|
| meta Std/Adv | 現行の最終選定は`Behind the Scenes`(Topic、辞書登録の成句)/`contract workers`/`concierge`/`bargain`/`by mistake`。U2のTier-Hは**発火0**(`containment_pairs_rare8_01.json`)。`behind`⊂`behind the scenes`は単語が希少語K=10に入らず対象外。U1は`haircuts check`,`inappropriate comments`,`book haircuts`等を先頭に置く(Wiktionaryに無ければ無害)。 | `of a`(Std)は全閉語類として除外(U3(i))。`calls`⊂`phone calls`(heuristic複合名詞)のような関係は登録外なのでTier-S(注釈のみ、除外しない)。 |
| hormuz Std/Adv | `Brent crude`/`crude futures`/`curtain rose`/`strait safe`等が先頭グループ(`budget_sim_01.json`)。過去の最終選定は`give back gains`/`sea blockade`/`Brent crude futures`/`take a sharp turn`/`settle at`(hormuz__run_02)で、登録済み複数語の内側の単語が選ばれていた形跡は無い(Tier-H発火0)。`crude`⊂`Brent crude futures`はTier-S(heuristic由来)。 | `settle at`/`take for`のような機能語で終わる句動詞断片は**登録済み**のためU3(ii)の対象外(成句として扱う)。この種の低価値断片の抑制はPkg P(タイブレーク文)に委ねる(機械ではしない)。 |

→ Tier-Hの発火は「辞書登録された複数語がword候補を完全に含む」場合だけ(U2の実効対象はCoffee Adv `time lag`の1件)で、6記事のうち既存候補ではCoffee Advの`time lag`(U1適用後)のみ。Coffee専用の文字列は一切使わない(`time lag`は評価fixture)。

---

## 8. 解説ページ接続案(データ構造・連携方針のみ。実装・正式採用なし)

### 8-1. 目的
将来の「文法・用語解説ページ」で、KPに選ばれなかった表現(記事独自比喩、`time lag`型の概念連語、`be behind X`型の用法)も解説候補として使えるよう、**表現単位のレコード**を保持する。

### 8-2. レコード案(JSON schema案、`kp_expression_record_v0_draft`)
```json
{
  "schema_version": "kp_expression_record_v0_draft",
  "article_id": "FAMILY_X_AUDIO_coffee_prices__run_v5_ms_01",
  "level": "std|adv",
  "source": {"sentence_id": "S7", "sentence_text": "...", "span": "time lag", "text_hash": "sha256:...(本文hash。offsetのずれ検出用)", "occurrences": [{"sentence_id": "S7", "char_start": 0, "char_end": 0}, {"sentence_id": "S12", "char_start": 0, "char_end": 0}]},
  "expression": {
    "surface": "time lag", "headword": "time lag", "unit_type": "word|phrase|phrasal_verb|idiom|noun_phrase|collocation",
    "evidence": ["wiktionary_multiword", "repeated_compound_noun", "llm_noncompositional"],
    "registered": true
  },
  "classification": {
    "nature": "established_idiom|collocation|phrasal_verb|domain_term|article_specific_figure|plain_word|unknown",
    "reusability": "general|article_specific|unknown",
    "transparency": "opaque|semi|transparent|unknown",
    "figurative_in_article": false
  },
  "meaning_in_article": {"ja_gloss": "時間差", "role_in_text": "値下がりが店頭価格に反映されるまでの遅れという記事の中心概念", "source": "selection_reason|llm_generated|null"},
  "kp_selection": {
    "selected": true, "role": "topic|important|null", "rank": 1,
    "selection_run_ref": "keywords_runtime_metadata.json#attempt1",
    "not_selected_reason_code": "none|dominated_by_more_complete|fragment_risk|cap_cut|lower_priority|article_specific_not_topic|basic_known|filtered_closed_class|not_supplied|lookup_budget_cut",
    "not_selected_reason_ja": null
  },
  "containment": {"contains": ["C31"], "contained_in": []},
  "explanation_page_candidate": {"recommended": true, "reason_code": "article_specific_figure|reusable_collocation_with_nuance|grammar_pattern|domain_term", "priority": "high|mid|low"},
  "provenance": {"stage1_candidate_id": "C40", "pipeline_version": "db_hybrid+kp_design_v0", "generated_at": "2026-10-13T00:00:00+09:00", "llm_calls": []}
}
```

### 8-2b. [委任_02追加] スキーマ補足
- `occurrences[]`: 同じ表現が複数箇所に出る場合に全出現を持つ(旧案は単一span)。
- `text_hash`: 本文のhash。本文が変わった(再生成された)ときoffset(`char_start/char_end`)のずれを検出するため。
- 非選定理由コード追加: `not_supplied`(そもそも候補に供給されなかった)/`lookup_budget_cut`(Wiktionary照会の予算で切られた=`time lag`型)。取りこぼしの種類を区別する。

### 8-3. 既存出力のどこに付加するか
| 情報 | 既存の保存先(新規ファイルを増やさない範囲) | 付加方法 |
|---|---|---|
| 選定済み | `key_phrases/keywords_canonicalized.json` items(`key_phrase_role`,`surface_echo`,`source_candidate_id`) | 変更せず読むだけ。sidecarで参照 |
| 未選択候補 | `key_phrases_db_hybrid/kp_auxiliary_candidates.json`(「未検証の参考候補」、v5でStd 21/Adv 27件) | [委任_02訂正] **既存の`kp_auxiliary_candidates.json`へは追記しない**(Production出力契約を変えないため)。理由コード・`containment`は**別ファイル(sidecar)**にのみ書く。U2/U3/U4の結果から導出可、LLM追加不要 |
| 除外理由 | `db_hybrid_stage1_debug.json`の`exclusion_gate_result`/`context_mismatch_excluded` | `filtered_closed_class`等のコードへ写す |
| 選定理由 | `keywords_runtime_metadata.json`のattempts_detail(`selection_reason`,`listening_difficulty_reason`) | `meaning_in_article.source="selection_reason"` |
| 記事独自比喩か/再利用性 | 抽出LLM(Pkg E)の`reusability`/`kind`/`transparency` | Pkg E採用時のみ。採用しない場合は`unknown` |
| 本文での意味・役割(非選定分) | 既存には無い | **解説ページ生成時のオンデマンドLLM**(本設計では実施しない。KP選定callには追加しない) |

→ 出力は同一`key_phrases/`配下の1ファイル(`key_phrase_expression_records.json`)として、Production KPパイプラインの**後段(read-only)**で生成する想定。Production KP選定の出力契約・検証には一切影響させない(解説ページが無い間は生成しなくてもKPは完結)。

---

## 9. リスク・費用・検証計画

### 9-1. リスク一覧
| # | リスク | 重大度 | 対策 |
|---|---|---|---|
| R1 | U1で従来先頭60件のうち押し出される辞書ヒットが減る | 中 | オフライン再判定で、従来先頭60件のヒットが新並びで失われる件数を測る(§9-3 Step1)。欠損があれば並びの拡張(優先枠の追加)で補う |
| R2 | U2 Tier-Hの誤除外(登録済み複数語が単語の価値を持つ場合) | 低 | 6記事でゼロ発火。Tier-S中心。誤除外が出たらTier-Hを無効化できる設計(flag) |
| R3 | U3の検出で閉じた語類リスト不備、またはU3(i)が`as well`/`at all`等の閉じた語類のみの定着成句を誤除外 | 中 | 実装時に既存`_CLOSED_CLASS_FUNCTION_WORDS`を単体testで網羅確認。Step1で成句への影響件数を集計(§9)。[委任_02訂正: 左拡張置換は撤回済み] |
| R4 | Prompt追記による出力揺れ・gate通過率低下 | 中 | §4-4。Aとの対照でgate通過率の非低下を受入基準にする |
| R5 | Pkg Eの偽陽性(陰性対照R3で`gets the first word`)、および「本文全文をLLMへ送らない」原則(`CURRENT_SPEC.md:1847`)との衝突 | 高 | OPEN-325の判断事項。本設計はEに**依存する項目を明示**し、U/P単独効果も測れる構成にする(b5=V1+d単独効果分離と合流) |
| R6 | Rule7の`been→be`問題が未解決だと`be behind price increases`型がINVALID | 高 | Pkg R(OPEN-310)を先行または同時決定 |
| R8 [委任_02追加] | Pkg Pの2文目が「完結した側」を選ばせて`be behind price increases`型を`be behind`へ倒す | 高 | 書換え済み(§4-2)。Trialで`been behind price increases`が`be behind`に倒れないことを受入確認(§7) |
| R7 | Wiktionary onlineの可用性・レート | 低〜中 | 失敗時は現行と同じ挙動に縮退(照会結果なし=追加候補なし)。WordNet等のオフライン化案(§3-2) |

### 9-2. 依存関係図(OPEN)
```
OPEN-325 (候補供給改善: (a)placeholder / (b1)LLM補助抽出 / (c)予約枠 / (d)guidance)  [USER_DECISION_REQUIRED, Opus③待ち]
   │  Pkg Eの採否は OPEN-325 (b1) の判断(原則文言改訂含む)に従属
   ▼
本設計 (新規OPEN-336)
   ├─ Pkg U1-U4 (上流機械処理) ── 単独で実施可能(OPEN-325の(a)(c)と併用可、独立)
   ├─ Pkg P (guidance追記) ───── U2/U3の注釈と、Eの`タグ`があるほど効果大。単独でも一部有効(タイブレーク・役割文)
   ├─ Pkg E (補助抽出v4) ──────── = OPEN-325 (b1) に統合して判断
   ├─ Pkg R (Rule7ヘッドワード) ─ = OPEN-310 (分離。`been behind price increases`型の根治に必要。本設計では設計のみ)
   └─ Pkg X (解説レコード) ───── 独立(Production非接続)
OPEN-310 (Rule7: 人称代名詞表・語追加) ←→ OPEN-325 (b3) の依存(既存)
```
**Dangling Reference Check(本設計書内)**: OPEN-310 / OPEN-325 / OPEN-336(本件) / `CURRENT_SPEC.md:1847` / `er064_output/kp_idiom_trial_01/phase_d/PHASE_D_REPORT_02.md` / `er064_output/kp_idiom_priority_abc_01/ABC_REPORT_01.md` はいずれも実在確認済み。OPEN-336は本委任でOPEN_ITEMS.mdへ起票(重複確認: OPEN-325=Idiom供給採否、OPEN-310=Rule7、いずれも本件のU/P/X部分を含まない)。

### 9-3. 検証計画(段階、いずれも着手はFable/ユーザー承認後)
| Step | 内容 | 費用 | 判定 |
|---|---|---|---|
| 0 | Opus独立技術レビュー(**条件A: 新しい構造・処理フロー**。U1〜U4・注釈・タグ・Pkg X)。Fableが別途起動 | Opus枠 | 指摘反映 |
| 1 | **オフライン再判定**(保存済み記事[Phase Aで走査した約400本]、Wiktionary APIは無料公開・既存関数・小バッチ・低頻度・cache・snapshot保存、§3-3): (i)V0候補集合が意図外に減っていないか、(ii)Wiktionary online hitの増減(**U1 / 予算拡大 / 両方の3方式を比較**: 新規ヒット・失うヒット・所要時間・rate limit・cache効果)、(iii)Tier-H/断片検出の発火件数と目視誤爆(U3(i)の`as well`/`at all`等への影響を含む)、(iv)U4(cap緩和)と`demoted_to_phrase`整列の効果、(v)`surface_echo`が候補`span`より広いケースの過去run走査(取りこぼしの記事横断頻度)、(vi)照会文字列の正規化(文頭大文字・複数形)。**【必須・委任_02追加】照会結果を注入して`run_stage1_and_shortlist`全体(除外Gate`gate_and_merge_multiword_hits`→名詞句判定`refine_multiword_hits_noun_phrase_flag`→重複除去→cap)を再生し、`time lag`がshortlistに入り`lag`が除外されるまでを確認する**(受入例1は、この確認までは△) | JPY0 | V0⊆新候補(意図した除外を除く)、誤爆0、`time lag`がshortlistに入り`lag`が除外される |
| 2 | **単体test**(U1〜U4、注釈付与、後方互換[注釈なしでPrompt同一])を追加 | JPY0 | 全PASS |
| 3 | **少数記事の有料Trial(最小)**[委任_02訂正: 対照設計を修正]: 対照は**同じv5入力・同じU適用後shortlist**で「現行guidance」vs「Pkg P」を比較する。**既存ABC run(v4原稿・V2 shortlist)の再利用は不可**(入力が異なる)。各条件**n≥3**。3記事(Coffee/meta/hormuz)×2Level×2条件×n=3=**36 job ≈ JPY32.4**(1 job≈JPY0.9=選定+canonicalization+Redundancy QA)。Pkg Eを併用する場合は抽出をLevel別に入力として固定し(同一抽出結果を両条件で使う)、抽出6回≒JPY1.5〜18回≒JPY4.5を加算。**実行前に**meta/hormuzの期待ラベル(良い例・避ける例)を登録する(登録案: `step3_expected_labels_preregistration_01.json`、Coffeeはユーザー基準)。登録前の実行は不可 | 約JPY32〜37 | gate通過率が現行guidanceから低下しない。受入7例の○増。`been behind price increases`が`be behind`へ倒れない(§7)。陰性対照で偽陽性0。費用が上限50を超えない |
| 4 | **拡大Trial**: 6記事×2Level×Pkg Pのみ×n=3=36 job≈JPY32.4+抽出36≈JPY9=**約JPY41**(現行guidanceの対照はStep3の結果を再利用できる記事に限る。**両条件の72 job≈JPY64.8は上限50を超えるため行わない**) | 約JPY41 | Step3で有意な改善とgate維持が確認できた場合のみ |
| 5 | Opus条件C(重要変更のProduction採用提案前)レビュー→ユーザー判断。Production採用は人間ユーザーのみ | — | `APPROVED_FOR_PRODUCTION`は人間のみ |

QCD要約: Quality=受入例の改善とgate維持 / Cost=Step1,2はJPY0、Step3は約JPY32〜37[委任_02再計算]、Step4は約JPY41、運用は1 job+2〜4%(+Pkg E時は+記事あたり約JPY0.5) / Delivery=Step1〜2は並列に実装・test可能(独立file)。直列化の理由はStep3以降が実装(U1〜U4)とユーザー判断(OPEN-325/310)に依存するため。

---

## 10. ユーザー判断事項(推奨付き)

| ID | 論点 | 推奨 | 理由 |
|---|---|---|---|
| A | **Pkg U(U1〜U4)をTrial対象として進めるか** | **進める**(まずオフライン再判定 Step1〜2をJPY0で。U1は「予算拡大」と比較して採否を決める) | 受入例1の機械部分(shortlist到達の再生確認が必須)を満たす見込み。LLM追加なし・OPEN-325とは独立。誤爆は6記事でゼロ。U2はTier-Sのみで足りる可能性も比較する |
| B | 記事独自比喩のImportant除外を**ガイダンス+記録だけの軽い検査(T6)(推奨)** / ガイダンスのみ / 構造validator強制(T5)のどれにするか | **guidance+記録flag**[委任_02訂正: 旧推奨「ガイダンスのみ」から変更] | 強制(T5)は抽出LLMの自己申告に依存しretry増=費用増。一方、ABCで現行LLMが`two numbers in the ring`等に`idiom`・importantを付けた実証があり、記録なしでは違反率が測れない。記録flagはretryなし・費用増0 |
| C | Std/Adv別の「既知とみなす基準」文を入れるか(現状は共通Promptで冒頭"B1"のまま) | **Family X guidanceへ1文追加(Level別)**を検討。ただし効果単独は未検証のため、Trialで有無を比較 | 現行はLevel差の指示が無く、Stdの5枠中3枠が基本連語になった実績(v5)。冒頭「B1」自体の扱いは判断J |
| D | WordNet等のオフライン複数語辞書の導入調査(ライセンス原文確認・カバー率測定、導入は提案のみ) | **調査のみ承認** | `time lag`型をオンライン照会の予算・可用性に依存させない選択肢。今回はライセンス未確認で導入判断不可 |
| E | `pumps its fist`型の扱い | **原則化して承認**: 「定着表現の比喩的・擬人的適用は、正規化後の形(`pump one's fist`)が他記事でも使えるならImportant可」 | 個別例ではなく原則にすることで判断を一般化できる。ユーザー基準例に明示が無いので確認が必要。創作的比喩と見なす場合は`タグ`判定を調整 |
| F | Pkg E(LLM補助抽出v4)=OPEN-325(b1)と「本文全文をLLMへ送らない」原則の改訂 | **OPEN-325側で判断**(本設計は依存を明示するのみ) | 既存の判断待ち事項。**Std側の改善(受入例7)はこの判断に依存する**(冒頭§0-7) |
| G | Pkg R(Rule7ヘッドワード)=OPEN-310 | **OPEN-310で先行判断**を推奨 | `been behind price increases`型のINVALIDを根治できず、Pkg U/P/Eの効果が出ない |
| H | Pkg X(解説ページ用レコード) | **設計の記録のみ**(実装は解説ページ着手時) | KP Production無影響のsidecar。付加方法(§8-3)はLLM追加不要 |
| J [委任_02追加] | Std選定Prompt冒頭が「**B1**英語記事本文」のまま(Family Zと共有テンプレート)をどう扱うか | **別OPENとして切り出し**(共有テンプレートはFamily Zに影響するため、本件ではFamily X guidanceでLevel差を足す範囲に留める) | テンプレート本体の変更はFamily Z等へ波及する。本件で扱う場合はFamily X専用テンプレートの複製が必要=変更範囲が大きい |
| I | 次工程 | Opus独立レビュー(条件A)の必須修正は委任_02で反映済み → Fableが照合 → 別委任でStep1〜2(JPY0)、Step3は費用ガード設定後 | 新規構造の設計のため |

---

## 付録

### A. 本設計に使った小script(Production非接続、読取・集計のみ)
- `er064_kp_candidate_selection_design_01_upstream_trace.py`(候補供給の再現、lookup pool順位)
- `er064_kp_candidate_selection_design_01_wiktionary_probe.py`(Wiktionary既存関数で17語を1回照会)
- `er064_kp_candidate_selection_design_01_budget_sim.py`(U1の机上並べ替え)
- `er064_kp_candidate_selection_design_01_containment_pairs.py`(包含ペア列挙)
- `er064_kp_candidate_selection_design_01_known_signals.py`(CEFR-J/Zipfシグナル確認)

### A2. [委任_02追加] 本委任の位置づけ
委任_02はOpus独立レビュー(条件A)の必須修正6点+推奨修正を反映した設計書訂正のみ(費用JPY0、LLM/Wiktionary追加照会なし、script実行も新規実証なし。コード行の参照[L454-455/L643/L601/L483-484]は既存ファイルの読取のみで確認)。

### B. 実証の主要数値
- Coffee v5 Adv: 未一致2-3-gram pool 694件、`time lag`=76番目(予算60の外)、U1適用後=9番目。Wiktionary照会: `time lag`=True、`in the ring`/`raw bean(s)`/`price measure`/`pumps its fist`/`be behind`=False。
- Coffee v5 final: Std = raw bean(T) / push prices up / take time / right away / on a regular basis。Adv = lag(T) / price tag / show up / come down / come with。
- ABC-A(v4, n=3, gate): pump-fist 5/6採択、gate完全PASS 6/6。Std = {raw bean, two numbers in the ring, pump one's fist, push prices up, its own hidden clock}が中核。Adv = lag 9/9、be behind price increases A 3/3。
- 費用: 本委任 JPY0。
