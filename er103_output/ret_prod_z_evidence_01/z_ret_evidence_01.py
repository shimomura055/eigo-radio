# -*- coding: utf-8 -*-
"""ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 委任_05 B工程: RET(OPEN-472) Z runtime evidence (区分A: 正式Z run_tts_stage + 実生成器 + TTS primitiveのみ保存wavへ差替 + 実ASR)。
隔離run_dir (er103_output/ret_prod_z_evidence_01/run_z)。Production runには触れない。Ledger/HR queue/Stage1(Perplexity+Ledger upsert)は隔離(Ledger語集合・ASR hintを空にして『初見の人名』を模擬)。
Case A: kind=narrator(Adv, b1b) clip_id=full_story_part1_c14 の実narrator生成器(segment_idを統一judgeへ渡す経路)
Case B: kind=dialogue(Std, a2) clip_id=full_story_part1_c14 の実dialogue生成器(er012_b generate_voice_body_wide_margin)
"""
import json, os, shutil, sys, time, wave
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(ROOT); sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "run_z")
if os.path.exists(RUN): shutil.rmtree(RUN)
os.makedirs(RUN)
import er005_cost_logger as cl
cl.install(os.path.join(RUN, "raw_usage_log.jsonl"))
import er002_common as common
import er006_secondary_asr_01 as sec
import er006_pronunciation_ledger_01 as pl
import er063_family_z_audio_01 as a63
import er103_proper_noun_alarm_policy_01 as pol
import er103_run_entity_table_01 as ret

SRC = "er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01_preserve_20261023_b7"   # 委任_07: 再生成前の保全コピー(誤読attempt1 wav入力を再現)
def canon(lv):
    d = json.load(open(f"{SRC}/{lv}/audit/tts_generation_results.json", encoding="utf-8"))
    return d["segments"]["full_story_part1_c14"]["canonical_text"]
CASES = {
    "A": dict(level="b1b", kind="narrator", speaker="narrator", voice="Aoede", wav=f"{SRC}/b1b/narration/attempts/full_story_part1_c14_attempt1_englishstyleprefixwidemargin.wav"),
    "B": dict(level="a2", kind="dialogue", speaker="vera", voice="Zephyr", wav=f"{SRC}/a2/narration/attempts/full_story_part1_c14_attempt1_englishstyleprefixwidemargin.wav"),
}
which = sys.argv[1] if len(sys.argv) > 1 else "A"
c = CASES[which]
text = canon(c["level"])
with wave.open(c["wav"]) as w:
    assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (24000, 1, 2)
    PCM = w.readframes(w.getnframes())
tts_calls = []
def stub_tts(call_fn, prompt, max_retry=2, sleep_fn=None, **kw):
    tts_calls.append(1); return PCM, 0, True, None
common._call_tts_with_retry = stub_tts          # TTS合成primitiveのみ差替(下流=trim/ASR/judge/Azure/cascade/PNAP/RETは正式経路)
hr_calls, st1 = [], []
sec._log_human_review = lambda d: hr_calls.append({"segment": d.get("segment_id"), "reason": d.get("reason") or d.get("review_reason")})
sec._resolve_unresolved_entity_for_review = lambda span: st1.append(span) or {"pronunciation_hint": "(stub)", "confidence": "stub", "sources": []}
pol.ledger_surface_tokens = lambda ledger=None: frozenset()      # 初見の固有名詞(Ledger未登録)の模擬
pl.get_hint_for_text = lambda *a, **k: []                          # ASR hintへもLedgerを供給しない

spec = a63.ClipSpec(clip_id="full_story_part1_c14", level=c["level"], kind=c["kind"], text=text, voice=c["voice"], speaker=c["speaker"],
                    role_key=a63.role_key_for(c["kind"], c["level"], c["speaker"]), part=1)
os.makedirs(f"{RUN}/{c['level']}", exist_ok=True)
gens = a63.real_generators()
t0 = time.time()
with cl.logging_context("z_ret_evidence_" + which, "tts"):
    out = a63.run_tts_stage(RUN, c["level"], [spec], generators=gens, only_clips=None, story_key="the_open_window")
dt = round(time.time() - t0, 1)
tr = json.load(open(f"{RUN}/{c['level']}/audit/tts_generation_results.json", encoding="utf-8"))
seg = tr["segments"]["full_story_part1_c14"]
aj = seg.get("asr_judgement") or {}
res = {"case": which, "evidence_class": "formal_Z_run_tts_stage+real_generator+TTS_primitive_replaced_by_stored_misread_wav+ledger_excluded_first_seen_simulation",
       "level": c["level"], "kind": c["kind"], "wav": c["wav"], "seconds": dt, "tts_stub_calls": len(tts_calls),
       "status": seg.get("status"), "asr_state": aj.get("state"), "asr_reason": aj.get("reason_code"), "role_in_judgement": aj.get("role"), "segment_key_in_judgement": aj.get("segment_key"),
       "pronunciation_alarm_eval": None, "pronunciation_alarm": aj.get("pronunciation_alarm"),
       "alarm_records": [{"proper_noun": r.get("proper_noun"), "evidence": (r.get("mismatch") or {}).get("proper_noun_evidence"), "entity_table_basis": r.get("entity_table_basis")} for r in aj.get("pronunciation_alarm_records") or []],
       "hr_stub_calls": hr_calls, "stage1_stub_calls": len(st1)}
for a in (seg.get("attempts") or []):
    pass
et = f"{RUN}/audit/entity_table.json"
if os.path.exists(et):
    s = json.load(open(et, encoding="utf-8")); res["entity_table_json"] = {"schema": s["schema"], "status": s["status"], "builds": s["builds"], "n_covered": len(s["covered_text_sha256"]),
        "entries": [(e["surface"], e["category"], e["grade"], e["sources"]) for e in s["derived_snapshot"]["entries"]]}
rep = f"{RUN}/{c['level']}/audit/operator_alarm_report.md"
res["operator_report_excerpt"] = open(rep, encoding="utf-8").read()[-1800:] if os.path.exists(rep) else None
ls = f"{RUN}/{c['level']}/audit/review_lock_state.json"
if os.path.exists(ls):
    st = json.load(open(ls, encoding="utf-8")).get("full_story_part1_c14", {})
    res["review_lock_state"] = st.get("state")
    res["attempt_judgements"] = [{"attempt": a["attempt"], "state": (a.get("asr_judgement") or {}).get("state"), "role": (a.get("asr_judgement") or {}).get("role"),
                                   "pae": (a.get("asr_judgement") or {}).get("pronunciation_alarm_eval")} for a in st.get("last_attempts_log", [])]
json.dump(res, open(os.path.join(HERE, f"z_ret_evidence_case{which}_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: res[k] for k in res if k not in ("operator_report_excerpt", "entity_table_json")}, ensure_ascii=False, default=str)[:3500])
