## PROMPTS
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

## MEASURE
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

## PER_CAND
{
 "M05": {
  "1": {
   "std": "暫定合格",
   "adv": "不合格(ASR/異音)",
   "both_pass": false,
   "std_wpm": 158.6,
   "std_raw": 168.7,
   "adv_wpm": 172.7,
   "raw_gap_mean": 3.7,
   "raw_gap_std_vs_adv": -4.0
  },
  "2": {
   "std": "不合格",
   "adv": "ポーズのみOK(速度外)",
   "both_pass": false,
   "std_wpm": 148.3,
   "std_raw": 157.8,
   "adv_wpm": 176.1,
   "raw_gap_mean": 9.1,
   "raw_gap_std_vs_adv": -18.3
  },
  "3": {
   "std": "ポーズのみOK(速度外)",
   "adv": "ポーズのみOK(速度外)",
   "both_pass": false,
   "std_wpm": 148.8,
   "std_raw": 158.3,
   "adv_wpm": 180.2,
   "raw_gap_mean": 10.9,
   "raw_gap_std_vs_adv": -21.9
  }
 },
 "N01": {
  "1": {
   "std": "暫定合格",
   "adv": "速度のみOK(ポーズ不良)",
   "both_pass": false,
   "std_wpm": 153.5,
   "std_raw": 163.3,
   "adv_wpm": 167.1,
   "raw_gap_mean": 1.9,
   "raw_gap_std_vs_adv": -3.8
  }
 },
 "N02": {
  "1": {
   "std": "速度のみOK(ポーズ不良)",
   "adv": "速度のみOK(ポーズ不良)",
   "both_pass": false,
   "std_wpm": 161.3,
   "std_raw": 171.6,
   "adv_wpm": 170.9,
   "raw_gap_mean": 4.2,
   "raw_gap_std_vs_adv": 0.7
  }
 },
 "N03": {
  "1": {
   "std": "不合格",
   "adv": "不合格",
   "both_pass": false,
   "std_wpm": 165.3,
   "std_raw": 175.9,
   "adv_wpm": 174.7,
   "raw_gap_mean": 8.3,
   "raw_gap_std_vs_adv": 1.2
  }
 },
 "N04": {
  "1": {
   "std": "暫定合格",
   "adv": "不合格(ASR/異音)",
   "both_pass": false,
   "std_wpm": 159.6,
   "std_raw": 169.8,
   "adv_wpm": 191.5,
   "raw_gap_mean": 13.7,
   "raw_gap_std_vs_adv": -21.7
  }
 }
}
