# ROUND5_REPORT_01: FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-04 Round 5 (2026-10-13、委任_02)

到達上限 VALIDATED(Trial)。Production変更なし。採用判断なし。ユーザー承認(2026-10-13): 音声Prompt探索 TRIAL-03 の予算を¥300まで(Trialのみ、累計上限¥300、ハードストップ¥290)。

**結論: 単一Promptで両レベル合格(Take1)は0件(N01-N04 Take1 8call、M05 Take2/3 4call、計12call)。Fable記録の条件により「無益STOP」に該当(Round 6は行わず総括へ)。Step C(再現性)・Step D(試聴ページ)は条件未達のため未実施。M05はStd 1/3・Adv 0/3合格で再現せず。最良到達はN01(Std暫定合格、Adv速度167.1[+0.1]・長無音1・ASR OKだが文末平均627msが基準593msを34ms超過)とN02(両レベル速度圏内、文末平均がStd+16ms/Adv+7ms超過)。**

モデル: gemini-3.8-flash-lite-tts(要求=応答model_version、Family-X TTSの最新世代ライン、最新)、voice Aoede、speech_metadata方式。Primary ASR=gpt-4o-mini-transcribe、速度測定はfaster-whisper small(local)。測定条件・判定基準はRound 4と同一(Std 157±6 / raw 167±6 / Adv 167±6、文末平均Std≤498・Adv≤593ms[510は参考列]、長無音(>=800ms)≤1、ASR OK、long_gap(medium+)なし、tts_input sha一致assert通過)。n=1〜3は方向の目安。

## 1. 候補
- M05(Round 4、30語、再利用。style sha c915f73aをgen時にassert): `A warm, bright storyteller telling a true story, going slightly slower than usual. Finish every sentence fully, then move straight to the next one, even when the story changes direction.`
- N01〜N04は2節。

## 2. Step A 設計と自己点検(`prompts_r5.json`)
- **N01** (37語, sha d1956c91, maxJaccard(J)=M05:0.267, H0=0.05): `A cheerful, kind storyteller sharing a true story at a pace a little slower than usual. Bring each sentence to its natural close, then go directly on to the next, including where the story takes a turn.`
  - 軸: speed=a little slower than usual(M05のslightly slowerを別表現、1回) / pause=文を自然な終わりまで言い切り→直接次へ。話の転換でも同様(肯定形、M05と別表現) / voice=陽気で優しい語り手 / strength=中 / structure=像+ペース+言い切り→次へ(話題転換節あり)
  - 意図: M05の言い切り→次へ直行を別表現に書き換え、構造の頑健性を確認(話題転換節は維持)。
  - 根拠(Round1知見): M05(Std全指標圏内、Adv数値圏内でASRのみ不合格)
  - 想定副作用: 別表現でM05の効きが再現しない/Advが速い
- **N02** (25語, sha a08fc23c, maxJaccard(J)=M05:0.821, H0=0.096): `A warm, bright storyteller telling a true story, going slightly slower than usual. Finish every sentence fully, then move straight on to the next one.`
  - 軸: speed=slightly slower(M05と同一語、1回) / pause=語尾を最後まで言い切って次へ直行(肯定形、話題転換節なし) / voice=温かく明るい語り手 / strength=中 / structure=像+減速+言い切り→次へ(話題転換節を除去した切除比較。M05に対し1語'on'のみ差、部分文字列回避)
  - 意図: M05から話題転換節(even when the story changes direction)を除き、その節が寄与しているかを切除比較する。
  - 根拠(Round1知見): M05、Step A/Round4(話題転換指示は長無音を減らさない)
  - 想定副作用: 話題転換節の除去で文末が長くなる/変化なし
- **N03** (39語, sha d29d7371, maxJaccard(J)=M05:0.794, H0=0.081): `A warm, bright storyteller telling a true story, going slightly slower than usual. Read the text word for word exactly as written, finish every sentence fully, then move straight to the next one, even when the story changes direction.`
  - 軸: speed=slightly slower(M05同一語、1回) / pause=言い切り→次へ直行(M05同一) / voice=温かく明るい語り手 / strength=中 / structure=M05+書かれた通りに一語ずつ読む肯定形指示(want→wanna対策、新軸=忠実読み)
  - 意図: M05のAdv ASR不合格(want→wanna)に対し、書かれた通りに読む肯定形指示でASR一致が改善するかを見る。
  - 根拠(Round1知見): Round4 M05/M06 Adv(want→wanna)
  - 想定副作用: 忠実読み指示が1語ずつの区切りを生み文中無音が増える/Stdが遅くなる
