# Family Y Production 運用手順 OPERATIONS_01

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 / 委任_02B(2026-10-25 JST)。**本書は手順書。本委任で実行したのはmock(API 0・実費0円・有料run 0)のみ。**

入口: `er121_family_y_runner_01.py`(Zのstage frameworkと同型)。音声層: `er121_family_y_audio_01.py`。構造定数: `er121_family_y_structure_01.py`。mock部品: `er121_family_y_mock_01.py`(test/--mode mock専用)。
状態の呼称: `FAMILY_Y_PRODUCTION`(DEVの`DEV_TRIAL_ONLY`と区別)。**PRODUCTION_WIREDとは呼ばない**(下記「未接続」が残る間、実走の成否はE-1 evidenceで確認する)。

## 0. 未接続・既知のギャップ(実走前に必ず確認)

| 項目 | 状態 | 影響 | 次の一手 |
|---|---|---|---|
| text core `produce_article`(Voice/Lead/紹介/Closing+Gateの記事組立I/F) | **接続済み(委任_03、4437e98cf。runner `stage_text`が`theme_package_path=`/`reuse=`[`--reuse-manifest`]付きで呼ぶ)。以下の「未接続」記述は02B時点の履歴**(`er121_family_y_text_core_01`にはClosing lane=`produce_closing`のみ。runnerは `produce_article` を呼び、無ければ `FAMILY_Y_TEXT_CORE_NOT_CONNECTED` でSTOP) | real実走の`text` stageは止まる。mockは偽text coreで全経路PASS | 02AのDESIGN_02で記事組立I/Fを確定→adapterを接続(戻り値の期待形はrunner `stage_text` の docstring/検査に記載: title/lead/intros{voice_n}/voices{voice_n}/closing/closing_record) |
| Part 1(Vocabulary & Expressions)・Part 2(文法) | **未接続スロット**(`study_text_slots.json`に「未接続」と記録。ページには描画しない) | 学習テキストは出ない | 別案件(PART2-GRAMMAR-PRODUCTION-WIRING-01はX/Zのみ) |
| Std(A2)生成関数のPromptは「In one lineを保つ」文を含む(X承認済み・無変更) | Yの入力はIOLなし。`must_fix`欄で「IOLを足すな」を1文明示し、出力にIOLがあれば契約違反として1回再試行→STOP | E-1 evidenceで実挙動を確認する必要あり(未検証) | E-1の最初のStd出力で確認 |
| KPのgloss整合Human Review事象 | Yには解消経路が未接続。事象があれば `FAMILY_Y_KP_GLOSS_HR_EVENTS` でSTOP(自動で通さない) | 発生時は止まる | 発生頻度を見て別案件 |
| Chunk TTS・中核数値v4/J2 | **Y非適用**(承認原文がX/Zのみ。YL-B08/YL-B05)。`audit/chunk_tts_decision.json`に非適用を記録 | なし | 承認時に適用コードを新設 |

## 1. 立上げ手順(推奨順)

> 【2026-10-28追記・参照のみ】新しいTheme Packageを作る前に、素材の情報源が`docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01/SOURCE_REGISTRY_01.md`で「条件付き利用可能」以上であることと、その条件(逐語転載なし・低負荷・個人情報を取り込まない等)を確認する。登録は継続利用の承認ではなく、新しい収集方式のProduction採用はユーザー承認が必要。小町・知恵袋由来の素材を含む既存Package(redelivery_fee)の再実行は凍結を提案中(OPEN_ITEMS参照)。

1. **STOP確認**: `py tools/stop_scope_check_01.py --managed-id FAMILY-Y-PRODUCTION-LAUNCH-01 --run-dir er121_output/family_y_production_01/<slug>/<run> --out <json>`。rc=3なら新規API呼出をせず停止して報告。
2. **dry-run**(副作用0・API 0): `py er121_family_y_runner_01.py --slug <slug> --run <run> --theme-package <theme.json>`(既定mode=dry-run)。routing登録・Voice割当・Theme Package・text core接続状態を表示。
3. **mock**(偽client・偽TTS。実APIへ出ない): `--mode mock`。出力は `<run>_mock/`。KPは`rc=4`で止まる(下記4)。
4. **real**(承認予算内のみ): `--mode real --approved-budget-jpy <N>`。`N`は案件個別Cap(**170円**、BUDGET_PLAN_03。委任_03でrunner定数を150→170へ)以下。警告閾値(既定100円)を超える見込みで新規API呼出の前にSTOP。`--ack-warn-threshold`はFable確認後のみ。**日付・stage分割で境界を回避しない**。
   - 例: `py er121_family_y_runner_01.py --mode real --slug <slug> --run run_01 --theme-package <theme.json> --approved-budget-jpy 150 --stages text,translate,support,kp`(KPでrc=4待機→下記4→同じ`--stages`の後半を**1起動**で再開)。

