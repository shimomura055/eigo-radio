## 管理ID

GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05C(委任_05(f28524f7e)でY経路がagent側の起動間隔違反(273秒に3回)による`FAMILY_Z_RESTART_STORM` STOPで停止した件の再開。**Fable権限によるSTOP解除を本委任で明示的に許可する**: 理由=「RESTART_STORMはevidence agentの起動cadence違反(同一run 5分3回)が原因であり、品質・安全・費用上の問題ではない。確定済み文法(Std Top1/Adv Top2)は確定内容保護の対象で変更しない」。解除は`--clear-stop --reason "<上記要旨> (Fable authorization: GPG委任_05C)"`で1回のみ。有料・上限¥10。並行Agent: AI-ISLAND委任_03(X runner、Yとは無関係)。あなたの所有=`er121_output/family_y_production_01/redelivery_fee/run_gpg5_y_01`、`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{EVIDENCE_RESULT_05C,ROUTE_STATUS_05,COST_05}.md`(ROUTE_STATUS_05/COST_05は追記更新)、`evidence_runs/y/`配下、`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_DELEGATION_05C.md`(+check.json)、`docs/pm/RESULT_PACKET_GPG5C.md`(gitignore)。Productionコード編集禁止。SSOT権なし。pathspec付きcommit、wav/raw_usage_log/STOP/lock不追跡。

## 性質/禁止

- 性質: evidence runの再開(DEV run dir)。到達上限=EVIDENCE取得。
- 絶対遵守: **起動は原則1回**。追加起動が必要な場合は前回起動から**300秒以上**空け、本委任内の起動合計は**2回まで**。2回で完走しなければ停止し報告(再度のSTOP解除・別名コピー続行は禁止)。他runner稼働確認(`tasklist /v | findstr /i python`)と150秒全体間隔も守る。
- 禁止: 確定済み文法の再選定・変更(KCPガードがISSUEを出したら止める)、TTS/音声再生成(事前に`tts` staleでないことを確認。staleなら起動せず報告)、HRなし宣言、Production既定動作の変更、禁止Git操作。
- 有料run前: `py tools/stop_scope_check_01.py --managed-id GRAMMAR-PREGEN-ALL-LEVELS-01 --run-dir <run> --out <scratch>`、必要性1行記録、`.venv\Scripts\python.exe`+`TTS_EXECUTION_MODE=STANDARD`。
- 時間見込み: 約40分。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-*.jsonl`のうち最新で先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0)参照)+check。T-2/T-3: 有料=対象。

## 実施事項

1. 事前確認: `run_gpg5_y_01`の`confirmed_grammar.json`(a2=Top1 g31f4b39e68、b1b=Top2 g938cd4b23a)の内容、`tts`成果物がstaleでないこと、`--regenerate-stage part2_b1b`(および必要ならpart2_a2)が「再finalize(再選定なし)」であることをコードGrep(`er121_family_y_runner_01.py`/`er120_part2_wiring_01.py`の`regenerate|finalize_stage|confirmed`)で確認し、確定が保持される根拠を1段落で記録。
2. STOP解除(上記理由、1回)→起動1回: `er121_family_y_runner_01.py --mode real --slug redelivery_fee --run run_gpg5_y_01 <委任_05で使用したtheme/reuse引数と同一> --stages kp,assemble,pages,page_verify --regenerate-stage part2_b1b[,part2_a2 必要時] --approved-budget-jpy 10`。
3. 取得evidence(Std/Adv): finalize LLM 0(usage差分0)、`confirmed_grammar_frozen.json`、ページ(Std節/Adv Part 1直後に文法ブロック1、`verify_outputs(level, html_text=節)`PASS、`page_verify` OK)、KCP G1〜G3 PASS、model名変更後の`require_final`でPart2Staleにならない(`tools/gpg5_frozen_model_change_01.py`、API 0)、非Top1(Adv Top2)採用がページまで到達。
4. `EVIDENCE_RESULT_05C.md`、`ROUTE_STATUS_05.md`更新(6経路×KCP/GPG/フォーム経路の最終表。Y=EVIDENCE取得/未取得)、`COST_05.md`追記。
5. commit: `GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05C: Y経路evidence再開(Fable許可のSTOP解除1回・起動1回、Std Top1/Adv Top2確定→finalize LLM 0→ページ・凍結・model耐性、¥<費用>)`、trailer `Delegation: GRAMMAR-PREGEN-ALL-LEVELS-01/05C`、`git push origin HEAD:main`。Secret grep 0件。

## 事前指定Read一覧

`docs/pm/RESULT_PACKET_GPG5.md`(Y節・停止の事情・再開コマンド)、`docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/EVIDENCE_RESULT_05.md`(Y節)、`evidence_runs/y/13_STOP_RESTART_STORM_kept.json`、`er121_family_y_runner_01.py`(Grep `clear-stop|RESTART_STORM|regenerate-stage|part2` ±10)。

## 報告

`RESULT_PACKET_GPG5C.md`: (0)T-0、(1)事前確認、(2)起動記録(時刻・回数・間隔)、(3)evidence表、(4)費用、(5)判断候補、(6)必須4行+「判定整合」、(7)SSOT文案(OPEN-559 6経路Status)、commit hash・raw URL。末尾5行要約。