# VERIFY_07 送信・コピー改善の検証(委任_07、2026-10-27、API 0)

## ローカル(http.server + headless Chrome、`browser_check_07.mjs`)
`browser_check_07_local_output.txt`: **pass=25 fail=0**(console error 0)。確認項目:
- 文法未決定は送信/コピー不可(clipboard未書込み)。AI島Std(確定KP/KW10件ロック表示・文法0件)のコピー=人間可読形式(記事見出し/①②③/文法：選定なし/自由コメント/照合コード1行)、JSON・candidate_id・SHA全文・AI理由なし、成功メッセージ(通常色)、`d6`==ブラウザが取得したデータ生バイトのWebCrypto SHA-256、実クリップボード(`readText`)==コピー文、コピーで選定状態不変。
- 送信=PREFACE(逐語返却依頼、「Claude Code向け指示案」なし)+人間可読+照合コード。**クリップボード書込みが`window.open`より先(同一クリック処理)**。閾値内は`https://chatgpt.com/?q=`に全文(`decodeURIComponent`==コピー文)、閾値超(長いコメント1,200字)は`https://chatgpt.com/`を開き「内容が長いため貼り付け方式です」を通常色で案内、全文はコピー済み。
- AI島Adv(文法Top1+複数行コメント): 【解説全文】が`grammar[].body`と逐語一致(欠落なし)、コメント複数行保持。
- クリップボード失敗(writeText拒否+execCommand失敗): 「自動コピーできませんでした…選定内容は保持されています」+手動コピー枠に全文、選定状態(localStorage)不変、送信ではChatGPTは開く。
- 「技術情報付きでコピー」は既定で閉じた`<details>`内(非表示)、押すと従来のテキスト+JSON(`candidates_all`付き)。
- 上限ロジック不変(4件目の①不可/①+②<=5/合計12件選択可)、12項目すべてが`- 英語：訳`行として出力。
- 取得したコピー文(`browser_check_07_captured_local.json`)を試作復元・`er128_form_readable_restore_01`で復元: AI島Std/Adv(文法0/1件)とも往復OK(ローカルのCRLF作業ツリーのため一部記事は`d6`差異が出る=下記注)。

## 公開URL
https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/ (commit b62a070cf、Pages反映確認: `form_logic.js`に`buildReadable`、index.html HTTP 200)
- headless Chrome(公開URL、実DOM) `browser_check_07.mjs`: **pass=25 fail=0**(`browser_check_07_public_output.txt`、console error 0)。ローカルと同一項目。
- 公開URLで取得したコピー文(`browser_check_07_captured_public.json`、5ケース)を復元: `er128_form_readable_restore_01.restore`(委任_07R)は**5/5復元OK**(AI島Std/Adv×文法0/1件、走れメロス相当12項目含む)。設計試作(`proto06`)は4/5OK、残る1件(CRLF作業ツリーの記事)は試作が`d6`をCRLFのまま計算するための差異で、公開(blob=LF)基準の`d6`を持つ照合コードは本番側tool(LF正規化)で一致する=上記注の実証。

## ユーザー実操作で確認していただく項目(自動検証の範囲外)
1. ChatGPTの`?q=`実上限(現行`URL_MAX=6000`字を引き上げられるか。AI島Std/Advの文法入り送信が貼付案内になるか)。
2. 実機ブラウザ(Chrome/Safari/スマホ)でのクリップボード書込み・貼り付けと、新タブでChatGPTが開くこと(ポップアップブロックの有無)。
3. ChatGPTがコードブロックで**逐語返却**するか(`**`強調・箇条書き記号が変わらないか)。変わった場合も復元tool側で検出・fail-closedするため誤確定はないが、再コピーが必要になる。
4. 返却された文章をClaudeへ貼り付けて確定内容として復元できること(委任_07Rのtool)。

## 注意・既知事項
- Windows作業ツリーのCRLFとリポジトリblob(LF)で`d6`が異なり得る。公開Pagesはblob(LF)を配信するため、公開URLでコピーした照合コードは復元tool(`d6_of_bytes`がCRLF->LF正規化)で一致する。ローカルhttp.server配信(CRLF)で得た文を復元toolへ渡すと、CRLFファイルの記事で`d6`差異が出る場合がある(ローカル検証固有)。
- `ai_island_temple__b1b__prod`の文法Top1は解説末尾が`。=====`(直前改行なし)。内部終端記号を含む逐語のまま出力し、復元側も同規則で一致する。データ側の終端統一は別途(`RESULT_PACKET_FORM7.md`判断候補ではなくB分類の記録)。
