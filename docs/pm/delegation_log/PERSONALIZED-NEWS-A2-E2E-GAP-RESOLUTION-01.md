## 管理ID

`PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01`(Phase A: 横断監査+設計、本委任)。前段: `PERSONALIZED-NEWS-A2-E2E-PREFLIGHT-01`(`docs/pm/RESULT_PACKET_PN_A2_PREFLIGHT.md`、未commit)。現在main=`222d4cbe`、並行タスクなし。報告は`docs/pm/RESULT_PACKET_PN_A2_GAP_PHASE_A.md`(新規)へ。`docs/pm/ACTIVE_TASK.md`は固定ヘッダ形式で上書き可(UDR-deferred欄に「USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-02: Space Weapons B1 2 segment Human Review Lock方針待ち」「OPEN-159 DEFERRED」「Family C 2仕様 APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE」を引継ぎ)。

## 性質/到達上限Status/禁止事項

- 性質: Preflightで判明した**B-Family A2新規topic E2E Production pathの欠落**を解消するための第1段階。**Family横断でA2生成方式をread-onlyで監査し、共通化候補を分類し、Personalized Newsを含む今後の新規topicで再利用可能なA2 E2E Production設計案を作る**。本委任(Phase A)では**Productionコードの実装は行わない**(設計案をFableが受入条件・ユーザー意図と照合した後、Phase Bで実装委任する)。ただしSSOTへの原則記録(下記)は本委任で行う。
- 到達上限Status(Phase A): `DESIGN_PROPOSED`(実装可否Gate=「そのまま実装可」と判定できた場合)または`USER_DECISION_REQUIRED`(新しい仕様判断が必要な場合、設計案+選択肢を提示)。`PRODUCTION_WIRED`はPhase B完了後にのみ到達可能。
- 禁止: Productionコード変更、Prompt変更、新runner作成、A2記事生成、API実行、TTS実行、Trial開始、B1→A2翻案の前提化、Personalized Newsだけの独自方式設計、「関数が存在する」だけでの「正式path使用」判定、ユーザー承認なしの方式選択、Open Item化による先送り(今回のA2 E2E gapはOpen Itemにしない)、`git add -A`/`stash`/`amend`/`rebase`/`force push`。

## ユーザー判断・新原則(原文要旨、忠実転記)

### 1. B1→A2翻案方式を現時点で採用しない
前回提案「B1完成記事→A2翻案入口を正式配線」は、実装量が少ないという理由だけでは採用しない。まず他Familyを横断確認し、eigo-radio全体としてA2記事をどのように生成しているか、共通化可能な正式パターンを確認する。Personalized Newsだけ独自方式を作らない。

### 新しい重要な設計・PM原則(SSOT記録対象)
今後、仕様・Production設計を考える際は常に、**他Familyを横にらみし、共通化できる部分は可能な限り共通仕様・共通Production primitiveとして設計する。**特定Familyだけを見て最小実装するのではなく、Family A/News・Discovery・Trend・Family B/Voices・Family C・その他既存Production Familyを必要に応じて横断確認する。Family固有である必要がない処理は、Family専用実装を増やすより共通化を優先する。ただし既存Production挙動を壊すような過剰一般化はしない。共通化範囲は実装前に既存仕様・runtime evidence・regression影響を確認する。この原則は今後の設計判断にも適用する。**DECISION_LOG/PM governance上の適切な正本へ記録する。未解決事項ではないためOPEN_ITEMSには入れない。**

### コスト制約の変更(SSOT記録対象)
Claudeの週間利用上限を理由に「最小実装」「最小token」を優先する必要はなくなった。今後は品質・Production整合・Family横断の共通性・保守性・再利用性・regression安全性を優先する。ただし無意味な再実行・不要なAPI消費・試行錯誤は引き続き避ける(「制限がない」は無制限Trial可の意味ではない)。

### Phase 1 — Family横断A2生成方式監査(read-only)
対象: 通常News/Discovery/Trend/Family B(Voices)/Family C/その他A2 Production実績があるFamily。各Familyで最低限: 1.Researchの作り方 2.Verified Fact Ledgerの位置づけ 3.A2 WriterがLedgerから直接書くのか 4.B1完成記事からA2へadaptするのか 5.A2/B1でResearch/Ledgerを共有するのか 6.Fact Checker 7.Ledger Deviation 8.retry/Local Rewrite 9.Leakage等Family固有QA 10.Scaffold/Comment 11.Key Phrase 12.日本語タイトル 13.TTS 14.Assembly 15.Audio Validation Gate 16.player 17.正式Production entrypoint 18.Trial/DEV依存の有無。「関数が存在する」ではなくProduction正式pathで実際に使われているかを確認。

