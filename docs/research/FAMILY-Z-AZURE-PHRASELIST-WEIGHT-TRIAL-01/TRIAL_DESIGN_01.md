# TRIAL_DESIGN_01 — Azure Phrase List 重み比較Trial(事前登録、実走前commit)

管理ID: FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 / 作成: 委任_01(2026-10-20) / **v02改訂: 委任_02b(2026-10-20、Opus_J GO_WITH_CHANGES反映、実走前)** / 性質: Offline Trial(Production非変更) / 到達上限: `PLW_TRIAL_CLOSEOUT_PENDING_FABLE`(eval機械判定はVALIDATED候補/REJECTED/判断候補/INCONCLUSIVE、最終ラベルはFable、Production採用はユーザーのみ)

> **v02注記**: §2-D〜§2-F・§3-v02・§4-v02は委任_02bで追加した(v01の§2-B負例・§3・§4は履歴として残置)。v01と矛盾する場合は**v02が優先**(理由は§9)。判定基準の機械可読な正本は`criteria_thresholds_01.json`(v02)で、testが本書§3-v02と一致を検査する。Opus_J逐語=`OPUS_REVIEW_J_01_VERBATIM.md`(sha256 26120a37…)。
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

## 2-D [v02] 負例の再設計(Opus_J M-3)と主評価集合(S-1)

### 2-D-1 負例の再分類と追加minimal pair(M-3)
- Ledger(`er006_output/pronunciation_ledger_01/ledger.json:1171-1175`)の期待発音は/ˈmiː.lɑːs/で別読みに/ˈmɪlɒs/・/ˈmɛloʊs/を持つため、**N2`mellows`(/ˈmɛloʊz/)・N4`Milos`(/ˈmɪlɒs/に近い)は「境界例」へ再分類**する。②の分母から除外し、別枠(「境界例: Azureがこれらを`Melos`と出す場合の本番判定」)で報告する(wavは生成済み、Azure条件も流す)。
- **負例の主軸=正例と同文脈のminimal pair**: P1/P3/P4の文脈で`Melos`だけを差し替え、TTS原稿の綴りで発音を誘導する: `Mello`(語末s脱落)・`Melon`(別子音)・`Mullos`(許容外母音)の3種 × 3文脈 × Aoede通常/Charon通常 = 18 take、+ Aoede減速(6%)9 = **27 wav**。Production判定へ注入するcanonicalは**元のMelos文**(例:`Then Melos walked away.`)。
- 有効負例 = N1・N3の6 wav + 27 = **33**。誤PASSが0件でも**rule of three(0/nの95%上限≈3/n。n=33で約9.1%)を併記**する。
- id規則: `NM_<P1|P3|P4>_<mello|melon|mullos>_<Aoede|Charon>_take1`(+`_slow6`)。manifest_01は不変、追加分と再分類フラグは`manifest_02.json`に保存。

### 2-D-2 主評価集合=本番既存take(S-1)
- 母集団: `er026_output/family_z_production_e2e_01/melos/run_e2e_0[1-5]/{a2,b1b}/narration/attempts/*.json`のうち、(i)そのsegmentの確定canonical(同run・同levelの`audit/tts_generation_results.json`の`canonical_text`)に`Melos`を含み、(ii)記録された本番Primary転写(`asr_text`)のMelos出現数がcanonicalと異なる(=Primary NG系)、(iii)wavが実在しsha256がattempt jsonと一致するtake。
- **選定規則(事前固定、結果非依存)**: 上限**20本**(秒数合計≤500秒)。(1)wavのsha256重複を除外。(2)canonical文字列が同一のものを1「文」とし、1文につき代表1 take(sha256の昇順最小)。(3)文の選択順: まず各segment_idにつき「Primary NGのtakeが最も多い文」(同数なら長い文、さらに同数ならcanonical sha昇順)、次に残りを秒数の短い順。20本または500秒に達したら打切り。(4)PhraseList=現行Ledgerから本番と同一の取得(`[h["canonical_spelling"] for h in get_hint_for_text(canonical, min_confidence="low")]`、`er003_v1_n3_01_tts_generate.py:139-141`)。(5)Primary転写は**記録値**(再転写しない)。
- 実績(委任_02b scan): Primary NG系候補93 take/26「文」(14 segment id)。選定=20 take(合計約209秒)。Melos以外のPL対象名(Dionysius/Selinuntius等)を含むcanonicalは**0件**(Ledgerには登録があるが`run_e2e_01-05`の本文clipに出現しない)→ 一般化probe(S-6)=**0本**(新規TTSによる一般化は本Trial外。別Trial/条件Cレビュー前に提案)。S-4(複数語PL)は自然には含まれない: 既定では追加しない(Scope・費用を広げない)。
- 本番takeの文脈は**実際の本番clip**(narrator、Aoede、flash-lite+PD06、長さ1.6〜50秒)で、TTS費用0・HR削減効果を最も直接に反映する。合成短文は文脈を分けて見る補助とする。

