## 管理ID

LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_04(KP 7+5 Production配線(commit 967109760、`KP_CANDIDATE_MAX`8→12・kind別cap 7/5)に伴うフォーム側引継ぎ: `export_form_data_01.py`の`shortfall_detail.cap`既定8→12(可能なら候補docの`N`/cap_by_kindから読む)、docstring(call1理由なし記述)の更新、cap_by_kind(7/5)の表示、6経路evidence doc(`run_kp75_ev_01`)からの実データ追加。API 0・JPY0)。並行Agent: PM-SSOT-SYNC-19(SSOT)、KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02B(コード)。これらのファイルは編集しない。所有=`user_test/selection_form_v3/**`、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{build_data_01.py,DATA_MODEL_02,VERIFY_04,TEST_04}.md`+test、`docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_04.md`(+check.json)、`docs/pm/RESULT_PACKET_FORM4.md`。Production Python編集禁止。SSOT編集権なし。pathspec付きcommit。

## 性質/禁止

- 性質: 承認済みフォーム仕様のデータ側追従(UI不変)。到達上限=IMPLEMENTED+公開+自己検証。
- 禁止: UI仕様変更(①≤3/①+②≤5/①+②+③≤12・文法独立2・コメント)、日本語訳・理由のAI再生成、公開済み/進行中Production runの改変、禁止Git操作。
- 時間見込み: 約1h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_04.md` をN=709から順に試し、先頭「## 管理ID」+「LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_04」のものを採用(同時刻にPM-SSOT-SYNC-19あり)。

## 実施事項

1. `export_form_data_01.py`: `shortfall_detail.cap`既定8→12(候補docに`N`/cap情報があればそれを正とし、無い旧docは12)。cap_by_kind(phrase 7/word 5)を出力。docstring(:90付近「call1は理由なし」)を「P7/W5'(2026-10-27配線)では全候補に`reason_ja`、旧Prompt 2 docでは空」に更新。`kind`は候補docの値逐語(7+5 docは`kind`必須)。
2. 7+5 evidence doc 8件(`er019_output/family_x_audio_production_wiring_01/{uk_train_speaker_playback,ai_island_temple}__run_kp75_ev_01`、`er121_output/family_y_production_01/redelivery_fee/run_kp75_ev_01`、`er026_output/family_z_production_e2e_01/melos/run_kp75_ev_01`の各a2/b1b `kp_candidates.json`)をフォームデータへ追加(記事枠は既存9枠の範囲で、旧3+5 docの同一記事×レベルは7+5版へ差し替え、旧版は`data/legacy/`へ退避。9枠を超える場合は7+5版を優先し、退避したものをDATA_MODEL_02に記録)。`ja_gloss_status`は正式経路doc=official。AI理由はP7/W5'の`reason_ja`を逐語。
3. フォームの表示でkind別上限(フレーズ7/単語5)と候補数12を正しく扱うこと(UI上限ロジックは不変、候補一覧が12件でも崩れないことをheadlessで確認)。
4. test(node既存41+/py既存12+、新規: cap 12・kind別cap・7+5 docの`reason_ja`逐語一致)、公開検証(`VERIFY_04.md`: HTTP 200、実DOM、Console error 0)。

## 事前指定Read一覧

- `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`(全体)、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{DATA_MODEL_02,build_data_01.py}`、`docs/research/KP-PHRASE7-WORD5-PRODUCTION-01/{EVIDENCE_01,DESIGN_02}.md`(候補doc schemaの`kind`/`N`/cap記述)、`er119_kp_candidates_01.py` Grep `_shortfall_detail|cap_by_kind|"N"` ±10

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_04.md --json-out ...\_check.json`
- test: `.venv\Scripts\python.exe run_project_regression.py --pattern "form1_selection_form_v3_test_01.py"`+node test+headless
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_FORM4.md`にOPEN-545追記文案。

## Git

- commit message: `LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_04: 7+5配線に追従(export cap 12・kind別cap 7/5・reason_ja)+6経路evidence docをフォームデータへ追加(UI不変、API 0)`。trailer: `Delegation: LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/04`。push。

## 報告

`docs/pm/RESULT_PACKET_FORM4.md`: (0)T-0、(1)差分、(2)データ差し替え一覧、(3)test・公開検証、(4)判断候補、(5)必須4行+「判定整合: 重大NG=<なし|あり>」、(6)SSOT文案、commit hash・raw URL。末尾5行要約。