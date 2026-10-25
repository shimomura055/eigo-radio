# OPEN517_PROD_PARITY_01(Production関数での base+F1F2 再現一致確認。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_09、2026-10-25、API 0・実費0円)
## 結論
**一致(差分0)**。委任_08が『pin `89b630bd1` の Production + proto v4 `apply_in_process`』で作った `base+F1F2`(F12)列と、07A commit(`5e50613f5`)後のHEAD Production関数(既定値=523/524 ON、および523/524 OFF)は、同じ入力1,232件で**判定(state・reason・label・warnings)が完全一致**した。
- 再現: `PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open517_prod_parity_01.py`(自分で3モードを子processで実行。決定的=2回実行で出力sha256同一 `4ff34c39…c7e52`)。出力=`open517_prod_parity_01.out.json`。
- 比較の構成: (1)`pin_v4`=pin snapshot(`git archive 89b630bd1`)の Production + `proto_value_gate_fix_04.apply_in_process()`(委任_08と同一) (2)`head_default`=現HEADのProduction(`READING_MATCH_FINAL_GATE=True`/`KANA_WORD_BOUNDARY_CHECK=True`/`WEAK_KANA_REGION_COMPAT=True`) (3)`head_off`=HEAD Productionで523/524のみOFF(F1+F2のみ=proto v4と同じ合格範囲)。
## 入力(委任_08/07Aが使った凍結データ)
| 群 | 件数 | 出典 | pin_v4 vs head_default | pin_v4 vs head_off |
|---|---|---|---|---|
| 月題12転写(attempt1-3×{保存+再転写3}) | 12 | eval_b_light_api0_02.out.json `moon` | 差分0 | 差分0 |
| N-3 30 clip(意図的誤読) | 30 | 同 `n3` | 0 | 0 |
| 実Production履歴P-S対 | 43 | 同 `hist` | 0 | 0 |
| Melos preview | 1 | 同 `melos` | 0 | 0 |
| 合成負例(V1/M3/FB) | 91 | 同 `synthetic_negative` | 0 | 0 |
| P-4 実attempt(正常143を含む) | 562 | attempt_pool_01.json | 0 | 0 |
| 未知データ | 493 | unknown_pool_02.json | 0 | 0 |
| 合計 | **1,232** | | **0** | **0** |
- 委任_08の保存列との照合: (a)F12列でPrimary PASS(kind=primary)の14件は pin_v4 のstage判定と一致(不一致0) (b)合成負例91件の `F12_pass`(Secondary受理を含む08の `final()` 規則)は head_off のstage+同規則で再現(不一致0。最初の版は『NG_SECONDARY_UNAVAILABLEのときだけSecondary受理』の規則を省いていたため3件見かけの不一致が出たが、**評価側の記述漏れ**でProduction差ではない。規則を揃えて0)。
- 07A範囲(1264件+合成15,877件)は `eval_open517_api0_prod_01.py` で別途再確認: 出力sha256 `eca28287…f5ee` が07A報告と同一(R-5追加後も不変)。
## 差分の原因(なし)/ 評価側の前提差
- Production側の不具合: **なし**(差分0)。
- 評価側の前提差として記録: (1)委任_08は07A未commit時点(`prod07a_committed_at_eval=false`)でpin snapshot+protoにより『F1+F2適用後Production』を代表させた。現HEADのProductionで直接再判定しても同一であることを本書で確認(proto v4とProductionの一致は07Aでも1264件で確認済み、今回は08固有の入力集合へ拡張)。(2)OPEN-523/524(合格を狭める)はhead_defaultでも本入力集合に差分を生まなかった(07A評価の1264+合成で差が出たのは『三日目』↔『みっかかん』1件・合成42件で、いずれも本集合には存在しない)。
- 範囲外(未実施): 委任_08のN-1 150対(Secondary=原稿の最悪ケース)・β(composite)列は DEV protoのみで Production には存在しないため対象外(βは未採用・未配線)。