### Phase 2 — 共通仕様候補の抽出
共通化すべきもの(例: Research/Ledger level非依存、A2 Writer input contract、Fact Checker/Ledger Deviation、retry/regeneration、scaffold handoff、title/KP input contract、TTS以降の共通handoff)とFamily固有で維持すべきもの(例: Editorial structure、Voice構成、Comment role、Leakage QA、Family固有Fact Safety、Story segmentation)に分類。特に**「A2はB1完成記事から翻案する」が本当にeigo-radio共通設計なのか**を確認。他FamilyがLedger→A2 Writer方式なら、Personalized NewsだけB1→A2翻案を採用しない。

### Phase 3 — A2 E2E正式設計
横断監査を根拠に、Personalized Newsを含む今後の新規topicで再利用可能なA2 E2E Production設計を決める。優先順位: 1.既存共通Production primitiveを再利用 2.Family横断で共通化できる入口・contractを共通化 3.Family固有ロジックだけをFamily moduleに残す 4.固定topic path/固定辞書/固定artifact依存を除去 5.Trial/DEV runnerを正式Productionから参照しない。

### 実装可否Gate
**そのまま実装可**: 既に承認済みの共通方式が明確/今回はその未配線部分を接続するだけ/新しい記事品質原則や生成方式の採用判断を必要としない。
**STOP(設計案提示)**: Family間でA2生成方式が競合/共通方式が存在しない/Ledger→A2直接WriterかB1→A2翻案か等のProduct仕様判断が必要/新しいPrompt原則が必要/Family共通仕様を新設する必要/既存承認仕様を変更する必要。ユーザー承認なしに方式を選ばない。

### Gap解消対象(今回解消、Open Item化しない)
A2新規topic Writer正式入口不在/`main_a2()`が固定topic音声化専用/固定article path/固定承認sha256前提/Key Phrase固定topic依存/日本語タイトル固定辞書依存/Writer→QA→Scaffold→AudioのE2E未接続。ユーザー判断待ちになった項目のみUSER_DECISION_REQUIRED。

### Personalized News
既存B1 2V成果物(Research/Ledgerあり、Fact Checker PASS、Ledger Deviation COMPLIANT、Comment Contract COMPLIANT、Analytical Leakage残存flag、Status PARTIAL / USER TEST READY)をA2生成に使うかは、横断監査で確定した正式A2方式に従う。B1→A2翻案を前提にしない。既存Ledgerがlevel非依存で正式再利用可能ならResearch再実行は避けてよい。Leakage残存flagをA2へ無条件に継承・許容しない(A2正式経路に既存Leakage QAがあれば実行し、受入条件内なら継続、USER_DECISION_REQUIRED相当ならSTOP)。

### Production Wiring Checklist(Phase Bで使用、設計案はこれを満たす構成であること)
新規topic A2正式初回経路/retry/fallback/regeneration/Fact Checker/Ledger Deviation/Family固有QA/Comment・Scaffold/Key Phrase/日本語タイトル/TTS/pronunciation・ASR safety/Human Review Lock/Assembly/Audio Validation Gate/player/runtime evidence/actual model_id・routing/regression test/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS整合/Git/approved仕様との一致。

