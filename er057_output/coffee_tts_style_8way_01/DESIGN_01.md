# DESIGN_01 (FAMILY-X-COFFEE-TTS-STYLE-8WAY-AB-TRIAL-01 委任_01、2026-10-13、設計・見積のみ。TTS/LLM/ASR呼出なし、費用JPY0、Production変更なし)

Status: 設計提出(生成はFable確認後の委任_02)。到達可能Status=VALIDATED/REJECTED/UDR。Trial結果はProduction仕様ではない。使用モデル: TTS=gemini-3.8-flash-lite-tts(Production同一)、ASR=既存Primary(gpt-4o-mini-transcribe)。

## 1. 代表箇所(両レベルともPart1)
出典: `er057_output/coffee_v5_pause_01/tts_input_texts.json`(tts_input)、`coffee_final_v5/wpm_v5_01.json`、`coffee_v5_pause_01/sentence_end_pause_stats.json`(-40dBFS、最小50ms、各Partの最終文除く)。
| 項目 | Std Part1 (std_part1) | Adv Part1 (adv_part1) |
|---|---|---|
| 原稿文字数/語数 | 657字 / 117語 | 731字 / 131語 |
| 文数/各文語数 | 13文: 4,9,9,9,19,10,7,12,8,13,8,5,4 | 9文: 4,8,14,12,24,15,23,17,14 |
| v5音声(sha12) | slow6 6546b00f7805(raw 8f8ede12a4b6) | 8b616edca69c |
| 尺 / v5実測WPM | 48.24s / 145.5(6%減速後) | 47.08s / 166.9 |
| 文末無音(ms) 平均/中央/最大 | 694 / 630 / 1050(12箇所) | 456 / 460 / 740(7箇所) |
| 800ms以上の文末無音 | 4件(1000,820,910,1050。局所長無音) | 0件 |
| 文中小無音(>=50ms、文末以外) | 38本 / 3.83s(300ms以上1本) | 49本 / 6.21s(300ms以上6本) |
選定理由: Std Part1は⑤調査で局所長無音(820〜1050ms)を確認した箇所で、短文連続(文間の間)と19語の長文を含む。Adv Part1は最長Part(Part2=31語文)ではなくPart1を採用: Stdと同じ話題導入で比較しやすく、24/23語の長文2つ(文中の間・長い文)と短い導入文を含み、文中小無音が多い(49本)ため。Part2/3は使わない。**Stdは短文中心、Advは長文中心**で同じPromptでも効き方が異なる可能性がある(別原稿のため別生成)。全編は使わない。

## 2. A〜H候補(Prompt全文は `prompts_8way_01.json` に逐語+sha256)
共通: Voice Aoede、`Part(text=<tts_input>, speech_metadata=SpeechMetadata(style=<下記>))`、数値WPM・速度倍率はPromptに書かない。

