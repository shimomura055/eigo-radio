# ER-010-EDITORIAL-TYPE-WRITER-ARCH-01 — 現行Writer仕様分解とEditorial Type導入設計

**管理ID: ER-010-EDITORIAL-TYPE-WRITER-ARCH-01**
**種別: 調査・分解・Architecture設計のみ(Production変更なし)**
**作成日: 2026-08-31**

用語メモ(このファイル内で繰り返し出てくるもの):
- **Writer**: 記事本文(Full Story・Point One・Point Two・In One Line)を生成するLLM呼び出し。
- **Verified Fact Ledger(VFL)**: 記事ごとに1つ作る「確認済みFactの一覧」。WriterはこのLedgerに書かれていない事実を勝手に足してはいけない、という安全装置。
- **Point**: 番組内の「Point One」「Point Two」という深掘りセクションのこと(本文の後、In One Lineの前)。
- **Overlap(重複)QA**: PointがMain Storyの言い換えになっていないかを機械的にチェックする仕組み。

---

## 1. 調査対象Production path

現行、実際にProduction(本番)で記事本文を生成しているのは以下の呼び出し経路である。

```
[人間が用意したTopic/Title/Ledger]
      │
      ▼
er006_pool_pilot_01_writer.py :: run_writer_for_theme()
      │  (「er003_v1_n3_01_articles_generate.py の本番run_one_pattern()をそのまま
      │   呼び出す薄いwrapper」とコード冒頭コメントに明記)
      ▼
er003_v1_n3_01_articles_generate.py
  ├─ build_common_block() / COMMON_BLOCK_TEMPLATE   … 全レベル共通の記事Prompt
  ├─ B1_B_DIRECT_INSTRUCTION / A2_KAI1_INSTRUCTION   … レベル別の難易度Instruction
  ├─ run_one_pattern()
  │    ├─ Writer呼び出し(vfl01.run_writer_with_technical_retry)
  │    ├─ Evidence Compression Editor(既定ON)
  │    ├─ Point Overlap QA + Diagnostic Full Retry(最大2回、記事全体再生成)
  │    ├─ Fact Checker(er002_ja_web_research_r3.py)
  │    ├─ Ledger Deviation Check(er003_v1_en_direct_vfl_01_generate.py::run_deviation_check)
  │    └─ Directional Fact Precheck(er008_directional_fact_precheck_08.py)
      ▼
er003_v1_n3_01_scaffold_generate.py
  ├─ Preview/Comment1-4 (b1s= er003_v1_b1_scaffold_01_generate.py,
  │                       a2gen=er003_v1_iran01_a2_generate.py の ROLE定数を再利用)
  └─ Key Phrase選定(er003_key_words_production.py等)
      ▼
er003_v1_n3_01_tts_generate.py → er003_v1_n3_01_assemble.py (TTS・組み立て・Audio Validation Gate)
```

No.8・No.9等、実際の番組回(Pool N-series)は、上記の共有関数をimportして
Topic/Titleだけを差し替える専用runner(例: `er009_n1_production_integration_01.py`)
から呼ばれている。パイプライン自体は使い回し、新しいWriterロジックを回ごとに
作り直してはいない。

**モデル**: Writer・Writer Fact Check・Support(Preview/Comment/Key Phrase)は
いずれも `GPT-5.6 Luna`(CURRENT_SPEC.md「Model Routing Contract」節、
`er006_model_routing_contract_01.py`がSSOT)。

---

## 2. CURRENT_SPEC確認結果

CURRENT_SPEC.md(438行)を全文確認した。今回のタスク指示との**重大な差異はなかった**。
指示にある「5 Editorial Type構想」「Voices Trial」という**用語**は、CURRENT_SPEC・
DECISION_LOG・OPEN_ITEMS.mdのいずれにも一言も存在しない(`Editorial Type`/`Voices`等で
リポジトリ全体をgrepしても0件)。つまり本タスクは既存仕様との整合性問題ではなく、
**まったく新しい設計軸を既存Productionへどう挿入するか**という設計問題である。

**ただし、概念としては過去に一度、非常に近いものが試みられ、廃棄されている**
(用語が違うため今回の事前grepでは見つからず、調査補助エージェントの詳細探索で
発見した)。`er002_editorial_angle_adapter.py`/`er002_editorial_common.py`
(2026年7月、現行のer003/er006/er008/er009系のどこからもimportされていない
`HISTORICAL`)は、1つのVerified Factsから**3つの異なる編集Angle**を提案させ、
別モデルロールによる独立Diversity評価(`central_tension_or_question`・
`point_one_editorial_role`/`point_two_editorial_role`の組み合わせ・
`non_obvious_takeaway`が3案間で実質的に異なるか)でスコアリングするCoding設計
だった。`point_one_editorial_role`/`point_two_editorial_role`は
`cause_explanation`/`consequence_or_stakes`/`counterpoint_or_tension`/
`human_or_concrete_detail`/`context_or_comparison`/`mechanism_or_process`の
6値から選ぶ設計で、これは今回のEditorial Type構想における「Point/Perspectiveの
役割」を型として明示するアイデアの先行事例そのものである。

