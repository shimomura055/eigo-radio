## 管理ID

`USER-TEST-LEGACY-WEB-AUDIO-EXPORT-02`
並行タスクなし(直近commit `7459c176`)。報告は`docs/pm/RESULT_PACKET_LEGACY_WEB_AUDIO_EXPORT.md`(新規)へ。`docs/pm/ACTIVE_TASK.md`は固定ヘッダ形式で上書き可。

## 性質/到達上限Status/禁止事項

- 性質: ChatGPT側でのWeb再生player作成・Google Sheetハイパーリンク追加のため、ローカルに存在する既存完成音声のみをWeb配信用MP3としてRepoへ保存する。**音声実体のexportだけ**。前タスク`USER-TEST-WEB-AUDIO-EXPORT-01`(`docs/pm/RESULT_PACKET_WEB_AUDIO_EXPORT.md`、変換スクリプト方式: soundfile+ffmpeg/lame、import=os/re/hashlib/json/soundfileのみ)と同一方式で実施。
- 到達上限Status: `WEB_AUDIO_EXPORTED / USER_TEST_PREP`のみ。`VALIDATED`/`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`への変更禁止(これはProduction作業ではない)。
- 対象(6 level): (1) A02 英国SNS門限 **B1のみ**(ER-003-REPRO-01でユーザー試聴PASSした完成音声、2026-08-08。A2は対象外)。(2) ADD03 ホルムズ海峡 **B1のみ**(ER-003-REPRO-FINALでユーザー試聴PASSした完成音声、2026-08-09。A2は対象外)。(3) Hanshin **A2/B1**(`er003_output/n3_01/hanshin/`、ARTIFACT_REGISTRY.mdで「Full Audio 完成」と記録されたもの)。(4) Health **A2/B1**(`er003_output/n3_01/health/`、ARTIFACT_REGISTRY.mdで「Full Audio 完成」と記録されたもの。**FIX-01後に再assembleされたものがあればそれを使用**)。
- 禁止: TTS再生成、API call(**0件**)、Article/Scaffold/Assembly再生成、Comment/Key Phrase/Prompt変更、Fact Checker/Ledger再実行、Web Search、Validator追加、QA改善Trial、Production runner変更、`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`変更、Production wiring、unrelated fix、player.htmlの作成・修正、Google Sheet修正、記事修正、`git add -A`/`stash`/`amend`、wavのcommit。
- **完成版の選択**: 複数のWAV候補がある場合、勝手に最新版らしきものを選ばない。上記の対象別基準(REPRO-01 PASS音声/REPRO-FINAL PASS音声/Registry「Full Audio 完成」/Health FIX-01後)で一意に確定し、根拠(Registry行・REPORT行・run_summary等)をmanifestとRESULT_PACKETに記録。
- STOP条件(該当対象のみ停止し`USER_DECISION_REQUIRED`で報告、他対象は続行、再生成しない): 該当完成WAVがローカルに存在しない/完成版候補が複数あり一意に決められない/Registry記録とローカルartifactが矛盾/音声変換だけではWeb配信用素材を作れない/GitHub file size制限等でpush不可/A02・ADD03でPASS済み音声とは別versionしか見つからない。segment exportが大きな追加作業になる場合はepisode全文MP3を優先し、segment未対応として報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

---
目的: ChatGPT側で以下4テーマのWeb再生player作成・Google Sheetへのハイパーリンク追加を行えるようにするため、Claude Codeローカルに存在する既存完成音声のみをWeb配信用MP3としてRepoへ保存する。今回は音声実体のexportだけを行う。player.htmlの作成・修正、Google Sheet修正、Productionコード変更、記事修正は行わない。

対象: 1. A02 英国SNS門限 — B1(既存完成音声・ユーザー試聴PASS済み。根拠: ARTIFACT_REGISTRY.md/User Quality PASS/ER-003-REPRO-01/2026-08-08。対象はB1のみ。A2は今回対象外[最新scriptと既存音声の不一致があり、再assemble要])。2. ADD03 ホルムズ海峡 — B1(既存完成音声・ユーザー試聴PASS済み。根拠: ARTIFACT_REGISTRY.md/User Quality PASS/ER-003-REPRO-FINAL/2026-08-09。対象はB1のみ。A2は今回対象外)。3. Hanshin — A2 / B1(既存完成音声あり。根拠: er003_output/n3_01/hanshin/、A2/B1ともFull Audio完成、Ledger / Fact QA完了、User Quality = NOT_REVIEWED)。4. Health — A2 / B1(根拠: er003_output/n3_01/health/、A2/B1ともFull Audio完成、Ledger / Fact QA完了、Health FIX-01反映済み、User Quality = NOT_REVIEWED)。

実施内容: 各対象について、現在ローカルに残っている既存完成版のassembled audioを特定する。必須: 既存WAV等からMP3へ変換し、各対象ディレクトリ配下にWeb配信用ファイルを保存する。原則: web/episode.mp3。A2/B1が同じtheme directoryに共存し、同じweb/を使う場合は、web/episode_a2.mp3/web/episode_b1.mp3としてよい。可能なら既存player相当のsegment単位試聴を後でChatGPT側で作れるよう、web/segments/<segment_name>.mp3も既存narration WAVから変換する。ただし、segment exportが大きく追加作業になる場合は、episode全文MP3を優先する。

