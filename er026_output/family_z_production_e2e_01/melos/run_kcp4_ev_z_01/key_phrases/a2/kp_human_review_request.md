# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `e7791e333a7d8c64` / 本文sha: `efba2a233a8a`
- あなたの作業: KPに使う最大3件を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | pull someone under | 人を水中に引き込む | The water pulled him under, but he fought toward the light | 「水中に引きずり込む」を表す句動詞です。 |  |
| 2 | KP | without asking for another promise | さらに約束を求めずに | His friend trusted him without asking for another promise | without asking for の自然な用法と含意を学べます。 |  |
| 3 | KP | lose one's trust in someone | 自分が誰かを信じる気持ちを失う | I almost lost my trust in you," his friend replied | lose trust in の語法と信頼を失う表現が学べます。 |  |
| 4 |  | win such trust | そのような信頼を得る | More softly, he then asked, "How can a man win such trust | win trust の自然なコロケーションが学べます。 | 修正済み(元: win such trust / REVERT_SURFACE)・QA再判定済み |
| 5 |  | demand | 強く求める | For once, he waited for a reply instead of demanding one | 要求するという意味で、議論や交渉など幅広い文脈で使えます。 |  |
| 6 |  | shepherd | 羊の世話をする人 | Silence came, and guards grabbed the young shepherd | 牧羊をする人を指す語で、物語や歴史の文脈で役立ちます。 |  |
| 7 |  | Silence | 沈黙 | Silence came, and guards grabbed the young shepherd | 単なる無音だけでなく、発言のない状態も表せます。 |  |
| 8 |  | exact | 正確な | Melos listened closely to remember its exact sound | 細部まで正確であることを表し、幅広い名詞と組み合わせます。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/melos/run_kp75_ev_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/melos/run_kp75_ev_01 --level a2 --accept-ai --candidates-sha e7791e333a7d8c64a0b71ce6a0440d2c53ed4cce36c255661f94ffe1e72e5b18 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/melos/run_kp75_ev_01 --level a2 --kp 1,2,3 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er026_output/family_z_production_e2e_01/melos/run_kp75_ev_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/melos/run_kp75_ev_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
