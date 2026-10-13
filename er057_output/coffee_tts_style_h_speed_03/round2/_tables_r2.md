## PROMPTS
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

## MEASURE
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
  }
 },
 "K02": {
  "1": {
   "std": "不合格",
   "adv": "ポーズのみOK(速度外)",
   "both_pass": false,
   "std_wpm": 166.7,
   "std_raw": 177.3,
   "adv_wpm": 186.5,
   "raw_gap_mean": 14.9,
   "raw_gap_std_vs_adv": -9.2
  }
 },
 "K03": {
  "1": {
   "std": "不合格(ASR/異音)",
   "adv": "ポーズのみOK(速度外)",
   "both_pass": false,
   "std_wpm": 152.2,
   "std_raw": 161.9,
   "adv_wpm": 174.5,
   "raw_gap_mean": 6.3,
   "raw_gap_std_vs_adv": -12.6
  }
 },
 "K04": {
  "1": {
   "std": "ポーズのみOK(速度外)",
   "adv": "不合格",
   "both_pass": false,
   "std_wpm": 172.9,
   "std_raw": 183.9,
   "adv_wpm": 173.3,
   "raw_gap_mean": 11.6,
   "raw_gap_std_vs_adv": 10.6
  }
 },
 "K05": {
  "1": {
   "std": "不合格(ASR/異音)",
   "adv": "ポーズのみOK(速度外)",
   "both_pass": false,
   "std_wpm": 168.7,
   "std_raw": 179.5,
   "adv_wpm": 181.8,
   "raw_gap_mean": 13.7,
   "raw_gap_std_vs_adv": -2.3
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
  }
 },
 "K07": {
  "1": {
   "std": "不合格",
   "adv": "ポーズのみOK(速度外)",
   "both_pass": false,
   "std_wpm": 170.2,
   "std_raw": 181.1,
   "adv_wpm": 184.5,
   "raw_gap_mean": 15.8,
   "raw_gap_std_vs_adv": -3.4
  }
 },
 "K08": {
  "1": {
   "std": "ポーズのみOK(速度外)",
   "adv": "ポーズのみOK(速度外)",
   "both_pass": false,
   "std_wpm": 164.1,
   "std_raw": 174.6,
   "adv_wpm": 179.7,
   "raw_gap_mean": 10.1,
   "raw_gap_std_vs_adv": -5.1
  }
 }
}
