# STAGE2_TRIAL_RESULT_01: 固有名詞発音 Stage 2 Trial 第1巡 結果(ユーザー§7の順)

管理ID: PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_07 / 2026-10-22 / 到達Status: `TRIAL_R1_DONE_PENDING_FABLE`(`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`はFable判定)。Production・正式Ledger・Validator・Prompt・モデル構成・Phrase List 無変更、Trial成果の正式Ledger登録0。
設計=`STAGE2_TRIAL_DESIGN_01.md`。証跡=`er100_output/pnps_stage2_trial_01/`。試聴ページ=https://shimomura055.github.io/eigo-radio/user_test/pnps_stage2_hr7_listen_01/index.html

## 1. 結論: Human Reviewを何件削減できたか
- **保存データ上の削減は実質0〜1件(58件中)**。辞書外7語に絡む保存HR事象58件のうち、新方式(v4受理条件=V4、Trial内の拡張比較=EXT)で警告付き自動PASSに変わったのは**1件(Khaite、2026-09-27 16:03の事象)のみ**。残り57件はHR維持(うち10件は新方式でもNG判定、47件は推定不成立/判定不能)。
- その1件も「正解」の確証はない: 当該事象の音声は再生成で上書きされ保存されておらず(耳で確認不能)、同じ記事・同じ語の保存attempt音声では、Production ASR(OpenAI Primary)が「Kate」と書いた3本をローカルWhisper(small/medium)は2本とも「kite/kites」と書いて食い違う(後述§3)。Whisperの一致を要件に加えるとPASSは**0件**になる。
- 一方、**現行のTTS(Gemini 3.8 flash-lite、Family X標準)で今回新規に生成した14本**では、Khaiteが2本とも4エンジン全部「Kate」と一致し、新方式で警告付きPASS(2/2)。つまりKhaiteは「現行TTSなら読みは正しい可能性が高く、旧モデル(gemini-2.5)時代のHR事象が古い」という側面が強く、新方式の効果というよりTTS側の改善が効いている可能性がある。
- 結論: **今回の方式(取得・推定した発音をASR転写のCMU音素と照合する方式)では、Human Reviewは意味のある量では減らない**。理由は§4・§5。ユーザー§4に従い、ここで終了せずStep A(原因分析)と代替案を示す。

## 2. 対象母数・現行HR件数・改善後HR件数(3区分を分離)
| 区分 | 件数 | 備考 |
|---|---|---|
| HR queue 全行(Family X/Z) | 113行 | `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl` |
| 辞書外7語に絡むHR事象(segment単位の行) | **58行** | 他に未解決spanを持つ行3行(Kallmeyer等) |
| 延べlookup(行×語) | 61 | toteme7 khaite10 altuzarra3 zabelina1 canele2 meink2 melos36 |
| 独立segment(canonical本文) | 30 | Melos 28行は同一segment(c5)の繰り返し。(語,segment)別は33 |
| 独立音声: HR事象時の最終wav | 保存22本(25パスはTemp削除で未保存)。保存ありのHR事象は33行、未保存25行(全Melos) | 保存最終wavは後の再生成で別世代のものがある(§3の注) |
| 独立音声: 保存attempt音声(ER-011保持) | **86本**(sha256別86、gemini-2.5-pro-preview-tts 58 / gemini-3.8-flash-lite-tts 28、うちProduction合格19) | 95語ペア |
| 新規生成(P2、今回) | 23本(綴りどおり14本+制御読み9本)+途中中止2本(誤ったprompt形式、破棄) | 今回のTTSモデルの読みの実測 |
- 現行HR=58事象 → 新方式V4/EXT後=**57**(PASS_WITH_WARNING 1、NG 10、HR維持47)。独立segment 30 → 29。Whisper一致を要件に加えた場合は58のまま。
- 「実際の発音不良とASR誤認識の区別」: 機械的な**候補**ラベルのみ(確定は耳)。58事象のうち、全ASRが同一の別語を出力=「TTS実誤発音の候補」8、ASR間で割れる/一部が正しい綴り=「ASR誤認識・不安定の候補」多数、2通りに割れる=不明。語別は試聴ページとRESULT§5。

