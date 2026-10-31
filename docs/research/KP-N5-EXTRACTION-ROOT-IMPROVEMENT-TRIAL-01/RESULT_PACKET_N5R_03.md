# RESULT_PACKET N5R_03 (KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01 委任_03、API 0)
- 内容: 保存済みプール(ev02)に対するcap{7,8,10,12,15}×{R0d,R1d,A9,A10,A13}の決定論集計。新規LLM呼出0、Production変更0。成果=CAP_SENSITIVITY_03.md・ev03/cap_sensitivity_03.json(+rows)・tools/n5r_cap_03.py
- 同時残存(untidi 24反復 / A9・A13は8反復) cap7/8/10/12/15: R0d 0/0/1/6/17、R1d 4/9/18/19/22、A10 11/12/21/20/24、A9 3/3/3/7/8(近似)、A13 3/5/6/8/8
- HR選定: R0d/R1d/A13全cap残存、A10 cap7-8で36/37、A9 cap7-8で10/12,11/12。A0最終7件残存平均: cap7で2.4-3.8、cap15で5.4-6.0
- 整合: R1d 4/18/22 of 24 = RESULT_02一致。保存picksからのcap7再計算も36件不一致0
- 近似: A9のcap>7は保存済みcap7選定+R1d補充(slate再実行なし)。A13はrerank順保存の8反復のみ、held-out対象外
- (1)整合: RESULT_02.md §1・§3 (2)未承認機能なし・flagなし (3)成果物=CAP_SENSITIVITY_03.md(判定なし) (4)撤去/残置なし
- 判定整合: 重大NG=なし
