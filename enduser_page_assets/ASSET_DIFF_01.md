# production asset 差分一覧(DEV rev01-e -> production rev01-h)

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
| H4a | index.html | ADD | rev01-g/h: キャッシュ更新用のbuild-id(rev01-e -> rev01-h。assetの更新が古いJSキャッシュで隠れない) |
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
| J37 | app.js | ADD | rev01-h: クリック選択の状態変数selectedSid(null|sid。停止中・一時停止中だけ保持) |
| J38 | app.js | ADD | rev01-h: render()の再構築で選択も初期化 |
| J39 | app.js | ADD | rev01-h: tick()=再生中は選択を解除して自動ハイライト優先。停止中・一時停止中で選択があれば位置由来の上書きをせず選択(英日)を維持 |
| J40 | app.js | ADD | rev01-h: 検証用の状態__EUPに選択sid(sel)を追加(読取専用) |
| J41 | app.js | ADD | rev01-h: seekSentence(その文から再生)を廃止し、selectSentence(選択ハイライトのみ。audio.play/pause/currentTimeを呼ばない)へ置換 |
| J42 | app.js | ADD | rev01-h: 文クリックのhandler=selectSentence(同期データ未取得でも選択はできる。日本語は点灯しない安全側) |
| J43 | app.js | ADD | rev01-h: 位置操作(ここから再生/全体再生)で選択を解除 |
| J44 | app.js | ADD | rev01-h: KP音声再生で選択を解除 |
| J45 | app.js | ADD | rev01-h: Vocabulary音声再生で選択を解除 |
| J46 | app.js | ADD | rev01-h: レベル切替で選択を解除 |
| J47 | app.js | ADD | rev01-h: -10秒で選択を解除(位置操作) |
| J48 | app.js | ADD | rev01-h: +10秒で選択を解除(位置操作) |
| J49 | app.js | ADD | rev01-h: シークバー操作で選択を解除(位置操作) |

sha256:

- index.html: `bc1e5e4e5f99a96e6053fc5f6a94403eeb90adf61a3ce2914907857d4e3b6df9`
- app.js: `abeea5e28123b5fa51db80e23354a467f4fcb37f40b1dde3e2d2ac323a40e259`
- style.css: `0b0a668a9db5575c130e14c0fabcd822c16d3421611a44c5653f1ef54f171ef4`
