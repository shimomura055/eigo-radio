# ROUND2_REPORT_01: FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-03 Round 2 (2026-10-13, 委任_02)

到達上限 VALIDATED(Trial)。Production変更なし。採用判断なし。結論: **Std/Adv両方を満たす単一Promptは0件(16 call中 暫定合格2件: K01 Adv / K06 Std)。Step C(再現性)・Step D(試聴ページ)は条件未達のため実施せず。**
モデル: gemini-3.8-flash-lite-tts(要求=応答model_version、最新世代のFamily-X TTSライン)、voice Aoede、speech_metadata方式、ASRはRound 1と同一(faster-whisper small local、Primary ASR既存)。測定は前回と同一条件(RMS<-40dBFS/50ms、WPM=原稿語数/尺、Stdは6%減速後を実測)。評価軸(Fable記録): 減速前換算(raw)WPM≒167を単一Promptで狙う(raw換算=Std実測÷0.94、Std減速後≒157/Adv≒167)。3列併記: 「Std減速後実測」「raw換算」「Adv実測」。n=1(Take1)の差は方向の目安。

## 1. 候補一覧(K01〜K08、全て一から記述・数値WPMなし・unhurried/slowly不使用)
- **K01** (37語, sha af176263, maxJaccard(J)=J05:0.298, H0=0.185): `A gentle storyteller sharing a true story with a few friends, warm and bright, with a smile in the voice. Go slightly slower than usual, and let every sentence flow straight on into the one after it.`
  - 軸: speed=slightly slower(控えめ減速、1回のみ) / pause=肯定形の接続(flow straight on) / voice=落ち着いたストーリーテリング / strength=中 / structure=速度+ポーズ肯定形
  - 意図: J10(raw速度が両レベルで揃った)の減速語を残し、J10で負けた『short silence』の否定的抑制をJ02型の肯定形接続に置換して、文末間増を防げるか。
  - 根拠(Round1知見): J10(slow系)とJ02(Do not pause系)の知見: 減速でStd文末+100〜200ms、肯定形ポーズ抑制はStdで有効
  - 想定副作用: 減速に接続指示が負けて文末が再び伸びる/長無音が出る
- **K02** (28語, sha a7b881e0, maxJaccard(J)=J13:0.361, H0=0.16): `A bright, friendly presenter reading at a pace a little slower than a news bulletin, with lively intonation. Between sentences leave only the tiniest gap, and keep going.`
  - 軸: speed=相対速度(a little slower than a news bulletin、J13の中間化) / pause=極小の間(tiniest gap / keep going) / voice=ラジオ/プレゼンター+抑揚 / strength=中(J13の強めを緩和) / structure=速度+ポーズ併記
  - 意図: J13はStd157.8/Adv177.6でAdvが+10.6速い。相対速度の強さをnoticeablyからa littleに弱め、Advを下げつつStdが過減速しないかを見る(強さ依存の確認)。
  - 根拠(Round1知見): J13(Std良好・Adv速すぎ)
  - 想定副作用: 弱めすぎてStd/Adv両方とも速くなる可能性
- **K03** (26語, sha c172f317, maxJaccard(J)=J02:0.444, H0=0.267): `A steady, gentle voice, warm and clear, with a smile in it. Do not pause between sentences; keep the story moving from one to the next.`
  - 軸: speed=steady, gentle(slowを使わない弱形、数値なし) / pause=停止禁止(Do not pause、肯定の継続指示つき) / voice=自然な語りかけ / strength=中(J02のslowを緩和) / structure=速度語+ポーズ併記
  - 意図: J02(slow, steady+Do not pause)はStd 156.1/Adv 186.8でStdのみ効いた。slowを外しても減速が残るか、Advの過速が緩和するかを切り分ける。
  - 根拠(Round1知見): J02(Stdのみ有効、数値130は不信頼)
  - 想定副作用: slowを外すと減速効果自体が消えて両レベルが速くなる
