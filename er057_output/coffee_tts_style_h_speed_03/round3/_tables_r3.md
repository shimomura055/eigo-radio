## PROMPTS
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

## MEASURE
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

## PER_CAND
{
 "K01": {
  "1": {
   "std": "速度のみOK(ポーズ不良)",
   "adv": "暫定合格",
   "both_pass": false,
   "std_wpm": 157.7,
   "std_raw": 167.8,
   "adv_wpm": 172.6,
   "raw_gap_mean": 3.2,
   "raw_gap_std_vs_adv": -4.8
  },
  "2": {
   "std": "速度のみOK(ポーズ不良)",
   "adv": "暫定合格",
   "both_pass": false,
   "std_wpm": 151.3,
   "std_raw": 161.0,
   "adv_wpm": 170.3,
   "raw_gap_mean": 4.7,
   "raw_gap_std_vs_adv": -9.3
  }
 },
 "K06": {
  "1": {
   "std": "暫定合格",
   "adv": "速度のみOK(ポーズ不良)",
   "both_pass": false,
   "std_wpm": 154.5,
   "std_raw": 164.4,
   "adv_wpm": 172.2,
   "raw_gap_mean": 3.9,
   "raw_gap_std_vs_adv": -7.8
  },
  "2": {
   "std": "暫定合格",
   "adv": "不合格(ASR/異音)",
   "both_pass": false,
   "std_wpm": 156.0,
   "std_raw": 166.0,
   "adv_wpm": 163.5,
   "raw_gap_mean": 2.2,
   "raw_gap_std_vs_adv": 2.5
  }
 },
 "L01": {
  "1": {
   "std": "速度のみOK(ポーズ不良)",
   "adv": "ポーズのみOK(速度外)",
   "both_pass": false,
   "std_wpm": 153.4,
   "std_raw": 163.2,
   "adv_wpm": 185.9,
   "raw_gap_mean": 11.4,
   "raw_gap_std_vs_adv": -22.7
  }
 },
 "L02": {
  "1": {
   "std": "速度のみOK(ポーズ不良)",
   "adv": "暫定合格",
   "both_pass": false,
   "std_wpm": 155.1,
   "std_raw": 165.0,
   "adv_wpm": 171.5,
   "raw_gap_mean": 3.2,
   "raw_gap_std_vs_adv": -6.5
  }
 },
 "L03": {
  "1": {
   "std": "不合格",
   "adv": "ポーズのみOK(速度外)",
   "both_pass": false,
   "std_wpm": 163.6,
   "std_raw": 174.0,
   "adv_wpm": 180.1,
   "raw_gap_mean": 10.0,
   "raw_gap_std_vs_adv": -6.1
  }
 },
 "L04": {
  "1": {
   "std": "速度のみOK(ポーズ不良)",
   "adv": "速度のみOK(ポーズ不良)",
   "both_pass": false,
   "std_wpm": 154.8,
   "std_raw": 164.7,
   "adv_wpm": 170.4,
   "raw_gap_mean": 2.9,
   "raw_gap_std_vs_adv": -5.7
  }
 },
 "L05": {
  "1": {
   "std": "不合格",
   "adv": "ポーズのみOK(速度外)",
   "both_pass": false,
   "std_wpm": 165.3,
   "std_raw": 175.9,
   "adv_wpm": 183.1,
   "raw_gap_mean": 12.5,
   "raw_gap_std_vs_adv": -7.2
  }
 },
 "L06": {
  "1": {
   "std": "速度のみOK(ポーズ不良)",
   "adv": "ポーズのみOK(速度外)",
   "both_pass": false,
   "std_wpm": 156.8,
   "std_raw": 166.8,
   "adv_wpm": 188.2,
   "raw_gap_mean": 10.7,
   "raw_gap_std_vs_adv": -21.4
  }
 }
}
