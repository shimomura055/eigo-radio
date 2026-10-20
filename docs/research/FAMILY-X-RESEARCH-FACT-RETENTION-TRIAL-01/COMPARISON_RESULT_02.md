# XRFR eval

(機械採点。gold=gold_02: 2026-10-20 ①E0実走後・候補方式(A〜E)の実走前に作成。gold_01(commit 383beeb22)からの変更はM-A1の1項目のみ)

## 方式×題材 集計

| 方式|題材 | n | KEY保持(Ledger) | KEY保持(下書き) | SEC | CTRL | Fact数平均 | Δ対E0 | フラグ(未判定/創作) | LLM呼出 | 費用JPY | 時間s | 検索 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A|coffee | 2 | 0.583 | 0.583 | None | 1.0 | 17 | -0.5 | 22(0/0) | 2 | 1.042 | 91.8 | 0 |
| A|mey | 2 | 0.667 | 0.667 | 0.5 | 1.0 | 12.5 | -1.5 | 7(0/1) | 2 | 0.961 | 89.4 | 0 |
| A|muse | 2 | 0.75 | 0.75 | 0.667 | 0.0 | 10 | 0 | 4(0/0) | 2 | 0.865 | 83.0 | 0 |
| B|coffee | 2 | 0.75 | 0.75 | None | 1.0 | 14 | -3.5 | 17(0/0) | 2 | 0.865 | 78.9 | 0 |
| B|mey | 2 | 1.0 | 1.0 | 0.5 | 0.5 | 14 | 0 | 8(0/0) | 2 | 0.886 | 93.6 | 0 |
| B|muse | 2 | 0.75 | 0.75 | 0.667 | 0.0 | 12.5 | 2.5 | 2(0/0) | 2 | 0.757 | 74.4 | 0 |
| C|coffee | 2 | 0.667 | 0.667 | None | 1.0 | 17.5 | 0.0 | 18(0/0) | 2 | 1.058 | 94.1 | 0 |
| C|mey | 2 | 0.75 | 0.75 | 0.5 | 1.0 | 14 | 0 | 9(0/0) | 2 | 1.075 | 120.8 | 0 |
| C|muse | 2 | 0.75 | 0.75 | 0.333 | 0.0 | 10 | 0 | 6(0/0) | 2 | 0.935 | 93.6 | 0 |
| D|coffee | 2 | 0.583 | 0.583 | None | 1.0 | 17 | -0.5 | 22(0/0) | 2 | 1.091 | 99.1 | 0 |
| D|mey | 2 | 0.667 | 0.667 | 0.5 | 1.0 | 12.5 | -1.5 | 7(0/1) | 2 | 0.999 | 94.1 | 0 |
| D|muse | 2 | 0.75 | 0.75 | 0.667 | 0.0 | 10 | 0 | 4(0/0) | 2 | 1.034 | 104.6 | 0 |
| E|coffee | 2 | 0.75 | 0.75 | None | 1.0 | 26 | 8.5 | 23(0/0) | 3 | 1.762 | 148.1 | 0 |
| E|mey | 2 | 0.75 | 0.75 | 1.0 | 1.0 | 29.5 | 15.5 | 18(0/0) | 3 | 1.871 | 431.0 | 0 |
| E|muse | 2 | 0.938 | 0.938 | 1.0 | 0.0 | 20 | 10 | 9(0/0) | 3 | 1.455 | 400.7 | 0 |
| E0|coffee | 2 | 0.667 | 0.667 | None | 1.0 | 17.5 | 0.0 | 18(0/0) | 2 | 0.934 | 78.9 | 0 |
| E0|mey | 2 | 0.75 | 0.75 | 0.5 | 1.0 | 14 | 0 | 9(0/0) | 2 | 0.983 | 114.1 | 0 |
| E0|muse | 2 | 0.75 | 0.75 | 0.333 | 0.0 | 10 | 0 | 6(0/0) | 2 | 0.711 | 68.6 | 0 |
| X1|mey | 2 | 0.75 | 0.75 | 0.5 | 1.0 | 13 | -1 | 5(0/1) | 2 | 1.14 | 78.0 | 0 |

## 方式別 機械判定(設計v02 §9-1。最終ラベルはFable)

- A: **REJECTED** unmet=['d:fabrication_unsupported=1'] []
- B: **NOT_VALIDATED_CRITERIA_UNMET** unmet=['b:muse improvement<+0.15 (E0<0.9)', 'b:coffee improvement<+0.15 (E0<0.9)', 'c:mey CTRL regression', 'e:muse delta_facts>+2'] []
- C: **REJECTED** unmet=['a:mey KEY improvement 0.000 < +0.10'] []
- D: **REJECTED** unmet=['d:fabrication_unsupported=1'] []
- E: **REJECTED** unmet=['a:mey KEY improvement 0.000 < +0.10'] []

