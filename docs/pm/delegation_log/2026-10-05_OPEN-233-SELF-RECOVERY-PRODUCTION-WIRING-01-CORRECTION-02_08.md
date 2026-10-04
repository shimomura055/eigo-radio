# 委任_08 OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-02(全文保存)

## 管理ID

`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-02`(委任_08、親 `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`)。並行タスクなし。

## 性質/到達Status/禁止事項

- 性質: (a)ユーザー是正指示02の逐語記録とStatus是正(`USER_DECISION_REQUIRED`→`APPROVED_FOR_PRODUCTION`維持・配線作業`IN_PROGRESS`)、(b)**A構成**(rep30 frozen出力を生成した`gpt-6-luna`+V4A系Checker構成)の正確な復元、(c)A構成の**fresh限定確認**(有料≈¥5〜8)、(d)受入判定。目的は「rep30で再利用していたChecker出力を同じ構成でfresh実行しても実用上再現できるか」の技術確認であり、A/B/C比較・新Checker作成・モデル比較ではない。
- 到達Status: `APPROVED_FOR_PRODUCTION`維持。PASSなら「Production Wiring継続」をFableへ報告(ユーザー判断は求めない)。FAILなら§6手順(原因調査→合理的是正→再確認)を1回まで自律実施し、それでも成立しない場合のみSTOP候補として報告。
- **受入条件(事前固定、結果を見て変えない)**: (1)Safety-critical群の既知重大claim(B3・B4-a・A2A3-0・A4-0・A5-0、`SAFETY_CRITICAL_CLAIM_DEFS`準拠)がfresh n=2で各2/2検出=PASS。1/2のclaimは当該instanceのみn=+2追加(≈¥0.6/instance)し≥3/4でPASS、それ未満はFAIL。0/2はFAIL。(2)B群(B2_hormuz・B3・B4系・neg5 B3-same)でrep30 frozen/V0差替えがMAJORとした既知重大claimの見逃し0。(3)正常/負例群(neg1〜3+NORMAL群から3 instance)の重大誤検出(MAJOR)率が、rep30 frozen負例群の同率を超えない(frozen側の数値を先に算出し記録)。(4)frozenとの乖離: 全対象でclaim単位一致率(token重なり50%照合)を記録、Safety-critical以外の乖離はFAIL条件にしないが報告。(5)Human Review 0を壊す構造的問題(Stage 2へ渡す形式・`related_fact_id`等schemaの欠落)なし。(6)1 call平均費用がrep30 Stage 1実測(¥0.14〜0.45)と同水準、単発¥3超は記録・報告(FAIL条件ではない)。
- 禁止: Production・Trial本体コード変更禁止(fresh確認は`er052_open233_stage1_phase1_recall_check_01.py`に`--stage1-variant a_frozen_config`を追加して実施。runner/er051/er003本体は変更しない)。A/B/C比較・V0との勝敗判定・新Prompt提案・Sol等モデル変更・N増し(上記1/2補完以外)禁止。`CURRENT_SPEC.md`/`PM_GOVERNANCE.md`編集禁止。`git add -A`/`stash`/`amend`禁止。既存M差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。1回の書き込みは2,500文字以下。
- 費用上限: ¥10(Guardrail。T-3: Cap到達=自動STOPではない、暴走疑い時のみSTOP)。概算: 対象≈14 instance×n=2≈28 call×≈¥0.2≈¥6。Phase累計¥750.24/¥900(残¥149.76)。有料前に概算、実測と並記。
- T-0: 本ログに全文保存(分割)、check実行・結果記録。ユーザー指示原文は本ログの````ブロックが転写元。
- 固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## 作業
1. T-0(分割保存)→check。
2. 記録: `DECISION_LOG.md`末尾に見出し「## 2026-10-05 ユーザー是正指示 OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-02(Status是正・A構成fresh限定確認・PASSなら配線継続)」+原文逐語(スクリプト`docs/pm/tools/append_decision_log_from_sources_01.py`で転写)+Fable判断3行(「ユーザー是正に従いUSER_DECISION_REQUIREDを撤回、APPROVED_FOR_PRODUCTION維持。A構成をfresh限定確認し、事前固定受入条件(委任_08)でPASSなら後段配線へ継続。委任_05費用¥20.10は管理不備として記録のみ。」)。`OPEN_ITEMS.md`該当行Status→「APPROVED_FOR_PRODUCTION(配線IN_PROGRESS。CORRECTION-02: A構成fresh限定確認中)」。`docs/pm/ACTIVE_TASK.md`ヘッダStatus・Fable判断・受入条件(addしない)。
3. A構成の復元(¥0、`docs/pm/rep30_stage1_provenance_01.md` §7追記): frozen生成元`er051_output/**/trial_02/**/V4A/run_1.json`(09-29)と負例群(09-30)の記録メタ(prompt本文/sha、developer message有無、schema、model、params、生成スクリプト名)と、当時のコード(`git log --until=2026-09-30 -- er051_open233_checker_trial_variant_01.py er050*.py`で該当commit特定、`git show <commit>:<file>`でprompt組立関数を範囲確認)から、A構成を再現可能な形で定義。再現promptのsha256がfrozen記録と一致するrun数を報告(委任_06で22 run一致・`safety_er009_*` 9 run不一致→原因を特定し一致させる。特定できない場合は9 runのfrozen prompt本文との差分を逐語記録)。
4. fresh限定確認(有料): `er052_open233_stage1_phase1_recall_check_01.py`に`--stage1-variant a_frozen_config`を追加(当時のprompt組立を再現。昇格ルールは出力に付与されても選別に使わない=rep30同様`severity`のみ)。対象: Safety-critical群(bgroup_B3, bgroup_B4, safety_A2A3, safety_A4, safety_A5)+B群(bgroup_B2_hormuz, neg5相当, 他B群instance)+正常/負例群(neg1, neg2, neg3+NORMAL群3 instance)。model `gpt-6-luna`、n=2、`--out-subdir a_frozen_fresh_01`。比較対象はfrozen記録(rep30が実際に使った出力)(V0ではない)。集計: 受入条件(1)〜(6)の各値、claim単位一致率、SC各claim検出回数、負例MAJOR率(frozen比)、費用/call・合計・単発¥3超有無。
5. 判定: 受入条件に照らしPASS/FAILを機械的に判定。1/2のSCがあればn=+2補完。FAILなら§6: 差分(prompt/developer message/schema/model/params/復元条件)を調査→合理的是正(A構成の復元精度の是正に限る。新Prompt作成は禁止)→再確認1回(上限内)。
6. SSOT: REPORT §65(fresh確認結果)、`REPORT_LEDGER.md`1行、`OPEN_ITEMS.md`該当行進捗「委任_08: A構成fresh限定確認【PASS/FAIL、SC検出 x/5、負例MAJOR率 y%(frozen z%)、費用¥w】。次: 【後段配線 委任_09 SSOT整備→実装/§6調査】」。
7. commit/push(明示add: DECISION_LOG、OPEN_ITEMS、REPORT、REPORT_LEDGER、provenance文書、スクリプト、出力、委任ログ+check.json)。メッセージ: `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-02: 是正指示を逐語記録・Status是正、A構成(gpt-6-luna+rep30 frozen生成V4A構成)を復元、fresh限定確認【PASS/FAIL・SC x/5・負例MAJOR y%】(委任_08)`

