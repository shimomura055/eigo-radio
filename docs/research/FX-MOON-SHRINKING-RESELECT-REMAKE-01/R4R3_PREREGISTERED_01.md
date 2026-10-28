# R4/R3 是正 事前登録 (FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_04、評価実行前に固定)
対象: `er007_ja_secondary_asr_01.py` の (a) `_secondary_accept` への値等価層適用(R4) (b) `_numeric_value_equivalence` triggerの桁区切りカンマ拡張(R3)。rollback定数 `JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED`(既定True)。
評価: `r4r3_eval_api0_01.py`(API 0、socket guard、Production adapter `evaluate_attempt_ja_with_cascade_detail`をそのまま呼び、定数False=是正前/True=是正後を比較。Azureはstub=Primary転写と同一転写を返すSecondary、およびSecondary不在の2モード)。2回実行で出力一致。
コーパス: N-1合成負例(`n1_pairs_01.all_pairs()`: er066凍結負例+prodbug+曖昧+新規[値10倍・桁違い・不規則読み含む]) / 実転写プール(`ng_pool_cases_01.json`,`unknown_pool_02.json`,`attempt_pool_01.json`) / 本委任の追加合成負例(桁区切り絡み: 値違い・桁違い・単位違い・非数値差併存・否定) / 正例対照(8,900↔8900 非数値完全一致など)。
合格基準(全て満たすこと):
1. N-1+追加合成負例: 是正前NG→是正後PASSの増分 = 0。
2. 実転写プール: PASS集合の増分は、(i)原稿に数値atomがある、(ii)値ガードEQUAL、(iii)数値atomを値トークンへ置換した両文がnormalize_ja後に完全一致、の全てを満たす対のみ。増分全件を列挙し目視監査。(iii)を満たさない増分=不合格。
3. 是正後PASS→是正前NG(退行) = 0。
4. 正例対照: 『月のしわ、8,900本超…』のSecondary転写『…8900…』は是正後PASS(NUMERIC_VALUE_EQUIVALENT_MATCH)。『月の詩は…』(しわ→詩は)は非受理のまま。値DIFF(8,800/89,000/9,900)・不規則読み値は非受理のまま。
5. 定数False時の結果が是正前と同一(rollback確認)。
6. 既存test(er007/er011/er078系)全PASS。
