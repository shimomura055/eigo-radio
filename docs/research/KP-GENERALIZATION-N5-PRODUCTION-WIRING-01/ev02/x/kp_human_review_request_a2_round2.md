# KP Human Review 依頼(a2) round 2

- 状態: PENDING_REVIEW / candidates_sha256: `70b7d536a643993b` / 本文sha: `7abb52d8cd85`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。
- Gate除外 1件(フレーズ1・単語0)に対し、補完候補 0件を末尾に追加しました(補完status: OK)。適切な補完候補が不足したため上限未達です(数合わせはしません)

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | hear someone out | 人の話を最後まで聞く | Before you bring out the storage box, hear it out | 相手の話を最後まで聞くことを表す句動詞です。 |  |
| 2 | KP | take something away from | 何かを差し引き、価値や効果を損なう | But that could take points away from the ways each home has found to make life work | 評価や得点を差し引く比喩的な表現です。 |  |
| 3 | KP | in session | 会議や審理が行われている | The Trial of "Leaving Things Out" Is Now in Session | 法廷などが開廷中であることを表します。 |  |
| 4 | 単語 | in sight | 視界に入って見える状態にある | The study did not test whether keeping it in sight works | 見える範囲にあることを表す定型句 |  |
| 5 | 単語 | not so fast | そう急がず、少し待つよう求める | But the court says, "Not so fast | 相手を制止する定型表現 |  |
| 6 |  | rely on | 人や物を頼りにする | But you might also remove the reminder the person relied on | 人や物を頼りにする動詞と前置詞 |  |
| 7 |  | clutter | 散らかった物 | The study gives us another way to look at clutter | 散らかりや雑然とした状態を表す有用な名詞です。 |  |
| 8 |  | verdict | 結論 | So the verdict is not, "Clutter is completely innocent | 判決だけでなく、最終的な判断にも使える語です。 |  |
| 9 |  | charge | 非難 | The charge is that it makes the kitchen look bad | 「告発・非難」の意味で使われる多義語です。 |  |
| 10 |  | scorecard | 評価基準 | A scorecard might say, "The fewer things you can see, the better | 評価基準や採点表を表す語として応用できます。 |  |
| 11 |  | supplement | サプリメント | A supplement sits alone in the kitchen | 栄養補助食品や補足物を表す実用的な語です。 |  |

## Gateで除外された候補(参考)

- needs another look : n5_select : 塊価値判定でkeepでない(cls=F, passive_fragment=False): needとlookの通常の組合せ
- make life work : n5_select : 塊価値判定でkeepでない(cls=F, passive_fragment=False): makeとworkの意味から導ける組合せ
- gets heated : canonicalization_qa : 救済後の表現が未検査(QA再判定=NOT_REJUDGED / gloss再整合=REALIGNED)。検査未了の候補は提示しない=fail-closed

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_n5ev`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_n5ev --level a2 --accept-ai --candidates-sha 70b7d536a643993bd107c79288e5b335616bbb54761b05e2e8f3559c46a12231 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_n5ev --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_n5ev --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_n5ev --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
