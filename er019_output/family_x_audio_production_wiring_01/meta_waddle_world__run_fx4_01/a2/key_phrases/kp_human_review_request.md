# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `2c8329dad8654ef1` / 本文sha: `df0c5f8e6460`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | At the time of writing | 執筆時点で | At the time of writing, no one had said when it would be available in Japan or other places | 「執筆時点で」を表す、記事や報告で使われる定型表現です。 |  |
| 2 | KP | make room for | ～のための時間を作る | It may matter more if they want to make room for one during the gaps in a busy day | 場所や時間を「空ける・確保する」という比喩的な用法を学べます。 | 重複(アラームのみ・選んでも止まりません): 5 |
| 3 | KP | side by side | 隣り合わせに | When it comes to usefulness, you can compare features side by side | 「並べて・並んで」を表す自然な副詞表現です。 |  |
| 4 | 単語 | early step toward | ～への初めの一歩 | TechCrunch has suggested it may be an early step toward future devices like pets | 何かの実現に向けた「初期段階」を表す語の組み合わせです。 |  |
| 5 |  | gaps in a busy day | 忙しい一日の合間にできる空き時間 | It may matter more if they want to make room for one during the gaps in a busy day | 忙しい一日の合間の時間を表す表現として使えます。 | 重複(アラームのみ・選んでも止まりません): 2 |
| 6 | 単語 | subscription | 定額制の契約 | It is free in app stores, and its official website says there is no subscription | 定期購読・定額契約を表す実用性の高い語です。 |  |
| 7 |  | usefulness | 役立ち具合 | When it comes to usefulness, you can compare features side by side | 「有用性」を表す抽象名詞で、幅広い文脈で使えます。 |  |
| 8 |  | prediction | 予測 | Still, it is too soon to get excited about future predictions | 将来の予測を表す語で、報道や議論で頻出します。 |  |
| 9 |  | craze | 大ブーム | We still do not know if it will become a craze like Tamagotchi | 一時的な熱狂や流行を表す語です。 |  |
| 10 |  | resident | 住人 | A new resident | 居住者を表し、人や場所について幅広く使えます。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01 --level a2 --accept-ai --candidates-sha 2c8329dad8654ef17d1e87fc13c6f14d0231c232588105a9b6ff8bf6fe78284c --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01 --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
