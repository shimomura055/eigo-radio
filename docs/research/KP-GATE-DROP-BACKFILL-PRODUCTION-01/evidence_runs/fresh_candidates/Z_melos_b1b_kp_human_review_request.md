# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `01dbdbf328ea04c4` / 本文sha: `03b3787d1c4e`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | sentence someone to death | 誰かに死刑を言い渡す | Then the guards seized the young shepherd, and the ruler sentenced him to death |  |  |
| 2 | KP | hold out one's hands | 自分の手を差し出す | Melos turned to his friend, but before he could speak, his friend held out his hands for the chains |  |  |
| 3 | KP | abandon someone | 誰かを見捨てる | I nearly abandoned you," he whispered |  |  |
| 4 | 単語 | pull someone under | 誰かを水中に引きずり込む | The current pulled him under | 「引きずり込む」という句動詞の意味と用法を学べる。 |  |
| 5 | 単語 | earn such trust | これほどの信頼を勝ち取る | Then, more quietly, he asked, "How does a man earn such trust | 「信頼を得る」という自然な語の組み合わせ。 |  |
| 6 |  | execution bell | 処刑を知らせる鐘 | At the city gates, the execution bell rang | 「処刑」を表すexecutionの語義を確認できる。 |  |
| 7 |  | seize | 捕らえる | Then the guards seized the young shepherd, and the ruler sentenced him to death | 「つかむ・拘束する」を表す硬めの動詞。 |  |
| 8 |  | ring through the hall | 広間に響き渡る | Melos's voice rang through the hall | 音が空間に響き渡る様子を表す表現。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01 --level b1b --accept-ai --candidates-sha 01dbdbf328ea04c41203c93ef149d391ac487d59856baa40059f29489d15f925 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
