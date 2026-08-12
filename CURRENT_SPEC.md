# CURRENT_SPEC — 現在有効な正式仕様

**管理ID: ER-PM-001**
**最終更新: 2026-08-12(ER-003-A2-SPEC-FREEZE-01)**

このファイルには、**現在正式に採用されている仕様だけ**を書く。経緯・
比較検討・却下案は書かない(→[DECISION_LOG.md](DECISION_LOG.md)/
[HISTORY_INDEX.md](HISTORY_INDEX.md))。未確定事項は書かない
(→[OPEN_ITEMS.md](OPEN_ITEMS.md))。

各項目は最低限、**管理ID／現在値／状態／根拠Decision／最終更新日**を持つ。

---

## Product(番組仕様)

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| サービス名 | English Your Way | `DECIDED` | ER-003-B1-P9A系 | 2026-08-07 |
| 対象ユーザー | 日本語話者の英語学習者(リスニング中心) | `DECIDED` | ER-003-B1系 | 2026-08-07 |
| 番組構成(19パート) | Intro→Welcome→Topic Intro→Japanese Title→notification1→Preview Intro→Point解説→Preview→notification2→Key Phrases Intro→Key Phrase×5→notification3→Full Story Intro→Full Story→Outro | `DECIDED` | ER-003-REPRO-01/02(A02・ADD03で再現確認済み) | 2026-08-09 |
| Key Phrasesセクション構成 | 番号→英語→日本語訳→英語(反復) | `DECIDED` | ER-003-B1-P9A系 | 2026-08-07 |

## CEFR(A2 / B1 / B2 比較)

| 項目 | CEFR-A2 | CEFR-B1 | CEFR-B2 |
|---|---|---|---|
| status | `DECIDED`(2026-08-12、ER-003-A2-SPEC-FREEZE-01。詳細経緯は[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)) | `DECIDED` | `DECIDED`(テキストのみ。音声化は[OPEN_ITEMS](OPEN_ITEMS.md)参照) |
| vocabulary | 可能な範囲で平易な一般語を優先(定性的方針)。**厳密なCEFR語彙数上限・wordlistは意図的に設けない**(正式wordlist不在でLLM判定が不安定なため、数値ルール化は`REJECTED`) | 定性的指示のみ("mostly common, everyday vocabulary... a B1 learner already knows")、wordlist参照コードなし | 定性的指示のみ("主に一般的なB2以下の語彙")、wordlist参照コードなし |
| 平均文長 | 11語以下(生成方針。B1/B2同様、機械的gateとしては未実装) | ≤15語(`B1_TARGET_AVG_WORDS_PER_SENTENCE`、**診断のみ、gateではない**) | ≤19語(`B2_MAX_AVG_WORDS_PER_SENTENCE`、**実際のgate**) |
| 最長文 | 18語以下(生成方針) | 24語(`B1_MAX_SENTENCE_WORD_COUNT`、診断のみ) | 32語(`B2_MAX_SENTENCE_WORD_COUNT`、実際のgate) |
| 全体語数 | 上限なし。**総語数を意図的に削らない**(B1と同等程度の主要情報量を保持) | 上限なし(明示的にhard limitを設けない設計) | 上限なし(記録のみ、gateなし) |
| 1文1アイデア | 原則1文1メッセージ | 定性的指示あり("Prefer one idea per sentence") | 規定なし |
| 等位接続・従属節 | 関係詞節は原則回避、分詞構文を避ける、複雑な受動態を避ける | 定性的指示のみ("avoid long subordinate clauses")、数値上限なし | 規定なし |
| 関係詞 | 原則回避 | 規定なし | 規定なし |
| 受動態 | 複雑な受動態は避ける(単純な受動態は許容) | 規定なし | 規定なし |
| 完了形・進行形 | 完了形等の複雑構造は必要最小限 | 規定なし | 規定なし |
| 助動詞 | 規定なし | 規定なし | 規定なし |
| 固有名詞 | 密度低減の数値目標は設けない(`REJECTED`、通常の編集判断に委ねる) | 保持可(周辺文は簡単に) | 理解に必要な場合のみ |
| 数字・金額・日付・% | 原則1文1数字。年齢範囲・スコア・時間帯・日付(月+日+年)は1つの意味単位として例外扱い | CEFR別の簡略化ルールなし(音声制作段階のMFA/ASR対応のみ) | 同左 |
| 専門語 | 規定なし(B1に準ずる想定) | 理解に必要なら保持可 | 理解に不可欠なら残してよい |
| タイトル | 固定構造(`# Title`)のみ、CEFR別の語数・語彙制限なし | 固定構造(`# Title`)のみ、CEFR別の語数・語彙制限なし | 同左 |
| 生成元 | Natural English Sourceから独立生成(B1/B2本文を入力にしない) | Natural English Sourceから独立生成 | Natural English Sourceから独立生成 |
| Spoken-first | `ADOPTED`。主語・動詞を早く出す、長い前置詞句・名詞句を文頭に置きすぎない、文末まで聞かないと意味が確定しない構造を避ける。厳格なsyntax validatorにはしない(style原則として運用) | 規定なし | 規定なし |
| Full Storyの役割 | Full Storyだけでニュースの核心が分かる。Point One/Twoは深掘り・背景・意味付けとし、Full Storyの代替にしない | 規定なし(Full Story=本編そのもの) | 規定なし |
| 本文品質要件 | **Simple AND Natural**(平易さと自然さを両立、どちらかを犠牲にしない) | 規定なし | 規定なし |
| Naturalness QA | 本文生成後、独立工程としてGrammar/Idiomaticity/News narration naturalness/Meaning preservation/A2 suitability/Spoken-firstの6観点を確認する方針を採用(`PASS`/`REVISE`/`HUMAN_REVIEW`、大規模自動化は未実装、詳細は本ファイル「A2構造・音声」節) | 規定なし | 規定なし |

