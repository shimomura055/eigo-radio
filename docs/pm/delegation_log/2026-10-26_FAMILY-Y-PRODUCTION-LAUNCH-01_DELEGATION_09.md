管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_09(2026-10-26 JST、E-1(宅配 redelivery_fee run_01)ユーザー試聴承認の正式反映→組立・検査・限定公開の完走→Y runtime証拠回収→SSOT/Git反映)。報告先 `docs/pm/RESULT_PACKET_YPL9.md`(新規)。あなたはsonnet-worker。委任元Fable。本委任文を `check_delegation_prompt.py` で検証し結果をRESULT_PACKETに記録すること。

## 0. 前提(全て既存成果物。全文読込は不要、必要箇所のみ)
- 手順書の正本: `docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/E1_HUMAN_REVIEW_01.md` §2(承認後の手順)・§8(減速後ASR再検証、`a2/hr_adopt_prep/y_voice_1_slowed_asr_recheck.json`=PASS済み、wav sha c3f59b00…)。直前報告 `docs/pm/RESULT_PACKET_YPL8.md`、`RESULT_PACKET_YPL7.md`、`RESULT_PACKET_YPL6.md`。
- 対象run: `er121_output/family_y_production_01/redelivery_fee/run_01/`(gate b1b/a2=BLOCK、a2 preview=STOPPED、HR Lock状態)。採用script `er121_e1_hr_adopt_r0_01.py`(既定dry-run、`--apply`は`--user-statement-ref`必須、a2 y_voice_1は再検証JSON PASS+sha一致必須、`.pre_ypl7_adopt.wav`バックアップ)。
- HEAD=2a66b4eb6、branch `work/post-merge-01`。今日の有料支出0円(日次上限1,000円)。Y案件Cap=200円(Fable 7-7)、Y累計≈167.25円 → 残≈32.75円。
- OPEN-517 F1+F2(JA ASR 誤PASS是正)はX/Z=PRODUCTION_WIRED、Y=コード配線済み・runtime未確認。E3/E4(OPEN-333)は2a66b4eb6で適用済み。Y Part 1/Part 2/文法HRはrunnerへ接続済み(委任_06)だがY実走証拠なし。

## 1. ユーザー承認(2026-10-26)— 逐語で保存すること
まず次の原文を**改変せず逐語で** `docs/pm/delegation_log/2026-10-26_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_E1_APPROVAL.md` に保存する(先頭に「ユーザー発言原文(2026-10-26、Fable経由で逐語保存)」の1行と、対象segment識別子 `a2/preview`・`b1b/y_voice_1`・`a2/y_voice_1` を列挙した付記行を加えてよい。原文部分は一字も変えない):

```
Family Y E-1『宅配の再配達は有料にすべきか？』の3音声（①②③）をすべて試聴しました。

**3本とも問題ありません。正式に採用を承認します。**

以下を進めてください。

1. ①②③のHuman Review承認を記録し、正式経路へ反映。
2. ③の6%減速版については、予定どおりASR再検証PASSを確認。
3. E-1の組立・品質検査・限定公開まで完走。
4. Family Y Part 2および日本語ASR F1+F2の正式runtime証拠を回収。
5. Fable独立受入、SSOT・Git反映を行い、Production Wiringの到達状況と完成版試聴URLを報告。

既存の承認済み仕様・品質基準は変更せず、不具合があれば委任範囲内で自律的に解決してください。
```
①=a2 `preview`、②=b1b `y_voice_1`、③=a2 `y_voice_1`(6%減速版)。`approved_by="user"`はこのユーザー発言に基づく場合のみ付与可(AI/Fableは付けない)。

