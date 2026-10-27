# SEND_CHECK_01 送信・コピー検証(2026-10-26)

> **【旧仕様】委任_07(2026-10-27)で送信形式を人間可読+照合コード1行へ変更したため、本ファイルのJSON同梱・URL降格順・candidate_id行を含む送信文に関する記述は旧仕様の測定記録です。現行の測定は`SEND_CHECK_04.md`。**

| 項目 | 状態 | 根拠 |
|---|---|---|
| ChatGPT送信URL生成(`https://chatgpt.com/?q=`+選定テキスト+JSON、<=6000字) | 検証済み(生成物) | headless Chrome(CDP)で`#send`クリック→`window.open`引数を捕捉。URL長2985、デコード後に選定・コメント・JSON含有(`browser_check_01_output.txt`) |
| 6000字超のコピー誘導 | 検証済み(logic) | node test `chatgpt url ... falls back` |
| **chatgpt.comが実際に`?q=`を入力欄へ反映するか** | **未検証**(外部サイトの挙動。ユーザー実操作確認項目) | 本環境から未ログインのchatgpt.comへ実到達の確認不可 |
| `navigator.clipboard`コピー成功 | **未検証**(headlessは権限なしで拒否) | ユーザー実操作確認項目 |
| コピー失敗時のフォールバック(textarea表示・手動コピー誘導) | 検証済み | clipboardを拒否へ差替え→textarea表示・文字数1304を確認 |
「動作確認済み」と書けるのは上記「検証済み」のみ。ChatGPTへ実際に渡るか・Clipboard成功はユーザー実操作で確認。
