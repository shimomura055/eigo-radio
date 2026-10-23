"""ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_02 runtime evidence(API 0・新規TTSなし・読み取り専用)。
既存X/Zの保存entry(tts_generation_results.json)の各segmentを、正式な再利用/引継ぎ経路の関数
 er078_reuse_value_guard_01.guard_entry(内部で er019_family_x_validation_inheritance_01.rejudge_with_current_judge を呼ぶ)
で再判定し、修正前(--modules base_HEAD)/修正後で判定・unified_state・reason・Tier1 atom列を記録する。
 py runtime_evidence_02.py --out OUT.json [--modules DIR]
対象: Z=『二十年後』c8(run_sf_prod_01)+c8原稿の時刻文の実対2表記(原稿は同じ・ASRのみ差し替え=合成entry、開示)/ X=時刻・数値・通貨を含む既存entry。
telemetry自動追記はno-op化(追跡ファイルを汚さない)。"""
import sys, os, json, re, argparse
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--modules"); a = ap.parse_args()
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, R)
if a.modules: sys.path.insert(0, os.path.abspath(a.modules))
a.out = os.path.abspath(a.out)
os.chdir(R)
import er021_en_asr_semantic_equivalence_production_01 as t1
t1.append_telemetry_log = lambda *x, **k: None
import er078_reuse_value_guard_01 as rvg
import er109_xz_scope_01 as xz
import er078_asr_value_guard_01 as vg

Z_FILE = "er026_output/family_z_production_e2e_01/after_twenty_years/run_sf_prod_01/a2/audit/tts_generation_results.json"
X_FILES = [
    "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/a2/audit/tts_generation_results.json",
    "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_kpq_01/a2/audit/tts_generation_results.json",
    "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_02/a2/audit/tts_generation_results.json",
    "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/small_bag__run_02/a2/audit/tts_generation_results.json",
    "er019_output/family_x_audio_production_wiring_01/ig_nobel_2026__run_nws_02/a2/audit/tts_generation_results.json",
]
NUMLIKE = re.compile(r"\d|\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion)\b", re.I)


def atoms(text):
    return [(x["kind"], str(x.get("value", x.get("word")))) for x in t1._tier1_atoms(text) if x["kind"] != "literal"]


def one(entry, label):
    g = rvg.guard_entry(entry, label=label)
    return {"blocked": g.get("blocked"), "applicable": g.get("applicable"), "reason": g.get("reason"), "unified_state": g.get("unified_state"),
            "reason_code": g.get("reason_code"), "api_calls": g.get("api_calls"), "secondary_new_calls": g.get("secondary_new_calls")}


def iter_entries(path):
    d = json.load(open(path, encoding="utf-8"))
    segs = d.get("segments") or {}
    for sid, e in (segs.items() if isinstance(segs, dict) else []):
        if isinstance(e, dict) and e.get("asr_text") and (e.get("text") or e.get("canonical_text")):
            yield sid, e


