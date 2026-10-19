# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_06(②Rewrite発動条件「両ASR合意」削除・③Rewrite後原稿照合のProduction配線保証チェックリスト[ユーザー2026-10-20 §3・§4の確認項目に1対1で証拠を付ける]+録音2 Lock解除の正規手順特定+Std/Adv全TTS再生成の実行計画[有料実行はしない]、JPY0)。2026-10-20。
並行タスク衝突確認: 同時に委任_05(①Melos/Mellows再照合。書込先=`docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEM1_ROOT_CAUSE_02_SPEC_RECONCILIATION_01.md`・`docs/pm/RESULT_PACKET_FZAQ5.md`・`docs/pm/delegation_log/2026-10-20_*`、M1/validation系コード)が走る。本委任は**それらを編集しない**(読取可)。本委任はコード・Prompt・Lock・SSOTを編集しない(読取と文書作成のみ)。SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`)編集権=無し。`docs/pm/ACTIVE_TASK.md`は先頭へ自委任ヘッダ4行を追記するのみ。commit前に`git status --porcelain`で`.git/index.lock`不在を確認し、自分のファイルのみ明示`git add`する。ユーザー指示原文の保存(T-0)は委任_05が担当(ファイル=`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_ROOT-CAUSE-WIRING-CLOSEOUT_USER.md`、存在すれば参照、無ければ本委任文内の原文抜粋を使う)。

## 性質/到達上限Status/禁止事項
- 性質: 配線証拠の整理(read-only)+実行計画作成。Production変更なし、有料API 0。
- 到達上限Status: `ITEMS23_WIRING_EVIDENCE_COMPILED_REGEN_PLAN_READY_PENDING_FABLE`。PRODUCTION_WIREDの判定はFable(証拠が不足する項目は「未確認」と明記し、PRODUCTION_WIREDと書かない)。
- 禁止: 新規TTS/ASR/LLM呼出(JPY0厳守)/HR Lock・`er026_output/family_z_production_e2e_01/melos/run_e2e_04/a2/audit/review_lock_state.json`(sha256 `6720ce80b7eedba9789dc190a431b030e20486b298a451479129e4d017fb3e19`)の変更(解除手順の**特定**のみ、実行は委任_07)/コード・Prompt変更/`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f/有料runの起動・再起動(26節)。
- 修正範囲の線引き(11-8): 本委任は修正を行わない。配線不備を発見した場合は、範囲内(承認済み仕様文と実装の乖離)か範囲外(受理面・閾値・方式の新設/拡大)かを分類してRESULT_PACKETに記す(修正は委任_07でFableが指示)。
- Opus独立技術レビューGate(11-3): 非該当(証拠整理・計画)。②③の実装はOpus_H(GO_WITH_CHANGES、必須修正6条件充足済み=`ITEMS23_...md` §10)でレビュー済み。内容が変わらなければ再レビューしない。
- 費用/日次: JPY0。
- 時間見込み: 全体1.5〜2.5h(②チェックリスト40分/③チェックリスト40分/Lock解除手順20分/再生成計画30分/報告15分)。並列化: 委任_05と並列。直列化理由: 再生成の実行は①結果のFable照合後(ユーザー§5「まず①の問題を解決し…その後再生成」)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。T-2追記(7-5): TTSを伴う委任は実行前に(1)差分再生成が対象コード上で可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等をタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告。(本委任はTTSを実行しないが、再生成計画でこの4点を**計画として**満たすこと。今回はユーザー指示による意図的な全再生成であり(4)の「想定外」には該当しない旨を計画に明記)
T-3: 本委任は費用上限を伴わない(JPY0)。再生成計画に記す上限は次の定型文で書く: 「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」

