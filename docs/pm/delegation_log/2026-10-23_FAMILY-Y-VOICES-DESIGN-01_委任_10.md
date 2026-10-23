# FAMILY-Y-VOICES-DESIGN-01 委任_10 委任文(Fable発、逐語。抽出toolなしのため手で逐語保存)

FABLE-DELEGATION-MARKER: FAMILY-Y-VOICES-DESIGN-01-委任_10-V1-REPAIR-B-AND-FULL-AUDIO-COMPLETION-20261023

# FAMILY-Y-VOICES-DESIGN-01 委任_10: 人物1(V1)音声の修復案B(英語V1の反復語句・文頭の言い換え→V1のみStd/Adv再生成)→正式Gate→Std/Adv通し音声組立→試聴ページ(`user_test/family_y_trial_03/`)完成→page_verify。DEV/Trial経路のみ、X/Z Production変更0、到達上限=VALIDATED候補(最終判定はFable)。費用上限40円(Y累計上限600円・残約284円の内。当日上限1,400円)。

## 0. 先に読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(固定ヘッダ、line 2、Family Y行)、`.claude/agents/sonnet-worker.md`、`docs/pm/RESULT_PACKET_FYT6.md`、`docs/research/FAMILY-Y-VOICES-DESIGN-01/TRIAL_03/{TRIAL_03_RESULT_01,V1_REPAIR_PLAN_01,AUDIO_QA_03,WORLD_SETTING_01,TEXT_DIFF_01,BUDGET_PLAN_01,PLAY_VERIFY_03}.md`、`docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_{USER_04,USER_04_ADDENDUM_BUDGET,委任_09B}.md`(制約継承)、`er011_output/local_rewrite_recovery/it3/b1b/local_rewrite_recovery_full_story_part1.json`、`er110_family_y_persona_trial03_01.py`、`er110_family_y_persona_audio_page_03.py`。

## 1. Fable判断
- 委任_09Bの結果(本文完成、V1以外の全segment正式OK、V1はAdv=Repetition QA method D'境界値flag×3+ASR1語差×1でHR Lock、Std=ASR1語差+D'境界flag+minimal_fallback→style gate BLOCK)を受け、**修復案B**を承認する(原稿段階の自然な言い換えによる偽陽性回避は委任_09で許可済みの範囲。Gate・閾値・HR Lockの変更/迂回は不可)。
- Bが不成功(両levelいずれかが確定しない)なら、再試行を重ねず停止し、案A(人間がV1テイクを聴いて承認)をユーザー判断候補としてFableへ返す。
- 世界設定(日本の高校、争点=「授業中だけ禁止」→「学校にいる間は使わない(持込可)」)とPersona3人維持はFable受入(一次資料: 文科省2020通知、埼玉県教委2014調査)。本文は変更しない(V1英語の言い換えのみ。日本語稿は意味が変わらない範囲で対応する最小修正のみ可)。

## 2. 作業
T-0 記録・予算 / T-1 V1英語の言い換え(Std/Adv両方、V1_REWRITE_DIFF_01.md、Std約11語/文・Adv約15語/文を維持) / T-2 V1再生成(各level最大3テイク、4テイク目なし、正式Gate迂回なし、Stdはminimal_fallback確定は確定扱いにしない)→両level確定で通し音声組立→試聴ページ更新(全編+パート別、Key Phrase掲載、「人間確認待ち」解除)→page_verify→PLAY_VERIFY_04.md。片levelHR Lock残存時は確定levelを進めて報告 / T-3 TRIAL_03_RESULT_02.md(受入条件1〜9)・AUDIO_QA_04.md・OPEN-463/469/470・DECISION_LOG・Git(secret scan、git commit --only、push、raw URL)。報告=docs/pm/RESULT_PACKET_FYT7.md。
(詳細は委任文原文のとおり。上限40円、累計32円で見込み再計算。)

## 3. 禁止・制約
X/Z Production code/Prompt/flag/閾値変更0。既存er110 module無変更(DEV trial03 module内の変更のみ)。R1/R2処理追加なし。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止。PIDは自分のもののみ(26-6)。Gate/HR Lock/STOP迂回禁止。有料runの再起動は本委任のテイク上限内のみ。`TTS_EXECUTION_MODE=STANDARD`。秘密情報出力禁止。上限40円無断超過禁止。
## 4. handback
完了/HR Lock残存/予算警告/blocker のいずれかで。途中経過は小刻みに返さない。

(注記: 本ファイルは委任文の主要部を逐語に近い形で保存し、T-0〜T-3の細目は要約。全文原本はFableの委任メッセージ。)