| 候補 | 文字数 | sha256先頭 | unhurried | 設計意図 | 想定副作用 | 減速語と180 WPM目安の整合 |
|---|---|---|---|---|---|---|
| A 現行P8 Baseline(完全同一条件) | 402 | 3eadf4f6 | あり | 比較基準。P8逐語(sha 3eadf4f6)。 | v5実測どおり: 文中の小無音多め、Std Part1に局所長無音、take間リズム差大。 | unhurried 2回(減速語あり=現状)。 |
| B P8の最小修正(減速語のみ肯定形の流れ指定へ置換、他は逐語維持) | 441 | 90744852 | なし | 単一変数の検証: 『unhurried』が文中小無音(+55%)の原因かを、P8の他要素(声質・抑揚・明瞭さ)を保ったまま切り分ける。 | 文末の間は残る可能性。『flowing』で語尾が流れて明瞭さが落ちる懸念(明瞭さ文は維持)。 | unhurriedを削除し『easy, flowing pace』『flowing smoothly into the next』へ。減速語を使わず速度は自然に委ねる(180目安に近づく想定)。 |
| C 不要な間の削減を明示(この1候補のみ) | 249 | 7e60501e | なし | 唯一、不要な間の削減を直接指示。意味上の息継ぎは『meaning truly needs』で残す。 | 命令(Do not pause)の副作用: 息継ぎ不足、早口化、聞き疲れ、文末の語尾が詰まる。 | 減速語なし。速度語も書かず、間の削減のみで全体が速くなる可能性(180を超える懸念をWPMで確認)。 |
| D 最短Prompt(過剰制御の回避) | 88 | 450b317f | なし | 指示を最小化しモデル本来の自然な語りに任せる。過剰制御による不自然な間・抑揚を避ける。 | 明瞭さ・明るさの保証が弱い。take間差が大きい可能性。 | 減速語なし。chatting naturallyで会話速度。 |
| E テンポ・文間のつながりを肯定形で指定(F5系の友人への語り+lively rhythm) | 255 | d07944c9 | なし | 文と文を一続きの考えとして繋げる肯定形のテンポ指示。F5の『lively natural rhythm』を継承。 | 友人調で口語化し、ニュース報道の信頼感が落ちる可能性(credible news narrationで補強)。 | not hurriedを含めず『lively, natural rhythm』で速度を暗示。減速語なし。 |
| F 明るさ・抑揚を少し強める(演技過剰は避ける) | 228 | e08eeaa6 | なし | 明るさ・抑揚の底上げ(目標2・4)。語尾を落ち着かせて抑揚の起伏で文の終わりを作る。 | 演技過剰・大げさ、数字強調で不自然な上昇調。間への直接効果は限定的。 | 速度語なし。『settle gently』は語尾の抑揚指示で、減速語ではない。 |
| G 明瞭さと自然な会話速度の両立(Podcastホスト像) | 243 | 3255b56e | なし | 明瞭さ(目標3)と自然速度(目標5)の両立。PD4系Podcast像+P8の明瞭さ文を要約。 | 平板化・熱量不足、明るさがP8より下がる懸念。 | 減速語なし。『natural conversational pace』『smooth, steady rhythm』で180目安に整合。 |
| H PD1系(報道キャスター調、実測最速)+PD8の温かさの組合せ | 252 | 49af7437 | なし | PD1(報道キャスター調、実測WPM最速186.8)の落ち着いた信頼感+PD8系の smile を統合。意味単位でまとめ文中の細かい止まりを減らす。 | 硬い・淡々とした印象で明るさ不足、抑揚が控えめ。 | 減速語なし。『breathe naturally between ideas』で息継ぎを意味の切れ目に限定。 |

### Prompt全文

**A**(現行P8 Baseline(完全同一条件))
```
Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, richly expressive, with full vowels and gentle emphasis, never flat or sleepy. Let the pitch rise and fall a little more on key words. Add a touch more brightness and a hint of a smile in the voice, while staying unhurried. Articulate crisply: distinct consonants, clean word endings, every syllable clearly heard.
```

**B**(P8の最小修正(減速語のみ肯定形の流れ指定へ置換、他は逐語維持))
```
Warm, bright, cozy storytelling in the manner of a well-loved radio feature: at an easy, flowing pace, richly expressive, with full vowels and gentle emphasis, never flat or sleepy. Let the pitch rise and fall a little more on key words. Add a touch more brightness and a hint of a smile in the voice, with each phrase flowing smoothly into the next. Articulate crisply: distinct consonants, clean word endings, every syllable clearly heard.
```

**C**(不要な間の削減を明示(この1候補のみ))
```
Warm, bright storytelling with a friendly smile in the voice. Do not pause after every sentence: take a breath only where the meaning truly needs one, and let one sentence lead straight into the next. Keep consonants distinct and word endings clean.
```

**D**(最短Prompt(過剰制御の回避))
```
Warm, bright and clear, like a friendly radio host chatting naturally with one listener.
```

**E**(テンポ・文間のつながりを肯定形で指定(F5系の友人への語り+lively rhythm))
```
Tell this like a short story to a friend: a lively, natural rhythm in which every sentence picks up right where the last one left off, so the whole passage sounds like one continuous thought. Warm, friendly and upbeat, with clear, credible news narration.
```

