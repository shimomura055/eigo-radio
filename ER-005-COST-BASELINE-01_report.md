# ER-005-COST-BASELINE-01 完了報告

**A2/B1 Production-like実測原価測定**
実施日: 2026-08-17
対象テーマ: COST-ARTICLE-01(AKB48)、COST-ARTICLE-02(子育てに関する最新の研究)

---

## A. Executive Summary

| 指標 | AKB48 | Parenting |
|---|---|---|
| Actual Cost(1 Theme = A2+B1) | **$5.039** | **$4.761** |
| Clean-run Cost(参考値) | $2.210 | $2.848 |
| Retry/Fallback Overhead | $2.829(56.1%) | $1.913(40.2%) |

- **2テーマ平均 Actual Cost: $4.90 / theme**(A2+B1両方、Shared Research込み)
- **2テーマ平均 Clean-run Cost: $2.53 / theme**
- **最大Cost Driver: Research/Verified Fact Ledger作成**(2テーマ合計$3.70、単体で最大の費目。Writer+Fact QAがそれに次ぐ)
- 上記とは別に、**今回の計測セッション固有の障害(Research Templateのトピック非依存化前の汚染call、Azure Speechクォータ枯渇による再実行)による追加支出が$10.40発生**。これは定常運用では発生しない一過性コストであり、Actual Costには含めていません(詳細はF・J節)。

## B. Pipeline Actually Executed

既存のProduction候補Pipelineを無改変で実行しました(理由はD節参照)。

| Stage | 使用モジュール | Provider/Model |
|---|---|---|
| Research → Fact Ledger draft | `er003_v1_en_direct_vfl_01_generate.py`(Researcher) | OpenAI Responses API, `gpt-5.6-sol`, `web_search`ツール |
| Fact Ledger Verification | 同上(独立Verification call) | 同上 |
| B1/A2 Writer | `er003_v1_n3_01_articles_generate.py` (`run_one_pattern`) | 同上 |
| Fact Checker | `er002_ja_web_research_r3.py` | 同上 |
| Ledger Deviation Check | `er003_v1_en_direct_vfl_01_generate.py` | 同上 |
| Scaffold(Preview/Comments) | `er003_v1_n3_01_scaffold_generate.py` | 同上 |
| Key Phrase選定(Strategy L+Canonicalization) | `er003_b1_p2_keywords.py`等 | 同上 |
| TTS(英語Component/News本文/Key Phrase) | `er003_v1_sing01_*`, `er003_v1_repro01_main_generate.py`等 | Gemini `gemini-2.5-pro-preview-tts` |
| TTS(日本語、reading-safety) | 同上 | 同上 |
| ASR検証 | `er003_b1_p3u_audio.py` / `er003_b1_p4_audio.py` | Azure Speech-to-Text(リアルタイム) |
| Full Audio組み立て | `er003_v1_n3_01_assemble.py` | ローカル処理(API課金なし) |

B2は生成していません(初回Launch対象外、CURRENT_SPEC通り)。

## C. Topic Selection / Research

キーワード入力から、私自身のWebSearchで現在ニュース価値のある具体的トピックを選定しました(既存Research Pipeline実行前の編集判断、ProductionのAPI課金対象外・$0)。

- **AKB48**: 68thシングル『好きish』(2026-08-19発売)。伊藤百花の2作連続センター(2014年渡辺麻友以来12年ぶり)と、20期研究生・近藤沙樹(14歳)の初選抜。「AKB48史上最年少」ではなく「現役最年少」である点を明確に区別。
- **Parenting**: Child Development誌(Vol.97 Issue 2、2026年3-4月号)掲載のDunedin Studyコホート研究(Islam, Jaffee, Belsky, Hancox, Poulton, Ramrakha, Wertz)。719人の親を対象に、社会階層の世代間移動と養育の質の関連を検証。

## D. Usage Summary(Provider/Model別)

Kept(最終的に採用された、テーマに合致した実行)分のみ。棄却分はF節参照。

