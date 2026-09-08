# FAMILY-A-DAILY-NEWS-SPEC-DRAFT-01 報告書

管理ID: FAMILY-A-DAILY-NEWS-SPEC-DRAFT-01(Lane A-3)。
**読み取り専用+ドラフト作成のみ。CURRENT_SPEC.md本体・コード・Promptの編集、
API呼び出し、Git操作は一切行っていない。** Lane A-1(`er003_v1_n3_01_articles_
generate.py`編集中)・Lane B(`er012_*`)の成果物は参照していない。

対象: 通常News(Major/Daily News)を、Hanshin系現役Production資産
(`ER-003-A2-B1-N3-01`、Hanshin/Health/Household)ベースで正式化する場合の
「CURRENT_SPEC追加候補テキスト」を、既存SSOTからの引用のみで作成する
(News固有層=Layer3 News Focus Moduleの設計は行わない、スコープ外)。

参照元: `FAMILY-A-LEGACY-NEWS-ASSET-SURVEY-01_REPORT.md`、
`OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md`、
`FAMILY-A-BRANCH-FACT-CHECK-02_REPORT.md`、`CURRENT_SPEC.md`(該当行のみ)。

---

## 1. 4区分整理

| 項目 | 区分 | 根拠(管理ID) |
|---|---|---|
| 11パート構造(Preview→Key Phrases→Comment1→Full Story Part1→Comment2→Part2→Comment3→Point One→Point Two→Comment4→In One Line) | **現在もProductionで有効** | ER-003-A2-STRUCT-02〜04、ER-003-A2-SPEC-FREEZE-01(2026-08-12、CURRENT_SPEC.md「CEFR-A2構造・音声仕様」節)。B1側も同構成(ER-003-B1-NOVEL-AUDIO-01系、2026-08-17) |
| Writer template(`COMMON_BLOCK_TEMPLATE`、`er003_v1_n3_01_articles_generate.py::run_one_pattern()`) | **現在もProductionで有効** | ER-003-A2-B1-N3-01。Pool Pilot・Theme 2・4層Trialまで唯一のProduction Writer共通テンプレートとして継続使用(DECISION_LOG.md 5981/6316行、`FAMILY-A-LEGACY-NEWS-ASSET-SURVEY-01_REPORT.md` §4) |
| Point Balance(目標30〜60語/許容25〜70語、診断的目安・hard capではない) | **現在もProductionで有効** | ER-003-SPOKEN-FIRST-03、ER-003-A2-B1-N3-01(3ジャンルで`VALIDATED across Sports/Health/Household`、2026-08-17) |
| Fact Safety標準(Verified Fact Ledger→Fact Checker→Ledger Deviation Checker v2の3段構成) | **現在もProductionで有効** | ER-003-A2-B1-N3-01、ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02(v2判定基準)、ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12(FAIL=blocking/REVIEW_REQUIRED=non-blocking advisory、`PRODUCTION_WIRED`2026-09-01) |
| Spoken-first数値原則(Numeric Precision含む) | **現在もProductionで有効** | ER-003-A2-B1-N3-01 §14(2026-08-17、Importance/Exactness 2軸)。ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01(2026-09-07、A2/B1/B2共通原則としてWriter共通Prompt「Spoken-first原則(数字の扱い)」C項へ配線済み) |
| Audio構造(segment順・Point Notification・SFX・TTS安全機構・Assembly) | **現在もProductionで有効** | ER-003-CROSSLEVEL-AUDIO-01〜04、ER-003-POINT-NOTIFICATION-01、ER-003-A2-B1-N3-01(3ジャンル横展開・音声確認済み)。SFXはComment前後には入れない(ポーズのみ)/Point One・Twoの直前のみ専用Notification音、というのが現行仕様(CURRENT_SPEC.md「Cross-level仕様」節) |
| Comment Contract(C1〜C4役割: Listening Focus/Mid-story Recovery/Story Meaning/Point Recovery) | **現在もProductionで有効** | ER-003-A2-STRUCT-02〜04(A2起源)、ER-003-B1-NOVEL-AUDIO-01系(B1へ言語のみ変更して継承、2026-08-17) |
| Key Phrase Contract(Strategy L選定+Canonicalization、提示順English→Japanese→English、レベルごとに自身の最終本文から独立選定) | **現在もProductionで有効** | ER-003-CROSSLEVEL-AUDIO-02(A2)、ER-003-B1-NOVEL-AUDIO-01系(B1)。日本語gloss表示/TTS分離・自然さ改善もPRODUCTION_WIRED(2026-09-06、KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01/KEYPHRASE-JA-GLOSS-NATURALNESS-PROD-WIRING-01) |
| A2/B1差(B1-B Direct Generationが現行) | **現在もProductionで有効** | ER-003-B1-B2-SCOPE-FIX-01(2026-08-17ユーザーDecision)。Verified Fact Ledgerから直接1回のWriter呼び出しでNatural English本文生成、B2別段階生成を廃止 |
| A2/B1差(B1-A、B2から派生させる旧2段階方式) | **obsolete** | 2026-08-17にB1-B Direct Generationへ置換・廃止(DECISION_LOG.md該当エントリ)。P-series(A01/A02/ADD03)のみで使用された記録として`HISTORICAL`保持 |
| P-series専用Writer/Audioスクリプト(`er003_v1_iran01_*.py`等、記事専用one-off) | **obsolete** | DECISION_LOG.md 5711行「既にHISTORICAL化済みの完成テーマ向けスクリプト」、現行Production配線対象から意図的除外 |
| Natural English Source方式(B2先行生成→B1流用) | **obsolete** | CURRENT_SPEC.md「CEFR(A2/B1/B2比較)」節「生成元」行、`HISTORICAL`表記。N3以降はLedgerから直接生成に置換 |
| 旧Preview分量(4文/67語程度) | **obsolete** | ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01(2026-09-07)で2〜3文程度の短い導入へ置換、`PRODUCTION_WIRED` |
| 旧Key Phrase trim margin 0.20秒 | **obsolete** | ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-PRODUCTION-WIRING-23(2026-09-04)で0.30秒へ置換、`PRODUCTION_WIRED` |
| A2 Key Phraseの`tight_speech_only()`再crop | **obsolete** | 同上、`load_a2_sources()`から削除済み |
| ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02/WRITER-ARCH-01(Editorial Type Arch設計文書) | **obsolete(参考資料のみ)** | OPEN-112行にてユーザーが「正式仕様として採用せず、参考資料(design reference only)」と明示位置づけ(2026-09-04)。git未追跡 |
| News Focus Module(Major/Daily variant) | **未設計・Trial要** | OPEN-112-NEWS-MODE-DESIGN-08(design-onlyと明記、Trial・記事生成0件)。`FAMILY-A-BRANCH-FACT-CHECK-02_REPORT.md`§5で「Editorial Typeとしてのコード実装は0%、Trial記録も0件」と再確認 |
| News Focus Module(Trend Synthesis variant) | **未設計相当だがTrialは進行**(Lane A-1で配線作業中、本タスクでは不参照) | OPEN-112-TREND-SYNTHESIS-MINIMAL-PROMPT-TRIAL-09以降、Production配線はDEFERRED(2026-09-08ユーザー決定) |
| Mode判定基準(単一起点質問/集約質問) | **未設計・Trial要** | OPEN-112-NEWS-MODE-DESIGN-08 §4(設計文書内のみ、コード実装なし) |
| Point Role Planning/Point Value QAのNews/Trend流用可否 | **未設計・Trial要(既存機構自体はDECIDED)** | 既存Point Role Planning/Point Value QAは`PRODUCTION_WIRED`(ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01)だが、News/Trend向けの動的役割候補リスト自体は設計提案のみ(OPEN-112-NEWS-MODE-DESIGN-08 §2/§3、未Trial) |

