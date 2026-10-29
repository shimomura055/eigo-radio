# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `a891b830b2b97a04` / 本文sha: `821e940c2738`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | go in opposite directions | 正反対の方向を向いている | Thanks for accepting his decision and thanks for changing his last name go in opposite directions | 意見や利害が正反対であることを比喩的に表す。 |  |
| 2 | KP | hold one's son back | 人の息子の足を引っ張る | Even so, I don't want my feelings as a parent to hold my son back | 人の行動や前進を妨げる句動詞の用法を学べる。 |  |
| 3 | KP | talk it over | それについてよく話し合う | I know a relative who took his wife's last name without first talking it over with his parents | 相談して決めることを表す自然な口語表現。 |  |
| 4 | 単語 | time to oneself | 自分だけの時間 | Living at my wife's parents' home, I still find it a little hard that I have so little time to myself | 一人で過ごす時間を表す定着した言い回し。 |  |
| 5 | 単語 | only natural | ごく当然のこと | But if it were my son, it would still bother me if his partner's parents thought it was only natural | 「当然のこと」という意味になる自然な組み合わせ。 |  |
| 6 |  | at ease | 気が楽な | Once I could accept that it was normal for things to be different, I felt much more at ease | 安心してくつろいだ状態を表す慣用表現。 |  |
| 7 |  | hesitation | ためらい | I had no hesitation at all about changing my last name | ためらいや迷いを表す名詞で、幅広い場面で使えます。 |  |
| 8 |  | rural | 田舎の | My parents' home is in a pretty rural place, but they don't have old-fashioned views, and they accepted it easily | 「田舎の」を表す語で、地域や暮らしの描写に役立ちます。 |  |
| 9 |  | adoption | 養子縁組 | It does not involve adoption | 「養子縁組」を表す名詞で、制度や家族の話題で使えます。 |  |
| 10 |  | generation | 世代 | Last is someone from the parents' generation whose relative chose his wife's last name | 「世代」を表し、社会や家族の変化を論じる際に使えます。 |  |
| 11 |  | grateful | 感謝している | I was grateful that both sets of parents accepted my decision without being upset | 感謝している状態を表す形容詞で、気持ちを的確に伝えます。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/surname_choice/run_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/surname_choice/run_01 --level b1b --accept-ai --candidates-sha a891b830b2b97a040d1beb08c4f87227e5c4ffacf94249dfddc5097519f6940c --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/surname_choice/run_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er121_output/family_y_production_01/surname_choice/run_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/surname_choice/run_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
