# CURRENT_FLOW_01 現行Part 2(文法)フロー調査(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01、read-only・API 0・JPY0、2026-10-27)

基準=`origin/main`(93915b971、KCP 委任_02B反映後)のHEAD版。行番号は`git show origin/main:<path>`基準。並行Agentが編集中のファイルは読むのみ。
略称: Std=Standard=`a2`、Adv=Advanced=`b1b`。stage名は現行どおり。

## 1. 共通核(全Family共通。再実装なし)

| 部品 | 役割 | 参照 |
|---|---|---|
| `er120_part2_grammar_production_01.py` | Prompt(StepA''/StepB、sha固定)・適格判定(`eligible7`)・Trial-08選定(`select_tiered`/`rank_eligible`)・候補doc・確定record・結果・fail-closed検査・描画 | `LEVEL="Advanced"`:42、`STEPA_PROMPT`:55(本文中に「Advancedレベル」「レベル: Advanced」の固定語)、`STEPB_PROMPT`:118、`TOP_N=2`:50、`rank_eligible`:417、`build_candidates_doc`:747(`"level": LEVEL`)、`select_from_candidates`:909(**単一`candidate`**)、`finalize_review_record`:968(`"level": LEVEL`)、`generate_explanation`:1117(1候補=1 call)、`build_result`:1134/`result_from_frozen`:1147(単一)、`run_part2`:1163(選定後にStep B)、`require_fresh_part2`:1272、`render_*`:1388-1421 |
| `er119_grammar_review_01.py` | 文法HR(kind="grammar")。候補保存・review状態・NG registry・依頼書 | `LEVEL_KEY="b1b"`:24、`pending_summary`:110(`"level": "Advanced"`固定)、`ensure_grammar_review`:148(`article_key.level=LEVEL_KEY`)、`render_request_md`:364(題「(Advanced)」固定。候補は構文名・教える価値・読み違い点のみ=**解説本文なし**)、`discover_dirs`:411(`<run>/b1b/study_text`と`<run>/study_text`の2か所固定) |
| `er120_part2_wiring_01.py` | runnerから呼ぶ薄い層(`candidate_stage`/`finalize_stage`/`require_final`/`verify_outputs`/`compose_page_html`/`public_study_html`) | `CAND_STAGE="part2_cand_b1b"`:26、`FINAL_STAGE="part2_b1b"`:27、`finalize_stage`:111(確定→M6凍結を使い、無ければStep B 0/1 call)、`public_study_html`:237(`<audio_dir>/b1b`固定) |
| `er128_kp_confirmed_content_01.py`(KCP) | 文法sidecar `confirmed_grammar.json`・凍結`confirmed_grammar_frozen.json`(M6)・G4 | `grammar_state`:835(`level=...or "b1b"`)、`load_frozen_grammar`:862(**単一`candidate_id`**)、`freeze_part2_result`/`freeze_from_sidecar`(`explanation_status=="provided"`ならStep B不要)、`guard_grammar`:964、`_write_grammar_sidecar`:1253(`gr.discover_dirs(run)[0]`=**level無視で先頭dir**)、from-form処理:1244(`groups["grammar"]`をそのままsidecarへ。**候補doc/事前生成との照合なし**) |

## 2. 現行の工程順(全Family共通の骨格)

```
本文確定(Adv) → [A] 候補抽出 Step A''(1 call, 実費¥0.26-0.88) → grammar_candidates.json + review(PENDING)
   → KP候補生成と同一待機点でHR待機(rc=4)。文法HRの提示=構文名/教える価値/読み違い点(解説本文なし)、HR選択=英文1つ(top1/top2/reselect/omit)
   → 確定(REVIEWED / UNREVIEWED_AUTO_ADOPTED[明示宣言のTOP1] / NO_CANDIDATE_UNREVIEWED)
   → Part 1(T1訳)後に [B] Step B 解説生成(選定した1件のみ, 1 call, 実費¥0.05-0.11, ref_jaをPart 1 poolから)
   → part2_result.json(単一) + md → 使う側(TTS/assemble/pages/player)でrequire_fresh_part2 → ページ(Part 1直後, Advの節のみ)
```
Std(a2)には上記のいずれも無い(候補抽出なし・HRなし・Step Bなし・ページブロックなし)。

## 3. Family別の現行呼出(全てAdvancedのみ)

