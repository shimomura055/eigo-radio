## 管理ID

TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02(ユーザー承認済みTrial、Trialのみ)。一時ファイル `docs/pm/ACTIVE_TASK_VR2.md` / `docs/pm/RESULT_PACKET_VR2.md`(commitしない)。並行: 別Sonnet 2件(Task 1 `er042_*`/`er042_output/`/`user_test/kp_advanced_explanation_audio_trial_03/`、Task 2 `er043_*`/`er043_output/`/`user_test/fixed_shell_champion_trial_02/`)→ これらに触れない。本タスクの所有: 新規 `er044_tts_variable_spoken_role_style_trial_02.py`(+`_test_01.py`)、`er044_output/tts_variable_spoken_role_style_trial_02/`(Trial専用Master Store含む)、`user_test/tts_variable_role_style_trial_02/`、`user_test/tts_all_role_style_trial_01/index.html`(先頭に新ページへの案内リンクを追記する場合のみ)、新規 `TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02_REPORT.md`、`docs/pm/design_tts_variable_spoken_role_style_trial_02.md`、delegation_log。`er038_*` は import/読み取りのみ(変更禁止)。**Production code・正式Prompt・CURRENT_SPEC・routing・Production Master Audio Store は一切変更しない。SSOT 4点は編集権なし(文案のみ)。削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断報告。APIキー本文表示禁止。試聴リンクはGitHub Pages。**

## 性質/到達上限Status/禁止事項

