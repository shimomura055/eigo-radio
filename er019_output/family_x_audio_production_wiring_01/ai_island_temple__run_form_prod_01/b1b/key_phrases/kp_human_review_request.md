# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `5d8c1b12f01b0de9` / 本文sha: `00f14092c072`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | carry over | 次に持ち越す | In the experiment, the island and the conversation were reset every hour, but the work area where the AI kept notes and programs was carried over | 情報や作業を次の期間へ引き継ぐ句動詞。 | 重複: 10 |
| 2 | KP | call on | 頼む | So, would that experience help the AI the next time it was called on | 人やシステムを必要な場面で呼び出す表現。 |  |
| 3 | KP | look at separately | 別々に検討する | The fact that the experienced group did better and the fact that removing a particular memory lowered its score need to be looked at separately | 論点を分けて検討する際に使える表現。 |  |
| 4 | 単語 | take a detour | 遠回りをする | The ones that had taken a detour were now one step ahead | 本筋から外れて寄り道することを表す比喩。 |  |
| 5 | 単語 | card to play | 打てる手 | A discovery that is no use right now might become a useful card to play next time, if it is saved | 使える手段や切り札を表す比喩表現。 |  |
| 6 |  | exploration | いろいろ探ること | They had no homework, but they were in exploration mode | 探究・開拓などを表す、幅広い文脈で使える名詞です。 |  |
| 7 |  | technique | やり方 | The researchers also removed a description of a technique for "throwing rocks to get more blocks" from one AI's memory | 技法や手法を指し、学術・実務の両方で役立ちます。 |  |
| 8 |  | overlook | 見過ごす | One tip in the strategy notes was not something to overlook | 「見落とす」の意味で使える汎用性の高い動詞です。 |  |
| 9 |  | obstacle | 障害物 | Then one AI started an obstacle course of its own | 障害や困難を表す、比喩的にも使いやすい語です。 |  |
| 10 |  | erase | 消し去る | The island went back to how it was before, but what the AI had discovered was not erased | 「消去された」を表す動詞の過去分詞形です。 | 重複: 1 |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kp75_ev_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kp75_ev_01 --level b1b --accept-ai --candidates-sha 5d8c1b12f01b0de9265721152da508e7f8f7afb1f7f126d5d461a835457d87f9 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kp75_ev_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kp75_ev_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kp75_ev_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
