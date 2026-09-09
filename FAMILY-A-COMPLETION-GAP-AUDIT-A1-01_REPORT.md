# FAMILY-A-COMPLETION-GAP-AUDIT-A1-01 — Family A 3 Editorial Type Gap確定(読み取り専用)

管理ID: FAMILY-A-COMPLETION-GAP-AUDIT-A1-01(Lane A, Step A1)
実施日: 2026-09-09
性質: **読み取り専用Gap Audit**。編集・Trial・API呼び出し・Git操作は一切
行っていない。並列稼働中の他Lane(Lane B 3V Trial `er012_*`、Ledger
Deviation Checkerコスト調査、SSOT統合)の成果物は参照していない。
`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`は編集していない。

前提: 記憶・推測で埋めず、以下のSSOT/Reportを実際に確認した(巨大SSOTは
管理ID・語でGrepし該当箇所のみ読了)。

- `OPEN_ITEMS.md` OPEN-112/113/129/130/132/133/134行(全文)
- `FAMILY-A-BRANCH-FACT-CHECK-02_REPORT.md`
- `FAMILY-A-TREND-SYNTHESIS-PRODUCTION-READINESS-01_REPORT.md`
- `OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01_REPORT.md`
- `FAMILY-A-DAILY-NEWS-REFERENCE-FORMALIZATION-01_REPORT.md`
- `OPEN-112-NEWS-MODE-DESIGN-08_REPORT.md`
- `FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-TRIAL-01_REPORT.md`
- `FAMILY-A-POINT-ROLE-PLANNING-FOCUS-MODULE-CONNECTION-TRIAL-03_REPORT.md`
- `FAMILY-A-DISCOVERY-DEFERRED-CLASSIFICATION-01_REPORT.md`
- `ARTIFACT_REGISTRY.md`(Hanshin/Health/Household記録、Theme2記載なしを
  確認)
- Production code: `er006_pool_pilot_01_writer.py`
  (`run_writer_for_theme`)、`er003_v1_n3_01_articles_generate.py`
  (`build_common_block`/`resolve_editorial_type_module_block`/
  `EDITORIAL_TYPE_MODULE_BLOCKS`辞書の実内容)

`FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-02/-04_REPORT.md`は
OPEN_ITEMS.md OPEN-112行の追記(全文)から内容確認した(個別ファイルは
未読了、OPEN_ITEMS集約記述で内容が確認できたため。§末尾「不明」参照)。

---

## 0. コード実態の直接確認(重要な前提)

`er003_v1_n3_01_articles_generate.py`の`EDITORIAL_TYPE_MODULE_BLOCKS`辞書
(451-453行)を実際に読んだ:

```python
EDITORIAL_TYPE_MODULE_BLOCKS = {
    "trend_synthesis": TREND_SYNTHESIS_FOCUS_MODULE_BLOCK + "\n\n" + TREND_SYNTHESIS_ENGAGEMENT_BLOCK,
}
```

**キーは`"trend_synthesis"`1件のみ**。Discovery/Whyにも
Major/Daily Newsにも対応するmode文字列は一切登録されていない
(`resolve_editorial_type_module_block()`は未知mode文字列に対し
`ValueError`をraiseするfail-closed設計、456-468行で確認)。

---

## 1. 3タイプ×15項目 Status表

Status略号: `PRODUCTION_WIRED` / `APPROVED_FOR_PRODUCTION but unwired` /
`VALIDATED` / `USER_DECISION_REQUIRED` / `DEFERRED` / `UNIMPLEMENTED`

### 共通(全テーマ共通のPRODUCTION_WIRED基盤)——タイプ別表の前に集約

