# DECISION_LOG — 確定した意思決定の索引

**管理ID: ER-PM-001**
**最終更新: 2026-08-12(ER-003-A2-SPEC-FREEZE-01)**

確定した意思決定と、その理由・根拠を記録する。個別のDecision Record原本
(`er003_output/p2i/ER-003-P2I_decision_record.md`等)は削除せず、本ファイルは
それらへの**索引**として機能する。未決事項は書かない(→[OPEN_ITEMS.md](OPEN_ITEMS.md))。

各Decisionは最低限、Decision ID／日付／内容／状態／採用理由／比較した
選択肢／却下理由／根拠レポート／commit／影響するCURRENT_SPEC項目を持つ。

---

## ER-003-B1-P7A: Preview TTSモデルをgemini-3.1-flash-tts-previewへ

- **日付**: 2026-08-06
- **内容**: Previewの日本語音声生成モデルを`gemini-2.5-pro-preview-tts`から`gemini-3.1-flash-tts-preview`へ切替
- **状態**: `DECIDED`
- **採用理由**: 旧モデルで「激しい」→「げきせつな」等の誤読が発生。3.1へ切替後、単一call検証で解消を確認
- **比較した選択肢**: 2.5継続 vs 3.1切替
- **却下理由(2.5継続)**: 誤読の再現性が高く、Preview用途に不適
- **根拠レポート**: ER-003-B1-P7A実行報告(18項目)
- **commit**: `b4f871f`
- **影響するCURRENT_SPEC項目**: Preview > TTS model

## ER-003-B1-P5A〜P5C: Google Cloud TTS(Neural2-B)を不採用

- **日付**: 2026-07-26頃
- **内容**: 日本語TTSエンジンとしてGoogle Cloud TTS(Amazon Pollyも候補)を検証したが不採用
- **状態**: `REJECTED`
- **採用理由**: (該当なし、不採用)
- **比較した選択肢**: Google Cloud TTS Neural2-B、Gemini TTS
- **却下理由**: ユーザー試聴で機械的な音声・誤読(「何が」→「なんが」)と判定され不合格
- **根拠レポート**: P5A/P5B/P5B-GCP/P5Cの各commit
- **commit**: `ffe9cc9`, `0fe94eb`, `8193e0b`, `e2b75b7`
- **影響するCURRENT_SPEC項目**: Full Story/Preview > TTS model(Gemini採用の背景)

## ER-003-P2I: Key Phrase選定方式にStrategy L(Listening Blocker Ranking)を採用

- **日付**: 2026-07-xx
- **内容**: B2 Key Words選定の標準方式として方式L(Listening Blocker Ranking)を採用
- **状態**: `DECIDED`
- **採用理由**: 「初回リスニングで理解を止める可能性が高い表現を選ぶ」という単純で説明可能な原則、個別学習者プロファイルへの依存がない
- **比較した選択肢**: 方式L(Listening Blocker Ranking)/方式P(Difficulty Portfolio)/方式U(Observed Learner Profile)。Top5評価はL・Uが同点
- **却下理由(P)**: Top5・Total双方の評価で他方式に劣る
- **却下理由(U)**: 標準方式としては不採用(将来のパーソナライズ機能候補として保持)
- **根拠レポート**: [ER-003-P2I_decision_record.md](er003_output/p2i/ER-003-P2I_decision_record.md)
- **commit**: `e33f227`
- **影響するCURRENT_SPEC項目**: Key Phrase > 選定方式

## ER-003-REPRO-01-KP: B1本文からKey Phraseを新規選定する方針へ訂正

- **日付**: 2026-08-08
- **内容**: Key PhraseはB2時代の承認済みリストを流用せず、各記事自身のCEFR-B1本文から方式Lで新規選定する
- **状態**: `DECIDED`
- **採用理由**: ユーザー指摘により、B2時代の選定結果をB1へ流用する前提が誤りと判明
- **比較した選択肢**: B2承認済みリストの流用 vs B1本文からの新規選定
- **却下理由(流用)**: 記事本文がB1で書き直されている以上、選定根拠が古い
- **根拠レポート**: ER-003-REPRO-01-KP実行報告
- **commit**: `46aa2e8`
- **影響するCURRENT_SPEC項目**: Key Phrase > 選定元

