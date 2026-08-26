# DECISION_LOG — 確定した意思決定の索引

**管理ID: ER-PM-001**
**最終更新: 2026-08-24(ER-007-SPOKEN-EVIDENCE-DENSITY-AB-01 Part B)**

**区分について(2026-08-17追記)**: 以下のDecisionは「サービス・生成仕様」
(番組の聞こえ方・記事の作られ方そのものに関わるもの)と「Implementation
Hardening」(実装の堅牢化。サービス仕様は変えず、コードの安全性・
再発防止のみを目的とするもの)を区別して記載する。各エントリの見出しに
区分を明記する。

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
- **状態**: `DECIDED / APPLIED`(2026-08-12、ER-003-A2-SCRIPT-FINAL-01で
  最終台本へ反映済み。音声への反映は次回A01 assemble時)
- **採用理由**: "added more time"は理解可能だが放送英語としてやや
  一般的すぎる。代替候補"extra time"はサッカーでは「延長戦」という
  別概念を指すため不採用、"added time"はロスタイムを指す正確な標準
  用語のため採用
- **比較した選択肢**: 現状維持 / "The referee added extra time." / "The game went into added time."
- **却下理由("extra time")**: 意味が変わってしまうリスク(延長戦との混同)
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-03_REPORT.md](ER-003-CROSSLEVEL-AUDIO-03_REPORT.md) 9節、[ER-003-A2-SCRIPT-FINAL-01_REPORT.md](ER-003-A2-SCRIPT-FINAL-01_REPORT.md)
- **影響するCURRENT_SPEC項目**: (個別記事の本文修正、CURRENT_SPEC仕様そのものへの影響なし)

## A01 script修正: "Rogers sent the ball across the front of goal." → "Rogers crossed the ball into the box."

- **日付**: 2026-08-12
- **内容**: A01のFull Story Part1にある直訳的で不自然な表現を、実際の
  サッカー実況で標準的に使われる"cross the ball into the box"を用いた
  表現へ修正する
- **状態**: `DECIDED / APPLIED`(2026-08-12、ER-003-A2-SCRIPT-FINAL-01で
  最終台本へ反映済み。音声への反映は次回A01 assemble時)
- **採用理由**: 事実関係(誰が・どこへ・どうボールを送ったか)は変えず、
  放送英語として自然な言い回しへ改善。A2文長制約(18語以下)にも適合
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-03_REPORT.md](ER-003-CROSSLEVEL-AUDIO-03_REPORT.md) 11節、[ER-003-A2-SCRIPT-FINAL-01_REPORT.md](ER-003-A2-SCRIPT-FINAL-01_REPORT.md)
- **影響するCURRENT_SPEC項目**: (個別記事の本文修正、CURRENT_SPEC仕様そのものへの影響なし)

## A01 script修正: "Messi sent the ball across goal from the right." → "Messi crossed the ball from the right."

- **日付**: 2026-08-12
- **内容**: 上記と同種の不自然な表現を、同じく"cross"を用いた自然な
  表現へ修正する
- **状態**: `DECIDED / APPLIED`(2026-08-12、ER-003-A2-SCRIPT-FINAL-01で
  最終台本へ反映済み。音声への反映は次回A01 assemble時)
- **採用理由**: 上記と同様。"from the right"というPoint Oneでの記述
  ("He helped Lautaro with a good ball from the right.")との整合性も
  維持される
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-03_REPORT.md](ER-003-CROSSLEVEL-AUDIO-03_REPORT.md) 11節、[ER-003-A2-SCRIPT-FINAL-01_REPORT.md](ER-003-A2-SCRIPT-FINAL-01_REPORT.md)
- **影響するCURRENT_SPEC項目**: (個別記事の本文修正、CURRENT_SPEC仕様そのものへの影響なし)

## A02 script修正: "apps under the plan would not open at first" → "apps under the plan would be switched off by default"

- **日付**: 2026-08-12
- **内容**: A02のFull Story Part1にある、誤読リスク(「起動できない」と
  誤解される恐れ)のある表現を、"switched off by default"(初期設定で
  オフになっている)へ修正する
- **状態**: `DECIDED / APPLIED`(2026-08-12、ER-003-A2-SCRIPT-FINAL-01で
  最終台本へ反映済み。音声への反映は次回A02 assemble時)
- **採用理由**: 意味誤読リスクの解消。Natural English Source
  (`er003_output/a2_p1_r3/A02/master_en_natural_source_approved.md`)
  の該当箇所"covered apps would be unavailable by default"と照合し、
  「対象アプリはdefaultで利用不可(オフ)になる」という原意と一致する
  ことを確認した上で採用(意味を変更する修正ではなく、原意を正確に
  反映する修正と判定)
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-03_REPORT.md](ER-003-CROSSLEVEL-AUDIO-03_REPORT.md) 11節、[ER-003-A2-SCRIPT-FINAL-01_REPORT.md](ER-003-A2-SCRIPT-FINAL-01_REPORT.md)
- **影響するCURRENT_SPEC項目**: (個別記事の本文修正、CURRENT_SPEC仕様そのものへの影響なし)

## ADD03 script修正: Brent原油価格段落の時系列flashback構造を解消

- **日付**: 2026-08-12
- **内容**: ADD03のFull Story Part2にある、7/14の出来事→7/13への回想→
  7/14の出来事、という時系列が前後する構成を、7/13→7/14の実時系列順
  へ並べ替える。あわせて重複していた「価格が下落した」旨の記述
  (旧文中2箇所)を1箇所へ統合し、"on July 13"/"July 14"という明示的な
  日付参照を追加した
- **状態**: `DECIDED / APPLIED`(2026-08-12、ER-003-A2-SCRIPT-FINAL-01で
  最終台本へ反映済み。音声への反映は次回ADD03 assemble時)
- **採用理由**: A2レベルの聞き手にとって時系列の前後が理解負荷になる
  ため。新しい事実は追加していない(既存文の並べ替え・日付明示・
  重複表現の統合のみ)。Natural English Source
  (`er003_output/a2_p1_r3/ADD03/master_en_natural_source_approved.md`)
  との整合を確認済み(「7/13に急騰・$87超のintraday高値」「fee撤回後に
  高値から反落」「7/14終値$84.73・前日比+2%・月間最高値」という
  事実関係は維持)
- **根拠レポート**: [ER-003-CROSSLEVEL-AUDIO-03_REPORT.md](ER-003-CROSSLEVEL-AUDIO-03_REPORT.md) 11節、[ER-003-A2-SCRIPT-FINAL-01_REPORT.md](ER-003-A2-SCRIPT-FINAL-01_REPORT.md)
- **影響するCURRENT_SPEC項目**: (個別記事の本文修正、CURRENT_SPEC仕様そのものへの影響なし)

## ER-003-SPOKEN-FIRST-03: Point Balance(Point One/TwoはA02で40〜50語が機能。全ジャンル一律ルール化はしない)

- **日付**: 2026-08-13
- **内容**: SPOKEN-FIRST-02のA02で、Point One(144語)が本編
  (166語)とほぼ同等の長さになり、「本文とは別の切り口を短く示す」
  というPointの役割から外れ、実質的に"第二の本編"になっていた問題を
  是正する設計判断を検証・確定する。判断の核心は「PointがK-1-1/K-1-2
  の役割(本編と同程度の情報量を持たせない、本編の再説明ではなく
  別の切り口・示唆を短く示す)を果たしているか」という**役割・比重
  基準**であり、固定語数ルールではない
- **状態**: `VALIDATED(A02単独検証) / NOT_YET_GENERALIZED`
  (ユーザー・レビュー承認済み。A01・ADD03等への横展開、Production
  仕様(CURRENT_SPEC.md)への組み込みはまだ行っていない)
- **採用理由**: A02のPoint One/Twoを、目標30〜60語(許容25〜70語)の
  範囲でVerified Fact Ledgerの範囲内のみを使い圧縮した結果、
  Point One=47語・Point Two=44語に自然収束し、核心メッセージを
  保持したまま本編とのバランスが改善した(Fact Checker `PASS`、
  Ledger Deviation `LEDGER_COMPLIANT`、技術的再試行0回)。本編
  (166語)・In One Line(28語)は完全無変更で、Point削減の埋め合わせ
  としての本編延長も発生しなかった
- **比較した選択肢**: (該当なし。単一のPoint圧縮方式のみ試行し
  best-of選択は行っていない)
- **却下理由**: (該当なし)
- **今回確定していない事項(誤読防止のため明記)**:
  「各Pointを必ず40〜50語にする」という固定ルールにはしない。
  40〜50語という実測値はA02(1記事1ジャンル)での目標範囲内収束
  結果にすぎず、他ジャンルへ機械的に適用してよいという意味ではない。
  A01のように元々Point One=37語・Point Two=60語で「第二の本編」化
  が起きていない記事まで機械的に圧縮する対象ではない
- **根拠レポート**: [ER-003-SPOKEN-FIRST-03_REPORT.md](ER-003-SPOKEN-FIRST-03_REPORT.md)(特にK節「検証済みの設計判断」)、[ER-003-SPOKEN-FIRST-02_REPORT.md](ER-003-SPOKEN-FIRST-02_REPORT.md)(問題発見の経緯)
- **commit**: `a1fcc2c`(生成・報告)、(本記録commitは送付メッセージ参照)
- **影響するCURRENT_SPEC項目**: (個別記事A02の実験的圧縮版のみ。
  CURRENT_SPEC.mdへの反映は未実施。次回横展開検証(A01・ADD03)の
  結果を踏まえて判断する→[OPEN_ITEMS.md](OPEN_ITEMS.md)へ追加要否は
  次段階で検討)

## [サービス・生成仕様] ER-003-B1-NOVEL-AUDIO-01系: B1をSupport-based Natural Englishへ再設計

- **日付**: 2026-08-14頃(複数タスクにまたがる、ER-003-B1-A2-SPEC-FREEZE-01で正式反映)
- **内容**: B1のNews本文(Full Story/Point One/Two/In One Line)専用の簡略化rewriteを行う旧来の設計をやめ、B2相当のNatural English本文を共通で使い、B1固有の体験はSupport(Preview/Comment1-4を平易な英語で提供)と役割設計だけで作る方式へ移行した。あわせてVoice role(Charon=Navigator/Support、Aoede=News Content)を再配置し、A2由来の日本語spoken text(Title/Preview/Comment等)をB1から除去し英語化した
- **状態**: `SUPERSEDED`(2026-08-17、`ER-003-B1-B2-SCOPE-FIX-01` Decision Aにより後継。B1のNews本文はB2と共通化せず、Verified Fact LedgerからB1専用Writerで独立生成する方式へ移行済み。本Decisionは当時の設計判断の記録として保持)
- **採用理由**: B1専用の簡略化英文を別途生成すると、A2との差別化が「難易度の異なる2つのNews本文」という設計になり、Ledgerに忠実な単一のNatural English本文という一貫性が失われる。Support(言語・役割)だけで難易度体験を作る方が、記事本文の事実表現を1つに保ちやすい
- **比較した選択肢**: B1専用の簡略化本文を維持する vs News本文をB2と共通化しSupportだけで差別化する
- **却下理由(B1専用簡略化本文の維持)**: 本文を2種類(A2向け簡略・B1向け簡略)+Support言語という組み合わせが増え、Fact Ledgerとの整合確認箇所が増える。ユーザー判断によりSupport-based設計を採用
- **根拠レポート**: ER-003-B1-NOVEL-AUDIO-01系タスク一式(Support English化・Voice role再配置・日本語残存要素の英語化)
- **影響するCURRENT_SPEC項目**: B1(Support-based Natural English)節一式

## [サービス・生成仕様] ER-003-A2-B1-N3-01: B1-B Direct Generationを採用し、B2の別段階生成を廃止

- **日付**: 2026-08-16
- **内容**: B1-A(B2から派生させる方式)とB1-B(Verified Fact Ledgerから1回のWriter呼び出しで直接Natural English本文を生成する方式)を4版比較した上で、B1-B Direct Generationを採用した。以後、B1/A2とも同一のVerified Fact Ledgerから、それぞれ独立したWriter呼び出しで生成し、B2を別段階として生成するステップはN3以降の新規記事では行わない
- **状態**: `DECIDED`
- **採用理由**: B1-B Direct Generationは、B2を経由する方式より生成段階が少なく、Fact Ledgerとの整合確認箇所も1本化できる。4版diagnostic比較でB1-Bが採用可能な品質と判定された
- **比較した選択肢**: B1-A(B2派生) vs B1-B(Ledgerから直接生成)
- **却下理由(B1-A)**: B2という中間生成物を介するぶん、生成・QA工程が増える
- **根拠レポート**: B1-A/B1-B新規生成・4版diagnostic metrics測定・4版比較Artifact作成の各タスク完了報告
- **影響するCURRENT_SPEC項目**: B1(Support-based Natural English) > News本文の生成方式

## [サービス・生成仕様] B1 Key Phraseの提示順序をEnglish→Japanese→Englishに確定(英英説明は不採用)

- **日付**: 2026-08-14頃
- **内容**: B1のKey Phraseも、A2と同じEnglish→Japanese→English(反復)の提示順序を正式仕様とする。英英説明(English-only definition)方式は採用しない
- **状態**: `DECIDED`
- **採用理由**: 難語の英英説明はそれ自体が新しい理解負荷になり、Support-based B1の「本文理解のためのListening Navigation」という目的に反する。section長文化も避けられる
- **比較した選択肢**: English→Japanese→English(反復) vs English-onlyの説明的Key Phrase提示
- **却下理由(English-only説明)**: 意味理解の確実性より難語説明の負荷が優先されてしまう
- **根拠レポート**: ER-003-B1-NOVEL-AUDIO-01系
- **影響するCURRENT_SPEC項目**: B1 Key Phrase節

## [サービス・生成仕様] ER-003-POINT-NOTIFICATION-01: Point One/Two専用Notificationと無言のPoint番号ラベル

- **日付**: 2026-08-14頃
- **内容**: Point One/Twoの直前に専用のNotification音(既存のKey Phrase/Full Story Notificationとは別音源)を挿入し、Point番号("Point One."等)は音声で明言しない設計を採用。あわせてNotification直後に追加の余白を入れない(音源自体の余韻をそのまま使う)方式へ修正した
- **状態**: `DECIDED`
- **採用理由**: 構造(Notification)と意味(semantic heading)を分離することで、機械的な番号読み上げより自然な聞こえ方になる
- **根拠レポート**: ER-003-POINT-NOTIFICATION-01完了報告、追加調整(Point Notification直後のpause除去)
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Point Notification、Point semantic heading

## [サービス・生成仕様] Point semantic headingは記事生成プロンプトの`###`見出しをそのまま使う

- **日付**: 2026-08-14頃(A2)、B1はVoice再配置と同時期
- **内容**: Point One/Twoの本文直前に置くsemantic headingは、追加のLLM呼び出しで別途生成せず、記事生成プロンプトが既に返している`###`見出し(装飾記号のみ`clean_heading()`で除去)をそのまま使う
- **状態**: `DECIDED`
- **採用理由**: 記事生成の時点で既に2つの`###`見出しを要求しているため、これがそのままsemantic headingとして使える。追加呼び出し・追加コストが不要
- **根拠レポート**: ER-003-A2-POINT-HEADING-AUDIO-01完了報告(発見の経緯)
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Point semantic heading

## [サービス・生成仕様] ER-003-A2-B1-N3-01: Point Balanceの目標範囲(30-60語/許容25-70語)を3ジャンルで検証、hard capへは昇格させない

- **日付**: 2026-08-17
- **内容**: ER-003-SPOKEN-FIRST-03でA02単独検証にとどまっていたPoint Balanceの目標範囲(目標30〜60語、許容25〜70語)を、Sports(Hanshin)・Health・Household の3ジャンルへ横展開した。3ジャンルとも、Fact Ledgerの範囲内でPointを圧縮した結果、目標範囲内に自然収束することを確認した
- **状態**: `VALIDATED across Sports/Health/Household`(hard capへの変更はしない)
- **採用理由**: 3ジャンルでの再現性が確認できたことで、単一記事の偶然の結果ではないという確信度が上がった。ただし、目標範囲を機械的なhard capにすると、記事によって自然に収まる長さが異なる可能性を無視することになるため、診断的な目安の位置づけを維持する
- **比較した選択肢**: 診断的目安のまま維持する vs 機械的なhard capへ格上げする
- **却下理由(hard cap化)**: 3ジャンルでの成功は「範囲内に収まりやすい」ことを示すが、「収まらなければならない」ことまでは示さない。ユーザー指示により、勝手にhard ruleへ変更しないことを明示的に維持
- **根拠レポート**: ER-003-A2-B1-N3-01完了報告(cross-level分析節)
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Point Balance(長さの扱い)

