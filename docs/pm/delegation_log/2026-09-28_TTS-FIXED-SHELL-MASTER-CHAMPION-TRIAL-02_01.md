# Delegation: TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02

## 管理ID

TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02(ユーザー承認済みTrial、Trialのみ)。一時ファイル `docs/pm/ACTIVE_TASK_CH2.md` / `docs/pm/RESULT_PACKET_CH2.md`(commitしない)。並行: 別Sonnet 2件(Task 1 `er042_*`/`er042_output/`/`user_test/kp_advanced_explanation_audio_trial_03/`、Task 3 `er044_*`/`er044_output/`/`user_test/tts_variable_role_style_trial_02/`/`user_test/tts_all_role_style_trial_01/`)→ これらに触れない。本タスクの所有: 新規 `er043_tts_fixed_shell_master_champion_trial_02.py`(+`_page_01.py`+`_test_01.py`)、`er043_output/tts_fixed_shell_master_champion_trial_02/`(Trial専用Master Store含む)、`user_test/fixed_shell_champion_trial_02/`、新規 `TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_REPORT.md`、`docs/pm/design_tts_fixed_shell_master_champion_trial_02.md`、delegation_log。**Production code・正式Prompt・CURRENT_SPEC・routing・Production Master Audio Store(`er006_output/master_audio_store_01/`)は一切変更しない。SSOT 4点は編集権なし(文案のみ)。削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断報告。APIキー本文表示禁止。試聴リンクはGitHub Pages。**

## 性質/到達上限Status/禁止事項