これは2026-07-19、ユーザーが試聴の上「**台本は事実の羅列に近く、切り口が弱い**」
と評価して`REJECTED`となった(HISTORY_INDEX.md)。その後、現行の
Master記事模倣方式(阪神記事のスタイル模倣、8月導入)へ方針転換した経緯がある。
**同じ「事実の羅列っぽい」という質の課題(後述OPEN-91)が、方式を変えても
形を変えて再発している**、という点は今回のEditorial Type設計で軽視すべきでない
(11節の次Stepに反映)。

現行Production仕様のうち、今回の設計に直接関係する既存決定事項:
- CEFR-A2/B1はそれぞれ独立したWriter呼び出しで生成する(同じLedgerを共有し、
  別Writerで独立生成、CURRENT_SPEC「B1」節)。この**難易度軸**と、今回導入したい
  **Editorial Type軸**は直交する別軸である。
- A2構造は11パート固定(Preview→Key Phrases→Comment1→Full Story Part1→
  Comment2→Full Story Part2→Comment3→Point One→Point Two→Comment4→
  In One Line、CURRENT_SPEC「CEFR-A2構造・音声仕様」節)。
- Point Balance(言い換えによる重複禁止)は2026-08-29に`PRODUCTION_WIRED`化
  されたばかりの最新仕様であり、まさに今回のCommon/Discovery分解の核心にあたる。

---

## 3. 現行Writerの全体構造

現行Writerが生成する記事は、常に以下の固定4ブロック構造(Markdown)である
(`COMMON_BLOCK_TEMPLATE`、[er003_v1_n3_01_articles_generate.py:116-129](er003_v1_n3_01_articles_generate.py:116)):

1. `# Title`
2. Main Story(本文、複数段落。**現在のFull Story Part1/Part2に対応**)
3. `###`見出し **ちょうど2つ**(Point One相当・Point Two相当。見出し文字列自体に
   "Point One"等の番号ラベルは含めない)
4. `## In one line`(結び、1〜2文)

この4ブロックのうち、Main Storyだけが「中心ストーリーの核心」を担い、
Point One/Twoは「本文とは別の切り口・示唆・背景・心理・社会的含意」を**短く**
付け加える場所、という役割分担が明示的にInstructionへ書かれている
([er003_v1_n3_01_articles_generate.py:131-152](er003_v1_n3_01_articles_generate.py:131))。

この記事本文Writerの前段には**Master記事模倣**という仕組みがある。過去に
ユーザーが「良い」と評価した阪神タイガース戦の記事(Hanshin Master)を
スタイル参照として毎回のPromptに埋め込み、「このセンスを活かして今回のテーマの
記事を書いてください」と指示する([er003_v1_n3_01_articles_generate.py:99-114](er003_v1_n3_01_articles_generate.py:99))。
これはSports/Health/Household等、**ジャンルを問わず同一のMaster記事を使う**設計であり、
「1本の筋(概要展開)+深掘り2点+一言まとめ」という単一のNarrative形を
事実上すべてのトピックへ適用していることを意味する。

---

## 4. Writer Instruction Map(現行Instruction/Prompt領域の分解)

