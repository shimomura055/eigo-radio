# ER-003-B1-P5B-GCP Google Cloud TTS単独検証

## 1. 現在の判定
ER-003-B1-P5Bは未完了である。
前回はGoogle Cloud TTSとAmazon Pollyの認証確認だけを実施し、音声合成は1回も実行していない。
コミット `0fe94eb` はP5B完了ではなく、認証待ちの実行準備状態として扱う。
今回はGoogle Cloud TTSのみを対象にする。Amazon Pollyの認証・実装・生成は行わない。

## 2. 目的
P4DおよびP5Aと完全に同一の全文ひらがな入力をGoogle Cloud TTSで1回生成し、以下を確認する。

* 原稿内の語句が省略されないか
* 原稿外の語句が追加されないか
* 「何が起きる」が「なにがおきる」と発話されるか
* 全文ひらがな入力でも自然な日本語として発話できるか
* Azure Speechの不自然さがAzure固有か、入力方式に起因するか

## 3. 認証方式
Application Default Credentialsを使用する。
以下を前提とする。

* ユーザーが `gcloud auth application-default login` を実行済み
* 対象Google CloudプロジェクトでText-to-Speech APIが有効
* ADCのクォータプロジェクトが設定済み

サービスアカウントキーファイルの作成を要求しない。
以下を禁止する。

* 認証情報のコードへの直書き
* アクセストークンのログ出力
* ADCファイルの読み取り・コピー
* 認証ファイルのGit管理
* ユーザー認証情報のレポート記載

## 4. 事前確認
音声生成前に、実環境で以下を確認する。

1. ADCから認証情報を取得できる
2. Text-to-Speech APIへ接続できる
3. `ja-JP-Neural2-B` が利用可能なvoiceとして返される
4. 使用プロジェクトが特定できる
5. APIの権限エラーがない

voice一覧確認で `ja-JP-Neural2-B` が存在しない場合は、別voiceへ変更しない。
その時点で停止し、実際に取得した日本語voice一覧を、秘密情報を除いて報告する。

## 5. Google Cloud合成処理の実装
前回未実装だったGoogle Cloud Text-to-Speechの音声合成処理を、公式クライアントライブラリの実際のレスポンス仕様に基づいて実装する。
以下を使用する。

* API：Google Cloud Text-to-Speech
* Language code：`ja-JP`
* Voice：`ja-JP-Neural2-B`
* Input：plain text
* Audio encoding：LINEAR16
* Speaking rate：明示指定しない
* Pitch：明示指定しない
* Volume gain：明示指定しない
* SSML：使用しない

推測したレスポンス構造を使用しない。
認証後に、公式SDKを使用した最小限の短い疎通確認を行ってよい。ただし、本検証の入力を使った合成は1回だけとする。
疎通確認で音声を生成した場合は、それも課金対象のTTS callとして呼び出し回数に含め、目的と入力を報告する。
可能であれば、音声を生成しないvoice一覧取得によって疎通を確認する。

## 6. 検証入力
以下の既存ファイルを変更せず使用する。
`pattern_a_full_hiragana.txt`
期待されるsha256：
`fb9ea8c9ef6740fd83fe905199d987609b2eba9e8ec79b6c3437dee17493bd5b`
以下を変更しない。

* 文字
* 句読点
* ダッシュ
* 空白
* 語順
* 「めじるし」
* 読み
* 文の区切り

APIへ渡した実際の文字列についてもsha256を計算し、入力ファイルと完全一致することを確認する。

## 7. 生成条件
全文を1回のTTS API呼び出しで生成する。
以下を行わない。

* chunk分割
* 文分割
* 原稿修正
* marker変更
* SSML
* 発音辞書
* 話速調整
* pitch調整
* 音量調整
* 英語Componentへの置換
* MFA
* Dynamics 3
* Gemini TTS生成
* Azure Speech生成
* Amazon Polly生成

APIの一時的な通信障害によるtechnical retryが発生した場合は、実際の呼び出し回数とエラー内容を記録する。

## 8. 保存成果物
以下を保存する。

