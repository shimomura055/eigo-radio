## 管理ID

PM-SSOT-SYNC-07(KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01 委任_01の結果とFable評価のSSOT反映。API 0・JPY0)。並行タスク衝突確認: 並行Agent 5件(FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01[`er121_*`+有料run]、FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 委任_01[read-only]、TTS-RETRY…01X/Y/Z[read-only])。いずれもSSOT編集権なし。**SSOT編集権は本Agentのみ**(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/ACTIVE_TASK.md`)。`CURRENT_SPEC.md`は本委任では編集しない(Trial段階・Production不変)。git index.lock競合時は10秒待って再実行(最大3回)。**注意**: 前委任(SYNC-06)時点でindexに他Agentのstage済みファイルが約248件残っていた(その後commit 3e7cf130fでcommit済みの可能性)。`git diff --cached --stat`で自分以外のstageが残っていれば、pathspec付き`git commit -- <自分のpath>`で自分のファイルだけをcommitし、他Agentのstageには触れない。

## 性質/到達上限Status/禁止事項

- 性質: SSOT転記。到達上限Status: 転記完了。転記内容のStatusはFable判定どおり(格上げ禁止)。
- 禁止: Production/コード変更、API支出、`CURRENT_SPEC.md`編集、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- 費用/日次: JPY0。
- Opus独立技術レビューGate(11-3): 非該当(転記)。
- 時間見込み: 約25分。並列化: なし(SSOT直列)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_PM-SSOT-SYNC-07_DELEGATION_01.md` をN=658から順に試し、先頭が「## 管理ID」+「PM-SSOT-SYNC-07」で始まるものを採用(`--index -1`不可)。

## ユーザー指示(原文)

該当なし(Fable判定の転記。Trial指示原文=`docs/pm/delegation_log/2026-10-26_KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01_USER.md`、2026-10-26後続指示§5「Trial完了時はVALIDATED／REJECTED／USER_DECISION_REQUIREDに分類し、正式採用はユーザー判断を待つ。」=`docs/pm/delegation_log/2026-10-26_FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_USER.md` §5)。

## Fable判定(転記する内容。文言はこのまま使う)

- **Trial Status: VALIDATED(限定)_USER_DECISION_REQUIRED(Production採用判断)**。Production不変。
- Fable独立評価(ユーザー原文§6の7項目):
  1. 単語候補は適切に増えた: W3は12/12 runで3件返答、Gate全通過(36/36)、有用(厳格Y)平均2.2件/run。現行方式では単語候補はほぼ0。
  2. フレーズ品質は下がっていない: フレーズY率61%→62%、数合わせ型(N)割合21%→4%。
  3. 最終6〜7件の安定確保: 境界込み(Y+B)では12/12 runで6件以上(中央7.5)、judge基準では中央6・最小5、厳格Yでは中央5.5・6件以上は6/12 run。**「有用」の閾値次第で評価が変わる**(限定事項)。
  4. 既存Gateとの整合: Production関数をimport同一引数で適用、Gate・Prompt・HR・候補数仕様は無改変。除外7件は既存Gateの既知挙動。
  5. X/Z共通: 同一`generate_candidates`注入点、Z SRC D1・人称整合も全PASS(44候補)。
  6. Y将来適用: 注入点は同一(`er121_family_y_runner_01.py:540-569`)だがY正式KP経路の一般化配線(OPEN-484)は未了。
  7. QCD: +0.19円/level(約+0.4円/記事セット=70円目標の約0.5%)、call数同等(P7→W3の2 call直列)、制作時間影響なし。
- 限定事項: P7は7件要求に平均5.4件しか返さない(フレーズは増えない)。文学作品Adv(猿の手)でフレーズ枠が記事固有句に偏り有用3件。現行側は各level1回のみ(分散未確認)。自ルーブリックとjudgeの一致67%。
- 採用時に必要な変更(ユーザー承認事項): (a)Prompt 2(3件)/Prompt 2-V(最大5件)→P7/W3への置換(承認済みPromptの変更)、(b)候補数仕様 `KP_CANDIDATE_MAX=8`→最大10、(c)HRでの単語枠の見せ方(現行の自動推奨=KP先頭3件/Adv単語先頭5件のままでは単語が採用に届かない)。
- Fable推奨: **採用(条件付き)**=P7→W3方式をProduction候補生成へ採用し、HRで「フレーズ枠/単語枠」を分けて提示、候補上限10。P7要求数の5への縮小・単語枠「不足許容」の明示は採用後の初回運用で観測してから判断(追加Trialは不要)。
- 費用: 実費38.64円(Trial 21.43+現行fresh 6.39+judge 10.82)、Guardrail 80内。モデル: 生成=gpt-6-luna(Production SUPPORT_MODELと同一、比較条件統一のため最新最上位ではない)、judge=gpt-6.1-sol(最新最上位系)。
- HEAD既存test失敗2件(er119 isolation・grammar_files)は本Trialに起因せず未修正(既知、後続)。isolation allowlistへ`er124_`2行追加(先例どおり)。

## KPI provenance欄

該当なし(転記。出典=`docs/pm/RESULT_PACKET_KPT1.md`、`docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/{RESULT_01,COMPARISON_01,STATUS_01}.md`)。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_KPT1.md`: Grep `^\(9\)|SSOT文案|^\(8\)` → ±25(SSOT文案と判断候補)
- `docs/pm/ACTIVE_TASK.md` 全文
- `docs/pm/RESULT_PACKET_SSOT6.md`: Grep `OPEN-533|最大番号|OPEN-53` → 新規OPEN番号の確認用

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `^\| OPEN-53[0-9]|OPEN-533` → 最大番号を確認し次番号(OPEN-534想定)で新規起票(11-8分類=ユーザー判断要[D区分]、Status=VALIDATED(限定)_USER_DECISION_REQUIRED、概要=RESULT_PACKET_KPT1 (9)の文案+Fable推奨)。Grep `OPEN-526` → 「KP Trial(OPEN-534)の採否はAI島HR候補数案A/B/Cと関連(採用時は候補上限10)」を1文追記。Grep `OPEN-484` → 「P7/W3採用時のY注入点は同一」1文追記。
- `DECISION_LOG.md`: 本日末尾に1件(RESULT_PACKET_KPT1 (9)の文案+Fable判定VALIDATED(限定)+推奨)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: 新規エントリ(決めること=P7→W3方式の採否/「有用6〜7件」の閾値/単語枠のHR扱い/文学Advの扱い、選択肢と影響、Fable推奨=採用(条件付き)、根拠1行、参照URL)。
- `docs/pm/REPORT_LEDGER.md`: KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01=Fable報告予定(2026-10-26)、本件。
- `docs/pm/ACTIVE_TASK.md`: 上書き(並行=FAMILY-Y-VOICE-TABLE(Cap60)、FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 委任_01(JPY0)、TTS-RETRY…01X/Y/Z(JPY0)、UDR-blocking=OPEN-526・527・529(区分2)・534(KP Trial採否)、STOP条件=猿の手run_fzcw_e1_01残置、QDC=当日約549円+Y Voice≤60/1,000)。

## 実行コマンド全文

- `git diff HEAD --stat -- OPEN_ITEMS.md DECISION_LOG.md docs/pm/REPORT_LEDGER.md docs/pm/USER_DECISION_REGISTER_01.md`(編集前。空であること。差分があればHEAD blob+自hunk方式)
- `git diff --cached --stat`(他Agentのstage有無を確認)
- Secret grep: `git diff --cached -- OPEN_ITEMS.md DECISION_LOG.md docs/pm/REPORT_LEDGER.md docs/pm/USER_DECISION_REGISTER_01.md | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

上記Fable判定の文言とRESULT_PACKET_KPT1 (9)の文案を使う。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/delegation_log/2026-10-26_PM-SSOT-SYNC-07_DELEGATION_01.md`(+`_check.json`)。commitはpathspec付き(`git commit -m ... -- <上記path>`)。ACTIVE_TASK/RESULT_PACKETはaddしない。
- commit message: `PM-SSOT-SYNC-07: KPフレーズ7+単語3 Trial結果(Fable評価VALIDATED(限定)_UDR、推奨=条件付き採用、OPEN-534起票、OPEN-526/484追記、UDR、報告台帳、API 0)`
- trailer: `Delegation: PM-SSOT-SYNC-07/01`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_SSOT7.md`: (0)T-0、(1)編集前状態・他Agent stageの有無、(2)更新行(ファイル:行)、(3)`git diff --cached --stat`、(4)commit hash・push・raw URL(OPEN_ITEMS.md/DECISION_LOG.md/USER_DECISION_REGISTER_01.md)、(5)必須4行+「判定整合: 重大NG=<なし|あり>」、(6)一覧外Read。末尾に要約5行以内。