| 現行Instruction/Prompt領域 | 実際の内容 | 現在の供給元 | Common/Discovery固有/Article固有 | 根拠 | Editorial Type導入時の扱い案 |
|---|---|---|---|---|---|
| Master記事模倣 | 阪神戦記事(Hanshin Master)をスタイル参照として全ジャンル共通で埋め込み、「このセンスを活かして書け」と指示 | `COMMON_BLOCK_TEMPLATE`冒頭、[articles_generate.py:99-114](er003_v1_n3_01_articles_generate.py:99) | **Discovery/Why固有**(単一Narrative Arcの見本を全記事に強制) | コード実物 | Editorial Type Moduleで置換対象。Voicesでは別サンプルを用意するか、模倣方式自体をやめてrole説明に置き換える |
| 記事の物理構成(Title/Main Story/`###`×2/`## In one line`) | 4ブロック構造。`###`は**ちょうど2つ**という数値制約 | 同上、[articles_generate.py:116-129](er003_v1_n3_01_articles_generate.py:116) | 外枠(Title/本体/見出しブロック/結び)は**Common**寄り。**「見出しブロックが2つ固定」はDiscovery固有**の設計判断 | コード実物、`split_common_sections_for_point_qa()`が`h3_matches != 2`ならNoneを返す([articles_generate.py:419-421](er003_v1_n3_01_articles_generate.py:419)) | 外枠はCommonとして残す。「2つ固定」はVoicesの2〜4可変要件と直接衝突するため要判断(詳細は7節) |
| Main Storyの役割定義 | 「何が起きるか・誰が対象か・仕組み・現状」の核心のみ。背景/補助数値/別角度/深い含意はPointへ追い出す | [articles_generate.py:131-139](er003_v1_n3_01_articles_generate.py:131) | **Discovery/Why固有**(単一の筋を追うニュース解説の型) | コード実物 | Editorial Type Module化。Voicesでは「Main Story」の役割自体を「Question/Hook」へ再定義する必要 |
| Point One/Twoの役割定義 | 本文とは別の切り口・示唆・背景・心理・社会的含意・別の因果・実生活上の解釈・意味づけ | [articles_generate.py:141-152](er003_v1_n3_01_articles_generate.py:141) | **Discovery/Why固有**(「本文への追加視点」という設計。複数の並立した立場ではない) | コード実物 | Voicesでは「Perspective 1/2」の役割(立場→重視点→見え方)へ置換 |
| Point-Main Story言い換え重複禁止 | 中心logic・結論を語彙だけ変えて再説明することを明示的に禁止(2026-08-29に実API A/B比較で効果確認、`PRODUCTION_WIRED`) | [articles_generate.py:154-177](er003_v1_n3_01_articles_generate.py:154)、CURRENT_SPEC.md L169 | **Discovery/Why固有**(比較対象がMain Story) | コード実物+CURRENT_SPEC | Voicesでは「Perspective同士の類似度」チェックへ比較対象を変更(要再設計、8節) |
| Point長さ目標 | 目標30〜60語/許容25〜70語(hard capではない) | [articles_generate.py:55-58,179-181](er003_v1_n3_01_articles_generate.py:55) | 数値自体は**Common化候補**(語数目安という仕組みは型を問わず必要) | コード実物 | Voicesの各Perspective目安(50〜70語、タスク指示10節)へ差し替え可能な設計にする |
| 記事全体語数目安 | 280〜420語程度(観察用、hard capではない) | [articles_generate.py:59-60,183-186](er003_v1_n3_01_articles_generate.py:59) | **Common** | コード実物 | 維持。ただしVoicesはHook短め+Perspective複数という配分が異なるため、内訳の意味は型ごとに変わる |
| Spoken-first数字ルール(A〜G) | 数字を削らない・変化の方向性優先・丸めてよい条件・同時比較は2つ以内・ANCHOR/EXACT_REQUIREDの扱い等 | [articles_generate.py:188-199](er003_v1_n3_01_articles_generate.py:188) | **Common**(Fact Safetyの一部、CURRENT_SPEC「Spoken-first Number Treatment」節でも型非依存の共通原則として明記) | コード実物+CURRENT_SPEC | そのまま全Type共通で維持 |
| Fact Ledger使用制約 | 新Fact追加禁止・correlation/causation混同禁止・個人向け推奨/危険な使用法の禁止・不使用Factを書き込まない | [articles_generate.py:201-216](er003_v1_n3_01_articles_generate.py:201) | **Common**(Fact Safetyの根幹) | コード実物 | そのまま全Type共通で維持。Voices仕様書12節の「Evidence is thick backstage, light on air」はこの既存原則と同じ思想であり、新規発明は不要 |
| Evidence Compression(訂正版、下記参照) | Writer生成**後**に別のLLM呼び出し(Lossless Editor)がspoken layerだけを軽量化。企業名・調査年等の一般化、近似数値の圧縮は許可、correlation→causation変換等のFact強化は絶対禁止 | `er003_v1_n3_01_evidence_compression_editor.py::run_lossless_editor()`、`run_one_pattern()`内で`apply_evidence_compression=True`が既定([articles_generate.py:570,588](er003_v1_n3_01_articles_generate.py:570)) | **Common**(Prompt文言ではなく別工程のため、Editorial Typeに関係なくそのまま動く) | コード実物+CURRENT_SPEC L256 | 全Type共通で維持 |
| B1難易度Instruction(`B1_B_DIRECT_INSTRUCTION`) | Clause Density/Long-distance Dependency等の診断的原則。hard rule(語数上限等)は追加しない | [articles_generate.py:311-348](er003_v1_n3_01_articles_generate.py:311) | **Common**(難易度軸はEditorial Type軸と直交) | コード実物+CURRENT_SPEC「B1」節 | 全Type共通でそのまま維持 |
| A2難易度Instruction(`A2_KAI1_INSTRUCTION`) | one idea at a time、Core Explanatory Logic Preservation原則含む | [articles_generate.py:350-356](er003_v1_n3_01_articles_generate.py:350) | **Common**(同上) | コード実物 | 全Type共通でそのまま維持。ただし「Preserve the core explanatory logic and decision rule」という文言はDiscovery/Whyの「Ledgerの判断軸」を暗黙に想定した表現であり、Voicesでは「立場ごとの重視点を単純化しても変えない」という言い換えが必要か要確認 |
| Preview Role | theme/problem/value/questionの4要素、turning pointを先出ししない | `PREVIEW_ROLE`、[er003_v1_b1_scaffold_01_generate.py:193-208](er003_v1_b1_scaffold_01_generate.py:193) | 枠組みはCommon寄りだが、「turning point」「問題意識」という言葉遣いは**単一の筋を持つ物語を想定**(Discovery寄りの含意) | コード実物 | 大枠は維持できるが、Voicesでは「turning point」を「なぜ見方が違うのか」という問いの立て方へ言い換える調整が要る |
| Comment1 Role(Listening Focus) | 次に何を聞くか、答えは言わない。原則1文 | [er003_v1_b1_scaffold_01_generate.py:146-154](er003_v1_b1_scaffold_01_generate.py:146) | **Common寄り**(放送構造上の役割であり、中身のNarrative型に依存しない) | コード実物 | そのまま維持可能 |
| Comment2 Role(Mid-story Recovery + Next Question) | 前半の要点を1点回収+後半への問い | [同上:156-165](er003_v1_b1_scaffold_01_generate.py:156) | **Discovery/Why寄り**(「本文前半/後半」という単一Main Storyの分割を前提) | コード実物 | Voicesで「Main Story」がHookに縮小される場合、Comment2の存在意義自体を見直す必要 |
| Comment3 Role(Story Meaning + Bridge to Points) | ニュース全体の意味を整理しPointへ橋渡し。答えは先出ししない | [同上:167-177](er003_v1_b1_scaffold_01_generate.py:167) | **Discovery/Why固有**(Point=深掘り2点の存在が前提) | コード実物 | Voicesでは「これから複数の異なる見方を聞く」という橋渡しへ役割を再定義 |
| Comment4 Role(Point Recovery + Bridge to In One Line) | 2つのPointの意味を軽く回収しIn One Lineへ | [同上:179-191](er003_v1_b1_scaffold_01_generate.py:179) | **Discovery/Why固有** | コード実物 | Voicesでは「なぜ見方が違うのかを軽く整理し、結びへ」という役割(=Tension/Difference相当)へ転用できる可能性あり(7節) |
| Topic/Verified Fact Ledger/Title/Japanese Title | 記事ごとに用意する入力一式 | `THEMES`辞書・各`er0XX_n1_..._production_XX.py`、例[er009_n1_production_integration_01.py:45-70](er009_n1_production_integration_01.py:45) | **Article-specific** | コード実物 | 変更なし。Voicesでは「Editorial Type: voices」というフィールドも同列の入力として追加する設計にする(19節) |
| Fact Checker(3段構成の1段目) | 独立したWeb検索付き検証、PASS/REVIEW_REQUIRED | [er002_ja_web_research_r3.py:241-266](er002_ja_web_research_r3.py:241)、article_text全体を渡すだけの汎用設計 | **Common**(構造非依存、記事全文だけを見る) | コード実物 | 全Type共通でそのまま利用可能 |
| Ledger Deviation Checker v2 | changed_fact/changed_scope等10種の意味変化検知、記事全文ベース | [er003_v1_en_direct_vfl_01_generate.py:464-548](er003_v1_en_direct_vfl_01_generate.py:464) | **Common**(構造非依存) | コード実物 | 全Type共通でそのまま利用可能 |
| Directional Fact Precheck | 比較方向反転(more/fewer等)のrule-based検知、記事全文ベース | `er008_directional_fact_precheck_08.py`、[articles_generate.py:714-727](er003_v1_n3_01_articles_generate.py:714)で呼び出し | **Common**(構造非依存) | コード実物+CURRENT_SPEC | 全Type共通でそのまま利用可能 |
| Point Overlap QA + Diagnostic Full Retry | Point文とMain Story本文のlexical overlap(閾値0.40)、flag時は記事全体を診断情報付きで最大2回再生成 | `er008_point_overlap_qa_18.py`、`er009_diagnostic_full_retry_modules_12.py`、[articles_generate.py:457-507,593-648](er003_v1_n3_01_articles_generate.py:457) | **Discovery/Why固有**(「Pointが本文の言い換えでないか」という判定軸そのものがDiscovery型の失敗モード) | コード実物+CURRENT_SPEC L294 | Voicesでは「Perspective同士が似すぎていないか」という別の判定軸への再設計が必要(比較対象・閾値とも要再検証、8節) |
| Shared Point Blueprint | `PointBlueprint`×2固定スキーマでPoint内容を事前計画。**現行mainの既定呼び出しでは`blueprint=None`のため未使用** | `er008_shared_point_blueprint_01.py`、[articles_generate.py:743-761,776-783](er003_v1_n3_01_articles_generate.py:743) | **Discovery/Why固有だが現状Production非稼働**(オプション引数のまま) | コード実物 | 現状影響なし。将来Diagnostic Full Retryに代えて再導入する場合はVoices非対応である点に注意 |
| Key Phrase選定 | 確定済み最終本文からStrategy L等で選定、構造非依存 | CURRENT_SPEC「Key Phrase」節、`er003_key_words_production.py`等 | **Common** | コード実物+CURRENT_SPEC | 全Type共通でそのまま利用可能 |
| Audio Validation Gate mandatory segment名・Point Notification | `point_one_heading`/`point_two_heading`等、**位置ベースの名前**で必須QA証跡・6% slowdown・Notification音挿入を管理 | [er003_v1_n3_01_assemble.py:166-169,244-257](er003_v1_n3_01_assemble.py:166)、CURRENT_SPEC L166 | 名前は"Point"だが実装は**位置ベース**であり、中身の意味がPerspectiveに変わっても**Commonとして再利用可能** | コード実物 | 見出しブロックが2つのままである限り、TTS/Assembly/QAコードの変更は不要(8節で詳述、重要な安心材料) |

