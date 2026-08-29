# DECISION_LOG — 確定した意思決定の索引

**管理ID: ER-PM-001**
**最終更新: 2026-08-29(ER-008-N8-FINAL-CLOSEOUT-24、地名/施設名CompressionのNo.8正式反映・Writer Point Balance prompt強化・cost計算モジュールの単価バグ修正・Stephen Reicher発音PASS確定)**

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

## ER-008-DIRECTIONAL-FACT-PRECHECK-08(2026-08-26)

- **Decision**: 前タスク(ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-
  NORMALIZATION-07)で発見したB1 Point Two Fact誤り(more/fewer型の
  比較方向反転)を踏まえ、OPEN-72が指摘した「script対Source Factの
  比較方向を機械的に検知する汎用Validator」の本格実装は行わず、
  実ユーザー検証対象(当面No.7)向けの軽量・rule-based・新規LLM call
  なしの暫定チェックとして`er008_directional_fact_precheck_08.py`を
  実装し、Production記事生成経路(`run_one_pattern()`)へ既定Trueで
  配線した(`PRODUCTION_WIRED`、暫定策)。OPEN-72自体は削除せず
  `DEFERRED / AFTER USER VALIDATION`として維持する
- **設計**: Part B必須12カテゴリ(more/fewer、higher/lower、increase/
  decrease、rise/fall、up/down、at least/at most、above/below、
  before/after、earlier/later、more than/less than、doubled/halved、
  growth/decline)を、「magnitude(量の大小)」「temporal(時間の前後)」
  の2軸へ統合した。個別カテゴリを独立に対比するのではなく2軸へ統合
  することで、"increase"(Ledger側)と"rise"(script側)のような正しい
  同義表現を、カテゴリの違いを理由に誤って「比較不能」とせず正しく
  MATCH判定できる。各語には確度(high/low、2語以上のphraseや曖昧性の
  低い語はhigh、bare "up"/"down"等はlow)とカテゴリ(trend/threshold)
  を付与し、trend(increase/decrease等、同じ名前の量の時間変化)と
  threshold(at least/at most等、基準値との大小関係)を独立に評価する
  設計にした
- **重要な実データ発見(false negative、正直に記録)**: 実装直後、
  本タスクの発端となったNo.7 F-008(CBRE従業員・デスク比率)を実際の
  VFL/Fact Ledgerデータで検証したところ、Fact LedgerとscriptをNumber-
  anchorで自動対応付けするcross-artifact層(Ledger対script、VFLの
  `claim`対`conditions`欄)では、**誤りだった旧B1本文をMATCH、修正済み
  の正しい本文をPOTENTIAL_DIRECTION_REVERSALと判定し、正誤が完全に
  逆転する**ことを発見した。原因は、「比率」とその逆数に近い量(従業員
  1人あたりのデスク数)という、reciprocal(逆数)関係にある2つの主語を
  行き来するFactに対し、表層的な語("以下"等)の比較だけでは対象の
  違いを区別できないため。この発見を受け、trend/thresholdカテゴリを
  分離した上で、thresholdカテゴリのみの衝突はcross-artifact層で
  FAILへ格上げしない設計(`_downgrade_threshold_only_reversal()`)へ
  変更し、少なくとも「誤って正しい本文をブロックする」false positive
  は防いだ。ただし「誤った本文を見逃す」false negative(reciprocal-
  quantity型Factを検知できない)は解消しておらず、既知の限界として
  CURRENT_SPEC/OPEN-74へ明記した(隠さない)
