# ER-010-EDITORIAL-TYPE-ARCH-BASELINE-DESIGN-02 報告書

対象: No.9 Production Baselineの固定・Rollback設計・Writer 3層分解・Neutral Block影響調査・
一般化architecture案・No.9 Regression Test設計・News/Trend Structure A互換性評価

**今回はコード変更・Prompt変更・Production配線変更を一切行っていません。調査・設計・Baseline証拠の
記録のみです。**

---

## 1. CURRENT_SPEC / Production path確認結果

### 1-1. 実行経路(確認済み、コード上の呼び出し連鎖で追跡)

```
er009_n1_production_integration_01.py (No.9専用runner、【git未追跡】)
  └─ run_writer_stage_baseline()
       └─ er006_pool_pilot_01_writer.py :: run_writer_for_theme()
            └─ er003_v1_n3_01_articles_generate.py :: run_one_pattern() / build_common_block()
                 ├─ er003_v1_en_direct_vfl_01_generate.py :: run_deviation_check()
                 ├─ er002_ja_web_research_r3.py :: build_fact_check_prompt() / run_fact_checker_with_gates()
                 ├─ er008_point_overlap_qa_18.py :: flag_possible_paraphrase()
                 ├─ er009_diagnostic_full_retry_modules_12.py :: build_diagnostic_section()
                 ├─ er003_v1_n3_01_evidence_compression_editor.py :: run_lossless_editor()
                 └─ er006_model_routing_contract_01.py :: require_model()(fail-closed)
```

`er003_v1_n3_01_articles_generate.py` が**唯一のProduction Writer本体**であることを、
①CURRENT_SPECの複数エントリでの参照、②`er006_pool_pilot_01_writer.py`が
「本番`run_one_pattern()`をそのまま呼び出す」薄いラッパーであること、③実際にNo.9を
生成した`er009_n1_production_integration_01.py`が上記の連鎖を経由していること、の3系統で
再確認した(前回タスクER-010-01と同一の結論、今回変更なし)。

### 1-2. 【新規発見】`er009_n1_production_integration_01.py` はgit未追跡

`git ls-files` / `git status --porcelain` で確認したところ、No.9を実際に生成した
runner本体 `er009_n1_production_integration_01.py` はコミットされたことが一度もない
(`?? er009_n1_production_integration_01.py`)。中身のロジック(THEME_ID・TOPIC_JA・
Standard同期TTS切替等)はDECISION_LOGの記述と一致することを確認したが、**Baseline復元の
観点では「戻すべき正式なSHAが存在しない」**という状態である(詳細は第2節・第3節)。

### 1-3. CURRENT_SPEC.md 該当箇所の現在の正文(subagent調査で確認、行番号付き)

- **Ledger Deviation Checker v2**(146行目からの「Cross-level仕様」節、該当行172): 10種類の
  意味上のFact差分(`changed_fact`/`changed_scope`/`changed_causality`/`changed_certainty`/
  `changed_number`/`changed_actor`/`changed_negation`/`changed_comparison`/`changed_time`/
  `unsupported_new_claim`)のいずれかが明確にtrueの場合のみMAJOR、`PRODUCTION_WIRED`。
- **Point Overlap QA / Diagnostic Full Retry**(276行目からの「QA / Human Review」節、
  該当行294): 2026-08-31追記として、Diagnostic Full Retry機構(診断情報生成は機械的で
  ¥0、Writer全文RetryのみLuna API課金)が`PRODUCTION_WIRED`として記載されている。
- **Model Routing Contract**(378行目からのセクション): B1/A2 Writer・Writer Fact Check・
  Support(Preview/Comment/Key Phrase)は全てGPT-5.6 Lunaに固定、Fail-Closed契約
  (`ModelContractViolation`)。

いずれも今回の調査結果(実コード)と矛盾しない。**ただし、CURRENT_SPEC 294行目自身の文中に
1件の内部矛盾を発見した(次節参照)。**

### 1-4. 【重要】CURRENT_SPECとDECISION_LOGの記述が実際のNo.9本文と食い違う箇所

CURRENT_SPEC.md 294行目(Point Overlap QA節、2026-08-31追記)は、Household回帰テストの
文脈で「原文 "growing frustration" を "strong consumer resistance" へ修正、MINOR 0 確認」
と記載している。一方 DECISION_LOG.md 2660行目(`ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14`)
は、同じ修正を**No.9自体のLedger改善**として記載している:

> 「No.9 Ledger 改善: 前回 MINOR 1 件（"growing frustration" が保証されていない傾向を暗示）
> を修正。修正："A 2026 survey found strong consumer resistance to tipping practices" へ
> 変更 → MINOR 0 件達成 (LEDGER_COMPLIANT)」

実際のNo.9本文(`er006_output/pool_pilot_01/pool_n9_tip_screens/{a2,b1b}/article.md`)を
直接読んだ結果、**この文言はどちらのファイルにも一度も存在しない**。"growing frustration"
という語句自体もNo.9出力ディレクトリ配下のどこにも存在しない。実際にこの文言のペアが
存在するのは以下の2箇所のみ:

1. `er009_n1_no9_ledger_revision_14.py` — No.9のfactを題材にした**独立診断スクリプト**
   (タイトルは`# The Tip Screen Is Not Just a Calculator`という、実際のNo.9記事
   タイトルとは異なる、ハードコードされたテスト用文字列。本番`article.md`を一切
   読み書きしていない)
2. CURRENT_SPEC自身が言及する**Household回帰テスト**の記事(Diagnostic Full Retry
   検証用に生成された、No.9とは無関係な家事テーマの記事)

