# byUs 発音同等性判定の救済失敗 原因調査 01

管理ID: FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_07(調査のみ・API 0・費用JPY0・コード/仕様/Ledger/成果物 無変更)
ユーザー指示原文: `docs/pm/delegation_log/2026-10-21_FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01_BYUS-EQUIVALENCE_USER.md`
対象: Production run `run_byus_01`(Family X、Advanced=b1b)Full Story 第1部・第3部。

略称: `B1B_RES`=`er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/b1b/audit/tts_generation_results.json`、tel=`er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl`、`val`=`er006_preprod_hardening_01_validation.py`、`sec`=`er006_secondary_asr_01.py`、`hp`=`er008_asr_variant_hardening_15_homophone_en.py`、`m1`=`er006_m1_multi_candidate_01.py`、`uj`=`er078_asr_unified_judge_01.py`。

**コード行番号はすべて`git show HEAD:`基準(HEAD=c4ca8d830時点)。** 作業treeに`sec`の差分(Ledger隔離対応の別agent変更、L358-380付近のみ)があるが、本調査の経路(L78-111・L470-1030の判定部)には無関係。

再現方法: HEADのpy一式を`git archive`で一時dirへ展開し、cwdだけ実リポジトリ(データ読取り用)にして`classify_asr_match`/`_step_alternate_pass`/`m1_multi_candidate_judge`/`pronouncing`を**オフライン実行**(API 0、telemetry書込みはno-op化、リポジトリ書込み0)。スクリプトはscratchpad内。
**run当時のコード(=01fdd3a2c^、複数差分是正の直前)に保存済み転写を再適用すると、記録された6attemptの全判定ラベルが一致**(再現性確認済み)。run=2026-10-21 13:16-13:40 JST、是正commit 01fdd3a2c=同日18:29 JST(run後)。

## 1. `ByUs → buy us / by us` の実測結果

原稿(canonical)は両partとも小文字始まり`byUs`(例 part1「LINE Manga has launched byUs, an AI serv…」、`It is pronounced "bias."`も含む)。ASR出力と判定(B1B_RES.segments.*.attempts_log[].asr_judgement、再現値を併記):

| part/att | 生成(JST) | Primary(OpenAI gpt-4o-mini-transcribe)のbyUs箇所 | Secondary(Azure、Phrase List空)のbyUs箇所 | 記録された判定 |
|---|---|---|---|---|
| p1/1 | 13:16 | **Bias**(+`story-making→storymaking`で別差分) | **`Buy Us`**(+storymaking・"the"脱落) | NG_BOTH secondary_not_accepted |
| p1/2 | 13:16 | BIOS(`pronounced bias`もBIOS) | Bias(+LINE→Lion・語脱落) | NG_BOTH |
| p1/3 | 13:27 | Byus(`pronounced`側のみ、byUs本体は一致) | 未呼出 | PASS primary_pass(`cmu_alternate`、HOMOPHONE_EQUIVALENT)=**採用** |
| p3/1 | 13:28 | Baias | **`by us`**(+was→with, and脱落, a way→away) | NG_BOTH |
| p3/2 | 13:29 | FAYAS(+`two works→20 works`) | 未呼出 | NG_PROTECTED p1_value_diff |
| p3/3 | 13:39 | BAYAS | bias(文境界崩れあり) | PASS_WITH_WARNING secondary_confirmed(Azureの`bias`で救済)=**採用** |

- `Buy Us`はp1/1のAzure(Secondary)だけ、`by us`はp3/1のAzure(Secondary)だけに出現。**Primary(OpenAI)が`buy us`/`by us`と認識した例は0件**(Primaryは Bias / BIOS / Byus / Baias / FAYAS / BAYAS)。
- tel行(tel:9744-9748=p1 att1 Pri/Sec・att2 Pri/Sec・att3 Pri、9750-9754=p3 att1 Pri/Sec・att2 Pri・att3 Pri/Sec): `content_word`(9744,9745,9746,9750,9751,9753)、`protected_number`(9752)、`homophone_only`(9748,9754)。
- 救済結果: **最終的にはどちらのpartも救済されたが「別attemptの別ASR結果」で**(p1=att3 Primary`Byus`、p3=att3 Azure`bias`)。`Buy Us`/`by us`の転写自体が救済された例は0件。再試行は両partで追加2回+cooldown 10分x2(`ADV_FULLSTORY_RETRY_ANALYSIS_01.md`/委任_06の実測 10.31円/本+20分、再利用)。
- 当該転写をrun当時コードへ再適用: `byus→buy us`は`TRUE_CONTENT_MISMATCH`(content_word diff=[byus→buy us]、entity_like=False、homophone_candidate=False)。p3/1の`by us`は`byus→us`(後述)で同`TRUE_CONTENT_MISMATCH`。