### Dangling Reference Check
共通仕様が正式に存在するか/各Family初回pathから参照されているか/retry・fallbackだけに孤立していないか/Trial定義をProductionが暗黙参照していないか。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一ファイル再読禁止。D-1: Grep→該当行範囲Read、全文Readは構造把握に必須の場合のみ(本タスクは横断監査のため、entrypoint関数本体の全文Readは可)。G-1: git出力は`--porcelain`/`--stat`/`--short`で最小化。F-1: transcript退避不要。T-1: 事前指定Read/Grep一覧に従い、一覧外の追加Readは理由をRESULT_PACKETに1行記録(本タスクは監査目的のため追加Readは広く許容、ただし記録すること)。T-0: 委任文を`docs/pm/delegation_log/PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。

## Fableからの補足(既知情報、検証のこと)

- **通常News(Family A、Hanshin reference)**: `er003_v1_n3_01_articles_generate.py`(COMMON_BLOCK_TEMPLATE、Ledger→A2 Writer直接、B1はB1-B Direct Generation=Ledgerから独立生成、A2/B1でLedger共有。CURRENT_SPEC L796-860「通常News Reference仕様」、L586「B1(独立生成Natural Spoken News English)」)。直近production-set例: `er014_output/four_type_observation_01/news/run_news_a2.py`・`run_news_b1b.py`(research/共有、r3+ab01+vfl01+prod_gen)、`er014_output/user_test_news_2ep_01/space_weapons/run_pipeline.py`(2026-09-17、A2/B1をResearch1回から生成、音声まで)。音声: `er003_v1_n3_01_scaffold_generate.py`/`tts_generate.py`/`assemble.py`、`er011_human_review_lock_01.py`。
- **Discovery/Trend(Family A派生)**: `er014_output/four_type_observation_01/discovery/`・`trend/`のrun_*_a2.py/run_*_b1b.py、`er011_family_a_completion_a2_trend_end_to_end_01_run.py`、`er011_family_a_trend_synthesis_ai_manufacturing_production_run_01_writer.py`/`_audio.py`(Trend=News Editorial Mode、CURRENT_SPEC L773)。Discovery A2は`run_discovery_a2_ut06_regen.py`等。
- **Family C(Future Story)**: `er013_family_c_production_01.py`/`er013_family_c_production_runner_01.py --level a2|b1`(article_config.json起点、story segmentation、A2 Comment=日本語理解ガイド。CURRENT_SPEC「Family C(Future Story)Production」節、APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE)。Ledger/Researchの位置づけを確認。
- **Family B(Voices)**: `er012_b_family_production_runner_01.py`(`main_b1_2v()` L1253=write_new_theme[Ledger→B1 Writer新規topic]、`main_b1_3v()` L1118、`main_a2()` L1625〜=固定topic[free_address]音声化専用、`A2_SOURCE_DIR` L1313、`reuse_approved_a2_assets` sha256突合 L1374〜、`A2_THEME_KEY`固定辞書)。`er012_b_family_voices_a2_production_01.py`(`run_writer_adapt(b1_article_text)` L160=B1→A2翻案、Production runnerから未呼出。`run_fact_checker` L215/`run_ledger_deviation` L235/`run_analytical_leakage_check` L395/`run_scaffold_a2` L482/`generate_japanese_title` L531/`reuse_key_phrases_a2` L545[B1 KP dir依存])。Trial: `er012_editorial_b_voices_a2_trial02_writer.py`(adapt)、`er012_b_voices_3v_a2_user_test_01.py`(3V adapt、AI hiring A2 evidence)。CURRENT_SPEC L652-718(EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01、Phase 1=既存承認済み記事の音声化に限定と明記)、L675(Personalized News B1 PARTIAL)。**B-Family A2の承認済み仕様がB1→A2翻案を仕様として定めているか、それとも翻案はTrial方式に過ぎないかを必ず確定**(これがGate判定の鍵)。`er012_b_family_editorial_type_registry_01.py`(COMMENT_ROLES、japanese_titles辞書)。
- **Household(Discovery/Why系候補)**: `er011_household_unified_final_candidate_01_run.py`(A2/B1音声)。
- Preflight結論: `docs/pm/RESULT_PACKET_PN_A2_PREFLIGHT.md`(14項目、既読扱い可、本委任で一緒にcommit)。
- SSOT正本: PM原則は`docs/pm/PM_GOVERNANCE.md`(節構成をGrep `^## `で確認し、設計原則に該当する節へ追記または新節「Family横断共通化原則」を追加)、`docs/pm/PM_BRIEF.md`(コスト制約・token guard関連の記述をGrep `token|週間|最小|minimal`で確認し、方針変更を反映)、`DECISION_LOG.md`(1エントリ、管理ID本ID、ユーザー判断3点=翻案不採用・横断共通化原則・コスト制約変更)。CURRENT_SPECは本委任では変更しない(設計案がPhase Bで承認・実装された後に反映)。

## 事前指定Read/Grep一覧