- **Part G/H受入テスト**: `compare_direction()`単体(対象が明確な2文の
  直接比較)に対する23件のfixture(Part Hの10項目+trend/threshold
  分離の追加検証+No.7実データ回帰テスト)は全てPASS。No.7旧B1 Point
  Twoの誤り("one desk per employee or fewer")と正しいFact("at least
  one desk per employee")の直接比較は正しくPOTENTIAL_DIRECTION_
  REVERSALとして検知できる(対象=主語が明確な場合はrule-baseで確実に
  機能することの証明)
- **No.7実証**: No.7 B1/A2の実記事全体(article.md)に対して
  `audit_article_directional_facts()`を実行した結果、意図しない
  POTENTIAL_DIRECTION_REVERSAL(false positive)は0件、DIRECTION_
  REVIEW_REQUIRED(WARN)が3件(いずれも「片方にのみ方向表現がある」
  ケースで、実際の衝突ではない)。article生成の完成を誤ってブロック
  しない設計であることを実データで確認した
- **STOP条件の検討**: 「rule-basedでは安全に方向判定できない」に該当
  するか検討した結果、GENERAL(非reciprocal)な直接比較方向反転
  (Part G/Hの23件全て)については確実に機能するため全面STOPはせず、
  reciprocal-quantity型Factという**特定の狭いFactタイプに限定した
  既知の限界**として正直に報告する方針とした(Part D「false negative
  懸念」の報告項目で対応)
- **今回実施しなかったこと**: OPEN-72の本格対策(構造化comparator、
  VFL生成段階での方向保証、他テーマ横断監査)、`assert_no_directional_
  reversal()`gateの完成候補宣言プロセスへの明示的組み込み、A2速度A/B
  (次タスクへ)
- **根拠レポート**: ER-008-DIRECTIONAL-FACT-PRECHECK-08完了報告、
  OPEN-71・OPEN-72・OPEN-74
- **影響するCURRENT_SPEC項目**: 「QA / Human Review」節へ「Interim
  directional fact precheck for user-validation phase」行を新規追加
  (`DECIDED`/`PRODUCTION_WIRED`、暫定策と明記)

## ER-008-A2-SPEED-SAME-TEXT-ABC-09(2026-08-26)

- **Decision**: No.7 A2の英語ナレーション速度について、A(現行Production
  指示)・B(やや強めの減速指示)・C(Bよりもう一段強めの減速指示)を、
  Full Story Part 1のみ・本文/voice/model/segment境界を完全固定した
  same-text条件で比較生成した。**Production既定速度は今回変更しない**
  (前回タスクは記事本文自体がMethod C適用で変わっており、WPM比較として
  クリーンではなかったため、今回はその反省を踏まえた純粋比較のみを
  目的とした)。3候補ともstandard path・fallback不使用でASR PASSした
  が、**B・CともAより速い結果**(B: +11.2%、C: +2.0%)となり、意図した
  減速方向とは逆だった。採用可否はユーザーの試聴判断へ委ねる
- **same-text条件の担保**: 本文はNo.7 A2 `parts.json`のpart1と一字一句
  同一であることを直接diffで確認した。model(`gemini-2.5-pro-preview-
  tts`)・voice(`Aoede`)は`style_prefix_override`を通しても不変(コード
  上、これらはstyle_prefix_overrideの有無に関わらず固定値として渡され
  る設計であることを確認済み)。fallback回避は「fallbackへ自動遷移する
  ラッパー関数を呼ばず、standard path関数(`generate_narration_snippet_
  verified_strict`)を直接呼ぶ」という構造的な設計で保証した(事後
  チェックではなく、fallbackへ物理的に到達し得ない呼び出し経路)
- **実測結果**(active-speech WPM、word_count=70固定):
  A=142.22 WPM(30.01s/29.53s active)、B=158.19 WPM(27.16s/26.55s)、
  C=145.07 WPM(29.49s/28.95s)。3候補ともPrimary ASR一発PASS(A:
  NORMALIZED_MATCH、B・C: EXACT_MATCH、retry 0回)
- **STOP条件の該当判断**: タスク仕様Part Kの「Cでも速度差がほぼ出ない」
  に該当すると判断した(C はAよりむしろ2%速く、B は11%速い。意図した
  減速方向へは3候補とも動いていない)。ただし「same-text条件が崩れる」
  「fallback発動」「B/Cで不自然なprosodyが明らか」「A/B/C以外のProd
  仕様変更が必要」には該当しないため、実装・比較自体は完了させ、結果を
  正直に提示した上でユーザー判断を仰ぐ方針とした(勝手にB/Cを再調整
  したり追加trialを重ねたりはしていない、Part K「不要な再実行は禁止」)
- **Artifact**: A/B/C音声・WPM・instruction差分を並べた試聴比較ページを
  公開した(https://claude.ai/code/artifact/cc667002-0be4-4e02-a7df-
  82f744eee0c9)。Claude側からの推奨候補は提示していない(仕様書Part I
  「最終判断はユーザー」)
- **OPEN-72/OPEN-74確認(Part J)**: 実施前に状態を確認し、OPEN-72は
  `DEFERRED / AFTER USER VALIDATION`のまま(変更なし)、OPEN-74には
  「補助的警告機能であり、Fact方向の安全性を保証するものではない」
  という明記が不足していたため、OPEN_ITEMS.md/CURRENT_SPEC.mdへ追記
  した(コードは変更していない、ドキュメントのみ)
- **今回実施しなかったこと**: Production速度既定の変更、B/C以外の追加
  候補生成、Writer/Editor/Fact Checkの再実行、Full Story Part 1以外の
  segmentでのA/B/C比較(Part K「Full Story Part 1のみ3候補」に限定)
- **根拠レポート**: ER-008-A2-SPEED-SAME-TEXT-ABC-09完了報告、
  比較Artifact(上記URL)
- **影響するCURRENT_SPEC項目**: 「A2英語ナレーション速度指示」行は
  今回変更していない(Production既定は前タスクのA相当のまま)。
  「Interim directional fact precheck for user-validation phase」行へ
  「安全保証ではない」を明記(`DECIDED`のまま、内容のみ補強)

## ER-008-A2-TIMESTRETCH-ABC-10(2026-08-26)

- **Decision**: 前タスク(ER-008-A2-SPEED-SAME-TEXT-ABC-09)で自然言語の
  TTS速度指示がsame-text条件下でも安定して機能しなかった(B/CともA
  より速くなった)ことを受け、既存のNo.7 A2 Full Story Part 1完成音声
  (新規TTS生成なし)に対し、FFmpegの`atempo`フィルタ(pitch-preserving
  time-stretch)で3%/6%/9%の機械的な減速を適用し、0%(元音声)と
  合わせて4条件を比較した。**ステータスは`VALIDATION_ONLY`**、
  Production Audio Pipelineへは配線していない。採用可否はユーザーの
  試聴判断へ委ねる
- **手法**: `imageio-ffmpeg`パッケージが提供する静的FFmpegバイナリ
  (7.1、`--enable-librubberband`付きだが今回はRubber Bandではなく
  ffmpeg標準の`atempo`のみ使用、Part Iの「Rubber Band等は今回試さない」
  に準拠)を使用。単純なsample-rate変更(pitchが下がる)は明示的に
  使わず、`atempo=1/(1+slowdown/100)`で再生時間だけを伸ばした
- **実測結果**(word_count=70固定、active-speech WPM):
  A(0%)=147.7 WPM(28.89s)、B(3%目標)=143.5 WPM(実測減速2.96%、
  29.75s)、C(6%目標)=139.4 WPM(実測5.96%、30.61s)、D(9%目標)=
  135.6 WPM(実測8.95%、31.48s)。目標値と実測値の差は0.05〜0.04ポイント
  と極めて小さく、自然言語Promptより大幅に予測可能・制御可能である
  ことを確認した
- **pitch維持確認**: 追加依存を増やさないため、numpy/scipyのみで
  自己相関法による簡易F0(基本周波数)推定を実装した。元音声216.2Hz
  に対し、3/6/9%いずれも214.3Hz(-0.9%)で実質不変だった。単純な
  sample-rate変更であれば速度低下率とほぼ同じ割合(9%なら約8-9%)で
  pitchも下がるはずであり、これが起きなかったことが、genuinely
  pitch-preservingであることの直接的な証拠になる
- **内容・品質確認**: 4条件ともPrimary ASR(OpenAI)で`NORMALIZED_MATCH`
  となり、time-stretch処理による内容破損は確認されなかった。peak
  level(0.699〜0.700)・RMS(0.0723〜0.0738)・クリッピング検出(全て
  0サンプル)も4条件でほぼ同一であり、レベル面の異常は見られなかった。
  ただし「声がこもる」「金属的」「子音の不自然さ」等の主観的な音質
  劣化はASR/レベル測定では検知できないため、最終判断はユーザー試聴に
  委ねた(Part E自体がそう明記している)
- **Claudeからの提案**: 6%(C、約139 WPM)を、前タスクで参考範囲として
  挙がっていた135〜140 WPM帯に収まること・time-stretch比率が控えめで
  WSOLA系アルゴリズムの劣化リスクが小さいと見られることを根拠に、
  検討の出発点として提示した。ただし決定はしていない(Part G「最終
  決定はユーザー」)
- **Artifact**: 0/3/6/9%の4条件を並べた試聴比較ページを公開した
  (https://claude.ai/code/artifact/6efa0f4c-79a8-4d1e-a3ae-8c81d853a53d)。
  公開後、埋め込み音声4件が実際にpublishされたファイルへ正しく含まれて
  いることを直接検証した(前タスクでユーザーから「B/Cの音声が無いのでは」
  という指摘を受けたため、今回は公開前後の検証を徹底した)
- **今回実施しなかったこと**: Production Audio Pipelineへの配線
  (`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`化は次タスク以降、
  ユーザーが採用を決めた場合のみ)、Rubber Band等の別アルゴリズムでの
  比較、Full Story Part 1以外のsegmentへの適用、新規TTS再生成
- **根拠レポート**: ER-008-A2-TIMESTRETCH-ABC-10完了報告、OPEN-75、
  比較Artifact(上記URL)
- **影響するCURRENT_SPEC項目**: 「A2英語ナレーション速度(post-
  processing time-stretch案)」行を新規追加(`VALIDATION_ONLY`、
  Production未配線と明記)

## ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11(2026-08-26)

- **Decision**: ER-008-A2-TIMESTRETCH-ABC-10でユーザーが試聴の上6%
  time-stretchを正式採用したことを受け、Production A2音声パイプライン
  へ配線した(`APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`)。新規
  `er008_a2_postprocess_slowdown_01.py`(FFmpeg `atempo`、既定6%)を
  作成し、`er003_v1_n3_01_tts_generate.py::generate_a2_segments()`の
  A2英語7segment(point_one_heading/point_two_heading/full_story_
  part1/full_story_part2/point_one/point_two/in_one_line)全てへ配線
  した
- **既存instructionとの関係(重要な設計判断)**: 実装の途中で、既存の
  自然言語「わずかに遅く」instruction(`A2_ENGLISH_STYLE_PREFIX_
  SLOWER`)を6% time-stretchへの置き換えとして除去しようとしたが、
  これは誤りだったため撤回した。ユーザーが実際に試聴・承認した音声
  (ER-008-A2-TIMESTRETCH-ABC-10)は「既存のinstructionで生成された
  現行Production音声」に6% time-stretchを重ねたものであり、
  instructionを除去した音声ではない。instruction単体の効果がsame-
  text比較(ABC-09)で不安定だったことは、instructionを外してよい
  理由にはならない(ユーザーが承認したのはinstruction込みの組み合わせ)。
  この誤りは、trim_info不整合のバグ修正作業中に自分自身の実装ログを
  見直す過程で発見し、ユーザーへの追加確認なしに撤回・修正した
  (承認された仕様の逸脱であり、単純な実装バグと同種の扱いとした)
- **trim_infoの不整合修正**: post-process(time-stretch)適用後も
  `tts_generation_results.json`の`trim_info`/`duration_seconds`が
  slowdown適用前の値のままになっていた(実際の最終音声ファイルとの
  食い違い)ことに気付き、time-stretch比率で比例配分して実際の長さと
  一致させる修正を`apply_a2_slowdown_postprocess()`へ組み込んだ
- **post-process後ASR再検証とretry機構**: post-process後の音声を
  実際にASRで再検証する設計にした結果、No.7実データでの初回実行時に
  2/7 segment(`point_one`・`in_one_line`)で、slowdown**前**は正しく
  ASR一致していたのに、slowdown**後**の音声だけがASR不一致になる
  事象を発見した(語尾の単数/複数混同、文脈的な近縁語への誤認識等)。
  これはtime-stretchが内容そのものを変えたのではなく、微妙なタイミング
  変化がASRの認識精度をわずかに下げることがあるためと考えられる。
  既存の「未検証音声を黙ってPASSさせない」という方針を踏まえ、
  post-process後の再検証が不一致の場合は通常ペースから取り直す
  (最大3回)retry機構を`generate_a2_segment_with_slowdown()`へ追加
  した。No.7本番データへ適用した結果、初回不一致だった`point_one`は
  1回のretryで解消し、最終的に7segment全てがstatus=OKとなった
- **No.7実データへの反映**: 7segment全てを実際にこの新経路で再生成し、
  実測減速率5.5〜6.0%(目標6%に近い)を確認、Audio Validation Gateを
  実PASSでA2を再assemble(325.905秒)した。B1は完全に無変更のまま
- **今回実施しなかったこと**: 他21テーマ(No.1〜6含む)への遡及適用
  (必要になった時点で個別対応する既存方針[OPEN-68]を踏襲)、Middle
  再開(現状DEFERREDのまま)、"_original.wav"の実際の再利用先の実装
  (仕組みとしては用意したが、Middle自体が動いていないため未使用)
- **根拠レポート**: ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11完了報告、
  OPEN-75・OPEN-76
- **影響するCURRENT_SPEC項目**: 「A2英語ナレーション速度(post-
  processing time-stretch)」行を`VALIDATION_ONLY`→`DECIDED`
  (`PRODUCTION_WIRED`)へ更新

## ER-009-JA-FOREIGN-TOKEN-GATE-01(2026-08-26)

- **Decision**: Pool Topic No.4(pool_n4_supermarket)を最新のA2 6%
  slowdown/Audio Validation Gate仕様へ揃える作業中、A2 comment_2が
  ASR_VALIDATION_UNCERTAIN(Human Review待ち)のままGateをブロックして
  いることが判明した。ユーザーが実際に音声を試聴し、原因を確認した上で
  台本(comment_2)を修正・再生成することを承認し、あわせて同種の問題を
  今後検出する仕組み(4分類ゲート)の新規実装を指示した。両方を実施し、
  検出ロジックを`er003_audio_tts_asr_safety.py`(既存のTTS/ASR共通安全
  部品モジュール)へ新設・Production配線した(`PRODUCTION_WIRED`)
- **root cause**: A2 comment_2のJapanese canonical textに、制作内部の
  章番号ラベル「Part 1」がリスナー向け日本語のまま残っていた
  ("Part 1では、店が売り場の配置を変え…")。TTS自体は正しく「パート1」
  と発話していたが、Japanese ASR(Primary OpenAI×2・Secondary Azure×2
  の4段Cascade全て)は文中の英字表記をローマ字のまま書き起こすことが
  ほぼ無いため、canonical text側の「Part 1」とASR書き起こし「パート1」
  が構造的に一致し得ず、旧STOPPED時12回+今回2回の計14回の試行全てで
  Human Review待ちへ回っていた。音声自体は正しく発話されており、
  ASR/TTS側の技術的不具合ではなく、「制作都合の内部ラベルをリスナー
  向け日本語にそのまま残した」という編集上の問題だったと判定した
- **台本修正**: comment_2を「物語の前半では、店が売り場の配置を変え、
  買い物客が最初に見る商品を変えたことを聞きました。では、その後、
  商品の売れ方はどう変わったのでしょうか。」へ修正した(「Part 1」を
  「物語の前半」へ言い換え、他の意味・情報・Fact内容は一切変更して
  いない)。B1(`b1_support_texts.json`)は同種の内部ラベル漏れが無い
  ことを確認済み(B1 Comment/Previewは日本語ではなくeasy Englishの
  ため、そもそも対象外)。A2側の他のJapanese文言(preview/comment_1・
  3・4/japanese_title/Key Phrase gloss5件)も同じ観点で確認し、他に
  内部ラベルは見つからなかった
- **新設ゲートの設計**: `classify_foreign_tokens_in_japanese_text()`
  (rule-based、新規LLM呼び出しなし、OPEN-72/ER-008-DIRECTIONAL-FACT-
  PRECHECK-08と同じ「確信が持てない場合は無理に自動判定しない」思想を
  踏襲)を新設した。日本語canonical text中の英字・数字混じりのトークン
  を、TTSへ渡す前に4分類へ振り分ける:
  (1) `NEEDS_JAPANESE_PARAPHRASE` — 「Part 1」「Point 2」等の制作内部
  segment名・章番号ラベル(ASCII英数字の前後だけを見るnegative
  lookaroundで検出、Python re のUnicode `\b`が漢字/かなも「単語文字」と
  みなす既知の落とし穴を回避)
  (2) `READING_DICTIONARY` — `DEFAULT_JA_READING_DICTIONARY`(小規模な
  組み込み辞書)に登録済みの定着した略語・固有名詞
  (3) `ENGLISH_PRONUNCIATION` — 呼び出し側が渡した`known_key_phrase_
  terms`(その記事のKey Phrase英語表現[used_form])そのものが含まれる
  箇所。渡さない場合はこの分類は行われない
  (4) `HUMAN_REVIEW` — 上記いずれにも機械的な確信を持って分類できない
  もの。既存のASR Cascade human_review_queue.jsonlと同じ思想で、
  `er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl`へ
  明示的にレビュー待ちとして記録する
  過検知でProduction全体を止めないため、TTS呼び出し自体をブロックする
  のはカテゴリ4のみに限定した(既存の`detect_gloss_placeholder_
  notation()`と同じ「ブロック対象は確信が持てるケースに限定する」設計)。
  カテゴリ1〜3は検出・記録に留め、生成そのものは止めない
- **配線**: `er003_v1_n3_01_tts_generate.py`の日本語TTS入口2箇所
  (B1: `generate_charon_japanese_with_reading_safety()`、A2:
  `generate_a2_japanese_with_reading_safety()`)の先頭、既存の
  `detect_gloss_placeholder_notation()`チェックの直後へ追加した。A2側は
  `generate_a2_japanese_with_fallback()`(標準+minimal instruction
  fallbackの両方を内包)を呼び出す前の1箇所でチェックするため、2つの
  経路を重複実装なしでカバーできる。既存のKey Phrase日本語gloss呼び出し
  (B1 kp_ja_charon・A2 meaning_N、いずれも`generate_a2_segments()`/
  `generate_b1_segments()`内)は、新設した`known_key_phrase_terms`
  引数へ`[used_form]`を渡すよう更新し、Key Phrase自身の英語表現が
  gloss中に現れてもHUMAN_REVIEWへ誤って回らないようにした
- **受入テスト**: `er009_ja_foreign_token_gate_01_test_01.py`(13件、
  全PASS)。No.4実例("Part 1"検出→NEEDS_JAPANESE_PARAPHRASE・修正後は
  検出0件)、Point/Comment/Section/Step等のラベル変種、読み方辞書
  ヒット(Wi-Fi)、Key Phrase表現の意図的な英語発話判定(渡す/渡さない
  両ケース)、未知の外来語トークンのHUMAN_REVIEW判定、既存の助数詞・
  年号・漢数字パターンでの誤検知が無いこと(OPEN-73実例を含む)、No.4
  A2の他の全Japanese文言での誤検知が無いこと、B1/A2の日本語TTS入口が
  HUMAN_REVIEW時に実際のTTS呼び出し前でSTOPPEDになることを確認した
- **No.4実データへの適用**: 新設ゲートをNo.4 A2の全Japanese文言
  (preview/comment_1〜4/japanese_title/Key Phrase gloss5件、計10件)へ
  実行した結果、修正前はcomment_2の「Part 1」1件のみNEEDS_JAPANESE_
  PARAPHRASEとして検出され、他9件は検出0件だった。comment_2修正後は
  全10件で検出0件を確認した。修正後のcomment_2を実際に再生成した結果、
  Primary ASRで一発一致(fallback不使用、`status=OK`)を確認し、A2の
  全14 segmentがVALIDATED状態になったことを確認した上でAudio
  Validation Gateを実PASSし、A2を再assemble(376.741秒、clipping無し)
  した。B1(b1b)は無変更のままGate実PASSを再確認した
- **既存回帰テストへの影響**: `run_project_regression.py`実行時、
  `er003_test_p2j_investigate.py::CollectionCountTests::test_combined_
  equals_sum_of_er002_and_er003`が1件failした(`1820 != 1757`)。原因を
  切り分けたところ、本タスクの新規テストファイルを一時的に取り除いても
  同じ失敗(`1807 != 1757`)が再現することを確認しており、**本タスクが
  作った新規の退行ではなく、er007/er008系テストファイルが`er0XX_test_
  *.py`(prefix直後に`_test_`が続く命名)ではなく`er0XX_<説明>_test_
  NN.py`という別の命名規則を使うようになった時点から既に存在していた
  当該meta-test(prefix別再集計ロジック)側の前提崩れ**と判定した。この
  1件を除く1819件は全てPASS。本件は今回のスコープ外として着手せず、
  Open Item化した(下記OPEN-77)
- **今回実施しなかったこと**: 既存22テーマ全体への遡及適用(No.4以外は
  未確認、OPEN-68の既存方針に準拠し必要になった時点で個別対応)、
  `test_combined_equals_sum_of_er002_and_er003`自体の修正(pre-existing
  かつ本タスクのスコープ外と判断、Open Item化のみ)
- **根拠レポート**: ER-009-JA-FOREIGN-TOKEN-GATE-01完了報告、OPEN-77
- **影響するCURRENT_SPEC項目**: Cross-level仕様節へ「日本語解説・
  Comment文での制作内部ラベル禁止」を新規追加(`DECIDED`)。QA/Human
  Review節へ「日本語canonical textの外来語/制作内部ラベル検出(4分類
  ゲート)」を新規追加(`DECIDED`、`PRODUCTION_WIRED`)

## ER-010-ENTITY-PHONETIC-CORROBORATION-01 / ER-010-DATE-SPOKEN-FORM-POINT-FIX-01(2026-08-27)

- **Decision**: No.5(pool_n5_cafes)B1の未解決2件(comment_4の意味
  不整合、full_story_part1/2のSTOPPED)を解消した。(1) comment_4を
  「方針の明確さ」テーマへ言い換え・再生成(OPEN-63対応)。(2) 固有
  名詞ASR表記揺れの軽量音韻類似度チェック(entity phonetic
  corroboration)を新規実装しfull_story_part1を解決。(3) 日付の
  TTS誤読(full_story_part2)をpoint fixで解決し、副産物として発見した
  複合序数正規化バグも修正した
- **comment_4修正**: 「customers who work there may offer the café
  more than their payment」(B1自身のpoint_two_bodyを要約した文だが、
  A2 Point Two・B1自身のIn One Lineが共に「方針の明確さ」テーマで
  締めており、この論点をどちらも引き継いでいなかった。OPEN-63で
  既に指摘済み)を、「how clearly a café sets its policy can shape
  whether both workers and social customers feel welcome」へ言い換えた
  (point_two_body・in_one_line・A2側は無変更)。再生成・ASR再検証で
  `status=OK`を確認
- **full_story_part1のroot cause**: 研究者名"L. Mimoun and A. Gruen"
  が英語ASRにとって馴染みの薄い固有名詞であり、現行Production Cascade
  (`news_tail_fix.generate_news_narration_wide_margin`、Secondary ASR
  Cascade込み)で正規の手順により再生成しても、`classify_asr_match()`
  の既存entity_only_diffs判定(固有名詞らしき語のみの音訳差は
  retryしても改善しないと判断してASR_VALIDATION_UNCERTAINへ)により
  Human Review行きになっていた。既存ロジックには「retryを止める」
  設計はあったが「自動PASSさせる」設計は無かった
- **調査した対策(a): reactive発音資料調査**: 全記事・全固有名詞への
  一律research工程は追加しないという方針のもと、実際に問題になった
  "L. Mimoun and A. Gruen"についてのみ一度だけWeb検索を行い、実在の
  著者名が"Laetitia Mimoun"・"Adèle Gruen"(2021年、Journal of Service
  Research)であることを確認したが、信頼できる発音資料(音声・IPA表記等)
  は見つからなかった。台本の"L. Mimoun and A. Gruen"という表記自体は
  変更しなかった(スコープ外の台本変更を避けるため)
- **採用した対策(b): 軽量音韻類似度チェック**: `er006_preprod_
  hardening_01_validation.py`へ`soundex_en()`(標準的なSoundex
  アルゴリズム、pure Python、新規外部依存なし)と
  `aggregate_entity_only_phonetic_corroboration()`を新設した。複数の
  独立したTTS take(同一canonical_textに対する別々の生成、同じ音声の
  複数回文字起こしではない)で観測されたentity_only_diffsのASR書き
  起こし候補を集約し、canonical綴りとの音韻類似度(soundex一致+文字列
  類似度+文字数差+語頭一致)で「同一固有名詞の表記揺れ」と判定できる
  場合のみ`ASR_VALIDATION_UNCERTAIN_PHONETIC_ACCEPTED`として自動採用
  する。保守的側に倒す設計(既存protected_check思想[数字/否定/内容語は
  絶対に見逃さない]を壊さないため):
  (1) 数字・否定・非固有名詞内容語の差を含むtakeは、そのtake単体を
  判断材料から除外するのみに留める(全体を一括拒否しない。実データで、
  1回のtakeに無関係な内容語差が混入していた場合でも、他の独立した
  takeの証拠は引き続き使えることを確認した)
  (2) 同じ誤認識が複数回**繰り返し**観測される場合(多様性の裏付けが
  無い)は自動PASSしない。"Robert"→"Rupert"のような、soundexが一致し
  文字列類似度も高いが実在する無関係な別人名への置き換わりを、単発の
  判定だけでは区別できないことを検証で確認したため、この多様性要件で
  緩和した
  (3) 単発観測(裏付け無し)は、複数回観測(多様性の裏付けあり)より
  厳しい閾値(文字列類似度0.75以上・文字数差1以内)を要求する
  (4) canonical/ASR両方の語数が一致する候補のみを判定対象にする。
  実データで、頭文字("L.")がASR側の書き起こしで直後の固有名詞と融合
  し("L. Mimoun"→"Elmi Moon")、difflibのspan境界が試行ごとに揺れる
  ことを発見したため、短い頭文字トークンを除いたgrouping keyで同一
  固有名詞の証拠をまとめ、語数が対応しない候補は「判定不能」として
  除外する(反証にも証拠にもしない)設計にした
- **配線**: `er003_v1_sing01_news_tail_fix.py::generate_news_narration_
  wide_margin()`(B1 Full Story等の長尺英語News本文生成)へ配線した。
  entity-only mismatchの場合、既存のmax_attempts(6)上限内でretryを
  継続し複数takeの証拠を集められるようにした(既存の「同一signature
  连続で打ち切り」ロジックには影響しない、コスト上限は拡張していない)
- **known limitation(正直に記録)**: soundexベースの軽量チェックは、
  実在する別名同士の完全な区別を理論上保証しない(上記(2)の多様性
  要件で緩和しているが、原理的に完全ではない)。本チェックはretry・
  Human Review滞留を減らすための補助的最適化であり、既存の必須プロセス
  (最終的なユーザー試聴)がこの限界に対する最終的な安全網であり続ける
- **full_story_part2のroot cause確定**: `tts_safe_news_en()`(A2/B1
  共通のTTS入力正規化)・`build_tts_prompt()`・Gemini Batch API呼び出し
  経路のコードを実際に追跡し、"April 28, 2026"が一切変換されずTTSへ
  渡っていることを確認した(前処理バグではない)。旧B1本文(digit表記
  "April 28")・新表記("April twenty eighth")のいずれでも、12回中
  多くの試行で"26"という一貫した誤読が観測され(新表記では6回中4回が
  誤読、2回が正読)、ユーザー自身も実際に音声を聴取し「26に聞こえる」
  ことを確認済みであることから、genuine TTS mispronunciationと結論した
- **point fix**: `b1b/parts.json`(part2)・`b1b/article.md`の該当箇所
  を"on April 28, 2026,"→"on April twenty eighth, 2026,"へ変更した
  (事実・意味は無変更)。ユーザー提示の具体例"twenty-eighth, twenty
  twenty-six"は、既存の`tts_safe_number_words_en()`(A2専用、ハイフン
  複合数詞をOPEN-58と同じパターンで誤変換する)を実際に通してみたところ
  "twenty-6"に壊れることを確認したため、ハイフンを使わない
  "twenty eighth"へ変更し、年号は元々問題が無かった("2026"は12回全て
  で正しく認識されていた)ため桁のまま残す形へ変更した(ユーザー提示の
  具体例をそのまま採用せず、必要な範囲だけ安全な形へ調整した)
- **副産物として発見した複合序数正規化バグ**: 上記の再生成で、6回中
  2回(attempt1・6)が実際には正しく"28th"と発話されていたにも関わらず
  TRUE_CONTENT_MISMATCHと誤判定されていることを発見した。原因は
  `normalize_text()`の数値正規化パイプラインが、"twenty eighth"を
  1つの複合序数として扱えず、独立したcardinal変換ステップが"twenty"を
  "20"へ、独立したordinal変換ステップが"eighth"を"8th"へそれぞれ別々に
  変換し、"20 8th"という無関係な2トークンへ分裂させていたことだった。
  OPEN-58と同じ教訓(共有regexへの機械的な追加は事故を招きやすい)を
  踏まえ、「十の位の単語+一の位の序数語」という閉じた具体的パターン
  のみを対象にした専用ステップ`_convert_compound_ordinal_words()`を、
  既存のcardinal/ordinal変換より先に実行する形で追加した(スペース・
  ハイフン両方の区切りに対応)。バグ修正後、attempt6(既に実際に生成
  済みの音声、新規API呼び出し無し)を再判定した結果、実際に`NORMALIZED_
  MATCH`(should_pass=True)になることを確認し、その音声をそのまま
  status=OKとして採用した(音声ファイルは無変更、判定記録のみ訂正)
- **再発防止策の検討と不採用**: 「重要な日付・数字をTTS入力へ渡す前に
  検出しHuman Review相当のフラグを立てる軽量チェック」を検討したが、
  今回は実装を見送った(OPEN-78として記録)。理由: 発生条件(なぜこの
  特定の日付表現でTTSが誤読するのか)が未解明のまま汎用検出ルールを
  設計すると過検知/過剰実装のリスクが高く、今回の個別事象はpoint fix
  で解決済みのため緊急性が低いと判断した
- **受入テスト**: `er010_entity_phonetic_corroboration_01_test_01.py`
  (22件、全PASS)。No.5実データ(Mimoun/Gruen/Ralf Rüller、頭文字融合
  ノイズ、Robert/Rupert型の拒否確認、複合序数の各パターン)を含む
- **No.5実データへの適用**: comment_4修正・再生成、full_story_part1を
  新設した音韻類似度チェック経由で2回の試行で解決(実際にこの経路で
  解決)、full_story_part2をバグ修正後の再判定で解決(新規TTS/ASR
  呼び出し無し)。B1の全14 segmentがVALIDATEDとなり、Audio Validation
  Gateを実PASSしB1を再assemble(366.774秒、clipping無し)した。A2は
  無変更のままGate実PASSを再確認した。既存回帰テストは1841/1842 PASS
  (残り1件はOPEN-77、本タスクと無関係のpre-existing test bug)
- **今回実施しなかったこと**: 全記事・全固有名詞への一律発音資料調査
  research工程の追加(コスト増回避、reactiveな個別対応のみ)、重要な
  日付・数字の一般的なTTS入力前検出ゲートの実装(OPEN-78、Deferred)
- **根拠レポート**: ER-010-ENTITY-PHONETIC-CORROBORATION-01/ER-010-
  DATE-SPOKEN-FORM-POINT-FIX-01完了報告、OPEN-63(解消)・OPEN-78(新設)
- **影響するCURRENT_SPEC項目**: QA/Human Review節へ「英語固有名詞ASR
  表記揺れの軽量音韻類似度チェック」「複合序数の正規化バグ修正」
  「重要な日付・数字のTTS入力前チェック(検討したが今回は不採用)」の
  3項目を新規追加

## ER-011-HUMAN-REVIEW-COST-GUARD-01(2026-08-27)

- **Decision**: No.5(pool_n5_cafes)のB1修正作業中に発生した異常な
  API消費事故を受け、Human Review Queueへ到達した(または繰り返し
  STOPPEDになった)segmentへの機械的な再生成を、明示的な承認が無い
  限りAPIレベルでブロックするReview Lock機構を新設し、Production
  経路(英語側・日本語側の両方)へ正式配線した(`APPROVED_FOR_
  PRODUCTION`→`PRODUCTION_WIRED`)
- **root cause(監査で判明、2026-08-27深夜)**: `er009_pool_n5_b1_
  fix_01.py`(No.5 full_story_part1/2の修正用に前タスクで作成した
  薄い呼び出しスクリプト)を、full_story_part1がASR_VALIDATION_
  UNCERTAIN(Human Review相当)・full_story_part2がSTOPPEDのまま
  何度も手動再実行してしまい、full_story_part1でTTS 18回・ASR
  59回、full_story_part2でTTS 12回という異常なAPI消費が発生した。
  根本原因は2つ: (1) 呼び出し側スクリプトが`results["segments"]
  [name] = r`で毎回結果を無条件に上書きし、過去の試行履歴・Human
  Review到達状態を一切引き継がない設計だったこと、(2) Human Review
  Queue(英語側`er006_output/audio_retry_cascade_prod_01/human_
  review_queue.jsonl`、日本語側`er007_output/ja_asr_cascade_01/
  human_review_queue.jsonl`)へ到達した後も、それを検知して新規
  TTS/ASR呼び出しをブロックする仕組みがProduction経路のどこにも
  存在しなかったこと
- **設計(Part C: Review Lock状態)**: `er011_human_review_lock_01.py`
  を新設し、narration wavパス(".../<theme>/<level>/narration/
  <segment>.wav")から`(theme_id, level, segment_id)`を機械的に
  導出するキー(`derive_segment_key()`)で、segment単位のlock状態
  (`AUTO_PROCESSING`/`HUMAN_REVIEW_REQUIRED`/`HUMAN_APPROVED`/
  `REGENERATE_APPROVED`/`RESOLVED`)を`{level_out_dir}/audit/
  review_lock_state.json`(既存のtts_generation_results.json・
  human_approved_segments.jsonと同じ置き場所の思想)で管理する。
  既存の関数シグネチャ(`text, out_path, ...`)を一切変更せず、
  out_pathから逆算する設計にしたことで、呼び出し元コードへの侵襲を
  最小化した。`HUMAN_APPROVED`判定は、新規の並行実装を避けるため
  既存の`record_human_approval()`(`er003_v1_n3_01_assemble.py`)を
  そのまま流用する
- **Part D(明示的解除)**: `approve_regenerate()`は対話的オペレー
  ター操作でのみ呼ぶことを想定した独立APIとし、通常のTTS生成経路
  からは絶対に到達しない設計にした。`REGENERATE_APPROVED`は次の
  1回の呼び出しだけで自動的に消費され(結果に応じて`RESOLVED`または
  `HUMAN_REVIEW_REQUIRED`へ遷移)、「同じスクリプトをもう一度実行
  しただけ」では再解除されないことを受入テストで確認した。台本
  (text)が変わった場合はSHA256ハッシュの不一致により自動的に新しい
  バージョンとして扱われ、過去のlockは無効になる(既存の
  `record_human_approval()`のtext変更時無効化と同じ設計思想)
- **Part E(attempt history)**: 既存のtts_generation_results.json
  (segment単位で上書きされる正)は一切変更せず、別ファイル
  (`er011_output/attempt_history.jsonl`)へ追記型で記録する。
  theme/level/segment/run_id/timestamp/TTS試行数/ASR呼び出し数/
  累積値/Human Review到達有無/最終lock状態/所要時間を1呼び出し
  あたり1行で記録する
- **Part F(budget guard)**: 既存のTTS retry上限(max_attempts=
  6〜8)を踏まえ、累積TTS試行数上限15・累積ASR呼び出し数上限60を
  第二防衛線として設定した(第一防衛線はHUMAN_REVIEW_REQUIRED
  到達時点での即時ブロック、高い閾値で形骸化させないよう実際の
  事故[TTS18回/ASR59回]より確実に低い値にした)。`REGENERATE_
  APPROVED`中であっても、この上限を超えた場合は強制的に
  `HUMAN_REVIEW_REQUIRED`へ固定する
- **Part G(queue重複防止)**: 英語・日本語両方の`_log_human_review()`
  (`er006_secondary_asr_01.py`/`er007_ja_secondary_asr_01.py`)へ
  `is_duplicate_queue_entry()`チェックを追加し、同一wav_path・同一
  canonical_textのentryが既に存在する場合は新規追記しないようにした
- **配線(Part J、英語側・日本語側両方)**: `guarded_generate(language)`
  デコレータ(`(text, out_path, *args, **kwargs)`シグネチャ用)・
  `guarded_generate_with_language_arg`デコレータ(`(text, language,
  out_path, ...)`シグネチャ用、en/ja両方を1つの関数で扱う
  `generate_narration_snippet_verified_strict`向け)を実装し、以下へ
  適用した: 英語側`er003_v1_sing01_voice01_generate.py::generate_
  charon_english`・`er003_v1_sing01_point_headings_aoede.py::
  generate`・`er003_v1_sing01_news_tail_fix.py::generate_news_
  narration_wide_margin`・`er003_v1_repro01_main_generate.py::
  generate_key_phrase_component_verified`、日本語側`er003_v1_
  sing01_voice01_generate.py::generate_charon_japanese`、両言語共通
  `er003_v1_repro01_main_generate.py::generate_narration_snippet_
  verified_strict`(A2/B1双方のstandard経路がこの関数を経由するため、
  1箇所の配線で広くカバーできる)。fallback経路を持つ合成関数
  (`er003_v1_crosslevel_audio_02_common.py::generate_english_
  segment_with_fallback`・`er003_v1_n3_01_tts_generate.py::
  generate_a2_japanese_with_fallback`)自体はデコレータで包まず
  (standard経路の内部呼び出しが既にguardされているため二重guardに
  なる)、代わりにstandard経路が`HUMAN_REVIEW_LOCKED`を返した場合に
  fallbackへ進まないよう明示的な早期returnを追加した(fallbackは
  未ガードの直接TTS/ASR呼び出しのため、ここを通過させるとLockの
  意味が無くなる)
- **既知の適用範囲外(意図的、正直に記録)**: A2 6% slowdown retry
  (`generate_a2_segment_with_slowdown`、ER-008-A2-POSTPROCESS-
  SLOWDOWN-PROD-11)は、内側の`generate_english_segment_with_
  fallback()`が`status=OK`を返した直後に、post-process後のASR
  再検証が別途不一致となり、同じ内側関数を最大3回まで正当に取り
  直す既存の設計を持つ。当初`RESOLVED`状態もブロック対象にする設計
  だったが、これが上記の既存の正当なretryを機械的に止めてしまう
  ことを実装中に発見し撤回した(`RESOLVED`は監査用の記録に留め、
  ブロックしない設計へ修正)。本Guardが防ぐべきは「Human Review・
  繰り返し失敗への機械的再挑戦」であり、「一度成功したsegmentへの
  正当な再挑戦」ではないと整理した
- **実装中に発見したバグ(正直に記録)**: 初期実装では、out_pathが
  既存の命名慣習(".../<theme>/<level>/narration/<segment>.wav")に
  従わない場合(単体テストのダミーパス"dummy_out.wav"等)、theme/
  level/segmentが空文字列に縮退し、複数の無関係な呼び出しが同じ
  (ドライブルート直下の)store pathを共有してしまう実バグを、
  既存回帰テスト(`er007_ja_tts_retry_path_fix_test_01.py`、2件の
  test methodが同じダミーテキスト・パスを使う)の失敗で発見した。
  `_has_valid_narration_layout()`を追加し、out_pathが規約に従わない
  場合はReview Lock機構全体を無効化する(常にproceedし、store
  読み書きも行わない)よう修正して解消した
- **受入テスト(Part H、5ケース+補強4ケース)**: `er011_human_review_
  lock_01_test_01.py`(9件、全PASS)。(1)Human Reviewへ到達→queue
  登録→STOP、(2)同じsegment再実行→TTS/ASR call 0・既存状態を返す、
  (3)明示的`approve_regenerate()`→初めて再生成可能、(4)再生成後
  また失敗→再びlock(再承認なしでは解除されないことも確認)、
  (5)queue重複なし、に加え、budget guard発火・derive_segment_keyの
  Windows形式パス対応・台本変更時のlock無効化を追加確認した
- **実データ検証**: No.5 full_story_part1の実際の事故シナリオを
  再現するため、実際のProduction関数(`er003_v1_sing01_news_tail_
  fix.py::generate_news_narration_wide_margin`、事故で実際に使われた
  関数そのもの)に対し、事前にHUMAN_REVIEW_REQUIRED状態を模擬した
  lockを与えた上で直接呼び出し、0.003秒で即座に`HUMAN_REVIEW_
  LOCKED`が返る(実TTS/ASR API呼び出しが一切発生しない)ことを確認
  した
- **今回実施しなかったこと**: legacy/one-off script(P-series・
  IRAN01・SING01等、既にHISTORICAL化済みの完成テーマ向けスクリプト)
  からの直接呼び出しへの配線(現行Production経路[N3-01/pool_pilot_
  01系]のみを対象とし、Part Hの既存方針[Audio Validation Gate等]
  と同様、legacy scriptは対象外とした)
- **根拠レポート**: ER-011-HUMAN-REVIEW-COST-GUARD-01完了報告
- **影響するCURRENT_SPEC項目**: QA/Human Review節へ「Human Review
  Cost Guard(Review Lock機構)」を新規追加(`DECIDED`、
  `PRODUCTION_WIRED`)

## ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15: TTS retry上限3回化+固有名詞/日本語表記ゆれ/英語homophoneのCascade改修(Implementation Hardening)

- **日付**: 2026-08-28
- **背景**: 前タスク(No.8 Human Review監査)で、Human Reviewへ落ちた3件(`Kristie Tse`人名/`ころ・頃`表記ゆれ/`wait・weight`同音異義語)がいずれも「音声不良」ではなく、Validator/Cascade側の機能不足が原因と判明した。加えて、ASR表記ゆれだけを理由に同一segmentを最大6回TTS再生成する既存仕様がCost/Delivery上不合理と判断された
- **内容**(5点、状態は下記参照):
  1. **TTS retry上限 6→3回**(ユーザー正式決定): `er011_human_review_lock_01.PRODUCTION_MAX_TTS_ATTEMPTS = 3`をSSOTとし、Production全8関数の`max_attempts`既定値を統一。standard+fallback 2段構成の4関数は、fallbackへ残り予算のみを渡すよう改修(合計が3回を超えないことをテストで確認)
  2. **固有名詞ASR判定**: 「ASR結果同士の収束」を自動PASSの根拠にすることをやめ(ASR consensus ≠ pronunciation verification)、(A) CMU Pronouncing Dictionaryの代表発音がcanonical綴りと直接一致する場合のみコストゼロで自動PASS、(B) 辞書に無い外国由来名はPronunciation Ledgerへ実データを投入(cache miss時のみPerplexityで1回research、記事横断でcache再利用)するが、これは自動PASSの根拠にはせずHuman Reviewパッケージの充実のみに使う、という二分岐へ再設計した
  3. **日本語表記ゆれ**: 濁点差の一律許容(`_reading_equal_allowing_voicing`)ではなく、「ASR側漢字spanが辞書上持ちうる正当な読み候補にcanonical期待読みが含まれるか」+「異なる2エンジン(OpenAI/Azure)以上の裏付け」を要求する`ORTHOGRAPHIC_VARIANT_CONFIRMED`を新設
  4. **英語homophone**: CMU Pronouncing DictionaryのARPAbet完全一致を主根拠とする`HOMOPHONE_EQUIVALENT`を新設。Secondary側は「canonicalへ戻る」ことではなく「ARPAbet完全一致(canonical一致でも同じhomophoneでもよい)」を要求し、「他に問題が見つからなかった」という消極的PASSは禁止
  5. **attempts_log保持**: Human Review Lock発動後にattempts_logが空配列で上書きされていたバグを修正(`last_attempts_log`)
- **状態**: `DECIDED` / `VALIDATED`(2026-08-28修正: 前回報告で誤って`PRODUCTION_WIRED`としていたが、(a) commit/push未実施、(b) `wait/weight`はattempts_log消失バグにより実ログではなく合成データでの検証、(c) `Kristie Tse`はCase Bが未解決のままHuman Reviewへ残っている、という条件により`PRODUCTION_WIRED`の要件[実装完了・SoT反映・commit・push・Production配線・テストPASS・実データ確認・Production相当runtime evidence確認]を全ては満たしていないと判断し、`VALIDATED`へ訂正した。commit/push後、残課題が無いことを確認できた時点で改めて`PRODUCTION_WIRED`へ昇格する)
- **採用理由**: No.8監査で発見した3件の根本原因(ASR consensusをpronunciation verificationの代わりに使っていた設計上の誤り、日本語の濁点一律許容、homophone対応の欠如、無駄なTTS retry)へ、量産(100記事規模)を見据えた最小限の修正で対応するため
- **比較した選択肢と却下理由**(ユーザーとの複数回の設計レビューで変遷):
  - 固有名詞: 当初「複数ASR結果同士の音韻的収束で自動PASS」を検討したが、「ASR同士が似た誤認識で一致することは、正しい発音と一致している証拠にはならない」との指摘で却下。次に「Ledgerの`expected_pronunciation_ipa`を静的IPA→ARPAbet対応表で変換して比較」を検討したが、「ARPAbetは英語音韻前提であり、外国語由来の音韻情報が変換時に失われ誤PASSしうる」との指摘で却下。最終的に「CMU辞書で両方が直接解決できる場合のみ自動PASS、それ以外は自動PASSせずLedgerは人間向け情報提供のみに使う」という二分岐へ収束
  - Homophone: 当初「閉じたペアテーブルのみ」を検討したが、100記事規模での保守負荷・False Negative増大が懸念されたため、QCD比較の結果CMU Pronouncing Dictionary主体のハイブリッド方式(新規軽量dependency、pykakasiと同種の性質)へ変更
  - 日本語表記ゆれ: 当初「4ステップが同じ表記へ収束したことをPASS根拠にする」設計だったが、「ASRが同じ漢字を何回書いたかは読みが正しい証拠にならない」との指摘で、辞書上の読み候補照合方式へ変更
- **実装中に発見した事実**:
  - `er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin`が、旧`ER-010-ENTITY-PHONETIC-CORROBORATION-01`(`aggregate_entity_only_phonetic_corroboration`、ASR結果同士の収束による自動PASS)を実際にlive productionへ配線しており、No.8 Kristie Tseケースはこの経路を実際に通っていたことが判明(監査時点では「配線されていない分析用関数」と認識していたが、実際には1関数で使われていた)。設計変更に合わせてこの経路を撤去した
  - `_phonetic_pair_ok`(ER-010)の`a[0] != b[0]`(先頭文字の綴り完全一致要求)が、"Kristie"(k)/"Christy"(c)のような、綴りは異なるが同じ音(/k/)を表す組を誤って弾いていたバグを、既存の`_SOUNDEX_CODES`テーブル(C/G/J/K/Q/S/X/Zを同一グループとして扱う)を先頭文字比較にも再利用する形で修正。ただし今回の再設計により、この関数自体はlive cascadeのPASS判定には使われない(audit専用関数のまま)
  - CMU Pronouncing Dictionaryに偶然"tse"というentryが存在し(無関係な理由、ARPAbet代表発音"T S IY1")、その1バリアント("S IY1")がASR誤認識候補"Sea"/"C"と一致してしまう実例を発見。固有名詞Case Aを「いずれかのバリアントが一致すれば可」ではなく「代表(先頭)バリアントの完全一致のみ」という、homophoneチェックより厳格な基準にした理由はこれ
  - pykakasiが同梱する漢和辞書データ(`kanwadict4.db`)が、単漢字の正当な読み候補一覧をそのまま提供することを発見し、新規dependencyゼロで日本語側の読み候補照合を実装できた
- **既知の限界(正直に記録)**: 「頃」のように単漢字として複数の読み(ころ/ごろ)が辞書上正当に登録されている文字は、テキストのみからは実際に発話された読みを完全には確定できない(OPEN-80)。異なる2エンジンの裏付けを要求することで緩和しているが、原理的な限界として残る
- **Part M再validation結果**(既存音声を再TTSせず、記録済みASR文字起こしへ新ロジックを再適用):
  - `ころ/頃`(A2 preview): 実際の記録済み4ステップASR結果で`ORTHOGRAPHIC_VARIANT_CONFIRMED`としてVALIDATED
  - `Kristie Tse`(B1 point_two): 実際に記録された5回のCascade試行のうち、ASRが偶然"Tse"を正しく書き起こした1回のみ`PROPER_NOUN_ENTITY_ARPABET_CONFIRMED`でVALIDATED(残り4回はCase Aで解決できず、Pronunciation Ledgerの実データ[Perplexity research、記事横断cache済み]を伴ってHuman Reviewのまま)。**正直な留保**: 旧6回retry前提で記録された5取得分の再評価であり、新しい3回上限の下で新規に3回生成し直した場合に同じ結果(1/3が解決)になる保証はない(新規TTS生成はPart Mの禁止事項のため未検証)
  - `wait/weight`(A2 point_one_heading): Human Review Lock発動時のattempts_log消失バグにより生ASR文字列が残っておらず、ユーザーの元タスク記述にある既知事実(「ASR: weight」)を仮定した合成データで`HOMOPHONE_EQUIVALENT`としてVALIDATED(実データでの裏付けは取れていない、OPEN-82)
- **regression**: 既存の全テストファイル(`er006_preprod_hardening_01_validation_test.py`55件、`er006_secondary_asr_01_test.py`14件→19件、`er007_ja_asr_validator_01_test.py`30件、`er007_ja_secondary_asr_01_test.py`6件→9件、`er006_pronunciation_ledger_01_test.py`5件、`er011_human_review_lock_01_test_01.py`9件→13件、`er010_entity_phonetic_corroboration_01_test_01.py`22件)が全てPASS。新規`er008_asr_variant_hardening_15_homophone_en_test.py`(6件)も全てPASS
- **API call数・コスト**: Perplexity research 1回(Kristie Tse、Part M再validation実行時に実施、記事横断でcache再利用されるため今後同一entityでの再課金は発生しない)。TTS/ASR APIの新規呼び出しは0件
- **根拠レポート**: ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15完了報告
- **影響するCURRENT_SPEC項目**: Audio Implementation Detail節へ「TTS生成の同一segment総試行回数上限」「固有名詞ASR不一致の自動PASS条件」「日本語表記ゆれのCascade内自動PASS条件」「英語homophoneのCascade内自動PASS条件」を新規追加

### 継続セッション(同日2026-08-28): 固有名詞ASR不一致の量産仕様化を検討し、STOP

- **依頼内容**: 上記(A)の「CMU辞書に無い固有名詞は常にHuman Review」という設計は、1日数十記事の量産では毎回Human Reviewが発生し不十分なため、「外部の信頼できる発音根拠(本人・公式情報源由来のIPA/音声等)を取得し、それを現在のTTS実音声と自動照合してAUTO PASSする」という正式フローへの格上げを検討した
- **調査結果**: 既存コードベースを確認したが、TTS実音声を音素レベルで書き起こす機能(phonetic ASR)、外部参照音声とTTS音声を音響的に比較する機能、強制アライメント(forced alignment)のいずれも実装されていない。ASR層(`er006_asr_provider_routing_01`のOpenAI ASR、`er006_secondary_asr_01`のAzure STT)は単語単位の正書法テキストしか返さない。`er006_pronunciation_research_01.research_pronunciations()`(Perplexity)が返すのもテキストのIPA/カタカナ的ヒントであり、参照音声そのものではない。OPEN-80も「音声そのものを使った実発音確認(MFA等の強制アライメント)」を将来検討事項として明記しており、現時点で未着手であることと整合する
- **判断: STOP**(タスク仕様§3の「実装上のSTOP条件」に従い、近似実装を行わずここで報告する)。「外部発音根拠 ↔ TTS実音声」を安全に自動照合する軽量な既存手段が無いため、Case B(CMU辞書に無い固有名詞)の自動PASS化は今回実装しない。検討した設計オプションと却下/保留理由:
  1. **Azure Pronunciation Assessment API**(既存のAzure Speech SDK依存を流用可能): 音声とreference textを渡すと音素単位の一致度スコアを返す機能。ただし本来は「学習者の発音が指定localeの標準的な発音にどれだけ近いか」を測る用途であり、外国語由来の固有名詞のカスタムIPAをreferenceとして直接検証できる設計ではない。誤った基準で「一致」と判定するリスクがあり、採用前に個別の検証実験が必要
  2. **外部参照音声(Forvo等)とTTS音声の音響的類似度比較**: 参照音声の取得・利用許諾、音響特徴量(MFCC等)によるDTW/類似度判定の実装・閾値調整が必要で、「軽量な追加実装」の範囲を超える新規パイプラインになる
  3. **音素レベル強制アライメント(MFA等、OPEN-80が既に言及)**: 音響モデルを伴う本格的な新規依存であり、同じく軽量実装の範囲を超える
  - いずれも「安全に比較できない方式を無理に近似しない」という原則、および「大規模Validator刷新はしない」という納期制約の両方に反するため、今回は採用しない
- **今回実施した安全な範囲の改善**(自動PASS化とは無関係、Human Reviewの質向上のみ):
  - `er006_pronunciation_research_01.py`のPerplexityプロンプトを改訂し、「本人・公式サイト・所属組織・公式イベント・信頼できるインタビュー等の一次情報源を優先する」指示を追加(取得したcitationsの信頼性が上がり、Human Reviewパッケージの質が上がる。自動PASSの判断には使わない)
  - OPEN-80を「頃」個別の問題から「同一漢字表記に複数の正当な読みがある語全般(多読漢字)」の問題へ再定義(詳細はOPEN_ITEMS.md参照)。既存の`ころ/頃`AUTO PASS仕様(ORTHOGRAPHIC_VARIANT_CONFIRMED)は変更していない
- **量産への影響**: Case B(外国由来固有名詞)は引き続きHuman Reviewへ進む。ただしPronunciation Ledgerによるresearch結果の記事横断cache再利用(Perplexity再課金の回避)は既に本番配線済みのため、同一固有名詞の外部検索コストが繰り返し発生することは無い。Human Reviewの発生自体を無くすには、上記いずれかの設計オプションの実験的検証が別タスクとして必要
- **状態**: `STOPPED_FOR_DESIGN_REVIEW`(ユーザー判断待ち。実装は行っていない)

## ER-008-N8-HUMAN-APPROVAL-AND-PROPER-NOUN-PRONUNCIATION-SPEC-16(2026-08-28)

- **目的**: (1) No.8でHuman Review待ちだった3 segment(A2 `preview`・A2 `point_one_heading`・B1 `point_two`)について、ユーザーが実際に試聴した結果を正式なHuman Approval記録へ反映しAssemble可能にする。(2) 固有名詞の発音判定基準を、「本人・原語としての厳密な発音」偏重から「eigo-radioが英語学習コンテンツであることを踏まえた、英語圏で実際に通用する発音」基準へ変更する
- **経緯**: 前セッションで作成した[Gate Hold](https://claude.ai/code/artifact/a545159e-fe1f-4816-8b66-56e5af6dfd1d)アーティファクトで3 segmentの音声をユーザーへ提示。ユーザーが実際に試聴し、3件とも現状の音声のまま使用してよいと判断(`Kristie Tse`のみ、本人の唯一の厳密発音ではなく「seeに近い、英語圏で許容される発音」という理由での承認)
- **Human Approval記録**(`er003_v1_n3_01_assemble.record_human_approval()`、新規TTS/ASR呼び出しなし):
  | segment | out_dir | canonical_text_sha256(先頭12桁) | 承認理由 |
  |---|---|---|---|
  | `preview` | `.../a2` | 参照実装参照 | ユーザー試聴、そのままでOK |
  | `point_one_heading` | `.../a2` | 参照実装参照 | ユーザー試聴、そのままでOK("A small wait can protect against a big fear") |
  | `point_two` | `.../b1b` | 参照実装参照 | ユーザー試聴、`Kristie Tse`の`Tse`が"see"に近い発音で英語圏の許容発音候補に含まれると判断 |
- **発見した既存バグとその修正**: 上記3件を承認記録した後にAudio Validation Gate(`verify_episode_audio_validation_gate`)を実行したところ、A2の2件(`preview`/`point_one_heading`)が承認記録があるにもかかわらずブロックされ続けることを発見した。原因調査の結果、`_segment_gate_status()`(ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05で実装)が判定する`status`分岐に、後から実装されたER-011 Human Review Lockが書き込む`status=HUMAN_REVIEW_LOCKED`という値が存在せず、どの分岐にも一致しないため無条件で`UNVALIDATED`(未承認)へ落ちてしまうという、2つの機能間の統合漏れ(いずれも正しく動作していたが、組み合わせ時の考慮が漏れていた)と判明した。`er003_v1_n3_01_assemble.py::_segment_gate_status()`の承認確認分岐に`HUMAN_REVIEW_LOCKED`を`ASR_VALIDATION_UNCERTAIN`と同列で追加し、修正後に3件全てが`HUMAN_APPROVED`として正しく通過することを実データで確認した(Gate自体の強制無効化・bypassは一切行っていない。承認記録が無いsegmentは修正後も引き続きブロックされる設計のまま)
- **固有名詞の発音判定基準の変更**(ユーザー承認、`APPROVED_FOR_PRODUCTION`): 新しい判定優先順位は (1) 本人自身の英語での発音 → (2) 公式プロフィール・所属組織・公式イベント等で確認できる英語発音 → (3) 信頼できる情報源で確認できる一般的な英語圏発音 → (4) 複数の英語圏発音が実際に認められる場合は許容発音集合として保持、の順。母語・原語における唯一の厳密発音との一致は今後必須条件にしない。**実装は行っていない**(現時点ではHuman Reviewでの人間の判断基準の変更のみ。Cascadeの自動判定ロジックへの組み込みは行っていない)
- **No.8 Assemble結果**(`stage_assemble_a2`/`stage_assemble_b1`、新規TTS/ASR呼び出し0件):
  - B1: `er006_output/pool_pilot_01/pool_n8_airport_line/b1b/assembled/English_Your_Way_B1B_POOL_N8_AIRPORT_LINE.wav`、318.155秒、clipping無し、peak 0.858
  - A2: `er006_output/pool_pilot_01/pool_n8_airport_line/a2/assembled/English_Your_Way_A2_POOL_N8_AIRPORT_LINE.wav`、372.827秒、clipping無し、peak 0.770
  - 完成音声(mp3変換版)をArtifactとして提供: https://claude.ai/code/artifact/d558fc26-3214-4987-9024-996bb9acbdef (Now Boarding)
- **API call数・コスト**: TTS 0件、ASR 0件、Perplexity等の外部発音調査 0件(全てローカルのAssemble処理のみ)
- **regression**: `_segment_gate_status()`変更に対する既存の専用テストファイルは無い(ER-008-15完了時点で確認済みの既存テストスイートに影響する変更ではない、Assembly gate関連のロジックのみの追加分岐)
- **影響するCURRENT_SPEC項目**: 「固有名詞ASR不一致の自動PASS条件」に発音基準変更を追記、「Audio Validation Gate」に`HUMAN_REVIEW_LOCKED`対応バグ修正を追記
- **OPEN-83への影響**: 判定基準の変更により今後Case B固有名詞がHuman Reviewへ進む頻度は下がる見込みだが、「外部発音根拠とTTS実音声を安全に自動照合する仕組み」自体は依然未実装のため、OPEN-83は`STOPPED_FOR_DESIGN_REVIEW`のまま維持。将来実装時は「唯一の原語発音」ではなく「許容される英語発音集合のいずれかとの一致」を判定対象にする旨をOPEN-83へ追記した
- **状態**: 3件のHuman Approval・Audio Validation Gate通過・No.8 Assemble完了は`DECIDED`。固有名詞発音判定基準の変更は`APPROVED_FOR_PRODUCTION`(Cascadeの自動判定ロジックへの実装・テスト・Production経路でのruntime確認が完了するまでは`PRODUCTION_WIRED`としない)

## ER-008-N8-QA-CONTENT-SPEED-HARDENING-18 / ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19(2026-08-29、Implementation Hardening)

- **背景**: No.8ユーザーFeedback監査(ER-008-N8-USER-FEEDBACK-AUDIT-17)で判明した12件の指摘のうち、即修正必須/実ユーザー検証前に直すべき、と分類された項目についてER-18で設計・トライアル実装・No.8個別修復を行い、ユーザー承認を得た上でER-19にてProduction経路への正式配線・回帰テスト・runtime evidence取得まで行った。ER-18時点の変更はcommit/pushされておらず、DECISION_LOGへの記録も本entryが初出のため、ER-18の決定事項も併せて記録する。
- **内容(項目ごと、状態は各行末尾を参照)**:
  1. **A2 disfluency QA(Key Phrase "uneven uneven choice")**: 前回調査(ER-17)では「Key Phraseの意図的な2回読み」と誤認識していたが、ユーザーの指摘で再調査した結果、`kp2_en.wav`単体に"uneven, uneven choice"という実在のpartial repetitionがあり、Production ASRがこれを平滑化して書き起こしていたためValidatorをすり抜けていたことを確認した(誤った前回結論を訂正)。無料・ローカルのfaster-whisperによるverbatim再チェック(`er008_disfluency_qa_18.py`)を新設し、Key Phrase/Point見出し/In One Line/B1 Previewの生成関数(`generate_key_phrase_component_verified`/`generate_a2_segment_with_slowdown`系/`point_headings.generate`/`generate_news_narration_wide_margin`/`generate_charon_english`)へ`disfluency_qa`引数として配線した。flag時は既存のTTS retry loop内でverified=Falseとして扱い、既存の総試行回数上限(3回)内で自動的にTTSを取り直す設計とし、Human Reviewを第一選択にしないというユーザー指示を満たした。No.8の実Key Phrase生成関数呼び出し(kp2相当のテキスト)でruntime evidenceを取得(disfluency_checked=True、当該実行では repetition非再現でOK)。**状態**: `PRODUCTION_WIRED`
  2. **B1 partial-word false start("Wh, why does...")**: 2種類の独立したfaster-whisperモデル(small/tiny)で再検証したが、テキスト上の証拠は見つからなかった(前回の波形20msエネルギー閾値による「検知」はfalse positiveだった可能性が高いと訂正)。word-level ASRの構造上、単語の一部分だけの言い直しは検知できないという既知の限界がある。ユーザー指示によりOpen Item化(OPEN-86)し、量産前解決必須・人手による毎回確認は不採用と明記。**状態**: `OPEN`(OPEN-86)
  3. **Point One/TwoとFull Storyの意味重複**: 第1段階のローカルlexical overlap検知(`er008_point_overlap_qa_18.py`)を新設し、暫定閾値0.45→ユーザー承認により0.40へ変更。記事全体を再生成せず、NGになったPoint 1件だけを再生成する`er008_point_regenerate_19.py::regenerate_point_only()`を新設し(Verified Fact Ledger・確定済みFull Story・他方のPointをcontextとして固定、Full Story論理の言い換え・新Fact追加・causal/certainty/scope driftを明示的に禁止)、`er003_v1_n3_01_articles_generate.py::run_one_pattern()`(Evidence Compression後・Fact Checker前)へ配線した。regenerateされたPointも既存のFact Checker/Ledger Deviation Checkを通る設計とした。No.8 B1実データ(Point One、Full Storyとのoverlap 0.481)で実証: 再生成後overlap 0.188(Full Story)/0.094(他方のPoint)まで低下、内容も「小さなコストvs大きな損失」から「秩序の公平性への不信」という別角度へ実際に変わったことを確認。**既知の限界**: 「新Fact追加なし」の判定は内容語の出現有無による弱いヒューリスティックに留まり、意味的なFact整合の最終判断は人間が必要。**状態**: `PRODUCTION_WIRED`
  4. **Comment 2内部ラベル漏れ("In Part 2...")**: 発生源(Comment生成のcontext/role prompt、A2/B1双方)から"Part 1/Part 2/Full Story Part 1/2"を除去し、非構造的な「前半/後半」表現へ変更。第二防御線として`er003_audio_tts_asr_safety.detect_internal_production_labels_in_english_text()`を新設し、`generate_charon_english()`(A2/B1共通)のTTS呼び出し前に配線した。No.8実データでComment 2(A2/B1とも)を再生成し、新Validatorでの検出0件を確認。**状態**: `PRODUCTION_WIRED`
  5-A. **A2 6% slowdown 必須post-process invariant gate**: No.8 point_one_headingが、Human Review Lock経由の承認によりslowdownを一度も受けないままVALIDATED扱いでAssembleへ到達していた事故を受け、他のmandatory post-process(trim・gain正規化)を横断調査した結果、抜け道が存在するのは条件付きで実行される6% slowdownのみと判明(大規模Architecture変更は不要と判断)。`er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate()`へ、A2の対象segmentについて`slowdown_applied`フィールド(第一evidence)または`{name}_original.wav`の現存(第二evidence、過去の「resume」系scriptがメタデータを記録し損ねていた既存データとの後方互換用)のいずれかを要求するinvariantチェックを追加した。No.8のpoint_one_heading相当ケースをfixtureで再現しblockされることを確認、かつNo.8の実データ(過去のresume由来segmentを含む)ではPASSすることを確認。**状態**: `PRODUCTION_WIRED`
  5-B. **B1 Preview話し方**: 実測WPM調査でPreview(184.5)が他のCharon segment(topic_intro 143.9、comment_1〜4は148.1〜173.5)より明確に速いことを確認(全segment共通の`ENGLISH_STYLE_PREFIX`のみで、Preview専用の速度制御が存在しなかったことが原因)。A2と同じ「自然言語のみ、数値WPM指定なし」方針で`B1_PREVIEW_STYLE_PREFIX_CALM`を新設し、既存の`style_prefix_override`引数経由でPreview呼び出しにのみ適用(topic_intro/comment_1-4は無変更)。ユーザーが比較試聴の上正式採用。Comment 1-4については現状調査(実測WPM記録)のみ行い、変更は今回未実施(ユーザー試聴前の正式確定を待つ)。**状態**: Preview `PRODUCTION_WIRED`、Comment 1-4は`TBD`(調査のみ)
  6. **Evidence Compression日付過多**: ユーザー指示により今回実装せず、OPEN-84を維持(変更なし)。**状態**: `OPEN`(OPEN-84)
  7. **A2 Preview短縮**: 現行157字/4文をユーザーが「長い」と指摘。theme/problem/valueの3要素を律儀に別文で書き並べない、2文程度・80〜110字程度を目安とする指示へ`PREVIEW_ROLE`(`er003_v1_iran01_a2_generate.py`)を更新した(絶対文字数のhard limitにはしない)。No.8の実際のarticle.md・comment_1/2テキストを使い、本番のPrompt/model/context経由で新規生成した結果157字→74字(2文)を確認(runtime evidence)。No.8本編の完成音声自体は今回差し替えていない(Prompt配線のみ、今後の新規生成から適用)。**状態**: `PRODUCTION_WIRED`(Prompt)
  8. **Key Phrase日本語gloss括弧書き**: ユーザー指示により今回実装せず、OPEN-85を維持(変更なし)。**状態**: `OPEN`(OPEN-85)
  9. **Stephen Reicher文修正**: ユーザー事前承認の置換文言をNo.8 B1 Full Story Part1へ適用し、TTS/ASR再生成・再Assemble済み(量産仕様変更なし、個別修正のみ)。**状態**: `DECIDED`(No.8限定の個別修正)
- **regression**: `run_project_regression.py`実行、collected=1895・passed=1893・failed=2(いずれも今回変更と無関係な既存の失敗: `er003_test_p2j_investigate.CollectionCountTests.test_combined_equals_sum_of_er002_and_er003`[er008系テストファイル増加によりcollected総数が既存の算術チェックとズレる既知の仕様]、`er007_ja_tts_retry_path_fix_test_01.VoiceCharonJapaneseStopRetryingTests.test_stop_retrying_false_still_retries_normally`)。新規追加したテストファイル5件(`er008_disfluency_qa_18_test_01.py`・`er008_point_overlap_qa_18_test_01.py`・`er008_point_regenerate_19_test_01.py`・`er008_n3_01_point_qa_wiring_19_test_01.py`・`er008_a2_slowdown_invariant_19_test_01.py`・`er008_internal_label_gate_18_test_01.py`)は全件PASS
- **API call数・コスト**: 本セッションのruntime evidence取得のための実API呼び出しは、(a) No.8実Key Phrase(kp2相当)のTTS 1回+ASR 1回、(b) No.8実A2 Preview生成LLM呼び出し1回、(c) No.8実B1 Point One regeneration LLM呼び出し1回、の計3件(いずれも数円〜十数円程度の少額、新規Providerの追加なし)。faster-whisperによるdisfluency QA自体はローカルCPU処理のみで追加API課金は無し
- **既知の限界(正直に記録)**: Point-only regenerationの「本当に新しい切り口か」「新Factが追加されていないか」の意味的判定は自動化されていない(弱いヒューリスティック+人間確認が前提)。disfluency QAは「同一単語まるごとの繰り返し」しか検知できず、partial-word型の言い直しは別課題として残る(OPEN-86)。A2 slowdown invariant gateのoriginal.wavフォールバックは、悪意ある/誤ったファイル配置による偽装を技術的に防止しない(既存データとの後方互換のためのゆるい第二evidence)
- **影響するCURRENT_SPEC項目**: 「Preview」節(A2 Preview長さ・B1 Preview話し方・B1 Comment話し方の3行追加)、「QA / Human Review」節(Disfluency QA・Point重複検知+regeneration・Comment内部ラベル二重防御・A2 slowdown invariant gateの4行追加)
- **OPEN_ITEMSへの影響**: OPEN-86新設(B1 partial-word false start、量産前解決必須)。OPEN-83/84/85は状態変更なし(維持)
- **状態**: 上記の通り項目ごとに異なる(`PRODUCTION_WIRED`5件、`OPEN`3件、No.8限定個別修正1件)

## ER-008-N8-FINAL-AUDIO-AND-REMAINING-PRODUCTION-WIRING-20(2026-08-29、Implementation Hardening)

- **背景**: ER-19で`PRODUCTION_WIRED`とした項目のうち、B1 Comment 1-4話し方だけがユーザー試聴前の`TBD`のまま残っていた。ユーザーがCommentへもPreviewと同じcalm styleを正式採用すると決定したため、Production配線・No.8完成版への実反映・最終試聴Artifact作成までを行った
- **内容**:
  1. **B1 Comment 1-4話し方の正式採用・配線**: `er003_v1_n3_01_tts_generate.py::generate_b1_segments()`のpreview/comment_1〜4共通ループを、Previewのみ→全件へ`style_prefix_override=B1_PREVIEW_STYLE_PREFIX_CALM`・`disfluency_qa=True`を適用するよう変更(Full Story/Point/In One LineへはBody別loopのため波及しない)。定数コメント内の"this introduction"という限定的文言を"this"へ一般化(Comment再利用に合わせた文言修正のみ、instruction本文の実質的な意味は変更なし)。No.8実データで実際にpreview/comment_1〜4を再TTS・ASR再検証し、実測WPM: preview 154.5(旧184.5)/comment_1 181.8/comment_2 143.0/comment_3 148.6/comment_4 153.6を確認、全件でdisfluency_checked=true・flagged=false・asr_verified=trueを確認。**状態**: `PRODUCTION_WIRED`
  2. **既承認6項目の再確認**: disfluency QA/Point overlap+regeneration/Comment内部ラベル二重防御/A2 slowdown invariant gate/B1 Preview calm style/A2 Preview短縮について、実装済み・正式Production経路から呼ばれる・設定が有効・テストPASS・runtime evidenceありの5条件を再確認した。結果は全て条件を満たしていたが、**Comment内部ラベル二重防御の項目で、前回(ER-19)の「A2/B1とも実データ0件確認」という報告に誤りを発見**(下記4を参照)
  3. **Point-only regenerationのFact fabricationリスクを実データで確認**: No.8のPoint One(A2: overlap 0.4、B1: overlap 0.542、いずれも閾値0.40でflag)に対し、記事全体を再生成せず`run_point_overlap_qa_and_regenerate()`を直接呼び出すsurgicalな方法(`er008_n8_point_regen_and_verify_20.py`)でPoint-only regenerationを実行した。生成された新テキストは、いずれもFull Story/他方Pointとの重複は大きく改善した(B1: overlap 0.542→0.188/0.094)が、検証済みFact Ledgerに存在しない新規主張(「American Airlinesが順番外搭乗に罰則を導入」「United Airlinesが搭乗改善策を試験中」等)を含んでおり、後続のFact CheckerがA2/B1ともREVIEW_REQUIRED(unsupported_specific_claims 3〜5件)と判定した。ユーザーが指示した監視項目「新Factを追加していないか」がまさに実際に発生した実例であり、`regenerate_point_only()`の自動validation(overlap再チェックのみ、Fact Checkerは含まない)だけでは不十分であることが実データで判明した。この結果は採用せず、Point One/parts.json/article.mdを元のテキストへ差し戻し、Fact Checker(再実行)でPASS・Ledger Deviation CheckでLEDGER_COMPLIANT(0件)を再確認した。**状態**: `PRODUCTION_WIRED`(機構自体は維持)、`MONITORING`(恒久対策は未実装、実ユーザー検証中の監視対象として明記)
  4. **Comment内部ラベル二重防御: ER-19報告の誤りを訂正**: 上記2の再確認作業中、No.8のB1 Comment 2 canonical text(`b1_support_texts.json`)に"In Part 2, what is American Airlines doing to manage this behavior?"という内部ラベルが**修正されないまま残っていた**ことを発見した。ER-19の報告(「No.8実データでComment 2[A2/B1とも]を再生成し検出0件を確認」)はA2側のみ正しく、B1側は実際には未修正だった(Validator自体は正しく機能しており、テキスト修正が漏れていた)。今回、Comment 1-4のcalm style適用に伴いcomment_2を実際に再生成した際、新Validatorが正しくこれを検出・STOPPEDでブロックしたことで発覚した。"In the second half, what is American Airlines doing to manage this behavior?"へ言い換え(A2 comment_2修正[No.4]と同じ、内部ラベルを一般的な時系列表現へ置き換えるだけの最小修正)、再生成してASR verified=true・disfluency flagged=falseを確認し、No.8完成版へ反映した。**状態**: `PRODUCTION_WIRED`(B1側の実データ不整合を修正済み)
  5. **No.8完成版の再Assemble**: 上記の変更を反映するため、変更のあったsegmentのみ再TTS(A2: preview。B1: preview・comment_1〜4)し、他segment(point_two等、Human Review承認済みを含む)は既存の音声をそのまま再利用した上で、`stage_assemble_b1`/`stage_assemble_a2`を実行。Audio Validation Gate(A2 slowdown invariant gate含む)は両レベルともPASS。A2: duration 360.97秒・peak 0.854・clipping無し。B1: duration 327.51秒・peak 0.825・clipping無し。ユーザー最終試聴用Artifact(フルエピソード2本+変更segment6本の個別試聴)を作成: https://claude.ai/code/artifact/ddedda51-daee-44c4-9e3a-88212deb30b1 。**状態**: `USER_FINAL_REVIEW`
- **regression**: `run_project_regression.py`実行、collected=1895・passed=1893・failed=2(ER-19と同一の、今回変更と無関係な既存の失敗2件のみ)
- **API call数・コスト**: (a) No.8実B1 Comment 1-4+Preview再TTS 5回+ASR 5回、(b) No.8実A2 Preview再TTS 1回+ASR 1回(audit記録の再整合目的、テキスト不変のため実質再生成)、(c) Point-only regeneration LLM呼び出し2回(A2/B1、いずれも不採用)+Fact Checker再実行4回(regenerated版2回+revert後再確認2回)+Ledger Deviation Check再実行2回、(d) B1 comment_2修正の再TTS 1回+ASR 1回。いずれも数円〜数十円程度の少額、新規Providerの追加なし。faster-whisperによるdisfluency QAはローカルCPU処理のみで追加API課金は無し
- **既知の限界(正直に記録)**: Point-only regenerationのFact安全性は自動化されておらず、今回のように生成物を人間(Claude)が個別に確認して差し戻す運用に依存している。恒久対策(再生成後にFact Checkerを自動実行し、REVIEW_REQUIRED/FAILなら自動的に差し戻すゲート)は今回実装していない
- **影響するCURRENT_SPEC項目**: 「Preview」節(B1 Comment 1-4話し方をPRODUCTION_WIREDへ、A2 Preview長さにNo.8反映済み注記を追加)、「QA / Human Review」節(Point重複検知+regenerationにMONITORING注記追加、Comment内部ラベル二重防御に訂正注記追加)、「Audio Assembly」節(No.8完成版再Assemble行を新設)
- **OPEN_ITEMSへの影響**: なし(OPEN-84/85/86は状態変更なしのまま維持、ユーザー指示通り)
- **状態**: 上記の通り項目ごとに異なる(`PRODUCTION_WIRED`4件、`MONITORING`1件、`USER_FINAL_REVIEW`1件)

## ER-008-N8-FINAL-QA-HARDENING-21(2026-08-29、Implementation Hardening + サービス・生成仕様混在)

- **背景**: ユーザーがNo.8最終試聴で6件の品質問題を報告した。うち3件(disfluency QA取りこぼし・Key Phrase gloss括弧書き・Point-only regeneration)は今回実装まで完了させ、残り3件(semantic consistency・Evidence Compression日付拡張・A2 In One Line速度)は調査・設計・コスト概算までを行い、ユーザー指定のSTOP条件に該当するため実装前にユーザー確認を求めることにした
- **内容**:
  1. **disfluency QA資産-記録紐付けの恒久修正(No.8 A2 kp2 "uneven choice"の実修正)**: 「disfluency QAはPRODUCTION_WIREDと報告済みなのに、実際の完成版音声に反復が残っていた」という報告を調査した結果、根本原因が3つ判明した。(a) `disfluency_checked`/`disfluency_evidence`が各生成関数のattempts_log内にしか記録されず、segment記録のtop-levelへ昇格されていなかった(6ファイルの生成関数すべてが同一パターンの欠落)。(b) `er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate()`がstatus=="OK"しか見ておらず、disfluency QAの証跡を一切参照していなかった。(c) `er006_master_audio_store_01.get_or_generate()`のcache hit reuse分岐が、生成時のQA証跡を運ばず最小限dict(status/path/reused/master_audio_idのみ)しか返さなかったため、QA合格済みの資産でも再利用のたびに証跡が失われる設計だった。kp2_en.wav自体は、disfluency QA配線(commit bef70c1、2026-08-29 08:08)より約24.5時間前(2026-08-28 07:31)にMaster Audio Store経由で生成された旧assetで、配線後もこの同じmasterがcache hit再利用され続けていた(sha256一致で確認、ファイル自体が生成後に差し替わった形跡はない)。恒久対策として3層を実装: (A) 上記6生成関数すべてでtop-level昇格、(B) Gateへ`_segment_missing_mandatory_disfluency_qa(name, entry, level)`を新設し、レベル別mandatory segment(B1: preview/comment_1-4/in_one_line/point_one_heading/point_two_heading、A2: in_one_line/point_one_heading/point_two_heading[preview/commentは日本語のため対象外と実装中に発見・修正]、Key Phrase英語は両レベル共通)についてtop-levelの`disfluency_checked is True`が無ければfail-closedでblockする、(C) Master Audio Store manifestへ`qa_evidence`を保存しreused=True側にも復元する。加えて`_segment_asset_hash_stale()`(記録済みsha256と実ファイルの突き合わせ)も新設した。No.8実データでは、新Gateにより過去生成された全English mandatory segment(A2/B1合計21件)が一旦block対象になったが、無料・ローカルのfaster-whisper再検査(`er008_n8_disfluency_backfill_21.py`)でkp2以外は全てクリーンと確認しbackfill(追加費用ゼロ)、kp2のみ実際に反復ありと再確認され、Master Audio Storeの該当manifest entry・音声ファイルを削除した上で本番経路(`shared_narration.ensure_key_phrase_english_component`)で再生成した(disfluency flagged=false、ASR EXACT_MATCH)。**状態**: `PRODUCTION_WIRED`(資産-記録紐付けまで確認済み)
  2. **Key Phrase日本語glossの括弧書き禁止**: No.8 A2のKey Phrase 1 gloss「搭乗前に列に並ぶ人（俗称）」が音声で読み上げると不自然な問題(OPEN-85)を調査し、発生源をKey Phrase選定段階(`er003_key_words_research10.py`が読み込むP2選定prompt、L/P/U全戦略共通の`ja_gloss`指示)と特定した(`er003_key_words_canonicalization.py`はglossを素通しするだけ)。3つのprompt template(`er003_v1_translator_briefs/b2_key_words_research10_{l,p,u}_prompt_template.txt`)へ「音声のみで意味が成立する自然な表現にする、括弧補足は避ける」指示を追加し、A2/B1で共通適用されるようにした。機械的Validatorも`validate_research10_selection()`へ追加(全角/半角括弧検知、新規API呼び出しなし)。No.8のA2 Key Phrase 1 glossを「ゲート前で早く並ぶ乗客を指す俗称」(B1と表現統一)へ修正し、本番経路で再TTS・ASR再検証(verified=true)。**状態**: `PRODUCTION_WIRED`、OPEN-85 CLOSE
  3. **Point-only regenerationのPRODUCTION_WIRED撤回**: ER-20で確認されたFact fabricationリスクを受け、ユーザーが「Point-only regenerationをProduction自動経路から外す」ことを正式決定した。`er003_v1_n3_01_articles_generate.py::POINT_ONLY_REGENERATION_ENABLED = False`(既定)を新設し、`run_point_overlap_qa_and_regenerate()`は overlap検知(monitoring)のみ行い、flag時も本文を一切書き換えず`NG_REVIEW_REQUIRED`として記録するだけに変更した(regenerate_point_only()自体は呼び出されない、回帰テストでLLM呼び出し0件を確認)。暫定Production方式として提案された「記事全体Writerを再実行、overlap再QA、NGなら最大2回retry、それでもNGならNG/REVIEW_REQUIRED」については、Writer実測コスト(No.8実測: writer_a2単独で約$1.50、writer_b1で約$1.35)を踏まえるとoverlap NG発生率(現時点で不明)次第でコストが数倍化する可能性があり、「Writer retry方式でProductionコストが大幅増」というユーザー指定のSTOP条件に該当し得ると判断し、今回はwiringまで到達していない(OPEN-88、ユーザー確認待ち)。**状態**: overlap検知は`MONITORING`として`PRODUCTION_WIRED`、Point-only regeneration自体は`PRODUCTION_WIRED`撤回・既定無効化
  4. **semantic consistency("wait"問題)の調査・STOP**: No.8で同一語"wait/waiting"が記事内で逆方向の意味(待たずに危険を冒す行動 vs 並んで安心する行動)を指している実例(A2/B1とも)を実データで確認した。既存QA(Fact Checker・Ledger Deviation Check・Point overlap QA)はいずれもこの種の記事内semantic consistencyを検査対象にしていないことをprompt/schema精査で確認した(Fact Checkerは外部事実整合、Ledger Deviationはfact ledger整合、Point overlap QAはPoint-Full Story間の言い換え検知が目的)。No.8内の他の高頻度語は簡易頻度スキャンで目視確認した限り同種の衝突は見つからなかった(網羅的LLM検査ではない)。対策候補(A: 記事全体LLM consistency check新設、B: 重要語抽出+疑わしいものだけLLM確認、C: Writer prompt予防的指示)を提示し、実測コスト参考値(writer $1.3〜1.5、research系各$0.2〜0.4)からAの追加コストを1記事$0.2〜0.6程度、1000記事/月換算$200〜600/月と概算したが、「有料LLM追加が大きな月次コスト増になる」というSTOP条件に該当し得るため実装せず、OPEN-87としてユーザー確認待ちとした。**状態**: `OPEN`(調査完了、実装は未着手)
  5. **Evidence Compressionの日付・数字拡張の調査・STOP**: ユーザーが方向転換し日付もCompression対象とすることを決定(OPEN-84)。No.8実データを調査し、April 14(発表日)とJune 8(9ゲート開設・確認日)という8週間差の2つの暦日、および"Dallas Fort Worth International Airport"という正式名称の2回出現(初出+再言及)を確認した。どちらの日付を残すか・空港名称の2回目言及を一般化すべきかは、記事の時系列理解・fact traceabilityに影響し得る編集判断であり、「情報欠落リスクが高い」というSTOP条件に該当し得ると判断し、具体案の確定と実装(Prompt変更・No.8再生成・Fact Checker再確認)はユーザー確認後に着手することとした。**状態**: `DECIDED`(方針)/`TBD`(具体案、OPEN-84更新)
  6. **A2 In One Line速度の調査・STOP**: A2全English segmentのWPM実測(topic_intro 129〜full_story_part1 145の範囲、in_one_line 127.1)、および6% slowdown適用比率(`{name}_original.wav`との尺比較、全segment 1.056〜1.060の範囲、in_one_lineも1.0595で他と同水準)を確認した結果、in_one_lineに機械的な二重減速(style指示+time-stretchの重複適用)は起きておらず、WPMも他segmentと1〜8%の差に留まることを確認した。「体感的に遅すぎる」の原因は計測可能な機械的バグではなく、内容の性質(要約文としての強調的な話し方をTTSモデルが選択している可能性)によると考えられる。新しい具体的WPM仕様(下限値の新設等)が必要な場合は「A2速度で新しい具体WPM仕様が必要」というSTOP条件に該当するため、実装前にユーザー確認が必要と判断した(OPEN-89)。**状態**: `TBD`(調査完了、実装は未着手)
  7. **No.8完成版の再Assemble**: 上記1・2の修正を反映するため、影響segmentのみ再TTS(A2: kp2_english・meaning_1[kp1 gloss]、他の旧mandatory segmentは無料ローカル再検査でクリーン確認のみ・TTS再生成なし)し、`stage_assemble_b1`/`stage_assemble_a2`を再実行した。新設したdisfluency QA必須証跡チェック・asset hash staleness チェックを含め、Audio Validation Gateは両レベルともPASS。A2: duration 359.34秒・peak 0.854・clipping無し。B1: duration 327.51秒(ER-20から変更なし)・peak 0.825・clipping無し。ユーザー最終試聴用Artifactを同一URLへ更新。**状態**: `USER_FINAL_REVIEW`
- **regression**: 本セッションで変更した箇所に対する targeted test実行、全128件PASS(`er008_disfluency_qa_18_test_01.py`[9件、うち2件は今回の実修正に合わせて更新]・`er008_audio_validation_gate_05_test.py`・`er008_a2_slowdown_invariant_19_test_01.py`[今回のGate拡張に合わせてfixture更新]・`er008_n8_qa_hardening_21_gate_test_01.py`[新規11件]・`er003_test_v1_n3_01_tts_generate.py`・`er003_test_key_words_research10.py`[新規2件含む]・`er008_n3_01_point_qa_wiring_19_test_01.py`[新規1件・既存1件を明示的有効化へ更新]・`er008_point_regenerate_19_test_01.py`・`er006_master_audio_store_01_test.py`[新規1件])。リポジトリ全体の`unittest discover`は、実行時間・API副作用のリスクを考慮し今回は実施していない(変更ファイルとその直接依存テストのみを対象とした)
- **API call数・コスト**: kp2_english再生成でTTS 2回・ASR 2回(1回目はqa_evidence backfillのMaster Audio Store修正前に実行したため、修正後に再度manifest entryを削除し再生成し直した)、kp1_japanese_meaning(gloss修正)でTTS 1回・ASR 1回。いずれも短い単語句のTTS+ASRで、比較可能な既存segment単価(tts_a2/tts_b1ステージ実績)から1件あたり$0.001未満と推定され、合計でも$0.01を大きく下回る(cost loggerの価格テーブルがこれらのmodel_idを未収載のため厳密な$算出はできなかったが、額としては無視できる水準)。disfluency backfill(21segment再検査)はローカルfaster-whisper実行のみで追加API課金は無し。semantic consistency/Evidence Compression拡張/Writer full retryはいずれも実装していないため、これらに起因する追加コストは今回発生していない
- **既知の限界(正直に記録)**: (1) semantic consistency・Evidence Compression拡張・Point-only regenerationの恒久的な代替方式は、いずれも設計候補の提示とコスト概算に留まり、実装はユーザー確認後になる。(2) disfluency QAのMaster Audio Store cache-key自体(schema version等)は変更していないため、将来また別の新しいQA種別を追加した際、同種の「既存cache済み資産にだけ新QAが適用されない」問題が再発し得る(今回はGate側のmandatory-evidence fail-closedチェックという、原因を問わず証跡の有無で機械的に判定する汎用的な防御で対応した)
- **影響するCURRENT_SPEC項目**: 「Disfluency QA」節(資産-記録紐付けの恒久修正を追記、`PRODUCTION_WIRED`維持)、「Point One/TwoとFull Storyの意味重複検知+Point-only regeneration」節(PRODUCTION_WIRED撤回を追記)、新設「Key Phrase日本語glossの括弧書き禁止」節、「No.8完成版 再Assemble(ER-21)」節を新設
- **OPEN_ITEMSへの影響**: OPEN-85をCLOSE、OPEN-84を投資調査結果で更新(未実装のまま)、OPEN-87/OPEN-88/OPEN-89を新規追加(いずれもユーザー確認待ち)、OPEN-86は変更なし
- **状態**: 上記の通り項目ごとに異なる(`PRODUCTION_WIRED`3件、`OPEN`/`TBD`3件、`USER_FINAL_REVIEW`1件)

## ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22(2026-08-29、No.8最終品質調整)

- **背景**: ER-21でOPEN化した3件("wait"意味衝突・Evidence Compression日付拡張・Point-only regeneration恒久方式)について、ユーザーが個別に方針を確定させた。加えてA2 In One Line speedの現状維持を確認し、semantic consistencyは低優先度Open Itemとして正式化した
- **内容**:
  1. **"wait"意味衝突のNo.8個別修正**: A2「... they may fear it will be full if they wait too long.」を「... if they stay seated too long.」へ、B1「If a passenger waits too long, there may be a small chance of missing a connection and then a flight.」を「If a passenger delays joining the line, there may be a small chance of missing a connecting flight.」へ、それぞれarticle.md/parts.jsonを直接修正した。修正前にVerified Fact Ledger(`research/verified_fact_ledger.txt`)を確認したところ、該当箇所はoverhead-bin容量という一般的な心理描写であり特定のFactに紐づく数値・主張ではないこと、既存のledger_deviation.json(A2/B1とも`LEDGER_COMPLIANT`・deviation 0件)がこの文言に依存していないことを確認した。影響segmentはA2/B1とも`full_story_part1`のみで、他segmentのテキストは無変更。**状態**: `RESOLVED`(No.8個別修正、恒久QAは未実装のままOPEN-87)
  2. **semantic consistency問題の低優先度Open Item化**: ユーザーが「汎用自動QAは今回実装しない(検出精度不足・コスト・Writer model upgrade時に再検討)」と正式決定。OPEN-87を`TBD`から`OPEN(低優先度、量産非Blocking)`へ変更し、量産移行の条件ではないことを明記した。**状態**: `DECIDED`(実装見送りを正式化)
  3. **Evidence Compression Editorへ日付・数値を圧縮対象化**: `er003_v1_n3_01_evidence_compression_editor.py`の許可編集リストへ、日付・数値の削減・一般化を追加した(「日付は必ず1個」という機械的hard ruleにはしない。時系列理解・ニュースの核心・Fact特定に必要な場合は残す。判断に迷えばFact safetyを優先し残す)。No.8実データ(A2/B1)へ実際にEditorを再実行して検証した結果、EditorはApril 14(発表日)を"earlier this year"へ一般化し、June 8(9ゲート開設・確認日)は一貫して残す判断をした。ただしEditor出力には日付とは無関係な副作用(B1で"Stephen Reicher"/"Kristie Tse"という既存承認済みの実名を"one/another psychologist"へ一般化)が混在していたため、Editor出力をそのまま採用せず、日付関連の文のみ手動でarticle.md/parts.jsonへ反映した(実名は維持)。プロンプト内容テスト(`er008_n8_evidence_compression_dates_22_test_01.py`、3件)で新ルール文言と既存禁止事項の共存を確認。**状態**: `PRODUCTION_WIRED`(日付ルール追加)、No.8個別反映は完了。空港正式名称は別問題としてOPEN-84継続
  4. **"Dallas Fort Worth International Airport"正式名称が残った理由の調査**: 既存のEvidence Compression Editor prompt(許可される編集リスト)を精査した結果、対象は「出典名」(企業・調査会社・研究機関・メディア・イベント名などの引用元名)のみで、ニュースの主題そのものである地名・施設名(空港名)は元々対象カテゴリに含まれていなかったことを確認した。したがって「評価した上で必要と判断して残した」のではなく「そもそもルールの対象外だった」が結論。ユーザー指示により今回は新しい固有名詞圧縮仕様を勝手に拡張せず、調査結果の報告とA2/B1それぞれの得失(A2は"one airport"/"a major U.S. airport"で足りる可能性、B1はニュースリテラシー上正式名称を残す価値がある可能性)を提示するに留めた。**状態**: `TBD`(仕様拡張要否はユーザー確認待ち、OPEN-84継続)
  5. **A2 In One Lineのstyle確認**: `er003_v1_n3_01_tts_generate.py::generate_a2_segments()`を再確認し、A2 In One LineはFull Story Part1/2・Point One/Twoと全く同じ`A2_ENGLISH_STYLE_PREFIX_SLOWER`(通常のA2英語style)+6% slowdownの経路を通っており、B1 Preview/Comment専用の`B1_PREVIEW_STYLE_PREFIX_CALM`はA2のどのsegmentにも適用されていないことを確認した(コード変更不要、ER-21の実測結果とも整合)。ユーザーからも新しい具体的WPM下限は要求されなかったため、OPEN-89は調査完了・対応不要としてCLOSEした。**状態**: `CONFIRMED`(コード変更なし)
  6. **Point overlap NG時のWriter full retry(最大2回)を正式実装**: `er003_v1_n3_01_articles_generate.py`の`run_one_pattern()`を、Writer呼び出し+Evidence Compressionを`_generate_and_compress_article()`ヘルパーへ共通化した上で、Point overlap QAをretryループ化した(`POINT_OVERLAP_ARTICLE_RETRY_MAX = 2`)。overlapがflagされた場合、Pointだけを差し替えず記事全体をWriterから再生成し(Full Story/Point One/Point Two/In One Line間の内部整合をWriterに保たせる)、overlapが解消するかretry上限に達するまで繰り返す。再実行するのはWriter→Evidence Compression→Point overlap QAの3工程のみで、Fact Checker・Ledger Deviation Check・Directional Fact Precheckはループの外(最終確定後)で一度だけ実行するよう設計し、不要な再実行を避けた。TTSより前の工程で完結するため、このretryによるTTS/ASR追加費用は発生しない。2回retryしても解消しない場合は自動続行せず`status="NG_REVIEW_REQUIRED"`を返し、Fact Checker以降を一切呼ばない。mock LLMによる単体テスト(`er008_n8_point_overlap_article_retry_22_test_01.py`、2件)で、(a)2回目のWriter呼び出しでoverlapが解消し最終記事がarticle.mdへ保存されるパス、(b)3回とも(初回+retry2回)overlapが解消せずNG_REVIEW_REQUIREDとなり、Fact Checker/Ledger Deviationの呼び出し回数が0であるパス、の両方を確認した。No.8自体のPoint One overlap(A2 ratio=0.40、B1 ratio=0.542、既存の暫定閾値0.40でflagされる水準)には今回この新方式を適用していない(既存の承認済み記事内容を無条件に書き換えないため、monitoring記録のまま維持)。**状態**: `WIRED`(mock test確認済み、実LLM end-to-end evidenceは次にPoint overlap NGが実データで自然発生した際に確認、それまでは`PRODUCTION_WIRED`を保留、OPEN-88参照)
  7. **No.8完成版の再Assemble**: 上記1・3の修正で本文が変わった4segment(A2: full_story_part1・full_story_part2、B1: full_story_part1・full_story_part2)のみ本番生成関数(`generate_a2_segment_with_slowdown`/`news_tail_fix.generate_news_narration_wide_margin`)で再TTS・ASR再検証し、他segmentは既存のVALIDATED/HUMAN_APPROVED音声をそのまま再利用した(`er008_n8_wait_and_date_fix_retts_22.py`)。canonical_textが変わったことでer011_human_review_lock_01が自動的に「新しいsegmentのバージョン」として扱い、通常のAUTO_PROCESSINGで再生成できた(明示的なapprove_regenerateは不要だった)。この過程で2件の未発見バグを実データで発見・修正した(詳細は下記8・9)。修正後、`stage_assemble_b1`/`stage_assemble_a2`を再実行し、Audio Validation Gate(disfluency QA証跡・asset hash整合・A2 slowdown invariantを含む)は両レベルともPASS。A2: duration 357.145秒(5:57)・peak 0.90634・clipping無し。B1: duration 323.314秒(5:23)・peak 0.89835・clipping無し。ユーザー最終試聴用Artifactを同一URLへ更新。**状態**: `USER_FINAL_REVIEW`
  8. **[想定外の発見・修正] ASR検証の短縮形(contraction)誤検知バグ**: B1 full_story_part2の再生成中、TTSが自然に"They are"を"They're"と発話しただけで、3回中3回ともTRUE_CONTENT_MISMATCHと誤判定されretryが尽きてSTOPPEDになる事象を発見した。原因調査の結果、`er006_preprod_hardening_01_validation.py::normalize_text()`がアポストロフィを空白へ置換するため"they're"が"they"+"re"の2 tokenへ分かれ、canonical側の展開形"they are"の"are"は既にstopwordだが、ASR側短縮形の残骸"re"はstopword集合に無く、意味の変化が無いのに孤立したcontent_word_diffとして検出されていたことが判明した。`_STOPWORDS`へ"re"を追加して修正(実データで確認済みの範囲に限定し、"will"/"have"由来の"ll"/"ve"は別の診断[replace型diff]が必要なため今回は対象外、OPEN-90参照)。既存55件のfixture回帰(`er006_preprod_hardening_01_validation_test.py`)は全PASSのまま、新規2件のcontraction fixtureを追加。この修正はNo.8に限らず、ASR検証を使う全segment・全記事に影響する(TTSが自然な短縮形で発話するたび不要なretry/Human Reviewを起こしていた可能性がある)。**状態**: `PRODUCTION_WIRED`(共通の安全側修正)
  9. **[想定外の発見・修正] A2 slowdown post-processでsha256が再計算されていなかったバグ**: full_story_part1/2再生成後、ER-21で追加したAssemble Gateの`_segment_asset_hash_stale()`が両segmentを`ASSET_HASH_MISMATCH`でblockした。調査の結果、`apply_a2_slowdown_postprocess()`が6% time-stretchでout_pathの中身を差し替えた後、`duration_seconds`/`trim_info`は比例配分で更新していたのに`sha256`だけ取り残されており、記録されたsha256が常にslowdown前の(=もう存在しない)ファイルのものになっていたことが判明した。A2の英語body全segment(full_story/point/in_one_line、`A2_SLOWDOWN_TARGET_SEGMENTS`)がこの経路を通るため、sha256が記録されているケースは全て同じ理由でGateに引っかかりうる潜在バグだった(ただし大半の既存segmentはsha256自体が未記録[None]で、ER-21のstaleness checkは「未記録は証跡なしとしてスキップ」という設計のため、これまで顕在化していなかった)。post-process後のout_pathからsha256を再計算するよう修正し、単体テスト2件(`er008_n8_a2_slowdown_sha256_refresh_22_test_01.py`)を追加。**状態**: `PRODUCTION_WIRED`
  10. **[想定外の発見・修正] B1 full_story_part1の実在心理学者名"Stephen Reicher"のTTS発音誤り**: full_story_part1再生成後、独立した4回のASR(OpenAI Primary×2、Azure Secondary×2)すべてが一貫して"Steven Reichert"に近い形で書き起こし、`ASR_VALIDATION_UNCERTAIN`でHuman Review行きになった。既存の固有名詞発音調査機構(Pronunciation Ledger research、ER-010由来)が自動的に外部ソース(本人の発音訂正記録を含む)を調査し、正しい発音はIPA `/ˈraɪkər/`("RY-ker"、Star Trekの"Riker"と同じ発音、高確信度)と判明した。4回全てが同じ方向へ一貫して誤ったことから、単発のASR誤認識ではなくTTS自体の発音誤りである可能性が高いと判断し、ER-010の日付safe-reading("April 28"→"April twenty eighth")と同じ設計思想で、記事本文の表示用綴り(article.md/parts.json)は"Stephen Reicher"のまま変更せず、TTS入力・ASR比較対象のテキストにのみ"Reicher"→"Riker"を適用する`tts_safe_name_pronunciation_en()`を新設し`tts_safe_news_en()`へ配線した。適用後、1回目の生成で`asr_verified=True`(ASR: "Stephen Riker"、完全一致)を確認。単体テスト3件(`er008_n8_reicher_pronunciation_22_test_01.py`)を追加。**状態**: `PRODUCTION_WIRED`(実在人物名のため、念のためユーザーにも本レポートで個別に発音根拠を提示する)
- **regression**: 新規/変更テストを対象実行、全139件PASS(`er008_n8_point_overlap_article_retry_22_test_01.py`[新規2件]・`er008_n3_01_point_qa_wiring_19_test_01.py`[既存3件、影響なし確認]・`er008_n8_evidence_compression_dates_22_test_01.py`[新規3件]・`er006_preprod_hardening_01_validation_test.py`[既存55件+新規2件]・`er006_secondary_asr_01_test.py`・`er007_en_blindspot_test_01.py`・`er010_entity_phonetic_corroboration_01_test_01.py`[contraction/entity関連の既存回帰、影響なし確認]・`er008_n8_a2_slowdown_sha256_refresh_22_test_01.py`[新規2件]・`er008_n8_reicher_pronunciation_22_test_01.py`[新規3件]・`er008_a2_slowdown_invariant_19_test_01.py`・`er008_n8_qa_hardening_21_gate_test_01.py`・`er006_master_audio_store_01_test.py`・`er003_test_key_words_research10.py`・`er008_disfluency_qa_18_test_01.py`)。プロジェクト全体`run_project_regression.py`は1922件中1918件PASS(失敗4件はER-21から継続する既知の無関係な事象: 3件は「テスト総数が増えると自動的に不一致になる」既存の帳簿的meta-test、1件は無関係な日本語TTSリトライのモックテスト)
- **API call数・コスト**: (a) Evidence Compression Editor再実行(日付ルール検証用、A2/B1各1回)は実測でA2 in=1685/out=685 tokens、B1 in=1659/out=756 tokens(writer_a2/writer_b1と同じ価格帯、1回あたり$0.01未満)。(b) full_story_part1/part2再TTS・ASR(A2/B1各2segment、計4segment)は既存のnews本文segment単価(No.8実績のtts_a2/tts_b1ステージ平均$0.0005〜0.0008/件)と同水準。(c) Point overlap Writer full retryは今回No.8へ未適用のため追加コスト無し。Writer full retryの将来コスト試算(No.8実測writer_a2 $0.183/call・writer_b1 $0.185/call、A2+B1ペア基準): retry 0回=$0.368/pair(基準)、片方が1回retry=+$0.18〜0.19、両方が1回ずつretry=+$0.368、両方が上限2回retry=+$0.735。月間換算(retry率は実績が乏しいため複数シナリオで提示): 低め(20%の記事pairが平均1.3回retry、100/500/1000記事で+$9.6/$47.8/$95.7)、No.8実績相当(50%が平均1.3回、+$23.9/$119.6/$239.2)、高め(100%が上限2回、+$73.5/$367.5/$735.0)。実際の運用でPoint overlap NGが発生した際に実測retry率を記録し、この試算を更新する
- **既知の限界(正直に記録)**: (1) Point overlap Writer full retryはコード配線・mock testまでで、実LLM呼び出しによるend-to-end動作は未確認(次回の自然発生を待つ)。(2) Evidence Compression Editorは、指示範囲外のテキスト(実名等)も呼び出しごとに変わりうることが今回実データで判明したため、当面は生成結果を無条件採用せず人手で差分レビューする運用とする(Editor自体のprompt厳格化は今回のスコープ外)。(3) 空港正式名称の扱いは仕様として未確定のまま(OPEN-84)。(4) contraction誤検知バグの修正は実データで確認された"'re"(are由来)のみに限定しており、"will"/"have"由来の"'ll"/"'ve"は別型のdiff(replace型)になるため未修正のまま(OPEN-90)。(5) `_NEGATION_WORDS`に"isnt"/"dont"等アポストロフィ無しの短縮形が定義されているが、`normalize_text()`の現在のtokenize方式ではアポストロフィが空白に置換されるため、これらのtoken自体が生成されず実質的に到達不能なコードであることを調査中に発見した(否定検出という安全性の高い機能に関わるため、今回は範囲外として触れず、OPEN-90にまとめて記録する)
- **影響するCURRENT_SPEC項目**: 「Evidence Compression(方式C、Lossless Editor)」節(日付・数値ルール追加を追記)、「Point One/TwoとFull Storyの意味重複検知+Point-only regeneration」節(Writer full retry実装を追記)、「Audio Validation Gate」節(sha256再計算バグ修正を追記)、新設「ASR検証のcontraction対応」節、新設「B1固有名詞発音safe-reading(Stephen Reicher→Riker)」節、「No.8完成版 再Assemble(ER-22)」節を新設
- **OPEN_ITEMSへの影響**: OPEN-84を日付圧縮実装結果で更新(空港正式名称のみ引き続きTBD)、OPEN-87を低優先度Open Itemとして正式化、OPEN-88をWriter full retry実装結果で更新、OPEN-89をCLOSE、OPEN-90を新設(contraction"'ll"/"'ve"未対応・否定短縮形token到達不能問題)、OPEN-85/86は変更なし
- **状態**: 上記の通り項目ごとに異なる(`RESOLVED`1件、`DECIDED`2件、`PRODUCTION_WIRED`4件、`TBD`1件、`CONFIRMED`1件、`WIRED`1件、`USER_FINAL_REVIEW`1件)

## ER-008-N8-FINAL-PRODUCTION-HARDENING-23(2026-08-29、Evidence Compression地名拡張・A2 In One Line速度調査・Point overlap Writer retry実runtime検証・固有名詞発音表示ルール)

- **背景**: ER-22の残課題(OPEN-84空港正式名称、OPEN-88実runtime evidence)への対応と、ユーザー自身の試聴でA2 In One Lineの速度・Stephen Reicherの発音に新たな懸念が出たための追加調査
- **内容**:
  1. **Evidence Compression Editorへ地名・施設名の圧縮を追加**: `er003_v1_n3_01_evidence_compression_editor.py`の許可編集リストへ「学習者の理解に不要な地名・空港名・施設名等の一般化」を追加した(日付/数値と同じ「hard ruleではない、Fact safety優先」の設計)。プロンプト内容テスト`er008_n8_evidence_compression_locations_23_test_01.py`(4件)で新ルール文言・既存禁止事項との共存を確認。**No.8実データへ実際にEditorを再実行**した結果、A2/B1とも一貫して"Dallas Fort Worth International Airport"→"Dallas Fort Worth"への圧縮を提案した。この変更のみをNo.8のarticle.md/parts.jsonへ反映しようとしたところ、**適用前に必須とされたFact Check再実行でREVIEW_REQUIRED(4件の指摘)を検出**した。指摘内容を精査した結果、地名圧縮とは無関係な既存記述(「flight attendants」という帰属の妥当性、電子ゲート導入目的の因果関係の記述、2024年の別施策との混同、"safety and control"という心理学的説明の裏付け不足)であり、ベースライン(圧縮前、現行本番テキスト)のFact Check結果は`PASS`だった。ライブweb検索を伴うFact Checkは再実行のたびに結果が変動しうるため、これはEditorの地名圧縮が原因ではなく、既存記述に対するFact Checkerの非決定性(再実行時に異なるweb検索結果を拾った)である可能性が高いと判断した。ユーザー指示「Fact Check/Ledger DeviationもPASSさせる」を満たせなかったため、**article.md/parts.json/音声への適用は見送り**、候補内容を`{a2,b1b}/audit/evidence_compression_locations_23_candidate.json`に記録するのみとした。**状態**: プロンプト/ロジック自体は`PRODUCTION_WIRED`(test済み、実LLM runで意図通りの圧縮を確認、以後生成される全記事に自動適用される)。No.8自体への適用は`BLOCKED_PENDING_USER_DECISION`(OPEN-84継続、Fact Check非決定性の扱いも新たな論点として追加)
  2. **A2 In One Line速度の再調査**: コードレベルでは、A2の`full_story_part1/2`・`point_one`・`point_two`・`point_one_heading`・`point_two_heading`・`in_one_line`は全て同一の`A2_ENGLISH_STYLE_PREFIX_SLOWER`+6% slowdownを通っており(ER-22で確認済みの通り、二重減速やB1専用styleの混入は無い)、コードの原因ではないことを再確認した。一方、**実測WPM**(実ファイルのduration・実テキストの単語数から算出)では、現在本番採用中のA2 in_one_line音声は127.1 WPM(6%減速後)/134.7 WPM(減速前)で、A2の英語body segment中最も遅く、Full Story(140.5〜146.7 WPM)より明確に遅かった。ただし、**同じTTS入力テキストをそのまま2回追加生成した実測**では137.2 WPM・137.7 WPM(いずれも減速前換算で145.3/145.8 WPM相当)となり、Full Story/Point本文の速度帯(136〜147 WPM)にほぼ収まった。leading/trailing silenceのmargin(実測0.6秒程度/17秒中)はWPM差(約13〜15%)を説明できるほど大きくない。以上から、**現在の本番音声はTTS生成のrun-to-run variance(1回ごとの自然なばらつき)の中でも遅めの1回を採用してしまった結果である可能性が高く、In One Line固有の隠れた仕様や二重減速のバグではない**と判断した。B1側でもIn One Line(143.8 WPM)はFull Story(155.9〜164.1 WPM)よりは遅く、同種の傾向(短い segmentほど平均WPMが下がりやすい)がA2に限らず存在することも確認した。全segmentの実測WPM表は本ターン完了報告で提示する。**対策候補**: (a) 現状維持、(b) 複数回生成して基準WPM帯に近いテイクを採用する運用へ変更(要仕様決定・追加コスト)、(c) 短いsegment向けにWPM許容下限のGateを新設する(要仕様決定)。ユーザー指示通り**仕様変更は行わず、調査結果の提示のみでSTOP**する。**状態**: `TBD`(調査完了、対応要否はユーザー判断待ち、新規OPEN項目として記録)
  3. **Point overlap Writer full retryの実Writer/API runtime evidence取得**: ER-22はmock LLMによる制御フロー検証のみだったため、`er008_n8_point_overlap_writer_retry_realapi_23.py`を新設し、初回(attempt 0)はovarlapする既存fixture記事(無償)を与えた上で、**retry(attempt 1)には実際のOpenAI Writer API・No.8 A2で実際に使われたprompt.txt・実Verified Fact Ledgerを使用**して実行した。結果、実Writerが記事全体を1回で再生成し、Point overlap QA(決定的な字面一致率判定、LLM不使用)が新記事をoverlapなしと判定してretryループが正しく終了、その後**実Fact Checker・実Ledger Deviation Checkが実際に1回だけ呼ばれた**ことを確認した(Point-only regenerationは呼ばれず、`POINT_ONLY_REGENERATION_ENABLED=False`を維持)。この実行のコストは実測$0.7861(Writer規約再生成 約$0.11 + Fact Checker 約$0.4753[検索込み] + Ledger Deviation 約$0.2033)。この検証用に生成された記事自体はFact Check `REVIEW_REQUIRED`・Ledger Deviation 3件を返したが、これはretry機構(Point重複の解消)の検証対象外であり、通常のWriterパイプライン品質のばらつきの範疇(retry機構のバグではない)。既存のmock test(`er008_n8_point_overlap_article_retry_22_test_01.py`)と合わせ、制御フロー(mock)・実API経路(realapi)の両方でretry上限・NG時のFact Checker/Deviation未呼び出し・Point-only regenerationの不使用を確認した。**状態**: `PRODUCTION_WIRED`(実Writer/API runtime evidence取得済み、OPEN-88解消)
  4. **固有名詞発音のHuman Review表示ルールを新設・Stephen Reicher発音の再検証**: (a) ユーザーから、No.8 B1のStephen Reicher発音が現在/ˈreɪkər/(RAY-ker寄り)に聞こえるとの報告を受け、ER-22で採用した根拠(Pronunciation Ledgerのconfidence="high"、IPA `/ˈraɪkər/`)を再検証した。再調査の結果、唯一の一次情報源が英国covid公聴会の**テキスト書き起こし**(音声ではない)であり、本人が名字を訂正して名乗った事実は伝えるが発音の音そのものは伝えないこと、他の引用元の一部が別人("Steve Reich"作曲家、"Stephen Richer"米州議会議員、"Stéphane Richer"元NHL選手)を指す無関係な情報だったことが判明し、**confidence="high"は根拠不十分だったと判断**した。Pronunciation Ledgerの当該entryを`confidence="medium"`へ手動で訂正し、根拠の限界を`ambiguity_note`に追記した。一方、ER-22で実際に生成・採用された音声のASR再検証結果は"Stephen **Riker**"(意図した綴りへの完全一致)であり、もしTTSが実際に/eɪ/寄りで発話していれば通常ASRは"Raker"/"Rayker"に近い書き起こしになるはずで、この一致は現在の音声が意図通り/aɪ/寄りで発話されている可能性を支持する一定の根拠になる。**現時点では「確実に誤り」とする根拠が無いため再TTSは行わず**、この評価根拠をユーザーへ提示し、改めての試聴判断を仰ぐこととした。(b) 恒久対策として、`er006_pronunciation_research_01.py`のPerplexity調査プロンプトへ「confidence="high"は本人の音声ソースが確認できた場合のみ、テキスト書き起こしのみの場合はmedium以下」という基準を追加し、`er006_secondary_asr_01.py::evaluate_attempt_with_cascade_detail()`で、lookup/research失敗時にspanをHuman Reviewパッケージから黙って省略していた既存の欠落(silent drop)を修正し、確定不能な場合は明示的に`confidence="unconfirmed"`のentryを必ず残すようにした(ユーザー新運用ルール「IPAが確定不能ならその旨を必ず表示する」への対応)。単体テスト1件(`er006_secondary_asr_01_test.py::test_case_b_unresolved_entity_research_failure_still_reports_unconfirmed`)を追加。**状態**: 表示ルール・confidence基準は`PRODUCTION_WIRED`。Reicher個別の発音要否判断は`USER_DECISION_REQUIRED`
- **regression**: 対象テスト`er008_n8_evidence_compression_locations_23_test_01.py`(新規4件)・`er008_n8_evidence_compression_dates_22_test_01.py`・`er008_n8_point_overlap_article_retry_22_test_01.py`(既存9件、影響なし確認)・`er006_secondary_asr_01_test.py`(新規1件含む20件、全PASS)。プロジェクト全体`run_project_regression.py`は1926件中1922件PASS(失敗4件はER-22から継続する既知の無関係な事象、新規失敗なし)
- **API call数・コスト(実測)**: (a) Evidence Compression地名圧縮の候補生成(A2/B1各1回、実行のみでNo.8へ不採用)は各$0.01未満(dates-22の再実行と同水準)。(b) Fact Check/Ledger Deviation再検証(A2/B1各1回)は合計で$0.5前後(web検索7回分を含む)。(c) A2 In One Line速度検証の追加TTS生成2回は本番同等単価(1回あたり$0.001未満)。(d) Point overlap Writer full retryの実API検証1回は実測$0.7861(内訳: Writer規約再生成約$0.11、Fact Checker約$0.4753、Ledger Deviation約$0.2033)。この実測値から、ER-22で概算した将来コスト試算(retry 0回=$0.368/pair基準、片方1回retry=+$0.18〜0.19等)は同じ桁数で妥当だったことを確認した。**重要な注記**: Fact Checker・Ledger Deviation Checkはretryループの外で1回だけ実行される設計のため、retry回数が増えてもこれらのコストは増えない(増分コストはWriter[+Evidence Compression]呼び出し分のみ)。retry上限(2回)に達しNG_REVIEW_REQUIREDになった場合は、Fact Checker/Ledger Deviationが一切呼ばれないため、そのケースはむしろ成功パスよりコストが低い。月間実コストは実際の自然発生retry率のデータが無いため、ER-22の複数シナリオ試算を暫定値として維持する(実際にNGが発生し始めた時点でシナリオを実測値へ更新する)
- **既知の限界(正直に記録)**: (1) 地名・施設名圧縮ルールはプロンプト・テストまで完了しているが、No.8自体には未適用(Fact Checkの非決定性という新たな論点が浮上したため)。(2) A2 In One Line速度は原因調査のみで、対応方針は未確定。(3) Point overlap Writer full retryは実API経路で1回のみ実証しており、複数回のNG→2回目retryまで到達する実例はまだ実データで確認していない(mock testでは確認済み)。(4) Fact Checkerがライブweb検索に依存するため、同じ記事に対して再実行するたびに異なる検証結果(PASS⇄REVIEW_REQUIRED)を返しうるという非決定性が今回新たに実データで確認された。これは今回の変更が原因ではなく既存のFact Checker設計の性質だが、「Fact CheckをPASSさせる」ことを機械的な適用条件にする場合の運用上の課題として新たに記録する必要がある
- **影響するCURRENT_SPEC項目**: 「Evidence Compression(方式C、Lossless Editor)」節(地名・施設名ルール追加を追記)、「Point One/TwoとFull StoryのWriter full retry」節(`PRODUCTION_WIRED`へ更新)、新設「固有名詞Human Review表示ルール(IPA/pronunciation guide/source/confidence必須表示)」節
- **OPEN_ITEMSへの影響**: OPEN-84を更新(地名圧縮ルール自体はPRODUCTION_WIRED、No.8適用はFact Check非決定性によりBLOCKED、空港名の仕様拡張要否は引き続きユーザー判断待ち)、OPEN-88をCLOSE(実runtime evidence取得完了)、新規OPEN-91(A2 In One Line速度、TBD)、新規OPEN-92(Fact Checkerのライブ検索非決定性、TBD)を追加
- **状態**: 上記の通り項目ごとに異なる(`PRODUCTION_WIRED`3件[地名圧縮ロジック・Point overlap retry・発音表示ルール]、`BLOCKED_PENDING_USER_DECISION`1件、`TBD`2件、`USER_DECISION_REQUIRED`1件)

## ER-008-N8-FINAL-CLOSEOUT-24(2026-08-29、地名/施設名CompressionのNo.8正式反映・Writer Point Balance prompt強化・cost計算バグ修正・Stephen Reicher PASS確定)

- **背景**: ER-23で見送った地名/施設名Compression(Fact Check非決定性でBLOCKED)・Point overlap Writer retryの実測コスト($0.7861/retry)・A2 In One Line速度・Stephen Reicher発音のそれぞれについて、ユーザーが最終判断を下し、closeoutを指示
- **内容**:
  1. **地名/施設名CompressionをNo.8へ正式反映**: ユーザーが「地名圧縮自体がFact Checkエラーを起こしたものではない」と整理し、無関係なFact Check結果だけでblockしない方針を確定。`er008_n8_location_compression_24.py`を新設し、"Dallas Fort Worth International Airport"→"Dallas Fort Worth"をA2 full_story_part2、B1 full_story_part2/in_one_lineの計3箇所へ機械的に反映(該当箇所以外は無変更)。影響を受けた3segmentのみ再TTS・ASR再検証を実施し、全件`asr_verified=true`を確認した。適用後の確認Fact Check/Ledger Deviationは、A2がFact Check`REVIEW_REQUIRED`(3件)/Deviation`LEDGER_COMPLIANT`(0件)、B1がFact Check`PASS`/Deviation`LEDGER_DEVIATION`(2件)という結果だった。B1の指摘1件は編集後の文に"Dallas Fort Worth"を含んでいたため、事前に用意したキーワードスクリーン(`_mentions_edit`)が自動的にflagし、スクリプトは安全側でAssembleを一旦停止した。人手でissue本文を精査した結果、実質的な指摘は"a more controlled digital process ... has now deployed"という表現がLedgerの裏付け(設計意図・導入事実)を超えて運用効果まで確立済みであるかのように読める、という地名とは完全に無関係な既存の懸念であり(編集前の原文"at Dallas Fort Worth International Airport"でも全く同じ文構造・同じ懸念が成立する)、地名圧縮が原因で新たに発生した問題ではないと判断し、採用へ進めた。A2の3件も同様にflight attendants帰属・safety/control表現・e-gate導入目的の因果関係という、地名と無関係な既存記述への指摘だった。以上の判断根拠を`er008_output/n8_location_compression_24_summary.json`の`adoption_decision_override`に明記した上で、Audio Validation Gateを経てA2・B1を再Assemble(A2 359.7秒/B1 318.5秒、いずれもclipping無し、peak 0.91/0.90)し、完成版へ反映した。**状態**: `PRODUCTION_WIRED / CLOSED`(OPEN-84解消)
  2. **Writer Point Balance promptの強化**: `er003_v1_n3_01_articles_generate.py`のCOMMON_BLOCK_TEMPLATE内、Point One/Twoの役割を定める節へ、(a)Main Storyの中心的なlogic・結論を語彙だけ変えて再説明することの明示的禁止、(b)Pointが追加すべき内容の具体例拡張(切り口/示唆/背景/**心理/社会的含意/別の因果/実生活上の解釈**/意味づけ)、(c)「Pointを書く前にMain Storyの主要論点を特定し、それを避けて構成する」という生成手順の推奨、(d)Point One・Point Two同士が異なる役割を持つことの明示、を追加した(新Fact追加禁止・Ledger範囲内・既存の長さ目標[30-60/25-70語]は無変更)。プロンプト内容テスト`er008_n8_point_prompt_strengthen_24_test_01.py`(8件)で、新旧の禁止事項・カテゴリが両立していることを確認。**実証**: No.8の実Topic・実Verified Fact Ledgerを使い、強化前(OLD)/強化後(NEW)のprompt each 4回、実OpenAI Writer APIで新規記事を生成し(`er008_n8_point_prompt_ab_24.py`、No.8の承認済み完成稿は一切変更していない)、Point-Full Story lexical overlap率(`er008_point_overlap_qa_18.lexical_overlap_ratio`、無償・決定的なlexicalチェック)を比較した。結果: 平均overlapが0.293→0.244、overlap QA閾値(0.40)超過によるretry対象率が25%(4件中1件)→0%(4件中0件)へ低下した。サンプル数が小さい(各4件)ため統計的に確定的な結論ではないが、方向は狙い通りだった。定性的にも、OLD条件の高overlap事例(overlap=0.538)はFull Storyの電子ゲート機能説明をほぼ再掲していたのに対し、NEW条件の一例は同じFactに対し「これは航空会社自身の自己申告であり、独立した効果検証は示されていない」という一段深めた視点を新Fact追加なしで加えていた。**状態**: `PRODUCTION_WIRED`(以後生成される全記事に自動適用)
  3. **retry marginal costの訂正(cost計算モジュールのバグ修正)**: ER-23の「Point overlap retry 1回=$0.7861」という実測値を、今回のcost試算(§4のretry marginal/total分離要求)のために再検証したところ、共有のcost計算モジュール`er005_stage7_cost_compute.py::record_cost()`が、providerが"openai"のrecordを、実際に使用したmodel_id(Writer/Fact Checker/Deviation Checkは全て`gpt-5.6-luna`)に関わらず常に`gpt-5.6-sol`単価(入力$5/M・出力$30/M)で計算していたバグを発見した。`gpt-5.6-luna`の実単価は入力$0.2/M・出力$1.2/M(sol比で概ね1/25)であり、この誤りにより過去の関連コスト試算(ER-23の$0.7861、`er003_v1_n3_01_articles_generate.py`内コメントの「writer_a2単体で約$1.5」等)は実際より大幅に(生成コスト部分だけで約25倍)過大だったことが判明した。`record_cost()`をrecord自身のmodel_idに応じて価格を引き直すよう修正した(`er008_n8_cost_compute_pricing_fix_24_test_01.py`4件PASS、model_id欠落時はsol単価へfallbackする後方互換を維持)。本モジュールは現状他のどのスクリプトからもimportされておらず[grep確認済み]、修正によるリスクは無い。**正しい実測値**(No.8実データの実トークン数): Writer記事全体retry1回の純増分コスト(Writer規約再生成+Evidence Compression Editor再生成)は約$0.0049(Writer $0.0037+EC Editor $0.0012)。Fact Checker・Ledger Deviation Checkは合計約$0.107(Fact Checkerのweb検索tool手数料$0.08が大半)だが、これは記事1本につき必ず1回発生する固定costであり、retry回数を増減させても変わらない。**期待コスト再計算**: 初回Point NG率を5%/10%/25%と仮定した場合、A2+B1ペア(2 label-generation)あたりの期待増分コストは1記事につき$0.00049/$0.00098/$0.00246であり、月100/500/1000記事でも最大$0.05/$0.25/$0.49(5%)〜$0.25/$1.23/$2.46(25%)程度と、無視できる水準である(旧$0.7861ベースの試算とは全く異なる結論になる)。**状態**: cost計算ロジック修正済み・訂正後の数値をDECISION_LOG/OPEN-88へ反映
  4. **A2 In One Line速度**: ユーザーが現状維持を正式決定(TTS生成のvarianceによる遅めのテイクだった可能性が高いという前回の調査結論を受け入れ)。WPM下限Gate新設・複数テイク運用のいずれも導入せず、追加TTSも実施していない。**状態**: `DECIDED`(OPEN-91を現状維持でclose)
  5. **Stephen Reicher発音のPASS確定**: ユーザーがNo.8の実際の音声を再試聴し、「/aɪ/寄り(RY-ker)に聞こえる」と判断したため、既存音声をPASSとして確定し、再生成しなかった。Pronunciation Ledgerの当該entryへ、この確認結果と「confidenceは根拠の性質[音声ではなくテキスト書き起こし由来]を反映してmediumのまま維持する」旨をambiguity_noteへ追記した(`er006_pronunciation_ledger_01.upsert()`経由)。ER-23で新設した固有名詞Human Review表示ルール(表記・IPA・確定不能ならその旨・pronunciation guide・source・confidence)は今後も継続する。**状態**: `DECIDED`(No.8個別PASS確定)
- **regression**: `run_project_regression.py`で1938件収集・1934件PASS・4件失敗(いずれもER-23以前から継続する既知の無関係な事象[`er003_test_bad`のfixture、`er003_test_p2j_investigate`の過去カウント照合、`er007_ja_tts_retry_path_fix_test_01`]、新規失敗なし)。新規テスト16件(Point prompt強化8件、cost計算バグ修正4件、既存の`er008_n8_evidence_compression_locations_23_test_01.py`等は無変更のままPASS)は全てPASS
- **API call数・コスト(実測、正しい単価で算出)**: (a) 地名圧縮の再TTS・ASR(3segment)は本番同等単価で数セント未満。(b) 地名圧縮適用後のFact Check/Deviation確認(A2/B1各1回)は合計で約$0.21(うちFact Checkerのweb検索tool手数料が大半)。(c) Writer Point Prompt A/B比較(OLD/NEW各4回、計8回の実Writer呼び出し)は合計で約$0.03(1回あたり約$0.0037)。(d) 音声のmp3再エンコード(ffmpeg、ローカル処理、API課金なし)。合計で本ターンの追加API実費は$1未満
- **既知の限界(正直に記録)**: (1) B1のLedger Deviation指摘(2件)のうち1件は、"a more controlled digital process ... has now deployed"という表現自体への懸念であり、地名圧縮とは無関係だが、記事の表現として実際に残存する既存の技術的な過大表現の可能性があるため、将来的に別途レビューする余地がある(今回のスコープ[地名圧縮の可否判断]の対象外として扱った)。(2) Point Prompt強化の効果検証はn=4×2条件と少数サンプルであり、大規模な統計的検証ではない。(3) Fact Checkerのライブ検索非決定性(OPEN-92)自体は今回も解消していない。(4) `er005_stage7_cost_compute.py`は本来ER-005当時の解析専用モジュールであり、その後の記事生成コスト分析に流用され続けてきたことで単価バグが temporarily 実際の判断(Point-only regenerationを見送る根拠の一つ)に影響していた可能性があるが、当時の判断自体(Fact fabricationの実例が確認されたこと)は本バグと無関係な別の理由によるものであり、覆す必要はないと判断した
- **影響するCURRENT_SPEC項目**: 「Evidence Compression(方式C、Lossless Editor)」節(No.8への正式反映を追記)、「Point Balance(言い換えによる重複の禁止・強化)」節(新設)
- **OPEN_ITEMSへの影響**: OPEN-84をCLOSE(No.8への正式反映完了)、OPEN-88のcost試算を訂正、OPEN-91を`DECIDED`(現状維持で確定)、OPEN-92は`TBD`のまま維持
- **状態**: `PRODUCTION_WIRED`4件(地名圧縮No.8適用・Point Balance prompt強化・cost計算バグ修正・No.8完成版反映)、`DECIDED`2件(A2 In One Line現状維持・Reicher PASS確定)

## ER-008-N8-CLOSEOUT-GOVERNANCE-25(2026-08-29、Fact Checker retry cap調査・Production全体loop横断監査・No.8 Point overlap記録整理・cost報告円ベース化・試聴Artifact全script掲載標準化)

- **背景**: No.8完成後のProduction運用を安全にするため、ユーザーが5点のgovernance課題(Fact Checker retry cap・Production全体の無限loop候補・No.8 Point Oneの記録整理・cost報告の通貨・試聴Artifactの全script掲載義務化)を提示し、調査と必要最小限の実装を指示。No.8音声そのものはユーザー最終試聴済みでOKのため、不要な再生成は行わない方針
- **内容**:
  1. **Fact Checker retry cap調査**: `er002_ja_web_research_r3.py::run_fact_checker_with_gates()`を精査した結果、`MAX_FACT_CHECK_ATTEMPTS=2`は「初回+技術的失敗(Web検索未使用/JSON解析失敗)時のみ最大1回の技術再試行」という設計であり、**verdict(PASS/REVIEW_REQUIRED/FAIL)を理由に再試行する経路は存在しない**ことを確認した(パース成功時点でverdictに関わらず即座に確定)。Ledger Deviation Check(`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`)にはretryロジック自体が無い。ユーザー提案の基本方針「初回+retry最大2回、その後STOP」よりも現行実装の方が厳格(実質的にverdictに対しては初回で確定)であるため、**追加のcap実装は不要**と判断した。regression test`er008_n8_fact_check_retry_cap_25_test_01.py`(4件)で、PASS/REVIEW_REQUIRED/FAILいずれのverdictでも呼び出しが1回で確定すること、技術的失敗時のretry上限が引き続き機能することを固定した。**状態**: `DECIDED`(既存実装のまま安全と確認、コード変更なし)
  2. **Production全体の無限loop横断監査**: TTS(標準+fallback、A2/B1・英語/日本語全経路)、ASR Cascade、Writer技術的retry、Point overlap記事全体retry、Evidence Compression、Research/Verification、Assembly前のAudio Validation Gate、Human Review Lock、Gemini Batch jobポーリング、および全`while True`/`while not`を横断監査した。**結論: 上限が完全に無い経路は0件**(全て数値cap・壁時計timeout・単発呼び出し・線形固定長シーケンスのいずれかで有界)。Assembly Audio Validation Gateは異常時に例外で完全停止(自動retryなし)、Human Review Lockは明示的な人間承認なしに自動再処理されない設計であることも確認し、いずれも意図通りの安全設計と判断した。**発見し修正した不整合**: `er003_v1_crosslevel_audio_02_common.py::generate_text_segments()`の日本語segment分岐が、Production SSOT(`er011_human_review_lock_01.py::PRODUCTION_MAX_TTS_ATTEMPTS=3`)の2倍にあたる`max_attempts=6`をハードコードしていた(無限ではないが他の全Production call siteと不整合な独自cap)。SSOT定数を明示的に参照するよう1行修正し、regression test`er008_crosslevel_audio_02_tts_cap_25_test_01.py`で固定した。**対象外と判断したもの**: `er003_v1_a2_audio_02_generate.py::stage_generate_v2_segments()`も同じ`max_attempts=6`を持つが、Production TTS/ASR call site一覧に含まれない一回限りのKey Phrase試作用スクリプトであり、上限自体は有限のため、低優先の技術的負債としてOPEN-93へ記録し現状維持とした。`er003_v1_n3_01_tts_generate.py::generate_a2_segment_with_slowdown()`がHuman Review Lockの`RESOLVED`状態を意図的にbypassする設計(既存の文書化済み例外)についても、他のretry層との組み合わせで累積予算guardに近づく事例が無いか独立検証が済んでいないことをOPEN-94として記録した。**状態**: `DECIDED`(横断監査完了、発見した1件の不整合は修正済み、残り2件は低優先のOPENとして記録)
  3. **No.8 Point Oneの記録整理**: No.8は完成版として採用するが、記録上`Point overlap gate PASS`とは扱わないというユーザー最終判断を反映した。No.8はWriter full retry機構(ER-22〜23)導入前に生成された記事であり、現行閾値0.40を適用するとB1 Point One(ER-19時点実測overlap 0.481)が超過している。これを**No.8限定のHuman Approved exception**として`CURRENT_SPEC.md`(「Point One/TwoとFull Storyの意味重複検知+Point-only regeneration」節)へ正式記録した(英文の例外文言をそのまま記載)。No.8の出力ディレクトリ配下に「Point overlap gate PASS」等の誤った主張をするmanifest/tracking recordが無いことを確認済みのため(grep確認)、CURRENT_SPEC.md以外の追加修正は不要と判断した。今後の記事生成ではこの例外を自動適用しない(現行Productionの閾値0.40・強化済みWriter prompt・Writer全体retry最大2回・それでもNGならNG_REVIEW_REQUIREDをそのまま適用)。**状態**: `DECIDED`(No.8個別記録、将来記事への適用を明示的に禁止)
  4. **cost報告の円ベース統一**: ユーザー決定(1 USD = 160円)を`CURRENT_SPEC.md`の「コスト報告の通貨ルール」節へ正式化した。既存の`er006_pool_pilot_01_cost_time_compute.py`(`USD_JPY=160.0`)・`compute_topic_cost.py`(`USD_TO_JPY=160`)は元々同一レートを個別に使用済みだったため、共有cost計算モジュール`er005_stage7_cost_compute.py`(ER-24でmodel_id別単価バグを修正済み)へ`USD_TO_JPY=160.0`定数と`usd_to_jpy()`ヘルパーを追加し、円換算のSSOTとした(単価表・トークン集計ロジック自体は無変更)。regression test`er008_n8_cost_jpy_reporting_25_test_01.py`(4件)で、レート値そのものと、既存2スクリプトのレートとの整合を固定した。今後Claudeがユーザーへ提示するコスト(LLM/Research/TTS/ASR/retry/regeneration/月次試算/A2・B1 pair/100・500・1000記事規模)は円を主表示としドルは括弧併記とする。**状態**: `DECIDED`(SSOT新設、表示層のルール化。計算ロジック自体は変更なし)
  5. **試聴Artifactへの全script掲載標準化**: 今後ユーザーへ提示する試聴Artifactは、実際に放送される全segmentのscriptを同ページへ全文掲載することを標準仕様とした。`er003_v1_n3_01_assemble.py::build_a2_timeline()`/`build_b1_timeline()`が実際に組み立てるsegment順序をそのまま反映した必須segment一覧を`er008_listening_artifact_script_standard_25.py`(`A2_REQUIRED_SEGMENTS`/`B1_REQUIRED_SEGMENTS`、Key Phrase件数チェック込みの`check_full_script_coverage()`)として新設し、`CURRENT_SPEC.md`に新設した「試聴Artifact仕様」節から参照した。fixture test`er008_listening_artifact_script_standard_25_test_01.py`(7件)で、1 segmentでも欠落するとFAILする(A2のPoint Two除去、Key Phrase件数不足の両方を検知)ことを確認した。No.8自体の試聴Artifact(先の追加作業で全script掲載済み)はこの機械的checkへは未配線(手動確認では要件を満たしている)だが、次回以降新規に作成する試聴Artifact生成scriptはこのmoduleを使って公開前に検証すること。**状態**: `DECIDED`(標準仕様として新設、次回記事から適用)
  6. **No.8自体の扱い**: 上記1〜5はいずれもgovernance/docs/監査対応であり、No.8の音声・本文の再生成は一切行っていない(ユーザー最終試聴済みの完成版をそのまま維持)
- **regression**: `run_project_regression.py`で1954件収集・1950件PASS・4件失敗(いずれもER-24以前から継続する既知の無関係な事象[`er003_test_bad`のfixture、`er003_test_p2j_investigate`の過去カウント照合3件、`er007_ja_tts_retry_path_fix_test_01`]、新規失敗なし)。新規テスト16件(Fact Checker retry cap固定4件、crosslevel TTS capのSSOT整合1件、cost円換算4件、試聴Artifact全script欠落検知7件)は全てPASS
- **API call数・コスト(実測)**: 本ターンはコード監査・regression実行・ドキュメント更新のみで、追加の有償API呼び出しは発生していない(約0円)
- **既知の限界(正直に記録)**: (1) OPEN-92(Fact Checkerのライブ検索非決定性)自体は解消しておらず、今回の監査は「コードが機械的にPASSを狙って再試行することはない」ことを確認したのみ。(2) OPEN-93/94として記録した2件は低優先のため未修正のまま。(3) 試聴Artifact全script標準は次回記事から適用する仕様であり、No.8自体のArtifactには機械的checkを後付けで配線していない(手動確認のみ)
- **影響するCURRENT_SPEC項目**: 「Point One/TwoとFull Storyの意味重複検知+Point-only regeneration」節(No.8 Human Approved exception追記)、「Fact Checker retry cap」節(新設)、「Production全体 retry/regenerate/polling上限の横断監査」節(新設)、「コスト報告の通貨ルール」節(新設)、「試聴Artifact(ユーザー提示用ページ)仕様」節(新設)
- **OPEN_ITEMSへの影響**: OPEN-92へ監査結果を追記(`TBD`のまま維持)、OPEN-93・OPEN-94を新規追加(いずれも`TBD`・低優先)
- **状態**: `DECIDED`5件(Fact Checker retry cap現状維持・Production全体loop監査完了+1件修正・No.8 Point overlap例外記録・cost円ベースSSOT新設・試聴Artifact全script標準新設)

## ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02(2026-08-29、Ledger Deviation Checkerの過剰検知是正・Production再配線・No.9再判定)

- **背景**: No.9(pool_n9_tip_screens、実ユーザー検証用の新規統合テスト記事)で、Ledger Deviation Check(`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`)が、NYCタクシー研究の結果をレストラン全般へ広げすぎていた本物の問題(scope clarificationで修正)に加え、意味を変えないparaphrase・A2/B1向け簡略化・Evidence間のbridge sentence・一般的な情景描写までMAJORとして誤検知していることが判明した(例: `credit card transactions`→`taxi rides`という用語の言い換え、「tip screenを見た人」という母集団表現、レストラン/カフェの一般的なtip screen文脈)。ユーザーからNo.9限定の例外扱いではなく、Checker自体のProduction仕様を再設計する指示があった
- **現行Checker実態調査**: `DEVIATION_PROMPT_TEMPLATE`(v1)は「Ledgerの範囲を超える具体的Factが1件でもあればMAJOR」という粗い基準で、severity判定の根拠を構造化フィールドとして要求していなかった。DECISION_LOG過去エントリ(ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03/ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04/ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05)を確認した結果、本Checkerには以前から「実行ごとの引用のまとめ方が非決定的」「scope拡張・具体性追加型の逸脱検知を主眼とし、比較方向の反転は対象外」という既知の弱点があり、過去にも複数回`VALIDATOR_FALSE_POSITIVE`と個別判定されていたことを確認した(根本のprompt/schema自体はこれまで未修正だった)
- **新仕様の設計と検証**: `changed_fact`/`changed_scope`/`changed_causality`/`changed_certainty`/`changed_number`/`changed_actor`/`changed_negation`/`changed_comparison`/`changed_time`/`unsupported_new_claim`の10種類の意味上のFact差分のいずれかが明確にtrueの場合のみMAJORとする新schema/promptを設計した(候補実装`er009_ledger_deviation_recalibration_02.py`)。モデルがこの制約に反してMAJOR+全フラグfalseを返した場合はpost-hoc validationでMINORへ自動降格し、overall_statusはprogram側で(降格後の)MAJOR残存有無から再計算する(モデルの自己申告するoverall_statusフィールドは使わない)。No.9実データ(B1/A2)で旧判定と比較した結果、B1は3MAJOR+3MINOR→0MAJOR(paraphraseと情景描写がALLOWED化)、A2は3MAJOR→1MAJOR(taxi study自身の効果と別Evidenceのsocial pressureを因果的に混同していた「In one line」結び文、記事側の実在する軽微な問題として個別修正)へ改善した。意図的に危険な9種のfixture(数値改変・主体変更・taxi→restaurantへの直接一般化・causality強化・certainty強化・negation反転・comparison方向反転・date変更・Ledgerにない新規主張)は全てMAJOR判定を維持することを確認した(`er009_ledger_deviation_recalibration_02_test.py`、9/9 PASS)
- **Production配線**: 検証済みのprompt/schema/post-hoc validationロジックを、Production側が実際に呼び出しているSSOT(`er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`)へ直接反映した(`DEVIATION_JSON_SCHEMA`/`DEVIATION_PROMPT_TEMPLATE`/`DEVIATION_DEVELOPER_MESSAGE`をv2へ置換、`_apply_deviation_post_hoc_validation()`を新設)。関数シグネチャ・戻り値の主要キー(`parsed.deviations`/`parsed.overall_status`)は既存Production呼び出し側(`er003_v1_n3_01_articles_generate.py::run_one_pattern()`)と完全後方互換のため、呼び出し側コードの変更は不要だった。post-hoc validationロジックの受入テスト6件(`er003_v1_en_direct_vfl_01_generate_deviation_v2_test.py`、API呼び出し不要)を追加し全PASSを確認した
- **No.9本文への反映と最終再判定**: A2の「In one line」結び文(taxi studyの効果とsocial pressureの混同)、B1の「the first option on the screen influenced the final choice」(研究が直接検証していない「画面最初の選択肢」という特定メカニズムへの過剰な具体化、Fact Checkerが独立に指摘していたのと同種の懸念)をそれぞれ最小限の言い換えで修正した。Production配線後の`run_deviation_check()`をNo.9 B1/A2へ実際に適用し、B1・A2とも**LEDGER_COMPLIANT(MAJOR 0件)**を2回連続の再実行で確認した(非決定性への配慮として1回だけでなく再実行で安定性を確認)。Point overlap QA・Fact Checkerも修正後の本文で再確認し、Point overlapは両levelとも非flagged(維持)、Fact Checker verdictは両levelともscope clarification前から変わらず`REVIEW_REQUIRED`(研究が直接検証したメカニズムの具体性に関する同種の解釈的指摘のみ、契約上のSTOP条件である`FAIL`ではない)
- **QCD差分**: Quality — 過剰検知(false positive)はB1で3件→0件、A2で3件→0件(該当箇所を個別修正後)に解消し、危険な改変への検知(true positive)は9/9 fixtureで維持。Cost — 同一model(`gpt-5.6-sol`)・同一reasoning effort(`high`)で1回あたりの単価は無変更、今回の検証(候補比較2回・fixture9回・No.9最終再判定/安定性確認/Point overlap・Fact Checker再確認)で発生した追加API呼び出し分のみコストが増加(下記参照)。Delivery — No.9はLedger DeviationによるSTOPが解消(この回のみの実測、他テーマへの一般化は未検証)
- **今回実施しなかったこと**: 既存22テーマへのv2 Checkerでの遡及再判定(過去のEvidence Compression Production採用時と同じ方針で、必要になったテーマのみ個別対応とし一括再監査は行わない)、比較方向反転検知の統合(既存のDirectional Fact Precheck[ER-008-08]で別ゲートとして担保済み、今回はスコープ外)、Fact Checkerが独立に指摘し続けている「アンカリング/心理的メカニズムの具体性」ニュアンスの完全解消(REVIEW_REQUIREDのまま許容、契約上のSTOP条件に該当しないため深追いしない)
- **API call数・コスト(実測+見積り)**: ログ記録済み(`cl.install()`使用)分は本タスク後半の最終再判定・安定性確認・Point overlap/Fact Checker再確認で20レコード、$0.60964(約**97.5円**)。これとは別に、候補実装での比較検証(No.9 B1/A2各1回+A2修正後再確認1回)と9種類のfalse negative fixture検証(計12回のAPI呼び出し)は、検証用スクリプトに`cl.install()`を呼び出し忘れており**ログに記録されていない**(過去のER-009-N1-SCOPE-CLARIFICATION-01作業時と同種のミス、詳細は完了報告で開示)。同程度の単価から見積もると追加で**約55〜65円程度**、本タスク全体では概算**150〜165円程度**(不確実性を含む見積り)
- **既知の限界(正直に記録)**: (1) 過去に指摘されていたLedger Deviation Checkの実行ごとの非決定性はv2でも解消されていない(今回は同一記事に対する2回の安定した一致で個別に確認したのみ)。(2) 既存22テーマは旧v1判定のまま未再監査であり、v2での結果が変わる可能性がある(次に該当テーマを扱うタイミングで個別対応)。(3) 検証用スクリプトのコストログ漏れが今回も再発しており、恒常的な対策(検証スクリプトの共通テンプレート化等)は未実装のままOpen Itemとして残す
- **影響するCURRENT_SPEC項目**: 「Ledger Deviation Checker v2(判定基準の再設計)」を新規行として追加(`PRODUCTION_WIRED`)。「Fact Safety(共通)」の既存行は無変更
- **OPEN_ITEMSへの影響**: 既存22テーマへのv2遡及監査、検証用スクリプトのコストログ漏れ再発防止を、いずれも`LOW / Non-blocking`のOpen Itemとして記録(次回の関連タスクで対応可否を判断)
- **状態**: `PRODUCTION_WIRED`(prompt/schema更新・post-hoc validation実装・受入テスト6件+false negative fixture 9件全PASS・No.9実データでの改善確認・CURRENT_SPEC/DECISION_LOG反映まで完了)

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[CURRENT_SPEC.md](CURRENT_SPEC.md)、
[HISTORY_INDEX.md](HISTORY_INDEX.md)、[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)
