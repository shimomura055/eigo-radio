# AZURE_ITN_IMPACT_01(2026-10-22、FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01 委任_02 (B)。読み取りのみ・API 0・費用0・Production変更0)

集計script=`docs/research/FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01/azure_itn_aggregate_01.py`、集計json=`azure_itn_aggregate_01.json`(再実行で同値)。**確認済み**=保存記録/コード実行の観測値、**推測**=近似・仮定を含む見積。

## 1. 結論

- Azure(Secondary)の転写は**ITN(数値整形)後の表示形**をそのまま使っており、lexical形は取得も保存もしていない。`one's`を`1's`と整形されると、値ガードが「期待側に数字なし・転写側に数字あり」を数値保護差(DIFF)と判定し、Azureは必ずNG+protected diffになる(確認済み)。
- 保存データで確認できる実害は **coffee a2・b1b の2 KP(wav 8本)のみ**。KP英語の保存lock state 566件(canonical解決548件)中2件=約0.4%、HR 13件中2件。ただし2件ともPrimaryがPASSしたattemptを含む(a2#1、b1b#1・#4)ため、Azureが`one's`と出していればHRに至らなかった**可能性が高い(推測)**。
- 仕様変更案(下記§5)は**どれも実施していない**。承認区分はいずれもFable判断→必要ならユーザー承認。

## 2. 判定器の仕様確認(file:行)

| 確認事項 | 結果 | 出典 |
|---|---|---|
| Azureが返す転写 | `evt.result.text`(Recognized時のtext=表示形=ITN・句読点・大文字化済み)を連結。lexical/NBest/Detailed形式は取得していない(grep: `lexical`/`NBest`/`Detailed`/`output_format`は`er006_secondary_asr_01.py`・`er078*.py`・`er104*.py`でヒット0) | `er006_secondary_asr_01.py:118`(`segments.append(evt.result.text)`)、:78-150 |
| 保存される形 | 表示形のみ(`review_lock_state.json` `asr_judgement.secondary.text`、attempt jsonの`cascade_steps[].text`) | 実データ(`Pump 1's fist.`) |
| KPの判定票 | `make_voter`=`classify_asr_match`+同音救済+`uj._protected`(値ガード+否定ガード)。`pdiff = vgr.kind==DIFF or neg`、`passed = ok and not pdiff` | `er104_kp_three_asr_vote_01.py:248-264` |
| 値ガード呼出 | `_protected`→`vg.value_guard(canonical, text, lang)` | `er078_asr_unified_judge_01.py:348-350` |
| `one's`の扱い | Tier1 atomizerは`one's`を**literal 1語**(`[{'literal':'pump'},{'literal':"one's"},{'literal':'fist'}]`、実行確認)。`1's`は**number atom(値1)** | `er078_asr_value_guard_01.py:339-357`(`_en_sequence`) |
| 数値保護差の発火 | 期待側literal vs 転写側number atom=対応する数atomなし→`drop(b, ..., "hyp")`。`soft_one`(転写側に単語`one`があるときのみ立つ、:351)でないため`UNKNOWN`でなく`DIFF("hyp_drop(b)")`(:490-499)。実行: `value_guard("pump one's fist","Pump 1's fist.","en")`=`DIFF`、`("Pump one's fist","Pump one's fist")`=`NO_VALUES` | `er078_asr_value_guard_01.py:475-525` |
| 既存の数詞↔数字正規化 | あり(単独`one`↔`1`等はnumber atomとして同値=`EQUAL`、実行確認: `one of the boys`/`1 of the boys`=EQUAL)。**`one's`↔`1's`(縮約・所有格)には効かない**(`one's`がatom化されないため) | 同上 :339-357、実行確認 |
| protected dissentでWhisperを呼ぶか | 呼ばない。PとSが割れて、異議側(dissent)がprotected_diffならWhisper不要(False)。PがPASSでSがprotected diff→`NG_PROTECTED_DISSENT` | `er104_kp_three_asr_vote_01.py:138-146`(`whisper_needed`)、:161-171(`tally`) |

## 3. 保存データ集計(出典・母数)

母集団の注意: Azure転写が保存されるのは「Primaryが不合格、または投票でSecondaryを呼んだ」attemptのみ。以下の「Azure転写あり」母数=**90 wav**(sha256で重複排除)。出典=全`**/audit/review_lock_state.json`の`kp*_en.last_attempts_log[].asr_judgement`(58 wav)+`**/narration/attempts/kp*_en_attempt*.json`の`cascade_steps`(重複除く32 wav、合計789 attempt jsonのうちAzure呼出あり)。期待KPは同run `audit/tts_generation_results.json`(なければ`key_phrases/keywords_canonicalized.json`)から解決(52/90 wavで解決、残りはcanonical不明で集計から除外=下表の分母は90でなく52が有効)。`er006_output/master_audio_store_01/manifest.json`は音声キー/ハッシュのみで転写・期待文を持たず**集計に使えない**(確認済み)。`er011_output/attempt_history.jsonl`はtext無し(sha256のみ)のためHR到達segment数の分母にのみ使用。

| 項目 | 件数 | 母数・備考 |
|---|---|---|
| (i-a) Azure転写に数字0-9あり かつ 期待KPに数字なし | **9** wav | うち8=coffee `run_jre_01` a2/b1b(`Pump 1's fist.`7本・`Pump 1's.`1本)、1=`evidence_06e`合成語`Xzqwtrlk wrangle`→`X ^2, a length wrangle.`(Azure誤認識で数字化。ITNによる数詞整形ではない=**除外して実質8**) |
| (i-b) そのうちAzure NG | 8(実質) | 保存フラグ`pass=false`は4(review_lock_state由来)。残り4本はattempt json由来でpass値が未保存→現行voter再判定(`make_voter`、API 0)で**8本すべてNG+protected_diff=True**(再現確認) |
| (ii) その件数のうち最終判定がHR | 8 wav(=**2 KP segment**) | coffee a2・b1bのkp1_en(`review_lock_state` state=`HUMAN_REVIEW_REQUIRED`) |
| 参考: Azure NG全体 | 19 wav(うち14がHR segment) | 母数90(pass 64、pass未保存7)。うち8がITN起因 |
| 反事実(近似): Azure転写の数字を英単語へ戻して再判定 | 8本中7本がPASS(`Pump one's fist.`)、1本は`Pump 1's.`(fist欠落)でNG | **推測**: 数字→単語の単純置換(実lexical形ではない)。API 0。`cf_pass`列 |
| (iii-a) 期待KPが所有格/不定代名詞形(`one's`・`someone's`等)を含む、KP英語segment | **24** / 548 | HR 3(coffee x2 + Z melos run_e2e b1b `force one's way through`=Azure転写が保存されておらず原因不明) |
| (iii-b) 期待KPが`one's`そのもの | **11** / 548(異なるテキスト7) | `pump one's fist` `apply one's findings` `at one's own pace` `place of one's own` `change one's surroundings` `force one's way through` `room for one's own pace`。HR 3 |
| (iii-c) 上記のAzure転写が保存されているもの | production保存: `pump one's fist`のみ8本(8/8がAzure `1's`→NG=NG率100%)。trial corpus `stored_audio_reeval_02.json`(84行): `apply one's findings`1本はAzure `one's`でPASS | 母数が小さい(同一フレーズ中心)。**ITN化は語・文脈依存**(`apply one's findings`は`one's`のまま)で、`someone's`系(`in someone's place`)は1語なので影響なし(Azure PASS) |
| 参考: 期待KPに単独`one`を含む | 4 / 548(HR 1=`Make one yourself with byUs.`の合成テスト) | 単独`one`↔`1`は数値正規化でEQUAL(影響なし) |
| 参考: `stored_audio_reeval_02.json`でITN数字 | 0 / 84行 | KP3V trial corpusには該当なし |
| 参考: KP英語segment総数・HR数 | lock state 566 segment、HR 13(`attempt_history.jsonl`では425 segment中HR 10、older runのみ) | |

## 4. 影響見積

- **確認済み**: ITNが直接の原因で「Azure NG+protected diff」になったattemptは8 wav、HR確定したKP segmentは**2件(coffee a2・b1b)**。KP英語の保存lock state 566件中2件(0.35%)、HR 13件中2件(15%)。
- **推測**: この2件はPrimaryがPASSしたattempt(a2#1、b1b#1・#4)を持つため、Azureが`one's`と出していればPASS_DUALとなりHRに至らなかった可能性が高い(Azure反事実は近似)。small_bag(`novelty minaudière`)はAzure転写に数字がなくITN無関係(別原因、EVIDENCE_01)。
- **将来見積(推測・低確度)**: 現行Luna全文選定は`its/his/her`→`one's`への一般化を行うため(承認済みの人称一般化規則)、`one's`含むKPは548 segment中11件(2.0%)ある。Azureが同様に`1's`へ整形する語は`pump one's fist`のみ確認済みで、他の`one's`は未確認(trialでは`one's`を維持)。一般化KPの何%が実際にITN起因HRとなるかは**未確定**(1語・1例のため)。
- 音声自体の良否は本分析では判断しない(ユーザー試聴待ち。OPEN-456 F3、EVIDENCE_01)。

## 5. 対策候補(**実装・採用なし**。列挙のみ)

区分: 承認済み仕様の変更か。

| # | 候補 | 承認済み仕様の変更か | 追加API | 誤PASSリスク |
|---|---|---|---|---|
| C1 | Azure取得時にlexical形(`RecognitionResult.best()[0].lexical`、Detailed output)を併せて取得・保存し、数値保護差の判定にlexicalを使う | 該当(KP3V/値ガードの入力定義変更=承認済みASR判定仕様の変更。ユーザー承認要) | 追加呼出なし(同一Azure呼出のoutput形式変更。SDK設定のみ) | 低〜中: lexicalは数詞が単語のままなので原稿の数字を誤読していても発話確認しにくい。数値KP(`2 days`等)の保護は維持が必要 **【ユーザー不採用(REJECTED、2026-10-22)。対症療法のためProduction配線しない。同一発音・異表記は包括対策ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01へ)】** |
| C2 | 値ガードで「期待側に数字なし・転写側のnumber atomが数詞1語由来(`1's`等)」をDIFFでなくUNKNOWN/AMBIGUOUSに(`one's`↔`1's`同値化、縮約`'s`付きの数詞を単語へ戻す) | 該当(`er078_asr_value_guard_01.py`の挙動変更=承認済みGate/保護条件の変更。ユーザー承認要) | 0 | 中: 本物の数字読み間違い(`1's`と実際に言った等)を見逃す余地。対象を`one's`/`ones`に限定すれば低 |
| C3 | 期待側に数字がない場合のみ、Azure由来の数字を英語数詞へ戻した転写(de-ITN)でも`classify_asr_match`+値ガードを再評価し、どちらかPASSなら可とする(本分析の近似反事実と同じ) | 該当(投票規則・保護条件の変更。ユーザー承認要) | 0 | 中: 近似de-ITN(`X ^2`のような誤認識数字を単語化する等)の誤PASSを個別検証が必要 |
| C4 | protected dissent(P=PASS・S=protected diffのみ)でもWhisper(local、API 0)を呼ぶ | 該当(「protected dissentはWhisperを呼ばない」設計=`er104:138-146`の変更。ユーザー承認要) | 0(local faster-whisper、費用0) | 中〜高: 数値保護差を多数決で覆す設計になり、本来保護差で止めるべき誤数値でも通る余地(Opusレビュー要の可能性) |
| C5 | Azure Phrase Listにcanonical(`pump one's fist`等)を渡して`one's`出力を誘導(現行KP判定はphrase_list 0) | 一部該当(Azure Phrase List適用範囲はAzure補強系で承認済み[`AZURE_PHRASE_LIST_WEIGHT`=2.0、er006:70-77]。KP英語への新規適用はFable判断) | 追加呼出なし | 低〜中: Phrase Listは重み付けのみで強制ではない。ITNを回避できるかは未検証(要Trial、費用0〜微小) |
| C6 | 上記は一切せず、HR queue運用のみで対処(量産でHR率が高ければ再判断。OPEN-456 F1/F3) | 非該当 | 0 | なし(現状維持)。ただしHR増=量産D影響 |

推奨(Fable判断材料): まず**ユーザー試聴でcoffee音声が実際に`one's fist`と聞こえるか確認**(OPEN-456 F3)。聞こえるなら「ITN起因の偽NG」が確定し、C1(lexical併用)またはC5(Trialで効果確認)が最も影響が局所的。聞こえないなら音声側の問題でありC1〜C4は不要。いずれも**承認済み仕様の変更**なのでTrial→VALIDATED→ユーザー正式採用の順。
