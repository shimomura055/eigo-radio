# Human Review 依頼(統合)

待機は1回です。下のKP(単語・表現)と文法(Part 2)の**すべて**に操作してから、制作コマンドを**同じまま1回だけ**再実行してください。
(不在なら明示宣言: `py er119_kp_human_review_cli_01.py declare-absent --runs <run> --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`。この宣言はKPと文法の両方に、このrunのこの候補roundだけ効きます)

---
## KP(level=a2)
(個別の依頼書: er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01/a2/key_phrases/kp_human_review_request.md)

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

---
## KP(level=b1b)
(個別の依頼書: er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01/b1b/key_phrases/kp_human_review_request.md)

# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `b3c5f901bddced09` / 本文sha: `00f14092c072`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | carry over | 次に持ち越す | In the experiment, the island and the conversation were reset every hour, but the work area where the AI kept notes and programs was carried over |  |  |
| 2 | KP | call on | 頼まれる | So, would that experience help the AI the next time it was called on |  |  |
| 3 | KP | look at separately | 分けて考える | The fact that the experienced group did better and the fact that removing a particular memory lowered its score need to be looked at separately |  |  |
| 4 | 単語 | one step ahead | 一歩先を行く | The ones that had taken a detour were now one step ahead | 「一歩先を行く」という優位性を表す定番表現。 |  |
| 5 | 単語 | card to play | 使える手 | A discovery that is no use right now might become a useful card to play next time, if it is saved | 「切れるカード・有効な手段」という比喩表現。 |  |
| 6 |  | take a detour | 寄り道をする | The ones that had taken a detour were now one step ahead | 本筋を外れて別の経験をする比喩的な表現。 |  |
| 7 |  | no use right now | 今は役に立たない | A discovery that is no use right now might become a useful card to play next time, if it is saved | 「今は役に立たない」を表す自然な言い回し。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01 --level b1b --accept-ai --candidates-sha b3c5f901bddced091650fa22e5cf9910fa0f84e396f783caf2034fbfdca3b4ab --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。

---
## 文法(Part 2)
(個別の依頼書: er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01/b1b/study_text/grammar_human_review_request.md)

# Part 2 文法解説 Human Review 依頼(Advanced) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `c97b6c8f8ad76cd4` / 本文sha: `dc291d4af4f5` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 本文の中で解説する英文を1つ選びます(AI推奨=TOP1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

## AI推奨(TOP1): 候補1 [T1 / HEAVY] 段落P4

> The island went back to how it was before, but what the AI had discovered was not erased.

- 構文: what節主語
- 教える価値: what節が主語になり、その後ろの動詞が主節の述語になると見分ける。
- 読み違えやすい点: what the AI had discovered全体が主語なのに、埋め込み節内のthe AIを主節の主語と取り違えることがある。

## TOP2: 候補2 [T1 / HEAVY] 段落P6

> After that, the average number of towers it could build fell.

- 構文: 関係節を含む長い主語
- 教える価値: 長い主語の中にある関係節の動詞と、主節の動詞を区別する。
- 読み違えやすい点: it could buildを主節の動詞と取り違え、文の主動詞fellを見落とすことがある。

(TOP2の次に控えがあと1件。reselectすると次順位が新しいTOP1/TOP2になります)

## 操作(コマンド。`--by` は操作者名)

- AI推奨(TOP1)を了承: `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01 --candidates-sha c97b6c8f8ad76cd44e5bba221646ab2c4237e485a55a984c5535508b9affaf69 --by <名前> --choice top1 --accept-ai`
- TOP1を選ぶ: `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01 --candidates-sha c97b6c8f8ad76cd44e5bba221646ab2c4237e485a55a984c5535508b9affaf69 --by <名前> --choice top1`
- TOP2を選ぶ(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01 --candidates-sha c97b6c8f8ad76cd44e5bba221646ab2c4237e485a55a984c5535508b9affaf69 --by <名前> --choice top2 --reason <理由>`
- 選び直し(TOP1/TOP2をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01 --candidates-sha c97b6c8f8ad76cd44e5bba221646ab2c4237e485a55a984c5535508b9affaf69 --by <名前> --choice reselect --reason <理由>`
- 今回は解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01 --candidates-sha c97b6c8f8ad76cd44e5bba221646ab2c4237e485a55a984c5535508b9affaf69 --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01`
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・supportの再生成は行われません)。