根拠: `er003_v1_translator_briefs/b1_p1_prompt_template.txt`、
`er003_b1_article.py`、`er003_v1_translator_briefs/b2_adapter_prompt_template.txt`、
`er003_b2_adapter.py`、[ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md)(2026-08-09)、
ER-003-A2-01〜03・ER-003-A2-STRUCT-02〜05・ER-003-A2-SPEC-FREEZE-01(2026-08-12)。

**`levels.py`のA2/B1/B2数値(vocab 1,000語/620-700語等)は、
`generate_test.py`/`tts_test.py`という無関係な別番組専用の値であり、
このCEFR表には一切採用していない。**

## CEFR-A2 構造・音声仕様

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 全体構造(11パート) | Preview→Key Phrases→Comment1→Full Story Part1→Comment2→Full Story Part2→Comment3→Point One→Point Two→Comment4→In One Line | `DECIDED` | ER-003-A2-STRUCT-02〜04、ER-003-A2-SPEC-FREEZE-01 | 2026-08-12 |
| Comment 1の役割 | Listening Focus(次に何を聞くかを示す、答えは言わない)。長さ目安: 原則1文 | `DECIDED` | 同上 | 2026-08-12 |
| Comment 2の役割 | Mid-story Recovery + Next Question(Part1の要点を1点回収し、Part2への問いを提示)。長さ目安: 1〜2文 | `DECIDED` | 同上 | 2026-08-12 |
| Comment 3の役割 | Story Meaning + Bridge to Points(Full Story全体の論点整理、Pointsへの橋渡し)。長さ目安: 2〜3文 | `DECIDED` | 同上 | 2026-08-12 |
| Comment 4の役割 | Point Recovery + Bridge to In One Line(Pointsの意味を回収しIn One Lineへつなぐ)。長さ目安: 2〜3文。「英語一文でまとめます」とは言わず、実際の3文構成と整合する自然な文言を使う | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-01、ER-003-A2-SPEC-FREEZE-01 | 2026-08-12 |
| Comment文言の一般化範囲 | 役割・判断基準のみを一般化し、具体的な文言は記事ごとに新規作成する(A02の文言をA01/ADD03へ機械的に流用しない、3記事で重複文言ゼロを確認済み) | `DECIDED` | ER-003-A2-STRUCT-04 | 2026-08-09 |
| Full Story分割 | 機械的な50:50分割は禁止。原則2ブロック。分割位置の優先順位: ①意味上の転換点 ②時系列上の転換点 ③問題→例外 ④発表→反応 ⑤What happened→What happened next / Why it matters | `DECIDED` | ER-003-A2-STRUCT-02〜04 | 2026-08-09 |
| In One Lineの構成 | 中心1文(要約)+英語の短い補足2文程度(B1相当のセクション密度)。「In One Line」は中心1文を指す語で、セクション全体を1文に限定しない。補足文はFull Story/Points既出情報のみを使い、新規factを追加しない | `DECIDED` | ER-003-A2-STRUCT-05 | 2026-08-09 |
| In One Line見出しのTTS | 見出し文字列("In One Line")を実際にTTS inputへ含めて発話させる(Point One/Twoと同じ方式)。instructionのみで発話させる方式は不使用 | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-04(3/3で安定動作確認)、ER-003-A2-AUDIO-AB-01(完成音声で確認) | 2026-08-12 |
| A2英語ナレーション速度 | 約135 WPMを**目安**として採用(hard constraintではない)。対象: Full Story Part1/2・Point One/Two・In One Lineの英語segmentのみ(日本語・Key Phrase・効果音・無音は除外)。数値達成のため不自然な間・単語単位の発話・pitch/rhythm崩壊を起こさない。segmentごとのWPMばらつきは許容し、最終的な自然さはユーザー試聴を優先する。制御手段はTTS自身の明示的speed parameterが存在しないため、prompt/style instructionによる誘導を使用(post-processing time-stretchは未使用)。**同一instructionでもsegmentごとに反応が異なり、指示を強めても必ずしも遅くならない(非単調)ことを確認済み** | `DECIDED`(目安として) | ER-003-A2-AUDIO-AB-01(A02でA/B比較、ユーザー承認) | 2026-08-12 |
| B1/B2音声速度 | 現行の自然な読み上げ速度を維持。明示的なWPM targetは新設しない | `DECIDED` | ER-003-A2-SPEC-FREEZE-01(ユーザー判断) | 2026-08-12 |
| Naturalness QAフロー | `A2生成 → 独立したNaturalness QA(Grammar/Idiomaticity/News narration naturalness/Meaning preservation/A2 suitability/Spoken-firstの6観点) → 必要箇所のみ修正 → re-QA`。判定は`PASS`/`REVISE`/`HUMAN_REVIEW`の3状態。生成モデル自身への自己確認にはしない(生成とQAを分離する) | `DECIDED`(方針として。大規模自動実装はまだ) | ER-003-CROSSLEVEL-AUDIO-04、ER-003-A2-SPEC-FREEZE-01 | 2026-08-12 |
| Key Phrase選定(A2) | A2最終本文から改めて選定する(B1 Key Phraseの機械的流用はしない)。方式は既存のStrategy L(Listening Blocker Ranking)+Canonicalization+minimum sufficient+semantic safeguardsをそのまま使用(A2専用の新方式は作らない) | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-02(A01/ADD03で新規選定を実施) | 2026-08-10 |