## 事前指定Read一覧
- Read: provenance文書全文、`er052_open233_stage1_phase1_recall_check_01.py`、er051_output V4A run_1.jsonメタ、当時commitのprompt組立関数、runner Grep `SAFETY_CRITICAL_CLAIM_DEFS|MODEL|temperature|reasoning`。

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep/追記位置: DECISION_LOG末尾(スクリプト)、OPEN_ITEMS該当行、REPORT `^## §64`の後に§65、provenance文書末尾に§7、REPORT_LEDGER末尾。

## 実行コマンド全文
- T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-02_08.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-02_08.md_check.json
- fresh: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_stage1_phase1_recall_check_01.py --stage1-variant a_frozen_config --model gpt-6-luna --n 2 --out-subdir a_frozen_fresh_01 --budget-jpy 10 → `--stage agg`(引数名は実装に合わせてよい)
- Git: `git status --porcelain`→明示add→commit→`git push origin main`→`git log --oneline -1`

## 報告
- 報告(短く): (1)結論8行以内、(2)受入条件(1)〜(6)表、(3)FAIL時の§6調査と是正・再確認、(4)費用概算/実測/Phase累計、(5)SSOT・T-0・commit・push・raw URL、一覧外Read、確認/推測、(6)Fableへの論点(配線継続に進めるか)。

## ユーザー指示(原文、全文)