**結論**: 「その修正がNo.9の本番記事に適用された」というDECISION_LOGの記述は誤りであり、
実際には診断スクリプトの捨てコードとHousehold回帰テスト記事に対する変更を、報告文の中で
No.9のものと混同したものと判断する。ただし、**No.9本文が最終的にLEDGER_COMPLIANTである
こと自体は、実際の`a2/ledger_deviation.json`(`overall_status: LEDGER_COMPLIANT`、
deviations: 0件)・`b1b/ledger_deviation.json`(同、MINOR 2件のみ)で別途確認できており、
これは事実として正しい**(結論は正しいが、その根拠として書かれた具体的な修正内容の記述が
誤り、という食い違いである)。

この指示に従い、**この食い違いは報告するに留め、DECISION_LOG.md/CURRENT_SPEC.mdを
本タスクで勝手に修正することはしない**(今回のタスク範囲外、Section 16「CURRENT_SPEC正式
変更は行わない」に該当)。第9節Open Itemsで正式な修正候補として記録する。

---

## 2. No.9 Production Baseline Snapshot

### 2-1. Baseline Code(コンポーネント一覧、SHAはHEAD時点でそのファイルへの最終変更コミット)

| Component | File / 主要関数 | 最終変更コミットSHA(日付) | 現在Productionで使用されている証拠 |
|---|---|---|---|
| Writer本体 | `er003_v1_n3_01_articles_generate.py` :: `run_one_pattern()`/`build_common_block()`/`COMMON_BLOCK_TEMPLATE` | `f6ecc1a`(2026-08-30) | `er006_pool_pilot_01_writer.py`から直接import・呼出し |
| Master article(スタイル参照) | `er002_v1_2m_masters/hanshin_ja_master.txt`(`ab01.load_master_full_text()`経由) | (前回調査で確認済み、変更なし) | `COMMON_BLOCK_TEMPLATE`の`{hanshin_master_full_text}`に埋め込み |
| A2/B1 difficulty instruction | 同ファイル内 `A2_KAI1_INSTRUCTION`/`B1_B_DIRECT_INSTRUCTION` | `f6ecc1a`(同上) | `build_prompt()`で共通blockへ結合 |
| Point Overlap QA | `er008_point_overlap_qa_18.py` :: `flag_possible_paraphrase()`(閾値0.40) | `bef70c1`(2026-08-29) | `run_point_overlap_qa_and_regenerate()`から呼出し |
| Diagnostic Full Retry | `er009_diagnostic_full_retry_modules_12.py` :: `build_diagnostic_section()` | `f46b6e1`(2026-08-30) | `build_diagnostic_retry_prompt()`から呼出し |
| Evidence Compression | `er003_v1_n3_01_evidence_compression_editor.py` :: `run_lossless_editor()` | `7aaebdf`(2026-08-29) | `_generate_and_compress_article()`内`apply_evidence_compression=True`が既定 |
| Ledger Deviation Checker v2 | `er003_v1_en_direct_vfl_01_generate.py` :: `run_deviation_check()` | `04adbeb`(2026-08-30) | `run_one_pattern()`終盤で呼出し |
| Fact Checker | `er002_ja_web_research_r3.py` :: `build_fact_check_prompt()`/`run_fact_checker_with_gates()` | (前回調査、変更なし) | 同上 |
| Directional Fact Precheck | `er008_directional_fact_precheck_08.py` :: `audit_article_directional_facts()` | (前回調査、変更なし) | 同上 |
| Preview / Comment1-4 role | `er003_v1_b1_scaffold_01_generate.py`(B1)、`er003_v1_n3_01_scaffold_generate.py`(N3合成) | `bef70c1`(2026-08-29) | `er006_pool_pilot_01_support.py`経由でNo.9 Support段で使用(DECISION_LOG「ER-009-N1-AUDIO-STAGE-01」で実行確認) |
| Model Routing Contract | `er006_model_routing_contract_01.py` :: `require_model()`(全プロセスLuna固定) | `04adbeb`(2026-08-30) | Writer/Fact Check呼出し箇所全てで`routing.require_model(...)`をinline使用 |
| Assembly / Audio Validation Gate | `er003_v1_n3_01_assemble.py` | `24c3a18`(2026-08-30) | No.9 Assembly完了(DECISION_LOG「ER-009-N1-AUDIO-STAGE-01」) |
| **No.9専用runner** | `er009_n1_production_integration_01.py` | **なし(git未追跡)** | **実際にNo.9を生成した実体だが、コミットされていないためSHAが存在しない** |

`CURRENT_SPEC.md`自体の最終更新は`94ec819`(2026-08-31、現在のHEAD)。

### 2-2. Baseline Inputs(No.9の実際のArticle-specific Input)

`er009_n1_production_integration_01.py`より(この定義自体は前述の通り未コミット):

- `theme_id`: `pool_n9_tip_screens`
- `TITLE_EN`: "Why the Tip Screen Always Suggests More Than You Meant to Give"(runner内の定義)
  ※ 実際に生成された記事の見出しはA2/B1で別々に異なる表現になっている(下記2-3参照)。
  これはWriterがTITLE_ENを直接見出しにコピーするのではなく、Fact Ledger/Topicから
  独自に見出しを生成する仕様(`COMMON_BLOCK_TEMPLATE`は`{topic}`のみを渡し、
  `{TITLE_EN}`自体はprompt内に含まれていない)であるための想定内の差である。
- `TOPIC_JA`: NYCタクシーのチップ画面研究(Haggag and Paci、2014年)+ Rutgers政策
  レポート(Michael Lahr、2022年)+ Popmenu消費者調査(2026年4月)を統合した日本語Topic文
  (runner内`er009_n1_production_integration_01.py`の`TOPIC_JA`変数、全文は同ファイル参照)
- `JAPANESE_TITLE_JA`: 「会計画面がいつも「多め」のチップを提案してくる理由」
  (`POOL_TOPIC_MASTER.md`No.9行と一致確認済み)
- `ledger_path`: `er006_output/pool_pilot_01/pool_n9_tip_screens/research/verified_fact_ledger.txt`
- `blueprint`: `None`(Shared Point Blueprint不使用、Baseline方式)

