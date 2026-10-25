# Human Review 依頼(統合)

待機は1回です。下のKP(単語・表現)と文法(Part 2)の**すべて**に操作してから、制作コマンドを**同じまま1回だけ**再実行してください。
(不在なら明示宣言: `py er119_kp_human_review_cli_01.py declare-absent --runs <run> --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`。この宣言はKPと文法の両方に、このrunのこの候補roundだけ効きます)

---
## KP(level=b1b)
(個別の依頼書: er121_output/family_y_production_01/redelivery_fee/run_01/key_phrases/b1b/kp_human_review_request.md)

# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `7da44f09777c39dd` / 本文sha: `f4f19da3217a`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | sit right with someone | 人にとって納得がいく | Having to pay for redelivery just doesn't sit right with me |  |  |
| 2 | KP | take the trouble | わざわざ手間をかける | Still, I take the trouble to think about how to receive my packages, so honestly, I think it's wrong that I pay the same fee as people who are always away and ask for redelivery |  | 重複: 6 |
| 3 | KP | on top of | ～に加えて | Charging for redelivery means the person receiving the package pays a fee on top of the usual shipping cost |  |  |
| 4 | 単語 | when it suits someone | 人の都合のよいときに | It's convenient to pick them up when it suits me, but for some items, I can't choose a locker | 「自分の都合がよいときに」を表す自然な定型表現。 |  |
| 5 | 単語 | end up receiving | 結局受け取ることになる | And even when I ask for a package to be sent to a delivery office, it may arrive late, so I sometimes end up receiving it in person after all | 「結局〜することになる」という end up の用法。 |  |
| 6 |  | make an effort | 努力する | For people who can choose how to receive packages, a redelivery fee can be a signal that encourages them to make an effort | 努力することを表す、幅広く使えるコロケーション。 | 重複: 2 |

## Gateで除外された候補(参考)

- can’t be helped : validate : 有限助動詞を含む(既存canonicalization Validatorが拒否する形)

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/redelivery_fee/run_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/redelivery_fee/run_01 --level b1b --accept-ai --candidates-sha 7da44f09777c39dd26355d95b381e03421ab1bb2bb806074578b5d86efe1bd0b --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/redelivery_fee/run_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er121_output/family_y_production_01/redelivery_fee/run_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/redelivery_fee/run_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。

---
## KP(level=a2)
(個別の依頼書: er121_output/family_y_production_01/redelivery_fee/run_01/key_phrases/a2/kp_human_review_request.md)

# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `d699b19591149879` / 本文sha: `c415df6b554b`
- あなたの作業: KPに使う最大3件を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | make an effort | 努力する | For people who can choose how to get packages, a redelivery fee can be a sign that encourages them to make an effort |  |  |
| 2 | KP | end up getting it | 結局それを受け取ることになる | So sometimes I end up getting it in person after all |  |  |
| 3 | KP | take up | 時間を取る | Redelivery takes up the delivery worker's time, so charging for it is fine |  |  |
| 4 |  | when it suits someone | 人にとって都合のいいときに | It is handy to pick them up when it suits me | 「自分の都合がよいときに」という自然な表現。 |  |

## Gateで除外された候補(参考)

- it can’t be helped : validate : 有限助動詞を含む(既存canonicalization Validatorが拒否する形)
- redelivery fee : cmu : CMU発音辞書に登録されていない語を含む(未登録語: redelivery。構成する全ての語がCMU辞書に登録された語句だけを選ぶ)

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/redelivery_fee/run_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/redelivery_fee/run_01 --level a2 --accept-ai --candidates-sha d699b19591149879fc9c9b5db24010ae3817082e6338de57d783cc37959e7450 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/redelivery_fee/run_01 --level a2 --kp 1,2,3 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er121_output/family_y_production_01/redelivery_fee/run_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/redelivery_fee/run_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。