- 性質: Trial。到達上限Status: `REJECTED` / `VALIDATED` / `USER_DECISION_REQUIRED`(ユーザーが Champion を選ぶ前は `USER_DECISION_REQUIRED`。選ばれても Production wiring へ進まない=別管理ID)。
- 費用: 上限¥40(想定: 10 phrase × 新規2候補=20 segment+ASR、既存 cascade の retry 上限内)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- **実行安全(前回インシデントの再発禁止)**: `--stage all` 相当の一括実行禁止。必要 segment だけ生成。**実行前に ACTIVE_TASK へ「対象 segment 一覧/想定 TTS call 数/retry 上限(既存 cascade の値)/想定費用/Guardrail」を記録してから実行**。既存音声(Production Master、TRIAL-01 の候補音声)は reuse。Bash timeout で background 化する前に phrase 単位で分割実行。
- 禁止: 新キャッシュ機構の新設、可変 text の対象化、記事再生成、Key Phrase 再選定、Production Master Store の置換・汚染、無意味な大量生成(各 phrase 最大3候補)、新規 Role 名の新設、Style の省略表記(ページには **実際に TTS へ渡した Style Prompt 全文** を表示)。モデル比較が目的ではない(最良の完成音声を選ぶことが最優先。Flash-Lite/2.5 Pro 等の使い分けは実装側判断、根拠を設計書に記録)。ユーザー向け表記は Standard/Advanced、TTS実行は 同期実行/バッチ実行。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 は標準(全文Readは `er040_*` script の構造確認時のみ可)。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_01.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_01.md --json-out docs/pm/delegation_log/2026-09-28_TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_01.md_check.json` を実行し結果1行記録。
T-2: `TTS_EXECUTION_MODE=STANDARD` 明示、Trial専用Store(`er043_output/.../master_store/`)、`--budget-jpy 40` 明示、Production Store 書込禁止。
T-3: 上記「性質」欄の定型文に従う。

## ユーザー指示(原文)

「Task 2 — 固定フレーズ Master Champion 再Trial。目的: 固定phraseは記事ごとに生成せず、最終的にChampionをMasterとして再利用する。今回のTrialではA/B/C候補を作り、ユーザーがChampionを選ぶ。基準: A = 現行Production Masterベース。ユーザー指摘: full_story_intro 現行は発音が速すぎる。→ 少し余裕を持たせ、自然な導入にする候補を作る。One.〜Five. 現行は、One / Two が大人しめ、Three が勢い強すぎ、Five が疑問形っぽい。→ 5個セットとして、テンション/抑揚/語尾/音量/テンポ を安定させる。特にFiveを疑問形にしない。ポイント解説 現行は平板。→ もう少し自然な抑揚をつける。A/B/C: 各固定phraseについて A/B/C の3候補を作る。指摘の無かった固定phraseも、仕様は変えず同じ条件で3回生成し、ばらつきの中からユーザーが一番良いものを選べるようにする。モデル比較が目的ではない。Flash-Lite / 2.5 Pro等は実装側に委任するが、最終的に最良の完成音声を選ぶことを最優先する。Role Style比較表から除外: 固定phraseは今後Master化するため、Task 3のRole Style比較表から除外する(Welcome/Preview intro/Key Phrase intro/Full Story intro/One〜Five/ポイント解説)。固定phraseはTask 2だけで評価する。」

## Fable補足

- Existing Spec / Prior Trial Check(設計書に記録): `TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01_REPORT.md`(棚卸し10件、A/B/C 結果、num_one/two/three の失敗、揃い指標)、`er040_tts_fixed_shell_master_champion_trial_01.py`/`_page_01.py`(候補生成・ASR cascade・lameenc ページ生成を **import/流用**)、`er006_master_audio_store_01.py`(`EQUALITY_FIELDS`、style version 区別)、`er006_output/master_audio_store_01/manifest.json`(read-only、現行 Master の style 文言・model・voice)、`er033_tts_flash_lite_family_x_styles_01.py`、OPEN-222/223/226(Grep)。
- **候補設計**: 対象は TRIAL-01 棚卸しの固定 phrase 10件(EN 9+JA 1「ポイント解説」)。**A=現行 Production Master 音声をコピー再利用(新規生成なし、¥0)**。**B/C=新規生成2候補**。(i) 指摘なし phrase(welcome/preview_intro/key_phrases_intro/num_four):仕様(style 文言・model・voice)を A と同一のまま 2 回生成(ばらつき比較)。(ii) 指摘あり phrase: `full_story_intro`=少し余裕のある自然な導入(style 文言に短い pace 指示を追加、文言は設計書に逐語)、`num_one`〜`num_five`=**5個セットとして同一 style で一括生成**し、テンション/抑揚/語尾/音量/テンポの安定を狙う短い style(例: declarative, even, steady; Five を疑問形にしないための語尾指示)を B・C で 2 種類試す(文言は設計書に逐語。TRIAL-01 で Role style「brief, clear, neutral」は num_one〜three が全滅したため、その文言はそのまま使わない)、`point_explanation`(JA)=平板を避ける自然な抑揚の短い JA style を B・C で 2 種類。B/C の生成は Production と同じ生成関数を Trial Store・Trial out-dir・style 上書きで呼び、ASR 検証は Production と同じ cascade(retry 上限は既存値)。ASR 失敗が上限に達した候補は「STOPPED」として記録し、独自 retry を追加しない。
- **One〜Five の揃い**: 候補ごとに duration 幅・RMS 幅・末尾ピッチ傾向(可能なら librosa/簡易 F0 で「上昇終止=疑問形っぽさ」を数値化、無理なら省略し明記)を表にし、One→Five 連続再生 mp3 を候補ごとに作る。
- 試聴ページ: `user_test/fixed_shell_champion_trial_02/index.html`(phrase × A/B/C: 音声/model/voice/**実際に渡した Style 全文**/duration/ASR 結果/drift、One〜Five 連続再生、A=現行 Production Baseline と明記)。
- **Pages 公開確認(7項目、全て満たすまで「試聴ページ完成」と書かない)**: (1) 対象 URL HTTP 200、(2) 実ブラウザ相当で公開ページを開く(Edge/Chrome `--headless --dump-dom <URL>` で公開 DOM 取得。不可なら Pages 反映後の `curl` 本文で代替し明記)、(3) 公開 DOM に `(existing 6-role value, unchanged)` が 0 件、(4) Style Prompt 全文が公開 DOM に実表示、(5) `<audio>` 件数、(6) 各 mp3 公開 URL が 200・audio content-type・非ゼロ長・デコード可能、(7) ページ表示 Style と生成音声の Style metadata(json)が一致。404/旧 cache は別 URL を乱造せず Pages の deploy 状態を調査して報告。
- 判定案: `USER_DECISION_REQUIRED`。Sonnet は `VALIDATED` を自己宣言しない。共有 append-only ログ `er011_output/attempt_history.jsonl` への追記が起きる場合は開示(OPEN-223 同型、commit 対象外)。

## 事前指定Read一覧

- `TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01_REPORT.md`: §1-§5, §9(1-96, 126-152行)
- `er040_tts_fixed_shell_master_champion_trial_01.py`: Grep `def |CANDIDATE|style|trial_master_audio_store|cascade`
- `er040_tts_fixed_shell_master_champion_trial_01_page_01.py`: Grep `def |lameenc|concat`
- `er006_output/master_audio_store_01/manifest.json`: Grep `canonical_text|style_instruction`(現行 Master 10件の style 文言)
- `OPEN_ITEMS.md`: Grep `OPEN-222|OPEN-223|OPEN-226`

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記。SSOT は Grep のみ(編集禁止)。
- 追記位置: 設計書(新規)、REPORT(新規)。
- 更新位置: なし。

## 実行コマンド全文

- `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er043_tts_fixed_shell_master_champion_trial_02.py --candidates B,C --phrases <phrase 単位で分割実行> --out-dir "er043_output/tts_fixed_shell_master_champion_trial_02" --trial-store "er043_output/tts_fixed_shell_master_champion_trial_02/master_store" --budget-jpy 40`(引数は実装に合わせ逐語記録)
- `.venv\Scripts\python.exe -m pytest C:\Users\tensh\eigo-radio\er043_tts_fixed_shell_master_champion_trial_02_test_01.py -q`(A=Production Master の sha256 一致、Store 隔離復元、style version key の区別、Production Store 非書込)
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er043*_test_*.py"`
- Production無変更の証拠: `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" "er006_output/master_audio_store_01/" | grep -v er043`(空。他タスク差分は列挙)+ Production manifest の sha256 作業前後一致
- Pages: `curl -sI https://shimomura055.github.io/eigo-radio/user_test/fixed_shell_champion_trial_02/index.html`、headless DOM 取得、mp3 200 確認(逐語記録)

## SSOT追記文

RESULT_PACKET へ文案のみ(REPORT_LEDGER 新行、DECISION_LOG、OPEN-222 追記案)。

## Git

- add対象(path指定のみ、`git add -A` 禁止): `er043_*`、`er043_output/.../`(json/md、wav 非commit)、`user_test/fixed_shell_champion_trial_02/`(mp3/html)、REPORT、設計書、delegation_log+`_check.json`。SSOT編集権: なし。
- メッセージ: `TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02: 固定フレーズ10件のA(現行Master)/B/C候補(full_story_intro余裕・One〜Fiveセット安定・ポイント解説抑揚)+One→Five連続比較ページ`、trailer `Management-ID: TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02`。`git push origin main`。

## 報告(RESULT_PACKET_CH2 + handback、目安30行)

ユーザー指定項目: 実施内容/使用Prompt全文(A/B/C の最終 style 文字列、phrase 別)/Candidate/試聴URL/公開実ブラウザ確認結果(7項目)/ASR・drift/retry/cost/regression/Production無変更証拠/Trial status/USER_DECISION_REQUIRED+STOP有無+SSOT文案+commit hash+raw URL。
