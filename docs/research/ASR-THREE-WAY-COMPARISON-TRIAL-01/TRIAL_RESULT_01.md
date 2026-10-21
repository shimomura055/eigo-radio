# TRIAL_RESULT_01 (ASR-THREE-WAY-COMPARISON-TRIAL-01 委任_01、2026-10-21)

Sonnetは分類のみ(判断候補表記)。Statusラベル(VALIDATED/REJECTED/USER_DECISION_REQUIRED)はFableが付与する。VALIDATEDでもProduction採用・配線ではない。
実行: `er091_asr_three_way_trial_01_{dataset,tts_construct,splice,run,analyze,phase3,takepart10,report,docs}.py`(各有料runは1回、再起動なし)。証跡: `er091_output/asr_three_way_trial_01/`(dataset_manifest.jsonl / results/asr_raw.jsonl[全転写・wall・CPU・トークン] / results/phase12_item_results.{json,csv} / results/phase3_item_results.{json,csv} / results/takepart10_phase3.json / results/summary.json / results/tables.md / paid_calls.jsonl / tts_construct_log.json / splice_log*.json / stop_check*.json)。詳細表=`RESULT_TABLES_01.md`、台帳=`DATASET_01.md`、設計=`TRIAL_DESIGN_01.md`(実行前commit b6aa90711)、再利用表=`PRIOR_WORK_01.md`。
Production code・Prompt・閾値・Ledger・Master Store・記事成果物・共有ログは無変更(Trial dirのみ書込)。

**使用モデル(25節)**: 3方式はProduction同一(比較目的の例外): OpenAI `gpt-4o-mini-transcribe`、Azure Speech STT en-US(SDK 1.50.0)、faster-whisper `small` cpu int8。追加: faster-whisper `medium` cpu int8(smallの誤りが容量由来と実測で示されたため1サイズ追加。結果§J)。TTS: Gemini `gemini-3.8-flash-lite-tts`(Production同一、新規8本)。LLMによる採点は不使用(機械的な正規化比較とProduction判定関数)。最新か: 各社の現行ProductionモデルであることをSSOT(`er006_asr_provider_routing_01.py:31`等)で確認したのみで、各社の最新世代かの外部確認はしていない。

## 費用(出典付き)
- ASR API実費 JPY**44.96**(`paid_calls.jsonl`集計: OpenAI 167呼出 JPY3.85[実トークン入力10,035/出力2,308 x $1.25/$5.0 per M、`er005_output/cost_baseline_01/pricing_snapshot.json`、JPY160/USD=`er078_asr_unified_judge_01.py:80`]、Azure 155呼出 JPY41.11[音声828.97秒、ceil秒x$1/h、`er078_asr_unified_judge_01.py:110-113`。正確秒数式なら約JPY36.8])。
- 新規TTS 8本 JPY**0.17**(`tts_raw_usage_log.jsonl`のcost_jpy合計、Gemini batch、8呼出・各1回・retry0)。
- 合計 約**JPY45.1** / T-3 Guardrail JPY250の約18%。日次(JST): S0実測 adopted 350.42 → 最終実測 adopted 387.18(`daily_dev_cost_01.py --date 2026-10-21`、並行2件の支出を含む)で1,000円に余裕あり。見積(S1時点)JPY約40〜60に対し実績45。

