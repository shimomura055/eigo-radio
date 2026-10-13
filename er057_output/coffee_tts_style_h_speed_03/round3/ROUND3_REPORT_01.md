# ROUND3_REPORT_01: FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-03 Round 3 (最終探索Round、2026-10-13、委任_03)

到達上限 VALIDATED(Trial)。Production変更なし。採用判断なし。結論: **Std/Adv両方を満たす単一Promptは0件(L01-L06 Take1 12call中、暫定合格1件=L02 Adv。K01/K06 Take2 4callでも両レベル合格なし)。Step C(再現性)・Step D(試聴ページ)は条件未達のため実施せず。本IDは最終Roundのため追加Roundは提案せず、7節にUSER_DECISION_REQUIRED用の総括を記載。**
モデル: gemini-3.8-flash-lite-tts(要求=応答model_version、Family-X TTSの最新世代ライン)、voice Aoede、speech_metadata方式。Primary ASR=gpt-4o-mini-transcribe(既存Primary、生成ログ記録)、速度測定はfaster-whisper small local(Round 1/2と同一)。測定条件はRound 2と同一(RMS<-40dBFS/50ms、WPM=原稿語数/尺、Stdは6%減速後を実測、3列併記: Std減速後実測/raw換算=Std÷0.94/Adv実測)。n=1の差は方向の目安。
Fable記録の評価条件: Std文末≤498ms(H0 T1実測)、Adv文末≤**593ms**(H0 T1実測、主判定)。510ms厳格適用は`classification_r3.json`のpause_ok_adv510に参考記録。判定基準(Std 157±6 / raw 167±6 / Adv 167±6、長無音(≥800ms)≤1、ASR OK、long_gap(medium+)なし)はRound 2と同一。

## 1. 候補一覧(L01〜L06、全て一から記述、数値WPMなし、unhurried/slowly不使用)
- **L01** (26語, sha 26b0b05b, maxJaccard(J)=K01:0.41, H0=0.163): `A warm, bright storyteller with a smile in the voice, going slightly slower than usual. Let each sentence end softly and begin the next at once.`
  - 軸: speed=slightly slower(像側の控えめ減速、1回のみ) / pause=語尾を柔らかく終えて即次へ(語尾処理+肯定形) / voice=落ち着いたストーリーテリング / strength=中 / structure=速度+語尾処理
  - 意図: K01(slightly slower)はraw 167.8/172.6で最良級だがStdの文末後800ms超が3本。『flow straight on』の接続指示を、語尾処理(softly end / at once)という別軸に置換して長無音が減るかを見る。
  - 根拠(Round1知見): K01(減速有効、Std長無音3本)
  - 想定副作用: 語尾処理が効かず長無音が残る、または語尾が弱まって聞き取りにくい
- **L02** (30語, sha 576c3a96, maxJaccard(J)=J10:0.213, H0=0.111): `A clear, friendly narrator sharing a true story at a slightly slower pace than usual. Do not wait between sentences; begin each new one right away, as one connected telling.`
  - 軸: speed=slightly slower(相対ペース、1回のみ) / pause=待たない禁止+肯定の即開始+一続きの語り / voice=ナレーター(明瞭・親しみ) / strength=中〜やや強 / structure=速度+禁止/肯定併記(1文に集約)
  - 意図: K01の肯定接続にK07/K03型の禁止形を併記して接続を強める。減速語は同じslightly slowerを残しStd長無音と文末間が詰まるかを確認。
  - 根拠(Round1知見): K01(長無音)・K07(禁止形で文末詰まる)・K03(禁止形でも減速は残る)
  - 想定副作用: 禁止形が強すぎて全体が速くなる(Adv超過)
- **L03** (23語, sha 04ffa761, maxJaccard(J)=K05:0.353, H0=0.205): `A warm, measured voice, bright and clear, carrying the story along. Carry each sentence into the next without a break in the flow.`
  - 軸: speed=measured voice(像としての減速、deliberateなし) / pause=肯定形の運び(carry into the next) / voice=落ち着いた語り / strength=中 / structure=速度+ポーズ肯定形
  - 意図: K06(measured)はStd合格だがAdv文末636ms・1040ms長無音。『Pause only briefly』(間を意識させる文)を、間に言及しない肯定形の運びに置換して、間への注意誘発を避ける。
  - 根拠(Round1知見): K06(Std合格・Adv間延び)・K01(肯定接続)
  - 想定副作用: 間に言及しないため文末が伸びる/measuredだけでは減速が足りない
