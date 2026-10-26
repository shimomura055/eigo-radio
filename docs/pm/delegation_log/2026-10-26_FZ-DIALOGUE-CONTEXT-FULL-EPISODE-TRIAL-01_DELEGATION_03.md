## 管理ID
FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_03(2026-10-26 JST、委任_02のM-5(3) STOPからの再開。Fable判断=案A採用)。並行: FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_03(`er121_*`・`user_test/family_y_*`・共有SSOT所有)。本委任は共有SSOT(`OPEN_ITEMS.md`/`CURRENT_SPEC.md`/`DECISION_LOG.md`/`docs/pm/ACTIVE_TASK.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`)を編集しない(文案をRESULT_PACKETへ)。所有・禁止・Guardrail・固定ブロック・ユーザー原文・KPI provenance・Git規約は**委任_02(`docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_DELEGATION_02.md`)と同一**(ここに再掲しない。E-1/D-1/G-1/F-1/T-0/T-2/T-3の固定ブロックも同文書のものを本委任に適用)。報告先 `docs/pm/RESULT_PACKET_FZFE3.md`。

## 性質/到達上限Status/禁止事項
- 委任_02と同一(Trial、DEV専用、到達上限=Status候補+ユーザー試聴待ち、Production採用・上書き禁止)。費用上限: 上限¥100(Guardrail、Phase 1b。既使用14.40円、残約85.6円、残り見積約14円)。T-3定型文は委任_02のとおり。
- Opus独立技術レビューGate: 実施済み(再レビュー不要。M-5前提の崩れは台帳補正事項として文案化)。
- 時間見込み: 約60〜75分(改訂commit 5、メロス生成2単位 約15、組立・解析・ページ 25、EVAL/TRIAL_RESULT 20、Git 5)。
- 費用/日次: 当日既使用JPY約112(出典: RESULT_PACKET_FZFE2。起動前に`py docs/pm/tools/daily_dev_cost_01.py`で実測)/残約888/本委任見積JPY約14/改善見込み高/承認区分: C。
- 前委任QDC・受入(Gate 7、Fable): 委任_02=Opus M-1〜M-8・R-1〜R-9実装(test 87 PASS)、事前登録02を生成前commit 04338d5b4で固定、自己検証4単位一致・dry-run隔離実測・TEXT同一性53/53、猿の手Std/Adv 32 clip生成(32/32初回OK、14.40円)、Production tree-hash差分0。STOP=M-5(3) headroom.scalar不一致(Trial 0.99656 vs Prod 1.0。原因=Trial clip part2_c10の24k→48k変換後サンプル間ピーク0.9834>安全弁0.98。Opus前提「会話peak≦0.95<0.98」の崩れ)。受入=ACCEPTED(STOPは委任文どおりの正しい停止)。判定整合: 重大NG=なし/主因=M-5(3)定義の前提崩れ/是正対象=事前登録02 M-5(3)の改訂(Fable)/STOP理由=解消(本委任で再開)/提示=本委任後。

## Fable判断(案A採用、理由付き)
- M-5(3)を次のとおり改訂する: 「`headroom.scalar`の差が生じても、(i)原因がTrial dialogue clipのサンプル間ピークのみ(非dialogue clipのpeakは不変)、(ii)Production安全弁(閾値0.98)の設計どおりの作動、(iii)差が0.1 dB以内、の3点を満たす場合は『記録付き成立』とし、実測scalar・dB差・原因clipを交絡として全報告に明記する。M-5(1)(2)は不変。」
- 理由: M-5はProduction規則・品質基準ではなくTrialの比較条件ガード(Fable設定)であり、安全弁は全編一律scalarで相対音量を変えない(−0.030 dB、聴感検知限界以下)。案B(take入替)は結果を見て試行を選ぶため不可、案C(評価不能)は目的に対し過剰。
- 開示義務: 本改訂は「1単位の組立観測後・残り単位の生成前・試聴/機械指標の観測前」に行う事前登録の改訂である。PREREGISTERED_CRITERIA_02に改訂履歴(時刻・理由・観測済み範囲)を明記し、EVAL/TRIAL_RESULT/ユーザー報告で「観測後改訂1件(M-5(3))」として必ず開示する。
- 猿の手の生成済み32 clipは再生成しない。