件数: 現在もProductionで有効=9件、obsolete=6件、未設計・Trial要=3件
(Trend Synthesis variantは本タスク対象外のため上表参考枠、件数に含めない)。

---

## 2. CURRENT_SPEC追加候補テキスト(ドラフト、未採用)

**注記: 以下は「CURRENT_SPEC.mdへ将来追加する場合の書式イメージ」を示す
ドラフトであり、CURRENT_SPEC.md本体には一切反映していない。管理ID列は
既存SSOTからの引用であり、本ドラフト自体の管理IDではない。News固有の
Layer3(Focus Module・Mode判定)は意図的に「未設計」のまま空欄相当とし、
設計内容を書いていない。**

```markdown
## 通常News(Major/Daily News)[ドラフト、未採用、CURRENT_SPEC.md未反映]

| 項目 | 現在値 | 状態 | 根拠Decision | 最終更新日 |
|---|---|---|---|---|
| 全体構造(11パート) | Preview→Key Phrases→Comment1→Full Story Part1→
  Comment2→Full Story Part2→Comment3→Point One→Point Two→Comment4→
  In One Line | `DECIDED`(既存A Family共通骨格を継承、News固有変更なし) |
  ER-003-A2-STRUCT-02〜04、ER-003-A2-SPEC-FREEZE-01、
  OPEN-112-NEWS-MODE-DESIGN-08 §12(A Family Common Skeletonとの整合確認、
  物理構造・見出し数の変更不要) | 2026-08-12(構造起源)/2026-09-05
  (Newsへの適用可能性確認) |
| Writer(本文生成) | `er003_v1_n3_01_articles_generate.py::
  COMMON_BLOCK_TEMPLATE`をNews記事にもそのまま使用。News専用のWriter
  分岐は存在しない | `DECIDED`(既存共通経路の継続利用、News専用実装は
  `未設計`) | ER-003-A2-B1-N3-01、FAMILY-A-LEGACY-NEWS-ASSET-SURVEY-01
  §4 | 2026-08-17 |
| B1本文生成方式 | B1-B Direct Generation(Verified Fact Ledgerから
  独立生成、B2非経由) | `DECIDED` | ER-003-B1-B2-SCOPE-FIX-01 |
  2026-08-17 |
| Point Balance | 目標30〜60語/許容25〜70語(診断的目安、hard capでは
  ない) | `VALIDATED across Sports/Health/Household` | ER-003-A2-B1-N3-01
  | 2026-08-17 |
| Fact Safety | Verified Fact Ledger→Fact Checker(PASS/REVIEW_REQUIRED
  /FAIL)→Ledger Deviation Checker v2(LEDGER_COMPLIANT/LEDGER_DEVIATION)
  の3段構成。FAILのみblocking、REVIEW_REQUIREDはnon-blocking advisory |
  `DECIDED`(`PRODUCTION_WIRED`) | ER-003-A2-B1-N3-01、
  ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02、
  ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12 |
  2026-09-01 |
| Spoken-first数値原則 | Importance(ANCHOR/SUPPORTING/DISPENSABLE)×
  Exactness(EXACT_REQUIRED/APPROXIMATE_OK/DIRECTION_ONLY)の2軸分類、
  精度に意味がある数字のみEXACT維持。全CEFRレベル共通原則(レベル別
  ルールにしない) | `DECIDED` | ER-003-A2-B1-N3-01 §14、
  ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01
  | 2026-09-07 |
| Comment Contract | C1: Listening Focus。C2: Mid-story Recovery +
  Next Question。C3: Story Meaning + Bridge to Points。C4: Point
  Recovery + Bridge to In One Line。役割は既存A/B1仕様をNewsでも
  そのまま使用 | `DECIDED` | ER-003-A2-STRUCT-02〜04、
  ER-003-B1-NOVEL-AUDIO-01系 | 2026-08-17 |
| Key Phrase Contract | Strategy L(Listening Blocker Ranking)+
  Canonicalization、提示順English→Japanese→English、レベルごとに
  自身の最終本文から独立選定 | `DECIDED` | ER-003-CROSSLEVEL-AUDIO-02、
  ER-003-B1-NOVEL-AUDIO-01系 | 2026-08-17 |
| Audio Assembly/SFX/TTS安全機構 | 既存Cross-level仕様(Point
  Notification、pause値、Ending-Clarity fallback、Repetition/Connected
  Speech QA等)をNewsにもそのまま適用。News専用の音声実装追加は無い |
  `DECIDED`(既存機構の継続適用) | CURRENT_SPEC.md「Cross-level仕様」
  「Audio Assembly」節 | 各行の最終更新日を参照 |
| News固有の視点付与層(Layer 3 News Focus Module、Major/Daily variant) |
  **未設計**。中心Question(何が起きたか/なぜ重要か/次に見るべきこと)、
  Mode判定基準(単一起点質問/集約質問)、Point One/TwoのNews向け候補
  役割はOPEN-112-NEWS-MODE-DESIGN-08で設計提案のみ存在し、Prompt文言
  確定・Trial実行・記事生成は0件 | `未設計・Trial要` |
  OPEN-112-NEWS-MODE-DESIGN-08 | 2026-09-05(設計文書日付) |
```

