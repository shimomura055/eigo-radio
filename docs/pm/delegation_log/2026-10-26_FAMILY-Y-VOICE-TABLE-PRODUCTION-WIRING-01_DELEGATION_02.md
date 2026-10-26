## 管理ID

FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01 委任_02(残りのruntime evidence取得: Advanced Voice 1=Puck、同引数再起動でAPI 0、Gate、組立。前委任の自己発動RESTART_STORMの解除を含む)。並行タスク衝突確認: 並行Agent 2件(TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_02[read-only統合]、FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 委任_01[read-only棚卸し。`run_voice_puck_ev_01`を読み取ることがあるが書込みなし])。あなたの所有=`er121_output/family_y_production_01/redelivery_fee/run_voice_puck_ev_01/`、`docs/research/FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01/{EVIDENCE_02,COST_02}.md`・`evidence_02.json`、`docs/pm/delegation_log/2026-10-26_FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_DELEGATION_02.md`(+check.json)、`docs/pm/RESULT_PACKET_YVT2.md`。コード編集なし(必要と判明したら実行前にSTOPして報告)。SSOT編集権なし。git index.lock競合時は10秒待って再実行(最大3回)。

## 前委任の受入記録(Gate 7)
- 当初目的(ユーザー原文§1逐語): 「Voice Registry、正式Production経路、必要なテスト、runtime evidence、SSOT/Gitまで整合させ、**PRODUCTION_WIRED**を目指す。」「既存の完成音声を無断で差し替えない。今後の制作に適用する。」
- 実際の最終成果物: コード反映(`er121_family_y_structure_01.py` `Y_DIALOGUE_VOICE_POOL`・`FIXED_VOICE_SLOTS` Voice 1=Puck、`verify_voice_assignment`のpool引数化)、test 9件新規+既存3箇所更新、er121回帰306 PASS/1 skip、commit 31c41ea76。runtime evidence=Std `y_voice_1`のみ(actual voice=Puck、model gemini-3.8-flash-lite-tts、STANDARD、attempt 1、ASR PASS、slowdown_applied=True、TTS 1回・ASR 2回、1.3459円)。
- 証拠: `docs/research/FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01/EVIDENCE_01.md`、`evidence_01.json`、run dir `.../run_voice_puck_ev_01/a2/`。
- 一致・不一致: 承認表・Voice 1=Puck・Z不変・既存音声不差し替え=一致。Adv evidence・再起動API 0・Gate・組立=未取得(不一致=未完)。
- 最終受入判定: 部分受入(コード・test=ACCEPTED、evidence=未完→本委任で継続)。判定整合: 重大NG=なし/主因=起動手順ミスによるRESTART_STORM/是正対象=evidence残り/STOP理由=run dir STOP(解除はFable権限)/提示=可。
- QDC記録: 費用1.35円/Cap 60、改善見込み高(残り約1.5円・2〜3起動)、次の一手=本委任。

## 性質/到達上限Status/禁止事項

