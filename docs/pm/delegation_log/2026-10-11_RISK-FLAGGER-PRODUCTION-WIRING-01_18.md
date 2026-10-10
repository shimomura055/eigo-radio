# RISK-FLAGGER-PRODUCTION-WIRING-01 委任_18 (2026-10-11)

内容: L3 coffee_prices (run_l3_01) 完成音声を GitHub Pages 試聴ページ化。課金API 0、Production code/Prompt/SSOT 変更なし。
Status: 試聴URL提示可能(Gate 7 (a)-(n) 全○、Pages 7項目 PASS、E2Eチェッカー PASS、Play実再生 PASS)。PRODUCTION_WIRED 宣言はユーザー判断待ち(委任_17の状態を維持)。

## 生成方法(前例踏襲)
- 前例 user_test/family_x_refresh_e2e_01/index.html(Meta、手書き相当の集約表)と同構成の index.html を生成。前例は unified.html 未使用だったが、恒久チェッカーと(n)検証のため各 Level の player.html(既存 er019 player.html を Level 別に分割、file:/// と wav を相対 mp3 へ変換)を追加し unified.html URL も発行。
- 生成script: er053_output/risk_flagger_production_wiring_01/l3_run_01/build_pages_01.py(Pages検証: pages_verify_01.py)
- wav->mp3: er014 build_web_player_common.wav_to_mp3 と同一手順(soundfile 0.14.0 / libsndfile 1.2.2、format=MP3、既定bitrate)。episode と player 参照の segment 全件(a2 21、b1b 20 mp3)。wav は commit しない。
- 配置: user_test/coffee_prices_l3_01/{index.html,a2/player.html,a2/web/**,b1b/player.html,b1b/web/**}

## 表示上の調整(音声・Production code 変更なし)
1. Advanced の Key Phrases 表示: 既存 player は "EN: / EXPLANATION: / EN (repeat…)" でラベル付き。(n) 準拠のため player 表示テキストを "phrase / 英語解説" の2列(ラベル無し)に変換。Advanced は Production 仕様上 日本語gloss が無いため右列は英語解説(Variant B)。要ユーザー認識: (n) の「右列=日本語」は Advanced では英語解説。
2. Advanced Key Phrase 行の voice 表示を Charon → Aoede に修正(tts_generation_results.json の english/explanation voice=Aoede に合わせた。既存 player テンプレートの表示誤り)。

## 試聴URL
- index: https://shimomura055.github.io/eigo-radio/user_test/coffee_prices_l3_01/index.html
- Standard: https://shimomura055.github.io/eigo-radio/user_test/unified.html?src=user_test%2Fcoffee_prices_l3_01%2Fa2%2Fplayer.html&level=A2&en=Coffee%20Prices%20Fall%2C%20but%20Store%20Prices%20Stay%3A%20Coffee%E2%80%99s%20%E2%80%9CJet%20Lag%E2%80%9D&ja=%E7%9B%B8%E5%A0%B4%E3%81%AF%E4%B8%8B%E8%90%BD%E3%80%81%E5%80%A4%E6%9C%AD%E3%81%AF%E5%B1%85%E6%AE%8B%E3%82%8A%E3%80%82%E3%82%B3%E3%83%BC%E3%83%92%E3%83%BC%E4%BE%A1%E6%A0%BC%E3%81%AE%E3%80%8C%E6%99%82%E5%B7%AE%E3%81%BC%E3%81%91%E3%80%8D
- Advanced: https://shimomura055.github.io/eigo-radio/user_test/unified.html?src=user_test%2Fcoffee_prices_l3_01%2Fb1b%2Fplayer.html&level=B1&en=Market%20Prices%20Fall%2C%20Price%20Tags%20Stay%20Put%3A%20Coffee%20Prices%E2%80%99%20%E2%80%9CJet%20Lag%E2%80%9D&ja=%E7%9B%B8%E5%A0%B4%E3%81%AF%E4%B8%8B%E8%90%BD%E3%80%81%E5%80%A4%E6%9C%AD%E3%81%AF%E5%B1%85%E6%AE%8B%E3%82%8A%E3%80%82%E3%82%B3%E3%83%BC%E3%83%92%E3%83%BC%E4%BE%A1%E6%A0%BC%E3%81%AE%E3%80%8C%E6%99%82%E5%B7%AE%E3%81%BC%E3%81%91%E3%80%8D

## Gate 7 (a)-(n)(実HTML/実DOMに対する確認)
| 項目 | 結果 | 根拠 |
|---|---|---|
| (a) 完成episode音声 | ○ | 各 Level の完成 episode.mp3(Std 320.961s / Adv 303.0s)、実episode構造 |
| (b) Preview | ○ | unified に Preview カード(スクリプト表示)、index に preview segment 行 |
| (c) Comment全件 | ○ | unified の Comment 1-4 全件(Std/Adv)、index に comment_1-4 行 |
| (d) 本文全section | ○ | Full Script に part1-3 全文 + In One Line。Family X は Point 構造なし(仕様) |
| (e) KP 英語+日本語gloss | ○(注) | Std: 英語/日本語 5件。Adv: 英語/英語解説 5件(日本語glossなし、Production仕様)。index に Phrase・J3/explanation・style 全文 |
| (f) Intro/Outro/SFX/固定文言 | ○ | 固定shell 10件(Std)/9件(Adv)の master_audio_id を index に表示、timeline に「読み上げなし/共有固定」明記 |
| (g) segment順・開始秒・click-seek | ○ | player.html timeline の seek ボタン(data-sec)、Pages 上で seek60s 動作確認(currentTime>=60) |
| (h) voice名 | ○ | index の segment 表と player timeline に voice 表示(unified カードは voice 非表示=既存仕様) |
| (i) Level分離 | ○ | Standard/Advanced で別 player・別 mp3・別 URL |
| (j) 未取得segment明記 | ○ | 未取得なし(全segment status OK)。timeline の Intro 等は「読み上げなし」と明記 |
| (k) TTS方式 | ○ | index に tts_backend=speech_metadata_flash_lite、style_version、model 表示 |
| (l) 再生ボタンと script 同一行 | ○ | timeline 各行に seek ボタン+voice+script+個別audio(web/segments/*.mp3) |
| (m) 開けるリンク | ○ | GitHub Pages のみ。file:/// 0件(index/players grep 0、DOM dump 0) |
| (n) 表示フォーマット | ○ | KP 2列・ラベル無し(チェッカー PASS)、eyebrow は Standard/Advanced のみ |

## 検証
- Pages 7項目: pages_play_evidence_01.json(item1 全200、item2 DOM dump=pages_index_dom_dump_01.html、item3 "(existing" 0件、item4 Style全文(Std5種/Adv6種)欠落0、item5 audio存在、item6 mp3 200+decode(Std episode 320.961s、Adv 303.0s、segment 21+20 全decode OK)、item7 表示style/voice/model=metadata一致)
- 恒久チェッカー(Pages URL、.venv): pages_e2e_checker_01.json overall PASS(Standard/Advanced)
- Play実再生(Pages): unified Std currentTime 15.46s、Adv 15.63s(5秒待機後、paused=false、readyState=4、error=null)、index 側 4s 後 3.98s で PASS。証跡 pages_play_evidence_01.json