## 3. 誤PASS・誤NG
- **誤PASS(明確な誤発音をPASS)**: 制御読みの負例(実TTS)6本(Khaite「Kite」「Kay-tee」、Meink「Mink」「May-ink」、Altuzarra「Al-tuh-ZAIR-ah」「Alt-oo-zarr」)で**PASS 0**(NG 2、判定不能=HR維持4)。保存データ上の新規誤PASSは**確認できた範囲で0**。ただし次の留意点がある。
  - 保存事象の1件(Khaite)は音声が残っておらず耳での確認不能(確証なし)。
  - 保存attempt 3本(Khaite、旧モデル)は「Production ASR(Primaryのみ観測)=Kate」で警告付きPASSだが、Whisper small/mediumが2本とも「kite/kites」と書き、**誤PASSの疑い(要試聴)**。Whisper一致を必須にすると0。試聴ページで耳確認可能。
  - 診断arm(DIAG_UNION=全候補の和集合)ではMeink事象(ASR「mink」)がPASSになる。Wikipediaは「MEENK」としており、和集合の受理は誤PASSの余地がある実例。EXT/V4には採用していない。
  - V4(G2P∩LLM)の共通部分はMeinkで「M AY NG K(マイン-ク)」に収束したが、取得できたWikipediaの読み(MEENK=M IY NG K)と**食い違った**。推定の一致が取得情報と矛盾し得るため、EXTでは「取得根拠があれば推定は上書きされる」としている(V4単独では誤受理の余地が残る)。
- **誤NG(正しい発音をNG)**: 真の正否の根拠が無いため測定不能。観測された例: Meinkの「合理的な読み」の制御入力「Meenk」はTTS→ASRで全エンジン「mink/mank」となりNG(入力どおりの読みが出ていない可能性。耳で確認が必要)。NGは現行でもHRなので、新方式のNGがHR件数を増やすことはない。

## 4. Web取得と合理的発音推定、それぞれの成功・失敗理由
**Web取得(O1+R0、無料。HTTP GETのみ、読み取り専用)**: 7語でHTTP GET計163回(O1の134回[Wikipedia/Wiktionary/Wikidata/既存調査の出典URL]+R0抽出の29回、成功はO1で104回)。Wikidata P898(IPA)=0件、Wiktionary英語項目の発音=0件(Canelé/Melosの別言語項目のみ)。取得できたのは4語:
| 語 | 取得した発音 | 出典 | 区分/問題 |
|---|---|---|---|
| Meink | /miːnk/ MEENK → M IY NG K | Wikipedia「Troy Meink」冒頭(同定=本人記事) | 許可リストA相当。**実際の呼ばれ方に近い一次級**。ただしTTS/ASRの比較が困難(§5) |
| Altuzarra | ahl-too-ZAH-rah → AA L T UW Z AA R AA | Business Insider / Nylon / Elle AU / HerWorld / Bustleの媒体ガイド5件が一致 | 媒体合意(許可リスト外)=B階層。綴り読み形式で従来の抽出器はIPAしか拾えず取得不可だった(Step A「抽出不可」) |
| Khaite | "kate" → K EY T | Nylon発音ガイド1件 | B階層(単一媒体)。E2/E3も一致 |
| Canelé | /kænəˈleɪ/ → K AE N AH L EY | youpronounce.it(辞書サイト、許可リスト外) | 単一サイト=弱い。E2(G2P)と不一致 |
取得できなかった: Toteme(22ページ本文を確認、発音記載なし)、Zabelina(人物発音の出典なし)、Melos(辞書IPAは普通名詞/島Milosのもので、『走れメロス』の登場人物と同一と確認できない=同定未確認)。
**合理的発音推定(E2 G2P=`g2p_en`、E3=`gpt-6-luna`web無し)**: 7語のうち共通部分が収束したのはKhaite(K EY T)とMeink(M AY NG K)の**2語のみ**。他5語はG2PとLLMの母音が割れて共通部分が空(Toteme: T OW T IY M vs T OW T EH M、Altuzarra、Zabelina、Canelé、Melos)。Meinkは収束先が取得発音と食い違った(§3)。失敗理由=2推定とも綴り規則に依存するが細部(母音の弱化・外来語の語尾)で割れる。
**自動判定の限界(最大の原因)**: 受理集合がある語でも、ASRが辞書外の綴り(altazara, kanele, zebelina…)で書くとCMUで音素にできず判定不能。保存データの観測のうちCMU比較可能170、OOV 33、正しい綴りそのまま9(Melosの未観測54を除く)。新規14本×4エンジンでは比較可能12、OOV 28、正しい綴りそのまま16(56観測)。同一音声でもToteme: toteme/totême/tateme/teteme/tautame、Altuzarra: altuzarra/altazara/altuzara…と**エンジン間で綴りが割れる**。さらにOpenAI Primaryは誤った読み(Altuzarraの明確な誤読2本)でも正しい綴り「altuzarra」を返し、Primary一致だけでは証拠にならない。