## [サービス・生成仕様] ER-003-A2-B1-N3-01: Spoken-first Number TreatmentをA2/B1共通仕様として正式化

- **日付**: 2026-08-17
- **内容**: Fact Ledgerはexact factを保持しつつ、spoken narrative側では精度自体に意味のない数字を丸め・概数化・方向化してよいという方針を、Importance(ANCHOR/SUPPORTING/DISPENSABLE)・Exactness(EXACT_REQUIRED/APPROXIMATE_OK/DIRECTION_ONLY)という2軸の分類として明文化し、A2/B1共通仕様として採用した
- **状態**: `DECIDED`
- **採用理由**: 過度な小数精度の読み上げはListening easeを損なう。一方でスコア・日付・研究結果等、精度自体が意味を持つ数字までは丸めない、という線引きを明示する必要があった
- **根拠レポート**: ER-003-A2-B1-N3-01完了報告 §14
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Spoken-first Number Treatment

## [サービス・生成仕様] ER-003-A2-B1-N3-01: Fact Safety(Verified Fact Ledger→Fact Checker→Ledger Deviation Check)をA2/B1共通標準として正式化

- **日付**: 2026-08-17
- **内容**: 記事ごとに1つのVerified Fact Ledgerを作成し、A2/B1双方がそこから生成される。生成後は独立Fact Checker(web検索付き)とLedger Deviation Checkの2段QAを標準として実施する
- **状態**: `DECIDED`
- **採用理由**: A2/B1で個別に取材・Ledger作成すると、同じ記事の中でA2とB1が異なる事実関係を語るリスクが生じる。単一Ledger共有によりこれを防ぐ
- **根拠レポート**: ER-003-A2-B1-N3-01完了報告
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Fact Safety(共通)

## [サービス・生成仕様] ER-003-A2-B1-N3-01: 3ジャンル(Sports/Health/Household)横展開によるジャンル再現性の確認

- **日付**: 2026-08-17
- **内容**: 仮Fixしていた A2/B1 の一連の仕様(B1-B Direct Generation、Support scaffold、Point Notification、semantic heading、Voice分離、difficulty差)が、スポーツ(阪神-広島戦)・健康(観察研究記事)・生活実用(冷蔵庫のクリスパードロワー)という3つの異なるジャンルで、追加の構造変更なしに機能することを確認した
- **状態**: `DECIDED`(validation evidenceとして記録)
- **採用理由**: 単一ジャンル(SNS規制記事等)での検証だけでは、他ジャンルへの一般化可能性が担保されない。3ジャンル展開により、構造面の再現性を実証した
- **根拠レポート**: ER-003-A2-B1-N3-01完了報告
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > ジャンル再現性

## [サービス・生成仕様] ER-003-N3-ROOT-FIX-01 / VERIFY-01: A2 Core Explanatory Logic Preservationを正式仕様へ採用

- **日付**: 2026-08-17
- **内容**: A2生成指示(`A2_KAI1_INSTRUCTION`)へ、「Verified Fact Ledgerが規定する中心的な説明ロジック・判断ルールを保持すること。語彙・文構造・具体例・提示順序は簡略化してよいが、Ledgerの仕組み・判断ルールを、Ledgerが支持しない/明示的に否定するショートカット・分類・因果関係・経験則へ置き換えないこと」という原則を追加した。ジャンル固有の具体例(Household記事のfruit/vegetable等)はこの一般原則のprompt本文へhard-codeしない
- **状態**: `DECIDED`
- **採用理由**: ER-003-N3-RCA-01のRoot Cause Analysisで、Household A2記事が「果物は低湿度、野菜は高湿度」という、Ledgerが明示的に否定するfruit/vegetable二分法を"基本ルール"として提示してしまっていたことが判明した。原因は、A2のCognitive Load Reductionが「正しいが複雑な判断軸」を「簡単だが別物の近似ルール」へ置換してしまうリスクであり、既存のFact Checkerは文単位の正確性は見ていても記事全体の判断軸までは見ていなかった(旧Household A2は実際にFact Checker PASSしていた)。この原因に対する発生源側の対策として、A2生成指示自体へ軸維持の原則を追加した
- **比較した選択肢**: (a) A2生成指示への原則追加(発生源対策)、(b) A2/B1間のクロスレベル一貫性チェックを新設(検出強化、追加LLM呼び出しが発生)、(c) 人間レビューゲートの追加(検出強化、量産と相性が悪い)
- **却下理由(b・c)**: 今回は「工程を重くせず発生源で再発率を下げる」ことを優先し、新しいLLM監査工程・人手工程は追加しないという方針のもとで、最小コストの(a)を採用した。(b)(c)は将来的な再発時の追加検討候補として保持する
- **検証根拠(ER-003-N3-ROOT-FIX-VERIFY-01)**: 既存Ledger・既存B1-Bを固定し、新しいA2_KAI1_INSTRUCTIONで3ジャンルを各1回だけ単発生成(best-of禁止)した結果:
  - Household: Core logic = **BETTER_PRESERVED**(旧版の"Fruit usually goes in low humidity..."という二分法を1回目の生成で回避し、ethylene放出/水分保持という仕組みを基本ルールとして提示。A2 ease・adult toneに副作用なし)
  - Health: Core logic = **SAME**(lifespan/healthspanの区別、observational study/非causationの説明を維持。副作用なし)
  - Hanshin: Core logic = **SAME**(元々シンプルなジャンルで、新しい段落による過剰な分析トーン化は見られず)
  - 3記事とも Fact Checker `PASS`、Ledger Deviation Check `LEDGER_COMPLIANT`(0件)。Writer/Fact Checker/Ledger Deviation Checkの呼び出し回数は変更前と同一(新しいLLM監査工程を追加していない)。**この`PASS`は、本Decisionの検証用にVerify-01で単発生成した`root_fix_01_regression/`配下のregressionテキストに対する結果である。本番article.md(特にHousehold A2)には未反映であり、本番article.mdのFact QA状態はこの`PASS`と同一ではない**(→[ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md)、2026-08-17 SoT Consistency Cleanupで区別を明記)
- **根拠レポート**: ER-003-N3-RCA-01完了報告、ER-003-N3-ROOT-FIX-01完了報告、ER-003-N3-ROOT-FIX-VERIFY-01完了報告
- **影響するCURRENT_SPEC項目**: CEFR-A2 構造・音声仕様 > Core Explanatory Logic Preservation
- **未実施事項(誤読防止のため明記)**: 今回のFreezeは仕様・prompt原則の正式反映のみ。既存記事(Hanshin/Health/Householdの本番article.md・音声)への遡及適用・再生成は行っていない。Household A2の本番article.mdは、ER-003-A2-B1-N3-01-FIX-01時点の手動編集版のままであり、今回正式採用したA2_KAI1_INSTRUCTIONで再生成したものではない(→[OPEN_ITEMS.md](OPEN_ITEMS.md))

## [Implementation Hardening] ER-003-N3-ROOT-FIX-01: English Key Phrase trim safety marginを0.20秒へ拡大(Key Phrase専用)

- **日付**: 2026-08-17
- **内容**: 英語Key Phrase音声生成のhead safety marginを0.08秒から0.20秒へ拡大した。共有関数のデフォルト値は変更せず、Key Phrase生成関数(`repro01.generate_key_phrase_component_verified`)だけが新しいmargin値を明示的に指定する設計とし、他segment(Preview/Comment/Title等)には一切波及しない
- **状態**: `DECIDED`(Audio実装詳細、サービス仕様の変更ではない)
- **採用理由**: "follow-up time"のようなKey Phraseで、無声摩擦音(/f/等)の語頭が無音判定の閾値付近にあり、既定の0.08秒marginでは実際に語頭が一部trimされる実例を波形解析で確認した。0.08秒では不足する実例が確認された一方、全Key Phraseの間合いを必要以上に長くしないため、0.35秒ではなく0.20秒(約2.5倍)を採用した
- **比較した選択肢**: (a) 全Key Phrase一律で0.20秒、(b) 語頭が無声摩擦音の単語だけ拡大、(c) 無音判定アルゴリズム自体を二段階しきい値へ再設計
- **却下理由(b・c)**: (b)は判定ロジックの追加実装が必要で複雑化する。(c)は共有の無音判定関数(他の多数の音声生成でも使われている)の改修になり、影響確認の負荷が大きい。今回は開発コスト・既存資産への影響が最も小さい(a)を採用
- **根拠レポート**: ER-003-N3-ROOT-FIX-01完了報告(波形解析による検証含む)
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Audio Implementation Detail > English Key Phrase trim safety margin

## [Implementation Hardening] ER-003-N3-ROOT-FIX-01: TTS style instructionの責務分離+短いJapanese phraseへのminimal instruction fallback

- **日付**: 2026-08-17
- **内容**: 共通style instruction(`er002_common.py`の`POINT_LABEL_FIDELITY_RULE`)が、Point One/Point Two/In One Lineという構成ラベル文字列を無条件に読み上げさせる指示を含んでいた。これは番組全体を1回のTTS呼び出しで読む旧方式のために書かれたもので、現行のセグメント単位生成では不要かつ、モデルが指示文自体を読み上げてしまう(instruction leakage)原因になっていた。全参照箇所を監査した上で、共通instructionからこの指示を既定で除外し(opt-inパラメータ化)、必要な一括生成呼び出し元がもしあれば明示的に有効化できる設計へ変更した。あわせて、検証の結果この対策だけでは短い単独の日本語フレーズ(Key Phrase訳等)へのinstruction leakageが解消しないことが判明したため、英語Key Phraseに既存のminimal instruction fallbackと同じ考え方を日本語の短いフレーズにも拡張した
- **状態**: `DECIDED`(Audio実装詳細、サービス仕様の変更ではない)
- **採用理由**: 実測で、POINT_LABEL_FIDELITY_RULE除去後も、短い日本語フレーズ("モデルで推定した差")で5/5回leakageが再現した一方、同程度の長さの文(Household日本語タイトル)では0/5回だった。これにより、脆弱性は「短いフレーズに長いstyle instructionを渡すこと」自体にあると判明し、英語で既に実証済みのfallbackパターンを日本語へ拡張することが最小コストの対策と判断した
- **比較した選択肢**: (a) 共通instructionの責務分離のみ、(b) (a)+日本語minimal instruction fallback、(c) Cross-level consistency用の新規LLM監査工程
- **却下理由(a単独)**: 実測で不十分と判明したため、(b)まで実施した。(c)は新しい監査工程を追加しない方針のため見送り
- **根拠レポート**: ER-003-N3-ROOT-FIX-01完了報告(caller監査表・leakage regression実測ログ含む)
- **運用コストの実測**: 標準経路が既に成功しているケースには呼び出し増なし。標準経路が不合格を繰り返すケースでのみ、fallback分のTTS/ASR呼び出しが追加発生する(実測: 1トライアルあたり1〜5回)
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Audio Implementation Detail > TTS style instruction責務分離、短いJapanese phraseのminimal instruction fallback

## [サービス・生成仕様] ER-003-B1-B2-SCOPE-FIX-01 Decision A: B1はB2共通本文ではなく、LedgerからB1用英文を独立生成する

- **日付**: 2026-08-17
- **内容**: ER-003-B1-A2-SPEC-FREEZE-01-R1で`NEEDS_CONFIRMATION`としていたB1/B2関係を確定する。B1はB2と同一テキストを共有しない。B1は、Verified Fact LedgerからB1専用のWriterで独立して英文を生成する。目標は: natural spoken news English、adult tone、A2ほど強く簡略化しない、B2相当の難しい英文よりlisteningで追いやすい、Clause Density/Concept Density/Long-distance Dependency等を抑える、hardなCEFR語彙制限・文長制限は設けない。既存の`B1_B_DIRECT_INSTRUCTION`の思想をそのままB1本文の正式仕様とする。「B1 = B2本文 + Support」という理解は採用しない
- **状態**: `DECIDED`
- **採用理由**: (1) N3で実際に採用・検証した方式(B1-B Direct Generation)と一致する。(2) 実際に検証済みの`B1_B_DIRECT_INSTRUCTION`の文言("clearly easier to follow while listening than a B2 news story")と一致する。(3) B1として自然さを保ちつつListening Loadを下げられる。(4) B2という中間生成物が不要になり、生成・QA工程が1本化できる
- **比較した選択肢**: (a) B1=B2本文をそのまま流用+Supportで差別化(FREEZE-01時点の暫定記述)、(b) B1=Verified LedgerからB1専用Writerで独立生成(採用)
- **却下理由(a)**: 実際の検証・実装(`B1_B_DIRECT_INSTRUCTION`)と一致しない。N3パイプラインには比較対象となる独立したB2生成段階自体が存在せず、「B2と同一」を実際に検証する手段がない
- **根拠レポート**: ER-003-A2-B1-N3-01(`B1_B_DIRECT_INSTRUCTION`の実装・3ジャンル検証)、ER-003-B1-A2-SPEC-FREEZE-01-R1(NEEDS_CONFIRMATION提起)、ER-003-B1-B2-SCOPE-FIX-01(本Decisionでのユーザー確定)
- **影響するCURRENT_SPEC項目**: 「B1(独立生成Natural Spoken News English)」節一式(基本方針、A2との関係、News本文の生成方式)

## [サービス・Scope仕様] ER-003-B1-B2-SCOPE-FIX-01 Decision B: Initial Launch levelはA2/B1の2つとする

- **日付**: 2026-08-17
- **内容**: 初期Launchの対象レベルを**A2/B1の2レベル**に絞る。CEFR-B2は初期サービス中核から外し、`LAUNCH_SCOPE: OUT_OF_INITIAL_SCOPE`とする。これはB2の廃止を意味しない。B2は今後、future expansion candidate / internal comparison・reference / historical experiment・referenceという位置づけで保持する。B2は初期External Pilot対象外、初期Production article generation対象外、初期UI/level selection対象外、初期Cost Baselineの必須対象外とする
- **状態**: `DECIDED`
- **採用理由**: (1) A2/B1が現在最も検証が進んでいる(N3-01の3ジャンル横展開・ROOT-FIX-01/VERIFY-01等)。(2) B2を初期Launchに含めると、記事生成・音声・QA・UI・External Pilot・運用コストのすべてが増える。(3) 初期の価値検証(External Pilotでの体験成立確認)には2レベルで十分。(4) B2は将来、必要になった時点で拡張可能な設計になっている(同一Ledgerからの独立Writer生成という構造はA2/B1と共通のため、B2追加時も既存アーキテクチャを再利用できる)
- **比較した選択肢**: (a) A2/B1/B2の3レベルで初期Launch、(b) A2/B1の2レベルで初期Launch、B2は将来拡張候補として保持(採用)
- **却下理由(a)**: 3レベル同時Launchは記事生成・音声制作・QA・UI設計・External Pilot設計・運用コストのいずれも増加させ、初期の価値検証を遅らせる。B2は現時点でテキストのみ生成済みで音声化が一度も実施されていない([OPEN_ITEMS.md](OPEN_ITEMS.md)参照)ため、初期Launchに含めると新たな検証範囲が発生する
- **根拠レポート**: ER-003-B1-B2-SCOPE-FIX-01(ユーザーDecision)
- **影響するCURRENT_SPEC項目**: CEFR比較表・冒頭の`LAUNCH_SCOPE`注記、[PROJECT_INDEX.md](PROJECT_INDEX.md)のLaunch対象レベル、[ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md)のB2行への注記

## [Implementation Hardening] ER-005-AUDIO-INSTRUCTION-SEPARATION-01: TTS style instructionとspoken textのStructured Separationを正式採用

