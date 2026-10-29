# production asset 差分一覧(DEV rev01-e -> production rev01-e)

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

sha256:

- index.html: `86231e4f85e0a8307f6d15e0a8bd2e41fcd730644fd228924349852744d512ab`
- app.js: `fe0238bfb9f9be9958d82bb7ae5d91f98db0f0834401959509c7b918e41bae47`
- style.css: `b292eb97418b84c944ed3dfaab28f678ad96c5c263e98933d5606932561eaed9`
