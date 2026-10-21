# byUs / LINE 固有名詞・Pronunciation Ledger・Azure Phrase List・重み2.0・同音等価判定 実行証拠調査 01

管理ID: FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_06(調査のみ・API 0・費用JPY 0・Production/Ledger/Prompt/設定/音声/SSOT 無変更)
対象: Production run `run_byus_01`(Family X、Advanced=b1b)Full Story 第1部・第3部。
ユーザー指示原文: `docs/pm/delegation_log/2026-10-21_FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01_PROPER-NOUN-PHRASELIST_USER.md`
出典の略称: 結果JSON=`er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/b1b/audit/tts_generation_results.json`(以降 `B1B_RES`)、usage=同dirの`raw_usage_log.jsonl`、ledger=`er006_output/pronunciation_ledger_01/ledger.json`、telemetry=`er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl` と `er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl`。各attemptの転写は `ADV_FULLSTORY_RETRY_ANALYSIS_01.md` を再利用(再抽出せず、本書の分類再計算のみ追加)。

## 1. 比較表(ユーザー§5)

凡例: 確認済み=出典付きで実データ/実コードから確認 / 未確認=記録なし・API再実行禁止のため確認不能。

| 確認事項 | byUs | LINE |
|---|---|---|
| 固有名詞として抽出・分類 | **EN(ASR判定・TTS前resolver)側: 抽出工程なし/entity_like=False(確認済み)**。ASR validatorのentity_likeは「原文で先頭大文字の語」(`er006_preprod_hardening_01_validation.py:467-489 capitalized_flags`)+非ASCII外来語のみで、`byUs`は先頭小文字のため全attemptで`entity_like=False`(§3-3の再計算で確認)。EN resolver(`er025_entity_pronunciation_resolver_core_01.py:439-531`)は既存Ledger参照のみで新規EN固有名詞の抽出はしない。**JA側: 抽出済み(確認済み)** - telemetry `{"event":"ja_web_lookup_call","tokens":["byUs"],... "logged_at":"2026-10-21T13:11:24"}`(er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl:466) | **ASR validatorではentity_like=True(先頭大文字、確認済み: `line`→`lion` diffがentity_like=True、§3-3)**。ただしLedger未登録・resolver抽出の記録なし(telemetryに`LINE`の行なし、grep 0件で確認済み)。一般英単語のためCMU Case A比較対象(`line`=L AY1 N / `lion`=L AY1 AH0 N は不一致、確認済み) |
| Pronunciation Ledger登録 | **登録あり(JA katakana用のみ)**: `surface=byus / entity_type=ja_reading_katakana / confidence=high / updated_at=2026-10-21T13:11:24 / resolution_method=web_search / resolved_at_stage=pre_tts`(ledger.json、確認済み)。**EN用entry(pronunciation_hint/IPA付き)は無し(確認済み)** | **登録なし(確認済み: ledger.json 38件中surface=line/LINEなし)** |
| 登録された読み | `ja_reading_katakana="バイアス"`(根拠: `ja_reading_sources=[https://prtimes.jp/main/html/rd/p/000000536.000063705.html]`)。`pronunciation_hint=""`・`expected_pronunciation_ipa=""`・`sources=[]`(EN側の読み情報は空、確認済み)。参考: Writer原稿の英文に"It is pronounced bias."(canonicalに含まれるが読み登録経路には接続されていない、§3-1) | なし |
| Azure Phrase List投入 | **投入なし(確認済み)**: usageのAzure 12行すべて`phrase_list_size=0`(本件の第1部att1/att2=04:16:34/04:17:07、第3部att1/att3=04:29:04/04:39:49も0)。理由(コード): Phrase Listは`pronun_ledger.get_hint_for_text(text,min_confidence="low")`が返すentryの`canonical_spelling`で、`if entry.get("pronunciation_hint")`が真のものだけ(`er006_pronunciation_ledger_01.py:164-206`、呼出し`er003_v1_repro01_main_generate.py:~357`)。byus entryはhint空のため除外。現ledgerで全Adv segmentに`get_hint_for_text`を再計算してもPhrase Listは全segment空(本書再計算、確認済み)。Phrase Listの**具体的内容そのもの**の記録は、本件経路(full_story)では結果JSONに無い(KP経路の`cascade_steps.azure_phrase_list`のみ記録機構あり、KP2では`[]`)。内容は「サイズ0の記録」+「現ledgerからの再計算=空」で確定、内容文字列の直接ログは**未確認(full_story経路に記録機構なし)** | 投入なし(同上、確認済み) |
| Azure重み2.0の適用 | **未適用(確認済み)**。コードは`if phrases:`の内側でのみ`setWeight(2.0)`(`er006_secondary_asr_01.py:106-111`)。本runはPhrase List空のため`PhraseListGrammar`自体が未生成=`setWeight(2.0)`は**一度も実行されていない**(サイズ0記録x12が証拠)。setWeight実行の記録は本run内に存在しない | 同上(未適用、確認済み) |
| 実際のASR認識 | 第1部 Primary: att1 Bias / att2 BIOS(`pronounced bias`もBIOS) / att3 Byus(`pronounced`部のみ、byUs本体は一致)。Azure: att1 Buy Us / att2 Bias。第3部 Primary: att1 Baias / att2 FAYAS / att3 BAYAS。Azure: att1 "by us" / att3 bias(救済)(結果JSON、確認済み) | Primary: 全attemptで正しく`LINE Manga`。Azure: 第1部att2のみ`Lion Manga`(att1・att3はLine Manga)。第3部本文にLINEなし(結果JSON、確認済み) |
| 問題・原因 | §3の原因(1)(2)(3)(5)。重み2.0は渡す語が空だったため未実行(原因4=原因3の帰結)。TTS発音(原因6)は**未確認**(音声未試聴・ASR/TTS再実行禁止) | リトライへの寄与=**0**(Lionは第1部att2のAzure(secondary)にのみ出現、同attemptはPrimaryでBIOSにより既にNG) |

