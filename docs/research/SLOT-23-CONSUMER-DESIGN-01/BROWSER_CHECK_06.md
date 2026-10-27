# BROWSER_CHECK_06 実ブラウザ検証(playwright/chromium headless、API 0)
対象=F班の最終pages出力(Y `pages/index.html`・`index_dev.html`、Z `pages_s23f/index.html`、X `player.html`・`player_dev.html`)をローカルHTTP(127.0.0.1)で開いた。
viewport: PC 1280x900(DPR1) / スマホ 375x812(DPR3) / スマホ 390x844(DPR2)。tool=`tools/browser_check_s23f_01.py`(結果JSON=`evidence_runs/31_browser_Y_X.json`・`32_browser_Z.json`、表=`evidence_runs/33_browser_summary_table.md`、スクリーンショット=`screenshots/`[要素crop=`*_lk{1,2,3}.png`、ページ冒頭=`*_top.jpg`。合計約1MB])。
計測: (1)各クラス(`strong.lk1`/`strong.lk2`/`span.lk3`)の1つめの要素の`getComputedStyle`(text-decoration-line/style、font-weight、font-size、color、background-color/image)と親要素の値の比較、(2)**下線の本数**=同一要素を「装飾あり」「`text-decoration:none`」の2回screenshotし、画素差分の行の連続グループ数(装飾の実描画行)を数える(lk1=2本、lk2/lk3=1本のはず)、(3)`document.body.innerText`の⏸・`data-hl`/`lk1..3`/`HL_`文字の有無、(4)装飾要素を含む親の選択テキスト(Range.toString)に⏸等の記号が混じるか、(5)装飾を剥がした`textContent`が装飾ありと同一か(改行・句読点・文字不変)、(6)横スクロール(`scrollWidth>innerWidth`)。

## 結果(全15行[5ページ×3viewport]。Pass/Failの総括は下)
| page | viewport | ①lk1 本数/style/weight | ②lk2 本数/style/weight | ③lk3 本数/style/weight | font-size=本文 | color=本文 | bg | ⏸(innerText) | dataattr文字 | copy余計記号 | 装飾剥がし=同一 | 横overflow |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Y_public | pc1280 | 2本/double/700 | 1本/solid/700 | 1本/solid/400 | True | True | なし | False | False | False | True(n=12) | False |
| Y_public | sp375_dpr3 | 4本/double/700 | 1本/solid/700 | 1本/solid/400 | True | True | なし | False | False | False | True(n=12) | True |
| Y_public | sp390_dpr2 | 4本/double/700 | 1本/solid/700 | 1本/solid/400 | True | True | なし | False | False | False | True(n=12) | True |
| Y_dev | pc1280 | 2本/double/700 | 1本/solid/700 | 1本/solid/400 | True | True | なし | True | False | False | True(n=12) | False |
| Y_dev | sp375_dpr3 | 4本/double/700 | 1本/solid/700 | 1本/solid/400 | True | True | なし | True | False | False | True(n=12) | True |
| Y_dev | sp390_dpr2 | 4本/double/700 | 1本/solid/700 | 1本/solid/400 | True | True | なし | True | False | False | True(n=12) | True |
| X_player_public | pc1280 | 2本/double/700 | 1本/solid/700 | 1本/solid/400 | True | True | なし | False | False | False | True(n=7) | True |
| X_player_public | sp375_dpr3 | 2本/double/700 | 1本/solid/700 | 1本/solid/400 | True | True | なし | False | False | False | True(n=7) | True |
| X_player_public | sp390_dpr2 | 2本/double/700 | 1本/solid/700 | 1本/solid/400 | True | True | なし | False | False | False | True(n=7) | True |
| X_player_dev | pc1280 | 2本/double/700 | 1本/solid/700 | 1本/solid/400 | True | True | なし | True | False | True | True(n=7) | True |
| X_player_dev | sp375_dpr3 | 2本/double/700 | 1本/solid/700 | 1本/solid/400 | True | True | なし | True | False | True | True(n=7) | True |
| X_player_dev | sp390_dpr2 | 2本/double/700 | 1本/solid/700 | 1本/solid/400 | True | True | なし | True | False | True | True(n=7) | True |
| Z_public | pc1280 | 2本/double/700 | 1本/solid/700 | 1本/solid/400 | True | True | なし | False | False | False | True(n=14) | False |
| Z_public | sp375_dpr3 | 2本/double/700 | 1本/solid/700 | 1本/solid/400 | True | True | なし | False | False | False | True(n=14) | True |
| Z_public | sp390_dpr2 | 2本/double/700 | 1本/solid/700 | 1本/solid/400 | True | True | なし | False | False | False | True(n=14) | True |

## 判定
- ①の二重下線が2本に見える: 全viewportで`text-decoration-style=double`、画素差分の下線行グループ=2(PC DPR1は行間1pxで2本[row20/22]、DPR2/3は明瞭に2本)。Y mobileの「4本」は**同一要素が2行に折返し、各行が2本**(rect数3。`wrapped_rect_count`)の意味。スクリーンショット例=`Y_public_sp375_dpr3_lk1.png`・`Y_public_sp390_dpr2_top.jpg`(「can’t be helped」が2行で各2本)。**所見**: PC(DPR1)の二重下線は2本の間隔が小さく、等倍表示では太い1本に近く見える(線間1px)。判別は可能(画素差分で2グループ)だが、細かい違いに依存する部分(仕様のCSS値`text-underline-offset:3px`・double)。
- ②③と太さ/下線の違いの判別: ②=太字(700)+実線1本、③=通常太さ(400)+実線1本、①=太字(700)+二重線。①②は太字で同じ、①と②は下線2本/1本、②と③は太さ。
- 文字サイズ・色が本文と同一: 全行 font-size=親と同一(Y/Z 15.2px、X 14.4px)・color=親と同一・背景なし(`rgba(0,0,0,0)`、background-image none)。
- 改行/段落/句読点不変: 装飾を剥がした`textContent`が装飾ありと同一(全ページ`all_equal=True`)。
- `document.body.innerText`に`⏸`なし(public全ページ)、`data-hl`等の文字混入なし(全ページ`False`)。コピーテキストに余計な記号なし(public全て`False`)。dev(`Y_dev`/`X_player_dev`)は⏸がinnerTextに出る(開発用仕様。Y_devは凡例の⏸のみ、X_player_devはChunk境界⏸12個。いずれも`data-hl`要素の外)。X_player_devのコピー有り=Chunk境界⏸を含む段落をコピーした場合(devのみ)。
- 横スクロール: PC1280はY/Zで無し、スマホ(375/390)はY/Z/Xで有り。**装飾を持たない既存ページ(ベース`run_gpg5_y_01/pages/index.html`)でも同じ(PC無し・スマホ有り)**ので装飾起因ではない既存挙動。X player.html/player_dev.htmlはPCでも横スクロール(広い表のレビュー用player。既存設計)。
- 範囲外/未実施: X公開ページ(標準builder)は不具合D-F1でSTOPしindex.htmlが無いため未計測(player.htmlは公開ページではない)。AI島(実記事)は別委任(AIF委任_06)。実機(実スマホ/Safari)ではなくchromiumのviewport/DPRエミュレーション。
