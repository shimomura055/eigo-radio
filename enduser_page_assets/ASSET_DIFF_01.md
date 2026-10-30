# production asset 差分一覧(DEV rev01-e -> production rev01-g)

許可リスト(EDITS)に載った変更のみ。REMOVE=DEV専用機能の除去 / ADD=本番に必要な最小追加。

| id | file | 種別 | 内容 |
|---|---|---|---|
| H1 | index.html | REMOVE | DEV表記のtitle |
| H2 | index.html | REMOVE | ダミー同期の状態表示(確認用) |
| H3 | index.html | ADD | 承認済みVoice説明文(Family Y。CURRENT_SPEC:3202-3206)の表示場所=hero直下 |
| J1 | app.js | REMOVE | DEV試作の説明コメント(DEV path・dummy同期の記述) |
| J2 | app.js | REMOVE | sync_index(複数記事の同期索引)の変数 |
| J3 | app.js | REMOVE | DEV訳(未承認)の判定変数とコメント |
| J4 | app.js | REMOVE | DEV訳(未承認)の表示タグ |
| J5 | app.js | ADD | Key Phrase表の3列目(Z Advanced: 英語での説明)を意味の下に表示(2列のKPは不変) |
| J6 | app.js | REMOVE | 文法の仮データ表示(placeholder)の判定 |
| J7 | app.js | REMOVE | 文法の仮データ注記 |
| J8 | app.js | REMOVE | 文法ラベルの仮表示 |
| J9 | app.js | REMOVE | ニュアンスの仮データ判定とコメント |
| J10 | app.js | REMOVE | ニュアンスの仮データ注記 |
| J11 | app.js | REMOVE | ニュアンスラベルの仮表示 |
| J12 | app.js | REMOVE | 同期データ読込: ?sync=dummy|off分岐・sync_index経由(複数記事)・状態表示を除き、data/sync_<lv>.jsonだけを読む |
| J13 | app.js | REMOVE | document.titleの[DEV]接頭辞 |
| J14 | app.js | REMOVE | URL queryの記事id(a=)。記事切替UIは無く1ページ=1記事 |
| J15 | app.js | REMOVE | 記事id引数・記事別data path(data/<id>.json)を固定のdata/article.jsonへ |
| J16 | app.js | ADD | 承認済みVoice説明文(Y)をhero直下へ表示(notice無しなら非表示のまま) |
| J17 | app.js | REMOVE | 記事切替の入口(Q.get('a')) |
| J18 | app.js | ADD | 不具合是正: 不規則動詞(hold/give等)の3単現・ing形(holds/giving等)を太字対象に含める(DEVはholds heat inのholdを取りこぼした。月Standardで検出) |
| C1 | style.css | REMOVE | DEV試作の説明コメント |
| C2 | style.css | REMOVE | DEV訳(未承認)タグのスタイル |
| C3 | style.css | REMOVE | 仮データ注記(phnote)のスタイル |
| C4 | style.css | ADD | Voice説明文(hero直下)とKP 3列目のスタイル |
| J19 | app.js | ADD | rev01-f: 連動用の状態変数(jgEls=群id->JA要素, sidToG=文sid->群id, activeG=点灯中の群, jaHold=文と文の間も保持する群) |
| J20 | app.js | ADD | rev01-f: jaHtml()=日本語訳の群範囲(UTF-16 code unitオフセット)を<span class=jhl>で包む。訳本文は不変・ja_align無し/不正は従来表示。escは切り出し後 |
| J21 | app.js | ADD | rev01-f: 日本語訳の各段落をjaHtml()経由で出力(ja_align無しは従来出力と同一) |
| J22 | app.js | ADD | rev01-f: render()末尾でjgEls/sidToGを構築(sentElsと同じ場所)。再構築時は点灯状態も初期化 |
| J23 | app.js | ADD | rev01-f: highlight(sid)の先頭でjaLight(sid)を呼ぶ(連動の追加点はこの1箇所。nullグループのEN文はJAを点灯しない) |
| J24 | app.js | ADD | rev01-f: tick()で文と文の間の保持群(jaHold)を更新してからhighlight()を呼ぶ(再生・シーク・クリック・レベル切替は従来どおりtick/highlightに集約) |
| J25 | app.js | ADD | rev01-f: 検証用の状態__EUPに点灯中のJA群(jg)を追加 |
| C5 | style.css | ADD | rev01-f: 日本語訳の対応群の点灯(.sent.onと同じ変数・同じ見た目) |
| H4a | index.html | ADD | rev01-g: キャッシュ更新用のbuild-id(rev01-e -> rev01-g。assetの更新が古いJSキャッシュで隠れない) |
| H4b | index.html | ADD | rev01-g: style.cssのcache-bust |
| H4c | index.html | ADD | rev01-g: body data-build |
| H4d | index.html | ADD | rev01-g: app.jsのcache-bust |
| J26 | app.js | ADD | rev01-g: Previewカードにも日本語訳(trHtml)を出す(訳が無いPreviewは空文字=表示不変)。Adv Previewの生成訳の表示場所 |
| J27 | app.js | ADD | rev01-g: Vocabulary単体音声の状態(mode='vocab'・vocabI=再生中の項目・resumeAt=再生前の通し位置) |
| J28 | app.js | ADD | rev01-g: Vocabulary & Expressionsの各項目(summary内=閉じていても押せる)に英語音声の再生ボタン(article.jsonのvocab[i].audioがある項目) |
| J29 | app.js | ADD | rev01-g: playVocab/endVocab(単体mp3を共有プレーヤで再生。終端で通し再生の状態へ戻す=再生前の位置・自動再生なし) |
| J30 | app.js | ADD | rev01-g: vocabモードの長さ(単体mp3のdur) |
| J31 | app.js | ADD | rev01-g: vocabモードは全編のどの部分でもない(通し再生のpart強調・文ハイライトを出さない) |
| J32 | app.js | ADD | rev01-g: nowLabelにvocab項目名 |
| J33 | app.js | ADD | rev01-g: vocabモード中はtickが文ハイライト(英語・日本語)を更新しない(単体音声の秒を全編の秒と取り違えない) |
| J34 | app.js | ADD | rev01-g: Vocabulary再生ボタンのclick(summary内のためdetailsの開閉を抑止) |
| J35 | app.js | ADD | rev01-g: 単体音声の終端でendVocab() |
| J36 | app.js | ADD | rev01-g: 検証用の状態__EUPにvocab項目(vi)を追加 |
| C6 | style.css | ADD | rev01-g: Vocabulary再生ボタンのレイアウト(PC=右横、mobile=意味の下) |

sha256:

- index.html: `d2c3c5495889bea1b539d46bc68f6af6dd02c01ecbde4f108eef741028e75c2a`
- app.js: `f616522b87e883ebd316fbb145949a2061ad3d33fd8cbafa74234eb8d0fb2091`
- style.css: `0b0a668a9db5575c130e14c0fabcd822c16d3421611a44c5653f1ef54f171ef4`
