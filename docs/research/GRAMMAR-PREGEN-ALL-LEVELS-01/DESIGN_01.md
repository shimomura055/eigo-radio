# DESIGN_01 文法解説の事前生成(全6経路 = Family X/Y/Z x Standard/Advanced)設計(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01)

Status: **DESIGN_READY**(Opus条件A依頼前。実装未着手・read-only・API 0・JPY0)。根拠=ユーザー正式決定(`APPROVED_FOR_PRODUCTION`、原文`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_USER.md` §1,§3,§5,§6)。現行フロー=`CURRENT_FLOW_01.md`、旧Adv限定の扱い=`ADV_ONLY_INVENTORY_01.md`。
承認済みの解説品質・文章量・学習内容(`STEPA_PROMPT`/`STEPB_PROMPT`のsha、`eligible7`、`select_tiered`、`TOP_N`)は**無変更**。変えるのは「いつ・何件・どのlevelで」生成/選定/確定/公開するかだけ。

## 0. 設計の要点(結論)
1. **工程順**: `候補抽出(Step A'')` → **`全候補のStep B解説を事前生成(新)`** → HR/フォーム(文法名+解説全文を提示、最大2件選択) → 確定(KCP sidecar+凍結) → `finalize`(**LLM 0 call**: 事前生成物から結果を組立) → 公開ページ。旧「選定後にStep B」は撤去(§4)。
2. **Standardにも同じ核**を適用: Std本文自身を入力に、同一Prompt・同一閾値で候補抽出。候補0件は正常(`NO_CANDIDATE_UNREVIEWED`、待たず確定、ページには既存の固定文面)。
3. **最大2件採用**を結果/ページ/凍結に通す(`part2_grammar_v2`、`items[]`)。現行の単一選定(`select_from_candidates`が単一`candidate`)を複数対応に拡張し、HR不在宣言のauto採用はTOP1のみ(既存承認条件を維持)。
4. **Family差の解消**: 共通核に`level`引数を追加し、X/Y/Zは「入力本文・stage台帳・ページ差込点」のadapterだけを持つ。
5. **確定内容保護**: 事前生成物のshaを固定→フォーム表示=確定=公開を一致させる(KCP M6の凍結を複数item化)。確定後の再生成禁止はKCP `guard_grammar`をStdにも適用。

## 1. 新しい工程順(各level独立。X/Y/Zとも同じ骨格)

```
level in {b1b(Adv), a2(Std)} それぞれ:
  本文確定
   -> [A] part2_cand_<lv>  : Step A''(1 call。resumeはextract_signature一致でAPI 0) -> grammar_candidates.json, review=PENDING_REVIEW/NO_CANDIDATE_UNREVIEWED
   -> [A2] part2_expl_<lv> : 候補ごとにStep B(1 call/候補、直列、上限PREGEN_MAX) -> grammar_explanations.json(全て揃うまで次へ進まない)
   -> KP候補生成と同一の待機点(rc=4。依頼書=KP+文法(level別)を1つに統合):
        依頼書/フォームに「文法名(construct_ja)+解説全文(explanation_md)+対象英文」を全候補分表示
   -> 確定: フォーム送信(`confirm --from-form`)または HR CLI(`grammar-select --choice pick --ids ..`)。最大2件。
        form経路=KCP確定レコード+sidecar(items<=2, explanation_status=provided)+凍結(source=form_displayed)
   -> (Part 1(T1訳)は従来どおり Adv のみ。Advのfinalizeは従来どおりPart 1後に実行[pool照合のため]、Stdは Part 1 が無くpoolなし。解説生成に参考訳は不要)
   -> [B] part2_<lv>      : finalize = LLM 0 call。確定ids -> 事前生成/凍結の解説を組立 -> part2_result.json(v2) + md
   -> 使う側(TTS/assemble/pages/player/page_verify)入口で require_fresh_part2(複数item対応)
   -> ページ: Adv=Part 1直後に文法ブロック / Std=Stdの節に文法ブロックのみ(Part 1は対象外、§10-Q3)
```
- 事前生成の位置: 候補抽出直後・待機の前。X scaffold(support/KP発注の前)、Y/Z `stage_kp`冒頭(KP候補生成の前)。**失敗はKP/supportを発注する前に止まる**(現行の候補抽出失敗と同じ規則)。
- `ref_ja`(Part 1の訳を参考訳として渡す機構)は事前生成では使えない(選定前=Part 1訳なし)。実測で候補文とPart 1引用文の重なり0/28(CURRENT_FLOW_01 §6)。重なりが生じた場合はKCP既存の`pool_ref_ja_issue`(確定した訳と異なるPart 1訳→ISSUE、黙って作り直さない)で扱う(§3-(b))。