## 1. 結論: どのASR構成が最も有望か(判断候補。確定ではない)
1. **現行の構造(OpenAI Primary → Azure Secondary)を維持し、Key Phraseに限って『Azureの拒否権』を足す案(C1dK=KPのみPrimary PASSでもAzure許容集合PASSを必須、または C5K=KPのみWhisper不一致時だけAzure必須)が、本Trialで最も根拠が強い。**根拠: ①『take part』旧NG音声10回の転写に各構成を適用すると、OpenAIの合意でPASSできる構成(C1/C2/C3)は**3/10で見逃し**(OpenAIが言語priorで『part』に補正)、Azureの拒否を必須にする構成(C1d/C4/C5)は**0/10見逃し**(§I)。②KP正常28本での過剰NGは0〜1件(C1dK 1/28[Wilson 1〜18%]、C1 0/28[0〜12%])。③追加原価は1記事セットあたり約JPY0.8(KP10音声x約JPY0.09)・検査時間+約4秒(§H)。**ただしこれはProduction仕様の変更(新仕様)であり、本Trialは推奨実装ではなく判断材料の提示。**
2. **Primaryの入替(Azure Primary=C2、Whisper Primary=C3/C4/C3m/C4m)は、本Trialの証拠では現行より明確に良いと言えない。** Azure Primaryは1記事ASR原価が約JPY18(70円目標の約26%、現行約6)で、Phrase List(重み2.0)に引かれた『Mullos』→『Melos』をPrimary段で誤PASSにする(Secondaryを経由しないため)。Whisper Primaryはsmallで容量由来の誤り(『weaken』→『WEEKEND』等)があり、mediumで解消するがCPU負荷(1記事約1,700 CPU秒)・時間(直列約270秒)が大きく、本文のHR難例では過剰NGが残る(8/11)。API原価の削減幅は約JPY0.7/記事で、リスクに見合うか不明。
3. **ASR単体の優劣は『種類別』に分かれ、単純ランキングは出せない**(§3)。Production条件のKP正常PASSはOpenAI(Production prompt付き)28/28・Whisper medium 28/28・Azure 27/28・Whisper small 26/28。固有名詞・HR難例の本文はAzure(Phrase List付き)が最も通すが、その分『Mullos』型の誤PASSも増える。誤発音の検出は4方式ともKP問題8/8(既知NG1+構成5+splice2)で差が出ず、差は『OpenAIが補正して見逃す確率』『Phrase Listが引く方向』という確率・偏りの違いに現れる。
4. **統計的な限界(必ず併記)**: 正常KP n=28、問題KP n=6(うち人間聴感1本、残りは構成ラベル)、本文の通常記事音声 n=24、HR難例+構成正常 n=11、本文問題 n=12(全て構成ラベル)。構成間の過剰NG差は0〜2件で有意差と言えない(Wilson区間が大きく重なる)。構成ラベルの問題音声は人工分布で、実運用の誤発音分布を代表しない。

## 2. 正常音声のPASS率・誤発音検出率・誤PASS率・過剰NG率(Phase 3、Production判定関数経由)
区分別(`RESULT_TABLES_01.md` G-4、Wilson95%区間):

| 構成 | KP正常 過剰NG | KP問題 誤PASS | 本文 通常記事音声(HR難例除く) 過剰NG | 本文 HR難例+構成正常 過剰NG | 本文問題(構成ラベル) 誤PASS |
|---|---|---|---|---|---|
| C1 現行 OpenAI→Azure | 0/28 [0-12%] | 0/6 | 0/24 [0-14%] | 5/11 | 2/12 |
| C1dK KPのみ両方PASS必須 | 1/28 [1-18%] | 0/6 | 0/24 | 5/11 | 2/12 |
| C1d 全音声で両方PASS必須 | 1/28 | 0/6 | 1/24 | 5/11 | 2/12 |
| C2 Azure→OpenAI | 0/28 | 0/6 | 1/24 | 5/11 | 2/12 |
| C3 Whisper small→OpenAI | 0/28 | 0/6 | 2/24 [2-26%] | 6/11 | 1/12 |
| C4 Whisper small→Azure | 1/28 | 0/6 | 0/24 | 4/11 | 2/12 |
| C5 / C5K 現行+Whisper不一致時Azure必須 | 1/28 | 0/6 | 0/24 | 5/11 | 2/12 |
| C3m Whisper medium→OpenAI | 0/28 | 0/6 | 0/24 | 8/11 | 0/12 |
| C4m / C5m | 0/28 | 0/6 | 1/24 | 4〜5/11 | 2/12 |

- **誤PASSと過剰NGは混ぜない**。誤PASS(問題音声がPASS)実例: ①`plw_NM_P3_mullos`/`plw_NM_P4_mullos`(『Mullos』と読ませた音声)がC1で`PASS_WITH_WARNING secondary_confirmed`: Primary『Mellos』『Molos』→NG、Azure(Phrase List『Melos』重み2.0)が『Melos』と転写し許容集合PASS(旧Trialが指摘した副作用[ユーザーが承知のうえ採用、OPEN-426]を独立に再現)。C2ではAzureがPrimaryなのでPrimary段で`primary_pass`(Secondaryを経由しない)。②スプライス欠落音声(`spl_body_almost_deleted`等)は3方式とも語を復元して転写(**ラベル確度が低いためheadlineから除外**。切断断片が残る可能性がありlabel不確実。詳細は§9)。③『take part』は今回の4音声では全構成で検出(OpenAIの今回4回は4/4『tart』)だが、旧Trial10回ではOpenAIが3/10『part』=C1/C2/C3の見逃し(§I)。
- 過剰NG(正常音声がNG)実例(C1): HR承認済みの`hr_run_e2e_04`(『Melos drank』→Primary『He drank』)、`hr_run_e2e_02`(『Melos said』→Primary『Mellis』・Azure『Mallow』)、`hr_space_weapons`(Troy Meink)、`hr_tiny_bags`(Toteme/Kallmeyer)、`plw_P1`(Melos drank→『Mellos drink』/『Mellow strength』)。**これらは過去に実際にHRへ回った種類**(固有名詞/語境界)と一致し、Phase 3 wrapperが実運用の傾向を再現している傍証(現行コードは当時と異なるため一致は保証ではない)。KPの過剰NGは『sentence someone to death』(Azure/Whisper small『Sentenced』、C1d/C4/C5で1件)のみ。
- 単独ASR(Phase 1/2、Production分類器を転写に適用、`RESULT_TABLES_01.md` C・D): Production条件でKP正常PASS OpenAI 28/28・Azure 27/28・Whisper small 26/28・medium 28/28、KP問題(構成/既知NG 6+splice 2)の検出は全方式8/8。本文の正常(N_human 29本)PASSはOpenAI 19/29・Azure 23/29・Whisper small 22/29・medium 21/29(HR難例5本を含み、**単独方式の通過率でありProductionの救済込み最終判定ではない**)。