## ER-003-KP-01: Pedagogical Phrase Canonicalizationの導入

- **日付**: 2026-08-08
- **内容**: Strategy Lの`display_phrase`を自然な学習単位`key_phrase`へ正規化する後処理段階を新設
- **状態**: `DECIDED`
- **採用理由**: `display_phrase`のまま採用すると学習単位として不自然/過不足がある場合がある
- **根拠レポート**: ER-003-KP-01実行報告、[er003_key_words_canonicalization.py](er003_key_words_canonicalization.py)
- **commit**: `e607d26`(Canonicalization本体)、`ae4928c`(3状態QAモデルへ拡張)
- **影響するCURRENT_SPEC項目**: Key Phrase > 後処理、QAモデル

## ER-003-KP-02: Canonicalization原則を「最小」から「最小十分」へ

- **日付**: 2026-08-08
- **内容**: Canonicalizationの目標を単なる「最小化」から「意味を保ったまま最小十分」へ修正
- **状態**: `DECIDED`
- **採用理由**: 「最小」を追求すると意味を保持する語まで削ってしまうリスクがある(over-minimization)
- **根拠レポート**: ER-003-KP-02実行報告
- **commit**: `8856264`
- **影響するCURRENT_SPEC項目**: Key Phrase > Canonicalization原則

## ER-003-KP-02-R1: Meaning Preservation Ruleの追加とTraceability再定義

- **日付**: 2026-08-08
- **内容**: (1) 意味保持QA(`qa_core_meaning_preserved`/`qa_no_semantic_role_loss`)を追加。(2) Traceability要件を「literal substring」から「source_spanから説明可能な正規化で導出できる」へ再定義。`normalization_reason`フィールド(固定enum)を追加
- **状態**: `DECIDED`
- **採用理由**: 「take a player off」(A01既承認)のような正当な文法的正規化が、旧Traceability定義では誤ってFAILと判定されていた
- **比較した選択肢**: 文字通りの部分文字列一致を維持 vs 説明可能な正規化まで許容
- **却下理由(維持)**: 既承認の正当な正規化ケースを説明できない
- **根拠レポート**: ER-003-KP-02-R1実行報告(16項目)
- **commit**: `5a94db0`
- **影響するCURRENT_SPEC項目**: Key Phrase > Traceability定義、`normalization_reason`

## used_form / key_phrase の重複を技術的負債として記録し整理しない

- **日付**: 2026-08-08
- **内容**: `used_form`が常に`key_phrase`と一致する(100%重複)ことを確認したが、実際に分ける必要が生じるまでリファクタリングしない
- **状態**: `DECIDED`(整理しないこと自体が決定事項)
- **採用理由**: ユーザー指示。「不要な分岐ロジックを増やさない」
- **根拠レポート**: ER-003-KP-02-R1承認時のユーザー発言
- **commit**: `5a94db0`(承認と同時のcommit)
- **影響するCURRENT_SPEC項目**: Key Phrase > `used_form`/`key_phrase`の関係。[OPEN_ITEMS.md](OPEN_ITEMS.md)にも技術的負債として記載

## strict ASR検証(部分一致+文字数上限)の追加

- **日付**: 2026-08-08
- **内容**: 短文ナレーションのASR検証を、部分一致だけでなく「ASR文字数が期待文字数を大きく超えていないか」も確認するよう強化
- **状態**: `DECIDED`
- **採用理由**: A02 meaning_5で、部分一致のみの検証が28.8秒のhallucination音声(目的の文言+26秒以上の無関係な創作内容)を誤って合格判定した
- **根拠レポート**: ER-003-REPRO-01-MAIN実行報告
- **commit**: `a13d97c`, `a70736d`
- **影響するCURRENT_SPEC項目**: Full Story > strict ASR検証