## 2. 既存Validatorで救済されなかった直接原因

(2-1) **`buy us`(2語化)**: `protected_check`のhomophone_candidateは「canon_content・asr_contentがともに**1語**」の置換のみ(`val:750` `if len(canon_content)==1 and len(asr_content)==1`)。`byus→[buy, us]`は1:2なのでFalse。
結果は`non_entity_diffs`(`val:1125`)に入り`TRUE_CONTENT_MISMATCH`(retry対象)。この分類だと以降の救済層がすべて入口で除外される:
- CMU同音(`sec:566 _step_alternate_pass`)・Case A(`sec:551`)は`ASR_VALIDATION_UNCERTAIN`の時だけ(`sec:318 is_homophone_candidate_mismatch`、`sec:938 cascade_eligible`)。
- M1は入口で`BASE_CLASSIFICATION_NOT_UNCERTAIN`(`m1:425 _entry_gate`、`m1:38`)。実測 M1: accepted=False reason=BASE_CLASSIFICATION_NOT_UNCERTAIN。
- Connected Speech(B1`classify_connected_speech`)は実測 `UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING`(f1_residualに`byUs→Buy,Us`が残る=連結発音規則に該当しない)。CS Equivalence層は`NO_DELETION_SHAPED_DIFF`(脱落形でないため対象外)。
- EN semantic equivalence(`er021`、Tier1は数値・略語専用/Tier3は規則複数・固有名詞corroboration)は`sub_reason=content_word`(tel:9745)で、救済層としては発動せずtelemetry記録のみ。

(2-2) **`by us`**: `by`は`_STOPWORDS`(`val:599`)に含まれ、内容語比較から除かれる。run当時は canon_content=[byus] vs asr_content=[us] で`byus→us`となり内容語差(`TRUE_CONTENT_MISMATCH`、tel:9751)。単独diffなら全文`despaced()`規則(`val:1043`、"byus"=="byus")でNORMALIZED_MATCHになるが、p3/1は他diff(and脱落・was→with・a way→away)が共存して全文規則が効かなかった。
**HEAD(複数差分是正01fdd3a2c後)では** span単位のdespace一致(`val:654 _is_compound_spacing_only_span`)で`by us`は内容語差から外れる。それでも**p3/1のAzure転写はHEADで`ASR_VALIDATION_UNCERTAIN`(low_ratio, ratio=0.9718<0.98)のままPASSしない**: 残差は`and`脱落・`was→with`(stopwordで内容語差0だが、ratio計算は生token列)。`by us→byUs`に置換した反実仮想は`HIGH_SIMILARITY_SAFE`(0.9811)=span吸収後もratioは分かち書き差の分だけ損なわれる(下記6末尾)。

(2-3) Primary側の同種失敗も同じ構造: p1/1 Primary`Bias`は単独ならCMU同音で救えるが、`story making→storymaking`が共存して`TRUE_CONTENT_MISMATCH`にされた(承認済み仕様の**不具合**、HEADで是正済み。HEADで再適用するとp1/1 PrimaryはHOMOPHONE_EQUIVALENTでPASS=実測)。

(2-4) 救えない綴り: `BIOS`(CMU `B AY1 OW0 S`=bias `B AY1 AH0 S`と別発音)=**救済すべきでないケース**。`Baias/BAYAS/FAYAS`(CMU辞書外、`pronouncing`で空)は`homophone_arpabet_equivalent`が`None`(判定不能、`hp:73-100`)=推測でPASSさせない設計どおり。

## 3. 原因が生じた根本原因

