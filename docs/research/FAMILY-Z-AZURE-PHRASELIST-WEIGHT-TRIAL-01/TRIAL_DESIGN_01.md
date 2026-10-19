# TRIAL_DESIGN_01 — Azure Phrase List 重み比較Trial(事前登録、実走前commit)

管理ID: FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 / 作成: 委任_01(2026-10-20) / 性質: Offline Trial(Production非変更) / 到達上限: VALIDATED(Production採用はユーザーのみ)
ユーザー原文: `docs/pm/delegation_log/2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_USER.md`(sha256 7d7b9e16…8a63358)。
harness: `er084_azure_phraselist_weight_trial_01_{lib,run,eval,judge,test_01}.py` / 条件: `design_matrix_01.json` / 生ログ: `er084_output/azure_phraselist_weight_trial_01/raw/azure_calls.jsonl`(追記型)。

## 0. 事前調査の確定事項(W1、実走前に確定したSDK事実)

| 項目 | 結果 | 根拠 |
|---|---|---|
| Production Azure呼出 | SDK `azure-cognitiveservices-speech` 1.50.0、`SpeechConfig`既定+`speech_recognition_language="en-US"`、`AudioConfig(filename)`、**連続認識**(`start_continuous_recognition`、recognizedをjoin)、`PhraseListGrammar.from_recognizer`+`addPhrase`のみ、**setWeight呼出なし** | `er006_secondary_asr_01.py:70-132`(`get_full_text_via_azure_stt_with_phrase_list`、L93-101が設定、L132が連続認識開始) |
| 重みAPI | **ある**: `PhraseListGrammar.setWeight(weight: float)`。`dir()`=`['addPhrase','clear','from_recognizer','setWeight']` | `.venv/Lib/site-packages/azure/cognitiveservices/speech/speech.py:1531-1537` docstring「The allowed range is [0.0, 2.0]. The default weight is 1.0. Value zero disables the phrase list.」 |
| 未指定の既定値 | SDK docstring上は1.0。**実機(wire)でも確認済み**: setWeight未呼出のとき、送信される`speech.context`は`"dgi":{"Groups":[{"Type":"Generic","Items":[{"Text":"Melos"}]}],"bias":1.000000}`で、`setWeight(1.0)`時と**一致**。2.0時は`"bias":2.000000`、property `SPEECH-PhraseListWeight`も1.0/1.0/2.0 | `er084_output/azure_phraselist_weight_trial_01/probe_weight_wire_evidence_01.json`(録音2の先頭4秒clipでSDK診断ログ`Speech_LogFilename`を取得、3呼出、実費約JPY0.53) |
| SDK更新の要否 | **不要**(現行1.50.0が重みAPIを持つ)。別venv検証も不要 | 上記 |
| 注意(Production側の古い注記) | `er006_secondary_asr_01.py:288` `CASCADE_CONFIG["phrase_list_weight"]` のコメントは「現行SDKでは重みAPIを公開していない」とするが、1.50.0は公開している(コメントの事実誤認。値`None`は未使用の設定キー)。本委任では変更しない | Grep: `phrase_list_weight`は同行のみ |

- 「重み未指定=1.0」はSDK docstringとwireログの両方で成立。ゆえに **`pl_unspecified`と`pl_w1.0`は送信内容がバイト同一**(同一音声ならAzure応答の差は「Azure側のばらつき」のみ=ノイズ床の直接測定に使える)。
- 重み反映の証拠は各呼出の`SDK log`(`sdk_logs/`)から`SPEECH-PhraseListWeight`と`speech.context`の`dgi.bias`を機械抽出して`raw`行に格納(`wire_evidence`)。`no_pl`は`dgi`が載らないことを確認する。
- 過去結果(同一wav反復の情報価値の事前評価): ITEM1_PHONETIC_EQUIVALENCE_ROOT_CAUSE_01.md §4(L71以降)=録音2のAzureは Production記録と今回再転写で`Mellows drank`が同一、PLあり/なしも同一(PLの効果なし)、take間では`Mellows`/`Mellow strength`/`Melos`と別綴り=**同一wavには決定的、takeの微小差には敏感**。HR_LOCK_PART3C1_ROOT_CAUSE_01.md §3も同旨。→ **H0(同一wavでは決定論的)の事前確率は高い**。したがって反復は「決定論性の実測」(Phase A、各条件3回)で一旦確かめ、決定論なら以後は同一wav反復でなく**take(音声)を増やす**方向へ配分する(ユーザー原文§2・§3-C「情報価値が低い場合は音声・文脈を増やす」に従う)。