````
Claude Code 指示
管理ID：OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01-CORRECTION-02
目的
前回の USER_DECISION_REQUIRED 判定を是正する。
ユーザーはすでに、
rep30でTrialに織り込まれ、Production未実装の仕様はすべて正式採用し、Productionへ忠実に配線する

と明示している。
したがって、Production初回CheckerについてA/B/Cをユーザー選択肢として再提示する必要はない。
今回の正式方針は以下。
rep30の大部分で実際に使われたgpt-6-lunaのChecker構成を正本候補としてfreshで限定確認し、再現性が確認できればそのままProduction Wiringを継続する。
これは新しいProduct判断ではなく、既承認rep30構成をProductionへ忠実に移すための技術確認である。
1. Status是正
現時点のStatusは、
APPROVED_FOR_PRODUCTION
を維持する。
Stage 1 fresh Checkerの再現性未確認は、Production Wiringの未充足事項ではあるが、現時点で直ちに USER_DECISION_REQUIRED ではない。
以下の場合のみSTOPして USER_DECISION_REQUIRED 候補として報告すること。
- rep30由来Checker構成をfresh実行した結果、Safety-criticalを再現できない
- rep30と大きく異なる検出傾向になる
- 正式仕様を変更しないとProduction成立しない
- 品質・費用・運用上、ユーザーのProduct判断が必要になる
2. Stage 1 Checkerの正本候補
対象はA案。
gpt-6-luna + rep30 frozen出力を生成したV4A系Checker構成
を正本候補として扱う。
新しいCheckerを作らないこと。
現行Production V0を採用し直すB案、今回新設した拡張Checker C案は、今回のProduction Wiring対象にしない。
理由：
- Bはrep30との一致性が低い
- Cはrep30の正本ではなく、かつB4等で見逃し実績あり
- ユーザー指示は「rep30をProductionへ忠実に反映」であり、Aが最もその指示に一致する
3. fresh限定確認
A構成をfresh実行し、必要最小限の確認を行う。
目的はA/B/C比較ではなく、
「rep30で再利用していたChecker出力を、同じ構成でfresh実行しても実用上再現できるか」
の確認である。
対象は最低限、
- Safety-critical群
- B群
- 正常/負例群
とする。
費用目安は既報どおり 約¥5〜8以内。
不要なN増し・モデル比較・Checker比較は行わない。
4. 受入条件
fresh確認で最低限、
- 重大Fact見逃し 0
- Safety-criticalで既知重大問題を拾える
- 正常ケースへの重大誤検出が許容範囲
- rep30 frozen結果と重大な乖離なし
- Human Review 0を壊す構造的問題なし
- 平均費用が既存KPI内
を確認する。
単発¥3超はFAIL条件ではないが、発生したら必ず記録・報告する。
5. PASSした場合
ユーザーへ追加判断を求めず、そのままProduction Wiringを継続すること。
後段については既に準備済みのOpus#15/Fable評価に従い、
- Production正式初回path
- Stage 1 → Stage 2
- Rewrite
- Recheck
- retry
- fallback
- regeneration
- Human Review出口
- runtime evidence
- regression / integration test
- actual model_id / routing
- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- Git反映
- Dangling Reference Check
まで進める。
すべて満たした場合のみ PRODUCTION_WIRED とする。
6. FAILした場合
fresh確認で重大な不一致が出た場合は、勝手にB/Cへ切り替えない。
まず、
- 何が再現できなかったか
- frozen出力との差
- Prompt差
- developer message差
- schema差
- model/routing差
- 当時の生成条件を復元できているか
を技術的に調査する。
合理的な是正でA構成を再現できるなら自律的に修正・再確認する。
それでも成立しない場合のみSTOPし、ユーザーへ報告する。
7. 不要な作業は禁止
今回の目的はChecker再選定ではない。
以下は行わない。
- A/B/Cの追加比較Trial
- V0とAの勝敗判定
- 新Checker Promptの提案
- Sol等へのモデル変更Trial
- Production採用条件の再定義
- 追加N増し
- ユーザーへ技術選択を戻すこと
必要な作業だけを実施すること。
8. 委任_05費用
委任_05で発生した ¥20.10 は管理不備として記録のみ。
追加のユーザー判断事項にしない。
9. Closeout
Stage 1 fresh確認がPASSし、Production Wiring Checklistをすべて満たした場合のみ、
PRODUCTION_WIRED
へ更新する。
未充足項目が1つでもあれば、
APPROVED_FOR_PRODUCTION
のまま報告すること。
````
