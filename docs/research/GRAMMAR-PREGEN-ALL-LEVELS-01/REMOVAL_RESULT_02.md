# REMOVAL_RESULT_02 (委任_05B)
- 撤去: `pregen_stage(all_candidates=)`(引数・分岐・docstring)。Grep `all_candidates` in `*.py`(.venv除く): er120系0件(残存は無関係のer003/er005の別変数のみ)。
- 撤去: `expectedFailure` + `KNOWN_DEFECT` 名称 (er128_kp_confirmed_content_02b_test_01.py)。Grep 0件を確認。
- 撤去: 旧「2件採用」test名 `test_two_items_adopted_*`(integration)。Grep 0件。
- 残置: レンダラ(`result_items`のN件描画)は旧2件結果の読取互換のため残置。