1. **正解発音をValidatorは持っていない。** `byUs`の「正解発音」はどこにも登録されておらず、Validatorが使うのは(i)canonical綴り`byus`をCMU辞書(`pronouncing`)で引いた値(`B AY1 AH0 S`、実測。CMUの`byus`は別語[姓等]の収録で、ブランドの公式発音ではない)と、(ii)ASR側綴りのCMU値との**綴り同士のARPAbet一致**だけ(`hp:73-92`)。`Bias`/`Byus`/`bias`は「CMU上たまたま`byus`と一致する」ために救済でき、公式発音に基づく判定ではない。
2. **Ledger/Phrase List/TTSヒントへの供給が空。** Ledgerのbyus entryはJA用のみ(`ja_reading_katakana=バイアス`、`pronunciation_hint=""`・`expected_pronunciation_ipa=""`・`sources=[]`、`git show HEAD:er006_output/pronunciation_ledger_01/ledger.json`で確認、updated_at=2026-10-21T13:11:24)。`get_hint_for_text`はhint空entryを返さず(`er006_pronunciation_ledger_01.py:164-206`、委任_06既出)、AzureのPhrase Listは全12呼出で`phrase_list_size=0`。Azureが`byUs`を一般語列`Buy Us`/`by us`に分割して書く余地が残った。
3. **多語→1語の同音比較は、承認済み仕様の範囲外。** CURRENT_SPEC.md:1839(英語homophone自動PASS条件)は「canonical/ASRの**単一語置換差**について…ARPAbet完全一致」と定義。実装(`val:750`、`hp`)もこれに一致。Case A(CURRENT_SPEC.md:1837)も語数一致が前提(`hp:138-148 entity_span_arpabet_match`は語数不一致なら`resolved=False`)。
4. **固有名詞扱い(entity_like)にもならない。** `capitalized_flags`(`val:467`)は大文字始まりの語だけ。`byUs`は小文字始まりでentity_like=False。仮に`ByUs`なら(反実仮想・実測)`byus→buy us`は`ASR_VALIDATION_UNCERTAIN`(entity_like=True)になるがCase Aは語数不一致で`PROPER_NOUN_ENTITY_ARPABET_CONFIRMED`にならずHuman Review行き(`Bias`側だけがPROPER_NOUN_ENTITY_ARPABET_CONFIRMEDで通る)。Ledger登録語のentity_like化(`LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATION=False`、`val:536`)は2026-09-28ユーザー判断でNOT_ADOPTED。
5. **Primary/Secondaryは統合されず独立評価。** `uj`の状態機械は、Primary NGならSecondary(Azure)を1回呼び、**Secondary転写を原稿と単独で照合**して許容集合(`sec:988 _secondary_accept`=should_pass+CMU同音/Case A+M1)に入れば`PASS_WITH_WARNING`、入らなければ`NG_BOTH secondary_not_accepted`(`uj:551`)。「Primaryは`Bias`・Azureは`Buy Us`」のような転写同士の突き合わせ・投票は無い。p1/1は両者が別々の理由(storymaking差/2語化)で落ちた。
6. **run当時のコードに承認済み仕様の不具合が1件**(上記2-3、`story-making`)。本調査より前に是正済み(commit 01fdd3a2c、CURRENT_SPEC.md:452)。

## 4. 既存のどの仕組みが機能し/しなかったか

| 仕組み | byUs事案での挙動 |
|---|---|
| CMU同音(homophone_candidate / `cmu_alternate` / HOMOPHONE_EQUIVALENT) | **機能**: `Bias`/`Byus`/`bias`(1語:1語)を救済。p1/3採用(Primary)、p3/3採用(Azure)の根拠。 |
| 複数差分時の個別許容(01fdd3a2c) | run後に追加。HEADでp1/1 Primaryを救済、`by us`をspan単位で吸収。run当時は未適用(run=13時台、是正=18:29)。 |
| CMU Case A(固有名詞) | 不発(entity_like=False。仮にTrueでも語数不一致で不成立)。 |
| M1(Ledger/CMU複数候補) | 不発(入口が`ASR_VALIDATION_UNCERTAIN`限定。Ledger IPA候補[C2]はCMU未収録語のみ、byusはCMU収録かつLedgerにIPAなし)。実測: `BASE_CLASSIFICATION_NOT_UNCERTAIN`/`F1_RESIDUAL_CONTENT`。 |
| Connected Speech(B1)/CS Equivalence/Semantic Equivalence(Tier1/Tier3) | 不発(連結発音規則に該当せず/脱落形でない/数値・規則複数でない)。telは`content_word`記録のみ。 |
| 統一judge(er078) | 仕様どおり動作。独立判定のため転写の収束は救済根拠にしない(CURRENT_SPEC.md:1837「ASR consensus ≠ pronunciation verification」)。 |
| Ledger EN hint / Phrase List(重み2.0) | **供給が空のため未使用**(重み2.0の実行経路は`sec:106-111 if phrases:`内のみ。空なら`setWeight`未実行)。 |

