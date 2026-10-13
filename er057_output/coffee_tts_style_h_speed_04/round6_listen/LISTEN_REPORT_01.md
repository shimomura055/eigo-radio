# LISTEN_REPORT_01 (FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-04 委任_03、2026-10-13)
暫定成果物。採用判断なし(Trial、VALIDATED上限)。ユーザー判断選択肢(i)「Std/Adv別Prompt」の試聴素材。追加探索ではない。

## 1. 3 take結果(測定条件はRound1-5と同一、合格基準はRound5同一)
基準: Std実測157+-6 / Adv実測167+-6 / 文末平均 Std<=498ms・Adv<=593ms / 800ms+長無音<=1本 / ASR・tail・long_gap異音OK。
| Prompt | Take | WPM(Std実測 / raw換算 / Adv実測) | 文末平均ms | 800ms+長無音 | ASR | 判定 |
|---|---|---|---|---|---|---|
| K06 Std | 1(既存) | 154.5 / 164.4 | 478 | 0 | NORMALIZED_MATCH | 暫定合格 |
| K06 Std | 2(既存) | 156.0 / 166.0 | 486 | 0 | NORMALIZED_MATCH | 暫定合格 |
| K06 Std | 3(新規) | 154.2 / 164.0 | 572 | 2(810,870ms) | NORMALIZED_MATCH | 速度のみOK(ポーズ不良) |
| K01 Adv | 1(既存) | 172.6 | 580 | 1 | NORMALIZED_MATCH | 暫定合格 |
| K01 Adv | 2(既存) | 170.3 | 466 | 1 | NORMALIZED_MATCH | 暫定合格 |
| K01 Adv | 3(新規) | 166.2 | 626 | 1(850ms) | TRUE_CONTENT_MISMATCH(his挿入) | 不合格(ASR) |
- K06 Std: 3take中2合格。WPM範囲154.2-156.0(幅1.8)、文末平均範囲478-572ms(幅94ms)。
- K01 Adv: 3take中2合格。WPM範囲166.2-172.6(幅6.4)、文末平均範囲466-626ms(幅160ms)。
- 比較: H0 Take1 Std 157.3/498ms/長無音1、Adv 166.9/593ms/0。現行v5 Part1 Std 145.5/694ms/4、Adv 166.9/456ms/0。
- ピッチ幅・強弱幅・異音は `measurements_r6.json`。いずれのtakeも異音はlow信頼度のみ(K01 Take3のlong_gap lowはASR不一致と併せ不合格扱い)。
- 長無音は全て文境界(continue./delay./away. の直後)で、Round4-5の話題転換位置の知見と整合(位置分類は目視、厳密検証なし)。

## 2. 試聴ページ
https://shimomura055.github.io/eigo-radio/user_test/coffee_style_h_speed_04/index.html
掲載: K06 Std T1-3、K01 Adv T1-3、H0 T1 Std/Adv、現行v5 Part1 Std/Adv、現行v5 Full Story Std/Adv(既存 `user_test/coffee_final_v5/audio/` を相対参照、再生成なし)。各音声にWPM・文末平均・長無音・ASR・3take合格数、Prompt全文を表示。冒頭に暫定成果物の注記あり。
音声変換: 新規6本はwav->mp3(lameenc 96kbps mono、既存02ページと同方式、`*.wav`はgitignore)。元wav shaは `audio_conversion_r6.json`。H0 T1/v5 Part1は `user_test/coffee_style_h_speed_02/audio/` からバイト単位コピー(既存ページ・既存音声は未変更)。

## 3. Playwright実再生evidence
`play_evidence_r6.json`: HTTP 200、audio 12本全て再生成功(plays_ok=12、失敗0)、mp3 HTTP全200、console error 0、HTTP>=400 0、file://混入なし、注記バナー表示あり、Prompt全文ブロック3。再生はmuted headless chromiumでのcurrentTime進行で確認(聴感確認は人間)。

## 4. 配線の事実(Step C、変更なし)
`er057_tone_trial_final_build_03.py` の `make_tts_call()` が返す `call(text, style, voice)`(92-93行、`speech_metadata=SpeechMetadata(style=style)`)は style を呼出ごとの引数として受け取るため、呼出単位でレベル別styleを渡すこと自体は既に可能(本Round 1-6のgen4/5/6はこの形でPromptを候補別に渡している)。一方、Full Story build(`cmd_gen` 208行付近)は `style = load_f5_style()` で単一F5 styleを取得し `run_job(j, call, style)`(217行付近)に全jobへ共通で渡しているため、そのままではレベル別に分けられず、`jobs_def()` の `level`(std/adv)でstyleを切り替える小改修(208・217・run_job内138行付近、数行規模の見込み)が必要。Production経路は別で、今回は未確認・未変更。実装は行っていない。

## 5. 費用・モデル
2call(技術retry 0)、TTS 2.19 + ASR推定0.46 = JPY2.65(上限6/ハードストップ8内)。累計JPY106.32/300(本委任枠の累計上限112内)。モデル gemini-3.8-flash-lite-tts(要求=応答記録、Round1-5と同一・評価用の最新)、voice Aoede。価格定数: `er057_tone_trial_final_build_03.py` の PRICE_IN=0.5/PRICE_OUT=6.0 USD/1M tok x 160円(新規出典確認なし=未確認)。ASRは推定。
Production state sha前後一致(`state_guard_r6.json` all_unchanged=True)。STOP/STOP_ALL不在確認済(Melos STOP_NOTICEは別ID)。

## 6. 注意
- 3take再現性は両Promptとも2/3。K06 Std Take3は文末+94ms・長無音2本、K01 Adv Take3はhis挿入のASR不一致(Round5のN04と同種)。
- 採用判断・Production反映は行っていない。レベル別Promptを実運用する場合の再現性(2/3)と配線改修は別判断。
