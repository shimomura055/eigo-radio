# 委任_05: AUW(ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01)— A2減速後判定の統一judge化・Dialogue・KP解説3回化・runner共有cache・is_last_slot配線
(sandwich-pm -> sonnet-worker 委任文。2026-10-15。branch feat/auw-unified-asr-01 HEAD 961d5b360)
禁止git操作: add -A/-f/stash/reset --hard/checkout -f/clean/rebase/amend/force push、mainへのpush/merge禁止(委任_07)。有料API 0(全testは通信遮断pytest plugin scratchpad\ng04方式+.venv/Scripts/python.exe)。

## T-0
委任文保存、check_delegation_prompt.py -> _check.json(FAILでも継続)。stop_scope_check rc=0。

## 事前指定参照
ユーザー原文_01.md L39-63基本フロー、L97優先規定、L143-153 Section固有例外(A2 6%減速・Dialogue・KP/日本語LR原則HR・見出し、新例外禁止)、L112-117 Regression基準、15必須受入条件(原文を開いて逐語引用)。
DESIGN_01 §4-3/§5(J7, Dialogue/er063, KP解説)/§6(C-H A2減速, C-I Dialogue, C-J KP)、DESIGN_02_ADDENDUM_01(OF-AUW-12 KP解説max_attempts=2->3, §4 SecondaryCache/begin_secondary_run(), §7 circuit breaker)、APPLICABILITY_MATRIX_01.csv。IMPLEMENTATION_03 §9/§10、IMPLEMENTATION_04(A2_PENDING_ENTRIES, attempt_ctx, if stop_retrying:到達不能分岐)。
対象: er003_v1_n3_01_tts_generate.py(apply_a2_slowdown_postprocess, _post_slowdown_cascade_rescue)、er026_post_slowdown_cascade_rescue_01.py、er063_family_z_audio_01.py、KP解説生成、runner群、er011_human_review_lock_01.py(無変更)。

## やること
A. A2減速後判定(J7): 直接classify_asr_match/transcribeを統一judge経由へ(減速6%・Prompt・Voice・速度不変。Primary->NGならSecondary1回、同一wav cache共有)。A2_PENDING_ENTRIESを空にし静的監査をdeferred 0・pending 0へ。asr_judgement_pre_slowdown退避維持。A2 rescue->registry hook結合test(減速後PASS_WITH_WARNINGが試聴リストに載る)。
B. Dialogue(er063/Family Z): 固有例外維持、EN(委任_03)・JA(委任_04)adapter到達を静的監査で確認、未到達leaf/hook配線。Prompt/閾値不変。
C. KP解説3回化(OF-AUW-12): max_attempts=2->3(これ以外の回数・閾値不変)。JA KPは原則HR維持。期待TTS呼出増分(最大+1/KP)をIMPLEMENTATION_05.mdに記載。
D. runner共有cache/circuit breaker: 各Production runner(X/Z/B/C, legacy n3)の実行開始点でbegin_secondary_run()導入。runnerごとの導入位置表。run内同一wav重複Secondary呼出0をtest固定。
E. is_last_slot/attempt_ctx配線: 各leaf(EN6+JA3)へattempt_ctx(slot/is_last_slot/script_version)。HR queue投入は最終slotのNGのみ。er011無変更、二重投入なし。到達不能if stop_retrying:分岐は削除せず記録のみ。
F. Family B/C hook: registry hook・ページ節をB/Cの生成完了点にも追加(write_listening_list_safe、0件節あり)。Family Cのget_or_run_asrは診断のみ。
G. test: 新規er078_asr_unified_wiring_05_test_01.py。既存97ファイル+er063/er013/B family testをper-file実行、baseline=patch_04/test_post_04.json、新規失敗0(α/β/γ区分、β期待値変更禁止)。
H. IMPLEMENTATION_05.md。commit/push(branch、明示add、secret_scan --staged hits=0)。message: ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_05: A2減速後判定の統一judge化+Dialogue到達確認+KP解説3回化(OF-AUW-12)+runner共有cache/circuit breaker+is_last_slot配線+B/C hook。main無変更、JPY0

## 禁止
Prompt/モデル/Voice/速度/閾値(KP回数以外)/HR Lock/予算guard変更、新Section例外、U1/U2定数変更、SSOT編集、main反映、有料API。設計判断が必要な競合・β矛盾・重大誤PASS・HR Lock経路変更が避けられない場合はSTOP報告。

## 報告様式
(1)当初目的=原文逐語(ファイル:行) (2)成果物 (3)証拠 (4)A〜H一致/不一致 (5)判定。加えて逸脱・委任_06(実音声対象・想定費用JPY)・07注意点・費用。
