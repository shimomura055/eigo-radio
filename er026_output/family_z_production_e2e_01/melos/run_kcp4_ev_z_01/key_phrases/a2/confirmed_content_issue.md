# 確定内容の不整合 (INTEGRITY_VIOLATION)

確定内容と音声/ページ/Part 1の出力が一致しません(G2/G3: 確定後に書換えられた、または別訳が表示/読み上げられた)。

- p_37c58c930b / japanese_gloss(ページ表示): 確定値=`人を水中に引き込む` / 観測値=`(ページに表示されていない)` (standard.html,index.html,index.html)

## 次の一手
- 原因がパイプライン側の変更なら: py er128_kp_confirmed_content_01.py restore --run C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_kcp4_ev_z_01 --level a2 --by <名> --reason <理由> (確定値で再finalize。API 0)
- 確定内容そのものを変えたい場合: py er128_kp_confirmed_content_01.py confirm-revise --run C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_kcp4_ev_z_01 --level a2 --by <名> --user-ref <ユーザー発言> --reason ... (ユーザー確認済みの変更のみ)
