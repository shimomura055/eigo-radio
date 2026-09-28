# Delegation: TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01

## 管理ID
TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01(ユーザー承認済みTrial、Trialのみ)。一時ファイル `docs/pm/ACTIVE_TASK_CH1.md` / `docs/pm/RESULT_PACKET_CH1.md`(commitしない)。並行: 別Sonnet 3件(Trial-02 `er039_*`/`user_test/concreteness_trial_02/`、Task D `er041_*`/`user_test/kp_advanced_explanation_trial_02/`、Task B追補 `er038_output/`/`user_test/tts_all_role_style_trial_01/`)→ これらに触れない。本タスクの所有: 新規 `er040_tts_fixed_shell_master_champion_trial_01*.py`(+test)、`er040_output/tts_fixed_shell_master_champion_trial_01/`(Trial専用Master Store含む)、`user_test/fixed_shell_champion_trial_01/`、新規 `TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01_REPORT.md`、`docs/pm/design_tts_fixed_shell_master_champion_trial_01.md`、delegation_log。**Production code・正式Prompt・CURRENT_SPEC・routing・Production Master Audio Store(`er006_output/master_audio_store_01/`)は一切変更しない**。SSOT 4点は編集権なし(文案をRESULT_PACKETへ)。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**(push競合時は `git merge origin/main` のみ、conflictは中断報告)。

## 性質/到達上限Status/禁止事項
- 性質: Trial。到達上限Status: `REJECTED` / `VALIDATED` / `USER_DECISION_REQUIRED`(ユーザーがChampionを選ぶ前は `USER_DECISION_REQUIRED`。選ばれてもProduction wiringへ進まない)。
- 費用: 上限¥40。超過時条件あり。暴走疑い時のみSTOP。
- 禁止: 新キャッシュ機構新設、可変text対象化、無意味な大量生成、Production Master Store置換・汚染、記事再生成、Key Phrase再選定。APIキー本文表示禁止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1/D-1/G-1/F-1は標準。T-0: 本ファイル保存+check script実行。T-2: TTS_EXECUTION_MODE=STANDARD明示、Trial専用Store使用、Production Store書込禁止、--budget-jpy明示。T-3: 性質欄定型文に従う。

## ユーザー指示(原文)
Task C — 固定フレーズ Master Champion Trial。目的: 毎記事・毎runで内容が変わらない固定フレーズについて、毎回TTS生成するのではなく、一度高品質なChampion音声を作成→Master Audio Storeから毎回reuseする前提で、Champion候補を選ぶ。品質向上だけでなく、TTS生成コスト削減/ASR検証コスト削減/retry削減/極短segmentの言語ドリフト削減/run間の品質ばらつき削減を目的とする。
対象固定segment: 最低限、現在Family Xで固定されている Welcome/Preview intro/Key Phrase intro/Full Story intro(Now, the full story.)/One./Two./Three./Four./Five./Standardのみの固定日本語(ポイント解説)。その他、Productionで「全記事共通かつ文言固定」のTTSがあれば一覧化。記事本文・Comment・Key Phrase本体など可変textは対象外。
既存Master Audio Store確認: まず既存仕様を確認。今回新しいキャッシュ機構を作らない。確認項目: canonical_text/voice/model/style_instruction_id・version/language/level依存・非依存/reuse条件/ASR verified状態。特に、新Role Style導入後の音声を旧styleのMasterとして誤reuseしないこと。新Champion採用時にstyle/versionを適切に区別できる構造であることを確認。
Champion候補: 作り方は実装側へ委任。目的は最良の固定音声を作ること。候補として Gemini 3.8 Flash-Lite/既存2.5 Pro系TTS/必要なら既存Productionで実績のあるmodel・voice・style を比較してよい。モデル比較自体が目的ではない。固定phraseごとに自然で安定したChampionを選ぶ。無意味に大量生成しない。2〜3候補程度を基本、明確なWinnerがあればSTOP。
特に One〜Five: 極短音声のため、言語ドリフトしない/数字として自然/大げさでない/前後のKey Phrase flowに馴染む/One〜Fiveで声質・テンポ・音量が揃う ことを重視。Two./Three. の既知の失敗を再発させない。One〜Fiveはセットとして統一感も評価。
ユーザー試聴: 比較ページ。各固定phraseについて Candidate A/B/(C)、model、voice、style、duration を表示。One〜Fiveは個別再生に加えてOne→Five連続再生比較も用意。現行Production Masterが存在する場合はBaselineとして併記。
Trial完了条件: ユーザーがChampionを選ぶ前は USER_DECISION_REQUIRED。選ばれても今回はProduction wiringへ進まない(別IDで Master登録/Assembly reuse確認/regenerationされない証拠/runtime evidence/regression/SSOT)。
コスト/QCD: 既存artifact再利用、無意味なTTS再生成禁止、Production Master Store汚染禁止、Production Prompt変更禁止、CURRENT_SPEC変更禁止。将来の量産時コスト削減効果も概算(1記事あたり何TTS call削減可能か、Standard/Advanced両方でどれだけreuseできるか)。
Closeout(12項目): 1 Existing Spec/Prior Trial確認 2 実施内容 3 Candidate 4 成果物 5 品質評価 6 Regression 7 Cost 8 再利用可能性 9 新規発見 10 Trial status 11 USER_DECISION_REQUIRED 12 Production変更ゼロの証拠。

