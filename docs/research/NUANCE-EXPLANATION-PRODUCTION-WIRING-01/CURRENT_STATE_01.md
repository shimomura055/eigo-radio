# CURRENT_STATE_01 現状調査(NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_01a)

調査専用・API 0・Productionコード/Prompt/SSOT/公開物の変更0。file:lineはHEAD(work/post-merge-01)の実測(2026-10-29)。並行Worker(JA-ASR配線・Family Y統合)が編集中のファイルは行番号がずれ得るため、実装時に再Grepすること。
背景: `docs/research/NUANCE-EXPLANATION-LOSS-INVESTIGATION-01/INVESTIGATION_01.md`(ニュアンス解説は独立Partとして一度もProduction配線されていない)、ユーザー原文 `docs/pm/delegation_log/2026-10-29_NUANCE-EXPLANATION-PRODUCTION-WIRING-01_USER.md` §2。

## 1. 結論(要点)

1. **学習解説(Part 1/Part 2)の組立・表示は X/Y/Z・Std/Adv の6経路すべてが、単一の共通builderを通る。** 表示の合流点は `er120_part2_wiring_01.compose_page_html`(:507) -> `er120_part2_grammar_production_01.compose_study_html`(:1449)。X公開ページは `public_study_html`(er120_part2_wiring:518)経由、X player/Y/Zは `compose_page_html` を直接呼ぶ。**ニュアンス解説の表示・文法0件の非表示は、この1か所の変更で全Family・全levelに及ぶ**(ただし検証側のブロック数検査は3か所に分散、§4)。
2. **HR確定データはlevel別 `<kp_dir>/confirmed_selection.json`(KP/Word、区分①②③)と level別 `<study_dir>/confirmed_grammar.json`(文法sidecar、0件=`items:[]`)。** 確定は `er128_kp_confirmed_content_01.cmd_from_form`(:1390)が1か所で行い、文法reviewを同じロック内で更新する。ニュアンスの採否は**この確定コマンドに乗せる**のが最小変更(新HR系統を作らない)。
3. **文法0件の現行表示は、見出し+固定文面**(`ZERO_P2`、er120_part2_grammar_production:161、描画:1433-1436)。ユーザー承認(2026-10-29 §2C)で「コーナー全体非表示」へ変更が必要。固定文面は md(`render_markdown`:1415-1420)・HTML(`render_html_block`:1430-1436)・検証(`count_grammar_blocks`:1962、`verify_selection_matches_outputs`:1368)・各runnerの `_verify_part2_outputs`(Y:1031-/Z:1843-)・テスト7ファイルに及ぶ(§5)。
4. **resume/regeneration時の確定保持の仕組みは既にある**(凍結値 `confirmed_grammar_frozen.json`、`stale_or_rebind`(er128:765)、`--regenerate-stage` のrevoke前拒否[CONFIRMED_CONTENT_LOCKED])。ニュアンスは同じ型(sidecar+本文引用の逐語再結合)で載せられる。

## 2. Family × Level × 工程 現状表

凡例: Adv=`b1b`(Advanced)、Std=`a2`(Standard)。`study_dir`は `er120_part2_wiring_01.study_dir_for`(:70): X=`<out>/<level>/study_text`、Y/Z Adv=`<out>/study_text`・Std=`<out>/a2/study_text`。`kp_dir`: X=`<out>/<level>/key_phrases`、Y/Z=`<out>/key_phrases/<level>`(er128 `display_spec_of`:483が両形を走査)。

