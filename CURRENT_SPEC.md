# CURRENT_SPEC — 現在有効な正式仕様

**管理ID: ER-PM-001**
**最終更新: 2026-08-28(ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15、TTS retry上限3回化・固有名詞ASR判定のPronunciation Ledger本番配線・日本語表記ゆれのCascade内自動PASS追加・英語homophone対策新設)**

このファイルには、**現在正式に採用されている仕様だけ**を書く。経緯・
比較検討・却下案は書かない(→[DECISION_LOG.md](DECISION_LOG.md)/
[HISTORY_INDEX.md](HISTORY_INDEX.md))。未確定事項は書かない
(→[OPEN_ITEMS.md](OPEN_ITEMS.md))。

各項目は最低限、**管理ID／現在値／状態／根拠Decision／最終更新日**を持つ。

---

## Product(番組仕様)

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| サービス名 | English Your Way | `DECIDED`(2026-08-17再確認: 現行B1コード`er003_v1_sing01_voice01_generate.py`のWelcomeナレーション文言"Welcome to English Your Way."で継続使用を確認、改称の証拠なし) | ER-003-B1-P9A系 | 2026-08-07 |
| 対象ユーザー | 日本語話者の英語学習者(リスニング中心) | `DECIDED` | ER-003-B1系 | 2026-08-07 |
| 番組構成(19パート) | `HISTORICAL`(P-series、Point構造導入前のシェル)。Intro→Welcome→Topic Intro→Japanese Title→notification1→Preview Intro→Point解説→Preview→notification2→Key Phrases Intro→Key Phrase×5→notification3→Full Story Intro→Full Story→Outro。**Comment 1〜4・Point One/Two・Point Notification・In One Lineを含んでおらず、現行の11-part content構造+Point Notification/Voice構成とは一致しない。** 現行の全体構成は本ファイル内の複数箇所(CEFR-A2/B1構造・音声仕様節の11パート構造、B1 Voice構成節、Cross-level仕様節のPoint Notification/pause各項目)に分散して記載されており、単一の更新済みN-part一覧はまだ存在しない(2026-08-17 SoT Consistency Cleanupで判明、統合は今回のスコープ外) | ER-003-REPRO-01/02(A02・ADD03で再現確認済み、ただしPoint構造導入前) | 2026-08-09(`HISTORICAL`化: 2026-08-17) |
| Key Phrasesセクション構成 | 番号→英語→日本語訳→英語(反復) | `DECIDED` | ER-003-B1-P9A系 | 2026-08-07 |

## CEFR(A2 / B1 / B2 比較)

**注意(2026-08-17追記、ER-003-B1-A2-SPEC-FREEZE-01/SCOPE-FIX-01)**: 下表の
CEFR-B1列は、A01/A02/ADD03(P-series)で使われた初期の「B1専用簡略英文」
設計を記録したものであり、**現在のProduction標準ではない**。B1の現行
正式仕様は、Verified Fact LedgerからB1専用Writerで独立生成した
natural spoken news English(B2と同一テキストではなく、B2よりlistening
loadを下げつつA2ほど強くは簡略化しない独自の本文)+Support
(Preview/Comment1-4)の言語・役割で作る設計へ更新された(下記
「B1(独立生成Natural Spoken News English)」節を参照)。下表のCEFR-B1列は
`HISTORICAL`として保持し、既存のP-series記事(A01/A02/ADD03のCEFR-B1)の
記録としてのみ有効とする。

**LAUNCH_SCOPE(2026-08-17、ER-003-B1-B2-SCOPE-FIX-01)**: 初期Launchの
対象レベルは**A2/B1の2レベル**であり、**CEFR-B2は`OUT_OF_INITIAL_SCOPE`**
(初期サービス中核から外す。廃止ではなく、future expansion candidate /
internal comparison・reference / historical experiment・referenceという
位置づけへ変更。詳細はDECISION_LOGの該当Decisionを参照)。下表のCEFR-B2列は、
研究・比較参照用の記録として保持する。

| 項目 | CEFR-A2(`LAUNCH_SCOPE: IN`) | CEFR-B1(`HISTORICAL`、P-series専用。現行B1仕様は下記節を参照。`LAUNCH_SCOPE: IN`) | CEFR-B2(`LAUNCH_SCOPE: OUT_OF_INITIAL_SCOPE`) |
|---|---|---|---|
| status | `DECIDED`(2026-08-12、ER-003-A2-SPEC-FREEZE-01。詳細経緯は[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)) | `DECIDED` | `DECIDED`(テキストのみ。初期Launch対象外。音声化は[OPEN_ITEMS](OPEN_ITEMS.md)参照) |
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
| 生成元 | `HISTORICAL`表記に注意: 「Natural English Source」はP-series(A01/A02/ADD03)のマスターテキスト経由の生成方式を指す。N3以降の新規記事(Hanshin/Health/Household等)は、Natural English Sourceという中間master textの段階を経ず、**Verified Fact Ledgerから直接**A2 Writerを1回呼び出して生成する(B1/B2本文を入力にしない、という原則自体はP-series/N3とも共通)。詳細はB1節「News本文の生成方式」を参照 | Natural English Sourceから独立生成(P-series) | Natural English Sourceから独立生成(P-series) |
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
| Core Explanatory Logic Preservation | A2生成指示(`A2_KAI1_INSTRUCTION`)へ追加した原則:「Preserve the core explanatory logic and decision rule established by the Verified Fact Ledger. You may simplify wording, sentence structure, examples, and presentation order, but do not replace the Ledger's underlying mechanism or decision rule with an easier shortcut, category, causal explanation, or rule of thumb that the Ledger does not support or explicitly rejects. Simplify how the listener understands the idea, not what the idea means.」語彙・文構造・具体例・提示順序の簡略化は許容するが、Ledgerが規定した判断軸・仕組みを、Ledgerが支持しない/明示的に否定するショートカット・分類・因果関係・経験則へ置き換えない。ジャンル固有の具体例(例: Household記事のfruit/vegetable)はこの一般原則のprompt本文へhard-codeしない | `DECIDED` | ER-003-N3-ROOT-FIX-01(instruction追加)、ER-003-N3-ROOT-FIX-VERIFY-01(3ジャンル検証、ユーザー承認) | 2026-08-17 |

## B1(独立生成Natural Spoken News English) — 2026-08-17新設、2026-08-17確定(SCOPE-FIX-01)

**B1/B2関係の確定(2026-08-17、ER-003-B1-B2-SCOPE-FIX-01でユーザーDecision)**:
前回のSoT Consistency Cleanupで`NEEDS_CONFIRMATION`としていたB1/B2の
関係は、以下の通り確定した。**B1はB2と同一テキストを共有しない。**
B1は、Verified Fact LedgerからB1専用のWriterで独立して英文を生成する
(A2と対称的な関係。同じLedgerを共有し、別々のWriterで独立生成する
という点でA2/B1は同格)。既存の`B1_B_DIRECT_INSTRUCTION`の思想
(natural spoken news English、adult tone、A2ほど強く簡略化しない、
B2相当の難しい英文よりListening Loadを下げる、Clause Density/Concept
Density/Long-distance Dependencyを抑える、hardなCEFR語彙・文長制限は
設けない)を、そのままB1 News本文の正式仕様とする。「B1 = B2本文 +
Support」という理解は誤りであり、正式には採用しない。

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 基本方針 | B1のNews本文(Full Story Part1/2・Point One・Point Two・In One Line)は、Verified Fact LedgerからB1専用のWriterで独立生成する。目標は: natural spoken news English、adult tone、A2ほど強く簡略化しない、B2相当の難しい英文よりlisteningで追いやすい、Clause Density/Concept Density/Long-distance Dependency等を抑える。hardなCEFR語彙制限・文長制限は設けない。B1の難易度差は、この独立生成された本文自体と、Supportの言語(easy English)・役割の両方で作る(Supportだけで難易度差を作るのではない) | `DECIDED` | ER-003-B1-B2-SCOPE-FIX-01(ユーザーDecision)、ER-003-A2-B1-N3-01(`B1_B_DIRECT_INSTRUCTION`の実装・検証) | 2026-08-17 |
| A2との関係 | A2とB1は同一のVerified Fact Ledgerを共有するが、別Writerでそれぞれ独立生成する。B1は自然なニュース英語を維持しながらB2相当よりListening Loadを下げる。A2はCognitive Load Reductionをより強く適用し、one idea at a timeへの再構成等を行う。両者ともLedgerのFact/Core Logic(A2 Core Explanatory Logic Preservationと同じ原則)を維持する | `DECIDED` | ER-003-B1-B2-SCOPE-FIX-01 | 2026-08-17 |
| News本文の生成方式 | Verified Fact Ledgerから直接1回のWriter呼び出しでNatural English本文を生成する(「B1-B Direct Generation」)。B2を別段階として先に生成し、それをB1へ流用する旧来の2段階パイプラインは使用しない。過去のP-series記事(A01/A02/ADD03)ではCEFR-B2が別途独立生成されているが、これは旧アーキテクチャの記録であり、新規記事のNews本文生成方式ではない | `DECIDED` | ER-003-A2-B1-N3-01(3ジャンル横展開で採用・検証) | 2026-08-17 |
| B1-B Direction Control原則 | 診断的原則であり、新しいhard ruleは追加しない: Clause Density(1文1主要アイデア+限定的な補足情報)、Long-distance Dependency(長い挿入節は分割)、Abstract Noun Chains(名詞化表現は聞き取りを妨げる場合のみ動詞化、機械的ルール化しない)、Logical Flow(必要な箇所のみ明示的接続詞)、Concept Density(新概念を詰め込みすぎない)、Passage Rebuilding(同じFact/Story Coreから自由に構成し直してよいが、Ledgerにない事実・因果・意図・評価を追加しない)。禁止する新規hard rule: 1文語数上限、CEFR外語彙禁止、受動態禁止、1文1事実の強制。平均文長は診断記録のみで、gateとして強制しない | `DECIDED` | ER-003-A2-B1-N3-01 §7-9 | 2026-08-17 |

### B1 Support(Preview / Comment 1-4)

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 対象要素 | Preview、Comment 1〜4を平易な英語で提供する | `DECIDED` | ER-003-B1-NOVEL-AUDIO-01系 | 2026-08-17 |
| Support Englishの難易度目標 | B1本文と同等の難易度は目指さない。目的はNatural English本文を理解するためのListening Navigationであり、Support自体を新しい学習課題にしない。原則: first-listenで理解しやすい、one simple idea at a time、familiar everyday wording、compressed/abstract explanationを避ける、adult tone維持 | `DECIDED` | 同上 | 2026-08-17 |
| Comment役割(C1〜C4) | A2で確立した役割をそのまま維持し、言語だけをJapanese→easy Englishへ変更する。C1: Listening Focus。C2: Mid-story Recovery + Next Question。C3: Story Meaning + Bridge to Points(Point One/Twoの具体的見出し・答えは先出ししない)。C4: Point Recovery + Bridge to In One Line(「英語一文でまとめます」等、In One Lineの文数を断定する表現は使わない) | `DECIDED` | ER-003-B1-NOVEL-AUDIO-01系、ER-003-CROSSLEVEL-AUDIO-01(C3/C4の役割定義はA2と共通起源)、ER-003-A2-B1-N3-01(3ジャンルで再現確認) | 2026-08-17 |

