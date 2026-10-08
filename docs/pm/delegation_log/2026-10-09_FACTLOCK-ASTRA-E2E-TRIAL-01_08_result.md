# 委任_08 結果(FACTLOCK-ASTRA-E2E-TRIAL-01、2026-10-09、Status=PROMPTS_READY)
## 1 成果物
ベース: er052_output/factlock_astra_e2e_trial_01/annotation/ — prompts/(20ファイル)、PROMPT_SHA256.json、AMBIGUOUS_FACT_MAP.json、FORBIDDEN_PATHS.md、audit_config.json、audit_strict_01.py(+_test.py)、build_prompts_01.py、RUN_ANNOTATION.md。ほかに PREREGISTRATION_01.md(v2.2、5-12追加)、docs/pm/REPORT_LEDGER.md 1行、本記録。
commit hash・raw URL: 末尾「commit」節。
## 2 テーマ別(プロンプトはA/B同一行数。「brief事実数」=B3が選択した台帳ID数。注記前なので【事実N】数は未確定)
| slug | プロンプト行数 | 台帳記録数 | brief選択ID数 | 選択されたAMBIGUOUS記録 |
|---|---|---|---|---|
| byd_recall | 281 | 11 | 5 | - |
| central_bank_mortgage | 290 | 11 | 6 | - |
| hormuz | 300 | 12 | 3 | - |
| inbound_tourism | 316 | 13 | 4 | F06 |
| meta | 307 | 15 | 3 | - |
| openai_copyright | 266 | 8 | 5 | - |
| semiconductor_earnings | 250 | 6 | 5 | F1 |
| small_bag | 254 | 6 | 3 | - |
| space_weapons | 368 | 22 | 5 | - |
| streaming_price | 258 | 7 | 6 | F01,F07 |
## 3 A/B同一性
全10テーマでA/Bは「注記者名(2箇所)と出力先パス(1箇所)」以外が逐語一致(正規化後一致=True、10/10。PROMPT_SHA256.json の ab_all_identical=true)。20ファイルとも 仕様v2・brief・台帳が逐語で含まれ(バイト一致検査OK)、未置換欄0。仕様sha256=8d145c3d...(固定値と一致)。事実選定本文(selected_fact_brief_text)は全テーマでmdの部分(見出し・ラベルの差のみ)だったため付記なし(0/10)。
## 4 注記者起動の固定文言(<slug>は10テーマ分を差し替え)
A用:
```
あなたは注記者Aです。次の1ファイルを、Readツールで1回だけ読み、その中の指示だけに従って、返答の本文だけで答えてください。
ファイル: C:\Users\tensh\eigo-radio\er052_output\factlock_astra_e2e_trial_01\annotation\prompts\<slug>__A.md
このファイル以外のファイルを読まない。Grep/Glob/Bash/Web/他のツールを使わない。ファイルを作らない。説明文を付けない。
```
B用:
```
あなたは注記者Bです。次の1ファイルを、Readツールで1回だけ読み、その中の指示だけに従って、返答の本文だけで答えてください。
ファイル: C:\Users\tensh\eigo-radio\er052_output\factlock_astra_e2e_trial_01\annotation\prompts\<slug>__B.md
このファイル以外のファイルを読まない。Grep/Glob/Bash/Web/他のツールを使わない。ファイルを作らない。説明文を付けない。
```
A・Bは別subagent、各subagentにはこれ以外を渡さない。保存・取り出し・check・merge・監査のコマンドはRUN_ANNOTATION.md。
## 5 未確認・Fable判断要
1. テンプレート(逐語)は「ファイルを読む等の道具を使うな」と書いてあるため、プロンプト冒頭に「この1ファイルの1回のReadだけが例外」という前置きを追加した(テンプレ・仕様の文言は不変、前置きと末尾の運用明確化[(a)(b)逐語]・返答受取の2行を追加)。この前置きの追加を承認するか判断要。
2. 「JSON用注記版テキスト」「サイドカーをannotation.jsonとして注記者が出力」は、仕様v2の出力形式(注記版md+サイドカーを本文で返す、ファイルは作らない)と矛盾するため、注記者には作らせず呼び出し側が reply.md から extract して annotated.md/annotation.json を作る方式にした。fact_selection_evidence.jsonの注記版JSON(check の --json)は注記者出力に含まれない(省略可の引数、必要なら別途機械生成を別委任)。
3. 「1注記者が10テーマを順に」は、仕様の出力形式が1テーマ1返答で区切り規則が無いため、推奨を1テーマ=1 subagent呼び出し(A10+B10、独立・並列可、テーマ間持ち越し無し)とした。連続処理を選ぶなら区切り規則が要る。
4. ambiguous_fact:true のサイドカー付与は、統合スクリプト非編集のため行わず、AMBIGUOUS_FACT_MAP.json の突合表で評価時に代替する案とした。付与が必須なら別委任。
5. AMBIGUOUS記録がB3に選択されたのは、指示のstreaming(F01,F07)・semiconductor(F1)に加え inbound_tourism F06 もある(F04は未選択)。v2.2の5-12にinboundも列挙した。
6. 監査スクリプトの穴: 既存 b3_annotator_audit_01.py は(a)解釈できないtranscript行を黙って捨てる、(b)禁止語に当たらない許可外パスのReadをNOTEにとどめる。このため audit_strict_01.py(許可Read以外・解釈不能行を違反とする、自己テスト5/5 ALL_PASS)を追加した(既存は非編集)。transcriptの取得方法は実行時にFableが確認要。
7. 運用明確化(a)(b)の「該当テーマ名の列挙」を逐語のまま全プロンプトに入れたため、注記者は他テーマ名(byd_recall等)を目にする。内容は仕様の適用方法のみで結果情報は含まない。
## 6 所要時間・API支出
約25分。API支出 ¥0(API呼び出し・注記実施なし)。既存コード・SSOT本体・委任_05のファイルは未編集。
