# COST_ESTIMATE_01 (FAMILY-X-COFFEE-ADVANCED-FULLSTORY-PACE-TRIAL-01 委任_01, 2026-10-12)
結論: 8候補x3Part概算 約JPY 31.9 > 上限JPY 20 のため、実行せずSTOP(API呼出なし、費用0)。

根拠: Final v2 Advanced実績(generation_log_03.jsonl)の1 Partあたり実費。
| Part | TTS JPY | Primary ASR JPY | 計 |
|---|---|---|---|
| 1 (41.36s) | 1.0052 | 0.2289 | 1.234 |
| 2 (48.49s) | 1.1836 | 0.2826 | 1.466 |
| 3 (43.01s) | 1.0468 | 0.2390 | 1.286 |
| 1候補(3Part) | 3.236 | 0.750 | 3.986 |

- 8候補: TTS 25.9 + ASR 6.0 = 約31.9(技術失敗retry余地・遅い候補の長尺化は別)
- 8候補 TTSのみ(ASRをlocal whisperへ代替): 約25.9 でも超過
- 5候補: 約19.9(余裕ほぼなし) / 4候補: 約15.9 / 6候補ASR省略: 約19.4
