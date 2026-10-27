# Human Review 依頼(統合)

待機は1回です。下のKP(単語・表現)と文法(Part 2)の**すべて**に操作してから、制作コマンドを**同じまま1回だけ**再実行してください。
(不在なら明示宣言: `py er119_kp_human_review_cli_01.py declare-absent --runs <run> --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`。この宣言はKPと文法の両方に、このrunのこの候補roundだけ効きます)

---
## KP(level=b1b)
(個別の依頼書: er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01/key_phrases/b1b/kp_human_review_request.md)

# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `41261214d178720a` / 本文sha: `0c71c2f017d1`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | blood went cold | 恐怖で血の気が引く | Whenever it turned towards me, my blood went cold | 恐怖で血の気が引くことを表す慣用表現。 |  |
| 2 | KP | sharpen someone's senses | 人の感覚を研ぎ澄ます | My illness sharpened my senses, especially my hearing | 感覚を研ぎ澄ますという自然な比喩表現。 |  |
| 3 | KP | never stir | 少しも身じろぎしない | I eased the door open so slowly he never stirred, then let one thin ray escape my lantern | 少しも動かない、目を覚まさないという表現。 | 重複: 5 |
| 4 | 単語 | Not a mark | 跡ひとつない | Not a mark | 跡形もないことを簡潔に表す言い回し。 |  |
| 5 |  | motionless | じっと動かない | I stood motionless | 動きがまったくない状態を表す語で、描写に幅広く使えます。 | 重複: 3 |
| 6 | 単語 | fastening | 留め具 | Then my thumb slipped against the lantern's fastening | 留め具や固定する仕組みを指し、幅広い場面で使えます。 |  |
| 7 |  | mock | ばかにする | Their smiles were mocking me | あざけるような態度や表情を表す語として有用です。 |  |
| 8 |  | hideous | ひどく気味の悪い | It is the beating of his hideous heart | 非常に醜い、またはぞっとするほど不快な様子を表します。 |  |
| 9 |  | shriek | 甲高い叫び声 | A neighbour had heard a shriek | 甲高い叫び声を表す語で、動詞としても使えます。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01 --level b1b --accept-ai --candidates-sha 41261214d178720ab45aafe121950c9d5dbb5a50872a473b5da10154e4d46b46 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。

---
## KP(level=a2)
(個別の依頼書: er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01/key_phrases/a2/kp_human_review_request.md)

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

