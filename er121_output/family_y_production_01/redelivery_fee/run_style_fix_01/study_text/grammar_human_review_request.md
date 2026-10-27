# Part 2 文法解説 Human Review 依頼(Advanced) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `d09c110af7ada425` / 本文sha: `f4f19da3217a` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 本文の中で解説する英文を1つ選びます(AI推奨=TOP1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

## AI推奨(TOP1): 候補1 [T1 / CMP] 段落P4

> Still, I take the trouble to think about how to receive my packages, so honestly, I think it’s wrong that I pay the same fee as people who are always away and ask for redelivery.

- 構文: asを用いた比較
- 教える価値: asの後に人などが続く比較では、何と何を比べているかを補って読む。
- 読み違えやすい点: 比較対象を人そのものと捉え、相手が支払う料金との比較だと補えないことがある。

## TOP2: 候補2 [T1 / HEAVY] 段落P5

> But having the person receiving the package pay won’t change late deliveries or how arrival times are shared.

- 構文: 動名詞節主語
- 教える価値: 動名詞節が文全体の主語になり、その中に目的語と原形不定詞を含む場合も、節のまとまりを見極める。
- 読み違えやすい点: 長い動名詞節の中のthe personを主語と捉え、文全体の主語と述語のつながりを取り違えることがある。

## 操作(コマンド。`--by` は操作者名)

- AI推奨(TOP1)を了承: `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/redelivery_fee/run_01 --candidates-sha d09c110af7ada425b97589d0b2e6d4950a931b577c33f83913f8ffe24a7b5fcd --by <名前> --choice top1 --accept-ai`
- TOP1を選ぶ: `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/redelivery_fee/run_01 --candidates-sha d09c110af7ada425b97589d0b2e6d4950a931b577c33f83913f8ffe24a7b5fcd --by <名前> --choice top1`
- TOP2を選ぶ(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/redelivery_fee/run_01 --candidates-sha d09c110af7ada425b97589d0b2e6d4950a931b577c33f83913f8ffe24a7b5fcd --by <名前> --choice top2 --reason <理由>`
- 選び直し(TOP1/TOP2をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/redelivery_fee/run_01 --candidates-sha d09c110af7ada425b97589d0b2e6d4950a931b577c33f83913f8ffe24a7b5fcd --by <名前> --choice reselect --reason <理由>`
- 今回は解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/redelivery_fee/run_01 --candidates-sha d09c110af7ada425b97589d0b2e6d4950a931b577c33f83913f8ffe24a7b5fcd --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/redelivery_fee/run_01` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er121_output/family_y_production_01/redelivery_fee/run_01`
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/redelivery_fee/run_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・supportの再生成は行われません)。