## 2. ユーザー§5の1〜5(要約)

1. **既存の固有名詞対策は仕様どおり機能していたか**: 「機構自体は仕様どおり動いた」点は確認済み(CMU同音判定は`byus`と`bias`をB AY1 AH0 Sで同音と判定、第1部att3のPrimary PASSはこの機構による)。一方「byUsに効くべき対策が本runで届いていない」ことも確認済み: (a)EN用Ledger entryが無く、Phrase List・TTS発音ヒント(`hints_applied=false`x全segment)とも空、(b)ASR validatorの固有名詞判定(entity_like)は先頭大文字ヒューリスティックでbyUsに効かない、(c)Ledger登録済み固有名詞をentity_likeに使う経路は意図的にOFF(`LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATION=False`、validation.py:525、2026-09-28ユーザー判断でDEFERRED/NOT_ADOPTED)。これらは**承認済み仕様どおりの挙動**で、仕様逸脱ではない(逸脱の可能性があるのは§3-3の`story-making`token差のみ)。
2. **重み2.0は適用されたか**: **されていない**。Phrase Listが空のため`setWeight(2.0)`に到達していない(usage Azure 12/12行`phrase_list_size=0`)。定数2.0とその実行経路の正しさ(Family Z実測 `docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01/wire_evidence_prod_01.json`)とは別問題で、「設定が効かなかった」のではなく「設定する対象語が渡されなかった」。Phrase Listに"byUs"が入っていれば認識が変わったかは**未確認**(新Trialなしでは検証不能)。
3. **なぜ解決できず再試行に至ったか**: byUs起因の不一致は、既存の同音等価で救える形(1語対1語かつCMU一致: Bias/Byus/第3部att3のAzure bias)と救えない形に割れた。救えない形: ①`Buy Us`/`by us`(2語化。`by`はstopwordで除去され`us`対`byus`になる/多語→1語の同音比較は未実装)、②`BIOS`(CMU上別発音B AY1 OW0 S)、③`Baias/BAYAS/FAYAS`(CMU辞書外→判定不能None→同音扱い不可)。加えて**byUs以外の原因**: 第1部att1はbyUs→Biasが同音で救えるのに`story-making`→`storymaking`のtoken差が同時にあり`TRUE_CONTENT_MISMATCH`(§3-3、再現済み)。第3部att2は`two works`→`20 works`(数値protected、byUs無関係)。
4. **既存仕様内で是正可能か**: (a)`story-making`→`storymaking`の分類不整合は、承認済み仕様(ハイフン境界の対称正規化=OPEN-121、CURRENT_SPEC.md:411-446)に対する**不具合の可能性が高い**(単独では`NORMALIZED_MATCH`で通るのに、他diffが1つでもあるとtoken比較で漏れる、§3-3の最小再現)。本委任の範囲外のため是正は未実施。既存仕様内の不具合是正としてFable判断で委任可能(PM_GOVERNANCE 11-8)。(b)byUsのEN読み登録、(c)多語→1語の同音等価、(d)Ledger登録語のentity_like化は**新仕様/Gate緩和**で、ユーザー判断が必要(判断候補、§5)。
5. **削減見込み**: 実測usage(Standard単価pricing_snapshot.json・160円/USD): 第1部att2+att3=5.16円、第3部att2+att3=5.14円、**計10.31円/本 + cooldown 10分x2=20分**。(a)の是正だけで確実に削減できるのは第1部の2試行(5.16円+10分)。第3部は(b)(c)が実現してもatt1の`Baias`が救えるかは未確認(辞書外)、att2は別原因(数値)なので確定削減は無し(上限として+5.14円+10分、未確認)。

