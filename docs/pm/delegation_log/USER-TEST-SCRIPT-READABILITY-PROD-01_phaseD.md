## 管理ID

USER-TEST-SCRIPT-READABILITY-PROD-01 / Phase D(Free-Address A2・AI Hiring A2の2 levelについて、現行canonical本文を正としてKey Phraseを再生成・更新し、Key Phrase asset/日本語意味/Pronunciation Ledger/Key Phrase音声/player/Phase Aの`kp_mapping.json`を整合させる)。並行Agentあり: Phase B1/B2(翻訳、`user_test/translations_wip/`配下と`docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01_phaseB{1,2}.md`・`docs/pm/delegation_log/*_phaseB{1,2}.md`のみ書き込み、git操作なし、音声stageなし)。本PhaseはKey Phrase stage(TTS/Ledger/Master Audio Store書き込み)を含む**音声stage**のため、開始時に`docs/pm/locks/audio_stage.lock`を`open(path,"x")`でatomicに取得し(既存なら内容を報告してSTOP)、終了時に削除する(`docs/pm/PM_GOVERNANCE.md` 8節 L741付近のルール)。`docs/pm/ACTIVE_TASK.md`の固定ヘッダ+要約をPhase D内容で更新してよい(Phase Aは完了済み)。

## 性質/到達上限Status/禁止事項

- 性質: Production修正(ユーザー正式判断2026-09-18: 「現行canonical本文を正として、現在の本文からKey Phraseを正しく再生成・更新する。旧Key Phraseに本文を合わせない。本文・記事内容は変更しない。必要な範囲でKey Phrase asset/Key Phrase日本語意味/Pronunciation Ledger/Key Phrase音声を更新。Key Phrase音声再生成が必要なら対象Phraseだけに限定。本文音声・記事本文は再生成しない。」)。
- Phase Dで到達する最大Status: `PHASE_D_DONE`(2 levelの新canonical artifact完成・runtime確認PASS・commit済み・未配線)。Landing page(`user_test/articles_2026_0918.html`)・TSV(`docs/user_test/ユーザーテスト記事一覧_2026-0918_選定10.tsv`)・SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`ARTIFACT_REGISTRY.md`)はPhase Cでまとめて更新するため本Phaseでは変更しない。
- 費用上限: 外部API(TTS/ASR/LLM)合計 ¥150。超過見込みの時点で実行せずSTOP。Key Phrase音声TTSは対象Phrase(各level 5件前後)だけに限定。本文(Hook/Voice/Tension/Closing/Comment/Intro/Preview)のTTS再生成禁止。
- 禁止: 記事本文(article.md/parts.json本文テキスト)変更禁止。本文音声segment変更禁止(新artifactの本文segmentは旧segmentとsha256一致であること)。既存canonical directoryの上書き禁止(旧artifactは履歴として残し、新artifactは新subdirectoryへ作る。`docs/pm/PM_GOVERNANCE.md` 2-3 Artifact supersession確認に従い、新旧の関係をRESULT_PACKETに明記)。`git add -A`/`stash`/`amend`/`rebase`/`force push`禁止。wav commit禁止(mp3は既存運用に従う)。`user_test/unified.html`・`user_test/translations/`のPhase A成果物のうち、対象2 levelの`kp_mapping.json`と`index.json`の該当2行以外は変更しない。
- STOP条件(該当時は`docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01.md`に`## Phase D`節で状況を記録し、lockを削除して終了): (1)現行本文からKey Phraseを既存Key Phrase生成pipelineで安全に再生成できない(pipelineが本文再生成やTTS全体再生成を必ず伴う等)、(2)Pronunciation Ledgerの整合が取れない、(3)Key Phrase音声だけの差し替え・再Assemblyができない(本文segmentの再TTSが必要になる)、(4)再生成したKey Phraseの本文対応箇所が一意に決まらない、(5)canonical本文の変更が必要になる、(6)新しいProduct仕様判断が必要(例: Key Phrase件数を変える、A2向け難易度基準が不明で選定に迷う)、(7)Secondary ASR/Phrase List評価でKey Phrase音声が不一致となりHuman Reviewが必要(その場合は`docs/pm/PM_GOVERNANCE.md` 9-12の試聴提示ルール[raw mp3リンク禁止・発音情報provided・Primary不一致のみではHuman Review不可]に従い、試聴用ページ準備までを行って報告)。判断に迷う点は推測で進めず記録してSTOP。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(本委任の保存先: `docs/pm/delegation_log/USER-TEST-SCRIPT-READABILITY-PROD-01_phaseD.md`)

