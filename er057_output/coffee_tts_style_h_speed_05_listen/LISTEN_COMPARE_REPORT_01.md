# LISTEN_COMPARE_REPORT_01(FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-LISTEN-COMPARE-01 委任_01)

日付: 2026-10-13。Status: VALIDATED(Trial到達上限)/USER_DECISION_REQUIRED継続。採用判断なし。費用: 有料API呼出ゼロ、JPY0(TTS・ASRとも未実行)。使用モデル: 新規呼出なし(既存音声はgemini-3.8-flash-lite-tts/Aoede)。

## 1. 成果物とURL
- ページ: https://shimomura055.github.io/eigo-radio/user_test/coffee_style_h_speed_05/index.html
- 構成: (A)Standard聞き比べ / (B)Advanced聞き比べ / (C)Prompt一覧(英語原文+日本語要約+設計軸)。各行に再生ボタン・WPM・文末平均・長無音件数・ASR・合否・不合格理由。セクション単位の連続再生ボタンあり。K06/K01は除外(ユーザー試聴NG)。
- 生成スクリプト: er057_coffee_tts_style_h_speed_05_page.py、検証: er057_coffee_tts_style_h_speed_05_play_verify.py

## 2. 音声の利用元(全14本、新規生成なし)
Std 5候補は測定に使った6%減速後wav(`*_slow6.wav`)をそのまま使用。ページ生成時にwav sha256が各measurementsの`final_sha256`と一致することをassertで確認(全一致)。減速の再適用は不要だった。Adv 5候補はraw wav(`raw_sha256`と一致を確認)。H0/v5は`user_test/coffee_style_h_speed_04/audio/`のmp3を複製。mp3は元wavからlameenc 96kbps mono(04ページと同方式)。詳細は`audio_conversion_01.json`。

| mp3 | 元wav(利用元) | 元wav sha256(先頭12) | 測定値転記元 |
|---|---|---|---|
| N01_std_t1.mp3 | er057_output/coffee_tts_style_h_speed_04/round5/attempts/N01_std_part1_t1_slow6.wav | e2c84ba443b8 | er057_output/coffee_tts_style_h_speed_04/round5/measurements_r5.json |
| N01_adv_t1.mp3 | er057_output/coffee_tts_style_h_speed_04/round5/attempts/N01_adv_part1_t1_raw.wav | 91e7dcbb2b47 | er057_output/coffee_tts_style_h_speed_04/round5/measurements_r5.json |
| N02_std_t1.mp3 | er057_output/coffee_tts_style_h_speed_04/round5/attempts/N02_std_part1_t1_slow6.wav | 9edf54aabec9 | er057_output/coffee_tts_style_h_speed_04/round5/measurements_r5.json |
| N02_adv_t1.mp3 | er057_output/coffee_tts_style_h_speed_04/round5/attempts/N02_adv_part1_t1_raw.wav | 6bf611c2ed6d | er057_output/coffee_tts_style_h_speed_04/round5/measurements_r5.json |
| L02_std_t1.mp3 | er057_output/coffee_tts_style_h_speed_03/round3/attempts/L02_std_part1_t1_slow6.wav | a9864385d770 | er057_output/coffee_tts_style_h_speed_03/round3/measurements_r3.json |
| L02_adv_t1.mp3 | er057_output/coffee_tts_style_h_speed_03/round3/attempts/L02_adv_part1_t1_raw.wav | b95ecb0786d2 | er057_output/coffee_tts_style_h_speed_03/round3/measurements_r3.json |
| J13_std_t1.mp3 | er057_output/coffee_tts_style_h_speed_03/round1/attempts/J13_std_part1_t1_slow6.wav | a8a244f9ebd0 | er057_output/coffee_tts_style_h_speed_03/round1/measurements_r1.json |
| J13_adv_t1.mp3 | er057_output/coffee_tts_style_h_speed_03/round1/attempts/J13_adv_part1_t1_raw.wav | dcc5076cf7ef | er057_output/coffee_tts_style_h_speed_03/round1/measurements_r1.json |
| J07_std_t1.mp3 | er057_output/coffee_tts_style_h_speed_03/round1/attempts/J07_std_part1_t1_slow6.wav | 3eae08f3f70b | er057_output/coffee_tts_style_h_speed_03/round1/measurements_r1.json |
| J07_adv_t1.mp3 | er057_output/coffee_tts_style_h_speed_03/round1/attempts/J07_adv_part1_t1_raw.wav | 2e5270a742a6 | er057_output/coffee_tts_style_h_speed_03/round1/measurements_r1.json |
| H0_std_t1.mp3 | (既存mp3複製) user_test/coffee_style_h_speed_04/audio/H0_std_t1.mp3 | mp3 e7ae35057377 | er057_output/coffee_tts_style_h_speed_04/round5/measurements_r5.json (H0_t1/v5) |
| v5_std.mp3 | (既存mp3複製) user_test/coffee_style_h_speed_04/audio/v5_std.mp3 | mp3 22988b3621b7 | er057_output/coffee_tts_style_h_speed_04/round5/measurements_r5.json (H0_t1/v5) |
| H0_adv_t1.mp3 | (既存mp3複製) user_test/coffee_style_h_speed_04/audio/H0_adv_t1.mp3 | mp3 6bb806794daa | er057_output/coffee_tts_style_h_speed_04/round5/measurements_r5.json (H0_t1/v5) |
| v5_adv.mp3 | (既存mp3複製) user_test/coffee_style_h_speed_04/audio/v5_adv.mp3 | mp3 164f662c1456 | er057_output/coffee_tts_style_h_speed_04/round5/measurements_r5.json (H0_t1/v5) |

