# ROUND4_REPORT_01: FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-04 Round 4 (2026-10-13、委任_01)

到達上限 VALIDATED(Trial)。Production変更なし。採用判断なし。ユーザー承認(2026-10-13): 音声Prompt探索 TRIAL-03 の予算を¥300まで(Trialのみ、TRIAL-03 Round 1〜3の¥72.99を含む累計上限¥300、ハードストップ¥290)。

**結論: Std/Adv両方を満たす単一Promptは0件(M01-M06 Take1 12call中)。Step D(再現性)・Step E(試聴ページ)は条件未達のため実施せず。最良候補はM05(Std暫定合格、Advは速度・文末・長無音すべて圏内だがPrimary ASRのみ不合格)。Step Aの話題転換指示でS05/S09の長無音が減る、という仮説は支持されなかった(5節)。**

モデル: gemini-3.8-flash-lite-tts(要求=応答model_version、Family-X TTSの最新世代ライン、最新)、voice Aoede、speech_metadata方式。Primary ASR=gpt-4o-mini-transcribe(既存Primary)、速度測定はfaster-whisper small local(Round 1〜3と同一)。測定条件・判定基準はRound 3と同一(Std 157±6 / raw 167±6 / Adv 167±6、文末≤498(Std)/593(Adv主判定、510参考列)、長無音(≥800ms)≤1、ASR OK、long_gapなし)。n=1の差は方向の目安。

## 1. Step A: 長無音の位置分析(¥0、`silence_positions_r4.md/json`)
- 対象: Round 1〜3全OK wav(Std 32本/Adv 32本、J01-13/K01-08/L01-06+Take2+H0 T1)を同条件で再集計。位置=原稿の第n文の直後(Snn)。
- **Std ≥800ms 22本のうち、第9文末(continue.→The)8本(36%)+第5文末(delay.→The)8本(36%)=16本(73%)、上位3位置で82%**(7 Promptずつに出現=Prompt横断)。Adv ≥800ms 9本のうち、第7文末(continue.→The)6本(66%)+第4文末(away.→When)2本=89%。Std第5/9文末の全wav平均文末無音は713/721ms(他位置は約380-590ms)。
- **仮説は『話題が切り替わる文末』への集中として支持されるが、『段落境界』ではない**: tts_input(Std/Adv)に改行・段落区切りは無い(1本の連続テキスト)。そのため『paragraph』語を使うPromptは入力に対応物がなく、Step Bは『新しい要点/話題の変わり目』の扱いを肯定形で指示する設計へ変更した(位置の語は直接指定しない)。
- 反実仮想: 第5/9文末(Adv第5/7)の無音を同wav内の他位置の中央値で頭打ちにすると、Std文末平均 507→465ms、498ms以内のwav割合 44%→78%。Advは 510→476ms(593ms以内 91%→94%)で元々影響は小。Stdは2位置を抑えるだけで文末平均の基準にほぼ届く構造。
- **Std減速後の文末平均を498ms以内にするためのraw時点の上限は 498/1.06 = 469.8ms**。全wav平均のStd(減速後)は507ms=raw換算約478msで約8ms超過。500-800msの無音は文末全般に広く出る(特定位置のみではない)。

## 2. 候補一覧(M01〜M06、全て一から記述、数値WPMなし、unhurried/slowly・否定形・位置の語は不使用)
- **M01** (39語, sha 51b8df85, maxJaccard=K01:0.319, H0=0.103): `A gentle friend telling a true story across the table, bright and warm, smiling as you speak. Go slightly slower than usual; when the story turns to a new point, start it as easily as you start any sentence.`
  - 軸: speed=slightly slower(K01型、指示文として1回) / pause=話題転換(新しい要点)でも通常の文頭と同じ入り方(肯定形) / voice=親しい語り手(K01の穏やか+明るい構造を保持) / strength=中 / structure=K01構造(像+減速指示+接続指示)の接続指示を話題転換の扱いへ置換
  - 意図: K01(raw167.8/172.6)の構造を保ち、flow straight onの代わりに話題転換点の扱いを指示。Std長無音3本(約18/33秒付近)が減るかを見る。
  - 根拠: K01(減速有効・Std長無音3本)、Step A(S05/S09に長無音が集中)
  - 想定副作用: 接続指示が文頭全般を詰めてAdvが速くなる