## 5. 初回で効果が限定的だった原因(Step A)と、Opus指摘・改善・再Trial
(Opus指摘・改善・再Trialは未実施。Fableが手配。以下はStep Aの原因分析と証拠。)

### 5-1. 語×音声単位の原因分類(証拠はreplay_result.json / est_e2_e3.json / r0_extractions.json / p2_results.json)
| 語 | HR事象(保存音声あり) | 主因(ユーザー例示の分類) | 証拠 |
|---|---|---|---|
| Toteme | 7(7) | **Web上に発音情報なし**/**G2PとLLMの推定が不一致**/音素照合で不合格/TTS実誤発音の候補 | O1で22ページ取得し発音記載0。E2 T OW T IY M ≠ E3 T OW T EH M。ASR「totem」(T OW T AH M)は両方に不一致、4事象は全6エンジン同一「totem」=TTSが「toh-təm」と読む候補(期待発音が未確定で断定不可)。現行TTSの新規2本はPrimary/Azureが「Toteme」と書きWhisperは割れる |
| Khaite | 10(10) | **音素照合でNG(8)=TTS実誤発音の候補(旧モデル「kite」)**/1件PASS/1件ASR判定不能 | 取得「kate」+E2=E3 K EY T。ASR「kite/kites」(K AY T)が8事象。現行TTS新規2本は4エンジン全て「Kate」→PASS |
| Altuzarra | 3(3) | **情報はあるが従来は抽出できない**/**G2PとLLMの不一致**/**出典の信頼性(媒体=B階層)**/ASRがCMU未収録で比較不能 | 媒体5件が「ahl-too-zah-rah」(R0抽出器を新設して取得)。E2 AA L T UW T AO R AH ≠ E3 AE L T UW Z AA R AH。ASR altazara/altuzara等はOOV |
| Zabelina | 1(1) | **Web上に発音情報なし**/G2PとLLMの不一致(IHとAHの弱化)/複数の合理的候補を扱えない | 出典は人物記事のみ。E3は2候補、E2は1つで共通部分なし。ASR「zebelina」OOV |
| Canelé | 2(2) | **出典の信頼性で落ちる(単一辞書サイト、許可リスト外)**/G2PとLLMの不一致/ASR誤認識の候補 | youpronounce /kænəˈleɪ/(E3と一致、E2と不一致)。Primary「kanele」(k綴り)、Secondary/Whisper「canele」(正しい綴り)=ASR間不一致 |
| Meink | 2(2) | **取得できたが推定の共通部分が取得発音と矛盾**/音素照合NG/実TTS不明 | Wikipedia MEENK(M IY NG K)。V4はM AY NG K。ASR「mink」(M IH NG K)は両方に不一致→NG。制御読み「Meenk」もASR「mink/mank」=入力どおりに読めていない可能性 |
| Melos(Family Z) | **36(11)** | **同定未確認(出典は普通名詞/島)**/G2P≠LLM/音素照合不一致/TTS誤発音の候補 | 36行は8segmentで、1segment(c5)が28行の反復。25行は音声未保存。ASR mello/mellow(M EH L OW)は受理集合に無い。現行TTS新規は4エンジン「Melos」(Productionでも通る読み)と「mellows」に割れる |

### 5-2. 全体の原因(分類別件数、61 lookup=58事象[3行は2語を含む])
- 受理集合が空(推定不成立): Toteme7+Zabelina1+Melos36=**44事象**(76%)。
- 受理集合はあるがASRがCMU未収録/整列不能で判定不能: Altuzarra3+Canelé2+Khaite1=**6事象**。
- 音素照合でNG(うちTTS実誤発音の候補が多い): Khaite8+Meink2=**10事象**。
- PASS_WITH_WARNING: **1事象**(Khaite、音声未保存)。
- 時期別: Family X旧(2026-09-04〜28、旧モデル主体)22事象(25 lookup)+Family Z Melos(10/12〜22)36事象。Melosの36は同一segmentの繰り返しが大半で、**独立なHR圧力はMelos 8segment**。

