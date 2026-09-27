# Flash-Lite Production Adoption Packet 01

管理ID: `TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01`(比較パケット作成、
ユーザー承認済み 2026-09-27)。

**本パケットの位置づけ(繰り返し明記)**: これは**Production採用承認では
ない**。現行Statusは引き続き`VALIDATED`(Trialとしての検証成功、という
意味に限定)。本パケットは、ユーザーが「Production採用するか」
「採用範囲」「role別style方針」を判断するための**判断材料の整理**であり、
Fable/Sonnetがこの時点で`APPROVED_FOR_PRODUCTION`へ変更する文書ではない。
SDK更新・Production配線・正式モデル切替は本タスクでは一切行っていない
(¥0、API呼び出し0件、Production `.venv`/`.venv-ci`/コード変更0件)。

参照元一次資料: `TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01_REPORT.md`
(§0-§22、特にStage 1/2/3の実測表)、`TTS-GEMINI-3.8-FLASH-LITE-AB-TRIAL-01_
REPORT.md`(前回モデル・旧Prompt方式でのREJECTED実測)、
`docs/pm/plan_tts_gemini_3_8_flash_lite_next_trial_01.md`。

---

## A. 品質比較

### A-1 現行(gemini-2.5-pro-preview-tts、Structured Separation方式) vs
新モデル(gemini-3.8-flash-lite-tts、`speech_metadata`構造化方式)

| 観点 | 現行Production(A) | 前回Trial: 3.8系+旧Prompt(AB-01、REJECTED) | 今回Trial: 3.8系+`speech_metadata`(NEXT-01、VALIDATED方向) |
|---|---|---|---|
| Prompt/API方式 | `build_tts_prompt`によるStructured Separation(本文内delimiter) | 同じStructured Separationをそのまま3.8系へ流用 | `speech_metadata`(`speaker`/`style`)をAPI構造体として分離送信、本文はverbatim transcriptのまま変更なし |
| SDK | google-genai 2.11.0(Production)/2.14.0(CI) | 2.14.0相当(speech_metadata非対応版) | google-genai==2.25.0(Trial限定導入、Production無変更) |
| 完了率(segment単位、ASR PASS到達) | 17/17(既存canonical記事、完成済み) | 3/17(14/17がSTOPPED、うち重度hallucination多数) | Stage1: 1/1、Stage2: 3/3、Stage3: 12/12(全12segment最終PASS、うち11segment attempt1・1segment attempt2) |
| instruction leakage(指示文の読み上げ) | 発生無し(既存仕様で防止済み) | 頻発(topic_intro/point_one_headingほか、区切り文字列自体を読み上げ) | 0件(Stage1+2+3合計17回のattempt全て`leaked_style_words=[]`) |
| 本文外発話(hallucination) | 発生無し | 頻発(point_one/two/threeで無関係な創作内容[家族の引っ越し・雑貨店等]) | 0件(`TRUE_CONTENT_MISMATCH`はfull_story_part1のattempt1のみ、原因は後述のdigit読み現象でhallucinationではない) |
| retry率 | 記事全体でtension_reflectionのみ実測3回(既存canonical内で吸収) | 17segment中16segmentで追加attempt発生、14segmentは3回使い切っても不合格 | Stage1+2: 0/4がretry。Stage3: 13attempt中1回のみretry(7.7%) |
| 異常長検知(duration anomaly) | 該当なし | 頻発(japanese_title/point_one_heading等) | 全attempt非該当(0件) |
| clipping | 該当なし | 未記録(REJECTED判定の主因ではない) | 全attempt`False` |
| ユーザー試聴結果 | (既存承認済み音声) | 試聴に至っていない(未完成のため見送り) | 「自然で全く問題なし。シーンごとの抑揚・トーンは今後詰めるが、現時点Trialを止めるものではない」(ユーザー逐語、2026-09-27) |

### A-2 "Act One/Two/Three"→digit読みの実測と安全網の挙動

