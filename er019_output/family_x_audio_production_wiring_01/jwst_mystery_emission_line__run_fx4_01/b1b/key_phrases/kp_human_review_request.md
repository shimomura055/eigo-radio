# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `7f0bc16d183feb7d` / 本文sha: `33ec46beb6f1`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | equivalent width | スペクトル線の強さを示す等価幅 | The authors used the line's absence from the images to estimate that its "equivalent width," a measure of the line's features, was at least 7,620 Å | 輝線の強さを表す天文学の専門用語。 |  |
| 2 | KP | narrow down the source | 発生源を絞り込む | The blank space had become a clue that could help narrow down the source | 候補を絞り込む句動詞の使い方が学べる。 |  |
| 3 | KP | set a lower limit | 下限を決める | That absence helped researchers set a lower limit on the line's equivalent width, but more observations are needed to identify its source | 研究で下限値を設定する際の定型表現。 |  |
| 4 | 単語 | take an unexpected turn | 思わぬ展開になる | Then the investigation took an unexpected turn | 予想外の展開になるという慣用表現。 |  |
| 5 | 単語 | point-like object | 点のように見える物体 | But when they checked its position in a deep image, they could not find a matching point-like object | 点状天体を表す天文学の専門表現。 |  |
| 6 |  | wavelength | 波長 | They searched for lines of light that appear at a particular wavelength | 光の波長を表す専門語で、科学文脈で広く使われます。 |  |
| 7 |  | celestial | 天体の | In the area they observed, they closed small windows that overlapped with some celestial objects already known, while leaving almost all the others open | 天体や天空に関する対象を表す、汎用性のある語です。 |  |
| 8 |  | absence | 見当たらないこと | The authors used the line's absence from the images to estimate that its "equivalent width," a measure of the line's features, was at least 7,620 Å | 「不在・欠如」を表し、抽象的な文脈でも使えます。 |  |
| 9 |  | investigation | 調査 | But this time, the researchers have turned the usual steps of the investigation upside down | 調査や捜査を意味し、幅広い話題で使える語です。 |  |
| 10 |  | frustrate | いら立たせる | A mystery like this, enough to frustrate any detective, has appeared in space | 期待や目的を妨げ、いら立たせる意味を持つ動詞です。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level b1b --accept-ai --candidates-sha 7f0bc16d183feb7dafcfe820c3d6f2f8fcba476ce8d1ced95f59caa112d3cecd --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
