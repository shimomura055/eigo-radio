# Part 2 文法解説 Human Review 依頼(Advanced) round 3

- 状態: RESELECT_EXHAUSTED / candidates_sha256: `4f53cda18c2baa0c` / 本文sha: `03b3787d1c4e` / 再選定 2/2回・再抽出 1/1回
- あなたの作業: 本文の中で解説する英文を1つ選びます(AI推奨=TOP1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

- **全候補をNGにして尽きました**。選べる操作: omit(omit=今回は解説を出さない、reextract=本文から候補を再抽出[Step A'' 1 call・上限1回])

## 操作(コマンド。`--by` は操作者名)

- 今回は解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3 --candidates-sha 4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945 --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3`
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・supportの再生成は行われません)。