## 2-E [v02] 条件・反復・抜き打ち(S-2/S-3)
- 重み条件: `no_pl`/`pl_unspecified`(ベースライン)/`pl_w1.5`/`pl_w2.0`の4条件を全wav(合成42+追加負例27+本番take20=89 wav)に1回ずつ。**`pl_w1.0`は送信がバイト同一**(§0)のため、全wavの約10%(9 wav)のみ抜き打ち。**rep2は同じ9 wavの4条件+w1.0**で決定論の再確認(Phase Aの1 wav×3回以外でも確認)。抜き打ち対象=wavごとに`sha256(wav sha256 + ":spot")`の昇順で、秒数≤10秒のwavから先頭9件(費用を抑えるため長尺を除外。選定規則は結果非依存)。
- **主たる重み=1.5を事前宣言**(Phase Aはpilot扱い)。2.0は副で、検定は多重比較としてα/2(=0.025)で行う(S-3)。承認3値以外(1.25/1.75等)は実走しない(S-5)。
- 1.25/1.75が必要と見えた場合(1.5で効果不足かつ2.0で副作用、等のトレードオフ)は、実走せずRESULT_PACKETの判断候補として報告する。

## 2-F [v02] Production判定の再現(M-1/M-2)
- judgeは**2つのrole条件**で呼ぶ(Opus_J M-5): (a)**FULL_STORY role**(Tier3あり・CS層有効): 本番takeは実segment名、合成wavは`full_story_part1_c1`(Family Z narrator clip名型)。`enable_connected_speech_equivalence_layer=connected_speech_enabled_for(segment_id)`、`force_secondary=False`(本番既定)。(b)**Tier3なしrole**: `segment_id=None`相当(KP型)。
- 副作用ガード: judge内で`semantic_equivalence.append_telemetry_log`をno-op化、`is_last_slot=False`固定(HR要否はeval側で「NGなら最終slotでHR」と換算=`ng_would_hr`)。`er021 telemetry.jsonl`・`ledger.json`・`er011 attempt_history.jsonl`・HR queue・HR logのsize+mtime不変をtestで検査。
- golden replay test(`er084_azure_phraselist_weight_trial_01_judge_test_02.py`、実走前Gate): run_e2e_04 part3_c1 attempt2記録(Primary`Mello drank`/Azure`Mellows drank`)で`primary_1,tier3_corroboration_secondary,secondary_1`の順に出てNG_BOTH、run_e2e_05 Std減速後(Primary`Mellos drank`/Azure=Melos)で`SECONDARY_ASR_CORROBORATED_MATCH`/`PASS_WITH_WARNING`の再現をassert。**PASSしなければPhase B Azure実走禁止**。
- M1凍結の注記(Opus_J補足): judge内M1は**現在のLedgerを読むread-only経路**(`er006_secondary_asr_01.py:233-237`)で、本番run時点のsnapshotとは異なる。「今後の本番挙動」を見る目的では現在のLedgerで妥当。
- Charon経路の制約(02a報告): Charonも本Trialではナレーター経路(flash-lite+PD06)で生成(Production ZのCharonは対話経路で別model)。Charonの結果はProduction対話経路の再現ではない。
- 減速の実測は5.4〜5.9%(`apply_a2_slowdown`のatempo実測。名目6%)。

