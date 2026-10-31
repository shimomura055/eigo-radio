# RESULT_PACKET PAS_01(PLAYWRIGHT-AUDIO-SAFETY-01 委任_01、API 0、2026-10-31)
disk_guard OK(66.0GB)/stop_scope rc=0/開始時の残存Playwright・observe process 0(kill対象なし)。worktree=scratchpad/wt_pwsafe(lock済み、unlockせず)。
**結論**: 原因=Playwright **WebKit**(`observe_caption_prod_01.py --browser webkit`)。mute引数が無くJSのplay()/ボタン/seekで3作品を連続再生。Chromium headlessはPlaywright既定の--mute-audioで元々無音。既定デバイス実出力peak: 旧WebKit 8.2e-4 → 修正後 2.3e-10(無音基準)。
**修正**: 共通helper `tools/playwright_safe_01.py`(無音[init scriptでmuted/volume強制+--mute-audio]/headless強制/hard timeout 600s/Job Object+atexit+signal+console ctrl handlerで子process確実終了/孤児回収/同一cmdline二重起動rc=75)。全Python 89本をimport1行置換(残存0)、生CDP mjs 10本に--mute-audio+exit hook、observe_caption_prod_01.pyに--hard-timeout-s(1800)とtry/finally。
**検証**: 単体/統合14 test OK(通常/例外/`taskkill /F`/Ctrl+Break/timeout後に子process 0)、実機observe Chromium 4 combo+WebKit 1 combo PASS、前後のPlaywright系process 0。既存er135 test 121+48 OK。
(1)既存仕様整合: `er135_enduser_page_verify_01.py:128`(Production再生検証)を含めimport行のみ置換、判定ロジック・閾値不変。`observe_caption_prod_01.py`の観測check不変(Chromium/WebKit全PASS)。PM_GOVERNANCE 26節(自起動PIDのみkill、image名一括kill禁止)と整合=helperは自processの子孫のうちms-playwright配下だけkill。
(2)未承認機能の既定値: 新規仕様なし。Production経路の挙動変化は安全装置のみ=既定で無音・600s超でrc=124・同一cmdline二重起動rc=75(確認=`grep PW_SAFE`/`FIX_01.md`3節、test済み)。音声解除は`allow_audio=True`+env`PW_SAFE_ALLOW_AUDIO=1`の二重明示のみ。
(3)失敗終了時の最終成果物: hard timeout/強制終了/例外時もbrowser子process 0(test済み)・observe.jsonは途中結果を書かず終了(従来同様)。成功時の成果物=`docs/research/PLAYWRIGHT-AUDIO-SAFETY-01/{ROOT_CAUSE_01,FIX_01,EVIDENCE_01}.md`・`evidence_01/`・`tools/playwright_safe_01*.py`。ユーザー原文4要望(原因特定/無音化/確実終了/長時間防止)に適合。未確認: 元事象の厳密な発生時刻、9記事全再走。
(4)撤去/残置: 撤去=`from playwright.sync_api import sync_playwright`直接import(`git grep`残存0、delegation_log除く)。残置=なし(旧ルール・旧検査なし)。mjsの`--headless=new`は`--mute-audio`併記で残置。
判定整合: 重大NG=なし / 主因=WebKit実再生(OPEN-640) / 是正対象=OPEN-640 / STOP理由=なし / 提示=可
判断候補: (a) `.claude/agents/sonnet-worker.md`へPlaywright helper必須の追記(案=FIX_01.md 5節)。分類=B(運用ファイルの追記でFable承認範囲、ユーザー判断ではない)。(b) 他workerが走行中のcaption wiring委任_02は、origin/main取り込み後にhelper経由へ自動で切替わる(再実行は不要、`migrate_playwright_imports_01.py`の再適用でconflict解消可)。
新規OPEN: OPEN-640=不具合修正・安全/分類=修正へ進む(同一委任内で完了)。
push: 後述の最終報告に記載(commit/push後にhashを追記)。
