# ER-006-AUDIO-COST-OPTIMIZATION-01 完了報告

TTS Batch・定型音声再利用・ASR代替比較・Retry Waste削減の調査結果。**実装はゼロ件** — 本タスクは調査・実測・設計提案のみ。すべての変更提案は次のユーザー承認を待つ。

---

## 0. サマリー(先に結論)

| 項目 | 結論 |
|---|---|
| Gemini TTS Batch | **英語・日本語どちらの現行モデルでも実際に動作することを本日、実際にジョブを完走させて確認済み**(公式ドキュメントの「対応表未記載」や8ヶ月前のGitHub Issueの報告と食い違うため、実機で検証した) |
| Batch料金 | Standardの**半額**(入力$1.00→$0.50、出力$20.00→$10.00 / 100万token、Gemini公式価格表に英語・日本語モデル共通で明記) |
| 定型音声(Master Audio)再現性 | 既に29%のセグメントがコピー流用されているが、**検証機構がゼロで実際に1件ドリフト(音声のズレ)を発見**。仕組み化の増分効果はセグメント数で+30〜33%、秒数で+4〜6%程度(本体寄与は小さいが、正しさのリスクは実在) |
| ASR代替 | AssemblyAI・DeepgramはAPIキー未設定のため実テスト不可(ブロック、要ユーザー対応)。**OpenAI gpt-4o-mini-transcribeは実際に取得済みキーでテスト実行し、Azureの既知の誤認識(street→St.、three→3:00等)の一部を実際に解消することを確認** |
| 残存STOPPED 8件 | 全件フォレンジック完了。うち2件はASR切替で完全解消、2件は大幅改善、1件は非決定性(再試行だけで解消)、1件はcanonical_text自体のバグ(プレースホルダ文字混入)、2件はASR切替でも未解消 |
| 最終コスト比較(音声パイプラインのみ、B1+A2ペア) | Current ¥132/pair → Option D(Batch+ASR切替+Master Audio) ¥44/pair、月次(20トピック/日)で¥79,000→¥26,000程度と試算 |
| Writer(Luna)のコスト | Batch API不可(web_search tool未対応、公式に確認)。Flexは非推奨(OpenAI公式)。Prompt Cachingは自動適用中だが**実測利用率はわずか2.4〜4.3%**(理論上限よりかなり低い、伸びしろあり) |
| 今回の新規有料API支出 | 合計 約¥25(Azure再テスト¥19、OpenAI-mini-transcribe¥3、Gemini Batch確認テスト¥1未満) |

---

## 1. ER-006-TTS-BATCH-01: Gemini TTS Batch API

### 1.1 Batch可否(model単位で実機確認、推測なし)

「Geminiファミリーだから使えるはず」という推測はせず、現行プロダクションで使っている**厳密なmodel ID単位**で、実際にAPIを叩いて確認した。

| Model ID | 用途 | Batch job作成 | Batch job完走(SUCCEEDED) | 実際の音声出力 |
|---|---|---|---|---|
| `gemini-2.5-pro-preview-tts` | 英語TTS(本番) | 成功 | **成功(実機確認)** | PCM 24kHz、192,526 bytes(約4秒の"Hello, this is a batch API completion test.") |
| `gemini-3.1-flash-tts-preview` | 日本語TTS(本番) | 成功 | **成功(実機確認)** | PCM 24kHz、251,520 bytes(約5.2秒の日本語文) |