## ユーザー指示(原文)

「1. 2記事のKey Phrase不整合修正 対象: Free-Address or Assigned Desks? Standard(A2) / When AI Helps Choose Who Gets Hired Standard(A2)。現行canonical本文を正として、現在の本文からKey Phraseを正しく再生成・更新する。旧Key Phraseに本文を合わせない。本文・記事内容は変更しない。必要な範囲で以下を更新: Key Phrase asset / Key Phrase日本語意味 / Pronunciation Ledger / Key Phrase音声。Key Phrase音声再生成が必要なら対象Phraseだけに限定。本文音声・記事本文は再生成しない。」
「2. Key Phrase整合要件 修正後は対象2 levelについて: 全Key Phraseが現行本文由来 / 全Key Phraseに本文中の対応箇所が存在 / 全Key Phraseが水色ハイライトされる / Key Phrase一覧と本文ハイライトが一致 / Key Phrase日本語意味が一致 / Key Phrase音声が一致。旧Key Phraseを残したまま、意味の近い別表現だけをハイライトする方法は禁止。」
「必要であれば各記事の固定SHA URLは変更してよい(Landing/TSVへの反映はPhase Cで実施)」
「14. 再発防止 今回見つかった問題: 本文を後から平易化したのにKey Phrase assetが追従していなかった。これは再発防止対象。Production量産時に『本文変更後はKey Phrase sourceとの整合確認を必須化』するべきか検討し、最低限、今回の原因と再発防止案を報告する。ただし、新しい恒久仕様をユーザー承認なしでProduction採用しない。」
「STOP条件: Key Phraseを現本文から安全に再生成できない / Pronunciation Ledger整合不能 / Key Phrase音声だけの再生成ができない / 対応Phrase判断が曖昧 / canonical本文変更が必要 / 新しいProduct仕様判断が必要」

## 事前指定Read一覧

