# 委任_07: AUW(ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01)— Closeout準備: main取り込み・SSOT・Dangling・Gate 4 revert予行・後方互換test・merge計画(mainへのmergeは行わない=ユーザーGo待ち)

場所: `C:\Users\tensh\eigo-radio`、branch `feat/auw-unified-asr-01`(HEAD cfada30b7)。禁止git操作: add -A/-f/stash/reset --hard/checkout -f/clean/rebase/amend/force push、mainへのpush/merge禁止。有料API上限 JPY 5(narrator A2外側ループの実音声1件のみ、再起動不可、隔離)。test実行は通信遮断plugin、本番stateへ副作用を出す既存testは有料runと並行しない。

## T-0
委任文を本ファイルへ全文保存、checker→_check.json。stop_scope_check rc=0。

## 参照
ユーザー原文_01.md(L201-215 15条件、L143-153、STOP条件)、DESIGN_01.md/DESIGN_02_ADDENDUM_01.md(§2 L99 後方互換test、Gate 4 revert予行)、IMPLEMENTATION_02b/03/04/05/06c.md、RUNTIME_EVIDENCE_06.md §3/§12/§13/§14、OPEN_ITEMS.md Grep OPEN-356・_post_slowdown_cascade_rescue・OPEN-146・Primary#2・OPEN-145、CURRENT_SPEC.md Grep Secondary ASR・cascade・_post_slowdown_cascade_rescue・Primary#2・KP解説・max_attempts、DECISION_LOG.md Grep ASR-TTS-UNIFIED、docs/pm/USER_DECISION_REGISTER_01.md Grep U1/AUW/#18、docs/pm/PM_GOVERNANCE.md Grep Gate 3/Gate 4/Gate 7/15-9/Dangling。全文読込禁止。

