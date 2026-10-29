# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `fd0b3f442dc0621b` / 本文sha: `94f8cf4a551a`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。
- Gate除外 1件(フレーズ1・単語0)に対し、補完候補 1件を末尾に追加しました(補完status: OK)

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | put the brakes on | 抑える | Spotting an ad and putting the brakes on wanting something seem to be two separate things | 計画や行動を抑制することを表す比喩的な慣用表現。 | 修正済み(元: put the brakes on / REANCHOR_D1) |
| 2 | KP | whose interests the conversation serves | 会話が誰の利益になるのか | The results suggest people may still want a product after spotting its ad, so shoppers should ask whose interests the conversation serves | 会話が誰の利益にかなうかを問う、抽象的な表現。 |  |
| 3 | KP | Sales pitch | 売り込み文句 | If an AI said that to you, would the guard inside your mind blow a whistle and shout, "Sales pitch detected! | 商品を売り込む話や宣伝文句を表す定番の連語。 | 重複(アラームのみ・選んでも止まりません): 6,8 |
| 4 | 単語 | confirm a clear drop | 明らかな減少を確認する | But compared with the usual persuasion condition, the researchers could not confirm a clear drop in the rate of sponsored product choices | 数値の明確な低下を確認する、研究報告で使える表現。 |  |
| 5 | 単語 | rate at which | 起こる割合 | The estimated rate at which participants chose the sponsored product was 40.7% | 「〜する割合」を導く、説明・分析で便利な構文。 | 修正済み(元: rate at which / REVERT_SURFACE)・QA再判定済み |
| 6 |  | persuasion | 説得 | But compared with the usual persuasion condition, the researchers could not confirm a clear drop in the rate of sponsored product choices | 説得という抽象概念を表し、学術・社会的な文脈でも使える。 | 重複(アラームのみ・選んでも止まりません): 3,8 |
| 7 |  | biased | 偏った | In the experiment, people who felt the recommendations were biased were asked, "Which product was being pushed | 偏りや先入観のある状態を表す、汎用性の高い語。 |  |
| 8 |  | persuade | 説得する | In one condition, the AI was told to persuade participants to choose a sponsored product | 「説得する」を表す動詞で、幅広い場面で使える。 | 重複(アラームのみ・選んでも止まりません): 3,6 |
| 9 |  | complications | 複雑な要素 | It did not recreate all the complications of real shopping, such as the cost of paying for something | 事態を複雑にする要因を指す、応用範囲の広い語。 |  |
| 10 |  | sponsored | スポンサーの支援を受けた | In one condition, the AI was told to persuade participants to choose a sponsored product | 広告・資金提供を受けた状態を表す重要語。 |  |
| 11 |  | or so it seemed | そう見えたのだが | It sat at the advice desk as a helpful guide—or so it seemed | 見かけと実態が異なることを示す、自然な挿入表現です。 | 補完候補(Gate除外の代替) |

## Gateで除外された候補(参考)

- counted as having failed : canonicalization_qa : 救済後の表現が未検査(QA再判定=NOT_REJUDGED / gloss再整合=REALIGNED)。検査未了の候補は提示しない=fail-closed

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level b1b --accept-ai --candidates-sha fd0b3f442dc0621b39adf6281e6a197d00ff16a2f1e86561e18f775143639dc1 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
