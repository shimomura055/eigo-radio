FABLE-DELEGATION-MARKER: JOINT-RUNTIME-EVIDENCE-RUN-委任_02-20261022

管理ID: JOINT-RUNTIME-EVIDENCE-01 委任_02(OPEN-455。対象=OPEN-450 PNAP / OPEN-451 KP3V / OPEN-454 KPFT)。目的: **本日2026-10-22 JST中に**、Family X 1 run + Family Z 1 runの正式Production経路で、3件の配線のruntime発火証拠を同時取得し、タスク別・Family別の確認結果をFableへ渡す。ユーザーは本日の開発費上限を1,500円へ引き上げ(累計。現在の支出≈900円、出典`docs/pm/REPORT_LEDGER.md`の予算例外行とRESULT_PACKET_BUD1)、「日付分割せず本日完成を最優先、品質・Gate・承認境界は緩めない」と指示済み(原文`docs/pm/delegation_log/2026-10-22_PM-BUDGET-EXCEPTION-20261022-01_USER.md`を最初に読む)。本委任の費用上限=**150円**(X≤60、Z≤40、失敗部分の再実行用50)。超過見込みなら実行前にSTOPしFableへ報告。

## 0. 読むもの
`docs/pm/PM_BRIEF.md`、`.claude/agents/sonnet-worker.md`、PM_GOVERNANCE 26節(有料runの再起動禁止・STOPセンチネル)・8節、`docs/research/JOINT-RUNTIME-EVIDENCE-01/PROCEDURE_01.md`(手順書。本委任が優先する差分は下記)、`er106_joint_runtime_evidence_01.py`、各RESULT_PACKET(`docs/pm/RESULT_PACKET_PNAP2.md`/`_PNAP3.md`/`_KP3V2.md`/`_KPFT2.md`)、各`RUNTIME_EVIDENCE_02.md`(PNAP/KP3V)、KPFT `IMPLEMENTATION_DESIGN_01.md`§runtime evidence。

