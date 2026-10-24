管理ID: FX-NEWS-SOURCE-LIST-CONFIRM-01 委任_01 — Family X記事候補探索で以前ユーザーと合意したニュースソース一覧(10サイト前後)と、現在の正式な記事候補探索ルールの**確認のみ**。Read-only(API 0・コード/SSOT/公開物変更0。作成してよいのは報告文書と原文・委任文の保存のみ)。サイトの追加・変更・新規記事探索は禁止。**記録が見つからない項目は推測で補わず「未確認/記録なし」と書く。**

## ユーザー原文(逐語)
Family Xの記事候補を探すため、以前ユーザーと合意したニュースソース一覧（10サイト前後）を確認してください。
1. Repo、CURRENT_SPEC、DECISION_LOG、過去の作業記録から、合意済みのサイト一覧をすべて抽出する。
2. 各サイト名・URL・選定理由を示す。
3. GIGAZINE以外のサイトも漏れなく確認する。
4. 現在の正式な記事候補探索ルール（直近24時間など）も併せて報告する。
**今回は既存の決定事項の確認のみ。サイトの追加・変更や新規記事探索は不要です。**
記録が見つからない場合は、推測で補わず、その旨を報告してください。

## 作業
1. 原文を `docs/pm/delegation_log/2026-10-24_FX-NEWS-SOURCE-LIST-CONFIRM-01_USER.md` に上記逐語で保存。本委任文を `..._DELEGATION_01.md` に保存(`py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index <最新> --out <path>`、先頭行一致確認)。
2. Grep調査(全文読込禁止、ヒット箇所の前後のみ読む): `CURRENT_SPEC.md`、`DECISION_LOG.md`、`DECISION_LOG_HISTORY.md`、`OPEN_ITEMS.md`、`OPEN_ITEMS_HISTORY.md`、`HISTORY_INDEX.md`、`ER-*_REPORT.md`、`docs/pm/PM_GOVERNANCE.md`(13節 新規記事テーマ選定ルール)、`docs/pm/delegation_log/`、`docs/research/`、`er019_*`/`er053_*`等のFamily Xニュース探索・テーマ選定関連の.py/設定/JSON(ソースURL・allowlist・RSS一覧等)。検索語の例: `ニュースソース|news source|source list|allowlist|RSS|feed|GIGAZINE|gigazine|ITmedia|Impress|日経|NHK|Reuters|BBC|Guardian|AP|TechCrunch|Ars Technica|The Verge|Nature|Science|直近24時間|24時間以内|within 24|テーマ候補|theme candidate|記事候補|候補探索|selection rule|選定理由`。Perplexity経由の探索(PERPLEXITY-401-INVESTIGATION-01)やテーマ選定プロンプトにサイト指定があるかも確認。
3. 結果は `docs/research/FX-NEWS-SOURCE-LIST-CONFIRM-01/SOURCE_LIST_CONFIRM_01.md` に: (a)合意済みサイト一覧表=サイト名/URL/選定理由/根拠(ファイル名:行番号、合意日、ユーザー承認の有無と承認記録の所在)。(b)「候補として挙がったが正式合意の記録がないサイト」は別表に分けて明記。(c)現在の正式な記事候補探索ルール(鮮度条件[直近24時間等]/除外条件/テーマ選定手順=複数候補提示→ユーザー選択/事実混同禁止等)を、根拠付きで列挙。(d)見つからなかった項目は「記録なし」と明記(推測禁止)。(e)矛盾・重複・古い記録がある場合はそのまま併記。
4. 報告 `docs/pm/RESULT_PACKET_FXNS1.md`(上記(a)〜(e)の要約+根拠パス)。
5. Git: 作成した3ファイル(原文・委任文・SOURCE_LIST_CONFIRM_01.md)のみ `git add <path>`→`git diff --cached --name-status`確認→`git commit --only -- <path…>`→`git push origin HEAD:main`。別agentが並行してcommit中のため、index lockは待って再試行。禁止: `git add -A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。SSOT・ACTIVE_TASK.mdは編集しない。