| 項目 | Status | 根拠 | 注記 |
|---|---|---|---|
| Writer正式初回path | `PRODUCTION_WIRED`(共通) | `er006_pool_pilot_01_writer.py::run_writer_for_theme()`→`er003_v1_n3_01_articles_generate.py::run_one_pattern()` | Editorial Type非分岐の単一経路。3タイプとも同じ関数を通る |
| Fact Checker・Ledger Deviation Checker | `PRODUCTION_WIRED`(共通) | `er003_v1_en_direct_vfl_01_generate.py`、Ledger Deviation 10種変化検知 | mode非依存。trend overclaim/source strength専用カテゴリなし(既知Gap、OPEN-112-NEWS-MODE-DESIGN-08§10) |
| Point Overlap QA・Point Value QA・Diagnostic Full Retry | `PRODUCTION_WIRED`(共通) | `er009_diagnostic_full_retry_modules_12.py`、G1回帰修正(OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01、commit`8596f34`) | G2(cross_point_overlapのstill_flagged統合)は`DEFERRED`(OPEN-133、A-UDR-21でSSOT記載を実態[未実装]へ訂正済み)。News/Trend共有語彙による誤flagは既知Gap |
| A2・B1等level展開 | `PRODUCTION_WIRED`(共通) | `build_common_block()`のlevel非分岐設計、Evidence Compression Editorがlevel/genre引数を持たない(OPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-CHECK-01で確認) | |
| Key Phrase選定・canonicalization・Redundancy QA | `PRODUCTION_WIRED`(共通) | `er003_v1_n3_01_scaffold_generate.run_key_phrases()`、gloss括弧回避配線(KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-WIRING-01) | mode非依存 |
| TTS・retry cascade・Repetition/False Start QA・Connected Speech Equivalence・Transcript Style Normalization | `PRODUCTION_WIRED`(共通) | `er003_v1_n3_01_tts_generate.py`、OPEN-121/122/123 | mode非依存、Theme2実績で確認済み |
| Audio Validation Gate(状態検証) | `PRODUCTION_WIRED`(共通) | `er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate()` | 既存entryの状態(ASR一致等)のみ検証 |
| Audio Validation Gate(構造完全性、opt-in) | `PRODUCTION_WIRED(opt-in)`(共通、A/B Family双方に定義あり) / mandatory化`DEFERRED` | OPEN-129、`required_structure`引数(既定`None`=OFF) | 既存3呼び出し元(`load_b1_sources`等)は引数省略のままopt-out。A-Family用`derive_a_family_required_structure()`は実装済みだが、A-Family側runnerが実際にこの引数を渡しているかは本タスク範囲では未確認(不明) |
| Assembly・最終artifact生成 | `PRODUCTION_WIRED`(共通) | `stage_assemble_a2`/`stage_assemble_b1` | mode非依存 |

### (A) Discovery/Why

