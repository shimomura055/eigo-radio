# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `761026a5e726ba64` / 本文sha: `6aa5c86dd0d6`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | through a medium | 霊媒を通して | I heard the bandit trying to comfort her," Takehiro's spirit said through a medium | mediumが霊媒を指す用法を学べる。 |  |
| 2 | KP | sink into darkness | 命が尽きる | Then I sank into darkness and stayed there for ever | 暗闇へ沈むという文学的な比喩表現。 |  |
| 3 | KP | couldn't bear | 我慢できなかった | I stabbed him because I couldn't bear those eyes | bearが「耐える」を表す自然な用法。 |  |
| 4 | 単語 | fight fairly | 正々堂々と戦う | I untied him, and we fought fairly with swords | fairlyが「正々堂々と」の意味で使われる。 |  |
| 5 |  | lasted twenty-three strokes | 二十三回の斬撃に耐え抜く | He lasted twenty-three strokes, but nobody else had reached twenty | lastが戦いの中で「持ちこたえる」を表す。 | 修正済み(元: lasted twenty-three strokes / REVERT_SURFACE) / AUTO対象外 |
| 6 | 単語 | constable | 警官 | I caught Tajomaru, the famous bandit," the constable said | 警察官を表すやや格式のある語で、報道や文学でも使われます。 |  |
| 7 |  | bandit | 盗賊 | I caught Tajomaru, the famous bandit," the constable said | 武装して人を襲う盗賊を指し、文学や歴史の文脈で役立ちます。 |  |
| 8 |  | dagger | 短刀 | She fought with her dagger, but I forced her to have sex with me | 短剣を意味し、物語や歴史の描写でよく使われます。 |  |
| 9 |  | veil | 顔や頭を覆う薄い布 | The wind lifted her veil, and I wanted her | ベールのほか、何かを覆い隠すものという比喩にも使われます。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level a2 --accept-ai --candidates-sha 761026a5e726ba644f4a89c4fc264b08b5f10719a6c7a5678f91615721c4c733 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
