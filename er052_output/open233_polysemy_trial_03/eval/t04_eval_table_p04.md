## P1p_gate_hm
| theme | recall | extra | attach | rate | holdout_over_expected | stability | warnings | bypass/promote/lint/cover_skip | cost |
|---|---|---|---|---|---|---|---|---|---|
| meta | 2/2 | 4 | 6/15 | 0.40 | - | - | 6 | 0/0/0/2 | 6.63 |
| hormuz | 0/2 | 4 | 4/12 | 0.33 | - | - | 4 | 0/0/0/0 | 5.04 |
| space_weapons | 0/4 | 1 | 1/22 | 0.05 | - | - | 0 | 0/0/0/2 | 3.04 |
| sewer | 0/3 | 3 | 3/20 | 0.15 | - | - | 0 | 0/0/1/1 | 4.55 |
| ai_control | 0/3 | 4 | 4/16 | 0.25 | - | - | 4 | 0/0/0/3 | 6.47 |
| A02 | 0/2 | 5 | 5/19 | 0.26 | 3 | - | 0 | 0/0/1/5 | 8.36 |
| small_bag | 0/0 | 4 | 4/17 | 0.24 | 3 | - | 0 | 0/0/8/0 | 7.11 |
| A01 | 0/0 | 0 | 0/30 | 0.00 | 0 | - | 0 | 0/0/0/1 | 2.54 |

### rollback Gate(別枠。機械チェックは候補判定。最終はFable。3値定義は eval/rollback_gate_labels.md)
- gate_fact=MUSE-HC-012 captured=True result=FAIL_CANDIDATE reasons=['A:取り下げ系の語がない', 'B:復活・再提供・再開・復旧を否定する表現がない']
- note全文: 注意(逆転): 台帳の表記'ロールバック'は、人間コンシェルジュ機能が当面提供されない状態の意味。Metaは人間コンシェルジュ機能を恒久的に廃止したのではない。
- 3値仮ラベル(Sonnet): 軸ずれ / 根拠: 'ロールバック'=当面提供されない状態は示すが、復活・再提供の否定が無く、否定軸は恒久廃止(時期)だけ(誤禁止表現は無い)

### 合格条件(機械判定分+Sonnet仮ラベル分)
- recall: 2/14 (>=9/14: NG)
- attach_rate: 0.21 (<=0.25: OK)
- holdout_attach_over_expected_max: 6 (<=1: NG)
- holdout_false_attach_strict(参考: targets外の全付与): 9
- 総費用(この表のrun合計): 43.75円 / 平均字数 89.1 / 最大字数 119 / 警告 14
- holdout 誤り(型H/X)ラベル数: 1(<=1が基準はholdout誤付与の方)
- 内容一致(主=生成noteのみ, 対象付与2件中): Y=0 P=1 N=1 → Y率=0% / (Y+P)率=50% / 未ラベル=0
- 対象外付与16件の内訳: 妥当(V)=11 / 変質止まり(D)=3 / 誤り(H+X)=2 ; 捏造=0 ; 曖昧語流用=0
- 副指標(和集合: 生成note+既存notes禁止文転記) 対象のY一致数: 生成のみ=0, 既存のみ=9, 和集合=9 / 14 ; 和集合付与率=54%

## P2p_stable
| theme | recall | extra | attach | rate | holdout_over_expected | stability | warnings | bypass/promote/lint/cover_skip | cost |
|---|---|---|---|---|---|---|---|---|---|
| meta | 1/2 | 1 | 2/15 | 0.13 | - | stage1 0.50 | 2 | 0/0/0/1 | 6.25 |
| hormuz | 1/2 | 2 | 3/12 | 0.25 | - | stage1 0.17 | 3 | 0/0/0/0 | 8.60 |
| space_weapons | 0/4 | 1 | 1/22 | 0.05 | - | stage1 0.57 | 1 | 0/0/0/3 | 6.07 |
| sewer | 1/3 | 1 | 2/20 | 0.10 | - | stage1 0.67 | 0 | 0/0/0/0 | 6.15 |
| ai_control | 0/3 | 3 | 3/16 | 0.19 | - | stage1 0.91 | 1 | 0/0/4/3 | 9.96 |
| A02 | 0/2 | 3 | 3/19 | 0.16 | 1 | stage1 0.50 | 2 | 0/0/3/8 | 9.85 |
| small_bag | 0/0 | 1 | 1/17 | 0.06 | 0 | stage1 0.09 | 0 | 0/0/2/0 | 6.94 |
| A01 | 0/0 | 5 | 5/30 | 0.17 | 3 | stage1 0.00 | 5 | 0/0/0/0 | 8.15 |

