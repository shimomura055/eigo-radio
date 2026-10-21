# DESIGN_OPTIONS_01: 方式比較と推奨案(固有名詞発音供給 #133 ＋ 1語⇔複数語の同音救済)

管理ID: PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_01 / Status管理ラベル: `PLAN_DRAFT_PENDING_FABLE_REVIEW`(API 0・JPY 0・Production無変更)
入力: `INVESTIGATION_01.md`(既存仕様・実装・オフライン実測)。ユーザー原文§2③の「出発点方式」を案Aとして含む。
実測の出典(すべて同dir): `replay_result_01.json`(3,493ペア再適用)、`replay_result_01_noguard.json`(ガードablation)、`rule_domain_result_01.json`(適用域)、`demand_oov_result_01.json`(#133需要)。

## 0. 問題の分解(2レイヤー)

| レイヤー | 問い | byUsでの状態 | 解の性質 |
|---|---|---|---|
| **L1 判定** | 「綴りが違う・語数が違う・でも発音が同じ」ASR転写を、正しい発音としてNGにしないか | `Buy Us`/`buy us`が`TRUE_CONTENT_MISMATCH`(retry/HR行き) | 転写テキストと期待発音のみの純関数。ASR構成に依存しない |
| **L2 供給** | システムは**期待される正しい発音**をどう知るか(CMU辞書外・綴りが非標準の名前) | byUsはEN発音情報が空。CMUの`byus`(姓)がたまたま`bias`と同音 | 情報源・信頼度・キャッシュ・費用の問題。ASR選定の一部(Phrase List等)に依存 |

案A系はL1、案B系はL2。**両者は独立に採否を決められる**(L1はL2未完でも成立。L2はL1未完でも成立)。統合方針は「L1を先に小さく入れ、L2は需要・費用で段階化する」(§5)。

## 1. 比較する案

- **A 音韻列の連結比較(span限定)** — ユーザー出発点案。
  - A-all: 全語対象。A-ent: 単語側がentity_like(先頭大文字)/CamelCase/Ledger登録語/CMU代表発音がない語に限定。
  - A+: A に M1凍結候補(Ledger IPA→ARPAbet、CMU未収録の名前)を期待発音源として追加(Phase 2)。
- **B 発音供給(#133)** — B1 PNEP全面(記事ごと事前検出→web_search調査→登録→PL供給) / **B2 縮小・遅延型**(CMU収録語は調査しない、不一致が実際に起きた語だけ反応的に調査、決定的な無料情報源を先に、失敗はnegative cacheで再調査抑止) / B3 綴りのみPL供給(J2)。
- **C Writer側の読み併記の標準化**(`It is pronounced "bias."`型)。
- **D Primary/Secondary転写の統合判定**(二つの転写が互いに一致すれば許容する等)。
- **E 正規化前処理型**(ASR転写の隣接tokenを、音韻が一致するcanonical tokenに書き換えてから既存判定へ渡す)。
- **F 綴り近似の拡張**(despaceの類似度版)。
- **G 名前ごとの別名リスト**(`byUs`に`buy us/by us/bias`を許容別名として登録)。
- **H LLM判定**(「この2つは同じ音か」を毎回LLMへ)。
- **I 音声直接の音素比較**(音素認識model/強制アラインメントで音声から音素列を取り、期待音素列と比較)。
- **J 現状維持**(UDR #133の(イ): CMU層+人間承認、見込み再試行を許容)。

## 2. 比較表(Q＞D＞C。評価は計画段階の見込み。数値はオフライン実測か明記)

| 案 | 救済力 | 誤PASSリスク | 既存Validator/Ledger/retry/fallback整合 | 実装量 | 量産単価影響 | ASR選定依存 |
|---|---|---|---|---|---|---|
| **A-all** | byUsの`buy us/by us`(綴り違いの多語化)を救済。実測: 判定変化4ペア/3,493(全て`byus→buy us`)。通常語も理論上救済(461組) | 小。音が同じなら聴感も同じ(1:1同音と同一思想)。実測誤PASS 0。要ガード(略語`AI phone→iPhone`がG5で防がれる実例1件。文字読み`u s`/`a m`は空白差として既存規則が吸収済みで提案の対象外)。**最大の穴は既存と同じ「CMU綴り発音が正解という前提」** | 高。`homophone_candidate`の入口のみ拡張、下流(`_step_alternate_pass`/Secondary許容集合/retry/HR/F1/M1)は無改変。承認済み仕様CURRENT_SPEC.md:1839の**拡張(新仕様)** | 小(`hp`に純関数1つ＋`protected_check`の条件1行、test) | 実行時API 0、CMU辞書引きのみ(µs)。再試行削減は小さい(判定が変わるペア4/3,493=0.11%、全て1記事由来) | **なし**(転写テキストの純関数)。効果量だけ構成で変わる |
| **A-ent** | A-allのうち固有名詞/造語/Ledger登録語に限定。byUs(小文字始まり・CamelCase)を拾うには**CamelCase検出か登録語判定が追加で必要** | 最小(適用域が狭い) | A-allと同じ+新しい検出規則(entity_like判定の拡張=`capitalized_flags`系の変更。LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATION=Falseの方針[OPEN-208 NOT_ADOPTED]との緊張) | 中(検出の追加) | A-allと同じ | なし |
| **A+** (M1候補追加) | CMU辞書外の名前(Melos等)のn:mも救済(Ledger IPAが必要=L2に依存) | 中(IPA→ARPAbet近似。M1既存ガード[sources非空・F1内側]が前提) | M1の凍結候補機構を再利用。M1はUNCERTAIN限定のため、入口(A)が前提 | 中 | A同様+Ledger登録費(L2) | 弱(登録手段) |
| **B1** | CMU辞書外/非標準名の登録→Phrase List(重み2.0)/TTS/M1。PNEP実測: 7名中登録1名、Phrase Listは腕Mで6例中1例NG→PASS・Lion隠蔽1例 | 小(登録validator)だが「PLが誤発音を転写上で隠す」経路が実在(K5) | 既存`get_hint_for_text`/M1と整合するが**登録=TTS注入/PLが自動で変わる**(`tts_injection_disabled`等の取消手段J6が採用前提) | 大(検出D1/D2+調査+登録+隔離) | **悪化寄り**: 研究約5.4円/名(追加調査で約16円/名)、登録失敗名にも毎回支払う。1記事に未登録2〜3語で約11〜16円 | **強**(PLはAzure固有。OpenAI promptやWhisper hotwordは別実装) |
| **B2** | B1と同じ対象に、**不一致が実際に起きた語だけ**反応的に調査+決定的無料情報源優先+negative cache | 小 | 既存のcascade reactive lookup(`sec:341-`、`cascade_unresolved_entity`)と同系統。negative cacheは既存「unconfirmed entryを残す」(CURRENT_SPEC ER-23)の延長 | 中 | 調査は「不一致が出た名前×1回」に限定され、記事あたり期待費用は0〜数円(未測定・要Trial)。登録済み/negativeは0円 | 中(供給先[PL/prompt]だけ依存。登録・判定は独立) |
| **B3** | 綴りのみPL供給。実測: 多語化3例中1例消滅、悪化0 | **要注意**: PLが実発音の誤り(Lion)を転写で隠した例1 | 既存PL機構そのまま。§3-7「確定不能語は登録しない」との緊張(J2) | 小 | 追加費用0 | 強(Azure固有) |
| **C** | Writerが読みを本文に併記→聴取者には読みが伝わる。Validatorの救済には直接寄与しない | なし(判定不変) | Writer/Prompt原則の変更=ユーザー承認事項。併記内容の事実性(Writer推定)が新たな事実リスク(PNEP R-07) | 小(Prompt) | 費用0。発生頻度は低い(保存原稿2,425本中`pronounced`併記は1記事) | なし |
| **D** | 多語化の転写同士の突合では救えない(PrimaryとSecondaryが別の綴りを書く) | **大**: 「ASR consensus ≠ pronunciation verification」(CURRENT_SPEC.md:1837)に反する方向 | 統一judgeの状態機械(独立評価)を変更=仕様変更リスク大 | 大 | 0 | 強 |
| **E** | Aと同等(隣接tokenを書き換えてから既存判定) | 中: 位置制約を加えない書き換えは遠隔のtokenを誤結合しうる。位置制約を付ければAと同一 | ratio・F1・M1が整列後の転写を見る利点。ただし**書き換えで証跡が失われる**(原転写の併記が必要) | 中 | A同様 | なし |
| **F** | `buy us`は綴りが異なり救えない | 綴り近似は誤PASSの温床(`bias`/`bios`) | despace規則の拡張=Gate緩和 | 小 | 0 | なし |
| **G** | 名前ごとに救済 | 中(別名の網羅が個別依存) | 「ByUs専用」で汎用性なし(ユーザー要求外) | 小 | 0 | なし |
| **H** | 理論上高いが非決定的 | 中(LLMの判断ぶれ、固有名詞の偽陽性) | 決定的Gateを非決定判定で置換する形 | 中 | 毎回API費用(不一致1件あたり約0.1〜1円規模、頻度依存)＋レイテンシ | なし |
| **I** | 最も直接(音声自体を見る) | 小〜中(音素認識の精度依存) | 既存に無い新規モデル。CURRENT_SPEC.md:1837 (B)「安全に行う軽量な既存手段が無くSTOP」(OPEN-83) | 大 | 追加モデル/計算 | 強 |
| **J** | 現状維持(HR行き/再試行) | 誤PASS 0だが**正しい発音のNG(偽NG)が残る** | — | 0 | 再試行約5円/件+10分cooldown(byUs実測10.3円/本・20分) | なし |

## 3. 推奨案

**推奨: 「A-all(ガード付き)を先行(L1)」＋「B2を段階化(L2、需要確認後)」＋「Cは保険(Writer原則の変更なしでは採らない)」。**
- 採らない: D(仕様根拠に反する)、E(Aの劣化版+証跡喪失)、F・G・H・I(前節の理由)、B1・B3(原価悪化・誤発音隠蔽リスク)。Jは「Aを採らない場合の比較基準」。
- 理由(Q＞D＞C):
  1. **品質(Q)**: Aは既存の1:1同音と同一の思想(音が同じならNGにしない/音が違えばPASSしない)の自然な一般化で、承認済みGate(数値・否定・内容語ガード)は無改変。実測で誤PASS 0・想定外変化 0。ガードの限界効果はablationで測定済み(G5=`ai phone→iPhone`の1件。G4は保存データ上0件で任意)。
  2. **速度(D)**: AはASR選定に依存しない(転写テキストの純関数)ため、3方式ASR比較Trialの完了を待たず**オフライン検証・実装準備を先行**でき、Trial(有料部分)はASR確定後の最小限で済む。
  3. **単価(C)**: Aは実行時コスト0。B1(約11〜16円/記事)は70円/記事セットに対し無視できない悪化なので、B2(反応的・negative cache)に絞る。
  4. **簡潔さ**: 新規は純関数1つ＋条件1行。Ledger/検出/調査の大規模新設を避ける。
- **A-allかA-entか**: 推奨はA-all。理由: (i)ユーザー要求「ByUs専用でなく汎用」、(ii)A-entは小文字始まり造語(byUs)を拾うために新しい検出規則(entity_like拡張)を要し、OPEN-208(NOT_ADOPTED)と衝突、(iii)音が同じなら通常語でも期待どおりPASSで害が無い(実測の発火はbyusのみ)。**ただし適用域が通常語にも及ぶ(461組)ことは、ユーザー判断事項として明示**(判断候補U1)。保険として、新ルールで救済した判定にはaudit上`multiword_homophone`印を残し(additive key)、導入初期に事後確認できるようにする。

## 4. 推奨案Aの仕様ドラフト(Trialで検証する内容。実装はしない)

### 4-1. 判定規則(`val.protected_check`のhomophone_candidate算出箇所`val:750-753`の直後)
入力: SequenceMatcherのopcode(`replace`)が返す**隣接した連続span**(canon_span, asr_span)。
1. 既存の順序を維持: 数値/否定ガード → `_is_compound_spacing_only_span`(空白差) → benign複数形 → 既存1:1同音 → **(新)n:m音韻一致**。
2. (新)n:m音韻一致が真になる条件(すべて満たす):
   - G1 片側が単語1つ、もう片側が連続2〜3語(**1:n/n:1に限定**。両側複数語[oronym: ice cream/I scream等]は対象外)。
   - G2 全tokenが英字(`[a-z']`のみ)、数値・否定語を含まない。
   - G3 **脱落/追加を含まない**: spanは**生token列**(stopwordを除外しない)を使用。span内に余分な語(`an`等)があれば連結音素列が一致せず非救済。これにより`byUs`→`buy`(usの脱落)、`buy us an`(追加)は非救済。
   - G4 **文字読みガード(任意・限界効果の実証なし)**: 複数語側に1文字tokenを含まない(`mello s`型)。保存データでは単独で効く例が無く、過剰と判断されれば削除可。
   - G5 **略語ガード**: canonical側のtokenは3字以上(CMUの`ai`代表発音は`AY1`[=eye]で略語の『エー・アイ』ではなく、`am`/`us`は文字読みvariantを持つため、略語様の短いtokenは期待発音を綴りから決められない)。実測で効く例=`ai phone→iphone`。
   - G6 全tokenがCMU辞書収録(OOVは**判定不能=非救済**。推測でPASSさせない)。variantの直積が64組を超えれば判定不能。
   - G7 音素列はストレス記号を除いたARPAbetで、any-variant一致(既存`homophone_arpabet_equivalent`と同じ集合論)。
   - G8 比較範囲はspan内のみ(離れた語は結合しない)。
3. 真になれば`homophone_candidate=True`(`content_word_diffs`のdictに既存キーのまま、追加キー`multiword_homophone: true`を付す)。以降は既存経路(`ASR_VALIDATION_UNCERTAIN`→`_step_alternate_pass`→`HOMOPHONE_EQUIVALENT`→Primary/Secondary許容集合、retry/HR)。
4. 「不確実な判定を安易にPASSしない」: OOV/variant過多/ガード該当は従来どおりNG経路(`TRUE_CONTENT_MISMATCH`→retry)のまま。UNCERTAIN→既存のSecondary/M1/HRの経路に委ねる(新たなPASS経路を作らない)。

### 4-2. 具体例(`proto_multiword_span_01.py`の実行結果)
| canonical span | ASR span | 判定 | 理由 |
|---|---|---|---|
| `byus` | `buy us` / `by us` | **救済(PASS側)** | `B AY1 + AH1 S`=`B AY AH S`(ストレス無視)=`byus`の`B AY1 AH0 S` |
| `onto` | `on to` | 救済 | 音素一致 |
| `byus` | `bios` | 非救済(1:1) | `B AY1 OW0 S`≠。既存1:1で非同音 |
| `byus` | `buy` / `buy us an` | 非救済 | 脱落/追加(連結音素列が不一致) |
| `us` / `am` | `u s` / `a m` | (提案の対象外) | 空白除去で綴りが一致するため既存の空白差規則が先に吸収し**現行でもPASS**。既存の穴として別管理(INVESTIGATION_01 §5) |
| `melos` | `mellow s` | 非救済 | OOV+G4(`s`)。Ledger/M1(A+)の領域 |
| `ai phone` | `iphone` | 非救済(G5) | `ai`が3字未満。ガード無しなら救済=AIを「アイ」と読む誤りを素通し(実測: ガード無しで判定が変わる唯一の追加ペア) |

### 4-3. 実装位置と配線(提案のみ)
- 純関数: `er008_asr_variant_hardening_15_homophone_en.py`に追加(既存`_phone_variants`を再利用)。呼出: `val.protected_check`の1箇所。Family X/Z/Y共通で自動反映(`INVESTIGATION_01.md`§6)。
- 段階: (1)Trial(DEV専用): 本調査の`proto_multiword_span_01.py`方式(メモリ上のsource patch)で**Productionを編集せず**検証。(2)VALIDATED後・ユーザー採用後にProduction実装。11-7限定例外(flag)の利用は不要(Trial段階で隔離が完結するため。採用判断前にProductionへコードを入れない)。判断候補。

## 5. #133との統合方針

1. **統合の骨子**: #133の目的「正しい発音をシステムが持つ」を「期待発音源(Expected Pronunciation Source)」という共通概念に整理し、L1(判定)が参照する期待発音の出所を**階層化**する。現行は`CMU(綴り)`のみ。拡張は順に: ①CMU(現行) → ②Ledger EN entry(根拠付き、M1 C2の凍結候補) → ③JA公式読み(J7、候補提示のみ)。
2. **L1はL2を待たない**: ①だけで閉じる(byUsの`buy us`はCMU `byus`=`bias`同音で救済される)。ただしこれは「期待発音=CMU綴り発音」という**既存の前提**に乗っているだけで、byUsの公式発音を確認したわけではない。この限界は全文書で明示する(INVESTIGATION_01 §2-追加1)。
3. **L2(#133)は縮小・段階化(B2)**: 
   - 対象: CMU辞書外の外国由来名(実需要=Triangeln/Ottoni/Seishiro等、`demand_oov_result_01.json`)に限る。CMU収録語(byUs、LINE、Vera等)は調査しない(PNEP R-05)。
   - 契機: 不一致が実際に起きた語のみ(反応的)。pre-TTSの全記事一括検出(D1/D2)は費用対効果が悪いので採用しない(記事あたり約0.5〜0.6円の検出費自体は小さいが、調査費が支配的)。
   - 結論としてUDR #133の選択肢では**(イ)現状維持を土台に、L1(案A)を追加採用する**形を推奨し、(ア)(ウ)は採らない。L2(B2)は「CMU辞書外の名前でHRが増える」実測が出た場合のオプションとして計画に残す(今は着手しない)。
4. **未解決のままの前提を隠さない**: byUsの公式EN発音は未確認(PNEP K1)。J7(権利者公式の日本語読み「バイアス」を根拠にしてよいか)はユーザー判断で、L1の成立には影響しないが、byUsのTrial正例ラベルの根拠に影響する(`TRIAL_PLAN_01.md`§2、シナリオ別ラベル)。

## 6. 固有名詞の正しい発音を取得する仕組み(ユーザー§2②、案B2の具体化)

### 6-1. 情報源の優先順位(上ほど優先。AIの推測は根拠にしない)
| Tier | 情報源 | 例 | 検証可能性 | 登録時のconfidence上限 |
|---|---|---|---|---|
| T0 | CMU辞書(収録語、既存) | line、bias | ローカル、決定的 | (登録不要。CMU層で足りる) |
| T1 | 権利者/本人の**英語**公式情報(音声・動画の書き起こし、公式の発音注記) | 公式サイトの"pronounced…"、公式動画の書き起こし | 出典URL+quoteの本文一致(PNEP V1')。音声・動画のみで書き起こし無し→不可(`media_source_quote_not_text_verifiable`) | high(音声source)/medium |
| T2a | 信頼できる辞書(Oxford Learner's、Cambridge、Merriam-Webster、Collins) | Vera(PNEP実績) | URL+quote | medium〜high |
| T2b | 公開参照データの発音欄(Wikipedia冒頭IPA、Wiktionary、Wikidata P898)**[決定的取得で費用ほぼ0の見込み。未検証=Trialで検証]** | 人名・地名・組織名 | HTTP取得でquote照合可能 | medium以下 |
| T3 | 権利者公式の**日本語読み**(カタカナ)→英語音素の写像 | byUs=バイアス | quote可能だが**英語発音の証拠ではない**(V2: カタカナ由来は不可)。J7でユーザーが認めた場合のみ「候補」として扱う | 候補のみ(単独で自動PASSの根拠にしない) |
| T4 | AI(LLM)による推定、綴りからの規則推定(G2P) | g2p_en等 | 検証不能 | 登録不可。**Human Review/Writer併記の素材にのみ使用** |

- 複数源がある場合: **上位Tierが優先**。同Tier内で矛盾→両方を許容発音集合(`alternate_pronunciations`)として登録できるのは**両方が根拠付きの場合のみ**。上位源と下位源が矛盾→上位を採用し下位は記録のみ(PNEP V5: 既存entryと矛盾する登録は禁止・競合を記録)。矛盾が解消できない→登録せず`UNCONFIRMED_SAFE`。
- G2P: `pronouncing`0.3.0/`cmudict`1.1.3は導入済み(`pip list`確認)。`g2p_en`・`eng_to_ipa`は未導入(導入候補、**今回はインストールしない**)。G2Pの出力はT4(推定)であり、登録・自動PASSの根拠にしない。

### 6-2. IPA等への変換・正規化
- 既存`m1.ipa_to_arpa`(`m1:91`)を再利用(新規変換器を作らない)。ストレス除去・any-variantは判定側で行う(`hp`同様)。IPA→ARPAbetは近似であり、CURRENT_SPEC.md:1837(B)「IPA→ARPAbet変換による近似自動PASSは行わない」と、M1の承認(2026-10-13: sources非空のLedger IPAをCMU未収録語の候補に使う)の**線引きを維持**: T1/T2の根拠付きIPAのみM1 C2候補にでき、T3/T4は候補にしない。
- 非英語由来のIPA(native発音)は`m1:88 _NON_ENGLISH_LABEL`が既に除外。

### 6-3. Ledger登録とキャッシュ(スキーマ追加なし)
- 登録条件はPNEP V1'-V6(出典URL+quote本文一致、非カタカナ、形式、confidence、競合、追跡)をそのまま使う。Tierは`resolution_method`の値(`en_official`/`en_dictionary`/`en_reference_data`)と`sources`で表す(新フィールドを足さない)。`led:77 entry_invalid_reason`・`ledger_disabled`の枠で不正を隔離。
- **キャッシュ=Ledger自体**(記事・Family横断で再利用、`source_context=""`)。**negative cache**: 調査したが確認できなかった名前は、PNEP V6の`UNCONFIRMED_SAFE`を「hint空のunconfirmed entry」として残し(CURRENT_SPEC ER-23と整合、`get_hint_for_text`はhint空を返さないので供給されない)、`updated_at`から一定期間(案: 90日)は再調査しない。**TTLの数値・保存形式は判断候補**(Fable/ユーザー)。
- 漏れ対策: LINE型(大小無視一致で無関係34テキストに発火)を避けるため、CMU収録語は登録しない。J5(`us`→`unknown`汚染の76テキスト)は既存問題としてPLIR1後の状態を再確認(別管理)。

### 6-4. 見つからない場合の自律解決(HR転送の前に)
1. T2b(決定的・無料)を試す(Trialで有効性を検証)。
2. 不一致が実際に出た名前に限り、`make_writer_research_fn`系のweb_search調査を1回(日次/記事あたりの回数上限は既存R5/R6を踏襲)。#134(Perplexity枠切れ)の結果、調査手段はOpenAI web_search(コスト高)が現実的な選択肢。
3. それでも不明: (a)該当segmentだけHR(音声付きパッケージ、既存)、(b)Writer併記(案C、承認事項)、(c)次回以降のためnegative cache。**AIの推測だけで発音を確定しない**(T4は根拠にしない)。
4. 「HRに回さない条件」: 不一致がL1(案A)で音韻一致と判定できる場合(byUsの`buy us`)はHR/再試行に回さない。それ以外のOOV不一致のみHR。

### 6-5. byUsの正しい発音の取得・確定(ユーザー§7-3)
現状の証拠(`TRIAL_RESULT_01.md` K1, `j7_evidence.json`): ①英語公式の発音記載なし(腕A 2呼出ともUNCONFIRMED)、②権利者公式のPR TIMESは「byUs（バイアス）」＝日本語読みのみ(quote確認済み)、③CMU `byus`(姓)=`B AY1 AH0 S`、④原稿自体が"pronounced bias"と併記(Writer生成、②由来の可能性が高く独立証拠ではない)。
- 確定の仕方は**ユーザー判断J7に依存**: (J7=認める)T3を「権利者公式の読み」として`bias`系音素`B AY AH S`を期待発音として確定、Trial正例の根拠とする。(J7=認めない)byUsはUNCONFIRMEDのまま。L1は影響を受けない(CMU綴りが土台)が、byUsを「確認済み正例」とは呼ばない。
- **いずれの場合も、AIが単独で確定しない**。確認できた時点でのみLedger登録(T1/T2 or J7)。

## 7. ASR選定への依存管理(ユーザー§3)

| 項目 | 依存 | 構成が変わっても成立するか | 再評価が必要な点 |
|---|---|---|---|
| 案Aの判定規則(純関数)、ガード、unit test、オフライン再適用 | なし | **成立** | 新Primary/Secondaryの転写で再適用し、判定変化の件数と内訳を再測定(API 0〜低額) |
| 負例バンク(CMU由来の近傍音生成、文字読み) | なし | 成立 | — |
| 効果量(どのエンジンが多語化を起こすか) | **あり** | 成立しない場合がある | Azure(Secondary)が多語化(`Buy Us`/`by us`)の主因だった(byus多語化の実転写6ペア[全て1記事run_byus_01]: Secondary 4 / Primary 2)。Azureが外れる構成・Whisperが入る構成では発生頻度が変わる→3方式比較Trialの転写キャッシュを再適用して再測定 |
| 案B2の調査・登録・Ledger | なし(ASR非依存) | 成立 | — |
| 供給先(Phrase List=Azure固有) | **あり** | Azureが外れれば無効 | OpenAI promptのbias語/Whisper hotwordsへの供給アダプタ化が必要(別設計)。B3(PL綴りのみ供給)は特に依存 |
| 統一judge(Primary/Secondary独立評価、Secondary許容集合) | 構成の役割定義に依存 | 判定ロジックは構成非依存(`secondary_accept_fn`に渡す) | 新Secondaryの`secondary_accept`経路で`HOMOPHONE_EQUIVALENT`が使えること(コード上は構成非依存だが、Trialで確認) |
| 有料Trial(designed audio × 新Primary/Secondary構成) | **あり** | ASR確定後に実施 | ASR確定前は有料部分を開始しない(ユーザー要件) |

3方式ASR比較Trial(`docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/`)の設定・評価・進行は変更しない。その完了後の**転写キャッシュは読み取り専用で再利用**できる見込み(Trial側が保存形式を決める。再利用可否は完了後に確認、**未確認**)。

## 8. QCD概算(詳細は`TRIAL_PLAN_01.md`§7)

- 実装(案A、Production): 純関数＋条件1行＋test約15〜25本。開発費は主に人手/トークン。実行時API 0。
- 量産単価: 案Aは実行時 0円/記事。期待値としては再試行削減(byUs型1件で約5円＋10分)×発生率(0.11%、全て1記事由来)で記事あたり0〜0.1円オーダーの**微減**。B2は期待費用0〜数円/記事(未測定、Trial対象)。B1は11〜16円/記事の悪化見込み(PNEP実測に基づく)で非推奨。
- 納期: Aは3方式ASR比較の完了を待たずオフライン検証まで進められる。有料Trialは約20〜60円・数時間規模(`TRIAL_PLAN_01.md`§7)。
- 不確実性: 発生率は保存データ上の値(Azureが主因)で、新Primary/Secondaryで変わり得る。B2の単価は未測定。
