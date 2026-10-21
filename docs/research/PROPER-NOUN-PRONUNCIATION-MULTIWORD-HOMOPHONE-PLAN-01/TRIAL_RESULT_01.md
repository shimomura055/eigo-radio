# TRIAL_RESULT_01: 多語同音救済(計画v3 判定層L1)のTrial結果

管理ID: PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_04 / OPEN-439 / Status管理ラベル: `TRIAL_DONE_PENDING_FABLE`(2026-10-22実行。最終分類はFable。VALIDATED≠APPROVED_FOR_PRODUCTION≠PRODUCTION_WIRED。Production採用・配線は行っていない)
ユーザー指示原文: `docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01_TRIAL-GO_USER.md`(本文1497字、sha256=55ac4069…)。計画: `PLAN_SUMMARY_01.md`・`TRIAL_PLAN_01.md`(v3、commit 31c80d76d)。証跡: `er093_output/pnmh_trial_01/`(dataset_manifest.json・asr_raw.jsonl・paid_calls.jsonl・tts_log.jsonl・layer_results.json・o1_result.json・stop_check_0{1,2,3}.json・sha256_before.txt、audio/*.wav 13本[ローカルのみ・未commit])。Trial script: `er093_pnmh_trial_01_{core,o1_baseline,o1,p1,analyze}.py`(Trial専用、Production関数は呼ぶだけ・メモリ上patch)。

## 0. 開始前チェック(22節): ユーザー指示§3・§4と計画の対応

| ユーザー指示 | 計画v3での検証箇所 | 本Trialでの実施 |
|---|---|---|
| §3-1 `ByUs`↔`by us`/`buy us`(1語対複数語)を救済できるか | ケースM1/M2/M4/M7/RS1/BI3、P1 F2/F3、保存転写 | O1ケース表41件+P1実音声13本+保存転写45件(§2) |
| §3-2 原稿側の正しい英語発音を信頼できる情報から取得・供給できるか | **計画v3の範囲外**(供給層L2は#133判断後の別計画・継続検討候補。TRIAL_PLAN §2/§9、PLAN_SUMMARY) | 範囲外。本Trialで言えるのは2点のみ: CMU収録語は収録発音で判定できる / 辞書外語は判定不能=推測PASSしない(N15:baias/bayas/fayas全てNG、F7 `bai`・F5 `bys`は辞書外でNG)。byUsの英語公式発音は未確定のまま(J7未回答)で「AIが確定した」とは主張しない |
| §3-3 既存の1語対1語・各種救済機構を壊さない | A3 Regression、R1-R8/EX1-3/H1、O0 4,032ペア | 提案無効時の出力はバイト一致、PASS→NG 0(§2-2、§4) |
| §3-4 発音が異なるものを誤PASSさせない | A2/A4、N1-N15/PH1/PH2/F4/F5/F7/F9 | 新規誤PASS 0(§3) |
| §3-5 Family X/Zの共通仕様との整合 | 共通入口=`val.protected_check`/`classify_asr_match`+`sec._step_alternate_pass`(X: `er019_family_x_audio_production_runner_01.py`が`er003_v1_sing01_voice01_generate.py:246`の`secondary_asr.evaluate_attempt_with_cascade`を経由、Z runner(`er026_family_z_fiction_production_runner_01.py`)の個別呼出行はXと同様にはgrepで確認していない[未確認]) | 判定関数は単一の共通入口。判定入口は共通関数(`val.classify_asr_match`)で、X/Z別実装は検出せず。保存転写4,032件にはZ由来(melos/er026_output系など約320行が該当語を含む)とX由来の両方が含まれ、同一関数で再判定済み |
| §3-6 処理速度・量産原価への影響 | TRIAL_PLAN §7 | 判定関数のオーバーヘッド実測・API追加0(§5) |
| §4 ASR構成/Azure重み2.0/ローカルWhisper/KP両方PASS/Trial専用/既存音声再利用/並列化 | TRIAL_PLAN §8・§9 | ASR構成変更なし、Whisper不使用、KP両方PASSは感度表の併記のみ、Production sha256不変、保存転写45件は再ASRせず再利用、ASR呼出は6並列(§6) |

STOP確認: `tools/stop_scope_check_01.py`(managed-id=本ID)をTTS前・ASR前に実行、rc=0・stop=false(`stop_check_01〜03.json`)。TTS_EXECUTION_MODE=STANDARD(Batch不可:Trialは同期・デバッグ性優先、7-4)。

## 1. Fix計画に対する実施結果

| 計画の段階/基準 | 実施 | 結果 |
|---|---|---|
| O1(1) unit test(20件) | 再実行 | 20件PASS(`test_proto_multiword_span_v3_01_result.txt`と同一、2.8秒) |
| O1(2) 提案無効時の出力不変 | 無patch別process(`er093_pnmh_trial_01_o1_baseline.py`)と、patch済み関数をMODE=currentで呼んだ結果を4,032ペアで全項目比較 | **バイト一致**(sha256 2e8f1d8d…、両者同一) |
| O1(3) 目視リスト | 理論域456組から抽出(§2-3) | 下記に掲載。想定外の自動PASSは保存データ上0件 |
| O0再適用(4,032ペア) | v3を**entity_like代表発音を実配線**した形(`er093_pnmh_trial_01_core.py`: patch点`homophone_candidate = bool(result_h)`直後に`entity_like`を渡す)で再適用 | 変化4件=全て`byus→buy us`(同一1記事由来)、PASS→NG 0、flat配線との差0 |
| ケース表41件 | v3(entity_like実配線)で再判定 | 全件が期待どおり(NG 0)、flat配線とも全件同一 |
| P1 構成音声13本+層A/B/C | 実行(§3) | 完了。費用6.32円(Cap 50円) |
| P1 既存wav再ASR | 保存済み転写45件(run_byus_01等、`pairs_02.jsonl`のbyus含有ペア)を再利用、再ASRなし(ASR構成が現行Productionのため) | 0円。うち4件で救済発動(§2-2) |
| A5 同一音声のASR反復 | 4クリップ×2エンジンで2回目を実行 | 判定反転0(§3-3) |

合格基準A1〜A9: A1=充足(適用域内の正例:ケース表5/5+保存転写4/4救済、ただしP1新規音声では救済対象の転写が発生せず=§3-2)、A2=充足(新規誤PASS 0)、A3=充足、A4=充足(F4/F5/F7/F9:PASS 0)、A5=反転0、A6=充足(6.32円、Production sha256不変)、A7=充足(層別・エンジン別、§3-1)、A8=記録値と一致(NX1はFable個別審査対象)、A9=**文字通りは未達1件(BI_C1_A: 層CでPASS 1)だが提案起因ではなく現行コードの1語同音PASS、かつ構成ラベル疑義(下記§3-2)**。

## 2. 救済できた例・できなかった例(O1: API 0)

### 2-1. ケース表41件(v3=entity_like代表発音実配線 / ガード有)
| ID | canonical → ASR | 期待 | 現行 | v3 |
|---|---|---|---|---|
| M1/M2 | byus→buy us(実保存転写) | PASS | NG:TRUE_CONTENT_MISMATCH | **PASS:HOMOPHONE_EQUIVALENT(救済)** |
| M4 | already→all ready | PASS | NG | **PASS(救済)**(一般語への適用域) |
| M7 | wait/weight(既存1:1)+byus→buy us 共存 | PASS | NG | **PASS(救済)** |
| RS1 | …the byUs team…→…the buy us team… | PASS | NG | **PASS(救済)** |
| BI3 | bias→by us(既知の残存) | PASS | NG | **PASS**(音素同一。区切り読みとの区別は音素列だけでは不可=既知の限界) |
| N1-N7,N10-N15,PH1,PH2 | bios/buys/bus/buy/buy us on/buy a/buy us us/Mellow s/uphill→a pill/qual of/lion/three/baias | NOT_PASS | NG | **NG維持**(誤PASS 0) |
| M3,CS1-CS3,M6,BI1,BI2 | 他差分共存・AI phone→iPhone・Bi-us・BAUS | NOT_PASS/KEEP | NG | **NG維持**(M6はガードG5で非救済) |
| R1-R8,EX1-EX3,H1 | 既存1:1・空白差・Case A・既存の穴 | KEEP | PASS | **判定不変**(EX1 AI→eye、EX2 us→u s、EX3 am→a m、H1 Tse→Sea は既存の穴のまま・悪化なし。U5は未回答のためKEEP) |
| NX1 | byUs has two apps→Buy us has to apps | 要審査 | NG | PASS:HOMOPHONE_MATCH_NUMBER_EXCEPTION(事前記録値と一致。**two→toの同音扱いがn:m同音と共存して新規PASSになる点をFableが個別審査**) |

### 2-2. 保存転写(4,032ペア、X・Z・golden・HR queue等)と既存wav(45件)
- 現行→v3で判定が変わったのは**4件のみ**(全て`byus→buy us`、うち2件は`story making→storymaking`併発)。**PASS→NG 0**、NG→PASS 4(全件が音素一致の真の正例、`story making→storymaking`は既存の複合語分かち書き規則で吸収されるspan=音素列比較の対象外)。標本は1記事(run_byus_01)由来で発生率0.10%(4/4,032)。
- byUs周辺の既存wav保存転写45件(`layer_results.json`の`existing_stored_transcripts`): 救済=idx 2338/2370/3463/3474(`byus→buy us`)。`bias`/`by us`/`BIAS`系は現行1:1・despace規則で既にPASS(不変)。`baias`/`bayas`/`fayas`/`bios`/`lion`/`baus bi us`は現行・v3とも**NG維持**(PASS化なし)。

### 2-3. 目視リスト(理論域456組、`o1_result.json`の`risk_lists`)
代表以外のvariantでのみ一致=27、ストレス除去でのみ一致=172、stopword含有317(うち代表外のみ19)。v3の実効値: canonical 1語(X)対ASR 2語でPASSとなる組は全variant比較407組、**entity_like(代表発音限定)では89組**、canonical 2語対ASR 1語は173組。代表外のみ27組のうち**一般語では(`businesses→business is`、`places→play says`、`closer→clothes are`、`ticket→to kit`等)音素列としては一致して自動PASSしうる**(entity_likeでは全て非救済)。保存データ4,032ペア上の発生は0件(上記4件は全て`byus`)。これは「発音が同じなら単語数や綴りでNGにしない」方針の帰結であり、リスク面としてFableが許容可否を判断する(§7)。

## 3. P1: 構成音声13本(層A/B/C、実測)

使用: TTS=`gemini-3.8-flash-lite-tts`(Production Family Xの量産TTS、STANDARD、voice Aoede[声A]/Charon[声B]、ASR検証なしの単発関数`generate_english_component_minimal_instruction`、各1回成功)。ASR: Primary=OpenAI `gpt-4o-mini-transcribe`(Production routingと同一kwargs、bodyのためprompt無し)、Secondary=Azure Speech STT en-US(Phrase List空=`pronunciation_ledger`にbyUs無し。Azure重み2.0は変更なし/該当Phrase無し)。25節: 本Trialは「Production条件での検証」が目的のためProduction採用済みのTTS/ASRを使った(最新世代モデルとの比較は本Trialの目的外)。carrier文C1=`LINE Manga has launched byUs, an AI service that lets you shape stories.`、C2=`Make one yourself with byUs.`(tts_safe変換なしの素の文)。

### 3-1. クリップ別(rep1。focal=byUs相当区間の転写、層B=現行Validator、層C=v3)
| clip | 種別(S1ラベル) | TTS入力 | OpenAI focal | Azure focal | 層B O/Z | 層C O/Z | cascade現行→v3 |
|---|---|---|---|---|---|---|---|
| F0_C1_A | 未確定(要試聴) | byUs | byus | by us | PASS/PASS | 同左 | PASS→PASS |
| F0_C1_B | 未確定(要試聴) | byUs | byus | by us | PASS/PASS | 同左 | PASS→PASS |
| F1_C1_A | 正 | bias | bias | bias | PASS(hom)/PASS(hom) | 同左 | PASS→PASS |
| F2_C1_A | 正 | by us | bias | by us | PASS(hom)/PASS | 同左 | PASS→PASS |
| F3_C1_A | 正 | buy us | bias | bias(+`Manga→Monga`) | PASS(hom)/NOT_PASS | 同左 | PASS→PASS |
| F3_C1_B | 正 | buy us | byus | by us | PASS/PASS | 同左 | PASS→PASS |
| F3_C2_A | 正 | buy us | bias | bias | PASS(hom)/PASS(hom) | 同左 | PASS→PASS |
| F4_C1_A | 負 | bios | bios | bios | NG/NG | NG/NG | NG→NG |
| F4_C1_B | 負 | bios | bios | bios | NG/NG | NG/NG | NG→NG |
| F5_C1_A | 負 | buys | bys | buys | NG/NG | NG/NG | NG→NG |
| F7_C1_A | 負 | buy | bai | by | NG/NG | NG/NG | NG→NG |
| F9_C1_A | 負 | B Y U S | byu | byu | NG/NG | NG/NG | NG→NG |
| BI_C1_A | 負(U-BI=NG維持。構成ラベル疑義) | Bi-us | bias | bias | PASS(hom)/PASS(hom) | 同左 | PASS→PASS |

(hom)=HOMOPHONE_EQUIVALENT(現行の1語同音救済)。**層Bと層Cは全13クリップ×2エンジンで一致=v3による判定変化0**。

### 3-2. 層A/B/Cの集約(エンジン別、rep1、各13本)
| 指標 | OpenAI(Primary) | Azure(Secondary) |
|---|---|---|
| 層A1 綴り一致(spoken text=focal) | 5/13 | 7/13 |
| 層A2 音素一致(CMU、ストレス無視) | 10/13 | 12/13 |
| 層A3 garbage(辞書外かつ非一致) | 2/13(`bai`・`bys`) | 0/13 |
| 層A4 多語化(focal 2語以上) | 0/13 | 4/13(全て`by us`。despaceで既にNORMALIZED_MATCH) |
| 層B 音素一致かつ綴り不一致(A2∧¬A1) | 5件: 現行PASS 5、v3 PASS 5 | 5件: 現行PASS 3、v3 PASS 3(残2件: `Manga→Monga`併発のF3_C1_A=ASR限界の別差分、`by`=F7の脱落でcanonicalと非同音) |
| 層B 音素不一致に対するPASS | 現行0、v3 0(**誤PASS 0**) | 現行0、v3 0(**誤PASS 0**) |
| v3による救済/新規NG | 0 / 0 | 0 / 0 |

層Aの低さ(辞書外`bai`/`bys`、F9`byu`)は「ASR限界」として層Bの失敗に数えない。**F3 `buy us`を指示した音声のうち、ASRが`buy us`と綴った転写は0件**(OpenAIは`Bias`/`Byus`、Azureは`by US`/`Bias`)=本Trialの新規音声ではn:m救済が必要になる転写が発生しなかった(救済の実例は保存転写由来の4件のみ)。F0(`byUs`をそのまま)はTTS・ASRとも`byus`/`by us`系で音素一致(ラベルは要試聴)。

**構成ラベル疑義**: BI_C1_A(`Bi-us`指示)は両エンジンとも`Bias`と転写し、TTSが`bias`と読んだ可能性が高い(実際に音節区切りで読んだかは試聴しないと不明)。A9を文字通り読むと「層CでPASS 0」に対し本件は1だが、現行コードでも同じPASS(救済0)で、v3の寄与ではない(V8ガードの対象=`bias⇔bi us`はケースBI1でNG維持を確認済み)。

### 3-3. A5 同一音声のASR反復(4クリップ×2エンジン)
転写の綴りは非決定(OpenAI F0 `Byus`↔`By us`、F2 `Bias`↔`BIAS`)だが、**判定反転は現行・v3とも0**。

## 4. 誤PASS・過剰NGの発生状況
- **新規誤PASS: 0**(ケース表41件、保存転写4,032ペア、実音声13本×2エンジン)。実音声負例(F4 bios×2、F5 buys、F7 buy、F9 B Y U S): PASS 0(除外あり/なし同じ)。
- **過剰NG(PASS→NG): 0**。F3_C1_A(Azure)のNGは`Manga→Monga`という別差分に起因(提案前後で同一)。
- 現行でも通る既存の穴(EX1 AI→eye、EX2、EX3、H1 Tse→Sea、BI_C1_A):悪化・拡大なし(是正はしていない)。

## 5. 既存Validator・ASR Cascadeへの影響
- Production関数・Prompt・閾値・辞書・Ledger・Phrase List・モデル構成は未編集。`sha256_before.txt`の5ファイル(`er006_preprod_hardening_01_validation.py`・`er006_secondary_asr_01.py`・`er003_v1_repro01_main_generate.py`・`er006_pronunciation_ledger_01.py`・`er006_asr_provider_routing_01.py`)は実行後も一致(`sha256sum -c` OK)。提案はメモリ上patchのみ(`er093_pnmh_trial_01_core.py`)、`git status`上、Trial開始後に更新されたtracked/untrackedはTrial dir・Trial script・delegation_log・docs/ACTIVE_TASKのみ。
- 提案無効時の出力はバイト一致(§1)。Secondaryの許容経路(`_secondary_accept`)と同じ`classify_asr_match`+`_step_alternate_pass`を共有=Primary/Secondary双方で同じ規則が働く(M1_MULTI_CANDIDATE経路は転写単体の再判定では再現しておらず「cascade」列は`should_pass`/代替PASSのみ。M1が加わればPASS側にのみ増える方向)。
- 判定挙動の変化4点(A8): (a)数字ゲート例外=NX1でPASS(要審査)、(b)M1矛盾拒否=CS3で分類のみ`TRUE_CONTENT_MISMATCH→ASR_VALIDATION_UNCERTAIN`(最終NOT_PASS、retry停止側へ)、(c)connected-speech迂回=CS1/CS2はNG維持、(d)F1残差=RS1はPASS。記録値と全て一致、PASS→NG 0。

## 6. QCD
- **品質**: 新規誤PASS 0・過剰NG 0。救済は音素列が一致するn:m置換のみ。限界: 実音声での救済実績は保存転写の1記事(4ペア)のみで、P1の新規音声(ASRが1語/despaceで出力)では発生せず。サンプルは小さく有意性は主張しない。
- **処理速度**: `classify_asr_match`+`_step_alternate_pass`1回あたり、現行1.375ms→v3 1.394ms(4,032ペア平均、差0.02ms=約1.4%、API 0)。ASR判定34件で0.49ms→0.49ms。Trial総所要: TTS 13本=約35秒(各2〜3秒、逐次)、ASR 34呼出=6並列で6.6秒(OpenAI平均0.90秒、Azure平均1.23秒)。
- **量産原価**: 実行時API追加0(CMU辞書引きのみ)。期待値はbyUs型のretry削減(1件約5円+cooldown10分)×発生率0.10%=記事あたり0〜0.1円オーダーの微減。実測の再試行削減は未確認(標本1記事)。
- **Trial費用(実測)**: 合計**6.32円**(Cap 50円、見積18〜28円の約1/3): OpenAI ASR 0.40円(usage token×$1.25/$5.0 per M、`pricing_snapshot.json`、160円/USD)+Azure STT 4.31円(音声秒切上×$1/h、`er078_asr_unified_judge_01.py:110-113`)+TTS 1.60円(13本、`tts_raw_usage_log.jsonl`のinput/output token×Standard $0.5/$6.0 per M、同snapshot)。出典: `paid_calls.jsonl`(ASR 34行)、`tts_raw_usage_log.jsonl`(TTS 13行)、`layer_results.json`の`cost`。日次累計: 本Trial分6.32円(同日の他タスク分は未確認)。再実行・再生成0。
- **ASR §8チェックリスト(現行構成で確認)**: (1)エンジン・モデルID=OpenAI gpt-4o-mini-transcribe/Azure STT en-US=**変更なし** (2)エンジン固有入力: Phrase List=空(Ledgerにbyus無し)・OpenAI prompt=body無し、**変更なし** (3)統一judge: Primary PASSならSecondary不要(現行)・`secondary_accept_fn`経路で`HOMOPHONE_EQUIVALENT`使用可=**変更なし** (4)表層差(句読点/大文字小文字/`BIAS`/`By us`/`by US`)は`val.tokenize`で吸収=P1転写34件で確認 (5)転写キャッシュ再適用: 4,032ペア再測定済み(ASR3Wの保存転写544件を含む、判定変化は`byus`の4件のみ) (6)KP/Body別構成: 同一構成=別集計不要(byUsを含むKPは存在せず) (7)費用単価更新: 上記実測。

### 感度分析(新仕様ではない解釈の併記): 「Primary・Secondary両方PASS必須」と読んだ場合
byUsを含むKey Phraseのクリップは存在しないため、本文carrierのP1 13本に同じ転写を適用した参考表(追加費用0)。
| 区分 | 現行(Primary PASSならSecondary不要) | 両方PASS必須の読み(現行判定) | 両方PASS必須の読み(v3) |
|---|---|---|---|
| 正例5本(F1,F2,F3×3) | 5/5 PASS | 4/5 PASS(F3_C1_A: Azureが`Monga`併発でNG) | 4/5(同じ) |
| 負例5本(F4×2,F5,F7,F9) | 0/5 PASS | 0/5 | 0/5 |
| BI/F0(参考) | 3/3 PASS | 3/3 | 3/3 |
v3は両方PASS必須の読みでも結果を変えない(救済対象の転写が発生しなかったため)。KPのPASS条件そのものはOPEN-440の別系統であり、本表は設計・実装ではない。

## 7. Fable独立評価
**最終分類: `VALIDATED`**(Trialとしての有効性確認。`APPROVED_FOR_PRODUCTION`ではない。Production採用・配線はユーザー正式承認が必須)

**合格基準の照合(Fable)**
- 既知正例の救済100%: 充足(保存転写`byus→buy us` 4/4、構成正例M1/M2/M4/M7/RS1)。
- 新規誤PASS 0: 充足(ケース表41件・保存転写4,032ペア・実音声13本×2エンジン)。
- 実音声負例のPASS 0: 充足(bios×2/buys/buy/B Y U S)。**A9(`Bi-us`型)の1件は「負例の構成失敗」と判定**: 両エンジンが`Bias`と転写しており、TTSが`bias`と読んだ疑いが強い。PASSは現行の1語同音規則によるもので提案の寄与は0。したがって提案の欠陥ではないが、「`Bi-us`型の実音声負例をNGにできる」ことは本Trialでは**実音声で未検証**であり、保証はケース表BI1/BI2(NOT_PASS)とV8ガードのコードレベルに留まる。採用時の実装testで実音声負例を1本取り直すことを条件とする。
- Regression PASS→NG 0: 充足。層A/B/C分離報告: 充足。

**サンプルの偏り(Fable)**
- 実音声での救済実績は1記事(run_byus_01)の4ペアのみ。新規13本ではASRが`Bias`/`Byus`/`by US`と出力し、`buy us`型の転写は0件。提案が必要になる頻度は低く(0.10%)、効果は主に予防的。有意性は主張しない。
- 一方、副作用の面は広く計測済み(4,032ペア再適用、機能語経由一致の全列挙407組→代表発音限定89組、保存データでの発生0)。安全側の評価としては十分。

**挙動変化4点の審査(Fable)**
- NX1(`two→to`が多語同音と共存して新規PASS): `two→to`は現行Productionが既に許容している1語同音の数値例外であり、新規に数値差を解放するものではない。各差分が独立に真の同音である以上、組合せでNGにすべき理由はない→**許容**(ただし採用提案時にユーザーへ明示)。
- BI3(`bias⇔by us`): ユーザー判断「発音が同じなら単語数・綴り・ストレスの違いでNGにしない」の範囲内→許容。区切り読みとの区別不能は既知の限界として記録。
- CS3の分類変化(最終NG不変)、RS1 PASS: 許容。
- 機能語経由の一致(`businesses→business is`等、代表発音限定89組): いずれも連続音声では同音であり、TTSが正しく読んだ場合にASRがそう綴る可能性のある組。保存データで発生0。採用時はこの89組を目視リストとして添付する。

**Family X/Z整合**: 判定入口は共通関数で、Z由来の保存転写も同一関数で再判定済み。Z runner呼出行の個別確認は採用実装時のtestで行う(未確認事項として残す)。

**QCD**: 実行時API追加0、判定時間+0.02ms、Trial費用JPY6.32(Cap 50)。量産原価への影響なし。

**Production採用に向けたFable推奨**: 採用を推奨する(品質ライン「同音の正しい読みをNGにしない」に適合し、誤PASS増0・原価0)。ただし効果が小さいため単独で急がず、**OPEN-440(Key Phrase両方PASS)の実装と同じ判定関数群を触るので、同一の実装・Opus独立レビュー(条件C)・Regression・runtime evidenceに束ねて実施する**ことを推奨。供給層L2は範囲外のまま(#133判断待ち)。

## 8. 分類案・Production採用に必要なユーザー判断(候補)
- **分類候補: `VALIDATED`(条件付き)**。根拠: A1〜A8を充足(新規誤PASS 0・PASS→NG 0・実音声負例PASS 0・提案無効時バイト一致・費用6.32円/Cap 50円・Production不変)。条件/留意: (i)A9の文字通りの数値(層CでBI相当のPASS 1)は現行コードの1語同音であり提案起因ではないが、構成ラベル疑義(要試聴)のため、Fableが「A9=充足」と判定できるか確認が必要。(ii)実音声での救済実績は保存転写1記事の4ペアのみで、P1新規音声では救済対象の転写が出なかった(効果は小さく、標本も小さい)。(iii)`REJECTED`該当(新規誤PASS)は0。境界があれば`USER_DECISION_REQUIRED`。
- **Production採用に必要なユーザー判断(判断候補)**:
  1. L1(判定層)をProductionへ採用するか。効果は発生率0.10%・原価削減はほぼ0だが、同音の正しい読みを誤ってNGにしない品質上の改善(`buy us`型)。採用する場合の配線方式(11-7の限定例外 or Offline Trial後の通常実装)と、条件C(重要変更のProduction採用提案前)のOpus独立レビュー。
  2. 許容する副作用の線引き: NX1(two→toが多語同音と共存して新規PASS)、BI3(bias⇔by usの区切り読み非区別)、一般語の機能語経由一致(`businesses→business is`等、§2-3)。
  3. U5(既存の穴EX1〜EX3・H1の是正)は未回答のまま別管理。
  4. L2(供給層:原稿側の正しい英語発音の取得・供給、ユーザー§3の2点目)は本Trialの範囲外。#133判断後の別計画でよいか。J7(byUsの公式英語発音)は未回答のまま。
  5. Bi-us型はNG維持(U-BI確定済み)。BI_C1_Aの試聴(`er093_output/pnmh_trial_01/audio/BI_C1_A.wav`)を行うか(任意)。

## 9. RESULT_PACKET 4行の裏付け(詳細は`docs/pm/RESULT_PACKET_PNMH4.md`)
照合ファイル: `TRIAL_PLAN_01.md`§5・§8、`PLAN_SUMMARY_01.md`、`proto_multiword_span_01.py`(v3)、`er006_preprod_hardening_01_validation.py:696-757`(patch点)、`er006_secondary_asr_01.py:571-598,993-1012`。
