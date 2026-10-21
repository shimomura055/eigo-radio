# TRIAL_PLAN_01: 1語⇔複数語の同音救済(案A)＋期待発音源(#133縮小統合)の検証計画

管理ID: PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_01 / Status管理ラベル: `PLAN_V2_PENDING_USER_FIX`(v2=委任_02: Fable/Opus独立レビューOF-PNMH-R-01〜13を反映。変更点は`DESIGN_OPTIONS_01.md` §3-§4と本書の【v2】印)
**本書は計画であり、Trialは開始しない。** 新Primary/Secondary確定(ASR-THREE-WAY-COMPARISON-TRIAL-01の結果＋ユーザー確定)と、ユーザーによる本計画のFixまで、有料API・TTS/ASR・Production変更は行わない。計画完成を理由にTrialへ自動移行しない。
対象方式: `DESIGN_OPTIONS_01.md` §3-§4(案A-all＋ガード、案B2は条件付きサブTrial)。

## 1. Status遷移

`PLAN_DRAFT_PENDING_FABLE_REVIEW`(委任_01) → Fable独立レビュー(+Opus条件A) → 委任_02で改訂 → **`PLAN_V2_PENDING_USER_FIX`(現在)** → **`PLAN_FIXED`(ユーザー確認・Fix)** → [ASR 3方式比較の結果・ユーザーのPrimary/Secondary確定] → `TRIAL_READY`(差替え条件§8反映) → `TRIAL_RUNNING` → `TRIAL_DONE_PENDING_FABLE` → **`VALIDATED`**(合格基準§5を満たす) / **`REJECTED`**(新規誤PASSがある等) / **`USER_DECISION_REQUIRED`**(基準の境界・新仕様判断)。VALIDATED≠APPROVED_FOR_PRODUCTION≠PRODUCTION_WIRED(Production採用は人間ユーザーのみ)。

## 2. 前提とラベルの扱い

- **ラベルの原則**: 「正例」=聴感上canonicalと同じ音で、救済(PASS)すべき。「負例」=音が違う/語が脱落・追加されている/誤読で、新たに誤PASSしてはならない。「KEEP」=現行判定を変えない(Regression、および既存の穴を悪化・拡大させない確認)。**ASRの出力そのものを正解にしない**(音声の正解は、構成音声ではTTS入力文＝既知のspoken text、実音声では多数決/試聴)。
- **byUsの期待発音に関する条件付きラベル**: byUsの公式EN発音は未確認(J7依存)。案Aの信頼の土台は『期待発音＝CMU収録綴りの発音』(現行1:1救済と同じ)で、byUsでは`B AY AH S`。
  - シナリオS1(J7=認める、または期待発音を`bias`系`B AY AH S`として確定): byUs/bias/by us/buy usの転写は全て正例。
  - シナリオS2(J7=認めない、未確認のまま): byUsを『確認済み正例』と呼ばない。ただし`B AY AH S`系の聴取音は現行1:1救済と同水準で扱う。合格基準は同じ(`buy us`救済は現行の`Bias`救済と同じ信頼土台)。レポートにはS1/S2どちらで評価したかを明記する。
  - どちらでも、**『byUsの正しい発音をAIが確定した』とは主張しない**。
- **【v2・R-02】`bias`⇔`Bi-us`型(音節を区切った読み)の期待ラベルはユーザー判断(U-BI)**: CMU `bi`=`B AY1`のため音素列は`bias`と同一で、CURRENT_SPEC.md:454は`BAUS`/`Bi-us`を「実音声の誤発音、引き続きNG」と記録している。ラベルの扱い: (B0)不合格維持=負例(推奨初期値、V8ガード有効化)、(B1)合格=正例(V1)。ユーザー判断前は**両ラベルで集計を併記**し、どちらでも他の基準(A1〜A8)の判定を変えない。
- 仕様拡張部分(n:m音韻一致)の検証はDEV専用経路(メモリ上のsource patch、`proto_multiword_span_01.py`方式)。Production関数・Prompt・閾値・辞書は編集しない。

## 3. ケース表(ユーザー§4の全種別。①は計画段階で既にオフライン事前測定済み)

事前測定=`build_case_table_01.py`→`TRIAL_CASES_01.json`(API 0、現行判定と提案判定[ガード有/無のablation]を併記)。列: ID/種別/期待/現行判定/提案判定(ガード有)/提案(ガード無ablation)/結果。実例は`pairs_01.jsonl`(保存転写3,493ペア)由来で、出典は`TRIAL_CASES_01.json`の`origin`。ラベル根拠は`label_basis`。

