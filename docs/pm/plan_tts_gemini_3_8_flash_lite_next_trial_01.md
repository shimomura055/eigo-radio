# TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-PLAN-01 計画doc

管理ID: `TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-PLAN-01`
性質: **計画作成のみ**。本タスクではTTS/LLM API呼び出しは一切行っていない
(実費用¥0)。実際のTrial実行は本計画のユーザー承認後、別の管理IDで行う。
到達Status: `TRIAL_PLAN_READY`(§10参照)。

参照した公式一次情報(すべてHTTP GET、検索API不使用):
- `https://ai.google.dev/gemini-api/docs/pricing`(取得: 2026-09-27 04:11 UTC)
- `https://ai.google.dev/gemini-api/docs/speech-generation`(取得: 2026-09-27
  04:11 UTC、ページ内`Last updated 2026-09-24 UTC.`)
- `https://ai.google.dev/gemini-api/docs/models`(取得: 2026-09-27 04:11 UTC)
- `https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash-lite-tts`
  (取得: 2026-09-27 04:16 UTC、ページ内`Last updated 2026-09-24 UTC.`)
- `https://ai.google.dev/gemini-api/docs/rate-limits`(取得: 2026-09-27 04:17
  UTC、モデル別RPM/TPM表はJS動的レンダリングのため静的HTMLからは**未確認**)

## §1 現行TTSとの差(公式ドキュメント逐語引用ベース)

### 1-1 APIスキーマそのものが変わっている(最重要の発見)

現行Production(`er003_b1_p7a_audio.make_tts_call_fn_for_model`)は、
`client.models.generate_content(model=..., contents=prompt, config=GenerateContentConfig(response_modalities=["AUDIO"], speech_config=...))`
という旧来のGenerateContent APIを使い、`prompt`は
`er003_b1_p4c_audio.build_tts_prompt(text, style_prefix)`が組み立てた
**単一の文字列**(Structured Separation、`=== STYLE INSTRUCTIONS ===`/
`=== TEXT TO SPEAK ===`区切り)である。

公式ガイド(speech-generation)は、Gemini 3.8系TTSモデル向けの主経路として
**Interactions API**(`client.interactions.create()`)を前提に書かれており、
以下を逐語引用する:

> "Gemini 3.8 TTS treats input text strictly as a verbatim transcript. Move
> sustained delivery instructions (`style`—such as `"whispering"`,
> `"out of breath"`, or `"speaking slowly"`) and speaker labels (`speaker`)
> into structured `speech_metadata` annotations rather than embedding stage
> directions in the transcript text."

> "Gemini 3.8 TTS models treat input text strictly as a verbatim transcript.
> Unlike earlier preview models where stage directions were embedded in
> plain text, Gemini 3.8 TTS separates sustained turn-level directions
> (`speech_metadata`) from point-in-time inline vocal tags."

つまり、現行Productionが使うStructured Separation(「本文の中にdelimiterで
区切ったstyle指示を混ぜ、`text`部分だけを読め」という**テキスト内表現による
分離**)は、Gemini 3.8系モデルの公式設計思想そのものと矛盾する。公式は
「`text`(transcript)は一切合切そのまま読み上げられる」ことを前提にしており、
style/speaker指示は**API呼び出しの構造化フィールド**(`speech_metadata`)へ
完全に外出しすることを要求している。

modelページ(`.../models/gemini-3.8-flash-lite-tts`)の移行ガイドには、
GenerateContent APIを使い続ける場合の対応も明記されている(逐語):

