# INPUT_CHECK_03(Trial-03、2026-10-25、API前の決定論的確認)

| 作品 | 本文(path / sha256) | KP 3個(出典) | 本文=公開Adv一致 |
|---|---|---|---|
| 賢者の贈り物(Z) | `er026_output/family_z_production_e2e_01/the_gift_of_the_magi/run_sf_prod_01/writer/r2.md` / fc3d1163...ff25c(Trial-01/02と同一) | hand down / catch sight of / catch one's breath(run_trial_01.KP同一object) | 公開 `user_test/family_z_gift_of_the_magi_01/advanced.html` と56/56文一致 |
| 開いた窓(Z) | `er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01/writer/r2.md` / f07a1465...d13688 | give way / at a moment's notice / keep someone company(`key_phrases/b1b_result.json` sha 140f5318...、英語解説`b1b/kp_explanations.json` sha bc2f98a4...) | 公開 `user_test/family_z_open_window_01/advanced.html` と60/60文一致 |
| イグ・ノーベル賞2026解説(X) | `er019_output/ig_nobel_2026/run_nws_02/b1b/article.md` / 067edef1...f16fd81(`## In one line`要約節のみ本文番号から除外=10段落[P1-P11]) | nutrient-rich crystals / bound to the protein / leap into action(`er019_output/family_x_audio_production_wiring_01/ig_nobel_2026__run_nws_02/b1b/key_phrases/keywords_canonicalized.json` sha 3745c4b0...、英語解説は同`b1b/audit/tts_generation_results.json`) | 公開 `user_test/ig_nobel_2026_e2e_02/index.html` と本文一致(In one lineのみ除外、他40/40) |

注意(取り違え防止): 『開いた窓』には旧runの `run_e2e_01`(KP=letter of introduction等)もあるが、公開・ユーザー承認の正式版は `run_sf_prod_01`。公開ページ照合で正式版を確定した(run_e2e_01のr2.mdは公開本文と49/59文不一致)。
KPの「本文の該当文」は本文から逐語抽出(run_trial_03.pyが`s in text`をassert)。canonical上のsource_sentenceは句読点・引用符が正規化されているため本文側の原文を使用。

## 条件固定の確認
- model=gpt-6-luna(全17 callで response.model一致、Trial-01/02と同一)、Responses API、reasoning/temperature指定なし、user message 1通、developer/few-shotなし。
- Part 3/4 Prompt・出力形式・制約・本文注入方式は全版不変。Gift向けBuildはPROMPT_02を完全再現(`build("gift","02")==t2.PROMPT`をassert済み)。
- STOP確認: `stop_scope_check_01.py` rc=0 ×4(`docs/pm/delegation_log/2026-10-25_FZST05_stop_check*.json`)。

## 引用逐語一致(決定論、`check_quotes_03.py` → `quote_check_03.json`)
出力中の5語以上の英語スパンを本文と照合(Part 4と比較用の文は除外)。全17出力で本文引用の不一致は**0件**。未一致として挙がったのは、見出しの番号接頭辞(`2. at a moment's notice`等)・構文パターン表記(`more than three times as much A as B`)・比較用/言い換えの英文(`the best source of nutrition`等)のみで、いずれも本文引用ではない(手動確認済み)。
意味の正確性は EVAL_03.md に記載(日本語訳・用法説明を全出力で人手確認)。
