# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `7718064b1272e528` / 本文sha: `efba2a233a8a`
- あなたの作業: KPに使う最大3件を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。
- Gate除外 1件(フレーズ1・単語0)に対し、補完候補 1件を末尾に追加しました(補完status: OK)

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | pull someone under | 誰かを水中に引きずり込む | The water pulled him under, but he fought toward the light |  |  |
| 2 | KP | block someone's way | 誰かの行く手をさえぎる | Later, three men blocked his way, and a knife flashed |  |  |
| 3 | KP | lose one's trust in someone | 人が誰かへの信頼を失う | I almost lost my trust in you," his friend replied |  |  |
| 4 |  | hold out | 差し出す | He remembered the hands held out for the chains | 手などを差し出す意味の句動詞です。 |  |
| 5 |  | For once | 今回に限って | For once, he waited for a reply instead of demanding one | 「今回ばかりは」を表す自然な慣用表現です。 |  |
| 6 |  | win such trust | そのような信頼を勝ち取る | More softly, he then asked, "How can a man win such trust | 信頼を得ることを表す win の用法が学べます。 |  |
| 7 |  | a knife flashed | ナイフが一瞬きらりと光った | Later, three men blocked his way, and a knife flashed | flashが「一瞬きらめく・現れる」を表す文学的用法。 | 補完候補(Gate除外の代替) |

## Gateで除外された候補(参考)

- in his place : validate : 本文に連続一致しない(変更・言い換え・創作)

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01 --level a2 --accept-ai --candidates-sha 7718064b1272e528cc77a86f622df9c56dd66cb80198f1c3db7958ce8b67eac7 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01 --level a2 --kp 1,2,3 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
