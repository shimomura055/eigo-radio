# TRIAL_PLAN_01: 1語⇔複数語の同音救済(案A)＋期待発音源(#133縮小統合)の検証計画

管理ID: PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_01 / Status管理ラベル: `PLAN_DRAFT_PENDING_FABLE_REVIEW`
**本書は計画であり、Trialは開始しない。** 新Primary/Secondary確定(ASR-THREE-WAY-COMPARISON-TRIAL-01の結果＋ユーザー確定)と、ユーザーによる本計画のFixまで、有料API・TTS/ASR・Production変更は行わない。計画完成を理由にTrialへ自動移行しない。
対象方式: `DESIGN_OPTIONS_01.md` §3-§4(案A-all＋ガード、案B2は条件付きサブTrial)。

## 1. Status遷移

`PLAN_DRAFT_PENDING_FABLE_REVIEW`(現在) → Fable独立レビュー(+Opus条件A) → 委任_02で改訂 → **`PLAN_FIXED`(ユーザー確認・Fix)** → [ASR 3方式比較の結果・ユーザーのPrimary/Secondary確定] → `TRIAL_READY`(差替え条件§8反映) → `TRIAL_RUNNING` → `TRIAL_DONE_PENDING_FABLE` → **`VALIDATED`**(合格基準§5を満たす) / **`REJECTED`**(新規誤PASSがある等) / **`USER_DECISION_REQUIRED`**(基準の境界・新仕様判断)。VALIDATED≠APPROVED_FOR_PRODUCTION≠PRODUCTION_WIRED(Production採用は人間ユーザーのみ)。

## 2. 前提とラベルの扱い

- **ラベルの原則**: 「正例」=聴感上canonicalと同じ音で、救済(PASS)すべき。「負例」=音が違う/語が脱落・追加されている/誤読で、新たに誤PASSしてはならない。「KEEP」=現行判定を変えない(Regression、および既存の穴を悪化・拡大させない確認)。**ASRの出力そのものを正解にしない**(音声の正解は、構成音声ではTTS入力文＝既知のspoken text、実音声では多数決/試聴)。
- **byUsの期待発音に関する条件付きラベル**: byUsの公式EN発音は未確認(J7依存)。案Aの信頼の土台は『期待発音＝CMU収録綴りの発音』(現行1:1救済と同じ)で、byUsでは`B AY AH S`。
  - シナリオS1(J7=認める、または期待発音を`bias`系`B AY AH S`として確定): byUs/bias/by us/buy usの転写は全て正例。
  - シナリオS2(J7=認めない、未確認のまま): byUsを『確認済み正例』と呼ばない。ただし`B AY AH S`系の聴取音は現行1:1救済と同水準で扱う。合格基準は同じ(`buy us`救済は現行の`Bias`救済と同じ信頼土台)。レポートにはS1/S2どちらで評価したかを明記する。
  - どちらでも、**『byUsの正しい発音をAIが確定した』とは主張しない**。
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

### 3-2. 追加ケース(有料Trialで新規に作る構成音声。designed audio)
TTS入力文を意図的に変えた音声で、(a)ASRの生認識、(b)救済後判定、を分離して測る。carrier文2種(C1=`LINE Manga has launched byUs, an AI service that lets you shape stories.` / C2=`Make one yourself with byUs.`)×声2種(Std lineupの男女各1)×spoken form:

| ID | TTS入力(spoken) | 期待(S1) | 狙い |
|---|---|---|---|
| F0 | `byUs`(そのまま) | 試聴/多数決で別途ラベル | TTSの実際の読み(BIOS等)。ラベル不明なら混同行列に入れず『要試聴』報告 |
| F1 | `bias` | 正例 | 同音(1:1、現行でも救済) |
| F2 | `by us` | 正例 | 同音(n:m、空白差) |
| F3 | `buy us` | 正例 | 同音(n:m、綴り違い=本命) |
| F4 | `bios` | 負例 | 近音(実ASR出力BIOSの再現) |
| F5 | `buys` | 負例 | 近音(Z/S) |
| F6 | `bus` | 負例 | 近音(母音) |
| F7 | `buy`(`us`脱落) | 負例 | 単語の脱落 |
| F8 | `buy us us` | 負例 | 単語の追加(重複) |
| F9 | `B Y U S`(文字読み) | 負例 | 文字読み(綴り読み) |
| F10 | `bayas` | 負例 | 実ASR出力(Baias/BAYAS)型の辞書外近似音 |
| F11 | `by us`の後に語を追加(`by us now`) | 負例 | 追加(carrierに無い語) |

計48クリップ(F0 4本＋F1-F11 44本)。TTSがcanonical側へ自動補正した可能性がある音声(全エンジンの転写がcanonicalと一致する負例)は『構成ラベル疑義(要試聴)』として除外あり/なし両方で集計(3方式ASR比較Trialの方式を踏襲)。
LINE→Lion型(K5)の実音声負例は、既存の保存wav(run_byus_01)があれば**再ASRのみ**(TTS 0)で追加する。
**固有名詞以外**の適用リスク確認: 一般語の正例(`already/all ready`型)・誤差(`places/place is`型)は§3の合成ケース＋適用域列挙(`rule_domain_result_01.json`)で扱い、有料音声は作らない(必要なら1〜2語種を追加。スコープ判断U1の結果に依存)。