| # | 項目 | Status | 根拠(管理ID・ファイル) | 注記 |
|---|---|---|---|---|
| 1 | theme input | `PRODUCTION_WIRED`寄り(人手選定) | POOL_TOPIC_MASTER.md No.18 | テーマ選定自体は人間が実施。自動選定パイプラインなし |
| 2 | Editorial Type指定・判定 | `UNIMPLEMENTED` | `EDITORIAL_TYPE_MODULE_BLOCKS`辞書に`"discovery"`等のキー無し(§0確認) | No.18生成時もDiscovery固有コード分岐は未使用(`FAMILY-A-BRANCH-FACT-CHECK-02_REPORT.md`§1) |
| 3 | Research・Web Search | `PRODUCTION_WIRED`(共通、Discovery固有ではない) | 既存Fact Checker独立Web検索 | Discovery固有のResearch経路は存在しない |
| 4 | Ledger・Reference生成・供給 | `PRODUCTION_WIRED`(共通経路のみ、Discovery固有の自動供給なし) | 同上 | No.18のLedgerは既存共通経路で作成、Discovery固有ではない |
| 5 | Focus Module・Editorial Type固有Prompt | `VALIDATED`(Trial止まり)、採用可否`DEFERRED` | `OPEN-112-A-FAMILY-4LAYER-PROMPT-DESIGN-TRIAL-05`(`er011_open112_a_family_4layer_prompt_trial_05.py`) | Article-onlyのTrial(No.18)のみ。Production Writerへの配線は0件。採否は2026-09-08ユーザー決定で`DEFERRED`(解釈強化リスクとのtrade-off未決) |
| 6 | Writer正式初回path | `PRODUCTION_WIRED`(共通、Discovery固有分岐なし) | 上表 | |
| 7 | Fact Checker・Ledger Deviation | `PRODUCTION_WIRED`(共通) | 上表 | Discovery Layer3採用時は`REVIEW_REQUIRED`件数増加(A2 0→3、B1 3→5)の既知リスク(`OPEN-112-DISCOVERY-4LAYER-FINAL-ADOPTION-READINESS-AND-OPEN114-REGISTER-07`) |
| 8 | Point QA・Value QA等 | `PRODUCTION_WIRED`(共通) | 上表 | |
| 9 | retry・fallback・regeneration | `PRODUCTION_WIRED`(共通) | 上表 | |
| 10 | A2・B1等level展開 | `PRODUCTION_WIRED`(共通) | 上表 | No.18はA2/B1両方生成済み |
| 11 | Comments・Key Phrase | `PRODUCTION_WIRED`(共通) | 上表 | |
| 12 | TTS | `PRODUCTION_WIRED`(共通、ただしDiscovery固有Layer3を使ったTTS実績は無し) | 上表 | No.18の完成音声は共通経路のみで生成(Layer3不使用) |
| 13 | Audio QA・Structural Gate | `PRODUCTION_WIRED`(共通) | 上表 | |
| 14 | 最終artifact | `USER_FINAL_AUDIO_REVIEW_REQUIRED`(A2)/`STOPPED`実績あり(B1) | `ER-011-NO18-DISCOVERY-WHY-FULL-PRODUCTION-RUN-01`(2026-09-02) | B1は`in_one_line`が3attempt ASR不合格でGate STOP(旧OPEN-107関連)。その後の全体的なKey Phrase/TTS改善(OPEN-116/119等)適用後にB1が最終的にどう解決したか、本タスク範囲では再確認できず**不明** |
| 15 | runtime evidence | 存在(2026-09-02、Layer3不使用版) | 同上 | Discovery固有Layer3を使った完成音声のruntime evidenceは**存在しない**(Article-onlyのTrial-05のみ) |

### (B) Trend Synthesis

