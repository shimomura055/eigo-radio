# 委任文全文(2026-09-28、_03、SSOT反映・修正2回目扱い)

管理ID: KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01(SSOT反映、修正2回目扱い)+ PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01(OPEN_ITEMS反映)。**¥0・API呼び出しなし・コード変更なし**。一時ファイル `docs/pm/ACTIVE_TASK_KPS1.md` / `docs/pm/RESULT_PACKET_KPS1.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-28_KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01_03.md` に保存しcommitに含める。

## 背景
先行Agent(KPC2、commit `9fa6f388`)は、SSOT 4点に別Agent(Flash-Lite -02)の未commit差分があったためSSOT編集を見送り、逐語の追記案を `docs/pm/RESULT_PACKET_KPC2.md` に用意した。Flash-Lite -02は commit `ccd7070e` でSSOTをcommit済みなので、今回適用する。

## やること
1. `git status` でSSOT 4点(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`)の未commit差分を確認。差分があれば別Agent(ASR包括対策 `EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02` 等)が編集中の可能性がある。最大10分待機し、解消しなければ**その差分に触れず**、自分の追記だけを行い、`git add -p`相当ではなく、自分の追記行だけを含む形でcommitできるかを慎重に判断する。混在が避けられない場合はcommitせずRESULT_PACKETへ状況を記録してSTOP(他Agentの差分をcommit/unstageしない)。
2. `docs/pm/RESULT_PACKET_KPC2.md` の「SSOT記載案」1〜4を**逐語**で適用(CURRENT_SPEC Key Phrase節、DECISION_LOG新規エントリ、OPEN-202追記、REPORT_LEDGER行更新)。挿入位置が記載どおりに見つからない場合は最も近い等価位置に入れ、差異をRESULT_PACKETへ記録。
3. `docs/pm/RESULT_PACKET_PRN9.md` の OPEN_ITEMS 記載案(OPEN-207追記+新規OPEN-208)を逐語適用。番号衝突(Flash-Lite -02が新OPEN番号を採番した可能性あり)があれば次の空き番号へ振り直し、参照箇所を整合させ、RESULT_PACKETに記録。
4. 新規OPEN項目を1件登録(Fable方針、Production変更を含まないPM追跡項目): 「`run_project_regression.py` の `DEFAULT_PATTERNS`(`er0*_test_*.py`)が末尾 `_NN_test.py` 形式(29モジュール、Production中核test含む)を収集しない既存gap、およびtest修正が実装切替に追随せずmockが空振りする mock-drift 構造リスクの恒久対策(検討・実装は別管理IDでユーザー判断後)」。Status `OPEN`、根拠 `KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01_REPORT.md` §11-4。
5. 適用後、KPC2 REPORT §11 のGate 3表の「SSOT反映」行を「済(修正2回目、commit hash)」へ更新。`PRODUCTION_WIRED` は宣言しない(Fable判定)。
6. Git: 変更ファイルをpath指定add(`git add -A`禁止)、トレーラー `Management-ID: KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01`、push origin main。`.env`/`ACTIVE_TASK*`/`RESULT_PACKET*`はcommitしない。履歴書き換え禁止。index.lock競合時はretry。

RESULT_PACKETに: 適用箇所一覧(ファイル・見出し)、番号振り直しの有無、待機した場合の時間と結果、commit hash、raw URL(4 SSOT+REPORT)。

---

## 実施時の特記事項(Sonnet実行ログからの要約)

着手時、`CURRENT_SPEC.md`/`OPEN_ITEMS.md`に`EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02`の未commit差分(各1行、OPEN-186/該当行)を検知した。`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`には差分なし。差分行と自分の挿入位置が十分離れており(CURRENT_SPEC.md: 他Agent行1631 vs 自分の挿入行1500、OPEN_ITEMS.md: 他Agent行367 vs 自分の挿入行384/389-390)、単一行差し替えのみだったため、待機せず編集を開始した。

編集中、`EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02`側が`git commit`を実行し(commit`3d9a28be`、push済み)、その時点で作業ツリーにあった自分の`CURRENT_SPEC.md`編集(Source Reference Contract行への追記)と`DECISION_LOG.md`新規エントリ(86行)が、意図せず同コミットへ混入した(相手側の`git add`操作がbroadだったため)。`OPEN_ITEMS.md`・`docs/pm/REPORT_LEDGER.md`・REPORT.mdへの自分の編集はこのコミットに含まれず、作業ツリーに残った。

混入した内容自体は正しい(委任文の逐語案どおり)ため、破壊的なgit操作(revert/reset)による「訂正」は行わず、残りの編集(OPEN_ITEMS.md/DECISION_LOG.mdの小修正/REPORT_LEDGER.md/REPORT.md)を通常どおりpath指定でcommitした。詳細は`docs/pm/RESULT_PACKET_KPS1.md`(一時ファイル、commitしない)参照。
