# VERIFY_03 公開検証(委任_03、2026-10-27、API 0)
- 公開URL: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/ (commit 31c80404b。Pages反映まで約8分、キャッシュバスタ付きで確認)
- HTTP: index.html / data/melos__a2__prod.json / data/articles.json = 200。公開`form_logic.js`に`candIdOf`あり、公開データJSONに`candidate_id`あり。
- headless Chrome(公開URL): `browser_check_03.mjs` pass=9 fail=0(`browser_check_03_public_output.txt`)、既存`browser_check_02.mjs` pass=19 fail=0(`browser_check_02_public_rerun_03.txt`=UI不変の回帰)。Console error/exception 0。
- 実DOMで確認した内容: 送信文の各選定項目に`candidate_id: <データ逐語>｜種類: phrase|word`、`候補集合sha256: <データ値>`行、AI理由行に`term(candidate_id)`、先頭5ブロック書式不変、コピーJSONに`schema_minor:1`・`article.candidates_sha256`(+source/path)・各itemと`ai_reference`と`candidates_all`の`candidate_id`/`kind`。Trial-02・replay由来データは`candidates_sha256:null`+`unavailable_*`を明示(捏造なし)。
- URL長影響: `SEND_CHECK_03.md`(3選択で+約390〜410字、全て6000以内)。
