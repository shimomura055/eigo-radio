# 委任_04: AUW(ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01)— JA統一judge配線 + J11(Family X継承再判定)+ 静的監査post_wiring化
(sandwich-pm -> sonnet-worker 委任文。2026-10-15。branch feat/auw-unified-asr-01 HEAD 7c368dbc2)
禁止: git add -A/-f/stash/reset --hard/checkout -f/clean/rebase/amend/force push、mainへのpush/merge。有料API 0: 全testは委任_03cの通信遮断pytest plugin付き、.venv/Scripts/python.exe。本委任で触ったtestからの外部通信は即mock化。既存test由来(er007 openai/er011 huggingface)は記録のみ。

## T-0
本委任文保存、check_delegation_prompt.py -> _check.json(FAILでも継続)。stop_scope_check rc=0。

## 事前指定参照
ユーザー原文 _01.md L39-60基本フロー、L97優先規定、Section固有例外(KP/日本語LR原則HR・見出し・A2 6%減速・Dialogue、新例外禁止)、15必須受入条件、「全Family全Section」。
DESIGN_01 §4-3/§5(J1-J11, J11=er019_family_x_validation_inheritance_01.rejudge_with_current_judge)/§6(C-A..C-M)/§11(U1)、DESIGN_02_ADDENDUM_01 §1/§3-2/§4/§7/J11引継ぎ/OF-AUW-17、APPLICABILITY_MATRIX_01.csv。IMPLEMENTATION_02b §7-8、IMPLEMENTATION_03 §9。
JA配線点: er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail(L383付近)と全呼出元、er007_ja_asr_validator_01.py、SCG費用式(L309-311)、er011_human_review_lock_01。er078_asr_unified_judge_01(U1/U2維持)、er078_asr_value_guard_01、静的監査+allowlist(post_wiring_en->post_wiring)。

## やること
A. JA adapter置換(ENと同契約、戻り値型・呼出元キー維持、全呼出点列挙)。PrimaryResultにequivalence_basis/signals埋め。Primary NG->Secondary1回(SecondaryCache共有)、Secondary PASS->PASS_WITH_WARNING+asr_judgement、障害->NG_SECONDARY_UNAVAILABLE、値ガードJA: DIFF->NG_PROTECTED、AMBIGUOUS->P3->同表層のみNUMERIC_AMBIGUOUS_SURFACE。否定語再否定ゲートはEN同様。COST_GUARDは実秒ベース。SCG費用式値不変。
B. Section固有例外維持(新例外禁止): 日本語KP/LRは原則HR維持、見出し、Dialogue。例外所在と維持証拠(ファイル:行)を表で。
C. J11: rejudge_with_current_judgeを統一judge経由に(asr_judgement_inherited、Secondary新規呼出なし、追補優先)。
D. 静的監査: phase->post_wiring、deferred 0、judge/adapter以外のASR呼出0、EN/JA両entrypointから到達をassert。Primary#2残存caller/testをGrep。
E. OF-AUW-17: JAのallowlist/count集計/HR queue投入条件をGrepし未知ラベル例外なし確認。
F. test: JA adapter各ケース+e2e mock(JA Primary NG・Secondary PASS音声が最終成果物でPASS_WITH_WARNINGとして試聴リストに載る)。9系統96ファイル+er019/er007をファイル単位実行。baseline patch_03b/test_post_03c.json、新規失敗0。旧cascade前提はα/β/γ区分、βで設計判断要ならSTOP。
G. IMPLEMENTATION_04.md(配線点・互換表・例外維持表・J11・静的監査snapshot・test数値・未実装(委任_05: A2減速・Dialogue・KP max_attempts3、begin_secondary_run、is_last_slot)・逸脱)。
H. commit/push(branch、明示add、secret_scan --staged hits=0)。message: ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_04: JA統一judge配線(adapter)+J11継承再判定+静的監査post_wiring+Section例外維持(KP/JA LR原則HR)。main無変更、JPY0

## 禁止
Prompt/モデル/Voice/速度/閾値/HR Lock/予算guard変更、新Section例外、U1/U2変更、SSOT編集、main反映、有料API。設計判断要の競合・βの矛盾・重大誤PASS兆候はSTOP報告。

## 報告様式
受入記録5項目: (1)当初目的=ユーザー原文該当行の逐語(原文ファイルを開いてファイル:行付き) (2)成果物 (3)証拠 (4)A-H一致/不一致 (5)判定。加えて逸脱・委任_05/06注意点・費用。