## 3. 原因の所在(1〜6)と証拠

### 3-1. (1)固有名詞の抽出・分類 - 該当(部分)
- EN側: TTS前resolverは既存Ledgerのcache lookupのみ(`er025_entity_pronunciation_resolver_core_01.py:461-531`)。新規EN固有名詞を事前に抽出・調査する工程は存在しない(新規は「ASR不一致後のcascade reactive lookup」でのみ`cascade_unresolved_entity`としてLedgerへ入る: `er006_secondary_asr_01.py:341-`)。本件はentity_like=Falseのためreactive lookupの対象にならずLedger追記なし(Ledger本体にbyUsのEN entryなし、確認済み)。
- JA側: byUsはJA pre_tts resolverで抽出されLedgerに`ja_reading_katakana`として登録(13:11:24、上表)。これがEN発音・Phrase Listに流れる経路は無い(`get_hint_for_text`は`pronunciation_hint`が空のentryを除外、ledger.py:204-205)。
- Writer原稿の "It is pronounced “bias.”" は canonical text の一部として全文比較の対象になるだけで、読み情報の登録・TTSヒント・Phrase Listの入力としては使われない(resolver/Phrase List構築のどちらにも該当処理なし、grep確認済み)。仕様どおり。
- 付随: M1(Ledgerの凍結候補による多候補受理)は「Ledgerのexpected/alternate IPAがありsources非空」が要件(`er006_secondary_asr_01.py:350-354`コメント)。byus entryはIPA/sources空のためM1も不発(adapter.layersにm1の記録なし、確認済み)。

### 3-2. (2)Pronunciation Ledgerへの読み登録 - 該当(EN読み未登録)
- ledger.json 38件のうちbyUs関連は`byus`(ja_reading_katakana)の1件のみ。ENのpronunciation_hint/IPAは空。LINEは未登録。
- 登録経路(確認済み): telemetry 466行、`resolution_method=web_search`(JA用、model gpt-5.6-sol)。

### 3-3. (5)ASR結果の同音等価判定 - 該当(複数の別要因)
本書での再計算(read-only、`classify_asr_match`を各attemptの結果JSON転写に再適用。API 0):

