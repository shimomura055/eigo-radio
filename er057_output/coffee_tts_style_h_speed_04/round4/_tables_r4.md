## PROMPTS
- **M01** (39語, sha 51b8df85, maxJaccard(J)=K01:0.319, H0=0.103): `A gentle friend telling a true story across the table, bright and warm, smiling as you speak. Go slightly slower than usual; when the story turns to a new point, start it as easily as you start any sentence.`
  - 軸: speed=slightly slower(K01型、指示文として1回) / pause=話題転換(新しい要点)でも通常の文頭と同じ入り方(肯定形) / voice=親しい語り手(K01の穏やか+明るい構造を保持) / strength=中 / structure=K01構造(像+減速指示+接続指示)の接続指示を話題転換の扱いへ置換
  - 意図: K01(raw167.8/172.6)の構造を保ち、flow straight onの代わりに話題転換点の扱いを指示。Std長無音3本(約18/33秒付近)が減るかを見る。
  - 根拠(Round1知見): K01(減速有効・Std長無音3本)、Step A(S05/S09に長無音が集中)
  - 想定副作用: 接続指示が文頭全般を詰めてAdvが速くなる
- **M02** (37語, sha 0253f9f3, maxJaccard(J)=L02:0.475, H0=0.102): `A friendly, clear narrator relating a true story at a slightly slower pace than usual. Take up each new point just as you take up any sentence, starting right after the last word, as one connected telling.`
  - 軸: speed=slightly slower pace than usual(L02型、1回) / pause=新しい要点も他の文と同じく直前語の直後から開始(肯定形) / voice=ナレーター(明瞭・親しみ) / strength=中〜やや強 / structure=L02構造(ナレーター+相対ペース+一続きの語り)の禁止形を肯定の開始位置指示+話題転換へ置換
  - 意図: L02(raw165.0/171.5、Std文末563ms・長無音870ms1本)の構造を保ち、待たない(禁止形)を直前語の直後から開始の肯定形+話題転換の扱いに置換。
  - 根拠(Round1知見): L02(Std/Adv速度が揃う)、Step A
  - 想定副作用: right after the last wordが文末全体を詰めすぎてAdv超過、または息継ぎ不足
- **M03** (32語, sha 72798353, maxJaccard(J)=K01:0.395, H0=0.17): `A bright, warm voice with a smile in it, telling a true story to a friend. Read slightly slower than usual, and treat every change of topic as just another sentence break.`
  - 軸: speed=slightly slower(像に埋めず独立の指示文として置換) / pause=話題の変わり目=普通の文の切れ目と同じ扱い(肯定形) / voice=明るく温かい声 / strength=中 / structure=像(速度語なし)+速度指示文+話題転換指示文
  - 意図: L05(像に減速を埋めて不発)の逆で、減速語を話者像から外し独立した指示文にして効きを確保。話題転換を通常の文末と同等に扱わせる。
  - 根拠(Round1知見): L05(像埋込は不発)、K01/L02(指示としての減速は有効)、Step A
  - 想定副作用: 3要素(声/速度/話題転換)の指示分離で話題転換指示が薄まる
- **M04** (34語, sha b689e360, maxJaccard(J)=K01:0.245, H0=0.145): `A friendly radio presenter, calm and clear, sharing a true story. Let your pace be measured. When the story moves on to something new, go into it as lightly as into any other sentence.`
  - 軸: speed=measured(指示文として1回、K06/L04型の語を別文に置く) / pause=話題転換でも他の文頭と同じ軽さで入る(肯定形) / voice=落ち着いた明瞭なラジオ進行役 / strength=中 / structure=像+独立の速度文(measured)+話題転換文(3文)
  - 意図: measuredをK06の話者像内ではなく独立の短い指示文に置き直す。K06はStd文末478/486msで再現済み、Advで長無音1040ms/ASR揺れがあり、話題転換の指示で補えるかを見る。
  - 根拠(Round1知見): K06(Std合格2/2、Advで長無音)、Step A
  - 想定副作用: 短い独立文でmeasuredの減速力が出ない/Advが速い