- **N04** (24語, sha efb6821e, maxJaccard(J)=M05:0.333, H0=0.08): `A friendly, bright narrator telling a true story at a measured pace. Finish each sentence fully, then go on to the next at once.`
  - 軸: speed=measured pace(1回) / pause=言い切って即次へ(肯定形、話題転換節なし) / voice=親しみのある明るいナレーター / strength=中 / structure=像+measured+言い切り→次へ(M05構造のmeasured版、話題転換節なし、2文)
  - 意図: M06のStd文末長・長無音を、話題転換節なしのmeasured+言い切り→次へで改善できるか、Adv速度安定を見る。
  - 根拠(Round1知見): M06(Std 535ms/長無音1)、M05
  - 想定副作用: measuredの減速力が弱くAdvが速い

- 自己点検: N01-N04 sha全相異、J/K/L/M/H0とsha相異(assert済)。N内最大Jaccard: N02-N03=0.657, N02-N04=0.406, N01-N04=0.342, N01-N02=0.317, N03-N04=0.279, N01-N03=0.231 / J/K/L/M/H0を部分文字列に含む・含まれる候補なし(assert済)。最大Jaccard: N01:M05=0.267, N02:M05=0.821, N03:M05=0.794, N04:M05=0.333 / H0: N01=0.05, N02=0.096, N03=0.081, N04=0.08 / 矛盾なし。N02はM05からの意図的切除比較で語彙がM05に極めて近い(Jaccard高)が1語差で部分文字列ではない。N03はM05構造+忠実読み指示。 / 速度語は各1回(slower/measured)、数値WPM・unhurried/slowly・否定形・位置語なし(assert済)。2文×4。
- 注記: N02はM05から話題転換節を除く『切除比較』のため、M05との語彙重複が高い(Jaccard 0.821)。M05に対し『on』1語を加えて部分文字列判定を避けた(委任文『全て一から書く』に対する切除比較ゆえの例外的扱い。Fable確認事項)。N03もM05+忠実読み指示(Jaccard 0.794)。

## 3. 測定全表(基準=H0 Take1・現行v5を先頭。M05 Take1はRound 4再利用)
3列=WPM実測(Std減速後)/raw換算(Std÷0.94)/Adv実測。

