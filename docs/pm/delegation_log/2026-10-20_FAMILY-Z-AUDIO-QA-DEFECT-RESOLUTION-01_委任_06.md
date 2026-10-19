# 委任文(Fable→sonnet-worker) 保存コピー(T-0、2026-10-20)

## 管理ID
FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_06(②Rewrite発動条件「両ASR合意」削除・③Rewrite後原稿照合のProduction配線保証チェックリスト[ユーザー2026-10-20 §3・§4の確認項目に1対1で証拠を付ける]+録音2 Lock解除の正規手順特定+Std/Adv全TTS再生成の実行計画[有料実行はしない]、JPY0)。2026-10-20。
並行タスク衝突確認: 同時に委任_05(①Melos/Mellows再照合。書込先=ITEM1_ROOT_CAUSE_02_SPEC_RECONCILIATION_01.md・docs/pm/RESULT_PACKET_FZAQ5.md・docs/pm/delegation_log/2026-10-20_*、M1/validation系コード)が走る。本委任はそれらを編集しない(読取可)。本委任はコード・Prompt・Lock・SSOTを編集しない(読取と文書作成のみ)。SSOT編集権=無し。docs/pm/ACTIVE_TASK.mdは先頭へ自委任ヘッダ4行を追記するのみ。commit前にgit status --porcelainで.git/index.lock不在を確認し、自分のファイルのみ明示git addする。ユーザー指示原文(T-0)は委任_05が保存(docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_ROOT-CAUSE-WIRING-CLOSEOUT_USER.md)。

## 性質/到達上限Status/禁止事項
- 性質: 配線証拠の整理(read-only)+実行計画作成。Production変更なし、有料API 0。
- 到達上限Status: ITEMS23_WIRING_EVIDENCE_COMPILED_REGEN_PLAN_READY_PENDING_FABLE。PRODUCTION_WIREDの判定はFable(証拠が不足する項目は「未確認」と明記)。
- 禁止: 新規TTS/ASR/LLM呼出(JPY0厳守)/HR Lock・run_e2e_04/a2/audit/review_lock_state.json(sha256 6720ce80b7eedba9789dc190a431b030e20486b298a451479129e4d017fb3e19)の変更(解除手順の特定のみ、実行は委任_07)/コード・Prompt変更/git add -A/-u/-f・amend・rebase・force push・stash・clean・reset --hard・checkout -f/有料runの起動・再起動(26節)。
- 修正範囲の線引き(11-8): 本委任は修正を行わない。配線不備を発見した場合は、範囲内/範囲外を分類してRESULT_PACKETに記す(修正は委任_07でFableが指示)。
- Opus独立技術レビューGate(11-3): 非該当。②③の実装はOpus_H(GO_WITH_CHANGES、必須修正6条件充足済み)でレビュー済み。
- 費用/日次: JPY0。時間見込み: 1.5〜2.5h。並列化: 委任_05と並列。直列化理由: 再生成の実行は①結果のFable照合後(ユーザー§5)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾の是正とそのRegression・検証。
G-1: git出力は--porcelain/--stat/--short等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0: 受領した委任文をdocs/pm/delegation_log/<管理ID>.mdへ保存し、check_delegation_prompt.pyを実行、結果をRESULT_PACKETへ1行記録する。
T-2: TTSを伴う委任は正式リリース前である限りTTS_EXECUTION_MODE=STANDARDを明示。7-5: 実行前に(1)差分再生成可否 (2)音声再利用キャッシュ有無 (3)--budget明示 (4)想定外の全再生成ならAPI前にSTOP。本委任はTTSを実行しないが再生成計画でこの4点を計画として満たす。今回はユーザー指示による意図的な全再生成((4)の「想定外」に非該当)。
T-3: 本委任は費用上限を伴わない(JPY0)。再生成計画に記す上限は次の定型文: 「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」

## ユーザー指示(原文抜粋。全文は委任_05保存ファイル)
3. Rewrite発動条件の修正、およびRewrite後の原稿照合修正は、正式Productionで確実に有効になっていることを確認する。
4. 録音2のHuman Review Lock解除は承認済み。
5. ①の問題解決後、Family Zの該当記事についてAdvancedを含む全TTSを再生成する。Advancedの「He drank」は元の「Melos」を含む原稿に戻す。
§3 ②: 「両ASRが同じ箇所の誤読に合意すること」条件を削除(正式承認済み)。基本フロー=TTS初回→承認済みPrimary/Secondary検証→NGなら最大2回のTTS再生成→なおNGなら既存のRewrite条件・Gateに従ってRewrite。確認項目: 正式初回Production経路で新仕様が有効/DEV・Trial専用経路や手動フラグONに依存しない/retry・fallback・regeneration・resumeでも整合/旧条件がコード・Prompt・Validator・後続経路から参照されていない/実行時の有効設定・判定経路・モデルrouting等の証拠/必須Regression・integration testがPASS/CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・Gitが実装内容と一致。コード変更済み・テストPASSだけでPRODUCTION_WIREDにしない。
§4 ③: 正式に許可されたRewrite後は書換え後の実送信文を後続音声検査の正解原稿とする。対象: 正式初回経路からのRewrite後TTS/減速後再検証/retry・fallback・regeneration・resume/再利用・継承/Family X・Z対象共通経路。live Rewrite自然発火は未観測。必要なruntime evidenceの充足状況を整理し、追加確認が必要なら最小限で。不必要な有料TTSを繰り返さない。証拠なしにPRODUCTION_WIREDと判定しない。
§5: 録音2のLock解除は承認済み。①解決後、Standard/Advancedの全TTSを正式Production経路で再生成。Advancedの「He drank」は元の「Melos」を含む原稿へ戻す。必須の音声QA・再試行・Rewrite・減速後再検証・Assembly Gateを通す。完成音声と試聴ページを更新。発動した判定経路・警告・HR対象を記録。録音2を新たな判断待ちとして再提示しない。