## 3. 指標と判定基準(事前固定) — **v01(委任_01。§3-v02で置換、履歴として残置)**

指標: 条件別(a)正例のMelos正認識率(wav単位。期待回数=原稿内のMelos数と一致、全rep正認識)、(b)負例の誤`Melos`率、(c)同一(wav,条件)内の異なり転写数(ばらつき)、(d)誤認識variant(mello/mellows/melo/mellow…)の回数、(e)Production判定offline注入の状態(PASS/PASS_WITH_WARNING/NG_BOTH等)、(f)呼出数・秒・JPY・処理時間。

**判定基準(結果を見る前に固定、変更は§9)**
- 比較基準: ベースライン=`pl_unspecified`(現行)。`no_pl`は対照、`pl_w1.0`はノイズ床(§0のとおり送信同一)。
- 識別力の前提: R(§2-C)≥6 でなければ効果の有無を断定しない(INCONCLUSIVE)。
- **改善(fixed)**: ベースライン失敗wavのうち、重みwで全repが正認識になった数。
- **VALIDATED候補**(w=1.5または2.0のいずれか): ①fixed ≥ 3 かつ fixed ≥ 0.30×R ②**負例の誤Melos件数がベースラインより増えない(増加0)**③悪化(ベースライン正認識→w誤認識)が fixed の1/3未満かつ ≤1 ④2文脈(P1〜P7のうち2種以上)かつ2種以上のVoice/話速条件(Aoede通常/Aoede減速/Charon)で改善が再現 ⑤Production判定注入で、改善wavがNG→PASS系に変わり、かつ負例canonicalの誤PASSが0。
- **REJECTED**: fixed < 3、または fixed<0.30×R(R≥6のとき)。
- **USER_DECISION_REQUIRED**: ①〜⑤のうち②が破れる(負例の誤Melos増≥1)が改善は①を満たす場合(トレードオフ)、または④が破れる(特定Voice/文脈限定)場合。
- 「1回だけの偶然」排除: 効果判定はwav単位の全rep一致で数える。揺れるwavは「不安定」として別枠に集計し、fixedに数えない。

## 3-v02 [v02] 指標と判定基準(委任_02b、実走前に固定。Opus_J M-4/M-5/S-3/S-8反映)

**主要指標=「本番判定のflip」**(Melos正認識率は副指標)。judgeは§2-Fの2 role条件で、各(wav,条件)のAzure転写(rep1)を注入して得る。
- **Primary-NG wav**: Azureを使わずに(Azure取得不能として)judgeを通してもPASS系にならないwav。Primary PASSのwavはAzure重みの影響を受けない(本番ではSecondary不要)ためflip集計から除外。
- **up(NG→PASS系)**: ベースライン(`pl_unspecified`)の状態がNG、重みwの状態がPASS/PASS_WITH_WARNING。**down(PASS→NG)**: 逆。rep間で状態が割れるwav(rep2抜き打ち)は「不安定」として別枠(up/downに数えない、件数は表に出す)。
- **R**=FULL_STORY roleで、正例(合成正例30+本番take20)のうちPrimary-NGかつベースラインがNGのwav数。
- **cluster**=(「文」, Voice, 減速有無)。「文」は合成=`sentence_id`、本番take=canonical sha。

