FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_05: 『告げ口心臓』Chunk分割版(run_chunk_01)を最終試聴ページ `user_test/family_z_tell_tale_heart_01/` へ公開差替え(ユーザー指示2026-10-25、原文は本委任で`docs/pm/delegation_log/2026-10-25_FZ-TELL-TALE-HEART-CHUNK-FINAL-01_USER.md`として保存する=下記Step 0)。あわせて作業ブランチのorigin/main整合(競合の安全解消はユーザー指示で許可済み)、SSOT更新、er109 FAILの解消。**TTS/LLM呼出は禁止(API 0)**。既存のrun_chunk_01音声を再利用し、本文・音声の再生成はしない。

## ユーザー指示の要点(逐語は下記Step 0で保存する原文を参照)
- 最終試聴対象をB_r1適用版へ変更。非分割版run_sf_prod_02は最終試聴対象としない。案A(一人称語り口)・B_r1(約70語目安分割+0.2秒)・既存Std/Adv品質仕様を維持。
- 既存run_chunk_01の音声が正式仕様・品質条件を満たすなら再利用。不要なTTS・本文再生成禁止。
- 公開URL https://shimomura055.github.io/eigo-radio/user_test/family_z_tell_tale_heart_01/index.html をChunk版へ更新し、次の8点を確認: 1.Std/Advとも正式完成音声 2.Advの対象箇所にB_r1適用 3.Stdは承認済み仕様どおり 4.案Aの一人称本文・語り口保持 5.分割境界の0.2秒ポーズ 6.全スクリプト・音声・パート再生が一致 7.古い非分割音声が混在しない 8.公開URLで全音声の再生・シーク・ページ検証PASS。
- 公開差替え時は既存成果物を退避し復旧可能に。
- Closeout: OPEN-510等Status、CURRENT_SPEC/DECISION_LOG整合、Git分岐・競合解消(承認済み仕様を優先し安全に解消、他案件の成果を破棄しない)、回帰、runtime evidence保持。
- 『告げ口心臓』は**USER_LISTENING_PENDING**で提出(試聴PASSを先取りしない)。追加の採用判断は不要。

## 現状(Fable確認済み)
- origin/main先頭 `e5e0bd1e2`(委任_04: OPEN-506/510=PRODUCTION_WIRED、er026に`--pages-dir`追加、Z候補ページpage_verify PASS)。作業ブランチ`work/post-merge-01` HEAD=`ef45f6b88`、origin/mainと分岐(ローカル側commit `1e7e5b436`/`ef45f6b88`はorigin側 `eb10aa06c`/`928213098` と同内容・別hash)。直前のmergeは`DECISION_LOG.md`でCONFLICT→abort済み。
- 作業ツリーにはorigin/main `e5e0bd1e2`と同内容の未commit差分(er026 runner・`er026_family_z_e2e_integration_test_01.py`・run_chunk_01の`e2e_stage_log`/`run_launch_log`/`page_verify_local.json`)と、他agentの未commit差分多数(`er0XX_output/`中心)、未追跡26件(origin/mainと同一or改行差のみ)がある。
- `run_chunk_01`(`er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_chunk_01`): Adv 22/Std 19 entry全OK、chunk `full_story_part2_c1`=[58,62]/`full_story_part3_c1`=[65,61]、親wav整数sample一致、共有Gate PASS、HR 0、kp stage(Part 1解説+T1訳)実行済み。候補ページ`user_test/family_z_tell_tale_heart_chunk_01/`はpage_verify PASS・Pages 200。
- 公開ページ`user_test/family_z_tell_tale_heart_01/`は run_sf_prod_02由来(非分割)。
- er109 `test_m3_scope_entry_call_sites_are_fixed_and_literal` FAIL原因=未追跡 `er019_output/_fxnr7_shadow_head/er019_family_x_audio_production_runner_01.py`(他agentが11:57に作ったrunner複製、当該agentは完了済み)がbasename二重計上。

