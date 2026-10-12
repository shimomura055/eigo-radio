| ID | 特徴 | 総秒 | 全体WPM | 発話WPM(500ms) | 発話WPM(300ms) | P0比 全体% | P0比 発話% | 秒差 | 文間無音(500ms)数/計s/最長s | 全無音量差s | 暫定目安 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P0 | 現行PD8(基準) | 46.29 | 169.8 | 180.9 | 199.1 | +0.0 | +0.0 | +0.00 | 5/2.84/0.62 | +0.00 | Pace-02参照 175未満 / P0(基準) |
| P1 | 抑揚 少し強め | 47.29 | 166.2 | 179.0 | 193.0 | -2.1 | -1.1 | +1.00 | 5/3.38/0.75 | +0.54 | Pace-02参照 175未満 / P0比±5%以内 |
| P2 | 抑揚 中程度 | 45.16 | 174.0 | 183.8 | 198.8 | +2.5 | +1.6 | -1.13 | 4/2.4/0.71 | -0.44 | Pace-02参照 175未満 / P0比±5%以内 |
| P3 | 明るさ・活力 少し | 44.32 | 177.3 | 190.0 | 196.5 | +4.4 | +5.0 | -1.97 | 5/2.95/0.76 | +0.11 | Pace-02参照 175-185 / P0比±5%以内 |
| P4 | 明るさ・活力 中程度 | 46.0 | 170.9 | 181.9 | 199.1 | +0.6 | +0.6 | -0.29 | 4/2.79/0.82 | -0.05 | Pace-02参照 175未満 / P0比±5%以内 |
| P5 | 明瞭さ重点 | 44.56 | 176.4 | 191.8 | 203.6 | +3.9 | +6.0 | -1.73 | 6/3.59/0.69 | +0.75 | Pace-02参照 175-185 / P0比±5%以内 |
| P6 | 抑揚+明瞭 | 47.11 | 166.8 | 181.9 | 196.5 | -1.8 | +0.6 | +0.82 | 6/3.89/0.83 | +1.05 | Pace-02参照 175未満 / P0比±5%以内 |
| P7 | 明るさ+明瞭 | 48.59 | 161.8 | 174.2 | 189.0 | -4.7 | -3.7 | +2.30 | 6/3.48/0.83 | +0.64 | Pace-02参照 175未満 / P0比±5%以内 |
| P8 | 抑揚+明るさ+明瞭 バランス型 | 44.79 | 175.5 | 184.3 | 206.9 | +3.4 | +1.9 | -1.50 | 4/2.15/0.58 | -0.69 | Pace-02参照 175-185 / P0比±5%以内 |

| ID | Primary ASR | 試行数 | peak dBFS | headroom dB | clip(>=0.999)数 | RMS dBFS | local whisper(medium)差分 |
|---|---|---|---|---|---|---|---|
| P0 | NORMALIZED_MATCH(verified) | 1 | -1.55 | 1.55 | 0 | -19.78 | {"ratio": 0.9621, "ref_n": 131, "asr_n": 133, "diffs": [{"op": "replace", "ref": "want to", "asr": "wanna"}, {"op": "replace", "ref": "8.7%", "asr": "8 7 %"}, {"op": "replace", "ref": "us", "asr": "u  |
| P1 | NUMERIC_EQUIVALENCE_MATCH(verified) | 1 | -1.46 | 1.46 | 0 | -19.8 | {"ratio": 0.9848, "ref_n": 131, "asr_n": 133, "diffs": [{"op": "replace", "ref": "8.7%", "asr": "8 7 %"}]} |
| P2 | NORMALIZED_MATCH(verified) | 2 | -1.43 | 1.43 | 0 | -19.98 | {"ratio": 0.9697, "ref_n": 131, "asr_n": 133, "diffs": [{"op": "replace", "ref": "8.7%", "asr": "8 7 %"}, {"op": "replace", "ref": "us", "asr": "u s"}, {"op": "delete", "ref": "sale", "asr": ""}]} |
| P3 | NORMALIZED_MATCH(verified) | 1 | -0.93 | 0.93 | 0 | -18.43 | {"ratio": 0.9848, "ref_n": 131, "asr_n": 133, "diffs": [{"op": "replace", "ref": "8.7%", "asr": "8 7 %"}]} |
| P4 | NORMALIZED_MATCH(verified) | 1 | -1.73 | 1.73 | 0 | -20.7 | {"ratio": 0.9736, "ref_n": 131, "asr_n": 134, "diffs": [{"op": "replace", "ref": "8.7%", "asr": "8 7 %"}, {"op": "replace", "ref": "us", "asr": "u s"}]} |
| P5 | NORMALIZED_MATCH(verified) | 1 | -1.43 | 1.43 | 0 | -19.66 | {"ratio": 0.9736, "ref_n": 131, "asr_n": 134, "diffs": [{"op": "replace", "ref": "8.7%", "asr": "8 7 %"}, {"op": "replace", "ref": "us", "asr": "u s"}]} |
| P6 | NUMERIC_EQUIVALENCE_MATCH(verified) | 1 | -1.18 | 1.18 | 0 | -19.47 | {"ratio": 0.9736, "ref_n": 131, "asr_n": 134, "diffs": [{"op": "replace", "ref": "8.7%", "asr": "8 7 %"}, {"op": "replace", "ref": "us", "asr": "u s"}]} |
| P7 | NORMALIZED_MATCH(verified) | 1 | -1.55 | 1.55 | 0 | -19.31 | {"ratio": 0.9736, "ref_n": 131, "asr_n": 134, "diffs": [{"op": "replace", "ref": "8.7%", "asr": "8 7 %"}, {"op": "replace", "ref": "us", "asr": "u s"}]} |
| P8 | NORMALIZED_MATCH(verified) | 1 | -1.65 | 1.65 | 0 | -20.24 | {"ratio": 0.9582, "ref_n": 131, "asr_n": 132, "diffs": [{"op": "replace", "ref": "want to", "asr": "wanna"}, {"op": "replace", "ref": "8.7%", "asr": "8 7 %"}, {"op": "delete", "ref": "in", "asr": ""}, |