## Cross-level仕様(A2/B1/B2共通)

以下はA2の検証で発見・試作したが、**特定レベル固有ではなく番組全体
(A2/B1/B2)に適用する編集・音声品質原則**として正式化したもの。
既存のB1/B2完成音声を今回一括で再生成することはしない。今後の新規
生成・再assemble時から適用する。

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| Preview原則 | ニュース全体のテーマ・問題意識・聞く価値・最後まで聞きたくなる問いを示す。後続本文で聞かせたい具体的な答え・詳細な数字・重要な転換点や結論を先出ししない。A2ではComment1/2がListening Focusとして機能するよう、Previewとの情報重複を特に避ける | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-01/02(A01/A02/ADD03の3記事で再現確認)、ER-003-A2-SPEC-FREEZE-01 | 2026-08-12 |
| Key Phrase発音品質(3条件) | 以下3条件を同時に満たす: (1) Meaning/contextual prosody(本文での意味に合ったイントネーション・stress) (2) Phoneme integrity(語末子音等の必要音素を自然に保持) (3) Phrase grouping(単語ごとに分断せず1つの意味単位として自然に読む)。個別単語パッチではなくこの共通原則で生成する。機械QAだけで自然さPASSとせず、主観的音声品質はユーザー判断を最終とする | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-04(Come on/Go ahead/Brent crude oil)、ER-003-A2-AUDIO-AB-01(A02の5件へ適用、ユーザー承認)、ER-003-A2-SPEC-FREEZE-01 | 2026-08-12 |
| 英語見出しのTTS方式 | Point One/Point Two/In One Line等の英語見出しは、見出し文字列そのものをTTS inputへ渡し、英語として自然に読ませる。「見出しを渡さずinstructionだけで発話させる」方式は使用しない | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-04 | 2026-08-12 |
| ポーズ(「ポイント解説」→Preview) | 0.7秒 | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-01/02(3記事で再現) | 2026-08-12 |
| ポーズ(Point One→Point Two) | 0.8秒 | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-03提案、ER-003-A2-AUDIO-AB-01で実装・確認 | 2026-08-12 |
| ポーズ(In One Line→Outro) | 0.8秒 | `DECIDED` | 同上 | 2026-08-12 |
| ポーズ(A2 Comment、英語→日本語) | 1.0秒 | `DECIDED` | ER-003-A2-AUDIO-01以降、無変更 | 2026-08-12 |
| ポーズ(A2 Comment、日本語→英語) | 0.8秒 | `DECIDED` | 同上 | 2026-08-12 |
| Comment前後の効果音 | 専用効果音は入れない(ポーズのみ) | `DECIDED` | ER-003-A2-AUDIO-01以降、無変更 | 2026-08-12 |
| Outro音量 | 最新の減衰方針(Introへのgain matching後、心理音響ベースの追加減衰を2段適用、単純な振幅比ではなく人間聴覚上のバランスを優先)を共通mix ruleとして採用。既存B1/B2完成音声は一括再生成しない | `DECIDED`(方針として) | ER-003-CROSSLEVEL-AUDIO-01〜04、ER-003-A2-AUDIO-AB-01、ER-003-A2-SPEC-FREEZE-01 | 2026-08-12 |