---

## 3. obsolete除外リスト(通常News仕様に含めない、管理ID・置換先付き)

| obsolete対象 | 置換先(現行仕様) | 管理ID |
|---|---|---|
| B1-A方式(B2から派生させる旧2段階B1生成パイプライン) | B1-B Direct Generation(Verified Fact Ledgerから直接独立生成) | ER-003-B1-B2-SCOPE-FIX-01(2026-08-17) |
| P-series専用Writer/Audioスクリプト(`er003_v1_iran01_articles_generate.py`等、ADD03/A02専用one-off) | `er003_v1_n3_01_articles_generate.py::COMMON_BLOCK_TEMPLATE`(全テーマ共通Writer) | DECISION_LOG.md 5711行、ER-003-A2-B1-N3-01 |
| Natural English Source方式(B2先行生成→B1流用の生成元) | Verified Fact Ledgerから各レベル独立生成(A2/B1とも同格) | CURRENT_SPEC.md「CEFR(A2/B1/B2比較)」節「生成元」行(`HISTORICAL`表記) |
| 旧Preview分量(4文/67語程度) | 2〜3文程度の短い導入(相対指定、hard word-count gateなし) | ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01 |
| 旧Key Phrase trim margin 0.20秒 | 0.30秒(cache identity保証付き) | ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-PRODUCTION-WIRING-23 |
| A2 Key Phraseの`tight_speech_only()`再crop | 削除済み(呼び出しなし) | 同上 |
| ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02/WRITER-ARCH-01の設計内容 | 参考資料としてのみ扱う(正式仕様として採用しない) | OPEN-112行(2026-09-04ユーザー決定) |
| P-seriesのCEFR-B1列(A01/A02/ADD03専用「B1専用簡略英文」設計) | 現行B1(Verified Fact Ledgerから独立生成したNatural Spoken News English) | ER-003-B1-A2-SPEC-FREEZE-01/SCOPE-FIX-01 |
| P-series Preview言語(日本語、Aoede)を現行B1として扱うこと | 現行B1 Previewは平易な英語・Charon voice(B1 Support節参照) | ER-003-B1-NOVEL-AUDIO-01系 |