- **L04** (22語, sha 5ad68036, maxJaccard(J)=J07:0.258, H0=0.149): `A friendly storyteller with a measured, even rhythm, warm and clear. Take short, quick breaths between sentences, all about the same length.`
  - 軸: speed=measured, even rhythm(リズム均一化語) / pause=短く均一な息継ぎ / voice=落ち着いたストーリーテリング / strength=中 / structure=速度+ポーズ(均一化)
  - 意図: 減速と間の均一化を『even rhythm』『同じ長さの息継ぎ』で同時に狙う。長無音(外れ値)を均一化で抑えられるかを見る(K01/K06の外れ値型長無音への対策)。
  - 根拠(Round1知見): K06(measuredで減速)・J07(短い息継ぎでAdv良好)
  - 想定副作用: 均一化指示が機械的な抑揚になる(ピッチ幅低下)
- **L05** (27語, sha bfcd87f5, maxJaccard(J)=K05:0.351, H0=0.163): `A bright, warm storyteller who takes it a bit slower than most people do, with a smile in the voice. Each sentence leads right into the next.`
  - 軸: speed=a bit slower(指示でなく像側に埋め込み) / pause=肯定形の連結(leads right into) / voice=ストーリーテラー像に減速を内包 / strength=中 / structure=像に速度を内包+ポーズ肯定形
  - 意図: 指示文の相反(『遅く』と『間を詰める』)を避け、減速を話者像の性格として与える。像が速度を決め、指示は連結だけに絞る。
  - 根拠(Round1知見): K01(指示型減速)・K05(像のみでは速くなる=像に速度語が無かった)
  - 想定副作用: 像側の減速語が弱く、K05同様に速くなる
- **L06** (24語, sha 9bd95f2f, maxJaccard(J)=K03:0.406, H0=0.227): `A warm, friendly voice, easy and even, never rushed, never dragging, with a smile in it. Keep the story rolling from sentence to sentence.`
  - 軸: speed=never rushed, never dragging(両側否定でペース中庸) / pause=肯定形(keep rolling) / voice=自然な語りかけ / strength=中 / structure=速度(両側否定)+ポーズ肯定形
  - 意図: unhurried/slowly不使用の制約下で、速すぎ(rushed)と間延び(dragging)を両側否定でペース中庸に誘導。間延びを明示的に否定することで文末間・長無音を抑える。
  - 根拠(Round1知見): K03/K08(弱形速度語で減速消失)・K06(間延び)
  - 想定副作用: 中庸指示では減速が弱く両レベル速い


## 2. 自己点検(`prompts_r3.json` self_check)
- 重複: L01-L06のsha全相異、J01-J13・K01-K08・H0ともsha相異(assert通過)。L内最大Jaccard: L01-L05=0.412、L01-L03=0.294、L03-L05=0.294。J/K系との最大Jaccard: L01:K01=0.410、L02:J10=0.213、L03:K05=0.353、L04:J07=0.258、L05:K05=0.351、L06:K03=0.406。H0とは0.111〜0.227。J/K/H0を部分文字列に含む/含まれる候補なし(assert)。
- 注意: L01は「slightly slower than usual」をK01と共有(Jaccard 0.410が最大)。減速語を意図的に残した再検証であり、接続部は別表現。一から書いた2文であり継ぎ足しではない。
- 矛盾なし。L05は減速を像に内包して指示文の相反(遅く/間を詰める)を避けた設計、L06は両側否定。冗長なし(速度/間/声質を各1回)。全て2文(22〜30語)、数値WPMなし。
- tts_input shaはStd 13740eca9a44 / Adv 627f1c7f7771でv5/8wayと一致(gen3実行時assert通過)。

