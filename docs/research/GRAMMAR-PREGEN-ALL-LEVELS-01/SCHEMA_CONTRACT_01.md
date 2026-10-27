# SCHEMA_CONTRACT_01 文法解説の事前生成: schema契約(F-0。委任_02a。委任_03/04が参照する唯一の契約)

Status: **CONTRACT_FIXED**(文書先行。実装=`er120_part2_grammar_production_01.py` / `er120_part2_wiring_01.py` / `er119_grammar_review_01.py` の委任_02本体commit)。API 0。
根拠: ユーザー正式決定(APPROVED_FOR_PRODUCTION、`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_USER.md`)、DESIGN_01、Opus条件Aレビュー(`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_OPUS_RESULT_01.md` 必須修正1〜7)。
承認済みの解説品質・Prompt(`STEPA_PROMPT`/`STEPB_PROMPT`の本文・sha)・`eligible7`・Trial-08 Tier・文章量は**無変更**。契約が決めるのは「いつ・何件・どのlevelで・どの形で保存/受け渡すか」だけ。

## 0. 共通規則
- **level** は文字列キー `b1b`(Advanced)/`a2`(Standard)。`LEVELS = {"b1b": "Advanced", "a2": "Standard"}`。候補docの`level`欄は表示名(`Advanced`/`Standard`)。**levelは全APIの必須引数**。`b1b`既定値・`discover_dirs()[0]`・`LEVEL_KEY`/`m.LEVEL`からの暗黙決定を廃止(`m.LEVEL="Advanced"`はv1読取専用の定数として残し新コードは参照0)。
- 候補doc(`grammar_candidates.json`)の`level`と呼出しの`level`が一致しない場合は **fail-closed**(pathからの推定はしない)。
- study dir: Adv=既存path不変、Std=新設。`study_dir_for(family, out_dir, level)`:
  - X: `<out>/<level>/study_text`(b1b=`<out>/b1b/study_text`、a2=`<out>/a2/study_text`)
  - Y/Z: b1b=`<out>/study_text`(既存)、a2=`<out>/a2/study_text`
- v1(単一選定)の成果物は**読取互換**(書換え・再署名しない)。新規書込みはv2。

## 1. `grammar_explanations.json`(`grammar_explanations_v1`。新設。事前生成物)
場所: `<study_dir>/grammar_explanations.json`(候補0件でも空itemsで必ず作る=「事前生成を通った」印)。
```
{
  "schema": "grammar_explanations_v1",
  "level": "Advanced"|"Standard",
  "text_sha256": "<候補docと同じ>",
  "candidates_sha256": "<最後に書いた時点の候補doc>",   // 情報。有効性判定は項目単位のexplain_signatureで行う
  "stepb_prompt_sha256": STEPB_PROMPT_SHA256, "model": MODEL, "pregen_max": 8,
  "items": [ {                                          // 候補rank順(本文出現順ではない)
      "candidate_id": "g…", "level": "Advanced"|"Standard",
      "title": "<候補のconstruct_ja>", "sentence": "<候補の英文>", "para": "P3",
      "explanation_md": "<Step B全文(【日本語訳】…)>", "translation_ja": "<【日本語訳】節>",
      "explanation_sha256": sha256(utf8(explanation_md)),
      "explain_signature": explain_signature(cand, ref_ja=None),   // 材料欄・Prompt sha・modelが同じなら再利用
      "generated_at": "…", "model_id": "<応答model>",
      "source": "pregen" | "stepB_generated",             // pregen=確定前に生成しユーザー提示対象 / stepB_generated=確定後(v1進行中run・auto採用)に生成しユーザー未閲覧
      "audit": {…} } ],
  "skipped_over_cap": ["g…"],                            // PREGEN_MAX(8)超過の候補(黙って捨てない)
  "explanations_sha256": sha256(json([[candidate_id, explanation_sha256] を candidate_id昇順])),
  "written_at": "…"
}
```
- 有効判定(fail-closed): 各itemの`explanation_sha256==sha256(explanation_md)`、`explain_signature==explain_signature(現在の候補, None)`、`candidate_id`が現候補docに存在、`explanations_sha256`再計算一致、`level`一致、`text_sha256`一致。1つでも不一致→`Part2Stale`。
- 「完全」=現候補doc先頭`PREGEN_MAX`件(`ids`指定時はその部分集合)の全itemが有効。不完全のままHR/フォームへ進まない。
- `part2_failed.json`(`part2_failed_v1`、既存形式): 事前生成の失敗は `stage="part2_expl_<level>"` で書く(成功分は`grammar_explanations.json`に保持。再開は未生成分のみ)。