## ユーザー指示(原文抜粋。全文は委任_05保存ファイル)
> 3. Rewrite発動条件の修正、およびRewrite後の原稿照合修正は、**正式Productionで確実に有効になっていることを確認する。**
> 4. 録音2のHuman Review Lock解除は承認済み。
> 5. ①の問題解決後、Family Zの該当記事についてAdvancedを含む全TTSを再生成する。Advancedの「He drank」は元の「Melos」を含む原稿に戻す。
>
> ## 3. ② Rewrite発動条件 — Production配線保証
> ユーザー正式承認済み：**「両ASRが同じ箇所の誤読に合意すること」という条件を削除する。**
> 基本フロー：TTS初回生成 → 承認済みPrimary/Secondary検証 → NGなら最大2回のTTS再生成 → なおNGなら既存のRewrite条件・Gateに従ってRewrite。
> 今回の原因分析で、旧条件は実装されておらず、閾値未定義のまま仕様書上だけで配線済みと扱われたことが判明した。今回の修正について、同じ問題を絶対に繰り返さないこと。具体的には以下を確認する。
> - 正式初回Production経路で新仕様が有効である。
> - DEV／Trial専用経路や、起動時の手動フラグONに依存しない。
> - retry／fallback／regeneration／resumeでも整合する。
> - 旧条件がコード・Prompt・Validator・後続経路から参照されていない。
> - 実行時の有効設定・判定経路・モデルrouting等の証拠を確認する。
> - 必須Regression／integration testがPASSする。
> - CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・Gitが実装内容と一致する。
> **コード変更済み・テストPASSというだけでPRODUCTION_WIREDにしない。** 既存の証拠で十分に確認できる部分については、不要な有料再検証を繰り返さないこと。
>
> ## 4. ③ Rewrite後の原稿照合 — Production配線保証
> 正式に許可されたRewrite後は、**書換え後の実送信文を、後続の音声検査の正解原稿とする。** 例：元原稿`Melos drank`/Rewrite後`He drank`/TTS実送信`He drank`/減速後の照合先`He drank`。
> 今回、旧原稿を照合先としていた不具合は修正済みとの報告だが、正式Productionで確実に有効になっていることを再確認する。対象：正式初回経路からのRewrite後TTS/減速後再検証/retry／fallback/regeneration／resume/再利用・継承/Family X／Zの対象共通経路。既存のSTOP・HR Lock・監査記録・品質Gateを変更しない。
> 今回の報告では、offline正式経路による実音声検証はPASSしているが、live Rewrite自然発火は未観測。**必要なruntime evidenceの充足状況を整理し、追加の確認が必要なら最小限の検証で取得すること。** 自然発生の誤発音やRewriteを待つために、不必要な有料TTSを繰り返さない。正式経路の発火証拠が不足する場合は、未確認事項を明示し、証拠なしにPRODUCTION_WIREDと判定しない。
>
> ## 5. 音声再生成・Human Review
> 録音2のHuman Review Lock解除はユーザー承認済み。まず①の問題を解決し、承認済み発音判定が正しく機能していることを確認する。その後、Family Zの該当Melos記事について、**Standard／Advancedの全TTSを正式Production経路で再生成する。**
> - Advancedの「He drank」は、元の「Melos」を含む原稿へ戻す。
> - 原稿の意味・構成・その他の承認済み品質仕様は維持する。
> - 必須の音声QA・再試行・Rewrite・減速後再検証・Assembly Gateを通す。
> - 完成音声と試聴ページを更新する。
> - 実際に発動した判定経路・警告・Human Review対象を記録する。
> ユーザー承認済みの録音2を、新たな判断待ちとして再提示しないこと。ただし、再生成した新音声は既存の品質Gateに従って独立に検証する。①の解決に新たな仕様承認が必要となった場合は、その境界でSTOPし、未承認仕様のまま再生成を強行しない。