| ID | 種別 | canonical → ASR転写(要約) | 期待 | 現行 | 提案(ガード有) | 提案(ガード無) | 結果 | ラベル根拠 / 出典 |
|---|---|---|---|---|---|---|---|---|
| M1 | 1語⇔複数語(正例) | (長文) 差分: byus→buy us; the→∅; story making→storymaking | PASS | NG:TRUE_CONTENT_MISMATCH | PASS:HOMOPHONE_EQUIVALENT | PASS:HOMOPHONE_EQUIVALENT | OK | 音韻定義: byus=B AY1 AH0 S, buy us=B AY1+AH1 S(ストレス無視で一致)。ただしbyUs自体の公式発音は未確認(J7依存) / 実保存転写:er019_output/family_x_audio_production_wiring_01/manga_ai_chat_b |
| M2 | 1語⇔複数語(正例) | (長文) 差分: byus→buy us | PASS | NG:TRUE_CONTENT_MISMATCH | PASS:HOMOPHONE_EQUIVALENT | PASS:HOMOPHONE_EQUIVALENT | OK | 同上(Primary転写) / 実保存転写:er019_output/family_x_audio_production_wiring_01/manga_ai_chat_b |
| M3 | 1語⇔複数語+他差分(Azure by us) | (長文) 差分: was→with; byus→by us; a way→away | KEEP | NG:ASR_VALIDATION_UNCERTAIN | NG:ASR_VALIDATION_UNCERTAIN | NG:ASR_VALIDATION_UNCERTAIN | OK | span自体は空白差(HEADで吸収)。ペアは他差分(and脱落・was→with・a way→away)があるためNG維持が正(提案でも変わらないことを確認) / 実保存転写:er019_output/family_x_audio_production_wiring_01/manga_ai_chat_b |
| M4 | 1語⇔複数語(正例・一般語、綴り違い) | It is already late. → It is all ready late. | PASS | NG:TRUE_CONTENT_MISMATCH | PASS:HOMOPHONE_EQUIVALENT | PASS:HOMOPHONE_EQUIVALENT | OK | 音韻定義: already=AO2 L R EH1 D IY0, all ready=AO1 L+R EH1 D IY0(CMU、ストレス無視で一致)。一般語への適用域の確認(空白差ではなく綴り違い) / 合成 |
| M6 | 略語+多語(負例) | Some AI Phone Calls Had Humans Behind the Scenes. → Some iPhone calls had humans behind the scenes. | NOT_PASS | NG:ASR_VALIDATION_UNCERTAIN | NG:ASR_VALIDATION_UNCERTAIN | PASS:HOMOPHONE_EQUIVALENT | OK | ai phone→iphone: ガードG5(canonical側3字未満)で非救済。ガード無しだとAIを『アイ』と読む誤りを素通し / telemetry実例 |
| M7 | 1語⇔複数語(正例・同一spanが他の1:1同音差分と共存) | Please wait. LINE Manga has launched byUs now. → Please weight. LINE Manga has launched buy us now. | PASS | NG:TRUE_CONTENT_MISMATCH | PASS:HOMOPHONE_EQUIVALENT | PASS:HOMOPHONE_EQUIVALENT | OK | wait/weight(既存1:1)+byus→buy us(新)の共存。全差分が同音のときのみPASS / 合成 |
| N1 | 近音/脱落/追加/文字読み(負例) | The service is called byUs now. → The service is called BIOS now. | NOT_PASS | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | OK | 実ASR出力BIOS(run_byus_01 p1/2)。CMU: bios=B AY1 OW0 S≠byus。1:1で非同音 / 合成(実例由来の型) |
| N2 | 近音/脱落/追加/文字読み(負例) | The service is called byUs now. → The service is called buys now. | NOT_PASS | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | OK | buys=B AY1 Z≠byus(Z/S) / 合成(実例由来の型) |
| N3 | 近音/脱落/追加/文字読み(負例) | The service is called byUs now. → The service is called bus now. | NOT_PASS | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | OK | bus=B AH1 S≠ / 合成(実例由来の型) |
| N4 | 近音/脱落/追加/文字読み(負例) | The service is called byUs now. → The service is called buy now. | NOT_PASS | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | OK | 脱落(us)。1:1で非同音 / 合成(実例由来の型) |
| N5 | 近音/脱落/追加/文字読み(負例) | The service is called byUs now. → The service is called buy us on now. | NOT_PASS | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | OK | 追加語(on): 連結音素列が不一致 / 合成(実例由来の型) |
| N6 | 近音/脱落/追加/文字読み(負例) | The service is called byUs now. → The service is called buy a now. | NOT_PASS | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | OK | buy a=B AY1 AH0≠(終端S無し) / 合成(実例由来の型) |
| N7 | 近音/脱落/追加/文字読み(負例) | The service is called byUs now. → The service is called buy us us now. | NOT_PASS | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | OK | 重複語(追加): 連結が不一致 / 合成(実例由来の型) |
| N10 | 近音/脱落/追加/文字読み(負例) | Melos ran to the city. → Mellow s ran to the city. | NOT_PASS | NG:ASR_VALIDATION_UNCERTAIN | NG:ASR_VALIDATION_UNCERTAIN | NG:ASR_VALIDATION_UNCERTAIN | OK | OOV+文字読み(G4/G6)。Melosの公式EN発音は未確認(PNEP Z1) / 合成(実例由来の型) |
| N11 | 近音/脱落/追加/文字読み(負例) | Walk uphill slowly. → Walk a pill slowly. | NOT_PASS | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | OK | uphill=AH1 P HH IH1 L≠a pill(K7実例) / 合成(実例由来の型) |
| N12 | 近音/脱落/追加/文字読み(負例) | The qualitative study ran. → The qual of study ran. | NOT_PASS | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | OK | 実例(qualitative→qual of)。音素不一致 / 合成(実例由来の型) |
| N13 | 近音/脱落/追加/文字読み(負例) | The line was long. → The lion was long. | NOT_PASS | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | OK | K5実例(LINE→Lion、独立エンジン2/3が実音声でLion)。line=L AY1 N≠lion=L AY1 AH0 N / 合成(実例由来の型) |
| N14 | 近音/脱落/追加/文字読み(負例) | The study followed two groups. → The study followed three groups. | NOT_PASS | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | OK | 数値ガード(既存) / 合成(実例由来の型) |
| N15 | 実ASR出力・CMU辞書外(負例/判定不能) | (長文) 差分: byus→baias | NOT_PASS | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | NG:TRUE_CONTENT_MISMATCH | OK | Baias/BAYAS/FAYAS: CMU辞書外→判定不能=推測でPASSさせない(委任_07 §2-4) / 実保存転写:er019_output/family_x_audio_production_wiring_01/manga_ai_chat_b |
| EX1 | 既存の穴(AI→eye、悪化させない) | The AI phone rings. → The eye phone rings. | KEEP | PASS:PROPER_NOUN_ENTITY_ARPABET_CONFIRMED | PASS:PROPER_NOUN_ENTITY_ARPABET_CONFIRMED | PASS:PROPER_NOUN_ENTITY_ARPABET_CONFIRMED | OK | AIは『エー・アイ』と読むべき。eyeはTTSの誤読。**現行でもPASSしてしまう既存の穴(INVESTIGATION_01 §2-追加5)**。提案で悪化/拡大させないことのみ確認(KEEP)。是正は別管理 / 合成 |
| EX2 | 既存の穴(us→u s、despace吸収、悪化させない) | He told us the plan. → He told u s the plan. | KEEP | PASS:NORMALIZED_MATCH | PASS:NORMALIZED_MATCH | PASS:NORMALIZED_MATCH | OK | usの文字読みu sは単独差分では全文despace(NORMALIZED_MATCH)でPASS(既存の穴、canonical=pronoun us)。canonical=国名USなら正読。提案で変化なしを確認(KEEP) / 合成 |
| EX3 | 既存の穴(am→a m、despace吸収、悪化させない) | Please wait. The meeting is at 10 am sharp. → Please weight. The meeting is at 10 a m sharp. | KEEP | PASS:HOMOPHONE_EQUIVALENT | PASS:HOMOPHONE_EQUIVALENT | PASS:HOMOPHONE_EQUIVALENT | OK | am→a mは空白差のみのspanとして既存の全文/span despace規則が吸収(提案の対象外)。canonical=時刻のAM(10 a.m.)なら正読。現行判定の維持のみ確認 / 合成 |
| R1 | 既存1語⇔1語同音(Regression) | (長文) 差分: bias→byus | KEEP | PASS:HOMOPHONE_EQUIVALENT | PASS:HOMOPHONE_EQUIVALENT | PASS:HOMOPHONE_EQUIVALENT | OK | run_byus_01 p1/3 Primary Byus: cmu_alternateでPASS採用(現行PASS維持) / 実保存転写:er019_output/family_x_audio_production_wiring_01/manga_ai_chat_b |
| R2 | 既存1語⇔1語同音(Regression) | (長文) 差分: byus→bias | KEEP | PASS:HOMOPHONE_EQUIVALENT | PASS:HOMOPHONE_EQUIVALENT | PASS:HOMOPHONE_EQUIVALENT | OK | p3/3 Azure bias: secondary_confirmedで採用 / 実保存転写:er019_output/family_x_audio_production_wiring_01/manga_ai_chat_b |
| R3 | story-making(Regression) | (長文) 差分: byus→bias; story making→storymaking | KEEP | PASS:HOMOPHONE_EQUIVALENT | PASS:HOMOPHONE_EQUIVALENT | PASS:HOMOPHONE_EQUIVALENT | OK | HEADでstory making→storymaking+byUs→Bias共存=HOMOPHONE_EQUIVALENT(MDJF是正) / 実保存転写:er019_output/family_x_audio_production_wiring_01/manga_ai_chat_b |
| R4 | 既存1語⇔1語同音(Regression) | Please wait here. → Please weight here. | KEEP | PASS:HOMOPHONE_EQUIVALENT | PASS:HOMOPHONE_EQUIVALENT | PASS:HOMOPHONE_EQUIVALENT | OK | wait/weight(No.8、完全同音) / 合成 |
| R5 | 固有名詞Case A(Regression) | Christie spoke first. → Kristie spoke first. | KEEP | PASS:PROPER_NOUN_ENTITY_ARPABET_CONFIRMED | PASS:PROPER_NOUN_ENTITY_ARPABET_CONFIRMED | PASS:PROPER_NOUN_ENTITY_ARPABET_CONFIRMED | OK | CMU代表発音一致(PROPER_NOUN_ENTITY_ARPABET_CONFIRMED) / 合成 |
| R6 | 空白差(Regression) | We read the story-making guide. → We read the story making guide. | KEEP | PASS:NORMALIZED_MATCH | PASS:NORMALIZED_MATCH | PASS:NORMALIZED_MATCH | OK | NORMALIZED_MATCH(despace) / 合成 |
| R7 | 空白差(Regression) | By Us lets you shape stories. → byUs lets you shape stories. | KEEP | PASS:NORMALIZED_MATCH | PASS:NORMALIZED_MATCH | PASS:NORMALIZED_MATCH | OK | run_byus_01 topic_intro: Primary 'By Us'=NORMALIZED_MATCH / 実例型 |
| R8 | 複合語(Regression) | A blitz scaling approach. → A blitzscaling approach. | KEEP | PASS:NORMALIZED_MATCH | PASS:NORMALIZED_MATCH | PASS:NORMALIZED_MATCH | OK | despace(冠詞除外版) / 合成 |

