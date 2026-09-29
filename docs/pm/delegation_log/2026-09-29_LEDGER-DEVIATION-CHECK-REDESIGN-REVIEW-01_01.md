## 管理ID

LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01(Part A=Repo/実装整合・Prompt/Schema 変更の要否・deterministic rule 化・QCD・既存仕様との競合、委任 _01)。**read-only レビュー**。一時ファイル `docs/pm/ACTIVE_TASK_RRA.md` / `docs/pm/RESULT_PACKET_RRA.md`(commitしない)。並行: 別 Sonnet 1 件(Part B=Product/Fact Safety/事例適用/Trial 設計、出力先 `docs/pm/review_ledger_deviation_redesign_01_part_b.md`)→ 同ファイルに触れない。本タスク出力先: `docs/pm/review_ledger_deviation_redesign_01_part_a.md`(新規)+delegation_log のみ。**Production code・Prompt・Ledger schema・Checker severity・SSOT 4 点・REPORT_LEDGER の変更禁止、Trial 実行禁止、Family X E2E 再開禁止、API 呼び出し禁止(¥0)、Opus 起動禁止**。削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止。未追跡ファイルは他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。APIキー本文表示禁止。改善案の提示は可、**採用・実装はしない**。賛成ありきでなく批判的に。

## レビュー対象(ChatGPT 再設計素案、Status=PROPOSED/REVIEW)

目的: Checker の目的を「Ledger 逸脱の最大検出」から「英語学習教材としてユーザーの主要な Fact 理解を実質的に誤らせる重大事故を防ぐ」へ寄せる(嘘・根拠なし・信頼性軽視は許容しない。QCD バランスで量産可能に)。
- A. 「Deviation 検出」と「Production STOP」を分離: 検出 → 実害評価 → Severity 決定 → Action 決定。判断軸=「一般的な英語学習ユーザーがニュースの主要な事実関係を実質的に誤って理解する可能性があるか」。
- B. Severity 3 層: BLOCKING(数字改変/主体取り違え/対象取り違え/肯定否定反転/比較方向反転/時系列の重大変更/値動き方向の反転/根拠のない重要 Fact 追加/相関・同時発生を重大な因果として断定/元 Fact と逆の意味 → must-fix/STOP)、QUALITY(厳密には改善できるが主要 Fact 理解は変わらない → 通す+warning/log)、ACCEPTABLE(教材化・要約・自然化の合理的範囲 → 通過)。10 category は廃止せず、Category と Severity を分離。
- C. changed_causality を一律 BLOCKING にしない: Blocking causality(同時期 → 引き起こした、かつニュース理解の中心)と Non-blocking causal phrasing(観測事実の自然な文章化)を区別。Hormuz「料金案が消えたからといって〜」は自動 BLOCKING にしない候補。
- D. claim 単体でなく文脈: causality/certainty/unsupported_new_claim の境界事例は前後 1〜2 文の context window で最終 Severity。数字/actor/negation/comparison/time は単体判定のまま。
- E. notes_for_writer を soft guidance へ戻す: Ledger Fact(hard)と notes_for_writer(soft)を区別、notes_for_writer 違反だけでは BLOCKING にしない。将来 schema 分離 Trial を検討(今回は Production 変更しない)。
- F. JA 側=重大 Fact 事故を記事生成段階で除去/EN 側=翻訳・A2 simplification で意味が壊れていないか。EN で origin=ja_source でも一律即 STOP にせず Severity で Action。
- G. JA Original/JA R2/Advanced/Standard の最低 4 call を QCD で見直す(JA canonical で品質確保後、EN は translation-induced に重点化できないか。見逃し事例があるため確定はせず Trial 対象)。
- H. LLM 非決定性を前提に、LLM category 検出+deterministic post-processing で最終 Severity(例: actor changed+Ledger entity mismatch → BLOCKING/changed_causality+数値・entity・時間の矛盾なし+限定表現あり+直後 qualifier あり → QUALITY 候補)。
- I. Human Review は非常口(BLOCKING が must-fix retry 後も残る場合のみ)。QUALITY はログ蓄積。
- J. Disclaimer は残余リスク説明であり Checker 品質低下の理由にしない。
- 想定 Trial: 過去実例 fixture(重大/過剰品質/境界/見逃し)で Q(BLOCKING 維持率・見逃し率・不要 BLOCK 率)/C(call・retry・費用・HR 数)/D(latency・STOP 率・完成率)+同一入力反復で一致率。

