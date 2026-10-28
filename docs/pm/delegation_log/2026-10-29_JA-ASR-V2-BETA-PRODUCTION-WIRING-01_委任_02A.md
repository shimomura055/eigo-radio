# 委任_02A(逐語。転写から機械抽出。Opus原文は OPUS_REVIEW_01.md)
Fableからの委任_02A(JA-ASR-V2-BETA-PRODUCTION-WIRING-01: Production配線の実装・テスト・runtime evidence。費用上限¥20(ASRのみ、TTS 0)。承認済みScope内)。

## 0. 開始手順
- 本プロンプトの`## 0.`〜`## 6.`を `docs/pm/delegation_log/2026-10-29_JA-ASR-V2-BETA-PRODUCTION-WIRING-01_委任_02A.md` に逐語保存。末尾`<<<OPUS>>>`〜`<<<END>>>`間を `docs/research/JA-ASR-V2-BETA-PRODUCTION-WIRING-01/OPUS_REVIEW_01.md` に一字一句そのまま保存(先頭に `# Opus条件Aレビュー(逐語、2026-10-29、Fable受領)` の1行)。heredoc失敗時はpyで書く。端末に再表示しない。
- `tools/stop_scope_check_01.py --managed-id JA-ASR-V2-BETA-PRODUCTION-WIRING-01 --run-dir docs/research/JA-ASR-V2-BETA-PRODUCTION-WIRING-01 --out docs/research/JA-ASR-V2-BETA-PRODUCTION-WIRING-01/stop_check_02A.json`(rc=3で停止)。有料run(runtime evidence)開始前にも再実行。
- 正本: ユーザー原文 `docs/pm/delegation_log/2026-10-29_JA-ASR-V2-BETA-PRODUCTION-WIRING-01_USER.md` §1A・§3(目的)、`WIRING_DESIGN_01.md`/`COVERAGE_MATRIX_01.md`/`TEST_PLAN_01.md`(設計)、上記OPUS_REVIEW_01.md(必須修正)。Python実行は `.venv\Scripts\python.exe`。
- 並行Worker: (M)Family Y調査3名が`docs/research/FAMILY-Y-DEBATE-SOURCE-DEEP-RESEARCH-01/`を編集中。ACTIVE_TASKは(I)行のみ(編集直前Re-Read)。index.lock衝突は数秒待って再試行。