### 2-3. Baseline Output(実際の最終ファイルを直接読んで確認)

| | A2 | B1B |
|---|---|---|
| 見出し | `# Why Tip Screens Keep Asking for More` | `# When "Recommended" Means More: The Quiet Pressure of Tip Screens` |
| `## Main Story`見出し | なし(タイトル直後から本文) | あり(B1テンプレートのみの差) |
| Point One見出し文言 | "The pressure is social, not only mathematical" | "The choice is no longer private" |
| Point Two見出し文言 | "Customers are starting to push back" | "Customers are starting to push back"(A2と同一文言) |
| `## In one line…` | あり | あり |
| 総語数 | 402語 | 407語 |
| `ledger_deviation.json` | `overall_status: LEDGER_COMPLIANT`、deviations 0件 | `overall_status: LEDGER_COMPLIANT`、MINOR 2件(出典の一般化に関する軽微な指摘のみ) |
| Fact Checker verdict | `REVIEW_REQUIRED`(契約上のSTOP条件`FAIL`ではない、DECISION_LOG記載通り) | 同左 |
| Point Overlap QA | 非flagged(最終文) | 非flagged(最終文) |

**Point Two見出しがA2/B1で完全に同一文言("Customers are starting to push back")**という
のは、独立生成のはずのA2/B1が収束した結果であり、Baseline証拠として記録するが評価は
本タスクの範囲外とする。

### 2-4. Baseline Runtime / QA Evidence(コスト・非決定性含む)

- 最終確定に至るまでのコスト実測はDECISION_LOG「ER-009-N1-LEDGER-DEVIATION-
  RECALIBRATION-02」に記載(約150〜165円、うち一部は検証スクリプトの`cl.install()`
  呼び出し漏れで未記録)。
- Audio Assembly完了実績: B1 317.4秒・A2 359.3秒、clipping無し(DECISION_LOG
  「ER-009-N1-AUDIO-STAGE-01」)。
- Human Review Lock: 5segmentが到達、うち4segmentは文字起こし照合による包括的承認、
  1segment(A2 Key Phrase 3)は実際の読み上げ誤りのため`used_form`変更の上で再生成し
  `NORMALIZED_MATCH`達成。

### 2-5. 【最重要】Baseline Recovery Pointの限界

- **コード側**: 上記2-1の各SHAへ`git checkout <SHA> -- <file>`で個別に戻せる。
  CURRENT_SPEC.md記載のPRODUCTION_WIREDな挙動(Ledger Deviation v2・Diagnostic Full
  Retry等)は、いずれもHEAD(`94ec819`)時点で揃っているため、**現在のHEAD自体が
  コードのBaseline Recovery Pointとして扱える**(個別ファイルごとに巻き戻す必要はなく、
  現状のHEADがそのままBaselineという整理でよい)。
- **出力(記事)側**: `er006_output/pool_pilot_01/pool_n9_tip_screens/`
  ディレクトリ全体(article.md・ledger_deviation.json・fact_qa.json・
  articles_run_summary.json等)は**git管理外(untracked)**であることを確認した
  (`git log --all --full-history`でも一切ヒットしない)。同様に実際のrunner
  `er009_n1_production_integration_01.py`もuntracked。
  → **「一般化実装に失敗したらgit操作でNo.9の承認済み最終記事へ戻せる」という
  前提は、現状では成立しない**。戻せるのはコード(Writerロジック)だけであり、
  No.9という個別記事の承認済み最終テキストそのものは、ワーキングツリー上に
  存在する現物ファイルでしか保全されていない。
- **`articles_run_summary.json`は信頼できないBaseline証拠**: このファイルは
  `run_theme()`が`run_one_pattern()`実行直後に書き出す実行ログだが、その後
  DECISION_LOG「Ledger Deviation Recalibration」等で行われた**手作業でのテキスト
  修正はこのJSONへ反映されない**(`run_theme()`を再実行していないため)。実際、
  このJSONは`ledger_status: LEDGER_DEVIATION`・`fact_verdict: REVIEW_REQUIRED`
  という、現在の`article.md`/`ledger_deviation.json`の実際の状態(LEDGER_COMPLIANT)
  と矛盾する古い値を今も保持している。**Baseline証拠として使ってよいのは
  `article.md`本文と、その本文に対して再実行した`ledger_deviation.json`・
  `fact_qa.json`の实際のファイル内容のみであり、`articles_run_summary.json`は
  参考にしないこと**(第9節Open Itemsにも記録)。

---

## 3. Rollback Plan

### 3-1. 変更対象にする予定のもの(次タスクで一般化実装する範囲、予告)

`er003_v1_n3_01_articles_generate.py`の`COMMON_BLOCK_TEMPLATE`(Prompt文字列)、
および`split_common_sections_for_point_qa()`/`section_word_counts()`等の構造解析関数
(Neutral Block化を行う場合)。今回は変更していない(設計のみ)。

### 3-2. 変更前の状態の固定方法(本タスクでの記録)

- コード側: 本報告書 第2-1節の表に記載した各SHAが、一般化着手前のBaselineとして
  参照可能(特別な追加コミットは不要、現在のHEADがそのままBaseline)。
- 出力側: 前節の通りuntrackedのため、**本報告書の第2-3節に記載した実測値
  (見出し文言・語数・ledger_deviation内容)自体を「一般化前のNo.9最終状態の記録」
  として扱う**(この報告書がBaseline証拠の代替記録になる)。

### 3-3. Rollback時に戻す対象

1. `er003_v1_n3_01_articles_generate.py`を含む第2-1節記載の全ファイルを、一般化
   実装前のSHA(基本的には現HEAD)へ`git checkout`または`git revert`で戻す。