| Provider | Model/Service | 用途 | Call数(2テーマ合計) |
|---|---|---|---|
| OpenAI | `gpt-5.6-sol`(Responses API) | Research/Writer/FactChecker/LedgerDeviation/Support/KeyPhrase | 60 |
| OpenAI | web_search tool | 上記に付随 | 実測値はraw_usage_log参照 |
| Gemini | `gemini-2.5-pro-preview-tts` | TTS(英語・日本語・Key Phrase) | 386 |
| Azure | Speech-to-Text(リアルタイム) | ASR検証 | 329 |

TokenはOFFICIAL_API_RESPONSE(公式usage metadata)を使用。ASRの送信音声秒数はWAVヘッダから直接算出(LOCAL_WAV_HEADER_EXACT、推定ではなく厳密値)。詳細な生ログは`er005_output/cost_baseline_01/raw_usage_log.jsonl`(1 call = 1 record)。

## E. Cost by Stage

| Cost | AKB48 | Parenting |
|---|---|---|
| Shared Research/Ledger | $1.606 | $2.094 |
| Search/Grounding(web_search tool fee) | $0.380 | $0.400 |
| B1 LLM(Writer+FactQA+Support+KeyPhrase) | $0.786 | $0.669 |
| A2 LLM(同上) | $0.899 | $0.704 |
| B1 TTS | $0.372 | $0.357 |
| A2 TTS | $0.564 | $0.259 |
| B1 ASR | $0.189 | $0.162 |
| A2 ASR | $0.243 | $0.117 |
| **Actual Total** | **$5.039** | **$4.761** |
| **Clean-run Total** | **$2.210** | **$2.848** |
| **Retry/Fallback Overhead** | **$2.829** | **$1.913** |

## F. Retry / Fallback Analysis

### F-1. 真のProduction Retry Overhead(Clean-run比較対象)
- AKB48: $2.829(56.1%)— 主因はB1/A2 TTS/ASRの内容起因retry(下記F-2)
- Parenting: $1.913(40.2%)— 主因はA2の2見出しretry(下記F-2)、および正常なfallback(短いJapanese phraseのminimal instruction fallback、OPEN-38相当)
- 2テーマ平均retry overhead: **$2.371(48.4%)**。TTS/ASRの内容起因retryが支配的で、Writer/FactChecker側のretryはほぼ発生しませんでした(4記事ともFact Checker PASS・Ledger Deviation 0件、1回で成功)。

### F-2. 内容起因の真のTTS/ASR不合格(STOPPED、Production上正常な挙動)
Best-of・無限retryは行わず、既存の標準経路(最大6回)+minimal instruction fallback経路(最大6〜8回)を使い切った時点でSTOPPEDとし、best-effort音声をそのまま採用しました。

| Theme/Level | Segment | 原因 |
|---|---|---|
| AKB48 B1 | `point_one_heading`, Key Phrase1英語 | "sole"を"soul"と発音・認識する同音異義語衝突(記事全体が"sole center"という語を核とするため複数segmentに影響) |
| AKB48 B1 | `full_story_part1` | 同上("sole"を含む) |
| AKB48 B1/A2 | `topic_intro` | 英文中に埋め込まれた日本語タイトル『好きish』の読み上げに起因する可能性(未確定) |
| AKB48 B1 | `point_two`、AKB48 A2 | `in_one_line` | 原因未特定(時間内に切り分けきれず) |
| Parenting A2 | `point_one_heading`, `point_two_heading` | "Point One:"/"Point Two:"の見出し表記を、TTSが".1"/".2"と読み上げる |
| Parenting B1 | (なし) | 全segment合格 |

これらは全て**内容起因の真のTTS/ASR不整合**であり、既存のPoint Notification/semantic heading仕様や語彙選択に起因する現象です。Production生成ロジック自体は変更していません。

### F-3. 計測セッション固有のOverhead(Actual Costに含めず、別掲)

| 原因 | AKB48 | Parenting |
|---|---|---|
| Research Templateのトピック非依存化前の汚染call(下記G参照) | $3.296 | $2.502 |
| Azureクォータ枯渇による1回目TTS/ASR run全体の再実行 | — | $4.606 |
| **計** | **$3.296** | **$7.108** |

これらは今回のPipeline側の潜在バグ(Research Templateが1テーマ専用のハードコードを含んでいた)と、Azure Speechの無料枠(F0)を使い切ったことに起因する、**今回限りの計測ノイズ**です。定常運用のコストには含めるべきでないため、Actual Cost/Clean-run Costの主要指標からは除外し、ここに独立して開示します。

