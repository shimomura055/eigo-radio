## 管理ID

PM-CLOSEOUT-CONSOLIDATION-133(USER-TEST-AUDIO-COMPLETION-01 成果物のGit記録・Web到達確認・SSOT反映・最終REPORT)
並行タスク衝突確認: 並行タスクなし。本タスクがGit・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを扱う唯一のタスク。

## 性質/到達上限Status/禁止事項

- 性質: Git記録・Web到達確認・SSOT反映・REPORT作成のみ。**API呼び出し(LLM/TTS)禁止、費用¥0**。Production/Trialコード変更禁止。
- 反映する事実(Fable照合済み。各RESULT_PACKETの値を使い、自己評価で格上げしない):
  - **Family C / Home robots**(`docs/pm/RESULT_PACKET_UT_FAMILYC.md`): Trial-09 VALIDATED不変。WAVは`.gitignore`の`*.wav`で除外されていた(前回commitに未収録の原因)。mp3化(完成episode+segment38件、soundfile、追加費¥0)、player相対パス化、`file:///`不在テスト追加(22件PASS)。
  - **Trend**(`RESULT_PACKET_UT_TREND.md`、`_2.md`): B1B=完成(Gate PASS、364.7秒、mp3・player生成済み)。A2=未完成(`point_two`「Alexa+」がASRで双方向に表記揺れ、読み整形後もHuman Review Cost Guardでロック、承認代行せずSTOP)。読み整形一覧`trend/audio/tts_reading_transforms.json`(Markdownリンク除去、Alexa+→Alexa Plus、natural-language→natural language)。B1B comment_4は既存Scaffold経路で再生成。音声化費=前回¥122.15+今回¥38.00=¥160.15。Trend Production 1生成セット総原価=本文¥174.03+音声化(A2途中分含む実費)¥160.15=**¥334.18**(RESULT_PACKET_2は「B1B完成分¥160.16」と表記しているが、Fable判断: 15-8「総原価」はA2未完成分の実費も含めて報告する。完成B1Bのみの内訳と、A2未完成分の実費を別行で示す)。
  - **Discovery**(`RESULT_PACKET_UT_DISCOVERY.md`、`_2.md`): B1B Key Phrase=人手選定完了(5件: nothing to do but think/reduced the feeling of connection/being in the present moment/actively choosing solitude/complicates any simple cultural story、canonicalization PASS/Redundancy PASS、have agency除外理由記録、Validator無変更)。A2=完成(Gate PASS、480秒、mp3・player)。B1B=未完成(`full_story_part2`で「In a study of 2,557 college students…」の1文をTTSが読み飛ばし、数字読み整形後も3回再発、ロック、STOP)。総原価=¥463.27+音声化¥85.51+¥16.32=**¥565.10**(Key Phrase B1B人手選定のLLM 2呼び出しは推定¥1〜6・ログ未記録、別記)。
  - **Voices**(`RESULT_PACKET_UT_VOICES.md`、`_2.md`): Status=**PARTIAL / USER TEST READY**(PRODUCTION_WIRED禁止、OPEN-151のStatusはPARTIALのまま)。Comment 2を既存Comment Contract経路で再生成(Preview+Comment1〜4全件、LEDGER_COMPLIANT)、run1のKey Phrase音声未生成バグを既存関数で補完、Gate PASS 14/14、309.5秒、mp3 3.5MB、Leakage残存(voice_b 5項目/tension 2項目)はplayer本文と`comment_fact_safety_evidence.json`に明記。総原価=¥140.39+¥32.34+¥13.01=**¥185.74**。
  - **Human Review Lockの扱い(Fable判断、DECISION_LOGに記録)**: `approve_regenerate()`は全タスクで未使用。根本原因(URL/記号/数字読み/挿入句)を除いた別テキストの初回生成として処理(lockキー=canonical_text_sha256が別)。旧lockエントリは無編集。
  - **新規Open Item登録(ユーザー指示「Open Item化する」+Fable判断)**: OPEN-152「Key Phrase選定Validatorが語彙動詞have/has(例: have agency)を有限助動詞ブロックリストで誤検知」(Discovery B1B 4回+人手選定で回避、Production Validator無変更、Status: USER_DECISION_REQUIRED、優先度MEDIUM)。OPEN-153「音声化経路のTTS入力前処理・TTS読み飛ばし系gap集約」(サブ項目: (a)Markdownリンク・記号(+)・ハイフン複合語の読み整形未実装[driver暫定]、(b)算用数字の読み整形、(c)長文segmentでの1文丸ごと読み飛ばし[Discovery B1B、再現3/3]、(d)Comment挿入句の読み飛ばし[Voices、再生成で回避]、(e)ブランド名「Alexa+」のASR双方向揺れ[Trend A2ロック中]、(f)B-Family write_new_theme経路がKey Phrase音声を生成しない[Voices、driver側補完]、(g)Voices run1のtts_generation_resultsがKey Phrase音声status=OKを空記録したバグ; Status: USER_DECISION_REQUIRED、優先度HIGH[ユーザー実検証を直接阻害])。
