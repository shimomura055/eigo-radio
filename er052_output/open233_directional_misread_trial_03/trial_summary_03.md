# trial_summary_03(事実のみ、Status判定はFable)

## 合格基準チェック(8行)

| 基準 | X | X根拠 | Y | Y根拠 |
|---|---|---|---|---|
| 1 HC-012 3/3維持 | 未達 | 1/3 rep0=NOT_MENTIONED | 未達 | 0/3 rep0=NOT_MENTIONED |
| 2 A5-0 3/3維持 | 未達 | 1/3 rep0=UNCLEAR | 未達 | 0/3 rep0=UNCLEAR |
| 3 D61 2/3以上 | 充足 | 2/3 rep0=SAME | 充足 | 2/3 rep0=NOT_MENTIONED |
| 4 held-out重大例 平均2/3以上かつ全例1/3以上 | 充足 | {'mean': 0.6667, 'min': 0.3333, 'per_item': {'H-G1': '2/3', 'H-G2': '2/3', 'H-G3': '3/3', 'H-G4': '1/3'}} | 未達 | {'mean': 0.75, 'min': 0.0, 'per_item': {'H-G1': '3/3', 'H-G2': '3/3', 'H-G3': '3/3', 'H-G4': '0/3'}} |
| 5 正常文+held-out正常例 不要な重大判定0 | 未達 | 1/49 ids=['H-F2'] (全repeat['H-F2']) | 未達 | 1/49 ids=['H-F1'] (全repeat['H-F1']) |
| 6 不要Rewrite見込み0件/run | 未達 | {'low': 0.068, 'mid': 0.152, 'high': 0.623} | 未達 | {'low': 0.068, 'mid': 0.152, 'high': 0.623} |
| 7 新たな重大見逃し0(前回REVERSED→今回非REVERSED) | 未達 | {'new_misses': ['G-01', 'G-02', 'S-07', 'S-12'], 'outside_event_list_ref': []} | 未達 | {'new_misses': ['G-01', 'G-02', 'S-12', 'S-13'], 'outside_event_list_ref': []} |
| 8 前回誤爆3件(F-09/F-10/F-19)再発なし | 充足 | {'F-09': ['SAME', 'SAME', 'SAME'], 'F-10': ['SAME', 'SAME', 'SAME'], 'F-19': ['NOT_MENTIONED', 'SAME', 'NOT_MENTIONED']} | 充足 | {'F-09': ['SAME', 'SAME', 'SAME'], 'F-10': ['SAME', 'SAME', 'SAME'], 'F-19': ['NOT_MENTIONED', 'UNCLEAR', 'UNCLEAR']} |

## 構成X: 実費4.5262円 / calls 261 / items 73