**事前測定の読み**: 30ケース全て期待どおり(0 NG)。正例(M1,M2,M4,M7)は救済、近音/脱落/追加/OOV/数値の負例は全て非救済のまま、Regression/KEEP(R1-R8,EX1-EX3,M3)は判定不変。ガード無しablationで判定が変わるのはM6(`AI phone→iPhone`)のみ。**これは受入Trialではなく計画の根拠測定**(合成carrier文を含む)。Trialでは新Primary/Secondaryの実転写・実音声で再測定する。

### 3-1b. 【v2】追加ケース(Opus R-02/R-03/R-04/R-05。API 0で事前測定済み、`measure_v2_01.py`→`measure_v2_result_01.json`)
判定は「現行コード」→「V1=ストレス無視・全variant・G4(a)のみ(`DESIGN_OPTIONS_01.md` §4)」。V8=G4(b)(2字tokenは機能語集合のみ)有効。

| ID | 種別 | canonical → ASR転写 | 期待 | 現行 | V1 | V8 | ラベル根拠 |
|---|---|---|---|---|---|---|---|
| BI1 | `Bi-us`型(R-02) | The service is called bias now. → The service is called Bi-us now. | **U-BI待ち**(B0=NOT_PASS/B1=PASS) | NG:TRUE_CONTENT_MISMATCH | PASS:HOMOPHONE_EQUIVALENT | NG:TRUE_CONTENT_MISMATCH | CURRENT_SPEC.md:454と衝突。`tokenize("Bi-us")`=`[bi,us]`でハイフン情報は消える |
| BI2 | 実データ(runtime evidence) | byUs ... pronounced "bias." → BAUS ... "Bi-us." (`runtime_evidence_x.json`) | NOT_PASS | NG | NG(`byus→baus`のOOV diffが残る) | NG | 実音声の誤発音。新規救済なし |
| NX1 | 数字ゲート例外(R-04a) | byUs has two apps. → Buy us has to apps. | **要審査**(two→toの同音扱いが拡大) | NG:TRUE_CONTENT_MISMATCH | PASS:HOMOPHONE_MATCH_NUMBER_EXCEPTION | PASS(同) | 1:1の対照`Bias has two apps.`→`Byus has to apps.`は現行でもPASS。n:m同音と共存する場合のPASSが新規 |
| CS1 | connected-speech迂回(R-04c) | Please check this stuff with byUs now. → ...this tough with buy us now. | NOT_PASS | NG | NG(変化なし) | NG | 他の内容語差が残る→従来評価 |
| CS2 | 同上 | Walk uphill slowly with byUs. → Walk a pill slowly with buy us. | NOT_PASS | NG | NG(変化なし) | NG | K7実例型 |
| CS3 | 固有名詞差混在(R-04c) | Melos met byUs today. → Mellow s met buy us today. | NOT_PASS | NG:TRUE_CONTENT_MISMATCH | NG:ASR_VALIDATION_UNCERTAIN(retry停止) | 同 | 分類のみ変化(最終NOT_PASS)。Secondaryへ渡す場合のM1矛盾拒否(R-04b)も変化: `Melos met buy us today.` TRUE_CONTENT_MISMATCH→UNCERTAIN |
| RS1 | 単純n:m正例の周辺文(R-04d) | He said the byUs team won the match. → He said the buy us team won the match. | PASS | NG | PASS:HOMOPHONE_EQUIVALENT | 同 | F1残差は1:1限定のため別途のF1経路は関与しない |
| H1 | 既存の穴(Tse→sea、R-03。新規ルール対象外) | Kristie Tse spoke first. → Kristie Sea spoke first. | KEEP(悪化させない。是正しない) | **PASS:HOMOPHONE_EQUIVALENT** | 同 | 同 | 『Case Aは代表発音のみ』の意図に反し、entity_like∧homophone_candidateなら全variant一致でPASSする既存の穴。保存canonical中のcapitalized語(621語)では非代表variantでのみ同音になる組が5組(`loewe→low`[46回]、`tse→sea/see`[12回]、`are→or`、`when→win`) |

