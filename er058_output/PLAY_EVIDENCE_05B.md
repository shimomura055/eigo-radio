# PLAY_EVIDENCE_05B: 未確定音声の試聴ページ Playwright実再生evidence(委任_05B、2026-10-12、費用0円)

ページ: https://shimomura055.github.io/eigo-radio/user_test/asr_misread_listen_01/index.html
生成: `er058_05b_listen_page_01.py`(ローカル処理のみ、API呼出なし、Production書込なし)。実再生確認: `er058_05b_play_evidence_01.py`、結果 `er058_output/PLAY_EVIDENCE_05B.json`(各音声の再生位置・長さ・HTTP状態)。行と音声の対応: `er058_output/trial_abc/listen_items_05B.json`。
commit: 58fbb370(静的ファイルのみ、`user_test/asr_misread_listen_01/`)。

## 結果(GitHub Pages上の実機確認、Chromium/Playwright)
| 項目 | 結果 |
|---|---|
| index.html HTTP | 200 |
| 音声要素 / 行数 | 40 / 40(Trial B未確定14+ja_voi5 1+needs_listen 5+Coffee 2+Trial C合意誤読11+曖昧7) |
| 全音声URLのHTTP | 40/40 が 200(自前mp3 35本+既存公開mp3再利用5本=`../open258_phase0_listen_01/`) |
| 実再生(muted、再生位置>=0.4秒まで進行) | **40/40 OK** |
| 各行の「原稿・Voice・ASR転写+判定の表・3択ラジオ」 | 40/40 |
| 音声要素の最小幅 | 360px |
| `file:///`・`C:\`の混入 | なし |
| 「結果をテキスト化」ボタン | 動作(1行目 `en_inf1_mis: 不明` を確認) |

## Gate 7 補足チェックリスト(a)〜(n)
| 項目 | 判定 | 備考 |
|---|---|---|
| (a)完成episode | N/A | 部品clip・1segmentの判断用ページ(明記済み) |
| (b)Preview (c)Comment全件 (d)本文全section (e)Key Phrase英日gloss (f)Intro/Outro/SFX | N/A | 同上。固定文言・SFXは含まない(ページ冒頭に明記) |
| (g)segment order・click-seek | N/A | 個別mp3(各行にplayer)。Coffee 2点は1segment全体(約50秒)で、該当語の位置目安を各行に記載 |
| (h)各segmentのvoice名 | OK | 各行に`Voice: Aoede/Charon` |
| (i)A2/B1等の分離 | N/A | レベル別ではなく型別・Trial別にセクション分け |
| (j)テキスト未取得の明記 | OK | Coffee 2点は原稿全文が保存attemptに無いため、該当文のみASR転写から引用し「推測補完なし」と明記 |
| (k)TTS方式 | OK | ページ冒頭に明記(Trial B=Standard同期・Flash-Lite speech_metadata。他は各Production生成時の方式) |
| (l)再生ボタンと原稿を同一行 | OK | 各行にaudio+原稿+意図した誤読(Trial B)+ASR転写表+3択 |
| (m)ユーザー環境から開けるリンク | OK | GitHub Pages(200)。`file:///`なし |
| (n)Key Phrase 2列表示 | N/A | Key Phraseリスト表示なし(ラベル文字列`English:`/`日本語:`は表示していない) |

## 注意
- Blindにしていない(原稿・意図した誤読・各ASR判定を併記)。聞いた後の判断(正しく読んだ/誤読/不明)をユーザーが返信に貼る方式(サーバー送信なし)。
- Trial Cの「合意誤読」「曖昧」ラベルは3系統ASRの合意による代理ラベルで、ground truthではない。試聴結果で代理ラベルの妥当性を確認する。
- ページ・mp3はTrial限定の静的ファイルで、Production(量産経路)には接続していない。
