## 管理ID

USER-TEST-AUDIO-COMPLETION-01-VOICES(Voices / Is personalized news good for us?: 2V candidate音声化+Web試聴player、Status上限 PARTIAL / USER TEST READY)
並行タスク衝突確認: 並行して Family C(er013)、Trend(`.../trend/`)、Discovery(`.../discovery/`)が走る。本タスクは`er014_output/four_type_observation_01/voices/`配下と、必要最小限のer012_*(2V音声経路の最小接続に限る)だけを書き、Git・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを触らない。共有資産への書き込みは既存経路が自動で行う分のみ。RESULT_PACKETは`docs/pm/RESULT_PACKET_UT_VOICES.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: 現在の2V canonical candidate(`voices/run2_clean/b1_2v_new_theme_attempt3/article.md`、374語、Fact Checker PASS/Ledger COMPLIANT/Comment Contract検証COMPLIANT、**Analytical Leakage Check残存flag[voice_b/tension]あり**)を、接続済みComment Contract・2V対応済みFact Safety Gate・Preview・Key Phrase・TTS・2V Voice構成・Assembly・Audio Validation・完成episode・Web試聴playerまで進める。**Status上限=`PARTIAL / USER TEST READY`。PRODUCTION_WIRED禁止。** OPEN-151のStatusを変えない。残存Leakageの事実を試聴対象から隠さず内部記録(player内の注記またはevidence JSON)に残す。
- ユーザー確定事項: MAX_WRITER_ATTEMPTSを増やさない/Leakage Gateを緩めない/Prompt改善Trialを始めない/記事再生成しない(現candidateをそのまま使う)。
- 経路調査(先に実施): B-Family Voices音声経路=`er012_b_family_voices_production_01.py`(3V Production配線Phase1)、`er012_b_family_production_runner_01.py`(`main_b1_2v`/`main_b1_3v`、a2/b1 runnerは承認済み固定記事のhash fail-closed)。2V記事(5区切り: The Question/One Voice/Another Voice/Why They See It Differently/What This Is Really About)に対し、TTS→Assembly→Audio Validation→playerの既存経路がそのまま使えるか、3V専用(6区切り前提)箇所があるかをGrepで特定。gapは**新仕様を作らず既存資産で最小接続**: 例=section parserは-02タスクで2V対応済みのものを使う、Voice割当は既存3V構成(narrator/voice_a/voice_b)からvoice_cを使わない2声構成として既存voice資産をそのまま使う、hash fail-closedのrunnerを使う場合は当該2V記事のhashを「USER_TEST_CANDIDATE(承認済み固定記事ではない)」と明示注記して登録(承認扱いにしない)。
- 実施内容: (1) 付帯要素: Preview・Comment 1〜4(run2_cleanで生成済みならそれを使用、未保存なら既存接続済み経路で生成)、Key Phrase(既存正式経路`run_key_phrases`相当のB-Family Key Phrase仕様で5件、Validator不合格時は入口再呼び出し最大3回)、Fact Safety Gate(2V対応済み、発火有無を記録)。(2) TTS(既存retry/fallback、2声+narrator構成)。(3) Assembly(既存B-Family仕様のIntro/Outro/SFX)。(4) Audio Validation Gate(緩和禁止)。(5) 完成episode WAV+配信用MP3(既存変換手段優先、Grep `mp3|ffmpeg|pydub` in ルート`*.py`、無ければffmpeg、pip install禁止)。(6) 標準Audio Review Player再利用(**相対パス参照のみ**、Title/level=B1 2V/完成episode/segment表判別可、Status注記「PARTIAL / USER TEST READY(Leakage残存)」)。出力: `voices/audio/b1_2v/{key_phrases/,tts/,assembled/,audio_validation.json,player.html,web/episode.mp3,web/segments/*.mp3,article_audio_consistency.json,comment_fact_safety_evidence.json}`。(7) **Comment/Fact Safetyがepisodeへ実際に反映された証拠**: `comment_fact_safety_evidence.json`に、Comment 1〜4のテキスト・Contract検証結果・各Commentのsegment音声ファイル名・episode内timeline位置、Fact Safety Gateの発火/非発火ログとその理由、Leakage残存flagの原文(voice_b/tension、項目名)を記録。(8) 記事⇔音声一致確認、gitignore確認、mp3<50MB。予定URL: player=`https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/voices/audio/b1_2v/player.html`、直接音声=`https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/voices/audio/b1_2v/web/episode.mp3`。(9) 費用: `voices/audio/cost_summary_audio.json`(Key Phrase LLM/Comment・Preview LLM/TTS/その他)、`voices/production_set_cost.json`更新(Voices Production 1生成セット総原価=既報¥140.39+音声化追加費、差分明記、50:50配賦なし)。
- 費用上限: ¥150。段階ごとに次段階見込み込みで事前判定。
- er012_*を変更した場合: 3V不変テスト(`er012_b_family_voices_variable_voice_count_test_01.py`)+`run_project_regression.py --pattern "er012*_test_*.py"`を実行しPASSを確認。変更は追加のみ(既存3V経路の挙動変更禁止)。
- 禁止: 記事再生成/Writer retry/Leakage Gate・Fact Safety Gate緩和/Prompt変更/MAX_WRITER_ATTEMPTS変更/PRODUCTION_WIRED表記/新player仕様/`.gitignore`変更/pip install/Git commit・push/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件: 新Production仕様が必要/Gate緩和が必要/canonical記事変更が必要/費用上限超過見込み/技術的にWeb配信不可。STOP時は「何を試したか/何が残ったか/ユーザーに必要な判断」を提示。

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

> 残存Leakageは現時点では追加Prompt改善等を行わず、PARTIALのままユーザー実検証へ持っていく。MAX_WRITER_ATTEMPTSを増やさない/Leakage Gateを緩めない/Prompt改善Trialを始めない。残存Leakageがある事実は、試聴対象から隠さず内部記録に残す。現在の2V canonical candidateを使って、接続済みComment Contract/2V対応済みFact Safety Gate/Preview/Key Phrase/TTS/2V Voice構成/Assembly/Audio Validation/完成episode/Web試聴playerまで進める。音声化できても、OPEN-151自体を勝手にPRODUCTION_WIREDにしない。Statusは PARTIAL / USER TEST READY 等、実態が分かる表記にする。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_VOICES_VAR2.md` 全文、`EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-02_REPORT.md`: Grep `run2_clean|Comment 1|comment_|preview|評価|Leakage` → Comment/Previewの保存先・Leakage原文の該当範囲。
2. `er014_output/four_type_observation_01/voices/run2_clean/`: Glob `**/*.json`・`**/*.md`(ファイル名一覧)→ Comment/Preview/Leakage結果ファイルのみRead。
3. `er012_b_family_voices_production_01.py`: Grep `^def |voice_c|six|6|three_voice|3v|assemble|verify_episode_audio_validation_gate|player|tts` → 3V固有箇所と音声段階の該当範囲のみ。
4. `er012_b_family_production_runner_01.py`: Grep `^def main|hash|APPROVED|fail.closed|level ==|b1_2v|audio|assemble` → hash fail-closedと音声段階の該当範囲のみ。
5. `er012_b_family_editorial_type_registry_01.py`: Grep `voice|Voice|comment|Comment|key_phrase|preview` → 2V構成に使うvoice割当・Comment Role定義のみ。
6. `CURRENT_SPEC.md`: Grep `B-Family.*Voice|Voices.*Key Phrase|3V.*Intro|Navigator|Charon` → B-Family音声構成仕様の該当行のみ。
7. `audio_review_player.py`: Grep `^def |src=|relative|title|level|note` → 引数のみ。
8. `er014_output/four_type_observation_01/voices/production_set_cost.json` 全文。
9. `.gitignore`: Grep `wav|mp3|er014|output|audio`。

## 事前指定Grep一覧+追記位置・更新位置の手順

- driver `voices/run_voices_2v_audio_completion.py`(新規、既存関数の最小接続、budget_jpy=150)。出力は上記(6)(7)(9)。`progress_log.md`1行追記。er012_*変更は追加のみ(2V音声接続用の最小関数/分岐)、変更箇所をRESULT_PACKETにdiff要約で記載。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-AUDIO-COMPLETION-01-VOICES.md --json-out docs\pm\delegation_log\USER-TEST-AUDIO-COMPLETION-01-VOICES_check.json`
2. `.venv\Scripts\python.exe er014_output\four_type_observation_01\voices\run_voices_2v_audio_completion.py`(全文コマンド・固定値を記録)
3. er012変更時のみ: `.venv\Scripts\python.exe -m unittest er012_b_family_voices_variable_voice_count_test_01 -v` および `.venv\Scripts\python.exe run_project_regression.py --pattern "er012*_test_*.py"`
4. 確認: `Select-String -Path er014_output\four_type_observation_01\voices\audio\b1_2v\player.html -Pattern "file:///|C:\\" | Measure-Object -Line`(0件)
5. `git check-ignore -v er014_output/four_type_observation_01/voices/audio/b1_2v/web/episode.mp3`

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-151末尾追記案(「音声化完了、Status=PARTIAL / USER TEST READY、Leakage残存記録、総原価」。PRODUCTION_WIREDと書かない)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補一覧(サイズ付き、er012変更ファイル含む)」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_UT_VOICES.md`に: 1) 最終Status(`PARTIAL / USER TEST READY`または未完成)、2) 使用経路とgap/最小接続(er012変更の有無・diff要約・テスト結果)、3) Preview/Comment 1〜4(テキスト、Contract検証、segment音声名、timeline位置)、4) Fact Safety Gate発火記録、5) Key Phrase 5件(phrase/gloss、Validator結果)、6) TTS(call数、retry/fallback、voice割当)、7) Audio Validation結果、8) 完成episode duration、9) 記事⇔音声一致確認、10) 残存Leakage原文の記録場所、11) mp3一覧・player相対参照確認・予定URL・gitignore確認、12) 費用: 音声化追加費(要素別)、**Voices Production 1生成セット総原価=¥140.39+追加=¥xx.xx**、13) model_id/TTS model、14) Open Item候補、15) commit対象候補一覧、16) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥150)
- [x] 並行タスク衝突回避あり(voices/配下+er012追加のみ・Git操作なし)