これらのポーズ・共通定数は、現状B1組立スクリプト側で記事ごとに
個別定義されている(一元化された共通定数モジュールはまだない)。
共通定数化そのものは今回のスコープに含めない([OPEN_ITEMS.md](OPEN_ITEMS.md)参照)。

## Key Phrase

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 選定方式 | Strategy L (Listening Blocker Ranking) | `DECIDED` | ER-003-P2I(commit `e33f227`) | 2026-07-xx |
| 件数 | 5件/記事 | `DECIDED` | ER-003-P2I | 2026-07-xx |
| 語数範囲 | 1〜5語(`key_phrase`) | `DECIDED` | ER-003-KP-02-R1(commit `5a94db0`) | 2026-08-08 |
| 選定元 | 各記事自身のCEFR-B1本文(承認済み) | `DECIDED` | ER-003-REPRO-01-KP(commit `46aa2e8`) | 2026-08-08 |
| 後処理 | Pedagogical Phrase Canonicalization(`source_span`→`display_phrase`→`key_phrase`→`used_form`) | `DECIDED` | ER-003-KP-01(commit `e607d26`) | 2026-08-08 |
| Canonicalization原則 | 「最小」ではなく「最小十分」 | `DECIDED` | ER-003-KP-02(commit `8856264`) | 2026-08-08 |
| QAモデル | 3状態(`CANONICALIZATION_PASS`/`REVIEW_REQUIRED`/`INVALID`)、11 QAフィールド | `DECIDED` | ER-003-KP-01→KP-02→KP-02-R1 | 2026-08-08 |
| Traceability定義 | 「source_spanから説明可能な正規化で導出できる」こと。文字通りの部分文字列一致は不要 | `DECIDED` | ER-003-KP-02-R1 | 2026-08-08 |
| human review条件 | いずれかのQAフィールドがFAILならREVIEW_REQUIRED、自動retryなし、人間承認で採用可 | `DECIDED` | ER-003-KP-01→KP-02 | 2026-08-08 |
| `used_form`/`key_phrase`の関係 | 現状100%重複(技術的負債として記録、整理はしない) | `DECIDED`(整理しない方針が決定事項) | ユーザー指示(2026-08-08、KP-02-R1承認時) | 2026-08-08 |

