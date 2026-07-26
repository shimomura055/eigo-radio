# ER-003-B1-P5A 実行報告(日本語TTS原稿忠実性スクリーニング)

## 1. 検証目的

ER-003-B1-P4D-AUDITで、Gemini TTSが完全な入力(前処理には欠落なし)の一部
(「で下げる」「という決断」)を音声生成段階で省略していたことが確認された。
本ステージでは、Gemini TTSへの局所修正を行わず、P4Dで実際に使用したのと
完全に同一の全文ひらがな入力を、複数の日本語TTSエンジンで生成し、
**原稿忠実性(省略・追加の有無)を第一評価軸として**比較する。

## 2. 使用した入力とハッシュ

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p4d/A01/source/pattern_a_full_hiragana.txt` |
| sha256 | `fb9ea8c9ef6740fd83fe905199d987609b2eba9e8ec79b6c3437dee17493bd5b` |

このファイルはP4D完了時に保存されたものをそのまま使用し、内容を一切変更していない。
実際にAzure Speechへ送信した文字列のsha256も同一値(`fb9ea8c9...`)であることを
機械確認済み(語句・句読点・ダッシュ・「めじるし」表現・空白・文分割・読み・語順、
いずれも無変更)。

## 3. 各エンジンの利用可否

| 候補 | 利用可否 | 理由 |
|---|---|---|
| Google Cloud Text-to-Speech(ja-JP-Neural2-B) | **不可** | `google-cloud-texttospeech`パッケージ未インストール、かつ`GOOGLE_APPLICATION_CREDENTIALS`が`.env`に未設定。利用するには(1) パッケージインストール、(2) GCPサービスアカウントキー発行、(3) Text-to-Speech API有効化が必要。 |
| Azure Speech(ja-JP-NanamiNeural) | **可** | SDK(`azure-cognitiveservices-speech`)インストール済み、`SPEECH_KEY`/`SPEECH_REGION`が`.env`に既存設定済み(このプロジェクトでAzure STT用に既に使用中の同一リソース)。実機での最小疎通テストも合格済み。 |
| Amazon Polly Neural(Kazuha) | **不可** | `boto3`パッケージ未インストール、かつ`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`が`.env`に未設定。利用するには(1) パッケージインストール、(2) AWS IAMユーザー発行・アクセスキー設定、(3) Amazon Polly(neural engine, Kazuha対応リージョン)への権限付与が必要。 |

指示section3の明記通り、勝手な代替エンジンへの差し替えは行わず、**利用可能な
Azure Speechのみを実行した。**

## 4. 各候補の実際の生成条件

| 項目 | 値 |
|---|---|
| chunk分割 | なし(全文1回) |
| 英語Component置換 | なし |
| MFA | 未実行 |
| Dynamics 3 | 未適用 |
| 話速・ピッチ調整 | なし |
| スタイル指定 | なし(Azure Speechのstyle未指定) |
| SSML発音修正 | なし(plain textをそのまま合成、`speak_text_async`使用) |
| 個別例外辞書 | なし |

## 5. 各候補のTTS call回数

| 候補 | call回数 | retry回数 |
|---|---|---|
| Azure Speech | 1 | 0(技術的失敗なし) |
| Google Cloud TTS | 0(未実行) | - |
| Amazon Polly | 0(未実行) | - |

## 6. 各raw音声の場所

| 候補 | path | duration | sha256(先頭16文字) |
|---|---|---|---|
| Azure Speech | `azure_ja-JP-NanamiNeural/raw/A01_p5a_azure_ja-JP-NanamiNeural.wav` | 38.975秒 | `15b013033d4962c3` |

## 7. 対象句ごとのASR診断

Azure STT(連続認識)による認識結果を、P4Dで確立済みの読み正規化処理(SudachiPy
tokenize→ひらがな化)へ通した後、5対象句の存在を確認した(境界決定・合否確定には
使わず、診断情報として扱う)。

| 対象句 | 診断結果 |
|---|---|
| せんしゅをこうたいでさげる | 検出 |
| めじるしというけつだんで | 検出 |
| しゅびをかため | 検出 |
| わずかなりーど | 検出 |
| さいごのすうふん | 検出 |

読み正規化後の該当箇所(抜粋):

> …いんぐらんどはせんしゅをこうたいでさげるめじるしというけつだんでしゅびをかため、わずかなりーどめじるしをまもろうとします。…

ASR生テキスト(参考、診断用):

> …イングランドは選手を交代で下げる目印という決断で守備を固め、わずかなリード目印を守ろうとします。…

**P4Dで欠落していた「で下げる」「という決断」に相当する箇所が、Azure Speechの
生成音声のASR認識では両方とも検出された。** ただし、これはASR結果に基づく診断
情報であり、実際の音声が本当に欠落なく発話されているかは、後述のユーザー試聴
での確認が必要(ASR結果と実音声が食い違う可能性があるため)。

その他、ASR側の軽微な誤変換(「シュート」→「修と」、「決勝」→「結晶」、
「歓喜」→「寒気」、「均衡」周辺の誤認識)が見られたが、これらはP4/P4B/P4Dの
複数の別TTS音声でも共通して見られたパターンであり、TTSの発話ではなくAzure STT
側の同音異義語の癖である可能性が高い。

## 8. 機械QA結果

| 項目 | 結果 |
|---|---|
| 3候補が同一入力を使用 | Azure Speechのみ実行(他2件は未実行につき対象外)。実行した1候補は入力ハッシュ一致を確認済み |
| 各候補のTTS call回数=1 | 合格 |
| chunk分割なし | 合格 |
| 入力文字列に欠落なし | 合格(送信文字列sha256がP4D入力と完全一致) |
| raw音声が正常に生成 | 合格(decode OK、clipping検出なし) |
| 「めじるし」5回検出 | 合格(marker_occurrence_total=5) |
| 日本語比率 | 0.9444(日本語と判定) |
| 意図しない英語混入 | なし |
| 全文一致率(marked_textとの比較、参考値) | 0.8989 |

**この機械QA合格は、原稿忠実性の承認を意味しない。** ASRの認識結果と実際の
音声が食い違う可能性があるため、最終判断は次のユーザー試聴による。

## 9. 作成・変更したファイル

- `er003_b1_p5a_audio.py`(新規): P4D入力読み込み・ハッシュ検証、3エンジン利用可否判定、Azure Speech用tts_call_fn、対象句チェック、ASR読み正規化
- `er003_b1_p5a_audio.py`にバグ修正: `check_engine_availability()`が`.env`を読み込まずに`SPEECH_KEY`/`SPEECH_REGION`を判定していたため、単体実行時に誤って「利用不可」と判定していた。`load_dotenv()`呼び出しを追加して修正(テストでは他テストの実行順序に依存して偶然合格していたため発覚)
- `er003_v1_b1_p5a_generate.py`(新規): オーケストレーションscript
- `er003_test_b1_p5a_audio.py`(新規、12件): 実Azure Speech APIへの最小呼び出し1件を含む
- `er003_output/b1_p5a/A01/`配下の成果物一式(下記参照)
- `er003_output/b1_p5a/A01/instruction/ER-003-B1-P5A_instruction.md`: 本指示書の保存(section11)

## 10. 再実行方法

```
.venv/Scripts/python.exe er003_v1_b1_p5a_generate.py
```

Google Cloud TTS / Amazon Pollyを追加する場合は、対応パッケージのインストールと
認証情報の`.env`設定後、`er003_b1_p5a_audio.check_engine_availability()`で
利用可否を再確認したうえで、`er003_v1_b1_p5a_generate.py`に各エンジン用の
生成関数を追加実装する必要がある(現時点では未実装、指示section3の「勝手な
代替禁止」に従い今回は見送った)。

## 11. 既知のリスク

- Google Cloud TTS・Amazon Pollyが未検証のため、Azure Speech以外の候補との
  比較ができていない。3候補中1候補のみの結果である。
- ASR診断はあくまで機械的な参考情報であり、実際の音声品質・忠実性の最終判断は
  ユーザー試聴が必須(指示・本レポート双方で明記済み)。
- Azure Speechの1回の生成結果のみであり、再現性(複数回生成しても毎回欠落なく
  発話されるか)は今回未検証(指示section10の分岐に従い、忠実性確認後に実施)。

## 12. 指示書の保存先とハッシュ

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p5a/A01/instruction/ER-003-B1-P5A_instruction.md` |
| sha256 | `3930297c96abc9565a90e6088260cfecc551e6cd5345abdcdb471c8b6eb5d7f7` |
| 管理ID | ER-003-B1-P5A |
| 実行時commit | `0004141cd664e872287dccc67595d7032d2dfe29`(P4D完了コミット、このステージ実行直前のHEAD) |
| 指示書からの逸脱 | なし |

## 13. Git status

このステージの成果物はまだコミットしていません(このレポート作成時点)。
P5A関連ファイルのみをステージしてコミットする予定です。

## 14. push

実行していません。

---

## ユーザー試聴のお願い

`azure_ja-JP-NanamiNeural/raw/A01_p5a_azure_ja-JP-NanamiNeural.wav`を試聴し、
指示section8の10項目(特に「選手を交代で下げる」「目印という決断で」の省略
有無)をご確認ください。機械QAは全て合格していますが、**ユーザー試聴による
確認前に「品質合格」「原稿忠実性確認済み」とは判断していません。**
