# 委任_02B 本文(逐語。2026-10-28、Fable→sonnet-worker)

管理ID JA-ASR-FALSE-NG-ROOT-FIX-02 委任_02B「Phase 2: 統合proto実装+(ii)ASR再試行の実測+再評価」。前提=Phase 1成果(`docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/`の PREREGISTERED_01/EVAL_UNIFIED_01/RESIDUAL_NG_ANALYSIS_01/DESIGN_PROPOSAL_01、`eval_unified_01.py`、ユーザー原文=`docs/pm/delegation_log/2026-10-28_JA-ASR-FALSE-NG-ROOT-FIX-02_USER.md`。全て先に読む)。Fable判断: 案Rを採用して進める=(i)v2+β をコア、(v-c)読み候補辞書拡張と(ii)ASR再試行を**切替可能な層として個別評価**、(iv)は既存HR機構との差分として定義。Opus条件Aレビューを並行実施中(結果はFableが委任_03で反映。あなたは待たない)。

**ファイル範囲**: `docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/`配下(PM_AUDIT_*除く)、`docs/pm/RESULT_PACKET_JAFIX2C.md`、`docs/pm/delegation_log/2026-10-28_JA-ASR-FALSE-NG-ROOT-FIX-02_委任_02B.md`(本文逐語)。**Production code(er0XX_*.py)・SSOT・ACTIVE_TASKは編集禁止**(別workerがSSOT同期中)。Family A/B/C不可。
開始時と有料run前に `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id JA-ASR-FALSE-NG-ROOT-FIX-02 --run-dir docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02 --out docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/stop_check_02B.json`(rc=3で停止)。

### 1. 事前登録 `PREREGISTERED_02.md`(実行前にcommit)
- 評価セット: 正例6音声(決定対+全draw 27対)、NEG 1439(Phase 1と同一、sha固定)+新規負例draw(下記3)。
- 層定義と切替: L0=現行HEAD、L1=v2 Primary読み層(**Primary側の不規則読みガードを追加**: `extract_atoms_ja`の不規則読み判定を使い、一日/ついたち等の不規則読み値はv2発音等価の対象外→Production判定へ戻す。fail-closed)、L2=β composite、L3=読み候補辞書拡張(『超』→こえ を**汎用規則**で: 数量+超 の接尾で ちょう/こえ 両読み。月題固有の語句は禁止。発火条件=両engineの値が原稿値と一致、かつ差分がこの語だけ。E4/C2同形異音との衝突test[本長/本帳/本蝶 は不受理]を含む)、L4=(ii)best-of-N再試行(N≤3、評価では保存drawを使い「最初にPASS/PASS_Wになったdrawで止める」をシミュレーション)。
- 合格写像(ユーザー§6): 6音声の最終判定を PASS / PASS_W(試聴必須) / NG で別集計。負例増分=Phase 1の3型以外で増分>0なら当該層は不合格。回帰0必須。VALIDATED判定はFableが行う(あなたはStatus候補のみ)。
- best-of-Nの誤PASS上限: 負例wav 1本につき4 drawで「いずれかのdrawがPASS/PASS_W」になる率を、N=1〜4で報告(釣りリスクの実測)。

### 2. proto実装 `proto_unified_02.py`(+test)
`proto_reading_compare_02.py`/`b_light_proto_02.py`を再利用し、L1〜L4をflag引数で合成(既定は全OFF=L0と同一出力であることをtestで固定)。Production関数(`er078_asr_unified_judge_01`/`er007_ja_secondary_asr_01`)は**呼ぶだけ・編集禁止**。各層の発火は監査キー(layer名・根拠)として出力。

### 3. (ii)実測(有料、上限¥3、見積約¥0.7)
`n3_clips_01.json`のN3 30 wav(保存済み)を OpenAI gpt-4o-mini-transcribe で各4 draw 再転写(Azureは変動0のため不要)。`BUDGET_PLAN_02.md`に見積→実行→`BUDGET_LOG_01.md`に実費・呼出数を追記。cost_logへ記録。転写は`n3_redraw_02.json`へ保存(wav sha・draw番号・モデル名・時刻)。ネットワークはこの工程だけ。6正例の追加drawは不要(27対で十分)。

### 4. 評価 `eval_unified_02.py`(API 0、socket guard、2回実行でsha一致)→`EVAL_UNIFIED_02.md`
- 6音声×層の組合せ(L0 / L1 / L1+L2 / L1+L2+L3 / L1+L2+L3+L4[N=2,3]): 最終Gate判定・理由・決めた条件・転写。
- 負例: 増分誤PASS(層別・型別)。L3は『超/越/超え/こえ』を含む負例(値違い・本長等)で検証。L4はN3 30wav×4drawでN別の誤PASS率。
- 残NG(あれば)の原因と「機械的に確定できない」ことの根拠、Human Review条件(iv)の機械条件案(既存HR Lock/個別採用registryとの差分を明記、抜け道の有無を負例で検証)。
- 6合格条件への到達度表(達成/部分/未達)とStatus候補(VALIDATED/REJECTED/USER_DECISION_REQUIRED、理由)。
- 単価: 採用時の記事あたり増減(保存Secondary利用/Azure追加呼出/再試行費/再生成削減)を、現行の誤NG率が未知なら区間で示す。

### 5. 成果物・Git
`docs/pm/RESULT_PACKET_JAFIX2C.md`(≤20行: 6音声×層の結果、負例増分、best-of-N誤PASS率、残NG、Status候補、費用、判断候補A/B/C/D仕分け、判定整合行、4行[既存仕様整合file:line/新方式既定値/失敗終了時の成果物/撤去要否])。commit: `git diff --cached --name-only`空を確認→自分のファイルのみ明示`git add … && git commit -m "JA-ASR-FALSE-NG-ROOT-FIX-02 委任_02B: 統合proto(v2+β+辞書層+best-of-N)実装+N3再転写実測+再評価(実費X円、Production変更0)"`を1コマンド、`git add -A`禁止。`git push origin HEAD:main`(FFのみ、拒否時fetch後再試行、force禁止)。hand-back: 6音声×層の最終表(1行ずつ)、負例増分、N別誤PASS率、残NG、Status候補、実費、commit sha、判断候補。