## 調査済み事実(前提、`LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`、全文 Read 可)

JA Fact Check と EN Deviation Check は同一関数 `er003_v1_en_direct_vfl_01_generate.py::run_deviation_check()`(同一 Prompt `DEVIATION_PROMPT_TEMPLATE`・10 category・post-hoc `_apply_deviation_post_hoc_validation()` L544-561)。EN のみ `source_article_text` で origin 付加。`origin=ja_source` MAJOR は `er012_e_family_entertainment_two_level_runner_01.py:388-398,484-498` で `JARecheckRequiredError` 即 STOP。JA 側は `er019_family_x_ja_writer_o_r1_r2_01.py` で must-fix 1 回 → `JAFactCheckStopError`。notes_for_writer は `vfl01.py:157`(Researcher Prompt: 後工程が使わない)で soft 設計だが `vfl01.py:302-303` で Ledger テキストに同列埋込。auto_downgraded は実データ 0 件。Checker 中央値 ¥0.90/33 秒。Family A/B/C/Z の他 runner も vfl01 を共有。

## レビュー項目(出力ファイルの章立て)

### C. Repo / 実装整合(現行 Production code と照合、ファイル:行を必ず付ける)
1. 素案 A〜I それぞれについて「どこを変更すれば実現可能か」(vfl01 の Prompt/schema/post-hoc、er012_e の origin 分岐・exception、er019 JA Writer O の must-fix ループ、Family A/B/C/Z の共有呼び出し元)。
2. 現行 post-hoc validation(`_apply_deviation_post_hoc_validation`)をどこまで reuse できるか(現在何を機械固定しているか逐語で確認し、Severity 3 層化・deterministic rule の置き場として使えるか)。
3. Schema 変更の要否: deviation JSON schema(`severity`/`origin`/`auto_downgraded`/10 flag)に `severity_final`・`action`・`context_evidence`・`ledger_field_basis`(hard field か notes_for_writer か)等を追加する必要があるか、後方互換(既存 audit json・テスト・REPORT 集計)への影響。Ledger schema(`FACT_LEDGER_JSON_SCHEMA` L78-126)の notes_for_writer 分離(E)の影響範囲(Researcher/Verification Prompt、Ledger テキスト化、既存 Ledger 資産の互換)。
4. Prompt 変更の要否: 素案 A/C/D/E/F のうち Prompt 文言変更なしで(post-hoc・呼び出し側・Ledger テキスト化の変更だけで)実現できるものと、Prompt 変更が不可避なもの(例: context window 判定、Blocking/Non-blocking causality の区別、notes_for_writer 除外)を分ける。Prompt 変更は共有関数のため全 Family に波及する点を明記。
5. deterministic rule として実装できる部分(例: notes_for_writer のみを根拠とする deviation の降格=`explanation`/`related_fact_id` から機械判定可能か、`changed_number/actor/negation/comparison/time` の Ledger 値との機械照合可能性、限定語・qualifier の検出、origin=ja_source × severity の Action 表)と、LLM 判断に残すべき部分。各 rule の「現行 audit json から取れる入力」と「取れない入力(新 schema 必要)」を分ける。
6. retry / origin / exception 構造への影響: `JARecheckRequiredError`・`JAFactCheckStopError`・RuntimeError の 3 種を Severity×Action へ再編する場合の呼び出し側(er012_e、er019 runner、Family Z er026 の将来利用)の変更点、`--stage writer` 単独実行時の整合、must-fix ブロック(`build_must_fix_block`)が BLOCKING のみを対象にする場合の変更。
7. JA/Advanced/Standard の共有実装に drift を生まないための構造(単一 `classify_severity()` を vfl01 に置き、呼び出し側は Action 表のみ持つ等の選択肢を列挙、採用はしない)。
8. Family A/B/C/Z への波及: vfl01 を使う他 Family の runner(Grep `run_deviation_check(`)一覧と、Severity 3 層化が既存 Gate(REJECTED/VALIDATED 判定、REPORT 集計)へ与える影響。