export_manifest: 各theme / levelについて、後からChatGPTがplayerを自動構築できるように、web/export_manifest.jsonを作成する。最低限、level/role/元WAV path/出力MP3 path/src sha256/duration/size/segment nameを記録する。A2/B1共通manifestでも、別manifestでも可。

重要: 完成版の選択。複数のWAV候補がある場合、勝手に最新版らしきものを選ばない。A02 B1: ER-003-REPRO-01でユーザー試聴PASSした完成音声。ADD03 B1: ER-003-REPRO-FINALでユーザー試聴PASSした完成音声。Hanshin: ARTIFACT_REGISTRY.mdで「Full Audio 完成」と記録されているA2/B1。Health: ARTIFACT_REGISTRY.mdで「Full Audio 完成」と記録されているA2/B1。FIX-01後に再assembleされたものがある場合は、それを使用。

Git: 作成したWeb配信用MP3とmanifestのみcommit / pushする。既存player.htmlは変更しない。Production code / SSOT / DECISION_LOG / OPEN_ITEMSも今回は変更しない。

受入条件: A02 B1/ADD03 B1: web/episode.mp3相当がRepoに存在。Hanshin A2/B1・Health A2/B1: Web用episode MP3あり。すべてpush済み/raw GitHub URLから取得可能/TTS/API call = 0/元完成音声からの変換のみ。

完了報告: 表(Theme/Level/元完成音声/Web MP3 path/segment export/raw取得/備考)+ 6 level分すべてexportできたか/segmentもexportしたか/manifest path/commit SHA/push結果/TTS/API call 0であること/未対応対象の有無/USER_DECISION_REQUIREDの有無。不要な追加調査・品質改善・Production対応は行わず、本タスク終了後STOPする。
---

## 事前指定Read一覧

- `ARTIFACT_REGISTRY.md`: Grepで`A02|SNS門限|ADD03|ホルムズ|Hanshin|hanshin|Health|health|Full Audio|User Quality|REPRO-01|REPRO-FINAL|FIX-01`→該当行(各対象の完成音声path・Status・根拠の記録行のみ)
- `ER-003-REPRO-01_REPORT.md`・`ER-003-REPRO-FINAL_REPORT.md`(Globで実ファイル名を確定、`ER-003-REPRO*_REPORT.md`): Grepで`assembled|\.wav|final|PASS|試聴|B1`→A02 B1/ADD03 B1のユーザー試聴PASS音声の実path行のみ
- Health FIX-01の記録: Glob`*HEALTH*FIX*_REPORT.md`または`Grep pattern="Health FIX-01|HEALTH-FIX-01" glob=*.md output_mode=files_with_matches`→該当REPORTのGrep`assembled|re-assemble|再assemble|\.wav`→FIX-01後の完成音声path行
- output directory: Glob`er003_output/n3_01/hanshin/**/*.wav`、`er003_output/n3_01/health/**/*.wav`、A02/ADD03のB1完成音声ディレクトリ(Registry/REPORTで確定したpath配下)のGlob`**/*.wav`→候補一覧(assembled/final系と個別narration系を区別)。`run_summary_assemble.json`・`timeline.json`等があればGrepで元segment一覧を確定。
- `docs/pm/RESULT_PACKET_WEB_AUDIO_EXPORT.md`: 1-30行(前タスクの変換方式・manifest構造。同形式を踏襲)
- `docs/pm/PM_BRIEF.md`: 135-159行

## 事前指定Grep一覧+追記位置・更新位置の手順

1. 完成版の一意確定(対象別): A02 B1=REPRO-01 REPORTで「ユーザー試聴PASS」と紐づく完成wav(Registry行と一致確認)。ADD03 B1=REPRO-FINAL REPORT同様。Hanshin A2/B1=Registry「Full Audio 完成」記録のpath(`er003_output/n3_01/hanshin/`配下のassembled最終wav)。Health A2/B1=同上+FIX-01後再assemble版があればそれ(REPORTとファイルmtime/run_summaryで裏付け)。**候補が複数あり基準で一意にならない、Registry記録とローカルが矛盾、A02/ADD03でPASS版と別versionしか無い場合は当該対象をSTOP(USER_DECISION_REQUIRED)**として候補と根拠を列挙し、他対象は続行。
2. 出力先: 各theme directory配下`web/`。A2/B1が同一theme directoryを共有する場合(Hanshin/Health想定)は`web/episode_a2.mp3`・`web/episode_b1.mp3`。A02/ADD03のB1は`<B1 dir>/web/episode.mp3`(A2と同一dirなら`episode_b1.mp3`)。segment: `web/segments/<segment_name>.mp3`(既存narration wavのstemをそのまま使用、level混在時は`a2_`/`b1_`プレフィックス等でmanifestに対応関係を記録)。
3. manifest: `web/export_manifest.json`(theme単位1件、A2/B1両方のエントリ)に各エントリ{theme, level, role(episode|segment), segment_name, src_wav_path, out_mp3_path, src_sha256, duration_sec, size_bytes, selection_basis(Registry行/REPORT名/FIX-01)}。
4. 変換: 前タスクのスクラッチパッド方式(`soundfile`読み+ffmpeg/lame書き、`-b:a 128k`)。既存mp3が正式完成版として存在すればコピー。スクリプトはスクラッチパッド`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\7464676f-2545-4919-a668-1fdd436c9816\scratchpad\export_legacy_web_audio_02.py`に置きrepoには置かない。importにネットワーク/LLM/TTS/er0*系productionモジュールを含めない。
5. サイズ確認(各mp3 100MB未満)→明示`git add`(mp3+manifestのみ)→commit→push→raw URL(`https://raw.githubusercontent.com/shimomura055/eigo-radio/main/<path>`)へUser-Agent+Range付きGETで取得確認(206/200、CDN遅延時60秒待ち最大3回)。