## 2. 文法review `grammar_human_review_v2`
場所: `<study_dir>/grammar_human_review.json`(`kind="grammar"`)。署名は`rv.save_review`が`er120.grammar_selection_signature`(schema別式)で計算。
```
{ "schema": "grammar_human_review_v2", "kind": "grammar", "level": "Advanced"|"Standard",
  "text_sha256", "candidates_sha256", "round", "status", "revision", "article_key": {"family","slug","level":"b1b|a2"},
  "mode_declaration": null|{auto宣言},
  "selection": { "choice": "pick"|"omit"|"none",
                 "candidate_ids": ["g…"…最大2。本文出現順(段落番号→段落内位置)に正規化。クリック順に依存しない],
                 "zero_reason": null|"human_omit"|"human_rejected_all"|"no_candidate"|"form_submission_no_grammar" },
  "decision": { "choice": "pick|top1|top2|omit|reselect|reextract", "candidate_ids": […(入力順)], "candidates_sha256", "reason", "by", "accept_ai",
                "explanation_sha_by_id": {"g…": "<explanation_sha256>"…},   // 提示した解説のid別sha(新候補追加だけでは古い扱いにならない)
                "channel": "cli"|"form" },
  "verdicts", "ng", "reselect_count", "reextract_count", "history", "selection_signature" }
```
- 選択上限`GRAMMAR_MAX=2`、**0件も可**(`omit`)。`top1`/`top2`は`pick`の単件ショートカット(decision.choiceに入力どおり残し、selection.choiceは`pick`)。
- auto(不在宣言)=**TOP1のみ**(`status=UNREVIEWED_AUTO_ADOPTED`、`choice=pick`、`candidate_ids=[TOP1]`)。2件自動採用はしない。
- 署名payload(v2): `{kind, schema:"v2", level, text_sha256, candidates_sha256, status, selection:{choice, candidate_ids: sorted, zero_reason}, verdicts, mode_declaration, ng: sorted ids}`。**v1の署名式は完全に保存**(schema=v1のrecordはv1式)。
- **フォームで文法0件**: 同一ロック内で`omit`(zero_reason=`form_submission_no_grammar`)を適用(API: `gr.apply_form_selection`)。冪等(同じ入力の再送は変更なし)。
- 書込み順(KCP from-form。Opus O-4): 検証を全て済ませる→**KPロック→文法ロック**→(1)文法review→(2)sidecar→(3)KPレコード保存(commit点)。
- v1(`grammar_human_review_v1`、単一`selection.candidate_id`)は読取互換。v1署名式・`decision`形はそのまま。