- 性質: Trial。到達上限Status: `REJECTED` / `VALIDATED` / `USER_DECISION_REQUIRED`(ユーザー試聴前は `USER_DECISION_REQUIRED`、Production配線へ進まない)。
- 費用: 上限¥60。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- **実行安全(前回 `--stage all` インシデントの再発禁止、最重要)**: `--stage all` および `run_tts_stage` 全体の再実行禁止。必要 segment だけを対象に明示した部分実行のみ(segment 単位/pattern 単位の関数を直接呼ぶ)。**実行前に ACTIVE_TASK へ「対象 segment 一覧/想定 TTS call 数/retry 上限(既存 cascade の値)/想定費用/Guardrail」を記録してから実行**。J0/E0(現状)は `er038_output/tts_all_spoken_role_style_trial_01/hormuz/` の既存音声を **コピー再利用**(style metadata が現行 Role style と一致することを確認。一致しなければ新規生成し理由記録)。記事本文・Key Phrase 選定・記事 text は再生成しない。Bash timeout で background 化する前に pattern×segment 単位で分割実行。
- 禁止: 過剰演技/trailer 調/sports 実況/大げさなニュースキャスター/不自然な emotion に振れる style、新規 Role 名の新設(既存 6-role/JA style 名を再利用)、Style の省略表記(ページには **実際に TTS へ渡した Style Prompt 全文** を表示。`(existing 6-role value, unchanged)` 等の表記は禁止)、固定 phrase(Welcome/Preview intro/Key Phrase intro/Full Story intro/One〜Five/ポイント解説)の対象化(Task 2 専用)、Key Phrase EN/英語解説(Task 1 専用)。ユーザー向け表記は Standard/Advanced、TTS実行は 同期実行/バッチ実行。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 は標準(全文Readは `er038_tts_all_spoken_role_style_trial_01.py` と Task B 設計書のみ可)。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02_01.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02_01.md --json-out docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02_01.md_check.json` を実行し結果1行記録。
T-2: `TTS_EXECUTION_MODE=STANDARD` 明示、Trial専用Store(`er044_output/.../master_store/`)、`--budget-jpy 60` 明示、Production Store 書込禁止。
T-3: 上記「性質」欄の定型文に従う。

## ユーザー指示(原文)

「Task 3 — 可変音声 Role Style 再Trial。目的: 現在のRole Styleは全体に単調。日本語・英語本文とも、自然な抑揚を少し加えた方が聞きやすい可能性がある。ただし、過剰演技/trailer調/sports実況/大げさなニュースキャスター/不自然なemotion にはしない。日本語Role Style: 日本語はPreview / Commentだけ個別に扱わず、基本方針を統一する。現状『落ち着いた、自然な話し言葉で』は抑揚不足。今回、J0 現状/J1 軽い抑揚/J2 中程度の抑揚/J3 J2より少し表情豊か の現状+3パターンを比較。方向性は、落ち着いた自然な話し言葉を維持しつつ、意味・流れ・強調点・転換に応じて自然な抑揚をつけ、単調にならないようにすること。各PatternのPrompt文言は短くシンプルに作る。日本語で対象となる可変segmentを棚卸しし、Master対象固定phraseは除外。英語本文Role Style: 対象は少なくとも FULL_STORY/IN_ONE_LINE。必要ならTOPIC_INTRO等の可変英語segmentもExisting Specを確認して対象化。現状の代表: FULL_STORY calm, steady news narration/IN_ONE_LINE concise, clear。これらは少し平板。今回、E0 現状/E1 軽い自然な抑揚/E2 中程度の抑揚/E3 E2より少し表情豊か の現状+3パターンを比較する。方向性: calm / clear を維持しつつ、意味の山、対比、転換、結論に応じて自然な抑揚をつけること。特にFull Storyは朗読的すぎず、ニュース原稿棒読みでもない自然なナレーションにする。In One Lineは短いまとめなので、簡潔さを保ちながら最後のまとめとして自然な着地をつける。試聴ページ: 既存の user_test/tts_all_role_style_trial_01/index.html をそのまま継ぎ足さず、今回の比較目的が分かるように整理し直してよい。ただし既存URLを更新する場合は、公開反映まで必ず確認すること。表示要件: Role Style欄で (existing 6-role value, unchanged) のような省略表記は禁止。必ず、実際にTTSへ渡したStyle Prompt全文を表示する。ユーザーが過去仕様を記憶している前提にしない。ページ構成: A. 日本語 各対象segmentについて J0〜J3 の音声を比較、Prompt全文表示。B. 英語本文 各対象segmentについて E0〜E3 を比較、Prompt全文表示。C. 固定phrase 載せない。D. Key Phrase英語解説 Task 1 のページまたは同ページ内独立section。」

## Fable補足

- Existing Spec / Prior Trial Check(設計書に記録): `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_REPORT.md` と `docs/pm/design_tts_all_spoken_role_style_trial_01.md` §2/§3(Role 棚卸し、JA style、EN 6-role 文言、Store 隔離)、`er038_tts_all_spoken_role_style_trial_01.py`(`TRIAL_ROLE_STYLE_EN`/JA style 定数、segment 生成関数、`trial_master_audio_store`)、`er033_tts_flash_lite_family_x_styles_01.py`(Production 6-role 現行文言)、`er019_family_x_audio_production_runner_01.py`(`_role_style`、JA segment の style、可変 segment 一覧)、`er006_master_audio_store_01.py`、OPEN-221/222/223/226(Grep)。
- **棚卸し**: 日本語の可変 segment(Family X: preview 本文・comment_1〜4・topic_intro が JA なら含める・Key Phrase の日本語意味は Key Phrase 系として除外可=理由記録)と英語の可変 segment(FULL_STORY part1〜3+heading、IN_ONE_LINE、TOPIC_INTRO 等、Existing Spec で確認)。固定 phrase は除外。対象は Hormuz 1 記事(Standard=A2 の JA segment、Advanced=B1B の EN segment。JA が両レベルにある場合は Standard 側のみを対象にし理由記録)。**コスト抑制**: FULL_STORY は part 単位で長いため、E1〜E3 は part1(または最短 part)+IN_ONE_LINE+TOPIC_INTRO を必須とし、part2/3 は費用余裕がある場合のみ。JA は comment_1・comment_2・preview を必須、残りは費用余裕で。実行前計画に対象数と想定費用を記録。
- **Pattern 文言**(短くシンプル、設計書に逐語。既存 style 文言に短い追記をする形で J0/E0 との差分が分かるようにする): J0=現状「落ち着いた、自然な話し言葉で」(Production/Task B で実際に渡している文言を逐語確認)、J1/J2/J3=方向性「落ち着いた自然な話し言葉を維持しつつ、意味・流れ・強調点・転換に応じて自然な抑揚」を段階化(軽い/中程度/少し表情豊か)。E0=現行 6-role 文言、E1/E2/E3=「calm/clear を維持しつつ、意味の山・対比・転換・結論に応じた自然な抑揚」を段階化(FULL_STORY は朗読的すぎず棒読みでもない、IN_ONE_LINE は簡潔さ+自然な着地)。禁止方向(過剰演技等)を打ち消す短い制約語を J2/J3・E2/E3 に含めてよい。
- 生成は Production と同じ生成関数を Trial Store・Trial out-dir・style 上書きで呼び、ASR 検証は Production と同じ cascade(retry 上限は既存値、独自変更なし)。**最終的に TTS へ渡した style 文字列の全文**(Production 側で付与される接頭・接尾・フォールバック文を含む)を metadata として保存しページに表示。Standard の 6% slowdown 等の post-process が現行 Production にあるなら J0〜J3 全てに同条件で適用し明記。
- 試聴ページ: 新規 `user_test/tts_variable_role_style_trial_02/index.html`(A. 日本語 segment × J0〜J3、B. 英語 segment × E0〜E3、各セルに音声/**Style 全文**/duration/ASR 結果、D. Task 1 ページ `https://shimomura055.github.io/eigo-radio/user_test/kp_advanced_explanation_audio_trial_03/index.html` へのリンク section[Task 1 は並行中のため URL リンクのみ]、固定 phrase は載せず Task 2 ページ `.../fixed_shell_champion_trial_02/index.html` へのリンクのみ)。既存 `user_test/tts_all_role_style_trial_01/index.html` は先頭に新ページ案内を1行追記するだけ(内容は変更しない。更新した場合は公開反映を確認)。
- **Pages 公開確認(7項目、全て満たすまで「試聴ページ完成」と書かない)**: (1) 対象 URL HTTP 200、(2) 実ブラウザ相当で公開ページを開く(Edge/Chrome `--headless --dump-dom <URL>` で公開 DOM 取得。不可なら Pages 反映後の `curl` 本文で代替し明記)、(3) 公開 DOM に `(existing 6-role value, unchanged)` が 0 件、(4) Style Prompt 全文が公開 DOM に実表示、(5) `<audio>` 件数、(6) 各 mp3 公開 URL が 200・audio content-type・非ゼロ長・デコード可能、(7) ページ表示 Style と生成音声の Style metadata(json)が一致。404/旧 cache は別 URL を乱造せず Pages の deploy 状態を調査して報告。
- 判定案: `USER_DECISION_REQUIRED`。Sonnet は `VALIDATED` を自己宣言しない。共有 append-only ログ `er011_output/attempt_history.jsonl` への追記は開示(OPEN-223 同型)。

