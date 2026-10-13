# -*- coding: utf-8 -*-
"""ASR-PHONETIC-EQUIVALENCE-M1-F1-PRODUCTION-WIRING-01 委任_03 (OF-168): M1(i)=CMU収録語のみの音素正規化で、
674ペアのうち新規受理(ACCEPT_M1)となる件数のread-only集計。配線はしない(M1は未配線)。API 0 / JPY0 / telemetry no-op。"""
import argparse, collections, json, os, sys
sys.path.insert(0, os.getcwd())
import er068_asr_phonetic_equivalence_generalization_01_offline as O
import er075_m1_f1_production_wiring_01_census as C
import er075_m1_f1_production_wiring_01_oov_options as OO


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--oov-fallback", choices=["off"], required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pairs, _ = C.load_pairs()
    rows, cnt = [], collections.Counter()
    for (c, asr), src in pairs.items():
        try:
            O.phoneme_ok = OO.ORIG
            leg = O.design_judge(c, asr)
            O.phoneme_ok = OO.make_phoneme_ok("no_oov")
            new = O.design_judge(c, asr)
        except Exception as e:
            cnt["error"] += 1
            continue
        finally:
            O.phoneme_ok = OO.ORIG
        lp = leg["verdict"] in ("EXACT", "PROD_PASS_UNCHANGED")
        np_ = new["verdict"] in ("EXACT", "PROD_PASS_UNCHANGED", "ACCEPT_M1")
        cnt[f"{src}|legacy_pass={lp}|m1i_pass={np_}"] += 1
        if np_ and not lp:
            rows.append({"src": src, "canonical": c, "asr": asr, "verdict": new["verdict"],
                         "subs": [(s["from"], s["to"], s.get("basis"), s.get("phoneme_rule")) for s in (new.get("m1") or {}).get("subs", [])]})
        if lp and not np_:
            cnt["REGRESSION_pass_to_nonpass"] += 1
    out = {"n_pairs": len(pairs), "counts": dict(cnt), "newly_accepted_by_m1_i": len(rows), "rows": rows, "oov_fallback": a.oov_fallback, "api_calls": 0}
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, ensure_ascii=False, indent=1))
    for r in rows:
        print("NEW", r["src"], r["verdict"], "|", r["canonical"][:120], "|", r["asr"][:120], "|", r["subs"])


if __name__ == "__main__":
    main()
