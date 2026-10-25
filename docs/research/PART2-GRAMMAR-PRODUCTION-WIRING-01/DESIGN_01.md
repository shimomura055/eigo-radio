# DESIGN_01(Part 2「Grammar & Sentence Structure」+Trial-08選定方式 Production module設計)

管理ID: PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_01 / 日付: 2026-10-25 / Status: **APPROVED_FOR_PRODUCTION(ユーザー2026-10-25)・module実装済み・未配線(PRODUCTION_WIREDではない)**。Production runner/er119/公開ページ変更0・API 0。
前提: `EXISTING_SPEC_CHECK_01.md`(承認済み仕様の固定・Level=Advancedのみ・Y入口なし)。参照パターン: Part 1(`er003_kp_general_explanation_01.py`)。実装: `er120_part2_grammar_production_01.py`、test: `er120_part2_grammar_production_01_test_01.py`(77 PASS)。

## 0. 要点
| 項目 | 内容 |
|---|---|
| 新規module | `er120_part2_grammar_production_01.py`(名称衝突なし: `ls er120*`=0件。X/Y/Z共通。Family分岐・runner参照なし) |
| 工程 | ①候補抽出(Step A'' 1 call) → ②決定論Tier順位付け(`rank_eligible`) → ③選定(Human/自動) → ④T1訳(1 call、Part 1既訳はAPI 0再利用) → ⑤Step B解説(1 call) → ⑥決定論の組立・描画 |
| LLM | `gpt-6-luna`(`routing.SUPPORT_MODEL`)。processは`STUDY_TEXT_GRAMMAR_EXTRACT`/`STUDY_TEXT_GRAMMAR_EXPLAIN`(原価・routing監査をPart 1と分離)。T1訳は既存`KEY_PHRASE_SOURCE_SENTENCE_JA` |
| 対象レベル | Advancedのみ(Trial条件と同一) |
| 失敗時 | 技術retry1回→**fail-closed**(`Part2Error`)。解説欠落のまま公開しない。parse不能を0件扱いにしない |
| 承認対象外の事項 | Tier内順位・TV=HIGH判定・OTHER分類・Prompt改良は**一切変更なし**(Prompt byte一致test) |

## 1. I/F(`er120_part2_grammar_production_01.py`)
| 関数 | 入力 → 出力 | 備考 |
|---|---|---|
| `paragraphs_from_article_md(text, stop_heading_prefixes=("## In one line",))` | X `article.md` → 本文段落list | Trial `work_data7`と同一処理。Zは`canonical_article_text(..).split("\n\n")`をそのまま渡す |
| `stepa_prompt(paragraphs, label)` | → Step A'' prompt | `label`=作品名/タイトル(1行) |
| `parse_candidates(text, paragraphs)` | LLM応答 → features(逐語解決・連結再解決・単一span検証) | 不正=`Part2StructureError`(retry対象) |
| `eligible7` / `select_tiered` / `tier_table` | Trial同一 | 回帰の正本 |
| `rank_eligible(feats)` | → `[(feature, tier)]`(Tier1全件→Tier2全件。同一(段落,文)重複除外) | 先頭は常に`select_tiered`と一致(`test_B2`) |
| `extract_candidates(paragraphs, label, *, call_fn, client, budget_guard, round_no, rejected_ids)` | → `grammar_candidates.json`のdoc | 1 call。構造不正はretry1回→STOP |
| `resolve_candidates(..., cached)` | 本文sha・label・Prompt sha・model一致でAPI 0再利用 | resume/copy-run |
| `review_request(doc)` | → er119 `kind="grammar"`へ渡す提示(TOP1/TOP2・`n_more`・`ai_recommended`・`choices`・`auto_default`) | 0件=`choices=["omit"]` |
| `select_from_candidates(doc, review, mode)` | → `{status, candidate, source}` | §3 |
| `reselect_candidates(doc, rejected_ids)` | 再選定(API 0。却下累積。枯渇=`exhausted`) | 枯渇時の再抽出は呼出側が`extract_candidates(..., rejected_ids, round_no+1)` |
| `translate_sentence(sentence, *, ref_ja_pool)` | T1訳(既存module再利用) / Part 1既訳プール | |
| `generate_explanation(cand, ref_ja)` | Step B 1 call+構造検査 | |
| `run_part2(paragraphs, label, *, review, mode="wait", cached_*, ref_ja_pool, *_call_fn, budget_guard)` | orchestrator → `{status, candidates, result, review_request}` | `PENDING_REVIEW`では有料のStep B・訳を呼ばない |
| `require_fresh_part2(result, paragraphs, label, *, next_command, where)` | 使う側のfail-closed確認(本文sha・signature・単一span・解説非空) | ZEROは正当な最終状態 |
| `write_artifacts` / `render_markdown` / `render_html_block(result, *, include_css)` | 保存・描画 | |