> "GenerateContent API: Attach `"speech_metadata": {"speaker": "...",
> "style": "..."}` to each `part`."

これは現行呼び出し形状(`client.models.generate_content`)を維持したまま、
`contents`を単一文字列ではなく`speech_metadata`付きの`part`として渡す形に
変更すれば済む可能性を示す一文だが、**コード例は提供されておらず
(このmodelページの移行ガイド1文のみで、speech-generation本編には
GenerateContent API自体の記載が一切ない)、Python SDK(`google-genai`)の
現在インストール済みバージョン(2.11.0、後述)でこの`part.speech_metadata`
フィールドが型定義として存在するかは未確認**(`types.Part.model_fields`に
`speech_metadata`という名前のフィールドは無く、`part_metadata`という別用途
[任意カスタムmetadata、音声合成とは無関係]のフィールドのみ存在することを
実機`.venv`で確認した)。dictを直接渡して動くかは、実際にAPIを呼ばない限り
確認できない(本計画では未実施、Trial実行時の最初の検証項目とする)。

### 1-2 Interactions API自体はインストール済みSDKで型定義が存在する

`.venv`(`google-genai==2.11.0`、`requirements-ci.txt`記載の2.14.0とは
バージョンが不一致であることも本調査で判明、**未確認の齟齬として記録**)を
実機で確認したところ、`client.interactions`プロパティ、および
`google.genai.interactions`モジュール配下に`Interaction`/
`InteractionCreateParams`/`CreateModelInteractionParam`/`TextContentParam`
(`annotations: List[AnnotationParam]`フィールドを持つ)/`SpeechConfigParam`
(`voice`/`speaker`/`language`)/`GenerationConfigParam`
(`speech_config: List[SpeechConfigParam]`)/`AudioResponseFormatParam`
(`mime_type`/`sample_rate`/`bit_rate`)が実在することを確認した。

ただし、レスポンス解析用の`Annotation`(Union型)は現バージョンでは
`url_citation`/`file_citation`/`place_citation`のみが列挙されており、
`speech_metadata`という名前のvariantはまだ型として明示されていない
(`AnnotationParam`という入力用TypedDict側は型検証が緩い可能性があるが、
実際にdictを送って受理されるかは**未確認**)。公式ドキュメントのコード例
(`"type": "speech_metadata", "style": "cheerful and friendly"`)通りの
dictをそのまま渡して動くかどうかは、Trial実行時の最初の最小1呼び出しで
確認すべき最優先項目である。

### 1-3 デフォルトの音声フォーマットが変わっている

公式(modelページ移行ガイド、逐語):

> "Unlike `gemini-3.1-flash-tts-preview` and earlier TTS models (which
> returned headerless raw PCM `audio/l16` by default), Gemini 3.8 TTS
> returns WAV audio (`audio/wav`) with a standard RIFF header by default
> for unary requests."

現行Production(`er002_common.pcm_bytes_to_float_mono`)は、受け取ったbytes
を**ヘッダ無しの16bit生PCMと無条件に仮定**して`np.frombuffer(..., dtype=np.int16)`
で変換している。Gemini 3.8系モデルがWAVヘッダ(44byte RIFF)付きで返す場合、
先頭44byte(=22サンプル、24kHzで約0.9ms)がノイズとして誤読される
(影響は理論上ごく僅かだが、正しくは`response_format`を明示的に
`"audio/l16"`/`"AUDIO_L16"`に指定するか、返ってきたbytesの先頭が`RIFF`
マジックバイトかどうかを検出してヘッダを除去すべき)。前回Trial(AB-01)の
17segment中3件がASR PASSした事実(§2参照)から、この差分が仮に発生して
いたとしても実害は無かったと推測されるが、**「response_formatを明示指定
すべき」という公式仕様自体は前回Trialでは未対応だったため、次回は明示的に
対応する**(推測ではなく公式記載に基づく対応)。

### 1-4 Voice名・言語カバレッジは互換

公式Voice options一覧(speech-generation guide)に、現行Production使用中の
`Charon`/`Kore`/`Aoede`/`Algieba`/`Erinome`/`Schedar`が確認できた
(prebuilt voice名として引き続き有効)。`gemini-3.8-flash-lite-tts`の
modelページはSupported languagesとして101言語(英語・日本語含む)を挙げて
おり、現行使用言語(英語/日本語)は両方サポート範囲内。

### 1-5 Input/Output token上限

modelページ(逐語): "Input token limit: 8,192" / "Output token limit:
16,384 (Gemini API serving limit)"。Audio token換算は"25 tokens per second
of audio"(pricingページ脚注)。よって理論上の最大出力音声長は
16,384 / 25 = **655.36秒**(約10分55秒)。前回Trialの最悪ケース
(point_one/two: 標準経路で無関係な長時間音声を生成、既存
`detect_duration_anomaly`が作動)は、この理論上限の範囲内で起こり得る規模
であることと整合する。

### 1-6 モデルのStatus

`docs/models`一覧で`Gemini 3.8 Flash-Lite TTS`は"New"/"Stable"表示
(Previewではない)。対して現行日本語model`gemini-3.1-flash-tts-preview`は
同ページで"Legacy TTS preview model. We recommend updating to Gemini 3.8
Flash TTS or Gemini 3.8 Flash-Lite TTS."と明記されている(公式が明示的に
移行を推奨している状態)。

## §2 前回失敗原因の仮説(事実ベース)

前回REPORT(TTS-GEMINI-3.8-FLASH-LITE-AB-TRIAL-01)の症状:
(a) 指示文(delimiter文言含む)をそのまま読み上げる、(b) 短いJA Commentは
成功率が高いが長文英語segmentほど無関係な内容を生成(hallucination)、
(c) 17segment中14がSTOPPED。

公式ドキュメントに基づく仮説(§1-1と直結):
**Gemini 3.8系モデルは「入力textは一字一句そのまま読み上げるverbatim
transcriptである」という前提で設計されており、style指示は本文と混ぜず
構造化フィールド(`speech_metadata`)で渡すことを公式に要求している。前回
TrialはこのAPI設計変更を認識せず、旧世代モデル(`gemini-2.5-pro-preview-tts`
/`gemini-3.1-flash-tts-preview`)向けに検証済みのStructured
Separation(本文内delimiter方式)をそのままモデル差替えだけで流用した。
その結果、モデルは「delimiter文言を含む全体を読み上げるべきtranscript」
として扱い、指示文自体を発話した(症状a)。加えて、本文が長く指示文も
含む長大な単一テキストになるほど、モデルが混乱し無関係な内容を自由生成
する頻度が上がった(症状b/c)という関連が観察と整合する。** これは
断定ではなく、公式ドキュメントの記述と前回症状の整合性から導いた仮説で
あり、実際に検証(次回Trial)するまでは確定しない。

副次的仮説(§1-3、影響は軽微と推測): デフォルト音声フォーマット変更
(WAV化)への未対応。前回3件成功があった事実と整合するため、主要因では
ないと考えるが、正しい対応はしていなかった事実として記録する。

## §3 新Trialで何を変えるか

1. **style/speaker指示の外出し**: `er003_b1_p4c_audio.build_tts_prompt`
   (本文内delimiter方式)を、Trial専用の新しい呼び出し経路に限り使わず、
   `speech_metadata`(GenerateContent API経由の`part.speech_metadata`案、
   またはInteractions API経由の`annotations`案、いずれもTrial実行時に
   実機で先に検証)へ置き換える。**本文(`text`)自体の文言は一切変更
   しない**(既存canonical本文をそのまま使う、ER-005の「内容は変えず
   区切り方だけ変える」という原則を、区切り方の実装先が変わっても踏襲する)。
2. **style文言そのものの簡略化(ユーザー方針)**: 現行Production
   (`A2_ENGLISH_STYLE_PREFIX_SLOWER`等)の詳細な指示文をそのまま移植せず、
   まず`natural, clear, conversational`程度の簡潔な`style`値、または
   公式ガイド推奨の「まずstyle無し(空)で試す」("Test plain TTS first:
   Synthesize your transcript with an empty style field first—most
   requests need no style instruction at all.")を先に試す。段階的に
   `casual, friendly`程度の短い調整を追加する(公式ガイドの推奨手順
   "Add short style prompts only for tweaks"に従う)。
3. **音声フォーマットの明示指定**: 可能なら`response_format`(または
   相当するconfig)を明示的に`audio/l16`(24kHz raw PCM)へ指定し、既存の
   `pcm_bytes_to_float_mono`との前提を一致させる。指定できない/未対応の
   場合は、受け取ったbytesの先頭が`RIFF`マジックバイトかを検出し
   ヘッダを除去してから渡す防御的処理を追加する。
4. **pricing_snapshot.jsonへの公式単価登録**(実装のみで実行はまだしない、
   §9参照): 前回はproxy rate(近縁モデル代用)だったが、今回は
   `gemini-3.8-flash-lite-tts`の公式単価が確認できたため正確な計算が可能。

## §4 何を変えないか

- **Voice**: Charon/Aoede/Algieba/Erinome/Schedar(現行と同一、公式Voice
  optionsに実在確認済み)。
- **ASR検証**: 変更しない。Primary ASR routing
  (`er006_asr_provider_routing_01.transcribe`)、英語6分類Validator
  (`er006_preprod_hardening_01_validation.classify_asr_match`)、日本語
  5分類Validator(`er007_ja_asr_validator_01.classify_ja_asr_match`)、
  Secondary ASR Cascade、Pronunciation Ledger運用は全て既存のまま再利用。
- **retry上限**: 標準2回+fallback1回=合計3回(`er011_human_review_lock_01
  .PRODUCTION_MAX_TTS_ATTEMPTS`)を変更しない。新Trial呼び出し関数も
  この上限を独自に緩めない(前回のTrialも遵守していた)。
- **異常長検知(duration anomaly detector)**: `er003_audio_tts_asr_safety
  .detect_duration_anomaly`/`estimate_max_reasonable_duration_seconds`
  (英語1.5秒/語+4秒、日本語1.2秒/文字+3秒の上限見積り、ASR前に破棄)は
  そのまま再利用する。新規実装しない。
- **repetition QA/disfluency QA/connected speech equivalence layer/6%
  slowdown post-process**: 既存関数をそのまま呼び出す(前回Trialと同じ
  方式、Production関数の中身は一切変更しない)。
- **Production本体ファイル**: `er003_*`/`er006_*`/`er011_*`/`er012_*`等は
  無変更。新Trialは前回同様、独立したTrial専用スクリプト(新規er0NN番号、
  実装時に採番)+専用`out_dir`(`er0NN_output/...`)を使い、
  `er003_b1_p9a_audio.ENGLISH_MODEL_NAME`/`JAPANESE_MODEL_NAME`を
  with文内でのみ一時上書きする既存パターン(前回er022と同型)を踏襲する
  か、もしくは呼び出し形状そのものが変わる(part単位でspeech_metadataを
  渡す)ため、新たな独立`tts_call_fn`をTrial専用モジュール内に用意する
  (どちらを取るかはTrial実装時、既存`generate_a2_segment_with_slowdown`
  等の内部で`build_tts_prompt`を直接呼んでいる箇所を確認した上で判断する。
  本計画では方針のみ示し、コード変更は行っていない)。

## §5 代表segment候補(既存完成音声から、根拠付き、最終選定はユーザー)

対象article/canonicalは前回Trialと同一(`er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/kp_fix_01/a2/`)を引き続き使う(既存完成音声=A側との直接比較可能性を保つため)。`parts.json`を確認したところ、
**この記事の全segmentに数字(算用数字)は1つも含まれていない**(CEFR-A2
のため数字表現自体を避けている可能性がある、実際に`re.search(r"\d", v)`
で全文検索し0件)。よって「数字を多少含む」候補は本記事内には無く、
「固有名詞」側のみで評価する。

| 候補 | 根拠 |
|---|---|
| **tension_reflection**(英語、Aoede、A実測62.25秒) | 唯一の固有名詞「New York City」を含む(法規制の文脈での言及)。前回Trialでrepetition/connected-speech QA対象外のシンプルなQA経路。**前回B側が3/3attempt全てTRUE_CONTENT_MISMATCH(無関係な創作内容)で最も重度に失敗したsegment**であり、根本原因(§2の仮説)を修正した場合に真っ先に改善が確認できるはずの回帰チェックとして最適。文字数850(今回対象中最長)。 |
| **full_story_part1**(英語、Aoede、A実測15.01秒) | 名称が文字通り「Full Story」であり、ユーザーが求める「Full Story等でEYW通常品質が分かる」を直接満たす。長さは中庸(短すぎない)。repetition QA・connected speech equivalence layerが有効な経路(前回と同じ)。固有名詞は含まないが、通常のNarrator読み上げ品質の基準点になる。 |
| **point_two_body**(英語、Erinome[Voice B]、A実測44.06秒[trim後]) | 3 Voices記事固有のキャラクター読み上げ(Narrator以外)の代表。ビジネス文脈の内容(「公式通知」等)でNarrator以外のvoiceでの相性も確認できる。固有名詞は含まないが、長さは中庸〜長め。 |

推奨する段階1(単一代表segment)の第一候補は**tension_reflection**
(理由: 前回の最悪失敗ケースの直接的な再検証になり、固有名詞を含む唯一の
segmentであるため)だが、最終選定はユーザーが行う。

## §6 Prompt・metadata方針(公式仕様ベース、具体案)

段階的に試す(公式ガイド"Recommended workflow"に準拠):

1. **Step A(style空)**: `speech_metadata`の`style`を付けない、または
   空文字列。本文(`text`)は既存canonical本文をそのまま(delimiterなし、
   verbatim)。
2. **Step B(簡潔style)**: Step Aで自然さが不十分な場合のみ、
   `style: "natural, clear, conversational"`程度の短い文字列を追加。
   ユーザー方針に基づく候補語彙: `natural`/`clear`/`conversational`/
   `easy to follow for English learners`。**`theatrical`や過度な
   感情指示、`speak slowly`のような明示的ペース指示は含めない**
   (ユーザー方針「不自然にslowにしない/theatricalにしすぎない」、および
   公式ガイド「Long-form "Audio Profile"/"Director's Notes"は voice
   driftの最大要因」という注意書きとも整合)。
3. **ポーズ**: 公式は文中の`<short pause>`/`<long pause>`インライン
   タグ、または句読点・省略記号(`...`)による自然な間を推奨。既存
   Productionのsegment間ポーズ(`PAUSE_AFTER_*_SECONDS`等、Assembly時の
   無音挿入)は変更しない(そちらはsegment間の話であり、公式ガイドの
   `<pause>`はsegment内部の話で別レイヤー)。
4. **speaker**: 現行は1 segment=1 voice=1 API呼び出し(3 Voicesは別々に
   生成)なので、公式の"multi-speaker requires speaker on every turn"は
   非該当(現行方式は単一話者呼び出しの繰り返しであり、multi-speaker
   turn機能は使わない、変更不要)。

## §7 ASR確認方法(変更なし)

既存Primary ASR(OpenAI `gpt-4o-mini-transcribe`)→必要時Secondary ASR
Cascade(Azure)、英語6分類/日本語5分類Validatorをそのまま使う。追加で、
**「本文外発話」検知**を明示チェック項目として追加する(新規実装ではなく
既存分類の解釈強化): ASR結果が`TRUE_CONTENT_MISMATCH`に分類され、かつ
ASRテキストにcanonical本文の主要語がほぼ含まれない場合、既存の
「無関係内容生成」への該当として扱い、既存retry上限(3回)以上は絶対に
追加生成しない(前回と同じ運用、変更なし)。

## §8 音質評価方法

前回同様、segment別A/B比較player(`player.html`、mp3実体つき)を専用
`out_dir`配下に生成する。**この段階ではSonnet/Fableによる自動チェック
(ASR PASS・異常長なし・本文外発話なし)を優先し、人間の試聴が必要と
判断された場合のみ、ユーザーへ試聴依頼を行う**(`docs/pm/PM_GOVERNANCE.md`
14節の7段階、および9-5の「クリックできるArtifact/playerリンク必須、
ローカルpath不可」に従う。ローカル出力のみの段階では、ユーザーへ試聴を
求める報告はしない)。

## §9 latency

前回実測: B(旧アプローチ)は17segment合計で約795秒(A比較 約2.2倍)。
今回は"Flash-Lite"という名称通り低latency設計のモデルであり、かつ
不要な長文instruction混在テキストを送らなくなる(本文のみのverbatim
transcriptになる)ため、input token数自体が減り、応答時間が短縮される
可能性がある(**未確認、推測に留める、実測はTrial時**)。段階1
(1 segment)での実測latencyを最初のGoサイン判断材料の一つとする。

## §10 cost(公式単価に基づく試算)

公式pricing(`https://ai.google.dev/gemini-api/docs/pricing`、
2026年12月31日までの現行レート、取得日2026-09-27):

