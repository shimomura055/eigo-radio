# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `4fe2e139af67acfc` / 本文sha: `76f80f62120b`
- あなたの作業: KPに使う最大3件を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | carry over | 持ち越される | But the work area with the AI's notes and programs carried over to the next hour |  |  |
| 2 | KP | take a detour | 寄り道をする | Those that had taken a detour were now one step ahead |  |  |
| 3 | KP | a useful card to play | 使える一手 | A discovery that is not useful now might be a useful card to play next time, if it is saved |  |  |
| 4 |  | one step ahead | 一歩先を行く | Those that had taken a detour were now one step ahead | 「一歩先を行く」という優位性を表す定番の比喩表現です。 |  |
| 5 |  | study separately | 別々に検討する | These two results need to be studied separately | 複数の要素を個別に検討する際に使う学術的な表現です。 |  |
| 6 |  | worth paying attention to | 気に留める価値がある | One tip in the strategy notes was worth paying attention to | 注目する価値があることを示す自然な定型表現です。 |  |
| 7 |  | obstacle course | 障害物のあるコース | Then one AI made its own obstacle course | 障害物を越えて進むコースを指す複合語です。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kpbf_ev_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kpbf_ev_01 --level a2 --accept-ai --candidates-sha 4fe2e139af67acfc84cd56bdb91755f3cd0ceaeb0e4082672629d8f53513134b --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kpbf_ev_01 --level a2 --kp 1,2,3 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kpbf_ev_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kpbf_ev_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