2. 一般化実装によって新設された新規ファイル(あれば)を削除する。
3. `er006_output/pool_pilot_01/pool_n9_tip_screens/`配下のファイルは、一般化作業中に
   誤って上書きしない限り変更対象にならない想定だが、万一誤って上書きされた場合は
   git管理外のため**復元できない**(下記3-6のリスク低減策を参照)。

### 3-4. Rollback後に再テストすべきこと

- `run_project_regression.py`全体実行(直近実績: 1954件収集・1950件PASS、既知の
  4件失敗のみ)。
- Model Routing Contractの静的監査(`er006_model_routing_contract_01_static_audit.py`)。
- 第7節で設計するNo.9 Regression Test Plan(一般化前のBaseline状態でも一度実行して
  「Rollback後はPASSに戻ることの確認」に使えるようにしておく)。

### 3-5. Rollback成功の判断基準

- 上記regressionが一般化実装前と同じPASS件数・同じ既知失敗のみであること。
- 第7節のNo.9 Regression Test Plan基準を満たすこと(Writer構造・Point役割・
  Fact Safety系QAの挙動が一般化前と一致)。
- `git diff`で対象ファイルが完全に一般化前の内容へ戻っていることを確認。

### 3-6. 【新規推奨、今回は未実施】出力側Baselineのgit保全

現状、No.9の承認済み最終記事はgit管理外であるため、一般化作業で誤ってこの
ディレクトリに触れた場合の実質的なrollback手段が無い。**一般化実装に着手する前に、
`er006_output/pool_pilot_01/pool_n9_tip_screens/`ディレクトリ全体と
`er009_n1_production_integration_01.py`を、現状のまま1回だけ専用コミットとして
記録することを推奨する**(このタスクでは commit/push 禁止のため実施していない。
第10節の次Stepとして提案)。

---

## 4. 現行Writer 3-Layer Map

前回タスク(ER-010-01)で作成した分解と一致する部分が大半だが、今回はNews/Trend
Synthesisとの共有可能性(Structure A)という観点を加味して再整理した。

| 現行Instruction/Component | Common Writing Contract | Discovery Module | Article-specific Input | 根拠 | 一般化時の扱い |
|---|---|---|---|---|---|
| Master article模倣("全体を面白く展開し、Pointは別角度、最後に一言") | — | ○(Discovery固有の構成美学として明文化されているが、実質的にはStructure A全体[Discovery+News/Trend]で共有可能な「概要→深掘り→まとめ」という骨格) | — | `COMMON_BLOCK_TEMPLATE`109-114行目 | Structure A共通のNarrative骨格としてLayer2最上位に格上げ、テーマ別の中身(何を深掘りするか)だけをEditorial Type Moduleで differ させる |
| Title/Main Story/###×2/In One Lineという記事構成の型 | ○(物理構造そのもの) | — | — | `COMMON_BLOCK_TEMPLATE`116-129行目 | Common Writing Contractの「出力形式」として維持。Editorial Typeが変わっても物理slot数(1 Main+2 Point+1 Closing)は変えない方針(第5-6節参照) |
| Main Storyの役割定義("中心ストーリーの核心のみ、背景/数値/別解釈/含意は入れない") | — | ○(Discovery/Whyの「核心→深掘り」という役割分担そのもの) | — | 131-139行目 | Editorial Type Moduleへ切り出し。News/Trendでは「変化の中心的事実」担当として同じ役割 |
| Point One/Twoの役割("本文とは別の切り口・示唆・背景・心理・社会的含意・別の因果") | — | ○ | — | 141-152行目 | 同上、Editorial Type Module。News/Trendでは「複数の最近の事実を束ねたSignal」担当 |
| 言い換えによる重複禁止(Point Balance原則) | ○(重複禁止という制約自体は型に関わらず必要) | 一部(「本文の中心的logic」という判定基準自体はDiscoveryの「core logic」概念に依存) | — | 154-177行目 | Common Contractの原則(重複禁止)として残しつつ、判定対象の記述("本文の中心的論点")はEditorial Type Moduleが定義する用語に合わせて言い換える |
| Point語数目標(30-60語、許容25-70語) | ○ | — | — | 179-181行目、`POINT_TARGET_*`定数 | Common Contract(diagnostic目安、hard capではない) |
| 記事全体語数目安(280-420語) | ○ | — | — | 183-186行目、`TOTAL_SOFT_*`定数 | Common Contract |
| Spoken-first数字原則(A〜G) | ○ | — | — | 188-199行目 | Common Contract、Editorial Type非依存 |
| Fact Ledger制約(新規Fact禁止・correlation/causation混同禁止等) | ○ | — | — | 201-216行目 | Common Contract(Fact Safety) |
| A2/B1 difficulty instruction | ○(CEFR軸はEditorial Type軸と直交) | — | — | `A2_KAI1_INSTRUCTION`/`B1_B_DIRECT_INSTRUCTION` | Common Contract、変更なし |
| Evidence Compression(Lossless Editor、post-hoc) | ○(Prompt文言ではなく別工程) | — | — | `run_one_pattern()`内`apply_evidence_compression=True`既定 | Common、全Type共通維持 |
| Point Overlap QA(閾値0.40)+Diagnostic Full Retry | ○(лexical overlapチェック自体はテーマ非依存) | 一部(「Full Storyの言い換え」という判定基準の言葉自体がMain Story/Point構造に依存) | — | `er008_point_overlap_qa_18.py`、`er009_diagnostic_full_retry_modules_12.py` | Common Contractの機構として維持。ただしDiagnostic prompt文言中の"Preserve Storytelling First."/"Preserve No Jargon."(83-84行目)は現行Discovery Writerに存在しない指示への言及であるバグ(第9節Open Item、前回タスクでも指摘済み・未修正) |
| Fact Checker / Ledger Deviation v2 / Directional Precheck | ○(記事全文blobに対する構造非依存チェック) | — | — | `er002_ja_web_research_r3.py`/`er003_v1_en_direct_vfl_01_generate.py`/`er008_directional_fact_precheck_08.py` | Common、無変更で全Type再利用可 |
| Model Routing Contract | ○ | — | — | `er006_model_routing_contract_01.py` | Common、無変更 |
| Preview role(テーマ/問題/価値/問いのフレーミング) | 一部(「ネタバレしない」という制約自体はCommon) | ○(「Main Story→Points→In One Lineを聞く」という前提のフレーミング文言) | — | `er003_v1_b1_scaffold_01_generate.py::PREVIEW_ROLE` | Editorial Type Moduleへ。News/Trendでも「これから何を聞くか」の説明自体は必要だが、言及する対象がPoint One/Twoの代わりにSignal 1/2になる |
| Comment1-4 role(Listening Focus/Mid-story Recovery/Story Meaning+Bridge/Point Recovery) | 「内部構造ラベルを含めない」という制約はCommon | ○(Part1/Part2/Point One/Point Two/In One Lineという物理slotを前提にした文脈構築) | — | 同ファイル146-192行目 | Common Contractの制約は残し、各Commentが参照する文脈の意味づけ(Comment3の"Story Meaning"等)はEditorial Type Moduleが定義 |
| Shared Point Blueprint(fact_id⇔Point所属の事前設計) | ○(仕組み自体はEditorial Type非依存) | — | — | `er008_shared_point_blueprint_01.py` | 現状`blueprint=None`でProduction未使用。将来Editorial Type Moduleごとに使うかは任意 |
| Topic/Title/Ledger/theme_id | — | — | ○ | `er009_n1_production_integration_01.py`等 | Article-specific Inputのまま。将来`editorial_type`フィールドをここへ追加する構想(今回は追加しない) |

