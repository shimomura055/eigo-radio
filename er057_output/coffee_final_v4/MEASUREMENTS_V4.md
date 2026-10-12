# MEASUREMENTS_V4
WPM = measure_wpm_01.py の count_primary / frame_rms_db / find_pauses を再利用(v3の値を同法で再現確認: Std 166.0/190.5、Adv 183.2/193.6)。語数=Full Story tts_input、WPM=語数/尺、発話WPM=500ms以上ポーズ全除外後。Standard v3/v4とも6%減速後。
### Standard Full Story
| Part | 語数 | v3 尺 | v3 WPM | v3 発話WPM | v4 尺 | v4 WPM | v4 発話WPM |
|---|---|---|---|---|---|---|---|
| Part1 | 117 | 46.96 | 149.5 | 181.2 | 48.24 | 145.5 | 172.8 |
| Part2 | 161 | 53.48 | 180.6 | 204.3 | 56.5 | 171.0 | 178.3 |
| Part3 | 134 | 48.49 | 165.8 | 183.9 | 47.69 | 168.6 | 179.1 |
| 全体 | 412 | 148.93 | 166.0 | 190.5 | 152.43 | 162.2 | 177.0 |
v3比: 全体WPM -2.3% / 発話WPM -7.1% / 尺 +2.4%

### Advanced Full Story
| Part | 語数 | v3 尺 | v3 WPM | v3 発話WPM | v4 尺 | v4 WPM | v4 発話WPM |
|---|---|---|---|---|---|---|---|
| Part1 | 131 | 46.29 | 169.8 | 180.9 | 47.08 | 166.9 | 176.3 |
| Part2 | 179 | 55.8 | 192.5 | 198.5 | 55.88 | 192.2 | 203.9 |
| Part3 | 152 | 49.21 | 185.3 | 199.9 | 50.44 | 180.8 | 187.5 |
| 全体 | 462 | 151.3 | 183.2 | 193.6 | 153.4 | 180.7 | 190.0 |
v3比: 全体WPM -1.4% / 発話WPM -1.9% / 尺 +1.4%

## 通し尺 / Gate
- Standard: 通し 317.683s(v3 314.172s)、peak 0.95718、clipping 0、headroom valve False(閾値0.98 OK=True、原因 Key Phrase 5は再利用KP5でFull Story起因でない、scalar 1.0)、wav長=timeline長=mp3長=317.683、>1s内部無音 [{'part': 'Key Phrase 1', 'longest_silence_s': 1.06}, {'part': 'Key Phrase 4', 'longest_silence_s': 1.04}, {'part': 'Key Phrase 5', 'longest_silence_s': 1.03}](v3同様KP内の仕様ポーズ)
- Advanced: 通し 317.07s(v3 314.97s)、peak 0.97995、clipping 0、headroom valve True(閾値0.98 OK=True、原因 Key Phrase 5は再利用KP5でFull Story起因でない、scalar 0.99533709)、wav長=timeline長=mp3長=317.07、>1s内部無音 [{'part': 'Key Phrase 4', 'longest_silence_s': 1.03}](v3同様KP内の仕様ポーズ)

## 異音検知(er057_audio_anomaly_detect_trial_01、閾値不変、通しwav)
- std: 候補 22(v3 20)、非固定音源 13、medium/high(非固定) 0件
- adv: 候補 21(v3 20)、非固定音源 12、medium/high(非固定) 0件