【V1での理論域】語彙3,725語、2語連続で等価になるX(単語)は**456組(distinct。委任_01の461はprimary-flag別の重複を含む)**。ストレス込みでも一致284/ストレス除去で初めて一致172、代表発音のみで成立122、代表以外のvariantでのみ成立27(`measure_v2_result_01_vocab01.json`)。

### 3-2. 追加ケース(有料Trialで新規に作る構成音声。designed audio)【v2・R-06/R-07: 48本→13本に縮小】
TTS入力文を意図的に変えた音声で、(a)ASRの生認識、(b)救済後判定、を分離して測る。carrier文C1=`LINE Manga has launched byUs, an AI service that lets you shape stories.`、C2=`Make one yourself with byUs.`。声は標準lineupの男女各1(声A/声B)。

| ID | TTS入力(spoken) | 期待(S1) | 狙い | 本数 |
|---|---|---|---|---|
| F0 | `byUs`(そのまま) | 試聴/多数決で別途ラベル | TTSの実際の読み(BIOS等) | C1×声A, C1×声B = 2 |
| F1 | `bias` | 正例 | 同音(1:1、現行でも救済) | C1×声A = 1 |
| F2 | `by us` | 正例 | 同音(n:m、空白差) | C1×声A = 1 |
| F3 | `buy us` | 正例 | 同音(n:m、綴り違い=本命) | C1×声A, C1×声B, C2×声A = 3 |
| F4 | `bios` | 負例 | 近音(実ASR出力BIOSの再現) | C1×声A, C1×声B = 2 |
| F5 | `buys` | 負例 | 近音(Z/S) | C1×声A = 1 |
| F7 | `buy`(`us`脱落) | 負例 | 単語の脱落 | C1×声A = 1 |
| F9 | `B Y U S`(文字読み) | 負例 | 文字読み | C1×声A = 1 |
| BI | `bi us`(ハイフン区切り`bi-us`を指示) | U-BI待ち | 音節区切りの実ASR出力(ハイフン有無) | C1×声A = 1 |