| 工程 | X (er019 runner) | Y (er121 runner) | Z (er026 runner) | 共通core |
|---|---|---|---|---|
| KP/Word候補生成+HR待機 | `_kpw().run_kp_with_review` er019:997 | `_kp_review_step` er121:572 -> `kw.run_kp_with_review`(:583) | `_kp_review_step` er026:2143 -> 同(:2164) | `er119_kp_wiring_01.run_kp_with_review`:59 -> `er119_kp_human_review_01.ensure_kp_review`:1370 |
| 文法候補+Top2事前生成 | `run_part2_candidates_x` er019:805(candidate_stage:820 + pregen_stage:831) | `_part2_cand_step` er121:887(`stage_kp`:614が両levelを先に実行) | `_part2_cand_step` er026:1726 | `er120_part2_wiring_01.candidate_stage`:84 / `pregen_stage`:130 / `candidate_and_pregen_stage`:168 |
| HR待機(rc=4)の合流 | `pending_banner(KP+文法)` er019:3925/3955/3965/3984 | `YKpReviewPending`(er121:71,655)-> banner er121:1696 | `FamilyZKpReviewPending` -> banner er026:3250 | `er119_kp_wiring_01.write_unified_request`:121 / `pending_banner`:130(`review_request.md`にKP+文法を1つへ統合) |
| KP/Word確定(HR結果) | フォーム->`confirm --from-readable`->`cmd_from_form` | 同 | 同 | `er128_form_readable_restore_01.cmd_from_readable`:504 -> `er128_kp_confirmed_content_01.cmd_from_form`:1390 |
| 文法確定(HR結果) | 同上(同一payload `selection.grammar[]`) | 同 | 同 | `cmd_from_form`内 `_validate_form_grammar`:1503 / `_apply_form_grammar_review`:1587 / `_write_grammar_sidecar`:1609。KP先行確定時は `cmd_grammar_from_form`:1645 |
| 文法finalize(LLM 0) | `run_part2_final_x` er019:838 | `_part2_final_step` er121:935 | `_part2_final_step` er026:1774 | `finalize_stage`:309 |
| 使う側の入口検査 | `_require_part2_fresh_x` er019:862(tts/assemble/player) | `_assert_study_ready` er121:1004(Adv)/`_assert_std_study_ready` :1013(Std) | 同(Z) | `require_final`:395 / `verify_outputs`:432 |
| 試聴ページへの合成 | player: er019:4082-4094(`compose_page_html`)。公開ページ: `er019_family_x_listening_page_01.py:161`(`public_study_html`) | `stage_pages` er121:1271(合成:1291) | `stage_pages` er026:2613(合成:2638-2639) | `compose_page_html`:507 -> `compose_study_html`(er120 prod:1449) -> `er_user_listening_page_common_01`(:219-238 `lv.get("study_html")`で挿入)。Y/Zは `er063_family_z_audio_01.build_pages`(:2697-2736、`study_html_by_level`) |
| ページ検証 | player: er019:4114(`verify_outputs`) | `_verify_part2_outputs` er121:1031(`n2 != 1`でSTOP:1049-) | `_verify_part2_outputs` er026:1843(`n2 != 1`:1861-) | `verify_selection_matches_outputs`:1357(当該levelの節に文法ブロック**ちょうど1個**:1368、md/HTMLの決定論描画一致:1370-1373) |
| stage/provenance | file存在+sha(X) | `STAGES`:34 / `UNIT_NAMES`:43 / `DEPENDENTS`:46(`part2_cand_<lv>`,`part2_<lv>`) | `E2E_STAGES`:1183 / `PART2_STAGES`:1675 | 来歴=`ensure_stage`(Y/Z)。再実行=`--regenerate-stage`、完成段=`--stages provision_shell,gate,assemble,pages,page_verify`(Z) |

### Level差(Std/Adv)
- Part 1(Vocabulary & Expressions、①②=最大5件): Adv=常に、Std=確定レコードが `display_spec` 付き(新記事のみ。遡及なし)のときだけ(`er120_part2_wiring_01._part1_enabled`:512、`er128.display_spec_of`:483、`er119.vocab_enabled`:501)。
- 区分: ①Key Phrase最大3 / ②追加解説(①と合わせ最大5=vocab) / ③本文意味表示(短い訳のみ)(`er119.SLOT_RULES`:63、`KP_FINAL_MAX`=3、`VOCAB_COUNT_MAX`=5)。**ユーザー原文の「Key Phrase・Word(最大5件)」=①+②(解説あり5件)**と読むのが自然(§2B。③は短い訳のみで「解説の焦点」を持たない)。
- 文法(Part 2): Std/Adv両level、AI評価Top1/Top2を提示し原則1件・0件可(2026-10-27ユーザー正式決定。`er119_kp_human_review_01.SLOT_RULES[KIND_GRAMMAR]`:65 `{"min":0,"max":1}`、`export_form_data_01.GRAMMAR_PRESENT_MAX`:28)。