| # | 項目 | Status | 根拠 | 注記 |
|---|---|---|---|---|
| 1 | theme input | `VALIDATED`(人手選定+一回限りTrial) | Theme2「若者の旅」(手動選定) | 自動テーマ選定・Mode自動判定パイプラインなし |
| 2 | Editorial Type指定・判定 | `PRODUCTION_WIRED`(手動指定のみ、自動判定は`UNIMPLEMENTED`) | `editorial_mode="trend_synthesis"`引数(`run_writer_for_theme`)、`OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01`(commit`9a09103`/`ef39ed2`、Fable受入済み`PRODUCTION_WIRED`) | Mode判定基準(単一起点/集約質問)は設計のみ(`OPEN-112-NEWS-MODE-DESIGN-08`§4)、コード実装0件。判定は人間が実施し`trend_gate_checklist`引数で手動記録するのみ |
| 3 | Research・Web Search | `USER_DECISION_REQUIRED`(自動化未検証) | `FAMILY-A-TREND-SYNTHESIS-PRODUCTION-READINESS-01_REPORT.md`§5 | Theme2 Ledgerは人間がWebSearchで手動収集・手動検証(Trial-12でF-005/F-009誤り発見・一次資料で手動修正)。既存自動Research pipeline(`er002_ja_web_research_r3.py`)との接続は未検証 |
| 4 | Ledger・Reference生成・供給 | `PRODUCTION_WIRED(手動供給が正式initial path)` | `OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01_REPORT.md`§4「承認済みLedgerの手動供給が正式initial path」 | 自動供給は`USER_DECISION_REQUIRED`のまま残件。Reference Digest(施策2)は不採用(Engagement施策1のみ採用、施策2は含めない) |
| 5 | Focus Module・Editorial Type固有Prompt | `PRODUCTION_WIRED` | `TREND_SYNTHESIS_FOCUS_MODULE_BLOCK`+`TREND_SYNTHESIS_ENGAGEMENT_BLOCK`(`EDITORIAL_TYPE_MODULE_BLOCKS["trend_synthesis"]`、§0でコード実在確認済み) | Point Role Planningへの役割hint接続は`VALIDATED`止まり未配線(Trial-03、下記共通Gap参照) |
| 6 | Writer正式初回path | `PRODUCTION_WIRED` | 同上 | |
| 7 | Fact Checker・Ledger Deviation | `PRODUCTION_WIRED`(共通、mode非依存で実証済み) | WIRING-01§5 runtime evidence(B1B: `LEDGER_COMPLIANT`、Local Rewrite 1回でMAJOR解消) | trend overclaim/source strength専用カテゴリ欠如は既知Gap(既存タグで代替検知、severityは一律MINOR) |
| 8 | Point QA・Value QA等 | `PRODUCTION_WIRED`(共通) | WIRING-01§5(B1B Diagnostic Full Retry 2回でPASS、A2はrerun_02[追加1回]でOK到達) | run間分散大(A2 Point Overlap ratio 0.31〜0.66)、原因未特定(Focus Module起因かsampling varianceか切り分け未実施) |
| 9 | retry・fallback・regeneration | `PRODUCTION_WIRED`(共通、mode保持を実runで確認) | WIRING-01§3 | |
| 10 | A2・B1等level展開 | `PRODUCTION_WIRED`(共通) | | |
| 11 | Comments・Key Phrase | `PRODUCTION_WIRED`(共通、wiring後の経路でも実証) | WIRING-01§11.2(`REDUNDANCY_PASS`) | |
| 12 | TTS | **`UNIMPLEMENTED`(wiring後の経路では未実施)** | WIRING-01§5・§11 | 重要な発見: Production Wiring後の`editorial_mode="trend_synthesis"`経路によるruntime evidenceは**Key Phrase選定まで**で止まっており、TTS/Assembly/完成音声には未到達。Theme2の完成音声(rerun_04、`APPROVED_FOR_PRODUCTION`)は**Wiring前の一回限りTrialスクリプト**(`er011_open112_trend_theme2_b_final_audio_rerun_04.py`等)で生成されたものであり、Wiring後の正式経路とは別run |
| 13 | Audio QA・Structural Gate | 上記12と同じ理由で`UNIMPLEMENTED`(wiring後経路) / Theme2完成音声はGate通過実績あり(旧経路) | 同上 | |
| 14 | 最終artifact | `APPROVED_FOR_PRODUCTION`(Theme2 A2/B1、ただし旧Trialスクリプト経路の成果物) | OPEN_ITEMS.md OPEN-112行「Theme 2音声: `CLOSED`」、PM-CLOSEOUT-CONSOLIDATION-07/08 | ARTIFACT_REGISTRY.mdにTheme2の記載は**無い**(記録はOPEN_ITEMS.md/DECISION_LOG.mdのみ、grep確認済み)。この完成音声がWiring後の正式経路で再現可能かは`FAMILY-A-BRANCH-FACT-CHECK-02_REPORT.md`「不明」項目のまま |
| 15 | runtime evidence | 存在(2系統、性質が異なる) | WIRING-01(text+KeyPhraseまで)/旧rerun_04系列(完成音声まで) | 「theme入力→完成artifact」を**Wiring後の正式経路だけで**一気通貫させたruntime evidenceは、本タスク範囲で確認できた限り**存在しない** |

### (C) 通常News(Major/Daily News)