## 3. Key Phrase / 本文 / 固有名詞 / 数字等の種類別(Production条件、正常PASS率 / 問題NG検出率。`RESULT_TABLES_01.md` D)
- KP短文・単語・3語以上: OpenAI(Production prompt付き)100%、Azure 100%/100%/91%、Whisper small 89%/100%/91%、medium 100%/100%/100%。Production promptの有無でOpenAI KP正常PASSは82%→100%(prompt無し23/28→有り28/28)。
- 固有名詞(正常27本、問題9本): 正常PASS OpenAI 52%・Azure 81%・Whisper small 67%・medium 63%、問題NG検出 OpenAI 100%・Azure 78%・small 89%・medium 100%。**Azure Phrase Listは通過率を上げる(PL有14本: PLなし21%→重み2.0で57%)が、問題検出は90%→80%に下がる**(『Mullos』型誤PASS 1件増)。
- 数字(正常12本): OpenAI 58%、Azure 67%、small 67%、medium 58%(『5』『five』『13』等の表記差が転写に出る。誤発音検出は構成ラベル『thirteen days』1本が全構成で検出)。否定(正常12本)58〜75%。同音異綴り/複合語: 『far bank』→OpenAI/Azure『Farbank』(despace等価でPASS)、『hold out』→OpenAI『Holdout』、『weaken』→small『WEEKEND』(mediumで『Weaken』)。連結発音/長文: body_long 8本は38〜50%と低い(長文は句読点・数字・固有名詞のどれかで単独方式では通りにくく、Productionでは救済層で通る)。
- Family X / Z: 正常PASS X 83〜90% / Z 67〜85%(Zは固有名詞Melos由来でOpenAIが最も低い)。Std / Adv: Std 66〜85% / Adv 82〜95%(Stdに固有名詞HR難例が偏在=構成の偏り)。

## 4. 3方式の安定性と実例(同一音声の反復=独立音声ではない)
- 短尺KP 20本x3回(Production条件): **Azure 20/20、Whisper small 20/20が3回とも同一転写**。OpenAIは6/20音声で転写が揺れたが、揺れは大小文字・句読点・空白のみ(『Meanness』/『Meanness.』、『Stone Video.』/『Stone video.』、『Intercept』/『intercept』、『Take tart.』/『TakeTart.』)で、**PASS/NG判定の反転は20音声中0**。
- ただし『take part』旧NG音声(旧Trial 10回)ではOpenAIが『part』x3/『tart』x6/『heart』x1と**内容語が揺れ判定が反転**(Azure 10/10・Whisper 10/10は不変)。本Trialの今回4回は4/4『tart』。**反転が起きるのは『言語priorが強く、音響が曖昧な語』に限られると推定(1音声の観測、一般化不可)**。
- Whisper: 決定論的(seed不要、CPU int8)。Azure: 同一音声で実用上同一。

