# ROUND1_REPORT_01: FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-03 Round 1 (2026-10-13)

到達上限 VALIDATED(Trial)。Production変更なし。採用判断なし。モデル: gemini-3.8-flash-lite-tts(要求=応答model_version、最新世代のFamily-X TTSライン)、voice Aoede、speech_metadata方式、ASRはPrimary(既存)。測定は前回TRIAL-02と同一条件(faster-whisper small、RMS<-40dBFS/50ms、WPM=原稿語数/尺)。

## 1. 設計と自己点検
13候補(J01-J13)を一から記述(各2文、10〜38語、H0を含む/H0に含まれる候補なし=assert済)。探索軸: 速度指示(数値WPM / 速度語measured・deliberate / テンポ語 / 相対速度 / 控えめ減速 / 指示なし)、ポーズ指示(停止禁止 / 接続・glide / 息継ぎ短く / 数値上限 / 指示なし)、声のスタイル(ニュース調 / 友人への語りかけ / 落ち着いたストーリーテリング)、強さ、構造、簡潔さ(極短10語まで)。H0 Take1は前回音声を再利用(再生成なし)。

自己点検(`prompts_r1.json` self_check): 全13件sha相異。最大Jaccard類似は0.349(J02-J05)で候補間の重複は小。速度/間/声質の指示は各1回ずつで冗長・重複なし。矛盾なし(J02のslow+no pause、J10/J13の減速+間短縮は相反効果を検証するための意図的併記)。`slowly/unhurried`は含まない。tts_inputはstd/adv両方とも前回v5/8wayとsha一致(assert通過: std 13740eca9a44 / adv 627f1c7f7771)。

## 2. 候補一覧(Prompt全文・語数・軸・意図)
- **J01** (31語, sha a260edef): `A warm, friendly radio presenter telling a human-interest story at about 150 words per minute. Sound clear and smiling, and carry each sentence straight into the next without a long stop.`
  - 軸: speed=数値WPM(150) / pause=文末停止抑制(carry ... without a long stop) / voice=自然な語りかけ / strength=明確 / structure=速度中心 / brevity=必要条件明示の短文
  - 意図: 数値WPMがTTSの速度に効くかを検証。Adv現状175-187なので150指定でどこまで下がるか。
  - 想定副作用: 数値を無視して速いまま/数値に引かれて間が増える恐れ
- **J02** (30語, sha a695d10d): `Speak at a slow, steady 130 words per minute, warm and clear, with a smile in your voice. Do not pause after sentences; let each one roll into the next.`
  - 軸: speed=数値WPM(130, slow steadyで強め) / pause=文末停止禁止(Do not pause) / voice=自然な語りかけ / strength=強め / structure=速度+ポーズ併記 / brevity=必要条件明示の短文
  - 意図: J01より強い数値指定+強い停止抑制。数値の強さ依存(150 vs 130)と相反効果(速度↓でポーズ↑)の検出。
  - 想定副作用: 過減速、語尾の引き延ばし、no pauseによる不自然な詰め込み
- **J03** (32語, sha 322aed42): `A warm storyteller reading a human-interest story in a measured, deliberate pace, clear and smiling. Let each sentence lead naturally into the next, pausing only briefly at the end of a sentence.`
  - 軸: speed=速度語(measured, deliberate) / pause=文末は短く(only briefly) / voice=落ち着いたストーリーテリング / strength=明確 / structure=速度中心 / brevity=必要条件明示の短文
  - 意図: measured/deliberateという速度語の強さ検証。slowlyを避けつつ減速できるか。
  - 想定副作用: deliberateが文末間・文中間を増やす恐れ(相反)
- **J04** (24語, sha 2d31d542): `A friendly radio host chatting with one listener in a relaxed, easy tempo. Keep the voice bright and clear, with a smile in it.`
  - 軸: speed=テンポ語(relaxed, easy) / pause=指示なし / voice=自然な語りかけ / strength=控えめ / structure=速度中心 / brevity=最小限
  - 意図: ポーズ指示なしでテンポ語のみ。会話調だけでペースが落ちるか(TRIAL-02 H2はcalm conversationalでも速かった)。
  - 想定副作用: 速度ほぼ不変の可能性、間の挙動はモデル任せ