---

## 5. Common / Discovery固有 / Article-specificの分解結果(まとめ)

**A. 全Editorial Typeで共通すべきもの(Common Writing Contract候補)**
- レベル別難易度Instruction(`B1_B_DIRECT_INSTRUCTION`/`A2_KAI1_INSTRUCTION`)— 難易度軸はType軸と直交
- Fact Ledger使用制約・Spoken-first数字ルール・Evidence Compression原則(Fact Safetyの根幹)
- Fact Checker → Ledger Deviation Check → Directional Fact Precheckの3段QA(いずれも記事全文ベースで構造非依存)
- Key Phrase選定・Model Routing Contract
- 放送shellの物理仕様(Preview→KP→Comment1→FullStoryPart1→Comment2→FullStoryPart2→Comment3→PointOne→PointTwo→Comment4→InOneLine の**位置**、pause/Notification音の秒数、TTS voice割当)
- Audio Validation Gate・disfluency QA・A2 6%slowdown等の**segment名ベースの機械QA**(中身の意味に依存しない)

**B. 現行Discovery/Why固有と思われるもの(Editorial Type Module候補)**
- Master記事模倣という仕組みそのもの、および模倣元(阪神戦記事)が体現する「単一の筋+深掘り2点+一言まとめ」という物語形
- Main Storyの役割定義(単一throughlineの核心のみを運ぶ)
- Point One/Twoの役割定義(本文への追加視点。並立する複数の立場ではない)
- Point-Main Story言い換え重複禁止ルールとその判定手段(Overlap QA/Diagnostic Full Retry)
- Comment2(前半/後半の回収)・Comment3(Points前振り)・Comment4(Points回収)のrole文言
- Preview roleの「turning point」という言葉が想定する単一の物語構造

