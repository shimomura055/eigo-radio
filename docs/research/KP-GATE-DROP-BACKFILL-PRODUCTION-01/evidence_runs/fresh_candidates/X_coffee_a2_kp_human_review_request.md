# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `69870372f729b544` / 本文sha: `07a0efc7f1d6`
- あなたの作業: KPに使う最大3件を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | coffee futures price | コーヒー先物の取引価格 | In February, before summer, New York's Arabica coffee futures price reached a record high |  |  |
| 2 | KP | put in place | 導入する | tariffs put in place during summer raised the price of the beans themselves |  |  |
| 3 | KP | pass through | 段階を経て波及する | At the time of that report, the tariff-caused rise had not yet passed through the whole supply chain |  |  |
| 4 |  | Turn Back the Clock | 時間をさかのぼる | The Coffee Price Rise Case: Turn Back the Clock on the Price Tag | 過去の状態に戻すという慣用表現。 |  |
| 5 |  | supply chain | 商品を作って届けるまでの流れ | At the time of that report, the tariff-caused rise had not yet passed through the whole supply chain | 供給網を指す経済・ビジネス分野の重要語。 |  |
| 6 |  | record high | 過去最高値 | In February, before summer, New York's Arabica coffee futures price reached a record high | 価格や数値が過去最高に達したことを表す定番表現。 |  |
| 7 |  | take a second look | もう一度見直す | Next time, take a second look at a store price tag | 見直す、もう一度注意して確認するという表現。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/coffee_prices__run_kpbf_ev_02`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/coffee_prices__run_kpbf_ev_02 --level a2 --accept-ai --candidates-sha 69870372f729b54421d615523277762de871d1bd26284a22a04ce6d6b4013069 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/coffee_prices__run_kpbf_ev_02 --level a2 --kp 1,2,3 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/coffee_prices__run_kpbf_ev_02 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/coffee_prices__run_kpbf_ev_02 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