### X(`er019_family_x_audio_production_runner_01.py`)
- Part 2節=628-720。study dir=`<out>/b1b/study_text`(`_part2_study_dir`:638)。入力=`<source_dir>/b1b/article.md`(`_part2_inputs_x`。`paragraphs_from_article_md`は`## In one line`で止まる)。
- scaffold内候補抽出: `if level == "b1b" and scaffold_only is None: run_part2_candidates_x(...)`(**:760**)。失敗=`part2_failed.json`+rc=3(support/KP未発注で停止)。待機はKPと統合しrc=4(:3500-3510)。
- `--stage study_text`: `if args.stage == "study_text" and "b1b" in levels`(**:3525**)で候補抽出(resumeはAPI 0)、`parser.error("--stage study_textはAdvanced(b1b)のみ対象です")`(:3548)。Part 1実行後に`run_part2_final_x`(Step B)。
- tts/assemble: `_part2_failed_markers`(:715-717 `lv == "b1b"`のみ)。入口検査`_require_part2_fresh_x`(:699)は`"b1b" in levels`時のみ(:3585)。
- player: `build_player_html`(:3022)は`{b1b_audio_html}{study_html}`の順で**Advの節の直後にだけ**study_htmlを置く。Stdの節(`a2_audio_html`)の後ろには何も置かない。`if "b1b" in levels:`でPart 1+Part 2連結(:3649-3664、コメント「Standard=a2には載せない」:3655)。R-3一致検証(:3667-3675)。
- 公開ページ: X公開ページは記事別の個別script(`er019_*_page_*.py`。例`er019_nws2_final_page_01.py:70`が`p1.study_html_for_audio_dir`をAdvの`tail=`にだけ渡す)。共通の公開ページbuilderは無く、`er120_part2_wiring_01.public_study_html`(:237)が「X公開ページ生成scriptが呼ぶ共通関数」。**Family差**(Y/Zは共有builderあり)。
- retry/regenerate/resume: X runnerには来歴ledgerが無い。`--stage study_text`が唯一の再実行点(候補はextract_signature一致でAPI 0再利用、確定済みはM6凍結で再抽出しない)。

### Y(`er121_family_y_runner_01.py`)
- stage=`STAGES`:34(`kp`内で候補抽出/確定)。unit=`part2_cand_b1b`/`part2_b1b`(:42-43)、依存`translate_b1b → part2_cand_b1b → part2_b1b`(:47-48)。**StdはAdvからの翻訳**(`translate_a2`はb1bに依存、:401-404)。
- `stage_kp`(:583): 冒頭で`_part2_cand_step`(:824。入力=`_part2_inputs`:794 `ys.canonical_body(b1b本文).split("\n\n")`、label=Adv英訳のタイトル行)→ levelごと(`for lv in LEVELS`)にKP review。待機は`pending`にKP(level別)+文法を1つにまとめrc=4。確定後Part 1→`_part2_final_step`(:848、`input_sha=final_stage_input_sha`、`write=False`でStep B、`p2w.write_md`)。
- 入口: `_assert_study_ready`(:912)を`tts_b1b`(:1016)/`gate`(:1064)/`assemble`(:1084)/`stage_pages`(:1102)/`page_verify`(:1156)で呼ぶ。Stdの`tts_a2`では呼ばない。
- ページ: `stage_pages`(:1097)が`levels=[a2,b1b]`を共有`ya.build_page_rows`で作り、**`if lvd["id"] == "advanced" and study_html: lvd["study_html"] = study_html`**(:1113)。共通`render_y_page`→`er_user_listening_page_common_01`(:51-70)はlevelごとの`study_html`(任意)を受ける(**Stdにも置ける構造は既にある**)。
- 検証: `_verify_part2_outputs`(:925-947付近)がindex.htmlのPart 2ブロック==1個、Part 1→Part 2の順、**`FAMILY_Y_PART2_ON_STANDARD_PAGE`(:945)=Part 2がAdvの節より前にあればSTOP**。
- regenerate: `ctx.regenerate_stage == PART2_CAND_STAGE/PART2_FINAL_STAGE`(:830/863)+`_stage_precheck`(親sha)。確定済み文法はKCP M6でrevoke必須。

### Z(`er026_family_z_fiction_production_runner_01.py` + `er062_family_z_writer_01.py` + `er063_family_z_audio_01.py`)
- Part 2節=1548-1710。study dir=`<out>/study_text`(:1562)。入力=`canonical_article_text(b1b本文).split("\n\n")`、label=`STORY_REGISTRY[story_key]["topic_title"]`(:1566)。
- stage=`part2_cand_b1b`/`part2_b1b`。`er062`のDEPENDENTS(:64-72): `r2 → [std_adjust, plan_b1b, kp_b1b, part2_cand_b1b]`、`part2_cand_b1b → part2_b1b`。Z Std本文は`std_adjust`(r2から)。
- 候補段=`stage_kp`内(:2012-2022)、finalize=Part 1後(:2123-2133)。`input_sha`: 候補=`cand_stage_input_sha`(本文sha+label+抽出signature)、finalize=`final_stage_input_sha`(本文sha+label+確定署名)。`_stage_precheck`:1572で有料呼出前に来歴規則で停止。
- 入口: `load_level_inputs`(:2275)内で`b1b`のときだけ`_assert_part2_final`(:2307)。TTS/Gate/Assembly共有。
- ページ: `stage_pages`(:2408)→`a63.build_pages(..., study_html=...)`。`er063:2588` `{"study_html": study_html} if (study_html and label == "Advanced")`。`_verify_part2_outputs`(:1685-1710): index.htmlに`Grammar &amp; Sentence Structure`が**1個**、`standard.html`/`advanced.html`(開発確認用)には無いこと、`FAMILY_Z_PART2_ON_STANDARD_PAGE`(:1708)。
- regenerate: `--regenerate-stage part2_b1b`=再finalize+子孫stale。再抽出はreselect CLIのみ(確定済みはrevoke必須)。