| 項目 | Standard tier | Batch tier |
|---|---|---|
| Input(text) | $0.50 / 1,000,000 tokens | $0.25 / 1,000,000 tokens |
| Output(audio) | $6.00 / 1,000,000 tokens(≈$0.0015/10秒音声) | $3.00 / 1,000,000 tokens |

Audio token換算は25 tokens/秒(公式脚注)。本Trialは
`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01`によりStandard同期を使う
(Batchは正式量産用、本Trialでは対象外)。

想定コスト(1回の成功attempt、USD_JPY=160換算、既存Trialコード
[`er011_connected_speech_equivalence_layer_trial_02.py`]と同じレート):

| segment | duration(A実測) | output tokens(25/秒) | 出力費用(円) |
|---|---|---|---|
| tension_reflection | 62.25秒 | 1,556 | 約¥1.49 |
| full_story_part1 | 15.01秒 | 375 | 約¥0.36 |
| point_two_body | 44.06秒 | 1,102 | 約¥1.06 |

input(text)側は数百文字程度でいずれも1円未満。ASR費用(既存`openai_asr`
料金、pricing_snapshot.json既存)は前回実測から1回あたり概ね¥0.5未満。

**worst-caseシナリオ(標準2回+fallback1回=最大3回、毎回が出力token上限
16,384付近まで暴走した場合)**: 1 attempt最大 ≈ $6.00×16,384/1,000,000
= $0.0983 ≈ **¥15.7**。3回連続で起きた場合、1 segmentあたり最大
**約¥47**。段階1(1 segment)のworst-case合計は約¥50、段階2(2〜3
segment)は約¥100〜150で、いずれも¥500 Cap内に十分収まる。段階3
(1記事、17segment)のworst-caseは約¥800となり得るため、**段階3へ
進む場合はCap再設定または追加承認をユーザーに諮る**(§13参照)。

