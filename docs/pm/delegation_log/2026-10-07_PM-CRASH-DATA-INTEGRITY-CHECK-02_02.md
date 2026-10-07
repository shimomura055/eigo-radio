# 2026-10-07 PM-CRASH-DATA-INTEGRITY-CHECK-02 委任_02(Closeout: ACTIVE_TASK更新+commit/push)

Management-ID: PM-CRASH-DATA-INTEGRITY-CHECK-02(委任_02)

## 管理ID・並行タスク
並行タスクなし(委任_01・OPEN-233-B3-BRIEF-STRUCTURE-TRIAL-01 委任_A4prepは完了済み)。

## 性質/到達上限Status/禁止事項
- 性質: 一時ファイル docs/pm/ACTIVE_TASK.md の更新と、整合性確認記録3件のcommit/pushのみ。費用¥0。
- 到達上限Status: USER_DECISION_REQUIRED(段階2再開可否はユーザー判断)。
- 禁止: SSOT編集、コード・Prompt編集、er052_output/配下の削除・修復・編集、Trial/記事生成/API呼び出し、git add -A/git add .、破損ファイル・0バイトファイルの削除、段階2の再開。
- 固定ブロック: E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(T-1/T-3非該当。T-0=本委任文保存+check結果保存)。

## 事前指定Read
- docs/pm/ACTIVE_TASK.md(全文) / docs/pm/PM_BRIEF.md 固定ヘッダ節 / _02_result.md

## 事前指定Grep一覧+追記位置・更新位置
Grep不要。ACTIVE_TASK冒頭に固定ヘッダ新規挿入、line 20(B3 TRIAL行)末尾へ段階2中断の1文を追記(詳細は委任原文のとおり)。

## 実行コマンド全文
1. ACTIVE_TASK.md編集 2. 本文保存+check_delegation_prompt.py→_02_check.json 3. 指定6ファイルのみ個別git add(staged 6件以内確認) 4. commit(trailer付き) 5. git push origin main(失敗時STOP)

## Git
個別add。git add -A禁止。

## 報告
RESULT_PACKET.md上書き(8行以内)+commit hash/push結果/差分要点/check結果/raw URL一覧。