| # | 項目 | Status | 根拠 | 注記 |
|---|---|---|---|---|
| 1 | theme input | `UNIMPLEMENTED`(Major/Daily Newsラベルでの選定実績なし) | Hanshin/Health/HouseholdはEditorial Type概念導入前の生成物(`FAMILY-A-BRANCH-FACT-CHECK-02_REPORT.md`§5) | Reference指定(`FAMILY-A-DAILY-NEWS-REFERENCE-FORMALIZATION-01`)はあるが、正式Major/Daily Newsラベル下でのテーマ選定・生成は0件 |
| 2 | Editorial Type指定・判定 | `VALIDATED`(設計のみ、判定基準に非対称性あり)、コード実装`UNIMPLEMENTED` | `OPEN-112-NEWS-MODE-DESIGN-08`§4、`EDITORIAL_TYPE_MODULE_BLOCKS`辞書に`"major_daily_news"`キー無し(§0確認) | Major/Daily Gate 6項目は「消去法的・非対称」(OPEN-130、`DEFERRED`)。将来自動判定には排他的・再現可能なロジックが必要 |
| 3 | Research・Web Search | `UNIMPLEMENTED`(News固有Trial実施0件) | `FAMILY-A-BRANCH-FACT-CHECK-02_REPORT.md`§5 | 共通経路自体はHanshin等で稼働実績があるが、Major/Daily Newsラベル下でのTrialは0件 |
| 4 | Ledger・Reference生成・供給 | `VALIDATED`(reference指定のみ)、News固有Focus Module用Ledger供給は`UNIMPLEMENTED` | `FAMILY-A-DAILY-NEWS-REFERENCE-FORMALIZATION-01_REPORT.md` | Hanshin/Health/Householdを構造・Fact Safety・音声referenceとして正式指定(CURRENT_SPEC新設節)。ただしこれはreference指定であり、Focus Module込みの新規生成ではない |
| 5 | Focus Module・Editorial Type固有Prompt | `VALIDATED`(設計案のみ、Trial実行0件) | `FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-TRIAL-01_REPORT.md`(mode名候補`major_daily_news`、Prompt文言ドラフト、Point Role候補7件) | 「これは既存Production Prompt文言に語彙・書式を合わせた新規ドラフトであり`APPROVED_FOR_PRODUCTION`ではない」と明記。Comparison Trial-02/04(OPEN_ITEMS集約記述)でHanshin Ledger固定のA2/B1B比較を実施したが結果はN数不足で方向不確定(baseline/focus NG率がレベル別に逆方向) |
| 6 | Writer正式初回path | `PRODUCTION_WIRED`(共通、News固有分岐は無し) | 上表(共通) | |
| 7 | Fact Checker・Ledger Deviation | `PRODUCTION_WIRED`(共通) | 上表 | News固有の専用カテゴリ欠如は既知Gap(Trend Synthesisと同一系統) |
| 8 | Point QA・Value QA等 | `PRODUCTION_WIRED`(共通)、News固有診断語彙は`UNIMPLEMENTED` | `OPEN-112-NEWS-MODE-DESIGN-08`§10 | Diagnostic Full Retry診断語彙(evidence listing/daily newsの背景過多/Point role collapse)は存在しない(Gap) |
| 9 | retry・fallback・regeneration | `PRODUCTION_WIRED`(共通) | 上表 | |
| 10 | A2・B1等level展開 | `PRODUCTION_WIRED`(共通、ただしMajor/Daily Newsラベルでの実績なし) | 上表 | |
| 11 | Comments・Key Phrase | `PRODUCTION_WIRED`(共通、実績はHanshin等の旧生成物のみ) | 上表 | |
| 12 | TTS | `PRODUCTION_WIRED`(共通、Major/Daily News固有Focus Moduleを使った音声実績は0件) | 上表 | |
| 13 | Audio QA・Structural Gate | `PRODUCTION_WIRED`(共通) | 上表 | |
| 14 | 最終artifact | Hanshin/Health/Household(旧経路生成物): ARTIFACT_REGISTRY.mdで`NOT_APPROVED`(機械QAのみPASS、人間試聴`NOT_REVIEWED`) | `ARTIFACT_REGISTRY.md`45-66行 | Major/Daily Newsラベル下での新規生成・完成artifactは0件 |
| 15 | runtime evidence | `UNIMPLEMENTED`(News固有Focus Module使用runtime evidence 0件) | 全報告確認、Trial実行記録なし | Discovery/Trend Synthesisと異なり、実記事Trial(Trial-09相当)が一度も実施されていない(比較Trial-02/04はFocus Module案文言込みで実施したが完成音声までは到達していない、text-onlyのまま) |