### B1 Key Phrase

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 提示順序 | English → Japanese → English(反復)を正式仕様とする。英英説明(English-only definition)へは変更しない | `DECIDED` | ER-003-B1-NOVEL-AUDIO-01系、ER-003-A2-B1-N3-01(3ジャンルで再現) | 2026-08-17 |
| 採用理由 | 難語の英英説明はそれ自体が新しい理解負荷になる、section長文化を防ぐ、意味理解の確実性を優先するため | `DECIDED` | 同上 | 2026-08-17 |
| 選定方式 | Strategy L(Listening Blocker Ranking)+ Canonicalization。B1本文確定後、B1自身の本文から選定する(A2 Key Phraseの流用はしない) | `DECIDED` | Key Phrase節と共通方針 | 2026-08-17 |

### B1 Voice構成

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| Navigator/Support(Charon) | Welcome、Topic intro、Preview intro/Preview、Key Phrases intro/番号/日本語訳、Full Story intro、Comment 1〜4、Outro | `DECIDED` | ER-003-B1-NOVEL-AUDIO-01-VOICE系(module: `er003_v1_sing01_voice01_generate.py`)、ER-003-A2-B1-N3-01(3ジャンルで再現確認) | 2026-08-17 |
| News Content(Aoede) | Full Story Part1/2、Point One/Twoのsemantic heading・本文、In One Line、Key Phrase英語Component | `DECIDED` | 同上 | 2026-08-17 |
| 検証範囲 | 上記配置は、`er003_v1_sing01_voice01_generate.py`(Voice役割再配置モジュール)およびER-003-A2-B1-N3-01での3ジャンル(Sports/Health/Household)横展開で実際に生成・音声確認済みの最新配置を記載している。過去の暫定版(labels_v2/labels_fixなど中間試作)は反映していない | `DECIDED` | 同上 | 2026-08-17 |

### B1日本語使用範囲

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 原則 | Key Phraseの日本語訳のみ日本語を使用する。Title・Preview・Comment・section narration等へA2由来の日本語spoken textを残さない。A2 Audio Shellの「役割」(Comment役割、Point構造等)は継承するが、A2固有の日本語spoken textそのものは継承しない | `DECIDED` | ER-003-B1-NOVEL-AUDIO-01系(日本語残存Shell要素の英語化) | 2026-08-17 |

## Cross-level仕様(A2/B1/B2共通)

以下はA2の検証で発見・試作したが、**特定レベル固有ではなく番組全体
(A2/B1/B2)に適用する編集・音声品質原則**として正式化したもの。
既存のB1/B2完成音声を今回一括で再生成することはしない。今後の新規
生成・再assemble時から適用する。

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| Preview原則 | ニュース全体のテーマ・問題意識・聞く価値・最後まで聞きたくなる問いを示す。後続本文で聞かせたい具体的な答え・詳細な数字・重要な転換点や結論を先出ししない。A2ではComment1/2がListening Focusとして機能するよう、Previewとの情報重複を特に避ける | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-01/02(A01/A02/ADD03の3記事で再現確認)、ER-003-A2-SPEC-FREEZE-01 | 2026-08-12 |
| 日本語解説・Comment文での制作内部ラベル禁止 | 日本語のComment/解説文(A2 Comment1〜4・Preview・japanese_title、B1 Support等)では、「Part 1」「Point 2」のような制作内部のsegment名・章番号ラベルを使わない。「物語の前半」「後半」「最初に紹介した内容」等、リスナーが単独で理解できる自然な日本語へ言い換える。No.4(pool_n4_supermarket)のA2 comment_2で、内部ラベル「Part 1」がそのまま残った結果、TTSは正しく発話していたにもかかわらずJapanese ASRが恒久的に不一致になりHuman Reviewへ滞留する実例が発生したことを受けて明文化した。今後の新規生成に適用し、既存の完成済みトピックへの一括遡及適用はしない(OPEN-68の既存方針に準拠)。機械的な検出・記録は下記QA/Human Review節の「日本語canonical textの外来語/制作内部ラベル検出」を参照 | `DECIDED` | ER-009-JA-FOREIGN-TOKEN-GATE-01 | 2026-08-26 |
| Key Phrase発音品質(3条件) | 以下3条件を同時に満たす: (1) Meaning/contextual prosody(本文での意味に合ったイントネーション・stress) (2) Phoneme integrity(語末子音等の必要音素を自然に保持) (3) Phrase grouping(単語ごとに分断せず1つの意味単位として自然に読む)。個別単語パッチではなくこの共通原則で生成する。機械QAだけで自然さPASSとせず、主観的音声品質はユーザー判断を最終とする | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-04(Come on/Go ahead/Brent crude oil)、ER-003-A2-AUDIO-AB-01(A02の5件へ適用、ユーザー承認)、ER-003-A2-SPEC-FREEZE-01 | 2026-08-12 |
| 英語見出しのTTS方式 | Point One/Point Two/In One Line等の英語見出しは、見出し文字列そのものをTTS inputへ渡し、英語として自然に読ませる。「見出しを渡さずinstructionだけで発話させる」方式は使用しない | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-04 | 2026-08-12 |
| ポーズ(「ポイント解説」→Preview) | 0.7秒 | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-01/02(3記事で再現) | 2026-08-12 |
| ポーズ(Point One→Point Two) | 0.8秒 | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-03提案、ER-003-A2-AUDIO-AB-01で実装・確認 | 2026-08-12 |
| ポーズ(In One Line→Outro) | 0.8秒 | `DECIDED` | 同上 | 2026-08-12 |
| ポーズ(A2 Comment、英語→日本語) | 1.0秒 | `DECIDED` | ER-003-A2-AUDIO-01以降、無変更 | 2026-08-12 |
| ポーズ(A2 Comment、日本語→英語) | 0.8秒 | `DECIDED` | 同上 | 2026-08-12 |
| Comment前後の効果音 | 専用効果音は入れない(ポーズのみ) | `DECIDED` | ER-003-A2-AUDIO-01以降、無変更 | 2026-08-12 |
| Outro音量 | 最新の減衰方針(Introへのgain matching後、心理音響ベースの追加減衰を2段適用、単純な振幅比ではなく人間聴覚上のバランスを優先)を共通mix ruleとして採用。既存B1/B2完成音声は一括再生成しない | `DECIDED`(方針として) | ER-003-CROSSLEVEL-AUDIO-01〜04、ER-003-A2-AUDIO-AB-01、ER-003-A2-SPEC-FREEZE-01 | 2026-08-12 |
| Point Notification | Point OneとPoint Twoの直前に、専用のNotification音(`universfield-new-notification-07-210334.mp3`、既存のKey Phrase/Full Story Notificationとは別音源、A2/B1共通)を挿入する。Point番号を音声で明言しない(「Point One.」「第一に」等は不使用)。Notification→semantic heading→本文の順で、Notification直後に追加の余白は入れない(Notification音源自体の余韻をそのまま使う) | `DECIDED` | ER-003-POINT-NOTIFICATION-01、ER-003-A2-B1-N3-01(Sports/Health/Householdで無修正のまま安定動作を確認) | 2026-08-17 |
| Point semantic heading | Point One/Twoの本文直前に、その回答・視点を要約する短い見出し(記事生成プロンプトが返す`###`見出しをそのまま使用、追加のLLM呼び出しは不要)を置く。見出し文字列は実際にTTS inputへ含めて発話させる(英語見出しのTTS方式と同じ考え方)。B1は見出し・本文ともAoede、A2も見出し・本文とも既存の単一Aoede構成を維持する | `DECIDED` | ER-003-A2-POINT-HEADING-AUDIO-01(A2)、ER-003-B1-NOVEL-AUDIO-01-VOICE系(B1)、ER-003-A2-B1-N3-01(3ジャンルで再現) | 2026-08-17 |
| Point Balance(長さの扱い) | 目標30〜60語、許容25〜70語を**診断的な目安**として使う。hard capにはしない。PointをMain Storyの反復("第二の本編")にせず、別角度・背景・意味・示唆を短く示す、という役割基準を優先判断とする | `VALIDATED across Sports/Health/Household`(hard ruleへの昇格はしない) | ER-003-SPOKEN-FIRST-03(A02単独で検証)、ER-003-A2-B1-N3-01(3ジャンルでこの目標範囲内に自然収束することを確認、hard capとしては未採用のまま) | 2026-08-17 |
| Spoken-first Number Treatment | Verified Fact Ledgerは常にexact factを保持する。spoken narrative側は、精度自体に意味がない数字を、丸め(round)・概数化(approximate)・方向化(directionalize)してListening easeを優先してよい。分類は2軸: Importance(`ANCHOR`/`SUPPORTING`/`DISPENSABLE`)、Exactness(`EXACT_REQUIRED`/`APPROXIMATE_OK`/`DIRECTION_ONLY`)。スコア・日付・記録・健康研究の結果・安全閾値など、精度そのものが意味を持つ数字はEXACT_REQUIREDのまま維持する | `DECIDED` | ER-003-A2-B1-N3-01 §14(A2/B1双方へ適用、3ジャンルで運用確認) | 2026-08-17 |
| Fact Safety(共通) | Verified Fact Ledger(記事ごとに1つ、A2/B1で共有)→独立Fact Checker(web検索付き、`PASS`/`REVIEW_REQUIRED`)→Ledger Deviation Check(`LEDGER_COMPLIANT`/`LEDGER_DEVIATION`)の3段構成を、A2/B1双方の標準QAとして使う。Supportは新しいFactを追加しない。特に scope expansion・causal strengthening・policy/pilotの混同・unsupported comparison・invented connectionを避ける。Fact CheckerがREVIEW_REQUIREDを返した場合、無限に再生成せず、内容をそのまま記録した上で許容判断を下してよい(記事固有の判断として記録に残す) | `DECIDED` | ER-003-A2-B1-N3-01、ER-003-N3-ROOT-FIX-01/VERIFY-01 | 2026-08-17 |
| ジャンル再現性 | 上記のScaffold役割・Point Notification・semantic heading・Voice分離・difficulty区別・Full Audio組み立て・Fact Safetyの一式が、Sports(Hanshin)・Health(Small Habits, Longer Lives)・Everyday Practical(Household crisper drawer)の3ジャンルで無修正のまま機能することを確認した | `DECIDED`(validation evidenceとして) | ER-003-A2-B1-N3-01 | 2026-08-17 |

これらのポーズ・共通定数は、現状B1組立スクリプト側で記事ごとに
個別定義されている(一元化された共通定数モジュールはまだない)。
共通定数化そのものは今回のスコープに含めない([OPEN_ITEMS.md](OPEN_ITEMS.md)参照)。

### Audio Implementation Detail(実装詳細、サービス仕様ではない)

以下はAudio生成パイプラインの実装詳細であり、番組の聞こえ方・サービス
仕様そのものを変更するものではない。理由・比較検討は[DECISION_LOG.md](DECISION_LOG.md)の
「Implementation Hardening」区分を参照。