## §11 retry方針(変更なし)

標準2回+fallback1回=合計3回(§4参照、既存`PRODUCTION_MAX_TTS_ATTEMPTS`
のクランプ機構をそのまま利用)。fallback経路の中身(minimal instruction)
も、Gemini 3.8系では「instruction自体を本文と混ぜない」がデフォルトの
はずなので、fallbackの意味合いが変わる可能性がある(例:
fallback=styleを完全に空にする、程度の単純な差になりうる)。この設計は
Trial実装時に確定する(本計画では方針のみ)。

## §12 成功条件

- 段階1(代表1 segment): 選定segmentがASR検証PASS(EXACT_MATCH/
  NORMALIZED_MATCH/PHONETIC_MATCH相当)かつ異常長検知に該当せず、
  本文外発話が確認されないこと。かつ実測latency・costが記録されること。
- 段階2(2〜3 segment、段階1成功後のみ): 追加segment(異なるvoice/
  言語を含む)でも同様の結果が再現すること。
- 段階3(1記事、段階2成功後のみ): 17segment全体でOK到達率が既存A
  (17/17)に近い水準(具体的な閾値はユーザー判断、目安として提示するに
  留める)。

## §13 STOP条件(segment単位の早期停止)

以下いずれかに該当した時点で、そのsegmentの追加attemptを行わず、Trial
全体も一旦停止しユーザーへ報告する:
1. 生成音声長が`estimate_max_reasonable_duration_seconds`の見積り上限を
   超える(既存`detect_duration_anomaly`が`is_anomaly=True`を返す)。