### gold
```
{
 "G-01": {
  "name": "HC-012",
  "rep0": "NOT_MENTIONED",
  "compares": [
   "NOT_MENTIONED",
   "REVERSED",
   "NOT_MENTIONED"
  ],
  "k": 1,
  "n": 3
 },
 "G-02": {
  "name": "A5-0",
  "rep0": "UNCLEAR",
  "compares": [
   "UNCLEAR",
   "REVERSED",
   "UNCLEAR"
  ],
  "k": 1,
  "n": 3
 },
 "G-03": {
  "name": "D61",
  "rep0": "SAME",
  "compares": [
   "SAME",
   "REVERSED",
   "REVERSED"
  ],
  "k": 2,
  "n": 3
 }
}
```
### held_gold
```
{
 "items": {
  "H-G1": {
   "rep0": "SAME",
   "compares": [
    "SAME",
    "REVERSED",
    "REVERSED"
   ],
   "k": 2,
   "n": 3
  },
  "H-G2": {
   "rep0": "SAME",
   "compares": [
    "SAME",
    "REVERSED",
    "REVERSED"
   ],
   "k": 2,
   "n": 3
  },
  "H-G3": {
   "rep0": "REVERSED",
   "compares": [
    "REVERSED",
    "REVERSED",
    "REVERSED"
   ],
   "k": 3,
   "n": 3
  },
  "H-G4": {
   "rep0": "NOT_MENTIONED",
   "compares": [
    "NOT_MENTIONED",
    "REVERSED",
    "NOT_MENTIONED"
   ],
   "k": 1,
   "n": 3
  }
 },
 "mean_k_rate": 0.6667,
 "min_k_rate": 0.3333
}
```
### normal_pool
```
{
 "n": 49,
 "n_held_normal": 6,
 "false_reversal": 1,
 "false_reversal_ids": [
  "H-F2"
 ],
 "rate_rep0": 0.0204,
 "rate_all_repeats": 0.0448,
 "false_reversal_any_repeat_ids": [
  "H-F2"
 ]
}
```
### prev_false_alarms
```
{
 "F-09": {
  "rep0": "SAME",
  "compares": [
   "SAME",
   "SAME",
   "SAME"
  ],
  "k": 0,
  "n": 3,
  "recurred": false
 },
 "F-10": {
  "rep0": "SAME",
  "compares": [
   "SAME",
   "SAME",
   "SAME"
  ],
  "k": 0,
  "n": 3,
  "recurred": false
 },
 "F-19": {
  "rep0": "NOT_MENTIONED",
  "compares": [
   "NOT_MENTIONED",
   "SAME",
   "NOT_MENTIONED"
  ],
  "k": 0,
  "n": 3,
  "recurred": false
 }
}
```
### fluctuation
```
{
 "n_multi": 19,
 "all_agree": 7,
 "agree_rate": 0.3684,
 "disagree_ids": [
  "F-19",
  "G-01",
  "G-02",
  "G-03",
  "G-04",
  "G-05",
  "G-06",
  "H-F1",
  "H-F4",
  "H-G1",
  "H-G2",
  "H-G4"
 ]
}
```
### fallback
```
{
 "items_with_fallback": 49,
 "repeats_with_fallback": 63,
 "repeat_fallback_rate": 0.5676,
 "fallback_calls": 120,
 "fallback_ids": [
  {
   "id": "F-01",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "UNCHANGED",
      "compare": "UNCLEAR"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "F-02",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "F-03",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "F-04",
   "compares": [
    "UNCLEAR"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "UNCHANGED",
      "compare": "UNCLEAR"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "UNCLEAR",
      "compare": "UNCLEAR"
     }
    ]
   ]
  },
  {
   "id": "F-06",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "F-07",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "F-08",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "F-14",
   "compares": [
    "UNCLEAR"
   ],
   "details": [
    [
     {
      "subject_x": "ホルムズ海峡を通るすべての貨物への20％の償還要求",
      "phase": "SINGLE",
      "ledger_state": "STARTED",
      "article_state": "AVAILABLE",
      "compare": "UNCLEAR"
     }
    ]
   ]
  },
  {
   "id": "F-19",
   "compares": [
    "NOT_MENTIONED",
    "SAME",
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "契約スタッフによる電話テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "F-21",
   "compares": [
    "SAME"
   ],
   "details": [
    [
     {
      "subject_x": "Brent原油先物価格",
      "phase": "SINGLE",
      "ledger_state": "INCREASED",
      "article_state": "INCREASED",
      "compare": "SAME"
     }
    ]
   ]
  },
  {
   "id": "G-01",
   "compares": [
    "NOT_MENTIONED",
    "REVERSED",
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "契約スタッフによる電話テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "UNCHANGED",
      "compare": "UNCLEAR"
     },
     {
      "subject_x": "電話機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "G-03",
   "compares": [
    "SAME",
    "REVERSED",
    "REVERSED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "DECREASED",
      "compare": "SAME"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "Brent先物の上げ幅",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "Brent先物の価格",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "DECREASED",
      "compare": "REVERSED"
     }
    ],
    [
     {
      "subject_x": "Brent先物の上げ幅",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "Brent先物の水準",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "DECREASED",
      "compare": "REVERSED"
     }
    ]
   ]
  },
  {
   "id": "G-04",
   "compares": [
    "NOT_MENTIONED",
    "UNCLEAR",
    "UNCLEAR"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "G-05",
   "compares": [
    "REVERSED",
    "SAME",
    "SAME"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "INCREASED",
      "compare": "REVERSED"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "INCREASED",
      "compare": "SAME"
     }
    ]
   ]
  },
  {
   "id": "G-06",
   "compares": [
    "NOT_MENTIONED",
    "UNCLEAR",
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "契約スタッフによる電話テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "H-F2",
   "compares": [
    "REVERSED",
    "REVERSED",
    "REVERSED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "DECREASED",
      "compare": "SAME"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "DECREASED",
      "compare": "REVERSED"
     }
    ],
    [
     {
      "subject_x": "Brent先物の上げ幅",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "DECREASED",
      "compare": "SAME"
     },
     {
      "subject_x": "Brent先物の価格",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "DECREASED",
      "compare": "REVERSED"
     }
    ]
   ]
  },
  {
   "id": "H-F3",
   "compares": [
    "UNCLEAR",
    "UNCLEAR",
    "UNCLEAR"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "UNCHANGED",
      "compare": "UNCLEAR"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "UNCHANGED",
      "compare": "UNCLEAR"
     }
    ],
    [
     {
      "subject_x": "Brent先物の上げ幅",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "UNCHANGED",
      "compare": "UNCLEAR"
     },
     {
      "subject_x": "Brent先物の価格",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "UNCHANGED",
      "compare": "UNCLEAR"
     }
    ],
    [
     {
      "subject_x": "Brent先物の上げ幅",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "UNCHANGED",
      "compare": "UNCLEAR"
     },
     {
      "subject_x": "Brent先物の水準",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "UNCHANGED",
      "compare": "UNCLEAR"
     }
    ]
   ]
  },
  {
   "id": "H-F4",
   "compares": [
    "UNCLEAR",
    "UNCLEAR",
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "ENDED",
      "compare": "UNCLEAR"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "ENDED",
      "compare": "UNCLEAR"
     }
    ],
    [
     {
      "subject_x": "Brent先物の上げ幅",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "Brent先物の水準",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "ENDED",
      "compare": "UNCLEAR"
     }
    ]
   ]
  },
  {
   "id": "H-F5",
   "compares": [
    "NOT_MENTIONED",
    "NOT_MENTIONED",
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "Brent先物の上げ幅",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "Brent先物の価格",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "UNCLEAR",
      "compare": "UNCLEAR"
     }
    ],
    [
     {
      "subject_x": "Brent先物の上げ幅",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "Brent先物の水準",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "H-G1",
   "compares": [
    "SAME",
    "REVERSED",
    "REVERSED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "DECREASED",
      "compare": "SAME"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "Brent先物の上げ幅",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "DECREASED",
      "compare": "SAME"
     },
     {
      "subject_x": "Brent先物の価格",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "DECREASED",
      "compare": "REVERSED"
     }
    ],
    [
     {
      "subject_x": "Brent先物の上げ幅",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "Brent先物の水準",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "DECREASED",
      "compare": "REVERSED"
     }
    ]
   ]
  },
  {
   "id": "H-G3",
   "compares": [
    "REVERSED",
    "REVERSED",
    "REVERSED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "DECREASED",
      "compare": "SAME"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "DECREASED",
      "compare": "REVERSED"
     }
    ]
   ]
  },
  {
   "id": "H-G4",
   "compares": [
    "NOT_MENTIONED",
    "REVERSED",
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "契約スタッフによる電話テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "AVAILABLE",
      "compare": "UNCLEAR"
     },
     {
      "subject_x": "電話機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-01",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-02",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-03",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-04",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-05",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-06",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-07",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-08",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-09",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-10",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-11",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-12",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-13",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-14",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-15",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-16",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-17",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "ND-04",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "human conciergeテスト",
      "phase": "SINGLE",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "ND-05",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "human conciergeテスト",
      "phase": "SINGLE",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "S-01",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "UNCHANGED",
      "compare": "UNCLEAR"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "S-02",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "UNCHANGED",
      "compare": "UNCLEAR"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "S-03",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "UNCLEAR",
      "compare": "UNCLEAR"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "S-04",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "UNCLEAR",
      "compare": "UNCLEAR"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "S-05",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "S-09",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "20％の米国償還料",
      "phase": "SINGLE",
      "ledger_state": "ENDED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "S-12",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "契約スタッフによる電話発信テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     },
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "S-14",
   "compares": [
    "REVERSED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent原油先物価格",
      "phase": "SINGLE",
      "ledger_state": "INCREASED",
      "article_state": "DECREASED",
      "compare": "REVERSED"
     }
    ]
   ]
  }
 ],
 "summary_fallback_calls": 120,
 "fallback_cost_jpy": null
}
```
### phase
```
{
 "article_phase_distribution": {
  "UNSPECIFIED": 47,
  "INTERIM": 29,
  "FINAL": 28,
  "None": 7
 },
 "expected_phase_n": 0,
 "expected_phase_match": null,
 "phase_repeat_items": 19,
 "phase_repeat_agree_rate": 0.4737
}
```
### rep0_distribution
```
{
 "NOT_MENTIONED": 40,
 "UNCLEAR": 7,
 "SAME": 13,
 "LEDGER_NO_DIRECTION": 7,
 "REVERSED": 6
}
```
### ledger_side / per_run
```
{
 "ledger": {
  "n_ledger_reps": 30,
  "has_direction_accuracy": 0.8667,
  "event_match_rate": 0.6923,
  "state_accuracy_given_match": 1.0,
  "ledger_phase_n": 27,
  "ledger_phase_accuracy": 0.8889
 },
 "per_run": {
  "jpy_per_call": 0.01734,
  "fallback_calls_per_repeat": 1.0811,
  "levels": {
   "low": {
    "units_per_run": 3.33,
    "added_calls": 20.6,
    "added_jpy": 0.357,
    "unneeded_rewrite_per_run": 0.068
   },
   "mid": {
    "units_per_run": 7.46,
    "added_calls": 29.19,
    "added_jpy": 0.506,
    "unneeded_rewrite_per_run": 0.152
   },
   "high": {
    "units_per_run": 30.56,
    "added_calls": 77.27,
    "added_jpy": 1.34,
    "unneeded_rewrite_per_run": 0.623
   }
  }
 }
}
```
### 前回比(TRIAL-02)

