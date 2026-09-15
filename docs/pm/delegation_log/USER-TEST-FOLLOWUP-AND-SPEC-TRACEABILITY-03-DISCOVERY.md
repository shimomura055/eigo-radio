## 管理ID

USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-DISCOVERY(Discovery A2再生成+音声再完成/B1 Human Review player)
並行タスク衝突確認: 並行して Family C(er013)、Trend命名整理(`.../trend/`)、仕様追跡調査(docs/pm配下の調査文書のみ)が走る。本タスクは`er014_output/four_type_observation_01/discovery/`配下のみを書き、Git・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_FU03_DISCOVERY.md`(新規)。

## 性質/到達上限Status/禁止事項

### Part A: Discovery B1 Human Review用player(API不使用、先に実施)
- ユーザー判断: B1(内部ID b1b)の`full_story_part2`は追加TTS再生成をしない。既存attempt音声を人間が聞いて内容一致を確認し承認する。そのためのHuman Review用playerを作る。
- 要件: `discovery/audio/b1b/human_review_player.html`(標準Audio Review Playerを再利用・拡張、相対パスのみ、`file:///`禁止)に、対象segment `full_story_part2`について同じ場所に (1) canonical script(2文分割版の確定本文該当部)、(2) ASR transcript(最終attemptの`asr_text`)、(3) 差分箇所(語単位diff、例「In a study ↔ In one study」「Japan–United States ↔ Japan/U.S.」を`<mark>`等でハイライト)、(4) 問題音声のseek位置(差分語の推定時刻: attempt音声のduration×文字位置比で概算し「約xx秒付近」と明記、概算であることを表示)、(5) 個別segment再生(attempt音声をmp3化して`web/review/full_story_part2_attemptN.mp3`、最終attemptを既定・他attemptも選択可)、を表示。音声・canonical本文は変更しない。ユーザー向け表示名は「**B1**」(B1Bは内部IDとしてのみ注記)。
- 完成判定はユーザー試聴後(本タスクではSTOPでも完成でもなく「Human Review READY」として報告)。

### Part B: Discovery A2再生成(ユーザー判断: 現604語版は不採用「長すぎて聞いていて疲れる」)
- 方式選定: 既存Discovery S2正式Production path(`er003_discovery_focus_staged_production_01.run_one_pattern_staged_discovery_focus`、editorial_mode="discovery_focus_staged"、同一Ledger `discovery/research/verified_fact_ledger.txt`、Stage構成無変更)で**再生成**する(604語版の圧縮編集はLocal Rewriteの多段人手編集となりFact Safety/コスト両面で高リスクのため不採用。理由をRESULT_PACKETに記載)。**Prompt変更禁止**(length指示の追加も禁止)。既存soft target 280〜420語を「意識する」=生成結果のword countを毎回記録し、**最大2回**の生成で目安に近い方(かつ全QA PASS)を採用候補にする。両方とも500語以上なら、採用せずSTOP(選択肢: 3回目/圧縮編集/Prompt length指示の正式検討)。
- 既存正式経路どおり確認: Focus維持(Stage 1 Focus)/Main Story・Pointsの役割/No Jargon(前回のjargon scanを再実行、ヒットがあれば既存rewrite経路で修正)/Fact Checker/Ledger Deviation/Point Overlap・Point Value/Directional/retry・fallback整合。結果を`discovery/a2_v2/`へ(旧604語版は`discovery/a2/`のまま履歴保持、`a2_before_regeneration_604w/`としてコピー退避)。採用候補確定後、canonical A2=`discovery/a2/article.md`と`reader_facing_article.txt`を新版へ差し替え(旧版パスを記録)。
- **Word-count報告ルール(ユーザー正式決定)**: A2記事が280語以下または500語以上の場合、完成報告時に必ず明示(hard gateではない、生成停止しない)。本タスクの全生成でword countを記録し、該当時は`word_count_flag`を明記。
- Cross-Level: B1(2文分割版)との突合表を再生成(最終テキスト引用)。