## Git禁止事項
`git add -A/-u/-f/-N`、amend、rebase、force push、stash、clean、`reset --hard`、`checkout -f`、`git checkout -- <file>`禁止。戻す必要があるときはscratchpad(`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\d5\`)へバックアップ後 `git show <rev>:<file> > <file>`。他agentの成果を破棄しない。

## Step 0: ユーザー指示原文の保存
ユーザー指示原文(逐語)は本セッションのjsonl `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl` の role=user メッセージで、冒頭が「# Claude Codeへの指示｜Family Z『告げ口心臓』Chunk分割版・最終音声完成」。`py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <上記> --role user --index N --out docs/pm/delegation_log/2026-10-25_FZ-TELL-TALE-HEART-CHUNK-FINAL-01_USER.md`(toolのuser抽出オプションが無ければ`py`で直接jsonlを走査し、該当user messageのtext fieldを無変更で書き出す。見つからなければ本委任文の「ユーザー指示の要点」を転記し**要点であり逐語でない**と注記)。

## Step 1: Git整合(作業ブランチ→origin/main)
1. `git fetch origin`。`git status --short -- er026_family_z_fiction_production_runner_01.py er026_family_z_e2e_integration_test_01.py er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_chunk_01/` を確認し、origin/main版と作業ツリー版が同一(`git diff origin/main -- <path>`が空)なら、それら「origin/mainと同内容の未commit差分」を `git commit --only -- <paths>` でローカルに先にcommit(メッセージ: "sync: 委任_04と同内容(origin/main e5e0bd1e2)")。同一でなければ差分を報告してこのファイルは触らない。
2. I∩W(origin/mainからの変更ファイル ∩ 作業ツリー未commit差分)を再点検し、作業ツリー側にしかない内容が無いことを確認(あれば内容を報告し、そのファイルはmerge前にcommitせず、mergeが拒否される場合は報告してSTOP)。
3. I∩U(未追跡で衝突するファイル)は scratchpad/d5/bak_iu へバックアップ後に削除(同一or改行差のみの場合のみ)。
4. `git merge --no-edit origin/main`。**競合は解消してよい(ユーザー許可済み)**。方針: 競合ファイルごとに、両側の追記エントリを**両方残す**(重複する同一内容エントリは1つに統合、順序はorigin/main側を基準)。承認済み仕様の記載が食い違う場合はorigin/main側(Fable受入反映済み)を優先し、ローカル側の固有内容は失わない。解消後に `git diff origin/main -- <file>` で「origin/mainに対する差分=ローカル固有の追記のみ」であることを確認し、競合ファイルと解消内容を報告に列挙。`git commit`(merge commit、amendなし)。
5. バックアップした未追跡ファイルは、merge後にorigin/mainから復元されたものはそのまま、復元されなかったものは戻す。
6. `git log --oneline -5`、`git rev-list --left-right --count HEAD...origin/main`(右=0であること)。

## Step 2: 公開差替え(API 0)
1. 退避: `user_test/family_z_tell_tale_heart_01/` 全体を `scratchpad/d5/backup_tell_tale_heart_01_<timestamp>/` へコピー(gitにも履歴あり、復旧コマンド `git show HEAD~1:<path>`を報告に記載)。
2. STOP確認: `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01` rc0。
3. 公開dirの旧ファイル残置防止: 差替え前に公開dir内のファイル一覧(名前+sha256)を記録。候補ページ `user_test/family_z_tell_tale_heart_chunk_01/` のファイル一覧(名前+sha256)と比較し、候補側に存在しない旧ファイル(非分割音声等)は差替え後に残らないようにする(方法: pages stageが上書きしないファイルを特定し、退避済みであることを確認してから削除)。
4. 実行: `.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --story the_tell_tale_heart --run run_chunk_01 --mode real --approved-budget-jpy 1 --stages pages,page_verify`(`--pages-dir`未指定=既定の公開dir。cost_log追記0・spent不変であることを確認。有料stageを含めない)。rc・stdout要点を記録。
5. 8点確認(事実のみ、各項目に根拠パスを付ける):
   1. Std/Advの音声がrun_chunk_01の`assembly`/gate OK成果物由来(mp3 sha256 ↔ run_chunk_01の組立成果物からの変換物、または候補ページchunk_01のmp3 sha256と一致)。
   2. Advの`full_story_part2_c1`/`full_story_part3_c1`がchunk `_k1/_k2`(58/62語・65/61語)から連結されたこと(`b1b/audit/chunk_plan_b1b.json`・`timeline.json`)。
   3. Stdはchunk化対象外で19 entry OK(a2 gate結果)。
   4. 案A: 公開advanced/standardページ本文が`run_chunk_01/writer/{r2,std}.md`と段落単位で一致し、一人称(I/my/me)・聞き手you・housemate 0件(`COMPARISON_03.md`の確認方法を踏襲。日本語noteセルの除外バグに注意)。
   5. 0.2秒ポーズ: `timeline.json`の`chunk_tts`のgap位置(188.516〜188.716/249.376〜249.576秒付近)と、公開mp3のAdvanced通し長(約280.6秒)が一致。
   6. 全スクリプト・音声・パート再生の一致: page_verify結果(plays_failed 0、console_errors 0、http_ge400 0、標準適合PASS)。
   7. 旧非分割音声の混在なし: 差替え後の公開dir内ファイル一覧がすべて候補ページchunk_01と一致(sha256)、旧sf_prod_02由来ファイル0件。
   8. 公開URL: commit/push後、`https://shimomura055.github.io/eigo-radio/user_test/family_z_tell_tale_heart_01/index.html`・`standard.html`・`advanced.html`と全mp3(ページ内のaudio src全件)にHTTP 200(Pages反映待ちは最大6回・各120秒)。Range(シーク)は公開URLに `Range: bytes=0-1` HEADER付きGETで206が返るかを1〜2ファイルで確認(GitHub PagesはRange対応)。
6. Part 1(Vocabulary & Expressions)の5項blockがAdvancedページに1つ入り、Standardに無いことを確認(PRODUCTION_WIRED済み仕様)。
7. 結果を `docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/PUBLIC_REPLACEMENT_01.md` に記録(8点表+根拠パス+退避場所+復旧手順+差替え前後ファイル一覧の要約)。

## Step 3: er109 FAIL解消
`_fxnr7_shadow_head` への参照をdocs/er0*.pyでGrep。参照が証跡の記述のみ(コードからの参照なし)なら、`er019_output/_fxnr7_shadow_head/` 全体を `scratchpad/d5/bak_fxnr7_shadow_head/` へ移動(削除ではなく退避)し、`.venv\Scripts\python.exe -m pytest er109_xz_isolation_01_test_01.py -q` PASSを確認。コードからの参照があれば触らず報告。

## Step 4: SSOT更新(直前再Read・最小Edit・バックアップ・`git diff --stat`)
- `OPEN_ITEMS.md` OPEN-503(告げ口心臓): Status→`COMPLETE_USER_LISTENING_PENDING(Chunk分割版 run_chunk_01、公開差替え2026-10-25 委任_05)`、非分割版run_sf_prod_02は最終試聴対象外、退避場所・復旧手順を1行。OPEN-510残件(b)「公開差替え=OPEN-503判断後」を**完了(ユーザー指示により前倒し実施)**へ。OPEN-512残件(a)「既公開Z/XページへのPart 1反映」のうち告げ口心臓=完了(run_chunk_01のkp stage由来)、X既公開ページは未反映のまま(分類B)。
- `DECISION_LOG.md` 1エントリ(ユーザー決定: 最終試聴対象をChunk版へ、公開差替え実施、USER_LISTENING_PENDING)。
- `CURRENT_SPEC.md`は変更不要(仕様変更なし)。変更が必要と判断した場合は理由を報告し編集しない。
- `docs/pm/ACTIVE_TASK.md` 更新(gitignore)。

## Step 5: 回帰・委任文・Git
- `.venv\Scripts\python.exe -m pytest er117_chunk_tts_production_01_test_01.py er117_x_chunk_wiring_test_01.py er117_z_chunk_wiring_test_01.py er109_xz_isolation_01_test_01.py er026_family_z_e2e_integration_test_01.py -q`。
- 委任文逐語: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <上記jsonl> --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01_DELEGATION_05.md`(N=551前後±6、冒頭「FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_05」で照合)。
- commit: 対象pathのみadd(公開dirは `user_test/family_z_tell_tale_heart_01/` 配下の変更・削除を含める。削除は`git rm`で個別に)→`git diff --cached --name-status`→commit→`git push origin HEAD:main`(mergeが済んでいればfast-forward。non-fast-forwardなら押さずに報告)。secret grep 0件。wav/raw_usage_log/STOP/lock/telemetry不追跡。

## 報告(`docs/pm/RESULT_PACKET_FXZC5.md`+返答)
1. 公開URL(HTTP 200確認結果) 2. Std/Adv完成状況 3. B_r1適用箇所と実測(語数・gap位置・長さ) 4. 音声品質Gate・page_verify結果 5. 再利用/再生成内訳と追加実費(0円のはず) 6. Git整合の結果(競合ファイルと解消内容、HEADとorigin/mainの関係) 7. er109の結果 8. 変更ファイル・commit hash・raw URL 9. RESULT_PACKET 4行(既存仕様整合/未承認機能の既定値/失敗終了時の成果物/撤去・残置)。8点確認のいずれかが不成立なら、差替えを**押さずに**(push前に)事実を報告してSTOP(退避から復旧可能な状態を保つ)。