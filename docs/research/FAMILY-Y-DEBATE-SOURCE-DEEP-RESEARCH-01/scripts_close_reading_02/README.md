# scripts_close_reading_02(限定精読の集計script。CLOSE_READING_02.mdの数値の再現用)

- 入力(commitしない): `gd/head.bin`=Grand Debat `la-transition-ecologique.csv`のRange 0-3999、`gd/mid.bin`=同Range 3000000-4199999(1,200,000B)、`polis/at.csv`=compdemocracy/openData `austria-climate.5tzfrp5eaa.2022-07-07/comments.csv`(348,261B)。作業ディレクトリ(scratchpad)直下に置いて`py -3 -I <script>`で実行。
- gd_cols.py=設問列の確認 / gd_parse2.py=一人称+生活語の候補抽出 / gd_stats.py=カテゴリ別件数(正規表現による**粗い代理指標**。手読みの結果ではない)+具体例の出力 / polis_an.py・polis_an2.py=Polis自己開示の抽出。
- LLM呼出なし(Python標準ライブラリのみ)。取得は手動相当の単発HTTP GET。
