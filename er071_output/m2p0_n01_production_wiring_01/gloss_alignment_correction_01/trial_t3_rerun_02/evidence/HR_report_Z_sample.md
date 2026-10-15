# GLOSS_ALIGNMENT_HUMAN_REVIEW

article: family_z_melos_b1b / level: b1b / generated_at: 2026-10-15T03:34:41+00:00

KP日本語glossの再整合が上限回数(item単位2回)で成立しませんでした。**対象levelのKP segment(日本語意味・B1解説)はTTSに進みません(0 API call)。正常完成としても扱われません。** 最終KPは短い候補へ戻していません。
対応: 下の再生成候補から人間が判断し、`resolve_gloss`で確定するか、KPを再生成してください(手順: HR_RESOLVE_PROCEDURE_01.md)。

## rank 2: Three men blocked the road
- 現在gloss: 意味2
- 追加内容語: ['road']
- 失敗理由:
  - attempt1: qa_reflects_all_key_phrase_words!=PASS
  - attempt2: qa_reflects_all_key_phrase_words!=PASS
- 試行結果:
  - attempt1: verdict=INVALID 提案gloss='x' 理由=['qa_reflects_all_key_phrase_words!=PASS']
  - attempt2: verdict=INVALID 提案gloss='x' 理由=['qa_reflects_all_key_phrase_words!=PASS']
- 再生成候補:
  - 提案gloss: ['x', 'x']
  - 欠落語一覧: ['road']
  - 参考: 候補表現='Three men blocked the' / 旧gloss='意味2' (KPを短くすると意味が失われる、人間判断でのみ採用)
  - KP再生成: 既存経路でKey Phraseを再生成する(1レベル1回の運用上限に注意)。人間判断のみ。