## gold項目別(各セル)

- A/coffee/s1 (facts=14, {'VERIFIED': 14, 'AMBIGUOUS': 0, 'REJECTED': 0}): K-B1:OK K-B2:MISS[absent_in_draft] K-B3:MISS[absent_in_draft] K-B4:MISS[absent_in_draft] K-B5:OK K-B6:OK K-C1:OK
- A/coffee/s2 (facts=20, {'VERIFIED': 20, 'AMBIGUOUS': 0, 'REJECTED': 0}): K-B1:OK K-B2:MISS[absent_in_draft] K-B3:MISS[absent_in_draft] K-B4:OK K-B5:OK K-B6:OK K-C1:OK
- B/coffee/s1 (facts=17, {'VERIFIED': 16, 'AMBIGUOUS': 1, 'REJECTED': 0}): K-B1:OK K-B2:MISS[absent_in_draft] K-B3:MISS[absent_in_draft] K-B4:OK K-B5:OK K-B6:OK K-C1:OK
- B/coffee/s2 (facts=11, {'VERIFIED': 11, 'AMBIGUOUS': 0, 'REJECTED': 0}): K-B1:OK K-B2:OK K-B3:MISS[absent_in_draft] K-B4:OK K-B5:OK K-B6:OK K-C1:OK
- C/coffee/s1 (facts=14, {'VERIFIED': 13, 'AMBIGUOUS': 1, 'REJECTED': 0}): K-B1:OK K-B2:MISS[absent_in_draft] K-B3:MISS[absent_in_draft] K-B4:OK K-B5:OK K-B6:OK K-C1:OK
- C/coffee/s2 (facts=21, {'VERIFIED': 19, 'AMBIGUOUS': 2, 'REJECTED': 0}): K-B1:OK K-B2:MISS[absent_in_draft] K-B3:MISS[absent_in_draft] K-B4:OK K-B5:OK K-B6:OK K-C1:OK
- D/coffee/s1 (facts=14, {'VERIFIED': 14, 'AMBIGUOUS': 0, 'REJECTED': 0}): K-B1:OK K-B2:MISS[absent_in_draft] K-B3:MISS[absent_in_draft] K-B4:MISS[absent_in_draft] K-B5:OK K-B6:OK K-C1:OK
- D/coffee/s2 (facts=20, {'VERIFIED': 19, 'AMBIGUOUS': 1, 'REJECTED': 0}): K-B1:OK K-B2:MISS[absent_in_draft] K-B3:MISS[absent_in_draft] K-B4:OK K-B5:OK K-B6:OK K-C1:OK
- E/coffee/s1 (facts=21, {'VERIFIED': 20, 'AMBIGUOUS': 1, 'REJECTED': 0}): K-B1:OK K-B2:OK K-B3:MISS[absent_in_draft] K-B4:OK K-B5:OK K-B6:OK K-C1:OK
- E/coffee/s2 (facts=31, {'VERIFIED': 31, 'AMBIGUOUS': 0, 'REJECTED': 0}): K-B1:OK K-B2:MISS[absent_in_draft] K-B3:MISS[absent_in_draft] K-B4:OK K-B5:OK K-B6:OK K-C1:OK
- E0/coffee/s1 (facts=14, {'VERIFIED': 14, 'AMBIGUOUS': 0, 'REJECTED': 0}): K-B1:OK K-B2:MISS[absent_in_draft] K-B3:MISS[absent_in_draft] K-B4:OK K-B5:OK K-B6:OK K-C1:OK
- E0/coffee/s2 (facts=21, {'VERIFIED': 20, 'AMBIGUOUS': 1, 'REJECTED': 0}): K-B1:OK K-B2:MISS[absent_in_draft] K-B3:MISS[absent_in_draft] K-B4:OK K-B5:OK K-B6:OK K-C1:OK
- A/mey/s1 (facts=13, {'VERIFIED': 12, 'AMBIGUOUS': 1, 'REJECTED': 0}): M-A1:OK M-A2:OK M-B1:OK M-B2:MISS[absent_in_draft] M-B3:MISS[absent_in_draft] M-B4:OK M-B5:OK M-C1:OK M-C2:OK M-C3:OK M-C4:OK
- A/mey/s2 (facts=12, {'VERIFIED': 11, 'AMBIGUOUS': 1, 'REJECTED': 0}): M-A1:OK M-A2:OK M-B1:OK M-B2:MISS[absent_in_draft] M-B3:MISS[absent_in_draft] M-B4:OK M-B5:MISS[absent_in_draft] M-C1:OK M-C2:OK M-C3:OK M-C4:OK
- B/mey/s1 (facts=14, {'VERIFIED': 14, 'AMBIGUOUS': 0, 'REJECTED': 0}): M-A1:OK M-A2:OK M-B1:OK M-B2:OK M-B3:OK M-B4:OK M-B5:MISS[absent_in_draft] M-C1:MISS[absent_in_draft] M-C2:MISS[absent_in_draft] M-C3:OK M-C4:OK
- B/mey/s2 (facts=14, {'VERIFIED': 13, 'AMBIGUOUS': 1, 'REJECTED': 0}): M-A1:OK M-A2:OK M-B1:OK M-B2:OK M-B3:OK M-B4:OK M-B5:OK M-C1:MISS[absent_in_draft] M-C2:MISS[absent_in_draft] M-C3:OK M-C4:OK
- C/mey/s1 (facts=12, {'VERIFIED': 9, 'AMBIGUOUS': 3, 'REJECTED': 0}): M-A1:MISS[absent_in_draft] M-A2:OK M-B1:OK M-B2:OK M-B3:MISS[absent_in_draft] M-B4:OK M-B5:MISS[absent_in_draft] M-C1:OK M-C2:OK M-C3:OK M-C4:OK
- C/mey/s2 (facts=16, {'VERIFIED': 16, 'AMBIGUOUS': 0, 'REJECTED': 0}): M-A1:OK M-A2:OK M-B1:OK M-B2:OK M-B3:MISS[absent_in_draft] M-B4:OK M-B5:OK M-C1:OK M-C2:OK M-C3:OK M-C4:OK
- D/mey/s1 (facts=13, {'VERIFIED': 13, 'AMBIGUOUS': 0, 'REJECTED': 0}): M-A1:OK M-A2:OK M-B1:OK M-B2:MISS[absent_in_draft] M-B3:MISS[absent_in_draft] M-B4:OK M-B5:OK M-C1:OK M-C2:OK M-C3:OK M-C4:OK
- D/mey/s2 (facts=12, {'VERIFIED': 11, 'AMBIGUOUS': 1, 'REJECTED': 0}): M-A1:OK M-A2:OK M-B1:OK M-B2:MISS[absent_in_draft] M-B3:MISS[absent_in_draft] M-B4:OK M-B5:MISS[absent_in_draft] M-C1:OK M-C2:OK M-C3:OK M-C4:OK
- E/mey/s1 (facts=29, {'VERIFIED': 28, 'AMBIGUOUS': 1, 'REJECTED': 0}): M-A1:MISS[absent_in_draft] M-A2:OK M-B1:OK M-B2:OK M-B3:MISS[absent_in_draft] M-B4:OK M-B5:OK M-C1:OK M-C2:OK M-C3:OK M-C4:OK
- E/mey/s2 (facts=30, {'VERIFIED': 30, 'AMBIGUOUS': 0, 'REJECTED': 0}): M-A1:OK M-A2:OK M-B1:OK M-B2:OK M-B3:MISS[absent_in_draft] M-B4:OK M-B5:OK M-C1:OK M-C2:OK M-C3:OK M-C4:OK
- E0/mey/s1 (facts=12, {'VERIFIED': 12, 'AMBIGUOUS': 0, 'REJECTED': 0}): M-A1:MISS[absent_in_draft] M-A2:OK M-B1:OK M-B2:OK M-B3:MISS[absent_in_draft] M-B4:OK M-B5:MISS[absent_in_draft] M-C1:OK M-C2:OK M-C3:OK M-C4:OK
- E0/mey/s2 (facts=16, {'VERIFIED': 16, 'AMBIGUOUS': 0, 'REJECTED': 0}): M-A1:OK M-A2:OK M-B1:OK M-B2:OK M-B3:MISS[absent_in_draft] M-B4:OK M-B5:OK M-C1:OK M-C2:OK M-C3:OK M-C4:OK
- X1/mey/s1 (facts=14, {'VERIFIED': 13, 'AMBIGUOUS': 1, 'REJECTED': 0}): M-A1:OK M-A2:OK M-B1:OK M-B2:OK M-B3:MISS[absent_in_draft] M-B4:OK M-B5:MISS[absent_in_draft] M-C1:OK M-C2:OK M-C3:OK M-C4:OK
- X1/mey/s2 (facts=12, {'VERIFIED': 11, 'AMBIGUOUS': 1, 'REJECTED': 0}): M-A1:MISS[absent_in_draft] M-A2:OK M-B1:OK M-B2:OK M-B3:MISS[absent_in_draft] M-B4:OK M-B5:OK M-C1:OK M-C2:OK M-C3:OK M-C4:OK
- A/muse/s1 (facts=11, {'VERIFIED': 11, 'AMBIGUOUS': 0, 'REJECTED': 0}): U-A1:OK U-A2:OK U-B1:OK U-B2:OK U-B3:OK U-B4:MISS[absent_in_draft] U-B6:MISS[absent_in_draft] U-R1:MISS[absent_in_draft] U-B5:MISS[absent_in_draft] U-B7:OK U-S1:OK U-C1:MISS[absent_in_draft]
- A/muse/s2 (facts=9, {'VERIFIED': 8, 'AMBIGUOUS': 1, 'REJECTED': 0}): U-A1:OK U-A2:OK U-B1:OK U-B2:OK U-B3:OK U-B4:MISS[absent_in_draft] U-B6:OK U-R1:OK U-B5:MISS[absent_in_draft] U-B7:OK U-S1:OK U-C1:MISS[absent_in_draft]
- B/muse/s1 (facts=14, {'VERIFIED': 13, 'AMBIGUOUS': 1, 'REJECTED': 0}): U-A1:OK U-A2:OK U-B1:MISS[absent_in_draft] U-B2:OK U-B3:OK U-B4:MISS[absent_in_draft] U-B6:OK U-R1:OK U-B5:MISS[absent_in_draft] U-B7:OK U-S1:OK U-C1:MISS[absent_in_draft]
- B/muse/s2 (facts=11, {'VERIFIED': 11, 'AMBIGUOUS': 0, 'REJECTED': 0}): U-A1:OK U-A2:OK U-B1:MISS[absent_in_draft] U-B2:OK U-B3:OK U-B4:MISS[absent_in_draft] U-B6:OK U-R1:OK U-B5:MISS[absent_in_draft] U-B7:OK U-S1:OK U-C1:MISS[absent_in_draft]
- C/muse/s1 (facts=12, {'VERIFIED': 9, 'AMBIGUOUS': 2, 'REJECTED': 1}): U-A1:OK U-A2:OK U-B1:OK U-B2:OK U-B3:OK U-B4:MISS[absent_in_draft] U-B6:MISS[absent_in_draft] U-R1:OK U-B5:MISS[absent_in_draft] U-B7:MISS[lost_after_draft] U-S1:OK U-C1:MISS[absent_in_draft]
- C/muse/s2 (facts=8, {'VERIFIED': 5, 'AMBIGUOUS': 3, 'REJECTED': 0}): U-A1:OK U-A2:OK U-B1:OK U-B2:OK U-B3:OK U-B4:MISS[absent_in_draft] U-B6:MISS[absent_in_draft] U-R1:OK U-B5:MISS[absent_in_draft] U-B7:MISS[absent_in_draft] U-S1:OK U-C1:MISS[absent_in_draft]
- D/muse/s1 (facts=11, {'VERIFIED': 0, 'AMBIGUOUS': 11, 'REJECTED': 0}): U-A1:OK U-A2:OK U-B1:OK U-B2:OK U-B3:OK U-B4:MISS[absent_in_draft] U-B6:MISS[absent_in_draft] U-R1:MISS[absent_in_draft] U-B5:MISS[absent_in_draft] U-B7:OK U-S1:OK U-C1:MISS[absent_in_draft]
- D/muse/s2 (facts=9, {'VERIFIED': 6, 'AMBIGUOUS': 3, 'REJECTED': 0}): U-A1:OK U-A2:OK U-B1:OK U-B2:OK U-B3:OK U-B4:MISS[absent_in_draft] U-B6:OK U-R1:OK U-B5:MISS[absent_in_draft] U-B7:OK U-S1:OK U-C1:MISS[absent_in_draft]
- E/muse/s1 (facts=21, {'VERIFIED': 19, 'AMBIGUOUS': 1, 'REJECTED': 1}): U-A1:OK U-A2:OK U-B1:OK U-B2:OK U-B3:OK U-B4:OK U-B6:OK U-R1:OK U-B5:OK U-B7:OK U-S1:OK U-C1:MISS[absent_in_draft]
- E/muse/s2 (facts=19, {'VERIFIED': 19, 'AMBIGUOUS': 0, 'REJECTED': 0}): U-A1:OK U-A2:OK U-B1:OK U-B2:OK U-B3:OK U-B4:OK U-B6:MISS[absent_in_draft] U-R1:OK U-B5:OK U-B7:OK U-S1:OK U-C1:MISS[absent_in_draft]
- E0/muse/s1 (facts=12, {'VERIFIED': 11, 'AMBIGUOUS': 0, 'REJECTED': 1}): U-A1:OK U-A2:OK U-B1:OK U-B2:OK U-B3:OK U-B4:MISS[absent_in_draft] U-B6:MISS[absent_in_draft] U-R1:OK U-B5:MISS[absent_in_draft] U-B7:MISS[lost_after_draft] U-S1:OK U-C1:MISS[absent_in_draft]
- E0/muse/s2 (facts=8, {'VERIFIED': 7, 'AMBIGUOUS': 1, 'REJECTED': 0}): U-A1:OK U-A2:OK U-B1:OK U-B2:OK U-B3:OK U-B4:MISS[absent_in_draft] U-B6:MISS[absent_in_draft] U-R1:OK U-B5:MISS[absent_in_draft] U-B7:MISS[absent_in_draft] U-S1:OK U-C1:MISS[absent_in_draft]

