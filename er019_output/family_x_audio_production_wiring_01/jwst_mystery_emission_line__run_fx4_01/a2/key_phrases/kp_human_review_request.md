# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `1b65418d4120c7d0` / 本文sha: `49e80412534f`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。
- Gate除外 1件(フレーズ1・単語0)に対し、補完候補 1件を末尾に追加しました(補完status: OK)

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | equivalent width | 光の線の特徴を表す幅 | The authors used the line's absence from images to estimate its "equivalent width," a measure of the line's features | 天文学で線の強さを示す専門用語。 |  |
| 2 | KP | a lower limit | 下限 | That absence helped set a lower limit for its equivalent width, but more observations are needed to find its source | 定量的な下限を示す学術的な表現。 |  |
| 3 | KP | narrow down the source | 発生源を絞り込む | The empty space had become a clue that could help narrow down the source | 候補や範囲を絞り込む句動詞表現。 |  |
| 4 | 単語 | turn the usual steps around | いつもの手順を逆にする | But this time, researchers turned the usual steps around | 手順を逆転させる意味の慣用的な言い方。 |  |
| 5 | 単語 | line's absence from images | 画像に光の線が写っていないこと | The authors used the line's absence from images to estimate its "equivalent width," a measure of the line's features | 画像に線が見られないことを表す科学的表現。 | 重複(アラームのみ・選んでも止まりません): 11 |
| 6 |  | wavelength | 波長 | They looked for lines of light at a certain wavelength | 光の波長を表す科学分野で汎用性の高い語。 |  |
| 7 |  | estimate | およその値を出す | The authors used the line's absence from images to estimate its "equivalent width," a measure of the line's features | 数量や価値を推定する際に幅広く使われる語。 |  |
| 8 |  | investigation | 調査 | Then the investigation took an unexpected turn | 調査や捜査を指し、幅広い文脈で使える語。 |  |
| 9 |  | frustrate | いら立たせる | This kind of mystery could frustrate any detective | 期待や計画を妨げ、いら立たせる意味の動詞。 |  |
| 10 |  | overlap | 一部が重なる | In the area they studied, they closed small windows that overlapped with some known space objects | 重なり合うことを示す動詞の過去形。 |  |
| 11 |  | show up | 現れる | The fact that it "doesn't show up" became evidence | 「現れる・目に見える」の意味で使う句動詞です。 | 重複(アラームのみ・選んでも止まりません): 5 / 補完候補(Gate除外の代替) |

## Gateで除外された候補(参考)

- limited the search to : canonicalization_qa : 救済後の表現が未検査(QA再判定=NOT_REJUDGED / gloss再整合=REALIGNED)。検査未了の候補は提示しない=fail-closed

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level a2 --accept-ai --candidates-sha 1b65418d4120c7d0ed457183bea5ccaaae6bafb32c02e30869584918aaedffe6 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