Stage 3(§22.5)で唯一のretryケースとして実測: `full_story_part1`の
canonical本文にある章見出し表現"Act One"/"Act Two"/"Act Three"(綴り文字)
を、新モデルがattempt1では**digit読み**("Act 1"等)で発話し、既存Production
ASR検証パイプラインの数字/否定不一致検出が正しく`TRUE_CONTENT_MISMATCH`と
判定してSTOP、attempt2(style文字列を変えただけ)ではword読みに戻り
`NORMALIZED_MATCH`でPASSした。**安全網(ASR数値検証+retry)は意図どおり
機能した**(誤った内容をそのまま採用させず、retryで是正)。ただしN=1であり、
統計的頻度・再現性は未確認(§G参照)。現行Production側(A)の同一segmentは
"Act one/two/three"のword読みで一貫してASR PASSしており、このリスクは
新モデル固有の観測(3.8系Flash-Liteのみで発生、現行2機種では未観測)。

### A-3 pace/duration差(B/A比、WPM、意図的遅め指示の有無)

| 段階 | 対象segment数 | B/A duration比 | 備考 |
|---|---|---|---|
| Stage 1 | 1(tension_reflection) | 78.9%(62.25秒→49.08秒) | style無し(attempt1、"plain TTS test first") |
| Stage 2 | 3(Voice2種、数値・固有名詞含む) | 79.3%〜82.6% | 同上 |
| Stage 3 | 11(既存音声がある11/12segment、full_story_part2は既存音声なしのため比較対象外) | 85.0%(合計181.43秒→154.20秒) | role別最小style採用(§22.3)、pace指示は含めていない |

一貫してB側がAより短い(現行比 79〜85%)。**現行Production側に意図的な
「わずかに遅く」指示があるのはA2レベルのみ**(`A2_ENGLISH_STYLE_PREFIX_
SLOWER`+生成後6% time-stretch post-process)であり、本Trialが検証した
Family X B1Bレベルの各Roleには元々pace指示が無い(§22.2実コード確認済み)。
したがって、この短縮傾向は「現行の意図的な遅め指示との対比」ではなく、
「pace指示無し同士でも新モデルの方が速く発話する」という素の傾向である。
WPM実測値はStage3結果表(REPORT §22.4)に全segment記録済み(113.6〜189.5)。
「不自然に速すぎないか」は自動チェック(ASR PASS・異常長非該当・指示文
漏れ無し)だけでは判定できず、人間試聴でのみ確認できる(REPORT §21.4-1、
§22参照)。ユーザーの上記試聴結果(A-1参照)は「自然で問題なし」だが、
「シーンごとの抑揚・トーンは今後詰める」という留保が付いている。

### A-4 role別styleの現状と未確定点

Stage 3で採用したrole別最小style(TOPIC_INTRO/PREVIEW/COMMENT/FULL_STORY/
HEADING_READOUT/IN_ONE_LINEの6role、REPORT §22.3)は、**初期案としての
最小限の割り当てであり、正式なshow全体のstyle仕様ではない**。抑揚・
トーンの詰めは未実施(委任文原文が「今後の論点」と明記)。現行Production
のrole別style実態(REPORT §22.2)との対応は下表の通り粗く近似したのみ:

| 現行Role | 現行style_prefix(実装) | Trial側最小style(speech_metadata) |
|---|---|---|
| TOPIC_INTRO | `ENGLISH_STYLE_PREFIX`(Level2 animated) | "brief, clear, engaging news topic introduction" |
| PREVIEW/COMMENT | `B1_PREVIEW_STYLE_PREFIX_CALM`(calm/unhurried、ユーザー正式承認済み) | "calm, conversational" |
| FULL_STORY | `ENGLISH_STYLE_PREFIX`素のまま | "calm, steady news narration" |
| HEADING_READOUT | `ENGLISH_STYLE_PREFIX`(fallback時MINIMAL) | "brief and clear" |
| IN_ONE_LINE | `ENGLISH_STYLE_PREFIX`素のまま | "concise, clear" |

---

## B. Cost比較

### B-1 現行モデル実測(Production実artifact、既存記事)