## 3. 測定全表(基準=H0 Take1・現行v5を先頭。K01/K06はTake1(Round 2)とTake2(Round 3)を併記)
| 候補 | take | Lv | WPM実測(目標差) | raw換算(167差) | 発話WPM | 文末無音 平均/中央/最大ms | 文中無音 本/計s/300ms+ | 800ms+ | Primary ASR | 末尾 | 異音med+ | ピッチ幅st/強弱幅dB | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0 Take1(TRIAL-02再利用) | - | std | 157.3 | 167.3 | 175.3 | 498/525/890 | 37/3.69/2 | 1 | NORMALIZED_MATCH | - | 0 | 9.79/17.3 | 基準 |
| H0 Take1(TRIAL-02再利用) | - | adv | 166.9 | 166.9 | 179.3 | 593/570/750 | 49/5.92/5 | 0 | NORMALIZED_MATCH | - | 0 | 10.34/16.6 | 基準 |
| 現行v5 | - | std | 145.5 | 154.8 | 172.7 | 694/630/1050 | 38/3.83/1 | 4 | - | - | 1 | 9.54/17.4 | 基準 |
| 現行v5 | - | adv | 166.9 | 166.9 | 172.3 | 456/460/740 | 49/6.21/6 | 0 | - | - | 0 | 10.13/18.0 | 基準 |
| K01 | 1 | adv | 172.6 (+5.6) | 172.6 (+5.6) | 188.6 | 580/560/800 | 44/5.25/4 | 1 | NORMALIZED_MATCH | OK | 0 | 10.11/17.9 | 暫定合格 |
| K01 | 2 | adv | 170.3 (+3.3) | 170.3 (+3.3) | 173.4 | 466/430/820 | 49/6.55/6 | 1 | NORMALIZED_MATCH | OK | 0 | 10.22/17.5 | 暫定合格 |
| K01 | 1 | std | 157.7 (+0.7) | 167.8 (+0.8) | 174.7 | 522/480/910 | 44/3.65/1 | 3 | NORMALIZED_MATCH | OK | 1 | 9.08/17.1 | 速度のみOK(ポーズ不良) |
| K01 | 2 | std | 151.3 (-5.7) | 161.0 (-6.0) | 166.2 | 564/435/1070 | 49/4.8/1 | 3 | NORMALIZED_MATCH | OK | 0 | 12.21/16.7 | 速度のみOK(ポーズ不良) |
| K06 | 1 | adv | 172.2 (+5.2) | 172.2 (+5.2) | 191.4 | 636/570/1040 | 44/5.42/5 | 1 | NORMALIZED_MATCH | OK | 0 | 10.38/18.2 | 速度のみOK(ポーズ不良) |
| K06 | 2 | adv | 163.5 (-3.5) | 163.5 (-3.5) | 179.9 | 530/610/750 | 42/6.65/7 | 0 | TRUE_CONTENT_MISMATCH | OK | 0 | 12.0/16.5 | 不合格(ASR/異音) |
| K06 | 1 | std | 154.5 (-2.5) | 164.4 (-2.6) | 171.3 | 478/530/740 | 37/4.31/3 | 0 | NORMALIZED_MATCH | OK | 0 | 9.88/18.2 | 暫定合格 |
| K06 | 2 | std | 156.0 (-1.0) | 166.0 (-1.0) | 166.7 | 486/460/660 | 41/4.72/3 | 0 | NORMALIZED_MATCH | OK | 0 | 11.31/15.7 | 暫定合格 |
| L01 | 1 | adv | 185.9 (+18.9) | 185.9 (+18.9) | 196.1 | 486/530/570 | 35/4.86/6 | 0 | NORMALIZED_MATCH | OK | 0 | 10.53/18.0 | ポーズのみOK(速度外) |
| L01 | 1 | std | 153.4 (-3.6) | 163.2 (-3.8) | 169.5 | 522/555/740 | 39/4.0/2 | 0 | NORMALIZED_MATCH | OK | 0 | 11.06/16.7 | 速度のみOK(ポーズ不良) |
| L02 | 1 | adv | 171.5 (+4.5) | 171.5 (+4.5) | 191.1 | 574/680/730 | 37/5.69/6 | 0 | NORMALIZED_MATCH | OK | 0 | 9.98/17.6 | 暫定合格 |
| L02 | 1 | std | 155.1 (-1.9) | 165.0 (-2.0) | 170.2 | 563/535/870 | 42/3.99/4 | 1 | NORMALIZED_MATCH | OK | 0 | 9.84/16.1 | 速度のみOK(ポーズ不良) |
| L03 | 1 | adv | 180.1 (+13.1) | 180.1 (+13.1) | 192.4 | 501/540/600 | 50/5.93/5 | 0 | NORMALIZED_MATCH | OK | 0 | 10.81/18.0 | ポーズのみOK(速度外) |
| L03 | 1 | std | 163.6 (+6.6) | 174.0 (+7.0) | 181.1 | 502/525/690 | 39/3.96/2 | 0 | NORMALIZED_MATCH | OK | 1 | 11.69/16.7 | 不合格 |
| L04 | 1 | adv | 170.4 (+3.4) | 170.4 (+3.4) | 191.5 | 651/630/860 | 35/4.77/5 | 1 | NORMALIZED_MATCH | OK | 0 | 9.33/17.8 | 速度のみOK(ポーズ不良) |
| L04 | 1 | std | 154.8 (-2.2) | 164.7 (-2.3) | 184.3 | 644/625/940 | 35/3.54/2 | 2 | NORMALIZED_MATCH | OK | 0 | 8.51/16.2 | 速度のみOK(ポーズ不良) |
| L05 | 1 | adv | 183.1 (+16.1) | 183.1 (+16.1) | 200.5 | 574/590/780 | 37/5.0/5 | 0 | NORMALIZED_MATCH | OK | 0 | 10.65/16.3 | ポーズのみOK(速度外) |
| L05 | 1 | std | 165.3 (+8.3) | 175.9 (+8.9) | 186.6 | 520/530/730 | 28/2.53/0 | 0 | NORMALIZED_MATCH | OK | 0 | 10.22/17.7 | 不合格 |
| L06 | 1 | adv | 188.2 (+21.2) | 188.2 (+21.2) | 211.9 | 586/570/710 | 34/4.06/4 | 0 | NORMALIZED_MATCH | OK | 1 | 9.22/15.8 | ポーズのみOK(速度外) |
| L06 | 1 | std | 156.8 (-0.2) | 166.8 (-0.2) | 170.1 | 520/475/850 | 35/2.96/1 | 1 | NORMALIZED_MATCH | OK | 0 | 9.64/17.0 | 速度のみOK(ポーズ不良) |


