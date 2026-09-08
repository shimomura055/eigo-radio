# FAMILY-A-DESIGN-FIX-INVENTORY-01 — Family A設計FIX棚卸し(読み取り専用)

管理ID: FAMILY-A-DESIGN-FIX-INVENTORY-01(Lane A)
実施日: 2026-09-08
実施者: sonnet-worker(読み取り専用、新規実装・SSOT編集・Git操作なし)

## 0. Family Aの範囲定義(根拠付き)

CURRENT_SPEC.md本体には「Family A」という語自体は存在しない
(grep 0件)。定義の根拠はOPEN_ITEMS.md OPEN-112行の追記
(`OPEN-112-EDITORIAL-TYPE-PRODUCTION-RECONCILIATION-AUDIT-01/
TOPIC-SSOT-AND-FAMILY-FRAME-02/CONTEXT-RECONCILIATION-03`、
2026-09-04)にある:

> 「ABC Family大枠(**A=Discovery/Why+News/Trend Synthesis**、
> B=Voices+Case Story、C=Future/Scenario)は設計方針の前提として
> 妥当と確認し、A群を優先して次工程(A Family Common設計)へ
> 進めることをユーザーが決定した」

同エントリはさらに **「Production Writerコード
(`er003_v1_n3_01_articles_generate.py`・
`er006_pool_pilot_01_writer.py`)には"Editorial Type"に対応する
module・条件分岐が一切実装されていないことをgrep監査(0件マッチ)で
確認した」** と明記している。すなわち「Family A」は現時点で
**コード上の型(Editorial Type module)としては存在せず**、設計上の
分類名にとどまる。全テーマ(N3以降のHanshin/Health/Household、
Theme 2 Trend Synthesis、No.18 Discovery/Why等)は単一の共通
Production Writerパスを通っており、これが実質的に「Family A」に
相当する記事を生み出している唯一の経路である。

本棚卸しでは、この**単一共通Production経路**
(Research/Ledger→Writer→Editor[Evidence Compression/Numeric
Precision]→Validator/Fact QA→Key Phrase→TTS[retry/Human Review
Lock/repetition QA/connected speech]→Assembly→試聴artifact)を
「Family Aに含まれるProduction経路」として扱う。

Dangling Reference Check(追加分): Family A Production code
(`er003_*`/`er006_*`/`er007_*`/`er008_*`/`er010_*`/`er011_*`の
非B-Family系ファイル)を`editorial_type`/`Editorial Type`で
grepした結果、参照0件(Lane B専用の`er012_*`4ファイルのみが
参照、Family A Productionコードは一切参照していない)。
`ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02_REPORT.md`・
`ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.md`はgit未追跡・
「参考資料(design reference only)」としてユーザーが位置づけ済み
(OPEN-112追記)で、Production経路からは参照されていない。
**新規のdangling reference候補は発見しなかった。**

## 1. 8分類

### (1) PRODUCTION_WIRED済み仕様(Family A共通経路に有効)

| 管理ID | 内容 | 根拠 | 最終更新 |
|---|---|---|---|
| OPEN-110 | B1 Connected Speech Validator(Pattern A/B/C) | OPEN_ITEMS.md OPEN-110行「RESOLVED」、CURRENT_SPEC.md 498行 | 2026-09-03 |
| OPEN-111 | A2 Reading Resolver | OPEN_ITEMS.md OPEN-111行「RESOLVED」、CURRENT_SPEC.md 501行 | 2026-09-03 |
| OPEN-113 | Local Rewrite Point-context-only(重複対策) | OPEN_ITEMS.md OPEN-113行「RESOLVED / PRODUCTION_WIRED」 | 2026-09-05 |
| OPEN-115 | Assembly Headroom Safety Valve | OPEN_ITEMS.md OPEN-115行、CURRENT_SPEC.md該当箇所 | 2026-09-06 |
| OPEN-116 | KP Validator numeric/homophone/gloss規約 | OPEN_ITEMS.md OPEN-116行「RESOLVED / PRODUCTION_WIRED」 | 2026-09-06 |
| OPEN-118 | KP日本語gloss naturalness Prompt追加 | OPEN_ITEMS.md OPEN-118行「RESOLVED / PRODUCTION_WIRED」 | 2026-09-06 |
| OPEN-119 | Non-Latin cascade(Key Phrase英語経路限定) | OPEN_ITEMS.md OPEN-119行「RESOLVED / PRODUCTION_WIRED」 | 2026-09-06 |
| OPEN-121 | TTS Repetition/False Start QA(A2/B1本文4segment、`generate_a2_segments()`/`generate_b1_segments()`が`True`で明示的に有効化) | CURRENT_SPEC.md 456行、commit`e6c2f37` | 2026-09-07 |
| OPEN-122 | Connected Speech Equivalence Layer(A2/B1本文segment) | CURRENT_SPEC.md 499行、commit`3297d1b` | 2026-09-07 |
| OPEN-123 | Transcript Style Normalization(ASR経路全体、KP含む) | CURRENT_SPEC.md 500行、commit`9f25f7d` | 2026-09-07 |
| OPEN-127 | 反復QA em dashトークナイズ修正 | OPEN_ITEMS.md OPEN-127行、commit`602f1f5`、CURRENT_SPEC.md第8弾changelog | 2026-09-08 |
| OPEN-128 | 方式D局所ASR確認2段判定 | OPEN_ITEMS.md OPEN-128行、commit`05bbeca`、CURRENT_SPEC.md第8弾changelog | 2026-09-08 |
| ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01 | Point Role Planning+Point Value QA、KP Set Redundancy QA、人称表現一般化 | CURRENT_SPEC.md該当行(2026-09-02) | 2026-09-02 |
| ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01 | B1 Preview分量原則・Numeric Precision共通原則 | CURRENT_SPEC.md該当行 | 2026-09-07 |
| ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-PRODUCTION-WIRING-23 | KP trim margin 0.30秒cache identity | CURRENT_SPEC.md該当行 | 2026-09-04 |
| ASR-first Retry Policy(EN/JA)、Fact Checker retry cap、横断retry監査 | 既存の安全上限機構 | CURRENT_SPEC.md 490-496行 | 2026-08-22〜29 |