- **ai_hiring A2(3 Voices、17segment、Key Phrase除く)**: 実測合計
  **約¥36.9**(`er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/
  kp_fix_01/a2/audit/raw_usage_log.jsonl`、TTS-GEMINI-3.8-FLASH-LITE-AB-
  TRIAL-01_REPORT.md §5から転記。`japanese_title`1件はsegmentタグ欠落で
  「既存log欠落」、未取得のまま推定に留めた既存記録)。
- **Hormuz B1B(Family X、12segment、Key Phrase・数値見出し含む本編のみ、
  `gemini-2.5-pro-preview-tts`分のみ集計)**: `er019_output/family_x_audio_
  production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_02/
  raw_usage_log.jsonl`を本タスクで実測集計した結果、B1B対象12segmentの
  gemini TTS呼び出し**36 attempt**(=segmentあたり平均3回、既存の複数
  runにまたがるretry履歴を含む可能性あり[本タスクでは1回のraw_usage_log
  ファイル全体から該当segment名でフィルタしただけであり、run_01からの
  引き継ぎ分が混在している可能性を排除できていない、「未取得」ではなく
  「集計方法の限界」として明記])で合計input_tokens=19,028/
  output_tokens=26,447、公式単価(pricing_snapshot.json、input$1.00/
  output$20.00 per 1M tokens)換算で**約¥87.7**(USD_TO_JPY=160換算)。
  ASR費用は本集計に含めていない(TTS[gemini]分のみ)。

### B-2 Flash-Lite実測(本Trial、Stage 1-3合計)

| 段階 | segment数 | attempt数 | 実費用(TTS+ASR合計) |
|---|---|---|---|
| Stage 1 | 1 | 1 | ¥1.76 |
| Stage 2 | 3 | 3 | ¥3.20 |
| Stage 3 | 12 | 13(うち1segmentのみ2回) | ¥8.72 |
| **合計** | 16(重複無し、Stage1のtension_reflectionは記事外) | 17 | **¥13.68**(Phase 0 SDK確認¥0を含めた管理ID全体累積は`TTS-GEMINI-3.8-FLASH-LITE-NEXT-TRIAL-01_REPORT.md`§17等に個別記載、本パケットはStage1-3のTTS/ASR実費用のみ集計) |

Stage 3(1記事12segment、Hormuz B1B)の実費用¥8.72は、B-1のHormuz B1B
現行実測¥87.7(TTSのみ、ASR別)と**同一記事・同一segment集合**の比較
であり、単純比較では新モデルの方が実費用が低い(ただし B-1のHormuz実測
[36 attempt]は複数run分のretry履歴を含む可能性があり、「既存Production
の1回の完成コスト」としての厳密な公平比較ではない点に注意)。

### B-3 retry込みexpected cost(retry率7.7%を用いた期待値)

Stage 3実測retry率=13attempt中1回=**7.7%**。1回のretryが発生した場合の
追加費用はfull_story_part1の実測から約¥1.5-3(TTS+ASR)程度と推定される
(Stage3結果表の同segment実測¥3.16[2attempt合計]から、1attempt分は
概算¥1.5前後)。したがって12segment規模の記事の期待値は、
「平均12segment×約¥0.7/segment(Stage3実測¥8.72÷12.083相当attempt)+
retry発生確率7.7%×追加¥1.5」という程度の粗い見積りに留まる。**N=1回の
Trial実行結果からの外挿であり、統計的信頼区間は無い**(退行や別記事での
再現性は未検証、§G参照)。

### B-4 A2/B1量産時の概算(前提条件明記)

- 前提: Stage1-3で観測された「attempt1回で概ね成功、retry率一桁%」という
  傾向が、他のFamily/レベル/記事でも同程度に再現すると仮定した場合の
  概算(**仮定であり実証ではない**)。
- Family X B1B相当記事(12segment程度)1本あたり: 概算¥9-15程度
  (Stage3実測¥8.72+retry余裕)。
- ai_hiring A2相当(17segment、3 Voices)記事1本あたり: 実測データが
  無いため**未取得**(Stage1-3はいずれもFamily X B1BまたはA2の一部
  segmentのみで、A2記事全体[17segment]をFlash-Liteで完走させた実測は
  無い)。

