# M1_BENEFIT_CENSUS_01 (OF-168) M1(i)=CMU収録語のみの音素正規化の実益集計

Status: 集計のみ(read-only、API 0、JPY0)。M1は未配線。コマンド: `er075_m1_f1_production_wiring_01_m1_benefit.py --oov-fallback off --out er075_output/m1_f1_production_wiring_01/m1_benefit_01.json`
(`er068_..._offline.py::design_judge` を、`phoneme_ok` をOOV fallback無効[canonicalがCMU未収録なら適用しない]に差替えて呼出し、legacy[Production現行判定]と比較。)

| 項目 | 結果 |
|---|---|
| 対象ペア | 674(HR queue 187 / er021 telemetry 434 / er069 results_02 53) |
| legacy PASS | 34(HR 7 / er021 9 / er069 18) |
| M1(i)で新規受理(legacy非PASS→PASS) | **0件** |
| M1(i)でPASS→非PASS(退行) | 0件 |
| 非PASSのまま | 640 |

所見: 既存の実データでは、CMU収録語のみに限定したM1(i)の実益は0件。Melos(CMU未収録=OOV)由来のASR揺れはM1(i)では救えず、OOV扱い(UDR-1)が実益の鍵であることを再確認(OOV_SAFETY_01.md参照)。F1は単独で価値あり(誤PASS是正)、M1は実益未確認のままOOV判断待ち。