---

## 5. Neutral Block Impact Map

「Main Story」「Point One」「Point Two」「In One Line」という現行名称を、将来
「Block A/B/C/Closing」のようなNeutral名称へ一般化した場合の影響範囲を、
位置依存(名前を変えても壊れない)か意味依存(名前・文言自体に依存するため
変更が必要)かで整理した。

| 現行名称 | 実装上の意味 | 位置依存/意味依存 | Neutral化の難易度 | 影響component |
|---|---|---|---|---|
| Main Story(タイトル直後〜最初の`###`まで) | 中心ストーリー本文 | 位置依存(`###`が現れるまでの全テキストとして抽出) | 低 | `split_article_text()`(`er003_v1_n3_01_scaffold_generate.py`103-158行目)、`split_common_sections_for_point_qa()`(位置ベース、無傷) |
| Main Story Part1/Part2分割 | TTS区切り単位 | 完全に位置依存(段落単位で語数が均等になる境界を機械的に選ぶ、記事固有マーカー不使用と明記) | 低 | 同上134-151行目。Neutral化の影響なし |
| `###`見出し=ちょうど2つという制約 | Point One/Two Bodyの検出条件 | 構造依存(意味ではなく「数が2」という制約自体) | 高(Voices等の2-4可変Perspectiveには非対応) | `split_article_text()`109行目(`RuntimeError`)、`split_common_sections_for_point_qa()`420行目(`None`を返す)、`er008_shared_point_blueprint_01.py`(2-Point固定schema)、Audio Validation Gate必須segmentリスト |
| Point One/Two(1番目・2番目の`###`) | 深掘り2箇所 | 位置依存(何番目の`###`か)だが、**LLM向けprompt文言**(`shared_point_blueprint`のrender文言、`diagnostic_full_retry_modules_12`のprompt template)は"Point One"/"Point Two"という**表示ラベル**をハードコードしている | 中 | `tts_generate.py`(107-108行目、辞書キー`"point_one"`/`"point_one_heading"`等に名称依存)、`listening_artifact_script_standard_25.py`(33-38・57-62行目、必須segmentマニフェストがキー名依存)、`er008_shared_point_blueprint_01.py`(prompt文言に"Point One"/"Point Two"を直接埋め込み)、`er009_diagnostic_full_retry_modules_12.py`(60-86行目、LLMへの指示文に"Point One"/"Point Two"を直接埋め込み) |
| `## In one line…`(見出し文言そのもの) | 結びの検出キー | **意味依存(最も危険)**。見出し文言が"In one line"という正規表現に一致しないと即`RuntimeError` | 最高 | `split_article_text()`110-112行目(記事生成そのものが失敗、TTS工程まで一切進めなくなる)、`section_word_counts()`(`er003_v1_spoken_first_01_r1_generate.py`65-66行目、見出し文言の部分一致[`"in one line" in line.lower()`]に失敗すると`header_skip`扱いとなり、**エラーにすらならずその区間の語数が黙ってゼロ集計される**、サイレント故障のリスク) |
| セグメント名(`point_one_heading`/`point_two_heading`/`full_story_part1`/`full_story_part2`/`point_one`/`point_two`/`in_one_line`) | TTS生成・Audio Validation Gate・Disfluency QA・試聴Artifactの必須segment判定に使う共通キー体系 | 名称依存(文字列そのものをdictキー・比較対象として使用) | 高(広範囲) | `er003_v1_n3_01_tts_generate.py`(107-108, 635, 648-651, 731, 747-751行目、Disfluency QA適用可否を`name == "in_one_line"`で分岐)、`er003_v1_n3_01_assemble.py`(Audio Validation Gate必須segmentリスト)、`er003_v1_spoken_first_01_r1_generate.py`(`section_word_counts`)、`er008_listening_artifact_script_standard_25.py`(必須19/21segmentのcoverage判定) |

### 5-1. 結論(Neutral Block化の推奨方針)

