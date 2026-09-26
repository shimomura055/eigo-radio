# Recon 02: EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01(Tier2/Tier3レビュー補完)

- 管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01
- 性質: レビュー(実装・Trial・Production変更・SSOT編集なし、API呼び出し0件、費用¥0)
- 前提: `docs/pm/recon_en_asr_semantic_equivalence_01.md`(Tier1数値系の穴・過去false rejection証跡(a)〜(h)・設計論点表・Regression Corpus候補表)を読了済み、重複調査していない。
- 本ファイルの実測は全てオフライン(`python3`で`er006_preprod_hardening_01_validation.classify_asr_match()`を直接呼び出し、API課金なし)。**推奨・採否は書かない**。

---

## T2-1 Tier 2候補ペアの棚卸し

### (a) 現在Production採用済みのペア(逐語、`er006_preprod_hardening_01_validation.py` L699-1004)

`classify_asr_match()`ラッパー(L952-1004)が、baseline(`_classify_asr_match_core`)がPASSしない場合のみ、`expand_standard_contractions()`(L732-745)を両側へ適用して再判定する。適用範囲は**英語ASR照合経路全体**(Key Phrase含む、opt-inフラグなし、L959-962コメント)。

- 否定保持contraction(`_NEGATION_CONTRACTIONS`, L699-706、17ペア): `don't→do not, doesn't→does not, didn't→did not, isn't→is not, aren't→are not, wasn't→was not, weren't→were not, hasn't→has not, haven't→have not, hadn't→had not, can't→cannot, won't→will not, wouldn't→would not, shouldn't→should not, couldn't→could not, mustn't→must not, needn't→need not, shan't→shall not`
- 非否定contraction(`_NON_NEGATION_CONTRACTIONS`, L714-724、26ペア): `i'm→i am, you're→you are, we're→we are, they're→they are, he's→he is, she's→she is, it's→it is, that's→that is, there's→there is, who's→who is, what's→what is, here's→here is, i've→i have, you've→you have, we've→we have, they've→they have, i'll→i will, you'll→you will, he'll→he will, she'll→she will, we'll→we will, they'll→they will, it'll→it will, i'd→i would, you'd→you would, he'd→he would, she'd→she would, we'd→we would, they'd→they would, let's→let us`
- 「'd」は**常に"would"へのみ**展開する(「had」の解釈は無い)。「's」は**常に"is"へのみ**展開する(「has」の解釈は無い)。曖昧性は「展開後に既存Validatorが一致した場合のみ採用」という設計(L964-983)で構造的に安全とされている(採用根拠: OPEN-123 §10、false accept 0/82)。
- **本Reconでの実測(T2-2-1c、下記)で、この安全設計に理論上の穴があることを実際に確認した**(「'd」が真に意味していた内容と異なる語をASRが出力しても、両者が同じ展開先("would")に収束すればPASSしてしまうケース。詳細はT2-2参照)。

### (b) OPEN-123 Trialで検証されたが不採用のペア(逐語引用、`OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-TRIAL-01_REPORT.md`)

- mode定義(§6、L106-111): "wanna_mode=b(適用しない、既定)/wanna_mode=a(無条件適用)/wanna_mode=c(Secondary/local corroboration必須)"。
- 59ケースの内訳(§8、L147-155の表): 「既存Regression fixture(POSITIVE 29+AMBIGUOUS 2+NEGATIVE 28)=59」「実例1: Trial-08 p3 Voice B(do not/don't)=3」「実例2: OPEN-122 wanna(P6)=1」「実例2: OPEN-122 asked/asks(Negative)=2」「新規TTS A(標準contraction+punctuation)=13」「新規TTS B(colloquial)=5」「新規TTS C(Negative Control、can/can't・will/won'tの否定反転含む)=6×3経路×3方式=54」。
- 対象ペア: `wanna⇔want to, gonna⇔going to, gotta⇔got to`(§201-208コード、`_COLLOQUIAL_CONTRACTIONS`、`er011_transcript_style_normalization_trial_01.py` L206-208)。
- 結論(§11、L214-219): mode_a(無条件)は「VALIDATED止まり、b05で理論上のリスクを確認、Production採用は非推奨」。mode_c(corroboration必須)は「VALIDATED(実例1件で正しく機能、テストカバレッジ小、ハーネスの自己参照上の限界あり)」。mode_b(現状維持)が「安全側、Production変更なし」。
- **b05の非対称性**(§6、L116-124、§8限界、L171-175): 「Secondary/Local側が台本の口語形を勝手に正書法"want to"へ書き換える非対称性」を実測1件で確認。Primary側での自然発生wanna化の再現率は依然1件(OPEN-122のP6のみ)にとどまる。

### (c) 未検証だがTier 2に含まれ得るペア(本Reconで実測、既存コードには不在)

| ペア | 意味変化の可能性 | 否定・時制・法助動詞に触れるか | 双方向 or 片方向 | 実測結果(現行コード、T2-2参照) |
|---|---|---|---|---|
| gotta⇔got to / have got to | 高(「got to」は「〜する機会を得た」達成の過去形とも読める、法助動詞「have got to」の省略とも読める、二重の曖昧性) | 法助動詞(義務)/完了形(達成)の両方に触れる | 未検証(実際に混同する具体例は本Reconでは構築できず) | 未実測(現行コードは非対応、TRUE_CONTENT_MISMATCH想定) |
| kinda⇔kind of | 中(「kind of X」の「of」脱落は「kind X」という別の名詞句と衝突しうる) | 触れない | 片方向が安全(canonical側が"kind of"、ASR側が"kinda"の場合のみ想定) | T2-2-5で実測(下記) |
| sorta⇔sort of | 中(kindaと同型) | 触れない | 同上 | T2-2-6で実測(下記) |
| 'cause⇔because | 低(意味はほぼ同一だが、"cause"は名詞「原因」としても頻出するため名詞用法との衝突リスクあり) | 触れない | 双方向は危険(名詞"cause"との衝突) | T2-2-7で実測(下記) |
| lemme⇔let me | 低 | 触れない | 双方向でも比較的安全 | T2-2-8で実測(下記) |
| gimme⇔give me | 低 | 触れない | 双方向でも比較的安全 | T2-2-9で実測(下記) |
| dunno⇔don't know | 中(否定"don't"を1語に埋め込むため、否定保護ゲートをすり抜けるリスクの構造を持つ) | **否定に触れる**(否定語が縮約に埋め込まれる) | 片方向が安全 | T2-2-10で実測(下記) |
| ya⇔you | 低(ただし"ya"は間投詞的用法もあり、代名詞以外の意味と衝突しうる) | 触れない | 双方向は危険 | T2-2-11で実測(下記) |
| outta⇔out of | 低 | 触れない | 双方向でも比較的安全 | T2-2-12で実測(下記) |
| ain't⇔am not/is not/are not/has not/have not(**5通りに曖昧**) | **高**(否定そのものは保持されるため意味反転のリスクは低いが、**主語一致・時制(単純現在/現在完了)がどれになるか一意に決まらない**) | **否定に触れる**、かつ現在完了⇔単純現在の時制選択を伴う | 片方向のみ安全(単一のasr→canonical方向へマップしても曖昧性は残る) | T2-2-13/14で実測(下記、5通りのうち1通りにしか展開できない構造的欠陥を確認) |

---

## T2-2 false acceptシナリオの具体列挙(実測、現行コード)

以下は全て`er006_preprod_hardening_01_validation.classify_asr_match()`をオフラインで実際に呼び出した結果(API呼び出し0件)。

| # | canonical | asr | 現行classification | should_pass | 備考(現行コードの実際の挙動) |
|---|---|---|---|---|---|
| T2-2-1 | "I'd already read the report before the meeting." | "I would already read the report before the meeting." | **TRANSCRIPT_STYLE_NORMALIZED_MATCH** | **True** | 現行Production採用済みの`i'd→i would`展開が発火し、両側とも"i would..."に収束してPASS。この例では意味が保たれている(意図通り)。 |
| **T2-2-1c(既存Production上の実在リスク)** | "By the time she called, I'd finished the entire report." | "By the time she called, I would finished the entire report." | **TRANSCRIPT_STYLE_NORMALIZED_MATCH** | **True** | **本Reconで実測した、現行Production(Tier2ではなくOPEN-123で既に採用済みの標準contraction展開)自体に存在するfalse accept構造**。canonicalの"I'd"は文脈上「I had」(過去完了)を意味しているが、`_NON_NEGATION_CONTRACTIONS`は"i'd"を**常に"i would"へのみ**展開する(L721)。ASR側が(何らかの理由で)文字通り"would"を書き起こした場合、両者は"I would finished..."という同一の(文法的には破綻した)文字列に収束し、実際には時制解釈が食い違っている(had=完了 vs would=仮定/意志)にもかかわらずPASSする。**これはTier2の新規リスクではなく、既にProduction配線済みのOPEN-123標準contraction展開が内包する既存の穴**(recon_01が指摘した「'd/'sは意味的に曖昧だが両側完全一致時のみ採用という設計で安全」という説明が、"canonical側の'd"の真の意味とは無関係に、ASR側がたまたま同じ展開先の語を発話・書き起こした場合には効かないことを実測で示した)。 |
| T2-2-1b | "I'd already read the report before the meeting." | "I had already read the report before the meeting." | TRUE_CONTENT_MISMATCH | False | 逆方向(ASR側が正しく"had"と書き起こした場合)は展開後も"would"≠"had"のためPASSしない(false rejectのまま、救済されない)。 |
| T2-2-2 | "You can't enter without a badge." | "You can enter without a badge." | TRUE_CONTENT_MISMATCH | False | 現行は"t"の脱落として`content_word_diffs`(delete)を検出、negation_mismatchesは0件(理由: normalize_textがアポストロフィを空白化するため"can't"→"can"+"t"となり、"t"自体は`_NEGATION_WORDS`に含まれない。もし将来Tier2が"cant"のような1トークン化を導入すると`_NEGATION_WORDS`の"cant"と衝突する可能性がある、要確認事項)。意味反転(可能⇔不可能)は正しくブロックされている。 |
| T2-2-3 | "The system won't restart automatically." | "The system wants restart automatically." | TRUE_CONTENT_MISMATCH | False | 正しくブロック。 |
| T2-2-4 | "We're gonna analyze the data." | "We're going into analyze the data." | TRUE_CONTENT_MISMATCH | False | "going into"という意味の異なる語句をcontent_word_diffsとして正しく検出(gonna⇔going toの単純な文字列マッピングだけでは"into"を弾けない設計の重要性を示す)。 |
| T2-2-4b | "We're gonna analyze the data." | "We're going to analyze the data." | TRUE_CONTENT_MISMATCH | False | 正当な等価ペアだが現行未対応のため救済されない(既知のfalse reject、Tier2導入で解決が期待される側)。 |
| T2-2-5 | "It's kind of expensive." | "It's kind expensive." | **ASR_VALIDATION_UNCERTAIN** | False | "of"は`_STOPWORDS`のため content_word_diffs には計上されず、ratio<0.98でfallbackへ落ちる。**Tier2で"kind of"⇔"kinda"の等価を認める設計にする場合、"of"の脱落自体は既にstopword経由で黙認されつつある(ただしratio閾値で最終的にブロックされている)ため、Tier2実装次第ではこの経路がそのままPASSに変わる可能性がある**(false accept候補: 実際には"kind of X"と"kind X"は異なる名詞句だが、現行の冠詞的除去ロジックがこれを「表記の揺れ」寄りに扱おうとする構造的圧力がある)。 |
| T2-2-6 | "The plan sort of worked." | "The plan sorta worked." | TRUE_CONTENT_MISMATCH | False | "sort"⇔"sorta"は1語対1語のreplaceとして検出、正しくブロック(現行は未対応のため false rejectのまま)。 |
| T2-2-7 | "We left early because it was raining." | "We left early cause it was raining." | TRUE_CONTENT_MISMATCH | False | "because"⇔"cause"は1語対1語のreplaceとして検出。**"cause"は名詞(原因)としても使われるため、Tier2で無条件に"because"と同一視すると、"That's the root cause of the delay."のような名詞用法の文で誤爆するリスクが構造的に存在する(本Reconでは名詞用法の具体的false accept例までは構築していない、追加検証が必要)。** |
| T2-2-8 | "Let me check the schedule." | "Lemme check the schedule." | TRUE_CONTENT_MISMATCH | False | "let me"(2トークン)⇔"lemme"(1トークン)、正しくブロック。 |
| T2-2-9 | "Give me a call tomorrow." | "Gimme a call tomorrow." | TRUE_CONTENT_MISMATCH | False | 同上。 |
| T2-2-10 | "I don't know the answer." | "I dunno the answer." | TRUE_CONTENT_MISMATCH | False | "don't know"(3トークン、否定語"don't"含む)⇔"dunno"(1トークン)。**現行`_NEGATION_WORDS`は"dont"という単独トークンなら否定として認識するが、"dunno"という合成トークンは否定語集合に無いため、この差はnegation_mismatchとしてではなく通常のcontent_word_diffとして検出されている(negation_mismatches=[]、content_word_diffsのみ)。もしTier2が"dunno→do not know"の展開を追加する場合、否定保護ゲート(`_NEGATION_WORDS`)への追加登録が必須になる、という実装上の具体的な注意点を実測で確認した。** |
| T2-2-11 | "Are you coming?" | "Are ya coming?" | TRUE_CONTENT_MISMATCH | False | "you"⇔"ya"、正しくブロック。 |
| T2-2-12 | "Get out of here." | "Get outta here." | TRUE_CONTENT_MISMATCH | False | "out"⇔"outta"、正しくブロック("of"は両側ともstopword扱いで既に計上外)。 |
| T2-2-13 | "It isn't ready yet." | "It ain't ready yet." | TRUE_CONTENT_MISMATCH | False | "isn"⇔"ain"のreplaceとして検出(否定自体は両側に存在するためnegation_mismatchesは0件、正しく非救済)。 |
| T2-2-14 | "I haven't seen it." | "I ain't seen it." | TRUE_CONTENT_MISMATCH | False | "haven"⇔"ain"のreplaceとして検出。**"ain't"は文脈上「am not/is not/are not/have not/has not」の5通りに展開されうるため、Tier2で単一の展開先(例: "is not")を選ぶ設計にすると、この実例("haven't"=have not)のような正当な救済対象を取りこぼす一方、別の文脈では誤って別の解釈と一致してしまうリスクが両方存在する(本ペアは現状「取りこぼし」側の実例)。** |
| T2-2-15 | "I wanna new phone." | "I want a new phone." | TRUE_CONTENT_MISMATCH | False | **"wanna"の二重の意味("want to"と"want a")を実測で確認**: "wanna"は名詞の前では口語的に"want a"(冠詞"a"の代用)としても使われる。現行のOPEN-123/Trial双方とも"wanna→want to"という単一マッピングのみを扱うため、この場合は展開後も"want to new phone"(不自然な文)≠"want a new phone"となり、**false acceptにはならず単に非救済のまま**(安全側)。ただし、もし将来Tier2の判定ロジックが「トークン数の差(1↔2)を許容する緩い比較」まで踏み込むと、"want to"と"want a"を区別できずに誤って一致させるリスクが理論上ある(現行の「両側完全一致のみ採用」という保守的設計を維持する限りは安全)。 |

**小括(事実のみ)**: 10件以上のTier2候補ペアを実測した結果、(1) 現行未対応のペア(gotta/kinda/sorta/'cause/lemme/gimme/dunno/ya/outta/ain't)はいずれも正しく`TRUE_CONTENT_MISMATCH`のまま(false accept 0件、ただし既知のfalse reject)、(2) **既にProduction採用済みの標準contraction展開(OPEN-123)自体に、"I'd"の解釈ambiguity(had/would)由来の実在するfalse accept構造がある**ことをT2-2-1cで実測確認、(3) "dunno"を将来Tier2へ追加する場合は`_NEGATION_WORDS`への登録が構造的に必須になる、という実装上の具体的知見を得た。

---

## T2-3 corroboration条件付き(mode_c相当)の安全性

### (a) OPEN-123実例での判定

`er011_transcript_style_normalization_trial_01.py`(L222-294)の`classify_with_style_normalization()`内、`wanna_mode="c"`分岐(L277-293)。実例(OPEN-123 Report §6、P6_dont_you、canonical="Don't you want to come with us?"、Primary ASR="Don't you wanna come with us?"、Secondary/Local ASR=canonical通り"want to")では、`corroborated_by=["secondary","local"]`となり`TRANSCRIPT_STYLE_NORMALIZED_MATCH`(should_pass=True)。表(OPEN-123 §8、L151)にも「wanna_mode=c: 救済(1/1)」と記録済み。

### (b) Secondary ASRも同じ縮約を返す場合(corroboration不成立)の扱い

コード上の仕組み(L278-284): `corroborated_by`は、secondary_text/local_textのそれぞれについて、まず`expand_contractions()`(標準contractionのみ、口語的縮約は展開しない)を適用した`other_c`を作り、`classify_asr_match(canon_c, other_c)`(`canon_c`=canonicalを標準contraction展開したもの、口語的縮約は未適用)がPASSするかどうかで判定する。**もしSecondary/LocalもPrimaryと同じ"wanna"を書き起こした場合、`other_c`も"wanna"のままとなり`canon_c`("...want to come...")とは一致しないため、`corroborated_by`は空リストのまま**(L294以降、コード参照範囲外だが構造上必然)。結果、`colloquial_candidate_rescued=False`相当となり、baseline(TRUE_CONTENT_MISMATCH)がそのまま返る。**つまりmode_cは「3経路全てが同じ聞き間違いをする」ケースには無力**(false rejectのまま、救済されない)。安全側だが、実運用上の救済率がPrimary/Secondary/Localが独立に間違えない場合に限定される、という制約が構造的に存在する。

### (c) 追加cost/latency(recon_01 §7の数値を再利用)

- Secondary ASR追加呼び出し自体の限界費用: recon_01 L164「Cascadeによる追加ASRコストは1回あたり$0.00002程度で無視できる水準」(`ER-006-GATE-CALIBRATION-ASR-CASCADE-MATH-VALIDATOR-01_report.md` L65)。
- Azure STT単発呼び出し実測単価: recon_01 L163「約13.8円/回相当」(`ER-005-AUDIO-VALIDATION-ROBUSTNESS-02_report.md` L164)。
- mode_cはSecondary/Local ASRが「既に他の目的(通常のCascade判定)で呼ばれている」場合は追加コストゼロ(結果を再利用するだけ)。Cascadeがそもそも未発火の経路(baseline PASSの場合)では、mode_cのために新たにSecondary/Localを呼ぶ追加コストが発生する設計次第(本Trialのテストハーネスは既存Cascade結果を再利用する前提で、追加API呼び出しは行っていない、Trial cost実測¥22.97はローカル文字列処理のみ)。
- OPEN-122 Equivalence Layer実測(recon_01 L165): 標準同期・実API合計¥3.34(A2 Flagship+B1実本文1件+敵対的陰性対照2件、TTS/ASR/Luna込み)が、同種の「Secondary/Local corroboration必須設計」を本番配線した場合の参考コスト規模。

### (d) OPEN-122 Equivalence Layerの既存corroboration機構の再利用可能性

`er011_connected_speech_equivalence_layer_production_01.py`:
- `_word_at_diff_matches_canonical(canonical_text, other_text, diff)`(L193-214、コメントL197「True→支持(corroboration、その位置でcanonical語と一致)」)が、diff位置単位でSecondary/Local ASRがcanonical側を支持するかを判定する既存の汎用ヘルパー。
- `classify_connected_speech_equivalence()`(L215-)内、`corroboration_count = sum(1 for v in (secondary_support, local_support) if v is True)`(L283)、`corroboration_count == 0 → INSUFFICIENT_EVIDENCE`(L291)という既存の判定パターン。
- **事実として、Tier2/mode_cが実装したい「独立ASRがcanonical側を支持する場合のみ採用」というロジックは、この`_word_at_diff_matches_canonical`/`corroboration_count`パターンと構造的に同型**(位置ベースかトークン全体ベースかの粒度の違いはあるが、「corroboration_count>=1のみ採用」という判定式自体は共通)。ただし本Trial(`er011_transcript_style_normalization_trial_01.py`)は独自に`corroborated_by`リストを実装しており、Equivalence Layerの関数を直接importして再利用してはいない(2つの独立実装が並存している状態、統合するかは設計判断)。

---

## T3-1 Tier 3救済候補の範囲(実測、5件以上)

`_is_benign_plural_pair`(規則的複数形)・entity_only_diffs(固有名詞差)・homophone_only_diffs(完全同音語差)はいずれも現行`ASR_VALIDATION_UNCERTAIN`(should_pass=False, should_retry=False)へ到達する。以下は「Secondary ASR corroborationで救済する設計にした場合のfalse acceptシナリオ」の実測(現行コードでの実際の分類を先に確認したうえで評価):

| # | canonical | asr | 現行classification | 該当メカニズム | false acceptシナリオとしての評価 |
|---|---|---|---|---|---|
| T3-1-a | "The article makes one point about pricing." | "The article makes one points about pricing." | ASR_VALIDATION_UNCERTAIN | `_is_benign_plural_pair`("point"/"points") | TTS-LOCAL-REWRITE report §12.2の実本番事例と同型(recon_01 (g)参照)。この例自体は意味を変えないが、"point"(論点/得点/小数点)は多義語であり、**文脈次第では単数/複数の違いが実際に量(得点差など)を意味することがある**(例: "The team is down one point"(1点差)vs"...one points"は非文法的で判別しにくいが、実際のスポーツ得点報告文脈では単数/複数が実質的な数値情報を持ちうる)。 |
| T3-1-b | "The team filed one report last week." | "The team filed one reports last week." | ASR_VALIDATION_UNCERTAIN | 同上("report"/"reports") | 文法的揺れのみで意味は変わらない、比較的安全な例。 |
| T3-1-c | "Please wait for the results." | "Please weight for the results." | TRUE_CONTENT_MISMATCH(homophone_candidateではあるが、entity_likeでもhomophone_only_diffsでもない単独パターンとしては本ケースはcontent_word_diffsのみで即TRUE_CONTENT_MISMATCH、`_try_homophone_number_rescue`は数字ゲート専用のため不発) | homophone_candidate自体はTrueだが本ケースは最終的にTRUE_CONTENT_MISMATCH(下記T3-2参照の通り、homophone_only_diffsに分類されるのはcontent_word_diffs全体がhomophone_candidateのみで構成される場合。本例は1件のみのdiffでhomophone_candidate=Trueだが、`non_entity_diffs`のフィルタ条件(`not d["entity_like"] and not d["homophone_candidate"]`)によりnon_entity_diffsから除外され、homophone_only_diffsへ回るはず。**実測結果は`TRUE_CONTENT_MISMATCH`だった。詳細確認要**(下記「実測上の注記」参照)。 | "wait"(動詞、待つ)⇔"weight"(名詞、重さ)は完全に異なる意味の単語であり、CMU辞書上の完全同音語一致だけを根拠にSecondary ASR corroborationで救済する設計は、**この組み合わせ自体が意味の異なる実在語のペアであるため、本質的にfalse acceptリスクを内包する**(現行コードのコメント[L580未満、No.8実例]でも「wait/weight」は既知の同音語問題として扱われている)。 |
| T3-1-d | "Ottoni and colleagues found similar results." | "Otani and colleagues found similar results." | ASR_VALIDATION_UNCERTAIN(entity_like=True) | entity_only_diffs | 固有名詞(学術者名)の音訳差、意味への影響は無い(同一人物を指している前提)、比較的安全。 |
| T3-1-e | "Triangeln station is nearby." | "Triangle station is nearby." | ASR_VALIDATION_UNCERTAIN(entity_like=True) | entity_only_diffs | 地名の音訳差、意味への影響は無い、比較的安全(ただし"Triangeln"[実在するスウェーデンMalmöの駅名]と"Triangle"[全く別の一般名詞/地名]が字面上は別の実体を指しうる場合、Secondary ASR corroborationが「別の実在地名」を偶然裏付けてしまうリスクは理論上残る)。 |
| T3-1-f | "It costs one dollar." | "It costs one dollars." | ASR_VALIDATION_UNCERTAIN | `_is_benign_plural_pair`("dollar"/"dollars") | 文法的揺れのみ(数量"one"自体は両側で一致しているため、値の誤りではない)、比較的安全。 |

**実測上の注記(T3-1-c)**: `wait`/`weight`の1語対1語replaceが`homophone_only_diffs`(should_pass=False, should_retry=False)ではなく`TRUE_CONTENT_MISMATCH`(should_retry=True)になった。コード(L876-880)を再確認したところ、`homophone_candidate`の判定自体は`protected_check()`内(L583-586)で行われ、`content_word_diffs`の各要素に`homophone_candidate`フラグとして正しく記録される(本実測でも`"homophone_candidate": false`と出力されていた)。**実際には"wait"/"weight"はCMU辞書上ARPAbet完全同音ではなかった**(`homophone_arpabet_equivalent()`が`False`を返した、CMU辞書の発音表記が異なる可能性がある。No.8実例で言及されている「wait/weight」問題は本Reconでは再現できなかった。既存のNo.8実例そのものを本Reconでは直接参照しておらず、本Reconが即席で作った例文が実際にはCMU辞書上同音判定されなかったことを事実として記録する)。**Tier3のhomophone救済ロジック自体は実測で動作を確認できなかった(本Reconの例文選定の限界であり、既存機構が壊れているという意味ではない)**。

---

## T3-2 時制・否定・値の保護の実効性(実測、各3件)

| カテゴリ | canonical | asr | 実測classification | number_mismatches | negation_mismatches | content_word_diffs(要約) |
|---|---|---|---|---|---|---|
| 時制1 | "The bridge will be rolled out next year." | "The bridge was rolled out next year." | **TRUE_CONTENT_MISMATCH** | [] | [] | "will"の削除(replace/delete) |
| 時制2 | "Prices are rising." | "Prices rose." | **TRUE_CONTENT_MISMATCH** | [] | [] | "rising"⇔"rose"のreplace |
| 時制3 | "She will complete the project." | "She completed the project." | **TRUE_CONTENT_MISMATCH** | [] | [] | "will complete"⇔"completed"のreplace |
| 否定1 | "The vaccine is effective." | "The vaccine is not effective." | **TRUE_CONTENT_MISMATCH** | [] | [["", "not"]] | なし(negation_mismatchesのみで検出) |
| 否定2 | "He can attend." | "He cannot attend." | **TRUE_CONTENT_MISMATCH** | [] | [["", "cannot"]] | "can"の削除(delete) |
| 否定3 | "This is safe." | "This is unsafe." | **TRUE_CONTENT_MISMATCH** | [] | [] | "safe"⇔"unsafe"のreplace(接頭辞否定は`_NEGATION_WORDS`の対象外だが、通常の内容語差として別ルートで正しく検出されている) |
| 値1 | "The price rose 5 percent." | "The price rose 15 percent." | **TRUE_CONTENT_MISMATCH** | [] | [] | "5xpercentx"⇔"15xpercentx"のreplace(数字マーカー込みでcontent_word_diffs、`_is_number()`は素の数字トークンのみを対象とするため、%マーカー付きの数値はnumber_mismatchesではなくcontent_word_diffs側で検出される) |
| 値2 | "The population is 2 million." | "The population is 3 million." | **TRUE_CONTENT_MISMATCH** | [["2", "3"]] | [] | なし(number_mismatchesのみで検出、"million"は数字トークンではなく`_is_number()`対象外のため差分自体は数字部分のみに現れる) |
| 値3 | "Revenue increased by $10." | "Revenue increased by $100." | **TRUE_CONTENT_MISMATCH** | [] | [] | "10xdollarx"⇔"100xdollarx"のreplace |

**事実確認**: 9件全てで`TRUE_CONTENT_MISMATCH`(保護が機能)を実測確認。値の差は検出経路が2パターンに分かれる(素の数字は`number_mismatches`、%/$マーカー付き数値は`content_word_diffs`)ことを実測で確認した(Tier1数値正規化の実装粒度によっては、この2経路のどちらに新Tierの判定ロジックを差し込むかで挙動が変わりうる、事実のみ記録)。

---

## C-1 7分類ラベルと現行`VALID_CLASSIFICATIONS`の写像表

ユーザー案7分類 ⇔ 現行12分類(`VALID_CLASSIFICATIONS`、L751-775)の対応:

| ユーザー案7分類 | 現行分類との対応 | 新規性 |
|---|---|---|
| EXACT_MATCH | `EXACT_MATCH`(既存) | 1対1、既存流用可 |
| SAFE_ORTHOGRAPHIC_EQUIVALENCE | `NORMALIZED_MATCH`(既存、発音区別符号・ハイフン・複合語分かち書き・英米綴り等) | 多対1、既存流用可(recon_01 §1.1・4(c)より) |
| NUMERIC_EQUIVALENCE | 現行は専用ラベル無し。数値表記差は`normalize_numeric()`が吸収できた分は`NORMALIZED_MATCH`に、吸収できない分(4(a)のmillion/billion複合等)は`TRUE_CONTENT_MISMATCH`に落ちる。`HOMOPHONE_MATCH_NUMBER_EXCEPTION`は数字ゲート例外という別の狭い機構(同音語限定)であり、Tier1数値等価そのものではない。 | **新規ラベルが必要**(既存のNORMALIZED_MATCH/TRUE_CONTENT_MISMATCHのどちらにも吸収されていない中間層) |
| TRANSCRIPT_STYLE_EQUIVALENCE | `TRANSCRIPT_STYLE_NORMALIZED_MATCH`(既存、ただし標準contractionのみ。wanna系は含まない) | 部分一致(既存ラベルは範囲が狭い、Tier2が"wanna"等まで含むなら同名ラベルの意味範囲を拡張するか、新規ラベルを切るかの選択が必要) |
| CONNECTED_SPEECH | `CONNECTED_SPEECH_ACCEPT`/`CONNECTED_SPEECH_PASS_WITH_WARNING`/`CONNECTED_SPEECH_EQUIVALENCE_ACCEPT`/`CONNECTED_SPEECH_EQUIVALENCE_PASS_WITH_WARNING`(既存4種) | 1対多、既存流用可 |
| PROTECTED_SEMANTIC_MISMATCH | `TRUE_CONTENT_MISMATCH`(既存) | 1対1、既存流用可(ただし現行は「retry対象」という運用上の意味も同時に背負っている、下記参照) |
| UNKNOWN | `ASR_VALIDATION_UNCERTAIN`(既存、should_retry=False) | 1対1、既存流用可(ただし現行のASR_VALIDATION_UNCERTAINは、entity_only_diffs・homophone_only_diffs・「内容語差は無いが一致率が届かない」の**3つの異なる原因**を1つのラベルへ集約しており、ユーザー案の分類粒度[SAFE_ORTHOGRAPHIC寄りの形態論的等価 vs 真にUNKNOWN]より粗い) |

未対応(新規追加候補): `HOMOPHONE_MATCH_NUMBER_EXCEPTION`はユーザー案7分類のどれにも直接対応しない(NUMERIC_EQUIVALENCEの部分集合として吸収可能かもしれないが、現状は「数字ゲート」という別の安全機構名で独立している)。

### 既存呼び出し元への影響(Grep実測)

- `VALID_CLASSIFICATIONS`の直接参照は3ファイルのみ(`er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py` L178のassert、`er011_transcript_style_normalization_production_wiring_01_test_01.py` L153のassertIn)。**いずれもテストコードであり、Production本体は`VALID_CLASSIFICATIONS`をハードコードした分岐に使っていない**(単なるドキュメント用tupleかつテスト用のvalidation)。
- `should_stop_retrying()`(`er006_preprod_hardening_01_validation.py` L1015-1027)が`r.classification in ("TRUE_CONTENT_MISMATCH", "TTS_FAILURE")`という**ラベル文字列への直接ハードコード依存**を持つ唯一の分岐(L1023)。新規ラベル(NUMERIC_EQUIVALENCE等)を「PASS系」として追加する場合はこの依存に触れない(should_pass=Trueならこの関数へ到達する前に`evaluate_attempt()`がreturnする、L1051-1052)。もし新規ラベルを「PASSしないが即mismatchでもない中間状態」として設計する場合は、この分岐への追加要否を個別に検討する必要がある(事実指摘のみ)。
- `er006_secondary_asr_01.py`は`result.classification != "ASR_VALIDATION_UNCERTAIN"`(L182, L194)、`cls.classification == "TRUE_CONTENT_MISMATCH" and cls.protected.passed`(L519)という**文字列直接比較の分岐を複数持つ**(Cascade層の中核)。新規ラベルを追加する場合、これらの分岐がその新規ラベルを"ASR_VALIDATION_UNCERTAIN"や"TRUE_CONTENT_MISMATCH"の代わりに誤って通過させない(または意図通り通過させる)ことを個別に確認する必要がある(事実指摘のみ、影響範囲としては同一ファイル内5箇所)。
- `er020_tts_retry_local_rewrite_01.py`(Local Rewrite判定): 本Reconで`should_pass`/`verified`/`status ==`/`classification`いずれのキーワードでも直接参照がヒットしなかった(recon_01 §3の「NG種別を区別しない」という記述を裏付ける実測結果)。**Local Rewriteはrole(segment_id)ベースのみで判定しており、分類ラベル追加の影響を受けない**。
- Telemetry(`er011_human_review_lock_01.py::record_outcome()`, L269「status = result.get("status")」、L348「"result_status": status」): **呼び出し元(generate関数)が渡した任意の文字列をそのまま`attempt_history.jsonl`へ書き込むだけの、ラベル非依存のパススルー**。新規ラベルを追加しても、telemetry自体のコード変更は不要(呼び出し元が新しいラベル文字列を`status`として渡すだけで自動的に記録される)。
- 個別呼び出し元(例: `er003_v1_sing01_voice01_generate.py` L148-159)は、ラベル文字列そのものではなく`ClassificationResult.should_pass`由来の`verified_content`(bool)で分岐している(L148「verified_content, stop_retrying, cls = ...」、L158「verified = verified_content and length_ok」)。**このことから、新規ラベルがshould_pass/should_retryを正しく設定してさえいれば、大多数の呼び出し元の制御フローは変更不要**という構造的知見を得た(C-1全体の総括)。

---

## C-2 実運用頻度(実測、¥0)

### attempt_history.jsonl(`er011_output/attempt_history.jsonl`、全6715行)

英語(`language=="en"`)レコード: **4069件**。`result_status`別内訳: `OK=2233, STOPPED=1411, ASR_VALIDATION_UNCERTAIN=425`。
**このファイルは`canonical_text_sha256`(ハッシュ)のみを保持し、生のcanonical/ASRテキストを保存していない**ため、diff内容(数値表記/複数形/縮約/その他)は**全4069件が判別不能**。

### review_lock_state.json(`find . -path "*/audit/review_lock_state.json"`、94ファイル)

英語segment-record: **882件**。`final_status`別: `OK=852, STOPPED=21, ASR_VALIDATION_UNCERTAIN=8, HUMAN_APPROVED=1`。
各segmentの`last_attempts_log`内、attempt単位の`audio_classification`(全attempt、retry分含む、延べ件数): `NORMALIZED_MATCH=675, EXACT_MATCH=149, TRUE_CONTENT_MISMATCH=88, HIGH_SIMILARITY_SAFE=16, ASR_VALIDATION_UNCERTAIN=14, TTS_FAILURE=10, TRANSCRIPT_STYLE_NORMALIZED_MATCH=7, CONNECTED_SPEECH_ACCEPT=3, HOMOPHONE_MATCH_NUMBER_EXCEPTION=2, CONNECTED_SPEECH_PASS_WITH_WARNING=1, CONNECTED_SPEECH_EQUIVALENCE_ACCEPT=1`。

診断内容の判別(このファイルは`canonical_text`の生テキストを保存していない、`asr_text`のみ保有):
- `TRANSCRIPT_STYLE_NORMALIZED_MATCH=7` → **縮約(contraction)** と判別可能(ラベル自体が確定させる)。
- `HOMOPHONE_MATCH_NUMBER_EXCEPTION=2` → **数値表記(同音数字ゲート)** と判別可能。
- `TRUE_CONTENT_MISMATCH=88`、`ASR_VALIDATION_UNCERTAIN=14`、`TTS_FAILURE=10` → **判別不能**(canonical生テキストが無く、`content_word_diffs`の内訳も保存されていないため、数値/複数形/縮約/その他のどれかを本Reconでは追加抽出できなかった)。

### tts_generation_results.json(`find . -path "*/audit/tts_generation_results.json"`、151ファイル)

英語segment: **448件**。うち`audio_classification`フィールドを持つもの(er006 validator経由): **316件**、持たないもの(er003旧世代validator経由、recon_01 §1.2で言及の`er003_v1_*`系レガシー経路): **132件**(このレガシー経路自体はTier2/Tier3の対象外である現行`er003.validate_asr_match`の3値判定を使っている可能性が高い、要個別確認)。
`audio_classification`の内訳(316件、attempt単位延べ件数): `NORMALIZED_MATCH=267, EXACT_MATCH=38, TRUE_CONTENT_MISMATCH=21, HIGH_SIMILARITY_SAFE=7, TRANSCRIPT_STYLE_NORMALIZED_MATCH=4, ASR_VALIDATION_UNCERTAIN=2`。
診断内容の判別: `TRANSCRIPT_STYLE_NORMALIZED_MATCH=4`→縮約、それ以外(`TRUE_CONTENT_MISMATCH=21, ASR_VALIDATION_UNCERTAIN=2`、計23件)は判別不能(理由は上記と同じ、`canonical_text`は本ファイルには保存されているケースもあるが[例示ファイルでは`"canonical_text"`キーが存在]、本Reconでは448件全件の逐語diff再計算までは実施していない[スコープ超過回避])。

### human_review_queue.jsonl(`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`)

全8件、**日本語(JA)専用ファイル**(サンプル確認したエントリのcanonical_textは日本語、`er007_ja_asr_validator_01.py`のJA専用分類ラベルを使用)。**英語segmentのNG分類には寄与しない(0件)**、念のため確認した事実として記録する。

### review_lock_state.json/tts_generation_results.json間の重複可能性についての注記

同一run/segmentが両ファイル形式に重複して記録されている可能性がある(recon_01 §1.2「英語Cascade統一エントリ」構成上、両者は異なる世代のスクリプトが書き込む先であり、本Reconでは名寄せ(同一segment_idの重複排除)を行っていない)。**上記の2つの集計(882件・448件)は単純合算しないこと**(単純合算すると二重計上のリスクがある)。

### 生ログ逐語引用(最大10件、`review_lock_state.json`を機械的に走査し先頭から10件を実抽出、`asr_text`のみ保持のためcanonical原文との対比は本Reconでは未実施)

| # | ファイル | segment_id | attempt | classification | asr_text(先頭部、長い場合は末尾を省略せず全文引用) |
|---|---|---|---|---|---|
| 1 | `er006_output/pool_pilot_01/pool_n18_notifications/a2/audit/review_lock_state.json` | full_story_part1 | 1 | TRUE_CONTENT_MISMATCH | "Imagine you are reading, studying, or working. Your phone is on the desk. You do not touch it. ...(中略、73人の大学生対象の2022年研究の説明が続く)...needed extra mental effort to keep working." |
| 2 | 同上 | full_story_part1 | 2 | TRUE_CONTENT_MISMATCH | (attempt 1と同一文面、2回連続同一ASR結果) |
| 3 | `er006_output/pool_pilot_01/pool_n18_notifications/b1b/audit/review_lock_state.json` | point_two | 1 | TRUE_CONTENT_MISMATCH | "A 2018 U.S. survey of teens age 13 to 17 found a familiar morning pattern. 72% said they often or sometimes checked messages or notifications soon after waking. ...habit." |
| 4 | 同上 | in_one_line | 1 | TRUE_CONTENT_MISMATCH | "Your phone does not have to be open to become **a** part of the task. In these studies, attention was pulled by the sound and affected by the silent device, ..." |
| 5 | 同上 | in_one_line | 2 | TRUE_CONTENT_MISMATCH | "Your phone does not have to be open to become part of the task. ..."(attempt1との差は"a part"⇔"part"の冠詞1語のみ、これがTRUE_CONTENT_MISMATCHの原因と推定される) |
| 6 | 同上 | in_one_line | 3 | TRUE_CONTENT_MISMATCH | attempt2と同一文面 |
| 7 | `er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/b1b/audit/review_lock_state.json` | comment_2 | 1 | TRUE_CONTENT_MISMATCH | "The studies show that a phone can affect attention even when you do not check it. How does this pull appear in everyday life, especially for teenagers?" |
| 8 | `er006_output/pool_pilot_01/pool_n8_airport_line/a2/audit/review_lock_state.json` | full_story_part2 | 1 | TRUE_CONTENT_MISMATCH | "Other passengers can make the line grow. ...(American Airlines Dallas Fort Worth 9ゲートの説明)... more hub and gateway airports in the future."(**同一文が2回連続で出現している**、ASR結果自体が本文を二重に書き起こしている可能性がある異常系) |
| 9 | `er006_output/pool_pilot_01/pool_n8_airport_line/b1b/audit/review_lock_state.json` | preview | 1 | TRUE_CONTENT_MISMATCH | "Why does a line appear at an airport gate before boarding has begun? ...whether a new boarding process could change it." |
| 10 | 同上 | in_one_line | 1 | **ASR_VALIDATION_UNCERTAIN** | "Gate lice are not simply careless passengers. They're responding to a small chance of a big loss, while American Airlines has now deployed a more controlled digital process at Dallas/Fort Worth." |

**判別区分(目視、diffの直接根拠[content_word_diffs]は本ファイルに保存されていないため推定)**: #4/#5/#6は冠詞"a"の有無のみの差と推定され「その他(冠詞、Tier1/2いずれの対象でもない)」、#1/#2/#3/#7/#9/#10はcanonical原文が無いため「判別不能」、#8は同一文の重複というASR異常(TTS読み上げ自体の反復幻覚寄りの可能性、OPEN-121領域)であり「その他」に分類。**数値表記・複数形・縮約が原因と断定できる例はこの10件には含まれなかった**(该当する実例は review_lock_state.json 全体を全走査すればさらに見つかる可能性があるが、本Reconでは「先頭から10件」という機械的な抽出に留めた)。

---

## 参照ファイル一覧(本Recon追加分)

- `er006_preprod_hardening_01_validation.py`(L699-1004ラッパー、L381-385 `_NEGATION_WORDS`、L487-531 `_STOPWORDS`/`_is_benign_plural_pair`、L534-591 `protected_check`、L1015-1027 `should_stop_retrying`、L1034-1055 `evaluate_attempt`)
- `er011_transcript_style_normalization_trial_01.py`(L206-294、`_COLLOQUIAL_CONTRACTIONS`/`classify_with_style_normalization`/mode_c corroboration実装)
- `er011_connected_speech_equivalence_layer_production_01.py`(L193-291、`_word_at_diff_matches_canonical`/`classify_connected_speech_equivalence`/`corroboration_count`)
- `er006_secondary_asr_01.py`(L182, L194, L305, L519、classification文字列直接比較箇所)
- `er020_tts_retry_local_rewrite_01.py`(classification/should_pass等への直接依存なしを実測確認)
- `er011_human_review_lock_01.py`(L255-354、`record_outcome`、telemetryパススルー構造)
- `er011_output/attempt_history.jsonl`(6715行、英語4069件)
- `er0*_output/**/audit/review_lock_state.json`(94ファイル、英語882件)
- `er0*_output/**/audit/tts_generation_results.json`(151ファイル、英語448件)
- `er007_output/ja_asr_cascade_01/human_review_queue.jsonl`(8件、JA専用)
- `OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-TRIAL-01_REPORT.md`(§6-11、mode定義・59ケース内訳・b05非対称性)
- `docs/pm/recon_en_asr_semantic_equivalence_01.md`(前提Recon、重複調査せず参照のみ)

---

Management-ID: EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01
