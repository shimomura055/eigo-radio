## 管理ID

USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-VOICES(Voices 2V「三人称化」の仕様調査→Production不整合なら修正・再生成→音声化)
並行タスク衝突確認: 並行して Family C(er013)、Trend(`.../trend/`)、Discovery(`.../discovery/`)が走る。本タスクは`er014_output/four_type_observation_01/voices/`配下と、Production不整合修正に必要な最小範囲のer012_*(Writer prompt)のみを書く。Git・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_FIX02_VOICES.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー指摘: 現2V記事(`voices/run2_clean/b1_2v_new_theme_attempt3/article.md`)が三人称(she…/the reader…)で構成されている。**まず調査**: B-Family Voices正式仕様(CURRENT_SPEC)、Writer Prompt(`er012_b_family_voices_writer_generic_01.py`の2V/3V prompt本文、`er012_b_family_editorial_type_registry_01.py`のRole/Contract)、2V/3V承認済み例(承認済み固定記事: `er012_output/editorial_b_voices_trial_07/`等、`main()`/`main_b1_3v()`が参照する固定記事)を確認し、「Voice本人が一人称で自分の立場を語る(I use…/I worry…/I feel…)」ことが既存仕様かを判定。根拠(ファイル・行・承認済み記事の実例引用)を`voices/first_person_investigation.md`に記録。
- **一人称が既存正式仕様の場合**: 新仕様ではなく**Production不整合**として修正する。(a) 不整合の所在を特定(例: 2V用prompt/Focus module block/Contractに一人称指示が欠落または三人称を許容する文言がある、3V用には存在する等)。(b) 修正は「既存仕様(一人称)にPromptを合わせる」最小変更のみ(3V側の文言・挙動は変えない。変更箇所のdiffをRESULT_PACKETへ)。3V不変テスト(`er012_b_family_voices_variable_voice_count_test_01.py`)と`run_project_regression.py --pattern "er012*_test_*.py"`をPASSさせる(3Vテストが「promptバイト不変」を前提にしている場合、3V側を変えていなければPASSするはず。2V側テストの期待値は仕様どおり更新可)。(c) 既存2V正式経路(`main_b1_2v()`のwrite_new_theme、同一Ledger再利用、Research再実行禁止、MAX_WRITER_ATTEMPTS不変、Leakage Gate不変、Fact Safety Gate不変)で記事を再生成し、Fact Checker/Ledger Deviation/Comment Contract/Leakage QAを通常どおり実行(出力`voices/run3_first_person/`)。Narratorが第三者として説明する形式へ戻さない。(d) 生成記事が一人称構造であることを機械確認(各Voice本文の一人称代名詞/三人称代名詞の出現数を`voices/run3_first_person/pov_check.json`へ)+Fable/ユーザーが読める全文。(e) 音声化: 前回CONT1のdriver(`run_voices_2v_audio_completion_2.py`)と同一経路で、新記事に対しPreview/Comment(接続済みComment Contract)/Key Phrase/TTS/Assembly/Audio Validation/mp3/player(`voices/audio/b1_2v_v2/player.html`、相対パス、Status注記「PARTIAL / USER TEST READY」+Leakage残存有無)/article-audio consistency/`comment_fact_safety_evidence.json`。旧v1(`voices/audio/b1_2v/`)は保持。
- **三人称も既存仕様上許容の場合**: 根拠を示して**STOP**(ユーザー判断へ)。音声化しない。Audio Validation PASSをEditorial構造PASSの根拠にしない。
- なぜ既存QAで「完成」と報告できたか(必須): 三人称化を検出できなかった理由(Leakage Check/Contract/Fact Checkerが視点を見ていない等、根拠付き)を記載。新Validatorは追加しない。
- Status上限: `PARTIAL / USER TEST READY`。OPEN-151はPARTIALのまま。PRODUCTION_WIRED禁止。
- 費用上限: ¥180(Writer再生成≈¥95+音声化≈¥50+QA)。段階ごとに次段階見込み込みで事前判定。
- 禁止: Research再実行/新Prompt原則の追加(既存仕様への整合のみ)/MAX_WRITER_ATTEMPTS変更/Leakage・Fact Safety Gate変更/3V挙動変更/`approve_regenerate()`(TTSロック時はSTOP)/PRODUCTION_WIRED表記/`.gitignore`変更/Git commit・push/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件: 三人称が仕様上許容/一人称化に新仕様が必要/Gate緩和が必要/費用上限超過見込み/TTS Human Review Lock到達/技術的にWeb配信不可。STOP時は「何を試したか/何が残ったか/ユーザーに必要な判断」を提示。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文)

> 現記事が三人称(she…/the reader…)で構成されている。ユーザーはこれを問題視。Repoで確認: B-Family Voices正式仕様/Writer Prompt/CURRENT_SPEC/2V/3V承認済み例。確認すること: Voice本人が一人称で語ることが既存仕様か。一人称が既存正式仕様なら新仕様ではなくProduction不整合。修正する。例: I use…/I worry…/I feel…。各Voice本人が自分の立場を語る構造へ戻す。Narratorが第三者として説明する形式へ戻さない。Fact/Ledger/Comment/Leakage QAを通常どおり再実行。三人称も既存仕様上許容なら根拠を示してSTOP。ユーザー判断へ戻す。Audio Validation PASSをEditorial構造PASSの根拠にしない。OPEN-151は残存Leakageがあるため、勝手にPRODUCTION_WIREDにしない。

