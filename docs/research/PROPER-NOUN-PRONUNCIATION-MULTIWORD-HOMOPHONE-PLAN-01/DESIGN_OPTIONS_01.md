# DESIGN_OPTIONS_01: 方式比較と推奨案(固有名詞発音供給 #133 ＋ 1語⇔複数語の同音救済)

管理ID: PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_01 / Status管理ラベル: `PLAN_V2_PENDING_USER_FIX`(v2=委任_02: Fable/Opus独立レビューOF-PNMH-R-01〜13を反映。API 0・JPY 0・Production無変更)
入力: `INVESTIGATION_01.md`(既存仕様・実装・オフライン実測)。ユーザー原文§2③の「出発点方式」を案Aとして含む。
実測の出典(すべて同dir): `replay_result_01.json`(3,493ペア再適用)、`replay_result_01_noguard.json`(ガードablation)、`rule_domain_result_01.json`(適用域)、`demand_oov_result_01.json`(#133需要)。 v2追加: `collect_pairs_02.py`→`pairs_02.jsonl`(4,032ペア)、`measure_v2_01.py`→`measure_v2_result_01.json`(pairs_02・ガード構成V1〜V8・R-01〜R-04)・`measure_v2_result_01_vocab01.json`(委任_01と同語彙の456組)・`triples_review_list_01*.json`(目視レビュー用リスト)。

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
| **A-all** | byUsの`buy us/by us`(綴り違いの多語化)を救済。実測: 判定変化4ペア/3,493(全て`byus→buy us`)。通常語も理論上救済(456組、うちストレス込みでも一致284/ストレス除去で初めて一致172[v2・R-01]) | 小。音が同じなら聴感も同じ(1:1同音と同一思想)。実測誤PASS 0。要ガード(略語`AI phone→iPhone`がG5で防がれる実例1件。文字読み`u s`/`a m`は空白差として既存規則が吸収済みで提案の対象外。`by us`も同様で新規救済ではない・R-12)。**最大の穴は既存と同じ「CMU綴り発音が正解という前提」**。**v2追記(R-01/R-02)**: 連結比較は**ストレス無視**で、既存1:1(ストレス込みの完全一致)より緩い=CURRENT_SPEC:1839からの緩和(§4-1 G7)。CMU `bi`=`B AY1`のため`bias`⇔`Bi-us`も同音扱いになり、CURRENT_SPEC:454(`Bi-us`は引き続きNG)と衝突する(§4-2/4-3) | 高。`homophone_candidate`の入口のみ拡張、**下流コード**(`_step_alternate_pass`/Secondary許容集合/retry/HR/F1/M1)は無改変だが**判定挙動は4点で変化**する(§4-4・R-04)。承認済み仕様CURRENT_SPEC.md:1839の**拡張(新仕様)** | 小(`hp`に純関数1つ＋`protected_check`の条件1行、test) | 実行時API 0、CMU辞書引きのみ(µs)。再試行削減は小さい(判定が変わるペア4/3,493=0.11%、全て1記事由来) | **なし**(転写テキストの純関数)。効果量だけ構成で変わる |
| **A-ent** | A-allのうち固有名詞/造語/Ledger登録語に限定。byUs(小文字始まり・CamelCase)を拾うには**CamelCase検出か登録語判定が追加で必要** | 最小(適用域が狭い) | A-allと同じ+新しい検出規則(entity_like判定の拡張=`capitalized_flags`系の変更。LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATION=Falseの方針[OPEN-208 NOT_ADOPTED]との緊張) | 中(検出の追加) | A-allと同じ | なし |
| **A+** (M1候補追加) | CMU辞書外の名前(Melos等)のn:mも救済(Ledger IPAが必要=L2に依存) | 中(IPA→ARPAbet近似。M1既存ガード[sources非空・F1内側]が前提) | M1の凍結候補機構を再利用。M1はUNCERTAIN限定のため、入口(A)が前提 | 中 | A同様+Ledger登録費(L2) | 弱(登録手段) |
| **B1** | CMU辞書外/非標準名の登録→Phrase List(重み2.0)/TTS/M1。PNEP実測: 7名中登録1名、Phrase Listは腕Mで6例中1例NG→PASS・Lion隠蔽1例 | 小(登録validator)だが「PLが誤発音を転写上で隠す」経路が実在(K5) | 既存`get_hint_for_text`/M1と整合するが**登録=TTS注入/PLが自動で変わる**(`tts_injection_disabled`等の取消手段J6が採用前提) | 大(検出D1/D2+調査+登録+隔離) | **悪化寄り**: 研究約5.4円/名(追加調査で約16円/名)、登録失敗名にも毎回支払う。1記事に未登録2〜3語で約11〜16円 | **強**(PLはAzure固有。OpenAI promptやWhisper hotwordは別実装) |
| **B2**(v2: #133判断後の別計画へ分離・R-08) | B1と同じ対象に、**不一致が実際に起きた語だけ**反応的に調査+決定的無料情報源優先+negative cache | 小 | 既存のcascade reactive lookup(`sec:341-`、`cascade_unresolved_entity`)と同系統。negative cacheは既存「unconfirmed entryを残す」(CURRENT_SPEC ER-23)の延長 | 中 | 調査は「不一致が出た名前×1回」に限定され、記事あたり期待費用は0〜数円(未測定・要Trial)。登録済み/negativeは0円 | 中(供給先[PL/prompt]だけ依存。登録・判定は独立) |
| **B3** | 綴りのみPL供給。実測: 多語化3例中1例消滅、悪化0 | **要注意**: PLが実発音の誤り(Lion)を転写で隠した例1 | 既存PL機構そのまま。§3-7「確定不能語は登録しない」との緊張(J2) | 小 | 追加費用0 | 強(Azure固有) |
| **C** | Writerが読みを本文に併記→聴取者には読みが伝わる。Validatorの救済には直接寄与しない | なし(判定不変) | Writer/Prompt原則の変更=ユーザー承認事項。併記内容の事実性(Writer推定)が新たな事実リスク(PNEP R-07) | 小(Prompt) | 費用0。発生頻度は低い(保存原稿2,425本中`pronounced`併記は1記事) | なし |
| **D** | 多語化の転写同士の突合では救えない(PrimaryとSecondaryが別の綴りを書く) | **大**: 「ASR consensus ≠ pronunciation verification」(CURRENT_SPEC.md:1837)に反する方向 | 統一judgeの状態機械(独立評価)を変更=仕様変更リスク大 | 大 | 0 | 強 |
| **E** | Aと同等(隣接tokenを書き換えてから既存判定) | 中: 位置制約を加えない書き換えは遠隔のtokenを誤結合しうる。位置制約を付ければAと同一 | ratio・F1・M1が整列後の転写を見る利点。ただし**書き換えで証跡が失われる**(原転写の併記が必要) | 中 | A同様 | なし |
| **F** | `buy us`は綴りが異なり救えない | 綴り近似は誤PASSの温床(`bias`/`bios`) | despace規則の拡張=Gate緩和 | 小 | 0 | なし |
| **G** | 名前ごとに救済 | 中(別名の網羅が個別依存) | 「ByUs専用」で汎用性なし(ユーザー要求外) | 小 | 0 | なし |
| **H** | 理論上高いが非決定的 | 中(LLMの判断ぶれ、固有名詞の偽陽性) | 決定的Gateを非決定判定で置換する形 | 中 | 毎回API費用(不一致1件あたり約0.1〜1円規模、頻度依存)＋レイテンシ | なし |
| **I** | 最も直接(音声自体を見る) | 小〜中(音素認識の精度依存) | 既存に無い新規モデル。CURRENT_SPEC.md:1837 (B)「安全に行う軽量な既存手段が無くSTOP」(OPEN-83) | 大 | 追加モデル/計算 | 強 |
| **J** | 現状維持(HR行き/再試行) | 誤PASS 0だが**正しい発音のNG(偽NG)が残る** | — | 0 | 再試行約5円/件+10分cooldown(byUs実測10.3円/本・20分) | なし |

## 3. 推奨案(v2)

**推奨: 「A-all(ガード付き)を先行(L1)」。ただし(i)ストレス無視は既存1:1より緩い新仕様として明示、(ii)canonical側がentity_likeのときは代表(先頭)variantのみ、(iii)`Bi-us`型の合否ラインはユーザー判断、とする。L2(発音供給#133)は今回のFix範囲外とし、#133判断後の別計画(§6は骨子のみ)。Cは保険(Writer原則の変更なしでは採らない)。**
- 採らない: D(仕様根拠に反する)、E(Aの劣化版+証跡喪失)、F・G・H・I(前節の理由)、B1・B3(原価悪化・誤発音隠蔽リスク)。Jは「Aを採らない場合の比較基準」。B2は#133判断後の別計画。
- **位置付け(R-11)**: 本案は、ユーザー決定済みのconnected-speech 3パターン(`val:1126-1131`、「この3種以外へ拡張しない」)の拡張**ではない**。同音判定の**入口**(`homophone_candidate`算出、`val:750-753`)を「1語⇔1語」から「1語⇔連続2〜3語」へ一般化するもので、connected-speech側のパターンは増やさない。
- 理由(Q＞D＞C):
  1. **品質(Q)**: 音が同じなら聴感も同じ、という既存1:1同音と同じ**思想**の一般化。承認済みGate(数値・否定・内容語ガード)は無改変、実測で誤PASS 0(§4-1)。ただし**既存1:1とは同一でない**(ストレス無視[R-01]、`bias`⇔`Bi-us`[R-02]、判定挙動の変化4点[R-04])ことを§4で明示し、ユーザー判断事項へ分離した。
  2. **速度(D)**: AはASR選定に依存しない(転写テキストの純関数)ため、オフライン検証は3方式ASR比較の完了を待たず先行でき、有料Trialは最小限(§TRIAL_PLAN 7)。
  3. **単価(C)**: 実行時API 0。再試行削減は小さい(保存転写4,032中4ペア=0.10%、全て1記事由来)ため、**価値は「偽NGの種類を1つ消す予防」**であり、計画・Trialの分量はそれに見合う必要最小限に絞る(Charter原則1)。
  4. **簡潔さ**: 新規は純関数1つ＋条件1行(＋条件付きaudit key)。
- **A-allかA-entか**: 推奨はA-all。理由: (i)ユーザー要求「ByUs専用でなく汎用」、(ii)A-entは小文字始まり造語(byUs)を拾うために新しい検出規則を要し、OPEN-208(NOT_ADOPTED)と衝突、(iii)音が同じなら通常語でも期待どおりPASSで害が無い(実測の発火はbyusのみ)。**適用域が通常語にも及ぶこと(理論上456組、§4-1)はユーザー判断事項(U1)**。推奨初期値=全語に適用し、**entity_likeは代表variant限定**(G9)。
- **既存のズレに上乗せしない(R-10)**: CURRENT_SPEC:1839は「Secondary(または2回目のASR)側が…を満たした場合のみPASS」と規定するが、コードはPrimary#1単独で`_step_alternate_pass`が成立すれば即PASSする(`sec:937-951`、`cmu_alternate`)。調査結果は`INVESTIGATION_01.md` §8-1(結論: (ii) 仕様文言とコードの不一致、Fable判定要)。**新ルールはこの既存挙動を拡大も是正もしない**: 新ルールで救済した判定も既存1:1と同じ経路(`_step_alternate_pass`→Primary/Secondary許容集合)に載せるだけで、Primary単独PASSの是非は本計画で決めない(是正が必要ならFableが11-8として別管理)。

## 4. 推奨案Aの仕様ドラフト(v2。Trialで検証する内容。実装はしない)

### 4-1. 判定規則(`val.protected_check`のhomophone_candidate算出箇所`val:750-753`の直後)
入力: SequenceMatcherのopcode(`replace`)が返す**隣接した連続span**(canon_span, asr_span)。
1. 既存の順序を維持: 数値/否定ガード → `_is_compound_spacing_only_span`(空白差) → benign複数形 → 既存1:1同音 → **(新)n:m音韻一致**。
2. (新)n:m音韻一致が真になる条件(すべて満たす):
   - G1 片側が単語1つ、もう片側が連続2〜3語(**1:n/n:1に限定**。両側複数語[oronym: ice cream/I scream等]は対象外)。
   - G2 全tokenが英字(`[a-z']`のみ)、数値・否定語を含まない。
   - G3 **脱落/追加を含まない**: spanは**生token列**(stopwordを除外しない)を使用。span内に余分な語(`an`等)があれば連結音素列が一致せず非救済(`byUs`→`buy`、`buy us an`は非救済)。
   - G4 **文字読み・音節区切りガード**: (a)複数語側に1文字tokenを含まない(`mello s`型)。(b)**(R-02、ユーザー判断U-BIに依存)** 複数語側の2字tokenは閉じた機能語集合(`us/on/to/in/of/by/at/it/is/as/or/an/my/me/he/we/be/do/go/up/so/no/if/am/ok`)のみ許可(案V8)。`Bi-us`型(CMU `bi`=`B AY1`が`bias`⇔`bi us`を同音にする)を不合格のまま維持する場合に有効化、合格とする場合は(b)を外す。比較と副作用は§4-3。
   - G5 **略語ガード**: canonical側tokenは3字以上(`ai`の代表発音は`AY1`[=eye]、`am`/`us`は文字読みvariantを持つため)。実測で効く例=`ai phone→iphone`。
   - G6 全tokenがCMU辞書収録(OOVは**判定不能=非救済**)。variantの直積が64組を超えれば判定不能。
   - **G7 (R-01訂正) 音素列はストレス記号を除いたARPAbetで、any-variant一致**。**これは既存1:1とは異なる**: 既存`homophone_arpabet_equivalent`(`er008_asr_variant_hardening_15_homophone_en.py:89-92`)は**ストレス付き文字列の集合積=ストレスまで完全一致**を要求する。連結比較はストレスを除去して比較するため、CURRENT_SPEC.md:1839(「ARPAbet音素列が完全一致」)からの**緩和=新仕様(ユーザー判断U2に含める)**。必要性の根拠: byus=`B AY1 AH0 S`、buy+us=`B AY1`+`AH1 S`はストレス除去でのみ一致し、ストレス込みでは保存データの救済が**0/4**(`measure_v2_result_01.json` V2: 変化0)。理論上の一般語(語彙3,725語中456組、`measure_v2_result_01_vocab01.json`): ストレス込みでも一致=284、**ストレス除去で初めて一致=172**(38%)。後者の全リストは`triples_review_list_01_vocab01.json`(`stress_removed_only`)に保存。
   - G8 比較範囲はspan内のみ(離れた語は結合しない)。
   - **G9 (R-03新設) canonical側がentity_likeのとき、両側とも各tokenの代表(先頭)variantのみで比較**。理由: 多語spanは`Case A`(代表発音のみ、固有名詞はtoken数不一致で必ず`resolved=False`、`hp:145-146`)を通らず、`_step_alternate_pass`の**全variant一致**(`sec:592-595`)に流れるため、固有名詞にD-2'(2026-08-28: 固有名詞は代表発音のみ)で不採用とした基準を通ってしまう。一般語は全variantのまま(推奨)。影響の計測(`measure_v2_result_01*.json`): 保存データ4,032ペアでは代表限定にしても**4/4維持**(byus=`B AY1 AH0 S`、buy=`B AY1`、us=`AH1 S`が各代表)。理論域(456組)では常に代表限定にすると救済域が**455→121**(canonical=単語側)/**173→51**(canonical=複数語側)に縮小するため、一般語まで代表限定にはしない(縮小が品質上必要という証拠がない)。判断はU1に含める。
3. 真になれば`homophone_candidate=True`(`content_word_diffs`のdictに既存キーのまま、**救済が成立したdiffに限り**追加キー`multiword_homophone: true`と監査用の生span・一致音素列を付す)。以降は既存経路(`ASR_VALIDATION_UNCERTAIN`→`_step_alternate_pass`→`HOMOPHONE_EQUIVALENT`→Primary/Secondary許容集合、retry/HR)。
4. 「不確実な判定を安易にPASSしない」: OOV/variant過多/ガード該当は従来どおりNG経路(`TRUE_CONTENT_MISMATCH`→retry)のまま。

### 4-2. 具体例(`measure_v2_01.py`/`proto_multiword_span_01.py`の実行結果。V1=G7ストレス無視・G4(a)のみ、V8=G4(b)も有効)
| canonical span | ASR span | 判定 | 理由 |
|---|---|---|---|
| `byus` | `buy us` | **新規に救済** | `B AY1`+`AH1 S`=`B AY AH S`(ストレス無視)=`byus`の`B AY1 AH0 S`。ストレス込みでは不一致(G7) |
| `byus` | `by us` | 救済済み(新規ではない) | 空白差のみ→既存の全文/span despace規則が先に吸収(DESIGN旧版の『救済』は誤り・R-12) |
| `bias` | `by us` | 新規に救済(V1/V8) | `by`は機能語・高頻度。canonicalが一般語`bias`の場合の同音扱い |
| **`bias`** | **`bi us`(`Bi-us`)** | **V1: 新規に救済 / V8: 非救済** | CMU `bi`=`B AY1`。**CURRENT_SPEC.md:454は`BAUS`/`Bi-us`を「実音声の誤発音、引き続きNG」と記録**(runtime evidence `FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01/runtime/runtime_evidence_x.json`)。V1では単独の`Bi-us`が救済されCURRENT_SPEC:454と衝突。実データの当該ペアは`byus→baus`(OOV)の別diffが残るためV1でもNGのまま(`measure_v2_result_01.json` R05)。期待ラベルは**ユーザー判断U-BI** |
| `onto` | `on to` | 救済 | 音素一致(`on`,`to`は機能語集合内) |
| `already` | `all ready` | 救済(一般語) | 音素一致 |
| `byus` | `bios` | 非救済(1:1) | `B AY1 OW0 S`≠ |
| `byus` | `buy` / `buy us an` | 非救済 | 脱落/追加(連結音素列が不一致) |
| `us` / `am` | `u s` / `a m` | 提案の対象外 | 空白差規則が先に吸収(現行でもPASS。既存の穴・U5) |
| `melos` | `mellow s` | 非救済 | OOV+G4(a)。Ledger/M1(A+)の領域 |
| `ai phone` | `iphone` | 非救済(G5) | `ai`が3字未満。ガード無しなら救済=AIを「アイ」と読む誤りを素通し |
| `Tse`(entity) | `sea`/`see`/`c` | **新規ルールの対象外・既存の穴(現行でPASS)** | 1:1。`Tse`=`T S IY1`/`S IY1`の第2variantが`sea`と一致→**現行コードで`Kristie Tse spoke first.`→`Kristie Sea spoke first.`がPASS:HOMOPHONE_EQUIVALENT**(Case A=代表のみは不成立だが、entity_likeかつhomophone_candidate=Trueなので`_step_alternate_pass`が2番目の分岐でPASS、`measure_v2_result_01.json` R03)。是正はしない(報告のみ、U5) |

### 4-3. `Bi-us`型の対策案の比較と副作用(R-02。ユーザー判断U-BIの材料。0円計測)
`measure_v2_01.py`が`span`レベルと文レベル、保存4,032ペア、理論域456組で計測(`measure_v2_result_01*.json`)。tokenize後は`Bi-us`→`['bi','us']`でハイフン情報が消えるため、**ハイフン有無による区別は`val.tokenize`後の層では不可能**(生文字列に戻る追加配線が必要になり不採用)。
| 案 | 内容 | `bias→bi us` | `byus→buy us`(実データ4件) | 理論域456組での救済数(canonical=単語/複数語) | 評価 |
|---|---|---|---|---|---|
| V1(基準) | ストレス無視・全variant・G4(a)のみ | 救済 | 4/4救済 | 455 / 173 | `Bi-us`単独が救済されCURRENT_SPEC:454と衝突 |
| V4/代表発音限定 | 全tokenを代表(先頭)variantに限定 | **救済のまま**(`bi`も`us`も代表で一致) | 4/4 | 121 / 51 | **対策にならない**(Opus案の1つは効かないと実測で判明) |
| V5 | G4を2字以下に強化(2字token全面禁止) | 非救済 | **0/4(`us`が2字のため主目的も消える)** | 173 / 173 | **不採用**(目的を損なう) |
| V6 | 2字tokenは`wordfreq`のzipf≥5.0のみ | 非救済 | 4/4 | 417 / 173 | 効くが新規依存(`wordfreq`はProduction依存でない)・閾値が恣意的 |
| **V8** | **2字tokenは閉じた機能語集合のみ** | **非救済** | **4/4** | **407 / 173**(-48) | **推奨(「不合格維持」を選ぶ場合)**: 新規依存なし、保存データでの喪失0、`us/on/to/by`等の主用途は維持 |
- 保存データへの副作用(V8): 変化4ペアのまま(`byus→buy us`)、PASS→NG 0、新規誤PASS 0。V2(ストレス込み)・V5は4ペアとも救済不能になる。
- 残る限界: V8でも`bias`⇔`by us`(`by`は機能語)は同音扱い。canonicalが一般語`bias`で実音声が「バイ・アス」と区切って読まれた場合を、音素列だけでは区別できない(=oronym問題)。ユーザーが「聴感が同じなら合格」を選ぶならV1、CURRENT_SPEC:454の方針(区切った読みはNG)を保つならV8。

### 4-4. 判定挙動の変化4点(R-04。「下流コード無改変」であって「判定挙動不変」ではない)
`measure_v2_01.py`の合成8ケース(`measure_v2_result_01.json` R04)と保存データで確認。いずれもTrialのケース表とunit testに追加する(`TRIAL_PLAN_01.md` §3-1b)。
- **(a) 数字ゲート例外の拡大**(`val:834-838`、`HOMOPHONE_MATCH_NUMBER_EXCEPTION`即PASS): `byUs has two apps.`→`Buy us has to apps.`が**TRUE_CONTENT_MISMATCH→PASS**。数字(two→to)の同音扱いは既存の1:1規則だが、n:m同音diffと共存してもPASSするようになる。1:1の`Bias has two apps.`→`Byus has to apps.`は現行でもPASS(対照)。
- **(b) M1のSecondary矛盾拒否が働かなくなる**(`er006_m1_multi_candidate_01.py:511`): Secondary転写`Melos met buy us today.`の分類が**TRUE_CONTENT_MISMATCH→ASR_VALIDATION_UNCERTAIN**に変わるため、`m1:511`の矛盾拒否(TRUE_CONTENT_MISMATCH/TTS_FAILURE)が発動しない。M1が動くのはCMU未収録の固有名詞+Secondaryに同時にn:m同音diffがある稀な組合せ(保存データ0件)。
- **(c) connected-speech/F1経路の迂回**(`val:1119-1162`): `byus→buy us`が`non_entity_diffs`から外れる。他の内容語差が残る場合は従来どおり評価され変化なし(合成2例: `stuff→tough`、`uphill→a pill`はTRUE_CONTENT_MISMATCHのまま)。固有名詞差が混在する場合(`Melos met byUs today.`→`Mellow s met buy us today.`)は**TRUE_CONTENT_MISMATCH→ASR_VALIDATION_UNCERTAIN**(`should_retry=False`、最終はNOT_PASS)となり、blind retryがHR/cascade側へ寄る(安全側の変化だが挙動は変わる)。理論上のPASS→NGは「以前connected-speechでACCEPTされた組合せがUNCERTAIN経路に移りalternate PASSが不成立」の場合だが、保存4,032ペア・合成8例で**PASS→NG 0**。
- **(d) F1残差判定は1:1限定のまま**(`val:1008`、`len(c)!=1 or len(a)!=1`→`content`扱い): F1が説明しきれない残差にn:m同音が含まれる場合は新ルールが効かず従来どおりTRUE_CONTENT_MISMATCH(安全側の漏れ)。

### 4-5. 対応不要の安全側の漏れ(R-13)
2:2 span(oronym)は対象外(G1)/F1残差の1:1限定(4-4 d)/固有名詞diffが混在する場合は`Case A`不成立でUNCERTAINのまま救済されない(4-4 c)/ASR側のOOV綴り(`Baias/BAYAS/FAYAS`)/CMU未収録の名前(`Melos`)。いずれも誤PASSではなく「救済しない」側の漏れで、現行から悪化せず、予防価値の範囲では対応不要。

### 4-6. 実装位置と配線(提案のみ)
- 純関数: `er008_asr_variant_hardening_15_homophone_en.py`に追加(既存`_phone_variants`を再利用)。呼出: `val.protected_check`の1箇所。Family X/Z/Y共通で自動反映。
- **audit key(R-09)**: `content_word_diffs`の各dictのkey集合は`er006_multi_diff_judge_fix_test_01.py:153`が完全一致で固定している。**追加keyは「救済が成立したdiffにのみ付ける(条件付き)」を推奨**: 既存diffのkey集合は不変でこのtestの改訂が不要、新ルールの救済diffを検証する新testを追加する。常に付ける案はこのtestと下流serialization(telemetry/HR package)の改訂が必要で不採用。監査用に生span(`canonical_span`/`asr_span`)と一致音素列(`matched_phonemes`)を記録する。
- 段階: (1)Trial(DEV専用、`measure_v2_01.py`方式のメモリ上patch): Productionを編集しない。(2)VALIDATED後・ユーザー採用後にProduction実装。11-7限定例外(flag)は使わない(Trial段階で隔離が完結し、採用前にProductionへコードを入れないため)。

## 5. #133との統合方針(v2)

1. **統合の骨子**: #133の目的「正しい発音をシステムが持つ」を「期待発音源(Expected Pronunciation Source)」という概念に整理し、L1(判定)が参照する期待発音の出所を階層化する方向は維持する(①CMU[現行] → ②Ledger EN entry[根拠付き、M1 C2] → ③JA公式読み[J7、候補提示のみ])。**ただし②③は今回のFixに含めない**。
2. **L1はL2を待たない**: ①だけで閉じる(byUsの`buy us`はCMU `byus`=`bias`同音で救済される)。これは「期待発音=CMU綴り発音」という既存の前提に乗っているだけで、byUsの公式発音を確認したわけではない。この限界は全文書で明示する。
3. **L2(#133)は今回のFix範囲外(R-08)**: UDR #133の選択肢では**(イ)現状維持を土台にL1(案A)を追加**する形を推奨し、(ア)(ウ)は採らない。B2(反応的調査・negative cache)は、CMU辞書外の名前でHRが増える実測が出た場合のオプションとして**#133判断後の別計画**に回す(§6は骨子のみ。Tier表・TTL・T2b・P2は確定範囲から外した)。
4. **未解決のままの前提を隠さない**: byUsの公式EN発音は未確認(PNEP K1)。J7(権利者公式の日本語読み「バイアス」を根拠にしてよいか)はユーザー判断で、L1の成立には影響しない。

## 6. 固有名詞の正しい発音を取得する仕組み(骨子のみ。#133判断後の別計画へ分離・R-08)

v1では情報源Tier表(T0〜T4)、negative cacheのTTL(90日)、T2b(Wikipedia/Wiktionary/Wikidata発音欄)、P2サブTrialまで詳細化したが、価値が不確定(#133は未回答、実需要はCMU辞書外の外国由来名のみで保存データ上は少数)なため、**今回の確定範囲から外す**。次の骨子だけ残す(正本は別計画で確定する)。
- 方向性: 根拠付き情報源のみをLedgerへ登録(AIの推測は根拠にしない、PNEP V1'-V6を再利用)。毎回Web検索せず、確認できた発音/確認できなかった事実をLedger自体にキャッシュして再利用する。CMU収録語は調査しない。
- 範囲外(別計画): 具体的なTier表と優先順位、negative cacheのTTL・保存形式、決定的な無料情報源(T2b)の有効性検証、web_search調査の費用実測。
- byUsの確定: AI単独では確定しない。J7(ユーザー判断)に依存。J7=認める→`B AY AH S`系を期待発音として確定、認めない→UNCONFIRMEDのまま(L1は影響を受けない)。

## 7. ASR選定への依存管理(ユーザー§3、v2)

| 項目 | 依存 | 構成が変わっても成立するか | 再評価が必要な点 |
|---|---|---|---|
| 案Aの判定規則(純関数)、ガード、unit test、オフライン再適用 | なし | **成立** | 新Primary/Secondaryの転写で再適用し、判定変化の件数と内訳を再測定(API 0〜低額) |
| 効果量(どのエンジンが多語化を起こすか) | **あり** | 成立しない場合がある | Azure(Secondary)が多語化(`Buy Us`/`by us`)の主因だった(実転写6ペア[全て1記事run_byus_01]: Secondary 4 / Primary 2)。構成が変われば発生頻度が変わる→3方式比較Trialの転写キャッシュを再適用して再測定 |
| 表記の癖(ハイフン`Bi-us`・音節区切り・大文字小文字) | **あり** | エンジンごとに異なる | 新構成でのハイフン/区切りの出方を層Aで集計(`TRIAL_PLAN_01.md` §8) |
| Secondaryの許容判定(`sec:993-1002`) | 構成の役割定義に依存 | 規則は構成非依存 | 新Secondaryで`secondary_accept`経路が新ルールを通ること |
| 供給先(Phrase List=Azure固有、promptの綴り誘導=K5型) | **あり** | Azureが外れれば無効 | 別計画(#133)。PL/promptで綴りが誘導された転写は独立証拠として使わない |
| 有料Trial(designed audio × 新Primary/Secondary) | **あり** | ASR確定後に実施 | ASR確定前は有料部分を開始しない(ユーザー要件) |

3方式ASR比較Trial(`docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/`)の設定・評価・進行は変更しない。転写キャッシュは読み取り専用で再利用する(再利用可否は完了後に確認)。

## 8. QCD概算(v2。詳細は`TRIAL_PLAN_01.md` §7)

- 実装(案A、Production): 純関数＋条件1行＋test約20〜30本(4-4の4点を含む)。実行時API 0。
- 量産単価: 案Aは実行時 0円/記事。期待値は再試行削減(byUs型1件約5円＋10分)×発生率(保存4,032ペア中4=0.10%、全て1記事由来)で記事あたり0〜0.1円オーダーの**微減**。価値は予防が中心。B1は11〜16円/記事の悪化見込み(非推奨)、B2は別計画。
- 納期: オフライン検証は3方式ASR比較の完了を待たず進められる。有料Trialは**約18〜28円・数時間規模、Cap JPY50**(`TRIAL_PLAN_01.md` §7、v1の25〜60円/Cap100から縮小・R-06)。
- 不確実性: 発生率は保存データ上の値(Azureが主因)で、新Primary/Secondaryで変わり得る。


---
## v3 Fix(2026-10-22ユーザー判断反映、委任_03。Status=`PLAN_FIXED_WAITING_ASR_SELECTION`。上のv2本文は履歴として保持し、矛盾時は本節が優先)
出典: `docs/pm/delegation_log/2026-10-22_PNMH-PLAN-FIX-AND-ASR-PASS-CONDITION-AUDIT-01_USER.md` §2。承認されたのは『計画v2の基本方針とTrial計画』であり、Production採用ではない(VALIDATED≠APPROVED_FOR_PRODUCTION≠PRODUCTION_WIRED)。

- **案Aの確定仕様(Trial計画として)**: 1語⇔連続2〜3語・ストレス無視・CMU全variant・ガードG1〜G9+**V8(2字tokenは閉じた機能語集合のみ=`Bi-us`型NG維持)**・entity_likeは代表発音のみ。試作=`proto_multiword_span_01.py`の`multiword_span_equivalent_v3`(v2既定の`multiword_span_equivalent`は不変)。
- **§4-3の『U-BIで決める』は決着**: ユーザーは『現行仕様に従いNG維持』を選択→V8採用(B0)。残る限界=`bias`⇔`by us`(機能語by)は救済される。
- **#133/L2**: 『辞書外・未解決の実際の不一致が発生した場合に調査する方式』(B2縮小=反応的調査)を**継続検討の候補**として残す。全固有名詞を毎回調査する方式(B1)は不採用(ユーザー判断)。#133のStatusは不変、未承認事項は正式採用しない。
- **リスク欄**: 現行の`Bias`救済と案Aの`buy us`救済は、CMU辞書が姓等として収録する`byus`(=`B AY1 AH0 S`)の綴り依存。ブランドの公式英語発音の確認ではない。『同綴りの別人名があるだけでは公式発音は確定しない』ため、byUsの英語発音は**未確定**(J7未回答)。