## minimal instruction fallbackを英語Key Phrase Componentへも一般化

- **日付**: 2026-08-08
- **内容**: 標準経路(`ENGLISH_STYLE_PREFIX`)が規定回数不合格の場合、最小限instructionへ自動フォールバックする仕組みを、短文ナレーションだけでなく英語Key Phrase Componentにも適用
- **状態**: `DECIDED`
- **採用理由**: A02のKey Phrase"opt out"が標準経路で6回とも無関係な内容を生成。フォールバックで1回で解決
- **根拠レポート**: ER-003-REPRO-01-MAIN実行報告
- **commit**: `a13d97c`
- **影響するCURRENT_SPEC項目**: Full Story > minimal instruction fallback

## Dynamics3を不使用、scalar RMS gainのみ採用

- **日付**: 2026-08-07(P9A時点で確立)
- **内容**: 音量調整にDynamics3(ダイナミックレンジ圧縮)を使わず、scalar gainのみで行う
- **状態**: `DECIDED`
- **採用理由**: コード内コメントに明記(理由の詳細な比較記録は未発見、[OPEN_ITEMS](OPEN_ITEMS.md)に記録漏れとして記載)
- **根拠レポート**: `er003_b1_p9a_audio.py`内コメント
- **commit**: `dcc6d8a`(P9A初版)
- **影響するCURRENT_SPEC項目**: Full Story > Dynamics処理

## 複数箇所編集は「後ろから前へ」の順序を徹底

- **日付**: 2026-08-07
- **内容**: 1つの音声ファイルへ複数箇所の時間軸編集を適用する場合、時系列で後ろにある編集から先に適用する
- **状態**: `DECIDED`
- **採用理由**: P7Cで5箇所の英語Key Phrase差し替えを1ループで同時処理した際、中間箇所の無音調整が既処理済み箇所のインデックスずれの影響を受けるバグが発生(目標0.40秒に対し実測0.145〜0.560秒)
- **根拠レポート**: [ER-003_PIPELINE_CROSS_CUTTING_RULES.md](ER-003_PIPELINE_CROSS_CUTTING_RULES.md) 2節
- **commit**: `b32c6e7`(バグ修正)
- **影響するCURRENT_SPEC項目**: Audio Assembly > 複数箇所編集の順序

## MFA単独では数字・日付境界を確定しない

- **日付**: 2026-08-07
- **内容**: MFAで境界を決めても、必ずASRまたは他の診断で妥当性を裏付ける
- **状態**: `DECIDED`
- **採用理由**: "England 1–2 Argentina"が実際には"England one, Argentina two"の語順で発話されており、書字通りの語順でMFAへ渡したため直前語の境界を誤認識(70.630秒→正しくは70.960秒)
- **根拠レポート**: ER-003-B1_HANDOFF.md、[ER-003_PIPELINE_CROSS_CUTTING_RULES.md](ER-003_PIPELINE_CROSS_CUTTING_RULES.md)
- **commit**: `d2aa9e6`(バグ修正)
- **影響するCURRENT_SPEC項目**: Audio Assembly > 境界検出、数字・日付境界

## ASR homophone ambiguityをhallucinationと区別し、2段階human reviewフローで扱う

- **日付**: 2026-08-09
- **内容**: TTS音声が正常でもASRが同音異義語を誤選択しstrict検証が機械的に不合格になり続ける事象を、hallucination(無関係な内容の生成)とは別の不具合分類として扱い、`PROVISIONALLY_ACCEPTED_REQUIRES_HUMAN_REVIEW`→ユーザー試聴→`ACCEPTED_AFTER_HUMAN_REVIEW`の2段階フローで確定する
- **状態**: `DECIDED`
- **採用理由**: ADD03 meaning_3「航行の自由」がASRに「高校の自由」と誤認識され続けたが、ユーザー試聴の結果TTS音声自体は正常と確定
- **比較した選択肢**: 無限retry / 機械的forced accept / human review flag
- **却下理由(無限retry)**: 同音異義語バイアスは系統的でretryでは解決しない
- **却下理由(機械的forced accept)**: 誤りである可能性を排除できない
- **根拠レポート**: [ER-003-B2-AUDIT-01_SPEC_AUDIT.md](ER-003-B2-AUDIT-01_SPEC_AUDIT.md)、ADD03 audio_validation_main.md
- **commit**: `1b62a20`(発見)、`c4a762c`(ユーザー試聴後の確定)
- **影響するCURRENT_SPEC項目**: QA / Human Review > ASR homophone ambiguity対応