| 項目 | 現在値 | 根拠Decision |
|---|---|---|
| English Key Phrase trim safety margin | 0.20秒(Key Phrase専用。他segment=Preview/Comment/Title等は既存の0.08秒のまま、他segmentへは波及していない) | ER-003-N3-ROOT-FIX-01 |
| TTS style instruction責務分離 | 共通style instructionに、Point One/Point Two/In One Lineを読み上げさせる指示(`POINT_LABEL_FIDELITY_RULE`)を無条件に含めない(既定で除外、必要な一括生成呼び出し元だけが明示的に有効化できるopt-in設計)。現行コードベースにfull-program一括TTS呼び出し元は存在しない | ER-003-N3-ROOT-FIX-01 |
| 短いJapanese phraseのminimal instruction fallback | 標準経路(JAPANESE_STYLE_PREFIXを使った生成)が既定回数不合格の場合、最小限instructionへ自動フォールバックする(英語Key Phraseに既存の仕組みと同じ考え方を日本語の短いフレーズにも拡張)。標準経路が成功している場合は追加呼び出しなし。標準経路が不合格を繰り返す場合のみ、fallback分のTTS/ASR呼び出しが追加発生する | ER-003-N3-ROOT-FIX-01 |
| TTS/ASR normalization共通部品 | `er003_audio_tts_asr_safety.py`をAudio共通安全部品として位置づける。ただし2026-08-17時点で、ER-003-A2-B1-N3-01/FIX-01で発見・実装した個別のnormalization処理(curly quote正規化、Markdown太字除去、数字表記ゆれ吸収、Key Phrase複合語対応等)の一部は、まだこの共通モジュールへ統合されておらず、N3専用スクリプト(`er003_v1_n3_01_tts_generate.py`)内に留まっている。**未統合**(→[OPEN_ITEMS.md](OPEN_ITEMS.md)) | ER-003-A2-B1-N3-01、ER-003-A2-B1-N3-01-FIX-01 |
| TTS Instruction/Spoken Text分離(Structured Separation) | **目的**: Gemini TTSが時々、style instruction(話し方の指示)を読み上げ対象の本文と混同し、instruction自体を発話・パラフレーズしようとする(instruction leakage、`INVALID_ARGUMENT`エラーや異常長hallucinationとして観測)。この混同を防ぐため、TTSへ渡す入力(`er003_b1_p4c_audio.build_tts_prompt(text, style_prefix)`)を、`=== STYLE INSTRUCTIONS (do not speak) ===`/`=== TEXT TO SPEAK ===`という明示的なdelimiterで区切る構造(Structured Separation)にする。**期待動作**: style_prefix(話し方の指示、voice/speaker/tone/pacing/narration characterの要求含む)とtext(実際に読み上げる本文)は、どちらも内容・語数・意味を一切変更しない。変更するのは区切り方のみ。standard path・fallback path(minimal instruction)の両方に同じ原則を適用する。**禁止事項**: style instruction本文・speaker指定・voice・tone・pacing要求・narration character・spoken text本文を変更すること(区切り方以外の変更は本Decisionのスコープ外)。Gemini公式`system_instruction`フィールドは、TTSでの対応が公式ドキュメントに記載されておらず実機でも不安定(500 INTERNAL)なため採用しない | ER-005-AUDIO-INSTRUCTION-SEPARATION-01 |
| 短い日本語segmentのASR検証: 発音ベースPhonetic Validation | **目的**: 短く文脈のない日本語Key Phrase/gloss(例:「内在化問題」)は、Azure STTが同音の一般語(例:「内在課問題」)へ書き起こすことがあり、実際には正しく発話されている音声を漢字表記の不一致だけでTTS再生成していた。**期待動作**: `er003_audio_tts_asr_safety.validate_japanese_short_segment_match()`が、EXACT_MATCH/NORMALIZED_MATCH/PHONETIC_MATCH(読みが完全一致、漢字表記は不問)/TRUE_CONTENT_MISMATCH/ASR_UNCERTAINの5分類を返す。EXACT_MATCH・NORMALIZED_MATCH・PHONETIC_MATCHは採用しTTS retryしない。TRUE_CONTENT_MISMATCHはTTS retry候補。ASR_UNCERTAIN(読みが近いが完全一致ではない等、機械的に断定できない)は「TTSが誤っている」と断定せず、既存audioを保持したまま既存fallback/reviewへ委ねる(無条件TTS再生成はしない)。適用対象は`JAPANESE_SHORT_SEGMENT_MAX_CHARS`(30文字)以下の短いsegmentのみ(長文Narrationには適用しない)。**禁止事項**: 数字の実質的な違い・否定の有無・主要語の欠落・明らかに異なる発音・無関係な発話・hallucinationをPHONETIC_MATCHで吸収すること。個別専門用語のwhitelist(1対1のハードコード)を主方式にすること | ER-005-JA-SHORT-ASR-PHONETIC-01 |
| TTS生成の同一segment総試行回数上限 | **3回**(初回を含め最大3回。「初回+3 retry」ではない。4回目以降は絶対にTTS生成しない)。`er011_human_review_lock_01.PRODUCTION_MAX_TTS_ATTEMPTS`をSSOTとし、Production全8関数(`generate_narration_snippet_verified_strict`/`generate_key_phrase_component_verified`/`generate_charon_english`/`generate_charon_japanese`/`generate_news_narration_wide_margin`/point_headings `generate`/`generate_english_segment_with_fallback`/`generate_a2_japanese_with_fallback`)の`max_attempts`既定値がこれを参照する。standard経路+fallback経路の2段構成を持つ関数は、fallbackへ「max_attempts−standardで消費した試行数」の残り予算のみを渡し、合計が上限を超えないようにする。新規生成のみに適用され、既存の完成済み音声を遡及的に再生成することはない(ER-011 Review Lockが既存segmentの自動再生成を既にブロックしているため) | ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15(ユーザー正式決定) |
| 固有名詞ASR不一致の自動PASS条件 | ASR結果同士が収束していることだけでは自動PASSしない(「ASR consensus ≠ pronunciation verification」)。(A) canonical綴り・ASR候補の両方がCMU Pronouncing Dictionaryに存在し、代表(先頭)発音が完全一致する場合のみ自動PASS(`PROPER_NOUN_ENTITY_ARPABET_CONFIRMED`、Perplexity lookup不要・コストゼロ)。(B) CMU辞書に無い外国由来固有名詞は、Pronunciation Ledgerをlookup(cache miss時のみPerplexityで1回research、記事横断でcache再利用)するが、その情報は自動PASSの根拠にはせず、Human Reviewパッケージ(canonical spelling/expected pronunciation/IPA/source/Primary・Secondary ASR結果/実音声)を充実させるためだけに使う。IPA→ARPAbet変換による近似自動PASSは行わない(外国語音韻情報の欠落による誤PASSを避けるため)。**2026-08-28追記**: (B)を「外部発音根拠とTTS実音声の自動照合によるAUTO PASS」へ格上げする案を検討したが、それを安全に行う軽量な既存手段が無いためSTOPし未実装(OPEN-83、DECISION_LOG参照)。(B)は引き続きHuman Review行きのまま。Perplexity研究プロンプトのみ、本人・公式情報源を優先するよう改善した(Human Reviewパッケージの質向上目的、PASS判断には使わない) | ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 |
| 日本語表記ゆれ(漢字/かな)のCascade内自動PASS条件 | `ORTHOGRAPHIC_VARIANT_CONFIRMED`: 「ASRが同じ表記を何回書いたか」ではなく、「ASR側の漢字spanが辞書上持ちうる正当な読み候補の中に、canonical側の期待読みが含まれるか」を各ステップ個別に確認し、かつ異なる2エンジン(OpenAI/Azure)以上がその状態に到達した場合のみPASSする。既知の限界: 「頃」のように単漢字として複数の読み(ころ/ごろ等)が辞書上正当とされる文字は、テキストのみからは実際に発話された読みを完全には確定できない(音声を伴わない原理的な限界、OPEN_ITEMS.md参照) | ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 |
| 英語homophone(同音異義語)のCascade内自動PASS条件 | `HOMOPHONE_EQUIVALENT`: canonical/ASRの単一語置換差について、CMU Pronouncing DictionaryのARPAbet音素列が完全一致する場合のみcascade対象とする(即blind TTS retryしない)。Secondary(または2回目のASR)側の結果が、(a)canonical文字一致、または(b)同じくARPAbet完全一致のいずれかを満たした場合のみPASSする(「他に問題が見つからなかった」という消極的な理由ではPASSしない)。辞書に無い語向けの小さな閉じた補完テーブルを併設(2026-08-28時点で空、必要時に追記) | ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 |

## Key Phrase

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 選定方式 | Strategy L (Listening Blocker Ranking) | `DECIDED` | ER-003-P2I(commit `e33f227`) | 2026-07-xx |
| 件数 | 5件/記事 | `DECIDED` | ER-003-P2I | 2026-07-xx |
| 語数範囲 | 1〜5語(`key_phrase`) | `DECIDED` | ER-003-KP-02-R1(commit `5a94db0`) | 2026-08-08 |
| 選定元 | `HISTORICAL`表記に注意: 「各記事自身のCEFR-B1本文」は、A2が存在する前の単一レベル(B1のみ)時代の記述。**現行はレベルごとに、そのレベル自身の最終確定本文から独立選定する**(A2はA2最終本文から、B1はB1最終本文から。CEFR-A2構造・音声仕様節「Key Phrase選定(A2)」、B1 Key Phrase節を参照)。他レベルのKey Phraseを機械的に流用しない、という原則自体はP-series/現行とも共通 | `DECIDED` | ER-003-REPRO-01-KP(commit `46aa2e8`、当時はB1のみ)。現行の per-level選定はER-003-CROSSLEVEL-AUDIO-02(A2)・ER-003-B1-NOVEL-AUDIO-01系(B1) | 2026-08-08(per-level化: 2026-08-10前後) |
| 後処理 | Pedagogical Phrase Canonicalization(`source_span`→`display_phrase`→`key_phrase`→`used_form`) | `DECIDED` | ER-003-KP-01(commit `e607d26`) | 2026-08-08 |
| Canonicalization原則 | 「最小」ではなく「最小十分」 | `DECIDED` | ER-003-KP-02(commit `8856264`) | 2026-08-08 |
| QAモデル | 3状態(`CANONICALIZATION_PASS`/`REVIEW_REQUIRED`/`INVALID`)、11 QAフィールド | `DECIDED` | ER-003-KP-01→KP-02→KP-02-R1 | 2026-08-08 |
| Traceability定義 | 「source_spanから説明可能な正規化で導出できる」こと。文字通りの部分文字列一致は不要 | `DECIDED` | ER-003-KP-02-R1 | 2026-08-08 |
| human review条件 | いずれかのQAフィールドがFAILならREVIEW_REQUIRED、自動retryなし、人間承認で採用可 | `DECIDED` | ER-003-KP-01→KP-02 | 2026-08-08 |
| `used_form`/`key_phrase`の関係 | 現状100%重複(技術的負債として記録、整理はしない) | `DECIDED`(整理しない方針が決定事項) | ユーザー指示(2026-08-08、KP-02-R1承認時) | 2026-08-08 |

## Preview

