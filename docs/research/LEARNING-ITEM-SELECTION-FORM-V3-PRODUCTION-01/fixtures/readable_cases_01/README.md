# readable_cases_01 人間可読コピー契約fixture(委任_07R作成・委任_07と共有、2026-10-27)

`COPY_FORMAT_01.md` の契約を固定する共有fixture。フォームJS(委任_07)は `buildReadable` の出力がここの `cases/<name>.readable.txt` と**バイト一致**することを、
Python側(`er128_form_readable_restore_01.py`)は復元結果が `cases/<name>.expected_structured.json`(既存 `FormLogic.buildStructured` の出力)と一致することを検査する。

- `data/`: 公開データJSONのスナップショット(実データ6件+合成3件)。`manifest.json` の `data.<stem>` が `d6`(JSONバイト列のsha256先頭6桁。**CRLFはLFへ正規化してから計算**。JSは公開Pages=LFのバイト列から計算)。
- `cases/<name>.state.json`: `{"stem", "state": {choices:{term:cat}, grammar:{id:bool}, grammar_zero:bool, comment}}`(form_logic.jsの状態と同形)。
- `cases/<name>.readable.txt`: 期待する人間可読コピー(LF、末尾改行なし、PREFACEなし)。末尾の照合コード行を含む。
- `cases/<name>.expected_structured.json`: 同じ入力に対する `buildStructured` の `article/selection/comment/grammar_status/grammar_decision/kp_confirmed`。
- `manifest.json`: 全ケースの `d6`・`readable_sha256`・照合コード。
- `node_structured_batch.js`: expected生成用(`node node_structured_batch.js <form_logic.js> <jobs.json>`)。
- 再生成: `.venv\Scripts\python.exe er128_form_readable_restore_test_01.py --regen-fixtures`(データ更新時。再生成後は委任_07側のJSも再検証すること)。

契約の注意: 自由コメントは前後をtrimした値が `m8`/本文の対象(先頭末尾の空白は保持されない)。コメントが文字列「なし」だけの場合は区別できないため復元側が拒否する。
Windowsのautocrlfで作業ツリーのfixtureがCRLFになる場合があるため、比較は**CRLFをLFへ正規化してから**行う(契約はLF)。