**Phrase List空と重み2.0の切り分け**: 判定ロジック(`classify_asr_match`/`_step_alternate_pass`/M1/`uj`)は転写テキストと原稿だけを入力とし、Phrase Listを参照しない(Phrase Listは`sec:78-111`でAzure呼出の入力、およびキャッシュキー`_phrase_hash`としてのみ現れる)。Phrase List空が影響したのは**Azureが`Buy Us`/`by us`と書いた要因**(判定の入力側)であり、判定ロジックの条件ではない。PNEP Trial(`TRIAL_RESULT_01.md`§3)でPhrase Listに`byUs`綴りを入れた腕Mは、多語化3例中1例のみ`byUs`に単語化(NG→PASS)、残り2例(`by us`)は不変、`Lion Manga`→`LINE Manga`の副作用も1例。**重み2.0は配線済み・正常**(Family Z実測+PNEP `dgi.Items`/`bias=[2.0]`一致)で、本事案は「それに渡す登録語が無かった」だけ。

## 5. 既存仕様の範囲で解決できるか(分類)

| 項目 | 分類(ユーザー§3の5区分) | 根拠 |
|---|---|---|
| `story-making→storymaking`による同音救済の阻害 | 承認済み仕様の不具合(実装漏れ相当、是正済み) | CURRENT_SPEC.md:452、commit 01fdd3a2c。HEAD再適用でp1/1 Primary=HOMOPHONE_EQUIVALENT |
| `Buy Us`(2語化)→`byUs`同音 | **既存仕様で未対応のケース**(新仕様) | CURRENT_SPEC.md:1839は単一語置換差。多語→1語は定義外。判定基準の拡張に当たる |
| `by us`のspan吸収(HEAD) | 実装済み機構の発動条件(是正済み)。ratioが残る | 上記2-2、6末尾 |
| byUsのEN正解発音(Ledger hint/Phrase List/TTSヒント) | **発音情報の供給不足** | Ledger hint空。PNEP Trial K1=`UNCONFIRMED_SAFE`(英語公式発音なし、公式は日本語「バイアス」のみ)=新仕様候補(OPEN-434、USER_DECISION_REQUIRED) |
| 小文字始まり造語がentity_like=False | 実装済み機構の発動条件(仕様どおり) | `val:467`。Ledger登録語のentity_like化はNOT_ADOPTED(2026-09-28) |
| `BIOS`・`Baias/BAYAS/FAYAS` | **実際には発音が異なる/救済すべきでない(または判定不能)ケース** | BIOS=CMU別発音。Baias等は辞書外→推測PASS禁止 |

「表記が異なるだけで発音が同じなら救済対象/正しい発音が未確定なら推測でPASSさせない」(ユーザー原文§3)に照らした**事実整理**(判断はユーザー): byUsの英語正解発音は**未確定**(公式は日本語読み「バイアス」、英語情報源にbyUsの発音記載なし[PNEP K1/j7_evidence])。現行の`Bias`救済は「CMUの`byus`綴りがたまたま`bias`と同音」に依拠しており、公式発音の確認ではない。原稿自体は`It is pronounced "bias."`(canonical内、Writer出力)とbiasを明示しているが、これは読み登録・Phrase List・Validatorのいずれにも接続されていない(委任_06)。ASRの綴り揺れ(BIOS/Baias/BAYAS/FAYAS)は、TTSが`byUs`の読みを揺らした可能性とASR側の綴り選択の可能性があり、**音声未試聴のため切り分け不能**。

## 6. 同種の固有名詞・造語への影響

- **telemetry実測(tel全9,803行、canonical中のCamelCase/小文字始まり語別)**: `byUs`=計56行(content_word 26 / homophone_only 18 / protected_number 9 / low_ratio 3)、`iCapital`(小文字始まり)=entity_only 3・content_word 3、`FamilyMart`=entity_only 15・content_word 3、`McCartney`=entity_only 15、`ByUs`(大文字始まり)=entity_only 2。複数run・複数attempt・Primary/Secondary合算で、ユニーク事象数ではない。
- **多語化の一般性(オフライン計測、tel中の非PASS 9,622行)**: 「canonical 1語→ASR 2-3語」の置換spanはユニーク27種。うち連結CMU発音がcanonicalのCMU発音と一致する(ストレス無視)のは6種(`byus→buy us`, `byus→by us`, `onto→on to`, `us→u s`, `am→a m`, `ai→a i`)。辞書外(None)18種(`melos→mellow s`, `familymart→family mart`, `icapital→i capital`, `altuzarra→also zara`等=連結同音比較では救えない)、不一致3種(`us→u k`, `qualitative→qual of`, `uphill→a pill`)。
- 影響する条件: (i)小文字始まり/CamelCase造語・ブランド名(entity_like=False)、(ii)Azureが一般語列に分割する名前、(iii)Ledger EN hintが空。大文字始まり固有名詞はCase Aに乗るが、多語化すると語数不一致で同様に落ちる。
- 付随(不具合候補、Fable判断): span吸収後もratio計算は生token列のため、分かち書き差の分だけratioが低下する(p3/1で`by us→byUs`置換のみで0.9718→0.9811)。全文`despaced()`規則との整合性の観点で不具合かは未判定。