## 事前指定Read一覧

- `docs/pm/design_tts_all_spoken_role_style_trial_01.md`: §2/§3
- `er038_tts_all_spoken_role_style_trial_01.py`: 全文(構造確認、変更禁止)
- `er033_tts_flash_lite_family_x_styles_01.py`: Grep `FAMILY_X_ROLE_STYLE|FALLBACK`
- `er019_family_x_audio_production_runner_01.py`: Grep `_role_style|A2_SLOWER_PACE_INSTRUCTION|comment_|preview|topic_intro|in_one_line|full_story`
- `er038_output/tts_all_spoken_role_style_trial_01/hormuz/{a2,b1b}/audit/tts_generation_results.json`(既存 J0/E0 音声の style metadata)
- `OPEN_ITEMS.md`: Grep `OPEN-221|OPEN-222|OPEN-223|OPEN-226`

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記。SSOT は Grep のみ(編集禁止)。
- 追記位置: 設計書(新規)、REPORT(新規)。
- 更新位置: `user_test/tts_all_role_style_trial_01/index.html` 先頭の案内1行のみ(任意)。

## 実行コマンド全文

- `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er044_tts_variable_spoken_role_style_trial_02.py --patterns J1,J2,J3 --segments <segment 単位で分割実行> --out-dir "er044_output/tts_variable_spoken_role_style_trial_02/hormuz" --trial-store "er044_output/tts_variable_spoken_role_style_trial_02/master_store" --tts-backend speech_metadata_flash_lite --budget-jpy 60`(EN は `--patterns E1,E2,E3`。引数は実装に合わせ逐語記録)
- `.venv\Scripts\python.exe -m pytest C:\Users\tensh\eigo-radio\er044_tts_variable_spoken_role_style_trial_02_test_01.py -q`(Pattern 文言の逐語、固定 phrase 非対象、Store 隔離復元、Production Store 非書込、`--stage all` 相当の関数が存在しない/呼ばれない)
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er044*_test_*.py"`
- Production無変更の証拠: `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" "er006_output/master_audio_store_01/" | grep -v er044`(空。他タスク差分は列挙)
- Pages: `curl -sI https://shimomura055.github.io/eigo-radio/user_test/tts_variable_role_style_trial_02/index.html`、headless DOM 取得、mp3 200 確認(逐語記録)

## SSOT追記文

RESULT_PACKET へ文案のみ(REPORT_LEDGER 新行、DECISION_LOG、OPEN 候補)。

## Git

- add対象(path指定のみ、`git add -A` 禁止): `er044_*`、`er044_output/.../`(json/md、wav 非commit)、`user_test/tts_variable_role_style_trial_02/`(mp3/html)、`user_test/tts_all_role_style_trial_01/index.html`(案内追記時のみ)、REPORT、設計書、delegation_log+`_check.json`。SSOT編集権: なし。
- メッセージ: `TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02: 可変segmentのRole Style比較(JA J0〜J3/EN E0〜E3、Style全文表示)+試聴ページ`、trailer `Management-ID: TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02`。`git push origin main`。

## 報告(RESULT_PACKET_VR2 + handback、目安35行)

ユーザー指定項目: 実施内容(棚卸し表、対象 segment、reuse 箇所)/使用Prompt全文(J0〜J3・E0〜E3 の最終文字列)/Candidate/試聴URL/公開実ブラウザ確認結果(7項目)/ASR・drift/retry/cost/regression/Production無変更証拠/Trial status/USER_DECISION_REQUIRED+STOP有無+SSOT文案+commit hash+raw URL。
