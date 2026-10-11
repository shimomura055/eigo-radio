# FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_07(統合→Regression→実fallback probe→Phase 2→試聴ページ)
- 日付: 2026-10-11 / 実行層: Sonnet / worktree `C:\Users\tensh\eigo-radio-tone` branch `feature/coffee-new-tone-01`
- Step1: `feature/coffee-new-tone-fallback-01` を `--no-ff` merge(conflictなし、merge commit fc3b3ebd)。Regression collected=5474 passed=5336 failed=17 errors=75 skipped=38(baseline 02 5400/5262/17/75/38 に対し collected/passed とも +74=46+28、failed/errors/skipped不変=新規fail 0)。tracked telemetry 4ファイルは`git checkout --`で復元。別worktree `eigo-radio-tone-fb` は初回Permission denied後、再試行で除去済み(branchは残存)。
- Step2: 実fallback probe 8呼出 (a)(b)(c)全PASS、費用 JPY 1.37。証跡 `FALLBACK_REAL_PROBE_01.md`。
- Step3: entertainment(EN/RF/Queue) JPY 2.93 + audio JPY 16.43、累計 JPY 20.73/50。Advanced完成。Standardは full_story_part2 が Human Review(承認は人間のみ)。詳細 `RUNTIME_EVIDENCE_01.md`。worktreeのMaster Store音声欠落を主ツリーから復元(worktree限定)。
- Step4: `user_test/coffee_new_tone_01/`、Playwright実再生PASS(ローカルRange対応server)。GitHub PagesはmainへmergeするまでURL未公開。詳細 `PLAY_EVIDENCE_01.md`。
- 非commit: `er019_output/coffee_prices/run_e_tone_01/`(builder再構成可)、wav、`_test_scratch/`。SSOT/mainは不変。
