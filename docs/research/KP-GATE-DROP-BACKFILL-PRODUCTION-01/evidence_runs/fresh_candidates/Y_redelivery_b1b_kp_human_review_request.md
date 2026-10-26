# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `884db644d8d98c16` / 本文sha: `f4f19da3217a`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | doesn't sit right with someone | 人には納得がいかない | Having to pay for redelivery just doesn't sit right with me |  | 修正済み(元: doesn't sit right with me / REDERIVE_M1_WINDOW)・QA再判定済み |
| 2 | KP | take the trouble | わざわざ手間をかける | Still, I take the trouble to think about how to receive my packages, so honestly, I think it's wrong that I pay the same fee as people who are always away and ask for redelivery |  |  |
| 3 | KP | can't be helped | 仕方がない | The delivery workers must have a hard time because there aren't enough of them, and I guess it can't be helped |  |  |
| 4 | 単語 | on top of | 〜に加えて | Charging for redelivery means the person receiving the package pays a fee on top of the usual shipping cost | 「〜に加えて」を表す慣用的な前置詞表現です。 |  |
| 5 | 単語 | take up | 占める | Redelivery takes up the delivery worker's time, so it's fine to charge for it | 時間や場所を「費やす・占める」を表す句動詞です。 |  |
| 6 |  | end up receiving | 結局受け取ることになる | And even when I ask for a package to be sent to a delivery office, it may arrive late, so I sometimes end up receiving it in person after all | 「結局〜を受け取ることになる」という結果を表します。 |  |
| 7 |  | beforehand | あらかじめ | There are also many packages where you can't choose a time, and you don't know beforehand when they'll arrive | 「事前に」を表す、簡潔で使い勝手のよい副詞です。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01 --level b1b --accept-ai --candidates-sha 884db644d8d98c164e4bf77be89d4a51a62e68a496f04e5b0cfdf5dc8e6eea3e --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
