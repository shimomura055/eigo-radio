# EVIDENCE_RESULT_07 (委任_07G) X標準公開page再取得(API 0)
対象: F班X複製run `er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_gpg5_x_01_s23f`(untracked run dir)。証跡=evidence_runs/x2/。
実行: `er019_family_x_listening_page_01.py --slug part2_hr_evidence_01 --run-name run_gpg5_x_01_s23f --web <run>/pages_s23g_N`(2回、rc=0/0、`10_listening_page_run{1,2}.txt`)。F班ではrc=3 STOPだったbuilderが完走。
| 項目 | 結果 |
|---|---|
| 出力・builder内検査 | index.html出力。builder内の check_page(public)・G3 verify_highlights・verify_outputs・X_PART1_BLOCK_COUNT を通過(rc=0)。独立検査 `21_verify_page_public.json`: check_page overall=PASS、failed 0 |
| Part 1 | Std/Advともh3 "Vocabulary & Expressions"ちょうど1個(①3+②2=5件、期待語と一致、`part1_items_equal_cat12=true`)、各項目に日本語の「本文中の意味/本文の英文/日本語訳/解説」(`22_structure.txt`)。Part 1→Part 2(Grammar)の順 |
| data-hl | Std/Adv とも lk1=3/lk2=2/lk3=2 = 確定件数、id集合一致 |
| ③訳リスト | 確定japanese_gloss逐語一致(Std: tariff / reach a record high、Adv: shortage / impose) |
| public ⏸ | 0(pause_total_in_html=0、data-hl内0、chunk_mark_spans 0) |
| 確定レコード | a2/b1b confirmed_selection.json はbuilder実行より前のmtime(再書込なし)。sha a2=3fb900f1…、b1b=c9c7c5e8… |
| 再実行 | index.html sha256同一(e9227af7a1997c91…)×2 |
| NOTICE | Std: HL_OCCURRENCE_RELOCATED 1件(F班既知・停止しない設計)、Adv: 0 |
| API | 0(TTS/LLM呼出なし。raw_usage_log不変、本builderはローカル生成のみ) |
| モデル | 使用なし(25節該当なし) |
golden/AI島dry: evidence_runs/x2/40_*, 41_*。