## 2. 成果物スキーマ(`<out>/b1b/study_text/`)
- `grammar_candidates.json`(`grammar_candidates_v1`): `status`(HAS_CANDIDATES/NO_CANDIDATE)、`text_sha256`、`extract_signature`、`prompt_template_sha256`、`model`、`round`、`candidates[]`(`candidate_id`[段落+正規化文のsha]、`rank`、`tier`、`feature_class`、`para`、`sentence`[本文の逐語span]、`teaching_value_ja`、`construct_ja`、`points_ja`、`context_ja`、`misread_*`、`prev/next`)、`top_ids`(先頭2件=TOP1/TOP2)、`tier_table`(全featureの適格/不適格理由=監査)、`rejected_ids`、`candidates_sha256`、`audit`(model・prompt_sha・response_id・usage・cost_jpy・retried_for_parse)。
- `part2_result.json`(`part2_grammar_v1`): `status`(SELECTED/ZERO)、`zero_reason`(no_candidate/human_omit)、`selection`(source[auto_top1/human_top1/human_top2…]・candidate_id・rank・tier・段落・文)、`translation_ja`+`translation_source`(T1/part1_pool)、`explanation_md`+`sections`、`explain_signature`、`audit`(extract/translate/explain)。
- `part2_grammar_sentence_structure.md`(組立済み、LLMなし)。

## 3. 文法HR接続点(er119共通核 `kind="grammar"`、本委任ではHR側を実装しない)
- 提示: `review_request(doc)`→TOP1/TOP2(順位・Tier・分類・段落・英文・`teaching_value_ja`)+残り件数+AI推奨(=TOP1)。選択肢=`top1|top2|reselect|omit`(ユーザー決定④)。
- 確定: `select_from_candidates(doc, review, mode)`。
  - Human review有り: `top1/top2/omit/reselect`。`candidates_sha256`が違えば`Part2ReviewError`(古い候補へのreviewを拒否)。
  - review無し: `mode="auto"`(er119/呼出側が**明示宣言**した場合のみ)→TOP1自動採用(`source=auto_top1`=未レビューを最終承認扱いしない旨がsourceに残る)。`mode="wait"`(既定)→`PENDING_REVIEW`(有料のStep B・訳へ進まない=HR待ちで無駄な費用を出さない)。
  - 候補0件: Humanの判断対象がないため待機せず`ZERO`(Trial-07の0件許容)。
- 再選定: API 0で次順位に進む(却下累積)。枯渇時のみ再抽出(0.32円)。
- Human確認の記録(修正内容・理由): ユーザー決定「Human Reviewの修正内容・理由を改善に使える形で記録」はer119の`history`/`verdicts`側(KP HR設計§b-1)。本moduleは`rejected_ids`・`selection.source`・`tier_table`(不適格理由)を提供し、er119が`kind="grammar"`のhistoryへ記録する(次委任)。
- 解説の再生成: Humanが選択を変えると`explain_signature`(候補ID+材料欄+ref_ja+Step B sha+model)が変わり、新選定の訳・解説のみ再生成(候補は再利用。`test_D4`)。

