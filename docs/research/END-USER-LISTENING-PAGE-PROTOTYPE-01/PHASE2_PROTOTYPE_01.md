# PHASE2_PROTOTYPE_01(END-USER-LISTENING-PAGE-PROTOTYPE-01 委任_01b、2026-10-29。API 0・費用0円・Production変更0)

## URL(DEV試作・正式公開ページではありません)
- https://shimomura055.github.io/eigo-radio/user_test/dev_enduser_page_01/index.html (主記事=AI島 Std/Adv)
- 月のしわ(Advのみ・Grammar 1件の表示確認): `...index.html?a=moon`
- ハイライトのフック確認用ダミー(精度を主張しない): `...index.html?a=ai_island&lv=std&sync=dummy`

## 構成
`user_test/dev_enduser_page_01/` = `index.html`(骨格)・`style.css`・`app.js`(外部ライブラリなし)・`data/{ai_island,moon}.json`(公開ページ+timeline.jsonから`tools/build_data_01.py`で生成。本文/解説は改変なし、audio sha256記録)・`data/sync_index.json`(空`{}`=実同期なし。委任_02で01aの`sentences.json`を接続)・`data/sync_dummy_*.json`(文字数比例の仮配分、フック動作確認専用)。音声は既存公開mp3を相対参照(`../family_x_ai_island_form_01/audio/`等、コピー・再生成なし)。

## 継承した要素 / 組み込んだ要素 / 未実装
- 継承=DESIGN_NOTE_01.md「継承した要素」表(unifiedの配色・hero・カード・「ここから再生」・内部情報非表示)。
- 組み込み: タイトル・レベル(Std/Advタブ)/全体再生(通しmp3)+パート別再生(segment mp3)/再生・停止・シークバー・±10秒/スクリプト(文単位span)/Key Phrase(Std=日本語の意味、Adv=英語での解説、各KP音声)/本文下線lk1-3+語の意味一覧/Vocabulary & Expressions(意味・本文英文・訳・解説)/Grammar & Sentence Structure(採用件数に応じ。AI島=0件で非表示、月Adv=1件表示)/Preview/Comment1-4/In One Line/固定フッター再生バー(スマホ親指操作)/文単位ハイライトのフック(`data-sid`+同期JSON、自動スクロール、ユーザー操作後3.5秒は抑止)。
- 未実装(意図的): 再生速度(既存に無い)、Top/一覧/会員、実同期データによるハイライト(委任_02)、文単位より細かい単位。

## 検証結果(Playwright、`tools/verify_page_01.py`。ローカルRange対応サーバ=`tools/range_server_01.py`+live URL)
- ローカル: PC 1280×900 / スマホ 390×844(iPhone UA、DPR3、touch)で全check OK(`verify_result_01.json`、NG 0)。live(GitHub Pages)でも同一スクリプトで全check OK(`verify_result_live_01.json`、NG 0)。
- 確認項目: 横スクロールなし(scrollWidth=innerWidth)/DEV表記/カード構成/KP3件・Vocab5件・文57(Std)/Grammar(AI島0件=非表示、月=表示、`=====`混入なし)/全体再生開始/シークバー(500→164秒)・±10秒/一時停止で位置保持・再開/Std可視パート14・Adv13・月13の**全segment再生開始**/パート再生は当該パート終端で停止/「通しで」再生/Std→Adv切替/ダミー同期でハイライト点灯・前進・一時停止中保持・シーク追従/console error 0・HTTP 4xx/5xx 0。
- スクショ(`shots/`): `pc_01..05`・`mobile_01..05`(トップ・再生中・ハイライト・Adv本文・月Grammar)。
- 注意: Python標準`http.server`はRange非対応でシークが効かない(試作の不具合ではなくlocal検証環境の制約)。Range対応サーバで再検証しlive(Range対応)でも一致。

## 既知の制約・未確認
1. 文単位ハイライトの**同期精度は本委任では未検証**(ダミー=文字数比例の仮配分でフック動作のみ確認。精度・Chunk境界・無音・再生終了は委任_02)。
2. 実機iOS Safari/Android Chromeでの再生・固定フッター・セーフエリアは**未確認**(Chromium+iPhone UA/viewportの模擬のみ)。
3. 文分割(`build_data_01.py`)と01aのsentences.jsonの文境界が一致する保証は未確認(委任_02で`text`照合またはdata再生成)。略語ピリオド・引用符内終止は簡易規則。
4. ±10秒ボタンは試作上の追加操作(承認済み表示仕様の項目ではない。Phase 3で要否判断)。
5. 月Adv Grammar解説末尾に区切り文字列`=====`が混入(`study_text`由来、`er019_output/.../moon_shrinking__run_reselect_01/b1b/study_text/{confirmed_grammar,confirmed_grammar_frozen,grammar_explanations,part2_result}.json`ほか)。試作では表示時のみ除去(`data/_sanitized_log.json`)。**上流の不具合候補**(公開候補ページ`user_test/family_x_moon_shrinking_reselect_01/index.html`にも`=====`が表示されている)=Fableへ報告(分類=修正へ進む候補)。
6. 公開ページは0件でも「今回の本文には…ありませんでした」をGrammar節に出す旧実装(AI島公開ページ)。試作は承認済み仕様(0件は非表示)に従い非表示。公開ページ側との表示差。
7. 公開済みページの音声が将来差し替わると相対参照の内容が変わる(sha256記録済みで検知可能)。