## 2. データモデル(study_dir = level別)

study dir: Adv=既存path不変(X `<out>/b1b/study_text`、Y/Z `<out>/study_text`)、Std=`<out>/a2/study_text`(新、X既存規約に統一)。単一関数`study_dir_for(family, out_dir, level)`。

| ファイル | 変更 | 内容 |
|---|---|---|
| `grammar_candidates.json` | `level`を`Advanced`/`Standard`(記録値)に。他は不変 | 候補doc(`candidates_sha256`) |
| **`grammar_explanations.json`(新, `grammar_explanations_v1`)** | 新設 | `{level, text_sha256, candidates_sha256, stepb_prompt_sha256, model, items:{candidate_id:{sentence, construct_ja, explain_signature, explanation_md, sections, translation_ja, audit{usage,cost_jpy,response_ids}, generated_at}}, skipped_over_cap:[candidate_id..], explanations_sha256}` |
| `grammar_human_review.json` | `grammar_human_review_v2`: `selection:{choice, candidate_ids:[<=2], zero_reason}`、`decision.explanations_sha256`(提示した解説のsha) | v1(単一`candidate_id`)は読取互換。署名式はschema別(v1記録の署名は不変=既存Adv確定を壊さない) |
| `confirmed_grammar.json`/`confirmed_grammar_frozen.json`(KCP) | frozen v2: `items[]`(各itemは現行frozenの項目と同じ。`frozen_sha256`の式不変) | v1(単一)は`items`長1として読取互換 |
| `part2_result.json` | `part2_grammar_v2`: `items[]`(各item=現行の`selection`/`translation_ja`/`explanation_md`/`sections`/`explain_signature`or`frozen`)。ZEROは現行どおり`status:"ZERO"` | v1は`items`長1へ正規化して検査/描画(書換えない) |
| `study_text/part2_grammar_sentence_structure.md` | 1件=現行とバイト同一。2件=同ブロックを本文英文の出現順に連結 | `render_markdown`の決定論描画 |

- 候補数の上限`PREGEN_MAX=8`(実測最大4、§6 D-c)。超過分は`skipped_over_cap`に記録(黙って捨てない)しフォームにも出さない。
- 選定上限`GRAMMAR_MAX=2`(ユーザー決定「文法は独立枠で最大2件」)。**0件選択も可**(任意)。
- `explain_signature(cand, ref_ja=None)`をそのまま使う(現行式)。事前生成物はこのsignatureで有効性を判定(候補の材料欄・Prompt sha・modelが同じ→API 0再利用)。

## 3. 指定項目(a)〜(h)

### (a) 工程順と各段の挙動
- **候補抽出**: `ensure_grammar_review`を`level`引数化(§3-(d))。Std本文の適用可否=Prompt sha・`eligible7`・`select_tiered`・閾値**無変更**で入力本文のみ変える(Promptの「Advancedレベル」固定語は維持、§6 D-a)。候補0件=`NO_CANDIDATE_UNREVIEWED`=待機なし、`grammar_status=no_candidates_found`(フォームに「該当なし」)。
- **事前生成**: `pregen_stage(study_dir, doc, call_fn, budget_guard)`。`for cand in doc.candidates[:PREGEN_MAX]`: 有効な既存解説(signature一致)があればskip、無ければ`generate_explanation(cand, None)`(**既存関数・既存Prompt・`_run_llm`の技術retry1回・モデル不一致STOP・fallbackなし**)。1候補ごとに`grammar_explanations.json`を原子的に更新(途中失敗でも成功分を保持→再開でAPI 0)。
  - 失敗(2回構造NG/モデル不一致/予算超過): `part2_failed.json`(stage=`part2_expl`)+STOP(rc=3)。**不完全な候補一覧でHR/フォームへ進まない**(§6 D-b)。
  - 直列。候補数<=8のため最悪でも数分。並列化(`ThreadPoolExecutor`)は`cl.logging_context`のスレッド安全性確認後の任意最適化(IMPL F-2注記)。
