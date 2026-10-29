# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `c0c11f7c3ed34c8c` / 本文sha: `483654aeb99e`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | draw attention to | ～に注意を向けさせる | But this test draws attention to the guide's job, not just its place | 論点や重要事項に注意を向ける、論説で頻出の表現。 |  |
| 2 | KP | apply to real purchases | 実際の買い物にも当てはまる | We also do not know if the same results apply to real purchases | 研究結果などが実際の事例にも当てはまるかを表す。 |  |
| 3 | KP | pick at random | 無作為に選ぶ | The promoted book was picked at random from the books shown | 無作為に選ばれたことを表す自然な定型表現。 |  |
| 4 | 単語 | persuade | 説得する | It was told to persuade the person to choose the promoted book | 相手を説得して行動させる意味の重要な動詞。 |  |
| 5 | 単語 | promoted | 宣伝対象の | The promoted book was picked at random from the books shown | 宣伝・販売促進の文脈で使われる語。 |  |
| 6 |  | neutral | 偏りのない | It put the promoted book first, but gave it a neutral description | 偏りや立場がないことを表す汎用性の高い語。 |  |
| 7 |  | estimate | 推定する | In this test, the study estimated that people chose the promoted book 61.2% of the time | データなどを基に推定する意味を学べる。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level a2 --accept-ai --candidates-sha c0c11f7c3ed34c8c680a16f7259885f38a1f61909b43521fb831406683d0f8af --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
