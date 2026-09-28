# 固有名詞 9->19 実体調査(er037_output/family_xy_concreteness_control_trial_01/meta)

## 旧カウンタ(Trial-01 `extract_entities_ja`/`extract_entities_en`)

- AN JA (旧): 12件 -> ['AI', 'Meta', 'Muse', 'エージェント', 'コールセンター', 'サービス', 'スタッフ', 'テスト', 'プライバシー', 'ミス', 'ユーザー', 'ロールバック']
- AN EN (旧): 11件 -> ['AI', 'AI’s', 'End', 'Human', 'Meta', 'Muse', 'Muse’s', 'Other', 'Phone', 'Twist:', 'Was']
- A0 JA (旧, baseline参考): 13件 -> ['AI', 'Meta', 'Muse', 'エージェント', 'コンシェルジュ', 'コールセンター', 'スタッフ', 'テスト', 'ドラマチック', 'プルルル', 'ミス', 'ルール', 'ロールバック']
- A0 EN (旧, baseline参考): 10件 -> ['AI', 'AI—But', 'Had', 'Inside', 'Meta', 'Meta’s', 'Muse', 'Person', 'Thought', 'Was']

## 改良カウンタ(Trial-02限定。実固有名詞のみ・複合語は1件・漢字固有名詞も検出・Title Case見出しは除外)

- AN JA (改良): 2件 -> ['Meta', 'Muse']
- AN EN (改良): 2件 -> ['Meta', 'Muse']
- A0 JA (改良, baseline参考): 2件 -> ['Meta', 'Muse']
- A0 EN (改良, baseline参考): 3件 -> ['Had', 'Meta', 'Muse']

## 名称単位 JA->EN 差分表(改良カウンタ、AN)

| 固有名詞(canonical) | JA出現 | EN出現 | ENで新規か | 備考 |
|---|---|---|---|---|
| Meta | True | True | False |  |
| Muse | True | True | False |  |