## 4. ASR生認識精度と救済後判定の分離評価

各クリップ×各エンジンについて、『focal span』(carrier内のbyUs相当区間)を次の3層で別々に記録する(同じ表で混ぜない):
- **層A ASR生認識(Validator前)**: (A1)focal spanの綴り一致率(転写のfocal span＝spoken text)、(A2)音素一致率(CMUでspoken textと転写focal spanの音素列が一致)、(A3)garbage率(OOV・無関係語)、(A4)エンジン別の多語化率(`byUs`→2語以上)。判定ロジックは一切通さない。
- **層B Validator救済**: 『層Aで綴りは不一致だが音素一致(A2∧¬A1)』のうち、現行判定でPASSした率(ベースライン)と提案判定でPASSした率(**救済率＝提案の寄与**)。『音素不一致』のうち提案でPASSした率(**誤PASS率**。新規誤PASS＝現行NG∧提案PASS)。
- **層C 最終**: ラベル(正例/負例/KEEP)に対する混同行列。Primary単独/Secondary救済/統一judge全体の3視点(構成C1: 現行、C1d: force_secondary 等、ASR確定構成に合わせる)。
層Aの低さ(Whisperがgarbageを返す等)は『ASR限界』として層Bの失敗にカウントしない。層Bは『音素が一致しているのにNGのまま』の件数のみ失敗とする。

## 5. 合格基準(事前固定。ユーザー基本受入条件『既知の正例を救済し、既知の負例を新たに誤PASSしない』)

| # | 基準 | 判定 |
|---|---|---|
| A1 | 正例(音素一致かつ適用域内[n≤3、全token CMU収録、ガード非該当]): 提案判定でPASSした率 = 100%(層B)。ASR garbage/OOV起因はASR限界として別掲、失敗に含めない | 未達=REJECTED(判定規則の不備)/USER_DECISION_REQUIRED(適用域の線引き) |
| A2 | 負例(近音・脱落・追加・文字読み・OOV・数値・K5型): **新規誤PASS = 0**(現行NG∧提案PASS=0)。現行でPASSする既存の穴(EX1-3)は悪化・拡大させない(提案でPASS件数が増えない) | 1件でも=REJECTED |
| A3 | Regression: 既存1:1同音、story-making、Case A、空白差、複合語、数値/否定ガード、Golden(MDJF 193＋保存転写全体3,493)で**PASS→NG=0**、NG→PASS全件を一覧化し『音素一致』を機械判定＋目視確認(想定外0) | 未達=REJECTED |
| A4 | 実音声負例(F4-F11): 層CでPASSした件数 = 0。『構成ラベル疑義』は除外あり/なし両方で0 | 未達=REJECTED |
| A5 | 同一音声のASR反復(最大2回): 判定反転の有無を報告(反転があれば原因=ASRの非決定性かValidatorかを層で切り分け) | 報告のみ(反転が提案起因ならREJECTED) |
| A6 | 費用がCap内、Production・Ledger・既存成果物の変更0(sha256不変) | 逸脱=STOP/報告 |
| A7 | 層A/層Bが分離して報告されている(エンジン別) | 欠落=不完全 |

『同等以上』判定は件数ベースで、有意性は主張しない(標本は小さい。外挿は『保存データ上の発生率0.11%、全て1記事由来』の制約付き)。

## 6. 段階と有料/無料の切り分け

| 段階 | 内容 | API/費用 | 開始条件 |
|---|---|---|---|
| **O0(実施済み)** | 保存転写3,493ペアの再適用、ASR 3方式比較Trialの保存転写544件[ラベル付き91音声、読取専用]への再適用[変化0・問題音声の新規PASS 0]、ケース表30件、ガードablation、適用域・需要の列挙 | 0円(本計画の根拠。再現script同dir) | — |
| **O1(PLAN_FIXED後、ASR確定を待たず可)** | (1)純関数のunit test(正例・近傍負例・ガード・OOV・variant過多・数値/否定)、(2)DefaultOffIsolation型(提案無効で出力不変・副作用0)、(3)CMUから機械生成する近傍音負例バンク(各正例について1音素置換/脱落/追加/語順入替、数百件)でNew false PASS=0、(4)ASR 3方式比較Trialの完了後はその転写キャッシュを**読み取り専用**で再適用(再利用可否は未確認) | 0円 | PLAN_FIXED。3方式比較の設定・進行は変更しない |
| **P1(ASR確定後)** | 構成音声48本のTTS生成＋新Primary/Secondary(確定構成)＋(参考)3方式でのASR、層A/B/C集計、K5型の既存wav再ASR | 有料(§7) | PLAN_FIXED ∧ Primary/Secondary確定 ∧ ユーザー承認(費用Cap) |
| **P2(任意・サブTrial)** | 案B2: T2b(Wikipedia/Wiktionary/Wikidata発音欄の決定的取得)の有効性(Triangeln/Ottoni/Seishiro等のCMU辞書外名・実需要語)と、反応的調査＋negative cacheの費用実測。HTTP取得は費用0見込み、web_searchを使う場合のみ有料 | 0〜約40円(未測定) | #134(調査手段)と合わせてユーザー判断。P1とは独立に実施可 |