- **M02** (37語, sha 0253f9f3, maxJaccard=L02:0.475, H0=0.102): `A friendly, clear narrator relating a true story at a slightly slower pace than usual. Take up each new point just as you take up any sentence, starting right after the last word, as one connected telling.`
  - 軸: speed=slightly slower pace than usual(L02型、1回) / pause=新しい要点も他の文と同じく直前語の直後から開始(肯定形) / voice=ナレーター(明瞭・親しみ) / strength=中〜やや強 / structure=L02構造(ナレーター+相対ペース+一続きの語り)の禁止形を肯定の開始位置指示+話題転換へ置換
  - 意図: L02(raw165.0/171.5、Std文末563ms・長無音870ms1本)の構造を保ち、待たない(禁止形)を直前語の直後から開始の肯定形+話題転換の扱いに置換。
  - 根拠: L02(Std/Adv速度が揃う)、Step A
  - 想定副作用: right after the last wordが文末全体を詰めすぎてAdv超過、または息継ぎ不足
- **M03** (32語, sha 72798353, maxJaccard=K01:0.395, H0=0.17): `A bright, warm voice with a smile in it, telling a true story to a friend. Read slightly slower than usual, and treat every change of topic as just another sentence break.`
  - 軸: speed=slightly slower(像に埋めず独立の指示文として置換) / pause=話題の変わり目=普通の文の切れ目と同じ扱い(肯定形) / voice=明るく温かい声 / strength=中 / structure=像(速度語なし)+速度指示文+話題転換指示文
  - 意図: L05(像に減速を埋めて不発)の逆で、減速語を話者像から外し独立した指示文にして効きを確保。話題転換を通常の文末と同等に扱わせる。
  - 根拠: L05(像埋込は不発)、K01/L02(指示としての減速は有効)、Step A
  - 想定副作用: 3要素(声/速度/話題転換)の指示分離で話題転換指示が薄まる
- **M04** (34語, sha b689e360, maxJaccard=K01:0.245, H0=0.145): `A friendly radio presenter, calm and clear, sharing a true story. Let your pace be measured. When the story moves on to something new, go into it as lightly as into any other sentence.`
  - 軸: speed=measured(指示文として1回、K06/L04型の語を別文に置く) / pause=話題転換でも他の文頭と同じ軽さで入る(肯定形) / voice=落ち着いた明瞭なラジオ進行役 / strength=中 / structure=像+独立の速度文(measured)+話題転換文(3文)
  - 意図: measuredをK06の話者像内ではなく独立の短い指示文に置き直す。K06はStd文末478/486msで再現済み、Advで長無音1040ms/ASR揺れがあり、話題転換の指示で補えるかを見る。
  - 根拠: K06(Std合格2/2、Advで長無音)、Step A
  - 想定副作用: 短い独立文でmeasuredの減速力が出ない/Advが速い
- **M05** (30語, sha c915f73a, maxJaccard=K01:0.349, H0=0.091): `A warm, bright storyteller telling a true story, going slightly slower than usual. Finish every sentence fully, then move straight to the next one, even when the story changes direction.`
  - 軸: speed=slightly slower(像側ではなく進行の描写、1回) / pause=語尾を最後まで言い切って次へ直行、話の方向が変わるときも同様(肯定形) / voice=温かく明るい語り手 / strength=中 / structure=像+減速+語尾言い切り→次へ(話題転換を含む)
  - 意図: L01(語尾を柔らかく終えて即次へ、不発)を最後まで言い切って次へに変え、話題転換の扱いを併記して再検証。
  - 根拠: L01(Std長無音0だが速度ずれ)、Step A
  - 想定副作用: 言い切りの強調で文末が長くなる/Advが速すぎる(L01型)
- **M06** (37語, sha 90a6bf37, maxJaccard=K05:0.289, H0=0.121): `A calm, friendly voice with a smile in it, speaking at a measured pace. Say each sentence ending clearly and carry on at once, giving a change of subject the same short stop as every other sentence.`
  - 軸: speed=measured pace(指示文内の語として1回) / pause=語尾を明瞭に言い切って即続行、話題転換にも他と同じ短い間(肯定形) / voice=穏やかで親しみのある声 / strength=中 / structure=像+速度+語尾明瞭→続行+話題転換の間の統一
  - 意図: 語尾を落とさず次へ系の2案目。M05と異なり減速語をmeasuredにし、話題転換の間を他と同じ短い間と明示して長無音を均す。
  - 根拠: L04(均一化の逆効果。ここでは長さでなく短さの統一を指示)、K06、Step A
  - 想定副作用: 同じ短い間が機械的な均一さを生む(L04型)

