# TEST_07 送信・コピー改善(人間可読+照合コード)のtest(委任_07、2026-10-27、API 0)

| test | 内容 | 結果 |
|---|---|---|
| `selection_form_logic_test_01.js`(node) | 既存50件+旧送信URL系3件を新仕様へ更新(JSON同梱廃止・貼付案内・全項目欠落なし)。上限3/5/12・文法1件/0件・ロック等は無変更でPASS | exit 0、PASS 56行(`TEST_07_node_output.txt`) |
| `form1_selection_form_v3_test_01.py` `ReadableCopyV3Test` | (1)固定fixture(`fixtures_07/mini_article.json`+`mini_expected_readable.txt`、約4,000字の解説・仮訳/未生成訳・同名文法・複数行コメント): node出力==Python試作出力をバイト一致、解説全文に欠落なし (2)全公開データ×8乱択(0/1件文法、ロック記事を含む): node(フォーム実装)==Python試作の人間可読+照合コードがバイト一致 (3)node出力->復元(試作)->payload==既存`buildStructured`(selection/article/comment、フォームが併記する`rank`のみ除外)、AI島Advの改変7種(項目欠落/訳の意訳/解説末尾切れ/解説改変/コメント改変/照合コード欠落/1字改変)は全て`RestoreError` (4)委任_07Rの`er128_form_readable_restore_01.restore`でも同じ出力を復元でき試作とpayload一致 (5)`index.html`静的契約(`writeText`が`window.open`より先、URL超過で`https://chatgpt.com/`、`<details>`内の技術情報、上限定数不変、`fetch(`2件) | 5件OK(`run_project_regression.py --pattern form1_selection_form_v3_test_01.py` -> 22 passed / 0 failed、`TEST_07_py_output.txt`) |
| `readable_dump_07.js` | フォーム実装の出力をtestへ渡す補助。`FL.sha256Hex`をnode標準cryptoと照合し不一致なら例外 | (上記に含む) |
| `browser_check_07.mjs`(headless Chrome実DOM) | `VERIFY_07.md`参照 | ローカル25/0 |

照合コードのバイト一致: 純JS SHA-256(`FormLogic.sha256Hex`)==node crypto==Python hashlib==ブラウザWebCrypto(d6の相互照合をbrowser_check_07 A項で実施)。