- **M05** (30語, sha c915f73a, maxJaccard(J)=K01:0.349, H0=0.091): `A warm, bright storyteller telling a true story, going slightly slower than usual. Finish every sentence fully, then move straight to the next one, even when the story changes direction.`
  - 軸: speed=slightly slower(像側ではなく進行の描写、1回) / pause=語尾を最後まで言い切って次へ直行、話の方向が変わるときも同様(肯定形) / voice=温かく明るい語り手 / strength=中 / structure=像+減速+語尾言い切り→次へ(話題転換を含む)
  - 意図: L01(語尾を柔らかく終えて即次へ、不発)を最後まで言い切って次へに変え、話題転換の扱いを併記して再検証。
  - 根拠(Round1知見): L01(Std長無音0だが速度ずれ)、Step A
  - 想定副作用: 言い切りの強調で文末が長くなる/Advが速すぎる(L01型)
- **M06** (37語, sha 90a6bf37, maxJaccard(J)=K05:0.289, H0=0.121): `A calm, friendly voice with a smile in it, speaking at a measured pace. Say each sentence ending clearly and carry on at once, giving a change of subject the same short stop as every other sentence.`
  - 軸: speed=measured pace(指示文内の語として1回) / pause=語尾を明瞭に言い切って即続行、話題転換にも他と同じ短い間(肯定形) / voice=穏やかで親しみのある声 / strength=中 / structure=像+速度+語尾明瞭→続行+話題転換の間の統一
  - 意図: 語尾を落とさず次へ系の2案目。M05と異なり減速語をmeasuredにし、話題転換の間を他と同じ短い間と明示して長無音を均す。
  - 根拠(Round1知見): L04(均一化の逆効果。ここでは長さでなく短さの統一を指示)、K06、Step A
  - 想定副作用: 同じ短い間が機械的な均一さを生む(L04型)

## MEASURE
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

## PER_CAND
{
 "M01": {
  "1": {
   "std": "速度のみOK(ポーズ不良)",
   "adv": "ポーズのみOK(速度外)",
   "both_pass": false,
   "std_wpm": 154.7,
   "std_raw": 164.6,
   "adv_wpm": 189.1,
   "raw_gap_mean": 12.2,
   "raw_gap_std_vs_adv": -24.5
  }
 },
 "M02": {
  "1": {
   "std": "速度のみOK(ポーズ不良)",
   "adv": "速度のみOK(ポーズ不良)",
   "both_pass": false,
   "std_wpm": 154.5,
   "std_raw": 164.4,
   "adv_wpm": 169.8,
   "raw_gap_mean": 2.7,
   "raw_gap_std_vs_adv": -5.4
  }
 },
 "M03": {
  "1": {
   "std": "ポーズのみOK(速度外)",
   "adv": "ポーズのみOK(速度外)",
   "both_pass": false,
   "std_wpm": 169.7,
   "std_raw": 180.5,
   "adv_wpm": 178.7,
   "raw_gap_mean": 12.6,
   "raw_gap_std_vs_adv": 1.8
  }
 },
 "M04": {
  "1": {
   "std": "速度のみOK(ポーズ不良)",
   "adv": "ポーズのみOK(速度外)",
   "both_pass": false,
   "std_wpm": 157.4,
   "std_raw": 167.4,
   "adv_wpm": 176.9,
   "raw_gap_mean": 5.2,
   "raw_gap_std_vs_adv": -9.5
  }
 },
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
  }
 },
 "M06": {
  "1": {
   "std": "速度のみOK(ポーズ不良)",
   "adv": "不合格(ASR/異音)",
   "both_pass": false,
   "std_wpm": 158.3,
   "std_raw": 168.4,
   "adv_wpm": 174.4,
   "raw_gap_mean": 4.4,
   "raw_gap_std_vs_adv": -6.0
  }
 }
}