## 3. `part2_result.json`(`part2_grammar_v2`)
```
{ "schema": "part2_grammar_v2", "level": "Advanced"|"Standard", "status": "SELECTED"|"ZERO", "zero_reason": null|…,
  "text_sha256", "extract_signature", "candidates_sha256", "round",
  "items": [ {                                         // 本文出現順(段落番号→段落内位置)。ZEROは[]
      "selection": {"source": "human_pick|human_top1|human_top2|auto_top1", "candidate_id", "rank", "tier", "feature_class", "para", "sentence", "construct_ja", "teaching_value_ja"},
      "translation_ja", "translation_source": "pregen"|"stepB_generated"|"frozen", "ref_ja": null,
      "explain_signature": "<signature>"|"frozen:<sha16>", "explanation_md", "sections": {…}, "explanation_sha256",
      "frozen": "frozen:<sha16>"（凍結由来のみ）, "frozen_source": "form_displayed|hr_displayed|stepB_generated_frozen" } ],
  "audit": {"extract": …, "explain": {candidate_id: {…}}}, "generated_at" }
```
- `render_markdown`/`render_html_block`: 1件は現行(v1)とバイト同一。2件は同ブロックを本文出現順に連結(`<section class='study'>`と`<h3>Grammar &amp; Sentence Structure</h3>`は1つ、`<div class='study-item'>`をitemごと)。ZEROは固定文面`ZERO_P2`(Std/Adv同一)。
- v1の`part2_grammar_v1`は`items`長1(ZEROは0)へ正規化して検査・描画(書換えない)。
- result v2は事前生成物(または凍結値)からの**決定論的組立(LLM 0 call)**。Step Bは`pregen_explanations`のみが呼ぶ。

## 4. 凍結 `confirmed_grammar_frozen.json` v2(KCP所有。委任_03/04で書込みを実装)
```
{ "schema": "eigo_radio_confirmed_grammar_frozen_v2", "confirmation_id",
  "items": [ {"candidate_id","sentence","construct_ja","explanation_md","sections","translation_ja","ref_ja_at_freeze","source","frozen_sha256"} …],
  "frozen_at", "file_sha256" }
```
- 各itemの`frozen_sha256`式は現行`frozen_sha_of(candidate_id, sentence, explanation_md, translation_ja)`と同一。v1(トップレベルに単一item)は`items`長1として読取互換。
- `er120_part2_wiring_01`は凍結を **list[item]** として扱う。現行er128(v1)しか無い間は、1件のみ従来関数で、2件以上は`Part2Stale`(KCP v2未対応のためfail-closed)。KCP v2が実装されたら、wiringは`getattr`で自動的にそちらを使う。
- **KCP v2が実装すべき関数名(委任_04。追補)**: `load_frozen_grammar_items(study_dir) -> list[item]|None`(確定レコード無し/凍結なし=None) / `freeze_from_sidecar_items(study_dir, selected_candidates) -> list[item]|None`(sidecarの`explanation_status=provided`全文を凍結。Step Bを呼ばない) /
  `freeze_part2_result_items(study_dir, result)`(通常検査を通ったv2結果の凍結。出所=stepB_generated_frozen) / `verify_part2_items(study_dir, result)`(G4: v2結果が確定した文法集合・凍結解説全文と一致。ZEROと確定の矛盾はINTEGRITY)。
  wiringは4関数を`getattr`で個別に検出する(`load_frozen_grammar_items`が無ければv1経路)。v2結果(`items[]`)をv1関数へ渡す場合は単件viewにする(2件以上はfail-closed)。

## 5. `form_grammar_items`(フォームexporter / KCP from-form向け。API 0の純関数)
`er120_part2_wiring_01.form_grammar_items(study_dir, *, level)` / `form_grammar_bundle(study_dir, *, level)`。事前生成が不完全・`part2_failed.json`あり・explanations不整合なら**データを出さずエラー**(`candidates_available`扱いにしない)。
```
bundle = { "level": "b1b|a2", "grammar_status": "candidates_available"|"no_candidates_found", "n_not_generated": <PREGEN_MAX超で解説未生成の件数>, "items": [...] }
item   = { "id": "g…"(=candidate_id。DATA_MODEL_02の既存キー), "candidate_id": "g…", "level": "Advanced|Standard",
           "title": "<construct_ja>", "explanation_full": "<explanation_md全文>", "explanation_status": "provided",
           "explanation_sha256": "<…>", "example": "<英文>", "rank": 1, "ai_recommended": true|false, "para": "P3", "feature_class": "CLEFT" }
```
- 並び=候補rank順(AI推奨=rank1=`select_tiered`の1件)。表示順の決定は本文出現順ではなくフォーム側のUI責務。
- KCP `cmd_from_form`の文法照合(委任_03/04): 各itemで`id ∈ 現候補doc`、`title == construct_ja`、`explanation_full == explanations[id].explanation_md`(バイト一致)、`explanation_sha256`一致、`explanation_status=="provided"`、件数≤2、重複idなし。不一致→ISSUE(rc=4)。sidecarは`study_dir_for(…, level)`へ。
- `grammar_status`は0件で`no_candidates_found`(旧`no_candidates_ungenerated`=未生成とは区別)。

