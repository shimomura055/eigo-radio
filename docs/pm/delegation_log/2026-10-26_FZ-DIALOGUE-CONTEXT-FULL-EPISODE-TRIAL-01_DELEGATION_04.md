## 管理ID
FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_04(2026-10-26 JST、委任_03のSTOP(メロスStd M-5(3)(iii)不成立)に対するFable判断=**案B**で完了工程を実施: 事前登録は再改訂しない。メロスStdはC5(ii)不成立として事前登録写像どおりの候補Statusを付け、4単位すべて組立・解析・試聴ページを作成し、交絡・観測後改訂を全面開示する。API 0)。並行: FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_03(`er121_*`・`user_test/family_y_*`・共有SSOT所有)。本委任は共有SSOT(`OPEN_ITEMS.md`/`CURRENT_SPEC.md`/`DECISION_LOG.md`/`docs/pm/ACTIVE_TASK.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`)を編集しない(文案をRESULT_PACKETへ)。所有・禁止・固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)・ユーザー原文・Git規約は委任_02(`docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_DELEGATION_02.md`)と同一で本委任に適用。報告先 `docs/pm/RESULT_PACKET_FZFE4.md`。

## 性質/到達上限Status/禁止事項
- 性質: Trial完了工程(解析・ページ・評価文書)。API 0・TTS 0(有料呼出禁止。再生成しない)。到達上限: Status候補(事前登録02写像、単位別)+Fable評価欄空欄+ユーザー試聴待ち。
- 禁止: 事前登録(M-5(3)含む)の再改訂、NG clipの再生成、メロスStdの除外(4単位すべて提示)、Production上書き、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- Opus独立技術レビューGate: 実施済み。費用上限: JPY0(本委任)。時間見込み: 45〜60分、直列。
- 費用/日次: 当日既使用JPY約123(出典: RESULT_PACKET_FZFE3)/残約877/本委任JPY0。
- 前委任QDC・受入(Gate 7、Fable): 委任_03=M-5(3)改訂を生成前commit 131294298で固定、メロスStd(10 clip: 9 OK+1 NG=part3_c10 3試行ASR不合格、転写は正解文でleakage 0)・メロスAdv(11/11 OK)生成、実費11.185円(Phase 1b累計25.581/100円)、組立=猿の手Adv成立(−0.030 dB)、メロスAdv成立(scalar完全一致0.96345)、メロスStd不成立(−0.158 dB、原因clip part3_c4 Trial peak 0.998 vs Prod 0.958、(i)(ii)成立・(iii)超過0.058 dB)。受入=ACCEPTED(STOPは事前登録どおり)。判定整合: 重大NG=なし/主因=ctx takeのpeakがProductionより高くなり得る(take差)/是正対象=なし(事前登録維持)/STOP理由=解消(案B)/提示=本委任後。

## Fable判断(案B、理由)
- 2回目の観測後改訂は事前登録の信頼を損なうため行わない。M-5(3)は比較条件ガードであり、メロスStdの−0.158 dB(全編一律、非dialogueの相対音量不変)は聴感上の影響が小さいと見込まれるが、**事前登録どおりC5(ii)不成立→メロスStdの候補Status=REJECTED(比較条件不成立)**と機械判定し、その性質(方式の品質欠陥ではなくProduction安全弁の作動による全編一律の音量係数差)を明記する。他3単位は事前登録写像どおり(猿の手Std/Adv、メロスAdv)。
- 4単位すべてページに載せ、メロスStdには「比較条件(音量係数)不成立: Trial版は全体で−0.16 dB」の注記と、NG clip part3_c10の「現行音声」明示を付ける。ユーザーは4単位すべてを試聴できる。
- 学習事項(Opus台帳補正): ctx方式のdialogue clipは同一本文でもpeakがProductionより高くなり得る→量産化設計時はheadroom/peak正規化の扱いを設計項目にする(新仕様判断=ユーザー)。

## 作業
1. `assemble`はメロスStdについて「STOP情報付きで組立wavを生成する」モードが必要なら、事前登録の判定は変えずに組立だけ完了させる(m5_ok=false・C5(ii)不成立を`assemble_result.json`に残したまま、通しmp3を作る)。他3単位の組立済みwavは再利用。C6 Gateは4単位とも実行し結果を記録。
2. `analyze`×4→`analyze-all`→`page-all`(Trial版通し/Production版通し[同一経路mp3]/セリフ個別A/B/本文+前後文脈+summary_ja/Std・Adv区別/NG箇所「現行音声」明示/メロスStdの比較条件注記/noindex・PAGE_NOTICE/Round 1・2ページへのリンク)。公開URL=`https://shimomura055.github.io/eigo-radio/user_test/fz_full_episode_trial_01/index.html`。`py -I tools\user_test_page_standard_check_01.py --page user_test\fz_full_episode_trial_01\index.html`(記事用のためrc≠0可、理由記録)。生成後snapshot差分0を再確認。
3. `EVAL_01.md`・`TRIAL_RESULT_01.md`: C1〜C7(作品×レベル表、メロスStdのC5(ii)不成立と性質)、N1〜N6(両側全件併記、R-7(b)(c))、§5の7項目(実Trial支出25.581円の内訳/量産想定Δ/set幅[k_prod版・R2 base版]/k_ctx実測=53 clipで初回OK 52・NG 1・再生成0→k_ctx=(call数)/clip/初回成功率/NG・再生成/時間[clipあたり約9秒、単位あたり、全体]/感情情報生成費用/レビュー自動化費用=未計上)、70円/set維持可否の評価(数値で)、Status候補(単位別: 猿の手Std/Adv・メロスAdv=<写像どおり>、メロスStd=REJECTED(比較条件不成立))、観測後改訂1件(M-5(3))の開示と改訂時点で観測済みだった範囲、交絡一覧(scalar差2件、NG 1件のProduction原音差替、Std会話ctx初回、メロスpart1_c4前run再利用)、ユーザー試聴の論点(§4 A/B人手評価項目、特に「同一人物の演技の一貫性」「地の文→セリフの切替」「不自然な速度変化・長ポーズ」)、機械評価と試聴評価の区別、Fable評価欄(空欄)。
4. `BUDGET_LOG_01.md`最終化(provider別実績、clipあたり、時間)。
5. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01_DELEGATION_04.md`(Nは627〜631付近を探索、`--index -1`不可、「FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01 委任_04」を含むもの)。`python docs/pm/tools/check_delegation_prompt.py --file <同path> --json-out <同path>_check.json`。
6. Git: `docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01/{EVAL_01,TRIAL_RESULT_01,BUDGET_LOG_01}.md`、`user_test/fz_full_episode_trial_01/`(html・mp3のみ)、er118変更分(組立モード追加があれば+test)、DELEGATION_04+check。`git commit --only <paths>`→`git push origin HEAD:main`。secret grep 0件。

## 報告(RESULT_PACKET_FZFE4.md)
「現在の状態/何をやったか/何が分かったか/何が残ったか/判断候補/補足」+RESULT_PACKET 4行+判定整合行。必ず含める: 公開URL、C1〜C7表、Status候補(単位別)、§5の7項目の数値と70円評価、N指標要約(needs_listen箇所の一覧=試聴の注目点)、開示文(観測後改訂・交絡)、SSOT/Opus台帳文案(OPEN新規行[Status=PHASE1B_DONE_USER_LISTENING_PENDING、単位別候補付き]・OPEN-516追記・DECISION_LOG・M-5補正事項)、commit/push・raw URL、check結果。