| 項目 | 前回(TRIAL-02) | 今回 |
|---|---|---|
| G-01 検出k/3 | 3 | 1 |
| G-02 検出k/3 | 3 | 1 |
| G-03 検出k/3 | 0 | 2 |
| 正常文 誤REVERSED(rep0) | 0 [] | 1 ['H-F2'] |
| UNCLEAR(rep0) | 6 | 7 |
| 実費(円) | 2.081872 | 4.5262 (差 2.4443) |

項目数 前回63 / 今回73、今回のみのid: ['H-F1', 'H-F2', 'H-F3', 'H-F4', 'H-F5', 'H-F6', 'H-G1', 'H-G2', 'H-G3', 'H-G4']
REVERSEDになった: ['G-05', 'S-14']
REVERSEDでなくなった: ['G-01', 'G-02', 'S-07', 'S-12']

rep0変化id一覧:
- F-04: NOT_MENTIONED -> UNCLEAR
- F-07: UNCLEAR -> NOT_MENTIONED
- F-11: UNCLEAR -> SAME
- F-13: UNCLEAR -> SAME
- F-14: SAME -> UNCLEAR
- F-19: SAME -> NOT_MENTIONED
- F-20: SAME_FAMILY -> SAME
- G-01: REVERSED -> NOT_MENTIONED
- G-02: REVERSED -> UNCLEAR
- G-03: NOT_MENTIONED -> SAME
- G-05: SAME -> REVERSED
- G-06: UNCLEAR -> NOT_MENTIONED
- N-02: UNCLEAR -> NOT_MENTIONED
- S-07: REVERSED -> SAME
- S-12: REVERSED -> NOT_MENTIONED
- S-14: NOT_MENTIONED -> REVERSED