## 7. 費用・時間の見積(概算と不確実性)

根拠: `docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/TRIAL_DESIGN_01.md` §4(OpenAI約0.0154円/回、Azureは音声秒切上×$1/h、新規TTS 8本≈1〜3円)、`TRIAL_RESULT_01.md`(PNEP: Azure実測平均2.2円/呼出[約50秒音声]、web_search研究約5.4円/名)。160円/USD。
- P1: TTS 48本×約0.15〜0.4円＝約7〜19円、ASR(OpenAI 0.015＋Azure 5秒≈0.22円＋Whisperローカル0)＝約0.24円×48≈12円、反復(12本×2回)≈6円。**合計約25〜40円、余裕を見て上限約60円**。時間: TTS＋ASR＋集計で数時間(Whisperローカル含む)。必要なら『要試聴』のみユーザーが短時間試聴。
- P2: HTTP取得のみなら0円、web_search併用で名あたり約5円(未測定)。
- Cap提案: P1 = JPY 100(上限60円の約1.7倍)、P2 = 別途JPY 50。**確定はFable/ユーザー(新仕様のため7-7の『新仕様=金額無関係に承認』に該当)**。日次1,000円は他Trialとの並走で超過見込みなら事前承認(7-9)。
- 量産単価への影響(案A採用時): 実行時 0円/記事(API 0、CMU辞書引きのみ)。期待値は再試行削減(byUs型1件約5円＋cooldown 10分)×発生率0.11%＝記事あたり0〜0.1円オーダーの微減。B2は未測定、B1は11〜16円/記事悪化見込み(非推奨)。

## 8. ASR選定確定後に差し替える条件(チェックリスト)

**依存の現況(2026-10-21時点、読取りのみ)**: ASR-THREE-WAY-COMPARISON-TRIAL-01は`TRIAL_DONE_PENDING_FABLE`(OPEN-438、`docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/TRIAL_RESULT_01.md`)。所見として『Primary入替は現行を上回る証拠なし』『KP限定dual-pass[C1dK/C5K]のOffline Trial次段階化が判断候補』『Whisper第3意見運用の許容』が挙がっているが、**新Primary/Secondaryはユーザー未確定**。本Trialは確定を待つ。以下は確定後に差し替える項目。

1. 確定したPrimary/Secondaryのエンジン・モデルID・SDK版(P1の層A/B/C対象と費用単価)。
2. エンジン固有の入力(Azure Phrase List＝Ledger hint由来／OpenAI prompt／Whisper hotwords・initial_prompt)の有無と内容。供給なし条件を基準にし、供給ありは別腕で分ける(PLが誤発音を隠すK5型の混入を避けるため、PL有の転写は独立証拠として使わない)。
3. 統一judge構成(Primary PASSならSecondary不要／force_secondary＝両方PASS必須／Secondary役割の入替)。`secondary_accept_fn`経路で`HOMOPHONE_EQUIVALENT`が使えること。
4. 転写の表層差(句読点・大文字小文字・数値表記・『Buy us』の分かち方)が`val.tokenize`で吸収されること(Whisper出力で再確認)。
5. 再測定: 保存転写再適用の対象に新構成の転写キャッシュ(3方式比較Trial)を追加し、判定変化の件数・内訳・エンジン別多語化率を更新。効果量(再試行削減の見込み)をここで再見積もりし、採否判断の材料にする。
6. KP(Key Phrase)とBody(本文)でASR構成が異なる場合は別集計。
7. 費用単価の更新。

## 9. 安全・隔離

- Trialコードは`docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/`配下のDEV専用。提案判定は`val.protected_check`をメモリ上でpatchして呼出（ファイル無編集）。Production経路にimportされない。実行前後で`git status`と主要ファイルsha256の不変を確認。
- 実Ledger・human_review_queue・telemetry・cost loggerへ書き込まない（Trial dirへ隔離。PNEP `TrialIsolation`の方式を踏襲）。
- Production採用はVALIDATED後にユーザーが判断。11-7限定例外(flag)は使わない(Trial段階で隔離が完結するため)。採用時も、新規audit key `multiword_homophone`(additive)で救済件数を追跡可能にする案を推奨。
- Opus独立技術レビュー: 本計画は『新しい判定ルールの設計(条件A)』に該当する見込みのため、Trial実行前のOpus条件Aレビューを推奨(Fable判断)。Production採用提案前は条件C。

## 10. 成果物（Trial実行時）

`TRIAL_RESULT_01.md`(層A/B/C表、ケース別現行/提案判定、新規PASS/NG一覧、費用実測、使用モデル名・最新か・最新でない場合の理由[25節]、ASR構成)、`results_*.json`、test。保存先は本dir（新規の証跡置き場を作らない）。