計**13本**(F0 2＋F1 1＋F2 1＋F3 3＋F4 2＋F5 1＋F7 1＋F9 1＋BI 1)。削除したF6(`bus`)・F8(`buy us us`)・F10(`bayas`)・F11(`by us now`)は、F4/F5/F7(近音・脱落)と§3の合成ケースN3/N5/N7/N15が同じ判定規則を既に事前測定で確認済み(新規情報が小さい)ため、Trialから外す。TTSがcanonical側へ自動補正した可能性がある音声(全エンジンの転写がcanonicalと一致する負例)は『構成ラベル疑義(要試聴)』として除外あり/なし両方で集計。
**既存wavの再ASR(TTS 0円・R-06)**: run_byus_01の既存attempt wav(byUs周辺でASR差分が出た約5本、`er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/*/narration/attempts/`)を**確定ASR構成で再ASR**する(新規TTS生成なし。K5型LINE→Lion等の実音声負例もここに含む)。
**固有名詞以外**の適用リスク確認: 一般語の正例(`already/all ready`型)・誤差(`places/place is`型)は§3の合成ケース＋適用域列挙(`triples_review_list_01*.json`)で扱い、有料音声は作らない。

## 4. ASR生認識精度と救済後判定の分離評価

各クリップ×各エンジンについて、『focal span』(carrier内のbyUs相当区間)を次の3層で別々に記録する(同じ表で混ぜない):
- **層A ASR生認識(Validator前)**: (A1)focal spanの綴り一致率(転写のfocal span＝spoken text)、(A2)音素一致率(CMUでspoken textと転写focal spanの音素列が一致)、(A3)garbage率(OOV・無関係語)、(A4)エンジン別の多語化率(`byUs`→2語以上)。判定ロジックは一切通さない。
- **層B Validator救済**: 『層Aで綴りは不一致だが音素一致(A2∧¬A1)』のうち、現行判定でPASSした率(ベースライン)と提案判定でPASSした率(**救済率＝提案の寄与**)。『音素不一致』のうち提案でPASSした率(**誤PASS率**。新規誤PASS＝現行NG∧提案PASS)。
- **層C 最終**: ラベル(正例/負例/KEEP)に対する混同行列。Primary単独/Secondary救済/統一judge全体の3視点(構成C1: 現行、C1d: force_secondary 等、ASR確定構成に合わせる)。
層Aの低さ(Whisperがgarbageを返す等)は『ASR限界』として層Bの失敗にカウントしない。層Bは『音素が一致しているのにNGのまま』の件数のみ失敗とする。