## 作業
1. `PREREGISTERED_CRITERIA_02.md`にM-5(3)改訂を履歴付きで追記し、`compare_to_production`の`m5_ok`判定を改訂に合わせて修正(test追加: 条件(i)〜(iii)成立時のみ成立、非dialogue peak変化や0.1 dB超は不成立)。**メロス生成前にcommit**(時刻固定)。
2. 起動前: daily cost実測、`py tools/stop_scope_check_01.py --managed-id FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 --run-dir er118_output/fz_full_episode_trial_01 --out er118_output/fz_full_episode_trial_01/stop_check_委任_03.json`(rc=3なら停止)、R-1 snapshot再取得(Y委任_03由来の差分はY dir配下かを確認し区別)。
3. 生成: `$env:PYTHONUTF8=1; $env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er118_fz_full_episode_trial_01.py gen --work melos --level a2` → 150秒以上後に `... gen --work melos --level b1b`(Get-Date記録、同一コマンド5分3回禁止、外部停止・原因不明rc≠0 2回でSTOP)。各単位後に実費を`BUDGET_LOG_01.md`へ。
4. `assemble`(猿の手Adv、メロスStd/Adv)→M-5改訂判定→C6 Gate→R-4 mp3→生成後snapshot差分0確認。`analyze`×4→`analyze-all`→`page-all`(Trial版通し/Production版通し[同一経路mp3]/セリフ個別A/B/本文+前後文脈+summary_ja/Std・Adv区別/NG箇所明示[今回NG 0なら「なし」]/noindex・PAGE_NOTICE/Round 1・2ページへのリンク)。公開URL=`https://shimomura055.github.io/eigo-radio/user_test/fz_full_episode_trial_01/index.html`。`py -I tools\user_test_page_standard_check_01.py --page user_test\fz_full_episode_trial_01\index.html`(記事用のためrc≠0可、理由記録)。
5. `EVAL_01.md`・`TRIAL_RESULT_01.md`: C1〜C7(作品×レベル)、N1〜N6(両側全件併記)、§5の7項目(実Trial支出/量産想定Δ/set幅[k_prod版・R2 base版]/k_ctx実測/初回成功率/NG・再生成/時間[clipあたり・全体])、70円/set維持可否、Status候補(事前登録02写像)、観測後改訂の開示、交絡一覧(scalar −0.030 dB、メロスpart1_c4前run再利用、Std会話ctx初回)、ユーザー試聴の論点(§4 A/Bの人手評価項目)、Fable評価欄(空欄)。
6. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_DELEGATION_03.md`(Nは629前後、`--index -1`不可、「FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_03」を含むもの)。`python docs/pm/tools/check_delegation_prompt.py --file <同path> --json-out <同path>_check.json`。
7. Git: 改訂commit(生成前: PREREGISTERED_CRITERIA_02、er118 module+test)と完了commit(EVAL_01、TRIAL_RESULT_01、BUDGET_LOG_01、`user_test/fz_full_episode_trial_01/`[html・mp3のみ]、DELEGATION_03+check)。`git commit --only <paths>`→`git push origin HEAD:main`。secret grep 0件。wav/raw_usage_log/PHASE1_GO/snapshot/RESULT_PACKET不追跡。

## 報告(RESULT_PACKET_FZFE3.md)
「現在の状態/何をやったか/何が分かったか/何が残ったか/判断候補/補足」+RESULT_PACKET 4行+判定整合行。必ず含める: 改訂commit hash・時刻、起動時刻・各単位実費・累計/100・日次、C1〜C7表、NG件数、N1〜N6要約、§5の7項目と70円評価、公開URL、Status候補、交絡・観測後改訂の開示文、SSOT/Opus台帳文案(OPEN新規行・OPEN-516追記・DECISION_LOG・M-5補正事項)、commit/push・raw URL、check結果。