**適用範囲の注意(2026-08-17追記)**: 本節は**A2、および旧P-series B1**の
Preview仕様を記す。**現行B1(Support-based Natural English)のPreviewは
本節と異なり、平易な英語・Charon voice**である(B1 Support節を参照)。
本節を「A2/B1共通のPreview実装仕様」と読まないこと(Cross-level仕様節の
「Preview原則」は言語・voiceによらない編集原則であり、本節の技術仕様
[言語・TTS model・voice]とは別レイヤー)。

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 言語 | 日本語のみ(A2、および旧P-series B1) | `DECIDED` | ER-003-B1-P9A-R1(英語Key Phrase埋め込み方式は不採用) | 2026-08-07 |
| TTS model | `gemini-3.1-flash-tts-preview` | `DECIDED` | ER-003-B1-P7A(commit `b4f871f`) | 2026-08-06 |
| 採用理由 | 旧モデル(2.5)で「激しい」→「げきせつな」等の誤読が発生し、3.1で解消を確認 | `DECIDED` | ER-003-B1-P7A | 2026-08-06 |
| voice | Aoede(A2、および旧P-series B1)。**現行B1はCharon**(B1 Voice構成節を参照) | `DECIDED` | ER-003-B1-P7A以降 | 2026-08-06 |
| 生成方式 | 単一TTS call(chunk分割なし) | `DECIDED` | ER-003-B1-P7A | 2026-08-06 |
| Key Phrase埋め込み | しない(Full Story側のみで扱う) | `DECIDED` | ER-003-B1-P9A-R1以降 | 2026-08-07 |
| モデル分離 | Preview(3.1)とFull Story(2.5)の設定を分離、片方の変更が他方に波及しない設計 | `DECIDED`、`ModelIsolationTests`で固定確認済み | ER-003-B1-P8A | 2026-08-07 |
| 承認フロー | ①台本(日本語テキスト)をチャットで提示→ユーザー承認→②その台本のまま音声生成→③音声試聴→ユーザー承認。台本確定後の勝手な再生成・変更はしない | `DECIDED` | ER-003-REPRO-01/02-PREVIEW系 | 2026-08-08〜09 |

## Full Story

