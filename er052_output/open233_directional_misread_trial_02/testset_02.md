# TRIAL-02 Trial対象セット 内訳(委任_02、事前登録)

基準: TRIAL-01 testset_01(63項目)を踏襲。gold定義・KPI不変。正解データは ledger_truth_02.json(複数事象)。

| 区分 | 項目数 | repeat | 合計call(Σrepeat) |
|---|---|---|---|
| 真の反転(gold) G-01〜03 | 3 | 3 | 9 |
| 曖昧 G-04〜06 | 3 | 3 | 9 |
| 忠実(状態変化語あり) F-01〜21 | 21 | F-09/F-10/F-19のみ3、他1 | 27 |
| 忠実(HC-012同fact・状態言及なし) N-01〜17 | 17 | 1 | 17 |
| 非該当(方向性なしfact) ND-01〜05 | 5 | 1 | 5 |
| 人工反転 S-01〜14 | 14 | 1 | 14 |
| **合計** | 63 | | **81**(TRIAL-01は75) |

label別: 忠実43/真の反転3/曖昧3/人工反転14(不変)。repeat=3項目(9件): G-01〜06, F-09, F-10, F-19。

## 前回誤爆3件の期待値
| id | 記事文要点 | 対象事象(expected_event_subject) | expected_compare | 許容 |
|---|---|---|---|---|
| F-09 | Brent futures briefly lost some of their gains | 上げ幅(DECREASED) | SAME | SAME/SAME_FAMILY/UNCLEAR |
| F-10 | Brent futures briefly gave up some of their gains | 上げ幅(DECREASED) | SAME | SAME/SAME_FAMILY/UNCLEAR |
| F-19 | Meta has pulled back the human concierge feature | 機能(PAUSED/STOPPED) | SAME | SAME/SAME_FAMILY |

解消条件: 3件x3回で重大(REVERSED)判定0。電話テスト(STARTED)や水準(INCREASED)と誤比較してREVERSEDにならないこと。

## 変更点一覧(TRIAL-01比)
- 全項目: `expected_event_subject`/`trial02_reason`/`legacy_expected_compare`/`legacy_acceptable_compare`/`outside_event_list`追加。
- repeat: F-09/F-10/F-19を1→3(call +6)。G-01〜06は継続3。
- compare見直し(15件): F-08(NOT_MENTIONED許容)、F-09/F-10(SAME_FAMILY許容追加)、F-16/F-17(NOT_MENTIONED許容追加)、F-19/F-20(SAME_FAMILY許容追加)、S-07は対象事象「上げ幅」の直接逆のためUNCLEAR許容を外し厳密REVERSED、S-01〜06/S-11は`outside_event_list=true`でSAME/NOT_MENTIONED許容追加。
- outside_event_list=true(7件): S-01〜S-06, S-11。置換語(plan arrives等)がLedger事象リスト外のため、検出必須とせず別集計(要判断: 検出必須とするか、KPI母数から外すか)。
- 事象を述べない文(N-01〜17, ND-01〜05)は subject=NONE、期待NOT_MENTIONED。

## 参照
- 正解データと採点規則: ledger_truth_02.md / ledger_truth_02.json
