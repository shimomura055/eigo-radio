## 管理ID

LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_07(ユーザー正式決定USER_03 §B(APPROVED_FOR_PRODUCTION)のフォーム側実装。設計=委任_06(commit b8917f366): `HANDOFF_DESIGN_01.md`/`COPY_FORMAT_01.md`/`TEST_PLAN_06.md`。Fable採否: 推奨(b)+(c)採用、PREFACE簡素化(ChatGPTに原文を逐語でコードブロック返却させる。「Claude Code向け指示案を作成」は外す)採用、「技術情報付きでコピー」は`<details>`内に補助として残置(既定非表示)採用、Opus不要。API 0・JPY0)。並行Agent: (a)LEARNING-ITEM 委任_07R(復元tool `er128_form_readable_restore_01.py`+CLI=**Python側。`COPY_FORMAT_01.md`の契約のみで並列実装**)、(b)GPG 05B、(c)YSP 08、(d)AI-ISLAND 委任_03、(e)SLOT-23設計。あなたの所有=`user_test/selection_form_v3/**`(`form_logic.js`/`index.html`/data再生成は不要)、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{selection_form_logic_test_01.js,browser_check_07.mjs,SEND_CHECK_04,VERIFY_07,TEST_07,DATA_MODEL_03}.md`、`form1_selection_form_v3_test_01.py`(フォーム側test)、`docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_07.md`(+check.json)、`docs/pm/RESULT_PACKET_FORM7.md`(gitignore、`-f`禁止)。Production Python編集禁止。SSOT編集権なし。pathspec付きcommit(他Agentのstage分を巻き込まない)。

## 性質/禁止

- 性質: 承認済み改善のフォーム実装。到達上限=IMPLEMENTED+公開+自己検証(ChatGPT実操作はユーザー確認項目)。
- 禁止: UI上限ロジック(①3/①+②5/①+②+③12・文法1件/0件)の変更、照合情報(candidate_id/候補集合sha/本文sha)の消失、直接送信を装う不完全実装、JSON手編集の要求、ブラウザ保存データのみ参照、禁止Git操作(`add -f`/`pull --rebase`/pathspecなしcommit)。
- 時間見込み: 約2h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行(jsonl index=実呼出順。NOT_FOUNDなら待って再試行)。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_07.md` をN=732から順に試し、先頭「## 管理ID」+「LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_07」のものを採用(同時刻に委任_07Rあり)。

## 実施事項

1. **コピー本文**: `COPY_FORMAT_01.md` §2の人間可読形式(記事：<名>｜<レベル>、①②③ごとに「- 英語：訳」、文法：<名>+【解説全文】…【解説ここまで】または「選定なし」、自由コメント、末尾1行「照合コード(変更しないでください)：AIF1-<stem>-<d6>-<c8>-<t8>-<s10>-<g10>-<m8>-<k4>」)。照合コードの算出は`RESTORE_TOOL_SPEC_01.md`の定義と**バイト一致**(nodeとPythonで同一入力→同一コードのtestを、委任_07Rの`proto06_copy_restore_01.py`既存試作に対して先に通す)。確定済み記事(KPロック)も同形式。
2. **送信ボタン**: 「ChatGPTへ送信」=常にクリップボードへコピー+URL(`?q=`)が閾値内なら新タブでChatGPTを開く、閾値超なら`chatgpt.com`を開き「貼り付けてください」を正常案内(エラー表示にしない)。「選定結果をコピー」=コピーのみ。コピー成功の明確な表示、短い操作説明、失敗時も選定状態保持。PREFACE=「以下を一字一句変えずにコードブロックで返してください」型に簡素化。
3. **技術情報**: 既定非表示の`<details>`「技術情報付きでコピー」(従来JSON同梱)を補助として残す。
4. **test**: node(照合コードのバイト一致・各形式・改変検出用の固定fixture、長文解説でも欠落なし、0件/1件文法、ロック記事)、py、headless(公開URL: ボタン動作、コピー内容、URL長分岐、Console error 0)。`SEND_CHECK_04.md`(11データ×主要ケースの文字数と分岐結果)、`SEND_CHECK_01〜03`のJSON同梱記述を旧仕様と明示。`DATA_MODEL_03.md`に送信形式v3(人間可読+照合コード)を追補。
5. 公開・検証(`VERIFY_07.md`)、ユーザー実操作確認項目(`?q=`実上限・clipboard実機・ChatGPT逐語返却)を明記。

## 事前指定Read一覧

- `docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/{HANDOFF_DESIGN_01,COPY_FORMAT_01,RESTORE_TOOL_SPEC_01,TEST_PLAN_06,DATA_MODEL_02}.md`、`proto06_copy_restore_01.py`/`proto06_node_structured.js`/`proto06_output_01.txt`
- `user_test/selection_form_v3/{form_logic.js,index.html}`(origin/main最新=AI-ISLAND委任_02後: Grep `buildText|buildCopyText|buildChatGptUrl|buildStructured|PREFACE|6000|copy|clipboard|kp_confirmed` ±10)

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_DELEGATION_07.md --json-out ...\_check.json`
- test: node test+`.venv\Scripts\python.exe run_project_regression.py --pattern "form1_selection_form_v3_test_01.py"`+headless(公開URL)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

編集権なし。`RESULT_PACKET_FORM7.md`にOPEN-545更新文案(送信・コピー改善IMPLEMENTED+公開、ユーザー実操作確認項目)。

## Git

- commit message: `LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_07: 選定結果コピーを人間可読形式+照合コード1行へ、送信は常時コピー+URL閾値内でChatGPT起動(JSONは技術情報detailsへ分離、UI上限不変、API 0)`。trailer: `Delegation: LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/07`。push(`git push origin HEAD:main`)。

## 報告

`docs/pm/RESULT_PACKET_FORM7.md`: (0)T-0、(1)差分、(2)コピー実例(AI島Std/Adv)、(3)test・公開検証・SEND_CHECK_04、(4)ユーザー実操作確認項目、(5)判断候補、(6)必須4行+「判定整合: 重大NG=<なし|あり>」、(7)SSOT文案、commit hash・公開URL・raw URL。末尾5行要約。