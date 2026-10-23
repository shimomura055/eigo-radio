"""ASR-TIME-NUMERAL-EQUIVALENCE-01: 正式経路の純関数だけで『Primary転写1本』の最終判定を再現する(API 0・ファイル出力なし)。
 実Production adapter(er006_secondary_asr_01)と同じ組立: cls=val.classify_asr_match(canon, asr, role) -> Primary(passed=cls.should_pass,
 basis=er006_secondary_asr_01._equivalence_basis_of(cls)) -> er078_asr_unified_judge_01.unified_judge(lang='en', final_and_gate=True)。
 Secondary ASRは呼べない(注入fnが不可を返す)ので、Primary NGの対は state=NG_SECONDARY_UNAVAILABLE/NG_PROTECTED で『Secondary救済前』の状態を示す。
 PASS系 = state in {PASS, PASS_WITH_WARNING}。"""
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as sec
import er078_asr_unified_judge_01 as uj
import er021_en_asr_semantic_equivalence_production_01 as _t1
# 副作用防止: classify_asr_match が呼ぶ telemetry追記(er021_output/.../telemetry.jsonl、tracked)を、この検証プロセス内だけ無効化する(Production codeは無変更)。
_t1.append_telemetry_log = lambda *a, **k: None
PASS_STATES = ("PASS", "PASS_WITH_WARNING")
def judge_primary(canon: str, asr: str, role: str = "FULL_STORY"):
    cls = val.classify_asr_match(canon, asr, role=role)
    primary = {"passed": bool(cls.should_pass), "text": asr, "label": cls.classification,
               "equivalence_basis": sec._equivalence_basis_of(cls) if cls.should_pass else None}
    ctx = uj.AttemptCtx(canonical_text=canon, wav_sha256="sim", audio_seconds=10.0)
    r = uj.unified_judge(ctx, primary, lambda c: uj.SecondaryOutcome(None, error="sim_no_secondary"), lang="en", role=role)
    return r.state, r.reason_code, cls.classification
