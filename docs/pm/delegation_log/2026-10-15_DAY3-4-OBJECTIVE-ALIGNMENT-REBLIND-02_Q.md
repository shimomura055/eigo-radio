# 委任_Q: OAR-02 Phase B実行 — 規則同期→7項目事前確認→再盲検1ラウンド起動(欠陥2+陰性1)→収集(採点はしない)

管理ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / DAY3-4-OBJECTIVE-ALIGNMENT-REBLIND-02。ユーザー承認: 再盲検は1ラウンドのみ(欠陥1〜2+陰性1)、定価換算USD 5〜10程度、Day5〜6開始禁止。あなたは「起動・収集役」。採点(Opus)・独立照合(Fable)は別役。`_scorer_only/`配下(EXPECTED_c1〜c3.md・SELECTION_LOG.md)は開かない(sha再作成でpathを扱うのは可、本文は読まない)。

作業場所: Repo外 C:\Users\tensh\eigo-radio-replay\oar2\。Repo書込は(a)C:\Users\tensh\eigo-radio-crbn(main worktree)への記録ファイル追加・commitと(b)C:\Users\tensh\eigo-radio\docs\pm\ACTIVE_TASK.mdのROLLOUT行のみ。C:\Users\tensh\eigo-radioは別案件がbranch作業中で、git操作禁止(delegation_log保存ファイルはcrbn側へコピーしてcommit)。git add -A/-f/stash/reset --hard/checkout -f/clean/rebase/amend/force push禁止。

## T-0
本委任文全文を crbn docs\pm\delegation_log\2026-10-15_DAY3-4-OBJECTIVE-ALIGNMENT-REBLIND-02_Q.md に保存、check_delegation_prompt.py→_check.json(FAILでも継続)。eigo-radio側の_P.mdと_P_check.jsonをcrbn側同pathへコピー。stop_scope_check rc=0確認(--run-dirはday3)。crbnでgit pull --ff-only origin main(HEADがf012b9330以降)。

## 事前指定参照
OAR2_PHASE_A_APPLIED_01.md(同期元6ファイルとsha256。正本)/ oar2\SYNC_RULES.sh, RULES_SYNC_STATUS.json, RUN_OAR2.ps1, PRECHECK_01.md, _runbook\ / 前回手順 BLIND_REPLAY_RUNBOOK_01.md, REBLIND_RUN_LOG_01.md / 前回決定①(7項目事前確認): claude -p起動可否/モデル・ルーティング/課金経路/ツール権限・委任/独立性/漏洩なし/Repo・秘密情報不可

## やること
1. 規則同期: SYNC_RULES.shのFILES/DIRSがOAR2_PHASE_A_APPLIED_01.mdの同期元を網羅しているか突合、不足は追加して実行。同期後、規則ファイルsha256が正本shaと一致(6ファイル×3パッケージの表)。neutralize.sedで文意が変わっていない(是正A/B文言 :75–91 が原形)ことをGrepで確認。
2. deny拡張: subject_settings_c?.jsonのdenyに eigo-radio-crbn/**、eigo-radio/**、_scorer_only/**、oar2\_runs/**、_runbook/**、rubric/**、_runs/**、_feasibility/**、day3/**、synthetic/**、defect_case*/**、negative_control/**、~\.claude\projects/** を確認・追加。パッケージ内にday3/・REBLIND_*・BLIND_REPLAY_*・OAR2_*・REPLAY_*が複製されていないことをGlob確認(あれば削除し記録)。
3. 漏洩Grep再実行(同期後): EXPECTED/正解/欠陥位置/採点/RUBRIC/v3/REBLIND/DEFECT_R/NEG_1/KGCPW/a337d8acc/c21cce27a/OAR2/OBJECTIVE-ALIGNMENT。0件または無関係と確認できるもののみ(ファイル:行と理由)。RULES_SYNC_STATUS.jsonをSYNCEDに。mk_sha.shで木shaを再作成し記録。
4. 7項目事前確認: RUN_OAR2.ps1 -CheckOnlyで3件とも「隔離確認OK・警告0」。PRECHECK_01.mdの「委任_Q結果」欄に7項目の観測値を記入。1項目でもNGなら起動せずSTOP報告。
5. 起動(1ラウンドのみ): claude -p --agent sandwich-pm --settings <subject_settings_c?.json> --permission-mode default --allowedTools Read Grep Glob Agent --output-format stream-json --verbose --max-budget-usd 3.5、cwd=各パッケージ、prompt=TASK_c?.md。出力先oar2\_runs\OAR2_c1|c2|c3\(stdout.stream.jsonl・meta.json)。3件並列可。rc≠0・途中打切り・max_budget到達はその件の再起動1回まで(理由記録、それでもダメなら欠番として報告。ラウンドを増やさない)。被験の出力に手を入れない。
6. 収集: ~\.claude\projects\<cwd slug>\<session_id>.jsonlとsubagents\を_runs\OAR2_c?\へコピー、SESSION_SUMMARY.md(最終assistant本文の逐語抽出+受入記録5項目の所在行+委任/subagent呼出一覧+費用usd/所要時間/rc/stop理由+3パッケージ木shaの起動前後比較で書込0確認)。採点・合否判断は書かない(「受入記録(1)に原文引用あり/なし」の機械抽出のみ可)。
7. 記録: crbn day3\OAR2_RUN_LOG_01.md に同期結果表/deny/漏洩Grep/7項目/起動コマンド・rc・時間・定価換算USD(実請求なし=OAuth subscription利用枠消費と区別)/再起動の有無/書込0確認/各runのpath。crbnで明示add→secret_scan --staged hits=0→commit(message: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 DAY3-4-OBJECTIVE-ALIGNMENT-REBLIND-02 委任_Q: 規則同期+7項目事前確認+再盲検1ラウンド(欠陥2・陰性1)起動・収集(採点未実施)。実請求なし、定価換算USD <x>)→push main。ACTIVE_TASK.md ROLLOUT行を「Phase B実施済み・採点待ち」に更新。

## 禁止
2ラウンド目・追加ケース・再試行1回超、_scorer_only本文の閲覧、被験出力の編集、採点・合否記述、Day5〜6着手、本体Repoのgit操作、SSOT(DECISION_LOG/OPEN_ITEMS/CURRENT_SPEC/REGISTER)編集(委任_Rで行う)。

## 報告様式(受入記録5項目)
(1)当初目的=ユーザー原文§4「未使用事例による再盲検」・§6費用・§7 STOP条件の該当部を逐語(delegation_log\..._USER.md引用、ファイル:行) (2)実際の成果物(3 run path・SESSION_SUMMARY・RUN_LOG・commit) (3)証拠(sha表・deny・漏洩Grep・7項目観測値・rc・USD・書込0) (4)一致/不一致(1ラウンド/件数/独立性/予算USD 10目安/書込0/STOP条件該当有無) (5)判定(「起動・収集完了」か「STOP」かのみ。合否は書かない)。加えて各SESSION_SUMMARYの行番号付き所在(受入記録(1)〜(5)の開始行、最終判定行)をFable照合用に列挙(本文の評価はしない)。

(注: 本ファイルは委任文の保存版。表記は一部記号を簡略化)