- **J05** (38語, sha 42d3a959): `A warm radio presenter, clear and approachable, with a smile in the voice. Never leave a long silence after a sentence: let the end of each sentence glide into the start of the next, as one continuous story.`
  - 軸: speed=指示なし / pause=文末停止抑制を強く(Never ... long silence / glide) / voice=ラジオニュース調寄り(presenter) / strength=強め / structure=ポーズ中心 / brevity=必要条件明示の短文
  - 意図: ポーズ指示のみの純粋効果(速度指示なし)。文末無音がどこまで短くなり、速度が上がるか(相反効果の観察)。
  - 想定副作用: ポーズ短縮で全体が速くなる(目標超過)可能性が高い
- **J06** (27語, sha 2d4cf138): `A friendly storyteller. Link words into long, smooth phrases and keep the voice moving through each clause, taking short natural breaths only at commas and sentence ends.`
  - 軸: speed=指示なし / pause=フレーズ接続強調+息継ぎ位置限定 / voice=自然な語りかけ / strength=明確 / structure=ポーズ中心 / brevity=必要条件明示の短文
  - 意図: 文中のつながり(フレーズ接続)を強調した時の文中無音・速度への影響。
  - 想定副作用: 長いphraseで早口化、息継ぎ位置限定で抑揚が平板になる恐れ
- **J07** (20語, sha db2980e8): `A warm, calm radio presenter, bright and clear. Take short, natural breaths between ideas, and never let a breath linger.`
  - 軸: speed=指示なし(calmのみ) / pause=自然な息継ぎ優先(短く) / voice=ラジオニュース調寄り / strength=控えめ / structure=ポーズ中心 / brevity=最小限
  - 意図: TRIAL-02 H0の『breathe naturally』を一から短く言い換え、息継ぎ指示の最小効果を観察。
  - 想定副作用: 速度は元のHに近い=速め傾向の再現の可能性
- **J08** (31語, sha f752c1cf): `A crisp radio news announcer reading a human-interest story at a calm broadcast pace, clear, credible and warm, with an upbeat smile in the voice. Keep sentence endings short and connected.`
  - 軸: speed=テンポ語(calm broadcast pace) / pause=文末は短く接続 / voice=ラジオニュース調 / strength=明確 / structure=簡潔統合 / brevity=必要条件明示の短文
  - 意図: ニュース調でcalm指定+crispの変化を見る(TRIAL-02 H1のnews-broadcast paceとの対比)。
  - 想定副作用: crispが速度を上げる恐れ、硬さで温かみ低下
- **J09** (35語, sha e398e9d2): `A natural, easygoing narrator speaking to a friend, warm and animated, with lively intonation and a smile in the voice. Talk at a relaxed pace, as if you were just telling someone what you read.`
  - 軸: speed=relaxed pace(語りかけの含意) / pause=指示なし / voice=自然な語りかけ(友人への語り) / strength=控えめ / structure=簡潔統合 / brevity=必要条件明示の短文
  - 意図: 最も口語的な像+抑揚(lively intonation)重視。声質(抑揚)への効果と速度の関係を見る。
  - 想定副作用: animatedが速度を上げる恐れ、口語で語尾が崩れる恐れ
- **J10** (35語, sha dc69610a): `A calm storyteller telling a true story to a small audience, warm and gentle, with expressive intonation. Slow the pace slightly, but keep the silence between sentences short and each ending connected to what follows.`
  - 軸: speed=slightly slower(控えめな減速) / pause=文末停止抑制(short silence / connected) / voice=落ち着いたストーリーテリング / strength=明確 / structure=速度+ポーズ併記(統合) / brevity=必要条件明示の短文
  - 意図: 減速と文末間短縮を同時に明示し、相反効果を打ち消せるかの本命候補の一つ。
  - 想定副作用: slowが文中間・語尾を延ばす、またはbut節で片方が無視される
- **J11** (10語, sha 3555c3fb): `Warm and clear, with a smile. Calm pace, short pauses.`
  - 軸: speed=calm pace / pause=short pauses / voice=指定最小 / strength=控えめ / structure=簡潔統合 / brevity=最小限(極短)
  - 意図: 最小限の指示で何が効くか。声質像を省いた時の声質劣化も確認。
  - 想定副作用: 声質像が薄くなる。極短Prompt(下限探索、2文)