## 4. Std(a2)の学習ページ構成の現状
- Part 1「Vocabulary & Expressions」もPart 2もAdvのみ(X `:3649`、Y `:1113`、Z `er063:2588`、Part 1はER-003系`b1b`固定)。**Stdの節には学習テキストブロックが無い**(試聴ページのStd節は通し音声・再生順script・KP表のみ)。
- 共有ページ構造は`<section>`をlevel別に持ち、study_htmlはlevel別の任意blockとして既に受けられる(`er_user_listening_page_common_01.py:51-70`)。標準適合check(`check_page`)はstudy blockを`<h3>`+`<div>/<dl>`のみとしてtable/h2判定に触れない設計(同:70コメント)。→ **Stdへの文法ブロック追加は、既存builderのlevel条件(Y:1113/Z:er063:2588/X:player 3649)を外し、同一テンプレート`compose_study_html(part1_html="", result)`を再利用すれば足りる**(`part1_html`が空ならCSSを含める実装済み、er120:1421)。
- Std本文の由来: X=入力`{b1b,a2}/article.md`(runner冒頭コメント:26。a2はStd本文として別途存在し、kp/scaffold時点で確定済み)、Y=`translate_a2`(Advから)、Z=`std_adjust`(r2から)。**候補抽出の入力はStd本文自身**(Adv本文の英文をStdページに載せると、Std本文に無い文を解説することになるため不可)。Std本文はkp stage時点で確定済み(Y: translate_a2→kp、Z: std_adjust→kp、X: a2 article.mdはscaffold時点で既存)。

## 5. 現行の再実行・再生成機構(保存すべき既存安全装置)
- Step A''/B共通`_run_llm`(er120): routing検証→予算guard→1 call→構造検査→技術retry 1回→fail-closed。応答モデル不一致はSTOP(fallbackなし)。
- `resolve_candidates`(:791): extract_signature(本文sha+label+Prompt sha+model)一致の保存済み候補はAPI 0再利用。`frozen=True`(KCP)は確定済み文法でPrompt/model変更でも再抽出しない。
- `MAX_RESELECT=2`/`MAX_REEXTRACT=1`(:632-633)。全NG=exhausted→`RESELECT_EXHAUSTED`で自動ZEROにしない。
- 確定: REVIEWED/UNREVIEWED_AUTO_ADOPTED(明示宣言のTOP1)/NO_CANDIDATE_UNREVIEWED。UNREVIEWED_AUTO_ADOPTEDを「レビュー済み」に数えない(M-6)。
- KCP: `guard_grammar`(er128:964)が確定済み文法に対するreselect/omit/reextract/ng/unng/`--regenerate-stage part2_cand_*`を拒否(revoke必須)。本文変更はM8で選定文の逐語span残存なら`_rebind_grammar_text`でAPI 0再バインド、残らなければISSUE。

## 6. 観測した既存データ(候補数・実費。COST_ESTIMATE_01の根拠)
`er*_output/**/grammar_candidates.json` 26件(重複run含む)・`part2_result.json`のaudit(`total_cost_jpy`)を集計(ファイル読取のみ):
- 候補数(Adv): X 2/3/4(平均3.0、3記事)、Y 2-3(平均約2.3、1記事×複数run)、Z 0-1(平均約0.73、実質2記事: 『走れメロス』1件/『Tell-Tale Heart』0件)。**Std本文の候補数は未観測**(Std抽出は現行未実施)。
- Step B実費/call: X ¥0.0505-0.0596(出力445-558 tokens)、Y ¥0.0902(923 tokens)、Z ¥0.1122(1216 tokens)。Step A''実費/call: X ¥0.379-0.881、Y ¥0.481、Z ¥0.2595。モデル=`gpt-6-luna`(`routing.SUPPORT_MODEL`)。見積guard`est_jpy=0.3`(`generate_explanation`)は上限見込みで実測の2.7-6倍。
- 候補文とPart 1の引用英文(KP元文)の重なり: 18 run・28候補で0件(ref_jaが効く場面は稀。事前生成でref_jaを渡せない影響は小さい。DESIGN_01 §3-(b))。