- 性質: Production配線のruntime evidence取得(承認済み仕様)。到達上限Status=EVIDENCE_COLLECTED(PRODUCTION_WIRED判定はFable)。
- **STOP解除のFable許可**: `run_voice_puck_ev_01`のSTOP/`RESTART_STORM_LOCK.json`は、前委任の起動手順ミス(`--theme-package`付け忘れrc=2[API 0]+Std成功+Adv rc=3[API 0]が300秒内)による自己発動であり、課金暴走・外部障害ではないことを前委任報告で確認した。**Fableは解除を許可する**。解除コマンドの`--reason`には「FABLE_AUTHORIZED: self-inflicted RESTART_STORM by launch-arg mistake (2 of 3 launches API 0), cause understood, no billing anomaly; delegation FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01/02」を入れる。解除後は**起動間隔150秒以上**(各起動前にGet-Date記録)を厳守し、同一run dirで5分内3起動を絶対に超えない(事前に引数を`--help`と前委任のlaunch記録で確認してから起動)。別run dir名での回避は禁止。rc≠0が1回でも出たら原因を把握するまで再起動しない(解析→必要なら報告)。
- 禁止: 公開pages生成(`pages`/`page_verify`は実行しない)、run_01・公開dirの変更、コード編集、Family Z変更、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- 費用: 上限¥20(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 費用/日次: 当日(JST)既使用約JPY551(出典: ACTIVE_TASK約549+前委任1.35)/残約JPY449/本委任見積JPY2〜5(根拠: Adv Voice 1 TTS 1〜3 attempt×約1.3円+Gate/組立API 0)/改善見込み高/承認区分: C。
- Opus独立技術レビューGate(11-3): 非該当(前委任で候補表は読み取り専用データ・選定機構新設なしと確認済み)。
- 時間見込み: 約40分(解除+Adv起動5分/150秒待機×2/Gate・組立起動10分/文書化15分)。並列化: 起動は直列(同一run dir)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」旧来の「上限¥X、超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが無いもの)は使用しない。既存7-5(4)「想定外の全再生成が判明したらAPI実行前にSTOP」は本T-3の「暴走疑い時のSTOP」に該当する条件として維持する(置き換えではない)。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_DELEGATION_02.md` をN=660から順に試し、先頭が「## 管理ID」+「FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01 委任_02」で始まるものを採用(`--index -1`不可)。

## ユーザー指示(原文)

`docs/pm/delegation_log/2026-10-26_FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_USER.md` §1・§6(保存済み。§6のPRODUCTION_WIRED判定条件9項目を本委任のチェックリストに使う)。

## 実施事項

1. `py tools\stop_scope_check_01.py --managed-id FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01 --run-dir er121_output\family_y_production_01\redelivery_fee\run_voice_puck_ev_01 --out docs\research\FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01\stop_check_02.json`(引数名が異なれば`--help`で確認し実値で記録)。本run dirのSTOPが「自己発動RESTART_STORM」であることを`RESTART_STORM_LOCK.json`の内容(3起動の時刻・rc)で再確認し、EVIDENCE_02に転記。
2. 解除: `py er121_family_y_runner_01.py --clear-stop --slug redelivery_fee --run run_voice_puck_ev_01 --reason "FABLE_AUTHORIZED: self-inflicted RESTART_STORM by launch-arg mistake (2 of 3 launches API 0), cause understood, no billing anomaly; delegation FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01/02"`。解除後のrun dir状態(STOP/LOCK消失、解除記録ファイル)を記録。
3. 起動A(Adv): 前委任のStd成功起動と同じ引数構成(`--theme-package`等を含む。前委任の`launch_*.json`/EVIDENCE_01の起動実例をそのまま流用)で `$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er121_family_y_runner_01.py --slug redelivery_fee --run run_voice_puck_ev_01 --level b1b --stage tts_b1b --only-segments y_voice_1 --budget-jpy 20 <前委任と同じ追加引数>`。実引数は全文記録。起動前Get-Date記録。
4. 起動B(150秒以上後): `--stages tts_b1b,tts_a2,gate,assemble`相当(前委任報告の2回目案)。目的=(i)同引数再起動で新規API 0(Std/Adv Voice 1とも`reused_from_previous_run`/cost_log不変)、(ii)新Voiceでの Y Gate・共有Audio Validation Gate PASS、(iii)組立OK。Gate/組立が別stage起動を要する場合は150秒規律を守って分ける(5分3回を超えない計画を事前に書く)。
5. evidence整理(`EVIDENCE_02.md`/`evidence_02.json`): ユーザー原文§6の9項目チェックリスト(承認仕様一致/正式初回経路実装/retry・fallback・regeneration・resume整合[再起動API 0+旧Algieba cacheが復活しない根拠=cache keyにvoice含有:行]/正式runtime発火証拠[Std・Adv actual voice=Puck]/Regression・Validator・integration test PASS/actual model_id・routing/CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS更新[Fable sync待ちと明記]/Git反映/未承認仕様・Dangling Referenceなし)。Advのattempt数・Repetition旗・ASR結果・長さ・Style prefix(使用されたstyle文字列も記録=Y-F01確認の参考)。
6. `COST_02.md`: 起動時刻・間隔・実費・累計(前委任1.3459円+本委任)。

## KPI provenance欄

fresh(production_formal_path、正式CLI `er121_family_y_runner_01.py`、新規run dir)。E2E自己確認: Yes(Voice 1 segment)。他segmentはrun_01からの複製(reuse)で本委任では生成しない。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

- `docs/research/FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01/EVIDENCE_01.md` 全文、`COST_01.md` 全文(起動実例・引数)
- `er121_output/family_y_production_01/redelivery_fee/run_voice_puck_ev_01/RESTART_STORM_LOCK.json`・`STOP`(内容)
- `er121_family_y_runner_01.py`: Grep `--clear-stop|clear_stop|RESTART_STORM|--stages|--stage|--only-segments|--theme-package|--budget-jpy` → ±10(引数の実名確認)
- `er121_family_y_audio_01.py`: Grep `reuse_key|cache_key|reused_from_previous_run|voice` → ±10(旧Voice cache非復活の根拠行)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `voice` in `er121_output/family_y_production_01/redelivery_fee/run_voice_puck_ev_01/b1b/results*.json`(起動A後) → actual voice=Puck確認
- Grep `spent_jpy|cost` in run dir `cost_log*`/`audit/raw_usage_log*`(起動B後) → 新規API 0確認
- 成果物は`docs/research/FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01/`へ追記ファイルとして新規作成

## 実行コマンド全文

上記「実施事項」1〜4のとおり(引数実値は`--help`と前委任記録で確定し、EVIDENCE_02に全文記録)。Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件。

## SSOT追記文

SSOT編集権なし。RESULT_PACKET_YVT2.md(9)に、前委任のSSOT文案を更新した最終文案(Status=EVIDENCE_COLLECTED[Std/Adv]、evidence path、Algieba vs Puckのattempt実績、OPEN-531 CLOSED案、OPEN-533追記案)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `docs/research/FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01/{EVIDENCE_02,COST_02}.md`、`evidence_02.json`、`stop_check_02.json`、`docs/pm/delegation_log/2026-10-26_FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_DELEGATION_02.md`(+check.json)。run dir配下はwav/raw_usage_log/STOP/lock不追跡。pathspec付きcommit。
- commit message: `FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01 委任_02: Voice 1=Puck Adv runtime evidence+再起動API 0+Gate/組立(正式CLI、実費<x>円、RESTART_STORM解除=Fable許可、Production未公開)`
- trailer: `Delegation: FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01/02`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_YVT2.md`: (0)T-0、(1)STOP解除の記録(根拠・コマンド・前後状態)、(2)起動A/Bの時刻・間隔・引数・rc、(3)Adv evidence(actual voice/model/attempt/ASR/Repetition/Style文字列)、(4)再起動API 0の証拠、(5)Gate・組立結果、(6)§6 9項目チェックリスト、(7)費用、(8)旧Voice cache非復活の根拠、(9)SSOT文案、(10)必須4行+「判定整合: 重大NG=<なし|あり>」、(11)一覧外Read、commit hash、raw URL。末尾に10行以内の要約。