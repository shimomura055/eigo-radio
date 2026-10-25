FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_04: 作業ブランチのorigin/main整合、Chunk配線のFable受入結果(PRODUCTION_WIRED)のSSOT反映、複製run用pages_dir分離+Z候補ページpage_verify、候補ページPages 200確認。API支出0(TTS/LLM呼出禁止)。Production code変更はer026 runnerのpages_dir分離(CLI引数)のみ。

## 前提(Fable確認済みの事実)
- 作業ブランチ `work/post-merge-01`(HEAD `1e7e5b436`)はorigin/main(先頭 `aa559be31`、その下 `eb10aa06c`/`753a3eb76`)と分岐(merge-base `ba6f27229`)。`1e7e5b436`と`eb10aa06c`はChunk配線Step C/Dの同内容(別commit)。origin/main側にはPart 1 T1のSSOT(`753a3eb76`、`aa559be31`)がある。
- 作業ツリーには他agentの未commit差分が多数(約1,500 file、大半は`er0XX_output/`)。**並行agent(FAMILY-Y-VOICES-DESIGN-01 委任_28)が稼働中**で、Y関連ファイルを編集中の可能性がある。
- 以前 `git merge origin/main` が未追跡ファイル `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/run_t1_check_01.py` の衝突で開始前に中断した。
- Fable受入判定(2026-10-25): Chunk配線 **X・Zとも PRODUCTION_WIRED**(要件1〜9適合、根拠=`docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/RUNTIME_EVIDENCE_01.md`、`docs/pm/RESULT_PACKET_FXZC2.md`)。注記: Z候補ページはpage_verify未実施→本委任で実施(API 0)。
- 『告げ口心臓』公開ページ`user_test/family_z_tell_tale_heart_01/`(run_sf_prod_02由来・非分割)は**変更しない**。分割版候補=`user_test/family_z_tell_tale_heart_chunk_01/`(run_chunk_01由来)。

