# FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01 委任_01A (2026-10-11)

範囲: 共通Intro A/B・E Advanced Preview・F Full Story(Aoede) 各5仕様のPrompt設計・生成・比較ページ。Trial限定、Production不変。

## 試聴URL
https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/intro_preview_fullstory/index.html

## 使用モデル/Voice/backend(実測)
- model_id実測: `gemini-3.8-flash-lite-tts`(全22 call、response.model_version)。最新世代TTS(現行Production同一、条件固定)
- backend: `generate_content` + `Part.speech_metadata.style`(speech_metadata_flash_lite相当、Standard同期)。Voice: A/B/E=Charon、F=Aoede
- Trial専用script: `er057_tone_trial_tts_gen_01.py`(生成)、`er057_tone_trial_assemble_01.py`(連結/mp3/6%減速)、`er057_tone_trial_page_01.py`(ページ)

## 仕様(詳細Prompt全文: er057_output/coffee_final_listening_tone_trial_01/part_AEF/prompts/prompts_{A,B,E,F}.md)
- A/B共通(Baseline shell style=`natural, clear, conversational`): 1=落ち着いたMC、2=自然な会話、3=明瞭な案内、4=リズム重視、5=文末処理重視(速度数値のみ変更は無し、全てstyle記述の観点違い)
- E(Baseline=E2_UPBEAT): 1=落ち着いたニュースキャスター、2=少しゆったりした自然会話、3=意味のまとまり重視、4=低めで落ち着いたVoice、5=文末の収まり重視
- F(Baseline=F1.5、全候補はF1.5を逐語保持し末尾に1文追加): 1=発話テンポ、2=意味のまとまり、3=自然な間、4=文末の収まり、5=Storytellingリズム。各候補に既存6%減速版(Production既存`er008_a2_postprocess_slowdown_01.apply_a2_slowdown`、FFmpeg atempo=1/1.06)。Standard専用Styleは新設せず
- 参考baseline追加: F0(現行F1.5で同一原稿再生成)、F0S(現行Standard方式再現=F1.5+減速指示+6%減速)。既存音声(Master Store shell/既存run dirのb1b preview・part1)も併載

## 費用
概算¥8.32(上限¥16.63、call数22、`COST_ESTIMATE_01A.md`)/実費¥5.16(22 call成功・retry 0、input 839/output 5308 tok、単価$0.5/$6.0 per 1M、USD/JPY160、`cost_actual_01A.json`)。

## Baseline由来(read-only、sha256先頭12桁)
Welcome 4c0d69cf7f6c(Master Store再利用 aa130472d437ac80b7cdd474) / Preview intro 69beef4047c1(b81f7fe5eb7a223fdeba29c9) / Topic intro 44922c8ccc5f / JA title 6e2d14e2b51b / Advanced Preview(E0) ca8a4697c344 / Advanced Part1(F既存) c53858531bf1 / Standard Part1 406c91ebaa01。元: eigo-radio-tone worktree `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_e_tone_01/`。Intro/通知音: `C:/Users/tensh/sound/`(既存)。

## 検証
- Playwright(公開Pages): 39 audio全てOK、combo通し再生OK、HTTP異常0、console error0、file:///・C:\混入なし(`PLAY_EVIDENCE_01A.md`)。
- Production不変: Master Store manifest/reuse_telemetry/human_review_queue/attempt_history/各telemetry/ledgerのsha256が作業前後で一致(`production_sha_before.txt`/`production_sha_after_check.txt`、全件OK)。
- 内容ASR検証は不要指示のため未実施(local whisper未導入)。聴感のみで評価要。

## 観測・注意(所見のみ、候補選定はしていない)
- 生成durationはBaseline比で一様に遅くはならない: A0 1.89s→A1〜A5 1.76〜3.28s、B0 1.24s→1.48〜2.12s、E0 11.97s→11.16〜13.76s、F0 17.92s→17.32〜19.60s。「遅い」とは限らず(A2/B2/E3/F3/F4は同等〜やや速い)、要試聴。
- 原稿差異: A/Bは現行shellの正確な文言を使用(`Welcome to English Your Way.`/`Here's a quick preview.`。依頼文の`Welcome to English your way`/`Here's the quick preview`は現行と異なるため現行を採用)。
- F既存音声(Advanced/Standard Part1)は冒頭段落以降(ICO/USDA等)も続く全文で、候補は冒頭段落のみ。Standard Part1は別原稿(易化版)。公平比較用にF0/F0Sを同一原稿で再生成した。
- 6%減速は実測5.94%(atempo整数丸め由来、Production処理と同一)。F候補はStandard専用減速指示を付けず6%機械減速のみ(F0Sのみ現行再現として指示付き)。
- gitignore: `ACTIVE_TASK_*.md`と`*.wav`はgitignore対象のため、raw wavと別ファイルACTIVE_TASKはcommitしていない(raw wavのsha256は`cost_actual_01A.json`)。

## Status案
VALIDATED(Trial資料として試聴可能な状態に到達、ユーザー試聴判断待ち)。Production採用なし。候補の優劣判断・採用はユーザー。
