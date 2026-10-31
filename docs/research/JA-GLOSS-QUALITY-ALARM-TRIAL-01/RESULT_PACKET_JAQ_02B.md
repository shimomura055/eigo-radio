# RESULT_PACKET_JAQ_02B (JA-GLOSS-QUALITY-ALARM-TRIAL-01 委任_02B)
(docs/pm/RESULT_PACKET_*.md は .gitignore:56 対象のため成果dirに保存。詳細=RESULT_02.md)

**要点**: 事前登録(TRIAL_PLAN_02 §9)どおり実施。主構成=R6(分析→判定型一括検査)/effort=medium/規則R_default/ref無効(凍結=trial/frozen_config.json)。**主合否 P-a' Precision=36.4%・30.8%(2 rep、平均33.6%)で目標80〜90%に未達**。ガードA(held-out major)7/8=87.5%通過、運用Recall 6/12=50%、P-c 3/6・2/3、誤警告 P-a' 7件・9件(共通3件)、未検査0。Status候補=**USER_DECISION_REQUIRED**。DEV試作URL=https://shimomura055.github.io/eigo-radio/user_test/dev_ja_alarm_mock_01/index.html?dev=all 。費用 **¥50.757 / Cap ¥60**(399 call、gpt-6-luna 399/399、retry 0)。止め線¥48はfinal実行中に超過(事前登録§9-6で見込み記録済み)、¥55未到達。

**原因仮説・観測値・次の一手(QDC記録材料)**: Precisionが伸びない主因=(1)有病率3.7%で正常208件のFPR 3.4〜4.3%(必要≤0.77%)、(2)Lunaが比喩喪失・定訳をminor/midと評価し(severity校正)規則で外れる→FPと見逃しが同時発生(charge・culprit・verdict[rep2])、(3)Family Z Advanced(文学)で言い換え指摘が多発(0 TP/FP 4〜5)、(4)出力の再現性が低い(FP 7→9、共通3)。前回(R1 dev P-dev 66.7%)→final 33.6%と大きく低下=devは正常44件・problem 5件と小さく過大評価(区間が広い)。次の一手の候補と自己評価: M5段2(取消0/38)・M6(ガードA未達)・R2 Prompt改善(ガードA低下)は効果なし→同方式の再試行は見込み低。本モデル限定のまま改善するなら『検査単位・追加情報の見直し』(例: 記事内の他levelや生成時メタの活用=M7はablation未実施)だが、改善見込みは低〜中、費用/Trial追加が必要。

**判定整合**: 重大NG=なし / 主因=Precision未達(有病率とFPR) / 是正対象=なし(基準は不変、技術的是正対象なし) / STOP理由=なし / 提示=可

**RESULT_PACKET 4行**
(1) 既存仕様整合: ユーザー原文 docs/pm/delegation_log/2026-10-31_JA-GLOSS-QUALITY-ALARM-TRIAL-01_USER.md:20-36(Precision80〜90%目標・別々に測定)、TRIAL_PLAN_02.md §1-2/§1-3/§3/§9(事前登録、基準途中緩和なし)、OPUS_REVIEW_01.md、凍結ラベル sha256 e98e830d…(git showで再確認、変更なし)、HR_UI_MOCK_DESIGN_01.md §2(form_logic.jsバイト同一)。
(2) Production到達経路に入る未承認機能の既定値: 追加0。Trial専用経路(docs/research/JA-GLOSS-QUALITY-ALARM-TRIAL-01/tools/jaq02b_*.py)と DEV複製(user_test/dev_ja_alarm_mock_01/、Production articles.jsonに未追記)のみ。flag新設なし。確認: 本委任のcommit群(26accac0b b381e17d0 52d61b238 62084a43a f4750d88c 8413701b7+本commit)の変更ファイルは docs/research/JA-GLOSS-QUALITY-ALARM-TRIAL-01/*・user_test/dev_ja_alarm_mock_01/*(新規)・OPEN_ITEMS.md(OPEN-636行)のみ。`grep -rl "jaq02b|JA-GLOSS-QUALITY-ALARM" er003_*.py er119_*.py er128_*.py user_test/selection_form_v3` = 0件。DEVコピー文のProduction restore()拒否=trial/mock_restore_check.json。
(3) 失敗終了時の最終成果物: 失敗終了なし(正常完了、Status候補=USER_DECISION_REQUIRED)。最終成果物=docs/research/JA-GLOSS-QUALITY-ALARM-TRIAL-01/RESULT_02.md(原文§8の8項目)・DEV試作URL・trial/(台帳・全出力)。目的要件への適合: ユーザー原文§2の6指標(Precision/Recall/誤警告件数・内容/見逃し件数・内容/重大誤訳検出/記事セット費用)を別々に実測し、目標未達を正確に報告(基準不変)。HR画面の赤字警告はDEV試作(承認操作を妨げず、Production無変更)で、運用適用には至らない(目標未達のため採用判断待ち)。
(4) 撤去・残置した規則・検査・test: Production側の撤去・残置なし(Trial専用の追加のみ)。Trial内=R2のPrompt v2(PRINCIPLES2)は不採用だがtools/jaq02b_prompts.pyに比較記録として残置(frozen_configは v1 を指す)、`confidence`列挙値は M-8照合のため `medium`→`mid` に改名。残存Grep: `grep -rn PRINCIPLES2 docs/research/JA-GLOSS-QUALITY-ALARM-TRIAL-01/tools` は prompts.py(定義)と run.py経由のみ。

**Fable裁定依頼**: (a) Status確定(USER_DECISION_REQUIREDとしてユーザー提示するか)。(b) 事前登録からの費用起因の縮退(M7・M2/M3一部effort・dev rep2・final 3rep・類型6合成確認が未実施)を許容するか。(c) 誤警告のうち境界normal(shepherd/registration等の定訳指摘)を『ラベル不変のままFP』として扱った点の確認(ラベル付け替えはしていない)。

**判断候補**(Fableが分類): [D真に新しい判断] 目標Precision80〜90%に対し実測33.6%。選択肢=A基準維持で不採用(REJECTED)/B基準・用途の見直し(警告→『確認の目安』、運用負担は小: 警告0.5〜0.6件/level・¥0.36/セット)/C別仕様の新Trial。停止根拠=TRIAL_PLAN_02.md §1-2(主合否P-a'・80%到達判定、区間下限未達は合格を断定しない)・§1-4(未達=基準を動かさずUSER_DECISION_REQUIRED)・§7。既判断(再質問しない)=モデルLuna限定・B3不採用・80〜90%目標(ユーザー基準のまま)・Fable決定(1)〜(4)。

**コミット**: 26accac0b(DEV試作)ほか上記。成果物パス=C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\7eda59a9-ca6c-4f6c-9eb5-2b973c0ca046\scratchpad\wt_jaq\docs\research\JA-GLOSS-QUALITY-ALARM-TRIAL-01\(origin/main同期後はメインツリーの docs/research/JA-GLOSS-QUALITY-ALARM-TRIAL-01/)。