## 本委任の作業
成果物A: `docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEMS23_WIRING_ASSURANCE_01.md`(新規)。ユーザー§3の7項目・§4の6対象それぞれに1行=1項目で「確認方法/証拠(ファイル:行・commit・test名・runtime記録)/判定(確認済み/未確認/不要[理由])」を付ける。要点:
- ②(旧条件削除): 旧条件がコード・Prompt・Validator・後続経路から参照されていないことを**Grep証拠**で示す(下記Grep一覧)。「正式初回Production経路で有効」=LR発火条件の実装箇所(`er020_tts_retry_local_rewrite_01.py`の発火判定関数:行)にslot3 NG・5 role・7 Gate以外の条件(合意・閾値・flag)が無いことを関数:行で示す。flag非依存=`er020`/`er003_v1_n3_01_tts_generate.py`/`er063_family_z_audio_01.py`に環境変数・起動flagでLR有効/無効を切替える箇所があるか(あれば既定値と、Production runnerが何を渡すか)。retry/fallback/regeneration/resume整合=委任_02/_03の`ITEMS23_...md` §1-b/§3/§8を参照し、未確認項目を残さない。runtime evidence=run_e2e_04での実際のLR発火記録(Std part3_c1はLR→`He drank`に至った=live発火の実例か? `er026_output/.../run_e2e_04/a2/audit/`配下のLR記録・`attempt_history`・`tts_generation_results.json`で確認し、「②削除前のコードでの発火」か「削除後」かを時系列(commit 4413a532b の時刻 vs run時刻 11:31-12:15 JST 2026-10-19)で判定する)。テスト=`er020_lr_post_rewrite_expected_text_fzaq2_test_01.py`(18)、`er020_lr_post_rewrite_m1_anchor_fzaq3_test_01.py`(11)、§10-1全体suite結果を引用(再実行不要。ただしHEADが当時のcommit以降にer020/er003系を変更していないか`git log --oneline -5 -- er020_tts_retry_local_rewrite_01.py er003_v1_n3_01_tts_generate.py er003_v1_crosslevel_audio_02_common.py`で確認し、変更があれば該当2 testのみ再実行)。SSOT一致=CURRENT_SPEC L2818・OPEN-422・OPEN-283・DECISION_LOG該当エントリの記述と実装の一致点/不一致点を列挙(不一致があれば委任_07の修正対象として記す)。
- ③(書換え後原稿を正解に): 単一参照点`resolve_expected_text_after_local_rewrite`(`er020:784`付近)の呼出元を**全列挙**(`Grep -n resolve_expected_text_after_local_rewrite` 全.py)し、§4の6対象(初回経路Rewrite後TTS/減速後再検証/retry・fallback/regeneration・resume/再利用・継承/X・Z共通)それぞれにどの呼出元が対応するか表にする。対応する呼出元が無い対象は「未配線」と明記。`ITEM3_FORMAL_PATH_VERIFY_01.json`(NORMALIZED_MATCH)が何を検証したか(入力=run_e2e_04のLR後音声?)を1行で。live Rewrite自然発火=run_e2e_04で実際に発火した記録があるならそれが「③修正前の発火」である点を明記し、③修正後のlive発火evidenceは**今回の全TTS再生成(委任_07)で自然に取得できる見込み(LRが発火すれば)/発火しなければ未観測のまま**と整理する(追加の有料検証は提案しない)。
- 結論欄: ②③それぞれ「Fableが PRODUCTION_WIRED と判定するために不足している証拠」を箇条書き(無ければ「無し」)。