## 5. 合格基準(事前固定。ユーザー基本受入条件『既知の正例を救済し、既知の負例を新たに誤PASSしない』)

| # | 基準 | 判定 |
|---|---|---|
| A1 | 正例(音素一致かつ適用域内[n≤3、全token CMU収録、ガード非該当、`Bi-us`型はU-BI次第]): 提案判定でPASSした率 = 100%(層B)。ASR garbage/OOV起因はASR限界として別掲、失敗に含めない | 未達=REJECTED(判定規則の不備)/USER_DECISION_REQUIRED(適用域の線引き) |
| A2 | 負例(近音・脱落・追加・文字読み・OOV・数値・K5型): **新規誤PASS = 0**(現行NG∧提案PASS=0)。現行でPASSする既存の穴(EX1-3)は悪化・拡大させない(提案でPASS件数が増えない) | 1件でも=REJECTED |
| A3 | Regression: 既存1:1同音、story-making、Case A、空白差、複合語、数値/否定ガード、Golden(MDJF 193＋保存転写全体4,032[pairs_02。v1は3,493])で**PASS→NG=0**、NG→PASS全件を一覧化し『音素一致』を機械判定＋目視確認(想定外0) | 未達=REJECTED |
| A4 | 実音声負例(F4-F11): 層CでPASSした件数 = 0。『構成ラベル疑義』は除外あり/なし両方で0 | 未達=REJECTED |
| A5 | 同一音声のASR反復(最大2回): 判定反転の有無を報告(反転があれば原因=ASRの非決定性かValidatorかを層で切り分け) | 報告のみ(反転が提案起因ならREJECTED) |
| A6 | 費用がCap内、Production・Ledger・既存成果物の変更0(sha256不変) | 逸脱=STOP/報告 |
| A7 | 層A/層Bが分離して報告されている(エンジン別) | 欠落=不完全 |
| A8 【v2・R-04】 | 判定挙動の変化4点(a数字ゲート例外/bM1矛盾拒否/cconnected-speech迂回/dF1残差1:1限定)がケース表(NX1,CS1-CS3,RS1)とunit testで固定され、各点の『変化後の判定』が事前に記録した値と一致し、**PASS→NG 0**。NX1(two→to)は新規PASSの種類が増えるため、Fableが個別に『許容できる同音の延長』か判定 | 逸脱=REJECTED/USER_DECISION_REQUIRED |
| A9 【v2・R-02】 | `Bi-us`型(BI1/BI)は、ユーザー判断U-BIの結果に従う: B0=層CでPASSした件数0(V8有効)、B1=救済100%。判断前は両方を併記 | U-BI未回答でも他基準は判定可能 |

『同等以上』判定は件数ベースで、有意性は主張しない(標本は小さい。外挿は『保存データ上の発生率0.10%[4/4,032]、全て1記事由来』の制約付き)。

## 6. 段階と有料/無料の切り分け【v2】

| 段階 | 内容 | API/費用 | 開始条件 |
|---|---|---|---|
| **O0(実施済み)** | 保存転写の再適用: **pairs_02 4,032ペア**(委任_01の3,493＋`human_review_queue.jsonl`[er006/er007他、235ペア]・`runtime_evidence_{x,z}.json`+fixtures・MDJF golden 193件[191ユニーク]・tts_results追加形式)、ASR 3方式比較Trialの保存転写544件[ラベル付き91音声、読取専用]、ケース表30+追加8件、ガードablation(V1〜V8)、適用域456組の列挙 | 0円(本計画の根拠。再現script=`collect_pairs_02.py`/`measure_v2_01.py`、同dir) | — |
| **O1(PLAN_FIXED後、ASR確定を待たず可)** | (1)純関数のunit test: 正例・近傍負例・G1〜G9・OOV・variant過多・数値/否定・**4-4の4点(a〜d)**・audit key(救済diffにのみ付与)。(2)**提案ルール無効時の出力不変test**(`PROTO_MULTIWORD`未呼出で現行出力とバイト単位一致。11-7のflagは使わないため『DefaultOffIsolation型』ではなく旧挙動の回帰test。【v2・R-12】)。(3)**目視レビュー用リスト**(0円): 理論域456組のうち『代表以外のvariantでのみ一致=27』『ストレス除去でのみ一致=172』『stopword(a/theなど)のvariant経由で一致=19(stopword含有は317)』を`triples_review_list_01_vocab01.json`から抽出して人間/Fableが目視。『1音素摂動の負例バンク』は完全一致規則に対し構造的に必ず合格する(ほぼ自明)ため削除【v2・R-07】。(4)3方式比較Trial完了後は転写キャッシュを読み取り専用で再適用 | 0円 | PLAN_FIXED。3方式比較の設定・進行は変更しない |
| **P1(ASR確定後)** | 構成音声**13本**のTTS生成(Gemini TTS)＋新Primary/Secondary(確定構成)のASR、既存wav約5本の再ASR(TTS 0円)、層A/B/C集計 | 有料(§7、見積約18〜28円、Cap JPY50) | PLAN_FIXED ∧ Primary/Secondary確定 ∧ ユーザー承認(新仕様Trialのため金額によらず承認・7-7) |
| ~~P2~~ | **【v2・R-08】削除**: 案B2(T2b有効性・negative cache・費用実測)は#133判断後の別計画へ分離(今回のFix範囲外) | — | — |

