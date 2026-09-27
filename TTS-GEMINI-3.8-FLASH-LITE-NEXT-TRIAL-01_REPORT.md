# TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01 REPORT

管理ID: `TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01`
性質: Trial限定。Production変更0件。**Stage 1(TTS実呼び出し)は未実施**。
実費用: **¥0**(Phase 0のSDK確認段階で、実行不可能であることが
ネットワーク呼び出し0件で確定したため、TTS/ASR課金APIを1回も呼んでいない)。

## §0 要約

委任文の「SDK(ユーザー決定)」節が求める事前確認(a)を実施した結果、
**google-genai==2.14.0のPython SDK経由では、公式ドキュメントが説明する
`speech_metadata`をGemini 3.8系TTSへ正しく送信する手段が存在しない**
ことが、ネットワーク呼び出し0件(client側のpydantic検証、および送信直前
httpxリクエストの内容検査のみ)で確定した。委任文の明記
(「問題があればSTOPして報告する」)に従い、Stage 1のTTS実呼び出しは
行わずここでSTOPし報告する。

具体的には、公式ガイドが示す2つの経路のいずれも機能しない:

1. **GenerateContent API**(`client.models.generate_content`、現行
   Productionと同じ呼び出し形状): `types.Part`に`speech_metadata`を
   指定すると、pydanticモデルが`extra="forbid"`のため
   **即座にValidationError**(`Extra inputs are not permitted
   [type=extra_forbidden]`)。dict直接渡し・kwarg・属性代入のいずれも
   同じ理由で失敗(SDK側に該当フィールド自体が無い)。
2. **Interactions API**(`client.interactions.create`): こちらは
   client側のバリデーションでは拒否されない(`_gaos`内部モデルは
   `extra="allow"`)。しかし実際に送信される直前のHTTPリクエストbodyを
   検査したところ、
   - `annotations`配列に`{"type": "speech_metadata", "style": "..."}`を
     入れた場合 → SDKの「未知annotation型はUnknownAnnotationへ変換して
     保持する」ロジックが働き、送信直前のwire body上では
     `{"type": "UNKNOWN", "raw": {"type": "speech_metadata", "style":
     "..."}, "is_unknown": true}`へ**変質**する(サーバが期待する形と
     一致しない)。
   - contentのsibling fieldとして`speech_metadata`を直接置いた場合 →
     TextContentの独自`model_serializer`が宣言済みfield以外を出力しない
     ため、送信直前のwire bodyから**完全に消失**する(サイレントに
     失われる、エラーも出ない)。

つまり、現行google-genai SDK(2.14.0、requirements-ci.txt記載バージョン)
は、Gemini 3.8系TTSの`speech_metadata`という中核機能に、まだ型定義上
追随できていない(公式ドキュメントとPython SDKの実装に乖離がある)。
本Trialの目的(「正しい入力形式で使いこなせるかの確認」)の前提条件が
この時点で満たせないため、Stage 1のTTS実呼び出しへは進んでいない。

## §1 SDK確認結果(委任文a〜d)

| 項目 | 結果 |
|---|---|
| (a) speech_metadataが2.14.0で実際に送信可能か | **不可**(上記§0参照、GenerateContent APIはclient側で即拒否、Interactions APIは送信直前に破損/消失。いずれもネットワーク呼び出し0件で確認、実費用¥0)。 |
| (b) 既存TTS呼び出しとの互換性 | **問題なし**。Trial隔離venvから既存TTS関連unit test 9ファイル(下記§2)を実行し全てOK(合計264+テストケース)。google-genai 2.11.0→2.14.0への切替自体は既存呼び出し形状(`client.models.generate_content(contents=文字列, config=...)`)に影響しない。 |
| (c) pip check で依存関係衝突なし | **問題なし**(`pip check` → "No broken requirements found")。 |
| (d) Trial環境だけの変更で実行できるか | **可能**。`.venv_trial_genai214`(Python 3.12、`requirements-ci.txt`と同一構成+production側の音声/日本語処理オプション依存[soundfile/pykakasi/jaconv/imageio_ffmpeg]を追加導入)を新規作成し、Production `.venv`/`.venv-ci`・`requirements*.txt`は無変更(`git status`で無差分)。 |

## §2 既存TTS関連unit test実行結果(Trial隔離venvから)

対象9ファイル、全てOK:

```
er002_test_common            : Ran 99 tests - OK
er003_test_b1_p3v_capability  : Ran 7 tests  - OK
er003_test_b1_p4c_audio       : Ran 29 tests - OK
er003_test_b1_p7a_audio       : Ran 9 tests  - OK
er003_test_b1_p9a_audio       : Ran 12 tests - OK
er003_test_b1_p9a_r1_audio    : Ran 14 tests - OK
er003_test_audio_tts_asr_safety: Ran 96 tests - OK
er003_test_v1_n3_01_tts_generate: Ran 21 tests - OK
er003_test_key_words_canonicalization: Ran 57 tests - OK
```

