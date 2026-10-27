# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `b030652528b02287` / 本文sha: `76f80f62120b`
- あなたの作業: KPに使う最大3件を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | carry over | 持ち越す | But the work area with the AI's notes and programs carried over to the next hour |  |  |
| 2 | KP | worth paying attention to | 注目する価値がある | One tip in the strategy notes was worth paying attention to |  |  |
| 3 | KP | a useful card to play | 使える手札 | A discovery that is not useful now might be a useful card to play next time, if it is saved |  |  |
| 4 |  | take a detour | 遠回りをする | Those that had taken a detour were now one step ahead | 本来の道筋から外れることを比喩的に表す。 |  |
| 5 |  | one step ahead | 一歩先を行っている | Those that had taken a detour were now one step ahead | 一歩先を行く、優位に立つという定番の比喩表現。 |  |

## Gateで除外された候補(参考)

- too soon to wave a flag : validate : 語数が1〜5語でない(実際: 6語)
- studied separately : canonicalization : key_phrase('study separately')がdisplay_phraseと一致せず、source_span('studied separately')内の連続部分文字列でもない(人称代名詞・所有格の一般化[閉じた語彙集合による1対1置換]にも該当しない)(Rule7: source_spanに存在しない別の辞書形を勝手に生成しない)

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01 --level a2 --accept-ai --candidates-sha b030652528b022874940a788abc0cdc187686aacfffe076f5da903c32d6121df --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01 --level a2 --kp 1,2,3 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。