## 7. 費用・時間の見積(概算と不確実性)【v2・R-06】

根拠: `docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/TRIAL_DESIGN_01.md` §4(OpenAI約0.0154円/回、Azureは音声秒切上×$1/h≒0.044円/秒、新規TTS 8本≈1〜3円)、`TRIAL_RESULT_01.md`(Azure実測平均2.2円/呼出[約50秒音声])。160円/USD。確定ASR構成により変動するため上限側で見積もる。
- 構成音声13本: TTS約0.15〜0.4円×13≒2〜5円、ASR(OpenAI 0.015＋Azure 5〜10秒≈0.22〜0.44円、Whisperローカル0)×13≒3〜6円。同一音声のASR反復(A5、約4本×2回)≒2〜3円。
- 既存wav再ASR(TTS 0円): 約5本×Azure約2.2円(約50秒)＋OpenAI約0.08円≒11〜12円。
- **合計約18〜28円**(v1の約25〜40円・上限60円から縮小)。**Cap案 = JPY 50**(見積上限の約1.8倍。v1はP1=JPY100・P2=JPY50)。**新仕様のTrialのため、金額によらずユーザー承認が必要(7-7)**。確定はFable/ユーザー。日次1,000円は他Trialとの並走で超過見込みなら事前承認(7-9)。
- 時間: TTS＋ASR＋集計で数時間(Whisperローカル含む)。必要なら『要試聴』のみユーザーが短時間試聴。
- 量産単価への影響(案A採用時): 実行時 0円/記事(API 0、CMU辞書引きのみ)。期待値は再試行削減(byUs型1件約5円＋cooldown 10分)×発生率(4,032ペア中4=0.10%)＝記事あたり0〜0.1円オーダーの微減。B1は11〜16円/記事悪化見込み(非推奨)、B2は別計画。

## 8. ASR選定確定後に差し替える条件(チェックリスト)

**依存の現況(2026-10-21時点、読取りのみ)**: ASR-THREE-WAY-COMPARISON-TRIAL-01は`TRIAL_DONE_PENDING_FABLE`(OPEN-438、`docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/TRIAL_RESULT_01.md`)。所見として『Primary入替は現行を上回る証拠なし』『KP限定dual-pass[C1dK/C5K]のOffline Trial次段階化が判断候補』『Whisper第3意見運用の許容』が挙がっているが、**新Primary/Secondaryはユーザー未確定**。本Trialは確定を待つ。以下は確定後に差し替える項目。

1. 確定したPrimary/Secondaryのエンジン・モデルID・SDK版(P1の層A/B/C対象と費用単価)。
2. エンジン固有の入力(Azure Phrase List＝Ledger hint由来／OpenAI prompt／Whisper hotwords・initial_prompt)の有無と内容。供給なし条件を基準にし、供給ありは別腕で分ける(PLが誤発音を隠すK5型の混入を避けるため、PL有の転写は独立証拠として使わない)。
3. 統一judge構成(Primary PASSならSecondary不要／force_secondary＝両方PASS必須／Secondary役割の入替)。`secondary_accept_fn`経路で`HOMOPHONE_EQUIVALENT`が使えること。
4. 転写の表層差(句読点・大文字小文字・数値表記・『Buy us』の分かち方)が`val.tokenize`で吸収されること(Whisper出力で再確認)。
5. 再測定: 保存転写再適用の対象に新構成の転写キャッシュ(3方式比較Trial)を追加し、判定変化の件数・内訳・エンジン別多語化率を更新。効果量(再試行削減の見込み)をここで再見積もりし、採否判断の材料にする。
6. KP(Key Phrase)とBody(本文)でASR構成が異なる場合は別集計。
7. 費用単価の更新。