- **J12** (29語, sha 4d6a0737): `Speak warmly and clearly, with a smile in the voice. Keep a pace of about 150 words per minute, and keep every pause between sentences under half a second.`
  - 軸: speed=数値WPM(150) / pause=数値の停止上限(0.5s未満) / voice=自然な語りかけ / strength=明確 / structure=簡潔統合 / brevity=必要条件明示の短文
  - 意図: 数値条件(速度+間の上限)の明示が効くかを検証。J01との差で『数値の間指定』の効果を分離。
  - 想定副作用: 数値の間指定は無視される可能性、短すぎる間で不自然
- **J13** (26語, sha ec4ecd8e): `Read noticeably slower than a news bulletin, warm and bright, with expressive intonation. Between sentences keep the silence very short and let the voice carry on.`
  - 軸: speed=相対速度(noticeably slower than a news bulletin) / pause=文末の間を非常に短く(very short / carry on) / voice=ラジオニュース調との対比 / strength=強め / structure=簡潔統合 / brevity=必要条件明示の短文
  - 意図: 相対基準で強めに減速+強く間を詰める。強め指示の限界と副作用を見る。
  - 想定副作用: 過減速で不自然、または間の抑制が負けて長沈黙


## 3. 測定表(Take1、Std/Adv、基準=H0 Take1・現行v5を先頭)

