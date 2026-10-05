# 委任_B 受領記録(OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01、2026-10-06)

管理ID: OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01(委任_B: 実装不具合修正「T最終削除処理が同cycleでRewrite成功済みの対象を再対象化→位置特定不能→誤ってHuman Review(STAGE4)」)。委任_A(再分類Trial)は並行(本委任はAのファイルを読まない・addしない)。

## 性質/到達上限Status/禁止事項
- 性質: 既存仕様(設計doc I-2/T)への整合修正=実装不具合修正。新Product判断ではない。到達上限: 修正・test・記録まで(Trial runner、Production正式path不変、`APPROVED_FOR_PRODUCTION`ではない)。
- 禁止: Stage 1/Stage 2構成・prompt・gold・Safety-critical定義・floor語彙の変更/有料API実行(¥0)/E2E再開/Human Review基準の緩和(fail-closed維持)/`git add -A`・stash・amend/`ACTIVE_TASK.md`・`RESULT_PACKET.md`のadd。
- 費用: ¥0。T-3のCap定型文は適用対象外。
- Opus独立技術レビューGate(11-3): 非該当(原因明確な実装不具合、構造不変)。ただし新しい遷移先・新Statusが必要と判明した部分は未実装でRESULT_PACKETへ設計案を記載しSTOP。

## ユーザー指示(原文)
> 3. 実装不具合は並行して修正する
> 以下の既知バグは、Checker設計とは別問題として並行修正する。
> 一度Rewrite済みの文を、同じ処理内で再び削除対象にしてしまい、既に文が変わっているため位置を見失い、誤ってHuman Reviewへ送る不具合。
> これは新Product仕様の判断事項ではなく、明確な実装不具合なのでユーザー判断待ちにしない。
> 期待動作：
> - 同一cycleでRewrite成功済みの対象を、最終削除処理で再対象化しない
> - Human Reviewへ送る前に、本当に構造上修正不能なのかを確認する
> - 非構造的な位置特定失敗を「構造上修正不能」と誤分類しない
> - regression testを追加する
> - retry / fallback / regenerationでも同種不具合が起きないことを確認する
> この種の明確な実装バグは、今後もまず修正・testしてから報告すること。新しいProduct判断が必要な場合のみSTOPする。
> 4. 実装不具合修正は既存仕様への整合修正なので、修正・test・必要な記録まで進めてよい。
> 2. Safety基準をTrial都合で緩和しないこと。

## 修正方針
(1) T対象選定で同cycleのRewrite成功済み/carry-forward済みclaimを除外(`t_skipped_reason=already_rewritten_in_cycle`)。(2) `_t_fail`→`blocking_structural_after_ladder`写像の前に検証。非構造の位置特定失敗は既存ラベル体系内でfail-closed、新遷移先なし。(3) regression test追加(neg7再現・真の構造枯渇・本文に残る未解消のfail-closed・retry/fallback/regen参照)。(4) `run_project_regression.py --pattern "er052*_test_*.py"`を1回。(5) T-0。(6) 修正前に再現FAIL→修正後PASSを両方記録。

## Git
明示add対象のみ(runner、テスト、OPEN_ITEMS.md、DECISION_LOG.md、docs/pm/REPORT_LEDGER.md、OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md、本ファイル+_check.json)。ACTIVE_TASK.md・RESULT_PACKET.md・委任_Aのファイルはaddしない。