- **K04** (28語, sha 6e294dd6, maxJaccard(J)=J07:0.265, H0=0.208): `A calm, upbeat radio host with a warm, clear voice, speaking a touch slower than a news reader. Keep your breaths brief between thoughts, and never hold one.`
  - 軸: speed=a touch slower than a news reader(弱い相対減速) / pause=短い息継ぎ(brief breaths / never hold) / voice=ラジオニュース調寄り(host) / strength=控えめ / structure=速度+ポーズ併記
  - 意図: J07(calm+短い息継ぎ)はAdv 169.4で良好だがStd 168.3で速かった。弱い相対減速を一言だけ入れて、Advを保ちStdを下げられるか。
  - 根拠(Round1知見): J07(Advのみ合格、Stdが速い)
  - 想定副作用: Advまで遅くなる、またはStdが変わらない
- **K05** (28語, sha f84c44f8, maxJaccard(J)=J05:0.4, H0=0.204): `A friendly storyteller, warm and relaxed, with a smile in the voice. Tell it as one continuous story, so each sentence glides into the next without any stop.`
  - 軸: speed=relaxed(像として含意、速度指示なし) / pause=肯定形の連続(one continuous story / glides) / voice=落ち着いたストーリーテリング / strength=中 / structure=ポーズ中心
  - 意図: J05(ニュース調像+Never long silence)は速度指示なしで速くなった。像をstorytellerに替え、肯定形の連続指示だけにして速度ずれと文末間が像で変わるか確認。
  - 根拠(Round1知見): J05(ポーズ指示のみで速度↑)、J06
  - 想定副作用: ポーズ短縮で全体が速くなる(Adv超過)
- **K06** (22語, sha f1c2786b, maxJaccard(J)=J03:0.441, H0=0.149): `A warm storyteller with a measured voice, clear and smiling. Pause only briefly at the end of each sentence, then go on.`
  - 軸: speed=measured単独(deliberateを除く) / pause=文末のみ短く(only briefly, then go on) / voice=落ち着いたストーリーテリング / strength=中 / structure=速度+ポーズ併記
  - 意図: J03(measured, deliberate)はStd 152.9/Adv 173.3と減速に有効だが文末間・1030ms長無音が増えた。deliberateを除いたmeasured単独で間延びが切り分けられるか。
  - 根拠(Round1知見): J03(減速有効、間延び副作用)
  - 想定副作用: measured単独では減速が弱くStd/Adv速い、または間延びが残る
- **K07** (24語, sha 146abfac, maxJaccard(J)=J07:0.323, H0=0.191): `A warm, trustworthy radio news presenter at a calm broadcast pace, clear and bright. Never stop between sentences; move straight on to the next.`
  - 軸: speed=calm broadcast pace / pause=停止禁止(Never stop / move straight on) / voice=ラジオニュース調固定 / strength=中 / structure=速度+ポーズ併記
  - 意図: J08(calm broadcast pace+short and connected)はStd 161.8/文末523ms、惜しかった。像はニュース調のまま、間抑制を強い禁止形にして文末を詰められるか。
  - 根拠(Round1知見): J08(Std惜しい、Adv 182速い)
  - 想定副作用: ニュース調でAdvが速いまま(+15)になる
- **K08** (18語, sha 53b6a34b, maxJaccard(J)=J11:0.444, H0=0.167): `A warm, friendly storyteller with a bright, clear voice and a smile. Steady pace, brief pauses, expressive intonation.`
  - 軸: speed=steady pace(弱形) / pause=brief pauses / voice=自然な語りかけ+声質像(storyteller) / strength=控えめ / structure=簡潔統合(約20語、声質像つき)
  - 意図: J11(10語)は声質像不足で品質事故。声質像(bright, clear, expressive intonation)を残した約20語の短形で、最小指示の効果を見直す。
  - 根拠(Round1知見): J11(極短で品質劣化、AdvでASR挿入)
  - 想定副作用: 短い指示が弱く両レベル速い、または抑揚指示が速度を上げる