stage順: `seed_check → text → translate → support → kp → tts_b1b → tts_a2 → gate → assemble → pages → page_verify`。`--stages a,b,c`で複数stageを**1起動**に束ねる(STAGES順に正規化)。`--stop-after <stage>`も可。

## 2. exit code

| rc | 意味 |
|---|---|
| 0 | 正常終了 |
| 2 | 設定不備・STOP(契約違反・予算・Gate BLOCK 等。stderrに`[STOP] <原因>`) |
| 3 | STOPセンチネル(`<run>/STOP`・`STOP_ALL`・RESTART_STORM)。**自動再開しない** |
| 4 | RUN_LOCK(二重起動)**または** KP Human Review待機(stdoutに`[KP_REVIEW_PENDING]`があれば後者。失敗ではない) |
| 5 | `--clear-stop`の拒否 |

## 3. 再開(resume)・再生成

- 再開 = 同じコマンドの再実行。各stageは入力sha/出力shaが一致すれば**再利用(API 0)**。TTSは前回results(同一out_dir)のOK segmentを、Voice名が記録・一致する場合に限り再利用。
- 再生成 = `--regenerate-stage <unit>`(unit: `text, translate_b1b, translate_a2, support_b1b, support_a2, kp_b1b, kp_a2, kp_expl_b1b, tts_b1b, tts_a2`)。**親を再生成すると推移的な子孫がstale**になり、子孫は明示`--regenerate-stage`が無い限りSTOP(自動再生成しない)。例: `translate_b1b`を再生成→同一起動内の`translate_a2`はstaleでSTOP→次の起動で`--regenerate-stage translate_a2`。
- 特定segmentだけ: `--only-segments y_voice_2,...`(非選択segmentは生成せず、検証済みentryは引継ぎ)。
- **完成段の再実行**は1起動で: `--stages tts_b1b,tts_a2,gate,assemble,pages,page_verify`(OPEN-480: 段を分けて連続起動するとRESTART_STORMを自行発動する)。
- **RESTART_STORM**: 同一runを**5分(300秒)間に3回**起動すると、3回目で`<run>/STOP`と`RESTART_STORM_LOCK.json`を作って停止(rc=3)。解除は`py er121_family_y_runner_01.py --clear-stop --slug <slug> --run <run> --reason "<理由>"`のみ(手動削除では解除されない)。起動間隔は**5分に2回まで**を目安にし、監視ループ・自動再起動ラッパを作らない。mockも`<run>_mock`で同じ判定。
- 自分が起動したprocessが外部から停止された/原因不明のrc≠0が2回続いたら、再起動せずSTOPして報告。

## 4. KP Human Review(rc=4の扱い)

- `kp` stageは最初から`er119_kp_wiring_01.run_kp_with_review`経由。候補(最大8)生成→Humanの選択 or **明示の不在宣言**まで待機(rc=4、`kp_review_pending.json`と統合依頼書`review_request.md`を`<run>/`に出力)。両レベル(Advanced/Standard)の候補を生成してからまとめて待機。待機中は有料の後続stage(Adv解説・TTS)へ進まない。
- 確定: 依頼書の手順でHuman選択、または `--kp-review auto --kp-review-by <名> --kp-review-reason "<理由>" [--kp-review-user-ref <ref>]`(この起動のrunについて不在を明示宣言)。確定後、**同じ`--stages`**で再実行(候補shaが一致すれば再選定せずAPI 0)。
- 確定後にKP集合が変わると`kp_*`の入力shaが変わり、`kp_expl_b1b`→`tts_*`がstale。案内に従い`--regenerate-stage kp_expl_b1b`を1回だけ明示して再開。

