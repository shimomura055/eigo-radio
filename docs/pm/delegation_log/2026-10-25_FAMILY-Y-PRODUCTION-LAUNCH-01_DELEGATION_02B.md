管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02B(runner/audio/routing/scope laneの実装・test。**API 0・有料run 0**)。並行して委任_02A(別agent)がDESIGN_02・Closing/Gate text core(`er121_family_y_text_core_01.py`)・台帳改訂・小額evidenceを担当。**ファイル所有を厳守**(§4)。

## 0. 読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(本案件節のみ更新。02Aと同節を編集するので直前再Read・最小追記)、`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/{DESIGN_01,EXISTING_SPEC_CHECK_01,SPEC_LEDGER_01,BUDGET_PLAN_01}.md`(DESIGN_02は02Aが作成中。存在すれば優先して読む)、Z stage framework `er062_family_z_structure_01.py`(397-640: `check_stop_sentinel`/`acquire_run_lock`/`record_launch_and_check_storm`等)・`er062_family_z_writer_01.py`(ensure_stage/DEPENDENTS)、Z runner `er026_family_z_fiction_production_runner_01.py`(1839-1954 stage_kp、2173-2193、2330)、`er063_family_z_audio_01.py`(1367-1416 run_tts_stage: PNAP hook・Run Entity Table・Chunk・prune_cached・style record)、X runner `er019_family_x_audio_production_runner_01.py`(scaffold/study_text/tts/assemble/player/pages、rc=4 KP HR入口)、`er119_kp_wiring_01.py`(`run_kp_with_review`、`sc.run_key_phrases`互換、family引数)、`er006_model_routing_contract_01.py`、`er103_proper_noun_alarm_policy_01.py:42`、`er109_xz_scope_01.py:25`、Y Trial audio `er110_family_y_audio_trial_01.py`(44-50,176、Aoede直書き・alias ID・In One Line=移植しない)、`docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/{DESIGN_02,OPERATIONS_01}.md`、`docs/research/PART2-GRAMMAR-PRODUCTION-WIRING-01/DESIGN_02.md`(接続点)。

## 1. Opus条件Aレビューで確定した設計方針(Fable採用済み。詳細は02Aが`OPUS_REVIEW_01.md`/`DESIGN_02.md`へ記録)
- runnerは新規`er121_*`、Zのstage framework形式(ensure_stage・DEPENDENTS・regenerate-stage・resume)。X runner拡張・DEV昇格は不採用。Productionは`er110_*`をimportしない(DEV予算skip・patched_*・alias ID・Aoede直書き・In One Lineを持ち込まない)。
- **M-3(配線漏れ再発防止)**: 共通工程(KP配線・gloss preflight/HR/人称Gate/未評価KP検出/SRC Gate/Adv英語解説/Part 1/study組立、TTSのPNAP hook・Run Entity Table・Chunk判定・prune_cached・style record、STOP/RUN_LOCK/RESTART_STORM)は**X/Zが使う共通moduleを直接importして呼ぶ**。Y固有として新規に書くのはテキスト生成・segment計画・timeline順・role文のみ。(b)**構造一致test**: er026/er019の対応stageが呼ぶ共通module呼出しを静的抽出しer121と比較、意図的差分は台帳ID付き許可リスト(X/Zに新しい共通呼出しが増えるとYのtestが落ちる)。(c)STOP/RUN_LOCKは`er062_family_z_structure_01.py`の関数をimport、写し禁止。
- **M-4**: KPは最初から`er119_kp_wiring_01.run_kp_with_review`を呼ぶ(`sc.run_key_phrases`直呼び経路を一時的にも作らない)。XのPENDING(rc=4)/NotConfirmed(rc=4)/Inconsistent(rc=3)入口確認・`verify_selection_matches_outputs`・`part1_items`も同形。文法HR/Part 2(er120)は接続点として残す(別案件でX/Z接続後に同形で接続。runnerにstage枠と`require_fresh_part2`呼出点を用意、未接続時はskipではなく「未接続」を明示記録)。
- Y固有構成: リード/人物紹介(ナレーター)+Voice1/2/3(本人)/Tension+Closing、In One Lineなし、公開ページに注意書き「本コンテンツのVoiceは、実在する人々の意見を参考に、AIが編集・構成したものであり、特定の実在人物の発言を再現したものではありません。」(本文外)、ナレーター=Yの既存Full Story設定を読み取る(声をコードに固定しない)、Y専用segment ID新設(page・assembly・Master store keyまで網羅test、alias ID禁止)。
- Chunk TTS: Yは「除外+OPEN記録」(承認原文X/Zのみ)。Chunk判定の共通hookは呼ぶが、Y scopeでは非適用になることをtestで固定(将来承認時に設定だけで有効化できる形)。中核数値v4/J2: 明示除外。PNAP/er109 scope: Family非依存の仕組みなのでY適用(scope "Y"追加)。
- routing key(02Aが確定・DESIGN_02 §routingに表を書く。先行して以下で登録し、DESIGN_02が出たら突合): `FAMILY_Y_CLOSING_GENERATE`(gpt-6.1-sol, effort high)、`FAMILY_Y_LEAK_JUDGE`(gpt-6-luna)、`FAMILY_Y_VOICE_GENERATE`、`FAMILY_Y_VOICE_REWRITE`、`FAMILY_Y_LEAD_GENERATE`、`FAMILY_Y_PERSONA_INTRO`、`FAMILY_Y_TRANSLATE_*`(値はX定数参照+drift test)。model_id照合はer006既存の実model照合関数を流用(snapshot付きIDの誤STOP防止)。費用集計がFamilyで混ざらないこと。
- 案B固定注入・Closing生成・Gate・Voice Gateは02Aのtext coreが提供(I/F: DESIGN_02 §text core。未確定部分はrunner側でadapter関数に分離しmockでtest)。