out = {"modules": t1.__file__, "records": []}
# --- Z: 『二十年後』c8 実対
z = json.load(open(Z_FILE, encoding="utf-8"))
c8 = z["segments"]["full_story_part2_c8"]
base_canon, base_asr = c8["canonical_text"], c8["asr_text"]
assert "At ten thirty," in base_canon and "At 10:30," in base_asr
variants = {
    "stored(canon=At ten thirty / ASR=At 10:30) [保存entryそのまま]": (base_canon, base_asr),
    "synthetic(canon=At 10 thirty[TTS数字化後] / ASR=At 10:30)": (base_canon.replace("At ten thirty,", "At 10 thirty,"), base_asr),
    "synthetic(canon=At 10 thirty / ASR=At ten-thirty) [ROOT_CAUSE_01実対]": (base_canon.replace("At ten thirty,", "At 10 thirty,"), base_asr.replace("At 10:30,", "At ten-thirty,")),
    "synthetic(canon=At ten thirty / ASR=At 1030) [桁連結=NG側であるべき]": (base_canon, base_asr.replace("At 10:30,", "At 1030,")),
}
with xz.run_scope("Z"):
    for name, (cn, asr) in variants.items():
        e = dict(c8); e["text"] = cn; e["canonical_text"] = cn; e["asr_text"] = asr
        e.pop("asr_judgement", None)
        out["records"].append({"scope": "Z", "source": Z_FILE, "segment": "full_story_part2_c8", "variant": name, "atoms_canon_time_part": atoms(cn[-60:]),
                               "atoms_asr_time_part": atoms(asr[-60:]), **one(e, "full_story_part2_c8")})
    # Z: 実attempt(c8のattempt2、ASR=`At ten-thirty,`)。canonはTTS入力(er003 tts_safe_number_words_enで数字化された `At 10 thirty,`)=実在の対(合成ではない)
    import er003_v1_n3_01_tts_generate as _n3
    ATT = "er026_output/family_z_production_e2e_01/after_twenty_years/run_sf_prod_01/a2/narration/attempts/full_story_part2_c8_attempt2_customa3c4625e.json"
    att = json.load(open(ATT, encoding="utf-8"))
    tin = _n3.tts_safe_number_words_en(c8["canonical_text"])
    assert "At 10 thirty," in tin and "ten-thirty" in att["asr_text"]
    e = dict(c8); e["text"] = tin; e["canonical_text"] = tin; e["asr_text"] = att["asr_text"]; e.pop("asr_judgement", None)
    out["records"].append({"scope": "Z", "source": ATT, "segment": "full_story_part2_c8", "variant": "REAL attempt2(canon=TTS入力 `At 10 thirty,` / ASR=`At ten-thirty,`)",
                           "atoms_canon_time_part": atoms(tin[-60:]), "atoms_asr_time_part": atoms(att["asr_text"][-60:]), **one(e, "full_story_part2_c8")})
    # Z: 同ファイルの数値/時刻を含む他entry
    for sid, e in iter_entries(Z_FILE):
        if sid == "full_story_part2_c8" or not NUMLIKE.search(e.get("text") or e.get("canonical_text") or ""):
            continue
        ee = dict(e); ee.pop("asr_judgement", None)
        out["records"].append({"scope": "Z", "source": Z_FILE, "segment": sid, "variant": "stored", **one(ee, sid)})
# --- X: 既存X entry(coffee_prices a2 full_story_part1)に時刻文を1文足した合成entry(保存entryに時刻パターンが無い/少ないため。合成であることを開示)
_xd = json.load(open(X_FILES[0], encoding="utf-8"))["segments"]
_xe = _xd["full_story_part1"]
XV = {
    "synthetic(+ 'The shop opens at 10 thirty.' / ASR 'ten-thirty')": (" The shop opens at 10 thirty.", " The shop opens at ten-thirty."),
    "synthetic(+ 'The shop opens at ten thirty.' / ASR '10:30')": (" The shop opens at ten thirty.", " The shop opens at 10:30."),
    "synthetic(+ 'The shop opens at ten thirty.' / ASR '1030')[NG側]": (" The shop opens at ten thirty.", " The shop opens at 1030."),
    "synthetic(+ 'Coffee costs 10 twenty-dollar bills.' / ASR '$20')": (" Coffee costs 10 twenty-dollar bills.", " Coffee costs 10 $20 bills."),
}
with xz.run_scope("X"):
    for name, (cs, asr_s) in XV.items():
        e = dict(_xe); cn = (_xe.get("text") or _xe.get("canonical_text")) + cs; e["text"] = cn; e["canonical_text"] = cn; e["asr_text"] = _xe["asr_text"] + asr_s
        e.pop("asr_judgement", None)
        out["records"].append({"scope": "X", "source": X_FILES[0], "segment": "full_story_part1", "variant": name, "atoms_canon_time_part": atoms(cn[-60:]),
                               "atoms_asr_time_part": atoms(e["asr_text"][-60:]), **one(e, "full_story_part1")})
# --- X
with xz.run_scope("X"):
    for f in X_FILES:
        if not os.path.exists(f):
            out["records"].append({"scope": "X", "source": f, "missing": True}); continue
        for sid, e in iter_entries(f):
            cn = e.get("text") or e.get("canonical_text")
            if not (NUMLIKE.search(cn) or NUMLIKE.search(e["asr_text"])):
                continue
            ee = dict(e); ee.pop("asr_judgement", None)
            has_time = bool(re.search(r"\d{1,2}[: ]\d{2}|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+(?:oh|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty)\b", cn + " " + e["asr_text"], re.I))
            out["records"].append({"scope": "X", "source": f, "segment": sid, "variant": "stored", "time_like": has_time,
                                   "atoms_canon": atoms(cn)[:8], "atoms_asr": atoms(e["asr_text"])[:8], **one(ee, sid)})
json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("records", len(out["records"]), "modules", t1.__file__)
