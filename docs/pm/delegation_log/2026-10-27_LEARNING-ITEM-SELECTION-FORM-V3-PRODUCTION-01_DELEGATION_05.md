## 管理ID

LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_05(ユーザー正式決定【全面修正版】2026-10-27 §4「従来方式など、理由が実際に存在しない候補は『AI理由なし』等を表示せず、理由欄を非表示にする。正式7＋5方式に移行後は、理由の欠落を正常状態として扱わない。」への追従。API 0・JPY0)。ユーザー原文=`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_USER.md`(並行Agentが保存中。未作成なら本委任文の引用で足りる)。並行Agent: GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01(read-only)、KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02B(Production Python)。これらのファイルは編集しない。あなたの所有=`user_test/selection_form_v3/**`、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{build_data_01.py,DATA_MODEL_02,VERIFY_05,TEST_05}.md`+test、`docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_05.md`(+check.json)、`docs/pm/RESULT_PACKET_FORM5.md`。Production Python編集禁止。SSOT編集権なし。pathspec付きcommit。

## 性質/禁止

- 性質: 正式採用済みフォーム(FIX)の承認済み表示規則の追従(UI仕様変更ではない)。到達上限=IMPLEMENTED+公開+自己検証。
- 禁止: 上限ロジック・文法枠・コメント等のUI仕様変更、理由のAI生成、禁止Git操作。
- 時間見込み: 約45分。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_05.md` をN=712から順に試し、先頭「## 管理ID」+「LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_05」のものを採用。

## 実施事項

1. `form_logic.js`/`index.html`: `reason_ja`が空の候補は理由欄(折りたたみ「AI理由・確認用」)自体を描画しない(「AI理由なし(仕様)」等の文言を撤去)。理由がある候補は従来どおり表示。送信payloadの`ai_reference`は理由がある候補のみ含める(空文字・「なし」文言を送らない)。
2. `export_form_data_01.py`: 候補docの`prompt_id`(P7/W5')または`kind`/`reason_source`からschema世代を判定し、7+5 doc(P7/W5')で`reason_ja`が欠落する候補があれば`data_warnings[]`に`reason_missing_in_p7w5`を記録(正常扱いしない、フォームの出所注記に警告表示)。旧Prompt 2 docは警告なし(理由欄非表示のみ)。
3. `DATA_MODEL_02.md`追補(理由欄の表示規則・警告)。test更新(node/py: 理由なし候補で理由DOMが存在しない/`ai_reference`から除外/7+5 docで欠落時に警告)。既存test(node 45+/py 15)維持、`data/legacy/`対象の旧「call1理由なし」検査は「理由欄非表示」検査へ置換。
4. 公開検証(`VERIFY_05.md`): HTTP 200、headless(公開URL)で理由ありは表示・理由なしは非表示、Console error 0。

## 事前指定Read一覧

- `user_test/selection_form_v3/{form_logic.js,index.html}`(Grep `reason|AI理由` ±10)、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`(Grep `reason|prompt_id|data_warnings` ±10)、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/DATA_MODEL_02.md`(Grep `reason` ±5)、`docs/research/KP-PHRASE7-WORD5-PRODUCTION-01/DESIGN_02.md`(Grep `reason_ja|prompt_id` ±5)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_05.md --json-out ...\_check.json`
- test: `.venv\Scripts\python.exe run_project_regression.py --pattern "form1_selection_form_v3_test_01.py"`+node test+headless
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_FORM5.md`にOPEN-545追記文案。

## Git

- commit message: `LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_05: 理由なし候補は理由欄非表示・7+5 docの理由欠落を警告(ユーザー決定§4、UI不変、API 0)`。trailer: `Delegation: LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/05`。push。

## 報告

`docs/pm/RESULT_PACKET_FORM5.md`: (0)T-0、(1)差分、(2)test・公開検証、(3)判断候補、(4)必須4行+「判定整合: 重大NG=<なし|あり>」、(5)SSOT文案、commit hash・raw URL。末尾5行要約。