FABLE-DELEGATION-MARKER: PM-SSOT-LINE-ENDING-RESTORE-CURRENT-SPEC-20261023

# 記録衛生(API 0・内容変更0): commit 1667aaa09 で `CURRENT_SPEC.md` が全行CRLF化して履歴diffが膨らんだ問題を、通常commitで復元する(amend/rebase/force push禁止)。

## 手順
1. `git show 1667aaa09~1:CURRENT_SPEC.md | file -` または `.venv\Scripts\python.exe -c` でバイト検査し、**直前commitの改行コード**(LF想定)を確認。HEADの `CURRENT_SPEC.md` も同様に検査。
2. 直前commitがLFでHEADがCRLFなら、作業コピーをLFへ正規化(内容は1バイトも変えない。BOM有無も維持)。`git diff --ignore-cr-at-eol 1667aaa09~1 -- CURRENT_SPEC.md` が「Fable最終受入2026-10-23の追記1行のみ」であることを確認し、正規化後の `git diff --stat HEAD -- CURRENT_SPEC.md` で行数が全行相当になる(=CRLF→LF復元)ことを確認。
3. 同じ検査を `OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/pm/PM_GOVERNANCE.md` にも行い、直前数commitでCRLF化したものがあれば同様に復元(内容不変を `--ignore-cr-at-eol` で確認)。
4. `.gitattributes` に `*.md text eol=lf` 等の設定があるか確認し、無ければ**追加しない**(設定変更はユーザー判断事項として報告のみ)。原因(どのツール/agentがCRLFで保存したか)を `git log -3 --format=%h -- CURRENT_SPEC.md` と `docs/pm/delegation_log/` の直近記録から推定して1行で報告。
5. Git: `git diff --cached --name-status` で対象ファイルのみ→ `git commit --only -- <path…>` (message: "SSOT改行コード復元: CURRENT_SPEC.md等をLFへ戻す(1667aaa09のCRLF化を修正、内容変更0)") → `git push origin HEAD:main`。他agentのstaged変更(FAMILY-Y関連)を巻き込まない。
6. 委任文を `docs/pm/delegation_log/2026-10-23_PM-SSOT-LINE-ENDING-RESTORE_委任_01.md` に逐語保存(手で逐語保存、末尾注記)。これも同じcommitに含めてよい。

## 禁止
内容の編集・整形・空白変更。amend/rebase/force push/stash/reset --hard/checkout -f/一時index。他agentの行・ファイルに触らない。完了したらcommit hash、復元したファイル一覧、原因推定、.gitattributesの有無のみ報告。

(注記: 委任文の手動逐語保存。システムリマインダ部は除く。)
