# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `3592d9c46608c9e3` / 本文sha: `00f14092c072`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | carry over | 次の段階に引き継ぐ | In the experiment, the island and the conversation were reset every hour, but the work area where the AI kept notes and programs was carried over |  |  |
| 2 | KP | look at separately | 分けて考える | The fact that the experienced group did better and the fact that removing a particular memory lowered its score need to be looked at separately |  |  |
| 3 | KP | a useful card to play | 役に立つ手札 | A discovery that is no use right now might become a useful card to play next time, if it is saved |  |  |
| 4 | 単語 | call on | 人に頼む | So, would that experience help the AI the next time it was called on | 人や機械が役割を求められる意味の句動詞です。 |  |
| 5 | 単語 | not something to overlook | 見過ごせないこと | One tip in the strategy notes was not something to overlook | 見過ごすべきでない重要性を表す自然な言い回しです。 |  |
| 6 |  | take a detour | 寄り道をする | The ones that had taken a detour were now one step ahead | 本筋から外れることを比喩的に表す表現です。 |  |
| 7 |  | one step ahead | 一歩先を行く | The ones that had taken a detour were now one step ahead | 他者より有利な立場にあることを表す慣用表現です。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kpbf_ev_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kpbf_ev_01 --level b1b --accept-ai --candidates-sha 3592d9c46608c9e3c537c740f5e31c8999ae62862568a53528b02697464a1dba --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kpbf_ev_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kpbf_ev_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kpbf_ev_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