## Preview

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 言語 | 日本語のみ | `DECIDED` | ER-003-B1-P9A-R1(英語Key Phrase埋め込み方式は不採用) | 2026-08-07 |
| TTS model | `gemini-3.1-flash-tts-preview` | `DECIDED` | ER-003-B1-P7A(commit `b4f871f`) | 2026-08-06 |
| 採用理由 | 旧モデル(2.5)で「激しい」→「げきせつな」等の誤読が発生し、3.1で解消を確認 | `DECIDED` | ER-003-B1-P7A | 2026-08-06 |
| voice | Aoede | `DECIDED` | ER-003-B1-P7A以降 | 2026-08-06 |
| 生成方式 | 単一TTS call(chunk分割なし) | `DECIDED` | ER-003-B1-P7A | 2026-08-06 |
| Key Phrase埋め込み | しない(Full Story側のみで扱う) | `DECIDED` | ER-003-B1-P9A-R1以降 | 2026-08-07 |
| モデル分離 | Preview(3.1)とFull Story(2.5)の設定を分離、片方の変更が他方に波及しない設計 | `DECIDED`、`ModelIsolationTests`で固定確認済み | ER-003-B1-P8A | 2026-08-07 |
| 承認フロー | ①台本(日本語テキスト)をチャットで提示→ユーザー承認→②その台本のまま音声生成→③音声試聴→ユーザー承認。台本確定後の勝手な再生成・変更はしない | `DECIDED` | ER-003-REPRO-01/02-PREVIEW系 | 2026-08-08〜09 |

## Full Story

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| TTS model | `gemini-2.5-pro-preview-tts` | `DECIDED`(凍結仕様) | ER-003-B1-P4D〜P8A | 2026-08-06以前 |
| voice | Aoede | `DECIDED` | 同上 | 同上 |
| chunk構成 | 3chunk | `DECIDED`(凍結仕様) | ER-003-B1-P4D〜P8A | 同上 |
| 内容QA retry | 3試行1セット(`run_tts_content_attempts`) | `DECIDED` | ER-003-B1-P8A系 | 2026-08-07 |
| 短文ナレーション生成 | 前後文脈のない短いフレーズは専用の最小限instructionで生成 | `DECIDED` | ER-003-B1-P9A-R1(commit `d41e4fe`) | 2026-08-07 |
| strict ASR検証 | 部分一致 + ASR文字数上限(期待文字数+少数の余裕)の両方を確認 | `DECIDED` | A02 meaning_5発見を機に追加 | 2026-08-08 |
| minimal instruction fallback | 標準経路が規定回数不合格の場合、最小限instructionへ自動フォールバック(短文ナレーション・英語Key Phrase Componentの両方に適用) | `DECIDED` | ER-003-REPRO-01-MAIN | 2026-08-08 |
| Dynamics処理 | **不使用**(scalar gainのみ、compressorやDynamics3は使わない) | `DECIDED` | `er003_b1_p9a_audio.py`にコード内コメントで明記 | 2026-08-07 |