**C. Article-specific Inputs**
- Topic(日本語の出来事・研究説明文)、Verified Fact Ledger、Title(英語)、Japanese Title、theme_id/出力先等の実行管理情報

---

## 6. Editorial Type導入後の推奨architecture

### 6.1 推奨方式: 部分Module置換(タスク指示の設計原則8に同意)

現行COMMON_BLOCK_TEMPLATEは1つの巨大な文字列(f-string)であり、Common要素
(Fact Ledger制約・Spoken-first数字ルール)とDiscovery固有要素(Master模倣・
Main Story役割・Point役割・重複禁止)が**物理的に同じテンプレート内**に混在
している([articles_generate.py:99-217](er003_v1_n3_01_articles_generate.py:99))。
したがって「Common Coreを共有しModuleだけ差し替える」を実現するには、まず
このテンプレートをCommon部分とNarrative部分に**物理的に分割するリファクタリング**
が前提として必要になる(今回は実施しない。次のステップとして明示する)。

分割後のイメージ:

```
Writer Prompt
  = COMMON_SAFETY_BLOCK        (Fact Ledger制約・Spoken-first数字ルール・Evidence Compression)
  + LEVEL_INSTRUCTION          (B1_B_DIRECT_INSTRUCTION / A2_KAI1_INSTRUCTION、既存のまま)
  + EDITORIAL_TYPE_MODULE      (Narrative模倣元・Main Story/見出しブロックの役割定義・重複/類似度ルール)
  + ARTICLE_INPUTS             (Topic / Verified Fact Ledger / Title)
```

