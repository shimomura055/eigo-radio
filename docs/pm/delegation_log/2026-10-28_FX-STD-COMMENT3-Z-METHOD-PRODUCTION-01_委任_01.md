# FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01 委任_01(設計+実装+test、配線は次委任)

管理ID: FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01(新規)。ユーザー正式決定: Trial `FX-AI-ISLAND-COMMENT-Z-METHOD-TRIAL-01`で検証したZ方式Comment 3をFamily X Standardへ**APPROVED_FOR_PRODUCTION**(目標PRODUCTION_WIRED)。範囲=Comment 3のPrompt(役割文)と本文参照範囲の両方。Comment 1・2・4・Preview、X Advanced、Y/Zは対象外(変更禁止)。並行worker(JA-ASR-FALSE-NG-ROOT-FIX-02 委任_03)がSSOT・ACTIVE_TASKを編集中=本委任ではSSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/UDR)・ACTIVE_TASKを編集しない(次委任で行う)。Family A/B/C不可。

ファイル範囲: `docs/research/FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01/`(新規)、本ログ2件、`docs/pm/RESULT_PACKET_FXC3P1.md`、Production code(Family X Std Comment生成関連、最小限)+新規test。本委任ではProduction経路から新関数を呼ばない(配線は委任_02、Opus条件Aレビュー後)。新関数・定数・testの追加のみ。API 0(testはmock)。開始時にstop_scope_check_01.py(rc=3で停止)。

手順:
1. 設計書`WIRING_DESIGN_01.md`(Trial `METHOD_DIFF_01.md`・`generate_after_01.py`・`after_generation_log_01.json`基準): (a)Comment 3役割文=Zの既存定数`a2gen.COMMENT_2_ROLE`を無改変流用(sha/逐語でTrialと同一を示す)。(b)ニュース向け参照範囲制御(決定論・LLM不使用): Part 3の一定割合を無条件に渡さない。Trialの結論・留保語手前打切りを基本に、結果文検出(数値・比較・結果動詞)で手前打切り、段落数・語数上限を併用。0文ならPart1+Part2のみ。境界例をAI島Part3と既公開X記事2〜3本で机上確認し表にする。(c)先取り検査(事後lint): 渡さなかったPart 3由来の数値・結果語がCommentに含まれていないか決定論で検査→違反なら1回retry。2回目も違反ならPart1+Part2のみで生成し監査記録。Zの物語語彙は適用しない。(d)配線点: `er019_family_x_audio_production_runner_01.py:331-355`付近、retry/fallback/regeneration/resumeの経路をfile:lineで列挙。DEV/Trial専用script(`generate_after_01.py`)は配線に使わない。(e)監査: Comment 3の方式版・渡したPart 3範囲・lint結果・retry回数を記録。(f)Regression test計画: Comment 1/2/4/Previewの役割文・参照範囲・生成順不変、X Adv・Y/Z不変。(g)Opus条件Aレビュー依頼論点の下書き`OPUS_REVIEW_REQUEST_01.md`。
2. 実装(未配線): 新関数と定数を既存/新規moduleに追加(Production経路から未呼出)。test: 参照範囲規則の境界例、lintの正例/負例、フォールバック、Comment1/2/4/Preview不変(sha固定)。既存関連test全PASS。
3. `docs/pm/RESULT_PACKET_FXC3P1.md`(15行以内)。
4. Git: 自分のファイルのみ明示`git add`、`git add -A`禁止、SSOT・ACTIVE_TASK・他workerファイル不可。`git push origin HEAD:main`(FFのみ、force禁止)。