不足音声: なし。

## 3. 合否(各Roundの`classification_r*.json`と再計算の一致をassertで確認)
基準(暫定): Std実測151-163WPM・文末平均498ms以下・800ms以上の長無音1本以下・ASR/異音OK。Adv実測161-173WPM・文末平均593ms以下・同上。

| レベル | 対象 | 判定 | 理由 |
|---|---|---|---|
| std | N01 | 合格(暫定/数値基準内) | - |
| std | N02 | 不合格/基準外 | 文末平均無音が基準超過(514ms > 498ms) |
| std | L02 | 不合格/基準外 | 文末平均無音が基準超過(563ms > 498ms) |
| std | J13 | 合格(暫定/数値基準内) | - |
| std | J07 | 不合格/基準外 | 速度が基準外(実測168.3WPM、基準151-163。速すぎ); ASR不一致(TRUE_CONTENT_MISMATCH) |
| std | H0 Take1(前回高評価Prompt) | 合格(暫定/数値基準内) | - |
| std | 現行v5 Part1 | 不合格/基準外 | 速度が基準外(実測145.5WPM、基準151-163。遅すぎ); 文末平均無音が基準超過(694ms > 498ms); 800ms以上の長無音が4本(基準は1本以下); 異音検知medium以上1件 |
| adv | N01 | 不合格/基準外 | 文末平均無音が基準超過(627ms > 593ms) |
| adv | N02 | 不合格/基準外 | 文末平均無音が基準超過(600ms > 593ms) |
| adv | L02 | 合格(暫定/数値基準内) | - |
| adv | J13 | 不合格/基準外 | 速度が基準外(実測177.6WPM、基準161-173。速すぎ) |
| adv | J07 | 合格(暫定/数値基準内) | - |
| adv | H0 Take1(前回高評価Prompt) | 合格(暫定/数値基準内) | - |
| adv | 現行v5 Part1 | 合格(暫定/数値基準内) | - |

事実: Take1同士で、Std/Adv両方が機械基準を満たす候補は0(N01・J13はStdのみ合格、L02・J07はAdvのみ合格)。全て1take(Take1)の結果で、再現性(3take)は未検証の候補が多い(N01/N02はRound5でTake1のみ、他も同様)。機械指標とユーザー試聴の一致は保証されない(K06/K01が機械では暫定合格だがユーザー試聴NGだった事実あり)。

## 4. 再生確認(Playwright、公開URL)
`play_evidence_01.json`: HTTP200、audio要素14、mp3 HTTP 14/14=200、再生成功14/14(failed 0)、console error 0、HTTP>=400 0、file://混入なし、注記バナー(「暫定成果物。Trial(VALIDATED上限)。採用判断なし。ユーザー試聴用」)あり、prompt blocks 6、sections std/adv/prompts。連続再生ボタン: 1本目再生→終了後2本目へ自動遷移→停止ボタンで全停止を確認。ブラウザ: Playwright Chromium。

## 5. Git
commit 00a5eef1(ページ・mp3・生成script・audio_conversion/judgement json)をorigin/mainへpush済み。GitHub Pages反映は約6分後(初回404→200)。証跡・SSOT・委任ログは続くcommit。secret scan: hits=0(1回目staged 18件)。

## 6. SSOT更新要否(事実として判定)
- CURRENT_SPEC.md: 更新不要(Production仕様無変更)。
- DECISION_LOG.md: 1エントリ追記済み(K06 Std/K01 Adv NG、比較試聴ページ作成、採用判断なし)。
- OPEN_ITEMS.md(OPEN-332): 更新不要。
- docs/pm/USER_DECISION_REGISTER_01.md: #39追加、集計整合(判断済み11、合計39)。
- 注意: DECISION_LOG.mdには別タスク(FAMILY-Z-STANDARD-PREVIEW-PROMPT-TRIAL-01)の未commit追記が混在していたため、本タスク分のhunkのみstageした。

## 7. 未解決事項
- 不足音声なし。5候補は全てTake1のみ(3take再現性は候補により未検証)。
- 候補選定はユーザー試聴待ち(USER_DECISION_REQUIRED継続、#29)。