## 本委任の作業(要旨)
成果物A: docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/ITEMS23_WIRING_ASSURANCE_01.md(§3の7項目・§4の6対象それぞれに確認方法/証拠/判定[確認済み/未確認/不要]。旧条件Grep、flag依存、LR発火時刻判定[commit 4413a532bとrun時刻]、test引用、SSOT一致、③呼出元全列挙表、ITEM3_FORMAL_PATH_VERIFYの内容、結論欄=PRODUCTION_WIRED判定に不足する証拠)。
成果物B: docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/REGEN_PLAN_01.md(B-1 録音2 Lock解除の正規手順特定[実行しない]/B-2 再生成方式[新run run_e2e_05、再利用無効化、Advanced原稿がMelosに戻る根拠、STOPセンチネル、費用見積、実行コマンド全文、完了条件、記録項目]/B-3 ①との依存)。
SSOT追記文: 編集権無し。RESULT_PACKETにOPEN-422への配線証拠要約1行案・OPEN-371現状1行案を記す。

## Git/報告
add対象: ITEMS23_WIRING_ASSURANCE_01.md, REGEN_PLAN_01.md, 本ファイルと_check.json。commit: FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_06: ②③Production配線保証チェックリスト(ユーザー§3/§4項目別証拠)+録音2 Lock解除正規手順+Std/Adv全TTS再生成計画(JPY0) / trailer: Delegation: FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/委任_06
報告: docs/pm/RESULT_PACKET_FZAQ6.md(13項目)。

## 事前指定Read一覧
- ITEMS23_REWRITE_CONDITION_AND_SCRIPT_REF_01.md(Grep見出し→§1-b/§2/§3/§5/§7/§8/§10) / ITEM3_FORMAL_PATH_VERIFY_01.json 先頭80行 / OPUS_REVIEW_H_01_VERBATIM.md(Grep 条件[1-6]|必須修正) / PHASE3_RUN_E2E_04_RECORD_01.md 1-30 / HR_LOCK_PART3C1_ROOT_CAUSE_01.md(Grep見出し) / CURRENT_SPEC.md 2818のみ / er020_tts_retry_local_rewrite_01.py(Grep→範囲) / er003_v1_n3_01_tts_generate.py 190-230 / er003_v1_crosslevel_audio_02_common.py 250-310,405-425 / er063_family_z_audio_01.py(Grep→範囲) / er011_human_review_lock_01.py 部分 / er003_v1_n3_01_assemble.py 80-130 / er019_family_x_validation_inheritance_01.py 240-260 / RESULT_PACKET_FZQI7.md 1-25 / run_e2e_04_copy_plan_07.json / cost_by_stage_04.json

## 事前指定Grep一覧+追記位置・更新位置の手順
- 旧条件残存(両ASR|両エンジン|合意誤読|consensus_misread|both_asr_agree|same_position_agree|agree_same)を*.py・prompts・docs/pm/templates・CURRENT_SPECで→成果物A②「旧条件非参照」行
- resolve_expected_text_after_local_rewrite全列挙→③呼出元表
- LOCAL_REWRITE_ENABLED|LR_ENABLED|local_rewrite_enabled|enable_local_rewrite→flag依存有無
- approved-budget-jpy|regenerate-stage|copy_reusable_run_assets→runner特定
- reuse|master_audio_store|MASTER_AUDIO→再利用無効化手段
- run_e2e_04 a2/b1b audit内 local_rewrite|He drank→LR発火記録
- docs/pm/ACTIVE_TASK.md先頭に本委任ヘッダ4行を追記

## 実行コマンド全文
- T-0: .venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_06.md --json-out docs\pm\delegation_log\2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_委任_06.md_check.json
- git log -1 --format=%cI 4413a532b / git log --oneline -5 -- er020_tts_retry_local_rewrite_01.py er003_v1_n3_01_tts_generate.py er003_v1_crosslevel_audio_02_common.py
- 条件付き再実行(上記で変更があった場合のみ): `.venv\Scripts\python.exe -m pytest er020_lr_post_rewrite_expected_text_fzaq2_test_01.py er020_lr_post_rewrite_m1_anchor_fzaq3_test_01.py -q`
- Lock sha不変確認(作業前後): `powershell -Command "Get-FileHash -Algorithm SHA256 er026_outputamily_z_production_e2e_01\melosun_e2e_042uditeview_lock_state.json | Select-Object -ExpandProperty Hash"`
un_e2e_042udit
eview_lock_state.json | Select-Object -ExpandProperty Hash"`
- secret scan: .venv\Scripts\python.exe tools\secret_scan_01.py --staged
- Git: git status --porcelain → 明示git add(4ファイル) → commit → push(force/rebase禁止)
(注: 本ファイルは受領文の要旨保存コピー。原文の全文はFableの委任メッセージ)
