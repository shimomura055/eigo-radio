# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `f688fdbba5b6e229` / 本文sha: `7bd525e4c83b`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | confirm a clear fall | はっきりした減少を確認する | But compared with the usual persuasion test, the researchers could not confirm a clear fall in sponsored product choices | 研究結果を慎重に述べる際の「明確な低下を確認する」という表現。 |  |
| 2 | KP | results suggest | 結果から～と考えられる | The results suggest people may still want a product after seeing its ad | 断定を避けて結果からの示唆を述べる、学術文脈で有用な表現。 |  |
| 3 | KP | sales pitch | 売り込み | People who did not think the advice favored one product were also counted as people who missed the sales pitch | 商品を売り込む話や宣伝文句を指す定番の名詞句。 | 重複(アラームのみ・選んでも止まりません): 7,8 |
| 4 | 単語 | favor one product | 特定の商品を推す | In the experiment, some people felt that the advice favored one product | 「特定の商品を有利に扱う」という動詞 favor の用法を学べる。 |  |
| 5 | 単語 | blow a whistle | 警報を鳴らす | If an AI said that to you, would a guard in your mind blow a whistle | 警告や異変を知らせる意味でも使われる比喩的な表現。 |  |
| 6 |  | let the advice through | 助言を受け入れる | Or would you let the advice through, thinking, "But it's just right for me | 助言を受け入れる、という比喩的な let ～ through の用法。 | 修正済み(元: let the advice through / REVERT_SURFACE)・QA再判定済み |
| 7 |  | persuasion | 説得 | But compared with the usual persuasion test, the researchers could not confirm a clear fall in sponsored product choices | 説得や説得手法を表す抽象度の高い語です。 | 重複(アラームのみ・選んでも止まりません): 3,8 |
| 8 |  | persuade | 納得させる | In one condition, the AI was told to try to persuade people to choose a sponsored product | 「説得する」を表し、幅広い文脈で使えます。 | 重複(アラームのみ・選んでも止まりません): 3,7 |
| 9 |  | sponsored | 広告主に宣伝されている | In one condition, the AI was told to try to persuade people to choose a sponsored product | 広告や支援を受けた状態を表す重要語です。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level a2 --accept-ai --candidates-sha f688fdbba5b6e229b8a9f252baa17f4068f94768205befaae40265f77fd9fdd0 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