| part/att/ASR | content_word_diffs(canonical→asr, homophone_candidate) | 分類 | byUs単独で救えるか |
|---|---|---|---|
| 1/1 Primary | byus→bias(**H=True**), story making→storymaking(False) | TRUE_CONTENT_MISMATCH | **救える**(`storymaking`を除けば`HOMOPHONE_EQUIVALENT`、再現済み) |
| 1/1 Azure | byus→buy us(False), story making→storymaking(False) | TRUE_CONTENT_MISMATCH | 不可(多語) |
| 1/2 Primary | byus→bios, bias→bios(いずれもFalse) | TRUE_CONTENT_MISMATCH | 不可(CMU上別発音) |
| 1/2 Azure | byus→bias(H=True), s→'', story→''(Azure脱落), line→lion(entity_like=True) | TRUE_CONTENT_MISMATCH | 不可(Azure脱落+Lion) |
| 1/3 Primary | bias→byus(H=True) | UNCERTAIN→`cmu_alternate`でPASS | 採用 |
| 3/1 Primary | byus→baias(辞書外) | TRUE_CONTENT_MISMATCH | 不可(CMU辞書外=None) |
| 3/1 Azure | byus→us(`by us`の`by`がstopword除去), way→away | TRUE_CONTENT_MISMATCH | 不可 |
| 3/2 Primary | byus→fayas | NG(さらに`two`→`20`がprotected_number、telemetry 9752) | 不可(別原因) |
| 3/3 Primary | byus→bayas | TRUE_CONTENT_MISMATCH | 不可(辞書外) |
| 3/3 Azure | byus→bias(H=True) | UNCERTAIN→secondary_confirmed PASS_WITH_WARNING | 採用 |

- `byus`はCMU辞書に存在し発音は`bias`と完全一致(`B AY1 AH0 S`、`pronouncing`で確認)。ゆえにBias/Byus/biasは既存の同音機構(`homophone_arpabet_equivalent`、`er008_asr_variant_hardening_15_homophone_en.py:73-100`)で救える。第1部att3のPrimary PASSは大文字小文字/連結の正規化ではなく、この`cmu_alternate`層(`er006_secondary_asr_01.py:946`)による(B1B_RESのadapter.layers=['cmu_alternate']、確認済み)。
- **新規発見(是正候補)**: 同一テキストで`story-making`→`storymaking`は単独なら`NORMALIZED_MATCH`(diffなし)だが、他に1つでもdiffがあるとtoken比較で`story making`と`storymaking`が内容語diffになる。最小再現: canonical`A stage of story-making. It is byUs.` x ASR`A stage of storymaking. It is Bias.` → TRUE_CONTENT_MISMATCH。ASRを`story making`に変えるとHOMOPHONE_EQUIVALENT。第1部att1はこれが唯一の阻害要因で、att1でPASSできた(再計算確認済み)。
- 付随: "LINE"→"Lion": entity_like=Trueだが、Case A(CMU代表発音一致)は`line`と`lion`で不成立。今回は他の阻害要因が先にあり寄与なし。

### 3-4. (3)(4)Phrase List受け渡し・重み2.0 - 該当(渡されていない)
- コード(GitHub上でも確認可): `get_full_text_via_azure_stt_with_phrase_list(...)`は`if phrases:`内でのみPhraseListGrammarを生成して`setWeight(float(AZURE_PHRASE_LIST_WEIGHT))`(`er006_secondary_asr_01.py:106-111`、定数2.0は同:75)。全Azure呼出は`_AzureShared`経由(同:708)で同一関数、Family X/Y/Z共通(同:70-75コメント)。
- ローカル実行ログ: usage Azure 12行すべて`phrase_list_size=0`。retry/Secondary再実行(第1部att1→att2、第3部att1→att3)も同じ入力(同一ledger・同一`get_hint_for_text`)で毎回空 -> 「維持された」のではなく「全attemptで空」。
- 注: 重み付けの効果そのもの(Azure内部)は直接観測不能。確認できたのは「APIに渡した設定=Phrase List空・setWeight未実行」までで、認識精度への効果は**未確認**。