## 2-2. 自己点検(`prompts_r4.json` self_check)
- 重複: M01-M06のsha全相異、J01-J13・K01-K08・L01-L06・H0ともsha相異(assert通過)。M内最大Jaccard: M01-M03=0.364、M01-M05=0.318、M01-M02=0.312。J/K/L系との最大Jaccard: M01:K01=0.319、M02:L02=0.475、M03:K01=0.395、M04:K01=0.245、M05:K01=0.349、M06:K05=0.289。H0とは0.091〜0.170。J/K/L/H0を部分文字列に含む/含まれる候補なし(assert)。
- 注意: M02はL02の構造(ナレーター+相対ペース+一続きの語り)を意図的に保ったためJaccard 0.475(最大)。禁止形(Do not wait)は肯定形(starting right after the last word)へ置換。M01はK01の構造(像+Go slightly slower+接続指示)を保ち、接続指示を話題転換の扱いへ置換。いずれも一から書いた文で継ぎ足しではない。
- 矛盾なし。速度語は各1回、全て肯定形(not/never/do not不使用をassert)。数値WPM・位置の語(delay/International/continue等)の直接指定なし(assert)。2〜3文(30〜39語)。
- tts_input shaはStd 13740eca9a44 / Adv 627f1c7f7771でv5/8wayと一致(gen4実行時assert通過)。

## 3. 測定全表(基準=H0 Take1・現行v5を先頭。Take1のみ)
3列=WPM実測(Std減速後)/raw換算(Std÷0.94)/Adv実測。

| 候補 | take | Lv | WPM実測(目標差) | raw換算(167差) | 発話WPM | 文末無音 平均/中央/最大ms | 文中無音 本/計s/300ms+ | 800ms+ | Primary ASR | 末尾 | 異音med+ | ピッチ幅st/強弱幅dB | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 Take1(TRIAL-02再利用) | - | std | 157.3 | 167.3 | 175.3 | 498/525/890 | 37/3.69/2 | 1 | NORMALIZED_MATCH | - | 0 | 9.79/17.3 | 基準 |
| H0 Take1(TRIAL-02再利用) | - | adv | 166.9 | 166.9 | 179.3 | 593/570/750 | 49/5.92/5 | 0 | NORMALIZED_MATCH | - | 0 | 10.34/16.6 | 基準 |
| 現行v5 | - | std | 145.5 | 154.8 | 172.7 | 694/630/1050 | 38/3.83/1 | 4 | - | - | 1 | 9.54/17.4 | 基準 |
| 現行v5 | - | adv | 166.9 | 166.9 | 172.3 | 456/460/740 | 49/6.21/6 | 0 | - | - | 0 | 10.13/18.0 | 基準 |
| M01 | 1 | adv | 189.1 (+22.1) | 189.1 (+22.1) | 194.4 | 429/470/580 | 48/5.27/4 | 0 | NORMALIZED_MATCH | OK | 0 | 9.89/16.6 | ポーズのみOK(速度外) |
| M01 | 1 | std | 154.7 (-2.3) | 164.6 (-2.4) | 184.8 | 674/600/960 | 32/3.26/1 | 5 | NORMALIZED_MATCH | OK | 0 | 9.94/16.6 | 速度のみOK(ポーズ不良) |
| M02 | 1 | adv | 169.8 (+2.8) | 169.8 (+2.8) | 182.8 | 607/600/800 | 37/5.3/7 | 1 | NORMALIZED_MATCH | OK | 0 | 10.98/15.5 | 速度のみOK(ポーズ不良) |
| M02 | 1 | std | 154.5 (-2.5) | 164.4 (-2.6) | 175.8 | 609/550/980 | 39/4.1/3 | 1 | NORMALIZED_MATCH | OK | 0 | 10.1/16.3 | 速度のみOK(ポーズ不良) |
| M03 | 1 | adv | 178.7 (+11.7) | 178.7 (+11.7) | 189.2 | 501/540/690 | 42/4.88/5 | 0 | NORMALIZED_MATCH | OK | 0 | 10.56/19.1 | ポーズのみOK(速度外) |
| M03 | 1 | std | 169.7 (+12.7) | 180.5 (+13.5) | 180.0 | 412/405/640 | 31/2.41/0 | 0 | NORMALIZED_MATCH | OK | 1 | 9.38/15.7 | ポーズのみOK(速度外) |
| M04 | 1 | adv | 176.9 (+9.9) | 176.9 (+9.9) | 189.3 | 516/540/650 | 43/5.29/4 | 0 | NORMALIZED_MATCH | OK | 0 | 10.73/16.1 | ポーズのみOK(速度外) |
| M04 | 1 | std | 157.4 (+0.4) | 167.4 (+0.4) | 181.3 | 578/595/830 | 25/2.39/1 | 1 | NORMALIZED_MATCH | OK | 0 | 9.64/16.3 | 速度のみOK(ポーズ不良) |
| M05 | 1 | adv | 172.7 (+5.7) | 172.7 (+5.7) | 190.3 | 587/620/650 | 42/5.57/7 | 0 | TRUE_CONTENT_MISMATCH | OK | 0 | 11.22/16.9 | 不合格(ASR/異音) |
| M05 | 1 | std | 158.6 (+1.6) | 168.7 (+1.7) | 170.4 | 473/475/760 | 33/3.08/1 | 0 | NORMALIZED_MATCH | OK | 0 | 10.53/16.9 | 暫定合格 |
| M06 | 1 | adv | 174.4 (+7.4) | 174.4 (+7.4) | 184.1 | 443/440/620 | 47/6.0/6 | 0 | TRUE_CONTENT_MISMATCH | OK | 0 | 11.31/17.8 | 不合格(ASR/異音) |
| M06 | 1 | std | 158.3 (+1.3) | 168.4 (+1.4) | 176.7 | 535/515/970 | 35/3.76/1 | 1 | NORMALIZED_MATCH | OK | 0 | 9.93/16.1 | 速度のみOK(ポーズ不良) |

