# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `90e6bd9ac9fb999b` / 本文sha: `5c17a0d3cff4`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。
- Gate除外 1件(フレーズ0・単語1)に対し、補完候補 1件を末尾に追加しました(補完status: OK)

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | slip away | そっと立ち去る | She melted into white mist, rose towards the roof beams, and slipped away through the smoke-hole | 人知れず立ち去る、または消える意味の句動詞。 |  |
| 2 | KP | have reason to complain | 不満を言う理由がある | If they ever have reason to complain of you, I will treat you as you deserve | 不満を申し立てる正当な理由があるという表現。 |  |
| 3 | KP | keep silent | 黙っている | He kept silent even about his master's death | 口外せず沈黙を守ることを表す自然な連語。 |  |
| 4 | 単語 | take shelter | 避難する | When they could go no farther, they took shelter in a hut beside a river | 避難することを表す自然なコロケーション。 |  |
| 5 | 単語 | as you deserve | あなたにふさわしいように | If they ever have reason to complain of you, I will treat you as you deserve | 相応の扱いを受ける、という含みのある表現。 |  |
| 6 |  | go no farther | それ以上先へ進まない | When they could go no farther, they took shelter in a hut beside a river | それ以上進まない、進めないことを表す表現。 |  |
| 7 |  | persuade | 説得する | He took her home to his widowed mother, who welcomed the girl and persuaded her to stay | 説得して相手の行動を変える意味の汎用的な動詞です。 |  |
| 8 |  | widowed | 配偶者を亡くした | He took her home to his widowed mother, who welcomed the girl and persuaded her to stay | 配偶者を亡くした状態を表す、知っておきたい形容詞です。 |  |
| 9 |  | bar | 通れないようにふさぐ | They barred the door and lay under their straw coats | 「閉ざした」の意味に加え、立ち入りを禁じる用法もあります。 |  |
| 10 |  | struggle | 苦労する | One winter night in Japan, two woodcutters struggled through a snowstorm | 困難に直面して努力する状況を幅広く表せます。 | 補完候補(Gate除外の代替) |

## Gateで除外された候補(参考)

- woodcutters : cmu : CMU発音辞書に登録されていない語を含む(未登録語: woodcutters。構成する全ての語がCMU辞書に登録された語句だけを選ぶ)

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01 --level b1b --accept-ai --candidates-sha 90e6bd9ac9fb999b9e18f53791f109999400c32e6d4f3b79cb16666da6fe48d3 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