## 創作候補フラグ(出典逐語照合が必要)

- A|coffee|s1|F3: causal_stated_by_source -> SUPPORTED
- A|coffee|s1|F5: causal_stated_by_source -> SUPPORTED
- A|coffee|s1|F6: causal_stated_by_source -> SUPPORTED
- A|coffee|s1|F7: causal_stated_by_source -> SUPPORTED
- A|coffee|s1|F8: causal_stated_by_source -> SUPPORTED
- A|coffee|s1|F9: causal_stated_by_source -> SUPPORTED
- A|coffee|s1|F10: causal_stated_by_source -> SUPPORTED
- A|coffee|s1|F11: causal_stated_by_source -> SUPPORTED
- A|coffee|s1|F13: causal_stated_by_source -> SUPPORTED
- A|coffee|s1|F14: causal_stated_by_source -> SUPPORTED
- B|coffee|s1|F4: causal_stated_by_source -> SUPPORTED
- B|coffee|s1|F7: causal_stated_by_source -> SUPPORTED
- B|coffee|s1|F8: causal_stated_by_source -> SUPPORTED
- B|coffee|s1|F9: causal_stated_by_source -> SUPPORTED
- B|coffee|s1|F11: causal_stated_by_source -> SUPPORTED
- B|coffee|s1|F12: causal_stated_by_source -> SUPPORTED
- B|coffee|s1|F13: causal_stated_by_source -> SUPPORTED
- B|coffee|s1|F14: causal_stated_by_source -> SUPPORTED
- B|coffee|s1|F16: causal_stated_by_source -> SUPPORTED
- B|coffee|s1|F17: causal_stated_by_source -> SUPPORTED
- C|coffee|s1|F03: causal_stated_by_source -> SUPPORTED
- C|coffee|s1|F05: causal_stated_by_source -> SUPPORTED
- C|coffee|s1|F06: causal_stated_by_source -> SUPPORTED
- C|coffee|s1|F07: causal_stated_by_source -> SUPPORTED
- C|coffee|s1|F08: causal_stated_by_source -> SUPPORTED
- C|coffee|s1|F09: causal_stated_by_source -> SUPPORTED
- C|coffee|s1|F10: causal_stated_by_source -> SUPPORTED
- C|coffee|s1|F11: causal_stated_by_source -> SUPPORTED
- C|coffee|s1|F13: causal_stated_by_source -> SUPPORTED
- C|coffee|s1|F14: causal_stated_by_source -> SUPPORTED
- D|coffee|s1|F3: causal_stated_by_source -> SUPPORTED
- D|coffee|s1|F5: causal_stated_by_source -> SUPPORTED
- D|coffee|s1|F6: causal_stated_by_source -> SUPPORTED
- D|coffee|s1|F7: causal_stated_by_source -> SUPPORTED
- D|coffee|s1|F8: causal_stated_by_source -> SUPPORTED
- D|coffee|s1|F9: causal_stated_by_source -> SUPPORTED
- D|coffee|s1|F10: causal_stated_by_source -> SUPPORTED
- D|coffee|s1|F11: causal_stated_by_source -> SUPPORTED
- D|coffee|s1|F13: causal_stated_by_source -> SUPPORTED
- D|coffee|s1|F14: causal_stated_by_source -> SUPPORTED
- E0|coffee|s1|F03: causal_stated_by_source -> SUPPORTED
- E0|coffee|s1|F05: causal_stated_by_source -> SUPPORTED
- E0|coffee|s1|F06: causal_stated_by_source -> SUPPORTED
- E0|coffee|s1|F07: causal_stated_by_source -> SUPPORTED
- E0|coffee|s1|F08: causal_stated_by_source -> SUPPORTED
- E0|coffee|s1|F09: causal_stated_by_source -> SUPPORTED
- E0|coffee|s1|F10: causal_stated_by_source -> SUPPORTED
- E0|coffee|s1|F11: causal_stated_by_source -> SUPPORTED
- E0|coffee|s1|F13: causal_stated_by_source -> SUPPORTED
- E0|coffee|s1|F14: causal_stated_by_source -> SUPPORTED
- E|coffee|s1|F03: causal_stated_by_source -> SUPPORTED
- E|coffee|s1|F05: causal_stated_by_source -> SUPPORTED
- E|coffee|s1|F06: causal_stated_by_source -> SUPPORTED
- E|coffee|s1|F07: causal_stated_by_source -> SUPPORTED
- E|coffee|s1|F08: causal_stated_by_source -> SUPPORTED
- E|coffee|s1|F09: causal_stated_by_source -> SUPPORTED
- E|coffee|s1|F10: causal_stated_by_source -> SUPPORTED
- E|coffee|s1|F11: causal_stated_by_source -> SUPPORTED
- E|coffee|s1|F13: causal_stated_by_source -> SUPPORTED
- E|coffee|s1|F14: causal_stated_by_source -> SUPPORTED
- E|coffee|s1|AU04: causal_stated_by_source -> SUPPORTED
- E|coffee|s1|AU06: causal_stated_by_source -> SUPPORTED
- E|coffee|s1|AU07: causal_stated_by_source -> SUPPORTED
- A|coffee|s2|F03: causal_stated_by_source -> SUPPORTED
- A|coffee|s2|F07: causal_stated_by_source -> SUPPORTED
- A|coffee|s2|F08: causal_stated_by_source -> SUPPORTED
- A|coffee|s2|F09: causal_stated_by_source -> SUPPORTED
- A|coffee|s2|F10: causal_stated_by_source -> SUPPORTED
- A|coffee|s2|F11: causal_stated_by_source -> SUPPORTED
- A|coffee|s2|F12: causal_stated_by_source -> SUPPORTED
- A|coffee|s2|F13: causal_stated_by_source -> SUPPORTED
- A|coffee|s2|F14: causal_stated_by_source -> SUPPORTED
- A|coffee|s2|F17: causal_stated_by_source -> SUPPORTED
- A|coffee|s2|F18: causal_stated_by_source -> SUPPORTED
- A|coffee|s2|F19: causal_stated_by_source -> SUPPORTED
- B|coffee|s2|F2: causal_stated_by_source -> SUPPORTED
- B|coffee|s2|F5: causal_stated_by_source -> SUPPORTED
- B|coffee|s2|F6: causal_stated_by_source -> SUPPORTED
- B|coffee|s2|F8: causal_stated_by_source -> SUPPORTED
- B|coffee|s2|F9: causal_stated_by_source -> SUPPORTED
- B|coffee|s2|F10: causal_stated_by_source -> SUPPORTED
- B|coffee|s2|F11: causal_stated_by_source -> SUPPORTED
- C|coffee|s2|F05: causal_stated_by_source -> SUPPORTED
- C|coffee|s2|F08: causal_stated_by_source -> SUPPORTED
- C|coffee|s2|F12: causal_stated_by_source -> SUPPORTED
- C|coffee|s2|F13: causal_stated_by_source -> SUPPORTED
- C|coffee|s2|F14: causal_stated_by_source -> SUPPORTED
- C|coffee|s2|F15: causal_stated_by_source -> SUPPORTED
- C|coffee|s2|F18: causal_stated_by_source -> SUPPORTED
- C|coffee|s2|F21: causal_stated_by_source -> SUPPORTED
- D|coffee|s2|F03: causal_stated_by_source -> SUPPORTED
- D|coffee|s2|F07: causal_stated_by_source -> SUPPORTED
- D|coffee|s2|F08: causal_stated_by_source -> SUPPORTED
- D|coffee|s2|F09: causal_stated_by_source -> SUPPORTED
- D|coffee|s2|F10: causal_stated_by_source -> SUPPORTED
- D|coffee|s2|F11: causal_stated_by_source -> SUPPORTED
- D|coffee|s2|F12: causal_stated_by_source -> SUPPORTED
- D|coffee|s2|F13: causal_stated_by_source -> SUPPORTED
- D|coffee|s2|F14: causal_stated_by_source -> SUPPORTED
- D|coffee|s2|F17: causal_stated_by_source -> SUPPORTED
- D|coffee|s2|F18: causal_stated_by_source -> SUPPORTED
- D|coffee|s2|F19: causal_stated_by_source -> SUPPORTED
- E0|coffee|s2|F05: causal_stated_by_source -> SUPPORTED
- E0|coffee|s2|F08: causal_stated_by_source -> SUPPORTED
- E0|coffee|s2|F12: causal_stated_by_source -> SUPPORTED
- E0|coffee|s2|F13: causal_stated_by_source -> SUPPORTED
- E0|coffee|s2|F14: causal_stated_by_source -> SUPPORTED
- E0|coffee|s2|F15: causal_stated_by_source -> SUPPORTED
- E0|coffee|s2|F18: causal_stated_by_source -> SUPPORTED
- E0|coffee|s2|F21: causal_stated_by_source -> SUPPORTED
- E|coffee|s2|F05: causal_stated_by_source -> SUPPORTED
- E|coffee|s2|F08: causal_stated_by_source -> SUPPORTED
- E|coffee|s2|F12: causal_stated_by_source -> SUPPORTED
- E|coffee|s2|F13: causal_stated_by_source -> SUPPORTED
- E|coffee|s2|F14: causal_stated_by_source -> SUPPORTED
- E|coffee|s2|F15: causal_stated_by_source -> SUPPORTED
- E|coffee|s2|F18: causal_stated_by_source -> SUPPORTED
- E|coffee|s2|F21: causal_stated_by_source -> SUPPORTED
- E|coffee|s2|AU04: causal_stated_by_source -> SUPPORTED
- E|coffee|s2|AU06: causal_stated_by_source -> SUPPORTED
- A|mey|s1|F2: motive_causal_marker -> SUPPORTED
- A|mey|s1|F6: causal_stated_by_source -> SUPPORTED
- A|mey|s1|F8: watch:us_israel_others -> SUPPORTED
- A|mey|s1|F13: causal_stated_by_source -> SUPPORTED
- B|mey|s1|F5: causal_stated_by_source -> SUPPORTED
- B|mey|s1|F6: causal_stated_by_source -> SUPPORTED
- B|mey|s1|F13: causal_stated_by_source -> SUPPORTED
- B|mey|s1|F14: causal_stated_by_source -> SUPPORTED
- C|mey|s1|F2: motive_causal_marker -> SUPPORTED
- C|mey|s1|F7: causal_stated_by_source -> SUPPORTED
- C|mey|s1|F8: causal_stated_by_source,watch:us_israel_others -> SUPPORTED
- C|mey|s1|F9: causal_stated_by_source -> SUPPORTED
- C|mey|s1|F12: causal_stated_by_source -> SUPPORTED
- D|mey|s1|F2: motive_causal_marker -> SUPPORTED
- D|mey|s1|F6: causal_stated_by_source -> SUPPORTED
- D|mey|s1|F8: watch:us_israel_others -> SUPPORTED
- D|mey|s1|F13: causal_stated_by_source -> SUPPORTED
- E0|mey|s1|F2: motive_causal_marker -> SUPPORTED
- E0|mey|s1|F7: causal_stated_by_source -> SUPPORTED
- E0|mey|s1|F8: causal_stated_by_source,watch:us_israel_others -> SUPPORTED
- E0|mey|s1|F9: causal_stated_by_source -> SUPPORTED
- E0|mey|s1|F12: causal_stated_by_source -> SUPPORTED
- E|mey|s1|F2: motive_causal_marker -> SUPPORTED
- E|mey|s1|F7: causal_stated_by_source -> SUPPORTED
- E|mey|s1|F8: causal_stated_by_source,watch:us_israel_others -> SUPPORTED
- E|mey|s1|F9: causal_stated_by_source -> SUPPORTED
- E|mey|s1|F12: causal_stated_by_source -> SUPPORTED
- E|mey|s1|AU03: causal_stated_by_source -> SUPPORTED
- E|mey|s1|AU06: causal_stated_by_source -> SUPPORTED
- E|mey|s1|AU10: causal_stated_by_source -> SUPPORTED
- E|mey|s1|AU11: watch:iran -> SUPPORTED
- E|mey|s1|AU13: causal_stated_by_source -> SUPPORTED
- X1|mey|s1|F05: causal_stated_by_source -> SUPPORTED
- X1|mey|s1|F14: causal_stated_by_source -> SUPPORTED
- A|mey|s2|F02: motive_causal_marker -> SUPPORTED
- A|mey|s2|F06: causal_stated_by_source -> SUPPORTED
- A|mey|s2|F12: motive_causal_marker -> UNSUPPORTED
- B|mey|s2|F5: causal_stated_by_source -> SUPPORTED
- B|mey|s2|F9: causal_stated_by_source -> SUPPORTED
- B|mey|s2|F13: causal_stated_by_source -> SUPPORTED
- B|mey|s2|F14: causal_stated_by_source -> SUPPORTED
- C|mey|s2|F02: motive_causal_marker -> SUPPORTED
- C|mey|s2|F06: causal_stated_by_source -> SUPPORTED
- C|mey|s2|F07: causal_stated_by_source -> SUPPORTED
- C|mey|s2|F10: causal_stated_by_source -> SUPPORTED
- D|mey|s2|F02: motive_causal_marker -> SUPPORTED
- D|mey|s2|F06: causal_stated_by_source -> SUPPORTED
- D|mey|s2|F12: motive_causal_marker -> UNSUPPORTED
- E0|mey|s2|F02: motive_causal_marker -> SUPPORTED
- E0|mey|s2|F06: causal_stated_by_source -> SUPPORTED
- E0|mey|s2|F07: causal_stated_by_source -> SUPPORTED
- E0|mey|s2|F10: causal_stated_by_source -> SUPPORTED
- E|mey|s2|F02: motive_causal_marker -> SUPPORTED
- E|mey|s2|F06: causal_stated_by_source -> SUPPORTED
- E|mey|s2|F07: causal_stated_by_source -> SUPPORTED
- E|mey|s2|F10: causal_stated_by_source -> SUPPORTED
- E|mey|s2|AU04: causal_stated_by_source -> SUPPORTED
- E|mey|s2|AU07: watch:us_israel_others -> SUPPORTED
- E|mey|s2|AU09: watch:iran -> SUPPORTED
- E|mey|s2|AU13: motive_causal_marker -> SUPPORTED
- X1|mey|s2|F1: motive_causal_marker -> SUPPORTED
- X1|mey|s2|F7: watch:us_israel_others -> SUPPORTED
- X1|mey|s2|F8: causal_stated_by_source -> SUPPORTED
- A|muse|s1|F6: causal_stated_by_source -> SUPPORTED
- A|muse|s1|F8: motive_causal_marker -> SUPPORTED
- B|muse|s1|F7: causal_stated_by_source -> SUPPORTED
- C|muse|s1|F7: causal_stated_by_source -> SUPPORTED
- C|muse|s1|F8: motive_causal_marker -> SUPPORTED
- C|muse|s1|F12: motive_causal_marker,causal_stated_by_source -> SUPPORTED
- D|muse|s1|F6: causal_stated_by_source -> SUPPORTED
- D|muse|s1|F8: motive_causal_marker -> SUPPORTED
- E0|muse|s1|F7: causal_stated_by_source -> SUPPORTED
- E0|muse|s1|F8: motive_causal_marker -> SUPPORTED
- E0|muse|s1|F12: motive_causal_marker,causal_stated_by_source -> SUPPORTED
- E|muse|s1|F7: causal_stated_by_source -> SUPPORTED
- E|muse|s1|F8: motive_causal_marker -> SUPPORTED
- E|muse|s1|F12: motive_causal_marker,causal_stated_by_source -> SUPPORTED
- A|muse|s2|F6: motive_causal_marker -> SUPPORTED
- A|muse|s2|F8: motive_causal_marker -> SUPPORTED
- B|muse|s2|F5: causal_stated_by_source -> SUPPORTED
- C|muse|s2|F5: motive_causal_marker -> SUPPORTED
- C|muse|s2|F7: motive_causal_marker -> SUPPORTED
- C|muse|s2|F8: motive_causal_marker -> SUPPORTED
- D|muse|s2|F6: motive_causal_marker -> SUPPORTED
- D|muse|s2|F8: motive_causal_marker -> SUPPORTED
- E0|muse|s2|F5: motive_causal_marker -> SUPPORTED
- E0|muse|s2|F7: motive_causal_marker -> SUPPORTED
- E0|muse|s2|F8: motive_causal_marker -> SUPPORTED
- E|muse|s2|F5: motive_causal_marker -> SUPPORTED
- E|muse|s2|F7: motive_causal_marker -> SUPPORTED
- E|muse|s2|F8: motive_causal_marker -> SUPPORTED
- E|muse|s2|AU02: motive_causal_marker -> SUPPORTED
- E|muse|s2|AU03: causal_stated_by_source -> SUPPORTED
- E|muse|s2|AU11: motive_causal_marker -> SUPPORTED
