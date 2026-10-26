# SURVEY_01 既存フォーム調査(LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_01、2026-10-26)

## 1. 「Family X記事選定フォーム」の実在調査(事実)
- Grep `選定フォーム|selection_form|theme_selection|記事選定`(全repo、`er*_output`/`.venv`除く): 該当は委任文2件・`er011_news_stage3_new_theme_ledger_trial_09.py`・`FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09_REPORT.md`のみ。いずれも「記事テーマ選定」の語で、**Webの選定フォームではない**。`user_test/`配下に選定フォーム用dir・HTMLは存在しない(108 dir中、form/select/theme名のdirは0)。
- 再利用可能な既存の公開方式(事実): `user_test/<name>/index.html`をGitHub Pagesで配信(`docs/pm/PM_BRIEF.md` 157-158行: 正式配布=`https://shimomura055.github.io/eigo-radio/user_test/...`、Landing=`user_test/articles_2026_0918.html`)。近い先例は`user_test/human_review.html`(静的HTML単体)。
- 結論: 「既存フォームの実装を再利用」はできない(実体なし)。**公開方式のみ再利用**: `user_test/selection_form_v3/index.html`+`form_logic.js`+`data/*.json`(静的、サーバ不要、fetch)。

## 2. 候補データ形式
- KP候補(Trial-02): `docs/research/KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/runs/<tag>/trial_result.json` の `doc.candidates[]`: `candidate_id/used_form/japanese_gloss/source_sentence/origin(call1=フレーズ,call2=単語)/rescue(KP救済旗)`。Gate除外は`doc.dropped`(今回の候補には出さない)。猿の手b1b=フレーズ7(うち`pulled free`・`caught in the machinery`が救済済み=`rescue.codes=[REVERT_SURFACE]`)+単語4。
- KP HR(Production): `er119_kp_human_review_01.py` `KP_CANDIDATE_MAX=8`(53行付近の`KP_FINAL_MAX=3`/`VOCAB_COUNT_MAX=5`)、候補schema=`SCHEMA_CANDIDATES`。選定の最終=KP先頭3+vocab(Advのみ)先頭5。
- 文法(Part 2): `er120_part2_grammar_production_01.py` `grammar_candidates.json`の`candidates[]`は**「解説する英文を1つ選ぶ」候補**(`sentence/feature_class/construct_ja/points_ja/context_ja/teaching_value_ja`)。`er119_kp_human_review_01.py` 65行`SLOT_RULES[KIND_GRAMMAR]={"grammar":{"min":0,"max":1}}`=現行は**最大1件**。**エンドユーザー向け解説本文は選定後に生成**され、候補時点では存在しない。
- 猿の手Advの正式Part 2候補: `er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01`に`grammar_candidates*`/`study_text`は無い(Glob 0件)。→ 試作では「候補なし・要生成」を表示、仮データは入れない。

## 3. 参照HTMLとの突合(判断候補の根拠)
- 参照フォームは「文法名+解説本文全文を表示して最大2件をチェック」。現行Part 2は「英文1件を選び、選定後に解説生成・最大1件」。**フォーム仕様(最大2・全文表示)と現行Part 2の差**は本委任の範囲外(下記判断候補はRESULT_PACKET_FORM1 (7))。
## 4. 公開ページの①②③ハイライト相当
- `user_test/family_z_monkeys_paw_01/advanced.html`をGrep(underline|highlight|<mark|class="kp…)→0件。①②③ハイライト(本文意味表示③を含む)の既存表示機構は同ページに確認できない。本委任では本文表示のProduction配線はしない(禁止事項どおり)。照合結果のみ記録。
