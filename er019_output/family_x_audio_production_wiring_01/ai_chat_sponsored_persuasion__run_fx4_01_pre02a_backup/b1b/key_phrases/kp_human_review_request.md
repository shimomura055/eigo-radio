# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `43aeae9f42844d14` / 本文sha: `5f88b4c74a00`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | play favorites | えこひいきする | The book got a prominent spot, but the guide did not play favorites | 人や物をえこひいきすることを表す慣用表現。 |  |
| 2 | KP | capture all that complexity | 複雑な事情をすべて捉える | The study did not capture all that complexity, and it has not yet been confirmed whether the same results would apply to real purchases | 複雑さを余さず捉えるという自然な動詞の使い方。 |  |
| 3 | KP | a different script | 別の指示 | Even though both conditions used chat-based AI, the AI was given a different script | 指示や役割を「脚本」にたとえた比喩表現。 |  |
| 4 | 単語 | choose at random | 無作為に選ぶ | The sponsored book was chosen at random from the books shown | 「無作為に選ばれる」を表す定型表現。 |  |
| 5 | 単語 | what stands out | 際立っている点 | But what stands out in this experiment is the guide's task, not just its seat | 特に目立つ点を導く便利な表現。 |  |
| 6 |  | in a news flash | ニュース速報で | But it is too soon to announce in a news flash, "AI is now the greatest salesperson | 速報として大々的に伝える場面を指す表現。 |  |
| 7 |  | a prominent spot | 人目につく位置 | The book got a prominent spot, but the guide did not play favorites | 目立つ位置を表す、広告や配置で使える語句。 | 重複(アラームのみ・選んでも止まりません): 10 |
| 8 |  | persuasive | 説得を目的とした | In this persuasive condition, the study estimated that people chose the sponsored book 61.2% of the time | 人を説得する性質を表す、議論や文章で役立つ語です。 |  |
| 9 |  | motive | 行動の理由 | Real shopping involves the cost of buying things and many different motives | 行動の背後にある動機を表す、幅広く使える語です。 |  |
| 10 |  | placement | 掲載される位置 | When we think about the competition for ads, it is easy to picture a fight over placement: "Get the top spot | 配置や掲載位置を表し、広告などで使われます。 | 重複(アラームのみ・選んでも止まりません): 7 |
| 11 |  | estimate | およその値を出す | In this persuasive condition, the study estimated that people chose the sponsored book 61.2% of the time | 数値や規模を推定したことを表す、学術文脈でも有用な語です。 |  |
| 12 |  | sponsored | スポンサー付きの | The sponsored book was chosen at random from the books shown | 資金提供や広告支援を受けた状態を表す語です。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level b1b --accept-ai --candidates-sha 43aeae9f42844d140cb582b47a87d71f99119a4573f85095ea2963a4a9b01974 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