## 3. HR確定データの保存先・resume時の読み方

| データ | 保存先 | 書く関数 | resume時の読み方(読取関数) |
|---|---|---|---|
| KP/Word候補doc(`candidates_sha256`) | `<kp_dir>/kp_candidates.json` | `rv.save_candidates`:918 | `rv.load_candidates`:266。本文sha不一致=STALE(再生成)。確定レコードがある場合は `stale_or_rebind`(er128:765)が出典文の逐語存在でAPI 0再結合、無ければISSUE(rc=4) |
| KPレビュー状態 | `<kp_dir>/kp_human_review.json`(`PENDING_REVIEW`/`REVIEWED`/`UNREVIEWED_AUTO_ADOPTED`...) | `rv.op_select`:648 他 | `rv.load_review`:259。確定済みreviewは再選定しない(`ensure_kp_review`:1370) |
| KP/Word確定(ユーザー) | `<kp_dir>/confirmed_selection.json`(`eigo_radio_confirmed_selection_v1`。items=①②、`unconsumed`=③、`confirmation_id=cf_*`、history chain、`display_spec`) | `er128.save_record`:212 | `er128.live_user_record`:224 / `load_verified_items`:1331(G1照合を通してから返す。part1=vocab最大5件) |
| 文法候補/解説/review | `<study_dir>/grammar_candidates.json` / `grammar_explanations.json` / `grammar_human_review.json` | `er119_grammar_review_01`・`er120.write_artifacts`:1389 | `gr.load_candidates`/`load_review`/`load_explanations`。v2は事前生成物が無いとINTEGRITY(`_check_integrity`:301) |
| 文法確定sidecar | `<study_dir>/confirmed_grammar.json`(`eigo_radio_confirmed_grammar_v2`、`items`、`presented_ids`、`explanation_sha_by_id`、`confirmation_id`、`kp_dir_rel`、`sidecar_sha256`) | `er128._write_grammar_sidecar`:1609 | `er128.grammar_state`:934(sha自己整合+`confirmation_id`==確定レコード。`status=pending`は未確定扱い) |
| 文法の凍結値 | `<study_dir>/confirmed_grammar_frozen.json` | `er128.freeze_part2_result_items`:1047 他 | `er128.load_frozen_grammar_items`:983(以後の再生成でも確定時の解説全文を逐語維持) |
| 文法の最終結果 | `<study_dir>/part2_result.json` + md | `finalize_stage`:309 -> `er120.write_artifacts`:1389 | `require_final`:395(古い/不整合=Part2Stale[STOP rc=3]、未確定=Part2NotConfirmed[rc=4]) |
| 統合依頼書 | `<run>/review_request.md` | `write_unified_request`:121 | 人間が読む。承認の正本ではない |
| フォーム提出元 | `<kp_dir>/confirmed_selection_source/rev<N>_payload.json` | `cmd_from_form`:1390- | 監査用 |

- **resume**: 同じ制作コマンドの再実行。候補sha一致なら再選定せずAPI 0(`ensure_kp_review`、`pregen_stage`は未生成分のみ)。確定済み(`live`)のKP/文法は凍結・照合され、`--regenerate-stage`で変えようとするとrevoke前は拒否(`CONFIRMED_CONTENT_LOCKED`、er019:824 / er121:905 / er026:1745 のD4)。
- **regeneration**: 本文が変わる再生成(LR等)は `stale_or_rebind`(er128:765)が、確定itemと文法選定文の出典文が新本文に**逐語で残る場合のみ**API 0で結合。残らない場合はISSUE(確定を黙って破棄しない)。
- **fallback/retry**: KP外側retryは候補生成段(`kcand.make_generate_fn`、`rv.RESELECT_MAX`=2)で閉じ、確定後のretryは確定レコードで保護(G1/G2/G3、er128:530-/825-)。

## 4. 文法0件時の現行表示(変更対象)