**判定(効果判定はFULL_STORY roleが主、Tier3なしroleは副)**: 重みw(主=1.5、副=2.0はα/2)について、
1. **識別力**: R<6 なら`INCONCLUSIVE`(REJECTEDより優先)。
2. **効果量**: up ≥ 3 かつ up ≥ 0.30×R。満たさなければ`REJECTED`。
3. **有意性**: up対downの片側exact符号検定 p ≤ α(主1.5: 0.05、副2.0: 0.025)(例: up:down=5:0, 7:1, 9:2…)。満たさなければ`INCONCLUSIVE`(効果の兆候はあるが偶然と区別できない)。
4. **広がり**: upを出したwavが(文,Voice/話速)clusterで3種以上、かつ2種以上のVoice/話速条件。
5. **副作用なし**: 有効負例33wav(N1・N3+minimal pair 27)で、wの**誤PASS(canonical=Melos文を注入した本番判定がPASS系)とAzure誤`Melos`の件数がベースライン以下(増加0)**。これを**FULL_STORY・Tier3なしの両roleで**満たす。境界例(N2/N4)は別枠報告で判定に使わない。
6. **悪化なし**: down(PASS→NG)+「ベースラインMelos正認識→w誤認識」の和 ≤ 1 かつ < up/3。Melos以外の語の揺れで判定がNGに転じたケースはdownに含まれる。
7. **Tier3なしroleの非逆転**: Tier3なしroleでdown ≤ up(重みが同roleで逆効果でない)。
- 全てを満たす → `VALIDATED候補`。2,3を満たし4〜7のいずれかを破る → `判断候補`(トレードオフ/限定)。録音2(Phase A基準wav)は選択バイアスがあるため確認集計から除外し参考値で別記する。
- **全体Status**=主たる重み(1.5)の判定。1.5が`VALIDATED候補`でなく2.0が副基準(α/2)で全て満たす場合は`判断候補`(2.0のみ)。

**副作用指標(M-5)**: (wav,重み)ごとに、(i)新規誤り語数=重みwの転写にあってベースライン転写に無い、canonicalとの非ターゲット差分語数(Melos位置を除く)、(ii)うち保護対象(数値・否定・固有名詞[文頭以外の大文字語]・内容語[機能語表外])、(iii)本番判定のflip、(iv)Melos位置からの語距離、を記録する。

**S-8 5分類への対応(Closeoutの整理用の機械フラグ。閾値は`criteria_thresholds_01.json`の`diagnosis`)**: (a)条件が簡単すぎた=Primary-NG wavのうちベースラインがPASS系の割合が高い(R小)、(b)PLが効いていない=w1.5/w2.0の転写がベースライン転写と異なるwavの割合が低い、(c)1.0(=現行)で既に十分=`no_pl`→`pl_unspecified`でPASS系が増えw1.5で追加増がない/ベースライン成功率が高い、(d)文脈・音声品質で変わる=upがVoice・話速・文長の特定cluster/層に集中、(e)重みでは解決できない=R大かつw2.0でもNGが大半で転写の誤variantが残る。

**統計の注意**: 合成takeには「TTSが実際にMelosと発音していない」wavが含まれうる(Primary NGの一因)。その場合の`NG→PASS`flipは「誤発音の見逃し」になり得るため、flipしたwavは全件を試聴ページに載せ、minimal pair負例の誤PASS(§3-v02の5)で副作用を別途測る。

## 4. 試行数・費用見積 — v01(履歴)(単価: `er005_output/cost_baseline_01/pricing_snapshot.json` azure STT USD1.0/audio hour、160JPY/USD≒JPY0.0444/秒)

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