**F**(明るさ・抑揚を少し強める(演技過剰は避ける))
```
Bright, warm and smiling, with lively, melodic intonation: let the pitch lift on key words and numbers and settle gently at the end of each idea. Expressive but natural, never theatrical. Crisp consonants and clean word endings.
```

**G**(明瞭さと自然な会話速度の両立(Podcastホスト像))
```
An engaging podcast host explaining an interesting news story to a curious listener at a natural conversational pace: every word easy to catch, with a smooth, steady rhythm and a warm, friendly tone. Consonants distinct, word endings complete.
```

**H**(PD1系(報道キャスター調、実測最速)+PD8の温かさの組合せ)
```
A warm, composed daytime radio news presenter telling a human-interest story: clear, credible and approachable, with a smile in the voice. Group words into meaningful phrases, keep the phrasing smooth and connected, and breathe naturally between ideas.
```

### 相互の差異(自己評価)
語集合Jaccard(0=無共通,1=同一)/文字列SequenceMatcher比を28組で計算(`prompts_8way_01.json` similarity_pairs)。上位:
| 組 | Jaccard | seq比 |
|---|---|---|
| A-B | 0.797 | 0.199 |
| B-F | 0.253 | 0.06 |
| B-C | 0.244 | 0.049 |
| A-F | 0.243 | 0.063 |
| A-C | 0.233 | 0.052 |
| E-G | 0.183 | 0.04 |
| D-G | 0.179 | 0.066 |
| D-E | 0.178 | 0.047 |

A-B(0.797)は**意図的な単一変数比較**(BはP8から減速語のみを肯定形へ置換、他は逐語)で、類似でも情報価値がある。A/B以外の全組はJaccard<=0.26で、役割(報道/Podcast/友人/radio feature)・長さ(88〜441字)・指示の種類(直接指示/肯定形テンポ/最短/抑揚/明瞭さ/局所息継ぎ)が異なる。8候補すべてに同じ「間を減らす」指示は付けず、直接指示するのはCのみ。減速語を残すのはA(現状)のみ。

役割分担: A=現状 / B=減速語の因果切り分け / C=直接指示 / D=最短 / E=肯定形つながり / F=明るさ抑揚 / G=明瞭さ+自然速度 / H=報道キャスター+温かさ(PD1由来)。目標1(間)に効く可能性: B,C,E,H。目標2/4: F,E。目標3: G,A,B,C。

### 既存Trial結果との対応(根拠)
- PD1(報道キャスター調)は pace_trial_02 で最速(186.8 WPM、PD8は183.2)→H。F5『lively, natural rhythm』『short story to a friend』→E。PD4/PD5のPodcast/余裕→G(減速語は除く)。
- ⑤調査: P8/PD8系は『unhurried』二重表現で文中小無音がF5比+55%、文末無音は有意差なし→Bで『unhurried』の寄与を単独検証。
- 注意: これらは単回比較の傾向。take間SD約190msのため、候補間差はTake1/Take2の一致で確認する。

## 3. 生成計画(委任_02、Fable確認後)
- 8候補x2 take x 2レベル=**32 call**。各callは該当Part1のtts_input(`B.jobs_def()`のstd_part1/adv_part1、`tts_safe_news_en`適用、v5と同shaを実行前にassert)。Take1/Take2は同一Promptの独立generate_content(複製・速度変更コピー禁止)。
- Std: 生成後に既存`apply_a2_slowdown`(6%)を適用、聴取用はslow6。Advは通常速度。trimは`trim_english_keyword_silence`(Production同一)。
- パラメータ: model gemini-3.8-flash-lite-tts、voice Aoede、speech_metadata方式、Standard同期、model_versionを全callで記録(Trial専用`B.make_tts_call`流用)。Master Store/manifest/telemetryへは書かない。
- 発音QA: 既存Primary ASR(`B.asr_and_judge`)1回のみ。NG・時間異常でも再生成せず警告記録(技術失敗=空応答/例外のみ1回retry)。Std slow6後のASR再実施はしない。
- 並列: 8 worker(pace_trial_02は6並列で24 call/66s)。32 callは4 wave程度→生成約1.5〜3分、ASR含め約5分。ローカルfaster-whisper small測定(32ファイル)約10〜15分(CPU)。全体約20分。直列化の必要なし(各callは独立、出力名衝突なし)。
- コード(委任_02で作成): `er057_coffee_tts_style_8way_01_gen.py`(`er057_pace_trial_02_gen.py`のrun関数流用、cascadeなし)、`_measure.py`(`er057_coffee_v5_pause_01_measure.py`のanalyze/silent_runs再利用)、`_page.py`。
- STOP/予算: 実行前に `docs/pm/delegation_log/*STOP_NOTICE*`・`<run>/STOP`・`STOP_ALL`確認。累計JPY60でハードストップ。再起動なし。