## 1. Fable判断(Opusレビュー照合済み。設計とOpusは実質一致、新仕様・新トレードオフなし→Fable判断で実装へ進む)
- **Opus必須修正M-1〜M-6をすべて採用**(circuit open時のβ早期return/βの費用・呼出回数・consecutive_failuresの計上/β発火条件に`length_ok is True ∧ audit["length"].primary_ok is not False`/Store再判定は`kp_vote_gate_follows`より前・版一致なら保存判定を信頼・版不一致はResolverなしAPI 0再判定・判定核hash↔`JUDGE_RULE_VERSION`固定test・β資産は`audit["secondary"]["text"]`保存必須/新module・依存libは`v2b.active`分岐内の遅延import+seam例外は従来判定(L0)へ+`ja_v2beta.error`記録+完了ブロックに無効化件数/Secondary側v2寄与でstate=PASSならPASS_WITH_WARNINGへ格上げ)。
- **推奨R-1〜R-10も採用**。特にR-2(β失敗をconsecutive_failuresに計上)、R-5(T-Rは既知8行の同一性集合で判定、1行でも増分があれば報告)、R-6(β PASS_Wは証拠の弱い順に先頭表示、run単位JSON、UDR #206/#207へ再提示トリガー登録=報告であってGateではない)、R-7(`JA_V2_BETA_ENABLED=True`定数+`is_active_for_run()`は`current_scope()`のみ読む、scope内OFFは`disabled_by:"constant"`記録、T-D1で`is True`固定)、R-8(HR一覧はHR queue/Lock登録から)、R-10(HEAD失敗5件の是正は**別commitで先行**。期待値合わせでなく不変条件で直す。現行Productionの承認仕様逸脱が判明したら黙示是正せずOPEN化してFableへ)。
- R-4: Secondary側E3/E4はproto同一(既定変更なし)。parityで「cls_sにE3/E4ありでS1S救済」件数を集計し、0件でなければ報告(判断はFable)。
- 不採用/禁止: L3別表・ASR再試行・合意再試行・超→こえ・R-1コード・veto化・新Gate・公開前人間試聴必須条件の復活・自動配信/公開機構・Family A/B/Cの挙動変更(scope外byte同一)・記事『月は少しずつ縮んでいる？』の公開差替え/FX-MOON-SHRINKING判断の代行・既存HR Lock/HUMAN_APPROVEDの変更。

## 2. やること(順序。独立部分は並列可)
1. **先行commit**: HEAD失敗test 5件の是正(R-10)。原因→不変条件で修正→`.venv`で該当test PASS→commit「委任_02A-0: 既存失敗test是正」。承認仕様逸脱が見つかったらRESULT_PACKETに即記載(作業は続行)。
2. 新module `er078_ja_v2beta_01.py`(純関数+定数+読取関数、題固有語なし)、`er007_ja_secondary_asr_01.py`の4 seam(S0/S1P/S1S/S2/S3)、`er078_reuse_value_guard_01.py`の寄与ブロック(M-4の位置)、registry/報告helper(`rescue_reason_ja`、run単位JSON、X/Z既存節との整合、**Y試聴ページ節の追加**`er121_family_y_runner_01.py:1282`)、完了ブロック標準出力。`unified_judge`本体は無改変。
3. テスト: TEST_PLAN_01全件+Opus M-1〜M-6/R-9各ケース+静的test(題固有語なし/制御フロー未参照[guard_entry内contributed()は許可]/「試聴必須」語なし/DefaultON `is True`/scope外byte同一/import graph)。既存regression(er078/er007/er011/er109/各runner test)全PASS。合格基準=「HEAD失敗ID集合からの新規失敗0」+新test全PASS。
4. **Offline再現(API 0)**: 月6本の保存draw→4 PASS_W/2 HR(`EVAL_UNIFIED_03`と一致)、N3 30負例+拡張負例→誤PASS増分の**行集合**が既知8行(T1 6+T2 2)と同一(R-5)、汎用題positive/negative、metamorphic。
5. **Runtime evidence(有料、上限¥20)**: 正式Production経路(X runner等のJA判定関数を実wavで実走。TTS再生成なし、既存wav再利用)で、月6本wavをv2+β配線後の判定にかけ、`asr_judgement`に`verdict/rescue_basis/judge_rule_version/ja_v2beta`・model_id(`gpt-4o-mini-transcribe`/azure)・routing・費用が記録されることを示す。E0は一時out_dirで、Production results・Store・HUMAN_APPROVED記録へ書き込まない(R-9e)。X/Y/Zそれぞれ1 Section以上で実走(Y/Zは既存run_dirのJA wavを再利用)。β追加Secondary呼出の費用計上がauditとrsで一致すること(M-2)。
6. 最終制作報告の掲載例: 実走結果からPASS_W(新方式)entryを含む完了ブロック・JSON・試聴ページ節(X/Y/Z)を生成して`RUNTIME_EVIDENCE_01.md`に貼る(対象音声・発生理由・警告内容)。
7. 月6本の新判定を再掲: 4 PASS_W(各rescue_basis・警告)+2 HR(ms_03 a1・reselect a3の扱い=既存HR Lock→個別採用[UDR #203、本IDで判断しない])。ユーザー既試聴判断(6本Human OK)との整合を1行で。
8. SSOT: `CURRENT_SPEC.md`(日本語ASR判定節へ v2+β/R-1 OFF/PASS_W非ブロッキング/verdict schema/再利用規則/最終報告掲載を追記。該当行をGrepで特定、全文読込禁止)、`DECISION_LOG.md` 1エントリ、`OPEN_ITEMS.md`(OPEN-515へPRODUCTION_WIRED候補追記[Fable受入後確定]、OPEN-263/272/287の統合先として追記、新規OPENは必要時のみ)、`docs/pm/USER_DECISION_REGISTER_01.md`(#201/#202/#204/#205(a)/#206/#207=判断済み(2026-10-29)追記、#206/#207に再提示トリガー[R-6]、#205(c)=独立C、#203=未決のまま)、ACTIVE_TASK(I)行。
9. `docs/research/JA-ASR-V2-BETA-PRODUCTION-WIRING-01/{RUNTIME_EVIDENCE_01.md, TEST_RESULTS_01.md, NEGATIVE_RECHECK_01.md, COST_01.md}`。commit(編集ファイル明示`git add`)→`git push origin HEAD:main`(FFのみ)。配線commitは先行commitと分ける。

## 3. 範囲(11-8)
範囲内=承認済み仕様(2026-10-29)の配線・Opus必須修正・承認済み仕様との矛盾の是正(既存失敗test含む)・Regression・検証・SSOT。範囲外=受理面/閾値/方式の新設・拡大(§1禁止事項)、A/B/C、月記事公開、自動配信。設計と異なる実装判断が必要になったら、その箇所だけ`判断候補`(停止根拠file:line)として報告し、他は進める。費用¥20超過見込み→停止して報告。

## 4. 報告
`docs/pm/RESULT_PACKET_JAW2.md`: 整合(ユーザー原文§3-5の完了条件ごとに達成/未達)/未承認機能0の確認/成果物と目的適合(成功・失敗経路の最終成果物)/撤去・残置/判断候補/R-4・R-5集計/費用実績/commit hashes。`判定整合:`行。最終回答は短く(test結果・月6本判定・負例増分行集合・費用・commit・判断候補)。

## 5. 補足
Opus指摘の未読箇所(`er127_tts_block_policy_01.py:726-740`、`er006_master_audio_store_01.py:130-137`の`_probe`が`asr_judgement_inherited`を含むか、proto依存lib)は実装前に確認して設計へ反映。