---

## C. Latency/throughput

| 指標 | 実測値 |
|---|---|
| TTS latency(1呼び出しあたり、Stage3実測13回平均) | 約6.15秒/回 |
| ASR latency(1呼び出しあたり、Stage3実測13回平均) | 約1.19秒/回 |
| 記事全体(12segment、13attempt)の合計latency | TTS約79.9秒+ASR約15.5秒 |
| retry発生時の影響 | full_story_part1のみ2attempt(TTS 12.65秒+12.07秒、ASR 2.01秒+2.14秒)、記事全体を止めることなく後続segmentは独立して生成継続(§22.6-2の設計確認) |

**Production同時実行時のrate limit**: 未確認。計画doc(§12補足)の記載通り、
Gemini公式rate-limitページはモデル別RPM/TPM表がJS動的レンダリングのため
静的HTML取得では確認できていない。本Trialの実行規模(1記事12segment、
最大36 API呼び出し)でのみ動作確認しており、Production相当の同時実行数・
日次記事数でのrate limitは**未取得**。

**追加実測が必要な項目(提案のみ、有料負荷試験は実施しない)**:
1. 複数記事の同時並列生成時のrate limit挙動(429エラー有無)。
2. retry率が7.7%より高くなった場合の記事完成までの総latency分布
   (N=1では測れない)。
3. Batch Mode(price表に存在するが本Trialでは未使用)の活用可否。

---

## D. SDK/Runtime影響

### D-1 現状のSDKバージョン相違(3系統が並存)

| 環境 | google-genai version | 用途 |
|---|---|---|
| Production `.venv`(実行時に使われる本番仮想環境) | **2.11.0** | 記事生成・音声合成の実運用 |
| `.venv-ci`(requirements-ci.txt記載) | **2.14.0** | ローカルCIテスト基盤専用(本番コードの依存関係全体を表すものではない、requirements-ci.txt冒頭の注記どおり) |
| `.venv_trial_genai225`(本Trial専用) | **2.25.0** | Flash-Lite `speech_metadata`検証専用、Production非混入 |

Production採用時は、Production `.venv`へ2.25.0(またはそれ以降の
`speech_metadata`対応版)を導入する作業が別途必要(本Trialでは未実施)。
2.11.0→2.25.0は14マイナーバージョンの差があり、`speech_metadata`以外の
未知の破壊的変更が無いかは本Trialの範囲では確認していない(§10で
「既存TTS呼び出しとの互換性」は2.14.0/2.25.0双方の隔離venvで確認済みだが、
確認対象は既存TTS関連unit test 9ファイルに限定され、Production venv全体
[TTS以外のGemini利用箇所含む]の網羅的な回帰確認ではない)。

### D-2 Regression範囲

`run_project_regression.py`は`er0*_test_*.py`パターン(`_test_`を含む
ファイル名限定)でdiscoverする設計。本Trialが実行した既存TTS関連unit test
9ファイル(er002_test_common/er003_test_b1_p3v_capability/
er003_test_b1_p4c_audio/er003_test_b1_p7a_audio/er003_test_b1_p9a_audio/
er003_test_b1_p9a_r1_audio/er003_test_audio_tts_asr_safety/
er003_test_v1_n3_01_tts_generate/er003_test_key_words_canonicalization、
合計264+ケース)は全てOKだったが、これは`run_project_regression.py`の
discover対象全体(現在collected 3300+件規模)のごく一部であり、**SDK
更新がProduction venv全体の回帰へ与える影響は、本Trialでは未確認**
(Production venv自体を2.25.0へ更新した状態でのフル回帰実行は行っていない、
本Trialは隔離venvでの部分実行のみ)。

### D-3 他のGemini利用箇所への影響(Grep結果一覧)

`google.genai`/`genai.Client`/`generate_content`をGrepした結果、
Production対象ファイルとして以下が該当(Trial専用ファイルを除く):

