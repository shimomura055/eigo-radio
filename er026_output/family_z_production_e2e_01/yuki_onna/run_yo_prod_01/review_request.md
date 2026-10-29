# Human Review 依頼(統合)

待機は1回です。下のKP(単語・表現)と文法(Part 2)の**すべて**に操作してから、制作コマンドを**同じまま1回だけ**再実行してください。
(不在なら明示宣言: `py er119_kp_human_review_cli_01.py declare-absent --runs <run> --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`。この宣言はKPと文法の両方に、このrunのこの候補roundだけ効きます)

---
## KP(level=b1b)
(個別の依頼書: er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01/key_phrases/b1b/kp_human_review_request.md)

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

---
## KP(level=a2)
(個別の依頼書: er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01/key_phrases/a2/kp_human_review_request.md)

# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `c5dfc27410d4fd6e` / 本文sha: `54ab9a6db4b1`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。
- Gate除外 1件(フレーズ0・単語1)に対し、補完候補 1件を末尾に追加しました(補完status: OK)

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | talk someone into staying | 誰かを説得して残ってもらう | His mother welcomed Yuki and talked her into staying | 「人を説得して〜させる」を表す句動詞の型。 |  |
| 2 | KP | get what you deserve | 自分にふさわしい報いを受ける | If they ever have reason to complain about you, you will get what you deserve | 当然の報いを受ける、という慣用表現。 |  |
| 3 | KP | slip away | こっそり立ち去る | Then she slipped away through the smoke-hole in the roof | 気づかれないように立ち去る含みのある句動詞。 |  |
| 4 | 単語 | riverside | 川沿いの | They could not continue, so they entered a riverside hut | 川辺を表す複合語で、場所の描写に幅広く使えます。 |  |
| 5 | 単語 | mist | 霧 | She melted into white mist and rose towards the roof beams | 霧やもやを指し、天候や情景描写で役立ちます。 |  |
| 6 |  | light-skinned | 色白の | Yuki became Minokichi's wife, and they later had ten light-skinned children | 肌の色が薄いことを表す形容詞で、人の描写に使えます。 |  |
| 7 |  | complain | 文句を言う | If they ever have reason to complain about you, you will get what you deserve | 不満を表明する意味で、幅広い場面で使える動詞です。 | 補完候補(Gate除外の代替) |

## Gateで除外された候補(参考)

- woodcutters : cmu : CMU発音辞書に登録されていない語を含む(未登録語: woodcutters。構成する全ての語がCMU辞書に登録された語句だけを選ぶ)

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01 --level a2 --accept-ai --candidates-sha c5dfc27410d4fd6e85bd638a6fe09845de1c787028ad842e2ff9570b31b81cdf --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01 --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。

---
## ニュアンス解説(level=a2)
(個別の依頼書: er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01/a2/study_text/nuance_human_review_request.md)

# ニュアンス解説 Human Review 依頼

- level: a2(Standard) / 最大1件・採用するか不採用かを決めます(不採用でも代替候補は自動補充されません)
- 候補ID: nuance_e97496c894b00f2a / candidate_sha256: e97496c894b00f2aa9cd3d480935b1b4f53902163f0f4f7a2124f26f66754457

## not even
- 本文の英文: Never tell anyone about tonight, not even your mother.
- 日本語訳: 今夜のことは誰にも話してはいけない。お母さんにさえ話してはいけない。
- ポイント: 否定の中で「例外になりそうなもの」まで含める強調

解説(全文):
「not even」は、否定の範囲に「当然なら例外になりそうなもの」まで含める強調です。ここでは母親にも話すなと例外を封じ、秘密の厳しさを際立たせています。単に「母親を含めて誰にも言うな」と伝える including your mother より、「母親でさえ例外ではない」という意外性が前に出ます。日本語の「〜でさえ」に近い感覚で捉えられます。

- 重複判定(KP/Word): pass / 暫定選定のKey Phrase・Wordとは学習上の焦点が別と判定しました。

## 決め方
- V3フォーム: 『ニュアンス解説』欄で採用/不採用を選び、KP・文法と一緒に送信(推奨)
- CLI(KPを先に確定した場合など): `py er119_kp_human_review_cli_01.py nuance-select --run er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01 --level a2 --choice adopt|reject --candidates-sha e97496c894b00f2aa9cd3d480935b1b4f53902163f0f4f7a2124f26f66754457 --by <名前> --user-ref <ユーザー発言のdelegation_logパス>`

