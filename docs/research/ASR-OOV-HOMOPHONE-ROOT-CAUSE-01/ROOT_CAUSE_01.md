# ROOT_CAUSE_01 (ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_01, 2026-10-24) 「gacha→gotcha」型の根本原因(層別)

対象run: `er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/`(Adv part3 全8テイク、Std各segment)。API実費=約8円(BUDGET_LOG_01.md)、Production変更0。証跡=本ディレクトリ(スクリプト+`work/console_*.txt`+結果JSON)。AIは耳確認できないため、各所に「証拠の種類」を明記する。

## 0. 先に結論(5行)
1. **TTSは正しく発音していた可能性が高い**(米音 /ɡɑːtʃə/=Ledgerの読みと一致、音素は gotcha と同一)。音声欠陥の証拠なし(機械証拠のみ、人の耳確認は未実施)。
2. Primary ASRの誤認は「バグ」ではなく**同音語の綴り判別不能**: 独立3エンジン(OpenAI 8/8・ローカルWhisper 8/8・Azure[PhraseListなし]6/8)が gotcha と書く。PhraseListを与えたAzureだけが全件 gacha と書く(=聞き分けではなく語彙バイアスが主)。
3. 既存の承認済み機構は「設計どおり動いて、全部が空振り」した。**最大の原因は3点の連鎖**: (i)小文字のCMU未登録語は entity_like にならず分類が TRUE_CONTENT_MISMATCH になる、(ii)Ledgerに gacha の読み(米 /ˈɡɑː.tʃə/)が既にあったのに、M1(Ledger読みを使う承認済み機構)の入口が ASR_VALIDATION_UNCERTAIN 限定で入れない、(iii)入れたとしてもM1は「正準語の期待綴りがCMUにある」場合しか音素比較できず、gacha は構造的に比較不能(OF-184「直接音素置換は範囲外・需要はtelemetryで測る」の領域)。
4. 費用は Secondary(Azure)が主因。**Secondaryは「再試行の後」ではなく毎attempt即時に発火**していた(依頼文の前提を訂正)。Azureは47〜50秒の全文を毎回送り、全文が単独で完全一致しないとNG_BOTHになるため、gacha以外の無関係なAzure誤転写(you've→you等)で多くのテイクが落ちた。
5. 副次の既存不具合1件(F1 `tokenize` が ’ を語構成文字にしない、§6)を発見。本委任では未修正。

## 1. 依頼文・先行資料の前提との差(訂正3点。Fableの判断材料)
| 依頼文/先行資料の記述 | 実測 | 根拠 |
|---|---|---|
| Secondaryは「確認」でなく「TTS再試行後」になる | **各attemptの同一ループ内で即発火**(Primary NG→Secondary 1回→両NGで次slot再生成)。part3は8attemptすべてでAzure呼出(raw log: part3 Azure 11呼出=528.9秒=23.48円。Std側含む) | CURRENT_SPEC L2818(基本フロー)、`tts_generation_results.json` full_story_part3 `asr_judgement.secondary.called=true`(記録が残る後半4attempt)、`raw_usage_log.jsonl` |
| 委任_01の3テイクは Primary=ASR_VALIDATION_UNCERTAIN(RUNTIME_EVIDENCE_01) | part3は**8テイクすべて Primary=TRUE_CONTENT_MISMATCH**(UNCERTAINは topic_intro(大文字Gacha)等の別segment) | `narration/attempts/full_story_part3_attempt{1..8}_*.json` `audio_classification` |
| Ledgerに gacha の読みは無い/使えない前提 | **Ledgerには gacha が既にあった**(entity_type=cascade_unresolved_entity、US `/ˈɡɑː.tʃə/`、UK `/ˈɡætʃ.ə/`、updated_at 2026-10-24T18:06:09=topic_intro のcascadeで作成)。part3 attempt1保存は18:15:02で、M1のOF-179「segment開始前」条件は満たす | `er006_output/pronunciation_ledger_01/ledger.json` key 4e8e014185b79c53、`m1_replay_01.py`(segment_started_at=18:10 で C2候補 [G AA CH AH]/[G AE CH AH] が凍結される。18:03にすると updated_at_not_before_segment_start で除外) |

## 2. (a) TTS音声は正しく発音されていたか
| 証拠(種類) | 結果 |
|---|---|
| 3つの独立ASRの転写(機械・間接) | OpenAI全文8/8、ローカルWhisper small(word timestamps)8/8、Azure窓(PhraseListなし)6/8 が gotcha(2/8は gacha)。PhraseList=[gacha](重み2.0、承認済み)を渡すと窓8/8が gacha。→ 音は gotcha の音素列と区別がつかない |
| 第1母音のF1/F2(LPC推定、同一wav内の基準語と比較。機械・間接、`formant_01.py`) | gacha第1母音 F2=1312〜1435Hz(8/8)。同一音声内の既知語の中央値: AA(gotcha型 /ɑ/) F2 1224〜1663、AE(gatcha型 /æ/) F2 1755〜1922。**8/8テイクで /ɑ/ 側**(att5のAA基準が1663と高めだが、gacha 1312は AE 1796 よりAAに近い)。F1も高く(794〜868)後舌低母音と整合 |
| Ledgerの出典付き読み | 米 /ˈɡɑː.tʃə/(Cambridge等、confidence=medium、evidence_tier=NAME_IN_CITED_PAGE=名称は出典ページにあるが読みの本人音声は無い) |
| g2p_en(参考) | gacha=G AE1 CH AH0(/æ/)。**Ledger・実音声(/ɑ/)と不一致**。G2Pは本件の正解読みにも合わない |

結論: TTSは米音の読み /ɡɑːtʃə/ で発音していた可能性が高い。音声側の欠陥ではなく判定側の問題。人の耳確認は未実施(現行part3はユーザー試聴承認済み=OPEN-499 CLOSED)。

## 3. (b) OpenAI Primary ASRが繰り返し gotcha にした理由
- 理由=上記のとおり**音素が同一の同音語**(CMU: gotcha=G AA1 CH AH0)。ASRは音から綴りを決められず、頻度の高い語に寄せる。再生成で音が変わっても(8テイク)結果が変わらないのはこのため。
- **ASR `prompt`(語彙ヒント)は現行Productionの本文segmentでは使われていない**(コード確認): `er006_asr_provider_routing_01.py:63-107` は prompt を受けるが、渡している呼出は英語Key Phrase系のみ(`er019_family_x_audio_production_runner_01.py:806`、`er003_v1_repro01_main_generate.py:354` の `asr_prompt` は language=="en" かつ呼出元指定時だけ)。本文系(`er003_v1_sing01_voice01_generate.py:239`、`er003_v1_sing01_news_tail_fix.py:192`、`er003_v1_crosslevel_audio_02_common.py:364`)は `routing.transcribe(out_path, language="en-US")` で prompt無し。
- ただし「promptが最有力の既存仕組み内対策」は実測で否定された(TRIAL_01_RESULT_01.md 表A): gacha窓8本に prompt='gacha' を付けて gacha になったのは 2/8(25%)。さらに**音声が実際に別語を言っているクリップへ prompt='gacha' を付けると誤って gacha と書く**(「gaycha」→gacha。prompt無しでは geisha)。過去Trial(er065 `TRIAL_REPORT_01.md` E-3: prompt付与で Mellis→`melos said` のmasking)と同じ現象。

## 4. (c) 既存機構が効かなかった理由(層別。すべて「設計どおり」で、配線漏れ・順序バグは確認されず)
| 層 | 結果 | 理由(根拠) |
|---|---|---|
| 分類 `classify_asr_match` | TRUE_CONTENT_MISMATCH(8/8) | 内容語差が entity_like でない。entity_like=「大文字始まり」(`capitalized_flags`)か「非ASCII外来語」(`loanword_flags`、`er006_preprod_hardening_01_validation.py:583`)のみ。Ledger登録語を entity_like に使う経路 A-1(a) は **`LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATION = False`(同:602付近、2026-09-28ユーザー判断 DEFERRED/NOT_ADOPTED。「量産telemetryで必要かつ安全な追加条件でfalse accept非増加の証拠が出たら再検討」)**。同形一般語ガードは canonical_spelling が大文字始まりの語しか通さず、小文字の gacha は元々通らない |
| er109(X/Z承認済み) | `incomparable`(fail-closed) | 音素源はCMUのみ。CMU未登録語は非同値(`er109_asr_orthographic_equivalence_01.py` 冒頭)。Ledgerを読まない純関数 |
| er008 `_HOMOPHONE_OVERRIDE_GROUPS` | 空 | 個別追記の口。主方式にしない設計(同ファイル:40-46)。OPEN-498案A=個別登録はユーザーが不採用 |
| PNAP/RET | 対象外 | 固有名詞(entity)専用。gacha は実体表3件に載らない |
| UKUS | 対象外 | 英米綴り固定対表 |
| **M1(Ledger C2読み。承認2026-10-13、X/Z/Y共通)** | **不発(`BASE_CLASSIFICATION_NOT_UNCERTAIN`)** | (i)入口 `_entry_gate`(`er006_m1_multi_candidate_01.py`)が分類==ASR_VALIDATION_UNCERTAIN のみ許可。(ii)入口を迂回してもM1は「ASR語の音素==正準語の**期待綴り**(plural/ed等のPattern)のCMU音素」でしか置換できない(`_enumerate_subs`:`spell_prons`)。gacha は派生形もCMUに無く `svs` が空で必ず不一致(`trial_run_e_01.py`でも入口緩和だけでは`MULTI_CANDIDATE_NO_MATCH`)。これはOF-184「直接音素置換は今回範囲外、no_match理由別telemetryで需要測定」で意図的に対象外にした領域(`docs/pm/OPUS_FINDINGS_LEDGER.md:211`、`docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEM1_ROOT_CAUSE_02_SPEC_RECONCILIATION_01.md` R8)。本件が初の実需要の実例 |
| Tier3(Secondary corroboration) | 不発 | 「規則的複数形・固有名詞の1トークン差」限定(CURRENT_SPEC L2166)。gacha は一般語扱い |
| Secondary(Azure、毎attempt発火) | 記録が残る後半4attemptのうち NG_BOTH 3、attempt8のみ採用 | Azureは PhraseList(ledger_phrases の gacha、重み2.0)で gacha を書いた。しかし**全文(47〜50秒)が単独で原稿と一致する必要があり**、gacha以外のAzure固有の誤転写で落ちた: att5=`you've→you`+`word's→words`、att6=`oh`欠落+`too→to`等、att7=`spark→dark`等、att8=`word's→words`のみ→採用(NORMALIZED_MATCH)。Primary側の差は gacha だけの回もあり、**語ごとに見れば全語がどちらかのエンジンで一致していた**が、判定は全文×エンジン単位 |
| Local Rewrite(承認済み、3NG後) | 作動 | slot3 NG後に発火(`you've felt→you have felt`。gachaとは無関係の語。本来不要だった) |
| HR Lock → Style Gate | 発生 | LR採用は人間承認が必要(OPEN-499) |

## 5. (d) 一般性(保存ASR記録、API 0)
母集団=全 `*tts_generation_results*.json`(`census_01.py`、er109 stored census と同一収集。5,681行/4,528 segment)。限界: stored_cls欠落行は率の分母から除外、OOV検出は `pronouncing` のCMU有無、固有名詞・テスト用ダミー語(`xzqwtrlk`)・非ASCII表記が混ざる。

| 区分 | segment | Primary NG attempt率 | 再試行segment率 | 最終 not OK |
|---|---|---|---|---|
| CMU未登録語を含む(全種) | 350 | 189/329=57.4% | 24.3% | 5.7% |
| 含まない | 4,178 | 675/4,391=15.4% | 11.6% | 2.7% |
| うち**小文字(固有名詞でない)のCMU未登録語**を含む | 109 | 46/137=33.6% | 22.0% | — |

- Primary NG行のうちCMU未登録語がdiff spanに関与=171/864。全spanがOOV関与(gacha型の形)=104行。ただしその大半は固有名詞(Framton 56、Teruaki等の日本人名)で、既存のPNAP/RET(X/Z)の領域。
- **小文字の一般語型で同型(1語置換が本文の唯一の差)が実在したのは gacha のみ**(7行、`census_02_common_oov.json`)。他は Khaite's→kite's(ブランド名)、minaudière(非ASCII。loanword_flagsで扱い済み)、prewash→pre wash(複合語分かち書き。既存規則)。**保存データ上の同型頻度は低い**(Word Gachaが「借用語・珍語」を主題にするため今回顕在化)。一方、構造(OOV語が1つあるだけで長文segmentが全文NG_BOTHに落ち、Azure 2〜3円/呼出が繰り返される)は借用語を含む全記事に共通。借用語・造語・サービス名の例=gacha、desking、blitzscaling、healthspan、counterspace、biofilm、touchscreen、unfollow、earbuds等(`census_02_common_oov.json`の上位)。
- Secondary救済の実態: Primary・Secondary転写の両方が残る144行中、Primary非PASS68行のうち Secondary採用37/NG_BOTH31(`census_03_union_result.json`)。長文で両エンジンが独立に別の箇所を誤る型は gacha 固有ではない。

## 6. 副次的に見つけた既存不具合(11-8分類=**修正へ進む**。本委任では未修正、Fableへ先に報告)
- `er011_b1_connected_speech_validator_01.py:103` `tokenize()` は `[A-Za-z']+` で、**ASRが出す ’(U+2019) を語構成文字として扱わない**(他の層 `er006_preprod_hardening_01_validation.py:497,1022` と `er006_m1_multi_candidate_01.py:60,331` は ’ を ' に正規化している)。結果、F1(Connected Speech)の residual が ’ を含む転写で `you've→you,ve` 等の偽残差になり、M1/Eq Layer の入口(F1残差 kind=content)で却下される。実データ: ’ を含むASR転写は全5,604行中23行(0.4%)、非PASS9件で ’ 正規化による結果変化は0件(過去の判定には影響なし)。ただし本run part3 attempt1・6(Adv)にも発生しており、ASRモデルの出力傾向次第で増える。修正は1行(正規化追加)。既存承認仕様の整合是正でありユーザー判断不要の見込み(Production共有file=Fableの先行承認を待つ)。`curly_apostrophe_census_01.py`。
- (注)RUNTIME_EVIDENCE_01の「Primary=UNCERTAIN」はpart3では不正確(§1)。

## 7. (e) 費用構造(本run実績。`raw_usage_log.jsonl`、`cost_cf_01.py`)
- 案件合計104.73円(text 37.71+audio 52.32+再生成14.70)。audioのAzureは36.03円(811秒、28呼出)。**gachaを含むsegmentだけで**: Azure 23.43円+TTS 13.12円+Primary ASR 2.02円=計38.58円(推計。attempt単位の配賦は保存分類から再構成。Gemini TTS単価=17.60円/923秒、Azure 0.0444円/秒、OpenAI ASR 4.64円/46呼出)。
- 同音誤認1件が招いた追加(part3 Advだけ): TTS 8回(通常1回)、Azure 8呼出(約15.0円)、Local Rewrite候補生成、600秒cooldown、HR Lock→approve_regenerate→Style Gate→人間承認(ユーザー手間)。
- 原価目標70円/記事セットに対し本件は104.73円(+34.7円)。

## 8. 過去に不採用/保留とされた方式(再導入しない。列挙)
| 方式 | 記録 | 本Phase 1での扱い |
|---|---|---|
| C3(規則G2P)・ASR転写からの後付け候補 | M1承認時に不採用(`er077_output/m1_oov_multi_pronunciation_01/SSOT_DRAFT_01.md`、CURRENT_SPEC L2797、UDR #52「綴りだけを根拠に任意の発音を許容しない」) | 候補Bとして**比較表に載せるが推奨せず**(再導入しない) |
| 直接音素置換(OF-184)・P2(G-1/G-2) | 「範囲外、需要はtelemetryで測定」/Fable ITEM1で「Qリスク大、非推奨」(`ITEM1_PHONETIC_EQUIVALENCE_ROOT_CAUSE_01.md` §5-2)。G-1/G-2はASR側OOV(Azure `Mellows`等)への自動許容を新設する案で、**Ledgerの出典付き読みに対する1:1直接一致(本委任の候補E2)とは対象が異なる**(E2は正準語側OOV+ASR語がCMU収録) | E2は「OF-184の需要測定が満たされた」ことを根拠に提案。ユーザー判断事項(承認済み受理面の拡張) |
| OpenAI promptの本文segment拡張 | er065 `TRIAL_REPORT_01.md` E-3で masking懸念、「独立証拠と併用が条件」(分類C=新規) | 候補A: 実測で効果25%+誤PASS実例あり→非推奨 |
| A-1(a) Ledger登録語のentity_like化 | 2026-09-28 DEFERRED/NOT_ADOPTED | 候補E1として比較。再採用は「必要かつ安全な追加条件」の証拠が要る→本件が証拠候補 |
| 個別override追記 | OPEN-498案Aをユーザーが不採用(UDR #183) | 候補D(比較基準のみ) |