## 1. 目的・仮説

目的: Azure Secondary ASRで、PhraseListの重み(1.0/1.5/2.0)が、固有名詞(Melos)の認識を実用上改善しつつ、誤発音を`Melos`と誤認する副作用を増やさないかを判定する。最終目的=一般的な固有名詞の誤認識を減らし不要なTTS再生成・HRを減らせるかの判断(特定重みで1回Melosが通ることではない)。

- H1: 重み↑で、正例の`Melos`正認識率が上がる。
- H2: 重み↑で、負例(Melosを発音していない音声)の誤`Melos`率が上がる(副作用)。
- H3: 文脈(後続音・文長・位置)・take・話速の影響が重みの効果より大きい。
- H0: 同一wavではAzureは決定論的で、(少なくとも録音2では)重みに感応しない。

## 2. 条件と試行設計

固定条件: Azure en-US・連続認識・SDK 1.50.0・Production同一コード経路(libは差分=setWeight呼出とSDK診断ログのみ)・PhraseList=`["Melos"]`(Production Ledger由来と同一、`asr_consistency_part3c1_01.py`と同じ)。音声は重み条件間で**同一wavを共有**(重み以外固定)。

条件(5): `no_pl`(PLなし・対照)/`pl_unspecified`(PLあり・setWeight未呼出=現行Production再現)/`pl_w1.0`/`pl_w1.5`/`pl_w2.0`。

### 2-A 基準条件(委任_01で実走)
録音2=`run_e2e_04/a2/narration/attempts/full_story_part3_c1_attempt2_customa3c4625e.wav`(sha256 f96c224d…、24.59秒、Voice=Aoede、model=gemini-3.8-flash-lite-tts、6%減速未適用の生take。HR_LOCK_PART3C1_ROOT_CAUSE_01.md L17、attempt json)。5条件×3回=15呼出(約369秒)。順序はrep外側・条件内側(時間ドリフトを均す)、逐次実行(SDK診断ログ競合の回避)。
Primary(OpenAI)転写はProduction記録(attempt2 json `asr_text`、`Mello drank`)を注入して、Production統一judge(`evaluate_attempt_with_cascade_detail`)にoffline注入(`..._judge.py`、判定ロジック無変更)。

### 2-B 文脈別(委任_02で実走。Aの決定論性実測を見て§2-Cで調整)
正例7: P1`Melos drank deeply from the cold stream.`(非歯擦音後続=失敗条件)/P2`Melos said nothing to the guards.`(歯擦音後続)/P3`The man waiting at the gate was Melos.`(文末)/P4`Then Melos walked away.`(文中)/P5`Melos spoke, and Melos listened.`(複数出現)/P6 長文(50語以上、`design_matrix_01.json`)/P7`Melos liked the mellow sound of the old bell.`(一般語競合を含む正例)。
負例4(原稿にMelosが無く、`Melos`と出たら誤認識): N1`The mellow sound of the bell drifted across the square.`/N2`The old wine mellows slowly in the cellar.`/N3`Her gray cat Mello slept by the window.`/N4`Milos drank slowly from the cup.`(実在の近音固有名詞)。
**負例の判定面(誤PASS検出)**: 各負例wavについて、Production判定への注入時のcanonicalを「confusable語をMelosに置換した文」(例N4→`Melos drank slowly from the cup.`)とし、Azureが`Melos`と出して誤PASSしないかを見る(=本来NGの音声を誤PASSしないか)。canonicalは実走前にwav manifestへ固定。
Voice: Aoede・Charon(Family Zで使用実績。run_e2e_05に両方あり)。Aoedeは6%減速版(Production Std経路と同じ`apply_a2_slowdown_postprocess`相当の後処理。実装は委任_02で既存関数をそのまま呼ぶ)も作る。P1のみ同一文を**4take/voice**(take差の測定)、他は1take/voice。TTSは`TTS_EXECUTION_MODE=STANDARD`、model=`gemini-3.8-flash-lite-tts`。
wav数=正例30(P1: 8take+Aoede減速4=12、P2〜P7: 各3=18)+負例12(4文×3)=**42wav**。