- 禁止: `git add -A`/`.`/`stash`/`clean`/`amend`/`rebase`/`force push`、API呼び出し、Production/Trialコード変更、`.gitignore`変更、`*.wav`のadd、gitignore対象(`docs/pm/ACTIVE_TASK.md`)のadd、SSOT全文Read。RESULT_PACKET_UT_*.mdは`git check-ignore -v`で追跡可否を確認し追跡対象のもののみadd。

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

> 最終報告は対象ごとに簡潔に: Family C(Web player URL/direct audio URL/playback確認/追加費用)、Trend(A2 player URL/B1 player URL/Audio Validation結果/完成episode duration/追加音声化費/最終Production 1生成セット総原価)、Discovery(人手選定したB1 Key Phrase 5件/have agencyを外した理由/Validator問題Open Item ID/A2/B1 player URL/Audio Validation結果/最終総原価)、Voices(2V player URL/Audio Validation結果/Comment・Fact Safetyが実際にepisodeへ反映された証拠/残存Leakageの記録/Status=PARTIAL / USER TEST READY/最終総原価)。最後に「ユーザーが今クリックして試聴すべきURL」だけを4対象分まとめて再掲。最低限: GitHub上に実音声ファイルが存在/playerがfile:///を参照していない/ユーザーのブラウザからアクセス可能/完成episodeを再生可能/A2/B1がある場合は明確に分離/player上でTitle・level・episode音声が判別可能。file:///のローカルリンクは最終報告に出さない。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_UT_FAMILYC.md`、`RESULT_PACKET_UT_TREND.md`、`RESULT_PACKET_UT_TREND_2.md`、`RESULT_PACKET_UT_DISCOVERY.md`、`RESULT_PACKET_UT_DISCOVERY_2.md`、`RESULT_PACKET_UT_VOICES.md`、`RESULT_PACKET_UT_VOICES_2.md` 各全文(REPORT素材・commit対象候補一覧)。
2. `OPEN_ITEMS.md`: Grep `^\| OPEN-135|^\| OPEN-147|^\| OPEN-151|^\| OPEN-15[0-9]` → 該当行と最終行番号(新規行追加位置)。Grep `^\| OPEN-1[0-9][0-9] \|` -c → 現在の最大番号確認(152/153が未使用であること)。
3. `DECISION_LOG.md`: Grep `PM-CLOSEOUT-CONSOLIDATION-132` → 直近エントリ位置と索引行。
4. `docs/pm/PM_GOVERNANCE.md`: Grep `^### 11-\d+|^11-\d+\.|11-x` → 11節の既存最大項番と、CONS-132で追加した「11-x」見出しの位置(正しい連番へ訂正)。
5. `er014_output/four_type_observation_01/index.html`: Grep `<h[1-6]|<tr|href=` → player/mp3リンク追加位置。
6. `docs/pm/PM_BRIEF.md` L133-157(ACTIVE_TASK固定ヘッダ書式)。
7. 各player.html: Grep `src=|href=` → 参照先が相対パスであること(4件+Trend A2は未生成)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- (a) Git: `git status --porcelain -- er013_output/family_c_episode_trial_09 er013_family_c_episode_trial_09_run.py er013_family_c_episode_trial_09_test_01.py er014_output/four_type_observation_01 docs/pm` で対象確認 → 明示add(各RESULT_PACKETのcommit対象候補一覧に従う。mp3・player.html・JSON・md・driver・delegation_log。wav除外)→ commit → `git push origin main`(classifierブロック時は同一コマンド最大3回再試行、bypass禁止)。
- (b) **Web到達確認(push後)**: PowerShell `Invoke-WebRequest -Method Head -Uri <url>`(または`curl.exe -sI`)で以下を確認しStatusCode・Content-Length・Content-Typeを`docs/pm/web_playback_check_UT01.json`へ記録: 直接音声4件=`https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er013_output/family_c_episode_trial_09/home_robots/web/family_c_home_robots_trial_09.mp3`、`.../er014_output/four_type_observation_01/trend/audio/b1b/web/episode.mp3`、`.../discovery/audio/a2/web/episode.mp3`、`.../voices/audio/b1_2v/web/episode.mp3`。player4件=`https://raw.githack.com/shimomura055/eigo-radio/main/<同path>/player.html`(HTTP 200かつContent-Type text/html)。さらに各player.htmlをGETし、内部の`src=`相対参照を同じbase URLで解決してHEADが200になること(完成episodeと先頭3 segment)を確認。raw.githubusercontentのCDN反映遅延で404の場合は60秒待って最大3回再試行。ブラウザ実再生はユーザー確認とする旨を明記(自動確認=HTTP取得+mp3ヘッダ/サイズ一致)。
- (c) 最終REPORT `USER-TEST-AUDIO-COMPLETION-01_REPORT.md`(新規root): ユーザー指定形式(対象別: Family C/Trend/Discovery/Voices)+「未完成2件(Trend A2・Discovery B1B)の実施済み対応/残った問題/ユーザー判断の選択肢」+Human Review Lockの扱い(Fable判断)+費用表(15-8: 各Family総原価と今回音声化差分、Family Cは開発・Trial費¥0差分)+Web到達確認結果+**「ユーザーが今クリックして試聴すべきURL」4件の再掲**(URLのみ)。file:///は記載しない。
- (d) `index.html`にplayer/mp3リンク(Web URL)を追加。
- (e) SSOT: `OPEN_ITEMS.md` OPEN-135末尾(Trend B1B完成/A2ロック、Discovery A2完成/B1Bロック、総原価、commit)、OPEN-147末尾(Family C Web導線修正、mp3、¥0)、OPEN-151末尾(音声化完了、PARTIAL / USER TEST READY、Leakage残存、¥185.74、PRODUCTION_WIREDと書かない)、新規行OPEN-152・OPEN-153(既存行の書式に合わせる)。`DECISION_LOG.md`: CONS-132直後に`## PM-CLOSEOUT-CONSOLIDATION-133`(4対象の結果、Human Review Lock判断、Open Item登録、費用、commit)+索引1行。`docs/pm/PM_GOVERNANCE.md`: 「11-x」見出しを実際の次番号へ訂正(内容不変)。`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`に音声化run 4行(TTS model/ASR model)。
- (f) ACTIVE_TASK固定ヘッダ更新(管理ID=CONS-133、報告単位Status: User test audio=Family C READY/Trend B1B READY・A2 UDR/Discovery A2 READY・B1B UDR/Voices PARTIAL / USER TEST READY)。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-133.md --json-out docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-133_check.json`
2. (a)のgitコマンド。commit後`git log --oneline -2`。
3. (b)の到達確認(PowerShell)。例: `Invoke-WebRequest -Method Head -Uri "https://raw.githubusercontent.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/voices/audio/b1_2v/web/episode.mp3" | Select-Object StatusCode, @{n='len';e={$_.Headers['Content-Length']}}, @{n='type';e={$_.Headers['Content-Type']}}`
4. SSOT/REPORT/index更新後、2回目commit(`PM-CLOSEOUT-CONSOLIDATION-133: SSOT反映+最終REPORT+Web到達確認結果`)→push。(音声・playerのcommitを先に行い、到達確認結果を含む文書を2回目でcommitする2段構成。)
5. push後: `git status --porcelain | Measure-Object -Line`(残差分要約)。
(回帰: Family Cタスクで`er013_family_c_episode_trial_09_test_01.py`が変更済み→`.venv\Scripts\python.exe run_project_regression.py --pattern "er013_family_c_episode_trial_09_test_*.py"`を1回実行しPASS確認。)

## SSOT追記文

上記(e)に従い実値で記載。PARTIALをOK/PRODUCTION_WIREDと書かない。未完成をREADYと書かない。

## Git(明示add対象・コミットメッセージ・trailer)

- 1回目メッセージ: `USER-TEST-AUDIO-COMPLETION-01: Web試聴成果物(Family C mp3/player、Trend B1B、Discovery A2、Voices 2V)+A2/B1B途中成果+driver` の後に空行、末尾に
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4`
- 2回目メッセージ: `PM-CLOSEOUT-CONSOLIDATION-133: USER-TEST-AUDIO-COMPLETION-01のSSOT反映+最終REPORT+Web到達確認+OPEN-152/153登録` +同trailer。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`(上書き)に: 1) commit hash 2件(full)・push結果、2) Web到達確認結果表(URL/StatusCode/Content-Length/Content-Type、player内相対参照の解決結果)、3) 最終REPORTパス、4) SSOT追記位置(OPEN-135/147/151/152/153、DECISION_LOG、PM_GOVERNANCE項番訂正)、5) 回帰結果、6) 費用表(15-8)、7) 「ユーザーが今クリックして試聴すべきURL」4件、8) T-0結果・事前指定外Read、9) push後残差分要約、10) ACTIVE_TASK更新済み。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥0)
- [x] 並行タスク衝突回避あり(単独)
