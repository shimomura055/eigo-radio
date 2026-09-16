## 管理ID

`USER-TEST-WEB-AUDIO-EXPORT-01`
並行タスクなし(直近commit `a9fadf34`)。報告は`docs/pm/RESULT_PACKET_WEB_AUDIO_EXPORT.md`(新規)へ。`docs/pm/ACTIVE_TASK.md`は本タスクで上書き可(固定ヘッダ形式)。

## 性質/到達上限Status/禁止事項

- 性質: 現在`file:///C:/...`参照になっている6 playerの既存完成音声を、GitHub Repoから参照可能なWeb配信用MP3として各playerディレクトリ配下`web/`へ保存しcommit/pushする。**音声実体のexportのみ**。ChatGPT側が後でplayerをWeb化するための素材提供が目的。
- 到達上限: export完了報告のみ(Status変更なし)。
- 禁止: TTS再生成、Assembly再実行、記事/Prompt/Voice/Comment/Key Phrase変更、Validator/Fact Checker/Web Search、API呼び出し(**0件**)、`player.html`の修正、SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)編集、Google Sheet変更、Productionコード変更、不要な調査・改善提案・Production wiring、`git add -A`/`stash`/`amend`、wavのcommit(mp3のみcommit)。
- STOP条件(勝手に再生成せず停止・報告): 元WAV(または既存mp3)がローカルに存在しない/どの音声が正式完成版か一意に決められない/MP3変換だけでは対応できない/GitHubのfile size制限等でpushできない(1ファイル100MB超・push拒否等)。該当対象のみSTOPし、他の対象は続行。個別segmentの変換が大きな追加作業(例: segment数が極端に多い・参照解決が複雑)になる場合は、episode全文MP3を優先し、segmentは未対応として報告してよい。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

---
目的: ChatGPT側で既存playerをWeb再生対応へ修正できるようにするため、現在Claude Codeローカルにのみ存在する既存完成音声を、GitHub Repoから参照可能なWeb配信用音声として保存する。今回は音声実体のexportだけを行う。player.htmlの修正、Google Sheet修正、Productionコード変更は行わない。

対象: 以下6 playerで現在 file:///C:/... 参照になっている既存音声。
- Young travelers / slow travel A2: er011_output/family_a_completion_a2_trend_end_to_end_01/a2/rerun_01/player.html
- Young travelers / slow travel B1: er011_output/family_a_completion_a2_trend_end_to_end_01/b1b/kp5_regen_and_completion_01/player.html
- Refrigerator / crisper A2/B1共通: er011_output/household_unified_final_candidate_01/player.html
- Free-address / assigned desk A2: er012_output/editorial_b_family_voices_a2_production_wiring_01/player.html
- Free-address / assigned desk B1: er012_output/editorial_b_family_production_phase1_02/player.html
- AI hiring B1 3V: er012_output/editorial_b_voices_3v_audio_trial_01/player.html

実施内容: 各playerが現在参照している既存のローカル完成音声を利用する。TTS再生成禁止/Assembly再実行禁止/記事・Prompt・Voice・Comment・Key Phrase変更禁止/Validator / Fact Checker / Web Search不要。既存WAVを、必要に応じてローカルでMP3へ変換し、各playerのディレクトリ配下に web/ を作成して保存する。最低限、完成episode全文のMP3は必ず保存すること。可能であれば、player内の個別segment controlsも後でChatGPTがWeb化できるよう、現在playerが参照している個別音声も同じく web/segments/ へMP3化して保存する。ただし、個別segmentの変換が大きな追加作業になる場合は、episode全文MP3を優先してSTOPして報告する。

ファイル名: episode全文は原則 web/episode.mp3。個別segmentは web/segments/<既存segment名>.mp3 とし、後から対応関係が分かるようにする。

Git: 対象音声をcommitしてmainへpushする。Productionコード、player.html、SSOT、Google Sheetには触れない。

受入条件: 各6対象について少なくとも: web/episode.mp3 がRepoに存在/push済み/GitHub/raw URLから取得可能/既存完成音声からの変換のみ/TTS/API呼び出し0。

STOP条件: 元WAVがローカルに存在しない/どの音声が正式完成版か一意に決められない/MP3変換だけでは対応できない/GitHubのfile size制限等でpushできない。

