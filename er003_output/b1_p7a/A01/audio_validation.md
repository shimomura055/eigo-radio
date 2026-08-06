# ER-003-B1-P7A 実行報告(Geminiモデル監査・3.1単一call限定検証)

## 1. P6Bの不合格理由

ユーザー試聴により、Stage 1(2-Macrochunk方式)は以下の理由で不合格と判定された。

- Macrochunk AとBで声質差があり、接続が不自然
- Macrochunk A冒頭「前半は激しい接触と緊張が続き」の「激しい」が
  「げきせつな」と誤発音された(従来「決勝→結晶」「歓喜→寒気」と
  同種のASR側の同音異義語の癖と誤って判断していたが、ユーザー実聴に
  より**TTS自体の誤発音**と判明)
- 独立したGemini TTS callを自然な連続ナレーションとして接続できなかった

Stage 2(英語Key Phrase置換)には進んでいない。詳細:
`er003_output/b1_p6b/A01/audio_validation.md` section22。

## 2. 現行モデルの監査結果

P4D・P6A・P6Bはいずれも同一の呼び出し経路を使用していた。

```
er002_gemini_client.make_tts_call_fn(voice_name)
  -> client.models.generate_content(model=er002_common.MODEL_NAME, ...)
```

`er002_common.MODEL_NAME`(er002_common.py:53)は以下の値で固定されている。

```python
MODEL_NAME = "gemini-2.5-pro-preview-tts"
```

このコード直上のコメントに「ER-001B-9/10・ER-002-S0の凍結仕様から
変更しない」と明記されており、P4D・P6A・P6Bのいずれの生成スクリプトも
このモジュール定数を上書きせず、`er002_gemini_client.make_tts_call_fn`を
そのまま呼び出していることをコード追跡で確認した(推測・ライブラリの
デフォルト値による判断ではない)。

| 対象 | 使用モデル呼び出し関数 | 実際に呼ばれるmodel引数 |
|---|---|---|
| P4D(`er003_v1_b1_p4d_generate.py:189`) | `gclient.make_tts_call_fn(p4d.VOICE_NAME)` | `common.MODEL_NAME` |
| P6A(`er003_v1_b1_p6a_generate.py:338`) | `gclient.make_tts_call_fn(p6a.VOICE_NAME)` | `common.MODEL_NAME` |
| P6B(`er003_v1_b1_p6b_stage1_generate.py:155`) | `gclient.make_tts_call_fn(p6b.VOICE_NAME)` | `common.MODEL_NAME` |

`gemini-2.5-pro-preview-tts`は`3.1`より前のモデルであるため、指示
section4「現行モデルが3.1未満の場合」に該当し、`gemini-3.1-flash-tts-preview`
による単一call検証を実施した。

## 3. 現行モデルIDの証拠

- コード証拠: `er002_common.py:53`(`MODEL_NAME = "gemini-2.5-pro-preview-tts"`)
- 呼び出し経路証拠: `er002_gemini_client.py:47-56`
  (`tts_call_fn`内で`model=common.MODEL_NAME`を無条件に使用)
- API疎通証拠: 実際にGemini Developer APIへ`client.models.list()`を
  実行し、このAPIキーに対して`models/gemini-2.5-pro-preview-tts`と
  `models/gemini-3.1-flash-tts-preview`の両方が存在・アクセス可能で
  あることを確認した(全58モデル中に完全一致)。
- 保存済みメタデータ: P4D/P6A/P6Bのいずれの`audio_metadata.json`にも
  モデルIDを記録するフィールドは存在しなかった(コードがAPIレスポンスの
  `model_version`を保存していないため)。この点はコード証拠とAPI疎通
  証拠で補った。

## 4. 使用SDK・API

