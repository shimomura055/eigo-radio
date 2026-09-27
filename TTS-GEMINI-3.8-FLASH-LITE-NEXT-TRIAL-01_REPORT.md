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

## §12 補足調査(SDK最新版・REST経路、2026-09-27)

本節はすべてread-only HTTP GETのみで実施(TTS/ASR課金API呼び出し0件、
実費用¥0)。`.venv_trial_genai214`への**インストールは行っていない**
(委任文の明示指示どおり、`pip index versions`によるクエリのみ、既存の
`google-genai==2.14.0`のまま無変更。確認コマンド`pip show google-genai`
実行結果: `Version: 2.14.0`のまま)。

### §12.1 PyPI公開バージョン一覧(2.14.0より新しい版の有無)

`.venv_trial_genai214`のpipで`pip index versions google-genai`実行
(2026-09-27 05:02 UTC)。結果: **2.14.0より新しい版が11件存在**
(INSTALLED: 2.14.0、LATEST: 2.25.0)。PyPI JSON API
(`https://pypi.org/pypi/google-genai/json`、取得日時2026-09-27 05:02 UTC)
による各バージョンの公開日時(`upload_time_iso_8601`):

| version | upload_time (UTC) |
|---|---|
| 2.14.0(Trial導入版) | 2026-07-22T21:35:42Z |
| 2.15.0 | 2026-07-29T17:43:20Z |
| 2.16.0 | 2026-07-30T14:34:35Z |
| 2.17.0 | 2026-08-06T05:10:39Z |
| 2.18.0 | 2026-08-13T00:12:51Z |
| 2.18.1 | 2026-08-13T22:13:48Z |
| 2.19.0 | 2026-08-19T23:05:41Z |
| 2.20.0 | 2026-08-25T21:28:25Z |
| 2.21.0 | 2026-08-31T21:49:12Z |
| 2.22.0 | 2026-09-02T18:06:00Z |
| 2.23.0 | 2026-09-10T22:55:29Z |
| 2.24.0 | 2026-09-16T22:38:35Z |
| 2.25.0(最新) | 2026-09-22T17:22:59Z |

### §12.2 CHANGELOG.md(googleapis/python-genai)の`speech_metadata`関連記述(逐語引用)

出典: `https://raw.githubusercontent.com/googleapis/python-genai/main/CHANGELOG.md`
(取得日時2026-09-27 05:03 UTC、HTTP 200)。

**該当あり**。バージョン`2.25.0`(2026-09-22公開、リポジトリの
Compareリンク`https://github.com/googleapis/python-genai/compare/v2.24.0...v2.25.0`)
のFeatures節に、以下の逐語記述:

> `## [2.25.0](https://github.com/googleapis/python-genai/compare/v2.24.0...v2.25.0) (2026-09-22)`
>
> `### Features`
>
> `* Expose SpeechMetadata, VoiceConfig.voice, and SpeechAnnotation in public GenAI SDKs ([a6d3243](https://github.com/googleapis/python-genai/commit/a6d32434b848ada0a635dae38406811dbf4a7c67))`

(同じFeatures節に`Add sample_audio to Voice in GAOS SDK`
`Add Voices API resource to GAOS SDK`
`Wire voice into sdk`等、関連機能追加も並記されている。)

`2.14.0`〜`2.24.0`のChangelogエントリ内には`speech_metadata`/
`SpeechMetadata`の文字列は出現しない(`grep -in`でCHANGELOG全文
2,207行を検索、`2.25.0`エントリの上記1箇所のみがヒット)。

**解釈(推測ではなく上記引用に基づく事実関係の整理)**: 本Trial
(Phase 0)がSDK 2.14.0で確認した「GenerateContent APIの`types.Part`が
`speech_metadata`フィールドを持たずpydanticが`extra_forbidden`で
拒否する」という制約は、2.25.0のこのChangelogエントリの内容
(「SpeechMetadataを公開SDKへexposeした」)と符合する。すなわち、
`speech_metadata`自体はより新しいバージョンのSDKで型定義として
追加されている可能性が高い(§12.4のREST側裏付けと合わせて記録、
ただし2.25.0を実際にインストールして検証してはいないため、
「動作する」との断定はしていない)。

### §12.3 REST APIリファレンス(`ai.google.dev/api/generate-content`)の記載(逐語引用)

出典: `https://ai.google.dev/api/generate-content`(取得日時2026-09-27
05:04 UTC、HTTP 200)。

**該当あり**。`Part`型のJSON representationセクションに、`text`と
並ぶ**sibling field**として`speechMetadata`が明記されている(逐語、
HTML構造上のプロパティ列挙。委任文の「(Interactions APIの)
contentのsibling fieldとして`speech_metadata`を直接置いた場合」の
実験と同じ形状が、実は**GenerateContent APIのPart型自体に正式に
存在する**ことが分かった):

