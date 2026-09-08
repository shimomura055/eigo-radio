# FAMILY-A-BRANCH-FACT-CHECK-02 — Discovery/News/Trend Synthesis 枝別事実確認(読み取り専用)

管理ID: FAMILY-A-BRANCH-FACT-CHECK-02(Lane A)
実施日: 2026-09-08
実施者: sonnet-worker(読み取り専用。新規実装・SSOT編集・API呼び出し・Git操作・
Lane B[`er012_*`]参照はいずれも行っていない)

前提: 前回`FAMILY-A-DESIGN-FIX-INVENTORY-01_REPORT.md`(結論`PARTIAL`)を、
Discovery/News/Trend Synthesisの枝ごとに再分解する。推測で補完せず、SSOTで
確認できない事項は「不明」と明記する。

---

## 1. Family Aの正式分類構造

CURRENT_SPEC.md本体には「Family A」「Editorial Type」の語は存在しない
(grep 0件、CURRENT_SPEC.md全620行)。分類の根拠はすべてOPEN_ITEMS.md
OPEN-112行の追記(DECISION_LOG.mdに対応エントリあり)。

- **ABC Family大枠**(OPEN-112-EDITORIAL-TYPE-PRODUCTION-RECONCILIATION-
  AUDIT-01/TOPIC-SSOT-AND-FAMILY-FRAME-02/CONTEXT-RECONCILIATION-03、
  2026-09-04、ユーザー決定): 「A=Discovery/Why+News/Trend Synthesis、
  B=Voices+Case Story、C=Future/Scenario」を**設計方針の前提として妥当と
  確認**。これは正式Decision(ユーザー判断記録)だが、**コード実装ではない**。
- **News系の2モード**(OPEN-112-NEWS-MODE-DESIGN-08、2026-09-05、
  read-only設計): 「News系(A Family)をMajor/Daily NewsとTrend Synthesisの
  2モードに整理し、Discovery/Whyと同じ4層構造(Layer1〜4)で成立するかを
  設計した」。この回のReport冒頭に明記: 「**今回はコード変更・Prompt正式
  文言の確定・Trial実行・記事生成のいずれも行っていません。設計整理のみ
  です。**」
- 「Editorial Type」「Family」という語自体は、Production Writerコード
  (`er003_v1_n3_01_articles_generate.py`・`er006_pool_pilot_01_writer.py`)
  には一切実装されていない(OPEN-112行、grep監査0件、2026-09-03発見・
  2026-09-04/08に再確認済み)。すなわち「Discovery」「News」「Trend
  Synthesis」は**すべて設計文書上の分類名**であり、コード上の型(module・
  条件分岐)としては**どれも存在しない**。
- 「Discovery」の中身: A Familyの1枝(Discovery/Why)を指し、Layer3
  Focus Module(`er011_open112_a_family_4layer_prompt_trial_05.py`)が
  Trial実装・Trial検証済み(DECISION_LOG.md 1179行台)だが、**Production
  Writerへの正式配線は行っていない**(同ファイルのコメント、DECISION_LOG.md
  6335行)。
- ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02_REPORT.md・
  ER-010-EDITORIAL-TYPE-WRITER-ARCH-01_REPORT.mdは共にgit未追跡(`??`)の
  設計文書で、OPEN-112行にて「正式仕様として採用せず、参考資料(design
  reference only)として扱う」とユーザーが明示的に位置づけ済み(2026-09-04)。

**結論**: 「Family」「Editorial Type」「Discovery」「News」「Trend
Synthesis」という**分類名自体はユーザーが正式Decisionとして受け入れた
設計方針**(2026-09-04のABC Family大枠決定)だが、**コードとしての実装は
0%**。現行Productionはこれらの分類に関わらず単一の共通Writer経路のみを
使用している。

---

## 2. 「News Typeの2つの型」の正体

DECISION_LOG.md OPEN-112-NEWS-MODE-DESIGN-08エントリ(1087〜1135行)、
および`OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md` §0「News系は Major/Daily
News と Trend Synthesis の2モードに集約する」との記載により確認:

