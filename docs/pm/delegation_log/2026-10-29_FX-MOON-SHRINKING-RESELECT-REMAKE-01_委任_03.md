# 委任_03(2026-10-29、Fable→Sonnet。FX-MOON-SHRINKING-RESELECT-REMAKE-01 + JA-ASR-V2-BETA-PRODUCTION-WIRING-01 Closeout)

Fableからの委任(2件): (1)JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_04A=Closeout確定(API 0) (2)FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_03=月記事『月は少しずつ縮んでいる？』Std/Adv最終完成版の制作・提出(run Cap¥60、現在約¥20.78)。

## 0. 最初に
(a) `docs/pm/delegation_log/2026-10-29_FX-MOON-SHRINKING-RESELECT-REMAKE-01_USER_02.md` を作成し、1行目 `# ユーザー指示原文(逐語、2026-10-29受領。JA-ASR v2+β Closeout／月記事の制作継続)` の後に末尾`<<<USER>>>`〜`<<<END>>>`間を一字一句そのまま保存(heredoc失敗時はpy/node)。
(b) 本プロンプトの`## 0.`〜`## 5.`を `docs/pm/delegation_log/2026-10-29_FX-MOON-SHRINKING-RESELECT-REMAKE-01_委任_03.md` に逐語保存。
(c) `tools/stop_scope_check_01.py --managed-id FX-MOON-SHRINKING-RESELECT-REMAKE-01 --run-dir <月記事のrun_dir> --out docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/stop_check_03.json`(rc=3で停止。有料stage前にも再実行)。
(d) 並行Worker: (O)ニュアンス02Bが`er120_part2_*`/`er128*`/`er121:1054`/`export_form_data`/`selection_form_v3`を編集中、(Q)視聴ページ試作が`user_test/dev_enduser_page_01/`。**月記事のassemble/pages/listening page生成の前に** `git status --porcelain -- er120_part2_wiring_01.py er120_part2_grammar_production_01.py er019_family_x_audio_production_runner_01.py er019_family_x_listening_page_01.py er128_kp_confirmed_content_01.py er007_ja_secondary_asr_01.py er078_*.py` を確認し、未commit差分がある間は有料・ページ生成stageを起動せず2分間隔で最大40分待つ(待機中に(1)Closeoutと(2)の照合作業を進める)。ACTIVE_TASKは(A)行と(I)行のみ編集(Re-Read)。index.lock衝突は数秒待って再試行。

## 1. JA-ASR Closeout(ユーザー原文§1。追加Trial・仕様変更なし)
- `OPEN_ITEMS.md` OPEN-515行末に「【2026-10-29 Closeout】ユーザーがPRODUCTION_WIRED受入を確認(原文§1)。Status=CLOSED(PRODUCTION_WIRED)。既知の誤PASSリスク(既知8行)とASR転写の揺れは承認済みの扱いを維持。残件=Z本番runner実走の追補(藪の中 tts_a2で記録予定)、OPEN-588(既存失敗test)」を追記。OPEN-588はそのまま。
- `docs/pm/PM_GOVERNANCE.md`のPM Closeout Mandatory Check(Grepで節を特定)の項目を `docs/research/JA-ASR-V2-BETA-PRODUCTION-WIRING-01/CLOSEOUT_01.md` に埋める(各項目に根拠file:line。目的達成度=達成)。`DECISION_LOG.md` 1件。ACTIVE_TASK(I)行を「CLOSED(PRODUCTION_WIRED、ユーザー確認2026-10-29)」へ。