### D. QCD
- 素案 G の call 削減余地: 現行 4 call の各役割(JA Original/R2/Advanced/Standard)と、削っても Q を維持できる可能性がある/削ってはいけない候補を、調査 REPORT の見逃し事例(A-1 時制ドリフト=Checker 2 回見逃し)と重複検出の実データ(同一 claim が JA と EN で二重検出された件数を audit json から集計、¥0)で裏付ける。
- latency/cost の削減可能性(reasoning=high の見直し・call 統合・Standard を translation-diff 限定にする等)は「可能性」として列挙、数値は実測がある範囲のみ。
- 二重・重複 Check の箇所(JA R2 と Advanced が同じ Ledger・ほぼ同じ内容を判定/Advanced と Standard の対称 Check)。

### 既存仕様との競合
- CURRENT_SPEC/DECISION_LOG(+HISTORY)/OPEN_ITEMS の Grep(`Deviation|Ledger|must-fix|ja_source|MAJOR|fail-closed|安全≠成功|Human Review`)で、素案と競合・矛盾する既存決定(例: ER-009-N1 recalibration の MAJOR 維持要件、「安全≠成功」原則、fail-closed 設計決定、JA Fact Check 配線決定 2026-09-27、Human Review Lock 仕様、OPEN-189)を列挙し、「素案採用時に SSOT 上どの決定を更新・撤回する必要があるか」を整理(決定はしない)。

### 再発防止(F)
- 過剰品質問題を再発させないための仕組みの置き場(仕様/Prompt/Validator/QA/運用/SSOT/Open Item)を、現行 repo の該当ファイル・既存機構(auto_downgraded、REPORT_LEDGER、OPEN_ITEMS、regression fixture)に即して列挙。

## 出力ファイル `docs/pm/review_ledger_deviation_redesign_01_part_a.md`

各主張に根拠(ファイル:行/commit/管理ID)。賛成ありきでなく、実装上の弱点・危険・不整合を明示。「新しい Product 判断が必要」な項目は明示的に印(★)を付ける。採用・実装はしない。

## 固定ブロック

T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_01.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_01.md --json-out docs/pm/delegation_log/2026-09-29_LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_01.md_check.json` を実行し結果1行記録。T-2: TTS なし。T-3: API 支出なし。E-1/D-1/G-1/F-1 標準。

## 事前指定Read一覧 / 事前指定Grep一覧

- `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`(全文)、`er003_v1_en_direct_vfl_01_generate.py`: Grep `DEVIATION_PROMPT_TEMPLATE|_apply_deviation_post_hoc_validation|DEVIATION_JSON_SCHEMA|FACT_LEDGER_JSON_SCHEMA|notes_for_writer|def run_deviation_check|auto_downgraded|def deviation_audit_record|origin`、`er012_e_family_entertainment_two_level_runner_01.py:262-500`、`er019_family_x_ja_writer_o_r1_r2_01.py`: Grep `fact_check|must_fix|JAFactCheckStopError`、`Grep -l "run_deviation_check(" er0*.py`(呼び出し元一覧)、SSOT は Grep 該当箇所のみ。
- 更新位置: 出力ファイル(新規)、delegation_log。

## 実行コマンド全文

- `git pull --ff-only origin main`
- 重複検出集計は scratchpad のスクリプト(repo に追加しない)

## Git

- add 対象(path 指定のみ): 出力ファイル、delegation_log+`_check.json`。メッセージ `LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01: Part A(Repo/実装整合・Prompt/Schema要否・deterministic rule化・QCD・既存仕様競合のレビュー、read-only)`、trailer `Management-ID: LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01`。push。

## 報告(RESULT_PACKET_RRA + handback、目安40行)

【Repo / 実装整合】【Prompt変更の必要性】【Schema変更の必要性】【deterministic rule化できる部分】【LLM判断に残す部分】【QCD評価】【既存仕様との競合】【再発防止】【★新しい Product 判断が必要な事項】の各見出しで 3〜6 行の要点(Fable が正式報告へ転記)/commit hash・raw URL。