| 場所 | 現行 | 根拠 |
|---|---|---|
| 公開HTML | `<section class='study'>` + `<h3>Grammar &amp; Sentence Structure</h3>` + 固定文「今回の本文には、このPartで特に取り上げる難所となる構文はありませんでした。」 | `er120_part2_grammar_production_01.py:1433-1436`、定数`ZERO_P2`:161 |
| study_text md | `# Grammar & Sentence Structure` + ZERO_P2 | `:1415-1420`(`render_markdown`) |
| 検証 | 各levelの節に文法ブロック**ちょうど1個**を要求 | `:1368`、`count_grammar_blocks`:1962、Y `_verify_part2_outputs`:1049-1051、Z:1861-1863 |
| 0件が起きる状態 | `status != "SELECTED"`(候補なし[`NO_CANDIDATE_UNREVIEWED`]/ユーザー省略[`omit`]/全候補NG[`RESELECT_EXHAUSTED`->omit]/AI島のように提示後にユーザーが0件確定) | `er119_kp_human_review_01.py:42-44`、`finalize_part2_v2`:1790 |
| AI島(公開候補)実例 | Std/Adv共に0件確定(`confirmed_grammar.json items:[]`)で上記の見出し+固定文面を表示 | INVESTIGATION_01 §6(`user_test/family_x_ai_island_form_01_candidate_b7_01/index.html:11,21`) |

- 「候補提示後にユーザーが省略」でも同一文面が出る点は INVESTIGATION_01 §6 で既に指摘済み。今回の仕様変更(非表示)で解消する。
- **CSSの行き先**: Part 1が空のとき、CSSはPart 2側が持つ設計(`compose_study_html`:1449の`include_css = not part1_html`)。**Part 2が空になるとCSSの行き先がなくなる**ので、Part 1/文法/ニュアンスのうち最初に出るブロックがCSSを持つ規則に一般化する必要がある(設計§7)。

## 5. 影響を受ける既存テスト(0件固定文面/ブロック数を期待値にしているもの)

固定文面や「ブロックちょうど1個」をassertしており、仕様変更で**期待値そのものの是正が必要**(不整合な出力を期待値にしない)。
- `er120_part2_grammar_production_01_test_01.py`:108(ZERO_P2一致)、:398、:506
- `er119_grammar_review_test_01.py`:150
- `er120_part2_pregen_test_01.py`:399、:649(`count_grammar_blocks==2`)、:664
- `er120_part2_wiring_integration_test_01.py`:236、:466
- `er121_family_y_runner_01_test_01.py`:788
- `er003_kp_general_explanation_01_runner_integration_test_01.py`(3件)、`er019_x_highlight_wiring_test_01.py`(2件)に `Grammar & Sentence` 参照(内容は実装時に再Grep)
- Z runnerのtest(`er026_family_z_*_test*.py`)の `part2_blocks` 期待は実装時に再Grep

## 6. 隔離・分離の現状(A/B/C互換確認)

- er119/er120/er128を直接importするのは X/Y/Z runner・listening page・共通核のみ(`er119_isolation_test_01.py` TestImportersAreOnlyXZRunners:ALLOWED)。**Family A/B/Cは Part 1/Part 2/HR共通核を使わない**(`sc.run_key_phrases`の共有関数は無変更をshaで固定:`er119_isolation_test_01.py`)。
- 新moduleがer119を直接importする場合は、このALLOWED一覧(test側)の更新が必要(設計§11)。

## 7. 補足

- フォームV3 `selection_form_v3` の照合コードは `AIF1-<stem>-<d6>-<c8>-<t8>-<s10>-<g10|0>-<m8|0>-<k4>`(`er128_form_readable_restore_01.py:48` CODE_RE、固定8区画)。ニュアンスの採否を人間可読コピーに載せるには版を上げる必要がある(`AIF2`、設計§6)。
- フォームデータexporterは `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`(docs配下のtool。Production運用の一部)。`--grammar-study-dir` で文法のform bundleを読む(:13)。ニュアンスも同型の入力口を足す。
- `er133_*` は既に使用済み(`er133_report_marks_01.py`)。新moduleは `er134_nuance_explanation_01.py` を提案(着手時に再確認)。
