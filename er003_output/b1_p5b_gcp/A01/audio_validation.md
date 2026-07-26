# ER-003-B1-P5B-GCP 実行報告(Google Cloud TTS単独検証)

## 1. 検証目的

P4D/P5Aと完全に同一の全文ひらがな入力をGoogle Cloud TTS(ja-JP-Neural2-B)で
1回生成し、原稿忠実性(語句の省略・追加の有無)・「何が起きる」の読み・
全体の自然さを確認する。Azure Speechが不合格だった不自然さが、Azure固有の
問題か、全文ひらがな入力方式自体に起因するかを切り分ける材料とする。

## 2. ADC認証結果

`gcloud auth application-default login`によるADC認証情報を、読み取り専用の
`list_voices`呼び出し(課金なし)で実際に取得できることを確認した。

| 確認項目 | 結果 |
|---|---|
| ADCから認証情報を取得できる | はい |
| Text-to-Speech APIへ接続できる | はい(list_voices成功) |
| `ja-JP-Neural2-B`が利用可能voiceとして返される | はい |
| APIの権限エラー | なし |

## 3. 使用Google Cloudプロジェクトの識別情報(秘密情報を除く)

`google.auth.default()`が返す認証情報オブジェクトの`quota_project_id`属性
(標準的なライブラリAPI経由、ADCファイル自体の読み取り・コピーは行っていない)
から取得した、秘密情報を含まないプロジェクト識別子:

```
quota_project_id: ikiiki-health-log
```

## 4. Text-to-Speech API利用可否

利用可能。上記list_voices呼び出しで、ja-JP向け41件のvoiceが返された。

## 5. `ja-JP-Neural2-B` の存在確認

存在を確認済み(41件のja-JP voice一覧に含まれる)。別voiceへの変更は行って
いない。