---

## 2. 「theme入力→完成artifact」連続性: 現状人手介在が必要な箇所

3タイプ共通:

1. **テーマ選定**: 3タイプとも自動選定パイプラインなし(POOL_TOPIC_
   MASTER.mdからの人間による選定、またはTrialごとの人間による一回限りの
   テーマ選定)。
2. **Editorial Mode/Type判定**: Trend Synthesisのみコード引数
   (`editorial_mode="trend_synthesis"`)が存在するが、判定自体
   (単一起点質問/集約質問への回答)は人間が行い、`trend_gate_checklist`
   引数へ手動で結果を記録する。Discovery/Major-Daily Newsはmode文字列
   自体が未登録(§0)。
3. **Ledger/Reference供給**: 3タイプとも「承認済みLedgerファイルを
   手動で用意し、パス経由で渡す」が正式initial path
   (`OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01_REPORT.md`§4)。
   既存自動Research pipeline(`er002_ja_web_research_r3.py`)との接続は
   いずれのタイプでも実施・検証されていない。
4. **Trial script経由の段**: Trend SynthesisのTheme2完成音声
   (`APPROVED_FOR_PRODUCTION`)は、Production Wiring完了前の一回限り
   Trialスクリプト(`er011_open112_trend_theme2_b_final_audio_rerun_04.py`
   等)により生成されたものであり、Wiring後の正式経路(`editorial_
   mode="trend_synthesis"`)ではまだ完成音声まで到達したruntime evidence
   がない(§1(B)-12/13/15)。

---

## 3. 3タイプ共通Gap と タイプ固有Gap の分離

### 共通Gap(3タイプいずれにも影響)

1. **Point Role PlanningへのFocus Module未接続**
   (`FAMILY-A-POINT-ROLE-PLANNING-FOCUS-MODULE-CONNECTION-TRIAL-03`、
   `VALIDATED`、未配線)。Focus Moduleの語彙(mechanism/counter-signal等)
   がPoint Role Planningの役割選択(独立LLM呼び出し)へ届かない。Trend
   Synthesisは現在稼働中のためこの断絶の影響を直接受ける。Discovery/
   Major-Daily Newsは、そもそも各Focus Module自体が未配線のため影響は
   顕在化前だが、将来配線時に同じ問題を持ち込む。
2. **Ledger自動供給**: 3タイプとも手動供給が正式initial path。既存
   自動Research pipelineとの接続は未検証(`USER_DECISION_REQUIRED`)。
3. **Mode/Editorial Type判定の自動化**: 未実装(Trend SynthesisはWiring
   済みだが判定自体は人間が実施)。
4. **Diagnostic Full Retry診断語彙のNews/Trend拡張**: 未実装
   (`OPEN-112-NEWS-MODE-DESIGN-08`§10、`FAMILY-A-TREND-SYNTHESIS-
   PRODUCTION-READINESS-01_REPORT.md`§2)。
5. **Ledger Deviation Checkerのtrend overclaim/source strength専用
   カテゴリ欠如**: 既存タグで代替検知しているが専用カテゴリはない
   (Discovery/News/Trendいずれにも共通の既知Gap)。
6. **G2(cross_point_overlapのretry判定統合)未実装**(OPEN-133、
   `DEFERRED`、A-UDR-21でSSOT記載を実態に合わせ訂正済み)。
7. **Audio Validation Gate構造完全性チェックのmandatory化未実施**
   (OPEN-129、opt-in配線済みだがA-Family runnerが実際に
   `required_structure`引数を渡しているかは本タスク範囲では未確認、
   mandatory化は`Trigger未達`でDEFERRED)。
8. **Point Overlap Loop Budget到達時のNG率**: G1修正後も未解消(OPEN-134、
   観測継続中、Exit条件は§4参照)。

### タイプ固有Gap

