管理ID: FAMILY-Y-VOICES-DESIGN-01 委任_33(Closing一般化Trial Round 2 有料実行+評価。到達上限VALIDATED、Production配線禁止)。

## 予算(Fable確認済み。ユーザー承認: 本Trial個別上限200円[USER_12]、本日JST 2026-10-25の日次上限は1,500円へ引上げ済み)
- 個別残枠 200−67.04=132.96円。Cap=130円(`er110_output/family_y_closing_general_02/BUDGET_APPROVED.json`をFable権限で作成してよい。内容は`BUDGET_PLAN_02.md` §3の例に従い、`approved_by`に「ユーザー(USER_12 200円)/日次1,500円引上げ(2026-10-25ユーザー指示)」を記す)。
- 日次: 起動前に`py docs/pm/tools/daily_dev_cost_01.py`で当日累計を確認(直近972.57円+他agentの消費分)。累計+130円が1,500円を超える見込みなら起動せずSTOP報告。
- 他案件(KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 evidence ≤300円)が同日並行で有料実行する可能性あり。各起動前に日次累計を再確認。

## 手順(正本: `docs/research/FAMILY-Y-VOICES-DESIGN-01/CLOSING_GENERAL_01/{BUDGET_PLAN_02,PREREGISTERED_CRITERIA_02,TRIAL_RESULT_01,EVAL_01}.md`、Prompt 02=`prompt_closing_general_02.txt` sha `4713ceff…`)
1. `docs/pm/PM_BRIEF.md`・`docs/pm/ACTIVE_TASK.md`(本案件節を更新、他節を消さない)を読む。
2. `py tools/stop_scope_check_01.py --managed-id FAMILY-Y-VOICES-DESIGN-01 --run-dir er110_output/family_y_closing_general_02 --out er110_output/family_y_closing_general_02/stop_check_委任_33.json`(rc=3なら起動しない)。
3. `py er110_family_y_closing_general_trial_01.py dryrun --prompt-version 02 --effort high`(API 0、sha確認)。test `er110_family_y_closing_general_trial_01_test_01.py` PASS確認。
4. 有料実行は`.venv\Scripts\python.exe`で、BUDGET_PLAN_02 §4の4コマンド(high×2テーマ×2gens、medium×2テーマ×1gen、`--paid`)。別processで並列可だが、同一run dirへの起動間隔150秒以上・同一run 5分以内3回起動禁止(RESTART_STORM)を守る(テーマ別にprocessを分け、必要なら起動をずらす)。外部停止・原因不明rc≠0が2回続いたら再起動せずSTOP。
5. 実費を`spent_jpy`で集計し`BUDGET_LOG_02.md`、medium実測で`GEN_EST_BY_EFFORT["medium"]`とtest期待値を更新。
6. 評価: `PREREGISTERED_CRITERIA_02.md`に従い`EVAL_02.md`(機械判定: 決定論検査・Leakage Gate・根拠引用逐語一致・創作0・問い型/推量語/逆接の収斂・候補選定の並び順依存・high vs mediumの品質/単価比較)、`TRIAL_RESULT_02.md`(ユーザー閲覧用: Prompt 02全文+Prompt 01からの差分表(P1〜P5)、6本のClosing全文+切り口+Gate結果、Round 1との比較、実費・単価見込み、Status候補、Fable評価欄は空欄)。Status候補はVALIDATED/REJECTED/UDRの3値で事前登録写像どおりに機械的に出し、最終はFable。
7. SSOT: OPEN-463へRound 2結果を追記(直前再Read・最小Edit・バックアップ。他agentがOPEN_ITEMSを並行編集中)。Production変更0・新flag 0。
8. Git: 対象pathのみadd(`raw_usage_log`は不追跡)→`git commit --only`→`git push origin HEAD:main`(non-fast-forwardならfetch→`git merge --no-edit origin/main`→push。競合は両方残しSTOP報告)。`git add -A/-u`・amend・rebase・force・stash・reset --hard禁止。secret grep 0件。
9. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FAMILY-Y-VOICES-DESIGN-01_DELEGATION_33.md`(Nは574前後。先頭「管理ID: FAMILY-Y-VOICES-DESIGN-01 委任_33」を570〜590で走査。`--index -1`不可)。

## 禁止
- Prompt 02の文言変更、Gate/判定器の変更、Production参照の追加、Family Y正式経路の新設。追加生成(6本超)・再Trial。最新モデル原則: 生成gpt-6.1-sol・判定gpt-6-luna(Round 1と同一。比較条件維持のため)を報告に明記。

## 報告(RESULT_PACKET_Y33.md+口頭要約)
- 6本の結果要約(テーマ×effort: Gate PASS/FAIL、決定論NG、字数、切り口1行)、機械判定とStatus候補、Round 1比較(改善/悪化: 問い主語・推量語・逆接・Gate FAIL率)、high vs medium(品質差・単価)、実費(Round 2・案件累計/200円・日次累計/1,500円)、commit hash・raw URL、RESULT_PACKET 4行+判定整合、判断候補(27-3仕分け)。