背景として、`gemini-2.5-pro-preview-tts`はGoogle公式のBatch APIガイドに対応モデルとして明記がなく、外部のGitHub Issue(google-gemini/cookbook#1077, 2025年12月open, 未解決)では同モデルでBatch実行時に404エラー("not supported for batchGenerateContent")が報告されていた。この食い違いを解消するため、本日(2026-08-22)実際に最小限のリクエスト(短い1文)でBatch jobを作成・完走まで確認した。結果、**現時点では両モデルともBatch APIが正常に機能する**ことを直接確認できた(Googleがその後有効化したか、Issue報告者側の別要因だったかは不明だが、現在の挙動としては動作する)。

新規有料API支出: 実行したBatchジョブ3件(英語テスト2回・日本語テスト1回、うち英語1回はPENDING状態で即キャンセルしたため課金なし)、合計 1円未満(数百tokenのみ)。

### 1.2 料金(Standard vs Batch、円換算)

Gemini公式価格表より、英語・日本語モデル共通:

| | Standard | Batch(50%オフ) |
|---|---|---|
| 入力(テキスト) | $1.00 / 100万token | $0.50 / 100万token |
| 出力(音声) | $20.00 / 100万token | $10.00 / 100万token |

実測(本番Pool Pilot run、`raw_usage_log.jsonl`のtts_a2/tts_b1ステージ、Gemini分のみ)によるTTS部分の実コスト構成比: **Gemini TTS ≈ 65.9%、Azure ASR ≈ 34.1%**(音声パイプライン全体コストの内訳、B1+A2ペア平均クリーンコスト¥77.24のうち)。Batchを適用するとGemini部分が半額になるため、音声パイプラインのクリーンコストは ¥77.24 → 約¥51.8(▲33%)。詳細な月次試算は §5 参照。

### 1.3 Batch品質(Voice/Style/Structured Separation維持)

Batch APIはStandardと**同一モデル・同一推論エンジン**を使う非同期スケジューリングの違いに過ぎない(モデル自体が別物になるわけではない)ため、理論上はvoice/style/pronunciationの品質は同一と期待できる。実施した完走テストでも、`speech_config`(voice="Aoede")をStandardと全く同じ`er002_gemini_client.py::build_speech_config()`から構築しており、生成されたPCM音声のヘッダ情報(sample rate, bytes/秒相当のデータ量)はStandard実行時と同じフォーマット。

ただし、**実際の音声波形を人間が聴き比べる完全なA/Bテストは今回実施していない**(Batchのターンアラウンドは公式には最大24時間、実際は数分〜1分程度で完了したが、有料API支出最小化の方針のもと、今回は「Hello」レベルの最小テキストのみに留めた)。本番の実コンテンツ(Key Phraseや長尺ナレーション)でのBatch音声を、ユーザーが実際に聴いて判断する完全なA/Bは、承認後の実装フェーズで改めて実施することを推奨する。

### 1.4 その他の制約(公式ドキュメントより)

| 項目 | 内容 |
|---|---|
| リクエスト形式 | 小規模(<20MB)は`InlinedRequest`のリストを直接渡せる。大規模はJSONLファイルをアップロード(最大2GB) |
| ターンアラウンド | 公式目標「24時間以内、多くの場合はもっと早い」。実測: 今回のテストは1分未満で完了 |
| 結果の保持期間 | 6週間 |
| 失敗アイテムの扱い | `batchStats.failedRequestCount`で件数を追跡。各アイテムの結果は`GenerateContentResponse`かエラーオブジェクトのいずれか |
| 個別結果の追跡 | バッチ内の各リクエストの結果を個別に参照可能(今回のテストでも`job.dest.inlined_responses[0]`で1件ずつ取得できることを確認) |
| Cost Telemetry | 完走したジョブの`response.usage_metadata`に通常のStandard呼び出しと同じ`prompt_token_count`/`candidates_token_count`が入っており、既存の`er005_cost_logger.py`のコスト計算ロジックがそのまま使える(実機で確認) |
| retry方法 | 失敗した個別アイテムのみを再度batchに含めて再送信する運用になる想定(バッチ全体の再実行は不要) |

### 1.5 夜間バッチ生産の月次コスト試算(20/30トピック/日)

Batch適用による音声パイプライン全体(TTS+ASR)への影響は §5 の最終比較表に統合して記載。TTS部分単独では、Gemini分が半額になることで音声クリーンコストが▲約26円/pair(¥77.24→¥51.8、Azure ASR分は変化なし)。

---

## 2. ER-006-TTS-MASTER-AUDIO-01: 定型音声(Master Audio)再利用

コードベース監査のみ(新規有料API呼び出しなし)。詳細は別ファイル添付(`master_audio_audit.md`、本報告書の末尾に主要部分を統合)。

### 2.1 セグメント分類(実コードを直接読んで分類、推測なし)

現行プロダクションパイプライン(`er003_b1_p9a_audio.py`, `er003_v1_n3_01_*.py`, `er006_pool_pilot_01_audio.py`)を対象に監査した。

| 区分 | 定義 | 件数(1トピック=B1+A2ペア) |
|---|---|---|
| **A: 完全固定** | 全エピソード共通で一言一句同じ音声(Intro/Outro等の外部mp3含む) | 19件(B1:9, A2:10) |
| **B: 条件付き固定** | レベル等の条件が同じなら固定になり得るが、現状は1つのTTS呼び出しに固定部分と可変部分を混在させており実質Cとして扱われている | 0件(仕組み上まだ実現できていない機会として1件特定: Topic introの固定接頭辞) |
| **C: コンテンツ依存** | 記事ごとに内容が変わる、再利用対象外 | 47件(Key Phrase本体、記事見出し、本文、Comment、Summary等) |

**既に29%のセグメントがコピー流用で音声生成をスキップしている**(ただし検証機構なしのアドホックな仕組み)。エピソード全体の再生時間に対する割合では、A区分のTTS由来音声は約3.9%(外部mp3のIntro/Outro等を含めると約11.3%)に過ぎない — 大半(約89%)はStory本文・Point・Commentなどコンテンツ依存部分が占めるため、これは仕組み上避けられない。

### 2.2 実在するドリフト(仕組み化の必要性を裏付ける発見)

B1向けとA2向けで、同じ"Welcome to English Your Way."という完全固定テキストが、**別々のディレクトリから別々のタイミングで生成された、実際に長さが異なる2つの録音**(2.111秒 vs 2.561秒、21%の差)として存在していることを実機確認した。現状の「ファイルが存在すればコピー」という仕組みには、この種のズレを検知する手段が一切ない。

### 2.3 新規に発見した再利用機会: 同一Key Phraseのレベル間重複

3トピック実データ(`keywords_canonicalized.json`)を調べたところ、**同一トピックのB1版とA2版で、voice/model/style全て同一のままKey Phraseテキストが完全一致するケースが4件**見つかった("hostile architecture", "sludge", "network effect", "blitzscaling")。これは1トピックあたり約1.3件、20〜30トピック/日換算で1日あたり約27〜40回の重複TTS呼び出しが回避可能と試算される(該当箇所は音声が短いため、秒数への影響は1日あたり30〜60秒程度と小さい)。

異なるトピック間での重複("network effects"が別の記事でも出現する、等)は今回の3トピックのサンプルでは観測されなかった。ユーザーが例示した仮定のケースは実データではまだ再現していないが、将来的に起こり得るため、Master Audio Keyの検索はトピックIDに紐付けず、テキスト内容そのものをキーにする設計を推奨する。

### 2.4 Master Audio Keyのスキーマ設計案

```
MasterAudioKey = {
  language, level(null可), speaker_voice, tts_model_id,
  style_instruction_id, style_instruction_version, instruction_path(primary/fallback),
  canonical_text_hash(TTS投入直前の正規化後テキストのハッシュ),
  audio_processing_version(trim policy・resample設定のバージョン),
  sample_rate, channels
}
master_audio_id = sha256(上記フィールドの正規化JSON)
```

**無効化(invalidation)条件**: voice変更・話者変更・TTSモデル変更・style instruction変更(内容ハッシュで検知、手動バージョン番号は不可)・primary⇔fallback instruction切替・発話テキスト変更・話速/pacing変更・trim policy変更・サンプルレート変更 — いずれか1つでも変わればMaster Audio IDが変わり、古いMasterは自動的に再利用対象外になる設計。音量正規化(gain)はエピソードごとに動的計算される値のため、Masterには含めず「都度適用」とする(キャッシュ対象から意図的に除外)。

### 2.5 実装は保留

本監査は設計提案のみ。**仕組みの実装(Master Audio Store、lookup-before-generateロジックの追加)は行っていない**。ユーザー承認後に着手する。

---

## 3. ER-006-ASR-COMPARE-01: ASR代替プロバイダ比較

### 3.1 credential状況(ブロッカーの開示)

`.env`を確認したところ、`OPENAI_API_KEY`はあるが**`ASSEMBLYAI_API_KEY`と`DEEPGRAM_API_KEY`が存在しない**。そのため:

- **AssemblyAI Universal-2・Deepgram Nova-3 Multilingual: 実テスト不可(ブロック)**。公式料金のみ記載する。テストを希望する場合はAPIキーの追加設定が必要(ユーザー対応事項)。
- **Azure(既存baseline)・OpenAI gpt-4o-mini-transcribe: 実際にAPIを叩いてテスト実施済み**。

### 3.2 固定fixtureセット(新規TTS生成なし、既存音声のみ使用)

過去のセッションで既に生成済みの音声ファイルから、指定された問題ケース全てをカバーする14件を選定(下記)。新規に生成した音声はゼロ件。

| # | ケース | 音声ファイル |
|---|---|---|
| 1 | Malmö/Triangeln(地名) | `pool_benches_luna/b1b/narration/point_two.wav`, `.../a2/narration/point_two.wav` |
| 2 | street→"St." | `pool_benches_luna/a2/narration/point_one.wav`, `.../b1b/narration/full_story_part1.wav` |
| 3 | three→"3:00" | `pool_benches_luna/b1b/narration/point_one.wav` |
| 4 | cancelling/canceling | `pool_subscriptions/b1b/narration/comment_2.wav` |
| 5 | Click-to-Cancel | `pool_subscriptions/a2/narration/full_story_part2.wav` |
| 6 | blitzscaling | `pool_startups/b1b/narration/full_story_part2.wav` |
| 7 | hostile architecture | `pool_benches/h_onset_diagnostic/hostile_repeat1.wav`, `hostile_repeat2.wav` |
| 8 | 日本語短語(ホモフォン) | `pool_benches_luna/b1b/narration/kp5_ja_charon.wav` |
| 9 | 通常長尺ナレーション(baseline) | `pool_benches_luna/b1b/narration/full_story_part1.wav`, `full_story_part2.wav` |

### 3.3 結果(Azure vs OpenAI gpt-4o-mini-transcribe、実測)

既存の分類器(`er006_preprod_hardening_01_validation.py::classify_asr_match`)で機械的に判定した結果:

| ケース | Azure判定 | Azure結果(要約) | OpenAI-mini判定 | OpenAI-mini結果(要約) |
|---|---|---|---|---|
| street/point_one (A2) | **TRUE_CONTENT_MISMATCH**(誤検知) | "St. furniture"/"busy St."(誤認識) | **NORMALIZED_MATCH**(合格) | "street furniture"/"busy street"(正しく認識) |
| street/full_story_part1 (B1) | **TRUE_CONTENT_MISMATCH** | 同上の"St."誤認識を再現 | **NORMALIZED_MATCH** | 正しく認識 |
| three→3:00 (B1 point_one) | **TRUE_CONTENT_MISMATCH** | "3:00"に誤変換 + "Ottoni"→"A Tony"(固有名詞) | **TRUE_CONTENT_MISMATCH**(一部改善) | "three"は正しく認識、"A Tony"は依然誤認識 |
| Malmö/Triangeln (B1 point_two) | **ASR_VALIDATION_UNCERTAIN** | "Malmo's Triangon"(誤認識) | **TRUE_CONTENT_MISMATCH**(別要因) | "Malmö's Triangeln"は正しく認識、ただし"put in"vs"reported"の語彙差で別途mismatch判定 |
| Malmö/Triangeln (A2 point_two、難しい方の用例) | ASR_VALIDATION_UNCERTAIN | "Momo's Triangle in station" | ASR_VALIDATION_UNCERTAIN(未解消) | "Mamo's Triangle and station"(こちらも誤認識) |
| cancelling/canceling | **TRUE_CONTENT_MISMATCH** | "canceling"(BrEng→AmEng変換は正規化対象内だが今回は別の語順差で不一致判定) | **NORMALIZED_MATCH** | 同じ変換だが正規化により合格 |
| Click-to-Cancel | **TRUE_CONTENT_MISMATCH** | 句読点・段落の差異で不一致判定 | **NORMALIZED_MATCH** | 合格 |
| blitzscaling | **TRUE_CONTENT_MISMATCH** | "vast expansion"等、複数の言い換え差 | **TRUE_CONTENT_MISMATCH**(未解消) | 同様に複数の言い換え差が残る |
| hostile architecture(1回目) | NORMALIZED_MATCH | "A hostile architecture." | NORMALIZED_MATCH | 同じ |
| hostile architecture(2回目) | NORMALIZED_MATCH | "Hostile architecture." | **TRUE_CONTENT_MISMATCH**(OpenAI-miniの誤り) | **"hustle architecture"と誤認識**(OpenAI-mini側の弱点) |
| 日本語短語 | NORMALIZED_MATCH(検証器が緩く判定) | "それをこれと結びつける。" | NORMALIZED_MATCH(同上) | 同一の誤認識テキスト |
| 通常長尺(baseline) | NORMALIZED_MATCH | ほぼ一致 | NORMALIZED_MATCH | ほぼ一致 |

**14件中の合格率(should_pass=true)**: Azure 5/14(35.7%) vs OpenAI-mini 8/14(57.1%)。

重要な点: **OpenAI-miniが常に優れているわけではない**("hostile"→"hustle"という新しい誤認識を1件発生させた)。ただし全体としては、Azure特有の系統的な癖(street→St.、three→3:00)を複数解消しており、これらは「TTSは正しいのにASRが誤読して不要な再試行を招く」典型例だった。

### 3.4 コスト比較(円換算、1USD=160円)

| プロバイダ | 単価 | Azure比 | テスト状況 |
|---|---|---|---|
| Azure(baseline) | $1.00/時間 = $0.0167/分 | — | 実測(baseline) |
| OpenAI gpt-4o-mini-transcribe | $0.003/分(定額) | **約82%安い** | **実測済み** |
| AssemblyAI Universal-2 | $0.15/時間 = $0.0025/分 | 約85%安い | 未テスト(APIキーなし、公式料金のみ) |
| Deepgram Nova-3 Multilingual | $0.0058〜0.0092/分(情報源により差あり) | 約45〜65%安い | 未テスト(APIキーなし、公式料金のみ) |

### 3.5 提供元選定基準に基づく評価

タスク指定の基準(「安ければ良い」ではない)に沿って評価:

1. **真の内容エラーを絶対に見逃さない** — 実測データ内でOpenAI-miniが「本当は間違っているTTSを正しいと誤判定した」ケースは0件(hostile→hustleの誤りは逆方向、正しい音声を誤って拒否する側のエラーであり、安全側)。
2. **Azureよりfalse negativeが少ない** — 実測で確認(Azure 9件失敗 → OpenAI-miniで4件が合格に転じた。詳細は§4)。
3. **英語長尺で安定** — 実測: 73秒の長尺(Click-to-Cancel)を含め安定して動作。
4. **日本語短語で許容範囲** — 実測: Azureと同じ誤認識をした(改善なし、悪化もなし)。
5. **単価がAzureより明確に安い** — 実測: 約82%安い。

**結論(暫定、要ユーザー最終判断)**: OpenAI gpt-4o-mini-transcribeは基準1〜3・5を満たす。基準4(日本語)は「同等」であり「改善」ではない。AssemblyAI/Deepgramは公式料金上さらに安いが未検証のため、この場では推奨に含めない。英語をOpenAI-miniに、日本語は現状Azure維持という**言語別分割**も選択肢として妥当(タスク仕様が許容する構成)。

---

## 4. ER-006-AUDIO-WASTE-RESIDUAL-01: 残存STOPPED/UNCERTAIN 8件の全数フォレンジック

Public Benches Luna run(前タスクで生成済み)のSTOPPED 7件+UNCERTAIN 1件、全件について、canonical_text・TTS入力・Azure実測トランスクリプト・新分類器判定・§3のASR代替結果を突き合わせ、分類した。

| # | セグメント | 元のstatus | 分類 | 根拠 |
|---|---|---|---|---|
| 1 | B1 comment_3 | STOPPED | **D(非決定性)** | 今回Azure・OpenAI-mini双方で再テストしたところ**両方とも合格**。ASRの実行ごとのブレによる一過性の失敗だった可能性が高く、追加リトライだけで自然解消していたと考えられる |
| 2 | B1 full_story_part1 | STOPPED | **B(Azure認識エラー)** | "street furniture"→"St. furniture"の系統的誤認識。OpenAI-miniでは完全解消(NORMALIZED_MATCH) |
| 3 | B1 point_one | STOPPED | **B+D混在** | "three"→"3:00"はAzure特有の誤認識(OpenAI-miniで解消)。ただし"Ottoni"→"A Tony"の固有名詞誤認識はOpenAI-miniでも未解消 — ASR一般の弱点(固有名詞)であり、プロバイダ変更だけでは全解決しない |
| 4 | B1 point_two | STOPPED | **B(部分)+D(検証器側)** | Malmö/Triangelnの地名誤認識はOpenAI-miniで解消。ただし"reported"→"put in"という言い換えで別のmismatch判定が発生 — これは検証器のcontent-word比較が厳格すぎる可能性がある(Validation over-strict寄り) |
| 5 | B1 kp5_ja | STOPPED | **C(検証設計の不具合)** | canonical_textが`"〜を…と結びつける"`という**プレースホルダ記号を含んだテンプレート文字列**になっている。実際に発話された音声をどのASRで認識しても、この記号自体は発音されないため原理的に一致しようがない。ASRプロバイダの問題ではなく、canonical_text生成側の不具合 |
| 6 | A2 full_story_part1 | STOPPED | **B(大幅改善)** | Azureは数字表記の乱れ("twenty-two.2014")で誤検知。OpenAI-miniはほぼ完全一致だが、句読点(スマートクォート)の差でASR_VALIDATION_UNCERTAIN止まり — 完全合格ではないが実用上問題ない水準まで改善 |
| 7 | A2 point_one | STOPPED | **B(完全解消)** | street→"St."誤認識。OpenAI-miniで完全解消(NORMALIZED_MATCH) |
| 8 | A2 point_two | UNCERTAIN | **A(未解決)** | Malmö/Triangelnのより難しい用例("At Momo's Triangle in station"のような文脈)。OpenAI-miniでも誤認識が残った。固有名詞・外来語のtransliterationはASRプロバイダを変えても限界がある |

**集計**: 8件中、2件が完全解消(#2, #7)、2件が大幅改善(#3一部, #6)、1件が非決定性(#1)、1件が検証設計側の不具合(#5、ASR無関係)、1件が部分的にASR起因・部分的に検証器側の厳格さ起因(#4)、1件が未解決(#8)。

**ASRプロバイダ切替単独での改善見込み**: 8件中およそ3〜5件相当が解消または大幅改善。残りは(a) canonical_textの記号混入バグの個別修正、(b) 固有名詞・難しい外来語の限界的ケースとしてHuman Review継続、のいずれかで対応する必要がある。

---

## 5. Retry-policy再設計の評価(Primary+Secondary ASR)

「TTS生成→Primary ASR→不一致ならSecondary ASRのみ(ambiguousな場合)→両者一致なら採用→両者が確認した真の不一致のみTTS再生成」という設計を、実装はせず評価のみ行った。

- **利点**: OpenAI-miniのfalse positive("hustle"誤認識のようなケース)をAzureとのクロスチェックで拾える可能性がある。実測§3.3で確認した通り、OpenAI-mini単独でも新たな誤りを生むため、二重チェックには一定の合理性がある。
- **欠点**: ambiguous判定になった分だけAzure二重課金が発生する(§3.4のコスト比較よりAzureはOpenAI-miniの約5.5倍高い)。実測データでのUNCERTAIN発生率(約14%、14件中2件)を前提にすると、コスト増分は音声パイプラインクリーンコストの5〜7%程度で収まる見込み(§6の試算Option C参照)。
- **結論**: 複雑さとコストの増分は許容範囲内だが、増分の恩恵(false positiveの追加削減効果)は今回の限られたfixtureサンプルでは明確に実証できていない。**まずはOption B(Primary ASRのみ切替)を先に本番投入し、実際のfalse positive発生率を大きいサンプルで観測した上で、Secondary ASRの要否を再判断することを推奨**する。

---

## 6. 最終コスト比較(4オプション、音声パイプラインのみ、JPY)

対象は音声(TTS+ASR)部分のみ。Writer/Research部分(B1+A2ペアあたり約¥4.1、Lunaモデル据え置き)は全オプション共通のため除外している。

**前提とした実測値**: B1+A2ペアのクリーン音声コスト ¥77.24(3トピックの実本番run平均)。Gemini TTS/Azure ASRのコスト構成比 65.9%/34.1%(実測)。実際のwaste比率(実際の呼び出し回数÷理論上の最小回数)= 1.708倍(`attempt_ledger.json`の実測reconciliationデータより)。以下、waste削減率はオプションごとの**モデル化した仮定**であり、§3・§4の実測知見を根拠に設定した(内訳は各行に注記)。

| オプション | 内容 | Clean cost/pair | 期待waste/pair | 実質cost/pair | 20トピック/日・月次 | 30トピック/日・月次 |
|---|---|---|---|---|---|---|
| **Current** | Standard TTS + Azure + 現行retry | ¥77 | ¥55(waste比+70.8%、実測) | **¥132** | **¥79,200** | **¥118,700** |
| **A** | Batch TTS + Azure + 改善retry(guardrail調整のみ、ASR切替なし) | ¥52 | ¥29(waste比+56.6%、guardrail調整のみでは限定的改善と仮定) | **¥81** | **¥48,700** | **¥73,000** |
| **B** | Batch TTS + OpenAI-mini(primary ASR切替)+ 改善retry | ¥30 | ¥12(waste比+38.9%、§4の実測改善率を根拠) | **¥42** | **¥25,200** | **¥37,800** |
| **C** | B + Secondary ASR(ambiguous時のみAzure併用) | ¥34(secondary分+¥4) | ¥12 | **¥46** | **¥27,500** | **¥41,300** |
| **D** | C + Master Audio再利用(TTS部分▲5%) | ¥33 | ¥12 | **¥44** | **¥26,500** | **¥39,700** |

**読み方の注意**: Current行は完全実測(§1.2の実測コスト構成比+§4元となった`attempt_ledger.json`のreconciliationデータ)。A〜D行のwaste削減率は、§3・§4で実際に観測した「ASR切替で何件解消したか」を参考にした**保守的な見積もり**であり、実際に本番投入して大規模に計測しないと確定しない。傾向として、**Batch適用(▲約33%)とASR切替(waste比の大幅改善)の効果が支配的で、Master Audio再利用の追加効果は相対的に小さい**という結論は、§2の監査結果とも整合している。

---

## 7. Writer(Luna)の公式ディスカウント機構の適用可能性(調査のみ、モデル変更なし)

Writerモデルは引き続きgpt-5.6-luna固定。以下、同一モデル・同一品質を保ったまま単価を下げられる公式機構の調査結果。

| 機構 | 適用可否 | 理由 |
|---|---|---|
| **OpenAI Batch API** | **不可** | Writer(Research段階)・Fact Checkの両方が`tools=[{"type": "web_search"}]`を使用しており(`er002_ja_web_research_r3.py`で実コード確認済み)、OpenAI公式ドキュメント・コミュニティ報告により**Batch APIはweb_search toolを現在サポートしていない**ことを確認した(WebFetch/WebSearchで公式情報源から確認) |
| **OpenAI Flex processing** | **非推奨** | 50%割引はBatchと同じだが、OpenAI自身が「本番運用には非推奨、評価用途向け」と明言しており、可用性が同期APIより不安定 |
| **Prompt Caching(自動適用)** | **適用可能・既に部分的に動作中だが低利用率** | 1,024token以上のプロンプトで、共通のprefixが再利用されると**コード変更不要で自動的に**キャッシュ割引(最大90%オフ)が適用される仕組み。**実測**(`raw_usage_log.jsonl`より): writer_b1ステージのキャッシュ利用率は入力token中わずか**2.4%**、writer_a2は**4.3%**。理論上の余地はもっと大きいはずで、B1/A2それぞれの呼び出しで共通のcommon_block(記事トピック+検証済みLedger)を先頭に配置する順序を工夫すれば、キャッシュヒット率を上げられる可能性がある。**ただしこれはプロンプト構築順序の変更(実装作業)にあたるため、今回は実装せず、伸びしろの存在のみ報告する** |

---

## 8. 制約の遵守確認

- エピソード構成・B1/A2仕様・Support内容・声質・トーン・pacing・TTS話者・発話テキスト内容・料金プランは**一切変更していない**。
- 実施した変更: **なし**(本タスクは調査・実測・設計提案のみ、コード変更ゼロ件)。
- 新規有料API支出: 合計約¥25(内訳: Azure ASR再テスト約419秒分 ¥19、OpenAI gpt-4o-mini-transcribe同区間 ¥3、Gemini Batch確認テスト3件 1円未満)。新規TTS大量生成は一切行っていない。
- AssemblyAI/Deepgramは`.env`にAPIキーが存在しないため実テストできなかった。テストを希望する場合は該当のAPIキー追加設定が必要(ユーザー対応事項として明示)。

---

## 9. 次のアクション(すべて承認待ち、未実装)

1. Master Audio Store の実装(§2.4スキーマに基づく) — welcome.wavのドリフト修正を含む
2. Primary ASRをOpenAI gpt-4o-mini-transcribeへ切替(Option B) — 本番投入前に大規模サンプルでのfalse positive率の実測を推奨
3. Gemini Batch APIの夜間バッチ生成への組み込み — 実コンテンツでの完全な音声A/B(ユーザー最終試聴)を先に実施
4. Writer側プロンプトのcommon_block配置見直し(Prompt Cachingヒット率向上) — 変更影響範囲の説明を別途行った上で着手
5. kp5_ja型のcanonical_textプレースホルダ文字混入バグの個別修正
6. AssemblyAI/Deepgramを試したい場合はAPIキーをご用意いただければ追加テスト可能

---

完了後STOP。残りPool Topic生成には進まない。