## 2. 自己点検(`prompts_r2.json` self_check)
- 重複: K01-K08のsha全相異、J01-J13・H0ともsha相異(assert通過)。K内最大Jaccard: K01-K05=0.326、K03-K05=0.316、K01-K03=0.279。
- J系/H0との関係: J系を部分文字列に含む/含まれる候補なし(assert)。J系との最大Jaccard: K01:J05=0.298、K02:J13=0.361、K03:J02=0.444、K04:J07=0.265、K05:J05=0.400、K06:J03=0.441、K07:J07=0.323、K08:J11=0.444(Prompt同一でなく、語彙の部分共有=同じ概念を別表現で書いた結果)。H0とのJaccardは0.149〜0.267。
- 矛盾なし。減速+間短縮の併記(K01/K02/K04/K06/K07)はRound1で有効だった構造「強い形容1回の減速+肯定形/禁止形の間抑制」の再検証として意図的。
- 冗長なし(速度/間/声質を各1回)。全て2文(18〜37語)。tts_inputはstd/advとも前回v5/8wayとsha一致(assert通過: std 13740eca9a44 / adv 627f1c7f7771)。

## 3. 測定全表(Take1、基準=H0 Take1・現行v5を先頭)
判定基準(Round1同一、事前固定): 速度=Std 157±6 / Adv 167±6、ポーズ=文末平均がH0 T1以下(主判定はRound1同一でStd≤498 / Adv≤593ms)かつ800ms超長無音0〜1件、品質=Primary ASR verified・末尾一致・long_gap(medium+)なし。raw換算167±6は参考列(Std rawは実測÷0.94)。**注意: 委任文はAdv文末を510ms相当と記載したが、Round1の実適用値はH0 T1実測の593msであり本報告の主判定は593。510ms厳格適用の参考判定は`classification_r2.json`のpause_ok_adv510に記録(下記5節参照)。**

