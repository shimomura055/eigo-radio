# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `c5e4d43e600b6945` / 本文sha: `03b3787d1c4e`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | sentence someone to death | 誰かに死刑を言い渡す | Then the guards seized the young shepherd, and the ruler sentenced him to death |  |  |
| 2 | KP | pull someone under | 誰かを水中に引きずり込む | The current pulled him under |  |  |
| 3 | KP | earn such trust | これほどの信頼を得る | Then, more quietly, he asked, "How does a man earn such trust | 「信頼を得る」を表す自然なコロケーションです。 |  |
| 4 | 単語 | execution | 処刑 | At the city gates, the execution bell rang | 処刑を意味する、法律・ニュースで使われる語です。 |  |

## Gateで除外された候補(参考)

- rose above : canonicalization : key_phrase('rise above the other voices')がdisplay_phraseと一致せず、source_span('rose above')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)
- held out : canonicalization : key_phrase("hold out one's hands")がdisplay_phraseと一致せず、source_span('held out')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3 --level b1b --accept-ai --candidates-sha c5e4d43e600b69455f9210984ec8d8bc3742acbb8fdb5563dc6bee85fb524107 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
