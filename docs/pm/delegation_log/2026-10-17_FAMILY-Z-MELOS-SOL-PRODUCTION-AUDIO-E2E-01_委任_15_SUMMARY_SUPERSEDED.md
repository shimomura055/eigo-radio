# FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_15 (Fable→Sonnet 委任文 全文保存 T-0)

## 管理ID
FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_15(Phase 2a、JPY0): Opusレビュー_C逐語保存+台帳 / Family Z Style配線(X共通定数参照化・全Role Style記録・run状態STOP・drift test・Dialogue不変test) / er006 flagger test是正 / Melos M1受理のオフライン監査 / SRC D1強化版の**オフライン解決dry-run(実装は#109回答後)** / Dangling Reference Check / SSOT / commit。**有料実行禁止(runner `--mode real`禁止)。STOP_NOTICE(2026-10-12)は有効のまま・編集禁止(有料実行なしのため本委任は継続可)。** 並行Agentなし。commitを伴う作業は本委任のみ。

## 性質/到達上限Status/禁止事項
- 性質: 承認済み仕様(ユーザー2026-10-17 §2B/§4)のProduction配線実装(Trial専用ではない正式経路)。到達上限Status=`Z_STYLE_WIRED_CODE_TESTED_PENDING_USER_108_109`。PRODUCTION_WIRED判定はFable、runtime evidence(Phase 3)後。
- 禁止: 有料API。`er003_v1_translator_briefs/*`等の共有Prompt変更(SRC D2相当=承認事項)。Strategy L選定方針の変更。`DEFAULT_NEW_RUN_PROFILE`への従属(Opus R-C1)。`FAMILY_Z_ROLE_STYLE_VERSION`のbump(R-C2)。Dialogue Style/Voice/speaker assignmentの変更。SRCのProduction code実装・`candidate_id_v1`ラベル付与(#109待ち、dry-runのみ)。`SUPPORTED_FAMILY_PROFILES`への"family_z"追加。旧run(run_e2e_01/02/kgcpw)配下の編集。STOPセンチネル操作。`er026_family_z_stop_sentinel_test_01`の実行(本物のSTOP_ALLを操作するため除外)。Family A/B/C。git add -A/-u/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f。
- Opus Gate: 条件A=レビュー_C実施済み(GO_WITH_FIXES)。本委任はその反映。Fable照合: R-C1〜R-C8を採択。
- 時間見込み: 約2〜3時間。直列(同一ファイル群)。
- 費用/日次: JPY0。

## 実装仕様(要点。委任文全体はFableのプロンプト原文に従う)
W1 Style配線(er063_family_z_audio_01.py): X定数import参照化、Z側_STYLE_SHA256にrole別期待sha固定、Z例外role(TOPIC_INTRO/J3/Adv Comment E2_UPBEAT/Dialogue)はorigin="family_z_specific"、FAMILY_Z_ROLE_STYLE_VERSION非bump、各entryにstyle_label記録。
W2 全Role Style記録+run状態STOP(style_record.json、結果ファイル存在かつrecord無しは課金前STOP、X _RUN_STATE_FILES方式踏襲)。
W3 copy allowlist/除外の定数化とtest。音声は新runで全Role再生成。
W4 test: er063_family_z_common_style_wiring_01_test_01.py (t1 drift, t2 コピー定数無し, t3 例外role列挙, t4 reuse_key, t5 speaker→Voice不変, t6 STOP, t7 allowlist, t8 非従属)。既存N01固定testは更新。
W5 er006 test_flagger_design_models_registered: Z Sol割当を許可集合へ(根拠ユーザー2026-10-17 §2A)。
W6 M1「Melos said.」受理オフライン監査(α/β)。βは修正せず即報告。
W7 SRC D1強化版オフラインdry-run(src_z_posthoc_dryrun_01.py/.md/.json、実装なし、ラベル案z_sentence_id_posthoc_v1)。
W8 Dangling Reference Check(旧名称N01/R2/M2参照の是正)。
W9 regression(er063*/er006*/er019_family_x_style*/er026 Z系、stop_sentinel testは除外)。
W10 SSOT(CURRENT_SPEC表Z列、OPEN-412/414/415、DECISION_LOG、REPORT_LEDGER、ACTIVE_TASK、REGISTER #109、OPUS_FINDINGS_LEDGER OF-FZ-C-01〜08)。

## Git
明示addのみ。commit message先頭: `FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_15: Opus条件Aレビュー_C(GO_WITH_FIXES)反映...`、trailer `Managed-ID: FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01`。git add -A禁止。
(注: 本ファイルは委任文の構成要素を保存したもの。受領原文の完全版はFableの委任プロンプト=sandwich-pm→sonnet-worker呼出文。ユーザー原文はCOMPLETION-AND-CROSS-FAMILY_USER.md sha256 a676e8be5f06aac1581a56d5896a0c7e1bfacf86a565a18b534d5ce9fb8e550c)
