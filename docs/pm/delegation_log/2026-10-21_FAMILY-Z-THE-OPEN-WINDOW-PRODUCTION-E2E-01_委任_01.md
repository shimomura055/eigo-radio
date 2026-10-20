# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01 委任_01(Phase 1: 原作Seed取得・日本国内権利Gate・STORY_REGISTRY登録・Melos固有ハードコードの棚卸しと最小パラメータ化・test/Regression・mock/dry-run E2E・実走計画。**有料API呼出なし(JPY0)**。`--mode real`は委任_02[Fable照合後])。並行agentなし。

## 性質/到達上限Status/禁止事項
- 性質: 既存Family Z正式Production経路による新規作品制作の準備。新仕様Trialではない。到達Status(本委任): `PHASE1_SEED_RIGHTS_REGISTRY_DRYRUN_READY_PENDING_FABLE`。
- 費用/日次: 本日2026-10-21(JST)既使用JPY0(出典: RESULT_PACKET_MEY5/daily_dev_cost)。本委任JPY0(`--mode real`禁止。`--mode mock`/`dry-run`のみ)。
- 禁止: 有料LLM/TTS/ASR/検索API呼出・`--mode real`/Writer/TTS実行・B3Z等不採用方式の復活・新しい音声品質基準/発音判定ルール/Gate/閾値の追加・Melos run(run_e2e_01〜06)成果物の変更・Family C本体変更・現代の第三者翻訳/翻案の流用・検索要約だけをSeedにすること・`git add -A`/`-u`/stash/amend/rebase/force push/branch操作。
- Opus独立技術レビューGate(11-3): 本委任時点は非該当(準備)。ただし**Melos固有ハードコードの解消が「story別の値をSTORY_REGISTRYへ移す」以上の構造変更(stage順・Gate・Prompt文・Voice割当ロジックの変更等)を要する場合は、その変更を実装せずRESULT_PACKETに設計案として記し、Fableが条件A該当を判定する**。
- 11-8修正範囲: 範囲内=Melos固有値のパラメータ化(挙動同一、Melos側は値不変)とそのRegression。範囲外=受理面・閾値・方式の新設/拡大。
- 時間見込み: 全体60〜90分。並列化: (A)原作取得+権利ブロック作成 ∥ (B)ハードコード棚卸し+パラメータ化+test ∥ (C)E2E_PLAN・実走計画・費用見積。(D)mock/dry-run E2EはA/B完了後に直列。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01_委任_01.md`へ逐語保存(打ち直し禁止。`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <上記path>`、N=本委任文[「THE-OPEN-WINDOW」と「委任_01」を含む最新、直前191はFZAQ委任_10])し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file <上記path> --json-out <上記path>_check.json`を実行、結果をRESULT_PACKETへ1行。
T-2: 本委任はTTSなし。委任_02の実走コマンドには`--tts-execution-mode STANDARD`を明示する前提で計画を書く。
T-3: 本委任JPY0のためCapなし。委任_02の費用枠は下記「費用枠の扱い」に従う。

## ユーザー指示(原文・2026-10-21)
`docs/pm/delegation_log/2026-10-21_FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01_USER.md` へ逐語保存(先頭に `# ユーザー指示原文(2026-10-21)` と `管理ID: FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01` の2行、以降一字一句変えない。文字数・sha256を報告)。
--- 原文ここから ---
# Family Z 古典文学第2作「開いた窓」Production制作指示

**管理ID：FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01**

## 1. ユーザー正式決定

Family Zの古典文学第2作として、サキ（Saki／H. H. Munro）の **『開いた窓（The Open Window）』** を採用する。

既存のFamily Z正式Production仕様を使用し、Standard／Advancedの両レベルについて、原稿生成からTTS・Audio QA・音声組立・試聴ページ公開まで一括実施する。

**目的：原作の面白さを維持した、完成度の高い英語学習ラジオを、品質を守りながら最短・最小原価で完成させる。**

