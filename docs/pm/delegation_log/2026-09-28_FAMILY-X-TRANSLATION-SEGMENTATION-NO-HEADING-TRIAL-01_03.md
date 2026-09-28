## 管理ID

FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01(SSOT反映のみ、委任 _03)。一時ファイル `docs/pm/RESULT_PACKET_NH1S.md`(commitしない)。並行Agentなし。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。自タスクの所有ファイル(SSOT 3点+REPORT_LEDGER+delegation_log)以外に触れない。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断報告。

## 性質/到達上限Status/禁止事項

- 性質: SSOT反映(記録のみ)。コード・Prompt・CURRENT_SPEC・PM_GOVERNANCE は変更しない。API支出なし(上限¥0)。
- **SSOT編集権: あり**(`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`)。現在 SSOT 編集権を持つ Agent は本タスクのみ。差分所有者確認: 開始時と commit 直前に `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md` で本タスク以外の差分ゼロを記録(他Agent差分があれば add せずSTOP)。
- 禁止: `VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED` と書かない(Status `USER_DECISION_REQUIRED`[Fable判定])。採否を決めない。OPEN-228 の修正に言及する場合も「ユーザー決定の順序に従う」と記載。APIキー本文表示禁止。DECISION_LOG.md は CRLF(Edit 失敗時は Python で CRLF 明示追記)。

## 固定ブロック

E-1/D-1/G-1/F-1 標準(SSOT 全文Read禁止)。T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_03.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_03.md --json-out docs/pm/delegation_log/2026-09-28_FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_03.md_check.json` を実行し結果1行記録。T-2: TTSなし。T-3: API支出なし。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_NH1B.md`(修正1回目の SSOT 文案)、`docs/pm/RESULT_PACKET_NH1.md`(初回文案)
- `FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_REPORT.md`: Grep `LEDGER_|In One Line|語数|must-fix|Cost|費用` → 該当範囲

## 事前指定Grep一覧+追記位置・更新位置の手順

- `docs/pm/REPORT_LEDGER.md`: Grep `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01` → 直後に新行。
- `DECISION_LOG.md`: Grep `PM-USER-DECISIONS-2026-09-28-CONSOLIDATION-SSOT-02` → 末尾に新エントリ。
- `OPEN_ITEMS.md`: Grep `OPEN-228|OPEN-229` → OPEN-228 本体行追記、末尾番号確認のうえ新規 OPEN-230。

## 反映内容(Fable確認済み事実)

commit `88b7e7de`(初回)/`9fc0c77a`(修正1回目)、push済み。重複確認=既存・進行中なし(新規 Trial)。入力=AN3-T0 の JA 完成記事(Hormuz/Meta)、Baseline=現行 Advanced(見出しあり)、Trial=見出し生成指示を除いた忠実英訳(既存語彙ルール流用、Trial 限定 Prompt)+段落境界のみで決定論的 3 分割+既存 Comment 1〜4 reuse+短い In One Line。結果: Hormuz Trial `LEDGER_COMPLIANT`(段落 8=8、分割 37.6/35.3/27.1%)。Meta Trial v1 は MAJOR 1(「元に戻した」を "put back the feature" と意味反転)→ Production 同等の must-fix retry 1 回(既存 `build_must_fix_block` 流用)で v2 `LEDGER_COMPLIANT`(段落 10=10、分割 37.6/31.5/30.9%)。In One Line: v1 は Baseline より長化(Hormuz 20→27 語、Meta 14→28 語)→ ユーザー仕様(短い自然な一文/論点を詰め込まない)を Trial Prompt に明示した v2 で各 18 語(参考ガイド 12〜18 語は Trial 限定)。rubric(14 項目): 忠実性・Fact・順序・新規 Fact 0 で Trial 優位、読みやすさ・聞きやすさ・Entertainment 性で Baseline 優位(5 対 4)、Comment 接続は Trial 優位、見出し廃止による単調化は著しくなし(4/5)、一部再評価ノイズあり。費用 約 ¥13.3(初回 ¥9.2[破棄 run ¥4.1 含む]+修正 ¥4.1)。Regression 19/19。Production 無変更、OPEN-228 未修正(ユーザー決定の順序に従う)。Existing Spec: 音声構造は既存と一致、見出し基準の本文 1/2/3 定義と Section Segmentation Contract(PRODUCTION_WIRED)は本 Trial が置き換える対象(無変更で残置)。公開: HTTP 200、初回は headless Edge で DOM 確認、修正回は fetch 確認のみ(text ページ)。Opus 発火なし。Fable 判定 `USER_DECISION_REQUIRED`(試読で採否)。試読: https://shimomura055.github.io/eigo-radio/user_test/no_heading_trial_01/index.html

1. `docs/pm/REPORT_LEDGER.md`: 新行(Status `USER_DECISION_REQUIRED`[Fable判定]、commit 2 件、Opus発火なし、REPORT名)。
2. `DECISION_LOG.md` 末尾に1エントリ `FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01: Trial記録(2026-09-28)`: 上記を簡潔に。「採用の場合の次段=新構造に合わせて split/Gate/retry 整理(OPEN-228 の前提不要化を含む)→ AN3-T0 Production Wiring 完了、の順(ユーザー決定)」「Production 採用はユーザーのみが判断」を明記。
3. `OPEN_ITEMS.md`: OPEN-228 本体行へ「2026-09-28追記: NO-HEADING-TRIAL-01 で見出しなし構成が Deviation Check を通過(Hormuz 初回/Meta must-fix 後)。採用判断後に『導入部 2 段落以上』前提の不要化を含む split/Gate/retry 整理を別管理IDで実施(単独修正はしない)」。新規 **OPEN-230**「忠実英訳方式は Fact 精度を自動保証しない(NO-HEADING-TRIAL-01 Meta v1 で MAJOR 1、Production 同等 must-fix retry 1 回で解消)。新構造を Production 化する場合は must-fix retry を必須要件とする。`OPEN`(採用判断待ち)」。

## 実行コマンド全文

- `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_03.md --json-out docs/pm/delegation_log/2026-09-28_FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_03.md_check.json`
- `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md`(2回)

## SSOT追記文

上記「反映内容」のとおり。

## Git

- add対象(path指定のみ): `DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`、delegation_log+`_check.json`。
- メッセージ: `FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01: Trial記録をSSOTへ反映(USER_DECISION_REQUIRED、OPEN-228追記、OPEN-230新設)`、trailer `Management-ID: FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01`。`git push origin main`。

## 報告(handback、目安15行)

適用箇所/T-0結果/差分所有者確認2回/未実施の禁止操作/commit hash・push結果/raw URL(3ファイル)/注意点。
