FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_17: Part 1(T1込み)Fable受入のSSOT実体照合・是正・PRODUCTION_WIRED反映(API 0・無料処理のみ、Production code変更禁止)

## 背景
委任_16(報告=`docs/pm/RESULT_PACKET_FZST16.md`、証跡=`docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/{PART1_WIRING_EVIDENCE_02,PART1_T1_CHECK_01}.md`+`part1_wiring_evidence_02/`)は「Production commit `a9e87da40`、証跡/SSOT commit `753a3eb76`、CURRENT_SPEC/OPEN-512/DECISION_LOG/UDR #197/ADOPTION_NOTE_04 更新済み、回帰結果=`REGRESSION_02.md`」と報告した。
しかしFableが作業ツリーをGrepしたところ:
- `OPEN_ITEMS.md`・`CURRENT_SPEC.md`に `kp_part1_ja_b1b` / `PART1_T1_CHECK_01` / `KEY_PHRASE_SOURCE_SENTENCE_JA` が0件。OPEN-512行(1027行目付近)は委任_14時点の内容(「Z=WIRED_PENDING_FABLE(描画停止中)/X=WIRED_EXCEPT_USER_PAGE」)のまま。
- `docs/pm/USER_DECISION_REGISTER_01.md` #197(398行目)は委任_14追記まで。T1承認(USER_07)の反映なし。
- `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/REGRESSION_02.md` がrepo内に存在しない(Glob `**/REGRESSION_02.md` 0件)。
並行して他agent2つ(FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_02、FAMILY-Y-VOICES-DESIGN-01 委任_28)が稼働中でSSOTを編集し得る。

## タスク
### Step 1: Git実体の照合(読み取りのみ)
1. `git log --oneline -3 753a3eb76`、`git show --stat 753a3eb76`、`git branch -r --contains 753a3eb76` で、commitの存在・含まれるファイル・origin/mainに載っているかを確認。
2. `git show HEAD:OPEN_ITEMS.md | grep -c kp_part1_ja_b1b`(CURRENT_SPEC.md / DECISION_LOG.md / docs/pm/USER_DECISION_REGISTER_01.md / docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/ADOPTION_NOTE_04.md も同様)と、`git show origin/main:…` でも同じ確認。`git ls-tree -r HEAD --name-only | grep REGRESSION_02` も。
3. 作業ツリー側: `git status --short -- OPEN_ITEMS.md CURRENT_SPEC.md DECISION_LOG.md docs/pm/USER_DECISION_REGISTER_01.md` と `git diff --stat HEAD -- <同4file>`。
4. 結論を次のいずれかに分類して報告に書く: (A) commitに含まれるが作業ツリーが他agentにより巻き戻された / (B) commitにSSOT更新が含まれていない(委任_16の報告と実体が不一致) / (C) 別の原因。どのケースでも、**他agentの未commit差分を消さない**(`git checkout --`・`git stash`・`reset`禁止)。

### Step 2: 是正(ケース別)
- (A)の場合: 作業ツリーの該当ファイルに、HEADにある委任_16の内容が失われていれば、他agentの差分を保ったまま委任_16の変更箇所だけを再適用(直前再Read・最小Edit。`git show HEAD:<file>`との差分を見て、消えた部分だけ戻す)。
- (B)の場合: `RESULT_PACKET_FZST16.md`・`PART1_WIRING_EVIDENCE_02.md`・`PART1_T1_CHECK_01.md`を根拠に、本来の委任_16 SSOT更新(下記Step 3の内容に統合して1回で書く)。`REGRESSION_02.md`が存在しなければ新規作成: Part 1関連testを実際に再実行して記録する(`py -m pytest er003_kp_source_sentence_ja_01_test_01.py er003_kp_general_explanation_01_test_01.py er003_kp_general_explanation_01_runner_integration_test_01.py er109_xz_isolation_01_test_01.py -q` 相当。`py`を使い`python`は使わない)。全件回帰7,192/7,207は委任_16報告値として「本委任では未再実行」と明記(全件再実行はしない)。
- 委任_16報告との不一致が確認された場合は、事実として報告に明記する(推測で埋めない)。

