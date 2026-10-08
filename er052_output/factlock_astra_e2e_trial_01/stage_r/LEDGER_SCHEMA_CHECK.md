# 台帳スキーマ点検(仕様v2 §8、b3_annotation_check_01.ledger_schemaを使用)

| slug | 記録数 | VERIFIED | numeric_value欄あり | date_or_period欄あり | 量語あり&numeric_value欄なし | 代替規則(nv) | 代替規則(date) |
|---|---|---|---|---|---|---|---|
| byd_recall | 11 | 11 | 6 | 7 | 0件 | 不要 | 不要 |
| openai_copyright | 8 | 8 | 6 | 8 | 0件 | 不要 | 不要 |
| central_bank_mortgage | 11 | 11 | 5 | 10 | 0件 | 不要 | 不要 |
| inbound_tourism | 11 | 11 | 9 | 11 | 0件 | 不要 | 不要 |
| meta | 15 | 15 | 3 | 15 | 0件 | 不要 | 不要 |
| hormuz | 12 | 12 | 10 | 12 | 0件 | 不要 | 不要 |
| space_weapons | 22 | 22 | 8 | 22 | 0件 | 不要 | 不要 |
| small_bag | 6 | 6 | 0 | 6 | 0件 | 適用 | 不要 |

欄名ごとの件数と警告:
- byd_recall: field_counts={'scope': 11, 'conditions': 11, 'numeric_value': 6, 'date_or_period': 7, 'notes_for_writer': 9, 'causal_strength': 5}; warnings=[]
- openai_copyright: field_counts={'scope': 8, 'conditions': 8, 'date_or_period': 8, 'notes_for_writer': 8, 'numeric_value': 6}; warnings=[]
- central_bank_mortgage: field_counts={'scope': 11, 'conditions': 11, 'date_or_period': 10, 'notes_for_writer': 11, 'numeric_value': 5, 'causal_strength': 6}; warnings=[]
- inbound_tourism: field_counts={'scope': 11, 'conditions': 11, 'numeric_value': 9, 'date_or_period': 11, 'causal_strength': 9, 'notes_for_writer': 11, 'ambiguity_note': 1}; warnings=[]
- meta: field_counts={'scope': 15, 'conditions': 15, 'date_or_period': 15, 'notes_for_writer': 15, 'numeric_value': 3, 'causal_strength': 4}; warnings=[]
- hormuz: field_counts={'scope': 12, 'conditions': 11, 'numeric_value': 10, 'date_or_period': 12, 'notes_for_writer': 12, 'causal_strength': 7}; warnings=[]
- space_weapons: field_counts={'scope': 22, 'conditions': 22, 'date_or_period': 22, 'causal_strength': 14, 'notes_for_writer': 22, 'numeric_value': 8}; warnings=[]
- small_bag: field_counts={'scope': 6, 'conditions': 6, 'date_or_period': 6, 'causal_strength': 6, 'notes_for_writer': 6}; warnings=['台帳に numeric_value 欄が1件も無い: 量のE1判定は statement 内の主数字で代替する (fallback)']
