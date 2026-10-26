# DATA_MODEL_01 データモデル(Opus論点なし。新規構造は既存パターンの静的JSONのみ)
- `data/articles.json` (`eigo_radio_selection_index_v1`): `articles[]={slug,level,level_label,name,data|null}`、`default`。状態キー=`slug__level`。9記事以上を追加可能(testで9件ダミー切替を確認)。
- `data/<slug>__<level>.json` (`eigo_radio_selection_article_v1`): `phrases[]`(<=7)/`words[]`(<=5)={id,term,meaning_ja,excerpt,flag?,flag_note_ja?}、`grammar[]`={id,title,body,example?}、`source`={kind,trial,run,text_sha256,model_id,note_ja}、`grammar_note_ja`。
- 出力 (`eigo_radio_selection_result_v1`, schema_version 1): `article{slug,level,level_label,name,text_sha256}`, `candidate_source`, `limits`, `selection{key_phrase[],extra_explanation[],meaning_display[],grammar[{id,title}]}`, `counts`, `comment`, `generated_at`, `production_connected:false`。
- 永続: localStorage `eigo-kp-form-v3` = `{ "<slug>__<level>": {choices:{term:0..3}, grammar:{id:bool}, comment} }`。
- 将来のClaude直接送信は上記出力JSONをそのまま利用可能(今回未実装)。
- 候補→フォームのadapter課題(判断候補): Part 2候補(英文選択・解説は選定後生成・最大1件)を「文法名+解説全文・最大2件」へ接続するには解説の事前生成/最大数変更が必要=新仕様。本委任では接続せず、データ型(`grammar[]`)のみ用意。
