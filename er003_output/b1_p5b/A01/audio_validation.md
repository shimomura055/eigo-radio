# ER-003-B1-P5B 実行報告(Google Cloud TTS／Amazon Polly比較検証)

## 1. 検証目的

P5AではAzure Speech(ja-JP-NanamiNeural)のみ検証できた。本ステージでは残る
2候補(Google Cloud Text-to-Speech、Amazon Polly Neural)について、P4Dと
完全に同一の全文ひらがな入力を用い、原稿忠実性と自然さを確認する予定だった。

## 2. Azure P5Aの不合格理由

ユーザー試聴により、以下の理由で不合格と判定された。

- 全体が自然な日本語読み上げになっていない
- 「何が起きる」を「なんがおきる」と発音した

Azureへの追加調整・再生成は行っていない。

## 3. 使用した入力と完全なsha256

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p4d/A01/source/pattern_a_full_hiragana.txt` |
| sha256(完全値) | `fb9ea8c9ef6740fd83fe905199d987609b2eba9e8ec79b6c3437dee17493bd5b` |
| P5Aで使用した入力との一致 | 一致(machine確認済み) |

## 4. Google Cloud TTSの利用可否

**利用不可。** 読み取り専用の`list_voices`呼び出し(音声合成は行わず課金は
生じない)で確認したところ、`DefaultCredentialsError`が発生した。

```
Your default credentials were not found. To set up Application Default
Credentials, see https://cloud.google.com/docs/authentication/external/set-up-adc
```

**必要な準備:**
1. GCPサービスアカウントキー(JSON)を発行し、環境変数`GOOGLE_APPLICATION_CREDENTIALS`にファイルパスを設定する。または`gcloud auth application-default login`でADCを設定する。
2. 対象GCPプロジェクトでCloud Text-to-Speech APIを有効化する。
3. 課金設定(該当プロジェクトに有効な請求先アカウントが紐付いていること)。

パッケージ(`google-cloud-texttospeech`)は今回インストール済み(認証情報が
用意され次第、すぐに実装・実行できる状態)。

## 5. Amazon Pollyの利用可否

**利用不可。** 読み取り専用の`describe_voices`呼び出し(音声合成は行わない)
で確認したところ、`NoCredentialsError`が発生した。

```
Unable to locate credentials
```

**必要な準備:**
1. AWS IAMユーザー(または既存ロール)を用意し、`polly:SynthesizeSpeech`および`polly:DescribeVoices`権限を付与する。
2. アクセスキーを発行し、環境変数`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`へ設定する(または`~/.aws/credentials`にprofileを設定する)。
3. Kazuha(neural engine)が利用可能なリージョン(例: `ap-northeast-1`)を指定する。

パッケージ(`boto3`)は今回インストール済み。

## 6. 認証・権限上、ユーザー対応が必要な事項

上記4・5の通り、**両エンジンとも、ユーザーによる認証情報の準備(GCPサービス
アカウントキーまたはADC設定、AWSアクセスキー発行)が必要**です。秘密情報の
値は、ログ・レポート・テスト出力・Git管理ファイルのいずれにも記録していません。
新しい恒久的アクセスキーの作成、`.env.example`への実値記載、認証ファイルの
コミットはいずれも行っていません。

## 7. 各エンジンの実際の生成条件

**未実施。** 両エンジンとも認証情報が利用できないため、音声合成呼び出し自体を
行っていない。

なお、Google Cloud TTSについては、LINEAR16形式でのレスポンスにWAVヘッダーが
含まれるかどうか(SDKバージョンにより挙動が異なる可能性がある既知の論点)を
実機で検証できていないため、認証情報なしに合成呼び出しコードを書くことは
見送った(推測に基づく未検証コードを書かない、というこのプロジェクト全体の
方針に従った)。認証情報が用意され次第、実装・検証する。

## 8. 各エンジンのAPI call回数

| エンジン | 合成call回数 | 可否確認call回数(読み取り専用、課金なし) |
|---|---|---|
| Google Cloud TTS | 0 | 1(`list_voices`) |
| Amazon Polly | 0 | 1(`describe_voices`) |

## 9. raw音声の場所

**なし。** 両エンジンとも合成を実行していないため、音声ファイルは生成されて
いない。

## 10. 対象句ごとのASR診断

**未実施。** 音声が生成されていないため、対象句(せんしゅをこうたいでさげる /
めじるしというけつだんで / しゅびをかため / わずかなりーど / さいごのすうふん /
なにがおきる)のASR診断は行っていない。

## 11. 「なにがおきる」の診断結果

**未実施。** 同上の理由により未確認。

## 12. 機械QA結果

音声生成自体が行われていないため、機械QAの対象がない。認証確認のみ:

| チェック項目 | Google Cloud TTS | Amazon Polly |
|---|---|---|
| パッケージインストール | 済み | 済み |
| 認証情報 | なし | なし |
| 読み取り専用呼び出し結果 | `DefaultCredentialsError` | `NoCredentialsError` |
| 音声合成 | 未実行 | 未実行 |

## 13. 作成・変更したファイル

- `er003_b1_p5b_audio.py`(新規): 2エンジンの利用可否判定(実クライアント呼び出し)、対象句チェック(6句、「なにがおきる」/「なんがおきる」判定を含む)
- `er003_v1_b1_p5b_generate.py`(新規): オーケストレーションscript(現時点では可否確認のみ実行)
- `er003_test_b1_p5b_audio.py`(新規、8件): 実クライアントへの読み取り専用呼び出しを含む
- `er003_output/b1_p5b/A01/`配下の成果物一式(source/availability.json、instruction/ER-003-B1-P5B_instruction.md等)
- 環境へのパッケージインストール: `google-cloud-texttospeech`、`boto3`(認証情報は一切含まない、コード上の秘密情報直書きなし)

## 14. 再実行方法

認証情報の準備後:

```
.venv/Scripts/python.exe er003_v1_b1_p5b_generate.py
```

ただし、上記の通り実際の合成呼び出しコード(特にGoogle Cloud TTS側)は
今回未実装のため、認証情報が用意された段階で、まず実機でレスポンス形式を
確認したうえで実装を追加する必要がある。

## 15. 既知のリスク

- 本ステージでは1件も音声を生成できておらず、仮説A(Azure固有の問題)・
  仮説B(全文ひらがな方式そのものの問題)のいずれも検証できていない。
- Google Cloud TTSのレスポンス形式(WAVヘッダー有無)を実機検証していないため、
  認証情報が用意された後の初回実装時に、追加の動作確認が必要になる。
- 2エンジンとも認証準備にはユーザー側の作業(サービスアカウント発行、IAM権限
  付与等)が必要であり、いつ検証を再開できるかはユーザーの対応状況に依存する。

## 16. 指示書の保存先とハッシュ

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p5b/A01/instruction/ER-003-B1-P5B_instruction.md` |
| sha256 | `c76ad29938346f827bb390edaa02d3ea6a8fd89d003f595afed4834a72da6c7c` |
| 管理ID | ER-003-B1-P5B |
| 実行時commit | `ffe9cc90746e69f38488fe0a7e2c215360c5101f`(P5A完了コミット、このステージ実行直前のHEAD) |
| 指示書からの逸脱 | なし(両エンジンとも認証情報未整備のため音声合成は未実行) |

## 17. Git status

このレポート作成時点では未コミット。P5B関連ファイルのみをステージしてコミット予定。

## 18. push

実行していません。

---

## ユーザーへの確認事項

Google Cloud TTS・Amazon Pollyのいずれも、認証情報が本実行環境に存在しない
ため、今回は比較検証を実施できませんでした。以下のいずれかをご検討ください。

1. 認証情報(GCPサービスアカウントキーまたはADC設定、AWSアクセスキー)をご用意いただければ、次回このステージを再実行します。
2. 認証情報の準備が難しい場合、この2エンジンの検証を見送り、別の方針(例: Azure Speechの別voice確認、全文ひらがな方式自体の見直し)へ進むか、ご指示ください。

音声が1件も生成されていないため、「品質合格」「自然さ確認済み」「原稿忠実性
確認済み」の判断はいずれのエンジンについても行っていません。