## 4. 軸別の効き方(Round 4、n=1の方向の目安)
- **減速語の効き**: slightly slower / measuredを指示文として1回置いた6候補で、Stdのraw換算は M01 164.6、M02 164.4、M04 167.4、M05 168.7、M06 168.4(5/6が167±6内)。**M03(像に速度語なし、独立文『Read slightly slower than usual』)のみStdが速い(raw 180.5、+13.5)**。Round 3 L05(像に埋め込み)と同様、速度語を独立の短い指示文に置くだけではStdが減速しない場合がある(n=1)。M04のmeasured独立文は効いた(167.4)ので、M03の不発は語(slightly slower)+配置の組合せ要因の可能性(原因は未特定)。
- **Advは同じ減速語でも散る(Round 3と同傾向)**: Adv実測は M01 189.1(+22.1)、M03 178.7、M04 176.9、M06 174.4(+7.4)、M05 172.7(+5.7)、M02 169.8(+2.8)。167±6内はM02/M05のみ。Std-Advのraw差は M02 -5.4、M05 -4.0、M06 -6.0が最小、M01 -24.5が最大。
- **話題転換の扱い指示(Step Aの仮説検証)**: 全6候補が話題転換の扱いを指示したが、Stdの第5文末(delay.→The)の平均無音は Round 4 M01-M06 = 787ms(940/800/640/780/760/800)で、Round 1-3 全32本の713msより長く、第9文末も765ms(960/760/610/690/600/970)対721msで差なし〜やや長い。Std第7文末も 683対592ms。**Std ≥800ms長無音は M01 5本、M02 1本、M04 1本、M06 1本、M03/M05 0本(計8本/6wav=1.33本/wav、M01除くと3本/5wav=0.6本/wav。Round 1-3は22本/32wav=0.69本/wav)で、指示が長無音を減らした証拠はない**(n=6、Prompt間ばらつきが大きい)。M01(K01型+話題転換指示)は、K01 Round 3(Std長無音3本)より悪い5本(約9/12/18/26/33秒)。**仮説『段落(話題転換)の扱いをPromptで指示すれば長無音が解消』は本Roundでは支持されない**。Adv第7文末(continue.→The)は578ms(Round 1-3平均658ms)と短め。
- **語尾言い切り→次へ直行(M05/M06)**: M05(Finish every sentence fully, then move straight to the next one)はStd 158.6/473ms/長無音0と全指標が圏内(暫定合格)。Advは172.7(+5.7、圏内ぎりぎり)/587ms/長無音0/ピッチ幅11.22stだが**Primary ASRがTRUE_CONTENT_MISMATCH**(want→wanna。原稿の『want to say』を『wanna say』と読んだとASRが判定)。M06も同様のAdv ASR不合格(want→wanna、too欠落)で、Stdは535ms/長無音1本(970ms)でポーズ不良。同じ『言い切って次へ』構造の2候補でAdvのASRが落ちた(5節・7節)。
- **接続の肯定形置換(M02)**: L02の禁止形をright after the last wordの肯定形に置換したM02は、Std 154.5(raw 164.4)/Adv 169.8で両レベルとも速度圏内(Std-Adv raw差-5.4、本Round最小級)。ただし文末が長い(Std 609ms、Adv 607ms)。話題転換の扱いを加えても、L02のStd文末563ms/長無音870msより改善せず(609ms/980ms)。
- **M03**: Std文末が最短(412ms、長無音0)でAdvも501ms/長無音0だが、両レベルとも速い(raw 180.5/178.7)。速度が出ない代わりに文末は詰まる、というRound 1-3の相反(減速と文末詰めのトレードオフ)をM03は文末側で再現。
- **声質(参考、機械指標)**: ピッチ幅9.38〜11.31st(H0 T1 Std 9.79/Adv 10.34)、強弱幅15.5〜19.1dB(H0 17.3/16.6)で全候補H0同等圏。異音medium+: M03 Std click 1件(9.15秒、聴感未確認)。最終判断は人間の試聴。