### 2-C 反復と追加(事前ルール)
1. Phase Aで各条件3回が全て同一転写(決定論)なら、Phase Bは1呼出/(wav×条件)。いずれかの条件で3回が揺れたら、Phase Bは2呼出(上限2)、かつ揺れた条件を最大5回まで追加(上限)。
2. Phase B後、**ベースライン失敗集合 R**(正例wavのうち`pl_unspecified`でMelosが正認識されないもの)が6件未満なら、効果が識別できない(条件が簡単すぎる)ため、失敗しやすい文脈(P1・P2型)のtakeを追加(別voice: Algieba/Erinome、最大+24take)して R≥6 を目指す。それでもR<6なら「識別不能=INCONCLUSIVE」として報告(結論の水増しはしない)。
3. 同じ条件を機械的に繰り返さない。追加は新take・新文脈に振る。

## 3. 指標と判定基準(事前固定)

指標: 条件別(a)正例のMelos正認識率(wav単位。期待回数=原稿内のMelos数と一致、全rep正認識)、(b)負例の誤`Melos`率、(c)同一(wav,条件)内の異なり転写数(ばらつき)、(d)誤認識variant(mello/mellows/melo/mellow…)の回数、(e)Production判定offline注入の状態(PASS/PASS_WITH_WARNING/NG_BOTH等)、(f)呼出数・秒・JPY・処理時間。

**判定基準(結果を見る前に固定、変更は§9)**
- 比較基準: ベースライン=`pl_unspecified`(現行)。`no_pl`は対照、`pl_w1.0`はノイズ床(§0のとおり送信同一)。
- 識別力の前提: R(§2-C)≥6 でなければ効果の有無を断定しない(INCONCLUSIVE)。
- **改善(fixed)**: ベースライン失敗wavのうち、重みwで全repが正認識になった数。
- **VALIDATED候補**(w=1.5または2.0のいずれか): ①fixed ≥ 3 かつ fixed ≥ 0.30×R ②**負例の誤Melos件数がベースラインより増えない(増加0)**③悪化(ベースライン正認識→w誤認識)が fixed の1/3未満かつ ≤1 ④2文脈(P1〜P7のうち2種以上)かつ2種以上のVoice/話速条件(Aoede通常/Aoede減速/Charon)で改善が再現 ⑤Production判定注入で、改善wavがNG→PASS系に変わり、かつ負例canonicalの誤PASSが0。
- **REJECTED**: fixed < 3、または fixed<0.30×R(R≥6のとき)。
- **USER_DECISION_REQUIRED**: ①〜⑤のうち②が破れる(負例の誤Melos増≥1)が改善は①を満たす場合(トレードオフ)、または④が破れる(特定Voice/文脈限定)場合。
- 「1回だけの偶然」排除: 効果判定はwav単位の全rep一致で数える。揺れるwavは「不安定」として別枠に集計し、fixedに数えない。

## 4. 試行数・費用見積(単価: `er005_output/cost_baseline_01/pricing_snapshot.json` azure STT USD1.0/audio hour、160JPY/USD≒JPY0.0444/秒)

| Phase | 内容 | 呼出 | 秒 | JPY |
|---|---|---|---|---|
| probe(実施済) | 録音2の先頭4秒×3(重み反映確認) | 3 | 12 | 0.53 |
| A | 録音2(24.59秒)×5条件×3回 | 15 | 368.85 | **16.39**(委任文の見積「録音2約10秒」は誤り。実wavは24.59秒) |
| B(1呼出/wav×条件) | 42wav(合計約220秒)×5条件 | 210 | 約1100 | 約49 |
| B TTS | 28take(Gemini flash-lite、約JPY0.3/take) | – | – | 約8 |
| B Primary(OpenAI gpt-4o-mini-transcribe) | 42wav×約JPY0.1 | 42 | – | 約4 |
| B 揺れ時の2呼出目(条件付き) | 上記Azure再実行 | +210 | +1100 | +49(条件付き) |
| C 予備 | 追加take・追加rep | – | – | 上限約60 |