## 4. 軸別の効き方(Round 3、n=1の方向の目安)
- **強い減速語はStdのrawを揃える(Round 1/2と整合)**: slightly slower(L01 raw163.2、L02 165.0)、measured(L04 164.7)、never rushed/never dragging(L06 166.8)は、Stdのraw換算が167±6内。一方、measured voiceに間の言及なし(L03 raw174.0)と、像側の「a bit slower than most」(L05 raw175.9)は減速が弱く速い。**減速語を像に埋め込む(L05)案は不発、指示文として置く方が効く**。
- **Advは同じ減速語でも大きくばらつく**: slightly slowerを含むK01 Adv 172.6/170.3、L02 Adv 171.5に対しL01 Adv 185.9(+18.9)。measured系もL03 Adv 180.1、L04 Adv 170.4。Std rawがほぼ同じ(163〜168)でもAdvが170〜188に散る(Std-Advのraw差: L01 -22.7、L06 -21.4、L02 -6.5、L04 -5.7、K01 -4.8/-9.3、K06 -7.8/+2.5)。Advは減速語より他の語(接続・禁止指示の書き方)の影響を受けやすい、というのが方向の目安。
- **Stdの文末間はraw速度を保つ候補で498msを超えやすい**: Stdで速度OKのL01 522、L02 563、L04 644、L06 520msは全て文末>498msでポーズ不良。速度が速くなるL03 502、L05 520も498超(速度は外れ)。Std文末≤498かつ速度OKを同時に満たしたのは、K06の2take(478/486ms)のみ(Round 1のJ02 471、J13 492は単発)。
- **長無音(≥800ms)は2か所に集中**: 約18秒付近(delay.→International: K01 Std 1070、L02 Std 870、L04 Std 870)と約33秒付近の段落境界(continue.→The: K01 Std 1030、L04 Std/Adv 940/860、L06 Std 850)。Round 2で指摘した段落境界起因の可能性(原稿構造起因)を再確認(Prompt横断で同位置に出る)が、因果は未検証。**Stdは6%減速で無音も約6%延びる(src→dst=1.06倍、gen_log記録)ため、同じrawでもAdvより文末間・長無音の基準を超えやすい構造**(Adv側の同位置は800ms未満が多い)。
- **均一化(L04: even rhythm + 同じ長さの息継ぎ)**: 速度は揃う(Std 164.7/Adv 170.4)が文末が長い(644/651ms)、長無音も増え、ピッチ幅も最小(Std 8.51st)。均一化指示は逆効果(n=1)。
- **語尾処理(L01)**: Stdの長無音は0本になった(K01 Stdの3本から減少)が、文末平均522msと速度過少気味(Adv 185.9で大幅に速い)。Std/Advの乖離が最大(-22.7)。
- **禁止+肯定の一文集約(L02)**: Std 155.1(raw165.0)/Adv 171.5で両レベルが速度圏内、Advは暫定合格。Stdは文末563ms+870ms長無音1本でポーズ不良(文末が基準を65ms超過)。Round 3では最もStd/Adv速度が揃った新規候補(raw差-6.5)。
- **K01/K06再現確認(6節)**。
- **声質(参考、機械指標)**: ピッチ幅8.51〜12.21st(H0 T1 Std 9.79/Adv 10.34)、強弱幅15.7〜18.2dB(H0 17.3/16.6)で、L04 Std 8.51st(最小)とK01/K06 Take2 Std 12.21/11.31st(大)を除き全候補H0同等圏。異音medium+: L03 Std click 1件(24.75s)、L06 Adv click 1件(15.76s)(聴感確認未実施)。最終判断は人間の試聴。

