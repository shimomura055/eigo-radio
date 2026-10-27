# FIX_DF1_01 (委任_07G) D-F1是正: public_study_htmlのPart 1をlevel+display_specで決める
- 不具合: `er120_part2_wiring_01.public_study_html`がPart 1を`level=="b1b"`限定で生成。X標準公開builder(er019_family_x_listening_page_01.py:143-148)はdisplay_spec付きStdでPart 1ちょうど1個を要求→X_PART1_BLOCK_COUNT(a2 page)でSTOP。承認済み仕様(USER_04 §2 Std②=①と同等の日本語詳細解説、Std Part 1=①+②)との矛盾=11-8の不具合。
- 修正(er120_part2_wiring_01.py): 新`_part1_enabled(audio_dir, level)` = `level=="b1b" or bool(_cc().display_spec_of(audio_dir, level))`(flag非経由・書込なし。X runner `part1_enabled`と同一規則)。分岐を`_part1_enabled`へ、`load_verified_items(..., level=level, which="part1")`、`p1.study_html_for_audio_dir(audio_dir, items=items, level=level)`。display_spec無しのa2=Part 1なし(従来)、b1b=従来どおり(b1bのlevel引数は既定と同値)。
- Validator/Gate無変更(G1=load_verified_items/require_final_consistent、Part 2確定=require_final、builderのX_PART1_BLOCK_COUNT・G3・check_page・verify_outputsはそのまま)。
- 他consumer: public_study_htmlの呼出元はer019_family_x_listening_page_01.build_pageのみ(Grep)。Y/Zは`compose_page_html`直(別経路)で本関数を通らない=コード上バイト同一。
- test: er120_public_study_html_level_test_01.py(3件: display_spec付きa2=Part 1ちょうど1個・Part 2より先 / 無しa2=0個 / b1b=display_specに依らず不変)。
- golden: evidence_runs/x2/41_golden_all_x_runs.txt。X全99 run: b1b 99/99 同一(旧HEAD実装 vs 新)、a2 97/99同一、差分2件=display_spec付き(AI島run_form_prod_01、s23f)のみ(意図した変更)。
- 旧規則残存Grep: `grep -n 'level == "b1b"' er120_part2_wiring_01.py` → 当該Part 1分岐は撤去(`_part1_enabled`内の`level == "b1b"`のみ)。