## Git禁止事項
`git add -A/-u/-f/-N`、amend、rebase、force push、stash、clean、`reset --hard`、`checkout -f`、`git checkout -- <file>`禁止。HEAD/origin版へ戻す必要があるときは必ず先に scratchpad(`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\`)へバックアップしてから `git show <rev>:<file> > <file>` 方式。他agentの未commit差分を失わせない。

## Step 1: 整合前点検(読み取り)
1. `git fetch origin`、`git rev-list --left-right --count HEAD...origin/main`。
2. `git diff --name-only ba6f27229 origin/main` (incoming変更ファイル一覧=I) と `git diff --name-only HEAD`(作業ツリー未commit変更=W) と `git ls-files --others --exclude-standard`(未追跡=U) を取り、I∩W と I∩U を列挙。
3. I∩W の各ファイルについて: 作業ツリー版とorigin/main版を比較し、「作業ツリー版の変更内容がorigin/mainに既に含まれているか(=作業ツリー版をorigin/main版へ置き換えても失われる内容がないか)」を判定(`git diff origin/main -- <file>`で、作業ツリー側にしかない行を確認)。SSOT 4file(`OPEN_ITEMS.md`/`CURRENT_SPEC.md`/`DECISION_LOG.md`/`docs/pm/USER_DECISION_REGISTER_01.md`)は特に丁寧に: 作業ツリー側にしかない行があれば、その内容(どの管理ID・どの委任の追記か)を報告に書く。
4. I∩U の各ファイル: 作業ツリー版とorigin/main版を`cmp`/`git diff --no-index`で比較。

## Step 2: 整合(条件付き)
- I∩W・I∩U のすべてで「作業ツリー側にしかない内容が無い」場合のみ: 該当ファイルをscratchpadへバックアップ→`git show origin/main:<file> > <file>`(未追跡は同じ内容なら削除してmergeに任せる)→`git merge --no-edit origin/main`(普通のmerge、rebase禁止)。
- 作業ツリー側にしかない内容が1つでもあれば **mergeしない**で、その一覧(file・内容・推定の担い手)を報告してSTOP(以降のStep 3〜5は、作業ツリーを触らない方法=origin/mainの一時worktree方式で実施する。委任_17がこの方式を使った: `git worktree add <scratchpad>/wt_main origin/main --detach` → 編集 → commit → `git push origin HEAD:main` → `git worktree remove`)。
- mergeで競合(conflict)が出たら解決せず `git merge --abort`(開始前状態へ復帰)し、競合ファイル一覧を報告してSTOP(ユーザー確認事項)。
- merge成功時: `git log --oneline -3`、`git status --short | wc -l`、`git diff HEAD --stat -- OPEN_ITEMS.md CURRENT_SPEC.md DECISION_LOG.md docs/pm/USER_DECISION_REGISTER_01.md`。

## Step 3: Chunk配線 PRODUCTION_WIRED のSSOT反映(直前再Read・最小Edit・バックアップ・`git diff --stat`)
1. `OPEN_ITEMS.md` OPEN-506(X)/OPEN-510(Z): Status→`PRODUCTION_WIRED(Fable受入 2026-10-25 委任_04、X=段落分割+0.2秒、Z=B_r1)`。残件(11-8分類): (a)候補ページ2件はユーザー参考試聴用(採用判断は完了済み、Gateではない)=分類B / (b)『告げ口心臓』公開ページ`family_z_tell_tale_heart_01`はrun_sf_prod_02由来で非分割(生成10:47〜10:54 JST、Z配線13:21より前)。分割版への公開差替え・Part 1 block追加は**Fable判断: OPEN-503のユーザー試聴判断後にまとめて1回**=分類B / (c)clean worktree回帰の既存失敗126件(未追跡assets起因、配線前と同一ID)=分類C・既知環境差 / (d)page_verifyの結果(Step 4)。
2. `docs/pm/USER_DECISION_REGISTER_01.md` #191: 配線完了・PRODUCTION_WIRED(X/Z)を追記し未決解除。
3. `CURRENT_SPEC.md` Chunk節: Status行を`PRODUCTION_WIRED(X/Z)`に更新(重複節を作らない)。`DECISION_LOG.md` 1エントリ(Fable受入、根拠、公開差替えは保留の理由)。
4. `docs/pm/ACTIVE_TASK.md` 更新(gitignore)。

## Step 4: 複製run用pages_dir分離 + Z候補ページpage_verify(API 0)
1. `er026_family_z_fiction_production_runner_01.py` に `--pages-dir <path>` CLI引数(未指定時は従来どおり既定の公開dir、既定動作バイト不変)を追加し、`E2EContext.pages_dir` を上書きできるようにする。既存test(`er026_*test*`、`er109_xz_isolation_01_test_01.py`)に追随が必要なら最小で。新規testを1〜2件(未指定=従来値、指定=反映)。
2. `run_chunk_01` に対し `--pages-dir user_test/family_z_tell_tale_heart_chunk_01 --stages pages,page_verify`(`--mode real`不要なら不要。TTS/LLMが走らない段のみ。起動前に `tools/stop_scope_check_01.py --managed-id FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01` rc0確認。`.venv\Scripts\python.exe`使用)。pagesの再生成で候補ページ内容が変わる場合は差分を`git diff --stat`で確認し、Advanced/Standard mp3が差し替わらない(sha同一)ことを確認。page_verify(Playwright)の結果を`docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/RUNTIME_EVIDENCE_01.md` §2末尾へ追記。**公開ページ`family_z_tell_tale_heart_01`に書かないことを実行前後の`git status -- user_test/family_z_tell_tale_heart_01`で確認**。
3. page_verifyが仕様上run dir内のpages(公開dir)前提で動かない等の理由で実行できない場合は、無理に改造せず理由を報告(未実施のまま)。

## Step 5: 候補ページ Pages 200確認
`https://shimomura055.github.io/eigo-radio/user_test/uk_train_speaker_playback_chunk_01/index.html` と `https://shimomura055.github.io/eigo-radio/user_test/family_z_tell_tale_heart_chunk_01/index.html` にHTTP HEAD/GET(PowerShell `Invoke-WebRequest -Method Head`)。Pages反映待ちなら最大5回・各120秒待って再試行。

## Step 6: 回帰・委任文・Git
- `.venv\Scripts\python.exe -m pytest er117_chunk_tts_production_01_test_01.py er117_x_chunk_wiring_test_01.py er117_z_chunk_wiring_test_01.py er109_xz_isolation_01_test_01.py <er026関連test> -q`。er109 `test_m3_scope_entry_call_sites` が作業ツリーでFAILする場合(委任_17報告: validation_inheritanceのX呼出数4 vs期待2)、原因ファイル(未commit差分のどれか)を`git diff HEAD --stat`と該当grepで特定し報告(修正は、原因が自分のcommit済みコードなら行う。他agentの未commit差分なら触らず報告)。
- 委任文逐語: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01_DELEGATION_04.md`(Nは548前後±6、冒頭「FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_04」で照合。`--index -1`不可)。委任_03(読み取り専用の状況確認)の逐語も同じ方法で`..._DELEGATION_03.md`へ保存(冒頭「FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_03」、index 547前後)。
- commit: `git status`→対象pathのみadd→`git diff --cached --name-status`→`git commit --only -- <paths>`(他agent差分混在時は一時index方式)→`git push origin HEAD:main`(merge未実施でpushがnon-fast-forwardになる場合はpushせず報告)。secret grep 0件。wav/raw_usage_log/STOP/lock/telemetry不追跡。

## 報告(`docs/pm/RESULT_PACKET_FXZC4.md`+返答)
Step 1の I∩W/I∩U一覧と判定、Step 2の結果(merge実施/不実施/abortと理由)、Step 3〜5の結果、er109の原因、変更ファイル・commit hash・push結果・raw URL、RESULT_PACKET 4行(既存仕様整合/未承認機能の既定値/失敗終了時の成果物/撤去・残置)。判断を要する点は推測で進めず報告で止める。