## 管理ID

FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01 委任_02(修正1回目: 事前登録した問い「clip長 vs s+s融合の分離」が動詞交絡(`said` vs `replied`)で未完のため、同一Trial・同一承認範囲内で対照armを追加する)。並行タスク: ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 委任_01(別sonnet-worker、`er068_*`、SSOT編集権あり)が稼働中。本委任は**SSOT編集権なし**。一時ファイルは`docs/pm/ACTIVE_TASK_SPLIT.md`/`docs/pm/RESULT_PACKET_SPLIT.md`(委任_01の内容に追記)。`er068_*`に触れない。git: `.git/index.lock`存在時は30秒待ち×3回、commit前に`git fetch origin && git merge --ff-only origin/main`(不可なら`git pull --no-rebase`、conflict時は両追記保持)。

## 性質/到達上限Status/禁止事項

- 性質: Trial(Production非変更)。委任_01(commit a4c0af16、Phase 2 JPY36.49)の追加arm。
- 到達上限Status: `VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`。Production採用禁止。
- 費用: 本委任の上限¥25(Guardrail。本Trial全体の承認上限¥100のうち残¥63.51の範囲内、PM_GOVERNANCE 7-7)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。実行前に`plan_02.md`へ設計(セル×take×単価、出典付き)を事前登録。Azure ASRが費用の主因(委任_01で¥27.48)なので、Azureは必要最小限(各セルtake別に1回、再実行なし)。
- 禁止: 委任_01と同じ(`git add -A`/`-f`、amend/rebase/force push、stash/clean/`reset --hard`/`checkout -f`、`.env`のsource・値表示、秘密値の出力、`*.wav`・telemetry・log・`words/`のadd、`ACTIVE_TASK*.md`/`RESULT_PACKET*.md`のcommit、Production経路ファイルの編集、Melos run_e2e_02配下・Master Store・HR queue・`attempt_history.jsonl`・ledger・共有telemetryへの書込(`append_telemetry_log`等はno-op化)、Melos Production再生成・試聴ページ更新、Batch TTS、外部停止プロセスの再起動、監督ループ/`timeout`ラッパ、有料runのkill)。
- STOP確認義務: 開始時に`er026_output/family_z_production_e2e_01/`配下の`STOP_NOTICE`/`STOP`/`STOP_ALL`を確認し記録(旧記録は非適用)。
- Opus独立技術レビューGate判定: 非該当。
- 時間見込み: 40〜60分(設計10/生成・測定25/集計・報告15)。並列化: 親ID設計タスクと並列。
- 最新モデル原則: 委任_01と同一(Production同一モデル=比較可能性の例外)。model_id実測を記録。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1/D-1/G-1/F-1/T-0/T-2(+追記)/T-3は標準固定ブロックの通り(本文は委任文参照: 同一task内で同一ファイルを再読しない/Grep→該当範囲Read/git出力最小化/transcript退避は委任文で明示時のみ/委任文本文全文をdelegation_logへ保存しcheck実行/TTSは`TTS_EXECUTION_MODE=STANDARD`明示・差分再生成可否・再利用cache・budget明示・全再生成判明時STOP/費用上限はGuardrail定型文)。

## ユーザー指示(原文)

(ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 §6)「こちらはユーザーがTrial実施を承認済み。…検証対象: 固有名詞の語末と後続語頭の子音連続を避ける自然な英文構成/極端に短いナレーターclipを避ける分割方法/原文の自然さ、ストーリー性、音声品質への影響。ただし、文章の不自然な書き換えや、音声構成の大幅変更は避ける。このTrialも、Productionへの自動採用は禁止する。」(PM_GOVERNANCE 7-8、2026-10-13)「低コスト・既存予算内・Production非変更の探索Trialでは、個別の技術的選択肢を逐一ユーザー判断させない。…Trial開始時に探索範囲・費用上限・STOP条件をまとめて提示し、承認された範囲内で効率的に探索する。」→ Fable判断: 本armは承認済みTrialの事前登録した問い(長さ vs s+s分離)を完結させるための同一scope内の追加であり、上限¥100内。

## KPI provenance欄

`fresh`(Trial隔離TTS+ASR)+`reuse`(委任_01の144音声・216観測との統合集計)。fresh Production初回path E2E値: No。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