## Fable補足
- 既存資産: 共有ナレーション定義 `er006_audio_cost_pilot_02_shared_narration.py`、Master Audio Store `er006_master_audio_store_01.py`(`EQUALITY_FIELDS`、`master_audio_id`=sha256、ASR verified登録条件)、Production manifest `er006_output/master_audio_store_01/manifest.json`(read-only)、Task B設計書、OPEN-201/212/222。棚卸しは Family X runner(`er019_family_x_audio_production_runner_01.py`)の shared narration 呼び出し+`ensure_fixed_*` 定義から列挙。
- 候補設計(各phrase 2〜3): (A) Flash-Lite+実証済み短style、(B) Flash-Lite+Task B設計のRole style、(C) 既存2.5 Pro系TTS+既存Production style。One〜Fiveは同一候補設定でセット生成し揃いを定量化。各候補はProductionと同じ生成関数をTrial Store・Trial out-dir・style上書きで呼ぶ。ASR検証はProductionと同じcascadeを通す。
- Master Store構造確認: 新Champion採用時にkeyへstyle_instruction_version/tts_model_id/voice/language/canonical_text_hashが含まれ旧style Masterと区別されることを設計書に表で示す。
- 試聴ページ: `user_test/fixed_shell_champion_trial_01/index.html`(GitHub Pages)。push後 curl -sI で200確認。
- コスト効果概算: Family X 1記事あたりの固定phrase TTS call数と削減見込みを表にする。
- 判定案: `USER_DECISION_REQUIRED`。Sonnetは`VALIDATED`を自己宣言しない。

## 事前指定Read一覧
- `er006_audio_cost_pilot_02_shared_narration.py`:1-160
- `er006_master_audio_store_01.py`(Grep EQUALITY_FIELDS|def register|verified|store_dir)
- `er006_output/master_audio_store_01/manifest.json`(Grep canonical_text)
- `docs/pm/design_tts_all_spoken_role_style_trial_01.md` §2/§3
- `er019_family_x_audio_production_runner_01.py`(Grep ensure_all_shared_narration|point_explanation)
- `OPEN_ITEMS.md`: OPEN-201/212/222

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep対象: `er006_master_audio_store_01.py`(`EQUALITY_FIELDS|def register|verified|store_dir`)、`er006_output/master_audio_store_01/manifest.json`(`canonical_text`)、`docs/pm/design_tts_all_spoken_role_style_trial_01.md`(`Store隔離|Role style`)、`er019_family_x_audio_production_runner_01.py`(`ensure_all_shared_narration|point_explanation`)、`OPEN_ITEMS.md`(`OPEN-201|OPEN-212|OPEN-222`)。
- 追記位置: 本Trialの新規設計内容は `C:\Users\tensh\eigo-radio\docs\pm\design_tts_fixed_shell_master_champion_trial_01.md` へ新規作成して追記する(既存設計書は変更しない)。
- 更新位置: 実行結果・評価は `C:\Users\tensh\eigo-radio\TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01_REPORT.md` を新規作成して更新する。SSOT本体(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`HISTORY_INDEX.md`)は本Trialでは直接更新せず、`docs/pm/RESULT_PACKET_CH1.md` へ追記案文のみを記載する。

## 実行コマンド全文
- `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er040_tts_fixed_shell_master_champion_trial_01.py --candidates A,B,C --out-dir "er040_output/tts_fixed_shell_master_champion_trial_01" --trial-store "er040_output/tts_fixed_shell_master_champion_trial_01/master_store" --budget-jpy 40`
- `.venv\Scripts\python.exe -m pytest C:\Users\tensh\eigo-radio\er040_tts_fixed_shell_master_champion_trial_01_test_01.py -q`
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er040*_test_*.py"`
- Production無変更証拠: `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" "er006_output/master_audio_store_01/" | grep -v er040`(空)

## SSOT追記文
RESULT_PACKETへ文案のみ。

## Git
add対象: er040_*、er040_output/tts_fixed_shell_master_champion_trial_01/(json/md、wavは非commit)、user_test/fixed_shell_champion_trial_01/(mp3/html)、REPORT、設計書、delegation_log+_check.json。SSOT編集権なし。
メッセージ: `TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01: 固定フレーズの棚卸し+Champion候補(Flash-Lite短style/Role style/2.5 Pro系)生成+One〜Five連続比較ページ+量産コスト削減概算`、trailer `Management-ID: TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01`。push origin main。

## 報告
ユーザー指定12項目+STOP有無+SSOT文案+commit hash+raw URL。