* 実際に送信した入力
* 入力の完全なsha256
* Google Cloud voice一覧確認結果
* 使用voice
* language code
* audio encoding
* TTS API call回数
* technical retry回数
* APIレスポンスの非秘密メタデータ
* raw音声
* 音声のduration、sample rate、channels
* ASR診断
* 機械QA結果
* 実行ログ

推奨ファイル名：
`A01_p5b_google_ja-JP-Neural2-B.wav`
次の状態を明記する。
`PROTOTYPE / NOT_APPROVED`

## 9. 機械QA
以下を確認する。

* 入力ハッシュが期待値と完全一致する
* API送信文字列のハッシュが入力ファイルと一致する
* voiceが `ja-JP-Neural2-B` である
* TTS生成callが1回である
* chunk分割がない
* LINEAR16音声が正常に保存されている
* 音声がdecode可能
* clippingなどの重大なファイル異常がない
* 「めじるし」がASR上5回存在するか
* 以下の対象句のASR結果

対象句：

1. せんしゅをこうたいでさげる
2. めじるしというけつだんで
3. しゅびをかため
4. わずかなりーど
5. さいごのすうふん
6. なにがおきる

「なにがおきる」が「なんがおきる」と認識された場合は、機械QA合格とはせず、要試聴箇所として明示する。
ASRは診断情報であり、ユーザー試聴を代替しない。

## 10. ユーザー試聴項目
ユーザーが以下を確認する。
原稿忠実性

* 「選手を交代で下げる」が省略されていない
* 「目印という決断で」が省略されていない
* 「守備を固め」に「る」が追加されていない
* 5つの「目印」がすべて発話される
* その他の欠落、追加、言い換えがない

読み

* 「最後の数分」が正しい
* 「何が起きる」が「なにがおきる」である
* 「わずかなリード」が自然である

自然さ

* 全体が自然な日本語として聞こえる
* 不自然に平坦でない
* 語句の切れ目が不自然でない
* 声色が大きく変化しない
* Listening Previewとして許容できる

## 11. 合格条件
以下をすべて満たした場合のみ合格候補とする。

* 原稿内語句の欠落がない
* 原稿外語句の追加がない
* 意味を変える言い換えがない
* 「なにがおきる」が正しく発話される
* 重点語句の読みが正しい
* 日本語として自然である
* Preview用途として最低限許容できる
* ユーザーが合格と判断する

機械QAが合格しても、ユーザー試聴前は合格扱いにしない。

## 12. 分岐
Google Cloud TTSが合格した場合
Amazon Pollyの準備は一旦保留する。
Google Cloud TTSについて複数回生成による再現性を別タスクで検証する。
原稿忠実性は合格だが、日本語が不自然な場合
全文ひらがな入力方式に原因がある可能性を高める。
同じGoogle Cloud voiceで以下の入力比較を別タスクとして検討する。

* 漢字かな交じり原稿
* 必要箇所だけ読み制御した原稿
* 全文ひらがな原稿

原稿の欠落・追加がある場合
Google Cloud TTSを不合格とし、Amazon Polly Kazuhaの準備・検証へ進む。

## 13. 非対象範囲

* Amazon Pollyの認証設定
* Amazon Polly合成処理
* Azure別voice
* Gemini TTSの再調整
* 原稿修正
* marker方式変更
* 英語音声生成・置換
* MFA
* Dynamics 3
* B1本文
* push

## 14. 実行報告
以下の順に報告する。

1. 検証目的
2. ADC認証結果
3. 使用Google Cloudプロジェクトの識別情報（秘密情報を除く）
4. Text-to-Speech API利用可否
5. `ja-JP-Neural2-B` の存在確認
6. 使用入力と完全なsha256
7. 実際の生成条件
8. TTS call回数
9. technical retry回数
10. raw音声の場所
11. 対象句ごとのASR診断
12. 「なにがおきる」の診断結果
13. 機械QA結果
14. 作成・変更したファイル
15. テスト結果
16. 再実行方法
17. 既知のリスク
18. Git status
19. pushを実行していないこと

ユーザー試聴前に「品質合格」「原稿忠実性確認済み」「自然さ確認済み」と判断しないこと。