## 2. 本委任(02B)のScope
A. `er006_model_routing_contract_01.py`へ`FAMILY_Y_*`登録(契約の列挙test更新。既存keyの値は変更しない)。
B. 共有file最小編集: `er103_proper_noun_alarm_policy_01.py`/`er109_xz_scope_01.py`のscopeへ"Y"追加(X/Zの挙動不変をtestで固定)、Y segment IDの登録先(既存の段ID定義module)にY専用IDを追加、公開ページの注意書き表示+検査tool(X/Zページには出ない静的test)。
C. 新規`er121_family_y_runner_01.py`(stage列=DESIGN_01 §3を基にM-3/M-4で修正: theme_package→voices(生成+Voice Gate、text core呼出)→lead/persona_intro→closing(一般化 or 案B固定、text core呼出)→check_closing/gate→english(翻訳)→kp(`run_kp_with_review`)→part1(b1b相当がYに存在するか=Yのレベル構成に従う。Adv限定仕様との関係はDESIGN_02に従う)→part2接続点→plan(segment計画・timeline)→tts(共通`run_tts_stage`相当の共通関数をimport)→asr/gate→assemble→pages→page_verify。各stageはensure_stage・input_sha・DEPENDENTS・`--regenerate-stage`・resume、STOP sentinel/RUN_LOCK/RESTART_STORMは`er062`からimport、rc=4待機(KP HR)と`[KP_REVIEW_PENDING]`マーカー、費用stage tag、actual model_id/routing/Prompt sha記録(`closing_record`等)、mock/dry-run modeは実APIへ到達しない(`_mock_isolation`相当)。
D. 新規`er121_family_y_audio_01.py`(segment計画: ナレーター[リード・人物紹介・Closing]とVoice1〜3の話者割当、Full Story設定の読取、Chunk hook呼出[Y非適用]、Master store key、reuse key、assembly順)。
E. test(mock、ネットワーク遮断harnessで実行、実client生成block): stage framework(regenerate/resume/STOP/LOCK/STORM)、KP HR rc=4経路、segment ID網羅(page・assembly・Master store)、注意書き、scope "Y"、routing契約(未登録key fail-closed・drift test)、**構造一致test(M-3b)**、X/Z回帰(er019/er026/er062/er063/er103/er109/er006関連)全PASS。
F. `OPERATIONS_01.md`(Y起動手順・HR操作・再開コマンド・RESTART_STORM間隔・案B固定記事の扱い)。
G. SSOT: OPEN-520へ02B進捗を最小追記(02Aと同時編集=直前再Read・最小Edit・バックアップ)。CURRENT_SPEC変更なし。
H. Git: 対象pathのみadd→`git commit --only`→`git push origin HEAD:main`(non-fast-forwardならfetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP報告)。禁止: `git add -A/-u`・amend・rebase・force・stash・reset --hard。secret grep 0件。`git status --porcelain`で意図外混入なし。
I. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_DELEGATION_02B.md`(Nは584前後、先頭「管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02B」を578〜605で走査)。

## 3. 禁止
有料API 0(test中の実client生成block+遮断harness。既存testが新入口を呼ぶ場合はmock化を先に確認=KP HR案件でmock漏れにより実LLM到達事故あり)。Production run起動0。`er110_*`のimport・変更禁止。Prompt 02・Gate基準・案B本文の変更禁止。Chunk・中核数値のY適用禁止。公開ページ・`er0XX_output/`既存成果物の変更禁止。

## 4. ファイル所有(厳守)
- 02B(本委任)が編集: `er121_family_y_runner_01.py`、`er121_family_y_audio_01.py`(+各test)、`er006`、`er103_proper_noun_alarm_policy_01.py`、`er109_xz_scope_01.py`、segment ID定義module、公開ページ注意書き関連、構造一致test、`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/OPERATIONS_01.md`、delegation_log 02B。
- 02Aが編集(読むだけ): `er121_family_y_text_core_01.py`、DESIGN_02/SPEC_LEDGER_02/BUDGET_PLAN_02/OPEN_TRACKING_02/OPUS_REVIEW_01/GATE_CALIBRATION_01/REWRITE_EVIDENCE_01、DECISION_LOG。
- 他agentが編集中(読むだけ): `er019/er026/er062/er119/er120`、KP HR・Part 2・JA ASRのdocs。er062/er063の関数は**importのみ**(変更不可)。必要な共通関数がimport不能な形(runner内直書き)の場合は、変更せず「共通化要望」として報告(次委任で該当agent完了後に抽出)。

## 5. 報告(RESULT_PACKET_YPL2B.md+口頭要約)
実装ファイル/関数・stage列・共通import一覧と許可リスト差分、test件数(新規/回帰、PASS、遮断下接続試行0)、routing登録表、共通化要望、02Aとの突合事項(I/F・routing名)、残作業(E-1〜E-5 evidenceに必要なもの)、費用0円、commit hash・raw URL、RESULT_PACKET 4行+判定整合、判断候補(27-3)。