## 事前指定Read一覧

1. `CURRENT_SPEC.md`: Grep `Voices|Voice A|Voice B|一人称|first.person|I |本人|当事者|語る|3V|2V` → B-Family Voices仕様の該当行のみ(Grep結果から節を特定し、その節のみRead)。
2. `er012_b_family_voices_writer_generic_01.py`: Grep `first person|first-person|I |you |third person|she|he |persona|speak as|in their own words|def build_focus_module_block|def build_focus_module_block_2v|def build_writer_prompt|VOICE_` → 2V/3Vのprompt本文(Voice本文の視点指示)該当範囲のみ。
3. `er012_b_family_editorial_type_registry_01.py`: Grep `Voice|voice_a|voice_b|Role|Contract|first|person` → Role定義のみ。
4. 承認済み記事例: `er012_output/editorial_b_voices_trial_07/`: Glob `**/article*.md` → 1件の Voice A/B節のみ(一人称/三人称の実例確認)。3V承認済み記事(`main_b1_3v()`が参照するパス、Grep `editorial_b_voices_3v|APPROVED|article_path` in `er012_b_family_production_runner_01.py`)→ 1件のVoice節のみ。
5. `er014_output/four_type_observation_01/voices/run2_clean/b1_2v_new_theme_attempt3/article.md` 全文(現記事)。
6. `er014_output/four_type_observation_01/voices/run_voices_2v_b1.py` および `run_voices_2v_audio_completion_2.py`: Grep `^def |argparse|add_argument|reuse|ledger|out` → 再生成・音声化の入口のみ。
7. `er012_b_family_voices_variable_voice_count_test_01.py`: Grep `^    def test_|byte|source|prompt` → 3V不変テストが何を固定しているか。
8. `er014_output/four_type_observation_01/voices/run2_clean/production_set_cost.json` 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 出力: `voices/first_person_investigation.md`、(修正時)er012_* diff、`voices/run3_first_person/{article.md, audit/, pov_check.json, cost_summary.json}`、`voices/audio/b1_2v_v2/{...同v1構成..., player.html, web/}`、`voices/audio/web_delivery.json`(v2追記)、`voices/run2_clean/production_set_cost.json`または`voices/production_set_cost.json`(Voices総原価=¥185.74+本タスク実費、差分明記。ファイル位置は既存の方を更新し、RESULT_PACKETに明記)、`progress_log.md`1行。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-VOICES.md --json-out docs\pm\delegation_log\USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-VOICES_check.json`
2. 修正時: `.venv\Scripts\python.exe -m unittest er012_b_family_voices_variable_voice_count_test_01 -v`、`.venv\Scripts\python.exe run_project_regression.py --pattern "er012*_test_*.py"`
3. 再生成: `.venv\Scripts\python.exe er014_output\four_type_observation_01\voices\run_voices_2v_b1.py --reuse-ledger --out-subdir run3_first_person --budget-jpy 110`(前回の引数名に合わせる。全文コマンド記録)
4. 音声化: `.venv\Scripts\python.exe er014_output\four_type_observation_01\voices\run_voices_2v_audio_completion_3.py --article-dir run3_first_person --out audio/b1_2v_v2 --budget-jpy 60`(driver派生、全文コマンド記録)
5. 確認: `Select-String -Path er014_output\four_type_observation_01\voices\audio\b1_2v_v2\player.html -Pattern "file:///|C:\\" | Measure-Object -Line`(0件)、`git check-ignore -v er014_output/four_type_observation_01/voices/audio/b1_2v_v2/web/episode.mp3`(exit 1)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-151末尾追記案(一人称仕様の判定結果、修正内容、再生成結果、音声化、Status PARTIAL / USER TEST READY、PRODUCTION_WIREDと書かない)、CURRENT_SPEC追記案(Production不整合の修正記録、仕様自体は不変)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補一覧(サイズ付き、er012変更ファイル含む、wav除外・mp3必須)」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FIX02_VOICES.md`に: 1) 仕様判定(一人称が既存仕様か、根拠引用)、2) 不整合の所在と修正diff要約(修正時)/STOP理由(許容時)、3) 3V不変テスト・回帰結果、4) 再生成記事(語数、attempt数、Fact Checker/Ledger/Comment Contract/Leakage結果、pov_check結果、記事全文パス)、5) 音声化(TTS attempt、Audio Validation、duration、mp3・player・予定URL `https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/voices/audio/b1_2v_v2/player.html`)、6) Comment/Fact Safety反映証拠、残存Leakage記録、7) なぜ既存QAで三人称化を検出できなかったか(根拠)、8) 費用(本タスク実費、**Voices総原価=¥185.74+実費=¥xx.xx**)、9) model_id/TTS model、10) Open Item候補、11) commit対象候補一覧、12) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥180)
- [x] 並行タスク衝突回避あり(voices/配下+er012 prompt最小・Git操作なし)