- **HR/フォーム提示**: §3-(c)。
- **確定**: 最大2件。保存は§3-(e)。
- **finalize**: §3-(b)。
- **ページ**: `compose_study_html(part1_html, result)`を両levelが同一テンプレートで使う(Stdは`part1_html=""`、CSSは自動付与済み)。2件=`<div class='study-item'>`を2つ(同一`<section class='study'>`内、`<h3>Grammar &amp; Sentence Structure</h3>`は1つ)。表示順=**本文の出現順**(段落番号→文の位置。決定論。ユーザーの選択順やrank順ではない。§6 D-e)。
- **0件(ZERO)のStd**: Advと同じ固定文面ブロック(`ZERO_P2`)を出す(共有builderをlevel分岐させない。§6 D-d)。

### (b) 旧「選定後Step B」の重複防止
- Step Bの呼出点を**1か所**(`pregen_stage`)に集約。`run_part2`/`finalize_part2`は`explanations`(事前生成物)か`frozen`を受け、**無ければ`Part2Stale`でfail-closed**(黙ってその場生成しない)。
- 旧run互換(`legacy_postselect`): 候補docに`grammar_explanations.json`が無く、かつreview確定済み+`part2_result.json`(v1)が存在する既存Adv run、のときだけ旧経路を許可(新規Step Bを呼ばず既存resultを正規化して使う)。pregenはこの場合**実行しない**(未選択候補への無駄な課金を避ける)。
- resume: 事前生成物はsignature一致でAPI 0。finalizeは常にAPI 0。→ **1 run内のStep B総数 = 生成した候補数(<=PREGEN_MAX)**。test(TEST_PLAN T3)で`generate_explanation`呼出回数をspyして固定。
- `--regenerate-stage`の扱い:
  | 指定 | 未確定 | 確定済み(sidecar/frozenあり) |
  |---|---|---|
  | `part2_cand_<lv>` | 再抽出(Step A'' 1 call)→候補doc更新→pregenは新候補分のみ生成(同一`candidate_id`+signature一致は再利用) | KCP `guard_grammar`で拒否(revoke必須) |
  | `part2_expl_<lv>`(新) | 事前生成物を破棄して再生成(N call、明示指定時のみ) | 拒否(`guard_grammar`のop追加) |
  | `part2_<lv>`(finalize) | 再組立(API 0)+子孫stale | 再組立(API 0。凍結値を使用) |
- 有料の自動再生成を新設しない: 上限は`_run_llm`の2 call/候補、reextract上限1、reselect上限2(既存値)。

### (c) 文法HRとフォーム確定の関係(HR CLI経路でも解説全文を見せる)
- 提示物(HR依頼書`grammar_human_review_request.md`・`grammar-show`・フォーム用データ)は同一の`form_grammar_items(study_dir)`から生成: `[{id=candidate_id, title=construct_ja, body=explanation_md(全文), example=sentence, rank, ai_recommended(rank1), para, feature_class}]`。依頼書は題を`Part 2 文法解説 Human Review 依頼({Advanced|Standard})`に、候補ごとに**解説全文**と`選ぶ: --ids <id>[,<id>]`コマンドを載せる。
- 操作: `grammar-select --level {a2|b1b} --choice pick --ids g1[,g2] [--accept-ai] --reason ... --candidates-sha ... --by ...`。`top1`/`top2`は`pick`の単件ショートカットとして維持。`omit`/`reextract`/`reselect`/NGは現行意味を維持(reselectは候補がPREGEN_MAX超で未表示の場合のみ提示)。
- フォーム経路: `confirm --from-form`(KCP)に文法照合を追加(§3-(e))。フォーム側データ(`export_form_data_01.convert(grammar=...)`は既に引数で受ける、`main()`が未接続)へ`form_grammar_items`を接続する契約を**フォーム担当委任と共有**(IMPL F-5)。`grammar_status`に`no_candidates_found`(本文に該当なし)を追加する依頼(現行は`candidates_available|no_candidates_ungenerated`の2値で、0件を「未生成」と誤表示する)。
- フォームと現行Part 2のHR(英文1つ選択)の型不一致(UDR-FORM-1)は、**フォーム型(文法名+解説全文・最大2)に揃える**ことで解消(ユーザー決定済み)。選定基準(Trial-08のTier順位)は変更しない: 候補の並び=`rank_eligible`順、AI推奨=rank1(`select_tiered`の1件と一致、既存test維持)。

