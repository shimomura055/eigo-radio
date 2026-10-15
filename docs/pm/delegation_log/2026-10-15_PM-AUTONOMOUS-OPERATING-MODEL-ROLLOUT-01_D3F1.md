(注: 受領した委任文の保存版。ユーザー指示原文は委任_E保存ファイル`2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_D3E.md`を正とし、下の長文箇条は要点に圧縮して保存した。)

## 管理ID

`PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01` Day 3〜4 Phase 2 = 委任_F1(規則実装・第2弾: Charter v4を`CLAUDE.md`冒頭へ挿入、Agent定義3本、テンプレート3本、`PM_BRIEF.md`入口・固定ヘッダ書式、任意W9b)。前提: 委任_F2(commit `a342f7b52`)はcommit済み。並行タスク: KGCPW 委任_03、CFSA 委任_02、SKJT 委任_01(それらのファイルには一切触れない)。git `index.lock`衝突時は30秒待ち最大3回再試行。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式判断U1〜U6に基づく運営規則の実装(第2弾)。設計正本=`day3/DAY3_IMPLEMENTATION_PLAN_01.md`(W1〜W3/W6/W7/X2/W9b)+`DAY3_IMPLEMENTATION_PLAN_02_ADDENDUM.md`+`CHARTER_DRAFT_04.md`。
- 到達上限Status: `DAY3_PHASE2_F1_COMPLETE`。運営刷新全体の完了宣言はしない。
- 編集可: `CLAUDE.md`(Charter挿入のみ)、`.claude/agents/{sandwich-pm,sonnet-worker,opus-consultant}.md`(haiku-workerはtools欄整合のみ必要時)、`docs/pm/PM_BRIEF.md`(入口・固定ヘッダ書式)、`docs/pm/templates/`の4本、(任意)`docs/pm/tools/daily_dev_cost_01.py`+test、(任意)`check_delegation_prompt.py`のWARN追加(PASS/FAIL・見出し検出は不変、既存test 13件PASS維持)、`day3/`新規、`docs/pm/delegation_log/`、`docs/pm/RESULT_PACKET_ROLL3F1.md`。それ以外は編集禁止。
- 禁止: 承認済み境界の弱体化、`check_delegation_prompt.py`検出見出し・固定ブロックラベルの変更、新しい管理ファイル・Hook・台帳、git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f、有料API(JPY0)。
- Opus独立技術レビューGate: 非該当(F2で条件Aレビュー済みの設計の実装)。時間見込み約2.5h+任意W9b 1.0h、単一Sonnet直列。
- 費用/日次: JPY0。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ。
G-1: git出力は`--porcelain`/`--stat`/`--short`で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し`check_delegation_prompt.py`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。
T-2: TTSなし(本委任は対象外)。
T-3: 費用上限JPY0のためGuardrail文不要。

## KPI provenance欄

該当なし。

## Opus台帳更新

本体は編集しない(F3)。OF-D3-02(e)実施時は`day3/OPUS_FINDINGS_D3_LEDGER_DRAFT_01.md`の該当行を`IMPLEMENTED`へ更新。

## 事前指定Read一覧

1. `day3/DAY3_IMPLEMENTATION_PLAN_02_ADDENDUM.md` 全文
2. `day3/DAY3_IMPLEMENTATION_PLAN_01.md` W1/W2/W3/W6/W7/X2/W9b各節
3. `day3/CHARTER_DRAFT_04.md`:1-60
4. `day3/U2_AUTONOMOUS_RESOLUTION_RULE_DESIGN_01.md`:150-158
5. `day3/U5_COST_MANAGEMENT_DESIGN_01.md`:91-105
6. `CLAUDE.md` 全文 / 7. `.claude/agents/`4本 / 8. `docs/pm/PM_BRIEF.md`:1-12,226-272 / 9. `docs/pm/templates/`4本の指定行 / 10. `PM_GOVERNANCE.md`のGrep / 11. `tools/stop_scope_check_01.py`:1-40 / 12. `check_delegation_prompt.py`のGrep

## 事前指定Grep一覧+追記位置・更新位置の手順

W1 Charter挿入(`CLAUDE.md`冒頭「# Claude Codeへの指示」直後に`## 共通Charter`+`CHARTER_BEGIN`〜`CHARTER_END`を逐語)/W3 sandwich-pm.md(手順4-2・5責任・手順6=A4・STOP節=A5・L3/条件B区分・観点11周知・haiku tools・STOP helper案a・残存語0)/W2 sonnet-worker.md(C1〜C3・11-7参照・報告4行・原因究明2周・STOP helper)/opus-consultant.md(役割1段落)/W7 テンプレ(C4/C5・費用/日次行・観点11注記・11-5句、READ_EFFICIENCY_BLOCKは無変更)/W6 PM_BRIEF(入口0・`QDC:`行・`承認済み指示:`行)/W9b/OF-D3-02(e)(任意)。検証=残存語rg 0、参照先実在、check test PASS、事例語0件、不変文言の残存。

## 実行コマンド全文

- 前提確認: `git log --oneline -5`
- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_D3F1.md --json-out docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_D3F1_check.json`
- Charter字数: `.venv\Scripts\python.exe -c "import sys,re;t=open(sys.argv[1],encoding='utf-8').read();m=re.search(r'<!-- CHARTER_BEGIN -->(.*?)<!-- CHARTER_END -->',t,re.S);print(len(m.group(1).strip()))" CLAUDE.md`(期待=2081)
- テスト: `.venv\Scripts\python.exe -m pytest docs/pm/tools/check_delegation_prompt_test_01.py -q` / `.venv\Scripts\python.exe -m pytest docs/pm/tools/daily_dev_cost_01_test.py -q`
- W9b: `.venv\Scripts\python.exe docs/pm/tools/daily_dev_cost_01.py --date 2026-10-15 --repo-root . --ledger docs/pm/REPORT_LEDGER.md --json-out docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/daily_dev_cost_2026-10-15.json`
- git: `git status --porcelain -- <対象>`、`git log --oneline -3`

## SSOT追記文

本委任ではSSOTを編集しない(F3)。`day3/DAY3_F3_SSOT_HANDOFF_01.md`を作成する。

## Git(明示add対象・コミットメッセージ・trailer)

SSOT編集権: なし。対象ファイルのみ明示add。コミットメッセージ=「PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day3 Phase2 委任_F1: 共通Charter v4をCLAUDE.md冒頭へ配置(U1)、…SSOT/Production無変更、JPY0」。push to origin/main。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_ROLL3F1.md`へ(1)前提確認・T-0 (2)Charter位置・字数・sha・参照先実在 (3)sandwich-pm.mdの変更前/後 (4)sonnet-worker/opus/haiku変更点 (5)テンプレ変更点 (6)PM_BRIEF変更点 (7)W9b/OF-D3-02(e)実施有無と実測値 (8)検証結果 (9)F3申し送り (10)commit hash・push・raw URL (11)確認できなかった事項 (12)逸脱。Fableは(2)(3)(5)(8)を自分で読んで照合する(受領≠受入)。
