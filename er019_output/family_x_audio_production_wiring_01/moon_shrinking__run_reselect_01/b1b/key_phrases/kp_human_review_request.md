# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `0ccf949d713a7b74` / 本文sha: `bb726361e196`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | way off | 大きく外れている | Does that mean the calculations are way off | 「大きく外れている」を表す口語的なイディオムです。 |  |
| 2 | KP | under the same conditions | 条件をそろえて | These aren't figures measured under the same conditions | 研究結果を比較する際によく使う学術的な表現です。 |  |
| 3 |  | keeps heat from escaping | 熱が逃げないようにする | Just as insulation in a house keeps heat from escaping, this layer may have made it harder for heat inside the Moon to escape | keep A from doing の構文と熱の保持を表す語法を学べます。 | 重複: 9 / 修正済み(元: keeps heat from escaping / REVERT_SURFACE) / AUTO対象外 |
| 4 | KP | total amount of shrinkage | 縮んだ量の合計 | This is not the total amount of shrinkage from its birth to today | 変化の総量を述べる際に使える科学分野の語句です。 |  |
| 5 | 単語 | over its entire history | 始まりから終わりまでずっと | On the other hand, models that calculate the Moon's cooling over its entire history predict much greater shrinkage | 対象の全歴史にわたる範囲を示す自然な表現です。 |  |
| 6 | 単語 | relatively recent faults | 比較的新しい断層 | What we are looking at is shrinkage in the later part of the Moon's history, left by relatively recent faults | 地質学的な時間の新旧を示す専門的な語の組み合わせです。 |  |
| 7 |  | One possible explanation | 考えられる説明の一つ | One possible explanation is a layer of broken rock | 断定を避けて仮説を示す学術的な言い回しです。 | 重複: 10 |
| 8 |  | porous | 小さな穴やすき間が多い | This is not the Moon's total shrinkage since formation, and a thick, porous rock layer may have slowed cooling, offering one possible explanation for the larger model predictions | 物質の多孔性を表す汎用性の高い形容詞です。 |  |
| 9 |  | insulation | 熱を逃がしにくくするもの | The research team suggests that a thick layer of rock full of gaps may have worked like insulation | 断熱材や絶縁を幅広い文脈で表せます。 | 重複: 3 |
| 10 |  | culprit | 原因 | But it is too soon to end the mystery by saying, "The coat is the culprit | 問題の原因や犯人を指す便利な語です。 | 重複: 7 |
| 11 |  | radius | 中心から外側までの長さ | Using this map to work out how much the Moon has shrunk, the team estimated that its radius had become about 42 to 46 meters smaller | 数学や科学で使われる重要な専門語です。 |  |
| 12 |  | puzzling | 理解しにくい | Still, the difference is puzzling | 不可解な状況や問題を表す形容詞です。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level b1b --accept-ai --candidates-sha 0ccf949d713a7b74f7a6827e05a05db3a330b73ddc826e2be22eba8b733e97fc --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