| 候補 | take | Lv | WPM実測(目標差) | raw換算(167差) | 発話WPM | 文末無音 平均/中央/最大ms | 文中無音 本/計s/300ms+ | 800ms+ | Primary ASR | 末尾 | 異音med+ | ピッチ幅st/強弱幅dB | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 Take1(TRIAL-02再利用) | - | std | 157.3 | 167.3 | 175.3 | 498/525/890 | 37/3.69/2 | 1 | NORMALIZED_MATCH | - | 0 | 9.79/17.3 | 基準 |
| H0 Take1(TRIAL-02再利用) | - | adv | 166.9 | 166.9 | 179.3 | 593/570/750 | 49/5.92/5 | 0 | NORMALIZED_MATCH | - | 0 | 10.34/16.6 | 基準 |
| 現行v5 | - | std | 145.5 | 154.8 | 172.7 | 694/630/1050 | 38/3.83/1 | 4 | - | - | 1 | 9.54/17.4 | 基準 |
| 現行v5 | - | adv | 166.9 | 166.9 | 172.3 | 456/460/740 | 49/6.21/6 | 0 | - | - | 0 | 10.13/18.0 | 基準 |
| M05 | 1 | adv | 172.7 (+5.7) | 172.7 (+5.7) | 190.3 | 587/620/650 | 42/5.57/7 | 0 | TRUE_CONTENT_MISMATCH | OK | 0 | 11.22/16.9 | 不合格(ASR/異音) |
| M05 | 2 | adv | 176.1 (+9.1) | 176.1 (+9.1) | 189.7 | 587/600/720 | 41/5.43/5 | 0 | NORMALIZED_MATCH | OK | 0 | 10.63/17.6 | ポーズのみOK(速度外) |
| M05 | 3 | adv | 180.2 (+13.2) | 180.2 (+13.2) | 191.2 | 544/540/700 | 49/5.17/3 | 0 | NORMALIZED_MATCH | OK | 1 | 11.58/18.1 | ポーズのみOK(速度外) |
| M05 | 1 | std | 158.6 (+1.6) | 168.7 (+1.7) | 170.4 | 473/475/760 | 33/3.08/1 | 0 | NORMALIZED_MATCH | OK | 0 | 10.53/16.9 | 暫定合格 |
| M05 | 2 | std | 148.3 (-8.7) | 157.8 (-9.2) | 169.2 | 628/605/1070 | 38/4.04/2 | 2 | NORMALIZED_MATCH | OK | 0 | 9.92/16.9 | 不合格 |
| M05 | 3 | std | 148.8 (-8.2) | 158.3 (-8.7) | 161.6 | 493/470/710 | 42/4.58/3 | 0 | NORMALIZED_MATCH | OK | 0 | 9.53/17.9 | ポーズのみOK(速度外) |
| N01 | 1 | adv | 167.1 (+0.1) | 167.1 (+0.1) | 189.1 | 627/590/830 | 46/6.62/9 | 1 | NORMALIZED_MATCH | OK | 0 | 9.35/16.5 | 速度のみOK(ポーズ不良) |
| N01 | 1 | std | 153.5 (-3.5) | 163.3 (-3.7) | 166.9 | 494/505/800 | 40/3.58/2 | 0 | NORMALIZED_MATCH | OK | 0 | 12.41/17.7 | 暫定合格 |
| N02 | 1 | adv | 170.9 (+3.9) | 170.9 (+3.9) | 186.3 | 600/530/850 | 45/5.58/6 | 1 | NORMALIZED_MATCH | OK | 0 | 10.6/16.9 | 速度のみOK(ポーズ不良) |
| N02 | 1 | std | 161.3 (+4.3) | 171.6 (+4.6) | 177.9 | 514/500/800 | 34/3.74/2 | 1 | NORMALIZED_MATCH | OK | 0 | 9.77/17.1 | 速度のみOK(ポーズ不良) |
| N03 | 1 | adv | 174.7 (+7.7) | 174.7 (+7.7) | 190.7 | 613/600/780 | 40/4.54/3 | 0 | NORMALIZED_MATCH | OK | 0 | 10.36/18.2 | 不合格 |
| N03 | 1 | std | 165.3 (+8.3) | 175.9 (+8.9) | 182.2 | 542/495/1040 | 29/2.7/2 | 1 | NORMALIZED_MATCH | OK | 0 | 9.17/15.7 | 不合格 |
| N04 | 1 | adv | 191.5 (+24.5) | 191.5 (+24.5) | 197.8 | 434/400/730 | 29/3.67/3 | 0 | TRUE_CONTENT_MISMATCH | OK | 1 | 9.29/16.6 | 不合格(ASR/異音) |
| N04 | 1 | std | 159.6 (+2.6) | 169.8 (+2.8) | 172.0 | 464/410/820 | 37/3.38/2 | 1 | NORMALIZED_MATCH | OK | 0 | 11.22/17.5 | 暫定合格 |

## 4. M05の再現結果(3 take、Std/Adv)
| 項目 | Take1 | Take2 | Take3 | 平均/結果 |
|---|---|---|---|---|
| Std raw換算WPM | 168.7 | 157.8 | 158.3 | 161.6(幅10.9) |
| Std 文末平均ms/長無音 | 473/0 | 628/2 | 493/0 | 531 |
| Std 判定 | 暫定合格 | 不合格(速度-9.2・文末628・長無音2) | ポーズのみOK(速度-8.7外) | **合格1/3** |
| Adv WPM | 172.7 | 176.1 | 180.2 | 176.3(幅7.5) |
| Adv 文末平均ms/長無音 | 587/0 | 587/0 | 544/0 | 573 |
| Adv 判定 | ASR不合格(wanna) | ポーズのみOK(速度+9.1外) | ポーズのみOK(速度+13.2外) | **合格0/3** |
- Std速度は3 takeで157.8〜168.7とばらつく(n=3)。Advは176〜180で一貫して基準167+6を超える(速い側)。
- **want→wanna型の内容逸脱はTake2/3で再現せず**(Primary ASRはTake2/3とも全NORMALIZED_MATCH、ASR文面にwanna出現0)。M05 Advのwannaは3 takeでTake1の1回のみ。
- Fable記録『3 take中Std 3/3かつAdv 2/3以上でM05も試聴ページ対象』は非該当(Std 1/3、Adv 0/3)。軽微不合格の範囲(速度±8・文末+30ms以内)でもStd Take2/3は速度-9.2/-8.7、Adv Take2/3は+9.1/+13.2で範囲外。

