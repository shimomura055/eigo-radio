## 管理ID

TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01(ユーザー承認済みTrial)。一時ファイル `docs/pm/ACTIVE_TASK_TF1.md` / `docs/pm/RESULT_PACKET_TF1.md`(commitしない)。並行: 別Sonnet 4件(Task 1 `er045_*`、Task 2 `er046_*`、Task 4 設計書、SSOT反映Agent)→ 触れない。SSOT 4点は編集権なし(文案のみ)。本タスクの所有: 新規 `er047_tts_fixed_shell_number_three_five_retrial_01.py`(+`_page_01.py`+`_test_01.py`)、`er047_output/tts_fixed_shell_number_three_five_retrial_01/`(Trial専用Store含む)、`user_test/fixed_shell_three_five_retrial_01/`、新規 `TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01_REPORT.md`、`docs/pm/design_tts_fixed_shell_number_three_five_retrial_01.md`、delegation_log。**Production code・Production Master Store・正式Prompt・CURRENT_SPEC は変更禁止。削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ。APIキー本文表示禁止。試聴リンクはGitHub Pages。**

## 性質/到達上限Status/禁止事項

- 性質: Trial。到達上限Status: `REJECTED` / `VALIDATED` / `USER_DECISION_REQUIRED`(ユーザーがサンプルから選ぶまで `USER_DECISION_REQUIRED`。Master 登録・配線は別管理ID)。
- **既決 Champion(ユーザー決定、再Trial不要)**: TRIAL-02 試聴ページ `user_test/fixed_shell_champion_trial_02/index.html` の列位置で、welcome=左、preview_intro=右、key_phrases_intro=右、full_story_intro=右、num_one=右、num_two=中、num_four=右、point_explanation=中。**最初に同 HTML を読み、左/中/右がそれぞれ A/B/C のどれに対応するかを列順から確定**し、対応表(phrase → candidate ID → 音声ファイル → 実際の style 全文 → model → voice)を設計書と REPORT 冒頭に記載する。列順が曖昧なら生成前に STOP 報告。
- 再Trial 対象: num_three / num_five のみ。**重要条件**: 採用済み One(右)/Two(中)/Four(右)とセンスを変えない → モデル変更禁止・voice 変更禁止・基本 Style 思想変更禁止。採用品が Flash-Lite なら Three/Five も Flash-Lite 固定。One/Two/Four の採用品が使った **同じ style 文言(候補 B 系統・C 系統の両方が採用されているなら両方)**・同 model・同 voice で、Three/Five をそれぞれ複数 sample(各 style 系統 × 各語 4 take 程度)生成する。目的はモデル比較ではなく「One/Two/Four と統一感のある Three/Five の良い take を複数提示」。
- 費用: 上限¥20(想定 16〜24 TTS call+ASR)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし報告。
- **実行安全**: `--stage all` 禁止。必要 segment のみ、実行前に ACTIVE_TASK へ「対象/想定 call 数/retry 上限/想定費用/Guardrail」を記録。既存採用音声(One/Two/Four、TRIAL-02 出力)は reuse。
- ASR: Production 同一 cascade(既存上限)。**ASR 不合格 take も、音声が保存されていれば「Production 登録不可(人間確認用)」と明示して試聴ページに載せる**(ユーザー指示)。合格/不合格を明確に区別表示。独自 retry 追加なし。
- 禁止: 新規 Role 名、Style 省略表記(TTS へ渡した Style 全文を表示)。ユーザー向け表記は Standard/Advanced、TTS実行は 同期実行/バッチ実行。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準(全文Readは `er043_*` script と TRIAL-02 の index.html のみ可、流用推奨)。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01_01.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01_01.md --json-out docs/pm/delegation_log/2026-09-28_TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01_01.md_check.json` を実行し結果1行記録。
T-2: `TTS_EXECUTION_MODE=STANDARD` 明示、Trial専用Store(`er047_output/.../master_store/`)、`--budget-jpy 20`、Production Store 書込禁止。
T-3: 上記「性質」欄の定型文に従う。

## Fable補足

- 生成は `er043_*` の候補生成経路(Production 同一関数+Trial Store 隔離+cascade)を import/流用。take ごとに全 attempt の wav・ASR text・分類を保存。
- ページ `user_test/fixed_shell_three_five_retrial_01/index.html`: 冒頭に採用済み One/Two/Four の音声(reuse)+style 全文+model/voice。Three/Five の各 take(style 系統別、合格/不合格の明示、ASR text、duration、簡易 F0 末尾傾向[TRIAL-02 の proxy を流用]、Style 全文)。**One→Five 連続再生**: 採用 One/Two/Four+Three take k+Five take k(k ごと)を連結した参考 mp3(不合格 take を含むものは「未検証を含む」と明示)。
- **Pages 公開確認 7項目**(HTTP 200/headless Edge・Chrome DOM/省略表記 0件/Style 全文表示/`<audio>` 件数/mp3 全件 200・audio・非ゼロ長・代表デコード/表示 Style と metadata 一致)。404/旧 cache は原因調査。
- 判定案: `USER_DECISION_REQUIRED`。共有ログ `attempt_history.jsonl` 追記は開示(OPEN-223 同型)。

## 事前指定Read一覧

- `user_test/fixed_shell_champion_trial_02/index.html`(全文、列順の確定)
- `er043_output/tts_fixed_shell_master_champion_trial_02/champion_trial_results.json`(Grep `num_one|num_two|num_four|style|model|voice`)
- `er043_tts_fixed_shell_master_champion_trial_02.py`(全文)、`_page_01.py`(Grep `def |concat|f0`)
- `OPEN_ITEMS.md`: Grep `OPEN-222|OPEN-223`

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記。SSOT は Grep のみ。追記位置: 設計書(新規)、REPORT(新規)。更新位置: なし。

## 実行コマンド全文

- `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er047_tts_fixed_shell_number_three_five_retrial_01.py --phrases num_three,num_five --styles <採用系統の candidate ID> --takes 4 --out-dir "er047_output/tts_fixed_shell_number_three_five_retrial_01" --trial-store "er047_output/tts_fixed_shell_number_three_five_retrial_01/master_store" --budget-jpy 20`(逐語記録)
- `.venv\Scripts\python.exe -m unittest er047_tts_fixed_shell_number_three_five_retrial_01_test_01 -v`(model/voice/style が採用品と一致、Store 隔離復元、Production Store 非書込)
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er047*_test_*.py"`
- `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" "er006_output/master_audio_store_01/" | grep -v er047`+Production manifest sha256 前後一致
- `curl -sI https://shimomura055.github.io/eigo-radio/user_test/fixed_shell_three_five_retrial_01/index.html`、headless DOM、mp3 200(逐語記録)

## SSOT追記文

RESULT_PACKET へ文案のみ(REPORT_LEDGER 新行、DECISION_LOG、OPEN-222 追記案)。

## Git

- add対象(path指定のみ): `er047_*`、`er047_output/.../`(json/md)、`user_test/fixed_shell_three_five_retrial_01/`、REPORT、設計書、delegation_log+`_check.json`。SSOT編集権なし。
- メッセージ: `TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01: 採用済みOne/Two/Fourと同条件でThree/Fiveの複数takeを生成(ASR不合格takeも人間確認用に明示表示)+One→Five連続比較ページ`、trailer `Management-ID: TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01`。`git push origin main`。

## 報告(RESULT_PACKET_TF1 + handback、目安30行)

冒頭: 左/中/右 → A/B/C の対応表(採用 8 phrase の candidate ID・style 全文・model・voice)。以降: 管理ID/実施内容/既存Spec確認結果/使用Prompt全文/model・voice/retry/ASR・drift(take ごとの合否)/cost/Regression/公開試聴URL/公開確認結果(7項目)/Production変更有無/Trial status/USER_DECISION_REQUIRED事項/未配線 APPROVED 項目(採用済み 8 phrase の Master 登録未実施)+commit hash+raw URL+STOP有無。