## 2. 原作・Story品質

制作前に以下を確認する。

- 原作本文を直接取得・確認する。検索結果の要約だけをSeedにしない。
- 日本国内での利用権利を確認し、既存のFamily Z権利GateをPASSする。
- 現代の第三者翻訳・翻案等を権利未確認のまま流用しない。
- `story_type=literature` とする。
- 既存のFamily Z Story品質基準を適用する。

本作で特に守るべき魅力は以下。

1. 少女が語る不気味な出来事と、その話を信じる訪問客の心理。
2. 開いた窓を中心とする伏線。
3. 人影が現れる場面の緊張感。
4. 最後の種明かしと、少女の巧みな嘘によるユーモア。

**結末の意外性を損なう先回りの説明や、過剰な解説を入れないこと。**

原作の中心Story、人物関係、因果関係、結末を維持する。短編化に必要な圧縮は許容するが、不要な創作や設定変更は行わない。

## 3. 原稿仕様

**Full Story本文の目標：400語／レベル**

- Standard：400語目安
- Advanced：400語目安
- 許容範囲：330〜470語
- 範囲外は既存仕様どおりWARNのみ。語数を理由とする不要な再生成は禁止。
- Preview／Comment／Key Phrases等は本文語数に含めない。

既存Productionの文章生成方式を使用する。

- Advanced：承認済みSolによるR0→R1→R2。
- Standard：Advanced最終稿を基に難易度調整。
- 原作の魅力、自然な英語、ストーリーとしての一貫性を重視する。
- StandardとAdvancedで、中心Storyや結末が変わらないようにする。

B3Zなど過去に不採用となった方式を復活させない。

## 4. 音声・品質仕様

**前作「走れメロス」で正式採用・配線済みのFamily Z Production仕様を継承する。**

特に以下を維持する。

- 承認済みNarrator／DialogueのVoice・Style。
- Standard英語音声の既存6%減速。Dialogueにも承認済みの生成後減速方式を適用。
- Preview／Comment／Key Phrasesの現行承認済み仕様。
- Pronunciation LedgerとAzure Phrase List（重み2.0）。
- Primary／Secondary ASRと承認済み発音同値判定。
- TTS retry → Local Rewrite → 再検証 → 必要時のみHuman Reviewの既存フロー。
- Rewrite後は必ず最新原稿を正本としてASR照合する。
- retry／fallback／regeneration／resumeでも原稿・音声の整合を維持する。

新作品に登場する固有名詞については、既存のPronunciation Ledger／読み解決機構を使用する。

**今回の制作を理由に、新しい音声品質基準や未承認の発音判定ルールを追加しないこと。**

## 5. 実行・QCD

正式Production初回経路でE2Eを実行する。

品質 ＞ 完成速度 ＞ 量産単価 ≫ 開発費用。

- 原作・権利確認と独立したProduction準備は並列化する。
- 原作・権利Gateを通過する前に有料の本文生成・TTSへ進まない。
- 既存実装・検証済み成果を再利用し、重複開発・不要なTrial・追加検索を避ける。
- 原稿生成から音声完成まで、不合理な日付分割や待機を設けない。
- 既存の品質Gate・安全条件・STOP条件をすべて維持する。
- 量産原価70円／記事セットを目標とし、実費と原価増加要因を記録する。
- 日次開発予算1,000円（JST）を遵守する。今回の個別費用上限は、既存規定・承認枠を確認し、未承認の上限を推定して適用しない。

承認済み仕様内の軽微な不具合は、原因究明から修正・再検証まで自律的に処理する。

新仕様採用、権利Gate不合格、重大品質問題、予算超過、明示STOPの場合のみ必要なユーザー判断を求める。

## 6. 完成条件

以下をすべて満たすこと。

