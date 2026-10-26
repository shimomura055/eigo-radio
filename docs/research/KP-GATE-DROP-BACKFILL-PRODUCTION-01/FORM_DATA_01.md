# FORM_DATA_01: Production候補doc→学習項目選定フォームv3のデータJSON(委任_03、2026-10-26)

変換tool=`tools/export_form_data_01.py`(API 0・入力docは変更しない)。データ契約=`DATA_CONTRACT_01.md`。フォームUI(`index.html`/`form_logic.js`)と既存データ(`monkeys_paw__b1b.json`、`ui_check_dummy__dummy.json`)は**不変**。生成コマンド=`evidence_runs/export_all_forms.sh`。

## 1. 追加した6件(`user_test/selection_form_v3/data/`、`articles.json`のindexへ登録。表示名に『Production候補・補完evidence』)
| ファイル | 元doc | 区分 | 候補(フレーズ/単語) | 補完 |
|---|---|---|---|---|
| `ai_island_temple__a2__prod.json` | X fresh AI島 a2 | PRODUCTION_FORMAL_PATH | 7/0 | 不発動(E=0。上限未満) |
| `ai_island_temple__b1b__prod.json` | X fresh AI島 b1b | PRODUCTION_FORMAL_PATH | 7/0 | 不発動(E=0。上限未満) |
| `redelivery_fee__a2__prod.json` | Y fresh 再配達 a2 | PRODUCTION_FORMAL_PATH | 7/0 | **発動(Gate除外1→補完1: `have a hard time`)** |
| `redelivery_fee__b1b__prod.json` | Y fresh 再配達 b1b | PRODUCTION_FORMAL_PATH | 6/1 | 不発動(E=0。救済1件`doesn't sit right with someone`あり) |
| `melos__a2__prod.json` | Z fresh メロス a2 | PRODUCTION_FORMAL_PATH | 7/0 | **発動(Gate除外1→補完1: `a knife flashed`)** |
| `monkeys_paw__b1b__prod.json` | replay R5a(Trial現行方式docの凍結+Production候補関数) | REPLAY_FROZEN_INITIAL_REAL_BACKFILL | 4/4 | 不発動(候補8=上限) |
- 猿の手は、Z runner経由のfreshがseed provenance不一致でSTOP(EVIDENCE_01 §6)のため、**replay由来**であることを`source.kind`と`source.note_ja`に明記した(『Production正式経路で生成』とは言わない)。メロスAdv(E=0・8件)は追加せず、補完が見えるa2を採用した(6件枠は委任文どおり)。
- 既存の猿の手Adv(Trial-02、`monkeys_paw__b1b`)は不変。新データは別slug(`*_prod`)で、状態キー(`slug__level`)が衝突しない。

## 2. 契約項目の出力(各entry)
`id`(=candidate_id)・`term`(=used_form)・`meaning_ja`・`excerpt`(既存4項目、フォームUIが使う)に加え、`kind`(phrase/word)・`origin`(call1/call2/backfill)・`ai_rank`・`auto_eligible`・`human_selectable`・`reason_ja`・`flags`(qa_fail/gloss_hr_pending/similar_to_ng/redundant_with/rescued/rescue_codes)・救済時は`rescue`要約。UI上の注記は`flag`/`flag_note_ja`(例『補完候補(Gate除外の代替)』『KP救済済み(REVERT_SURFACE)』『AUTO採用不可(人間のみ採用可)』)。doc単位で`backfill`要約(enabled/triggered/status/reason/E_total/N_total/added/dropped_by_stage)・`shortfall`・`shortfall_detail`(n_candidates/cap/missing/E_total/backfilled/unfilled_by_kind)・`shortfall_note_ja`(人が読める上限未達の理由)を持つ。`source`にkind/trial/run/text_sha256/model_id/prompt_sha256/note_ja。`grammar`は正式Part 2候補が無いため空で、`grammar_note_ja`=『候補なし・要生成』(仮データは入れていない)。
- フォームの枠(フレーズ≤7・単語≤5)を超える候補は`overflow[]`に保持し`shortfall_note_ja`で告知する(今回の6件では発生せず)。
- 古いdoc(`kind`欠落)は`word_count`相当(英単語数1)で補う。

## 3. 検証
- `run_project_regression.py --pattern "form1_selection_form_v3_test_01.py"` → collected=6 passed=6 failed=0。(JS単体test`selection_form_logic_test_01.js`を含む。articles.jsonの『9記事枠』判定は`_prod`slugを数えないよう1行だけ修正[新6枠を追加しても正式9枠の数え方を維持するため]。)
- 各データは`FL.validateArticle`相当(schema・slug/level/name・フレーズ≤7/単語≤5・term重複なし)を上記JS testの`index data files exist and valid`で検証済み。
- `er119_kp_backfill_test_01.py` collected=55 passed=55。
- 公開URL(push後、2026-10-26): `https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/` と `data/articles.json`・新6データ・既存`monkeys_paw__b1b.json`がHTTP 200(`articles.json`に`_prod`7箇所=6entry+note)。commit `2b3fcefe1`。