| 候補 | take | Lv | WPM実測(目標差) | raw換算(167差) | 発話WPM | 文末無音 平均/中央/最大ms | 文中無音 本/計s/300ms+ | 800ms+ | Primary ASR | 末尾 | 異音med+ | ピッチ幅st/強弱幅dB | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 Take1(TRIAL-02再利用) | - | std | 157.3 | 167.3 | 175.3 | 498/525/890 | 37/3.69/2 | 1 | NORMALIZED_MATCH | - | 0 | 9.79/17.3 | 基準 |
| H0 Take1(TRIAL-02再利用) | - | adv | 166.9 | 166.9 | 179.3 | 593/570/750 | 49/5.92/5 | 0 | NORMALIZED_MATCH | - | 0 | 10.34/16.6 | 基準 |
| 現行v5 | - | std | 145.5 | 154.8 | 172.7 | 694/630/1050 | 38/3.83/1 | 4 | - | - | 1 | 9.54/17.4 | 基準 |
| 現行v5 | - | adv | 166.9 | 166.9 | 172.3 | 456/460/740 | 49/6.21/6 | 0 | - | - | 0 | 10.13/18.0 | 基準 |
| K01 | 1 | adv | 172.6 (+5.6) | 172.6 (+5.6) | 188.6 | 580/560/800 | 44/5.25/4 | 1 | NORMALIZED_MATCH | OK | 0 | 10.11/17.9 | 暫定合格 |
| K01 | 1 | std | 157.7 (+0.7) | 167.8 (+0.8) | 174.7 | 522/480/910 | 44/3.65/1 | 3 | NORMALIZED_MATCH | OK | 1 | 9.08/17.1 | 速度のみOK(ポーズ不良) |
| K02 | 1 | adv | 186.5 (+19.5) | 186.5 (+19.5) | 196.5 | 427/510/590 | 38/4.12/3 | 0 | NORMALIZED_MATCH | OK | 0 | 9.68/16.8 | ポーズのみOK(速度外) |
| K02 | 1 | std | 166.7 (+9.7) | 177.3 (+10.3) | 187.0 | 542/540/830 | 35/2.92/1 | 1 | NORMALIZED_MATCH | OK | 0 | 11.42/15.7 | 不合格 |
| K03 | 1 | adv | 174.5 (+7.5) | 174.5 (+7.5) | 183.8 | 473/450/650 | 45/5.13/3 | 0 | NORMALIZED_MATCH | OK | 0 | 10.49/16.9 | ポーズのみOK(速度外) |
| K03 | 1 | std | 152.2 (-4.8) | 161.9 (-5.1) | 179.8 | 648/635/900 | 30/3.73/3 | 3 | ASR_VALIDATION_UNCERTA | OK | 0 | 9.51/16.5 | 不合格(ASR/異音) |
| K04 | 1 | adv | 173.3 (+6.3) | 173.3 (+6.3) | 181.0 | 553/470/1110 | 54/5.29/3 | 2 | NORMALIZED_MATCH | OK | 0 | 10.28/16.8 | 不合格 |
| K04 | 1 | std | 172.9 (+15.9) | 183.9 (+16.9) | 181.4 | 475/475/710 | 31/2.55/0 | 0 | NORMALIZED_MATCH | OK | 0 | 10.44/16.7 | ポーズのみOK(速度外) |
| K05 | 1 | adv | 181.8 (+14.8) | 181.8 (+14.8) | 192.6 | 444/480/670 | 38/4.75/4 | 0 | NORMALIZED_MATCH | OK | 0 | 10.83/18.1 | ポーズのみOK(速度外) |
| K05 | 1 | std | 168.7 (+11.7) | 179.5 (+12.5) | 186.4 | 482/525/630 | 30/2.43/0 | 0 | TRUE_CONTENT_MISMATCH | OK | 0 | 10.66/17.1 | 不合格(ASR/異音) |
| K06 | 1 | adv | 172.2 (+5.2) | 172.2 (+5.2) | 191.4 | 636/570/1040 | 44/5.42/5 | 1 | NORMALIZED_MATCH | OK | 0 | 10.38/18.2 | 速度のみOK(ポーズ不良) |
| K06 | 1 | std | 154.5 (-2.5) | 164.4 (-2.6) | 171.3 | 478/530/740 | 37/4.31/3 | 0 | NORMALIZED_MATCH | OK | 0 | 9.88/18.2 | 暫定合格 |
| K07 | 1 | adv | 184.5 (+17.5) | 184.5 (+17.5) | 192.4 | 463/420/600 | 32/3.66/2 | 0 | NORMALIZED_MATCH | OK | 0 | 9.54/16.9 | ポーズのみOK(速度外) |
| K07 | 1 | std | 170.2 (+13.2) | 181.1 (+14.1) | 189.1 | 503/530/700 | 32/2.88/2 | 0 | NORMALIZED_MATCH | OK | 0 | 9.99/16.0 | 不合格 |
| K08 | 1 | adv | 179.7 (+12.7) | 179.7 (+12.7) | 186.8 | 521/480/990 | 56/4.99/1 | 1 | NORMALIZED_MATCH | OK | 0 | 9.43/18.2 | ポーズのみOK(速度外) |
| K08 | 1 | std | 164.1 (+7.1) | 174.6 (+7.6) | 174.3 | 486/440/660 | 35/3.55/2 | 0 | NORMALIZED_MATCH | OK | 0 | 10.2/16.1 | ポーズのみOK(速度外) |

(`_tables_r2.md`のMEASURE節と同一。異音med+はclick/level_step等のmedium以上の件数。K01 Stdはclick medium 1件(18.5s、聴感確認要)。)