### 5-3. 改善見込みの高い代替案(事実ベース、最大3つ。採否はFable/Opus)
1. **取得できた発音を判定側でなくTTS側の生成に使う(TTS-safe綴り置換)**: Khaiteで「Kate」入力は4エンジン全一致(P2)。取得できたのは3〜4/7語(Altuzarra/Khaite/Meink+弱いCanelé)。限界: Altuzarraの置換入力でもAzure/Whisperは綴りが収束せず、検証側は依然判定不能(P2: altazarra/altuzara)。Production既存の置換機構との整合・ESTIMATEDを供給しない原則(v4-5)との関係は未確認。改善見込み: 中(HRの原因が「TTS誤読」の語に効く。「判定不能」には効かない)。
2. **ASR綴り経由をやめ、音声から直接音素を認識して候補集合と照合する(wav2vec2系の音素認識など、ローカル・API費0)**: 根拠=同一音声のASR綴りがエンジン間で割れ(§4)、OOVが観測の約半数(新規56観測中28)で、ASR綴り→CMUの経路が判定の天井。未導入(torch・約1GBのモデル)で精度は未測定、導入と評価が必要。見込み: 高い上限だが不確実(音素誤り率とNG検出力の測定が先)。
3. **複数ASR(Primaryを除く独立2エンジン以上)が同一の綴りを返すこと+Whisper一致を条件にする**: PrimaryがAltuzarraの誤読でも正しい綴りを返す実測があり、Primary単独は不可。Azure+Whisper small/mediumが同じ綴りを返す語は限定的(新規56観測でEXACT 16)。見込み: 低〜中(効く語が少ない)。承認済みの自動PASS条件の変更に当たる。
- 追加の事実: 現行TTS(gemini-3.8)では旧モデルのKhaite「kite」問題が再現せず(2/2 Kate)、HR原因の一部はTTSモデル更新で自然に解消している可能性がある。母集団は小さい(各語2本)。

## 6. 使用総額・量産単価への影響
- 使用額: **JPY15.54**(`paid_calls.jsonl`): E3(gpt-6-luna、7呼出)0.272、P2のTTS(Gemini 3.8 flash-lite TTS、25呼出[うち2は中止した誤prompt形式])4.622、OpenAI ASR 2.819、Azure STT 7.829。単価の出典: gpt-6-luna=pricing_snapshot.json、Gemini TTS=同(入力$0.5/M・出力$6/M[25 tok/s])でtoken数は概算、Azure STT=$1/audio-hour(snapshot)。OpenAI ASRはtoken単価のみ登録で秒当たり換算が**未確認のため上限見積($0.006/分)**。為替=プロジェクト既定USD_JPY=160(`er009`)。
- Cap: 累計300円のうち使用15.54、**残284.46**。本巡Guardrail150のうち残134.46。当日(JST 2026-10-22)累計=委任文の既使用約482に、その後に完了した別委任KPMG1(188.28、`docs/pm/ACTIVE_TASK.md`先頭の記載)と本巡15.54を加えた**約686/1,000円**(本巡開始時点の約482+本巡15.54=約497.5だが、並行完了分を加算)。
- 量産単価への影響: 追加費用は新規に調べる語1つあたりE3 約0.04円(実測0.272/7語)、G2P・HTTPは0円。削減側は今回の保存データでHR 58→57(自動PASS+1)で**ほぼ0**。1記事セット当たりの影響=悪化≤約0.04円×新出現語数(未測定)、改善は測定可能な水準に達せず(0に近い)。70円目標への影響は小さいが、削減が無いので純改善ではない。**未測定**: 記事あたりの新出現辞書外語数、旧モデル事象が現行モデルでどの程度再発するか。

## 7. Fable独立評価、Trial終了Status
(Fable記入欄)到達Status=`TRIAL_R1_DONE_PENDING_FABLE`。Opus独立レビュー(Step B)の要否はFable判断。

## 8. Production採用に必要なユーザー判断
(Fable記入欄)現時点で本巡の結果から新規にユーザー判断が必要な事項は無い(Production採用の段階ではない)。参考: EXT arm(許可リスト拡張・媒体合意・単一サイト+推定一致)の採用、およびWhisper一致の要件化は承認済み出典階層・自動PASS条件の変更案であり、採用前にユーザー判断が必要(Step C以降)。

---
## 付録
- 導入: `.venv\Scripts\python.exe -m pip install g2p_en`(g2p-en 2.1.0、nltk 3.10.4、numpy 2.5.1、inflect 7.6.0 ほか依存)。Trial専用でProduction importに入れていない。nltkデータ(averaged_perceptron_tagger_eng, cmudict)は初回に自動取得。
- 再現: `er100_pnps_stage2_trial_01_{o0,whisper,attempts,o1,r0,est,replay,attempts_replay,p2,stepa,page}.py`。
- 限界の開示: (1)保存最終wavは再生成で上書きされた別世代があり、ASR欄はHR事象時点のもの(同世代判定は保存時刻とHR時刻の差≤150秒)。(2)attempt音声のASRはPrimary(一部cascade)のみで、Secondaryが無いものがある。(3)「区別の候補」は機械ラベル。(4)Melosはidentity未確認。(5)P2は各語2サンプルで統計的な評価ではない。
