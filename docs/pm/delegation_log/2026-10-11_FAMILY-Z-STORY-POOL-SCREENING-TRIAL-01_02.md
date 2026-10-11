# FAMILY-Z-STORY-POOL-SCREENING-TRIAL-01 委任_02(2026-10-11、課金0・有料API未実行)
ユーザー追加指示: Trial基本モデルを gpt-6-luna に固定、権利情報の解釈・整理工程を新設、費用再見積。
## 変更
- er006_model_routing_contract_01.py: Trial専用key `FAMILY_Z_TRIAL_STORY_QUALITY_EVAL` / `FAMILY_Z_TRIAL_RIGHTS_INTERPRET`(=gpt-6-luna)を追加のみ。Production key不変(testで固定)。
- er054_family_z_story_pool_trial_common_01.py(新規): Trial key解決・許可外モデル拒否・封印ファイルdeny guard。
- er054_..._quality_eval_trial_01.py: 許可モデルをgpt-6-lunaのみ(Astra/Sol拒否)、routing経由、actual_model_id/usage/prompt_sha256記録。
- er054_..._rights_interpret_trial_01.py(新規): 権利解釈driver。LLMは決定論判定を上書き不可(降格のみ、昇格不可、final_pass_confirmed常にFalse、一次資料未取得は降格)。
- er054_..._trial_02_test_01.py(新規): 11 test PASS(Trial key=luna、Production key不変、許可外モデル拒否、封印ファイル読込拒否、降格のみ等)。
- 設計書: PHASE_C_EVAL_DESIGN_01.md付録(差し替え理由=ユーザー指示・25節例外)、PHASE_B2_RIGHTS_INTERPRET_DESIGN_01.md、PHASE_C_COST_ESTIMATE_02_luna.md/.json。
## 検証(実測)
- 新test 11件OK。既存routing test(er006 contract/pricing coverage/gpt6 wiring/er009 pricing) OK。
- 乾式(モック): 品質評価 8/9/10作品、権利解釈 10作品(昇格0・降格check/据え置きcheck OK)、real起動拒否(承認上限なし)・許可外モデル拒否を確認。
## 再見積(点見積/上限×1.5、円)
(a)品質PASS8: 4.26/6.39、(b)L04含む9: 4.75/7.12、(c)権利解釈10: 4.68/7.02、(d)a+c: 8.94/13.41、(e)b+c: 9.43/14.14。出力token(約75%)が最大の不確実性。L01先行実測は約1.1円。
## 注意
- phase_c_dry_run/gpt-6-astra/ は委任_01の乾式出力(履歴として残置、現在は無効)。
- sources/配下の未追跡ファイル(委任_01由来)は今回stageしていない。
## Status: USER_DECISION_REQUIRED(課金上限・ケース選択・L04含否)。Trial限定、Production採用ではない。