1. `er069_output/attribution_clip_split_trial_01/trial_conclusion_01.md`、`results_summary_01.md`、`plan_01.md`。
2. `er069_attribution_clip_split_trial_01_gen.py`、`_measure.py`(再利用)。
3. `docs/pm/RESULT_PACKET_SPLIT.md`(委任_01の(7)SSOT追記文案・Dangling Reference)。

## 作業内容

### 設計(plan_02.md、事前登録)
目的: 委任_01で分離できなかった「s+s融合の効果」と「動詞の効果」を分離する。
- 要因A 次語頭: 歯擦音始まり(s+s あり) vs 非歯擦音始まり(s+s なし)
- 要因B 動詞の種類を交差: s始まり={said, says, sighed}、非s始まり={replied, answered, asked}(said/repliedは委任_01と同一条件で再現性確認を兼ねる)
- 名前: Melos、Brontes。長さ: 2語固定。レベル: Std(減速前→6%減速後)+Adv。take: 2〜3(費用内で最大化。Melos>Brontes、said/replied>他動詞)。
- 判定: 委任_01と同一(evaluate_attempt/OpenAI、Azure+Phrase List [NAME]→classify_asr_match、faster-whisper参考)。加えてAzure Phrase Listなし1条件をMelos×said/repliedのみで追加。
- 費用見積: TTS call数×単価、Azure秒数×$1/h、OpenAI text単価(音声入力単価は未確認と明記)。¥25内。

### 実行・集計
- gen/measureを再利用、委任_01出力と分離。
- 集計(results_summary_02.md): (i)動詞別×名前別のOR PASS率・OpenAI綴り一致率、(ii)要因A主効果 vs 要因B効果の分離、(iii)委任_01のsaid/replied結果との再現一致、(iv)減速前/減速後/Adv別、(v)Phrase Listなし条件のMelos結果。
- 結論: 「s+s融合が主因」「said固有」「分離不能」のいずれかに数値と限界を添えて判定。Status更新、R1記述を結果に合わせて修正。
- state_guard(8件)begin/end、test_01更新、secret_scan。

## 実行コマンド全文

```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-13_FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01_02.md --json-out docs\pm\delegation_log\2026-10-13_FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01_02_check.json
set PYTHONUTF8=1
set TTS_EXECUTION_MODE=STANDARD
.venv\Scripts\python.exe er069_attribution_clip_split_trial_01_gen.py --plan er069_output\attribution_clip_split_trial_01\plan_02.json --out-dir er069_output\attribution_clip_split_trial_01\gen02 --budget-jpy 25 --no-telemetry
.venv\Scripts\python.exe er069_attribution_clip_split_trial_01_measure.py --gen-dir er069_output\attribution_clip_split_trial_01\gen02 --out er069_output\attribution_clip_split_trial_01\results_02.json --no-telemetry
.venv\Scripts\python.exe er069_attribution_clip_split_trial_01_test_01.py
.venv\Scripts\python.exe tools\secret_scan_01.py --staged
```

## Git

SSOT編集権なし。明示add: er069_attribution_clip_split_trial_01_*.py(変更分)、er069_output/attribution_clip_split_trial_01/plan_02.{md,json}、results_02.json、results_summary_02.md、trial_conclusion_02.md、cost_02.json、state_guard_02.json、本delegation_log(+_check.json)。コミット: 「FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01 委任_02: 動詞交絡の分離arm(JPY<実費>、Status=<判定>、Production無変更・採用判断なし)」trailer Managed-ID。push。

## 報告

docs/pm/RESULT_PACKET_SPLIT.md「## 委任_02」に(0)check結果・STOP確認、(1)plan_02設計・セル数・take数、(2)結果表、(3)要因分離の結論と限界・再現一致、(4)Status更新とR1/R2記述更新、(5)費用・model_id実測・単価出典・OpenAI音声入力単価未確認、回帰・state_guard、(6)SSOT追記文案(更新版)・Dangling Reference、(7)ユーザー判断候補(推奨付き)、(8)commit hash+raw URL。ACTIVE_TASK_SPLIT.md固定ヘッダ更新。
(注: 本ファイルの固定ブロック・ユーザー指示は圧縮転記。他は委任文のまま。)