## 5. 判定内訳(16 call)
- **両レベル合格(単一Prompt、同一take): 0件**
- L01-L06 Take1(12call): 暫定合格1(L02 Adv)、速度のみOK(ポーズ不良)5(L01 Std、L02 Std、L04 Std、L04 Adv、L06 Std)、ポーズのみOK(速度外)4(L01/L03/L05/L06 Adv、いずれも速すぎ)、不合格2(L03 Std、L05 Std、速度・ポーズとも外れ)。
- K01/K06 Take2(4call): 暫定合格2(K01 Adv、K06 Std)、速度のみOK(ポーズ不良)1(K01 Std)、不合格(ASR)1(K06 Adv)。
- **近接例**: L02(raw差-6.5、Adv合格、Std文末563ms・長無音1本870ms)。K01は両take共Adv合格・Std長無音3本で不合格(Std側は再現性ある課題)。
- 510ms厳格適用(参考): Adv暫定合格はK01 Adv Take2(466ms)のみ、L02 Adv(574ms)・K01 Adv Take1(580ms)は不合格になる。

## 6. 再現確認(K01・K06 Take2)とStep C
- **K01**: Adv Take1 172.6/580ms/長無音1 → Take2 170.3/466ms/長無音1(820ms)で**暫定合格を再現(2/2)**。Std Take1 157.7/522ms/長無音3 → Take2 151.3(raw161.0、-5.7でぎりぎり圏内)/564ms/長無音3(1070/910/1030ms)で**ポーズ不良を再現(2/2)**。K01 Stdの長無音3本は偶然ではなくK01の挙動(約18/27/34秒の文末後)。
- **K06**: Std Take1 154.5/478ms/長無音0 → Take2 156.0/486ms/長無音0で**暫定合格を再現(2/2)**。Adv Take1 172.2/636ms/長無音1(1040ms)でポーズ不良 → Take2 163.5/530ms/長無音0だがPrimary ASRがTRUE_CONTENT_MISMATCH(原稿のtooに相当する内容語1語が欠落とされた、末尾3語一致は維持)で**ASR不合格**。Take2はASR以外の指標では圏内だが、規則通り不合格。K06 Advは2take中0合格(ばらつきが大きい)。
- ばらつき(同一Prompt・同一条件の2take): K01 Std WPM 157.7/151.3(差6.4)、K01 Adv 172.6/170.3、K06 Std 154.5/156.0、K06 Adv 172.2/163.5(差8.7)。n=2のため目安。Adv文末平均はK01 580→466、K06 636→530で、K06 Adv Take1の636msは偶然寄り(Take2は530ms)だが、1040ms長無音の有無は2take間で揺れる。
- **Step C: 未実施**(両レベル合格の単一Promptが0件のため、委任文の条件により実施しない)。**Step D(試聴ページ): 作成なし**。

