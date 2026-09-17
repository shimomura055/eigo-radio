# RESULT_PACKET: USER-TEST-ARTICLE-LANDING-10-01

最終Status(FIX-01反映後): `PRODUCTION_WIRED`(Gate 3全項目○)
公開URL(FIX-01固定、最新): `https://rawcdn.githack.com/shimomura055/eigo-radio/41594eecc7d5e5dc07b506e52d38f895c473eb0e/user_test/articles_2026_0918.html`

★★★★報告ここから(初版)

1. 最終Status: `PRODUCTION_WIRED`(Gate 3全項目○)
2. TSV読取結果: `docs/user_test/ユーザーテスト記事一覧_2026-0918_選定10.tsv`をcsv.DictReaderで実パース。10行(ヘッダー除く)、全20 URLが`https://`で始まることをassertで確認。カテゴリー数3。
3. 使用SSOT path: `C:\Users\tensh\eigo-radio\docs\user_test\ユーザーテスト記事一覧_2026-0918_選定10.tsv`
4. 対象10記事(TSV順):
   1. Why Young Travelers Are Slowing Down(News系)
   2. Why We Wake Before the Alarm(News系)
   3. AI in the Convenience-Store Kitchen(News系)
   4. Are Tiny Bags Really Back?(News系)
   5. Free-Address or Assigned Desks?(様々な意見)
   6. Personalized News: Useful or Narrowing?(様々な意見)
   7. When AI Helps Choose Who Gets Hired(様々な意見)
   8. Home Robots: What They May Change(未来小説)
   9. How Technology May Change Memory(未来小説)
   10. Digital Twins: A Copy of the Real World(未来小説)
5. 3カテゴリー(TSV表記): 「News系の記事」(4件)/「様々な意見をまとめた記事」(3件)/「未来をテーマにした小説」(3件)
6. 作成ページpath: `user_test/articles_2026_0918.html`(既存ファイル無変更、新規作成)
7. 公開URL(HTML含むcommit `b78f3cb5`固定):
   `https://rawcdn.githack.com/shimomura055/eigo-radio/b78f3cb5918856fceaba934d337f51ea9756af42/user_test/articles_2026_0918.html`
8. PC表示runtime確認: 1280x800でPlaywright実行。10カードtitle_en/title_ja完全一致、3カテゴリー見出し一致、カード重なり0件、横スクロールなし(scrollWidth=innerWidth=1280)、Standard/Advancedボタン各10個。代表4本(News代表+様々な意見代表+未来小説代表+AI Hiring Standard)を実クリックし新タブ遷移URL一致・Play進行(currentTime>0、error=null)を4/4確認。
9. スマホ表示runtime確認: 390x844モバイルUA/touchでPlaywright実行。単一列(全カードx座標同一)、横スクロールなし、テキスト切れ0件、ボタン高さ全て44px以上・画面内、カテゴリー見出し一致。代表2本をクリックし遷移URL一致・Play進行を2/2確認。
10. 全20リンク一致: `docs/pm/closeout_136_e2e/landing_10_01/href_match.json` overall=PASS(10/10行、Standard/Advanced取り違えなし)。加えて全20 URL HTTP GET 200(`http200_check.json`)。
11. Personalized News Advanced FIX-01一致: TSVのadvanced_urlはDECISION_LOG `USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01-FIX-01-CLOSEOUT`のcanonical URL(commit`7ea8bd7a`)と文字列完全一致。
12. Browser E2E結果(evidenceパス): `docs/pm/closeout_136_e2e/landing_10_01/e2e_result.json`(PC/スマホとも全項目PASS)、screenshot `pc_full.png`・`mobile_full.png`(目視確認済み、崩れなし)。
13. Git commit: `b78f3cb5`(HTML+SSOT TSV+href_match.json+http200_check.json)push済み。`b271203f`(DECISION_LOG/ARTIFACT_REGISTRY/E2E evidence/RESULT_PACKET/delegation_log)push済み。
14. main=origin/main: 各pushの直前に`git fetch origin`で衝突なし確認。最終push成功(`b78f3cb5..b271203f`)、push後の`git fetch origin`でmain=origin/main=`b271203f`を確認済み。
15. SSOT/Decision Log更新内容: `DECISION_LOG.md`に`## USER-TEST-ARTICLE-LANDING-10-01`索引+本体エントリ追加。`ARTIFACT_REGISTRY.md`に「ユーザーテスト一覧ページ(10記事、2026-09-18)」行追加。`OPEN_ITEMS.md`/`CURRENT_SPEC.md`は変更なし(新規問題なし)。
16. 未解決事項: なし(本タスク範囲内)。
17. USER_DECISION_REQUIRED残存有無: なし。
18. APPROVED_FOR_PRODUCTION未配線項目の有無: なし(本ページ自体は既存承認済み10記事への導線のみで、記事内容・音声への変更なし)。
19. Dangling Reference Check結果: 20本の遷移先は全て既存`USER_TEST_READY`記事のcanonical URL、DEV/Trial-only artifactへの参照なし。AI Hiring Standardのsrc実体はRepo内存在確認済み。既存`unified.html`/`human_review.html`/記事/音声は無変更(git diff対象外)。Closeout Mandatory Check 21項目のうち本タスク該当分は○(詳細はDECISION_LOG本体エントリのPM Closeout Check 10項目参照)。