### 3-5. (6)TTS自体の発音 - 未確認
第1部att2の`BIOS`(byUsと"pronounced bias"の両方がBIOS)はTTSがそう発音した可能性とASRの誤りの可能性の双方があり、音声未試聴かつASR/TTS再実行禁止のため切り分け不能。`Baias/BAYAS/FAYAS`も同様に、TTS発音の揺れかASRの綴り選択か不明。

## 4. 削減見込み(実測usageから算出、Standard単価・160円/USD)
- 第1部: att2 TTS+ASR+Azure=3.65円、att3 TTS+ASR=1.52円(計5.16円)、cooldown 10分(att2→att3、cooldown_events)。
- 第3部: att2 TTS+ASR=1.44円、att3 TTS+ASR+Azure=3.70円(計5.14円)、cooldown 10分。
- 計10.31円/本・待ち20分。確定削減(是正案Aのみ): 第1部の5.16円+10分。上限(第3部がatt1で通ると仮定): +5.14円+10分(未確認)。
- 70円/記事セット目標に対し10.3円は約15%相当(ただしAdv Full Storyが毎回byUsのような造語を含むわけではなく、頻度は未確認)。

## 5. 是正案
- 案A(既存仕様内・不具合是正、推奨): token-levelでのhyphen→空白/結合の取りこぼし(`story making`と`storymaking`)を、全文normalized一致のときだけでなくtoken差分でも許容する(OPEN-121対称正規化の意図の完遂)。効果: 第1部att1がPASS(確定)。リスク: 他のtoken差分を誤許容しないことの回帰確認が必要。Production挙動の意味的変更を伴わない不具合是正(11-8)として委任可否はFable判断。
- 案B(新仕様候補、判断候補): 造語・Ledger JA登録語のEN読み(pronunciation_hint)をLedgerに登録しPhrase List(重み2.0)とTTS発音ヒントへ流す。効果は未確認(新Trialでのみ検証可)。既存の承認(2026-10-13「辞書未収録語は既存Pronunciation Ledgerや利用可能な発音情報から合理的な候補を取得する」、`er006_secondary_asr_01.py:350-354`コメント引用)との関係はFable判断。
- 案C(新仕様候補、判断候補): 多語化(`Buy Us`/`by us`)→1語の同音等価、`Baias/BAYAS/FAYAS`等辞書外綴りの扱い、Ledger登録語のentity_like化(`LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATION`)。誤PASS増のリスクがあり、品質Gate(固有名詞自動PASS条件 CURRENT_SPEC.md:1829)の変更に当たるためユーザー承認が必要。

## 6. 区別一覧
- GitHubコード上で確認(ローカル不要): `setWeight(2.0)`は`if phrases:`内でのみ実行(er006_secondary_asr_01.py:106-111, 75) / Phrase Listの構築元=`get_hint_for_text`でhint非空のentryの`canonical_spelling`(er006_pronunciation_ledger_01.py:164-206、er003_v1_repro01_main_generate.py:~357、er003_v1_crosslevel_audio_02_common.py:366) / entity_likeは先頭大文字+非ASCIIのみ(validation.py:467-489、525) / `byus`と`bias`のCMU一致(pronouncing辞書) / EN resolverはLedger cache専用(er025_entity_pronunciation_resolver_core_01.py:461-531)。
- ローカル実行ログでのみ確認: ledger.jsonのbyus entry(13:11:24、hint空) / usage Azure 12行`phrase_list_size=0` / 結果JSONの各attempt転写・判定・adapter.layers / telemetry 466(JA web lookup)・9744-9755(EN同音判定) / cooldown_events。
- 未確認: Phrase List内容の直接ログ(full_story経路に記録機構なし) / Phrase Listに"byUs"を入れた場合の認識変化(新Trial要) / BIOS・Baias等がTTS由来かASR由来か(音声未試聴、API禁止) / Azure内部の重み効果 / Adv Full Storyで造語が出る頻度。

## 7. 調査の範囲(再現性)
API 0・Production無変更。classify再適用は`er006_preprod_hardening_01_validation.classify_asr_match`・`er006_secondary_asr_01._step_alternate_pass`・`pronouncing`のローカル呼出のみ(ネットワークなし)。
