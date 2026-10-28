# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `4514a7ce9ecc7106` / 本文sha: `f456110d37df`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | shoving match | 激しい押し合い | The cliffs are a record of a huge "shoving match" cut into the Moon's surface | 押し合いの争いを表す、比喩的で生き生きした表現です。 |  |
| 2 | KP | under the same conditions | 同じ条件で | These numbers were not measured under the same conditions | 実験や比較で「同じ条件下で」を表す定型表現です。 |  |
| 3 | KP | hold heat in | 熱を逃がさない | What matters is how well it holds heat in | 熱を内部に保つ意味の句動詞表現です。 | 重複: 5 |
| 4 | 単語 | work out | 割り出す | Using the map, the team worked out how much the Moon had shrunk | 計算・検討して答えを導き出す句動詞です。 | 重複: 8 |
| 5 |  | insulation | 断熱材 | The team thinks a thick layer of rock with many gaps may have worked like insulation | 断熱材・断熱を表す、科学や建築で役立つ語です。 | 重複: 3 |
| 6 | 単語 | shrinkage | 縮み | The shrinkage we can see comes from the later part of the Moon's history | 縮小・収縮を表す名詞で、幅広い文脈で使えます。 |  |
| 7 |  | radius | 半径 | They estimated that its radius had become about 42 to 46 meters smaller | 半径を意味し、数学や科学の文脈で頻出します。 |  |
| 8 |  | estimate | だいたいの値を出す | They estimated that its radius had become about 42 to 46 meters smaller | 数値や規模を推定する際に使う学術的な語です。 | 重複: 4 |
| 9 |  | fault | 断層 | It was left by faults that formed fairly recently | 地質学の断層や一般的な欠陥を表す語です。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level a2 --accept-ai --candidates-sha 4514a7ce9ecc7106775fd2dbf4390fdafda6095d41b5dd636c55ec71c7831008 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
