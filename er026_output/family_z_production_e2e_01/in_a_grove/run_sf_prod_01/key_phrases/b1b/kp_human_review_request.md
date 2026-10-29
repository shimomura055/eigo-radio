# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `941647eb453de90d` / 本文sha: `ee5433934163`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | cold contempt | 冷ややかな軽蔑 | But his eyes held nothing except cold contempt | 「冷ややかな軽蔑」を表す印象的な語の組み合わせ。 |  |
| 2 | KP | The thicket fell silent | 茂みが静まり返る | The thicket fell silent | 場所を主語にした、文学的な擬人表現。 |  |
| 3 | KP | on soft feet | 忍び足で | Then someone crept towards me on soft feet | 「足音を立てずに」を表す文学的な言い回し。 |  |
| 4 | 単語 | sink for ever | 永遠の眠りにつく | I sank for ever into the darkness | 「永遠に沈んだ」という余韻のある文学的表現。 |  |
| 5 | 単語 | trampled | 踏みつけられた | The broken bamboo and trampled earth showed a struggle | 踏み荒らす意味を持つ、描写に役立つ動詞です。 |  |
| 6 |  | constable | 警官 | I caught Tajomaru, the famous bandit, by the stone bridge," said the constable | 警察官を指す語で、英語圏の制度理解にも役立ちます。 |  |
| 7 |  | veiled | ベールで覆われた | His wife rode beside him, her face veiled | 「覆われた」から「隠された」まで表せる語です。 |  |
| 8 |  | seize | ぐっとつかむ | Then she seized my arm | 「つかむ・奪う」など幅広い場面で使われます。 |  |
| 9 |  | medium | 霊媒師 | I heard the bandit comforting her," said Takehiro's spirit through the medium | 霊媒を指す意味を含む、多義的で汎用性のある語です。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level b1b --accept-ai --candidates-sha 941647eb453de90d41fdced487cf47ed28a4065bb782f43dd206f75a0ad2bee4 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
