## 管理ID

LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01(Part A=現行 Ledger Check / Deviation Check の役割整理・hard/soft 区別・信頼性の最低ライン・Hormuz 事例 trace、委任 _01)。**read-only 調査**。一時ファイル `docs/pm/ACTIVE_TASK_LDA.md` / `docs/pm/RESULT_PACKET_LDA.md`(commitしない)。並行: 別 Sonnet 1 件(Part B=過去 STOP 事例・分類・QCD、出力先 `docs/pm/investigation_ledger_deviation_check_01_part_b.md`)→ 同ファイルに触れない。本タスクの出力先: `docs/pm/investigation_ledger_deviation_check_01_part_a.md`(新規)+delegation_log のみ。**Production code・Prompt・Checker threshold・SSOT 4 点・REPORT_LEDGER の変更禁止、Trial 開始禁止、E2E 再開禁止、API 呼び出し禁止(費用 ¥0)、Opus 起動禁止**。削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止。未追跡ファイルは他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。APIキー本文表示禁止。

## 背景(ユーザー問題意識、逐語要旨)

Hormuz 記事(`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01` run_02)で JA「料金案が消えたからといって、価格がそのまま大きく下がる展開にはなりませんでした。」→ EN "The disappearance of the fee plan did not lead to a large, lasting fall in prices." が EN 側 Deviation Check で `changed_causality` MAJOR(origin=ja_source、related HF-011)、JA 側 Fact Check は COMPLIANT。ユーザーは「JA 側が甘い」ではなく「**EN 側 Deviation Check が英語学習サービスとして厳しすぎる可能性が高い**」と見ている。eigo-radio はニュース報道機関ではなく英語学習サービス(嘘・低信ぴょう性・根拠なしを許容する意味ではない)。Production 量産には Quality / Cost / Delivery のバランスが必要。目的は「信頼性の最低ラインを守りながら、過剰品質になっている Check を見直し、量産性のある検証機構へ再設計できるかの調査」。**本委任は調査のみ。新 Checker 仕様・閾値・Prompt・判定ロジックを実装・提案採用しない**(設計素案は ChatGPT 側で作成、その後 Opus レビュー)。

## 調査項目(出力ファイルの章立てをこの順にする)

### 1. 現行 Ledger Check / Deviation Check の正確な役割整理
Repo・CURRENT_SPEC・DECISION_LOG(+`DECISION_LOG_HISTORY.md`)・OPEN_ITEMS(+`OPEN_ITEMS_HISTORY.md`)・各 REPORT・Production code を確認し整理:
- **Ledger Check(JA 側 Fact Check / Verified Fact Ledger 照合)**: 入力/検証内容/Ledger 各 field(fact_id, scope, conditions, numeric_value, numeric_scope, date_or_period, causal_strength, notes_for_writer 等)の意味/`notes_for_writer` の役割/COMPLIANT・MAJOR・MINOR の判定基準/実行段階(Original・must-fix・R1・R2 のどこ)/STOP 条件/retry・must-fix との関係/JA Writer O との関係/Production 量産上の目的。
- **Deviation Check(EN 側)**: 入力/検証内容/Ledger との関係/JA source・English translation・rewritten content のどこを見るか/10 category(changed_fact/scope/causality/certainty/number/actor/negation/comparison/time/unsupported_new_claim)/MAJOR・MINOR 基準/`auto_downgraded` の意味/STOP 条件/retry(must-fix 1 回)との関係/`origin=ja_source` の現在の扱い(`JARecheckRequiredError`)/Standard(A2)側の Deviation Check の有無と扱い/Production 量産上の目的。
- 冒頭に **「両者は何が同じで何が違うか」** をユーザーが理解できる言葉で(表+短文)。Prompt 本文は該当箇所を逐語引用(sha256 とファイル:行)。
- 主要ファイル(Grep 起点): `er003_v1_n3_01_verified_fact_ledger*.py`(`run_deviation_check|deviation_audit_record|notes_for_writer|changed_causality|auto_downgraded|MAJOR|MINOR|def run_fact_check|LEDGER_COMPLIANT`)、`er019_family_x_ja_writer_o_r1_r2_01.py`(`fact_check|must_fix|R1|R2|deviation`)、`er012_e_family_entertainment_two_level_runner_01.py:262-420,440-500`、`er003_v1_n3_01_advanced_adaptation_generate.py`(`build_must_fix_block|deviation`)、`er003_v1_n3_01_standard_a2_generate.py`(`must_fix|deviation`)、Family A/B/C の runner(`er012_b_*`/`er012_c_*`/`er012_d_*`)での同 Check の使われ方(差異があれば表)。