```
"speechMetadata": {
    object (SpeechMetadata)
},
// data
"text": string,
```

`Part.FIELDS.speech_metadata`セクションの説明文(逐語):

> `Optional. Metadata applied to text parts to customize how they should be spoken or synthesized, such as specifying speaker identity or speaking style.`

`SpeechMetadata`型自体の定義(逐語):

> `Speech metadata for text parts.`
>
> フィールド: `speaker`(`string`、`Optional. Optional speaker name
> for multi-speaker synthesis.`)、`style`(`string`、`Optional. Optional
> style instruction for the speech synthesis.`)

JSON representation(逐語):
```
{
  "speaker": string,
  "style": string
}
```

**解釈**: REST API仕様上は、`speechMetadata`(camelCase)は
GenerateContent APIの`Part`のフィールドとして**公式に定義されている**
(Interactions APIの`annotations`配列を経由する形とは別に、
GenerateContent API自体にもこのフィールドが存在する)。Phase 0で
`types.Part(text=..., speech_metadata=...)`が即座に
`pydantic.ValidationError(extra_forbidden)`になったのは、
サーバ側/REST仕様の問題ではなく、**2.14.0時点のPython SDK側の型定義
(pydanticモデル)がこのフィールドをまだ持っていなかったこと**が
直接の原因であったことが、この一次資料により裏付けられた。

### §12.4 公式ガイド(`gemini-api/docs/speech-generation`)側の記載

出典: `https://ai.google.dev/gemini-api/docs/speech-generation`
(取得日時2026-09-27 05:04 UTC、HTTP 200)。

このガイド内の実行例(JSON/Python/JavaScript)はいずれも
**Interactions API形式(`annotations: [{"type": "speech_metadata",
"style": "..."}]`)のみ**を示しており、GenerateContent APIの
`Part.speechMetadata`(§12.3)を直接使う例は本ガイド内には無い
(見出し`Control speech style with metadata and tags`配下、逐語:
`Gemini 3.8 TTS treats the text field strictly as a verbatim
transcript. To control delivery without having stage directions read
aloud, split your instructions by scope:`)。

**未確認事項として残るもの(推測で埋めない)**: GenerateContent API
経由で`Part.speechMetadata`を直接使う具体例・挙動は、本Trialで
参照した2つの一次資料(REST APIリファレンス・speech-generation
ガイド)のどちらにも実行例が無く、未確認。§12.2のSDK
Changelog(2.25.0で「公開SDKへexpose」)と§12.3のREST定義の存在は
確認できたが、**2.25.0を実際にインストールして
`client.models.generate_content`経由で送信できるかどうかの実機検証は、
本Trialでは行っていない**(委任文の「インストールはしない」指示に
従ったため)。

## §13 Fable評価(2026-09-27)

Status: `USER_DECISION_REQUIRED`(Stage 1未着手、TTS課金¥0、
Cap ¥500未消費)。SDK制約の発見時点でSTOPした判断は委任条件どおりで
適切。隔離環境で既存TTS関連テスト264件超がPASSしたことにより、
Production `.venv`無変更は確認済み。

§12の補足調査により、当初§10で「未確認」としていた事項の一部に
新しい事実(推測ではなく一次資料の逐語引用)が加わった: (1) SDKには
2.14.0より新しい版が11件存在し、うち2.25.0(2026-09-22公開)の
Changelogに「SpeechMetadataを公開GenAI SDKへexposeした」という
直接該当する記述がある。(2) REST APIリファレンス自体には、
GenerateContent APIの`Part`型の一部として`speechMetadata`
フィールド(`speaker`/`style`)が公式に定義されている。これらは
Phase 0で発見された制約(2.14.0のSDK型定義に`speech_metadata`が
存在しない)が、サーバ/仕様側の欠落ではなくSDKのバージョン遅れに
起因していた可能性を示す一次資料上の裏付けであり、2.25.0を
実際にインストールして動作確認しない限り「解決した」とは断定
できない(§12.4参照、実機検証は本タスクの範囲外[インストール禁止]
のため未実施)。

次の一手はユーザー判断(選択肢: 新SDK版[2.25.0]をTrial環境
[`.venv_trial_genai214`とは別の新規Trial venv、または既存を複製]へ
導入して実機再確認する/RESTでの直接送信をTrial限定で試す/保留)。
Fable推奨は、§12の一次資料(Changelog・REST定義双方が2.25.0での
対応を示唆)を踏まえ、**選択肢2(新SDKバージョンをTrial限定で導入し
GenerateContent API経由での実機確認を行う)を次のTrial候補として
優先度高く提示する**。ただし実装はユーザー承認後に行う(Sonnetの
裁量では実施していない)。

pricing_snapshot.jsonへの公式単価追加は追加のみで既存エントリ無変更を
確認(Gate上の副作用なし)。