## 2. 作業(順序依存のため直列。各起動間150秒以上、Get-Dateで起動時刻を記録。同一run 5分3回禁止)
A. 事前確認: `py tools/stop_scope_check_01.py --managed-id FAMILY-Y-PRODUCTION-LAUNCH-01 --run-dir er121_output/family_y_production_01/redelivery_fee/run_01 --out <run>/stop_check_委任_09.json`(rc=3なら停止・報告)。他agentのY/X/Z runnerプロセスが稼働中なら消滅を待つ。`git status --short` で共有ファイルの他agent差分を確認(DECISION_LOG.mdはCRLF全行差分あり→HEAD blob+自分のhunkでcommitすること)。
B. 承認反映: §2手順1の3コマンドを、まずdry-runで3本、問題なければ `--apply` で3本実行(③は再検証JSON PASS+sha一致が満たされることを確認。満たされなければrc=2で止まり、原因を報告。NOT_RUN代替や検査skipは禁止)。各出力(`human_review`記録・`approved_by="user"`・statement ref・バックアップwav)を証跡化。
C. Part 2の状態確認(**完走前に必ず**): run_01のmanifest/stage状態で、Y Part 2(文法解説・Key Phrase)と文法HR・KP HRのstageが**既に完了しているか**を確認する。未完了なら、runner既定のstage順に従いPart 2関連stage(名称はrunnerの`--help`/manifestで確定)を `gate,assemble,pages,page_verify` の前に、**1起動**で連結して実行する(必要なら Part 2 stage→gate→assemble→pages→page_verify を同一起動に含める。分割起動はOPEN-480 RESTART_STORMの原因)。Part 2が有料になる場合: 見積を先に算出し、Y残≈32.75円以内なら実行可、超えるなら実行せず報告。runner `APPROVED_BUDGET_MAX_JPY`=170のままで累計167.25円が予算guardに当たる場合は、Fable決定済み(Cap 200)に合わせて200へ更新し(`--approved-budget-jpy 200`)、変更箇所を報告。有料runは `.venv\Scripts\python.exe`、起動前に `cl.install` 等cost_log記録が有効であることを確認。
   - KP HR/文法HRでrc=4(待機)になった場合: 文法は既存Z R3実績と同じ `grammar-select --choice top1 --accept-ai`(Fable権限内)で進めてよい。KP HRで候補確認が必要な場合も同様にtop1採用可。**音声NGのHR Lock(ER-011/disfluency等)は、approve_regenerateを1 segmentにつき最大1回まで(Fable権限)、それでもLockが残れば採用せずSTOPして報告**(ユーザー試聴承認が必要)。
D. 完走: §2手順2を1起動で実行(`--stages gate,assemble,pages,page_verify`、Cで追加stageがあればそれを含めた1起動)。gate b1b/a2 PASS、assemble、pages、page_verify ok、final_manifest.json生成を確認。
E. 限定公開: §2手順3どおり `<run>/pages/{index.html,audio/}` を `user_test/family_y_production_redelivery_fee_01/` へ配置(`listening/`はそのまま残す。公開音声はmp3のみ、wav不追跡)。`py -I tools\user_test_page_standard_check_01.py` と `py -I tools\y_page_notice_check_01.py` 両方rc=0。公開URLは `https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_01/index.html`(E-3 SNSは `user_test/family_y_production_sns_age_limit_01/index.html`)。
F. runtime証拠回収(API 0):
   - OPEN-517 F1+F2(Y): run_01内の全JA ASR判定(`asr_judgement.r5`・`canonical_text`・`secondary.provenance_complete`・`secondary.model_id`、`a2/hr_adopt_prep/y_voice_1_slowed_asr_recheck.json`も含む)を `py docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open517_first_run_tally_01.py` で集計し、どの判定が**F1+F2適用コミット(5e50613f5)以降かつR-5(7261b9fff)以降**に生成されたかを時刻/shaで区別して記録。F1/F2が発火0でも、READING_MATCH経路で`final_gate`が適用された行が1件以上あれば「正式経路で適用済み」の証拠として記録(Fable受入基準はX/Zと同一)。`open333_first_run_tally_01.py` も実行(E3 reject・E4 fired/outcomes、alert基準: DEMOTE>3/run、E3 reject>3/run、E4 fired>3/run または E4発火行がHR到達=即報告)。結果を `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/OPEN517_RUNTIME_EVIDENCE_03_Y.md`(新規)に記録。
   - Y Part 2: Part 2の生成物(文法解説・KP選定・文法HR/KP HRの状態・ページ上の表示)の所在と検査結果を `docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/EVIDENCE_03.md`(新規)に記録。機能×Family表(①Part 2文法解説 ②Trial-08選定 ③KP HR ④文法HR ⑤OPEN-517 F1+F2 ⑥E3/E4)のY列を「事実」で埋める(PRODUCTION_WIRED判定語はFableが付ける。あなたは候補と根拠のみ)。