### Part C: Discovery A2音声再完成
- 旧604語版の音声(`discovery/audio/a2/`)は再利用しない(`discovery/audio/a2_604w_old/`へ移動し履歴保持、playerは「旧版・最新候補ではない」注記)。新canonical A2に対し、Key Phrase再選定(既存正式経路、入口再呼び出し最大3回)、Support(Preview/Comment)再生成、TTS、Assembly、Audio Validation Gate(緩和禁止)、mp3、標準player(`discovery/audio/a2/player.html`、相対パス、Title/level=A2、word count表示)、article/audio consistency、`web_delivery.json`。TTS Human Review Lock到達時は`approve_regenerate()`禁止でSTOP。
- 費用上限: Part A ¥0/Part B ¥120(生成最大2回+QA)/Part C ¥60。合計¥180。段階ごとに次段階見込み込みで事前判定。**費用は「開発・Trial/検証費」と「Production 1生成セット総原価」を分けて記録**: 604語版は不採用のためその生成費は「不採用run(参考)」、新A2の生成+QA+Key Phrase+音声化はProduction総原価へ加算(既存累計¥606.08に加算、推定合算禁止・ログ未記録分は「未記録」と明記)。
- 禁止: Prompt変更/length指示追加/Validator変更/Gate緩和/retry上限変更/`approve_regenerate()`/B1Bの音声・本文変更/Production(er003/er006/er011)コード変更/`.gitignore`変更/Git commit・push/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件: 2回とも500語以上/Fact Checker FAILが既存rewrite経路で解消しない/新仕様が必要/費用上限超過見込み/TTS Human Review Lock到達/技術的にWeb配信不可。STOP時は「何を試したか/何が残ったか/ユーザーに必要な判断」を提示。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文・要点)