すべてFamily Aの実運用経路(N3系Writer→TTS→Assembly)へ直接配線
済み。OPEN-127/128は共有module
(`er011_open121_repetition_qa_production_01.py`)への追記であり、
B-Family Phase 1が発見のきっかけだったが**配線先はFamily A本文
segment(A2/B1 full_story/point_one/point_two)であり、Family A
本体に直接効く**(B-Family固有の実装ではない点を区別して記載)。

### (2) APPROVED_FOR_PRODUCTIONだが未配線

**該当0件(Family A範囲内では発見せず)**。今回確認した
APPROVED_FOR_PRODUCTION言及はいずれも既に`PRODUCTION_WIRED`済み
(上記(1))か、B-Family(Voices)固有のもの(OPEN-120行の
Comment Contract全体`APPROVED_FOR_PRODUCTION`(未配線)は
**Family Bスコープであり本棚卸しの対象外**、参考記載のみ)。

### (3) VALIDATEDだが未採用

| 管理ID | 内容 | 根拠 | 最終更新 |
|---|---|---|---|
| OPEN-121(方式C-v2) | 窓内独立判定によるgap<0.5秒即時言い直し検知 | OPEN_ITEMS.md OPEN-121行「適用範囲拡大…`USER_DECISION_REQUIRED`」、「未配線」注記 | 2026-09-07 |
| OPEN-121(方式A-ext) | 単語duration異常検知(partial-word false start) | OPEN_ITEMS.md OPEN-121行「false reject 10/26(38%)…現状のままauto-rejectゲートとしては不適格」 | 2026-09-07 |
| OPEN-117(核変換ルール) | 先頭/読点直後「～」→「なになに」変換(A2 rank5実証) | OPEN_ITEMS.md OPEN-117行「Production正式経路でも`VALIDATED`…全体は`USER_DECISION_REQUIRED`」 | 2026-09-06 |

### (4) USER_DECISION_REQUIRED(Family A関連)

| 管理ID | 内容 | 根拠 | 最終更新 | Blocking区分 |
|---|---|---|---|---|
| OPEN-121(本体) | 検知方式の他segmentへの適用範囲拡大要否 | OPEN_ITEMS.md OPEN-121行 status=`USER_DECISION_REQUIRED` | 2026-09-07 | Non-blocking |
| OPEN-117(全体) | 変換規則適用範囲拡張要否・A2 rank2 REGENERATE_APPROVED要否 | OPEN_ITEMS.md OPEN-117行 | 2026-09-06 | 未確認(記載なし、影響範囲小) |
| OPEN-124 | 未追跡ファイル分類(削除・.gitignore方針等) | OPEN_ITEMS.md OPEN-124行 status=`USER_DECISION_REQUIRED` | 2026-09-08 | Non-blocking |
| OPEN-83 | CMU辞書に無い外国由来固有名詞の発音判定強化(3設計案) | OPEN_ITEMS.md OPEN-83行 status=`STOPPED_FOR_DESIGN_REVIEW` | 2026-08-26頃 | Non-blocking |

### (5) deferred・non-blocking

| 管理ID | 内容 | 根拠 | 最終更新 |
|---|---|---|---|
| OPEN-100 | Point解説の数字羅列(survey readout調)問題 | OPEN_ITEMS.md OPEN-100行「DEFERRED / NON-BLOCKING」 | 2026-09-01 |
| OPEN-103 | Key Phrase「default」のTTS誤発音(恒久課題) | OPEN_ITEMS.md OPEN-103行「DEFERRED / NON-BLOCKING」 | 2026-09-02 |
| OPEN-107 | Ending-Clarity Fallback(旧仕様) | `WITHDRAWN`、B1 Connected Speech Validatorへ置換済み | 2026-09-03 |
| OPEN-114 | Ledger Deviation Checker Judgment Variance | OPEN_ITEMS.md OPEN-114行「DEFERRED / NON-BLOCKING」 | 2026-09-05 |
| OPEN-112(本体残件) | Discovery 4-layer採否・Engagement根底指示採否・News Ledger自動Research化 | OPEN_ITEMS.md OPEN-112行「本体残件: `DEFERRED`」(2026-09-08ユーザー決定) | 2026-09-08 |
| OPEN-126 | A2/B1独立Editorによる数字表現粒度差 | `CLOSED`(対策なしでclose、2026-09-08) | 2026-09-08 |