- **コード上の識別子(dictキー・変数名)を今すぐ`block_a`/`block_b`/`block_c`/`closing`
  へ改名することは推奨しない**。影響ファイルが最低7〜8本(TTS生成・Assembly・
  Disfluency QA・試聴Artifact・Shared Point Blueprint・Diagnostic Full Retry・
  spoken-first語数集計)にまたがり、かつ`## In one line`のようにテキスト内容自体が
  構造検出のキーになっている箇所があるため、改名だけで記事生成そのものが
  `RuntimeError`で止まるリスクがある(QCD原則の「一般化のついでにDiscovery
  Promptを壊さない」に反する)。
- **Structure A(Discovery/Why + News/Trend Synthesis)の範囲では、Neutral Block化は
  概念上のものに留め、コード識別子は現行のまま(`point_one`/`point_two`/
  `in_one_line`等)を維持する**ことを推奨する。理由: News/Trendも物理的には
  「Main相当1つ+深掘り2つ+結び1つ」という同じ2-heading構造にそのまま収まり
  (第8節参照)、コード変更を一切必要としないため。
- 真の意味でのNeutral Block化(コード識別子自体の一般化)は、`###`見出し数が
  2固定でなくなる場合(例: Voicesの2-4可変Perspective)に初めて必要になる、
  より大きな別タスクとして切り出すべきである(前回タスクER-010-01の結論
  「Voices Trial 1は2 Perspectiveに限定してPipeline変更を回避する」と整合する)。

---

## 6. 一般化architecture推奨案

### 6-1. 3層構造(既決定事項の確認)

```
Writer Prompt = Common Writing Contract + Editorial Type Module + Article-specific Inputs
```

### 6-2. 実装方式の推奨: Prompt文字列の部分差し替え(完全複製ではない)

現行`COMMON_BLOCK_TEMPLATE`(1つの巨大文字列)を、以下のように分割することを推奨する:

```python
COMMON_WRITING_CONTRACT = """
(出力形式・Point語数目標・記事全体語数目安・Spoken-first数字原則・
 Fact Ledger制約 = 第4節でCommonと分類した部分、テキストはほぼ無改変で移設)
"""

DISCOVERY_WHY_MODULE = """
(Master article模倣の説明・Main Storyの役割・Point One/Twoの役割・
 言い換え禁止の判定基準 = 第4節でDiscovery固有と分類した部分)
"""

def build_common_block(master_full_text, topic, verified_ledger_text,
                        editorial_type_module=DISCOVERY_WHY_MODULE, ...):
    return (COMMON_WRITING_CONTRACT_HEADER + editorial_type_module +
            COMMON_WRITING_CONTRACT_FOOTER).format(...)
```

- **完全複製(Editorial Typeごとに`COMMON_BLOCK_TEMPLATE`を丸ごと複製する方式)は
  推奨しない**。理由はタスク文書8節の設計原則通り: Fact Safety・Spoken-first数字
  原則・語数目安等のCommon部分に将来修正が入るたびに5箇所を同時に直さねば
  ならなくなり、前回のER-002 Editorial Angle系の教訓(仕組みが複雑化すると
  かえって「切り口が弱い」問題の診断・修正が難しくなる)とも整合しない。
- 部分差し替え方式の具体的な安全策: `editorial_type_module`引数の**既定値を
  `DISCOVERY_WHY_MODULE`にする**ことで、次タスクで一般化コードを導入した
  直後の時点では、既存の全呼び出し箇所(`run_theme()`等、引数を渡さない)が
  一般化前と完全に同一のPromptを生成する。これは実際に現行コードが
  `evidence_compression: bool = False`や`blueprint=None`で採用している
  後方互換パターン(`build_common_block()`289行目のdocstring参照)と同じ設計
  であり、リスクの低さが実証済みの手法である。

### 6-3. 影響を受けない既存モジュール(Common Layerとして無改造で再利用)

Fact Checker・Ledger Deviation Checker v2・Directional Fact Precheck・Model Routing
Contract・Evidence Compression Editorは、いずれも記事全文blobに対して動作する
構造非依存の実装であるため、Editorial Type Module導入によるコード変更は一切不要
(前回タスクER-010-01の結論を再確認)。

### 6-4. Point Overlap QA / Diagnostic Full Retryへの影響

`split_common_sections_for_point_qa()`(位置ベース、`###`見出し数=2のみに依存)は
Discovery/News-Trend共通でそのまま使える。ただし`er009_diagnostic_full_retry_
modules_12.py`のprompt template(60-86行目)が"Point One"/"Point Two"という表示
ラベルをLLMへ直接送っている点は、Editorial Type Moduleが将来Point以外の呼称
(例: News/TrendでSignal 1/Signal 2と呼ぶ場合)を使うなら、diagnostic prompt側の
ラベルも合わせて可変にする小さな追随修正が必要になる(第9節へOpen Item化)。
今回は現状維持(News/Trend Trialでも内部的には"Point One/Two"という呼称を
そのまま使い、表示上のheading文言だけをNews/Trend向けに変える方針、第8節参照)。

---

## 7. No.9 Regression Test Plan

### 7-1. 目的

一般化リファクタ(Editorial Type Module分離)によって、Discovery/Whyの品質・役割・
QA挙動が変化していないことを確認する。**ただし、第2-5節で確認した通り、現行No.9の
最終テキストは`run_one_pattern()`単体の自動生成物ではなく、その後の手作業修正
(Ledger Deviation Recalibration時の言い換え等)を経た成果物である。したがって
「一般化後にNo.9を再実行して現行`article.md`とバイト単位で一致すること」を
PASS基準にすることはできない(LLM出力の非決定性に加え、そもそも比較対象の
Baseline自体が単純な1回実行の産物ではないため)。**

### 7-2. 評価対象と対象外(Fact Safety系は変更なしとして対象外)