- `er002_gemini_client.py`(Geminiクライアント共通初期化と思われる、SDK
  更新の影響を最も直接受ける可能性が高い箇所)
- `er003_b1_p7a_audio.py`(TTS呼び出し本体)
- `er003_b1_p3v_capability.py`
- `er003_v1_b1_p3v_generate.py` / `er003_v1_b1_p7a_generate.py`
- `er003_v1_repro01_main_generate.py`
- `er006_model_routing_contract_01.py`
- `er006_batch_tts_wiring_01.py`(Batch Mode関連)
- `er005_avr02_instruction_separation.py`
- `er005_e2e_research_ab_01_p1.py` / `er005_model_ab_01a_phase1.py`
- `er008_n7_baseline_reset_01.py` / `er008_n7_pilot_run_01.py`
- `er011_open121_tts_repetition_general_qa_trial_01.py` /
  `er011_open107_opened_tts_diagnostic_trial_01.py` /
  `er011_kp_display_tts_separation_prod_wiring_01.py` /
  `er011_tts_execution_mode_switch_wiring_01_test.py`
- `er001b*`系(過去のNarrator/Direction/Intensity/Connected Narration
  比較スクリプト群、現行稼働中かは未確認)

**未確認事項**: 上記ファイルのうち、どれがSDK型定義の変更(2.11.0→2.25.0)
で実際に動作へ影響を受けるかは、個別のコードレビュー・実行確認をしていない
(本タスクの範囲外、SDK実更新時に必要な作業として§Gへ記録)。

### D-4 Rollback案

Production `.venv`のgoogle-genaiをピン留めしたまま(2.11.0)、Trial限定
venvでの検証を継続する現状維持が最も低リスク。仮にProduction `.venv`へ
2.25.0を導入した場合、問題発生時は`pip install google-genai==2.11.0`で
即座に旧バージョンへ戻せる(requirements的な構造上の障害は無い、本Trial
確認済みの`pip check`はいずれのバージョンでも依存衝突なし)。ただし
ロールバック運用手順そのもの(誰がいつ判断するか)は未設計。

---

## E. Production配線案

### E-1 候補比較

| 案 | 内容 | 長所 | 短所/リスク |
|---|---|---|---|
| (1) 現行維持 | Flash-Lite不採用、gemini-2.5-pro-preview-tts/3.1-flash-tts-previewを継続 | リスクゼロ、追加作業不要 | コスト削減機会(B-2実測で示唆)を見送る |
| (2) Family Xのみ先行 | Hormuz B1B等Family Xの配線経路のみFlash-Liteへ切替、Family A/Zは現行維持 | 本Trialの実測範囲(Family X B1B)と一致、リスク限定 | 複数モデル運用の複雑化(model routing/pricing_snapshot/cost_logger等が2系統併存) |
| (3) Family A/X/Z共通TTS pathへ配線 | 全Family一括切替 | 運用一本化 | Family A(A2/B1、3 Voices・Key Phrase含む)・Family Z(TTS未実装スタブ)は本Trialで未検証、リスク大 |
| (4) 段階導入 | (2)を先行し、role別style確定・追加記事でのretry率再現性確認後にFamily Aへ拡大 | 実測に基づき拡大判断できる、既存の「1記事ずつ完結」原則と整合 | 期間が長くなる |

### E-2 各案と既存機構との整合(表)