| 候補 | Lv | WPM(目標差) | 発話WPM | 文末無音 平均/中央/最大ms | 文中無音 本/計s/300ms+ | 800ms+ | Primary ASR | 末尾 | 異音med+ | ピッチ幅st/強弱幅dB | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 Take1(TRIAL-02再利用) | std | 157.3 | 175.3 | 498/525/890 | 37/3.69/2 | 1 | NORMALIZED_MATCH | - | 0 | 9.79/17.3 | 基準 |
| H0 Take1(TRIAL-02再利用) | adv | 166.9 | 179.3 | 593/570/750 | 49/5.92/5 | 0 | NORMALIZED_MATCH | - | 0 | 10.34/16.6 | 基準 |
| 現行v5 | std | 145.5 | 172.7 | 694/630/1050 | 38/3.83/1 | 4 | - | - | 1 | 9.54/17.4 | 基準 |
| 現行v5 | adv | 166.9 | 172.3 | 456/460/740 | 49/6.21/6 | 0 | - | - | 0 | 10.13/18.0 | 基準 |
| J01 | adv | 191.3 (+24.3) | 193.8 | 296/270/520 | 42/4.09/2 | 0 | NORMALIZED_MATCH | OK | 0 | 10.13/19.3 | ポーズのみOK(速度外) |
| J01 | std | 176.8 (+19.8) | 181.7 | 419/415/560 | 33/2.61/0 | 0 | NORMALIZED_MATCH | OK | 0 | 9.84/16.7 | ポーズのみOK(速度外) |
| J02 | adv | 186.8 (+19.8) | 206.8 | 544/560/630 | 37/4.48/4 | 0 | NORMALIZED_MATCH | OK | 0 | 11.19/16.9 | ポーズのみOK(速度外) |
| J02 | std | 156.1 (-0.9) | 165.5 | 471/455/790 | 41/4.08/0 | 0 | NORMALIZED_MATCH | OK | 0 | 10.6/18.4 | 暫定合格 |
| J03 | adv | 173.3 (+6.3) | 185.3 | 446/480/640 | 45/6.23/7 | 0 | NORMALIZED_MATCH | OK | 0 | 10.93/16.2 | ポーズのみOK(速度外) |
| J03 | std | 152.9 (-4.1) | 177.9 | 608/560/1030 | 35/3.38/1 | 1 | NORMALIZED_MATCH | OK | 1 | 8.95/16.6 | 不合格(ASR/異音) |
| J04 | adv | 184.0 (+17.0) | 191.4 | 410/460/550 | 43/5.36/7 | 0 | NORMALIZED_MATCH | OK | 0 | 10.24/15.6 | ポーズのみOK(速度外) |
| J04 | std | 164.2 (+7.2) | 169.0 | 358/365/700 | 39/3.38/0 | 0 | TRANSCRIPT_STYLE_NORMA | OK | 0 | 9.79/18.0 | ポーズのみOK(速度外) |
| J05 | adv | 179.9 (+12.9) | 187.3 | 486/470/620 | 43/5.38/5 | 0 | NORMALIZED_MATCH | OK | 1 | 11.29/17.2 | ポーズのみOK(速度外) |
| J05 | std | 161.7 (+4.7) | 168.1 | 438/415/850 | 30/2.95/1 | 1 | TRUE_CONTENT_MISMATCH | OK | 1 | 11.3/16.7 | 不合格(ASR/異音) |
| J06 | adv | 188.0 (+21.0) | 196.8 | 504/480/680 | 46/4.58/2 | 0 | NORMALIZED_MATCH | OK | 0 | 10.44/17.2 | ポーズのみOK(速度外) |
| J06 | std | 167.5 (+10.5) | 182.6 | 499/505/710 | 34/3.0/2 | 0 | NORMALIZED_MATCH | OK | 0 | 9.74/16.6 | 不合格 |
| J07 | adv | 169.4 (+2.4) | 183.3 | 510/550/720 | 38/4.67/3 | 0 | NORMALIZED_MATCH | OK | 0 | 8.99/16.4 | 暫定合格 |
| J07 | std | 168.3 (+11.3) | 183.4 | 490/505/670 | 33/3.15/2 | 0 | TRUE_CONTENT_MISMATCH | OK | 0 | 10.36/16.6 | 不合格(ASR/異音) |
| J08 | adv | 182.3 (+15.3) | 189.5 | 499/500/570 | 39/4.92/6 | 0 | NORMALIZED_MATCH | OK | 0 | 10.16/17.7 | ポーズのみOK(速度外) |
| J08 | std | 161.8 (+4.8) | 177.4 | 523/505/730 | 28/2.71/2 | 0 | NORMALIZED_MATCH | OK | 0 | 10.98/16.6 | 速度のみOK(ポーズ不良) |
| J09 | adv | 188.2 (+21.2) | 193.2 | 341/420/540 | 34/3.75/3 | 0 | NORMALIZED_MATCH | OK | 0 | 10.77/17.5 | ポーズのみOK(速度外) |
| J09 | std | 166.5 (+9.5) | 186.4 | 567/550/800 | 30/3.03/2 | 1 | NORMALIZED_MATCH | OK | 0 | 10.65/16.7 | 不合格 |
| J10 | adv | 165.9 (-1.1) | 184.9 | 694/630/980 | 51/6.15/8 | 2 | NORMALIZED_MATCH | OK | 0 | 9.83/16.1 | 速度のみOK(ポーズ不良) |
| J10 | std | 154.0 (-3.0) | 187.7 | 663/675/940 | 34/3.67/3 | 1 | NORMALIZED_MATCH | OK | 0 | 10.19/16.8 | 速度のみOK(ポーズ不良) |
| J11 | adv | 161.5 (-5.5) | 178.1 | 560/580/630 | 41/6.35/10 | 0 | TRUE_CONTENT_MISMATCH | NG | 0 | 10.82/16.3 | 不合格(ASR/異音) |
| J11 | std | 167.3 (+10.3) | 181.7 | 505/470/870 | 33/2.56/0 | 1 | NORMALIZED_MATCH | OK | 0 | 10.1/16.8 | 不合格 |
| J12 | adv | 189.7 (+22.7) | 198.6 | 484/500/690 | 39/4.69/6 | 0 | NORMALIZED_MATCH | OK | 0 | 10.56/15.8 | ポーズのみOK(速度外) |
| J12 | std | 183.6 (+26.6) | 189.7 | 361/315/720 | 37/2.71/0 | 0 | TRUE_CONTENT_MISMATCH | OK | 0 | 9.65/18.1 | 不合格(ASR/異音) |
| J13 | adv | 177.6 (+10.6) | 191.1 | 539/530/690 | 41/5.1/4 | 0 | NORMALIZED_MATCH | OK | 0 | 11.13/16.4 | ポーズのみOK(速度外) |
| J13 | std | 157.8 (+0.8) | 169.6 | 492/470/860 | 41/4.2/2 | 1 | NORMALIZED_MATCH | OK | 0 | 10.7/16.7 | 暫定合格 |

判定基準(事前固定): 速度=Std 157±6 / Adv 167±6 WPM、ポーズ=文末平均がH0 T1以下(Std≤498 / Adv≤593ms)かつ800ms超長無音0〜1件、品質=Primary ASR verified・末尾一致・long_gap(medium+)なし。ピッチ幅・強弱幅は参考。Stdは6%減速後を測定。