## 構成Y: 実費3.566709円 / calls 199 / items 73

### gold
```
{
 "G-01": {
  "name": "HC-012",
  "rep0": "NOT_MENTIONED",
  "compares": [
   "NOT_MENTIONED",
   "UNCLEAR",
   "NOT_MENTIONED"
  ],
  "k": 0,
  "n": 3
 },
 "G-02": {
  "name": "A5-0",
  "rep0": "UNCLEAR",
  "compares": [
   "UNCLEAR",
   "UNCLEAR",
   "UNCLEAR"
  ],
  "k": 0,
  "n": 3
 },
 "G-03": {
  "name": "D61",
  "rep0": "NOT_MENTIONED",
  "compares": [
   "NOT_MENTIONED",
   "REVERSED",
   "REVERSED"
  ],
  "k": 2,
  "n": 3
 }
}
```
### held_gold
```
{
 "items": {
  "H-G1": {
   "rep0": "REVERSED",
   "compares": [
    "REVERSED",
    "REVERSED",
    "REVERSED"
   ],
   "k": 3,
   "n": 3
  },
  "H-G2": {
   "rep0": "REVERSED",
   "compares": [
    "REVERSED",
    "REVERSED",
    "REVERSED"
   ],
   "k": 3,
   "n": 3
  },
  "H-G3": {
   "rep0": "REVERSED",
   "compares": [
    "REVERSED",
    "REVERSED",
    "REVERSED"
   ],
   "k": 3,
   "n": 3
  },
  "H-G4": {
   "rep0": "NOT_MENTIONED",
   "compares": [
    "NOT_MENTIONED",
    "UNCLEAR",
    "NOT_MENTIONED"
   ],
   "k": 0,
   "n": 3
  }
 },
 "mean_k_rate": 0.75,
 "min_k_rate": 0.0
}
```
### normal_pool
```
{
 "n": 49,
 "n_held_normal": 6,
 "false_reversal": 1,
 "false_reversal_ids": [
  "H-F1"
 ],
 "rate_rep0": 0.0204,
 "rate_all_repeats": 0.0149,
 "false_reversal_any_repeat_ids": [
  "H-F1"
 ]
}
```
### prev_false_alarms
```
{
 "F-09": {
  "rep0": "SAME",
  "compares": [
   "SAME",
   "SAME",
   "SAME"
  ],
  "k": 0,
  "n": 3,
  "recurred": false
 },
 "F-10": {
  "rep0": "SAME",
  "compares": [
   "SAME",
   "SAME",
   "SAME"
  ],
  "k": 0,
  "n": 3,
  "recurred": false
 },
 "F-19": {
  "rep0": "NOT_MENTIONED",
  "compares": [
   "NOT_MENTIONED",
   "UNCLEAR",
   "UNCLEAR"
  ],
  "k": 0,
  "n": 3,
  "recurred": false
 }
}
```
### fluctuation
```
{
 "n_multi": 19,
 "all_agree": 10,
 "agree_rate": 0.5263,
 "disagree_ids": [
  "F-19",
  "G-01",
  "G-03",
  "G-04",
  "G-06",
  "H-F1",
  "H-F2",
  "H-F4",
  "H-G4"
 ]
}
```
### fallback
```
{
 "items_with_fallback": 48,
 "repeats_with_fallback": 64,
 "repeat_fallback_rate": 0.5766,
 "fallback_calls": 64,
 "fallback_ids": [
  {
   "id": "F-01",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "F-02",
   "compares": [
    "UNCLEAR"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "UNCHANGED",
      "compare": "UNCLEAR"
     }
    ]
   ]
  },
  {
   "id": "F-03",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "F-04",
   "compares": [
    "UNCLEAR"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "UNCHANGED",
      "compare": "UNCLEAR"
     }
    ]
   ]
  },
  {
   "id": "F-06",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "F-07",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "F-08",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "F-19",
   "compares": [
    "NOT_MENTIONED",
    "UNCLEAR",
    "UNCLEAR"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "契約スタッフによる電話テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "PAUSED",
      "compare": "UNCLEAR"
     }
    ]
   ]
  },
  {
   "id": "F-21",
   "compares": [
    "SAME"
   ],
   "details": [
    [
     {
      "subject_x": "Brent原油先物価格",
      "phase": "SINGLE",
      "ledger_state": "INCREASED",
      "article_state": "INCREASED",
      "compare": "SAME"
     }
    ]
   ]
  },
  {
   "id": "G-01",
   "compares": [
    "NOT_MENTIONED",
    "UNCLEAR",
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "契約スタッフによる電話テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "G-03",
   "compares": [
    "NOT_MENTIONED",
    "REVERSED",
    "REVERSED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "Brent先物の価格",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "DECREASED",
      "compare": "REVERSED"
     }
    ],
    [
     {
      "subject_x": "Brent先物の水準",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "DECREASED",
      "compare": "REVERSED"
     }
    ]
   ]
  },
  {
   "id": "G-04",
   "compares": [
    "NOT_MENTIONED",
    "UNCLEAR",
    "UNCLEAR"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "Brent先物の価格",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "UNCLEAR",
      "compare": "UNCLEAR"
     }
    ]
   ]
  },
  {
   "id": "G-06",
   "compares": [
    "NOT_MENTIONED",
    "UNCLEAR",
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "契約スタッフによる電話テスト",
      "phase": "INTERIM",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "H-F1",
   "compares": [
    "REVERSED",
    "UNCLEAR",
    "UNCLEAR"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物の水準",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "UNCLEAR",
      "compare": "UNCLEAR"
     }
    ]
   ]
  },
  {
   "id": "H-F2",
   "compares": [
    "SAME",
    "NOT_MENTIONED",
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物の上げ幅",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "Brent先物の上げ幅",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "H-F3",
   "compares": [
    "UNCLEAR",
    "UNCLEAR",
    "UNCLEAR"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "UNCHANGED",
      "compare": "UNCLEAR"
     }
    ],
    [
     {
      "subject_x": "Brent先物の価格",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "UNCHANGED",
      "compare": "UNCLEAR"
     }
    ],
    [
     {
      "subject_x": "Brent先物の水準",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "UNCHANGED",
      "compare": "UNCLEAR"
     }
    ]
   ]
  },
  {
   "id": "H-F4",
   "compares": [
    "UNCLEAR",
    "NOT_MENTIONED",
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "ENDED",
      "compare": "UNCLEAR"
     }
    ],
    [
     {
      "subject_x": "Brent先物の上げ幅",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "Brent先物の上げ幅",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "H-F5",
   "compares": [
    "NOT_MENTIONED",
    "NOT_MENTIONED",
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "Brent先物の価格",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "Brent先物の水準",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "H-G1",
   "compares": [
    "REVERSED",
    "REVERSED",
    "REVERSED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "DECREASED",
      "compare": "REVERSED"
     }
    ],
    [
     {
      "subject_x": "Brent先物の価格",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "DECREASED",
      "compare": "REVERSED"
     }
    ]
   ]
  },
  {
   "id": "H-G3",
   "compares": [
    "REVERSED",
    "REVERSED",
    "REVERSED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "DECREASED",
      "compare": "REVERSED"
     }
    ],
    [
     {
      "subject_x": "Brent先物の水準",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "DECREASED",
      "compare": "REVERSED"
     }
    ]
   ]
  },
  {
   "id": "H-G4",
   "compares": [
    "NOT_MENTIONED",
    "UNCLEAR",
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ],
    [
     {
      "subject_x": "電話機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-01",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-02",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-03",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-04",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-05",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-06",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-07",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-08",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-09",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-10",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-11",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-12",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-13",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-14",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-15",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-16",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "N-17",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "ND-04",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "human conciergeテスト",
      "phase": "SINGLE",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "ND-05",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "human conciergeテスト",
      "phase": "SINGLE",
      "ledger_state": "STARTED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "S-01",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "S-02",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "S-03",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "INTERIM",
      "ledger_state": "DECREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "S-04",
   "compares": [
    "UNCLEAR"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "UNCLEAR",
      "compare": "UNCLEAR"
     }
    ]
   ]
  },
  {
   "id": "S-05",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent先物",
      "phase": "FINAL",
      "ledger_state": "INCREASED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "S-08",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "20％の米国償還料",
      "phase": "SINGLE",
      "ledger_state": "ENDED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "S-12",
   "compares": [
    "NOT_MENTIONED"
   ],
   "details": [
    [
     {
      "subject_x": "電話発信機能",
      "phase": "FINAL",
      "ledger_state": "PAUSED",
      "article_state": "NOT_MENTIONED",
      "compare": "NOT_MENTIONED"
     }
    ]
   ]
  },
  {
   "id": "S-14",
   "compares": [
    "REVERSED"
   ],
   "details": [
    [
     {
      "subject_x": "Brent原油先物価格",
      "phase": "SINGLE",
      "ledger_state": "INCREASED",
      "article_state": "DECREASED",
      "compare": "REVERSED"
     }
    ]
   ]
  }
 ],
 "summary_fallback_calls": 64,
 "fallback_cost_jpy": null
}
```
### phase
```
{
 "article_phase_distribution": {
  "UNSPECIFIED": 43,
  "FINAL": 33,
  "INTERIM": 28,
  "None": 7
 },
 "expected_phase_n": 0,
 "expected_phase_match": null,
 "phase_repeat_items": 19,
 "phase_repeat_agree_rate": 0.6842
}
```
### rep0_distribution
```
{
 "NOT_MENTIONED": 38,
 "UNCLEAR": 11,
 "SAME": 9,
 "LEDGER_NO_DIRECTION": 7,
 "REVERSED": 8
}
```
### ledger_side / per_run
```
{
 "ledger": {
  "n_ledger_reps": 30,
  "has_direction_accuracy": 0.8667,
  "event_match_rate": 0.6923,
  "state_accuracy_given_match": 1.0,
  "ledger_phase_n": 27,
  "ledger_phase_accuracy": 0.8889
 },
 "per_run": {
  "jpy_per_call": 0.01792,
  "fallback_calls_per_repeat": 0.5766,
  "levels": {
   "low": {
    "units_per_run": 3.33,
    "added_calls": 18.92,
    "added_jpy": 0.339,
    "unneeded_rewrite_per_run": 0.068
   },
   "mid": {
    "units_per_run": 7.46,
    "added_calls": 25.43,
    "added_jpy": 0.456,
    "unneeded_rewrite_per_run": 0.152
   },
   "high": {
    "units_per_run": 30.56,
    "added_calls": 61.85,
    "added_jpy": 1.109,
    "unneeded_rewrite_per_run": 0.623
   }
  }
 }
}
```
### 前回比(TRIAL-02)