- `CURRENT_SPEC.md`: Grep `^## |^### `で節一覧→A2関連節(CEFR-A2構造・音声仕様/B1/Cross-level/通常News/News Editorial Mode/Family C/B-Family Voices A2/Key Phrase/Preview/Audio Assembly)の該当行のみ
- 上記各runner/module: Grep `^def main|^def |stage|level|ledger|adapt|research|write_new_theme|japanese_title|key_phrase|scaffold|assemble|gate|player|import er0`→entrypoint本体と呼び出し順
- `er014_output/**/run_*.py`(news/discovery/trend/space_weapons): Grep `import er0|def main|prod_gen\.|vfl01\.|sc\.|tts_gen\.|asm\.`→呼び出しモジュール一覧
- `docs/pm/PM_GOVERNANCE.md`/`docs/pm/PM_BRIEF.md`: Grep(上記)
- `DECISION_LOG.md`: Grep `EDITORIAL-B-FAMILY-VOICES-A2|OPEN-151|FAMILY-A-DAILY-NEWS-REFERENCE|FAMILY-C.*PRODUCTION`→要旨行
- `OPEN_ITEMS.md`: Grep `OPEN-151|OPEN-147|OPEN-157|OPEN-158`(all-Family候補既存項目との関係確認)

## 手順

1. T-0。
2. Phase 1: Family別18項目マトリクス(○=正式pathで実使用/△=定義のみ・Trial経由/×=なし、根拠=ファイル:行)。
3. Phase 2: 共通化候補/Family固有の分類表。「A2=B1翻案」が共通設計か否かを明記(各FamilyのA2 Writer入力: Ledger直接/B1記事/その他)。
4. Phase 3: 設計案(構成図はテキストで可): 共通primitive(既存)の再利用箇所、共通化する入口・contract(新設が必要ならその旨)、Family固有moduleに残すもの、除去する固定依存、Personalized Newsへの適用手順(Research再実行要否、Leakage QA適用)、Production Wiring Checklist各項目の充足計画、regression対象(既存test: `er012_b_family_*test*.py`、`er013_family_c_production_test_01.py`等Globで確認)、想定コスト。
5. 実装可否Gate判定: 「そのまま実装可」の3条件を満たすか個別に○×。満たさない場合はSTOP条件のどれに該当するかと、ユーザーに必要な判断(選択肢・各案の影響・推奨)を提示。**方式を勝手に選ばない**。
6. SSOT記録(本委任で実施): PM_GOVERNANCE.md(横断共通化原則、節番号付き)、PM_BRIEF.md(コスト制約変更)、DECISION_LOG.md(1エントリ)。OPEN_ITEMSは変更しない(A2 E2E gapはOpen Item化しない)。
7. Dangling Reference Check結果を記録。
8. Git: 明示add(`docs/pm/RESULT_PACKET_PN_A2_PREFLIGHT.md`、`docs/pm/delegation_log/PERSONALIZED-NEWS-A2-E2E-PREFLIGHT-01.md`+`_check.json`、本タスクのdelegation_log+check、RESULT_PACKET_PN_A2_GAP_PHASE_A.md、PM_GOVERNANCE.md、PM_BRIEF.md、DECISION_LOG.md、ACTIVE_TASK.md[gitignore対象なら除外])。メッセージ`PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01 Phase A: Family横断A2生成方式監査+E2E設計案+横断共通化原則/コスト方針のSSOT記録(+PREFLIGHT-01成果commit)`、trailer `Task-ID: PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01`。push。

## 報告(`docs/pm/RESULT_PACKET_PN_A2_GAP_PHASE_A.md`)

0. T-0
1. Family別A2生成方式の比較(18項目マトリクス+要約)
2. eigo-radioとして共通化できる部分
3. Family固有で残す部分
4. B1→A2翻案が共通方式か否か(結論+根拠)
5. 提案するA2 E2E設計(Phase 3の内容)
6. 実装対象ファイル・Production entrypoint(設計上の予定)
7. Personalized Newsへの適用計画(Ledger再利用/Leakage QA)
8. 実装可否Gate判定(3条件○×)+STOP該当有無
9. Dangling Reference Check
10. SSOT更新結果(PM_GOVERNANCE節番号・PM_BRIEF行・DECISION_LOG行)
11. Git commit/push SHA
12. 到達Status(`DESIGN_PROPOSED`/`USER_DECISION_REQUIRED`)
13. 未決事項・ユーザーに必要な判断(あれば選択肢・影響・推奨理由)
14. 無変更証跡(`git status --porcelain CURRENT_SPEC.md OPEN_ITEMS.md er0*.py`が空)/事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一(内部識別子`b1b`はpathにのみ可)。