> Discovery A2: 現604語版は不採用(長すぎて聞いていて疲れる)。記事自体を作り直す。既存Discovery S2正式Production pathで再生成。目安280〜420語を意識、hard capにしない。圧縮編集か再生成かは既存設計との整合・Fact Safety・コストで最小リスク方式を選ぶ。Focusを壊さない/Main Story・Pointsの役割維持/No Jargon/Fact Checker/Ledger Deviation/Point Overlap・Value/Directional/retry・fallback整合。Word-count報告ルール: 280語以下・500語以上は完成報告時に必ず明示(hard gateでも生成停止でもない)。Audio: 旧604語版音声を再利用せず、新canonicalにKey Phrase再選定/Support再生成/TTS/Assembly/Audio Validation/Web playerまで再完成。旧playerは履歴として残すが最新候補として提示しない。
> Discovery B1: 追加TTS再生成はしない。既存attempt音声を人間が聞いて確認し承認。Human Review用player: canonical script/ASR transcript/差分箇所/問題音声のseek位置/個別segment再生を同じ場所に表示、差分はハイライト。音声・canonical本文は変更しない。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_FIX02_DISCOVERY.md` 全文(B1B最終attempt・確定本文・lock状態)。
2. `er014_output/four_type_observation_01/discovery/audio/b1b/audit/review_lock_state.json`: Grep `"segment_id": "full_story_part2"` -A 60 → 最終lockエントリのattempts(asr_text・attempt_audio_path)のみ。
3. `er014_output/four_type_observation_01/discovery/run_discovery_a2.py` 全文(初回A2生成driver: S2正式pathの呼び出し・引数・出力構造)。`er003_discovery_focus_staged_production_01.py`: Grep `^def run_one_pattern_staged_discovery_focus|editorial_mode|ledger|out_dir|STAGE1_MAX_REGENERATIONS|POINT_OVERLAP` → 入口・引数のみ。
4. `er014_output/four_type_observation_01/discovery/run_discovery_fix_b1b_kp.py`: Grep `^def |JARGON_PATTERNS|jargon_scan|run_final_qa` → jargon scan・final QA関数(再利用)。
5. `er014_output/four_type_observation_01/discovery/run_discovery_audio_completion.py`・`_3.py`: Grep `^def |argparse|add_argument` → A2音声化経路・Assembly・player・mp3関数(再利用)。
6. `audio_review_player.py`: Grep `^def |src=|title|level|note|extra_html|sections` → 拡張ポイント。
7. `er014_output/four_type_observation_01/discovery/production_set_cost.json` 全文。
8. `CURRENT_SPEC.md`: Grep `Discovery Focus S2` → 経路の正式定義行のみ(editorial_mode名・opt-in条件の確認)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- Part A出力: `discovery/audio/b1b/human_review_player.html`、`discovery/audio/b1b/web/review/full_story_part2_attempt*.mp3`、`discovery/audio/b1b/human_review_diff.json`(canonical/ASR/diff/推定seek秒)。
- Part B出力: `discovery/a2_v2/attempt1/`・`attempt2/`(各: article.md、QA JSON、word_count.json、jargon_scan)、`discovery/a2_before_regeneration_604w/`(退避)、`discovery/a2/`(採用版へ差し替え)、`reader_facing_article.txt`(同期)、`cross_level_consistency.md`(再生成)、`discovery/a2_regeneration_log.md`(方式選定理由・各attemptのword count・QA・採用判断・word_count_flag)。
- Part C出力: `discovery/audio/a2_604w_old/`(旧移動)、`discovery/audio/a2/`(新: key_phrases/、narration/、assembled/、audio_validation.json、player.html、web/episode.mp3、web/segments/、article_audio_consistency.json)、`discovery/audio/web_delivery.json`(更新)、`discovery/key_phrases/a2/`(新版へ差し替え、旧は`a2_604w_old/`)。
- 共通: `discovery/production_set_cost.json`(開発・Trial費/Production総原価を分離して更新)、`progress_log.md`1行。driver: `discovery/run_discovery_a2_regen_fu03.py`、`discovery/build_b1_human_review_player.py`。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-DISCOVERY.md --json-out docs\pm\delegation_log\USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-DISCOVERY_check.json`
2. Part A: `.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\build_b1_human_review_player.py`
3. Part B: `.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\run_discovery_a2_regen_fu03.py --max-attempts 2 --budget-jpy 120`
4. Part C: `.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\run_discovery_a2_regen_fu03.py --audio --budget-jpy 60`
5. 確認: `Select-String -Path er014_output\four_type_observation_01\discovery\audio\a2\player.html,er014_output\four_type_observation_01\discovery\audio\b1b\human_review_player.html -Pattern "file:///|C:\\" | Measure-Object -Line`(0件)、`git check-ignore -v er014_output/four_type_observation_01/discovery/audio/a2/web/episode.mp3`(exit 1)
(回帰不要: Productionコード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-135末尾追記案(A2再生成結果・word count・flag、B1 Human Review READY)、OPEN-153追記案(B1は人間試聴承認方式へ)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補一覧(サイズ付き、wav除外・mp3必須)」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FU03_DISCOVERY.md`に: A) Human Review player(パス、表示要素、diff一覧、推定seek秒、mp3一覧、予定URL `https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/discovery/audio/b1b/human_review_player.html`)、B) 方式選定理由、attemptごとのword count(本文/見出し込み)・QA結果(Fact Checker/Ledger Deviation/Point Overlap・Value/Directional/No Jargon)・retry/fallback、採用版とword_count_flag(≤280/≥500の該当有無を必ず明記)、Focus/Main Story/Points役割維持の確認、Cross-Level、C) Key Phrase 5件・Support一覧・TTS attempt・Audio Validation・duration・mp3/player/予定URL・article/audio consistency、旧版の履歴保持先、D) 費用: 開発・Trial/検証費(不採用run等)と**Discovery Production 1生成セット総原価=¥606.08+加算=¥xx.xx**を分離、E) model_id、Open Item候補、commit対象候補一覧、T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥180)
- [x] 並行タスク衝突回避あり(discovery/配下限定・Git操作なし)
