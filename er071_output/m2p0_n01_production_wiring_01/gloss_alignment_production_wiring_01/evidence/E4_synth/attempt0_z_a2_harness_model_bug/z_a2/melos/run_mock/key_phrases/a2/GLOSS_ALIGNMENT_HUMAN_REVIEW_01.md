# GLOSS_ALIGNMENT_HUMAN_REVIEW

article: family_z_melos_a2 / level: a2 / generated_at: 2026-10-15T07:07:46+00:00

KP日本語glossの再整合が上限回数(item単位2回)で成立しませんでした。**対象levelのKP segment(日本語意味・B1解説)はTTSに進みません(0 API call)。正常完成としても扱われません。** 最終KPは短い候補へ戻していません。
対応: 下の再生成候補から人間が判断し、`resolve_gloss`で確定するか、KPを再生成してください(手順: docs/pm/runbooks/KP_GLOSS_ALIGNMENT_HR_RESOLVE_01.md)。

## rank 2: Three men blocked the road
- 現在gloss: 意味2
- 追加内容語: ['road']
- 失敗理由:
  - attempt1: NotFoundError: Error code: 404 - {'error': {'message': 'The model `synthetic-model` does not exist or you do not have access to it.', 'type': 'invalid_request_error', 'param': None, 'code': 'model_not_found'}}
  - attempt2: NotFoundError: Error code: 404 - {'error': {'message': 'The model `synthetic-model` does not exist or you do not have access to it.', 'type': 'invalid_request_error', 'param': None, 'code': 'model_not_found'}}
- 試行結果:
  - attempt1: verdict=TECHNICAL_FAILED 提案gloss=None 理由=["NotFoundError: Error code: 404 - {'error': {'message': 'The model `synthetic-model` does not exist or you do not have access to it.', 'type': 'invalid_request_error', 'param': None, 'code': 'model_not_found'}}"]
  - attempt2: verdict=TECHNICAL_FAILED 提案gloss=None 理由=["NotFoundError: Error code: 404 - {'error': {'message': 'The model `synthetic-model` does not exist or you do not have access to it.', 'type': 'invalid_request_error', 'param': None, 'code': 'model_not_found'}}"]
- 再生成候補:
  - 提案gloss: []
  - 欠落語一覧: ['road']
  - 参考: 候補表現='Three men blocked the' / 旧gloss='意味2' (KPを短くすると意味が失われる、人間判断でのみ採用)
  - KP再生成: 既存経路でKey Phraseを再生成する(1レベル1回の運用上限に注意)。人間判断のみ。
