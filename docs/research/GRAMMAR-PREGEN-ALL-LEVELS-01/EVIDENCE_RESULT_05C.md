# EVIDENCE_RESULT_05C Y経路 evidence再開(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05C)
run: `er121_output/family_y_production_01/redelivery_fee/run_gpg5_y_01`(DEV run。Production不変)。証跡: `evidence_runs/y/20_*〜25_*`。

## 起動記録
- 事前: `stop_scope_check_01.py` rc=3(原因は当runの`STOP`+`RESTART_STORM_LOCK.json`のみ)。他python runner稼働なし(tasklist 1件=当方以外の待機のみ)。
- STOP解除1回(12:35:35、`--clear-stop --reason "...(Fable authorization: GPG委任_05C)"`)。STOP/LOCKの2ファイルのみ削除、STOP_ALLなし。
- 起動1回(12:35:36〜、rc=0、`20_launch05C.txt`): `--stages kp,assemble,pages,page_verify --regenerate-stage part2_b1b --approved-budget-jpy 10 --tts-execution-mode STANDARD`(委任_05と同一theme/reuse引数)。追加起動なし。
- `--regenerate-stage part2_b1b`の根拠: part2_b1b来歴entryは旧(2026-10-25 input_sha)、part2_a2はentry無し(自動finalize)。runnerは確定済み文法に対し**再抽出しない**(`er121_family_y_runner_01.py:870付近` cand_input_shaを据え置き、`_part2_final_step`は「確定済みreviewからfinalize(LLM 0・再抽出なし)」)。regenerate拒否は`CONFIRMED_CONTENT_LOCKED`時のみ(同:899)。`tts_a2/tts_b1b` provenanceはdownstream_stale=[]でfresh、Part 2はTTSの親でない(DEPENDENTS leaf、同:46-50)。実際、TTS行0・確定selectionはbyte同一。

## 結果(Y Std=a2 / Adv=b1b)
| 項目 | Y Std(a2) | Y Adv(b1b) |
|---|---|---|
| 確定内容 | Top1 g31f4b39e68 | **Top2 g938cd4b23a(非Top1。提示rank2、`03_presented_b1b.json`)** |
| 確定の不変(`11_confirmed_selection_*` vs 実行後`24_confirmed_selection_*_after`) | cmp同一 | cmp同一 |
| (v) finalize LLM 0 | cost_log 7行->10行、増加3行は全て stage=`kp`(final_redundancy_qa: KP/Vocabの既存冗長性QA、`key_phrases/*/final_redundancy_qa`)。`part2_*`行の増加0(`21_cost_log_after_05C.jsonl`) | 同左 |
| frozen | `24_confirmed_grammar_frozen_a2.json`(schema frozen_v2、cf_b229605ff74957d9) | `24_..._b1b.json`(cf_d845bc512f3de806) |
| part2_result | status SELECTED(human_pick) | SELECTED(human_pick) |
| (vi) ページ | page_verify `part2_verified` a2: standard part2_blocks=1 | b1b: advanced part1_blocks=1 / part2_blocks=1、本文`First to speak is a delivery...`がAdv節に出現。`verify_outputs(level, html_text=節)`はpage_verify内で実行されviolations=[] ok=true(`25_page_verify_local.json`) |
| KCP G1 | PASS(`23_g1_after.txt`) | PASS |
| KCP G2/G3 | page_verify `kp_selection_verified` ok=true/legacy=false(verify_selection_matches_outputs内でG2/G3呼出、er128:750-835) | 同左(signature 744be4a3...) |
| (viii) 凍結後model名変更 | PASS(Part2Staleにならない、result不変。`22_frozen_model_change_a2.txt`、API 0) | PASS(`22_..._b1b.txt`) |
| 非Top1採用のページ到達 | - | **到達(Top2 g938cd4b23a)** |
注: `tools/gpg5_frozen_model_change_01.py`にY branch(read-only・API 0)を追加。assembleはwavを既存narrationから再結合しただけ(TTS API行0)。
未観測: 2件拒否のページ後再確認は不要(05で取得済み)。フォームUI(Playwright)は別委任。