2. ASR結果が本文外発話(canonical本文の主要語がほぼ含まれない
   `TRUE_CONTENT_MISMATCH`)と判定される。
3. 同一segmentでretryが2回発生した時点(3回目に入る前)で、原因(§2仮説
   のどれに該当するか)を一度立ち止まって確認する(前回のように「retry
   が3回終わるまで気づかない」運用を避ける)。
4. `assert_budget_ok()`相当のチェックで、**次の1回のTTS呼び出しを行うと
   想定コストが¥500を超える見込みになった時点**(実測ではなく事前判定、
   §14参照)。
5. 累積実測費用(`compute_cost_jpy_so_far()`相当)が¥500に到達した時点。
6. その他、既存Production安全装置(Human Review Lock等)が作動した場合。

## §14 拡大条件(段階の進め方)

1→2〜3→1記事の順に進め、各段階の完了後にユーザーへ結果(ASR結果・
異常長有無・latency・cost・試聴artifact[必要な場合のみ])を報告し、
次段階へ進む可否をユーザーに確認してから進める(自動連鎖しない)。
段階1がSTOP該当(§13)になった場合、段階2以降には進まず
`USER_DECISION_REQUIRED`として報告する。

## §15 ¥500 Cap実装方法

`er011_connected_speech_equivalence_layer_trial_02.py`の
`compute_cost_jpy_so_far()`/`assert_budget_ok()`/`BUDGET_JPY_CAP`と同型の
仕組みをTrial専用スクリプトへ実装する:

1. **pricing_snapshot.jsonへの追記案**(実装のみ、本タスクでは未実施):
   `er005_output/cost_baseline_01/pricing_snapshot.json`の`prices`配列へ、
   `provider="gemini"`, `model="gemini-3.8-flash-lite-tts"`について
   Standard/Batch各tierのinput_tokens/output_tokensエントリを追加する
   (値は§10表、`source_url`は本計画冒頭のpricingページURL、
   `confidence="OFFICIAL_SOURCE"`、`note`に取得日2026-09-27と
   「2026年12月31日までの現行レート、2027年以降値上げ予定」を明記)。
   **未収録のまま計算すると前回同様proxy推定に頼らざるを得ないため、
   Trial実行前に必ずこの登録を先に行う**(Trial実装タスクのPhase 0)。
2. `compute_cost_jpy_so_far()`と同型の関数で、Trial専用のcost
   logへ記録された全呼び出し(Gemini TTS・ASR・reading-safety LLM)を
   pricing_snapshotの値で都度円換算し合計する。
3. `assert_budget_ok(note)`を**TTS呼び出しの直前**(生成後ではない)に
   呼び、現在の累積費用に「次の1回の想定最大費用(worst-case、§10の
   ¥15.7/attempt)」を加えた見込みが¥500を超える場合は、その場で
   `RuntimeError`相当を送出しTrialを停止する(前回のような「実行後に
   超過が判明」を防ぐ、事前ガード方式)。