★★★★報告ここまで

## FIX-01(Fable受入照合による差し戻し1回目、CSS調整のみ)

1. 修正内容: 発見された問題は、PC 1280px幅・3列グリッドで各カードの
   「Advanced｜英語のみ」ボタン(10件全て)と「Standard｜日本語サポートあり」
   ボタンがボタン内テキストの途中で2行に折り返していたこと。`user_test/
   articles_2026_0918.html`のCSSのみを修正: `.btnrow`を横並び(2ボタン並列)
   から縦積みへ、`.btn`を`flex:1 1 130px`(幅制約あり)から`width:100%`
   (カード幅いっぱい)へ変更しテキストの表示幅を拡大、font-sizeを13.5px→14px
   へ引き上げ、`white-space:nowrap`を追加。列数(3列)・カードグリッド自体・
   href・記事内容は無変更。
2. 新公開URL(このCSS修正commitのSHAで固定):
   `https://rawcdn.githack.com/shimomura055/eigo-radio/41594eecc7d5e5dc07b506e52d38f895c473eb0e/user_test/articles_2026_0918.html`
   (HTTP 200確認済み、fetchしたCSSが修正後の内容であることを直接確認)。
3. PC E2E結果(1280×800、Playwright): 10カードtitle_en/title_ja完全一致・
   3カテゴリー一致・カード重なり0件・横スクロールなし・ボタン各10個・
   グリッド3列維持に加え、**20ボタン全件でボタン内テキストが1行に収まって
   いること**を`getClientRects().length===1`(要素・テキストRange両方)で
   機械判定し全件PASS(`btn_single_line_all_pass:true, fail_count:0`)。
   代表4本(News代表+様々な意見代表+未来小説代表+AI Hiring Standard)実クリック
   で遷移URL一致・Play進行4/4 PASS。screenshot: `pc_full_fix01.png`
   (目視でも10ボタン全て1行表示を確認)。evidence: `docs/pm/closeout_136_e2e/
   landing_10_01/e2e_result_fix01.json`。
4. スマホE2E結果(390×844): 同様に単一列・横スクロールなし・テキスト切れ0件・
   ボタン全て≥44px・**ボタン1行収まり20/20 PASS**、代表2本実クリックでPlay
   進行2/2 PASS。screenshot: `mobile_full_fix01.png`。
5. 全20 href一致再確認: `docs/pm/closeout_136_e2e/landing_10_01/
   href_match_fix01.json`でTSVとHTMLを再パース・再比較しoverall=`PASS`
   (10/10行)。hrefは無変更のため当然の結果。
6. Git commit: `41594eec`(HTML CSS修正+E2E evidence4点)push済み、
   `86101053`(DECISION_LOG/ARTIFACT_REGISTRY FIX-01反映)push済み。各push前後
   に`git fetch origin`で確認し、最終main=origin/main=`86101053`。
7. SSOT更新: `DECISION_LOG.md`の`## USER-TEST-ARTICLE-LANDING-10-01`エントリ
   末尾に`### FIX-01`節を追記(差し戻し理由・修正内容・新URL・E2E結果)。
   `ARTIFACT_REGISTRY.md`の該当行のURL・evidenceパスをFIX-01のものへ更新。
8. 無変更証跡: `git diff`で今回の変更ファイルは`user_test/
   articles_2026_0918.html`(CSSブロックのみ、+2/-4行)のみと確認。SSOT TSV
   (`docs/user_test/ユーザーテスト記事一覧_2026-0918_選定10.tsv`)・
   `unified.html`・記事本文・音声は本タスクのcommitに含まれず無変更。
9. 最終Status: `PRODUCTION_WIRED`(Gate 3全項目○、CSS修正後も維持)。
