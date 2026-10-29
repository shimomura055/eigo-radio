# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `df69c2469a1585cb` / 本文sha: `975c98267084`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 |  | taking offense | 気を悪くする | I was grateful that both sets of parents accepted my decision without taking offense | 「気分を害する」という意味の慣用表現。 | 修正済み(元: taking offense / REVERT_SURFACE) / AUTO対象外 |
| 2 | KP | let go of | 手放す | I need to let go of my son, don't I | 人や物への執着を手放す句動詞。 | 重複: 3,6 |
| 3 |  | hold one's son back | 人の息子の足を引っ張る | Even so, I don't want to hold my son back because of my feelings as a parent | 人の行動を妨げる句動詞の用例。 | 重複: 2 |
| 4 | KP | at ease | 気持ちが楽で | Once I could accept that of course we were different, I felt much more at ease | 安心してくつろいだ状態を表す表現。 |  |
| 5 | KP | way out in the country | かなり田舎のほうに | My parents accepted it easily, even though my hometown is way out in the country | 「かなり田舎に」を表す口語的な表現。 |  |
| 6 |  | give something up | 何かをあきらめる | In a conversation about last names, perhaps a person's own choice overlaps with the feeling that a parent is giving something up | 何かを手放すことを表す句動詞。 | 重複: 2 |
| 7 | 単語 | overlap with | 〜と重なり合う | In a conversation about last names, perhaps a person's own choice overlaps with the feeling that a parent is giving something up | 考えや感情が重なることを表す動詞表現。 |  |
| 8 | 単語 | registration | 届け出 | Whether a husband chooses his wife's last name on the marriage registration form or joins her family as an adopted son, he and each of their families have their own feelings | 公的な登録手続きに関わる語で、幅広く使えます。 |  |
| 9 |  | grateful | ありがたく思う | I was grateful that both sets of parents accepted my decision without taking offense | 感謝の気持ちを表す、汎用性の高い形容詞です。 |  |
| 10 |  | Alongside | 〜に加えて | Alongside the couple's decision about their last name, there are feelings that parents want to share with the other parents | 「〜と並んで」を表し、文章で使いやすい語です。 |  |
| 11 |  | adopted | 養子になった | Whether a husband chooses his wife's last name on the marriage registration form or joins her family as an adopted son, he and each of their families have their own feelings | 養子縁組など、文脈に応じた意味を学べます。 |  |
| 12 |  | adjust | 慣れる | I still find it a little hard that I don't get much time to myself while living at my wife's parents' home, but adjusting to the way each family does things was harder than changing my last name | 状況や環境に順応することを表す語です。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/surname_choice/run_02`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/surname_choice/run_02 --level b1b --accept-ai --candidates-sha df69c2469a1585cb5e532a8a8a7f9a745b26be29a60e3831149514f16c99a51f --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/surname_choice/run_02 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er121_output/family_y_production_01/surname_choice/run_02 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/surname_choice/run_02 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