## 5. 判定内訳(12 call)
- **両レベル合格(単一Prompt、同一take): 0件**
- 暫定合格1(M05 Std)。速度のみOK(ポーズ不良)5(M01 Std、M02 Std、M02 Adv、M04 Std、M06 Std)。ポーズのみOK(速度外)4(M01 Adv、M03 Std、M03 Adv、M04 Adv、いずれも速すぎ)。不合格(ASR)2(M05 Adv、M06 Adv。速度・ポーズ指標はM05 Adv圏内、M06 Advは速度+7.4で圏外だがポーズOK)。
- **近接例**: M05(Std暫定合格、Adv速度+5.7/文末587ms/長無音0/異音0で指標は圏内、Primary ASRのみ不合格=want→wanna。510ms厳格適用ではAdv 587msは不合格)。次点M02(両レベル速度圏内、文末607/609msと長無音1本ずつでポーズ不良)。
- 510ms厳格適用(参考): Adv ポーズOKはM01(429)/M03(501)/M06(443)で、M04(516)・M05(587)は不合格。いずれも速度外またはASR不合格のため判定は変わらない。

## 6. 再現性(Step D)・試聴ページ(Step E)
- **未実施**(両レベル合格の単一Promptが0件のため、委任文の条件により実施しない)。M05のAdv ASR(wanna)がTake依存か確認するにはTake2/3が必要だが、条件外のため実施していない(Round 5案に含めた)。
- 試聴ページ`user_test/coffee_style_h_speed_04/`は作成していない。

## 7. STOP判定と次案
### 7-1. Fable提示のSTOP条件4種への該当有無
| STOP条件 | 該当 | 根拠 |
|---|---|---|
| 成功STOP(単一PromptでStd/Adv 3 take全合格) | **非該当** | 両合格0件。Step D未実施 |
| 無益STOP(2 Round連続で最良候補の目標距離が改善しない) | **非該当(改善あり)** | Round 3最良=L02(Adv暫定合格、Std文末563ms・長無音870ms 1本でポーズ不良)。Round 4最良=M05(Std暫定合格、Advは速度・文末・長無音とも圏内でPrimary ASRのみ不合格)。両レベルのraw距離は L02 平均3.3→M05 平均3.7でrawの数値は同等だが、ポーズ側の不合格が解消した点で距離は縮小(Fable判断) |
| 予算STOP | **非該当** | 累計¥88.27/¥300(ハードストップ¥290)、残¥211.73 |
| 品質STOP(同一構造で重大ASR事故2回以上) | **該当の可能性あり(Fable判断)** | 『語尾を言い切って次へ直行』構造のM05 AdvとM06 Advで、Primary ASRがTRUE_CONTENT_MISMATCH(2件)。内容はいずれもwant→wanna(口語短縮)で、M06はtoo欠落も(固有名詞や数値は欠落なし、末尾3語は一致)。Round 3 K06 Adv Take2(内容語1語欠落)と合わせ、Advで内容語レベルのASR揺れが再発。『重大』か否かは人間/Fable判断(現行ルール上は不合格として扱った) |