1. `docs/pm/PM_GOVERNANCE.md` L730-760(8節のlock・並列運用ルール、Grep `audio_stage\.lock` で位置確認)
2. `docs/pm/PM_GOVERNANCE.md` 9-12節(Grep `9-12` → 該当節全体、Human Review試聴提示ルール)
3. `docs/pm/PM_GOVERNANCE.md` 2-3節(Grep `2-3\. Artifact supersession` → 該当節)
4. `user_test/translations/free_address/A2/kp_mapping.json` 全文、`user_test/translations/ai_hiring/A2/kp_mapping.json` 全文(Phase Aの不整合記録)、`user_test/translations/index.json` 全文(対象2行のsrc/key_phrase_asset_path確認)
5. 対象2 levelのcanonical directory: `er012_output/editorial_b_family_voices_a2_production_wiring_01/`(Free-Address A2)と`er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/`(AI Hiring A2)を`Glob`で一覧し、`article.md`/`parts.json`/`keywords_canonicalized.json`(+同ディレクトリの他key_phrases成果物)/`audit/`配下のmanifest・生成ログ/`player.html`または`user_test_simple.html`/`web/episode.mp3`/segment音声の構成を把握(本文article.md・parts.jsonは全文Read可、その他はGrep→範囲Read)。
6. 生成pipeline特定: DECISION_LOG.mdをGrep `editorial_b_family_voices_a2_production_wiring_01`(L8223付近ほか)・`user_test_voices_a2_minimal_01`(L8152・L8679付近ほか)で、各artifactを生成したdriver/script名・Key Phrase生成段階・Assembly方法を特定して該当範囲を読む。Key Phrase再生成の先例として`kp5_regen_and_completion_01`(Grep in DECISION_LOG.md、Young Travelers B1でKey Phrase再生成+完成を行った実績)のエントリを読み、同じ手順・同じ判定Gateを踏襲する。
7. Key Phrase仕様: `CURRENT_SPEC.md`をGrep `Key Phrase`・`keywords_canonicalized`・`Phrase List`で、Key Phrase件数(5件)・選定基準(A2向け)・canonical化ルール・Key Phrase音声/Ledger/Phrase Listの正式仕様の該当行のみ読む。
8. 特定したdriver/script(例: `er0XX_*key_phrase*.py`、Assembly `er003_v1_n3_01_assemble.py`、player生成`build_web_player_common.py`)の必要範囲(Grep→範囲Read)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `keywords_canonicalized` in `*.py`(repo root)→ Key Phrase生成・canonical化・Ledger書き込みを行うモジュールを特定。
- Grep `key_phrase|keyphrase` in `er003_v1_n3_01_assemble.py`・`build_web_player_common.py` → Assembly時のKey Phrase segment挿入位置とplayerのKey Phrase表(英語|日本語)生成箇所を特定。
- Grep `phrase_list_used|ledger_phrases` in `er006_secondary_asr_01.py` → Key Phrase音声のASR評価(Phrase List)の呼び方を確認。
- 更新位置: (a)新canonical subdirectory(例: `er012_output/editorial_b_family_voices_a2_production_wiring_01/kp_fix_01/`、`er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/kp_fix_01/`。先例`kp5_regen_and_completion_01`の命名慣行に合わせてよい)に article.md/parts.json(本文同一)・新`key_phrases/keywords_canonicalized.json`・新Key Phrase音声・再Assembly episode.mp3・player.html(AI Hiring A2は現行canonicalが`user_test_simple.html`のsimpleRender経路だが、新artifactは他記事と同じ標準`player.html`で生成してよい。ただし本文・Comment内容は同一)。(b)`user_test/translations/index.json`の該当2行の`src`/`key_phrase_asset_path`/`player_sha256`を新artifactへ更新(旧行は削除、Trial/旧参照を残さない)。(c)`user_test/translations/free_address/A2/kp_mapping.json`と`user_test/translations/ai_hiring/A2/kp_mapping.json`を新Key Phraseで再作成(Phase Aと同じschema・同じ判定ルール: exactまたはKey Phrase資産の`source_span`一致による一意特定、UNRESOLVEDは0件が目標)。(d)`user_test/translations/<id>/A2/source_sections.json`は本文同一のため変更不要(変更が必要になったらSTOP条件(5))。

## 実行内容(この順で)