> 「News系(A Family)をMajor/Daily NewsとTrend Synthesisの2モードに整理し」

**「News Typeの2つの型」= 「通常News(Major/Daily News)」と
「Trend Synthesis」の2モードで確定**(単一記事ベース/複数ソース統合、
Discovery/News等の別分類ではない)。判定基準も設計済み(§4、単一起点質問/
集約質問の2問)だが、**この判定基準・両Moduleとも実コード・実Prompt文言は
未確定**(design-onlyの記載どおり)。

「Major/Daily News」という語自体は、リポジトリ全体でOPEN-112-NEWS-MODE-
DESIGN-08の設計文書・DECISION_LOG.md該当エントリにしか登場せず(grep確認、
DECISION_LOG.md/OPEN_ITEMS.md/CURRENT_SPEC.md内)、これ以降のTrial・
Production wiring記録は**一件も存在しない**。一方「Trend Synthesis」は
Trial-09以降、実記事Trial・完成音声まで進んでいる(§6参照)。すなわち
**設計時点(2026-09-05)では2モード対等に設計されたが、その後の実装深度は
Trend SynthesisのみがTrial実施され、Major/Daily Newsは設計図のまま停止
している**。

---

## 3. 「若者の旅」(Theme 2)の事実確認

管理ID系列(すべてOPEN_ITEMS.md OPEN-112行・DECISION_LOG.md該当エントリで
確認):

- `OPEN-112-TREND-THEME2-SERIES-11-17`(2026-09-06、Trial-11〜17・Opus
  診断-14/-15の親エントリ、DECISION_LOG.md 630行「Theme 2(若者の旅行)
  Trend Synthesis Trial系列」)
  - `OPEN-112-ENGAGEMENT-REFERENCE-CROSS-TOPIC-AB-TRIAL-11`
  - `OPEN-112-TREND-THEME2-B-LEDGER-FIX-AND-A2-B1-TEXT-TRIAL-12`
  - `OPEN-112-TREND-THEME2-B-A2-B1-FULL-AUDIO-TRIAL-13`
  - `OPEN-112-TREND-THEME2-B-A2-PEAK-MEASUREMENT-16`
  - `OPEN-112-TREND-THEME2-B-KEYPHRASE-VALIDATOR-FIX-TRIAL-17`
- `OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-01`/`-02`
- `OPEN-112-THEME2-B1-REASSEMBLY-POST-WIRING-03`
- `OPEN-112-THEME2-B1-NUMERIC-PRECISION-WIRING-AUDIT-01`
- `OPEN-112-THEME2-B1-NUMERIC-PRECISION-MINIMAL-FIX-RERUN-04`
- `OPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-CHECK-01`
- `NUMERIC-PRECISION-RETROACTIVE-AUDIT-01`(関連、Theme2 A2「24.1%」新規発見)

**mode**: OPEN-112行内でTheme2系列は一貫して「Trend Synthesis」と明記
(例: 「Theme2(若者の旅行)Trend Synthesis Trial系列」、Trial-09の
「Mode判定もTREND_SYNTHESISを再確認」)。**通常News(Major/Daily)としての
扱いは一切ない**。

**到達点**: Theme 2 A2/B1の完成音声はrerun_04版がユーザー最終試聴で
`APPROVED_FOR_PRODUCTION`(2026-09-08、PM-CLOSEOUT-CONSOLIDATION-08、
OPEN_ITEMS.md OPEN-112行)。ただしこれは**この特定の音声コンテンツに対する
承認**であり、OPEN-112行は明示的に「Theme 2音声: `CLOSED` / 本体残件:
`DEFERRED`」と状態を分離している。本体残件(Discovery 4-layer Focus
Module Production採用可否・Engagement根底指示Production採用可否・News
Ledger自動Research経由化)は2026-09-08時点で**ユーザー決定によりDEFERRED
のまま**(§6参照)。

---

## 4. 各枝のStatus分類(管理ID・根拠付き)

