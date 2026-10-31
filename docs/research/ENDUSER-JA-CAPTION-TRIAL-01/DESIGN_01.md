# DESIGN_01 日本語キャプション Trial(未承認・Production無変更)

## 方式
`enduser_page_assets/rev01-h/{app.js,style.css,index.html}`をコピーし`tools/build_caption_trial_01.py`で機械的にpatch(各置換は出現1回をassert)。出力=`user_test/enduser_caption_trial_01/`(`assets/`+6ページ`x|y|z_std|adv/index.html`+一覧`index.html`)。記事data/audioは既公開dirを`data-src`で参照(複製・再生成なし、API 0)。

## 表示仕様
- 位置: 固定再生バー内、2行目(`全体`ラベル/±10秒)の直下に`#jcap`(淡黄の小枠、タグ「日本語」)。スマホでは固定バーと一緒に常時見える。
- 内容: 現在点灯中の日本語群(`activeG`の`.jhl`のtextContent連結)。再生中=自動ハイライトに追従、停止中/一時停止中=クリック選択に追従、文間(jaHold)は直前を維持。
- null安全: 群なし/対応日本語なし/KP・Vocab再生中は空表示(タグも非表示)。枠は常に確保(min-height約2行)し、出現/消滅で本文がガタつかない。
- 長文: 折返し・`max-height:5.4em`・縦スクロール。サイズ14px(スマホ13.5px)。
- 既存仕様は無変更: 点灯ロジック/`selectSentence`/再生系/本文側日本語ブロックはそのまま。追加は`capUpdate()`(jaLight末尾とrender末尾から呼ぶのみ)。固定バー高さ変数`--bar-h`をON時に増やし本文が隠れないようにした(176px/スマホ168px)。
- 比較: ページ上部の黄色Trial帯に`キャプション: ON/OFF`ボタン(同一ページ内。`?caption=0|1`、既定ON)と`現行版(Production)を開く`リンク(同記事・同レベル)。
- Trial識別: build-id=`cap-trial-01`、`noindex`、帯表示。Production assetには混入しない。
