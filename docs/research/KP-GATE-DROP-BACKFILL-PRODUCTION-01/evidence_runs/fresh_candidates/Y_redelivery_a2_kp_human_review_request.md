# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `cd8c2c18b6ab8b9c` / 本文sha: `c415df6b554b`
- あなたの作業: KPに使う最大3件を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。
- Gate除外 1件(フレーズ1・単語0)に対し、補完候補 1件を末尾に追加しました(補完status: OK)

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | can't be helped | 仕方がない | I guess it can't be helped |  |  |
| 2 | KP | end up getting | 結局受け取ることになる | So sometimes I end up getting it in person after all |  |  |
| 3 | KP | take up | 時間を取る | Redelivery takes up the delivery worker's time, so charging for it is fine |  |  |
| 4 |  | when it suits someone | 誰かの都合がいいときに | It is handy to pick them up when it suits me | 「自分の都合に合うとき」を表す自然な定型表現。 |  |
| 5 |  | take the time | 時間をかける | Still, I take the time to think about how to get my packages | 時間をかけて何かをする際に使える自然な連語。 |  |
| 6 |  | make an effort | 努力する | For people who can choose how to get packages, a redelivery fee can be a sign that encourages them to make an effort | 努力することを表す、幅広く使える熟語。 |  |
| 7 |  | have a hard time | 苦労する | Delivery workers must have a hard time because there are not enough of them | 「苦労する」を表す、会話でもよく使われる定型表現です。 | 補完候補(Gate除外の代替) |

## Gateで除外された候補(参考)

- as it is : validate : 有限助動詞を含む(既存canonicalization Validatorが拒否する形)
- redelivery fee : cmu : CMU発音辞書に登録されていない語を含む(未登録語: redelivery。構成する全ての語がCMU辞書に登録された語句だけを選ぶ)
- make more sense than : validate : 本文に連続一致しない(変更・言い換え・創作)

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01 --level a2 --accept-ai --candidates-sha cd8c2c18b6ab8b9c9082c7e4535147778e4bf9b59d14191b3d1a4d86db7f3f69 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01 --level a2 --kp 1,2,3 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