## 4. 費用見積(`cost_estimate_01.json`)
- 単価: `er005_output/cost_baseline_01/pricing_snapshot.json` gemini-3.8-flash-lite-tts Standard(入力$0.5/1M、出力$6.0/1M=25tok/s)、USD/JPY=160。ASRは`er057_tone_trial_final_build_03.py`の推定式(gpt-4o-mini-transcribe $1.25/$5)。
- 基準値: v4実績 Std Part1 入143/出1139tok(JPY1.105)、Adv Part1 入157/出1177tok(JPY1.1425)。ASR推定 Std 0.22/Adv 0.24。
| 見込み | 合計 |
|---|---|
| 中央(32 call) | **JPY43.4** |
| 上限(出力tok+20%、入力+40tok) | JPY51.2 |
| 上限+技術failure retry 4 call | JPY57.6 |
| 相互確認: pace_trial_02実績 JPY1.402/call x32 | JPY44.9 |
- 上限JPY60に**収まる**(最悪57.6、余裕2.4)。余裕は小さいため累計JPY60でハードストップ。短縮案(必要時): Part1前半6文のみ(中央約JPY22)、またはStdのみ先行(16 call、約JPY22)。
- 請求画面未確認の推定。出力トークンは候補により尺が変わる。

## 5. 測定・試聴ページ設計
**測定(各take、Std=slow6後・Adv=生成後)**: 尺、語数、実測WPM(総語数/尺、500ms超無音除外の発話WPMも併記)、文末無音(平均/中央/最大/分布 [<150/150-300/300-500/500-800/800-1200/>=1200])、文中無音(>=50ms文末以外の本数/総時間/300ms以上本数)、長無音箇所(800ms以上の位置と直前語)、語尾欠落・破綻(ASR Primary classification+`detect_duration_anomaly`+difflib整列での末尾語欠落検査)、音量(RMS dBFS、peak)、Take1/Take2差(WPM差、文末無音平均差、文ごと文末無音SD)、v5既存音声との比較。手法は⑤と同じ(faster-whisper small、費用0)。機械指標は参考表示のみ(足切りしない。選抜はユーザー試聴)。
**試聴ページ `user_test/coffee_style_8way_01/index.html`**(委任_02で作成、スマホ簡素):
- 冒頭に『試聴順序: まずTake1でA〜Hを聴き比べて選ぶ → 気に入った候補のTake2を確認(再現性)』を記載。
- A〜Hを縦に一覧。各カード: 見出し(記号+一言ラベル)、Std再生とAdv再生(`<audio controls>`、主表示=Take1)。Take2は`<details>`で折りたたみ(副表示)。
- 各音声の下にWPM・文末無音平均/最大・文中無音本数・警告を1〜2行で併記。Prompt全文は`<details>`で表示(sha先頭付き)。Aは『現行v5と同条件』と明記。
- 音声は`user_test/coffee_style_8way_01/audio/`の相対パス(Std=slow6)。生成後に既存play_verify方式で全audio要素の再生確認。

## 6. 要判断事項(Fable)
1. 代表箇所Part1/Part1の採否。2. C(直接指示)・H(報道キャスター)を含む8候補構成の採否。3. Std slow6後ASR省略の可否。4. Aは既存v5音声を再利用せず新規2 take生成(同一条件のtake差を測るため32 callに含む)。