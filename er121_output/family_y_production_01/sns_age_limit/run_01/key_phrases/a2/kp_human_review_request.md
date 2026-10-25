# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `3f79580a85869463` / 本文sha: `d22a671a92d5`
- あなたの作業: KPに使う最大3件を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | draw a line | 線を引く | Rather than draw a line based only on age, I think it would be better, if possible, to let them use more features step by step as they learn to handle them |  |  |
| 2 | KP | bring up another question | 別の疑問を持ち出す | Setting an age when children can use social media also brings up another question: how much can they turn to adults after they start |  |  |
| 3 | KP | thrown into it | その状況に放り込まれる | Just as you need to practice swimming before going into the sea, it's still scary when a child who isn't ready is suddenly thrown into it |  |  |
| 4 |  | turn to adults | 大人に頼る | Setting an age when children can use social media also brings up another question: how much can they turn to adults after they start | 助けを求めて人に頼る意味の句動詞です。 |  |
| 5 |  | a say in | ～について意見を言う権利 | I want a say in what I can use and how I use it | 物事への発言権や決定への関与を表します。 |  |
| 6 |  | happen to like | たまたま気に入る | I don't think it's okay to let them use anything they happen to like | 「たまたま好きである」という構文です。 |  |
| 7 |  | put two things together | 二つのことを両立させる | It is hard to put two things together: choosing how to use social media, and going to adults when something goes wrong | 二つの事柄を結びつけて考える表現です。 |  |
| 8 |  | safety filter | 危険な情報を防ぐフィルター | Instead of giving everyone the same limits because of their age, I think we can do other things, like set safety filters | 安全機能を指す、実用的な複合語です。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/sns_age_limit/run_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/sns_age_limit/run_01 --level a2 --accept-ai --candidates-sha 3f79580a85869463fe4b28cdad99def18b02765dd4cbf56a5720a5b0aa00d163 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/sns_age_limit/run_01 --level a2 --kp 1,2,3 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er121_output/family_y_production_01/sns_age_limit/run_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/sns_age_limit/run_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