### Step 3: Fable受入結果のSSOT反映(Fable判断済み、下記をそのまま反映)
Fable受入判定(2026-10-25): **Part 1(案α+T1訳工程)= Family Z・Family X とも `PRODUCTION_WIRED`**。根拠=受入条件1〜7をEVIDENCE_02/T1_CHECK_01/5項出力(`part1_wiring_evidence_02/{Z,X}_part1_vocabulary_expressions.md`)でFableが照合。T1訳の正確性=9文中 意味同一7・軽微1・中程度1(非再現)・重大0、Z/X実発火6文はすべて意味整合OK=ユーザー承認条件「引用英文のみ入力・自然な訳・正確性と意味整合を確認」の範囲内。
反映内容:
1. `OPEN_ITEMS.md` OPEN-512: Statusを `PRODUCTION_WIRED(Z/X、Part 1=案α+T1訳、Fable受入2026-10-25 委任_17)` に更新。残件を11-8分類付きで記載: (a)既公開Z/Xページ(告げ口心臓等)へのPart 1 block追加・再公開=**Fable判断: 保留**(ユーザー試聴中案件OPEN-503の判断後に、Chunk配線後の再公開とまとめて1回で実施。理由: 試聴中ページを変更しない)=分類B / (b)T1 Prompt改善(副詞句の係り先明示等)=分類C・未採用・必須ではない(Prompt変更=再検証要) / (c)複製runの`--stage pages`が公開pages_dirへ書く問題=修正へ進む候補・低優先・API 0 (`E2EContext.pages_dir`分離) / (d)`er053_c2` dangling 1件=FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01側のコード起因、同案件の受入で解消確認 / (e)Part 2〜4は別(Trial-07 VALIDATED(限定)・配線禁止)。インシデント2件(複製run `run_p1_evidence_02`にRESTART_STORMのSTOP残置[複製のみ]、複製run `_03`の`--stage pages`が公開`user_test/family_z_tell_tale_heart_01/index.html`を一時差替→`git checkout --`で復元・公開反映0・以後は`git show HEAD:<file> > <file>`方式を使う)も事実として1行記録。
2. `docs/pm/USER_DECISION_REGISTER_01.md` #197: 「判断済み・2026-10-25: T1専用翻訳工程をユーザー正式承認(原文=`docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_07.md`、入力=引用英文のみ・解説LLMと独立・5項構成維持・+約0.03円/セット[実測0.031〜0.039円])。Opus論点(a)gloss参照=不採用(ユーザー原文優先)、(b)品質根拠=直接採用+9文対照`PART1_T1_CHECK_01.md`。Part 1=Z/X PRODUCTION_WIRED(Fable受入、OPEN-512)」を追記し、未決扱いを解除。
3. `CURRENT_SPEC.md`: Part 1(学習解説 Vocabulary & Expressions)の正式仕様節に、T1訳工程(module `er003_kp_source_sentence_ja_01.py`、routing `KEY_PHRASE_SOURCE_SENTENCE_JA`=SUPPORT_MODEL、Prompt sha `98b1871c…7999`、入力=逐語照合済み引用英文のみ、1 call/set JSON、技術retry1回→fail-closed[Z `FAMILY_Z_KP_PART1_JA_NOT_OK`/X `KP_PART1_JA_FAILED` rc=3]、再生成キー=引用英文+Prompt sha+model、Z stage `kp_part1_ja_b1b`、X自動再生成、描画は`docs/pm/decisions/part1_translation_decision.json`(decision=T1)のみで有効、Advancedのみ、X公開ページ=`study_html_for_audio_dir`+`er019_nws2_final_page_01.py`1呼出)と Status=PRODUCTION_WIRED(Z/X)を記載。既に委任_14/16の記載があればそれを更新(重複節を作らない)。
4. `DECISION_LOG.md`: 1エントリ追加(Part 1 Z/X PRODUCTION_WIRED Fable受入・T1ユーザー承認USER_07・既公開ページ反映は保留の判断と理由)。
5. `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/ADOPTION_NOTE_04.md`(存在すれば)末尾にStatus行を追記。
6. `docs/pm/ACTIVE_TASK.md`: Part 1行をPRODUCTION_WIRED(Fable受入済み)へ更新。

### Step 4: 委任文逐語保存
`py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_DELEGATION_17.md`(Nは560前後から±6を試し、冒頭「FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_17」で照合。`--index -1`不可。見つからなければ本文を手転記し注記)。

### Step 5: Git
`git status`→対象pathのみ`git add`(`-A/-u/-f`禁止)→`git diff --cached --name-status`→他agentの差分が同一ファイルに混在する場合は一時index方式(`GIT_INDEX_FILE`)でHEAD版+自分の変更だけをcommit→`git commit`→`git push origin HEAD:main`。secret grep 0件確認。ACTIVE_TASK/RESULT_PACKET*はgitignore対象(commitしない)。
作業ブランチは`work/post-merge-01`。amend/rebase/force push/stash/clean/reset --hard/checkout -f/`git checkout -- <file>`禁止。

## 報告(`docs/pm/RESULT_PACKET_FZST17.md`に書き、要点を返答)
- Step 1の分類(A/B/C)と証拠(コマンド出力の要点)。委任_16報告との不一致があれば明記。
- 是正した内容・REGRESSION_02.mdの再実行結果(test件数PASS/FAIL)。
- 変更ファイル一覧・commit hash・push結果・raw.githubusercontent.com URL。
- RESULT_PACKET 4行(既存仕様整合/未承認機能の既定値/失敗終了時の成果物/撤去・残置)。
判断を要する不明点があれば、推測で進めず報告で止める。