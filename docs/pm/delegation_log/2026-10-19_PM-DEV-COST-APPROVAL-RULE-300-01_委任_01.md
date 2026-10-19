# 委任文(Fable→sonnet-worker)

## 管理ID
PM-DEV-COST-APPROVAL-RULE-300-01 委任_01(ユーザー2026-10-19指示原文保存+開発費承認ルール改訂「見積100円超→300円超で事前承認」の全文書・全Agent整合、旧ルール撤去、判定テスト、SSOT反映。**文書・運用ルール改訂のみ、JPY0、Production runtime/コード/Prompt/Gate不変**)。日付: 2026-10-19(JST)。

## 性質・到達上限Status・禁止事項
- 性質: 文書・Agent指示の改訂+判定テスト。有料API呼出0。Production仕様・記事生成Prompt・TTS仕様・品質Gateのコードは変更しない。
- 到達上限Status: `COST_RULE_300_DOCS_ALIGNED_TESTED_PENDING_FABLE`(Fableが独立照合後にCLOSE判定)。
- 禁止: 金額以外の安全・承認・STOPルール(個別Cap・日次1,000円・Production承認Gate・STOPセンチネル・HR Lock・未承認仕様の隔離)の緩和/「追記のみ」で旧100円基準を残すこと/過剰な新規Validator・承認工程の増設(既存機構の改訂+小さな判定テストに留める)/ユーザー原文の要約保存。
- 固定ブロック: **E-1**(既存仕様照合: PM_GOVERNANCE 7-6/7-7/7-9/11節(自明な修正・STOP条件)/29節(Charter明確化判定表)、CLAUDE.md共通Charter第2・第6原則と「安全・承認境界」の予算文、PM_BRIEF「予算Cap」節、`.claude/agents/{sandwich-pm,sonnet-worker,opus-consultant,haiku-worker}.md`、`docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`・F-1ブロック、`docs/pm/tools/check_charter_references_01.py`、既存の費用管理ツール(daily_dev_cost等)をGrepし、「100円」基準の参照箇所を全件列挙してから改訂)/**D-1**(不適用)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。**並行agentあり(FAMILY-X-B3-FACT-MIN2-PRODUCTION-01 委任_01、OPEN_ITEMS/DECISION_LOG/USER_DECISION_REGISTER/REPORT_LEDGER/ACTIVE_TASKを編集・commit予定)**: 共有SSOT5ファイル(OPEN_ITEMS.md/DECISION_LOG.md/docs/pm/USER_DECISION_REGISTER_01.md/docs/pm/REPORT_LEDGER.md/docs/pm/ACTIVE_TASK.md)の編集は作業の最後に回し、`git log --oneline -8`に`FAMILY-X-B3-FACT-MIN2-PRODUCTION-01 委任_01`のcommitが現れるまで編集しない(60秒間隔で最大20回確認。現れなければ共有SSOT5ファイルは編集せずcommit 1[非共有ファイル]のみで報告し、未反映分をRESULT_PACKETに明記)。共有SSOTは自分の変更行のみ(編集直前に再読)、`.git/index.lock`があれば待ち再試行、non-ffは`pull --ff-only`後再試行、conflictはSTOP。commitは2回に分けてよい: commit 1=非共有ファイル(CLAUDE.md/PM_GOVERNANCE/PM_BRIEF/agents/templates/tools/delegation_log)、commit 2=共有SSOT5ファイル)/**F-1**(JPY0)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_PM-DEV-COST-APPROVAL-RULE-300-01_委任_01.md`へ保存し`check_delegation_prompt.py`実行。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_COST300_1.md`)。

## ユーザー指示原文(2026-10-19、逐語。`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_PM-DEV-COST-APPROVAL-RULE-300-01_USER.md`へ以下「# Claude Code／Fableへの正式指示」から「単なる文書追記では完了としない。**」までを原文のまま(1文字も変えず)保存し、文字数とsha256を報告)

# Claude Code／Fableへの正式指示
## 開発費承認ルール改訂・既存PM Governanceとの整合

### 1. ユーザー正式決定

開発費の承認ルールを以下に変更する。

**Status：APPROVED_FOR_PRODUCTION（運用ルールとして正式採用、文書・Agent反映待ち）**

| 条件 | 承認ルール |
|---|---|
| 日次開発予算 | 原則1,000円／日（JST） |
| 承認済みScope内・案件見積300円以下 | AIが自律判断。個別費用承認不要 |
| 案件見積300円超 | ユーザーの事前費用承認が必要 |
| 日次累計1,000円超過見込み | ユーザーの事前予算承認が必要 |
| 新仕様採用・未承認Trial範囲・重要なScope変更 | 金額に関係なくユーザー承認が必要 |

従来の「個別予算枠のない新規有料作業は見積100円超で事前承認」という金額ルールを、今回の正式決定に合わせて改訂する。

**日次予算1,000円は、AIが承認済みScope内の開発費を自律配分するための枠であり、未承認の新仕様・新しいTrial範囲・Scope変更を自由に実行する許可ではない。**

### 2. 運用上の具体的な考え方

- 案件見積が300円以下で、既存の承認済みScope内であれば、20円・50円などの少額Trialや検証のたびにユーザーへ確認せず、自律的に実行する。
- 見積300円超の場合は、日次予算に残額があっても、事前にユーザー承認を得る。
- 日次累計が1,000円を超える見込みの場合は、案件ごとの見積が300円以下であっても、超過前に承認を得る。
- 既存のユーザー承認済み個別Cap・明示STOP・安全上限・Production承認Gateは維持する。既存Capを超える場合は、300円以下でも承認が必要。
- 1案件を複数の小作業に分割して300円以下に見せかけたり、日付を分割して承認境界を回避したりしない。
- 見積と実費を記録し、残予算と改善見込みから効率的に費用配分する。必要十分な品質に達した後の不要なTrialは行わない。

### 3. 既存仕様との整合・文書改訂

今回の決定を既存SSOT・Agent共通Charterへ反映する。

主な確認・改訂対象：

- `CLAUDE.md` 共通Charterの第2・第6原則および費用承認に関する補足
- `docs/pm/PM_GOVERNANCE.md` §7-7・§7-9・§11・§29および関連参照
- Agent指示、Fableの委任・費用判断ルール
- PM_BRIEF、委任テンプレート
- CURRENT_SPEC、DECISION_LOG、OPEN_ITEMS、判断レジスタ

既存の100円基準を残して今回の300円基準と競合させないこと。

ただし、金額以外の既存の安全・承認・STOPルールは、ユーザーが変更を決定した範囲を超えて緩和しない。

**単なる追記で済ませず、旧ルールの修正・撤去と参照先の整合まで行う。**

### 4. QCD・再発防止

本改訂の目的は、費用の承認確認がDeliveryを不合理に遅らせることを防ぎつつ、開発費と承認範囲を適切に管理することである。

特に次の問題を防止する。

- 承認済みScope内で20円程度の費用を都度確認して停止する。
- 日次1,000円以内であることを理由に、未承認TrialやScope変更へ着手する。
- 300円を超える案件を分割して事前承認を回避する。
- 個別Capや日次予算の超過を見落とす。
- 費用承認を回避するため、合理的理由なくTrialを翌日に分ける。

既存の費用管理機構を優先利用し、過剰な新規Validator・承認工程は増設しない。

### 5. 実施範囲・検証

今回の対象は、**費用承認ルールと関連する文書・Agent運用の整合**である。

- 旧100円ルールと新300円ルールの参照箇所を調査する。
- 新ルールが全Agentに一貫して適用されるよう整備する。
- 金額判定・個別Cap・日次累計・Scope承認の組み合わせをテストする。
- 既存のProduction仕様、記事生成Prompt、TTS仕様、品質Gateは変更しない。
- 必要なSSOT更新、Git commit／pushを完了する。

### 6. STOP条件

今回承認された範囲を超える実質的な仕様変更、既存の重要な承認境界との解消不能な矛盾、安全上の問題が見つかった場合はSTOPして報告する。

既存仕様・Gate・承認済み予算の範囲内で解決できる軽微な不整合は、自律的に修正・検証する。

### 7. 完了報告・Fable受入

Fableは次の内容を独立して確認する。

1. 100円基準が適切に300円基準へ改訂されたこと。
2. 承認済みScope内では少額費用の都度承認が不要になったこと。
3. 個別Cap・日次1,000円・未承認Scope・STOP境界が維持されていること。
4. 既存ルールとの矛盾・Dangling Referenceがないこと。
5. 必須テストPASS、SSOT更新、Git反映が完了したこと。

最終報告には、変更ファイル、承認判定の代表例、テスト結果、commit、未解決事項を簡潔に示す。

**本件の完了条件は、開発費承認ルールが全Agent・PM運用で矛盾なく適用できる状態になること。単なる文書追記では完了としない。**

## Fable指示(作業要件)
1. **参照箇所の全件調査**: Grep(下記)で「100円」基準(7-7、「個別予算枠のない新規有料作業」「見積100円超」等)の全参照を列挙し、各箇所を「撤去/改訂/履歴として残置(改定前と明記)」に分類した表を作る。履歴文書(DECISION_LOG過去エントリ、delegation_log、HISTORY、過去RESULT_PACKET、ER-*_REPORT)は編集せず残置(改定履歴として有効)。現行ルール文書(CLAUDE.md、PM_GOVERNANCE、PM_BRIEF、agents、templates、CURRENT_SPEC現行節、OPEN_ITEMS現行Status)は改訂。
2. **正本の改訂**: `docs/pm/PM_GOVERNANCE.md` 7-7を新ルール表(ユーザー§1の表+§2の6項目を逐語に近い形で)へ書き換え、7-9(日次1,000円)・11節(STOP条件/自明な修正)・29節(Charter判定表の費用関連行)との参照整合を取る。「分割して300円以下に見せかける/日付分割で境界回避」禁止、「既存Capを超える場合は300円以下でも承認」「日次1,000円超過見込みは案件300円以下でも事前承認」「新仕様採用・未承認Trial範囲・重要Scope変更は金額無関係に承認」を必ず含める。改定履歴行(「2026-10-18までの旧7-7=見積100円超→2026-10-19ユーザー決定で300円へ改訂、PM-DEV-COST-APPROVAL-RULE-300-01」)を1行残す。
3. **CLAUDE.md共通Charter**: 8原則本文は逐語のまま変更しない(第2・第6原則の原文には金額基準が含まれない。含まれる場合のみユーザー原文に沿う最小修正をし、その事実を報告)。「安全・承認境界」の予算文(「予算上限(日次1,000円は超過見込み時の事前承認、7-9)」)に300円基準への参照を最小追加(例: 「案件見積300円超は事前費用承認、7-7」)。`docs/pm/tools/check_charter_references_01.py`を再実行し36件PASSが維持されることを確認(逐語checkが失敗したら本文を戻す)。
4. **Agent指示・PM_BRIEF・テンプレート**: `.claude/agents/sandwich-pm.md`(「7-7 見積100円超=ユーザー判断」等)、`sonnet-worker.md`、`opus-consultant.md`、`haiku-worker.md`、`docs/pm/PM_BRIEF.md`、`docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`(F-1ブロックの費用記述)、`docs/pm/templates/`配下の他テンプレートで100円基準・旧表現を全て300円基準へ改訂。参照は正本7-7へ向け、ルール本文の複製は最小にする。
5. **判定テスト**: 既存の費用管理機構(daily_dev_cost集計、`docs/pm/tools/`配下の費用関連script)を確認し、承認要否の判定表を機械的に検証する小さなテスト`docs/pm/tools/check_cost_approval_rule_01.py`(+結果json)を作る(既存scriptに同等機能があればそれを拡張し新設しない)。少なくとも次の代表例を判定: (a)承認済みScope内・見積20円・日次残あり→自律可 (b)見積50円・Scope内→自律可 (c)見積300円ちょうど・Scope内→自律可 (d)見積301円→事前費用承認 (e)見積120円だが日次累計が1,000円超過見込み→事前予算承認 (f)見積80円だが案件個別Cap超過→承認必要 (g)見積40円だが未承認の新仕様/新Trial範囲→承認必要 (h)見積600円を200円×3に分割→分割合算で承認必要(分割回避検知) (i)日付をまたいで分割→合算判定。文書(7-7)の表とテストの判定表が一致することをテスト内で確認(7-7の表をGrepして閾値300/1000を読み取る等、二重定義を避ける工夫)。
6. **Dangling Reference確認**: 改訂後に`100円`・`見積100円`・`7-7`参照をGrepし、現行文書に旧基準が残っていないこと、参照先節番号が存在することを確認して表にする。
7. **SSOT**: CURRENT_SPEC.mdの費用承認/予算に関する現行記述(Grep `100円|7-7|日次1,000円`)を改訂(履歴節は残置)。OPEN_ITEMS: 新規`OPEN-421 PM-DEV-COST-APPROVAL-RULE-300-01`(番号は末尾最大+1を直前Grepで確定。並行agentがOPEN-420を使う予定)Status=DOCS_ALIGNED_PENDING_FABLE。OPEN-418(Charter残事項)にD-1(7-7維持の保留)が本決定で解決した旨追記。DECISION_LOG末尾に本決定(原文sha付き)。USER_DECISION_REGISTER: Charter D-1(7-7)の保留項目を判断済みへ、本決定を次番号で判断済み登録。REPORT_LEDGER末尾1行。ACTIVE_TASK先頭に固定ヘッダ(並行agentのヘッダの上に自分のブロックを追記、旧ヘッダは残す)。
8. **判定表の記録**: PM_GOVERNANCE 29節の判定表(明確化/実質変更)に本件を「実質変更(ユーザー正式決定2026-10-19)」として1行追加。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\pm\PM_GOVERNANCE.md` 7-6〜7-9節・11節冒頭(STOP条件・自明な修正)・29節
- `C:\Users\tensh\eigo-radio\CLAUDE.md` 共通Charter節(全体)
- `C:\Users\tensh\eigo-radio\.claude\agents\sandwich-pm.md`・`sonnet-worker.md`・`opus-consultant.md`・`haiku-worker.md`
- `C:\Users\tensh\eigo-radio\docs\pm\templates\DELEGATION_STANDARD_TEMPLATE.md`
- `C:\Users\tensh\eigo-radio\docs\pm\tools\check_charter_references_01.py`
- `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_PM-COMMON-CHARTER-REVISION-02_USER.md`(前回Charter改訂の原文、7-7保留の経緯)

## 事前指定Grep一覧+追記位置・更新位置の手順
- 全体: `rg -n "100円" --glob "!*.jsonl" --glob "!er0*_output/**"`→分類表へ。`rg -n "7-7"`→参照先の整合確認。`rg -n "見積.{0,6}100|個別予算枠のない"`。
- `PM_GOVERNANCE.md`: `^## 7|^### 7-7|^### 7-9|^## 11|^## 29`で節位置確定→7-7本文を置換、7-9/11/29は参照整合の最小修正。
- `CURRENT_SPEC.md`: `100円|7-7|費用承認|日次1,000`→現行節のみ改訂。
- `OPEN_ITEMS.md`: `OPEN-418|OPEN-42[0-9]`→番号確定・OPEN-418追記・OPEN-421新規。
- `docs/pm/USER_DECISION_REGISTER_01.md`: `7-7|D-1|#11[0-9]`→保留項目の更新・次番号登録。
- `DECISION_LOG.md`: 末尾追記。`docs/pm/REPORT_LEDGER.md`: 末尾1行。`docs/pm/ACTIVE_TASK.md`: 先頭追記。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_PM-DEV-COST-APPROVAL-RULE-300-01_委任_01.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_PM-DEV-COST-APPROVAL-RULE-300-01_委任_01.md_check.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_charter_references_01.py`(改訂前後の2回。結果json `C:\Users\tensh\eigo-radio\docs\pm\tools\check_charter_references_01_result.json`で`all_ok: true`・n=36を確認)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_cost_approval_rule_01.py --json-out C:\Users\tensh\eigo-radio\docs\pm\tools\check_cost_approval_rule_01_result.json`(新設。既存scriptを拡張した場合はその実パスに置き換え、RESULT_PACKETに実行した全文を記載)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`
- `certutil -hashfile C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_PM-DEV-COST-APPROVAL-RULE-300-01_USER.md SHA256`

## SSOT追記文(要点)
- OPEN-421(新規): 「ユーザー2026-10-19正式決定(原文sha): 開発費承認=承認済みScope内・案件見積300円以下は自律/300円超は事前費用承認/日次1,000円超過見込みは事前予算承認/新仕様・未承認Trial範囲・重要Scope変更は金額無関係に承認/既存個別Cap・STOP・安全上限・Production Gate維持/分割・日付分割による回避禁止。旧7-7(100円)は改訂済み。Status=DOCS_ALIGNED_PENDING_FABLE」。
- DECISION_LOG: 同旨+「旧7-7の100円基準は本決定で廃止(履歴文書は残置)」。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1(非共有): delegation_log 2件(+_check.json)、CLAUDE.md、docs/pm/PM_GOVERNANCE.md、docs/pm/PM_BRIEF.md、.claude/agents/*.md(変更分)、docs/pm/templates/*(変更分)、docs/pm/tools/check_cost_approval_rule_01.py(+_result.json)、docs/pm/tools/check_charter_references_01_result.json、CURRENT_SPEC.md。msg: `PM-DEV-COST-APPROVAL-RULE-300-01 委任_01: 開発費承認ルール改訂(見積100円超→300円超で事前承認、日次1,000円・個別Cap・Scope承認・分割回避禁止を明文化)、PM_GOVERNANCE 7-7正本改訂+CLAUDE.md/PM_BRIEF/Agent指示/テンプレート整合+判定テスト(JPY0)`
- commit 2(共有SSOT、並行agentのcommit確認後): OPEN_ITEMS.md、DECISION_LOG.md、docs/pm/USER_DECISION_REGISTER_01.md、docs/pm/REPORT_LEDGER.md、docs/pm/ACTIVE_TASK.md。msg: `PM-DEV-COST-APPROVAL-RULE-300-01 委任_01: SSOT記録(OPEN-421新規・OPEN-418更新・DECISION_LOG・REGISTER・ACTIVE_TASK)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_COST300_1.md`)
4行: (1)整合(100円参照の全件分類表の要約: 撤去/改訂/履歴残置の件数とファイル、7-7新旧対照、Charter 8原則逐語不変の確認、check_charter 36/36)(2)Production到達経路=変更なし(コード・Prompt・Gate不変)(3)成果物とcommit sha(1・2)、判定テスト結果(a)〜(i)の表、Dangling Reference確認表、変更ファイル一覧(4)撤去/残置(旧100円基準の残置箇所=履歴のみ)。`判定整合:`・`判断候補:`(金額以外の境界を緩和せざるを得ない矛盾があればUSER_DECISION候補として明記)・T-0 check・自己チェック(有料0/Productionコード不変/原文逐語保存の文字数とsha256/共有SSOT編集の待機結果)。
