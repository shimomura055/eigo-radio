# ASR-FLAP-T-PRODUCTION-WIRING-01 委任_02: 実際に起きたFlap-T偽NGの保存attempt(FX4⑨ latter→Ladder / FZ The Open Window Bertie→Birdie)を、
# 正式な保存音声再判定経路(`er019_family_x_validation_inheritance_01.rejudge_with_current_judge`=継承/HR再判定の入口、出自はattempt記録のsha/voice/modelからhydrate)で
# 再判定する(API 0・読取専用)。ON/OFF対照: 出自あり/出自なし/未確認Voice(Puck|pro)/flag OFF/scope外(A/B/C)。
# 実行: PYTHONUTF8=1 <venv python> <this> --code <worktree> --data <main tree> --out <ev02 dir>
import argparse, glob, json, os, sys

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--data", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
CODE, DATA = os.path.abspath(a.code), os.path.abspath(a.data)
sys.path.insert(0, CODE)
os.chdir(CODE)
import er021_en_asr_semantic_equivalence_production_01 as _er021
_er021.append_telemetry_log = lambda *x, **k: None
import er019_family_x_validation_inheritance_01 as vi
import er103_proper_noun_alarm_policy_01 as pol
import er109_xz_scope_01 as xz
import er139_flapt_equivalence_01 as fe
import er139_flapt_provenance_01 as prov
import warnings
warnings.simplefilter("ignore")
assert os.path.dirname(os.path.abspath(vi.__file__)) == CODE and os.path.dirname(os.path.abspath(fe.__file__)) == CODE

CASES = [
    ("X_nine_latter_ladder", "latter",
     f"{DATA}/er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01/b1b/narration/attempts/vocab_extra_3_en_attempt1_custom60ebc452.json", "vocab_extra_3_en", "b1b"),
]
for i, f in enumerate(sorted(glob.glob(f"{DATA}/er026_output/family_z_production_e2e_01/the_open_window/_preserve_20261023_b8/a2/narration/attempts/full_story_part1_c14_attempt*.json"))[:4], 1):
    CASES.append((f"Z_open_window_bertie_birdie_attempt{i}", None, f, "full_story_part1_c14", "a2"))


def entry_of(att, canon, drop_prov=False, voice=None, model=None):
    e = {"text": canon, "asr_text": att.get("asr_text"), "sha256": att.get("sha256"), "voice": att.get("voice"), "model": att.get("model")}
    sec = [s.get("text") for s in att.get("cascade_steps", []) if str(s.get("provider", "")).startswith("azure") and s.get("text")]
    if sec:
        e["scg_info"] = {"secondary_transcript": sec[0]}
    if drop_prov:
        e.pop("voice")
        e.pop("model")
    if voice:
        e["voice"], e["model"] = voice, model
    return e


def run(entry, level, label, scope="X", flag=True):
    fe.FLAP_T_EQUIVALENCE_ENABLED = flag
    prov.reset_for_tests()
    try:
        if scope:
            with pol.run_scope(scope), xz.run_scope(scope):
                return vi.rejudge_with_current_judge(entry, level, label, force_lang="en")
        return vi.rejudge_with_current_judge(entry, level, label, force_lang="en")
    finally:
        fe.FLAP_T_EQUIVALENCE_ENABLED = True


out = {"cases": []}
for cid, canon, path, label, level in CASES:
    att = json.load(open(path, encoding="utf-8"))
    canonical = canon
    if canonical is None:   # Z: 同runの保存results(tts_generation_results.json)の実canonical_text(原稿)
        res = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(path))), "audit", "tts_generation_results.json"), encoding="utf-8"))
        canonical = res["segments"][label]["canonical_text"]
    row = {"id": cid, "voice": att.get("voice"), "model": att.get("model"), "asr_text": att.get("asr_text"), "canonical": canonical, "attempt_sha256": att.get("sha256")}
    scen = {
        "ON_provenance_from_record": run(entry_of(att, canonical), level, label),
        "OFF_no_provenance": run(entry_of(att, canonical, drop_prov=True), level, label),
        "OFF_unconfirmed_voice_Puck_pro": run(entry_of(att, canonical, voice="Puck", model="gemini-2.5-pro-preview-tts"), level, label),
        "OFF_flag_off": run(entry_of(att, canonical), level, label, flag=False),
        "OFF_scope_outside_ABC": run(entry_of(att, canonical), level, label, scope=None),
    }
    row["scenarios"] = {k: {"ok": bool(v.get("ok")), "unified_state": v.get("unified_state"), "reason": v.get("unified_reason_code") or v.get("reason"),
                            "warnings": (v.get("asr_judgement_inherited") or {}).get("warnings"),
                            "flapt_declined": ((v.get("asr_judgement_inherited") or {}).get("flapt_declined"))} for k, v in scen.items()}
    on = scen["ON_provenance_from_record"]
    sites = ((on.get("asr_judgement_inherited") or {}).get("orthographic_equivalence") or {}).get("sites") or []
    if sites:
        row["audit_flapt"] = (sites[0].get("er109") or {}).get("flapt")
        row["audit_span"] = (sites[0].get("er109") or {}).get("spans")
    out["cases"].append(row)
os.makedirs(a.out, exist_ok=True)
json.dump(out, open(os.path.join(a.out, "attempt_replay_02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in out["cases"]:
    print(r["id"], r["voice"], r["model"], {k: (v["ok"], v["unified_state"], v["warnings"]) for k, v in r["scenarios"].items()})
