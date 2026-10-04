# 委任_04e OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01

管理ID: OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01(委任_04e)。git操作・API実行・他ファイル編集は行わない。

## 背景
Opus#15レビュー全文の保存がモデル再出力中に2回中断。本文を再出力せず、Fableセッション記録からスクリプトで抽出してコピーする。

## 作業
1. docs/pm/tools/extract_agent_text_from_transcript_01.py(汎用)を作成。引数 --transcript --start-marker --end-marker --out --header-file。全文字列値を走査し、start〜endの最長一致を抽出。
2. transcript=f9ae115b-...jsonl から Opus#15本文を docs/pm/opus_l2_review_open233_production_wiring_15.md へ抽出(4行header付き)。
3. 文字数・見出し(論点別判定/Safety hole/STOP条件/十分に答えられなかった点)を確認。
4. 本委任文を保存しcheck実行。

## 報告(5行以内)
抽出文字数、見出し確認、出力パス、スクリプトパス、check結果。本文引用なし。
