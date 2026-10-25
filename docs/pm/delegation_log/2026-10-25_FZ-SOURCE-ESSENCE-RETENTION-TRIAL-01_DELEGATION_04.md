# 委任文(Fable→sonnet-worker)
管理ID: FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_04(Opus条件A必須修正1〜5+推奨の反映→案AのProduction実装[Writer 4か所+Seed 5作品補完+test]→全回帰→『告げ口心臓』正式再生成 run_sf_prod_02[Std/Adv]→公開差替え→runtime evidence→SSOT→Git)
前提: 委任_03(WIRING_DESIGN_01.md、OPUS_REVIEW_REQUEST_02.md、先行検証16/16 byte一致、commit 547074875)。**Fable判断: Opusレビュー(§1)は設計見直し不要・必須修正5点。設計と実質一致、案A=APPROVED_FOR_PRODUCTION(ユーザー承認済み)、再生成も承認済み(UDR #193)のため、修正反映後に実装・再生成へ進む(Fable Go)。PRODUCTION_WIRED判定はFable受入後。ユーザー最終試聴PASSは先取りしない。**

## 0. 最初に
- `docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/OPUS_REVIEW_02.md` に§1のOpusレビュー全文を保存(先頭に「Fable転記、2026-10-25、条件A[Production配線]」)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 522 --out docs/pm/delegation_log/2026-10-25_FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01_DELEGATION_04.md`。冒頭が「管理ID: FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_04」と一致するか確認、不一致なら index 519〜525 を順に試す(`--index -1`不可)。

## 1. Opusレビュー全文(逐語)
```
## Opus独立技術レビュー(条件A): FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 案A Production配線設計 + 『告げ口心臓』再生成計画

**判定: 必須修正あり。設計の見直しは不要。** 下の修正5点を反映すれば実装へ進めてよい。Writer側の配線(W1〜W5)、Seed補完、runnerのコード変更0という判断は妥当と確認した。
- 確認した事実:
  - Prompt組立は`run_writer_chain`(730〜768行)が毎回Seedから作り直す純関数。初回・`--regenerate-stage`・resume・部分run・LLM技術retryのどれでも同じbuilderを通る。
  - resumeで再利用するかの判定には`ess.sha256`(narration_voiceを含む)が入る(781行)。
  - plan/support/kp/TTSは物語本文のPromptを組まない。
  - 『告げ口心臓』の話者設定(structure 304〜321行)は既に一人称前提。
  - Std側の共有ブロック(`er003_v1_n3_01_standard_a2_generate.py`)に人称の指定はない。
  - 本番コードからDEV runnerへの参照は0件。
  - Prompt本文に入る人称関連の指示は`REVISE_USER_TMPL`の141行と`_CONVERSION_SUBSTITUTIONS`の131行だけ。131行は、Grepした範囲で5作品の`er026_seeds`の`conversion_plan`に一致文言がなく発火しない。

### 必須修正
1. **【最重要】再生成計画③「tts_b1bとtts_a2を並列2process」はそのままでは動かない。**
   - 同じrun dirでは2本目が`FamilyZRunLockHeld`で起動を拒否される。`er062_family_z_structure_01.py:558-587`の`acquire_run_lock`が、run dir単位で`RUN_LOCK.json`を排他作成するため。
   - 加えて、5分間に3回以上起動すると`RESTART_STORM`でrun dirに`STOP`が自動作成される(607-636行。解除は`--clear-stop`のみ)。
   - 修正案: ③と④をまとめ、`--stages tts_b1b,tts_a2,provision_shell,gate,assemble,pages,page_verify`の1起動にする(OPEN-480も満たす)。各起動の間は5分以上空ける。
   - 「並列2process」の記述は撤回する。直列化の理由は「同じrun dirの排他lock」。
2. **公開差替えの確認範囲にStandardを加える。** 旧Standardも旧三人称Advから作られているため、同じ問題を持つ。
   - (ii)の確認対象に`standard.html`と`audio_standard`(sha差分、全ファイルがrun_sf_prod_02由来であること)を追加する。
   - 「housemate」が無いことの確認(否定条件)だけでは弱い。両レベルの本文に一人称の`I`と、聞き手への`you`があることも、Fableが目視で引用確認する(自動判定は作らない)。
3. **runtime evidenceで「dumpされたPrompt=実際に送ったPrompt」を結びつける手順を明記する。**
   - `{stage}_prompt.txt`は、ensure_stageで本文を再利用した場合でも書き直される(768行)。dumpの存在だけでは送信の証拠にならない。
   - 受入時の手順:
     - (a) run_sf_prod_02でr0/r1/r2/std_adjustの4段すべてのstatusがgeneratedであること。
     - (b) 各dumpから`sha((dev or "") + "\n\n---\n\n" + user)`を再計算し、provenanceの`prompt_sha256`と一致すること。r1/r2のdumpはdevも区切りも含まないので、再計算式を合わせる。
     - (c) git HEADと`er062_family_z_writer_01.py`のfile shaを`RUNTIME_EVIDENCE_02.md`に記録する。これが「Trial専用経路ではない」証拠になる。
   - 新しいログ機構は不要。narration_voice自体はessentials_sha256とdumpで追跡できる。
   - PM Gateの「各工程」はR0/R1/R2/Std調整を指すと明記する(ユーザー原文§1の範囲。plan/support/kpは本文Promptを作らない)。
4. **W6(CPチェックリストのnarration行を「重大」にする)と、既存の`CP_TREATMENT_RULE`(803-808行、2026-10-23ユーザー承認)の文言を整合させる。**
   - 現在の(A)重大の列挙にnarrationが無い。このままだと「重大なのに処置規則の対象外」という矛盾が出る。
   - 推奨: (A)の列挙にnarrationを加える。根拠として10-25承認の§1(語り口維持)と§6(PRODUCTION_WIRED条件)を併記し、DECISION_LOGに記録する。
   - 処置は既存の明示`--regenerate-stage`と決定論パッチのみで、新retryや自動判定は入らない。承認範囲内と判断する。
5. **DEV runnerを昇格後に動かすと壊れることへの対処。**
   - `fz_essence_dev_runner_01.py`のarm iiiを昇格後に動かすと、Narration行が二重に入る。さらに`revise_dev`がテンプレートを先に置換するため、W3の`assert _REVISE_THIRD in tmpl`が失敗する。
   - 対処(どちらか):
     - (a) DEV runnerの先頭に、本番writerが`_NARR_LINE`を持っていれば停止するfail-fast guardを入れ、「歴史的」と注記する。
     - (b) 同runnerのtestは移植済みであることを確認し、全回帰の対象外として理由を記録する。
   - これを実装commitの前に決める。

### 推奨(任意)
- `ESSENTIALS_EXEMPT_STORIES == ("melos",)`を固定するtestを追加する。`in third person`の残置がMelos以外へ広がらないようにするため。
- 『賢者の贈り物』の`free_to_cut`に"the narrator's jokes and asides"があり、記入規則(c)と緊張関係にある。Trialとのbyte同一性を守るため、今回は変更しない。次回この作品を再生成するときに見直す、と記録する。
- R0の共通ブロック94行の例示(her mother/his father)は三人称の所有格になっている。Trialとbyte一致している範囲なので、今回は変更しない。

### 論点別の所見
- **(a) 配線の網羅**: 漏れは見つからなかった。retry(`llm.call`)はPrompt固定。`_bak_*`と`STALE_*`はplan以降の段なので、本文Promptには関与しない。
- **(b) Seed必須化**: W4(`Essentials.__init__`)とW5の2か所で必須化し、置換条件を`essentials is not None`に揃える。この設計で第3状態(essentialsはあるのに語り口欄が無い)には到達しない。妥当。
  - **Melos**: 残置を「受容して記録」で可とする。理由: 原作が三人称で、承認と矛盾しない。汎用句に置き換えるとMelosのbyte同一性が崩れる。完了報告の§2に「Melos専用経路に原作どおりの三人称指定を残置」と明記する。
  - **『二十年後』**: 「受容して記録」。既存Seedの`conversion_plan`はBobを主役に置いており、"close on Bob"はこれと一致する。視点がBobに寄ることで、結末前に警官の正体を伏せる働きとも矛盾しない。有料の追加確認は不要。API 0の構造test+次回再生成時の初回CPで足りる。
- **(c) 「役割で呼ぶ」指示との整合**: Narration行は「人称・視点・語り手の立場を保つ」という汎用1句だけ。新たな文学基準や作品別の禁止ルールは含まれていない。
- **(d) 既存作品の副作用確認**: Prompt byte一致16/16+Trial結果の再利用で、必要十分と判断する。猿の手の段落数+8は限界として記録すれば足りる。告げ口心臓の`free_to_cut`差替えは承認範囲内と判断する。Trialで検証した条件そのものである。現行の「the narrator's repeated arguments that he is wise and cunning」はユーザー原文§4-3(自己正当化)と矛盾する。DECISION_LOGに、案AのSeed補完の一部として根拠付きで記録する。
- **(f) S-1(既存run dirでSeed sha不一致STOP)**: M3(受容して記録)で可。影響はplan/support/kpのみ(`_prov`を呼ぶのは1421/1440/1697行だけ)。注意: 試聴待ちの既存Z作品で、KPやsupportをその場で直す必要が出た場合はSTOPする。そのときはM4(provenanceの付替え手順)を別委任で作るか、新runで作り直す。
- **(g) 撤退とX/Yへの波及**: 単一commitのrevert+STALE退避+公開物の差替えを別commitにする、で十分。X/Yとの共有は無く、波及は無い(er111はnarration_voiceを参照しない)。
- **(h) 再生成計画**: 段階分割と、CP確認をstd_adjustの後・planの前に置く点は妥当。予算70円は前例と同じだが余裕が少ない。TTSの段別見積は各40円で、着手時の累計約22〜29円に足すと62〜69円になる。LR等で費用が増えると、guardでSTOPしうる。STOPしても安全側の停止であり、300円以下の範囲で上限を上げるのはAI自律で可。事前に80円程度へ上げておく選択肢もある。

### リスクと対処
- 並列TTSで二重起動を拒否される、またはRESTART_STORMでSTOPする → 必須修正1。
- 旧Standardが残る → 必須修正2。
- 本文を再利用したdumpを証拠と誤認する → 必須修正3。
- DEV runnerを誤って再利用し、二重注入になる → 必須修正5。

### ユーザー判断が必要になりうる論点
現時点ではUDRは不要と判断する。Melosの残置と、CP処置規則へのnarration追加は承認範囲内の整合作業として扱う。どちらも完了報告とDECISION_LOGに明記して、透明性を確保すること。
```

## 2. Fable判断(反映指示)
- 必須修正1〜5: 全て反映。修正5は(a)fail-fast guardを採用(DEV runnerは歴史的資産と注記)。推奨3点も採用(`ESSENTIALS_EXEMPT_STORIES`固定test、賢者free_to_cut・R0例示は今回不変で記録)。Melos残置・CP処置規則へのnarration追加・告げ口心臓free_to_cut差替えは承認範囲内の整合作業としてDECISION_LOGに根拠付きで記録(新UDRは起票しない)。
- 再生成: 新run `run_sf_prod_02`。起動構成=①`seed_check,writer,std_adjust`→CP確認(narration行を含む。Fable目視用にr2.md/std.mdの冒頭段落と聞き手への語りかけ箇所を `COMPARISON_03.md` に抜粋)→②`plan,support,kp`→③`tts_b1b,tts_a2,provision_shell,gate,assemble,pages,page_verify`(1起動、OPEN-480準拠)。各起動の間隔5分以上、RESTART_STORM回避、再起動回数記録。`--approved-budget-jpy 80`(Fable: 300円以下の自律範囲で引上げ、概算40円との差は実費で報告)。TTS直列化flagを尊重(並行agentのTTSと並走しない)。HR Lock発生時は既存の自律解決手順(approve_regenerateはFable権限=停止して報告)。
- 公開差替え: `user_test/family_z_tell_tale_heart_01/` の index/standard/advanced と audio_standard/audio_advanced を全てrun_sf_prod_02由来に(旧ページはscratchpadへ退避、sha差分で旧ファイル残存0を確認)。「housemate」0件に加え、Std/Adv本文の一人称`I`と聞き手への`you`の箇所をFable目視用に引用抜粋(自動判定は作らない)。page_verify PASS、公開URL HTTP 200。
- runtime evidence `RUNTIME_EVIDENCE_02.md`: 修正3(a)(b)(c)の手順どおり(4段status=generated、各dumpからのprompt_sha256再計算一致[r1/r2は再計算式を合わせる]、git HEAD+writer file sha)、essentials_sha256、actual_model_id、routing_key、seed_check stage log、cp_checklist(narration行)、REVISE文言に"in third person"が含まれないことのdump Grep、tts段のmodel/voice/style記録、Gate結果、費用。
- Production採用時の全回帰: 自分起因の失敗0(既存test期待値の差替えは設計どおり、理由を記録)。
- 既存作品の副作用: 再生成しない。配線後にProduction builderで賢者/開いた窓/猿の手/告げ口心臓のR0/R1/R2/Std Promptを組み、Trial送信Promptとbyte一致(16/16)を再確認し記録(委任_03の先行検証をProductionコードで再実行)。二十年後はPrompt組立のみ(構造test)。
- 量産単価: 追加LLM 0、+約90 token/段(実測で確認)。

## 3. 文書・SSOT・Git・報告
- `WIRING_DESIGN_02.md`(修正反映後の最終設計、変更箇所表、Melos残置・CP規則整合の記録)、`RUNTIME_EVIDENCE_02.md`、`COMPARISON_03.md`(現行run_sf_prod_01 vs run_sf_prod_02のStd/Adv冒頭・語りかけ箇所・結末の抜粋、Fable目視用)、`REGRESSION_01.md`(全回帰結果、期待値差替えの一覧と理由、byte一致再確認)、`BUDGET_LOG_01.md`(再生成実費、概算40円との比較)。
- SSOT: `CURRENT_SPEC.md` のFamily Z該当節に案Aの仕様行を追記(DECIDED、Fable受入後にPRODUCTION_WIRED表記=本委任では`WIRED_PENDING_FABLE`)、OPEN-508 Status=`WIRED_PENDING_FABLE`、OPEN-503=『告げ口心臓』run_sf_prod_02=`COMPLETE_USER_LISTENING_PENDING`(旧run_sf_prod_01は退避扱い)、`DECISION_LOG.md`(配線・Seed補完[free_to_cut差替え根拠]・Melos残置・CP規則整合・再生成の記録)、`docs/pm/USER_DECISION_REGISTER_01.md` #193に実施記録(最終試聴は未回答のまま)、`docs/pm/ACTIVE_TASK.md` 自行(並行agent: FX-CORE-NUMERIC 委任_04、FX/FZ-CHUNK 委任、FZ-DIALOGUE調査、STUDY-TEXT。編集直前に再Read・最小Edit・衝突時再試行)。SSOT編集前にscratchpadへバックアップ、編集後 `git diff --stat -- <file>` 確認(空ファイル化・CRLF事故防止)。無料処理は`py`、有料runは`.venv\Scripts\python.exe`。
- Git: Production実装(Writer+test+Seed補完+DEV guard)は1 commit(撤退=revert単位)、公開差替え・成果物は別commit、SSOTは別commit。`git status` → 対象pathのみ `git add`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status`(意図外D/Aなし・secret 0件・wav/telemetry/raw_usage_log不混入、公開mp3は`user_test/`配下のみ) → `git commit --only -- <path…>` → `git push origin HEAD:main`。他agent差分混在時は一時index方式。import graphに未commit変更がないことをProduction run前に確認。
- 報告 `docs/pm/RESULT_PACKET_FZSE4.md`: ユーザー原文§8の1〜10の順(1 配線完了状況+runtime evidence、2 旧固定指示撤去確認[Melos残置の明記]、3 既存作品副作用[byte一致16/16]、4 再生成結果[Std/Adv秒数・Gate・HR・retry]、5 語り口維持の抜粋[Sonnet所見、最終はFable目視]、6 test結果、7 試聴URL、8 実費/量産単価、9 SSOT/Git、10 Status候補=WIRED_PENDING_FABLE+USER_LISTENING_PENDING、残Open)。変更ファイル・commit、`check_delegation_prompt.py`結果、問題点。

## 4. 禁止
未承認のChunk方式等の混入(別案件FX/FZ-CHUNK Trialの方式をProductionへ入れない)、新Validator/追加LLM/新retry、作品別禁止ルール・新文学基準の追加、Family X/Yへの展開、Gate迂回・`--clear-stop`・approve_regenerate(Fable権限)、ユーザー最終試聴PASSの記録、Trial音声の正式音声としての流用、自PID以外のprocess終了。