Comment1〜4・Preview roleは、現状はB1/A2それぞれ専用モジュール内の定数
(`COMMENT_1_ROLE`等)として1つに固定されている。Editorial Type別に
差し替えるには、これらも**Type別のroleセットを持つ辞書/関数**へ変える必要が
あり、現状「role文言をType別にswitchする仕組み」自体が存在しない
(今回は設計するが実装はしない)。

### 6.2 最大の構造的制約: 「見出しブロックはちょうど2つ」という前提

今回の調査で判明した最も重要な事実は、「`###`見出しブロックはちょうど2つ」
という前提が、**Prompt文言だけでなく複数の独立したモジュールに分散して
ハードコードされている**ことである:

- `split_common_sections_for_point_qa()`が`h3_matches != 2`ならNoneを返す
  ([articles_generate.py:419-421](er003_v1_n3_01_articles_generate.py:419))
- `section_word_counts()`が`point_one`/`point_two`という固定2キーだけを返す
  ([er003_v1_spoken_first_01_r1_generate.py:77-79](er003_v1_spoken_first_01_r1_generate.py:77))
- `SharedPointBlueprint`が`PointBlueprint`×2の固定スキーマ
  ([er008_shared_point_blueprint_01.py:30-41](er008_shared_point_blueprint_01.py:30))
- Audio Validation Gate・disfluency QA必須segment・Point Notification挿入が
  `point_one_heading`/`point_two_heading`という**2つの固定名**を前提にしている
  ([er003_v1_n3_01_assemble.py:166-169](er003_v1_n3_01_assemble.py:166))

Voices仕様(タスク指示11節)は「Perspective数は2〜4でFlexible」を求めており、
これは上記すべてのモジュールに影響する**横断的な構造拡張**になる。

**推奨**: Voices Trial 1(No.10)は、見出しブロック数を**2つに限定した構成**
(Perspective 2つ)で行う。これはタスク指示11節の「2軸で十分に面白い場合は2」
というケースに完全に合致し、かつ上記のいずれのモジュールにも**コード変更を
要求しない**(見出しの中身の意味がPointからPerspectiveへ変わるだけで、
数・位置は変わらないため)。3〜4 Perspectiveへの対応は、この構造拡張が
必要になった時点で、別のER番号として計画することを推奨する。

---

## 7. Voicesで実際に差し替える範囲

見出しブロックを2つに限定したVoices Trial 1を前提に、COMMON_BLOCK_TEMPLATE相当と
Comment/Preview roleのうち、実際に差し替えが必要な範囲は以下の通り。

| 現行(Discovery/Why) | Voices版への置換方針 |
|---|---|
| Master記事模倣(阪神戦記事参照) | Voices向けの別サンプル記事を用意するか、模倣方式自体をやめてrole説明文へ置換(どちらが良いかは実際にドラフトして比較する必要あり、11節) |
| Main Story = 中心ストーリーの核心(単一の筋) | Main Story = Question/Hook(タスク指示10節: 30〜50語)+ 立場が分かれる問いの土台となる状況説明。現行の「Full Story Part1/2」という**長い**本文の枠に、**短い**Hookをどう収めるかは要検討(下記8節のミスマッチ参照) |
| Point One/Two = 本文への追加視点(深掘り) | Perspective 1/2 = 立場→何を重視しているか→だからどう見えるか(タスク指示11節)。「本文の言い換え禁止」ではなく「単純な賛成/反対の羅列にしない」「Perspective同士が異なる役割を持つ」という制約に置換 |
| Point-Main Story言い換え重複禁止 | Perspective同士の類似度チェックへ変更(8節で詳述、閾値は要実データ再検証) |
| Comment3: Story Meaning + Bridge to Points | 「これから複数の異なる見方を聞く」という橋渡しへ再定義 |
| Comment4: Point Recovery + Bridge to In One Line | Tension/Difference相当(なぜ見方が違うのかを軽く整理)+ Meaning/Closeへの橋渡しへ再定義 |
| In One Line | Meaning/Close(タスク指示9節: 勝者・正解を決めない、Perspectiveの違いから見えるものを整理)へ役割文言のみ調整。物理構造(見出し+1〜2文)は流用可 |
| Preview roleの「turning point」 | 「なぜ見方が違うのか」という問いの立て方へ言い換え |