詳細ログ:
`er022_output/tts_gemini_3_8_flash_lite_next_trial_01/existing_unit_tests_log.txt`

備考: `fugashi`(日本語形態素解析、JA ASR補完層Candidate B/C/Dで使用)は
Trial venvに未導入だが、これは既存の設計済みfail-safe
(`er007_ja_secondary_asr_01.py`、import失敗時はpykakasiベースのみで
継続する旨のRuntimeWarningを出して縮退)が正しく作動しただけであり、
genai版数とは無関係、テスト結果はいずれもOKのまま。

## §3 SDKバージョン・依存関係

- Trial隔離venv: `.venv_trial_genai214`(Production `.venv`
  [google-genai==2.11.0]・`.venv-ci`[2.14.0]とは別、新規作成)。
- `google-genai==2.14.0`(requirements-ci.txt記載と一致)。
- `pip check`: `No broken requirements found`
  (`er022_output/tts_gemini_3_8_flash_lite_next_trial_01/venv_pip_check.txt`)。
- Production `.venv`・`.venv-ci`・`requirements-ci.txt`への変更: **0件**。

## §4 speech_metadata送信形状の実測(キー本文非掲載、構造のみ)

ネットワーク送信直前のHTTPリクエストbody(`httpx.Client.send`を
Trial検証コード内だけで一時的に差し替え、実際の送信直前で意図的に
`RuntimeError`へ変換して中断。**ネットワーク呼び出しは1件も発生していない**、
APIキーは環境変数からのみ読み込み、本文・キー実値はログ未出力):

- GenerateContent API: リクエスト構築の時点(`types.Part`生成)で
  `pydantic.ValidationError`が発生するため、そもそもHTTPリクエストが
  組み立てられない。
- Interactions API `annotations`経路: 送信直前のbody例(構造のみ、
  実際のcanonical本文ではなくprobe用の汎用文言)
  ```
  {"text": "...", "annotations": [{"type": "UNKNOWN", "raw":
    {"type": "speech_metadata", "style": "..."}, "is_unknown": true}],
   "type": "text"}
  ```
  (公式が期待する`{"type": "speech_metadata", "style": "..."}`という
  形ではなく、SDKの「未知annotation保持」ラッパーへ変質している)。
- Interactions API sibling field経路: 送信直前のbodyに`speech_metadata`
  キー自体が存在しない(TextContentの`model_serializer`が宣言済み
  フィールドのみを出力するため)。

再現コード: `er022_tts_gemini_3_8_flash_lite_next_trial_01_sdk_check.py`
(Trial専用、Production非変更、実行しても課金APIは呼ばれない設計)。
結果JSON: `er022_output/tts_gemini_3_8_flash_lite_next_trial_01/sdk_check_results.json`

## §5 pricing_snapshot.json登録(実施済み、既存エントリは無変更)

`er005_output/cost_baseline_01/pricing_snapshot.json`へ、
`gemini-3.8-flash-lite-tts`の公式単価(Standard: 入力$0.50/出力$6.00、
Batch: 入力$0.25/出力$3.00、いずれもper 1,000,000 tokens)を**追加のみ**
で登録した(出典`https://ai.google.dev/gemini-api/docs/pricing`、
取得日時2026-09-27 04:11 UTC、既存の`gemini-2.5-pro-preview-tts`/
`gemini-3.1-flash-tts-preview`エントリは無変更)。

## §6 Stage別segment表・A/B試聴artifact・latency・cost実測

**該当なし。Stage 1のTTS実呼び出しを行っていないため、既存完成音声(A)
との比較・ASR結果・duration実測・latency・実費用は発生していない。**
代表segment候補(`tension_reflection`)の選定自体は計画doc §5・
PLAN-01 REPORT §3のとおり有効(変更なし)。

## §7 音質所見・現行TTSとの差

**音質評価は実施していない**(TTS呼び出しに到達していないため)。
現行TTSとの差(§1-1〜§1-6、公式ドキュメントベースの技術差分)は
計画doc(`docs/pm/plan_tts_gemini_3_8_flash_lite_next_trial_01.md`)の
記載から変わらない。本Trialで新たに判明した差分は、**「公式ドキュメントが
説明するAPI形状と、実際にインストール可能なPython SDK(google-genai
2.14.0)の型定義が一致していない」という、ドキュメント-SDK間の乖離**
そのものである(§0参照)。

## §8 累積費用・Cap

- 実費用: **¥0**(TTS/ASR課金API呼び出し0件)。
- Cap: ¥500(未消費)。
- pricing_snapshot.json登録(§5)・SDK環境構築・unit test実行・
  probe実行はいずれも課金APIを伴わない。