| 枝 | Status | 管理ID | 根拠 |
|---|---|---|---|
| ABC Family大枠(分類そのもの) | 設計方針として`ユーザー決定`だがコード実装0% | OPEN-112-...-TOPIC-SSOT-AND-FAMILY-FRAME-02 | OPEN_ITEMS.md OPEN-112行、grep監査0件 |
| Discovery/Why Layer3 Focus Module | `VALIDATED`(Trial実施済み)、Production未配線 | Trial-05(`er011_open112_a_family_4layer_prompt_trial_05.py`) | DECISION_LOG.md 6320-6335行「Production側ファイルは一切変更していない」 |
| Discovery 4-layer全体のProduction採用可否 | `DEFERRED`(2026-09-08ユーザー決定) | OPEN-112本体残件 | OPEN_ITEMS.md OPEN-112行末尾 |
| News(A Family共通)4層構造・2モード分割 | 設計のみ(コード0、Trial 0) | OPEN-112-NEWS-MODE-DESIGN-08 | Report冒頭「コード変更・Prompt確定・Trial実行・記事生成のいずれも行っていません」 |
| Major/Daily News(通常News) | **設計のみで停止**(以降のTrial記録なし) | OPEN-112-NEWS-MODE-DESIGN-08 | grep: DECISION_LOG/OPEN_ITEMS/CURRENT_SPEC全体で本エントリ以外に言及なし |
| Trend Synthesis Focus Module(最小Prompt) | `VALIDATED`(実記事Trialあり) | OPEN-112-TREND-SYNTHESIS-MINIMAL-PROMPT-TRIAL-09 | 「Production Prompt/code変更なし」だが実記事(A2×2・B1B×1)をTrial生成 |
| Trend Synthesis Engagement/Reference Digest | `USER_DECISION_REQUIRED`候補として報告のみ、未登録・未実装 | OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10 | 「OPEN_ITEMSへの正式登録・実装はいずれも今回行っていない」 |
| Trend Synthesis 実記事(Theme2)完成音声 | `APPROVED_FOR_PRODUCTION`(音声コンテンツのみ) | OPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-CHECK-01ほか(§3) | OPEN_ITEMS.md OPEN-112行末尾「Theme 2音声: CLOSED」 |
| Trend Synthesis mode自体のProduction採用・配線 | `DEFERRED`(2026-09-08ユーザー決定) | OPEN-112本体残件 | OPEN_ITEMS.md OPEN-112行末尾「本体残件: DEFERRED」 |
| Family A共通Production配管(Writer→Editor→QA→TTS→Assembly) | `PRODUCTION_WIRED`(広範) | OPEN-110/111/113/115/116/118/119/121/122/123/127/128等 | 前回`FAMILY-A-DESIGN-FIX-INVENTORY-01_REPORT.md`表(1) |

APPROVED_FOR_PRODUCTIONだが未配線(Family A範囲): 前回棚卸しで**該当0件**
(今回の追加確認でも新規発見なし)。

---

## 5. 通常News: 「記事設計自体が未完成」か「上流の一部だけ未完成」か

**判定: 記事設計(Editorial Type としてのMajor/Daily News)自体が未着手に
近い。「上流Research routeの一部だけ未完成」ではない。**

根拠:
1. 「Major/Daily News」というLayer3 Focus Module・Mode判定基準・Prompt
   文言は、OPEN-112-NEWS-MODE-DESIGN-08の設計文書内にのみ存在し、Trial
   実行(記事生成)は**一度も行われていない**(grep確認、Trend Synthesisと
   異なりTrial-09相当の後続実施記録が無い)。
2. 一方、**基盤となる共通Production配管**(Writer/Editor/Fact QA/Key
   Phrase/TTS retry cascade/Assembly)は、Editorial Typeの区別なしに
   News風の実記事(Hanshin/Health/Household、n3_01、2026-08-17生成)で
   **既に実運用済み**。ただしPOOL_TOPIC_MASTER.mdにはHanshin/Health/
   Householdの記載自体が無く(grep確認)、これらは「Editorial Type」概念
   導入(No.10〜20以降)より前の生成物であり、**「Major/Daily News」という
   正式Editorial Typeラベルの下で生成された記事ではない**(単に共通経路で
   生成されたニュース風記事、というだけ)。
