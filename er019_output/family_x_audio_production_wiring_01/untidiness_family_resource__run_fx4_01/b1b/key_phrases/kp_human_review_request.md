# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `d1d0facbac9a7f89` / 本文sha: `937862fe9e6e`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。
- Gate除外 2件(フレーズ2・単語0)に対し、補完候補 2件を末尾に追加しました(補完status: OK)

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | apply to every household | すべての家庭に当てはまる | Many of the participants had a high level of education, too, so the findings cannot simply be applied to every household | 研究結果の一般化可能性を論じる際に役立つ表現。 |  |
| 2 | KP | turn into an interrogation | 尋問になる | the conversation can turn into an interrogation | 会話が尋問のようなものに変わる様子を表す。 |  |
| 3 | KP | hear it out | 言い分を最後まで聞く | Before bringing out the storage box, hear it out | 結論を急がず、まず最後まで話を聞くという慣用表現。 | 重複(アラームのみ・選んでも止まりません): 10 |
| 4 | 単語 | the participant's own explanation | 参加者本人の説明 | The supplement example is the participant's own explanation; the study did not test whether keeping it in sight works | 研究参加者自身の説明を示す学術的な表現。 |  |
| 5 | 単語 | what it helps with | 何に役立つのか | Before putting something away, ask what it helps with | 物事が何に役立つかを自然に尋ねる表現。 | 重複(アラームのみ・選んでも止まりません): 9 |
| 6 |  | clutter | 物が散らかった状態 | The study offers a different way to look at clutter: it isn't always a personal failure, and it can also support daily life | 散らかりを表し、物理的・情報的な混雑にも使える語です。 |  |
| 7 |  | verdict | 結論 | So the verdict is not, "Clutter is completely innocent | 裁判の評決だけでなく、最終的な判断も表せます。 |  |
| 8 |  | prosecutor | 検察官 | The prosecutor, speaking for the side that wants things put away, immediately demands its removal | 検察官を指す、法律や報道で役立つ語です。 |  |
| 9 |  | contribution | 役立つ働き | Its contribution to daily life: needs another review | 貢献や寄与を幅広い文脈で表現できます。 | 重複(アラームのみ・選んでも止まりません): 5 |
| 10 |  | dismiss | 退ける | Don't dismiss it without question just because it's out | 意見などを退ける意味で使える動詞です。 | 重複(アラームのみ・選んでも止まりません): 3 |
| 11 |  | demand its removal | それを取り除くよう要求する | The prosecutor, speaking for the side that wants things put away, immediately demands its removal | 「撤去を要求する」という硬めの表現で、removalとの結びつきも学べます。 | 補完候補(Gate除外の代替) |
| 12 |  | Now in Session | ただいま開廷中 | The Trial of "Leaving Things Out" Is Now in Session | 法廷などが「開廷中・開始中」であることを示す定型表現です。 | 補完候補(Gate除外の代替) |

## Gateで除外された候補(参考)

- taking points away from : canonicalization_qa : canonicalization QA不合格(REVIEW_REQUIRED): qa_standalone_natural_unit, qa_standalone_comprehensibility
- did not test whether : canonicalization_qa : canonicalization QA不合格(REVIEW_REQUIRED): qa_standalone_natural_unit, qa_standalone_comprehensibility
- gets heated : canonicalization_qa : 救済後の表現が未検査(QA再判定=NOT_REJUDGED / gloss再整合=REALIGNED)。検査未了の候補は提示しない=fail-closed

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_fx4_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_fx4_01 --level b1b --accept-ai --candidates-sha d1d0facbac9a7f890a8a794ca9998b1477c84ad55d1dc3a2f2632a20dc84a414 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_fx4_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_fx4_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
