# Part 2 文法解説 Human Review 依頼(Advanced) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `7e53201cc0392e89` / 本文sha: `03b3787d1c4e` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 本文の中で解説する英文を1つ選びます(AI推奨=TOP1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

## AI推奨(TOP1): 候補1 [T1 / POSTMOD] 段落P11

> Melos struck the man holding it with his walking stick and ran uphill, their shouts following him.

- 構文: 後置修飾と前置詞句の係り先
- 教える価値: 後置された前置詞句が名詞と動詞のどちらを修飾するか、文の意味から判断する読み方。
- 読み違えやすい点: この前置詞句を「the man」にかかると取り、男性が杖を持っていたという構造に読み違える可能性がある。

## 操作(コマンド。`--by` は操作者名)

- AI推奨(TOP1)を了承: `py er119_kp_human_review_cli_01.py grammar-select --run er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3 --candidates-sha 7e53201cc0392e89a6decbc9dcc72a3cda3aeaa20280b143d0a74d5afdee3933 --by <名前> --choice top1 --accept-ai`
- TOP1を選ぶ: `py er119_kp_human_review_cli_01.py grammar-select --run er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3 --candidates-sha 7e53201cc0392e89a6decbc9dcc72a3cda3aeaa20280b143d0a74d5afdee3933 --by <名前> --choice top1`
- 選び直し(TOP1/TOP2をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3 --candidates-sha 7e53201cc0392e89a6decbc9dcc72a3cda3aeaa20280b143d0a74d5afdee3933 --by <名前> --choice reselect --reason <理由>`
- 今回は解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3 --candidates-sha 7e53201cc0392e89a6decbc9dcc72a3cda3aeaa20280b143d0a74d5afdee3933 --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3`
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・supportの再生成は行われません)。