D-1. lock取得→対象2 levelの現状inventory(本文/旧Key Phrase/音声segment構成/生成pipeline)。旧Key Phraseと本文の不一致の原因(本文が後から平易化されたのか、Key PhraseがB1版から流用されたのか等)をartifactの生成日時・audit・DECISION_LOGから特定し、事実として記録。
D-2. 既存Key Phrase生成pipelineを現行本文(article.md/parts.json)に対して実行し、A2向けKey Phrase(既存仕様の件数・基準)を再生成。生成された各Key Phraseについて、本文中の対応箇所(`source_span`/`source_sentence`)が現行本文に実在することを機械確認(不在なら採用しない)。日本語意味(phrase_ja)を生成・確認。
D-3. Pronunciation Ledger更新(既存モジュールの正式手順)。Key Phrase音声を対象Phraseのみ生成(TTS)し、既存のASR評価(Primary+Secondary+Phrase List)を通す。Primary不一致のみではHuman Review要求しない。
D-4. 本文segment(旧artifactの本文音声)を**そのまま流用**してKey Phrase segmentだけ差し替えた再Assemblyでepisode.mp3を生成。本文segmentのsha256が旧と一致することを記録。標準playerを生成(Key Phrase表は英語|日本語2列、表示ラベル無し)。
D-5. `index.json`該当2行・`kp_mapping.json`2件を更新。ローカルhttpサーバ+`docs/pm/tools/user_test_readability_check.py`で新src(2 level)をPC/mobileで確認: 水色ハイライト数=Key Phrase件数(全件mapped)、Key Phrase一覧2列ラベル無し、Standard表記、横スクロールなし、Play/Seek、JS errorなし(translation_ja.jsonはPhase B完了前のため未配置でよく、日本語訳セクションはPhase Cで確認)。screenshotを`docs/pm/closeout_136_e2e/script_readability_prod_01/phase_d/`へ保存。
D-6. 費用集計(TTS/ASR/LLM、実測)。lock削除。commit/push。
D-7. 再発防止案(報告のみ、採用しない): 原因、量産時に「本文変更後はKey Phrase source整合確認を必須化」すべきか、実装案(例: Assembly/Gateで`keywords_canonicalized.json`の`source_span`が`parts.json`本文に実在することをチェックしFAILで止める)、コスト影響。

## 実行コマンド全文

- 委任文検証: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-SCRIPT-READABILITY-PROD-01_phaseD.md --json-out docs\pm\delegation_log\USER-TEST-SCRIPT-READABILITY-PROD-01_phaseD.md_check.json`
- lock取得: `.venv\Scripts\python.exe -c "import pathlib,datetime; p=pathlib.Path('docs/pm/locks/audio_stage.lock'); p.parent.mkdir(parents=True,exist_ok=True); f=open(p,'x',encoding='utf-8'); f.write('USER-TEST-SCRIPT-READABILITY-PROD-01 Phase D '+datetime.datetime.now().isoformat()); f.close(); print('locked')"`(FileExistsErrorなら内容を表示してSTOP)。終了時: `Remove-Item docs\pm\locks\audio_stage.lock`。
- Key Phrase生成・Ledger・TTS・ASR・Assembly・player生成のコマンドは、D-1で特定したdriver/scriptの実引数(絶対パス・レベルA2・対象subdirectory・件数)を含めた全文をRESULT_PACKETに記録して実行する(コスト記録`er005_cost_logger.install()`が有効な経路で実行)。
- 本文segment無変更証明: `.venv\Scripts\python.exe docs\pm\tools\sha256_snapshot.py`(Phase A作成)を旧canonical directoryと新subdirectoryの本文segment音声に対して実行し、対応segmentのsha256一致表を`docs/pm/closeout_136_e2e/script_readability_prod_01/phase_d/body_segments_sha256.json`へ出力(スクリプトの引数仕様がディレクトリ指定に対応していない場合は`--extra`で個別指定、または同ツールへ`--dir`オプションを追加してよい)。
- runtime確認: `Start-Process -NoNewWindow .venv\Scripts\python.exe -ArgumentList "-m","http.server","8765"` → `.venv\Scripts\python.exe docs\pm\tools\user_test_readability_check.py --base http://localhost:8765 --tsv docs\user_test\ユーザーテスト記事一覧_2026-0918_選定10.tsv --translations user_test\translations --out docs\pm\closeout_136_e2e\script_readability_prod_01\phase_d\e2e_result.json --screenshots docs\pm\closeout_136_e2e\script_readability_prod_01\phase_d`(TSVは旧srcのままなので、対象2 levelは新srcで個別指定できるオプション[例`--only free_address:A2,ai_hiring:A2 --src-override ...`]を追加するか、`index.json`のsrcを正として実行する。追加オプションの仕様はRESULT_PACKETに記す)。
- 回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er0*_test_*.py"`(既知の3件失敗[er003_test_bad、er003_test_p2j_investigate×2]以外の新規失敗が無いこと)。