Fact Checker・Ledger Deviation Checker v2・Directional Fact Precheck・Model Routing
Contractは、一般化によってコード変更を受けない想定コンポーネント(第6-3節)の
ため、Regressionの主眼はWriter Prompt生成ロジックとPoint Overlap QA/Diagnostic
Full Retryの継続動作確認に絞る。

### 7-3. PASS/FAIL基準(具体案)

| 評価項目 | 確認方法 | PASS基準 | FAIL基準 |
|---|---|---|---|
| Prompt文字列の同一性(リファクタ直後、Editorial Type Module未指定時) | `build_common_block()`をDiscovery既定引数で呼び出し、リファクタ前の`COMMON_BLOCK_TEMPLATE.format(...)`出力とテキスト完全一致比較 | 1文字も違わず完全一致 | 1文字でも異なる(空白・改行含む) |
| 記事構造 | 新規生成記事に対し`split_article_text()`/`split_common_sections_for_point_qa()`を実行 | 例外を投げず、Title+Main Story+`###`×2+`## In one line`が例外なく抽出できる | `RuntimeError`または`None`が返る |
| Main Story役割 | 生成記事のMain Storyに、Fact Ledgerの「背景・補助数値・別角度解釈・deeper implications」に相当する内容が入り込んでいないか目視確認(LLMのため機械判定は困難、人手レビュー) | 深掘り情報がPointへ委譲されている | Main StoryがPoint相当の内容まで肥大化している |
| Point役割の区別 | Point One/TwoがMain Storyの言い換えでなく、異なる切り口を持つか | `flag_possible_paraphrase()`(閾値0.40)で両Pointとも非flagged | いずれかがflagged |
| Point Overlap NG時のretry動作 | 意図的にoverlapが起きやすいLedgerで生成し、Diagnostic Full Retryが発火するか確認 | retry上限2回以内で収束、または`NG_REVIEW_REQUIRED`として正しく報告される(前回のHousehold実測と同じ挙動) | retryが機能しない、または無限ループ・例外終了 |
| Fact Safety(不変のはずの3チェック) | Fact Checker/Ledger Deviation/Directional Precheckを実行 | 一般化前と同じ入力に対し同じ判定ロジックが動く(コード自体を変えていないため、判定基準の変化自体はFAIL事由にしない。呼び出しエラーの有無のみ確認) | 呼び出しが例外・型エラーで失敗する |
| A2/B1語数・構造 | `compute_metrics()`/`section_word_counts()` | 例外なく計算でき、Point語数目安(25-70語)からの逸脱が一般化前と同程度の頻度に収まる(厳密な数値一致は求めない) | 関数呼び出し自体が失敗する、または明らかに構造が壊れている(例: 語数が0または負) |
| Model Routing | 生成時のAPI呼び出しログ | 全プロセスがGPT-5.6 Lunaで実行される(`require_model()`のfail-closedが正常に通過) | `ModelContractViolation`が発生する、または別モデルが使われる |
| コスト | 生成1回あたりのAPI課金額 | 一般化前(No.8実測: writer_a2単体で約$1.5)と同程度のオーダーに収まる(新規LLM呼び出しを追加していないため) | 呼び出し回数が増え、コストが有意に増加する |

### 7-4. Regression FAIL時のSTOP条件

Section 12の指示通り、以下を明記する:

1. 上記いずれかがFAILした場合、**News/Trend Module設計へ進まない**。
2. **No.16 Trialへ進まない**。
3. 原因をFAIL項目単位で特定する(Prompt生成ロジックの実装ミスか、既存モジュール
   側の想定外の入力依存かを切り分ける)。
4. 必要なら第3節のRollback Planに従い、一般化コードのみを対象コミットへ
   `git revert`する(No.9の出力ファイル自体はそもそも一般化作業で変更しない
   想定のため、通常は影響を受けない)。
5. Rollback後、上記表の全項目を再度実行し、Rollback前(一般化実装前)と同じ
   結果に戻ることを確認する。

---

## 8. News / Trend Synthesis の Structure A互換性評価

### 8-1. 物理構造の対応関係(仮案、Promptドラフトは作成していない)

| Discovery / Why(現行) | News / Trend Synthesis(仮) | 現行コードでの扱い |
|---|---|---|
| Main Story = 中心現象の核心 | "What is changing now?"(今何が変わりつつあるか) | `###`より前のテキストブロックとして同じ物理slotにそのまま収まる。コード変更不要(第5節Neutral Block Impact Mapの結論通り) |
| Point One = 深掘りAngle 1 | Signal / Evidence cluster 1 | 1番目の`###`、位置依存のみでコード変更不要 |
| Point Two = 深掘りAngle 2 / Why it matters | Signal / Evidence cluster 2 | 2番目の`###`、同上 |
| In One Line = まとめ一言 | What this trend may mean | `## In one line`の見出し文言自体は変更しない(第5節の通り、この文言を変えると`RuntimeError`になるため、見出し文言は現行のまま固定し、中身の意味づけだけをEditorial Type Moduleで変える) |

### 8-2. 最大のリスク: 「News A → Survey B → Data C」の列挙化

タスク文書13節が明記する通り、News/Trend Synthesisの核心はSynthesis(複数の
recent factsを束ねた時に見える変化)であり、単純な列挙にしてはならない。この
懸念は、**現行Discovery/Whyで実際に発生している問題そのもの**(第9節・OPEN-91、
No.9 Point Twoが「4つの数値を連続で読み上げる調査レポート的な文章」になった
問題)と本質的に同種のリスクである。したがって:

- News/Trend Module設計時は、OPEN-91で検証済みの「Meaning First」原則
  (Factを選ぶ前に一段落の意味を決める指示)を、Discovery Module改善としてで
  はなく、**Common Writing Contract側の一般原則として先に格上げする**選択肢を
  検討する価値がある(現状はDiscovery固有の未採用Trialだが、News/Trendも
  同じ弱点を持つ可能性が高いため、両Editorial Typeに共通する原則として
  Common化した方が保守コストが低い)。これは次タスクでの意思決定事項として
  第10節へ記録する。