## 6. 使用入力と完全なsha256

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p4d/A01/source/pattern_a_full_hiragana.txt` |
| sha256(完全値) | `fb9ea8c9ef6740fd83fe905199d987609b2eba9e8ec79b6c3437dee17493bd5b` |
| P5Aで使用した入力との一致 | 一致 |
| APIへ実際に送信した文字列のsha256 | 同一値(`fb9ea8c9...`)であることを機械確認済み |

## 7. 実際の生成条件

| 項目 | 値 |
|---|---|
| chunk分割 | なし(全文1回) |
| SSML | 使用しない(plain text) |
| 話速・pitch・音量 | いずれも明示指定なし(デフォルト) |
| audio encoding | LINEAR16 |
| 発音辞書・語句別例外 | なし |

**レスポンス形式の実機検証について**: Google Cloud TTSのLINEAR16応答が
生PCMかWAVコンテナ(RIFF/WAVEヘッダー付き)かは公式ドキュメントだけでは
確実に判断できなかったため、認証確立後、短い単語「テスト」による最小限の
疎通確認を2回実施した(1回目: RIFF/WAVEヘッダーの有無確認、2回目:
framerate/channels/sampwidthの確認)。結果、**audio_content全体が
RIFF/WAVEヘッダー付きの完全なWAVファイル(24000Hz/mono/16bit)であることを
実機確認した**(推測ではない)。この2回はいずれも課金対象のTTS callであり、
下記の呼び出し回数に算入している。

## 8. TTS call回数

| 呼び出し | 入力 | 目的 |
|---|---|---|
| 1回目(疎通確認) | 「テスト」 | audio_contentのヘッダー形式確認 |
| 2回目(疎通確認) | 「テスト」 | framerate/channels/sampwidth確認 |
| 3回目(本検証) | `pattern_a_full_hiragana.txt`全文 | 本ステージの検証対象 |

本検証の入力を使った合成は1回のみ(指示通り)。合計3回のTTS callのうち、
本検証用は1回。

## 9. technical retry回数

0回(いずれの呼び出しも技術的失敗なし)。

## 10. raw音声の場所

| 項目 | 値 |
|---|---|
| path | `raw/A01_p5b_google_ja-JP-Neural2-B.wav` |
| duration | 37.548秒 |
| sample rate | 24000Hz |
| channels | 1(mono) |
| sha256 | `3ee5ef711fca71fa3cf01aa07cf7c756721885a84b4e539eb22d6e3bf8c0fbdc` |
| decode | OK |
| clipping | 検出なし |

## 11. 対象句ごとのASR診断

Azure STT(連続認識、診断用途のみ)による認識結果を、P4Dで確立済みの読み
正規化処理(SudachiPy tokenize→ひらがな化)へ通した後、6対象句の存在を
確認した。

| 対象句 | 診断結果 |
|---|---|
| せんしゅをこうたいでさげる | 検出 |
| めじるしというけつだんで | **未検出**(下記参照) |
| しゅびをかため | 検出 |
| わずかなりーど | 検出 |
| さいごのすうふん | 検出 |
| なにがおきる | **未検出**(下記参照) |

読み正規化後の該当箇所(抜粋):

> …いんぐらんどはせんしゅをこうたいでさげるめじるしというけつだん。でしゅびをかため、わずかなりーどめじるしをまもろうとします。…

「めじるしというけつだんで」が未検出だった理由: ASRが「めじるしという
けつだん」と「でしゅびをかため」の間に句点(。)を挿入したため、厳密な
部分文字列比較では不一致となった。ただし形態素列自体(せんしゅ/を/こうたい/
で/さげる/めじるし/という/けつだん/で/しゅび/を/かため)はすべて連続して
存在しており、**語句そのものの脱落ではなく、ASRの区切り方の癖である
可能性が高い**(断定はしない。試聴での確認が必要)。

## 12. 「なにがおきる」の診断結果

| 項目 | 結果 |
|---|---|
| 「なにがおきる」(正しい読み) | 検出されず |
| 「なんがおきる」(Azureの不合格理由と同じ誤読) | 検出されず |
| 実際のASR認識 | 「南が起きる」(みなみがおきる) |

読み正規化後の該当箇所:

> …さいごのすうふん、さむけといたみのさかいめでみなみがおきるのでしょうか。

Azure Speechで確認された「なんがおきる」とは異なる、**「みなみがおきる」
という別の誤認識**がASR上で確認された。これがGoogle Cloud TTS自体の発話
(「みなみ」と発音した)なのか、ASRの誤認識なのかは、本レポートでは断定
していない。**指示section9の明記通り、機械QA合格とはせず、要試聴箇所として
明示する。**

## 13. 機械QA結果

| 項目 | 結果 |
|---|---|
| 入力ハッシュが期待値と完全一致 | 合格 |
| API送信文字列のハッシュが入力ファイルと一致 | 合格 |
| voice=ja-JP-Neural2-B | 合格 |
| TTS生成call回数=1(本検証入力) | 合格 |
| chunk分割なし | 合格 |
| LINEAR16音声が正常に保存 | 合格 |
| decode可能 | 合格 |
| clipping等の重大なファイル異常 | なし(合格) |
| 「めじるし」ASR上5回 | 合格 |
| 対象句6件全て一致 | **不合格**(2件未検出、上記11・12参照) |

**総合判定: 機械QAは無条件合格としていない。** 「めじるしというけつだんで」
「なにがおきる」の2箇所は要試聴確認事項として明示する。ASRは診断情報であり、
ユーザー試聴を代替しない。

## 14. 作成・変更したファイル

- `er003_b1_p5b_audio.py`(更新): Google Cloud TTS用`make_google_tts_call_fn`・`extract_pcm_from_google_wav_response`(WAVヘッダー除去)を追加、`check_google_cloud_tts_availability`に`quota_project_id`取得を追加
- `er003_v1_b1_p5b_gcp_generate.py`(新規): 本ステージのオーケストレーションscript
- `er003_test_b1_p5b_audio.py`(更新): Google Cloud TTS利用可否テストを「利用不可」から「利用可能(ADCログイン後)」へ更新、WAVヘッダー抽出ロジックの単体テスト(synthetic WAVバイト列使用、実API呼び出しなし)を追加
- `er003_output/b1_p5b_gcp/A01/`配下の成果物一式
- `er003_output/b1_p5b_gcp/A01/instruction/ER-003-B1-P5B-GCP_instruction.md`: 本指示書の保存

## 15. テスト結果

- `er003_test_b1_p5b_audio.py`(11件、実API呼び出しは`list_voices`1回のみ、音声合成は含まない): 全合格
- プロジェクト全体の既存テストスイート: 1086件全合格(discover実行、回帰なし)

## 16. 再実行方法

```
.venv/Scripts/python.exe er003_v1_b1_p5b_gcp_generate.py
```

## 17. 既知のリスク

- ASR診断で2箇所(「めじるしというけつだんで」「なにがおきる」)が期待通りに
  検出されず、特に「なにがおきる」についてはAzureとは異なる誤認識
  (「みなみがおきる」)が見られた。これがTTS側の問題かASR側の問題かは
  未確定であり、試聴による確認が必須。
- 全文一致率(content_similarity_ratio)は0.9062で、P5A(Azure)の0.8989と
  近い水準。機械的な指標だけでは、AzureとGoogle Cloud TTSの優劣を判断
  できない。
- Amazon Pollyは今回も未検証のまま。

## 18. Git status

このレポート作成時点では未コミット。P5B-GCP関連ファイルのみをステージして
コミット予定。

## 19. push

実行していません。

---

## ユーザー試聴のお願い

`raw/A01_p5b_google_ja-JP-Neural2-B.wav`を試聴し、指示section10の全項目
(特に「目印という決断で」周辺の欠落有無、「何が起きる」が「なにがおきる」
と正しく発話されているか)をご確認ください。機械QAは2項目で厳密一致せず、
**「品質合格」「原稿忠実性確認済み」「自然さ確認済み」とは判断していません。**