## 5. 軸別の効き方(Round 5、n=1〜3の方向の目安)
- **N01(言い切り→次へ直行の別表現+話題転換節あり)**: Std raw 163.3(-3.7)/494ms/長無音0/ASR OK=**暫定合格**(M05と別表現でも言い切り→次へ構造がStdに効く)。Adv 167.1(+0.1、目標167にほぼ一致)/長無音1(830ms、continue.→The)/ASR OK/異音medium+なしだが、文末平均627msが基準593msを34ms超過=ポーズのみ不合格。Std-Adv raw差-3.8(単一Promptで両レベルの速度が揃う点では最良級)。
- **N02(M05から話題転換節を除去)**: Std raw 171.6(+4.6)/514ms(基準+16)/長無音1(800ms)、Adv 170.9(+3.9)/600ms(基準+7)/長無音1(850ms)。両レベル速度圏内で文末平均が基準をわずかに超過。**M05(3 take)とN02を比べて、話題転換節の有無で速度・文末・長無音に判別可能な差は無い**(M05 Std raw 157.8〜168.7・文末473〜628ms、N02 171.6/514ms。n=1でM05のばらつきに近い)。話題転換節は寄与なし/検出不能。
- **N03(M05+書かれた通りに一語ずつ読む)**: Std raw 175.9(+8.9)/Adv 174.7(+7.7)で両レベルとも速くなり圏外(M05 3 take平均はStd 161.6/Adv 176.3)。ASRは両レベルNORMALIZED_MATCHでwannaなし。ただしM05自体もTake2/3でwannaが再現しなかったため、**忠実読み指示がwanna抑制に効いたとは判別できない**(M05 Adv wanna=1/3、N03=0/1)。副作用として速くなる傾向(n=1)。
- **N04(measured版+言い切り→次へ、話題転換節なし)**: Std raw 169.8(+2.8)/464ms/長無音1(820ms)=暫定合格。**Advは191.5(+24.5)と極端に速く**、文末434ms、Primary ASRが内容不一致(『pumps his fist』の『his』挿入、wanna型ではない)=不合格。measuredはStdには効くがAdvを下げない(Round 1〜4と同傾向)。
- **相反関係の再確認**: Std暫定合格はM05 T1/N01/N04。Advで速度圏内かつ文末≤593に該当なし(N01は速度OKだが627ms、N02は600ms)。Advが基準に近いと文末が593をわずかに超え、文末が短いPromptは速度が+9〜+24で速くなる傾向。
- **話題転換2箇所の長無音**: Round 5の12wavで≥800msは7本(Std 5: M05 T2に2、N02/N03/N04に各1。Adv 2: N01/N02に各1)で、**全て第5文末(delay.→The/International)または第7〜9文末(continue.→The/US)の話題転換位置**。Round 5もPrompt指示では解消せず。
- 声質(機械指標、参考): ピッチ幅9.17〜12.41st(H0 T1 9.79/10.34)、強弱幅15.7〜18.2dB(H0 17.3/16.6)でH0同等圏(N01 Stdのピッチ幅12.41はやや広い)。異音medium+: M05 Adv T3 click 1(40.97s)、N04 Adv click 1(13.99s)。聴感未確認、最終判断は人間の試聴。

