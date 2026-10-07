# 2026-10-07 PM-CRASH-DATA-INTEGRITY-CHECK-02 (初回委任)

Management-ID: PM-CRASH-DATA-INTEGRITY-CHECK-02

(sandwich-pm(Fable)からの委任文を要旨のまま保存。前例: 2026-10-01_PM-CRASH-DATA-INTEGRITY-CHECK-01.md)

## 性質/到達上限Status/禁止事項
- 性質: read-onlyの調査のみ。PC強制終了後のリポジトリ破損・進行中作業の確認。修復は一切しない。
- 到達上限Status: 調査完了(INTEGRITY_OK / INTEGRITY_ISSUE_FOUND)。費用: 0円(API呼び出し禁止)。
- 禁止: ACTIVE_TASK.md/RESULT_PACKET.md編集、SSOT/コード/Prompt/er0XX_output編集、状態を変えるgit操作全般、lock/0バイト/壊れたファイルの削除・修復、検査スクリプトのリポジトリ内作成(scratchpad配下のみ)、回帰テスト・Trial・記事生成の実行。
- リポジトリ内への新規作成は本委任文+check結果json+報告ファイル1件のみ。

## 固定ブロック
E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3(TTS・API呼び出しなし、T-1・T-3非該当)。

## ユーザー指示(原文)
> パソコンが固まり強制終了しました。現状を確認した上で、作業の再開を御願いします。

## 実行内容(要旨) A-G
A. Git本体(fsck/HEAD/reflog/origin比較/stash/lock/NUL)。B. 作業ツリー変更件数・未追跡一覧。C. クラッシュ時刻(Get-WinEvent 41/6008/1001)+最終commit以降のmtime更新ファイル列挙。D. 更新ファイルの破損スキャン(json/jsonl parse、NUL)。E. 進行中作業の特定(delegation_log 10-07、RESULT_PACKET、er052_output)。F. 重要ファイル存在・NUL・末尾確認、.venv python確認。G. 残存pythonプロセス確認。

## Git
commit・push・addは行わない。SSOT編集権なし。

## 報告
docs/pm/delegation_log/2026-10-07_PM-CRASH-DATA-INTEGRITY-CHECK-02_result.md へ書き、同内容を最終メッセージで返す(項目1-9)。