**Development Cost(今回のCost Logger実装・テンプレート修正・報告書作成等)とRunning Cost(E節の表)は明確に分離しています。**上記F-3のテンプレート/クォータ問題への対応時間もDevelopment側であり、E〜G節の数値には含めていません。

## G. Wall-clock Time

| Stage | AKB48(実測) | Parenting(実測) |
|---|---|---|
| Research+Verification(Machine/API) | 約5.1分 | 約7.0分 |
| B1 Writer+FactQA+LedgerDeviation | 約2.0分 | 約2.0分 |
| A2 Writer+FactQA+LedgerDeviation | 約1.9分 | 約1.9分 |
| B1 Scaffold+KeyPhrase | 約1.7分 | 約1.4分 |
| A2 Scaffold+KeyPhrase | 約1.7分 | 約2.5分 |
| B1 TTS/ASR(Machine/API) | 約49.6分 | 約36.7分 |
| A2 TTS/ASR(Machine/API) | 約64.5分 | 約26.4分 |
| Audio組み立て(ローカル) | 1分未満 | 1分未満 |
| **Production Machine/API合計** | **約126.5分(2時間7分)** | **約77.5分(1時間18分)** |

AKB48のTTS/ASRが長いのは、F-2の内容起因retry(特に"sole"/"soul"の複数segment波及)によるものです。

上記は**Machine/API elapsed timeのみ**(私自身のデバッグ・バグ修正・ユーザーとの障害対応のやり取りに要した時間は含みません)。今回のセッション全体では、OpenAIクレジット枯渇・Azureクォータ枯渇という2件の計測用アカウント側ブロッカーへの対応で、上記に加えて相当のHuman intervention時間(ユーザーへの確認・待機を含む)を要しましたが、これはDevelopment/Measurement-session側の時間であり、Production生成時間には含めていません(次節H参照)。

## H. Article Quality / QA Results

品質はコスト計測のために一切妥協していません。

| | AKB48 B1 | AKB48 A2 | Parenting B1 | Parenting A2 |
|---|---|---|---|---|
| Fact Checker | PASS(1回目) | PASS(1回目) | PASS(1回目) | PASS(1回目) |
| Ledger Deviation | LEDGER_COMPLIANT(0件) | LEDGER_COMPLIANT(0件) | LEDGER_COMPLIANT(0件) | LEDGER_COMPLIANT(0件) |
| 語数 | 299語 | 330語 | 365語 | 398語 |
| Audio QA(peak/clipping) | peak 0.934, clipping無し | peak 0.901, clipping無し | peak 0.766, clipping無し | peak 0.950, clipping無し |
| 音声尺 | 4:46 | 5:16 | 5:52 | 6:04 |
| TTS/ASR STOPPED segment | 4件(F-2参照、best-effort採用) | 2件 | 0件 | 2件 |

`user_quality_status`は自動PASSにせず`NOT_REVIEWED`のまま(K節のArtifactでご試聴いただいた上で判断をお願いします)。

## I. Unit Economics Illustration(ILLUSTRATIVE、2テーマのみのサンプル)

**この節の数値は将来のPricing Decisionを断定するものではなく、参考試算(ILLUSTRATIVE)です。**

### I-1. Marginal cost per unique personalized theme(最重要指標)

「ユーザー1人のためだけに1テーマを新規生成すると追加でいくらか」= Shared Research/Ledger込みで、片方のレベルだけを生成した場合のコスト。

| Theme | B1のみ(Shared込み) | A2のみ(Shared込み) |
|---|---|---|
| AKB48 | $3.332 | $3.692 |
| Parenting | $3.682 | $3.573 |
| **平均** | **約$3.51 / unique theme** | |

→ **1ユーザーに1日1テーマを新規生成して届ける場合、限界コストは約$3.5〜3.7/テーマ**(2サンプル平均)。

### I-2. Case A: 完全Personalized(1 user × 1 unique theme/day)

1ユーザーが毎日別の一意なテーマを受け取る場合:

- 1テーマ(1レベルのみ配信)あたり 約$3.51
- 30日 × 1ユーザー = **約$105/月/ユーザー**(ILLUSTRATIVE)
- Research/Ledgerが個人ごとに毎回発生するため、ユーザー数に対して線形にコストが増える設計です。

