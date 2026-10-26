# VERIFY_01 公開検証(2026-10-26)
- 公開URL: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/ (push `0f4caaaff`、Pages反映まで約5分)
- HTTP: `/`200(11382B)、`form_logic.js`200、`data/articles.json`200、`data/ui_check_dummy__dummy.json`200、`data/monkeys_paw__b1b.json`200。
- 公開URLに対するheadless Chrome(CDP)実DOM検証: `browser_check_public_01_output.txt` → pass=32 fail=0(JSON読込・上限挙動・記事切替・保持・文法2件・送信URL・コピーfallback・Console error 0)。
- 未検証(ユーザー実操作): chatgpt.comが`?q=`を入力欄に反映するか、`navigator.clipboard`成功、スマホ表示、実機ブラウザ(Safari等)。
