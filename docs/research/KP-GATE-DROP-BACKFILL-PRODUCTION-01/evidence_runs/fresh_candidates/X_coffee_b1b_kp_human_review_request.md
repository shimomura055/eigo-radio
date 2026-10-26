# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `e89c1b10862a468a` / 本文sha: `2e58952fc33a`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | off the hook | 責任を問われない | So, are tariffs off the hook |  |  |
| 2 | KP | all-time high | 史上最高 | Turn the pages of the record, and we find that in February, before summer, the futures price for Arabica coffee in New York reached an all-time high |  |  |
| 3 | KP | make its way through | 段階を経て伝わる | The key point is that, at the time of that report, the tariff-driven rise had not yet fully made its way through the supply chain to the prices consumers paid |  |  |
| 4 | 単語 | jump to conclusions | 早まって結論を出す | No, that would be jumping to conclusions too | 十分な根拠なしに結論を急ぐことを表す定型表現。 |  |
| 5 | 単語 | futures price | 先物価格 | Turn the pages of the record, and we find that in February, before summer, the futures price for Arabica coffee in New York reached an all-time high | 先物取引での価格を表す金融・経済用語。 |  |
| 6 |  | year over year | 前年の同じ時期と比べて | price of ground coffee rose 41% year over year, mostly because of earlier bean shortages and higher bean costs | 前年同期比を示す報告・分析でよく使う表現。 |  |
| 7 |  | supply chain | 商品が作られて届くまでの流れ | The key point is that, at the time of that report, the tariff-driven rise had not yet fully made its way through the supply chain to the prices consumers paid | 原材料から消費者までの供給網を指す重要語。 |  |
| 8 |  | tariff-driven rise | 関税による値上がり | The key point is that, at the time of that report, the tariff-driven rise had not yet fully made its way through the supply chain to the prices consumers paid | 関税が要因となる上昇を簡潔に表す複合表現。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/coffee_prices__run_kpbf_ev_02`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/coffee_prices__run_kpbf_ev_02 --level b1b --accept-ai --candidates-sha e89c1b10862a468a11480f80ae9072f0eda281c7f5f503bb7c47604a3feac23a --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/coffee_prices__run_kpbf_ev_02 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/coffee_prices__run_kpbf_ev_02 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/coffee_prices__run_kpbf_ev_02 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