G. SSOT/記録(最小編集、全文読込禁止、Grepで該当行のみ): `OPEN_ITEMS.md` OPEN-520(Y立上げ)・OPEN-484・OPEN-517・OPEN-525 の該当行をStatus要約で更新(新規OPENを起票する場合は11-8分類必須)。`CURRENT_SPEC.md` の「Family別Status」節・OPEN-517 Y行を事実ベースで更新。`DECISION_LOG.md` に委任_09の1エントリ(ユーザー承認の逐語出典path付き)。`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/BUDGET_LOG_02.md` に本委任の実費(cost_log実測、未記録なら「未確認」と明記し推定値を費用表に使わない)。`docs/pm/ACTIVE_TASK.md` 固定ヘッダ(PM_BRIEF書式)+委任_09節、`docs/pm/REPORT_LEDGER.md`・`docs/pm/USER_DECISION_REGISTER_01.md`(E-1試聴承認=判断済みへ)。
H. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-26_FAMILY-Y-PRODUCTION-LAUNCH-01_DELEGATION_09.md`(Nは612前後。`--index -1`不可。「委任_09」「RESULT_PACKET_YPL9」を含むものを探し、一致を確認)。
I. Git: secret grep 0件確認。対象pathのみ(`git add <path>`個別、または共有SSOTに他agent差分がある場合は一時index+commit-tree/`git commit --only`)。禁止: `git add -A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f、`git checkout -- <file>`。commit後 `git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP)。wav/raw_usage_log/STOP/lock/RUN_LOCK/ACTIVE_TASK/RESULT_PACKETは不追跡。

## 3. 禁止・境界
- 承認済み仕様・Gate・閾値・Prompt・品質基準を変更しない(不具合是正は委任範囲内で可、ただし変更前後の差分と影響範囲を報告)。STOP/HR Lock/Gateの迂回・名称変更による回避禁止。
- `approved_by="user"`はユーザー原文に基づく3 segmentのみ。他segmentがNGになった場合はAI承認しない。
- 有料支出は合計でY残≈32.75円を超えない。超える見込みなら実行前に止めて報告。
- 外部停止・原因不明rc≠0が2回続いたら再起動せずSTOP。

## 4. 報告(RESULT_PACKET_YPL9.md、Fable向け。「現在の状態/何をやったか/何が分かったか/何が残ったか/ユーザー判断候補/補足」)
必ず含める: (1)3 segmentの採用記録(approved_by・statement ref・時刻)、(2)③の再検証PASS参照(path・sha一致)、(3)gate/assemble/pages/page_verify結果と公開URL・standard/notice check rc、(4)Part 2のY実走結果(stage・HR状態・費用)、(5)OPEN-517/E3/E4 tally結果とalert該当、(6)機能×Family表のY列(事実+Status候補+根拠)、(7)費用(cost_log実測、Y累計/200、日次/1,000)、(8)起動時刻一覧(Get-Date)、(9)commit hash・push結果・変更ファイルのraw.githubusercontent.com URL、(10)未解決・ユーザー判断候補(実害・影響・QCD影響を確認したもののみ)。