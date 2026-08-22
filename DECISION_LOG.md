# DECISION_LOG — 確定した意思決定の索引

**管理ID: ER-PM-001**
**最終更新: 2026-08-17(ER-003-B1-B2-SCOPE-FIX-01-R1、Residual SoT Cleanup)**

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

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[CURRENT_SPEC.md](CURRENT_SPEC.md)、
[HISTORY_INDEX.md](HISTORY_INDEX.md)、[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)