## 4. 軸別の効き方(n=1の方向の目安)
- **強い減速語は効くが弱い減速語は効かない(Round1と整合)**: slightly slower(K01)はraw 167.8(Std)/172.6(Adv)で両レベルが目標付近に揃い、raw差-4.8と全候補で最良級(Round1 J10は163.8/165.9)。measured(K06)もraw 164.4/172.2。一方、a little slower than a news bulletin(K02: raw177.3/186.5)、a touch slower(K04: 183.9/173.3)、steady pace(K08: 174.6/179.7)、calm broadcast pace(K07: 181.1/184.5)、relaxed(K05: 179.5/181.8)はほぼ効かない。**弱形化(noticeably→a little、slow→steady)は減速効果を失う**。
- **Advは下がりにくい**: 8候補のAdv実測は172.2〜186.5(167±6内はK01 172.6・K06 172.2のみ。K04 173.3/K03 174.5は+6.3/+7.5で外れ)。167そのものに届いたPromptはなし。Round1全体でもAdv 167±6はJ07/J10/J11のみ。
- **deliberateの間延び切り分け(K06 vs J03)**: measured単独(deliberate除去)でStd長無音0本・文末478ms(J03 Std: 608ms/長無音1030ms)。deliberateが間延び要因という仮説は支持(n=1)。ただしAdvではK06が文末636ms・1040msの長無音1本(J03 Adv: 446ms)で逆に増えた。Std/Advで挙動が一貫しない。
- **肯定形接続の効果(K01 vs J10)**: 文末平均はStd 663→522ms、Adv 694→580msと改善、ただしStdの長無音は1→3本(910/810/850ms、いずれも文末後)でポーズ不良判定。減速と間抑制の相反は「軽減」まで。
- **停止禁止形(K03 Do not pause、K07 Never stop)**: K07はStd 503/Adv 463msと文末は詰まったが速度が速い(raw181/184)。K03(steady, gentle+Do not pause)は減速が残る(Std raw161.9)ものの文末648ms・長無音3本・ASR判定uncertain(原文「US」が「u s」表記、固有名詞綴り差)で不良。Round1 J02(slow, steady+Do not pause)の「slow」を弱めると文末間が悪化した。
- **簡潔統合(K08、約18語)**: J11の品質事故(Adv ASR挿入)は再現せず(両レベルASR OK、異音med+0)。ただし速度は速い(raw174.6/179.7)。声質像を入れれば短形は成立するが減速力は弱い。
- **storyteller像×連続指示(K05)**: Std ASR置換(had→have)、速度速い(raw179.5/181.8)。J05同様、ポーズ指示のみでは速くなる。
- **声質(参考、機械指標)**: ピッチ幅(p10-p90半音)9.08〜11.42(H0 T1 Std 9.79/Adv 10.34)、強弱幅15.7〜18.2dB(H0 T1 17.3/16.6)で全候補H0同等圏、明確な平板化なし。最低はK01 Std 9.08。最終判断は人間の試聴。
- **共通**: 段落境界(原文「...continue. The ...」約33秒付近)に800ms超の無音が多くの候補で出る(K01/K03/K04/K06の各1本)。H0にも同種の長無音があり、Prompt起因ではなく原稿構造起因の可能性(未検証)。

## 5. 判定(16 call)
- **両レベル合格(単一Prompt): 0件**
- 暫定合格(速度+ポーズ+品質を同一レベルで満たす) 2件: **K01 Adv**(172.6、文末580ms、長無音1本、ASR OK)、**K06 Std**(154.5、文末478ms、長無音0、ASR OK)。いずれも片側のみ。
- 速度のみOK(ポーズ不良) 2件: K01 Std(157.7/raw167.8、文末522ms、長無音3本)、K06 Adv(172.2、文末636ms、長無音1040ms)。
- ポーズのみOK(速度外) 7件: K02 Adv、K03 Adv、K04 Std、K05 Adv、K07 Adv、K08 Std、K08 Adv(いずれも速すぎ)。
- 不合格(ASR/異音) 2件: K03 Std(ASR uncertain: US→u s、長無音3本)、K05 Std(had→have置換)。
- 不合格(速度・ポーズとも外れ) 3件: K02 Std、K04 Adv(文末553/長無音2本1110ms)、K07 Std。
- **近接例**: K01は同一Promptでraw換算が両レベル167.8/172.6(raw差4.8)と最も揃い、Adv側は速度・ポーズとも合格だが、Std側の文末間が522ms(+24ms)かつ800ms超が3本でポーズ不良。K06はStd合格だがAdv文末636ms。**510ms厳格適用(委任文の字義)ではK01 Adv(580ms)は不合格になり、暫定合格はK06 Stdのみ**になる点を開示する。
- 「Std/Adv両方満たす単一Prompt」の観点で、Round1(J02/J13/J07はいずれも片側のみ)に続き今回も未達。未達の構造的原因: Advは弱い指示では下がらず(172〜186)、強い減速語(slightly slower/measured)は効くがStdの文末間・長無音が増える。