### 8-3. 技術的結論

News/Trend SynthesisをStructure A(Discovery/Whyと同じ物理構造)に載せること
自体は、**コード変更ゼロで実現可能**という見通しが得られた(Point数=2固定・
In One Line見出し文言固定という制約の範囲内に収まるため)。実際のPrompt文言
(Editorial Type Module本体)の設計は次タスク以降のスコープとする。

---

## 9. Risks / Open Questions

1. **【新規・要ユーザー判断】DECISION_LOG.md「ER-009-N1-DIAGNOSTIC-FULL-RETRY-
   CLOSEOUT-14」の記述誤り**: 「No.9 Ledger改善」として記載されている
   "growing frustration"→"strong consumer resistance"という具体的修正は、
   実際にはNo.9の本番`article.md`ではなく、独立診断スクリプト
   (`er009_n1_no9_ledger_revision_14.py`)のテスト文字列とHousehold回帰
   テスト記事に対して行われたものだった(第1-4節参照)。No.9自体が
   LEDGER_COMPLIANTであること自体は別途正しく確認できているため実害は
   小さいが、DECISION_LOG/CURRENT_SPECの記録としては訂正が必要。本タスクでは
   修正していない(Section 16「CURRENT_SPEC正式変更なし」のため)。
2. **【新規・重要】No.9出力ディレクトリと専用runnerがgit未追跡**: 
   `er006_output/pool_pilot_01/pool_n9_tip_screens/`と`er009_n1_production_
   integration_01.py`は一度もコミットされていない。一般化作業で誤って
   上書き・削除された場合、git操作での復元手段が存在しない(第2-5節・
   第3-6節)。次タスク着手前のコミットを強く推奨する。
3. **`articles_run_summary.json`の陳腐化**: 手作業修正後にPipeline全体を
   再実行していないため、現在の`ledger_status`等の値が実態(LEDGER_COMPLIANT)
   と矛盾したまま残っている。将来この値を機械的に参照する仕組みを作る場合は
   注意が必要(第2-5節)。
4. **OPEN-90/OPEN-91のID重複バグ**: `OPEN_ITEMS.md`に、無関係な2件ずつが
   同じID番号(OPEN-90が2件、OPEN-91が2件)で存在している。参照時の混乱
   リスクがあるため、次回OPEN_ITEMS.mdを扱うタスクでの採番修正を推奨する
   (本タスクでは修正していない)。
5. **OPEN-90(未決定)**: Key Phrase選定で高度専門語(regression discontinuity等)
   を避ける基準の正式化。`USER_DECISION_REQUIRED`のまま。
6. **OPEN-91(未決定、前回タスクからの継続)**: Writer Point Twoの「調査
   レポート的」問題へのMeaning First原則採用可否。6/6 TrialでLEDGER_COMPLIANT
   維持を確認済みだが未採用。第8-2節の通り、News/Trend Module設計時に
   Common Writing Contract側への格上げも選択肢として検討することを推奨。
7. **OPEN-95/OPEN-96(Non-blocking、TBD)**: 既存22テーマへのLedger Deviation
   Checker v2遡及監査は未実施。検証用使い捨てスクリプトの`cl.install()`
   呼び出し漏れ(コストログ欠落)が複数回再発している技術的負債。
8. **Diagnostic Full Retry promptの構造依存バグ(前回タスクからの継続、未修正)**:
   `er009_diagnostic_full_retry_modules_12.py`83-84行目が「Preserve
   Storytelling First.」「Preserve No Jargon.」という、現行本番Writer Prompt
   には存在しない概念への言及を含む。Editorial Type Module導入時にこの
   prompt文言も合わせて見直す必要がある(第6-4節)。
9. **Editorial Type Module言い換えの一貫性リスク**: News/Trend Module導入時、
   Diagnostic Full Retry・Shared Point Blueprintのprompt文言が"Point One"/
   "Point Two"という表示ラベルを固定的にLLMへ送る点(第5節)は、将来
   Editorial Typeごとに異なる呼称(Signal 1/2等)を使いたくなった場合に
   追随修正が必要になる。今回のNews/Trend Trialでは呼称を変えない方針
   (第8-1節)で当面回避できる。

---

## 10. 次タスクで実装する場合の推奨scope

1. **着手前の必須ステップ**: `er006_output/pool_pilot_01/pool_n9_tip_screens/`
   ディレクトリと`er009_n1_production_integration_01.py`を、専用コミットとして
   一度記録する(ユーザー確認の上で実施)。これがない限り、一般化実装は
   「戻せない状態で行う」ことになり、タスク文書6節のRollback原則に反する。
2. `COMMON_BLOCK_TEMPLATE`を`COMMON_WRITING_CONTRACT`(不変部分)と
   `DISCOVERY_WHY_MODULE`(第4節でDiscovery固有と分類した部分)へ分離する
   リファクタを実施し、`build_common_block()`の引数へ`editorial_type_module`
   (既定値`DISCOVERY_WHY_MODULE`)を追加する。
3. 第7節のRegression Test Planを実際に実行し、全項目PASSを確認する。
4. PASS後、News/Trend Synthesis Module(第8節の物理対応表をベースにした
   実際のPrompt文言)を設計する。その際、OPEN-91のMeaning First原則を
   Common Writing Contract側へ格上げするかどうかをユーザーに確認する
   (第8-2節)。
5. News/Trend Module設計後、No.16「Japan's New Way of Traveling」でTrial
   生成を行う(今回は生成しない)。
6. Diagnostic Full Retry prompt(第9節Item 8)の構造依存バグ修正は、今回の
   一般化と合わせて直すか、別タスクにするかをユーザーに確認する。

---

**Status: BASELINE FIXED / DESIGN ONLY — NO PRODUCTION CHANGE**