**【v2・R-追加採用】ASR構成が変わったとき再評価が必要な6点**:
1. **エンジン別の多語化率**(`byUs`→2語以上に分割する頻度): 保存データではAzureが主因(4/6)。構成が変われば再測定。
2. **表記の癖**: ハイフン(`Bi-us`)・音節区切り・大文字小文字・数字表記の出方。`val.tokenize`はハイフンを空白に変えるためハイフン情報は判定層で失われる(U-BIの判断に影響)。
3. **Phrase List・promptの綴り誘導(K5型)**: 供給があるとPLが誤発音を転写上で隠す(LINE→Lion)ため、供給あり転写は独立証拠として使わず、供給なし条件を基準に別腕で比較する。
4. **Secondary許容判定も同規則**(`sec:993-1002 _secondary_accept`): 新Secondaryでも新ルールが同じ経路で働くこと(Primary単独PASSの`sec:937-951`は既存挙動で、R-10の整理は`INVESTIGATION_01.md` §8-1)。
5. **KPと本文で構成が違う場合の別集計**: 本文とKey Phraseで新Primary/Secondaryが異なるなら、救済率・誤PASSを別々に集計する。
6. **M1矛盾拒否の頻度**(4-4 b): 新規ルールでSecondary側の`TRUE_CONTENT_MISMATCH`が`UNCERTAIN`に変わる件数を、確定構成の転写で再測定する。

## 9. 安全・隔離

- Trialコードは`docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/`配下のDEV専用。提案判定は`val.protected_check`をメモリ上でpatchして呼出（ファイル無編集）。Production経路にimportされない。実行前後で`git status`と主要ファイルsha256の不変を確認。
- 実Ledger・human_review_queue・telemetry・cost loggerへ書き込まない（Trial dirへ隔離。PNEP `TrialIsolation`の方式を踏襲）。
- Production採用はVALIDATED後にユーザーが判断。11-7限定例外(flag)は使わない(Trial段階で隔離が完結するため)。採用時も、新規audit key `multiword_homophone`を**救済が成立したdiffにのみ付ける(条件付き・additive、既存testのkey集合完全一致[`er006_multi_diff_judge_fix_test_01.py:153`]を壊さない)**案を推奨(R-09)。
- Opus独立技術レビュー: 委任_01の計画に対し実施済み(OF-PNMH-R-01〜13、`OPUS_FINDINGS_LEDGER`)。v2は反映後。Trial実行前に変更が大きければ再レビュー(Fable判断)、Production採用提案前は条件C。

## 10. 成果物（Trial実行時）

`TRIAL_RESULT_01.md`(層A/B/C表、ケース別現行/提案判定、新規PASS/NG一覧、費用実測、使用モデル名・最新か・最新でない場合の理由[25節]、ASR構成)、`results_*.json`、test。保存先は本dir（新規の証跡置き場を作らない）。


---
## v3 Fix(2026-10-22ユーザー判断反映、委任_03。Status=`PLAN_FIXED_WAITING_ASR_SELECTION`。上のv2本文は履歴として保持し、矛盾時は本節が優先)
出典: `docs/pm/delegation_log/2026-10-22_PNMH-PLAN-FIX-AND-ASR-PASS-CONDITION-AUDIT-01_USER.md` §2。承認されたのは『計画v2の基本方針とTrial計画』であり、Production採用ではない(VALIDATED≠APPROVED_FOR_PRODUCTION≠PRODUCTION_WIRED)。

1. **ラベル確定**: `Bi-us`型(BI1/BI2)=**NOT_PASS**(U-BI=NG維持、V8有効)。v2の『U-BI待ち・両ラベル併記』『A9のB0/B1併記』は**B0のみ**に確定(A9: 層CでPASS 0)。`bias`⇔`by us`(BI3)は音素同一のため期待=PASS(既知の残存、層Cで要審査)。
2. **合格基準A1〜A9へのv3追加**: ストレス差のみの正例は救済100%、音素相違(PH1/PH2/N1〜N7)は誤PASS 0、entity_likeは代表発音のみで比較(`today→to day`は全variantならPASS・代表発音ならNG、unit testで固定)。
3. **ケース表**: `TRIAL_CASES_01.json`は41件(+BI1/BI2/NX1/CS1-3/RS1/H1/BI3/PH1/PH2)。v3判定は全件期待どおり(`update_cases_v3_01_result.txt`)。
4. **実行条件**: P1は『新Primary/Secondary確定のユーザー通知』をトリガーとし、Cap案JPY50(見積18〜28円)。**現時点では実行しない**。確定前は有料API/TTS/ASRを使わない。§8チェックリストはそのまま使う。
5. **O1実施済み(0円)**: `test_proto_multiword_span_v3_01.py` 20件PASS。O0(4,032ペア)は再実行で保存結果とバイト一致(前提不変)。
6. **U5**: 既存の穴(EX1〜EX3・H1)はユーザー未回答のためKEEP(悪化させない・是正しない)のまま。