| 項目 | 前回(TRIAL-02) | 今回 |
|---|---|---|
| G-01 検出k/3 | 3 | 0 |
| G-02 検出k/3 | 3 | 0 |
| G-03 検出k/3 | 0 | 2 |
| 正常文 誤REVERSED(rep0) | 0 [] | 1 ['H-F1'] |
| UNCLEAR(rep0) | 6 | 11 |
| 実費(円) | 2.081872 | 3.566709 (差 1.4848) |

項目数 前回63 / 今回73、今回のみのid: ['H-F1', 'H-F2', 'H-F3', 'H-F4', 'H-F5', 'H-F6', 'H-G1', 'H-G2', 'H-G3', 'H-G4']
REVERSEDになった: ['S-09', 'S-14']
REVERSEDでなくなった: ['G-01', 'G-02', 'S-12', 'S-13']

rep0変化id一覧:
- F-02: NOT_MENTIONED -> UNCLEAR
- F-04: NOT_MENTIONED -> UNCLEAR
- F-07: UNCLEAR -> NOT_MENTIONED
- F-11: UNCLEAR -> SAME
- F-12: SAME -> UNCLEAR
- F-13: UNCLEAR -> SAME
- F-19: SAME -> NOT_MENTIONED
- F-20: SAME_FAMILY -> UNCLEAR
- G-01: REVERSED -> NOT_MENTIONED
- G-02: REVERSED -> UNCLEAR
- G-06: UNCLEAR -> NOT_MENTIONED
- N-02: UNCLEAR -> NOT_MENTIONED
- S-04: NOT_MENTIONED -> UNCLEAR
- S-09: NOT_MENTIONED -> REVERSED
- S-12: REVERSED -> NOT_MENTIONED
- S-13: REVERSED -> UNCLEAR
- S-14: NOT_MENTIONED -> REVERSED