- **管理ID**: `ER-005-AUDIO-INSTRUCTION-SEPARATION-01`
- **日付**: 2026-08-21
- **状態**: `DECIDED` / `CURRENT_SPEC`(Audio実装詳細、サービス仕様の変更ではない)
- **内容**: Gemini TTSへ渡す入力(`er003_b1_p4c_audio.build_tts_prompt(text, style_prefix)`)で、style instruction(話し方の指示)とspoken text(実際に読み上げる本文)を、`=== STYLE INSTRUCTIONS (do not speak) ===`/`=== TEXT TO SPEAK ===`という明示的なdelimiterで区切る構造(Structured Separation)を、現行production TTS経路(B1/A2、英語/日本語、standard/fallback双方)の標準方式として採用した。既存のこの共有関数を経由しない直接文字列連結(`style_prefix + text`)が2箇所(`er003_b1_p9a_audio.generate_narration_snippet`の日本語分岐、`er003_v1_sing01_voice01_generate.generate_charon_japanese`の標準経路)で見つかり、あわせて`build_tts_prompt()`経由へ統一した
- **何を変えたか**: TTSへ渡す入力の「区切り方」のみ。共有関数`build_tts_prompt()`を1箇所変更することで、これを呼び出す全経路(B1: `voice01.generate_charon_english/generate_charon_japanese`、`news_tail_fix.generate_news_narration_wide_margin`、`point_headings.generate`。A2/共通: `p9a.generate_narration_snippet`経由の`repro01.generate_narration_snippet_verified_strict`、`repro01.generate_key_phrase_component_verified`、`repro01.generate_english_component_minimal_instruction`、A2日本語fallback)へ一括反映した
- **何を変えていないか**: style instruction本文(内容・語数・意味)、speaker指定、voice、tone、pacing要求、narration character、spoken text本文(内容・語数・意味)は一切変更していない。Gemini公式`system_instruction`フィールドへの置き換えは行っていない(次項参照)
- **検証根拠(ER-005-AUDIO-VALIDATION-ROBUSTNESS-02のControlled Test)**: 過去に問題が確認された5segment(A2 `topic_intro`/`point_one`/`full_story_part1`、B1 Key Phrase 5英語・日本語)を対象に、Current方式とStructured Separation方式を同一style instruction・同一spoken textで比較した(各方式合計18回)。Current正常生成4/18(22.2%)、Structured正常生成13/18(72.2%)。技術的失敗(`INVALID_ARGUMENT`・応答parts欠落・500 INTERNAL)は、Current 9/18(50%)からStructured 0/18(0%)へ改善。Structured側で成功した全13件は、ASR検証(EXACT_MATCH)・音声長のいずれも正常範囲内であることを確認した。ユーザー試聴Artifact([Instruction Separation A/B Test](https://claude.ai/code/artifact/24309532-42d8-46f1-9e43-4116afb4c311))でAudio Style(自然さ・落ち着き・ニュースらしさ・話者の印象・テンポ・聞きやすさ)を確認いただいた上で、本Decisionを確定した
- **留保(重要)**: 試行数は各条件2〜5回と小規模であり、この検証だけでGemini TTSのinstruction leakage問題の**確定的な誘発条件を特定した**とは記録しない。「現時点で最も安定したProduction Baselineとして採用」という位置づけであり、「完全解決」ではない。誘発条件そのものは未解明のまま[OPEN_ITEMS.md](OPEN_ITEMS.md)で監視を継続する
- **比較した選択肢**: (a) 現状維持(単純連結)、(b) Gemini公式`system_instruction`フィールドで分離、(c) 単一`contents`文字列内を明示的delimiterで区切るStructured Separation(採用)
- **却下理由(b)**: Google公式ドキュメント(ai.google.dev/gemini-api/docs/speech-generation)にTTSでの`system_instruction`対応記載がなく、実機テストでも同一リクエストから`system_instruction`だけを外すと成功するのに対し、指定すると2/2で`500 INTERNAL`エラーになることを確認した。技術的に不安定/非対応と判断し不採用とした。将来Google側の公式仕様が変更された場合は別タスクで再評価する。現在の実装を今回の判断だけでsystem_instruction方式へ勝手に置き換えないこと
- **根拠レポート**: ER-005-AUDIO-VALIDATION-ROBUSTNESS-02完了報告(Controlled Test実測データ)、ER-005-AUDIO-ROBUSTNESS-SPEC-FIX-01完了報告(Production適用範囲監査・regression test)
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Audio Implementation Detail > TTS Instruction/Spoken Text分離(Structured Separation)

## [Implementation Hardening] ER-005-JA-SHORT-ASR-PHONETIC-01: 短い日本語segmentの発音ベースASR Validationを正式採用

- **管理ID**: `ER-005-JA-SHORT-ASR-PHONETIC-01`
- **日付**: 2026-08-21
- **状態**: `DECIDED` / `CURRENT_SPEC`(Audio実装詳細、サービス仕様の変更ではない)
- **内容**: 短い日本語segment(Japanese Key Phrase・gloss/meaning等、30文字以下)のASR検証に、漢字表記の完全一致だけに依存しない発音(読み)ベースの判定を追加した。`er003_audio_tts_asr_safety.validate_japanese_short_segment_match()`が、EXACT_MATCH/NORMALIZED_MATCH/PHONETIC_MATCH/TRUE_CONTENT_MISMATCH/ASR_UNCERTAINの5分類を返す。PHONETIC_MATCH(pykakasiによる読み変換が完全一致)は採用しTTS retryしない。TRUE_CONTENT_MISMATCH(数字・否定語の不一致、または読みが大きく異なる)はTTS retry候補のまま。ASR_UNCERTAIN(読みが近いが完全一致ではない中間ケース)は、TTSが誤っていると断定せず既存audioを保持したまま既存fallback/reviewへ委ねる
- **何を変えたか**: `er003_v1_sing01_voice01_generate.generate_charon_japanese`(B1、standard/fallback双方)、`er003_v1_repro01_main_generate.generate_narration_snippet_verified_strict`(language="ja"の場合、A2共有)、`er003_v1_n3_01_tts_generate.generate_a2_japanese_with_fallback`(A2 fallback)の検証ロジックへ、既存の完全一致/部分一致チェックが不合格の場合の**追加の採用条件**として組み込んだ。既存の合格ケースを壊す変更ではない(既存チェックが通れば従来通り即採用)
- **何を変えていないか**: 数字の実質的な違い・否定の有無・主要語の欠落・明らかに異なる発音・無関係な発話・hallucinationはPHONETIC_MATCHで吸収しない(hard-fail条件として維持)。長文Narrationへの適用範囲拡大は行っていない(30文字以下のみ)。個別専門用語のwhitelist(1対1のハードコード)は主方式にしていない
- **検証根拠**: ER-005-AUDIO-WASTE-REDUCTION-01のfixture(内向化問題/内効果問題、外向化問題/外交化問題等、鏡像/京三・恭三、行動上の問題/公道上の問題)全件でPHONETIC_MATCHとして正しく採用されることを確認。数字違い・否定語違い・無関係内容・空ASR・長文への誤適用は全てFAILすることをunit testで確認(negative test)。加えて、ER-005-AUDIO-VALIDATION-ROBUSTNESS-02のControlled Testで得た、fixtureに含まれない未知のASR誤認識パターン(「関連・相関」に対する「関連創刊」「関連、創建」等10件)でも、8/10が正しくEXACT_MATCH/PHONETIC_MATCHと判定され、明らかに無関係な1件・曖昧な2件はそれぞれ正しくTRUE_CONTENT_MISMATCH/ASR_UNCERTAINに分類されることを確認した(fixture外データでの追加検証)
- **比較した選択肢**: (a) 現状維持(漢字表記完全一致のみ)、(b) 個別専門用語ごとのwhitelist(「内向化→内効果ならPASS」等の1対1登録)、(c) 発音(読み)ベースの一般的な検証ロジック(採用)
- **却下理由(b)**: 新しい専門用語が出るたびに個別登録が必要になり、量産(新テーマ・新記事)に向かない。一般的な読み・発音正規化で吸収できない特殊ケースだけを将来的な限定fallback候補として扱う方針とし、(b)を主方式にはしない
- **根拠レポート**: ER-005-AUDIO-WASTE-REDUCTION-01完了報告、ER-005-AUDIO-VALIDATION-ROBUSTNESS-02完了報告、ER-005-AUDIO-ROBUSTNESS-SPEC-FIX-01完了報告(Production適用範囲・regression test)
- **影響するCURRENT_SPEC項目**: Cross-level仕様 > Audio Implementation Detail > 短い日本語segmentのASR検証: 発音ベースPhonetic Validation

## [Implementation Hardening] ER-006-MODEL-ROUTING-CONTRACT-01: Production Model RoutingをLunaへ統一・Fail-Closed契約化

- **管理ID**: `ER-006-MODEL-ROUTING-CONTRACT-01`
- **日付**: 2026-08-22
- **状態**: `DECIDED` / `CURRENT_SPEC`(Model Routingの実装契約、B1/A2構造やSupport内容等のサービス仕様の変更ではない)
- **監査で判明した経緯**: B1/A2 Writer・Writer Fact Check・Deviation Check・B1/A2
  Support(Comment/Preview/Key Phrase選定・正規化)は、コード上は元々(ER-002/003時代
  から一貫して)`gpt-5.6-sol`を使う設計だった(`er002_ja_free_markdown_restore.
  WRITER_MODEL = "gpt-5.6-sol"`という単一のhardcoded literalへ、Writer/Support/Key
  Phrase Selector等の全チェーンが連鎖的に依存)。`gpt-5.6-luna`は元々Query
  Planning/Topic Selection(`gather_topic.py`のMODEL_SEARCH)専用として設計されており、
  Writer/Support系をLunaにするという明文化された決定は、`CURRENT_SPEC.md`・
  `DECISION_LOG.md`のどちらにも存在しなかった(ER-005-WRITER/SUPPORT-COST-QUALITY-01
  はLunaでの品質同等性を検証しない前提の未検証な試験提案だった)。ER-006-POOL-PILOT-
  COST-ROOTFIX-01でこれを「Sol混入」と呼んだのは不正確で、正しくは「Cost集計スクリプト
  がLuna単価を誤って適用していた」バグと、「Writer/Support系Model RoutingをLunaへ
  正式決定するかどうかがこれまで未決だった」という2つの別の問題だった
- **今回のユーザー決定**: Writer(B1/A2)・Writer Fact Check・Support(B1/A2、Key
  Phrase選定・正規化含む)・Support Fact Checkの4工程は、ER-005での方針に整合させる
  形で`gpt-5.6-luna`をApproved Modelとして正式に固定する。Solはこれら工程では使用禁止
  とし、Fail-Closed契約(規定外modelが渡された場合はAPI call前に例外を送出、model
  未指定もFAIL)を適用する。Research系(Evidence Pack/VFL/Verification)・Query
  Planning・Topic SelectionはLunaのまま変更なし
- **何を変えたか**: [er006_model_routing_contract_01.py](er006_model_routing_contract_01.py)
  にProcess別Approved Model/ProviderのSingle Source of Truthと`require_model()`/
  `require_provider()`(fail-closed validator)を新設。production到達可能な各呼び出し
  箇所([er003_v1_n3_01_articles_generate.py](er003_v1_n3_01_articles_generate.py)の
  Writer/Fact Check/Deviation Check、[er003_v1_n3_01_scaffold_generate.py]
  (er003_v1_n3_01_scaffold_generate.py)のB1/A2 Support・Key Phrase選定・正規化、
  [er006_pool_pilot_01_research.py](er006_pool_pilot_01_research.py)のEvidence
  Pack/VFL/Verification/Exception Search、[er006_pool_pilot_01_support.py]
  (er006_pool_pilot_01_support.py)のSupport Fact Check)へ、SSOT経由の明示的な
  `model=`指定を追加した
- **何を変えていないか**: 各leaf関数(`vfl01.run_writer_no_search`等)自体の既定値
  (`MODEL`、Sol系譜)はそのまま残し、`model`引数を追加しただけ(後方互換)。この
  既定値を使う他の呼び出し元(Translation pipeline・過去のCEFR/spoken-first等の実験
  タスク、30件以上)はSolのまま変更していない(今回のスコープ外。過度な大規模
  refactorを避けるため、共有root定数自体は変更せず、production到達可能な呼び出し
  箇所だけへ明示的にoverrideを注入する方式を採った)
- **品質検証状況(重要な留保)**: LunaがSolと同等の記事・Support品質を出せるかは、
  本タスクでは検証していない。次回以降のPool topic生成・既存テーマ(hanshin/health/
  household)再生成時の実際の出力で確認が必要
- **Cost影響**: 6episode(ER-006 Pool Pilot)のHistorical Actual Spend(実際に支払った
  金額、¥2,639.6)は書き換えない。Counterfactual(今回のApproved Routingだった場合の
  理論値)は¥883.8で、差額¥1,755.8がSol使用による超過コストだった
- **根拠レポート**: ER-006-MODEL-ROUTING-CONTRACT-01完了報告(Model監査・
  Fail-Closed契約実装・Regression/Static Audit test・Cost再計算)
- **影響するCURRENT_SPEC項目**: Model Routing Contract(新設セクション)

## [Implementation Hardening] ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01: Audio ValidationのProduction配線・ASR一致と発音品質の分離・Luna品質確認

- **管理ID**: `ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01`
- **日付**: 2026-08-22
- **状態**: `DECIDED` / `CURRENT_SPEC`(Audio実装詳細・Model Routing運用、B1/A2構造等の
  サービス仕様変更ではない)
- **内容1(Audio Validation配線)**: ER-006-POOL-PREPROD-HARDENING-01で実装済み
  だった、ASR比較の正規化+6分類(EXACT_MATCH/NORMALIZED_MATCH/HIGH_SIMILARITY_
  SAFE/ASR_VALIDATION_UNCERTAIN/TRUE_CONTENT_MISMATCH/TTS_FAILURE)+Protected
  Check+同一signature retry guardrailを、英語(language=="en")のProduction
  retry loopへ配線した(`er006_preprod_hardening_01_validation.evaluate_
  attempt()`が統一エントリポイント)。対象: `er003_v1_sing01_voice01_
  generate.py::generate_charon_english`、`er003_v1_sing01_news_tail_fix.py`、
  `er003_v1_sing01_point_headings_aoede.py`、`er003_v1_repro01_main_
  generate.py::generate_narration_snippet_verified_strict/generate_key_
  phrase_component_verified`、`er003_v1_crosslevel_audio_02_common.py::
  generate_english_segment_with_fallback`。新status`ASR_VALIDATION_
  UNCERTAIN`を追加し、同一signatureが3回連続で改善しない場合はretryを
  打ち切り直前のaudioを保持する(STOPPEDとは区別、Human Review対象)。実際の
  Public Benches Luna版生成で、A2 point_twoがこの新statusで正しく打ち切られる
  ことを確認した。日本語(ja)経路は既存のphonetic_verdict方式のまま無変更
- **内容2(ASR一致と発音品質の原則)**: Key Phrase "hostile architecture"の
  ユーザーHuman Review報告(語頭/h/が/p/様に聞こえる)を、既存生成物の
  forensic調査(canonical text→TTS input→raw音声振幅エンベロープ→assembled
  音声との定量比較→ASR transcript)により調査した。ASRは全サンプルで正しく
  "Hostile architecture."と書き起こしていたが、raw音声の振幅エンベロープには
  母音遷移部で最大2.3〜4.7倍(20ms窓)という急峻な立ち上がりがあり、これは
  Assembly処理(resampling/gain)由来ではなくraw TTS生成時点で既に存在する
  ことをcross-correlationによる実測で確認した。別の/h/開始語でも同程度の
  急峻さを確認し、hostile固有ではなく短いKey Phrase発話の一般的なTTS特性で
  ある可能性が高いと判断(個別whitelist化はしていない)。この調査結果を
  踏まえ、「ASR transcript一致は発音品質PASSの証明ではない」という原則を
  [CURRENT_SPEC.md](CURRENT_SPEC.md)のQA/Human Review節へ正式に明文化した。
  振幅エンベロープの急峻さを検出する新しいAudio Validation(将来候補)は
  今回実装していない(詳細は[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-44、
  `UNDER_REVIEW`のまま)
- **内容3(Luna品質の実地確認)**: Public Benches(既存の確定済みEvidence
  Pack/VFL/Verification/Ledgerを再利用、Researchは再実行せず)のB1/A2を
  Model Routing Contract(全工程Luna、Sol call 0件を実測で確認)で新規生成し、
  旧Sol版と比較した。B1: Writer Fact Check PASS・Ledger完全準拠(Sol版は
  MINOR 1件)。A2: Fact Check REVIEW_REQUIRED(矛盾ではなく未確認の詳細3件)・
  Ledger MINOR 2件(Sol版は完全準拠)。総じて明確な品質劣化は確認されな
  かったが、A2でSol版よりわずかに逸脱が増えた点は留保として記録する。
  Audio面はSTOPPED/UNCERTAIN数がSol版(4件)よりLuna版(7件STOPPED+1件
  UNCERTAIN)で増えたが、個別調査の結果、原因はLuna特有の品質問題ではなく
  Azure ASRの表記揺れ(street→St.、three→3:00等)や既知のMalmö/Triangeln
  固有名詞音訳差であり、比較対象のSol版でも同種の事象が確認されている
- **Cost影響**: Writer+Support実費は約16分の1に削減(Sol版はRewrite込みで
  約¥766、Luna版は単一passで約¥47)。Audio実費はSTOPPED増加により若干上昇
  したが、総額は約65%削減(詳細は完了報告参照)
- **根拠レポート**: ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01完了報告
- **影響するCURRENT_SPEC項目**: QA/Human Review > ASR一致と発音品質の関係(新設)

## ER-006-AUDIO-COST-PILOT-02(2026-08-22)

- **Decision**: 音声パイプラインのASR Provider Routingを、**英語=OpenAI
  gpt-4o-mini-transcribe(Primary)、日本語=Azure Speech STT(維持)**の
  言語別構成でPilot導入する(SSOT: `er006_asr_provider_routing_01.py`)。
  Fail-closed設計(未登録言語は例外送出、暗黙fallback禁止)
- **根拠**: 同一トピックでの実測比較で、STOPPED数が7件→3件、TTS+ASR
  attempt総数が110→79(-28%)、Audio実費が¥306→¥199/pair(-35.1%)。
  誤って内容誤りをPASSさせたケースは0件
- **Validator方針変更**: street/St.のような通り種別略語(USPS標準の
  閉じた既知集合)は、canonical側テキストを基準に安全吸収する方針へ
  転換した(ER-006-POOL-PREPROD-HARDENING-01時点の「Saint曖昧性を
  理由に吸収しない」という以前の判断を上書き。canonical-anchored設計
  によりSaint/Streetの曖昧性は解消できることを確認したため)
- **未決定のまま保留**: Gemini TTS Batch API採用の可否(Human Review
  Artifact試聴待ち)。固有名詞"Ottoni"のASR認識限界への対応方針
  (発音辞書登録等は未着手)。量産再開の可否
- **根拠レポート**: ER-006-AUDIO-COST-PILOT-02完了報告
- **影響するCURRENT_SPEC項目**: なし(サービス仕様は無変更、実装
  アーキテクチャ層の変更のみ)

## ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01(2026-08-22)

- **Decision**: 1 Topic(B1+A2 pair)のExpected Production Costは
  **¥111.17/pairを正とする**(ER-006-AUDIO-COST-PILOT-02の¥106.4、
  ER-006-AUDIO-RETRY-CASCADE-PROD-01の¥113.0はいずれも今後参照しない)
- **根拠**: ¥106.4はPronunciation Research/Secondary ASR Cascade費用を
  一切含んでいなかった(その時点で未実装)。¥113.0はその費用を含めたが
  「Cascade発動1.3回/topic」という根拠不明の仮定を使っており、実測
  (3 topic・6 curated segment中2回発動)より高く見積もっていた。今回、
  Clean Cost(¥65.14)・Expected Waste(¥46.03、TTS/ASR retry実測1.68倍+
  Pronunciation Research実測cache miss率+Secondary ASR保守的estimate)を
  分離して再構築し、¥111.17/pairへ収束させた
- **併せて決定**: Validatorの数値正規化(cardinal/comma/decimal/percent/
  currency/ordinal third以降)を一般化する。ただし"first"・"second"は
  副詞用法との曖昧性が高いため対象外とする(実際に既存fixtureで誤PASSの
  回帰を検出したため)。序数接尾辞の除去は月名直後の日付文脈のみに限定
  する(従来の無条件除去は"28"と"28th"を誤って同一視する実バグだった)
- **未決定のまま保留**: Secondary ASR Cascadeの発動率(1回/topic、
  ESTIMATE)はランダムサンプルでの検証待ち。Production default化の
  判断もOPEN-48から継続保留
- **根拠レポート**: ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01完了報告
- **影響するCURRENT_SPEC項目**: なし(サービス仕様は無変更、Validator/
  原価計算ロジックのみの変更)

## ER-006-AUDIO-COST-SPEC-FIX-01(2026-08-22)

**管理ID: ER-006-AUDIO-COST-SPEC-FIX-01**

過去4タスク(AUDIO-COST-PILOT-02/PRONUNCIATION-LEDGER-SECONDARY-ASR-01/
AUDIO-RETRY-CASCADE-PROD-01/VALIDATOR-NUMERIC-COST-RECONCILE-01)で行った
実装アーキテクチャ決定を、SSOT(CURRENT_SPEC.md「Audio Production
Pipeline」節新設、OPEN_ITEMS.md、Model Routing Contract)へ正式に固定した。
本タスク自体は新規のAPI呼び出し・新規実装を行っていない
(ドキュメント統合+Drift Prevention Static Audit追加のみ)。以下8件を
正式Decisionとして記録する。

**Decision 1 — Model Routing: B1/A2 Writer・Support系はLuna**
- 内容: Writer/Writer Fact Check/Support/Support Fact CheckのApproved
  ModelをGPT-5.6 Lunaとする(既存Decision、ER-006-MODEL-ROUTING-CONTRACT-01
  で確定済み)
- Supersedes: ER-002/003時代のgpt-5.6-sol既定値
- 根拠タスク: ER-006-MODEL-ROUTING-CONTRACT-01、ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01(Audio面での再検証)
- 本タスクでの扱い: 既存Decisionの再確認・CURRENT_SPEC Model Routing Contract表の日付整合のみ、内容変更なし

**Decision 2 — Gemini TTS Batch API採用(方式として)**
- 内容: Gemini TTSの呼び出し方式は、Standard同期呼び出しではなくBatch
  API(`client.batches.create()`)をProduction標準として採用する
- 根拠: Batch APIは英語`gemini-2.5-pro-preview-tts`・日本語
  `gemini-3.1-flash-tts-preview`とも実機で完走確認済み(50%オフ)。
  ユーザーによるHuman Review試聴で、StandardとBatchの間に品質差が
  ないことを確認済み(voice/style/Structured Separation/spoken text/
  TTS model自体は無変更、実装方式のみの変更でありサービス仕様変更では
  ない)
- **実装状況の更新(2026-08-22、ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01)**:
  当初(ER-006-AUDIO-COST-SPEC-FIX-01時点)は採用「方針」の確定のみで、
  実際のProduction TTS生成6箇所は全てStandard呼び出しのままだった
  (OPEN-50として記録)。ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01で、
  新設した`er006_batch_tts_wiring_01.py`(既存のtts_call_fn(prompt)->bytes
  という呼び出し形状を保つdrop-in Batch factory、fail-closed設計・
  Standardへの暗黙fallbackなし)を、Production 6ファイルの全call site
  (`er003_v1_repro01_main_generate.py`・`er003_v1_sing01_news_tail_fix.py`・
  `er003_v1_sing01_point_headings_aoede.py`・`er003_v1_sing01_voice01_
  generate.py`・`er003_v1_n3_01_tts_generate.py`。
  `er003_v1_crosslevel_audio_02_common.py`はrepro01の関数を再利用する
  だけのため直接変更なしで自動的にBatch経由になる)へ配線した。
  1 Batch job = 1 itemの設計(item数に関わらずBatch料金割引は
  per-request適用のため、コスト効果は完全に得られる)。既存の
  ASR-first Retry Cascade・Validator・Master Audio Storeは無変更
  (TTS呼び出しの中身だけをStandardからBatchへ差し替えるdrop-in
  replacement)。item単位の成功/API error/empty result/invalid audio/
  missing responseの5分類・cost telemetry(`er005_cost_logger`統合)も
  実装済み。Static Audit(`er006_audio_cost_spec_fix_01_static_audit.py`)
  でStandard専用call_fn構築が実コードに残っていないことをassertion
  化して確認。OPEN-50はこの範囲でResolvedへ更新(TTS Pronunciation
  Hint配線は今回のスコープ外のまま、OPEN-47で継続)
- Supersedes: Standard呼び出しのみを前提としていた過去の暗黙の前提
- 根拠タスク: ER-006-AUDIO-COST-OPTIMIZATION-01(実機検証)、
  ER-006-AUDIO-COST-SPEC-FIX-01(方針の正式化・実装ギャップの明記)、
  ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01(Production実配線)

**Decision 3 — Primary ASR: 英語はOpenAI gpt-4o-mini-transcribe**
- 内容: 英語ASRのPrimaryを、Azure Speech-to-TextからOpenAI
  `gpt-4o-mini-transcribe`へ切り替える。日本語はAzureのまま維持する。
  SSOTは`er006_asr_provider_routing_01.py`(fail-closed、未登録言語は例外)
- 根拠: 同一トピック実測でSTOPPED数7→3件、attempt数110→79(-28%)、
  Audio実費¥306→¥199/pair(-35.1%)、誤って内容誤りをPASSさせたケース0件
- Supersedes: Azureを英語ASR Primaryとする旧構成
- 根拠タスク: ER-006-AUDIO-COST-PILOT-02

**Decision 4 — Master Audio Store採用**
- 内容: 固定/完全一致で再利用可能な音声は`er006_master_audio_store_01.py`
  経由で生成・キャッシュし、無条件の毎回TTS再生成をしない
- 根拠: 言語・レベル・voice・TTS model・style instruction hash・
  canonical text hash・processing version・sample rate等をキーとする
  ことで、条件不一致audioの誤再利用を防ぎつつ固定segmentの重複生成を
  避けられる
- Supersedes: 固定ナレーションを含め毎回無条件でTTS呼び出しを行っていた旧実装
- 根拠タスク: ER-006-AUDIO-COST-PILOT-02(最小実装・Production配線)

**Decision 5 — Validatorの数値正規化を一般化**
- 内容: cardinal number・桁区切りカンマ・小数点・パーセント・通貨・
  序数(third以降)の表記ゆれを、個別記事のwhitelistではなく一般規則で
  吸収する。ただし数値が異なる・時刻表記artifact・序数と基数の取り違え・
  記号欠落・年の違い・否定の有無の違いは絶対に吸収しない
- 根拠: Public Benches Boavida segment("28"↔"twenty-eight")・
  Subscriptions full_story_part2("Eighth"↔"8th")の実際のFalse NGを解消。
  検証中に「28」と「28th」を誤って同一視する序数接尾辞除去の実バグを
  発見・修正(月名直後の日付文脈のみに限定する安全な形へ変更)
- Supersedes: 個別ケースのみ対応していた旧Validator(街路名等の
  限定的な略語吸収のみ)
- 根拠タスク: ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01

**Decision 6 — Pronunciation Ledger採用(ASR側配線)**
- 内容: 固有名詞発音情報をPerplexity経由で事前取得しcacheする
  Pronunciation Ledgerを、Secondary ASRのPhrase List(`ledger_phrases`)
  経由でProduction 6箇所へ配線する。cache hitの場合は再調査しない。
  Perplexityクエリを機械的に「1トピック1リクエスト」へまとめない
  (品質低下を実測で確認したため)
- **実装状況の明記**: TTS生成側への発音ヒント注入
  (`augment_style_prefix_with_pronunciation()`)は基盤として保持するが、
  最難関ケース"Ottoni"のA/B検証で確実な改善効果を実証できなかった
  (mixed/負の結果)ため、Production TTS生成への強制配線は見送っている
- Supersedes: 発音情報を一切事前取得しない旧実装
- 根拠タスク: ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01、
  ER-006-AUDIO-RETRY-CASCADE-PROD-01(ASR側配線)

**Decision 7 — 固有名詞ASR不確実性はASR再検証を優先、TTS即時再生成を禁止**
- 内容: 固有名詞のASR不一致が疑われる場合、OpenAI Primary#1→Primary#2→
  Azure Secondary+Phrase List#1→Secondary#2→Human Reviewの順でASR側の
  再検証を先に尽くし、この過程を経ずにGemini TTSを即座に再生成する
  古い経路を禁止する。TTS再生成は真の内容誤り・数値/日付の意味的な違い・
  否定の違い・重要語の欠落追加・TTS技術的失敗・Human Review確定後の
  実音声誤りに限定する
- 根拠: 3 Topic実測で6対象segment中4件がPrimary ASR単体でPASS
  (旧構成では6〜12回試行のSTOPPEDだった箇所)。true content誤PASSは
  0件、new savings実測+¥128.4
- Supersedes: 「Primary ASR FAIL→即Gemini TTS再生成」という旧retry方針
- 根拠タスク: ER-006-AUDIO-RETRY-CASCADE-PROD-01

**Decision 8 — Cost定義4区分をSSOT化**
- 内容: Historical Actual(実際に支払われた金額)/Clean Production Cost
  (全工程初回成功時の理論下限、¥65.14/pair)/Expected Conditional Waste
  (Primary#2・Secondary ASR・Pronunciation Research・TTS retry等の
  条件付き追加費用の期待値、¥46.03/pair)/Expected Production Cost
  (Clean+Waste、¥111.17/pair)の4区分を、今後のER-006+報告の共通言語
  とする。Expected Production Costは推定を含む進化中のbaselineであり、
  恒久固定値ではない
- Supersedes: ER-006-AUDIO-COST-PILOT-02の¥106.4/pair、
  ER-006-AUDIO-RETRY-CASCADE-PROD-01の¥113.0/pair(いずれも今後参照しない)
- 根拠タスク: ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01(再構築)、
  ER-006-AUDIO-COST-SPEC-FIX-01(用語定義自体のSSOT化)

**Drift Prevention(Static Audit)**: 上記Decision中、機械的に検証可能な
部分(旧Azure英語Primary直接呼び出しの不在、旧Validator直接呼び出しの
不在、旧retry loop [ASR不確実性からの即時TTS再生成] の不在、Master
Audio bypassの不在、Sol modelの不在、Pronunciation Ledgerが呼び出し
経路から無視されていないこと)は、新規作成した
[er006_audio_cost_spec_fix_01_static_audit.py](er006_audio_cost_spec_fix_01_static_audit.py)
で全件PASSを確認した(2026-08-22時点)。Batch API配線(Decision 2の実装
ギャップ)のみ、当時は既知GAPとして明示的にassertion対象外で状況報告
する設計とした(誤って「配線済み」と偽装しないため)。**2026-08-22
追記(ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01)**: Batch配線の実装完了に
伴い、このチェックも正式なassertion対象へ昇格させた(詳細は下記
新規Decision参照)。

- **根拠レポート**: ER-006-AUDIO-COST-SPEC-FIX-01完了報告
- **影響するCURRENT_SPEC項目**: 「Audio Production Pipeline」節(新設)、
  「Model Routing Contract」節のTTS/ASR行

## ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01(2026-08-22)

**管理ID: ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01**

- **Decision**: ER-006-AUDIO-COST-SPEC-FIX-01のDecision 2(Gemini TTS
  Batch API採用)を、実際のProduction TTS生成6経路へ実配線した
  (詳細は上記Decision 2の実装状況追記を参照)。加えて、CURRENT_SPEC.md
  「QA / Human Review」節に残っていた「Azure STTを全内容確認・境界
  検証に使用」という旧ASR記述を、現行の言語別Routing仕様(英語Primary
  =OpenAI `gpt-4o-mini-transcribe`、日本語=Azure、Azureは英語Secondary
  としても使用、最終判断はASR単独では行わない)へ整合させた
- **根拠**: 実装ギャップ(OPEN-50)の解消。新設`er006_batch_tts_wiring_01.py`
  は既存のtts_call_fn(prompt)->bytesという呼び出し形状を保つdrop-in
  replacementとして設計し、ASR-first Retry Cascade・Validator・Master
  Audio Store・spoken text・voice・style instructionは一切変更していない
  (実行方式のみの変更)
- **設計判断の明記**: タスク仕様では「複数segmentをまとめて投入」する
  グループ投入も許容されていたが(実装方法は過度に指定しないとの前提)、
  既存6ファイルの1segmentずつのretry loop制御フローを書き換える大規模
  リファクタリングは、Production安定性優先の方針(CLAUDE.md)に照らして
  リスクが高いと判断し、今回は1 Batch job = 1 itemのdrop-in方式を
  主たる配線方式として採用した。Gemini Batch APIの料金割引(50%オフ)は
  job内item数に関わらずper-request適用されるため、この設計でも
  コスト削減効果は完全に得られる。複数item一括投入用のAPI
  (`submit_batch_multi`/`wait_for_batch_multi`)は同モジュール内に将来の
  最適化余地として用意したが、今回はいずれの本番ファイルからも呼ばれて
  いない
- **未決定のまま保留**: Secondary ASR Cascade default ON化(OPEN-48から
  継続)。TTS Pronunciation Hint配線(Ottoni検証で効果不明確だったため、
  今回のBatch配線と同時に有効化しない、OPEN-47/OPEN-50から継続)
- **根拠レポート**: ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01完了報告
- **影響するCURRENT_SPEC項目**: 「Audio Production Pipeline」節の
  「Gemini TTS実装方式」行(NOT_WIRED→WIRED)、「Model Routing Contract」
  節のTTS行、「QA / Human Review」節のASR記述

## ER-006-POOL-MASTER-ADOPTION-N4N6-RESUME-01(2026-08-22)

**管理ID: ER-006-POOL-MASTER-ADOPTION-N4N6-RESUME-01**

- **Decision**: Pool型(Evergreen)記事の生成対象となる20 Topicの正式
  母集団を、ユーザー承認のもと[POOL_TOPIC_MASTER.md](POOL_TOPIC_MASTER.md)
  として新規制定した。No.1〜3(Public Benches/Subscriptions/Startups)は
  既存生成物と一致することを確認の上で編入。No.4〜6(Supermarket
  Shuffle/Cafes/Delivery Tracking)を次回Production対象として確定した
- **背景**: ER-006-POOL-ADOPTION-N4N6-PRODUCTION-01で、「20 Topicリスト
  の一次資料をリポジトリから特定する」という前提が実際には満たされて
  いない(No.1〜3はTopic Selectionを意図的にスキップして手動選定された
  Pilot用の3件であり、20件全体を記録したファイルは一度も存在しな
  かった)ことが判明し、名前の推測・新規作成をせずSTOPして報告した。
  今回、ユーザーが残り17件を含む20件全体を新たに確定・承認したことで
  このSTOP条件が解消した
- **Topic Selection routingとの関係**: No.4〜6は、通常のTopic Selection
  Production Model(GPT-5.6 Luna)を再実行せず、ユーザーが本Master
  リストから直接指定した。これは既存のTopic Selection Routing Contract
  (`er006_model_routing_contract_01.py`の`TOPIC_SELECTOR_MODEL`)を
  変更するものではなく、「今回はユーザー指定という特別な選定経路を
  使った」という1回限りの記録であり、No.7以降の新規選定が必要になった
  場合は通常通りLuna Topic Selectionを使う
- **重複SSOT回避**: 20件のリスト本文はPOOL_TOPIC_MASTER.md 1箇所にのみ
  記録し、他ファイル(本Decision含む)へは複製しない
- **根拠レポート**: ER-006-POOL-MASTER-ADOPTION-N4N6-RESUME-01完了報告
- **影響するCURRENT_SPEC項目**: なし(サービス仕様は無変更、新規SSOT
  ファイルPOOL_TOPIC_MASTER.mdの制定のみ)

## ER-006-POOL-ADOPTION-AUDIT-01 / ER-006-POOL-N4-N6-PRODUCTION-01 / ER-006-PRODUCTION-THROUGHPUT-GATE-01(2026-08-23)

**管理ID: ER-006-POOL-MASTER-ADOPTION-N4N6-RESUME-01(3区分まとめて記録)**

- **Decision(Adoption Audit)**: 既存3記事の最終採用Candidateを確定した。
  Public Benches=script Luna版+audio ASR-Pilot-02版(parts.json完全一致
  確認済み)、Subscriptions/Startups=唯一存在する原初版(Sol Writer)。
  Script/Audio一致確認では、送信テキストと正式scriptの完全一致(既知の
  安全な正規化除く)を確認した一方、6segmentが機械ASR検証未合格のまま
  assembled音声に含まれていることを検出し、ユーザー確認Artifactで
  明示的に警告した。詳細は[ER-006-POOL-ADOPTION-AUDIT-01_diff.md](ER-006-POOL-ADOPTION-AUDIT-01_diff.md)
- **Decision(N4-N6 Production)**: No.4〜6を現行Production仕様(Luna
  Writer/Support/FactCheck、Gemini Batch TTS、OpenAI English Primary
  ASR、Azure Japanese ASR、現行Validator、Master Audio Store)で通し
  生成した。実在の学術論文・トレード記事をWebSearch/WebFetchで収集し
  Ledgerへ組み込んだ。Sol呼び出し0件、Standard TTS呼び出し0件を確認
- **Decision(Throughput Gate)**: No.4単独・No.5+No.6の2 lane並列実行
  の実測から、Gemini Batch TTSが総所要時間の83〜96%を占める支配的
  ボトルネックであることを確認した。20 Topic/day判定は`AT_RISK`
  (4〜5 lane並列の実測なし、Human Review所要時間未計測のため)。
  詳細は[ER-006-PRODUCTION-THROUGHPUT-GATE-01_report.md](ER-006-PRODUCTION-THROUGHPUT-GATE-01_report.md)
- **未決定のまま保留**: No.4〜6の最終採用判断(ユーザー試聴待ち、
  OPEN-53)、4〜5 lane並列実行の実測(OPEN-51)、Key Phrase Selectorの
  retry loop追加要否(OPEN-52)
- **根拠レポート**: ER-006-POOL-ADOPTION-AUDIT-01_diff.md、
  ER-006-POOL-N4-N6-PRODUCTION-01完了報告(本Decisionの一部として
  統合報告)、ER-006-PRODUCTION-THROUGHPUT-GATE-01完了報告
- **影響するCURRENT_SPEC項目**: なし(サービス仕様は無変更)

## ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01(2026-08-24)

- **Decision 1(数式Validator正式採用)**: 前タスク(ER-006-GATE-
  CALIBRATION-ASR-CASCADE-MATH-VALIDATOR-01)で実装した数式表記正規化
  (Markdown italic変数表記、`=`/`<`/`>`/`×`/数字間`x`、Unicode上付き
  指数・ASCIIキャレット指数、規則的な単数形/複数形吸収)を、Production
  標準Validatorの正式仕様として採用する。Regression fixtureは既存32件+
  新規23件=**計55件、全PASSを再確認**した上で採用した
- **Decision 2(ASR Secondary Cascade Production ON)**: `er006_secondary_
  asr_01.py`の`FEATURE_FLAG_SECONDARY_ASR_ENABLED`を`False`→`True`へ
  変更し、Production既定でCascadeを有効化した。前タスクで発見・修正した
  「A2側の複数形差がCascade対象外条件を誤って満たしてしまう」バグの
  修正後、実No.6 Sweeny音声(B1/A2)でCascadeがPrimary#1→#2→Secondary#1→
  #2→Human Reviewの順で正しく動作し、TTS再生成0件を確認した上で有効化
  した。全Production call site 6箇所は`cascade_enabled=secondary_asr.
  FEATURE_FLAG_SECONDARY_ASR_ENABLED`という形でモジュール定数を呼び出し
  時に参照するため、この1箇所の変更のみで全call siteへ反映される
- **Decision 3(Research Coverage GateはProduction未配線のまま据え置き)**:
  No.1(Public Benches)・No.2(Subscriptions)の較正後Gate判定
  `MORE_RESEARCH_REQUIRED`を、既存Research/Ledger/完成記事/Fact Check/
  Ledger Deviation Checkのみで追加検証した結果、8 missing_items中
  TRUE_COVERAGE_GAPは0件、FALSE_POSITIVE 7件、BORDERLINE 1件と判定した。
  No.1はGateへ渡していたtitleがpre-Writer working title(POOL_TOPIC_
  MASTER.md記載)であり、Writerが実際に採用した最終タイトルと異なって
  いたことが根本原因(実際の最終タイトルで再実行するとCOVERAGE_PASSへ
  反転することを確認、新規Researchなし)。No.2は最終タイトルで再実行
  してもMORE_RESEARCH_REQUIREDのままであり、「因果的『なぜ』を問う
  Topicで、記事が実際には行動効果Evidenceを主張せず概念的な説明に
  留める」パターンへの較正が前タスクでは不足していたことが判明した。
  この2点により、Gate単体の判定精度はまだProduction基準に達していないと
  判断し、**Production配線は行わない**(タスク仕様Part A-3で明示的に
  禁止されている通り、ユーザー指示なしに配線しない)
- **根拠レポート**: ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01
  完了報告
- **影響するCURRENT_SPEC項目**: 「Audio Production Pipeline」節の
  Validator項(55件へ更新、数式表記・複数形吸収を追加記載)、ASR-first
  Retry Policy項(`FEATURE_FLAG_SECONDARY_ASR_ENABLED=True`へ更新)

## ER-006-RESEARCH-COVERAGE-GATE-DEFER-01(2026-08-24)

- **Decision**: Research Coverage Gateを、現時点ではProductionへ導入
  **しない**。`DEFERRED / PROMISING_BUT_MORE_DATA_NEEDED`として将来の
  織り込み候補に位置づけ、実装・較正の成果は温存する
- **背景**: ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01で
  No.1(Public Benches)・No.2(Subscriptions)の較正後Gate判定を追加
  検証した結果、TRUE_COVERAGE_GAP 0件、FALSE_POSITIVE 7件、BORDERLINE
  1件と、過検知が実運用水準に対してなお残っていることが判明した。
  一方、Gate実費は約¥0.31/topic、Clean Cost増加は約0.48%(基準値
  ¥65.14/pair)と、コスト面の障壁自体は小さいことも確認済み
- **見送りの理由**: (1) No.4型のResearch不足をWriter前に検知できる
  可能性は確認済みで、Gateという仕組み自体の有用性は否定されていない、
  (2) しかし残る較正課題(①Gateへ渡すtitleの入力契約[pre-Writer working
  titleと実際の最終タイトルの乖離]、②因果的タイトルでも記事本文は
  概念説明に留める正当な編集パターンへの対応)の解消には追加の開発・
  検証時間が必要、(3) 現段階ではExternal/User Validation(実際の
  学習者・プロジェクト責任者による試聴)を優先すべきであり、Gate較正へ
  追加の開発時間を割かない、とユーザーが判断した
- **今回実施しなかったこと**: Gate promptの追加調整、新規backtest、
  Production配線、新規API call、No.7以降の記事生成(いずれもタスク
  仕様の非対象事項として明示的に除外)
- **再検討Trigger**: (a) 今後のProductionでNo.4型のResearch不足→Writer
  再生成が複数回発生する、(b) Additional Research/Writer Costが再び
  大きくなる、(c) External/User Validation後、量産フェーズへ移行する、
  (d) Topic生成数が増え、Gate評価用サンプルが自然に蓄積する。いずれか
  発生時に、OPEN-54記載の残課題への対応から再開する
- **根拠レポート**: OPEN_ITEMS.md OPEN-54(本Decisionにより正式化)、
  ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01完了報告(検証
  データの一次情報)
- **影響するCURRENT_SPEC項目**: なし(Production仕様として未追加のまま、
  今回も追加しない)

## ER-007-SPOKEN-EVIDENCE-DENSITY-AB-01 Part B(2026-08-24)

- **Decision**: No.2(Subscriptions)A2 comment_3の「やめにくくする」が「やめにくかする」寄りに
  聞こえた問題は、**TTS固有の偶発的発音ゆれ**と判定する。特定の音韻パターン(「くく」の連続
  音節等)に起因する一般化可能な問題ではないため、テキスト書き換え・「くく」の表記変更・
  No.2専用whitelistのいずれも行わず、**音声の再生成のみ**で対応する
- **根拠**: canonical text・TTS入力とも正しく、reading-safety処理による変更もなかった。実際の
  生成音声のAzure ASR書き起こしは「やめにくかする」であり、主観的な聞き取り誤りではなく音声
  自体に実際のゆれがあったことをまず確認した。次に、同一canonical textを本番と同じ生成関数で
  4回再生成したところ、4回とも正しく「やめにくくする」と発音・認識され、再現しなかった
  (再現率0/4)。これにより、構造的・音韻的に不可避な問題ではなく、単発の生成ゆれだったと
  結論づけた
- **副次的発見**: A2の長い(30文字超)Comment/Support segmentの検証は「先頭数文字一致+文字数
  許容範囲」のみを見ており、文中の一部だけが別の音へ変わっても検出できない設計上のgapが
  ある(短いsegment向けのPHONETIC_MATCH等は30文字以下のみ対象)。今回は1件のみの発見のため、
  新規Validator実装は見送り、OPEN-57へ記録した
- **根拠レポート**: ER-007-SPOKEN-EVIDENCE-DENSITY-AB-01完了報告
- **影響するCURRENT_SPEC項目**: なし(既存の短いsegment向け検証方式・Validator仕様は無変更)

## ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01(2026-08-25)

- **Decision**: 日本語ASR検証を、旧「文頭2文字prefix一致+文字数チェック」方式から、
  英語Validatorと同じ思想の全文Validator(`er007_ja_asr_validator_01.py`)+
  Secondary Cascade(`er007_ja_secondary_asr_01.py`)へ置き換え、**Production 3箇所
  (`er003_v1_repro01_main_generate.py`のJapanese分岐、`er003_v1_sing01_voice01_
  generate.py`、`er003_v1_n3_01_tts_generate.py`)へ実配線した**。あわせて日本語
  Primary ASRをAzure Speech STTからOpenAI `gpt-4o-mini-transcribe`へ切り替え、
  英語と同一構成に統一した(`ASR_ROUTING["ja"]`、`FEATURE_FLAG_JA_PRIMARY_OPENAI=True`)
- **背景**: ER-007-EVIDENCE-WORDCOUNT-JA-ASR-EFFECTIVENESS-AUDIT-01で、旧方式は
  30文字を超えるsegment(A2のPreview/Comment等)に対し実質的な内容検証を行っておらず
  (prefix一致+長さのみ)、6種類の誤り(内容の欠落・置換・数字誤り・否定反転等)全てが
  検出をすり抜けることを、fixtureによるblind-spot testingで実証していた
  (ER-007-EVIDENCE-WORDCOUNT-JA-ASR-EFFECTIVENESS-AUDIT-01完了報告)
- **配線判断の根拠(Part Fの6条件、全て満たすことを確認済み)**: (1) 新Validatorが
  実データ・fixture(20件)で6種類の誤りを全て検出、(2) 新Cascadeが真の内容誤りを
  救済しないことを6件のmock testで確認、(3) OpenAI mini日本語ASR品質がAzureと
  「比較可能、明確な劣化なし」(n=14実音声、13/14が同等以上)、(4) cost/latency
  projectionが大幅改善(-82%/-70%、96 segmentシミュレーション、実測価格ベース)、
  (5) fixtureが全種類の既知の誤りパターンを網羅、(6) STOP条件(品質不足・誤検知過多・
  誤PASS発生・cost/latency悪化)いずれにも該当しなかった
- **既知の残存限界(受容済み)**: kakasi(形態素解析器なし、規則ベース)は孤立漢字の
  異読み分岐(「頃」のgoro/koro、「後」のあと/のち等)を、diff span前後4文字の文脈
  パディングでも完全には解消できない場合がある。実データ96 segment中約3件
  (約3.1%)で発生を確認したが、影響方向は常にfalse positive(安全側: 不要なretryが
  発生するのみで、誤ってPASSすることはない)。配線後のProduction smoke test
  (`verify_ja_cascade_production_on.py`、既存音声・実OpenAI ASR呼び出し)でも同種の
  1件を実際に再現し、既知の限界どおりの挙動(TRUE_CONTENT_MISMATCHとして検出され
  retry対象になるのみ)であることを確認した
- **非対象事項(今回変更しなかったこと)**: 日本語segmentの分割・再設計、TTS
  モデル変更、第3のASR provider追加、No.7以降の記事生成、Evidence Compression
  仕様の再調整、Research Coverage Gateの再検討、英語Validator・Writer仕様の変更
- **根拠レポート**: ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01完了報告、
  OPEN_ITEMS.md OPEN-61
- **影響するCURRENT_SPEC項目**: 「QA / Human Review」節のASR診断項、「Audio
  Production Pipeline」節のPrimary ASR Routing項・Validator(日本語)項(新設)・
  ASR-first Retry Policy(日本語)項(新設)・Production TTS/ASR call site一覧項、
  「Model Routing Contract」節のASR / Audio QA項

## ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01(2026-08-25)

- **Decision**: 日本語ASR Cascade配線直後にユーザーから指摘された2件の
  問題を修正する。(A) `stop_retrying=True`(Cascadeを尽くしても未解決)
  後もTTS再生成が続くbugを`er003_v1_sing01_voice01_generate.py`・
  `er003_v1_n3_01_tts_generate.py`で修正、(B) 濁点/半濁点の有無だけが
  異なる読みゆれ(「頃」のgoro/koro等)を`TRUE_CONTENT_MISMATCH`(即TTS
  retry対象)ではなく`ASR_VALIDATION_UNCERTAIN`(Cascade対象)へ分類する
  よう`er007_ja_asr_validator_01.py`を拡張する
- **背景**: ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01のProduction
  配線直後、ユーザーが「漢字読みの誤検知・ASR表記ゆれだけの場合にTTS
  再生成へ進む経路が残っていないか」を確認するよう依頼した
  (ER-007-JA-ASR-TTS-RETRY-PATH-CHECK-01)。調査の結果、実際にどちらも
  該当することが判明した: 経路Aは、Cascade呼び出しを新規2箇所へ配線
  する際、既存の正しい実装(`er003_v1_repro01_main_generate.py`)にある
  `stop_retrying`短絡処理の移植漏れ。経路Bは、`is_entity_like_
  mismatch_ja()`がカタカナ/acronymらしさのみをCascade対象基準にして
  おり、「頃」をkakasi(形態素解析なしの規則ベース読み変換)が文脈なしで
  連濁形「ごろ」と読んでしまう実例(実データsmoke testで発見)を拾え
  なかったこと
- **修正内容**: 経路Aは、`voice01.py`(標準/フォールバック両経路)・
  `n3_01.py`(フォールバック経路)へ`if stop_retrying:`短絡処理を追加
  (英語側`crosslevel_audio_02_common.py`の既存実装を参考)。経路Bは、
  読みをひらがな変換後、Unicode NFD正規化で濁点/半濁点(結合文字)を
  除去した「清音化」文字列同士の比較(`_reading_equal_allowing_
  voicing()`)を新設し、一致すれば`phonetic_uncertain=True`として
  Cascade対象に含めた。「頃」という文字列へのハードコードではなく、
  一般的な清音化比較であることを、「頃」を含まない5組の合成ペア
  (か/が、さ/ざ、た/だ、は/ば、は/ぱ)で直接検証した
- **安全性の確認**: `phonetic_uncertain`はCascade対象への分類にのみ
  影響し、`should_pass`を直接Trueにしない(既存設計、Part Bで変更して
  いない)ため、たとえ意味の異なる語同士(例: 柿/鍵、清音化後に偶然
  一致する既知のトレードオフとして発見・記録)を誤って拾っても、
  誤PASSは構造的に起こりえない(Cascadeを尽くしてもHuman Reviewへ回る
  だけ)。「漢字なら全部Cascade」になっていないことも、清音化しても
  一致しない別読みの語(月のつき/がつ)がTRUE_CONTENT_MISMATCHのまま
  残ることで確認した
- **実測影響**: No.1〜6の既存96 Japanese segmentのうち、経路Bの誤分類で
  実際に影響を受けていたのは2件(No.5・No.6のA2 preview、同一の
  「ころ/頃」パターン)。経路Aは今回のCascade配線と同じセッション内で
  発見・修正したため、実運用ログには影響が現れていない(worst-case
  見積りのみ、詳細は完了報告Part E参照)
- **根拠レポート**: ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01完了報告
- **影響するCURRENT_SPEC項目**: 「Audio Production Pipeline」節の
  Validator(日本語)項(濁点/半濁点許容の追加を反映)、ASR-first Retry
  Policy(日本語)項(stop_retrying無視bug修正を反映)

## A2/B1 Point Structure Semantic Alignment(2026-08-25)

- **Decision**: A2/B1のPoint One・Point Two間の意味的不整合(ER-008-A2-
  STORY-B1-SUPPORT-COMPATIBILITY-AUDIT-01/OPEN-63で発見)を、生成後の
  互換性Checkerで検出・修正するのではなく、**生成前の共通設計(Shared
  Point Blueprint)をSingle Source of Truthとして防止する**方針を正式
  採用する。A2・B1で文章・語数・全Factを完全共通化するのではなく、
  「どのFactがどちらのPointに属するか」「各Pointの中心結論」という
  意味構造だけを共通化し、表現・語彙・情報量は各CEFRレベルへ独立に
  最適化されたままとする
- **背景**: OPEN-63のAuditで、No.5(カフェ)・No.6(配達追跡)それぞれで、
  A2 WriterとB1 Writerが同じVerified Fact Ledgerを見ながら独立に
  Point One/Twoへfactを振り分けた結果、両者の間で内容が食い違う
  (No.5: B1のPoint TwoがA2には無い主張[顧客労働者の価値]を中心に
  据える、No.6: 同じ実験詳細がA2ではPoint One・B1ではPoint Twoに
  配置される)ことが判明していた
- **設計**: Verified Fact LedgerのFact(既存の`fact_id`をそのまま
  再利用)を、Point 1/Point 2それぞれの`common_fact_ids`(両レベル
  必須)・`optional_b1_fact_ids`(B1のみ可)・`comment_anchor`(共通
  Commentが安全に参照できる範囲)等へ振り分けるBlueprintを、A2/B1
  Writer呼び出し前に1回生成し、両Writerへ共通入力として渡す。
  互換性の検証は、Writer/Comment自身が申告するfact_id利用状況
  (応答末尾の軽量なfenced JSON block)とBlueprintの宣言を突き合わせる
  **決定論的なStructural Validator**で行い、意味理解を要する新しい
  Runtime LLM Checkerは追加しない
- **実装**: [er008_shared_point_blueprint_01.py](er008_shared_point_blueprint_01.py)(Schema・prompt構築)・
  [er008_point_blueprint_validator_01.py](er008_point_blueprint_validator_01.py)(Structural Validator)を新設し、
  既存Writer/Support Pipeline(4ファイル)へ全てオプション引数として
  配線した(Blueprint未指定時は既存Topicと完全に同一の挙動、既存
  No.1〜6を含む全既存Topicへの影響ゼロを確認済み)
- **検証範囲(重要な限定)**: fixture(18件、タスク仕様指定の6件含む)は
  全PASS。No.4〜6については、既存Ledgerと実記事本文を手作業で突き
  合わせた**後付けBlueprintによる机上Simulation**を行い、Validatorが
  No.4を正しくPASSさせ、No.5・No.6の実際の不整合を正確に検出する
  ことを確認した。**ただし、Blueprint生成・Writer/Comment生成の実LLM
  呼び出しによる検証(承認が必要な新規有料API呼び出し)は今回実施して
  いない**。「LLMが実際にBlueprintの制約へどこまで従うか」という
  価値仮説の核心部分は、次段階の検証を待つ
- **今回実施しなかったこと**: 有料Writer APIによる新規記事生成、
  新規TTS/ASR生成、既存No.1〜6記事の一括再生成、新しいRuntime LLM
  Checkerの追加、Production仕様(CURRENT_SPEC.md)への正式反映(実LLM
  検証前のため時期尚早と判断)
- **根拠レポート**: ER-008-POINT-BLUEPRINT-01完了報告、OPEN_ITEMS.md
  OPEN-64(本Decisionにより新規記録)
- **影響するCURRENT_SPEC項目**: なし(実LLM検証前のため今回は追加
  しない、次段階完了後に正式仕様化を検討する)

## ER-008-N7-SHARED-POINT-BLUEPRINT-3LEVEL-PILOT-01(2026-08-25)

- **Decision**: Shared Point Blueprint機構(A2/B1 Point Structure
  Semantic Alignment)を、新規Topic No.7「Assigned Desks Are Back in
  Some Offices」で初めて実LLM・実音声で検証する。Production採用の
  正式決定は行わない(タスク仕様通り、ユーザーが比較試聴Artifactを
  聴取した後に別途判断する)
- **背景**: 前タスクでBlueprint機構自体は実装済みだったが、実LLM
  生成・実Writer/Comment生成・実音声による検証はまだ行われておらず、
  「Blueprintの制約へLLMがどこまで従うか」という中心的な価値仮説が
  未検証のままだった
- **実施内容**: Research(実Web調査3件)→Evidence Pack/VFL(Fact
  F-001〜F-012)→Shared Point Blueprint(実LLM初回生成)→A2/B1
  Writer(Blueprint使用)→Fact Check/Ledger Deviation→Support
  (B1 Comment 3/4はcomment_anchor使用)→TTS(今回のみ同期モード、
  DEV/VALIDATION限定)→Assembly、を全て実際のAPI呼び出しで実行した。
  加えて、B1/A2の既存完成音声を新規TTS無しで組み合わせる
  「Middle/Bridge」音声組み立てをPilot専用スクリプトとして新規実装した
- **結果**: Point Oneはfact_id完全一致、Point Twoは必須factで一致
  (補助factの選択にA2がoptional_b1_fact_idを使う軽微な逸脱があったが
  内容矛盾やネタバレは生じなかった)。B1 Comment 1〜4は全てA2本文へ
  接続しても自然に成立することを確認した。Middle音声は新規TTS/ASR
  0件で完成した。A2側2segment(preview/comment_1)は、ER-007で既に
  開示済みのJA ASR「後」異読み限界により機械検証未合格のまま採用され
  ており、人間による聴取確認が必要
- **今回実施しなかったこと**: Production Level追加、Level名称決定、
  UI変更、Subscription仕様決定、全既存Topicへの展開。CURRENT_SPECの
  Production TTS標準(Batch API)は変更していない(同期TTSは今回限りの
  DEV/VALIDATION実行)
- **根拠レポート**: ER-008-N7-SHARED-POINT-BLUEPRINT-3LEVEL-PILOT-01
  完了報告、OPEN_ITEMS.md OPEN-64、比較試聴Artifact
  (https://claude.ai/code/artifact/de5ca386-8f04-470d-926b-edcb579a58d7)
- **影響するCURRENT_SPEC項目**: なし(Production採用の正式決定を今回
  行っていないため、CURRENT_SPECへの反映はユーザーの試聴・判断後とする)

## ER-008-N7-MIDDLE-SPEC-STORY-BALANCE-KEYPHRASE-AUDIT-01(2026-08-25)

- **Decision**: Middleの仕様を「A2 storyをベースにB1 supportを足したもの」
  から「B1をベースに、本文系7箇所(Full Story Part1/2、Point One/Two見出し
  +本文、In One Line)だけをA2に差し替えたもの」へ再定義し、実装をこれに
  合わせて作り直した。Key Phrase(英語phrase・構造)は今後B1のものを使う
  (前タスクの「A2のKey Phraseを使う」という推奨を本タスクの仕様指示により
  覆した)。Production採用の正式決定は今回も行わない(引き続きPilot段階)
- **背景**: 前タスクで実装したMiddleは「A2ベースにB1のsupportを差し込む」
  形だったが、ユーザーからMiddleは「基本B1、ニュース本文だけA2」という
  逆方向の設計であるべきという指示があった。またNo.7のA2 Full Storyが
  Part1=38語と短く、Middleにも影響することが判明した。加えてKey Phraseの
  番号読み上げ→phraseの間のpauseがA2よりB1の方が長く感じるという指摘が
  あった
- **実施内容(3件)**:
  1. Middle組み立てを`er003_v1_n3_01_assemble.py`の`build_b1_timeline()`
     をそのまま使う形に全面書き換え。B1の`apply_b1_gain()`出力を土台に
     Story系7箇所だけA2音源(B1のtarget_rmsへ再gain)へ差し替える方式とし、
     独立した日本語タイトルsegmentは廃止(B1の構造に元々存在しないため)
  2. No.4〜7のFull Story Part1/2語数を実測。No.4〜6はA2 212〜300語・
     B1 224〜302語で安定していたのに対し、No.7はA2 102語(Part1=38語)・
     B1 124語と突出して短く、構造的な問題ではなく単発の外れ値と判断。
     Evidence(Fact)を増やさず、状況描写・つなぎ等の物語技法のみで
     No.7 A2 Full StoryをPart1=99語/Part2=70語(計169語)へ拡張した。
     拡張1回目でLedger未根拠の主張が2件混入したため、該当箇所のみを
     指定した2回目の修正LLM呼び出しで是正し、Ledger Deviation件数を
     拡張前と同じ4件(内容も同一カテゴリ)まで戻したことを確認した
  3. Key Phraseのpause差の原因を実測で特定。B1側の音源読み込み
     (`load_b1_sources()`)にA2側で既に行っていた`tight_speech_only()`
     によるsafety margin無音のtrimmingが抜けており、体感pauseがB1で
     0.600秒・A2で0.400秒と異なっていた(pause定数自体はA2/B1で完全に
     同一、`IMPLEMENTATION_DIFF`)。共有ProductionファイルへA2と同じ
     trimmingを追加して統一した(今後の全B1/Middle生成に影響する
     恒久修正)
- **結果**: No.7 A2/B1/Middleを全て再生成・再組み立てし、比較試聴
  Artifactを更新した。新規有料呼び出しはLLM4件(story拡張・是正・
  deviation再検証2件)とTTS/ASR各2件(該当2segmentのみ再生成)の計
  約$0.05(¥8)。Middle自体は新規TTS/ASR 0件のまま。全体回帰テストは
  1774/1775 PASS(既知のharness自己テストの1件のみ、影響なし)
- **今回実施しなかったこと**: Middleの正式Level名称決定、UI追加、
  Pricing変更、No.8生成、Full Story語数の下限をPromptへ機械的に
  ハードコードすること(下限の目安はユーザーへの提案に留め、独断で
  仕様化はしていない)
- **根拠レポート**: ER-008-N7-MIDDLE-SPEC-STORY-BALANCE-KEYPHRASE-AUDIT-01
  完了報告、比較試聴Artifact
  (https://claude.ai/code/artifact/de5ca386-8f04-470d-926b-edcb579a58d7)
- **影響するCURRENT_SPEC項目**: なし(Production採用の正式決定を今回も
  行っていないため、CURRENT_SPECへの反映はユーザーの試聴・判断後とする)

## ER-008-N7-BASELINE-RESET-AND-MIDDLE-DEFER-01(2026-08-25)

- **Decision**: No.7「Assigned Desks Are Back in Some Offices」を、Middle
  Pilot検証(ER-008-N7-SHARED-POINT-BLUEPRINT-3LEVEL-PILOT-01/ER-008-N7-
  MIDDLE-SPEC-STORY-BALANCE-KEYPHRASE-AUDIT-01)以前の正式Fixed A2/B1
  Production仕様だけを使ってB1/A2の2版として再生成した(Shared Point
  Blueprint・comment anchor制約・Full Story延長処理・Key Phrase pause
  調整のいずれも不使用)。Middle/Bridgeは`DEFERRED / FUTURE_CANDIDATE`
  として正式に保留し、今回は生成しない
- **背景**: Middle Pilot検証中に追加した複数の検証専用処理(Blueprint・
  comment anchor・Story延長・Key Phrase pause trimming)が、No.7の
  A2/B1本体にも影響していた。中間仕様を検討する前に、まず「素の正式
  Production仕様で生成した場合に、指摘されていた問題(本文が短い・
  本文とCommentの接続が不自然・Key Phraseのpauseが違う)が実際に
  再現するか」を切り分ける必要があった
- **実施内容**: Research(既存のVerified Fact Ledgerをそのまま再利用、
  Blueprintに依存しないため未再実行)→Writer(`blueprint=None`で
  `er006_pool_pilot_01_writer.py`を実行、既存Topicと完全に同一の挙動)
  →Support(`blueprint=None`でComment 3/4のcomment anchor制約なし)→
  TTS/ASR(検証速度優先で同期呼び出し、Batch API仕様は無変更)→Assembly、
  を全て実行した。加えて、前タスクでB1側のKey Phrase読み込みに追加した
  `tight_speech_only()`のtrimmingを、共有Productionファイル
  ([er003_v1_n3_01_assemble.py](er003_v1_n3_01_assemble.py))から一旦
  revertし、真の未修正Baseline挙動を計測した
- **結果(3つの疑いのある問題を個別に検証)**:
  1. **Full Story短さ問題**: 再現しなかった。BaselineのA2は
     Part1=87語/Part2=92語(計179語)、B1はPart1=111語/Part2=78語
     (計189語)で、いずれもNo.4〜6の実績レンジに近い。前回の
     Part1=38語という極端な短さは、その回のPilot固有の生成結果
     (単発の外れ値)であり、Baseline自体の構造的な問題ではないと判断
  2. **B1本文→Comment 2接続の不自然さ**: 再現した。B1 Comment 2が
     「are some companies moving away from shared desks?」と問いかけた
     直後に、Full Story Part 2の冒頭が「Now, some employers are asking
     a different question: should every desk be shared?」と、ほぼ同じ
     論点を再度問いかけており、重複した疑問形の接続になっている
  3. **Key Phrase pause差**: 再現した。番号読み上げ→Key Phrase本体の
     実測間隔は、A2が約0.47秒、B1が約0.75秒(差約0.28秒)。原因は
     ER-008-N7-MIDDLE-SPEC-STORY-BALANCE-KEYPHRASE-AUDIT-01と同じ
     (B1側の数字読み上げ音声・Key Phrase英語Component音声の両方に
     元々の余白無音が多く残っている、既存の共有静的音声ファイル間の
     差異)
  Fact/Ledger Deviationは、A2=5件(MAJOR3件)・B1=1件(MAJOR1件)で、
  No.4〜6の実績レンジ(総数1〜6件、MAJOR0〜2件)からA2のMAJOR数が
  やや高いが、明確な逸脱とまでは言えない範囲だった
- **STOPして新規対策を入れなかった項目**: 2.(B1本文→Comment接続)と
  3.(Key Phrase pause差)はいずれもBaselineで再現することを確認した
  時点でSTOPし、新しい修正は入れていない(タスク仕様の指示通り)。
  今後、正式仕様として対応するかどうかは別途ユーザー判断とする
- **Middle仕様の扱い**: `DEFERRED / FUTURE_CANDIDATE`として
  OPEN_ITEMS.md OPEN-64に正式記録。基本方針(B1がベース、本文系のみA2、
  Key PhraseもA2版を使う[前回Decisionから方針変更]、将来再開時の
  必須検証項目8点)を記録した。Shared Point Blueprint実装自体は削除
  せず、Production未採用・オプトインのまま保持する
- **今回実施しなかったこと**: Middle版生成、Middle正式Level化、Shared
  Point Blueprint Production採用、Full Story soft minimum追加、Key
  Phrase pause新規統一、B1 Comment prompt修正、No.8生成、UI変更、
  Pricing変更
- **根拠レポート**: ER-008-N7-BASELINE-RESET-AND-MIDDLE-DEFER-01完了
  報告、OPEN_ITEMS.md OPEN-64、比較試聴Artifact(B1/A2のみ、
  https://claude.ai/code/artifact/de5ca386-8f04-470d-926b-edcb579a58d7)
- **影響するCURRENT_SPEC項目**: なし。今回はNo.7を既存の正式仕様へ
  戻しただけであり、CURRENT_SPEC自体への変更はない。B1本文→Comment
  接続とKey Phrase pause差は、Baseline自体に元からある挙動として
  確認されたが、対応方針はユーザー判断待ちのため仕様変更はしていない

## ER-008-N7-CONTENT-AUDIO-QA-02(2026-08-26)

- **Decision**: No.7正式Baselineのユーザー試聴で見つかった5点を調査し、
  影響がPilotに閉じない2件のバグ(共有ProductionコードのValidator gap、
  Key Phrase音声のstaleファイル使用)を修正した。No.7自体はB1 Key
  Phrase 2の音声/gloss修正、A2 Key Phrase pauseの+0.1秒変更(B1は無変更)
  を適用。Evidence Density(spoken layerでの固有名詞・数字の扱い)は
  Production Promptへ未配線と判明したが、大規模なPrompt再設計は行わず
  提案のみでSTOPした。読み上げ速度は今回測定のみで変更していない
- **Part A: B1 Key Phrase不整合のroot cause**: 表示上は"compare poorly
  with"/"〜より見劣りする..."で正しかったが、実音声は2つの独立したバグの
  複合で食い違っていた。(1) 日本語glossの"〜"(項変数記法、ER-006-KP5-
  CANONICAL-BUG-01の既存検出ロジックが意図通り検出)によりTTS生成が
  STOPPEDし、diskに残っていた前回実行(別のKey Phraseセット)の古い
  音声がassembly時にそのまま使われていた。(2) 英語Componentの実音声は
  "with"が脱落した"Compare poorly"だったが、ASR一致判定
  (`er006_preprod_hardening_01_validation.py::classify_asr_match`)の
  「冠詞等のstopwordを除いた内容語だけを比較する」近道処理が、意味を
  持つ前置詞"with"も冠詞と同列にstopword扱いしていたため誤って
  NORMALIZED_MATCH判定していた(Validator gap)。修正: glossを
  "他と比べて見劣りする／他より劣る"へ書き換え、対象のstopword集合を
  冠詞(a/an/the)のみへ絞り込み、kp2の英語/日本語を実際に再生成し
  (両方とも正しい内容をASRで再確認済み)、B1を再組み立てした
- **Part A: 一般整合性checkの追加**: `er003_v1_n3_01_assemble.py`の
  `load_b1_sources()`/`load_a2_sources()`へ`verify_key_phrase_audio_
  integrity()`を追加。assembly直前に、今回の実行のtts_generation_
  results.jsonで各Key Phraseの英語/日本語生成が実際にOK
  (またはASR_VALIDATION_UNCERTAIN)だったかを確認し、STOPPED等の失敗が
  あれば明示的なエラーで停止する(diskに残った古い音声を黙って使う
  ことを防ぐ)。診断ファイルを書かない旧テーマ・別pipelineには影響
  しない(後方互換)
- **Part B: A2 Key Phrase pause**: ユーザー決定により、A2の番号読み上げ
  →Key Phrase本体の間だけ0.4秒→0.5秒(+0.1秒)へ変更(B1は0.4秒のまま
  無変更)。`er003_b1_p9a_audio.py::build_key_phrase_block()`へ
  `numbering_pause_seconds`引数を追加(既定None=既存動作、後方互換)。
  実WAV計測(No.7 A2 5件平均): 修正前は約0.41〜0.47秒、修正後は
  約0.51〜0.57秒(いずれも数字→英語間の実測、無音区間+pause定数+
  trim後の頭無音の合計)。将来Middle再開時はA2のKey Phraseをそのまま
  使う仕様(下記Part C-2参照)のため、この値も自動的に継承される
- **Part C: A2 Point One見出しの発音問題**: Point見出しもASR全文検証の
  対象であることを確認(`generate_english_segment_with_fallback`経由)。
  元音声は標準経路(ENGLISH_STYLE_PREFIX)がGemini側の一時的な500エラー
  で6回とも失敗し、fallbackの"minimal instruction"経路で生成された
  ものだった。OpenAI Primary ASRは"A desk can feel like a place..."と
  正しく書き起こし(NORMALIZED_MATCHでPASS)たが、Azure Secondary ASR
  で同じ音声を再確認すると"A desk can feel LITHA."と全く異なる書き起こし
  になった。Secondary ASR cascadeはPrimaryがmismatchを返した場合のみ
  起動する設計のため、Primaryが(内容的には正しい語を)書き起こして
  しまうこの種の発音品質問題は、既存の検証フローでは検知できない
  (ASRでは検知困難な発音品質問題、Validator側のバグではなく構造的
  限界)。同じ経路で再生成した候補は、今回は標準経路が成功し、
  Primary/Secondary両方で完全一致の書き起こしを得た。試聴Artifactに
  原音声と候補を並べて掲載し、採用可否はユーザー判断とする(自動置換
  はしていない)
- **Part D-1: Evidence Compression Production配線状態**: `NOT_WIRED`。
  実際のProduction Writer Prompt(`er003_v1_n3_01_articles_generate.py`
  の`B1_B_DIRECT_INSTRUCTION`/`A2_KAI1_INSTRUCTION`/`build_common_
  block`)には、"Evidence Compression"や固有名詞・研究者名・企業名を
  spoken layerで削減する指示は一切存在しない。唯一近い規定は
  「Spoken-first原則(数字の扱い)」だが、これは「Fact Ledgerの数字を
  恣意的に削らない」ことを明示しており、むしろ逆方向の原則である。
  過去のNo.7 Full Story延長タスクで使った"Evidence Compression"という
  言葉は、その場限りの手動編集方針であり、正式なProduction仕様
  (CURRENT_SPEC.md)にも一切記載がない
- **Part D-2/D-3: No.7の固有名詞・数字監査**: Full Story+Point One/Two
  中の主な固有名詞(Scotiabank・iCapital Network・Bisnow・Gensler・
  Korn Ferry・CBRE)は、いずれも「その名前を聞くこと自体がStory理解を
  改善する」基準を満たさず`COMPRESS`(Bisnow・Bisnowのイベント名は
  さらに弱く`REMOVE_FROM_SPOKEN`)。一方、87%/74%・80%/67%(Point One)、
  20%/「パンデミック前の2倍」(B1 Part2)、56%/40%・2023/2024・
  2026(Point Two)は、比較の核心そのものであり`KEEP`。改善案(最小、
  未実装): Production Promptへ「固有名詞(企業・研究機関・出版物名)は、
  その名前自体がStory理解に必要でない限りspoken scriptへ出さず、
  『ある調査』『複数の企業』等の一般化表現に置き換える」という1文を
  追加する案を提示するに留め、実際のPrompt改修は行っていない
  (大規模なPrompt再設計は今回のスコープ外、ユーザー判断待ち)
- **Part E: 読み上げ速度実測**: TTS Prompt・API呼び出しのいずれにも
  話速指定は存在しないことを確認(`er002_common.py::assert_no_wpm_
  specification()`により数値WPM指定が混入しないことをbuild時に
  assertで保証済み、Gemini API呼び出しにも`speaking_rate`等のパラメータ
  は渡していない)。A2/B1でスタイル指示文自体は完全に同一(レベル間の
  速度差指定は無し)。実測(実発話区間ベース、無音除外): A2平均
  138.8WPM(中央値142.3、Story平均152.55、Point平均118.55)、B1平均
  151.4WPM(中央値152.1、Story平均148.6、Point平均124.05)。過去に
  言及した135WPM案等は、正式採用された仕様ではなく現状の実測基準
  として扱っていない。今回は速度変更を行っていない
- **今回実施しなかったこと**: Middle再開、No.8生成、A2/B1読み上げ速度
  変更、Full Story length rule追加、Research Coverage Gate再開、ASR
  provider変更、TTS model変更、Evidence Density Prompt改修の実装
- **根拠レポート**: ER-008-N7-CONTENT-AUDIO-QA-02完了報告、比較試聴
  Artifact(https://claude.ai/code/artifact/de5ca386-8f04-470d-926b-edcb579a58d7)
- **影響するCURRENT_SPEC項目**: なし。Key Phrase pauseの数値・Evidence
  Density方針・読み上げ速度はいずれも正式仕様化されておらず、今回も
  CURRENT_SPECへの追加は行っていない(pause変更は実装済みだがNo.7限定の
  検証、方針としての正式採用は別途判断)

## ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03(2026-08-26)

- **Decision**: 2テーマを独立に扱った。TTS fallback(minimal instruction
  fallback)は`INVESTIGATION`のまま、既存ログ解析中心で実態を調査し、
  対策案の提示に留めてProduction改修はしていない(詳細OPEN-66)。
  Evidence Compressionは、No.7を対象に実Writerでcandidate scriptを
  script-only(TTS/ASR無し)で実際に生成し、`VALIDATED_CANDIDATE /
  USER_REVIEW_REQUIRED`とした(詳細OPEN-65)。CURRENT_SPECのProduction
  Writer仕様・TTS標準経路のいずれも変更していない
- **TTS fallbackの主な発見**: (1) 導入経緯はcommit `a13d97c`
  (2026-08-08、ER-003-REPRO-01-MAIN、短い孤立フレーズでの
  hallucination対応)、CURRENT_SPEC.mdに`DECIDED`の正式仕様として記載
  済みだが、当時の受入条件は実質n=2のhallucination事例のみで、
  Gemini側の一時的障害(No.7のケース)は検証対象外だった。CURRENT_SPEC
  自身が「根本原因は未解明のまま」と明記している。(2) standardと
  fallbackの唯一の実質的な差はTTS instructionの文言で、fallbackは
  prosody・感情の起伏に関する指示を一切持たない1文のみ。(3) 過去ログ
  442 segment分析の結果、fallbackへ落ちるのは6.3%(28件)と稀だが、
  発動した場合の帰結はOK 25%・ASR_VALIDATION_UNCERTAIN 11%・
  **STOPPED(音声未生成)64%**であり、fallbackは「発動すればほぼ解決
  する安全網」ではない。(4) No.7の6連続失敗は全て同一のGemini
  `500 INTERNAL`エラーで、`LIKELY_PROVIDER_TRANSIENT`と判定できる
  runtime evidenceがある一方、過去ログ全体はtimeout・応答パース失敗も
  混在し`MIXED`。(5) 現行QAの弱点は、fallback経路のSecondary ASR
  cascadeがPrimary ASRの「entity-likeな不一致」でのみ起動する設計の
  ため、Primaryが見かけ上正しく書き起こしてしまう発音品質問題
  (No.7 point_one_heading)を検知できないこと。推奨(未実装)は
  Option 2「fallback発動時のみSecondary ASRを必須化」
- **Evidence Compressionの主な発見**: `er003_v1_n3_01_articles_
  generate.py::build_common_block()`へ`evidence_compression`引数
  (既定False、Production挙動は無変更)を追加し、No.7でcandidateを
  生成した。固有名詞(Scotiabank/iCapital Network/Bisnow/Gensler/
  Korn Ferry/CBRE)は全sectionで0件まで削減され、Point Oneの4つの
  比較%は1文の傾向表現へ圧縮、Point Twoの核心的な比較数値
  (56%/40%・2023/2024/2026)は維持された。Fact Check verdictは
  A2で変化なし、B1はREVIEW_REQUIRED→PASSへ改善した一方、**Ledger
  Deviationは B1でbaseline1件→candidate6件(新規MAJOR3件)と悪化**
  した。新規MAJOR逸脱には、元のcorrelational evidenceより踏み込んだ
  因果的表現("...because some offices are questioning the human
  cost of desk sharing")が含まれており、出典名を削っただけでなく
  主張自体がやや強まった可能性がある。これは「出典名を消しただけで
  Fact自体は安全」ではなく「Evidenceを削ったことで主張が強くなった」
  側に近い事例として明示的に記録し、Production採用の判断材料とする
- **今回実施しなかったこと**: TTS音声生成、A2速度変更、fallback
  Production改修、ASR Primary/Secondary入れ替え、Evidence
  Compression正式Production配線、Middle再開、No.8生成
- **根拠レポート**: ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03
  完了報告、OPEN-65・OPEN-66、比較Artifact
  (https://claude.ai/code/artifact/33775f4c-6acb-4bc5-ad0f-6ed0b9959a06)
- **影響するCURRENT_SPEC項目**: なし。`evidence_compression`引数は
  既定Falseで実装したのみで、Production Writer仕様(CURRENT_SPEC.md)
  への追加・変更はしていない。TTS fallbackの既存記載(244行目・263行目)
  も今回は変更していない(調査結果を踏まえた改修は別タスクでの判断)

## ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04(2026-08-26)

- **Decision**: ユーザー承認済みの暫定対策として、fallback(minimal
  instruction)経由で生成された英語音声にSecondary ASR確認を必須化する
  変更をProductionへ正式配線した(`PRODUCTION_WIRED`)。fallback自体の
  根本再設計は`DEFERRED / AFTER USER VALIDATION`としてOPEN-67へ切り
  出した。Evidence Compressionは、強化したFact safety制約のもとで
  方式B(Compression-aware Writer)・方式C(Lossless Editor)をNo.7で
  比較し、方式Cを推奨として`VALIDATED_CANDIDATE / USER_REVIEW_
  REQUIRED`のまま記録した。CURRENT_SPECのProduction Writer既定Prompt
  は変更していない
- **fallback発動条件の確定**: 実コードを追跡し、Gemini 5xx/timeout/
  応答異常はいずれも`_call_tts_with_retry`内の同一Exception捕捉で
  扱われ、技術retry(既定1回)を経てそのTTS試行1回分の失敗として
  outer loop(既定6回)で再試行されること、ASR content mismatch/
  hallucinationは`classify_asr_match`のTRUE_CONTENT_MISMATCH/
  TTS_FAILURE分類でretry対象になること、entity-likeな不一致のみが
  Cascade(Primary#2→Secondary#1→Secondary#2)の対象になることを確認
  した。「6回」は同一standard prompt・同一voiceでの6回独立したフレッシュ
  TTS生成試行を意味し(ASR retryの回数ではない)、`max_attempts: int = 6`
  が現在の唯一の設定値(topic単位のチューニング機構は無い)
- **重大な追加発見(Part B)**: TTS生成の各試行は、ASR内容検証の前に
  `write_wav_float()`で無条件に音声ファイルをdisk上書きしているため、
  standard/fallbackとも全試行が尽きて最終的に`STOPPED`となった場合
  でも、disk上には最後の(未検証・却下された)音声がそのまま残る。
  Assembly側はtts_generation_results.jsonのstatusを一切確認せず
  このファイルを読み込むため、**無人Production量産でfallbackも失敗
  した場合、自動的には停止せず、未検証の音声を含んだままエピソードが
  完成する**ことを、No.6 Deliveryの実例(手動再実行スクリプト
  `resume_audio_n6.py`実行後もSTOPPEDのままだが完成済みwavが存在する)
  で確認した。この一般的なリスクへの対策(Key Phrase以外の全segment
  への適用)は今回のスコープ外とし、OPEN-67の一部として記録した
- **Secondary ASR必須化の実装**: `er006_secondary_asr_01.py::
  evaluate_attempt_with_cascade`/`evaluate_attempt_with_cascade_
  detail`へ`force_secondary`引数(既定False)を追加。standard path
  (`er003_v1_repro01_main_generate.py`の`generate_narration_
  snippet_verified_strict`)は無変更・追加コストゼロ。fallback path
  2箇所(`generate_key_phrase_component_verified`の内部fallbackループ、
  `er003_v1_crosslevel_audio_02_common.py::generate_english_
  segment_with_fallback`のfallbackループ)へ`force_secondary=True`を
  配線し、PrimaryがPASSしてもSecondaryが同意しない限り自動PASSしない
  ようにした。5件の受入テスト(standard無影響/両ASR一致でPASS/
  Secondary不一致で自動PASS阻止/Primary不一致時の既存Cascade維持/
  No.7実event fixture)を[er006_secondary_asr_01_test.py](er006_secondary_asr_01_test.py)
  へ追加し全PASSを確認、CURRENT_SPEC.mdを更新した
- **Evidence Compression 3方式比較**: 前回(ER-008-TTS-FALLBACK-AND-
  EVIDENCE-COMPRESSION-03)発見したB1候補の因果表現drift対策として、
  `EVIDENCE_COMPRESSION_BLOCK`へFact safety不変条件(相関→因果への
  変換禁止・scope拡張禁止・hedging削除禁止等)を明示追加した。方式B
  (Writer再生成)と、新規実装した方式C(Lossless Editor、Baseline
  記事をそのまま渡し軽量編集のみ許可する新規opt-in経路、
  `er008_evidence_compression_ab_04.py`)をNo.7で比較した結果、両方式
  とも因果強化表現の新規混入は0件(drift再発なし)を確認した。方式C
  は固有名詞削減の安定性が高く(全section・両levelで0件を達成)、
  Ledger DeviationもBaseline水準に近く、A2はFact Check verdictが
  PASSへ改善した。方式Bは実行ごとのばらつきが大きく(この回はA2で
  固有名詞が一部残った)、B1のLedger Deviationが1件→6件へ悪化した。
  **推奨は方式C**とした
- **今回実施しなかったこと**: Evidence CompressionのProduction採用、
  Evidence Compression音声生成、A2速度変更、A2 Point One音声差し替え、
  A2 Key Phrase pause追加、Middle再開、No.8生成、Primary/Secondary
  Provider入れ替え(※A2 Key Phrase pause追加・Point One修正音声・A2
  slightly slower TTSは次の音声生成タスクで実施予定、Open Itemから
  落とさない)
- **根拠レポート**: ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-
  COMPRESSION-AB-04完了報告、OPEN-65・OPEN-66・OPEN-67、比較Artifact
  (https://claude.ai/code/artifact/29af88f0-2849-480b-830d-3381c556f812)
- **影響するCURRENT_SPEC項目**: minimal instruction fallback(244行目、
  Secondary ASR必須化を追記、`PRODUCTION_WIRED`)。Evidence Compression
  ・Production Writer既定Promptは今回も変更していない

## ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05(2026-08-26)

- **Decision**: ユーザー承認済み(`APPROVED_FOR_PRODUCTION`)のAudio
  Validation Gateを正式Productionへ配線した(`PRODUCTION_WIRED`)。
  未検証・stale・STOPPEDの音声がassemblyされる問題を、Key Phrase限定
  だった既存の仕組みを一般化して全segmentへ適用することで解消した。
  Evidence Compressionは、方式C(Lossless Editor)のB1で増えたLedger
  MAJOR逸脱1件ずつを精査し、いずれもBaselineの既存事項が重複計上
  されただけ(`VALIDATOR_FALSE_POSITIVE`)と判定した。引き続き
  `VALIDATED_CANDIDATE / USER_REVIEW_REQUIRED`のまま、Production
  採用はしていない
- **root cause**: 各TTS生成試行(`er003_b1_p9a_audio.py::generate_
  narration_snippet`他)はASR内容検証の前に`write_wav_float()`で
  無条件にファイルをdisk上書きするため、standard/fallbackとも全試行
  が失敗して最終`STOPPED`になっても、最後の(未検証・却下された)
  音声がそのままdiskに残る。Assembly側はファイルの存在だけで読み
  込んでいたため、QA未合格音声がProduction episodeへ混入しうる状態
  だった(No.6 Delivery・No.7 B1 Key Phrase 2で実例確認済み)
- **新仕様の設計**: 新しいmanifestファイルは作らず、既存の`tts_
  generation_results.json`(このrunの診断ファイル、既に全segment/Key
  Phraseの生成結果を含む)を正とする単一のgateへ統合した(重複実装を
  避ける)。各segmentをVALIDATED(status=OK)/HUMAN_APPROVED(ASR_
  VALIDATION_UNCERTAINだがcanonical_text一致の明示的承認記録あり)/
  UNVALIDATED/STOPPEDへ正規化し、`verify_episode_audio_validation_
  gate()`がassembly直前に全segmentを検査する。VALIDATED・HUMAN_
  APPROVED以外が1件でもあれば`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`
  としてRuntimeErrorを送出し、assembly全体を中止する。Human Review
  用に`record_human_approval()`(segment名+canonical_textのsha256+
  承認日時を記録、textが変わったら承認は無効)を新設した。ファイルの
  temp/atomic-rename分離(タスク仕様のPart C推奨設計)は、既存の
  tts_generation_results.jsonベースのgateだけで受入テスト9件全てを
  満たせることを確認できたため、大規模な生成関数リファクタリングは
  見送り、gateによる防御を主とした
- **受入テスト**: standard PASS/final STOPPEDでblock/retry途中status
  でblock/current run STOPPEDならstale音声があってもblock(No.7 Key
  Phrase実例の直接再現)/fallback Secondary不一致でblock/fallback
  両ASR一致でPASS/Human Approved後はPASS/text変更後は旧承認が無効/
  1segmentだけ未検証でepisode全体block/No.6実データfixtureでblock、
  の10件全てPASS([er008_audio_validation_gate_05_test.py](er008_audio_validation_gate_05_test.py))
- **重大な追加発見(Part H)**: 現行Production経路を持つ全12テーマ×2
  レベル=24組を実際に新Gateで検査した結果、**22組が最低1segmentで
  blocked状態**(pool_n4_supermarket/b1bとpool_n5_cafes/a2の2組のみ
  現状クリーン)であることが判明した。既に組み立て済みのepisode wav
  ファイル自体は無変更だが、今後これらのテーマを再assemblyしようと
  した場合、新Gateにより明示的にブロックされる。No.7自体もfull_
  story_part1・point_oneがHuman Approval記録の無いASR_VALIDATION_
  UNCERTAINのままのため、次回音声タスク(A2 pause追加・Point One
  差し替え等)で再assemblyする際は、該当segmentの再生成または明示
  承認が必要になる
- **Evidence Compression方式C MAJOR精査**: B1でBaseline(Ledger
  MAJOR1件)→方式C(MAJOR2件)へ増加した点を1件ずつ精査した結果、
  新たにMAJORとして挙げられた2文はいずれもBaselineから一字一句
  変更されていない(byte単位で同一)ことを確認した。CBRE調査(F-008/
  F-009)を「wider/broader office market」と一般化する、Baselineに
  元々あった同一のscope越境が、Deviation Checkerの実行ごとの引用の
  まとめ方が非決定的なために今回はより多くの独立レコードとして数え
  られただけと判定した(`VALIDATOR_FALSE_POSITIVE`)。方式C自体の
  Production候補評価は総合して肯定的(固有名詞削減・数字負荷削減・
  Fact loss/追加なし・causal driftなし・英語は概ね自然)。一方、
  "one report"のような出典主体を消した結果の曖昧な言い回しは改善
  余地として新規記録した(OPEN-69)
- **今回実施しなかったこと**: Evidence CompressionのProduction採用、
  fallback根本再設計の実装(論点整理[OPEN-67]のみ)、既存22テーマの
  一括是正、A2 Key Phrase pause追加・Point One音声差し替え・A2読み
  上げ速度調整(次回音声タスクへ引継ぎ、OPEN-70)
- **根拠レポート**: ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-
  AUDIT-05完了報告、OPEN-65・OPEN-67・OPEN-68・OPEN-69・OPEN-70
- **影響するCURRENT_SPEC項目**: Audio Validation Gateを新規項目として
  「QA / Human Review」節へ追加(`DECIDED`/`PRODUCTION_WIRED`)。
  Evidence Compression・Production Writer既定Promptは今回も無変更

## ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06(2026-08-26)

- **Decision**: Evidence Compression方式C(Lossless Editor)をユーザー
  が正式採用し、Production Writerパイプラインへ配線した(`APPROVED_
  FOR_PRODUCTION`→`PRODUCTION_WIRED`)。No.7 A2/B1を、この新Production
  経路(方式C+既存Audio Validation Gate)で実際に再生成し、`USER
  LISTENING READY`な完成候補音声とした。加えてA2のみ、(1) Key Phrase
  番号→phrase間のポーズをさらに+0.1秒(累計+0.2秒)、(2) Point One
  見出しの誤発音修正、(3) 自然言語による「わずかに遅く」ナレーション
  指示、の3点を配線した(B1・Key Phraseの速度は無変更)
- **方式Cの実装**: 新規`er003_v1_n3_01_evidence_compression_editor.py`
  に`run_lossless_editor()`を実装し、`er003_v1_n3_01_articles_
  generate.py::run_one_pattern()`内(Writer出力直後、Fact Check/
  Ledger Deviation Checkの前)へ組み込んだ(`apply_evidence_
  compression`引数、既定`True`)。Editorは「意味を保ったまま聴取負荷
  を下げる」工程に限定し、Fact追加/削除・相関→因果・確信度強化・
  hedging削除・scope拡張・比較/時間方向の変更・Point/Story構造変更を
  明示的に禁止するprompt設計とした(過去3回のAB/精査タスクで確立
  した不変条件リストを踏襲)。Method B(Compression-aware Writer、
  `evidence_compression`引数)は既定Falseのまま完全に別経路として
  維持した(混同防止のためdocstringへ明記)
- **Safety Gate運用**: No.7実データでのSafety Gate確認として、
  Writer出力直後の生原稿を`audit/pre_editor_article.md`へ保存し、
  Editor適用後に新規発生したLedger Deviationを1件ずつこの生原稿と
  突き合わせた。B1は8件中7件・A2は6件中大半がEditor適用前から存在
  する内容(Writer自身の一般化傾向)で、Editor起因の新規driftは
  「Korn Ferry says」→「One survey says」のような出典ラベルの言い
  換え(既知のOPEN-69と同種、軽微)に留まり、新規の意味的driftは
  確認されなかった
- **音声再生成での実運用確認**: 大規模音声生成中、A2 assemblyが
  `comment_4`の`STOPPED`によりAudio Validation Gateで実際に
  ブロックされた(便宜的なHuman Approvalでのバイパスは行わず、原因
  を精査)。原因は日本語ASRが正準テキストの漢数字「二つ」を常に
  算用数字「2つ」として書き起こす決定論的な不一致で、6標準+6
  fallback試行すべてが同一の`TRUE_CONTENT_MISMATCH`だった。
  `a2_support_texts.json`の該当テキストを実際のASR書き起こし表記
  (「2つ」)に合わせて修正し、該当segmentのみ再生成・ASR再検証
  (`asr_verified: True`)した上でGateを正当に通過させた
- **A2速度指示**: `er003_b1_p9a_audio.py`等4ファイルへ`style_prefix_
  override`引数を新設し、A2の対象5区分(Full Story Part1/2・Point
  One/Two・In One Line)へのみ`A2_ENGLISH_STYLE_PREFIX_SLOWER`
  (数値WPM/speed指定なし、既存の感情・自然さ指示は維持したまま追記)
  を適用した。fallback経路には適用しない設計とした。実測の結果、
  平均WPMは138.8→141.5とむしろ微増し、単体での明確な減速効果は
  確認できなかった。ただしMethod C適用+Writer新規生成でテキスト
  自体が旧baselineと完全に異なるため単純比較はできず、タスク仕様
  通り追加のprompt再調整はせずそのまま報告した(OPEN-32を訂正、
  過去の「135WPM」記述は未実装だった)
- **今回実施しなかったこと**: No.1〜6を含む既存22テーマへの方式C
  遡及適用・再生成(OPEN-68の方針通り、必要になったテーマのみ個別
  対応)、fallback根本再設計(OPEN-67、引き続き実ユーザー検証後まで
  凍結)、"one report"表現の改善(OPEN-69、LOW優先度のまま)、Support
  (Preview/Comment)への方式C効果の検証
- **根拠レポート**: ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06
  完了報告、OPEN-32・OPEN-65・OPEN-68・OPEN-69・OPEN-67、No.7完成
  候補Artifact(https://claude.ai/code/artifact/de5ca386-8f04-470d-
  926b-edcb579a58d7)
- **影響するCURRENT_SPEC項目**: 「Evidence Compression(方式C、
  Lossless Editor)」「A2 Key Phrase pause(番号→phrase間)」「A2英語
  ナレーション速度指示」の3行を新規追加(いずれも`DECIDED`/
  `PRODUCTION_WIRED`)

## ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07(2026-08-26)

- **Decision**: No.7 B1 Point Twoの"one desk per employee or fewer"を
  `FACT_ERROR`(CBRE調査の実際の方向と完全に逆)と判定し、"at least one
  desk per employee"へ修正した。同時に、A2 comment_4の「二つ」→「2つ」
  というASR都合のcanonical text書き換え(前タスクの暫定対応)を見直し、
  Validator側の限定的な同値正規化(助数詞「つ」直前の漢数字のみ)を
  実装した上で、canonical textを自然な表記「二つ」へ復元した
- **B1 Fact監査**: Evidence Pack(E-003-02)・Fact Ledger(F-008の`claim`
  欄)・Fact Ledger検証ノートは全て正しい方向("ratio of 1.0:1 or less"
  =従業員1人あたりデスク1台以上)を記録していたが、**VFL(F-008)自身の
  `conditions`欄**が、同じFactの`claim`欄と逆方向の言い換え("従業員1人
  につきデスク1台以下")になっていた。Writer出力の時点(Evidence
  Compression Editor適用前の`pre_editor_article.md`)で既に"or fewer"が
  存在しており、Editor由来ではなくWriter由来と判定した。同時に生成された
  A2側は同じF-008から独立に正しい"at least one desk per employee"を
  生成できていたため、単発のLLMサンプリング誤りであり、VFLの`conditions`
  欄の逆方向記述が誘因になった可能性が高いと判断した
- **Validatorが検知しなかった理由**: Fact Check(OpenAI web検索付き)は
  自らCBRE公式ページを検索・取得したが、検証ノート自体が記事と同じ
  逆方向の言い換え("従業員1人あたり1席以下の比率が…")をしてしまい、
  誤り同士が一致してすり抜けた。Ledger Deviation Checkはscope拡張・
  具体性追加型の逸脱検知を主眼としており、比較方向の反転そのものは
  対象にしていないため検知しなかった。既存の音声側Validator
  (`protected_check()`/`protected_check_ja()`)は「TTS音声がcanonical
  scriptと一致するか」の層であり、canonical script自体が誤っている
  ケースはそもそも対象範囲外であることを確認した(汎用的なscript対
  Source Fact比較方向Validatorは今回新設せず、OPEN-72として記録するに
  留めた。大規模Validator再設計は今回の非スコープ)
- **B1修正の反映**: `point_two` segmentのみ音声を再生成(NORMALIZED_MATCH、
  fallback不使用、初回試行でPASS)。Fact Checkを再実行し`REVIEW_REQUIRED`
  →`PASS`へ改善、Ledger Deviationを再実行し8件→6件(Point Two関連の
  新規逸脱なし、減少分はLLM実行ばらつきによるMINOR2件)。Audio
  Validation Gateを実PASSでB1/A2を再assemble(バイパスなし)
- **JA数字正規化**: `er007_ja_asr_validator_01.py`(長文用、31文字以上)
  ・`er003_audio_tts_asr_safety.py`(短いsegment用)双方に、助数詞「つ」
  の直前に来る単独漢数字(一〜九)だけを算用数字へ揃える限定的な同値
  正規化(`normalize_kanji_counter_numerals_ja()`)を実装した。「二十」
  「二回」等、助数詞「つ」が続かない漢数字は対象外のまま(既存の
  `_extract_numbers_ja()`/`protected_check_ja()`が単独漢数字を数字保護
  対象外としてきた設計思想[固有名詞的な語との誤判別リスク回避]を維持
  しつつ、助数詞という文脈が明確な場合のみ限定的に拡張した)。この
  過程で、OPEN-59が指摘していた「31文字以上のlong segmentは意味検証が
  構造的に発動しない」という`MATERIAL_VALIDATION_GAP`が、2026-08-25の
  ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01-WIRE-01で既に解消
  済み(全文diff方式の`classify_ja_asr_match()`がProduction配線済み)
  であることを、今回のNo.7実データ再生成で直接確認できたため、OPEN-59
  を`RESOLVED`へ更新した
- **今回実施しなかったこと**: VFL生成プロンプト自体への「`claim`と
  `conditions`の方向統一」指示追加(No.7個別修正のみ)、他テーマ(No.1〜
  6)への同種VFL方向不一致の横断監査、比較方向反転を検知する汎用
  Validatorの新設(OPEN-72として記録)、A2速度A/B(次タスクへ)
- **根拠レポート**: ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-
  NORMALIZATION-07完了報告、OPEN-59・OPEN-71・OPEN-72・OPEN-73
- **影響するCURRENT_SPEC項目**: 「Validator(日本語)」行へ助数詞「つ」
  数字正規化を追記(`DECIDED`)

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[CURRENT_SPEC.md](CURRENT_SPEC.md)、
[HISTORY_INDEX.md](HISTORY_INDEX.md)、[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)