**変更しないもの**: Fact Ledger制約・Spoken-first数字ルール・Evidence Compression・
レベル別難易度Instruction・Fact Checker/Ledger Deviation/Directional Precheckの
3段QA・Key Phrase選定・放送shellの物理仕様(pause秒数・TTS voice割当)。

---

## 8. 既存Validator/downstreamへの影響

| 対象 | 影響 | 対応方針 |
|---|---|---|
| Fact Checker / Ledger Deviation Check / Directional Fact Precheck | **影響なし**。いずれも記事全文(article_text)を渡すだけの汎用設計で、Main Story/Pointという構造を一切参照していない([er002_ja_web_research_r3.py:241-244](er002_ja_web_research_r3.py:241)、[er003_v1_en_direct_vfl_01_generate.py:533-548](er003_v1_en_direct_vfl_01_generate.py:533)) | そのまま利用 |
| Key Phrase選定 | **影響なし**。確定済み最終本文から選ぶだけ | そのまま利用 |
| Audio Validation Gate・disfluency QA・A2 6%slowdown・Point Notification | **影響なし(見出し2つを維持する限り)**。segment名は`point_one`/`point_two`という名前だが、実装は位置ベースであり中身の意味(Point/Perspective)を判定していない | そのまま利用。ただし変数名・ログ上に残る"Point"という名称は将来の可読性のため要リネーム検討(今回は不要) |
| Point Overlap QA + Diagnostic Full Retry | **要再設計**。現行は「Perspective/PointがMain Storyの言い換えでないか」を見ているが、Voicesで見るべきは「Perspective同士が似すぎていないか(単純な賛成/反対の言い換えになっていないか)」という**別の比較ペア**。関数自体(`lexical_overlap_ratio(text_a, text_b)`)は2つのテキストを比較するだけの汎用実装のため、呼び出し側の引数を`(perspective_2, perspective_1)`に変えるだけで技術的には転用できるが、**閾値0.40はPoint-vs-Main Storyの実データで調整された値であり、Perspective-vs-Perspective(同じトピックについて話すため語彙が自然に重なりやすい)にそのまま使える保証はない**。Diagnostic Full Retryの診断分類(`_EVIDENCE_WORDS`/`_IMPLICATION_WORDS`/`_CAUSE_WORDS`)もDiscovery型の失敗パターンに合わせた分類であり、Voicesの失敗パターン(「結局同じことを言っている」)には別の分類が要る可能性がある | Voices Trial 1では、いったんこのQAを**monitoring専用(gateにしない)**にとどめ、実データが数件集まってから閾値・分類を再設計することを推奨。Fact Safety(Fact Checker/Ledger Deviation)は無効化しない |
| Shared Point Blueprint | 現行mainでは`blueprint=None`のため**現状は無関係**(Production未稼働) | 今回は考慮不要。将来再稼働させる場合はVoices非対応である点を明記しておく |
| Word count validators(`POINT_TARGET_*`/`TOTAL_SOFT_*`) | Perspectiveの目安語数(タスク指示10節: 各50〜70語)は現行のPoint目安(30〜60語)と近いが同一ではない。Hook(30〜50語)・Tension(50〜70語)・Meaning/Close(40〜60語)に相当する専用の語数診断は**現状存在しない**(Main Story全体の語数目安280〜420語の内訳としてしか見られない) | Trial 1では新しい専用validatorを作らず、記事全体語数目安のみ流用し、パート別の目安は人間レビューで確認する運用を提案 |

---

## 9. QCD評価

**Quality**: 最大のリスクは、Main Story(現状は「本文の核心を運ぶ長い部分」)と
Point/Perspective(現状は「短い深掘り2点」)という**分量配分そのものがDiscovery/Why
向けに最適化されている**点。Voicesでは本来「Hookは短く、Perspectiveが記事の
本体」という逆の配分が自然だが、これを無理に現行の物理構造(Full Story Part1/2が
長尺・Point One/Twoが短尺)へ当てはめると、Perspectiveの語数目安(50〜70語)が
現行Point目安(30〜60語)と近いために窮屈になり、逆にMain Story(Hook)側が
必要以上に長く書かれてしまう懸念がある。これは実際にドラフトを書いて確認しないと
判断できない(11節の次Stepに含める)。

**Cost**: Point Overlap QA/Diagnostic Full Retryをそのまま閾値0.40でVoicesへ
適用すると、Perspective同士は同じトピックを扱う以上、Discovery型のPointより
語彙が重なりやすく、誤ってflagされ記事全体retry(Luna API呼び出し)が
頻発するリスクがある。8節の通りmonitoring専用にとどめることで、この
コストリスクを今回は回避する。