## 5. 処理速度・原価(1記事セット換算。記事B構成: KP10音声[11.5秒]+英語本文15セグメント[388.7秒]。前提と式は`RESULT_TABLES_01.md` H)
- 実測の処理時間(1音声): KP平均 OpenAI 0.65s / Azure 0.72s / Whisper small 1.81s / medium 5.30s。本文は回帰で OpenAI 0.67+0.034x秒、Azure -0.17+0.45x秒、small 1.52+0.128x秒、medium 4.20+0.392x秒(x=音声秒)。API方式は6スレッド並列で221呼出が69秒(実効0.31秒/呼出)。Whisperはsmall/medium自身が複数コアを使い(CPU 1.47 / 4.23 CPU秒/音声秒)、別process同時実行は2並列で全体36.5秒(モデルロード込み、直列合計43.7秒はロード別)・4並列でも同等=**同時実行の短縮は約17%程度にとどまる**(16論理CPU、他agent並走下の値)。
- 1記事セット(直列合計の目安): C1 現行 84秒・ASR原価JPY約6.2(Secondary率: HR難例を含む本Trial母集団では本文31%、HR難例を除く通常本文では約17%[4/24]のため約3〜6円)/ C1dK 88秒・JPY約6.9(+約0.8)/ C2 180秒・JPY約18.5 / C1d(全音声両方PASS)207秒・JPY約19.1 / C3 95秒・JPY約0.14(CPU約590秒)/ C4 125秒・JPY約3.7 / C5K 101秒・JPY約6.2 / C3m 266秒・JPY約0.11(CPU約1,694秒)。**70円/記事セット目標に対し、ASR API原価の差は最大でも約JPY18で、構成選択の主因は原価ではなく品質(見逃し/過剰NG/HR)と運用負荷**。
- 過剰NG由来のTTS再生成費用: 本文15セグメントの通常記事音声レートで期待数は0〜0.62件、追加TTS原価はStandard単価で約JPY0〜0.4(Batchは半額)=無視できる。**実質的なコストはHuman Review/再生成の回数と時間**: HR到達期待(独立仮定の下限〜過剰NGが全枠NG確定の上限)はC1 0〜0、C1dK 0〜0.36件/記事、C1d 0.001〜0.98(KP4枠・本文3枠想定)。HR難例(固有名詞)は全構成で過剰NG 4〜8/11と高く、**Family Z/固有名詞多用記事ではHRが構成に関わらず発生する**。
- ローカルWhisperの運用負荷: CPU飽和(他の生成・検査と競合)、モデル配布・バージョン固定、出力形式差(二重空白: 下記§6)。API障害時のfallbackとしての独立性は利点。

## 6. Primary/Secondary入替の利点・リスク(現行ルールをそのまま使えない点を含む)
- **Azure Primary(C2)**: 利点=転写が決定論的、固有名詞(Phrase List付き)の通過率が最も高い(81%)。リスク=①Phrase List重み2.0がPrimary段で誤PASSを通す(『Mullos』→『Melos』2/2、Secondary確認を経由しない)、②ASR原価が約3倍(約JPY18/記事、目標の26%)、③Production規則の前提がずれる: `unified_judge`はPrimary PASSで即PASS(`er078_asr_unified_judge_01.py:436-441`)でSecondaryの拒否権が無い、Tier1/baseline/CMU同音救済は『OpenAIのprior補正を前提にした救済』、Azure転写を前提にした救済調整はない。
- **Whisper Primary(C3/C4/C3m/C4m)**: 利点=API原価ほぼ0・OpenAIのpriorと独立。リスク=①small単独は容量由来の誤り(13件の単独NGのうち6件をmediumが解消=改善例は`weaken`/`Sentenced`/`Melos`系)で、mediumは時間・CPUが約3倍(CPU 4.2秒/音声秒)、②**出力が二重空白を含む**(『Take  Tarte.』)ため、空白を畳まないと`max_len`(`len(asr_text) <= max_len`)で人工的な長さNGが出る(本Trial初回の空白未処理でC3の正常過剰NGが11件、畳み後8件=+3件)。TrialではProduction判定関数に渡す前にwrapperで畳んだ(Production側は未変更=実装するなら正規化規則の新設が必要)、③Primary側の規則(Tier1・B1連結・CMU・M1)はOpenAI出力の癖を前提に調整されている。本Trialでは現行ルールを流用した値のみ(新ルール設計はしていない)。
- **Secondary許容集合の定義**: Production Secondaryは`classify_asr_match`+`_step_alternate_pass`(CMU同音/Case A)+M1(`er006_secondary_asr_01.py:993-1010`)で、転写元がAzureでもOpenAIでも同じ関数が使える(技術的には入替可)。ただし『Secondaryが合意すればPASS』という設計上、**OpenAIをSecondaryにするとOpenAIのprior補正がそのまま救済になる**(C2/C3で『take part』が3/10通る)。
- **entity救済・M1・low_ratio 0.98**(`er006_preprod_hardening_01_validation.py:1016,1228`の`high_similarity_threshold=0.98`): 入替時に別転写へ同じ閾値が適用される。本Trial範囲では閾値・規則を変更せず、現行ルール流用の参考値として結果を出した。