| 既存機構 | 本Trialでの扱い | Production配線時に必要な作業 |
|---|---|---|
| initial/retry/fallback(3回上限、標準2+fallback1) | Stage1-3ともTrial独立orchestrationループとして`PRODUCTION_MAX_TTS_ATTEMPTS`等の値のみ参照し、実装は独立コード(Production関数を呼んでいない) | 実際の`generate_charon_english`等Production関数内部で`speech_metadata`方式を使う実装への置き換えが必要(現状は未実装、Trial scriptのみ) |
| regeneration(Human Review Lock経由の再生成) | 未接続(Trial-local判定のみ、REPORT§22.8-4明記) | `er011_human_review_lock_01`との実配線が必要 |
| Human Review Lock | 未接続 | 同上 |
| ASR validation | 既存Production関数(`er006_preprod_hardening_01_validation.classify_asr_match`等)をそのままimportして使用(結果整合性は確認済み) | 配線自体は流用可能、Production呼び出し経路への差し込み位置の設計が必要 |
| pronunciation・reading resolver(発音注入) | **未接続**。Trialは`speech_metadata`のstyleフィールドのみを使い、既存のstyle prefix経由発音注入(pronunciation_ledger等)との統合方法は未検証 | speech_metadata方式で発音注入をどう表現するか(style文字列へ埋め込む/別途annotationを使う等)の設計が必要、§F参照 |
| A2 6% slowdown post-process | 本Trial対象(B1B)には適用されないため未検証(REPORT§22.8-5) | A2記事へ適用する場合、新モデル出力へそのままpost-processを適用するか、新モデル用に再調整するか要検討 |
| role別style | Stage3で最小限案を新規実装(既存style_prefix定数とは別体系) | 正式仕様化するかはユーザー判断待ち(§I) |
| voice指定 | 既存Voice名(Charon/Aoede/Erinome)をそのまま使用、Voice指定自体はモデル間で共通動作を確認済み | 追加作業不要 |
| cost ledger・telemetry | Trial専用パスにのみ記録(共有store非書込みを原則として実装、§22.6-3の1件のみ意図せず例外) | Production cost_logger/pricing_snapshotへの正式統合が必要(pricing自体は既に登録済み、§5) |

---

## F. Dangling Reference Check

Flash-Lite側のrole別style(§A-4、Stage3で新規実装した6role分類・最小
style文字列)は、**現行Production仕様(CURRENT_SPEC.md)のどこにも
存在しない未承認の新しい体系**である。現行仕様が定めるのは
`ENGLISH_STYLE_PREFIX`/`B1_PREVIEW_STYLE_PREFIX_CALM`/
`A2_ENGLISH_STYLE_PREFIX_SLOWER`という既存3種のみであり、Trial側の
role別最小style(TOPIC_INTRO/PREVIEW/COMMENT/FULL_STORY/HEADING_READOUT/
IN_ONE_LINEの6分類)はこれらと**厳密には対応していない独自の初期案**
(REPORT§22.3が「必要最小限」の初期案と明記)。**この6role分類・style文字列
はProduction仕様として扱わない**(Trial専用、ユーザー承認済みProduction
仕様への格上げは未実施)。

同様に、Trial実装(`er022_tts_gemini_3_8_flash_lite_next_trial_01_stage*.py`)
はProduction関数の一部(ASR routing・英語6分類Validator・異常長検知)を
importして使うが、Human Review Lock・pronunciation resolver・cost logger
共有store・A2 slowdown post-processへは接続していない(意図的な独立
実装、REPORT§20/§22.7で確認済み)。これらの未接続部分は、Production
初回pathが依存する既存機構への参照が「存在しない」のではなく「意図的に
まだ繋いでいない」状態であり、採用判断時にはこれらの機構との統合設計
(§E-2)が必須の残作業となる。

---

## G. Production採用前の残作業

### G-1 採用判断前に確認すべきもの

1. SDK 2.25.0(またはそれ以降)をProduction `.venv`へ実際に導入した状態
   での、`run_project_regression.py`フル回帰(現状collected 3300+件規模)
   の実行(本Trialは隔離venvでの部分test 9ファイルのみ)。
2. rate limit・concurrency(§C、Production相当の同時実行数での挙動は
   未確認)。
3. "Act One"型(綴り文字の順序・章見出し表現)のdigit読みリスクの追加
   確認(N=1のみ、他記事・他表現での再現性未検証)。
4. role別style正式仕様化の要否(§A-4、現状は初期案どまり)。
5. A2 6% slowdown post-processとの関係(新モデルは元々発話が速い傾向
   [§A-3]があるため、slowdown post-processをそのまま適用するとどうなるか
   の検証が必要)。
6. Family別配線範囲の決定(§E-1、現行はFamily X B1Bのみ検証済み、
   Family A[A2/B1、Key Phrase含む]・Family Z[TTS未実装]は未検証)。