## 4. 結果の要点
- 26 call全て成功(技術retry 0、約44秒)。ASR不合格は4件: J05 Std(had→have)、J07 Std(its→his)、J12 Std(tag→drop)、J11 Adv(原稿外の1文を挿入)。3件は1語の置換(前回H1/H3でも出たits→his型の聞き違い系を含む。聴感確認要)、J11 Advのみ原稿外1文の挿入という実質的な欠陥。候補群の大半に及ぶ品質事故ではない(STOP条件非該当)。他に異音medium+: J03 Std(1030ms long_gap)、J05 Std/Adv(click medium、聴感確認要)。
- 全体的な傾向は前回と同じ: **Adv は指示にかかわらず165〜191 WPMと速い**(13候補中10候補が目標+6超、範囲内はJ07 169.4・J10 165.9・J11 161.5のみ)。Stdは減速後で153〜184。
- 暫定合格(速度+ポーズ+品質を同一レベルで満たす)は**3件のみ(26中)**: J02 Std 156.1WPM(文末471ms、長無音0)、J13 Std 157.8WPM(文末492ms、860ms長無音1件)、J07 Adv 169.4WPM(文末510ms、長無音0)。**Std・Adv両方を満たす単一Promptはなし。**
- 惜しい候補: J03 Adv 173.3(+6.3、文末446ms、長無音0、ただし文中無音計6.23s/300ms超7本で間延び懸念)、J08 Std 161.8(文末523ms、目標より25ms長いだけ、長無音0)、J10(Std 154.0/Adv 165.9で**両レベルとも速度中心**、ただし文末663/694ms・長無音1〜2件でポーズ不良)。
- 同一Promptの減速前換算(Std実測÷0.94)で見ると、J10はStd 163.8 / Adv 165.9と**両レベルのraw速度が最も揃う**(単一Prompt運用なら理想はraw約167)。他候補はAdvがStd rawより10〜20 WPM速い(J02 166/187、J13 168/178、J03 163/173、J07 179/169は逆転)。

## 5. 軸別の効き方・相反効果
- **速度指示の種類**
  - 数値WPM: J01(150)は176.8/191.3で**ほぼ無視され最速グループ**、J12(150+間0.5s未満)は183.6/189.7で**Std最速(全候補中)、Advも最速グループ**。J02(slow, steady 130)はStdのみ156.1に下がりAdvは186.8のまま。**数値は速度制御として不信頼**(強い形容詞slow, steadyが数値より効いた可能性)。
  - 速度語: measured, deliberate(J03)は152.9/173.3で明確に効く(Std -4.4、Adv -6)が、**副作用として文末間と1000ms超の長無音を生んだ**(Std 608ms・1030ms)。slightly slower(J10)も同様に減速するが文末間が663〜694msに増える。
  - テンポ語: relaxed/easy(J04)・relaxed pace(J09)は164/184、167/188でほぼ効かない。calm broadcast pace(J08)も162/182で効果は小さい。
  - 相対速度: noticeably slower than a news bulletin(J13)は157.8/177.6。Stdでは目標付近、Advでは+10.6でなお速い。
  - 指示なし(ポーズ指示のみ J05/J06/J07): 161.7〜168.3 / 169.4〜188.0。J07(calm+短い息継ぎ)のAdvは169.4と良好。
- **ポーズ指示**
  - 停止禁止/接続(J02 Do not pause, J05 never long silence/glide, J06 link words, J08 short and connected): 文末平均は438〜523msでH0 T1(Std 498)並み〜やや短い。**「長沈黙を作るな」系は文末間を短く保つ効果あり**。ただし長無音はJ05 Stdで850ms 1件(異音medium)。
  - 数値の間上限(J12 under half a second): 文末361ms/484msで短縮は効くが、速度が最速(184/190)で**速度↑の副作用**。
  - 「short silence」を減速と併記したJ10/J13: J13は文末492/539ms(効果あり、減速も部分的)、J10は663/694msで**短縮が減速に負けた**。