## 6. 再現性(Step C)
**未実施**(両レベル合格の単一Promptが0件のため、委任文の条件により実施しない)。

## 7. 次の案(Step Cを実施しないため、Round 3設計案。実施はFable確認後の委任_03、要新規Prompt群・継ぎ足し禁止)
狙い: 強い減速語(slightly slower / measured)でraw 167付近を保ちつつ、Stdの文末間・長無音(特に文末後800ms超)を抑える。新規記述6候補(L01〜L06):
1. L01: 「slightly slower」+文末の語尾を柔らかく終えて即次へ(語尾処理の指示、K01の『flow straight on』を別表現で)。
2. L02: 「slightly slower」+『文と文の間で止まらず、次を直ちに始める』禁止+肯定の併記(1文に集約)。
3. L03: 「measured voice」+『文を次へ運ぶ』(K06の『Pause only briefly』を肯定形の連続に置換)。
4. L04: 「a measured, even rhythm」(リズム均一化語)+短い息継ぎ。減速と間の均一化を同一語で狙う。
5. L05: 「slightly slower」を主語の像側へ(『a storyteller who takes it a bit slower than most』)で指示でなく像として入れる(指示文の相反を避ける)。
6. L06: 『conversational but unhurried』は使えない(unhurried禁止方針)ため、『easy and even, never rushed, never dragging』(両側否定でペース中庸を指す)。
見積: 6候補×Take1×Std/Adv=12call×約¥1.25=約¥15.1(上振れ+20%で¥18.1)、本ID累計¥52.50→約¥67.6(上振れ¥70.6)/枠¥100。代替(または併用): K01・K06のTake2をStd/Adv各1回(4call≒¥5.0)で近接例が偶然かを確認。追加予算は本ID枠内の残¥47.5で収まるが、委任文上の本委任有料上限(Step B ¥24+Step C ¥10)は消化していないため、Round 3はFableの新規委任が必要。

## 8. 費用・モデル
Step B実績: 16 call、技術retry 0、TTS ¥16.49 + ASR推定 ¥3.58 = **¥20.07**(1call≒¥1.254、見積¥19.78〜23.73内、上限¥24・ハードストップ¥26未満)。Step C ¥0(未実施)。本ID累計 ¥32.43 + ¥20.07 = **¥52.50 / ¥100**(残¥47.5)。要求モデル=応答model_version=gemini-3.8-flash-lite-tts(最新世代)、voice Aoede。ASRはfaster-whisper small(local、¥0相当、既存Primary ASR費用推定はRound1と同一手法)。TTS単価は既存`er057_tone_trial_final_build_03`の価格定数を使用(新規の出典確認は行っていない=出典はRound1同様の既存定数)。見積と実績は`cost_r2.json`。

## 9. 注意事項・証跡
- STOP/STOP_ALL/`round2/STOP`は不在を生成前に確認。`docs/pm/delegation_log/`に`2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_STOP_NOTICE.md`が存在するが対象は別ID(Melos)でありFamily-X Coffeeとは無関係(Round1と同じ扱い。Fableの指示でMelos関連には触れていない)。有料runは1回のみ(監督ループ・再起動なし、26秒)。
- 採用判断・Production反映は行っていない。結果は事実のまま(両レベル合格0件)。n=1の差は方向の目安。
- 異音: K01 Std click medium 1件(18.5s)は聴感確認未実施。K03 StdのASR uncertainは原稿「US」の綴り差(固有名詞扱い)で内容誤りではない可能性が高いが、判定は規則通り不合格。
- 試聴ページは条件未達のため作成なし。
- 証跡: `round2/{prompts_r2,measurements_r2,classification_r2,cost_r2,state_guard_pre_r2,state_guard_r2}.json`、`generation_log_r2.jsonl`、`gen_summary_r2_B.json`、`_tables_r2.md`、`attempts/*.wav`(中間wavはgit管理外)、コード`er057_coffee_tts_style_h_speed_03_{design2,gen2,guard2,measure2,report2}.py`。Production state sha前後一致(`state_guard_r2.json` all_unchanged=true)。