## やること
1. main取り込み: git fetch origin→git merge --no-edit origin/main をbranch上で(mainにはCRB/OAR-02の文書commitのみ)。競合があれば解決せずSTOP報告。取り込み後、AUW中核test+静的監査を再実行し一致を確認。
2. narrator A2外側ループの実音声1件(06e申し送り(d)): 隔離runで通算3回目減速後NG→HR末端を実音声で確認(JPY≤5)。§14へ追記。
3. 後方互換test(ADDENDUM §2 L99): tts_generation_results.json等の新キー(asr_judgement/asr_judgement_inherited/asr_judgement_pre_slowdown/technical_stop_status/試聴リストJSON)を持たない旧出力を既存の下流(HR Lock build_attempts_detail、ページ生成、master store、集計script)が従来どおり読めること、新キーありでも旧読み手が壊れないことをtestで固定。
4. Gate 4 revert予行: 別worktree(git worktree add ../eigo-radio-auw-revert <branch HEAD>、パス長に注意)で、git revert --no-commit <mainからの全AUW commit範囲>(merge commitは-m 1)またはgit diff origin/main...HEAD -- '*.py' '*.json' | git apply -R 相当でコードをmain相当へ戻し、(i)適用が衝突なく通る (ii)旧test(main時点のbaseline)がmain時点と同じ結果になる (iii)flag OFF(cascade_enabled=False/FEATURE_FLAG_SECONDARY_ASR_ENABLED)でのロールバック経路test(06c)がbranch上でもPASS、を記録(REVERT_REHEARSAL_07.md)。worktreeは終了後git worktree remove。
5. Dangling Reference Check: 撤去した_post_slowdown_cascade_rescue/Primary#2/Secondary#2/4段尽きHR直行の記述がCURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.md/PM_GOVERNANCE.md/er026_output/.../reeval_*.py/docs内に残る箇所を列挙し、SSOT側は「旧記述(2026-10-16 AUWで撤去済み、現行は統一judge)」の注記追記(既存行の書換・削除はしない)、証跡scriptは冒頭に「撤去済み関数参照・履歴保存」コメント追加(実行不能を明示)。結果表(ファイル:行/処置)。
6. SSOT草案をbranch上で追記(mainへは入れない):
 - CURRENT_SPEC.md: 統一ASR判定仕様の正式節(状態機械PASS/PASS_WITH_WARNING/NG_PROTECTED/NG_EXCLUDED/NG_BOTH/NG_SECONDARY_UNAVAILABLE/技術STOP、値ガード5値と9例、Secondary 1回+cache、試聴リスト、Section例外維持、KP解説3回、KP英語4回構成の例外明記、OF-AUW-08 R+許容集合縮小、値等価の実装位置、CS MIXED時のSecondary単独採用の挙動変化、U1/U2/U3暫定値、Status=「実装済み・main merge待ち(PRODUCTION_WIRED未宣言)」)。
 - DECISION_LOG.md: 索引1行+本体節(ユーザー原文の決定部分を逐語、Fable判断で採用した技術決定[選択肢A、OF-AUW-08 R+、技術STOP≠Lock未適用、再利用guard]、Opus条件A/Cの所見採否、費用実績: 06 9.9/06b 52.0/06d 23.8/06e 3.5+07、事故: 03b Perplexity未確認、06d再起動5.4)。
 - OPEN_ITEMS.md: OPEN-356更新注記(配線済み・merge待ち)、新規OPEN: (a)U4 技術STOPのLock早期return・Secondary障害時のLR抑止 (b)F4 Family C JA新規TTSがen固定/reuse_from meta非複製 (c)06c(B)再利用guard偽陽性(いちばん/一番・装飾記号) (d)既存testの本番state追記副作用の隔離 (e)STANDARD TTS/legacy費用記録(06 D1、legacy Aは是正済み) (f)D-B4〜D-B6 LR入れ子再帰・HR重複行・audio_text_deviationズレ(main既存、仕様判断) (g)スコア表記「8–1」とASR「8 to 1」の等価(仕様候補) (h)既存test外部通信(er007 openai/er011 huggingface)のmock化 (i)Z entryのasr_judgement_pre_slowdown非保持 (j)旧評価script群のPrimary#2参照(再現不能)。各行に区分・担当工程。
 - docs/pm/USER_DECISION_REGISTER_01.md: U1(JA C1固有名詞・類似度<0.4の除外解放可否、現行維持中)/U2(LR後v1のSecondary必須化範囲、A2_ONLY暫定)/U3(「十分/10分」AMBIGUOUS同表層の扱い: a現行=警告付き採用/b NG_BOTH保守/cWriter側「10分」表記運用)/U4(技術STOP≠HR Lockの早期return+Secondary障害時LR抑止=HR Lockロジック3行変更の承認)/Go: mainへの単一merge承認、をUSER_DECISION_REQUIREDで追加(#83〜)。各項目に現状挙動・推奨・影響を1〜2行。
 - docs/pm/REPORT_LEDGER.md 1行。
7. Gate 3/4/7チェックリストとmerge計画(CLOSEOUT_PLAN_07.md): mergeコマンド(git merge --no-ff feat/auw-unified-asr-01 on main、squash禁止)、merge後に走らせるtest・静的監査・smoke(API 0)、ロールバック手順(revert予行の結果)、15条件の最終充足表(充足/一部/未充足と理由)。
8. commit/push(branch、明示add、secret_scan --staged hits=0)。message: `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_07: main取込+後方互換test+Gate4 revert予行+Dangling注記+SSOT草案(CURRENT_SPEC/DECISION_LOG/OPEN/REGISTER U1〜U4+Go)+Closeout計画。main未merge、JPY <実額>`。

## 報告様式(受入記録5項目)
(1)当初目的=原文L201-215の逐語 (2)成果物 (3)証拠(revert予行結果・互換test数・Dangling表・commit hash・費用) (4)15条件の最終表と1〜8ごとの一致/不一致 (5)判定材料(PRODUCTION_WIRED宣言はしない)。加えて逸脱・累計費用。