- **相反効果の確認**: 速度↓でポーズ↑は明確(J03, J10: 減速するとき文末+100〜200ms、長無音増)、ポーズ↓で速度↑も明確(J12, J01, J09 Adv: 文末296〜361ms=最短グループが速度も最速)。**文末平均と速度は逆相関の傾向**(全体の相関係数は未算出)。両立したのは「slow, steady」+「Do not pause」のJ02 Std、「noticeably slower」+「very short」のJ13 Stdで、いずれも**ポーズを肯定形で強く抑えつつ減速語を強い形容で1回だけ入れた**構造。
- **声のスタイル**: ニュース調(J07/J08)は温かみ指示を残せば明るさ維持、友人への語りかけ(J09)は最速グループ(Adv 188)。落ち着いたストーリーテリング(J03/J10)は減速に最も効くがポーズ副作用。
- **強さ/構造/簡潔さ**: 強め指示(J02/J13)は有効だが副作用も大きい。極短J11(10語)は声質像不足でAdvに原稿外挿入(1件)・文中300ms超10本と最悪で、**簡潔すぎは不可**。
- **声質(参考)**: ピッチ幅(p10-p90半音)は8.95〜11.3(H0 T1 Std 9.79/Adv 10.34)、強弱幅は15.6〜18.4dB(H0 T1 17.3/16.6)で、**全候補がH0同等圏内、明確な平板化なし**。最低はJ03 Std 8.95/J07 Adv 8.99。機械指標のため最終判断はユーザー試聴。

## 6. 暫定合格・片方のみ・不合格の分類(26件)
- 暫定合格(3): J02 Std、J13 Std、J07 Adv。
- 速度のみOK(ポーズ不良)(3): J08 Std(文末+25ms、惜しい)、J10 Std、J10 Adv。
- ポーズのみOK(速度外)(12): Adv 10件(J01/J02/J03/J04/J05/J06/J08/J09/J12/J13、いずれもAdv速すぎ。J03は+6.3で境界)+Std 2件(J01/J04、速すぎ)。
- 不合格(8): ASR/異音 5件(J03 Std, J05 Std, J07 Std, J11 Adv, J12 Std)+速度・ポーズとも外れ 3件(J06 Std, J09 Std, J11 Std)。
(個別判定は `classification_r1.json`)

## 7. Round 2設計案(Fable確認後の委任_02、要新規Prompt群・継ぎ足し禁止)
狙い: 単一Promptで**raw約167 WPM(Std減速後157/Adv167)・文末≤500ms・長無音0〜1**。有望要素=J02/J13の構造(強い形容1回の減速+肯定形の強いポーズ抑制)、J10のraw速度揃い、J07のAdv、J05のglide。数値WPMは使わない。案(8候補、すべて一から書く):
1. K01: J10速度(slightly slower)+J02型の肯定形接続("let each sentence roll into the next")、storyteller像。
2. K02: J13相対速度の強さを中間化("a little slower than a news bulletin")+very short silence。
3. K03: J02の"slow, steady"を"steady, gentle"に弱めた版+Do not pause(数値なし)。
4. K04: J07(calm+短い息継ぎ)にJ13の"slower than a news bulletin"を弱く追加(Adv 169を保ちStdを下げる)。
5. K05: ポーズ肯定形のみ(glide/continuous story)+像をstorytellerに(J05の速度ずれ確認)。
6. K06: J03のmeasured単独(deliberateを除く)+短い間("briefly")、deliberateの間延び副作用の切り分け。
7. K07: J08(calm broadcast)+J02の停止禁止、ニュース調固定で間を詰める。
8. K08: 簡潔統合(J11失敗を踏まえ声質像を入れた約20語)。
見積: 8候補×Take1×Std/Adv=16call×¥1.24=約¥19.8(上振れ+20%で¥23.8)。Round 2/3枠¥40内、Round 3(絞込み再生成)に約¥16残。再現性試験(Take2/3)は合格Promptのみ。

## 8. 費用・モデル
推定 ¥32.43(TTS ¥26.60 + ASR推定 ¥5.83)/ Round1上限¥35、累計(本管理ID)¥32.43 / ¥100。26 call、技術retry 0。要求モデル=応答model_version=gemini-3.8-flash-lite-tts(最新世代)。見積は`cost_estimate_r1.json`(中心¥32.14)、実測は`cost_r1.json`。

## 9. 証跡
`prompts_r1.json` / `measurements_r1.json` / `classification_r1.json` / `cost_r1.json` / `cost_estimate_r1.json` / `state_guard_pre_r1.json`・`state_guard_r1.json`(Production state sha全一致) / `generation_log_r1.jsonl` / `attempts/*.wav`(中間wavはgit管理外) / コード: `er057_coffee_tts_style_h_speed_03_{design,gen,measure,guard,report}.py`。試聴ページは任意のため未作成(内部確認用のみ、ユーザー提示なし)。