見込み合計: 基本約JPY78(probe+A+B)、最大約JPY187(Bの2呼出目+C予備全額)。**案件合算300円以下**。日次1,000円内(当日既使用28.79)。
Phase A実費がFable枠(委任_01 ≤JPY12)を超える理由: 録音2のwavが約10秒でなく24.59秒だったため(原因把握済み・異常retryでない・便益=H0の決定論性直接測定)。超過額≈JPY4.4+probe0.53をRESULT_PACKETに記録。

量産影響(70円/記事セット目標): 重み導入は`setWeight`1行でAzure呼出回数・秒数は不変=**追加費用0**。便益側は、誤NG回避1回あたりTTS再生成(約JPY0.3〜1.2)+Azure/OpenAI再検証(約JPY1.2)+HR工数の削減。副作用(誤PASS)のリスクは§3で別評価。

## 5. 実行順序・並列化
A先行(逐次15呼出、約7〜10分)→A集計→Bのwav生成(TTS 28takeを1回でまとめて生成。Gemini TTSは単価・rate limitを見てFableが並列度を判断)→Azure呼出(wav×条件はSDK診断ログ競合を避けるため基本逐次、wavごとにprocess並列化する場合はログ名を分離)→集計。Primary OpenAI転写は42wavを並列可。直列理由: A→Bの反復数決定(§2-C-1)、SDK診断ログの競合回避。

## 6. 都合のよい採用の防止
全試行の生ログ(`raw/azure_calls.jsonl`)を追記型で保存し、eval scriptは**全行**を集計(除外ロジックなし、`test_aggregate_positive_negative_and_no_exclusion`)。除外条件は事前に列挙: 「SDK errorでtext無し」のみ(err列として別集計し母数から外すが件数は表に出す)。条件・指標・閾値の変更は§9の改訂履歴に残す。

## 7. Opusレビュー観点案(5件以内)
1. 判定基準(fixed≥3かつ≥30%R、負例増加0、悪化<fixed/3)が統計的に妥当か。小標本(R≥6)での過大解釈の余地。
2. `pl_unspecified`と`pl_w1.0`が送信同一である前提で、両者の差を「ノイズ床」として扱う設計の妥当性。
3. 負例のcanonical置換による誤PASS検出が、Production判定の保護(CMU/M1/Tier3等)を過不足なく再現しているか(offline注入の忠実性)。
4. Voice/話速/文脈の要因分離(P1を4take/voiceにする配分)が、take差と重み効果を分離できるか。
5. Phase Cの停止則(R<6でINCONCLUSIVE)が「過剰Trial」と「結論の水増し」のどちらにも偏らないか。

## 8. 既存仕様照合(E-1)
- Production PhraseList仕様: `CURRENT_SPEC.md:2089`「Azure ... Secondary ASR Cascade(entity-like mismatch検出時のみ、英語はPhrase List付き)として両言語で使用する...決定はASR単独では下さない」、`:2139`「Ledgerから取得した発音候補をSecondary ASRのPhrase List(`ledger_phrases`)へ渡す経路のみ」、`:2141` ASR-first Retry Policy ③「Azure Secondary ASR + Phrase List #1(entity-like mismatch検出時のみ)」。
- 「PhraseListは聞き取りバイアスのみで受理根拠にならない」原則: `er006_secondary_asr_01.py:70-76` docstring「Azureがその語を認識しやすくなる(重み付けのみ、認識結果を強制はしない)」。Trialでも、重み↑で`Melos`と出ることを根拠にPASSさせる設計にはしない(§3②・⑤で誤PASSを別評価)。
- A案・A'案(REJECTED)・P1/P2は暗黙採用しない。判定ロジックは`evaluate_attempt_with_cascade_detail`を無変更で呼ぶのみ。HR log/attempt_history等のProduction副作用ファイルは書かない(`test_judge_offline_matches_production_and_no_side_effects`)。

## 9. 改訂履歴
- 2026-10-20 v01: 初版(実走前)。