完了報告: 6対象それぞれ web/episode.mp3 作成済みか/個別segmentもexportしたか/作成したRepo path/commit SHA/push結果/未対応対象の有無と理由。不要な調査・改善提案・Production wiringは行わない。本タスク完了後STOPする。
---

## 事前指定Read一覧

- 対象6 `player.html`: それぞれGrepで`file:///|src=|\.wav|\.mp3|audio`→音声参照箇所のみ範囲Read(全文Read不要)。episode全文音声のsrcと個別segment音声のsrc一覧(segment名の取り出し)を確定。
- 各player配下の`web_delivery.json`(存在すれば)Grepで`episode|mp3|wav`→正式完成版episodeファイル名の裏付け。
- 変換ツールの所在: `Grep pattern="ffmpeg|pydub|lameenc|AudioSegment.*export" glob=er014_output/four_type_observation_01/trend/run_trend_audio_completion.py`および`Grep pattern="def .*to_mp3|ffmpeg|export\(.*mp3" glob=er0*.py output_mode=files_with_matches head_limit=5`→既存のwav→mp3変換パターン(前タスクUSER-TEST-VOICES-A2-MINIMAL-01でも`run_trend_audio_completion.py`のmp3変換パターンを流用済み)。既存パターンをそのまま使う(新規ツール導入は最小限、ffmpegがPATHにあればそれを使用)。
- `docs/pm/PM_BRIEF.md`: 135-159行(ACTIVE_TASK固定ヘッダ)。

## 事前指定Grep一覧+追記位置・更新位置の手順

1. 各playerの音声参照を解決: `file:///C:/Users/tensh/eigo-radio/<path>`形式ならrepo相対pathへ変換して実在確認(`Glob`/`os.path.exists`)。episode全文の元ファイル(wavまたは既存mp3)が一意に特定できることを確認(複数候補[例: `assembled/*.wav`と`web/*.mp3`が異なる内容]なら、playerが実際に参照しているものを正とし、`web_delivery.json`・`run_summary_assemble.json`で裏付け。裏付け不能ならSTOP対象)。
2. 変換: ffmpeg(またはリポジトリ既存の変換関数)でwav→mp3(既存パターンのビットレートに合わせる。無指定なら`-b:a 128k`)。既にmp3が正式完成版として存在する場合はコピー(再エンコードしない)。出力: `<player dir>/web/episode.mp3`。個別segment: playerが参照する個別音声を`<player dir>/web/segments/<既存segment名>.mp3`へ(既存ファイル名のstemをそのまま使用)。対象ごとのsegment数が多くても機械変換で済む範囲なら実施、参照解決が複雑・元ファイル不在が多い場合はその対象のsegmentは未対応として報告。
3. 対応表: `<player dir>/web/export_manifest.json`に{元ファイルpath, 出力path, sha256(元), duration秒, 変換方式}を記録(後からChatGPTが対応関係を辿れるように)。
4. サイズ確認: 各mp3が100MB未満、合計が妥当(想定: episode 4〜6MB×6+segments)。
5. Git: 明示`git add`で`web/`配下のmp3と`export_manifest.json`のみ追加(wav除外、player.html・SSOT・コード無変更)。commit・push。push後、各`web/episode.mp3`をraw URL(`https://raw.githubusercontent.com/shimomura055/eigo-radio/main/<path>`)でHTTP GET(Range/HEADでも可、User-Agent付き)して200確認(CDN遅延時60秒待ち最大3回)。

## 実行コマンド全文

