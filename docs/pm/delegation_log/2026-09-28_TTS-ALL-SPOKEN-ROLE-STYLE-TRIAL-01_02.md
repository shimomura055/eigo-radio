## 管理ID

TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01 の Trial記録の SSOT 反映(¥0、コード変更なし)。一時ファイル `docs/pm/ACTIVE_TASK_SSOT6.md` / `docs/pm/RESULT_PACKET_SSOT6.md`(commitしない)。**SSOT編集権: 本タスクのみ**(他Agentなし)。開始時・commit直前に `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md` で他差分なしを確認。

## 性質/到達上限Status/禁止事項

Trial記録(Fable判定 `USER_DECISION_REQUIRED`)。CURRENT_SPECへTrial仕様は追加しない。禁止: コード変更、`git add -A`、`stash`/`rebase`/`reset`/`amend`/`force push`(push競合時は `git merge origin/main` のみ、conflictなら中断報告)。E-1/D-1/G-1: 再読なし、Grep→範囲Read、git出力最小化。F-1: 退避不要。T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_02.md` へ保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_02.md --json-out docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_02.md_check.json`、結果1行記録。T-2: TTSなし。T-3: ¥0。

## 事前指定Read一覧

- `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_REPORT.md` 末尾「SSOT追記文案」節(Grep `SSOT追記` → 末尾まで)
- `OPEN_ITEMS.md`: 最終OPEN番号(Grep `OPEN-22`)、OPEN-201行

## 事前指定Grep一覧+追記位置・更新位置の手順

1. `docs/pm/REPORT_LEDGER.md` 新行: `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01 | Trial | USER_DECISION_REQUIRED(Fable判定、2026-09-28、試聴待ち) | TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_REPORT.md | commit e6d2a6cd / f1e23ce2 | Opus発火なし`(既存列構成に合わせる)。
2. `DECISION_LOG.md` 末尾: REPORT文案を逐語適用+Fable判定 `USER_DECISION_REQUIRED` と判断待ち論点(Trial限定のLock解除+"Two."/"Three."再生成[NUMBER_LABEL styleをProduction実証済み `FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]` へ差し替え]+Advanced結合/Advanced英語解説の前提維持[現状「英語句+日本語意味」、過去Trial `KEY-PHRASE-LEVEL-SPEC-TRIAL-01` REJECTED]/共有ログ混入のOPEN登録)、費用¥23.41、Production変更ゼロの証拠、Production採用未決。
3. `OPEN_ITEMS.md` 新規(次番号から、REPORT候補3件を逐語): (a) Advanced Key Phrase英語解説artifact不在(仕様前提の不一致、Product判断待ち)、(b) 極短context-free単語("Two."/"Three.")のFlash-Lite言語ドリフトがTrial styleでも再現(OPEN-201関連、style依存性の観測)、(c) Human Review Lock/attempt historyの共有固定pathがパラメータ化されておらずTrial分が混入した可能性(Trial隔離のパラメータ化要否)。OPEN-201行末尾へ「TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01でNUMBER_LABEL style時に同型ドリフト再現(CJK文字)、Production shell style(FALLBACK[0])では全件成功」を追記。

## Git

add対象: SSOT 4点(CURRENT_SPECは変更なしなら含めない)+delegation_log+`_check.json`。コミット: `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01: Trial記録をSSOTへ反映(USER_DECISION_REQUIRED、OPEN 3件)`、trailer `Management-ID: TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01`。`git push origin main`。

## 報告

適用箇所/新規OPEN番号/差分所有者確認/commit hash/raw URL(3 SSOT)。