7. 現行モデルとの記事単位cost比較の精緻化(§B、Hormuz実測はretry履歴の
   混入可能性があり「既存Productionの1回の完成コスト」との厳密な比較には
   なっていない)。

### G-2 採用承認後にProduction wiringで必要なもの

1. Production `.venv`のgoogle-genaiバージョン更新(2.11.0→2.25.0以降)。
2. `er003_b1_p7a_audio`等TTS呼び出し本体を、Structured Separation方式
   から`speech_metadata`方式へ実装変更(現状はTrial独立scriptのみ)。
3. Human Review Lock・pronunciation resolver・A2 slowdown post-process・
   cost logger・pricing_snapshotとの正式統合。
4. retry/fallback構成(標準2+fallback1)を、`speech_metadata`方式の
   実際のProduction関数内部へ再実装(現状はTrial独立orchestrationループ)。
5. §22.6-3で発生した共有store(`er021_output/en_asr_semantic_equivalence_
   production_wiring_01/telemetry.jsonl`)への意図しない4行書込みの
   後始末(下記I参照、USER_DECISION_REQUIRED)。

---

## H. 推奨案(Fable向け素案、最終採否はユーザー)

**Sonnetからの素案**: QCD(品質・コスト・納期)の実測結果を総合すると、
Stage 1-3の範囲(Family X B1B、12segment、Voice2種、数値/固有名詞/幕番号
表現を含む)では、Flash-Lite(`speech_metadata`方式)は現行モデルに対し
**品質面で同等以上(instruction leakage/hallucination 0件、ユーザー試聴で
自然と評価)、コスト面で明確に有利(同一記事でTTS実費用が現行実測の
1/10程度)**という結果が出ている。一方で、SDKバージョン更新・Production
実配線・既存安全機構(Human Review Lock/pronunciation resolver/A2
slowdown)との統合・role別styleの正式仕様化はいずれも未着手であり、
「今すぐ全Family一括採用」するにはリスクが大きい。

したがって、Sonnet素案としては**E-1の(4)段階導入**(まずFamily X B1Bで
Production先行導入し、G-1の残論点[特にSDK regression・rate limit・
Act One型追加確認]をクリアしてからFamily A/Zへ拡大)を推奨する。ただし
これはあくまで判断材料としての素案であり、Fableが自身の評価・推奨を
加えた上でユーザーへ報告し、最終採否・採用範囲はユーザーが判断すること
(繰り返し明記: Sonnet/Fableが`APPROVED_FOR_PRODUCTION`へ変更することは
できない)。

---

## I. Status/PM

- Flash-Lite(`speech_metadata`方式)のStatus: **`VALIDATED`のまま**
  (Stage1-3の範囲でTrialとして機能することを確認、という意味に限定。
  Production採用[`APPROVED_FOR_PRODUCTION`]ではない)。
- **USER_DECISION_REQUIRED(新規、本パケット起因)**:
  1. Flash-Lite(`gemini-3.8-flash-lite-tts`、`speech_metadata`方式)を
     Production採用するか。
  2. 採用する場合の範囲(Family Xのみ先行/複数Family同時/条件付き、
     §E-1・§H参照)。
  3. 採用する場合、role別style方針(Stage3の6role最小案を正式仕様化する
     か、追加のトーン調整Trialを行うか)。
- **USER_DECISION_REQUIRED(既存、再掲・ユーザー既決事項の再確認ではない
  別件)**: §22.6-3で発生した共有telemetry(`er021_output/en_asr_semantic_
  equivalence_production_wiring_01/telemetry.jsonl`末尾1624-1627行)への
  意図しない4行書込みについて、ユーザーは「残置」を既に承認済み
  (2026-09-27、本パケット冒頭「ユーザー既決」参照)。**close済み**
  (再度の判断は求めない、由来[Stage3実行中の一時的コード変更による副作用、
  Production Gate・Cost・記事生成には影響しない観測専用ログ]・行番号は
  本パケットとOPEN_ITEMS.md OPEN-201に記録)。