## §9 Sonnet仮分類

**STOP該当(委任文の明記に基づく機械的STOP、Sonnetの独自判断による
拡大解釈ではない)**。委任文「切替前に必ず確認して記録: (a)...
問題があればSTOPして報告する(2.11.0へ戻すなどの独自判断はしない)」に
定められた条件に直接該当するため、Stage 1のTTS実呼び出しへは進んで
いない。分類ラベルとしては、本Trialの主題(`speech_metadata`による
verbatim transcript方式の実現可能性)自体が**現時点のSDKでは検証不能
(NOT_EXECUTABLE_WITH_CURRENT_SDK)**であり、「Prompt/style調整をしても
解決しない種類の障壁」である点で、前回Trial(AB-01、Prompt不一致由来の
REJECTED)とは性質が異なる。

## §10 未確認事項として残るもの(推測で埋めていない)

- google-genai SDKの将来バージョン(2.14.0より新しい版)で
  `speech_metadata`が正式にタイプ定義される可能性(SDK側の既知の
  issue/changelogは本Trialでは調査していない)。
- SDKの型層を経由せず、生のHTTP POST(`requests`/`httpx`を直接使い、
  公式ドキュメント記載のJSON形状をそのまま送る、SDKの`interactions`
  ラッパーを使わない実装)であれば、サーバ側が`speech_metadata`を
  正しく解釈するかどうか(**未検証、かつ本Trialの承認範囲
  [「Trialでは google-genai 2.14.0 を使う」]を超える新しいアプローチ
  のため、Sonnet独自の判断では実装していない**、§11参照)。
- Vertex AI経由(`vertexai=True`)であれば別の型定義・エンドポイントに
  なる可能性(本Trialは`GEMINI_API_KEY`によるGenerative Language API
  経路のみを確認、Vertex AIは未確認)。

## §11 次の一手の選択肢(USER_DECISION_REQUIRED、実装はしていない)

1. **SDKバイパス(生REST)を試す**: `google-genai`のPython型層を経由せず、
   `requests`/`httpx`で公式ドキュメント記載のJSON形状を直接POSTする
   Trial追加実装。長所: SDKの型定義の遅れに影響されず、公式APIそのものの
   挙動を検証できる。短所: 「Trialでは google-genai 2.14.0 を使う」という
   既存ユーザー決定の実装方針(SDK経由)から外れる新しいアプローチであり、
   ユーザーの追加承認が必要。
2. **SDKの新しいバージョンを待つ/調査する**: `google-genai`のリリース
   ノート・GitHub issueを確認し、`speech_metadata`対応版がいつ出るか
   調べる(追加のHTTP GETのみ、¥0)。
3. **本Trialをここで打ち切り、Gemini 3.8系TTSの採用自体を保留**にする
   (現行Production[2.5-pro-preview-tts/3.1-flash-tts-preview]を継続、
   将来SDKが追随した時点で再検討)。
4. **現行の`build_tts_prompt`(Structured Separation、本文内delimiter)を
   維持したまま3.8系へモデルだけ差し替える**(前回AB-01と同じアプローチ、
   既にREJECTED方向の結果が出ている、再実施は非推奨)。

Fable/ユーザーの判断を仰ぐ。Sonnetの裁量で1・2以降へ自動的に進んでいない。

## §12 Production非変更の確認

- `er003_*`/`er006_*`/`er011_*`/`er012_*`等Production対象ファイルへの
  変更: **0件**。
- Production `.venv`・`.venv-ci`・`requirements-ci.txt`への変更: **0件**。
- 新規ファイルのみ: `er022_tts_gemini_3_8_flash_lite_next_trial_01_sdk_check.py`
  (Trial専用)、`er022_output/tts_gemini_3_8_flash_lite_next_trial_01/`
  配下(JSON/txtログのみ、音声ファイルは1つも生成していない)。
- `er005_output/cost_baseline_01/pricing_snapshot.json`: 新規4エントリの
  追加のみ、既存エントリは無変更(§5)。
- `.gitignore`: `.venv_trial*/`を追加(Trial隔離venvをリポジトリへ
  混入させないため)。
- API呼び出し: TTS/ASR課金API **0件**。HTTP GET(公式ドキュメント取得)は
  計画Docタスクで既に実施済み分のみ、本タスクでの追加GETは無し。

## §13 Git

対象: 本REPORT、`docs/pm/plan_...`は変更なし、
`er022_tts_gemini_3_8_flash_lite_next_trial_01_sdk_check.py`、
`er022_output/tts_gemini_3_8_flash_lite_next_trial_01/`配下(JSON/txt)、
`er005_output/cost_baseline_01/pricing_snapshot.json`、`.gitignore`。
`ACTIVE_TASK_FLT.md`/`RESULT_PACKET_FLT.md`・`.venv_trial_genai214/`は
commit対象外。