作業ディレクトリ`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-WEB-AUDIO-EXPORT-01.md --json-out docs\pm\delegation_log\USER-TEST-WEB-AUDIO-EXPORT-01_check.json
```
音声参照抽出(6 player):
```
.venv\Scripts\python.exe -c "import re,sys;ps=['er011_output/family_a_completion_a2_trend_end_to_end_01/a2/rerun_01/player.html','er011_output/family_a_completion_a2_trend_end_to_end_01/b1b/kp5_regen_and_completion_01/player.html','er011_output/household_unified_final_candidate_01/player.html','er012_output/editorial_b_family_voices_a2_production_wiring_01/player.html','er012_output/editorial_b_family_production_phase1_02/player.html','er012_output/editorial_b_voices_3v_audio_trial_01/player.html'];[print(p,'\n  ','\n   '.join(sorted(set(re.findall(r'(?:src|href)=[\"\\']([^\"\\']+\\.(?:wav|mp3))',open(p,encoding='utf-8').read()))))) for p in ps]"
```
変換スクリプト(スクラッチパッド`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\7464676f-2545-4919-a668-1fdd436c9816\scratchpad\export_web_audio_01.py`に作成、リポジトリには置かない): 上記参照一覧を入力に、ffmpeg(`ffmpeg -y -i <src.wav> -codec:a libmp3lame -b:a 128k <dst.mp3>`)で変換、manifest出力。ffmpegがPATHに無い場合は既存Python変換関数(Grepで特定)を使用。実行:
```
.venv\Scripts\python.exe C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\7464676f-2545-4919-a668-1fdd436c9816\scratchpad\export_web_audio_01.py
```
API/TTS 0件の確認: 変換スクリプトがネットワーク・LLM・TTS moduleをimportしないこと(スクリプト全文をRESULT_PACKETに添付、または`grep -c "import er0\|genai\|openai\|requests" ` が0)。
Web到達確認(push後):
```
.venv\Scripts\python.exe -c "import urllib.request as u;ps=['er011_output/family_a_completion_a2_trend_end_to_end_01/a2/rerun_01/web/episode.mp3','er011_output/family_a_completion_a2_trend_end_to_end_01/b1b/kp5_regen_and_completion_01/web/episode.mp3','er011_output/household_unified_final_candidate_01/web/episode.mp3','er012_output/editorial_b_family_voices_a2_production_wiring_01/web/episode.mp3','er012_output/editorial_b_family_production_phase1_02/web/episode.mp3','er012_output/editorial_b_voices_3v_audio_trial_01/web/episode.mp3'];[print(u.urlopen(u.Request('https://raw.githubusercontent.com/shimomura055/eigo-radio/main/'+p,headers={'User-Agent':'Mozilla/5.0','Range':'bytes=0-1023'})).status,p) for p in ps]"
```

## SSOT追記文

なし(SSOT編集禁止)。`docs/pm/ACTIVE_TASK.md`のみ固定ヘッダ形式で上書き(Status: Web音声export完了/未対応対象、APPROVED未配線欄・UDR-deferred欄は前回内容[Family C 2仕様=APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE、Discovery B1/A2個別対応、OPEN-154/155、Voices Priority 2着手待ち、AI hiring A2試聴待ち]を引継ぎ)。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add対象: 6対象の`<player dir>/web/episode.mp3`、`<player dir>/web/segments/*.mp3`(export した場合)、`<player dir>/web/export_manifest.json`、`docs/pm/delegation_log/USER-TEST-WEB-AUDIO-EXPORT-01.md`、同`_check.json`、`docs/pm/RESULT_PACKET_WEB_AUDIO_EXPORT.md`。
- 触らない: `player.html`、SSOT、Productionコード、wav、`er006_output/`・`er011_output/`の既存M(本タスクで追加する`web/`配下以外)、`docs/pm/ACTIVE_TASK_*.md`/`RESULT_PACKET_*.md`の既存??。
- コミットメッセージ: `USER-TEST-WEB-AUDIO-EXPORT-01: 既存完成音声6 playerのWeb配信用MP3 export(web/episode.mp3[+segments]、TTS/API 0、player/SSOT無変更)`
- trailer: `Task-ID: USER-TEST-WEB-AUDIO-EXPORT-01`
- push: `git push origin main`。サイズ起因でpush失敗時はSTOP条件として報告(commitはローカルに残してよいが、その旨明記)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_WEB_AUDIO_EXPORT.md`に簡潔に:
1. T-0結果
2. 6対象の表: 対象/元音声path(wav or mp3)/一意確定の根拠/`web/episode.mp3`作成済みか/サイズ・duration/個別segment export有無(件数、未対応理由)/raw URL HTTP status
3. 作成したRepo path一覧(episode 6件+segments件数+manifest)
4. commit SHA・push結果
5. 未対応対象の有無と理由(STOP該当があれば内容のみ、再生成は行っていないことを明記)
6. TTS/API呼び出し0件の証跡(変換スクリプトのimport一覧)、player.html/SSOT/Productionコード無変更の証跡(`git status --porcelain`該当パス空、`git show --stat`にそれらが含まれない)
7. 事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一(「B1B」不使用、内部識別子`b1b`はpathにのみ可)。
