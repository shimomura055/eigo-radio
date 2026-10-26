## 管理ID

PM-SSOT-SYNC-18(①git整合確認[並行Agentが禁止操作`git stash`/`stash pop`を実行したと自己申告。commit喪失・作業ツリー欠落の有無を検証]、②SSOT反映: OPEN-540限定解除=PRODUCTION_WIRED、OPEN-551 IMPLEMENTED+猿の手c10のユーザー判断起票、OPEN-549/552等の整理、日次費用。API 0・JPY0)。並行Agent: なし。所有=`OPEN_ITEMS.md`・`CURRENT_SPEC.md`・`DECISION_LOG.md`・`docs/pm/USER_DECISION_REGISTER_01.md`・`docs/pm/ACTIVE_TASK.md`・`docs/pm/PM_GOVERNANCE.md`(禁止Git操作の違反記録節への追記のみ。該当節をGrep `stash|禁止Git|Git運用` で特定。無ければOPEN_ITEMSの違反記録で代替)・`docs/research/PM-SSOT-SYNC-18/GIT_INTEGRITY_01.md`・`docs/pm/delegation_log/2026-10-27_PM-SSOT-SYNC-18_DELEGATION_01.md`(+check.json)・`docs/pm/RESULT_PACKET_SSOT18.md`。pathspec付きcommit。

## 性質/禁止

- 性質: 整合確認+SSOT同期。到達上限=SYNCED。
- 禁止: SSOT全文読込、コード編集、禁止Git操作(`git add -A/-u/-f/-N`・amend・rebase・force push・**stash**・clean・reset --hard・checkout -f・`git checkout -- <file>`)。
- 時間見込み: 約1h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_PM-SSOT-SYNC-18_DELEGATION_01.md` をN=698から順に試し、先頭「## 管理ID」+「PM-SSOT-SYNC-18」のものを採用。

## 事前指定Read/Grep一覧+手順

### ① git整合確認(`GIT_INTEGRITY_01.md`)
- `git stash list`(空であること)、`git status --porcelain`(未追跡・変更の一覧。RESULT_PACKET_*/ACTIVE_TASK/er0XX_output等の想定内を区別)、`git log --oneline -15`、`git branch -r --contains 5db9e40bc`・`88b1a5173`・`52c07550d`・`6e7fa7cf5`・`31423fdce`・`94fee9a44`(全てorigin/mainに含まれること)。
- 内容検証: `er127_tts_block_policy_01.py`に`log_fn`(委任_06)が存在、`er003_v1_n3_01_tts_generate.py`/`er003_v1_sing01_voice01_generate.py`に`register_ja_terminal_hr`呼出が存在、`er063_family_z_audio_01.py`に`z_style_actual_gate`が存在、`docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/EVIDENCE_JA_TERMINAL_02.md`存在。`git diff HEAD --stat`で意図しない差分(追跡ファイルの消失・巻き戻り)がないか。
- 結論: 喪失なし/あり(ありなら対象と復旧案を記載しSTOP)。

### ② SSOT反映(Fable判定)
- **OPEN-540**: 限定解除→**PRODUCTION_WIRED**(2026-10-27 Fable受入)。追記: 委任_04(6e7fa7cf5: JA終端登録追加・BlockProgress merge・er011コメント)、委任_05(5db9e40bc: 実経路JA_01でHRQ 2行=二重登録を検出、¥0.56)、委任_06(88b1a5173: `log_fn`化でJA queueへ・判定器と同一dedupe、JA_02でhrq_rows==1確認、¥0.585)。未観測(X STOP offline/Y chunk構造的不発火/Zセリフ終端Std)は追跡注記のまま。
- CURRENT_SPEC統一仕様節の「限定事項」を「解消(2026-10-27)」へ更新。
- **OPEN-551**: IMPLEMENTED(52c07550d: `z_style_actual_gate`・`Z_ROLE_COVERAGE`・fail-closed・過去run警告・fallback人間承認・`style_actual`記録・test 31件・正式経路mockで発火/PASS/BLOCK確認。Dialogueはleaf非公開のため意図sha+`measurement_gap`)。evidence要=次の新規Z run(実leaf)。**猿の手Std公開版c10**: fallback(PD06落ち)clipが公開mp3 128.6〜133.4秒(4.7秒/301.8秒)に含まれる事実→**ユーザー判断(D)**: 案A現状維持/案B当該clipのみ再生成(約¥1〜2)→再組立→公開更新(Fable推奨B)/案C聴取して人間承認。
- 新規OPEN候補の整理: Dialogue実測化(`er012`に`style_prefix`返却、X/Y/Z共有→修正へ進む、別委任)、Z新Gateの実run初回検証(追跡)、er119/er109既存test失敗7件(修正へ進む、OPEN-543へ統合)。
- **Git運用違反の記録**: FAMILY-Z-STYLE-ACTUAL-GATE-01 委任_01が`git stash`/`stash pop`を実行(自己申告、stash残0)。①の検証結果とともにOPEN_ITEMS(OPEN-543または新規「PM運用違反記録」)へ記録。再発防止=委任文の禁止事項に`stash`を明記済み(継続)。
- 費用: 2026-10-27 当日約¥1.15(TRU 0.56+0.585)。
- UDR: 新規「猿の手Std c10差替え(推奨B)」。ACTIVE_TASK更新。

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_PM-SSOT-SYNC-18_DELEGATION_01.md --json-out ...\_check.json`
- 上記git確認コマンド(出力は`--porcelain`/`--stat`/`--oneline`で最小化)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## Git

- commit message: `PM-SSOT-SYNC-18: git整合確認(stash事故)+OPEN-540 PRODUCTION_WIRED(限定解除)、OPEN-551 IMPLEMENTED+猿の手c10 UDR、違反記録(API 0)`。trailer: `Delegation: PM-SSOT-SYNC-18/01`。push。

## 報告

`docs/pm/RESULT_PACKET_SSOT18.md`: (0)T-0、(1)git整合の結論、(2)編集箇所、(3)必須4行+「判定整合: 重大NG=<なし|あり>」、(4)commit hash・raw URL。末尾5行要約。