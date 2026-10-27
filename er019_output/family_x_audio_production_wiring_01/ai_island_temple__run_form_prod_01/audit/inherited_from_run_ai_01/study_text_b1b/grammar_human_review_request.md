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
