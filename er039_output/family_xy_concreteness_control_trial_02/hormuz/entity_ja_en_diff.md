# 固有名詞 9->19 実体調査(er037_output/family_xy_concreteness_control_trial_01/hormuz)

## 旧カウンタ(Trial-01 `extract_entities_ja`/`extract_entities_en`)

- AN JA (旧): 9件 -> ['イラン', 'ガソリン', 'タンカー', 'トランプ', 'ドル', 'ニュース', 'バレル', 'ブレント', 'ホルムズ']
- AN EN (旧): 19件 -> ['Bill', 'Brent', 'Character:', 'Donald', 'Eastern', 'Gulf', 'Hormuz', 'Iran', 'July', 'Main', "Market's", 'Middle', 'Missing', 'Oil', 'Percent', 'States', 'Strait', 'Trump', 'United']
- A0 JA (旧, baseline参考): 14件 -> ['Brent', 'Reuters', 'イラン', 'エネルギー', 'カーブ', 'タンカー', 'チャート', 'トランプ', 'ドラマ', 'ドル', 'ニュース', 'バレル', 'ホルムズ', '・イラン']
- A0 EN (旧, baseline参考): 19件 -> ['Act', 'Brent', 'Chart', 'Eastern', 'Finished', 'Gulf', 'Hormuz', 'Iran', 'July', 'Middle', 'Oil', 'States', 'Strait', 'Trump', 'US', 'US-Iran', 'United', 'Was', 'Withdrawn—but']

## 改良カウンタ(Trial-02限定。実固有名詞のみ・複合語は1件・漢字固有名詞も検出・Title Case見出しは除外)

- AN JA (改良): 7件 -> ['Gulf states', 'Middle East', 'United States', 'イラン', 'トランプ', 'ブレント', 'ホルムズ']
- AN EN (改良): 7件 -> ['Brent', 'Donald Trump', 'Gulf states', 'Iran', 'Middle East', 'Strait of Hormuz', 'United States']
- A0 JA (改良, baseline参考): 8件 -> ['Brent', 'Gulf states', 'Middle East', 'Reuters', 'United States', 'イラン', 'トランプ', 'ホルムズ']
- A0 EN (改良, baseline参考): 10件 -> ['Act', 'Brent', 'Gulf states', 'Iran', 'Middle East', 'Strait of Hormuz', 'Trump', 'US', 'US-Iran', 'United States']

## 名称単位 JA->EN 差分表(改良カウンタ、AN)

| 固有名詞(canonical) | JA出現 | EN出現 | ENで新規か | 備考 |
|---|---|---|---|---|
| Donald Trump | True | True | False |  |
| Strait of Hormuz | True | True | False |  |
| Brent | True | True | False |  |
| Iran | True | True | False |  |
| United States | False | True | True |  |
| Middle East | False | True | True |  |
| Gulf states | False | True | True |  |
| Gulf states | True | False | False | unmapped(JAのみ、CANONICAL_ENTITY_PAIRS未登録) |
| Middle East | True | False | False | unmapped(JAのみ、CANONICAL_ENTITY_PAIRS未登録) |
| United States | True | False | False | unmapped(JAのみ、CANONICAL_ENTITY_PAIRS未登録) |