## 7. 現行Productionと候補構成の差分
- 現行(C1): KP=OpenAI(Production prompt)→NGのときだけAzure(PL有ならw2.0)。Primary PASSならSecondary不要。
- C1dK(KP限定dual): 差分=KPのみ`force_secondary=True`相当(Primary PASSでもAzure許容集合PASSを必須)。既存`force_secondary`機構(fallback音声用)の対象拡大で実装でき、新ルール追加は最小。ただし**新仕様=Production挙動の意味的変更**(`FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01`の案と同一系)。
- C5K(KP限定・Whisper起動): 差分=KPにWhisperを常時実行し、不一致のときだけAzureを必須化(原価増ほぼ0、CPU 1.5秒/KP)。Whisper smallの転写がcanonicalと乖離しないとAzureが起動しない(=Whisperが同じpriorで補正する語を見逃す)ため、見逃しの上限はWhisperの検出力に依存する。
- C3/C4等の入替: 上記§6の追加規則が必要。

## 8. Fable独立評価(Fable記入欄。以下はSonnetが自己申告する限界のみ)
(Fable記入欄)
**Sonnet自己申告の限界**: ①Sonnetは音声を聴取できず、構成ラベル(TTS/splice)の正しさは3方式のASR転写との整合でしか確認できない(全方式が台本どおりに転写した場合のみ『ラベル疑義』と表示。`spl_body_almost_deleted`1件のみ該当。TTS 8本は全て台本と異なる文面で転写され読ませた文面とほぼ一致[1本は『rewards』と複数形]=ASRが同じ補正をしていれば検出できない循環が残る)。②正常ラベルは『記事全体の試聴PASS』でありKP/セグメント個別の聴取ではない。③HR承認難例の現存wavは承認時wavと同一か未照合。④問題音声の大半が構成ラベル(人工)で、実運用の誤発音分布を代表しない。KP問題の独立音声は6本のみ(目標8〜15に未達=新規TTS上限8本のため)。⑤構成間の差は0〜2件で統計的に有意でない。⑥入替構成は現行規則の流用であり、規則最適化後の性能ではない。⑦Whisper別サイズはmediumのみ(large-v3は未実施)。⑧Phrase List有のKPがデータに0件(全KPがLedger hint無し)=KPのPL供給時挙動は未検証。⑨Batch TTSを使用(PM_GOVERNANCE 7-1/7-4はTrial=Standard同期が既定。Production wrapperの既定がBatchで、明示切替を怠ったため8本の生成に約25分かかった。費用は安価側[JPY0.17]、品質・仕様への影響なし=運用の逸脱として自己申告)。

## 9. 残存問題・必要な追加Trial(判断候補)
1. **ラベルの強化**: TTS構成音声8本・正常KPの『weaken』『sentence someone to death』『far bank』(Azure/Whisperと不一致)をユーザーが短時間で試聴する(約20音声)と、構成ラベルとHR難例の確度が上がる。費用0。
2. 現行C1の見逃しを定量化するには『OpenAIが補正する語』の独立音声をさらに増やす必要がある(今は1音声x10回と構成TTS 5本)。Store内29件ASR不一致(KP_TAKE_PART_INVESTIGATION_01.md §5)を聴取者ラベルで確定する案が最も費用対効果が高い(新規TTS不要)。
3. スプライス欠落音声の方式見直し(語境界の共調音断片が残り、3方式が語を復元する。TTSによる脱落音声[function wordのみ新規TTS]へ置換、または欠落区間のエネルギー確認)。
4. 入替構成を実際に比較するなら、規則側の調整(Whisper出力の空白/大小文字正規化、Primary側規則の再較正)が前提。**判断候補**: ここまで進めるか、C1dK/C5Kの実装前Trial(Offline Trial)で止めるか。
5. Family X記事での実運用確認(KPのPL空/非空、Standard/Advanced別)は未実施。

## 10. Production採用に関するユーザー判断事項(判断候補。Sonnetは判断しない)
- 判断候補A(KP限定dual-pass: C1dKまたはC5K)を、Offline Trialの次段階へ進めるか(分類の根拠=新仕様の追加・Production挙動の意味的変更のため`27-3 D`相当の候補。『OpenAI Primary → Azure Secondary』『既存Validator』のProduction実装は本Trialで変更していない)。
- 判断候補B: ASR Primary/Secondaryの入替(Azure/Whisper Primary化)は、本Trialでは現行を上回る証拠が得られていない(原価・見逃し・HRの観点)。進める場合は規則側の再較正が必要で、別Trial(追加の聴取ラベル付き音声と費用承認)が前提。
- 判断候補C: Whisper(small/medium)を『独立した第3の意見』として常時走らせる運用(CPU負荷・モデル管理)を許容するか。
