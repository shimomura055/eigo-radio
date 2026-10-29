# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `57b998cd0c3446db` / 本文sha: `2c4b13c306f5`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | hold someone's son back | 人の息子の足を引っ張る | Even so, I don't want my feelings as a parent to hold my son back | 「人の行動を妨げる」という意味の句動詞です。 | 重複: 7 |
| 2 | KP | fit in with | ～に合わせる | But fitting in with what each family thought was normal was harder than changing my last name | 周囲の考えや慣習に合わせる意味で使います。 |  |
| 3 | KP | go in opposite directions | 互いに相反している | Thanks for accepting his choice and thanks for changing his name go in opposite directions | 物事が正反対の方向を示す比喩表現です。 |  |
| 4 | 単語 | only natural | ごく自然なこと | But if it were my son, it would still bother me if his partner's parents thought it was only natural | 当然だ、自然なことだという意味の慣用表現です。 |  |
| 5 | 単語 | at ease | 気持ちが楽な | Once I accepted that things could be different, I felt much more at ease | 緊張や不安がなく、気楽な状態を表します。 |  |
| 6 |  | hesitate | ためらう | I did not hesitate at all about changing my last name | 判断をためらう意味で幅広く使える動詞。 |  |
| 7 |  | oppose | 反対する | If my son made that choice, I wouldn't oppose him | 意見や提案に反対することを表す動詞。 | 重複: 1 |
| 8 |  | grateful | 感謝している | I want them to feel at least a little grateful to my son | 感謝している気持ちを表す重要な形容詞。 |  |
| 9 |  | adoption | 養子縁組 | This does not mean adoption | 養子縁組などを表す汎用性のある名詞。 |  |
| 10 |  | relative | 親戚 | Last is someone from the parents' generation whose relative chose his wife's last name | 親族を意味し、日常的に使える名詞。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/surname_choice/run_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/surname_choice/run_01 --level a2 --accept-ai --candidates-sha 57b998cd0c3446db1abdfcf770e2d4b0be4eaba92b5a2203db4eba19d144a242 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/surname_choice/run_01 --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er121_output/family_y_production_01/surname_choice/run_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/surname_choice/run_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
