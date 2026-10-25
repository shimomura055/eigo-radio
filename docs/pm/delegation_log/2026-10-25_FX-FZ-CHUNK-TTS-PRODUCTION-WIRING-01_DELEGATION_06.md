FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_06: 前委任_05(途中で強制停止)の残りを完了する。『告げ口心臓』Chunk分割版(run_chunk_01)の最終試聴ページ `user_test/family_z_tell_tale_heart_01/` 公開差替えのcloseout。**TTS/LLM呼出禁止(API 0)**。Production code変更禁止。

## 委任_05で完了済み(Fableが読み取り確認)
- ユーザー指示原文保存: `docs/pm/delegation_log/2026-10-25_FZ-TELL-TALE-HEART-CHUNK-FINAL-01_USER.md`(存在確認のみ。中身が逐語か確認し、要点転記なら注記があるか確認)。
- Git: 作業ブランチ`work/post-merge-01`にorigin/main(`e5e0bd1e2`)をmerge済み(HEAD `658256c6b`、ORIG_HEAD `7e62af937`=merge前のsync commit)。**push前**。merge進行中状態なし。
- 公開dir退避: scratchpad `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\d5\backup_tell_tale_heart_01_20261025_150429\`(58ファイル)。差替え前一覧=`scratchpad\d5\pub_before.txt`、候補一覧=`scratchpad\d5\cand.txt`。
- `--stages pages,page_verify`(既定pages_dir=公開dir)を15:04〜15:06に実行済み(`scratchpad\d5\pages_run.log`: 全ファイル200、spent 16.6657不変)。公開dirは58ファイルで候補ページ`user_test/family_z_tell_tale_heart_chunk_01/`と同じ構成。
- 未完了: 8点確認の記録、SSOT更新、er109複製退避、commit/push、公開URL確認、報告。

## ユーザー指示の要点(原文は上記USERファイル)
最終試聴対象をB_r1適用版へ。公開URL https://shimomura055.github.io/eigo-radio/user_test/family_z_tell_tale_heart_01/index.html をChunk版へ更新し8点確認: 1.Std/Advとも正式完成音声 2.Advの対象箇所にB_r1適用 3.Stdは承認済み仕様どおり 4.案Aの一人称本文・語り口保持 5.分割境界の0.2秒ポーズ 6.全スクリプト・音声・パート再生が一致 7.古い非分割音声が混在しない 8.公開URLで全音声の再生・シーク・ページ検証PASS。退避し復旧可能に。『告げ口心臓』は**USER_LISTENING_PENDING**で提出(試聴PASSを先取りしない)。

## Git禁止事項
`git add -A/-u/-f/-N`、amend、rebase、force push、stash、clean、`reset --hard`、`checkout -f`、`git checkout -- <file>`禁止。復旧が必要なら退避dirからコピー、または `git show <rev>:<file> > <file>`。他agentの未commit差分(多数、`er0XX_output/`中心)を巻き込まない。

## Step 1: Git状態確認
`git status | head -5`(merge中でないこと)、`git log --oneline -4`、`git rev-list --left-right --count HEAD...origin/main`(右=0のはず)、`git status --short -- user_test/family_z_tell_tale_heart_01 user_test/family_z_tell_tale_heart_chunk_01 er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_chunk_01`。merge commit `658256c6b`の`DECISION_LOG.md`/`OPEN_ITEMS.md`が origin/main に対して「ローカル固有の追記のみ差分」になっているか `git diff origin/main --stat -- DECISION_LOG.md OPEN_ITEMS.md CURRENT_SPEC.md docs/pm/USER_DECISION_REGISTER_01.md` で確認し、競合解消の内容(どのエントリを両方残したか)を報告に書く。

## Step 2: 8点確認(事実のみ・根拠パス付き)
1. 公開dirの全58ファイルのsha256を、候補ページ`family_z_tell_tale_heart_chunk_01`の同名ファイルと比較(mp3は一致のはず。html は study block/タイトル等が同一か差分を要約)。run_chunk_01の組立成果物(`b1b/assembly`、`a2/...`)由来であることを `page_verify_local.json`/provenance/`e2e_stage_log`で確認。
2. `run_chunk_01/b1b/audit/chunk_plan_b1b.json`・`timeline.json`で `full_story_part2_c1`=[58,62]/`full_story_part3_c1`=[65,61](`_k1/_k2`)を確認。
3. Std(a2)はchunk化なし・19 entry OK(a2 gate結果)。
4. 案A: 公開 advanced.html/standard.html の本文セルを `run_chunk_01/writer/{r2,std}.md` と段落単位で照合(全段落一致数)。一人称(I/my/me)を含む段落数、聞き手youの文、`housemate`/`narrator` 0件(日本語noteセルを除外して本文を落とす旧バグに注意、`docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/ACCEPTANCE_CHECK_01.md`の方法を踏襲)。
5. 0.2秒ポーズ: `timeline.json`の`chunk_tts` gap位置(約188.5/249.4秒)と公開 `audio_advanced/TellTaleHeart_b1b_full.mp3` の長さ(約280.6秒)を実測(ffprobeまたはpython)。可能なら該当位置±0.1秒の振幅が無音(max|x|≤0.001)であることをwavデコードで確認(無理なら理由)。
6. page_verify: `run_chunk_01/page_verify_local.json`(15:06更新)の plays_failed/console_errors/http_ge400/標準適合。
7. 差替え後の公開dirに `pub_before.txt` にあって `cand.txt` にないファイルが残っていないこと、旧run_sf_prod_02由来mp3(退避dir内)とsha一致するファイルが公開dirに**無い**こと(全58ファイルで旧sha≠新sha、ただしStandardは run_chunk_01 で再生成されているため全て変わるはず。変わっていないファイルがあれば列挙し理由を調べる)。
8. (push後) 公開URL index/standard/advanced と全mp3のHTTP 200(ページ内audio src全件)、Rangeリクエスト(`Range: bytes=0-1`)で206が返るか2ファイル確認。Pages反映待ちは最大6回・各120秒。
- 加えて: AdvancedページにPart 1(Vocabulary & Expressions)blockが1つ、Standardには無いこと。
- 結果を `docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/PUBLIC_REPLACEMENT_01.md` に記録(8点表+根拠+退避場所+復旧手順[退避dirからのコピー、または `git show <差替え前commit>:user_test/family_z_tell_tale_heart_01/<file>`]+変更ファイル要約)。
- 8点のいずれかが不成立なら **pushせず** 事実を報告してSTOP。

## Step 3: er109 FAIL解消
未追跡 `er019_output/_fxnr7_shadow_head/`(他agentが作ったrunner複製、当該agent完了済み)への参照を `docs/`・`er0*.py` でGrep。コードからの参照が無ければ `scratchpad\d5\bak_fxnr7_shadow_head\` へ移動(削除ではなく退避)し、`.venv\Scripts\python.exe -m pytest er109_xz_isolation_01_test_01.py -q` PASSを確認。コード参照があれば触らず報告。

## Step 4: SSOT(直前再Read・最小Edit・バックアップ・`git diff --stat`)
- `OPEN_ITEMS.md` OPEN-503: Status→`COMPLETE_USER_LISTENING_PENDING(Chunk分割版 run_chunk_01、公開差替え2026-10-25 委任_05/06)`、非分割版run_sf_prod_02は最終試聴対象外、退避場所・復旧手順を1行。OPEN-510残件(b)=完了(ユーザー指示で前倒し)。OPEN-512残件(a)の告げ口心臓分=完了(run_chunk_01 kp stage由来のPart 1込み)、X既公開ページは未反映(分類B)。
- `DECISION_LOG.md` 1エントリ(ユーザー決定: 最終試聴対象をChunk版へ、公開差替え、USER_LISTENING_PENDING)。CURRENT_SPECは変更不要。
- `docs/pm/ACTIVE_TASK.md` 更新(gitignore)。

## Step 5: 回帰・委任文・Git
- `.venv\Scripts\python.exe -m pytest er117_chunk_tts_production_01_test_01.py er117_x_chunk_wiring_test_01.py er117_z_chunk_wiring_test_01.py er109_xz_isolation_01_test_01.py er026_family_z_e2e_integration_test_01.py -q`。
- 委任文逐語: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01_DELEGATION_06.md`(N=560前後±8、冒頭「FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_06」で照合。`--index -1`不可)。委任_05の逐語(冒頭「FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_05」、index 552前後)も `..._DELEGATION_05.md` へ保存(未保存なら)。
- commit: 対象pathのみ(`user_test/family_z_tell_tale_heart_01/` 配下の変更、PUBLIC_REPLACEMENT_01.md、run_chunk_01の`page_verify_local.json`/stage log、SSOT 2 file、委任文)→`git diff --cached --name-status`→commit→`git push origin HEAD:main`。mergeが済んでいるのでfast-forwardのはず。non-fast-forward(他agentが先にpush)なら `git fetch` → `git merge --no-edit origin/main`(競合は両方残して解消、他案件の成果を破棄しない)→ push。secret grep 0件。wav/raw_usage_log/STOP/lock/telemetry不追跡。

## 報告(`docs/pm/RESULT_PACKET_FXZC6.md`+返答)
1. 公開URL(200/Range結果) 2. Std/Adv完成状況 3. B_r1適用箇所と実測(語数・gap位置・長さ) 4. Gate・page_verify 5. 再利用/再生成内訳と追加実費(0円) 6. Git(merge内容・競合解消・HEAD/origin関係・commit hash) 7. er109 8. raw URL 9. RESULT_PACKET 4行(既存仕様整合/未承認機能の既定値/失敗終了時の成果物/撤去・残置)。