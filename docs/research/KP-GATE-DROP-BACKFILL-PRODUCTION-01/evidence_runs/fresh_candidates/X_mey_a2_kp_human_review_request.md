# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `d5b2047737f7a554` / 本文sha: `c270df8bcd28`
- あなたの作業: KPに使う最大3件を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。
- Gate除外 1件(フレーズ1・単語0)に対し、補完候補 1件を末尾に追加しました(補完status: OK)

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | air-defense mission | 空からの攻撃を防ぐ任務 | In this case, the UK Ministry of Defence announced an air-defense mission for Royal Air Force Typhoon fighter jets |  |  |
| 2 | KP | ballistic missile | 弾道ミサイル | A spokesperson for the Saudi-led coalition forces in Yemen said they had stopped and destroyed one ballistic missile |  |  |
| 3 | KP | responsible for military support | 軍事支援を担う責任がある | But this example cannot tell us who is responsible for military support |  |  |
| 4 |  | Saudi-led coalition forces | 一国が率いる連合軍 | A spokesperson for the Saudi-led coalition forces in Yemen said they had stopped and destroyed one ballistic missile | 紛争報道で使われる「主導国＋連合軍」の表現です。 |  |
| 5 |  | continue refueling support | 給油支援を続ける | Britain also said it would continue refueling support for Saudi air-defense work | 軍事支援の継続を表す、報道で役立つ連語です。 |  |
| 6 |  | more than the facts show | 事実から分かる以上のこと | But if you look at the refueling support and say, "Then the Typhoons will attack too," you claim more than the facts show | 事実が示す範囲を超える主張を表す言い回し。 | 補完候補(Gate除外の代替) |

## Gateで除外された候補(参考)

- to weaken Houthi military targets : cmu : CMU発音辞書に登録されていない語を含む(未登録語: Houthi。構成する全ての語がCMU辞書に登録された語句だけを選ぶ)

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_kpbf_ev_03`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_kpbf_ev_03 --level a2 --accept-ai --candidates-sha d5b2047737f7a554a47ca5759e7207a2249ec900fe4f646a95f65b01df78a42b --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_kpbf_ev_03 --level a2 --kp 1,2,3 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_kpbf_ev_03 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_kpbf_ev_03 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