## 4. retry / regeneration / resume
| 事象 | 挙動 |
|---|---|
| 構造不正(JSON・見出し・禁止語)・incomplete応答 | **技術retry1回**→なお不正なら`Part2Error`(fail-closed)。QA起因の再生成ループは作らない(新Validatorなし) |
| 応答model≠期待model | retryもfallbackもせずSTOP(routing契約) |
| API例外(network/rate) | clientの既定retryに任せ追加ラッパなし。例外はstage失敗として伝播 |
| resume(同一本文・label・Prompt・model) | 候補・結果ともAPI 0で再利用(`test_D2`) |
| 本文変更(Writer r2再生成/Local Rewrite) | `text_sha256`が変わる→候補再抽出。Zは`ensure_stage`のProvenanceMismatch+`DEPENDENTS`(`r2`の従属に`part2_b1b`追加、次委任)、Xは署名不一致で自動再生成。古い結果は`require_fresh_part2`が拒否(`test_D3`,`test_E3`) |
| KP再選定 | **影響なし**(Part 2はKP非依存。KP HRの再選定でPart 2を再生成しない) |
| 外側retry(KP選定の最大3回等) | Part 2はretryループの外・後工程。Part 2失敗でKP選定をやり直さない |
| 予算 | `budget_guard(stage, est_jpy)`を各call前に呼ぶ(Z`_guard`/X`budget_check`をhookで渡す)。例外でAPI前に停止(`test_D13`) |

## 5. 配置と描画(次委任の配線指針)
- 本文確定後(KPと独立)・TTS前。Z=新stage`part2_b1b`(`ensure_stage`、`kp`と並列可)、X=scaffold b1b内(KP PASS後)+再実行stage。
- 使う側(TTS/Gate/Assembly入口・`stage_pages`・X player/公開ページ)で`require_fresh_part2`をfail-closed確認(Part 1 M2と同型。`PENDING_REVIEW`・未生成・古い=公開不可)。
- 描画: `render_html_block(result, include_css=False)`をPart 1ブロック(`p1.render_html_block`)の**直後**に連結して`study_html`へ渡す。規約はPart 1と同一(`<section class='study'>`・`<h3>`・`<dl>`、`<table>`/`<h2>`不使用、LLM出力はエスケープ後`**`→`<b>`、ページ非表示語regex非該当)。Part番号は出さない。0件は`ZERO_P2`文面。
- Part 2は承認済み仕様のため描画の追加flagを置かない(Part 1のT1判断記録のような未決はない)。ただしrunnerに配線されるまで発火しない(module単体はAPI 0・出力0)。

## 6. 費用・時間(実測ベース。詳細`BUDGET_PLAN_01.md`)
Step A'' 0.32円 + T1訳 0.03〜0.08円 + Step B 0.08円 ≒ **0.43〜0.48円/セット**(ユーザー推定0.41円と整合。70円比0.6〜0.7%)。HRでTOP2選択=+0.11円、再選定(枯渇)=+0.32円。時間は+約30〜60秒(Trial実測の合算。KPと並列化で追加≒0)。

## 7. Dangling Reference 対策
- moduleは`docs/research`/`run_trial_*`をimportも文字列参照もしない(`test_P2`)。Trial資産はtestでのみ読む(回帰fixture)。
- 旧ルール/旧testの撤去対象なし(Part 2はProductionに無かった。Grep: 本module以外に`rank_eligible`/`STUDY_TEXT_GRAMMAR_*`参照0)。Trial資産(`run_trial_07/08.py`・`PART2_TRIAL0*_RESULTS`・OUTPUT_07/08)はDEV資産として残置(ProductionからはimportしないのでDangling 0)。
- 配線後に更新する記述: `DESIGN_04.md §1`・`ADOPTION_NOTE_08.md §3`の「Production未配線」へ追記(原文は消さない)。

## 8. 残リスクと扱い(承認対象外のため触れない)
- TV=HIGH判定のばらつき・低価値な非倒置の優先・OTHER未対応・Tier内順位(猿P18/P22): Trial-08 EVAL §5の既知課題。ユーザー決定により**Wiring延期理由にしない・本委任で変更しない**。HRのTOP2/再選定がAI選定の弱点を受け止める設計(29標本中19標本が候補2件以上、4標本が1件、6標本が0件=HRで選べる余地の実測)。
- 構造検査(D-3)が良質な応答を誤って落とす可能性: Trial-07の実Step B出力(有料7件、`_raw_07_07_r1_stepB_*.txt`)の7/7が検査を通ることを`test_A5`で固定済み(誤棄却0)。