4. BUDGET_JPY_CAP=500として定数化する。段階3(1記事)へ進む場合は、
   段階1・2の結果を踏まえてユーザーが新しいCapを設定し直す
   (自動引き上げしない)。

## §16 未確認事項(推測で埋めていない項目)

- `client.models.generate_content`経由で`part.speech_metadata`を実際に
  送信できるか(SDK型定義に存在しない、dictで代用可能かは未検証)。
- `client.interactions.create()`経由で`speech_metadata`アノテーションが
  実際に受理されるか(型定義Union未列挙、dictで代用可能かは未検証)。
- `requirements-ci.txt`記載の`google-genai==2.14.0`と実機`.venv`の
  `2.11.0`の齟齬(本計画のスコープ外の発見事項として記録のみ、Production
  への影響有無は未調査)。
- モデル別RPM/TPM(rate-limits公式ページがJS動的レンダリングのため
  静的HTML取得では確認できず)。
- `response_format`をGenerateContent API経由でも明示指定できるか
  (Interactions API側のフィールドとして記載されているのみ確認)。
- 実際のlatency改善有無(推測のみ、実測はTrial時)。

## §17 このTrialで検証しないこと(範囲外、変更なし)

- Luna(記事本文生成LLM)の評価とは混同しない(TTSのみが対象)。
- 既存Production記事・既存完成音声の変更は一切行わない。
- Key Phrase(kp1-5)は前回同様、本計画の代表segment候補には含めない
  (対象article自体にKey Phraseの新規Trial要求は無いため)。