### (d) X/Y/Z共通核への配線点(Family差の解消)
共通核の追加/変更(`level`引数化。**Prompt/閾値は触らない**):
| 部品 | 変更 |
|---|---|
| `er120_part2_grammar_production_01.py` | `level`引数(`LEVELS={"b1b":"Advanced","a2":"Standard"}`)。`pregen_explanations()`・`select_from_candidates`の複数id対応(`pick`)・`finalize_review_record` v2・`build_result` v2(`items[]`)・`require_fresh_part2`/`_expected_outcome`/`verify_selection_matches_outputs`の複数item対応・`render_markdown`/`render_html_block`のitems対応(1件は現行とバイト同一)。`run_part2`から`generate_explanation`呼出を撤去 |
| `er119_grammar_review_01.py` | `LEVEL_KEY`→引数、`pending_summary(level)`、`render_request_md`(解説全文・level題)、`discover_dirs(run, level=None)`、`op_decide(choice="pick", ids=..)`(`guard_grammar`はid集合で照合) |
| `er120_part2_wiring_01.py` | `stage_names(level)`、`study_dir_for`、`pregen_stage`、`finalize_stage`(LLM 0)、`require_final`、`form_grammar_items`、`public_study_html(audio_dir, level)` |
| `er119_kp_human_review_cli_01.py` / `er119_kp_wiring_01.py` | `grammar-*`に`--level`、統合依頼書/bannerのpendingにlevelを表示 |
| `er128_kp_confirmed_content_01.py`(KCP) | §3-(e) |
adapter(Family固有。差はここだけ):
- **X**: scaffoldの`level in ("b1b","a2")`で`run_part2_candidates_x`+`run_part2_pregen_x`(support/KP発注前)。`--stage study_text`を`--level a2`/`both`許容(`parser.error`のAdv限定を撤去)。tts/assemble/player入口の`"b1b" in levels`条件をlevel別に。`build_player_html`にStd節の文法ブロック(`a2_audio_html`直後)。記事別page scriptは`public_study_html(level=)`呼出へ。
- **Y**: `UNIT_NAMES`/`DEPENDENTS`に`part2_cand_a2`/`part2_expl_{b1b,a2}`/`part2_a2`を追加(`translate_a2 → part2_cand_a2 → part2_expl_a2 → part2_a2`、`part2_cand_b1b → part2_expl_b1b → part2_b1b`)。`stage_kp`で両levelの候補/事前生成。`_assert_study_ready`を`tts_a2`にも。`stage_pages`で`lvd["id"]`に応じ各levelのstudy_htmlを差込(`if lvd["id"] == "advanced"`撤去)。`_verify_part2_outputs`を「各levelの自節に1個」検査へ(`ON_STANDARD_PAGE`置換)。
- **Z**: `er062`のDEPENDENTS/ALL_STAGESに追加(`std_adjust → part2_cand_a2 → ...`)。`load_level_inputs`のb1b限定撤去。`build_pages(study_html_by_level={"a2":..,"b1b":..})`(`er063:2588`の`label=="Advanced"`撤去、引数をlevel別dictに。`study_html: str`は後方互換で残す)。`_verify_part2_outputs`をlevel別へ。
- stage_precheck/`ensure_stage`(Y/Z): 事前生成stageの`input_sha`=`sha(candidates_sha256|stepb_prompt_sha|model)`。確定済みで候補doc本文sha一致なら記録値を据え置く(KCP `cand_input_sha`と同じ規則。revoke必須のためmodel変更で解消不能STOPになるのを避ける)。

