# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `f48b52514ec54408` / 本文sha: `8ec5e76f9381`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。
- Gate除外 1件(フレーズ0・単語1)に対し、補完候補 1件を末尾に追加しました(補完status: OK)

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | through a medium | 霊媒を通して | I heard him speaking kindly to her," Takehiro's spirit said through a medium | 霊媒を介して意思を伝える表現です。 |  |
| 2 | KP | on silent feet | 足音を立てずに | Someone came slowly towards me on silent feet | 足音を立てずに進む様子を表す文学的表現です。 |  |
| 3 | KP | sink into the darkness | 死の闇へ沈んでいく | I sank into the darkness and never came back | 闇へ沈むように消えていく詩的な言い回しです。 |  |
| 4 | 単語 | constable | 警官 | I caught the famous bandit Tajomaru near the bridge," the constable said | 警察官を指すやや改まった語で、報道などでも使われる。 |  |
| 5 | 単語 | drown | 溺れる | I later tried drowning myself, but I failed | 「溺れること」を表し、事故や救助の文脈で使える。 |  |
| 6 |  | dagger | 短剣 | She fought with her dagger | 短剣を指す語で、歴史・物語の描写に使われる。 |  |
| 7 |  | bandit | 盗賊 | I caught the famous bandit Tajomaru near the bridge," the constable said | 物語や歴史の文脈で幅広く使われる語です。 | 補完候補(Gate除外の代替) |

## Gateで除外された候補(参考)

- woodcutter : cmu : CMU発音辞書に登録されていない語を含む(未登録語: woodcutter。構成する全ての語がCMU辞書に登録された語句だけを選ぶ)

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level a2 --accept-ai --candidates-sha f48b52514ec544083dbdb0b3e4006c41fa2ad707f7b97065d180fef577f79344 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