## 6. 判定内訳(Round 5の12call+M05 Take1)
- **両レベル合格(単一Prompt、同一take): 0件**(M05 T1/T2/T3、N01〜N04 T1いずれも)。
- 暫定合格(単一レベル): M05 Std T1、N01 Std、N04 Std(計3)。速度のみOK(ポーズ不良): N01 Adv、N02 Std/Adv(計3)。ポーズのみOK(速度外): M05 Std T3、M05 Adv T2/T3(計3)。不合格: M05 Std T2、N03 Std/Adv(計3)。不合格(ASR): M05 Adv T1(Round 4)、N04 Adv(計2)。
- raw距離(Std/Adv各167からの絶対差の平均): N01 1.9、N02 4.2、M05 T1 3.7、N03 8.3、N04 13.7。

## 7. 再現性(Step C)・試聴ページ(Step D)
- Step C: **未実施**(単一Prompt両レベル合格Take1が0件のため、委任文の条件により実施しない)。
- Step D: **未実施**。3 take全合格または軽微不合格のPromptが無い(M05は4節の通り非該当)。`user_test/coffee_style_h_speed_04/`は作成せず、Playwright evidenceも該当なし。

## 8. STOP判定
| STOP条件 | 該当 | 根拠 |
|---|---|---|
| 成功STOP(単一PromptでStd/Adv 3 take全合格) | 非該当 | 両合格0件 |
| **無益STOP**(Fable記録: Round 5で単一Prompt両合格Take1が出なければ無益STOP) | **該当** | Take1両合格0件。Round 6は実施せず総括へ |
| 予算STOP | 非該当 | 累計¥103.67/¥300(ハードストップ¥290) |
| 品質STOP(同構造Advでwanna型内容逸脱がさらに2回以上) | 非該当 | Round 5でwanna型逸脱は0回(M05 Adv T2/T3、N03とも0)。N04 Advに『his』挿入のASR不一致が1回あるが別型(wanna型ではない)・別構造(measured版) |

### 8-2. 総括: Round 1〜5(計37 Prompt: J13/K8/L6/M6/N4 +H0基準、各Take1、一部Take2/3)
(推奨は書かない。USER_DECISION_REQUIRED用。委任文の『39+Prompt』は概数、実数は37 Prompt + H0基準)
- **効く軸**: 強い形容1回の減速語(slightly slower、measured、a little slower)がStdのraw換算を概ね167付近に揃える。『言い切って次へ直行』(M05、N01、N04)はStdで速度・文末・長無音を同時に圏内にしやすい(Std暫定合格はM05 T1/N01/N04)。
- **効かない軸**: 弱形減速語、像のみ、均一化指示、極短Prompt、話題転換の扱い指示(Round 4のM01-M06、Round 5のN01/N02。N02の切除比較でも差なし)、忠実読み指示(N03は速くなる方向、wanna抑制効果は判別不能)。
- **相反関係**: 減速するとStd文末平均が延び長無音が増える。文末を詰めると速度が速くなる。Std/Adv単一Promptで両立する組合せは見つかっていない。
- **Advが下がりにくい事実**: 減速語を入れてもAdv Take1は167+6を超える側に集中。Round 5でもN04 191.5、M05 176〜180、N03 174.7。167±6内はN01(167.1)・N02(170.9)のみで、いずれも文末平均が593ms基準をわずかに超過(627/600ms)。
- **原稿の話題転換2箇所の長無音**: Stdの≥800msは主に第5文末(delay.→The)・第9文末(continue.→The)に集中(Round 4 Step A: 73%)。Prompt指示では解消せず、原稿構造(話題が切り替わる文末)に起因する可能性が高い。
- **単一Prompt両立の到達度(最良候補の実測値)**: N01(Std 163.3/494ms/長無音0/ASR OK=合格、Adv 167.1/627ms/長無音1/ASR OK=文末のみ+34ms超過)。N02(Std 171.6/514ms/長無音1、Adv 170.9/600ms/長無音1、両レベル速度圏内で文末がStd+16/Adv+7ms超過)。いずれもn=1(再現未確認)。M05は3 takeで再現せず。