### 2. hard constraint / soft guidance の区別
特に `notes_for_writer`: 現在どの記述が hard constraint として扱われているか/どれが本来 writer guidance だったか/guidance 違反がなぜ MAJOR STOP になっているか/Code・Prompt・Validator のどこで hard 化されているか(ファイル:行、Prompt 逐語)/歴史的にいつ・なぜこの設計になったか(commit hash・Trial 管理ID・DECISION_LOG エントリまで遡る: `git log -S "notes_for_writer"`、`git log -S "changed_causality"`、`git log -S "origin"`/`ja_source`、`git log -S "JARecheckRequiredError"`、DECISION_LOG/HISTORY の Grep `Deviation|Ledger|notes_for_writer|ja_source|causal`)。Ledger 生成側(B3 fact selection、`NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01`)で `notes_for_writer` がどう生成・意図されているかも確認。

### 6. 信頼性の最低ライン(章番号はユーザー指定に合わせ 6)
既存仕様・過去議論から、eigo-radio が絶対に守ろうとしてきた Fact 品質を **抽出**(新規定義しない): invented fact 禁止/contradiction 禁止/数値改変禁止/actor・entity 誤認禁止/significant causality fabrication 禁止/source にない重大主張の追加禁止 等。各項目に根拠(CURRENT_SPEC 小節名・DECISION_LOG エントリ・commit)。

### 7. Hormuz 事例の trace
`er019_output/family_x_refresh_e2e_01/hormuz/run_02/`(`ledger/`、`ja_writer/`(original・fact_check・must_fix・revision1/2 の audit json)、`b1b/audit/deviation_checks/advanced_attempt1.json`)と run_01 の同等ファイルを読み、一本の trace として: Ledger 上の元 Fact(HF-009/HF-011 逐語)/notes_for_writer(逐語)/JA 生成文(段落と前後文)/JA Fact Check の判定(該当文に対する記載の有無、prompt の該当基準)/EN 生成文/EN Deviation Check 判定(逐語、10 flag)/なぜ `changed_causality` になったか(Prompt 上の該当ルールと notes_for_writer の関係)/JA 側が COMPLIANT とした理由(JA 側 Prompt に notes_for_writer 遵守が含まれるか、10 category があるか、`origin` 判定の有無)。run_01 の MAJOR(HF-006 燃料輸送費)も同様に短く trace。
その上で **「現行仕様で MAJOR になる理由」** と **「実際のユーザー理解・英語学習サービス上の実害がどの程度あり得るか」** を分けて記述。後者は断定せず Product 観点の論点として整理(例: JA 文は直後に「この値動きだけで理由を一つに決められない」と留保している、EN は "large, lasting" と限定している、等の観察を事実として列挙)。

## 出力ファイル `docs/pm/investigation_ledger_deviation_check_01_part_a.md`

- 章 1・2・6・7(上記)。各主張に根拠(ファイル:行/commit/管理ID)。推測は「推測」と明記、未確認は「未確認」。**採用提案・仕様決定・Production 変更提案を書かない**(論点整理まで)。ユーザー向け表記は Standard/Advanced(A2/B1B は内部名として併記可)。
- 末尾に「Part B(過去事例・分類・QCD)との統合は別委任」と明記。

## 固定ブロック

T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_01.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_01.md --json-out docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_01.md_check.json` を実行し結果1行記録。T-2: TTS なし。T-3: API 支出なし(¥0)。E-1/D-1/G-1/F-1 標準。

## 事前指定Read一覧 / 事前指定Grep一覧

- 上記「主要ファイル」の Grep パターン。`CURRENT_SPEC.md`: Grep `Verified Fact Ledger|Deviation Check|Fact Check|notes_for_writer|must-fix|ja_source|changed_causality`(該当小節のみ Read、全文読込禁止)。`DECISION_LOG.md`/`DECISION_LOG_HISTORY.md`/`OPEN_ITEMS.md`/`OPEN_ITEMS_HISTORY.md`: 同 Grep。REPORT: `Glob *LEDGER*_REPORT.md`, `*FACT*_REPORT.md`, `*DEVIATION*_REPORT.md`, `NEWS-FAMILY-X-B3-*_REPORT.md`, `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` §E2E。
- 更新位置: 出力ファイル(新規)、delegation_log のみ。

## 実行コマンド全文

- `git log --oneline -S "notes_for_writer" -- "er0*.py" | head -30`(同様に `changed_causality`、`ja_source`、`JARecheckRequiredError`)
- `git log --oneline -S "notes_for_writer" -- CURRENT_SPEC.md DECISION_LOG.md | head -20`

## Git

- add 対象(path 指定のみ): `docs/pm/investigation_ledger_deviation_check_01_part_a.md`、delegation_log+`_check.json`。メッセージ `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01: Part A(現行Ledger Check/Deviation Checkの役割整理・hard/soft区別・信頼性の最低ライン・Hormuz事例trace、read-only調査)`、trailer `Management-ID: LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01`。push。

## 報告(RESULT_PACKET_LDA + handback、目安35行)

章ごとの要点(両者の違い表の要約、hard 化箇所のファイル:行と由来 commit、最低ラインの抽出リスト、Hormuz trace の要点と「MAJOR になる理由」/「実害の論点」)/未確認事項/新たに見つかった重大問題(修正せず報告)/費用 ¥0/commit hash・raw URL。