## 7. 総括: Round 1〜3を通じた知見とユーザー判断用の選択肢
(本IDの最終探索Round。追加Roundは提案しない。USER_DECISION_REQUIRED用。推奨は書かない。)

### 7-1. 知見(Round 1: J01-J13 / Round 2: K01-K08 / Round 3: L01-L06、計27 Prompt、Take1ベース)
- **単一Promptで両レベル合格は0件/27**(各Round末の判定は、Round 1・2・3とも両レベル合格0)。
- **効く軸**: 「強い形容1回の減速語(slightly slower、measured、slow)」がStdのraw換算を167付近に揃える。Std speed 157±6はTake1で13/27 Promptが圏内。肯定形の接続指示(flow straight on等)は、Stdの文末間を一部詰める。
- **効かない軸**: 弱形減速語(a little/a touch/steady/relaxed/calm broadcast pace/a bit slower)、像のみ(storyteller像)、均一化指示(even rhythm: 逆効果)、極短Prompt(Round 1 J11の品質事故、Round 2 K08で回避したが減速力なし)。ポーズ指示のみでは速くなる(J05/K05)。
- **相反関係**: 減速するとStd文末平均+数十〜200ms(Round 1/2既報)、長無音(特に約18秒・約33秒の文末後)が増える。文末を詰めると速度が戻る。この2つを同時に満たしたStd Promptは、K06(2take再現、478/486ms)とJ02/J13(単発)のみ。Stdは6%減速で無音も約6%延びるため、構造的に文末間の基準を超えやすい。
- **Advが下がりにくい事実**: Adv Take1の速度は27 Promptで161.5〜191.3(中央値180.1)。167±6内は7/27(J07 169.4/J10 165.9/J11 161.5(ASR不合格)/K01 172.6/K06 172.2/L02 171.5/L04 170.4)、残り20は速い側で、遅い側に外れた例はなし。減速語を入れても、Std rawと同じ水準までは落ちにくい(Std-Adv rawの乖離は-4.8〜-22.7)。
- **単一Prompt両立の可否**: 27 Prompt(+Take2)の範囲では未達。Stdの文末≤498ms(H0 T1が基準で、もともと厳しい基準)と、Advの速度167±6を、同じ語で満たすPromptは見つかっていない。ただし探索は27 Prompt、各n=1(一部n=2)であり、存在しないことの証明ではない。
- 段落境界などの長無音は原稿構造起因の可能性(未検証)。Prompt横断で同位置に出る。

### 7-2. 再現性のある個別合格(Take1+Take2、単一レベルのみ)
| Prompt | Lv | Take | WPM(raw) | 文末平均ms | 長無音(≥800ms) | ASR | 判定 |
|---|---|---|---|---|---|---|---|
| K06 | Std | 1/2 | 154.5(164.4)/156.0(166.0) | 478/486 | 0/0 | OK/OK | 合格2/2 |
| K01 | Adv | 1/2 | 172.6/170.3 | 580/466 | 1/1 | OK/OK | 合格2/2(593基準。510基準だとTake1は不合格) |
| J02 | Std | 1(単発) | 156.1 | 471 | 0 | OK | 合格(再現未確認) |
| J13 | Std | 1(単発) | 157.8 | 492 | 1 | OK | 合格(再現未確認) |
| J07 | Adv | 1(単発) | 169.4 | 510 | 0 | OK | 合格(再現未確認) |
| L02 | Adv | 1(単発) | 171.5 | 574 | 0 | OK | 合格(再現未確認) |

