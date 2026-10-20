# 委任文(Fable→sonnet-worker)

## 管理ID
PM-GIT-PUSH-TARGET-CORRECTION-01(FAMILY-X-RESEARCH-FACT-RETENTION-TRIAL-01 委任_04のpush先是正。JPY0、read-mostly)。並行: 別agent(FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 委任_01)が同じ作業treeでcommitを続けている。本委任は**ファイル編集・add・commitを一切しない**。pushと確認のみ。

## 背景
- ローカルbranchは `work/post-merge-01`(HEAD=252d0c3be)。`origin/main`=6e1efec39(直前までの全commitはmainへ届いていた=従来は `git push origin HEAD:main` 相当で運用)。
- 委任_04のagentは `git push origin work/post-merge-01` を行い、mainが更新されていない(origin/work/post-merge-01が新設された)。GitHub Pages(試聴ページ)はmain配信のため、mainへ反映が必要。

## 作業
1. `git fetch origin --prune` → `git log --oneline origin/main..HEAD` で、origin/mainがHEADの祖先(fast-forward可能)であることを確認。`git status --porcelain | Measure-Object -Line` で未commit件数も記録(編集はしない)。
2. fast-forward可能なら `git push origin HEAD:main`(**force禁止**。rejectedなら中止して報告)。
3. `git log --oneline -1 origin/main` でmainがHEAD(または並行agentがその後に積んだcommit)になったことを確認。
4. `origin/work/post-merge-01` は削除しない(ユーザー判断事項、報告のみ)。
5. 直近の数日間、どのようにmainへpushされていたか `git reflog --date=iso -n 40 | Select-String push` と `git log --format='%h %D' -n 8` で確認し、従来運用(`HEAD:main`か)を1行で報告。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 本委任文を `docs/pm/delegation_log/2026-10-20_PM-GIT-PUSH-TARGET-CORRECTION-01_委任_01.md` へ保存(extractツール `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <上記path>`、Nは本委任文のindex[管理ID PM-GIT-PUSH-TARGET-CORRECTION-01を含む最新])し `check_delegation_prompt.py --file <上記path> --json-out <上記path>_check.json` を実行。**このファイルはadd/commitしない**(並行agentのindex汚染回避。次回委任でcommit)。
T-2: TTSなし。

## 報告(docs/pm/RESULT_PACKET_GITFIX1.md)
fast-forward可否/push結果/origin/mainの新hash/従来運用の確認結果/未commit件数/T-0結果。判断候補があれば「判断候補」と書く。