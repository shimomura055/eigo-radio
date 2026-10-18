# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_19(ユーザー2026-10-18指示: 「走れメロス」試聴ページを承認済み標準フォーマットへ是正+Preview生成仕様のread-only確認+共通フォーマットRegression。**JPY0目標、記事再生成・TTS再生成禁止**)。日付: 2026-10-18(JST)。

## 性質・到達上限Status・禁止事項
- 性質: ユーザー試聴ページ(UI)の是正とページ生成機構の共通化(X/Z/将来Y)、Regression追加、SSOT記録。音声Production仕様は不変。
- 到達上限Status: `LISTENING_PAGE_FIXED_PAGES_VERIFIED_USER_LISTENING_PENDING`(#23は保留のまま)。
- 禁止: 記事・音声の再生成(TTS/ASR/LLM呼出0)/既存mp3・wav・原稿・KP成果物の変更/音声Production仕様(Style・Voice・AUW・6%減速・Assembly)の変更/Preview生成の範囲・Prompt・順序の変更/`user_test/family_z_melos_01`(旧ページ)の変更/承認済み標準フォーマットが不明確な場合の独断代替(STOP報告)/Landing更新。
- 固定ブロック: **E-1**(承認済みユーザー試聴ページの標準=ユーザー受入済みのFamily Xページ `user_test/boredom_aggression_bape_e2e_01/index.html`(2026-10-17試聴PASS)と `user_test/coffee_fxpw_e2e_01_s3prod/index.html`(S3試聴PASS)を正本候補とし、CURRENT_SPEC/PM_GOVERNANCEをGrep `試聴ページ|user_test`で承認済みフォーマット定義の有無を確認。定義が見つからなければ「ユーザー受入済みXページの構成」を標準として採用し、その旨を記録(新仕様の創作はしない))/**D-1**(不適用)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`)/**F-1**(JPY0。有料呼出が必要になったらSTOP)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_委任_19.md`へ保存し`check_delegation_prompt.py`実行、`_check.json`保持)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZ19.md`、ACTIVE_TASK.md先頭へ新ヘッダをEdit/Writeで追記、旧ヘッダ保持、sed禁止)。
- **並行作業注意(重要)**: 同じ作業ツリーで別agentがRLCT(er082_*)とFamily X新記事(er019_output/middle_east_yemen_saudi、er019_mey_*)を並行中。(a)`docs/pm/ACTIVE_TASK.md`は編集直前に再読し自分のヘッダ1ブロックの先頭追記のみ (b)git: 自分のファイルだけ`git add <path>`、`.git/index.lock`があれば最大5分待って再試行、commit直前に`git status --porcelain`で自分の対象以外がstagedでないことを確認、pushがnon-ffなら`git pull --ff-only`後に再試行(force禁止)、conflictはSTOP報告 (c)`er082_*`・`er019_output/middle_east*`・`er019_mey_*`・`er026_output/.../run_e2e_03`の音声成果物に触れない(読み取りは可)。

## ユーザー指示原文(2026-10-18、逐語。`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_LISTENING-PAGE-FIX_USER.md`へ原文のまま保存し、文字数とsha256を報告)
(原文は上記USERファイルに保存。内容: 試聴ページ是正[Std/Adv通し再生ボタン・再生順の全スクリプト・KP英日・効果音/内部情報除去・ASR警告は補助表示・既存承認ページ踏襲・ブラウザ実確認・GitHub Pages実確認]、Preview生成仕様のread-only確認[run_support_std/adv]、再発防止[共通仕様化・Regression・SSOT記録]、STOP条件、報告項目、#23保留。)

## Fable決定(本委任で確定)
- 標準フォーマットの正本: 承認済み定義がSSOTにあればそれ、なければ**ユーザー受入済みFamily Xページ(BAPE)の構成**(各レベル: 全編通し再生(assembled音声)ボタン/再生順の全スクリプト(Preview→Full Story→KP→Comment等、効果音・内部情報なし)/Key Phrases(英語+日本語意味)/ASR警告等は折りたたみ補助表示)。ページ生成はFamily Xの生成機構(`er019_family_x_audio_production_runner_01.py` `player` stage相当のbuilder)を**共通builderとして抽出または再利用**し、Zはそれにデータ(assembled音声path・segment順序・テキスト・KP)を渡す形にする。Zの音声成果物(run_e2e_03の`assembly/Family_Z_melos_{a2,b1b}.wav`およびclip)は既存のものを使う(mp3化が必要なら無料のローカル変換のみ)。
- 受入検証の再発防止: 「ユーザー試聴ページ標準適合チェック」(通し再生ボタンの存在/スクリプト順序/KP表示/内部情報非表示/ASR警告の補助化)をpage_verify系に追加し、X/Zどちらのページでも同じcheckが走るRegressionにする。Family X側(BAPEページ)は変更しない(checkが現状PASSすることを確認)。
- Preview仕様確認(§2)はread-onlyで、`er062_family_z_writer_01.py` `run_support_std`/`run_support_adv`と正式runnerの呼出経路(stage support)の整合を報告するのみ。変更なし。
- Opusレビュー: 本件は試聴ページ(提示層)の共通化で音声Production経路に触れないため条件A対象外と判断(記録のみ)。ただし共通builder化がProduction runnerの`player`/`pages` stageの挙動(出力形式)を変える場合はその差分を明示し、Fable CPを待つ(STOP報告)。

## 事前指定Read一覧
- user_test/boredom_aggression_bape_e2e_01/index.html、user_test/family_z_melos_02/{index,standard,advanced}.html、er019_family_x_audio_production_runner_01.py(player/pages)、er026_family_z_fiction_production_runner_01.py(stage_pages/page_verify)、er063_family_z_audio_01.py(ページ生成)、er063_family_z_page_verify_01.py、er026_fz_play_verify_17.py、er019_bape_play_verify_04.py、er062_family_z_writer_01.py run_support_std/run_support_adv(read-only)

## 事前指定Grep一覧+追記位置・更新位置の手順
- CURRENT_SPEC.md: Grep `試聴ページ|user_test`→承認済みフォーマット定義の有無を確認。見つからなければ「ユーザー試聴ページ標準フォーマット(2026-10-18、X/Z/Y共通、BAPEページ構成を正本)」の節をStatus=ユーザー指示に基づく是正記録として追記(新仕様の創作ではなく既存受入済み構成の明文化であることを明記)。
- OPEN_ITEMS.md: Grep `OPEN-412`→是正記録。新規1件: `OPEN-4xx ユーザー試聴ページ標準適合check(X/Z/Y共通)`(番号は末尾最大+1、commit直前に再Grepして衝突回避)。
- DECISION_LOG.md: 末尾に委任_19エントリ。
- docs/pm/USER_DECISION_REGISTER_01.md: Grep `#23`→「修正ページ提供後に試聴判断(保留継続)」。
- docs/pm/PM_GOVERNANCE.md: Grep `Gate 7`→受入記録に「ユーザー試聴ページ標準適合」を確認項目として1行追加(運用補足)。
- docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/FZ_COMPLETION_PLAN_01.md: 「## §13 試聴ページ是正(委任_19)」追記。

## 作業(順序)
1. T-0・原文保存。2. 標準フォーマットの特定。不明確ならSTOP報告。3. Z用データ組立(既存成果物から、再生成なし)。4. 共通builderで`user_test/family_z_melos_02/`を再生成。5. 標準適合check実装+Regression(X BAPEページ・Zページの両方でPASS)。6. ローカル実再生。7. commit→push→GitHub Pages公開URLで実再生検証→evidence json保存。8. Preview仕様read-only確認を報告。9. SSOT追記→commit→push。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-18_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_委任_19.md`
- ページ再生成: APIを呼ばない無料経路(builder直接呼出)。TTS_EXECUTION_MODE=STANDARD、TTS呼出0のためbatch-reason不要、--budget 0、差分再生成なし。
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\user_test_page_standard_check_01.py --page C:\Users\tensh\eigo-radio\user_test\family_z_melos_02\index.html --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03\audit\page_standard_check_19.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er026_fz_play_verify_17.py --url https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_02/index.html --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03\audit\pages_play_evidence_19.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I -m pytest C:\Users\tensh\eigo-radio\tools\user_test_page_standard_check_01_test_01.py C:\Users\tensh\eigo-radio\er026_family_z_e2e_integration_test_01.py C:\Users\tensh\eigo-radio\er063_family_z_audio_01_test_01.py -q`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py`

## Git
- commit 1: delegation_log 2件(+_check.json)、共通builder/check/verify、test、user_test/family_z_melos_02/**、evidence json。commit 2: SSOT各種。trailer: Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>

## 報告
RESULT_PACKET_FZ19.md: 4行(整合/Production到達経路/成果物[URL・表示内容・実確認・変更ファイル・test・Preview仕様確認]/撤去残置)+判定整合+判断候補+T-0 check+自己チェック(有料0/再生成0/melos_01不変/BAPEページ不変/#23保留/並行作業ファイル不干渉)。

(注: 本ファイルの「ユーザー指示原文」「事前指定Read/Grep」「実行コマンド」「作業」節は、保存容量上の要約を含む。委任文全文の正本は呼出し元Fableの委任記録。T-0要約保存の旨をRESULT_PACKETに記載。)
