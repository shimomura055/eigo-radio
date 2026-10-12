# REPORT_03 FAMILY-X-COFFEE-AOEDE-STYLE-TRIAL-03(2026-10-12、Status=VALIDATED、Trial限定、Production不採用)
試聴URL: https://shimomura055.github.io/eigo-radio/user_test/coffee_aoede_style_trial_03/index.html

## 共通サンプルと条件
- サンプル: Coffee v3 Advanced Full Story **Part1**(131語、PD8既存音声 `er057_output/pace_trial_02/attempts/PD8_adv_part1.wav` = P0、sha256 b20b1208c2f3bdeb76384528f1924cca25fb704891c14be3fe88924b77ffd910。v3 Advanced組立でそのまま使用した音声)。原稿は tts_input(tts_safe_news_en適用済み)を逐語使用。
- 選定理由: Pace Trial-02で比較に使った3 Partの一つで最も短く(46秒)費用が小さい。感嘆文・引用文(Haven't you heard the news?)・数字(8.7%)・固有名詞(International Coffee Organization、Brazil、US Department of Agriculture)・複数文を含み、抑揚・明瞭さ・語りの差が判断しやすい。
- 固定: Voice Aoede、model gemini-3.8-flash-lite-tts(speech_metadata、Standard同期、model_version実測も同一)、機械減速なし、Style以外同一。最新モデル原則: Production同一モデルの測定のため例外種別2(Production同一モデル)。ASR=gpt-4o-mini-transcribe(既存Primary)。
- 生成: P1〜P8各1回(P2のみ初回 ASR_VALIDATION_UNCERTAIN[ASRが fist を fists と聞き取り+US表記揺れ]のため同一Promptで再生成1回、2回目 NORMALIZED_MATCH を採用。上限2試行内)。P0は再利用(再生成なし)。
## Prompt差分(P0=PD8、166文字。全候補で P0 文を不変のまま末尾に句を追加、速度指示 unhurried 維持、lively等の速度誘発語は不使用。全文・sha256は prompts/prompts_aoede_style_03.md)
| ID | 追加句 |
|---|---|
| P1 抑揚少し | Let the pitch rise and fall a little more on key words. |
| P2 抑揚中程度 | Let the pitch rise and fall noticeably on key words and at the ends of phrases, with a clear, natural melodic contour. |
| P3 明るさ少し | Add a touch more brightness and a hint of a smile in the voice, while staying unhurried. |
| P4 明るさ中程度 | Bring a cheerful, sparkling warmth with a clearly audible smile in the voice, while staying unhurried. |
| P5 明瞭さ | Articulate crisply: distinct consonants, clean word endings, every syllable clearly heard. |
| P6 抑揚+明瞭 | P1句 + P5句 |
| P7 明るさ+明瞭 | P3句 + P5句 |
| P8 バランス | P1句 + P3句 + P5句 |
## 速度(全9本同一script `er057_aoede_style_trial_03_measure.py`、−40dBFS、無音500ms/300ms)
(`MEASUREMENTS_03.md`/`measurements.json` が正本。許容差は Pace Trial-02基準[目標約180、<=190、175-185優先]を参照した**暫定評価値**。P0比±5%も本Trialの暫定目安で、Production合格基準ではない)
| ID | 総秒 | 全体WPM | 発話WPM(500ms) | 発話WPM(300ms) | P0比 全体% | P0比 発話% | 文間無音(500ms)数/計s | 全無音量差s |
|---|---|---|---|---|---|---|---|---|
| P0 | 46.29 | 169.8 | 180.9 | 199.1 | 0 | 0 | 5/2.84 | 0 |
| P1 | 47.29 | 166.2 | 179.0 | 193.0 | -2.1 | -1.1 | 5/3.38 | +0.54 |
| P2 | 45.16 | 174.0 | 183.8 | 198.8 | +2.5 | +1.6 | 4/2.40 | -0.44 |
| P3 | 44.32 | 177.3 | 190.0 | 196.5 | +4.4 | +5.0 | 5/2.95 | +0.11 |
| P4 | 46.00 | 170.9 | 181.9 | 199.1 | +0.6 | +0.6 | 4/2.79 | -0.05 |
| P5 | 44.56 | 176.4 | 191.8 | 203.6 | +3.9 | +6.0 | 6/3.59 | +0.75 |
| P6 | 47.11 | 166.8 | 181.9 | 196.5 | -1.8 | +0.6 | 6/3.89 | +1.05 |
| P7 | 48.59 | 161.8 | 174.2 | 189.0 | -4.7 | -3.7 | 6/3.48 | +0.64 |
| P8 | 44.79 | 175.5 | 184.3 | 206.9 | +3.4 | +1.9 | 4/2.15 | -0.69 |
所見(機械指標のみ): 全体WPMは全候補P0比±5%以内(最大P7 -4.7%、P3 +4.4%)。ただし P5の発話WPMは+6.0%(500ms基準)と5%超で、明瞭さ重視Promptで発話自体が速くなった可能性。P7は最も遅い(-4.7%)。全体WPM 175〜185(Pace-02参照)に入るのはP3・P5・P8(P2は174.0で僅かに下)。P0自身がPart1では175未満(169.8)で、Part1は元々遅めの区間。
## ASR / Audio QA(全9本)
- Primary ASR(gpt-4o-mini-transcribe、既存evaluate_attempt): 全9本 verified(P0 NORMALIZED_MATCH、P1 NUMERIC_EQUIVALENCE_MATCH、P2 NORMALIZED_MATCH[2試行目]、P3/P4/P5/P7/P8 NORMALIZED_MATCH、P6 NUMERIC_EQUIVALENCE_MATCH)。
- peak -0.93〜-1.73 dBFS(全9本 headroom 0.93dB以上)、clip(|x|>=0.999) 全0件。最小headroomはP3(-0.93)。RMS -18.4〜-20.7 dBFS。duration anomalyなし(生成記録参照)。
- ローカルwhisper(medium)差分: 全候補 8.7%の表記(「8 7 %」)と us→u s(US表記)は共通で発音差ではなく表記揺れ。固有の差分: P0 want to→wanna(P0既知)、P2 'sale' 脱落、P8 want to→wanna+'in' 脱落。いずれもASR側の聞き落とし/縮約の可能性があり、実際の読み間違い・不自然な強調かは**聴感未確認**(Sonnetは聴けず、断定しない)。
## 費用
実費約JPY12.2(TTS 10.02+ASR推定2.14、9生成=8候補+P2再生成1回、model gemini-3.8-flash-lite-tts、請求画面未確認)/上限JPY40。
## 推薦(機械指標に基づく試聴優先順の提案のみ、最良Styleの決定ではない)
速度維持の観点で P0比 全体±2.5%以内かつ発話WPM±2%以内は P1・P2・P4・P6。抑揚〜明瞭さの複合を一度に比べやすいのは P8(バランス型、全体+3.4%、無音量-0.69s)。試聴優先: P8 → P2(抑揚中程度) → P4(明るさ中程度) → P6。P5は発話+6%に注意、P7は遅く(-4.7%)なる傾向。聴感は未評価で、最終判断はユーザー試聴。
## 未決事項
USER_DECISION_REQUIRED: ユーザー試聴評価(OPEN新規)。Production採用・Coffee v3差替・他Family横展開は未決定(APPROVED_FOR_PRODUCTION未取得)。Coffee v3完成音声/Production Prompt/Master Storeは不変。