- **Discovery/Why固有**: Layer3 Focus Module採用可否そのものが
  `DEFERRED`(解釈強化リスク[Fact Checker REVIEW_REQUIRED増加]との
  trade-off判断待ち)。No.18のB1完成音声の最終到達状況は本タスク範囲では
  再確認できず**不明**。
- **Trend Synthesis固有**: (a) Mode判定自動化・(b) News Ledger自動供給・
  (c) Reference Digest追加検証・(d) Diagnostic Full Retry診断語彙拡張の
  4件が明示的に「Trial候補として仕様化せず据え置き」(WIRING-01)。加えて
  Wiring後経路でのTTS/Assembly/完成音声のruntime evidence欠如(§1参照)。
  A2 Point Overlap ratioのrun間分散(0.31〜0.66)の原因未特定。
- **Major/Daily News固有**: Editorial Typeとしての実装深度が3タイプ中
  最も浅い。Focus Module設計案(Trial-01)・比較Trial(Trial-02/04)は
  存在するが、コード実装0%・完成記事0件・完成音声0件。加えて
  Household記事はNews対象外の可能性が高いという新規発見
  (Trial-01§2.2、A-UDR-9でHousehold除外は決定済み)、Major/Daily Gate 6
  項目の非対称性(OPEN-130、`DEFERRED`)。

---

## 4. Step A2/A3/A4への引き継ぎ: 着手可能な既承認範囲の作業 と ユーザー判断が必要な項目

### Step A2(Trend Synthesis)

**着手可能な既承認範囲の作業(推奨順)**:
1. Wiring後の正式経路(`editorial_mode="trend_synthesis"`)でKey Phrase
   選定後のTTS/Assembly/Audio Gateまでruntime evidenceを完走させる
   (既存承認済み経路の続行であり新規仕様ではない可能性が高いが、
   費用発生を伴うため着手前にFable/ユーザーへ確認推奨)。
2. A2 Point Overlap ratio分散の観測継続(A-UDR-7、Production runでの
   軽量観測、既存決定どおり追加Trial不要)。

**ユーザー判断が必要な項目(推奨順)**:
1. Mode判定自動化の要否(精度検証未実施)。
2. News Ledger自動供給への統合要否(自動Research pipelineとの互換性
   未検証)。
3. Reference Digest(施策2)追加検証要否。
4. Diagnostic Full Retry診断語彙拡張要否。
5. Point Role Planning接続(Trial-03案(b))のProduction配線要否。

### Step A3(通常News/Major-Daily News)

**着手可能な既承認範囲の作業(推奨順)**:
1. 現状、Focus Module・Prompt文言・Mode判定基準はいずれも
   `VALIDATED`(設計)止まりで`APPROVED_FOR_PRODUCTION`に至っていない
   ため、Production配線に直接着手できる既承認範囲の作業は**存在しない**
   (Trial-01の設計案・Prompt文言案は明示的に「未採用」「ドラフト」と
   記載されている)。

**ユーザー判断が必要な項目(推奨順、Trial-01§6の6項目を踏襲)**:
1. Major/Daily variant設計案(Prompt文言・mode名`major_daily_news`)の
   採用可否。
2. Household記事のNews分類対象外という発見への対応(A-UDR-9で除外は
   既に決定済みだが、これに伴うHanshin/Health/Household一括reference
   枠組みの修正要否)。
3. Health記事の境界(単一研究発表 vs 大規模メタ分析)の扱い。
4. Major/Daily Gate 6項目の非対称性の扱い(OPEN-130、将来自動判定時に
   排他的・再現可能なロジックへの書き換えが必要という指摘は既に記録済み)。
5. myth-correction候補(Household由来)の採否。
6. Hanshin Ledger再利用による検証Trial実施の可否・時期
   (概算¥30〜80、Comparison Trial-02/04で既に類似の比較は実施済みだが
   結論不確定)。

### Step A4(Discovery/Why)

**着手可能な既承認範囲の作業(推奨順)**:
1. No.18のB1完成音声の現状到達状況の再確認(過去のGate STOP後、
   その後の全体的なKey Phrase/TTS改善[OPEN-116/119等]適用後にどう
   なったかは本タスク範囲では不明。読み取り専用の状況確認自体は
   既承認範囲の作業として着手可能)。

