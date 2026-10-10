# 委任_02 FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01 Phase 1 設計・実現性確認

- 日付: 2026-10-11 / 実行層: Sonnet / 依頼: Fable
- 範囲: Trial driver設計・実現性確認・事前登録案(コードなし、課金API呼出なし、Production/Prompt/Routing/SSOT変更なし)
- 成果物: er052_output/ja_article_quality_model_allocation_trial_01/DESIGN_01.md, PREREGISTRATION_01.md
- 費用: 0円(API呼出なし。モデル一覧取得も未実施)
- 実施: 既存コードの読取り、既存artifact(pricing_snapshot、antenna/sol_n1 raw log、run_regen_01)の照合、Writer/B3 moduleのimportによるPrompt sha取得(無課金・ローカルのみ)
- 要点: 方式Y(純関数import+driver側で同手順再構成、require_model_or_override使用、stub client等価テスト必須)。Sol=gpt-6.1-sol推奨(effort high・B3 json_schema未確認、gpt-6-solとの関係未確認)。C案B3はA再利用推奨。案別cap C65/D85/E50。
- 未確定: ユーザー指示のSTOP条件6点の原文(草案で代替)、Sol id、C案B3再利用可否
- 並行: 委任_01(AB_BASELINE_01.md/COST_VERIFICATION_01.md)には触れていない。ACTIVE_TASK.md/RESULT_PACKET.mdは並行編集の衝突回避のため未更新(Fable側で更新)。
