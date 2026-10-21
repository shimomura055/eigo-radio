# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01 委任_01b(話者roster/Voice表のstory別化[Fable判定: 11-8範囲内の是正・Opus条件A非該当]→test/mock→**real run text工程のみ**(`--stop-after std_adjust`)→Fable CP材料)。並行agent: `FAMILY-X-WRITER-DETECTIVE-WORD-AVOIDANCE-TRIAL-01 委任_01`(er086*/er019 run_mey_02読取/user_test/writer_detective_trial_01/OPEN_ITEMS末尾新規行/REPORT_LEDGER)。本委任はFamily Z module(er026/er062/er063)・`the_open_window`配下・E2E_PLAN_01.md・OPEN-428行・REPORT_LEDGER 1行・ACTIVE_TASK先頭のみ編集。共有プロトコル(編集直前git status/再Grep、自分の行のみ、即add/commit、index.lockは30秒待ち、`git diff --cached --stat`で混入確認)。

## Fable判定(委任_01 RESULT_PACKET_OW1照合結果。転記・実施すること)
1. **話者roster story別化=実施**。根拠: Family Z仕様は一般仕様(CURRENT_SPEC 2026-10-12追記「走れメロス個別例外ではない」)であり、`SPEAKERS`/`Z_VOICE_KEYWORDS`/`ATTR_USER_TMPL`のroster文・schema enum/Voice表/`SPEAKER_ALIASES`がMelos固定なのは仕様文と実装の乖離(11-8 T2相当)。是正=registryへ値を移しstory_keyで解決、**Melos出力はバイト同一**(Snapshot test)。stage順・Gate・判定ロジック・Prompt文の構造は変えない(roster行の名前列挙と`{main_character}`等の差替えのみ)。→ Opus条件A非該当。
2. **Lint config値追加(STORY_LINT_CONFIG["the_open_window"] forbidden_names/spoiler)=承認**(既存機構へのstory別値追加。受理面の新設ではない)。ただし語彙は結末のネタバレ防止に必要な最小限(叔母の夫/弟の帰還・「作り話/嘘/romance at short notice」系の結末語)に留め、一般語は入れない。最終リストをE2E_PLAN §3へ。
3. **Mrs. SappletonのVoice=ユーザー判断待ち(D候補)**。本委任ではVoice表に`mrs_sappleton`を**placeholder(未割当=plan stageでfail-closed)**として登録し、`--stop-after std_adjust`で止めるため本委任中はVoice不要。TTS/plan以降は委任_02。
4. **人物名方針**: 固有名=主人公Framton Nuttel(Writer Prompt既存方針「主人公のみ固有名」。外国人名ルール=Nuttel または Framton の一方。Melos同様First/Lastどちらかに統一し、Writerの出力に従う)。Vera/Mrs. Sappleton/Ronnieは役割語(the niece/the girl、her aunt/Mrs. Sappleton?)→ 既存Prompt方針に従い**Prompt文は変更しない**。Writer出力でVeraが固有名で出た場合はWARN記録のみ(`NAME_RULE_NOTE`既存)。
5. **起動計画(Fable明示許可)**: 本委任で有料runを1回起動: `--mode real --stage all --stop-after std_adjust`(見積JPY約22〜30=writer 22+std_adjust 8、出典run_e2e_02実測)。これは計画的な`--stop-after`であり26節の「失敗後の再起動」ではない。委任_02での同run resume(`--stage all`、残stage)もFableが本委任文で事前許可する(委任_02で再掲)。rc≠0・STOP sentinel・RUN_LOCK残置等の異常時は再起動せず報告。

## 性質/到達上限Status/禁止事項
- 到達Status: `TEXT_STAGES_DONE_PENDING_FABLE_CP(roster story別化済み・Std/Adv本文生成済み・plan以降未実行)`。
- 費用/日次: 本日2026-10-21既使用=開始時に`daily_dev_cost_01.py --date 2026-10-21`で確認(並行のDetective Trialが約JPY50を使う見込み)。本委任見積JPY22〜30。承認区分C。T-3: 上限¥300/警告¥200(既存Family Z E2E規定、runner定数)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 禁止: `std_adjust`より先のstage実行(plan/support/kp/TTS等)・新Voice採用・新Prompt文/Gate/閾値の追加・B3Z等の復活・Melos run/値の変更・`--regenerate-stage`による語数合わせ(語数は330〜470目安、範囲外WARNのみ)・`git add -A`/`-u`/stash/amend/rebase/force push/branch操作。
- 時間見込み: roster実装+test+mock 45〜60分 → real text run 10〜15分 → CP材料整理 15分。並列化: roster実装中にCP材料テンプレ(E2E_PLAN §10)を用意。real runは実装完了・全test PASS後に直列。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01_委任_01b.md`へ逐語保存(打ち直し禁止。`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <上記path>`、N=本委任文[「委任_01b」を含む最新。直前は194 Detective Trial/193 E2E-02 委任_05])し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file <上記path> --json-out <上記path>_check.json`を実行、結果をRESULT_PACKETへ1行。
T-2: 本委任はTTS stageを実行しないが、runnerコマンドには`TTS_EXECUTION_MODE=STANDARD`と`--tts-execution-mode STANDARD`を明示する。T-2追記4点は委任_02(TTS)で適用。