1. 原作Seed・日本国内権利Gateの確認完了。
2. Standard／Advancedの本文・補助コンテンツ完成。
3. 原作の伏線・心理・結末・ユーモアが適切に維持されている。
4. 全必須Audio QA／Validator／Assembly Gate PASS。
5. Standardの6%減速が実際の完成音声に反映されている。
6. 正式Production runtime evidence取得。
7. Standard／Advancedの試聴ページ公開。
8. SSOT／Git反映とFable独立受入確認。

試聴ページには、完成音声の通し再生、Section別の全文原稿、Key Phrasesを掲載する。

**Production完成とユーザー試聴PASSは区別する。** 完成後は `USER_LISTENING_PENDING` とし、ユーザーの最終試聴を待つ。

## 7. 最終報告

ユーザー判断への重要度順に、以下を簡潔に報告する。

1. **完成可否とStandard／Advancedの試聴URL**
2. 原作・権利Gate結果
3. Story品質と語数、原作からの主要な編集内容
4. 音声QA・6%減速・Human Review結果
5. 実費、量産単価、所要時間
6. Production runtime evidence・Fable受入判定
7. SSOT／Git反映状況
8. 未解決事項・必要なユーザー判断（ある場合のみ）

---

**本件は既存のFamily Z仕様による新規作品制作であり、新たな仕様開発Trialではない。**

前作メロスで完成・承認されたProduction経路を最大限再利用し、『開いた窓』の意外な結末とブラックユーモアを損なわず、必要十分な品質で速やかに完成させること。
--- 原文ここまで ---

## 費用枠の扱い(Fable確認済み。推定上限を新設しない)
既存規定=CURRENT_SPEC.md「Family Z(Fiction)」節 2026-10-12追記「費用上限: 本E2Eの追加API費用上限¥300、警告¥200」(Family Z一般仕様として維持、L1604/L1614)および runner `E2E_APPROVED_BUDGET_MAX_JPY=300`/`E2E_WARN_THRESHOLD_JPY=200`。PM_GOVERNANCE 7-7(案件見積300円以下=承認済みScope内でAI自律)と整合。委任_02の実走は `--approved-budget-jpy 300 --warn-threshold-jpy 200`(既存値)で、期待実費はMelos実績から見積もる(run_e2e_02総額JPY62.83=text 22.33+TTS/ASR 40.17、`FZ_COMPLETION_PLAN_01.md` §10-5、run_e2e_06再生成27.58)。本委任ではこの見積を工程別に記す(推定で費用表を埋めず、出典のあるMelos実測を根拠にする)。

