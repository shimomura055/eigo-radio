## 管理ID

FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(Phase B' / W6=ja_source MAJOR への暫定対応「案B」の Production 配線+SSOT 反映(案B 採用、Checker 再設計の deferred Open Item 化)、委任 _11)。一時ファイル `docs/pm/ACTIVE_TASK_RF6.md` / `docs/pm/RESULT_PACKET_RF6.md`(commitしない)。並行 Agent なし(`git pull --ff-only origin main`、HEAD `2c4f5ed3` 以降)。**SSOT 4 点(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)+REPORT_LEDGER は本タスクが編集権を持つ(直列化)**。削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止。未追跡ファイルは他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。APIキー本文表示禁止。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー明示決定(2026-09-29)「案B を採用、`APPROVED_FOR_PRODUCTION` として扱ってよい。ただし Gate 3 を満たすまで `PRODUCTION_WIRED` としない」の Production 配線。**暫定的な Production retry 拡張**であり Checker 過剰品質問題の正式解決ではない。到達上限 Status: `APPROVED_FOR_PRODUCTION`(配線済み・Gate 3 待ち)。
- **案B 暫定 Flow(逐語)**: EN Deviation Check で `origin=ja_source MAJOR` が出た場合: 1. その具体的な指摘を JA Writer O へ must-fix として差し戻す/2. JA を 1 回だけ再生成/3. 再 Fact Check/4. 再英訳/5. 再 Deviation Check/6. それでも MAJOR なら STOP。制約(逐語): 「1 回上限」「fail-closed 維持」「無限 retry 禁止」「Checker Prompt 自体は今回変更しない」「Ledger / Deviation severity 設計も変更しない」。
- 費用: **上限¥0**(mock/regression のみ)。
- 禁止: `DEVIATION_PROMPT_TEMPLATE`・severity・post-hoc validation・Ledger schema・JA Writer Prompt 本文の変更(既存 must-fix ブロック機構の再利用は可)、Family A/B/C/Z 経路の変更、共有 `vfl01` の挙動変更、W1〜W5 の承認済み配線の変更、`--stage all`。ユーザー向け表記 Standard/Advanced。
- STOP 条件: 新 Product 判断・未承認 Prompt 変更が必要になった場合のみ。

## 固定ブロック

E-1/D-1/G-1/F-1 標準。T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_11.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_11.md --json-out docs/pm/delegation_log/2026-09-29_FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_11.md_check.json` を実行し結果 1 行記録。T-2: TTS なし。T-3: API 支出なし。

## 実装

### A. 案B の配線(設計判断は最小・記録付き)
1. **現状把握**: JA 生成は `er019_family_x_entertainment_production_runner_01.py` → `er019_family_x_ja_writer_o_r1_r2_01.py`(Original → Fact Check → must-fix 1 回 → R1 → R2 → Fact Check、`JAFactCheckStopError`)、EN は `er012_e_family_entertainment_two_level_runner_01.py::run_writer_stage()`(Advanced/Standard Deviation Check、`JARecheckRequiredError` at :388-398/:484-498)。E2E run_02 の実行手順(REPORT §E2E 再開)で 2 runner をどう呼んだかを確認し、**案B のループを 1 箇所に置く**(候補: (i) er012_e の writer stage が `JARecheckRequiredError` を捕捉し、JA Writer O の must-fix 再生成関数を import して JA を再生成 → EN を再実行、(ii) er019 production runner の orchestration 層で 2 runner を包む。どちらかを選び、理由を設計書 §9-W6 に記録。共有 `vfl01` には触れない)。
2. **must-fix の受け渡し**: `JARecheckRequiredError.major_deviations`(claim_in_article・issue・explanation・related_fact_id、日本語)を JA Writer O の既存 must-fix ブロック形式へ変換(既存 `build_must_fix_block` 相当の JA 側機構を再利用。**新しい Prompt 文言を作らない**。JA 側 must-fix が英語 claim を受け取る場合は「EN 訳文の該当箇所」+「issue/explanation(日本語)」+「related_fact_id」を既存フィールドにそのまま入れる)。
3. **1 回上限・fail-closed**: JA 再生成(Original must-fix → R1 → R2 → Fact Check)→ 再英訳(Advanced)→ 再 Deviation Check → Standard → Deviation Check の全体を **1 回**だけ。Standard 段で ja_source MAJOR が出た場合も同じ 1 回枠を消費(Advanced/Standard 合計で JA 再生成は 1 回)。再実行後も ja_source MAJOR なら `JARecheckRequiredError`(reason に `ja_recheck_attempts=1` を含める)で STOP。translation 由来 MAJOR の既存 must-fix retry 1 回は不変。JA 再 Fact Check で `JAFactCheckStopError` なら即 STOP。
4. **Audit**: `ja_writer/audit/ja_recheck_attempt1.json`(差し戻した deviations・must-fix ブロック・再生成結果・Fact Check 結果)、`b1b/audit/deviation_checks/advanced_attempt1_after_ja_recheck.json` 等、既存命名規則に合わせて保存。`entry_point.json`/REPORT 用サマリに `ja_recheck_used: true/false`・回数・費用を記録。run_02 の artifact は上書きしない(run_03 で使用)。
5. **JA 再生成後の下流整合**: JA が変わると japanese_title/preview/comment/KP の JA 入力・3 分割・article.md sha256 が変わる。writer 段の出力(article.md、parts、provenance)が再生成後の JA・EN を指すこと、旧 JA 由来の中間物が残らないこと(cache guard: W3/W5 の text guard が効く)をテストで確認。

### B. テスト
新規 `er019_family_x_ja_recheck_retry_01_test_01.py`(mock): ja_source MAJOR → JA must-fix 差し戻し → 再生成 1 回 → COMPLIANT で完走/再実行後も MAJOR → STOP(2 回目の JA 再生成が呼ばれない=無限 retry 禁止の証明)/Standard 段で発生しても 1 回枠共有/translation MAJOR の既存 retry は不変/JA Fact Check STOP の伝播/Checker Prompt・severity 定数の sha256 が変更前後で不変/audit ファイルの存在と内容。regression: `run_project_regression.py --pattern "er019*_test_*.py"`、`"er012*_test_*.py"`、`"er003*_test_*.py"`(pre-existing 4 件は根拠付き非起因)、`"er009*_test_*.py"`(Checker fixture 回帰、該当時)。

### C. SSOT 反映(決定の逐語記録、`PRODUCTION_WIRED` と書かない)
1. **DECISION_LOG** 新エントリ(2026-09-29): (a) 「Checker 再設計は一旦 defer。理由: GPT-6 系への移行可能性が高く、モデル変更により過剰 BLOCK 傾向・非決定性・changed_causality 判定・notes_for_writer の扱い・重大 fixture 検出率自体が変わる可能性があるため。順序: Family X E2E 完了 → GPT-6 Trial / Routing 判断 → 必要な Production 導入 → 新モデル前提で Checker 問題を再評価。再設計案は破棄せず deferred / non-blocking Open Item として保持。現時点で VALIDATED / APPROVED_FOR_PRODUCTION ではない」(b) 「ja_source MAJOR への暫定対応として案B を採用(上記 Flow 逐語+制約逐語)。ユーザー明示決定により APPROVED_FOR_PRODUCTION。Gate 3 まで PRODUCTION_WIRED としない。Checker 過剰品質問題の正式解決ではない」(c) 優先順位「① 案B で Family X E2E 完了 ② Gate 3 / PRODUCTION_WIRED 判定 ③ GPT-6 Trial / 導入判断 ④ 新モデル前提で Checker 品質問題へ戻る」。
2. **OPEN_ITEMS** 新規 OPEN(番号=既存最大+1、Status `DEFERRED (non-blocking)`): テーマ「Ledger / Deviation Check の過剰品質・非決定性・QCD 再設計」/再開タイミング「GPT-6 Trial / Production Routing 判断後」/再利用する Evidence: Hormuz B-1、Hormuz B-2、B-3 / B-4、A-1〜A-5 重大事例、notes_for_writer 調査(12/12 factual constraint)、origin 付き 15 件分類、Checker コスト・latency(中央値 ¥0.90/33 秒)、非決定性調査、ChatGPT redesign v0.1、Claude review 結果(各 REPORT・docs/pm ファイルのパスと commit を明記: `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md` 247e0a1f、`LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_REPORT.md` 2c4f5ed3、part_a/part_b 各 2 件)/再開時に再評価するもの: 不要 BLOCK 率、重大 fixture 検出率、同一 input の一致率、notes_for_writer の扱い、changed_causality severity、JA / EN 重複 Check、Checker call 数、retry / STOP 率、QCD/GPT-6 Trial の基本方針「新旧モデルを同一入力・同一 Prompt・同一 Validator 条件で比較。Checker は今回の Evidence(重大 A 群・過剰品質 B 群・Hormuz B-2・changed_causality・notes_for_writer・非決定性)をそのまま比較可能な状態にする」。前回 E2E 委任で文案化した「Deviation Check 非決定性」OPEN 候補はこの OPEN に統合(別番号を立てない)。
3. **CURRENT_SPEC**: Family X writer 経路の小節に「ja_source MAJOR 時の暫定 retry 拡張(案B、1 回上限、fail-closed、APPROVED_FOR_PRODUCTION・Gate 3 待ち、Checker Prompt/severity 不変)」を追記。fail-closed 記述(「安全≠成功」・origin=ja_source 即 STOP)は「JA 差し戻し 1 回後も MAJOR なら STOP」へ整合させる(原則は維持)。
4. **REPORT_LEDGER**: `LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`(調査完了)と `LEDGER-DEVIATION-CHECK-REDESIGN-REVIEW-01_REPORT.md`(PROPOSED/REVIEW、deferred)を登録。
5. `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` §W6 追記(設計判断・変更箇所・テスト・SSOT 更新箇所)、設計書 §9-W6。

## 事前指定Read一覧 / 事前指定Grep一覧

- `er012_e_family_entertainment_two_level_runner_01.py:262-500`、`er019_family_x_ja_writer_o_r1_r2_01.py`: Grep `must_fix|fact_check|JAFactCheckStopError|def run_|R1|R2|build_must_fix`、`er019_family_x_entertainment_production_runner_01.py`: Grep `ja_writer|run_writer_stage|def main|--stage`、REPORT `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md` §E2E(run_02 の実行手順・コマンド)、`CURRENT_SPEC.md` Grep `ja_source|fail-closed|安全≠成功|JARecheck|Family X.*writer`、`OPEN_ITEMS.md` Grep `OPEN-2[0-9][0-9]`(最大番号)、`DECISION_LOG.md` 先頭ヘッダーチェーン。
- 更新位置: 上記コード 1〜2 ファイル+新規テスト、REPORT、設計書、SSOT 3 点+REPORT_LEDGER、delegation_log。

## 実行コマンド全文

- `git pull --ff-only origin main`
- `.venv\Scripts\python.exe -m unittest er019_family_x_ja_recheck_retry_01_test_01 -v`
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er019*_test_*.py"`(同様に er012/er003/er009)
- `git diff --stat HEAD`

## Git

- commit 2 つ: (1) コード+テスト+REPORT+設計書+delegation_log `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 (W6): ja_source MAJOR時のJA must-fix差し戻し1回(案B、fail-closed、Checker Prompt/severity不変)をFamily X writer経路へ配線`;(2) SSOT 3 点+REPORT_LEDGER `FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01: SSOT反映(案B=APPROVED_FOR_PRODUCTION・Gate 3待ち、Checker再設計をdeferred non-blocking Open Item化、優先順位①〜④、REPORT_LEDGER登録)`。trailer `Management-ID: FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01`、path 指定 add、push。

## 報告(RESULT_PACKET_RF6 + handback、目安35行)

配線位置と理由/must-fix 受け渡しの形式(新 Prompt 文言なしの証明)/1 回上限・fail-closed のテスト証拠/Checker Prompt・severity sha256 不変/regression 結果/SSOT 更新箇所(OPEN 番号)/E2E run_03 の実行手順(run_02 との差分: 案B 有効化に必要な引数があれば逐語)/費用 ¥0/commit hash 2 件・raw URL/STOP 有無。