| 項目 | 値 |
|---|---|
| API | Gemini Developer API(`genai.Client(api_key=...)`。Vertex AIではない) |
| SDK | `google-genai` |
| インストール済みバージョン(実環境確認) | `2.11.0` |
| 呼び出しメソッド | `client.models.generate_content(model=..., contents=..., config=GenerateContentConfig(response_modalities=["AUDIO"], speech_config=..., http_options=HttpOptions(timeout=150000)))` |

## 5. 3.1検証を実施したか

**実施した。** 現行モデル(`gemini-2.5-pro-preview-tts`)が3.1未満のため、
指示section4の分岐に従い`gemini-3.1-flash-tts-preview`による単一call
検証を実行した。

## 6. 使用入力とsha256

P4Dで生成した「英語5件を目印へ置換した直後」の漢字かな交じり原稿を、
一切変更せずに使用した。

| 項目 | 値 |
|---|---|
| 入力path | `er003_output/b1_p4d/A01/source/pattern_a_with_markers.txt` |
| sha256(P4D保存時点) | `a28f3cf892fce482d27b5c512be1a260ca305c286c7f6625fd68aff9a4193cd8` |
| sha256(P7A読み込み時点) | `a28f3cf892fce482d27b5c512be1a260ca305c286c7f6625fd68aff9a4193cd8`(**完全一致**) |
| 文字数 | 204 |
| 「目印」出現回数 | 5(想定通り) |

全文ひらがな版は使用していない。語句・句読点・ダッシュ・語順・文構造・
5つの「目印」・日本語表記のいずれも変更していない。

## 7. 実際のinstruction

P4D/P6A/P6Bと同一の`JAPANESE_STYLE_PREFIX`(`er003_b1_p4b_audio.
JAPANESE_STYLE_PREFIX` → 実体は`er003_b1_p3y_audio.
build_japanese_style_prefix()`が返す文字列)をそのまま再利用し、
一切変更していない。

- 保存先: `er003_output/b1_p7a/A01/source/instruction.txt`
- sha256: `fe683c89e7403bef36c4b79017d7ebd53242ec5d99e9047e4274bc8293138c73`
- 文字数: 2236

先頭行(言語指定): 「次の文章を、翻訳・言い換えせず、日本語のまま
読み上げてください。」

