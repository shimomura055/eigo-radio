# ADOPTION_NOTE_08(Trial-08: 倒置優先順位変更。採用に向けたメモ。採用判断はユーザーのみ)

管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_18 / 日付: 2026-10-25 / Status候補: VALIDATED(条件付き。DEV/Trial専用。Production採用・配線なし)

## 1. 何を検証したか
Part 2の選定順を「Tier1=倒置以外の適格 → Tier2=適格な倒置 → Tier3=0件」に変更(Trial-07の適格条件・Tier内順位・最大1件は不変)。実装は `run_trial_08.py select_tiered`。詳細は `DESIGN_08.md`、結果は `PART2_TRIAL08_RESULTS_01.md`、判定は `EVAL_08.md`、要因分解は `COMPARISON_08.md`。

## 2. 結果の要点
- 倒置選定: 代表標本8作品で4 → 1。既存18標本で10 → 4。倒置を一律除外しておらず、Tier1が空の作品(賢者・告げ口心臓r2)では倒置が残った。
- 機械基準(事前登録6点)すべて合格。実費3.58円(量産単価への影響ほぼ0)。
- 質: 告げ口心臓は明確に改善、開いた窓・猿の手は多様化(価値は同等〜やや良い/低い可能性)。低価値な非倒置が選ばれるリスクあり(旧賢者r3 `Like Jim,`、猿r2 同格)。

## 3. 正式採用に必要な作業(ユーザー承認後)
1. ユーザーが採用を判断(D)。承認原文が必要。
2. CURRENT_SPEC / DECISION_LOG に採用を記録(Trial段階のため今回は未変更)。
3. Production側への配線は別委任(Part 2はまだProductionに存在しない。DESIGN_04 §1)。単一flag・既定OFFの限定例外(PM_GOVERNANCE 11-7)に従う場合も、選定規則の追加は新コード経路のみ。
4. 採用前に推奨される確認: (a)学習価値閾値(TV=HIGH)の扱い、(b)OTHER分類(分詞構文・付帯状況)の取り扱い、(c)Tier内順位の見直し要否。いずれも品質基準の変更に当たりうるため承認要。

## 4. 未承認事項
本Trialの規則・Promptは未承認。`run_trial_08.py` はDEV専用で、Production file・Prompt・閾値・flagの変更は0。

Status: VALIDATED(限定)、Fable受入2026-10-25 委任_19、Production未配線。
