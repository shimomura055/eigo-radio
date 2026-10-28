# BUDGET_PLAN_01 (FX-AI-ISLAND-COMMENT-Z-METHOD-TRIAL-01 委任_01)

- 上限: 100円 / 日次1,000円枠内。音声化・TTS・ASRは行わない(0円)。
- 生成: After Comment 1〜4 を各1回(計4呼出、gpt-6-luna=Production A2_SUPPORT設定、`er006_model_routing_contract_01.SUPPORT_MODEL`)。再生成は技術失敗時のみ(a2gen.run_support_text内蔵の最大2attempt)。
- 見積: 各呼出 入力約1.5k token・出力+reasoning約1k token。pricing_snapshot gpt-6-luna in 0.10 / out 0.50 USD per M x 160円 → 4呼出で約0.1円(最大でも1円未満)。上限100円に対し余裕あり。
- 追加モデル比較・反復生成なし。
