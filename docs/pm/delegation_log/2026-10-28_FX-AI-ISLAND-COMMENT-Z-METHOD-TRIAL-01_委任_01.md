管理ID: FX-AI-ISLAND-COMMENT-Z-METHOD-TRIAL-01(新規、委任_01)。Family X『AI島』Standard日本語Comment 1〜4について、現行完成版(Before)とFamily Z方式で新規生成した版(After)の文章比較Trial。Production採用ではない(VALIDATED上限)。並行して別管理ID(JA-ASR-FALSE-NG-ROOT-FIX-02)の3workerが稼働中=`docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/`・SSOT・`docs/pm/ACTIVE_TASK.md`には触らない。

**ファイル範囲**: `docs/research/FX-AI-ISLAND-COMMENT-Z-METHOD-TRIAL-01/`配下(新規)、`docs/pm/RESULT_PACKET_FXAIC1.md`、`docs/pm/delegation_log/2026-10-28_FX-AI-ISLAND-COMMENT-Z-METHOD-TRIAL-01_USER.md`(ユーザー原文を逐語保存、最初に行う)、同`_委任_01.md`(本委任文)。Production Prompt・コード・正式記事・公開ページ(`user_test/family_x_ai_island_form_01*`)・SSOT・ACTIVE_TASKは変更禁止。AI島の既存完成版と最終試聴承認待ち状態を維持。音声化禁止。Family A/B/C不可。
開始時と有料API前にstop_scope_check_01.py(rc=3で停止)。費用: 上限¥100(見積を`BUDGET_PLAN_01.md`に先に書く。生成は各Comment 1回、不要な反復・追加モデル比較禁止)。モデルはZ現行Production設定を使う。

手順(要旨): 1.METHOD_DIFF_01.md(X/Z Comment生成のPrompt逐語・file:line対照、方式差と固定項目) 2.Before取得(完成版の日本語Comment 1〜4逐語、出典・sha) 3.generate_after_01.py(DEV専用、Z方式の参照範囲・順序・前後情報をX本文へ適用、ネタバレ制御はニュース向けに変換、Comment4は合理的な場合のみ、ログをafter_generation_log_01.jsonへ) 4.COMPARISON_01.md(Before/After全文横並び、変更点、7観点のSonnet所見) 5.BUDGET_LOG_01.md、RESULT_PACKET_FXAIC1.md(≤15行) 6.git: 自分のファイルのみ明示add、git add -A禁止、commit後 git push origin HEAD:main(FFのみ)。hand-back: 方式差3〜5行、Comment1〜4 Before/After全文、所見、実費、commit sha、判断候補。
(注: 本ファイルは委任文の要旨。全文はFable側の委任メッセージが正本。)