## 作業
### A. 原作Seed取得・権利Gate(ユーザー§2)
1. 原作本文を一次資料から直接取得: Saki "The Open Window"(初出 1914年、短編集 *Beasts and Super-Beasts*)。Project Gutenberg(例: *Beasts and Super-Beasts* eBook #269 等。実際のURLは取得時に確認しHTTP 200を記録)から英語原文を取得し、`er026_seeds/the_open_window/story.md`(先頭 `### The Open Window`、本文は原文を改変せず全文、出典URL・取得日時・sha256を`seed.json`へ)として保存。語数を記録。**検索要約・Wikipediaの梗概・現代翻訳は使わない**。
2. `seed.json`はMelosのseed(`er018_output/fiction_external_seed_selection_criteria_trial_02/stories/03_japanese_lit_2/seed.json`)と同一スキーマで作成(キーを増減しない。値のみ本作のもの。不明な値は推測で埋めず`null`+理由)。`story_type=literature`。Story品質基準4項目(CURRENT_SPEC「Family Z(Fiction)」節 項目3(d)と、Trial-02 REPORTの基準定義をGrep `Story品質基準`で特定)の充足を1項目ずつ根拠付きで記録(原則3項目以上)。ユーザー§2の「守るべき魅力4点」と「結末の意外性を損なわない」を、Writer入力に渡せる既存の仕組み(seed.jsonの既存フィールド/Melosで使った経路)があればそこへ記録し、無ければPrompt追加はせずE2E_PLANへ「Fable CPの照合観点」として記す(新Prompt文を作らない)。
3. rights block: `MELOS_RIGHTS_BLOCK`と同じ必須フィールド(`RIGHTS_REQUIRED_FIELDS`)を全て、**出典付き・確認日付き**で作成(`OPEN_WINDOW_RIGHTS_BLOCK`)。著者 Hector Hugh Munro(Saki)、没年月日(1916-11-14、一次/信頼できる出典URLとHTTP 200を記録)、日本国内PD根拠(旧法死後50年+連合国(英国)著作物の戦時加算の有無と計算、2018年70年化の非遡及、いずれも出典明記。法的最終判断と書かない)、source_url(Gutenberg)、米国status(記録事項: 1914年出版=米国PD、出典)、legal_use_basis(Melosと同じユーザー決定文の逐語転記、FICTION-FAMILY-Z-RIGHTS-RECHECK-01_REPORT.md §6)、gate_reference。`check_rights_gate`で必須フィールド充足をtestで確認。**権利に疑義が残る場合はSTOPして報告(有料工程へ進まない)**。
### B. STORY_REGISTRY登録とMelos固有ハードコードの棚卸し・最小パラメータ化
1. `er026_family_z_fiction_production_runner_01.py`(Grep `melos|Melos|MELOS` 13件)、`er063_family_z_audio_01.py`(16件)、`er062_family_z_writer_01.py`(15件)、および`er026`がimportする他のFamily Z module(Grep `melos` in `er06*_family_z*.py`・`tools/stop_scope_check_01.py`)の全該当箇所を表(ファイル:行/種別=コメント・定数・Prompt文・分岐・test fixture/story別化の要否)にする。
2. 要パラメータ化の定数(例: `E2E_MANAGEMENT_ID`/`E2E_THEME_TAG`/`E2E_PAGES_DIR`/`voice_keywords`/`voice_tts_names_plan`/`japanese_title_*`/Pronunciation Ledger登録・Phrase List生成の語源等)はSTORY_REGISTRYの項目として持たせ、**Melos側の値は不変・挙動同一**(既存test全PASSで担保)。Prompt文中に"Melos"が埋め込まれている場合は、Story名の差替え以上の文言変更をせず、差替え不能(Melos固有の指示)なら実装せずRESULT_PACKETで報告。
3. 本作の登録値: key=`the_open_window`、slug既定同名、`topic_title`=原題"The Open Window"(英題はFamily Zの既存運用に従う。Melosは英題を別に付与したが、本作は原題が英語なので同一)、`japanese_title_text`=「開いた窓(The Open Window)」、`japanese_title_tts`=「開いた窓」、`story_type=literature`、`trial_seed_dir`=`er026_seeds/the_open_window`、`rights_block`=上記、`voice_keywords`/`voice_tts_names_plan`=登場人物(Vera[15歳の姪]、Framton Nuttel[訪問客]、Mrs. Sappleton[叔母]。その他の端役が台詞を持つ場合はnarratorに含める既存規則に従う)に対し、**CURRENT_SPEC Z-4追記の承認済みVoice pool(Grep `Z-4|Erinome|Charon|Aoede`)の範囲内**で割当案を作る。承認poolで性別・人数が賄えない場合は新Voiceを採用せず「判断候補」として選択肢を報告。Melos用の人物名ルール(主人公のみ固有名、外国人名はFirst/Last一方のみ=Vera / Nuttel / Mrs. Sappleton の扱い)はWriter Prompt側の既存方針に従い、本作での適用案を1行で記す(Prompt変更なし)。
4. 新run root: `E2E_RUN_ROOT`配下 `the_open_window/run_e2e_01`、pages dir `user_test/family_z_open_window_01`(既存ページを上書きしない)。管理ID `FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01`をstop_scope/監査記録に使えるようにする(`tools/stop_scope_check_01.py`が管理IDをどう使うかGrepし、必要なら登録)。
5. test: 既存`er026_*_test_*.py`/`er062_*_test*`/`er063_*_test*`を`.venv\Scripts\python.exe run_project_regression.py --pattern "er026*_test_*.py"`等で全件1回実行(PASS数/FAIL数)。新規test `er026_family_z_story_registry_open_window_test_01.py`: (a)registry両storyの必須キー一致、(b)`check_rights_gate(OPEN_WINDOW_RIGHTS_BLOCK)`PASS、(c)seed.json/story.md読込、(d)Melos側の値がパラメータ化前後で同一(定数のスナップショット比較)。
### C. E2E計画書 `docs/research/FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01/E2E_PLAN_01.md`
§0 T-0/原文 §1 原作Seed・権利Gate記録(出典・計算) §2 Story品質基準充足表+守るべき魅力4点のFable CP観点 §3 ハードコード棚卸し表と変更差分(ファイル:行、Melos挙動不変の根拠) §4 Voice割当案 §5 工程表(委任_02用: `TTS_EXECUTION_MODE=STANDARD`、`.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --story the_open_window --run run_e2e_01 --mode real --stage all --approved-budget-jpy 300 --warn-threshold-jpy 200 --tts-execution-mode STANDARD`、各stage前stop_scope、Gate一覧、STOP条件[HR Lock/BLOCK/rc≠0は再起動禁止26節/権利/予算]) §6 費用見積(Melos実測出典のみ) §7 試聴ページ要件(通し再生・Section別全文原稿・Key Phrases、Melos `family_z_melos_02`と同構成) §8 mock/dry-run結果。
### D. mock/dry-run E2E(JPY0)
`--mode dry-run --stage all`と`--mode mock --stage all`を`--story the_open_window --run run_mock_01`(run_e2e_01は実走用に温存)で実行し、全stageが本作の設定で通る(seed_check PASS[語数・権利]、plan/support/kp/tts/provision/gate/assemble/pages/page_verifyのmock通過、生成されたpages dirが`family_z_open_window_01`配下、Melosのpages/runに書き込みなし)ことを確認。rc・console・出力一覧を§8へ。mockの出力は実走前に削除せず残置(gitignore対象か確認し、追跡対象ならcommitしない)。

## 事前指定Read/Grep一覧
- `er026_family_z_fiction_production_runner_01.py`: L110-230(rights/registry)、L805-835(E2E定数)、Grep `melos|Melos|MELOS|E2E_PAGES_DIR|E2E_MANAGEMENT_ID|E2E_THEME_TAG|voice_keywords|voice_tts_names_plan|japanese_title` → 該当行±10。
- `er063_family_z_audio_01.py`/`er062_family_z_writer_01.py`: Grep `melos|Melos|メロス` → 該当行±10。
- `er018_output/fiction_external_seed_selection_criteria_trial_02/stories/03_japanese_lit_2/seed.json`: 全文(スキーマ)。同`story.md`: 先頭20行(書式)。
- `CURRENT_SPEC.md`: L1457-1530(Family Z項目1〜5)、L1597-1625(2026-10-12/10-19追記)、Grep `Z-4` `Erinome` → 該当行±5。全文Read禁止。
- `docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/FZ_COMPLETION_PLAN_01.md`: §10-4〜10-7、§11(実走記録)、§13(試聴ページ)。
- `docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01/MELOS_REGEN_RUN_E2E_06_RECORD_01.md`: 全文(直近の正式run記録・費用)。
- `FICTION-FAMILY-Z-RIGHTS-RECHECK-01_REPORT.md`(Glob で所在特定): §6のみ。`docs/research/FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02*`または`FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02_REPORT.md`: Grep `Story品質基準|Gate3` → 該当節。
- `tools/stop_scope_check_01.py`: Grep `managed.id|MANAGED` → 該当行±10。
- `user_test/family_z_melos_02/index.html`: 構造確認(先頭100行)。

## 実行コマンド全文
- T-0: 上記。Regression: `.venv\Scripts\python.exe run_project_regression.py --pattern "er026*_test_*.py"`、`--pattern "er062*_test*.py"`、`--pattern "er063*_test*.py"`(存在するもののみ、globは`_test`を含める)。新規test: `.venv\Scripts\python.exe -m unittest er026_family_z_story_registry_open_window_test_01 -v`。
- dry-run/mock: `$env:TTS_EXECUTION_MODE="STANDARD"; $env:PYTHONIOENCODING="utf-8"; .venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --story the_open_window --run run_mock_01 --mode dry-run --stage all` / 同 `--mode mock`。
- stop_scope: `.venv\Scripts\python.exe tools\stop_scope_check_01.py --managed-id FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01 --run-dir er026_output\family_z_production_e2e_01\the_open_window\run_e2e_01 --out er026_output\family_z_production_e2e_01\_stop_scope_check_ow_01.json`(run-dir未作成時の挙動も記録)。
- 原文取得: `curl.exe -sSL -o <scratch>/beasts_and_super_beasts.txt <URL>`(HTTPコード記録)→該当章を抽出してstory.mdへ。取得物はscratch dirに置き、-I付きで処理。
- secret scan: `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`(hits=0必須。前委任_10で未実施だった分を本委任のscanで事後確認し、結果を記す)。

## SSOT(本委任の編集権: OPEN_ITEMS.md新規行1件[OPEN-428想定、既存最終番号をGrepして採番]・REPORT_LEDGER.md 1行・docs/pm/ACTIVE_TASK.md先頭ヘッダ。CURRENT_SPEC/DECISION_LOGは委任_02完了時にまとめて編集するため本委任では編集しない[文案のみE2E_PLAN §9へ])
- OPEN-428文案: `FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01 [PHASE1_READY_PENDING_FABLE・ユーザー2026-10-21指示(原文=...USER.md、sha)・Family Z第2作『開いた窓』(Saki)・既存Production仕様継承・費用枠=既存Family Z E2E規定¥300/警告¥200(7-7内)・実走は委任_02]`+要旨。POST_USER_VALIDATION区分。

## Git
明示add: T-0 2ファイル+USER原文+`er026_seeds/the_open_window/`+runner/er062/er063の変更+新規test+E2E_PLAN_01.md+OPEN_ITEMS.md+REPORT_LEDGER.md(+stop_scope登録があればそのファイル)。mock出力はgitignore対象なら含めない。secret scan hits=0。commit `FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01 委任_01: 原作Seed(Gutenberg)+権利ブロック+STORY_REGISTRY登録+Melos固有値パラメータ化(挙動不変、test N件PASS)+mock E2E通過+E2E_PLAN`。`git push origin HEAD:main`(force禁止、現origin/main=dc0e40811からfast-forward)。raw URL列挙。

## 報告(docs/pm/RESULT_PACKET_OW1.md 上書き)
1. 権利Gate結果(フィールド別出典、戦時加算計算、疑義の有無)。2. Seed(語数・sha・出典HTTP)とStory品質基準充足表。3. ハードコード棚卸し表・変更差分要約(ファイル:行、Melos不変の根拠=test結果)・実装せず設計案に留めた箇所。4. Voice割当案(承認pool内か、判断候補の有無)。5. Regression/新規test結果。6. dry-run/mock結果(rc・stage通過・出力dir)。7. 委任_02実走計画と費用見積(出典付き)。8. commit/push・raw URL・T-0結果・secret scan結果・JPY0確認。9. 判断候補(あれば。USER_DECISION_REQUIREDラベルは付けない)。Fableが照合後に委任_02(実走)を出す。