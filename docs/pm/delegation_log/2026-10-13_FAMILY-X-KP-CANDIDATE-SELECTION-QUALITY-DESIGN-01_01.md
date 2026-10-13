# FAMILY-X-KP-CANDIDATE-SELECTION-QUALITY-DESIGN-01 委任_01(2026-10-13、Sonnet)
- 範囲: Key Phrase候補選定品質の調査・設計のみ(JPY0)。Production code/Prompt/DB/CURRENT_SPEC無変更。Melos関連(er026_output/melos、OPEN-331/320、COST_LEDGER、user_test/family_z_melos_01)には触れていない。
- 成果: 設計書 `docs/pm/design/2026-10-13_KP-CANDIDATE-SELECTION-QUALITY-DESIGN-01.md`(10章)、読取script5本 `er064_kp_candidate_selection_design_01_*.py`、結果JSON `er064_output/kp_candidate_selection_design_01/`(8ファイル)。
- 主要所見: time lagは抽出段(照会予算76番目、Wiktionaryヒットあり)、in the ringはextractor出力そのもの、既知性・連語強度は機械判定不可。
- STOP確認: 開始時にMelos STOP_NOTICE(別案件)のみ存在、STOP_ALL不在。有料API呼出なし(Wiktionary公開APIのみ1回)。
- 制約: 机上の期待(c)は未検証。LLM判断依存項目は△。WordNet等はライセンス未確認で提案のみ。concurrent編集(OPEN_ITEMS/DECISION_LOG)は追記のみ。
- SSOT: OPEN-336新規、OPEN-325/310相互参照、DECISION_LOG追記。次: FableがOpus独立レビュー(条件A)を起動。