## 5. 案B固定記事の扱い(redelivery_fee)

- 案B本文は text core の**固定registry**(`FIXED_CLOSING_REGISTRY`)で、slug=`redelivery_fee` かつ Theme Package sha・Voice R0 sha が登録時と一致する場合**のみ**注入される(他記事へ流用不可。sha不一致は注入せずSTOP)。runner側は`text_records.json`の`closing_record`(source=`fixed_user_approved` / `general_prompt_02`)を**そのまま最終成果物(`final_manifest.json`)に記録**するだけで、案Bか一般化かを選択・上書きしない。
- 一般化経路(Prompt 02)の実走evidenceは**別記事(例: SNS)**で取る(受入条件3)。案B記事のE-1は固定注入の経路確認であり、一般化経路の受入根拠にならない(`closing_record.general_method_used`で区別)。
- 案Bの Leakage Gate は既存PASS記録を再利用する場合にprompt sha一致を要求(M-1でpromptが変わっていれば再判定=有料)。

## 6. 成果物・失敗終了時の状態

- 成功: `<run>/final_manifest.json`(path・実model_id/routing_key/response_id/prompt sha・closing_record・費用)、`<run>/{b1b,a2}/assembled/Family_Y_<SLUG>_{B1,A2}.wav`、`<run>/pages/index.html`(+`audio/`)。**ページの出力先は`<run>/pages`(公開dirではない)**。公開(`docs/`等への配置)は別手順で、配置前に `py -I tools/user_test_page_standard_check_01.py --page <index.html>` と `py -I tools/y_page_notice_check_01.py --page <index.html>` が共にrc=0であること。X/Zページは `y_page_notice_check_01.py --expect none` でrc=0(注意書きが出ていない)。
- 失敗/STOP/rc=4: 途中までの来歴(`provenance.json`)・`e2e_stage_log.jsonl`・生成済みstage出力(`text/`,`translate/`,`support/`,`key_phrases/`)が`<run>/`に残る。契約違反の英訳・Gate BLOCKの音声は**成果物として残さない/組み立てない**(`STOP`原因はstderr、`gate_summary.json`/`assemble_summary.json`にBLOCK理由)。本文を手で直さない。
- 注意書き(AI編集の告知)は**ページ本文外のみ**。音声(ナレーション)に入れない: `text`/`support`で`AI_ANNOUNCE`系の語を検出したらSTOP(Lead/紹介の再生成で対処)。

## 7. test(API 0・network遮断)

- `py -m pytest -q er121_family_y_runner_01_test_01.py er121_family_y_structure_match_test_01.py`(35+24件)。
- X/Z回帰: `er019*/er026*/er062*/er063*/er103*/er109*/er006*/er020*`関連(結果は`RESULT_PACKET_YPL2B.md`)。

## 8. 委任_03で判明した運用上の注意(E-1/E-3 evidenceより、詳細=EVIDENCE_01.md)
- 宅配(案B)の起動例: `--theme-package docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json --reuse-manifest docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/redelivery_fee_reuse_01.json`(registryのTheme Package sha `f0d0af36…`はこのfile bytes)。凍結file(Theme Package/R0/Prompt)は`.gitattributes`で`-text`(改行変換なし)。
- KP不在宣言の例: `py er119_kp_human_review_cli_01.py declare-absent --runs <run_dir> --by "<名前>" --user-ref "<ユーザー発言の参照>" --reason "<理由>"`(AI名義は`--user-ref`必須)。rc=4後に宣言→**同じ制作コマンドを再実行**。
- TTSが1 segmentで上限3回に達するとER-011のHR Lock(`HUMAN_REVIEW_LOCKED`)になり、再起動(`--regenerate-stage tts_a2`を付けても)では再生成されず、Gateが`FAMILY_Y_GATE_BLOCK`でrc=2。解除は`er011_human_review_lock_01.approve_regenerate()`(ユーザー承認)のみ。回避しない。
- 共有working treeを他agentが編集中の有料runは、codeが途中で変わりうる(import済みmoduleは影響なし・未import moduleは新codeを読む)。有料run前に`git status`で`er121_*`が未commit変更でないことを確認する。
