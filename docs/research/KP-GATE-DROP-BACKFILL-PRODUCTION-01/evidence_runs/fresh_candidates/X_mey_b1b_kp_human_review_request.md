# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `f72003f1b849da0d` / 本文sha: `4d9ac5a20200`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。
- Gate除外 2件(フレーズ2・単語0)に対し、補完候補 2件を末尾に追加しました(補完status: OK)

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 |  | intercepted and destroy | 迎撃して破壊する | A spokesperson for the Saudi-led coalition forces in Yemen said they had intercepted and destroyed one ballistic missile fired toward Riyadh by the Houthis |  | 修正済み(元: intercepted and destroyed / REDERIVE_M1_WINDOW) / AUTO対象外 |
| 2 | KP | ballistic missile | 弾道ミサイル | A spokesperson for the Saudi-led coalition forces in Yemen said they had intercepted and destroyed one ballistic missile fired toward Riyadh by the Houthis |  |  |
| 3 |  | goes beyond the evidence | 証拠から言える範囲を超えている | On the other hand, looking at what the refueling support covers and saying, "Then the Typhoons will attack too," goes beyond the evidence |  | 修正済み(元: goes beyond the evidence / REVERT_SURFACE) / AUTO対象外 |
| 4 | KP | put in the same box | 同じ枠にまとめられる | Even though both are put in the same box marked "British support," they are not all the same kind of activity | 異なるものを同一視してひとまとめにする比喩。 |  |
| 5 |  | backs operations | 作戦を支援する | Meanwhile, refueling support also backs operations to weaken Houthi military targets | 動詞 back が「作戦を支援する」の意味で使われる。 | 修正済み(元: backs operations / REVERT_SURFACE) / AUTO対象外 |
| 6 | KP | what the words cover | その言葉がどこまでを指すか | What we need to check is what the words cover | 言葉が何を対象に含むか、適用範囲を示す表現。 |  |
| 7 | 単語 | Saudi-led coalition forces | サウジ主導の連合軍 | A spokesperson for the Saudi-led coalition forces in Yemen said they had intercepted and destroyed one ballistic missile fired toward Riyadh by the Houthis | 報道で頻出する、主導国を示す複合表現です。 | 補完候補(Gate除外の代替) |
| 8 | 単語 | track down the subject | 主語を突き止める | This time, it's the news detective's turn to track down the subject | track downは情報を追跡して突き止める句動詞です。 | 補完候補(Gate除外の代替) |

## Gateで除外された候補(参考)

- stretch what was said : validate : 有限助動詞を含む(既存canonicalization Validatorが拒否する形)
- settle who is responsible : validate : 有限助動詞を含む(既存canonicalization Validatorが拒否する形)

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_kpbf_ev_03`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_kpbf_ev_03 --level b1b --accept-ai --candidates-sha f72003f1b849da0d5c81c571ccd3655466a9d156dc0a94ce5d7dad9b902bcc21 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_kpbf_ev_03 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_kpbf_ev_03 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_kpbf_ev_03 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