### 4-v02 [v02] 費用見積(委任_02b)
| 内容 | 呼出 | 秒 | JPY |
|---|---|---|---|
| Phase B 合成42wav×4条件(no_pl/pl_unspecified/pl_w1.5/pl_w2.0) | 168 | 約762 | 約34 |
| 追加負例minimal pair 27wav: TTS(18 take) | – | – | 約5.4(上限6) |
| 同 Primary(OpenAI gpt-4o-mini-transcribe)27 wav | 27 | – | 約0.7 |
| 同 Azure×4条件 | 108 | 約367 | 約16 |
| 本番take20×4条件 | 80 | 約837 | 約37 |
| 抜き打ち(w1.0 9 wav + rep2 9 wav×5条件) | 54 | 約190 | 約8 |
| 一般化probe(S-6) | 0 | – | 0(対象takeなし) |
| 合計 | 約410 Azure | 約2150 | 約101(Azure約95+TTS/Primary約6) |
- 本委任の上限はJPY200以内。案件合算=20.91(02a時点)+約101=約122で300円以下。R<6で追加take(§2-C-2)を行う場合の予備は上限内で確保(追加take≤24本×4条件≈JPY30未満)。
- 量産単価: 重み導入は`setWeight`1行でAzure呼出回数・秒数は不変=追加費用0(v01と同じ)。

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
- 2026-10-20 v02(委任_02b、**Phase B Azure実走前**、Opus_J=GO_WITH_CHANGES反映): 理由=Opus_J独立レビュー(`OPUS_REVIEW_J_01_VERBATIM.md`、sha256 26120a37…)。
  - M-1採用: judgeを本番相当(segment_id/CS層flag/force_secondary既定)で呼ぶ。golden replay test追加。Phase A再注入で`pl_w2.0`が旧NG_BOTH→FULL_STORY roleでPASS_WITH_WARNING(Tier3)と判明(`PHASE_A_RESULT_01.md`「v02再注入」)。
  - M-2採用: telemetry no-op、`is_last_slot=False`固定、副作用ファイルsize+mtime不変test。
  - M-3採用: N2/N4は境界例へ再分類、負例主軸=minimal pair 27 wav(§2-D-1)。有効負例33、rule of three併記。
  - M-4採用: 主要指標=本番判定flip、片側exact符号検定、cluster≥3、R<6→INCONCLUSIVE優先、録音2を確認集計から除外、悪化に他語揺れによるNG転化を含める(§3-v02)。`criteria_thresholds_01.json`をv02へ。
  - M-5採用: 副作用指標(i)〜(iv)、2 role条件の判定。
  - S-1採用: 本番既存take 20本を主評価集合(§2-D-2、選定規則を実走前に固定)。S-2: w1.0とrep2は約10%抜き打ち。S-3: 主=1.5、2.0はα/2。S-4: 自然には含まれない(PL対象名がMelosのみ)ため既定では追加しない。S-5: 1.25/1.75は実走しない(判断候補で報告のみ)。S-6: Closeout文言を「Melos・Family Z・2 Voice・ナレーター経路限定」とし、一般化probeは対象takeなしで0本。S-7: 新規wavのPrimaryは本番同一関数`er006_asr_provider_routing_01.transcribe`(OpenAI gpt-4o-mini-transcribe、prompt無し)、モデル名をrawに記録。S-8: eval出力を5分類へ対応(§3-v02)。
  - 補足採用: M1凍結の現在Ledger注記、Charon経路の制約、減速実測5.4〜5.9%、閾値jsonの正本化(§2-F)。
  - v01からの閾値変更の有無: v01の数値(fixed≥3、0.30×R、増加0、悪化≤1かつ<1/3、min_R=6、文脈2/Voice話速2)は維持。追加=符号検定、cluster≥3、role条件、負例分母33。**結果を見る前の変更**であり、Phase B実走前にcommitする。

- 2026-10-20 v02 実走後の記録(委任_02b、閾値・条件・選定規則は**不変**。変更は以下のとおり透明に記録):
  - (実装是正、11-8) S-8 (e)「重みでは解決できない」の分母: 事前登録文は「**R大かつw2.0でもNGが大半**」だが、eval_v02の初版実装はPrimary-NG正例全体を分母にしていた(文と実装の乖離)。分母をR(Primary-NGかつベースラインNGの正例)に是正した(閾値0.7は不変)。判定基準1〜7・Status判定には無関係(診断フラグのみ)。testで固定。
  - (記述的追加、判定に不使用) PL自体の価値(no_pl→pl_unspecified のflip)、重みが新たに作った誤PASSの転写表、文脈別/Voice別/長さ別のMelos正認識数(§3b)をevalに追加。事前登録した判定基準・閾値は変更していない。
  - (運用事故) Phase B runnerが最初の5呼出の後、SDK診断ログ削除(`os.remove`)のWindowsファイルロックで例外終了(原因既知=Trial harness側のバグ、Azure側error・外部停止ではない)。削除をtry/except化し終了時に掃除する修正のみ行い、skip-existing(`done_keys`)で未実施の405呼出だけを再開(1回の再開、重複呼出0: raw 410行=一意(audio_id,cond,rep)410)。
  - Phase C(追加take): §2-C-2の発動条件(R<6)に該当しない(R=9)ため未実施。