## 2. 月記事: 承認記録の照合(API 0、原文§2-1〜4)
- 証拠を集める: `docs/pm/delegation_log/*FX-MOON-SHRINKING-RESELECT-REMAKE-01*`(過去のユーザー原文・委任文)、`docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/`(JA_TITLE_ASR_RECURRENCE_01.md等)、`docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/`(6音声の定義: ms_03 a1/a2/a3・reselect a1/a2/a3、Human OKの出所)、HR試聴ページ `user_test/fx_moon_title_asr_listen_01/`、HUMAN_APPROVED記録(`er006_output/.../human_review_queue.jsonl`、`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`、runのaudit、`record_human_approval`の記録先)、UDR #203(`docs/pm/USER_DECISION_REGISTER_01.md:550`付近)、ACTIVE_TASK(A)行、OPEN-515/517。
- 「前回OKとした3音声」を**記録から**特定する(ユーザー原文に『3音声』とある。6音声のうちどの3本に承認記録/ユーザーOKの記録があるか。記録が3本でない場合はその事実をそのまま書き、推測で3本を作らない)。承認のscope(例「this single segment / attempt 2 only」)を逐語で記録。
- 今回HRに残った2音声(ms_03 a1=`p1_value_diff`、reselect a3=`secondary_not_accepted`)と承認記録の関係を表にする(音声|run/attempt|wav sha|今回判定|承認記録の有無・scope|結論=承認済み/未承認)。
- **承認済み音声について再判断を求めない。**Std日本語題に使う音声=承認記録がある音声(複数あれば、現runの採用経路に最も近いもの=reselect runの承認済みattemptがあればそれ、無ければms_03の承認済み音声を既存の「承認済み音声再利用注入(sha照合・HUMAN_APPROVED記録・scope記録)」経路で注入)。注入経路が存在しない/承認scopeが現runへの再利用を許していない場合は、**その事実をfile:lineで示して停止**(新機構は作らない)。未承認の音声しか残らない場合のみ、対象と理由を報告。

## 3. 月記事: 完成版の制作(原文§2-5・6)
- 現状確認: run_dir(ACTIVE_TASK(A)=Adv候補ページ `user_test/family_x_moon_shrinking_reselect_01` 完成、Std=日本語題HR Lockで組立停止)の状態・KP/文法HR確定内容(confirmed_*.json)・既存Gate結果を確認。
- Std: 承認済み音声の注入(§2)→HR Lock解消の正式手順(迂回禁止。承認記録に基づく既存経路のみ)→`--stage assemble --level a2`(TTS再生成なし)→style_profile gate→両レベルplayer/listening page生成(正式経路)→page_verify(local Playwright: 全音声再生・console error 0・4xx 0)→候補ページを `user_test/family_x_moon_shrinking_reselect_01/` に反映(Std/Adv両方)→push→live検証(全asset HTTP 200・byte一致)。**音声の再生成・Prompt変更・Gate緩和・HR Lockの手動解除なし。**JA判定が新たに走る箇所があれば、新配線(v2+β)の`verdict/rescue_basis/judge_rule_version`を記録(X本番runner実走証拠として`docs/research/JA-ASR-V2-BETA-PRODUCTION-WIRING-01/RUNTIME_EVIDENCE_01.md`へ追補)。
- 検証項目(原文§2末尾): 正式Production経路/音声品質(既存Gate結果)/KP・Word/文法解説(HR確定どおり。文法0件なら新仕様=コーナー非表示、採用ありなら表示)/HR確定内容/既存品質Gateの整合、をRUNTIME_EVIDENCE_02.mdに表で。
- 費用: stage別・累計/Cap¥60。超過見込みで停止。

## 4. SSOT・報告
- OPEN-517(または月記事の管理OPEN)行末に「完成候補・ユーザー最終試聴待ち(URL・sha・費用)」追記、UDR #203に「承認済み音声の再利用で解消(再質問なし)。残=記事単位の試聴PASS/公開承認」追記(新UDRは記事試聴の1件のみ)、`DECISION_LOG.md` 1件、ACTIVE_TASK(A)行。commit(編集ファイル明示`git add`)→`git push origin HEAD:main`(FF)。
- `docs/pm/RESULT_PACKET_FXMS3.md`: 整合/未承認機能/成果物(URL・sha)と目的適合(成功・失敗経路)/撤去・残置/判断候補(停止根拠file:line)/費用/commit。`判定整合:`行。最終回答は短く(Closeout commit・3音声照合結果・Std/Adv完成状況・URL・費用・判断候補)。

## 5. 範囲(11-8)
範囲内=Closeout記録、承認記録に基づく既存経路での完成、検証、記録。範囲外=音声再生成(承認なし)、題変更、新機構、HR Lock迂回、Gate緩和、正式公開承認(試聴PASSはユーザー)、Family A/B/C。