## 作業
### A. 話者roster/Voice表のstory別化(E2E_PLAN_01.md §3-C設計案に従う)
1. `er062_family_z_structure_01.py:21,24-28`(`SPEAKERS`/`Z_VOICE_KEYWORDS`)、`er062_family_z_writer_01.py:199-212,221`(`ATTR_USER_TMPL` roster文・schema enum)、`er063_family_z_audio_01.py:343-360`(Voice表・`SPEAKER_ALIASES`)を、`er026` `STORY_REGISTRY[story]`の`speakers`/`speaker_roster_text`/`voice_keywords`/`voice_tts_names_plan`/`speaker_aliases`から解決する形へ。既定(引数省略時)はMelos従来値=バイト同一。Melos値の出所はregistry一箇所にし重複定義を残さない(旧定数はMelos値を参照する互換aliasとして残してよいが、二重定義でドリフトしないようtestで同一性固定)。
2. 本作のroster: `narrator`、`framton`(主人公、Voice Algieba)、`vera`(Erinome)、`mrs_sappleton`(**placeholder=None、割当はユーザー判断後**)、`other`(叔母の夫・弟・Ronnie等の男性端役=Charon、歌声含む)。keywordsは原文/Writer出力で想定される呼称(Framton/Nuttel/the visitor、Vera/the niece/the girl、Mrs. Sappleton/the aunt、Ronnie/brother/husband)。
3. plan stageで`mrs_sappleton`のVoice未割当ならfail-closedで明示エラー(既存のfail-closed様式に合わせる。新Gateではなく値欠落の検出)になることをmockで確認(本委任ではplanを実行しないので、test/mockでの確認のみ)。
4. test: 新規`er062_family_z_speaker_roster_story_test_01.py`(Melosバイト同一Snapshot[ATTR_USER_TMPL展開結果・SPEAKERS・keywords・Voice表・aliases]/本作rosterの解決/未割当Voiceのfail-closed)。既存`er062*_test*.py` 79・`er063*_test*.py` 84・`er026*_test_*.py` 129を**逐次**で全件1回(mockと並列にしない)。
5. mock: `--story the_open_window --run run_mock_02 --mode mock --stage all`がrc=0(timeoutは十分長く、page_verifyの約160秒を見込む)、`--story melos --run run_mock_02 --mode mock --stage all`もrc=0でMelos出力が従来と同一(Writer fixtureは内蔵のため配管確認)。
### B. real run(text工程のみ)
1. 直前: `tools\stop_scope_check_01.py --managed-id FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01 --run-dir er026_output\family_z_production_e2e_01\the_open_window\run_e2e_01 --out er026_output\family_z_production_e2e_01\_stop_scope_check_ow_02.json`(rc=3なら中止)。`daily_dev_cost_01.py --date 2026-10-21`記録。`run_e2e_01`が未作成であること。
2. 実行: `$env:TTS_EXECUTION_MODE="STANDARD"; $env:PYTHONIOENCODING="utf-8"; .venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --story the_open_window --run run_e2e_01 --mode real --stage all --stop-after std_adjust --approved-budget-jpy 300 --warn-threshold-jpy 200 --tts-execution-mode STANDARD`(console→`run_e2e_01/console_text_01b.txt`)。rc・stage結果・費用(cost_log.jsonl)・LLM呼出数・model_id(Sol)・retry/WARN(語数・NAME_RULE_NOTE・構造)を記録。rc≠0なら再起動せず報告。
3. CP材料(E2E_PLAN_01.md §10): Adv R2最終稿とStd調整稿の全文(語数付き)、3分割の各Part語数比(20〜45%条件)、ユーザー§2「守るべき魅力4点」の対応箇所(本文引用: ①少女の語りと訪問客の心理 ②開いた窓の伏線 ③人影の緊張 ④種明かしと嘘のユーモア)、結末前の先回り説明・結末後の解説の有無、原作との主要編集(削除した脇筋・圧縮箇所・固有名の扱い)、Std/Advで中心Story・結末が同一か、Ledger外…(Family Zなので)原作に無い創作要素の有無、語数WARNの有無。**Sonnetの所見は事実・引用ベースで書き、合否はFableが判定**。
### C. 記録・SSOT
- E2E_PLAN_01.md §3-C(実装結果・test)・§10(text実走記録・CP材料)・§5(委任_02 resumeコマンド: `... --story the_open_window --run run_e2e_01 --mode real --stage all --approved-budget-jpy 300 --warn-threshold-jpy 200 --tts-execution-mode STANDARD`、Voice割当反映後)。
- OPEN-428行: Status角括弧を`[TEXT_STAGES_DONE_PENDING_FABLE_CP・roster story別化済み・Voice(Mrs. Sappleton)ユーザー判断待ち(D候補)・実費JPY<x>]`へ更新、行末に1行追記。REPORT_LEDGER 1行。ACTIVE_TASK先頭ヘッダ更新。CURRENT_SPEC/DECISION_LOGは委任_02完了時(文案をE2E_PLAN §9へ追記)。

