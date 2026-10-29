# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `24da1af1ea100143` / 本文sha: `0bb1b74418b6`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | pore over | じっくり調べる | It's certainly nice not to have to pore over a price list | 資料などを細かく注意深く読む表現。 |  |
| 2 | KP | make room for | ～のために時間を作る | The appeal of AI pets for adults may lie less in how many things they can do and more in whether you want to make room for one in the gaps of a busy day | 時間や余地を確保する際に使う表現。 |  |
| 3 | KP | by the time of reporting | 報道時点までに | When it will become available in Japan and other places had not been announced by the time of reporting | 報道時点を示す記事で使える表現。 |  |
| 4 | 単語 | on the scale of | ～並みの規模で | Whether it will become a craze on the scale of Tamagotchi is still an open question | 規模を比較する際に使う語句。 |  |
| 5 | 単語 | an open question | まだ答えが出ていない問題 | Whether it will become a craze on the scale of Tamagotchi is still an open question | まだ答えが出ていない問題を表す。 |  |
| 6 |  | in the gaps | ちょっとした空き時間に | The appeal of AI pets for adults may lie less in how many things they can do and more in whether you want to make room for one in the gaps of a busy day | 忙しい日々の合間を指す表現。 |  |
| 7 |  | subscription | 定額制の契約 | It is free in the app stores, and its official website says there is no subscription either | 定期購読・定額契約を表す、幅広い場面で使える語。 |  |
| 8 |  | latter | 後者 | However, the latter is not a rule about who can use the app | 前に挙げた二つのうち「後者」を指す重要な文章語。 |  |
| 9 |  | craze | 大流行 | Whether it will become a craze on the scale of Tamagotchi is still an open question | 一時的に大流行するものを表す、ニュアンスのある名詞。 |  |
| 10 |  | appeal | 魅力 | The appeal of AI pets for adults may lie less in how many things they can do and more in whether you want to make room for one in the gaps of a busy day | 魅力や訴求力を表し、幅広い文脈で使える語。 |  |
| 11 |  | usefulness | 役に立つ度合い | When it comes to usefulness, you can compare features side by side | 有用性を表す名詞で、抽象的な議論にも使える。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01 --level b1b --accept-ai --candidates-sha 24da1af1ea100143f3660581f0b7eab0354ead2744f51f41f243bcb626e5faf9 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
