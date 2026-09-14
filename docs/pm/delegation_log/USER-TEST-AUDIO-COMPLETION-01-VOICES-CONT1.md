## 管理ID

USER-TEST-AUDIO-COMPLETION-01-VOICES(継続CONT1、Fable修正指示1回目)
並行タスク衝突確認: 並行して Trend音声化継続(.../trend/)、Discovery音声化(.../discovery/)が走る。本タスクはer014_output/four_type_observation_01/voices/配下のみを書き(er012_*は前回同様無変更)、Git・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを触らない。RESULT_PACKETはdocs/pm/RESULT_PACKET_UT_VOICES_2.md(新規)。

## 性質/到達上限Status/禁止事項

- 性質: 前回(docs/pm/RESULT_PACKET_UT_VOICES.md)で14 segment中13 OK、comment_2のみTTSが挿入句 "one after the other. Each" を3回とも読み飛ばしTRUE_CONTENT_MISMATCH→Human Review Cost Guardで停止。Status上限=PARTIAL / USER TEST READY。PRODUCTION_WIRED禁止。OPEN-151のStatusを変えない。
- 対応方針(Fable判断、既存仕様内): 記事本文(2V canonical candidate)は一切変更しない。Comment 2は補助生成テキスト(Comment Contract経路で生成)であり、既存の接続済みComment Contract経路(-02タスクでrun_comment_contract_for_new_theme()に接続した既存関数、またはrun2_cleanで使われた同一関数)でComment 2を再生成し(Contract検証=Ledger Deviation Checkを含む既存経路そのまま、最大2回)、新テキストでTTS(既存上限どおり)を行う。可能ならComment 2のみ再生成、関数が全件生成しかできない場合はComment 1〜4+Previewを再生成し、変更されたsegmentのみ再TTS(既存OK分のwavは、テキストが同一なら再利用)。旧Comment 2テキスト・新テキスト・Contract検証結果をcomment_2_regeneration.jsonに記録。
- Human Review Lockの扱い(重要): approve_regenerate()は呼ばない。新テキストはlockキー(canonical_text_sha256)が別になるため通常の初回TTS/ASRとして扱う。旧lockエントリは削除・編集しない。「同一テキストの再試行ではなく、読み飛ばしを誘発した文の既存経路による再生成」であることをRESULT_PACKETに明記。新テキストでも既存上限まで失敗した場合はSTOP(承認代行禁止)。
- 続き(前回未到達分): Assembly(既存B-Family仕様、run_assembly()と同一の下位primitive呼び出し)→Audio Validation Gate(緩和禁止)→完成episode WAV+MP3(er013_output/family_c_episode_trial_09/build_web_delivery.pyと同じsoundfile.write(format="MP3")方式)→標準Audio Review Player(相対パス、Title/level=B1 2V、Status注記「PARTIAL / USER TEST READY(Analytical Leakage残存)」、voices/audio/b1_2v/player.html、web/episode.mp3、web/segments/*.mp3)→記事⇔音声一致確認(article_audio_consistency.json)→comment_fact_safety_evidence.json(Comment 1〜4+Previewのテキスト・Contract検証・segment音声名・timeline位置、Fact Safety Gate記録[run2_clean時の非発火理由の転記]、Leakage残存原文[run2_clean/b1_2v_new_theme_attempt3/analytical_leakage_check_2v_attempt3.jsonの項目名・原文])→gitignore確認・mp3<50MB→費用更新(voices/audio/cost_summary_audio.json、voices/production_set_cost.json: Voices総原価=¥140.39+前回¥32.34+本タスク実費、差分明記)、progress_log.md1行追記。
- 費用上限: 本タスク¥60。段階ごとに次段階見込み込みで事前判定。
- 禁止: 記事再生成/Writer retry/MAX_WRITER_ATTEMPTS変更/Leakage・Fact Safety Gate緩和/Prompt変更/approve_regenerate()呼び出し/lockファイル編集/PRODUCTION_WIRED表記/新player仕様/er012_*変更/.gitignore変更/pip install/Git commit・push/run_project_regression.py --patternに_testを含まないglob/PATH上の素python。
- STOP条件: 新Production仕様が必要/Gate緩和が必要/canonical記事変更が必要/費用上限超過見込み/新Comment 2でも既存上限まで失敗/技術的にWeb配信不可。STOP時は「何を試したか/何が残ったか/ユーザーに必要な判断」を提示(その場合、attempt3音声narration/attempts/comment_2_attempt3_englishstyleprefix.wavをmp3化してvoices/audio/b1_2v/web/review/comment_2_attempt3.mp3に置き、ユーザー試聴用に提示)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は--porcelain/--stat/--short等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0: 受領した委任文をdocs/pm/delegation_log/<管理ID>.mdへ保存し、python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.jsonを実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する。

## ユーザー指示(原文)

現在の2V canonical candidateを使って、接続済みComment Contract/2V対応済みFact Safety Gate/Preview/Key Phrase/TTS/2V Voice構成/Assembly/Audio Validation/完成episode/Web試聴playerまで進める。MAX_WRITER_ATTEMPTSを増やさない/Leakage Gateを緩めない/Prompt改善Trialを始めない。残存Leakageがある事実は、試聴対象から隠さず内部記録に残す。音声化できても、OPEN-151自体を勝手にPRODUCTION_WIREDにしない。Statusは PARTIAL / USER TEST READY 等、実態が分かる表記にする。

## 事前指定Read一覧

1. docs/pm/RESULT_PACKET_UT_VOICES.md 全文(前回到達点)。
2. er014_output/four_type_observation_01/voices/run_voices_2v_audio_completion.py 全文(前回driver。Comment 2再生成段階とAssembly以降を追加してrun_voices_2v_audio_completion_2.pyを派生)。
3. er012_b_family_production_runner_01.py: Grep def run_comment_contract_for_new_theme|def run_scaffold|comment_2|support_texts|def run_assembly → Comment生成関数の引数・戻り値と、Assembly呼び出しの該当範囲のみ。
4. er014_output/four_type_observation_01/voices/run2_clean/b1_2v_new_theme/audit/new_theme_comment_contract_summary.json 全文(旧Comment 2テキスト・検証結果)。
5. er011_human_review_lock_01.py: Grep sha256|canonical_text|def check_before_generation → lockキー算出のみ。
6. er013_output/family_c_episode_trial_09/build_web_delivery.py 全文(MP3化方式)。
7. audio_review_player.py: Grep ^def |title|level|src=|note → 引数のみ。
8. er014_output/four_type_observation_01/voices/production_set_cost.json 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 出力: voices/audio/b1_2v/{comment_2_regeneration.json, b1b/narration/comment_2.wav(新), b1b/assembled/, audio_validation.json, player.html, web/episode.mp3, web/segments/*.mp3, article_audio_consistency.json, comment_fact_safety_evidence.json}、voices/audio/cost_summary_audio.json、voices/audio/web_delivery.json、voices/production_set_cost.json、progress_log.md。

## 実行コマンド全文

(すべて C:\Users\tensh\eigo-radio で実行)
1. T-0: .venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-AUDIO-COMPLETION-01-VOICES-CONT1.md --json-out docs\pm\delegation_log\USER-TEST-AUDIO-COMPLETION-01-VOICES-CONT1_check.json
2. .venv\Scripts\python.exe er014_output\four_type_observation_01\voices\run_voices_2v_audio_completion_2.py(budget_jpy=60。全文コマンド記録)
3. 確認: Select-String -Path er014_output\four_type_observation_01\voices\audio\b1_2v\player.html -Pattern "file:///|C:\\" | Measure-Object -Line(0件)
4. git check-ignore -v er014_output/four_type_observation_01/voices/audio/b1_2v/web/episode.mp3(exit 1=無視されない)
(回帰不要: er012無変更。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-151末尾追記案(音声化完了、Status=PARTIAL / USER TEST READY、Comment 2再生成、Leakage残存記録、総原価。PRODUCTION_WIREDと書かない)と、Open Item案「B-Family Comment文でTTSがカンマ区切り挿入句を脱落させる」を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補一覧(サイズ付き、wav除外・mp3必須)」を列挙。

## 報告(RESULT_PACKET項目)

docs/pm/RESULT_PACKET_UT_VOICES_2.mdに: 1) 最終Status、2) Comment 2再生成(旧→新テキスト、Contract検証結果、再生成回数、他Comment/Previewの変更有無)、3) TTS(新テキストのattempt数、lock非バイパスの説明)、4) Audio Validation結果、5) 完成episode duration、6) 記事⇔音声一致確認、7) Comment/Fact Safety反映証拠(ファイルパスと要約: 各Commentのtimeline位置)、8) 残存Leakage記録場所と項目名、9) mp3一覧・player相対参照確認・予定URL・gitignore確認、10) 費用: 本タスク実費、Voices Production 1生成セット総原価=¥140.39+¥32.34+本タスク=¥xx.xx(音声化追加費内訳)、11) model_id/TTS model・voice割当、12) Open Item候補、13) commit対象候補一覧、14) T-0・事前指定外Read・STOP有無。