### (e) KCP M6凍結との接続
- 事前生成物の`explanation_md`は`explanations_sha256`と`decision.explanations_sha256`で**提示時点を固定**。フォームには`explanation_md`全文がそのまま載る(`body`)。
- `confirm --from-form`(KCP)の文法検証を追加(R5): 各grammar itemについて `id ∈ 現在の候補doc`、`title == construct_ja`、`explanation_full == 事前生成物.explanation_md`(バイト一致)、`explanation_status=="provided"`、件数<=2、重複idなし。いずれか不一致→ISSUE(rc=4・黙って置換しない)。sidecarは**対象levelのstudy_dir**へ(`discover_dirs(run)[0]`のlevel無視を廃止、`--level`必須)。同じreview_lock内で文法reviewに`pick(ids)`を適用(現行は「KP selectのみで、文法reviewへは別途grammar-select」の二段。atomic化)。
- 凍結(`freeze_from_sidecar`)をitem反復に拡張→`confirmed_grammar_frozen.json` v2(`items[]`、`source=form_displayed`)。`require_fresh_part2`は凍結あり→各itemを`frozen:<sha>`+選定文の逐語span+candidate_id一致で判定(M6の規則をitemごとに適用)。`guard_grammar`は`ids`集合(既に複数対応)で判定。
- CLI経路(フォームなし): `decision.explanations_sha256`を記録。`confirm --adopt-existing`相当で保護下に置けば同じ凍結(`source=hr_displayed`)。保護下に無い(AI auto採用/KCP未確定)場合も、`finalize`は事前生成物をそのまま使い再生成しない(上書きされない)。
- 本文変更: 確定itemの選定文が新本文に逐語で残れば`_rebind_grammar_text`でAPI 0再バインド(各item)。1つでも残らなければISSUE(全体をrc=4。黙って一部を捨てない)。
- 事前生成物自体の再生成が確定内容に影響しない理由: 確定後は凍結値が正であり、`part2_expl_<lv>`の再生成は拒否(§3-(b))。

### (f) Trial-08選定方式との整合
- 変更しないもの: `eligible7`・Tier1(INV以外)/Tier2(INV)/Tier3(なし)・`PRIORITY`・`rank_eligible`の順序とspan重複除外・`TOP_N`の意味(AI推奨=rank1)・Trial-07/08の29標本回帰test。
- 変わるもの: ユーザーに見える**提示物**(解説全文が加わる)と、選べる件数(1→最大2)。`select_tiered`の1件=AI推奨としてフォームに表示(rank1)。Trial-08の「最大1件選定」は**AI推奨の決定規則**として維持され、ユーザー選択の上限(2)とは別層。
- 回帰: 事前生成後も`candidates[0]`が`select_tiered`と一致(TEST T1)。

### (g) 費用(詳細`COST_ESTIMATE_01.md`)
- 実測: Step B ¥0.05-0.11/call(X 0.055/Y 0.090/Z 0.112)、Step A'' ¥0.26-0.88/call。候補数(Adv)X平均3.0/Y約2.3/Z約0.73。
- 増分/記事セット(Adv追加分+Std新規): X約¥0.9(範囲0.6-1.3)、Y約¥0.8、Z約¥0.34(実測ベース)。ユーザー式(¥0.3x候補数)の保守見積でもX約¥2.7/Y約¥2.1/Z約¥0.9。¥70/記事セット比 0.5-1.9%(実測)/<=4.6%(保守)。Std候補数は**未観測**(実測の最優先項目。EVIDENCE_PLAN)。

### (h) 旧仕様参照のretry/fallback/Validator/test
`ADV_ONLY_INVENTORY_01.md` §1,§6を正本とする(撤去/更新/履歴化/維持の一覧)。要点: `*_ON_STANDARD_PAGE`検査は「自levelの節にだけある」検査へ置換、`m.LEVEL=="Advanced"`等のtestは更新、Prompt byte一致test・`_run_llm`のretry/モデル不一致STOP・reselect/reextract上限・`er119_isolation_test_01`(A/B/Cへ文法kindを持ち込まない)は維持。

## 4. retry / fallback / regeneration / resume の整理(確定内容が不当に変わらないこと)

