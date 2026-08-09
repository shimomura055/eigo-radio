# A2_PROTOTYPE_SPEC — CEFR-A2 言語仕様候補(プロトタイプ)

**管理ID: ER-003-A2-01〜A2-03、ER-003-A2-STRUCT-02**
**最終更新: 2026-08-09**
**ステータス: 文書全体が`PROTOTYPE`。個々の項目の状態(ADOPTED/REJECTED/PROTOTYPE継続)は表内で明示する。**

## この文書の位置づけ

CEFR-A2は現時点で**全体としてまだ`DECIDED`ではない**([CURRENT_SPEC.md](CURRENT_SPEC.md)の
CEFR節を参照。同ファイルには確定仕様のみを書くというルール上、A2の
詳細な検証経緯・候補・却下項目はここにまとめる)。本文書はA2-01→A2-02→
A2-03→A2-STRUCT-02の一連の検証で得られた言語仕様の**現時点の候補**を
整理したものであり、CURRENT_SPECへの正式昇格(DECIDED化)はユーザーの
別途承認を要する。

**正式なCURRENT_SPECとの混同防止**: 表内の「ADOPTED」は「今後のA2生成
方針として採用する」という意味であり、CEFR-B1/B2のようにCURRENT_SPECへ
`DECIDED`として記載された確定仕様と同列ではない。A2全体がPrototype段階
である間は、この文書がA2言語仕様の一次参照先となる。

## 維持する項目(A2-01〜A2-03を通じて有効と確認済み)

