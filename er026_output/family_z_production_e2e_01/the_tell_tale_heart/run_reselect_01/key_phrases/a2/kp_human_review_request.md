# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `196a84f81bdd12e2` / 本文sha: `66da3226a61e`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | make one's blood turn cold | 人をぞっとさせる | That vulture's eye made my blood turn cold | 強い恐怖や衝撃を表す定型的な比喩表現。 |  |
| 2 | KP | rush at someone | 人に向かって突進する | I rushed at him, and he gave one scream | 「〜に突進する・襲いかかる」を表す句動詞。 |  |
| 3 |  | blame one's scream on | 人の叫び声を何かのせいにする | I welcomed them and blamed my scream on a bad dream | blame A on B（AをBのせいにする）の型。 | QA FAIL(採用には --accept-qa-fail) / AUTO対象外 |
| 4 | KP | go on talking | 話し続ける | They went on talking and smiling as before | 「話し続ける」を表す go on＋動名詞の用法。 |  |
| 5 | 単語 | raise one's voice | 声を大きくする | I raised my voice, but the beating grew louder too | 声を大きくする・声を荒らげるという自然な連語。 |  |
| 6 |  | scrape one's chair across | 人の椅子をこすりながら引きずる | I walked about and scraped my chair across the floorboards | 物をこすりながら横切らせる scrape の用法。 | QA FAIL(採用には --accept-qa-fail) / AUTO対象外 |
| 7 | 単語 | pulse | 脈 | Finally his heart stopped, and I could feel no pulse | 脈拍を表す語で、医療や生理の文脈でも使える。 |  |
| 8 |  | groan | うめく | Finally, he groaned softly in fear, not pain | 苦痛や不満をうめき声で表す動詞として役立つ。 |  |
| 9 |  | vulture's | ハゲワシの | That vulture's eye made my blood turn cold | 「ハゲワシ」の語彙で、比喩的な用法にも触れられる。 | QA FAIL(採用には --accept-qa-fail) / AUTO対象外 |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01 --level a2 --accept-ai --candidates-sha 196a84f81bdd12e227b36f2d8858a5d8faeea75cb902171d2b10a68fc61ace51 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01 --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
