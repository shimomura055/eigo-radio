# LEDGER_COMPLETENESS_01: 完全Fact Ledger完全性確認(API前、全テーマ)

方式: FIX01-A/FIX02/ANTENNAと同じ完全台帳方式(見出し正規表現 `^\[(?P<st>[A-Z_]+)(?:\s+-\s+[^\]]*)?\]\s+(?P<id>[^\s:]+):` をprocess内のみ差し替え。`detectors/ledger_restore_01.py` は無変更)。
expected = 行頭が `[` の行数(形式不問) / regex = 上記正規表現に一致する見出し行数 / parsed = `parse_ledger_text` のFact件数。3者一致かつIDに重複なし、をAPI前の必須条件とし、driverは各セル実行時にも再assertする(不一致ならAPI前に停止)。

| Theme | 台帳path | sha256(先頭12) | expected | regex | parsed | 判定 | 状態 | Fact ID一覧 |
|---|---|---|---|---|---|---|---|---|
| meta | `runs/meta/new/research_ledger/verified_fact_ledger.txt` | 6e271bb24fdf | 15 | 15 | 15 | PASS | {'VERIFIED': 15} | MUSE-HC-001, MUSE-HC-002, MUSE-HC-003, MUSE-HC-004, MUSE-HC-005, MUSE-HC-006, MUSE-HC-007, MUSE-HC-008, MUSE-HC-009, MUSE-HC-010, MUSE-HC-011, MUSE-HC-012, MUSE-HC-013, MUSE-HC-014, MUSE-HC-015 |
| hormuz | `runs/hormuz/new/research_ledger/verified_fact_ledger.txt` | 83b2a09b99b2 | 12 | 12 | 12 | PASS | {'VERIFIED': 12} | HF-001, HF-002, HF-003, HF-004, HF-005, HF-006, HF-007, HF-008, HF-009, HF-010, HF-011, HF-012 |
| space_weapons | `runs/space_weapons/new/research_ledger/verified_fact_ledger.txt` | 2ebdce8660fb | 22 | 22 | 22 | PASS | {'VERIFIED': 22} | F-001, F-002, F-003, F-004, F-005, F-006, F-007, F-008, F-009, F-010, F-011, F-012, F-013, F-014, F-015, F-016, F-017, F-018, F-019, F-020, F-021, F-024 |
| small_bag | `runs/small_bag/new/research_ledger/verified_fact_ledger.txt` | f011dc266e0d | 6 | 6 | 6 | PASS | {'VERIFIED': 6} | MB-01, MB-02, MB-03, MB-04, MB-05, MB-06 |
| byd_recall | `runs/byd_recall/new/research_ledger/verified_fact_ledger.txt` | a7a2d0d910a6 | 11 | 11 | 11 | PASS | {'VERIFIED': 11} | BYD-RECALL-01, BYD-RECALL-02, BYD-RECALL-03, BYD-RECALL-04, BYD-RECALL-05, BYD-RECALL-06, BYD-RECALL-07, BYD-RECALL-08, BYD-RECALL-09, BYD-RECALL-10, BYD-RECALL-11 |
| streaming_price | `runs/streaming_price/new/research_ledger/verified_fact_ledger.txt` | 6488ef82b057 | 7 | 7 | 7 | PASS | {'AMBIGUOUS': 2, 'VERIFIED': 5} | F01, F02, F03, F04, F05, F06, F07 |
| openai_copyright | `runs/openai_copyright/new/research_ledger/verified_fact_ledger.txt` | 870034d74950 | 8 | 8 | 8 | PASS | {'VERIFIED': 8} | F1, F2, F3, F4, F5, F6, F7, F8 |
| semiconductor_earnings | `runs/semiconductor_earnings/new/research_ledger/verified_fact_ledger.txt` | f45eb25bb7ab | 6 | 6 | 6 | PASS | {'AMBIGUOUS': 1, 'VERIFIED': 5} | F1, F2, F3, F4, F5, F6 |

注記: streaming_price(AMBIGUOUS 1件)・semiconductor_earnings(AMBIGUOUS 1件)は従来パーサの見出し正規表現では落ちる形式(`[AMBIGUOUS - ...]`)だが、完全台帳方式で全件取得できた。space_weapons の Fact ID は F-022/F-023 が台帳ファイル自体に存在しない(F-021 の次が F-024。expected=parsed=22 でパーサ欠落ではない)。
全8テーマ PASS。1件でも不一致ならAPIを呼ばない規則に該当なし。