| 項目 | 内容 | 状態 | 根拠Decision |
|---|---|---|---|
| 生成元 | Natural English Sourceから独立生成(B1/B2/A2の過去バージョン本文は入力に使わない) | `PROTOTYPE`(恒久方針としての確定はユーザー判断待ち、[OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-02) | ER-003-A2-01〜03 |
| 情報量 | 総語数を意図的に削らない。B1と同等程度の主要情報量を保持してよい | `PROTOTYPE` | ER-003-A2-02 |
| Full Storyの役割 | Full Storyだけでニュースの核心が分かる。Point One/Twoは深掘り・背景・意味付けの役割とし、Full Storyの代替にしない | `PROTOTYPE` | ER-003-A2-02 |
| 平均文長 | 11語以下 | `PROTOTYPE` | ER-003-A2-01〜03 |
| 最長文 | 18語以下 | `PROTOTYPE` | ER-003-A2-01〜03 |
| 1文1メッセージ | 原則1文1メッセージ | `PROTOTYPE` | ER-003-A2-01〜03 |
| 構文単純化 | SVO中心、関係詞節は原則回避、分詞構文を避ける、複雑な受動態を避ける、完了形等の複雑な構造は必要最小限 | `PROTOTYPE` | ER-003-A2-01〜03 |
| 語彙の一般方針 | A2として可能な範囲で平易な一般語を優先する(**数値上限は設けない**、下記「不採用」参照) | `PROTOTYPE` | ER-003-A2-STRUCT-02 |
| **Spoken-first** | 主語を早く出す、動詞を早く出す、長い前置詞句・名詞句を文頭に置きすぎない、文末まで聞かないと意味が確定しない構造を避ける。自然な英語らしさを優先し、厳格なsyntax validatorにはしない(style / generation principleとして運用) | **`ADOPTED`**(A2の継続仕様) | ER-003-A2-STRUCT-02 |
| 1文1数字 | 数字は原則1文1つ。年齢範囲・スコア・時間帯・**日付(月+日+年)**等、1つの意味単位として結合している表現は例外 | `PROTOTYPE`(継続。日付を例外に含める方針は確定したが、checker実装[`er003_a2_article.py`の`_EXEMPT_NUMBER_PATTERNS`]は未着手、[OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-18) | ER-003-A2-03、ER-003-A2-STRUCT-02 |

## 不採用とした項目(A2-03で検証したが採用しない)

| 項目 | 内容 | 状態 | 却下理由(要約) | 根拠Decision |
|---|---|---|---|---|
| A2超一般語 最大5語 | 記事全体でA2超の一般語を5語までに制限する数値ルール | `REJECTED` | 正式wordlist不在でLLM判定が不安定、反復修正が必要で量産フローが複雑化、効果が複雑化に見合わない | [DECISION_LOG.md](DECISION_LOG.md) |
| 抽象語→具体的行動表現への一律変換 | 抽象表現を「誰が何をしたか」へ優先的に変換する一般ルール | `REJECTED_AS_GENERAL_RULE` | 具体化が有効な場合もあるが、無理な変換で意味関係が不明瞭になる・説明が長くなる場合もあり一方向ルールにできない | [DECISION_LOG.md](DECISION_LOG.md) |
| 固有名詞密度低減 | 固有名詞のtoken数・密度を意図的に下げる一般ルール | `REJECTED` | 「誰が何をしたかの明確化」「spoken-first」等、別の分かりやすさ要求と競合する場合がある。数量目標は設けず通常の編集判断に委ねる | [DECISION_LOG.md](DECISION_LOG.md) |

## 過去に不採用と確認済みの項目(A2-02より前、再確認は不要)

| 項目 | 状態 |
|---|---|
| 1文1新情報(1文1メッセージより厳格な、1文に新概念を1個だけとするルール) | `NOT_ADOPTED`(ER-003-A2-03で明示的に不採用と指定、英語として不自然になるリスクのため) |
| 重要語の機械的反復(同じ名詞を毎回繰り返すルール化) | `NOT_ADOPTED`(自然な代名詞・言い換えを許容) |
| 使用文型の限定("X is Y"等の特定文型のみに制限) | `NOT_ADOPTED`(英語らしさの維持を優先) |
| B1主要情報の70〜80%程度を残す(情報量の目安としての残存率) | `NOT_ADOPTED`(ER-003-A2-02で廃止、総語数を難易度指標として使わない方針へ転換) |

## 構造支援候補(言語仕様とは別枠)

構造支援(Full Story分割+日本語コメント、簡易Listening Questions)は、
A2の**言語仕様**とは別の検討軸として[OPEN_ITEMS.md](OPEN_ITEMS.md)の
OPEN-13/OPEN-14で管理する。Candidate A(Full Story分割+日本語コメント)
はER-003-A2-STRUCT-02/03でA02のプロトタイプを完成済み
(`PROTOTYPE_BUILT / UNDER_EVALUATION`、11パート構成: Preview→Key
Phrases→Comment1→Full Story Part1→Comment2→Full Story Part2→
Comment3→Point One→Point Two→Comment4→In One Line)。設計根拠は
[ER-003-A2-STRUCT-02_A02_PROTOTYPE.md](ER-003-A2-STRUCT-02_A02_PROTOTYPE.md)、
Preview〜In One Lineを通した1本の統合台本は
[ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md)
(QAは[ER-003-A2-STRUCT-03_REPORT.md](ER-003-A2-STRUCT-03_REPORT.md))を参照。
Candidate B(Listening Questions)は未着手のまま。

**一般化の際の役割フレームワーク**(他記事へ適用する場合、文言では
なく役割のみを再利用する):

| コメント | 役割名 | 機能 | 長さ目安 |
|---|---|---|---|
| Comment 1 | Listening Focus | 次の英語で何を聞くかを示す(答えは言わない) | 原則1文 |
| Comment 2 | Mid-story Recovery + Next Question | Part 1の重要点を1点回収し、Part 2への問いを提示 | 1〜2文 |
| Comment 3 | Story Meaning + Bridge to Points | Full Story全体の論点を整理し、Pointsへの橋渡し | 2〜3文 |
| Comment 4 | Point Recovery + Bridge to In One Line | Points の意味を回収し、In One Lineへつなぐ | 2〜3文 |

**Full Story分割位置の優先順位**(機械的な均等分割はしない):
①意味上の転換点 ②時系列上の転換点 ③問題→例外 ④発表→反応
⑤What happened→What happened next / Why it matters

## まだ全く仕様が存在しない項目(CEFR-A2全20項目監査より、A2-01〜03で未着手のもの)

以下は[ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md)で監査
済みだが、A2-01〜A2-03のいずれでも扱っていない項目。引き続き`TBD`。

- Key Phrase選定条件(A2本文確定後に方式L+Canonicalizationで別途選定予定)
- Preview固有ルール(既存Preview仕様の流用を想定、A2固有の調整は未検討)
- タイトル・Point One/Point Two/In One LineのA2固有ルール(構造はB1と共通、CEFR別の追加ルールは未検討)
- 音声速度・TTS条件のA2固有差(仕組み自体が存在しない、変更予定なし)

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[CURRENT_SPEC.md](CURRENT_SPEC.md)、
[DECISION_LOG.md](DECISION_LOG.md)、[OPEN_ITEMS.md](OPEN_ITEMS.md)、
[ER-003-A2-01_TEXT_VERIFICATION.md](ER-003-A2-01_TEXT_VERIFICATION.md)、
[ER-003-A2-02_INFO_BALANCE_VERIFICATION.md](ER-003-A2-02_INFO_BALANCE_VERIFICATION.md)、
[ER-003-A2-03_LISTENING_SIMPLIFICATION.md](ER-003-A2-03_LISTENING_SIMPLIFICATION.md)