### 7-3. 選択肢(推奨なし、長所短所のみ)
- **(i) Std/Advで別Promptを使う案**(例: Std=K06、Adv=K01。K06 Std・K01 Advは各2/2再現):
  - 長所: 実測で各レベルの基準を満たした再現性ある組合せが既にある(K06 Std 154.5/156.0、478/486ms、長無音0/0。K01 Adv 172.6/170.3、580/466ms、長無音1/1)。H0と比べStd文末はほぼ同等(≤498)。
  - 短所: Prompt管理が2本になる(現行Productionがレベル別Promptを許容する配線かは本Trialで未確認。要確認)。K06はAdvで不安定(Take2はASR不合格)、K01 Stdは長無音3本(Stdには使えない)。レベル間で声質の連続性が変わりうる(最終判断は人間の試聴)。n=2。
- **(ii) Advにも軽微な減速後処理を適用する案**(現行仕様外。現行はStd 6%減速のみ。本Trialでは実施せず):
  - 長所: 単一Prompt(例: K06/K01系)でAdvが172〜173のとき6%後処理で約162前後(圏内)になる計算。Prompt管理が1本のまま。
  - 短所: 現行仕様の変更が必要(ユーザー承認が前提)。後処理はAdvの長無音・文末間も約6%延ばす(Adv K06 Take1の1040msは約1100msへ)。Advは現行v5で既に166.9(基準)であり、改悪するリスクもある。実測していない(計算上の目安)。
- **(iii) H0 T1を暫定維持**:
  - 長所: 追加コスト0、既に基準(Std 157.3/498ms/長無音1、Adv 166.9/593ms/長無音0)として全測定の基準点になっている。
  - 短所: 本IDで狙った「単一Promptでの改善」は得られない。H0はTRIAL-02由来でn=1。
- **(iv) 追加予算で探索継続**:
  - 長所: 本ID残¥27.01(枠¥100内、約21 call)。有望な系統(K01/K06、L02)の細部微調整・再現性追加が可能。
  - 短所: 3Round・27 Promptで単一Prompt両合格0のため成功確率は不明。追加予算はユーザー未承認で、Round 3が本IDの上限。

## 8. 費用・モデル
- 生成前見積: 16 call × ¥1.254 = 中央¥20.06 / +20%上振れ¥24.08(Step B上限¥23・ハードストップ¥26、`cost_r3.json` estimate)。
- 実績: 16 call、技術retry 0、TTS ¥16.88 + ASR推定 ¥3.61 = **¥20.49**(1call≒¥1.281)。**本ID累計 ¥52.50 + ¥20.49 = ¥72.99 / ¥100(残¥27.01)**。Step C ¥0(未実施)。
- モデル: 要求=応答=gemini-3.8-flash-lite-tts(最新世代のFamily-X TTSライン)、voice Aoede。ASR: faster-whisper small(local、¥0)で速度測定、Primary ASRは既存gpt-4o-mini-transcribe。
- 価格: 既存`er057_tone_trial_final_build_03.py`のPRICE_IN/PRICE_OUT×USD_JPY定数(Round 1/2同一、本委任で新規出典確認は行っていない)。

## 9. 注意事項・証跡
- STOP/STOP_ALL/`round*/STOP`は生成前に不在確認。`docs/pm/delegation_log/2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_STOP_NOTICE.md`は別ID(Melos)の通知でCoffeeには無関係(Round 1/2と同じ扱い)。有料runは1回(28秒、再起動・監督ループなし)。
- 採用判断・Production反映なし。Production state sha前後一致(`state_guard_r3.json` all_unchanged=true)。
- 異音medium+(L03 Std/L06 Adv click各1件)は聴感未確認。K06 Adv Take2のASR不合格は、原稿のtooに相当する1語の欠落判定で、ASR側の誤認か実際の欠落かは未確認。
- 証跡: `round3/{prompts_r3,measurements_r3,classification_r3,cost_r3,state_guard_pre_r3,state_guard_r3}.json`、`generation_log_r3.jsonl`、`gen_summary_r3_B.json`、`_tables_r3.md`、`attempts/*.wav`(git管理外)、コード`er057_coffee_tts_style_h_speed_03_{design3,gen3,guard3,measure3,report3}.py`。
