## 管理ID

LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_03(Opus条件Aレビュー(KP-CONFIRMED-CONTENT-PROTECTION-01)で指摘されたフォーム側の契約不足の是正: 送信payload schema v2へ`candidate_id`・`kind`(phrase/word)・`candidates_sha256`を追加。canonicalization後は同じ`term`が複数候補にあり得るため、termでの対応付けは曖昧。API 0・JPY0)。並行Agent: (a)KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02A(`er128_kp_confirmed_content_01.py`新設・`er119_kp_human_review_01.py`等。あなたの`DATA_MODEL_02.md`更新を待って`candidate_id`照合を実装する=**最優先で`DATA_MODEL_02.md`を更新・commitし、その後に残作業**)、(b)KP-PHRASE7-WORD5-PRODUCTION-01 委任_01(read-only)。あなたの所有=`user_test/selection_form_v3/**`、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{build_data_01.py,DATA_MODEL_02,SEND_CHECK_03,TEST_03,VERIFY_03}.md`+test、`docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_03.md`(+check.json)、`docs/pm/RESULT_PACKET_FORM3.md`。Production Python経路編集禁止。SSOT編集権なし。pathspec付きcommit。

## 性質/禁止

- 性質: 承認済みフォーム仕様の送信データ契約の補強(UI不変、API 0)。到達上限=IMPLEMENTED+公開+自己検証。
- 禁止: UI仕様変更、日本語訳・理由のAI再生成、`ja_gloss_status`の意味変更、禁止Git操作。
- 時間見込み: 約1h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_03.md` をN=702から順に試し、先頭「## 管理ID」+「LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_03」のものを採用(同時刻にKCP 委任_02Aあり)。

## 実施事項

1. **`DATA_MODEL_02.md`更新(最優先・先行commit)**: データJSON(`data/<slug>__<level>.json`)の各候補に`candidate_id`(候補docの`candidate_id`逐語)・`kind`(`phrase`|`word`、候補docの`kind`。無い場合は`word_count==1`→word、それ以外phrase、`kind_source`を記録)、記事×レベル単位に`candidates_sha256`(候補docの自己sha。`kp_candidates.json`の該当フィールド名を`er119_kp_human_review_01.py` Grep `candidates_sha256` で確認)と`source_kp_candidates_path`を追加。送信payload v2(JSON・人間可読テキストの両方)の各選定項目に`candidate_id`・`kind`、記事×レベルに`candidates_sha256`を含める。`ja_gloss_status`は従来どおり(official以外の訳を確定した場合、受け側(er128)がISSUEとして扱う旨を注記)。schema_versionは`2`のまま(additive)とし`schema_minor`等で区別。commit message: `LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_03a: DATA_MODEL_02 v2契約にcandidate_id/kind/candidates_sha256を追加(文書先行)`。push。
2. `export_form_data_01.py`/`build_data_01.py`拡張→データJSON 7件再生成(Trial-02由来・replay由来は`candidates_sha256`が取れない場合`null`+`sha_source`注記、捏造しない)。`form_logic.js`の送信組立に追加(表示UIは不変)。
3. test: node(payload v2の項目有無・candidate_id一意性)、Python(データJSONの`candidate_id`が元docと逐語一致、`candidates_sha256`一致)、既存36+11件維持。headless実DOMで送信テキストに`candidate_id`/`kind`が出ることを確認。
4. 公開・検証(`VERIFY_03.md`): push後HTTP 200、Console error 0、URL長への影響(`candidate_id`分の増加量)を`SEND_CHECK_03.md`に記録。

## 事前指定Read一覧

- `docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{DATA_MODEL_02,SEND_CHECK_02}.md`、`user_test/selection_form_v3/{form_logic.js,data/articles.json}`、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/{tools/export_form_data_01.py,DATA_CONTRACT_01.md}`
- `er119_kp_human_review_01.py`: Grep `candidates_sha256|candidate_id|kind` ±5; `er119_kp_candidates_01.py`: Grep `candidate_id|"kind"` ±5

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_03.md --json-out ...\_check.json`
- test: `.venv\Scripts\python.exe run_project_regression.py --pattern "form1_selection_form_v3_test_01.py"`+node test
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_FORM3.md`にOPEN-545追記文案。

## Git

- 本体commit message: `LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_03: 送信payload v2にcandidate_id/kind/candidates_sha256を追加(確定内容保護との契約、UI不変、API 0)`。trailer: `Delegation: LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/03`。push。

## 報告

`docs/pm/RESULT_PACKET_FORM3.md`: (0)T-0、(1)契約差分、(2)実装差分、(3)test・公開検証、(4)判断候補、(5)必須4行+「判定整合: 重大NG=<なし|あり>」、(6)SSOT文案、commit hash・raw URL。末尾5行要約。