**Delivery**: No.10→No.11で2記事検証するという段階的方針(タスク指示18節)は、
見出しブロック数を2つに限定する今回の推奨と両立する。全5 Editorial Typeを
一度に作らず、Voicesの2-Perspectiveケースだけをまず検証するのは、実装コストと
検証速度の両面で妥当。

---

## 10. Open Questions / Risks

1. **分量配分のミスマッチ**: Main Story(Hook、短い想定)とPerspective(記事の本体、
   中程度の分量)という配分が、現行の「Main Story=長尺本文/Point=短い深掘り」という
   物理構造とどこまで整合するか、実際のドラフトで検証が必要。
2. **Perspective類似度チェックの再設計**: 閾値・比較対象・NG時の扱い(記事全体
   retryか、monitoringのみか)を、実データなしに机上だけで決めるのは危険。
3. **Master記事模倣の扱い**: Voices用の別サンプル記事を新規に用意するか、
   模倣方式自体をやめてrole説明文だけに頼るか。前者はサンプル記事自体の
   質がVoices全体の質を左右するリスクがあり、後者はDiscovery/Whyで実証済みの
   「模倣によるスタイル安定効果」を失うリスクがある。
4. **Comment role文言のType別管理の仕組み**: 現状はB1/A2それぞれ専用モジュール内の
   定数として1つに固定されている。Editorial Type別に切り替える仕組み自体が
   まだ存在しないため、これをどう設計するか(辞書化/関数化)は次のステップで
   具体化が必要。
5. **Researcher/VFL生成側への影響**: Voicesは「利害関係者ごとに異なる事実認識・
   優先事項」を必要とするため、現行のVerified Fact Ledger生成(Researcher
   instruction)がPerspectiveごとに十分な材料を拾えるかは未検証(今回は
   Writer側の分解が主眼のため、Researcher側の調査はスコープ外としている)。
6. **既存の未解決課題(OPEN-91)との関係**: No.9で発生した「Point Twoが調査
   レポート的になる(4つの数値を連続で読み上げる)」という問題は、独立Trialで
   原因がWriter Prompt自体にあると特定済みで、対策(Meaning First instruction)
   も6/6で有効性を確認済みだが、Production採用は`USER_DECISION_REQUIRED`のまま
   保留されている(`OPEN_ITEMS.md`)。これはDiscovery/Why固有の課題であり、
   Editorial Type Module化のタイミングでこの未決定事項も合わせて解消できる
   可能性がある(Discovery Moduleの改善課題として引き継ぐことを推奨)。
7. **Diagnostic Full Retry内の未整合(今回の副次発見)**: 現在Production稼働中の
   `er009_diagnostic_full_retry_modules_12.py`のretry prompt末尾に
   "Preserve Storytelling First." "Preserve No Jargon." という指示が含まれて
   いるが、この2つの用語は**現行Production Writer Prompt(COMMON_BLOCK_TEMPLATE等)
   のどこにも定義されていない**(Trial専用Writerにのみ存在する用語)。モデルに
   「一度も与えられていないルールを維持しろ」と指示している状態であり、
   Editorial Type Module導入時にrole文言の管理を一本化する際、あわせて修正
   すべき既存の小さな不整合として記録しておく(今回のスコープでは修正しない)。

---

## 11. No.10 Trialへ進むための推奨次Step

1. Voices版Writer Instruction(Master記事模倣の扱い含む、Main Story=Hook・
   Perspective1/2の役割定義・類似度に関する制約文言)を具体的にドラフトし、
   ユーザーレビューを受ける。ドラフト前に`er002_editorial_angle_adapter.py`/
   `er002_editorial_common.py`(2節参照、廃棄済みだが役割の型・Diversity評価の
   考え方は再利用価値が高い)に目を通し、同じ「事実の羅列っぽくなる」失敗を
   繰り返さない設計にする。
2. Voices版Comment3/4・Preview roleの文言をドラフトする。
3. Perspective類似度チェックの運用方針(monitoring専用にするか、閾値を
   独自に設定するか)をユーザーと確認する。
4. No.10のTopic「Do We Still Want to Work From Home?」のVerified Fact Ledgerを
   通常のResearch pipelineで生成し、複数の利害関係者(在宅勤務を続けたい従業員/
   オフィス回帰を求める経営陣/オフィス不動産側/対面重視の新人育成担当等)の
   視点を裏付けるFactが十分に含まれているか確認する。
5. 上記が揃った段階で、ユーザー承認を得た上でNo.10の実生成に着手する
   (今回はここまでで実装しない)。

---

## Status

**Status: DESIGN / ANALYSIS ONLY — NOT VALIDATED, NOT APPROVED_FOR_PRODUCTION, NOT PRODUCTION_WIRED**