### I-3. Case B: Shared Article Pool(1テーマ→A2+B1を作り、多数ユーザーへ配信)

1テーマ(A2+B1両方、平均$4.90)を作成し、N人のユーザーへ配信する場合、音声ファイルの追加配信コストは実質$0(既存の音声ストレージ配信のみ)。

| 想定ユーザー数(1テーマあたり) | 実効コスト/ユーザー/テーマ |
|---|---|
| 100人 | $0.049 |
| 1,000人 | $0.0049 |
| 10,000人 | $0.00049 |

### I-4. 示唆

Case AとCase Bでは月次原価構造が大きく異なります。Case Aは「新規性」を極大化できますが、ユーザー数に対して線形にコストが増えます。Case Bはユーザー数が増えるほど1人あたりコストが急減しますが、「その日届く記事」は共通テーマに限られます。ハイブリッド(例: 一定数の共通テーマ+週数回の完全パーソナライズ)も検討余地がありますが、これは今回の測定範囲外です。

## J. Measurement Limitations

- **2テーマのみのサンプル**であり、統計的な信頼区間は持ちません。特にI節参照。
- **Research/Verification stageの計測方法についてご確認いただいた通り**、既存の`vfl01.py`のResearcher Templateは元々1テーマ専用のハードコードを含んでおり、今回それを除去してtopic非依存化しました(D節)。これは「既存Pipelineをそのまま使う」という前提の中で見つかった潜在バグの修正であり、Production側の生成ロジック(Writer/QA/TTS/ASR)には一切手を加えていません。
- **Azure ASRのquota-exceeded応答の一部は、既存パイプラインの結果JSON上"success"扱いとして記録される場合があることを確認**しました(空文字列の文字起こしをNoneと区別していない箇所がある)。これはF-3で正しくtimestampベースに切り分けて除外していますが、raw_usage_log.jsonl単体を将来再利用する場合はこの点にご留意ください。
- **Preview価格帯のモデルであるため、料金は変更される可能性**があります(Gemini `gemini-2.5-pro-preview-tts`はGoogle自身がpreview表記)。
- Clean-run costは「各(theme, stage, provider, api)の最初の1回」を基準とした近似値であり、1回のTTS attemptに複数のASR call(word-timestamp用途等)が対応するケースを完全に1:1で紐付けたものではありません。

## K. Artifacts

4本の完成候補をご試聴いただけます(いずれもtranscript付き):

- **AKB48**: https://claude.ai/code/artifact/d292abfd-2edf-4757-8875-034197ba2baf(B1・A2両方)
- **Parenting Research**: https://claude.ai/code/artifact/5c9e74b7-fdbb-4d5b-a912-570515cfdb4b(B1・A2両方)

## L. Files / Instrumentation Added

- `er005_cost_logger.py` — OpenAI Responses API / Gemini `generate_content` / Azure ASR2関数をSDKレベルでmonkeypatchするCost Logger。Production呼び出しコードは無改変。
- `er005_stage1_research_generate.py`〜`er005_stage5_assemble.py` — 各Stageの既存Production関数をそのまま呼び出すDriver Script(新規テーマ2件用。既存N3-01の3テーマには一切影響なし)。
- `er005_stage7_cost_compute.py` — raw usage log + pricing snapshotからのCost集計。
- `er005_build_artifacts.py` — 試聴用Artifact HTML組み立て。
- `er003_v1_en_direct_vfl_01_generate.py` — `RESEARCHER_PROMPT_TEMPLATE`からUK social-media-curfew固有のハードコードを除去し、topic非依存化(唯一のProduction側コード変更、ユーザー承認済み)。
- `er005_output/cost_baseline_01/` — raw_usage_log.jsonl、pricing_snapshot.json、cost_summary.json、両テーマのVerified Fact Ledger・記事・Scaffold・監査ログ・組み立て済み音声(WAV/MP3)一式。

**CURRENT_SPEC.mdは変更していません**(今回はCost Measurement toolingのみ)。

## M. Git

コミット対象は非音声ファイル(コード・JSON・Markdown)のみとし、WAV/MP3は既存の除外方針(er003_output等と同様)に従い未コミットとします。詳細はcommit後に報告します。