以降、Emotional+Connected/Level2相当の指示(自然な感情の起伏、章をまたぐ
連続性の維持、"Treat the narration as one continuous program, even when
it is generated in separate sections."を含む)は無変更。

実際にAPIへ送った完全なprompt(instruction + 入力原稿)は
`er003_output/b1_p7a/A01/source/full_prompt.txt`
(sha256: `658a9603857b8e43ec21a33ddf6c3a5cdf8571cf634ca780cc0dd864250d8899`)
に保存済み。

## 8. 実際の生成条件

| 項目 | 値 |
|---|---|
| Model | `gemini-3.1-flash-tts-preview` |
| Voice | Aoede(P4D/P6A/P6Bと同一) |
| Speaker | 単一 |
| chunk分割 | なし(全文を1回のTTS callで生成) |
| speed number | 指定なし |
| instruction | Emotional+Connected/Level2相当、無変更(section7参照) |
| technical retry | なし(`max_retry=0`) |
| 候補生成数 | 1件 |

旧API呼び出し(`er002_gemini_client.make_tts_call_fn`)と全く同じ呼び出し
形状(`response_modalities=["AUDIO"]`、`speech_config`、`http timeout`)を
維持し、`model`引数のみを`gemini-3.1-flash-tts-preview`へ差し替えた
(`er003_b1_p7a_audio.make_tts_call_fn_for_model`)。`er002_gemini_client.py`・
`er002_common.py`本体は変更していない(ER-002本編が依存する凍結仕様の
ため)。3.1対応にあたり、呼び出し形状自体の変更は不要だった(型エラー・
非対応パラメータは発生しなかった)。

## 9. TTS call回数

**1回。** 初回で成功し、retryは発生しなかった(`retry_count=0`)。

## 10. raw音声の場所

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p7a/A01/raw/A01_p7a_gemini31_single_call.wav` |
| sha256 | `30162196543087ce2a0a5e15e1f0e12b8caf65f57f51345128e2a06beab1d22b` |
| 長さ | 39.84秒 |
| clipping | 検出なし |

**注意**: `.wav`ファイルは`.gitignore`の`*.wav`ルールによりリポジトリ
には含まれていない(このプロジェクト全体で一貫した運用)。ローカル
ファイルとして存在するので、ユーザーが直接再生する必要がある。

## 11. 重点語句ごとのASR診断

Azure STT(ja-JP、連続認識)によるASR結果(全文):

> 前半は激しい接触と緊張が続き、両チームとも枠内シュート目印を記録できないまま静かな均衡が保たれます。後半に試合が動くと、イングランドは選手を交代で下げる目印という決断で守備を固め、わずかなリード目印を守ろうとします。アルゼンチンの結晶への道を閉ざすこと。目印が現実になりそうなその時。メッシが流れを変え、ついにアディショナルタイム目印へ。最後の数分、寒気と痛みの境目で何が起きるのでしょうか。

重点語句(指示section8)の検出結果:

| 重点語句 | 検出 |
|---|---|
| 激しい接触 | **検出**(P6Bで「げきせつな」と誤発音された箇所。今回はASR上、正しい形で検出された) |
| 枠内シュート | 検出 |
| 選手を交代で下げる | 検出 |
| 目印という決断で | 検出 |
| 守備を固め | 検出 |
| わずかなリード | 検出 |
| 最後の数分 | 検出 |
| 何が起きるのでしょうか | 検出 |
| 「目印」出現回数 | 5(想定通り) |

**全重点語句が検出された。** ただし指示section8の明記通り、これは
ASRのテキスト一致であり、実際の発話品質(自然さ・アクセント・
誤発音の有無)は保証しない。特に「激しい接触」はASR上の文字列としては
正しく検出されたが、**実際の音声としての自然さ・正しい発音かどうかは
ユーザー試聴でのみ判定できる**(P6Bでも、「激折な」というASR書き起こし
だけを見て「軽微なASR誤変換」と誤判断した前例があるため、テキスト
一致のみでの合格判定はしない)。

## 12. 全文の疑わしい差分

`difflib.SequenceMatcher`による入力原稿とASR結果の全文比較
(類似度スコアのみでの合否判定はしていない)。

| 種別 | 入力側 | ASR側 | 備考 |
|---|---|---|---|
| delete | 、(4箇所) | (なし) | 読点。Azure STTは通常句読点を書き起こさないため想定内 |
| replace | ―― | 。 | ダッシュ。同上、想定内 |
| delete | ―― | (なし) | 同上 |
| replace | 、 | 。 | 同上 |
| replace | **決勝** | **結晶** | 同音異義語(けっしょう)。過去のP6B等でも繰り返し出現したパターン |
| replace | **歓喜** | **寒気** | 同音異義語(かんき)。同上 |

similarity_ratio: 0.95

**重要な注意**: 「決勝→結晶」「歓喜→寒気」は、これまで一貫して
「ASR側の同音異義語の癖」と説明してきたパターンと一致する。しかし
P6Bで「激しい→激折な(げきせつな)」を同様に「ASR側の癖」と誤判断した
結果、実際にはTTS自体の誤発音だったことが後日ユーザー試聴で判明した
という前例がある。**したがって本報告でも、この2箇所をASR側の癖と
断定せず、ユーザー試聴での確認が必要な項目として扱う。**

原稿内語句の脱落・原稿外語句の追加・語順の変更は検出されなかった。

## 13. 機械QA結果

| 項目 | 結果 |
|---|---|
| 実際のモデルIDが`gemini-3.1-flash-tts-preview` | 合格(コード経路+API疎通確認で証明) |
| 入力が保存済み原稿と完全一致 | 合格(sha256完全一致) |
| TTS callが1回 | 合格 |
| chunk分割なし | 合格 |
| voiceがAoede | 合格 |
| instructionが既存条件と同等 | 合格(P4D/P6A/P6Bと同一オブジェクトを再利用) |
| raw音声が正常に生成・decode可能 | 合格 |
| clippingなどの重大なファイル異常がない | 合格(clipping未検出) |
| 重点語句のASR診断が保存されている | 合格 |

**機械QAは全て合格した。ただし、指示section9の明記通り、これは音声
品質(自然さ・声質の連続性・「激しい」の正しい発音かどうか)の承認を
意味しない。合否は指示section10〜11のユーザー試聴確認を経て確定する。**

## 14. 作成・変更したファイル

- `er003_b1_p7a_audio.py`(新規): モデル監査定数、モデル差し替え版
  `tts_call_fn`、重点語句チェック、全文diff。`er002_gemini_client.py`・
  `er002_common.py`は変更していない(凍結仕様のため)
- `er003_v1_b1_p7a_generate.py`(新規): P7Aオーケストレーションscript
  (モデル監査→入力準備→TTS生成→ASR診断)
- `er003_test_b1_p7a_audio.py`(新規、9件、実API呼び出しなし)
- `er003_output/b1_p7a/A01/`配下の成果物一式
  (`audit/model_audit.json`、`source/input_text.txt`・
  `input_hashes.json`・`instruction.txt`・`full_prompt.txt`、
  `raw/A01_p7a_gemini31_single_call.wav`、
  `asr/asr_transcript.txt`・`key_expression_check.json`・
  `diff_report.json`)

## 15. テスト結果

- `er003_test_b1_p7a_audio.py`(新規9件、実TTS/ASR呼び出しなし): 全合格
- プロジェクト全体回帰テスト(`run_project_regression.py`、
  er0*_test_*.py全探索): **1575件全合格、回帰なし**

## 16. 再実行方法

```
.venv/Scripts/python.exe er003_v1_b1_p7a_generate.py
```

## 17. 既知のリスク

- 機械QA(モデルID・入力一致・ASRテキスト一致)は全て合格したが、
  これは音声品質・自然さ・「激しい」の正しい発音の保証ではない。
  ユーザー試聴が必須。
- 「決勝→結晶」「歓喜→寒気」の2箇所は、過去に「ASR側の癖」と誤判断
  した前例があるため、今回も断定していない。ユーザー試聴で明示的に
  確認する必要がある。
- 3.1モデルでも、P4Dと同様の全文一括生成のため、原稿内語句の省略・
  声質の不連続が別の形で発生している可能性はASRだけでは検出できない。
- 指示section7により、分割方式・marker処理の再調整、Stage2相当の
  英語置換、他エンジン(Polly/Azure Speech/Neural2/ElevenLabs)、
  MFA、Dynamics3、B1本文生成は一切実施していない。

## 18. Git status

このレポート作成時点では未コミット。P7A関連ファイルのみをステージして
コミットします。

## 19. push

実行していません。

---

## ユーザーへの確認事項

以下の音声を試聴し、指示section10の項目をご確認ください。

- [A01_p7a_gemini31_single_call.wav](raw/A01_p7a_gemini31_single_call.wav)
  (gemini-3.1-flash-tts-preview、単一call、全文39.84秒)

**原稿忠実性**: 「激しい」が正しく発話されるか / 「選手を交代で下げる」
「目印という決断で」が省略されないか / 「守備を固める」へ変更されて
いないか / 「最後の数分」「何が」が正しく発話されるか / その他の欠落・
追加・言い換えがないか。

**音声品質**: 日本語のアクセント・イントネーションが自然か / 声質が
全文を通して連続しているか(今回は単一callのため、Macrochunk間の接続
という問題自体は原理的に発生しない点にご留意ください) / 機械音声感が
強くないか / Previewとして許容可能か。

機械QAは全て合格していますが、「品質合格」「自然さ確認済み」とは
判断していません。指示section12の分岐に従い、ご判断の結果をお知らせ
ください。