## Audio Assembly

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 複数箇所編集の順序 | 時系列で**後ろから前へ**適用(insert2→insert1→title_trim等) | `DECIDED` | ER-003-B1-P7C(バグ発見)〜P9A-R1/R2で徹底 | 2026-08-07 |
| 境界検出 | MFA(Montreal Forced Aligner)を優先、RMSは補助のみ | `DECIDED` | プロジェクト全体方針(P3W以降) | - |
| 数字・日付境界 | MFA単独で確定せず、必ずASRまたは他の診断で裏付ける | `DECIDED` | ER-003-B1-P9A-R2("England 1–2 Argentina"語順バグを機に確立) | 2026-08-07 |
| notification2挿入 | Full Story内2箇所(Today's Points直前、In One Line直前) | `DECIDED` | ER-003-REPRO-01/02-MAIN | 2026-08-08〜09 |
| 音量調整 | scalar RMS基準(Preview/Bodyは無調整のアンカー、他要素は平均RMSへ、OutroはIntro基準RMSへ一致)。A01のみ追加の聴感補正(約-5.85dB)を適用、A02/ADD03には適用していない | `DECIDED` | ER-003-B1-P9A系/ER-003-REPRO-01-MAIN | 2026-08-07〜08 |

## QA / Human Review

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| ASR診断 | Azure STT(`en-US`/`ja-JP`)を全内容確認・境界検証に使用。決定はASRだけで下さない | `DECIDED` | プロジェクト全体方針 | - |
| hallucination対応 | strict検証+minimal instruction fallbackで自動検出・自動吸収(A02で2件実績)。**根本原因は未解明のまま** | `DECIDED`(運用方針)、原因は`UNDER_REVIEW`ではなく未解明のまま保留 | ER-003-REPRO-01-MAIN | 2026-08-08 |
| ASR homophone ambiguity対応 | strict検証が規定回数不合格でも、TTS自体が正常な可能性がある場合はretryを打ち切り、`PROVISIONALLY_ACCEPTED_REQUIRES_HUMAN_REVIEW`→ユーザー試聴後`ACCEPTED_AFTER_HUMAN_REVIEW`という2段階の人間確認フローを使う | `DECIDED`(ADD03 meaning_3で初適用・確定) | ER-003-REPRO-02-MAIN/FINAL | 2026-08-09 |
| 最終人間試聴 | 機械QA全合格でも「完成」「量産再現性合格」とは判断せず、必ずユーザー試聴を経る | `DECIDED` | 全ステージで一貫 | - |
| 量産再現性判定 | A. 量産候補として採用可能(A02・ADD03の2記事連続成功に基づく)。ただし完全自動化ではなく最終人間試聴を必須ゲートとして維持 | `DECIDED` | ER-003-REPRO-FINAL(commit `c4a762c`) | 2026-08-09 |

## 参照元

[ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md)、
[ER-003-B2-AUDIT-01_SPEC_AUDIT.md](ER-003-B2-AUDIT-01_SPEC_AUDIT.md)、
[ER-003-REPRO_BASELINE.md](ER-003-REPRO_BASELINE.md)、
[ER-003_PIPELINE_CROSS_CUTTING_RULES.md](ER-003_PIPELINE_CROSS_CUTTING_RULES.md)、
[ER-003-B1_P8A-P9A_AUDIT_REPORT.md](ER-003-B1_P8A-P9A_AUDIT_REPORT.md)、
[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)(A2の検証経緯、CURRENT_SPEC昇格後は履歴記録として保持)、
[ER-003-CROSSLEVEL-AUDIO-01_REPORT.md](ER-003-CROSSLEVEL-AUDIO-01_REPORT.md)、
[ER-003-CROSSLEVEL-AUDIO-02_REPORT.md](ER-003-CROSSLEVEL-AUDIO-02_REPORT.md)、
[ER-003-CROSSLEVEL-AUDIO-03_REPORT.md](ER-003-CROSSLEVEL-AUDIO-03_REPORT.md)、
[ER-003-CROSSLEVEL-AUDIO-04_REPORT.md](ER-003-CROSSLEVEL-AUDIO-04_REPORT.md)、
[ER-003-A2-AUDIO-AB-01_REPORT.md](ER-003-A2-AUDIO-AB-01_REPORT.md)、
[ER-003-A2-SPEC-FREEZE-01_REPORT.md](ER-003-A2-SPEC-FREEZE-01_REPORT.md)、
[DECISION_LOG.md](DECISION_LOG.md)
