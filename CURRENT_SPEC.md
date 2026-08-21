# CURRENT_SPEC — 現在有効な正式仕様

**管理ID: ER-PM-001**
**最終更新: 2026-08-17(ER-003-B1-B2-SCOPE-FIX-01、B1生成仕様確定・B2 Launch Scope整理)**

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
| TTS | Gemini `gemini-2.5-pro-preview-tts` | `DECIDED` | プロジェクト全体方針 | - |
| ASR / Audio QA | Azure Speech-to-Text | `DECIDED` | プロジェクト全体方針 | - |

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
[DECISION_LOG.md](DECISION_LOG.md)
