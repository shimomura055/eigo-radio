# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `c5dfc27410d4fd6e` / 本文sha: `54ab9a6db4b1`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。
- Gate除外 1件(フレーズ0・単語1)に対し、補完候補 1件を末尾に追加しました(補完status: OK)

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | talk someone into staying | 誰かを説得して残ってもらう | His mother welcomed Yuki and talked her into staying | 「人を説得して〜させる」を表す句動詞の型。 |  |
| 2 | KP | get what you deserve | 自分にふさわしい報いを受ける | If they ever have reason to complain about you, you will get what you deserve | 当然の報いを受ける、という慣用表現。 |  |
| 3 | KP | slip away | こっそり立ち去る | Then she slipped away through the smoke-hole in the roof | 気づかれないように立ち去る含みのある句動詞。 |  |
| 4 | 単語 | riverside | 川沿いの | They could not continue, so they entered a riverside hut | 川辺を表す複合語で、場所の描写に幅広く使えます。 |  |
| 5 | 単語 | mist | 霧 | She melted into white mist and rose towards the roof beams | 霧やもやを指し、天候や情景描写で役立ちます。 |  |
| 6 |  | light-skinned | 色白の | Yuki became Minokichi's wife, and they later had ten light-skinned children | 肌の色が薄いことを表す形容詞で、人の描写に使えます。 |  |
| 7 |  | complain | 文句を言う | If they ever have reason to complain about you, you will get what you deserve | 不満を表明する意味で、幅広い場面で使える動詞です。 | 補完候補(Gate除外の代替) |

## Gateで除外された候補(参考)

- woodcutters : cmu : CMU発音辞書に登録されていない語を含む(未登録語: woodcutters。構成する全ての語がCMU辞書に登録された語句だけを選ぶ)

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01 --level a2 --accept-ai --candidates-sha c5dfc27410d4fd6e85bd638a6fe09845de1c787028ad842e2ff9570b31b81cdf --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01 --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