## 実行コマンド全文

作業ディレクトリ`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-LEGACY-WEB-AUDIO-EXPORT-02.md --json-out docs\pm\delegation_log\USER-TEST-LEGACY-WEB-AUDIO-EXPORT-02_check.json
```
候補一覧(read-only):
```
.venv\Scripts\python.exe -c "import glob,os,time;[print(p, os.path.getsize(p), time.strftime('%Y-%m-%d %H:%M',time.localtime(os.path.getmtime(p)))) for pat in ['er003_output/n3_01/hanshin/**/*.wav','er003_output/n3_01/health/**/*.wav'] for p in sorted(glob.glob(pat,recursive=True)) if 'assembled' in p.lower() or 'final' in p.lower() or 'episode' in p.lower()]"
```
(A02/ADD03はRegistry/REPORTで確定したディレクトリに対して同様に実行。実引数全文を報告。)
変換:
```
.venv\Scripts\python.exe C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\7464676f-2545-4919-a668-1fdd436c9816\scratchpad\export_legacy_web_audio_02.py
```
Web到達確認(push後、出力pathは実結果に置換):
```
.venv\Scripts\python.exe -c "import urllib.request as u,sys;[print(u.urlopen(u.Request('https://raw.githubusercontent.com/shimomura055/eigo-radio/main/'+p,headers={'User-Agent':'Mozilla/5.0','Range':'bytes=0-1023'})).status,p) for p in sys.argv[1:]]" <episode mp3 path 1> <path 2> ... <path 6>
```
API 0件証跡: 変換スクリプトのimport行一覧をRESULT_PACKETに記載。無変更証跡: `git show --stat <commit>`にplayer.html/wav/SSOT/`.py`(repo内)が含まれないこと、`git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md`が空。

## SSOT追記文

なし(SSOT/DECISION_LOG/OPEN_ITEMS変更禁止)。`docs/pm/ACTIVE_TASK.md`のみ固定ヘッダ形式で上書き(Status: Legacy 4テーマ6 levelのWeb音声export結果、到達Status=WEB_AUDIO_EXPORTED / USER_TEST_PREP。UDR-deferred/APPROVED未配線欄は前回内容[Family C 2仕様=APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE、Discovery B1/A2個別対応、OPEN-154/155、Voices Priority 2着手待ち、AI hiring A2試聴待ち]を引継ぎ)。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add対象: 各theme`web/episode*.mp3`、`web/segments/*.mp3`(exportした場合)、`web/export_manifest.json`、`docs/pm/delegation_log/USER-TEST-LEGACY-WEB-AUDIO-EXPORT-02.md`、同`_check.json`、`docs/pm/RESULT_PACKET_LEGACY_WEB_AUDIO_EXPORT.md`。
- 触らない: player.html、wav、SSOT、Productionコード、既存の無関係な未commit差分。
- コミットメッセージ: `USER-TEST-LEGACY-WEB-AUDIO-EXPORT-02: A02 B1/ADD03 B1/Hanshin A2・B1/Health A2・B1の既存完成音声をWeb配信用MP3へexport(TTS/API 0、player/SSOT無変更)`
- trailer: `Task-ID: USER-TEST-LEGACY-WEB-AUDIO-EXPORT-02`
- push: `git push origin main`。サイズ起因の失敗はSTOP条件として報告。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_LEGACY_WEB_AUDIO_EXPORT.md`に簡潔に:
1. T-0結果
2. 表: Theme/Level/元完成音声(path+一意確定の根拠[Registry行・REPORT名・FIX-01])/Web MP3 path/segment export(件数または未対応理由)/raw取得(HTTP status)/備考
3. 6 level分すべてexportできたか/segmentもexportしたか/manifest path一覧/commit SHA/push結果/TTS・API call 0の証跡(import一覧)/未対応対象の有無と理由/`USER_DECISION_REQUIRED`の有無(あれば候補・根拠・最小の選択肢のみ)
4. 無変更証跡(`git show --stat`にplayer.html/wav/SSOT/.pyなし)
5. 事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一(「B1B」不使用、内部識別子`b1b`はpathにのみ可)。