## 7. 最小是正案(提案のみ・実装なし)

| 案 | 内容 | 既存仕様内/新仕様 | 変更箇所 | 品質(誤PASS) | 速度 | 量産単価 | 再試行削減見込み |
|---|---|---|---|---|---|---|---|
| (a) 多語→1語の連結同音比較 | `1 canon語 vs 2-3 ASR語`の置換spanで、ASR語のCMU発音を連結(**ストレス記号無視**: `buy+us`=`B AY1 + AH1 S`はstress付きでは`byus B AY1 AH0 S`と不一致、無視すれば一致)しcanonicalのCMU発音と一致する場合のみ`homophone_candidate`相当とする | **新仕様**(判定基準の拡張、CURRENT_SPEC.md:1839「単一語置換差」の拡張。ユーザー承認+Opusレビュー条件要) | `val:750`周辺(1:1条件の拡張)+`hp`に連結比較関数。DefaultOffIsolation型で隔離可 | 誤PASS増は小の見込みだが要ガード: 実測27種中の一致6種のうち`us→u s`/`am→a m`/`ai→a i`は文字読みで誤PASS候補→各語2字以上+canonical語3字以上等のガードで`byus`系のみ残る(N小、追加測定要)。CMU辞書外(18種)は救えない | 即時PASS(追加ASR・TTS不要) | 0〜微減 | PNEP J3: 反実仮想3例中2例PASS。ただしp1/1は是正済みで救済済、p3/1は`by us`でもratio/他差分で未救済のため効果は限定的 |
| (b) EN発音のLedger供給(PNEP) | byUs等のEN発音(根拠付き)をLedger登録→Phrase List(重み2.0)/TTSヒント/M1候補へ | **新仕様**(OPEN-434、承認前) | PNEP設計参照 | 公式発音未確定のbyUsは登録0(K1=UNCONFIRMED_SAFE)。J7(日本語公式読み「バイアス」→bias)の可否はユーザー判断 | 検出は軽量 | 研究費が登録失敗でも発生(PNEP: 約5.4円/名、byUs型は成功しにくい) | 腕Mで`Buy Us`の1/3のみ単語化(限定的) |
| (c) 原稿側の扱い(Writer) | CamelCase造語は原稿で読みを示す(`It is pronounced "bias."`は既にある)/読みが一意なら表記を変える等 | **原稿仕様**(Writer/Prompt原則、承認事項) | Writerプロンプト | 判定基準は不変。発音の曖昧さを減らす方向 | 生成のみ | 影響小 | TTS発音揺れ(BIOS/BAYAS等)低減の見込み。効果は未測定 |
| (d) 分かち書き差のratio反映 | span吸収した差をratio計算でも吸収(despace後token列でratio計算) | 既存仕様内の不具合是正の可能性(全文despace規則との整合、Fableが11-8で判定) | `val:1033`のratio計算 | 吸収対象は既存と同一の分かち書き基準のみ、誤PASS増は小 | 即時 | 微減 | p3/1型(by us+軽微差)の一部。単独効果は小 |

**所見(採否はFable/ユーザー)**: まず(d)が不具合かをFableが判定。(a)は新仕様でユーザー判断。(b)(c)はOPEN-434/J7と同じ判断線上。byUsの正解発音確定が前提条件に近く、(a)は`byus`のCMU登録(姓等)に依拠する点も含めて許容範囲をユーザーが判断する。

## 限界
- 実音声は未試聴。TTSが実際に`bias`と発話していたか(`Baias/BAYAS`等がTTS由来か)は確認不能。API再実行は禁止のため未実施。
- tel語別集計は全run合算。27種の連結同音計測は小標本。
