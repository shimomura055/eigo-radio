# DATA_MODEL_03 記事データ/送信payload(委任_02差分。DATA_MODEL_02への追加)
## 記事データ(eigo_radio_selection_article_v1への追加項目、任意)
- `kp_confirmed`: {status:"USER_CONFIRMED", locked:true, confirmed_at, user_ref, payload_path, payload_sha256, text_sha256, candidates_sha256, selection:[{term,category,category_label,ja_gloss,ja_gloss_status:"official",candidate_id,kind,selection_phrase?}×10(3/2/5)]}。`validateArticle`が候補データと逐語照合(candidate_id存在/term/ja_gloss/件数3-2-5/sha一致)し、不一致はデータ形式エラー(fail-closed)。
- `grammar_spec`: {version:"top2_select1_v1", presented_max:2, max_select:1, allow_zero:true, presented_ids[], hidden_ids[], source_*_sha256}。`validateArticle`: grammar<=2件・rank=1,2・presented_ids一致・max_select=1。
- `grammar[]`: 提示分のみ(Top1/Top2)。各item: id/candidate_id/title/body/explanation_full/example/explanation_sha256/rank。
## 状態(localStorage `eigo-kp-form-v3`)
`grammar`(id→bool、最大1)・`grammar_zero`(true=「適切な候補なし」明示)。決定状態: selected|none|undecided|n/a。旧状態は正規化(2件選択→未決定)。`kp_confirmed`記事では`choices`を無視。
## payload(eigo_radio_selection_result_v2, schema_minor 1のまま追加項目)
`limits.grammar=1,grammar_presented_max=2`、`selection.grammar[]`(0/1件、rank/rank_label付き)、`grammar_status`、`grammar_decision`、`kp_confirmed`(locked)。er128 `from-form`が読む既存項目(selection.{key_phrase,extra_explanation,meaning_display}.{term,candidate_id,kind,ja_gloss,ja_gloss_status}、selection.grammar[].{id,title,explanation_full,...}、article.{candidates_sha256,text_sha256})は不変。