### 7-2. Round 5設計案(別委任、自動実施しない。4〜6候補、見積。推奨はFable判断)
知見: (1)話題転換指示は長無音を減らさない(5節)。(2)M05型『Finish every sentence fully, then move straight to the next one』はStd全指標・Adv数値指標を満たした唯一の構造(ただしn=1、Adv ASRはwanna)。(3)Adv ASR不合格の原因は『want to』を『wanna』と読む傾向で、読み上げの忠実性を肯定形で指示する余地がある(未検証)。
- **N01** M05の『言い切り→次へ直行』を別表現へ書き換え(話題転換節を維持。構造の頑健性確認)
- **N02** M05から話題転換節を除いた版(切除比較。話題転換節が寄与しているかを見る)
- **N03** M05に『書かれた通りの語を一語ずつ読む』趣旨の肯定形指示を追加(wannaなど口語短縮を抑えるか。新軸=忠実読み)
- **N04** measuredを減速語にし『言い切り→次へ直行』を載せた版(M06のStd文末改善を狙い、話題転換節なし、Advの速度安定を確認)
- **M05 Take2**(同一Promptの再現確認、Std/Adv各1回)
- 見積: N01-N04 × Std/Adv × Take1 = 8call + M05 Take2 = 2call、計10call ≈ ¥12.8(1call≈¥1.281、+20%で¥15.4)。M05 Take3を加える場合は+2call≈¥2.6(計12call≈¥15.4、+20%で¥18.5)。累計は¥88.27+¥12.8〜15.4 = 約¥101〜104(枠¥300内)。
- 前提: Round 5の可否はFable/ユーザー判断。採用判断・Production反映は含まない。

## 8. 費用・モデル
- 生成前見積: 12 call × ¥1.281 = 中央¥15.37 / +20%上振れ¥18.45(Step C上限¥20・ハードストップ¥23、`cost_r4.json` estimate)。
- 実績: 12 call、技術retry 0、TTS ¥12.58 + ASR推定 ¥2.70 = **¥15.28**(1call≒¥1.273)。**累計(TRIAL-03含む)¥72.99 + ¥15.28 = ¥88.27 / ¥300(ハードストップ¥290、残¥211.73)**。本委任の上限¥40に対し¥15.28(Step D ¥0)。
- モデル: 要求=応答=gemini-3.8-flash-lite-tts(最新世代のFamily-X TTSライン、最新)、voice Aoede。ASR: faster-whisper small(local、¥0)で速度測定、Primary ASRは既存gpt-4o-mini-transcribe。
- 価格: 既存`er057_tone_trial_final_build_03.py`のPRICE_IN/PRICE_OUT×USD_JPY定数(Round 1〜3同一、本委任で新規出典確認は行っていない=未確認)。

## 9. 注意事項・証跡
- STOP/STOP_ALL/`round4/STOP`は生成前に不在確認。`docs/pm/delegation_log/2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_STOP_NOTICE.md`は別ID(Melos)の通知でCoffeeには無関係(TRIAL-03と同じ扱い)。有料runは1回(24秒、再起動・監督ループなし)。
- 採用判断・Production反映なし。Production state sha前後一致(`state_guard_r4.json` all_unchanged=true)。
- tts_input改変・無音カット・6%以外の速度変換・原稿編集なし。Melos関連・既存`user_test/`ページに触れていない。
- M03 Std click(medium)、M05/M06 Advのwanna/too判定は聴感未確認(ASR側の誤認か実際の読み替えかは未確認)。
- 証跡: `round4/{prompts_r4,measurements_r4,classification_r4,cost_r4,position_effect_r4,state_guard_pre_r4,state_guard_r4}.json`、`silence_positions_r4.{md,json}`、`silence_agg_r4.json`、`silence_posstats_r4.json`、`silence_rows_r4.json`、`generation_log_r4.jsonl`、`gen_summary_r4_C.json`、`_tables_r4.md`、`attempts/*.wav`(git管理外)、コード`er057_coffee_tts_style_h_speed_04_{stepA,stepA2,stepA3,design4,gen4,guard4,measure4,report4}.py`。
