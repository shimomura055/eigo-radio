# RESULT_01: Full Story Tone Trial(FAMILY-X-TTS-FULL-STORY-TONE-TRIAL-01 委任_01)
Status: USER_DECISION_REQUIRED(ユーザー試聴待ち)。到達上限VALIDATED、Production採用未承認。
試聴URL: https://shimomura055.github.io/eigo-radio/user_test/tts_full_story_tone_01/index.html (Pages HTTP200 5/5、Playwright実再生4/4 OK: listen_play_evidence_01.json)

## 条件(全案共通)
model gemini-3.8-flash-lite-tts / backend speech_metadata_flash_lite / voice Aoede / 通常速度(6%減速なし) / 各案1回(call_count=1,retry0) / 原稿同一(正規化後87語) / 音量RMS正規化のみ(目標=F0)。詳細は CONDITIONS_01.md。
Style: F0=現行FULL_STORY定数(assert一致) / F1 / F1.5 / F2 はタスク指示どおり逐語(`full_story_tone_trial_01.py`・results_01.jsonl)。

## 比較
| ID | 長さ(s) | 生成(s) | raw RMS | gain | 正規化後peak | ASR | ASR語数/原稿語数 | 推定費用USD |
|---|---|---|---|---|---|---|---|---|
| F0 | 32.64 | 10.1 | 0.08143 | 1.0 | 0.6999 | NORMALIZED_MATCH | 87/87 | 0.004969 |
| F1 | 31.0 | 10.4 | 0.09023 | 0.9024 | 0.6316 | NORMALIZED_MATCH | 87/87 | 0.004723 |
| F1.5 | 30.05 | 9.2 | 0.10938 | 0.7445 | 0.5211 | NORMALIZED_MATCH | 87/87 | 0.004581 |
| F2 | 27.69 | 9.5 | 0.09863 | 0.8255 | 0.5778 | NORMALIZED_MATCH | 87/87 | 0.004227 |

推定総費用 USD 0.0185(約JPY3.0、Standard単価からの推定。上限JPY20内)。実測の請求値ではない。

## QA
ASR全案 NORMALIZED_MATCH、ASR語数=原稿語数(87)で欠落・重複・途中切れなし。長さはF0>F1>F1.5>F2(明るいほど短い=テンポ速め)。peakはgain後も0.95未満。ASRは「“Coffee prices are falling!”」の引用符・「News?」の扱いのみ句読点差(語は一致)。聴感(明るさ・自然さ)は未評価、ユーザー試聴待ち。