## 1. Fable決定(手順書の未決事項への回答)
- (1) X/ZのTTS段は**直列**(Store manifest競合回避)。X→Zの順。KP段(選定〜gloss)はZをXのTTS中に先行してよい(Storeに触れない範囲)。
- (2) Zの試聴ページ出力先: 実行前に `user_test/family_z_melos_02` を `user_test/family_z_melos_02__backup_20261022/` へコピー退避(gitにはコピーをcommitしない。退避先は.gitignore対象か確認し、対象外なら`git status`に出たまま放置しFableへ報告)。
- (3) Xのstyle profileは正式既定 `fx_20261017`。
- (4) ZのPNAP発火素材: 同一素材の反復・発火狙いの追加runは**行わない**(PNAP設計§10)。Z PNAPは観測結果をそのまま記録。
- (5) **X素材の選定**: PNAPの正式入口(runner main)からの発火・Khaite供給証拠が必要なため、**small_bag**(`er019_output/family_x_audio_production_wiring_01/pnap_evidence_01__small_bag__run_02`、b1b本文に「Khaite's palm-sized evening clutch」)を優先。a2/b1bの両本文(article.md/parts.json)と必要なplan/supportが揃っていれば **X run=small_bag 1本**でKPFT/KP3V/PNAPの3件を兼ねる。a2が無い等で両レベル不可なら、X=coffee_prices(`er019_output/coffee_prices/run_v5_ms_01/{a2,b1b}/article.md`、新run dir)でKPFT/KP3V、+small_bag b1bのみを正式入口から1本(PNAP、≤20円)。どちらを選んだか理由付きで報告。
- (6) Z素材: melos旧完成run(最新の受入済みrun。`er026_output/family_z_production_e2e_01/melos/` 配下をls・OPEN_ITEMSのZ PRODUCTION_WIRED記録で確認)を `run_jre_01` へ複製→`--mode dry-run`でwriter/std_adjust/plan/supportが「再利用」になることを確認→`--stage all`を1回起動。RESTART_STORM(5分3回)に注意、自己timeoutを短く設定しない(長時間runはバックグラウンド起動+ログpolling)。

## 2. 事前チェック(必須・順守)
a. `git fetch`不要。`git status --porcelain` と `git diff --stat HEAD -- '*.py'` で **Production .py に未commit差分が無い**ことを確認(他agentの残置hunkがあれば実行せずFableへ報告。`er*_output/`等のデータ差分は許容)。`git log --oneline -6`で 0a82ece8e(KPFT SSOT)・25e54b99c(KP3V c)・7e8aacf69(PNAP 02c)・0febed8cb(Khaite承認)がHEAD系列に含まれることを確認。
b. 全回帰 `run_project_regression.py` を1回実行し、KPFT報告のbaseline(collected 6871/passed 6835/failed 13/errors 17)と比較、新規失敗0を確認。あわせて、KPFT報告で「baselineから消えた」とされる `er019_family_x_fx_20261016…test_k2_store_module_is_family_x_only` が何故collectされなくなったか(test削除/改名/skip)を特定し報告(修正が必要なら最小修正、Production無変更)。
c. `tools/stop_scope_check_01.py`(または手順書記載のSTOP確認)をX/Zのscopeで実行し rc=0。rc≠0なら起動しない。
d. `TTS_EXECUTION_MODE=STANDARD`。Khaite Ledger entry(ledger_id 1652efa9f4bdd7e8、human_approved=True、tts_respelling=Kate)の存在確認。
e. `er106 --dangling-grep`(配線後の値)を取得・保存。

## 3. 実行
- X run(§1(5))→各stage完了ごとに `er106` を実行(read-only)して中間保存→Z run→同様。費用は各runのraw_usage_log/台帳から集計(出典付き。未確認は未確認)。
- **失敗時**: 原因を切り分け(どの配線由来か)、技術不具合は承認範囲内で修正→test→commit→**失敗した部分のみ**再実行(走行中の有料runの再起動は禁止。終了確認後に別run dirで)。仕様変更が必要/安全問題/150円超の見込み/自律解決不能はSTOPしてFableへ報告。flagを切っての再実行による切り分けは行わない。
- 禁止: STOP/HR Lock迂回、人工entry、Store/manifestの手編集、既存runの改変、`git add -A/-u/-f`、amend/rebase/force push/stash/reset --hard。

## 4. 収集・判定(タスク別・Family別に表で)
PNAP(X/Z): 正式入口からの発火(`PASS_WITH_PRONUNCIATION_ALARM`)有無・HR queue/attempt_history増分0・Lock RESOLVED・`audit/pronunciation_alarms.json`と`operator_alarm_report.md`の内容・公開ページへの非露出・Khaite供給(TTS入力置換記録、供給適用一覧、該当clipの判定)・実使用モデルID(TTS/Primary/Secondary)。Zで自然発火が無ければ「正式経路実行済み・発火未観測」と記録。
KP3V(X/Z): 各KP clipの投票記録(P/S/W、tie-break発火有無、PASS/PASS_WITH_WARNING/NG、再生成)、Whisper preflight、技術STOPの有無、Store再利用時の再判定、追加API 0。
KPFT(X/Z): 各レベルKP=3件(Standardの3件を並べて表示)、Prompt 2 sha、`kp_backend_used`、Luna実model ID(response.model)、選定/canonicalization/gloss/Redundancy/外側retry回数、基本形化validatorの受理・拒否実例、gloss生成の品質(目視・機械)、Adv解説が`used_form`に対して生成、D1 gate結果(Z)、再生順序(Std 英→日→英/Adv 英→英解説→英)、試聴ページに3件、旧5件・Topic枠の残骸0、`kp_stage_failed.json`非発生。ユーザー原文§6の12確認項目へ1対1でPASS/FAIL/未確認。
費用: raw_usage_log stage別集計→1記事セット単価の推定(旧5件時との比較、KP選定chain/KP音声/解説の内訳)。処理時間(KP stage・TTS stageの所要)。

## 5. SSOT・成果物
- `docs/research/JOINT-RUNTIME-EVIDENCE-01/RESULT_01.md`(上記表+run dir path+費用出典)、`er106`出力json/md、試聴ページ(X: player.html、Z: pages)へのpath(ユーザーが開けるGitHub Pages URLがあれば併記)。
- OPEN-455→`RUN_COMPLETE_PENDING_FABLE`、OPEN-450/451/454→`WIRED_PENDING_FABLE`(evidence参照付き。**PRODUCTION_WIREDとは書かない**。Fableが判定後に別途反映)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: PNAP/KP3V/KPFTの3件のユーザー承認(APPROVED_FOR_PRODUCTION、2026-10-22、原文=各`_USER.md`)が登録されているかGrepし、無ければ新番号で「決定済み」として追加(KP3V報告で「UDR番号未確認」のため)。
- `docs/pm/REPORT_LEDGER.md` 1行(費用出典付き)、T-0保存 `docs/pm/delegation_log/2026-10-22_JOINT-RUNTIME-EVIDENCE-01_委任_02.md`(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、末尾から探索、本文先頭marker `FABLE-DELEGATION-MARKER: JOINT-RUNTIME-EVIDENCE-RUN-委任_02-20261022` 一致で確定)。
- commit(自分のファイル+evidence成果物のみ `git add <file>`)、secret_scan `--staged` hits=0、`git push origin HEAD:main`。大きな音声ファイルは既存の運用(Store/run dirのgit管理方針)に従う。
- `docs/pm/RESULT_PACKET_JRE2.md`に4行+判定整合行。ACTIVE_TASK固定ヘッダ更新。

## 6. 報告(Fable宛)
タスク別・Family別の判定表(PASS/FAIL/未確認とその根拠path)、本日費用累計(出典付き)、失敗と修正の履歴(commit)、未確認項目、ユーザー判断候補(原則なし)。推測で発音正否を断定しない。