成果物B: `docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/REGEN_PLAN_01.md`(新規)。
- B-1 録音2 Lock解除の正規手順: `er011_human_review_lock_01.py`の状態遷移(HUMAN_APPROVED=`record_human_approval`[`er003_v1_n3_01_assemble.py:96`付近] / REGENERATE_APPROVED=`approve_regenerate` L474)を読み、ユーザー決定「録音2をHuman Review承認として扱う」に対応する正規API呼出(関数・引数・承認者文字列・承認キー=元原稿`Melos drank`を含む文、出力先)を特定する。実行はしない。Lock解除がrun_e2e_04(既存run)のStd part3_c1だけに効く点と、新run(下記B-2)には別のLock stateファイルが生成される点を確認し、「録音2承認の記録」と「全再生成」の関係(録音2は#116の正式クローズ記録として承認し、新runでは新音声を独立にGate判定)を整理する。
- B-2 再生成方式: 既存runner(`--run run_e2e_04 --mode real --stage all --approved-budget-jpy 80 --tts-execution-mode STANDARD --regenerate-stage support_a2`の形式を使ったscript。`Grep -l "approved-budget-jpy" *.py`で特定)で、(i)新run `run_e2e_05`を`copy_reusable_run_assets`で作る場合に**writer/std_adjust/plan/support/kpは再利用、tts_b1b・tts_a2は全clip再生成**とする具体的な引数(`--regenerate-stage`の値、reuse無効化の方法、master audio store再利用(`er006_output/master_audio_store_01`)が同一文面を再利用してしまわないか=T-2(2)の確認と無効化手段)、(ii)Advanced part3_c1が「He drank」(LR後原稿)で保存されている箇所(`run_e2e_04/b1b/...`または`a2`)と、新runで元原稿「Melos drank」から生成される根拠(原稿ソース=writer成果物の元文か、LR記録が継承されないか=`audio_text_deviation`/`local_rewrite_recovery`が新runへcopyされないことをDENY listで確認)、(iii)STOPセンチネル(run_e2e_04へ`STOP`設置の要否、26節)、(iv)費用見積(run_e2e_04実測: tts_b1b 26.24+tts_a2 19.59=JPY45.8[TTS gemini 22.58/ASR azure 18.48/openai 4.18]を根拠に、Std+Adv全clip+想定retry/LR込みで上限を算出。出典=`run_e2e_04/audit/cost_by_stage_04.json`)、(v)実行コマンド全文(絶対パス・実引数・`TTS_EXECUTION_MODE=STANDARD`)、(vi)完了条件(gate/assemble/pages/page_verify、試聴ページ=`user_test/family_z_melos_02/`更新、Pages 200確認)、(vii)記録項目(発動した判定経路・警告・LR発火・HR対象・`post_slowdown_expected_text_source`の観測)。
- B-3 ①との依存: 委任_05が「範囲内修正あり」の場合、修正後に再生成する順序とRegression確認の挿入位置を1行で。

## 事前指定Read一覧
- `docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEMS23_REWRITE_CONDITION_AND_SCRIPT_REF_01.md`: Grep `^## |^### `→§1-b/§2/§3/§5/§7/§8/§10の範囲Read
- `docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEM3_FORMAL_PATH_VERIFY_01.json`: 先頭80行
- `docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/OPUS_REVIEW_H_01_VERBATIM.md`: Grep `条件[1-6]|必須修正`→該当範囲
- `docs/research/FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01/PHASE3_RUN_E2E_04_RECORD_01.md`:1-30
- `docs/research/FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01/HR_LOCK_PART3C1_ROOT_CAUSE_01.md`: Grep `^## `→LR発火・減速後照合の節
- `CURRENT_SPEC.md`: 2818(1行のみ。全文Read禁止)
- `er020_tts_retry_local_rewrite_01.py`: Grep `def .*local_rewrite|def resolve_expected_text_after_local_rewrite|lr_used|slot|consensus|agree|both_engines|両`→該当範囲Read
- `er003_v1_n3_01_tts_generate.py`:190-230(減速後再検証)、Grep `finalize_a2_slowdown_final_ng|post_slowdown_expected_text_source`
- `er003_v1_crosslevel_audio_02_common.py`:250-310, 405-425
- `er063_family_z_audio_01.py`: Grep `local_rewrite|LR_|audio_text_deviation|_retts`→該当範囲
- `er011_human_review_lock_01.py`:1-60, 100-120, 150-160, 175-200, 310-345, 470-520
- `er003_v1_n3_01_assemble.py`:80-130(record_human_approval)
- `er019_family_x_validation_inheritance_01.py`:240-260
- `docs/pm/RESULT_PACKET_FZQI7.md`:1-25(run_e2e_04の起動引数・copy方式)
- `docs/research/FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01/run_e2e_04_copy_plan_07.json`(存在すれば先頭100行; 無ければ`er026_output/.../run_e2e_04/`直下の同名json)
- `er026_output/family_z_production_e2e_01/melos/run_e2e_04/audit/cost_by_stage_04.json`

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep(旧条件残存確認、`-n`): `両ASR|両エンジン|合意誤読|consensus_misread|both_asr_agree|same_position_agree|agree_same` in `*.py`・`prompts/**`・`docs/pm/templates/**`・`CURRENT_SPEC.md`(CURRENT_SPECは歴史注記[削除済みと明記された文]と現行条件文を区別)→成果物A ②の「旧条件非参照」行へ件数・該当行を記す。
- Grep `resolve_expected_text_after_local_rewrite` in `*.py`(`-n`)→③の呼出元全列挙表。
- Grep `LOCAL_REWRITE_ENABLED|LR_ENABLED|local_rewrite_enabled|enable_local_rewrite` in `*.py`・`.env.example`・`er026_*.py`→flag依存の有無。
- Grep `approved-budget-jpy|regenerate-stage|copy_reusable_run_assets` in `*.py`→runner特定と引数仕様。
- Grep `reuse|master_audio_store|MASTER_AUDIO` in 上記runnerと`er063_family_z_audio_01.py`→再利用無効化手段。
- Grep `local_rewrite|LR_REWRITTEN|audio_text_after|He drank` in `er026_output/family_z_production_e2e_01/melos/run_e2e_04/a2/audit/*.json`と`.../b1b/audit/*.json`→LR発火記録・He drank保存箇所・時刻。
- `docs/pm/ACTIVE_TASK.md`先頭に本委任ヘッダ4行(管理ID/Status/禁止維持/報告=RESULT_PACKET_FZAQ6.md)を追記。

## 実行コマンド全文
- T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_06.md --json-out docs\pm\delegation_log\2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_06.md_check.json`(本メッセージ全文を同パスへ先に保存)
- commit時刻確認: `git log -1 --format=%cI 4413a532b` および `git log --oneline -5 -- er020_tts_retry_local_rewrite_01.py er003_v1_n3_01_tts_generate.py er003_v1_crosslevel_audio_02_common.py`
- 条件付き再実行(上記で変更があった場合のみ): `.venv\Scripts\python.exe -m pytest er020_lr_post_rewrite_expected_text_fzaq2_test_01.py er020_lr_post_rewrite_m1_anchor_fzaq3_test_01.py -q`
- Lock sha不変確認(作業前後): `powershell -Command "Get-FileHash -Algorithm SHA256 er026_output\family_z_production_e2e_01\melos\run_e2e_04\a2\audit\review_lock_state.json | Select-Object -ExpandProperty Hash"`
- secret scan: `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`
- Git: `git status --porcelain` → `git add docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEMS23_WIRING_ASSURANCE_01.md docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/REGEN_PLAN_01.md docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_06.md docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_06.md_check.json` → commit → push(直近commit e3995f51a と同じ手順、`git log --oneline -3 origin/main`で到達確認、force/rebase禁止)

## SSOT追記文
編集権無し。RESULT_PACKETに「OPEN-422への配線証拠要約1行案」「OPEN-371(3NGにSecondary障害を含まない、未実装)の現状1行案」を記す。

## Git(明示add対象・コミットメッセージ・trailer)
- add対象: 上記4ファイルのみ。
- commit: `FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_06: ②③Production配線保証チェックリスト(ユーザー§3/§4項目別証拠)+録音2 Lock解除正規手順+Std/Adv全TTS再生成計画(JPY0)`
- trailer: `Delegation: FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/委任_06`

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_FZAQ6.md`(新規): (1)T-0結果 (2)②チェックリスト7項目の判定一覧(確認済み/未確認/不要) (3)③6対象の判定一覧+呼出元表 (4)旧条件Grep結果(件数) (5)run_e2e_04のLR発火が②③修正前/後どちらのコードか(時刻根拠) (6)Fableが PRODUCTION_WIRED判定するのに不足する証拠 (7)Lock解除の正規API・引数(実行していないことを明記) (8)再生成計画の要点: 方式/再利用無効化/Advanced原稿がMelosに戻る根拠/費用見積と出典/実行コマンド全文/完了条件 (9)委任_05結果との依存 (10)費用JPY0・Lock sha前後 (11)Git (12)判断候補(あれば。ラベルは付けない) (13)一覧外Read理由。