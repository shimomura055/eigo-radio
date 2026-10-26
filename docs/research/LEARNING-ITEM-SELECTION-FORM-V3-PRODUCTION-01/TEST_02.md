# TEST_02(委任_02、2026-10-27)
| 種別 | 結果 |
|---|---|
| node `selection_form_logic_test_01.js` | ALL PASS 36(既存25維持[うちv1文字列配列前提の2 assertをv2 item配列へ更新]+新11: データschema/status規則/placeholder抑止/テキスト・JSONの全項目/AI理由分離/文法未生成の明示/全記事フル選択の欠落なし/URL長/コピーJSON) |
| `run_project_regression.py --pattern form1_selection_form_v3_test_01.py` | collected=11 passed=11(既存6維持+新5: gloss_status規則、reason_info規則、元kp_candidates.json/trial_result.jsonとの逐語一致[再生成なし]、フォームの外部通信なし[fetch2箇所のみ]、ページ表示元=japanese_glossの静的照合) |
| `er119_kp_backfill_test_01.py`(export tool影響確認) | collected=55 passed=55 |
| headless Chrome `browser_check_02.mjs`(ローカル) | pass=19 fail=0(`browser_check_02_local_output.txt`) |
| 既存UI仕様の維持 | `counts/allowed/setChoice/setGrammar`未改変。node fuzz20000の参照HTML等価性PASS。旧`browser_check_01.mjs`は記事枠数が前委任で変わった(10→16)ため旧件数assertは古い(本委任では`_02`で置換。UI上限挙動の旧check項目は`browser_check_01`のまま有効な箇所のみ参照) |
