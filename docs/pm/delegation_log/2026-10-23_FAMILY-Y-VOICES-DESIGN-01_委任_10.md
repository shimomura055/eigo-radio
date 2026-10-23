FABLE-DELEGATION-MARKER: FAMILY-Y-VOICES-DESIGN-01-委任_10-V1-REPAIR-B-AND-FULL-AUDIO-COMPLETION-20261023

# FAMILY-Y-VOICES-DESIGN-01 委任_10: 人物1(V1)音声の修復案B(英語V1の反復語句・文頭の言い換え→V1のみStd/Adv再生成)→正式Gate→Std/Adv通し音声組立→試聴ページ(`user_test/family_y_trial_03/`)完成→page_verify。DEV/Trial経路のみ、X/Z Production変更0、到達上限=VALIDATED候補(最終判定はFable)。費用上限40円(Y累計上限600円・残約284円の内。当日上限1,400円)。

## 0. 先に読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(固定ヘッダ、line 2、Family Y行)、`.claude/agents/sonnet-worker.md`、`docs/pm/RESULT_PACKET_FYT6.md`、`docs/research/FAMILY-Y-VOICES-DESIGN-01/TRIAL_03/{TRIAL_03_RESULT_01,V1_REPAIR_PLAN_01,AUDIO_QA_03,WORLD_SETTING_01,TEXT_DIFF_01,BUDGET_PLAN_01,PLAY_VERIFY_03}.md`、`docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_{USER_04,USER_04_ADDENDUM_BUDGET,委任_09B}.md`(制約継承)、`er011_output/local_rewrite_recovery/it3/b1b/local_rewrite_recovery_full_story_part1.json`、`er110_family_y_persona_trial03_01.py`、`er110_family_y_persona_audio_page_03.py`。

## 1. Fable判断
- 委任_09Bの結果(本文完成、V1以外の全segment正式OK、V1はAdv=Repetition QA method D'境界値flag×3+ASR1語差×1でHR Lock、Std=ASR1語差+D'境界flag+minimal_fallback→style gate BLOCK)を受け、**修復案B**を承認する(原稿段階の自然な言い換えによる偽陽性回避は委任_09で許可済みの範囲。Gate・閾値・HR Lockの変更/迂回は不可)。
- Bが不成功(両levelいずれかが確定しない)なら、再試行を重ねず停止し、案A(人間がV1テイクを聴いて承認)をユーザー判断候補としてFableへ返す。
- 世界設定(日本の高校、争点=「授業中だけ禁止」→「学校にいる間は使わない(持込可)」)とPersona3人維持はFable受入(一次資料: 文科省2020通知、埼玉県教委2014調査)。本文は変更しない(V1英語の言い換えのみ。日本語稿は意味が変わらない範囲で対応する最小修正のみ可)。

## 2. 作業
### T-0 記録・予算(API 0)
- 委任文逐語保存 `docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_委任_10.md`(抽出toolが無ければ手で逐語保存し末尾に注記)。
- ACTIVE_TASK Family Y行(自分の行のみ): 委任_10 Status=`V1_REPAIR_B_IN_PROGRESS`、上限40円、報告=`docs/pm/RESULT_PACKET_FYT7.md`。
- 予算見積(開始前): V1 Std/Adv各≤3テイク+ASR+Gate+組立、合計見込みと残予算(Y累計約315.7円/600円、当日約825円/1,400円)を`BUDGET_PLAN_02.md`へ。累計32円到達で見込み再計算、40円超過見込みなら停止前にFableへ。
### T-1 V1英語の言い換え(API 0〜小)
- D'がflagした反復区間(`in the…in the`、`I want…I don't want` 等、`V1_REPAIR_PLAN_01.md`のflag位置)と、ASR誤転写した語(can/could、it/I)の前後を、**意味・感情・人物差を変えずに**言い換える(Std/Adv両方)。言い換え前後の差分を`TRIAL_03/V1_REWRITE_DIFF_01.md`に記録(目的=偽陽性回避、意味不変の確認文付き)。日本語稿は変更不要(英語表現の調整で意味が変わらないため)。
- Std/Adv難易度差を維持(語数/文の目安: Std 約11、Adv 約15)。
### T-2 V1再生成→Gate→組立(TTS直列化: 他行の「有料run(TTS)進行中」待機、最大30分。自行にflag記載/終了更新)
- V1のみ Std/Adv を再生成(各level 最大3テイク。4テイク目は行わない)。正式Gate(Repetition QA/ASR/Y style gate含む)を迂回しない。Stdは`minimal_fallback`に落とさず正規経路で確定させる(fallbackで確定した場合はstyle gate BLOCKになるため、確定扱いにしない)。
- 両level確定→Std/Adv全編通し音声を組立(V1以外の確定済みsegmentは再利用)→試聴ページ更新(全編+パート別、Key Phraseも掲載[前回途中経過版は未掲載]、「人間確認待ち」表示を解除)→page_verify(Playwright実再生、全編・パート別、console error 0)→`PLAY_VERIFY_04.md`。
- 片levelでもHR Lockが残ったら: 停止し、残りの作業(確定したlevelの通し音声・ページ更新・資料)を進めてから報告(迂回なし)。
### T-3 評価資料・SSOT・Git
- `TRIAL_03_RESULT_02.md`: ユーザー§6受入条件1〜9の自己チェック(各項目に証跡path)、V1修復の経緯、Std/Adv難易度指標、残存リスク、自己判定(VALIDATED候補/USER_DECISION_REQUIRED候補)。
- `AUDIO_QA_04.md`(V1テイクの正式Gate結果、再利用/再生成の別)。
- OPEN-463/469/470追記。DECISION_LOG(Fableの修復案B承認)。CURRENT_SPEC変更なし。
- Git: secret scan(`Glob **/secret_scan*`、無ければcached差分のkey/tokenパターンGrep 0件)→`git diff --cached --name-status`(他agentのstaged変更を巻き込まない)→`git commit --only -- <path…>`→`git push origin HEAD:main`。wav/raw_usage_log追跡禁止。raw URL添付。
- 報告=`docs/pm/RESULT_PACKET_FYT7.md`: (1)V1修復結果(言い換え内容・テイク数・Gate結果) (2)完成版試聴URL Std/Adv(全編・パート別) (3)品質評価(受入条件1〜9、Std/Adv難易度差) (4)QCD(本委任費用・Y累計・当日累計・量産単価見込み・制作時間、出典) (5)Status・Open Items。使用model名・最新か。

## 3. 禁止・制約
X/Z Production code/Prompt/flag/閾値変更0。既存er110 module無変更(DEV trial03 module内の変更のみ)。R1/R2処理追加なし。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止。PIDは自分のもののみ(26-6)。Gate/HR Lock/STOP迂回禁止。有料runの再起動は本委任のテイク上限内のみ。`TTS_EXECUTION_MODE=STANDARD`。秘密情報出力禁止。上限40円無断超過禁止。
## 4. handback
完了/HR Lock残存/予算警告/blocker のいずれかで。途中経過は小刻みに返さない。