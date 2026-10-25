# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `208f5fd0764db2d9` / 本文sha: `5ca8fb080f9d`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | draw the line | 線を引く | Rather than drawing the line by age alone, I think it would be better, if possible, for the features they can use to grow step by step as they become able to handle more |  |  |
| 2 | KP | take someone's use into account | 人の使い方を考えに入れる | I want the approach to change so it takes our use into account, without even stopping us from keeping in touch with friends |  |  |
| 3 | KP | fit neatly together | うまくかみ合う | The freedom to decide how to use social media and turning to adults when something goes wrong do not fit neatly together |  |  |
| 4 | 単語 | raise the question of | 〜という疑問を投げかける | The question of setting an age when children are allowed to use social media also raises the question of how much they can turn to adults after they start | 議論や検討すべき問題を提起する際に使う表現。 |  |
| 5 | 単語 | turn to an adult | 大人を頼る | If people say bad things about me or threaten me, I'd still want to turn to an adult right away | 困ったときに大人を頼る、という意味の句動詞表現。 |  |
| 6 |  | thrown into it | その状況に放り込まれる | Just as you need to practice swimming before going into the sea, it's still scary when a child who isn't ready is suddenly thrown into it | 準備のないまま状況に放り込まれることを表す比喩表現。 | QA FAIL(採用には --accept-qa-fail) / AUTO対象外 |

## Gateで除外された候補(参考)

- have a say : validate : 有限助動詞を含む(既存canonicalization Validatorが拒否する形)
- catch their interest : validate : 本文に連続一致しない(変更・言い換え・創作)

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/sns_age_limit/run_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/sns_age_limit/run_01 --level b1b --accept-ai --candidates-sha 208f5fd0764db2d93df8d5a26873aaf48f9beb1766f5820883c761d4bd01b629 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/sns_age_limit/run_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er121_output/family_y_production_01/sns_age_limit/run_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/sns_age_limit/run_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