### (6) Family A全体の未決・未配線の有無

**あり(構造レベルで1点、内容レベルで複数)**。
最大の未決は、Family Aという分類自体が**コードとして未実装**である
という点(OPEN-112行の中核記述、grep監査0件)。現状は「全テーマが
同一の安全な共通経路を使っているだけ」で機能不全は起きていないが、
Editorial Type別の挙動差を前提にした将来判断(例: OPEN-100の
「Editorial Type多様化でsurvey/numeric-heavy比率が下がる」という
前提)が未実装の仮定の上に乗っているリスクが、ユーザー決定
(OPEN-112-EDITORIAL-TYPE-PRODUCTION-RECONCILIATION-AUDIT-01等)
としてそのまま記録されている。内容レベルでは、News/Trend
Synthesisモードの4層設計(OPEN-112-NEWS-MODE-DESIGN-08)は
read-only設計のみでコード変更・Prompt確定・記事生成は未実施。

### (7) 「設計FIX済み」と呼べる範囲

- Family Aに実質相当する単一共通Production経路
  (Research/Ledger→Writer→Evidence Compression/Numeric
  Precision Editor→Fact QA/Ledger Deviation→Key Phrase選定→
  TTS retry cascade[ASR-first Retry・Human Review Lock・
  repetition QA・connected speech]→Assembly→試聴artifact)は、
  上記(1)の通り広範にPRODUCTION_WIRED済みで、現時点で確認できた
  APPROVED_FOR_PRODUCTIONの未配線項目は0件だった。
- 直近のGate 3/Gate 4(Dangling Reference Check)・project-wide
  regression(collected=2184、passed=2181、既知3件のみ)を経て
  Fableが正式受入済み(OPEN-127/128、PM-CLOSEOUT-CONSOLIDATION-13)。
- 既存のretry上限・Human Review Lock・Cost Guardは横断監査済み
  (ER-008-N8-CLOSEOUT-GOVERNANCE-25)で、無制限loopは0件。

### (8) 「まだFIXと呼べない」範囲

- **Family A(Editorial Type)自体の実装が0%**。設計文書
  (ER-010-EDITORIAL-TYPE-*)はgit未追跡・参考資料止まりで、
  正式Decision化されていない。
- Trend Synthesis(A Family内News mode)はTrial段階止まり
  (Trial-09/10、`USER_DECISION_REQUIRED`のTrend overclaim/Point
  Overlap閾値/Trend Ledger作成方式の3論点が未決)。
- OPEN-121本体(検知方式拡張)・OPEN-117(変換規則拡張)は
  `USER_DECISION_REQUIRED`のまま。
- OPEN-83(外国由来固有名詞発音)は`STOPPED_FOR_DESIGN_REVIEW`の
  まま未解消(ただしNon-blocking)。

## 2. 結論: PARTIAL

**Family Aは現時点でFIX済みとは言えない(PARTIAL判定)。**

根拠:
1. Family Aに実質相当する共通Production経路(音声・記事生成の
   安全機構一式)は極めて広くPRODUCTION_WIRED済みで、今回の棚卸しで
   確認できたAPPROVED_FOR_PRODUCTIONの未配線項目は0件だった
   (カテゴリ(2)該当なし)。
2. しかし「Family A」という設計分類自体はコード上0%実装
   (Editorial Type module不在、OPEN-112行のgrep監査で確認済み)
   であり、これは既にユーザー・PM双方が認識している既知のギャップ
   である。
3. Trend Synthesis(Family A内News mode)はTrial段階に留まり、
   3件のUSER_DECISION_REQUIRED論点(Ledger Deviation severity、
   Point Overlap閾値のNews/Trend調整、Trend Ledger作成経路)が
   未決。
4. OPEN-121(TTS反復検知の拡張)・OPEN-117(gloss変換規則拡張)は
   コア部分はPRODUCTION_WIRED/VALIDATEDだが、全体としては
   USER_DECISION_REQUIREDのまま。
5. OPEN-83(外国由来固有名詞発音)はSTOPPED_FOR_DESIGN_REVIEWで
   未解消。

残課題(すべてNon-blocking、現行Production運用は継続可能):
- OPEN-112(本体残件、DEFERRED) — Family A設計の正式コード化自体
- OPEN-121(本体、USER_DECISION_REQUIRED) — 検知拡張範囲
- OPEN-117(全体、USER_DECISION_REQUIRED) — gloss変換拡張範囲
- OPEN-83(STOPPED_FOR_DESIGN_REVIEW) — 外国由来固有名詞発音
- OPEN-124(USER_DECISION_REQUIRED) — 未追跡ファイル整理(Family A
  自体の仕様には非直結)

新Trial・追加仕様・Production実装の提案はしない(本タスク範囲外)。