## 事前指定Read/Grep一覧
- `docs/research/FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01/E2E_PLAN_01.md` §3-A/§3-C/§4/§5(Grep `^## |^### `で位置特定)。`docs/pm/RESULT_PACKET_OW1.md` 全文(前委任報告)。
- `er062_family_z_structure_01.py` L1-60、`er062_family_z_writer_01.py` L180-240、`er063_family_z_audio_01.py` L330-380、`er026_family_z_fiction_production_runner_01.py` L176-260(registry)・Grep `voice_keywords|voice_tts_names_plan|speakers|SPEAKER_ALIASES|Z_VOICE_KEYWORDS|ATTR_USER_TMPL` → 使用箇所±10。
- `er026_family_z_story_registry_open_window_test_01.py` 全文(Snapshot testの書式流用)。
- `CURRENT_SPEC.md` L1539-1553(Z-4)、L297付近(Grep `Sulafat` → 該当行±5、Voice候補poolの記述確認、委任_02の判断材料として引用)。
- `er026_output/family_z_production_e2e_01/melos/run_e2e_06/`: `cost_log.jsonl`の先頭数行(書式)・`writer/`配下のファイル名(CP材料の所在把握)。読取のみ。

## 実行コマンド全文
上記A-4/A-5/B-1/B-2のとおり(python=`.venv\Scripts\python.exe`、regression=`run_project_regression.py --pattern "er062*_test*.py"`等、globに`_test`を含める)。secret scan: `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`(hits=0必須)。

## Git
commit 2回: (1)roster story別化+test+mock結果(E2E_PLAN §3-C) `FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01 委任_01b: 話者roster/Voice表をSTORY_REGISTRYへstory別化(Melosバイト同一・test N件PASS・mock rc0)`、(2)real text run成果(run_e2e_01配下のjson/md/txt、wavなし)+E2E_PLAN §10+OPEN-428/REPORT_LEDGER `... 委任_01b: text工程実走(writer R0-R2 Sol/std_adjust、実費JPY x、語数Adv n/Std m)+Fable CP材料`。明示add。secret scan hits=0。`git push origin HEAD:main`(force禁止、並行agentで進んでいてもfast-forwardできればOK、rejectedなら報告)。raw URL列挙。

## 報告(docs/pm/RESULT_PACKET_OW2.md 上書き)
1. roster story別化の差分要約(ファイル:行)・Melos不変の根拠(Snapshot test)・既存test結果(件数)・mock結果。2. real text run: rc・stage・model_id・LLM呼出数・実費(出典)・所要時間・WARN/retry。3. CP材料の所在(E2E_PLAN §10)と要点(語数Adv/Std・Part比・魅力4点の対応有無・先回り説明/事後解説の有無・Std/Adv結末一致・原作外創作の有無。所見のみ、合否はFable)。4. 委任_02 resumeの前提(Voice割当待ち、残stage、残見積JPY27〜40)。5. commit/push・raw URL・T-0・secret scan・当日累計。6. 判断候補(USER_DECISION_REQUIREDラベルは付けない)。