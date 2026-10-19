# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_06(②Standard Preview/Comment=Advanced方式の日本語適用(P-A、Opus_E F3-1〜F3-3・R-E4 L-1反映)のProduction実装+test、付帯=既存test FAIL 3件の是正(kp_expl sig期待値2件・er078 06c 実HTTP mock化)。**JPY0、有料実行なし**)。日付: 2026-10-19(JST)。

## 性質・到達上限Status・禁止事項
- 性質: 承認済み仕様②(ユーザー2026-10-19 APPROVED_FOR_PRODUCTION)の正式Production配線(Z writer/runner)+test是正。
- 到達上限Status: `ITEM2_CODE_WIRED_TESTED_PENDING_PHASE3`。PRODUCTION_WIREDはFable判定(Phase 3後)。
- 禁止: 新しいPrompt文(役割文)の創作(P-B不可。既存`a2gen.COMMENT_1_ROLE/COMMENT_2_ROLE/PREVIEW_ROLE`を無改変流用)/Advanced側の経路・Prompt・shaの変更/新Gate・新STOP経路の創設(重複・先取りはWARN記録のみ)/lint関数の既定挙動変更(Z Std呼出側から明示的にWARN化。NEWS/IOL/Point/構造ラベル/ネタバレ/禁止名/言語のblockingは維持)/有料実行/メロス成果物(run_e2e_03)の書換え/①③④のコード再変更(必要なら理由を報告)。
- 固定ブロック: **E-1**(ITEMS234_DESIGN_01 §2(P-A・sha/prior対策・WARN)、OPUS_REVIEW_E R-E3/R-E4、2026-10-13ユーザー判断(Z Std PreviewはX Std `PREVIEW_ROLE`基準)、2026-10-17決定A(Preview・Comment1現行維持)=本件で上書き、OPEN-338・er076 Trial B'記録)/**D-1**(不適用=承認済み仕様。`STD_SUPPORT_METHOD_VERSION`はflagではなく方式版の識別子)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。並行agentなし。SSOTは自分の変更行のみstaged blob)/**F-1**(JPY0)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_06.md`へ保存し`check_delegation_prompt.py --file <path> --json-out <path>_check.json`実行。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI6.md`、ACTIVE_TASK.md先頭へ自分のブロックのみEdit追記)。

## Fable決定(Opus_E採用。記録用)
- ②方式=P-A: `run_support_std`を`run_support_adv`と同形に(入力構成=本文全文+Comment1・2、生成順序Adv同一、役割文=`a2gen.COMMENT_1_ROLE/COMMENT_2_ROLE/PREVIEW_ROLE`無改変、Std固有=`SUPPORT_JA_PRINCIPLE`(平易さ)と日本語出力)。旧`scene_transition`文は入力から外れる(Advにも無い)=test固定(F3-3)。fam_c経路は呼ばない。
- resume/regenerate対策: `STD_SUPPORT_METHOD_VERSION`(例 `"adv_method_ja_v1"`)をStd側のstage入力shaに混ぜ、`prior`再利用はmethod一致時のみ。sha計算(`er026:1139`・`er062:1278`)は共通ヘルパ化。Adv shaは不変。他storyの旧方式runはresume時にSTOP→明示regenerate要求(意図どおりとして記録)。
- WARN記録(Gate化しない): 日本語4-gram重複は固有名(カタカナ固有名・「メロス」等)と頻出語を除外し参考値と明記。結末語は既存`spoiler_ja`辞書+カタカナ固有名に限定(英日跨ぎのPart3固有語checkは削除=F3-1)。`support.json`に`method`・`overlap_notes`を記録。
- lint(R-E4)=L-1: Z Std JAの`LISTEN_INSTRUCTION`のみblocking→WARN(`support.json`へ記録)。関数の既定は変えず、Z Stdの呼出側から明示(例: `allow_listen_instruction_as_warn=True`)。他のblockingは維持。`fam_c`禁止語句はP-Aでfam_c経路を呼ばないため非該当であることを確認。
- F3-2: Phase 3出力のComment1注目点と本文の整合はFableが照合(本委任では仕組みのみ)。
- 2026-10-17決定A「Preview・Comment1現行維持・A/B新方式不採用」は本件②(ユーザー2026-10-19)で上書き。CURRENT_SPEC L1597/1600付近を更新し、DECISION_LOGに上書き関係を明記。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01\ITEMS234_DESIGN_01.md` §2・§7
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01\OPUS_REVIEW_E_01_VERBATIM.md` R-E3・R-E4
- `C:\Users\tensh\eigo-radio\er062_family_z_writer_01.py` L800-930(run_support_std/adv)・L1270-1290(sha)・`prior`機構
- `C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py` L440-500(旧Std Preview Prompt)・L1112-1145(stage_support)・L1135-1145(sha)
- `C:\Users\tensh\eigo-radio\er062_family_z_structure_01.py` L634-690(lint)
- `C:\Users\tensh\eigo-radio\er003_v1_iran01_a2_generate.py` L120-210(a2gen役割文)・`er003_v1_b1_scaffold_01_generate.py` L140-215
- 既存test: `er062_family_z_writer_01_test_01.py`(`test_std_comment3_receives_only_front_part_and_prior_reused`/`test_std_comment_facts_only_from_target_part`/`test_std_preview_has_no_listen_instruction`)、`er070`系trial test、`er026_family_z_e2e_integration_test_01.py`
- 付帯: `er003_test_kp_gloss_alignment_stop_paths.py`(T3 l-Z)、`er003_test_kp_gloss_alignment_wiring.py`(`ExplanationSignatureZ::test_status_less_keeps_display_only_signature`)、`er078_asr_unified_wiring_06c_test_01.py::test_d_en_last_slot_real_ng_still_goes_to_hr`(実HTTP発行箇所: `er006_pronunciation_research_01.research_pronunciations`→`requests.post`)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `er062_family_z_writer_01.py`: Grep `def run_support_std|def run_support_adv|scene_transition|fam_c|prior`→P-A実装、共通ヘルパ`support_stage_input_sha(level, …, method_version)`新設。
- `er026_family_z_fiction_production_runner_01.py`: Grep `_FAMILY_Z_PREVIEW_ROLE_JA|def stage_support|support_a2`→stage_supportでヘルパ使用、旧`_FAMILY_Z_PREVIEW_ROLE_JA`はSUPERSEDEDコメントのみ(Phase1互換・trial/test参照のため残置)。
- `er062_family_z_structure_01.py`: Grep `_LINT_LISTEN_JA|LISTEN_INSTRUCTION`→呼出側オプションでWARN化(既定不変)。
- `CURRENT_SPEC.md`: Grep `Preview・Comment1|Comment 1|現行方式維持|A/B新方式`(Family Z節 L1590-1615)→②仕様文へ更新(「Std Preview/Comment=Adv方式の日本語適用(a2gen役割文流用、SUPPORT_JA_PRINCIPLE維持)、method version=…、重複・先取りはWARN記録、Std JA lint LISTEN_INSTRUCTIONはWARN(Adv lintと同一思想)。2026-10-19ユーザー決定が2026-10-17決定Aを上書き。コード配線済み(commit)、runtime evidence待ち」)。
- `OPEN_ITEMS.md`: Grep `OPEN-419`→②進捗。Grep `OPEN-338`→「2026-10-19 ②で上書き(Adv方式日本語適用採用)」注記(CLOSED維持)。Grep `OPEN-414`→付帯test是正3件を追記。
- `DECISION_LOG.md`: 末尾に委任_06エントリ。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。

## 作業(順序)
A. T-0。B. ②実装(P-A、ヘルパ、prior、WARN記録、lint呼出側WARN化)。C. test: 更新3件(設計書記載)+er070系期待値更新+新規約10件(Adv同形の入力構成/生成順序/役割文がa2genと同一オブジェクト/scene_transition不在/fam_c不呼出/method versionがshaに影響しAdv shaは不変/prior method不一致で不使用/旧方式cache reuse→ProvenanceMismatchStop/LISTEN_INSTRUCTIONがWARN記録でraiseしない・他blocking維持/overlap_notes記録)。D. 付帯是正: kp_expl sig期待値2件をSRC D1 "src"追加に追従(期待値更新のみ、実装不変)/er078 06cの`requests.post`をmonkeypatchでmock(環境依存の実HTTP排除、課金経路ゼロ)。E. 回帰: er062 writer、er026 runner/integration、er062_structure、er003 gloss系(stop_paths/wiring/person)、er078 05/06c、er063系(PASS数)。F. SSOT→commit→push。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_06.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_06.md_check.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I -m pytest C:\Users\tensh\eigo-radio\er062_family_z_writer_01_test_01.py C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01_test.py C:\Users\tensh\eigo-radio\er026_family_z_e2e_integration_test_01.py C:\Users\tensh\eigo-radio\er003_test_kp_gloss_alignment_stop_paths.py C:\Users\tensh\eigo-radio\er003_test_kp_gloss_alignment_wiring.py C:\Users\tensh\eigo-radio\er003_test_kp_gloss_person_alignment.py C:\Users\tensh\eigo-radio\er078_asr_unified_wiring_05_test_01.py C:\Users\tensh\eigo-radio\er078_asr_unified_wiring_06c_test_01.py C:\Users\tensh\eigo-radio\er063_family_z_audio_01_test_01.py -q`(+er062_structure test・er070系の実在file名)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`(実在script名に置換)

## SSOT追記文(要点)
- CURRENT_SPEC(Family Z節): 上記②仕様文。
- DECISION_LOG: 「2026-10-19 FZQI 委任_06: ②P-A配線(a2gen役割文流用、method version sha、prior制限、WARN記録、Std JA lint LISTEN_INSTRUCTION WARN化=承認済み②の不可避な付随変更・Opus_E R-E4妥当)。2026-10-17決定Aを上書き。付帯test是正3件。JPY0。runtime evidenceはPhase 3」。

## Git(明示add対象・コミットメッセージ・trailer)
- commit: delegation_log 委任_06+_check.json、`er062_family_z_writer_01.py`、`er026_family_z_fiction_production_runner_01.py`、`er062_family_z_structure_01.py`、test更新/新規、付帯test 3件、ITEMS234_DESIGN_01.md(追記分)、CURRENT_SPEC.md、OPEN_ITEMS.md、DECISION_LOG.md、REPORT_LEDGER.md。msg: `FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_06: ②Std Preview/Comment=Adv方式の日本語適用(a2gen役割文流用・SUPPORT_JA_PRINCIPLE維持・method version sha・prior制限・重複/先取りWARN記録・Std JA lint LISTEN_INSTRUCTION WARN化)をProduction配線+test(JPY0)+既存test是正3件(kp_expl sig期待値・er078 06c実HTTP mock)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI6.md`)
4行: (1)整合(P-A=Adv方式の日本語適用の根拠、Opus F3-1〜F3-3/L-1の反映箇所:行、上書きした既存決定)(2)Production到達経路(初回/reuse/regenerate/resumeでの発火保証=sha・prior、lintの変更範囲、Adv不変の根拠)(3)成果物とcommit sha、test PASS数(付帯3件の是正結果含む)、旧Std方式との差分表(入力・役割・開示方針・平易さ)(4)撤去/残置(旧Std Preview Prompt・fam_c呼出・scene_transition)。`判定整合:`・`判断候補:`・T-0 check・自己チェック(新Prompt文創作なし/Adv不変/新Gateなし/有料0/run_e2e_03不変)。