## A02・ADD03の量産再現性判定: 量産候補として採用可能

- **日付**: 2026-08-09
- **内容**: A02・ADD03が2記事連続で、記事固有のハードコードを増やさずに初回通し候補がそのままユーザーOKに到達したことから、「量産候補として採用可能」と判定。ただし完全無人公開は不可、最終ユーザー試聴を必須ゲートとして維持
- **状態**: `DECIDED`
- **採用理由**: 2記事連続成功、発生した不具合(hallucination/ASR ambiguity)がいずれも安全に検出・処理できた
- **根拠レポート**: [ER-003-REPRO_BASELINE.md](ER-003-REPRO_BASELINE.md) ER-003-REPRO-FINAL章
- **commit**: `c4a762c`
- **影響するCURRENT_SPEC項目**: QA / Human Review > 量産再現性判定

## ER-002実験(A01・A02の初回音声)を破棄し、ER-003アーキテクチャへ全面移行

- **日付**: 2026-07-19(ユーザー評価)〜2026-08-06(ER-003開始)
- **内容**: ER-002-S3で生成・試聴したA01(サッカー)・A02(SNS)の初回音声を、編集的に不十分と判断して破棄。改訂版(v1.1B)も再度拒否。Natural English Source→CEFR B1/B2/A2独立生成というER-003の新アーキテクチャへ全面移行
- **状態**: `DECIDED`(移行済み)、旧成果物は`HISTORICAL`
- **採用理由**: ユーザー評価で「台本は事実の羅列に近く、切り口が弱い」(A01)、「記事選定と台本内容の両方が不十分」(A02)と判定
- **却下理由**: 編集的失敗(`COMMON_SCRIPT_EDITORIAL_FAILURE`/`TOPIC_SELECTION_AND_SCRIPT_EDITORIAL_FAILURE`)
- **根拠レポート**: `er002_output/A01/user_evaluation.json`、[ER-003-B2-AUDIT-01_SPEC_AUDIT.md](ER-003-B2-AUDIT-01_SPEC_AUDIT.md)
- **commit**: `ed0f786`(ER-002側記録)、ER-003開始は`fcb1387`等
- **影響するCURRENT_SPEC項目**: (アーキテクチャ全体の前提)

## ER-003-A2-STRUCT-02: A2超一般語5語制限を不採用