**適用範囲の注意(2026-08-17追記)**: 「chunk構成(3chunk)」はP-seriesの
パイプライン(単一のFull StoryをTTS 1呼び出し内で3分割生成)を指す
`HISTORICAL`情報。N3以降はFull Story Part1/Part2をそれぞれ独立した
1回のWriter/TTS呼び出しで生成し、3chunk分割は行わない。TTS model
(`gemini-2.5-pro-preview-tts`)・voice(Aoede)は、N3のFull Story Part1/2・
Point One/Two・In One Line(=News Content)でも同一の値が使われており、
この2項目はP-series/N3を通じて現在も有効。

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| TTS model | `gemini-2.5-pro-preview-tts` | `DECIDED`(凍結仕様、N3のNews Contentでも継続使用を確認) | ER-003-B1-P4D〜P8A | 2026-08-06以前 |
| voice | Aoede(News Content。B1のNavigator/Support要素はCharon、B1 Voice構成節を参照) | `DECIDED` | 同上 | 同上 |
| chunk構成 | `HISTORICAL`(P-series専用、3chunk)。N3以降はPart1/Part2をそれぞれ単一呼び出しで生成し、chunk分割はしない | `DECIDED`(P-seriesの凍結仕様として) | ER-003-B1-P4D〜P8A | 同上 |
| 内容QA retry | 3試行1セット(`run_tts_content_attempts`) | `DECIDED` | ER-003-B1-P8A系 | 2026-08-07 |
| 短文ナレーション生成 | 前後文脈のない短いフレーズは専用の最小限instructionで生成 | `DECIDED` | ER-003-B1-P9A-R1(commit `d41e4fe`) | 2026-08-07 |
| strict ASR検証 | 部分一致 + ASR文字数上限(期待文字数+少数の余裕)の両方を確認 | `DECIDED` | A02 meaning_5発見を機に追加 | 2026-08-08 |
| minimal instruction fallback | 標準経路が規定回数(既定6回)不合格の場合、最小限instructionへ自動フォールバック(短文ナレーション・英語Key Phrase Componentの両方に適用)。**2026-08-26更新(ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04)**: fallback(minimal instruction)経由で生成された英語音声は、Primary ASRの結果に関係なくSecondary ASR(Azure)による確認を必須化した(`er006_secondary_asr_01.py::evaluate_attempt_with_cascade(force_secondary=True)`)。standard path側は無変更・追加コストなし。No.7 A2 point_one_headingで実際に発生した「Primaryは正常認識・Secondaryは全く別内容」という誤PASS事故の再発を防ぐ暫定対策(fallback自体の根本原因見直しはOPEN-66・OPEN-67参照、`DEFERRED / AFTER USER VALIDATION`) | `DECIDED`(fallback導入)、`PRODUCTION_WIRED`(Secondary ASR必須化、2026-08-26) | ER-003-REPRO-01-MAIN(導入)、ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04(Secondary必須化) | 2026-08-08(導入)、2026-08-26(Secondary必須化) |
| Dynamics処理 | **不使用**(scalar gainのみ、compressorやDynamics3は使わない) | `DECIDED` | `er003_b1_p9a_audio.py`にコード内コメントで明記 | 2026-08-07 |
| Evidence Compression(方式C、Lossless Editor) | 通常WriterがFact-safeな記事を生成した直後(`er003_v1_n3_01_articles_generate.py::run_one_pattern()`内)、Lossless Editor(`er003_v1_n3_01_evidence_compression_editor.py`)がspoken layerだけを軽量化する。許可: 不要な出典名(企業・調査会社・研究機関・メディア・イベント名)の削除・一般化、重複/近似数字の圧縮(ただしトレンドの大きさ・方向そのものを理解するために必要な核心的比較は残す)、冗長なEvidence説明の簡素化。禁止: Fact追加・削除、correlation→causation、certainty強化、uncertainty/hedging削除、scope拡張、negation変更、comparison direction変更、temporal direction変更、Point意味変更、Story論旨変更。Research/Evidence Pack/VFL/Fact Ledger自体は変更しない。Editor適用後のテキストに既存のFact Check/Ledger Deviation Checkをそのまま適用する(同じ安全確認プロセスを再利用)。`apply_evidence_compression`引数(`run_one_pattern`)/`apply_evidence_compression_editor`引数(`run_writer_for_theme`)、既定`True`(Production既定で有効)、DEV/testでOFFにしたい場合のみ`False`を渡す | `DECIDED`(`PRODUCTION_WIRED`) | ER-008-TTS-FALLBACK-AND-EVIDENCE-COMPRESSION-03(script-only初回実証)→ER-008-FALLBACK-TRIGGER-MITIGATION-AND-EVIDENCE-COMPRESSION-AB-04(方式B比較・方式C推奨・Fact safety不変条件追加)→ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05(方式C MAJOR精査)→ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06(ユーザー正式採用・Production配線) | 2026-08-26 |
| A2 Key Phrase pause(番号→phrase間) | A2のみ、番号読み上げ→Key Phrase本体の間を、既存の`KEY_PHRASE_INTERNAL_PAUSE_SECONDS`(0.4秒)より合計+0.2秒長くする(`A2_KEY_PHRASE_NUMBERING_PAUSE_SECONDS`、`er003_v1_n3_01_assemble.py`)。B1は無変更(0.4秒のまま)。No.7実音声で実測: 各Key Phraseで約0.61〜0.67秒(元Baseline実測の約0.41〜0.47秒からおよそ+0.2秒) | `DECIDED`(`PRODUCTION_WIRED`) | ER-008-N7-CONTENT-AUDIO-QA-02(+0.1秒)→ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06(さらに+0.1秒、合計+0.2秒) | 2026-08-26 |
| A2英語ナレーション速度指示 | A2の英語spoken content(Full Story Part1/2・Point One/Two見出し・本文・In One Line)にのみ、既存のENGLISH_STYLE_PREFIX(emotion/prosody指示)の末尾へ自然言語の追加指示("Speak at a slightly slower, relaxed pace than natural adult narration, while keeping the delivery smooth, conversational, and natural. Do not exaggerate pauses or sound instructional.")を付与する(`A2_ENGLISH_STYLE_PREFIX_SLOWER`、`er003_v1_n3_01_tts_generate.py`)。数値WPM指定・speed factor指定はしない(`assert_no_wpm_specification`で保証)。B1・fallback(minimal instruction)経路には適用しない。No.7での実測: 新旧で使用テキストが完全に異なる(Method C適用+Writerの新規生成)ため単純比較はできないが、平均WPMは138.8→141.5とむしろ微増しており、この指示だけで明確な減速効果は確認できなかった(そのまま報告、追加のprompt再調整はしていない) | `DECIDED`(`PRODUCTION_WIRED`、効果は限定的と判明) | ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06 | 2026-08-26 |
| A2英語ナレーション速度(post-processing time-stretch) | 自然言語Prompt(上記行)がsame-text条件下でも安定して機能しない([OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-71〜74参照、ER-008-A2-SPEED-SAME-TEXT-ABC-09でB/CともAより速くなることを確認)ことを受け、既存の完成音声そのものをFFmpeg `atempo`フィルタ(pitch-preserving time-stretch、単純なsample-rate変更[pitchが下がる]ではない)で事後的に減速する方式を検証(ER-008-A2-TIMESTRETCH-ABC-10、No.7 A2 Full Story Part 1で3%/6%/9%比較、pitch実質不変・ASR内容破損なしを確認)した上で、**ユーザーが試聴の上6%を正式採用**した(ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11)。`er008_a2_postprocess_slowdown_01.py`(`apply_a2_slowdown`、既定6%)を新設し、`er003_v1_n3_01_tts_generate.py::generate_a2_segments()`の`generate_a2_segment_with_slowdown()`経由でA2英語7segment(point_one_heading/point_two_heading/full_story_part1/full_story_part2/point_one/point_two/in_one_line)全てへ配線した。**既存の自然言語「わずかに遅く」instruction(`A2_ENGLISH_STYLE_PREFIX_SLOWER`)は引き続き使用する**(ユーザーが承認した音声は instruction込みの音声への6% time-stretchであり、instructionを除去したものではないため)。time-stretch前の通常ペース音声は`{name}_original.wav`として保持し、Middle等で現状より速い読み上げが必要な場合にTTS再生成なしで再利用できる。post-process後の音声を実際にASRで再検証し、不一致の場合は最大3回まで通常ペースから取り直すretry機構を持つ(実運用でpost-process後にのみASR不一致が生じる事象を発見、retryで解消することを確認済み、[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-76)。No.7 A2の7segment全てを実データで再生成し、Audio Validation Gateを実PASSで再assemble済み。比較Artifact: https://claude.ai/code/artifact/6efa0f4c-79a8-4d1e-a3ae-8c81d853a53d | `DECIDED`(`PRODUCTION_WIRED`) | ER-008-A2-TIMESTRETCH-ABC-10(検証)、ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11(ユーザー承認・Production配線) | 2026-08-26 |

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
| ASR診断 | **2026-08-25更新(ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01)**: 現行仕様: 英語・日本語ともPrimary ASR=OpenAI `gpt-4o-mini-transcribe`(2言語で統一)、AzureはSecondary ASR Cascade(entity-like mismatch検出時のみ、英語はPhrase List付き)として両言語で使用する。SSOTは[er006_asr_provider_routing_01.py](er006_asr_provider_routing_01.py)。決定はASR単独では下さない(Validator・Secondary ASR Cascade・Human Reviewを含む複数段階で判断する) | `DECIDED` | ER-006-AUDIO-COST-PILOT-02(英語Routing切替)、ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01(日本語Routing切替) | 2026-08-25 |
| ASR一致と発音品質の関係 | ASR transcript一致(EXACT_MATCH/NORMALIZED_MATCH等)は「書き起こしテキストが正しい」ことの確認であり、「人間が聞いて自然・正確な発音である」ことの証明ではない。ASR一致=発音品質PASSと**扱わない**(ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01: Key Phrase "hostile architecture"でASRは正しく書き起こしていたが、ユーザー試聴では語頭/h/が/p/様に聞こえるという実例で確認。詳細は[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-44) | `DECIDED` | ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01 | 2026-08-22 |
| hallucination対応 | strict検証+minimal instruction fallbackで自動検出・自動吸収(A02で2件実績)。**根本原因は未解明のまま** | `DECIDED`(運用方針)、原因は`UNDER_REVIEW`ではなく未解明のまま保留 | ER-003-REPRO-01-MAIN | 2026-08-08 |
| ASR homophone ambiguity対応 | strict検証が規定回数不合格でも、TTS自体が正常な可能性がある場合はretryを打ち切り、`PROVISIONALLY_ACCEPTED_REQUIRES_HUMAN_REVIEW`→ユーザー試聴後`ACCEPTED_AFTER_HUMAN_REVIEW`という2段階の人間確認フローを使う | `DECIDED`(ADD03 meaning_3で初適用・確定) | ER-003-REPRO-02-MAIN/FINAL | 2026-08-09 |
| 最終人間試聴 | 機械QA全合格でも「完成」「量産再現性合格」とは判断せず、必ずユーザー試聴を経る | `DECIDED` | 全ステージで一貫 | - |
| 量産再現性判定 | A. 量産候補として採用可能(A02・ADD03の2記事連続成功に基づく)。ただし完全自動化ではなく最終人間試聴を必須ゲートとして維持 | `DECIDED` | ER-003-REPRO-FINAL(commit `c4a762c`) | 2026-08-09 |
| Audio Validation Gate(Assembly直前の検証ゲート) | Production assembly(`er003_v1_n3_01_assemble.py::load_b1_sources`/`load_a2_sources`)は、実行直前に`verify_episode_audio_validation_gate()`で、そのrunの`tts_generation_results.json`に記録された全segment(Full Story/Point見出し・本文/Preview/Comment/In One Line/Key Phrase英日、ファイルに存在する全て)を検査する。各segmentはVALIDATED(status=OK)/HUMAN_APPROVED(ASR_VALIDATION_UNCERTAINだがcanonical_text一致の明示的承認記録あり、`record_human_approval()`で記録)/UNVALIDATED/STOPPEDへ正規化され、VALIDATED・HUMAN_APPROVED以外が1件でもあればepisode assembly全体を`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`として中止する。ファイルが存在するだけでは採用条件を満たさない(「とりあえず最後のWAVを使う」の禁止)。既存の`tts_generation_results.json`を正とし、新しいmanifestファイルは作らない(重複実装回避)。適用範囲は現行Production経路(本ファイルが読むtheme)のみ、legacy/experimental scriptは対象外 | `DECIDED`(`PRODUCTION_WIRED`) | ER-008-N7-CONTENT-AUDIO-QA-02(Key Phrase限定の原型`verify_key_phrase_audio_integrity`)、ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05(全segmentへ一般化・Production配線) | 2026-08-26 |
| Interim directional fact precheck for user-validation phase(比較方向Fact事前チェック、暫定) | [er008_directional_fact_precheck_08.py](er008_directional_fact_precheck_08.py)の`audit_article_directional_facts()`を、`er003_v1_n3_01_articles_generate.py::run_one_pattern()`(Fact Check/Ledger Deviation Checkの直後)へ既定Trueで配線した。more/fewer、at least/at most、increase/decrease等の比較方向反転(No.7 B1 Point Twoで実際に発生、[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-71)を、rule-based(新規LLM callなし)で検知する**暫定策**。判定はMATCH/POTENTIAL_DIRECTION_REVERSAL/DIRECTION_REVIEW_REQUIRED/NOT_APPLICABLEの4分類、結果は`audit/directional_fact_precheck.json`へ記録する。article生成自体は自動でblockしない(`assert_no_directional_reversal()`という明示的なgate関数を別途用意、完成候補宣言プロセスへの組み込みは今回未実施)。**既知の限界**: 「比率」とその逆数に近い量(例: 従業員・デスク比率 対 従業員1人あたりのデスク数)のように主語が逆数関係にあるFactは、表層的な語の比較だけでは正しく判定できない(実データ検証で、誤りだった旧No.7 B1本文をMATCH、修正済みの正しい本文をWARNと判定し、正誤を区別できなかったことを確認済み)。この暫定策は**OPEN-72(構造化comparator等による本格対策)を根本解決するものではなく**、OPEN-72は`DEFERRED / AFTER USER VALIDATION`のまま維持する。既存22テーマへの横断適用は今回未実施(新規生成分のみ既定で有効)。**本チェックは補助的な警告機能であり、Fact方向の安全性を保証するものではない**(POTENTIAL_DIRECTION_REVERSALが出ないことをもって「方向誤りが無い」と結論しないこと) | `DECIDED`(`PRODUCTION_WIRED`、暫定策) | ER-008-DIRECTIONAL-FACT-PRECHECK-08(fixture 23件全PASS、No.7 B1/A2実データで実証) | 2026-08-26 |
| 日本語canonical textの外来語/制作内部ラベル検出(4分類ゲート) | No.4(pool_n4_supermarket)のA2 comment_2で、制作内部の章番号ラベル「Part 1」がリスナー向け日本語にそのまま残り("Part 1では、店が…")、TTS自体は正しく「パート1」と発話していたが、Japanese ASRが文中の英字表記をローマ字のまま書き起こすことがほぼ無いためcanonical textと恒久的に不一致になり、Human Reviewへ滞留していた(14回の試行全てで再現)。根本原因はASR/TTS側の不具合ではなく編集上の問題(制作都合の内部ラベルをリスナー向け日本語に残した)と判明したことを受け、`er003_audio_tts_asr_safety.classify_foreign_tokens_in_japanese_text()`を新設した。日本語canonical text中の英字・数字混じりのトークンを、TTS呼び出し前に(1)NEEDS_JAPANESE_PARAPHRASE(「Part 1」等の制作内部ラベル、自然な日本語へ言い換えるべき)/(2)READING_DICTIONARY(定着した略語・固有名詞、`DEFAULT_JA_READING_DICTIONARY`に登録済みなら機械的に対応可)/(3)ENGLISH_PRONUNCIATION(その記事のKey Phrase英語表現[used_form]そのもの、呼び出し側が`known_key_phrase_terms`を渡した場合のみ判定)/(4)HUMAN_REVIEW(上記いずれにも機械的な確信を持って分類できないもの)の4分類へ振り分ける(rule-based、新規LLM呼び出しなし、OPEN-72/ER-008-DIRECTIONAL-FACT-PRECHECK-08と同じ「確信が持てない場合は無理に自動判定しない」思想)。過検知でProduction全体を止めないため、TTS呼び出し自体をブロックするのはカテゴリ4(HUMAN_REVIEW)のみに限定し(既存の`detect_gloss_placeholder_notation()`と同じ設計)、カテゴリ1〜3は検出・記録のみに留めて生成は継続する。HUMAN_REVIEW判定時は既存のASR Cascade human_review_queue.jsonlと同じ思想で`er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl`へ記録し、TTS呼び出し自体を行わずSTOPPEDで止める。`er003_v1_n3_01_tts_generate.py`の日本語TTS入口2箇所(B1: `generate_charon_japanese_with_reading_safety()`、A2: `generate_a2_japanese_with_reading_safety()`、後者はminimal instruction fallback経路も内包するため1箇所のチェックで両経路をカバーする)へ配線した。既存のKey Phrase日本語gloss呼び出し(B1 kp_ja_charon・A2 meaning_N)は`known_key_phrase_terms=[used_form]`を渡すよう更新済み。No.4 A2の全Japanese文言(preview/comment_1〜4/japanese_title/Key Phrase gloss5件)へ実行した結果、修正前はcomment_2の「Part 1」1件のみNEEDS_JAPANESE_PARAPHRASEとして検出され、他は0件。comment_2修正後は全segmentで検出0件を確認した | `DECIDED`(`PRODUCTION_WIRED`) | ER-009-JA-FOREIGN-TOKEN-GATE-01(受入テスト13件全PASS[er009_ja_foreign_token_gate_01_test_01.py]、No.4実データで実証・comment_2修正後にAudio Validation Gate実PASS) | 2026-08-26 |
| 英語固有名詞ASR表記揺れの軽量音韻類似度チェック(entity phonetic corroboration) | 既存のentity_only_diffs判定(`er006_preprod_hardening_01_validation.py::classify_asr_match()`、固有名詞らしき語のみの音訳差)は、「retryを打ち切る」設計はあったが「自動PASSさせる」設計が無く、実際には正しく発話されている固有名詞(No.5 pool_n5_cafes B1 full_story_part1の"L. Mimoun and A. Gruen")がHuman Reviewへ滞留していた。全記事・全固有名詞への一律research工程は追加せず(コスト増回避)、`aggregate_entity_only_phonetic_corroboration()`を新設した: 複数の独立したTTS take(同一canonical_textに対する別々の生成)で観測されたASR書き起こし候補を集約し、pure PythonのSoundex実装(`soundex_en()`、新規外部依存なし)+文字列類似度+文字数差+語頭一致による軽量な音韻類似度チェックで、「同一固有名詞の表記揺れ」と判定できる場合のみ`ASR_VALIDATION_UNCERTAIN_PHONETIC_ACCEPTED`として自動採用する。保守的側に倒す設計: (1)数字・否定・非固有名詞内容語の差を含むtakeはそのtake単体を判断材料から除外する(全体は拒否しない)、(2)同じ誤認識が複数回**繰り返し**観測される場合(多様性の裏付けが無い)は自動PASSしない(soundexだけでは"Robert"/"Rupert"のような無関係な別の実在人名同士を区別できないため、これを緩和する設計)、(3)単発観測(裏付け無し)は複数回観測時より厳しい閾値を要求する、(4)canonical/ASR両方の語数が一致する候補のみを判定対象にする(語数不一致[例: "Neukölln"→"new Cologne"]は別の単語への丸ごと置換の疑いが強いため対象外)。`er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin()`(B1 Full Story等の長尺英語News本文生成)へ配線し、entity-only mismatchの場合は既存のmax_attempts上限内でretryを継続して複数takeの証拠を集めるようにした(コスト上限は既存のまま拡張していない)。**既知の限界(正直に記録)**: soundexベースの軽量チェックは実在する別名同士の完全な区別を理論上保証しない。本チェックはretry・Human Review滞留を減らすための補助的最適化であり、既存の必須プロセス(最終的なユーザー試聴)がこの限界に対する最終的な安全網であり続ける | `DECIDED`(`PRODUCTION_WIRED`) | ER-010-ENTITY-PHONETIC-CORROBORATION-01(受入テスト22件全PASS[er010_entity_phonetic_corroboration_01_test_01.py]、No.5実データ[full_story_part1]で実証・Audio Validation Gate実PASS) | 2026-08-27 |
| 複合序数("twenty eighth"型)の正規化バグ修正 | No.5 full_story_part2の日付発話形修正("April 28, 2026,"→"April twenty eighth, 2026,")作業中に、`normalize_text()`の数値正規化パイプラインが、十の位の単語("twenty")と一の位の序数語("eighth")から成る複合序数を正しく1つの序数("28th")へ変換できず、独立した2つのcardinal/ordinal変換ステップがそれぞれ"20"と"8th"へ別々に変換してしまい、"20 8th"という無関係な2トークンへ分裂する実バグを発見した(TTSは実際には正しく"28th"と発話していたにもかかわらず、この正規化バグのせいでASR検証が常に不合格になっていた)。OPEN-58(複合基数のハイフン誤変換)と同じ教訓を踏まえ、汎用的な書き換えはせず、「十の位の単語+一の位の序数語」という閉じた具体的パターンのみを対象にした専用の変換ステップ(`_convert_compound_ordinal_words()`)を、既存のcardinal/ordinal変換より先に実行する形で追加した。スペース区切り("twenty eighth")・ハイフン区切り("twenty-eighth")の両方に対応する | `DECIDED`(`PRODUCTION_WIRED`) | ER-010-DATE-SPOKEN-FORM-POINT-FIX-01(受入テスト7件全PASS、No.5実データで実証) | 2026-08-27 |
| 重要な日付・数字のTTS入力前チェック(検討したが今回は不採用) | No.5 full_story_part2で、正しい"April 28"がTTSにより複数回にわたり"April 26"と発話される事象(ASRの表記揺れではなく、12回中一貫して"26"になる実データから、genuine TTS mispronunciationと判断)が発生した。再発防止として「桁の大きい年号+日付の組み合わせをWriter/Support生成後・TTS前に検出しHuman Review相当のフラグを立てる軽量チェック」の追加を検討したが、今回は実装を見送った。理由: (1) 発生頻度・条件(なぜこの特定の日付表現でTTSが誤読するのか)が未解明で、汎用的な検出ルールを今の時点で設計すると過検知/過剰実装(OPEN-58と同じ教訓)のリスクが高い、(2) 今回発見した個別事象(No.5のこの1箇所)はpoint fix(発話安全形への言い換え)で解決済みであり、緊急に一般化する必要性が低い。今回は個別のpoint fixのみ採用し、一般的な検出ゲートは見送ったことを明記する(必要になった時点でOPEN item化した上で改めて検討する) | `DEFERRED`(不採用、Open Item化) | ER-010-DATE-SPOKEN-FORM-POINT-FIX-01 Part D、OPEN-78 | 2026-08-27 |
| Human Review Cost Guard(Review Lock機構) | No.5(pool_n5_cafes)のB1修正作業中、Human Review Queueへ到達した(または繰り返しSTOPPEDになった)segment(full_story_part1/2)に対し、同じ生成スクリプト(`er009_pool_n5_b1_fix_01.py`)を手動で繰り返し実行してしまい、full_story_part1でTTS 18回・ASR 59回、full_story_part2でTTS 12回という異常なAPI消費が発生した。原因は(1)呼び出し側スクリプトが結果を無条件に上書きし過去の試行履歴・Human Review到達状態を引き継がない設計だったこと、(2)Human Review Queueへ到達した後もそれを検知して新規TTS/ASR呼び出しをブロックする仕組みが存在しなかったこと。`er011_human_review_lock_01.py`を新設し、segment単位のReview Lock状態(`AUTO_PROCESSING`/`HUMAN_REVIEW_REQUIRED`/`HUMAN_APPROVED`/`REGENERATE_APPROVED`/`RESOLVED`)を、narration wavパス(".../<theme>/<level>/narration/<segment>.wav")から機械的に導出したキーで管理する(呼び出し側の関数シグネチャは一切変更しない設計)。`HUMAN_REVIEW_REQUIRED`(cascadeがHuman Reviewへ回した場合、または規定回数STOPPEDで打ち切った場合)または`HUMAN_APPROVED`(既存の`record_human_approval()`と連携)の状態にあるsegmentは、明示的な`approve_regenerate()`呼び出し(`REGENERATE_APPROVED`への遷移、対話的オペレーター操作でのみ到達する経路)が無い限り、TTS/ASR呼び出しを一切行わず既存状態をそのまま返す(0 API call)。`REGENERATE_APPROVED`は次の1回の呼び出しだけで自動的に消費され(`RESOLVED`または`HUMAN_REVIEW_REQUIRED`へ遷移)、「同じスクリプトをもう一度実行しただけ」では再解除されない。台本(text)が変わった場合はSHA256ハッシュの不一致により自動的に新しいバージョンとして扱われ、過去のlockは無効になる(既存の`record_human_approval()`のtext変更時無効化と同じ設計)。累積TTS試行数(既定上限15)・累積ASR呼び出し数(既定上限60)を超えた場合、`REGENERATE_APPROVED`中でも強制的に`HUMAN_REVIEW_REQUIRED`へ固定するbudget guardを第二防衛線として持つ(第一防衛線はHUMAN_REVIEW_REQUIRED到達時点での即時ブロック)。Human Review Queue(英語`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`・日本語`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`)への重複投入も防止する(同一segment・同一canonical_textなら既存entryを再利用)。既存のtts_generation_results.json(segment単位で上書きされる正)は変更せず、別途append-onlyのattempt history(`er011_output/attempt_history.jsonl`)へ記録する。**配線箇所**: 英語側5関数(`er003_v1_sing01_voice01_generate.py::generate_charon_english`、`er003_v1_sing01_point_headings_aoede.py::generate`、`er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin`、`er003_v1_repro01_main_generate.py::generate_narration_snippet_verified_strict`[en/ja共通]・`generate_key_phrase_component_verified`)、日本語側は`generate_narration_snippet_verified_strict`のja分岐と`er003_v1_sing01_voice01_generate.py::generate_charon_japanese`。fallback経路を持つ合成関数(`generate_english_segment_with_fallback`・`generate_a2_japanese_with_fallback`)は、standard経路が`HUMAN_REVIEW_LOCKED`を返した場合にfallbackへ進まないよう明示的に早期returnする(fallbackは未ガードの直接TTS/ASR呼び出しのため)。**既知の適用範囲外**: A2 6% slowdown retry(`generate_a2_segment_with_slowdown`)は内側の関数が`status=OK`を返した後に別途post-process検証で取り直す既存の正当な設計のため、`RESOLVED`状態はブロック対象にしていない(ブロックすると既存の正当なretryを壊すため) | `DECIDED`(`PRODUCTION_WIRED`) | ER-011-HUMAN-REVIEW-COST-GUARD-01(受入テスト9件全PASS[er011_human_review_lock_01_test_01.py]、No.5 full_story_part1相当のシナリオを実際の本番関数で再現し0 API callを実証) | 2026-08-27 |

## Audio Production Pipeline(ER-006、Pool/N3 Production基盤)

ER-006の一連のタスク(AUDIO-COST-OPTIMIZATION-01→AUDIO-COST-PILOT-02→
PRONUNCIATION-LEDGER-SECONDARY-ASR-01→AUDIO-RETRY-CASCADE-PROD-01→
VALIDATOR-NUMERIC-COST-RECONCILE-01)で決定・実装したAudio生成
パイプラインの実装アーキテクチャを、本節でProduction標準として正式化
する。**番組の聞こえ方・言語仕様(voice/style/spoken text/TTS model)は
一切変更しない**(実装方式のみの変更、Cross-level仕様節の内容と矛盾
しない)。本節はDrift Prevention(将来のcommitが気づかず古い実装へ
後退しないようにする)を主目的とし、実装状況を機械的に確認する
Static Audit: [er006_audio_cost_spec_fix_01_static_audit.py](er006_audio_cost_spec_fix_01_static_audit.py)。

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| Gemini TTS実装方式(Batch API) | **Batch API(`client.batches.create()`)をProduction標準として採用・実配線済み**。新設[er006_batch_tts_wiring_01.py](er006_batch_tts_wiring_01.py)(既存の`tts_call_fn(prompt) -> bytes`という呼び出し形状を保つdrop-in factory、`make_batch_tts_call_fn(model, voice)`)を、Production TTS生成6箇所(下記「Production TTS/ASR call site一覧」参照)すべてへ配線した(`er003_v1_crosslevel_audio_02_common.py`は自身でcall_fnを構築せず`repro01`の配線済み関数を再利用するため直接変更なしで対象に含まれる)。1 Batch job = 1 itemの設計(Batch料金割引はitem数に関わらずper-request適用されるためコスト効果は完全に得られる。複数item一括投入用のAPI`submit_batch_multi`/`wait_for_batch_multi`は将来の最適化余地として同モジュール内に用意したが未使用)。voice/style instruction/Structured Separation/spoken text/pacingは無変更、ASR-first Retry Cascade・Validator・Master Audio Storeも無変更(TTS呼び出しの中身だけをStandardからBatchへ差し替え)。**実API最小確認済み**(2026-08-22、代表segment2件[英語Key Phrase"opt out"・日本語gloss「参加・適用を断る」]、既存の承認済み本番文言を再利用、専用出力先へ書き込み既存完成音声には非接触): 実際のProduction call site経由でBatch job計5件が全てSUCCEEDED、既存のtrim/hallucination検知/ASR検証(OpenAI Primary英語・Azure日本語)を通過して最終的に両segmentともstatus=OK。実測コスト削減率50.02%(Batch実費$0.003376 vs Standard換算$0.006755、詳細は`er006_output/tts_batch_wiring_01_smoke/cost_comparison.json`)。**運用上の注意点(新たに判明)**: 1 Batch jobの完了待ちは実測91〜167秒/件で、Standard(通常数秒)より大幅に遅い。ASR不一致でretryが発生するsegmentでは、retry回数分この待ち時間が積み重なる(実測: 英語segmentが4回attemptで522秒)。総生成コストは下がるが総生成時間は増える可能性があるため、量産運用時は監視すること | `DECIDED` / `WIRED` | ER-006-AUDIO-COST-OPTIMIZATION-01(50%オフ完走確認)、ER-006-AUDIO-COST-SPEC-FIX-01(方針の正式化)、ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01(Production実配線・実API確認) | 2026-08-22 |
| Batch Failure Handling | Batch job単位の成功(`state.endswith("SUCCEEDED")`)を個別item(segment)の成功と同一視しない。`er006_batch_tts_wiring_01.py`が、応答内item(現状1 job=1 itemのためitem 0のみ)ごとにsuccess/API error/empty result/invalid audio/missing responseの5分類で判定し、success以外は例外を送出する(fail-closed、Standardへの暗黙fallbackなし)。既存の技術的retry機構(`common._call_tts_with_retry`)が、失敗時に新しいBatch jobを再投入する形で「失敗したitemのみのretry」を実現している(job全体の無条件再投入ではなく、失敗した1 itemがそのまま次のjobの唯一のitemになる設計) | `DECIDED` / `WIRED` | ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01 | 2026-08-22 |
| Master Audio Store | 固定/完全一致で再利用可能な音声(Welcome/Outro等の共通ナレーション、Key Phrase英語Component等)は、[er006_master_audio_store_01.py](er006_master_audio_store_01.py)経由で生成・再利用する。Keyは言語・レベル(nullable)・speaker voice・TTS model・style instruction hash/version・instruction path・canonical text hash(sha256)・processing version・sample rate/channelsの組で構成し、条件が一致しない音声を誤って再利用しない。B1/A2ともsegment生成の最上流(`generate_b1_segments()`/`generate_a2_segments()`)で`ensure_all_shared_narration_b1()`/`ensure_all_shared_narration_a2()`を呼び、Storeのlookupを経由しない無条件の毎回TTS再生成をしない | `DECIDED` | ER-006-AUDIO-COST-PILOT-02(最小実装・配線) | 2026-08-22 |
| Primary ASR Routing | **2026-08-25更新**: 英語・日本語ともOpenAI `gpt-4o-mini-transcribe`(Primary)。言語別構成のSSOTは[er006_asr_provider_routing_01.py](er006_asr_provider_routing_01.py)(`ASR_ROUTING`/`require_asr_route()`/`transcribe()`)であり、Production leaf pathはこのSSOT経由で呼び出す(未登録言語はfail-closedで例外送出、暗黙のAzureへのfallbackは禁止)。**旧`er006_model_routing_contract_01.py`の`ASR_PROVIDER`定数(`"azure"`固定)は、実際のASR呼び出し経路からは参照されておらず、本Routing SSOTが正である**(Model Routing Contract節を参照) | `DECIDED` | ER-006-AUDIO-COST-PILOT-02(英語Primary切替、実測: STOPPED 7→3件、attempt数110→79、Audio実費¥306→¥199/pair)、ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01(日本語Primary切替、実測cost-82%・latency-70%projection、n=14実音声品質確認) | 2026-08-25 |
| Validator(数値正規化含む一般化仕様) | [er006_preprod_hardening_01_validation.py](er006_preprod_hardening_01_validation.py)の`classify_asr_match()`/`normalize_text()`/`normalize_numeric()`を、全Production Audio QAの標準Validatorとして固定する。安全に吸収してよい表記ゆれ: street/St.等のUSPS通り種別略語(canonical側テキストを基準に判定、Saint固有名詞との曖昧性はcanonical-anchored設計で解消)、綴り数字↔算用数字(cardinal)、桁区切りカンマ、小数点、パーセント記号、通貨記号、序数(third以降。first/secondは副詞用法との曖昧性のため対象外)、日付文脈直後の序数接尾辞のみ、規則的な単数形/複数形の語尾差(result/results等、閉じた語尾パターン[-s/-es]のみ、無関係語の誤同一視を避けるため長さ・語尾形状を厳格に限定)。**数式表記の正規化**(2026-08-24、ER-006-GATE-CALIBRATION-ASR-CASCADE-MATH-VALIDATOR-01で追加、本タスクで正式採用): Markdown italic変数表記(`*b*`)、`=`/`is equal to`/`was equal to`↔"equals"、`<`↔"less than"、`>`↔"greater than"、`×`・数字に挟まれた`x`↔"times"、Unicode上付き指数(`10⁻¹⁶`)・ASCIIキャレット指数(`10^-16`)↔話し言葉("N to the minus/negative M(th)?")。指数はxexpx(正)/xexpnegxマーカーで底・符号・桁を保持したまま区別し、Unicode上付き文字は`strip_diacritics()`のNFKD分解で情報が失われる前(`normalize_text()`の先頭)で処理する。**絶対にPASSさせてはならない差**(regression test固定): 数値が異なる(2≠3等)、時刻表記artifact(three≠3:00)、序数と基数の取り違え(28≠28th)、通貨/パーセント記号の欠落(5≠$5、5≠5%)、年の違い(2023≠2024)、否定の有無の違い、指数の符号・桁違い(10⁻¹⁶≠10⁻⁶、10⁻¹⁶≠10¹⁶)、小数値違い(0.90≠0.09)、係数違い(2×10⁻¹⁶≠2×10⁻¹⁵)、無関係な複数形の誤同一視(cats≠dogs)。記事個別のwhitelist(固有名詞の1対1ハードコード等)は使わない。Regression fixture: [er006_preprod_hardening_01_validation_test.py](er006_preprod_hardening_01_validation_test.py)(POSITIVE/AMBIGUOUS/NEGATIVE、計55件[既存32件+数式・複数形23件]、2026-08-24時点で全PASS確認済み) | `DECIDED` | ER-006-AUDIO-COST-PILOT-02(street/St.方針転換)、ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01(数値正規化の一般化、序数バグ修正)、ER-006-GATE-CALIBRATION-ASR-CASCADE-MATH-VALIDATOR-01(数式表記・複数形正規化の実装)、ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01(正式採用) | 2026-08-24 |
| Validator(日本語) | **2026-08-25新設、同日ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01で拡張**: [er007_ja_asr_validator_01.py](er007_ja_asr_validator_01.py)の`classify_ja_asr_match()`を、日本語Production Audio QAの標準Validatorとして採用(旧「文頭prefix一致+文字数チェック」方式を置き換え)。文字単位の全文sequence diff(`difflib.SequenceMatcher`)を取り、opcode単位で数字/否定マーカー/固有名詞らしさ(カタカナ列・英字acronym、`entity_like`)/濁点・半濁点の有無だけが異なる読みゆれ(`phonetic_uncertain`、清音化[NFD正規化+結合文字除去]による比較、「頃」のkakasi読み判定限界[goro/koro]対応)/読み完全一致(pykakasi、diff span前後4文字を文脈として付加してから比較)を個別判定する。5分類: EXACT_MATCH/NORMALIZED_MATCH/PHONETIC_MATCH(読み完全一致)/ASR_VALIDATION_UNCERTAIN(`entity_like`または`phonetic_uncertain`のみの差、Cascade対象)/TRUE_CONTENT_MISMATCH。**安全性**: `phonetic_uncertain`はCascade対象への分類のみに影響し、`should_pass`を直接Trueにはしない(誤PASSは構造的に発生しない)。**既知の残存限界**: (1)孤立漢字の異読み分岐のうち清音/濁音の関係にない異読み(例: 「後」のあと/のち)は依然未解消、(2)清音化後に偶然一致する意味の異なる実在語ペア(例: 柿/鍵)はCascadeへ余分に回りうる(誤PASSはしない、コスト増のみ)。**助数詞「つ」数字正規化**(2026-08-26、ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07で追加): 助数詞「つ」の直前に来る単独漢数字(一〜九)だけを算用数字へ揃える`normalize_kanji_counter_numerals_ja()`(`er003_audio_tts_asr_safety.py`)を`normalize_ja()`へ組み込んだ(例:"二つ"↔"2つ"を同値とする)。「二十」「二回」等、助数詞「つ」が続かない漢数字は対象外のまま(一般化しない、既存の数字保護は弱めない)。canonical textをASR表記に合わせて書き換えるのではなく、Validator側の同値正規化で吸収する方針を優先する(No.7 A2 comment_4で実証: canonical「二つ」・ASR「2つ」が`NORMALIZED_MATCH`でPASS)。Regression fixture: [er007_ja_asr_validator_01_test.py](er007_ja_asr_validator_01_test.py)(30件+voicingメカニズム一般性確認7項目、全PASS)、[er003_test_audio_tts_asr_safety.py](er003_test_audio_tts_asr_safety.py)の`JapaneseShortSegmentPhoneticMatchTests`(短いsegment用、同じ正規化を適用) | `DECIDED` | ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01、ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01(濁点/半濁点許容の追加)、ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07(助数詞数字正規化の追加) | 2026-08-26 |
| Pronunciation Ledger | 固有名詞の発音情報(Perplexity調査結果)を[er006_pronunciation_ledger_01.py](er006_pronunciation_ledger_01.py)でsurface+entity_typeをキーにcacheする。cache hitの場合は再調査(Perplexity再クエリ)を行わない。Perplexityへのクエリは、機械的に「1トピック1リクエスト」へまとめてはならない(個別/少数クエリのほうが品質が高いことを実測で確認済み、まとめるとconfidence low・hint空欄になる劣化を確認)。**Production配線範囲の明確化**: 現在Productionへ配線されているのは、Ledgerから取得した発音候補をSecondary ASRのPhrase List(`ledger_phrases`)へ渡す経路のみ(下記TTS Pronunciation Hintは未配線、次項参照) | `DECIDED(ASR側配線)` | ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01、ER-006-AUDIO-RETRY-CASCADE-PROD-01(Production 6箇所への配線) | 2026-08-22 |
| TTS Pronunciation Hint | [er006_pronunciation_tts_injection_01.py](er006_pronunciation_tts_injection_01.py)の`augment_style_prefix_with_pronunciation()`(発音ヒントをmeta/style instructionへ注入、読み上げ対象のspoken text本文自体は一切変更しない設計)は、Production基盤として保持する。個別語のphonetic respelling/whitelistは基本方式にしない。**ただし現時点でProduction 6箇所のTTS生成呼び出しには未配線**(A/Bテスト用script`er006_pronunciation_ab_01_run.py`でのみ使用実績あり)。理由: 最難関ケース"Ottoni"でのA/B検証(ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01)で、TTS発音ヒント注入の確実な改善効果を実証できなかった(mixed/負の結果)ため、Production TTS生成への強制配線は見送っている。基盤としては維持しつつ、配線判断は追加検証待ちの状態を正直に記録する(→[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-47) | `DECIDED(基盤として保持)` / `NOT_WIRED(TTS生成側)` | ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01(A/B検証、mixed/負の結果) | 2026-08-22 |
| ASR-first Retry Policy(固有名詞ASR不確実性、英語) | 固有名詞のASR不一致が疑われる場合、**TTSを即座に再生成しない**。以下の順序でASR側の再検証を先に尽くす: ①OpenAI Primary ASR #1 → ②Primary #2(必要時) → ③Azure Secondary ASR + Phrase List #1(entity-like mismatch検出時のみ) → ④Secondary #2(必要時) → ⑤それでも未解決ならHuman Review行き。実装は[er006_secondary_asr_01.py](er006_secondary_asr_01.py)の`evaluate_attempt_with_cascade()`(`CASCADE_CONFIG`: max_primary_attempts=2, max_secondary_attempts=2)。「Primary ASR FAIL→即Gemini TTS再生成」という旧経路への後退を禁止する。**`FEATURE_FLAG_SECONDARY_ASR_ENABLED`は2026-08-24付でProduction既定`True`(ON)** (ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01。旧OFF状態はOPEN-48で「追加検証待ち」としていたが、実No.6 Sweeny audio 2件[B1/A2]でCascadeが正しく起動しTTS再生成0件でHuman Reviewへ到達することを実音声で確認、既存Ottoni/Boavida系mock fixtureおよび数値/true content mismatch fixtureで真の内容誤りが誤PASSされないことも確認した上で有効化)。Production call site 6箇所は全て`cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED`という形で呼び出し時にモジュール定数を参照するため、この1箇所のフラグ変更のみで全call siteへ反映される | `DECIDED` / `WIRED(ON)` | ER-006-AUDIO-RETRY-CASCADE-PROD-01(Production 6箇所へ配線、3 Topic実測でtrue content誤PASS 0件、new savings+¥128.4)、ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01(feature flag ON化) | 2026-08-24 |
| ASR-first Retry Policy(固有名詞ASR不確実性、日本語) | **2026-08-25新設**: 英語と同じ思想を日本語へ適用。固有名詞・略語らしき語のみのASR不一致(entity-like)が疑われる場合、TTSを即座に再生成せず①OpenAI Primary ASR #1 → ②Primary #2(必要時) → ③Azure Secondary ASR #1(entity-like mismatch検出時のみ) → ④Secondary #2(必要時) → ⑤それでも未解決ならHuman Review行きの順で再検証する。実装は[er007_ja_secondary_asr_01.py](er007_ja_secondary_asr_01.py)の`evaluate_attempt_ja_with_cascade()`(`CASCADE_CONFIG_JA`: max_primary_attempts=2, max_secondary_attempts=2)。`FEATURE_FLAG_JA_PRIMARY_OPENAI`はProduction既定`True`(ON、Cascade自体も有効)。Production call site 3箇所(`er003_v1_repro01_main_generate.py`のJapanese分岐、`er003_v1_sing01_voice01_generate.py`、`er003_v1_n3_01_tts_generate.py`)は全て`cascade_enabled=ja_secondary.FEATURE_FLAG_JA_PRIMARY_OPENAI`という形でモジュール定数を参照する。実音声smoke test([verify_ja_cascade_production_on.py](verify_ja_cascade_production_on.py))でProduction call siteと同一の呼び出し方によりOpenAI Primaryが実際に呼ばれ分類が破綻しないことを確認済み。**2026-08-25追記(ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01)**: Cascadeが`stop_retrying=True`(Cascadeを尽くしても未解決)を返した後、`er003_v1_sing01_voice01_generate.py`・`er003_v1_n3_01_tts_generate.py`の自前retry loopがこれを無視してTTS再生成を続けるbugを修正した(`er003_v1_repro01_main_generate.py`は元々正しく短絡していた)。修正後はmock test([er007_ja_tts_retry_path_fix_test_01.py](er007_ja_tts_retry_path_fix_test_01.py))でTTS生成回数が1回で打ち切られることを確認済み | `DECIDED` / `WIRED(ON)` | ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01、ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01(stop_retrying無視bug修正) | 2026-08-25 |
| TTS Retry条件(絞り込み) | TTS音声の再生成(regenerate)は、以下に該当する場合のみ行う: 真の内容誤り(true content mismatch)、数値/年/日付の意味的な違い、否定の有無の違い、重要語の欠落・追加、TTS技術的失敗(hallucination・INVALID_ARGUMENT等)、Human Reviewで実際の音声誤りと確認された場合。**固有名詞のASR表記ゆれのみを理由とした繰り返しTTS再生成は行わない**(上記ASR-first Retry Policyでのre-verificationを先に尽くす) | `DECIDED` | ER-006-AUDIO-RETRY-CASCADE-PROD-01 | 2026-08-22 |
| Human Review Route | Cascadeを尽くしても未解決の固有名詞/ASR不確実性ケースは、API呼び出しを重ねてSTOPPEDにし続けるのではなく、Human Review queueへ送る。Queueは最低限以下を保持する: canonical text、audio、発音メタデータ(Pronunciation Ledgerのhint)、Primary ASR transcripts、Secondary ASR transcripts、判定理由(classification/reason)。ログ実装: `HUMAN_REVIEW_LOG_PATH`(`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`) | `DECIDED` | ER-006-AUDIO-RETRY-CASCADE-PROD-01 | 2026-08-22 |
| Production TTS/ASR call site一覧 | `er003_v1_crosslevel_audio_02_common.py`、`er003_v1_repro01_main_generate.py`(2箇所)、`er003_v1_sing01_news_tail_fix.py`、`er003_v1_sing01_point_headings_aoede.py`、`er003_v1_sing01_voice01_generate.py`、`er003_v1_n3_01_tts_generate.py`の計6ファイルが、本節のASR Routing/Validator/Pronunciation Ledger(ASR側)/ASR-first Retry Policyを実際に配線しているProduction leaf pathである。Legacy/experimental script(A/Bテスト用`er006_batch_ab_01_generate.py`・`er006_pronunciation_ab_01_run.py`等)はProduction scope外であり、上記経路とは区別する。**2026-08-25更新**: このうち日本語分岐を持つ`er003_v1_repro01_main_generate.py`(`generate_narration_snippet_verified_strict`のJapanese分岐)、`er003_v1_sing01_voice01_generate.py`(`generate_charon_japanese`)、`er003_v1_n3_01_tts_generate.py`(`generate_a2_japanese_with_fallback`)の3ファイルへ、日本語Validator+Cascade(`er007_ja_asr_validator_01.py`/`er007_ja_secondary_asr_01.py`)を配線した(ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01) | `DECIDED`(範囲の明確化) | ER-006-AUDIO-COST-SPEC-FIX-01(Static Audit対象範囲の確定)、ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01(日本語3箇所への配線) | 2026-08-25 |

### Cost定義(Audio Production)

ER-006以降のAudio Cost報告は、以下4区分を共通言語として使う
(過去の報告で「実費」「想定コスト」等の曖昧な語を単一の数字として
混同していた反省を踏まえる、ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01
で初めて明確化)。

| 用語 | 定義 | 現在の基準値(1 Topic=B1+A2 pair) | 備考 |
|---|---|---|---|
| Historical Actual | 実際に支払われた金額(過去ログの実測合計そのもの) | ログごとに異なる(単一の固定値なし) | `er005_cost_logger.py`の`raw_usage_log.jsonl`から集計 |
| Clean Production Cost | 全工程が初回attemptで成功した場合に必要な費用(retry・研究・Cascade等の追加費用を一切含まない理論下限) | ¥65.14/pair | ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01で再構築 |
| Expected Conditional Waste | 条件付きで発生しうる追加費用の期待値(Primary ASR #2、Secondary ASR Cascade、Pronunciation Research、TTS retry等) | ¥46.03/pair | 実測1.68倍のTTS/ASR retry・Pronunciation Research実測cache miss率・Secondary ASR保守的estimateを合成 |
| Expected Production Cost | Clean Production Cost + Expected Conditional Waste | ¥111.17/pair | **この値はestimateを含む進化中のbaselineであり、恒久的な固定値ではない**。特にSecondary ASR Cascade発動率(1回/topic、ESTIMATE)はランダムサンプル未検証のまま(→[OPEN_ITEMS.md](OPEN_ITEMS.md)のOPEN-49) |

**過去の報告値との関係**: ER-006-AUDIO-COST-PILOT-02の¥106.4/pairと
ER-006-AUDIO-RETRY-CASCADE-PROD-01の¥113.0/pairは、いずれも今後
参照しない(前者はPronunciation/Cascade費用未計上、後者は根拠の薄い
仮定「1.3回/topic」を使用していた)。¥111.17/pairが現時点の正である。

## Model Routing Contract

Single Source of Truth: [er006_model_routing_contract_01.py](er006_model_routing_contract_01.py)
(`PROCESS_MODEL_MAP`/`PROCESS_PROVIDER_MAP`、`require_model()`/`require_provider()`)。

| Process | Approved Model/Provider | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| Query Planning | GPT-5.6 Luna | `DECIDED` | ER-005以前から(gather_topic.py) | - |
| Topic Selection | GPT-5.6 Luna | `DECIDED` | ER-005以前から | - |
| Evidence Pack / VFL / Verification | GPT-5.6 Luna | `DECIDED` | ER-006-POOL-PILOT-01(新規構築時から) | 2026-08-21 |
| Exception Search | Perplexity Search API | `DECIDED` | ER-006-POOL-PILOT-01 | 2026-08-21 |
| B1 Writer / A2 Writer(Deviation Check含む) | GPT-5.6 Luna | `DECIDED`(Solから変更) | ER-006-MODEL-ROUTING-CONTRACT-01 | 2026-08-22 |
| Writer Fact Check | GPT-5.6 Luna | `DECIDED`(Solから変更) | ER-006-MODEL-ROUTING-CONTRACT-01 | 2026-08-22 |
| B1 Support / A2 Support(Key Phrase選定・正規化含む) | GPT-5.6 Luna | `DECIDED`(Solから変更) | ER-006-MODEL-ROUTING-CONTRACT-01 | 2026-08-22 |
| Support Fact Check | GPT-5.6 Luna | `DECIDED` | ER-005-SUPPORT-COST-QUALITY-01系実装をER-006 Pool Pilotで採用、ER-006-MODEL-ROUTING-CONTRACT-01で正式契約化 | 2026-08-22 |
| TTS | Gemini `gemini-2.5-pro-preview-tts`(英語)/`gemini-3.1-flash-tts-preview`(日本語)。呼び出し方式はBatch API(`client.batches.create()`)がApproved方式であり、**Production call site全6箇所へ実配線済み**(詳細はAudio Production Pipeline節「Gemini TTS実装方式」) | `DECIDED` / `WIRED` | プロジェクト全体方針(model)、ER-006-AUDIO-COST-SPEC-FIX-01(Batch方式の正式化)、ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01(Production実配線) | 2026-08-22 |
| ASR / Audio QA | **2026-08-25更新: 英語・日本語ともOpenAI `gpt-4o-mini-transcribe`(Primary)、AzureはSecondary Cascade用**。SSOTは[er006_asr_provider_routing_01.py](er006_asr_provider_routing_01.py)(`ASR_ROUTING`/`require_asr_route()`)であり、本Routing Contractの`ASR_PROVIDER`定数(`"azure"`固定)は既存test互換のためのみ残す未配線の値である(詳細はAudio Production Pipeline節「Primary ASR Routing」) | `DECIDED` | ER-006-AUDIO-COST-PILOT-02、ER-006-AUDIO-COST-SPEC-FIX-01(Contract表への反映)、ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01(日本語Primary切替) | 2026-08-25 |

**Fail-Closed契約**: 上記いずれの工程も、規定外Model/Providerが指定された場合、または
Model未指定でSDK defaultへ落ちる場合は、API call実行前に`ModelContractViolation`を
送出する(fallbackとして高価なmodelへ自動昇格しない)。Regression test:
[er006_model_routing_contract_01_test.py](er006_model_routing_contract_01_test.py)、
Static audit: [er006_model_routing_contract_01_static_audit.py](er006_model_routing_contract_01_static_audit.py)。

**適用範囲の注記**: Writer/Support系のSSOT配線は、production到達可能な呼び出し箇所
(N3/Pool pipeline: `er003_v1_n3_01_articles_generate.py`・
`er003_v1_n3_01_scaffold_generate.py`・`er006_pool_pilot_01_*.py`)にのみ適用した。
Translation pipeline・CEFR/spoken-first系の過去の実験タスク等、この契約の対象外と
した箇所は、既存のSol既定値のまま変更していない(該当箇所は
ER-006-MODEL-ROUTING-CONTRACT-01完了報告のAudit一覧を参照)。

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
ER-003-B1-NOVEL-AUDIO-01系レポート(Support English化・Voice役割再配置)、
ER-003-A2-B1-N3-01完了報告(3ジャンル横展開: Hanshin/Health/Household)、
ER-003-A2-B1-N3-01-FIX-01完了報告、ER-003-N3-RCA-01完了報告、
ER-003-N3-ROOT-FIX-01完了報告(Key Phrase trim margin・TTS instruction責務分離・A2 Core Logic Preservation)、
ER-003-N3-ROOT-FIX-VERIFY-01完了報告(3ジャンルでのA2 Core Logic Preservation検証)、
ER-003-B1-A2-SPEC-FREEZE-01-R1完了報告(SoT内部整合性クリーンアップ)、
ER-003-B1-B2-SCOPE-FIX-01完了報告(B1生成仕様確定・B2 Launch Scope整理)、
ER-006-AUDIO-COST-OPTIMIZATION-01完了報告(Batch/Master Audio/ASR代替の調査)、
ER-006-AUDIO-COST-PILOT-02完了報告(ASR Provider Routing・Master Audio最小実装)、
ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01完了報告(発音Ledger・Secondary ASR)、
ER-006-AUDIO-RETRY-CASCADE-PROD-01完了報告(Cascade Production配線)、
ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01完了報告(Validator一般化・Cost再構築)、
ER-006-AUDIO-COST-SPEC-FIX-01完了報告(本節・Model Routing Contract更新のSSOT統合)、
ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01完了報告(Gemini TTS Batch API実配線・ASR旧記述整合化)、
[DECISION_LOG.md](DECISION_LOG.md)