## SSOT追記文

Phase DではSSOT本体(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`ARTIFACT_REGISTRY.md`)へ追記しない(Phase Cでまとめて反映)。ただしPhase Cが転記できるよう、`docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01.md`の`## Phase D`節に「DECISION_LOG追記用の事実(旧→新Key Phrase一覧、原因、費用、新canonical path)」と「ARTIFACT_REGISTRY追記用行(新artifact、旧artifactはSUPERSEDED)」をそのまま使える形で書く。

## Git(明示add対象・コミットメッセージ・trailer)

runtime確認PASS後に1 commit(push前`git fetch origin`、push後`git fetch origin`でmain=origin/main確認):
- 明示add: 新subdirectory配下の article.md/parts.json/key_phrases/**/*.json/audit/**/*.json/player.html/web/episode.mp3(mp3のみ、wav不可)、`user_test/translations/index.json`、`user_test/translations/free_address/A2/kp_mapping.json`、`user_test/translations/ai_hiring/A2/kp_mapping.json`、`docs/pm/closeout_136_e2e/script_readability_prod_01/phase_d/*`、`docs/pm/tools/sha256_snapshot.py`・`docs/pm/tools/user_test_readability_check.py`(変更した場合)、`docs/pm/delegation_log/USER-TEST-SCRIPT-READABILITY-PROD-01_phaseD.md`(+`_check.json`)、`docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01.md`、`docs/pm/ACTIVE_TASK.md`。共有状態ファイル(`er006_output/pronunciation_ledger_01/ledger.json`、`er006_output/master_audio_store_01/manifest.json`等)は既存運用でcommit対象なら明示addする(過去のcommit履歴を`git log --oneline -3 -- er006_output/pronunciation_ledger_01/ledger.json`で確認して従う)。
- Phase B1/B2の`user_test/translations_wip/`と`*_phaseB{1,2}.md`は**含めない**(`git status --porcelain`で混入なしを確認)。
- コミットメッセージ: `USER-TEST-SCRIPT-READABILITY-PROD-01 Phase D: Free-Address A2/AI Hiring A2のKey Phraseを現行本文から再生成(asset+訳+Ledger+KP音声のみ再TTS+再Assembly+player)、kp_mapping更新(Landing/TSV/SSOT未更新)`
- trailer: `Task-ID: USER-TEST-SCRIPT-READABILITY-PROD-01`

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_SCRIPT_READABILITY_PROD_01.md`に`## Phase D`節を追記(Phase A節は残す): Status(PHASE_D_DONE/USER_DECISION_REQUIRED/STOP理由)/不整合の原因(事実、artifact日時・DECISION_LOG根拠付き)/使用した生成pipeline・driverと実行コマンド全文/旧→新Key Phrase一覧(2 level、各phrase/phrase_ja/source_span/本文実在確認)/Key Phrase音声更新内容(件数、TTS voice、ASR Primary/Secondary/Phrase List結果、Human Review要否)/Pronunciation Ledger更新内容/本文segment無変更証拠(sha256一致表path)・本文article.md/parts.json本文同一の証拠/新canonical path(2 level)と旧artifactのsupersession記録、index.json更新行/kp_mapping.json再作成結果(2 level: total/mapped/exact/non_exact/unresolved、非exactのrationale)/runtime確認結果(PC/mobile、項目別)+screenshot path/費用実測(TTS/ASR/LLM内訳、合計、上限¥150に対する消化)/回帰テスト結果/lock取得・解放の記録/Git commit SHA、main=origin/main確認、混入なし確認/再発防止案(原因/提案/実装案/コスト影響。採用はユーザー判断)/一覧外Read(あれば理由1行)、check_delegation_prompt結果/Phase Cへの引き継ぎ(新src 2件のURLエンコード済み値、Landing/TSVで置換すべき旧src→新src対応)。