3. No.18(Discovery/Whyラベル)についても、POOL_TOPIC_MASTER.md経緯注記に
   「No.18は…No.9までのProduction Wired仕様のみを使い正式生成した」と
   明記されており、**Discovery固有のコード分岐を一切使っていない**
   (Discoveryも通常Newsも、現行Productionでは同一の無区別な経路を通る)。

したがって、「通常News」については **(a) Layer3 Focus Module・Mode判定
という記事設計そのものが実質未着手**(設計文書1本のみ、Trial 0件)であり、
**(b) その記事を支える上流〜下流のProduction配管自体は既に広く稼働実績が
ある**が、それは「通常News」という分類に固有の実装ではなく、全テーマ共通の
無区別な経路である、という二重構造。「上流Research routeの一部だけ未完成」
という限定的な表現は**不正確**(Research route固有の欠落ではなく、
Editorial Type自体が丸ごと未実装のうちの1枝が「たまたまTrialすら未実施」
という状態)。

---

## 6. Trend Synthesis: VALIDATED範囲とProduction採用・配線状況

**VALIDATED済みの範囲**(いずれも「VALIDATED」または相当の実データ確認済み、
Production配線とは別):

- Trend Gate(6条件)・Mode判定(TREND_SYNTHESIS再確認): Trial-09で実記事
  (イラン・ホルムズ海峡テーマ)にてPASS確認。
- 最小Focus Module Prompt: Trial-09でA2×2・B1B×1の実記事生成に成功
  (Production Prompt/code変更なしのTrial実行)。
- Engagement/Storytelling原則(施策1): Trial-10のA/B比較で「時系列列挙→
  反転・対比構成」への改善を確認、Point Overlap/Value QAとも余裕を持って
  PASS。
- Reference Digest(施策2、Fact source禁止): Trial-10でFact漏洩0件を確認
  したが、効果は「今回不明瞭」(1回比較のみ)。
- Point Overlap閾値(0.40固定)への懸念: Trial-09でNews/Trend共有語彙
  による誤flag事例が発生(構造的行き詰まりではなく閾値付近の不安定さと
  判定)。Trial-10では再現せず。
- Ledger Deviation Checker: `changed_causality`/`changed_certainty`/
  `unsupported_new_claim`タグでtrend overclaimを検知(Trial-09でPoint Two
  4件MINOR検知)。専用カテゴリは無いが既存タグがEXISTING_QA_SUFFICIENT
  寄りと評価。
- News Ledger自動Research経由化: **Trialなし**、「べきか」という論点の
  提起のみ(未検証)。
- Discovery 4-layer Focus Module: これはDiscovery枝の仕様であり(§1)
  Trend Synthesis自体の話ではないが、両者は同じ4層構造フレームを共有する
  設計。

**Production採用・配線状況**:
- Theme 2完成音声(A2/B1)は`APPROVED_FOR_PRODUCTION`(2026-09-08)だが、
  これは記事テキスト生成に使ったTrialスクリプト
  (`er011_open112_trend_theme2_b_final_audio_rerun_04.py`等)による
  **一回限りの成果物への承認**。Assembly段は既存Production関数
  (`stage_assemble_b1`等、無変更)を利用しているが、**Trend Synthesis
  記事生成そのもの(Writer/Focus Module)はProduction Writerコードへ配線
  されていない**。
- OPEN-112本体(Discovery 4-layer採否・Engagement根底指示採否・News
  Ledger自動Research化)は2026-09-08にユーザーが「追加Trial・Production
  変更なし」で**DEFERRED**と決定(OPEN_ITEMS.md OPEN-112行末尾)。