## 6. ISSUE(Part 1訳とStep B訳の食い違い。Opus O-1)
- 事前生成物は`ref_ja=None`。Adv(Part 1あり)では、選定文がPart 1訳pool一致で、`pool訳 != 結果の【日本語訳】`(凍結の有無に関係なく)なら **ISSUE(rc=4、`Part2NotConfirmed`)**。`require_fresh_part2`(v2)は`ref_ja_pool`を署名照合に使わない。
- 解消手段(2つ): (a) 別候補を選ぶ/省略する(`omit`/`pick`)、(b) ユーザーが了承して現状のまま進める(`gr.op_accept_translation_diff(study_dir, ids, by, user_ref, reason)`。`--user-ref`必須、`grammar_translation_ack.json`へ記録、再送は冪等)。CLI配線は後続委任。
- Std(Part 1なし)はpool空のためISSUEなし。
- ISSUEは `grammar_translation_issue.json`(差分と解消手段)に記録。了承は `grammar_translation_ack.json`(Step B訳とPart 1訳のshaに結びつく=Part 1訳が変われば了承は効かない)。

## 8. 補足(実装で確定した細部)
- `pregen_stage(study_dir, *, level, next_command, ..., all_candidates=False)`: 未確定=全候補(source=pregen) / 確定済み(auto採用・v1確定)=選定済みidだけ(source=stepB_generated。凍結値のある候補は生成しない)。`all_candidates=True`(明示opt-in・有料)は、auto採用済みrunで全候補の解説を見て選び直す事後Reviewのため。
- 事前生成物のsourceは「生成時点」を表す(pregen=確定前=ユーザー提示対象 / stepB_generated=確定後=ユーザー未閲覧)。結果itemの`translation_source`は pregen|stepB_generated|frozen。
- `decision.explanation_sha_by_id`: 凍結なしの選定itemは、結果の`explanation_sha256`がこのshaと一致すること(確定=提示=公開)。凍結ありのitemは`frozen:<sha>`が正。
- `gr.discover_dirs(run, level=None)`: level未指定は全levelの列挙のみ(status表示用。b1b,a2の順)。選択・sidecar書込みには必ずlevelを指定する(未指定の`[0]`は禁止)。
- v1の確定済みreview(`grammar_human_review_v1`)+結果なし(進行中run)はreviewをv1のまま保ち、finalizeはv2結果+v1署名で突合する。未確定のv1 reviewは`ensure_grammar_review`がv2へ置換(履歴引継ぎ)。

## 7. 公開API(委任_03/04が参照する関数名)
`er120_part2_grammar_production_01`: `LEVELS`, `level_name`, `PREGEN_MAX`, `GRAMMAR_MAX`, `pregen_explanations`, `validate_explanations`, `explanations_complete`, `select_from_candidates_v2`, `review_request_v2`, `finalize_review_record_v2`, `finalize_part2_v2`, `result_items`, `require_fresh_part2`(v1/v2自動判別), `verify_selection_matches_outputs`, `translation_issues`。
`er120_part2_wiring_01`: `study_dir_for`, `stage_names`, `candidate_stage`, `pregen_stage`, `candidate_and_pregen_stage`, `finalize_stage`(LLM 0), `require_final`, `verify_outputs`(節単位4者一致), `public_study_html(level=)`, `form_grammar_items`, `form_grammar_bundle`。
`er119_grammar_review_01`: `ensure_grammar_review(level=)`, `op_decide(choice="pick", ids=…)`, `apply_form_selection`, `op_accept_translation_diff`, `discover_dirs(run, level)`, `render_request_md`(解説全文・fail-closed)。