- **日付**: 2026-08-09
- **内容**: ER-003-A2-03で試行した「A2超一般語を記事全体で最大5語に制限する」仕様を不採用とする。今後のA2生成prompt・QAの必須条件にしない
- **状態**: `REJECTED`
- **採用理由**: (該当なし、不採用)
- **比較した選択肢**: 数値上限を維持し反復修正機構を新設する vs 数値上限を撤廃し「平易な語を優先する」原則のみ残す
- **却下理由**: **A2-03で実測が目標(5語)を達成できなかったこと自体を主理由とはしない。** (1) 正式CEFR-A2語彙リストがリポジトリに存在せず、LLM semantic QAでは`ahead`/`reach`/`lead`/`still`/`move`/`deal`/`market`等までA2超と判定されるなど判定基準が安定しない(=厳密なCEFR語彙判定基盤がない)、(2) 厳密な5語制限の達成には生成→語彙QA→再生成という反復処理が必要になり量産フローが複雑化する(=運用が複雑になる)、(3) ルールの複雑化に対してユーザーが感じるリスニング難易度改善効果が十分確認できなかった。この3点を理由に、今回は数値上限の導入を断念する
- **根拠レポート**: [ER-003-A2-03_LISTENING_SIMPLIFICATION.md](ER-003-A2-03_LISTENING_SIMPLIFICATION.md) 8節、ER-003-A2-STRUCT-02(ユーザー指示による理由の明確化、2026-08-09)
- **影響するCURRENT_SPEC項目**: A2言語仕様(→[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、数値上限なしの「平易な語を優先」原則のみ残す)

## ER-003-A2-STRUCT-02: 抽象語→具体的行動表現への一律変換を不採用

- **日付**: 2026-08-09
- **内容**: ER-003-A2-03で試行した「抽象的な表現を『誰が何をしたか』という具体的行動表現へ優先的に変換する」一般ルールを不採用とする
- **状態**: `REJECTED_AS_GENERAL_RULE`
- **採用理由**: (該当なし、一般ルールとしては不採用。個別の編集判断としては引き続き有効な手段)
- **比較した選択肢**: 一律の変換ルールとして必須化する vs 記事・文脈ごとの通常の編集判断に委ねる
- **却下理由**: 具体化によって理解しやすくなるケースは実際に存在したが、抽象概念を無理に具体的行動へ置換すると元の意味関係が見えにくくなったり説明がかえって長くなったりするケースもあり、「抽象表現は悪い/具体表現は良い」という一方向ルールは成立しないと判断
- **根拠レポート**: [ER-003-A2-03_LISTENING_SIMPLIFICATION.md](ER-003-A2-03_LISTENING_SIMPLIFICATION.md) 10節
- **影響するCURRENT_SPEC項目**: A2言語仕様(→[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、一般ルールとしては採用しない)

## ER-003-A2-STRUCT-02: 固有名詞密度低減を不採用

- **日付**: 2026-08-09
- **内容**: ER-003-A2-03で試行した「固有名詞のtoken数・密度を意図的に下げる」一般ルールを不採用とする
- **状態**: `REJECTED`
- **採用理由**: (該当なし、不採用)
- **比較した選択肢**: 密度目標・数量目標を設けて維持する vs 目標を撤廃し通常の編集判断(記事理解上の必要性)に委ねる
- **却下理由**: A01では固有名詞トークン数が減った(49→40)一方、ADD03ではTrumpを明示的主語にした結果増加した(18→24)。固有名詞削減を目的化すると、「誰が何をしたかを明確にする」「referentを明確にする」「spoken-firstにする」という別の分かりやすさ要求と競合することが判明。このための追加ルール・計測の維持は量産フローを不必要に複雑化する
- **根拠レポート**: [ER-003-A2-03_LISTENING_SIMPLIFICATION.md](ER-003-A2-03_LISTENING_SIMPLIFICATION.md) 14節
- **影響するCURRENT_SPEC項目**: A2言語仕様(→[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、密度目標は設けない)

## ER-003-A2-STRUCT-02: Spoken-firstをA2の継続仕様として採用

- **日付**: 2026-08-09
- **内容**: ER-003-A2-03で試行した「読んだときの洗練より、一度聞いたときに意味を取りやすい自然な英語を優先する」spoken-first方針を、A2原稿生成の継続仕様として採用する。主語を早く出す、動詞を早く出す、長い前置詞句・名詞句を文頭に置きすぎない、文末まで聞かないと意味が確定しない構造を避ける、を運用原則とする。厳格なsyntax validatorにはせず、自然さを損なう機械的書き換えは行わない(style / generation principleとして運用)
- **状態**: `ADOPTED`
- **採用理由**: 音声だけでニュースを理解する際の負荷軽減に資すると判断
- **比較した選択肢**: 厳格な文法チェッカーとして実装する vs style原則としてprompt指示にとどめる
- **却下理由(厳格チェッカー化)**: 自然な英語らしさを損なうリスクがあるため、機械的な検証・強制は行わない
- **根拠レポート**: [ER-003-A2-03_LISTENING_SIMPLIFICATION.md](ER-003-A2-03_LISTENING_SIMPLIFICATION.md) 11節
- **影響するCURRENT_SPEC項目**: A2言語仕様(→[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、「維持」項目としてSpoken-firstを明記)

## ER-003-A2-STRUCT-02: 1文1数字ルールを維持、日付は1つの数字情報として扱う方向で整理

- **日付**: 2026-08-09
- **内容**: ER-003-A2-03で導入した「1文1数字」原則(年齢範囲・スコア・時間帯は例外)は撤回せず、A2 Prototype仕様として維持する。加えて、"July 13, 2026"のような「月+日+年」の日付表記は、年齢範囲・スコア・時間帯と同様に**1つの日付情報として扱う**方向で整理する
- **状態**: `DECIDED`(原則の整理のみ。checker実装は今回見送り)
- **採用理由**: 日付を1つの意味単位として扱うことは、既存の例外(年齢範囲・スコア・時間帯)と同じ考え方に合致する
- **比較した選択肢**: 例外リストへ正式に追加しchecker実装も更新する vs 原則の解釈のみ整理し実装は見送る
- **却下理由(即時のchecker実装)**: この整理のためだけに数字QAロジックの改修を今回は行わない(小規模な変更ではあるが、他の優先事項がある中で今回のスコープには含めない)
- **根拠レポート**: [ER-003-A2-03_LISTENING_SIMPLIFICATION.md](ER-003-A2-03_LISTENING_SIMPLIFICATION.md) 9節、[OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-18
- **影響するCURRENT_SPEC項目**: A2言語仕様(→[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、1文1数字の例外定義)

## ER-003-A2-SPEC-FREEZE-01: A2言語・構造仕様をPROTOTYPEからDECIDEDへ昇格

- **日付**: 2026-08-12
- **内容**: ER-003-A2-01〜03・ER-003-A2-STRUCT-02〜05で検証してきたA2の
  言語方針(Natural English Source独立生成、総語数を削らない、平均文長
  11語以下・最長18語以下、1文1メッセージ、SVO中心・関係詞節/分詞構文/
  複雑な受動態を避ける、Spoken-first、Simple AND Natural要件)と構造仕様
  (11パート構造、Comment1〜4の役割、Full Story分割優先順位、In One Line
  =中心1文+補足2文)を、`PROTOTYPE`から`DECIDED`へ正式に昇格した
- **状態**: `DECIDED`
- **採用理由**: ER-003-A2-AUDIO-AB-01でA02の完成候補(A/B比較)をユーザーが
  試聴し、全体としてOKと判断。個別に検証してきた言語・構造方針が音声
  完成候補として統合的に成立することを確認できた
- **比較した選択肢**: 個別reportに仕様を分散させたまま運用を続ける vs
  CURRENT_SPECへ正式反映し一次参照先を一本化する
- **却下理由(分散運用継続)**: 過去に決定事項がhandoffや個別reportへ
  埋もれ、Project Managementの機能不全を招いた教訓があるため
- **根拠レポート**: [ER-003-A2-SPEC-FREEZE-01_REPORT.md](ER-003-A2-SPEC-FREEZE-01_REPORT.md)
- **影響するCURRENT_SPEC項目**: CEFR(A2/B1/B2比較)、CEFR-A2 構造・音声仕様

## ER-003-A2-SPEC-FREEZE-01: A2英語ナレーション速度を約135 WPM目安として採用

- **日付**: 2026-08-12
- **内容**: A2の英語ニュースナレーション(Full Story/Points/In One Line)
  の速度目安として約135 WPMを採用する。hard constraintではなく目安とし、
  自然なprosodyを優先する。B1/B2は現行速度を維持し、新たなWPM targetは
  設けない
- **状態**: `DECIDED`(目安として)
- **採用理由**: ER-003-A2-AUDIO-AB-01でA02の速度A版(指定なし、平均約
  155 WPM)/B版(約135 WPM目安)を生成しユーザーが試聴、B版を採用可と判断
- **比較した選択肢**: 速度指定なし(A版) vs 約135 WPM目安(B版)。倍率
  固定案(現行速度の0.9倍)も検討したが、B1自体のWPMが記事により139〜143と
  幅があるため倍率ではなく絶対値の目安として採用
- **却下理由(倍率固定・0.9x)**: 記事構成差の影響を受けやすく、絶対値
  target(約135)の方が運用しやすいと判断
- **根拠レポート**: [ER-003-A2-AUDIO-AB-01_REPORT.md](ER-003-A2-AUDIO-AB-01_REPORT.md)
- **commit**: `e0e9a8d`
- **影響するCURRENT_SPEC項目**: CEFR-A2 構造・音声仕様 > A2英語ナレーション速度、B1/B2音声速度

## Cross-level: Preview原則をA2/B1/B2共通仕様として採用

- **日付**: 2026-08-12(原則試作はER-003-CROSSLEVEL-AUDIO-01、2026-08-09)
- **内容**: Previewはニュース全体のテーマ・問題意識・聞く価値・問いを
  示すことに限定し、後続本文の具体的な答え・詳細な数字・重要な転換点や
  結論を先出ししない、という原則をA2固有ではなくA2/B1/B2共通仕様として
  正式採用する
- **状態**: `DECIDED`
- **採用理由**: A01/A02/ADD03の3記事でこの原則に沿ってPreviewを再設計し、
  Comment1/2との情報重複解消を確認。ユーザーがA/B比較・3記事分の試聴を
  経て方向性を承認
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-01_REPORT.md](ER-003-CROSSLEVEL-AUDIO-01_REPORT.md)、[ER-003-CROSSLEVEL-AUDIO-02_REPORT.md](ER-003-CROSSLEVEL-AUDIO-02_REPORT.md)
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Preview原則
- **注意**: 既存B1/B2完成音声のPreviewは今回遡って差し替えない。今後の新規生成時から適用する

## Cross-level: Key Phrase発音品質の3条件をA2/B1/B2共通仕様として採用

- **日付**: 2026-08-12
- **内容**: Key Phraseの発音品質を(1) Meaning/contextual prosody、
  (2) Phoneme integrity(語末音素保持)、(3) Phrase grouping(単語ごとに
  分断しない)の3条件を同時に満たすものと定義し、A2/B1/B2共通の品質原則
  として採用する。個別単語への場当たり的パッチではなく、この共通原則で
  生成する
- **状態**: `DECIDED`
- **採用理由**: "Come on"/"Go ahead"/"Brent crude oil"で3条件を同時に
  満たす統合instructionを試作し、A02のKey Phrase 5件(personalized feedは
  既承認版を維持)へ適用。ユーザーがA/B完成候補内で試聴し承認
- **比較した選択肢**: 語末音素対策(segmental accuracy)のみを品質基準と
  する現状維持 vs 意味prosody・phrase一体感を含めた3条件へ拡張
- **却下理由(現状維持)**: 語末音素が正しくても、意味に合わない
  イントネーション(例: "Go ahead"が許可の意味に聞こえる)は別の問題として
  残ることが判明したため
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-04_REPORT.md](ER-003-CROSSLEVEL-AUDIO-04_REPORT.md)、[ER-003-A2-AUDIO-AB-01_REPORT.md](ER-003-A2-AUDIO-AB-01_REPORT.md)
- **commit**: `c061ae9`, `e0e9a8d`
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Key Phrase発音品質(3条件)

## Cross-level: 英語見出しは見出しテキストを実際にTTS inputへ含める方式を採用

- **日付**: 2026-08-12
- **内容**: Point One/Point Two/In One Line等の英語見出しは、見出し
  文字列そのものをTTS inputへ渡して発話させる。見出しテキストを含めず
  instructionだけで「見出しを言うように」指示する方式は使用しない
- **状態**: `DECIDED`
- **採用理由**: ADD03のIn One Lineで、見出しテキストを本文に含めずに
  生成した結果、モデルが指示に反応して見出しを不安定に(日本語風に
  聞こえる形で)発話する事象が発生。見出しテキストを実際に含める方式
  (Point One/Twoで既に問題が起きていなかった方式と同一)へ統一したところ、
  3回中3回で安定した正しい発話を確認
- **比較した選択肢**: 見出しを発話しないよう指示で抑制する(誤った初期
  対応、ER-003-CROSSLEVEL-AUDIO-03で一度採用したが後に訂正) vs 見出し
  テキストを実際に含める(最終採用)
- **却下理由(発話抑制)**: In One Lineは本来読み上げるべき見出しであり、
  「発話させない」ことは要件に反する誤った対応だった
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-04_REPORT.md](ER-003-CROSSLEVEL-AUDIO-04_REPORT.md)
- **影響するCURRENT_SPEC項目**: CEFR-A2構造・音声仕様 > In One Line見出しのTTS、Cross-level仕様 > 英語見出しのTTS方式

## Cross-level: Pause値(0.7秒/0.8秒)をA2/B1/B2共通仕様として採用

- **日付**: 2026-08-12
- **内容**: 「ポイント解説」→Preview間を0.7秒、Point One→Point Two間を
  0.8秒、In One Line→Outro間を0.8秒とする。A2 Comment前後の1.0秒(英→日)・
  0.8秒(日→英)は無変更で維持する
- **状態**: `DECIDED`
- **採用理由**: A02のA/B完成候補でユーザーが試聴し承認
- **根拠レポート**: [ER-003-A2-AUDIO-AB-01_REPORT.md](ER-003-A2-AUDIO-AB-01_REPORT.md)
- **commit**: `e0e9a8d`
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > ポーズ各項目
- **注意**: 現状は記事ごとの組立スクリプトへ個別にハードコードされており、共通定数への一元化はまだ行っていない([OPEN_ITEMS.md](OPEN_ITEMS.md)参照)

## Cross-level: Outro音量の心理音響ベース減衰方針を採用

- **日付**: 2026-08-12
- **内容**: Outro音量を、単純な振幅比の変更ではなく心理音響上の知覚音量
  ベースの計算(10dBの変化で知覚音量が倍/半分になるという経験則)で
  段階的に減衰する方針を、A2/B1/B2共通のmix ruleとして採用する
- **状態**: `DECIDED`(方針として)
- **採用理由**: A02のA/B完成候補でユーザーが試聴し承認
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-01_REPORT.md](ER-003-CROSSLEVEL-AUDIO-01_REPORT.md)〜[04](ER-003-CROSSLEVEL-AUDIO-04_REPORT.md)、[ER-003-A2-AUDIO-AB-01_REPORT.md](ER-003-A2-AUDIO-AB-01_REPORT.md)
- **commit**: `e0e9a8d`
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Outro音量
- **注意**: 既存B1/B2完成音声のOutroは今回遡って差し替えない

## A01 script修正: "The referee then added more time." → "The game went into added time."

- **日付**: 2026-08-12
- **内容**: A01のFull Story Part2にある"The referee then added more
  time."を、サッカー放送で標準的に使われる用語"added time"を用いた
  "The game went into added time."へ修正する
- **状態**: `DECIDED`(方針確定。完成音声への反映は次回A01 assemble時)
- **採用理由**: "added more time"は理解可能だが放送英語としてやや
  一般的すぎる。代替候補"extra time"はサッカーでは「延長戦」という
  別概念を指すため不採用、"added time"はロスタイムを指す正確な標準
  用語のため採用
- **比較した選択肢**: 現状維持 / "The referee added extra time." / "The game went into added time."
- **却下理由("extra time")**: 意味が変わってしまうリスク(延長戦との混同)
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-03_REPORT.md](ER-003-CROSSLEVEL-AUDIO-03_REPORT.md) 9節
- **影響するCURRENT_SPEC項目**: (個別記事の本文修正、CURRENT_SPEC仕様そのものへの影響なし)

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[CURRENT_SPEC.md](CURRENT_SPEC.md)、
[HISTORY_INDEX.md](HISTORY_INDEX.md)、[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)