**ユーザー判断が必要な項目(推奨順)**:
1. Discovery 4-layer Focus Module Production採用可否(解釈強化リスクとの
   trade-off、Fact Checker REVIEW_REQUIRED増加[A2 0→3、B1 3→5]の許容
   要否)。
2. Engagement根底指示(Trend Synthesisで採用済み)のDiscoveryへの共通
   適用要否(未検証)。
3. ER-010-EDITORIAL-TYPE-*設計文書2件の正式Decision化(git commit)要否。

---

## 5. OPEN-134観測との関係

OPEN-134(Point Overlap NG 12本中5本[42%]がG1修正対象外の原因[Value QA
単独FAIL 3件・Fact Checker FAIL 2件]によるもの)は、2026-09-09ユーザー
正式決定(A-UDR-22)によりExit条件が明文化されている。Completion作業で
正式Production runが発生した場合、以下の条件に該当すれば観測runとして
記録すべき:

- **対象**: Production正式pathでの記事生成run(A-Family通常News・Trend
  Synthesis、A2/B1B)。
- **観測量**: 次の20 run(10記事×A2/B1B)または30日のいずれか早い方。
- **記録内容**: run単位でNGをPoint Overlap(初回/retry後)/Value QA/
  Fact Checker FAIL/Ledger Deviation/その他に分解し、
  `er011_output/point_overlap_observation_log.jsonl`へ記録。
- **主要因判定**: 単一failure modeがNG runの50%以上かつ4件以上→
  「主要因」と判定し改善Trial起票を`USER_DECISION_REQUIRED`で提示。
- **全体NG率の再対策閾値**: 20 run中NG率40%以上(8件以上)→再対策検討を
  `USER_DECISION_REQUIRED`で提示。20%以下→観測終了(closeout報告)。
  中間(20〜40%)→追加10 runの観測延長を1回だけ可。
- **現状**: 観測run #1(B1B)・#2(A2)がHanshin・Production正式path
  (`run_writer_for_theme`、mode指定なし)で記録済み(両run
  `ng_cause=Point Overlap[retry後もNG]`)。残り18 run。

Step A2/A3/A4でTrend Synthesis・通常News・Discoveryいずれかの
Production正式pathでの記事生成runが発生した場合、上記条件に該当するかを
都度確認し、該当すれば`point_overlap_observation_log.jsonl`へ記録すること。

---

## 「不明」とした項目

- No.18(Discovery)のB1完成音声が、旧OPEN-107 STOP以降の全体的な
  Key Phrase/TTS改善(OPEN-116/119/121/122/123等)適用後に最終的にどう
  解決したか(本タスク範囲では再確認していない)。
- `FAMILY-A-DAILY-NEWS-FOCUS-LAYER-COMPARISON-TRIAL-02/-04_REPORT.md`の
  個別ファイル内容(OPEN_ITEMS.md OPEN-112行の追記から内容確認したのみ、
  原本ファイルは本タスクでは開封していない)。
- A-Family用`derive_a_family_required_structure()`(OPEN-129)が、
  現行のA-Family runner(通常のProduction Writer/Assembly経路)から
  実際に`required_structure`引数付きで呼ばれているか、それとも
  Lane B(B-Family)側からのみ呼ばれているか(本タスク範囲では未確認)。
- Trend Synthesis Wiring後経路(`editorial_mode="trend_synthesis"`)の
  runtime evidenceが、Key Phrase選定より先(TTS/Assembly/Audio Gate)へ
  進んだ記録がSSOT内に存在するか(本タスクで確認した範囲では見つからず、
  「存在しない」と暫定的に記載したが、他Lane[Lane B等]の成果物を
  参照していないため完全な確証ではない)。
- OPEN-117(Blocking区分)・OPEN-83(発音3設計案の有力案)は前回監査
  (`FAMILY-A-BRANCH-FACT-CHECK-02_REPORT.md`)同様、本タスク範囲外につき
  未確認のまま。