---

## 4. イラン(ADD03)/英SNS(A02)から引き継ぐreference

**題材・構造referenceとしてのみ扱う(本文生成コードパス・完成音声は再利用
しない)。**

- **ADD03(ホルムズ海峡/イラン情勢)**: 複数ソース(AP/WaPo/Axios/CBS等)、
  CONTESTED/SINGLE-SOURCE区分を要する国際情勢という題材の型として参考。
  音声構造(11パート、Preview日本語のみ、Key Phrase発話順序)は現行
  CURRENT_SPEC.mdの起源そのもの(ER-003-A2-STRUCT-02〜04、
  ER-003-A2-SPEC-FREEZE-01)。ただしADD03専用Writer/Audioスクリプト自体は
  §3の通りobsolete。
- **A02(英国SNS門限)**: UK政策/規制という「単一起点イベント」の典型例、
  DESIGN-08 §4のMode判定基準に照らすとMAJOR_DAILY相当の題材型として参考。
  Main Story本文が記事固有の装飾見出し(「Today's Late-Night Scrolling
  Points」)を使っていた点は、現行の汎用見出し(単純に「Point One」)とは
  異なるため、そのまま踏襲しない。
- 両記事とも、DESIGN-08 §11でMajor/Daily・Trend Synthesisの候補として
  read-onlyで名指しされているが、いずれも**生成・Trial実行は行われて
  いない**(既存Topic Master `topic_package_*.py`の存在確認のみ)。

---

## 5. Trend Synthesisとの境界(共通/通常News限定の区別)

**共通(A Family Common Skeleton、通常NewsとTrend Synthesisで共有)**:

- Layer 1: Common Writing Contract(News/Trend固有ではない一般原則)
- Layer 2: 4-slot構造(Main Story/Point One/Point Two/In One Line)、
  物理構造・見出し数
