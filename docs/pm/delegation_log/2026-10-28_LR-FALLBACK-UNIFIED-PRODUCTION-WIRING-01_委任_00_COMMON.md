# 委任_00 共通事項(LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01、Fable→sonnet-worker、2026-10-28)

## 管理ID・目的
LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01。ユーザー正式決定(`APPROVED_FOR_PRODUCTION`)=UD-1(LR後の英文を最終表示本文にも反映)・UD-2(AI島 AIs→AI agents/AI systems)・UD-3(M3/Style Gate: 承認済みStyle照合維持、正常なFallback/LR発動のみを理由とする組立停止・HR要求は解除、異常は従来どおり停止)・最終Human報告用資料の表示仕様(LR=赤、Fallback=濃い青、注記は最終確認資料のみ)。到達目標=全Family・全Level・全RoleでPRODUCTION_WIRED。**ユーザー原文(必読・全文)**=`docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_USER.md`。

## Phase A(本委任群)=設計・調査のみ(API 0、Productionコード・SSOT編集禁止)
Phase Aの成果物をFableが統合し、Opus条件A(新構造・処理フロー)レビューを経てから実装(Phase B)へ進む。Phase Aでは**コードを変更しない**(test・scriptの新規作成も不可。読み取りとdocs作成のみ)。SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/USER_DECISION_REGISTER_01.md`)は編集しない・全文読込禁止(Grep+該当行)。

## 前提資料(所在)
- 直前の横断監査(OPEN-565): `docs/research/LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01/{W1_LR_DATAFLOW_01,W2_SIX_ROUTES_01,W3_M3_LR_HR_01,W4_ROLE_COVERAGE_01,FIX_A_01,FIX_A_02}.md`。原文=`…/2026-10-27_LR-FALLBACK-M3-CROSS-FAMILY-AUDIT-01_USER.md`。是正commit 7dab92aba・8fbfae04c。
- 統一TTS仕様(X/Y/Z): `CURRENT_SPEC.md`「TTS Retry/Fallback/Local Rewrite 統一仕様」節(約:3148-3220、Grepで特定)。**49経路対応表**=`docs/research/TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01/ROW_MAPPING_01.md` §2(49行・9 policy)、同`DESIGN_01/02.md`、`SPEC_LEDGER_01.md`、Opusレビュー`OPUS_REVIEW_01.md`。policy実装=`er127_tts_block_policy_01.py`(`PROFILES`、`BlockProgress`)。
- LR実装: `er020_tts_retry_local_rewrite_01.py`(`run_local_rewrite_recovery`、`resolve_expected_text_after_local_rewrite`、`HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG`)。LR決定(2026-09-26 `RESOLVED_BY_LOCAL_REWRITE` CURRENT_SPEC:~2214、2026-10-19 書換え後文=ASR正解・HR Lock keyは原文・`LR_REWRITTEN`警告 CURRENT_SPEC:~2925)。
- Gate: X M3=`er019_family_x_style_profile_01.py`(`_approved` ~L629、`m3_assembly_gate` ~L685-760、`LOCAL_REWRITE_RECOVERY` ~L742、`STD_FALLBACK_USED_OR_UNKNOWN` ~L716)。Y=`er121_family_y_audio_01.py:~929`。Z=`er063_family_z_audio_01.py`(LR Gateなし、ページ注記のみ ~L2464)。HR Lock/HR採用=`er121_e1_hr_adopt_r0_01.py`、X `record_human_approval`。
- 確定内容保護: `er128_kp_confirmed_content_01.py`(G0-G4、`confirmed_selection.json` text_sha256)、V3フォーム照合コード(`er128_form_readable_restore_01.py`)。
- 既公開不一致4件: X「英単語ガチャ」Adv(you've→you have、UDR #183(a)承認、OPEN-499)/Z「走れメロス」Adv(Melos→He、注記あり)/Z「猿の手」Std(guest→visitor、注記あり)/X「AI島」Std・Adv(AIs→音声は AI agents / AI systems、OPEN-561/563、hr_02)。所在はW4_ROLE_COVERAGE_01.md・W1_LR_DATAFLOW_01.md参照。
- 既存の人間確認資料(候補): X HR試聴ページ(`user_test/<article>_hr_*`、`hr_02`等)、Y HR試聴節(`user_test/family_y_production_redelivery_fee_03`)、Z `review_request.md`/試聴ページ(`er026`→`user_test/family_z_*`)、`user_test/human_review.html`、各`pass_with_warning_listening_list.json`。
- 『告げ口心臓』完成版(2026-10-28、LR 0・Fallback 0)=`er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01`、ページ`user_test/family_z_tell_tale_heart_reselect_01/`。

## 共通ルール
- Python=`.venv\Scripts\python.exe`(読み取り・集計のみ。有料API禁止)。
- 用語: 「表示本文」=学習者向け公開ページの英文。「TTS入力」=読み上げ原稿。「ASR正解原稿」=判定の期待文。「最終Human報告用資料」=TTS/ASR/組立完了後のユーザー最終確認資料(新設または既存資料の拡張。学習者向けページとは別)。
- 判断候補はA(既存仕様内で自己解決)/B(Fable判断)/C(軽微・実害なし)/D(ユーザー判断要)で区分。ユーザー原文で既に決定済みの事項(UD-1/2/3・色表示仕様・試行回数不変など)は再質問しない。
- 成果物=`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/<委任名>.md`。Git: 自分の成果物のみ`git add`(`git add -A`禁止)、commit message冒頭に管理IDと委任番号、末尾`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`、`git push origin HEAD:main`。他案件の未コミット差分(`export_form_data_01.py`、`THEME_DATA_02.json`、`review_queue/`等)は含めない。
- 最終応答=成果物パス+要約10行以内+判断候補(区分付き)。