### rollback Gate(別枠。機械チェックは候補判定。最終はFable。3値定義は eval/rollback_gate_labels.md)
- gate_fact=MUSE-HC-012 captured=False result=FAIL_CANDIDATE reasons=['未捕捉']
- note全文: None
- 3値仮ラベル(Sonnet): 未捕捉(コードr_echo照合で却下) / 根拠: 却下されたnote文は P1' と同型(軸ずれ)。r_echo末尾『。』の有無だけの不一致で却下された(ハーネス厳格さの欠陥、評価基準は変更しない)

### 合格条件(機械判定分+Sonnet仮ラベル分)
- recall: 3/14 (>=9/14: NG)
- attach_rate: 0.13 (<=0.25: OK)
- holdout_attach_over_expected_max: 4 (<=1: NG)
- holdout_false_attach_strict(参考: targets外の全付与): 9
- 総費用(この表のrun合計): 61.97円 / 平均字数 79.5 / 最大字数 101 / 警告 7
- holdout 誤り(型H/X)ラベル数: 1(<=1が基準はholdout誤付与の方)
- 内容一致(主=生成noteのみ, 対象付与3件中): Y=2 P=0 N=1 → Y率=67% / (Y+P)率=67% / 未ラベル=0
- 対象外付与8件の内訳: 妥当(V)=4 / 変質止まり(D)=4 / 誤り(H+X)=0 ; 捏造=0 ; 曖昧語流用=0
- 副指標(和集合: 生成note+既存notes禁止文転記) 対象のY一致数: 生成のみ=2, 既存のみ=9, 和集合=9 / 14 ; 和集合付与率=49%

## P3_writer_compress
| theme | recall | extra | attach | rate | holdout_over_expected | stability | warnings | bypass/promote/lint/cover_skip | cost |
|---|---|---|---|---|---|---|---|---|---|
| meta | 2/2 | 4 | 6/15 | 0.40 | - | - | 5 | 1/0/0/0 | 5.85 |
| hormuz | 1/2 | 2 | 3/12 | 0.25 | - | - | 3 | 0/0/0/0 | 4.94 |
| space_weapons | 0/4 | 1 | 1/22 | 0.05 | - | - | 1 | 0/0/0/1 | 3.32 |
| sewer | 0/3 | 3 | 3/20 | 0.15 | - | - | 1 | 0/0/1/0 | 4.36 |
| ai_control | (no run) |
| A02 | (no run) |
| small_bag | (no run) |
| A01 | (no run) |

### rollback Gate(別枠。機械チェックは候補判定。最終はFable。3値定義は eval/rollback_gate_labels.md)
- gate_fact=MUSE-HC-012 captured=True result=FAIL_CANDIDATE reasons=['B:復活・再提供・再開・復旧を否定する表現がない']
- note全文: 注意(逆転): 台帳の表記'ロールバックした'は、人間コンシェルジュ機能が当面停止している状態の意味。Metaは人間コンシェルジュ機能を恒久的に廃止したのではない。
- 3値仮ラベル(Sonnet): 軸ずれ / 根拠: 'ロールバックした'=当面停止の状態は示すが、復活・再提供の否定が無く否定軸は恒久廃止(時期)だけ(素通り経路で付与)

### 合格条件(機械判定分+Sonnet仮ラベル分)
- recall: 3/11 (>=9/14: NG)
- attach_rate: 0.19 (<=0.25: OK)
- holdout_attach_over_expected_max: -
- holdout_false_attach_strict(参考: targets外の全付与): 0
- 総費用(この表のrun合計): 18.47円 / 平均字数 90.2 / 最大字数 111 / 警告 10
- holdout 誤り(型H/X)ラベル数: 0(<=1が基準はholdout誤付与の方)
- 内容一致(主=生成noteのみ, 対象付与3件中): Y=0 P=2 N=1 → Y率=0% / (Y+P)率=67% / 未ラベル=0
- 対象外付与10件の内訳: 妥当(V)=9 / 変質止まり(D)=1 / 誤り(H+X)=0 ; 捏造=0 ; 曖昧語流用=0
- 副指標(和集合: 生成note+既存notes禁止文転記) 対象のY一致数: 生成のみ=0, 既存のみ=6, 和集合=6 / 14 ; 和集合付与率=49%