- したがって「mode自体の正式採用」は**未決(DEFERRED)**であり、「Theme 2
  完成音声がAPPROVED_FOR_PRODUCTIONであること」とは明確に別の論点
  (OPEN-112行自身がこの2つを「Theme 2音声: CLOSED / 本体残件: DEFERRED」
  と分離表現している)。

---

## 7. Discovery: 既にFIX済みの部分とdeferredな上流設計の分離

**既にFIX済み(PRODUCTION_WIRED)な部分**: 現行Production記事構造
(Preview/Full Story/Point One・Two/Comment/Key Phrase/In One Line、
Evidence Compression・Numeric Precision Editor、Fact QA、TTS retry
cascade、Assembly)。ただしこれは**「Discovery」固有の実装ではなく**、
Editorial Typeの区別なしに全テーマ(Discovery labelのNo.18も、ラベルなしの
Hanshin/Health/Householdも)が通る**単一の共通経路**(§5と同じ結論)。

**deferredな上流設計**: Discovery/Why Layer3 Focus Module(4層構造の
Layer3のみDiscovery固有)は、Trial-05で実装・実記事検証済み
(`VALIDATED`相当)だが、Production Writerへの配線は行われておらず、
Production採用可否そのものが2026-09-08にOPEN-112本体残件として
`DEFERRED`(ユーザー決定、追加Trial・Production変更なし)。

**結論**: 「Discovery」という言葉には2つの層が混在している。(1)
現行Production記事の一般構造(=Family A共通骨格、PRODUCTION_WIRED済みだが
Discovery固有ではない)と、(2)Discovery固有のLayer3 Focus Module
(Trial検証済みだがProduction未配線・採否DEFERRED)。前回Reportの表(1)は
(1)を指しており、これを「Discoveryが完成している」と読むのは不正確。

---

## 8. 最終まとめ

- **Discovery**: 記事の一般構造(共通Production配管)はPRODUCTION_WIRED
  済みだが、これはDiscovery固有ではなく全テーマ共通。Discovery固有の
  Layer3 Focus ModuleはTrial検証済み(Trial-05)止まりで、Production
  採否自体が2026-09-08にDEFERRED。
- **通常News(Major/Daily News)**: Editorial Typeとしての設計・実装が
  最も手薄。OPEN-112-NEWS-MODE-DESIGN-08による設計図(2026-09-05)のみで、
  実記事Trial・Prompt文言確定・コード実装のいずれも0件。基盤の共通配管は
  稼働実績があるが、それは「通常News」固有ではなく全テーマ共通の経路。
- **Trend Synthesis**: 3枝の中で最も進んでいる。最小Prompt Trial・
  Engagement A/B・Theme2実記事Trial系列・完成音声(Theme2、
  `APPROVED_FOR_PRODUCTION`)まで到達したが、これはあくまでTrialスクリプト
  経由の一回限りの成果物であり、Trend Synthesis modeそのもののProduction
  Writer正式配線は未実施、採否自体が2026-09-08にDEFERRED。

3枝いずれも「Editorial Type」としてのコード実装は0%。差があるのは
「Trial・実記事検証がどこまで進んだか」の深さのみ(Trend Synthesis >
Discovery > 通常News)。

---

## 「不明」とした項目

- OPEN-117(全体)のBlocking区分(前回Reportで「未確認、影響範囲小」と記載
  されており、本タスクでも追加確認せず不明のまま)。
- OPEN-83(外国由来固有名詞発音)の3設計案のうちどれが有力かは本タスク
  範囲外につき未確認。
- Hanshin/Health/Household(n3_01)が「Major/Daily News」的な記事内容に
  該当するかどうかの編集的な性質判定(POOL_TOPIC_MASTER.mdに記載が無いため
  正式Editorial Typeラベルの割り当て自体が存在しない。内容がNews的か
  Discovery的かの主観的判定はSSOTで確認できないため行っていない)。
- Trend Synthesis Theme2完成音声の記事テキストが、仮にProduction Writer
  コードへ将来配線された場合に同一の結果(byte-for-byte)を再現するかどうか
  (Trialスクリプトとの差分検証はSSOT内に記録なし、不明)。