- Fact Safety標準(Verified Fact Ledger→Fact Checker→Ledger Deviation
  Checker v2)
- Spoken-first数値原則
- Point Role Planning/Point Value QAの機構自体(動的役割選択という仕組み)
- Comment Contract(C1〜C4)・Key Phrase Contract
- Audio構造(segment順・Point Notification・pause値・TTS安全機構・
  Assembly)

**通常Newsには含めない(Trend Synthesis限定要素、Lane A-1配線対象・
本タスクでは不参照)**:

- News Focus Module(Trend Synthesis variant)固有のPrompt文言・
  Counter-signal/limitation必須化ルール
- Mode判定基準のうち「集約質問」(TREND_SYNTHESIS判定側)
- Trend成立条件(独立2件以上のSignal等の定性的Gate)
- Evidence Strength分類タグ語彙(`official_statistics`等)
- Trend Memory(重複防止、将来設計のみ)
- Engagement/Storytelling原則(施策1)・Reference Digest(施策2)
  (OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10、Lane A-1で配線
  進行中の可能性がある未承認内容、本タスクでは中身を参照・引用していない)

本ドラフトは上記「通常Newsには含めない」要素を一切含んでいないことを
確認済み(§2ドラフトテキストにTrend固有語彙の混入なし)。

---

## 6. Gate 4観点の自己点検

**確認項目**: 本ドラフトが、未承認・未実装・Trial-only仕様を参照して
いないか。

- §2ドラフトの各行はいずれも根拠管理IDが`DECIDED`/`PRODUCTION_WIRED`/
  `VALIDATED`(3ジャンル横展開で検証済み)のいずれかであり、`USER_
  DECISION_REQUIRED`・`DEFERRED`・Trial-onlyの内容を引用していない。
- 「News固有の視点付与層」の1行のみ`未設計・Trial要`と明記し、設計
  内容そのものは書いていない(タスク指示通り、スコープ外として空欄
  相当)。
- ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02/WRITER-ARCH-01(参考
  資料指定、Trial-only)・Discovery Layer3 Focus Module(Trial-05、
  Production未配線)・Trend Synthesis Focus Module/Engagement/Reference
  Digest(Lane A-1進行中)は、いずれも§3(obsolete除外)または§5
  (通常Newsには含めない)へ明示的に分離し、§2ドラフト本文には引用
  していない。
- Lane A-1(`er003_v1_n3_01_articles_generate.py`編集中)・Lane B
  (`er012_*`)の成果物は本タスクで一切参照していない(定数名・
  テンプレート名の確認も含め、当該ファイル自体を今回読んでいない。
  引用は全てCURRENT_SPEC.md/既存Reportからの引用)。

**結果: PASS(未承認・Trial-only仕様の混入なし)。**

---

## 7. 正式化を進める場合の次工程(実行しない、ユーザー判断項目の列挙のみ)

1. **書き起こし案(§2)の承認可否**: このドラフトをCURRENT_SPEC.mdへ
   実際に追記するかどうか(追記する場合、既存「Product」節等との
   配置箇所も要決定)。
2. **reference記事の指定**: Hanshin(N3-01)をMajor/Daily構造の
   reference実装として正式指定するか。ADD03/A02は題材・構造reference
   限定(§4)のままでよいか、それとも別途扱いを変えるか。
3. **News固有Layer3(Focus Module・Mode判定)のTrial要否**: 通常News
   固有の視点付与層を新規にTrial設計・実施するか、それとも「通常
   Newsは現行共通骨格のみで十分」としてLayer3自体を導入しないか。
4. **Diagnostic Full Retry/Ledger Deviation Checkerの語彙拡張要否**:
   OPEN-112-NEWS-MODE-DESIGN-08 §10で指摘済みのGap(News固有の失敗
   パターン語彙が存在しない)へ対応するかどうか(通常NewsはTrend
   Synthesisほど深刻ではない可能性があるが、未検証)。
5. **Trend Synthesisとの実装順序**: Lane A-1が進めているTrend
   Synthesis配線と、通常News正式化のどちらを先行させるか、または
   並行させるか。

以上、いずれも実行せず提案・列挙のみ。