| 事象 | 挙動(新) | 確定内容への影響 |
|---|---|---|
| Step A''/B 構造NG | `_run_llm`の技術retry 1回→なお失敗でSTOP(`part2_failed.json`)。fallbackなし | 確定前のみ発生 |
| 事前生成の途中失敗 | 成功分を保持してSTOP。再開で未生成分だけ生成 | なし |
| resume(同一コマンド再実行) | 候補/事前生成/finalizeすべてAPI 0(signature一致) | 不変 |
| 候補の再抽出(未確定) | 新候補分のみpregen。NG済みは共有registry | 確定前のみ |
| 確定後の再抽出/reselect/omit/ng/regenerate | `guard_grammar`で拒否(revoke必須)。Stdにも適用 | 保護 |
| 本文変更(Local Rewrite/再生成) | 確定itemの選定文が逐語残存→再バインド(API 0)/残らない→ISSUE | 黙って書換えない |
| モデル/Prompt/routing変更 | 確定済みはfrozen:<sha>で判定(再抽出・再解説しない)。未確定は新signatureで再生成 | 保護 |
| Part 1訳との食い違い(稀) | KCP `pool_ref_ja_issue`→ISSUE | 黙って作り直さない |

## 5. 失敗終了時の最終成果物(目的要件への適合)
- 事前生成STOP: 候補doc+review(PENDING)+部分的`grammar_explanations.json`+`part2_failed.json`。TTS/ページは作られない(部分公開物なし)。ユーザー向けの不完全なフォームを出さない。
- ISSUE(rc=4): `confirmed_content_issue.json/.md`に差分・次の一手。確定レコード/凍結値は不変。
- どの失敗でも**ユーザーが確定した文法名・解説全文は書き換わらない**。

## 6. Fable設計判断事項(推奨付き。いずれもユーザー決定の範囲内で、新仕様ではない)

| ID | 論点 | 選択肢 | 推奨 |
|---|---|---|---|
| D-a | Step A''のPromptがAdv語固定(「Advancedレベル」「レベル: Advanced」「B1〜B2相当」)。Std本文へ適用する際 | (1)Prompt無変更(sha不変・Trial-08回帰同一) (2)level差込(sha変更=Production Prompt編集で別承認) | **(1)**。ユーザー決定「解説品質・学習内容を独断変更しない」に合致。Std候補の質(偽陽性/ZERO率)を実測し、問題が出た場合のみ(2)を`判断候補`化 |
| D-b | 事前生成の失敗時 | (1)STOP(rc=3、再開で未生成分のみ)(2)失敗候補を除外して続行 | **(1)**(不完全なフォームを出さない。既存fail-closed思想) |
| D-c | 事前生成の上限 | 無制限 / `PREGEN_MAX=8` | **8**(実測最大4。費用ガードで承認範囲内) |
| D-d | StdのZERO時の表示 | Advと同じ固定文面 / Stdでは非表示 | **同一**(builderをlevel分岐させない=単純・検査も共通。固定文面は承認済み) |
| D-e | 2件採用時の表示順 | 本文出現順 / 選択順 / rank順 | **本文出現順**(読解順・決定論) |
| D-f | 事前生成のStep B入力 | `ref_ja=None` | 採用(選定前にPart 1訳が無いため。重なり実測0/28、稀な食い違いはISSUEで保護) |
| D-g | Std文法ブロックの位置 | Stdの節の末尾(Part 1なし) | 採用(共有builderの`study_html`をStd節に差込) |
| D-h | auto(不在宣言)採用 | TOP1のみ(既存承認条件) | 採用(2件自動採用は承認範囲外) |

## 7. 範囲外・他委任との接続・新仕様候補
- **Q3(Fable報告のみ・実装しない)**: Part 1「Vocabulary & Expressions」はAdvのみ(S3)。今回のユーザー決定は文法解説のみ。Std学習ページの構成(Part 1が無く文法のみ)が意図どおりかはFable確認事項。Stdへ広げる提案はしない。
- フォーム側(LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_04)とは`form_grammar_items`契約(`{id,title,body,example}`+`grammar_status`3値)と`explanation_full==事前生成物`の一致のみで接続。フォームUI変更は無し。
- KCP(委任_02B)とは`grammar_state`/凍結のitem複数化・level別sidecar・`cmd_from_form`の文法照合で接続(KCP完了後に実装。IMPL F-6)。ファイル所有が衝突するため**KCP側の担当に引渡すか、KCP完了後に本委任系で改修**。
- OPEN新規起票文案・SSOT文案は`docs/pm/RESULT_PACKET_GPG1.md` (8)。