### 8-3. ユーザー判断用の選択肢(推奨なし、長所短所のみ)
- **(i) Std/Adv別Prompt**: 再現済みの組合せの実測 — Std=K06(2/2、154.5/156.0、478/486ms、長無音0/0)、Adv=K01(2/2、172.6/170.3、580/466ms、長無音1/1)(TRIAL-03 Round 3報告)。Round 4〜5の単発Std合格(M05 T1/N01/N04)は再現未確認。長所: 実測済み、各レベルで基準を満たす。短所: Prompt管理が2本、声質の連続性が変わりうる、n=2。**Production配線の事実確認(Grep)**: `er003_v1_n3_01_tts_generate.py`はA2(Std)英語segmentに`style_prefix_override=A2_ENGLISH_STYLE_PREFIX_SLOWER`を渡し、B1側はoverride無し(既定`p9a.ENGLISH_STYLE_PREFIX`)、Comment1-4/PreviewにはB1_PREVIEW_STYLE_PREFIX_CALMを渡す。つまり『レベル/セグメント別にstyle prefixを渡し分ける引数(style_prefix_override)』は既にある。ただしCoffee v5のTrial方式(speech_metadata.style単体)でレベル別Promptを許容する配線は本Trialで未確認(Production無変更)。
- **(ii) Advにも軽微な減速後処理(現行仕様外)**: 長所: 単一Prompt(例: N01/N02系でAdv 167〜171、M05系176〜180)で約6%減速すると計算上Adv約157〜166(N01/N02)、約166〜169(M05系)になる目安。短所: 現行はStd 6%減速のみで、仕様変更にユーザー承認が必要。Advの文末間・長無音も約6%延びる。Advは現行v5で既に166.9。実測していない(計算上の目安)。
- **(iii) H0 T1暫定維持**: 長所: 追加費用0、基準としてStd 157.3/498ms/長無音1、Adv 166.9/593ms/長無音0。短所: 本IDの『単一Promptでの改善』は得られない。H0はn=1。
- **(iv) 探索継続**: 残額¥196.33(累計¥103.67/¥300)。長所: N01/N02系が数値上最も近く、再現性追加(Take2/3)や微調整の余地。短所: 5 Round・37 Promptで単一Prompt両合格0、話題転換2箇所の長無音はPrompt指示で解消せず成功確率は不明、n=1の方向性。追加Roundはユーザー判断(自動実施しない)。

## 9. 費用・モデル
- 生成前見積: 12call×¥1.273=中央¥15.28(+20%上振れ¥18.33は、Step B上限¥16・ハードストップ¥18を上振れ側で超える。実績は中央付近。プロセスのBUDGET_STOP=18設定で実行)。`cost_r5.json`。
- 実績: 12 call、技術retry 0、TTS ¥12.68 + ASR推定 ¥2.71 = **¥15.40**。Step C/D未実施(¥0)。**累計 ¥88.27 + ¥15.40 = ¥103.67 / ¥300(残¥196.33)**。本委任上限¥25に対し¥15.40。
- モデル: 要求=応答=gemini-3.8-flash-lite-tts(Family-X TTS最新世代ライン、最新)、voice Aoede。ASR: faster-whisper small(local、¥0)、Primary ASR gpt-4o-mini-transcribe。
- 価格定数: 既存`er057_tone_trial_final_build_03.py`のPRICE_IN/PRICE_OUT×USD_JPY(Round 1〜4同一、新規出典確認は未実施=未確認)。

## 10. 注意事項・証跡
- 生成前にSTOP/STOP_ALL/round5/STOP不在確認(`docs/pm/delegation_log/*STOP_NOTICE*`のMelos通知は別ID)。有料runは1回(25.5秒)、再起動・監督ループなし。
- 採用判断・Production反映なし。Production state sha前後一致(`state_guard_r5.json` all_unchanged=true)。tts_input改変・無音カット・6%以外の速度変換・原稿編集なし。Melos関連・既存`user_test/`ページに触れていない。
- 聴感未確認: N04 Adv『his』挿入、M05 Adv T3/N04 Adv clickはASR/検出器判定のみ。
- 証跡: `round5/{prompts_r5,measurements_r5,classification_r5,cost_r5,state_guard_pre_r5,state_guard_r5}.json`、`generation_log_r5.jsonl`、`gen_summary_r5_B.json`、`_tables_r5.md`、`attempts/*.wav`(git管理外)、コード`er057_coffee_tts_style_h_speed_04_{design5,gen5,guard5,measure5,report5}.py`。
